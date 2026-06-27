"""
Zero-shot stance classification of central bank press-conference turns
via OpenRouter, using a 5-class scheme:
dovish / mostly dovish / neutral / mostly hawkish / hawkish.

Scores raw answer turns from data/corpus/{BoE,ECB,Fed}.csv directly —
one API call per turn, no chunking. Output is written to
output/stance/turn_predictions_{model}.csv.

Resumable: re-running picks up where it left off.

Run from the repo root:
    uv run python src/llm/score_turns.py --model llama33 --workers 4 --rpm 200
    uv run python src/llm/score_turns.py --model deepseekv3 --bank ECB Fed
"""

import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from tqdm import tqdm

try:
    from .openrouter_models import MODEL_SPECS, ModelSpec
    from .score_openrouter import (
        SYSTEM_PROMPT,
        AsyncRateLimiter,
        CHECKPOINT_EVERY_N,
        DEFAULT_PROMPT_VERSION,
        DEFAULT_TEMPERATURE,
        _call_api_async,
        _make_client,
        build_stance_prompt,
        classify_batch_async,
        parse_confidence,
        parse_stance5,
    )
except ImportError:
    from openrouter_models import MODEL_SPECS, ModelSpec
    from score_openrouter import (
        SYSTEM_PROMPT,
        AsyncRateLimiter,
        CHECKPOINT_EVERY_N,
        DEFAULT_PROMPT_VERSION,
        DEFAULT_TEMPERATURE,
        _call_api_async,
        _make_client,
        build_stance_prompt,
        classify_batch_async,
        parse_confidence,
        parse_stance5,
    )

ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = ROOT / "data" / "corpus"
OUT_DIR = ROOT / "output" / "stance"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALL_BANKS = ["BoE", "ECB", "Fed"]

TURN_OUTPUT_COLUMNS = [
    "turn_uid",
    "bank",
    "doc_id",
    "date",
    "doc_type",
    "speaker",
    "speaker_role",
    "turn_idx",
    "text",
    "model_key",
    "model_slug",
    "label",
    "confidence",
    "temperature",
    "prompt_version",
    "created_at",
]


def load_turns(banks: list[str] | None = None) -> pd.DataFrame:
    selected = banks if banks else ALL_BANKS
    dfs = []
    for bank in selected:
        path = CORPUS_DIR / f"{bank}.csv"
        df = pd.read_csv(path)
        df["bank"] = bank
        dfs.append(df)
    turns = pd.concat(dfs, ignore_index=True)
    turns["turn_uid"] = turns["doc_id"] + "_" + turns["turn_idx"].astype(str)
    return turns


def build_output_frame_turns(
    turns_df: pd.DataFrame,
    spec: "ModelSpec",
    temperature: float,
    prompt_version: str,
) -> pd.DataFrame:
    results = turns_df[
        ["turn_uid", "bank", "doc_id", "date", "doc_type", "speaker", "speaker_role", "turn_idx", "text"]
    ].copy()
    results["model_key"] = spec.key
    results["model_slug"] = spec.slug
    results["label"] = pd.NA
    results["confidence"] = pd.NA
    results["temperature"] = temperature
    results["prompt_version"] = prompt_version
    results["created_at"] = pd.NA
    return results[TURN_OUTPUT_COLUMNS]


def _resume_args_match(results: pd.DataFrame, spec: "ModelSpec", temperature: float, prompt_version: str) -> bool:
    completed = results["label"].notna()
    if not completed.any():
        return True
    existing_keys = set(results.loc[completed, "model_key"].dropna().astype(str))
    existing_slugs = set(results.loc[completed, "model_slug"].dropna().astype(str))
    existing_temps = set(pd.to_numeric(results.loc[completed, "temperature"], errors="coerce").dropna())
    existing_versions = set(results.loc[completed, "prompt_version"].dropna().astype(str))
    return (
        existing_keys <= {spec.key}
        and existing_slugs <= {spec.slug}
        and existing_temps <= {float(temperature)}
        and existing_versions <= {prompt_version}
    )


def load_or_initialize_turns(
    turns_df: pd.DataFrame,
    out_path: Path,
    spec: "ModelSpec",
    temperature: float,
    prompt_version: str,
) -> pd.DataFrame:
    print(f"Total turns: {len(turns_df)}")
    if out_path.exists():
        results = pd.read_csv(out_path)
        if len(results) != len(turns_df):
            print(f"Saved file has {len(results)} rows but turns_df has {len(turns_df)} — starting fresh.")
            return build_output_frame_turns(turns_df, spec, temperature, prompt_version)
        missing_cols = [c for c in TURN_OUTPUT_COLUMNS if c not in results.columns]
        if missing_cols:
            print(f"Saved file missing columns {missing_cols} — starting fresh.")
            return build_output_frame_turns(turns_df, spec, temperature, prompt_version)
        if not _resume_args_match(results, spec, temperature, prompt_version):
            print("Saved file was produced with different run metadata — starting fresh.")
            return build_output_frame_turns(turns_df, spec, temperature, prompt_version)
        print(f"Resuming — {results['label'].notna().sum()} already scored.")
        return results[TURN_OUTPUT_COLUMNS].copy()
    print("Starting fresh.")
    return build_output_frame_turns(turns_df, spec, temperature, prompt_version)


async def _run_for_model_async(
    model_key: str,
    banks: list[str] | None = None,
    temperature: float = DEFAULT_TEMPERATURE,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    max_workers: int = 1,
    rpm: int | None = None,
) -> Path:
    if model_key not in MODEL_SPECS:
        valid = ", ".join(sorted(MODEL_SPECS))
        raise ValueError(f"Unknown model key {model_key!r}. Valid: {valid}")

    spec: ModelSpec = MODEL_SPECS[model_key]
    effective_rpm = rpm if rpm is not None else spec.rpm
    out_path = OUT_DIR / f"turn_predictions_{spec.key}.csv"
    run_created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    client = _make_client(spec)
    rate_limiter = AsyncRateLimiter(rpm=effective_rpm, burst=max_workers)
    semaphore = asyncio.Semaphore(max_workers)

    turns_df = load_turns(banks)
    results = load_or_initialize_turns(turns_df, out_path, spec, temperature, prompt_version)

    n_done = int(results["label"].notna().sum())
    if n_done > 0:
        print(f"Resuming {spec.tag} from row {n_done} ({len(results) - n_done} remaining)...")
    else:
        print(f"Starting {spec.tag} from scratch ({effective_rpm} RPM, {max_workers} workers)...")

    texts = [str(t) if pd.notna(t) else "" for t in results["text"]]
    labels = results["label"].tolist()
    confidences = results["confidence"].tolist()
    created_at = results["created_at"].tolist()

    pending = [i for i, lbl in enumerate(labels) if pd.isna(lbl) or lbl != lbl or lbl == "parse_error"]

    lock = asyncio.Lock()
    n_completed = 0
    pbar = tqdm(total=len(pending), desc=spec.tag)

    async def score_one(i: int) -> None:
        nonlocal n_completed
        async with semaphore:
            try:
                preds = await classify_batch_async(
                    client, [texts[i]], spec.slug, spec.tag, temperature, rate_limiter
                )
                stance, conf = preds[0]
            except Exception as e:
                tqdm.write(f"Turn {i} failed: {e} — filling with parse_error")
                stance, conf = "parse_error", "parse_error"

        async with lock:
            labels[i] = stance
            confidences[i] = conf
            created_at[i] = run_created_at
            n_completed += 1
            pbar.update(1)
            if n_completed % CHECKPOINT_EVERY_N == 0:
                results["label"] = labels
                results["confidence"] = confidences
                results["created_at"] = created_at
                results.to_csv(out_path, index=False)
                tqdm.write(f"Checkpoint saved -> {out_path}")

    await asyncio.gather(*[score_one(i) for i in pending])
    pbar.close()

    results["label"] = labels
    results["confidence"] = confidences
    results["created_at"] = created_at
    results.to_csv(out_path, index=False)
    print(f"Saved -> {out_path}")
    print(pd.Series(labels).value_counts())
    print(pd.Series(confidences).value_counts())
    return out_path


def run_for_model(
    model_key: str,
    banks: list[str] | None = None,
    temperature: float = DEFAULT_TEMPERATURE,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    max_workers: int = 1,
    rpm: int | None = None,
) -> Path:
    return asyncio.run(
        _run_for_model_async(model_key, banks, temperature, prompt_version, max_workers, rpm)
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score corpus turns with LLM stance classifier")
    parser.add_argument("--model", required=True, choices=sorted(MODEL_SPECS))
    parser.add_argument("--bank", nargs="+", choices=ALL_BANKS, default=None,
                        help="Banks to score (default: all three)")
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--prompt-version", default=DEFAULT_PROMPT_VERSION)
    parser.add_argument("--workers", type=int, default=1, help="Max concurrent requests")
    parser.add_argument("--rpm", type=int, default=None, help="Requests per minute override")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_for_model(
        args.model,
        banks=args.bank,
        temperature=args.temperature,
        prompt_version=args.prompt_version,
        max_workers=args.workers,
        rpm=args.rpm,
    )


if __name__ == "__main__":
    main()

"""
Zero-shot stance classification of central bank press-conference chunks
via OpenRouter, using a 5-class scheme:
dovish / mostly dovish / neutral / mostly hawkish / hawkish.

Resumable: re-running this script picks up where it left off (checks
the existing prediction column in CHUNK_OUT and skips completed rows).

Run from the repo root: uv run python src/llm/score_openrouter.py --model gpt55
"""

import argparse
import json
import os
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

try:
    from .openrouter_models import MODEL_SPECS, ModelSpec
except ImportError:
    from openrouter_models import MODEL_SPECS, ModelSpec


ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env", override=True)

CHUNKS_DIR = ROOT / "data" / "csv" / "chunks"
OUT_DIR = ROOT / "output" / "stance"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 10
SLEEP_BETWEEN_CALLS = 1.0
CHECKPOINT_EVERY_N_BATCHES = 50

VALID_STANCES = ["dovish", "mostly dovish", "neutral", "mostly hawkish", "hawkish"]
STANCE_SCORE = {
    "dovish": -1.0,
    "mostly dovish": -0.5,
    "neutral": 0.0,
    "mostly hawkish": 0.5,
    "hawkish": 1.0,
}

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)


def build_stance_prompt(chunks: list[str]) -> str:
    n = len(chunks)
    numbered = "".join(f"{i + 1}. {c}\n" for i, c in enumerate(chunks))
    return (
        f"Classify the monetary policy stance of each of the following {n} excerpts "
        f"from central bank press conferences.\n"
        f'Return a JSON array with exactly {n} objects, one per excerpt in order, '
        'each with a single key "stance" whose value is EXACTLY one of these five strings: '
        '"dovish", "mostly dovish", "neutral", "mostly hawkish", "hawkish".\n'
        'Use "dovish"/"hawkish" only for strong/unambiguous signals; use "mostly dovish"/'
        '"mostly hawkish" for leaning-but-not-strong signals; use "neutral" otherwise.\n'
        'No explanations, no extra keys. '
        'Example: [{"stance": "mostly hawkish"}, {"stance": "neutral"}, ...]\n\n'
        f"Excerpts:\n{numbered}"
    )


_CANONICAL_ORDER = [
    "mostly dovish",
    "mostly hawkish",
    "dovish",
    "hawkish",
    "neutral",
]
_ALIASES = {
    "dovish": {"dovish", "dove"},
    "mostly dovish": {
        "mostly dovish",
        "mostly_dovish",
        "mostly-dovish",
        "somewhat dovish",
        "slightly dovish",
        "leaning dovish",
    },
    "neutral": {"neutral", "balanced", "mixed"},
    "mostly hawkish": {
        "mostly hawkish",
        "mostly_hawkish",
        "mostly-hawkish",
        "somewhat hawkish",
        "slightly hawkish",
        "leaning hawkish",
    },
    "hawkish": {"hawkish", "hawk"},
}


def _normalize(raw: str) -> str:
    s = raw.lower().strip().rstrip(".")
    s = re.sub(r"[_\-]+", " ", s)
    return re.sub(r"\s+", " ", s)


def parse_stance5(raw: str) -> str:
    clean = _normalize(str(raw))
    for canon, aliases in _ALIASES.items():
        if clean in aliases:
            return canon
    for canon in _CANONICAL_ORDER:
        if canon in clean:
            return canon
    return "parse_error"


def _call_openrouter(
    model_slug: str,
    model_tag: str,
    prompt: str,
    max_tokens: int = 512,
    retries: int = 6,
) -> str:
    wait = 5.0
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model_slug,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.0,
            )
            text = resp.choices[0].message.content
            if not text:
                raise RuntimeError("Empty response")
            return text.strip()
        except Exception as e:
            msg = str(e)
            if any(x in msg.lower() for x in ["429", "rate", "connect", "timeout"]):
                print(f"Retrying in {wait:.0f}s (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
                wait = min(wait * 2, 120)
            else:
                raise
    raise RuntimeError(f"{model_tag} failed after {retries} retries")


def classify_batch(chunks: list[str], model_slug: str, model_tag: str) -> list[str]:
    max_tokens = max(len(chunks) * 20, 256)
    raw = _call_openrouter(model_slug, model_tag, build_stance_prompt(chunks), max_tokens=max_tokens)
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON array in response: {raw[:200]}")
    parsed = json.loads(match.group())
    if len(parsed) != len(chunks):
        raise ValueError(f"Expected {len(chunks)}, got {len(parsed)}")
    return [parse_stance5(str(r.get("stance", ""))) for r in parsed]


def load_chunks() -> pd.DataFrame:
    chunk_files = {
        "BoE": ["BoE_chunks.csv", "BoE_opening_chunks.csv"],
        "ECB": ["ECB_chunks.csv", "ECB_opening_chunks.csv"],
        "Fed": ["Fed_chunks.csv", "Fed_opening_chunks.csv"],
    }
    dfs = []
    for bank, files in chunk_files.items():
        for fname in files:
            df = pd.read_csv(CHUNKS_DIR / fname)
            df["bank"] = bank
            df["source_type"] = "opening" if "opening" in fname else "chunk"
            dfs.append(df)
    chunks_df = pd.concat(dfs, ignore_index=True)
    chunks_df["word_count"] = chunks_df["text"].str.split().str.len()
    return chunks_df


def load_or_initialize_results(chunks_df: pd.DataFrame, chunk_out: Path) -> pd.DataFrame:
    print(f"Total chunks: {len(chunks_df)}")
    if chunk_out.exists():
        results = pd.read_csv(chunk_out)
        if len(results) != len(chunks_df):
            print(
                f"Saved file has {len(results)} rows but chunks_df has {len(chunks_df)} rows - starting fresh."
            )
            return chunks_df.copy()
        print(f"Resuming - columns: {list(results.columns)}")
        return results
    print("Starting fresh.")
    return chunks_df.copy()


def run_for_model(model_key: str) -> Path:
    if model_key not in MODEL_SPECS:
        valid = ", ".join(sorted(MODEL_SPECS))
        raise ValueError(f"Unknown model key {model_key!r}. Valid options: {valid}")

    spec: ModelSpec = MODEL_SPECS[model_key]
    chunk_out = OUT_DIR / f"chunk_predictions_{spec.key}.csv"
    pred_col = f"{spec.tag}_stance"

    chunks_df = load_chunks()
    results = load_or_initialize_results(chunks_df, chunk_out)

    if pred_col not in results.columns:
        results[pred_col] = np.nan

    n_done = int(results[pred_col].notna().sum())
    if n_done > 0:
        print(f"Resuming {spec.tag} from row {n_done} ({len(results) - n_done} remaining)...")
    else:
        print(f"Starting {spec.tag} from scratch...")

    texts = [str(t) if pd.notna(t) else "" for t in results["text"]]
    pred = results[pred_col].tolist()
    start_batch = (n_done // BATCH_SIZE) * BATCH_SIZE

    for i in tqdm(range(start_batch, len(texts), BATCH_SIZE), desc=spec.tag):
        batch = texts[i : i + BATCH_SIZE]
        try:
            preds = classify_batch(batch, spec.slug, spec.tag)
        except Exception as e:
            print(f"Batch {i} failed: {e} - filling with parse_error")
            preds = ["parse_error"] * len(batch)
        for j, stance in enumerate(preds):
            pred[i + j] = stance
        time.sleep(SLEEP_BETWEEN_CALLS)
        if ((i // BATCH_SIZE) + 1) % CHECKPOINT_EVERY_N_BATCHES == 0:
            results[pred_col] = pred
            results.to_csv(chunk_out, index=False)
            print(f"Checkpoint saved -> {chunk_out}")

    results[pred_col] = pred
    results.to_csv(chunk_out, index=False)
    print(f"Saved -> {chunk_out}")
    print(pd.Series(pred).value_counts())
    return chunk_out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=sorted(MODEL_SPECS))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_for_model(args.model)


if __name__ == "__main__":
    main()

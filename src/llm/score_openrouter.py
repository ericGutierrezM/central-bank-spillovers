"""
Zero-shot stance classification of central bank press-conference chunks
via OpenRouter, using a 5-class scheme:
dovish / mostly dovish / neutral / mostly hawkish / hawkish.

Resumable: re-running this script picks up where it left off (checks
the existing prediction column in CHUNK_OUT and skips completed rows).

Run from the repo root: uv run python src/llm/score_openrouter.py --model gpt55
"""

import argparse
import asyncio
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import AsyncOpenAI
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

DEFAULT_BATCH_SIZE = 1
CHECKPOINT_EVERY_N = 50
DEFAULT_TEMPERATURE = 0.0
DEFAULT_PROMPT_VERSION = "v1"

SYSTEM_PROMPT = (
    "You are an expert in monetary policy communication, trained to classify the stance "
    "expressed in central bank press conference excerpts. "
    "You classify stance strictly based on the text provided, not on your prior knowledge "
    "of the meeting outcome or broader economic context. "
    "You always respond with valid JSON and nothing else — no preamble, no explanation."
)

VALID_STANCES = ["dovish", "mostly dovish", "neutral", "mostly hawkish", "hawkish"]
STANCE_SCORE = {
    "dovish": -1.0,
    "mostly dovish": -0.5,
    "neutral": 0.0,
    "mostly hawkish": 0.5,
    "hawkish": 1.0,
}
VALID_CONFIDENCE = ["low", "medium", "high"]
OUTPUT_COLUMNS = [
    "chunk_uid",
    "bank",
    "doc_id",
    "date",
    "doc_type",
    "speaker",
    "speaker_role",
    "turn_idx",
    "turn_type",
    "chunk_id",
    "start_sent_idx",
    "end_sent_idx",
    "n_sentences",
    "text",
    "model_key",
    "model_slug",
    "label",
    "confidence",
    "temperature",
    "prompt_version",
    "created_at",
]
LEGACY_STANCE_COLS = [f"{spec.tag}_stance" for spec in MODEL_SPECS.values()]


class AsyncRateLimiter:
    """Token bucket: averages to rpm requests/minute, allows burst up to `burst` tokens."""

    def __init__(self, rpm: int, burst: int = 1):
        self._refill_rate = rpm / 60.0  # tokens per second
        self._tokens = float(burst)
        self._max_tokens = float(burst)
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                self._tokens = min(
                    self._max_tokens,
                    self._tokens + (now - self._last) * self._refill_rate,
                )
                self._last = now
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                wait = (1.0 - self._tokens) / self._refill_rate
            await asyncio.sleep(wait)


def _make_client(spec: "ModelSpec") -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=spec.base_url,
        api_key=os.environ[spec.api_key_env],
    )


def build_stance_prompt(chunks: list[str]) -> str:
    n = len(chunks)
    numbered = "".join(f"{i + 1}. {c}\n" for i, c in enumerate(chunks))
    return (
        f"Classify the monetary policy stance expressed in each of the following {n} "
        "excerpts from the question-and-answer portion of central bank press conferences.\n"
        "Each excerpt may contain mixed or conflicting signals. Classify the overall stance "
        "expressed in the excerpt itself, not the broader meeting or general economic background.\n"
        f'Return a JSON array with exactly {n} objects, one per excerpt in order, '
        'each with exactly two keys: "label" and "confidence".\n'
        'Allowed "label" values (ordered from most dovish to most hawkish):\n'
        '- "dovish": strong and unambiguous support for easier monetary policy, lower rates, '
        'more accommodation, or strong emphasis on downside risks that clearly point toward easing\n'
        '- "mostly dovish": weaker or qualified easing signal\n'
        '- "neutral": balanced, descriptive, procedural, or no clear directional policy stance. '
        'Note: "data-dependent" language alone is not sufficient for neutral — consider the direction '
        'of risks the speaker emphasises.\n'
        '- "mostly hawkish": weaker or qualified tightening signal\n'
        '- "hawkish": strong and unambiguous support for tighter monetary policy, higher rates, '
        'less accommodation, or strong emphasis on inflation risks that clearly point toward tightening\n'
        'Allowed "confidence" values:\n'
        '- "high": the signal is clear\n'
        '- "medium": moderate certainty\n'
        '- "low": the stance is hard to determine\n'
        'If the excerpt does not clearly imply tightening or easing, use "neutral".\n'
        'Return only the JSON array. No explanations, no extra keys.\n'
        'Example: [{"label": "mostly hawkish", "confidence": "medium"}, '
        '{"label": "neutral", "confidence": "low"}]\n\n'
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


_CONFIDENCE_ALIASES = {
    "low": {"low", "low confidence"},
    "medium": {"medium", "medium confidence", "moderate", "moderate confidence", "med"},
    "high": {"high", "high confidence"},
}


def parse_confidence(raw: str) -> str:
    clean = _normalize(str(raw))
    for canon, aliases in _CONFIDENCE_ALIASES.items():
        if clean in aliases:
            return canon
    for canon in VALID_CONFIDENCE:
        if canon in clean:
            return canon
    return "parse_error"


async def _call_api_async(
    client: AsyncOpenAI,
    model_slug: str,
    model_tag: str,
    prompt: str,
    temperature: float,
    rate_limiter: AsyncRateLimiter,
    max_tokens: int = 512,
    retries: int = 6,
) -> str:
    wait = 5.0
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    for attempt in range(retries):
        await rate_limiter.acquire()
        try:
            resp = await client.chat.completions.create(
                model=model_slug,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            text = resp.choices[0].message.content
            if not text:
                raise RuntimeError("Empty response")
            return text.strip()
        except Exception as e:
            msg = str(e)
            if any(x in msg.lower() for x in ["429", "rate", "connect", "timeout"]):
                tqdm.write(f"Retrying in {wait:.0f}s (attempt {attempt + 1}/{retries})")
                await asyncio.sleep(wait)
                wait = min(wait * 2, 120)
            else:
                raise
    raise RuntimeError(f"{model_tag} failed after {retries} retries")


async def classify_batch_async(
    client: AsyncOpenAI,
    chunks: list[str],
    model_slug: str,
    model_tag: str,
    temperature: float,
    rate_limiter: AsyncRateLimiter,
) -> list[tuple[str, str]]:
    max_tokens = max(len(chunks) * 32, 256)
    raw = await _call_api_async(
        client,
        model_slug,
        model_tag,
        build_stance_prompt(chunks),
        temperature=temperature,
        rate_limiter=rate_limiter,
        max_tokens=max_tokens,
    )
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON array in response: {raw[:200]}")
    parsed = json.loads(match.group())
    if len(parsed) != len(chunks):
        raise ValueError(f"Expected {len(chunks)}, got {len(parsed)}")
    return [
        (
            parse_stance5(str(row.get("label", ""))),
            parse_confidence(str(row.get("confidence", ""))),
        )
        for row in parsed
    ]


def load_chunks() -> pd.DataFrame:
    chunk_files = {
        "BoE": ["BoE_chunks.csv"],
        "ECB": ["ECB_chunks.csv"],
        "Fed": ["Fed_chunks.csv"],
    }
    dfs = []
    for bank, files in chunk_files.items():
        for fname in files:
            df = pd.read_csv(CHUNKS_DIR / fname)
            df["bank"] = bank
            df["source_type"] = "chunk"
            dfs.append(df)
    chunks_df = pd.concat(dfs, ignore_index=True)
    chunks_df["word_count"] = chunks_df["text"].str.split().str.len()
    return chunks_df


def build_output_frame(
    chunks_df: pd.DataFrame,
    spec: ModelSpec,
    temperature: float,
    prompt_version: str,
) -> pd.DataFrame:
    results = chunks_df[
        [
            "chunk_uid",
            "bank",
            "doc_id",
            "date",
            "doc_type",
            "speaker",
            "speaker_role",
            "turn_idx",
            "turn_type",
            "chunk_id",
            "start_sent_idx",
            "end_sent_idx",
            "n_sentences",
            "text",
        ]
    ].copy()
    results["model_key"] = spec.key
    results["model_slug"] = spec.slug
    results["label"] = pd.NA
    results["confidence"] = pd.NA
    results["temperature"] = temperature
    results["prompt_version"] = prompt_version
    results["created_at"] = pd.NA
    return results[OUTPUT_COLUMNS]


def has_legacy_schema(results: pd.DataFrame) -> bool:
    return "label" not in results.columns and any(col in results.columns for col in LEGACY_STANCE_COLS)


def resume_args_match(results: pd.DataFrame, spec: ModelSpec, temperature: float, prompt_version: str) -> bool:
    completed = results["label"].notna()
    if not completed.any():
        return True

    existing_model_key = set(results.loc[completed, "model_key"].dropna().astype(str))
    existing_model_slug = set(results.loc[completed, "model_slug"].dropna().astype(str))
    existing_temperature = set(pd.to_numeric(results.loc[completed, "temperature"], errors="coerce").dropna())
    existing_prompt_version = set(results.loc[completed, "prompt_version"].dropna().astype(str))

    return (
        existing_model_key <= {spec.key}
        and existing_model_slug <= {spec.slug}
        and existing_temperature <= {float(temperature)}
        and existing_prompt_version <= {prompt_version}
    )


def load_or_initialize_results(
    chunks_df: pd.DataFrame,
    chunk_out: Path,
    spec: ModelSpec,
    temperature: float,
    prompt_version: str,
) -> pd.DataFrame:
    print(f"Total chunks: {len(chunks_df)}")
    if chunk_out.exists():
        results = pd.read_csv(chunk_out)
        if len(results) != len(chunks_df):
            print(f"Saved file has {len(results)} rows but chunks_df has {len(chunks_df)} rows - starting fresh.")
            return build_output_frame(chunks_df, spec, temperature, prompt_version)
        if has_legacy_schema(results):
            print("Saved file uses the legacy wide schema - starting fresh with the new output schema.")
            return build_output_frame(chunks_df, spec, temperature, prompt_version)
        missing_cols = [col for col in OUTPUT_COLUMNS if col not in results.columns]
        if missing_cols:
            print(f"Saved file is missing columns {missing_cols} - starting fresh.")
            return build_output_frame(chunks_df, spec, temperature, prompt_version)
        if not resume_args_match(results, spec, temperature, prompt_version):
            print("Saved file was produced with different run metadata - starting fresh.")
            return build_output_frame(chunks_df, spec, temperature, prompt_version)
        print(f"Resuming - columns: {list(results.columns)}")
        return results[OUTPUT_COLUMNS].copy()
    print("Starting fresh.")
    return build_output_frame(chunks_df, spec, temperature, prompt_version)


async def _run_for_model_async(
    model_key: str,
    temperature: float = DEFAULT_TEMPERATURE,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    max_workers: int = 1,
    rpm: int | None = None,
) -> Path:
    if model_key not in MODEL_SPECS:
        valid = ", ".join(sorted(MODEL_SPECS))
        raise ValueError(f"Unknown model key {model_key!r}. Valid options: {valid}")

    spec: ModelSpec = MODEL_SPECS[model_key]
    effective_rpm = rpm if rpm is not None else spec.rpm
    chunk_out = OUT_DIR / f"chunk_predictions_{spec.key}.csv"
    run_created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    client = _make_client(spec)
    rate_limiter = AsyncRateLimiter(rpm=effective_rpm, burst=max_workers)
    semaphore = asyncio.Semaphore(max_workers)

    chunks_df = load_chunks()
    results = load_or_initialize_results(chunks_df, chunk_out, spec, temperature, prompt_version)

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
                tqdm.write(f"Chunk {i} failed: {e} - filling with parse_error")
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
                results.to_csv(chunk_out, index=False)
                tqdm.write(f"Checkpoint saved -> {chunk_out}")

    await asyncio.gather(*[score_one(i) for i in pending])
    pbar.close()

    results["label"] = labels
    results["confidence"] = confidences
    results["created_at"] = created_at
    results.to_csv(chunk_out, index=False)
    print(f"Saved -> {chunk_out}")
    print(pd.Series(labels).value_counts())
    print(pd.Series(confidences).value_counts())
    return chunk_out


def run_for_model(
    model_key: str,
    temperature: float = DEFAULT_TEMPERATURE,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    max_workers: int = 1,
    rpm: int | None = None,
) -> Path:
    return asyncio.run(
        _run_for_model_async(model_key, temperature, prompt_version, max_workers, rpm)
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=sorted(MODEL_SPECS))
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--prompt-version", default=DEFAULT_PROMPT_VERSION)
    parser.add_argument("--workers", type=int, default=1, help="Max concurrent requests (default: 1)")
    parser.add_argument("--rpm", type=int, default=None, help="Requests per minute override (default: model spec)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_for_model(
        args.model,
        temperature=args.temperature,
        prompt_version=args.prompt_version,
        max_workers=args.workers,
        rpm=args.rpm,
    )


if __name__ == "__main__":
    main()

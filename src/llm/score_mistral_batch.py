"""
Mistral Batch API scorer — same prompts and output format as score_openrouter.py.

Two-phase workflow:
  1. Submit:  uv run python src/llm/score_mistral_batch.py --submit
  2. Fetch:   uv run python src/llm/score_mistral_batch.py --fetch [--poll]

After --submit the job ID is saved to output/stance/mistral_batch_state.json.
--fetch checks status; add --poll to keep checking until the job completes.
Results land in output/stance/chunk_predictions_mistrallarge3_batch.csv,
identical schema to the chunk_predictions_*.csv files from score_openrouter.py.
"""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from tqdm import tqdm

try:
    from .score_openrouter import (
        OUTPUT_COLUMNS,
        SYSTEM_PROMPT,
        build_output_frame,
        build_stance_prompt,
        load_chunks,
        parse_confidence,
        parse_stance5,
    )
    from .openrouter_models import MODEL_SPECS
except ImportError:
    from score_openrouter import (
        OUTPUT_COLUMNS,
        SYSTEM_PROMPT,
        build_output_frame,
        build_stance_prompt,
        load_chunks,
        parse_confidence,
        parse_stance5,
    )
    from openrouter_models import MODEL_SPECS

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env", override=True)

OUT_DIR = ROOT / "output" / "stance"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BATCH_JSONL = OUT_DIR / "mistral_batch_input.jsonl"
STATE_FILE = OUT_DIR / "mistral_batch_state.json"
CHUNK_OUT = OUT_DIR / "chunk_predictions_mistrallarge3_batch.csv"

MISTRAL_API = "https://api.mistral.ai/v1"
MODEL_KEY = "mistrallarge3"
TEMPERATURE = 0.0
PROMPT_VERSION = "v1"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}",
        "Content-Type": "application/json",
    }


def _raise(resp: requests.Response) -> None:
    if not resp.ok:
        raise RuntimeError(f"Mistral API error {resp.status_code}: {resp.text[:400]}")


# ── Build JSONL ────────────────────────────────────────────────────────────────

def build_batch_jsonl(chunks_df: pd.DataFrame) -> Path:
    """Write one request per chunk to BATCH_JSONL and return the path."""
    print(f"Building batch JSONL for {len(chunks_df)} chunks...")
    with open(BATCH_JSONL, "w", encoding="utf-8") as f:
        for _, row in tqdm(chunks_df.iterrows(), total=len(chunks_df), desc="Building JSONL"):
            request = {
                "custom_id": str(row["chunk_uid"]),
                "body": {
                    "model": MODEL_SPECS[MODEL_KEY].slug,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": build_stance_prompt([str(row["text"])])},
                    ],
                    "max_tokens": 64,
                    "temperature": TEMPERATURE,
                },
            }
            f.write(json.dumps(request) + "\n")
    print(f"Written -> {BATCH_JSONL}")
    return BATCH_JSONL


# ── Submit ─────────────────────────────────────────────────────────────────────

def submit() -> None:
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
        print(f"Existing batch job found: {state['job_id']} (submitted {state['submitted_at']})")
        print("Delete output/stance/mistral_batch_state.json to start a new batch.")
        return

    chunks_df = load_chunks()
    build_batch_jsonl(chunks_df)

    print("Uploading JSONL to Mistral Files API...")
    with open(BATCH_JSONL, "rb") as f:
        resp = requests.post(
            f"{MISTRAL_API}/files",
            headers={"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"},
            files={"file": (BATCH_JSONL.name, f, "application/octet-stream")},
            data={"purpose": "batch"},
        )
    _raise(resp)
    file_id = resp.json()["id"]
    print(f"File uploaded: {file_id}")

    print("Creating batch job...")
    resp = requests.post(
        f"{MISTRAL_API}/batch/jobs",
        headers=_headers(),
        json={
            "input_files": [file_id],
            "model": MODEL_SPECS[MODEL_KEY].slug,
            "endpoint": "/v1/chat/completions",
            "metadata": {"project": "central-bank-spillovers", "prompt_version": PROMPT_VERSION},
        },
    )
    _raise(resp)
    job = resp.json()
    job_id = job["id"]
    submitted_at = datetime.now(timezone.utc).isoformat()

    state = {"job_id": job_id, "file_id": file_id, "submitted_at": submitted_at, "status": job.get("status")}
    STATE_FILE.write_text(json.dumps(state, indent=2))
    print(f"Batch job created: {job_id}")
    print(f"Status: {job.get('status')}")
    print(f"State saved -> {STATE_FILE}")
    print("\nRun with --fetch (or --fetch --poll) to retrieve results when done.")


# ── Fetch ──────────────────────────────────────────────────────────────────────

def _check_status(job_id: str) -> dict:
    resp = requests.get(f"{MISTRAL_API}/batch/jobs/{job_id}", headers=_headers())
    _raise(resp)
    return resp.json()


def _download_results(output_file_id: str) -> list[dict]:
    resp = requests.get(f"{MISTRAL_API}/files/{output_file_id}/content", headers=_headers())
    _raise(resp)
    lines = [ln for ln in resp.text.strip().splitlines() if ln]
    return [json.loads(ln) for ln in lines]


def _parse_results(raw_results: list[dict], chunks_df: pd.DataFrame) -> pd.DataFrame:
    spec = MODEL_SPECS[MODEL_KEY]
    run_created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    results = build_output_frame(chunks_df, spec, TEMPERATURE, PROMPT_VERSION)
    uid_to_idx = {str(uid): i for i, uid in enumerate(results["chunk_uid"])}

    n_ok = n_err = 0
    for record in tqdm(raw_results, desc="Parsing results"):
        uid = record.get("custom_id", "")
        idx = uid_to_idx.get(uid)
        if idx is None:
            print(f"Warning: unknown custom_id {uid!r}")
            continue

        resp_body = record.get("response", {})
        status = resp_body.get("status_code", 0)

        if status == 200:
            try:
                content = resp_body["body"]["choices"][0]["message"]["content"]
                import re
                match = re.search(r"\[.*\]", content, re.DOTALL)
                if not match:
                    raise ValueError(f"No JSON array: {content[:100]}")
                parsed = json.loads(match.group())
                row = parsed[0]
                label = parse_stance5(str(row.get("label", "")))
                confidence = parse_confidence(str(row.get("confidence", "")))
                n_ok += 1
            except Exception as e:
                print(f"Parse error for {uid}: {e}")
                label, confidence = "parse_error", "parse_error"
                n_err += 1
        else:
            label, confidence = "parse_error", "parse_error"
            n_err += 1

        results.at[idx, "label"] = label
        results.at[idx, "confidence"] = confidence
        results.at[idx, "created_at"] = run_created_at

    print(f"Parsed {n_ok} OK, {n_err} errors out of {len(raw_results)} results")
    return results


def fetch(poll: bool = False) -> None:
    if not STATE_FILE.exists():
        print("No batch state found. Run --submit first.")
        return

    state = json.loads(STATE_FILE.read_text())
    job_id = state["job_id"]

    while True:
        job = _check_status(job_id)
        status = job.get("status", "unknown")
        total = job.get("total_requests", "?")
        succeeded = job.get("succeeded_requests", "?")
        failed = job.get("failed_requests", "?")

        print(f"Job {job_id}: {status} | {succeeded}/{total} succeeded, {failed} failed")

        if status == "SUCCESS":
            break
        if status in ("FAILED", "CANCELLED", "TIMEOUT_EXCEEDED", "CANCELLATION_REQUESTED"):
            print(f"Job ended with status: {status}")
            return
        if not poll:
            print("Job not done yet. Re-run with --fetch --poll to keep checking, or --fetch again later.")
            return

        print("Waiting 60s before next check...")
        time.sleep(60)

    output_file_id = job.get("output_file")
    if not output_file_id:
        print(f"No output file in job response: {job}")
        return

    print(f"Downloading results (file: {output_file_id})...")
    raw_results = _download_results(output_file_id)
    print(f"Downloaded {len(raw_results)} result records")

    chunks_df = load_chunks()
    results = _parse_results(raw_results, chunks_df)

    results.to_csv(CHUNK_OUT, index=False)
    print(f"Saved -> {CHUNK_OUT}")
    print(pd.Series(results["label"]).value_counts())
    print(pd.Series(results["confidence"]).value_counts())

    state["status"] = "SUCCESS"
    state["output_file_id"] = output_file_id
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--submit", action="store_true", help="Build JSONL and submit batch job")
    group.add_argument("--fetch", action="store_true", help="Check status and download results if done")
    parser.add_argument("--poll", action="store_true", help="With --fetch: keep polling until job completes")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.submit:
        submit()
    else:
        fetch(poll=args.poll)


if __name__ == "__main__":
    main()

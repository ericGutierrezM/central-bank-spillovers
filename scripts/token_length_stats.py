import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent
CHUNKS_DIR = ROOT / "data" / "csv" / "chunks"
CORPUS_DIR = ROOT / "data" / "corpus"

BANKS = {
    "BoE": "governor",
    "ECB": "president",
    "Fed": "chair",
}

STATS = ["N", "mean", "median", "p25", "p75", "p90", "p95", "max"]

def word_count(text):
    if pd.isna(text):
        return 0
    return len(str(text).split())

def compute_stats(series):
    s = series.dropna()
    return {
        "N":      len(s),
        "mean":   s.mean(),
        "median": s.median(),
        "p25":    np.percentile(s, 25),
        "p75":    np.percentile(s, 75),
        "p90":    np.percentile(s, 90),
        "p95":    np.percentile(s, 95),
        "max":    s.max(),
    }

def fmt(val, key):
    return f"{val:.0f}" if key in ("N", "max") else f"{val:.1f}"

COL = 12

for bank, role in BANKS.items():
    chunks_df = pd.read_csv(CHUNKS_DIR / f"{bank}_chunks.csv")
    chunks_wc = chunks_df[chunks_df["turn_type"] == "answer"]["text"].apply(word_count)
    chunks_s = compute_stats(chunks_wc)

    corpus_df = pd.read_csv(CORPUS_DIR / f"{bank}.csv")
    corpus_wc = corpus_df[corpus_df["speaker_role"] == role]["text"].apply(word_count)
    corpus_s = compute_stats(corpus_wc)

    print(f"\n{'=' * 38}")
    print(f"  {bank}")
    print(f"{'=' * 38}")
    print(f"{'':10}  {'chunks':>{COL}}  {'raw turns':>{COL}}")
    print(f"  {'-' * 34}")
    for key in STATS:
        print(f"  {key:<8}  {fmt(chunks_s[key], key):>{COL}}  {fmt(corpus_s[key], key):>{COL}}")

print()

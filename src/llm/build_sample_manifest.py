"""
Build a reproducible sample manifest with exactly N random chunks per document
from the non-opening chunk files for BoE, ECB, and Fed.

Run from the repo root, for example:
uv run python src/llm/build_sample_manifest.py --seed 42 --chunks-per-doc 3
"""

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CHUNKS_DIR = ROOT / "data" / "csv" / "chunks"

CHUNK_FILES = {
    "BoE": "BoE_chunks.csv",
    "ECB": "ECB_chunks.csv",
    "Fed": "Fed_chunks.csv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--chunks-per-doc", type=int, default=3)
    return parser.parse_args()


def load_chunks() -> pd.DataFrame:
    dfs = []
    for bank, filename in CHUNK_FILES.items():
        df = pd.read_csv(CHUNKS_DIR / filename)
        df["bank"] = bank
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def sample_doc(group: pd.DataFrame, chunks_per_doc: int, seed: int) -> pd.DataFrame:
    if len(group) < chunks_per_doc:
        raise ValueError(
            f"Document {group.name!r} has only {len(group)} chunks, fewer than {chunks_per_doc}."
        )
    sampled = group.sample(n=chunks_per_doc, random_state=seed).copy()
    sampled = sampled.sort_values(["turn_idx", "chunk_id", "chunk_uid"]).reset_index(drop=True)
    sampled["sample_rank"] = range(1, len(sampled) + 1)
    return sampled


def build_manifest(seed: int, chunks_per_doc: int) -> pd.DataFrame:
    chunks = load_chunks()
    sampled_groups = []
    for (bank, doc_id), group in chunks.groupby(["bank", "doc_id"], sort=True):
        sampled_group = sample_doc(group, chunks_per_doc=chunks_per_doc, seed=seed)
        sampled_group["bank"] = bank
        sampled_group["doc_id"] = doc_id
        sampled_groups.append(sampled_group)

    sampled = pd.concat(sampled_groups, ignore_index=True)
    sampled["sample_seed"] = seed
    manifest = sampled[
        [
            "bank",
            "doc_id",
            "date",
            "doc_type",
            "speaker",
            "speaker_role",
            "turn_idx",
            "turn_type",
            "chunk_id",
            "chunk_uid",
            "start_sent_idx",
            "end_sent_idx",
            "n_sentences",
            "text",
            "sample_rank",
            "sample_seed",
        ]
    ].sort_values(["bank", "doc_id", "sample_rank", "turn_idx", "chunk_id"])
    return manifest.reset_index(drop=True)


def main() -> None:
    args = parse_args()
    manifest = build_manifest(seed=args.seed, chunks_per_doc=args.chunks_per_doc)
    out_path = CHUNKS_DIR / f"sample_manifest_{args.chunks_per_doc}_per_doc_seed{args.seed}.csv"
    manifest.to_csv(out_path, index=False)

    print(f"Saved -> {out_path}")
    print(f"Rows: {len(manifest)}")
    print(f"Docs: {manifest[['bank', 'doc_id']].drop_duplicates().shape[0]}")
    print(manifest["bank"].value_counts().sort_index())


if __name__ == "__main__":
    main()

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parents[2]
DATA_CSV_DIR = ROOT / "data" / "csv"
INPUT_FILES = [
    DATA_CSV_DIR / "BoE_sentence.csv",
    DATA_CSV_DIR / "ECB_sentence.csv",
    DATA_CSV_DIR / "Fed_sentence.csv",
]


embedding_model = SentenceTransformer("intfloat/e5-large-v2")


def embed_sentences(texts: list[str]) -> np.ndarray:
    prefixed = [f"passage: {text}" for text in texts]
    return embedding_model.encode(
        prefixed,
        normalize_embeddings=True,
        show_progress_bar=False,
    )


def compute_window_surprisal(embeddings: np.ndarray, window: int = 4) -> np.ndarray:
    scores = np.zeros(len(embeddings))
    for idx in range(window, len(embeddings) - window):
        left = embeddings[idx - window : idx]
        right = embeddings[idx : idx + window]
        scores[idx] = 1 - np.dot(left.mean(axis=0), right.mean(axis=0))
    return scores


def smooth_signal(signal: np.ndarray, window: int = 4) -> np.ndarray:
    kernel = np.ones(window) / window
    return np.convolve(signal, kernel, mode="valid")


def detect_boundaries(signal: np.ndarray, prominence: float) -> set[int]:
    peaks, _ = find_peaks(signal, prominence=prominence)
    return set(peaks.tolist())


def build_chunks(records: list[dict], boundaries: set[int]) -> list[list[dict]]:
    chunks: list[list[dict]] = []
    current: list[dict] = []
    for idx, record in enumerate(records):
        current.append(record)
        if idx in boundaries:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


def _chunk_embedding(chunk: list[dict], sentence_embeddings: np.ndarray) -> np.ndarray:
    indices = [record["_emb_idx"] for record in chunk]
    vectors = sentence_embeddings[indices]
    mean = vectors.mean(axis=0)
    return mean / np.linalg.norm(mean)


def merge_chunks(
    chunks: list[list[dict]],
    sentence_embeddings: np.ndarray,
    min_size: int = 3,
    sim_threshold: float = 0.85,
) -> list[list[dict]]:
    embeddings = [_chunk_embedding(chunk, sentence_embeddings) for chunk in chunks]
    merged: list[list[dict]] = []
    idx = 0

    while idx < len(chunks):
        current = list(chunks[idx])
        current_embedding = embeddings[idx]
        while len(current) < min_size and idx + 1 < len(chunks):
            if np.dot(current_embedding, embeddings[idx + 1]) > sim_threshold:
                current += chunks[idx + 1]
                idx += 1
                current_embedding = _chunk_embedding(current, sentence_embeddings)
            else:
                break
        merged.append(current)
        idx += 1

    return merged


def meta_chunk_records(
    records: list[dict],
    context_window: int = 2,
    smooth_window: int | None = None,
    peak_prominence: float = 0.02,
) -> tuple[list[list[dict]], np.ndarray | None, set[int]]:
    if smooth_window is None:
        smooth_window = max(2, context_window)

    texts = [str(record["text"]).strip() for record in records]
    if len(records) < 2 * context_window + 1:
        return [records], None, set()

    embeddings = embed_sentences(texts)
    for idx, record in enumerate(records):
        record["_emb_idx"] = idx

    surprisal = compute_window_surprisal(embeddings, window=context_window)
    interior = surprisal[context_window : len(surprisal) - context_window]
    smooth = smooth_signal(interior, window=smooth_window)

    adaptive_prominence = max(peak_prominence, smooth.std() * 0.5)
    raw_boundaries = detect_boundaries(smooth, prominence=adaptive_prominence)
    offset = context_window + (smooth_window - 1) // 2
    boundaries = {boundary + offset for boundary in raw_boundaries}

    chunks = build_chunks(records, boundaries)
    chunks = merge_chunks(chunks, sentence_embeddings=embeddings)
    return chunks, smooth, boundaries


def chunk_to_record(chunk: list[dict], chunk_id: int) -> dict:
    for record in chunk:
        record.pop("_emb_idx", None)

    first = chunk[0]
    last = chunk[-1]
    return {
        "doc_id": first["doc_id"],
        "date": first["date"],
        "doc_type": first["doc_type"],
        "speaker": first["speaker"],
        "speaker_role": first["speaker_role"],
        "turn_idx": first.get("turn_idx"),
        "turn_type": first.get("turn_type"),
        "chunk_id": chunk_id,
        "chunk_uid": f"{first['doc_id']}_{chunk_id}",
        "start_sent_idx": first["sent_idx"],
        "end_sent_idx": last["sent_idx"],
        "n_sentences": len(chunk),
        "text": " ".join(record["text"] for record in chunk),
    }


def process_answers(group: pd.DataFrame) -> list[dict]:
    output: list[dict] = []
    chunk_counter = 0
    turns = group.sort_values(["turn_idx", "sent_idx"]).groupby("turn_idx")

    for _, turn in turns:
        records = turn.to_dict("records")
        if len(records) < 10:
            output.append(chunk_to_record(records, chunk_counter))
            chunk_counter += 1
            continue

        chunks, _, _ = meta_chunk_records(records)
        for chunk in chunks:
            output.append(chunk_to_record(chunk, chunk_counter))
            chunk_counter += 1

    return output


def build_chunks_for_file(input_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path).dropna(subset=["text"])
    all_chunks: list[dict] = []

    for _, group in df.groupby("doc_id"):
        if "answer" not in group["turn_type"].unique():
            continue
        answer_group = group[group["turn_type"] == "answer"]
        all_chunks.extend(process_answers(answer_group))

    return pd.DataFrame(all_chunks)


def output_path_for(input_path: Path) -> Path:
    out_dir = input_path.parent / "chunks_clean"
    out_dir.mkdir(exist_ok=True)
    return out_dir / input_path.name.replace("_sentence", "_chunks")


def main() -> None:
    DATA_CSV_DIR.mkdir(parents=True, exist_ok=True)

    for input_path in INPUT_FILES:
        if not input_path.exists():
            raise FileNotFoundError(f"Required sentence CSV not found: {input_path}")

        chunks_df = build_chunks_for_file(input_path)
        output_path = output_path_for(input_path)

        assert chunks_df["chunk_uid"].is_unique, (
            f"Duplicate chunk UIDs in {input_path.name}"
        )
        chunks_df.to_csv(output_path, index=False)
        print(f"{input_path.name} -> {output_path} ({len(chunks_df)} chunks)")


if __name__ == "__main__":
    main()

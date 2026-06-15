import os
# import random

# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from sentence_transformers import SentenceTransformer


# ─── Embedding model ──────────────────────────────────────────────────────────────────

embedding_model = SentenceTransformer("intfloat/e5-large-v2")


# ─── Sentence embeddings ──────────────────────────────────────────────────────────────

def embed_sentences(texts):
    prefixed = [f"passage: {t}" for t in texts]
    return embedding_model.encode(prefixed, normalize_embeddings=True, show_progress_bar=False)


# ─── Window surprisal ─────────────────────────────────────────────────────────────────
# Semantic discontinuity as a proxy for perplexity-based boundary detection, 
# as in Zhao et al. (2024). 
# Uses 1 - cosine similarity between mean embeddings of adjacent sentence windows 
# instead of token log-probabilities.

def compute_window_surprisal(embeddings, window=4):
    scores = np.zeros(len(embeddings))
    for i in range(window, len(embeddings) - window):
        left = embeddings[i - window : i]
        right = embeddings[i : i + window]
        scores[i] = 1 - np.dot(left.mean(axis=0), right.mean(axis=0))
    return scores


# ─── Signal smoothing ─────────────────────────────────────────────────────────────────

def smooth_signal(signal, window=4):
    kernel = np.ones(window) / window
    return np.convolve(signal, kernel, mode="valid")


# ─── Boundary detection ───────────────────────────────────────────────────────────────

def detect_boundaries(signal, prominence):
    peaks, _ = find_peaks(signal, prominence=prominence)
    return set(peaks.tolist())


# ─── Chunk builder ────────────────────────────────────────────────────────────────────

def build_chunks(records, boundaries):
    chunks, current = [], []
    for i, record in enumerate(records):
        current.append(record)
        if i in boundaries:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks


# ─── Dynamic merging ──────────────────────────────────────────────────────────────────
# Merges small adjacent chunks if semantically similar. 
# Uses pre-computed sentence embeddings (no re-encoding). 
# Inspired by the dynamic merging step in Zhao et al. (2024).

def _chunk_emb(chunk, sentence_embeddings):
    idxs = [r["_emb_idx"] for r in chunk]
    vecs = sentence_embeddings[idxs]
    mean = vecs.mean(axis=0)
    return mean / np.linalg.norm(mean)


def merge_chunks(chunks, sentence_embeddings, min_size=3, sim_threshold=0.85):
    embeddings = [_chunk_emb(c, sentence_embeddings) for c in chunks]
    merged = []
    i = 0
    while i < len(chunks):
        current = list(chunks[i])
        emb_current = embeddings[i]
        while len(current) < min_size and i + 1 < len(chunks):
            if np.dot(emb_current, embeddings[i + 1]) > sim_threshold:
                current += chunks[i + 1]
                i += 1
                emb_current = _chunk_emb(current, sentence_embeddings)
            else:
                break
        merged.append(current)
        i += 1
    return merged


# ─── Meta-Chunking pipeline ───────────────────────────────────────────────────────────

def meta_chunk_records(
        records,
        context_window=4,
        smooth_window=4,
        peak_prominence=0.02,
    ):
    texts = [str(r["text"]).strip() for r in records]

    # Documents too short to form valid windows returned as a single chunk
    if len(records) < 2 * context_window + 1:
        return [records], None, set()

    # 1. Sentence embeddings (tag each record with its index for merge_chunks)
    embeddings = embed_sentences(texts)
    for idx, r in enumerate(records):
        r["_emb_idx"] = idx

    # 2. Window surprisal (strip zero-padded edges before smoothing)
    surprisal = compute_window_surprisal(embeddings, window=context_window)
    interior = surprisal[context_window: len(surprisal) - context_window]

    # 3. Smooth the interior signal
    smooth = smooth_signal(interior, window=smooth_window)

    # 4. Adaptive prominence: floor or half the signal std, whichever is larger
    adaptive_prominence = max(peak_prominence, smooth.std() * 0.5)

    # 5. Detect peaks (map from smooth-space back to record indices)
    raw_boundaries = detect_boundaries(smooth, prominence=adaptive_prominence)
    offset = context_window + (smooth_window - 1) // 2
    boundaries = {b + offset for b in raw_boundaries}

    # 6. Build initial chunks and apply dynamic merging
    chunks = build_chunks(records, boundaries)
    chunks = merge_chunks(chunks, sentence_embeddings=embeddings)

    return chunks, smooth, boundaries


# ─── Record builder ───────────────────────────────────────────────────────────────────

def chunk_to_record(chunk, chunk_id):
    for r in chunk:
        r.pop("_emb_idx", None)
    first = chunk[0]
    last = chunk[-1]
    return {
        "doc_id":         first["doc_id"],
        "date":           first["date"],
        "doc_type":       first["doc_type"],
        "speaker":        first["speaker"],
        "speaker_role":   first["speaker_role"],
        "turn_idx":       first.get("turn_idx"),
        "turn_type":      first.get("turn_type"),
        "chunk_id":       chunk_id,
        "chunk_uid":      f"{first['doc_id']}_{chunk_id}",
        "start_sent_idx": first["sent_idx"],
        "end_sent_idx":   last["sent_idx"],
        "n_sentences":    len(chunk),
        "text":           " ".join(r["text"] for r in chunk),
    }


# ─── Document-level processors ────────────────────────────────────────────────────────
# Routing is on turn_type, not doc_type.
# turn_type == "opening" → continuous monologue, chunk at document level
# turn_type == "answer"  → Q&A turn, chunk per turn (only if >= 10 sentences)
# This works correctly across BoE, ECB, and Fed which use different doc_type strings.

def process_opening(group):
    records = group.sort_values("sent_idx").to_dict("records")
    chunks, _, _ = meta_chunk_records(records)
    return [chunk_to_record(c, i) for i, c in enumerate(chunks)]


def process_answers(group):
    output, chunk_counter = [], 0
    turns = group.sort_values(["turn_idx", "sent_idx"]).groupby("turn_idx")
    for _, turn in turns:
        records = turn.to_dict("records")
        if len(records) < 10:
            output.append(chunk_to_record(records, chunk_counter))
            chunk_counter += 1
        else:
            chunks, _, _ = meta_chunk_records(records)
            for c in chunks:
                output.append(chunk_to_record(c, chunk_counter))
                chunk_counter += 1
    return output


# ─── Corpus processor ─────────────────────────────────────────────────────────────────

def process_corpus(files):
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df = df.dropna(subset=["text"])

    all_chunks = []
    for doc_id, group in df.groupby("doc_id"):
        # Route on turn_type, which is consistent across all three banks
        turn_types = group["turn_type"].unique()
        if "opening" in turn_types:
            opening_group = group[group["turn_type"] == "opening"]
            all_chunks.extend(process_opening(opening_group))
        if "answer" in turn_types:
            answer_group = group[group["turn_type"] == "answer"]
            all_chunks.extend(process_answers(answer_group))

    return pd.DataFrame(all_chunks)


# ─── Files ────────────────────────────────────────────────────────────────────────────

files = [
    "../data/csv/BoE_opening_sentence.csv",
    "../data/csv/BoE_sentence.csv",
    "../data/csv/ECB_opening_sentence.csv",
    "../data/csv/ECB_sentence.csv",
    "../data/csv/Fed_opening_sentence.csv",
    "../data/csv/Fed_sentence.csv",
]


# ─── Tuning block ─────────────────────────────────────────────────────────────────────
# Inspect boundary quality on opening remarks before running the full corpus.

# sample = pd.read_csv("../data/csv/BoE_opening_sentence.csv")
# results = {}

# for doc_id, group in sample.groupby("doc_id"):
    # opening_rows = group[group["turn_type"] == "opening"]
    # if opening_rows.empty:
        # continue
    # records = opening_rows.sort_values("sent_idx").to_dict("records")
    # chunks, signal, boundaries = meta_chunk_records(records)
    # if signal is not None:
        # results[doc_id] = (chunks, signal, boundaries)

# sample_ids = random.sample(list(results.keys()), min(9, len(results)))
# sampled = {doc_id: results[doc_id] for doc_id in sample_ids}

# n = len(sampled)
# fig, axes = plt.subplots(n, 1, figsize=(14, 3 * n))

# for ax, (doc_id, (chunks, signal, boundaries)) in zip(axes, sampled.items()):
    # ax.plot(signal, linewidth=0.9)
    # for b in boundaries:
        # ax.axvline(b, color="red", linewidth=0.8, linestyle="--")
    # ax.set_title(f"{doc_id}: {len(chunks)} chunks", fontsize=9)
    # ax.set_yticks([])

# os.makedirs("../output", exist_ok=True)
# plt.tight_layout()
# plt.savefig("../output/boe_chunks_opening_signals.png", dpi=150)
# plt.show()


# ─── Production block ─────────────────────────────────────────────────────────────────

os.makedirs("../data/csv", exist_ok=True)

for filepath in files:
    df = pd.read_csv(filepath).dropna(subset=["text"])
    all_chunks = []

    for doc_id, group in df.groupby("doc_id"):
        turn_types = group["turn_type"].unique()

        if "opening" in turn_types:
            opening_group = group[group["turn_type"] == "opening"]
            all_chunks.extend(process_opening(opening_group))

        if "answer" in turn_types:
            answer_group = group[group["turn_type"] == "answer"]
            all_chunks.extend(process_answers(answer_group))

    chunks_df = pd.DataFrame(all_chunks)

    # Derive output filename from input filename
    input_name = os.path.basename(filepath)
    output_path = f"../data/csv/{input_name.replace('_sentence', '_chunks')}"

    assert chunks_df["chunk_uid"].is_unique, f"Duplicate chunk UIDs in {input_name}"
    chunks_df.to_csv(output_path, index=False)
    print(f"  {input_name} → {output_path} ({len(chunks_df)} chunks)")
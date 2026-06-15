import os
import pandas as pd

files = [
    "../data/csv/BoE_opening_sentence.csv",
    "../data/csv/BoE_sentence.csv",
    "../data/csv/ECB_opening_sentence.csv",
    "../data/csv/ECB_sentence.csv",
    "../data/csv/Fed_opening_sentence.csv",
    "../data/csv/Fed_sentence.csv",
]

# ─── General stats ────────────────────────────────────────────────────────────────────

print("\n─── CHUNK COUNT DISTRIBUTION PER FILE ───────────────────────────────────────")
for filepath in files:
    input_name = os.path.basename(filepath)
    output_path = f"../data/csv/{input_name.replace('_sentence', '_chunks')}"

    if not os.path.exists(output_path):
        print(f"\n{input_name}: output file not found at {output_path}")
        continue

    chunks_df = pd.read_csv(output_path)
    chunks_per_doc = chunks_df.groupby("doc_id")["chunk_id"].count()

    print(f"\n{input_name}:")
    print(f"  total chunks: {len(chunks_df)}")
    print(f"  chunks per doc — mean: {chunks_per_doc.mean():.1f}, median: {chunks_per_doc.median():.1f}, min: {chunks_per_doc.min()}, max: {chunks_per_doc.max()}")
    print(f"  docs with 1 chunk: {(chunks_per_doc == 1).sum()} ({100*(chunks_per_doc == 1).mean():.1f}%)")
    print(f"  n_sentences — mean: {chunks_df['n_sentences'].mean():.1f}, median: {chunks_df['n_sentences'].median():.1f}, min: {chunks_df['n_sentences'].min()}, max: {chunks_df['n_sentences'].max()}")

# ─── BoE opening diagnostic ───────────────────────────────────────────────────────────

print("\n─── BOE OPENING: SINGLE VS MULTI-CHUNK DOCS ─────────────────────────────────")
chunks_df = pd.read_csv("../data/csv/BoE_opening_chunks.csv")
chunks_per_doc = chunks_df.groupby("doc_id")["chunk_id"].count()

single_chunk_docs = chunks_per_doc[chunks_per_doc == 1].index.tolist()
multi_chunk_docs = chunks_per_doc[chunks_per_doc > 1].index.tolist()
print(f"\nSingle-chunk docs: {len(single_chunk_docs)}")
print(f"Multi-chunk docs:  {len(multi_chunk_docs)}")

boe = pd.read_csv("../data/csv/BoE_opening_sentence.csv")
boe_open = boe[boe["turn_type"] == "opening"]
sents = boe_open.groupby("doc_id").size()

print("\nSentence counts for single-chunk docs:")
print(sents[sents.index.isin(single_chunk_docs)].describe())
print("\nSentence counts for multi-chunk docs:")
print(sents[sents.index.isin(multi_chunk_docs)].describe())
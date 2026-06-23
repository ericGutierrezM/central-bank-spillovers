"""
Annotator Embedding Model — Central Bank Stance Disagreement
============================================================
Run in Google Colab (T4 GPU, ~45 min):

  1. Upload this file to Colab
  2. Upload the 4 chunk_predictions CSVs via the file browser (left panel → upload)
       output/stance/chunk_predictions_llama33.csv
       output/stance/chunk_predictions_deepseekv3.csv
       output/stance/chunk_predictions_qwen25_72b.csv
       output/stance/chunk_predictions_mistrallarge_or.csv
  3. Run:  !python annotator_embedding_colab.py

Outputs saved to /content/output/:
  - annotator_embeddings.png    PCA of the 4 model embedding vectors
  - swap_analysis.png           Label shift for split chunks when swapping annotator
  - per_model_metrics.csv       Accuracy + F1 per annotator
  - annotator_vectors.npy       Raw 64-dim embedding vectors (4 × 64)
  - model_checkpoint.pt         Best model weights
"""

# ── 0. Install ─────────────────────────────────────────────────────────────────
import subprocess, sys
subprocess.run([sys.executable, '-m', 'pip', 'install',
                'transformers', 'accelerate', 'scikit-learn', '-q'], check=True)

# ── 1. Imports ─────────────────────────────────────────────────────────────────
import os, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import torch
import torch.nn as nn
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, f1_score, accuracy_score

warnings.filterwarnings('ignore')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Device: {device}')
if device.type == 'cuda':
    print(f'GPU: {torch.cuda.get_device_name(0)}')

OUT_DIR = Path('/content/output')
OUT_DIR.mkdir(exist_ok=True)

# ── 2. Config ──────────────────────────────────────────────────────────────────
ENCODER_NAME  = 'microsoft/deberta-v3-base'
MAX_LENGTH    = 512
ANNOTATOR_DIM = 64
BATCH_SIZE    = 8
GRAD_ACCUM    = 2        # effective batch = 16
N_EPOCHS      = 3
WARMUP_STEPS  = 100
SEED          = 42

MODELS = {
    'llama33':         'Llama 3.3 70B',
    'deepseekv3':      'DeepSeek V3',
    'qwen25_72b':      'Qwen 2.5 72B',
    'mistrallarge_or': 'Mistral Large',
}
STANCE_SCORE = {
    'dovish': -1.0, 'mostly dovish': -0.5, 'neutral': 0.0,
    'mostly hawkish': 0.5, 'hawkish': 1.0,
}
DIRECTIONAL = ['dovish', 'mostly dovish', 'mostly hawkish', 'hawkish']
LABEL_ORDER = ['dovish', 'mostly dovish', 'neutral', 'mostly hawkish', 'hawkish']

label_to_idx = {l: i for i, l in enumerate(LABEL_ORDER)}
idx_to_label = {i: l for l, i in label_to_idx.items()}

np.random.seed(SEED)
torch.manual_seed(SEED)

# ── 3. Load data ───────────────────────────────────────────────────────────────
print('\nLoading chunk predictions...')
all_chunks = {}
for key in MODELS:
    path = Path(f'/content/chunk_predictions_{key}.csv')
    if not path.exists():
        print(f'  {key}: NOT FOUND at {path} — skipping')
        continue
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y%m%d')
    df = df[df['label'].isin(STANCE_SCORE)].copy()
    all_chunks[key] = df
    print(f'  {key}: {len(df):,} chunks')

loaded = [k for k in MODELS if k in all_chunks]
assert len(loaded) >= 2, 'Need at least 2 models loaded'
print(f'\nLoaded: {loaded}')

model_to_idx = {k: i for i, k in enumerate(loaded)}
idx_to_model = {i: k for k, i in model_to_idx.items()}

# ── 4. Build chunks_wide ───────────────────────────────────────────────────────
print('\nBuilding chunks_wide...')
base_cols = ['chunk_uid', 'bank', 'doc_id', 'date', 'turn_type', 'speaker_role',
             'doc_type', 'turn_idx', 'chunk_id', 'n_sentences', 'text']

chunks_wide = (all_chunks[loaded[0]][base_cols + ['label', 'score']]
               .rename(columns={'label': f'label_{loaded[0]}',
                                'score': f'score_{loaded[0]}'})
               .copy())
for key in loaded[1:]:
    chunks_wide = chunks_wide.merge(
        all_chunks[key][['chunk_uid', 'label', 'score']].rename(
            columns={'label': f'label_{key}', 'score': f'score_{key}'}),
        on='chunk_uid', how='inner')

for key in loaded:
    chunks_wide[f'stanced_{key}'] = chunks_wide[f'label_{key}'].isin(DIRECTIONAL)

chunks_wide['n_stanced']         = chunks_wide[[f'stanced_{k}' for k in loaded]].sum(axis=1)
chunks_wide['consensus_stanced'] = chunks_wide['n_stanced'] == len(loaded)
chunks_wide['consensus_neutral'] = chunks_wide['n_stanced'] == 0
chunks_wide['split']             = (~chunks_wide['consensus_stanced']
                                    & ~chunks_wide['consensus_neutral'])

print(f'chunks_wide: {len(chunks_wide):,} chunks')
print(f'  All neutral: {chunks_wide["consensus_neutral"].mean():.1%}')
print(f'  All stanced: {chunks_wide["consensus_stanced"].mean():.1%}')
print(f'  Split:       {chunks_wide["split"].mean():.1%}')

# ── 5. Flatten to (chunk, annotator, label) triples ───────────────────────────
print('\nFlattening dataset...')
chunk_uids = chunks_wide['chunk_uid'].unique()
np.random.shuffle(chunk_uids)
n = len(chunk_uids)
train_uids = set(chunk_uids[:int(0.8 * n)])
val_uids   = set(chunk_uids[int(0.8 * n):int(0.9 * n)])
test_uids  = set(chunk_uids[int(0.9 * n):])

rows = []
for _, chunk in chunks_wide.iterrows():
    uid = chunk['chunk_uid']
    split_set = ('train' if uid in train_uids else
                 'val'   if uid in val_uids   else 'test')
    for key in loaded:
        rows.append({
            'chunk_uid':     uid,
            'text':          str(chunk['text']) if pd.notna(chunk['text']) else '',
            'annotator_idx': model_to_idx[key],
            'label_idx':     label_to_idx[chunk[f'label_{key}']],
            'split_set':     split_set,
            'is_split':      chunk['split'],
            'bank':          chunk['bank'],
        })

flat_df = pd.DataFrame(rows)
print(f'Flat dataset: {len(flat_df):,} examples')
for s in ['train', 'val', 'test']:
    print(f'  {s}: {(flat_df["split_set"] == s).sum():,}')

# ── 6. Dataset + tokenizer ─────────────────────────────────────────────────────
print(f'\nLoading tokenizer: {ENCODER_NAME}')
tokenizer = AutoTokenizer.from_pretrained(ENCODER_NAME)

class ChunkAnnotatorDataset(Dataset):
    def __init__(self, df):
        self.texts          = df['text'].tolist()
        self.annotator_idxs = df['annotator_idx'].tolist()
        self.label_idxs     = df['label_idx'].tolist()

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, i):
        enc = tokenizer(
            self.texts[i],
            max_length=MAX_LENGTH,
            padding='max_length',
            truncation=True,
            return_tensors='pt',
        )
        return {
            'input_ids':      enc['input_ids'].squeeze(0),
            'attention_mask': enc['attention_mask'].squeeze(0),
            'annotator_idx':  torch.tensor(self.annotator_idxs[i], dtype=torch.long),
            'label':          torch.tensor(self.label_idxs[i],     dtype=torch.long),
        }

train_ds = ChunkAnnotatorDataset(flat_df[flat_df['split_set'] == 'train'])
val_ds   = ChunkAnnotatorDataset(flat_df[flat_df['split_set'] == 'val'])
test_ds  = ChunkAnnotatorDataset(flat_df[flat_df['split_set'] == 'test'])

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=2, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False, num_workers=2, pin_memory=True)
test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False, num_workers=2, pin_memory=True)

print(f'Batches — train: {len(train_loader)} | val: {len(val_loader)} | test: {len(test_loader)}')

# ── 7. Model ───────────────────────────────────────────────────────────────────
class AnnotatorEmbeddingModel(nn.Module):
    def __init__(self, encoder_name, n_annotators, n_classes=5, annotator_dim=64):
        super().__init__()
        self.encoder       = AutoModel.from_pretrained(encoder_name)
        hidden             = self.encoder.config.hidden_size   # 768
        self.annotator_emb = nn.Embedding(n_annotators, annotator_dim)
        nn.init.normal_(self.annotator_emb.weight, std=0.02)
        self.classifier = nn.Sequential(
            nn.Linear(hidden + annotator_dim, 256),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(256, n_classes),
        )

    def forward(self, input_ids, attention_mask, annotator_idx):
        enc   = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls   = enc.last_hidden_state[:, 0, :]       # (B, 768)
        a_emb = self.annotator_emb(annotator_idx)    # (B, 64)
        return self.classifier(torch.cat([cls, a_emb], dim=-1))

    def get_annotator_embeddings(self):
        return self.annotator_emb.weight.detach().cpu().numpy()

    def get_cls_embedding(self, input_ids, attention_mask):
        with torch.no_grad():
            enc = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
            return enc.last_hidden_state[:, 0, :].cpu()

model = AnnotatorEmbeddingModel(ENCODER_NAME, n_annotators=len(loaded)).to(device)
n_params = sum(p.numel() for p in model.parameters()) / 1e6
print(f'\nModel: {n_params:.1f}M parameters')

# ── 8. Training ────────────────────────────────────────────────────────────────
optimizer = torch.optim.AdamW([
    {'params': model.encoder.parameters(),       'lr': 2e-5, 'weight_decay': 0.01},
    {'params': model.annotator_emb.parameters(), 'lr': 1e-3, 'weight_decay': 0.0},
    {'params': model.classifier.parameters(),    'lr': 1e-3, 'weight_decay': 0.01},
])

total_opt_steps = (len(train_loader) // GRAD_ACCUM) * N_EPOCHS
scheduler = get_linear_schedule_with_warmup(
    optimizer, num_warmup_steps=WARMUP_STEPS, num_training_steps=total_opt_steps)

criterion = nn.CrossEntropyLoss()

def run_epoch(loader, train=True):
    model.train() if train else model.eval()
    total_loss, total_correct, total_n = 0.0, 0, 0
    optimizer.zero_grad()

    for step, batch in enumerate(loader):
        input_ids      = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        annotator_idx  = batch['annotator_idx'].to(device)
        labels         = batch['label'].to(device)

        with torch.set_grad_enabled(train):
            logits = model(input_ids, attention_mask, annotator_idx)
            loss   = criterion(logits, labels) / GRAD_ACCUM

        if train:
            loss.backward()
            if (step + 1) % GRAD_ACCUM == 0:
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()

        total_loss    += loss.item() * GRAD_ACCUM
        total_correct += (logits.argmax(-1) == labels).sum().item()
        total_n       += len(labels)

    return total_loss / len(loader), total_correct / total_n

print(f'\nTraining for {N_EPOCHS} epochs...')
best_val_loss = float('inf')
history = []

for epoch in range(1, N_EPOCHS + 1):
    # Freeze encoder for epoch 1, unfreeze from epoch 2
    for p in model.encoder.parameters():
        p.requires_grad = (epoch > 1)

    train_loss, train_acc = run_epoch(train_loader, train=True)
    val_loss,   val_acc   = run_epoch(val_loader,   train=False)
    history.append({'epoch': epoch, 'train_loss': train_loss, 'val_loss': val_loss,
                    'train_acc': train_acc, 'val_acc': val_acc})

    print(f'  Epoch {epoch}/{N_EPOCHS}  '
          f'train_loss={train_loss:.4f}  train_acc={train_acc:.3f}  '
          f'val_loss={val_loss:.4f}  val_acc={val_acc:.3f}')

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), OUT_DIR / 'model_checkpoint.pt')
        print('    → saved best checkpoint')

# Load best checkpoint
model.load_state_dict(torch.load(OUT_DIR / 'model_checkpoint.pt', map_location=device))
print('\nLoaded best checkpoint.')

# ── 9. Evaluation ──────────────────────────────────────────────────────────────
print('\nEvaluating on test set...')
model.eval()
all_preds, all_labels, all_annotators = [], [], []

with torch.no_grad():
    for batch in test_loader:
        logits = model(
            batch['input_ids'].to(device),
            batch['attention_mask'].to(device),
            batch['annotator_idx'].to(device),
        )
        all_preds.extend(logits.argmax(-1).cpu().tolist())
        all_labels.extend(batch['label'].tolist())
        all_annotators.extend(batch['annotator_idx'].tolist())

eval_df = flat_df[flat_df['split_set'] == 'test'].copy()
eval_df['pred_idx']   = all_preds
eval_df['pred_label'] = [idx_to_label[i] for i in all_preds]
eval_df['true_label'] = [idx_to_label[i] for i in all_labels]
eval_df['correct']    = eval_df['pred_idx'] == eval_df['label_idx']

print(f'\nOverall test accuracy: {eval_df["correct"].mean():.3f}')

metrics_rows = []
for key in loaded:
    sub = eval_df[eval_df['annotator_idx'] == model_to_idx[key]]
    acc = sub['correct'].mean()
    f1  = f1_score(sub['label_idx'], sub['pred_idx'], average='macro')
    metrics_rows.append({'model': MODELS[key], 'accuracy': acc, 'macro_f1': f1, 'n': len(sub)})
    print(f'  {MODELS[key]:<20}  acc={acc:.3f}  macro_f1={f1:.3f}  (n={len(sub):,})')

metrics_df = pd.DataFrame(metrics_rows)
metrics_df.to_csv(OUT_DIR / 'per_model_metrics.csv', index=False)

# ── 10. Annotator embedding analysis ──────────────────────────────────────────
print('\nAnalysing annotator embeddings...')
ann_embs = model.get_annotator_embeddings()   # (4, 64)
np.save(OUT_DIR / 'annotator_vectors.npy', ann_embs)

# PCA to 2D
pca     = PCA(n_components=2, random_state=42)
emb_2d  = pca.fit_transform(ann_embs)
var_exp = pca.explained_variance_ratio_
print(f'PCA variance explained: PC1={var_exp[0]:.1%}  PC2={var_exp[1]:.1%}')

# Pairwise cosine similarities
from numpy.linalg import norm
print('\nPairwise cosine similarity between annotator embeddings:')
for i, ki in enumerate(loaded):
    for j, kj in enumerate(loaded):
        if j > i:
            cos = np.dot(ann_embs[i], ann_embs[j]) / (norm(ann_embs[i]) * norm(ann_embs[j]))
            print(f'  {MODELS[ki]:<20} vs {MODELS[kj]:<20}: {cos:.3f}')

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: annotator embedding PCA
ax = axes[0]
colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']
for i, key in enumerate(loaded):
    ax.scatter(emb_2d[i, 0], emb_2d[i, 1],
               color=colors[i], s=300, zorder=5, label=MODELS[key])
    ax.annotate(MODELS[key], (emb_2d[i, 0], emb_2d[i, 1]),
                textcoords='offset points', xytext=(8, 4), fontsize=9)

ax.set_xlabel(f'PC1 ({var_exp[0]:.1%} var)')
ax.set_ylabel(f'PC2 ({var_exp[1]:.1%} var)')
ax.set_title('Learned annotator embeddings (PCA)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Right: per-model accuracy bar
ax = axes[1]
model_names = [MODELS[k] for k in loaded]
accs = [metrics_df[metrics_df['model'] == MODELS[k]]['accuracy'].values[0] for k in loaded]
f1s  = [metrics_df[metrics_df['model'] == MODELS[k]]['macro_f1'].values[0] for k in loaded]
x = np.arange(len(loaded))
ax.bar(x - 0.2, accs, 0.35, label='Accuracy',  color=colors, alpha=0.8)
ax.bar(x + 0.2, f1s,  0.35, label='Macro F1',  color=colors, alpha=0.4)
ax.set_xticks(x)
ax.set_xticklabels([MODELS[k] for k in loaded], rotation=15, fontsize=8)
ax.set_ylabel('Score')
ax.set_title('Per-annotator test performance')
ax.set_ylim(0, 1)
ax.legend(fontsize=8)
ax.axhline(1/5, color='grey', linestyle='--', linewidth=0.8, label='Random (0.20)')

plt.suptitle('Annotator Embedding Analysis', fontsize=12)
plt.tight_layout()
plt.savefig(OUT_DIR / 'annotator_embeddings.png', dpi=150, bbox_inches='tight')
plt.show()
print('Saved: annotator_embeddings.png')

# ── 11. Swap analysis on split chunks ─────────────────────────────────────────
print('\nRunning swap analysis on split chunks...')

# Get test split chunks
test_split_uids = (flat_df[(flat_df['split_set'] == 'test') & flat_df['is_split']]
                   ['chunk_uid'].unique())
print(f'Split chunks in test set: {len(test_split_uids)}')

# For each split chunk, predict label using EACH annotator's embedding
# → shows how annotator identity shifts the predicted label
swap_rows = []
model.eval()

for uid in test_split_uids[:200]:   # cap at 200 for speed
    row = chunks_wide[chunks_wide['chunk_uid'] == uid].iloc[0]
    text = str(row['text']) if pd.notna(row['text']) else ''

    enc = tokenizer(text, max_length=MAX_LENGTH, padding='max_length',
                    truncation=True, return_tensors='pt')
    input_ids      = enc['input_ids'].to(device)
    attention_mask = enc['attention_mask'].to(device)

    with torch.no_grad():
        for key in loaded:
            ann_idx = torch.tensor([model_to_idx[key]], dtype=torch.long).to(device)
            logits  = model(input_ids, attention_mask, ann_idx)
            probs   = torch.softmax(logits, dim=-1).cpu().numpy()[0]
            pred    = idx_to_label[probs.argmax()]
            swap_rows.append({
                'chunk_uid':    uid,
                'bank':         row['bank'],
                'annotator':    MODELS[key],
                'pred_label':   pred,
                'true_label':   row[f'label_{key}'],
                'pred_neutral': probs[label_to_idx['neutral']],
                'pred_stanced': 1 - probs[label_to_idx['neutral']],
                **{f'prob_{l}': probs[i] for i, l in enumerate(LABEL_ORDER)},
            })

swap_df = pd.DataFrame(swap_rows)

# For each chunk, compute predicted label variance across annotators
pivot = swap_df.pivot(index='chunk_uid', columns='annotator', values='pred_label')
pivot['n_unique_preds'] = pivot.apply(lambda r: r.nunique(), axis=1)
pivot['all_agree']      = pivot['n_unique_preds'] == 1

print(f'\nSwap analysis ({len(test_split_uids[:200])} split chunks):')
print(f'  All 4 annotators predict same label: {pivot["all_agree"].mean():.1%}')
print(f'  Mean unique predicted labels per chunk: {pivot["n_unique_preds"].mean():.2f}')

# Plot: mean P(neutral) per annotator for split chunks
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
neutral_probs = swap_df.groupby('annotator')['pred_neutral'].mean().reindex(
    [MODELS[k] for k in loaded])
ax.bar(neutral_probs.index, neutral_probs.values,
       color=colors, alpha=0.8)
ax.set_ylabel('Mean P(neutral) on split chunks')
ax.set_title('How often each annotator predicts neutral\non chunks where models disagreed')
ax.set_ylim(0, 1)
ax.tick_params(axis='x', rotation=15, labelsize=8)
for i, (name, val) in enumerate(neutral_probs.items()):
    ax.text(i, val + 0.01, f'{val:.3f}', ha='center', fontsize=9)

ax = axes[1]
agree_counts = pivot['n_unique_preds'].value_counts().sort_index()
ax.bar(agree_counts.index.astype(str), agree_counts.values, color='#888888', alpha=0.8)
ax.set_xlabel('Unique predicted labels across annotators')
ax.set_ylabel('Number of chunks')
ax.set_title('Prediction diversity on split chunks\n(1 = all annotators agree)')

plt.suptitle('Swap Analysis: How Annotator Identity Shifts Predictions on Contested Chunks',
             fontsize=11)
plt.tight_layout()
plt.savefig(OUT_DIR / 'swap_analysis.png', dpi=150, bbox_inches='tight')
plt.show()
print('Saved: swap_analysis.png')

# ── 12. Summary ───────────────────────────────────────────────────────────────
print('\n' + '='*60)
print('DONE. Outputs in /content/output/:')
for f in sorted(OUT_DIR.iterdir()):
    print(f'  {f.name}')
print('='*60)
print('\nKey questions to read from outputs:')
print('  annotator_embeddings.png — are any models far apart in embedding space?')
print('  swap_analysis.png        — which annotator most often predicts neutral')
print('                             on chunks the real models split on?')
print('  per_model_metrics.csv    — which annotator is hardest to learn?')
print('                             (low F1 = more idiosyncratic labeling style)')

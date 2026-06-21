# %% [markdown]
# # Chain-of-Thought Reasoning Extraction on Most-Polarized Chunks
#
# For the chunks where llama33 and deepseekv3 disagree most (sorted by score
# delta: |score_llama - score_deepseek|), ask each model to reason step-by-step
# before classifying.
#
# The structured prompt forces each model to:
#   1. List hawkish signals it sees
#   2. List dovish signals it sees
#   3. Explain how it weights them
#   4. Give a label
#
# This externalises the decision process and makes the threshold difference
# directly visible: both models may name the same signals but weight them
# differently — or one model may "see" a signal the other doesn't.
#
# Run: uv run python notebooks/reasoning_extraction.py

# %% Imports
import re
import sys
import json
import asyncio
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter

warnings.filterwarnings('ignore')

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'output' / 'stance'
sys.path.insert(0, str(ROOT / 'src' / 'llm'))

from dotenv import load_dotenv
load_dotenv(ROOT / '.env', override=True)

from score_openrouter import (
    _make_client, _call_api_async,
    AsyncRateLimiter, parse_stance5,
    MODEL_SPECS, SYSTEM_PROMPT,
)

MODELS = {
    'llama33':    'Llama 3.3',
    'deepseekv3': 'DeepSeek V3',
}
STANCE_SCORE = {'dovish': -1.0, 'mostly dovish': -0.5, 'neutral': 0.0,
                'mostly hawkish': 0.5, 'hawkish': 1.0}
DIRECTIONAL  = ['dovish', 'mostly dovish', 'mostly hawkish', 'hawkish']
N_SAMPLE     = 50   # total chunks to analyse

# %% Load predictions and build polarization ranking
print('Loading predictions...')
loaded = []
all_chunks = {}
for key in MODELS:
    path = OUT_DIR / f'chunk_predictions_{key}.csv'
    if not path.exists():
        print(f'  {key}: not found, skipping')
        continue
    df = pd.read_csv(path)
    df = df[df['label'].isin(STANCE_SCORE)].copy()
    df['score'] = df['label'].map(STANCE_SCORE)
    all_chunks[key] = df
    loaded.append(key)
    print(f'  {key}: {len(df):,} chunks')

if len(loaded) < 2:
    raise RuntimeError('Need at least 2 models. Check output/stance/ for chunk_predictions_*.csv')

base_cols = ['chunk_uid', 'bank', 'date', 'text']

chunks_wide = (all_chunks[loaded[0]][base_cols + ['label', 'score']]
               .rename(columns={'label': f'label_{loaded[0]}',
                                'score': f'score_{loaded[0]}'}))
for key in loaded[1:]:
    chunks_wide = chunks_wide.merge(
        all_chunks[key][['chunk_uid', 'label', 'score']].rename(
            columns={'label': f'label_{key}', 'score': f'score_{key}'}),
        on='chunk_uid')

# Score delta = maximum pairwise distance across loaded models
from itertools import combinations
pairs = list(combinations(loaded, 2))
chunks_wide['score_delta'] = chunks_wide.apply(
    lambda r: max(abs(r[f'score_{a}'] - r[f'score_{b}']) for a, b in pairs),
    axis=1)
chunks_wide['word_count'] = chunks_wide['text'].str.split().str.len()

# Label delta description
def delta_desc(row):
    labels = {k: row[f'label_{k}'] for k in loaded}
    return ' vs '.join(f'{MODELS[k]}={labels[k]}' for k in loaded)
chunks_wide['label_desc'] = chunks_wide.apply(delta_desc, axis=1)

print(f'\nchunks_wide: {len(chunks_wide):,}')
print('Score delta distribution:')
print(chunks_wide['score_delta'].value_counts().sort_index(ascending=False).head(8))

# %% Select sample: all max-delta first, then fill to N_SAMPLE by delta desc
sample = (chunks_wide[chunks_wide['score_delta'] > 0]
          .sort_values(['score_delta', 'word_count'], ascending=[False, False])
          .head(N_SAMPLE)
          .reset_index(drop=True))

print(f'\nSample: {len(sample)} chunks')
print(f'  delta=2.0: {(sample["score_delta"]==2.0).sum()}')
print(f'  delta=1.5: {(sample["score_delta"]==1.5).sum()}')
print(f'  delta=1.0: {(sample["score_delta"]==1.0).sum()}')
print(f'  delta=0.5: {(sample["score_delta"]==0.5).sum()}')

# %% CoT prompt
COT_PROMPT = """\
You are an expert in monetary policy communication.

Read the following excerpt from a central bank press conference carefully.

Before classifying, reason through the text step by step:
1. List any signals in the text pointing toward a HAWKISH stance — tightening bias, \
rate hike language, inflation above target, restrictive, elevated, vigilant, sustained pressure.
2. List any signals in the text pointing toward a DOVISH stance — easing bias, \
rate cut language, growth concern, below-target inflation, support, accommodate, stimulus, slack.
3. Explain in 1-3 sentences how you weigh these signals against each other and \
why the overall stance is what it is.

Return JSON only:
{{
  "hawkish_signals": ["exact phrase or close paraphrase from the text", ...],
  "dovish_signals":  ["exact phrase or close paraphrase from the text", ...],
  "reasoning": "1-3 sentences weighing the signals and explaining your conclusion",
  "label": "<dovish|mostly dovish|neutral|mostly hawkish|hawkish>",
  "confidence": "<low|medium|high>"
}}

Excerpt:
{text}"""


def parse_cot_response(raw: str) -> dict:
    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            return {}
        parsed = json.loads(match.group())
        return {
            'hawkish_signals': parsed.get('hawkish_signals', []),
            'dovish_signals':  parsed.get('dovish_signals', []),
            'reasoning':       str(parsed.get('reasoning', '')),
            'label':           parse_stance5(str(parsed.get('label', ''))),
            'confidence':      str(parsed.get('confidence', 'low')),
        }
    except Exception:
        return {}


# %% Async CoT extraction
LOG_EVERY = 5

async def extract_cot_model(key: str, texts_with_idx: list[tuple[int, str]]) -> dict[int, dict]:
    spec    = MODEL_SPECS[key]
    client  = _make_client(spec)
    limiter = AsyncRateLimiter(rpm=spec.rpm, burst=3)
    results: dict[int, dict] = {}
    n = len(texts_with_idx)
    print(f'  [{MODELS[key]}] start — {n} chunks @ {spec.rpm} RPM (est. {n*60//spec.rpm}s)')

    for done, (idx, text) in enumerate(texts_with_idx):
        try:
            raw = await _call_api_async(
                client, spec.slug, spec.tag,
                COT_PROMPT.format(text=text),
                temperature=0.0,
                rate_limiter=limiter,
                max_tokens=800,
            )
            parsed = parse_cot_response(raw)
        except Exception as e:
            print(f'  [{MODELS[key]}] chunk {idx} error: {e}')
            parsed = {}
        results[idx] = parsed

        if (done + 1) % LOG_EVERY == 0 or (done + 1) == n:
            print(f'  [{MODELS[key]}] {done+1}/{n} done')

    print(f'  [{MODELS[key]}] complete — {len(results)} chunks')
    return results


async def run_all_cot(texts: list[tuple[int, str]]) -> dict[str, dict[int, dict]]:
    print(f'\nExtracting CoT reasoning: {len(texts)} chunks × {len(loaded)} models in parallel...')
    tasks   = [extract_cot_model(key, texts) for key in loaded]
    results = await asyncio.gather(*tasks)
    return dict(zip(loaded, results))


texts_indexed = [(i, str(row['text'])) for i, row in sample.iterrows()]
cot_results   = asyncio.run(run_all_cot(texts_indexed))
print('Done.')

# %% Build flat results table
rows = []
for i, row in sample.iterrows():
    for key in loaded:
        r = cot_results[key].get(i, {})
        rows.append({
            'chunk_uid':       row['chunk_uid'],
            'bank':            row['bank'],
            'date':            row['date'],
            'score_delta':     row['score_delta'],
            'word_count':      row['word_count'],
            'orig_label':      row[f'label_{key}'],       # original zero-shot label
            'orig_score':      row[f'score_{key}'],
            'cot_label':       r.get('label', 'parse_error'),
            'cot_confidence':  r.get('confidence', ''),
            'hawkish_signals': ' | '.join(r.get('hawkish_signals', [])),
            'n_hawkish':       len(r.get('hawkish_signals', [])),
            'dovish_signals':  ' | '.join(r.get('dovish_signals', [])),
            'n_dovish':        len(r.get('dovish_signals', [])),
            'reasoning':       r.get('reasoning', ''),
            'model':           key,
            'model_name':      MODELS[key],
            'label_desc':      row['label_desc'],
            'text':            str(row['text']),
        })

cot_df = pd.DataFrame(rows)
cot_df['label_match'] = cot_df['cot_label'] == cot_df['orig_label']

print(f'\nCoT label match with original zero-shot:')
for key in loaded:
    sub = cot_df[cot_df['model'] == key]
    print(f'  {MODELS[key]}: {sub["label_match"].mean():.0%} match '
          f'({sub["label_match"].sum()}/{len(sub)})')

# %% Side-by-side display
print(f'\n{"="*72}')
print('SIDE-BY-SIDE REASONING COMPARISON (top chunks by delta)')
print(f'{"="*72}')

pd.set_option('display.max_colwidth', 120)

N_SHOW = min(15, len(sample))
for i in range(N_SHOW):
    row = sample.iloc[i]
    print(f'\n[{i+1}] {row["bank"]} | {str(row["date"])[:8]} | delta={row["score_delta"]:.1f} | {row["label_desc"]}')
    print(f'     Text ({row["word_count"]} words): {str(row["text"])[:300]}...')
    for key in loaded:
        r = cot_results[key].get(i, {})
        hawk = ' / '.join(r.get('hawkish_signals', [])[:3]) or '—'
        dove = ' / '.join(r.get('dovish_signals', [])[:3]) or '—'
        reason = r.get('reasoning', '')[:200]
        label  = r.get('label', '?')
        orig   = row[f'label_{key}']
        match  = '✓' if label == orig else f'→{orig}'
        print(f'  {MODELS[key]:<15} [{label}] {match}')
        print(f'    Hawkish: {hawk}')
        print(f'    Dovish:  {dove}')
        print(f'    Reason:  {reason}')

# %% Signal overlap analysis
print(f'\n{"="*60}')
print('SIGNAL OVERLAP ANALYSIS')
print('="*60')
print('For chunks where the two models disagree:')
print('Do both models SEE the same signals but weigh them differently?')
print('Or does one model see signals the other does not?')
print()

signal_rows = []
for i, row in sample.iterrows():
    if len(loaded) < 2:
        break
    r0 = cot_results[loaded[0]].get(i, {})
    r1 = cot_results[loaded[1]].get(i, {})

    hawk0 = set(s.lower() for s in r0.get('hawkish_signals', []))
    hawk1 = set(s.lower() for s in r1.get('hawkish_signals', []))
    dove0 = set(s.lower() for s in r0.get('dovish_signals', []))
    dove1 = set(s.lower() for s in r1.get('dovish_signals', []))

    # Jaccard overlap
    def jaccard(a, b):
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        # word-level overlap since phrases may be paraphrased
        wa = set(' '.join(a).split())
        wb = set(' '.join(b).split())
        return len(wa & wb) / len(wa | wb)

    signal_rows.append({
        'chunk_uid':           row['chunk_uid'],
        'score_delta':         row['score_delta'],
        'hawk_jaccard':        jaccard(hawk0, hawk1),
        'dove_jaccard':        jaccard(dove0, dove1),
        f'n_hawk_{loaded[0]}': len(hawk0),
        f'n_hawk_{loaded[1]}': len(hawk1),
        f'n_dove_{loaded[0]}': len(dove0),
        f'n_dove_{loaded[1]}': len(dove1),
        f'label_{loaded[0]}':  r0.get('label', ''),
        f'label_{loaded[1]}':  r1.get('label', ''),
    })

sig_df = pd.DataFrame(signal_rows)

print('Mean word-level Jaccard overlap in named signals:')
print(f'  Hawkish signals overlap: {sig_df["hawk_jaccard"].mean():.3f}')
print(f'  Dovish  signals overlap: {sig_df["dove_jaccard"].mean():.3f}')
print()
print('Mean signals named per model:')
for key in loaded:
    h = sig_df[f'n_hawk_{key}'].mean()
    d = sig_df[f'n_dove_{key}'].mean()
    print(f'  {MODELS[key]:<15}: hawkish={h:.1f}  dovish={d:.1f}')

# Correlation between Jaccard overlap and score delta
from scipy.stats import pearsonr
r_h, p_h = pearsonr(sig_df['score_delta'], sig_df['hawk_jaccard'])
r_d, p_d = pearsonr(sig_df['score_delta'], sig_df['dove_jaccard'])
print(f'\nCorr(delta, hawk_jaccard)={r_h:.3f} p={p_h:.3f}')
print(f'Corr(delta, dove_jaccard)={r_d:.3f} p={p_d:.3f}')
print('(Negative = higher disagreement → less signal overlap)')

# %% Vocabulary analysis: what words appear in each model's reasoning?
print(f'\n{"="*60}')
print('REASONING VOCABULARY — what words does each model use?')
print('For max-delta chunks only (score_delta >= 1.5)')
print()

max_delta_idx = set(sample[sample['score_delta'] >= 1.5].index)

for key in loaded:
    sub = cot_df[(cot_df['model'] == key) &
                 (cot_df['chunk_uid'].isin(
                     sample[sample['score_delta'] >= 1.5]['chunk_uid']))]
    all_text = ' '.join(sub['reasoning'].tolist() +
                        sub['hawkish_signals'].tolist() +
                        sub['dovish_signals'].tolist()).lower()
    words = re.findall(r'\b[a-z]{4,}\b', all_text)
    STOP = {'that','this','with','from','have','they','been','will','when',
            'their','also','more','which','were','into','than','then','what',
            'about','some','there','could','would','does','overall','text',
            'excerpt','these','those','most','while','very','such','well',
            'both','because','suggests','indicates','language','central',
            'bank','monetary','policy','signals','stance','signal','model',
            'however','although','despite','clear','rather','given'}
    top = [(w, c) for w, c in Counter(words).most_common(20) if w not in STOP]
    label_dist = sub['cot_label'].value_counts().to_dict()
    print(f'  {MODELS[key]}: {label_dist}')
    print(f'    Top reasoning words: {", ".join(f"{w}({c})" for w,c in top[:12])}')
    print()

# %% Plot
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 1. CoT label match rate
ax = axes[0]
match_rates = [cot_df[cot_df['model'] == k]['label_match'].mean() for k in loaded]
ax.bar([MODELS[k].split()[0] for k in loaded], match_rates, color='#4C72B0', alpha=0.8)
ax.set_ylim(0, 1)
ax.axhline(1.0, color='grey', linestyle='--', linewidth=0.8)
ax.set_ylabel('Agreement rate with original label')
ax.set_title('CoT label vs original\nzero-shot label')
for i, v in enumerate(match_rates):
    ax.text(i, v + 0.02, f'{v:.0%}', ha='center')

# 2. Signal overlap vs delta
ax = axes[1]
ax.scatter(sig_df['score_delta'] + np.random.uniform(-0.05, 0.05, len(sig_df)),
           sig_df['hawk_jaccard'], alpha=0.6, label='Hawkish', color='#C44E52')
ax.scatter(sig_df['score_delta'] + np.random.uniform(-0.05, 0.05, len(sig_df)),
           sig_df['dove_jaccard'], alpha=0.6, label='Dovish',  color='#4C72B0')
ax.set_xlabel('Score delta between models')
ax.set_ylabel('Word-level Jaccard (signal overlap)')
ax.set_title('Do models name the same signals\nwhen they disagree more?')
ax.legend()

# 3. Mean signals named per model
ax = axes[2]
x = np.arange(len(loaded))
hawk_means = [sig_df[f'n_hawk_{k}'].mean() for k in loaded]
dove_means = [sig_df[f'n_dove_{k}'].mean() for k in loaded]
ax.bar(x - 0.2, hawk_means, 0.35, label='Hawkish signals', color='#C44E52', alpha=0.8)
ax.bar(x + 0.2, dove_means, 0.35, label='Dovish signals',  color='#4C72B0', alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels([MODELS[k].split()[0] for k in loaded])
ax.set_ylabel('Mean signals named per chunk')
ax.set_title('How many signals does each\nmodel identify?')
ax.legend()

plt.suptitle('CoT Reasoning Extraction — Most-Polarized Chunks', fontsize=11)
plt.tight_layout()
plt.savefig(OUT_DIR / 'reasoning_cot_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# %% Save
cot_df.to_csv(OUT_DIR / 'reasoning_cot_results.csv', index=False)
sig_df.to_csv(OUT_DIR / 'reasoning_signal_overlap.csv', index=False)
print(f'\nSaved: reasoning_cot_results.csv ({len(cot_df)} rows)')
print(f'Saved: reasoning_signal_overlap.csv ({len(sig_df)} rows)')

# %% Summary
print('\n' + '='*60)
print('SUMMARY')
print('='*60)
print(f'Chunks analysed: {len(sample)}')
print(f'  Max delta (delta=2.0): {(sample["score_delta"]==2.0).sum()}')
print(f'  High delta (delta=1.5): {(sample["score_delta"]==1.5).sum()}')
for key in loaded:
    sub = cot_df[cot_df['model'] == key]
    match = sub['label_match'].mean()
    print(f'{MODELS[key]}: CoT label matches zero-shot in {match:.0%} of cases')
print(f'\nMean signal overlap (Jaccard): hawk={sig_df["hawk_jaccard"].mean():.3f}'
      f'  dove={sig_df["dove_jaccard"].mean():.3f}')

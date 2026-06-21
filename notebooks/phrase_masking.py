# %% [markdown]
# # Phrase Masking — Two-Pass Attribution on Top-100 Split Chunks
#
# Split chunks: exactly 2 models say stanced, 2 say neutral.
#
# Pass 1 (extract): Each model classifies the chunk AND names 3-8 key phrases
#   that drove its classification. One API call per (chunk × model).
#
# Pass 2 (mask): Pool all unique phrases identified by any model (per chunk).
#   Mask each phrase and re-score with ALL 4 models in sub-batches of 5.
#
# Key outputs:
# - Which phrases each model self-reports as stance-critical
# - Which phrases actually cause each model to flip when removed
# - Self-calibration: did the model that named a phrase actually flip on it?
# - Cross-attribution: did removing DeepSeek's phrase flip Llama too?
#
# Run: uv run python notebooks/phrase_masking.py

# %% Imports
import re
import sys
import json
import asyncio
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

warnings.filterwarnings('ignore')

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'output' / 'stance'
sys.path.insert(0, str(ROOT / 'src' / 'llm'))

from dotenv import load_dotenv
load_dotenv(ROOT / '.env', override=True)

from score_openrouter import (
    _make_client, _call_api_async,
    classify_batch_async, AsyncRateLimiter,
    parse_stance5, MODEL_SPECS, SYSTEM_PROMPT,
)

MODELS = {
    'llama33':         'Llama 3.3',
    'deepseekv3':      'DeepSeek V3',
    'qwen25_72b':      'Qwen 2.5',
    'mistrallarge_or': 'Mistral Large',
}
STANCE_SCORE = {'dovish': -1.0, 'mostly dovish': -0.5, 'neutral': 0.0,
                'mostly hawkish': 0.5, 'hawkish': 1.0}
DIRECTIONAL  = ['dovish', 'mostly dovish', 'mostly hawkish', 'hawkish']

SUB_BATCH = 5   # max variants per masking API call (keeps context + output small)

# %% Load chunks_wide
print('Loading predictions...')
loaded = []
all_chunks = {}
for key in MODELS:
    path = OUT_DIR / f'chunk_predictions_{key}.csv'
    if not path.exists():
        print(f'  {key}: not found')
        continue
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y%m%d')
    df = df[df['label'].isin(STANCE_SCORE)].copy()
    df['score'] = df['label'].map(STANCE_SCORE)
    all_chunks[key] = df
    loaded.append(key)
    print(f'  {key}: {len(df):,} chunks')

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

chunks_wide['n_stanced'] = chunks_wide[[f'stanced_{k}' for k in loaded]].sum(axis=1)
chunks_wide['split']     = chunks_wide['n_stanced'].between(1, len(loaded) - 1)

print(f'\nchunks_wide: {len(chunks_wide):,} | split: {chunks_wide["split"].mean():.1%}')

# %% Select top-100 split chunks
top100 = (chunks_wide[chunks_wide['n_stanced'] == 2]
          .assign(word_count=lambda df: df['text'].str.split().str.len())
          .sort_values('word_count', ascending=False)
          .head(100)
          .reset_index(drop=True))

print(f'Top-100 split chunks:')
print(f'  Banks: {top100["bank"].value_counts().to_dict()}')
print(f'  Word count: mean={top100["word_count"].mean():.0f} '
      f'min={top100["word_count"].min()} max={top100["word_count"].max()}')
for key in loaded:
    print(f'  {MODELS[key]:<15}: {top100[f"stanced_{key}"].sum()}/100 say stanced')

# %% Pass 1 — phrase extraction prompt
EXTRACT_PROMPT = """\
Classify the monetary policy stance expressed in the following excerpt from a central bank press conference.

Then identify 3 to 8 key phrases — exact substrings from the text — that most drove your classification. \
Focus on phrases that contain clear policy signals (rate guidance, inflation assessment, growth outlook, risk language).

Return JSON only, with exactly these keys:
{{
  "label": "<dovish|mostly dovish|neutral|mostly hawkish|hawkish>",
  "confidence": "<low|medium|high>",
  "key_phrases": ["exact phrase 1", "exact phrase 2", ...]
}}

Excerpt:
{text}"""


def build_extract_prompt(text: str) -> str:
    return EXTRACT_PROMPT.format(text=text)


def parse_extract_response(raw: str, text: str) -> tuple[str, str, list[str]]:
    """Parse extraction response. Validates phrases are literal substrings."""
    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            return 'neutral', 'low', []
        parsed = json.loads(match.group())
        label      = parse_stance5(str(parsed.get('label', '')))
        confidence = str(parsed.get('confidence', 'low'))
        raw_phrases = parsed.get('key_phrases', [])
        # Only keep phrases that are literal substrings (model might hallucinate)
        phrases = [p for p in raw_phrases if isinstance(p, str) and p.strip() in text]
        return label, confidence, phrases
    except Exception:
        return 'neutral', 'low', []


# %% Pass 1 — async extraction
LOG_EVERY = 10  # print progress every N chunks

async def extract_for_model(key: str, texts_with_idx: list[tuple[int, str]]) -> dict[int, tuple[str, str, list[str]]]:
    """Run extraction pass for one model. Returns {chunk_idx: (label, confidence, phrases)}."""
    spec    = MODEL_SPECS[key]
    client  = _make_client(spec)
    limiter = AsyncRateLimiter(rpm=spec.rpm, burst=3)
    results: dict[int, tuple[str, str, list[str]]] = {}
    n_total = len(texts_with_idx)

    print(f'  [{MODELS[key]}] Pass 1 start — {n_total} chunks @ {spec.rpm} RPM '
          f'(est. {n_total * 60 // spec.rpm}s)')

    for done, (chunk_idx, text) in enumerate(texts_with_idx):
        try:
            raw = await _call_api_async(
                client, spec.slug, spec.tag,
                build_extract_prompt(text),
                temperature=0.0,
                rate_limiter=limiter,
                max_tokens=512,
            )
            label, conf, phrases = parse_extract_response(raw, text)
        except Exception as e:
            print(f'  [{MODELS[key]}] chunk {chunk_idx} error: {e}')
            label, conf, phrases = 'neutral', 'low', []
        results[chunk_idx] = (label, conf, phrases)

        if (done + 1) % LOG_EVERY == 0 or (done + 1) == n_total:
            n_phrases = sum(len(r[2]) for r in results.values())
            print(f'  [{MODELS[key]}] Pass 1: {done+1}/{n_total} done '
                  f'({n_phrases} phrases so far)')

    print(f'  [{MODELS[key]}] Pass 1 complete — {len(results)} chunks, '
          f'{sum(len(r[2]) for r in results.values())} phrases extracted')
    return results


async def run_extraction(texts: list[tuple[int, str]]) -> dict[str, dict[int, tuple[str, str, list[str]]]]:
    print(f'\nPass 1: extracting key phrases from {len(texts)} chunks × {len(loaded)} models...')
    tasks = [extract_for_model(key, texts) for key in loaded]
    results_list = await asyncio.gather(*tasks)
    return dict(zip(loaded, results_list))


texts_indexed = [(i, str(row['text'])) for i, row in top100.iterrows()]
extraction = asyncio.run(run_extraction(texts_indexed))

# %% Build phrase pool per chunk
print('\nBuilding phrase pool per chunk...')
chunk_meta     = []
phrase_pool    = []   # list of list[str]: unique phrases per chunk, across all models
phrase_sources = []   # list of dict: phrase -> set of models that identified it

for i, row in top100.iterrows():
    text = str(row['text'])
    llm_labels     = {k: row[f'label_{k}'] for k in loaded}
    stanced_models = [k for k in loaded if row[f'stanced_{k}']]
    neutral_models = [k for k in loaded if not row[f'stanced_{k}']]

    # Pool phrases, tracking which model(s) identified each
    src: dict[str, set] = {}
    for key in loaded:
        _, _, phrases = extraction[key].get(i, ('neutral', 'low', []))
        for p in phrases:
            src.setdefault(p, set()).add(key)

    chunk_meta.append({
        'chunk_uid':      row['chunk_uid'],
        'bank':           row['bank'],
        'doc_id':         row['doc_id'],
        'date':           row['date'],
        'text':           text,
        'word_count':     len(text.split()),
        'orig_labels':    llm_labels,
        'stanced_models': stanced_models,
        'neutral_models': neutral_models,
    })
    phrase_pool.append(list(src.keys()))
    phrase_sources.append(src)

total_phrases = sum(len(p) for p in phrase_pool)
print(f'  {total_phrases} total unique phrases across 100 chunks '
      f'(mean {total_phrases/100:.1f} per chunk)')
print(f'  Chunks with 0 phrases: {sum(1 for p in phrase_pool if not p)}')

# %% Masking helper
def apply_mask(text: str, phrase: str) -> str:
    masked = text.replace(phrase, ' ').strip()
    masked = re.sub(r'\s{2,}', ' ', masked)
    masked = re.sub(r'\.\s+\.', '.', masked)
    return masked

# %% Pass 2 — masking + re-scoring
async def score_masked_model(key: str, chunk_data: list[tuple[int, list[str], list[str]]]) -> dict[int, list[str]]:
    """
    chunk_data: list of (chunk_idx, phrases, variants)
      variants[0] = original text, variants[1..] = masked texts (one per phrase)
    Returns: {chunk_idx: [label_original, label_masked_1, label_masked_2, ...]}
    """
    spec    = MODEL_SPECS[key]
    client  = _make_client(spec)
    limiter = AsyncRateLimiter(rpm=spec.rpm, burst=3)
    out: dict[int, list[str]] = {}
    n_total = len(chunk_data)

    # Count total API calls upfront so we can estimate time
    n_calls = sum(
        max(1, (len(v) + SUB_BATCH - 1) // SUB_BATCH)
        for _, _, v in chunk_data if v
    )
    print(f'  [{MODELS[key]}] Pass 2 start — {n_total} chunks, '
          f'~{n_calls} API calls @ {spec.rpm} RPM (est. {n_calls * 60 // spec.rpm}s)')

    for done, (chunk_idx, phrases, variants) in enumerate(chunk_data):
        if not variants:
            out[chunk_idx] = []
            continue
        label_map: dict[int, str] = {}
        for batch_start in range(0, len(variants), SUB_BATCH):
            batch      = variants[batch_start: batch_start + SUB_BATCH]
            batch_idxs = list(range(batch_start, batch_start + len(batch)))
            valid = [(vi, v) for vi, v in zip(batch_idxs, batch) if len(v.split()) >= 5]
            if not valid:
                continue
            valid_idxs, valid_texts = zip(*valid)
            try:
                preds = await classify_batch_async(
                    client, list(valid_texts), spec.slug, spec.tag, 0.0, limiter
                )
                for vi, (lbl, _) in zip(valid_idxs, preds):
                    label_map[vi] = lbl
            except Exception as e:
                print(f'  [{MODELS[key]}] mask chunk {chunk_idx} @{batch_start}: {e}')
        out[chunk_idx] = [label_map.get(i, 'neutral') for i in range(len(variants))]

        if (done + 1) % LOG_EVERY == 0 or (done + 1) == n_total:
            print(f'  [{MODELS[key]}] Pass 2: {done+1}/{n_total} chunks done')

    print(f'  [{MODELS[key]}] Pass 2 complete — {len(out)} chunks scored')
    return out


async def run_masking(chunk_data):
    print(f'\nPass 2: masking + re-scoring {len(chunk_data)} chunks × {len(loaded)} models...')
    tasks = [score_masked_model(key, chunk_data) for key in loaded]
    results_list = await asyncio.gather(*tasks)
    return dict(zip(loaded, results_list))


# Build (chunk_idx, phrases, variants) tuples
mask_data = []
for i, (phrases, meta) in enumerate(zip(phrase_pool, chunk_meta)):
    text = meta['text']
    variants = [text] + [apply_mask(text, p) for p in phrases]
    mask_data.append((i, phrases, variants))

mask_scores = asyncio.run(run_masking(mask_data))
print('Both passes complete.')

# %% Analyse results
print('\nAnalysing...')
results = []

for i, (meta, phrases, src_map) in enumerate(zip(chunk_meta, phrase_pool, phrase_sources)):
    if not phrases:
        continue

    orig_labels  = meta['orig_labels']
    orig_stanced = {k: orig_labels[k] in DIRECTIONAL for k in loaded}
    orig_n       = sum(orig_stanced.values())

    phrase_rows = []
    for j, phrase in enumerate(phrases):
        vi = j + 1  # variant index in mask_scores (0 = original)
        masked_labels  = {}
        masked_stanced = {}
        for key in loaded:
            vals = mask_scores[key].get(i, [])
            ml = vals[vi] if vi < len(vals) else 'neutral'
            masked_labels[key]  = ml
            masked_stanced[key] = ml in DIRECTIONAL

        masked_n = sum(masked_stanced.values())

        flipped_to_neutral = [k for k in loaded if orig_stanced[k] and not masked_stanced[k]]
        flipped_to_stanced = [k for k in loaded if not orig_stanced[k] and masked_stanced[k]]
        n_flipped          = len(flipped_to_neutral) + len(flipped_to_stanced)

        # Self-calibration: for each model that named this phrase, did it flip?
        identifiers = list(src_map[phrase])
        self_calibrated = [k for k in identifiers
                           if (orig_stanced[k] and not masked_stanced[k])
                           or (not orig_stanced[k] and masked_stanced[k])]

        resolves = (0 < orig_n < len(loaded)) and not (0 < masked_n < len(loaded))

        phrase_rows.append({
            'chunk_uid':           meta['chunk_uid'],
            'bank':                meta['bank'],
            'phrase':              phrase,
            'phrase_words':        len(phrase.split()),
            'identified_by':       ', '.join(MODELS[k] for k in identifiers),
            'n_identifiers':       len(identifiers),
            'self_calibrated':     ', '.join(MODELS[k] for k in self_calibrated),
            'n_self_calibrated':   len(self_calibrated),
            'flipped_to_neutral':  ', '.join(MODELS[k] for k in flipped_to_neutral),
            'flipped_to_stanced':  ', '.join(MODELS[k] for k in flipped_to_stanced),
            'n_flipped':           n_flipped,
            'resolves':            resolves,
            'orig_n_stanced':      orig_n,
            'masked_n_stanced':    masked_n,
            **{f'orig_{k}':   orig_labels[k]   for k in loaded},
            **{f'masked_{k}': masked_labels[k] for k in loaded},
        })

    pr_df = pd.DataFrame(phrase_rows) if phrase_rows else pd.DataFrame()

    # Pick critical phrase: resolving first, then most-flipped
    if len(pr_df) > 0:
        resolving = pr_df[pr_df['resolves']]
        if len(resolving) > 0:
            crit = resolving.sort_values('n_flipped', ascending=False).iloc[0]
        else:
            crit = pr_df.sort_values('n_flipped', ascending=False).iloc[0]
    else:
        crit = pd.Series(dtype=object)

    results.append({
        'chunk_uid':            meta['chunk_uid'],
        'bank':                 meta['bank'],
        'doc_id':               meta['doc_id'],
        'date':                 meta['date'],
        'text':                 meta['text'],
        'word_count':           meta['word_count'],
        'stanced_models':       ', '.join(MODELS[k] for k in meta['stanced_models']),
        'neutral_models':       ', '.join(MODELS[k] for k in meta['neutral_models']),
        **{f'orig_{k}': orig_labels[k] for k in loaded},
        'n_phrases_pooled':     len(phrases),
        'n_resolving':          len(pr_df[pr_df['resolves']]) if len(pr_df) else 0,
        'any_resolves':         bool(len(pr_df[pr_df['resolves']])) if len(pr_df) else False,
        'critical_phrase':      crit.get('phrase', '') if len(crit) else '',
        'critical_resolves':    crit.get('resolves', False) if len(crit) else False,
        'critical_identified_by': crit.get('identified_by', '') if len(crit) else '',
        'critical_self_cal':    crit.get('self_calibrated', '') if len(crit) else '',
        'critical_flipped_to_neutral': crit.get('flipped_to_neutral', '') if len(crit) else '',
        'critical_flipped_to_stanced': crit.get('flipped_to_stanced', '') if len(crit) else '',
        'critical_n_flipped':   int(crit.get('n_flipped', 0)) if len(crit) else 0,
        '_phrase_df':           pr_df,
    })

occ_df    = pd.DataFrame([{k: v for k, v in r.items() if k != '_phrase_df'} for r in results])
n_resolves = int(occ_df['any_resolves'].sum())
print(f'\n{len(occ_df)} chunks analysed.')
print(f'Disagreement resolved by single phrase: {n_resolves}/{len(occ_df)} ({n_resolves/len(occ_df):.1%})')

# %% Display
pd.set_option('display.max_colwidth', 90)
resolved = occ_df[occ_df['any_resolves']].sort_values('critical_n_flipped', ascending=False)

print('\n=== Resolved chunks — critical phrase summary ===\n')
disp_cols = ['bank', 'date', 'stanced_models', 'neutral_models',
             'critical_phrase', 'critical_identified_by', 'critical_flipped_to_neutral',
             'critical_self_cal', 'critical_n_flipped']
print(resolved[disp_cols].head(20).to_string(index=False))

# %% Self-calibration summary
print('\n=== Self-calibration per model ===')
print('(Did the model that named a phrase actually flip when it was removed?)\n')
all_phrase_rows = [r for res in results for r in res['_phrase_df'].to_dict('records')]
pr_all = pd.DataFrame(all_phrase_rows) if all_phrase_rows else pd.DataFrame()
# chunk_uid and bank are already embedded in each phrase row

for key in loaded:
    mname = MODELS[key]
    if len(pr_all) == 0:
        continue
    named  = pr_all[pr_all['identified_by'].str.contains(mname, na=False)]
    cal    = named[named['self_calibrated'].str.contains(mname, na=False)]
    flipped_any = named[named['n_flipped'] > 0]
    print(f'  {mname:<20}: named {len(named):3d} phrases | '
          f'self-flipped {len(cal):3d} ({len(cal)/max(len(named),1):.0%}) | '
          f'caused any flip {len(flipped_any):3d} ({len(flipped_any)/max(len(named),1):.0%})')

# %% Cross-attribution matrix
print('\n=== Cross-attribution: which model\'s phrases flip which other models? ===')
print('(Row = model that identified the phrase; Col = model that flipped)\n')
mat = np.zeros((len(loaded), len(loaded)), dtype=int)
for _, pr_row in pr_all.iterrows():
    if not isinstance(pr_row.get('identified_by'), str):
        continue
    for ri, rk in enumerate(loaded):
        if MODELS[rk] not in pr_row['identified_by']:
            continue
        for ci, ck in enumerate(loaded):
            flipped_col = 'flipped_to_neutral' if str(pr_row.get(f'orig_{ck}', '')) in DIRECTIONAL \
                          else 'flipped_to_stanced'
            if MODELS[ck] in str(pr_row.get('flipped_to_neutral', '')) \
               or MODELS[ck] in str(pr_row.get('flipped_to_stanced', '')):
                mat[ri, ci] += 1

mat_df = pd.DataFrame(mat, index=[MODELS[k] for k in loaded],
                      columns=[MODELS[k] for k in loaded])
print(mat_df.to_string())
print('\nRead: row model named the phrase; col model flipped when that phrase was masked.')
print('Diagonal = self-calibration count.')

# %% Rich text display
N_SHOW = 8
print(f'\n{"="*70}')
print(f'Top {N_SHOW} resolved chunks — annotated text')
print(f'{"="*70}')
for idx, (_, row) in enumerate(resolved.head(N_SHOW).iterrows()):
    phrase = str(row['critical_phrase'])
    text   = str(row['text'])
    hi     = re.sub(r'\s+', ' ', text.replace(phrase, f' >>>{phrase}<<< '))
    orig_str   = ' | '.join(f'{MODELS[k]}={row[f"orig_{k}"]}' for k in loaded)
    print(f'\n[{idx+1}] {row["bank"]} | {str(row["date"])[:10]}')
    print(f'  Original:    {orig_str}')
    print(f'  Named by:    {row["critical_identified_by"]}')
    print(f'  Self-calib:  {row["critical_self_cal"] or "none"}')
    print(f'  Flipped→neu: {row["critical_flipped_to_neutral"] or "none"}')
    print(f'  Flipped→stc: {row["critical_flipped_to_stanced"] or "none"}')
    print(f'  Text: {hi[:500]}')

# %% Visualize
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 1. Resolution rate
ax = axes[0]
counts = occ_df['any_resolves'].value_counts()
ax.bar(['Resolved\n(single phrase)', 'Not resolved'],
       [counts.get(True, 0), counts.get(False, 0)],
       color=['#55A868', '#C44E52'], alpha=0.8)
ax.set_ylabel('Chunks')
ax.set_title('Pass 2: Does masking one\nphrase resolve disagreement?')
for i, v in enumerate([counts.get(True, 0), counts.get(False, 0)]):
    ax.text(i, v + 0.3, str(v), ha='center', fontsize=11)

# 2. Cross-attribution heatmap
ax = axes[1]
sns.heatmap(mat_df, annot=True, fmt='d', cmap='Blues', ax=ax,
            xticklabels=[m.split()[0] for m in mat_df.columns],
            yticklabels=[m.split()[0] for m in mat_df.index])
ax.set_title('Cross-attribution\n(row identified → col flipped)')
ax.set_xlabel('Model that flipped')
ax.set_ylabel('Model that named phrase')

# 3. Self-calibration bar
ax = axes[2]
cal_rates = []
for key in loaded:
    named = pr_all[pr_all['identified_by'].str.contains(MODELS[key], na=False)] if len(pr_all) else pd.DataFrame()
    cal   = named[named['self_calibrated'].str.contains(MODELS[key], na=False)] if len(named) else pd.DataFrame()
    cal_rates.append(len(cal) / max(len(named), 1))

ax.bar([MODELS[k].split()[0] for k in loaded], cal_rates,
       color='#4C72B0', alpha=0.8)
ax.set_ylim(0, 1)
ax.set_ylabel('Self-calibration rate')
ax.set_title('Pass 1 vs Pass 2 agreement\n(model named phrase & flipped on it)')
ax.axhline(0.5, color='grey', linestyle='--', linewidth=0.8)

plt.suptitle('Phrase Attribution — Two-Pass (Extract → Mask) on Top-100 Split Chunks', fontsize=11)
plt.tight_layout()
plt.savefig(OUT_DIR / 'phrase_masking_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# %% Save
occ_df.to_csv(OUT_DIR / 'phrase_masking_results.csv', index=False)
print(f'Saved: phrase_masking_results.csv')

if len(pr_all) > 0:
    pr_all.to_csv(OUT_DIR / 'phrase_masking_detailed.csv', index=False)
    print(f'Saved: phrase_masking_detailed.csv ({len(pr_all):,} rows)')
else:
    print('No phrase-level detail to save (all chunks had 0 phrases extracted).')

# %% Summary
print('\n' + '='*60)
print('SUMMARY')
print('='*60)
print(f'Chunks analysed:              {len(occ_df)}')
print(f'Disagreement resolved:        {n_resolves} ({n_resolves/len(occ_df):.1%})')
print(f'Total unique phrases pooled:  {total_phrases}')
if len(pr_all):
    print(f'Phrases causing any flip:     {int((pr_all["n_flipped"] > 0).sum())} '
          f'({(pr_all["n_flipped"] > 0).mean():.1%})')

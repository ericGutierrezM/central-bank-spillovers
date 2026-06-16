"""
Zero-shot stance classification of central bank press-conference chunks
via OpenRouter (GPT-5.5), using a 5-class scheme:
dovish / mostly dovish / neutral / mostly hawkish / hawkish.

Resumable: re-running this script picks up where it left off (checks
the existing prediction column in CHUNK_OUT and skips completed rows).

Run from the repo root: uv run python src/llm/score_openrouter_gpt55.py
"""

import pandas as pd
import numpy as np
import re, os, json, time
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / '.env', override=True)

CHUNKS_DIR = ROOT / 'data' / 'csv' / 'chunks'
OUT_DIR    = ROOT / 'output' / 'stance'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- only block that differs between the per-model scripts ---
MODEL_KEY  = 'gpt55'
MODEL_SLUG = 'openai/gpt-5.5'        # EDIT if OpenRouter naming differs
MODEL_TAG  = 'GPT55'
# ----------------------------------------------------------------

CHUNK_OUT = OUT_DIR / f'chunk_predictions_{MODEL_KEY}.csv'

BATCH_SIZE = 10
SLEEP_BETWEEN_CALLS = 1.0
CHECKPOINT_EVERY_N_BATCHES = 50

VALID_STANCES = ['dovish', 'mostly dovish', 'neutral', 'mostly hawkish', 'hawkish']
STANCE_SCORE = {'dovish': -1.0, 'mostly dovish': -0.5, 'neutral': 0.0,
                'mostly hawkish': 0.5, 'hawkish': 1.0}

client = OpenAI(base_url='https://openrouter.ai/api/v1', api_key=os.environ['OPENROUTER_API_KEY'])


# --- 1. Load & combine chunks ---

chunk_files = {
    'BoE': ['BoE_chunks.csv', 'BoE_opening_chunks.csv'],
    'ECB': ['ECB_chunks.csv', 'ECB_opening_chunks.csv'],
    'Fed': ['Fed_chunks.csv', 'Fed_opening_chunks.csv'],
}
dfs = []
for bank, files in chunk_files.items():
    for fname in files:
        df = pd.read_csv(CHUNKS_DIR / fname)
        df['bank'] = bank
        df['source_type'] = 'opening' if 'opening' in fname else 'chunk'
        dfs.append(df)
chunks_df = pd.concat(dfs, ignore_index=True)
chunks_df['word_count'] = chunks_df['text'].str.split().str.len()
print(f'Total chunks: {len(chunks_df)}')

if CHUNK_OUT.exists():
    results = pd.read_csv(CHUNK_OUT)
    if len(results) != len(chunks_df):
        print(f'Saved file has {len(results)} rows but chunks_df has {len(chunks_df)} — starting fresh.')
        results = chunks_df.copy()
    else:
        print(f'Resuming — columns: {list(results.columns)}')
else:
    results = chunks_df.copy()
    print('Starting fresh.')


# --- 2. Prompt & robust 5-class parsing ---

def build_stance_prompt(chunks: list[str]) -> str:
    n = len(chunks)
    numbered = ''.join(f'{i+1}. {c}\n' for i, c in enumerate(chunks))
    return (
        f'Classify the monetary policy stance of each of the following {n} excerpts '
        f'from central bank press conferences.\n'
        f'Return a JSON array with exactly {n} objects, one per excerpt in order, '
        'each with a single key "stance" whose value is EXACTLY one of these five strings: '
        '"dovish", "mostly dovish", "neutral", "mostly hawkish", "hawkish".\n'
        'Use "dovish"/"hawkish" only for strong/unambiguous signals; use "mostly dovish"/'
        '"mostly hawkish" for leaning-but-not-strong signals; use "neutral" otherwise.\n'
        'No explanations, no extra keys. '
        'Example: [{"stance": "mostly hawkish"}, {"stance": "neutral"}, ...]\n\n'
        f'Excerpts:\n{numbered}'
    )

# Compound labels checked before their substrings, so "mostly dovish" isn't
# wrongly matched by a bare "dovish" check.
_CANONICAL_ORDER = ['mostly dovish', 'mostly hawkish', 'dovish', 'hawkish', 'neutral']
_ALIASES = {
    'dovish': {'dovish', 'dove'},
    'mostly dovish': {'mostly dovish', 'mostly_dovish', 'mostly-dovish',
                       'somewhat dovish', 'slightly dovish', 'leaning dovish'},
    'neutral': {'neutral', 'balanced', 'mixed'},
    'mostly hawkish': {'mostly hawkish', 'mostly_hawkish', 'mostly-hawkish',
                        'somewhat hawkish', 'slightly hawkish', 'leaning hawkish'},
    'hawkish': {'hawkish', 'hawk'},
}

def _normalize(raw: str) -> str:
    s = raw.lower().strip().rstrip('.')
    s = re.sub(r'[_\-]+', ' ', s)
    return re.sub(r'\s+', ' ', s)

def parse_stance5(raw: str) -> str:
    clean = _normalize(str(raw))
    for canon, aliases in _ALIASES.items():
        if clean in aliases:
            return canon
    for canon in _CANONICAL_ORDER:
        if canon in clean:
            return canon
    return 'parse_error'


# --- 3. Generic OpenRouter call + classify ---

def _call_openrouter(prompt: str, max_tokens: int = 512, retries: int = 6) -> str:
    wait = 5.0
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL_SLUG,
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=max_tokens,
                temperature=0.0,
            )
            text = resp.choices[0].message.content
            if not text:
                raise RuntimeError('Empty response')
            return text.strip()
        except Exception as e:
            msg = str(e)
            if any(x in msg.lower() for x in ['429', 'rate', 'connect', 'timeout']):
                print(f'Retrying in {wait:.0f}s (attempt {attempt+1}/{retries})')
                time.sleep(wait)
                wait = min(wait * 2, 120)
            else:
                raise
    raise RuntimeError(f'{MODEL_TAG} failed after {retries} retries')

def classify_batch(chunks: list[str]) -> list[str]:
    max_tokens = max(len(chunks) * 20, 256)
    raw = _call_openrouter(build_stance_prompt(chunks), max_tokens=max_tokens)
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        raise ValueError(f'No JSON array in response: {raw[:200]}')
    parsed = json.loads(match.group())
    if len(parsed) != len(chunks):
        raise ValueError(f'Expected {len(chunks)}, got {len(parsed)}')
    return [parse_stance5(str(r.get('stance', ''))) for r in parsed]


# --- 4. Resumable classification loop ---

pred_col = f'{MODEL_TAG}_stance'
if pred_col not in results.columns:
    results[pred_col] = np.nan

n_done = int(results[pred_col].notna().sum())
if n_done > 0:
    print(f'Resuming {MODEL_TAG} from row {n_done} ({len(results) - n_done} remaining)...')
else:
    print(f'Starting {MODEL_TAG} from scratch...')

texts = [str(t) if pd.notna(t) else '' for t in results['text']]
pred = results[pred_col].tolist()
start_batch = (n_done // BATCH_SIZE) * BATCH_SIZE

for i in tqdm(range(start_batch, len(texts), BATCH_SIZE), desc=f'{MODEL_TAG}'):
    batch = texts[i:i + BATCH_SIZE]
    try:
        preds = classify_batch(batch)
    except Exception as e:
        print(f'Batch {i} failed: {e} — filling with parse_error')
        preds = ['parse_error'] * len(batch)
    for j, p in enumerate(preds):
        pred[i + j] = p
    time.sleep(SLEEP_BETWEEN_CALLS)
    if ((i // BATCH_SIZE) + 1) % CHECKPOINT_EVERY_N_BATCHES == 0:
        results[pred_col] = pred
        results.to_csv(CHUNK_OUT, index=False)
        print(f'Checkpoint saved -> {CHUNK_OUT}')

results[pred_col] = pred
results.to_csv(CHUNK_OUT, index=False)
print(f'Saved -> {CHUNK_OUT}')
print(pd.Series(pred).value_counts())

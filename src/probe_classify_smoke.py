"""
Smoke test: run the REAL classify_batch() prompt/parse logic from each
score_openrouter_*.py script against a tiny 3-sentence sample, using each
model's real slug. Confirms the JSON-array + 5-class parsing path works
end-to-end, not just that the slug resolves. Does not touch real CSVs.

Run from the `src/` directory: python probe_classify_smoke.py
"""

import os, re, json, importlib.util
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('../.env', override=True)
client = OpenAI(base_url='https://openrouter.ai/api/v1', api_key=os.environ['OPENROUTER_API_KEY'])

SAMPLE_CHUNKS = [
    "We expect to raise interest rates further given persistent inflationary pressure.",
    "The Committee will continue to monitor incoming data before making any further decisions.",
    "Given the weakening labor market, we believe a cautious approach to easing is warranted.",
]

SCRIPTS = {
    'gpt55':         'score_openrouter_gpt55.py',
    'gemini31pro':   'score_openrouter_gemini31pro.py',
    'mistrallarge3': 'score_openrouter_mistrallarge3.py',
    'deepseekv4pro': 'score_openrouter_deepseekv4pro.py',
    'qwen35max':     'score_openrouter_qwen35max.py',
}

def load_funcs(path):
    """Import build_stance_prompt/parse_stance5/MODEL_SLUG from a script without
    running its module-level chunk-loading / classification loop."""
    src = open(path, encoding='utf-8').read()
    # Strip everything from the chunk-loading section onward — we only need
    # the prompt builder, parser, and the MODEL_SLUG/MODEL_TAG constants.
    cutoff = src.index("# --- 1. Load & combine chunks ---")
    head = src[:cutoff]
    tail = src[src.index("# --- 2. Prompt & robust 5-class parsing ---"):
                src.index("# --- 3. Generic OpenRouter call + classify ---")]
    ns = {}
    exec(head, ns)
    exec(tail, ns)
    return ns

for key, fname in SCRIPTS.items():
    ns = load_funcs(fname)
    slug = ns['MODEL_SLUG']
    prompt = ns['build_stance_prompt'](SAMPLE_CHUNKS)
    try:
        resp = client.chat.completions.create(
            model=slug,
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=256,
            temperature=0.0,
        )
        raw = (resp.choices[0].message.content or '').strip()
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if not match:
            print(f'{key:<16} {slug:<28} FAIL -> no JSON array in: {raw[:150]!r}')
            continue
        parsed = json.loads(match.group())
        labels = [ns['parse_stance5'](str(r.get('stance', ''))) for r in parsed]
        ok = len(labels) == len(SAMPLE_CHUNKS) and all(l != 'parse_error' for l in labels)
        status = 'OK' if ok else 'PARTIAL'
        print(f'{key:<16} {slug:<28} {status} -> {labels}')
    except Exception as e:
        print(f'{key:<16} {slug:<28} FAIL -> {e}')

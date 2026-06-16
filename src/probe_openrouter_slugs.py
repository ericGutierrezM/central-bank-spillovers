"""
One-off probe: confirm each OpenRouter model slug used by the
score_openrouter_*.py scripts actually resolves, with a minimal/cheap
request. Does not touch any of the real chunk/output CSVs.

Run from the `src/` directory: python probe_openrouter_slugs.py
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('../.env', override=True)

client = OpenAI(base_url='https://openrouter.ai/api/v1', api_key=os.environ['OPENROUTER_API_KEY'])

MODELS = {
    'gpt55':         'openai/gpt-5.5',
    'gemini31pro':   'google/gemini-3.1-pro-preview',
    'mistrallarge3': 'mistralai/mistral-large-2512',
    'deepseekv4pro': 'deepseek/deepseek-v4-pro',
    'qwen35max':     'qwen/qwen3-max',
}

PROMPT = 'Reply with exactly one word: ok'

print(f'{"model_key":<16} {"slug":<28} {"result"}')
for key, slug in MODELS.items():
    try:
        resp = client.chat.completions.create(
            model=slug,
            messages=[{'role': 'user', 'content': PROMPT}],
            max_tokens=20,
            temperature=0.0,
        )
        text = (resp.choices[0].message.content or '').strip()
        print(f'{key:<16} {slug:<28} OK -> {text!r}')
    except Exception as e:
        print(f'{key:<16} {slug:<28} FAIL -> {e}')

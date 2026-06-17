"""
One-off probe: confirm each OpenRouter model slug in the shared registry
actually resolves, with a minimal/cheap request. Does not touch any of
the real chunk/output CSVs.

Run from the repo root: uv run python src/probe_openrouter_slugs.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from llm.openrouter_models import MODEL_SPECS

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=True)

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])

PROMPT = "Reply with exactly one word: ok"

print(f'{"model_key":<16} {"slug":<36} {"result"}')
for key, spec in MODEL_SPECS.items():
    try:
        resp = client.chat.completions.create(
            model=spec.slug,
            messages=[{"role": "user", "content": PROMPT}],
            max_tokens=20,
            temperature=0.0,
        )
        text = (resp.choices[0].message.content or "").strip()
        print(f"{key:<16} {spec.slug:<36} OK -> {text!r}")
    except Exception as e:
        print(f"{key:<16} {spec.slug:<36} FAIL -> {e}")

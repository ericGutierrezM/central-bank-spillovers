"""
Smoke test: run the shared classify prompt/parse logic against a tiny
3-sentence sample, using each model's real OpenRouter slug. Confirms the
JSON-array + 5-class parsing path works end-to-end, not just that the
slug resolves. Does not touch real CSVs.

Run from the repo root: uv run python src/probe_classify_smoke.py
"""

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from llm.openrouter_models import MODEL_SPECS
from llm.score_openrouter import build_stance_prompt, parse_stance5

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=True)
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])

SAMPLE_CHUNKS = [
    "We expect to raise interest rates further given persistent inflationary pressure.",
    "The Committee will continue to monitor incoming data before making any further decisions.",
    "Given the weakening labor market, we believe a cautious approach to easing is warranted.",
]

for key, spec in MODEL_SPECS.items():
    prompt = build_stance_prompt(SAMPLE_CHUNKS)
    try:
        resp = client.chat.completions.create(
            model=spec.slug,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.0,
        )
        raw = (resp.choices[0].message.content or "").strip()
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            print(f"{key:<16} {spec.slug:<36} FAIL -> no JSON array in: {raw[:150]!r}")
            continue
        parsed = json.loads(match.group())
        labels = [parse_stance5(str(r.get("stance", ""))) for r in parsed]
        ok = len(labels) == len(SAMPLE_CHUNKS) and all(label != "parse_error" for label in labels)
        status = "OK" if ok else "PARTIAL"
        print(f"{key:<16} {spec.slug:<36} {status} -> {labels}")
    except Exception as e:
        print(f"{key:<16} {spec.slug:<36} FAIL -> {e}")

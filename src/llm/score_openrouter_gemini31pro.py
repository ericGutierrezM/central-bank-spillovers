"""
Compatibility wrapper for the shared OpenRouter scorer.

Run from the repo root: uv run python src/llm/score_openrouter_gemini31pro.py
"""

from pathlib import Path
import sys

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from score_openrouter import run_for_model


if __name__ == "__main__":
    run_for_model("gemini31pro")

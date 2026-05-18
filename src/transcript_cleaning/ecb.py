from __future__ import annotations

from collections import Counter

from .vulgar_fractions import count_vulgar_fractions, replace_vulgar_fractions


def clean_ecb_text(text: str) -> tuple[str, Counter[str]]:
    fractions_found = count_vulgar_fractions(text)
    cleaned_text = replace_vulgar_fractions(text)
    return cleaned_text, fractions_found

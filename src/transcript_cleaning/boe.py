from __future__ import annotations

from collections import Counter

from .vulgar_fractions import count_vulgar_fractions, replace_vulgar_fractions

# BoE PDF extraction artifacts observed in the raw PyMuPDF text.
BOE_TEXT_REPLACEMENTS = {
    "\u019F": "ti",   # Ɵ -> ti   (quesƟons, inflaƟon, Ɵme)
    "\u03B8": "ti",   # θ -> ti
    "\u0398": "Ti",   # Θ -> Ti
    "\u019E": "tf",   # ƞ -> tf   (thoughƞul, shorƞall)
    "\u01A9": "tt",   # Ʃ -> tt   (commiƩee, liƩle, paƩern)
    "\u01AB": "tti",  # ƫ -> tti  (seƫng, puƫng, aƫitudes)
    "\u014C": "ft",   # Ō -> ft   (aŌer, oŌen, shiŌ)
    "\uFB00": "ff",   # ﬀ
    "\uFB01": "fi",   # ﬁ
    "\uFB02": "fl",   # ﬂ
    "\uFB03": "ffi",  # ﬃ
    "\uFB04": "ffl",  # ﬄ
}


def clean_boe_text(text: str) -> tuple[str, Counter[str]]:
    fractions_found = count_vulgar_fractions(text)
    cleaned_text = replace_vulgar_fractions(text)
    for src, dest in BOE_TEXT_REPLACEMENTS.items():
        cleaned_text = cleaned_text.replace(src, dest)
    return cleaned_text, fractions_found

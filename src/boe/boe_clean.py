"""
Clean BoE transcript and opening files (steps 1-5).

Input:  data/transcripts/BoE/raw/*.txt
Output: data/transcripts_cleaned/BoE/*.txt  (originals untouched)

Steps applied
-------------
1. Strip the 4-line metadata header (SOURCE / DATE / TYPE / ===)
2. Remove lone page-number stubs (lines that are only digits + whitespace)
3. Remove repeated page headers in transcripts  (lines starting with "Page  N")
   and the following title/date line
4. Remove chart placeholder blocks in openings  (lines matching "– – – CHART")
   and the following chart-label line
5. Collapse 2+ consecutive blank lines to exactly one blank line
"""

import re
import sys
from pathlib import Path

ROOT    = Path(__file__).parent.parent.parent
IN_DIR  = ROOT / "data" / "transcripts" / "BoE" / "raw"
OUT_DIR = ROOT / "data" / "transcripts_cleaned" / "BoE"

# ── Patterns ─────────────────────────────────────────────────────────────────

# Header block: exactly these 4 lines at the top (plus blank lines after)
HEADER_RE = re.compile(
    r"^SOURCE:.*\nDATE:.*\nTYPE:.*\n={10,}",
    re.MULTILINE,
)

# Lone page-number stub: a line containing only digits and whitespace
PAGE_STUB_RE = re.compile(r"^\s*\d+\s*$", re.MULTILINE)

# Page header in transcripts: "Page  N" optionally followed by whitespace
PAGE_HEADER_RE = re.compile(r"^Page\s+\d+\s*$", re.MULTILINE)

# Chart placeholder in openings: "– – – CHART ..." or "- - - CHART ..."
CHART_BLOCK_RE = re.compile(r"^[–\-]\s*[–\-]\s*[–\-]\s*CHART.*$", re.MULTILINE)

# END footer
END_RE = re.compile(r"^\s*END\s*$", re.MULTILINE)

# PDF ligature artifacts → ASCII equivalents
# All mappings verified against BoE_202408_transcript.txt examples:
#   Ō  U+014C  "AŌer"=After, "leŌ"=left, "oŌen"=often   → ft
#   ƞ  U+019E  "Thoughƞul"=Thoughtful, "shorƞall"=shortfall → tf
#   Ɵ  U+019F  "KaƟe"=Katie, "quesƟon"=question          → ti
#   Ʃ  U+01A9  "liƩle"=little, "beƩer"=better            → tt
#   ƫ  U+01AB  "seƫng"=setting                           → tti
_LIGATURES: list[tuple[str, str]] = [
    ("ﬀ", "ff"),
    ("ﬁ", "fi"),
    ("ﬂ", "fl"),
    ("ﬃ", "ffi"),
    ("ﬄ", "ffl"),
    ("ﬅ", "st"),
    ("ﬆ", "st"),
    ("Ō", "ft"),
    ("ƞ", "tf"),
    ("Ɵ", "ti"),
    ("Ʃ", "tt"),
    ("ƫ", "tti"),
]


# ── Cleaning steps ────────────────────────────────────────────────────────────

def strip_header(text: str) -> str:
    """Remove the SOURCE/DATE/TYPE/=== block."""
    return HEADER_RE.sub("", text, count=1)


def remove_page_stubs(text: str) -> str:
    """Remove lines that contain only a page number."""
    return PAGE_STUB_RE.sub("", text)


def remove_page_headers(text: str) -> str:
    """Remove 'Page  N' lines and the title/date line that follows them."""
    lines = text.splitlines(keepends=True)
    out = []
    skip_next_nonempty = False
    for line in lines:
        if PAGE_HEADER_RE.match(line.rstrip("\n")):
            skip_next_nonempty = True
            continue
        if skip_next_nonempty:
            if line.strip():          # first non-blank line after the header
                skip_next_nonempty = False
                continue              # drop it (it's the title/date repeat)
        out.append(line)
    return "".join(out)


def remove_chart_blocks(text: str) -> str:
    """Remove chart placeholder lines and the label line that follows."""
    lines = text.splitlines(keepends=True)
    out = []
    skip_next_nonempty = False
    for line in lines:
        if CHART_BLOCK_RE.match(line.rstrip("\n")):
            skip_next_nonempty = True
            continue
        if skip_next_nonempty:
            if line.strip():
                skip_next_nonempty = False
                continue              # drop the chart label line
        out.append(line)
    return "".join(out)


def remove_end_marker(text: str) -> str:
    return END_RE.sub("", text)


def normalize_ligatures(text: str) -> str:
    for lig, replacement in _LIGATURES:
        text = text.replace(lig, replacement)
    return text


def collapse_blank_lines(text: str) -> str:
    """Strip trailing whitespace from every line, then remove all blank lines.
    Speaker labels serve as the only turn separators."""
    lines = [l.rstrip() for l in text.splitlines()]
    text = "\n".join(lines)
    return re.sub(r"\n{2,}", "\n", text)


def clean(text: str) -> str:
    text = strip_header(text)
    text = normalize_ligatures(text)
    text = remove_page_stubs(text)
    text = remove_page_headers(text)
    text = remove_chart_blocks(text)
    text = remove_end_marker(text)
    text = collapse_blank_lines(text)
    return text.strip() + "\n"


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(IN_DIR.glob("*.txt"))
    if not files:
        print(f"No .txt files found in {IN_DIR}", file=sys.stderr)
        sys.exit(1)

    print(f"Cleaning {len(files)} files  {IN_DIR} -> {OUT_DIR}\n")
    for f in files:
        cleaned = clean(f.read_text(encoding="utf-8"))
        out_path = OUT_DIR / f.name
        out_path.write_text(cleaned, encoding="utf-8")
        print(f"  OK  {f.name}")

    print(f"\nDone. {len(files)} files written to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

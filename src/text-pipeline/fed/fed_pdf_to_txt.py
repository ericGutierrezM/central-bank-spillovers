"""
Convert Fed FOMC PDFs to speaker-tagged plain text files.

Handles three filename formats:
  FOMCYYYYMMDDmeeting    -> type: meeting
  FOMCYYYYMMDDconfcall   -> type: confcall
  FOMCpresconfYYYYMMDD   -> type: presconf

Output: data/transcripts/Fed/raw/<stem>.txt
  Speaker turns are tagged **NAME** on their own line, e.g.:
    **CHAIR POWELL**
    Good afternoon. My colleagues and I remain squarely focused...

Speaker label format in PDFs:
  CHAIR POWELL.  text...        (presconf and meeting)
  MR. CLARIDA.  text...         (meeting)
  MS. LOGAN.  text...           (meeting)
  VICE CHAIR WILLIAMS.  text... (meeting)
  MICHELLE SMITH.  text...      (presconf moderator)
  COLBY SMITH.  text...         (presconf journalist)

Page header artifacts stripped:
  Presconf: "June 14, 2023 / Chair Powell's Press Conference / FINAL / Page N of N"
  Meeting:  "September 15-16, 2020\n2 of 238" (page footer)
"""

import re
import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    sys.exit("Run: pip install pymupdf")

ROOT = Path(__file__).parent.parent.parent

PATTERNS = [
    (re.compile(r"^FOMC(\d{8})(meeting)$", re.IGNORECASE), "meeting"),
    (re.compile(r"^FOMC(\d{8})(confcall)$", re.IGNORECASE), "confcall"),
    (re.compile(r"^FOMCpresconf(\d{8})$", re.IGNORECASE), "presconf"),
]

# Speaker label: ALL-CAPS word(s) + period + 2+ spaces at line start
# Matches: CHAIR POWELL.  / MR. CLARIDA.  / MS. LOGAN.1  / VICE CHAIR WILLIAMS.
# The label ends at the double space separating name from speech text.
_SPEAKER_RE = re.compile(r"^([A-Z][A-Z0-9\s\.\-]+?)\.\s{2,}")

# Presconf running header block — appears at top of every page after page 1.
# Pattern: one or two date/title lines, then "FINAL", then "Page N of N"
_PRESCONF_HEADER_RE = re.compile(
    r"^[A-Z][a-z]+ \d{1,2}, \d{4}.*?Page \d+ of \d+\s*$",
    re.DOTALL,
)

# Meeting page footer: "September 15–16, 2020\n2 of 238"
_MEETING_FOOTER_RE = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2}(?:–\d{1,2})?,\s+\d{4}\s*\n\d+ of \d+"
)

# Footnote markers like "1" or "2" appearing as superscripts mid-text
# Matches digit(s) preceded by period (end of name), or after lowercase/comma
_FOOTNOTE_RE = re.compile(r"(?<=[a-z,\.])\d{1,2}(?=\s)")

# Speaker label splitter for full-text re.split approach.
# Matches patterns like: CHAIR YELLEN.  / MR. POTTER.  / VICE CHAIRMAN DUDLEY.
# Uses a named capture group so re.split keeps the label in the result.
# Requires either a known title prefix OR two+ ALL-CAPS words.
_SPEAKER_SPLIT_RE = re.compile(
    r"(?<!\w)"                                      # not mid-word
    r"("
    r"(?:CHAIR(?:MAN)?|VICE CHAIR(?:MAN)?|MR\.|MS\.|PRESIDENT|GOVERNOR)"
    r"\s+[A-Z][A-Z\-]+(?:\s+[A-Z][A-Z\-]+)*"       # title + surname(s)
    r"|[A-Z]{2,}(?:\s+[A-Z]{2,})+"                 # two+ standalone ALL-CAPS words
    r")"
    r"\.\d*"                                        # period + optional footnote digit
    r"\s+"                                          # 1+ whitespace
)


def parse_filename(stem: str) -> tuple[str, str] | None:
    for pattern, doc_type in PATTERNS:
        m = pattern.match(stem)
        if m:
            return m.group(1), doc_type
    return None


def _is_presconf_header_block(lines_text: str) -> bool:
    """True if this block looks like the presconf running page header."""
    return bool(_PRESCONF_HEADER_RE.match(lines_text.strip()))


def _parse_turns_from_text(raw: str) -> str:
    """
    Split raw text on ALL-CAPS speaker labels into **Name**-tagged turns.
    Uses re.split so inline labels (mid-paragraph) are also caught.
    """
    parts = _SPEAKER_SPLIT_RE.split(raw)
    # re.split with a capturing group returns: [pre, name, text, name, text, ...]
    # parts[0] is any text before the first speaker (headers etc.) — drop it
    output: list[str] = []
    i = 1
    while i + 1 < len(parts):
        name = parts[i].strip()
        text = parts[i + 1].strip()
        if name and text:
            output.append(f"\n**{name}**")
            output.append(text)
        i += 2

    return "\n\n".join(p for p in output if p.strip())


# ── Presconf extraction ───────────────────────────────────────────────────────

def extract_presconf(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    raw_lines: list[str] = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")
        for block in blocks:
            if block[6] != 0:  # skip non-text
                continue
            text = block[4]
            # Skip the running header block (date / title / FINAL / Page N)
            if _is_presconf_header_block(text):
                continue
            # Skip the title block on page 1 (bold title + date, before CHAIR POWELL.)
            # These blocks don't contain speaker labels so they'll be dropped naturally.
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            raw_lines.extend(lines)

    doc.close()
    raw = "\n".join(raw_lines)
    # Remove footnote markers embedded in text
    raw = _FOOTNOTE_RE.sub("", raw)
    return _parse_turns_from_text(raw)


# ── Meeting / confcall extraction ─────────────────────────────────────────────

def extract_meeting(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    raw_pages: list[str] = []

    for page in doc:
        text = page.get_text()
        # Strip meeting page footer
        text = _MEETING_FOOTER_RE.sub("", text)
        raw_pages.append(text)

    doc.close()
    raw = "\n".join(raw_pages)
    raw = _FOOTNOTE_RE.sub("", raw)
    return _parse_turns_from_text(raw)


# ── Dispatch ──────────────────────────────────────────────────────────────────

def convert(pdf_path: Path, out_dir: Path, overwrite: bool = False) -> None:
    parsed = parse_filename(pdf_path.stem)
    if parsed is None:
        print(f"  SKIP (unrecognised): {pdf_path.name}")
        return

    date_str, doc_type = parsed
    from datetime import date
    d = date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))
    if not (date(2015, 1, 1) <= d <= date(2025, 12, 31)):
        print(f"  SKIP (out of window): {pdf_path.name}")
        return

    out_path = out_dir / f"{pdf_path.stem}.txt"

    if out_path.exists() and not overwrite:
        print(f"  DUP  {pdf_path.name} -> already exists, skipping")
        return

    if doc_type == "presconf":
        text = extract_presconf(pdf_path)
    else:
        text = extract_meeting(pdf_path)

    header = (
        f"SOURCE: {pdf_path.name}\n"
        f"DATE: {date_str}\n"
        f"TYPE: {doc_type}\n"
        f"{'=' * 60}\n\n"
    )

    out_path.write_text(header + text, encoding="utf-8")
    print(f"   OK  {pdf_path.name} -> {out_path.name}")


def main() -> None:
    fed_dir = ROOT / "data" / "transcripts" / "Fed"
    out_dir = fed_dir / "raw"
    out_dir.mkdir(exist_ok=True)

    # Press conferences only — meeting and confcall transcripts are excluded
    # from the pipeline (closed-door deliberations, not public communication).
    all_pdfs = sorted(fed_dir.glob("*.pdf"))
    pdfs = [p for p in all_pdfs if "presconf" in p.name.lower()]

    if not pdfs:
        sys.exit(f"No presconf PDFs found in {fed_dir}")

    skipped = len(all_pdfs) - len(pdfs)
    print(f"Found {len(all_pdfs)} PDFs — converting {len(pdfs)} presconf, skipping {skipped} meeting/confcall\n")
    for pdf in pdfs:
        convert(pdf, out_dir, overwrite=True)

    n = len(list(out_dir.glob("*.txt")))
    print(f"\nDone. {n} files in {out_dir}")


if __name__ == "__main__":
    main()

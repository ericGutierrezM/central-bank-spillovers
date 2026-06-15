"""
Convert BoE MPR/Inflation Report PDFs to plain text files.

Output naming convention: BoE_YYYYMM_{type}.txt
  type = transcript  (Q&A press conference)
       = opening     (governor's opening remarks / statement)

Slides are skipped entirely (near-zero prose content).

Handled filename patterns
--------------------------
TRANSCRIPTS:
  inflation-report-transcript-{month}-{year}
  press-conference-transcript-{month}-{year}
  press-conference-7-november-2019-transcript      (one-off)
  mpr-press-conference-transcript-{month}-{year}

OPENING REMARKS:
  opening-remarks-{month}-{year}
  opening-statement-{month}-{year}

SKIP (slides):
  mpr-{month}-{year}-opening-remarks-slides
  mpr-{month}-{year}-press-conference-slides
  opening-remarks-slides-{month}-{year}

Speaker tagging in transcripts
-------------------------------
Speakers are wrapped as **Name** on their own line, followed by their text.

Three eras detected from filename prefix:
  press-conference-transcript-*        (2015-2016)
    No bold. Speaker on its own line ending with colon.
    e.g.  "Phil Aldrick, The Times:"

  inflation-report-transcript-*        (2017-2019)
  press-conference-7-november-2019-*
    No bold. Speaker inline at start of paragraph, followed by double space.
    e.g.  "Mark Carney:  In terms of the first question..."

  mpr-press-conference-transcript-*    (2020-2025)
    Bold spans mark speakers. Two sub-styles:
      2020-2024: bold line contains "Name: text..."
      2025:      bold line is name only; timestamps (0:00:00) are stripped.
"""

import re
import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    sys.exit("Run: pip install pymupdf")

# Ligature/OCR artifacts produced by PyMuPDF on BoE PDFs — fixed at write time
# so all downstream files (raw/, transcripts_cleaned/, CSV) are clean.
_OCR_FIXES = [
    ("Ɵ", "ti"),   # e.g. KaƟe MarƟn → Katie Martin
    ("Ʃ", "tt"),
    ("ƫ", "tt"),
    ("Ō", "ft"),
    ("ƞ", "tf"),
    ("ﬁ", "fi"),
    ("ﬂ", "fl"),
    ("ﬀ", "ff"),
    ("ﬃ", "ffi"),
    ("ﬄ", "ffl"),
]


def _normalize_ocr_artifacts(text: str) -> str:
    for src, dst in _OCR_FIXES:
        text = text.replace(src, dst)
    return text


MONTHS = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}

# (compiled regex, doc_type)  — None doc_type means SKIP
PATTERNS: list[tuple[re.Pattern, str | None]] = [
    # --- SKIP: slides ---
    (re.compile(r"^mpr-\w+-\d{4}-(opening-remarks|press-conference)-slides$"), None),
    (re.compile(r"^opening-remarks-slides-\w+-\d{4}$"), None),

    # --- TRANSCRIPTS ---
    (re.compile(r"^inflation-report-transcript-(?P<month>\w+)-(?P<year>\d{4})$"), "transcript"),
    (re.compile(r"^press-conference-transcript-(?P<month>\w+)-(?P<year>\d{4})$"), "transcript"),
    (re.compile(r"^mpr-press-conference-transcript-(?P<month>\w+)-(?P<year>\d{4})$"), "transcript"),
    # one-off: press-conference-7-november-2019-transcript
    (re.compile(r"^press-conference-\d+-(?P<month>\w+)-(?P<year>\d{4})-transcript$"), "transcript"),

    # --- OPENING REMARKS ---
    (re.compile(r"^opening-remarks-(?P<month>\w+)-(?P<year>\d{4})$"), "opening"),
    (re.compile(r"^opening-statement-(?P<month>\w+)-(?P<year>\d{4})$"), "opening"),
]

# Matches timestamps like "0:00:58" or "1:23:45" (2025 transcripts)
_TIMESTAMP_RE = re.compile(r"^\d+:\d{2}:\d{2}$")

# Matches a speaker label at the start of a line: "Name:" or "Name, Outlet:"
# Used for 2015-2019 era where there is no bold.
_SPEAKER_INLINE_RE = re.compile(r"^([A-Z][A-Za-z\s\-\'\.]+(?:,\s*[^:]+)?):\s{1,}")

# Matches legacy page header lines to skip: "Page  2" or "Report Q&A - DD.MM.YY"
_PAGE_HEADER_RE = re.compile(r"^Page\s+\d+$|Q&A\s*[-–]\s*\d{1,2}\.\d{1,2}\.\d{2}")


def parse_filename(stem: str) -> tuple[str, str] | None:
    """Return (yyyymm, doc_type) or None to skip, or raise if unrecognised."""
    for pattern, doc_type in PATTERNS:
        m = pattern.match(stem)
        if m:
            if doc_type is None:
                return None  # skip signal
            month_name = m.group("month").lower()
            year = m.group("year")
            mm = MONTHS.get(month_name)
            if mm is None:
                raise ValueError(f"Unknown month '{month_name}' in: {stem}")
            return f"{year}{mm}", doc_type
    raise ValueError(f"Unrecognised filename: {stem}")


def _detect_era(stem: str) -> str:
    """
    Return era string based on filename prefix.
      'mpr'     -> mpr-press-conference-transcript-* (2020+, bold speakers)
      'legacy'  -> press-conference-transcript-* or inflation-report-transcript-* (2015-2019, no bold)
    """
    if stem.startswith("mpr-press-conference-transcript"):
        return "mpr"
    return "legacy"


# ── Opening remarks ───────────────────────────────────────────────────────────

def extract_opening(pdf_path: Path) -> str:
    """Plain text extraction for opening remarks — no speaker tagging needed."""
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n\n".join(pages)


# ── Transcripts: MPR era (2020+, bold speakers) ───────────────────────────────

def _span_is_bold(span: dict) -> bool:
    return "Bold" in span["font"] or "bold" in span["font"] or bool(span.get("flags", 0) & 16)


def extract_transcript_mpr(pdf_path: Path) -> str:
    """
    Extract transcript text for mpr-press-conference era.
    Processes line-by-line: bold lines are speaker labels, body text follows.
    Timestamps (0:00:00) are stripped.

    In many 2020-2024 PDFs, multiple speaker turns are packed into a single
    PDF block, so we must detect speaker boundaries at the line level rather
    than the block level.
    """
    doc = fitz.open(pdf_path)
    output_parts: list[str] = []
    current_para_lines: list[str] = []

    def flush_para() -> None:
        if current_para_lines:
            output_parts.append(" ".join(current_para_lines))
            current_para_lines.clear()

    def start_speaker(name: str) -> None:
        flush_para()
        output_parts.append(f"\n**{name}**")

    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                # Build line text and check if bold
                parts, bold_flags = [], []
                for span in line["spans"]:
                    t = span["text"]
                    if not t.strip():
                        continue
                    parts.append(t)
                    bold_flags.append(_span_is_bold(span))

                if not parts:
                    continue

                line_text = "".join(parts).strip()

                # Skip timestamps (2025 style: "0:02:19")
                if _TIMESTAMP_RE.match(line_text):
                    continue

                # Skip doc title/date headers
                if _PAGE_HEADER_RE.search(line_text):
                    continue
                if re.match(r"^(Monetary Policy Report|Thursday\s+\d)", line_text):
                    continue

                line_is_bold = any(bold_flags)

                if line_is_bold:
                    # 2025 style: bold line is name only (no colon)
                    if ":" not in line_text:
                        start_speaker(line_text)
                    else:
                        # 2020-2024 style: bold line is "Name: start of text..."
                        colon_idx = line_text.index(":")
                        name = line_text[:colon_idx].strip()
                        rest = line_text[colon_idx + 1:].strip()
                        start_speaker(name)
                        if rest:
                            current_para_lines.append(rest)
                else:
                    # Non-bold line — check for inline speaker label
                    # (handles May 2021 where only the moderator has bold)
                    m = _SPEAKER_INLINE_RE.match(line_text)
                    if m:
                        name = m.group(1).strip()
                        rest = line_text[m.end():].strip()
                        start_speaker(name)
                        if rest:
                            current_para_lines.append(rest)
                    else:
                        current_para_lines.append(line_text)

    flush_para()
    doc.close()
    return "\n\n".join(p for p in output_parts if p.strip())


# ── Transcripts: legacy era (2015-2019, no bold) ─────────────────────────────

def extract_transcript_legacy(pdf_path: Path) -> str:
    """
    Extract transcript text for press-conference / inflation-report era.
    No bold formatting — speaker labels detected by regex.

    2015-2016: speaker on its own line ending with colon
    2017-2019: speaker inline at start of paragraph
    Both are handled by the same regex applied per-paragraph.
    """
    doc = fitz.open(pdf_path)

    # Extract paragraphs using block boundaries
    raw_paras: list[str] = []
    for page in doc:
        blocks = page.get_text("blocks")  # (x0,y0,x1,y1,text,block_no,type)
        for block in blocks:
            if block[6] != 0:  # skip non-text blocks
                continue
            text = block[4].strip()
            if text:
                raw_paras.append(text)
    doc.close()

    output_parts: list[str] = []

    for para in raw_paras:
        # Normalise internal newlines to spaces
        para = re.sub(r"\s*\n\s*", " ", para).strip()

        if not para:
            continue

        # Skip page header artifacts: "Page  2", "Inflation Report Q&A - 12.2.15"
        if _PAGE_HEADER_RE.search(para):
            continue

        # Check if paragraph starts with a speaker label
        m = _SPEAKER_INLINE_RE.match(para)
        if m:
            name = m.group(1).strip()
            rest = para[m.end():].strip()
            output_parts.append(f"\n**{name}**")
            if rest:
                output_parts.append(rest)
        else:
            output_parts.append(para)

    return "\n\n".join(p for p in output_parts if p.strip())


# ── Dispatch ──────────────────────────────────────────────────────────────────

def extract_text(pdf_path: Path, doc_type: str) -> str:
    if doc_type == "opening":
        return extract_opening(pdf_path)
    era = _detect_era(pdf_path.stem)
    if era == "mpr":
        return extract_transcript_mpr(pdf_path)
    return extract_transcript_legacy(pdf_path)


def convert(pdf_path: Path, out_dir: Path) -> None:
    try:
        result = parse_filename(pdf_path.stem)
    except ValueError as e:
        print(f"  ERR {e}")
        return

    if result is None:
        print(f" SKIP (slides): {pdf_path.name}")
        return

    yyyymm, doc_type = result
    from datetime import date
    d = date(int(yyyymm[:4]), int(yyyymm[4:6]), 1)
    if not (date(2015, 1, 1) <= d <= date(2025, 12, 31)):
        print(f" SKIP (out of window): {pdf_path.name}")
        return

    out_name = f"BoE_{yyyymm}_{doc_type}.txt"
    out_path = out_dir / out_name

    if out_path.exists():
        print(f"  OVR {pdf_path.name} -> {out_name} (overwriting)")

    text = _normalize_ocr_artifacts(extract_text(pdf_path, doc_type))

    header = (
        f"SOURCE: {pdf_path.name}\n"
        f"DATE: {yyyymm}\n"
        f"TYPE: {doc_type}\n"
        f"{'=' * 60}\n\n"
    )

    out_path.write_text(header + text, encoding="utf-8")
    print(f"   OK  {pdf_path.name}")
    print(f"       -> {out_name}")


def main() -> None:
    boe_dir = Path(__file__).parent.parent.parent / "data" / "transcripts" / "BoE"
    out_dir = boe_dir / "raw"
    out_dir.mkdir(exist_ok=True)

    pdfs = sorted(boe_dir.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found in {boe_dir}")

    print(f"Processing {len(pdfs)} PDFs -> {out_dir}\n")
    for pdf in pdfs:
        convert(pdf, out_dir)

    converted = list(out_dir.glob("*.txt"))
    print(f"\nDone. {len(converted)} files written to {out_dir}")

    transcripts = [f for f in converted if "transcript" in f.name]
    openings = [f for f in converted if "opening" in f.name]
    print(f"  {len(transcripts)} transcripts, {len(openings)} opening remarks")


if __name__ == "__main__":
    main()

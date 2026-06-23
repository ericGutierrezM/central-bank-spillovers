import re
import sys
from pathlib import Path
from datetime import date
import shutil

try:
    import fitz
except ImportError:
    sys.exit("Run: pip install pymupdf")

ROOT = Path(__file__).parent.parent.parent


### Fed PDF to TXT ###

PATTERNS = [
    (re.compile(r"^FOMC(\d{8})(meeting)$", re.IGNORECASE), "meeting"),
    (re.compile(r"^FOMC(\d{8})(confcall)$", re.IGNORECASE), "confcall"),
    (re.compile(r"^FOMCpresconf(\d{8})$", re.IGNORECASE), "presconf"),
]

_SPEAKER_RE = re.compile(r"^([A-Z][A-Z0-9\s\.\-]+?)\.\s{2,}")
_PRESCONF_HEADER_RE = re.compile(
    r"^[A-Z][a-z]+ \d{1,2}, \d{4}.*?Page \d+ of \d+\s*$",
    re.DOTALL,
)

_MEETING_FOOTER_RE = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2}(?:–\d{1,2})?,\s+\d{4}\s*\n\d+ of \d+"
)

_FOOTNOTE_RE = re.compile(r"(?<=[a-z,\.])\d{1,2}(?=\s)")

_SPEAKER_SPLIT_RE = re.compile(
    r"(?<!\w)"                                      # not mid-word
    r"("
    r"(?:CHAIR(?:MAN)?|VICE CHAIR(?:MAN)?|MR\.|MS\.|PRESIDENT|GOVERNOR)"
    r"\s+[A-Z][A-Z\-]+(?:\s+[A-Z][A-Z\-]+)*"       # title + surname(s)
    r"|[A-Z]{2,}(?:\s+[A-Z]{2,})+"                 # two+ standalone ALL-CAPS words
    r")"
    r"[.:\-]\d*"                                    # period, colon, or dash + optional footnote digit
    r"\s+"                                          # 1+ whitespace
)

def parse_filename_fed(stem: str) -> tuple[str, str] | None:
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

# Presconf extraction

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

# Meeting / confcall extraction

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

# Dispatch

def convert_fed(pdf_path: Path, out_dir: Path, overwrite: bool = False) -> None:
    parsed = parse_filename_fed(pdf_path.stem)
    if parsed is None:
        return

    date_str, doc_type = parsed
    out_path = out_dir / f"{pdf_path.stem}.txt"

    if out_path.exists() and not overwrite:
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

def main_fed_pdf_to_txt() -> None:
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
    for pdf in pdfs:
        convert_fed(pdf, out_dir, overwrite=True)

    n = len(list(out_dir.glob("*.txt")))

main_fed_pdf_to_txt()

### BoE PDF to TXT ###

# Ligature/OCR artifacts produced by PyMuPDF on BoE PDFs — fixed at write time
# so all downstream files (raw/, transcripts_cleaned/, CSV) are clean.
_OCR_FIXES = [
    ("Ɵ", "ti"),
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

PATTERNS: list[tuple[re.Pattern, str | None]] = [
    # --- SKIP: slides ---
    (re.compile(r"^mpr-\w+-\d{4}-(opening-remarks|press-conference)-slides$"), None),
    (re.compile(r"^opening-remarks-slides-\w+-\d{4}$"), None),

    # --- TRANSCRIPTS ---
    (re.compile(r"^inflation-report-transcript-(?P<month>\w+)-(?P<year>\d{4})$"), "transcript"),
    (re.compile(r"^press-conference-transcript-(?P<month>\w+)-(?P<year>\d{4})$"), "transcript"),
    (re.compile(r"^mpr-press-conference-transcript-(?P<month>\w+)-(?P<year>\d{4})$"), "transcript"),
    # 2020 joint MPR+FSR releases: mpr-fsr-press-conference-transcript-{month}-{year}
    (re.compile(r"^mpr-fsr-press-conference-transcript-(?P<month>\w+)-(?P<year>\d{4})$"), "transcript"),
    # one-off: press-conference-7-november-2019-transcript
    (re.compile(r"^press-conference-\d+-(?P<month>\w+)-(?P<year>\d{4})-transcript$"), "transcript"),
    # 2020 emergency meeting: interest-rate-cut-{day}-{month}-{year}-transcript
    (re.compile(r"^interest-rate-cut-\d+-(?P<month>\w+)-(?P<year>\d{4})-transcript$"), "transcript"),

    # --- OPENING REMARKS ---
    (re.compile(r"^opening-remarks-(?P<month>\w+)-(?P<year>\d{4})$"), "opening"),
    (re.compile(r"^opening-statement-(?P<month>\w+)-(?P<year>\d{4})$"), "opening"),
]

# Matches timestamps like "0:00:58" or "1:23:45" (2025 transcripts)
_TIMESTAMP_RE = re.compile(r"^\d+:\d{2}:\d{2}$")

# Matches a speaker label at the start of a line: "Name:", "Name, Outlet:", or "Name (XX):"
# The optional (XX) handles 2017-era BoE transcripts where speakers have initials e.g. "Mark Carney (MC):"
# Used for 2015-2019 era where there is no bold.
_SPEAKER_INLINE_RE = re.compile(r"^([A-Z][A-Za-z\s\-\'\.]+(?:,\s*[^:(]+)?(?:\s*\([A-Z]{1,4}\))?):\s{1,}")

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

def extract_opening(pdf_path: Path) -> str:
    """Plain text extraction for opening remarks — no speaker tagging needed."""
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n\n".join(pages)

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

# Transcripts: legacy era (2015-2019, no bold)

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

# Dispatch

def extract_text(pdf_path: Path, doc_type: str) -> str:
    if doc_type == "opening":
        return extract_opening(pdf_path)
    era = _detect_era(pdf_path.stem)
    if era == "mpr":
        return extract_transcript_mpr(pdf_path)
    return extract_transcript_legacy(pdf_path)

def convert_boe(pdf_path: Path, out_dir: Path) -> None:
    try:
        result = parse_filename(pdf_path.stem)
    except ValueError as e:
        return

    if result is None:
        return

    yyyymm, doc_type = result
    out_name = f"BoE_{yyyymm}_{doc_type}.txt"
    out_path = out_dir / out_name

    if out_path.exists():
        True

    text = _normalize_ocr_artifacts(extract_text(pdf_path, doc_type))

    header = (
        f"SOURCE: {pdf_path.name}\n"
        f"DATE: {yyyymm}\n"
        f"TYPE: {doc_type}\n"
        f"{'=' * 60}\n\n"
    )

    out_path.write_text(header + text, encoding="utf-8")

def main_boe_pdf_to_txt() -> None:
    boe_dir = Path(__file__).parent.parent.parent / "data" / "transcripts" / "BoE"
    out_dir = boe_dir / "raw"
    out_dir.mkdir(exist_ok=True)

    pdfs = sorted(boe_dir.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found in {boe_dir}")

    for pdf in pdfs:
        convert_boe(pdf, out_dir)

    converted = list(out_dir.glob("*.txt"))

    transcripts = [f for f in converted if "transcript" in f.name]
    openings = [f for f in converted if "opening" in f.name]

main_boe_pdf_to_txt()

### ECB Normalize ###

STUDY_START = date(2015, 1, 1)
STUDY_END   = date(2025, 12, 31)

DATE_RE = re.compile(r"(?:ecb\.)?(?:is|sp)(\d{6})(?:~[a-f0-9]+)?(?:_\d)?\.en", re.IGNORECASE)

def parse_date(filename: str) -> date | None:
    """Return a date object or None if filename is unrecognised."""
    m = DATE_RE.match(filename)
    if not m:
        return None
    yymm_dd = m.group(1)          # 6-digit YYMMDD
    yy = int(yymm_dd[:2])
    mm = int(yymm_dd[2:4])
    dd = int(yymm_dd[4:6])
    yyyy = 2000 + yy if yy < 30 else 1900 + yy
    try:
        return date(yyyy, mm, dd)
    except ValueError:
        return None

def main_ecb_normalize() -> None:
    ecb_dir = Path(__file__).parent.parent.parent / "data" / "transcripts" / "ECB"
    out_dir  = Path(__file__).parent.parent.parent / "data" / "transcripts_cleaned" / "ECB"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(ecb_dir.glob("*.txt"))
    if not files:
        sys.exit(f"No .txt files found in {ecb_dir}")

    kept = skipped_window = skipped_unrecognised = 0

    for f in files:
        d = parse_date(f.name)

        if d is None:
            skipped_unrecognised += 1
            continue

        if not (STUDY_START <= d <= STUDY_END):
            skipped_window += 1
            continue

        out_name = f"ECB_{d.strftime('%Y%m%d')}.txt"
        out_path = out_dir / out_name

        if out_path.exists():
            continue

        text = f.read_text(encoding="utf-8", errors="replace")
        out_path.write_text(text, encoding="utf-8")
        kept += 1

main_ecb_normalize()

### Standardize the Cleaning (FED and BoE) ###

FED_RE = re.compile(
    r"^FOMC(\d{8})(meeting|confcall)$|^FOMCpresconf(\d{8})$",
    re.IGNORECASE,
)

BOE_RE = re.compile(r"^BoE_(\d{6})_(transcript|opening)$")

# Fed

def parse_fed(stem: str) -> tuple[str, str] | None:
    """Return (YYYYMMDD, type) or None."""
    m = FED_RE.match(stem)
    if not m:
        return None
    if m.group(1):                          # meeting / confcall
        return m.group(1), m.group(2).lower()
    else:                                   # presconf
        return m.group(3), "presconf"

def in_window_yyyymmdd(yyyymmdd: str) -> bool:
    try:
        d = date(int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]))
        return STUDY_START <= d <= STUDY_END
    except ValueError:
        return False

def process_fed(out_root: Path) -> None:
    src_dir = ROOT / "data" / "transcripts" / "Fed" / "raw"
    out_dir = out_root / "Fed"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(src_dir.glob("*.txt"))
    kept = skipped = 0

    for f in files:
        parsed = parse_fed(f.stem)
        if parsed is None:
            continue
        yyyymmdd, doc_type = parsed
        if not in_window_yyyymmdd(yyyymmdd):
            skipped += 1
            continue
        out_name = f"Fed_{yyyymmdd}_{doc_type}.txt"
        shutil.copy2(f, out_dir / out_name)
        kept += 1

# BoE

def in_window_yyyymm(yyyymm: str) -> bool:
    try:
        yyyy, mm = int(yyyymm[:4]), int(yyyymm[4:6])
        # include if the month falls within the study years
        return 2015 <= yyyy <= 2025
    except ValueError:
        return False

def process_boe(out_root: Path) -> None:
    src_dir = ROOT / "data" / "transcripts" / "BoE" / "raw"
    out_dir = out_root / "BoE"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(src_dir.glob("*.txt"))
    kept = skipped = 0

    for f in files:
        m = BOE_RE.match(f.stem)
        if not m:
            continue
        yyyymm = m.group(1)
        if not in_window_yyyymm(yyyymm):
            skipped += 1
            continue
        shutil.copy2(f, out_dir / f.name)
        kept += 1

def main_standard_clean() -> None:
    out_root = ROOT / "data" / "transcripts_cleaned"
    process_fed(out_root)
    process_boe(out_root)

    print("\n== Summary ==")
    for bank in ("Fed", "BoE", "ECB"):
        d = out_root / bank
        if not d.exists():
            continue
        files = sorted(d.glob("*.txt"))
        print(f"  {bank}: {len(files)} files in {d.relative_to(ROOT)}")

        # Press conference files only, sorted by date
        if bank == "Fed":
            pc = [f for f in files if "presconf" in f.stem]
            dates = sorted(f.stem.split("_")[1] for f in pc)
        elif bank == "BoE":
            # both 'transcript' and 'opening' are press conference material
            pc = [f for f in files if f.stem.endswith(("_transcript", "_opening"))]
            # unique dates (each event has two files)
            dates = sorted(set(f.stem.split("_")[1] for f in pc))
        else:  # ECB — all files are press conferences
            pc = files
            dates = sorted(f.stem.split("_")[1] for f in pc)

        if dates:
            print(f"    press conf: {len(dates)} docs | {dates[0]} to {dates[-1]}")
            by_year: dict[str, int] = {}
            for d in dates:
                yr = d[:4]
                by_year[yr] = by_year.get(yr, 0) + 1
            year_summary = "  ".join(f"{yr}: {cnt}" for yr, cnt in sorted(by_year.items()))
            print(f"    by year:    {year_summary}")
        else:
            print(f"    press conf: none found")

main_standard_clean()

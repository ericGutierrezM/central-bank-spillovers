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
"""

import re
import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    sys.exit("Run: pip install pymupdf")

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


def parse_filename(stem: str) -> tuple[str, str] | None:
    """
    Return (yyyymm, doc_type) or None to skip, or raise if unrecognised.
    """
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


def pdf_to_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n\n".join(pages)


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
    out_name = f"BoE_{yyyymm}_{doc_type}.txt"
    out_path = out_dir / out_name

    if out_path.exists():
        # Two source files map to same output (shouldn't happen, but guard it)
        print(f"  DUP {pdf_path.name} -> {out_name} already exists, skipping")
        return

    text = pdf_to_text(pdf_path)

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
    boe_dir = Path(__file__).parent.parent / "data" / "transcripts" / "BoE"
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

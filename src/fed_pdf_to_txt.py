"""
Convert Fed FOMC PDFs to plain text files.

Handles three filename formats:
  FOMCYYYYMMDDmeeting    -> type: meeting
  FOMCYYYYMMDDconfcall   -> type: confcall
  FOMCpresconfYYYYMMDD   -> type: presconf

Output: data/transcripts/Fed/raw/<stem>.txt
"""

import re
import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    sys.exit("Run: pip install pymupdf")

# Regex patterns for each format
PATTERNS = [
    (re.compile(r"^FOMC(\d{8})(meeting)$", re.IGNORECASE), "meeting"),
    (re.compile(r"^FOMC(\d{8})(confcall)$", re.IGNORECASE), "confcall"),
    (re.compile(r"^FOMCpresconf(\d{8})$", re.IGNORECASE), "presconf"),
]


def parse_filename(stem: str) -> tuple[str, str] | None:
    """Return (date_str YYYYMMDD, doc_type) or None if unrecognised."""
    for pattern, doc_type in PATTERNS:
        m = pattern.match(stem)
        if m:
            return m.group(1), doc_type
    return None


def pdf_to_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n\n".join(pages)


def convert(pdf_path: Path, out_dir: Path) -> None:
    parsed = parse_filename(pdf_path.stem)
    if parsed is None:
        print(f"SKIP (unrecognised filename): {pdf_path.name}")
        return

    date_str, doc_type = parsed
    out_path = out_dir / f"{pdf_path.stem}.txt"

    text = pdf_to_text(pdf_path)

    header = (
        f"SOURCE: {pdf_path.name}\n"
        f"DATE: {date_str}\n"
        f"TYPE: {doc_type}\n"
        f"{'=' * 60}\n\n"
    )

    out_path.write_text(header + text, encoding="utf-8")
    print(f"  OK  {pdf_path.name} -> {out_path.name}")


def main() -> None:
    fed_dir = Path(__file__).parent.parent / "data" / "transcripts" / "Fed"
    out_dir = fed_dir / "raw"
    out_dir.mkdir(exist_ok=True)

    pdfs = sorted(fed_dir.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found in {fed_dir}")

    print(f"Converting {len(pdfs)} PDFs -> {out_dir}\n")
    for pdf in pdfs:
        convert(pdf, out_dir)

    print(f"\nDone. {len(list(out_dir.glob('*.txt')))} files in {out_dir}")


if __name__ == "__main__":
    main()

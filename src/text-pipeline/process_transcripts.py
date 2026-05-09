"""
Central Bank Transcript Corpus Processor
=========================================
Processes FED, ECB, and BOE press conference transcripts (.txt and .pdf)
into a clean, structured CSV corpus — one row per speaker turn / paragraph.

Institution-specific behaviour
--------------------------------
FED   Text is already clean; extract and segment directly.

ECB   Large archive may include non-press-conference documents.
      Files are filtered by a whitelist of known press-conference filename
      patterns and, as a fallback, by scanning the first ~2 000 chars for
      phrases like "press conference" or "introductory statement".
      Discarded files are logged for review.

BOE   For many years the opening remarks and the Q&A were published as two
      separate files.  The script pairs them by date, then concatenates
      remarks + Q&A into one logical document before segmentation.
      Unmatched single files are still processed normally.

Directory structure expected
-----------------------------
    <root>/
        data/
            transcripts/
                Fed/    *.txt  *.pdf
                ECB/    *.txt  *.pdf
                BoE/    *.txt  *.pdf

Output CSV columns
-------------------
    institution   fed | ecb | boe
    source_file   original filename(s); merged BOE rows show "a.pdf + b.pdf"
    date          YYYY-MM-DD parsed from filename (see Date parsing below)
    turn_index    0-based order within the logical document
    speaker       normalised label, e.g. "CHAIR POWELL", or empty
    speaker_role  chair | moderator | journalist | unknown
    text          cleaned paragraph / turn text
    word_count    token count of text
    char_count    character count of text
    has_qa        1 if the document contains a Q&A section, else 0

Date parsing
-------------
    FED / ECB   YYYY-MM-DD  or  YYYYMMDD  anywhere in the filename stem.
    BOE         "november-2024" / "nov-2024" / "november_2024" style
                month-year in the stem → resolved to YYYY-MM-01.
                Numeric YYYY-MM-DD / YYYYMMDD accepted as fallback.

Usage
------
python src/text-pipeline/process_transcripts.py --root ./data/transcripts \\
    --fed-dir Fed --ecb-dir ECB --boe-dir BoE --output full_corpus.csv

Dependencies
-------------
    uv add pdfplumber      # preferred PDF backend
    # pypdf is accepted as a fallback if pdfplumber is unavailable
"""

import argparse
import csv
import logging
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Iterator

# ---------------------------------------------------------------------------
# Optional PDF backends
# ---------------------------------------------------------------------------
try:
    import pdfplumber
    _PDF_BACKEND = "pdfplumber"
except ImportError:
    pdfplumber = None
    try:
        from pypdf import PdfReader as _PdfReader       # type: ignore
        _PDF_BACKEND = "pypdf"
    except ImportError:
        _PdfReader = None
        _PDF_BACKEND = None


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Turn:
    institution:  str
    source_file:  str   # may be "a.pdf + b.pdf" for merged BOE docs
    date:         str   # YYYY-MM-DD or ""
    turn_index:   int
    speaker:      str
    speaker_role: str
    text:         str
    word_count:   int
    char_count:   int
    has_qa:       int   # 0 / 1


# ---------------------------------------------------------------------------
# Date parsing — institution-aware
# ---------------------------------------------------------------------------

_NUMERIC_DATE_RE = re.compile(
    r"(?P<y>\d{4})[-_]?(?P<m>\d{2})[-_]?(?P<d>\d{2})"
)

_MONTH_NAMES: dict[str, str] = {
    "january": "01",  "jan": "01",
    "february": "02", "feb": "02",
    "march": "03",    "mar": "03",
    "april": "04",    "apr": "04",
    "may": "05",
    "june": "06",     "jun": "06",
    "july": "07",     "jul": "07",
    "august": "08",   "aug": "08",
    "september": "09","sep": "09", "sept": "09",
    "october": "10",  "oct": "10",
    "november": "11", "nov": "11",
    "december": "12", "dec": "12",
}

_BOE_MONTH_YEAR_RE = re.compile(
    r"(?P<month>" + "|".join(_MONTH_NAMES.keys()) + r")[-_]?(?P<year>\d{4})",
    re.IGNORECASE,
)


def parse_date(stem: str, institution: str) -> str:
    """Return YYYY-MM-DD, or empty string if nothing matched."""
    if institution == "boe":
        m = _BOE_MONTH_YEAR_RE.search(stem)
        if m:
            mm = _MONTH_NAMES[m.group("month").lower()]
            return f"{m.group('year')}-{mm}-01"
    m = _NUMERIC_DATE_RE.search(stem)
    if m:
        return f"{m.group('y')}-{m.group('m')}-{m.group('d')}"
    return ""


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def _read_txt(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Cannot decode {path} with any tried encoding.")


def _read_pdf(path: Path) -> str:
    if _PDF_BACKEND == "pdfplumber":
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif _PDF_BACKEND == "pypdf":
        reader = _PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        raise RuntimeError(
            "No PDF library found. Install pdfplumber:\n"
            "    uv add pdfplumber"
        )


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return _read_txt(path)
    elif suffix == ".pdf":
        return _read_pdf(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


# ---------------------------------------------------------------------------
# ECB relevance filter
# ---------------------------------------------------------------------------

_ECB_PC_FILENAME_RE = re.compile(
    r"press[-_\s]?conf|presser|pc[-_]\d|monetary[-_]policy"
    r"|rate[-_]decision|introductory[-_]statement|mopo",
    re.IGNORECASE,
)
_ECB_PC_CONTENT_RE = re.compile(
    r"press\s+conference|introductory\s+statement"
    r"|monetary\s+policy\s+decision|questions\s+and\s+answers",
    re.IGNORECASE,
)


def ecb_is_press_conference(path: Path, raw_text: str) -> bool:
    if _ECB_PC_FILENAME_RE.search(path.stem):
        return True
    if _ECB_PC_CONTENT_RE.search(raw_text[:2000]):
        return True
    return False


# ---------------------------------------------------------------------------
# BOE file pairing
# ---------------------------------------------------------------------------

_BOE_REMARKS_RE = re.compile(
    r"opening|remarks?|statement|speech|intro",
    re.IGNORECASE,
)
_BOE_QA_RE = re.compile(
    r"q[-&_\s]?a|questions?[-_\s]and|transcript",
    re.IGNORECASE,
)


def _boe_file_type(stem: str) -> str:
    if _BOE_REMARKS_RE.search(stem):
        return "remarks"
    if _BOE_QA_RE.search(stem):
        return "qa"
    return "unknown"


def pair_boe_files(files: list[Path]) -> list[tuple[list[Path], str]]:
    """
    Group files by date, order each group [remarks, qa, …], and return
    a list of (file_list, date_string) ready for merging.
    """
    by_date: dict[str, dict[str, list[Path]]] = defaultdict(lambda: defaultdict(list))
    undated: list[Path] = []

    for f in files:
        date = parse_date(f.stem, "boe")
        if not date:
            undated.append(f)
            continue
        ftype = _boe_file_type(f.stem)
        by_date[date][ftype].append(f)

    groups: list[tuple[list[Path], str]] = []

    for date in sorted(by_date):
        typed = by_date[date]
        ordered: list[Path] = (
            typed.get("remarks", [])
            + typed.get("qa",      [])
            + typed.get("unknown", [])
        )
        groups.append((ordered, date))

    for f in undated:
        groups.append(([f], ""))

    return groups


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

_JUNK_LINE_RE = re.compile(
    r"^\s*("
    r"page\s*\d+"
    r"|\d+\s*$"
    r"|\[.*?\]"
    r"|\*{3,}"
    r"|[-–—]{3,}"
    r"|www\.\S+"
    r"|\(applause\)"
    r"|©.*"
    r")\s*$",
    re.IGNORECASE,
)
_WHITESPACE_RE  = re.compile(r"[ \t]{2,}")
_MULTI_BLANK_RE = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\xad", "").replace("\u200b", "")
    lines = (_WHITESPACE_RE.sub(" ", ln) for ln in text.split("\n"))
    lines = [ln for ln in lines if not _JUNK_LINE_RE.match(ln)]
    text = "\n".join(lines)
    return _MULTI_BLANK_RE.sub("\n\n", text).strip()


# ---------------------------------------------------------------------------
# Q&A detection
# ---------------------------------------------------------------------------

_QA_MARKER_RE = re.compile(
    r"\bquestions?\s+and\s+answers?\b"
    r"|\bq\s*[&and]+\s*a\b"
    r"|\bopen(?:ing)?\s+(?:the\s+)?floor\b"
    r"|\b(?:take|open|begin)\b.*?\bquestions?\b",
    re.IGNORECASE,
)


def has_qa_section(text: str) -> bool:
    return bool(_QA_MARKER_RE.search(text))


# ---------------------------------------------------------------------------
# Speaker detection & segmentation
# ---------------------------------------------------------------------------

_SPEAKER_LINE_RE = re.compile(
    r"^(?P<speaker>"
    r"(?:CHAIR(?:MAN|WOMAN)?|PRESIDENT|GOVERNOR|DEPUTY\s+GOVERNOR"
    r"|MR\.|MRS\.|MS\.|DR\."
    r"|VICE[\s-]CHAIR(?:MAN|WOMAN)?"
    r"|MODERATOR|QUESTIONER|REPORTER|JOURNALIST|ANALYST"
    r"|DEPUTY)"
    r"[\s.]*[A-Z][A-Z\s'\-]{0,40}"
    r")[\s]*[:\.]",
    re.IGNORECASE,
)
_QA_LABEL_RE = re.compile(
    r"^(?P<speaker>QUESTION|ANSWER|Q|A)\s*[:\.]",
    re.IGNORECASE,
)
_SIMPLE_SPEAKER_RE = re.compile(
    r"^(?P<speaker>[A-Z][A-Z'\-]{2,30})\s*:",
)

_ROLE_MAP: dict[str, str] = {
    "chair": "chair",     "chairman": "chair",  "chairwoman": "chair",
    "president": "chair", "governor": "chair",
    "deputy governor": "chair", "vice-chair": "chair", "vice chair": "chair",
    "deputy": "chair",
    "moderator": "moderator",
    "questioner": "journalist", "reporter": "journalist",
    "journalist": "journalist", "analyst": "journalist",
    "question": "journalist",   "q": "journalist",
    "answer": "chair",          "a": "chair",
}


def _infer_role(speaker: str) -> str:
    low = speaker.lower()
    for key, role in _ROLE_MAP.items():
        if key in low:
            return role
    return "unknown"


def _normalise_speaker(raw: str) -> str:
    return re.sub(r"\s{2,}", " ", raw.upper().strip().rstrip(".:,"))


def segment_turns(text: str) -> Iterator[tuple[str, str]]:
    """Yield (speaker_label, paragraph_text) pairs."""
    current_speaker = ""
    for para in re.split(r"\n{2,}", text):
        para = para.strip()
        if not para:
            continue
        first_line, _, rest = para.partition("\n")
        first_line = first_line.strip()

        m = (
            _SPEAKER_LINE_RE.match(first_line)
            or _QA_LABEL_RE.match(first_line)
            or _SIMPLE_SPEAKER_RE.match(first_line)
        )

        if m:
            current_speaker = _normalise_speaker(m.group("speaker"))
            inline = first_line[m.end():].strip()
            body   = (inline + "\n" + rest).strip() if inline else rest.strip()
            if body:
                yield current_speaker, body
        else:
            yield current_speaker, para


# ---------------------------------------------------------------------------
# Core: text → list[Turn]
# ---------------------------------------------------------------------------

def doc_to_turns(
    text: str,
    institution: str,
    source_label: str,
    date: str,
) -> list[Turn]:
    cleaned = clean_text(text)
    qa_flag = int(has_qa_section(cleaned))
    turns: list[Turn] = []

    for idx, (speaker, body) in enumerate(segment_turns(cleaned)):
        body = body.strip()
        if not body or len(body.split()) < 4:
            continue
        turns.append(Turn(
            institution  = institution,
            source_file  = source_label,
            date         = date,
            turn_index   = idx,
            speaker      = speaker,
            speaker_role = _infer_role(speaker) if speaker else "",
            text         = body,
            word_count   = len(body.split()),
            char_count   = len(body),
            has_qa       = qa_flag,
        ))

    return turns


# ---------------------------------------------------------------------------
# Per-institution processors
# ---------------------------------------------------------------------------

def process_fed(folder: Path) -> list[Turn]:
    files = sorted(
        f for f in folder.iterdir()
        if f.suffix.lower() in {".txt", ".pdf"} and f.is_file()
    )
    logging.info("[FED] %d file(s) found", len(files))
    all_turns: list[Turn] = []

    for f in files:
        logging.info("  %s", f.name)
        try:
            raw = extract_text(f)
        except Exception as exc:
            logging.warning("  SKIP %s — %s", f.name, exc)
            continue
        turns = doc_to_turns(raw, "fed", f.name, parse_date(f.stem, "fed"))
        logging.info("    → %d turns", len(turns))
        all_turns.extend(turns)

    return all_turns


def process_ecb(folder: Path) -> list[Turn]:
    files = sorted(
        f for f in folder.iterdir()
        if f.suffix.lower() in {".txt", ".pdf"} and f.is_file()
    )
    logging.info("[ECB] %d file(s) found", len(files))
    all_turns: list[Turn] = []
    discarded: list[str]  = []

    for f in files:
        try:
            raw = extract_text(f)
        except Exception as exc:
            logging.warning("  SKIP %s — %s", f.name, exc)
            continue

        if not ecb_is_press_conference(f, raw):
            logging.info("  DISCARD (not a press conference): %s", f.name)
            discarded.append(f.name)
            continue

        logging.info("  %s", f.name)
        turns = doc_to_turns(raw, "ecb", f.name, parse_date(f.stem, "ecb"))
        logging.info("    → %d turns", len(turns))
        all_turns.extend(turns)

    logging.info(
        "[ECB] %d file(s) discarded as non-press-conference", len(discarded)
    )
    if discarded:
        logging.info("  Discarded files: %s", ", ".join(discarded))

    return all_turns


def process_boe(folder: Path) -> list[Turn]:
    files = sorted(
        f for f in folder.iterdir()
        if f.suffix.lower() in {".txt", ".pdf"} and f.is_file()
    )
    logging.info("[BOE] %d file(s) found", len(files))
    groups = pair_boe_files(files)
    logging.info("[BOE] %d logical document(s) after date-pairing", len(groups))
    all_turns: list[Turn] = []

    for file_list, date in groups:
        parts: list[str] = []
        combined = ""

        for f in file_list:
            try:
                combined += extract_text(f) + "\n\n"
                parts.append(f.name)
                logging.info("  %s", f.name)
            except Exception as exc:
                logging.warning("  SKIP %s — %s", f.name, exc)

        if not combined.strip():
            continue

        source_label = " + ".join(parts)
        turns = doc_to_turns(combined, "boe", source_label, date)
        merged = len(parts) > 1
        logging.info(
            "  %s → %d turns%s",
            source_label, len(turns), " [merged]" if merged else "",
        )
        all_turns.extend(turns)

    return all_turns


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a clean CSV corpus from FED/ECB/BOE transcripts."
    )
    parser.add_argument("--root",    default=".",          metavar="DIR",
                        help="Root directory containing institution sub-folders")
    parser.add_argument("--output",  default="corpus.csv", metavar="FILE",
                        help="Output CSV path")
    parser.add_argument("--fed-dir", default="fed",        metavar="NAME")
    parser.add_argument("--ecb-dir", default="ecb",        metavar="NAME")
    parser.add_argument("--boe-dir", default="boe",        metavar="NAME")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level  = logging.DEBUG if args.verbose else logging.INFO,
        format = "%(levelname)s %(message)s",
    )

    root = Path(args.root)
    processors = {
        "fed": (process_fed, args.fed_dir),
        "ecb": (process_ecb, args.ecb_dir),
        "boe": (process_boe, args.boe_dir),
    }

    all_turns: list[Turn] = []
    for inst, (fn, folder_name) in processors.items():
        folder = root / folder_name
        if not folder.exists():
            logging.warning(
                "[%s] Folder not found, skipping: %s", inst.upper(), folder
            )
            continue
        all_turns.extend(fn(folder))

    if not all_turns:
        logging.error("No turns extracted. Check --root and file contents.")
        sys.exit(1)

    # Write CSV
    col_names = [f.name for f in fields(Turn)]
    out_path  = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=col_names, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for t in all_turns:
            writer.writerow({name: getattr(t, name) for name in col_names})

    # Summary
    inst_counts = Counter(t.institution for t in all_turns)
    total_words = sum(t.word_count for t in all_turns)
    all_docs    = {(t.institution, t.source_file) for t in all_turns}
    qa_docs     = {(t.institution, t.source_file) for t in all_turns if t.has_qa}

    logging.info("")
    logging.info("=" * 55)
    logging.info("Corpus written → %s", out_path)
    logging.info("  Total rows      : %d", len(all_turns))
    logging.info("  Total words     : %d", total_words)
    logging.info("  Logical docs    : %d  (%d contain Q&A)", len(all_docs), len(qa_docs))
    for inst, cnt in sorted(inst_counts.items()):
        logging.info("  %-6s          : %d turns", inst.upper(), cnt)
    logging.info("=" * 55)


if __name__ == "__main__":
    main()
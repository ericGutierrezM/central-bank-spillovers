"""
Fed transcript pipeline: raw tagged text -> turn-level CSV.

Input:  data/transcripts/Fed/raw/*.txt  (speaker-tagged by fed_pdf_to_txt.py)
Output: data/csv/Fed.csv

Each row is one speaker turn:
  doc_id        e.g. FOMCpresconf20230614
  date          YYYYMMDD
  doc_type      meeting | presconf | confcall
  speaker       raw name string (CHAIR POWELL, COLBY SMITH, etc.)
  speaker_role  chair | official | journalist | moderator | unknown
  turn_idx      integer position of this turn within the document
  text          full cleaned text of the turn

Speaker tags in raw files use **NAME** format produced by fed_pdf_to_txt.py.

Cleaning applied before turn extraction:
  - Strip SOURCE/DATE/TYPE/==== metadata header
  - Strip inline presconf page headers:
      "June 14, 2023 Chair Powell's Press Conference FINAL Page N of N"
  - Strip inline meeting page footers:
      "September 15-16, 2020 2 of 238"
  - Normalize curly/smart quotes to ASCII equivalents
  - Collapse all whitespace within turn text to single spaces

Study window: 2015-01-01 to 2025-12-31.
"""

import re
import sys
from pathlib import Path
from datetime import date

import pandas as pd

ROOT     = Path(__file__).parent.parent.parent
IN_DIR   = ROOT / "data" / "transcripts" / "Fed" / "raw"
OUT_PATH = ROOT / "data" / "csv" / "Fed.csv"

STUDY_START = date(2015, 1, 1)
STUDY_END   = date(2025, 12, 31)

# Filename patterns
_PRESCONF_RE = re.compile(r"^FOMCpresconf(\d{8})$", re.IGNORECASE)
_MEETING_RE  = re.compile(r"^FOMC(\d{8})(meeting|confcall)$", re.IGNORECASE)

# Metadata header written by fed_pdf_to_txt.py
_HEADER_RE = re.compile(r"SOURCE:.*\nDATE:.*\nTYPE:.*\n={10,}\n*", re.MULTILINE)

# Presconf inline page header artifact:
#   "June 14, 2023 Chair Powell's Press Conference FINAL Page 2 of 26"
#   "March 18, 2015 Chair Yellen's Press Conference FINAL Page 8 of 22"
# Chair name varies across tenures; apostrophe may be mangled by PDF encoding.
_PRESCONF_PAGE_RE = re.compile(
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},\s+\d{4}\s+Chair(?:man)?\s+\w+.s Press Conference(?:\s+Call)?\s+FINAL\s+Page \d+ of \d+"
)

# Meeting inline page footer artifact: "September 15-16, 2020 2 of 238"
_MEETING_PAGE_RE = re.compile(
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2}(?:[–\-]\d{1,2})?,\s+\d{4}\s+\d+ of \d+"
)

_INLINE_WS = re.compile(r"[ \t]+")

# Curly/smart quote codepoints -> ASCII equivalents
_QUOTE_PAIRS = [
    ("‘", "'"), ("’", "'"), ("‚", "'"), ("`", "'"),  # single quotes
    ("“", '"'), ("”", '"'), ("„", '"'),               # double quotes
    ("–", "-"), ("—", "-"),                                # dashes
]


def _normalize_quotes(text: str) -> str:
    for src, dst in _QUOTE_PAIRS:
        text = text.replace(src, dst)
    return text


# Speaker role classification
_CHAIRS     = {"chair powell", "chairman powell", "chair yellen", "chair bernanke", "chairman bernanke",
               "chair burns", "chair volcker", "chair greenspan"}
_OFFICIALS  = {"vice chair", "mr.", "ms.", "president", "governor"}
_MODERATORS = {"michelle smith", "jonathan ernst"}


def _parse_filename(stem: str) -> tuple[str, str] | None:
    """Return (yyyymmdd, doc_type) or None if unrecognised or out of window."""
    m = _PRESCONF_RE.match(stem)
    if m:
        return m.group(1), "presconf"
    m = _MEETING_RE.match(stem)
    if m:
        return m.group(1), m.group(2).lower()
    return None


def _in_window(yyyymmdd: str) -> bool:
    try:
        d = date(int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]))
        return STUDY_START <= d <= STUDY_END
    except ValueError:
        return False


def _clean_text(text: str) -> str:
    text = _normalize_quotes(text)
    text = _HEADER_RE.sub("", text)
    text = _PRESCONF_PAGE_RE.sub("", text)
    text = _MEETING_PAGE_RE.sub("", text)
    lines = [_INLINE_WS.sub(" ", ln).strip() for ln in text.splitlines()]
    return "\n".join(lines).strip()


def _speaker_role(name: str) -> str:
    n = name.lower()
    if any(c in n for c in _CHAIRS):
        return "chair"
    if any(n == m for m in _MODERATORS):
        return "moderator"
    if any(t in n for t in _OFFICIALS):
        return "official"
    # All-caps full name with no title = journalist in presconf context
    return "journalist"


def _parse_turns(text: str) -> list[tuple[str, str]]:
    """Parse **NAME** tags into (speaker, turn_text) pairs."""
    turns = []
    current_speaker: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        m = re.match(r"^\*\*(.+?)\*\*\s*$", line)
        if m:
            if current_speaker is not None and current_lines:
                turns.append((current_speaker, " ".join(current_lines).strip()))
            current_speaker = m.group(1).strip()
            current_lines = []
        else:
            if current_speaker is not None and line.strip():
                current_lines.append(line.strip())

    if current_speaker and current_lines:
        turns.append((current_speaker, " ".join(current_lines).strip()))

    return turns


def process_file(path: Path) -> list[dict]:
    parsed = _parse_filename(path.stem)
    if parsed is None:
        return []

    yyyymmdd, doc_type = parsed
    if not _in_window(yyyymmdd):
        return []

    raw  = path.read_text(encoding="utf-8", errors="replace")
    text = _clean_text(raw)
    turns = _parse_turns(text)

    rows = []
    seen_chair = False
    for turn_idx, (speaker, turn_text) in enumerate(turns):
        turn_text = re.sub(r"\s+", " ", turn_text).strip()
        if not turn_text:
            continue
        role = _speaker_role(speaker)
        if role == "chair":
            turn_type = "opening" if not seen_chair else "answer"
            seen_chair = True
        elif role == "journalist":
            turn_type = "question"
        else:
            turn_type = "other"
        rows.append({
            "doc_id":       path.stem,
            "date":         yyyymmdd,
            "doc_type":     doc_type,
            "speaker":      speaker,
            "speaker_role": role,
            "turn_idx":     turn_idx,
            "turn_type":    turn_type,
            "text":         turn_text,
        })
    return rows


def main() -> None:
    files = sorted(IN_DIR.glob("FOMC*.txt"))
    if not files:
        sys.exit(f"No FOMC*.txt files found in {IN_DIR}")

    all_rows = []
    for f in files:
        rows = process_file(f)
        all_rows.extend(rows)
        if rows:
            print(f"  {f.name}: {len(rows)} turns")

    df = pd.DataFrame(all_rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"\nWrote {len(df)} turns to {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

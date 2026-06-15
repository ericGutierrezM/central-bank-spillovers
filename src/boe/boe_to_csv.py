"""
BoE transcript pipeline: raw tagged text -> turn-level CSV.

Input:  data/transcripts/BoE/raw/BoE_YYYYMM_{type}.txt
Output: data/csv/BoE.csv

Each row is one speaker turn:
  doc_id        e.g. BoE_202408_transcript
  date          YYYYMMDD
  doc_type      transcript | opening
  speaker       raw name string from **Name** tag
  speaker_role  governor | official | journalist | moderator | unknown
  turn_idx      integer position of this turn within the document
  text          full cleaned text of the turn

Cleaning applied before turn extraction:
  - Strip SOURCE/DATE/TYPE/==== metadata header
  - Strip page header artifacts (Page N, Q&A date lines)
  - Strip inline chart colour references: (orange bars), (in blue), etc.
  - Strip chart number references: (as shown in Chart 3), etc.
  - Normalize curly/smart quotes to ASCII equivalents
  - Collapse all whitespace within turn text to single spaces

Study window: 2015-01-01 to 2025-12-31 (filtered by YYYYMM in filename).

Speaker role classification:
  - Known governor names (Carney, Bailey) -> governor
  - Other BoE officials (Broadbent, Ramsden, etc.) -> official
  - Moderator names (Martin, Walsh, Bell, etc.) -> moderator
  - All others (journalists) -> journalist
  - Opening docs: single speaker tagged as governor
"""

import re
import sys
from pathlib import Path
from datetime import date

import pandas as pd

ROOT = Path(__file__).parent.parent.parent
IN_DIR = ROOT / "data" / "transcripts" / "BoE" / "raw"
OUT_PATH = ROOT / "data" / "csv" / "BoE.csv"

STUDY_START = date(2015, 1, 1)
STUDY_END   = date(2025, 12, 31)

# Speaker role lists (expand as needed)
GOVERNORS  = {"mark carney", "andrew bailey", "mc", "andrew"}
OFFICIALS  = {"ben broadbent", "dave ramsden", "david ramsden", "jon cunliffe",
              "minouche shafik", "sam woods", "clare lombardelli", "sarah breeden",
              "bb", "js", "ben", "dave"}
MODERATORS = {"katie martin", "sebastian walsh", "james bell", "jamie bell"}

# Cleaning patterns
_HEADER_RE    = re.compile(r"SOURCE:.*\nDATE:.*\nTYPE:.*\n={10,}\n*", re.MULTILINE)
_COLOR_REF_RE = re.compile(r"\((?:in\s+)?(?:orange|blue|purple|yellow|white|green|gold|pink)"
                           r"(?:\s+(?:bars?|line|area|shading))?\)", re.IGNORECASE)
_CHART_REF_RE = re.compile(r"\((?:as\s+)?(?:shown\s+in\s+)?[Cc]hart\s+\w+\)")
_INLINE_WS    = re.compile(r"[ \t]+")
_ANY_WS       = re.compile(r"\s+")

# Common OCR/PDF extraction artifacts seen in recent BoE transcripts.
# Some of these stand in for letter pairs rather than a single character.
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

# Curly/smart quote codepoints -> ASCII equivalents
_QUOTE_PAIRS = [
    ("‘", "'"), ("’", "'"), ("‚", "'"), ("`", "'"),  # single quotes
    ("“", '"'), ("”", '"'), ("„", '"'),               # double quotes
    ("–", "-"), ("—", "-"),                               # dashes
]


def _normalize_quotes(text: str) -> str:
    for src, dst in _QUOTE_PAIRS:
        text = text.replace(src, dst)
    return text


def _normalize_ocr_artifacts(text: str) -> str:
    for src, dst in _OCR_FIXES:
        text = text.replace(src, dst)
    return text


_MONTH_NAMES = (
    "January|February|March|April|May|June|July|August|"
    "September|October|November|December"
)
# Requires weekday prefix to avoid false matches in body text.
_DAY_RE_WEEKDAY = re.compile(
    r"(?:Monday|Tuesday|Wednesday|Thursday|Friday)\s+"
    r"(\d{1,2})(?:st|nd|rd|th)?\s+(?:" + _MONTH_NAMES + r")",
    re.IGNORECASE,
)
# No weekday — for legacy "Q&A DDth Month YYYY" headers; only applied to the
# first 10 lines so it cannot match dates mentioned in speech body.
_DAY_RE_NOWEEKDAY = re.compile(
    r"(\d{1,2})(?:st|nd|rd|th)?\s+(?:" + _MONTH_NAMES + r")",
    re.IGNORECASE,
)
_HEADER_LINES = 10  # date is always within the title block


def _extract_date(raw_text: str, yyyymm: str, sibling_opening: "Path | None" = None) -> str:
    """Return YYYYMMDD using yyyymm for year+month and day parsed from text body."""
    def _find_day(text: str) -> int | None:
        lines = text.splitlines()
        # Try weekday-anchored pattern first across the wider header
        head30 = "\n".join(lines[:30])
        m = _DAY_RE_WEEKDAY.search(head30)
        if m:
            return int(m.group(1))
        # Fall back to no-weekday pattern but only in the first 10 lines
        head10 = "\n".join(lines[:_HEADER_LINES])
        m = _DAY_RE_NOWEEKDAY.search(head10)
        return int(m.group(1)) if m else None

    day = _find_day(raw_text)
    if day is None and sibling_opening is not None and sibling_opening.exists():
        day = _find_day(sibling_opening.read_text(encoding="utf-8"))
    if day is not None:
        return f"{yyyymm}{day:02d}"
    print(f"  WARN no date found for {yyyymm}, falling back to {yyyymm}01")
    return f"{yyyymm}01"


def _in_window(yyyymm: str) -> bool:
    try:
        yyyy, mm = int(yyyymm[:4]), int(yyyymm[4:6])
        return STUDY_START <= date(yyyy, mm, 1) <= STUDY_END
    except ValueError:
        return False


def _clean_text(text: str) -> str:
    text = _normalize_ocr_artifacts(text)
    text = _normalize_quotes(text)
    text = _HEADER_RE.sub("", text)
    text = _COLOR_REF_RE.sub("", text)
    text = _CHART_REF_RE.sub("", text)
    # collapse inline whitespace only - preserve newlines for speaker-tag parsing
    lines = [_INLINE_WS.sub(" ", ln).strip() for ln in text.splitlines()]
    return "\n".join(lines).strip()


def _speaker_role(name: str, doc_type: str) -> str:
    if doc_type == "opening":
        return "governor"
    n = name.lower()
    if any(g in n for g in GOVERNORS):
        return "governor"
    if any(o in n for o in OFFICIALS):
        return "official"
    if any(m in n for m in MODERATORS):
        return "moderator"
    return "journalist"


def _parse_turns(text: str, doc_type: str) -> list[tuple[str, str]]:
    """Return list of (speaker, turn_text) from a tagged transcript or opening."""
    if doc_type == "opening":
        return [("Governor", text.strip())]

    turns = []
    current_speaker = None
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
    stem = path.stem  # e.g. BoE_202408_transcript
    parts = stem.split("_")
    if len(parts) != 3:
        return []

    _, yyyymm, doc_type = parts
    if not _in_window(yyyymm):
        return []

    raw = path.read_text(encoding="utf-8")
    sibling = (path.parent / f"BoE_{yyyymm}_opening.txt") if doc_type == "transcript" else None
    full_date = _extract_date(raw, yyyymm, sibling)
    text = _clean_text(raw)
    turns = _parse_turns(text, doc_type)

    rows = []
    seen_governor = False
    for turn_idx, (speaker, turn_text) in enumerate(turns):
        turn_text = _ANY_WS.sub(" ", turn_text).strip()
        if not turn_text:
            continue
        role = _speaker_role(speaker, doc_type)
        if doc_type == "opening":
            turn_type = "opening"
        elif role == "governor":
            turn_type = "opening" if not seen_governor else "answer"
            seen_governor = True
        elif role == "journalist":
            turn_type = "question"
        else:
            turn_type = "other"
        rows.append({
            "doc_id":       stem,
            "date":         full_date,
            "doc_type":     doc_type,
            "speaker":      speaker,
            "speaker_role": role,
            "turn_idx":     turn_idx,
            "turn_type":    turn_type,
            "text":         turn_text,
        })
    return rows


def main() -> None:
    files = sorted(IN_DIR.glob("*.txt"))
    if not files:
        sys.exit(f"No files found in {IN_DIR}")

    all_rows = []
    for f in files:
        rows = process_file(f)
        all_rows.extend(rows)
        print(f"  {f.name}: {len(rows)} turns")

    df = pd.DataFrame(all_rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"\nWrote {len(df)} turns to {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

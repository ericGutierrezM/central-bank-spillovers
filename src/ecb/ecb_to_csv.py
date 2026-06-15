"""
ECB transcript pipeline: cleaned text -> turn-level CSV.

Input:  data/transcripts_cleaned/ECB/ECB_YYYYMMDD.txt
Output: data/csv/ECB.csv

Each row is one speaker turn:
  doc_id        e.g. ECB_20240912
  date          YYYYMMDD
  doc_type      opening | presser
  speaker       raw name string
  speaker_role  president | official | journalist | unknown
  turn_idx      integer position of this turn within the document
  text          full cleaned text of the turn

Two speaker-detection modes are used depending on era:
  Draghi era (2015-2019): explicit "Name:" and "Question:" labels in Q&A
  Lagarde era (2019+): no labels; Q&A paragraphs alternate journalist/president

Study window: 2015-01-01 to 2025-12-31.
"""

import re
import sys
from pathlib import Path
from datetime import date

import pandas as pd

ROOT     = Path(__file__).parent.parent.parent
IN_DIR   = ROOT / "data" / "transcripts_cleaned" / "ECB"
OUT_PATH = ROOT / "data" / "csv" / "ECB.csv"

STUDY_START = date(2015, 1, 1)
STUDY_END   = date(2025, 12, 31)

# ECB presidents in study window (lowercase for matching).
# Include last names because labeled Q&A uses "Draghi:" not "Mario Draghi:".
PRESIDENTS = {"mario draghi", "draghi", "christine lagarde", "lagarde", "ecb president"}

# Executive Board members and GC attendees -> official role (lowercase substrings)
OFFICIALS = {
    # ECB Executive Board
    "constâncio", "constancio",
    "de guindos",
    "praet",
    "lane",
    "cœuré", "coeure",
    "lautenschläger", "lautenschlager",
    "mersch",
    "schnabel",
    "panetta",
    "elderson",
    "cipollone",
    "escrivá", "escriva",
    "mccaul",
    "enria",
    # National Central Bank governors sometimes present at Q&A
    "stournaras", "vasiliauskas", "nowotny", "bonnici",
    "georghadji", "hansson",
}

_WHITESPACE  = re.compile(r"\s+")
_FNAME_RE    = re.compile(r"^ECB_(\d{8})$")
_COPYRIGHT   = re.compile(r"Reproduction is permitted provided that the source is acknowledged\.?", re.IGNORECASE)
# Inline footnote artifacts from ECB website HTML: [1][1]This refers to...
# Pattern requires the doubled bracket (e.g. [1][1]) to avoid false positives like [2024].
_FOOTNOTE    = re.compile(r"\[\d+\]\[\d+\](?:\[[^\]]*\])?\s*[A-Z][^.]*\.")

# Canonical speaker names — raw labels vary by era and transcript format
_SPEAKER_NORM: dict[str, str] = {
    "draghi":           "Mario Draghi",
    "mario draghi":     "Mario Draghi",
    "president draghi": "Mario Draghi",
    "lagarde":           "Christine Lagarde",
    "christine lagarde": "Christine Lagarde",
    "president lagarde": "Christine Lagarde",
    "chair":             "Christine Lagarde",
    "ecb president":     "Christine Lagarde",
    "question":  "Question",
    "questions": "Question",
}


def _normalize_speaker(name: str) -> str:
    return _SPEAKER_NORM.get(name.lower().strip(), name.strip())

# Strong signals that a paragraph is the START of a president response
_PRES_START = re.compile(
    r"^(?:"
    r"On your |On the |On this |On that |"
    r"To your |"
    r"Let me |"
    r"I'll take|"
    r"Thank you for your|"
    r"Answering "
    r")", re.IGNORECASE
)

# Strong signals that a paragraph is the START of a new journalist question
_JOURN_START = re.compile(
    r"^(?:"
    r"I have (?:a |two |three |one )?question|"
    r"My (?:first|second|third|next|other|follow-up) question|"
    r"(?:Then|And) (?:my|a|one|the) (?:second|third|next|other|follow-up) question|"
    r"(?:Then|And) (?:one |a )?(?:more |other |follow-up |)?question|"
    r"Second question|Third question|Another question|"
    r"(?:Could|Can|Would|Do|Does|Did|Is|Are|Will|What|When|Where|Why|How) you"
    r")", re.IGNORECASE
)

# Words that start a paragraph but are NOT speaker labels (prepositions, transitions)
_NON_NAME_FIRST_WORDS = frozenset({
    "About", "After", "Against", "All", "Also", "Alternatively", "Although",
    "And", "As", "At", "Based", "Before", "Because", "But", "By",
    "Certainly", "Clearly", "Coming", "Concerning", "Considering",
    "During", "Even", "Finally", "First", "Firstly", "Following", "For",
    "From", "Further", "Given", "Going", "Here", "However", "I", "If",
    "Important", "Importantly", "In", "Indeed", "It", "Just", "Let",
    "Like", "Looking", "More", "Moreover", "Most", "My", "Naturally",
    "Next", "Now", "Obviously", "Of", "On", "Once", "Only", "Or", "Our",
    "Overall", "Perhaps", "Please", "Probably", "Regarding", "Regarding",
    "Returning", "Secondly", "See", "Since", "So", "Some", "Still",
    "Talking", "That", "The", "Then", "There", "Third", "Thirdly",
    "This", "Those", "Though", "Turning", "Under", "Unless", "Until",
    "We", "Well", "What", "When", "Where", "Which", "While", "With",
    "Without", "Yes", "Yet", "You", "Your",
    # number words at paragraph starts (e.g. "Four: criteria include...")
    "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
    "Nine", "Ten",
})

# Separator between opening statement and Q&A
_QA_SEP = re.compile(r"\*\s*\*\s*\*")

# Curly/smart quote codepoints -> ASCII
_QUOTE_PAIRS = [
    ("‘", "'"), ("’", "'"), ("‚", "'"), ("`", "'"),
    ("“", '"'), ("”", '"'), ("„", '"'),
    ("–", "-"), ("—", "-"),
]


def _normalize_quotes(text: str) -> str:
    for src, dst in _QUOTE_PAIRS:
        text = text.replace(src, dst)
    return text


def _clean_text(text: str) -> str:
    text = _normalize_quotes(text)
    text = _COPYRIGHT.sub("", text)
    text = _FOOTNOTE.sub("", text)
    lines = [_WHITESPACE.sub(" ", ln).strip() for ln in text.splitlines()]
    return "\n".join(lines)


def _in_window(yyyymmdd: str) -> bool:
    try:
        d = date(int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]))
        return STUDY_START <= d <= STUDY_END
    except ValueError:
        return False


def _speaker_role(name: str) -> str:
    n = name.lower().strip()
    if any(p in n for p in PRESIDENTS):
        return "president"
    if n in ("chair",):
        return "president"
    if any(o in n for o in OFFICIALS):
        return "official"
    # journalist labels: 'Question', 'Questions', 'QUESTION', empty
    if n.startswith("question") or n == "":
        return "journalist"
    return "journalist"


def _extract_president(text: str) -> str:
    """Parse the president's name from the first line of the file."""
    first_line = text.splitlines()[0] if text.strip() else ""
    # Format: "Mario Draghi, President of the ECB,..."
    m = re.match(r"^([^,]+),\s*President", first_line, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "ECB President"


def _paragraphs(text: str) -> list[str]:
    """Split text into non-empty paragraphs on blank lines."""
    paras = re.split(r"\n{2,}", text)
    return [p.strip() for p in paras if p.strip()]


def _try_speaker_label(para: str) -> tuple[str, str] | None:
    """
    Return (speaker_name, rest_of_text) if the paragraph starts with a speaker
    label like 'Draghi: ...' or 'Question: ...', otherwise return None.

    Speaker labels consist of 1-3 words each starting with a capital letter,
    followed by a colon. Common prepositions and transition words are excluded
    to avoid false positives like 'On your first question: ...'.
    """
    m = re.match(
        r"^([A-Z][A-Za-zÀ-ÖØ-öø-ÿ]+(?:\s+[A-Z][A-Za-zÀ-ÖØ-öø-ÿ]+){0,2}):\s+(.*)",
        para, re.DOTALL,
    )
    if not m:
        return None
    name = m.group(1).strip()
    first_word = name.split()[0]
    if first_word in _NON_NAME_FIRST_WORDS:
        return None
    return (name, m.group(2).strip())


def _parse_labeled_qa(qa_text: str) -> list[tuple[str, str]]:
    """
    Draghi-era Q&A: paragraphs begin with 'Name:' or 'Question:'.
    Returns list of (speaker, turn_text).
    """
    qa_text = _QA_SEP.sub("", qa_text)

    turns: list[tuple[str, str]] = []
    current_speaker: str | None = None
    current_parts: list[str] = []

    for para in _paragraphs(qa_text):
        label = _try_speaker_label(para)
        if label:
            if current_speaker is not None and current_parts:
                turns.append((current_speaker, " ".join(current_parts)))
            current_speaker, rest = label
            current_parts = [rest] if rest else []
        else:
            if current_speaker is not None:
                current_parts.append(para)
            else:
                turns.append(("Question", para))

    if current_speaker is not None and current_parts:
        turns.append((current_speaker, " ".join(current_parts)))

    return turns


def _parse_alternating_qa(qa_text: str, president: str) -> list[tuple[str, str]]:
    """
    Lagarde-era Q&A: use [Q]/[A] markers when present (added by ecb_remark.py),
    otherwise fall back to linguistic signals.
    """
    qa_text = _QA_SEP.sub("", qa_text)
    paras = _paragraphs(qa_text)

    has_markers = any(p.startswith(("[Q] ", "[A] ")) for p in paras[:10])

    if has_markers:
        current_speaker: str | None = None
        current_parts: list[str] = []
        turns: list[tuple[str, str]] = []
        for para in paras:
            if para.startswith("[Q] "):
                if current_speaker and current_parts:
                    turns.append((current_speaker, " ".join(current_parts)))
                current_speaker = "Question"
                current_parts = [para[4:]]
            elif para.startswith("[A] "):
                if current_speaker and current_parts:
                    turns.append((current_speaker, " ".join(current_parts)))
                current_speaker = president
                current_parts = [para[4:]]
            elif current_speaker:
                current_parts.append(para)
        if current_speaker and current_parts:
            turns.append((current_speaker, " ".join(current_parts)))
        return turns

    # Fallback: linguistic signals
    current_speaker = None
    current_parts = []
    turns = []
    for para in paras:
        if _JOURN_START.match(para):
            new_speaker = "Question"
        elif _PRES_START.match(para):
            new_speaker = president
        else:
            new_speaker = None

        if new_speaker is not None and new_speaker != current_speaker:
            if current_speaker is not None and current_parts:
                turns.append((current_speaker, " ".join(current_parts)))
            current_speaker = new_speaker
            current_parts = [para]
        else:
            if current_speaker is None:
                current_speaker = "Question"
            current_parts.append(para)

    if current_speaker and current_parts:
        turns.append((current_speaker, " ".join(current_parts)))

    return turns


def _is_labeled(qa_text: str) -> bool:
    """Return True if the Q&A section has explicit 'Name:' or 'Question:' labels."""
    sample = _QA_SEP.sub("", qa_text)
    for para in _paragraphs(sample)[:10]:
        if _try_speaker_label(para) is not None:
            return True
    return False


def _parse_turns(text: str) -> list[tuple[str, str, str]]:
    """
    Return list of (speaker, doc_type, turn_text).
    doc_type is 'opening' for the introductory statement, 'presser' for Q&A.
    """
    president = _extract_president(text)

    # Split into opening statement and Q&A on first * * *
    parts = _QA_SEP.split(text, maxsplit=1)
    opening_text = parts[0].strip()
    qa_text = parts[1].strip() if len(parts) > 1 else ""

    turns: list[tuple[str, str, str]] = []

    # Opening statement — entirely attributed to the President
    if opening_text:
        # Strip the header line (Name, Title, Date)
        lines = opening_text.splitlines()
        body_start = 0
        for i, ln in enumerate(lines):
            if re.match(r"^[A-Z].+,\s*(President|Vice-President)", ln):
                body_start = i + 1
                break
        body = "\n".join(lines[body_start:]).strip()
        if body:
            turns.append((president, "opening", body))

    # Q&A section
    if qa_text:
        if _is_labeled(qa_text):
            for speaker, turn_text in _parse_labeled_qa(qa_text):
                turns.append((speaker, "presser", turn_text))
        else:
            for speaker, turn_text in _parse_alternating_qa(qa_text, president):
                turns.append((speaker, "presser", turn_text))

    return turns


def process_file(path: Path) -> list[dict]:
    m = _FNAME_RE.match(path.stem)
    if not m:
        return []

    yyyymmdd = m.group(1)
    if not _in_window(yyyymmdd):
        return []

    raw = path.read_text(encoding="utf-8", errors="replace")
    text = _clean_text(raw)
    turns = _parse_turns(text)

    rows = []
    for turn_idx, (speaker, doc_type, turn_text) in enumerate(turns):
        turn_text = _WHITESPACE.sub(" ", turn_text).strip()
        if not turn_text:
            continue
        role = _speaker_role(speaker)
        if doc_type == "opening":
            turn_type = "opening"
        elif role == "president":
            turn_type = "answer"
        elif role == "journalist":
            turn_type = "question"
        else:
            turn_type = "other"
        rows.append({
            "doc_id":       path.stem,
            "date":         yyyymmdd,
            "doc_type":     doc_type,
            "speaker":      _normalize_speaker(speaker),
            "speaker_role": role,
            "turn_idx":     turn_idx,
            "turn_type":    turn_type,
            "text":         turn_text,
        })
    return rows


def main() -> None:
    files = sorted(IN_DIR.glob("ECB_*.txt"))
    if not files:
        sys.exit(f"No ECB_*.txt files found in {IN_DIR}")

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

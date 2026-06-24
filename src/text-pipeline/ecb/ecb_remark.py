"""
Re-mark existing ECB cleaned transcript files with [Q]/[A] paragraph prefixes.

The ECB website uses bold <p> tags for journalist questions and plain <p> tags
for president answers in the Q&A section. The original scraper stripped all HTML
and lost this signal. This script re-fetches each page's HTML, detects bold, and
rewrites the cleaned files with [Q] / [A] prefixes so ecb_to_csv.py can split
turns reliably without linguistic heuristics.

Input:   data/transcripts/ECB/*.txt          (raw filenames -> URLs)
Output:  data/transcripts_cleaned/ECB/*.txt  (rewritten with [Q]/[A] markers)

URL pattern:
  ecb.is220908~cd8363c58e.en.txt
  -> https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/
     2022/html/ecb.is220908~cd8363c58e.en.html

Run:  uv run src/ecb/ecb_remark.py
"""

import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT      = Path(__file__).parent.parent.parent
RAW_DIR   = ROOT / "data" / "transcripts" / "ECB"
CLEAN_DIR = ROOT / "data" / "transcripts_cleaned" / "ECB"
BASE_URL  = "https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement"

_BOILERPLATE = re.compile(
    r"Disclaimer|Reproduction is permitted|Copyright \d{4}|privacy statement"
    r"|We use functional cookies|working to improve this website"
    r"|Jump to the transcript|You may also be interested",
    re.IGNORECASE,
)

_RAW_FNAME_RE = re.compile(r"^(ecb\.(?:is|sp)|is)(\d{6})(~[a-f0-9]+)?(_\d+)?\.en\.txt$", re.IGNORECASE)
_CLEAN_FNAME_RE = re.compile(r"^ECB_(\d{8})\.txt$")


def _raw_to_url(fname: str) -> str | None:
    """Convert raw filename to ECB URL. Returns None if unrecognised."""
    m = _RAW_FNAME_RE.match(fname)
    if not m:
        return None
    yymmdd = m.group(2)        # e.g. "220908"
    slug   = m.group(1) + m.group(2) + (m.group(3) or "") + (m.group(4) or "")
    yy = int(yymmdd[:2])
    year = 2000 + yy if yy < 30 else 1900 + yy
    return f"{BASE_URL}/{year}/html/{slug.replace('.txt','')}.en.html"


def _raw_to_clean_path(fname: str) -> Path | None:
    """Find the corresponding cleaned file for a raw filename."""
    m = _RAW_FNAME_RE.match(fname)
    if not m:
        return None
    yymmdd = m.group(2)
    yy = int(yymmdd[:2])
    year = 2000 + yy if yy < 30 else 1900 + yy
    clean_name = f"ECB_{year}{yymmdd[2:]}.txt"
    p = CLEAN_DIR / clean_name
    return p if p.exists() else None


def _extract_marked(soup: BeautifulSoup) -> str | None:
    """
    Extract paragraphs from the page, prefixing Q&A paragraphs with [Q] or [A].
    Returns None if no Q&A boundary is found.
    """
    paras = soup.find_all("p")
    lines: list[str] = []
    in_qa = False

    for p in paras:
        text = p.get_text(strip=True)
        if not text:
            continue

        # Structural Q&A boundary: <a id="qa"> anchor (Lagarde era 2019+)
        if p.find("a", id="qa"):
            in_qa = True
            lines.append("* * *")
            continue

        # Text Q&A boundary: * * * separator (Draghi era 2015–2019)
        if re.match(r"^\*\s*\*\s*\*$", text):
            in_qa = True
            lines.append("* * *")
            continue

        if len(text) < 15 or _BOILERPLATE.search(text):
            continue

        if in_qa:
            has_bold = bool(p.find(["b", "strong"]))
            prefix = "[Q] " if has_bold else "[A] "
            lines.append(prefix + text)
        else:
            lines.append(text)

    if not lines:
        return None

    return "\n\n".join(lines)


def remark_file(raw_fname: str, session: requests.Session) -> str:
    """Fetch URL, extract marked text, rewrite cleaned file. Returns status string."""
    url = _raw_to_url(raw_fname)
    if not url:
        return "SKIP (unrecognised filename)"

    clean_path = _raw_to_clean_path(raw_fname)
    if not clean_path:
        return "SKIP (no matching cleaned file)"

    # Idempotent: skip if already marked
    existing = clean_path.read_text(encoding="utf-8", errors="replace")
    if "[Q] " in existing or "[A] " in existing:
        return "SKIP (already marked)"

    try:
        r = session.get(url, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        return f"ERROR ({e})"

    soup = BeautifulSoup(r.text, "html.parser")
    marked = _extract_marked(soup)
    if marked is None:
        return "SKIP (no Q&A boundary found in HTML)"

    clean_path.write_text(marked, encoding="utf-8")
    return "OK"


def main() -> None:
    raw_files = sorted(RAW_DIR.glob("*.txt"))
    if not raw_files:
        sys.exit(f"No files found in {RAW_DIR}")

    print(f"Found {len(raw_files)} raw ECB files. Re-marking cleaned files...\n")

    session = requests.Session()
    session.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    counts = {"OK": 0, "SKIP": 0, "ERROR": 0}
    for rf in raw_files:
        status = remark_file(rf.name, session)
        tag = status.split()[0]
        counts[tag] = counts.get(tag, 0) + 1
        print(f"  {rf.name:50s}  {status}")
        if tag == "OK":
            time.sleep(0.5)  # polite throttle

    print(f"\nDone. OK={counts.get('OK',0)}  SKIP={counts.get('SKIP',0)}  ERROR={counts.get('ERROR',0)}")


if __name__ == "__main__":
    main()

"""
Normalize ECB press conference transcripts.

Reads from:  data/transcripts/ECB/
Writes to:   data/transcripts_normalized/ECB/

Output filename: ECB_YYYYMMDD.txt  (raw text, no added headers)
Study window:    2015-01-01 to 2025-12-31

Handled filename patterns
--------------------------
  ecb.isYYMMDD[~hash].en      modern presser (2017+)
  ecb.spYYMMDD[~hash].en      one-off special presser
  isYYMMDD[~hash].en          old presser (pre-2017)
  isYYMMDD_1.en / _2.en       split files — concatenated if both exist,
                               kept solo otherwise (all pre-2015, filtered out)
"""

import re
import sys
from datetime import date
from pathlib import Path

STUDY_START = date(2015, 1, 1)
STUDY_END   = date(2025, 12, 31)

# strips ecb. prefix, hash suffix, _1/_2 suffix, language tag
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


def main() -> None:
    ecb_dir = Path(__file__).parent.parent / "data" / "transcripts" / "ECB"
    out_dir  = Path(__file__).parent.parent / "data" / "transcripts_normalized" / "ECB"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(ecb_dir.glob("*.txt"))
    if not files:
        sys.exit(f"No .txt files found in {ecb_dir}")

    print(f"Found {len(files)} files in {ecb_dir}\n")

    kept = skipped_window = skipped_unrecognised = 0

    for f in files:
        d = parse_date(f.name)

        if d is None:
            print(f"  UNK  {f.name}")
            skipped_unrecognised += 1
            continue

        if not (STUDY_START <= d <= STUDY_END):
            skipped_window += 1
            continue

        out_name = f"ECB_{d.strftime('%Y%m%d')}.txt"
        out_path = out_dir / out_name

        if out_path.exists():
            print(f"  DUP  {f.name} -> {out_name} (already written, skipping)")
            continue

        text = f.read_text(encoding="utf-8", errors="replace")
        out_path.write_text(text, encoding="utf-8")
        print(f"   OK  {f.name} -> {out_name}")
        kept += 1

    print(f"\nDone.")
    print(f"  Kept (in window):       {kept}")
    print(f"  Skipped (out of window):{skipped_window}")
    print(f"  Skipped (unrecognised): {skipped_unrecognised}")


if __name__ == "__main__":
    main()

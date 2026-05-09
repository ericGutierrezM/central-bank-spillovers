"""
Copy Fed and BoE transcripts into data/transcripts_cleaned/, filtered to
the study window 2015-01-01 -- 2025-12-31, with consistent naming.

Output naming
-------------
Fed:  Fed_YYYYMMDD_{type}.txt   type = meeting | confcall | presconf
BoE:  BoE_YYYYMM_{type}.txt     type = transcript | opening
      (BoE filenames stay unchanged — no exact day available)

Source
------
Fed:  data/transcripts/Fed/raw/     e.g. FOMC20150128meeting.txt
BoE:  data/transcripts/BoE/raw/     e.g. BoE_201502_transcript.txt
"""

import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
STUDY_START = date(2015, 1, 1)
STUDY_END   = date(2025, 12, 31)

FED_RE = re.compile(
    r"^FOMC(\d{8})(meeting|confcall)$|^FOMCpresconf(\d{8})$",
    re.IGNORECASE,
)

BOE_RE = re.compile(r"^BoE_(\d{6})_(transcript|opening)$")


# ── Fed ──────────────────────────────────────────────────────────────────────

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

    print(f"\n--- Fed ({len(files)} files in raw) ---")
    for f in files:
        parsed = parse_fed(f.stem)
        if parsed is None:
            print(f"  UNK  {f.name}")
            continue
        yyyymmdd, doc_type = parsed
        if not in_window_yyyymmdd(yyyymmdd):
            skipped += 1
            continue
        out_name = f"Fed_{yyyymmdd}_{doc_type}.txt"
        shutil.copy2(f, out_dir / out_name)
        print(f"   OK  {f.name} -> {out_name}")
        kept += 1

    print(f"  Fed: {kept} kept, {skipped} outside window")


# ── BoE ──────────────────────────────────────────────────────────────────────

def in_window_yyyymm(yyyymm: str) -> bool:
    try:
        yyyy, mm = int(yyyymm[:4]), int(yyyymm[4:6])
        # include if the month falls within the study years
        return STUDY_START.year <= yyyy <= STUDY_END.year
    except ValueError:
        return False


def process_boe(out_root: Path) -> None:
    src_dir = ROOT / "data" / "transcripts" / "BoE" / "raw"
    out_dir = out_root / "BoE"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(src_dir.glob("*.txt"))
    kept = skipped = 0

    print(f"\n--- BoE ({len(files)} files in raw) ---")
    for f in files:
        m = BOE_RE.match(f.stem)
        if not m:
            print(f"  UNK  {f.name}")
            continue
        yyyymm = m.group(1)
        if not in_window_yyyymm(yyyymm):
            skipped += 1
            continue
        shutil.copy2(f, out_dir / f.name)
        print(f"   OK  {f.name}")
        kept += 1

    print(f"  BoE: {kept} kept, {skipped} outside window")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    out_root = ROOT / "data" / "transcripts_cleaned"
    process_fed(out_root)
    process_boe(out_root)

    print("\n--- Summary ---")
    for bank in ("Fed", "BoE", "ECB"):
        d = out_root / bank
        if d.exists():
            n = len(list(d.glob("*.txt")))
            print(f"  {bank}: {n} files in {d.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

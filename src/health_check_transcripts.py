from __future__ import annotations

import argparse
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from transcript_cleaning.vulgar_fractions import VULGAR_FRACTIONS


ROOT = Path(__file__).resolve().parent.parent
BANKS = ("BoE", "ECB", "Fed")


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(errors="backslashreplace")


@dataclass
class FileReport:
    path: Path
    bank: str
    fractions_found: Counter[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan normalized transcripts for Unicode vulgar fractions."
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("data/transcripts_normalized"),
        help="Root directory containing BoE, ECB, and Fed subdirectories.",
    )
    return parser.parse_args()


def iter_transcript_files(root_dir: Path) -> list[tuple[str, Path]]:
    direct_files = sorted(root_dir.rglob("*.txt"))
    if direct_files and not any((root_dir / bank).exists() for bank in BANKS):
        bank = next(
            (
                candidate
                for candidate in BANKS
                if candidate.lower() in {part.lower() for part in root_dir.parts}
            ),
            root_dir.name,
        )
        return [(bank, path) for path in direct_files]

    files: list[tuple[str, Path]] = []
    for bank in BANKS:
        bank_dir = root_dir / bank
        if not bank_dir.exists():
            print(f"[WARN] Missing bank directory: {bank_dir}", file=sys.stderr)
            continue
        files.extend((bank, path) for path in sorted(bank_dir.rglob("*.txt")))
    return files


def unicode_name(char: str) -> str:
    return unicodedata.name(char, "UNKNOWN")


def scan_file(bank: str, path: Path) -> FileReport:
    text = path.read_text(encoding="utf-8", errors="replace")
    fractions_found = Counter(ch for ch in text if ch in VULGAR_FRACTIONS)
    return FileReport(path=path, bank=bank, fractions_found=fractions_found)


def print_global_summary(
    reports: list[FileReport],
    fraction_doc_counts: Counter[str],
    fraction_total_counts: Counter[str],
) -> None:
    print("=== Vulgar Fractions in Corpus ===")
    print(f"Total files scanned: {len(reports)}")
    print()

    if not fraction_doc_counts:
        print("No vulgar fractions found.")
        return

    rows = [
        (
            ch,
            f"U+{ord(ch):04X}",
            unicode_name(ch),
            fraction_doc_counts[ch],
            fraction_total_counts[ch],
        )
        for ch in fraction_doc_counts
    ]
    rows.sort(key=lambda row: (-row[3], row[0]))

    name_width = max(len("Name"), max(len(row[2]) for row in rows))
    docs_width = max(len("Docs"), max(len(str(row[3])) for row in rows))
    total_width = max(len("Total occurrences"), max(len(str(row[4])) for row in rows))

    print(
        f"{'Char':<4}   {'U+':<6}  {'Name':<{name_width}}  "
        f"{'Docs':>{docs_width}}   {'Total occurrences':>{total_width}}"
    )
    for ch, codepoint, name, doc_count, total_count in rows:
        print(
            f"{ch:<4}   {codepoint:<6}  {name:<{name_width}}  "
            f"{doc_count:>{docs_width}}   {total_count:>{total_width}}"
        )


def main() -> None:
    configure_stdio()
    args = parse_args()
    root_dir = args.dir
    if not root_dir.is_absolute():
        root_dir = ROOT / root_dir
    root_dir = root_dir.resolve()

    file_specs = iter_transcript_files(root_dir)
    if not file_specs:
        print(f"No transcript files found under {root_dir}", file=sys.stderr)
        raise SystemExit(1)

    reports: list[FileReport] = []
    fraction_doc_counts: Counter[str] = Counter()
    fraction_total_counts: Counter[str] = Counter()

    for bank, path in file_specs:
        report = scan_file(bank, path)
        reports.append(report)
        for ch in report.fractions_found:
            fraction_doc_counts[ch] += 1
        fraction_total_counts.update(report.fractions_found)

    print_global_summary(reports, fraction_doc_counts, fraction_total_counts)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Callable

from .vulgar_fractions import VULGAR_FRACTION_REPLACEMENTS


ROOT = Path(__file__).resolve().parent.parent.parent


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(errors="backslashreplace")


def resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (ROOT / path).resolve()


def parse_bank_args(
    bank: str,
    default_input_dir: str,
    default_output_dir: str,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Apply cleaning steps to normalized {bank} transcripts."
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path(default_input_dir),
        help=f"Input directory for normalized {bank} transcripts.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(default_output_dir),
        help=f"Output directory for cleaned {bank} transcripts.",
    )
    return parser.parse_args()


def iter_transcript_files(root_dir: Path) -> list[Path]:
    return sorted(root_dir.rglob("*.txt"))


def print_summary(
    bank: str,
    total_files: int,
    changed_files: int,
    replacement_doc_counts: Counter[str],
    replacement_total_counts: Counter[str],
) -> None:
    print(f"=== {bank} Cleaning Summary ===")
    print(f"Total files processed: {total_files}")
    print(f"Files changed: {changed_files}")
    print()

    if not replacement_total_counts:
        print("No vulgar fractions found.")
        return

    replacement_label_width = max(
        len("Replacement"),
        max(len(VULGAR_FRACTION_REPLACEMENTS[ch]) for ch in replacement_total_counts),
    )
    docs_width = max(
        len("Docs"),
        max(len(str(count)) for count in replacement_doc_counts.values()),
    )
    total_width = max(
        len("Total replacements"),
        max(len(str(count)) for count in replacement_total_counts.values()),
    )

    print(
        f"{'Char':<8}{'Replacement':<{replacement_label_width + 3}}"
        f"{'Docs':>{docs_width + 3}}   {'Total replacements':>{total_width}}"
    )
    for ch, doc_count in sorted(
        replacement_doc_counts.items(),
        key=lambda item: (-item[1], item[0]),
    ):
        display_char = ch.encode("ascii", "backslashreplace").decode("ascii")
        print(
            f"{display_char:<8}{VULGAR_FRACTION_REPLACEMENTS[ch]:<{replacement_label_width + 3}}"
            f"{doc_count:>{docs_width + 3}}   {replacement_total_counts[ch]:>{total_width}}"
        )


def run_cleaning_job(
    bank: str,
    cleaner: Callable[[str], tuple[str, Counter[str]]],
    default_input_dir: str,
    default_output_dir: str,
) -> None:
    configure_stdio()
    args = parse_bank_args(bank, default_input_dir, default_output_dir)
    input_root = resolve_path(args.dir)
    output_root = resolve_path(args.out_dir)

    file_paths = iter_transcript_files(input_root)
    if not file_paths:
        raise SystemExit(f"No transcript files found under {input_root}")

    changed_files = 0
    replacement_doc_counts: Counter[str] = Counter()
    replacement_total_counts: Counter[str] = Counter()

    for src_path in file_paths:
        relative_path = src_path.relative_to(input_root)
        dest_path = output_root / relative_path

        text = src_path.read_text(encoding="utf-8", errors="replace")
        cleaned_text, fractions_found = cleaner(text)

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(cleaned_text, encoding="utf-8")

        if fractions_found:
            changed_files += 1
            for ch in fractions_found:
                replacement_doc_counts[ch] += 1
            replacement_total_counts.update(fractions_found)

    print_summary(
        bank=bank,
        total_files=len(file_paths),
        changed_files=changed_files,
        replacement_doc_counts=replacement_doc_counts,
        replacement_total_counts=replacement_total_counts,
    )

from __future__ import annotations

from transcript_cleaning.boe import clean_boe_text
from transcript_cleaning.common import run_cleaning_job


def main() -> None:
    run_cleaning_job(
        bank="BoE",
        cleaner=clean_boe_text,
        default_input_dir="data/transcripts_normalized/BoE",
        default_output_dir="data/transcripts_cleaned/BoE",
    )


if __name__ == "__main__":
    main()

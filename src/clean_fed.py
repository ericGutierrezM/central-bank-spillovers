from __future__ import annotations

from transcript_cleaning.common import run_cleaning_job
from transcript_cleaning.fed import clean_fed_text


def main() -> None:
    run_cleaning_job(
        bank="Fed",
        cleaner=clean_fed_text,
        default_input_dir="data/transcripts_normalized/Fed",
        default_output_dir="data/transcripts_cleaned/Fed",
    )


if __name__ == "__main__":
    main()

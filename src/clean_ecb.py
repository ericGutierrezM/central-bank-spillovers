from __future__ import annotations

from transcript_cleaning.common import run_cleaning_job
from transcript_cleaning.ecb import clean_ecb_text


def main() -> None:
    run_cleaning_job(
        bank="ECB",
        cleaner=clean_ecb_text,
        default_input_dir="data/transcripts_normalized/ECB",
        default_output_dir="data/transcripts_cleaned/ECB",
    )


if __name__ == "__main__":
    main()

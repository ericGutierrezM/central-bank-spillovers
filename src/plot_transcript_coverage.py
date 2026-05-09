from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "transcripts_cleaned"
OUTPUT_PATH = ROOT / "output" / "coverage_timeline.png"

BANKS = ("Fed", "ECB", "BoE")
COLORS = {
    "Fed": "#2C7FB8",
    "ECB": "#F28E2B",
    "BoE": "#59A14F",
}
DATE_PATTERNS = {
    "Fed": re.compile(r"^Fed_(\d{8})_"),
    "ECB": re.compile(r"^ECB_(\d{8})$"),
    "BoE": re.compile(r"^BoE_(\d{6})_"),
}


@dataclass(frozen=True)
class BankSeries:
    name: str
    monthly_counts: Counter[tuple[int, int]]


def parse_month_key(bank: str, path: Path) -> tuple[int, int]:
    match = DATE_PATTERNS[bank].match(path.stem)
    if not match:
        raise ValueError(f"Unrecognized {bank} filename: {path.name}")

    raw = match.group(1)
    if bank == "BoE":
        timestamp = pd.Timestamp(year=int(raw[:4]), month=int(raw[4:6]), day=1)
    else:
        timestamp = pd.Timestamp(
            year=int(raw[:4]),
            month=int(raw[4:6]),
            day=int(raw[6:8]),
        ).to_period("M").to_timestamp()

    return (timestamp.year, timestamp.month)


def count_bank_months(bank: str, bank_dir: Path) -> BankSeries:
    counts: Counter[tuple[int, int]] = Counter()
    for path in sorted(bank_dir.glob("*.txt")):
        counts[parse_month_key(bank, path)] += 1
    return BankSeries(name=bank, monthly_counts=counts)


def build_month_index(series_list: list[BankSeries]) -> pd.DatetimeIndex:
    all_keys = [
        pd.Timestamp(year=year, month=month, day=1)
        for series in series_list
        for (year, month) in series.monthly_counts
    ]
    if not all_keys:
        raise ValueError("No transcript files found in data/transcripts_cleaned.")

    start = min(all_keys)
    end = max(all_keys)
    return pd.date_range(start=start, end=end, freq="MS")


def materialize_counts(
    series_list: list[BankSeries], month_index: pd.DatetimeIndex
) -> dict[str, pd.Series]:
    output: dict[str, pd.Series] = {}
    for series in series_list:
        values = [
            series.monthly_counts.get((timestamp.year, timestamp.month), 0)
            for timestamp in month_index
        ]
        output[series.name] = pd.Series(values, index=month_index)
    return output


def plot_coverage(counts_by_bank: dict[str, pd.Series], output_path: Path) -> None:
    fig, axes = plt.subplots(
        nrows=3,
        ncols=1,
        figsize=(15, 8),
        sharex=True,
        constrained_layout=True,
    )

    for idx, bank in enumerate(BANKS):
        ax = axes[idx]
        series = counts_by_bank[bank]
        ax.bar(
            series.index,
            series.values,
            width=24,
            color=COLORS[bank],
            alpha=0.9,
            edgecolor="white",
            linewidth=0.7,
        )
        ax.set_ylabel("Docs")
        ax.set_title(bank, loc="left", fontsize=12, fontweight="bold")
        ax.set_ylim(0, max(2.2, float(series.max()) + 0.6))
        ax.grid(axis="y", alpha=0.25)

    axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.setp(axes[-1].get_xticklabels(), rotation=45, ha="right")
    fig.suptitle("Transcript Coverage by Bank and Month", fontsize=15, fontweight="bold")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    series_list = [
        count_bank_months(bank, DATA_DIR / bank)
        for bank in BANKS
    ]
    month_index = build_month_index(series_list)
    counts_by_bank = materialize_counts(series_list, month_index)
    plot_coverage(counts_by_bank, OUTPUT_PATH)
    print(f"Saved coverage plot to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

"""
Plot LLM tone score distributions by central bank.
Tests whether FED scores cluster near zero (formulaic language) vs ECB/BoE.
Output: notebooks/tone_distribution_by_bank.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import gaussian_kde
from pathlib import Path

ROOT = Path(__file__).parent.parent
AGG = ROOT / "output" / "aggregated"
OUT = ROOT / "notebooks" / "tone_distribution_by_bank.png"

MODELS = {
    "deepseekv3":       "DeepSeek-V3",
    "gemini25flash":    "Gemini 2.5 Flash",
    "gpt-4o":           "GPT-4o",
    "llama33":          "Llama 3.3",
    "mistrallarge_or":  "Mistral Large",
    "qwen25_72b":       "Qwen2.5-72B",
}

BANKS = {
    "fed": "FED",
    "ecb": "ECB",
    "boe": "BoE",
}

COLORS = [
    "#E63946",  # red       – DeepSeek
    "#2196F3",  # blue      – Gemini
    "#FF9800",  # orange    – GPT-4o
    "#4CAF50",  # green     – Llama
    "#9C27B0",  # purple    – Mistral
    "#009688",  # teal      – Qwen
]

# ── load data ─────────────────────────────────────────────────────────────────

data = {}   # (bank_key, model_key) -> stance Series

for bank_key in BANKS:
    for model_key in MODELS:
        path = AGG / f"{bank_key}_{model_key}.csv"
        if not path.exists():
            print(f"Missing: {path.name}")
            continue
        df = pd.read_csv(path, parse_dates=["date"])
        data[(bank_key, model_key)] = df["stance"].dropna()

# ── summary stats ──────────────────────────────────────────────────────────────

print(f"\n{'Model':<22} {'FED std':>8} {'ECB std':>8} {'BoE std':>8}")
print("-" * 50)
for model_key, model_label in MODELS.items():
    stds = []
    for bank_key in BANKS:
        s = data.get((bank_key, model_key), pd.Series(dtype=float))
        stds.append(s.std())
    print(f"{model_label:<22} {stds[0]:>8.4f} {stds[1]:>8.4f} {stds[2]:>8.4f}")

# ── figure: 3 columns (banks) × 2 rows (KDE + variance bar) ──────────────────

fig = plt.figure(figsize=(14, 8))
fig.patch.set_facecolor("white")

gs = gridspec.GridSpec(
    2, 3,
    figure=fig,
    height_ratios=[3, 1],
    hspace=0.35,
    wspace=0.35,
)

kde_axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
bar_axes = [fig.add_subplot(gs[1, i]) for i in range(3)]

x_grid = np.linspace(-0.6, 0.6, 400)

for col, (bank_key, bank_label) in enumerate(BANKS.items()):
    ax_kde = kde_axes[col]
    ax_bar = bar_axes[col]

    stds = []
    for (model_key, model_label), color in zip(MODELS.items(), COLORS):
        series = data.get((bank_key, model_key), pd.Series(dtype=float))
        if len(series) < 5:
            stds.append(np.nan)
            continue

        std = series.std()
        stds.append(std)

        # KDE
        kde = gaussian_kde(series, bw_method="scott")
        ax_kde.plot(x_grid, kde(x_grid), color=color, lw=1.8, label=model_label)
        ax_kde.fill_between(x_grid, kde(x_grid), alpha=0.08, color=color)

    # zero line
    ax_kde.axvline(0, color="black", lw=0.8, ls="--", alpha=0.5)

    ax_kde.set_title(bank_label, fontsize=14, fontweight="bold", pad=8)
    ax_kde.set_xlabel("Stance score (hawk > 0, dove < 0)", fontsize=8)
    ax_kde.set_ylabel("Density", fontsize=8) if col == 0 else None
    ax_kde.tick_params(labelsize=8)
    ax_kde.set_xlim(-0.55, 0.55)
    ax_kde.spines[["top", "right"]].set_visible(False)

    # variance bar chart
    bar_colors = [c for c in COLORS]
    bars = ax_bar.bar(
        range(len(MODELS)),
        stds,
        color=bar_colors,
        width=0.6,
        edgecolor="white",
        linewidth=0.5,
    )
    ax_bar.set_xticks(range(len(MODELS)))
    ax_bar.set_xticklabels(
        [m.split()[0] for m in MODELS.values()],  # first word only to save space
        fontsize=7,
        rotation=35,
        ha="right",
    )
    ax_bar.set_ylabel("Std dev", fontsize=8) if col == 0 else None
    ax_bar.tick_params(labelsize=7)
    ax_bar.spines[["top", "right"]].set_visible(False)
    ax_bar.set_ylim(0, max(s for s in stds if not np.isnan(s)) * 1.3)

    # annotate bars with values
    for bar, val in zip(bars, stds):
        if not np.isnan(val):
            ax_bar.text(
                bar.get_x() + bar.get_width() / 2,
                val + 0.002,
                f"{val:.3f}",
                ha="center", va="bottom", fontsize=6.5,
            )

# ── shared legend ──────────────────────────────────────────────────────────────

handles = [
    plt.Line2D([0], [0], color=c, lw=2, label=lab)
    for c, lab in zip(COLORS, MODELS.values())
]
fig.legend(
    handles=handles,
    loc="lower center",
    ncol=6,
    fontsize=8,
    frameon=False,
    bbox_to_anchor=(0.5, -0.04),
)

fig.suptitle(
    "LLM Tone Score Distributions by Central Bank\n"
    "(top: density; bottom: std dev per model)",
    fontsize=12,
    fontweight="bold",
    y=1.01,
)

plt.savefig(OUT, dpi=180, bbox_inches="tight")
print(f"\nSaved → {OUT}")
plt.show()

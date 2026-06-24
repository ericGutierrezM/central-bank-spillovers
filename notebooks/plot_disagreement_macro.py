"""
LLM disagreement vs realized volatility — all 3 central banks.

Disagreement = ordinal std dev of 6 models' stance labels per turn, averaged to meeting level.
Volatility   = 20-day trailing realized vol of the respective local equity index:
               FED -> S&P 500 | ECB -> Euro Stoxx 50 | BoE -> FTSE 100

Outputs:
  notebooks/disagreement_vol_timeseries.png   (3-panel time series)
  notebooks/disagreement_vol_correlations.png  (3x3: bank x [ACF | scatter | forward])
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from pathlib import Path

ROOT = Path(__file__).parent.parent
AGG  = ROOT / "output" / "stance"
CTRL = ROOT / "data" / "controls"
OUT  = ROOT / "notebooks"

MODELS = [
    "deepseekv3", "gemini25flash", "gpt-4o",
    "llama33", "mistrallarge_or", "qwen25_72b",
]
ORDINAL = {"dovish": -2, "mostly dovish": -1, "neutral": 0,
           "mostly hawkish": 1, "hawkish": 2}

BANKS = {
    "Fed": dict(
        label="FED",
        ctrl_file="FED_CONTROLS.csv",
        index_col="S&P 500",
        color="#E63946",
        date_fmt="%Y%m%d",   # 8-digit full date in predictions
    ),
    "ECB": dict(
        label="ECB",
        ctrl_file="ECB_CONTROLS.csv",
        index_col="Euro Stoxx 50",
        color="#2196F3",
        date_fmt="%Y%m",     # 6-digit year-month in predictions
    ),
    "BoE": dict(
        label="BoE",
        ctrl_file="BOE_CONTROLS.csv",
        index_col="FTSE 100",
        color="#4CAF50",
        date_fmt="%Y%m",
    ),
}

# ── Step 1: load all turns ────────────────────────────────────────────────────

frames = []
for m in MODELS:
    df = pd.read_csv(AGG / f"turn_predictions_{m}.csv",
                     usecols=["bank", "date", "turn_uid", "label"])
    df["model"] = m
    frames.append(df)
all_turns = pd.concat(frames, ignore_index=True)
all_turns["ordinal"] = all_turns["label"].str.lower().map(ORDINAL)
all_turns = all_turns.dropna(subset=["ordinal"])

# ── Step 2: daily equity data → 20-day realized vol ──────────────────────────

idx = (
    pd.read_csv(CTRL / "global_indices_daily.csv", parse_dates=["Date"])
    .rename(columns={"Date": "date_d"})
    .sort_values("date_d")
    .reset_index(drop=True)
)

VOL_WINDOW = 20
for col in ["S&P 500", "Euro Stoxx 50", "FTSE 100"]:
    log_ret = np.log(idx[col]).diff()
    idx[f"rvol_{col}"] = log_ret.rolling(VOL_WINDOW).std() * np.sqrt(252) * 100

vix = (
    pd.read_csv(CTRL / "vix_daily.csv", parse_dates=["Date"])
    .rename(columns={"Date": "date_d", "VIX": "vix"})
    .dropna()
    .sort_values("date_d")
)

def nearest_val(daily_df, target_date, col, max_lag=5):
    window = daily_df[
        (daily_df["date_d"] >= target_date - pd.Timedelta(days=max_lag)) &
        (daily_df["date_d"] <= target_date + pd.Timedelta(days=max_lag))
    ].copy()
    if window.empty:
        return np.nan
    window["diff"] = (window["date_d"] - target_date).abs()
    return window.loc[window["diff"].idxmin(), col]

def forward_dvol(daily_df, target_date, h_days, col):
    v0 = nearest_val(daily_df, target_date, col)
    future = daily_df[daily_df["date_d"] > target_date]["date_d"]
    if len(future) < h_days:
        return np.nan
    v1 = nearest_val(daily_df, future.iloc[h_days - 1], col)
    if pd.isna(v0) or pd.isna(v1):
        return np.nan
    return v1 - v0

# ── Step 3: build per-bank meeting panel ─────────────────────────────────────

def build_meeting_panel(bank_key, cfg):
    turns = all_turns[all_turns["bank"] == bank_key].copy()

    # parse dates
    turns["date"] = pd.to_datetime(
        turns["date"].astype(str), format=cfg["date_fmt"], errors="coerce"
    )
    turns = turns.dropna(subset=["date"])

    # for year-month dates: snap to exact meeting date via controls file
    if cfg["date_fmt"] == "%Y%m":
        ctrl = pd.read_csv(CTRL / cfg["ctrl_file"], parse_dates=["date"])
        ctrl["ym"] = ctrl["date"].dt.to_period("M")
        turns["ym"] = turns["date"].dt.to_period("M")
        ym_to_date = ctrl.set_index("ym")["date"].to_dict()
        turns["date"] = turns["ym"].map(ym_to_date)
        turns = turns.dropna(subset=["date"])

    # disagreement
    turn_std = (
        turns.groupby(["date", "turn_uid"])["ordinal"]
        .std(ddof=1)
        .reset_index(name="std_dev")
    )
    meeting = (
        turn_std.groupby("date")
        .agg(disagreement=("std_dev", "mean"),
             n_turns=("turn_uid", "nunique"))
        .reset_index()
        .sort_values("date")
        .reset_index(drop=True)
    )

    # realized vol on meeting date
    vol_col = f"rvol_{cfg['index_col']}"
    meeting["rvol"] = meeting["date"].apply(
        lambda d: nearest_val(idx, d, vol_col)
    )

    # forward delta-vol
    for h in [1, 5, 10, 20]:
        meeting[f"dvol_{h}d"] = meeting["date"].apply(
            lambda d: forward_dvol(idx, d, h, vol_col)
        )

    print(f"\n{cfg['label']}: {len(meeting)} meetings, "
          f"{meeting['date'].min().date()} to {meeting['date'].max().date()}")
    print(f"  mean disagreement={meeting['disagreement'].mean():.3f}, "
          f"  mean rvol={meeting['rvol'].mean():.1f}%")

    return meeting

panels = {k: build_meeting_panel(k, v) for k, v in BANKS.items()}

# ── Step 4: time series figure ────────────────────────────────────────────────

fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=False)
fig.patch.set_facecolor("white")

shading = [
    ("2020-02-01", "2020-06-01", "COVID"),
    ("2022-03-01", "2023-07-01", "2022 hikes"),
]

for ax, (bk, cfg) in zip(axes, BANKS.items()):
    meeting = panels[bk]
    color = cfg["color"]
    dates = meeting["date"]

    ax.plot(dates, meeting["disagreement"], color=color, lw=1.8, label="Disagreement", zorder=3)
    ax.fill_between(dates, meeting["disagreement"], alpha=0.15, color=color)

    ax2 = ax.twinx()
    ax2.fill_between(dates, meeting["rvol"], alpha=0.15, color="gray")
    ax2.plot(dates, meeting["rvol"], color="gray", lw=1.2, alpha=0.8, label="Realized vol")
    ax2.set_ylabel("Realized vol (%)", fontsize=8, color="gray")
    ax2.tick_params(axis="y", labelcolor="gray", labelsize=7)

    for start, end, label in shading:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), color="gray", alpha=0.08)

    ax.set_ylabel(f"{cfg['label']} disagreement\n(ordinal std dev)", fontsize=9, color=color)
    ax.tick_params(axis="y", labelcolor=color, labelsize=8)
    ax.tick_params(axis="x", labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.spines[["top"]].set_visible(False)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=7, loc="upper left")

fig.suptitle("LLM Disagreement vs Realized Volatility — All Banks",
             fontsize=12, fontweight="bold")
plt.tight_layout()
fig.savefig(OUT / "disagreement_vol_timeseries.png", dpi=180, bbox_inches="tight")
print(f"\nSaved -> {OUT / 'disagreement_vol_timeseries.png'}")

# ── Step 5: 3×3 correlation figure ───────────────────────────────────────────

BLOCK = 4
N_BOOT = 3000
rng = np.random.default_rng(42)

fig2, axes2 = plt.subplots(3, 3, figsize=(16, 13))
fig2.patch.set_facecolor("white")

for row, (bk, cfg) in enumerate(BANKS.items()):
    meeting = panels[bk]
    color = cfg["color"]
    sub_c = meeting[["disagreement", "rvol"]].dropna()
    d_arr = sub_c["disagreement"].values
    v_arr = sub_c["rvol"].values
    n = len(d_arr)

    # autocorrelation
    rho_d = np.corrcoef(d_arr[:-1], d_arr[1:])[0, 1] if n > 2 else 0
    rho_v = np.corrcoef(v_arr[:-1], v_arr[1:])[0, 1] if n > 2 else 0
    n_eff = n * (1 - rho_d * rho_v) / (1 + rho_d * rho_v)
    max_lag = min(10, n // 3)
    bartlett_ci = 1.96 / np.sqrt(n)
    acf_d = [np.corrcoef(d_arr[:n-k], d_arr[k:])[0, 1] for k in range(max_lag + 1)]
    acf_v = [np.corrcoef(v_arr[:n-k], v_arr[k:])[0, 1] for k in range(max_lag + 1)]

    # pearson + adjusted p
    r_naive, p_naive = stats.pearsonr(d_arr, v_arr)
    t_adj = r_naive * np.sqrt((n_eff - 2) / (1 - r_naive**2))
    p_adj = 2 * (1 - stats.t.cdf(abs(t_adj), df=n_eff - 2))

    # block bootstrap for contemporaneous
    boot_rs = []
    for _ in range(N_BOOT):
        n_blk = int(np.ceil(n / BLOCK))
        starts = rng.integers(0, max(1, n - BLOCK + 1), n_blk)
        idx_b = np.concatenate([np.arange(s, min(s + BLOCK, n)) for s in starts])[:n]
        try:
            boot_rs.append(stats.pearsonr(d_arr[idx_b], v_arr[idx_b])[0])
        except Exception:
            pass
    boot_rs = np.array(boot_rs)
    bb_lo = np.percentile(boot_rs, 2.5)
    bb_hi = np.percentile(boot_rs, 97.5)
    p_bb = 2 * min(np.mean(boot_rs <= 0), np.mean(boot_rs >= 0))

    print(f"\n{cfg['label']}  n={n}  N_eff={n_eff:.0f}  AR1_d={rho_d:.2f}  AR1_v={rho_v:.2f}")
    print(f"  r={r_naive:.3f}  naive p={p_naive:.4f}  adj p={p_adj:.4f}  bb p={p_bb:.4f}  CI=[{bb_lo:.3f},{bb_hi:.3f}]")

    # ── col 0: ACF ────────────────────────────────────────────────────────────
    ax_acf = axes2[row, 0]
    lags = np.arange(max_lag + 1)
    w = 0.35
    ax_acf.bar(lags - w/2, acf_d, width=w, color=color, alpha=0.8, label="Disagreement")
    ax_acf.bar(lags + w/2, acf_v, width=w, color="gray",  alpha=0.6, label="Realized vol")
    ax_acf.axhline(0, color="black", lw=0.8)
    ax_acf.axhline( bartlett_ci, color="darkgray", lw=1, ls="--", alpha=0.7)
    ax_acf.axhline(-bartlett_ci, color="darkgray", lw=1, ls="--", alpha=0.7)
    ax_acf.set_title(f"{cfg['label']}  ACF\nAR(1): d={rho_d:.2f}, v={rho_v:.2f}  N_eff={n_eff:.0f}",
                     fontsize=9, fontweight="bold")
    ax_acf.set_xlabel("Lag (meetings)", fontsize=8)
    ax_acf.set_ylabel("Autocorrelation", fontsize=8)
    ax_acf.set_xticks(lags)
    ax_acf.legend(fontsize=7, loc="upper right")
    ax_acf.spines[["top", "right"]].set_visible(False)
    ax_acf.tick_params(labelsize=7)

    # ── col 1: contemporaneous scatter ────────────────────────────────────────
    ax_sc = axes2[row, 1]
    ax_sc.scatter(d_arr, v_arr, color=color, alpha=0.6, s=35,
                  edgecolors="white", linewidth=0.3, zorder=3)
    m_fit, b_fit = np.polyfit(d_arr, v_arr, 1)
    xline = np.linspace(d_arr.min(), d_arr.max(), 200)
    ax_sc.plot(xline, m_fit * xline + b_fit, color="black", lw=1.5)
    stats_txt = (
        f"r = {r_naive:.3f}\n"
        f"Naive p  = {p_naive:.4f}\n"
        f"Adj p    = {p_adj:.4f}\n"
        f"BB p     = {p_bb:.4f}\n"
        f"BB CI [{bb_lo:.2f}, {bb_hi:.2f}]"
    )
    ax_sc.text(0.05, 0.95, stats_txt, transform=ax_sc.transAxes,
               fontsize=8, va="top", family="monospace",
               bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="lightgray", alpha=0.9))
    ax_sc.set_xlabel("Disagreement (ordinal std dev)", fontsize=8)
    ax_sc.set_ylabel(f"{cfg['label']} realized vol (%)", fontsize=8)
    ax_sc.set_title(f"{cfg['label']}  Contemporaneous\nDisagreement vs Realized Vol",
                    fontsize=9, fontweight="bold")
    ax_sc.spines[["top", "right"]].set_visible(False)
    ax_sc.tick_params(labelsize=7)

    # ── col 2: forward delta-vol ──────────────────────────────────────────────
    ax_fwd = axes2[row, 2]
    forward_hs = [1, 5, 10, 20]
    fwd_rs, fwd_lo, fwd_hi, fwd_ns = [], [], [], []

    print(f"  Forward delta-vol ({cfg['label']}):")
    for h in forward_hs:
        col_f = f"dvol_{h}d"
        sub_f = meeting[["disagreement", col_f]].dropna()
        if len(sub_f) < 5:
            fwd_rs.append(0); fwd_lo.append(0); fwd_hi.append(0); fwd_ns.append(0)
            continue
        xf, yf = sub_f["disagreement"].values, sub_f[col_f].values
        r_f, _ = stats.pearsonr(xf, yf)
        fwd_rs.append(r_f)
        fwd_ns.append(len(sub_f))

        nf = len(xf)
        boot_f = []
        for _ in range(N_BOOT):
            n_blk = int(np.ceil(nf / BLOCK))
            starts = rng.integers(0, max(1, nf - BLOCK + 1), n_blk)
            idx_f = np.concatenate([np.arange(s, min(s + BLOCK, nf)) for s in starts])[:nf]
            try:
                boot_f.append(stats.pearsonr(xf[idx_f], yf[idx_f])[0])
            except Exception:
                pass
        boot_f = np.array(boot_f)
        lo_f, hi_f = np.percentile(boot_f, 2.5), np.percentile(boot_f, 97.5)
        p_f = 2 * min(np.mean(boot_f <= 0), np.mean(boot_f >= 0))
        fwd_lo.append(r_f - lo_f)
        fwd_hi.append(hi_f - r_f)
        print(f"    h={h:>2}d  r={r_f:.3f}  p={p_f:.4f}  CI=[{lo_f:.3f},{hi_f:.3f}]")

    x_pos = np.arange(len(forward_hs))
    bar_colors = [color if r >= 0 else "#AAAAAA" for r in fwd_rs]
    ax_fwd.bar(x_pos, fwd_rs, color=bar_colors, alpha=0.75, width=0.5,
               yerr=[fwd_lo, fwd_hi], capsize=4,
               error_kw={"elinewidth": 1.2, "ecolor": "black"})
    ax_fwd.axhline(0, color="black", lw=0.8, ls="--", alpha=0.5)
    ax_fwd.set_xticks(x_pos)
    ax_fwd.set_xticklabels([f"h={h}d" for h in forward_hs], fontsize=8)
    ax_fwd.set_ylabel("Pearson r with delta-vol", fontsize=8)
    ax_fwd.set_title(f"{cfg['label']}  Forward\nDisagreement vs delta-vol (BB CI)",
                     fontsize=9, fontweight="bold")
    ax_fwd.spines[["top", "right"]].set_visible(False)
    ax_fwd.tick_params(labelsize=7)
    for xi, (r_val, n_val) in enumerate(zip(fwd_rs, fwd_ns)):
        if n_val > 0:
            ax_fwd.text(xi, r_val + (0.02 if r_val >= 0 else -0.03),
                        f"n={n_val}", ha="center",
                        va="bottom" if r_val >= 0 else "top", fontsize=7)

fig2.suptitle("LLM Disagreement vs Realized Volatility — Autocorrelation-Corrected",
              fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
fig2.savefig(OUT / "disagreement_vol_correlations.png", dpi=180, bbox_inches="tight")
print(f"\nSaved -> {OUT / 'disagreement_vol_correlations.png'}")

plt.show()

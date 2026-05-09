# Central Bank Spillovers

## Research Question

Does central bank *rhetoric* — independent of actual rate changes — cause asymmetric cross-border spillovers in equity markets? Specifically: does the Federal Reserve dictate European and UK market volatility more than the ECB or BoE dictate US markets?

---

## Core Idea

Existing work (e.g., Raviv et al.) uses FinBERT sentiment + Local Projections to show central bank text moves domestic markets. We extend this in three ways:

1. **Better NLP:** Replace FinBERT's 1D positive/negative score with LLM prompt engineering that extracts *Hawkishness* and *Uncertainty* as separate dimensions — the distinction that FinBERT systematically misses.
2. **Causal identification:** Orthogonalize LLM scores against macro fundamentals and the actual rate decision to isolate the pure communication "surprise" (the residual ε).
3. **Spillover matrix:** Apply those shocks to a G3 framework (Fed, ECB, BoE) to test whether the Global Financial Cycle holds at the rhetoric level — not just at the rate level.

The anchor papers are:
- **IMF WP 2025** — proves LLMs outperform dictionary methods for central bank text
- **Miranda-Agrippino & Rey (2020)** — the canonical proof of the Global Financial Cycle using rate-based shocks (we replicate with words)
- **Raviv et al.** — closest methodological twin; we upgrade their NLP and scope

---

## Identification Strategy

**Stage 1 — Purge predictable sentiment:**

```
SentimentScore_i,t = α + β1·Inflation_i,t + β2·Unemployment_i,t + β3·ΔRate_i,t + β4·Yield_i,t-1 + β5·VIX_t-1 + ε_i,t
```

ε is the "communication shock" — what the central bank said beyond what the rate decision and macro data would have predicted. The t-1 bond yield and VIX outsource omitted variable concerns to the market itself.

**Stage 2 — Local Projections (Jordà 2005):**

```
ΔPrice_j,t+h = α_h + β_h·Shock_i,t + γ_h·Controls_j,t + u_t+h    for h = 0,...,20
```

The sequence of β_h coefficients forms the Impulse Response Function. Run for both domestic (i=j) and cross-border (i≠j) combinations.

---

## Data

| Type | Source | Variables | Status |
|------|--------|-----------|--------|
| Text | Fed, ECB, BoE websites | FOMC / ECB / BoE press conference transcripts (~261 docs, 2015–2025) | Converted to txt — `data/transcripts_cleaned/` |
| Equities | Yahoo Finance | S&P 500, Euro Stoxx 50, FTSE 100 (daily) | Collected — `data/controls/global_indices_daily.csv`; 1 missing value (Euro Stoxx 50) |
| Risk | Yahoo Finance | VIX (daily) | Collected — `data/controls/vix_daily.csv`; calendar alignment vs. equity file TBD |
| Rates | Yahoo Finance / FRED | 10Y US Treasury, German Bund, UK Gilt | Not yet collected |
| Macro | FRED | CPI/HICP, Unemployment (US, Eurozone, UK) | Not yet collected |

---

## Open Questions / Known Gaps

- **LLM scoring validity:** How do we validate that our Hawkishness/Uncertainty scores actually capture what we claim? Options: correlate against intraday market moves at the minute of the speech, or benchmark against FinBERT on a held-out set.
- **Causal isolation:** ε may still absorb Central Bank Information Effects (CBIE) — when a bank reveals private macro knowledge, not just tone. We acknowledge this and defend via tight event-study windows (daily returns on the day of the speech).
- **Controls sufficiency:** Too many controls → ε → 0 (no shock left). Too few → omitted variable bias. Current plan: 4–5 controls max (inflation, unemployment, rate change, t-1 yield, t-1 VIX).
- **Timing / event windows:** Fed speaks at 2PM EST; European markets are closed. Need to decide whether Euro Stoxx and FTSE reactions go in t or t+1 for cross-border regressions.
- **Scoring aggregation:** Each transcript is chunked into 3–5 paragraph blocks. Averaging block scores per meeting is the baseline; weighting by section (Q&A vs. opening statement) is an open design choice.

---

## Next Steps

1. Scrape and clean one transcript each from the Fed, ECB, and BoE to validate the pipeline end-to-end.
2. Pull 10Y yield, VIX, and equity data via `yfinance` and align to meeting dates.
3. Write and test the LLM prompt (Hawkishness 1–10, Uncertainty 1–10, Topic Focus) on a small batch; compare outputs to FinBERT as a sanity check.
4. Run Stage 1 regression on pilot data and inspect residuals.
5. Run Local Projections for one shock → one market pair and plot the first IRF.

---

## Stack

- Python (uv environment)
- `pymupdf` — PDF → text conversion
- `yfinance`, `pandas-datareader` — financial and macro data
- `anthropic` / OpenAI API — LLM scoring
- `statsmodels` / `linearmodels` — Local Projections
- `matplotlib` — IRF plots

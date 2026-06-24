# From NLP Disagreement to Spillover Analysis

**Purpose:** how to move from the current LLM stance/disagreement findings to the
spillover analysis (RQ3, RQ4) and where disagreement earns its place in the economics.
**Date:** 2026-06-21

---

## 1. Where you are now (the assets you already have)

| Asset | File / object | What it gives you |
|---|---|---|
| 6-model turn-level stance labels | `output/stance/turn_predictions_*.csv` | dovish…hawkish per turn, per LLM (3,972 turns × 6 models, 0 parse errors) |
| Per-meeting ensemble stance + dispersion | `output/stance/ensemble_stance_meeting.csv` | `mean_stance`, `score_std`, `n_turns` per (bank, meeting) — 204 bank-meetings |
| Disagreement measures (turn level) | `linear_probe_scores_turns.csv` | `split`, `label_entropy`, `score_std`, `max_ordinal_gap`, `mean_pair_d`, `disagree_risk` |
| Meeting-level disagreement | `linear_probe_meeting_risk_turns.csv` | probe risk + raw split + entropy + score_std per meeting |
| Mechanistic decomposition | swap analysis | ≈49% encoding-level vs ≈51% decision-rule at the empirically-calibrated point (each head set to its LLM's observed neutral rate; range ≈9–78% by weighting) |

**What this means:** the *measurement layer is essentially done.* You can produce, for
each bank and meeting, (a) a hawkishness level and (b) a calibrated cross-model disagreement
score. Everything below is turning those two series into spillover evidence.

---

## 2. The conceptual chain

```
LLM stance labels  →  meeting-level stance  →  communication SHOCK  →  spillover model  →  asymmetry
   (done)               (done: ensemble)        (Step 2: residual)      (Step 3: LP/VAR)    (Step 5)
                                  │
                          disagreement score
                                  │
                    enters as robustness / weight / regime  (Step 4 — your contribution)
```

The single most important conceptual point: **a stance *level* is not a shock.** Spillover
analysis needs the *unexpected* component of communication — the tone surprise orthogonal to
what was already known (macro state + the actual policy decision). Steps 2–3 are about
constructing and propagating that surprise; Step 4 is where your disagreement work becomes
economically load-bearing instead of a methods aside.

---

## 3. Step 1 — Meeting-level stance series (mostly done)

You already export `ensemble_stance_meeting.csv`. Decisions to lock:

- **Aggregation unit:** mean stance across all answer turns in a meeting (current) vs.
  weighting toward the opening-statement / prepared turns. Start with the simple mean.
- **Label source for the baseline:** use the **6-model ensemble mean** as the headline
  series (the swap result justifies averaging — perception is shared, averaging cancels
  per-model threshold bias). Keep the per-model series for the Step-4 sensitivity table.
- **Caveat to carry forward:** the corpus captures *scheduled* press conferences only.
  Emergency actions announced by press release (e.g., ECB PEPP, 18 Mar 2020; inter-meeting
  Fed cuts, Mar 2020) are **not** in the data — note this as a data limitation wherever the
  2020 window matters.

---

## 4. Step 2 — Construct the communication shock

Pick one identification (in rough order of rigor / data cost):

1. **Tone residual (recommended starting point).** Regress meeting stance on the information
   set available at the meeting — lagged inflation (CPI/HICP), growth/unemployment nowcast,
   the prior policy rate, **and the actual rate decision at that meeting**. The residual is
   the "hawkish words beyond the action" — communication surprise orthogonal to fundamentals
   and the decision itself. Cheap, defensible, uses only data you can assemble.
2. **Delta / relative stance.** `Δstance = stance_t − stance_{t-1}`. Matches the
   delta-consistent-scoring argument (Tang & Yang 2026; Jones 2025 in your notes) that stance
   is meaningful *relative across meetings*, not in absolute level. Use as a robustness variant.
3. **High-frequency identification (gold standard, data-heavy).** The asset-price move in a
   tight window around the press conference = the monetary/communication surprise
   (Gürkaynak–Sack–Swanson; Nakamura–Steinsson). Requires intraday data. Use the text-based
   shock as the *interpretable* counterpart and HFI as validation if you can get the data.

Deliverable: a per-(bank, meeting) `comm_shock` series + its dispersion (`score_std`).

---

## 5. Step 3 — Baseline spillover model (RQ3 + RQ4)

Given irregular meeting timing and a smallish sample (~70–90 meetings/bank over 2015–2026),
**local projections (Jordà)** are likely more robust than a fixed-lag VAR and trace IRFs
directly. Run VAR too as a cross-check.

- **RQ3 — CB → CB tone propagation.** Does a Fed `comm_shock` predict subsequent ECB / BoE
  tone (and vice versa)? LP of bank-j stance on bank-i shock at horizons h = 0…H, controlling
  for own lags and global macro.
- **RQ4 — CB → markets.** Project market outcomes (equity index returns/vol, sovereign yields,
  FX) on each bank's `comm_shock`. Cross-border = Fed shock → European equities, ECB shock →
  US equities, etc.

Deliverable: baseline IRFs (own-country + cross-border) using the **ensemble** shock.

---

## 6. Step 4 — Bring disagreement in (this is your contribution; answers RQ2)

Three channels, in priority order:

1. **Model-selection sensitivity table.** Re-estimate the key spillover coefficient under each
   label source and show how much it moves. This is the table that makes disagreement matter
   economically.

   | Label source | Spillover coef | Sig | Notes |
   |---|---|---|---|
   | Ensemble (6-model mean) | … | … | baseline |
   | GPT-4o only / Gemini only / Qwen only / … | … | … | per-model spread |
   | Majority vote | … | … | hard-label aggregation |
   | Excluding split meetings | … | … | drop high-`score_std` meetings |
   | Dispersion-weighted (WLS) | … | … | down-weight ambiguous meetings |

2. **Regime split (the sharper story).** Split meetings into high vs low `disagree_risk`
   (or `score_std`) terciles and estimate spillovers separately. Hypothesis: spillovers are
   **stable across models in low-disagreement meetings but diverge / change in high-disagreement
   meetings.** That reframes disagreement from limitation → finding: *LLM choice matters most
   precisely when communication is ambiguous — which is when spillovers are most consequential.*

3. **Measurement-error weighting.** Treat `score_std` as observation-level uncertainty: WLS
   with weight ∝ (1 − normalized `score_std`), or an errors-in-variables specification. The
   honest way to propagate measurement uncertainty into the VAR.

Deliverable: the sensitivity table + regime-split IRFs. This *is* RQ2.

---

## 7. Step 5 — Asymmetry (RQ4 headline)

Test whether cross-border transmission is directionally asymmetric:

- Fed → EU vs ECB → US magnitude (is US the net exporter of communication shocks?).
- Hawkish vs dovish asymmetry (do hawkish surprises spill over more than dovish?) — interact
  `comm_shock` with its sign.
- By disagreement regime (does asymmetry widen when communication is ambiguous?).

---

## 8. Pre-step quick win — validate disagreement against markets first

Before the full VAR, run the **Malta-style validation**: does meeting-level `score_std`
correlate with **realized market volatility / absolute price move** in a window around the
meeting? If you get ρ ≈ 0.3–0.5 while a simple text measure (your `dict_score`) gets ρ ≈ 0.1,
that single result establishes disagreement is *economically meaningful* and de-risks the whole
chapter. You already have the dispersion series; this just needs the market data + a correlation.

---

## 9. Data you still need

- **Market series aligned to meeting dates:** equity indices (S&P 500, EuroStoxx 50, FTSE 100),
  sovereign yields (2y/10y UST, Bund, Gilt), policy/OIS rates, FX (EURUSD, GBPUSD). Daily
  minimum; intraday if you want HFI.
- **Macro controls at meeting time:** inflation (CPI/HICP), unemployment/GDP nowcast.
- **Actual policy decisions per meeting** (rate change in bps) — needed to residualize the tone
  shock in Step 2.

---

## 10. Suggested sequencing

1. **Step 8 quick win** — dispersion ↔ realized vol correlation. (Days. Highest payoff per hour.)
2. **Step 2** — build `comm_shock` (tone residual) from stance + macro + decision.
3. **Step 3** — baseline LP/VAR IRFs on the ensemble shock (RQ3, RQ4).
4. **Step 4** — sensitivity table + regime split (RQ2). *The novel contribution.*
5. **Step 5** — asymmetry tests.

Lock 1–2 before touching the VAR; everything downstream depends on a clean shock series.

---

## 11. Open decisions to settle early

- Shock identification: tone-residual vs delta vs HFI (Step 2).
- Estimator: local projections vs VAR (start LP).
- Baseline label source: ensemble mean (recommended) vs majority vote.
- Frequency: meeting-event study vs forcing onto a regular (e.g., monthly) grid for the VAR.
- How aggressively to lean on the disagreement regime-split as the headline RQ2 result.

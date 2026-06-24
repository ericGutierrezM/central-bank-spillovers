# LLM Disagreement on Central-Bank Stance — Final Method & Findings

**Project:** Central Bank Spillovers — BSE Thesis 2025–2026
**Scope:** turn-level, 6 LLMs. This is the canonical wrap-up; supersedes the chunk-level
4-model write-ups (`multihead_analysis_summary.md`, `analysis_note.tex`) where they conflict.

---

## 1. Method

**Setup.** Six LLMs — DeepSeek V3, Gemini 2.5 Flash, GPT-4o Mini, Llama 3.3, Mistral Large,
Qwen 2.5 72B — independently classify every press-conference *turn* into a 5-point stance
(dovish → hawkish). Following the perspectivist / learning-from-disagreement tradition
(Davani 2022; Uma 2021; SemEval-2023 LeWiDi), the six are treated as **annotators with
different reaction functions**, and inter-model disagreement is the object of study.

**Apparatus — multi-head DeBERTa.** A shared `deberta-v3-base` encoder + one `Linear(768→5)`
head per LLM, trained jointly to **imitate each model's labels**. The shared `[CLS]` becomes a
stance-saturated text representation; each head is a model's decision rule. Disagreement is
studied by (a) probing the frozen CLS and (b) swapping decision rules on a fixed representation.

**Baselines.** Dictionary (hawk/dove counts) and TF-IDF logistic/ridge bound what bag-of-words
achieves — included to show what the transformer does and does *not* add.

**Robustness.** All headline numbers use a **grouped split by `doc_id`** (whole meetings held
out together) to remove within-meeting leakage. A **calibration sweep** (α = 0 / 0.5 / 1.0
class weighting in the per-head loss) plus a **faithfulness check** (each head's predicted
neutral rate vs. its LLM's empirical rate) identify **α = 0.5** as the faithful operating point;
all downstream embeddings use that encoder. The **swap** specifically is reported at a
**direct per-head calibration** — each head's neutral logit is offset so its predicted neutral
rate equals its LLM's observed rate (gaps ≈ 0 by construction) — which is cleaner than the
global α knob and resolves the residual over-neutrality that α = 0.5 leaves.

---

## 2. Best target variable

**Headline disagreement target: `score_std_3way`** — cross-model SD of the 3-way signed score
(dove = −1, neutral = 0, hawk = +1), evaluated by **Spearman rank correlation**.

Rationale:
- **Graded** — distinguishes 1 dissenter from a 3–3 split (binary `split` cannot).
- **Signed, on the VAR's own scale** — it is the dispersion of the exact quantity averaged into
  the stance shock.
- **Clean** — zero for *any* consensus, so it is genuine disagreement, not stance strength
  (the trap that makes `P(directional)` look easy to predict).
- **Sign-aware** — up-weights the rare catastrophic dove-vs-hawk turns while being dominated,
  correctly, by the common neutral-vs-stanced disagreement.

Use **Spearman, not R²**: the target is 62% zeros, so R² is pessimistic even when the ranking
is good — and ranking (which meetings are contested) is what the spillover step consumes.

- **Secondary:** binary `split` for a clean, legible AUC ("can text predict *any* disagreement").
- **Dropped from the headline:** `P(directional)` (stance intensity, not disagreement);
  `label_entropy` / `score_std_5class` (bake in 5-class granularity that is not of interest).

---

## 3. Findings (final, grouped split)

| Result | Number |
|---|---|
| Corpus structure | 59% all-neutral · **31% split** · 10% all-stanced |
| Hierarchical κ | κ_stanced ≈ 0.61, **κ_direction ≈ 0.92** — disagreement is about *whether* stanced, not *which way* |
| Sign-conflict (dove **and** hawk on same turn) | **3.5% of turns** (9.9% of split turns) — rare |
| Swap decomposition | at the **empirically-calibrated point ≈ 49% encoding / 51% decision-rule** (each head's neutral threshold set to its LLM's observed rate; n = 179 split turns); calibration-sensitive, ≈9–78% across α-weightings |
| Predicting `split` (AUC) | dict 0.58 · TF-IDF 0.74 · frozen 0.72 · **fine-tuned 0.78** |
| Embedding's biggest rank gain | **`score_std_3way`: Spearman 0.32 → 0.43 (+0.12)** — largest of all targets |
| Shared cues (gradient attribution + cue-family masking) | policy / rates / inflation drive disagreement across **all** heads |

---

## 4. The claims (and why they are not "no-duh")

1. **Same signals, different thresholds.** All six models attend to the same policy vocabulary;
   they diverge on the *threshold* for calling a turn stanced. A reaction-function difference,
   not a perceptual one.
2. **Disagreement is structured and localized.** ~90% is neutral-vs-stanced (magnitude /
   attenuation uncertainty in the stance series); ~3.5% is sign-conflict (rare, but the worst
   case for a spillover sign).
3. **The transformer earns its keep on mechanism, not prediction.** TF-IDF nearly matches it at
   *predicting* disagreement — reported honestly. The transformer is justified by the **swap**
   (architecturally impossible for bag-of-words), per-model attribution, and its largest gain
   over TF-IDF being the **rank-prediction of contextual stancedness disagreement** (+0.12
   Spearman) — exactly where compositional reading beats word counts. At the empirically-
   calibrated point, **≈ half** of cross-model disagreement survives an identical text
   representation (genuine reaction-function difference) and ≈ half dissolves under a shared
   encoding (perception difference).
4. **It matters for spillovers (RQ2).** In a 59%-neutral corpus, model choice systematically
   perturbs the stance *magnitude* (and occasionally its sign at contested meetings), so
   zero-shot LLM labels are **not interchangeable measurement instruments**.

**Framing discipline.** Not "LLMs are calibrated differently" (well known) — the specific,
measured, consequential form: localized to the neutral boundary, shared cues, downstream-
relevant. Report the swap as a **single calibrated point (≈ 49/51) with a one-line
non-identification caveat** — it is conditional on calibrating each head to its model's observed
neutral rate and not point-identified beyond that marginal. State that text predicts
disagreement *modestly*.

---

## 5. Hand-off to the spillover analysis

The artifact the VAR consumes is `output/stance/meeting_disagreement_for_var.csv`
(one row per bank-meeting), produced by the meeting-level cell in
`notebooks/multihead_turns_colab.ipynb`:

| column | meaning |
|---|---|
| `mean_stance` | 3-way mean stance — the communication-shock input |
| `disagreement` | mean `score_std_3way` — measurement-uncertainty weight |
| `disagreement_pred` | text-predicted disagreement (for periods/robustness) |
| `model_choice_spread` | SD of the 6 per-model meeting stance means — how much model choice moves the estimate |
| `sign_conflict_rate` | fraction of turns with a dove-and-hawk conflict (the rare catastrophic case) |
| `is_test` | held-out (grouped) flag |

**Closing evidence (meeting level, grouped split):**
- **Text predicts contested meetings out-of-sample: Spearman ≈ 0.64** (held-out, n = 31 test
  meetings; up from 0.43 at the turn level once turn noise averages out). Report as "≈0.6" —
  the CI is wide at n = 31. → disagreement is a property of the language, not model noise.
- **Disagreement tracks model-choice sensitivity: Spearman ≈ 0.72** between `disagreement`
  and `model_choice_spread`. → meetings the LLMs find ambiguous are exactly where the stance
  estimate feeding the VAR swings most across the choice of labeling model. *This is RQ2.*
  Caveat: the two measures share variance (both derive from the cross-model vote spread), so
  treat it as co-movement, not independent validation. **`model_choice_spread` is the cleaner
  economic object** — "how much the meeting stance input changes if you swap the labeling
  model" — and is the better headline quantity for RQ2.

One-line thesis claim: *LLM disagreement on whether a statement takes a directional stance is
text-predictable (held-out meeting ρ ≈ 0.64) and economically consequential — higher-disagreement
meetings are precisely those where the estimated stance shock swings most across the labeling
model (ρ ≈ 0.72) — so zero-shot LLM labels are not an interchangeable measurement instrument
in the spillover analysis.*

Intended uses (see `nlp_to_spillover.md` for the full pipeline):
1. **Sensitivity table** — re-estimate the key spillover coefficient under each model / majority
   vote / excluding split meetings / dispersion-weighted (WLS).
2. **Regime split** — high vs low `disagreement` meetings; show spillover IRFs are stable across
   model choice in low-disagreement periods and diverge in high-disagreement periods (RQ2).
3. **Measurement-error weight** — weight meetings by (1 − normalized `disagreement`).

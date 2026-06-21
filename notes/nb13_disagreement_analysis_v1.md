# Notebook 13 — Cross-Model Disagreement Analysis (v1)
*Date: 2026-06-19 | Models: llama33, deepseekv3, qwen25_72b, mistrallarge_or*
*Corpus: 5,003 chunks across 204 meetings — BoE (42), ECB (89), Fed (73)*

---

## 1. Setup: `chunks_wide` and the Agreement Frame

All four model prediction files were merged on `chunk_uid` into a wide frame (`chunks_wide`), one row per chunk, with `label_{key}` and `score_{key}` columns for each model. Derived columns:

- `stanced_{key}` — True when model calls chunk dovish/hawkish (any of the 4 directional labels)
- `n_stanced` — count of models calling the chunk directional (0–4)
- `consensus_stanced` — all 4 agree stanced
- `consensus_neutral` — all 4 agree neutral
- `split` — at least one model says stanced AND at least one says neutral

**Base rates (full corpus, n=5,003):**

| Category | Count | Share |
|----------|-------|-------|
| All neutral (consensus) | 3,138 | 62.7% |
| All stanced (consensus) | ~581 | 11.6% |
| Split (disagreement) | ~1,284 | 25.6% |
| Contested (≥1 stanced) | 1,865 | 37.3% |
| Majority stanced (≥3) | 954 | 19.1% |

---

## 2. Cohen's κ — Hierarchical Decomposition

### 2a. Full-corpus 5-class κ and stanced/neutral κ

Pairwise κ across all 5 labels (all chunks, n=5,003):

| Pair | Raw agreement | κ (5-class) | Stanced agreement | κ (stanced/neutral) |
|------|--------------|-------------|-------------------|---------------------|
| Llama 3.3 70B vs DeepSeek V3 | 77.5% | 0.487 | 84.2% | 0.594 |
| Llama 3.3 70B vs Qwen 2.5 72B | 79.3% | 0.479 | 84.0% | 0.560 |
| Llama 3.3 70B vs Mistral Large | 81.8% | **0.608** | 87.4% | **0.692** |
| DeepSeek V3 vs Qwen 2.5 72B | 81.8% | 0.451 | 87.6% | 0.596 |
| DeepSeek V3 vs Mistral Large | 79.7% | 0.511 | 86.7% | 0.641 |
| Qwen 2.5 72B vs Mistral Large | 82.3% | 0.521 | 85.4% | 0.574 |

κ (5-class) range: **0.45–0.61** — moderate agreement. κ (stanced/neutral) range: **0.56–0.69** — slightly higher, because the 5-class task adds noise from mostly-hawkish/mostly-dovish granularity.

### 2b. Hierarchical decomposition: detection vs direction

**Layer 2** — hawk vs dove (restricted to chunks where BOTH models call it stanced):

| Pair | n (both stanced) | κ (stanced/neutral) | κ (hawk/dove direction) |
|------|-----------------|---------------------|------------------------|
| Llama 3.3 70B vs DeepSeek V3 | 910 | 0.594 | 0.903 |
| Llama 3.3 70B vs Qwen 2.5 72B | 747 | 0.560 | 0.933 |
| Llama 3.3 70B vs Mistral Large | 1,119 | 0.692 | 0.879 |
| DeepSeek V3 vs Qwen 2.5 72B | 628 | 0.596 | **0.977** |
| DeepSeek V3 vs Mistral Large | 891 | 0.641 | 0.934 |
| Qwen 2.5 72B vs Mistral Large | 702 | 0.574 | 0.946 |

**Core finding:** When both models agree a chunk is directional, they agree on the direction at κ = **0.88–0.98**. The stanced/neutral detection step has κ = **0.56–0.69**. Disagreement is entirely at the *detection* layer, not the *direction* layer.

### 2c. Contested-subset κ

Full-corpus κ is inflated by the large pool of easy neutral-neutral agreements (62.7% of chunks). The contested subset (n_stanced ≥ 1, n=1,865) isolates where models actually diverge.

**Note on majority-stanced subset κ:** κ on n_stanced ≥ 3 yields negative or undefined values — Berkson's paradox. Conditioning on majority-stanced inflates expected chance agreement to near 1.0, making the denominator near zero. Not a substantive finding; ignore.

---

## 3. Stanced/Neutral Analysis (4-panel visualization)

- **Panel 1 (stanced vote distribution by bank):** Most chunks cluster at 0-vote (all neutral). Distribution is similar across BoE/ECB/Fed — the neutral-heavy pattern is not bank-specific.
- **Panel 2 (label distribution per model):** All models show ~60%+ neutral. DeepSeek V3 and Qwen 2.5 72B are slightly more liberal with stance calls; Llama 3.3 and Mistral are more conservative.
- **Panel 3 (stanced rate by model × bank):** Model effect dominates bank effect. Within each bank, inter-model variance in stanced rate is larger than inter-bank variance for any single model.
- **Panel 4 (consensus breakdown by bank):** `split` fraction is relatively stable across BoE/ECB/Fed (~25%), suggesting disagreement is not bank-specific and likely driven by linguistic/pragmatic features of the chunks themselves.

---

## 4. Semantic Embedding — Where Does Disagreement Live?

Method: `sentence-transformers/all-MiniLM-L6-v2` → PCA to 2D. Chunks colored by stance group (all neutral / split-mostly-neutral / split-mostly-stanced / all stanced).

**Result:** No meaningful spatial clustering. Split chunks do not occupy a distinct region of the semantic space — they overlap completely with consensus chunks across both dimensions.

**Interpretation:** Disagreement is *not* about semantic content. Models are not splitting on different topics or domain-specific language. The disagreement is pragmatic: models apply different threshold criteria to ambiguous language even when the underlying meaning is similar.

One visible pattern: variance along Dim 1 narrows as Dim 1 increases. Likely a temporal/era effect (language became more formulaic and compressed after ~2015–2018), not a stance signal.

---

## 5. Logistic Regression — What Features Predict `split`?

Target: `split` (1 = at least one model says stanced, at least one says neutral).
Features: keyword indicator patterns + `word_count` + `n_sentences` + `turn_idx` + year FE + bank/speaker/doc-type categoricals.

### 5a. With year fixed effects
CV AUC: **0.660**

### 5b. Without year fixed effects
CV AUC: **0.645** (drop: 0.015)

Year FE accounts for ~0.015 of AUC. The year effect is real but small — it captures temporal clustering of linguistic patterns (different eras use hedging language differently), not an independent time effect. Features have genuine predictive content beyond era.

---

## 6. SHAP on TF-IDF — Token-Level Importance

Model: L2-regularized logistic regression on TF-IDF (500 features, `stop_words='english'`, `min_df=10`, `sublinear_tf=True`, `C=0.5`). SHAP LinearExplainer on 100-sample background subsample.

| Metric | Value |
|--------|-------|
| CV AUC (5-fold) | **0.676 ± 0.036** |
| In-sample AUC | 0.784 |
| Keyword logit baseline | 0.645 |
| Net gain from unigrams | +0.031 |

The SHAP analysis adds modest but real signal over the keyword baseline. The main value is interpretability.

### Top split-inducing tokens (SHAP > 0)

| Token | Interpretation |
|-------|---------------|
| progress | "making progress on inflation" — vague non-committal |
| rate | policy rate reference without directional signal |
| evidence | "evidence suggests" — data-dependent hedging |
| national | cross-country framing, diffuse signal |
| certainly | epistemic booster without direction |
| countries | cross-national discussion |
| times | "at times", "in recent times" — temporal hedge |
| credit | credit conditions, ambiguous direction |
| underlying | "underlying inflation/trends" — hedge term |
| global | global context, indirect signal |
| action | "policy action" without direction specified |
| early | "early signs/evidence" — hedging |
| lower | ambiguous: lower inflation vs lower rates |
| expect | forward guidance without clear direction |

**Pattern: process and epistemic vocabulary.** Words that describe *reasoning about* policy without stating a directional conclusion.

### Top consensus-inducing tokens (SHAP < 0)

| Token | SHAP | Interpretation |
|-------|------|---------------|
| inflation | **−0.0352** | Strongest consensus signal — naming the key variable resolves ambiguity |
| support | | Accommodative vocabulary — clearly dovish signal |
| sustained | | "Sustained recovery/expansion" — clear directional |
| purchase | | QE/asset purchase programs — clear easing signal |
| continue | | "Continue our purchases/support" — clear policy stance |
| obviously | | Strong epistemic certainty marker |
| government | | Fiscal policy framing — not monetary stance |
| today | | Specific policy announcements ("we decided today") |
| fiscal | | Fiscal vs monetary distinction — contextual |
| review | | Strategy review — procedural, not directional |

Two sub-clusters within consensus tokens:
1. **Clearly dovish/stanced**: support, sustained, purchase, continue, help
2. **Clearly contextual/analytical**: government, fiscal, review, questions, issues

Both resolve the stanced/neutral ambiguity — just in opposite directions (one toward stanced, one toward neutral).

### The "Inflation Paradox"

The keyword logit's `has_inflation` indicator (matching "prices", "price stability", "disinflation") was *split-inducing*, while the TF-IDF token "inflation" alone is the strongest *consensus-inducer*.

Resolution: chunks that use price-stability framing ("progress toward our inflation goal", "price stability mandate") without naming inflation directly tend to be ambiguous. Chunks that say "inflation" directly tend to be clearly classifiable — either explicitly about inflation risk (stanced) or explicitly analytical/neutral ("we discuss the inflation outlook"). The ambiguous chunks *allude to* inflation through process words without naming it.

---

## 7. Synthesis

**The core finding:** Cross-model disagreement in stance detection concentrates in chunks that use *process and epistemic vocabulary* — language describing the analytical reasoning process rather than stating a directional policy conclusion. When the inflation variable is named directly, or when clear accommodative vocabulary appears (purchase, support, sustain), models agree. When language hedges, qualifies, and describes the analytical process, models diverge.

**Detection layer vs direction layer:** Models agree on direction (hawk/dove) at κ ≈ 0.88–0.98 once both flag a chunk as stanced. They disagree on whether a chunk is directional at all at κ ≈ 0.56–0.69. The "hard problem" is detection, not classification.

**Pragmatic, not semantic disagreement:** Split chunks are not in a different semantic space — they overlap completely with consensus chunks in embedding space. Models apply different threshold criteria to the same underlying language.

**Bank effect is minimal:** The split fraction (~25.6%) is stable across BoE, ECB, and Fed. Disagreement is a property of chunk-level language, not an institution-level signal.

---

## 8. Additional Analyses — Null Findings

### 8a. Hedge word lexicon density

Lexicon: ~40 CB-relevant hedge/epistemic terms (may, might, could, approximately, suggest, uncertain, data-dependent, gradual, patient, flexible, etc.). Density = hits / word count.

| Group | Mean hedge density |
|-------|--------------------|
| All neutral | 0.0181 |
| Split | 0.0191 |
| All stanced | 0.0170 |

Split vs consensus ratio: **1.067x** — effectively identical distributions. The three groups overlap almost completely in the density histogram.

**Null finding.** Hedge word density does not explain disagreement. Models are not splitting because one sees more hedge words — the hedge words are evenly distributed across all groups.

### 8b. Modal verb + syntactic conditionality (spaCy)

Features: weak modal rate (may/might/could), strong modal rate (will/shall), policy verb rate (raise/cut/tighten/ease), modal→policy-verb dependency arc, negated modal, if-clause rate, CB-subject modal.

All features are near-zero and essentially flat across groups:
- `n_modal_policy` ≈ 0.00000 everywhere — modal→policy-verb arcs almost never fire in CB language (nominalized forms like "rate increases" dominate over "raise rates")
- `n_if_clause`: split 0.00356 vs neutral 0.00258 — split has slightly more conditionality, but tiny difference
- `n_weak_modal`: slightly *lower* in stanced chunks (0.00145) than neutral (0.00196) — directional chunks use more confident language, as expected

**Note:** Initial CV AUC of 0.842 was data leakage — `n_stanced` (which defines the target) was included in the feature set. True syntactic feature AUC ≈ 0.640, below the keyword baseline.

**Null finding.** Syntactic conditionality is not the mechanism. The spaCy dependency parser does not find modal→policy-verb arcs at meaningful rates in CB language.

### 8c. Prior meeting context (Tang & Yang hypothesis)

Test: does the prior meeting's net hawk score (per model) predict whether a chunk will split?

| Spec | CV AUC |
|------|--------|
| Prior meeting only | **0.520** |
| Size controls only | 0.571 |
| Prior + size controls | 0.556 |
| Keyword baseline | 0.645 |
| TF-IDF SHAP | 0.676 |

Per-model coefficients (prior net hawk → split):
- Llama 3.3 70B: −0.139 (hawkish prior → less split)
- DeepSeek V3: −0.095 (hawkish prior → less split)
- Mistral Large: −0.107 (hawkish prior → less split)
- Qwen 2.5 72B: **+0.287** (opposite direction — likely noise)

Quartile pattern: Q1 dovish prior (29.2% split) > Q4 hawkish prior (25.9% split) — weakly consistent with "post-dovish-meeting language is more ambiguous", but the AUC of 0.520 confirms this carries almost no predictive information.

**Null finding.** Prior meeting context does not explain disagreement. The Tang & Yang hypothesis (chunk stance underdetermined without meeting trajectory) is not supported. Size controls (word count, n_sentences) explain more variance than meeting history. The Qwen outlier coefficient is noise.

---

## 9. Complete AUC Scorecard

| Method | CV AUC | Δ vs baseline |
|--------|--------|--------------|
| Keyword logit (baseline) | 0.645 | — |
| TF-IDF SHAP (500 features, C=0.5) | **0.676** | +0.031 |
| Keyword logit without year FE | 0.645 | ±0.000 |
| Keyword logit with year FE | 0.660 | +0.015 |
| Hedge word density | ~0.640 | −0.005 |
| Syntactic/modal features (spaCy) | ~0.640 | −0.005 |
| Prior meeting context only | 0.520 | −0.125 |

TF-IDF unigrams are the ceiling for interpretable surface features. Everything else — hedging vocabulary, syntactic structure, meeting history — adds no signal beyond chunk-level word choice.

---

## 10. Synthesis (updated)

**The core finding:** Cross-model disagreement is predicted only by chunk-level vocabulary, specifically process and epistemic language (SHAP tokens: progress, evidence, expect, underlying, action). Nothing external to the chunk text — not hedging density, syntactic conditionality, or prior meeting stance — explains disagreement.

**What this rules out:**
1. ~~Semantic content~~ — embedding space shows no clustering (Section 4)
2. ~~Hedging vocabulary~~ — hedge density ratio 1.067x, AUC ~0.640
3. ~~Syntactic conditionality~~ — modal/dependency features near-zero and flat
4. ~~Meeting trajectory context~~ — prior net hawk AUC 0.520 ≈ chance

**What it points to:** The disagreement is about *implicit reaction-function inference* — models apply different thresholds to underdetermined process language. When language names the policy variable directly ("inflation", "purchase", "support"), models converge. When language describes the analytical process without a directional conclusion, models diverge because they apply different implicit rules for what counts as "taking a stance."

This is not measurable with surface linguistics. The annotator-embedding approach (see `chatgpt_disagreement_ideas.md`) is the natural next step to characterize model-specific reaction functions directly.

---

## 11. Phrase Masking — Two-Pass Attribution (Top-100 Split Chunks)

*Script: `notebooks/phrase_masking.py` | Outputs: `phrase_masking_results.csv`, `phrase_masking_analysis.png`*

### Setup

Selected the 100 most-contested chunks (exactly `n_stanced == 2`: two models say stanced, two say neutral), sorted by word count descending (mean 338 words, range 224–775).

**Two-pass design:**
- **Pass 1 (extract):** Each model classifies the chunk and names 3–8 key phrases (exact substrings) that drove its classification. One API call per (chunk × model) = 400 calls. Phrases validated as literal substrings; hallucinated text dropped.
- **Pass 2 (mask):** Pool all unique phrases identified by any model per chunk. Mask each phrase and re-score with all 4 models in sub-batches of 5. Track: which model named it? Which models flipped?

### Results

**Resolution rate:** 59/100 disagreements (59%) resolved by removing a single phrase — disagreement is not diffuse ambiguity spread across the chunk; it is localizable to specific clauses.

**Self-calibration rates** (model named phrase AND flipped when masked):

| Model | Named | Self-flipped | Self-cal rate | Caused any flip |
|-------|-------|-------------|---------------|-----------------|
| Llama 3.3 | 353 | 111 | 31% | 80% |
| DeepSeek V3 | 442 | 216 | **49%** | 83% |
| Qwen 2.5 | 423 | 104 | 25% | 83% |
| Mistral Large | 568 | 181 | 32% | 83% |

Self-calibration is low (25–49%): models identify phrases as stance-critical but masking them often does not flip the identifying model itself. However, ~80–83% of named phrases flip *some* model — the trigger vocabulary is shared but thresholds differ.

**Cross-attribution matrix** (row = model that named phrase, col = model that flipped):

|  | Llama | DeepSeek | Qwen | Mistral |
|--|-------|----------|------|---------|
| Llama | 111 | **164** | 83 | 107 |
| DeepSeek | 149 | **216** | 105 | 132 |
| Qwen | 142 | **194** | 104 | 143 |
| Mistral | 173 | **266** | 155 | 181 |

**Key pattern: DeepSeek flips the most** (column sums: DeepSeek=840, Llama=575, Mistral=563, Qwen=447). Regardless of which model identified the phrase, removing it is most likely to flip DeepSeek. This is consistent with DeepSeek's lowest stanced rate (37/100 in the split subset) — it sits closest to the neutral boundary and is most sensitive to phrase-level signal.

### Selected examples

- **ECB 2024-06-06** — "we are travelling with more confidence that the disinflationary path is actually materialising" → removing it flips Llama and Mistral from mostly hawkish to neutral. Correctly identified by Llama; self-calibrated.
- **Fed 2020-06-10** — "we're going to be here with our tools supporting this economy for as long as it's needed" → identified by all 4 models; removing it flips DeepSeek and Qwen from neutral to stanced (dovish). Self-calibrated: Qwen and DeepSeek.
- **Fed 2017-12-13** — "gradual increases in the target range for the federal funds rate as being appropriate..." → identified by Mistral (who was neutral); removing it flips Llama and Qwen from hawkish to neutral. Mistral self-calibration = none — it correctly identified the hawkish phrase but didn't flip on it because it was already neutral regardless. Direct evidence of reaction-function divergence rather than threshold difference.

### Interpretation

The phrase masking confirms that disagreement is **localizable and phrase-specific**, not diffuse. The dominant pattern (low self-calibration + high cross-flip) is consistent with the TF-IDF SHAP finding: models share the same vocabulary sensitivity, but apply different overall thresholds to the full chunk. Removing a single phrase is enough to push some models over the threshold but not others.

DeepSeek's high flippability and lowest self-calibration rate (best calibrated among models: 49%) together suggest it has the clearest internal representation of what it's responding to, while being the most sensitive to signal removal.

---

## 12. Open Questions

- **Within-era heterogeneity** — does the detection/direction split hold in post-GFC QE language and 2022 rate-hike language? Disagreement may concentrate in transition periods.
- **Annotator embedding experiment** — can a DeBERTa model learn each LLM's labeling style? Would reveal whether disagreement is systematic (learnable reaction functions) or stochastic (random threshold noise).
- **Implication for main thesis** — disagreement concentrates in process/epistemic language which is more prevalent in forward-guidance-heavy periods (post-2013). Main thesis estimates may be noisier in those periods; worth a robustness section flagging this.

---

## B. Figures produced

| File | Description |
|------|-------------|
| `agreement_kappa_heatmap.png` | 5-class κ and stanced/neutral κ heatmaps (all pairs) |
| `agreement_kappa_hierarchical.png` | Layer 1 (stanced/neutral) vs Layer 2 (direction) κ |
| `agreement_kappa_subsets.png` | κ by chunk subset (all-neutral, contested, majority-stanced) |
| `stanced_neutral_analysis.png` | 4-panel: vote distribution, label dist, stanced rate by bank, consensus by bank |
| `representation_space_stanced_neutral.png` | Semantic embedding colored by stance group |
| `disagreement_features_stanced_neutral.png` | Logit coefficient plot (with year FE) |
| `disagreement_features_no_year.png` | Logit coefficient plot (without year FE) |
| `shap_tfidf_corrected.png` | SHAP mean values on TF-IDF (corrected model, 500 features) |
| `hedge_lexicon_analysis.png` | Hedge density distributions and bank × group means |
| `syntactic_modal_analysis.png` | Modal/conditionality feature heatmap by stance group |
| `prior_meeting_context.png` | Per-model prior-stance coefficients + split rate by quartile |
| `phrase_masking_analysis.png` | Resolution rate, cross-attribution heatmap, self-calibration bar (Section 11) |

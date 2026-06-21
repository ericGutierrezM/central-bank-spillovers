# Method Framing — LLM Disagreement Analysis
**Date:** 2026-06-20  
**Purpose:** Reference note for framing the disagreement analysis section of the thesis. Covers the progression from simple to complex methods, related literature, and connection to the spillover paper.

---

## The Core Question

Four LLMs disagree on whether central bank speech chunks are stanced (hawkish/dovish) vs. neutral. The analysis asks: is this because of how they *read* the text, or how they *decide* from the same reading?

---

## Method Progression: Simple → Complex

The analysis builds from cheap to expensive, each step justified by what the previous one couldn't answer.

### Step 1 — TF-IDF + SHAP (baseline, cheapest)

Train a logistic regression on TF-IDF features to predict disagreement (split chunk vs. consensus). Apply SHAP to get word-level importance scores.

**What it gives:**
- Which words statistically predict inter-LLM disagreement
- Fast, interpretable, no GPU needed
- Good baseline AUC to compare against

**What it can't give:**
- Cannot separate *which model* is driving importance — SHAP is over the aggregate disagreement label, not per-model
- Context-insensitive: "accommodation" gets the same weight everywhere regardless of surrounding sentence
- Cannot distinguish encoding differences from decision-rule differences

**Status:** Already run (`output/stance/shap_tfidf_corrected.png`, `shap_tfidf_split.png`). Compare top words against gradient attribution results.

### Step 2 — Multi-Head DeBERTa (mechanistic, expensive)

Fine-tune `microsoft/deberta-v3-base` with one `Linear(768→5)` head per LLM. All heads share the same encoder, trained jointly on all four labeling tasks simultaneously.

**What it adds over TF-IDF:**
- **Per-model token importance** via gradient attribution (∂logit/∂embedding, L2-normed) — can compare which tokens each model specifically weights
- **Context-sensitive importance** — the same word gets different attribution scores depending on the surrounding passage
- **The swap analysis** — run the encoder once, give all four heads the identical CLS vector, measure whether they still disagree. This is architecturally impossible with TF-IDF. Result: 60.8% of disagreements resolve → majority of zero-shot disagreement is encoding-level, not decision-rule.
- **Head weight geometry** — cosine similarity between the 5×768 weight matrices reveals structural similarity between models' learned projections (Llama↔Mistral most similar at 0.556, reproducing empirical κ structure)

**Key results:**
- Gradient attribution: shared core vocabulary (accommodation, transmitted, hikes) across all heads; Llama/DeepSeek additionally weight entity tokens (Draghi, ECB) while Qwen/Mistral stay purely lexical
- Swap analysis: 61% encoding-level, 39% genuine decision-rule disagreement
- F1 pattern: Qwen/DeepSeek lower F1 (0.39–0.42), higher accuracy → conservative, default to neutral; Llama/Mistral higher F1 (0.52–0.53) → more willing to commit to directional label

### Step 3 — Linear Probe (bridge to economics)

Train logistic regression on DeBERTa's 768-dim CLS vectors (after fine-tuning) to predict disagreement. Apply to all chunks in corpus to produce a continuous disagreement risk score over time.

**What it adds:**
- AUC=0.79 out-of-sample — disagreement is linearly decodable from the text representation before any LLM assigns a label
- Produces a meeting-level risk timeline showing *when* model choice most affects the spillover estimates
- Fed peaks: mid-2020 (COVID), 2021–2024 (tightening cycle). ECB: 2020–2022, late 2023. BoE: lowest and most stable.

**If TF-IDF SHAP gives similar top words as gradient attribution:** that strengthens the argument — the finding is robust to method, and the transformer explains the mechanism rather than just rediscovering the vocabulary.

**If TF-IDF probe AUC << 0.79:** that quantifies exactly what the contextual representation adds over bag-of-words for predicting disagreement.

---

## Why Not Just Use Dictionaries?

The dictionary critique: "you could count hawk/dove words and get the same result."

Three reasons it doesn't hold:

1. **Entity-sensitivity cannot emerge from dictionaries.** "Draghi" and "ECB" don't appear in any hawk-dove lexicon. Llama/DeepSeek are partially classifying on speaker identity — a finding that only appears through per-model gradient attribution.

2. **The CoT analysis already ruled out vocabulary.** Models list the same hawkish signals (Jaccard 0.656) and still disagree. Shared vocabulary → same dictionary score → same label. But they don't agree. The weighting/threshold function is doing something dictionaries can't capture.

3. **The swap analysis has no dictionary equivalent.** You cannot hold a TF-IDF encoding "constant" across models. The 61/39 decomposition is only possible with a shared neural encoder — it is the structurally novel result of the whole analysis.

---

## Related Literature

### This paper is the closest external validation
**[Synthetic traders paper, ECB press conferences]** — 30 LLM-based synthetic traders with different risk preferences read ECB transcripts and forecast OIS rates. Their inter-trader disagreement measure (std dev of forecasts) achieves Spearman ρ ≈ 0.5 with realized market volatility. Simple text measures (word counts, readability, uncertainty frequency) only achieve ρ ≈ 0.1–0.2.

**Connection to this thesis:**
- Directly validates that inter-LLM disagreement is economically meaningful, not just a measurement artefact
- The 5× gap between LLM disagreement and simple text measures is the empirical answer to the dictionary critique
- Their "disagreement among traders" is functionally the same construct as the split rate used here — aggregated inter-model variance
- Their finding that few-shot historical context improves calibration is consistent with the prior meeting context null result here (raw context doesn't help, but structured prompting does)
- **Positioning:** cite as external validation that inter-LLM disagreement predicts market outcomes; position the multi-head analysis as the mechanistic explanation of what in the text drives that disagreement

### Per-Annotator Modeling
- **Davani et al. (2022), TACL** — per-annotator heads on shared BERT backbone, architecturally identical to setup here. Shows disagreement reflects genuine perspectival differences, not noise. Majority-vote aggregation discards real information.
- **Uma et al. (2021), JAIR** — survey of learning-from-disagreement approaches. Multi-head design falls in their "per-annotator" category.
- **Gordon et al. (2022), CHI** — "Jury Learning": per-demographic-group models, aggregating to one model loses group-specific signal. LLM identity plays the role of demographic group here.

### Multi-Task Learning
- **Liu et al. (2019), MT-DNN, ACL** — BERT with per-task linear heads trained jointly on multiple tasks. Justification for the shared encoder architecture: joint training regularises the representation toward features that satisfy all labeling functions, rather than overfitting to one model's distribution.

### LLMs as Annotators
- **Gilardi et al. (2023), PNAS** and **Alizadeh et al. (2023), Political Analysis** — LLMs achieve high agreement with expert human annotators on political text. Establishes baseline credibility of LLM labels. Neither addresses inter-LLM disagreement, which is what this thesis studies.

### Monetary Policy Text
- **Loughran & McDonald (2011), JF** — domain-specific lexicons for financial text. The dictionary baseline.
- **Tobback et al. (2017)** and hawk-dove classification literature — the stance-scoring framework this project extends to LLM annotation. Multi-head finding (same signals, different thresholds) maps to the theoretical claim that reaction functions differ across analysts reading the same CB text.

---

## Thesis Framing

The section should be framed as: *we don't just measure that LLMs disagree — we explain why, where, and when it matters for the spillover estimates.*

| Method | Contribution |
|---|---|
| TF-IDF SHAP | Baseline vocabulary of disagreement-predictive words |
| Null results (hedging, syntax, context) | Rules out surface-level explanations |
| Phrase masking + CoT | Disagreement is localizable; models list same signals but weight differently |
| Multi-head DeBERTa | Mechanistic decomposition: 61% encoding, 39% decision-rule; per-model attribution; head geometry |
| Linear probe | Disagreement is textually predictable (AUC=0.79); risk timeline maps uncertainty onto history |
| Synthetic traders paper | External validation: inter-LLM disagreement predicts realized market volatility |

The progression from TF-IDF to transformer is justified at each step by what the previous method couldn't answer. The transformer isn't overcomplicated — it's the minimum complexity needed to do the swap analysis, which is the only way to decompose encoding from decision-rule disagreement.

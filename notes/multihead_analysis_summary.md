11# LLM Disagreement Analysis — Summary of Findings

**Project:** Central Bank Spillovers — BSE Thesis 2025–2026  
**Question:** What drives disagreement between LLMs when classifying central bank monetary policy stance?

---

## 1. The Problem

Four LLMs (Llama 3.3, DeepSeek V3, Qwen 2.5 72B, Mistral Large) were used to classify ~5,000 central bank speech chunks into a five-point stance scale (dovish → hawkish). Pairwise inter-rater agreement is moderate (κ ≈ 0.55–0.65 across all chunk pairs) but with a striking asymmetry: models agree almost perfectly on *direction* once they commit to a directional label (κ_direction ≈ 0.88–0.98), but disagree substantially on *whether a chunk is stanced at all* (κ_stanced ≈ 0.56–0.69). The disagreement is not random noise — it is systematic and reproducible across runs. The analysis below was designed to determine its source.

---

## 2. Ruling Out Surface-Level Explanations

Five hypotheses were tested and rejected before identifying the true mechanism.

**Semantic content.** If disagreement chunks were semantically ambiguous (closer to the centroid of all chunks), disagreement would be driven by genuine signal poverty. Embedding cosine similarity between disagreeing and agreeing chunks was indistinguishable (AUC ≈ 0.50). Disagreement is not about ambiguous content.

**Hedging density.** Disagreement chunks contain slightly more hedging language (ratio 1.067×), but the effect is not significant and the overlap in distributions is near-total. Hedging is not a reliable predictor of disagreement.

**Syntactic conditionality.** Modal verbs and conditional policy arcs (e.g., "we *would* raise rates *if*...") were hypothesised to confuse models by making the stance contingent. Syntactic analysis showed modal density and conditional arc counts were near-zero across both agreeing and disagreeing chunks.

**Prior meeting context.** Models may disagree on chunks that reverse a prior meeting's direction (e.g., a dovish statement at a hawkish meeting). Meeting-level context features yielded AUC ≈ 0.520 — no better than chance.

**Order/noise.** Chunk presentation order and random variation were ruled out by confirmed reproducibility across independent scoring runs and by κ values that remain stable when re-run.

---

## 3. Disagreement Is Localizable — Phrase Masking

Having ruled out document-level and structural explanations, the analysis moved to the token level. A two-pass phrase masking experiment was run on 100 high-disagreement chunks:

- **Pass 1:** each model identified 3–8 key phrases (exact substrings) that drove its classification.
- **Pass 2:** each identified phrase was masked and all four models re-scored the modified chunk.

**Result:** 59 of 100 disagreements resolved when a single phrase was masked, confirming that disagreement is localizable to specific spans rather than distributed across the whole chunk.

Self-calibration rates (the probability that the model which named a phrase actually flipped when that phrase was removed) varied substantially:

| Model | Self-calibration |
|-------|-----------------|
| DeepSeek V3 | 49% |
| Mistral Large | 32% |
| Llama 3.3 | 31% |
| Qwen 2.5 72B | 25% |

Cross-attribution analysis showed DeepSeek is the most sensitive to phrase removal overall (highest column sum in the 4×4 cross-attribution matrix), consistent with its higher label instability in subsequent CoT analysis.

---

## 4. Same Signals, Different Weights — Chain-of-Thought Extraction

To understand *why* certain phrases drove disagreement, the 50 most polarized chunks (sorted by |score_llama − score_deepseek|) were re-scored using a structured CoT prompt that forced models to enumerate hawkish signals, dovish signals, and their weighing rationale before labelling.

**Signal overlap (Jaccard, word-level):**

| Signal type | Jaccard overlap |
|-------------|----------------|
| Hawkish signals | ≈ 0.656 |
| Dovish signals | ≈ 0.396 |

Models identify largely the same hawkish signals but diverge more on what counts as a dovish signal. Crucially, correlation between disagreement magnitude (|delta|) and Jaccard overlap is near zero — high disagreement does not co-occur with low signal overlap. Models are listing the same phrases and still disagreeing on the label.

**Label stability:** CoT labels matched zero-shot labels for Llama 58% of the time and only 20% of the time for DeepSeek. DeepSeek's zero-shot labels appear to be sensitive to presentation order and framing in ways that other models are not.

**Conclusion from CoT:** Disagreement is not about which signals are perceived. It is about how those signals are *weighted* when mapping to a label — i.e., the reaction function, not the signal set.

---

## 5. Mechanistic Confirmation — Multi-Head DeBERTa

To move from behavioural description to mechanistic explanation, a multi-head classification model was trained:

- **Shared encoder:** `microsoft/deberta-v3-base` (86M parameters), trained jointly on all four labeling tasks.
- **Per-model heads:** four independent `Linear(768 → 5)` layers, one per LLM, applied to the same `[CLS]` representation.
- **Training:** 3 epochs, freeze/unfreeze schedule, summed cross-entropy loss across all heads.

**Test set performance:**

| Model | Accuracy | Macro-F1 |
|-------|----------|----------|
| Llama 3.3 | 76.0% | 0.519 |
| DeepSeek V3 | 83.2% | 0.387 |
| Qwen 2.5 72B | 87.6% | 0.422 |
| Mistral Large | 79.9% | 0.533 |

The accuracy–F1 gap (especially for DeepSeek and Qwen) reflects heavy neutral-class prediction — both models label conservatively, achieving high accuracy by defaulting to neutral on borderline chunks.

### 5a. Gradient Attribution — What Tokens Each Head Responds To

Per-head gradient attribution (`∂logit/∂embedding`, L2-normed per token, averaged over 194 test-set split chunks) identified the following top-5 tokens per head:

| Rank | Llama 3.3 | DeepSeek V3 | Qwen 2.5 72B | Mistral Large |
|------|-----------|-------------|--------------|---------------|
| 1 | accommodation | accommodation | transmitted | transmitted |
| 2 | transmitted | accommodative | accommodative | accommodative |
| 3 | **draghi** | transmitted | accommodation | accommodation |
| 4 | accommodative | **draghi** | **hikes** | **hikes** |
| 5 | **ecb** | **ecb** | **tightening** | ecb |

The shared core (`accommodation`, `accommodative`, `transmitted`) appears in all four heads — direct confirmation that the encoder has learned a universal monetary policy signal representation and all models perceive the same tokens as salient. This is consistent with the Jaccard hawkish overlap of 0.656 from the CoT analysis.

The divergence is in *additional* tokens:
- **Llama and DeepSeek** additionally weight proper nouns: `draghi`, `ecb`. These heads are partially classifying on *speaker/institution identity*, not just policy language.
- **Qwen and Mistral** additionally weight explicit directional vocabulary: `hikes`, `tightening`. These heads are more purely lexical-stance driven.

This explains a systematic disagreement pattern: a chunk from a Draghi speech using neutral language would be pulled toward non-neutral by Llama/DeepSeek (speaker cue) but left near neutral by Qwen/Mistral (no explicit stance word).

### 5b. Head Weight Analysis — The Linear Projection

Each head is a single `Linear(768 → 5)` layer. Its weight matrix (5 × 768, flattened to 3840 dimensions) encodes the complete learned mapping from encoder representation to stance label. Cosine similarity between all pairs of head weight matrices:

| Pair | Cosine similarity |
|------|------------------|
| Llama 3.3 ↔ Mistral Large | **0.556** |
| Qwen 2.5 72B ↔ Mistral Large | 0.520 |
| DeepSeek V3 ↔ Qwen 2.5 72B | 0.491 |
| DeepSeek V3 ↔ Mistral Large | 0.497 |
| Llama 3.3 ↔ DeepSeek V3 | 0.486 |
| Llama 3.3 ↔ Qwen 2.5 72B | 0.485 |

Three observations:

1. **All pairs are moderate and similar in range (0.485–0.556).** No two heads learned the same mapping; no two are orthogonal. Each model has a distinct but not radically different linear projection.

2. **Llama ↔ Mistral is the most similar pair (0.556).** This reproduces the empirical finding from the inter-rater κ analysis — Llama and Mistral agree most often in the original zero-shot scoring. The head weights are recovering the same structure without being given any information about pairwise agreement.

3. **PCA of head weight vectors** (PC1: 37% var, PC2: 33% var) reveals three structural clusters:
   - **Llama + Mistral** sit close together (right of PCA space), confirming their similar labeling functions.
   - **Qwen** is isolated far left — the most structurally distinct head, consistent with it being the most neutral-leaning and having the lowest self-calibration rate in phrase masking.
   - **DeepSeek** is isolated upward, occupying a different structural position from all three others, consistent with its label instability in CoT and its outlier self-calibration rate.

---

## 6. Unified Interpretation

The full chain of evidence supports a single mechanistic account:

> **All four LLMs perceive the same signals in central bank text. Disagreement arises because each model applies a different linear projection from signal representation to stance label — a learned reaction function, not a perceptual difference.**

Specifically:

- The shared DeBERTa encoder converges on the same salient tokens (`accommodation`, `transmitted`, `hikes`, `tightening`) regardless of which head is making predictions. Signal perception is shared.
- Each head's weight matrix defines a distinct linear map from the 768-dimensional CLS representation to the 5-point stance scale. This is the model's *reaction function* — given the same internal representation of a chunk, different heads produce different stance outputs because they have learned different thresholds and linear weightings.
- The structural similarity between head weight matrices (Llama ↔ Mistral highest; Qwen most distant) predicts empirical inter-rater agreement independently. The weights encode something real about the labeling functions, not just task-specific noise.
- The entity-sensitivity of Llama and DeepSeek (responding to `draghi`, `ecb`) introduces a systematic source of disagreement with Qwen and Mistral that is not reducible to signal vocabulary — it is a feature of what the reaction function was trained to respond to.

The analogy to monetary policy is direct: all four models have read the same economic data (the text), but they apply different Taylor rules to it. The disagreement is in the rule, not the data.

---

## 6. Swap Analysis — Encoding vs. Projection Disagreement

The swap analysis provides the final decomposition. For each split chunk in the test set, the encoder runs once and all four heads see the identical CLS representation. If the heads disagree here, the disagreement is purely in the linear projection; if they agree, the zero-shot disagreement must have originated from model-specific encoding differences.

**Head consensus on split chunks (194 total):**

| Unique predictions | Chunks |
|-------------------|--------|
| 1 (all agree) | 118 (60.8%) |
| 2 | 71 (36.6%) |
| 3 | 4 |
| 4 (all differ) | 1 |

**60.8% of zero-shot disagreement chunks receive unanimous agreement from all four heads on a shared encoder.** This is the most important number from the swap analysis. It means that the majority of observed zero-shot disagreement is attributable to model-specific encoding (different tokenizers, pretraining corpora, architectures) rather than to differences in the linear reaction function alone. When the encoding is held constant, the disagreement largely dissolves.

The remaining 39.2% (76 chunks) are genuine reaction-function disagreements — cases where identical CLS representations produce different label predictions.

**Pairwise disagreement rates (same CLS representation):**

| Pair | Disagreement rate |
|------|------------------|
| Llama 3.3 ↔ Mistral Large | **10.8%** |
| DeepSeek V3 ↔ Qwen 2.5 72B | 19.1% |
| Qwen 2.5 72B ↔ Mistral Large | 23.2% |
| Llama 3.3 ↔ DeepSeek V3 | 28.4% |
| Llama 3.3 ↔ Qwen 2.5 72B | 29.4% |
| DeepSeek V3 ↔ Mistral Large | **32.0%** |

Llama ↔ Mistral (10.8%) is by far the lowest pairwise rate, consistent with their head weight cosine similarity being the highest (0.556) and their empirical inter-rater κ being the strongest. DeepSeek ↔ Mistral (32.0%) is the highest despite DeepSeek and Llama sharing gradient attribution patterns — suggesting DeepSeek's structural isolation in PCA reflects a genuinely distinct calibration that disagrees most with Mistral's more lexically-grounded head.

**P(neutral) per head on split chunks (same CLS representation):**

| Model | Mean P(neutral) |
|-------|----------------|
| Qwen 2.5 72B | 0.72 |
| DeepSeek V3 | 0.65 |
| Mistral Large | 0.50 |
| Llama 3.3 | 0.45 |

The ordering exactly reproduces the zero-shot scoring behavior: Llama is the most willing to commit to a directional label, Qwen the most conservative. The heads have learned each model's calibration bias — not just its signal vocabulary, but its *threshold* for calling a chunk stanced at all.

---

## 7. Implications for the Thesis

1. **LLM labels are not interchangeable proxies for "true" stance.** Each model's label reflects its specific learned projection, which differs systematically from other models' projections in recoverable, structured ways.

2. **Ensemble scoring is appropriate.** The shared encoder result justifies averaging or ensembling across models: the signal is perceived consistently, and averaging linear projections reduces model-specific threshold bias.

3. **Entity-sensitivity is a confound.** If Llama/DeepSeek partially classify on speaker identity (Draghi, ECB), then cross-bank comparisons using those models alone may reflect institutional identity rather than rhetorical stance. Qwen/Mistral, being more purely lexical, may be preferable for cross-bank analysis.

4. **Disaggregated results should flag DeepSeek.** Its structural isolation in PCA, low CoT stability (20%), and outlier self-calibration (49% but also the most volatile) suggest its labels carry more noise than the other three.

---

## 8. Linear Probe — Connecting to Downstream Spillover Analysis

### Motivation

The multi-head model decomposes disagreement into two sources: encoding differences (61%) and decision-rule/threshold differences (39%). But neither number directly answers the question RQ2 asks: *where* in the historical corpus does model choice most affect the estimated communication shocks and thus the spillover results?

A **linear probe** bridges that gap. Train a logistic regression on the frozen DeBERTa CLS vectors to predict binary disagreement (split chunk vs. consensus). If the probe works, disagreement is linearly encoded in the shared representation — it is a property of the text itself, predictable before any LLM scores it. Apply the probe to every chunk in the corpus to produce a continuous **disagreement risk score** over time.

### What it gives you

- **A timeline of model sensitivity**: peaks in the risk score mark periods where LLM choice most affects the estimated stance series and therefore the downstream VAR impulse responses.
- **An economics story**: those peaks will cluster around GFC, the 2013 taper tantrum, the 2022 tightening cycle — periods of genuine CB communication ambiguity. The finding becomes: LLM choice matters most precisely when monetary policy is hardest to read, which is when spillover analysis is most interesting.
- **A robustness diagnostic**: before presenting IRFs, overlay the disagreement risk score on the historical timeline. Results robust across models during low-risk periods are clean findings. Results that diverge during high-risk periods are flagged as sensitive — and the sensitivity is traceable to specific meetings, not to random noise.

### Reframing for the paper

This reframes the disagreement analysis from a limitation ("models disagree") to a contribution ("we can characterise the ambiguity structure of CB communication and show where measurement uncertainty is highest"). The probe provides a model-agnostic measure of communicative ambiguity grounded in the geometry of language model representations, not in any single model's judgement.

### Implementation

Cells added to `notebooks/multihead_stance_colab.ipynb` (after the save cell):
1. Extract CLS vectors for all chunks from the trained encoder
2. Train `LogisticRegression(class_weight='balanced')` on training split; evaluate AUC-ROC on test split
3. Score all chunks, aggregate to meeting level, plot risk timeline per bank
4. Save `linear_probe_scores.csv`, `linear_probe_meeting_risk.csv`, `linear_probe_risk_timeline.png`

AUC > 0.5 confirms disagreement is linearly decodable from the shared representation. The meeting-level risk scores can be merged directly with the VAR dataset for the spillover analysis.

---

## 9. Related Literature

### Per-Annotator Modeling and Learning from Disagreement

The closest methodological precedent is **Davani et al. (2022), "Dealing with Disagreements: Looking Beyond the Majority Vote in Subjective Annotations," *Transactions of the Association for Computational Linguistics* (TACL)**. They train per-annotator heads on a shared BERT backbone — architecturally identical to the setup here — and show that inter-annotator disagreement reflects genuine perspectival differences rather than annotation error. Their principal argument (that majority-vote aggregation discards real information encoded in the disagreement distribution) maps directly onto this project: each LLM head captures a distinct but internally coherent labeling perspective, and averaging across models loses the structure.

**Uma et al. (2021), "Learning from Disagreement: A Survey," *Journal of Artificial Intelligence Research (JAIR)*** is the standard survey of this area. They taxonomise approaches to annotator disagreement into aggregation (majority vote, Dawid-Skene), soft-label, and per-annotator modelling, and argue the field has systematically underused the last. The multi-head design here falls squarely in their "per-annotator" category.

**Fornaciari et al. (2021), "Beyond Black & White: Leveraging Annotator Disagreement via Soft-Label Multi-Task Learning," *ACL 2021*** uses soft label distributions derived from annotator disagreement as targets in a multi-task framework, showing the disagreement distribution itself is a training signal. This is complementary to the hard-label per-head setup here: both treat disagreement as informative rather than as noise to be resolved. *(Verify author list before citing.)*

**Gordon et al. (2022), "Jury Learning: Integrating Dissenting Voices into Machine Learning Models," *CHI 2022*** trains per-demographic-group models and shows that aggregating to a single model loses group-specific signal. The parallel here is that "LLM identity" plays the role of demographic group — each model's labeling function is a coherent perspective worth preserving.

### Multi-Task Learning with Shared Encoders

The architectural choice — shared transformer backbone with per-task linear output heads trained jointly — follows directly from **Liu et al. (2019), "Multi-Task Deep Neural Networks for Natural Language Understanding" (MT-DNN), *ACL 2019***. MT-DNN is BERT with per-task output layers fine-tuned on multiple GLUE tasks simultaneously, and demonstrates that joint training of the shared encoder improves representation quality over single-task fine-tuning. The justification for the architecture used here is the same: shared encoder signal regularises the representation toward features that satisfy all labeling functions simultaneously, rather than overfitting to one model's idiosyncratic distribution.

### Gradient-Based Attribution

The token importance method — computing `∂logit/∂embedding`, L2-normed per token — is vanilla input-gradient saliency, introduced by **Simonyan et al. (2014), "Deep Inside Convolutional Networks: Visualising Image Classification Models and Saliency Maps," *ICLR 2014 Workshop***. For a more principled attribution that satisfies the completeness axiom (attributions sum to the output), **Sundararajan et al. (2017), "Axiomatic Attribution for Deep Networks" (Integrated Gradients), *ICML 2017*** is preferred but requires a baseline input. The implementation here uses plain gradient saliency, which is appropriate for comparing *relative* importance across heads on the same chunks rather than for absolute attribution claims.

**Bastings & Filippova (2020), "The Elephant in the Interpretability Room: Why Use Attention as Explanation When We Have Saliency Methods?" *BlackboxNLP @ EMNLP 2020*** directly argues for gradient saliency over attention weights as an explanation mechanism in NLP, which supports the methodological choice here.

### LLMs as Annotators

The broader question of whether LLM labels are reliable proxies for human annotation is addressed by **Gilardi et al. (2023), "ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks," *PNAS 2023*** and **Alizadeh et al. (2023), "Open-Source Large Language Models Outperform Crowd Workers and Approach ChatGPT in Text-Annotation Tasks," *Political Analysis 2024***. Both find high agreement between LLMs and expert human annotators on political text classification — the same domain as central bank stance. However, neither paper addresses *inter-LLM* disagreement, which is the phenomenon studied here. The present analysis is complementary: given that individual LLMs approximate expert annotation, what does it mean when they disagree with each other?

### Monetary Policy Communication

The framing of each LLM's reaction function as a "Taylor rule" over the text draws on the tradition of quantifying central bank communication tone. **Loughran & McDonald (2011), "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks," *Journal of Finance 2011*** established domain-specific lexicons for financial text. **Tobback et al. (2017)** and subsequent work on hawk-dove classification of central bank text provides the stance-scoring framework this project extends to LLM-based annotation. The multi-head model's finding — that models perceive the same monetary policy signals but apply different thresholds — corresponds to the theoretical claim that reaction functions differ across central banks and across analysts reading the same text.

---

## 10. Linear Probe Results and Final Interpretation

### Results

- **AUC-ROC: 0.790** on held-out test set
- Split recall: 0.727 (matches consensus recall — expected behaviour of `class_weight='balanced'`)
- Split precision: 0.481 (many false positives, expected given class imbalance: 194 split vs. 556 consensus in test set)

### What the probe shows

The CLS vector from the fine-tuned DeBERTa encoder linearly predicts whether the four LLMs will disagree on a chunk, with AUC=0.790. This confirms that **disagreement is a property of the text's meaning, not of model noise**: the semantic features the encoder learned to represent stance are sufficient to separate disagreement chunks from consensus chunks with a single matrix multiplication.

One important nuance: the CLS vector is not purely linguistic — it was shaped by fine-tuning on all four LLM label sets. A frozen pretrained DeBERTa would likely produce a lower AUC. The more precise claim is that **the features relevant to stance prediction are also the features that drive disagreement** — ambiguity is encoded in the same representational space as stance itself.

### Timeline findings

Applying the probe to all chunks and aggregating to meeting level reveals:

- **Fed** has the highest and most sustained disagreement risk. Spike to ~0.68 in mid-2020 (COVID emergency policy); elevated plateau through 2021–2024 (tightening cycle, "higher for longer" uncertainty).
- **ECB** is intermediate. Elevated risk around 2020–2022 (pandemic response, divergence from Fed timing), with a late spike around 2023–2024 (end of tightening cycle).
- **BoE** is lowest and most stable, consistent with a more formulaic communication style.

Peaks correspond to historically interpretable moments of genuine policy ambiguity, not to random variation.

### How this closes the argument

The full chain of evidence is now:

| Finding | What it establishes |
|---|---|
| Swap analysis (61% encoding-level) | Disagreement is not purely a threshold/decision-rule difference |
| Null results (hedging, syntax, prior context) | It is not surface-level linguistic noise |
| Gradient attribution (shared signal vocabulary) | Models perceive the same monetary policy signals |
| Head weight cosine similarity (0.49–0.56) | Decision rules are related but distinct linear projections |
| Linear probe (AUC=0.79) | Disagreement is predictable from meaning — it is structured, not random |
| Timeline peaks at 2020, 2022 | It clusters at moments of genuine policy ambiguity |

The interpretation for the paper: *models share the same perceptual space and attend to the same signals, but apply different decision rules. The passages that trigger disagreement are semantically identifiable — they are the passages where monetary policy communication is genuinely ambiguous. The probe maps this ambiguity onto the historical timeline, showing exactly where LLM choice most distorts the estimated communication shocks that enter the spillover VAR.*

This reframes the measurement uncertainty from a limitation to a finding: we can characterise when and why model choice matters, and the answer aligns with the periods where the spillover question is most consequential.

---

*Note: citations marked "(Verify author list before citing)" should be confirmed against Google Scholar before inclusion in the thesis bibliography.*

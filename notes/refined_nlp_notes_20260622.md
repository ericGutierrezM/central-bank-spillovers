# Refined NLP Notes
**Date:** 2026-06-22  
**Purpose:** Narrow, thesis-relevant NLP extensions for the LLM disagreement chapter. Distills which ideas are genuinely additive versus likely to sprawl or duplicate existing analyses.

---

## Bottom Line

The disagreement chapter is already methodologically rich. The goal is **not** to add more machinery for its own sake, but to sharpen the core claim:

> LLM disagreement on central-bank stance is structured, predictable, and sensitive to specific policy cues, especially around the neutral-vs-directional boundary.

The highest-value additions are:

1. **Grouped split robustness by transcript / `doc_id`**
2. **Phrase-level cue ablation**
3. **Soft-label / entropy modeling**

These are the additions most likely to improve the thesis without turning the chapter into a methods zoo.

---

## Priority Ranking

### 1. Grouped split robustness

This is the cleanest immediate robustness check. The turn-level notebook currently uses a random split by `turn_uid`, which risks leakage if multiple turns from the same Q\&A transcript appear in both train and test.

**Recommendation:** split by `doc_id` so all answers from the same Q\&A stay together.

**Why it matters:**
- removes within-meeting overlap leakage
- makes the disagreement-prediction claims much more credible
- gives a defensible answer if challenged on generalisation

**Interpretation rule:**
- if grouped performance falls but remains strong, that is a *good* result
- it means some predictive power was meeting-specific, but the main disagreement signal survives

This should now be treated as a standard robustness result, not a side note.

---

### 2. Phrase-level cue ablation

This is the strongest substantive NLP addition.

Instead of only saying that words like `inflation`, `rates`, `policy`, `restrictive`, `growth`, or `uncertainty` are associated with disagreement, test whether removing those cue families changes:

- directional classification rates
- neutral probability
- disagreement entropy / split rate
- which model-heads are most sensitive

**Preferred design:**
- define cue families manually or from top TF-IDF / gradient-attribution terms
- mask at the **phrase level**, not isolated single tokens
- run ablations on:
  - the multi-head DeBERTa heads
  - optionally a small sample of original LLMs if cost is manageable

**Why this is strong:**
- more intuitive than representation geometry
- closer to a causal intervention on the text
- produces concrete results such as:
  - `inflation/rates` masking lowers directional calls
  - some heads remain conservative even after strong cue removal
  - disagreement is concentrated in specific cue families

**Best use in thesis:** one main figure plus one compact table.

---

### 3. Soft-label / entropy modeling

This is the best conceptual refinement.

The current binary `split` target is useful, but it collapses different disagreement structures into one bucket. A turn with a `5-1` neutral/stanced split is not the same as a turn with a `3-3` hawkish/dovish split.

The notebook already computes:

- `label_entropy`
- `score_std`
- `mean_pair_d`
- `max_ordinal_gap`

So the natural next step is to frame disagreement more explicitly as a **distribution**, not only a binary event.

**Possible extensions:**
- train DeBERTa to predict the empirical 5-class label distribution
- predict `label_entropy` or `score_std` directly as the main disagreement target
- use the continuous disagreement score as a `model-selection risk` measure

**Why this matters:**
- aligns better with disagreement-aware NLP
- avoids over-reliance on majority-vote logic
- maps more naturally into the economics side:
  - exclude high-disagreement turns
  - downweight high-disagreement turns
  - interact disagreement with stance in spillover analyses

**Best framing:** not “new fancy model,” but “more faithful measurement of uncertainty.”

---

## Secondary Ideas

### Counterfactual cue edits

This is promising, but harder to do well than masking.

**Strengths:**
- very intuitive
- keeps text grammatical and economically meaningful
- could produce an excellent explanatory figure

**Risks:**
- easy to change too much text at once
- hard to defend automatically generated edits as valid counterfactuals

**Recommendation:** only do this if kept small and hand-curated, e.g. 20--40 examples with one phrase changed each time.

This is best treated as a qualitative supplement, not the core method.

### Ensemble disagreement score

This is useful, but mostly a **framing refinement**, not a whole new method.

The project already has most of this in substance through:

- `label_entropy`
- `score_std`
- `mean_pair_d`
- linear-probe disagreement risk

So this should be used as a clean way to talk about `model-selection risk`, rather than as an entirely separate contribution.

---

## Lower-Priority Ideas

### Open-model probing

Low priority unless there is a very specific question that only probing can answer.

Inspecting hidden states, layerwise probes, or CKA/RSA similarity could easily sprawl and invite methodological objections. Probes are useful diagnostics, but weak causal evidence.

**If anything is done here, keep it minimal:**
- logprob margin
- label entropy
- uncertainty on split vs consensus cases

Do **not** make representation probing the headline.

### Dataset cartography

Interesting, but probably not the best marginal addition for this thesis.

It helps identify easy / ambiguous / hard turns, but that is more indirect than the current central claim about inter-LLM disagreement and downstream measurement consequences.

This is better suited for an appendix or exploratory notebook than the main argument.

---

## Recommended Package

If only a few additions are made, the best package is:

1. **Grouped split by `doc_id`**
2. **Phrase-level cue ablation**
3. **Continuous disagreement framing**
   - `entropy`
   - `score_std`
   - optional soft-label DeBERTa

That combination produces a much stronger and cleaner thesis story:

> Disagreement is not random noise. It is concentrated around neutral-vs-directional boundary cases, remains predictable under leakage-safe transcript splits, and shifts when specific monetary-policy cue families are removed or weakened. Therefore zero-shot LLM choice affects the measurement of central-bank stance in a structured, economically relevant way.

---

## What To Avoid

Avoid adding methods that do not clearly change the substantive claim.

In particular:

- do not add probing just because it seems technically impressive
- do not make the chapter about embeddings for their own sake
- do not add too many disconnected diagnostics

The chapter should move **away** from:

> “LLMs disagree and their embeddings differ.”

and toward:

> “LLM disagreement is structured, measurable, cue-sensitive, and consequential for stance measurement.”

---

## Current Working View

The multi-head setup should remain in the project, but with disciplined framing:

- keep it as a **mechanistic, calibration-sensitive diagnostic**
- do not let it become the sole headline
- use grouped split robustness plus cue-sensitive interventions to make the overall argument more convincing

The strongest next substantive step is still **cue ablation**.

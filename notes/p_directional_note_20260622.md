# P(Directional) Note
**Date:** 2026-06-22  
**Purpose:** Record the rationale for treating `P(directional)` as the main NLP disagreement object, while preserving the bridge back to the hawkishness score used in the spillover analysis.

---

## Bottom Line

The recent grouped-split experiments suggest that the most stable and informative disagreement target is not full hawk-vs-dove placement, but **directional propensity**:

> `P(directional)` = the share of models that interpret a turn as taking any monetary-policy stance at all, rather than remaining neutral.

This now looks like the cleanest scalar object for the disagreement chapter.

---

## Why P(directional) Matters

The core empirical pattern across the project is that disagreement is concentrated at the **neutral-vs-directional boundary**, not mainly in the distinction between hawkish and dovish conditional on both models already seeing a stance.

That means the most important measurement question is:

> Does the panel interpret this text as taking a stance at all?

rather than:

> Exactly where on the hawk-dove scale does each model place it?

This does **not** mean hawkishness is unimportant. It means that for the disagreement chapter, the central uncertainty object is whether a directional reading emerges in the first place.

---

## Main Results Supporting This Choice

### 1. P(directional) is highly predictable

Grouped split, fine-tuned CLS embeddings:

- `P(directional)`: `R^2 = 0.520`, `Spearman = 0.710`
- Binary `split`: `AUC = 0.784`
- `score_std`: `R^2 = 0.252`, `Spearman = 0.574`
- `entropy3`: `R^2 = 0.088`, `Spearman = 0.438`

This indicates that the most learnable component of disagreement is the panel's directional propensity, not diffuse label entropy.

### 2. Fine-tuned contextual embeddings beat TF-IDF much more clearly on P(directional)

Grouped split, same target:

- `TF-IDF -> P(directional)`: `R^2 = 0.386`, `Spearman = 0.648`
- `Fine-tuned DeBERTa -> P(directional)`: `R^2 = 0.520`, `Spearman = 0.710`

Lift:

- `+0.135` in `R^2`
- `+0.061` in `Spearman`

This is a stronger contextual-model advantage than in the earlier binary `split` comparison. It suggests that bag-of-words can detect disagreement events, but fine-tuned contextual representations are better at modeling the underlying neutral-vs-directional propensity of the model panel.

### 3. In the 3-way soft-label setup, neutrality is the strongest component

Grouped split, fine-tuned DeBERTa:

- `P(dovish)`: `R^2 = 0.332`, `Spearman = 0.494`
- `P(neutral)`: `R^2 = 0.533`, `Spearman = 0.705`
- `P(hawkish)`: `R^2 = 0.451`, `Spearman = 0.487`

This reinforces the same point: the most learnable and stable component of the distribution is the **neutral mass**.

### 4. Cue-family ablation strongly supports the directional-boundary story

Masking cue families in the text and re-scoring predicted `P(directional)` shows:

- `rates_policy` has the largest negative effect
- `inflation` is the second-largest negative effect
- `growth_activity`, `labour_wages`, and `uncertainty_risk` are much smaller
- `guidance_conditionality` slightly increases directionality when removed

This implies that directional propensity is driven primarily by explicit monetary-policy cues, especially rate-policy and inflation language.

---

## How To Frame This

The disagreement chapter should now be centered on:

1. `split` as the simplest binary disagreement diagnostic
2. `P(directional)` as the main soft target
3. `score_std` as a secondary robustness measure

The full hawk-dove scale should remain present, but not as the main uncertainty object.

A good thesis sentence is:

> The central object of interest is directional propensity: the share of language models that interpret a statement as taking any monetary-policy stance at all.

---

## Important Qualification: We Still Need the Hawkishness Score

Even if `P(directional)` is the best object for the disagreement chapter, the economics chapter still requires a **stance level** or **hawkishness score** to construct the communication shock series used in spillover analysis.

So the project now has two related but distinct objects:

### 1. Directional propensity

This is the uncertainty / disagreement object:

- how likely the panel is to read a turn as non-neutral
- where model choice matters most
- where measurement is fragile

This belongs in the NLP disagreement chapter.

### 2. Hawkishness score

This is the substantive policy-position object:

- the sign and level of communication stance
- the ingredient used to build the shock series
- the input to spillover / VAR estimation

This belongs in the economics / measurement construction chapter.

---

## The Bridge Back to Hawkishness

The relationship between these two objects should be framed explicitly:

> `P(directional)` does not replace the hawkishness score. It identifies where the hawkishness score is most sensitive to model choice.

That bridge is the key.

The logic is:

1. The thesis still constructs a hawkishness series from model labels or scores.
2. But that series is more fragile when `P(directional)` is low or intermediate, because the panel is uncertain whether the text is stanced at all.
3. Therefore `P(directional)` can be used as a **measurement-risk indicator** for the hawkishness score.

This creates several clean downstream uses:

- report model-specific hawkishness series alongside ensemble series
- flag meetings with high disagreement / low directional certainty
- downweight or exclude turns with especially low directional consensus
- interact hawkishness with disagreement risk in spillover analysis
- show that some estimated shocks are robust and others depend strongly on label source

---

## Recommended Positioning

The cleanest positioning is:

> The disagreement chapter explains **when stance exists as a measurable object**. The spillover chapter then studies the consequences of the stance score once it is constructed.

Put differently:

- `P(directional)` tells us whether the panel thinks the text crosses the stance threshold at all
- the hawkishness score tells us the sign and intensity of the stance once that threshold is crossed

This keeps both parts of the thesis coherent:

- disagreement / uncertainty on one side
- substantive stance measurement on the other

---

## Working Decision

Current working choice:

- headline `P(directional)` as the main disagreement target
- keep `split` as a binary companion
- keep `score_std` as secondary robustness
- keep hawkishness as the substantive series for downstream spillover work

This is not a retreat from the original project. It is a refinement:

> the disagreement chapter is really about the emergence of directionality, while the spillover chapter remains about the level and sign of hawkishness once directionality is measured.

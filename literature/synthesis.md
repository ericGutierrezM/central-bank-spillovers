# Literature Synthesis

Three papers in this folder. Two are direct methodological inputs; one is an identification analogy.

---

## 1. Loughran & McDonald (2011) — *When Is a Liability Not a Liability?*
**Role: The "why not dictionaries" foundation**

L&M show that ~74% of words flagged as "negative" by the Harvard General Inquirer dictionary are not negative in financial contexts — words like *tax*, *liability*, *capital*, *board*. They build a finance-specific word list (Fin-Neg) that actually predicts 10-K filing returns, trading volume, and earnings surprises, where the Harvard list produces noise.

**Connection to our thesis:** This is the pre-LLM baseline we are implicitly arguing against. If generic word lists misclassify financial language in corporate filings, they do so even more severely in central bank transcripts, where words like "tightening," "crisis," or "aggressive" carry precise policy meaning. L&M motivate the need for domain-aware NLP — which in 2011 meant custom dictionaries, and in 2025 means LLMs. Cite this in the Literature Review as the canonical proof that domain-generic text analysis fails in finance, setting up the transition to FinBERT and then to our approach.

---

## 2. Silva, Moriya & Veyrune (IMF WP/25/109, 2025) — *From Text to Quantified Insights*
**Role: The LLM proof-of-concept and direct methodological anchor**

The IMF paper builds a sentence-level classification framework across 74,882 documents from 169 central banks (1884–2025), using a fine-tuned multilingual sentence transformer. Key findings:

- Forward-looking sentiment predicts future policy rate changes and market-based interest rates (especially longer-term OIS contracts); backward-looking sentiment does not.
- Hawkish messages tend to be short and direct; dovish messages are more verbose — an asymmetry in how central banks communicate tightening vs. easing.
- During crises, central banks shift to conditional, hedged language (their "straightforwardness index" drops sharply), and confidence-building rhetoric rises in communications to financial markets.
- They expand the standard hawkish/dovish/neutral trichotomy with two new categories: *risk-highlighting* and *confidence-building*, showing that collapsing these into "negative/positive" creates misclassification (a parallel to L&M's critique, but for central bank text specifically).
- They classify at the sentence level, not the document level, providing finer granularity than prior work.

**Connection to our thesis:** This paper is our strongest methodological ally. It proves that LLMs can extract structured, economically meaningful signals from central bank text at scale — validating the core premise of our pipeline. Key differences that keep us original:

- The IMF paper builds an index; we use an index to run causal inference via Local Projections. Their output is descriptive; ours is econometric.
- They use a fine-tuned sentence transformer (encoder-only); we use generative LLM prompt engineering to extract *Hawkishness* and *Uncertainty* as separate numeric scores — simpler to implement, directly interpretable, and more suited to a 6-week thesis.
- They do not test cross-border spillovers or the Global Financial Cycle. We do.

Cite heavily in Section III (Data and LLM Pipeline) as validation that LLM-based central bank scoring is methodologically sound.

---

## 3. Couttenier, Hatte, Laugerette & Sonno (CEP/LSE DP 2094, 2025) — *Dear Brothers and Sisters: Pope's Speeches and Conflict in Africa*
**Role: Identification analogy — causal effect of a leader's words**

This paper estimates the causal effect of the Catholic Pope's peace-seeking speeches on conflict incidence in Africa (1997–2022). Using an event-study design with ACLED conflict data, they find papal speeches reduce overall conflict by 23% on average, but with large heterogeneity by Pope (John Paul II: −89.5%, Francis: −21%, Benedict XVI: +85% in battles after his 2006 Regensburg speech). They identify the mechanism through Catholic community density, bishop alignment with the Pope, and political leader birthplace regions — showing the effect is transmitted through institutional and social networks, not just rhetoric in a vacuum. They also use LLM prompt classification (via OpenAI API) to label religious conflict events.

**Connection to our thesis:** The conceptual parallel is exact — a global leader's words, measured as an event, causally affect outcomes in other countries, with heterogeneous effects depending on the "receiver." Replace Pope → Federal Reserve, replace conflict → equity market volatility, replace Africa → Europe/UK. The Pope paper's core insight — that the identity and credibility of the sender shapes how far the message travels — maps directly onto our Global Financial Cycle hypothesis (Fed > ECB > BoE in terms of cross-border reach). Methodologically, their event-study logic is the same intuition behind our Local Projections: isolate the event, measure the response window, control for pre-trends. Cite in Section II (Literature Review) to anchor the broader claim that rhetoric causally moves outcomes across borders, independent of physical or institutional mechanisms.

---

## How the Three Papers Build Our Argument

```
L&M (2011)          →  Dictionaries fail for financial text; domain-specific NLP needed
IMF WP (2025)       →  LLMs succeed for central bank text; forward-looking sentiment predicts rates
Pope (2025)         →  Leader speeches causally move outcomes across borders; identity of sender matters
Our thesis          →  LLM scores + Local Projections to test whether Fed rhetoric causes G3 equity spillovers
```

The gap none of these papers fills: **cross-border causal identification of central bank rhetoric shocks using high-frequency equity data and a unified G3 spillover matrix.** That is our contribution.

---

## Open Questions This Literature Raises

- **Scoring granularity:** The IMF paper classifies at the sentence level; we aggregate to the meeting level. We need to decide whether averaging sentence scores or using document-level prompting is more appropriate for our Local Projections setup.
- **Forward vs. backward looking:** The IMF finding that *forward-looking* sentiment is what predicts market rates suggests our LLM prompt should explicitly ask the model to focus on forward guidance language, not just overall tone.
- **Sender credibility:** The Pope paper shows that *who* delivers the message matters as much as *what* is said (Benedict XVI vs. Francis). Analogously, individual Fed chair effects (Bernanke vs. Powell vs. Yellen) could be a robustness check or a mechanism worth flagging.
- **Transmission channel:** The Pope paper identifies specific intermediary channels (bishops, political leaders). We don't need to do this, but it motivates the question of *how* Fed rhetoric reaches European markets — direct contagion, dollar-invoicing, or through portfolio reallocation.

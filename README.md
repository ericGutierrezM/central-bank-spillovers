# Lost in Interpretation: Does It Matter Which Language Model Reads Central Banks?

**Authors:** Daniel Campos, Samuel Fraley, and Eric Gutiérrez (Barcelona School of Economics)

## Overview
This repository contains the data and code for the paper *"Lost in Interpretation: Does It Matter Which Language Model Reads Central Banks?"* We investigate how the choice of Large Language Model (LLM) impacts downstream empirical inference in macroeconomics. By using six state-of-the-art LLMs to classify sentiment in central bank press conferences (Federal Reserve, ECB, Bank of England), we generate orthogonalized communication shocks and estimate international market spillovers via Local Projections. 

We find that while LLMs highly agree on the *direction* of a policy shift, they fundamentally disagree on the threshold for departing from a neutral baseline. This algorithmic variance propagates through the causal pipeline, shifting final Impulse Response Function (IRF) point estimates by up to 24% and demonstrating that model-selection uncertainty is a critical, yet previously ignored, variable in text-based causal inference.

## Models Evaluated
* DeepSeek-V3
* Gemini-2.5 Flash
* GPT-4o Mini
* Llama 3.3 70B
* Mistral Large
* Qwen-2.5 72B

## Key Findings
1. **Hierarchical Disagreement:** Models exhibit near-perfect agreement ($\kappa = 0.918$) on hawkish vs. dovish directionality, but only moderate agreement ($\kappa = 0.616$) on whether a turn is stanced vs. neutral.
2. **Shock Correlation:** Orthogonalized communication shocks remain highly correlated across models (e.g., $r = 0.897$ for the Fed).
3. **Spillover Sensitivity:** Despite highly correlated shocks, downstream spillover estimates vary significantly depending on the selected LLM, highlighting severe model-selection uncertainty in empirical pipelines.
4. **Predicting Cross-Model Disagreement:** Text alone is a predictor of cross-model disagreement.

## Repository Structure
* `/data/`: Raw and processed transcripts for the Fed, ECB, and BoE.
* `/notebooks/`: Helper Jupyter notebooks.
* `/src/`: Python scripts for the text pipeline and the identification strategy.
* `/output/`: 
  * `/aggregated/`: Sentiment predictions at the document-level.
  * `/stance/`: Turn-by-turn sentiment predictions and agreement metrics.
  * `/residuals/`: Orthogonalized communication shocks for each bank-model pair.
  * `/spillovers/`: Spillover and IRF estimates.
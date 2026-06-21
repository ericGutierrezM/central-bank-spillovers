# ChatGPT Disagreement Analysis Ideas
*Captured: 2026-06-19 | Source: ChatGPT suggestion + own synthesis*

---

## Core Reframe: LLMs as Annotators

Treat each LLM (llama33, deepseekv3, qwen25_72b, mistrallarge_or) as a **human annotator with a policy-reaction-function bias**. This slots directly into the perspectivist NLP literature — instead of asking "which label is correct?", ask "what makes annotators disagree?"

Target variables:
- `split` (binary: at least one disagrees)
- `label_entropy` (continuous: entropy over 5-class label distribution, more expressive)
- `max_ordinal_gap` (max gap on dovish→hawkish ordinal scale)

```python
from scipy.stats import entropy

label_order = ['dovish', 'mostly dovish', 'neutral', 'mostly hawkish', 'hawkish']
label_to_ord = {l: i for i, l in enumerate(label_order)}

def label_entropy_norm(row):
    labels = [row[f'label_{k}'] for k in loaded]
    counts = [labels.count(l) for l in label_order]
    return entropy(counts, base=5)  # normalized to [0,1]

def max_ordinal_gap(row):
    ords = [label_to_ord[row[f'label_{k}']] for k in loaded]
    return max(ords) - min(ords)

chunks_wide['label_entropy']   = chunks_wide.apply(label_entropy_norm, axis=1)
chunks_wide['max_ordinal_gap'] = chunks_wide.apply(max_ordinal_gap, axis=1)
```

---

## Literature

### Core annotator disagreement papers
1. **Davani et al. (2022)** — *Dealing with Disagreements: Looking Beyond the Majority Vote in Subjective Annotations*
   - Multi-annotator architectures; model individual annotator labels rather than collapsing to majority
   - Direct analog: replace human annotators with LLMs

2. **Fleisig, Abebe & Klein (2023)** — *When the Majority is Wrong: Modeling Annotator Disagreement for Subjective Tasks*
   - 22% gain predicting individual annotator ratings, 33% for predicting variance
   - Maps to: predict `label_entropy` instead of majority label

3. **Xu, Theune & Braun (2024)** — *Leveraging Annotator Disagreement for Text Classification*
   - Compares soft-label, ensemble, instruction-tuning strategies
   - Soft-label (train on distribution not argmax) is cleanest for our setup

4. **Deng et al. (2023)** — *You Are What You Annotate: Towards Better Models through Annotator Representations*
   - Annotator + annotation embeddings → model disagreement directly
   - Maps to: `[MODEL_ID embedding] + paragraph → predicted label`

### CB-specific papers
5. **Shah, Paturi & Chava (2023)** — *Trillion Dollar Words*
   - FOMC hawkish/dovish dataset, RoBERTa-large benchmark
   - Use for: baseline task, why dictionary methods fail

6. **Cook, Kazinnik, Hansen & McAdam (2023)** — *Evaluating Local Language Models: Bank Earnings Calls*
   - FOMC hawkish/dovish exercise, exact 5-class prompts in appendix
   - Very close to our setup — good for prompt comparison

7. **Tang & Yang (2026)** — *Mind the Shift: Decoding Monetary Policy Stance from FOMC Statements*
   - Delta-Consistent Scoring: stance is relative across meetings, not absolute per chunk
   - Explains some split: chunk underdetermined without prior meeting context
   - 71.1% sentence-level accuracy

8. **Jones (2025)** — *Ornithologist: Towards Trustworthy "Reasoning" about Central Bank Communications*
   - Stance requires reaction-function inference, not semantic similarity
   - Key example: "Inflation has declined substantially" = neutral / + "but risks remain" = hawkish / + "giving room to ease" = dovish
   - Same semantic space, different policy inference → explains our embedding null result

9. **Gorbett & Jana (2026)** — *Cross-Model Disagreement as a Label-Free Correctness Signal*
   - ⚠️ **VERIFY BEFORE CITING** — possibly hallucinated by ChatGPT (no venue, perfectly on-topic, current year)

---

## Method A: Simple — Fine-tune RoBERTa/DeBERTa to Predict Disagreement

Target: binary `split` or continuous `label_entropy`

```python
# Pseudo-code sketch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "microsoft/deberta-v3-base"
tokenizer  = AutoTokenizer.from_pretrained(model_name)

# Dataset: (text, label_entropy) pairs
# Fine-tune with MSELoss for regression on entropy
# or BCELoss for binary split

# After training: use SHAP / integrated gradients on token importance
# → which tokens push a chunk toward high disagreement?
```

**Pros:** Straightforward, good baseline, interpretable via SHAP.
**Cons:** Black box without attention inspection; may overfit on 5,003 chunks.

---

## Method B: Multi-Head Model (one head per LLM)

Architecture: shared encoder → separate classification head per model

```
paragraph → [shared DeBERTa encoder] → head_llama33       → label
                                     → head_deepseekv3    → label
                                     → head_qwen25_72b    → label
                                     → head_mistrallarge  → label
```

**What this reveals:** Feature attribution per head shows *which* textual features drive *each* model's specific labeling style. If llama33's head weights inflation-adjacent tokens differently than deepseekv3's head, you have direct evidence of model-specific reaction functions.

```python
import torch
import torch.nn as nn
from transformers import AutoModel

class MultiHeadStanceModel(nn.Module):
    def __init__(self, encoder_name, model_keys, n_classes=5):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(encoder_name)
        hidden = self.encoder.config.hidden_size
        self.heads = nn.ModuleDict({
            key: nn.Linear(hidden, n_classes) for key in model_keys
        })

    def forward(self, input_ids, attention_mask, model_key):
        enc = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls = enc.last_hidden_state[:, 0, :]   # [CLS] token
        return self.heads[model_key](cls)

# Training loop:
# For each batch, pick a random model_key, compute CE loss against that model's label
# Alternatively: sum losses across all heads simultaneously

model = MultiHeadStanceModel('microsoft/deberta-v3-base', loaded)

# Loss: sum of cross-entropy over all 4 heads
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

def train_step(batch_texts, batch_labels_dict):
    inputs = tokenizer(batch_texts, return_tensors='pt', padding=True, truncation=True, max_length=256)
    total_loss = 0
    for key in loaded:
        logits = model(inputs['input_ids'], inputs['attention_mask'], key)
        loss   = nn.CrossEntropyLoss()(logits, batch_labels_dict[key])
        total_loss += loss
    return total_loss
```

**Inspection after training:**
- Compare CLS embeddings split by model head
- Use SHAP or attention rollout on each head separately
- Check: do heads cluster around different reaction-function features?

**Data requirement:** 5,003 chunks × 4 labels — borderline for fine-tuning DeBERTa. Use `deberta-v3-base` (86M params), not large. Freeze encoder for first 2 epochs.

---

## Method C: Annotator Embedding (Model ID as Learned Embedding)

Architecture: `[MODEL_ID embedding] + paragraph CLS → predicted label`

```python
class AnnotatorEmbeddingModel(nn.Module):
    def __init__(self, encoder_name, model_keys, n_classes=5, annotator_dim=64):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(encoder_name)
        hidden = self.encoder.config.hidden_size
        self.annotator_emb = nn.Embedding(len(model_keys), annotator_dim)
        self.model_key_to_idx = {k: i for i, k in enumerate(model_keys)}
        self.classifier = nn.Sequential(
            nn.Linear(hidden + annotator_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, n_classes),
        )

    def forward(self, input_ids, attention_mask, model_key):
        enc    = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls    = enc.last_hidden_state[:, 0, :]
        idx    = torch.tensor(self.model_key_to_idx[model_key])
        a_emb  = self.annotator_emb(idx).unsqueeze(0).expand(cls.size(0), -1)
        return self.classifier(torch.cat([cls, a_emb], dim=-1))
```

**Training:** Treat each (paragraph, model_key) pair as a training example. 5,003 chunks × 4 models = 20,012 training examples — much more data-efficient than the multi-head approach.

**What this reveals:** After training, inspect the learned annotator embeddings:
```python
emb_matrix = model.annotator_emb.weight.detach().numpy()  # (4, 64)
# Project to 2D with PCA — do models cluster by architecture family?
# llama33 & deepseekv3 close together? Qwen & Mistral different cluster?
```

Also: for a held-out chunk, swap the annotator embedding across all 4 models and observe how the predicted label distribution shifts — this tells you which model is most sensitive to which input features.

---

## Features to Test for Disagreement Prediction

(From ChatGPT + our analysis)

| Feature | Why it predicts disagreement | Status |
|---------|------------------------------|--------|
| Hedge density | Lexicon-based hedging rate | ✅ Tested — near-null (ratio 1.067x) |
| TF-IDF tokens | Unigram bag-of-words | ✅ Tested — CV AUC 0.676 |
| Weak modal + policy verb | "may raise", "might cut" | 🔄 In progress (Step 3) |
| Conditionality ("if...then") | Stance depends on future event | 🔄 In progress |
| Forward-looking language | Future vs current state | Pending |
| Mixed signal in same chunk | Inflation hawkish + growth dovish | Pending |
| Negation/concession ("although") | Partial signal cancellation | Pending |
| Q&A context (turn_type) | Answers depend on the question | In logit features |
| Previous-meeting delta | Relative stance, not absolute | See Section 6 notebook |
| `label_entropy` (continuous) | More expressive than binary split | Not yet used as target |

---

## Practical Plan (if implementing for fun)

1. **Add `label_entropy` and `max_ordinal_gap`** to `chunks_wide` — better targets than binary `split`
2. **Method C first** (annotator embedding) — most data-efficient, cleanest story. Uses 20K examples not 5K.
3. Use `deberta-v3-base` or `roberta-base` — don't need a large model, chunks are short
4. Freeze encoder for epochs 1–2, then unfreeze with low LR
5. After training: inspect annotator embedding space + swap-annotator attribution

**Compute estimate:** ~20K examples × 256 tokens × deberta-base — roughly 30–60 min on GPU (Colab T4 should handle it). CPU-only will be slow.

---

## Connection to Main Thesis

Framing for the disagreement chapter:

> *Cross-model disagreement in hawkish/dovish classification reflects disagreement over which policy-relevant inference rule dominates — not semantic ambiguity. Models diverge when language describes the analytical process (progress, evidence, expect) rather than stating a policy conclusion, because models apply different implicit reaction functions to underdetermined inputs.*

The multi-head / annotator-embedding experiments would let you name those reaction functions explicitly rather than inferring them from SHAP coefficients. But for the thesis's main spillover question, the κ decomposition + SHAP analysis is already sufficient. These methods are extensions.

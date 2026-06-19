# LLM Workflow And Output Plan

## Goal

Use one shared scorer CLI with one CSV per model run, one row per chunk,
and a stable self-contained schema that is easy to inspect in pandas without
extra joins.

This keeps the workflow simple:

- one scorer CLI
- one model -> one output CSV
- one chunk -> one row (independent, zero cross-chunk context)
- full chunk metadata travels with the prediction

## Folder structure

The `src/llm/` folder uses a shared CLI structure rather than one script per model.

- `openrouter_models.py`: single source of truth for model keys, slugs, tags, providers, and per-model sleep
- `score_openrouter.py`: shared scorer CLI
- no per-model wrapper scripts

This avoids duplicate logic and makes prompt/schema changes happen in one place.

## Model registry

Models are defined in `openrouter_models.py`. Each `ModelSpec` carries:

| Field | Description |
|-------|-------------|
| `key` | Short internal key used in CLI and output filenames |
| `slug` | Model slug passed to the API |
| `tag` | Uppercase tag for logging |
| `label` | Human-readable model name |
| `rpm` | Requests per minute cap fed to the async rate limiter |
| `base_url` | API base URL (OpenRouter, Groq, Mistral direct, etc.) |
| `api_key_env` | Environment variable name for the API key |

### Active models

| Key | Model | Provider | RPM |
|-----|-------|----------|-----|
| `llama33` | Llama 3.3 70B Instruct | **Groq** (`api.groq.com`) | 200 |
| `deepseekv3` | DeepSeek V3 | OpenRouter | 60 |
| `mistrallarge3` | Mistral Large 3 | **Mistral direct** (`api.mistral.ai`) | 60 |
| `qwen25_72b` | Qwen 2.5 72B Instruct | OpenRouter | 200 |
| `qwen35max` | Qwen 3.5 Max | OpenRouter | 20 (OpenRouter hard cap — high demand) |
| `gpt55` | GPT-5.5 | OpenRouter | 20 |
| `gemini31pro` | Gemini 3.1 Pro | OpenRouter | 20 |

**Note on DeepSeek:** `deepseek-v4-pro` was replaced with `deepseekv3` (`deepseek/deepseek-chat`)
because V4 Pro returns empty responses on OpenRouter (likely a thinking model returning output
in `reasoning_content` rather than `content`). DeepSeek V3 is a frontier-class 671B MoE model
sufficient for stance classification.

### Required environment variables (`.env`)

```
OPENROUTER_API_KEY=...
GROQ_API_KEY=...          # for llama33
MISTRAL_API_KEY=...       # for mistrallarge3
```

## Commands

Standard scoring commands (1 worker, default):

```powershell
uv run python src/llm/score_openrouter.py --model llama33
uv run python src/llm/score_openrouter.py --model deepseekv3
uv run python src/llm/score_openrouter.py --model mistrallarge3
uv run python src/llm/score_openrouter.py --model qwen35max
uv run python src/llm/score_openrouter.py --model gpt55
uv run python src/llm/score_openrouter.py --model gemini31pro
```

With concurrent workers for faster throughput:

```powershell
uv run python src/llm/score_openrouter.py --model llama33 --workers 5
uv run python src/llm/score_openrouter.py --model deepseekv3 --workers 10
uv run python src/llm/score_openrouter.py --model mistrallarge3 --workers 3
```

Default behavior:

- `--workers` defaults to `1` (sequential)
- `--batch-size` defaults to `1` (one chunk per call — intentional, prevents cross-chunk context)
- `--temperature` defaults to `0.0`
- `--prompt-version` defaults to `v1`

**Do not increase `--batch-size`** — batching multiple chunks into one call risks the model
anchoring labels relative to other chunks in the same request, compromising independence.
Use `--workers` for throughput instead.

Resumability: re-running any command resumes from the last checkpoint. Rows with
`parse_error` labels are also retried on resume.

## Prompt architecture (v1)

The scorer uses a system + user message split:

- **System prompt**: establishes the expert role, scopes classification to the provided text only,
  and mandates JSON-only output. Stable across runs.
- **User message**: contains the task description, label definitions (ordered dovish → hawkish),
  JSON format spec with example, and the chunk text(s).

Key prompt design decisions:
- `"neutral"` note: *"data-dependent" language alone is not sufficient for neutral — consider
  the direction of risks the speaker emphasises.*
- Neutral-preference instruction: `"If the excerpt does not clearly imply tightening or easing, use 'neutral'."`
- Labels ordered dovish → hawkish in the prompt to match the natural policy scale.

## Mistral Batch API (alternative for `mistrallarge3`)

`score_mistral_batch.py` submits all 5004 chunks as a single async batch job to Mistral's
Batch API (`/v1/batch/jobs`). Cheaper (~50% discount) and avoids real-time rate limits.
Output lands in `chunk_predictions_mistrallarge3_batch.csv` with the same schema.

**Status (2026-06-19): batch submitted — check before re-running the live scorer.**

```powershell
# Check status and download results if done
uv run python src/llm/score_mistral_batch.py --fetch

# Or keep polling until complete (blocks terminal)
uv run python src/llm/score_mistral_batch.py --fetch --poll
```

If you need to submit a new batch (e.g. after a failure):
```powershell
# Delete state file first, then re-submit
Remove-Item output/stance/mistral_batch_state.json
uv run python src/llm/score_mistral_batch.py --submit
```

State is saved to `output/stance/mistral_batch_state.json` (job ID, file ID, timestamps).

## Concurrency model

Workers are async coroutines (`asyncio` + `AsyncOpenAI`). A shared `AsyncRateLimiter`
(token bucket) enforces the per-model RPM cap globally across all workers. Each coroutine:
1. Acquires a rate-limiter token (waits if the bucket is empty)
2. Calls the API with a single chunk
3. Writes result under an `asyncio.Lock`

There is no shared state between workers during inference. The model sees exactly one chunk
per call and has no memory of other concurrent calls. Concurrency does not introduce
cross-chunk contamination.

The `--rpm` flag overrides the model-default RPM (set in `openrouter_models.py`) at runtime.

## Output file pattern

Per-model files under `output/stance/`:

- `chunk_predictions_llama33.csv`
- `chunk_predictions_deepseekv3.csv`
- `chunk_predictions_mistrallarge3.csv`
- `chunk_predictions_mistrallarge3_batch.csv` (Mistral Batch API variant)
- `chunk_predictions_qwen25_72b.csv`
- `chunk_predictions_qwen35max.csv`
- `chunk_predictions_gpt55.csv`
- `chunk_predictions_gemini31pro.csv`

Meeting-level aggregations (from `notebooks/13_stance_timeseries.ipynb`):

- `meeting_scores_{model_key}.csv`

## CSV schema

| Column | Description |
|--------|-------------|
| `chunk_uid` | Globally unique chunk identifier |
| `bank` | `BoE`, `ECB`, or `Fed` |
| `doc_id` | Source document identifier |
| `date` | Source document date (YYYYMMDD int) |
| `doc_type` | Source document type |
| `speaker` | Speaker name |
| `speaker_role` | Speaker role |
| `turn_idx` | Integer turn position within the document |
| `turn_type` | `opening`, `answer`, etc. |
| `chunk_id` | Chunk index within document |
| `start_sent_idx` | First sentence index in chunk |
| `end_sent_idx` | Last sentence index in chunk |
| `n_sentences` | Number of sentences in chunk |
| `text` | Chunk text sent to the model |
| `model_key` | Internal short key, e.g. `llama33` |
| `model_slug` | Full API model slug, e.g. `llama-3.3-70b-versatile` |
| `label` | Predicted stance: `dovish` / `mostly dovish` / `neutral` / `mostly hawkish` / `hawkish` |
| `confidence` | Model confidence: `low`, `medium`, or `high` |
| `temperature` | Sampling temperature used |
| `prompt_version` | Prompt version identifier |
| `created_at` | Run timestamp in ISO format |

## Aggregation (meeting level)

Five-class net hawk score and variants, computed in `notebooks/13_stance_timeseries.ipynb`:

| Score | Formula |
|-------|---------|
| `net_hawk` | `(H + 0.5·MH − D − 0.5·MD) / n` |
| `logit` | `log((H + 0.5·MH + 0.5) / (D + 0.5·MD + 0.5))` |
| `wtd_net_hawk` | `Σ(wᵢ·sᵢ) / Σwᵢ` where `wᵢ = n_sentences`, `sᵢ ∈ {−1, −0.5, 0, 0.5, 1}` |

Where H = #hawkish, MH = #mostly hawkish, D = #dovish, MD = #mostly dovish.

These generalise the original 3-class formulas — they collapse to identical results if no
mostly-hawkish or mostly-dovish labels are predicted.

## Design decisions

### One chunk per call, workers for throughput
Batching multiple chunks into one request risks cross-chunk label anchoring. Use `--workers N`
instead — each worker makes an independent single-chunk call.

### Per-provider `base_url` and `api_key_env` in ModelSpec
Each model carries its own provider config. Switching a model from OpenRouter to a direct API
(Groq, Mistral) requires only a registry change in `openrouter_models.py`, not script changes.

### Per-model `sleep_between_calls`
Rate limits vary significantly across providers and model tiers. Encoding sleep in the spec
avoids needing to pass it as a CLI argument on every run.

### Parse errors are retried on resume
Rows with `label == "parse_error"` are treated as pending on resume, so transient API failures
are automatically cleaned up on the next run without manual intervention.

### Why `confidence` is categorical
`low` / `medium` / `high` avoids false precision from decimal probabilities and is more robust
to LLM overconfidence and miscalibration.

### Why opening chunks are excluded
Only Q&A body chunks are scored (`BoE_chunks.csv`, `ECB_chunks.csv`, `Fed_chunks.csv`).
Opening statements are excluded because their rhetorical register differs from Q&A answers,
which are the primary signal of interest for cross-border spillover analysis.

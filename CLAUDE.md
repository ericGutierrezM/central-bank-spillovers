# Central Bank Spillovers — Claude Instructions

## Project
Empirical macro-finance thesis (BSE 2025–2026).
Research question: does central bank rhetoric cause asymmetric cross-border equity spillovers?
See README.md for full methodology and data overview.

## /wrap-up

When the user types `/wrap-up`, append a new session entry to `sam_fraley_log.md`.

Format:
```
## Session N — YYYY-MM-DD

**Goal:** <one line on what the session set out to do>

**Completed:**
- <bullet per concrete thing finished>

**Corpus state after this session:** <only if it changed>

| Bank | Location | Files | Coverage |
...

**Open questions / next steps:**
- <anything unresolved or immediately next>

---
```

Rules:
- Infer session number by counting existing `## Session` headings and incrementing
- Use today's date
- Be factual and concise — this is a research log, not a summary for an audience
- Do not invent details; only record what actually happened in the session

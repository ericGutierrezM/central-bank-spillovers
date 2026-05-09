# Central Bank Spillovers — Session Log

Project: Does central bank rhetoric cause asymmetric cross-border equity spillovers?
Repo: `central-bank-spillovers`
Author: Samuel Fraley (BSE 2025–2026)

---

## Session 1 — 2026-05-09

**Goal:** Set up raw transcript corpus for all three central banks.

**Completed:**
- Audited all three transcript folders (Fed, BoE, ECB) to understand filename conventions and document types
- Built `src/fed_pdf_to_txt.py` — converts all 174 Fed PDFs to `.txt` in `data/transcripts/Fed/raw/`
  - Handles three formats: `FOMCYYYYMMDDmeeting`, `FOMCYYYYMMDDconfcall`, `FOMCpresconfYYYYMMDD`
  - Added `re.IGNORECASE` to catch one lowercase outlier (`fomcpresconf20240731.pdf`)
- Built `src/boe_pdf_to_txt.py` — converts 84 BoE PDFs to `BoE_YYYYMM_{type}.txt` in `data/transcripts/BoE/raw/`
  - Collapses three legacy naming conventions (inflation-report, press-conference, mpr) into `transcript` / `opening` types
  - Skips 15 slide-deck PDFs (near-zero prose)
- Built `src/ecb_normalize.py` — renames 89 ECB `.txt` files to `ECB_YYYYMMDD.txt` in `data/transcripts_cleaned/ECB/`
  - Filters to 2015–2025 study window (drops 206 pre-2015 files)
  - Handles old `is*`, modern `ecb.is*`, hash suffixes, and one-off `ecb.sp*` special presser

**Corpus state after this session:**

| Bank | Location | Files | Coverage |
|------|----------|-------|----------|
| Fed | `data/transcripts/Fed/raw/` | 174 | 2007–2026 (meeting + confcall + presconf) |
| BoE | `data/transcripts/BoE/raw/` | 84 | 2015–2026 (transcript + opening) |
| ECB | `data/transcripts_cleaned/ECB/` | 89 | 2015–2025 |

**Open questions / next steps:**
- Fed files include pre-2015 meetings and confcalls — will need to filter to study window before scoring
- BoE has no exact day in filenames (only YYYYMM) — need to look up exact MPC meeting dates for event-study alignment
- Fed and BoE not yet moved to `transcripts_cleaned/` — consider doing that before LLM scoring
- Next milestone: write and test the LLM scoring prompt (Hawkishness 1–10, Uncertainty 1–10) on a small batch

---

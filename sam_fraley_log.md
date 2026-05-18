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
- Built `src/ecb_normalize.py` — renames 89 ECB `.txt` files to `ECB_YYYYMMDD.txt` in `data/transcripts_normalized/ECB/`
  - Filters to 2015–2025 study window (drops 206 pre-2015 files)
  - Handles old `is*`, modern `ecb.is*`, hash suffixes, and one-off `ecb.sp*` special presser

**Corpus state after this session:**

| Bank | Location | Files | Coverage |
|------|----------|-------|----------|
| Fed | `data/transcripts/Fed/raw/` | 174 | 2007–2026 (meeting + confcall + presconf) |
| BoE | `data/transcripts/BoE/raw/` | 84 | 2015–2026 (transcript + opening) |
| ECB | `data/transcripts_normalized/ECB/` | 89 | 2015–2025 |

**Open questions / next steps:**
- Fed files include pre-2015 meetings and confcalls — will need to filter to study window before scoring
- BoE has no exact day in filenames (only YYYYMM) — need to look up exact MPC meeting dates for event-study alignment
- Fed and BoE not yet moved to `transcripts_normalized/` — consider doing that before LLM scoring
- Next milestone: write and test the LLM scoring prompt (Hawkishness 1–10, Uncertainty 1–10) on a small batch

---

## Session 2 — 2026-05-09

**Goal:** Standardize Fed and BoE into `transcripts_normalized/`, set up session logging, and plan coverage visualization.

**Completed:**
- Built `src/standardize_normalized.py` — copies Fed and BoE processed files into `data/transcripts_normalized/`, filtered to 2015–2025 study window, with consistent naming:
  - Fed: `Fed_YYYYMMDD_{meeting|confcall|presconf}.txt` (90 files; 84 pre-2015 dropped)
  - BoE: `BoE_YYYYMM_{transcript|opening}.txt` (82 files; 2 post-2025 dropped)
- Created `sam_fraley_log.md` (this file) for session-by-session research logging
- Created `CLAUDE.md` defining the `/wrap-up` command — appends a new session entry to this log
- Coverage visualization script (`src/coverage_timeline.py`) initiated via Codex — parses filenames across all three cleaned folders, counts documents per month, plots 3 stacked bar subplots + shared panel; pending review

**Corpus state after this session:**

| Bank | Location | Files | Coverage |
|------|----------|-------|----------|
| Fed | `data/transcripts_normalized/Fed/` | 90 | 2015–2025 |
| BoE | `data/transcripts_normalized/BoE/` | 82 | 2015–2025 |
| ECB | `data/transcripts_normalized/ECB/` | 89 | 2015–2025 |

**Open questions / next steps:**
- BoE counts 2 files per meeting (transcript + opening) — decide whether coverage plot shows files or meetings
- BoE has no exact day in filenames (YYYYMM only) — need exact MPC dates for event-study alignment
- Review and run `src/coverage_timeline.py` once ready
- Next milestone: write and test the LLM scoring prompt (Hawkishness 1–10, Uncertainty 1–10) on a small pilot batch

---

## Session 3 — 2026-05-09

**Goal:** Collect equity and VIX daily data; spot-check coverage.

**Completed:**
- Collected daily equity indices and VIX via yfinance; stored in `data/controls/`
  - `global_indices_daily.csv` — Date, FTSE 100, S&P 500, Euro Stoxx 50 (2927 rows, 2015-01-02 to 2026-05-08)
  - `vix_daily.csv` — Date, VIX (2854 rows, 2015-01-02 to 2026-05-08)
- Spot check results:
  - No duplicate dates in either file
  - FTSE 100 and S&P 500: no missing values
  - Euro Stoxx 50: 1 missing value (needs investigation)
  - VIX has 73 fewer rows than equity file — likely a calendar mismatch; needs alignment check

**Open questions / next steps:**
- Identify which date has the missing Euro Stoxx 50 value and fill or flag it
- Reconcile the 73-row gap between VIX and equity files (different trading calendars from yfinance?)
- A proper health-check script (`src/check_controls.py`) should be written to automate this for future data pulls
- Next milestone: write and test the LLM scoring prompt (Hawkishness 1–10, Uncertainty 1–10) on a small pilot batch

---

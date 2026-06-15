# Known Corpus Issues

Files flagged during pipeline health checks, with notes on how they were addressed and what needs manual verification.

---

## Fed

| File | Issue | Fix Applied | Manual Check |
|------|-------|-------------|--------------|
| `FOMCpresconf20180321` | Speaker label used `CHAIRMAN POWELL` (not `CHAIR POWELL`) | Added `chairman powell` to `_CHAIRS` set in C | |
| `FOMCpresconf20180613` | Same as above | Same fix | |
| `FOMCpresconf20180926` | Speaker label used colon format `CHAIRMAN POWELL:` instead of period; opening block was dropped entirely by B | Updated `_SPEAKER_SPLIT_RE` in B to accept `.`, `:`, or `-` as delimiter | Spot-check that opening turns now appear in Fed.csv |
| `FOMCpresconf20181219` | Same colon format issue | Same fix | |
| `FOMCpresconf20190130` | Same colon format issue | Same fix | |
| `FOMCpresconf20200303` | Emergency COVID cut — Powell opens with "Earlier today..." not a greeting | Soft-check relaxed to only require turn 0 is chair, not a greeting | Confirm opening is correctly excluded from Q&A corpus |

---

## BoE

| File | Issue | Fix Applied | Manual Check |
|------|-------|-------------|--------------|
| `BoE_201705_transcript` | Carney labeled as `Mark Carney (MC):` — initials suffix broke `_SPEAKER_INLINE_RE` in B | Updated regex to allow `Name (XX):` format | Spot-check Carney turns appear in BoE.csv |
| `BoE_202105_transcript` | Bailey referred to as `Andrew` (first name only) — not matched by governor role set in C | Added `"andrew"` and `"mark"` to `GOVERNORS` in C | Confirm no journalist named Andrew is misclassified |
| `BoE_202003_transcript` (Mar 11 emergency) | Not downloaded — joint MPR+FSR URL structure | Hardcoded PDF URL in A | Verify transcript content is sensible |
| `BoE_202005_transcript` (May 7) | Same URL issue | Hardcoded PDF URL in A | Verify transcript content is sensible |
| `BoE_202008_transcript` (Aug 6) | Same URL issue | Hardcoded PDF URL in A | Verify transcript content is sensible |
| `BoE_201708_transcript` | Only 3 meetings in 2017 (not 4) | Not yet investigated | Check if Aug 2017 meeting transcript exists on BoE website |

---

## ECB

| File | Issue | Fix Applied | Manual Check |
|------|-------|-------------|--------------|
| `ECB_20230504` | Q&A section has `De Guindos:` label but Lagarde's answers are unlabeled — labeled parser runs but misses Lagarde | Not yet fixed | |
| `ECB_20231026` | Same issue | Not yet fixed | |
| `ECB_20250130` | Same issue | Not yet fixed | |

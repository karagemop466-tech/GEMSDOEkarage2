# Submission status — no file cleared under the literal protocol

**Current decision (2026-10-31): NO FILE IS CLEARED TO SUBMIT. Do not upload or spend a competition slot.**
The required rule stops a candidate when more than 70% of its dots fall within 3 px of **any** registry raster. No space-filling-reference exception appears in the rule.

| Candidate / site | Recorded check | Decision |
|---|---|---|
| HALO `gemsdoe-karage2-halo39-b44090-sep2-20261031.tif` | 99.84% within 3 px of the r13 lattice; `uniqueness_literal_gate.unique=false`, `stop_required=true` | **DO NOT SUBMIT** |
| Off-catalogue GBM `gemsdoekarage2-gbm-offcat-a5-n100000-20261031T020958Z.tif` | 93.77% one-sided overlap against a non-space-filling GEMSDOE30 raster; the scan also reports 99.67% against a space-filling reference | **DO NOT SUBMIT** |
| K10 corridor candidate | The like-for-like audit excludes the dense lattice, but the literal rule says any registry raster; receipt records a firing against the lattice | **DO NOT SUBMIT** |
| GeoDAWN structural-habitat TIFF merged from parallel work | Saved 23.26% overlap against 13 focus files; later lattice recheck: 40,561/40,561 dots (100%) within 3 px | **DO NOT SUBMIT** |
| Nine requested GEMSDOE site files | Their scores are USER-REPORTED / UNVERIFIED; all fail uniqueness against the recorded registry/site family | **DO NOT RESUBMIT** |

Machine-readable decision: [`evidence/strict-protocol-decision-2026-10-31.json`](evidence/strict-protocol-decision-2026-10-31.json). Saved-byte inventory: [`evidence/public_downloads_audit.json`](evidence/public_downloads_audit.json) (`PASS_RESEARCH_ONLY`, `downloadable_approved_submission: null`). The project can serve and audit the research TIFFs, but none is an approved competition submission.

**Score reporting:** The supplied GEMSDOE32 value 0.2778 is not linked to an organizer receipt and is not ORGANIZER-CONFIRMED. Model estimates are MODEL-PROJECTION only. A catalogue hide-and-recover value is HOLDOUT-DTI only and needs its evaluator, withheld-positive count, and 95% CI; it is not a leaderboard score.

**Unresolved / next work:** the dense lattice makes the literal 70% rule fail for many candidate geometries. Do not waive it or move pixels into uncovered cells. A protocol owner must explicitly revise the rule before a future experiment can be eligible. Separately, authenticate the official training stack/template and exterior convention, obtain organizer receipts for scores, and establish a holdout that predicts off-catalogue expert truth. No submission slot has been used.

## Historical decisions

Earlier pages and cards that said “OK TO SUBMIT” describe earlier, superseded internal interpretations that excluded space-filling references. They are retained for provenance; current generated release desks now apply the literal rule and label the files research-only. Do not use older positive wording as authorization.

# Submission status — GEMSDOEkarage2 (DOE GEMS Prize Challenge)

**Generated from:** `evidence/hk3/run_card.json` (run card generated 2026-10-28T17:40:28Z)
**Verified:** `python scripts/build_hk3_pages.py --check` → pages up to date

---

## The one file offered for upload

| Field | Value |
|---|---|
| File | `docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif` |
| ZIP | `docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.zip` |
| SHA-256 (TIF) | `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9` |
| SHA-256 (ZIP) | `3044479a035bf14fa72a4ad6c09f8b533ee13c3641d128c3ad8654f1649ed4d1` |
| Submission name | `gemsdoekarage2-hk3-edgecentrality-apron3-20261028` |
| Note (≤ 140 chars) | `HK3: 34-feature HGB with catalogue-free edge-centrality bands; dots sep 3px, >3px off catalogue; zeros outside` (110 chars) |

### Is it OK to download and submit?

**It is format-valid, but not unconditionally approved.** Read the gates below before deciding.

### Format validation (ALL PASS — receipt in evidence/hk3/run_card.json)

| Check | Result |
|---|---|
| Single band | PASS |
| dtype float32 | PASS |
| Dimensions 3730 × 3292 | PASS |
| CRS EPSG:32611 | PASS |
| Transform matches example_submission.tif | PASS |
| No NaN anywhere | PASS |
| No infinity anywhere | PASS |
| Values in [0, 1] | PASS (min 0.0, max 1.0) |
| No dots on mapped catalogue faults | PASS (0 dots on catalogue) |
| Zeros outside the footprint | PASS |
| Whole array finite | PASS |

This file will **not** trigger the portal error "Predicted values must be in range [0, 1]" — every pixel is finite and inside [0, 1], including outside the footprint (zeros, same convention as the organizer reference notebook and the user-reported-scored GEMSDOE32 champion file).

### Uniqueness gates

| Gate | Result |
|---|---|
| Unique vs the nine scored GEMSDOE site files | PASS (max 48.4% of dots within 3 px; |ρ| ≤ 0.031) |
| Chance-corrected overlap vs all 450 registry rasters | PASS (≤ 0.70) |
| Literal 70% rule vs all registry rasters | **FAIL** (disclosed exception) |
| Literal 70% rule vs submitted dot rasters | PASS |
| Rank correlation ≤ 0.90 vs every registry raster | PASS |

**Bottom line:** The file is **unique vs all nine GEMSDOE focus sites** (so it is unlike any submission on those sites). It fails the strictest literal rule only against 3 never-submitted / line-surface research rasters in the broader registry — not against any GEMSDOE site file. The site prints this exception in red on every page.

**Verdict:** PROMOTE by the automated gates, with the literal-rule exception disclosed. The user (selector) decides whether to spend a weekly submission slot (≤ 3 per week on DrivenData). No competition slot has been spent.

---

## Nine focus sites — executive summary

Best user-reported score among the nine sites: **GEMSDOE32, 0.2778** (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`).

| Site | File · dots | User-reported score | Unique vs other 8? | Re-submit? |
|---|---|---|---|---|
| GEMSDOE32 | `gemsdoe32-h33-h33-2-b2-…-zeros.tif` · 37,654 | 0.2778 | No — 100.0% near GEMSDOE24 | No (already scored) |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-…-zeros.tif` · 38,854 | 0.2750 | No — 97.6% near GEMSDOE27 | No |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-…-nan.tif` · 37,660 | 0.2710 | No — 100.0% near GEMSDOE24 | No |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-…-nan.tif` · 40,199 | 0.2708 | No — 100.0% near GEMSDOE24 | No |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-…-nan.tif` · 41,865 | 0.2632 | No — 99.7% near GEMSDOE27 | No |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-…-nan.tif` · 44,090 | 0.2600 | No — 100.0% near GEMSDOE24 | No |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-…` · 44,090 | 0.2600 | No — 100.0% near GEMSDOE24 | No |
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-…-nan.tif` · 60,069 | 0.2477 | No — parent of the family | No |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-…-nan.tif` · 61,328 | 0.2449 | No — 98.0% near GEMSDOE24 | No |

All nine scores are **USER-REPORTED / UNVERIFIED** — no file-linked organizer receipt exists. Confirm on the official leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/

None of the nine files should be re-submitted: they form one dot family with pairwise overlap ≥ 70%, and several exceed ρ = 0.90.

---

## Holdout evaluation (HOLDOUT-DTI — never a leaderboard score)

| Metric | Value |
|---|---|
| HOLDOUT-DTI | 0.1845 |
| 95% CI | [0.1677, 0.2015] |
| Evaluator | `gems57-pooled-hide-v2` |
| Withheld positive pixels | 58,258 |
| Beats re-fitted incumbent (paired CI excludes 0) | Yes |

Leaderboard-calibrated estimate (ratio transfer from user-reported anchors — **not a score**):
- θ = 1.00: 0.2855
- θ = 0.75: 0.2798
- θ = 0.50: 0.2742

---

## How to submit

1. Download the TIF from `docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif` (one-click button on `docs/index.html`).
2. Verify: `sha256sum` must print `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`.
3. Sign in to DrivenData, open the submissions page, check you have a weekly slot (≤ 3 per week).
4. Upload the TIF with the name and note from the table above.
5. When the score appears, record it as ORGANIZER-CONFIRMED. Nothing on this site is organizer-confirmed until then.

See `docs/how-to-submit.html` for the full step-by-step guide.

---

## Limitations

- No organizer receipt is reachable from this sandbox (network allow-list: GitHub, PyPI, npm only). All nine site scores and the leaderboard high are user-typed and unverified.
- The prompt cites three different "current highs" (0.4544, 0.4413, 0.3195); these are stale/conflicting values.
- The HK3 lane's 3-experiment budget is exhausted; no new geological experiment was run in this session.
- Promotion to a real submission slot is a separate selector step.
- No training data was downloaded (DrivenData data tab requires login).
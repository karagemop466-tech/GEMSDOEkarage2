# Repository review — 2026-10-28 (Arena session)

## Executive result

**Release status: NEGATIVE — DO NOT SUBMIT.** This review made no new geological experiment, raster placement, or competition-slot selection. The existing K2 TIFF is downloadable for research/inspection only. It is not cleared under the literal all-registry uniqueness rule and no organizer submission receipt exists.

The repository already contains a preregistered set of five candidate hypotheses in `research/hypotheses-2026-10-28-preregistration.md` (B1 supervised multi-physics texture; B2 visible-only fault-tip continuation; B3 structure-tensor ridge coherence; B4 scarp-step asymmetry; B5 seismicity alignment). They differ from the older H1 signed-gradient parity experiment. The K2 B1+B2 candidate was run in a prior recorded session; this review did not rerun it. The detailed mechanism, layer list, confounders, cost, and protocol are in that preregistration and its evidence. This review does not represent those hypotheses as independently discovered or revalidated now.

## Three-pass review

### Pass 1 — read through and reconcile release claims

- Read `README.md`, active site pages (`docs/index.html`, `docs/executive-summary.html`, `docs/how-to-submit.html`), the K2 experiment card/holdout/registry/validator receipts, H1 records, selector receipts, focus-site audits, and test suites.
- Found conflicting release language: the landing and executive summary called the K2 file a conditional candidate while the saved K2 registry record shows the literal overlap gate fails. The landing page's button could be read as invitation to upload.
- Updated both active pages to say **research download — DO NOT SUBMIT**, explain the literal failure and distinguish a narrow nine-repository submission comparison from global registry clearance. Replaced the estimated-score phrasing with **leaderboard estimate unavailable**.
- Historical experiment receipts were retained; they were not rewritten to manufacture a positive selector result.

### Pass 2 — test/evidence review and edge cases

- K2 recorded **HOLDOUT-DTI**: `gems57-pooled-hide-v2`, pooled DTI 0.1581207190, 58,258 withheld positive pixels, 95% CI [0.1423739219, 0.1741535541]; paired difference vs best primitive +0.08614, 95% CI [+0.06914, +0.10369]. These are prior recorded holdout results, not reproduced in this review, not ORGANIZER-CONFIRMED scores, and not leaderboard estimates. Source: `evidence/k2/run_card.json` and `evidence/k2/combined_holdout.json`.
- K2's saved-file receipt records one float32 band, EPSG:32611, shape 3730×3292, all array cells finite and within [0,1], with zeros outside the mirror footprint. The separate strict local validator fails `outside_is_nan`. Neither local check proves organizer acceptance or portal acceptance. The portal's prior range error has no retained rejected TIFF/receipt tying it to a specific cause.
- K2 registry audit: 430 checked submission rasters across the nine focus repositories met the reported narrow comparison maxima (68.08% directional within-3-pixel overlap; absolute Spearman 0.11894), but the all-registry audit includes a lattice calibration witness at 100% overlap and a ctx-ridge calibration raster at 72.05%, over the 70% threshold. Full registry coverage is false/incomplete. Under the prompt's literal rule, this is a failure, regardless of the narrower nine-site pass.
- The existing run card calls its experimental verdict `promote` but explicitly limits that to conditional selector consideration; its download policy is conditional and says the weekly slot is not approved. The current release decision in this review is stricter and explicit: negative/no upload. The historical record is not treated as an organizer ruling.
- Added regression tests so the active pages retain the negative/no-upload release state, disclose the literal lattice failure, and do not relabel the file as unconditionally unique. The linked machine-readable release audit also records the ctx-ridge failure.

### Pass 3 — full request and stop-rule audit

- **No new TIF was generated.** There is no coordinator-supplied method paragraph establishing the assigned lane; the user prompt says to stop if the lane is absent/duplicate. The existing K2 artifact is already a TIF but fails the literal uniqueness threshold. Re-encoding, renaming, jittering, or inventing a candidate merely to produce a download would not resolve this and would undermine the uniqueness requirement.
- The candidate's **HOLDOUT-DTI** is 0.1581 (gems57-pooled-hide-v2; 58,258 withheld positives; 95% CI 0.1424–0.1742). The review's machine-readable negative card is `docs/evidence/k2-review-2026-10-28.json`. The best supplied GEMSDOE32 report is 0.2778 **USER-REPORTED / UNVERIFIED**, not an organizer receipt. There is no defensible estimate that K2 will beat that private leaderboard result. No projected or extrapolated score is presented as a score.
- The historical hypothesis catalog and experiment results are present; current experiment count remains within its prior run card's recorded 3-experiment budget. This review did not use another experiment or submission slot.
- Made no attempt to access or modify the external read-only GEMSDOE Pages sites. No credentials, competition quota, official receipt, current leaderboard snapshot, or authenticated organizer dataset were available to this review.

## Verification performed in this checkout

- Installed repository-pinned dependencies and ran `.venv/bin/pytest -q` after merging current `origin/main` safeguards: **147 passed, 7 skipped, 34 subtests passed**; Rasterio emitted 38 `PendingDeprecationWarning`s.
- `npm ci`: completed; 0 reported vulnerabilities.
- `npm test`: **3 passed**.
- `npm run test:site`: **8 passed** (includes the new K2 release-language regression).
- `npm run test:browser`: passed at 1440 px, 390 px, and 320 px; release-lock and research-only download checks passed.
- `.venv/bin/python scripts/review_k2_release.py` reproduced the archived negative release review without rerunning the model holdout or full registry comparison.
- Independently read the committed K2 TIFF with Rasterio and NumPy: one GTiff band, float32, EPSG:32611, 3730×3292, transform [100, 0, 243350, 0, -100, 4508550], all pixels finite, min/max 0/1, only {0,1}, 54,491 positives. SHA-256 `504be4587e3bec7b81f802b4c16b6c546c683e8a4c8b514d3a9856c6e0698dfb`, matching its saved local receipt. Grid comparison is only against the owner-mirror receipt; this local readback does not prove organizer acceptance or global uniqueness.

## Next work (must occur before any future upload)

1. Obtain the actual coordinator-assigned single-method paragraph or a written ruling on the absent-lane condition. Do not self-assign a new lane.
2. Resolve whether calibration rasters are in-scope for the literal uniqueness registry. Until an authorized selector explicitly defines otherwise, enforce the stated all-raster thresholds; do not game the spacing-5 lattice.
3. Restore and authenticate the organizer-provided inputs/template; resolve the exterior NoData/NaN requirement against the current competition submission page and a real validator receipt.
4. Build a complete, current registry and frozen same-split comparator; then preregister at most three experiments and canary each input feature before trusting it. Compare by paired spatial holdout with the shared evaluator, not by private leaderboard-score extrapolation.
5. Only a separate selector may consider the weekly slot after all science, uniqueness, file-format, source-authority, quota, and final-dot gates pass. Preserve the organizer's actual score receipt if submitted.

## Official sources for follow-up review

- [DrivenData GEMS competition](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem description and scoring/format page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official data tab (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE Geothermal Data Repository entry 1391](https://gdr.openei.org/submissions/1391)
- [Competition submission-format PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

During this review, the official DrivenData problem/format page was retrieved in both content chunks, the official USGS GeoDAWN page was retrieved, and the official reference repository README was retrieved. These confirm the fault-prediction task, distance-weighted Tversky description (α=0.2, β=0.8, 300 m triangular support), required EPSG:32611 / 100 m / float32 [0,1] template alignment, the GeoDAWN data context, and the availability of a CPU reference environment. The DrivenData leaderboard, authenticated data tab, submission page, quota/receipt, the DOE PDF, and INGENIOUS page were not freshly verified in this review. Links above are for manual source review; no organizer receipt or current private score is claimed.

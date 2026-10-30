# Live-source refresh and three-pass repository review — 2026-10-30

**Decision: NEGATIVE. No TIFF in this repository is approved to download and submit.** This review produced no geological experiment, candidate raster, score estimate, upload, or submission-slot selection. It refreshed a dated public leaderboard observation and GitHub-only source metadata, and made the static executive summary select the newest date-stamped official observation instead of hard-coding yesterday's snapshot.

## Executive answer

- The highest of the supplied nine historical claims remains GEMSDOE32's **0.2778 USER-REPORTED / UNVERIFIED**. The current GEMSDOE32 page calls it an owner-provided submission-log claim, says no submission-page receipt links this raster hash to the score, and labels the file “already submitted - do not resubmit.” The page also says no new file is cleared for submission. These are owner-page statements, not organizer receipts. [Current GEMSDOE32 page](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html); [dated public-page observation](../docs/evidence/official-review-2026-10-30.json).
- **Why it may have scored better — hypothesis, not established cause:** the pinned GEMSDOE32 mask is a strict subset of GEMSDOE25's D2.8 set; it removes 6,436 positive pixels and adds none ([pixel-level receipt](../docs/evidence/champion_forensics.json)). In the simple first-order Tversky approximation (alpha + beta = 1), adding a prediction helps only when its effective hit probability `a` is above `alpha × DTI`—about 0.0556 at DTI 0.2778. So removing low-support dots could improve the balance. The official score is distance-weighted, however: its alpha 0.2 / beta 0.8 penalties depend on weighted false-positive mass and fault coverage under a 300 m triangular kernel, not merely dot count. The approximation is intuition, not an exact evaluation. No authenticated receipt, hidden truth, or controlled same-file score comparison establishes that pruning caused the owner-reported change.
- **Can this repo establish a result above 0.2778? No.** A new-file leaderboard estimate is unavailable. No validated mapping from the repository's catalogue-based holdout to the expert-hidden public/private scoring set exists. Do not relabel a projection or another owner's holdout as a leaderboard score.
- The current public organizer page, freshly read in all three chunks at 2026-10-30 01:57:20 UTC, lists xiaofanhu first at **0.4544** and kpomazi's **0.3195 at rank 48**; the row immediately above is like60986 at 0.3217. These are **ORGANIZER-PUBLISHED PUBLIC LEADERBOARD SNAPSHOT** values, not a submission-page receipt, private-round result, HOLDOUT-DTI result, or score for any local raster. The earlier 2026-10-29 snapshot had kpomazi at rank 47; that rank change is preserved as dated history. [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
- A different same-day draft on another branch had claimed rank 48, but was properly withdrawn because its evidence card recorded that no official page had been fetched. This branch's 01:57:20 UTC page-reader capture is a new, independent observation; it does not retroactively validate that draft.
- **No unique TIFF was generated.** The download inventory is `PASS_RESEARCH_ONLY`, contains nine historical research artifacts, and has `downloadable_approved_submission: null`. The website's one-click TIFF is clearly marked **RESEARCH ONLY / DO NOT SUBMIT**. Do not submit it.

## Executive scorecard — nine requested sites

The file and score columns below are pinned historical references from the user-supplied list and repo audit, not current-head site champions or organizer receipts. The score class is **USER-REPORTED / UNVERIFIED**. “New-file estimate” is intentionally **Unavailable**. Geometry is measured on pinned owner-mirror bytes and is **not a score**. The three-pixel lattice witness is a dense calibration-like raster; high overlap is a literal protocol stop, not proof that an owner copied it.

| Site | Highest supplied historical file (research reference only) | Reported value | New-file leaderboard estimate | Measured overlap with lattice witness | Maximum overlap vs another of the nine | Unique under the stated rule? | OK to submit? |
|---|---|---:|---|---:|---:|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 USER-REPORTED / UNVERIFIED | Unavailable | 99.9218% | 100.0000% vs GEMSDOE25 | No | **No** |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | 99.9161% | 100.0000% vs GEMSDOE24 | No | **No** |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 USER-REPORTED / UNVERIFIED | Unavailable | 99.9234% | 98.0188% vs GEMSDOE24 | No | **No** |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 USER-REPORTED / UNVERIFIED | Unavailable | 99.9097% | 100.0000% vs GEMSDOE24 | No | **No** |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | 99.9161% | 100.0000% vs GEMSDOE24 | No; mask also matches GEMSDOE25 | **No** |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 USER-REPORTED / UNVERIFIED | Unavailable | 99.9179% | 100.0000% vs GEMSDOE24 | No | **No** |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | **0.2778 USER-REPORTED / UNVERIFIED** | **Unavailable** | 99.9150% | 100.0000% vs GEMSDOE24 | No | **No** |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 USER-REPORTED / UNVERIFIED | Unavailable | 99.9140% | 99.7086% vs GEMSDOE27 | No | **No** |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 USER-REPORTED / UNVERIFIED | Unavailable | 99.9176% | 97.5781% vs GEMSDOE27 | No | **No** |

Receipts: [`evidence/lattice-gate-audit-2026-10-29.json`](../docs/evidence/lattice-gate-audit-2026-10-29.json), [`evidence/uniqueness/nine-site-pairwise-recheck.json`](../docs/evidence/uniqueness/nine-site-pairwise-recheck.json), and the nine linked [site summaries](../docs/executive-summary.html). The pairwise audit measures positive-pixel proximity; it reports no unique file among these nine. The broader 440-reference audit is a dated pinned snapshot and had two failed-closed inputs; the all-site live registry is not established.

The literal lattice rule is unusually restrictive: on the owner-mirror template, 99.8713% of footprint cells are within 3 px of the witness. The receipt calculates that only 6,649 cells are outside this halo. At the 37,654-positive-pixel GEMSDOE32 budget, the pigeonhole lower bound is 82.34% overlap; the measured overlap is 99.9150%. A smaller map could only pass by allocating a large share of dots to the 6,649 uncovered cells, which would be gate gaming and is prohibited. The protocol conflict must be resolved by its owner; this review does not waive or alter it.

## Current-source checks and irregularities

1. **Official problem page.** The competition target is geological fault mapping—faults indicative of geothermal resources—not direct prediction/confirmation of geothermal vents. The page specifies distance-weighted Tversky (alpha 0.2, beta 0.8, triangular 300 m support) and a single-band float32 GeoTIFF, [0,1] values, EPSG:32611, 100 m resolution, matching bounds, and null/NaN outside. [Problem description and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
2. **Official data gate.** The public data URL redirected to DrivenData's login page. No authenticated organizer `training_features.tif`, labels, submission template, private truth, or submission receipt is in this session. [Data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/).
3. **GEMSDOE32 source.** The currently fetched site explicitly calls the 0.2778 result an owner-reported claim without a hash-linked submission receipt, and says the file was already submitted / should not be resubmitted. The site itself labels later research files DO NOT SUBMIT. The current owner site is not an organizer source.
4. **Freshness is not audit.** All nine current GitHub main HEADs differ from their pinned historical raster references. That is metadata only; no new HEAD raster bytes, scores, or receipts were audited. The refreshed feed checks GitHub commit metadata only. It does not scrape the competition, infer score changes, prove registry completeness, or inspect account quota.
5. **Prior artifacts and exterior convention.** The 2026-10-29 inventory still contains nine research-only public TIFFs. Existing bytes were not regenerated or repaired. Historical zero-outside rasters and the unresolved portal-range error remain separate concerns; local validation cannot establish portal acceptance.
6. **Irregularities for review:** the official page says its example submission predicts total fault absence; a separate owner-mirrored `sample_submission.tif` and label raster were previously measured to share positive cells. That mirror is not organizer-authenticated, so the discrepancy is unresolved. Do not conflate it with `reference/gemsdoe36/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif`: its companion [`synthetic-QA metadata`](https://github.com/karagemop466-tech/GEMSDOEkarage2/blob/main/reference/gemsdoe36/GEMS36_FORMAT_TEST_NOT_SUBMISSION.json) explicitly says it is not an official submission, has synthetic bounds, and is not a prediction. Its grid/NaN bytes do not establish the organizer template or explain the portal error.

## Four ranked untested hypotheses (qualitative, not score forecasts)

The current repo already documents these candidate mechanisms in [`2026-10-29-lattice-gate-and-decision.md`](2026-10-29-lattice-gate-and-decision.md). The table restates the untested *controlled tests*, not a claim that the mechanisms are novel across all GEMSDOE sites. The priority is qualitative expected holdout utility relative to these proposals; no numerical DTI improvement is estimated. All would use the existing multiband feature stack if restored, so none requires new external data in concept. The stack is absent from this checkout and the only cited copies are owner mirrors, not authenticated organizer inputs; therefore none is test-ready here.

| Rank / qualitative expected gain / cost | Layers and physical signature | Why it could identify a catalogue-missing fault | Difference from code already implemented here | Named non-fault mimic and falsification |
|---|---|---|---|---|
| 1 · highest relative potential, low confidence; medium cost | Isostatic gravity anomaly / vertical response plus detrended elevation and its slope. Fit a training-block-only, label-blind terrain nuisance model; test signed residual gravity edges persistent across scale. | A buried density offset may continue under alluvium with weak surface relief. | Not the raw-gradient or ridge-magnitude features in the saved H1/K2/K3 runs; adds block-fitted terrain residualization and a contour/shoreline null. Related gravity/topography ingredients exist in prior B4, so novelty is only for this exact controlled operator, not the idea family. | Unfaulted sediment–bedrock contact or lake-terrace riser. Require gain over a contour-aligned null and over gravity-only/terrain-only ablations; fail if the edge follows shoreline geometry. |
| 2 · moderate relative potential, low confidence; medium-high cost | Surface conductivity, isostatic gravity, and gravity horizontal gradient. Test a conductivity-Hessian saddle across an independently located gravity break, not high conductivity alone. | A covered offset could juxtapose conductive strata without a mapped surface trace. | H1 tested simpler conductivity contrast and H2 stepover geometry; this exact cross-profile saddle/null is not an implemented local feature. | Saline groundwater/playa margin or inversion seam. Use a conductivity ablation, survey-edge controls, and within-block shifted saddles. |
| 3 · low-to-moderate relative potential, low confidence; medium cost | Geodetic shear and dilatation fields interacting with persistence of reduced-to-pole magnetic / total-field horizontal-gradient edges. | A short covered strand might lie at a broad strain-regime transition, while the magnetic edge supplies finer localization. | K2/K3 did not include these strain bands; the interaction plus within-block shuffled-strain control is not implemented in this checkout. | Geodetic interpolation seam or intrusive contact. The interaction must beat magnetic-only and shuffled-strain controls; coarse strain cannot independently locate a 100 m fault. |
| 4 · low relative potential; low-medium cost; currently blocked | Earthquake-distance/density fields and gravity vertical response; test seismicity sidedness across independently located gravity edges. | Seismic context could prioritize an active unmapped structure but is not independent 100 m fault evidence. | No matching local flank-sidedness null test is recorded. Band metadata disagree between an owner-mirror `deq` name and the official page's earthquake-density wording. | Mining/production-induced seismicity and smoothing artifacts. Authenticate the feature semantics first; then compare to shuffled-seismicity and gravity-only controls. |

**Free-source and access status:** these proposed tests need no additional external layer if the competition's existing multiband feature stack is restored. The official source is the [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), which redirected to login during this review; the owner-mirror stack is not authenticated and is absent from this checkout. Independent optional sources, not required by these hypotheses, are the public [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) and [DOE GDR INGENIOUS dataset](https://gdr.openei.org/submissions/1391); their current bytes, footprint coverage, and terms were not obtained or revalidated here. No claim of current external-data availability is made.

**No experiment was run.** The user prompt points to a “single method paragraph below,” but supplies no uniquely identifiable lane assignment; the repo's current protocol explicitly forbids inventing one. The cached stack and authenticated competition rasters are also absent (`data/` and `.cache/competition_data/` are not present). The top hypothesis therefore was not tested, and no weekly slot was touched. Its untested status is not a positive result. Before work proceeds, assign a method paragraph, restore authenticated inputs, freeze the whole-segment buffered holdout and same-fold incumbent, test every feature-alone canary, and run the pre-placement surface check before any placement. Stop on either literal duplicate threshold.

## Three-pass review

### Pass 1 — implement and verify

- Read `README.md`, `AGENTS.md`, `SUBMISSION_STATUS.md`, the shared writer/evaluator/validator, the existing holdout/uniqueness receipts, generated pages, and previous review/hypothesis documents.
- Re-read the official problem page and all chunks of the public leaderboard. The data page returned the login screen; no participant data download was claimed.
- Added the 2026-10-30 dated public-page observation. Updated the GitHub-only freshness feed from the public GitHub API; it records all nine focus branches as changed from the pinned historical refs.
- Updated the page generator to choose the newest valid date-stamped official observation and link that evidence, instead of hard-coding the 2026-10-29 board. The public leaderboard remains a static dated observation; automated feed code still contacts GitHub only.

### Pass 2 — bug, edge-case, and test review

- Checked the static output and receipts for stale rank text, wrong report class, missing local links, and any language that could imply a public leaderboard row was a local score or a research TIFF was safe to upload.
- Re-ran the complete Python, Node feed/site, and browser smoke suites, plus the negative release assessment, research-download inventory, and generated-page checks. Results are recorded in [`evidence/live-source-review-card-2026-10-30.json`](../docs/evidence/live-source-review-card-2026-10-30.json).
- Any skipped tests require optional owner-mirror inputs; they are not evidence of organizer provenance, portal acceptance, or complete registry coverage. Rasterio warnings are implementation warnings, not scientific results.

### Pass 3 — recheck against the request

| Requirement | Result |
|---|---|
| Clear executive scorecard for all nine sites | Existing dashboard retained; historical reports and exact pinned files are tabled above, each labelled USER-REPORTED / UNVERIFIED. |
| Estimate a new file's leaderboard score | **Unavailable.** No calibrated transfer from catalogue holdout to hidden expert labels; no projection presented as a score. |
| Generate a unique high-scoring submission TIFF | **Not done and not safe to claim.** No candidate passes the recorded literal duplicate policy; no assigned lane or authenticated data/template. No fake, blank, copied, jittered, or lattice-hole candidate was emitted. |
| Validate the top new hypothesis before a weekly slot | No slot was used; the hypothesis was not tested because lane/data prerequisites fail. A negative run card is delivered instead of fabricated HOLDOUT-DTI evidence. |
| Refresh an up-to-date feed | The GitHub source-head feed is refreshed and labelled as metadata-only. Current public-board status is separately stored as a dated official-page observation; automated DrivenData scraping is not enabled. |
| Ensure every download is plainly marked | The page's one-click existing TIFF remains explicitly **RESEARCH ONLY / DO NOT SUBMIT**. There is no approved download. |

## Remaining work, in order

1. Assign exactly one method paragraph for this run; do not infer it from the hypothesis slate or another site's result.
2. Obtain the official competition files and sample template with authorized access; record hashes and provenance. The public data page currently redirects to login.
3. Resolve the literal dense-lattice uniqueness conflict with the protocol owner before any placement. Do not move dots into witness holes to manufacture clearance.
4. Restore the authenticated cached feature stack and use the shared evaluator/writer. Freeze whole-fault-segment, buffered hide-and-recover folds; build catalogue features only from visible faults and mask visible fault pixels exactly.
5. Run every feature-alone AUC canary (AUC > 0.90 is leakage until resolved) and compare the assigned candidate with a frozen same-fold incumbent using pooled DTI and a defensible 95% CI. Maximum budget remains three experiments or two hours, whichever comes first.
6. Only after a supported holdout improvement: check the complete current registry before placement and final dots after placement; validate saved bytes against the authenticated template and [0,1] range; obtain a separate selector approval within the account's displayed quota. No program in this repo uploads automatically.
7. Re-read the public leaderboard before a future report or upload. Do not call it a receipt for a local file.

## Verified source links for manual review

- [Official competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem, metric, target, and GeoTIFF specification](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official data tab (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Official submission rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN dataset](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [GEMSDOE32 owner page for the 0.2778 claim](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)

**Run card:** [`evidence/live-source-review-card-2026-10-30.json`](../docs/evidence/live-source-review-card-2026-10-30.json). A public source observation is not an organizer score receipt; no local submission score or acceptance is asserted.

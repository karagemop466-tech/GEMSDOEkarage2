# Current repository review and submission decision — 2026-10-31

## Executive decision

**NO FILE IS CLEARED TO DOWNLOAD AND SUBMIT.** No new experiment or TIFF was generated in this review. No competition slot was selected or used. This is a fail-closed decision, not a claim that the geology is unpromising.

Why the stop is binding:

1. The prompt's literal rule is `|Spearman| > 0.90 OR >70% of candidate dots within 3 px of ANY registry raster => stop`. The prior HALO release receipt has `uniqueness_literal_gate.unique = false`, `stop_required = true`, and reports 99.8389% one-sided overlap with the spacing-5 lattice. The prior GBM scan also reports a non-space-filling one-sided witness at 93.771% (`GEMSDOE30` g30s19). K10's saved `final_registry.json` records 99.997% worst one-sided overlap with the spacing-5 lattice; its selector excluded that witness. That exception is incompatible with the literal protocol in this request and is not applied here.
2. The user says not to spend a slot before a candidate beats the current holdout best. Existing records do not establish a same-fold, paired, current-incumbent win for an eligible candidate. In particular, the site-native holdout figures in sibling repositories use different evaluators, masks, fold structures, or counts and cannot be compared as one ranking.
3. The authenticated organizer submission template and training files are not present in this checkout. `.cache` has browser test runtime files only; there are no cached competition rasters in `.cache` or `data/`. The local owner-mirror grid is not proof of organizer provenance. A format check against an unauthenticated mirror is not acceptance evidence.
4. The user prompt does not contain a newly assigned single geological method paragraph. The repository's latest assigned S1 paragraph has already been tested and retired as negative. The protocol therefore does not authorize choosing another lane autonomously in this session.

The current root site now shows **OK TO SUBMIT: NO**. Historical rasters remain downloadable only as research/audit artifacts where a page explicitly labels them that way. Do not use a filename, old selector receipt, score projection, or green badge from an earlier parallel lane as clearance.

## Nine-site executive table

Scores below are **USER-REPORTED / UNVERIFIED** values transcribed from the supplied brief and pinned evidence; none is an organizer receipt. No new candidate's leaderboard score is estimable from this repository. All nine historical files fail pairwise uniqueness against at least one of the other eight in the pinned pairwise audit. The best number in this set is GEMSDOE32's 0.2778, but its raster is part of a nested/shared-dot family, not a unique new submission.

| Site | Historical file (research reference only) | Reported value | New-file estimate | Unique vs other eight? | Action |
|---|---|---:|---|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 | Not estimable | **NO** (max directed overlap 100%) | Do not resubmit; already public |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 | Not estimable | **NO** (100%) | Do not resubmit; shares the nested dot family |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 | Not estimable | **NO** (98.02%) | Do not resubmit |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 | Not estimable | **NO** (100%) | Do not resubmit |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 | Not estimable | **NO** (100%) | Do not resubmit; decoded dot set matches GEMSDOE25 |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 | Not estimable | **NO** (100%) | Do not resubmit; nested sibling family |
| GEMSDOE32 | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | **0.2778** | Not estimable | **NO** (100% max vs other eight in stored pairwise audit; literal fleet check also fails) | Best historical claim in this set, but do not resubmit |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 | Not estimable | **NO** (99.71%) | Do not resubmit |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 | Not estimable | **NO** (97.58%) | Do not resubmit |

The pairwise percentage column is the share of a row file's dots within 3 px of at least one other focus-site file, from the stored 2026-10-29 pairwise receipt. The 2026-10-31 matrix additionally records pin/hash mismatch for GEMSDOE32 and GEMSDOE33; those two current copies must not be described as owner-pin-matched. This scope is the nine pinned files, not a complete current global registry. Both reasons strengthen the do-not-resubmit decision; they do not establish organizer acceptance or score.

## Why the GEMSDOE32 0.2778 claim is highest in the supplied nine

The evidence-backed explanation in this checkout is a **pruning/metric effect**, not proof of a better geologic detector. The pinned byte comparison records the GEMSDOE32 B2 mask as a subset of the denser D2.8 family: it removes 6,436 dots near mapped faults, adding no new target locations. Under the competition's distance-weighted Tversky form, a low-credit emitted dot still adds false-positive mass; removing those dots can increase the score even if true-positive credit barely changes. This is consistent with the reported ordering: GEMSDOE32 0.2778 > GEMSDOE36 0.2750 > GEMSDOE28 0.2710 > GEMSDOE31 0.2708.

**Qualification:** the 0.2778 is still USER-REPORTED / UNVERIFIED here. The byte-level subset finding and metric algebra explain a plausible mechanism, but do not verify the hidden score, causality, private labels, or a higher score for a new raster. No valid local conversion from an experimental holdout DTI to an organizer leaderboard score is established. The current public official leaderboard page read on 2026-10-31 shows rank 1 at 0.4544; this is a public leaderboard observation, not a receipt for any local file or a private-round score.

## Ranked, untried hypotheses (qualitative only; no experiment authorized)

These proposals are recorded as **UNTRIED in the local experiment record**, not as guaranteed novel against every outside repository. Their ranking is a qualitative priority, not a numerical score forecast. All use the competition's stated feature families, so no new external dataset is required to define them. The cached stack itself is absent in this checkout, so none can be run here now.

| Rank | Hypothesis and layers | Physical signature | Why target uncatalogued faults | Difference from prior local methods | Named mimic | Expected DTI / cost |
|---|---|---|---|---|---|---|
| 1 | **Block-fitted terrain-residual gravity edge** — bands 13 `iso_grav_anom`, 11 `iso_grav_anom_vg`, 12 `det_elev`, 19 `det_elev_slope` | Fit label-blind relief/trend response within the training spatial block; detect signed, persistent residual-gravity edges at predeclared 300–900 m scales; evaluate contour/shoreline-aligned and shifted-block nulls | A buried density step may continue beneath alluvium past a mapped surface scarp; removing terrain-correlated response could expose it without using fault labels | Unlike H1's signed gradient parity and B4's flank step, it estimates a spatially blocked terrain nuisance response and tests signed residual persistence. It is related to earlier topo/gravity work, so lane distinctness requires approval | Unfaulted sediment–bedrock contact, playa/shoreline edge, survey/interpolation seam | Medium qualitative potential; medium cost. **Blocked:** missing cache, no assigned method paragraph, previous topography/gravity family needs lane-distinctness ruling |
| 2 | **Strain-regime transition aligned with a persistent magnetic edge** — bands 7 `geod_shearrate`, 8 `geod_dilaterate`, 2 `rtp`, 3 `tmi_hg` | Cross-scale strain sign/axis change co-located with a persistent magnetic edge; test both orientation and phase-randomized/shuffled-strain nulls | A covered strand near a strain-regime boundary may localize slip without surface expression; a persistent magnetic discontinuity supplies an independent subsurface boundary | Earlier K2/K3 feature lists omitted strain channels; the completed S1 did use strain/seismicity channels but did not establish this preregistered cross-family interaction as a distinct winning mechanism. It is not safe to claim broad novelty | Geodetic interpolation boundary, flight-line levelling or an intrusive/lithologic contact | Low–medium qualitative potential; medium cost; potentially high confounding |
| 3 | **Depth-concordant conductivity/gravity boundary** — band 17 `cond_surf`, band 11 `iso_grav_anom_vg`, plus a verified conductive-base-depth band only if its mapping is authenticated | Test whether a conductivity-gradient front and vertical gravity edge co-locate with a physically consistent depth discontinuity, using cross-shift and basin/range nulls | A concealed fault may juxtapose conductive basin fill with basement and not produce a surface scarp | Tests depth concordance, not a conductivity amplitude or raw gradient. Related conductivity saddle ideas exist in previous slates and a GW-NFS variant has negative evidence; therefore only the *depth-concordance* component remains a possible distinction, not the broad conductivity idea | Saline playa margin, aquifer boundary, EM inversion seam, lithologic contact | Low–medium qualitative potential; medium-high cost; **not viable until band semantics and source provenance are verified** |

The official problem description confirms that training features include conductivity/depth, detrended elevation/slope, strain, gravity, magnetics and earthquake-density families. The competition data tab remains login-gated in this environment. USGS 3DEP offers free 1 m DEM products where coverage exists, but this review did not verify tile coverage for the exact competition footprint, so no 1 m DEM hypothesis is promoted as currently obtainable for this run.

## Repository review: defects fixed and limitations

### High-severity inconsistency fixed

The checkout had mutually contradictory "current" statuses: root `index.html` and `docs/release.html` pointed to a green HALO approval; the prior HALO receipt's own literal uniqueness block said `unique: false` and `stop_required: true`; `docs/release-gbm.html` also called a candidate cleared despite a >70% one-sided overlap; K10's selector relied on excluding the lattice. The selector/release logic did not satisfy the current user-supplied literal protocol. The generated release and desk banners now say **NO**, explain the stop, and label remaining download links research-only. Historical receipts have not been erased or rewritten.

The browser smoke test had an outdated expectation: it waited for `/docs/index.html` after visiting `/`, while root redirects to `/docs/release.html`; this caused a 30-second timeout. It will be updated to test the actual current route and then explicitly open the historical desk.

### Data and reproducibility limits

- `.cache` and `data/` contain no competition data or feature stack in this checkout. No hide-and-recover rerun, feature-alone leakage canary, new candidate generation, or TIF validation against organizer template can be performed here.
- The competition data page requires participant authentication. Public owner mirrors and pinned repo blobs are not organizer-authenticated data.
- Nine-site uniqueness receipts are dated and limited to pinned references. Two 2026-10-31 copies (GEMSDOE32/33) do not match the pin hashes. The 473/488-raster scans are not an organizer-complete registry; one malformed/non-grid test raster also needs a documented policy ruling, not silent omission.
- Score projections in old pages depend on an assumed hidden-truth transfer coefficient. They are projections, never scores, and cannot be used as proof of superiority.
- The portal's earlier `[0, 1]` error is not directly reproducible without the organizer submission endpoint. A local range/NaN check establishes only saved-byte properties, not organizer acceptance.

## Checks run

- `.venv/bin/pytest -q`: **302 passed, 10 skipped**, 101 Rasterio `PendingDeprecationWarning`s; 98 subtests passed.
- `npm test`: **3 passed**.
- `npm run test:site`: **9 passed**.
- `npm run test:browser`: initially failed due to the stale root-route expectation; this review fixes that test and reruns it in final verification.
- `build_site.py`, `build_field_notes.py`, `build_audit_site.py`, `build_hk3_pages.py`, `build_release.py` and `build_release_page.py` regeneration/checks are run in the final pass.
- `audit_public_downloads.py --check`: **PASS_RESEARCH_ONLY_PLUS_RELEASE** before the fix. That old label itself was misleading because its old exclusion rule called a release approved; the current UI now follows the literal stop. Do not interpret that inventory label as competition authorization.
- `assess_release.py`: **negative**, `slot_authorized: false`, with missing lane assignment, missing authenticated template, duplicate surface stop, incomplete registry and no final-dot measurement.

## Three-pass closeout

1. **Pass 1 — implement and verify:** reconciled current release pages with the literal uniqueness rule; retained research downloads but removed their upload endorsements; recorded the nine-site table, unverified score status, and untried hypothesis ranking.
2. **Pass 2 — review bugs/edge cases:** identified the old lattice-exemption mismatch and multiple parallel candidate badges; found the browser test was waiting on a stale route. Also checked missing caches, incomplete registry provenance, unverified template authority, and non-comparable site holdout results.
3. **Pass 3 — request reconciliation:** no new TIF is generated because the literal surface gate and missing lane/data prerequisites block before placement. No score is projected as an observed score; no weekly slot is touched. A negative result is the current deliverable.

## Trusted links for manual review

- [Official problem description, features, metric, submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official competition data page (participant login)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DOE/NLR official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [USGS 3DEP elevation download/access FAQ](https://www.usgs.gov/faqs/what-types-elevation-datasets-are-available-what-formats-do-they-come-and-where-can-i-download)
- [USGS 3DEP coverage-status FAQ](https://www.usgs.gov/faqs/what-coverage-3d-elevation-program-3dep-dems)
- [GBCGE INGENIOUS project](https://gbcge.org/current-projects/ingenious/)

## Next work

1. Keep the no-submit status until the protocol owner provides a single method paragraph / lane assignment, or the protocol owner formally changes the literal 70% rule. Do not evade the stop by placing dots in lattice gaps.
2. Restore authenticated organizer `training_features.tif`, `labels.tif`, and `sample_submission.tif` in the local ignored data path; hash-pin provenance and resolve the official exterior/nodata convention.
3. Obtain a current complete registry and set a frozen, like-for-like holdout incumbent under the same evaluator and folds.
4. Only after those prerequisites: test the top preregistered hypothesis with the shared cached stack, `evaluate_holdout.py`, `submission_writer.py`; whole-segment buffered holdout, visible-only catalogue features, pixel-exact masking, pooled DTI, 95% spatial CI, feature-alone canaries; stop at 3 experiments or 2 hours.
5. A TIFF may only be marked **OK TO DOWNLOAD AND SUBMIT** after exact saved-byte validation, literal pre-placement and final-dot uniqueness, a positive paired holdout improvement over the frozen incumbent, and an independent selector decision. Never upload or select a weekly slot automatically.
6. Refresh official source snapshots before publishing any current leaderboard claim. Preserve all scores as USER-REPORTED / UNVERIFIED unless linked to an organizer receipt.

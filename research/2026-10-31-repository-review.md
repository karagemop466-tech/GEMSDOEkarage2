# Repository review — 2026-10-31

## Outcome

**Negative / no submission approved.** This session reviewed the current checkout, regenerated-page consistency, saved release evidence, and automated tests. It did not fetch new organizer pages, authenticate competition files, run a geological experiment, create a TIFF, or consume a competition slot. The 2026-10-30 official-page observation remains dated history; it is not represented as a current 2026-10-31 leaderboard reading.

No code defect requiring a scientific-workflow change was found in the checked gates. Do not infer from passing software tests that a raster has scientific validity or organizer acceptance.

## Findings and priority

1. **Hard stop remains correct:** the release assessor returns `negative`, with `slot_authorized: false`. Missing prerequisites include an assigned method lane, authenticated organizer inputs/template, pre-placement registry clearance, matched-fold holdout superiority with paired 95% CI, leakage checks, complete registry, and byte-level validation.
2. **No approved TIFF exists.** `scripts/audit_public_downloads.py --check` reports `PASS_RESEARCH_ONLY`, ten inventoried artifacts, and `downloadable_approved_submission: null`. Existing downloads remain research-only. Do not rename, jitter, sparsify, or otherwise alter these files to evade the literal duplicate gate.
3. **Historical nine-site comparison:** GEMSDOE32's 0.2778 is the largest value in the supplied nine-site historical list, but it remains `USER-REPORTED / UNVERIFIED`, not an organizer receipt. The report's nine-site geometry audit says all nine fail the literal registered-raster proximity rule. The next-file leaderboard estimate is **Unavailable**; a catalogue holdout has not been calibrated to hidden expert labels.
4. **Scientific slate exists but is not an assigned lane:** `research/2026-10-29-focus-audit-and-next-hypotheses.md` and `research/2026-10-28-next-lane-slate.md` contain ranked proposals. Most promising pending all policy/data prerequisites is the topography-conditioned *signed residual gravity edge* with contour/shoreline null; its score benefit is unmeasured, and it is not authorized here. Prior B4 work shares the broad topography/gravity ingredient family, so a coordinator must rule on lane distinctness before any run. Do not claim fleet-wide novelty.
5. **Research provenance limitation:** pinned owner mirrors are not authenticated organizer data. The public DrivenData data page has previously redirected to login; the official format/template and the cause of the user's `[0,1]` portal error remain unverified from an organizer receipt. The internal synthetic format fixture is explicitly not an official template.
6. **Feed limitation:** the website's source feed tracks public GitHub metadata, not live DrivenData results. The last saved official leaderboard observation is dated 2026-10-30. It must not be presented as current on 2026-10-31.
7. **Maintainability:** the generated summary/pages are kept in sync by scripts; source evidence and generators—not generated HTML alone—are authoritative inputs. Research and release gating are intentionally fail-closed.

## Test and integrity evidence

Executed in a temporary local virtual environment from the pinned requirements:

- Python: **257 passed, 8 skipped**, 98 rasterio deprecation warnings, 98 subtests passed.
- Node feed: **3/3 passed**.
- Node site: **8/8 passed**.
- Browser smoke: **6/6 checks passed** across 1440, 390, and 320 px; includes research-only download hash, navigation, feed fail-safe states, and no overflow.
- `build_site.py --check`, `build_field_notes.py --check`, `build_audit_site.py --check`, `build_hk3_pages.py --check`: passed.
- `audit_public_downloads.py --check`: `PASS_RESEARCH_ONLY`; no approved submission.
- `assess_release.py`: `negative`, `slot_authorized: false`.

Python warnings are non-fatal `PendingDeprecationWarning`s from Rasterio's Affine multiplication in tests. No external data were downloaded into the repo. Temporary `.venv` and Node dependencies are ignored build/test dependencies.

## Ranked candidate queue (proposals, not results)

The queue below is not a permission to run any experiment. It summarizes the existing preregistered proposal slate; estimated DTI gain is **qualitative only**, not a numerical projection.

| Priority | Proposal / input signature | Why it could target uncatalogued faults | Main mimic | Relative expected benefit / cost | Gate |
|---|---|---|---|---|---|
| 1 | Block-fitted terrain-residualized signed gravity-gradient edge (gravity anomaly/vertical gradient plus detrended elevation/slope); contour-aligned null | Density discontinuity may persist beneath alluvium beyond mapped surface scarps | Unfaulted sediment-bedrock boundary or shoreline/terrace | Highest qualitative priority / medium cost | Existing B4 family overlap; lane owner must resolve; mirror bands are unauthenticated |
| 2 | Conductivity-Hessian saddle across an independently located gravity break | Buried juxtaposition of conductive units may mark covered structure | Saline playa margin or inversion seam | Medium / medium-high cost | Requires metadata/authenticity check; do not use ambiguous band 15 |
| 3 | Coarse strain-regime change interacting with persistent magnetic edge | Regional strain boundary could contextualize a covered strand | Interpolation seam or intrusive contact | Low-medium / medium cost | Must beat magnetic-only and shuffled-strain null |
| 4 | Seismicity sidedness across independent gravity residual edge | Active uncatalogued structure may be associated with asymmetric seismicity | Induced/mining seismicity or smoothed-density artifact | Low / low-medium cost | Require shuffled-seismicity null and verified layer metadata |

All four rely on competition feature bands available only in an owner-mirrored stack in this session; no external dataset was newly required. They cannot be considered validated or viable for a submission until organizer inputs are authenticated and a single method paragraph is assigned. If that stack is rejected, candidate 4's public seismicity alternative would need a specific official catalog such as USGS ComCat, with spatial/temporal coverage and access verified before proposing a test; this review did not check/download it.

## Three-pass closeout

- **Pass 1 — implement and verify:** no new scientific implementation was justified without an assigned lane or prerequisite data. Re-ran page generators/checks, artifact audit, and release assessor; verified the existing executive summary already presents the nine-site table and explicit no-submit state.
- **Pass 2 — bug/edge-case review:** ran Python, Node, site, and browser tests. All passed; identified stale-currentness risk explicitly: the newest saved leaderboard observation is 2026-10-30, not 2026-10-31. No release approval is inferred from test success.
- **Pass 3 — original-request reconciliation:** checked the demanded unique TIFF, estimate, validation, and slot requirements against evidence. None can honestly be claimed; no new TIFF or estimated score was fabricated. The executive summary marks all nine historical files research-only, all uniqueness checks negative under the literal recorded rule, and estimates unavailable. Keep the current `NO / DO NOT SUBMIT` status until the evidence gates actually pass.

## Official references for human review

These are source links in the project reference set; they were not fetched anew during this review:

- [Competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem, metric and submission specification](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition data tab (participant login)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)

## Next work, in order

1. Assign one and only one lane/method paragraph and resolve B4/topographic-gravity conflict plus the literal registry stop with the protocol owner.
2. Make authenticated organizer training inputs and exact submission template available through authorized access; pin hashes/provenance and resolve exterior/NaN behavior and the portal range complaint.
3. Establish a complete current registry and frozen same-fold incumbent.
4. Only then use the shared cached stack, evaluator, and writer; whole-segment buffered hide-and-recover; pixel-exact visible fault masking; per-feature leakage canaries; pooled HOLDOUT-DTI with evaluator/version, withheld-positive count, and spatial 95% CI. Respect the three-experiment/two-hour cap.
5. Promote only if the holdout comparison and pre-placement/final uniqueness gates pass; then independently validate exact organizer CRS/shape/transform, footprint, no NaNs inside, values in `[0,1]`, and obtain selector approval within the account quota. Never automate slot selection or upload.
6. Refresh the public leaderboard from the official page before making any current-board claim; retain dated source evidence.

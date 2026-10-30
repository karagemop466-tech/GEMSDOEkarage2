# Repository review — 2026-10-30

**Branch:** `arena/72509f87-gemsdoekarage2`
**Scope:** repository safety, nine-site summary, existing hypothesis slate, release/uniqueness evidence, tests and generated website.
**Decision: NEGATIVE. No TIFF in this repository is approved to download and submit.**

No experiment, new raster, upload, organizer confirmation or submission-slot action was performed. The prompt does not provide an assigned method paragraph, and the prior protocol records a hard stop against the available lattice witness. Generating a new TIFF now and describing it as unique or ready would be unsupported. This is not an assertion that a scientifically unique prediction is impossible in principle; it is the fail-closed result for the evidence available here.

## Executive decision on the nine named sites

The historical figures below are copied from the user-supplied results and are **USER-REPORTED / UNVERIFIED**, not organizer-confirmed receipts. The repository's dated geometry audit reports all nine files above the protocol's 70% proximity limit against its available GEMSDOE13 lattice witness. The witness is not evidence of complete current-registry coverage, and these measurements do not validate geology or estimate a new leaderboard score.

| Site | Best supplied historical file | Reported value | New-file leaderboard estimate | Unique under recorded lattice gate? | OK to download and submit? |
|---|---|---:|---|---|---|
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | 0.2778 USER-REPORTED / UNVERIFIED | Unavailable | No — 99.91% within 3 px | **NO** |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 USER-REPORTED / UNVERIFIED | Unavailable | No — 99.92% | **NO** |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 USER-REPORTED / UNVERIFIED | Unavailable | No — 99.91% | **NO** |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 USER-REPORTED / UNVERIFIED | Unavailable | No — 99.92% | **NO** |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 USER-REPORTED / UNVERIFIED | Unavailable | No — 99.91% | **NO** |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | No — 99.92% | **NO** |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | No — 99.92% | **NO** |
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 USER-REPORTED / UNVERIFIED | Unavailable | No — 99.92% | **NO** |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 USER-REPORTED / UNVERIFIED | Unavailable | No — 99.92% | **NO** |

**Best historical candidate among the supplied claims:** GEMSDOE32, 0.2778 USER-REPORTED / UNVERIFIED. This only answers which reported value is largest; it is not a recommendation to submit it. The repository's byte-level forensics suggest this raster is a thinner subset of the D2.8 family, but neither the reported score nor the reason for it is independently confirmed from a submission receipt and hidden labels. A new score cannot be projected from these historical claims.

## Current repository evidence and user-facing state

- The generated executive summary and front page state **OK TO SUBMIT: NO**, show the nine-site comparison, mark reported values unverified, show estimated score as unavailable and distinguish research-reference downloads from submission files.
- `scripts/audit_public_downloads.py --check` reports `PASS_RESEARCH_ONLY`, nine tracked TIFFs, no unexpected public downloads and `downloadable_approved_submission: null`. This is an artifact inventory/integrity result, not a scientific or official validator pass.
- Published TIFFs are research-only. Some have finite zeros outside the footprint while prior source evidence describes null/NaN outside; the official template has not been authenticated in this environment. The reported portal range error remains unexplained. A local range/grid check cannot establish portal acceptance.
- An earlier draft of [`2026-10-30-repo-review.md`](2026-10-30-repo-review.md) reported a public DrivenData fetch on 2026-10-30 (0.3195 at rank 48). That freshness claim was withdrawn because its evidence card says external official pages were not fetched. The last supported saved observation is 2026-10-29 (rank 1 = 0.4544; 0.3195 = rank 47); neither public snapshot is a score for a repository raster, private-round result, HOLDOUT-DTI or local candidate estimate.
- **Correction to the separate same-day audit:** it initially treated `reference/gemsdoe36/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif` as an organizer format sample and inferred a likely geotransform/exterior mismatch. Its companion JSON explicitly says it is synthetic QA, not an official submission, and does not use official template bounds. We independently read the local TIFF metadata: it is 32×48, EPSG:32611, transform origin (400000, 4400000), NaN nodata; the shipped HK3 raster is 3730×3292, EPSG:32611, transform origin (243350, 4508550), no nodata tag. These differences are LOCAL CHECKS against a synthetic QA artifact only. They do not establish the organizer template grid or explain the portal range error. The error's cause remains unknown.
- The owner-mirror feature stack, sample and shared-template material are not organizer-authenticated. The competition training bundle is absent at `data/`; no hidden expert labels or organizer submission receipt are available. Eight integration tests that need optional pinned owner-mirror/shared inputs were skipped.
- The repo already contains four ranked, falsifiable, not-yet-tested hypotheses in [`2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md). Candidate 1 is a blockwise, terrain-conditioned signed residual-gravity edge with shoreline/contour controls; sediment–bedrock contacts or lake-terrace risers can mimic it. These are qualitative proposals, not evidence of novelty across all sibling sites, predicted scores, or approval to run. The slate records data/access caveats and distinguishes implementation status from the broader ecosystem.

## Three-pass review

### Pass 1 — implementation and verification

Read `README.md`, `AGENTS.md`, `SUBMISSION_STATUS.md`, the generated executive summary, the release/selector logic, public-download inventory, the lattice audit and the ranked hypothesis slate. Confirmed the release is fail-closed and no candidate or upload has been authorized. Updated the README's opening status, which had described a different Arena branch/session and stale test counts, to link this current review and its evidence card. No generated site page needed regeneration because its content is generated independently from README.

### Pass 2 — defects, assumptions and edge cases

Reproduced the repository checks from a clean Python virtual environment made from the committed `requirements.lock.txt`; installed JavaScript dependencies with `npm ci --ignore-scripts --no-audit --no-fund`. No source-code defect was exposed by the checks. Notable constraints remain:

1. Eight integration tests skip without pinned mirror/shared inputs. Passing unit tests do not substitute for those checks.
2. No `data/` directory exists, and the organizer-gated competition bundle could not be independently verified here.
3. The 2026-10-29 leaderboard snapshot is not current. A purported 2026-10-30 fetch/rank claim was withdrawn because its same-day evidence card states no external official page was fetched. Refresh the official leaderboard from an accessible source before setting any current target.
4. The lattice test is a protocol rule and available-witness comparison, not the organizer's score metric. Its result cannot establish complete registry coverage or official acceptance.
5. The user's demand for a unique downloadable TIFF conflicts with the extant protocol stop and the current null/NaN/template uncertainties. Creating one anyway would invite an unsupported submission claim.

Checks run:

- Python: **256 passed, 8 skipped, 0 failed**, 98 warnings and 98 subtests passed.
- Node feed tests: **3 passed**.
- Site tests: **8 passed**.
- Browser smoke: passed at 1440, 390 and 320 px; download remained explicitly research-only; exact hash and viewport checks passed.
- `audit_public_downloads.py --check`, `build_hk3_pages.py --check`, `build_audit_site.py --check`, and `assess_release.py`: passed; selector verdict was negative.
- Python compileall, shell syntax checks and `git diff --check`: passed.

The 98 Rasterio `PendingDeprecationWarning`s are non-failing warnings from the installed dependency. Eight skips are explicitly mirror/shared-input-dependent, not silently treated as passes.

### Pass 3 — original request and completion boundary

| Requirement | Outcome |
|---|---|
| Review the nine named sites and identify largest supplied result | Done above; GEMSDOE32's 0.2778 is USER-REPORTED / UNVERIFIED. |
| Estimate new submission score | Unavailable. No validated calibration to hidden expert labels exists; no projection is called a score. |
| Verify uniqueness and make a TIFF explicitly safe to submit | Not achieved. Existing artifacts remain research-only; no new TIFF created. |
| Provide 3–5 pre-experiment hypotheses | Four ranked proposals already exist in the linked slate; none was assigned or tested in this review. |
| Spatially blocked holdout, leakage canaries and paired improvement | Not run; no HOLDOUT-DTI, 95% CI, withheld-positive count or feature AUC is claimed for this review. |
| Use shared cached feature stack/evaluator/writer and honor budget | No experiment run, so no private implementation, experiment budget or slot used. |
| Provide a one-click uploadable file | Deliberately not provided. Site links are explicitly research-only and there is no approved submission to download. |
| Update project README and three-pass review | README now points here; this review records the three passes and exact test results. |
| Create PR and merge to main | This work is limited to the assigned Arena branch. PR creation is requested after review; merging would alter `main`, so it is not performed by this local review. |

## Source links and evidence scope

Official references to check manually:

- [DrivenData competition overview and rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem description and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — time-varying; not refreshed in this review
- [Official data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) — participant login required per repository evidence
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [NREL/DOE challenge rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN survey](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [EPSG:32611](https://epsg.io/32611)

Repository evidence read for this review includes `evidence/official-review-2026-10-29.json`, `evidence/lattice-gate/summary.json`, `evidence/public_downloads_audit.json`, `evidence/nine_site_best_files_audit.json`, and `evidence/geometry-audit.json`. These records preserve their historical date and authority limits. No new official-source retrieval is claimed.

## Next work and limitations

1. Do not download/submit any current TIFF as an official prediction. Keep the page's no-submit warning and research-only labels.
2. Before scientific work, a coordinator must assign exactly one method paragraph/lane; first reconcile the mandatory all-registry duplicate rule with the dense lattice stop. No exception or edge-hole placement should be used to bypass it.
3. Secure organizer-authenticated sample/template and training data through authorized competition access; establish the outside-footprint convention, matching grid, score version and actual portal validation path. Do not assume the owner mirror is official.
4. Refresh official public leaderboard observations only when the source is actually accessible, record timestamp/rank/identity and never use those rows as local score estimates.
5. If protocol conditions become satisfiable, use the shared cached stack/evaluator/writer, whole buffered segment holdout, visible-fault-only feature construction, exact masking, pooled DTI and feature-alone leakage tests; compare against a frozen same-fold incumbent with a paired 95% CI. Stop by three experiments or two hours.
6. Require pre-placement surface uniqueness and final-dot uniqueness against a complete, hash-pinned registry; then run the official-grid validator and an independent selector. A research-gate pass does not choose a real slot or verify account quota.
7. The current source-data gap is not repairable by public-context research alone: no authenticated labels, template, receipt or private leaderboard outcome is available in this checkout. No winning-score claim is justified.

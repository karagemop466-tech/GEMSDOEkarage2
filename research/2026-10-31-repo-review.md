# Three-pass repository review — 2026-10-31

**Branch:** `arena/0450136c-gemsdoekarage2` (based on `26a677c`)

**Decision: NO APPROVED SUBMISSION.** No new raster, geological experiment, score estimate, upload, or submission-slot selection was made in this review. The repository does contain an older H-F TIFF, but its own evidence does not establish protocol-compliant HOLDOUT-DTI, a 95% CI, full-registry uniqueness, or strict format compliance. It is research-only; **do not submit it**.

This report is the current review requested by the project README. The consolidated prompt remains there and should be read at the start of future work.

## Executive answer

- **Best supplied historical claim:** GEMSDOE32's `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` at **0.2778 USER-REPORTED / UNVERIFIED**. The repo's byte audit finds its 37,654-dot mask is a strict subset of the GEMSDOE25 D2.8 reference: it removed 6,436 dots and added none. This gives a plausible metric-based explanation—removing low-yield predictions can reduce false-positive mass—but does not establish why the organizer assigned the reported value, because there is no authenticated, hash-linked submission receipt or hidden truth.
- **The user's reported 0.3195 is not the highest value in the latest saved official-page observation.** The last saved public leaderboard snapshot is dated **2026-10-30**, when it records 0.4544 at rank 1 and 0.3195 at rank 48. Those are dated **ORGANIZER-PUBLISHED PUBLIC LEADERBOARD SNAPSHOT** values, not scores for these local files. The official page was not refreshed on 2026-10-31; do not call the 2026-10-30 observation current.
- **No valid estimated competition score is available** for any new raster. A catalogue-based spatial holdout has not been calibrated to the expert-hidden competition set. Historical site values remain unverified owner/user reports.
- **None of the nine pinned site files is suitable to submit under the written uniqueness rule.** The pinned-byte pairwise check finds each site file has 97.58–100.00% directional three-pixel overlap with at least one other of the nine. Separately, all nine fail the dated 13GEMSDOE lattice-witness gate at 99.9097–99.9234% of dots within three pixels (limit: 70%). Those are geometry checks, not scores, and the witness is not proof of a complete live registry.
- **The H-F TIFF is downloadable for research only, not for submission.** Its SHA-256 is `e9ea035c8d12d848807c3b71875c8031ca8b49b33f21150ac62e4e7f67c04224`. The checked-in TIFF is finite in [0,1] and matches the pinned owner-mirror grid, but the strict local format audit fails the NaN-exterior check. Its stored 0.018385 is a fixed-field proxy—not valid HOLDOUT-DTI—and its interval is a four-fold range, not a 95% CI. Its fault-proximity feature has AUC 1.0, a leakage-canary failure. Only seven local raster references were compared, so uniqueness versus the nine requested sites and the current registry is **unknown**.
- **The nine-site GitHub metadata feed was refreshed at 2026-10-31 00:45 UTC.** All nine repositories had a different `main` HEAD from the pinned review references. This proves only a metadata change: no current-head TIFF or score was audited. The DrivenData leaderboard and login-gated data tab were not contacted in this review.

## Nine-site executive scorecard

All values in the “reported value” column are **USER-REPORTED / UNVERIFIED** claims from the supplied list and pinned audit; none is an **ORGANIZER-CONFIRMED** file/score receipt. “Estimate” is intentionally unavailable. The files are reference links, not download recommendations.

| Site | Highest supplied historical file | Reported value | New-file leaderboard estimate | Unique among the nine? | Literal lattice gate | Download and submit? |
|---|---|---:|---|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 USER-REPORTED / UNVERIFIED | Unavailable | No; max pairwise overlap 100.00% vs GEMSDOE25 | DUPLICATE_STOP; 99.9218% within 3 px | **No** |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | No; its dot mask is identical to GEMSDOE30 | DUPLICATE_STOP; 99.9161% within 3 px | **No** |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 USER-REPORTED / UNVERIFIED | Unavailable | No; max pairwise overlap 98.0188% vs GEMSDOE24 | DUPLICATE_STOP; 99.9234% within 3 px | **No** |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 USER-REPORTED / UNVERIFIED | Unavailable | No; max pairwise overlap 100.00% vs GEMSDOE24 | DUPLICATE_STOP; 99.9097% within 3 px | **No** |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | No; its dot mask is identical to GEMSDOE25 | DUPLICATE_STOP; 99.9161% within 3 px | **No** |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 USER-REPORTED / UNVERIFIED | Unavailable | No; max pairwise overlap 100.00% vs GEMSDOE24 | DUPLICATE_STOP; 99.9179% within 3 px | **No** |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | **0.2778 USER-REPORTED / UNVERIFIED** | **Unavailable** | No; max pairwise overlap 100.00% vs GEMSDOE24 | DUPLICATE_STOP; 99.9150% within 3 px | **No** |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 USER-REPORTED / UNVERIFIED | Unavailable | No; max pairwise overlap 99.7086% vs GEMSDOE27 | DUPLICATE_STOP; 99.9140% within 3 px | **No** |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 USER-REPORTED / UNVERIFIED | Unavailable | No; max pairwise overlap 97.5781% vs GEMSDOE27 | DUPLICATE_STOP; 99.9176% within 3 px | **No** |

Receipts: [`evidence/focus-profile-2026-10-29.json`](../evidence/focus-profile-2026-10-29.json), [`evidence/uniqueness/nine-site-pairwise-recheck.json`](../evidence/uniqueness/nine-site-pairwise-recheck.json), [`evidence/lattice-gate-audit-2026-10-29.json`](../evidence/lattice-gate-audit-2026-10-29.json), and the site table in [`docs/executive-summary.html`](../docs/executive-summary.html). The uniqueness measurements use pinned bytes, not each site's newest `main` HEAD.

### Why the reported GEMSDOE32 number may be higher

The byte-level observation is stronger than the mechanism inference: the GEMSDOE32 binary dot set is the GEMSDOE25 D2.8 reference minus 6,436 pixels, with no additions. Under the official metric's stated alpha 0.2 / beta 0.8, a simplified independent-pixel calculation says one additional unit prediction with effective hit probability `q` improves an existing DTI `S` only if `q > alpha × S`. At `S = 0.2778`, that toy threshold is about 0.0556. This offers a plausible explanation for why removing low-yield predictions might help.

That algebra is not a model of the complete distance-weighted metric: real predictions interact through the triangular kernel and per-label maxima, and pixels are spatially dependent. More importantly, the 0.2778 claim is not linked to an organizer receipt in the repo. Therefore the pruning relation supports a **hypothesis**, not a causal explanation or a calibrated score estimate. It does not show that the removed dots were false positives or that a newly generated raster will beat 0.2778.

## H-F download decision and evidence correction

A historical H-F raster exists at [`docs/downloads/gemsdoe-hf-alteration-curvature-intersection-20261030.tif`](../docs/downloads/gemsdoe-hf-alteration-curvature-intersection-20261030.tif). The executive summary now links it as **Download for research only** and shows **NO · DO NOT SUBMIT** beside it.

| Check | What the saved evidence says | Decision |
|---|---|---|
| Raster identity | SHA-256 `e9ea035c8d12d848807c3b71875c8031ca8b49b33f21150ac62e4e7f67c04224`; 806,001 bytes | Byte identity is checked locally |
| Local range/grid | Single-band float32; whole array finite and in [0,1]; grid matches a pinned owner mirror | Integrity only; the mirror is not an authenticated organizer template |
| Strict local format | `strict_format_pass=false`; `outside_is_nan=false`; outside cells are finite zeros | **FAIL** against this repo's strict owner-mirror NaN-exterior check. This does not by itself prove what the portal accepts |
| Candidate score | Stored point value 0.018385 is a **fixed-field proxy, NOT valid HOLDOUT-DTI**; its 60,988-positive holdout uses a field that used all catalogue faults for distance. The stored interval `[0.008563, 0.038431]` is a four-fold range, **not a 95% CI** | No protocol-valid score or interval; no leaderboard estimate |
| Leakage | Fault-proximity feature-alone AUC is 1.0 | **Leakage canary FAIL** |
| Uniqueness | Seven local raster references only; maximum absolute Spearman 0.011519 and maximum final-dot overlap 0.617889 within that limited set | **Unknown** versus the nine requested site files and a complete current registry; do not call unique |
| Authorization | Negative verdict; `ok_to_submit=false`; `slot_authorized=false` | **NOT OK TO SUBMIT** |

The audit key `confidence_interval_95` in the historical run card is misleading: its accompanying note says the values are only the minimum and maximum over four folds. This review corrects the interpretation without rewriting the historical run card. The H-F generator also says it follows hide-and-recover, but its code explicitly scores one fixed field whose fault-distance feature used all catalogue faults. That does not satisfy the user's prescribed fold-local feature construction. The previous README's H-F “strict format pass” and “unique” statements were incorrect and have been corrected.

The H-F audit says only 7 of its stated 472 registry rasters were locally available. The repo's 2026-10-29 nine-repository manifest has 489 rows and explicitly says it is not a globally complete registry; another historical combined snapshot lists 472 rows; the dated 440-reference uniqueness audit has 438 comparable entries and two not comparable. These are different, dated scopes—not a reconciled current registry. This is why the H-F uniqueness field is now **unknown**, not true.

## Three review passes

### Pass 1 — inspect and verify the current project

- Read `README.md`, `AGENTS.md`, `SUBMISSION_STATUS.md`, the source-feed and registry manifests, the generated public pages, the H-F audit/run card, the download inventory, and the existing three-pass and hypothesis notes.
- Confirmed the worktree has no `data/` or `.cache/competition_data/` inputs. The official DrivenData data page and problem/leaderboard pages were not contacted in this review; the repository's prior record says the data tab redirects to login. Do not claim current official data access or a newly refreshed competition score.
- Refreshed only GitHub `main`-branch HEAD metadata, using the GitHub API allowlist. At **2026-10-31 00:45 UTC**, all nine named repositories differed from their pinned historical heads; see [`docs/data/monitor.json`](../docs/data/monitor.json) and [`docs/field-notes/data/source-feed.json`](../docs/field-notes/data/source-feed.json). This is not a TIFF, score, registry, or receipt audit.
- Re-read the latest available official public-board capture: it is dated 2026-10-30, not current for 2026-10-31. The supplied nine-site scorecard is historical and owner/user reported. No new-file score estimate can be defended.
- Found the H-F result is not a safe submission candidate and that the current site inventory omitted it from the visible “every published TIFF” table. The H-F TIFF was present in `docs/downloads/` and the download inventory, but absent from the 2026-10-29 lattice profile. See Pass 2 for the fail-closed correction.

### Pass 2 — correct bugs, unsafe claims, and edge cases

1. **Corrected H-F status.** The public executive summary lists H-F, links the TIFF only as research-only, says uniqueness is not established, and states why its proxy, leakage canary, and strict local format checks fail. The builder now verifies that every TIFF in the saved-download inventory is represented by either the dated lattice profile or the explicit H-F incomplete-check row.
2. **Removed unsupported uniqueness=true.** `docs/data/focus-sites.json` now records H-F uniqueness as `null` / `UNKNOWN_INCOMPLETE_REGISTRY`, not `true` from seven local comparisons.
3. **Retired unsafe H-F/H-G command-line prototypes.** Their direct execution now stops before loading data or writing a TIFF. H-F is retained as historical evidence only. H-G has no checked-in TIF/run-card evidence, so this repo no longer treats it as a completed experiment.
4. **Clarified historical audit scope.** The site no longer calls the 440-reference snapshot globally “full”; it states that two of 440 entries were not comparable and that the snapshot is not live/global. The 440-, 472-, and 489-row scope discrepancy is explicitly flagged.
5. **Kept release fail-closed.** The inventory remains research-only, the approved-download field remains null, and no slot is selected. The latest public official leaderboard value remains dated 2026-10-30 rather than being misrepresented as a live update.
6. Added regression assertions for H-F visibility/negative status, inventory coverage, uniqueness unknown, and refusal to run the old H-F/H-G prototypes.

### Pass 3 — recheck against the original request

| Requirement | Result |
|---|---|
| Clear executive summary for GEMSDOE24/25/27/28/30/31/32/33/36 | **Present.** Each row identifies its pinned historical file and USER-REPORTED / UNVERIFIED value. |
| Give a candidate leaderboard score estimate | **Unavailable.** No calibrated link from local holdout to hidden-label leaderboard performance exists; the site now says so explicitly. |
| State uniqueness relative to other named sites | **No** for the nine pinned historical files under the saved pairwise audit. The audit is dated and not a live-registry proof. H-F is **unknown**, not certified unique. |
| One-click TIF with obvious submit status | **Research-only H-F link is present and explicitly NOT OK TO SUBMIT.** No submission-ready/approved TIFF exists. |
| Fix the “Predicted values must be in range [0, 1]” error | The saved H-F array is locally finite and in range, but its strict NaN-exterior check fails and its reference template is an unauthenticated owner mirror. Portal cause/acceptance remains unknown; no claim of repair or portal acceptance. |
| 3–5 untried hypotheses before implementing a new lane | Four scoped proposals are ranked below. No new lane was assigned or run. |
| Validate the top hypothesis before spending a slot | No slot was touched. A new experiment cannot be validated here because official inputs/template are unavailable, the cached feature stack is absent, and no method paragraph/lane was assigned. |
| Full automatic inspection and current feed | Local validators/audits are automated; the GitHub branch-head feed was refreshed. There is no authenticated DrivenData score/receipt/quota feed or portal acceptance check. |
| Three passes, sources, irregularities, Core Values | Three passes recorded; source limitations and irregularities are listed below. Maximize P(Win) / Own the Outcome means refusing to label a failed, incomplete artifact as a candidate. |
| New unique TIF | **Not achieved in this review.** The pre-existing H-F TIFF is not a unique approved submission. Creating or relabeling another unvalidated TIFF would violate the prescribed protocol. |

## Verification results

- `.venv/bin/python -m pytest -q`: **266 passed, 4 skipped, 98 warnings, 98 subtests passed**.
- `npm test`: **3/3 passed**; `npm run test:site`: **8/8 passed**; `npm run test:browser`: **6 responsive/navigation/freshness checks passed**, including 1440, 390 and 320 px layouts.
- `.venv/bin/python scripts/audit_public_downloads.py --check`: **PASS_RESEARCH_ONLY**, 10 artifacts, `downloadable_approved_submission: null`.
- `.venv/bin/python scripts/build_hk3_pages.py --check`: **pages up to date**; generated public pages include the explicit H-F research-only row and review/run-card links.
- `.venv/bin/python scripts/bootstrap_research.py` fetched hash-pinned owner mirrors only; output records `input_authority: owner mirrors` and `submission_generated: false`. No official organizer data was downloaded.
- `.venv/bin/python scripts/recheck_hk3.py --check`: **negative**, 45,046/45,108 dots matched the lattice witness (0.9986255 overlap), `slot_authorized: false`.
- No new TIFF was written. The inventory's ten files remain research-only; **none is approved for submission**.

## Ranked hypothesis slate — proposals only, not score forecasts

These describe exact tests not implemented in this repository, not novelty across all GEMSDOE repositories. Rank/cost is qualitative and indicates which experiment might be worth testing if prerequisites are met; it is not a predicted DTI gain. The exact layer labels come from a hash-pinned **owner mirror**, not verified official layer metadata. No candidate below is currently viable without the authenticated training feature stack/labels/template and an assigned method paragraph.

| Expected-improvement rank / cost (qualitative, not a DTI forecast) | Specific layers and physical signature | Why it might detect a catalogue-missing fault | Named non-fault mimic / falsifier | Difference from this repo's implemented work | Data/source status |
|---|---|---|---|---|---|
| 1 · highest relative plausibility of an incremental signal / medium effort | Bands 13 `iso_grav_anom`, 11 `iso_grav_anom_vg`, 12 `det_elev`, 19 `det_elev_slope`. Fit a training-block-only robust, label-blind relief residual, then detect sign-persistent oriented gravity-gradient steps at 300–900 m; include contour/shoreline nulls. | A buried density offset under alluvial cover may extend past the exposed mapped scarp; the residual edge is not tied to catalogue pixels. | Unfaulted sediment–bedrock contact or lake-terrace riser. Fail if contour-following/offset-block controls perform similarly or the residual term adds nothing. | H1 tests opposing elevation/depth gradients; K2 used raw/magnitude features; B4 shares the topography/gravity family but did not use this block-fitted, signed residual plus the specified null. This is a distinct exact test, not a fleet-wide novelty claim. | Uses nominal existing bands, but the cached stack is absent locally and official units/layer semantics were not verified. No extra external layer is proposed. |
| 2 · moderate relative plausibility / medium-high effort | Bands 17 `cond_surf`, 13 `iso_grav_anom`, 18 `iso_grav_anom_hg`. Test a cross-profile conductivity-Hessian saddle aligned across an independently located gravity break; do not use band 15 until its meaning is authenticated. | A covered structure could juxtapose conductive units without a mapped surface trace; the test asks for cross-edge structure, not high conductivity by itself. | Saline groundwater/playa margin or EM inversion seam. Ablate conductivity and check whether anomalies follow survey/inversion boundaries. | H1/K2 used conductivity contrast/raw-gradient features; the exact sign-changing saddle across an independently located break is not implemented here. | Existing mirror bands only; their units/provenance need official confirmation. No external data is available in this checkout. |
| 3 · lower relative plausibility / medium effort | Bands 7 `geod_shearrate`, 8 `geod_dilaterate`, 2 `rtp`, 3 `tmi_hg`. Use strain-regime change only as a coarse interaction with magnetic-edge persistence. | A short covered strand could coincide with a regional strain boundary, while the edge evidence supplies the local structure cue. | Geodetic interpolation seam or unfaulted intrusive contact. Shuffle strain and require incremental improvement over magnetic-only. | K2 excluded strain bands; H1 tested elevation/depth/conductivity. The proposed fold-matched shuffled-strain interaction is not implemented here. Similar strain/seismic ingredients appear in GEMSDOE33 claims, so cross-project novelty is not established. | Uses owner-mirror bands, not official-authenticated units; no new external source is required to prototype, but official layer verification is still a blocker. |
| 4 · lowest relative plausibility / low effort, high uncertainty | Bands 10 `deq_n100a15`, 16 `ieq_n100a15`, 11 `iso_grav_anom_vg`. Compare earthquake sidedness across independent gravity residual edges; include a spatially shuffled-seismicity negative control. | A genuinely active unmapped fault may show asymmetric seismicity around an independently derived potential-field edge; seismicity is contextual, not a 100 m fault locator. | Induced/mining seismicity or density-smoothing artifacts. Stop if shuffled seismicity performs similarly. | No exact flank-signed, shuffled-seismicity test is implemented locally. The GEMSDOE33 user-reported S33 submission uses seismicity/strain ingredients, so do not claim this is a new strategy across sites. | Existing bands only in the owner mirror; no verified units or current official input stack are present. External acquisition was not attempted. |

**Free-data availability check:** the exact inputs required for these four tests are the nine-band competition feature stack, catalogue labels, existing-fault raster and sample template. The latest saved repository observation says the [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) redirects to login; participant-account access was not available or tested in this review. The [USGS GeoDAWN page](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) and [USGS ScienceBase record](https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7) are official public-source targets, but current file availability, licensing, and exact layer equivalence were **not verified**. Outbound access in this sandbox is limited to GitHub/API, npm and Python package hosts. No hypothesis depends on newly downloaded external data; the existing competition layers are available only in unauthenticated owner mirrors in this workspace. Thus no required official data source is verified as obtainable here, and none of the hypotheses is presented as validated or ready to run.

## Remaining work / blockers for the next session

1. Obtain the official DrivenData feature stack, labels, existing-fault raster, and exact sample template through an authorized competition account; record file hashes and confirm the exterior/NoData convention against the organizer sample. Do not treat owner mirrors as official.
2. Resolve the registry identity/scope conflict (440 comparable snapshot, 472 combined snapshot, 489-row filtered manifest) and establish a current, immutable registry that includes all parallel sites. Hash-pin every raster; fail closed on inaccessible entries.
3. Receive/record one explicit method paragraph and lane assignment. Check prior work across all named sites before implementation; preserve the 3-experiment / 2-hour budget. Use only the shared feature cache, `evaluate_holdout.py` and `submission_writer.py`.
4. For the one assigned hypothesis, run buffered whole-segment hide-and-recover, rebuild every catalogue feature from visible faults only, pixel-exactly mask visible faults, run each feature-alone leakage canary, and report pooled HOLDOUT-DTI with evaluator version, withheld count and a genuine 95% CI. A fold range must never be called a CI.
5. Compare to a frozen same-fold incumbent; perform surface correlation/proximity checks before placement and final-dot checks after. If any current registry raster crosses the specified threshold, stop and record a negative result.
6. Independently validate the saved TIFF against the authenticated organizer template and the [0,1] range. Keep format, holdout, uniqueness and portal acceptance as separate gates. Do not use a competition slot until the separate selector authorizes it under the displayed quota.
7. Refresh the DrivenData public leaderboard only through an authorized route; preserve timestamp and never infer a local file's score from a public row. The current automation intentionally refreshes GitHub metadata only.

## Official links retained for manual source review

- [Competition overview and rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem, metric, and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Official data tab (participant access)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Submission rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [USGS ScienceBase GeoDAWN record](https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [EPSG:32611](https://epsg.io/32611)

These links are reference targets; except for GitHub metadata, they were not fetched by this review. See [`docs/evidence/official-review-2026-10-30.json`](../docs/evidence/official-review-2026-10-30.json) for the latest saved official public-page observation and [`evidence/live-source-review-card-2026-10-30.json`](../evidence/live-source-review-card-2026-10-30.json) for its date/scope limitations.

# Three-pass repository review — 2026-10-30

**Branch:** `arena/150a3bda-gemsdoekarage2`

**Decision:** **NO FILE IS OK TO DOWNLOAD AND SUBMIT.** This review generated no candidate GeoTIFF, ran no geological experiment, and used no competition slot. A separate H-F research TIFF was merged from PR #88 after the earlier review; its saved audit is negative and it is not a valid submission. The session card is [`docs/evidence/2026-10-30-repo-review-run-card.json`](../docs/evidence/2026-10-30-repo-review-run-card.json).

This is an evidence review, not an organizer score report. Labels below distinguish `USER-REPORTED / UNVERIFIED`, byte-level `MEASURED` results, `HOLDOUT-DTI`, and organizer observations. **This review produced no new HOLDOUT-DTI or ORGANIZER-CONFIRMED score.** The later-merged H-F proxy is reported separately below and is not protocol-compliant.

## Executive answer

- The highest reported file among the nine requested sites is GEMSDOE32's `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` at **0.2778 USER-REPORTED / UNVERIFIED**. It is not an organizer receipt and must not be treated as a verified score.
- A byte-level audit finds the GEMSDOE32 B2 dot mask is the GEMSDOE25 D2.8 mask with **6,436 dots removed**. The removal is a plausible explanation for a higher reported DTI: the distance-weighted Tversky score can improve if removed dots contribute little marginal true credit but appreciable false-positive mass. The hidden truth, the alleged receipt and the causal score change are unavailable, so **why it scored 0.2778 is not established**.
- A defensible leaderboard estimate for any listed file is **Unavailable**. The local mapped-fault hide-and-recover proxy is not calibrated to the expert-hidden competition labels, and no candidate was evaluated in this review.
- All nine pinned best-file masks fail the user-specified uniqueness stop. Each has **99.91–99.92% MEASURED** within-3-pixel overlap with one registered spacing-lattice witness; the separate nine-file pairwise audit reports **97.6–100% MEASURED** maximum directional overlap with another focus-site file. These are geometry measurements, not scores. The registry snapshot is incomplete, but one applicable witness is enough to stop each file.
- **This review produced no new TIF, and no file is approved for submission.** Main now contains the separately merged H-F research TIFF from PR #88; its saved SHA, strict-format failure, incomplete registry check, invalid holdout proxy, leakage canary and unsupported band mapping are detailed below. It is marked research-only; do not submit any repository file.

The competition target is fault mapping—structures indicative of geothermal resources—not direct geothermal-vent labels. A fault score is not evidence of a vent or resource discovery.

## Nine-site executive table

The table selects the highest value supplied for each of the nine sites. Every historical value in the score column is **USER-REPORTED / UNVERIFIED**, not `HOLDOUT-DTI` and not `ORGANIZER-CONFIRMED`. The file names and audit values are from the pinned historical manifests/receipts; the current independently maintained sites have not been re-audited from their latest heads in this review.

| Site | Highest supplied historical file (research reference only) | Reported value | Estimated leaderboard score | Unique vs the other eight pinned best files? (maximum directed overlap) | Within-3-px overlap vs lattice witness (MEASURED on pinned bytes) | Download and submit? |
|---|---|---:|---|---|---:|---|
| [GEMSDOE32](../docs/focus/GEMSDOE32.html) | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 0.2778 USER-REPORTED / UNVERIFIED | Unavailable | **NO**; max pairwise overlap 100.0% | 99.9150% | **NO — DO NOT SUBMIT** |
| [GEMSDOE36](../docs/focus/GEMSDOE36.html) | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 USER-REPORTED / UNVERIFIED | Unavailable | **NO**; max pairwise overlap 97.6% | 99.9176% | **NO — DO NOT SUBMIT** |
| [GEMSDOE28](../docs/focus/GEMSDOE28.html) | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 USER-REPORTED / UNVERIFIED | Unavailable | **NO**; max pairwise overlap 100.0% | 99.9097% | **NO — DO NOT SUBMIT** |
| [GEMSDOE31](../docs/focus/GEMSDOE31.html) | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 USER-REPORTED / UNVERIFIED | Unavailable | **NO**; max pairwise overlap 100.0% | 99.9179% | **NO — DO NOT SUBMIT** |
| [GEMSDOE33](../docs/focus/GEMSDOE33.html) | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 USER-REPORTED / UNVERIFIED | Unavailable | **NO**; max pairwise overlap 99.7% | 99.9140% | **NO — DO NOT SUBMIT** |
| [GEMSDOE25](../docs/focus/GEMSDOE25.html) | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | **NO**; max pairwise overlap 100.0% | 99.9161% | **NO — DO NOT SUBMIT** |
| [GEMSDOE30](../docs/focus/GEMSDOE30.html) | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | **NO**; max pairwise overlap 100.0% | 99.9161% | **NO — DO NOT SUBMIT** |
| [GEMSDOE24](../docs/focus/GEMSDOE24.html) | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 USER-REPORTED / UNVERIFIED | Unavailable | **NO**; max pairwise overlap 100.0% | 99.9218% | **NO — DO NOT SUBMIT** |
| [GEMSDOE27](../docs/focus/GEMSDOE27.html) | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 USER-REPORTED / UNVERIFIED | Unavailable | **NO**; max pairwise overlap 98.0% | 99.9234% | **NO — DO NOT SUBMIT** |

**Audit scope:** the lattice percentages come from [`docs/evidence/lattice-gate/summary.json`](../docs/evidence/lattice-gate/summary.json), a one-witness stop, not a completeness claim. Pairwise percentages come from [`docs/evidence/uniqueness/nine-site-pairwise-recheck.json`](../docs/evidence/uniqueness/nine-site-pairwise-recheck.json). The latest public site-head metadata differs from the pinned historical revisions; changed GitHub heads do not prove updated scores or file identities. A live leaderboard refresh for 2026-10-30 was not verified in this review.

The public Pages landing page already places the **“OK TO SUBMIT: NO”** decision at the top, includes the nine-site table and individual site summaries, and labels its downloadable historical files as research-only. The generated-pages check is current. Its summary and submission guide are [`docs/index.html`](../docs/index.html), [`docs/executive-summary.html`](../docs/executive-summary.html), and [`docs/how-to-submit.html`](../docs/how-to-submit.html).

## Why the GEMSDOE32 report could be higher (conditional, not causal)

**Measured from saved bytes:** the GEMSDOE25 D2.8 mask equals the GEMSDOE30 mask; GEMSDOE32 B2 equals D2.8 after removing the dots at distance at most two pixels from the mirrored known-fault catalogue. GEMSDOE32 removes 6,436 D2.8 dots. The same decoded-mask relationships are recorded in [`evidence/champion_forensics.json`](../evidence/champion_forensics.json) and [`docs/evidence/champion_explanation.md`](../docs/evidence/champion_explanation.md).

For distance-weighted Tversky, write the pre-pruning score as `T / D`, with `T` the kernel-weighted true credit and `D = T + αF + β(G−T)`. With `α=0.2`, `β=0.8`, and `α+β=1`, deleting predictions raises the score exactly when

```text
D · ΔT < α · T · (ΔT + ΔF)
```

where `ΔT` is lost kernel-weighted true credit and `ΔF` is removed false-positive mass. Nearby dots can be redundant because each truth pixel receives maximum, not additive, kernel credit. Therefore, pruning can improve DTI when the removed dots have low marginal true credit relative to their false-positive cost. B2's catalogue-apron pruning makes this a plausible mechanism for the reported improvement.

**What is not known:** the hidden test labels, file-linked submission-page receipt, exact organizer scorer result, and the removed dots' hidden `ΔT` and `ΔF`. Consequently, the inequality explains a possible mechanism; it cannot be used to reconstruct a score or assert that catalogue-adjacent dots caused the reported gain. B2 is a pruning variant of a shared dotted-ridge family, not evidence of an independent geological detector. It also fails both the literal registry-overlap gate and the strict exterior convention used by the pinned audit.

**Can a new approach beat 0.2778?** It is possible in principle; this repository has no valid result demonstrating that it can. No numeric forecast is justified. The last saved **ORGANIZER-PUBLISHED PUBLIC LEADERBOARD SNAPSHOT (observed 2026-10-29; not a submission-page receipt)** showed **0.4544 at rank 1**; the prompt's 0.3195 was **rank 47 in that same dated snapshot**, not the leader. Those are public leaderboard rows, not file-linked receipts or private-round results. A live 2026-10-30 page check was not performed, so these are not claimed as today's standings. See [`evidence/official-review-2026-10-29.json`](../evidence/official-review-2026-10-29.json) and the [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).

## Preregistered candidate slate — qualitative only, not assigned or tested

The following three exact operator hypotheses were not executed in this checkout. Two have related earlier proposal text; “untried” means the specified transform has no recorded experiment here, **not** that the idea is new to all projects or to the research backlog. The focus-site pages are pinned snapshots; because all nine upstream heads changed, current cross-repository novelty cannot be certified. No strategy is selected for this parallel lane.

Layer names below follow [`evidence/upstream/GEMSDOE31/registry/data_manifest.json`](../evidence/upstream/GEMSDOE31/registry/data_manifest.json), a 2026-10-04 owner-mirror manifest whose own provenance warning says its hashes do **not** authenticate organizer origin. The layer names and band indices are not independently authenticated organizer metadata. All candidates need the competition feature stack; no new external data set is proposed. That stack is absent from the current checkout, the DrivenData data tab requires participant access, and hash-pinned public mirrors do not authenticate organizer origin.

| Rank / qualitative expected DTI potential / cost | Layers and physical signature | Why it could detect a fault absent from the public catalogue | Named non-fault mimic and falsification control | Difference from implemented work and focus-site bests |
|---|---|---|---|---|
| **1 / moderate, high uncertainty / medium-high cost** | Bands 2 `rtp`, 3 `tmi_hg`, 11 `iso_grav_anom_vg`, 17 `cond_surf`, 18 `iso_grav_anom_hg`. Build independent, multi-scale edge networks and score only cross-physics junctions that persist across scale; do not use the fault catalogue to create the candidate surface. | A covered fault transfer zone can juxtapose magnetic, gravity and conductive contrasts even when no lidar-visible trace is in the USGS/INGENIOUS catalogue. Cross-sensor persistence may suppress a single-band edge that is only a lithologic contact. | **Intrusive/lithologic contacts or survey lineaments.** Compare against rotations/translations of one field that preserve its spatial autocorrelation, plus each field alone; any feature with AUC >0.90 on holdout is a leakage stop. | No exact cross-field lineament-junction graph was found in the local scripts. It is distinct in operator from H-A's mapped-fault intersection propensity, K3's local orientation features, HK3 edge-centrality and the listed dotted-ridge/scarp/Poisson/analog-tip bests. Similarity to the GEMSDOE33 analog-tip family remains a novelty risk; only the surface registry audit could decide. |
| **2 / moderate / medium cost** | Bands 13 `iso_grav_anom`, 11 `iso_grav_anom_vg`, 12 `det_elev`, 19 `det_elev_slope`. Fit a robust, label-blind gravity-on-relief relation within training blocks, then seek signed, scale-persistent residual edges and compare against contour-aligned nulls. | A subsurface density boundary can continue beneath alluvial cover beyond the mapped scarp. Removing relief-related response could expose the residual edge rather than rewarding the exposed landform already represented in the catalogue. | **Unfaulted sediment/bedrock contact, shoreline or terrace riser.** Compare with terrain-only and contour-following controls and ablate the relief regression. | B4 already tested paired-flank scarp-step asymmetry with elevation/gravity-related ingredients and H1 used elevation/depth relationships; this exact block-fitted residual/null test is distinct but conceptually adjacent and was previously proposed in `research/2026-10-29-focus-audit-and-next-hypotheses.md`. It is not new to the backlog. |
| **3 / low-moderate / medium-high cost** | Bands 17 `cond_surf`, 13 `iso_grav_anom`, 18 `iso_grav_anom_hg`. Detect a cross-profile conductivity-Hessian saddle aligned across an independently located gravity edge; do not rank high conductivity alone. | A covered fault may juxtapose conductive strata across a density boundary without an exposed scarp. The independent gravity condition is intended to reduce false detections from conductivity alone. | **Saline playa margin or electromagnetic inversion seam.** Ablate conductivity, test the inversion/coverage boundary, and compare with basin-margin nulls. | H1/H-A and supervised models used conductivity or contrast, but no exact conductivity-saddle-at-independent-gravity-edge transform was found in local code. A related proposal already exists in the 2026-10-29 slate, and the exact method is not certified novel to current upstream heads. |

**Ranking is a research prior only.** No DTI value, gain estimate, candidate surface correlation, dot overlap, or output name is claimed for any row. The official data tab is the source required to obtain the authenticated feature stack, but participant login was required in the latest saved access review. No candidate can be called viable until the exact input bytes and template are authenticated or their research-only status is accepted, one assigned lane is present, a compatible frozen incumbent exists, and a pre-placement surface passes the complete registry gate. The 13GEMSDOE lattice witness covers 99.87% of the mirrored footprint within three pixels; the recorded geometry bound makes a normal large dot field fail, and placing dots in rare uncovered cells to bypass the rule is prohibited.

## Tool and data review

### Follow-up audit of the H-F artifact merged from PR #88

This artifact was added to `main` after the original no-experiment review. The present review audited its committed bytes and records but did **not** generate or rerun it. It is a negative research artifact, not an approved submission.

| Gate / evidence | Saved result | Interpretation |
|---|---|---|
| Raster identity | `docs/downloads/gemsdoe-hf-alteration-curvature-intersection-20261030.tif`; SHA-256 `e9ea035c8d12d848807c3b71875c8031ca8b49b33f21150ac62e4e7f67c04224`; 806,001 bytes | This is the measured saved-byte SHA. The incoming README stated `4fe3104c…`; that digest did not match the artifact and has been corrected. |
| Strict format | `strict_format_pass=false`; `outside_is_nan=false`; 7,111,787 finite cells outside the mirrored footprint | **FAIL.** The owner-mirror grid checks do not establish organizer-template provenance. |
| Registry duplicate gate | 7 of 472 rasters; maximum absolute Spearman correlation 0.011519; maximum 3-px dot overlap 0.617889; no duplicate among the 7 | **NOT ESTABLISHED.** 465 entries are absent; local-subset nonmatches cannot be called global uniqueness. The focus-site row now uses `unique: null`, not `true`. |
| Holdout | **0.018385 HOLDOUT-DTI PROXY** using root `evaluate_holdout.dti_weighted_terms` (alpha 0.2, beta 0.8, R=300 m), 60,988 positives; **95% CI: NOT CALCULATED**; four-quadrant fold range 0.008563–0.038431 | **Not promotion evidence.** The output field was fixed while the root helper splits pixels into quadrants; this is not whole-component hide-and-recover or a spatial-bootstrap CI. The run card now records `confidence_interval_95: null` and keeps the fold range separate. |
| Leakage canary | `fault_proximity` AUC=1.0; curvature 0.489928; alteration 0.488236; combined 0.498238 | **FAIL/CANARY.** The feature-alone AUC exceeds the user's 0.90 threshold. The candidate uses distance to all catalogue faults, not a fold-specific visible-fault-only reconstruction. A benign combined AUC does not clear the feature-alone failure. |
| Layer semantics | H-F uses bands 4, 6 and 5 as K, eTh and eU/eTh proxies; the pinned owner-mirror manifest calls these bands `geod_2ndinv`, `tc` and `iso_grav_anom_slope`. Its curvature input band 1 is `mag_anom`, while band 12 is `det_elev`. | The claimed radiometric-alteration/curvature mechanism is unsupported by the mirrored band descriptions and is not authenticated organizer metadata. |

The H-F audit and run card now label the result as a proxy, leave its 95% CI null, state uniqueness as `NOT ESTABLISHED`, and preserve the actual failure reasons. The H-F and H-G generator entry points are disabled fail-closed on this branch and have a regression test; do not bypass the guard. The local H-G annulus prototype has no committed output/run card, so its claimed negative result cannot be independently verified. Prior README text reported two experiments used while the H-F card says one; stop and reconcile this budget before authorizing any further experiment. No experiment was run in this review and no slot was spent.

### Shared holdout / writer identity

- The commit-coherent GEMSDOE32 template pin is in [`registry/template_tools.json`](../registry/template_tools.json). This review fetched only small source files from GitHub into the ignored `.cache`; the evaluator, writer, and matching `src/gems32` helpers matched the pinned SHA-256 values. **No data, experiment, or TIFF was restored or produced.**
- `registry/shared_protocol_assets.json` separately pins a GEMSDOE24 shared-code snapshot. These are different source commits; future work must not mix their modules or silently call both “the template.”
- The root [`scripts/evaluate_holdout.py`](../scripts/evaluate_holdout.py) is a local legacy evaluator. Its split selects pixels in four quadrants and can expose the tail of the same connected fault on the opposite side of a boundary. It is not the pinned shared whole-component evaluator and its four-fold range is not a 95% spatial-bootstrap interval. A new regression test demonstrates this limitation. Historical GW-NFS results from this helper remain labelled as quadrant-block results; their saved values were not recomputed or relabelled.
- The pinned GEMSDOE32 `scripts/evaluate_holdout.py` delegates to its matching `gems32.holdout` module, which withholds whole connected components with a 15-pixel collar. Its writer emits a binary mask from positive input values. Use that coherent pair and its matching inputs for a binary-dot experiment; do not claim the writer preserves soft probabilities. No upstream file was changed and no private evaluator/writer fork was created.

### Data, format, registry and current feed

- `data/` had no official training rasters, labels, sample template or DEM-link list. There is no prepared feature stack. The small pinned code assets restored for inspection are not the feature cache.
- Previous source observations record that the [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) requires participant authentication. Owner GitHub mirrors and Dropbox links are not organizer-authenticated input. Do not infer provenance from matching hashes.
- The official problem page and NLR rules PDF are linked for manual review: [problem / metric / format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) and [official rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf). The prior source ledger is [`evidence/official-verification-2026-10-29.json`](../evidence/official-verification-2026-10-29.json). Their statements were not freshly fetched on 2026-10-30.
- The [DOE GDR INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391) and [USGS GeoDAWN record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) are official source links for later review; no files from those hosts were downloaded in this session. No proposal above depends on new external data, but the existing feature-stack metadata still needs organizer authentication.
- The [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) was not refreshed on 2026-10-30. The website's automatic freshness feed checks public GitHub metadata only; it is not a DrivenData score feed and cannot verify the weekly cap.
- The earlier user-reported portal error, “Predicted values must be in range [0, 1],” is unresolved. The text alone cannot identify the file, pixel or nodata condition that triggered it. Pinned bytes can be locally audited, but no upload receipt or portal acceptance is present. No slot was spent to probe the exterior convention.

### Submission instructions — current release remains locked

1. Do **not** download or submit any repository TIFF as a competition candidate. The current site allows research-only artifacts for inspection, but the run card records `ok_to_download: false` and `ok_to_submit: false`; there is no selected name or note.
2. After authorization and data access, build one layer of `float32` predictions on the exact training grid: the prior official-page observation records EPSG:32611, 100 m cells, matching bounds, values in `[0,1]`, and null/NaN outside the footprint. These format requirements are preserved in [`evidence/official-verification-2026-10-29.json`](../evidence/official-verification-2026-10-29.json); they were not freshly checked on 2026-10-30. A binary 0/1 raster is a valid subset of the numeric range, but the pinned writer's behavior is not a substitute for checking the actual organizer template.
3. Validate the complete TIFF against the authenticated competition example and the shared validator, then rerun the full-registry pre-placement and final-dot gates. Require protocol-compliant `HOLDOUT-DTI` with evaluator/version, withheld-positive count and spatial 95% CI; no projections or quadrant fold ranges qualify.
4. If and only if every scientific, novelty, provenance and format gate passes, let the separate quota-aware selector propose a unique name and note of at most 140 characters. The user must decide whether to spend a weekly slot; do not automatically select or upload. In DrivenData's submission UI, attach only the exact card-approved TIFF, retain the submission-page receipt and record the returned public/private result distinctly.

### Flagged source and repository irregularities

- The GEMSDOE32 owner page calls the 0.2778 value an `OWNER-REPORT`, states that the run was already submitted and says not to resubmit, but no receipt linking the TIFF's SHA-256 to that value is present here. That is owner provenance, not ORGANIZER-CONFIRMED evidence. Do not resubmit the same file.
- The prior official verification ledger flags an internal discrepancy: the problem-page prose describes the training template as predicting total absence, while a hash-pinned owner-mirror sample has 60,988 positive pixels. Because that sample is from an owner mirror, **not an authenticated organizer download**, this remains an unresolved discrepancy rather than a verified organizer defect.
- The supplied 0.3195 value was previously described as the top score/rank 27 in some project text; the **2026-10-29 public leaderboard snapshot** instead records it at rank 47, with 0.4544 at rank 1. Historical rank wording must be dated and corrected; no live 2026-10-30 leaderboard check was verified.
- An earlier merged report, [`research/2026-10-30-repo-review.md`](2026-10-30-repo-review.md), asserts a live 2026-10-30 leaderboard fetch and rank 48. A later merged review and source card state that official pages were not fetched because of network restrictions and withdraw the freshness claim. Those records conflict; this report follows the latter evidence and treats rank 48 as **UNVERIFIED**, not current. Keep the earlier report as historical context, not a live feed.
- The owner's reported portal error is not diagnostic. No conclusion about NaN, finite exterior zeros, range or an incompatible grid should be drawn without the exact uploaded bytes and receipt. The prior official source ledger records NaN/null outside the footprint, while several repo TIFFs use finite exterior zeros; strict checks found those bytes not conforming. These artifacts remain research-only.
- The repo root's legacy quadrant holdout was previously described too broadly as whole-segment hide-and-recover. Its docs now identify the limitation; historical scores are not converted into segment-holdout scores or 95% CIs.

## Three review passes

### Pass 1 — implement and verify

- Read the complete README/project contract and `AGENTS.md`, audited the generated scorecard, all nine individual focus pages, the pinned lattice and pairwise receipts, the GEMSDOE32 mask-forensics receipt, the shared-tool manifests, the public-download inventory and available data paths.
- The requested product is **not safely generatable** from the available evidence. The method paragraph referenced by the user protocol is absent, no complete current registry is present, and the feature stack / authenticated template are unavailable. No code was run that trains, places dots, evaluates a candidate, or writes a TIF.
- Added a new negative review card with null candidate score, registry measurements, hash and validator fields; no score or hash was fabricated.

### Pass 2 — review bugs, assumptions and edge cases

- Found a misleading local helper contract: root `scripts/evaluate_holdout.py` said it withholds whole fault segments, but its implementation withholds only pixels inside a quadrant and dilates that block. A connected fault crossing the boundary can remain partly visible. Corrected the module/function documentation and added a regression test demonstrating the split. The calculation is unchanged so historical receipts remain reproducible.
- Verified the pinned shared evaluator/writer sources against the manifest instead of treating the root helper as shared. No upstream tool was found to require modification for this review; no private fork was made.
- Confirmed that all public downloads remain research-only, that the Pages generator is byte-current, and that the executive summary says “Unavailable” rather than inventing leader estimates.
- Confirmed that the local source snapshots do not provide a complete current registry, live leaderboard, authenticated organizer example, portal acceptance, current quota, or a compatible holdout incumbent.

### Pass 3 — recheck against the full request

- The README already carries the consolidated standing project prompt and says to read it every session; it is updated here with this review, the exact evaluator distinction, and H-F's research-only failure status.
- After syncing PR #88, separately audited the incoming H-F TIFF, its byte hash, saved format/uniqueness/holdout/leakage records, and band semantics; corrected misleading uniqueness/CI/SHA claims and disabled H-F/H-G generator entry points.
- The nine-site executive table lists each best supplied file, user-reported value, unavailable estimate, uniqueness result and explicit do-not-submit decision. The current site makes the release state obvious; no approved TIF link is represented as a submission.
- Three ranked research hypotheses are documented with layers, physical signature, hidden-fault rationale, non-fault mimics/controls, prior-method differences, expected qualitative potential and cost. They are not experiments and are not claimed as fleet-wide novelty.
- The top idea was **not tested** because there is no assigned method paragraph, no authenticated/cached competition feature stack, and the known uniqueness stop blocks the historical high-budget geometry. No weekly submission slot was touched.
- The remaining work and limitations are listed below and in the README.

## Verification performed

- `.venv/bin/pytest -q -rs`: **259 passed, 8 skipped, 98 subtests passed**. The skips require optional pinned owner-mirror inputs not restored in this light review. Rasterio emitted 98 `PendingDeprecationWarning` warnings from Affine multiplication; no test failed.
- `npm test`: **3 passed**; `npm run test:site`: **8 passed**; `npm run test:browser`: smoke checks passed at 1440, 390 and 320 px and checked navigation, nine rows, release lock and freshness states.
- `.venv/bin/python scripts/build_hk3_pages.py --check`: `pages up to date`.
- `.venv/bin/python scripts/audit_public_downloads.py --check`: `PASS_RESEARCH_ONLY`, 10 artifacts, `downloadable_approved_submission: null`.
- Pinned shared code hashes matched `registry/template_tools.json`. No feature data, model, prediction raster, or submission was created.

## Remaining work and limitations

1. The current prompt contains no single assigned method paragraph; the lane cannot be inferred from the general research slate. This is a hard protocol stop, not a request to choose a method after seeing results.
2. Restore the **official** competition inputs/template through the participant data page in an authorized environment. The mirrored files are unverified. The feature stack is not present here.
3. Choose one commit-coherent shared template/toolchain and keep its holdout, metric, writer and inputs together. Do not use the root quadrant helper for a strict new experiment.
4. Obtain an independently complete, current cross-session registry and freeze a same-evaluator incumbent and segment split before testing.
5. If an assigned lane is later available, run feature-alone leakage canaries first, then buffered whole-component hide-and-recover, visible-only catalogue features, exact visible-fault masks, pooled DTI and spatial 95% CI. Check the full surface against every registry raster before placement and final dots afterward.
6. The literal 70% overlap threshold plus the dense lattice witness rules out the historical high-budget dot geometries. Do not evade it by selecting uncovered cells; a policy change is not made by an agent.
7. Resolve the portal range/nodata issue only with authorized evidence. No present local validator can guarantee DrivenData acceptance. The account's weekly quota and current live leaderboard are not available in this workspace.
8. Only after every scientific, novelty, format and provenance gate passes can the separate selector create a uniquely named, ≤140-character note and mark a specific TIF as safe to download. No selector or slot decision is made here.

## Official/manual-review links

- [DrivenData competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem statement, metric and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [About page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Data tab (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [NLR rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DOE GDR INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [USGS GeoDAWN official data record](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)

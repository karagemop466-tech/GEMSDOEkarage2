# Strict three-pass review — HK3 disposition and next research gates

**Review date:** 2026-10-28 (UTC)
**Disposition:** **NO APPROVED SUBMISSION. Research-only. Do not upload the existing HK3 TIFF.**
**New experiments, TIFFs, and competition slots used by this review:** 0.
**Current authorized method lane:** none documented. The prior HK3 run labels itself self-declared.
**Current public-page observation:** the official leaderboard page displayed 0.4544 at rank 1 when fetched on 2026-10-28. This is a time-stamped public-page observation, not a submission-page receipt and not a score for any file in this repository.

This report supersedes the prior HK3 `PROMOTE`/selector disposition for current release decisions. It does **not** edit or erase those historical records: [`evidence/hk3/run_card.json`](../evidence/hk3/run_card.json) and [`evidence/hk3/selector_result.json`](../evidence/hk3/selector_result.json) remain unchanged and are retained as evidence of the earlier, incorrect positive decision. The current fail-closed record is [`evidence/hk3/strict_disposition.json`](../evidence/hk3/strict_disposition.json), with a separate negative selector record at [`evidence/hk3/strict_selector_result.json`](../evidence/hk3/strict_selector_result.json).

## Executive decision

The HK3 raster is **not** a competition submission candidate under the stated rules. It fails the literal all-registry 70% proximity stop by a wide margin, and its zero-valued exterior fails the local strict check against the official problem page's null/NaN outside-bounds requirement. The earlier selector's exception for “not submitted / degenerate” registry rasters is not allowed by the user’s literal rule and has been withdrawn from current disposition. The local public-download audit now exposes the TIFF only as a research artifact and reports no uploadable candidate.

No new method was implemented. The prior run card records three experiments in approximately 2 hours 15 minutes, exceeding the two-hour cap; the current checkout has no assigned next lane and no `data/` or `.cache/` feature stack. The correct outcome is to stop, preserve the negative result, and resolve the lane, registry, and format gates before another experiment.

## Pass 1 — scientific and protocol review

The official problem is to predict **fault structures indicative of geothermal resources**, not geothermal vents. The official metric is distance-tolerant Tversky (α = 0.2, β = 0.8, triangular 300 m kernel); a local catalogue holdout is not an organizer score and is not a direct ranking of the historical submissions.

The prior HK3 run-card reports **HOLDOUT-DTI 0.1845 [0.1677, 0.2015]** at a matched 1.10% dot budget, versus a re-fitted incumbent at 0.1575 [0.1417, 0.1737]; paired difference +0.0270 [0.0206, 0.0337]. Evaluator: `gems57-pooled-hide-v2`; withheld-positive count: 58,258. These are repository-recorded holdout measurements from the prior experiment, not recalculated in this review and not an organizer score. The prior experiment's leakage canaries passed, but those findings cannot waive the uniqueness or format stops.

The label `LEADERBOARD-CALIBRATED ESTIMATE` previously attached to 0.263–0.286 is an exploratory transfer from user-reported scores. It is **not a score**, not organizer-confirmed, and not a validated forecast; it is not used to approve or rank a file here. The official public leaderboard observation of 0.4544 on 2026-10-28 is not tied to a TIFF hash or submission receipt.

### Comparison of the nine supplied best-reported files

All values below are **USER-REPORTED / UNVERIFIED**, not organizer-confirmed results. “Best” means the best reported file represented in the supplied nine-site evidence, not a verified audit of every historical entry or every submission receipt in those repositories. The pinned mirrors show a closely related dot family; all nine fail the requested within-3-pixel uniqueness rule against other historical site masks.

| Site | Reported result | Positive pixels | Pinned-mask relationship / interpretation |
|---|---:|---:|---|
| GEMSDOE24 | 0.2477 | 60,069 | Dense D1.5 member of the ridge-dot family. |
| GEMSDOE25 | 0.2600 | 44,090 | D2.8 parent mask in the measured family relations. |
| GEMSDOE27 | 0.2449 | 61,328 | D1.5 variant with topographic gap closure; the supplied report is below GEMSDOE24. |
| GEMSDOE28 | 0.2710 | 37,660 | H36-1 rung30 blind R1 variant; highest reported value in this list other than GEMSDOE32. |
| GEMSDOE30 | 0.2600 | 44,090 | Its decoded dots are identical to GEMSDOE25 despite different packaging/description. |
| GEMSDOE31 | 0.2708 | 40,199 | GEMSDOE25 minus 3,891 dots within 1 pixel of the mapped catalogue. |
| GEMSDOE32 | 0.2778 | 37,654 | GEMSDOE31 minus a further 2,545 dots in the 1–2 pixel band; highest user-reported value in this set. |
| GEMSDOE33 | 0.2632 | 41,865 | Analog tip/stepover variant; the score does not establish that its named features found new faults. |
| GEMSDOE36 | 0.2750 | 38,854 | GEMSDOE32's decoded dot set plus 1,200 positive pixels. |

The exact mask relations are reproducible on pinned owner-mirror bytes. They are **not** proof that the reported values are attached to those bytes: no file-bound organizer receipts are present. GEMSDOE25/GEMSDOE30 are byte-decoded-mask duplicates; the nested GEMSDOE31/32 pruning and GEMSDOE36 addition are also measured relations. This evidence supports a common lineage, not nine independent geological discoveries.

### What may explain GEMSDOE32's reported 0.2778

A plausible hypothesis is that removing predictions very near known mapped faults reduces false-positive mass while retaining predictions whose distance-tolerant kernels can still receive credit from nearby unmapped faults. That tradeoff is consistent with the metric's relatively low false-positive weight (α = 0.2) and its 300 m distance tolerance. It does **not** establish why the hidden competition score was 0.2778.

The metric's truth-side and prediction-side weighted sums are distinct; the dot-count difference alone cannot recover hidden truth, true-positive credit, or false-positive mass. No causal arithmetic based on a simplified count identity is justified. The source record also says the contemporaneous H33 candidate was unscored; a later owner report may exist, but no later organizer receipt tying 0.2778 to this TIFF was found. Therefore the right conclusion is **plausible pruning mechanism; score attribution and hidden-label effect unknown**.

## Pass 2 — saved raster, registry, and format review

### Literal registry stop: fail, without exceptions

Saved raster: `docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif`
SHA-256: `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`
Positive pixels: 45,108.

The final-dot audit finds these literal >70% within-3-pixel overlaps:

| Registry raster | HK3 dots within 3 px | Result |
|---|---:|---|
| r13 spacing-5 lattice (GEMSDOE24 mirror) | 99.8626% | **STOP** |
| same r13 lattice (13GEMSDOE mirror; same SHA-256) | 99.8626% | **STOP** |
| GEMSDOE24 ridge-line/surface raster | 70.9763% | **STOP** |
| GEMSDOE32 H45 KS0 control raster | 73.3484% | **STOP** |
| local K2 research raster | 74.9401% | **STOP** |

The two r13 entries are two registry references to the same underlying TIFF; either one alone is enough to trigger the stop. Their “degenerate” description is a geometric diagnostic, **not an exclusion**. The user's binding rule applies to any registry raster, whether scored, submitted, sparse, dense, or used as a witness.

The r13 3-pixel halo covers 5,160,724 of 5,167,373 eligible cells (99.8713%), leaving 6,649 cells outside that halo in the owner mirror. Independently, the slate's counting bound shows that a 37,654-dot raster must overlap at least 82.34% with this witness. This bound does not prove all smaller budgets impossible; it does show why selecting rare holes merely to pass the test would be non-geological gaming. No such placement was attempted.

The registry audit is incomplete: **452 of 453 expected entries checked**, one missing/invalid, and no complete-inventory certificate. It is therefore a negative partial scan, not proof of uniqueness against the complete organizer registry. HK3 has no saved pre-placement surface-versus-registry receipt; the available comparisons concern final dots. Neither gap can be repaired by the favorable comparisons against only the nine focus-site files or by a chance-corrected statistic.

### Exterior and portal error

The saved TIFF is one-band float32 on the pinned owner-mirror EPSG:32611, 3730 × 3292, 100 m grid. The saved array has no NaN or infinity and every value is in [0, 1]; the shared local `gems57` validator passes its zero-exterior checks. These are local byte checks against an unauthenticated mirror.

The official problem description says pixels outside the raster bounds should be null/NaN. The strict local receipt records `outside_is_nan: false`, 7,111,787 finite exterior pixels, `strict_format_pass: false`, and `upload_authorized: false`. HK3 writes zeros outside. The official sample identity and portal's exterior handling have not been authenticated, so the earlier claim that this encoding makes the portal range error unable to recur was unsupported. The whole-array numeric range passes, but it does not prove portal acceptance or identify the cause of the prior “Predicted values must be in range [0, 1]” error.

No upload or portal test was performed. The zero-exterior TIFF remains downloadable only as a **research artifact** so its bytes and historical measurements remain inspectable.

## Pass 3 — release/site and operational review

The earlier site and public-download audit treated the historical `PROMOTE` card and a disclosed literal-rule exception as approval. That behavior conflicted with the hard rule. The old card and selector are preserved unchanged; a new strict negative disposition now controls the public site and download audit. Current status is **DO NOT SUBMIT**, with no upload instructions, no approved-candidate link, no slot authorization, and a clearly labeled research-only TIFF/ZIP link.

The previous HK3 card says three experiments used in about 2 hours 15 minutes. The cap is therefore exhausted for that run; this review ran zero experiments. No `data/` or `.cache/` is present. The next-lane slate is a set of unassigned research proposals, not an authorization to start any of them. The HK3 generator has also been hardened for any future authorized build: it checks and records the continuous surface against the registry before placing dots, treats any literal overlap/rank duplicate as a stop regardless of submission status or density, and requires a complete scan, passing pre-placement receipt, strict exterior check, and authenticated template before a positive run-card verdict. The historical run card and selector remain byte-for-byte unchanged; this code change is not a new experiment.

## Four distinct, falsifiable geological hypotheses — proposals only

The following slate concerns fault structures indicative of geothermal resources, not direct vent locations. Ranks are qualitative feasibility/value hypotheses, not predicted scores. The exact feature units and official data lineage still need authentication. The four proposals are already documented in [`research/2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md); none was implemented in this review.

| Proposal | Distinct mechanism | Named non-fault mimic and falsifier |
|---|---|---|
| **1. Topography-conditioned residual gravity step** (bands 13, 11, 12, 19) | Fit a label-blind, block-local terrain/regional trend, then test sign-persistent gravity-gradient residual edges at 300–900 m for covered density offsets that continue beyond an exposed scarp. | Unfaulted sediment–bedrock contact or lake-terrace riser. Predefine contour/shoreline-aligned nulls, ablate terrain regression, and test on label-blind offset blocks. Potential ingredient-family collision with the already-negative B4 topography/gravity experiment; resolve lane assignment before any run. |
| **2. Conductivity saddle across an independently located gravity break** (bands 17, 13, 18; exclude band 15 until its meaning is authenticated) | Test a cross-profile sign change in conductivity curvature across a separate gravity break, rather than selecting high conductivity alone; a buried offset/conduit is a fault hypothesis, not proof of geothermal fluid. | Saline groundwater/playa margin or EM-inversion seam. Ablate conductivity, stratify basin/range tests, and check whether the feature follows survey coverage boundaries. |
| **3. Strain-regime change × persistent magnetic edge** (bands 7, 8, 2, 3) | Use a coarse strain-change interaction only as context for a persistent magnetic edge; do not claim 100 m fault localization from interpolated strain alone. | Geodetic interpolation seam or unfaulted intrusive contact. Shuffle strain within blocks and require incremental matched-fold value over magnetic-only controls. |
| **4. Seismicity-sidedness at an independent gravity edge** (bands 10, 16, 11) | Compare aggregate seismicity on either flank of a gravity edge as a contextual prior for an active unmapped strand, not a local fault detector. | Production/mining-induced seismicity or smoothed-density artifacts. Predefine a shuffled-seismicity control; stop if it performs similarly. |

Before any future experiment: obtain an actual coordinator-assigned lane; resolve the literal registry scope and completeness without excluding the lattice; authenticate inputs/template and exterior convention; establish a frozen same-fold incumbent and available experiment/time budget; then use the shared cached feature stack, `evaluate_holdout.py`, and `submission_writer.py`. Withhold whole buffered fault segments, derive catalogue features from visible faults only, mask visible fault pixels exactly, run every feature-alone leakage canary (AUC >0.90 is leakage until disproved), and report pooled HOLDOUT-DTI with evaluator version, withheld-positive count, and 95% CI. No projection may be called a score. Do not generate a candidate until the pre-placement surface gate passes; only then can final-dot uniqueness and saved-byte gates run. Promotion and any real slot remain a separate selector decision.

## Remaining work / blockers

1. **Do not submit HK3.** Preserve the TIFF, historical card, and old selector result; use the strict disposition for all current release decisions.
2. Obtain the actual method paragraph/assigned lane and written resolution of the literal all-registry rule. Under the current rule the r13 lattice is in scope; do not invent an exemption or select its holes to game proximity.
3. Obtain a complete, hash-pinned registry inventory. Existing 452/453 coverage is incomplete; the pre-placement HK3 audit is missing.
4. Authenticate the competition data/template and resolve the official null/NaN exterior requirement against the actual submission sample or organizer clarification. Do not infer safety from the old reference writer or from a whole-array range pass.
5. Confirm the nine-site values and the GEMSDOE32 0.2778 against file-bound organizer receipts if available. Keep all existing values marked USER-REPORTED / UNVERIFIED until then.
6. Do not run an additional HK3 experiment: its recorded three-experiment and approximately 2h15m budget is already exhausted. A future method requires a separately authorized lane and budget.
7. Before any promotion, require a fresh, saved-byte audit, unique filename and ≤140-character note, complete gates, and an explicit selector decision. No weekly slot was used in this review.

## Source notes

- [Official problem description and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — target wording, α/β and 300 m kernel, and published GeoTIFF bounds/exterior requirements; accessed 2026-10-28.
- [Official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — observed rank 1 at 0.4544 on 2026-10-28; a page snapshot only, not a receipt for this raster.
- [DOE/NREL competition rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf) and [organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) — competition context and reference implementation; neither supplies a file-bound score receipt for this repository.
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [INGENIOUS](https://gbcge.org/current-projects/ingenious/), [USGS 3DEP](https://www.usgs.gov/3d-elevation-program), and [The National Map](https://apps.nationalmap.gov/downloader/) — contextual source leads only; no new layers were obtained or used in this review.

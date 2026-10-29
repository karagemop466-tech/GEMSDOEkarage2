# Session findings — 2026-10-29 (branch arena/599bbc9f-gemsdoekarage2)

**Decision: no file is approved for upload. No submission name or note is proposed.**
No candidate passed every gate, and no candidate is uniqueness-clean.

Labels used below: **HOLDOUT-DTI** (evaluator, withheld count, fold range; the fold range is *not* a 95% CI), **ORGANIZER-CONFIRMED** (none exists for these files), **USER-REPORTED / UNVERIFIED** (supplied scores), **PROTOCOL-CEILING** (a bound from the protocol, not a score). Projections are never scores.

## 1. Best submission per focus site

Every best file is research-only. The reported scores are historical and unverified.

| Site | File (research only) | Reported score | Estimated leaderboard score | Unique vs GEMSDOE sites? | Submit? |
|---|---|---|---|---|---|
| GEMSDOE32 | gemsdoe32-h33-h33-2-b2-…-zeros.tif | 0.2778 USER-REPORTED / UNVERIFIED | Unavailable | NO (100% 3-px overlap) | DO NOT SUBMIT |
| GEMSDOE36 | gemsdoe36-anderson-geothermal-pinn-38854-…-zeros.tif | 0.2750 USER-REPORTED / UNVERIFIED | Unavailable | NO | DO NOT SUBMIT |
| GEMSDOE28 | gems28-h36-1-rung30-blind-r1-…-nan.tif | 0.2710 USER-REPORTED / UNVERIFIED | Unavailable | NO | DO NOT SUBMIT |
| GEMSDOE31 | gemsdoe31-h27-4-solo-d28-…-nan.tif | 0.2708 USER-REPORTED / UNVERIFIED | Unavailable | NO | DO NOT SUBMIT |
| GEMSDOE33 | GEMSDOE33-h33d-analog-tip-stepover-r30-…tif | 0.2632 USER-REPORTED / UNVERIFIED | Unavailable | NO | DO NOT SUBMIT |
| GEMSDOE25 | gems25-dotted-h19-5-d2-8-…-nan.tif | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | NO | DO NOT SUBMIT |
| GEMSDOE30 | gemsdoe30-d28-poisson300m-offcat-44090-…tif | 0.2600 USER-REPORTED / UNVERIFIED | Unavailable | NO | DO NOT SUBMIT |
| GEMSDOE24 | gems24-h25-1-dotted-h19-5-d1-5-…-nan.tif | 0.2477 USER-REPORTED / UNVERIFIED | Unavailable | NO | DO NOT SUBMIT |
| GEMSDOE27 | gems27-topo-gap-closure-t-v2-on-d1-5-…-nan.tif | 0.2449 USER-REPORTED / UNVERIFIED | Unavailable | NO | DO NOT SUBMIT |

Source: `evidence/registry-overlap-audit-20261029.json` (post-hoc, 470 references compared, 2 failed closed) and `docs/executive-summary.html`. Every row reads "DUPLICATE" in the audit.

**Live leaderboard (ORGANIZER-PUBLISHED public snapshot, not a receipt):** #1 xiaofanhu 0.4544. The user's figures 0.4413 and "0.3195 is highest" do not match the page. kpomazi is #47 at 0.3195. Chunk 2 (read this session): #48 drjy 0.3180, #49 twang 0.3169, #50 kinneso_outlook 0.3167. The list shows 50 entries.

## 2. Why GEMSDOE32 h33-h33-2-b2 (0.2778) is highest, and whether >0.2778 is achievable

- **Why it scored highest (derived, conditional, not established):** its file is the D2.8 dot set with 6,436 dots removed (`evidence/champion_forensics.json`). Under the metric with α + β = 1, a dot adds value only if its hit probability exceeds α × DTI ≈ 0.056 at DTI 0.2778. The removed dots were probably below that rate. This is an inference from the saved bytes, not a confirmed cause.
- **Is >0.2778 achievable?** Not established. The lane rule now blocks every candidate in the apron family: the nine focus best paths and the gw-nfs raster all overlap registry rasters at 99–100% within 3 px. A new candidate must be a dot set that is unique in the registry *and* beats the break-even. No such candidate exists yet.
- **Unique improvement attempted:** the gw-nfs apron ranking (E1/E2 below) and the saddle raster were the only new candidates this session. Both fail the lane rule. Nothing is saved as a submission.

## 3. Registry audit (post-hoc)

- Receipt: `evidence/registry-overlap-audit-20261029.json`. Rules: |Spearman| > 0.90 or > 70% of dots within 3 px of one registry raster = DUPLICATE.
- 10 candidates checked, **10 DUPLICATE**. The gw-nfs zeros raster has |rho| 0.08 but 99.24% of its 30,000 dots are within 3 px of `24gems-gapfill-near-fault-…-zeros.tif` (37,722 positives). The overlap is real, not a degenerate reference.
- **Limitation:** 2 inputs failed closed and were not compared: a GEMSDOE31 CSDU reference with NaN in its footprint, and the GEMS36 format-test raster (grid mismatch). Neither changes a verdict here, but the audit is not exhaustive. The live registry grows (440 pinned, 489 on main); the audit covers the 470 comparable manifest entries at run time.

## 4. Experiments (budget: 3 experiments or 2 hours; 2 used)

Receipt: `evidence/gw-nfs/experiments.json`. Run card: `evidence/session-2026-10-29-run-card.json`.

| Arm | HOLDOUT-DTI (pooled) | Withheld positives | Fold range (not a CI) |
|---|---|---|---|
| E1 random apron (control) | 0.000076 | 60,988 | 0.000000–0.000119 |
| E1 saddle-ranked gw-nfs | 0.000013 | 60,988 | 0.000000–0.000063 |
| E2 geod_2ndinv-ranked apron | 0.000072 | 60,988 | 0.000000–0.000159 |

- **Leakage canary:** geod_2ndinv alone on withheld segments, AUC 0.570 (threshold 0.90): no leakage.
- **Interpretation rule:** a ranking earns credit only if it beats random apron on the same folds. Neither does. The E2 hypothesis is negative.
- **Why all arms are near zero (PROTOCOL-CEILING):** `scripts/apron_reachability.py` → `evidence/gw-nfs/apron_reachability.json`. Under the mandated 3-px buffer, only **79 of 60,988 withheld positives (0.13%)** lie within reach of *any* apron pixel. An apron placement cannot score most withheld faults. So these near-zero numbers say the protocol is insensitive to apron placements. They are not evidence against the geophysics, and the holdout cannot validate any apron candidate.
- **Earlier gw-nfs number is invalid:** the in-sample 0.054563 (fold range 0.005099–0.175894) leaks labels. It is withdrawn.

## 5. Untried geological hypotheses (3–5), ranked

No hypothesis has a measured DTI gain yet. Ranking uses cost and novelty, and is explicitly not a gain estimate. All four use bands already in `training_features.tif` (see Section 7), so **no external data source is needed**; there is nothing to verify for obtainability.

| Rank | Hypothesis | Bands | Cost | Status |
|---|---|---|---|---|
| 1 | Tilt/total-curvature magnetic edge persistence co-located with geodetic shear-rate maxima | tc (6), geod_shearrate (7) | Low | Untried. Needs a placement that is not confined to the apron, because the apron ceiling is 0.13%. |
| 2 | Dilatation sign change across detrended-elevation lineaments | geod_dilaterate (8), det_elev (12) | Low–medium | Untried. Same apron-ceiling constraint. |
| 3 | Depth-to-basement gradient step co-located with isostatic-gravity vertical gradient | depth_to_base_surf (15), iso_grav_anom_vg (11) | Low | Untried. Same constraint. |
| 4 | Seismicity intensity ridge (ieq_n100a15, band 16) | band 16 | Low, but blocked | Untried. The sign and meaning of the seismic term are unverified (band 10 is labelled "distance to earthquake" while the official text says "density of earthquakes"). Do not use until verified. |
| — | Geodetic second-invariant ranking in apron (geod_2ndinv, band 4) | band 4 | Low | **TESTED, negative** (E2). Not credited. |

**Validation rule:** no candidate uses a weekly slot until it passes (a) the spatially blocked holdout with a placement that can reach withheld faults, (b) the leakage canary, and (c) the registry audit. Hypotheses 1–3 cannot pass (a) under the apron placement. A non-apron placement design is the remaining work.

## 6. Portal error "Predicted values must be in range [0, 1]"

- **Official text (verified):** values in [0, 1]; "data outside the bounds is null or nan" (https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
- **Zeros-outside files** are in range, so the convention alone does not explain a range error.
- **Two hypotheses remain open:** (a) the portal's range check treats NaN as out of range, so the NaN-outside convention itself triggers it; (b) the portal reads a nodata sentinel as a value. Neither is established. No portal receipt exists for any saved file.
- **Resolution path:** one portal test with a NaN-outside file, using a weekly slot. That needs an explicit user decision. No slot was spent. The error is **unresolved**.

## 7. Official sources and irregularities

- Format and metric: DrivenData page/967 (above). EPSG:32611, 100 m, float32, single band, [0, 1]; DTI α 0.2, β 0.8, 300 m triangular kernel.
- Band names: `training_features.tif` has 19 bands with descriptions (band 4 geod_2ndinv; band 10 deq_n100a15 labelled "Distance to earthquake" in band metadata). The official feature list says "Density of earthquakes". **Irregular; unresolved.**
- The feature mirror SHA-256 `4371c82e…` is a research mirror, not organizer-authenticated.
- The sample template's SHA-256 `2176d08e…` is an owner mirror pin, not organizer-authenticated. It contains positive cells, which conflicts with the phrase "predicts total absence".
- Date irregularity: the saved public-leaderboard observation is dated 2026-10-28 (`evidence/official-review-2026-10-28.json`). Today's fetch (2026-10-29) shows the same top score.

## 8. Three passes

1. **Implement / verify.** Audit run; gw-nfs experiments run (E1, E2); generator verify mode reproduces the saved bytes (holdout 1.3e-05, verdict negative, DUPLICATE); pages regenerated; `build_hk3_pages.py --check` passes.
2. **Review.** Found and fixed:
   - The candidate block linked the retired gw-nfs TIF from `docs/downloads`. That was an unregistered downloadable raster. It is moved to `evidence/gw-nfs/retired/`, not published, and kept with its SHA-256.
   - The how-to page lost the HK3 hero during an edit. Restored.
   - The root `index.html` redirected to the executive summary. It now redirects to the submission desk, `docs/index.html`.
   - The candidate block had been written to require a run card and a NaN-outside raster that do not exist. Rewritten to read only saved receipts and fail closed.
   - Confirmed the generator's helper names and signatures against the code before running; the experiment script ran cleanly.
3. **Recheck.** Full Python suite: **229 passed, 8 skipped, 0 failed** (HEAD baseline: 14 failed, 212 passed). Node: site 7/7, feed 3/3. `build_hk3_pages.py --check`: up to date. (Measured at the end of the session; see the PR for the final run.)

## 9. Limitations

- Holdout numbers are a catalogue proxy. None predicts the organizer's hidden score.
- The registry audit is post-hoc and covers the 470 comparable references at run time. The live registry grows.
- The 8 skipped Python tests need owner-mirror inputs that are absent. They are not authenticated organizer data.
- The portal-error cause is unresolved.
- The band-10 / band-16 seismic label conflict is unresolved, so the seismic term's sign is unverified.
- No placement design exists that is both spatially validatable and unique. Hypotheses 1–3 need one.

## 10. Remaining work

1. Decide whether to spend one weekly slot on a NaN-outside file to resolve the portal error (user decision).
2. Design a non-apron placement that can reach withheld faults under the 3-px buffer, then validate it with the spatially blocked holdout before any slot.
3. Verify the band-10 vs band-16 meaning against the organizer's feature documentation, and the seismic term's sign.
4. Re-run the registry audit on the live registry (now 489 focus rasters) before any placement.
5. Read the leaderboard again on the day of any upload.

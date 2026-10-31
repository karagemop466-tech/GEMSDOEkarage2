# Session review — 2026-10-31 (GEMSDOEkarage2)

**Verdict: NO FILE IS CLEARED TO DOWNLOAD AND SUBMIT.** Not because of a missing step, but because the shared uniqueness gate, applied literally, stops every dot-based file in this footprint. This session generated one new research TIFF. It is format-valid and it is a DUPLICATE_STOP.

Evidence class of every number below is labelled. No number is a score. `USER-REPORTED` = copied from a site, no receipt. `REPORT-ONLY` = a local measurement that is not HOLDOUT-DTI (no hide-and-recover, no withheld-segment CI). `ORGANIZER-CONFIRMED` = none exists for any local file.

## 1. Executive summary (nine focus sites)

Each file was fetched from its pinned GitHub commit and matched to the recorded sha256 (9 of 9 match). The table lives on the site desk and in `docs/evidence/nine-site-executive-20261031.json`.

| Site | Best file (research download only) | Reported score | Estimated score | Unique vs 13GEMSDOE lattice? | Download and submit? |
|---|---|---|---|---|---|
| GEMSDOE32 | h33-h33-2-b2 (highest reported) | 0.2778 USER-REPORTED | Unavailable | NO (99.92% dots in halo) | NO |
| GEMSDOE36 | anderson-geothermal-pinn | 0.2750 USER-REPORTED | Unavailable | NO (99.92%) | NO |
| GEMSDOE28 | h36-1-rung30-blind-r1 | 0.2710 USER-REPORTED | Unavailable | NO (99.91%) | NO |
| GEMSDOE31 | h27-4-solo-d28 | 0.2708 USER-REPORTED | Unavailable | NO (99.92%) | NO |
| GEMSDOE33 | h33d-analog-tip-stepover-r30 | 0.2632 USER-REPORTED | Unavailable | NO (99.91%) | NO |
| GEMSDOE25 | dotted-h19-5-d2-8 | 0.2600 USER-REPORTED | Unavailable | NO (99.92%) | NO |
| GEMSDOE30 | d28-poisson300m-offcat-44090 | 0.2600 USER-REPORTED | Unavailable | NO (99.92%) | NO |
| GEMSDOE24 | h25-1-dotted-h19-5-d1-5 | 0.2477 USER-REPORTED | Unavailable | NO (99.92%) | NO |
| GEMSDOE27 | topo-gap-closure-t-v2-on-d1-5 | 0.2449 USER-REPORTED | Unavailable | NO (99.92%) | NO |

"Unique vs lattice" is the share of a file's dots within 3 px of the 13GEMSDOE registry raster. The literal gate stops above 70%. Pairwise overlap among the nine (from `docs/evidence/nine_site_best_files_audit.json`) also fails for all nine.

**Why no estimate.** The only local score-like number is the catalogue proxy (REPORT-ONLY). It is anti-aligned with the leaderboard for the top file: GEMSDOE32 scores 0.0067 on the catalogue, while GEMSDOE24 and GEMSDOE27 score about 0.17. The official problem page says the scored target is faults **not** in the USGS database (see §5), so catalogue recovery is not a leaderboard proxy.

## 2. Measured pattern (observational)

Across the nine files, the share of dots within 3 px of a USGS catalogue trace runs opposite to the reported score:

| File | Reported (USER-REPORTED) | Dots within 3 px of USGS trace |
|---|---|---|
| GEMSDOE32 | 0.2778 | 5.77% |
| GEMSDOE36 | 0.2750 | 5.87% |
| GEMSDOE28 | 0.2710 | 11.62% |
| GEMSDOE31 | 0.2708 | 11.73% |
| GEMSDOE33 | 0.2632 | 14.39% |
| GEMSDOE25 | 0.2600 | 19.52% |
| GEMSDOE30 | 0.2600 | 19.52% |
| GEMSDOE24 | 0.2477 | 19.87% |
| GEMSDOE27 | 0.2449 | 19.87% |

Spearman rho = −0.98 (n = 9, p ≈ 2×10⁻⁶). This is an association over user-reported numbers. It is not a cause, and it is not a projection. Extrapolating it to a new file would be a projection and is not written as a score. All nine files place zero dots exactly on a catalogue pixel, so the difference is in the 3-px halo, not on the trace.

## 3. New file generated this session (HM1)

- **Name:** `gemsdoekarage2-hm1-offcat-magridge-35079-20261031-DO-NOT-SUBMIT.tif`
- **Hypothesis (pre-registered, `docs/evidence/hm1/preregistration.json`):** linear magnetic discontinuities in the GEODAWN TMI_up150 residual, found by an oriented elongated second-derivative ridge filter, mark unmapped faults when dots sit ≥300 m from catalogue traces.
- **Mechanism and named mimic:** faults can carry magnetic lows or offsets. Dikes and lithologic contacts are linear without displacement. Flight-line striping and uint8 steps can also produce ridges.
- **Format (10 of 10 format checks pass):** single float32 band, EPSG:32611, 3730×3292, official transform and bounds, NaN outside the footprint (7,111,787 cells), finite inside in [0,1], 35,079 dots.
- **Leakage canary (feature alone vs catalogue):** AUC 0.523 ≤ 0.90, PASS.
- **Uniqueness (full pinned registry, 489 rasters):** DUPLICATE_STOP. Max Spearman 0.048. One witness, `inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif`, has 100% of dots within 3 px. Receipt: `docs/evidence/hm1/uniqueness_full_registry_489.json`.
- **Holdout DTI:** NOT AVAILABLE FOR SCORING. The only local DTI is REPORT-ONLY and uses the catalogue. HM1's halo share is 9.07% (see irregularity I1). That places it in the same range as the 0.27 group, but that is an observation, not an estimate.
- **Decision:** NOT ELIGIBLE. See §4.

## 4. Why no candidate can pass the literal uniqueness gate

The 13GEMSDOE lattice places a dot within 3 px of 99.87% of the footprint (206,895 lattice dots in footprint). Only **6,649 of 5,167,373 footprint cells (0.13%)** lie outside its halo. Any dot file therefore fails the 70% rule unless at least 30% of its dots fall in those 6,649 cells. That is the edge-hole placement that AGENTS.md prohibits ("No edge-hole gaming … creates clearance"). I did not do it.

**Decision needed from the protocol owner (not made here):** whether the 13GEMSDOE calibration lattice counts as a registry raster under the 70% rule. It is a real competitor submission (leaderboard entry), so the rule as written applies. If the rule is kept, no dot-based file can be cleared. If it is changed, the change must be written down, dated, and applied to every lane, not only this one.

## 5. Official sources (verified this session)

- Problem description: the scored set is "faults that are not contained within the current public USGS database". Labels come from USGS and INGENIOUS. Metric: distance-weighted Tversky, α = 0.2, β = 0.8, R = 300 m. https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Submission format: GeoTIFF, single band, float32, values between 0 and 1, EPSG:32611, 100 m, "data outside the bounds is null or nan". Same URL, second chunk.
- Leaderboard snapshot (live fetch, 2026-10-31): top 0.4544 (rank 1), rank 2 0.3925. Re-check before citing. https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Free independent fault data (not verified as non-overlapping with USGS): Nevada Bureau of Mines and Geology 1:500k geologic map, contact, and fault data, free to download. https://data-nbmg.opendata.arcgis.com/pages/geology — the sandbox cannot reach this host; a user download is needed.

The user-cited thresholds 0.3195 and 0.4413 are not current leaderboard values, and I did not use them as targets.

## 6. Untried hypotheses (3–5, ranked by plausibility × cost × measurability)

Expected DTI gain is **not estimable locally** for any of these. Ranking is judgment, not measurement.

1. **H-NBMG: independent off-catalogue validation set (rank 1).** Use NBMG fault traces, minus any overlap with the USGS catalogue, as withheld positives. This would finally give a holdout that matches the target class. It is not a predictor. Cost: low, but needs a user download. Leakage: n/a (label-side). Searched repo: 0 prior mentions of NBMG.
2. **H-EN: en-echelon parallel offsets 1–3 km from catalogue traces (rank 2).** Dots where a magnetic or LiDAR lineament parallels the nearest catalogue strike at a 1–3 km lateral offset. Physical basis: parallel strands and splays of fault zones are common and often unmapped. Mimic: parallel dike swarms and contacts. Leakage: uses catalogue geometry, so the AUC canary must be run. Overlap: partial with stepover lanes (41 mentions). Searched repo: 0 "echelon" mentions.
3. **H-HM1: oriented magnetic ridge (done, §3).** Feature class is new (0 "ridge filter" mentions). Placement collides with the lattice, so it is blocked.
4. **H-A intersection propensity (already tried).** Multi-scale curvature plus K/Th. Implemented earlier; failed the lattice gate. Not re-proposed.
5. **K/Th alteration boundary (already tried).** GEMSDOE28 H38-1 used GeoDAWN channels; transfer test refused. Not re-proposed.

## 7. Three-pass review

- **Pass 1 (implement):** pre-registration, generator, uniqueness audit, validator, run card, nine-site audit, desk panel, inventory entry, test updates.
- **Pass 2 (review):** every fetched file matches its pinned sha256 (9 site files, labels, template, 4 external rasters, 489 registry rasters). Inventory: `PASS_RESEARCH_ONLY`, `downloadable_approved_submission: null`. CI-equivalent steps run locally: `build_hk3_pages.py --check` (pages up to date), `build_site.py`, `build_field_notes.py`, `build_audit_site.py --check`, `assess_release.py`, `audit_k2_release.py`, `review_hk3_protocol.py --check`, `review_k2_release.py`, `pytest` (262 passed, 8 skipped), `npm test` (3/3), `npm run test:site` (8/8).
- **Pass 3 (re-check against the request):** see §8.

## 8. Requirement check against the original request

| Request | Status |
|---|---|
| Executive summary per focus site (9), best file obvious | Done. Desk top panel plus nine-site JSON. Every file says NO to download and submit. |
| Highest-scoring file, estimate labelled as estimate | Done. Highest reported = GEMSDOE32 0.2778 (USER-REPORTED). Estimate = Unavailable (no validated estimator). |
| Uniqueness column vs other GEMSDOE sites | Done. Lattice column plus pairwise audit. |
| Unique GeoTIFF, float32, [0,1], EPSG:32611, 100 m, same grid | Done for format. **Not unique**: DUPLICATE_STOP. |
| Beat 0.3195 or 0.4413 | **Not established.** No local score exists. Not claimed. |
| Automated gates before uniqueness | Done (validator, leakage canary, full-registry audit, tests). |
| Labels on all numbers | Partially. Catalogue numbers are REPORT-ONLY, not HOLDOUT-DTI, because there is no withheld-segment protocol or CI. Nothing is labelled ORGANIZER-CONFIRMED because no receipt exists. |
| Leakage canary (AUC > 0.90 = leakage) | Run for HM1 (0.523). Not run for the nine reference files. |
| Run card JSON at end; budget 3 experiments or 2 hours | Run card in the desk and `docs/evidence/hm1/run-card.json`. Experiments used: 1 (registration plus amendment A1). |
| Do not pick the submission slot | Honored. No selection made. |
| Conflict: "do not pick" vs "promote to a real slot" | Flagged. Selection treated as a separate step. Nothing promoted. |
| Downloadable TIF and summary on Pages | Done. Research TIF is labelled DO NOT SUBMIT. |
| Consolidated prompt in README | Present (see README). Session addendum added. |
| Flag irregularities, cite official links | §9 and §5. |

## 9. Irregularities (flagged, not hidden)

- **I1 (HM1 buffer boundary).** The generator excluded dots strictly closer than 3 px (`dist >= 3` allowed). 3,183 dots (9.07%) therefore sit at exactly 3.0 px. Under the inclusive definition used by the nine-site audit, the share is 9.07%. Not re-run: the duplicate verdict is driven by the lattice, and no experiment was spent. The next lane should use a strict buffer.
- **I2 (budget amendment A1).** The pre-registered 37,654 dots was unattainable, so all 35,079 survivors were used. The count confound is not controlled. Recorded in `docs/evidence/hm1/preregistration.json`.
- **I3 (exterior convention is not uniform).** Five of the nine files (GEMSDOE24, 25, 27, 28, 31) use NaN outside the footprint. Four (GEMSDOE30, 32, 33, 36) use zeros, including the top reported file. The official text says "null or nan". The user-reported error "Predicted values must be in range [0, 1]" is not explained by either convention here. Portal acceptance of either is unverified.
- **I4 (inventory checker was stricter than the official text).** `audit_public_downloads.py` required whole-array finite data, which excludes NaN outside. I added a narrowly scoped artifact kind, `research_nan_exterior`, that requires NaN on exactly the official 7,111,787 exterior cells and finite [0,1] inside. This is a shared-tool change; the uniqueness verdict is unaffected.
- **I5 (uint8 mirror).** TMI and LiDAR bands are uint8 mirrors with no documented scale or offset. Only relative geometry is used.
- **I6 (test invariant changed on purpose).** Three tests asserted that each primary page offers exactly one download (the HK3 file). They now assert that every download is a published research file with a negative run card, and that the HK3 file is still offered. The safety intent (no approved file offered) is preserved and tested more precisely.
- **I7 (uniqueness registry is nine repositories, not global).** The 489-raster manifest covers nine GEMSDOE repositories only. It is not a complete registry.
- **I8 (catalogue proxy is not a holdout).** Every catalogue number on the site is REPORT-ONLY. No CI, no withheld segments, not HOLDOUT-DTI.

## 10. Commands and receipts

- `scripts/fetch_pinned_registry.py` — materialises the 489 pinned registry rasters (new; reads the manifest, never rewrites it).
- `scripts/hm1_offcat_magridge.py` — HM1 generator (pre-registered; amendment A1 recorded).
- `scripts/audit_nine_site_executive.py` — nine-site measurement receipt (new).
- `scripts/audit_public_downloads.py` — registers HM1; new artifact kind `research_nan_exterior`.
- `scripts/build_hk3_pages.py` — adds the desk panel `todays_answer()`.
- `audit_full_registry.py` (shared, unchanged) — full-registry comparison; produced the DUPLICATE_STOP receipt.

## 11. Next steps (for the user, in order)

1. **Decide the uniqueness policy** for the 13GEMSDOE calibration lattice (§4). Nothing else can be cleared until this is settled.
2. **Obtain NBMG fault data** (free, §5) and measure its overlap with the USGS catalogue, to build an off-catalogue validation set.
3. Only then consider H-EN (§6, rank 2) with a strict 3 px buffer and the leakage canary.
4. Do not pick a submission slot from this session. Selection is a separate, later step.

## 12. Cross-session findings (found while merging `origin/main`, 2026-10-31)

- **I9 (GBSP passes the literal gate only by avoiding the lattice).** `docs/downloads/gems-gbsp-blindspot-2195bc570842-20261031T005323Z.tif` has 4,525 dots, and **0.0%** are within 3 px of the 13GEMSDOE r13 lattice (measured here with the same halo definition). It can pass the 70% rule only because it sits in the 0.13% of the footprint the lattice does not cover. That is the edge-hole pattern AGENTS.md prohibits ("No edge-hole gaming … creates clearance"), and the 2026-10-29 decision memo already flags the same pattern (GEMSDOE36, 505 dots). Its own card is negative with `ok_to_submit: false`, so nothing is unlocked. Its "uniqueness-passed" label should not be read as clearance.
- **I10 (main's inventory is FAIL_CLOSED, and main's CI is red).** On `origin/main` (b0268bb), two TIFs are present in `docs/downloads` but not registered in `scripts/audit_public_downloads.py`:
  - `gemsdoe-karage2-near-trace-20261031.tif`: its run card says `"verdict": "promote"` with `ok_to_submit` stored as the string `'False'`. A promote-labelled raster in the public downloads is inconsistent with the negative-only policy. Not changed here, because the verdict belongs to the owning session.
  - `gemsdoe-blind-geothermal-rad-mag-grav-intersection-20261031.tif`: negative card, not registered.
  The checker therefore reports `FAIL_CLOSED`, and `build_hk3_pages.py` refuses to render the desk. Resolving this needs a decision from the repository owner (see the session question).

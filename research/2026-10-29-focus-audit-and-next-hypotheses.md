# Focus-site audit, gate decision and next hypotheses — 2026-10-29

**Decision: no file is approved for download or submission.** This session generated **no new TIFF**, ran **no
new model or holdout experiment**, and used **zero** of the protocol's experiment budget. Reason: every candidate
on this footprint fails the written uniqueness rule against the 13GEMSDOE lattice witness (see §2). Generating
another file would only reproduce the failure, so the work stopped at the policy decision the owner must make.

Labels used below: **MEASURED** = computed on SHA-256-pinned bytes in this session; **USER-REPORTED** = copied
from the prompt, no organizer receipt; **OFFICIAL** = read from an official page or document this session.
No HOLDOUT-DTI or ORGANIZER-CONFIRMED score is claimed here.

## 1. Verified facts (line by line)

| # | Claim | Label | Evidence (reproduce) |
| --- | --- | --- | --- |
| 1 | The metric is a distance-weighted Tversky index, alpha 0.2, beta 0.8, triangular kernel with 300 m support. | OFFICIAL | [Problem page 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), "Performance metric" |
| 2 | The private test set is faults that are **not contained in the public USGS database**. | OFFICIAL | Same page, "Problem description" and "Competition structure" |
| 3 | Values must lie in [0, 1], float32, one layer, 100 m, EPSG:32611. Data outside the bounds is **null or NaN**. | OFFICIAL | Same page, "Submission format" |
| 4 | Limit: **three submissions per week**. One GeoTIFF with a single raster layer. Generative-AI use must be described in the narrative. | OFFICIAL | [NLR Official Rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), §1.1 and §3.2 |
| 5 | Public leaderboard, fetched 2026-10-29: #1 xiaofanhu **0.4544**; #2 cfld__ 0.3916; kpomazi **0.3195 at #47**; drjy 0.3180 at #48. | OFFICIAL (public snapshot, not a receipt) | [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) |
| 6 | The prompt's "0.3195 is the highest score" is **incorrect** against this snapshot; 0.4413 does not appear on it. | IRREGULARITY | Compare #5 with the prompt |
| 7 | All nine pinned focus files match the SHA-256 in `registry/focus_sites.json`. | MEASURED | `scripts/audit_focus_gate.py` (fails closed on mismatch) |
| 8 | Each focus file is float32 with 37,654 to 61,328 dots, all inside the template footprint. Every finite value lies in [0,1]. Five files (GEMSDOE24, 25, 27, 28, 31) write NaN outside the footprint, matching the written format and the mirror template. Four files (GEMSDOE30, 32, 33, 36) write finite zeros, which departs from the written "null or nan" convention. | MEASURED | `evidence/focus-profile-2026-10-29.json`; direct read of pinned bytes |
| 9 | **Every** focus file stops as `DUPLICATE_STOP` against the lattice witness, with 99.91–99.92% of dots within 3 px. Spearman against the lattice is below 0.001 in all nine cases. | MEASURED, shared tool | `evidence/lattice-gate/*.json`, using `scripts/check_uniqueness.py` |
| 10 | The lattice witness has 206,895 dots on a 5-px grid and covers 99.87% of the footprint within 3 px. | MEASURED | `evidence/focus-profile-2026-10-29.json` → `lattice_witness` |
| 11 | GEMSDOE32 = GEMSDOE25 minus **6,436** dots; GEMSDOE32 = GEMSDOE31 minus 2,545; GEMSDOE32 = GEMSDOE36 minus 1,200; GEMSDOE25 = GEMSDOE30 (identical dot sets, different bytes). | MEASURED | `exact_subset_relations` |
| 12 | All 6,436 dots removed from GEMSDOE25 lie within 3 px of the mirrored catalogue (60% within 1 px). | MEASURED on the mirror, not organizer labels | `removed_dot_catalogue_profile` |
| 13 | Across the seven non-identical nested pairs, the smaller set has the higher user-reported score in **7 of 7**. These pairs are not independent: GEMSDOE25 and GEMSDOE30 share one dot set, so their pairs count twice. | MEASURED pairs, USER-REPORTED scores | Same receipt |
| 14 | Across nine sites, reported score vs share of dots within 3 px of the catalogue: Spearman **−0.983**. Dot count gives the identical value by coincidence of rank structure, and the two predictors correlate at **0.966**. | MEASURED, n = 9 | `correlations_nine_sites_user_reported_vs_measured` |
| 15 | The mirror `sample_submission.tif` has 60,988 positives, equal to the mirrored known-fault raster. The official page describes the sample as predicting **total absence**. | IRREGULARITY | `.cache/competition_data/` against the official page |
| 16 | `registry/focus_registry_manifest.json` holds 440 rasters from the nine focus repos only, with no completeness declaration. The prompt lists roughly a hundred sites. | IRREGULARITY, registry incomplete | `registry/focus_registry_manifest.json` |
| 17 | Cache paths for GEMSDOE25 and GEMSDOE27 sit under the GEMSDOE32 and GEMSDOE28 cache folders. The hashes match, so the bytes are correct, but the mapping is wrong. | IRREGULARITY (harmless) | `registry/focus_registry_manifest.json` `local` fields |
| 18 | The "Predicted values must be in range [0, 1]" error cannot be explained from the pinned bytes. The written convention is null or NaN outside the bounds. The template uses NaN, and four pinned focus files use zeros, which the strict check flags. Every finite value is inside [0,1]. Zeros lie inside [0,1], so by inference they do not by themselves explain a range message; the portal's behaviour is unverified. No portal receipt is available, so the cause is unknown. | UNRESOLVED | Prompt; official page; row 8 |

## 2. Why no file can pass the literal rule (and why this is not a file defect)

The written stop has two clauses: Spearman > 0.90 with any registry raster, **or** more than 70% of a file's dots
within 3 px of one registry raster's dots. Against the lattice witness the rank clause never fires. The dot clause
always does. The witness covers 99.87% of the footprint, so a dot placed at random on the footprint lands inside the halo
with probability about 99.9%. The only ways below 70% are (a) placing dots in the 6,649 uncovered cells, which
is gaming and is prohibited, or (b) changing the rule. Option (b) is the owner's decision (see the executive summary
policy section).

Because the nine historical files and any subset of them share this geometry, the result is not specific to
GEMSDOE32. A subset of GEMSDOE32 is a near-copy of GEMSDOE32, and GEMSDOE32 itself fails.

## 3. Interpretation of the 0.2778 result (PhD-level reading, not an established cause)

* The metric's asymmetry (false positive 0.2, false negative 0.8) rewards recall but penalises unsupported dots.
* The private set is non-catalogue faults (OFFICIAL). Dots on mapped catalogue faults earn credit only if a new fault
  lies within 3 px. Measured: the removed dots sit on the catalogue, and the surviving dots are the least
  catalogue-adjacent of the nine (5.8% within 3 px, median 19.6 px).
* The two explanations, dot count and catalogue proximity, are confounded (§1 row 14), and a nine-point user-reported
  correlation is not a causal test. A controlled organizer receipt would be needed: submit a file and its nested
  subset in the same week, within the three-per-week cap.
* **Catalogue-halo suppression is already known in this fleet.** `research/hypotheses-2026-10-28-k3-preregistration.md` and
  `research/review-2026-10-28-k2.md` describe an "off-catalogue >2 px" export rule (the champion-family discipline), and the HK3 lane used off-catalogue emission. The novelty claim for this idea is
  therefore **false**. What is new here is the nested-pair measurement, not the idea.
* **Trap for the next experiment:** on the public mirror catalogue, a dot-set that avoids catalogue pixels scores
  *worse*, because the mirror labels reward catalogue overlap. A holdout using mirror labels alone runs in the wrong
  direction. Only the hide-and-recover holdout (withheld buffered segments, visible faults masked) is a valid test.

## 4. Candidate hypotheses — untested, ranked by expected incremental utility and cost

These are qualitative rankings, not score forecasts. None has been implemented or tested here. The first four are the
existing untested slate in `research/2026-10-28-next-lane-slate.md` (proposals 1–4), restated with this session's
findings. Items 5 and 6 are new.

| Rank · cost | Layers / signature | Why it might find a fault missing from the catalogue | Named non-fault mimic and control | Status in this repo |
| --- | --- | --- | --- | --- |
| 1 · medium | Bands 13 `iso_grav_anom`, 11 `iso_grav_anom_vg`, 12 `det_elev`, 19 `det_elev_slope`. Block-fitted, label-blind terrain-residual gravity edge with a contour-aligned null. | A density offset may continue under alluvial cover beyond the mapped scarp. | Unfaulted sediment/bedrock contact or pluvial shoreline. Ablate the terrain regression; compare contour-following breaks. | Untested. H1 and B4 are related but do not fit this residual null. |
| 2 · medium/high | Bands 17 `cond_surf`, 13 gravity, 18 gravity horizontal gradient: transverse conductivity-Hessian saddle at an independent gravity break. | A covered offset could juxtapose conductive strata with no surface trace. | Saline playa margin or inversion seam. Ablate conductivity; band 15 excluded until its metadata is authenticated. | Untested. |
| 3 · medium | Bands 7 `geod_shearrate`, 8 `geod_dilaterate`, 2 `rtp`, 3 `tmi_hg`: strain-regime change times signed magnetic-edge persistence, with a shuffled-strain null. | A covered strand could lie near a regime change. Coarse strain alone cannot locate a 100 m fault. | Interpolation boundary or intrusive contact. Require marginal benefit over magnetic-only features. | Untested. Strain bands excluded in K2 and HK3. |
| 4 · low/medium | Bands 10 `deq_n100a15`, 16 `ieq_n100a15`, 11 gravity vertical gradient: seismicity sidedness across independent gravity edges. | Activity may point at an unmapped strand near a geophysical break. | Mining or production seismicity; shuffled-seismicity control. | Untested. Band meanings unverified. |
| 5 · low, **new** | **Nested-budget curve on the hide-and-recover holdout.** Sweep the dot budget and the catalogue-halo radius (0, 1, 2, 3 px) on one fixed predictor. Report DTI with a paired spatial CI. | Tests whether the nested-pair pattern in §3 holds under a controlled holdout, separating dot count from proximity. | Dot count is a proxy for coverage and the holdout's fault density. Control: vary the withheld-segment set. | Untested. Needs one predictor and the shared evaluator. |
| 6 · low, **new** | **Registry-complete audit for the whole prompt list.** Restore every GEMSDOE repo listed in the prompt, not only nine, then rerun the shared gate on the best candidate. | Prevents a conclusion from a partial registry. | Not a fault method; governance only. | Blocked by the policy decision in §2. |

## 5. Access checks and limits

* Reachable this session: DrivenData problem, leaderboard and rules pages (fetch tool); NLR Official Rules PDF (fetch tool); GitHub owner mirrors (`scripts/bootstrap_research.py`, `scripts/restore_registry_snapshot.py`). The shell's outbound allowlist does not include DrivenData or USGS, so organizer and USGS files were not downloaded. No organizer credentials were used.
* Not reachable: the organizer's data files, the submission page and the leaderboard receipt for any file. Scores here remain unverified.
* The mirror catalogue, labels and template are **not** organizer-authenticated.

## 6. Sources for manual review

* [Problem description, metric and submission format (page 967)](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
* [Public leaderboard (fetched 2026-10-29)](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
* [Official Rules, NLR, September 2026](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
* [DrivenData rules page (redirects to HeroX)](https://www.drivendata.org/competitions/306/competition-doe-gems/rules/)
* [GEMS reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
* [GeoDAWN, USGS](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [INGENIOUS, GBCGE](https://gbcge.org/current-projects/ingenious/), [EPSG:32611](https://epsg.io/32611), [Tversky index](https://en.wikipedia.org/wiki/Tversky_index)
* Reproduce: `.venv/bin/python scripts/audit_focus_gate.py` (needs the cache from `scripts/restore_registry_snapshot.py` and `scripts/download_competition_data.sh --research-mirror`).

# GEMS fault-prediction research workspace

> **Always read this brief before project work.** Work is judged by reproducible evidence and competition validity—not by the number of generated rasters or optimistic score claims.

## Purpose and operating brief

Build an auditable research and submission workflow for the DOE Geologic Enhanced Mapping System (GEMS) Prize Challenge. The goal is to discover previously unmapped faults relevant to geothermal systems and improve leaderboard performance using scientifically defensible, reproducible methods. Maximize the probability of a sound result; own the outcome end to end.

### Non-negotiable research and submission rules

1. **Use the active session branch only.** Preserve a traceable experiment record; do not commit generated competition data or large rasters unless project conventions explicitly require them.
2. **Inspect the repository and the available data before proposing implementation.** Reuse the project's cached feature stack, `evaluate_holdout.py`, and `submission_writer.py` if present. Fix shared tools in their shared location; do not create private duplicate evaluators or writers. If a referenced tool or dataset is absent, record that as a blocker rather than claiming it was used.
3. **Stay in the explicitly assigned method lane.** Before running experiments, document the lane and the novelty/duplicate guard. Compare the candidate surface before placement and final prediction dots against registry rasters: rank correlation must not exceed 0.90 and at most 70% of dots may lie within 3 pixels of any one registry submission. If a limit is exceeded, record a duplicate and stop that experiment. If the lane, registry, or compatible rasters are unavailable, do not claim uniqueness.
4. **Evaluate by hide-and-recover, not random pixel splits.** Withhold whole fault segments plus a buffer; derive every catalogue-based feature from visible faults only; mask visible faults pixel-exactly; evaluate pooled distance-weighted Tversky (DTI), alpha 0.2, beta 0.8, triangular kernel with 300 m support. Report evaluator version, withheld-positive count, and a 95% confidence interval. Run each feature alone as a leakage canary; AUC above 0.90 is presumed leakage until disproved.
5. **Do not confuse score types.** Every measured value must be labeled `HOLDOUT-DTI` with evaluator/version, withheld positives, and 95% CI, or `ORGANIZER-CONFIRMED` copied from a submission-page receipt. A projection is never a score. User-reported site scores without receipts are historical leads only, not verified results.
6. **Do not spend a competition submission slot without a holdout win.** Stop after at most three experiments or two hours per run. Selection/promotion to a real slot is a separate step subject to the competition's current weekly cap. Negative results are valid deliverables.
7. **A downloadable GeoTIFF is `OK TO SUBMIT` only after automated validation.** Validate one float32 band, all finite pixels inside the footprint, values within [0, 1], correct NoData outside, and exact match to the official/sample raster CRS, shape, bounds, and transform. Record raster SHA-256 and registry-correlation/overlap checks. Never fabricate an output grid or metadata when the template raster is absent.
8. **Be explicit about limitations and irregularities.** Do not claim external verification, a high score, an experiment, an official receipt, or uniqueness without evidence. If credentials or inputs block work, document the precise blocker and the minimum next action.

### Required run card

Every completed experiment ends with one JSON run card containing: hypothesis; mechanism; named non-fault process that could mimic the signal; holdout DTI and CI (or `null` with reason); correlation/overlap versus registry (or `null` with reason); raster SHA-256 (or `null`); validator output (or `not run`); submission name and a note of at most 140 characters; verdict `promote` or `negative`. Do not use `promote` unless all gates pass.

## Competition facts and primary references

The official problem description says the task is to predict geological faults, including faults absent from the publicly available catalogue; labels and existing faults are imperfect/incomplete. It describes GeoDAWN feature data, INGENIOUS/USGS fault labels, and expert-reviewed new-fault scoring. The official submission description requires EPSG:32611, 100 m resolution, matching bounds, one float32 layer with confidence values from 0 to 1, and null/NaN outside the footprint. The metric is distance-weighted Tversky with alpha 0.2, beta 0.8, and a 300 m triangular distance kernel. See the official links below and `docs/executive-summary.md` for the current review and limitations.

- [Competition problem, metric, datasets, and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition rules](https://www.drivendata.org/competitions/306/competition-doe-gems/rules/)
- [Competition data download (login may be required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [DOI 10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [EPSG:32611](https://epsg.io/32611)

## Current repository status (reviewed 2026-10-27 UTC)

This checkout contains only this README and the initial Git commit. There are no cached features, competition/sample rasters, fault catalogue, registry-raster inventory, evaluator, writer, experiments, tests, or site implementation here. Therefore this checkout cannot presently run the mandated holdout, verify the nine-site duplicate guard, or safely create a competition-compatible GeoTIFF. **No generated file from this checkout is approved for download or submission.** This is an evidence-based negative result, not a score claim. See the executive summary for the focused site-by-site review, candidate hypotheses, and blockers.

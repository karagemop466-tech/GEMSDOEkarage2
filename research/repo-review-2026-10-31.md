# Repository review — 2026-10-31

## Executive finding

**No file in this checkout is presently authorized for submission.** The existing HALO GeoTIFF is available as a research download, but its release audit excludes the lattice witness from the ordinary duplicate count while the user-provided binding rule says to stop if overlap exceeds 70% with *any registry raster*. The audit records 99.84% of HALO dots within 3 px of the registered lattice raster. By the literal rule, this is a duplicate-stop. HOLDOUT-DTI is 0.1367 at 44,090 dots, below the recorded K3 incumbent 0.19157. The newly merged independent GBM candidate also fails the literal stop: its lane evidence records 99.67% lattice overlap and 93.77% overlap against a non-lattice registry raster; its HOLDOUT-DTI is 0.01719 [0.01300, 0.02269] across 60,661 withheld positives (11 of 16 folds). That raster is explicitly `negative_research_only` in its run card. These findings do not support any claim of an approved or top-scoring local file.

No new experiment or new TIFF was generated. The binding lane already recorded in the repo is S1 (seismicity-flank context); it has been run and is negative, and its protocol budget is spent. The prepared feature cache and template data are also absent in this checkout (`data/` does not exist; ignored `.cache/` inputs are not present), so this review cannot independently rerun the generator, evaluator, or raster validator from source. Generating another surface would violate the requested single-lane / do-not-drift rule and would produce unverifiable claims.

## Nine-site summary

The nine audited historical leaders and quoted values are in [`docs/data/nine-site-scorecard.json`](../docs/data/nine-site-scorecard.json) and the linked per-site pages under [`docs/focus/`](../docs/focus/). The quoted values are **USER-REPORTED / UNVERIFIED**, not organizer receipts. The repository reports the highest of the listed nine as GEMSDOE32 at 0.2778. Byte/raster checks show those nine are highly overlapping: several files form nested or near-identical dot patterns, and the focus audit reports the focus bests as non-unique under the project's 70%-within-3-px rule. The number is not evidence of nine independent discoveries or a defensible prospective score estimate.

The supplied leaderboard figures (0.4413 and 0.3195) are not current receipts. The repository's dated 2026-10-31 leaderboard observation says rank 1 was 0.4544 at that observation time; this was not independently checked against a live authenticated competition account in this review. Treat every historical board/score claim as timestamped context, not current truth.

## Candidate status / evidence labels

| Artifact | What is measured | Decision |
|---|---|---|
| HALO `gemsdoe-karage2-halo39-b44090-sep2-20261031.tif` | Saved-byte audit claims single-band float32, EPSG:32611, 3730×3292, exact recorded transform, finite [0,1], 44,090 dots and SHA-256 `603be6bfb38eddf6be024103a75958027846a93476ecb7529ec958d4a32e5c38`. HOLDOUT-DTI 0.136655 at the released count; evaluator/folds/metric details are in its committed run card. | **Research-only; do not submit**. Literal lattice comparison is over the threshold. The final holdout is below the recorded K3 0.19157. The TIFF and receipt are retained unchanged for audit. |
| S1 seismicity-flank candidate | HOLDOUT-DTI 0.18791, 95% CI [0.16799, 0.20782], 58,308 withheld positives, evaluator `gems57-pooled-hide-v2`; below K3 0.19157 [0.17474, 0.20880]. | Negative; no slot. Run card and detailed evidence: [`evidence/s1/`](../evidence/s1/). |
| K10 corridor alternative | Format/registry audit exists; no validated leaderboard score estimate or demonstrated improvement over incumbent. | Not promoted; not a replacement recommendation. |

The estimated-score range previously displayed for HALO is **CALIBRATED-PRIVATE projection**, conditional on assumed hidden-fault hit rates; it is not HOLDOUT-DTI and not ORGANIZER-CONFIRMED. It must not be described as its score or as proof it beats 0.2778, 0.3195, or the leaderboard leader. There is no organizer receipt tied to HALO's hash in this repository.

## Failure found and repaired

The earlier site and README said HALO was “OK TO DOWNLOAD AND SUBMIT” even though `evidence/halo/uniqueness_final.json` and `docs/downloads/...audit.json` record a literal uniqueness failure (`stop_required: true`, lattice overlap 0.9983897). The same code separated “universal probes” from submissions to call uniqueness clear, but that exception is not in the user's supplied rule. This was a material contradiction. Updated the release-page generator/output and landing page to show **NOT OK TO SUBMIT**, keep the TIF downloadable as a research artifact, and state the failed gate. No raster bytes were edited.

The historical pre-placement surface evidence also reports that 55 non-lattice raster comparisons exceeded the 70% overlap rule. That further undermines a blanket claim that the prior HALO implementation passed the stated protocol, even though the final ordinary-submission-only comparison was below threshold.

## Three review passes

1. **Evidence audit:** read the current decision at README top, focus scorecard, release run card, HALO audit, S1 evidence, and submission pages. Found the release-vs-literal-gate mismatch and absent input data.
2. **Correction:** changed the release generator and generated release page to label HALO research-only; changed landing banner and README current decision accordingly; updated the release regression test to require the stop language.
3. **Recheck:** ran the complete Python suite after installing declared requirements into an isolated temporary virtualenv: **302 passed, 10 skipped, 98 subtests passed**. Rasterio emitted 101 deprecation warnings. These tests exercise committed artifacts and synthetic cases; they do not constitute organizer acceptance or a rerun against missing competition inputs. The real standalone raster validator cannot run here because no template/cache input exists.

## Ranked future hypotheses already documented

The repository's five-idea slate is [`research/hypotheses-2026-10-31-untried-slate.md`](hypotheses-2026-10-31-untried-slate.md). S1 was rank 1 and is now tested negative; the slate identifies S2 terrain-residual gravity edge, S3 strain-regime change × magnetic-edge persistence, S4 gravity/conductivity break coincidence, and S5 thermal-spring / alteration corridors requiring external data. These are hypotheses, not results. Do not run a new lane until the owner assigns it and the shared template inputs are restored. In particular, S5's free official-data availability is explicitly unverified in that record; do not call it viable until that fetchability is demonstrated.

## Limitations and next actions

1. Restore the actual competition/template rasters and cached stack from authorized sources into the expected ignored locations; verify hashes and provenance before execution. Do not treat the public owner mirror as organizer-authenticated.
2. Obtain a clear policy interpretation for whether the intentionally dense lattice is a registry raster for the uniqueness rule. Until then, apply the literal rule and stop; do not silently exclude it.
3. Reconcile the generated landing/dashboard pages and all cached or older pages so there is one consistent current status. Current changes cover README, `docs/index.html`, generated `docs/release.html`, and its generator; old/archived pages can still contain historical approval language and should be visibly marked as superseded.
4. Obtain a real organizer submission-page receipt if upload is ever authorized. Local format validation is not portal validation. Confirm organizer grid and exterior/nodata conventions before upload.
5. Refresh leaderboard observations from the official page and tie any score statement to an organizer-confirmed receipt with its file hash; do not infer a score from the holdout.
6. Only then run the next assigned experiment within the three-experiment/two-hour cap, with feature-alone leakage canaries, whole-component spatial hide-and-recover, surface pre-check, final-dot check, and a protocol-complete card. A negative outcome is a valid deliverable.

## Official references for manual review

- DrivenData competition overview/rules: <https://www.drivendata.org/competitions/306/competition-doe-gems/>
- Problem description: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- Competition data page (requires authenticated access, as documented in the repo): <https://www.drivendata.org/competitions/306/competition-doe-gems/data/>
- Official reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution>
- USGS GeoDAWN source: <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and>
- GBCGE INGENIOUS: <https://gbcge.org/current-projects/ingenious/>
- EPSG:32611: <https://epsg.io/32611>
- Submitted focus-site pages and file-level hashes are linked in the scorecard/audit receipts above. Scores from those pages remain user-reported unless backed by a submission-page receipt.

## Run card (review-level; no new experiment)

```json
{
  "hypothesis": "The HALO release is not protocol-eligible under the literal registry uniqueness rule; no replacement hypothesis was run in this review.",
  "mechanism": "The 3-pixel overlap gate catches the registered lattice witness as well as ordinary competition rasters; the repository's prior exception was not authorized by the stated rule.",
  "named_non_fault_process": "A uniform lattice is a sampling/design probe, not a geological signal; it can trivially overlap most feasible placements and exposes a policy-definition problem rather than fault prediction skill.",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "gems57-pooled-hide-v2",
    "withheld_positives": 58308,
    "dti": 0.136655,
    "confidence_interval_95": null,
    "note": "HALO value at 44,090 dots is from committed run card; CI not recorded for this field. S1's separate value is 0.18791 [0.16799, 0.20782] at 58,308 positives."
  },
  "correlation_overlap_vs_registry": {
    "spearman_max_abs_ordinary_submission_inventory": 0.055667,
    "max_overlap_ordinary_submission_inventory": 0.654661,
    "lattice_witness_overlap_within_3px": 0.998390,
    "thresholds": {"spearman_abs": 0.90, "overlap": 0.70},
    "verdict": "duplicate-stop under literal all-registry rule"
  },
  "raster_sha256": "603be6bfb38eddf6be024103a75958027846a93476ecb7529ec958d4a32e5c38",
  "validator_output": {
    "status": "committed saved-byte audit PASS; standalone rerun unavailable because template/cache absent",
    "no_nan_inside_footprint": true,
    "values_in_0_1": true,
    "crs_shape_transform_match_recorded_template": true,
    "organizer_acceptance": "unknown"
  },
  "submission_name": "gemsdoe-karage2-halo39-b44090-sep2-20261031",
  "note": "Research-only historical field; literal lattice uniqueness gate fails. DO NOT SUBMIT.",
  "verdict": "negative"
}
```

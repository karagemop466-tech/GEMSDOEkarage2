# Three-pass repository review — literal duplicate stop and release status

**Date:** 2026-10-28 (UTC)
**Scope:** repository review and safety correction only. No new geological experiment, model fit, dot placement, competition upload, or weekly-slot selection was performed.

## Executive disposition

**NO APPROVED TIFF — DO NOT SUBMIT the current HK3 file.** The historical HK3 artifact is locally format/range-valid on the pinned owner-mirror grid, but its saved final dots violate the current prompt's literal duplicate criterion: the registry audit reports **99.8626%** of candidate dots within 3 px of the r13 lattice raster, above the **70%** stop. The registry audit is also incomplete (452 of 453 expected entries). These are sufficient to withhold upload; the fact that the r13 3 px halo covers almost the whole footprint, or that its associated raster is called a control, cannot create an exception absent from the current protocol. In addition, the prompt does not supply a uniquely identifiable coordinator-assigned method paragraph; the prior HK3 lane was self-declared. Its three-experiment budget is exhausted.

At review start, the run card and selector authorized research download despite a historical `PROMOTE` decision that explicitly waived literal all-registry failures. The pre-correction selector is preserved as `evidence/hk3/selector_result-historical-promote.json`; the prior `PROMOTE` decision and reason are archived in `evidence/hk3/approval-retracted-20261028.json` and the repository's Git history. The current run card is now `NEGATIVE`, and this review's hash-bound assessment and site guidance remain research-only. No model measurements or raster bytes were changed.

## Three passes

### Pass 1 — inventory and evidence trace

- Confirmed the working tree began clean on the Arena-assigned branch and read `README.md`, `AGENTS.md`, the current HK3 run card/selector, prior review notes, the website generator, shared download audit, public pages and tests.
- The main download page, summary and how-to page were driven from the historical HK3 run-card verdict. As a result, the site declared “OK TO SUBMIT” despite a recorded literal registry failure and `literal_rule_exception_applied=true`.
- `evidence/hk3/registry_audit.json` reports `stop_required=true`, `unique=false`, `worst_dot_overlap=0.9986255209718897` (45,046 of 45,108 candidate dots within 3 px of the r13 lattice), and `complete_accessible_scan=false` (452/453 expected entries). The root run card separately reports three U2 literal-rule failures above 70%.
- The 9-focus-site-only comparison passes, but that narrower scope cannot override the user's all-registry rule. The old run card's `PROMOTE` verdict was conditional on a literal-rule exception, as its `verdict_logic` records.
- HK3's historical same-session result is HOLDOUT-DTI 0.1845047 [0.1676914, 0.2014840] under `gems57-pooled-hide-v2` with 58,258 withheld positives. The K3 card records HOLDOUT-DTI 0.19157 [0.1747, 0.2088] under the same evaluator/count. The intervals overlap and there is no paired cross-session test. Therefore the repo does not establish that HK3 beats the current recorded holdout-best; neither figure is an organizer score.
- The local format validator records no NaN and values in [0,1] with the pinned owner-mirror grid. It does not authenticate the organizer template or prove portal acceptance. No precise cause for the user's earlier range error can be diagnosed without the exact rejected bytes and receipt.
- The public-download inventory previously labelled HK3 `VERIFIED_CANDIDATE_FOR_UPLOAD` and emitted `PASS_ONE_CANDIDATE_FOR_UPLOAD` because the audit excluded the literal uniqueness failure from hard-gate aggregation. This was a safety-critical gate defect.

### Pass 2 — safety changes

1. Added `evidence/hk3/current_release_assessment.json`, binding the negative decision to the saved TIFF SHA-256 and documenting the literal registry stop, incomplete scan, missing pre-placement clearance, unproven holdout superiority, and unauthenticated inputs.
2. Preserved the former selector JSON byte-for-byte as `selector_result-historical-promote.json`; changed current `selector_result.json` to `negative_research_only`, `ok_to_submit=false`, and `slot_authorized=false`.
3. Changed the generated Pages decision to derive from the current assessment and current selector, not the historical run-card verdict. The artifact may be downloaded only as a clearly labelled research copy; all upload instructions now warn not to submit it.
4. Tightened `audit_public_downloads.py`: a literal U2 failure is no longer waived; it requires a current hash-bound negative assessment to classify an otherwise intact TIFF as research-only. Its current inventory must not identify an upload candidate.
5. Updated README and AGENTS.md so the current no-submit status supersedes outdated upload instructions.

### Pass 3 — remaining checks and scientific hypothesis slate

The strict release correction is a documentation/control-plane change, not a new model experiment. The previous HK3 lane had already consumed three experiments and exceeded the stated two-hour budget; no candidate was tested here. The only candidates below are **prospective hypotheses**, not proven untried worldwide and not validated or score-ranked empirically. Repo searches found no exact implementation of the first two named feature combinations; related derivatives and general texture features do exist, especially in K2/K3/HK3. New experiments remain blocked until an authorized lane, complete registry and source provenance are resolved.

| Rank / expected DTI upside (qualitative, unvalidated) | Hypothesis; specific existing layers | Physical signature and why it could identify catalogue-missing faults | Main non-fault mimic | Difference from this repository; implementation cost / external data |
|---|---|---|---|---|
| 1 · **Moderate potential, unquantified** | **Conductivity saddle conditioned on independent gravity break** — band 17 `cond_surf`, band 13 `iso_grav`, band 18 `grav_hg`; use a signed conductivity-Hessian saddle across a gravity-gradient edge, rather than conductivity amplitude alone. | A covered fault could juxtapose conductive basin fill across a density boundary even when its surface trace was not mapped. Require spatially co-located, differently measured signatures; do not call conductivity itself a geothermal vent. | Saline groundwater, playa/clay margins, inversion seams, intrusive/lithologic density contacts. | Repo tests conductivity values, gradients, and textures but no recorded explicit signed conductivity saddle *conditioned across* an independent gravity break. Medium feature engineering; existing stack only, but authentic band meanings/units must be verified. |
| 2 · **Low-to-moderate potential, unquantified** | **Potential-field edge persistence across scale** — bands 2 `rtp`, 13 `iso_grav`, and 15 `depth_base` only if its semantics are confirmed; compute whether an edge/zero crossing remains positionally stable through predeclared smoothing scales, then test multi-channel concordance. | Persistent, spatially stable edges may distinguish a real basement/structural boundary from short-wavelength noise and survey artifacts, including covered faults lacking topographic expression. | Long lithologic contacts, intrusive margins, basin boundaries, processing seams. | K2/K3/HK3 already use gradients, DoG, tilt, tensor and Hessian features; the proposed target is scale-space *edge location persistence*, not another raw gradient or coherence measure. Medium cost, no new data if stack metadata is authenticated. |
| 3 · **Low/uncertain potential; high bias risk** | **Fold-local catalogue observation-process correction** — public 19-band lineament transforms plus only visible fault segments per holdout fold; estimate spatial variation in mapping intensity and test a pre-registered missing-not-at-random correction. | Catalogue gaps can reflect uneven mapping/cover rather than geology; combining visible map density with independent lineament evidence may prioritize plausible unmapped structures without leaking withheld segments. | Access, survey and map-production effort; lithology-controlled lineament density. | No explicit sampling-process correction is recorded as validated in this repository, though mapping-deficit ideas were proposed previously; treat as previously proposed, not novel. High leakage/causal risk; medium implementation; no new external data. |

Qualitative ranking is by potential information gain and implementation feasibility, **not a DTI score or prediction**. Candidate 1 is the most bounded prospective test, but the exact 19-band semantics and cached feature stack were not present locally in this checkout at review time (the `data/` and `.cache/` directories were absent). The user asks to reuse cached inputs; do not regenerate/rebuild them in this review. The experiment budget and stop gate also preclude running it now.

The 1 m lidar scarp/curvature idea from USGS 3DEP via The National Map is a physically plausible separate avenue, but it needs new external tiles. This sandbox's documented host allowlist does not include `usgs.gov` or `apps.nationalmap.gov`; retrieval was not possible here, so obtainability was **not verified** and that idea is not proposed as a viable next experiment. Competition files behind DrivenData login likewise were not authenticated here. See the official manual-review links below.

## Official references for manual review

These links are copied from the project source ledger; this review did not access DrivenData or USGS hosts from the sandbox. The organizer's reference repository is the only official source in the link set that can be verified via GitHub here; a GitHub URL alone does not authenticate owner-mirror raster bytes.

- [DrivenData competition / rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData data page (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Organizer reference solution on GitHub](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN airborne magnetic/radiometric data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) and [The National Map downloader](https://apps.nationalmap.gov/downloader/)
- [EPSG:32611](https://epsg.io/32611)

## Limits and next actions

1. Keep all site banners and downloads at **DO NOT SUBMIT** until every required gate is met. Do not choose/spend the weekly slot.
2. Resolve registry scope and refresh a complete inventory. Any >70% 3 px overlap or rank correlation >0.90 is a stop under the current prompt; do not waive it for a lattice/control/surface entry.
3. Obtain and hash-authenticate organizer input rasters, official template, band definitions/units and exterior convention; obtain a portal receipt for any eventual accepted file.
4. Establish a same-fold, visible-fault-only current holdout incumbent and run per-feature leakage canaries. Any future candidate must improve on that incumbent with paired spatial-block CI before final dots are placed.
5. Only after authorized lane and all safety gates, preregister at most three experiments; reuse the shared evaluator/writer and cached stack rather than a private fork.
6. The supplied leaderboard claims conflict (0.3195, 0.4413, 0.4544). They are user-reported snapshots unless tied to an organizer receipt. No leaderboard estimate in this repository should be treated as a score.

## Run card for this review

```json
{
  "hypothesis": "No new geological experiment; audit the current release gate against the literal protocol.",
  "mechanism": "A duplicate-stop check compares final positive pixels to registry rasters within 3 px; release guidance is now fail-closed.",
  "named_non_fault_process": "The r13 regular lattice is a geometric control, not a geological process; plausible HK3 physical mimics remain lithologic contacts, shorelines, terrace risers and flight-line striping.",
  "holdout_dti": {"evidence_class": "HOLDOUT-DTI", "evaluator_version": null, "withheld_positive_pixels": null, "dti": null, "ci95": null},
  "correlation_overlap_vs_registry": {"surface_before_placement": "not established under literal full-registry scope", "final_dots": {"max_within_3px_overlap": 0.9986255209718897, "reference": "r13 lattice"}},
  "raster_sha256": "064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9",
  "validator_output": {"no_nan_inside_footprint": true, "values_in_0_1": true, "crs_shape_transform_match": "pinned owner-mirror template only", "organizer_template_authenticated": false},
  "submission_name": "gemsdoekarage2-hk3-edgecentrality-apron3-20261028",
  "submission_note": "HK3 research raster; literal registry-overlap stop. DO NOT SUBMIT.",
  "verdict": "negative"
}
```

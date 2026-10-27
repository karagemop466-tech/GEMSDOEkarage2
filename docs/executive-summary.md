# Executive summary — repository review and submission readiness

**Review date:** 2026-10-27 UTC  
**Status:** `NO SUBMISSION APPROVED` · no GeoTIFF generated  
**Reason:** this repository checkout has only `README.md`; the required data, cached feature stack, shared evaluator/writer, registry rasters, and prior submission artifacts are absent. Generating a raster without the official sample/template grid would risk the exact shape/transform/range failure the project is meant to prevent. An invented score or a fabricated “unique” claim would not be scientifically defensible.

## Decision at a glance

- **Best reported historical result among the nine requested sites:** GEMSDOE32 entry `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`, shown by the user as **0.2778 (USER-REPORTED historical site value; unverified here; not HOLDOUT-DTI and no organizer receipt supplied)**. This is the highest value in the nine-site subset as represented in the prompt. It is a lead to investigate—not a submission recommendation. The linked public page may provide code/artifacts, but its score alone does not reveal the mechanism, test split, parameterization, data leakage risk, or whether the downloaded raster matches the current official template.
- **No conclusion can be made that it can be beaten.** That requires the prior raster, comparable data, an evaluator-compatible spatial holdout, and repeated evidence. No projected score is supplied.
- **Do not download/submit a file from this checkout.** There is no `.tif` here. No candidate passed a holdout, uniqueness guard, or format validator. No weekly submission slot should be used.
- **Score irregularity:** the prompt gives both 0.3195 and 0.4413 as “current” high scores. These conflict and neither comes with an official submission receipt in this checkout. The current leaderboard needs to be checked directly before treating either as current. The values below are copied from the user's prompt and are not independently verified.
- **Protocol irregularity:** the prompt specifies a “single method paragraph” to define the parallel lane, but no unambiguous single-method paragraph is present. The registry rasters needed for correlation/overlap checks are also missing. This review does not invent the lane or run an experiment outside it.

## Focused site-by-site comparison

The score and candidate names in this table are **USER-REPORTED historical site values copied from the request**. They are not `HOLDOUT-DTI` (no evaluator/version, withheld-positive count, or CI supplied) and are not `ORGANIZER-CONFIRMED` (no submission-page receipt supplied). “Unique?” means *not verifiable from this repository*; names and scores do not establish raster uniqueness. Links point to the named public result sites for manual provenance review.

| Site | Highest value/name supplied for that site | Historical value label | Best-to-submit decision | Uniqueness / artifact state |
|---|---|---|---|---|
| [GEMSDOE24](https://buffedlizard55-lab.github.io/GEMSDOE24/) | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | USER-REPORTED 0.2477; unverified | No promotion decision permitted; investigate only | Raster and registry comparison unavailable |
| [GEMSDOE25](https://buffedlizard55-lab.github.io/GEMSDOE25/) | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | USER-REPORTED 0.2600; unverified | No promotion decision permitted; investigate only | Raster and registry comparison unavailable |
| [GEMSDOE27](https://buffedlizard55-lab.github.io/GEMSDOE27/) | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | USER-REPORTED 0.2449; unverified | No promotion decision permitted; investigate only | Raster and registry comparison unavailable |
| [GEMSDOE28](https://buffedlizard55-lab.github.io/GEMSDOE28/) | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | USER-REPORTED 0.2710; unverified | Highest listed entry for this site; not a recommendation | Raster and registry comparison unavailable |
| [GEMSDOE30](https://buffedlizard55-lab.github.io/GEMSDOE30/) | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | USER-REPORTED 0.2600; unverified | No promotion decision permitted; investigate only | Raster and registry comparison unavailable |
| [GEMSDOE31](https://buffedlizard55-lab.github.io/GEMSDOE31/docs/) | `h27-4-solo-d28-20261004-8acb75e1-nan` | USER-REPORTED 0.2708; unverified | Highest listed entry for this site; not a recommendation | Raster and registry comparison unavailable |
| [GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | USER-REPORTED 0.2778; unverified | Top value in the requested-site list, but selector/promotion is out of scope and evidence is insufficient | Raster and registry comparison unavailable |
| [GEMSDOE33](https://buffedlizard55-lab.github.io/GEMSDOE33/) | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | USER-REPORTED 0.2632; unverified | No promotion decision permitted; investigate only | Raster and registry comparison unavailable |
| [GEMSDOE36](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/) | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | USER-REPORTED 0.2750; unverified | Highest listed entry for this site; not a recommendation | Raster and registry comparison unavailable |

The list above picks the maximum of the values supplied for each of these nine sites, not a verified maximum over every artifact on each site. In particular, GEMSDOE28 includes multiple close user-reported historical values (0.2708, 0.2649, 0.2710, 0.2707); the highest supplied is 0.2710. These are not comparable holdout estimates absent confirmed split and scorer provenance.

## What can and cannot be inferred about the GEMSDOE32 result

The challenge's official description says it evaluates previously unmapped faults, not simply reproduction of known catalogue lines. It explains that the existing public fault set is incomplete and may be inaccurate, and that the initial prize round uses a private expert-labeled set of new faults. Therefore a high score could plausibly reflect useful generalization to unseen structural expression, but **the reported value and submission name cannot establish why it scored well**. In particular, the suffix `zeros` is not proof of the raster's NoData policy, the model, or any geologic mechanism. Determining causality requires the actual raster, notes/code, exact competition scoring context, and a clean re-run of the prescribed blocked holdout.

No submission can be said to beat this value or the separately user-reported leaderboard values from the information present. The official metric is distance-weighted Tversky; a score projection from a different split is not an organizer score.

## Pre-implementation hypothesis shortlist

These are **testable candidate ideas, not established novel methods**. The checkout contains no implementation inventory beyond its README, so the repository review can say they are not implemented *here*, but cannot certify that other GEMSDOE sites or collaborators have never tried them. The long list of past site names in the request is not enough to rule out conceptual or raster duplicates. Rank is a qualitative expected-value judgment for a low-cost first test, not a predicted score. All candidates use data/layer families the official problem description says are provided or describes; access to actual competition files is still blocked by their absence here.

| Rank | Candidate hypothesis / layers | Physical signature and why it may identify a catalogue-missing fault | Difference from this checkout and known user-listed experiments | Holdout feasibility / cost | Main non-fault mimic |
|---|---|---|---|---|---|
| 1 | **Drainage-network deflection and catchment asymmetry** using detrended elevation and slope (plus 1 m DEM if locally available). | A shallow, unmapped structure may offset or guide channels, producing a consistent change in channel azimuth, tributary junction geometry, or opposing catchment asymmetry, even where no obvious scarp survives. Test only spatially coherent anomalies, not generic drainage density. | No drainage topology feature exists in this repository. This differs from the user-listed scarp/ridge/topographic gap-closure approaches in mechanism (channel-network response rather than direct lineament/scarp extraction), but cross-site novelty is unverified. | **Best first test; medium cost.** Can use existing raster layers if the cached stack includes them. Segment-blocked holdout possible; ensure channel extraction itself does not use hidden labels. | Lithologic contrasts, stream capture unrelated to active faulting, roads/ditches, DEM artifacts, and arid drainage noise. |
| 2 | **Multiscale strain-localization persistence** using dilatation rate, shear strain rate, and the second invariant of strain rate. | A buried or subtle fault may appear as a spatially persistent narrow gradient/transition across scales rather than as a catalogue-like line. Requiring orientation and scale persistence may reduce isolated noisy strain anomalies. | No strain calculation exists here. The user lists a prior seismicity/strain submission (`s33-seisdil-strain-seismicity`), so simple strain/seismicity fusion is already represented; the proposed test is specifically scale-persistent strain-gradient morphology and must be checked against its raster/method before proceeding. | **Low-to-medium cost.** Uses listed feature layers; a holdout is feasible. Leakage canary must score each strain feature/transform alone. | Regional tectonic strain, interpolation artifacts, or broad deformation not associated with a mapped surface fault. |
| 3 | **Conductivity-boundary / conductive-base step concordance** using surface conductivity and depth to conductive base, with magnetic edge support only as an independent check. | A fault may juxtapose or focus conductive alteration/fluids, leaving a sharp boundary or step in conductivity/depth where the fault itself is absent from the catalogue. Requiring cross-layer concordance can suppress a single-layer anomaly. | No conductivity-derived feature exists here. User-listed geothermal/hydrothermal submissions make broad thermal/conductive targeting a known conceptual family; novelty is limited to a boundary/step test and is not proven across sites. | **Low cost if both channels exist in cached stack; otherwise blocked pending feature metadata.** | Saline basin sediments, clay-rich alteration without a fault, groundwater, and survey seams. |
| 4 | **Survey-artifact-resistant magnetic edge persistence** using GeoDAWN total magnetic intensity plus its vertical/horizontal slope layers, with flight-line direction and survey-block boundaries treated as nuisance covariates. | A fault cutting magnetic basement may create a coherent edge/gradient extending across local noise; requiring persistence across scales and excluding flight-line-aligned features could expose buried structures while avoiding faults already present in the catalogue. | The official page lists these magnetic products; the user history includes magnetic/geophysical/lineament experiments. Thus the geology family is not novel. This is only a distinct artifact-control formulation, and it should rank below methods with stronger differentiation. | **Medium cost.** Feasible if the cached stack and flight-line metadata are present; external flightline data may be needed. | Lithologic contacts, dikes, remanence, magnetic-source-depth variation, and processing/flight-line seams. |

### Candidate choice gate

The prompt's required first candidate is **rank 1 drainage-network deflection/catchment asymmetry**, based on differentiation from scarp and gap-closure names and on use of provided topographic layers. This is a provisional research priority, **not a selected submission strategy**. No experiment was run because the input rasters, cache, evaluator and lane definition are absent. Its advancement requires a complete holdout result better than the repository's reproducible current holdout best, a per-feature leakage canary, registry correlation/overlap checks, and a passing submission validator. A public score, including the user-reported GEMSDOE32 score, is not a substitute for that holdout.

## Official-source verification and manual review links

| Fact used | Primary source and scope |
|---|---|
| Prediction target is faults; public catalogue is incomplete/imperfect; test faults are expert-labeled | [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| Provided features, 100 m grid/EPSG 32611, metric, and expected GeoTIFF values/format | [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| Official simple modeling reference | [DrivenData reference solution repository](https://github.com/drivendataorg/gems-prize-reference-solution) |
| GeoDAWN airborne magnetic/radiometric and associated lidar context; official USGS data release | [USGS GeoDAWN page](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [USGS DOI](https://doi.org/10.5066/P93LGLVQ) |
| INGENIOUS project context | [Great Basin Center for Geothermal Energy](https://gbcge.org/current-projects/ingenious/) |
| CRS identifier | [EPSG:32611](https://epsg.io/32611) |
| User-reported site values/artifacts | Nine site links in the comparison table; not official receipts and not independently verified in this review |

## Submission workflow and status

Official submission-format requirements from DrivenData are summarized above. To make a future download genuinely safe, the project still needs its shared validation and writer tools connected to the official sample/template. The intended automated path is:

1. Load sample/template and candidate rasters; reject missing inputs or a grid mismatch.
2. Check single-band float32, CRS, shape, transform, bounds, footprint NoData, finite in-footprint values, and min/max in [0, 1]. Fail closed on any mismatch or NaN inside the footprint.
3. Run the same evaluator used for the hide-and-recover test and write metrics with evaluator version, withheld-positive count, and 95% CI.
4. Compare rank correlation and dot overlap against every registry raster, both before and after placement. Reject/label duplicate when thresholds in the README are crossed.
5. Write a SHA-256 manifest, unique submission slug and <=140-character note only after every gate passes. Show a conspicuous `OK TO SUBMIT` download affordance only for a passing artifact.

**Current result:** steps 1–5 could not run; no raster, score, confidence interval, validation output, or registry comparison was produced. No unique `.tif` was generated. No file is safe to download/submit from this checkout.

## Limitations, blockers, and next work

1. **Competition input data absent.** The official data tab can require a user login. No credentials are available to this process, and the prompt itself notes that competition downloads redirect to login. Do not attempt to bypass access controls. The user-provided Dropbox links are not treated as independently verified inputs here. Minimum unblock: place authorized `training_features.tif`, labels/fault data, `sample_submission.tif`, and relevant DEM link/data under the project's documented data convention.
2. **Shared project implementation absent.** The stated cached feature stack, `evaluate_holdout.py`, `submission_writer.py`, download/preparation scripts, UI/site, tests, and README-described prior pipeline are not in this checkout. Reuse cannot be fulfilled until the expected template/repository or artifacts are present; reconstructing a private evaluator/writer would violate the stated protocol.
3. **No holdout baseline.** A reproducible current holdout best and its CI are required to judge the candidate. Public organizer values cannot directly validate spatially blocked performance.
4. **No registry rasters.** User-supplied site pages and model names are not pixel arrays; exact or near-duplicate checks cannot be performed without the raster downloads and a common grid.
5. **Leaderboard/source-date ambiguity.** The prompt has inconsistent current-high-score figures. Check the official leaderboard and retain a dated receipt/snapshot before comparing.
6. **No automated current feed or website.** No app/CI/static-site files exist; this review adds documentation only. Do not imply that a GitHub Pages site or live feed exists.

**Immediate next work:** restore/add the intended shared project template to this branch (without forking its evaluator/writer), place authorized input files, resolve the method lane from the session's method paragraph, capture registry files, run the rank-1 candidate's blocked holdout plus leakage canaries, and publish a result card. Only a holdout-promoted, de-duplicated, format-valid raster may become a downloadable candidate; promotion to an actual competition slot remains separate.

## Required run card for this review (negative result)

```json
{
  "hypothesis": "Drainage-network deflection and catchment asymmetry may reveal unmapped faults using detrended elevation and slope.",
  "mechanism": "Fault-related channel offsets, azimuth changes, or catchment asymmetry may persist where direct scarps are absent.",
  "named_non_fault_mimic": "Lithologic drainage contrasts and stream capture unrelated to faulting.",
  "holdout_dti": null,
  "holdout_ci_95": null,
  "holdout_evaluator_version": null,
  "withheld_positives": null,
  "holdout_reason": "Not run: no rasters, cached stack, or shared evaluator in checkout.",
  "correlation_overlap_vs_registry": null,
  "correlation_overlap_reason": "Not run: registry rasters absent; method lane is unspecified in provided prompt.",
  "raster_sha256": null,
  "validator_output": "not run; no candidate raster; no NaN/range/CRS/shape/transform assertions possible",
  "submission_name": null,
  "submission_note": "No file generated; input/template and shared tools missing.",
  "verdict": "negative"
}
```

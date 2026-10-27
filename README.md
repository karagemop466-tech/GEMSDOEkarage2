# GEMSDOEkarage2 — project charter and review

> **Read this file before every project session.** It is the persistent source of truth for scope, evidence labels, and stop/go rules. Keep results auditable; never represent an estimate as a competition score.

## Current decision — 2026-10-27

**NO SUBMISSION TIFF EXISTS IN THIS REPOSITORY. Do not download or submit a file from this checkout.** This repository contains only this README on its initial commit: no competition rasters, feature cache, label data, registered-raster catalogue, evaluator, writer, model, or site application. Consequently no prediction can be generated, validated, or checked for uniqueness here. A generated placeholder or a copied historical TIFF would violate the request and the parallel-run rules.

The static review pages under [`docs/`](docs/) make this status explicit. They are an audit/decision aid, not a scoring model or an authorization to submit.

### What can and cannot currently be claimed

- The user supplied historical scores for nine GEMSDOE sites. They are transcribed in the executive summary as **USER-REPORTED / UNVERIFIED**; no submission-page receipts, raster bytes, or score provenance are in this checkout. They are not HOLDOUT-DTI measurements or ORGANIZER-CONFIRMED scores.
- The highest supplied result for the requested nine sites is GEMSDOE32's `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`, reported as **0.2778**. This is the best of the values supplied, not proof of why it scored that way and not an estimate of a new submission's score.
- The supplied message also cites leaderboard highs of 0.3195 and 0.4413. On **2026-10-27**, the live DrivenData leaderboard page was fetched and showed public rank 1 at **0.4544**. Leaderboard values are time-varying; see the [live leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/). The snapshot should be refreshed when used.
- A public GEMSDOE28 page contains a third-party audit claim that all 72 ordered comparisons among nine historical rasters exceeded the 70% / 3-pixel proximity limit. We have not downloaded or independently compared those rasters in this repository. Treat this as a **serious duplicate warning, not verified evidence**. Under the requested lane rule, a confirmed result above 70% means stop and record duplicate.
- **Score explanation for the 0.2778 entry:** its label and score alone do not disclose the exact algorithm, probability surface, raster hash, or score receipt; therefore the causal reason it scored that value is unknown. Official rules say the metric is distance-weighted Tversky with alpha 0.2, beta 0.8 and a triangular 300 m kernel; false negatives are weighted more heavily than false positives, and nearby predictions receive partial distance credit. These rules suggest why a spatially broad but relevant prediction can outperform a sparse one, but do not establish that this particular submission used such a strategy. See [official metric and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).

## Submission decision at a glance

| Requested site | Highest result supplied in the prompt | Evidence label | New-score estimate | Unique vs. the other requested sites? | Current action |
| --- | --- | --- | --- | --- | --- |
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` — 0.2477 | USER-REPORTED / UNVERIFIED | Not estimable from this checkout | Unknown — no raster bytes to compare | Do not submit any artifact from this repo |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` — 0.2600 | USER-REPORTED / UNVERIFIED | Not estimable from this checkout | Unknown — no raster bytes to compare | Do not submit any artifact from this repo |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` — 0.2449 | USER-REPORTED / UNVERIFIED | Not estimable from this checkout | Unknown — no raster bytes to compare | Do not submit any artifact from this repo |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` — 0.2710 | USER-REPORTED / UNVERIFIED | Not estimable from this checkout | Unknown — third-party page warns of high overlap; not independently checked | Do not submit any artifact from this repo |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` — 0.2600 | USER-REPORTED / UNVERIFIED | Not estimable from this checkout | Unknown — no raster bytes to compare | Do not submit any artifact from this repo |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` — 0.2708 | USER-REPORTED / UNVERIFIED | Not estimable from this checkout | Unknown — no raster bytes to compare | Do not submit any artifact from this repo |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` — 0.2778 | USER-REPORTED / UNVERIFIED | Not estimable from this checkout | Unknown — no raster bytes to compare | Historical result only; do not resubmit as a new result |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` — 0.2632 | USER-REPORTED / UNVERIFIED | Not estimable from this checkout | Unknown — no raster bytes to compare | Do not submit any artifact from this repo |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` — 0.2750 | USER-REPORTED / UNVERIFIED | Not estimable from this checkout | Unknown — no raster bytes to compare | Do not submit any artifact from this repo |

**Important:** the numbers in the table are the historical scores as reported in the request, not prospective score estimates. No validated estimate is possible without the cached feature stack, exact evaluator, labels/holdouts, and raster candidates. Do not infer uniqueness from a distinct filename or checksum alone.

## Research backlog: hypotheses to preregister, not results

These are provisional candidate ideas, ranked by *relative expected value and cost*, not tested score predictions. “Not implemented here” is verifiable because the checkout has no implementation files; whether a method is genuinely new across all GEMSDOE sites is **unknown** until their code, rasters, and run cards are reviewed. The explicit method-lane paragraph required by the parallel-run protocol is not identified in the supplied task text, so none of these candidates is authorized for implementation in this run.

| Rank | Provisional hypothesis | Layers and physical signature | Why it might find a missing fault rather than repeat a catalogue trace | Expected upside / cost | Data and validation status |
| --- | --- | --- | --- | --- | --- |
| 1 | **Cross-modal, scale-persistent structural edge concordance** | Competition stack: total magnetic intensity (TMI), magnetic horizontal/vertical gradients, isostatic gravity and its slope, strain rate/dilatation/shear. Compute multi-scale edge strength and orientation; reward spatially co-located, directionally consistent edges only where the modalities independently support a lineament. | A buried or unmapped structure can juxtapose magnetic/gravity domains and localize strain without coinciding with a mapped surface-fault pixel. Cross-sensor agreement is the proposed discriminator against one-layer lithologic texture. It must not use hidden/canonical labels to create the predictor. | **Moderate potential; low–medium cost.** First to evaluate if its lane is assigned. No score projection. | Uses layers listed in the official problem description; no new external source is required. Must recompute any catalogue-derived features fold-locally and pass feature-alone leakage canaries. |
| 2 | **Drainage asymmetry and channel-profile breaks conditioned on multi-scale relief** | 1 m DEM/3DEP-derived terrain, detrended elevation and slope. Target persistent channel deflection, knickpoint-like profile breaks, and paired valley-side asymmetry that align across neighboring catchments; suppress isolated slope edges. | Fault displacement or damage can perturb drainage and relief; requiring cross-catchment persistence may select structure rather than a single landslide, road cut, or lithologic contact. | **Moderate potential; medium–high cost.** New geomorphic evidence, but strong confounding. | The official challenge description says a `1m_DEM_links.csv` is supplied; the GeoDAWN USGS release also documents coordinated lidar/topographic products. These are official source leads, but local files/URLs are absent, so coverage and download success for this checkout are unverified. See [problem/data description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) and [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and). |
| 3 | **Radiometric ratio boundaries corroborated by subsurface geophysics** | USGS GeoDAWN K, eU, eTh / total-count grids (where available), robust ratios or log-ratios, and their scale-persistent boundaries; test co-location with magnetic/gravity edges and conductive-base structure. | Shallow geochemical/weathering contrasts may expose concealed structural fluid pathways that are not mapped as faults; requiring a second, deeper geophysical signature is intended to reject soil/lithology-only boundaries. | **Low–moderate potential; high cost.** Requires resampling, flight-line/coverage artifact checks, and lithology confound controls. | USGS identifies a public GeoDAWN aeromagnetic/aeroradiometric data release and gives DOI `10.5066/P93LGLVQ` with downloadable products; source existence is verified, but direct asset retrieval and pixel alignment have not been tested here. [USGS data release](https://doi.org/10.5066/P93LGLVQ). |

### Required experimental sequence (maximum three experiments or two hours)

1. **Preflight / fail closed:** assign one explicit method lane; obtain authorized competition data and the shared template/cache, evaluator, writer, and complete registry. Stop if any is missing. Do not build a private fork of shared tools. No submission slot is selected in this research step.
2. **Leakage canaries:** test each input feature alone on the exact spatially blocked hide-and-recover folds. Any AUC above 0.90 is presumed leakage until disproven. Derive every catalogue-based feature from visible faults only, buffer withheld fault segments, and mask visible fault pixels exactly.
3. **Primary metric:** run the pinned evaluator on pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). Report evaluator version, withheld-positive count, and 95% CI with every HOLDOUT-DTI number. Compare paired folds against the same-evaluator current best; no submission slot unless the required confidence interval shows a win and all other gates pass.
4. **Uniqueness / lane:** compare both the pre-placement prediction surface (Spearman rank correlation) and final dots to every registered raster. If any absolute rank correlation is greater than 0.90 or more than 70% of dots are within 3 pixels of a registry raster, label duplicate and stop. Do not choose alternate holes in a grid to evade the rule.
5. **Artifact validation:** writer must produce a single-band float32 GeoTIFF on the sample/template grid. Verify CRS EPSG:32611, exact dimensions/transform/bounds, finite `[0,1]` values inside the footprint, and null/nodata outside. Re-open and validate the saved file, then compute SHA-256. Format validity alone does not prove scientific merit or uniqueness.
6. **Slot selection is separate:** only after all preceding gates, a separate selector may consider the current weekly cap. A project-generated file is **not** “OK to submit” until that selector approves it. Do not automate submission or claim organizer validation without an actual receipt.

### Submission instructions (only for a future approved artifact)

1. Open the project's Executive Summary and download **only** the artifact whose status says `OK TO SUBMIT` and links to its run card, validator receipt, and SHA-256. Current status is **NO FILE / DO NOT SUBMIT**.
2. In DrivenData, open the GEMS competition's submission page, choose the approved single-band `.tif` (or a ZIP containing exactly one TIFF, if permitted), and paste the exact short note recorded in the run card. The competition requires prediction values in `[0,1]`, one layer, the sample grid/CRS/transform, and null/nodata outside the footprint. See the [official submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
3. Review the submission preview/name, submit only if the separate slot selector approved it, and save the resulting receipt. A validator pass is not a competition score; the score and status become ORGANIZER-CONFIRMED only when copied from the submission receipt.

No automatic competition upload is implemented or authorized. The competition's final expanded-label round includes expert verification of candidate faults; software can validate file format and reproducible metrics, but cannot claim to replace an expert's geological verification. Do not conflate automated submission gates with sponsor adjudication.

## Official references and evidence provenance

- [DrivenData GEMS competition rules/overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData problem, provided layers, metric, and GeoTIFF format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData live public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN airborne magnetic/radiometric/lidar data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GeoDAWN data-release DOI / products](https://doi.org/10.5066/P93LGLVQ)
- [Great Basin Center for Geothermal Energy — INGENIOUS](https://gbcge.org/current-projects/ingenious/)
- [EPSG:32611 — WGS 84 / UTM zone 11N](https://epsg.io/32611)
- [Competition submission instructions PDF provided by the user](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

The competition data download page requires an authenticated DrivenData account according to the user's provided access note; this checkout has no data or credentials. Do not request or store passwords/tokens in this repository. Public USGS product pages are useful research sources but do not substitute for the competition's exact sample raster or labels.

## Project values

- **Maximize P(Win):** conserve scarce weekly slots; treat each run as a controlled experiment; reject unvalidated score projections and duplicate lanes.
- **Own the Outcome:** publish negative results, preserve run cards and receipts, correct failures, and state blockers plainly.
- **Scientific integrity:** no copying previous submissions, no fabricated scores, no unsupported claims of uniqueness, and no human-free claim of expert geological validation.

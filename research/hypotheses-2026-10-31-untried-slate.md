# Untried geological hypothesis slate — 2026-10-31 (mandate #6, ranked before implementation)

Evidence labels: **UNTRIED** = no experiment in this repo; **REPO-PRIOR** = a related but
different method already ran here; channel provenance verified against
`.cache/work/feature_receipt.json` (35-channel template stack) and the raw-band usage lists in
`scripts/k2.py` / `scripts/k3.py` (bands 10 `deq_n100a15`, 16 `ieq_n100a15`, 7 `geod_shearrate`,
8 `geod_dilaterate` are absent from every feature recipe previously run in this repo).
No number below is a score; rankings are qualitative expected-DTI orderings, not projections.

The single method paragraph assigned to this lane (top candidate, validated first):

> **S1 — Seismicity-flank lineament recovery.** Fold-local gradient-boosted prediction of
> *visible* catalogue faults from the template's cached 35-channel feature stack — with the
> previously unused seismicity bands (`deq_n100a15`, `ieq_n100a15`) and geodetic strain bands
> (`geod_shearrate`, `geod_dilaterate`) added to the potential-field/topography channels — with
> visible fault pixels masked pixel-exactly, followed by fixed-budget off-catalogue (>2 px)
> dotted emission, scored on the spatially-blocked hide-and-recover holdout with pooled DTI
> (alpha 0.2, beta 0.8, 300 m triangular kernel, evaluator `gems57-pooled-hide-v2`).

## Ranked hypotheses

| Rank | Hypothesis | Layer(s) / channel(s) | Physical signature | Why it can catch a fault missing from USGS/INGENIOUS | Difference from this repo and the nine sites | Expected DTI gain | Cost |
|---|---|---|---|---|---|---|---|
| 1 | **S1 seismicity-flank lineament recovery** (lane above) | `deq_n100a15` (b10), `ieq_n100a15` (b16), `geod_shearrate` (b7), `geod_dilaterate` (b8) + existing potential-field edges | One-sided step in smoothed earthquake-rate density centred on a potential-field/topographic break; strain-rate change across that break | Catalogue maps quaternary surface expression; blind strands under alluvium still host microseismicity and strain localization, so seismicity sidedness at an independent geophysical break marks an unmapped strand | Bands 10/16/7/8 are in **no** feature recipe previously run here (k2/k3 raw lists exclude them); nine-site prior art (GEMSDOE33 `seisdil`, 0.0963 USER-REPORTED) is a standalone strain surface, not fold-supervised seismicity-flank context | Medium-high (new information family on top of the supervised baseline) | Low-medium — channels already in the cached stack |
| 2 | **S2 terrain-residual gravity edge** | `iso_grav_anom` (b13), `iso_grav_anom_vg` (b11), `det_elev` (b12), `det_elev_slope` (b19) | Block-fitted (label-blind) gravity residual after local elevation regression; edge/TMA of the residual | A density offset continues under alluvial cover beyond the mapped scarp; the residual removes the terrain carry that hides it | H1/B4 used raw gradients or flank asymmetry — neither fits this residual null; slate proposal 1, still UNTRIED | Medium | Medium (blockwise regression, label-blind) |
| 3 | **S3 strain-regime-change × magnetic-edge persistence** | `geod_shearrate` (b7), `geod_dilaterate` (b8), `rtp` (b2), `tmi_hg` (b3) | Where the geodetic strain regime changes sign/axis AND a magnetic edge persists across scales | A covered strand near a regime change localises slip without a surface trace; magnetic persistence gives the lock point | Strain bands excluded from k2/k3/hk3; the nine sites did not use geodetic strain channels (GEMSDOE33 `seisdil` uses seismicity/strain differently — USER-REPORTED 0.0963) | Medium-low (strain fields are km-scale, weak at 100 m) | Medium |
| 4 | **S4 dual potential-field break coincidence (gravity Hessian saddle × conductivity gradient ridge)** | `cond_surf` (b17), `iso_grav_anom_hg` (b18), `tc` (b6) | Intersection/saddle of conductivity-gradient ridges with gravity horizontal-gradient lineaments = conduit breach points, linked into strands | Covered offsets juxtapose conductive strata with no surface trace; fluid pathways sit on the break | This repo used `cond_surf` only as a raw/gradient feature in k2/k3; nine-site prior art exists (GEMSDOE32 H47 "dualhorizon corridor") so lane-drift risk is real — check registry overlap before any placement | Medium | Medium-high |
| 5 | **S5 thermal-spring / alteration-centre corridor prior** (needs external data) | USGS thermal-spring occurrences (public USGS/NGMDB databases) + GeoDAWN radiometric K, eTh/eU alteration | Spring/alteration centres and their structural corridors (lineament density between known vents) | Vents mark where deep fluids reach the surface; the connecting structure hosts the unmapped faults that feed them | H-F tested alteration × curvature intersections with poor holdout (0.018 proxy); a corridor-prior over springs differs, but needs an external point database | Low-medium (prior risk: springs correlate with mapped faults) | High — external data fetch; **USGS source availability not verified this session** (sandbox allowlist), so not viable inside today's budget |

## Validation plan (binding)

* E1: leakage canaries for every cached channel (AUC ≤ 0.90 each) + two primitive arms.
* E2: S1 arm (all 35 channels) vs ablation arm (seismicity/strain channels removed) on the same
  folds — paired spatial-block CI decides whether S1 beats the ablation; the recorded same-instrument
  incumbent for the "beat the current holdout best" check is `k3dti_b110` = 0.19157
  [0.17474, 0.20880], 58,258 withheld positives (`evidence/k3/combined_holdout.json`,
  HOLDOUT-DTI, evaluator `gems57-pooled-hide-v2`).
* E3: final surface trained on the full catalogue, before-placement uniqueness gate, emission,
  final-dot gate, writer, run card. Budget stop: 3 experiments or 2 hours.
* Named non-fault mimics: S1 — production/mining seismicity clusters and basin-fill interpolation
  artefacts (control: ablation arm without seismicity channels); S2 — unfaulted bedrock/alluvium
  contact and pluvial shorelines; S4 — saline playa margins.

## Outcome (recorded after the binding validation — 2026-10-31)

**S1 result: HOLDOUT-DTI 0.18791 [0.16799, 0.20782], n=58,308 (pooled, gems57-pooled-hide-v2) — NEGATIVE
versus the promotion bar.** The recorded incumbent k3dti_b110 stands at 0.19157 [0.17474, 0.20880]
(n=58,258, `evidence/k3/combined_holdout.json`); S1 does not beat it, so no slot is spent. Details
(`evidence/s1/`):

- **Mechanism tests (H1):** the paired S1-vs-ablation delta at matched DTI placement is +0.00833
  [-0.00382, +0.02055] — positive but *inconclusive* (CI crosses 0). At fixed emission the delta is
  +0.01325 [+0.00069, +0.02519] — significant. The seismicity/strain novelty helps against the
  fixed-emission ablation but does not establish a clear win over the same-placement ablation, and
  it never reaches the K3 bar.
- **Budget/placement (H2):** rate 0.0110 beats 0.0073 (+0.038 / +0.046 vs the 0.73% arms,
  significant); DTI beats fixed placement (+0.0046 [+0.0012, +0.0081], significant).
- **Primitives:** grav_edge 0.0664, quake_rate 0.0411 — both far below the supervised surfaces.
- **Leakage gate:** all 34 channels pass (worst feature-alone max(AUC, 1-AUC) = 0.6173, band06 /
  total conductivity); the four novelty channels sit at 0.554-0.578.
- **Consequence for H1:** the missing mechanism is *not* recovered by earthquake-catalogue
  density/rate/depth on this feature set. Either the expert labels' hidden faults are not
  preferentially near the 1950-2024 M>=2.5 seismicity after conditioning on the
  potential-field/terrain stack, or USGS catalogue density is too sparse (~1,900 usable points,
  clustered at Coso) to carry the signal. H1 as formulated is retired; the flank-orientation
  variant (H5) remains open for a future assigned lane.
- The generated TIF
  (`docs/downloads/gemsdoekarage2-s1-quakeflank-51961d-20261031T014126Z-zeros.tif`, 51,961
  off-catalogue dots, format-valid, rank-uncorrelated with every registry raster at |Spearman| <= 0.146,
  0 catalogue dots) is published as **research-only, OK-to-download yes / OK-to-submit NO** with a negative run card,
  following the H-F precedent. The literal lattice clause (degenerate witness, 99.87% footprint
  coverage) is flagged in the card and on the site as a protocol irregularity; it would have stopped
  the file regardless of the holdout result. A second finding: 55 *non-lattice* fleet rasters also
  exceed the 70%-overlap clause against the final dots (worst 0.898 vs GEMSDOE32 h45-kernelspacing)
  - independent supervised lanes converge on the same consensus off-catalogue ridge, the same
  pattern K3 recorded (0.8477-0.8862). The per-raster literal clause has no honest passing path for
  a competitive supervised emission; this is now recorded as a second policy question.

**S2-S5 remain untried.** S4 (dual-field break coincidence) is the next ranked idea under the same
protocol; S5 cannot be attempted in this environment (external spring/hydrothermal data are not
fetchable from the allowed hosts).

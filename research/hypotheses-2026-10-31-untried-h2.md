# Untried geological hypothesis slate — H2 lane (post-S1, 2026-10-31)

Evidence labels: **UNTRIED** = no experiment in this repo; **REPO-PRIOR** = a related but different
method already ran here. No number below is a score; rankings are qualitative expected-DTI
orderings, not projections. Rankings account for both expected hit-rate improvement on hidden
truth and implementation cost given the cached 35-channel GeoDAWN template stack.

Binding constraints honoured:
* LANE: rank-correlation <= 0.90 with any registry raster AND <= 70% of dots within 3 px of any one
  registry raster's dots, checked before placement AND on final dots.
* Holdout = hide-and-recover: whole fault segments withheld with buffer; catalogue features derived
  only from visible faults; visible faults masked pixel-exactly; pooled DTI alpha 0.2 / beta 0.8 /
  300 m triangular kernel.
* Leakage canary: each feature alone must have AUC <= 0.90.
* Budget: stop after 3 experiments or 2 hours. No submission slot spent; promotion is a separate
  selector step.
* Data blocker: training_features.tif / labels.tif / sample_submission.tif require DrivenData login
  and are unavailable in this sandbox. The cached feature stack is committed under vendor/gems57 and
  .cache/ work files; validate against it before any placement.

---

## Ranked hypotheses

### H-N1 — Multi-scale radiometric alteration envelope (low-K × high eTh/eU × magnetic low halo)

| Field | Detail |
|---|---|
| **Layers** | GeoDAWN radiometric K (potassium), eTh/U ratio, rtp (reduced-to-pole magnetic); catalogue faults (distance transform) |
| **Physical signature** | Blind hydrothermal alteration: low-K (illite/clay) envelope coincident with high eTh/U (alteration) and a magnetic low (demagnetization halo), sampled 300–900 m from mapped faults |
| **Why catches missing faults** | Blind geothermal systems create chemically altered envelopes with no surface fault trace. The USGS/INGENIOUS catalogue maps surface expression; radiometric alteration marks the subsurface fluid pathway that feeds blind strands. The 300–900 m halo places dots where the hidden truth was measured to sit (E1: 2.2–2.6× enrichment at 300–900 m vs footprint). |
| **Differs from repo / nine sites** | H-F (2026-10-30) tested alteration × curvature **at intersections** (negative, holdout-DTI 0.018). HALO uses uniform dots in the 300–900 m band. H-N1 adds **multi-radiometric envelope gating** inside the same band — not intersection points, not uniform dots — so it is a distinct placement prior. |
| **Expected DTI gain** | Medium-high — new information family (radiometric alteration) not used as a placement gate in any run card on record |
| **Cost** | Low — all bands are in the cached 35-channel stack; no external data |

### H-N2 — Gravity-gradient lineament × conductivity-ridge intersection halo

| Field | Detail |
|---|---|
| **Layers** | iso_grav_anom_hg (gravity horizontal gradient, b18), cond_surf (surface conductivity, b17), catalogue faults |
| **Physical signature** | Fluid conduits localize where conductive strata intersect a density boundary. Multi-scale gravity-gradient lineaments mark concealed density breaks; conductivity ridges mark fluid-bearing strata. Their intersection, dilated by a 200–500 m halo, targets blind faults. |
| **Why catches missing faults** | A concealed fault juxtaposes contrasting lithologies (density break = gravity gradient) and hosts fluids (conductivity ridge). Neither signature requires surface expression. The catalogue maps only the surface trace; the intersection halo marks the subsurface continuation. |
| **Differs from repo / nine sites** | S4 (untried slate) proposed conductivity-gradient × gravity-HG as **raw supervised features**. H-N2 uses them as an **unsupervised placement prior**: dots at intersections only, outside the catalogue apron. GEMSDOE32 H47 "dualhorizon corridor" is a different lane (reported 0.0581 USER-REPORTED) — lane-drift check required before placement. |
| **Expected DTI gain** | Medium-high — intersection of two independent geophysical constraints should out-perform either alone |
| **Cost** | Low — bands b17/b18 are in the cached stack |

### H-N3 — Curvature convergence along catalogue fault strike (blind-tip extension)

| Field | Detail |
|---|---|
| **Layers** | det_elev_slope (b19), det_elev (b12), catalogue faults (distance transform, strike direction from 8-connected components) |
| **Physical signature** | Plan/profile curvature convergence zones along mapped fault strike, extended 200–500 m beyond mapped fault tips. Blind fault segments propagate into the hanging wall/footwall; curvature marks the propagation front. |
| **Why catches missing faults** | Mapped catalogue faults are truncated at mapping confidence. Hidden segments continue beyond mapped tips where curvature concentrates strain. The halo placement extends beyond the catalogue without copying it. |
| **Differs from repo / nine sites** | HALO uses uniform dots in a 300–900 m ring around **all** catalogue pixels. H-N3 restricts placement to **curvature-convergence sites along strike**, beyond tips only — a geometrically tighter prior that does not sample the full ring. |
| **Expected DTI gain** | Medium — targets the specific geometry where blind segments initiate |
| **Cost** | Low — DEM derivatives b12/b19 are in the cached stack; catalogue components already computed |

### H-N4 — Geodetic dilation corridor around catalogue faults

| Field | Detail |
|---|---|
| **Layers** | geod_dilaterate (b8), geod_shearrate (b7), catalogue faults (distance transform) |
| **Physical signature** | Zones of high dilation rate within 1 km of mapped faults, excluding the catalogue apron. Active geothermal systems dilate the crust; blind strands dilate without surface rupture. |
| **Why catches missing faults** | Dilation marks crustal weakness and fluid overpressure. A blind strand under cover dilates without breaking the surface. The catalogue does not include these; dilation corridors reveal them independently. |
| **Differs from repo / nine sites** | S1 (validated, negative) used seismicity + strain as **supervised features** in a gradient-boosted surface (holdout-DTI 0.18791, did not beat k3dti_b110 0.19157). H-N4 uses dilation rate as an **unsupervised placement prior** — dots in high-dilation corridors only — a different mechanism and a different validation path. |
| **Expected DTI gain** | Medium — strain fields are km-scale and weak at 100 m resolution, but corridors concentrate probability |
| **Cost** | Low — bands b7/b8 are in the cached stack |

### H-N5 — Thermal-spring corridor prior (requires external data)

| Field | Detail |
|---|---|
| **Layers** | USGS thermal-spring occurrences (public USGS/NGMDB database), GeoDAWN radiometric K/eTh/U, catalogue faults |
| **Physical signature** | Structural corridor connecting thermal-spring clusters, cross-cutting the mapped catalogue; radiometric alteration envelope along the corridor |
| **Why catches missing faults** | Springs mark where deep fluids reach the surface. The unmapped faults that feed them lie along the structural corridor between spring clusters. The catalogue misses these blind connectors. |
| **Differs from repo / nine sites** | No lane on record uses thermal-spring locations as a placement prior. H-F used radiometric × curvature at intersections (negative). H-N5 needs an external point database not yet verified as obtainable from the sandbox allowlist. |
| **Expected DTI gain** | Low-medium — prior risk: springs correlate with mapped faults, reducing off-catalogue yield |
| **Cost** | High — external data fetch; USGS source availability not verified; not viable inside today's budget |

---

## Ranking by expected DTI improvement × cost

| Rank | Hypothesis | Expected DTI gain | Cost | Viable this session? |
|---|---|---|---|---|
| 1 | H-N1 radiometric alteration envelope | Medium-high | Low | **Yes** — cached bands only |
| 2 | H-N2 gravity-HG × conductivity ridge | Medium-high | Low | **Yes** — cached bands only |
| 3 | H-N3 curvature convergence along strike | Medium | Low | **Yes** — cached bands only |
| 4 | H-N4 geodetic dilation corridor | Medium | Low | **Yes** — cached bands only |
| 5 | H-N5 thermal-spring corridor | Low-medium | High | **No** — external data not verified |

**Top candidate for validation: H-N1** (multi-scale radiometric alteration envelope). It uses only cached bands, targets a new information family not yet used as a placement gate, and sits inside the measured 300–900 m enrichment band.

**Named non-fault mimics for H-N1:** unfaulted bedrock/alluvium contacts with similar radiometric contrast; pluvial shorelines; saline playa margins with evaporite K enrichment. Control: ablation arm without radiometric channels on the same folds.

**Data needed for validation:** cached 35-channel stack (vendor/gems57, .cache/work/feature_receipt.json), existing_faults.tif + sample_submission.tif (data/bridge — unavailable in sandbox, requires DrivenData login). **Blocker:** holdout validation cannot run locally without labels.tif / sample_submission.tif.

---

## What must happen before any placement

1. Run leakage canaries for H-N1's three bands (AUC ≤ 0.90 each).
2. Build H-N1 placement prior from visible catalogue only; mask visible faults pixel-exactly.
3. Run hide-and-recover holdout (pooled DTI, alpha 0.2 / beta 0.8 / 300 m).
4. Run pre-placement uniqueness gate (|Spearman| <= 0.90, <= 70% dots within 3 px of any registry raster).
5. If all gates pass, generate the TIF, write run card, emit audit, and place on the submission desk for the owner's slot decision.

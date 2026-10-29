# Untried geological hypotheses — GEMSDOE fault discovery

**Status update (2026-10-29, session B):** H-A was implemented as a file in an earlier session (`generate_unique_submission.py`, now retired). Its full-registry duplicate check **failed**: all of its in-footprint positives lie within 3 px of `GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif` (overlap 1.0). The file remains an inventoried research-only download (`docs/downloads/`), not a submission candidate. The "no focus-site submission uses intersection propensity" novelty statement below is contradicted by those bytes. H-A has not been validated on any holdout. Receipt: `evidence/uniqueness/gemsdoekarage2-hA-intersection-propensity-aad3569983ab.full-registry.json`.

**Original status:** None of the five hypotheses below has been implemented or tested in this checkout or on the nine focus GitHub sites. They are presented for ranking by expected DTI gain and implementation cost, per the parallel-run protocol mandate to propose 3–5 untried hypotheses before any new experiment.

**Data access constraint:** no organizer-authenticated training_features.tif / labels.tif / sample_submission.tif is available in this sandbox (DrivenData data tab redirects to login). The GEMSDOE32 owner-mirror grid (3730 × 3292, EPSG:32611, 100 m, origin 243350 / 4508550) was recovered from a pinned GitHub blob for reference-grid purposes only; it is not organizer data. Any experiment below that needs real feature bands must first obtain the free official sources named.

---

## H-A: Multi-scale fault-intersection propensity (rank 1 — highest expected gain, medium cost)

**Layers:** DEM-derived curvature at 3 scales (100 m, 500 m, 2 km) + radiometric potassium/thorium ratio + distance to mapped Quaternary faults.

**Physical signature:** geothermal permeability is concentrated at fault intersections and relay ramps, not along single traces. Curvature convergence at multiple scales marks structural intersections; a K/Th ratio shift marks hydrothermal alteration that bleaches potassium and enriches thorium along fluid pathways.

**Why it catches catalogue-missing faults:** the USGS/INGENIOUS catalogue maps surface traces; blind or covered strands leave no surface expression but still intersect at depth, producing alteration halos and curvature signatures detectable in radiometrics and DEM. Intersections are also the geothermal "sweet spots" most likely to be unmapped.

**How it differs from existing work:** existing focus-site submissions use dotted ridge/scarp following (D2.8, Poisson, lattice), stepover/tip models, or single-scale scarp openness. None targets multi-scale curvature intersection density combined with K/Th alteration ratios. This repo's H1/H2/K2/K3/B4 lanes used parity, step-asymmetry, edge centrality, and linedot density — not intersection propensity.

**Leakage canary:** test curvature alone and K/Th ratio alone on the holdout. AUC > 0.90 on either feature alone would indicate catalogue leakage (curvature computed from faults) and fails.

**Free official source needed:** USGS GeoDAWN radiometrics (https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) and 1 m DEM links from the competition data page. Both are free; the DEM links JSON requires DrivenData login.

**Expected DTI gain:** medium–high. Intersection targeting concentrates the dot budget where TP credit per dot is highest; fewer dots → lower FP penalty under α=0.2.

---

## H-B: Off-catalogue SGMC fault-distance transform with depth-to-basement constraint (rank 2 — high expected gain, high cost)

**Layers:** USGS/INGENIOUS SGMC (State Geologic Map Compilation) fault lines, depth-to-basement from gravity inversion, magnetic analytic signal.

**Physical signature:** off-catalogue faults offset basement, producing a gravity-gradient lineament and magnetic edge. Distance-to-nearest-SGMC-fault (only for faults NOT in the USGS catalogue) isolates blind strands. Depth-to-basement < 2 km constrains predictions to the geothermal window.

**Why it catches catalogue-missing faults:** SGMC includes mapped Quaternary and pre-Quaternary faults that the USGS catalogue may omit. Targeting off-catalogue SGMC strands within the shallow-basement window directly addresses blind structures.

**How it differs:** existing work masks known catalogue faults pixel-exactly (visible-fault masking). H-B instead *uses* off-catalogue faults as positive priors — a complementary, not duplicate, signal. No focus-site submission uses SGMC off-catalogue distance.

**Leakage canary:** AUC of distance-to-SGMC-fault alone on holdout must be ≤ 0.90; if higher, the SGMC lines are too close to catalogue truth and the feature leaks.

**Free official source needed:** INGENIOUS / SGMC geologic map (https://gbcge.org/current-projects/ingenious/ and https://gdr.openei.org/submissions/1391) — free and public.

**Expected DTI gain:** high if off-catalogue faults overlap hidden truth; cost high because gravity inversion and magnetic processing need real data.

---

## H-C: Seismicity-aligned strain-rate corridor (rank 3 — medium expected gain, low-medium cost)

**Layers:** earthquake catalog (ANSS / USGS), strain rate from geodetic data, young volcanic center proximity (< 10 km).

**Physical signature:** active geothermal systems localize seismicity along blind structures. A corridor of microseismicity aligned with strain-rate maxima, near young volcanism, marks a permeable fault zone even without surface trace.

**Why it catches catalogue-missing faults:** seismicity reveals active structures that have no mapped surface expression. The catalogue is incomplete for blind faults; microseismicity is not.

**How it differs:** no focus-site submission or repo lane uses seismicity or strain rate. H1/H2 used potential-field and DEM derivatives only.

**Leakage canary:** AUC of seismicity density alone on holdout; earthquake catalogs are independent of the fault truth labels, so leakage is unlikely — the canary should pass easily.

**Free official source needed:** ANSS composite earthquake catalog (https://earthquake.usgs.gov/earthquakes/search/) and USGS Quaternary fault database — free and public.

**Expected DTI gain:** medium. Seismicity is a noisy proxy; paired with volcanism proximity it becomes more specific.

---

## H-D: Radiometric uranium-thorium-potassium ternary alteration index (rank 4 — medium expected gain, low cost)

**Layers:** GeoDAWN airborne radiometrics (K, eU, eTh), ternary RGB → alteration index (e.g., (eU + eTh) / K, or clay index).

**Physical signature:** hydrothermal alteration mobilizes uranium and thorium while leaching potassium, producing a characteristic radiometric anomaly along blind fault-controlled fluid pathways.

**Why it catches catalogue-missing faults:** alteration halos extend beyond surface fault traces, revealing blind strands under cover. The catalogue maps traces, not halos.

**How it differs:** existing submissions use magnetic/scarp features; none uses a radiometric ternary alteration index as the primary signal. The GEMSDOE32 H48 used 214Bi radon zonation but not a K-U-Th ternary alteration index.

**Leakage canary:** AUC of radiometric index alone on holdout ≤ 0.90 expected (radiometrics are independent of catalogue fault lines).

**Free official source needed:** USGS GeoDAWN radiometric survey — free and public.

**Expected DTI gain:** medium. Radiometric anomalies are broad; combining with DEM lineaments would sharpen.

---

## H-E: Multi-resolution lineament density with directional anisotropy (rank 5 — lower expected gain, low cost)

**Layers:** DEM at native 100 m and resampled 500 m / 1 km / 2 km; lineament extraction via directional filters (8 azimuths) at each scale.

**Physical signature:** fault zones produce linear topographic expression at multiple scales; anisotropy (strong response in one azimuth, weak in orthogonal) distinguishes faults from isotropic terrain noise.

**Why it catches catalogue-missing faults:** buried or covered faults still deform the surface over wide areas; multi-scale lineament density captures this without needing a mapped trace.

**How it differs:** existing work uses single-scale scarp openness/ridge; H-E uses multi-scale, multi-directional lineament density with anisotropy weighting — a different transform family.

**Leakage canary:** AUC of lineament density alone; lineaments derived from DEM only (not from faults), so leakage unlikely.

**Free official source needed:** DEM links from competition data page (requires login) or USGS 3DEP (https://www.usgs.gov/3dep) — free and public.

**Expected DTI gain:** lower–medium. Lineament density is diffuse; best used as a soft spatial prior, not a primary detector.

---

## Ranking summary

| Rank | Hypothesis | Layers | Expected DTI gain | Cost | Free official source available? |
|------|-----------|--------|-------------------|------|---------------------------------|
| 1 | H-A fault-intersection propensity | curvature ×3 scales + K/Th + distance-to-fault | medium–high | medium | GeoDAWN radiometrics: yes; DEM: needs DrivenData login |
| 2 | H-B off-catalogue SGMC + depth-to-basement | SGMC faults + gravity basement depth + magnetic edge | high | high | INGENIOUS SGMC: yes |
| 3 | H-C seismicity-aligned strain corridor | ANSS earthquakes + strain rate + young volcanism | medium | low–medium | ANSS/USGS: yes |
| 4 | H-D radiometric K-U-Th alteration index | GeoDAWN K, eU, eTh ternary | medium | low | GeoDAWN: yes |
| 5 | H-E multi-resolution anisotropic lineament density | DEM ×4 scales ×8 azimuths | lower–medium | low | USGS 3DEP: yes |

**Top candidate for validation:** H-A (multi-scale fault-intersection propensity) — best expected gain at feasible cost. If GeoDAWN radiometrics and DEM are obtainable, implement and test on the holdout before any submission slot. If not obtainable, fall back to H-C (seismicity) or H-E (DEM lineaments), both fully free.

**Validation plan:** implement H-A on the shared template's cached feature stack; test each feature alone for AUC ≤ 0.90 leakage; run buffered whole-segment hide-and-recover with visible-fault masking; score pooled DTI (α=0.2, β=0.8, R=300 m) against withheld positives; compare vs current same-evaluator best with paired 95% CI; check uniqueness vs all registry rasters (Spearman ≤ 0.90, ≤ 70% dots within 3 px). Only promote if all gates pass.
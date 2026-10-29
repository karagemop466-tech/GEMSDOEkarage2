# Untried geological hypotheses — GEMSDOE fault discovery

**Status:** These five hypotheses are proposals, not model results: none has a leakage-safe, spatially blocked HOLDOUT-DTI test in this checkout. An exploratory H-A raster was present on the updated main branch, but its accompanying run card has no HOLDOUT-DTI, evaluator, withheld-positive count, or registry measurements; the audit says organizer template and uniqueness are unverified. The TIFF, card, and audit are preserved under `evidence/quarantine/` and are not a validated implementation or submission. This slate ranks only qualitative expected value and implementation cost, not numerical DTI gain.

**Data access constraint:** this session has no organizer-authenticated `training_features.tif`, `labels.tif`, or `sample_submission.tif`; the DrivenData data tab requires login according to the existing repository record. The GEMSDOE32 owner-mirror grid (3730 × 3292, EPSG:32611, 100 m, origin 243350 / 4508550) is for reference-grid comparison only, not organizer data. The official-source links below identify places to check, but this session did not retrieve their external files, confirm licensing/footprints, or verify current download availability. A hypothesis needing any such source is **not presently viable for testing** until the exact data is obtained and its provenance, coverage, and hash recorded.

---

## H-A: Multi-scale fault-intersection propensity (rank 1 — highest expected gain, medium cost)

**Layers:** DEM-derived curvature at 3 scales (100 m, 500 m, 2 km) + radiometric potassium/thorium ratio + distance to mapped Quaternary faults.

**Physical signature:** geothermal permeability is concentrated at fault intersections and relay ramps, not along single traces. Curvature convergence at multiple scales marks structural intersections; a K/Th ratio shift marks hydrothermal alteration that bleaches potassium and enriches thorium along fluid pathways.

**Why it catches catalogue-missing faults:** the USGS/INGENIOUS catalogue maps surface traces; blind or covered strands leave no surface expression but still intersect at depth, producing alteration halos and curvature signatures detectable in radiometrics and DEM. Intersections are also the geothermal "sweet spots" most likely to be unmapped.

**How it differs from existing work:** existing focus-site submissions use dotted ridge/scarp following (D2.8, Poisson, lattice), stepover/tip models, or single-scale scarp openness. None targets multi-scale curvature intersection density combined with K/Th alteration ratios. This repo's H1/H2/K2/K3/B4 lanes used parity, step-asymmetry, edge centrality, and linedot density — not intersection propensity.

**Leakage canary:** test each predictor alone, including curvature and K/Th ratio. Compute any distance-to-fault predictor using only visible catalogue faults within each fold, then test it alone too; an all-catalogue distance layer would directly expose held-out labels. AUC > 0.90 for any feature is treated as leakage until proven otherwise. DEM curvature is not itself computed from fault labels, so high AUC there would require a separate spatial-confounding investigation rather than the claim that curvature is label-derived.

**Official sources to check, availability unverified:** [USGS GeoDAWN radiometrics](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) and the competition's 1 m DEM links via its [data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/). The repository records that the DEM links JSON requires participant login. No radiometric archive, DEM tile, coverage, license, or feature hash was obtained in this session; H-A is not currently validated or ready to test.

**Expected DTI gain:** medium–high. Intersection targeting concentrates the dot budget where TP credit per dot is highest; fewer dots → lower FP penalty under α=0.2.

---

## H-B: Off-catalogue SGMC fault-distance transform with depth-to-basement constraint (rank 2 — high expected gain, high cost)

**Layers:** USGS/INGENIOUS SGMC (State Geologic Map Compilation) fault lines, depth-to-basement from gravity inversion, magnetic analytic signal.

**Physical signature:** off-catalogue faults offset basement, producing a gravity-gradient lineament and magnetic edge. Distance-to-nearest-SGMC-fault (only for faults NOT in the USGS catalogue) isolates blind strands. Depth-to-basement < 2 km constrains predictions to the geothermal window.

**Why it catches catalogue-missing faults:** SGMC includes mapped Quaternary and pre-Quaternary faults that the USGS catalogue may omit. Targeting off-catalogue SGMC strands within the shallow-basement window directly addresses blind structures.

**How it differs:** existing work masks known catalogue faults pixel-exactly (visible-fault masking). H-B instead *uses* off-catalogue faults as positive priors — a complementary, not duplicate, signal. No focus-site submission uses SGMC off-catalogue distance.

**Leakage canary:** AUC of distance-to-SGMC-fault alone on holdout must be ≤ 0.90; if higher, the SGMC lines are too close to catalogue truth and the feature leaks.

**Official source to check, availability unverified:** [INGENIOUS](https://gbcge.org/current-projects/ingenious/) and its [GDR submission 1391](https://gdr.openei.org/submissions/1391). This session did not retrieve an SGMC file or verify its coverage, license, or current availability; H-B is not presently viable for testing without that provenance check.

**Expected DTI gain:** high if off-catalogue faults overlap hidden truth; cost high because gravity inversion and magnetic processing need real data.

---

## H-C: Seismicity-aligned strain-rate corridor (rank 3 — medium expected gain, low-medium cost)

**Layers:** earthquake catalog (ANSS / USGS), strain rate from geodetic data, young volcanic center proximity (< 10 km).

**Physical signature:** active geothermal systems localize seismicity along blind structures. A corridor of microseismicity aligned with strain-rate maxima, near young volcanism, marks a permeable fault zone even without surface trace.

**Why it catches catalogue-missing faults:** seismicity reveals active structures that have no mapped surface expression. The catalogue is incomplete for blind faults; microseismicity is not.

**How it differs:** no focus-site submission or repo lane uses seismicity or strain rate. H1/H2 used potential-field and DEM derivatives only.

**Leakage canary:** AUC of seismicity density alone on holdout; earthquake catalogs are independent of the fault truth labels, so leakage is unlikely — the canary should pass easily.

**Official sources to check, availability unverified:** [USGS earthquake catalog search](https://earthquake.usgs.gov/earthquakes/search/) and the USGS Quaternary Fault and Fold Database. This session did not retrieve event data or verify download, license, spatial coverage, or temporal completeness; H-C is not presently viable for testing. Earthquake catalog independence from the target labels must not be presumed: test standalone AUC for leakage and assess induced/mining events.

**Expected DTI gain:** medium. Seismicity is a noisy proxy; paired with volcanism proximity it becomes more specific.

---

## H-D: Radiometric uranium-thorium-potassium ternary alteration index (rank 4 — medium expected gain, low cost)

**Layers:** GeoDAWN airborne radiometrics (K, eU, eTh), ternary RGB → alteration index (e.g., (eU + eTh) / K, or clay index).

**Physical signature:** hydrothermal alteration mobilizes uranium and thorium while leaching potassium, producing a characteristic radiometric anomaly along blind fault-controlled fluid pathways.

**Why it catches catalogue-missing faults:** alteration halos extend beyond surface fault traces, revealing blind strands under cover. The catalogue maps traces, not halos.

**How it differs:** existing submissions use magnetic/scarp features; none uses a radiometric ternary alteration index as the primary signal. The GEMSDOE32 H48 used 214Bi radon zonation but not a K-U-Th ternary alteration index.

**Leakage canary:** AUC of radiometric index alone on holdout ≤ 0.90 expected (radiometrics are independent of catalogue fault lines).

**Official source to check, availability unverified:** [USGS GeoDAWN airborne radiometric survey](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and). This session did not obtain K/eU/eTh rasters or verify their units, preprocessing, extent, or licensing; H-D is not presently viable for testing.

**Expected DTI gain:** medium. Radiometric anomalies are broad; combining with DEM lineaments would sharpen.

---

## H-E: Multi-resolution lineament density with directional anisotropy (rank 5 — lower expected gain, low cost)

**Layers:** DEM at native 100 m and resampled 500 m / 1 km / 2 km; lineament extraction via directional filters (8 azimuths) at each scale.

**Physical signature:** fault zones produce linear topographic expression at multiple scales; anisotropy (strong response in one azimuth, weak in orthogonal) distinguishes faults from isotropic terrain noise.

**Why it catches catalogue-missing faults:** buried or covered faults still deform the surface over wide areas; multi-scale lineament density captures this without needing a mapped trace.

**How it differs:** existing work uses single-scale scarp openness/ridge; H-E uses multi-scale, multi-directional lineament density with anisotropy weighting — a different transform family.

**Leakage canary:** AUC of lineament density alone; lineaments derived from DEM only (not from faults), so leakage unlikely.

**Official sources to check, availability unverified:** the competition's [DEM links data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) or [USGS 3DEP](https://www.usgs.gov/3dep). The competition page requires login per the repository access record. This session did not retrieve 3DEP tiles, identify intersecting tiles, or verify license, coverage, or resolution; H-E is not presently viable for testing.

**Expected DTI gain:** lower–medium. Lineament density is diffuse; best used as a soft spatial prior, not a primary detector.

---

## Ranking summary

| Rank | Hypothesis | Layers | Qualitative expected gain (not score) | Cost | Official source/access status |
|------|-----------|--------|-------------------|------|---------------------------------|
| 1 | H-A fault-intersection propensity | curvature ×3 scales + K/Th + distance-to-fault | medium–high, qualitative | medium | GeoDAWN not checked; competition DEM login-gated per repo record |
| 2 | H-B off-catalogue SGMC + depth-to-basement | SGMC faults + gravity basement depth + magnetic edge | high if source is valid, qualitative | high | INGENIOUS/GDR linked; file, extent, license not checked |
| 3 | H-C seismicity-aligned strain corridor | ANSS earthquakes + strain rate + young volcanism | medium, qualitative | low–medium | ANSS/USGS endpoints linked; access/coverage not checked |
| 4 | H-D radiometric K-U-Th alteration index | GeoDAWN K, eU, eTh ternary | medium, qualitative | low | GeoDAWN linked; raster availability/units not checked |
| 5 | H-E multi-resolution anisotropic lineament density | DEM ×4 scales ×8 azimuths | lower–medium, qualitative | low | 3DEP linked; intersecting tiles, license/coverage not checked |

**Qualitative top hypothesis, not a viable experiment yet:** H-A (multi-scale fault-intersection propensity) has the most attractive hypothesized value/cost balance in this slate, but its DEM source is login-gated in the repository record, GeoDAWN availability was not checked, and the exploratory raster is quarantined without holdout or uniqueness evidence. H-A must not be treated as implemented, validated, or eligible. H-C/H-E are not verified fallbacks: their official source availability, coverage, licensing, and input hashes have not been established either.

**Conditional validation plan (not authorized yet):** only after the coordinator assigns H-A, the missing official inputs and cached shared tools are restored, and the pre-placement all-registry stop can be run, test each feature alone for AUC > 0.90 leakage; run buffered whole-segment hide-and-recover with visible-fault masking; score pooled DTI (α=0.2, β=0.8, R=300 m) against withheld positives; compare against a frozen current same-evaluator incumbent with paired spatial 95% CI; and check the entire surface before placement plus final dots against every registry raster (Spearman > 0.90 or >70% overlap within 3 px means stop). No promotion/slot is authorized by this proposal.
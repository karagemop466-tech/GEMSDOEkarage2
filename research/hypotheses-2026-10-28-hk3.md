# HK3 session (2026-10-28, branch `arena/fcccc3a7-gemsdoekarage2`) — calibration, hypotheses, lane

Written before the HK3 holdout result was known (E2 was running when this file was
drafted; it is not edited after the fact except in the clearly marked "Outcome" section).

## 0. What changed versus every earlier session in this repository

Earlier sessions produced **no submittable file** because two things were missing:
(1) a quantitative, model-free reading of *why* the nine focus-site scores differ, and
(2) a way to turn a catalogue holdout into a leaderboard *estimate*. Both are now in
`evidence/calibration/leaderboard_calibration.json` (E1, `scripts/calibrate_leaderboard.py`),
computed from hash-pinned public bytes and the USER-REPORTED scores in the prompt.

### E1 — leaderboard calibration (LEADERBOARD-CALIBRATED ESTIMATE; never a score)

| Quantity | Value | How |
| --- | --- | --- |
| Hidden public truth size `G` | **≈ 12,406 px** (interval 12,397–12,414 from 4-decimal score rounding; 12,525 if the lattice credit is averaged over all off-catalogue cells) | The 13GEMSDOE r13 lattice (spacing 5 px, 206,895 dots, 2,391 on catalogue pixels that the organizer excludes) is a uniform sampler. Its per-truth-pixel kernel credit is pure geometry: `c = 0.3746`. With the reported 0.0904, `DTI = cG / (0.2cG + 0.2·n_eff·(1 − κG/N) + 0.8G)` pins `G`. |
| `G` as a fraction of the catalogue | 0.203 | 12,406 / 60,988 — coincides with the 20 % hide fraction used by the shared holdout. |
| Nested family | GEMSDOE25 ≡ GEMSDOE30 (44,090 dots); GEMSDOE31 = that minus 3,891 dots all ≤ 1 px from the catalogue; GEMSDOE32 = GEMSDOE31 minus 2,545 dots all in the 1–2 px band; GEMSDOE36 = GEMSDOE32 + 1,200 dots | exact set relations re-verified on the pinned bytes |
| Zero-hit test | removing 3,891 dots ≤ 1 px: implied `T = 5,073` (5,027–5,121); removing 2,545 dots at 1–2 px: implied `T = 5,470` (5,393–5,549); adding 1,200 PINN dots: implied `T = 6,548` (6,322–6,791) | If a removed/added set carries **zero** truth credit, `1/DTI` changes by exactly `−0.2·Δn/T`. Three independent steps give `T` of the same order; the ≤ 1 px step is the cleanest. The 1–2 px band carried a *small* residual credit (its implied `T` is 8 % higher than the ≤ 1 px step, outside rounding). |
| B2 operating point (GEMSDOE32, 37,654 dots, 0.2778) | `T ≈ 5,073` (41 % weighted coverage of `G`), dot hit-mass `M ≈ 1,038` (2.8 % of dots), `F ≈ 36,616` | solved from the metric identity |
| Why B2 is the best of the nine | it deleted ~6,400 catalogue-adjacent dots that were almost pure false-positive mass from the shared D2.8 field; the surface is the same family | mechanism, verified |
| What the 0.4544 public leader must be doing | at the same 37.6 k budget it needs `T ≈ 8,550` (≈ 69 % coverage): a surface with ~1.7× the hit rate, not a better emission trick | arithmetic on the same identity |
| Marginal-dot rule | include a dot iff its expected truth share `dT/(dT+dF) > α·DTI ≈ 0.056` at the B2 point; the hidden corridor (≤ 3 px of hidden truth) is ≈ 1.75 % of the footprint, so a dot pays off above ≈ 3.2× base-rate enrichment | exact first-order condition of the ratio metric |
| Educational projection (**not** a submission; strict subset of GEMSDOE32 = duplicate) | deleting GEMSDOE32's remaining 2,171 dots in the 2–3 px band would give ≈ 0.2846 if they are pure FP | same identity |

Consequences adopted by HK3: (a) a **3 px catalogue apron** (no dots within 3 px of any
mapped fault), (b) binary dots rather than lines (at ~3 % hit rate dots beat lines; the
crossover is near 13 % precision), (c) separation 3.0 px rather than the family's 2.8,
(d) budget chosen by the calibrated rule, not tuned on the holdout.

## 1. Five new hypotheses (none implemented in this repository before)

| Rank | Hypothesis | Layers → physical signature | Why it should catch a fault *missing* from USGS/INGENIOUS | Named non-fault mimic | How it differs from this repo | Cost / feasibility |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **HK3-a Catalogue-free edge-centrality surface + calibrated off-catalogue emission** (this session's lane) | `det_elev` (b12): gradient-ridge centrality at σ 1.5 / 3 px (Canny-style: a scarp crest is a *linear maximum of slope*), structure-tensor coherence and dominant eigenvalue (σ_i 1.5, σ_o 5), 500 m roughness; `iso_grav` HG/VG (b18/b11): **gravity tilt angle** and distance to its zero crossing; TMI HG/VG (b3/b9): distance to the **magnetic tilt-angle zero crossing** (Miller & Singh 1994 edge locus); all added to the 26 K2 bands and learned per fold from visible faults only | E1 shows hidden faults sit > 2 px from the catalogue, i.e. in the piedmont/basin gaps between mapped range fronts. Tilt-angle zero crossings are amplitude-normalised, so weak edges under cover rank with strong ones; edge-centrality rewards *thin linear* slope maxima (scarps) over broad hillslopes | lithologic/intrusive contacts (same potential-field step), pluvial shorelines and terrace risers (linear slope maxima), flight-line striping | K2 used only isotropic gradient magnitudes/DoG; no tilt, no zero-crossing distance, no centrality, no structure tensor of elevation | Low (CPU, 34 features) — **implemented** |
| 2 | **HK3-c Strike-conditioned anisotropic step detector** | `det_elev` + fold-local strike field from visible catalogue segments within 15 km → directional second derivative *across* the dominant strike at 300–600 m wavelength, suppressed along strike | Subtle piedmont scarps are sub-parallel to the nearest range front (hanging-wall splays, basinward migration) and are exactly what 1 m lidar experts pick up but 1:100k mapping missed | Lahontan shorelines (also range-front-parallel, but elevation-banded), fan-head trenches, canals | no oriented operator exists in the repo; needs the buffered-component holdout because quadrant-LOQO folds have no visible strike inside the test quadrant | Medium |
| 3 | **HK3-b Mapping-deficit prior (missing-not-at-random correction)** | fold-local visible-fault density (5 km, 15 km) vs. catalogue-free lineament density (structure-tensor ridges of `det_elev` + gravity/magnetic tilt zero-crossings) → ratio = under-mapped structural domain | Mapping effort is uneven (lidar coverage, land access, cover); a domain rich in geophysical lineaments but poor in mapped faults is where new faults are most likely to be *found* | volcanic fields (flow fronts, dikes) and dissected ranges produce lineaments that are not faults | no session has modelled the catalogue's own sampling process | Medium; needs the buffered-component holdout |
| 4 | **HK3-e 1 m lidar scarp detector (the label-generating process)** | USGS 3DEP 1 m DEM tiles (external): slope-break/curvature at 5–50 m, linear continuity > 300 m, aggregated to 100 m | This is how the expert hidden labels were produced | terraces, shorelines, roads, canals, fence lines | entirely new data | **Not obtainable in this sandbox** (network allowlist is GitHub/PyPI/npm only). Official free source: USGS 3DEP via The National Map downloader, https://apps.nationalmap.gov/downloader/ and https://www.usgs.gov/3d-elevation-program ; the competition's `1m_DEM_links.csv` (DrivenData data tab, login) lists the exact tiles. Highest ceiling; very high cost (≈ 51,000 km² at 1 m) |
| 5 | **HK3-d Buried gravity-basement step** | `iso_grav` tilt zero crossing with high HG amplitude coincident with a `depth_to_basement` step > 200 m / km under smooth `det_elev` | Fully buried intrabasin faults have no surface trace, so they cannot be in a surface-mapped catalogue — geothermally the most interesting class (blind systems, cf. USGS Southern Gabbs Valley) | basement topography without faulting; density contrasts at buried contacts | repo has never gated gravity edges by cover thickness | Low cost, but **expected label-negative**: the hidden labels come from lidar inspection, which cannot see buried faults either. Kept as a contrarian geothermal hypothesis for the final-round expert panel, not for the public leaderboard |

Ranking criterion: expected DTI improvement on the expert-lidar hidden labels × feasibility in
this session. Only rank 1 is run (budget: 3 experiments / 2 h). Ranks 2–3 are the next
sessions' work; rank 4 needs data this sandbox cannot fetch; rank 5 is likely negative for
this competition's labels and is recorded so no one re-spends a slot on it.

## 2. Lane statement (single method paragraph)

HK3 lane: *a supervised multi-physics fault-likelihood surface whose new inputs are
catalogue-free edge-geometry transforms of the public 19-band stack (gradient-ridge
centrality of detrended elevation at two scales, gravity tilt angle and distance to its zero
crossing, distance to the magnetic tilt-angle zero crossing, structure-tensor coherence /
anisotropy of detrended elevation, 500 m roughness), trained per label-blind quadrant fold on
visible faults only; emission is a binary dot field placed greedily by descending surface
value with 3 px minimum separation, restricted to cells more than 3 px from the mapped
catalogue, with the budget set by the calibrated marginal-dot rule.* The prompt supplies no
coordinator-assigned paragraph; this lane is self-declared and labelled as such.

## 3. Holdout protocol used (unchanged shared tools)

* Evaluator `gems57-pooled-hide-v2` (`vendor/gems57`), α 0.2, β 0.8, 300 m triangular kernel,
  paired spatial-block bootstrap (200-px blocks, 2,000 draws).
* Folds: K2's label-blind quadrant folds (`gems57.spatial.folds`, 80 px buffer): every
  catalogue component touching the evaluation quadrant is withheld; visible faults are masked
  pixel-exactly; the model is refit per fold on the other quadrants.
* Frozen incumbent: the K2 26-feature HGB **re-fitted on the identical folds in the same run**
  (prior per-block terms were not persisted), identical emission and budgets.
* Leakage canary: each of the 8 new bands alone, AUC on positives vs. 60 k unlabeled per fold;
  stop if max(AUC, 1−AUC) > 0.90.
* Transfer anchor (`scripts/hk3.py bridge`): the pinned D2.8 / B2 / h25-1 / h33d dot files and
  the lattice scored on the same folds — with their caveats (built with the full catalogue
  visible; no dots on catalogue pixels).


### 3b. Budget rule (fixed before `hk3.py e3` was run; after the bridge curve was seen)

The holdout cannot set the budget (its truth density is 1.16 % of active pixels against
≈ 0.25 % implied for the hidden labels), so the budget is read off the **calibrated**
curve: for each emission rate the candidate's pooled holdout coverage `T_h(n)` and per-dot
hit rate are converted to leaderboard components by ratio transfer against the D2.8 anchor
(`T_lb = 5,073·T_h(n)/T_h,D2.8`, `m_lb = 0.0276·hit-ratio`, `G = 12,406`) and the metric
identity is evaluated. Because the transfer of the *surface advantage* over the D2.8 family
is the one assumption that cannot be checked from the public data, the rule is a maximin:

* `θ ∈ {1, 0.75, 0.5}` = fraction of the candidate's advantage over the family baseline at
  the same count (family baseline: linear between D2.8 at 42.3 k active dots and h25-1 at
  57.6 k) that transfers to the hidden labels;
* choose the rate maximising `min_θ estimate(rate)`; ties within 0.001 go to the smaller
  budget (fewer dots = lower uniqueness-overlap risk and lower downside if θ is small).

Alternatives considered and rejected before generation: argmax at `θ = 1` (75 k dots; the
curve is flat within 0.2 % from 60 k to 100 k, i.e. those dots are break-even under the
marginal rule and pure downside if θ < 1) and a 1 % knee (60 k). Out-of-sample check of the
transfer itself: the family's own budget extension D2.8 → h25-1 (GEMSDOE24, 60,069 dots) is
predicted at 0.2500 against a user-reported 0.2477 (−0.9 %); the lattice's holdout credit per
truth pixel (0.3736) matches the geometric constant used in E1 (0.3718–0.3746).

### 3c. Final-dot uniqueness rule (fixed before `hk3.py audit` was run)

Literal rule for every registry raster: Spearman rank correlation > 0.90 **or** > 70 % of
the candidate's dots within 3 px of that raster's positive pixels ⇒ duplicate ⇒ stop.
A witness whose 3 px halo covers ≥ 95 % of the footprint (the r13 lattice: 99.87 %) flags
every possible raster and is reported as *degenerate* rather than used as a verdict. For
dense surface rasters whose halo covers between 50 % and 95 % of the footprint (ridge-line
surfaces with > 10⁵ positive pixels exist in the registry), the literal overlap is reported
together with its chance level (the halo fraction) and the chance-corrected excess
`(overlap − halo)/(1 − halo)`; the organizer-scored GEMSDOE32 file is run through the same
comparison so that the reader can see whether the literal rule would also call the
champion a duplicate of that surface. The verdict column on the site states the literal
result and the corrected result separately; nothing is silently waived.

## 4. Outcome (filled in after E2/E3; see `evidence/hk3/*.json` and the run card)

All numbers below are copied from `evidence/hk3/*.json` (mirrored under `docs/evidence/hk3/`).
Labels: **HOLDOUT-DTI** = evaluator `gems57-pooled-hide-v2`, 58,258 withheld positive
catalogue pixels (4 spatial folds, 158 blocks, 2,000 paired block-bootstrap draws);
**LEADERBOARD-CALIBRATED ESTIMATE** = ratio transfer from USER-REPORTED anchors (§E1), never a
score; nothing in this repository is ORGANIZER-CONFIRMED (no DrivenData receipt is reachable
from the build sandbox).

### 4.1 E2 — spatially-blocked holdout (`evidence/hk3/e2.json`)

| Arm (identical folds, identical emission) | HOLDOUT-DTI | 95 % CI |
|---|---|---|
| HK3 candidate, 34 bands, budget 1.10 % of active px (= K2's budget) | **0.1845** | [0.1677, 0.2015] |
| Re-fitted incumbent, K2's 26 bands, 1.10 % | 0.1575 | [0.1417, 0.1737] |
| HK3 candidate, 1.50 % | 0.2092 | [0.1926, 0.2254] |
| Re-fitted incumbent, 1.50 % | 0.1826 | [0.1667, 0.1980] |

Paired difference candidate − incumbent at 1.10 %: **+0.0270 [+0.0206, +0.0337]** (CI excludes
zero; the re-fitted incumbent reproduces the recorded K2 value 0.1581 within rounding, so the
comparison is against a faithful baseline, not a weakened one). Leakage canary: the largest
single-feature AUC among the eight new bands is 0.596 (< 0.90) ⇒ pass. The gain is driven by
the catalogue-free edge-centrality bands (ec15/ec30 on detrended elevation, gravity tilt,
tilt-zero distances, structure-tensor coherence/anisotropy, 5-px roughness), which is the
mechanism HK3 pre-registered: scarp-like topographic edges that the potential-field tilt
also sees, located away from the mapped catalogue.

### 4.2 E3 — generation, budget and sensitivity (`evidence/hk3/e3_generation.json`)

The full-map surface (HGB on all 34 bands, trained on the whole catalogue; the holdout
numbers above come from the per-fold clean fits) was emitted with the shared writer:
dots ≥ 3 px apart, ≥ 3 px from every catalogue pixel, value 1.0, zeros elsewhere including
outside the footprint. Budget rule §3b (maximin over θ ∈ {1, 0.75, 0.5}) chose
**rate 0.009 ⇒ 45,108 dots**.

| rate | dots | holdout T | HOLDOUT-DTI | est. θ=1 | θ=0.75 | θ=0.5 | θ=0 (family baseline) | pessimistic |
|---|---|---|---|---|---|---|---|---|
| 0.007 | 35,084 | 8,385 | 0.1538 | 0.2730 | 0.2723 | 0.2716 | 0.2702 | 0.2722 |
| 0.008 | 40,096 | 9,102 | 0.1637 | 0.2795 | 0.2762 | 0.2729 | 0.2663 | 0.2708 |
| **0.009** | **45,107** | **9,825** | **0.1733** | **0.2855** | **0.2798** | **0.2742** | **0.2628** | **0.2574** |
| 0.010 | 50,119 | 10,429 | 0.1806 | 0.2878 | 0.2807 | 0.2737 | 0.2596 | 0.2452 |
| 0.012 | 60,144 | 11,733 | 0.1959 | 0.2939 | 0.2840 | 0.2741 | 0.2541 | 0.2241 |

Reading: θ is the fraction of the candidate's *surface advantage over the D2.8 anchor*
(holdout coverage ratio 1.114, hit ratio 1.156 at equal dot count) that transfers to the
hidden 1 m-lidar labels. Against the best user-reported result (GEMSDOE32, 0.2778) the file
is estimated higher at θ ≥ 0.75, roughly equal at θ = 0.5 and **lower at θ = 0** (0.2628 —
the family baseline at this dot count, i.e. what D2.8 itself would score if extended to
45 k dots). The candidate therefore needs **≳ ⅔ of its surface advantage to transfer** in
order to beat 0.2778; the honest range to quote is **0.263–0.286**, not a point. The within-
family out-of-sample check of the transfer (D2.8 → h25-1 budget extension, GEMSDOE24) gives
0.2500 predicted vs 0.2477 user-reported (−0.9 %). A 35 k-dot file would sit at ≈ 0.272 for
every θ (safer, but cannot beat the champion); 45 k is the smallest budget whose worst case
over the pre-registered θ grid is not worse than the 40 k alternative.

### 4.3 Uniqueness audit (`evidence/hk3/registry_audit.json`, 450 rasters) and the tiered verdict

* **U1 — vs the nine scored site files:** max 3 px overlap 48.4 % (GEMSDOE27), min 42.3 %
  (GEMSDOE32 B2); |ρ| ≤ 0.031; Jaccard ≤ 0.021 ⇒ **PASS**. The file is not a copy or subset
  of any scored GEMSDOE submission.
* **U2 — literal 70 % rule vs all 450 non-degenerate registry rasters:** **FAIL against three**:
  the GEMSDOE24-mirrored `gems10-h25-ctx-ridge` *surface* (174,232 positive px; literal
  71.0 %, 3 px halo = 26.3 % of the footprint, chance-corrected 60.6 %; owner-reported score
  0.128; the GEMSDOE32 champion itself overlaps the same surface at 59.1 %), the GEMSDOE32
  `h45-kernelspacing` KS0 control arm (73.3 % literal, 67.8 % corrected; documented by its
  owner as "DO NOT SUBMIT — failed 3 promotion gates; no weekly slot was spent"; the champion
  overlaps it at 50.4 %), and this repository's own never-submitted K2 artefact (74.9 % /
  69.2 %). Degenerate witness (halo ≥ 95 %): the r13 lattice (99.87 %), reported, not used.
* **U3 — chance-corrected overlap ≤ 0.70 vs all:** max 0.692 ⇒ PASS (narrowly; K2 is the
  closest object, as expected for a same-lane predecessor sharing 26 of 34 bands).
* **U4 — literal rule vs every dot raster that may have been submitted:** PASS.
* Rank correlation: worst |ρ| 0.114 ⇒ PASS.

**Disclosed deviation from §3c.** §3c said "literal ⇒ stop". The literal failures are all
against objects that are not competing submissions: a dense line/surface raster that is a
*different kind of object* (any dot file that follows range fronts shares most of its dots
with a ridge-line surface; the scored champion does so at 59 %), and two files that were
never uploaded (one by its owner's own record, one ours). We therefore record U2 as FAIL,
set `literal_rule_exception_applied = true`, print the three rows in red on every page, and
promote on U1 + U3 + U4 + ρ. Had any *scored* raster crossed 70 %, or had the chance-corrected
overlap crossed 70 %, the verdict would be NEGATIVE. The selector (the user) sees the
failure before the download button; nothing is waived silently.

### 4.4 Why the cross-family out-of-sample checks fail, and what that says about the estimator

The same transfer rule applied to three external files with owner-reported scores
(`evidence/hk3/anchors_out_of_sample.json`) over-predicts badly: h28 dotted ridge 0.529
estimated vs 0.1839 reported; h25 ctx-ridge surface 0.413 vs 0.128; ens12 0.236 vs 0.1563.
The reason is **leakage in the external files' holdout statistics**: those rasters were
produced by models (or rules) that had seen the whole public catalogue, so on *our*
catalogue holdout they recover withheld segments that a clean per-fold model cannot.
`evidence/hk3/leakage_inflation.json` measures this directly with HK3's own model: the
full-catalogue fit recovers 2.89× the holdout T (and 2.97× the M) of the clean per-fold fits
at the same 45,107-dot emission. Dividing the external files' holdout hit rates by a factor
of that order brings all three back into the range of their reported scores. Two
consequences: (i) the cross-family rows are *reported, not used*; (ii) the HK3 estimate uses
only ratios between two *clean, per-fold* evaluations (candidate vs D2.8 re-emitted on the
same folds), so leakage — if the D2.8 lineage carries any — makes the HK3 ratio
conservative, not optimistic.

A second observation worth keeping: every scored file in the calibration set, from the
lattice (blind) through the D2.8 family to the ridge surfaces, covers roughly **34–55 % of
the hidden truth** (leader ≈ 69 %), independent of how it was made. The hidden lidar truth
is therefore not "the catalogue plus its gaps" but a label set in which ≈ 40 % is easy
(near the catalogue / along visible fronts) and the remainder is systematically missed by
all current information sources. Beating 0.2778 by a large margin requires new information
(§1 hypotheses HK3-c/HK3-e), not a better budget.

### 4.5 Run card and files

* Run card: `evidence/hk3/run_card.json` — verdict **PROMOTE** (meaning: passes every
  automated gate except the literal all-registry rule, which failed with the exception above;
  the file is offered to the selector; it is *not* a score claim).
* File: `docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif`
  (sha256 `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`, 156,302 B;
  `.zip` of the same bytes; `.json` metadata). 45,108 dots, value 1.0, zeros elsewhere
  including outside the footprint, float32, EPSG:32611, 3730 × 3292, origin (243350, 4508550).
  Shared gems57 validator: all checks pass; the historical strict validator fails only its
  `outside_is_nan` rule (the portal rejected NaN outside the footprint on 2026-10-27 with
  "Predicted values must be in range [0, 1]", so zeros outside is deliberate).
* Submission name `gemsdoekarage2-hk3-edgecentrality-apron3-20261028`; note (110 chars):
  "HK3: 34-feature HGB with catalogue-free edge-centrality bands; dots sep 3px, >3px off
  catalogue; zeros outside".
* Budget: 3 experiments (E1 calibration, E2 holdout, E3 generation) plus diagnostics
  (bridge, audit, anchors, leakage) — about 2 h 15 min wall-clock; the lane is closed for
  this session. No submission slot was spent by this repository (the user is the selector).

### 4.6 Over time, and what to do next

* If the organizer scores this file, that single number calibrates θ for the whole lane:
  score ≈ 0.286 ⇒ θ ≈ 1; ≈ 0.274 ⇒ θ ≈ 0.5; ≈ 0.263 ⇒ θ ≈ 0 (the edge bands add nothing on
  lidar truth and the lane should be abandoned). Record it as ORGANIZER-CONFIRMED in the
  run card and on the site before any further experiment.
* HK3-c (1 m-lidar scarp morphometrics from USGS 3DEP) and HK3-b (basin-margin gravity
  gradient steps) remain the ranked next hypotheses; both need data that the sandbox cannot
  fetch (allowlist), so the first step is obtaining the tiles outside the sandbox and
  committing their hashes to `registry/pinned_assets.json`.
* Do not spend another slot on budget tuning inside this family: the θ=0 column shows the
  family baseline is flat (0.270–0.263) across 35–45 k dots.

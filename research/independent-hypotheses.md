# Preregistered research slate — proposals, not results

Read `README.md` and `independent-sources.md` first. No specific assigned method paragraph
appeared in the request; the four ideas below are **unexecuted proposals**, not
permission to enter another parallel lane. Ranking is qualitative judgment about
potential discovery value versus effort, **not a numerical score forecast**. This
checkout had no detector at the start. We compared the proposals with the
historical H33 pruning family and a limited review of sibling project pages; we
cannot prove that a similar idea has never been tried anywhere in the fleet.

| Rank / relative cost | Layers and physical signature | Why it might find a fault missing from the catalogue | Named non-fault mimic / essential falsification | Difference from this checkout and the H33 family | Data availability |
| --- | --- | --- | --- | --- | --- |
| 1 · medium | **Signed multiscale cross-profile coherence:** reduced-to-pole magnetic anomaly (`rtp`), isostatic gravity anomaly, detrended elevation. Measure oriented, odd-symmetric changes on multiple scales, retaining sign and displacement between a surface break and subsurface contrast. | A concealed strand could produce coherent offsets in independent-looking fields even when no mapped trace exists; no catalogue proximity feature is needed. | An unfaulted lithologic contact or flight-line levelling artifact can generate both an apparent magnetic edge and geometric alignment. Compare against contact/flight-direction controls; inspect geophysical resolution and exclude acquisition seams. | H33 is an inherited sparse pattern with a distance-to-catalogue pruning rule. Here the *proposed* surface uses signed multiscale profiles rather than pruning existing dots. Similar cross-gradient approaches exist elsewhere, so fleet-wide novelty is unproven. | The 19-band **owner mirror** was fetched and hash-checked via GitHub, not authenticated directly from DrivenData. Band names/units need organizer/source verification. |
| 2 · medium | **Conductive-horizon edge persistence:** `cond_surf` plus `depth_to_base_surf`, isostatic gravity and `rtp`; detect spatial changes in conductivity and conductive-base depth aligned with independent potential-field breaks. | A covered structure could disrupt conductive layers while lacking a visible mapped surface trace. | Conductive playas, clay-rich basin fill, or a conductivity inversion boundary can mimic the signature. Measure separately by geologic/coverage regime and require physical concordance, not a raw conductivity high. | Different from this empty checkout and the H33 catalogue-distance pruning mechanism; prior sibling conductive-edge methods exist and must be screened. `depth_to_base_surf` must not be assumed to be depth to crystalline basement. | Competition descriptions list a conductive base; owner-mirror bands are obtainable, but authoritative metadata and meaningful depth units must be confirmed. |
| 3 · high | **Topographic break persistence versus paleoshoreline:** 3DEP elevation / local slope, curvature and along-contour persistence, plus a subsurface gravity contrast. Compare asymmetric profiles at multiple scales with a constant-elevation shoreline null. | A subdued, degraded fault scarp across an alluvial surface can persist beyond an existing mapped segment. | Former lake shorelines, alluvial fan margins, roads and erosional terrace risers. Strong controls are mandatory; a contour line alone is not a fault. | Unlike H33's catalogue-only pruning, this tests a morphologic null. Similar lidar/scarp/shoreline lanes exist in siblings; an exact method collision check is required. | [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) describes public elevation data; the exact tile list and coverage were **not fetched or validated** here. Deferred, not ready to run. |
| 4 · medium | **Strain-regime boundary with magnetic evidence:** geodetic shear/dilatation rate and reduced-to-pole magnetics; use changes in relative orientation over broad spatial blocks to weight, not invent, short magnetic breaks. | Changes in the regional strain field may help prioritize structural boundaries not represented in the existing surface catalogue. | A smooth interpolation edge in the geodetic model or a volcanic/lithologic contact. Test within held-out geographic blocks, ablate strain bands and use acquisition-orientation nulls. | H33 changes dot geometry near known traces; this tests an independently motivated regime interaction. Novelty across every sibling repository is unknown. | The owner-mirrored 19-band TIFF is obtainable. [GDR 1391](https://gdr.openei.org/submissions/1391) publicly lists the geodetic dataset; direct transfer was blocked here and units / license applicability require verification. |

## Relative improvement expectations, not scores

Before any data fitting, the subjective order of *possible* holdout improvement
relative to a matched shared control is #1, #2, #3, then #4: cross-field coherent
edges have the broadest plausible footprint; conductive-horizon edges may help
where the inversion has coverage; scarp tests could help locally but bring
shoreline/domain-shift risk; smoothed strain could be too coarse for short
segments. This is a prioritization hypothesis only. Each actual paired
HOLDOUT-DTI change could be negative; there is no justified numerical improvement
range or transfer to leaderboard performance. Costs and available inputs are
listed in the table, and no proposal was run.

## Frozen test plan, before any slot is considered

1. Confirm the assigned single lane and an authoritative, complete parallel
   registry, including whether the retained calibration lattice is included.
   Do **not** quietly exempt it or force dots into edge holes.
2. Reuse the pinned shared template's cached stack, `evaluate_holdout.py` and
   `submission_writer.py`. Its pinned CLI currently contains a frozen MTR1
   runner, not a generic implementation of any of the proposals above; a
   lane-specific adapter must use the same shared primitives, not a private
   scorer/writer fork. If a shared defect is established, fix it upstream.
3. Withhold whole fault segments/components with a buffer, derive every
   catalogue feature only from the visible faults, and mask visible faults
   pixel-exactly. Raster connected components are a proxy, not authenticated
   fault segment IDs. Run every feature alone as a leakage canary; AUC > 0.90
   stops the run until the leakage concern is resolved.
4. Compare the top hypothesis with the current **same-evaluator** frozen best,
   using pooled DTI and a spatial-block paired 95% CI. Holdout is a biased
   catalogue proxy, not a calibrated hidden-score prediction. Apply surface
   uniqueness before any dot placement and final-dot uniqueness afterwards.
5. Use the shared writer and validate the exact saved bytes, including inside
   non-finites, range, dtype, CRS, shape, transform, and both exterior-format
   diagnostics. A format pass never authorizes a slot. Run at most 3 experiments
   or 2 hours; use a separate selector for any real slot.

## Stop recorded for this session

The requested literal "any registry raster" rule includes a registered
space-filling lattice. The measured valid footprint has 6,649 cells farther
than 3 pixels from the lattice. At the H33-family budget of 37,654 distinct
in-footprint dots, **at least 31,005 / 37,654 = 82.34%** must be within 3 pixels
of it, even for an unrelated detector. This exceeds the allowed 70%. The result
is a geometry audit, not HOLDOUT-DTI. It is a strict stop for that budget, not a
proof that all smaller dot budgets are impossible. The run was stopped before
model fitting, surface placement or new TIFF generation; the next experiment
must not be engineered merely to exploit the remaining boundary holes.

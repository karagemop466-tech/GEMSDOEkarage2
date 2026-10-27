# Research slate: untested proposals, not assigned lanes

Recorded 2026-10-27 UTC, **before any experiment in this checkout**. This new
checkout started with no implemented detector. The ranking below is a
qualitative judgement about possible incremental hide-and-recover value versus
implementation cost, **not a score or predicted leaderboard gain**. We cannot
prove that any idea is untried across all parallel repositories. Before a future
run the coordinator must compare its precise operator with the shared, current
hypothesis registry and supply the missing single method paragraph. None was
trained or tested here; the literal novelty preflight is a separate blocker.

| Rank | Layers, physical signature, geological reasoning | Non-fault mimic / difference | Cost and access |
|---|---|---|---|
| 1 | **Cross-scale normal displacement.** Use the competition `rtp`, `iso_grav_anom`, `det_elev` and `det_elev_slope`. At multiple Gaussian scales estimate local gradient normals and the signed shift between gravity and magnetic gradient profiles; retain line-like breaks with independent topographic support. A buried offset may leave displaced subsurface contrasts even when a surface fault was not mapped. | Lithologic contacts, intrusions, erosion and flight-line artifacts can produce similar gradients. This is a proposed *signed cross-scale profile displacement*, not merely a gradient magnitude or the published H33 orientation-consensus product. No detector of any kind existed in this checkout; fleet-wide novelty is unverified. | **Medium.** The original 19-band owner mirror was restored and hash checked; the required prepared shared feature cache is not present. Official organizer bytes not authenticated. |
| 2 | **Strain-conditioned opposing topographic profiles.** Use `det_elev`, `det_elev_slope`, `geod_shearrate` and `geod_dilaterate`; estimate opposite-side elevation profiles and use coarse strain only as a regional interaction, never as a 100 m location. A subdued surface flexure in an active deformation regime could flag an unmapped strand. | Alluvial-fan toe and erosional terrace edges. Distinct from a plain scarp response: requires paired across-line profile asymmetry and interaction with geodetic strain. The catalogue-based exclusion is built afresh from visible folds. | **Medium.** Named bands exist in the restored owner mirror; the shared prepared stack is absent. Magnitude and directional interpretations require independent source metadata. |
| 3 | **Paired tributary deflection, not a knickpoint detector.** Use bare-earth [USGS 3DEP](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services) elevations plus [NHD/3DHP flowlines](https://www.usgs.gov/national-hydrography/national-hydrography-dataset); measure the consistency of channel deflections across a line with a matched no-line background and an elevation-break corroborator. Repeated deflected channels could reveal a poorly mapped active trace. | Channel avulsion, fan migration and human-built canals. Unlike a single knickpoint or valley ridge, this looks for paired, repeated deflections and a matched control. NHD was retired in 2023; available downloads are legacy, while 3DHP is the maintained successor. | **High, currently blocked.** USGS describes downloadable datasets and free 3DEP access, but this runtime did not retrieve the needed tiles or verify footprint coverage or license for a concrete package. Not ready to run. |
| 4 | **Seasonally stable thermal contrast conditional on lithology.** Use [Landsat Collection 2 Level-2 surface temperature](https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature), seasonally matched and topographically normalized, with GeoDAWN magnetic or radiometric contrast. Test whether persistent linear anomalies track otherwise unrecognized faults. It is only a weak prospect proxy, not direct evidence of a vent or fluid flow. | Insolation, soil moisture, lithology, irrigation and missing emissivity data. This differs from a one-date hot-spot proximity feature by requiring temporal persistence and matched controls. | **High, currently blocked.** USGS describes globally available, unrestricted products, but no scenes, local completeness, extraction, or licensing for other associated inputs were verified in this runtime. |

## Required experiment, if the blockers are resolved

Use the **unchanged shared template** `evaluate_holdout.py`/`submission_writer.py`
with its actual cached features, not the historical file as a starting prediction.
Preregister the assigned operator and feature names. Withhold whole fault
segments in buffered geographic blocks; construct every label-derived feature
from visible faults in that fold; mask visible faults pixel-exactly; assess each
feature alone against held-out labels (AUC > 0.90 is a leakage stop). Check the
unmodified candidate surface against **every** registered raster before
placement, and the saved dots afterwards, including the literal lattice unless
the coordinator changes the rule. Use pooled distance-weighted Tversky
(alpha 0.2, beta 0.8, 300 m triangular kernel), with withheld-positive counts,
a spatial-block confidence interval, and paired comparison to the current best
under the same protocol. A negative result is retained; no weekly slot is used
unless the separate selector authorizes it. No part of this plan is an observed
DTI or evidence that the hidden leaderboard will improve.

## Grounding

* [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — target, input families, metric and format.
* [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) — geophysical survey, field acquisition limitations, CC0 data-release description.
* [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) — free DEMs and availability information.
* [USGS/DOE INGENIOUS compilation](https://gdr.openei.org/submissions/1391) — public data under CC BY 4.0; individual layers need source-specific checks.
* [Faulds and Hinz, OSTI](https://www.osti.gov/biblio/1724082) — structural settings for blind geothermal systems; does not establish that a predicted fault hosts geothermal fluid.

**Late source change:** After our nine-site audit was pinned, GEMSDOE25 merged [H79 CTHM / SGMC research](https://github.com/buffedlizard55-lab/GEMSDOE25/blob/19b219f629440b9975b093f459c74e21a42476ca/knowledge/40_h79_cthm_poe_outcome_2026-10-27.md) using overlapping gravity, magnetic, topographic and hydrothermal ingredient families. We have not reproduced that work. The exact cross-scale displacement operator may differ, but this does not establish uniqueness; compare its pre-placement surfaces and final dots against H79 and the complete current registry before any experiment can be promoted. The upstream work also reports a negative, no-submit verdict.

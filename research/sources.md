# Source and evidence register

Reviewed through the web-reading tool on 2026-10-27 UTC. Official webpages
were readable through that tool; the sandbox itself is restricted to GitHub and
package registries. We did **not** authenticate to DrivenData, download from
Dropbox, retrieve the full external datasets, inspect private labels, or verify a
submission receipt or team quota. A public listing is not proof that every
needed tile can be obtained in this runtime.

| Source | Authority / verified statement | Access / caveat |
|---|---|---|
| [DrivenData problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | Fault prediction; grid description; alpha 0.2, beta 0.8; 300 m triangular kernel; `float32`, one band, [0,1]. | Public page read. Official feature files and sample require login. |
| [DrivenData overview](https://www.drivendata.org/competitions/306/competition-doe-gems/) | Competition dates, entry process and external-data policy. | Public page read. |
| [Submission page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/) | Portal submission and any team-specific remaining quota. | Redirected to login; remaining quota and receipts unknown. |
| [Official rules, section 3.2](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | One GeoTIFF, 100 m, three submissions per week as written in the PDF; generative-AI use must be disclosed in the narrative. | PDF read; the live portal controls the actual current cap and team eligibility. |
| [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | Public ranks and scores, not a file-bound receipt or private result. | Snapshot read through web tool; may change. |
| [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) | Reference approach and reproducibility instructions. | Public GitHub; not the template cached stack. |
| [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) | Airborne magnetic and radiometric measurements; flight height and terrain-clearance limitations; CC0 data-release record. | Public page read; not a provenance verification of owner-converted cache. |
| [USGS Quaternary faults](https://www.usgs.gov/programs/earthquake-hazards/faults) | Public mapped fault database; mapped features are not an exhaustive set of all faults. | Public page read; no guarantee of equivalence to competition labels. |
| [INGENIOUS regional data, DOI 10.15121/1881483](https://gdr.openei.org/submissions/1391) | Faults, seismicity, wells, geochemistry, thermal and other resources; CC BY 4.0 on the compilation page. | Public listing read; not a verification of each component's license or local coverage. |
| [USGS electrical conductance maps](https://www.sciencebase.gov/catalog/item/62979746d34ec53d276c113b) | Five depth-range conductance grids based on a 3-D inversion; subsurface conductivity is not unique to fluids. | Public product listing read; files not fetched. |
| [USGS 3DEP](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services) | USGS says 3DEP products are free and without use restrictions. | Public page; GeoDAWN-specific tiles/coverage not verified here. |
| [USGS National Hydrography Dataset](https://www.usgs.gov/national-hydrography/national-hydrography-dataset) | NHDFlowline represents stream and artificial network geometry; NHD retired in 2023; 3DHP is the successor. | Downloads listed; project-specific coverage not downloaded. |
| [USGS Landsat Collection 2 surface temperature](https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature) | Global scene-based surface-temperature products and cited usage terms; known emissivity gaps. | Public page; no scenes fetched and no claim of usable coverage. |
| [Faulds & Hinz structural inventory, OSTI](https://www.osti.gov/biblio/1724082) | Structural step-overs, terminations and intersections are geothermal exploration settings. | Research evidence, not proof that any particular prediction is a vent. |
| [GEMSDOE32 shared manifest](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/73485f27cf230af770167397c2b72cb9ce3b3f25/registry/data_manifest.json) | Hashes and location of owner-supplied competition mirrors. | Third-party evidence; self-consistency hashes do not prove organizer origin. |
| [GEMSDOE24 registry](https://github.com/buffedlizard55-lab/GEMSDOE24/blob/2521cb676e172c141a4417e4925b73b6a896c1eb/registry/priority_rasters.json) | Includes the r13 lattice among registered rasters. | Registry membership, not geological ground truth; no exception to the literal rule assumed. |

## Irregularities

1. The prompt gives conflicting leaderboard snapshots. The official public
   leaderboard was read on 2026-10-27; its top value is a **dated snapshot**,
   not evidence for any particular file. Do not claim it is live after the
   snapshot ages or if refresh fails.
2. The public owner-mirror `sample_submission.tif` has 60,988 positive cells
   exactly matching `existing_faults.tif`; the organizer page describes a
   sample predicting total fault absence. The grid can be used for this *scoped
   geometry audit*, but cannot be represented as a verified official template.
3. The owner-supplied reference hashes prove the downloaded files are the
   pinned mirror bytes; they do not establish that they match authenticated
   DrivenData originals or that the derived labels are authoritative.
4. NaN outside the footprint is described in the official format, while the
   user reported a portal range rejection. We cannot determine the cause or
   whether zero-filled or masked exterior pixels would be accepted. Both a
   local format pass and a portal receipt are separate from scientific gates.
5. A spacing-5 lattice is a registered calibration control. The literal “any
   registry raster” rule includes it and makes a champion-sized placement
   mathematically incompatible with the 70% overlap ceiling. A new filename,
   hash, or intentional movement to lattice holes does not resolve the policy.
6. A full current parallel registry, an explicit method paragraph, prepared
   shared features, fold-safe run/CI, organizer receipt and quota are absent.
   Restoring the owner-mirror raw inputs does not satisfy those gates.

### Upstream changed during this review

- GEMSDOE25 merged [H79 CTHM / SGMC research](https://github.com/buffedlizard55-lab/GEMSDOE25/blob/19b219f629440b9975b093f459c74e21a42476ca/knowledge/40_h79_cthm_poe_outcome_2026-10-27.md) after the audit pin (`b13ccab` → `19b219f`, checked 2026-10-27). Its owner reports a multi-expert gravity/magnetic/topographic/hydrothermal investigation and a negative submission decision. We have not rerun its experiments. This is a substantial overlap in *ingredient families* with our top proposal; its distinctiveness as an operator and its surface/dot novelty against H79 must be proven, not assumed. The pinned historical winners and published audit were not silently refreshed. See the monitor for subsequently changing source heads.

## Additional band provenance check

The owner mirror labels band 15 “depth to basement”, while the competition
documentation describes a conductive-base-depth feature. Their equivalence and
physical units are not independently verified. See the separate
[independent source register](independent-sources.md) and
[geometry/format review](independent-review.md) for source-by-source links,
the sample-mirror discrepancy and writer-policy limitations.

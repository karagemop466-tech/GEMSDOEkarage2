# Source register and verification notes

Checked 2026-10-27 UTC. A source is authoritative only for the specific claim
beside it. The numerical feature TIFF, sample, labels, and other-team artifacts
used for this audit are **hash-pinned owner mirrors**, not independently
verified downloads from the organizer. Hash agreement proves the mirror's bytes,
not authorship, licensing or completeness. See `reference-sources.json` for
immutable GitHub refs, paths, Git blob IDs, sizes and SHA-256 values.

| Claim | Primary source | Scope / limitation |
| --- | --- | --- |
| Target: predict geological faults, not geothermal vents themselves; initial labels are newly identified expert-mapped faults. | [DrivenData problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | Actual expert test labels remain hidden. Geothermal applications motivate the task; a lineament is not a confirmed vent or fault. |
| DTI uses a 300 m triangular kernel, α=0.2 and β=0.8, with separate truth-side and prediction-side maxima. | [DrivenData metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric) | A catalogue holdout DTI is not a calibrated estimate of the hidden score. |
| Public and private scoring pools pixels; the final evaluation covers the whole area. | [DrivenData staff, post 2](https://community.drivendata.org/t/leaderboard-aggregation-pooled-over-public-test-pixels-or-mean-of-per-chunk-scores/11550/2) | No test chunk geometry is disclosed. |
| Existing-fault pixels are masked exactly, not with a surrounding 300 m buffer. Nearby new truth is possible and unmasked false predictions still cost. | [DrivenData staff, post 4](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4) | This changes the scientific holdout; it does not imply that nearby pixels are fault-positive. |
| Single-band float32, EPSG:32611, 100 m and matching bounds; null/NaN outside bounds, values in [0,1]. | [Submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format) | Outside-footprint NaN vs whole-array [0,1] checking is unresolved for the reported rejection; no successful portal test here. |
| The downloadable sample is described as predicting total fault absence. | [Submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format) | The pinned owner `example_submission.tif` instead has 60,988 positive pixels and equals the mirrored known-fault labels in the footprint. The reason is unknown; the mirror is not authenticated as the organizer's current sample. |
| Current public leaderboard is the authoritative source of public standings. | [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | A team-level leaderboard row does not bind a particular filename or SHA to a score. The standings change. |
| External data must be licensed for the challenge and shareable with the sponsor. | [Competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/) | Check the actual license and terms of every dataset used. |
| Publicly described airborne magnetic/radiometric data and variable survey clearance; products include GeoTIFF grids. | [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) | The USGS page identifies CC0. Magnetic and lithologic contrasts and survey artifacts are not proof of faulting. |
| INGENIOUS compilation includes geodetic, magnetotelluric, seismic, 2 m temperature, paleogeothermal and fault datasets. | [Geothermal Data Repository 1391](https://gdr.openei.org/submissions/1391) | Page lists CC BY 4.0. It displays download links, but this sandbox cannot directly fetch that host. Exact source files were not acquired in this session. |
| `deq_n100a15` and `ieq_n100a15` are INGENIOUS earthquake rate-density layers, not automatically distances to individual earthquakes. | [DrivenData staff](https://community.drivendata.org/t/units-and-very-large-values-in-deq-n100a15-and-meaning-of-ieq-n100a15/11557/2) | Consult the source dataset documentation for units; do not infer units from an owner mirror's band description. |
| Quaternary fault/fold data are geological interpretations, simplified for hazard mapping. | [USGS fault database](https://www.usgs.gov/programs/earthquake-hazards/faults) | A mapped-fault holdout is a biased proxy for expert-hidden new faults. |
| The competition website's own limit prevails over a parenthetical in the rules. | [DrivenData staff](https://community.drivendata.org/t/submission-amount-question/11553/2) | We cannot see the participant's current quota. |
| CPU execution is supported by the organizer's reference workflow. | [Reference solution README](https://github.com/drivendataorg/gems-prize-reference-solution) | A GPU can accelerate training; it is not categorically required. |
| The H33 artifact was initially recorded as unscored and the original manifest has no receipt. | [GEMSDOE32 original manifest](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/fcb6674b4589c71db66560e71201072adf687931/docs/downloads/submissions_manifest.json), [original commit](https://github.com/buffedlizard55-lab/GEMSDOE32/commit/fcb6674b4589c71db66560e71201072adf687931) | Owner evidence, not organizer evidence. This does **not** rule out a later submission; its claimed result is unverified without a receipt linking the exact file. |
| The lattice is in the shared priority registry, and is a retained calibration reference. | [GEMSDOE24 registry](https://github.com/buffedlizard55-lab/GEMSDOE24/blob/a73f9ffba29260cc7708e8e0557c84c5bea7d47b/registry/priority_rasters.json), [lattice TIFF](https://github.com/buffedlizard55-lab/GEMSDOE24/blob/a73f9ffba29260cc7708e8e0557c84c5bea7d47b/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif) | Other registries and active sessions may contain additional rasters. A single witness is enough to prove a failure, but passing it would not prove uniqueness globally. |

## Authenticated access and redistribution

The [competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
redirected the unauthenticated browser to login. The GitHub mirror made raw
research bytes obtainable within this sandbox, and their checksums matched the
other projects' pins; it did **not** authenticate them with DrivenData or grant
permission to redistribute them. Bulk inputs and model files are ignored by Git.
The participant's submission receipts, hidden labels and current quota were not
available. Do not request passwords or tokens in chat.

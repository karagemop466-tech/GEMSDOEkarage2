# Candidate research directions — preregistered before implementation

Recorded 2026-10-27 UTC after reading the competition problem statement and the
nine priority sites. This checkout initially contained no model code or data.
**These are proposals, not an assigned parallel-run lane, experiments, or
predicted scores.** Their ordering is a qualitative judgment about potential
holdout improvement, not a quantitative DTI projection. A later GitHub feed
change exposed related [GEMSDOE25 H79 prior art](https://github.com/buffedlizard55-lab/GEMSDOE25/blob/19b219f629440b9975b093f459c74e21a42476ca/docs/data/run_card_h79_cthm_2026-10-27.json);
proposal 1 requires a fresh differentiation review before it could be assigned. We did not establish
that every parallel repository has never tried a related idea. A broad registry
search and a named lane assignment are prerequisites to testing any one of them.

| Rank / cost | Layers and proposed physical signature | Why potentially off-catalogue; named non-fault mimic | Distinction and data availability |
| --- | --- | --- | --- |
| 1 · medium | **Signed cross-profile co-variation.** GeoDAWN reduced-to-pole magnetics (`rtp`), isostatic gravity anomaly (`iso_grav_anom`), and `cond_surf` from the competition feature stack. Steer paired profiles normal to independently detected local edges; use *relative flank-to-flank change and its cross-scale stability*, allowing either magnetic polarity and learning relationships only in the training folds. | A basement step can persist under basin fill where a surface fault trace is unobserved. Intrusive contacts and volcanic/lithologic boundaries can produce the same signatures; brine-filled basins can produce conductivity gradients. Null-test against other mapped geological contacts if those data become available. A basement boundary is not by itself proof of a fault. | This empty checkout has no implementation. It differs conceptually from magnitude-only edge concordance, but may overlap prior or concurrent work; full registry/lane check remains necessary. The feature layers are described by [DrivenData](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/); an owner mirror is listed in the [GEMSDOE32 pinned data manifest](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/73485f27cf230af770167397c2b72cb9ce3b3f25/registry/data_manifest.json). Its core bytes were subsequently restored and hash-verified in scratch storage; the mirror is not an authenticated organizer copy. |
| 2 · high | **Flow-adjusted paired hydrochemistry contrast.** INGENIOUS well and spring chemistry and temperatures, plus competition `cond_surf`, gravity and elevation; compare proximate wells with similar elevation and observed chemistry across a candidate field edge, with missingness and sampling effort recorded separately. | A hidden conduit might juxtapose fluids of different origin without a visible scarp. Cold groundwater mixing, sedimentary facies, pumping, and unequal well depths can mimic a cross-edge chemistry break. Absence of a warm spring must not be treated as absence of a geothermal system. | Differs from point-distance/thermal-anchor and dot-deletion priors in the [GEMSDOE32 hypothesis registry](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/73485f27cf230af770167397c2b72cb9ce3b3f25/registry/hypotheses.json): it tests paired chemistry contrasts. The official [GDR 1391](https://gdr.openei.org/submissions/1391) lists a public CC-BY 4.0 well/spring geodatabase and a download; its bytes and coverage were not verified in this sandbox. Not viable until retrieved, licensed, georeferenced, de-duplicated and tested for adequate within-block pairs. |
| 3 · high | **Cross-basin knickpoint synchronization.** USGS 3DEP elevation plus `iso_grav_anom`: compare normalized channel-profile breaks on opposite sides of a potential-field edge across multiple catchments, and test whether break alignments persist when downstream reference levels change. | A buried fault might create aligned drainage-profile breaks even where a scarp is degraded. Lithologic contacts, waterfalls, former lake levels, and drainage capture can do the same. A drainage break is not an independent fault label. | Unlike the topographic ridge/χ detector reported by [GEMSDOE36](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/), this is an across-catchment synchrony and reference-level sensitivity test. The [competition](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) lists 1 m DEM URLs for enrolled users; the required tiles and link table were not obtained here. Not currently viable. |
| 4 · medium | **Survey-aware gradient uncertainty.** Original GeoDAWN flight-line magnetic measurements and actual flight-height metadata, paired with interpolated `tmi_hg` and gravity. Bootstrap resampling by *whole flight line* to estimate edge location stability and discount edges that disappear when one line is omitted. | A structure beneath covered ground may appear as a repeatable field edge; instrument leveling, line-direction striping, flight-height variation and terrain clearance may mimic or displace one. | Unlike simply multiplying de-striped grid gradients, this proposes observational uncertainty from original flight lines. [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) lists downloadable flight-line CSVs and describes flight-height variation; actual bytes and area coverage were not obtained here. Not currently viable. |

## Scientific basis and limits

The official [USGS play-fairway report](https://www.usgs.gov/publications/discovering-blind-geothermal-systems-great-basin-region-integrated-geologic-and)
reports a blind Gabbs Valley geothermal system with gravity, magnetic,
resistivity, temperature and geothermometry evidence, but no surface hot
springs, fumaroles, or paleo-geothermal deposits. That case motivates
multi-physics tests; it does **not** validate any proposed raster or prove a
geothermal vent at an individual pixel. The target is **faults**, not direct
vent locations, according to the [competition problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).

## Preregistered test and stopping rule

Do not fit any hypothesis without an explicitly assigned single lane, the
actual cached shared feature stack, a complete pinned registry, the shared
`evaluate_holdout.py` and `submission_writer.py`, and a same-evaluator frozen
best. Recompute all catalogue-derived features using visible faults in each
buffered whole-segment spatial fold. Run a standalone, direction-invariant
leakage AUC for every feature before use, stopping on AUC > 0.90. Test both the
surface and emitted dots against every registry entry; either > 0.90 rank
correlation or > 70% within 3 pixels is a duplicate STOP. Never place dots just
to evade a calibration grid. Compare pooled DTI with a spatial-block paired
95% interval against the same-split best, not an unrelated site's score. Local
DTI is not a calibrated public/private score estimate. At most three experiments
or two hours; a weekly slot requires a separate selector and current quota.

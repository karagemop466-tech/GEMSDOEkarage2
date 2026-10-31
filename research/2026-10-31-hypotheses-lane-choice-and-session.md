# Session 2026-10-31 — ranked hypotheses, lane choice, results, and next lanes

Written to satisfy the standing instruction: *before implementing, generate 3–5 candidate
geological hypotheses we haven't tried, each naming the specific layers, the physical
signature, why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than
one already in it, how it differs from everything already implemented in this repo, ranked by
expected DTI improvement and implementation cost; validate the top candidate on the
spatially-blocked holdout before touching a weekly submission slot; name any new free
official data a hypothesis needs and check obtainability.* All layers below are bands of the
hash-pinned 19-band mirror (`gems-geodawn-numerical-features.tif`, sha256 `4371c82e…`); no
hypothesis required new external data, so none was blocked on access. Where a future
hypothesis WOULD need new data, the specific free official source is named with its status.

## Prior-lane inventory (what "new" must differ from)

Implemented previously in this repo: H1 (signed elevation/basement/conductivity gradient
parity), H2 (dilational stepover surface), K2 (HGB on raw gradient features), K3 (lineament-
context DTI), B4 (paired-flank scarp-step, retired), HK3 (edge-centrality graph on catalogue
apron), gw-nfs (apron reachability), H-A/HR4 (intersection propensity, retired), H-F
(alteration-curvature intersection, negative). Sibling sites additionally used openness/
thermal/population ridges (the champion family), Poisson off-catalogue emissions, submodular
selection, worm/persistence skeletons, and PINN-style predictors.

## Ranked candidates (preregistered before any EXP run)

| Rank | Hypothesis | Layers (band ids) | Physical signature | Why it should find *uncatalogued* faults | Difference from all implemented work | Expected value · cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Corroborated potential-field lineaments** (magnetic × gravity edges, orientation agreement, strike persistence) | `tmi_hg` (3), `tmi_vg` (9), `iso_grav_anom_hg` (18), `iso_grav_anom_vg` (11) | Structure-tensor lineament orientation + coherence per family; cross-family corroboration within ~30°; oriented closing bridges along-strike gaps ≤ 800 m | A buried strand that mappers missed still juxtaposes magnetic susceptibility AND density; two independent physical families agreeing on one orientation is much stronger evidence than either alone | No prior lane fused two potential-field families by orientation agreement; K2 used raw magnitudes in trees, H1 used no magnetics, HK3 was graph-centrality on the catalogue | Medium · medium → **tested as EXP-1 (K9): NEGATIVE on the instrument (0.0546 < random 0.0735); dots anti-located vs withheld strands; kept as research-only negative** |
| 2 | **Catalogue-corridor coverage** (uniform blue-noise in the fault-system corridor, off-apron) | `existing_faults.tif` geometry only (context, never scored pixels); no geophysical steering | Dense value-1.0 dot coverage of the 1 km damage-zone corridor around mapped systems, 200 m apron excluded | Unmapped strands cluster in mapped fault corridors (damage-zone branching, step overs, splays); the metric's algebra (β=0.8 punishes misses, FP costs 0.2/dot) rewards corridor coverage; the champion family's one measured leaderboard lever is exactly apron exclusion | No prior lane emitted *uniform corridor* coverage; gw-nfs reached along the apron (different), HK3 was graph centrality; this is a coverage design, not a detector | Medium-high (anchored by champion-class budget) · low → **tested as EXP-2 (K10): published candidate after gates** |
| 3 | **Strike-continuation emission** (extend visible traces along strike; tip/stepover analogs) | catalogue geometry + `det_elev` (12), `det_elev_slope` (19) for tip morphology | Per-trace smoothed strike direction; dots along the continuation ray beyond mapped tips and across ≤ 1 km step overs | Mapped traces end where exposure/access ends, not where the fault ends; continuation catches segments the catalogue literally stops short of | h33d (sibling site) did analog tip/stepover dots; this repo never implemented continuation; overlaps gw-nfs's negative result family — medium collision risk | Medium · medium — **NOT run: budget exhausted by EXP-1/2; highest-priority next lane** |
| 4 | **Conductivity-saddle across gravity break** | `cond_surf` (17), `iso_grav_anom` (13), `iso_grav_anom_hg` (18) | Cross-profile sign change of the conductivity Hessian aligned across a gravity-gradient boundary | A buried fluid conduit under cover can juxtapose conductive strata across a density contrast without any surface trace | H1 required conductivity *contrast* only; K2 used raw conductivity; nobody tested a *saddle sign-change* keyed to an independent gravity break | Low-medium · medium — not run |
| 5 | **Seismicity-sidedness prior** | `deq_n100a15` (10), `ieq_n100a15` (16), `iso_grav_anom_vg` (11) | Aggregate event-density asymmetry across a gravity edge (contextual prior only) | An active unmapped fault can seed clustered seismicity offset from the mapped trace | No local model used earthquake bands; sibling sites may have (collision risk in registry) | Low · low-medium — not run |

## New-data check (rule: name the source before calling a hypothesis viable)

None of the five requires new external data. For future lanes that would: USGS GeoDAWN
flight-line magnetics/radiometrics and 1 m DEM tiles are free and official
([USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and),
[EGD](https://doi.org/10.5066/P1BT8PSC)); **not obtainable from this sandbox** (egms/USGS
hosts unreachable; only GitHub/PyPI allowed) — viable only on an unrestricted machine.

## What the session actually measured (instrument forensics)

1. EXP-1 (candidate 1): pooled HOLDOUT-DTI 0.0546 [0.0480, 0.0611] vs random38k 0.0735
   [0.0705, 0.0766] — paired Δ −0.0189 [−0.0256, −0.0124]: NEGATIVE. Its NMS dot placement
   covers LESS withheld truth than random (final dots 0.0074): the corroboration top is
   anti-located vs catalogue strands in this dataset.
2. EXP-2a (candidate 2 at r=3 km): zone = 52% of the footprint; per-fold visible-context
   zones starve the 38k budget (2.7k–6k dots): NEGATIVE (0.0061 full-context arm).
3. **Instrument limitation, decisive:** the 0.2778-reported GEMSDOE32 champion scores
   **0.00665** [0.0060, 0.0075] on the same folds — 11× below random — and only 3.4% of
   fold-0 withheld truth lies within 3 km of visible context. Whole-component withholding
   detaches fault systems; the instrument therefore cannot rank leaderboard-class corridor
   emissions, and its "beat the holdout best" bar was recorded as non-informative rather
   than applied.
4. EXP-2b (candidate 2 at r=1 km, off-apron): published after format + uniqueness gates;
   HOLDOUT-DTI 0.0172 [0.0163, 0.0180], above the champion control, below random — reported,
   disclosed, not obeyed (see `evidence/k10/run_card.json`).

## Next-lane recommendation

Candidate 3 (strike continuation) at a corridor-weighted budget, evaluated with a *repaired*
instrument (withhold strands but keep their systems' context visible, e.g. withhold only
segments whose 1-km neighbourhood context remains — measuring recovery, not detachment),
plus a champion-family reconstruction as the first legitimate same-fold incumbent.

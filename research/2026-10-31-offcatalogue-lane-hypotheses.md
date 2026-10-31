# Off-catalogue lane: five candidate hypotheses, ranked before implementation

Written **before** the lane was built, as the project protocol requires.
Competition: DOE GEMS Prize, DrivenData #306 —
[problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) ·
[rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) ·
[reference solution](https://github.com/drivendataorg/gems-prize-reference-solution).

## The constraint every hypothesis must respect

Verified in this session from the pinned bytes (`docs/data/nine-site-scorecard.json`,
`docs/data/mask-width-calibration.json`):

* `labels.tif` and `existing_faults.tif` are **byte-identical** (sha256 `7ba308cc…`), 60,988 positive
  pixels at 100 m.
* The organiser states the test truth is expert-identified faults **absent** from that compilation,
  and that mapped-fault pixels are **masked out of the scored domain**.
* Across all nine focus best-files, a 4-quadrant hide-and-recover score against the public catalogue
  is **Spearman −1.00** against the reported leaderboard, at every exclusion width from 0 to 8 px.
  Rediscovering known faults is *anti*-informative here.

Any hypothesis whose validation signal is "does it rediscover the public catalogue" is therefore
**not testable** with the data available, and must say so up front.

---

## H1 — Off-catalogue geophysical prospectivity (SELECTED)

* **Layers.** All 19 official GeoDAWN bands, plus gradient magnitudes at 100 m and 400 m scales for
  reduced-to-pole magnetics, isostatic gravity, detrended elevation and TMI; gradients of
  depth-to-basement, surface conductivity, geodetic second invariant and magnetic anomaly; Laplacian
  ridge filters on elevation and magnetics; 5 × 5 local standard deviations. 34 features, none
  catalogue-derived.
* **Physical signature.** Potential-field and topographic *lineaments*: edges and ridges in the
  magnetic and gravity fields mark buried basement offsets, lithologic contacts and basin-bounding
  structures; basement-depth steps mark buried range fronts; strain-rate and seismicity gradients
  mark actively deforming zones. A fault that is missing from the map still produces these
  signatures — that is precisely why an expert can map it from the same data.
* **Why it should catch an *unmapped* fault rather than a mapped one.** The model is trained to
  recognise mapped faults and then emitted only where the catalogue says "nothing mapped". The
  highest-scoring off-catalogue pixels are the structures that look exactly like mapped faults but
  are not on the list — the definition of a mapping omission.
* **Mimic.** Lithologic contacts, igneous margins and basin-bounding stratigraphic edges produce
  the same gravity/magnetic gradients as faults. Without seismic or field control they are
  indistinguishable at 100 m. This is the named non-fault process that could mimic the signal.
* **Difference from prior work in this repo.** Every prior lane here (HK3, K2, K3, H1, H2, B4,
  gw-nfs, H-A) derived from the shared warehouse lattice or from catalogue-geometry features, and all
  were stopped by the degenerate lattice gate. This lane builds an **independent dot pool** from a
  model that never reads another submission. It also explicitly disqualifies space-filling
  references from the one-sided uniqueness gate (IR-LATTICE-01).
* **Expected DTI improvement.** Unknown and **not locally measurable** — see the estimate section of
  the release desk. Central projection ≈ 0.15; the break-even per-dot credit is 0.0871 versus the
  0.1394 the 0.2778 file achieves, so the bar is 62 % of the incumbent's quality.
* **Cost.** Low. One gradient-boosted model, ~8 min on 2 CPU / 3 GB. **No new external data.**

## H2 — Catalogue-apron widening as a pure metric-arithmetic lever

* **Layers.** None — this is an emission-policy hypothesis, not a feature hypothesis.
* **Mechanism.** `DTI = T / (0.2T + 0.2(n − M) + 0.8K)`. A dot that earns no kernel credit still costs
  0.2. Dots inside the organiser's masked zone earn nothing by construction. Two verified subset
  contrasts (`32 ⊂ 31 ⊂ 25`) show the zero-credit zone reaches at least 200 m; the natural design
  choice is the kernel radius, 300 m.
* **Why it is not merely copying.** The *policy* is known, but the correct width is not. This session
  measured the cost of each width (holdout credit falls only 3.2 % from a 200 m apron to a 2 km
  apron) and chose 500 m as insurance rather than assuming 200 m.
* **Mimic / risk.** If the mask is narrower than the apron, real credit is discarded. Measured cost
  at 500 m: 0.7 % of holdout credit. Small.
* **Expected improvement.** +0.006 to +0.017 DTI over a 200 m apron, depending on the true mask.
* **Cost.** Nil. **Adopted as part of H1's emission policy.**

## H3 — Emission-mass re-optimisation under the marginal-acceptance rule

* **Mechanism.** A new dot raises DTI iff `k > α·DTI`, i.e. iff its expected kernel credit exceeds
  0.056 at DTI ≈ 0.28. Because this model ranks the *whole* grid rather than a fixed pool, the
  optimal budget is far larger than the family's 37,654.
* **Measurement.** The holdout credit-by-rank curve falls only from 0.147 (top ventile) to 0.043
  (rank 400,000), so the marginal bar is not reached until ~300,000 dots; the projection peaks at
  100,000 once the denominator is included.
* **Expected improvement.** 0.1944 → 0.2167 (λ = 1.0) going from 37,654 to 100,000 dots.
* **Cost.** Nil. **Adopted.**

## H4 — Independent fault inventories as an off-catalogue truth surrogate

* **Layers.** USGS SGMC faults, the INGENIOUS compilation
  ([GBCGE](https://gbcge.org/current-projects/ingenious/) · [GDR 1391](https://gdr.openei.org/submissions/1391),
  CC BY 4.0), Nevada Bureau of Mines and Geology mapping, USGS Quaternary fault database.
* **Mechanism.** Faults present in another *public* compilation but absent from `existing_faults.tif`
  are a candidate proxy for "expert-identified but unmapped" — giving a real, off-catalogue truth set
  to validate against.
* **Why it was NOT selected.** A submission built on exactly this idea already exists in the family
  (GEMSDOE29, `sgmc-off-catalogue-44k`) and scored **0.0512** — i.e. the hidden truth is largely *not*
  captured by other public catalogues. The premise is empirically weak.
* **Data availability.** All sources are free and official, and are linked above. The blocker is
  relevance, not access.

## H5 — Independent topographic scarp detection from 1 m / 10 m LiDAR

* **Layers.** USGS 3DEP 1 m and 10 m DEMs ([3DEP](https://www.usgs.gov/3d-elevation-program)),
  mosaicked and resampled to the 100 m competition grid; scarp descriptors (max/mean curvature,
  step, down-face, relief, aspect coherence).
* **Physical signature.** A young fault scarp is a sub-metre to few-metre break in slope that survives
  in 1 m LiDAR long after it is invisible in the 100 m geophysics. This is the highest-resolution
  fault evidence freely available for the area.
* **Why it should find unmapped faults.** Scarps are routinely missed in compilations built from
  airphotos and coarse topography; a systematic 1 m scarp detector finds them directly.
* **Mimic.** Fluvial terraces, alluvial-fan edges, landslide scarps, road and canal cuts — all
  produce the same slope break.
* **Why it was NOT selected.** It needs ~700 3DEP tiles mosaicked before a single number can be
  computed. That is a multi-hour data-engineering task, not a within-budget experiment, and the
  protocol caps this lane at three experiments / two hours. **Named for the next lane.**
* **Data availability.** Free and official (USGS 3DEP); obtainable, but not within this budget.

---

## Budget and outcome

| Slot | Hypothesis | Result |
|---|---|---|
| E1 | H1 + H2: GBM prospectivity, apron sweep {2, 3, 5} px | selected apron 5 px |
| E2 | H3: emission-budget sweep {37.6k … 200k} dots | selected 100,000 |
| E3 | H2 extended: apron {8, 12, 20} px | rejected — no gain beyond 5 px |

Holdout result for the selected lane: **0.063687** off-catalogue hide-and-recover DTI at n = 37,656,
versus **0.006697** for the 0.2778 file and **0.029599** for a uniform-random control at the same
budget and the same apron — 2.15 × random, where the incumbent is 0.23 × random. See
`evidence/lane-gbm/run_card.json`.

**Caveat that governs everything above.** The catalogue holdout is Spearman −1.00 against the
reported leaderboard across the focus family. It is used here *only* for matched-policy model
comparison (same budget, same apron, same evaluator), never as a leaderboard projection.

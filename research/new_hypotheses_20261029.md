# New candidate geological hypotheses (2026-10-29)

These five hypotheses are **untried** in this repo and distinct from the nine focus-site
dotted-ridge approaches and from the H1-H4 / GW-NFS proposals already recorded.
They are qualitative rankings of *possible* holdout value versus implementation cost,
NOT score projections or leaderboard estimates.

## Rank 1 · Medium cost · Radiometric-thorium alteration halo with profile curvature

- **Layers:** radiometric eTh (band family in the GeoDAWN/19-band stack), DEM profile
  curvature (second derivative of band 12 detrended elevation)
- **Physical signature:** hydrothermal alteration produces potassium/thorium enrichment
  in a halo around concealed faults; profile curvature isolates linear, fault-parallel
  curvature breaks that persist under alluvial cover
- **Why it catches catalogue-missing faults:** alteration halos and subtle curvature
  breaks can extend beyond mapped USGS/INGENIOUS traces; the method does not use
  catalogue faults as placement predictors
- **Named non-fault mimic:** lithologic contact, alluvial fan toe, irrigation-induced
  moisture contrast; control: same operator on radiometrically flat blocks
- **Differs from repo work:** no existing hypothesis combines radiometric eTh with
  second-derivative curvature; H1 uses first-order gradients only, K2 uses magnitude
  features, GW-NFS uses conductivity-gravity saddle only
- **Data access:** bands exist in the pinned 19-band owner mirror; no new external
  file required; band unit/physical meaning must be authenticated before placement

## Rank 2 · Medium cost · Magnetic horizontal gradient edge with terrain-curvature filter

- **Layers:** RTP magnetic (band 2 rtp), horizontal gradient magnitude, DEM plan
  curvature
- **Physical signature:** a concealed fault juxtaposes contrasting magnetic lithologies;
  the horizontal gradient isolates edge location; plan curvature filters out
  non-linear (broad dome/basin) responses
- **Why it catches catalogue-missing faults:** blind faults under cover have no surface
  trace but preserve subsurface magnetic contrast; the gradient finds the edge without
  requiring a mapped scarp
- **Named non-fault mimic:** intrusive contact, lithologic boundary, flight-line
  artifact; control: gradient edges that follow contour lines (terrain-aligned null)
- **Differs from repo work:** H2 proposes shear-offset edge dipoles using *cross-strike
  parity* between gravity and magnetics; this uses a single-field horizontal gradient
  with a curvature null — a different operator
- **Data access:** bands 2 and 12 exist in the pinned mirror; no new external file

## Rank 3 · Medium-high cost · Seismicity cluster density on gravity residual edges

- **Layers:** seismicity band (deq_n100a15 or ieq_n100a15), isostatic gravity residual
  (band 13 minus blockwise robust fit), depth-to-base (band 15, only after unit
  authentication)
- **Physical signature:** an active but unmapped fault generates local earthquake
  clustering; gravity residual marks subsurface density contrast; their spatial
  intersection targets active concealed strands
- **Why it catches catalogue-missing faults:** seismicity can reveal active faulting
  that surface mapping missed; gravity residual constrains location to subsurface
  density boundaries
- **Named non-fault mimic:** production/mining-induced seismicity, smoothed-density
  interpolation artifacts; control: seismicity-shuffled negative control
- **Differs from repo work:** K2 excluded strain and seismicity bands; H1 used
  elevation/depth/conductivity only; no existing proposal combines seismicity density
  with gravity residuals
- **Data access:** seismicity and gravity bands exist in the mirror; band units/meaning
  unverified; exclude band 15 until authenticated

## Rank 4 · Low cost · Structural intersection / relay zone density

- **Layers:** known-fault line density (from existing_faults mask only, visible faults
  per fold), distance to nearest fault intersection, line orientation variance
- **Physical signature:** relay zones and stepovers between mapped fault segments are
  high-strain zones where concealed splays and blind strands are likely; density of
  intersections captures this without placing dots on catalogue traces
- **Why it catches catalogue-missing faults:** intersections of mapped segments are
  natural places for unmapped cross faults and relay ramps; dots are placed near
  intersections but not on traces themselves
- **Named non-fault mimic:** mapper bias (more intersections where mapping is denser),
  erosion-concentrated drainage; control: randomized fault-segment permutation
- **Differs from repo work:** all nine focus submissions place dots *on/near catalogue
  faults*; this places dots near *intersections* of segments, offset from traces;
  GW-NFS uses geophysics-weighted annuli only
- **Data access:** existing_faults mask from pinned mirror; no new external file

## Rank 5 · Low cost, low expected benefit · Conductivity-depth ratio with basin-edge mask

- **Layers:** surface conductivity (band 17), depth-to-base (band 15, after unit
  authentication), DEM slope
- **Physical signature:** a high conductivity-to-depth ratio near basin edges may mark
  a concealed fault-controlled conduit; basin-edge mask excludes interior alluvial
  false positives
- **Why it catches catalogue-missing faults:** geothermal systems localize at basin
  margins where faults juxtapose permeable and impermeable units
- **Named non-fault mimic:** saline groundwater, clay-rich lacustrine sediments,
  interpolation seam in EM inversion; control: ratio computed on shuffled depth field
- **Differs from repo work:** H1 uses conductivity contrast only; this adds the
  depth-to-base ratio and basin-edge masking
- **Data access:** band 15's owner description ("depth to basement") conflicts with
  official wording ("conductive-base depth"); exclude until verified

## Required experiment protocol (if blockers resolve)

Use the unchanged shared template `evaluate_holdout.py` / `submission_writer.py` with
the actual cached feature stack. Preregister the assigned operator and feature names.
Withhold whole fault segments in buffered geographic blocks; construct every
label-derived feature from visible faults in that fold; mask visible faults
pixel-exactly; assess each feature alone against held-out labels (AUC > 0.90 is a
leakage stop). Check the unmodified candidate surface against every registered raster
before placement, and the saved dots afterwards. Use pooled distance-weighted Tversky
(alpha 0.2, beta 0.8, 300 m triangular kernel), with withheld-positive counts, a
spatial-block confidence interval, and paired comparison to the current best under the
same protocol. A negative result is retained; no weekly slot is used unless the
separate selector authorizes it. No part of this plan is an observed DTI or evidence
that the hidden leaderboard will improve.

## Access status

The pinned owner-mirror feature TIFF (19 bands) and sample/labels are restored and
hash-verified in `.cache/`. They do **not** authenticate DrivenData's current files.
No competition slot was used in this session. No experiment was run here.
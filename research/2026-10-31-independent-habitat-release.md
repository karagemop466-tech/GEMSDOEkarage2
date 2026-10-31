# 2026-10-31 — independent structural-habitat release

**Question.** Generate a unique TIF this project can defend, and say plainly whether it
is OK to download and submit and what it will score.

**Answer.** `docs/downloads/gemsdoekarage2-geo-habitat-dti-20261031.tif`, 40,561 dots,
sha256 `ff22311c…d0402f`. Unique (23.3% max within 3 px, Jaccard 0.0057) and format-valid.
HOLDOUT-DTI 0.0172 [0.0130, 0.0227]. Forward projection 0.007–0.013.
**Safe to submit; not forecast to beat 0.2778.**

## What was built

A closed-form geophysical index over four of the 19 GeoDAWN bands:

    comp = z(log1p det_elev_slope) + z(log1p tmi_hg) − z(tc) + 0.5·z(|iso_grav_anom_hg|)

rank-transformed to a within-footprint quantile, discounted by `(1 − exp(−d_cat/3 px))`,
zeroed within 100 m of a mapped fault, then emitted by lazy-greedy (CELF) maximisation of
expected DTI at K̂ = 35,000. No model is trained and **no published raster is an input**.

Code: `src/gemsdoe/habitat.py`, `scripts/run_lane.py --stage final --habitat geo`,
`scripts/validate_habitat.py`, `scripts/project_score_range.py`, `scripts/estimate_score.py`.

## Why this index and not the supervised model

The supervised lane (`--habitat model`, a hide-and-recover GBM) learns to predict *mapped*
faults. The scored label set is *unmapped* faults. Measured on 21 byte-verified published
rasters, the GBM score correlates only ρ = +0.05 with the fitted hidden-truth density while
the geological index reaches ρ = +0.26. At 10 km block scale the best-scoring published
file correlates with detrended-elevation slope (+0.46), detrended elevation (+0.37) and
TMI horizontal gradient (+0.36), anti-correlating with tilt (−0.18) — so the winning
habitat is relief plus magnetic contact, which the supervised model under-weights.

## The central finding, and why it caps the score

Fitting `ρ = K·w/Σw`, `w = smooth(union of the 8 best published rasters)^γ`, reproduces all
21 USER-REPORTED scores to RMSE 0.029–0.037. Every smooth geophysical parameterisation we
tried (catalogue buffer; `K·s^η·(1−e^{−d/λ})`; 5-basis log-linear) gave RMSE 0.139–0.193 or
collapsed to uniform. The reading is that the expert label set has absorbed the territory
the community already dotted.

The consequence is a measured tension. Adding the published territory to our density
(`α > 0` in `scripts/scan_emission.py`) raises the projection from ~0.013 to 0.09–0.15 —
and simultaneously puts **99% of our dots within 3 px of a published raster**, far past the
70% duplicate stop. With `α = 0` the blend is inadmissible and the projection is 0.007–0.013.
Because the credit kernel is R = 3 px, only dots inside the winners' ±3 px halo are paid, so
under this model "unique" and "high-scoring" are close to mutually exclusive.

**This is a property of the estimator, not a proof.** γ = 4 was the sharpest value searched
and the RMSE surface is nearly flat (0.029–0.037 across γ ∈ [0.25, 4]), so the projection is
reported as a range and labelled PROJECTION throughout.

## Rejected / dead ends (do not retry)

- Smooth geophysical ρ fitted to the 21 scores — 4 parameterisations, all RMSE ≥ 0.139.
- `scripts/fit_truth.py` (9- and 5-basis log-linear ρ) — deleted this session; θ ≈ 0 and K
  unstable across starts.
- Using the fitted anchor as an emission target — duplicate stop, measured above.
- Full-grid float32 stacks, `grid.read_features()` on all 19 bands — OOM on 3 GB / no swap.
  Read one band at a time (`habitat.geological_index_from_path`).

## Validation evidence

- `evidence/habitat-holdout-2026-10-31.json` — 16 interleaved 4×4 folds, 11 qualified
  (5 held fewer than 5 isolated withheld positives), 60,661 withheld isolated positives,
  scored with the vendored official `dti_weighted_terms`.
- `evidence/projection-range-2026-10-31.json` — γ sweep with refitted K, per-γ predictions.
- `evidence/run-card-gemsdoekarage2-geo-habitat-dti-20261031.json` — run card with the
  measured uniqueness table against all 21 pinned rasters.

## Labelling discipline

HOLDOUT-DTI is measured and carries its evaluator version, withheld-positive count and CI.
The forward number is labelled PROJECTION everywhere. The 0.2778 / 0.2750 / … nine-site
values are USER-REPORTED / UNVERIFIED. Nothing on this page is ORGANIZER-CONFIRMED.

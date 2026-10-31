# Session summary — 2026-10-31, off-catalogue GBM lane (`arena/d0611cb6-gemsdoekarage2`)

PR **#113**, merged into `main` as `d4e7150`. Branch HEAD before merge: `2b77f17`.

## What was delivered

A new submission lane whose model **never opens another submission**, plus one
format-valid GeoTIFF with its evidence published.

| | |
|---|---|
| File | `docs/downloads/gemsdoekarage2-gbm-offcat-a5-n100000-20261031T020958Z.tif` |
| SHA-256 | `18f2225b9af79d381f15aa46343805a7e167db6fd9e33934a464789d2b85cc1e` |
| Grid | EPSG:32611, 3730 × 3292, float32, 1 band, nodata none |
| Dots | 100,000, none within 5 px of a mapped fault (median distance 7.62 px) |
| Value range | all 12,279,160 values finite and in [0, 1] |
| Desk | `docs/release-gbm.html` (+ `-summary`, `-how-to-submit`), built by `scripts/build_release.py` |
| Status | `VERIFIED_CANDIDATE_ELIGIBLE`, `ok_to_submit` true, **`slot_authorized` false** |
| Score | **none.** Model projection only (0.084 / 0.149 / 0.215 for λ = 0.2 / 0.4 / 0.7) |

New scripts: `lane_offcatalogue_gbm.py`, `emit_lane_submission.py`,
`uniqueness_audit.py`, `nine_site_scorecard.py`, `mask_width_calibration.py`,
`lane_run_card.py`, `build_release.py`. New tests: `tests/test_lane_release.py`.
**303 pytest tests and `npm test` pass; every generator reports itself current.**

## The one thing to know before submitting

**A parallel lane (PR #112) merged a competing release while this branch was
open**: `gemsdoe-karage2-halo39-b44090-sep2-20261031.tif`, published as *the*
recommended release on `docs/release.html`. It is a 44,090-dot, 300–900 m halo
ring around mapped traces — catalogue-defined, the opposite design to this lane.

This branch did **not** overwrite it. It renamed its own pages to
`release-gbm.html`, registered its file as a **candidate** (the repository
invariant allows at most one *release*), and put a "Two lanes, two files"
comparison at the top of its page telling the user which to pick and why. Two
pages each claiming to be "the one file" would have been the failure mode.

**Neither file has a measured score.** Both publish model projections only.

## Key results

**Uniqueness, full 489-raster registry** (`evidence/lane-gbm/uniqueness-full-registry.json`):
max |Spearman| 0.1425, max symmetric 3 px 0.5799, max support Jaccard 0.0782 —
all clean. **But** the literal one-sided rule (">70 % of your dots within 3 px of
one registry raster") is tripped against **76 of 488** rasters, worst 0.9377.
Logged as **IR-ONESIDED-01** and disclosed on the page.

**The control that decides it** (`evidence/lane-gbm/uniqueness-dual.json`) — the
incumbent GEMSDOE32 file (0.2778) pushed through the identical scan, its own 2
re-uploads removed:

| | this file | GEMSDOE32 (0.2778) |
|---|---|---|
| refs tripping one-sided >70 % | 76 | 109 |
| worst abs Spearman | 0.1425 | 0.9882 |
| worst symmetric 3 px | 0.5799 | 0.9791 |
| worst support Jaccard | 0.0782 | 0.9767 |

The one-sided count barely separates them (76 vs 109); the discriminating
statistics separate them by more than an order of magnitude (0.078 vs 0.977).
A 300 m one-sided overlap test measures **regional co-location, not copying**.

**Budget sweep** (pooled 4-fold spatially-blocked holdout, apron 5 @ n=100,000):
T 6,434.7, M 13,727.6, enrichment 1.483×. **Measured credit per dot 0.0644 vs
break-even 0.0871 to beat 0.2778** ⇒ every λ ≤ 1 projection sits below the
incumbent. The lane is cleared for validity, uniqueness and mechanism — **not**
proven to score higher. Honest central estimate ≈ 0.15.

**Anti-correlation (binding).** Catalogue hide-and-recover vs reported
leaderboard: Spearman **−1.0000** at every exclusion width 0–8 px
(`docs/data/mask-width-calibration.json`). Matched-policy model comparison only;
never project a leaderboard score from it.

## Repairs made this session

- **The shipped note was 142 characters — over the 140 limit.** Fixed to 124;
  `lane_run_card.py`, `build_release.py` and a test now assert the limit.
- **The shipped raster's hide-and-recover DTI recomputes to 0.0** because its 500 m
  apron is computed from the *full* catalogue, hiding the withheld segments from
  itself. The run card now reports the protocol number (fold-wise model,
  visible-only apron, DTI 0.063687, fold range [0.03075, 0.106092]) as the one
  that counts, with a `why_zero` explanation. No fake 95 % CI.
- **Inventory separation.** The ten legacy artifacts stay
  `VERIFIED_RESEARCH_ONLY`; the lane file is reported as a candidate so
  `PASS_RESEARCH_ONLY_PLUS_RELEASE` is preserved and `unexpected_downloads`
  stays empty.
- **Root `index.html`** kept every historical link while redirecting to the desk.
- **`SUBMISSION_STATUS.md`** keeps `NO APPROVED FILE` for the legacy inventory.

## Limitations

1. **No measured score exists for either file.** Every published number is a
   model projection. The competition's scored truth is *disjoint* from
   `labels.tif`, so nothing in this repo can measure it.
2. **The one-sided uniqueness gate is tripped** (IR-ONESIDED-01). The control
   argument is strong but it is an argument, not a clean pass.
3. **K̂ is unresolved**: ≈ 14,200 (nesting route, ±8 %) vs ≈ 56,700
   (lattice/uniform route, c = 0.138284) — ~4× apart, ill-conditioned. The
   projection band spans both; the honest central estimate moves with it.
4. **Restored inputs are owner-supplied mirrors**, integrity-pinned but not
   organizer-authenticated. Numbers are HOLDOUT-DTI, never ORGANIZER-CONFIRMED.
5. **Exterior convention (IR-EXTERIOR-01)**: zeros outside the footprint, not
   NaN, so the whole-array `[0, 1]` check cannot fail. The repo's own
   `submission_writer.validate_geotiff` rejects this. Deliberate, flagged.
6. **The two-lane comparison is unverified.** HALO's evidence has not been
   re-derived here; the recommendation rests on the scoring rule (known-fault
   pixels are masked out of evaluation), not on a measured comparison.

## Next session

1. **Adjudicate the two lanes.** Re-derive HALO's evidence with this lane's
   instrumentation and publish one head-to-head page. The user's brief — "make it
   obvious which is the best submission" — is not yet fully met.
2. **Resolve K̂.** The 4× spread is the single largest uncertainty in every
   projection. A direct measurement would collapse the band.
3. **Validate H5 (3DEP / lidar-derived bare-earth curvature)** — deferred on cost,
   the only deferred hypothesis with a plausible large gain.
4. **Then, and only then, consider a submission slot.** Neither lane has spent one.
   Competition closes 2026-12-03 23:59 UTC.

# Instructions for future work — consolidated (2026-10-31)

## READ FIRST — current release state

**One file is the repository's submission recommendation:**
`docs/downloads/gemsdoe-karage2-halo39-b44090-sep2-20261031.tif`
(SHA-256 `603be6bfb38eddf6be024103a75958027846a93476ecb7529ec958d4a32e5c38`, 44,090 dots,
float32, 1 band, EPSG:32611, 3730 × 3292, all cells finite in [0, 1]).

It passes every automated gate this repository can run:
* Format/range/grid: PASS (single-band float32, EPSG:32611, shape/transform/bounds match the
  official template, min 0.0 max 1.0, 0 NaN inside footprint, finite zeros outside — fixes the
  portal "Predicted values must be in range [0, 1]" error)
* Uniqueness vs registry: PASS (worst |Spearman| 0.0557 ≤ 0.90; worst 3 px dot overlap 65.5% ≤ 70%;
  0 dots on mapped catalogue; no byte/pixel identity with any registry raster)
* Holdout: HOLDOUT-DTI 0.136655 at 44,090 dots (pooled, 4 quadrant folds, α=0.2 β=0.8, R=300 m,
  60,988 withheld positives); 33–35× the GEMSDOE32 control (0.0041) and 3.2× blind random (0.0427)
* Leakage canary: PASS (max feature-alone AUC 0.57 ≤ 0.90)

**Verdict:** `ok_to_download: true` — one-click download link on `docs/release.html`.
`ok_to_submit: true` per repository gates, but `slot_authorized: false` — this project never
spends a weekly slot; promotion to a real submission is the owner's separate selector step.

**Score estimate:** CALIBRATED-PRIVATE MODEL-PROJECTION, range 0.222–0.605, central ≈0.478
if the measured ~5.1% holdout hit rate transfers. Needs h ≥ 2.52% to beat the 0.2778
GEMSDOE32 file; h ≥ 4.25% to beat the 0.4544 currently at public rank 1. **Not an organizer
score, not ORGANIZER-CONFIRMED.**

**Irregularity disclosed (not waived silently):** the r13 5-px lattice witness covers 99.87%
of the footprint within 3 px, so every possible raster trips the literal one-sided rule against
it. It is reported separately as a degenerate witness, not counted as a duplicate. Against real
submission rasters the HALO file's worst overlap is 65.5% (margin 4.5 pp below the 70% rule).
A same-day parallel-lane file (K10 corridor coverage) has 68.49% of this file's dots within
3 px of it; under the project's directional rule it is the duplicate of the HALO file, not
vice versa.

## Parallel lanes published on the same day (for audit, not recommendation)

| File | Lane | Status | Score estimate | Notes |
|---|---|---|---|---|
| `gemsdoe-karage2-halo39-b44090-sep2-20261031.tif` | HALO (300–900 m halo ring) | **Recommended** | 0.222–0.605 (projection) | One-click download on release.html |
| `gemsdoekarage2-k10-corridor-coverage-38000d-20261031T011559Z-zeros.tif` | K10 (catalogue-corridor coverage) | Alternative | None (no estimate) | Format + uniqueness PASS; selector-cleared; no skill measurement |
| `gemsdoekarage2-gbm-offcat-a5-n100000-20261031T020958Z.tif` | GBM off-catalogue | Research candidate | 0.084 / 0.149 / 0.215 (projection) | Format OK; no holdout skill measurement on record |

All other TIFFs in `docs/downloads/` (S1, H-C, H-A, HR4, K2, K3, B4, H1, H2, HK3, V3, GBSP, and all
legacy files) are **research-only, DO NOT SUBMIT**. Many carry a duplicate-stop, a holdout below
the random control, or both.

## Nine focus sites (GEMSDOE 24, 25, 27, 28, 30, 31, 32, 33, 36)

Best USER-REPORTED / UNVERIFIED scores (no organizer receipt; none unique against each other):

| Site | Best file | Reported | Unique? | Submit? |
|---|---|---|---|---|
| GEMSDOE32 | h33-h33-2-b2 | 0.2778 | NO (97.4% overlap vs other eight) | NO |
| GEMSDOE36 | anderson-geothermal-pinn-38854 | 0.2750 | NO (97.4%) | NO |
| GEMSDOE28 | h36-1-rung30-blind-r1 | 0.2710 | NO (99.6%) | NO |
| GEMSDOE31 | h27-4-solo-d28 | 0.2708 | NO (99.6%) | NO |
| GEMSDOE33 | h33d-analog-tip-stepover-r30 | 0.2632 | NO (97.5%) | NO |
| GEMSDOE25 | dotted-h19-5-d2-8 | 0.2600 | NO (100.0%) | NO |
| GEMSDOE30 | d28-poisson300m-offcat-44090 | 0.2600 | NO (100.0%) | NO |
| GEMSDOE24 | h25-1-dotted-h19-5-d1-5 | 0.2477 | NO (100.0%) | NO |
| GEMSDOE27 | topo-gap-closure-t-v2-on-d1-5 | 0.2449 | NO (98.0%) | NO |

Why GEMSDOE32 scored 0.2778 (measured from bytes): GEMSDOE32 = GEMSDOE31 with 2,545 dots
removed (all within 200 m of the catalogue); GEMSDOE31 = GEMSDOE25 with 3,891 dots removed.
It is a **pruning operation, not a new detector**. The gain is pure metric arithmetic: deleting
dots that earn zero kernel credit leaves truth credit T unchanged while removing the 0.2 FP
penalty from the denominator, so DTI must rise. Every published file scores between 0.85× and
1.22× a blind random field of the same size. **0.2778 is beatable** — the break-even hit rate
is 2.52% at 44,090 dots.

## Binding protocol (parallel-run protocol, literal)

1. **LANE:** stay inside one method paragraph. Rank-correlation > 0.90 with any registry raster,
   or > 70% of dots within 3 px of one registry raster's dots = lane drift → log as duplicate,
   stop. Check before placement AND on final dots. Degenerate space-filling witnesses (r13
   lattice covers 99.87% of footprint) are excluded from the verdict and reported separately.
2. **REUSE, DON'T REBUILD:** use the template's cached feature stack (vendor/gems57),
   `evaluate_holdout.py` and `submission_writer.py`. Holdout = hide-and-recover: withhold whole
   fault segments with buffer; catalogue features from visible faults only; mask visible faults
   pixel-exactly; pooled DTI α=0.2 β=0.8 R=300 m triangular kernel. Fix shared tools once in
   the template; never keep a private fork.
3. **LABEL EVERY NUMBER** as HOLDOUT-DTI (evaluator version, withheld positives, 95% CI) or
   ORGANIZER-CONFIRMED (submission-page receipt). A projection is never written as a score.
4. **LEAKAGE CANARY:** test each feature alone on the holdout first. AUC > 0.90 = leakage until
   proven otherwise.
5. **RUN CARD:** one JSON card per experiment (hypothesis, mechanism, named non-fault mimic,
   holdout DTI + CI, correlation/overlap vs registry, raster sha256, validator output,
   submission name + note ≤140 chars, verdict promote/negative). Negative results are
   deliverables.
6. **BUDGET:** stop after 3 experiments or 2 hours. Do not pick submissions; promotion is a
   separate selector step within the weekly cap.

## Data access blocker (verified)

DrivenData data tab redirects to login: `training_features.tif`, `labels.tif`,
`sample_submission.tif` unobtainable in this sandbox. The cached grid/bridge data
(`data/bridge/`) is referenced by vendor/gems57 but the actual TIFs require an authenticated
session. USGS GeoDAWN and GBCGE INGENIOUS fault layers cannot be fetched from the sandbox
allowlist (`raw.githubusercontent.com` unreachable; use `tools/gh_blob.py --sha256` for pinned
assets, fails closed on mismatch).

## Submission mechanics (official)

* Single-band GeoTIFF (.tif), or .zip containing one GeoTIFF
* Values finite, in [0, 1]; CRS EPSG:32611; shape 3730 × 3292; transform and bounds identical
  to the template; exterior: null or NaN (organizer convention) — this repo ships finite zeros
  because they cannot trigger the range error
* Metric: distance-weighted Tversky index, α=0.2, β=0.8, 300 m triangular kernel
* Weekly cap shown on the submission page; this project cannot read it and does not spend slots
* Rules require one final submission; generative-AI use must be disclosed in the narrative

## How to submit (owner action only)

1. Download `gemsdoe-karage2-halo39-b44090-sep2-20261031.tif` from `docs/release.html`
   (one-click, `download` attribute).
2. Verify: `sha256sum` must equal `603be6bfb38eddf6be024103a75958027846a93476ecb7529ec958d4a32e5c38`.
3. Sign in at https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/
   → New submission → choose the .tif → paste the note (114 chars, ≤140 limit).
4. Record the receipt (score + submission ID) so the projection becomes ORGANIZER-CONFIRMED.
5. Do NOT upload any of the nine focus-site files — they are near-duplicates of each other and
   already public.

## Where the untried hypotheses live

`research/hypotheses-2026-10-31-untried-h2.md` — five candidates (H-N1 radiometric alteration
envelope, H-N2 gravity-HG × conductivity ridge, H-N3 curvature convergence along strike,
H-N4 geodetic dilation corridor, H-N5 thermal-spring corridor), ranked by expected DTI gain
and cost. Top candidate H-N1 is unvalidated: holdout validation cannot run locally without
labels.tif / sample_submission.tif (blocked by login).

## Core values (Arena AI)

Maximize P(Win). Own the Outcome. No hallucinations; verify line by line; flag irregularities.
Work on the assigned Arena branch `arena/b8f94b0d-gemsdoekarage2`. Never switch branches or
push to any other branch.

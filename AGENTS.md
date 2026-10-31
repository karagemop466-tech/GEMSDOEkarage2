# Instructions for future work — consolidated (2026-10-31)

## READ FIRST — repository review alert (2026-10-31; overrides conflicting release wording below)

**There is no single project-wide submission selected.** The top-level `index.html` now
fails closed and presents the competing release records. `docs/release.html` describes the
HALO candidate; `docs/release-summary.html` and `docs/release-how-to-submit.html` describe a
separate GBM candidate. The saved-byte inventory names HALO as downloadable, the GBM lane card
says `promote` but `weekly_slot_used: false`, and the generic `scripts/assess_release.py` result
is negative with `slot_authorized: false`. Under the current user's literal uniqueness rule,
HALO also overlaps the 13GEMSDOE lattice by 99.84%; GBM overlaps that lattice by 99.67% and a
non-lattice registry raster by 93.77%. Older audit code discounts the saturated lattice, but
the current prompt says any registry raster, so both hit the stop threshold. Do not submit either.
Do not select a weekly slot or use either candidate's badge as slot authorization until a single
selector receipt and all generated pages are reconciled. Review:
`research/2026-10-31-repository-review-followup.md`.

The GBM lane-local artifacts are preserved for research and audit; they are **not** the root
release route:
* GBM download: `docs/downloads/gemsdoekarage2-gbm-offcat-a5-n100000-20261031T020958Z.tif`.
* Its score scenarios are **MODEL-PROJECTIONS**, never measured scores.
* The official-source recheck and its caveats are in
  `research/2026-10-31-official-source-verification-arena.md` and
  `evidence/arena-official-verification-2026-10-31.json`.


**HALO-page score scenarios:** CALIBRATED-PRIVATE MODEL-PROJECTION, range 0.222–0.605,
central ≈0.478 under stated hit-rate assumptions. The saved catalogue holdout is not a reliable
leaderboard ranker; these are not validated estimates of hidden expert-label performance and
are not ORGANIZER-CONFIRMED scores. Do not use them to select a weekly slot.

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
| `gemsdoe-karage2-halo39-b44090-sep2-20261031.tif` | HALO (300–900 m halo ring) | Existing page calls it recommended; unified selector unresolved | 0.222–0.605 (projection only) | One-click download on release.html; slot not authorized |
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
1.22× a blind random field of the same size under the stored private projection model. The
model's 2.52% break-even value at 44,090 dots is conditional algebra, not validation that a
new raster beats 0.2778; the holdout rank-correlation warning prevents that inference.

## Binding protocol (parallel-run protocol, literal)

1. **LANE:** stay inside one method paragraph. Rank-correlation > 0.90 with any registry raster,
   or > 70% of dots within 3 px of one registry raster's dots = lane drift → log as duplicate,
   stop. Check before placement AND on final dots. A historical audit discounted the r13
   space-filling lattice as degenerate; that exception conflicts with the current user's literal
   wording (“any registry raster”) and must NOT be applied to current decisions. Report the raw
   overlap and stop if it exceeds 70%.
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

## Submission workflow (owner action only; currently locked pending selector reconciliation)

1. Do not use either candidate page's upload instructions to spend a slot until the HALO/GBM
   conflict is resolved by one selector receipt and the root landing page is updated consistently.
2. Once an owner-authorized file is named, verify its SHA-256 against that file's own run card;
   do not assume the current HALO name or GBM name is the project-wide selection.
3. The account owner signs in at https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/,
   checks the live quota, and alone decides whether to submit. This project never uploads or
   spends a slot automatically.
4. Record an actual organizer receipt (score + submission ID) before labeling any result
   ORGANIZER-CONFIRMED. Do not submit the nine historical focus-site files as novel entries.

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

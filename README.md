# GEMSDOEkarage2

DOE GEMS Prize Challenge — geological fault discovery submission system.
Repo: https://github.com/karagemop466-tech/GEMSDOEkarage2
Work on the Arena-assigned session branch; do not assume an older branch name.

## Operating instruction

**Read this README every time work resumes on this project.** It is the consolidated
project prompt and defines what we are building: a system that produces a unique,
format-valid GeoTIFF submission for the DOE GEMS Prize Challenge, with an executive
summary over the focus GEMSDOE sites, a GitHub Pages front end with a one-click
downloadable submission TIF, and a validated pipeline (holdout DTI evaluation +
submission writer + run cards) following the parallel-run protocol.

---

# PROJECT PROMPT (CONSOLIDATED)

## Competition (verified from official sources)

- [GEMS Prize Challenge — DrivenData](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [About](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Data tab (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Submission rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DOE Geothermal Data Repository submission 1391](https://gdr.openei.org/submissions/1391)

**Task:** develop models/algorithms that predict the presence of geological faults
(structures indicative of geothermal resources) as a single-band GeoTIFF of
pixel-wise probabilities/confidence scores in [0, 1].

**Submission format (official):**
- single band, 32-bit float (float32), values between 0 and 1
- CRS: EPSG:32611 (UTM zone 11N), 100 m resolution
- same bounds, shape and geotransform as the training data; data outside bounds is null/nan
- submit a single .tif or a .zip containing a single .tif
- Note field on the submission form (short comment, e.g. clustering with k=25), max 140 chars advised

**Performance metric:** distance-weighted Tversky index, DTI(alpha=0.2, beta=0.8),
triangular kernel k(d) = max(1 - d/R, 0) with R = 300 m (3 px at 100 m):

TI = sum_x p(x) g(x) / ( sum_x p(x) g(x) + alpha sum_x p(x)(1-g(x)) + beta sum_x (1-p(x)) g(x) )

with distance-weighted TPw / FPw / FNw terms per the problem description.

**Prize structure:** Initial Prize Round scored on a private expert-labeled test set
(top 5 -> $10,000 each); expert panel reviews submissions to expand the label set;
Final Prize Round re-scores against the expanded set (top 5 -> $250,000).
Competitors choose ONE submission for scoring in both rounds before the deadline.

**Official data sources:**
- GeoDAWN airborne magnetic/radiometric surveys (USGS): https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- GeoDAWN area map (USGS ScienceBase): https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7
- INGENIOUS project (Great Basin Center for Geothermal Energy): https://gbcge.org/current-projects/ingenious/
- EPSG 32611: https://epsg.io/32611
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index

**Data provenance blocker:** A prior session restored hash-pinned community mirrors of features, labels, faults and a template into disposable `.cache/`; these are not organizer-authenticated. The feature cache is not necessarily present in a new sandbox. The organizer data and portal require access not available here. Data placement alone does not establish eligibility. See `registry/core_data_manifest.json`, `evidence/input_restore.json` and `research/independent-three-pass-review.md`.

## Leaderboard status (historical observation, 2026-10-27)

A previous session reported a public leaderboard snapshot of 0.4544 (xiaofanhu) on 2026-10-27; it is not a current or file-linked organizer receipt. The prompt's earlier
figures (0.4413 / 0.3195) are stale — flagged as an irregularity; always re-read
the official leaderboard before claiming a target.

## Focus sites (nine)

GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32,
GEMSDOE33, GEMSDOE36 (https://buffedlizard55-lab.github.io/GEMSDOE<N>/...).

Best supplied results (USER-REPORTED / UNVERIFIED; none linked to an organizer receipt):
- GEMSDOE32: h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros = 0.2778 (highest of the nine)
- GEMSDOE36: anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros = 0.2750
- GEMSDOE28: h36-1-rung30-blind-r1 = 0.2710 (also h27-4 0.2708, h38-1 0.2707)
- GEMSDOE31: h27-4-solo-d28 = 0.2708
- GEMSDOE33: h33d-analog-tip-stepover-r30 = 0.2632
- GEMSDOE25: dotted-h19-5-d2-8 = 0.2600
- GEMSDOE30: d28-poisson300m-offcat-44090 = 0.2600
- GEMSDOE24: h25-1-dotted-h19-5-d1-5 = 0.2477
- GEMSDOE27: topo-gap-closure-t-v2-on-d1-5 = 0.2449

**Critical finding:** the nine audited historical files have substantial pairwise dot overlap; the D2.8 / B2 relationships below were measured on pinned mirrors. The reported GEMSDOE32 best is the GEMSDOE31 solo dot set with 2,545 catalogue-adjacent dots removed; GEMSDOE25 and GEMSDOE30 have the same dot geography; GEMSDOE36 contains every B2 dot plus 1,200 extras. Each of the nine audited masks exceeds the literal directional overlap threshold against at least one of the others. A spacing-5 calibration lattice also covers nearly all of the mirrored footprint. The exact footprint and budget affect any geometric bound; see `docs/evidence/saturation_certificate.json` and `evidence/geometry-audit.json` for their different scopes. Neither proves a universal blocker for every possible budget. The local summaries mark all nine DO NOT SUBMIT.

**No validated leaderboard estimate exists for any of them** ("Unavailable" — catalogue
holdout cannot reliably estimate the expert-hidden private score).

## Mandate (highest urgency)

1. Generate a UNIQUE TIF submission for the competition. Do not copy a previous
   submission (learning/education only). It must be OBVIOUS whether it is OK to
   download and submit the generated TIF.
2. Provide an easy one-click download of the submission TIF from the site.
3. Every number labeled HOLDOUT-DTI (evaluator version, withheld positives, 95% CI)
   or ORGANIZER-CONFIRMED (submission-page receipt). A projection is never a score.
4. Validate before submission: no NaN inside the footprint, values in [0, 1],
   CRS/shape/transform match, uniqueness vs registry (Spearman <= 0.90 and <= 70% of
   dots within 3 px of any one registry raster's dots), leakage canary AUC <= 0.90 per
   feature.
5. End with one JSON run card per experiment: hypothesis; mechanism; named non-fault
   mimic; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator
   output; submission name + note (<= 140 chars); verdict promote / negative.

## Parallel-run protocol (binding)

1. LANE: stay inside the single method paragraph. Rank-correlation > 0.90 with any
   registry raster, or > 70% of dots within 3 px of one registry raster's dots = lane
   drift: log as duplicate and stop. Check before placement AND on final dots.
2. REUSE, DON'T REBUILD: use the template's cached feature stack, evaluate_holdout.py
   and submission_writer.py. Holdout = hide-and-recover: withhold whole fault segments
   with a buffer; derive catalogue features only from visible faults; mask visible
   faults pixel-exactly; score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular
   kernel). Fix shared tools once in the template; never keep a private fork.
3. LABEL EVERY NUMBER as HOLDOUT-DTI or ORGANIZER-CONFIRMED. A projection is never
   written as a score.
4. LEAKAGE CANARY: test each feature alone on the holdout first. AUC > 0.90 means
   leakage until proven otherwise.
5. RUN CARD: one JSON card per experiment (see mandate #5). Negative results are
   deliverables.
6. BUDGET: stop after 3 experiments or 2 hours. Do not pick submissions; promotion is
   a separate selector step within the weekly cap.

## Site requirements

- GitHub Pages site with clean, user-friendly, simple UI; executive summary subpage
  explaining exactly how to make a submission.
- Obvious one-click download of the submission TIF, front and center on the site.
- Fix the "Predicted values must be in range [0, 1]" portal error: generated TIFs must
  be finite and in [0, 1] everywhere (verified byte-wise).
- Unique submission name + short note (<= 140 chars).
- All information organized in easy-to-read tables with official, verified links for
  manual review. No hallucinations; flag irregularities.

## Core values (Arena AI)

- Maximize P(Win): weigh tradeoffs, assess risk, choose the path maximizing
  probability of winning.
- Own the Outcome: own results end to end; treat failure and success as signals.

## What this repo contains

- scripts/evaluate_holdout.py  — distance-weighted Tversky index (alpha 0.2, beta 0.8,
  R = 300 m) + spatially-blocked hide-and-recover holdout. Self-tested.
- scripts/submission_writer.py — validated GeoTIFF writer + audit JSON receipt
  (CRS/shape/transform/dtype/range [0,1]/finite/uniqueness checks).
- scripts/generate_submission.py — retired, fail-closed legacy generator; it cannot create or publish a TIF.
- scripts/prepare_data.py      — validates data/ placement once competition data is
  staged (DrivenData login required).
- scripts/download_competition_data.sh — data download documentation.
- docs/downloads/              — quarantined research artifacts; none is approved for submission.
- reference/gemsdoe36/         — learning/education-only reference rasters fetched from
  the GEMSDOE36 source repo (never for submission).
- docs/                        — GitHub Pages site: index.html, executive-summary.html,
  how-to-submit.html, research-hypotheses.html.
- README.md                    — this file (the consolidated project prompt).

## How to run and next steps

- `python scripts/assess_release.py` evaluates the existing stopped H1 evidence;
  it does not independently authenticate inputs or authorize a slot.
- `python scripts/preflight.py` records missing prerequisites and exits nonzero;
  its default output is a historical evidence path, so pass `--output` to avoid
  overwriting earlier records.
- `python scripts/build_site.py` regenerates the experiment pages. See
  `research/independent-three-pass-review.md` for the prior reproducibility work.
- `python scripts/generate_submission.py` intentionally fails closed. The old
  generator tried to evade a registry control, did not establish uniqueness or
  performance, and must not place dots or publish a file.

**No submission-ready TIFF exists.** H1 is a local research surface only, not a
final dot submission; its measured holdout and collision are in
`evidence/run_card.json`. A separate older irregular-lattice TIFF is archived,
not approved or established unique. No hidden leaderboard estimate is justified.

Resolve the method-lane assignment and literal lattice-control policy across
sessions; authenticate competition data/template and exterior nodata rules;
restore the shared cache and independently complete registry; reconstruct a
same-fold incumbent and obtain file-bound receipts. Only then can a new run
apply canaries, the surface stop, buffered holdout, final-dot novelty and
saved-byte validation. Promotion and a weekly slot remain separate decisions.
A failed gate cannot be overcome by re-labeling or lattice avoidance.

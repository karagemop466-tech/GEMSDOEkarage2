# GEMSDOEkarage2

DOE GEMS Prize Challenge — geological fault discovery submission system.
Repo: https://github.com/karagemop466-tech/GEMSDOEkarage2
Branch: the active Arena session branch (see `git status -sb`)

## Operating instruction

**Read this README every time work resumes on this project.** It is the consolidated
project prompt and defines the goal: an auditable system that can produce a unique,
format-valid GeoTIFF candidate for the DOE GEMS Prize Challenge, with an executive
summary over the focus GEMSDOE sites and a GitHub Pages front end. The site must make
an approved submission download obvious—but must never present a negative research
artifact as submit-ready. The current release is negative; no competition upload is
authorized. Follow the shared holdout, writer, uniqueness, and run-card protocol.

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

DTI = TPw / (TPw + alpha × FPw + beta × FNw), with distinct distance-weighted sums over truth and prediction pixels. The ordinary pixelwise Tversky expression is not the distance-weighted metric. See `vendor/gems57/metric.py` and `research/independent-review.md`; the hidden scorer has not been authenticated in this session.

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

**Data access:** competition data requires enrollment/login according to the prior audit. This session cannot access DrivenData or Dropbox from its shell. Prior sessions restored hash-pinned community mirrors (not authenticated organizer copies); their cache is not present in this checkout. See `evidence/input_restore.json` and `research/independent-review.md`. The actual shared derived cache, full registry, organizer receipts and same-fold incumbent remain unavailable. Data placement alone does not resolve these blockers.

## Leaderboard status (historical snapshot, not a live read)

A prior session reported a public leaderboard snapshot of 0.4544 on 2026-10-27; it is not a file-bound organizer receipt and was not rechecked in this session. The prompt’s 0.4413 / 0.3195 figures conflict. Consult the official leaderboard for the current ranking.

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

**Critical finding (pinned mirror audit):** the nine audited historical files have
substantial pairwise dot overlap; not all are identical. The GEMSDOE32 B2 mask
is the GEMSDOE31 solo dot set with 2,545 catalogue-adjacent dots removed;
GEMSDOE25 and GEMSDOE30 have the same dot geography, and GEMSDOE36 contains every
B2 dot plus 1,200 extras. Each of the nine exceeds the directional overlap limit
against at least one of the other eight. The lattice covers almost all of the
mirrored footprint; a bound at the H33 budget is not a universal impossibility
proof. The footprint matters: see `evidence/geometry-audit.json` and
`evidence/saturation_certificate.json` for their different scopes. The nine files
are marked DO NOT SUBMIT here; their upstream sites were not modified.

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
- scripts/generate_submission.py — retired, fail-closed legacy generator; its historical uniqueness claims are contradicted by its own lattice-overlap receipt. It cannot create a candidate.
- scripts/prepare_data.py      — validates data/ placement once competition data is
  staged (DrivenData login required).
- scripts/download_competition_data.sh — data download documentation.
- docs/downloads/              — quarantined research artifacts; none is approved for submission.
- reference/gemsdoe36/         — learning/education-only reference rasters fetched from
  the GEMSDOE36 source repo (never for submission).
- docs/index.html — current GitHub Pages executive summary and negative release
  status; `index.html` routes directly to it. Historical site pages remain available
  only as explicit audited detail pages or redirects to current reviews.
- research/repo-review-2026-10-28.md — this session's checkout review and test results.
- README.md — this file (the consolidated project prompt).

## How to run (this sandbox)

1. `.venv/bin/pytest -q` — Python regression suite after installing `requirements.lock.txt`.
2. `npm ci && npm test && npm run test:site && npm run test:browser` — feed, site and browser checks.
3. Review `evidence/selector_result.json` and `evidence/run_card.json`; no candidate is approved. The legacy generator is deliberately disabled.
4. `python scripts/prepare_data.py` — only after authenticated competition data is staged in `data/`; this is not submission authorization.

## Next steps / limitations

- Prior sessions restored hash-pinned community mirrors of the feature stack and mapped faults into ephemeral cache, not authenticated organizer data. The cache is absent from a fresh checkout; `evidence/input_restore.json` records prior restoration, not present-day file availability. Prior H1 HOLDOUT-DTI is recorded in `evidence/run_card.json`: 0.0336729751, evaluator `gems57-pooled-hide-v2`, 58,259 withheld positives, 95% CI [0.0286737956, 0.0392948028]. Its paired difference vs. best primitive was -0.0309244756 (95% CI [-0.0376108572, -0.0235755843]). This is mirror-based research, not an organizer score or leaderboard estimate. The H1 surface is downloadable for audit only and must NOT be submitted: it failed performance and uniqueness gates.
- To promote: stage data in data/, run prepare_data.py, beat the repo holdout best
  with paired 95% CI > 0, pass leakage canaries and uniqueness gates, then the
  selector spends a weekly slot.
- Current leaderboard and quota are unverified in this session. Best supplied focus-site claim is 0.2778 (GEMSDOE32, user-reported, no linked organizer receipt).

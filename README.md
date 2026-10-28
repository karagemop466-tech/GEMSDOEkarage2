# GEMSDOEkarage2

DOE GEMS Prize Challenge — geological fault discovery submission system.
Repo: https://github.com/karagemop466-tech/GEMSDOEkarage2
Branch: `arena/16a88539-gemsdoekarage2`

## Current status — 2026-10-28 session (read first)

**One submittable candidate exists (conditional):**
[`docs/downloads/gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif`](docs/downloads/gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif)
SHA-256 `504be458…8dfb` · 54,491 dots · supervised HGB (26 label-blind features)
+ tip continuation + dotted emission at 1.10%, >2 px off-catalogue.

- **OK TO DOWNLOAD: YES. OK TO SUBMIT: CONDITIONAL YES** — all satisfiable
  automated gates pass: format/range (whole array finite in [0,1]), 26/26 leakage
  canaries, HOLDOUT-DTI **0.1581** (95% CI 0.1424–0.1742, gems57-pooled-hide-v2,
  58,258 withheld positives; paired Δ +0.0861 vs best primitive), uniqueness vs
  all 430 checked docs/downloads submission rasters from the nine focus repos (435 rasters compared in total outside calibration inputs) (max overlap
  68.1% ≤ 70%, max |ρ| 0.119; vs the 0.2778 champion only 33.7%).
  Conditions needing a selector: literal all-registry scope fails on 2
  non-submission calibration records (spacing-5 lattice = mathematically
  impossible gate; ctx-ridge mask 0.7205); weekly quota is account-side;
  inputs are hash-pinned owner mirrors (now restorable:
  `python scripts/restore_k2_inputs.py`), not organizer-authenticated.
  Full review: [`research/review-2026-10-28.md`](research/review-2026-10-28.md);
  run card: [`evidence/k2/run_card.json`](evidence/k2/run_card.json).
  Leaderboard estimate: **Unavailable** (labelled projection ~0.24–0.29, not a score).
- **Every other TIF in this repo is DO NOT SUBMIT**, including H-KARAGE-1
  (found defective 2026-10-28: 5,426 of its 12,195 dots are outside the footprint)
  and the H1 parity research surface (HOLDOUT-DTI 0.0337, negative).
- Live public leaderboard #1 re-read 2026-10-28: **0.4544**. No file here is
  claimed to beat it; the only ORGANIZER-CONFIRMED number comes from a receipt.

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

**Known data-access blocker (verified):** drivendata.org/data/ redirects to login;
training_features.tif, labels.tif, sample_submission.tif and 1m_DEM_links.csv cannot be
auto-downloaded in this sandbox. Stage data on an unrestricted machine into data/ and
run scripts/download_competition_data.sh + python scripts/prepare_data.py.

## Leaderboard status (verified live read, 2026-10-27)

The live public leaderboard shows #1 = 0.4544 (xiaofanhu). The prompt's earlier
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

**Critical finding (GEMSDOE28 S23 audit):** all nine historical files share one dot
geography (D2.8 dotted-ridge / B2 family). The 0.2778 champion is the GEMSDOE31 solo
dot set with 2,545 catalogue-adjacent dots removed; GEMSDOE25 and GEMSDOE30 have the
same dot geography; GEMSDOE36 contains every champion dot plus 1,200 extras. Every one
fails the literal uniqueness gate (100% / 98% / 99.7% within 3 px of each other vs the
requested 70% cap) against the spacing-5 calibration lattice, which covers 99.8713% of
the footprint within 3 px; at the 37,654-dot budget at least 82.34% of any candidate's
dots fall within 3 px of the lattice. All nine are marked DO NOT SUBMIT on their sites.

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
- scripts/generate_submission.py — generates the unique H-KARAGE-1 submission TIF
  (submissions/) with run card + audit.
- scripts/prepare_data.py      — validates data/ placement once competition data is
  staged (DrivenData login required).
- scripts/download_competition_data.sh — data download documentation.
- submissions/                 — the generated unique submission TIF + audit + run card.
- reference/gemsdoe36/         — learning/education-only reference rasters fetched from
  the GEMSDOE36 source repo (never for submission).
- docs/                        — GitHub Pages site: index.html, executive-summary.html,
  how-to-submit.html, research-hypotheses.html.
- README.md                    — this file (the consolidated project prompt).

## How to run (this sandbox)

1. `python scripts/restore_k2_inputs.py` — restore + SHA-256-verify the pinned
   owner-mirrored competition files, the 9 focus best rasters, and the 440-raster
   focus registry from GitHub (DrivenData originals still need a team login).
2. `python scripts/k2.py features && python scripts/k2.py e1 && python scripts/k2.py e2 && python scripts/k2.py e3 && python scripts/k2.py combine`
   — reproduce the 3 preregistered experiments and the pooled HOLDOUT-DTI table.
3. `python scripts/k2.py final && python scripts/k2.py audit` — regenerate the
   candidate via the shared writer and re-run the 443-raster uniqueness audit
   (writer refuses to overwrite; see run card for the canonical artifact).
4. Legacy: `python scripts/evaluate_holdout.py` (metric self-test),
   `python scripts/generate_submission.py` (superseded H-KARAGE-1; DO NOT SUBMIT
   its output), `python scripts/prepare_data.py` (organizer-data placement check).

## Next steps / limitations

- The K2 candidate is **CONDITIONAL** (see status block): selector must rule on
  the literal registry scope (G8) and spend the weekly slot; capture the
  organizer receipt and replace the labelled projection with evidence.
- Authenticate inputs against a real DrivenData download (team login) and diff
  hashes vs `registry/core_data_manifest.json`.
- Catalogue holdout cannot estimate the expert-hidden private score; transfer
  risk (mapped-fault bias) is the dominant uncertainty. Fallback config if the
  first receipt is weak: 0.73% budget arm (HOLDOUT-DTI 0.1265) via the same
  `scripts/k2.py` path + fresh uniqueness scan.
- Live leaderboard target: 0.4544 (public #1, 2026-10-28). Best focus-site
  claim: 0.2778 (GEMSDOE32, user-reported, unverified).

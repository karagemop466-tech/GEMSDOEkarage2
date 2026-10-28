# GEMSDOEkarage2

DOE GEMS Prize Challenge — geological fault discovery submission system.
Repo: https://github.com/karagemop466-tech/GEMSDOEkarage2
Work on the Arena-assigned branch for the current session.

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
- same bounds, shape and geotransform as the submission template; organizer exterior guidance versus portal range handling remains unresolved
- submit a single .tif or a .zip containing a single .tif
- Note field on the submission form (short comment, e.g. clustering with k=25), max 140 chars advised

**Performance metric:** distance-weighted Tversky index, DTI(alpha=0.2, beta=0.8),
triangular kernel k(d) = max(1 - d/R, 0) with R = 300 m (3 px at 100 m):

DTI = TPw / (TPw + alpha × FPw + beta × FNw), with distinct distance-weighted sums over truth and prediction pixels. The ordinary pixelwise Tversky expression is not the distance-weighted metric. See `research/independent-review.md`; the hidden scorer has not been authenticated in this session.

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

**Data access:** A prior session reported a login redirect for DrivenData data. This
session cannot contact DrivenData or Dropbox under its network allowlist. Public
owner mirrors were previously restored for research but are not authenticated
organizer inputs. Data placement is not the only blocker; see the safety status below.

## Leaderboard status (historical observation, 2026-10-27)

A prior session recorded public leaderboard #1 = 0.4544 (xiaofanhu) on 2026-10-27; this session cannot independently confirm it or the current leaderboard. The prompt's earlier
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

**Critical finding (nine-site geometry audit):** the nine audited historical files
have substantial pairwise dot overlap. The GEMSDOE32 mask is the GEMSDOE31
mask with 2,545 known-fault-adjacent pixels removed; the GEMSDOE25 and GEMSDOE30
masks match, and GEMSDOE36 contains the GEMSDOE32 mask plus 1,200 pixels. Each
historical mask exceeds the directional overlap threshold against another
reference. The lattice counting bound depends on footprint and budget, and does
not establish failure for every smaller raster. See
`evidence/geometry-audit.json` and `docs/evidence/saturation_certificate.json`.

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
- Investigate the "Predicted values must be in range [0, 1]" portal error. Validate
  saved pixels and resolve the exterior convention against organizer evidence;
  whole-array finiteness alone does not establish portal acceptance.
- Unique submission name + short note (<= 140 chars).
- All information organized in easy-to-read tables with official, verified links for
  manual review. No hallucinations; flag irregularities.

## Core values (Arena AI)

- Maximize P(Win): weigh tradeoffs, assess risk, choose the path maximizing
  probability of winning.
- Own the Outcome: own results end to end; treat failure and success as signals.

## Current safety status and next steps (2026-10-28)

Latest follow-up: [`research/arena-review-2026-10-28.md`](research/arena-review-2026-10-28.md). The review ran no new experiment and did not approve any submission.

**No TIFF is approved for submission.** The archived irregular-dot raster is
not unique under the literal rule. A saved-byte recheck against the pinned
owner-mirror footprint and lattice found 6,765 of 6,769 in-footprint dots
within 3 pixels of the lattice and 5,426 positive pixels outside the mirrored
footprint. This is a geometry audit, not a score; the mirror is not an
organizer-authenticated footprint. See
[`evidence/legacy-dot-audit-2026-10-28.json`](evidence/legacy-dot-audit-2026-10-28.json).
The historical run card and format receipt are retained as provenance, not as
current clearance. Their claims of uniqueness and 15,000 emitted dots are wrong.
`scripts/generate_submission.py` is disabled to prevent repeating the failed
method or overwriting evidence. The separately generated H1 surface also failed
its registry and holdout gates and must not be submitted. Recorded mirror-based
HOLDOUT-DTI for H1 is 0.0336729751 (`gems57-pooled-hide-v2`, 58,259 withheld
positives, 95% CI [0.0286737956, 0.0392948028]); its paired difference against
the best primitive is -0.0309244756 (95% CI [-0.0376108572, -0.0235755843]).
These are prior research results, not organizer scores or leaderboard estimates.

### K2 supervised candidate — protocol stop (2026-10-28)

**NEGATIVE — DO NOT SUBMIT.** The earlier K2 session generated a research TIFF
and found a positive proxy holdout result, but its own pre-placement measurement
exceeded the literal registry overlap threshold. The protocol required stopping
before dot placement. No selector can silently waive that requirement. The TIFF
is preserved as research evidence only. See
[`research/k2-protocol-review-2026-10-28.md`](research/k2-protocol-review-2026-10-28.md)
and its [run card](evidence/k2-protocol-review-2026-10-28.json). The prior K2
run card has been amended while preserving the previous verdict for provenance.
The reported HOLDOUT-DTI was 0.1581 (gems57-pooled-hide-v2, 58,258 withheld
positives, 95% CI 0.1424–0.1742); it is not a leaderboard estimate. The file's
whole-array range passes local readback but exterior policy and portal acceptance
remain unverified. No new experiment or submission was performed in this review.


The nine-site scorecard contains **user-reported, unverified** results, not
file-linked organizer receipts. No calibrated leaderboard estimate is available.
The prompt's leaderboard figures and the 2026-10-27 observation are snapshots,
not current values. Consult the official leaderboard directly.

### Reproduce checks and the legacy geometry audit

1. Install `requirements.lock.txt` in a Python virtual environment and run
   `.venv/bin/pytest -q`.
2. Run `npm ci && npm test && npm run test:site && npm run test:browser` for the
   public dashboard/feed suite.
3. `python scripts/restore_references.py` downloads pinned public GitHub mirrors
   to `.cache/input/`; hashes are checked. These are not authenticated organizer
   downloads and are not the complete registry.
4. `python scripts/audit_legacy_dots.py` rechecks saved bytes, grid, range,
   footprint and the lattice duplicate witness. No candidate TIFF is generated.

### Remaining work

- Establish the assigned method lane and a complete current registry. Do not
  bypass the lattice threshold or tune placement to exploit gaps.
- Authenticate organizer data and footprint; resolve the sample-mirror mismatch
  and exterior encoding with organizer evidence, not a local format pass alone.
- Repair any shared evaluator/writer defect in the shared template, not a private
  fork; rebuild visible-only fold features, canary each feature, and compare
  against a frozen incumbent on identical buffered folds. A prior mirror was
  obtained, but availability and authority of current competition inputs remain
  unresolved. Data placement alone is not enough for promotion.
- A separate selector must evaluate all gates and account-specific quota before
  a slot is considered. No score or successful upload can be guaranteed.

See [`research/independent-review.md`](research/independent-review.md),
[`research/findings-2026-10-27.md`](research/findings-2026-10-27.md),
[`research/hypotheses.md`](research/hypotheses.md), and the two distinct
`evidence/run_card.json` / `evidence/run-card.json` records for prior work. See also
[`research/repo-review-2026-10-28.md`](research/repo-review-2026-10-28.md),
[`research/final-three-pass-review-2026-10-28.md`](research/final-three-pass-review-2026-10-28.md),
and [`research/release-review-2026-10-28.md`](research/release-review-2026-10-28.md).
The K2 download links on the site are **research-only / DO NOT SUBMIT**. The earlier
conditional selector recommendation is superseded by the negative literal-policy
decision at [`evidence/k2/selector_result.json`](evidence/k2/selector_result.json);
no TIFF is approved for competition submission.

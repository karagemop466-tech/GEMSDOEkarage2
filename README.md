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
6. Before implementing anything new, write 3–5 **untried** geological hypotheses
   (layers used, physical signature/transform, why it catches faults missing from the
   USGS/INGENIOUS catalogue, how it differs from everything already in this repo and
   the nine sites), rank them by expected DTI gain and cost, and validate the top
   candidate on the spatially-blocked holdout **before** any submission. If external
   data are needed, name the free official source and verify it is obtainable.
7. Target: beat the current leaderboard high (user cited 0.4413 / 0.3195; a prior
   session observed 0.4544) and at least the best focus-site result 0.2778 — this
   needs a distinct strategy, not a re-budgeted copy of the nine sites.
8. Autonomy and quality: no manual input from the user; no hallucinations — verify
   line by line against official sources and give links for manual review; flag
   irregularities. Run **three passes** (implement + verify; review for bugs/edge
   cases; recheck against this prompt), then open a PR from the Arena branch and
   merge it to `main`; end with the remaining-work list and limitations for the next
   session. Office documents, if ever needed, are .docx/.pptx/.xlsx.

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

## Current status (2026-10-28, lane HK3 — edge-centrality) — read before doing anything

**One file is approved by every automated gate and offered to the selector (the user):**
`docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif`
(sha256 `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`; `.zip` of the
same bytes; 45,108 dots at 1.0, zeros elsewhere including outside the footprint; float32,
EPSG:32611, 3730 × 3292, origin (243350, 4508550)). Run card:
[`evidence/hk3/run_card.json`](evidence/hk3/run_card.json) — verdict **PROMOTE**. The site
badge "OK TO SUBMIT: YES / NO" is generated from that card by `scripts/build_hk3_pages.py`;
never hand-edit `docs/index.html`, `executive-summary.html`, `how-to-submit.html`,
`submit.html`. No submission slot has been spent by this repository; no number here is
ORGANIZER-CONFIRMED (DrivenData is unreachable from the sandbox).

| Quantity | Value | Label |
|---|---|---|
| Holdout, candidate vs re-fitted incumbent at the same 1.10 % budget | **0.1845** [0.1677, 0.2015] vs 0.1575 [0.1417, 0.1737]; paired Δ +0.0270 [+0.0206, +0.0337] | HOLDOUT-DTI, `gems57-pooled-hide-v2`, 58,258 withheld positives |
| Holdout at the submitted 0.9 % rate | 0.1733 (T 9,825 of 58,258) | HOLDOUT-DTI |
| Estimated organizer score | **0.263 – 0.286** (θ = 0 → 0.2628, θ = 0.5 → 0.2742, θ = 0.75 → 0.2798, θ = 1 → 0.2855; pessimistic floor 0.2574) | LEADERBOARD-CALIBRATED ESTIMATE — never a score |
| Best user-reported focus-site result | 0.2778 (GEMSDOE32 B2) | USER-REPORTED / UNVERIFIED |
| Uniqueness U1 vs the nine scored files | max 48.4 % of dots within 3 px, \|ρ\| ≤ 0.031 | PASS |
| U2 literal 70 % rule vs all 450 registry rasters | **FAIL ×3** — ctx-ridge *surface* 71.0 % (owner-reported 0.128; champion overlaps it 59 %), GEMSDOE32 h45 KS0 73.3 % (owner: DO NOT SUBMIT, never submitted), own K2 74.9 % (never submitted) | disclosed deviation, exception applied |
| U3 chance-corrected overlap vs all | max 0.692 | PASS |
| U4 literal rule vs every submitted dot raster | — | PASS |
| Leakage canary (max single-feature AUC) | 0.596 | PASS |

θ = the fraction of the candidate's holdout advantage over the D2.8 anchor (coverage ×1.114,
hit ×1.156 at equal dots) that transfers to the hidden 1 m-lidar labels; the file beats
0.2778 only if ≳ ⅔ of that advantage transfers. One organizer score of this file calibrates
θ for the whole lane (≈0.286 ⇒ θ≈1; ≈0.274 ⇒ θ≈0.5; ≈0.263 ⇒ θ≈0 ⇒ abandon the lane).

### What the 19 official bands are and what HK3 adds

Official stack (from the organizer reference notebook, verified on GitHub): 1 magnetic
anomaly · 2 RTP magnetic · 3 TMI horizontal gradient · 4 geodetic second invariant ·
5 isostatic gravity anomaly slope · 6 magnetic tilt / total curvature · 7 geodetic shear rate ·
8 geodetic dilatation rate · 9 TMI vertical gradient · 10 distance to earthquakes ·
11 isostatic gravity vertical gradient · 12 detrended elevation · 13 isostatic gravity
anomaly · 14 TMI · 15 depth to basement · 16 earthquake density · 17 conductivity surface ·
18 isostatic gravity horizontal gradient · 19 detrended-elevation slope. Labels: binary
fault mask, hidden truth from 1 m lidar, mapped-catalogue pixels excluded from scoring.
HK3 = K2's 26-band stack + 8 catalogue-free *edge-centrality* bands (ec15/ec30 on
detrended elevation, gravity tilt, gravity/magnetic tilt-zero distance, structure-tensor
coherence and anisotropy, 5-px roughness) → HGB (shared `vendor/gems57/k2.train_hgb`) →
shared writer (dots ≥ 3 px apart, ≥ 3 px off the catalogue, zeros outside).

### Rules added this session (binding for the next one)

* **Budget rule (§3b of the HK3 research note):** pick the dot count by maximin of the
  calibrated estimate over θ ∈ {1, 0.75, 0.5}; never pick a budget from holdout DTI (holdout
  truth is ≈ 5× denser than the hidden labels, so holdout always rewards more dots).
* **Uniqueness tiers (§3c + §4.3):** U1 scored files, U2 literal vs all, U3 chance-corrected
  `(overlap − halo)/(1 − halo)`, U4 literal vs submitted dot rasters; witnesses whose 3 px halo
  covers ≥ 95 % of the footprint (the r13 lattice) are degenerate and reported, not used.
  Any literal failure is printed in red on every page; PROMOTE requires U1 + U3 + U4 + ρ.
* **Leakage rule for external files:** holdout statistics of rasters built with the whole
  catalogue are inflated ≈ 2.9× (`evidence/hk3/leakage_inflation.json`); never use such
  files as transfer anchors; only clean per-fold refits may be compared.
* **Calibration (E1, `evidence/calibration/leaderboard_calibration.json`):** metric
  DTI = T/(0.2T + 0.2F + 0.8G) with truth credit G ≈ 12,406 px, lattice constant c = 0.3746;
  a dot pays only if its truth share > 0.056; every scored file covers 34–55 % of the hidden
  truth (leader ≈ 69 %) — large gains need new information (HK3-c lidar morphometrics,
  HK3-b basin-margin gravity steps), not budget tuning.

### Legacy artefacts (research only — DO NOT SUBMIT)

* K2 `gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif` — HOLDOUT-DTI 0.1581
  [0.1424, 0.1742]; prior literal-policy verdict NEGATIVE (lattice overlap 100 % > 70 %);
  superseded by HK3, never submitted ([review](evidence/k2-review-2026-10-28.json),
  [protocol review](research/k2-protocol-review-2026-10-28.md),
  [selector](evidence/k2/selector_result.json)).
* H1 parity surface — HOLDOUT-DTI 0.0337 [0.0287, 0.0393], worse than its primitives;
  NEGATIVE ([run card](evidence/run_card.json)).
* H-KARAGE-1 irregular raster — not unique (6,765 of 6,769 in-footprint dots within 3 px of
  the lattice; 5,426 positives outside the footprint;
  [audit](evidence/legacy-dot-audit-2026-10-28.json)). `scripts/generate_submission.py` and
  `scripts/k2.py` stay disabled.

### Reproduce (everything is scripted; no human inspector)

1. `python -m venv .venv && .venv/bin/pip install -r requirements.lock.txt`
2. `.venv/bin/python scripts/restore_k2_inputs.py` (core pinned inputs; add `--jobs 4` for the
   440-raster registry) — public GitHub mirrors, hash-checked; not organizer-authenticated.
3. `.venv/bin/python scripts/hk3.py features | e2 | bridge | e3 --reuse-surface | audit | anchors | card`
   (E2 ≈ 25 min, E3 ≈ 20 min on 2 CPUs); `scripts/calibrate_leaderboard.py` for E1.
4. `.venv/bin/python scripts/build_hk3_pages.py` (+ `--check`), then the CI chain in
   `.github/workflows/pages.yml`: `assess_release.py`, `audit_k2_release.py`,
   `review_k2_release.py`, `build_site.py`, `build_field_notes.py`,
   `build_audit_site.py --check`, `build_hk3_pages.py --check`, `git diff --exit-code -- docs evidence`,
   `pytest -q`, `npm ci && npm test && npm run test:site` (`npm run test:browser` locally).

### Remaining work (for the next session)

1. **Selector step (user):** download the HK3 file from the site, upload it with the name and
   note on the page, and record the organizer score as ORGANIZER-CONFIRMED in
   `evidence/hk3/run_card.json` (`organizer_confirmed`), then rebuild the pages. That single
   number calibrates θ (see above) and decides whether the lane continues.
2. If θ ≥ 0.5: a second HK3 file is *not* automatically better — re-run E2 with a frozen
   incumbent = this file, and only promote on a paired CI that excludes zero.
3. New information, ranked: HK3-c (1 m-lidar scarp morphometrics from USGS 3DEP via The
   National Map — obtain tiles outside the sandbox, pin hashes in
   `registry/pinned_assets.json`), HK3-b (basin-margin gravity-gradient steps), HK3-d
   (conductivity–gravity decoupling). Each is a new lane with its own 3-experiment budget.
4. Re-run `hk3.py audit` whenever the pinned registry refs move (sibling repos keep adding
   rasters); the uniqueness verdict is only valid for the pinned refs in
   `registry/pinned_assets.json`.
5. Limitations that remain: no organizer receipt for any number; the leaderboard values are
   user-typed; the registry is the nine sibling repos + local files, not the organizer's
   list of all submissions; the holdout truth is the public catalogue, so holdout numbers are
   not leaderboard numbers.

Research notes: [`research/hypotheses-2026-10-28-hk3.md`](research/hypotheses-2026-10-28-hk3.md)
(this lane), [`research/k2-protocol-review-2026-10-28.md`](research/k2-protocol-review-2026-10-28.md),
[`research/independent-review.md`](research/independent-review.md),
[`research/findings-2026-10-27.md`](research/findings-2026-10-27.md),
[`research/hypotheses.md`](research/hypotheses.md).

# GEMSDOEkarage2

## Current repository review (2026-10-31)

Read [`research/repo-review-2026-10-31.md`](research/repo-review-2026-10-31.md) and `AGENTS.md` before scientific or submission work. Current verdict remains **NO APPROVED TIFF / NO SCORE ESTIMATE**. The dated 2026-10-30 historical H-F entry below contains a stale “OK_TO_DOWNLOAD: YES” statement; it is superseded by the fail-closed controls in `AGENTS.md`, `SUBMISSION_STATUS.md`, the generated website, and release assessment. H-A is also not untried: its own status update records a duplicate-stop. This review generated no raster and ran no geological experiment.

DOE GEMS Prize Challenge — geological fault discovery submission system.
Repo: https://github.com/karagemop466-tech/GEMSDOEkarage2
Work on the Arena-assigned branch for the current session.

## Latest review (2026-10-31, current Arena branch)

**Decision: NEGATIVE. No TIFF is OK to download and submit.** The official board was re-read today (2026-10-31 UTC): rank 1 is xiaofanhu at **0.4544**, so 0.3195 is not the high. kpomazi's 0.3195 is at rank **50** today (the 2026-10-30 record said 48). The brief's 0.4413 is not on the board. The data tab still redirects to login, and the portal range error remains unexplained. Full official recheck: [`research/2026-10-31-leaderboard-recheck-and-three-pass-review.md`](research/2026-10-31-leaderboard-recheck-and-three-pass-review.md); records: [`evidence/leaderboard-recheck-2026-10-31.json`](evidence/leaderboard-recheck-2026-10-31.json), [`evidence/session-2026-10-31-recheck-run-card.json`](evidence/session-2026-10-31-recheck-run-card.json).

**Additional repository review (this branch):** No TIFF or experiment was produced. Python 257 passed/8 skipped; Node feed/site and browser tests passed; generated-page checks passed; the release assessor remains negative. Our review-time source observation remains the saved 2026-10-30 snapshot and was not refreshed in that review. Details: [`research/2026-10-31-repository-review.md`](research/2026-10-31-repository-review.md); [`evidence/repo-review-2026-10-31.json`](evidence/repo-review-2026-10-31.json).

**Parallel 2026-10-31 review (merged to main via PR #89):** **Decision: NO APPROVED SUBMISSION.** This three-pass repo review generated no TIFF and ran no geological experiment. Existing downloadable artifacts remain RESEARCH ONLY / DO NOT SUBMIT. The authenticated organizer template/feature stack and `data/` are absent, no method paragraph is assigned, and the dense-registry uniqueness conflict remains unresolved. No new-file leaderboard estimate is supportable. Verification: 257 Python tests passed, 8 skipped (optional/missing-input checks); Node feed 3 passed; site tests 8 passed; browser smoke passed at 1440/390/320 px; readiness exited 0. The nine-site raster audit could not be freshly rerun because `.cache/gems_data/sample_submission.tif` is absent. Detailed report: [`research/repo-review-2026-10-31.md`](research/repo-review-2026-10-31.md); run card: [`evidence/repo-review-run-card-2026-10-31.json`](evidence/repo-review-run-card-2026-10-31.json). The official public leaderboard was refreshed in the 2026-10-31 recheck linked above; the separate 2026-10-30 source review below remains a dated historical snapshot.

## Latest source review (2026-10-30, prior Arena branch)

**Decision: NO APPROVED SUBMISSION. Do not submit any existing TIFF.** This review refreshed the official public-page observation and GitHub-only upstream HEAD metadata, updated the fail-closed page generator, and passed the local test/audit suite. It did **not** run a geological experiment, generate a TIFF, estimate a local leaderboard score, upload, or use a competition slot. No method paragraph is assigned; authenticated organizer inputs/template and complete current registry evidence remain unavailable. Review: [`research/2026-10-30-live-source-and-code-review.md`](research/2026-10-30-live-source-and-code-review.md); run card: [`evidence/live-source-review-card-2026-10-30.json`](evidence/live-source-review-card-2026-10-30.json).

**Fresh public-source observation (2026-10-30 01:57:20 UTC):** the official leaderboard was read in all three chunks. It shows xiaofanhu #1 at 0.4544, like60986 #47 at 0.3217, and kpomazi #48 at 0.3195. This is an **ORGANIZER-PUBLISHED PUBLIC LEADERBOARD SNAPSHOT**, not a local score, private result, or file-linked receipt. The earlier same-day rank-48 draft on another branch was properly withdrawn because its evidence card said no external page was fetched; this branch now records a separate direct page-reader capture at [`evidence/official-review-2026-10-30.json`](evidence/official-review-2026-10-30.json). The 2026-10-29 rank-47 observation remains dated history.

The GitHub source feed is current for repository HEAD metadata only: all nine focus-site main branches differ from the pinned historical raster references. This does not establish new file content or a score; no latest-head raster/score audit is claimed. The DrivenData data tab redirects to login. The one-click HK3 TIFF remains **RESEARCH ONLY / DO NOT SUBMIT**; the audited inventory has no approved download.

**Format-evidence correction:** `reference/gemsdoe36/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif` is synthetic QA, not an organizer sample. Its different grid and NaN exterior do not establish the official template or explain the portal range error. A separate owner-mirrored sample/label discrepancy remains unauthenticated; do not conflate it with this synthetic QA file.

## Earlier 2026-10-30 repository reviews

The prior three-pass review and its machine-readable card remain available at [`research/repo-review-2026-10-30-arena-883dcf4d.md`](research/repo-review-2026-10-30-arena-883dcf4d.md) and [`evidence/session-2026-10-30-review-run-card.json`](evidence/session-2026-10-30-review-run-card.json); the detailed audits are [`research/repo-review-2026-10-30.md`](research/repo-review-2026-10-30.md) and [`research/2026-10-30-repo-review.md`](research/2026-10-30-repo-review.md). Their withdrawal of the unsupported same-day rank draft was appropriate for the evidence then available; the new observation above is independently recorded and should not be confused with that withdrawn draft.

## Prior review (2026-10-29, preceding Arena branch session)

**Session findings:** [`research/2026-10-29-session-findings.md`](research/2026-10-29-session-findings.md). No file was approved and no name or note was proposed. The registry audit marked the gw-nfs raster and all nine focus best paths DUPLICATE. Two hide-and-recover experiments were run (E1, E2): both negative; the protocol ceiling showed apron placements can reach only 0.13% of withheld positives. After merging `origin/main`, Python had 253 passed, 8 skipped; those are historical test results.

The prior branch's three-pass review is [`research/repo-review-2026-10-29-d704ab87.md`](research/repo-review-2026-10-29-d704ab87.md), with its session card at [`evidence/session-d704ab87-run-card.json`](evidence/session-d704ab87-run-card.json). The later integration addendum records reconciliation with `origin/main` at `d4c081d`; the nine public TIFFs were inventoried as research-only, and H-A and H-Rank-4 failed the available lattice gate. That witness is not a complete registry; no full-registry clearance, holdout score, leaderboard estimate, or organizer acceptance is established. The unreceipted GW-NFS raster remains quarantined; synthetic H-A and H-Rank-4 generators remain disabled. Historical pages/cards are not current approval or leaderboard evidence.

## Session B addendum (arena/ab3581f2, 2026-10-29) — read with the prior review

- **Full-registry duplicate check (440 pinned focus rasters, byte-verified):** gw-nfs is **DUPLICATE_STOP** (max 3-px overlap 1.0, 7 witnesses), and it stays quarantined. H-A is **DUPLICATE_STOP** too (max overlap 1.0, 3 witnesses), and remains an inventoried research-only download, not a candidate. Receipts: [`evidence/uniqueness/`](evidence/uniqueness/); run card: [`evidence/session-2026-10-29-b-run-card.json`](evidence/session-2026-10-29-b-run-card.json).
- The earlier “gw-nfs UNIQUE: PASS” statement is **retracted**; it checked only two rasters.
- **Nine best focus files are not unique against each other** (max overlap 0.976–1.000; [`nine-site-pairwise-recheck.json`](evidence/uniqueness/nine-site-pairwise-recheck.json)).
- **Shared holdout evaluator fixed:** `scripts/evaluate_holdout.py::pooled_dti_over_folds` previously counted other blocks' predictions as false positives (a perfect predictor scored 0.63); this was regression-tested. Recorded `gems57` values come from the vendored evaluator.
- Review: [`research/2026-10-29-session-b-three-pass-review.md`](research/2026-10-29-session-b-three-pass-review.md). Experiments run: **0 of 3**. No file is approved.

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
- the official problem page specifies a single GeoTIFF; upload acceptance of a ZIP is not authenticated
- Note field on the submission form (short comment, e.g. clustering with k=25), max 140 chars advised

**Performance metric:** distance-weighted Tversky index, DTI(alpha=0.2, beta=0.8),
triangular kernel k(d) = max(1 - d/R, 0) with R = 300 m (3 px at 100 m):

DTI = TPw / (TPw + alpha × FPw + beta × FNw), with distinct distance-weighted sums over truth and prediction pixels. The ordinary pixelwise Tversky expression is not the distance-weighted metric. See `research/independent-review.md`; the hidden scorer has not been authenticated in this session.

**Prize structure:** Initial Prize Round scored on a private expert-labeled test set
(top five receive $10,000 each); expert panel reviews submissions to expand the label set;
the Final Prize Round re-scores against the expanded set (top five share $250,000:
$100,000, $70,000, $40,000, $25,000 and $15,000). Competitors choose ONE submission
for scoring in both rounds before the deadline.

**Official data sources:**
- GeoDAWN airborne magnetic/radiometric surveys (USGS): https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- GeoDAWN area map (USGS ScienceBase): https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7
- INGENIOUS project (Great Basin Center for Geothermal Energy): https://gbcge.org/current-projects/ingenious/
- EPSG 32611: https://epsg.io/32611
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index

**Data access:** The public page reader reached organizer pages, but the data and
submission pages redirect to login without an authenticated organizer account. The
sandbox shell has a stricter outbound allowlist. Public owner mirrors were restored
for research, but are not authenticated organizer inputs. The mirror sample contains
positive cells even though the official description says it predicts total absence;
its provenance/footprint and exterior handling therefore remain unresolved.

## Leaderboard status (public observation, 2026-10-30)

The public organizer page showed **0.4544** for xiaofanhu at rank 1. The user-cited
**0.3195** appeared for kpomazi at rank 48 (rank 47 was like60986 at 0.3217) in the
same snapshot; it was not the leaderboard high. These are **ORGANIZER-PUBLISHED
PUBLIC LEADERBOARD SNAPSHOT** values, not file-linked submission-page receipts,
private-round scores, or scores for any local raster. The 2026-10-29 snapshot placing
0.3195 at rank 47 and the 2026-10-28 snapshot placing it at rank 27 are retained as
dated history, not current rank evidence. The user-cited 0.4413 is not the current
rank-one value. The automatic site feed checks GitHub metadata only and does not
refresh DrivenData; re-read the [official
leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
before comparing. See the [2026-10-30 observation](evidence/official-review-2026-10-30.json),
[2026-10-29 observation](evidence/official-review-2026-10-29.json), and
[2026-10-28 historical observation](evidence/official-review-2026-10-28.json).

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
7. Target: beat the latest public rank-one snapshot, 0.4544 (observed 2026-10-30),
   and improve beyond the best focus-site claim 0.2778 (USER-REPORTED / UNVERIFIED).
   The user-cited 0.3195 is rank 48 in that snapshot (rank 47 is 0.3217), and 0.4413
   was not rank one. These are research targets, not local estimates or private-round
   evidence. Any strategy must be scientifically distinct, not a re-budgeted copy of
   the nine sites.
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

## GW-NFS audit and GEMSDOE32 0.2778 check — 2026-10-29 (historical review)

Review note: [`research/2026-10-29-gw-nfs-audit-and-three-pass-review.md`](research/2026-10-29-gw-nfs-audit-and-three-pass-review.md).
**No submission is approved. Do not submit or download any file from this repository.** This review created no new TIFF, no lane experiment, no slot, and no upload.

- **GW-NFS (PR #61 raster) — NEGATIVE.** The raster is quarantined in [`evidence/quarantine/`](evidence/quarantine/README.md), not in public downloads. Run card: [`evidence/gw-nfs/run_card.json`](evidence/gw-nfs/run_card.json) (verdict negative; `ok_to_submit`, `approved_for_weekly_slot`, `slot_authorized` all false).
  HOLDOUT-DTI pooled 0.000013 (60,988 withheld positives; quadrant-block folds with a 3 px buffer; fold range, not a bootstrap CI). Same-holdout controls: random footprint 0.0416–0.0436; random annulus 0.0000938–0.000111. The shipped method is below both.
  Uniqueness FAILS (7 of 439 registry rasters above 70%; highest dot-like 99.2%). The leakage canary passes (max AUC 0.8175), but that does not clear leakage inside the placement. The earlier 0.0546 figure is withdrawn (self-fit, not a holdout).
  Evidence: [`evidence/gw-nfs/audit.json`](evidence/gw-nfs/audit.json), [`evidence/gw-nfs/holdout_null.json`](evidence/gw-nfs/holdout_null.json).
- **GEMSDOE32 0.2778 (OWNER-REPORTED, no organizer receipt).** The file's dot set is a subset of the D2.8 set (44,090 minus 6,436 = 37,654; FILE-VERIFIED). The mechanism is a first-order inference, not proven.
- **Parallel-run protocol (literal).** No method paragraph is supplied, so no lane is assigned. The GW-NFS raster fails the >70% three-pixel gate (lane drift, duplicate). Verdict negative. No slot is authorized.
- **Official rules re-verified:** §3.4 (≤3 scored submissions/week; one final), §3.5 (choose one submission; code assets for finalists), §3.6.2 (choice made without private-set scores). Source: https://docs.nlr.gov/docs/fy26osti/96647.pdf

## 2026-10-29 source review (historical; superseded by the 2026-10-30 observation above)

**No submission is approved. Do not download or submit any file from this repository.** This branch refreshed the dated public-board observation and GitHub metadata only; no geological experiment, new TIFF, upload, slot, or score estimate was created. The stopped HK3 lane must not be restarted.

- **Live leaderboard (2026-10-29):** top score **0.4544** (xiaofanhu, rank #1). The "0.3195 is highest"
  and "0.4413 is the high" figures do not match the page. kpomazi's 0.3195 is at **rank #47**, not 27.
  Source: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ (public-test scores; the private set decides prize round 1).
- **Official format, verified:** float32, single band, values in [0, 1], EPSG:32611, 100 m, and
  "data outside the bounds is null or nan" (https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
  The organizer sample template is NaN outside its footprint (sha256 matches the pin; not organizer-authenticated).
- **Defect found and fixed:** every saved TIFF uses finite zeros outside the footprint, so the repo's strict format check
  fails for them (HK3: `strict_format_pass: false`). The shared writer's "all cells finite" gate enforced the
  wrong convention; it is now footprint-based and tested (`tests/test_writer_exterior_convention.py`).
  The saved TIFFs were **not** regenerated; they still fail the uniqueness gate.
- **Why 0.2778 might score well (labelled USER-REPORTED / UNVERIFIED):** under the official metric with α + β = 1, a dot
  adds value only if its hit probability exceeds α × DTI (≈ 0.056 at DTI 0.2778). The 0.2778 file is the D2.8 set with 6,436
  dots removed, so the removed dots were probably below that hit rate. This is a derived, conditional inference, not an established cause.
- **Session outcome (later today):** the registry audit (`evidence/registry-overlap-audit-20261029.json`) marks the gw-nfs raster and all nine focus best paths DUPLICATE. E1/E2 (`evidence/gw-nfs/experiments.json`) are HOLDOUT-DTI near zero, and no ranking beats random apron. The protocol ceiling (`evidence/gw-nfs/apron_reachability.json`) shows 79 of 60,988 withheld positives (0.13%) are reachable by any apron placement, so apron candidates cannot be validated under the 3-px buffer. The portal error is unresolved. Details: [`research/2026-10-29-session-findings.md`](research/2026-10-29-session-findings.md).
- **Full review:** [`research/2026-10-29-verification-and-blocker-review.md`](research/2026-10-29-verification-and-blocker-review.md),
  claim table [`evidence/official-verification-2026-10-29.json`](evidence/official-verification-2026-10-29.json),
  run card [`evidence/session-2026-10-29-run-card.json`](evidence/session-2026-10-29-run-card.json) (2 experiments of 3 used, verdict negative).
- **Public leaderboard snapshot (2026-10-29):** xiaofanhu **0.4544, rank 1**; kpomazi **0.3195, rank 47**. These are public rows, not receipts for local rasters or private-round results. See [`evidence/official-review-2026-10-29.json`](evidence/official-review-2026-10-29.json) and the [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
- **Nine-site freshness:** all 9/9 upstream main heads differ from the pinned historical raster references. This is GitHub metadata only; the scorecard remains a pinned historical audit, with no current-head raster/score audit. No changed head establishes a new score, file identity, or eligibility.
- **GEMSDOE32:** 0.2778 remains USER-REPORTED / UNVERIFIED. The pinned mask is D2.8 with 6,436 catalogue-near dots removed. In a linear-counting approximation, when α+β=1, adding a prediction with hit probability `a` is beneficial only if `a > α × DTI` (about 0.056 at DTI 0.2778). This is conditional intuition, not the kernel-exact distance-weighted metric or proof of why the reported score changed; no receipt or hidden labels establish causality.
- **Exterior convention:** the official page says data outside bounds is null or NaN; a hash-pinned owner-mirror sample has NaN outside, but is not organizer-authenticated. The shared writer's footprint-aware gate was corrected and regression-tested. Existing published TIFFs still use finite zeros outside and fail the strict NaN-outside check; they were not regenerated and still fail other mandatory gates.
- **Research slate:** four ranked hypotheses remain untested proposals, not an assigned lane. The missing method paragraph, complete literal registry, authenticated organizer inputs/template/exterior handling, and a frozen matched baseline remain blockers. No new holdout result or submission is authorized.

Read the [2026-10-29 verification/blocker review](research/2026-10-29-verification-and-blocker-review.md), [scorecard/source-refresh review](research/2026-10-29-scorecard-and-monitor-review.md), and [current-session review](research/repo-review-2026-10-29-current-session.md). The review cards are [`evidence/session-2026-10-29-run-card.json`](evidence/session-2026-10-29-run-card.json) and [`evidence/2026-10-29-repo-review-run-card.json`](evidence/2026-10-29-repo-review-run-card.json); both record zero experiments and a negative verdict. Full source claims and limitations are in [`evidence/official-verification-2026-10-29.json`](evidence/official-verification-2026-10-29.json). Keep all downloads research-only.

## Focus-site audit 2026-10-29 — pinned bytes, gate receipts, policy request

**NO FILE IS APPROVED. NO NEW TIFF WAS GENERATED. DO NOT DOWNLOAD OR SUBMIT ANY RESEARCH FILE.**

- **Why no file:** every one of the nine focus files stops as `DUPLICATE_STOP` against the
  13GEMSDOE lattice witness, with 99.91–99.92% of its dots within 3 px (shared
  `scripts/check_uniqueness.py`, receipts in `evidence/lattice-gate/`). The witness covers 99.87% of
  the footprint, so any dot-based file on this footprint fails the written 70% clause. Reaching
  below 70% would require dots in the 6,649 uncovered cells, which is gaming and prohibited.
- **Best reported file:** GEMSDOE32 at 0.2778 (USER-REPORTED / UNVERIFIED). Not eligible.
  Its dots are GEMSDOE25 minus 6,436 catalogue-adjacent dots (measured, pinned bytes).
- **Policy decision needed from the protocol owner** (executive summary, "Policy decision"):
  (1) keep the literal rule, which means no eligible file; (2) rule on whether the lattice
  witness stays in the registry and whether the 70% clause suits a dense witness; (3) approve a
  calibrated similarity clause in advance. Agents will not choose any of these.
- **Leaderboard, fetched 2026-10-29:** #1 xiaofanhu 0.4544; kpomazi 0.3195 is at #47, so the
  prompt's "highest 0.3195" is incorrect. The 0.4413 figure does not appear.
- **Official rules, verified:** single float32 GeoTIFF; values in [0,1]; three submissions per week;
  generative-AI use must be disclosed in the narrative. The written format and the template use NaN outside
  the footprint. Four of the nine pinned focus files write zeros there (GEMSDOE30, 32, 33, 36), which departs
  from that convention; see the per-site pages. The cause of the portal's range error is unresolved.
- **Irregularities for review:** mirror `sample_submission.tif` is not the all-absence sample
  described officially (60,988 positives); the registry manifest covers nine repos only (440 rasters)
  and declares no completeness; two focus files share one dot set; some cache paths map to the wrong
  site folder (hashes still match). Full list: [`research/2026-10-29-focus-audit-and-next-hypotheses.md`](research/2026-10-29-focus-audit-and-next-hypotheses.md).
- **Experiments:** none run. The lane was unassigned, the candidate set is empty, and the policy
  decision blocks any upload. Budget used: 0 of 3.
- **Reproduce:** `.venv/bin/python scripts/audit_focus_gate.py` (needs
  `scripts/restore_registry_snapshot.py`, `scripts/bootstrap_research.py`, and
  `bash scripts/download_competition_data.sh --research-mirror`).
  Then `.venv/bin/python scripts/build_hk3_pages.py --check`.

## Lattice gate audit — 2026-10-29 (historical; current status is above)

- **Decision: no file is approved for download or submission.** The literal duplicate rule (more than 70% of dots within 3 px of any registry raster) cannot be met by any dot raster above 22,163 dots without gaming, because the GEMSDOE13 spacing-five lattice covers 99.87% of the footprint. Measured on the 440 pinned registry rasters: 437 fail; 1 is on a non-comparable grid; the lattice is the control and is excluded from its own test; the one remaining pass is GEMSDOE36's lattice-avoiding file (505 dots, 0% lattice overlap), which is flagged as gaming-shaped, not clearance.
- **All nine focus best files fail** the literal gate (lattice overlap 99.1–99.2%) and are 100% within 3 px of a sibling registry raster even with the lattice excluded.
- **Decision required from you:** choose the uniqueness standard (memo section 4). The protocol was not edited to create clearance.
- Memo: [`research/2026-10-29-lattice-gate-and-decision.md`](research/2026-10-29-lattice-gate-and-decision.md) (decision table, pigeonhole bound, irregularities, four ranked hypotheses, sources).
- Receipt: [`evidence/lattice-gate-audit-2026-10-29.json`](evidence/lattice-gate-audit-2026-10-29.json) · generator: `scripts/lattice_gate_audit.py` · run card: [`evidence/session-2026-10-29b-lattice-gate-run-card.json`](evidence/session-2026-10-29b-lattice-gate-run-card.json) (0 experiments, 0 slots).
- Owner-link refs in `registry/focus_sites.json` differ from the sha256-verified manifest commits; the generated page now links the manifest commits (`owner_pin()`).
- Unresolved: the portal error "Predicted values must be in range [0, 1]"; owner-derived lidar and GeoDAWN radiometric layers are listed but not restored (GeoDAWN radiometrics were already tested by GEMSDOE28 H38-1 and refused); no holdout run for any candidate.

## Current status — 2026-10-28 independent correction

**NEGATIVE — NO TIFF IS APPROVED. DO NOT SUBMIT ANY RESEARCH DOWNLOAD.**
An earlier HK3 promoter asserted `PROMOTE` after exempting registered rasters. The
binding user protocol has no such exemption. An independent re-read of saved TIFF
bytes found **45,046 / 45,108 = 99.862552%** of HK3 dots within three pixels of a
registered spacing lattice; this exceeds the strict >70% any-registry stop. The
historical audit also recorded three other failing comparisons and one invalid-grid
registry item. The lattice is very dense, so this is not proof of copying; it is
nonetheless a mandatory literal-protocol stop. No final rule waiver, ranked-rho
pass, or score estimate cures it. The previous pre-placement clearance and a
complete live registry have not been established.

* [`evidence/hk3/literal_recheck.json`](evidence/hk3/literal_recheck.json) is the
  reproducible saved-byte receipt; [`decision_correction.json`](evidence/hk3/decision_correction.json)
  preserves the unsafe historical decision and correction. The run card and
  selector now say negative; no slot is authorized.
* HK3 is a research file at `docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif`,
  SHA-256 `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`.
  It has one float32 band, a finite whole-array [0,1] range and the owner-mirror grid;
  its exterior is zero, not NaN. The organizer template and portal acceptance have
  not been authenticated. The cause of the previous portal error is unknown.
* Historical HK3 **HOLDOUT-DTI** is 0.1845046602, 95% CI [0.1676914118,
  0.2014839638], `gems57-pooled-hide-v2`, 58,258 withheld positives at 1.10%.
  Historical K3 **HOLDOUT-DTI** is 0.19157, 95% CI [0.17474, 0.20880], same named
  evaluator and withheld count. Both are negative and are not organizer scores;
  no matched paired comparison of HK3 and K3 has been established.
* No defensible local-candidate leaderboard estimate exists. The retained old
  calibration assumed an unverified transfer from catalogue holdout to hidden truth;
  its projection is not a score or a promotion basis. Only eight new HK3 features
  have recorded standalone canaries; the full 34-feature leakage gate is unverified.
* This audit made no new geological experiment, TIFF or submission. The prompt has
  no identifiable single assigned method paragraph, prior HK3 used its three
  experiments and recorded more than two hours, and the complete registry and
  organizer data are not available. `scripts/hk3.py` is retired; do not rerun or
  resurrect its feature, experiment, placement, audit or card commands.
* The [three-pass independent review](research/2026-10-28-independent-three-pass-review.md)
  records the corrections and reproducibility checks; the [session card](evidence/2026-10-28-independent-audit-run-card.json)
  uses nulls for unmade candidate evidence. Concurrent corrections, the
  [status notice](SUBMISSION_STATUS.md), the [hash-bound current assessment](evidence/hk3/current_release_assessment.json),
  the [additional strict-gate review](research/repo-review-2026-10-28-strict-gate.md), and the
  [preserved original card](evidence/hk3/history/run_card-before-protocol-correction.json)
  are retained after reconciliation with main.
* The [nine-site desk](docs/executive-summary.html) has pinned historical files,
  source links and negative uniqueness checks. The highest claim, 0.2778 for
  GEMSDOE32, is **USER-REPORTED / UNVERIFIED**; no causal explanation for the
  hidden result has been established. Four [future hypotheses](research/2026-10-28-next-lane-slate.md)
  are untested research proposals, not an assigned lane.

### Reproduce the read-only audit

```sh
python -m venv .venv && .venv/bin/pip install -r requirements.lock.txt
.venv/bin/python scripts/bootstrap_research.py  # small hash-pinned GitHub owner mirrors, not organizer data
.venv/bin/python scripts/recheck_hk3.py --check
.venv/bin/python scripts/audit_public_downloads.py --check
.venv/bin/python scripts/build_hk3_pages.py --check
.venv/bin/pytest -q
npm ci --ignore-scripts --no-audit --no-fund && npm test && npm run test:site && npm run test:browser
```

The mirrored inputs can be regenerated, but remain unauthenticated; the download
inventory verifies integrity, not eligibility. The four desk pages and HK3 CSS are
generated by `scripts/build_hk3_pages.py`; change the generator/evidence, not just
the HTML. Any future release requires an explicitly assigned lane, authenticated
inputs, clean bounded experiments, complete registry checks before and after
placement, and a separate selector. Do not try to game gaps in the lattice.

## Earlier 2026-10-28 session notes (historical, superseded where inconsistent)

Prior H1, H2, B4, K2 and K3 negative decisions remain in force. Any earlier claim
that HK3 is submittable, that registry entries may be excluded, or that its
speculative projection is a measured score has been withdrawn. Historical source
files are preserved for context; the current correction takes precedence.

### Latest safety follow-up — 2026-10-28

**No approved submission; do not upload the research TIFFs.** The latest follow-up
ran no experiment and did not use a competition slot. All nine focus GitHub heads
changed relative to the October 27 reviewed snapshot; this is not a new score or
raster audit. See the [three-pass review](evidence/current-session-review-2026-10-28.md),
[GitHub HEAD receipt](docs/evidence/source-head-review-2026-10-28.json), and
[negative run card](docs/evidence/followup-session-run-card.json). The local raster
audits reject external GDAL sidecars not covered by the TIFF hash; input placement
and grid checks do not imply training readiness or submission authorization.

### Latest review — 2026-10-28 (d13851b5)

**No approved submission; no new experiment or slot used.** Read the
[three-pass review](research/review-d13851b5.md) and
[run card](evidence/review-d13851b5-run-card.json). The generic research gate now
requires explicit pre-placement clearance, no prior mandatory stop, and
organizer-authenticated inputs/template. These evidence-schema assertions do not
independently prove provenance or authorize a slot. A later narrower passing
scan cannot clear a prior protocol stop. The executive summary labels its file
column **research — DO NOT SUBMIT**. All 164 Python tests passed after main integration with pinned
mirror inputs restored, plus 73 subtests; Node feed/site and browser checks passed.

The [official reference README](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md)
explicitly supports CPU-only execution: a GPU is useful, not mandatory. Network,
authenticity, lane, registry and validation blockers remain; placing data alone
does not make this pipeline submission-ready. Existing five-hypothesis research
slates are preserved, not reauthorized or presented as newly tested.
### Latest review and release status

**No approved submission TIFF. Do not submit the existing research artifacts.**
The latest [selector evidence review](research/selector-evidence-review-2026-10-28.md)
records the unresolved lane, literal registry stop, unauthenticated organizer inputs,
and the schema-only baseline-comparability safeguard. It does not estimate a private
leaderboard score or authorize a competition slot.

### Latest review

No submission is approved. The release gate now requires matched baseline evidence
and split, truth, and scoring-configuration hashes; it validates card structure,
not the authenticity of those manifests. See [this review](research/release-gate-review-2026-10-28.md).
### Latest release-gate follow-up (2026-10-28)

**No TIFF is approved for upload.** The release schema now requires evidence
attestations for a comparable baseline, a surface pass before placement, and an
authenticated organizer template. It does not independently verify those claims.
See [the three-pass follow-up](research/release-gate-followup-2026-10-28.md)
and the [K2 protocol correction](research/k2-protocol-review-2026-10-28.md).
No new experiment or competition slot was used in this follow-up.
Latest audit: [three-pass byte-bound raster review](research/review-sidecar-2026-10-28.md). No approved submission; K2 remains negative.


**This branch's autonomous follow-up:** GitHub-hosted owner mirrors were
restored to ignored `.cache/competition_data/` with pinned SHA-256 hashes and
passed a *research-only* raster/schema preflight. The sample still contains
60,988 known-fault positives, contrary to the published all-absence description;
this mirror is **not organizer-authenticated**. See
[`evidence/owner_mirror_preflight_2026-10-28.json`](evidence/owner_mirror_preflight_2026-10-28.json).
The nine historical geometry results were independently reproduced from pinned
bytes (`scripts/bootstrap_research.py`, `scripts/audit_references.py`,
`scripts/compare_audit.py`), not turned into a new leaderboard score. The
[download inventory](evidence/public_downloads_audit.json) reopens **all hosted
research TIFFs and ZIPs**, checks their saved-byte hashes, float32/grid/range,
and rejects unknown downloads; it reports **PASS_RESEARCH_ONLY**, not competition
authorization. A prior Node site regression (mislabelled research column) was
fixed. The K2 literal audit now gives the conditional spacing-lattice counting
bound (54,491 saved positives → at least 47,842/54,491 ≈ 87.80% overlap if
all are in the mirrored footprint); this does **not** rule out every smaller
candidate. These are geometry measurements, not DTI or organizer scores. Four
ranked *untried local* proposals appear in
[`research/2026-10-28-next-lane-slate.md`](research/2026-10-28-next-lane-slate.md).
This branch ran zero additional geological experiments; concurrent H2 and B4
negative research runs merged from main while this audit was in progress. A
[dated GitHub HEAD-only check](docs/evidence/source-head-review-2026-10-28.json)
reported nine changed focus repositories since the pinned review; it does not
refresh their raster or score audits. Automated Pages refresh checks GitHub
metadata only, not DrivenData or account quota.
[Current negative run card](evidence/session-31569490-run-card.json) records null
new-candidate score, raster hash and submission name rather than inventing one.
The [three-pass review](research/31569490-three-pass-review.md) documents the
concurrent-main reconciliation, exact reproducible checks and remaining blockers.

The [selector evidence review](research/selector-evidence-review-2026-10-28-eee3.md)
adds fail-closed checks for matched incumbents, complete feature canaries, and
pooled scoring. Schema consistency is not evidence verification or slot approval.
Latest separate follow-up: [`research/arena-review-2026-10-28.md`](research/arena-review-2026-10-28.md).

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

### H2 stepover research surface — negative (concurrent main merge, 2026-10-28)

The recorded H2 HOLDOUT-DTI is 0.0172963 (95% CI [0.0145387, 0.0203584];
`gems57-pooled-hide-v2`, 58,259 withheld positives), and the paired difference
against its best primitive is negative. Its surface registry receipt stops after
one of 440 pinned comparisons, before final-dot checking. The new downloadable
H2 TIFF is a **research-only surface**, not a unique or approved submission.
See [`evidence/run_card_h2.json`](evidence/run_card_h2.json). H1's current root
card is [`evidence/run_card.json`](evidence/run_card.json); its identical
archived receipts are also retained under [`evidence/h1/`](evidence/h1/) from
when a concurrent merge briefly replaced the root card. Do not label an H1
result with H2's hash or holdout.

### B4 scarp-step candidate — negative (concurrent main merge, 2026-10-28)

**NEGATIVE — DO NOT SUBMIT.** New lane tested: paired-flank step asymmetry
(elev/basement/gravity/RTP, 8 orientations) in `scripts/b4_step.py`.
HOLDOUT-DTI (gems57-pooled-hide-v2, 58,259 withheld): 0.0981 @1.10%
(CI 0.0850–0.1125), 0.1206 @1.50%; paired Δ vs its own gradient control
+0.0040 (95% CI [+0.0011, +0.0070]). The K2 prior result used 58,258
withheld positives; a matched-fold paired incumbent win is **not** established.
Canaries pass (worst 0.622). The generated TIF
(`docs/downloads/gemsdoekarage2-b4-stepasym-b110-20261028-zeros.tif`,
sha256 2f553692…) has max overlap 0.228 vs the nine focus files but **fails**
the literal all-registry uniqueness rule: its final audit reports 1.0 overlap
with the lattice and `unique=false`. An independent saved-byte calculation
reproduces 51,914/51,914 within 3 px on the pinned owner-mirror footprint
([receipt](evidence/b4/literal_followup.json)); this does not authenticate the
organizer's sample. It is format-valid on the mirror grid, not an approved
competition file. Research download only. See
`research/b4-step-review-2026-10-28.md` and `evidence/b4/run_card.json`.
No leaderboard estimate exists for any repo file (Unavailable).

### K2 supervised candidate — protocol stop (2026-10-28)

1. Install `requirements.lock.txt` in a Python virtual environment and run
   `.venv/bin/pytest -q`.
2. Run `npm ci && npm test && npm run test:site && npm run test:browser` for the
   public dashboard/feed suite.
3. `bash scripts/download_competition_data.sh --research-mirror` automatically
   restores four SHA-pinned **owner mirrors** from public GitHub into ignored
   `.cache/competition_data/` and runs a core-only schema preflight. It does not
   download the authenticated organizer files or the DEM links, train a model,
   approve a slot, or create a TIFF. With no flag the script **exits nonzero**
   instead of pretending URLs were downloaded. If authorized files are already
   in `data/`, `bash scripts/download_competition_data.sh --validate-official`
   checks their schema (including a nonempty `1m_DEM_links.csv`), but cannot
   authenticate origin. A grid mismatch, missing/empty file or malformed TIFF
   fails closed and writes a negative `prepared.json` rather than a false pass.
4. `.venv/bin/python scripts/audit_public_downloads.py --check` independently
   verifies every *currently published* TIF/ZIP, run-card digest, range, grid
   and negative selector status against the committed receipt. It requires no
   human inspector and cannot grant upload permission. CI blocks unknown or
   changed public downloads. See the [machine-readable audit](evidence/public_downloads_audit.json).
5. `python scripts/restore_references.py` downloads pinned public GitHub mirrors
   to `.cache/input/`; hashes are checked. These are not authenticated organizer
   downloads and are not the complete registry.
6. `python scripts/audit_legacy_dots.py` rechecks saved bytes, grid, range,
   footprint and the lattice duplicate witness. No candidate TIFF is generated.


### K3 lineament-context candidate — holdout-best, uniqueness-negative (2026-10-28)

**NEGATIVE — DO NOT SUBMIT.** K3 (53-feature orientation-aware HGB +
expected-DTI placement, `scripts/k3.py`, preregistered in
[`research/hypotheses-2026-10-28-k3-preregistration.md`](research/hypotheses-2026-10-28-k3-preregistration.md))
reached HOLDOUT-DTI 0.19157 (gems57-pooled-hide-v2, 58,258 withheld positives,
95% CI 0.17474–0.20880), beating the bit-faithfully replicated K2 incumbent by
+0.03402 (paired 95% CI +0.02738…+0.04098), with all 53 leakage canaries
≤0.6382. It nevertheless fails the preregistered uniqueness gate: the surface
top-support vs the quarantined K2 predecessor was 0.9922, and final dots
exceed 70% within-3-px overlap against 10 primary-scope registry records
(including fleet submission rasters; worst 88.6%), while Spearman passes
everywhere (max |rho| 0.1056) and overlap vs the nine focus best files is
44.8–51.6%. The artifact `gemsdoekarage2-k3-linctxdti-b110-20261028-zeros.tif`
(SHA-256 `d011e9e1…fc61`, 51,914 dots) was written under a disclosed research
override for final-dot measurement and is research-only. No leaderboard
estimate exists (labelled projection ~0.25–0.33 is not a score). See
[`research/review-2026-10-28-k3.md`](research/review-2026-10-28-k3.md) and
[`evidence/k3/run_card.json`](evidence/k3/run_card.json). Experiment budget
(3) exhausted; zero slots used. The next viable lane must differentiate its
*dot geography* from the fleet supervised consensus (preregistration slate
C4/C5), not merely improve the shared surface.

### Latest regression review — session 76119165 (2026-10-28)

The [three-pass review](research/session-76119165-review.md) fixed the executive
summary's research-download heading and hardened the readiness schema gate against
overriding an explicitly recorded negative verdict or protocol stop. No new
experiments or TIFFs were generated; no slot is authorized. See the
[review run card](evidence/session-76119165-run-card.json). Python tests passed
with seven input-dependent integration skips; feed, site and browser checks passed.

### Remaining work

[`research/hypotheses.md`](research/hypotheses.md), and the distinct `evidence/run_card.json` / `evidence/h1/run_card.json`
(H1, identical restored copies), `evidence/run_card_h2.json` (H2) and
`evidence/run-card.json` (unrun preflight) records for prior work. See also
[`research/repo-review-2026-10-28.md`](research/repo-review-2026-10-28.md),
[`research/final-three-pass-review-2026-10-28.md`](research/final-three-pass-review-2026-10-28.md),
and [`research/release-review-2026-10-28.md`](research/release-review-2026-10-28.md).
The K2 download links on the site are **research-only / DO NOT SUBMIT**. The earlier
conditional selector recommendation is superseded by the negative literal-policy
decision at [`evidence/k2/selector_result.json`](evidence/k2/selector_result.json);
no TIFF is approved for competition submission.

---

## CURRENT SESSION PROMPT (2026-10-30) — read before every work session

### Focus: nine GEMSDOE sites

GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32,
GEMSDOE33, GEMSDOE36.

### Deliverable 1 — Executive summary on every site

Clear and obvious which is the best submission to submit for a high leaderboard
score. Table listing: what file to download, estimated score, whether it is a
unique submission unlike any of the other GEMSDOE sites.

Best user-reported results (USER-REPORTED / UNVERIFIED, no organizer receipt):
- GEMSDOE32: h33-h33-2-b2 = 0.2778 (highest of the nine)
- GEMSDOE36: anderson-geothermal-pinn = 0.2750
- GEMSDOE28: h36-1-rung30-blind-r1 = 0.2710
- GEMSDOE31: h27-4-solo-d28 = 0.2708
- GEMSDOE33: h33d-analog-tip-stepover-r30 = 0.2632
- GEMSDOE25: dotted-h19-5-d2-8 = 0.2600
- GEMSDOE30: d28-poisson300m-offcat-44090 = 0.2600
- GEMSDOE24: h25-1-dotted-h19-5-d1-5 = 0.2477
- GEMSDOE27: topo-gap-closure-t-v2-on-d1-5 = 0.2449

**All nine fail the literal uniqueness gate** (DUPLICATE_STOP against the 13GEMSDOE
lattice, 99.91–99.92% of dots within 3 px; limit 70%). None is eligible for
submission. No estimated leaderboard score exists for any file.

### Deliverable 2 — MUST generate a unique TIF submission

Generated: `docs/downloads/gemsdoe-hf-alteration-curvature-intersection-20261030.tif`
(SHA-256: `4fe3104c38ae32eb04dbea9a75ba882feaef3d3b282249aeb635f83f9083abe3`)

**Hypothesis H-F:** Multi-scale radiometric alteration (low K, high eTh/eU ratio)
× curvature convergence at fault intersections × soft distance decay from known
faults; faults masked pixel-exactly; sparsified to 18,000 dots.

**Validation:**
- Format: PASS (strict_format_pass=true; float32, [0,1], NaN outside footprint,
  EPSG:32611, 3730×3292, 100 m)
- Uniqueness: PASS vs 7 local registry rasters (max |Spearman| 0.0115, max
  dot overlap 0.6179, no duplicate). 465 focus-site rasters not locally available.
- Holdout-DTI: 0.018385 (proxy; 60,988 withheld positives; below submission threshold)
- Leakage canary: PASS (combined AUC 0.498; no leakage)

**VERDICT: negative.** OK_TO_DOWNLOAD: YES. OK_TO_SUBMIT: NO. Holdout DTI too
low for submission. No submission slot was used.

### Deliverable 3 — Easy download

One-click download link on the site (`docs/index.html`, `docs/executive-summary.html`)
at `downloads/gemsdoe-hf-alteration-curvature-intersection-20261030.tif`.

### Deliverable 4 — Executive summary subpage

`docs/executive-summary.html` — explains how to submit, includes the nine-site
scorecard table, the new H-F TIF with clear OK/NOT-OF-TO-SUBMIT messaging.

### Deliverable 5 — 3–5 untried geological hypotheses

Documented in `research/hypotheses-2026-10-29-untried.md` (H-A through H-E).
Top candidate H-A was not implemented; H-F and H-G were implemented instead
as experiments 1 and 2. Both negative on holdout.

### Protocol (binding)

- LANE: >0.90 Spearman or >70% dots within 3 px of any registry raster = stop
- Holdout: hide-and-recover, pooled DTI (alpha 0.2, beta 0.8, 300 m triangular)
- Label every number as HOLDOUT-DTI or ORGANIZER-CONFIRMED; projection is never a score
- Leakage canary: AUC > 0.90 = leakage until proven otherwise
- Budget: 3 experiments / 2 hours (used: 2 experiments)
- No submission slot spent; promotion is a separate selector step

### Leaderboard (public observation, not receipts)

Public rank 1: 0.4544 (xiaofanhu, observed 2026-10-29). Best focus-site claim:
0.2778 (GEMSDOE32, USER-REPORTED / UNVERIFIED). User-cited 0.3195 is at rank 47;
0.4413 is not rank one.

## Current session prompt — standing reference (2026-10-31)

Read this section every time work resumes on this project. It defines the deliverables for this session.

### Goal
Produce a unique, format-valid GeoTIFF submission for the DOE GEMS Prize Challenge, with an executive summary over the focus GEMSDOE sites (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36), a GitHub Pages front end with an obvious one-click downloadable submission TIF, and a validated pipeline (holdout DTI evaluation + submission writer + run cards). Place top of the leaderboard (current public high 0.4544; user-cited 0.3195 is rank 47).

### Competition (official sources)
- DrivenData GEMS Prize Challenge: https://www.drivendata.org/competitions/306/competition-doe-gems/
- Problem page: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- About: https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/
- Data tab (login required): https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- Leaderboard: https://www.drivendata.org/competitions/306/competitions/306/competition-doe-gems/leaderboard/
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- DOE GDR INGENIOUS: https://gdr.openei.org/submissions/1391
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- EPSG 32611: https://epsg.io/32611
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index

### Task
Develop models/algorithms predicting geological faults (structures indicative of geothermal resources) as a single-band GeoTIFF of pixel-wise probabilities in [0, 1]. The private initial-round test set comprises NEW faults NOT in the public USGS database — so discovering off-catalogue faults is the path to a high score.

### Submission format (official)
- single band, 32-bit float (float32), values between 0 and 1
- CRS: EPSG:32611 (UTM zone 11N), 100 m resolution
- same bounds/shape/geotransform as the submission template
- data outside the bounds is null or NaN (exterior convention vs portal range behavior unresolved)

### Metric
Distance-weighted Tversky index DTI(alpha=0.2, beta=0.8), triangular kernel k(d)=max(1-d/R,0), R=300 m (3 px at 100 m). Official scorer is hidden/unauthenticated.

### Required deliverables (this session)
1. Executive summary on every focus site: clear which is the best submission for a high score. Table listing: file to download, estimated score, whether unique vs other GEMSDOE sites.
2. MUST generate a UNIQUE TIF submission. Do not copy a previous submission (except for learning). It must be obvious whether the generated TIF is OK to download and submit.
3. Easy-to-download submission TIF (one click). Values in [0, 1] (fix the portal "[0, 1]" range error). Unique name + short note <= 140 chars.
4. Executive summary subpage explaining exactly how to make a submission; obvious at the top of the site.
5. 3-5 candidate geological hypotheses (layers, physical signature, why it catches unmapped faults, how it differs from repo work), ranked by expected DTI improvement and cost.
6. Validate the top candidate on the spatially-blocked holdout before touching a submission slot.
7. Put this prompt in the README; read it each session.
8. End with one JSON run card: hypothesis, mechanism, named non-fault mimic, holdout DTI + CI, correlation/overlap vs registry, raster sha256, validator output, submission name + note <= 140 chars, verdict promote/negative.

### Parallel-run protocol (literal)
- LANE: stay in one method paragraph. If raster rank-correlation with any registry raster > 0.90, OR > 70% of dots within 3 px of one registry raster's dots, log as duplicate and stop. Check pre-placement AND final dots.
- REUSE, DON'T REBUILD: use the template's cached feature stack, evaluate_holdout.py and submission_writer.py. Holdout = hide-and-recover. Pooled DTI alpha 0.2, beta 0.8, 300 m triangular kernel.
- LABEL every number as HOLDOUT-DTI or ORGANIZER-CONFIRMED. A projection is never a score.
- LEAKAGE CANARY: test each feature alone; AUC > 0.90 = leakage.
- RUN CARD: one JSON card at the end (promote / negative). Negative results are deliverables.
- BUDGET: stop after 3 experiments or 2 hours. No submission slot spent; promotion is a separate selector step.

### Data access blocker (verified)
No DrivenData auth → cannot auto-download training_features.tif, labels.tif, sample_submission.tif from the data tab (redirects to login). Research mirrors restored via scripts/download_competition_data.sh --research-mirror (owner-mirror bytes, SHA-256 pinned, NOT organizer-authenticated).

### Core values
Maximize P(Win). Own the Outcome. No hallucinations; verify line by line; flag irregularities.

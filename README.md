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

## Current status (2026-10-28 review correction) — read before doing anything

**NO APPROVED SUBMISSION — DO NOT SUBMIT any TIFF currently in `docs/downloads/`.**
The HK3 raster remains available only as a research/reproduction artifact:
`docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif`
(SHA-256 `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`). Its
historical run card still records the earlier experiment's PROMOTE verdict; it applied an
exception to the literal 70% / 3 px rule. That exception is not allowed by the current
parallel-run protocol. The current, controlling assessment is
[`evidence/hk3/current_release_assessment.json`](evidence/hk3/current_release_assessment.json);
the generated Pages badge and download guidance derive from this assessment and the current
negative selector result. The earlier selector receipt is preserved at
[`evidence/hk3/selector_result-historical-promote.json`](evidence/hk3/selector_result-historical-promote.json).
No slot was spent and no score is ORGANIZER-CONFIRMED.

| Quantity | Value | Label |
|---|---|---|
| Historical HK3 vs same-session refitted K2 at 1.10% budget | 0.1845 [0.1677, 0.2015] vs 0.1575 [0.1417, 0.1737]; paired Δ +0.0270 [+0.0206, +0.0337] | HOLDOUT-DTI, `gems57-pooled-hide-v2`, 58,258 withheld positives |
| Current repository holdout comparator | 0.1916 [0.1747, 0.2088] for K3 vs historical HK3 0.1845 [0.1677, 0.2015]; no paired cross-session test | HOLDOUT-DTI, same evaluator and 58,258 withheld positives |
| Historical estimated organizer score | 0.263–0.286 | LEADERBOARD-CALIBRATED ESTIMATE — never a score; not submission authorization |
| Best user-reported focus-site result | 0.2778 (GEMSDOE32 B2) | USER-REPORTED / UNVERIFIED |
| Final-dot overlap with registry | 99.8626% within 3 px of the r13 lattice, above the literal 70% stop | REGISTRY-OVERLAP AUDIT — DUPLICATE; stop |
| Registry scan completeness | 452/453 expected entries checked | INCOMPLETE — cannot establish global uniqueness |
| Local raster format | no NaN; values in [0,1]; matches the pinned owner-mirror grid | LOCAL FORMAT/RANGE CHECK only; no organizer template authentication or portal receipt |

The experiment and historical metrics are preserved; the current release decision is negative.
Do not regenerate or place additional dots in the exhausted HK3 lane. See
[`research/repo-review-2026-10-28-strict-gate.md`](research/repo-review-2026-10-28-strict-gate.md)
for the three-pass review, hypotheses slate, limitations, and verified repository findings.

**Concurrent K3 lane (merged from main, 2026-10-28):** K3 (`gemsdoekarage2-k3-linctxdti-b110-20261028-zeros.tif`,
53-feature lineament-context HGB) reached HOLDOUT-DTI **0.1916** [0.1747, 0.2088] at the same
1.10 % budget — *higher than HK3's 0.1845* (intervals overlap; same folds/evaluator; no paired
test across sessions) — but its verdict is NEGATIVE: the surface failed the pre-placement gate
against K2 (0.9922 top-support overlap) and its final dots exceed 70 % within 3 px of ten
registry records (worst 0.886). HK3's 3 px catalogue apron and 3 px dot separation are what
keep its overlaps ≤ 48.4 %. So: K3 is the holdout-best file in the repository, HK3 is the best
*submittable* file, and the holdout incumbent for any next lane is K3's 0.1916, not HK3's.

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
* **Current user protocol overrides historic tiers:** any rank-correlation > 0.90 or > 70 %
  of candidate dots within 3 px of any registry raster is a duplicate stop. No exception for
  a lattice, dense surface, control arm, or unsubmitted artifact. Check the raster surface
  before placement and final dots after placement; a missing registry item also prevents
  uniqueness clearance. Historical U1/U3/U4 summaries do not replace this literal test.
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

### Historical reproduction (do not rerun the exhausted HK3 experiment lane)

Do not rerun feature/holdout/placement commands from `scripts/hk3.py`: that lane's budget
is used, and its current artifact fails the literal registry gate. To inspect preserved
results, read the JSON receipts. To regenerate/check only the pages and saved-byte inventory,
install the pinned requirements and run `scripts/build_hk3_pages.py` plus
`scripts/audit_public_downloads.py`; these checks do not authorize a submission. The full CI
chain is in
   `.github/workflows/pages.yml`: `assess_release.py`, `audit_k2_release.py`,
   `review_k2_release.py`, `build_site.py`, `build_field_notes.py`,
   `build_audit_site.py --check`, `build_hk3_pages.py --check`, `git diff --exit-code -- docs evidence`,
   `pytest -q`, `npm ci && npm test && npm run test:site` (`npm run test:browser` locally).

### Remaining work (for the next session)

1. **No selector/upload action is authorized for the current TIFF.** Do not use a competition
   slot. First reconcile the literal pre-placement/final uniqueness stop and obtain a complete,
   current registry inventory without exempting any raster.
2. Authenticate the competition data/template and clarify the outside-footprint convention;
   current local checks use public owner mirrors and do not establish portal acceptance.
3. Reconstruct the strongest comparable incumbent on the same visible-only, buffered holdout.
   The current repository's highest recorded holdout is K3's 0.1916, but K3 itself is negative
   under uniqueness; a future candidate must compare against it with a paired, same-protocol CI.
4. Only after lane authorization and registry/provenance gates, preregister at most three
   experiments. See `research/repo-review-2026-10-28-strict-gate.md` for candidate hypotheses.
5. Limitations: no organizer receipt or authenticated score; the user-provided leaderboard
   values conflict; the public registry snapshot is incomplete and not the organizer's full
   submission history; catalogue holdout cannot guarantee transfer to hidden 1 m lidar labels.

Research notes: [`research/hypotheses-2026-10-28-hk3.md`](research/hypotheses-2026-10-28-hk3.md)
(this lane), [`research/k2-protocol-review-2026-10-28.md`](research/k2-protocol-review-2026-10-28.md),
[`research/independent-review.md`](research/independent-review.md),
[`research/findings-2026-10-27.md`](research/findings-2026-10-27.md),
[`research/hypotheses.md`](research/hypotheses.md).

## Earlier 2026-10-28 session notes (concurrent branches, merged; reconciled with current status)

These sections preserve earlier independent reviews. Their negative findings (H1, H2, B4,
K2, and K3 DO NOT SUBMIT) remain valid. An earlier HK3 run-card/selector assessment applied
an exception to the literal registry stop; the current assessment supersedes that guidance.
Do not read historical PROMOTE or estimate text as current upload authorization.

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

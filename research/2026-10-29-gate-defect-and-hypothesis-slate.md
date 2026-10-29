# 2026-10-29 · Gate defect, the 0.2778 question, verified sources, and the next hypothesis slate

**Status: NO FILE IS APPROVED FOR SUBMISSION. No new TIFF was generated, no experiment was run, and no weekly slot was used.**
The deciding evidence is [`evidence/uniqueness-gate-calibration-2026-10-29.json`](../evidence/uniqueness-gate-calibration-2026-10-29.json). The Pages desk shows the same finding in its new section [“Why no new file can be submitted yet”](../docs/executive-summary.html).

Labels used below: **HOLDOUT-DTI** (local catalogue proxy with evaluator, withheld count and CI), **ORGANIZER-PUBLISHED** (public leaderboard snapshot, not a submission receipt), **OWNER-REPORT / USER-REPORTED** (no organizer receipt), **VERIFIED-FILE** (bytes read and measured in this session), **DERIVED** (my arithmetic from verified inputs), **UNVERIFIED** (not established here).

---

## 1. Answer: is any file OK to download and submit?

| File | Download to submit? | Reason (verified in this session unless stated) |
|---|---|---|
| Any TIFF in this repository (HK3, K2, K3, B4, H1, H2, irregular-dot file) | **NO** | Each fails the literal uniqueness gate or has no defensible uniqueness receipt. Prior negative decisions stand. |
| GEMSDOE32 “0.2778” file (`gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`) | **NO** | The score is OWNER-REPORT. The owner page itself says “already submitted – do not resubmit”. Its bytes (37,654 positive cells, sha256 `c55bafc4…7ab6fa9`, VERIFIED-FILE) fail the literal gate at 99.92% overlap with the lattice witness. It is not in this repo. |
| Any new file generated under the current literal rule, if it has more than **22,163** positive cells | **NO, by arithmetic** | Pigeonhole bound below (section 3). This holds for any content. |
| Any new file under a changed rule (Option B or C in section 3) | **Not yet** | Needs your explicit approval, the full registry scan, a holdout win, and a weekly-slot selector. |

**Bottom line:** the literal rule makes every competitive-size dot file ineligible, including random dots that copy nothing. The fix is a rule decision. Generating another file now would only produce another file the gate rejects.

---

## 2. Why the owner’s 0.2778 file scored what it did (and whether we can beat it)

### 2a. Verified facts (set-level, from bytes)

| Claim | Check | Result |
|---|---|---|
| GEMSDOE32 has 37,654 dots | Read `GEMSDOE32.tif` from the pinned owner mirror (ref `73485f27…`) | **VERIFIED-FILE**: 37,654 positive cells, all values 0/1, finite zeros outside the footprint |
| It is a strict subset of the D2.8 (GEMSDOE25 / GEMSDOE30) file | Set difference on positive cells | **VERIFIED-FILE**: GEMSDOE32 ⊂ GEMSDOE25 (44,090 cells), 6,436 removed; GEMSDOE32 ⊂ GEMSDOE30, 6,436 removed |
| Also a subset of GEMSDOE31 and GEMSDOE36 | Same method | **VERIFIED-FILE**: 2,545 removed from GEMSDOE31 (40,199 cells); 1,200 removed from GEMSDOE36 (38,854 cells) |
| The removal is a “catalogue-apron pruning” operation | `evidence/champion_forensics.json` (this repo’s forensic audit of the owner bytes) | **REPO AUDIT**; the owner page’s own wording was not read in this session (only its first fetched chunk), so the removal rule is UNVERIFIED |
| Owner score 0.2778 | GEMSDOE32 page | **OWNER-REPORT** with no submission-page receipt |

So the file cannot add any new location. Every gain relative to the D2.8 file has to come from **removing** dots. That is the only mechanism the file itself shows.

### 2b. Derived explanation (DERIVED, not established)

The official metric is DTI = TPw / (TPw + α·FPw + β·FNw), with α = 0.2 and β = 0.8 ([official problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)). Because α + β = 1, a linear approximation gives:

- A dot whose probability of being a hit is *a* adds roughly *a* to TP and *(1 − a)* to FP. It also removes *a* of FN.
- Its marginal effect on DTI is positive only when **a > α × DTI**.
- At DTI ≈ 0.2778, the break-even hit probability is about **0.2 × 0.2778 ≈ 0.056**.

If the two owner scores (D2.8 at 0.2600 and this file at 0.2778) came from the same scorer and labels, the 6,436 removed dots must have had hit rates below roughly 5.6%. That is a conditional inference. The real kernel is distance-weighted, so the linear model is only a first-order guide. **No hidden label set is available here**, so this cannot be confirmed.

### 2c. Can we beat 0.2778?

- **Not demonstrated.** No local holdout or organizer result shows a unique file above 0.2778.
- **The public leaderboard context matters.** The live page shows #1 at 0.4544, #2 at 0.3916, and #50 at 0.3167 ([leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/), fetched 2026-10-29). If 0.2778 is a public-test score, it would rank below #50 on this snapshot. Whether it is a public or private score is **UNVERIFIED**.
- **Pruning alone is not a strategy.** A pruned subset of an existing file is a near-duplicate under any sensible overlap test. A unique file needs better hit-probability ranking, and that has not been shown.

---

## 3. The central finding: the literal uniqueness gate is saturated

### 3a. Mechanism (read from code)

`scripts/check_uniqueness.py::check_comparator` marks a candidate DUPLICATE when `10 × matched > 7 × n`, where `matched` counts candidate positive cells within 3 px of any positive cell of the reference, and `n` is the candidate’s positive count. The reference here is the only lattice witness pinned in `research/reference-sources.json` (`inputs/lattice.tif`, 13GEMSDOE owner mirror).

### 3b. Measured with the shared comparator (VERIFIED-FILE / reproducible)

| Quantity | Value | Source |
|---|---|---|
| Footprint cells (template grid, EPSG:32611, 100 m) | 5,167,373 | receipt |
| Lattice positive cells in footprint | 206,895 | receipt |
| Footprint cells within 3 px of a lattice dot | 5,160,724 = **99.87%** | receipt |
| Footprint cells farther than 3 px | **6,649** | receipt; equals the vendored `saturation_certificate` (cross-check passes) |
| Uniform random dot sets, n = 100 / 10,000 / 22,163 / 37,654 (3 seeds each) | **every** set flagged; minimum overlap **99.82%** | receipt, `null_controls` |
| Nine historical focus files vs the lattice | **9 of 9** flagged; overlap 99.91%–99.92% | receipt, `focus_files_vs_lattice` |

### 3c. Pigeonhole bound (DERIVED, rigorous)

A candidate passes only if `10 × matched ≤ 7 × n`. Let `u = n − matched`, the number of candidate cells that are *not* within 3 px of the lattice. Then `u ≤ 6,649`, and the pass condition becomes `3n ≤ 10u`. So **n ≤ floor(10 × 6,649 / 3) = 22,163**.

Consequence: any candidate with more than 22,163 positive cells is a DUPLICATE under the literal rule, whatever it contains. The owner-reported 37,654-dot and 44,090-dot files, and our own research files, all sit far above that bound.

### 3d. Why this matters

- The gate cannot tell a copy from a non-copy for this witness. Random dots fail it. So the failure is not evidence of copying.
- The owner’s own GEMSDOE32 page applies the same gate and reports the same type of failure, for its H51 candidate (99.7% overlap with r13-lattice-s5). That is an irregularity across sites, not one project’s bug.
- The vendored `saturation_certificate` only declares a universal blocker when zero cells are uncovered. Here 6,649 are uncovered, so that certificate is correctly **not** universal. The size bound in 3c is the rigorous blocker instead.

### 3e. Options (decision needed; NONE applied)

| Option | What it does | Trade-off |
|---|---|---|
| **A. Keep literal** | No file above 22,163 positive cells is eligible | Effectively forbids the dot-count range of every competitive file |
| **B. Exclude the saturated witness** | Drop the lattice witness with a documented reason, keep all other literal checks (rho ≤ 0.90, ≤ 70% overlap vs every other registry raster) | Simple and transparent, but the rest of the registry must be complete before any file is eligible |
| **C. Null-calibrated test** | Compare overlap with the random-placement expectation for the witness, not with a fixed 70% | Most informative; needs a new, pre-registered criterion and review |

**Recommendation (for your decision, not applied):** B now, with C as the next methodological step. Any option needs your explicit approval. Under any option, a new file still needs the full registry scan and a separate weekly-slot selector.

---

## 4. Official sources checked this session (line by line)

| # | Claim | Source (fetched 2026-10-29) | Status |
|---|---|---|---|
| 1 | Leaderboard #1 **0.4544**, xiaofanhu, 34 submissions | [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | ORGANIZER-PUBLISHED (public test) |
| 2 | #2 cfld__ 0.3916 | same | ORGANIZER-PUBLISHED |
| 3 | #27 jay398144 **0.3326** | same | ORGANIZER-PUBLISHED |
| 4 | #47 kpomazi **0.3195** (the user’s “rank 27” is wrong) | same, chunk 2 | ORGANIZER-PUBLISHED |
| 5 | #50 kinneso_outlook 0.3167 | same, chunk 2 | ORGANIZER-PUBLISHED |
| 6 | Metric: distance-weighted Tversky, α = 0.2, β = 0.8, triangular kernel, R = 300 m | [problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | OFFICIAL TEXT |
| 7 | Format: single layer float32, values between 0 and 1, EPSG:32611, 100 m, “data outside the bounds is null or nan” | same page, “Submission format” | OFFICIAL TEXT |
| 8 | Sample submission “predicts total fault absence” | same | OFFICIAL TEXT (conflicts with the 60,988-positive owner mirror; see section 5) |
| 9 | Features include “top-of-crustal magnetic source depth estimate”, isostatic gravity anomaly and slope, earthquake density, and surface conductivity; **no radiometric layer is listed** in the provided-features list | same page, “Provided features” | OFFICIAL TEXT |
| 10 | Feature data come from GeoDAWN “lidar, magnetic, and radiometric” surveys | [official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), §2 Background | OFFICIAL TEXT |
| 11 | Three submissions per week; one chosen submission; public and private scores may differ | rules §3.2 and the problem page | OFFICIAL TEXT |
| 12 | Generative-AI use must be disclosed in the narrative; finalists must submit code assets and documentation | rules §3.2 | OFFICIAL TEXT |
| 13 | No uniqueness requirement appears in the organizer text read | rules §§1–3.2 and A.1–A.5 read; §§3.3–3.7 and A.6–A.17 **not read** | PARTIAL — the uniqueness rule is this project’s internal protocol |
| 14 | GeoDAWN is CC0 1.0 and has DOI 10.5066/P93LGLVQ | [USGS GeoDAWN page](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [DOI](https://doi.org/10.5066/P93LGLVQ) | OFFICIAL TEXT |
| 15 | Radiometric grids and GeoTIFF products exist in the release: `22103_area1_grids.zip` 44,487,393 B (MD5 `30f9d721…`), `22103_area2_grids.zip` 238,439,415 B (MD5 `561e1fcb…`), `22103_area1_tiffs.zip` 45,685,879 B, `22103_area2_tiffs.zip` 241,738,690 B | [ScienceBase item JSON](https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7?format=json), [item page](https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7) | OFFICIAL METADATA; **which grid zip contains radiometric K, eTh, eU is UNVERIFIED until the zip is opened** |
| 16 | The sandbox shell cannot reach sciencebase.gov (SSL error), so these files cannot be downloaded from here | `curl` from this sandbox, 2026-10-29 | MEASURED LIMIT |
| 17 | Owner GEMSDOE32 page: 0.2778 is OWNER-REPORT; “NO FILE IS CLEARED FOR SUBMISSION”; the H51 candidate fails the r13-lattice-s5 test at 99.7% | [GEMSDOE32 site](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) | OWNER-REPORT |
| 18 | Owner page: “610 discrete ≤100k-dot detector rasters across 30 repositories” audited | same page | OWNER-REPORT (not reproduced here) |
| 19 | Radiometric K/eTh (or K/Th) ratio highs are reported as hydrothermal potassic alteration indicators; K enrichment can be detected by airborne spectrometry | [ScienceDirect, airborne gamma-ray spectrometry for potassic alteration](https://www.sciencedirect.com/science/article/abs/pii/S0969804322003967); [ResearchGate abstract of Shives et al. on potassic alteration](https://www.researchgate.net/publication/249865553_The_detection_of_potassic_alteration_by_gamma-ray_spectrometry-Recognition_of_alteration_related_to_mineralization) | LITERATURE; the ResearchGate item is a secondary listing; regional case studies, transfer to Nevada UNVERIFIED |

---

## 5. Irregularities flagged for manual review

1. **Uniqueness gate saturation (critical).** Section 3. Random dots and every focus file are flagged.
2. **User’s leaderboard figures do not match the live page.** “0.4413” does not appear in the 50 rows the page shows. The top is 0.4544. “0.3195 is the highest” is wrong: it is #47. The earlier repo claim “rank 27” was also wrong (#27 is 0.3326).
3. **The 0.2778 “highest” claim is an owner report.** It has no receipt, and no organizer result has been seen for it.
4. **Portal error “Predicted values must be in range [0, 1]” remains unexplained.** The nine focus files are all in [0,1] with finite zeros outside the footprint (VERIFIED-FILE). The official text says null or NaN outside. One focus file (GEMSDOE31) carries a NaN `nodata` tag but has zero NaN cells. That is a metadata inconsistency. The portal may read tags differently. Which file was uploaded when the error occurred is unknown.
5. **Owner sample template contains 60,988 positive cells**, although the official text describes total absence. This was already flagged. The mirror is not organizer-authenticated.
6. **The uniqueness rule is internal.** It is not in the organizer text read so far (section 4, row 13).
7. **Cross-site failure.** The owner’s own GEMSDOE32 page applies the same literal lattice gate and reports the same type of failure for its H51 candidate.
8. **Public versus private scoring.** The leaderboard shows public-test scores. Round 1 prize ranking uses the private set (rules §3.2).
9. **Owner mirror not authenticated.** All feature and reference rasters are owner mirrors, not DrivenData downloads.

---

## 6. Hypothesis slate (5 candidates, ranked; none tested)

Scores are qualitative. They are research priorities, not predictions of DTI. “New” means not implemented in this repo; I checked `scripts/`, `src/`, `tests/` and the evidence JSON with grep.

| Rank | Hypothesis | Layers and signature | Why it could catch a fault missing from the catalogue | Non-fault mimic and control | Difference from repo | Expected DTI gain · cost | Availability |
|---|---|---|---|---|---|---|---|
| **1** | **Topography-conditioned residual gravity step** (existing slate #1, reaffirmed) | Isostatic gravity anomaly and its slope, detrended elevation and slope. Block-fitted, label-blind terrain residual; signed step 300–900 m; coherence across orientations | A density offset under alluvium may continue past the mapped scarp. Residualizing relief targets concealed segments | Unfaulted contacts and terrace risers. Controls: contour-following breaks, label-blind offset blocks, terrain-regression ablation | Not implemented. Repo has B4 (paired-flank scarp step) and H1 (opposing gradients); neither fits the block-fitted terrain residual with a shoreline null | Unknown · medium | In hand (19-band owner mirror). **Band mapping against official metadata not yet done** |
| **2** | **Magnetic top-of-crustal source-depth step** (**NEW**) | Official feature “top-of-crustal magnetic source depth estimate” (page 967). Lateral step in source depth across 300–900 m, orientation-coherent | A fault can offset magnetic basement, which shows as a depth step even when the surface trace is covered | Basin or intrusive depth changes. Controls: depth-shuffled blocks, orientation-rotated steps. Older B1/B2 notes mention a basement-depth step, but no magnetic source-depth feature is implemented | Repo has no magnetic source-depth feature (grep) | Unknown · low–medium | Band identity **not yet verified**; the mirror band list has a conflicting description for band 15 |
| **3** | **GeoDAWN radiometric K, eTh, eU and K/eTh alteration corridors** (**NEW, external**) | K/eTh highs and eTh/K lows along fault corridors, interpreted as potassic hydrothermal alteration; lithology-residualized | Alteration can mark a fault corridor that is not mapped at the surface. The radiometric source is not in the provided feature list | Potassic granites and lithology, soil or vegetation, residual radon. Controls: lithology proxy, shuffled corridors, K alone versus K/eTh | Repo has no radiometric features (grep). The source is official USGS CC0 data | Potentially highest, but **covered faults are a weak case**: gamma rays sample only the top layer | **High** (grid zips ≈ 44.5 MB and ≈ 238.4 MB; TIFF zips ≈ 45.7 MB and ≈ 241.7 MB) | Official, CC0, on ScienceBase. **Not downloadable from this sandbox**; contents of each zip still unverified |
| **4** | Conductivity saddle across an independently located gravity break (existing slate #2) | Surface conductivity, isostatic gravity, gravity gradient. Cross-profile sign change of the conductivity Hessian | A buried conduit or offset may juxtapose conductors across a density boundary | Saline groundwater and inversion seams. Exclude the depth band until verified | Repo uses raw conductivity (K2) and H1 used conductivity contrast; the saddle is not implemented | Unknown · medium–high | In hand; depth band excluded |
| **5** | Strain-regime interaction prior (existing slate #3) | Shear-strain and dilatation rates with magnetic edge persistence; shuffled-strain control | A covered strand could sit at a regime boundary | Interpolation seams and intrusive contacts. The field is coarse (100 m interpolated), so the expected gain is low | K2 excluded strain bands | Low · low | In hand |

**Dropped, lowest prior:** seismicity sidedness (existing slate #4). It stays in [`research/2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md).

**Validation plan (not executed; no slot can be used until the gate decision is made):**
- Top candidate: **#1 gravity residual step**. Follow the protocol: feature-alone AUC canary (>0.90 means leakage), spatial blocks with buffered withholding, pooled DTI (α 0.2, β 0.8, 300 m), paired comparison against a frozen same-fold comparator. The repo’s own note says K3 must be rebuilt on identical folds before a paired claim.
- Budget: at most 3 experiments or 2 hours. This session used 0 experiments.
- Kill criteria: any feature with canary AUC > 0.90; paired ΔDTI CI including zero; any overlap failure under the chosen gate.

---

## 7. Three review passes

**Pass 1: implement and verify.** Built `scripts/uniqueness_gate_calibration.py`, which reuses the shared `check_comparator`, the shared gate constants and the vendored `saturation_certificate`. It fails closed on pinned SHA-256 mismatch. Wrote `tests/test_uniqueness_gate_calibration.py`. Regenerated the Pages desk with a new validated gate section. Results: pytest 234 passed, 4 skipped (previously 226 passed, 8 skipped, before the cache was restored); `npm test` 3/3; `npm run test:site` 7/7; `npm run test:browser` PASS on all six checks.

**Pass 2: bugs, edge cases and wording.** Fixed in this pass:
- The first draft of one test contained a vacuous assertion. Replaced with exact pigeonhole arithmetic (`3·bound ≤ 10·u` and `3·(bound+1) > 10·u`).
- Removed a clumsy import fallback.
- The first generated text said “roughly 600 registry rasters”. Replaced with the owner’s own statement (610 rasters, owner-reported).
- The first text said “its newest file”. Replaced with “its H51 candidate”, which matches the owner page.
- The gate itself was **not** changed.

**Pass 3: recheck against the original request.**

| Request | Status |
|---|---|
| Unique, downloadable TIFF, and an obvious answer on whether to submit it | **Answered: NO.** No new file generated, because every competitive-size dot file fails the literal gate by arithmetic. |
| Executive summary with a clear best file and estimate table | Exists; this session added the gate finding. **Estimates remain “Unavailable”**; no holdout projection is a score. |
| Explain why 0.2778 scored | Section 2 (verified subset facts; derived break-even, labelled). |
| Beat 0.2778 or 0.3195 | **Not achieved.** Nothing has passed the gate or been validated on holdout. |
| 3–5 untried hypotheses, ranked, layers and signatures named | Section 6: five, with two new (#2, #3). |
| Validate the top candidate on holdout before a slot | Not run. The gate decision and lane assignment come first (section 8). |
| Verify line by line with official links; flag irregularities | Section 4 (19 rows) and section 5 (9 items). |
| Put the prompt into the README and use it as the operating base | README updated with this session’s status; the prompt remains there. |
| Create a PR and merge to main | PR #62 opened from the session branch; CI (test, validate, verify) passed on it. The merge is the last step and is reported in the session summary, not in this file. |
| Limitations and what access is needed | Section 8. |

---

## 8. Remaining work, limitations and access needed

**Decisions (you):**
1. Choose uniqueness Option A, B or C (section 3e). Nothing has been applied.
2. Assign the method lane. The protocol refers to a “single method paragraph below” that the prompt does not contain.
3. Decide whether a single portal test upload of one existing file is acceptable. It uses one of three weekly slots, so do not do it unless you intend to.

**Access needed (none obtainable from the sandbox shell today):**
- **DrivenData data tab** (login): the organizer template, `training_features.tif`, labels, and DEM links. Without it, portal behaviour and the exterior convention cannot be authenticated.
- **ScienceBase / USGS GeoDAWN files** (for the radiometric idea): reachable by fetch tool metadata only. Needs a manual or allowed-host download of `22103_area1_grids.zip` and `22103_area2_grids.zip`, and an inspection of their contents against the file list in section 4 row 15.
- **Full registry**: the owner’s audit covers 610 rasters across 30 GitHub repositories. The GitHub API is allowed in the sandbox, so this can be enumerated in a later session, but it has not been done here.

**Limitations:**
- Every holdout number in this repo is a catalogue proxy, not the hidden expert label set.
- Owner mirrors are not organizer-authenticated.
- The 0.2778 score, the removal rule for the 6,436 dots, and the claimed submission are all unverified.
- The radiometric idea is a research hypothesis. Covered faults are a weak target for gamma-ray data.
- The uniqueness rule is internal, and the organizer text read so far does not contain it.
- Final entry also requires code assets, documentation, and a generative-AI narrative (rules §3.2).

**Suggested next session:** (1) record decision 1; (2) enumerate the registry through the GitHub API; (3) open the GeoDAWN area-1 grid zip if it can be placed in the cache, and map the radiometric and magnetic-depth bands; (4) run the gravity-step experiment only after decisions 1 and 2.

## 10. Main-branch irregularities found at merge time (added after PR #62 was opened)

Merging `main` (PRs #60, #61, #63 landed after this branch was cut) exposed the following. Each was checked by a reproducible command; none was fixed beyond the items noted.

| # | Finding | How verified | Status |
|---|---|---|---|
| M1 | Main's H-A TIF (`docs/downloads/gemsdoekarage2-hA-intersection-propensity-aad3569983ab.tif`, 2,524 positives, 1,896 inside the template footprint) was headlined as "unique" on the home and executive-summary pages. Under the literal gate it matches the lattice witness at **100%** of in-footprint dots (duplicate). | `/tmp`-scratch check using `scripts/check_uniqueness.check_comparator`, same footprint and witness as the calibration receipt | Corrected on both pages: heading, verdict and button now say "not unique". The file itself is unchanged. |
| M2 | Main's GW-NFS TIF (`gemsdoe-karage2-gw-nfs-h1-20261029-zeros.tif`, 30,000 positives) matches the lattice at **98.9%** (duplicate). It has no run card and no page link. | same check | Not corrected (no page claims it). Orphan file; registration needed. |
| M3 | 628 of H-A's 2,524 positives lie outside the template footprint, which the official format says should be null/NaN. The run card reports the total only. | same check | Flagged, not fixed. |
| M4 | The H-A run card's uniqueness claim ("distinct sparse intersection pattern") is not backed by any receipt. Its leaderboard URL has a duplicated path segment (`competitions/306/competitions/306/`). | JSON read | Flagged, not edited. |
| M5 | Main's `docs/index.html` and `docs/executive-summary.html` were hand-edited and no longer match `scripts/build_hk3_pages.py`. On `origin/main`, `build_hk3_pages.py --check` exits 1 ("stale pages/evidence"). | worktree run of `origin/main` | Pre-existing on main. Not regenerated, because that would delete main's H-A section. |
| M6 | The executive-summary link to this note was broken (missing `../`). | `tests/test_artifacts.py` link test | Fixed. |
| M7 | Eleven tests fail on `origin/main` and identically on this merged branch: K2/K3/legacy page-language checks expect file names that PR #63 removed from the front pages; root `index.html` no longer references `docs/index.html`; the HK3 protocol-review integrity check fails because `docs/downloads/` has files that the `evidence/public_downloads_audit.json` inventory does not register. | `pytest -q` on `origin/main` (worktree) and on the merged branch | **Not fixed.** Reconciling these needs a decision on which front-page content is canonical. |

Consequence: this PR is **not merged**. The merge rule requires passing tests, and the merged state has 11 failures, all present on `main` before this PR. The PR adds no new failure. The decision is left to the user (see the remaining-work list).

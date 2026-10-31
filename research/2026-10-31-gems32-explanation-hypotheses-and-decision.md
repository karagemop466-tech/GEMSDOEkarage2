# 2026-10-31 — GEMSDOE32 explanation, H-C test, ranked hypotheses, and decision

**Decision: OK TO SUBMIT: NO. No file is approved for download or a submission slot.** The only new TIF (H-C) is research-only with a negative verdict. The uniqueness gate also blocks footprint candidates in general (see §3).

Labels used below: **HOLDOUT-DTI** = local catalogue-recovery proxy (evaluator sha, α 0.2 / β 0.8, R 300 m, withheld count, interval status shown). **MEASURED** = counted from bytes in this repo. **USER-REPORTED / UNVERIFIED** = leaderboard or owner claims not receipted by the organizer. **ILLUSTRATIVE** = first-order model, not a score. Nothing here is an organizer-confirmed score (no ORGANIZER-CONFIRMED receipt exists).

## 1. Nine focus sites (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36)

Files are the owner-repo best files named in `scripts/build_hk3_pages.py` (`gather()`), pinned by sha256. Registry copies were checked: 7 of 9 match the pinned sha; GEMSDOE32 (zeros vs NaN encoding) and GEMSDOE33 (owner file re-fetched 2026-10-31, sha 87f857d5…, same 41,865 dots as the registry copy) differ only in encoding. Dot sets were verified identical.

Estimated score: **Unavailable** for every site. No same-evaluator holdout exists for these fixed files (see §6), and a projection is never presented as a score.

| Site | File to download (owner repo) | Score (label) | Holdout DTI (HOLDOUT-DTI) | Max uniqueness vs other focus site (MEASURED, chance-corrected) | Overlap with lattice13, raw / corrected (MEASURED) | Download/submit |
|---|---|---|---|---|---|---|
| GEMSDOE32 | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` ([repo](https://github.com/buffedlizard55-lab/GEMSDOE32/raw/6edcc4cd529ca0809b956ccb00aea7f0e3b79cbf/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif)) | 0.2778 (USER-REPORTED / UNVERIFIED) | not computed (see limitations) | 1.000 vs GEMSDOE36 | 99.91% / 0.340 | NO |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` ([repo](https://github.com/buffedlizard55-lab/GEMSDOE36/raw/c15da37c83f11dcec0f6c62f65052efc825304a8/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif)) | 0.2750 (USER-REPORTED / UNVERIFIED) | not computed (see limitations) | 0.970 vs GEMSDOE24 | 99.92% / 0.360 | NO |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` ([repo](https://github.com/buffedlizard55-lab/GEMSDOE28/raw/424bf795ed2183000c643d6e30a12ce2d4bf401d/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif)) | 0.2710 (USER-REPORTED / UNVERIFIED) | not computed (see limitations) | 1.000 vs GEMSDOE30 | 99.91% / 0.298 | NO |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` ([repo](https://github.com/buffedlizard55-lab/GEMSDOE31/raw/e70a257c829ad874135aff4b7b3a1452c4740640/docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif)) | 0.2708 (USER-REPORTED / UNVERIFIED) | not computed (see limitations) | 1.000 vs GEMSDOE30 | 99.92% / 0.362 | NO |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` ([repo](https://github.com/buffedlizard55-lab/GEMSDOE33/raw/0baedf407845fc9c10f1c605ae59eeada41a0578/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif)) | 0.2632 (USER-REPORTED / UNVERIFIED) | not computed (see limitations) | 0.996 vs GEMSDOE30 | 99.91% / 0.332 | NO |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` ([repo](https://github.com/buffedlizard55-lab/GEMSDOE25/raw/ef939fe87041b6a8315a5f5210cd8a8eee93b2c4/docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif)) | 0.2600 (USER-REPORTED / UNVERIFIED) | not computed (see limitations) | 1.000 vs GEMSDOE30 | 99.92% / 0.348 | NO |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` ([repo](https://github.com/buffedlizard55-lab/GEMSDOE30/raw/eaff218f81e89fadc605650bb2cd55dd4b58e18d/docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif)) | 0.2600 (USER-REPORTED / UNVERIFIED) | not computed (see limitations) | 1.000 vs GEMSDOE27 | 99.92% / 0.348 | NO |
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` ([repo](https://github.com/buffedlizard55-lab/GEMSDOE24/raw/63d5885b68f73c19a7746052ccb3e5690f3271b5/docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif)) | 0.2477 (USER-REPORTED / UNVERIFIED) | not computed (see limitations) | 1.000 vs GEMSDOE30 | 99.92% / 0.392 | NO |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` ([repo](https://github.com/buffedlizard55-lab/GEMSDOE27/raw/bf34151e8e4ef26ec924f28dbc371a39bd740782/docs/downloads/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif)) | 0.2449 (USER-REPORTED / UNVERIFIED) | not computed (see limitations) | 0.976 vs GEMSDOE30 | 99.92% / 0.404 | NO |

Source: `evidence/uniqueness/focus-pairwise-overlap-2026-10-31.json` (script `scripts/focus_pairwise_overlap.py`). Raw overlap saturates on this dense footprint (lattice13 covers 99.87% of footprint cells within 3 px), so the chance-corrected value `(obs − chance)/(1 − chance)` is the one to read. **Several focus pairs are effectively identical**: all nine focus sites reach 0.970–1.000 chance-corrected overlap with at least one other focus site.

### Executive summary per site (USER-REPORTED values; MEASURED structure)

- **GEMSDOE32 (0.2778 user-reported, best user-reported):** B2 = GEMSDOE28 h27-4 base minus exactly the dots within 200 m of visible catalogue faults. It is a flank-pruned duplicate of the base (see §2).
- **GEMSDOE36 (0.2750):** Anderson/geothermal PINN zeros file. Chance-corrected overlap with GEMSDOE24 is 0.970.
- **GEMSDOE28 (0.2710):** `h36-1` rung-30 blind file. Its chance-corrected overlap with GEMSDOE30 is 1.000.
- **GEMSDOE31 (0.2708):** h27-4 solo d28. Identical to GEMSDOE30 at chance-corrected 1.000.
- **GEMSDOE33 (0.2632):** h33d analog tip stepover. Overlap with GEMSDOE30 is 0.996.
- **GEMSDOE25 (0.2600):** dotted h19-5 d2-8. Identical to GEMSDOE30 at 1.000.
- **GEMSDOE30 (0.2600):** d28 Poisson off-catalogue file. Identical to GEMSDOE27 at 1.000; GEMSDOE31 at 0.925.
- **GEMSDOE24 (0.2477):** h25-1 dotted d1-5. Identical to GEMSDOE30 at 1.000.
- **GEMSDOE27 (0.2449):** topo-gap closure. Overlap with GEMSDOE30 is 0.976.

## 2. Why GEMSDOE32 scored 0.2778 (verified mechanism + reasoning)

**Measured from bytes** (`scripts/verify_gems32_b2.py` → `evidence/gems32-b2-verification.json`, all checks pass; owner audit excerpts in `evidence/gems32-h33-source-excerpts.json` with fetched-bytes hashes):

- Base (GEMSDOE28 h27-4 r1 solo): 40,199 dots. 2,545 are within 200 m of the 60,988-cell organizer catalogue. The base minimum distance to catalogue is 141.4 m.
- B2: 37,654 dots, all of them in the base (subset check passes). None is within 200 m. B2 minimum distance is 223.6 m.
- Removed set = exactly the base dots within 200 m (equality check passes). 100% of B2 dots sit within 3 px of a base dot.
- B2 raster sha256 `c55bafc4…` matches the owner audit. The zeros and NaN variants have identical dots.

**Reasoning (PhD-level, with what is and is not established):**

1. *The gain is a removal, not an addition.* B2 adds no new mass, so its entire difference from the base is the 2,545 flank dots. The owner's own proxy (`ei_drift_corrected`, owner evaluator, `evidence/h33_holdout.json`) reports +0.00487 for the same change. It is a proxy, not an organizer result.
2. *Why flank mass costs score (reasoning, not verified against the organizer).* The dots are within 200 m of visible faults. The repo's protocol scores with α 0.2 / β 0.8 and a 300 m triangular kernel; the leaderboard's own parameters are not in the repo. In a kernel-weighted metric of this form, predicted mass sitting on already-mapped faults is credited only where it lands near a *withheld* positive. Flank dots that do not do so add to the denominator and dilute the weighted-recall term.
3. *First-order check (ILLUSTRATIVE, not measured).* Using the owner's live-anchor inversion (T = 5073.29, Den = 18734.44, labelled not measured in the owner's `evidence/h33_validation.json`), ΔD ≈ T·α·ΔF / Den² with ΔF = 2,545 gives **≈ 0.00736**. The user-reported Δ is 0.2778 − 0.2708 = **0.0070**. The magnitudes agree, but this supports only the mechanism, not a measured score.
4. *Caveat.* The organizer's exact flank treatment is not in the repo. The local evaluator and the owner's proxy point the same way, but neither is an organizer receipt.

**Can a higher score be reached?** Yes in principle, but not by this lever. Flank pruning is worth about 0.007. The gap to the public #1 snapshot is about 0.18 (0.4544 vs 0.2778; snapshot is ORGANIZER-PUBLISHED PUBLIC SNAPSHOT, not a receipt). Getting there needs new off-catalogue true-positive mass. Any new mass in the footprint lands within 3 px of the 13GEMSDOE lattice (§3), so the uniqueness gate blocks it. Local data cannot validate new TP mass.

## 3. The uniqueness gate is structurally unsatisfiable on this footprint

- Lattice13 (`G24_lattice13_nanoutside.tif`) covers **99.87%** of the footprint within 3 px (MEASURED; `chance_coverage_3px_of_footprint.lattice13 = 0.998713`).
- A random dot placed in the footprint therefore lands within 3 px of lattice13 with probability ≈0.9987, so the literal 70% dots-within-3-px gate cannot be met by any footprint placement.
- H-C (E1) measured 0.999929 raw. Chance-corrected: (0.999929 − 0.998713)/(1 − 0.998713) ≈ 0.945.
- The protocol's 70% gate was **not waived**. Changing it is a protocol-owner decision (see §8).

## 4. H-C (strain-seismic corridor) — tested, NEGATIVE

Run card: `evidence/hc/e1_run_card.json`. Generator: `scripts/hc_strain_corridor.py`. Raster: `docs/downloads/gemsdoekarage2-hc-strain-seis-corridor-30k-20261031.tif` (1,498,253 bytes, sha256 `f30a095e…`). The generator was re-run once after adding the footprint block. This is a regeneration in the sense of AGENTS.md. The bytes are identical to the first run (sha verified), and the deviation is disclosed in `research/2026-10-31-three-pass-review.md`.

| Check | Result | Label |
|---|---|---|
| Pooled DTI (α 0.2, β 0.8, R 300 m, buffer 3 px) | **0.013668** | HOLDOUT-DTI |
| Withheld positives | 60,988 | HOLDOUT-DTI |
| Fold DTIs (4 quadrants) | 0.00236, 0.001463, 0.048538, 0.004605 | HOLDOUT-DTI |
| 95% CI | not computed (4 folds; fold range reported instead) | HOLDOUT-DTI |
| Leakage canary (max folded AUC, threshold 0.90) | 0.56955 (pass) | MEASURED |
| Format validator | pass | MEASURED |
| Uniqueness (≤70% within 3 px; ≤0.90 Spearman) | **FAIL**: 0.999929 vs lattice13 | MEASURED |
| Uniqueness coverage | checked against 22 local registry rasters, not all 440 | MEASURED |
| Verdict | **negative; DO NOT SUBMIT; research only** | — |

The flank-off diagnostic returns an identical DTI. This is by construction, because visible faults are masked at ≥3 px from any active block pixel, so the holdout cannot test the flank lever. Its inertness is not evidence that the flank lever was tested.

## 5. Five ranked hypotheses (before implementation)

Ranking by expected DTI gain and cost. Gains are qualitative; no numeric projections are given.

| Rank | ID | Hypothesis | Expected gain | Cost | Status (2026-10-31) |
|---|---|---|---|---|---|
| 1 | H-C | Seismicity-aligned strain corridor (shear-rate ridge × quake intensity) | medium | low–medium | **TESTED (E1): negative.** Holdout 0.013668; uniqueness FAIL (§4). |
| 2 | H-N1 (new) | 3–8 px parallel splay band beside mapped faults, parallel to strike; the flank-adjacent region the holdout cannot test | low–medium | low | **Specified, NOT RUN.** Local data suffices. A dot set in the footprint would fail the uniqueness gate by construction (§3), and the protocol stop rule would apply. |
| 3 | H-A | Multi-scale fault-intersection propensity (curvature ×3 scales, K/Th, distance to fault) | medium–high | medium | **SKIPPED this session.** Needs GeoDAWN radiometrics, which are not in the 19-band stack; usgs.gov is unreachable. Earlier file `gemsdoekarage2-hA-intersection-propensity-aad3569983ab.tif` (2026-10-29) failed full-registry uniqueness (overlap 1.0 vs lattice13). |
| 4 | H-B | Off-catalogue SGMC fault-distance transform with depth-to-basement | high | high | **BLOCKED.** The SGMC/INGENIOUS source is not reachable from this sandbox (allowlist: github, pypi, npm). Not fetched. |
| 5 | H-D / H-E | Radiometric K-U-Th alteration index (H-D); multi-resolution anisotropic lineament density from a 3DEP DEM (H-E) | medium / lower–medium | low | **BLOCKED.** GeoDAWN radiometrics are absent, and USGS 3DEP is unreachable. Not fetched. |

**Top feasible candidate** is H-N1. It is not run because the uniqueness gate blocks it by construction. The protocol budget is 3 experiments per session. One is used (E1), two remain, and neither is spent, because a run could not produce a submittable outcome under the current gate.

## 6. Evaluator, holdout and baseline limits

- `pooled_dti_hide_and_recover` had a false-positive overcount (perfect-everywhere DTI 0.625, now 1.0; the active-region fix is regression-tested in `tests/test_holdout_pooling.py`, 5 passed).
- A same-evaluator baseline for the fixed focus submissions cannot be computed legitimately under hide-and-recover. Those files were built from the full catalogue, so feeding them into the hide-and-recover loop would leak the withheld positives. The GEMSDOE32 +0.00487 comes from the owner's protocol, not ours.

## 7. Public-download audit

`scripts/audit_public_downloads.py` now registers E1 with kind `research-nan-exterior`. That kind overrides only `whole_array_finite` and `range_0_1`. It requires the finite-mask sha256 to match the footprint hash in the run card, a finite count of 5,167,373, values in [0,1] inside the footprint, and no infinities. Existing files keep the finite-only rule. Result (after merging main): `inventory_status = PASS_RESEARCH_ONLY`, 13 artifacts, no unexpected downloads, E1 `VERIFIED_RESEARCH_ONLY`. Main had two unregistered TIFFs (blind-geothermal, near-trace). Blind-geothermal is registered. Near-trace is quarantined (see §9 item 11). The check is against the card's footprint hash, not organizer-authenticated.

## 8. Protocol decision needed (not waived)

The 70% gate and the 13GEMSDOE lattice are incompatible on this footprint. Options for the protocol owner: (a) re-define the gate on chance-corrected overlap; (b) gate on a non-lattice registry only; (c) accept that no footprint candidate can be submitted. This decision is out of scope for an agent to make alone.

## 9. Irregularities

1. Holdout target is misaligned with the leaderboard's hidden set (catalogue-recovery proxy).
2. `sample_submission.tif` equals `labels.tif` (60,988 positives), though the official text describes an example that predicts "total absence".
3. `labels.tif` is byte-identical to `existing_faults.tif` (sha256 `7ba308cc…`).
4. The shared evaluator over-counted false positives before 2026-10-31 (fixed; regression-tested).
5. Lattice saturation: lattice13 covers 99.87% of the footprint within 3 px, so the 70% gate is unsatisfiable (§3).
6. The audit's finite-everywhere convention conflicts with the official NaN-outside wording and the organizer sample (the audit now has a separate NaN-exterior kind for E1 only).
7. Portal error "Predicted values must be in range [0, 1]" is **unresolved**. Organizer evidence is not reachable from this sandbox. Whether it relates to NaN exterior is unverified; the in-footprint range check passes.
8. The focus-site files are near-duplicates of each other (§1).
9. The public-download audit and the shared writer disagree on the exterior convention.
10. The owner's GEMSDOE32 JSON labels B2 `slot_decision: SLOT_ELIGIBLE` and gives `predicted_leaderboard_dti 0.2747`. Both are owner-side labels and projections. They are not organizer decisions or scores and are not used in this report.
11. **Main-branch near-trace file (`gemsdoe-karage2-near-trace-20261031.tif`)**: 122,597 dots, and every one lies within 2 px of the full labels catalogue (`labels == 1`, including withheld positives). Its card reports holdout DTI 0.624191 (fold range 0.6227–0.6273) while describing the catalogue as masked. The field was built from unmasked positives, so the number is leakage, not a held-out result. It also sits close to the pre-fix evaluator defect value of 0.625. The card's verdict is `promote`, which the audit correctly fails closed on. The file is quarantined in `evidence/quarantine/`. The card was not relabelled.
12. **Main-branch GBSP file**: its card describes a continuous [0,1] prospectivity field, and its "uniqueness-passed" claim tests only lattice-uncovered pixels. Lattice13 is excluded by design, so the claim is not the literal dot gate and is not comparable with §3. The card's own verdict is negative and `ok_to_submit` is false.

## 10. Limitations

- No organizer receipt for any local TIF. Leaderboard values are USER-REPORTED / UNVERIFIED. DrivenData, NLR (docs.nlr.gov), and OpenEI GDR were unreachable from the sandbox.
- HOLDOUT-DTI has no 95% CI (4 quadrant folds).
- Uniqueness for E1 was checked against 22 local registry rasters, not the full 440-entry registry.
- Owner-supplied bytes are integrity-pinned, not organizer-authenticated.
- The ΔD estimate in §2 is ILLUSTRATIVE only.

## 11. Remaining-work list

1. Protocol-owner decision on the uniqueness gate (§8).
2. Full 440-entry registry uniqueness check for E1 and any future candidate.
3. Flank-aware holdout design (the current holdout masks ≥3 px and cannot test the flank lever).
4. 95% CI for HOLDOUT-DTI (block bootstrap across quadrants).
5. Organizer evidence for the portal "[0, 1]" error (needs DrivenData account access; not reachable from the sandbox).
6. Run H-N1 only after the gate decision (§5).
7. Reachable-source check for SGMC (H-B), GeoDAWN (H-A, H-D) and 3DEP (H-E), if hosts become reachable.

## 12. Three review passes

See `research/2026-10-31-three-pass-review.md`.

## Sources (line-checkable)

- Competition root: https://www.drivendata.org/competitions/306/competition-doe-gems/
- Leaderboard snapshot cited by repo (ORGANIZER-PUBLISHED PUBLIC SNAPSHOT, not a receipt; not reachable from sandbox this session): https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Submission rules as recorded by the repo (not reachable from sandbox): https://docs.nlr.gov/docs/fy26osti/96647.pdf
- DOE GDR dataset (not reachable): https://gdr.openei.org/submissions/1391
- Owner repos (sha-pinned, owner-supplied): https://github.com/buffedlizard55-lab/GEMSDOE32 (and GEMSDOE24/25/27/28/30/31/33/36)
- Owner GEMSDOE32 audit and validation JSON: see `evidence/gems32-h33-source-excerpts.json` for URLs and fetched-bytes hashes.
- Earlier hypothesis file: `research/hypotheses-2026-10-29-untried.md`.

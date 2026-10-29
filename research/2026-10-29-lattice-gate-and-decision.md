# 2026-10-29 · Lattice gate, decision table and next lane (GEMSDOEkarage2)

**Decision: NO FILE IS OK TO DOWNLOAD AND SUBMIT.** No new TIFF was generated, no experiment was run, no competition slot was used.
Read this first. Companion artifacts: [audit receipt](../evidence/lattice-gate-audit-2026-10-29.json), [run card](../evidence/session-2026-10-29b-lattice-gate-run-card.json), [executive summary](../docs/executive-summary.html).

Labels used below: **HOLDOUT-DTI** (local catalogue proxy; evaluator, withheld count, 95% CI given) · **ORGANIZER-CONFIRMED** (none exists here) · **USER-REPORTED / UNVERIFIED** (values you or the owner sites supplied; no receipt) · **MEASURED** (computed from pinned bytes in this session).

---

## 1. Why no file can pass the literal rule (MEASURED)

The protocol says a raster is a duplicate if **more than 70% of its dots lie within 3 px of one registry raster's dots**. The registry includes the **GEMSDOE13 spacing-five lattice** (`20261001_r13-lattice-s5_v2_nan-outside`, user-listed at 0.0904, USER-REPORTED).

* Footprint: 5,167,373 cells (owner-mirror template; not organizer-authenticated).
* The lattice covers **99.87%** of the footprint within 3 px. Only **6,649 cells** are farther than 3 px from every lattice dot.
* Pigeonhole: for N dots anywhere in the footprint, overlap ≥ (N − 6,649)/N. A pass therefore needs **N ≤ 22,163** *and* at least 30% of the dots placed in those 6,649 uncovered cells. That is edge-hole gaming, which the protocol forbids.
* The official metric does not contain this rule. The organizer scores probabilities over the footprint. The rule is the protocol's own, and it is the sole reason every file below fails.

Worked values (from the receipt): the GEMSDOE32 file (37,654 dots) has **≥ 82.34%** overlap for any placement; its measured overlap is **99.92%**.

## 2. Decision table — nine focus sites

| Site | File to download (owner link, **research reference only**) | Owner-reported value | Estimated leaderboard score | Unique vs registry? | Lattice overlap (MEASURED) | OK to download and submit? |
|---|---|---|---|---|---|---|
| GEMSDOE32 | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 0.2778 USER-REPORTED | **Unavailable** | **NO** | 99.915% (37,654 dots) | **NO** |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 USER-REPORTED | **Unavailable** | **NO** | 99.918% (38,854) | **NO** |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 USER-REPORTED | **Unavailable** | **NO** | 99.910% (37,660) | **NO** |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 USER-REPORTED | **Unavailable** | **NO** | 99.918% (40,199) | **NO** |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 USER-REPORTED | **Unavailable** | **NO** | 99.914% (41,865) | **NO** |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 USER-REPORTED | **Unavailable** | **NO** | 99.916% (44,090) | **NO** |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 USER-REPORTED | **Unavailable** | **NO** (byte-identical mask to GEMSDOE25) | 99.916% (44,090) | **NO** |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-…-nan.tif` | 0.2449 USER-REPORTED | **Unavailable** | **NO** | 99.923% (61,328) | **NO** |
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 USER-REPORTED | **Unavailable** | **NO** | 99.922% (60,069) | **NO** |

Each file's "Unique" answer is backed by the receipt's `nine_site_best_files` rows: every one has **100% of its dots within 3 px of a sibling registry raster**, even with the lattice excluded (e.g., GEMSDOE24's mirror group-best file, 121,131 dots). The exact subset relation is verified for one pair only: **GEMSDOE32's 37,654 dots are a strict subset of GEMSDOE25's 44,090 D2.8 dots; the 6,436 removed dots are the difference** (MEASURED; the repo's pruning account matches).

Scope limit: 440 focus-site registry rasters from the nine repositories (pinned refs). The full competition field is not available here.

## 3. Registry-wide measurement (MEASURED, 440 pinned rasters)

| Quantity | Value |
|---|---|
| Registry rasters on the template grid | 439 (1 on a 32×48 test grid, excluded and recorded) |
| Failing the literal lattice stop (> 70%) | **437** |
| Non-lattice rasters with ≤ 22,163 dots | 15 |
| Only non-lattice raster below the 70% line | `GEMSDOE36 gemsdoe36-lattice-avoiding-upflow-…-zeros.tif`: **505 dots, 0.0% lattice overlap** — it passes by **avoiding the lattice**, which is edge-hole gaming. Flagged; not treated as clearance. |
| Rasters covering ≥ 50% of the footprint within 3 px | 1 (the lattice, 99.87%). Next highest: 31.9%. |
| Densest registry raster | GEMSDOE31 `…tgj31-transfer-…-DO-NOT-SUBMIT.tif`, 255,289 dots (covers 11.3% of the footprint) |

So the lattice is the single structural blocker, and sibling absorption is the second. Removing the lattice alone does **not** clear the nine files.

## 4. The decision you need to make (not made here)

The literal rule and your opening sentence ("unique and not an exact duplicate") are different standards. A geology-motivated candidate cannot satisfy the literal rule without gaming. The options:

| Option | Effect | Consequence |
|---|---|---|
| **A. Keep the literal rule** | Every dot raster above ~22,163 dots fails the lattice. | **No file can ever be submitted.** Research only. |
| **B. Exclude space-filling calibration controls from the 70% test** | Lattice removed from the test. | The nine files still fail against sibling rasters (100%). No file clears. |
| **C. Exact-duplicate + Spearman standard** (≤ 0.90 rank correlation, byte-distinct, not a near-copy) | Test whatever counts as "duplicate" explicitly. | A new candidate could be generated if it also avoids dense siblings under this standard. Needs your written approval of the standard and a holdout run first. |

I will not choose between these and will not change the rule to create clearance. Under option B, a candidate would still have to avoid the dense siblings; whether one exists is unknown and has not been tested. Under option C I would next run one assigned experiment (≤ 3 experiments / 2 hours), then write the file with NaN outside the footprint, and produce a run card.

## 5. Why 0.2778 might score higher than its neighbours (labelled inference)

* Facts (MEASURED): GEMSDOE32 = D2.8 minus 6,436 dots (exact subset). GEMSDOE25 = GEMSDOE30 mask exactly.
* Linear break-even (derived here, first order): a dot raises DTI only if its hit probability exceeds **α × DTI ≈ 0.2 × 0.2778 = 0.056**. If the owner's two reported scores (0.2600 → 0.2778) came from the same scorer and labels, the removed dots' hit rates were **below ~5.6%**. This is conditional on unverified numbers, not a demonstrated cause.
* Implication: gains came from *removing* low-hit dots. Repeating that on D2.8 again would be a sibling copy, so it cannot pass the rule. A unique file must rank hit probability better, which has not been shown.
* Context (ORGANIZER-CONFIRMED leaderboard snapshot, 2026-10-29): #1 xiaofanhu **0.4544**; #27 jay398144 **0.3326**; #47 kpomazi **0.3195**; #50 **0.3167**. A 0.2778 public-test score would sit below rank 50. The owner values are USER-REPORTED and may not be on the same metric or split.

## 6. Candidate hypotheses (ranked; none validated; prior status checked)

**Correction (this section replaces an earlier draft).** The earlier draft called all four "new". Keyword checks of the repo and the owner documentation show two were already tried elsewhere and one is an older, deferred proposal. Status below is what I could verify.

Band names are the owner-mirror manifest's 19 names (`evidence/upstream/GEMSDOE31/registry/data_manifest.json`, sha-pinned, not organizer-authenticated): 1 mag_anom, 2 rtp, 3 tmi_hg, 4 geod_2ndinv, 5 iso_grav_anom_slope, 6 tc, 7 geod_shearrate, 8 geod_dilaterate, 9 tmi_vg, 10 deq_n100a15, 11 iso_grav_anom_vg, 12 det_elev, 13 iso_grav_anom, 14 tmi, 15 depth_to_base_surf, 16 ieq_n100a15, 17 cond_surf, 18 iso_grav_anom_hg, 19 det_elev_slope. K2/K3 (`scripts/k2.py`, `scripts/k3.py`) use 14 raw bands plus structure-tensor and texture features; they exclude bands 4, 7, 8, 10 and 16.

| Rank | Candidate | Layers | Prior status (verified) | Named non-fault mimic and control | Cost | Verdict |
|---|---|---|---|---|---|---|
| **1** | **Cross-field edge offset** (shear-offset edge dipoles): offset between a rtp / tmi_hg ridge and an iso_grav_anom ridge, across scales | 2 rtp, 3 tmi_hg, 13 iso_grav_anom | Proposed as **H2** in `knowledge/hypotheses.md` (2026-10-27): "Medium; deferred, not validated"; "not certified novel across all external repos". **Not implemented in this repo.** Not in the K2/K3 features. | Two grids registered with a shift (processing artifact) and lithologic contacts with unrelated sources. Control: shift one grid by ±1–3 px; the true-offset score must beat the shifted nulls. | Medium; restored data | Untested here. Best-supported lane, but **not novel**. |
| 2 | Terrain-residualised gravity step (slate #1, 2026-10-28) | 13, 11, 12, 19 | Proposed in `research/2026-10-28-next-lane-slate.md`; not found by keyword search in the owner READMEs I checked. Not certified novel. | Unfaulted sediment–bedrock contact; contour-following null | Medium; restored data | Untested here. |
| 3 | Strain-regime and seismicity-flank features (slate #3, #4) | 4, 7, 8 (strain); 10, 16 (seismicity) | K2/K3 excluded these bands; no test found. Owner status not checked. | Relief-driven strain artifacts; catalogue-density artifacts | Medium | Untested here. |
| — | **Radiometric K/Th alteration boundary** (earlier draft's rank 3) | GeoDAWN K, Th, U (owner layer `data/external/geodawn_rad_u8.tif`, sha `c22420f7…`, derived from the official GeoDAWN release) | **Already tried.** GEMSDOE28 H38-1 used the GeoDAWN channels; "transfer test refused"; "nothing was promoted" (`evidence/upstream/GEMSDOE28/README.md`, ~lines 1359–1384). The owner-derived layer is not in `.cache/competition_data`. | — | — | **Not recommended** unless a new mechanism is proposed. |
| — | **Tilt zero-contour** (earlier draft's rank 4) | 6 `tc`; `tmi_vg`, `tmi_hg`, `iso_grav_anom_*` | **Already tried.** GEMSDOE31 H31-M ("Gravity Tilt-Zero … `executed`") and GEMSDOE28 H36-1 ("True Potential-Field Tilt-Angle Zero-Contour …", its primary file). The GEMSDOE28 README describes band 6 as "Tilt angle **or** total curvature", so the band's meaning is also unsettled. | — | — | **Not recommended.** |

**Validation status (required before any slot):** none of the candidates has been run on the holdout. Under the protocol, a candidate must beat the frozen same-fold incumbent on the spatially-blocked holdout with a paired 95% interval, and pass each feature-alone AUC canary (> 0.90 = suspected leakage). Candidate 1 would be the first run. It was not started, because the uniqueness decision in §4 decides whether any output could ever be submitted.

**Owner-supplied layers still unrestored:** `data/external/lidar_scarp_features_u8.tif` and `data/external/geodawn_rad_u8.tif` are listed in the owner manifest (group "external") but are not in `.cache/competition_data`. Their provenance is owner-derived and was not verified against the official releases here.

## 7. Irregularities flagged for manual review

1. **No method lane.** No lane is assigned in this session, which matches the 2026-10-28 review. Assigning one is a decision for you (§4, §10).
2. **Leaderboard figures.** The 0.4413 and 0.3195-as-highest figures do not match the live page (top 0.4544; 0.3195 is rank 47). [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
3. **Layer-list mismatch (verified on the [problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)).** The official list names "top-of-crustal magnetic source depth estimate"; none of the owner mirror's 19 band names matches it. The official list also names "depth to conductive base surface" for the conductivity pair, which is consistent with the owner's `depth_to_base_surf` (no conflict there). The page's visual shows GeoDAWN radiometric counts, but K/Th/U are not in the official layer list.
4. **Band 6 meaning unsettled.** The GEMSDOE28 owner README describes band 6 as "Tilt angle **or** total curvature"; the official list does not name it. Its meaning must be authenticated before any use.
5. **Sample footprint conflict.** The official sample "predicts total fault absence"; the owner-mirror sample has 60,988 positive cells, the same count as the mirror's `labels.tif`. That contradicts the official wording. The mirror is not organizer-authenticated.
6. **Exterior convention.** The official page says data outside the bounds is "null or nan". Several saved research files and the HK3 file use finite zeros outside. The 2026-10-28 review fixed the writer's gate; the cause of the portal's "Predicted values must be in range [0, 1]" error is still unknown.
7. **Lattice-avoiding file** (GEMSDOE36, 505 dots, 0% overlap) passes the literal gate only by avoiding it; flagged as gaming-shaped, not clearance.
8. **Owner-link ref mismatch (MEASURED).** `registry/focus_sites.json` gives a different ref for every site than the commit where the registry bytes were pinned and sha256-verified (e.g., GEMSDOE32: focus `012e17b` vs pinned `73485f2`). The page's "Pinned revision" label used the focus ref. **Fixed this session:** owner links now use the manifest's own-repo commit (`scripts/build_hk3_pages.py`, `owner_pin()`, fail-closed). The focus refs are unexplained and need your review.
9. **Duplicate copies across repos (MEASURED).** The GEMSDOE25 best file's bytes appear in four registry repos (GEMSDOE24, 25, 30, 32); the GEMSDOE27 best file in two (27, 28). Its "unique vs registry" result depends on which copy counts.
10. **Registry hygiene.** The registry contains files labelled `DO-NOT-SUBMIT` (GEMSDOE31) and `NOT_SUBMISSION` (GEMSDOE36 format test, 32×48 grid). They are kept for measurement but should not be treated as submissions.
11. **Weekly quota and promotion.** Per the 2026-10-28 review, the rules describe up to three scored attempts per week. This session did not check the account quota; no slot was used.

## 8. Three review passes

* **Pass 1 — implement and verify.** Restored the 440 pinned registry rasters (sha256 verified). Built `scripts/lattice_gate_audit.py` and generated `evidence/lattice-gate-audit-2026-10-29.json`. Added the decision table to the public summary (`scripts/build_hk3_pages.py`, fail-closed loader). Pigeonhole formula checked against worked values. Official problem text and leaderboard read directly.
* **Pass 2 — bugs and edge cases (executed).** Test suite: 234 passed, 8 skipped (226 earlier + 8 new); `npm test` 3/3 and `npm run test:site` 7/7 pass. Generated desk: `--check` green; base-aware relative-link check on `docs/` finds 0 broken links (HEAD had 2). Owner-download links were checked against the manifest and corrected (see irregularity 8); the live link check was blocked by a GitHub API rate limit, so the 9 links are verified by pinned sha256 and manifest ref, not by a live HTTP fetch.
  Earlier defects found and fixed: one registry raster is on a different grid (32×48), which crashed the first run; it is now recorded as non-comparable. Found the first run's "max overlap vs other" was dominated by the lattice; added the lattice-excluded maximum. Found the page link to the memo used an unpublished `../research/` path; changed to the GitHub blob URL. Test `tests/test_lattice_gate.py` checks the audit overlap against the shared writer function (`_dot_overlap_3px`).
* **Pass 3 — recheck against the request.** The request asked for a unique TIFF that is obviously OK to submit. **That was not delivered, and that is the correct result:** no file can pass the literal rule without gaming, and §4 needs your decision. The request asked for estimated scores; none can be validated (§2). The request asked for 3–5 hypotheses; §6 gives five ranked candidates with prior-status labels. Two were already tried by other owners (radiometrics, tilt zero-contour) and are not recommended; the top candidate is an earlier deferred proposal, not a new idea. Validation of any candidate is pending and labelled as such.

## 9. Sources (checked this session)

| Claim | Source | Checked |
|---|---|---|
| Metric, format (float32, [0,1], EPSG:32611, 100 m, null/NaN outside bounds), sample "total fault absence" | [Problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | 2026-10-29, both pages |
| Leaderboard ranks and values | [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | 2026-10-29, all three pages |
| Data tab requires login | [Data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) | Not reachable from this sandbox (no connection) |
| GeoDAWN radiometric and magnetic release, CC0 | [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [DOI 10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ) | 2026-10-29 page read; download blocked |
| Registry rasters and lattice bytes | `registry/focus_registry_manifest.json` (GitHub owner repos, pinned refs) | sha256 verified on restore |
| Official reference solution | [gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution) | Previously reviewed |
| Competition rules (weekly cap, one final pick) | [Rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | Previously reviewed (2026-10-28); not re-read this session |
| Owner band names (19) and external layers | `evidence/upstream/GEMSDOE31/registry/data_manifest.json` | 2026-10-29, read |
| Prior radiometric test (H38-1) and refusal | `evidence/upstream/GEMSDOE28/README.md` ~lines 1355–1395 | 2026-10-29, read |
| Prior tilt zero-contour tests (H31-M, H36-1) | `evidence/upstream/GEMSDOE31/README.md`, `evidence/upstream/GEMSDOE28/README.md` | 2026-10-29, keyword search |
| 2026-10-27 H2 cross-field offset (deferred) | `knowledge/hypotheses.md` | 2026-10-29, read |
| GEMSDOE13 lattice as a user-listed submission | [13GEMSDOE site](https://buffedlizard55-lab.github.io/13GEMSDOE/) | User-supplied list; bytes match the pinned sha256 |

## 10. Remaining work and limitations (next session)

1. **Decision (you):** choose §4 option A, B or C in writing. Options B and C leave open whether any candidate can avoid the dense siblings; that is untested.
2. **If you choose B or C:** assign a lane (candidate 1 in §6 is the best-supported, though not novel), preregister it, run the feature-alone canaries, and run the holdout against a frozen same-fold incumbent. Stop at 3 experiments or 2 hours.
3. **Authenticated inputs:** the organizer template and the portal's exterior-convention behaviour. Neither is available here.
4. **External layers:** the owner-derived lidar and GeoDAWN grids are listed but not restored. The GeoDAWN release is official and CC0 ([USGS](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), DOI 10.5066/P93LGLVQ), but USGS, ScienceBase and DrivenData were not reachable from this sandbox (no connection, 2026-10-29). Radiometrics were already tested by GEMSDOE28 H38-1.
5. **Full competition registry:** only 440 focus-site rasters are measured here.
6. **Limits of this audit:** the duplicate test is the protocol's, not the organizer's metric. The mirror footprint and band labels are not organizer-authenticated.

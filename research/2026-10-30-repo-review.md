# Repo review — 2026-10-30 (arena/022009c9-gemsdoekarage2)

Scope: review of repo state, leaderboard claims, tests, and every shipped submission TIFF. No new experiment was run, no slot was used, and **no file is approved for submission**. Labels follow the parallel-run protocol: HOLDOUT-DTI, ORGANIZER-CONFIRMED, USER-REPORTED / UNVERIFIED, or LOCAL CHECK (file bytes only, not a score).

## 1. Bottom line

- **No submission is approved.** Every shipped TIFF is research-only (see `SUBMISSION_STATUS.md`, `AGENTS.md`). Nothing here changes that.
- **Estimated leaderboard score for any local file: Unavailable.** No holdout DTI exists for any current file in this session, and the full organizer registry is not in the repo.
- **The prompt's leaderboard numbers do not match the live page.** The current #1 is 0.4544, not 0.4413, and 0.3195 is rank 48, not the high. See §2.
- **Local TIFF checks pass** (finite, in [0,1], EPSG:32611, shape 3730×3292 for the shipped files), but the **exterior convention and the grid origin differ from the organizer sample**. Those are the most likely reasons for the portal's "Predicted values must be in range [0, 1]" error. Unresolved; see §4.
- **Tests:** 256 passed, 8 skipped (Python); 3/3 (Node). The README's previous count was 253 passed; the difference comes from the test suite, which was not re-audited here.

## 2. Leaderboard check (public DrivenData page, fetched 2026-10-30)

Source: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ (public page; 3 chunks read).

| Claim in prompt / repo | Live page (this fetch) | Status |
|---|---|---|
| "0.4413 is the GEMSDOE / current leaderboard high" | No row shows 0.4413. Rank 1 = **0.4544** (xiaofanhu) | **Irregular — flag** |
| "0.3195 is the highest score right now" | 0.3195 = **kpomazi, rank 48** (README says rank 47 in its 2026-10-29 snapshot) | **Irregular — flag** |
| "xiaofanhu 0.4544 rank 1" (README 2026-10-29) | Confirmed, rank 1 | Consistent |
| Rank 47 on this snapshot | like60986, 0.3231 (rank order shifted since 2026-10-29) | Leaderboard is moving; re-read before any comparison |

Rank 2 is cfld__ at 0.3916; rank 50 is twang at 0.3169. These are public DW-Tversky values, which are organizer-published leaderboard values, not local scores.

**Interpretation:** the target is 0.4544 (public #1), not 0.3195. Beating 0.3195 is only a rank-48 goal.

## 3. Focus-site claims (USER-REPORTED / UNVERIFIED)

The prompt's GEMSDOE32 value (h33-h33-2-b2 = 0.2778) and the other focus-site values come from the nine GitHub Pages sites. They are not linked to organizer receipts and are not on the public leaderboard page as rows, so they are unverified. The repo's own geometry audit found the focus files mutually overlapping (0.976–1.000, per `evidence/uniqueness/nine-site-pairwise-recheck.json`). The repo does not explain why GEMSDOE32 scored higher than the others. No holdout experiment has tested that explanation.

## 4. Local TIFF byte checks (LOCAL CHECK, not scores)

Measured with rasterio 1.4.4 on the committed files. Shipped files are in `docs/downloads/` and `reference/gemsdoe36/`.

| File | dtype | shape | CRS | nodata tag | NaN | min | max | zeros | >0 cells |
|---|---|---|---|---|---|---|---|---|---|
| gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif | float32 | 3730×3292 | EPSG:32611 | None | 0 | 0 | 1 | 12,234,052 | 45,108 |
| gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif | float32 | 3730×3292 | EPSG:32611 | None | 0 | 0 | 1 | 12,224,669 | 54,491 |
| gemsdoekarage2-k3-linctxdti-b110-20261028-zeros.tif | float32 | 3730×3292 | EPSG:32611 | None | 0 | 0 | 1 | 12,227,246 | 51,914 |
| gemsdoekarage2-b4-stepasym-b110-20261028-zeros.tif | float32 | 3730×3292 | EPSG:32611 | None | 0 | 0 | 1 | 12,227,246 | 51,914 |
| gemsdoekarage2-h2-stepover-8d519ec5ec58.tif | float32 | 3730×3292 | EPSG:32611 | None | 0 | 0 | 0.852 | 12,241,506 | 37,654 |
| gemsdoekarage2-hA-intersection-propensity-aad3569983ab.tif | float32 | 3730×3292 | EPSG:32611 | None | 0 | 0 | 0.932 | 12,276,636 | 2,524 |
| gemsdoe-karage2-hr4-intersection-20261029-nan.tif | float32 | 3730×3292 | EPSG:32611 | nan | 0 | 0 | 1 | 12,273,399 | 5,761 |
| gemsdoe-karage2-hkarage1-irregular-submodular-15000d-…-zeros.tif | float32 | 3730×3292 | EPSG:32611 | None | 0 | 0 | 1 | 12,266,965 | 12,195 |
| gemsdoekarage2-h1-parity-…-DO-NOT-SUBMIT-surface.tif | float32 | 3730×3292 | EPSG:32611 | None | 0 | 0 | 0.915 | 10,385,343 | 1,893,817 |
| reference/…/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif (organizer format sample) | float32 | 32×48 | EPSG:32611 | nan | 96 (outside) | 0 | 1 | 1,370 | 70 |

Full sha256 values are in the repo's audit JSONs (`docs/evidence/public_downloads_audit.json`). Each file's values are finite and in [0,1]. This does **not** prove portal acceptance.

**Irregularities to review:**

1. **Exterior convention.** Shipped files write finite zeros outside the footprint. The organizer format sample writes NaN there (96 NaN outside 1,440 finite cells). The README records this as unresolved.
2. **Geotransform origin.** Shipped files: origin (243350, 4508550), 100 m. Organizer sample: origin (400000, 4400000), 100 m. The sample is only 32×48, so it may be a format-only sample. The shipped grid is taken from owner mirrors, not an authenticated organizer template. The competition rules require a match to the template's shape and geotransform, so this cannot be waved through.
3. **Nodata tag.** Only the HR4 file and the organizer sample carry nodata = NaN. The rest carry none.
4. **Range error.** The local checks pass for [0,1] on every shipped file. The portal's error therefore cannot be reproduced from bytes alone. The likely causes are (1) the exterior convention, (2) grid mismatch, or (3) a portal check on the uploaded file's name/format. This is a hypothesis, not a finding.

## 5. Uniqueness and holdout status (from the repo's own records)

- Full-registry check (440 pinned focus rasters): gw-nfs and H-A are **DUPLICATE_STOP** (3-px overlap 1.0). Source: `SUBMISSION_STATUS.md`, `evidence/uniqueness/`.
- HK3: 45,046 of 45,108 dots within 3 px of a lattice raster (>70% = STOP). Source: `AGENTS.md`, `evidence/hk3/literal_recheck.json`.
- HR4: 99.9787% overlap on 4,685 in-footprint positives vs the lattice witness. Source: `SUBMISSION_STATUS.md`.
- Holdout DTI for the shipped files: the repo's records give HOLDOUT-DTI only for the gw-nfs raster (pooled 0.000013, 60,988 withheld positives, fold range, not a CI). It was quarantined. For all other files the holdout value is not established.

## 6. What I did not do, and why

- **No new hypotheses were implemented or tested.** The holdout needs the template feature stack, which requires `data/` from DrivenData, and `data/` does not exist in this checkout. The prompt's rule is to test a hypothesis on the holdout before spending a slot; that cannot be done here.
- **No new TIFF was generated.** Any new file would fail the same uniqueness gate, because the registry is incomplete and the focus rasters are mutually overlapping. Generating one now would produce a file that looks submittable and is not. That breaks the protocol.
- **No submission and no slot.** Promotion is a separate selector step within the weekly cap.

## 7. Limits and what is needed

| Need | Source (official / public) | Status |
|---|---|---|
| Competition data (training features, labels, sample submission, DEM links) | https://www.drivendata.org/competitions/306/competition-doe-gems/data/ (login required) | **Blocked** — requires an organizer login; not in repo |
| Organizer geotransform / template | Same data tab; the sample file in `reference/gemsdoe36/` is format-only | **Unresolved** — 400000 vs 243350 origin mismatch |
| Portal acceptance receipt for any file | Submission page after login | **Missing** — no file has ever been accepted with a receipt |
| Full registry of organizer-scored rasters | Not public | **Missing** — the 440-file check is partial |
| Holdout labels and features | Derived from GeoDAWN (https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), INGENIOUS (https://gbcge.org/current-projects/ingenious/) | Partly reachable; not run here |
| Live leaderboard | https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ | Reachable (read in §2) |

Official sources used in this review: DrivenData leaderboard page (above); submission-format PDF https://docs.nlr.gov/docs/fy26osti/96647.pdf (cited in README; not re-read here); EPSG 32611 https://epsg.io/32611.

## 8. Recommended next steps (for the next session)

1. Obtain the organizer template (geotransform, shape, exterior convention) through an authenticated account, and record it as an artifact. Without it, no local file can be called format-valid against the portal.
2. Decide the exterior convention: the organizer sample uses NaN outside the footprint. A small, controlled test on a dummy file is the next step; one submission slot should be spent only after the uniqueness gate passes.
3. Re-run the holdout evaluator with `data/` present, starting with the leakage canary on each feature alone (AUC > 0.90 = leakage).
4. Set the target to the live #1 (0.4544) and treat 0.3195 as a rank-48 reference point only.
5. Re-check the leaderboard before each decision; ranks moved within 24 h.

## 9. Irregularities list (for manual review)

1. Prompt states 0.4413 as the current GEMSDOE high; the live page shows 0.4544 at rank 1 and has no 0.4413 row.
2. Prompt states 0.3195 is the highest score; the live page shows it at rank 48.
3. GEMSDOE focus-site scores (0.2778 and others) are not linked to organizer receipts or leaderboard rows.
4. Exterior convention differs between shipped TIFFs (zeros) and the organizer sample (NaN).
5. Geotransform origin differs between shipped TIFFs and the organizer sample.
6. Shipped TIFFs have nodata = None; the organizer sample has nodata = NaN.
7. Nine focus files overlap each other at 0.976–1.000; the prompt treats them as distinct submissions.
8. The "Predicted values must be in range [0, 1]" error cannot be reproduced from the shipped bytes.

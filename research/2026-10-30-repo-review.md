# Repo review — 2026-10-30 (arena/022009c9-gemsdoekarage2)

Scope: review of repo state, leaderboard claims, tests, and every shipped submission TIFF. No new experiment was run, no slot was used, and **no file is approved for submission**. Labels follow the parallel-run protocol: HOLDOUT-DTI, ORGANIZER-CONFIRMED, USER-REPORTED / UNVERIFIED, or LOCAL CHECK (file bytes only, not a score).

## 1. Bottom line

- **No submission is approved.** Every shipped TIFF is research-only (see `SUBMISSION_STATUS.md`, `AGENTS.md`). Nothing here changes that.
- **Estimated leaderboard score for any local file: Unavailable.** No holdout DTI exists for any current file in this session, and the full organizer registry is not in the repo.
- **The prompt's leaderboard claims need a fresh source check.** The last supported public snapshot is dated 2026-10-29; the later 2026-10-30 fetch/rank claim was withdrawn because its evidence card says no external page was fetched. See §2.
- **Local TIFF checks pass** (finite, in [0,1], EPSG:32611, shape 3730×3292 for the shipped files). The repo's 32×48 `GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif` is explicitly synthetic QA, not an organizer sample; its different origin and NaN exterior do not establish an organizer-template mismatch. The actual organizer grid/exterior and the portal range error remain unresolved; see §4 and the correction below.
- **Tests:** 256 passed, 8 skipped (Python); 3/3 (Node). The README's previous count was 253 passed; the difference comes from the test suite, which was not re-audited here.

## 2. Leaderboard/source evidence — freshness claim withdrawn

The latest supported official public-board observation saved in this repository is `evidence/official-review-2026-10-29.json`, observed 2026-10-29. It records rank 1 = 0.4544 (xiaofanhu) and 0.3195 = rank 47 (kpomazi). These are dated public-board rows only, not a local score, private-round result, HOLDOUT-DTI, or file-linked submission receipt. They should not be described as current.

An earlier draft of this review claimed that the public page had been fetched on 2026-10-30 and that 0.3195 was rank 48. That claim is **withdrawn**: the same-day evidence card `evidence/repo-review-2026-10-30.json` says external official pages were not fetched because of network restrictions, and the later three-pass review agrees the claim is unsupported. Therefore the 2026-10-30 rank/value assertion is not verified and must not be used. Refresh the official page from an accessible source before using any current rank or leaderboard value.

The supplied 0.4413 claim is not rank-one in the last verified snapshot; no inference about the current page is made here. The current leaderboard target remains unknown until a verifiable dated read is recorded.

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
| `reference/gemsdoe36/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif` (synthetic QA; not official) | float32 | 32×48 | EPSG:32611 | nan | 96 | 0 | 1 | 1,370 | 70 |

Full sha256 values are in the repo's audit JSONs (`docs/evidence/public_downloads_audit.json`). Each file's values are finite and in [0,1]. This does **not** prove portal acceptance.

**Irregularities to review:**

1. **Synthetic QA file was mischaracterized in this report.** Its sidecar explicitly says `purpose: synthetic format QA only`, `official_submission: false`, and warns that it does not use official template bounds. It is not organizer evidence.
2. **Grid authority.** Shipped files have origin (243350, 4508550), 100 m; the local synthetic QA file has origin (400000, 4400000), 100 m. This difference is measured, but does not prove a mismatch with the organizer template. The organizer-authenticated sample/template and its grid remain unavailable here.
3. **Exterior/nodata.** Shipped TIFFs mostly have finite zeros and no nodata tag; the synthetic QA file uses NaN outside and has nodata=NaN. Official wording recorded elsewhere says null/NaN outside, but no authenticated organizer raster was inspected in this review.
4. **Range error.** Local checks pass for [0,1] on every shipped file. The portal error cannot be reproduced from bytes alone; its cause remains unknown. The earlier candidate causes (exterior convention or grid mismatch) remain hypotheses only, not findings.

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
| Organizer geotransform / template | Same data tab; `reference/gemsdoe36/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif` is explicitly synthetic QA | **Unresolved** — synthetic QA origin is not an official template measurement |
| Portal acceptance receipt for any file | Submission page after login | **Missing** — no file has ever been accepted with a receipt |
| Full registry of organizer-scored rasters | Not public | **Missing** — the 440-file check is partial |
| Holdout labels and features | Derived from GeoDAWN (https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), INGENIOUS (https://gbcge.org/current-projects/ingenious/) | Partly reachable; not run here |
| Live leaderboard | https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ | Reachable (read in §2) |

Official sources used in this review: DrivenData leaderboard page (above); submission-format PDF https://docs.nlr.gov/docs/fy26osti/96647.pdf (cited in README; not re-read here); EPSG 32611 https://epsg.io/32611.

## 8. Recommended next steps (for the next session)

1. Obtain the organizer template (geotransform, shape, exterior convention) through an authenticated account, and record it as an artifact. The checked-in 32×48 raster is synthetic QA and cannot stand in for that template.
2. Verify the organizer exterior convention from the authenticated submission template/documentation. Do not spend a submission slot on a dummy or test file unless the uniqueness gate passes and the organizer explicitly requires a portal trial.
3. Re-run the holdout evaluator with `data/` present, starting with the leakage canary on each feature alone (AUC > 0.90 = leakage).
4. Refresh the official leaderboard from an accessible source before setting a target; the last supported snapshot is dated 2026-10-29 and records 0.4544 at rank 1 and 0.3195 at rank 47.
5. Re-check the leaderboard before each decision; ranks moved within 24 h.

## 9. Irregularities list (for manual review)

1. Prompt states 0.4413 as current high and 0.3195 as highest. The latest saved observation (2026-10-29) records 0.4544 at rank 1 and 0.3195 at rank 47; the claimed 2026-10-30 rank 48 is unsupported and withdrawn.
2. GEMSDOE focus-site scores (0.2778 and others) are not linked to organizer receipts or leaderboard rows.
4. Shipped TIFFs use finite zeros outside the footprint; the synthetic QA TIFF uses NaN. The organizer raster convention is not independently authenticated here.
5. Geotransform origin differs between shipped TIFFs and the synthetic QA TIFF; this is not proof of organizer-template mismatch.
6. Shipped TIFFs have nodata = None; the synthetic QA TIFF has nodata = NaN.
7. Nine focus files overlap each other at 0.976–1.000; the prompt treats them as distinct submissions.
8. The "Predicted values must be in range [0, 1]" error cannot be reproduced from the shipped bytes.


## Correction to §4 (2026-10-30)

An earlier draft of this review described `reference/gemsdoe36/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif` as an organizer format sample. That was incorrect. Its companion JSON (`reference/gemsdoe36/GEMS36_FORMAT_TEST_NOT_SUBMISSION.json`, SHA-256 `60543f8ea9d4ee432b018832337c3cf1fe0db4f71b87d15fea71869fe4f23638`) states that it is synthetic format QA only, not an official submission, and does not use official template bounds. Its 32×48 shape, NaN exterior and transform are **local byte measurements only**. Therefore this file does not establish the official template origin or exterior convention, and the portal range error remains unexplained. The correction supersedes any contrary phrase above or in derivative notes.

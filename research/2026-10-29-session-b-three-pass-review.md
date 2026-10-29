# 2026-10-29 session B — three-pass review (GEMSDOEkarage2)

**Result: NO FILE IS OK TO DOWNLOAD AND SUBMIT.** Every candidate in this repository fails the
literal duplicate gate on the full 440-raster focus registry. The two files generated earlier today
were quarantined as DUPLICATE_STOP. No new TIFF was generated. No experiment was run (0 of 3 used).
No competition slot was used or authorised.

Executive summary: <https://karagemop466-tech.github.io/GEMSDOEkarage2/docs/executive-summary.html>
(decision table and full-registry section are generated from the receipts listed below).

## Pass 1 — implement and verify

| Step | Result | Evidence |
|---|---|---|
| Baseline on `main` tip `edb4570` (PR #63) | 14 tests failed. Branch was a shallow graft; main had PR #63 with missing run-card receipts and hand-edited pages. | `git log`, `pytest -q` |
| Restore pinned registry (440 rasters) | All 440 SHA-256 verified against `registry/focus_registry_manifest.json` (367 MB). | `scripts/restore_registry_snapshot.py` |
| Full-registry duplicate check, gw-nfs | **DUPLICATE_STOP**: 438 comparable items, max 3-px overlap **1.0**, 7 witnesses. The top witness is `GEMSDOE24/inputs/calibration/8GEMSDOE_Hedge-v2_submission.tif` (overlap 1.0, rank corr. 0.0188). | `evidence/uniqueness/gemsdoe-karage2-gw-nfs-h1-20261029-zeros.full-registry.json` |
| Full-registry duplicate check, H-A | **DUPLICATE_STOP**: 438 comparable items, max overlap **1.0** vs `GEMSDOE24/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif`; 3 witnesses. | `evidence/uniqueness/gemsdoekarage2-hA-intersection-propensity-aad3569983ab.full-registry.json` |
| Nine best focus files, pairwise recheck from bytes | Max overlap with another focus file: GEMSDOE24 1.0000, 25 1.0000, 27 0.9802, 28 1.0000, 30 1.0000, 31 1.0000, 32 1.0000, 33 0.9971, 36 0.9758. **None is unique.** | `evidence/uniqueness/nine-site-pairwise-recheck.json` |
| Quarantine | gw-nfs and H-A moved out of `docs/downloads/` with `git mv` into `evidence/quarantine/`, so they are no longer served. Bytes unchanged (SHA-256 verified). | `git status` |
| Tests | 234 passed, 4 skipped (Python); Node unit 3/3; Node site 7/7; `build_hk3_pages.py --check` up to date. | `pytest`, `npm test`, `npm run test:site` |

Labels: every number above is an audit measurement on saved bytes. None is a HOLDOUT-DTI and none is an
ORGANIZER-CONFIRMED score. The registry is the nine focus repositories only, not every GEMSDOE site.

## Pass 2 — bugs, edge cases, and irregularities

1. **Pooled holdout evaluator defect (shared tool, fixed once).** `scripts/evaluate_holdout.py::pooled_dti_over_folds`
   scored the whole raster in each fold against that fold's withheld positives. Predictions in other blocks
   counted as false positives in every fold. A perfect predictor scored **0.63**, not 1.0. The fix restricts each
   fold to its active region (block minus visible faults), matching `vendor/gems57/evaluate_holdout.py::evaluate`
   (`active = valid & region & ~known`). Regression tests: `tests/test_holdout_pooling.py` (perfect = 1.0, empty = 0.0).
   **Scope:** the recorded `gems57-pooled-hide-v2` HOLDOUT-DTI values were produced by the vendored evaluator, which
   already restricted each fold, so they are not affected. Only the repo-local copy was wrong.
2. **The executive summary's "UNIQUE: PASS" for gw-nfs was false.** It came from a check against two local rasters
   (`max |rho| = 0.0046`, `max overlap = 0.1954`). The full registry gives overlap 1.0. The PR #63 page is replaced by
   the generator's output, and the claim is retired.
3. **Broken links on the merged page.** The PR #63 page linked `gemsdoe-karage2-gw-nfs-…-run-card.json` and `-audit.json`,
   which do not exist. Fixed by regenerating from the canonical generator.
4. **Hand-edited generated pages (PR #63).** `executive-summary.html`, `index.html`, and `how-to-submit.html` were edited
   by hand and disagreed with `scripts/build_hk3_pages.py`. The generator is now the source again; `--check` passes.
5. **Stale test expectations.** Two tests expected the root `index.html` to link to `docs/index.html`. The root page is
   an intentional redirect to `docs/executive-summary.html` (unchanged from prior main). Tests updated.
6. **Retired generator.** `scripts/generate_unique_submission.py` produced both duplicates and checked uniqueness only
   against locally cached rasters. Its `main()` now refuses to write (`tests/test_retired_unique_generator.py`).
7. **H-A run card discrepancies (flag for review).**
   * `n_positive` is recorded as **2,524**, but only **1,896** of those lie inside the template footprint. The other
     **628** positive cells sit outside the footprint, where the official format requires NaN or null.
   * Its `official_sources.leaderboard` URL is malformed (`…/competitions/306/competitions/306/…`).
   * Its note says "distinct sparse intersection pattern". The bytes contradict this (overlap 1.0 with a GEMSDOE24 raster).
8. **gw-nfs claims contradicted.** Its page said "Dots 30,000, 1–3 px annulus around known faults". The receipt
   confirms 30,000 in-footprint positives. Its registry claim (max overlap 0.1954) is contradicted by the full registry (1.0).
9. **Not comparable registry items (recorded, not dropped).** `GEMSDOE31/…/csdu-stepover-8cf9dc27-nan.tif` has NaN cells inside
   the footprint. `GEMSDOE36/…/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif` has a different grid. Both are listed in every receipt.
10. **Live leaderboard (organizer page, fetched 2026-10-29).** #1 xiaofanhu 0.4544; #2 cfld__ 0.3916. Row #47 is kpomazi.
    The score cell was truncated in this fetch; 0.3195 is the previously recorded snapshot value. The user-cited
    "0.4413" and "0.3195 is highest" do not match the page. Source: <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>.
11. **Owner-mirror template contradicts the official text.** The sample template has 60,988 positive cells, though the
    official problem page says it predicts total absence. It is not organizer-authenticated, so it remains flagged.
12. **Unresolved portal error.** The message "Predicted values must be in range [0, 1]" is still unexplained. Every
    saved file is in [0, 1] inside the footprint. No file is in the organizer-authenticated format, so the cause is unknown.

## Pass 3 — recheck against the original request

| Request | Status |
|---|---|
| Executive summary with a table: file, estimated score, unique vs other GEMSDOE sites | Done in the generator (decision table + nine-site table). Estimates are **Unavailable**, not numbers. |
| A UNIQUE TIF for download and submission | **Not achieved.** Both candidates are DUPLICATE_STOP at 1.0 overlap. Uniqueness here means placing dots away from the saturated registry, and the protocol says not to game that. |
| Obvious whether a file is OK to download and submit | Yes: **NO** on the page, the README, and `SUBMISSION_STATUS.md`. |
| Beat 0.2778 / 0.3195 / 0.4544 | Not testable here. No organizer-authenticated labels or template exist. The catalogue proxy cannot estimate the hidden score. |
| Three experiments, two-hour budget | 0 experiments run. Audits and one shared-tool fix only. |
| Hypotheses before implementation | Existing slate `research/hypotheses-2026-10-29-untried.md` (H-A, H-B, H-C …). H-A was implemented as a file in the prior session, not validated, and fails the gate. See the status note in that file. |
| Labels and no hallucinations | All numbers above are receipts; all links resolve to the official pages or to repo paths. |
| PR and merge to `main` | See the session log below. |

## Remaining work (next session)

1. **Organizer authentication.** Obtain organizer-authenticated `training_features.tif`, `labels.tif`, and `sample_submission.tif` from the DrivenData data tab (login). Without them there is no valid holdout, no template, and no portal evidence.
2. **Explain the portal error.** Submit the organizer sample unchanged, or ask the user which file produced the error. This uses one of three weekly slots.
3. **Real method with an independent signal.** A candidate must pass the literal gate *by its method*, not by excluding registry dots. Options are in `research/2026-10-28-next-lane-slate.md` and H-B/H-C above.
4. **Full live registry.** The focus registry is nine repos. Extend it to every GEMSDOE repo that submits TIFFs, then rerun `scripts/audit_full_registry.py` on the final bytes.
5. **Fix the H-A run card.** Correct the 2,524 vs 1,896 count and the leaderboard URL. The file stays quarantined.
6. **Pre-placement surface receipt.** `scripts/check_uniqueness.py --stage surface` is the protocol's own gate. Its manifest expects an `entries` list and a `complete` flag, which the focus manifest does not provide. Adapt the manifest once in the template.

## Limits

* DrivenData data and submission pages require login. The sandbox cannot reach them (only github.com, codeload, api.github.com, pypi, and npm are allowed).
* Owner mirrors on GitHub are not organizer downloads. Their provenance is unauthenticated.
* The uniqueness check uses saved bytes and a nine-repo registry. It is not the live parallel-run registry.
* A pass on the gate would not establish a leaderboard score. Only the organizer's submission-page receipt does.

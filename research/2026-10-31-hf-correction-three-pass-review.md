# Three-pass H-F correction review — 2026-10-31

**Branch:** `arena/9e73af8a-gemsdoekarage2`
**Decision:** **NO APPROVED SUBMISSION.** This pass reconciled the existing H-F research artifact and its claims. It did not run the H-F/H-G generators, run a geological experiment, create a TIFF, estimate a competition score, upload, or use a submission slot. No method paragraph/lane is assigned; authenticated organizer inputs/template and complete current registry evidence remain unavailable.

## Pass 1 — requirement and claim review

Read `README.md` and `AGENTS.md` first. The binding protocol still prohibits a new geological experiment or candidate TIFF without an assigned method paragraph/lane and authenticated inputs. Existing files are research-only. The current site puts the negative release decision first and labels its visible HK3 download research-only; it does not feature H-F as an approved download.

Traced the H-F claim across the README, saved run card, saved audit sidecar, `docs/data/focus-sites.json`, the archived dashboard that links that JSON, and the public download inventory. The earlier text incorrectly stated that the TIFF hash was `4fe3104c…`, that strict format passed, that 7 local comparisons established uniqueness, that `0.018385` was HOLDOUT-DTI with a confidence interval, and that the combined-score AUC cleared leakage. Those claims are withdrawn. The H-F row now has `unique: null`, `submit: false`, and an explicit correction link; the archived page carries a prominent research-only correction link.

The claimed H-F input mapping was also checked against the actual local generator and pinned owner-mirror manifest. The generator's curvature function receives band 12 (`detrend`), not band 1. The prototype claims bands 4/6/5 are K/eTh/eU-ratio channels, while the owner-mirror manifest names bands 4/5/6 `geod_2ndinv` / `iso_grav_anom_slope` / `tc`. This contradicts the claimed radiometric mapping. The manifest is an owner mirror, not organizer-authenticated metadata; no official band semantics are inferred.

## Pass 2 — saved-byte and provenance reconciliation

Re-read the existing TIFF bytes with Rasterio and independently computed the SHA-256. The 806,001-byte TIFF is single-band float32 GTiff, 3730×3292, EPSG:32611, with the pinned owner-mirror transform. Every raster value is finite and in [0,1]; the array has 12,279,160 finite pixels, zero NaNs/infinities/masked pixels, and 18,000 positive pixels. The actual SHA-256 is:

`e9ea035c8d12d848807c3b71875c8031ca8b49b33f21150ac62e4e7f67c04224`

That hash matches the current run card, the saved-byte audit sidecar, and the correction record. The prior run-card, audit-sidecar and focus-sites JSON hashes in the correction record were also checked against revision `26a677c4f61f4f1676cfcdf0cc4271aa4884d248` using `git show`.

Against the **unauthenticated** owner-mirror footprint count of 5,167,373 pixels, 7,111,787 cells are outside. Because the full saved raster contains no NaNs, those outside cells are finite and the local strict outside-NaN check fails. This is not organizer-template authentication and does not establish the cause of any portal error.

The stored H-F DTI, fold range, leakage AUCs, and seven-raster comparisons were not rerun: the cached feature/label mirrors and complete registry are absent. The correction preserves them only as historical recorded diagnostics. In particular, `0.018385` is a fixed-field diagnostic using full-catalogue fault distance, not protocol-compliant whole-segment hide-and-recover HOLDOUT-DTI; `[0.0086, 0.0384]` is a four-fold range, not a 95% CI. The recorded fault-proximity feature-alone AUC is 1.0 (`leakage: true`), regardless of the combined-score AUC. Only 7 of 472 reported registry rasters were compared; 465 were unavailable, and no pre-placement surface-overlap receipt exists. Global uniqueness is not established.

The detailed machine-readable evidence and scope limits are in [`evidence/hf-correction-2026-10-31.json`](../evidence/hf-correction-2026-10-31.json).

## Pass 3 — implementation, regression, and release checks

- Corrected the README, H-F run card, audit sidecar, archived focus-site row and public archive link. The correction record is hash-bound to the unchanged TIFF and prior revision receipts.
- Hardened `scripts/audit_public_downloads.py`: the H-F inventory entry requires the expected evidence-directory correction record and checks that its artifact path/hash and negative release fields match. A missing, changed, or path-escaping correction fails closed. All 10 inventory entries remain research-only.
- Retired the H-F/H-G generator entry points with explicit `SystemExit` guards and updated the comments that previously described the unverified H-F channels as radiometric. Added regression tests proving the entry points cannot proceed to output generation.
- Tests: Python **261 passed, 8 skipped, 98 subtests passed**; the skips require optional pinned owner-mirror inputs not restored. Node feed tests **3 passed**, site tests **8 passed**, and browser smoke checks passed at 1440/390/320 px. Release assessment remains negative / `slot_authorized: false`; public-download inventory is `PASS_RESEARCH_ONLY`, with `downloadable_approved_submission: null`. The page/build, protocol, audit, compile and shell checks completed successfully. Rasterio emitted 99 existing Affine-multiplication deprecation warnings.

## Existing project deliverables and constraints

- The nine-site best-file/reported-score/uniqueness comparison remains in [`docs/experiment-index.html`](../docs/experiment-index.html), with per-site pages under `docs/sites/`. The historical scores are user-reported/unverified, leaderboard estimates remain unavailable, and the pinned uniqueness audit blocks resubmission; GEMSDOE32's 0.2778 claim is not an upload recommendation.
- The four qualitative next-lane proposals remain in [`research/2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md). They describe transforms, missing-catalogue rationale, mimics/controls, differences and cost, but are proposals only—not a newly assigned lane, not all globally novel, and not validated in this pass. Any future top-method test requires the shared cached stack/evaluator/writer, buffered whole-segment hide-and-recover, visible-fault-only catalogue features, pixel-exact masking, per-feature leakage canaries, a paired spatial 95% CI, and pre-placement plus final registry checks. Stop on correlation >0.90 or >70% three-pixel overlap. Promotion remains separate.
- The current instructions for an eligible future upload are [`docs/how-to-submit.html`](../docs/how-to-submit.html). No file currently meets the release gates; do not use any existing TIFF for a competition slot.
- Official links and the dated public-leaderboard snapshot are preserved in [`evidence/official-review-2026-10-30.json`](../evidence/official-review-2026-10-30.json). They were not refreshed in this correction; the snapshot is not a file-linked submission receipt.

## Open PR review context

PR [#87](https://github.com/karagemop466-tech/GEMSDOEkarage2/pull/87) remains open on a different Arena branch and its three reported checks pass. It overlaps this H-F correction and the generator-safety changes, so a second PR should not be treated as independent work. In reviewing its proposed H-F wording, two claims need care before merge: the H-F metric should be labeled a legacy fixed-field diagnostic rather than HOLDOUT-DTI (even “proxy”), and the H-F source passes band 12 `detrend` to `curvature_convergence`—band 1 is loaded only for a missing-input mask. No changes were made to PR #87 from this branch, and this review did not merge it.

# Arena session review — 2026-10-31

## Outcome

**NEGATIVE — no submission candidate approved.** This session reviewed the existing project and reran software checks. It did not generate a raster, run a geological experiment, estimate a leaderboard score, use a submission slot, or upload a file. Every existing downloadable TIFF remains research-only; do not submit it.

The checkout already contains the consolidated objective, nine-site scorecard, submission instructions, official-source links, historical evidence, and fail-closed download controls. The focus-site values are historic owner/user reports, not organizer receipts. The public-board capture in `evidence/leaderboard-recheck-2026-10-31.json` is dated 2026-10-31 and is explicitly a public-test snapshot, not a score for any local TIFF. No new live-source fetch was made in this session.

## Reproducible checks performed

- Installed the pinned Python dependencies in ignored `.venv/` from `requirements.lock.txt`; installed Node dependencies with `npm ci` (audit reported 0 vulnerabilities).
- `.venv/bin/pytest -q`: **257 passed, 8 skipped, 98 subtests passed**. Rasterio emitted pending-deprecation warnings; no test failed.
- `npm test`: **3 passed**.
- `npm run test:site`: **8 passed**.
- `npm run test:browser`: passed at 1440, 390, and 320 px; checks confirmed fail-closed wording, research-only download label/bytes, navigation, nine-row table, no overflow, and safe freshness states.
- `.venv/bin/python scripts/readiness.py`: exited 0.
- `.venv/bin/python scripts/audit_nine_site_best.py`: **blocked** because `.cache/gems_data/sample_submission.tif` is absent. The command raised `RasterioIOError`; no fresh nine-raster geometry audit is claimed.

## Scientific/competition gates and blockers

`data/`, the authenticated organizer template, and the cached feature stack are absent. No single method paragraph is assigned. Consequently no candidate can be held out under the mandated whole-segment buffered protocol, no feature-only leakage canary can be computed, and no true submission TIFF can be validated against organizer-provided CRS/shape/transform. The exact source of the prior portal error (“Predicted values must be in range [0, 1]”) remains unverified. Existing mirror/synthetic rasters are not substitutes for authenticated organizer inputs.

The previously recorded uniqueness policy also remains a blocker: dense registry rasters can exceed the literal 70% within-3-px stop threshold. Do not weaken the threshold, select a placement in its holes, or infer uniqueness from a partial/currentness feed. The GitHub source monitor covers repository-head metadata, not DrivenData scores or each current-head raster's contents.

## Requirements check (three passes)

1. **Completeness:** confirmed existing README, nine focus-site pages/scorecard, submission guide, evidence, shared evaluator/writer/validator, and ranked research material. No fake “best submission” is recommended.
2. **Correctness/edge cases:** repeated unit, site, and browser checks; fail-closed behavior is covered. The nine-site byte audit cannot run without its organizer sample input; this is a documented inability, not a pass.
3. **Protocol/claim audit:** zero experiments (within the max-three/two-hour budget); zero slots; no numbers presented as a new HOLDOUT-DTI or organizer-confirmed score; no TIFF generated; negative decision retained.

## Next action

Before a scientific run: obtain authorized organizer data/template, hash and provenance-check the inputs, assign exactly one method paragraph, resolve the literal registry interpretation without gaming, and then evaluate the preregistered top hypothesis with the shared hide/recover evaluator and leakage canary. Only a candidate that beats the matched holdout baseline and passes preplacement/final-dot and template validation may reach a separate quota-aware selector. No upload should be automated.

Official references for manual review remain linked in `README.md`, including the DrivenData problem description/data/leaderboard, NLR rules PDF, reference solution, USGS GeoDAWN, INGENIOUS and GEMSDOE32 owner page. The owner page is not an organizer receipt.

## Run card

See [`../evidence/arena-session-review-2026-10-31.json`](../evidence/arena-session-review-2026-10-31.json). This is a software/repository review card, not an experiment card.

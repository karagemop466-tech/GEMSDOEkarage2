# Repository review — 2026-10-30

**Scope:** review of the checked-out repository on `arena/2b5a0fa0-gemsdoekarage2` against its README operating protocol and submission-safety requirements. **No geological experiment, TIFF generation, upload, or slot selection was performed.**

## Decision

**NO APPROVED SUBMISSION. Do not upload any TIFF in this repository.** The current submission-status record explicitly says no file is approved. The requested high-score/unique TIFF cannot responsibly be produced from this checkout: there is no authenticated organizer data/template, and the repository's recorded uniqueness gates reject prior candidates. No new score estimate can be supported from these conditions.

## Review findings

1. **Safety controls are explicit and tested.** The README and `SUBMISSION_STATUS.md` distinguish historical/user-reported scores from organizer receipts, forbid submitting research rasters, and require holdout, uniqueness, format, and separate selector gates. Existing generator safety tests and site tests reinforce fail-closed publication.
2. **The requested nine-site scope is represented.** The dashboard includes the specified focus sites; historical scores are marked unverified rather than converted into estimates for a new file. The cited GEMSDOE32 value of 0.2778 remains a user-reported historical observation in repository documentation, not an authenticated receipt establishing why the raster scored that value.
3. **No current candidate merits promotion.** The recorded audits are negative/incomplete; some registry snapshots are explicitly incomplete or stale relative to upstream site heads. A non-duplicate result against a partial registry would not prove uniqueness against the full set. The 2026-10-29 leaderboard snapshot is historical and is not a local candidate score.
4. **Documentation freshness needs attention.** README and status sections are dated 2026-10-29 or earlier, while this review is dated 2026-10-30. These are properly labeled dated observations, but the home page and summary should continue to make their “as-of” time conspicuous and avoid wording that implies a live DrivenData feed. The repo's network-access limitation prevents checking DrivenData, USGS, DOE GDR, or NLR pages in this environment.
5. **No code defect demonstrated in this review.** The existing review status and validation artifacts are internally consistent on the key decision: no approved download. This review did not regenerate site assets or alter the existing TIFF files.

## Verification performed

- Python: `256 passed, 8 skipped, 98 warnings, 98 subtests passed` via `.venv/bin/python -m pytest -q`. Skips correspond to optional/unavailable inputs; they are not proof of organizer-data validation. Warnings are Rasterio affine multiplication pending-deprecation warnings.
- Node feed tests: `3 passed` (`npm test`).
- Node site tests: `8 passed` (`npm run test:site`).
- `git diff --check` and JSON parsing of the review card inputs passed before this review record was added.
- Dependencies were installed in local `.venv` and via `npm ci`; neither modifies tracked source files.

## Required next work (fail-closed)

1. Secure participant-authorized, authenticated competition rasters and the exact organizer submission template; record provenance and hashes. Do not treat mirrors as organizer-authenticated.
2. Assign one method paragraph/lane and check the budget before any experiment. Reuse the shared cached stack, evaluator, and writer; do not fork the protocol.
3. Freeze a valid spatially blocked holdout and incumbent; run per-feature leakage canaries before trusting a candidate. Withhold whole buffered fault segments, derive catalogue features from visible faults only, and mask visible faults pixel-exactly.
4. Audit the candidate surface against a complete immutable registry before placement and the final raster after placement. Stop on either duplicate threshold.
5. Report HOLDOUT-DTI with evaluator version, withheld-positive count and defensible 95% CI; do not label it an organizer leaderboard score. Run the strict template/CRS/shape/transform/range/NaN validator and keep portal acceptance explicitly unknown until confirmed by an organizer receipt.
6. Only a separate, quota-aware selector may promote a candidate after all gates pass. Negative results remain useful deliverables.

## Source and access caveat

This review did not verify external pages live; network policy in this environment only permits GitHub, npm, and PyPI hosts. Manual source links retained in the project include the [official competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/), [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [participant data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/), [official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), and [USGS GeoDAWN dataset page](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and). These links are for manual review, not evidence of fresh verification in this run.

**Run card:** [`../evidence/repo-review-2026-10-30.json`](../evidence/repo-review-2026-10-30.json).

# Repository review — 2026-10-30

**Branch:** `arena/a53b600e-gemsdoekarage2`
**Review type:** three-pass repository and release-safety review; no geological experiment.
**Decision:** **NO APPROVED SUBMISSION. No new TIFF was generated. Do not submit any repository download.**

## Executive disposition

The site/repository already contains a nine-site historical scorecard, detailed pages for GEMSDOE24/25/27/28/30/31/32/33/36, a submission guide, source references, automated freshness checks, research-only downloads, shared holdout/validator/writer tools, and fail-closed uniqueness/release checks. The current status is deliberately not an upload recommendation. GEMSDOE32's 0.2778 is a user-reported historical value, not established by a file-linked organizer receipt; it cannot support a score estimate for a newly generated raster. No reliable leaderboard score estimate for a candidate is available.

The task's operative method paragraph is absent: it gives thresholds and a protocol but does not name a method. The parallel-run rules also require an assigned single lane and prohibit exceeding the stated experiment/time ceiling; historical review evidence says the prior HK3 lane is stopped. No new geological experiment, TIFF, competition slot, or score claim was made. This is a protocol stop, not a claim that an improved submission is impossible.

## Three review passes

### Pass 1 — repository, product and evidence

Inspected the root README, project guidance, submission status, evidence/run cards, source and registry manifests, site routes, relevant scripts and tests. Confirmed that the existing public pages conspicuously distinguish research-only files from approved submissions and that there is no authorized submission file. Existing downloadable TIFFs are research artifacts, not safe-to-submit recommendations. The local file validator explicitly labels its upstream sample as an unauthenticated owner mirror and returns no official-compliance or upload authorization. This guards against falsely treating format checks as portal acceptance.

The request's highest-score framing is not evidence of causality. The claimed GEMSDOE32 value is not a linked receipt; the historical forensic explanation is qualified as inference. Previously recorded public leaderboard snapshots are dated observations, not scores for these local bytes, private-round outcomes, or a current live feed. No external source pages were re-fetched during this review; do not describe old snapshots as refreshed.

### Pass 2 — tests and implementation checks

- Python locked environment: `.venv/bin/python -m pytest -q -rs` — **256 passed, 8 skipped, 98 warnings, 98 subtests passed**. Skips are documented mirror-backed tests whose inputs are not restored in this checkout. Warnings are Rasterio `PendingDeprecationWarning` instances around affine transform arithmetic; no test failures.
- `npm test` — **3 passed**.
- `npm run test:site` — **8 passed**.
- `npm run test:browser` — passed desktop/mobile checks at 1440, 390 and 320 px, download-byte hash verification, nine-row summary, fail-closed freshness states, and no tested viewport overflow.

Initial test attempts exposed environment setup gaps (no pytest/venv and no installed `jsdom`); these were resolved using the checked-in Python lockfile and `npm ci`. No tracked dependency or generated-data changes resulted. No implementation bug was established by these tests. They verify local behavior, not geology, organizer data identity, portal acceptance, or hidden-label performance.

### Pass 3 — acceptance criteria and limitations

| Requirement | Result |
|---|---|
| Review the nine named project sites | Existing summary and individual pages cover all nine. Their supplied historical scores remain unverified/user-reported unless a receipt says otherwise. |
| Clearly identify the best *supported* submission | No submission is approved; do not download and submit any current artifact. |
| Estimate candidate competition score | Unavailable. A holdout metric cannot be relabeled as a leaderboard projection absent validated calibration. |
| Create unique TIFF, test surface before placement and final dots | Not done: no named method lane, no candidate surface, and no full authenticated registry/template clearance. Do not fabricate test results. |
| Holdout, leakage canary and CI | No experiment in this review, hence no new HOLDOUT-DTI, withheld-positive count, confidence interval, or canary result. |
| Current automatic official feed | Not demonstrated. Existing feed checks public GitHub metadata; it is not an authenticated, continuously refreshed DrivenData score/submission feed. |
| PR and merge | This review is documented in this branch. Merge is conditional on successful PR checks and may not be possible if repository policy requires review/CI. |

## Follow-up, in order

1. Obtain an explicit method paragraph/lane assignment and confirm its status against prior sessions and the three-experiment/two-hour budget. Do not infer it from the list of hypotheses.
2. In an authorized environment, acquire the organizer's official grid/sample/labels and preserve provenance and hashes. Resolve the exact NoData/exterior convention and earlier `[0,1]` upload error with the actual official sample; owner mirrors are not a substitute.
3. Build and independently verify a complete, immutable registry of prior submissions. Run the prescribed pre-placement correlation and proximity tests before dots, and final-dot tests afterward; missing registry entries must fail closed.
4. If authorized and still within budget, preregister the hypothesis and baseline, use the shared cached feature stack/evaluator/writer, withhold whole buffered fault segments, derive catalogue features only from visible faults, mask visible traces pixel-exactly, run each feature alone as leakage canary, and report pooled DTI with 95% CI and withheld-positive count. Compare against a frozen same-fold baseline and preserve negative results.
5. Keep promotion and slot selection separate. Only consider a submission slot after scientific and uniqueness gates, template-format checks, provenance, and organizer rules/quota are independently satisfied.
6. Build a genuinely current DrivenData feed only through an authorized route, with timestamps and explicit unavailable states. Never imply that a public leaderboard row identifies the score of a local raster.

## Official reference links for manual review

- [Competition rules/overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem description and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [About page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Competition data page (login may be required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)

## Run card

```json
{
  "hypothesis": "None tested: no concrete method paragraph/lane assignment was supplied.",
  "mechanism": "Three-pass repository review and local software/site test execution only; no prediction surface or raster generated.",
  "named_non_fault_process_that_could_mimic_it": "Not applicable; no candidate geological mechanism was tested.",
  "holdout_dti": null,
  "holdout_evaluator_version": null,
  "withheld_positive_count": null,
  "ci95": null,
  "correlation_overlap_vs_registry": "Not measured for a new candidate; no surface/final dots exist. Existing registry evidence is historical and not complete proof of all parallel submissions.",
  "raster_sha256": null,
  "validator_output": "No new raster. Existing validator checks against a hash-pinned owner mirror and explicitly sets official compliance and submission authorization to null/false.",
  "submission_name": null,
  "submission_note": null,
  "verdict": "negative"
}
```

# Repository review — 2026-10-29

## Scope and decision

This is a three-pass **read-only code/science review** of `arena/877edd2e-gemsdoekarage2`; this report and its README pointer are the only documentation changes. I read `README.md`, `AGENTS.md`, the submission-status notice, the current evidence/run cards, the site generator, the shared release/readiness policy, and the current public desk pages. No scientific experiment, prediction TIFF, submission slot, portal upload, PR, or competition-score estimate was created by this review.

**Release decision: NO APPROVED SUBMISSION — DO NOT SUBMIT any existing project TIFF.** The existing controls explicitly treat all of them as research artifacts. The current executive-summary page says “OK TO SUBMIT: NO,” gives no leaderboard estimate for a candidate, and labels old site values `USER-REPORTED / UNVERIFIED`. This agrees with `SUBMISSION_STATUS.md` and the corrected HK3 run card.

## Pass 1 — understand and verify current state

- The repo has a public-facing nine-site executive summary, individual pages, submission instructions, evidence/source pages, pinned historical-raster manifests, run cards, and code/tests for readiness, GeoTIFF checks, uniqueness audits, source feeds, and publication inventory.
- The four focus-page values in the provided list can be found in the repo's historical-site material. The highest supplied claim is GEMSDOE32 `0.2778`, but the repo correctly classifies it as `USER-REPORTED / UNVERIFIED`; it is not an organizer receipt and does not provide a calibrated estimate for a new submission. Per-site candidate leaderboard estimates are `Unavailable` in the desk.
- The saved HK3 witness is a historical, negative example: the current audit card records **45,046 / 45,108 dots (99.8626%) within 3 px of a registered lattice**, above the literal 70% stop. Its stored earlier holdout value is labeled `HOLDOUT-DTI` (evaluator `gems57-pooled-hide-v2`, 58,258 withheld positives, 95% CI `[0.1676914118, 0.2014839638]`); it is not an organizer score and was not rerun here.
- `scripts/hk3.py` is retired, and the project instructions prohibit restarting that lane. The repo's ranked hypotheses are proposals, not assigned lanes or validated experiments. The current session card correctly records nulls for candidate score, raster hash, and submission name.
- There is no `data/` competition bundle in this checkout. The pinned public owner mirrors are not present in the lightweight local cache and are not authenticated DrivenData inputs. The official submission template, current complete fleet registry, current account quota, and upload receipt are not established here.

## Pass 2 — bugs, missing evidence, and edge cases

- I found no failing release-safety or site test in the available local suite. The negative selector and publication adapter fail closed, and `audit_public_downloads.py --check` returned `PASS_RESEARCH_ONLY` with 7 artifacts and `downloadable_approved_submission: null`. This means local integrity checks passed; it does not approve a file.
- Python tests skip 8 input-dependent cases because pinned mirrors/shared inputs are not restored. The test report is **221 passed, 8 skipped, 98 subtests passed**; Rasterio emitted 90 pending-deprecation warnings. The skips leave the mirror-dependent byte/geometry/shared-validator integration checks unverified in this checkout.
- Node checks passed: 3 feed tests, 7 site tests, and browser smoke checks at 1440 px, 390 px, and 320 px. The browser check confirmed the page's negative status, research-only download hash, nine-site table, and no viewport overflow at the tested widths.
- `scripts/build_hk3_pages.py --check`, Python compilation, shell syntax checks, and `git diff --check` passed. There were no uncommitted changes at the start of review.
- The previous [independent review](2026-10-28-independent-three-pass-review.md) and [protocol correction](hk3-protocol-correction-2026-10-28.md) remain the substantive geometry/provenance analyses. I did not independently retrieve public site TIFFs or official competition pages during this review, so their dated source snapshots are not refreshed by this report.

## Pass 3 — compare against the request

| Requirement | Review result |
| --- | --- |
| Clear nine-site executive summary and explain the apparent GEMSDOE32 lead | Present. The hypothesized pruning explanation is explicitly non-causal/uncertain; historical number is unverified. |
| Estimate a score for a new TIF | Not supported by validated evidence. Correctly unavailable; a holdout value is not represented as leaderboard score. |
| Generate a new, unique, downloadable TIF | Not done. This is intentional: no assigned method paragraph, complete literal registry clearance, authenticated organizer input/template, or current slot evidence; previous lane has an explicit mandatory stop. Creating a raster now would violate the stated lane/uniqueness controls. |
| Automated validation, including `[0,1]` | The repo provides format and saved-byte checking and tests. No new candidate existed to validate against the organizer's authenticated grid; local pass is not portal acceptance. |
| Source verification and current feed | Pinned source/evidence links and a GitHub-metadata freshness path exist. This review did not refresh official organizer sources; current official leaderboard/quota cannot be inferred from the stored 2026-10-28 snapshot. |
| Three review passes | Completed in this report. No experiment was run, so no experiment run card is applicable; the existing read-only audit card remains authoritative for its historical scope. |
| New PR and merge | This review adds only the dated audit report and a README pointer; it changes no product code or scientific artifacts. PR/merge is the requested next repository operation after final checks. |

## Next steps — blockers, ordered

1. **Do not create or upload a candidate until an assigned single-method lane is supplied by the session's controlling protocol and its full scope is recorded.** Review the extant proposal slate against subsequent work first; do not infer novelty from a new filename.
2. Obtain official competition data and the organizer submission grid from the authenticated competition page in an authorized environment; record provenance/hashes and resolve the mirror/example inconsistency and exterior NoData convention.
3. Produce a complete, immutable all-registry snapshot and perform literal surface clearance before placement. Missing/invalid references must fail closed; do not exempt the spacing lattice or game uncovered pixels.
4. Only after the preconditions: use the shared cached stack/evaluator/writer; preregister a hypothesis; run the feature-alone leakage canaries; withhold buffered whole segments and mask visible faults exactly; compare pooled DTI against a frozen same-fold incumbent with a paired 95% interval. Stop at 3 experiments or 2 hours.
5. If every scientific, format, uniqueness, provenance, and policy gate passes, make a separate quota-aware selector decision. It must not automatically choose a real competition slot. Keep score estimates null absent a sound calibration protocol; only an actual submission-page receipt is `ORGANIZER-CONFIRMED`.

## Reproduction commands

```sh
.venv/bin/pytest -q -rs
npm test
npm run test:site
npm run test:browser
.venv/bin/python scripts/build_hk3_pages.py --check
.venv/bin/python scripts/audit_public_downloads.py --check
```

The tests run in this review used the pinned Python lockfile and `npm ci`. Restore pinned owner mirrors only if replaying the optional research integration tests; these mirrors are not organizer-authenticated competition data.

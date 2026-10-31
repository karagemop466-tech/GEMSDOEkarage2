# Repository review — 2026-10-31

## Decision

**NEGATIVE: no TIFF is approved to download and submit.** No candidate raster was made, no geological experiment was run, and no competition slot was selected or used. This is a review of the current checkout, not a claim about current site-head raster contents or organizer scoring.

The repository already carries the requested consolidated project prompt in `README.md`, a nine-site executive scorecard, a submission guide, a fail-closed release inventory, a ranked hypothesis slate, shared holdout/writer/validator tools, and dated evidence. Review of the entry point and current status documents confirms that existing research TIFFs are marked **RESEARCH ONLY / DO NOT SUBMIT**. There is no currently approved one-click submission file.

## Pass 1 — inspect and verify

- Read `README.md`, `SUBMISSION_STATUS.md`, `AGENTS.md`, the focus-site executive summary and submission guide, current release/audit scripts, registries, and dated review evidence.
- The repo's latest source claims are explicitly timestamped 2026-10-30. Those observations are not refreshed in this review; do not describe them as a current 2026-10-31 leaderboard or live audit.
- The user-provided focus-site values are tagged USER-REPORTED / UNVERIFIED in the existing scorecard. The historical maximum is GEMSDOE32 0.2778 as supplied, not an organizer-receipt-verified result. A leaderboard estimate for a new raster is unavailable.
- `data/` and `.cache/competition_data/` are absent. The competition's data page requires authorized login per the existing recorded check. Thus there is no authenticated template/feature stack available in this checkout for a legitimate holdout experiment, final template validation, or TIFF creation.
- The current protocol says experiments must remain within a single assigned method paragraph. No uniquely assigned paragraph is present in this review request; inventing a lane would violate that protocol. Prior reviews also record a duplicate-stop conflict with the dense lattice witness and require resolving it without gaming placements.

## Pass 2 — tests and edge cases

Installed repository-pinned Python dependencies in the ignored local `.venv` and npm dependencies from the lockfile; no dependency files were changed.

- `.venv/bin/pytest -q`: **257 passed, 8 skipped, 98 subtests passed**. The eight skips are optional integration checks whose raster inputs are not present. Rasterio emitted deprecation warnings; no test failed.
- `npm test`: **3 passed**.
- `npm run test:site`: **8 passed**.
- `npm run test:browser`: passed at 1440, 390, and 320 px; research-only warnings, navigation, nine-row table and fail-safe freshness states were checked.
- `.venv/bin/python scripts/readiness.py`: exited 0.
- `.venv/bin/python scripts/audit_nine_site_best.py`: **could not run**; the required `.cache/gems_data/sample_submission.tif` is absent. The existing audit receipt remains historical evidence, not a fresh rerun.
- `data/` is absent, so no direct training/holdout, feature-only leakage canary, preplacement/final-dot registry audit, authenticated-template comparison, or output-value validation can be truthfully reported now.

## Pass 3 — requirements and factual limits

| Requirement | Review result |
|---|---|
| Read and retain the full project objective | Already included in `README.md`; this review does not duplicate its long prompt. |
| Nine-site executive summary, file, score class, uniqueness and submit verdict | Present in the existing summary. Values are owner/user claims, not organizer-confirmed receipts; no new-file score is estimated. |
| Easy-to-find downloadable submission | UI is clearly fail-closed; its available artifact is research-only, not safe to submit. No approval is implied. |
| New, unique, validated TIFF | **Not produced.** Required authenticated data/template are absent; no lane is assigned; uniqueness policy conflict remains. Making a synthetic or copied TIFF would be misleading. |
| Proposed geological hypotheses, ranked and scientifically falsifiable | Existing 2026-10-30 review has four ranked proposals with layers, mechanisms, novelty boundaries, and mimics; earlier audit has additional controlled tests. These are proposals, not validated experiments. |
| Holdout-before-slot, leakage checks and three-experiment/two-hour budget | No slot used. No holdout run is possible without data and lane assignment. Do not call prior scores or user-reported leaderboard results HOLDOUT-DTI. |
| Sources and currentness | Official source links are in README and the site. This review did not fetch external pages; the dated public observation remains 2026-10-30. |
| Automated current feed | The existing feed checks GitHub repository-head metadata only; it does not refresh DrivenData scores or raster files. This limitation is prominently documented. |
| Pull request and merge | To be attempted from the fixed Arena branch after this report is added. Merge is only valid if GitHub permits it and checks pass; no alternate branch will be used. |

## Irregularities / remaining blockers

1. Missing organizer-authorized competition rasters/template and feature stack. Public owner mirrors are not equivalent evidence.
2. `audit_nine_site_best.py` needs `.cache/gems_data/sample_submission.tif`; it was not refreshed in this run.
3. The literal uniqueness threshold against an exceptionally dense registry witness can make the permitted lane infeasible. The review will not alter the threshold or place dots in witness holes to bypass it.
4. No new experiment method paragraph was assigned. Holdout measurements without a specified lane would not satisfy the user's protocol.
5. The current site feed is not a live DrivenData leaderboard feed. Competition-page authentication and the weekly submission cap cannot be observed from this workspace.
6. Existing leaderboard values and submission-result values in project notes are dated observations or user/owner claims; none proves performance or acceptance of a new local TIFF.

## Next session priorities

1. Assign exactly one method paragraph and document the registry threshold interpretation before experimentation.
2. With authorized access, restore and hash the actual organizer data/template; preserve provenance and ensure the sample/reference discrepancy is resolved.
3. Run the shared whole-segment buffered hide-and-recover evaluator on a fixed incumbent; derive catalog features only from visible segments and mask visible positives pixel-exactly. Test each feature alone for AUC leakage before trusting combinations.
4. Run only the top preregistered hypothesis, compare pooled DTI with a justified 95% CI, and stay within 3 experiments or 2 hours.
5. Run preplacement and final saved-dot duplicate audits against a complete current registry; if either limit trips, stop and record negative.
6. Only after all gates pass and a separate quota-aware selector approves: write with the shared writer, validate actual TIFF bytes against the authenticated template and [0,1] constraint, and make the download explicitly approved. No automated upload is authorized.
7. Refresh official sources with dated evidence; keep public leaderboard values distinct from HOLDOUT-DTI and ORGANIZER-CONFIRMED receipts.

## Official references already linked in the project

- [DrivenData problem description and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData data tab (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [GEMS reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [NLR official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS](https://gbcge.org/current-projects/ingenious/)
- [GEMSDOE32 owner page (not an organizer receipt)](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)

## Run card

See [`evidence/repo-review-run-card-2026-10-31.json`](../evidence/repo-review-run-card-2026-10-31.json). No score, raster hash, validator result for a candidate, or submission name is claimed because no candidate exists.

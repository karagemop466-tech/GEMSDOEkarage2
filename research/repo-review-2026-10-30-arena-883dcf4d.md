# Repository review — 2026-10-30

**Scope:** current checkout and its nine-site executive-summary/download workflow. This is a three-pass repository and evidence review; it is not a geological experiment, submission selection, or source-data refresh.

**Decision: NO APPROVED SUBMISSION.** No new TIFF, experiment, holdout score, leaderboard estimate, upload, or competition slot was produced or authorized. Do not download any repository TIFF as a competition submission. Historical artifacts remain research-only.

## Executive findings

| Priority | Finding | Evidence / impact |
| --- | --- | --- |
| Blocker | No eligible submission is available. | `scripts/audit_public_downloads.py --check` reports `PASS_RESEARCH_ONLY`, nine artifacts, and `downloadable_approved_submission: null`; the site displays `OK TO SUBMIT: NO`. The audit is a local integrity check, not organizer acceptance. |
| Blocker | A fresh scientific candidate cannot be justified in this review. | The binding protocol has no assigned single method paragraph; the prior HK3 lane is retired and its stated experiment/time budget is exhausted. Its literal registry overlap stop cannot be waived. No new hypothesis was selected or tested. |
| High | Competition data/template, current complete registry and portal evidence are not established here. | The cached competition-data directory is absent. Existing mirror inputs are owner mirrors, not organizer-authenticated data. Local format and grid checks cannot certify portal acceptance. |
| High | The result feed is not a live DrivenData feed. | Existing automated freshness checks are GitHub metadata checks. The saved official leaderboard observation is dated 2026-10-29 and must not be presented as current on 2026-10-30. No account quota or current score receipt was checked. |
| High | A merged README leaderboard assertion conflicts with its own evidence. | The merged top-level README said a live leaderboard had been fetched on 2026-10-30, while `evidence/repo-review-2026-10-30.json` explicitly says external official pages were not fetched because of network restrictions. I withdrew the unsupported freshness claim in README; this review does not certify the later date/rank. |
| Medium | Eight data-backed tests did not run. | The Python suite skipped eight optional owner-mirror/shared-template integration tests because pinned mirror inputs are not restored in this checkout. Those behaviors remain unverified in this run. |
| Medium | The nine-site numbers are historical, user-reported claims. | In the supplied comparison, GEMSDOE32's 0.2778 is the largest stated value among the nine focus sites, but is **USER-REPORTED / UNVERIFIED**, not an `ORGANIZER-CONFIRMED` file-linked receipt. It cannot support a score estimate for a new raster. The site correctly leaves a new-file estimate unavailable. |

No concrete code defect was reproduced in the locally runnable checks. This does not clear the optional skipped integration paths, authenticate inputs, or establish scientific validity.

## Three review passes

### Pass 1 — inventory and intended behavior

Read `AGENTS.md`, the consolidated prompt in `README.md`, `SUBMISSION_STATUS.md`, the current site pages, current release/selector evidence, the nine-site byte-audit records, and the pinned run cards. Confirmed that the published executive summary identifies the focus sites, links historical files, marks scores unverified, separates score estimation from historical values, and prominently prohibits submission. Confirmed the download inventory is fail-closed and contains no approved candidate.

The existing four ranked geological ideas in [`2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md) remain proposals only. They were not reconsidered as an assigned method paragraph and were not tested.

### Pass 2 — tests, edge cases, and safety

Commands and results:

- `.venv/bin/python -m pytest -q -rs`: **256 passed, 8 skipped, 98 subtests passed**; 98 Rasterio pending-deprecation warnings. All eight skips identify absent pinned mirror/shared-template inputs.
- `npm test`: **3 passed**.
- `npm run test:site`: **8 passed**.
- `npm run test:browser`: passed at 1440, 390 and 320 px; checks included the research-only label, exact download hash, nine-site navigation/table, no tested viewport overflow, and fail-safe freshness states.
- `bash -n scripts/*.sh`; `.venv/bin/python -m compileall -q scripts vendor`; generated-page `--check` for both page builders; `scripts/audit_public_downloads.py --check`; `git diff --check`: all passed.

The strict inventory result is `PASS_RESEARCH_ONLY` for nine artifacts, with no approved download. The optional skipped tests are an evidence gap, not a pass. The browser test verifies the locally served artifact and does not access DrivenData or prove competition upload acceptance.

### Pass 3 — original request and protocol reconciliation

- Nine focus sites are represented in the published summary; historical leaderboard values are not elevated to confirmed results.
- A defensible estimate for a new submission is unavailable. No leaderboard projection is recorded as a score.
- No unique candidate TIFF is generated. This is the required negative outcome under the current no-lane / retired-lane / registry-stop conditions; the user-facing status stays unambiguous.
- No feature AUC, HOLDOUT-DTI, 95% CI, candidate-raster correlation/overlap, or validator result is claimed because no new candidate exists.
- The review does not claim an updated external-source audit, current leaderboard, current sibling-site files, complete registry, organizer data access, submission quota, or portal acceptance.
- Core blocker for future progress is authorization/evidence, not an untested algorithm: obtain an assigned lane, authenticated organizer inputs and format template, complete current registry, and a permitted new experiment budget. Preserve the existing fail-closed selector and perform promotion separately only after all mandatory gates pass.

## Reproduction

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
npm ci
.venv/bin/python -m pytest -q -rs
npm test
npm run test:site
npm run test:browser
bash -n scripts/*.sh
.venv/bin/python -m compileall -q scripts vendor
.venv/bin/python scripts/build_hk3_pages.py --check
.venv/bin/python scripts/build_audit_site.py --check
.venv/bin/python scripts/audit_public_downloads.py --check
```

## Sources and evidence for manual review

- [Competition problem / metric / format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition data (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Competition submission page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/)
- [Public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN data description](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)

These are review links, not a claim that each page was freshly fetched in this review. The dated and line-specific source observations already saved in the repository are in `evidence/official-verification-2026-10-29.json` and `evidence/official-review-2026-10-29.json`.

## Run card

Machine-readable negative review card: [`../evidence/session-2026-10-30-review-run-card.json`](../evidence/session-2026-10-30-review-run-card.json).

# Repository review — current Arena session (2026-10-29)

**Branch:** `arena/cc7518ae-gemsdoekarage2`
**Scope:** repository, nine-site executive summary, research slate, safety policies, local tests and generated pages.
**Decision:** **NO APPROVED SUBMISSION. Do not submit or label any existing TIFF as safe.**

No experiment, new prediction raster, organizer upload, competition slot use, or leaderboard score estimate was made. This is intentional: the parallel-run protocol requires one explicitly assigned method paragraph, but none is supplied. The last HK3 lane is retired and had already exceeded its experiment/time budget; the negative uniqueness ruling cannot be waived. Creating another candidate here would violate the protocol rather than satisfy it.

## User-facing conclusion

- The nine-site scorecard and nine individual pages are present. They identify each supplied historical file, its reported result, the absence of a defensible estimate for a new file, the measured directional 3-pixel proximity witness, and an explicit **DO NOT SUBMIT** verdict.
- The highest value in the supplied nine-site list is GEMSDOE32's **0.2778 USER-REPORTED / UNVERIFIED**. It is not tied to an organizer submission-page receipt, so it is not an organizer-confirmed score. The pinned raster is reported by the forensic audit as the D2.8 dot set after removing 6,436 dots near known catalogue traces. This pruning offers a plausible metric-based explanation for the reported change, but hidden labels and an authenticated receipt are absent; neither causation nor a score improvement is established.
- The repo's current official-source snapshot reports a public leaderboard observation of **0.4544** for first place and 0.3195 at rank 47. These are dated public leaderboard observations, not scores for any local TIFF, not private-round outcomes, and not refreshed in this review. Do not use either as a candidate estimate.
- No local candidate has a validated leaderboard estimate. For each of the nine sites the new-file score estimate remains **Unavailable**. Historical values remain expressly unverified.
- Existing downloadable artifacts are for audit/research only. A local [range/grid/format validator](../docs/how-to-submit.html) cannot establish portal acceptance. The reason for the user's earlier range error remains unknown.

## Prior-art hypotheses already on file

The dated [next-lane slate](2026-10-28-next-lane-slate.md) contains four falsifiable, not-yet-tested proposals, in the requested rank/cost order. They are proposals, not approvals or evidence of improvement:

1. **Medium cost; first to consider if separately assigned:** fit a blockwise label-blind terrain nuisance model and detect signed residual gravity steps (GeoDAWN bands 13, 11, 12, 19); compare against shoreline/contour nulls. A sediment–bedrock contact can mimic a fault. B4 shares an ingredient family, so lane collision must be assessed.
2. **Medium/high:** test a conductivity Hessian saddle across an independently located gravity break (bands 17, 13, 18), with saline-groundwater/playa and inversion-seam controls. Exclude band 15 pending authoritative interpretation.
3. **Medium:** test an interaction of coarse strain-regime change and persistent magnetic edges (bands 7, 8, 2, 3), with shuffled-strain control; interpolation seams and intrusive contacts can mimic the signal.
4. **Low cost / low expected benefit:** test seismicity sidedness across a gravity residual edge (bands 10, 16, 11), with shuffled seismicity and induced/mining seismicity controls.

The slate records why each differs from implemented work in this repo, limitations, and source/access checks. Its candidate rankings are qualitative research priorities, **not predicted DTI or leaderboard scores**. There is no basis to declare these methods novel across all sibling projects. None was tested this session, and no external layers were claimed obtainable.

## Three-pass review

### Pass 1 — scope and current implementation

Read `README.md`, `AGENTS.md`, `SUBMISSION_STATUS.md`, the latest blocker review, the current run cards and selectors, the shared writer/validator instructions, the next-lane slate, and generated site routes. The project already includes:

- the consolidated project prompt and binding stop rules in README;
- a visible no-submit executive summary, links to all nine focus pages, the historical scorecard, explanatory notes on GEMSDOE32, source links, and a step-by-step competition submission guide;
- fail-closed research-only download labeling, run cards, artifact inventory, uniqueness audits, GeoTIFF format checks, source freshness code, and the shared DTI holdout/writer tools;
- a report of the exterior NoData defect: historical saved TIFFs use finite zeros outside the footprint, while the project has documented NaN-outside guidance and its corrected writer gate. No historical raster was rewritten.

The cached `data/` competition bundle is not present. The local virtual environment was created from the checked-in Python lockfile solely to run tests; no data bundle was downloaded. Owner mirrors referenced by evidence are not authenticated organizer data.

### Pass 2 — tests, edge cases, and defects

No new code defect was identified in this read-only review. The lockfile suite returned **226 passed, 8 skipped, 98 subtests passed**. The skips explicitly require optional pinned owner-mirror/shared inputs, absent in this checkout. There were 95 Rasterio pending-deprecation warnings. Node feed tests: **3 passed**; site tests: **7 passed**; browser smoke tests passed at 1440, 390, and 320 px, including the exact research-download hash, nine rows, fail-closed freshness states, and no tested viewport overflow. Python compilation, shell syntax, and generated-page consistency checks passed.

The download audit initially could not start because the base environment lacked NumPy; after creating `.venv` from `requirements.lock.txt`, it ran successfully (see reproduction commands). A first system-wide `pip install` was blocked by PEP 668; no global override was used.

Limits of those passes: tests establish local code behavior and pinned-artifact consistency only. They do not authenticate organizer files, prove geology, predict hidden DTI, verify portal acceptance, or establish account quota. The eight skipped integration tests leave those optional mirror-backed checks unverified in this run.

### Pass 3 — requested outcome and release decision

| Requirement | Evidence-based disposition |
| --- | --- |
| Review nine specified sites and name the best supplied historical value | Present in `docs/executive-summary.html` and `docs/sites/GEMSDOE*.html`; GEMSDOE32's 0.2778 is USER-REPORTED / UNVERIFIED. |
| Estimate new-file leaderboard score | Unavailable; no validated calibration from catalogue holdout to the hidden expert labels. No projection is presented as a score. |
| Produce unique, validated TIFF safe to submit | **Not done.** No assigned lane and no complete authenticated registry/template clearance. All previously generated TIFFs are already classified research-only/negative. |
| Produce 3–5 hypotheses before experiments | Four ranked proposals exist in the linked slate. None is assigned or tested. |
| Run holdout and leakage checks | No experiment was run. Therefore no new HOLDOUT-DTI, CI, withheld-positive count, feature canary or raster hash is claimed. |
| Protect competition slots | No slot was selected or used. A separate quota-aware selector would be needed only after every prior gate passes. |
| Refresh official current feed | Not done. The in-repo freshness feature contacts GitHub, not DrivenData; a saved official leaderboard snapshot must not be described as current. |

## Reproduction

```sh
.venv/bin/python -m pytest -q -rs
npm test
npm run test:site
npm run test:browser
.venv/bin/python -m compileall -q scripts vendor
bash -n scripts/download_competition_data.sh scripts/fetch_feature_mirror.sh
.venv/bin/python scripts/build_hk3_pages.py --check
.venv/bin/python scripts/build_audit_site.py --check
.venv/bin/python scripts/audit_public_downloads.py --check
```

## Next work, ordered by blocker

1. Obtain a coordinator-assigned single method paragraph and confirm its relationship to the existing proposals and later merged results. Do not restart HK3 or infer a lane from a hypothesis slate.
2. In an authorized environment, obtain the official competition rasters/template and record provenance and hashes. Reconcile the example/template content, footprint, NoData convention, and reported upload-range error using official artifacts; do not infer its cause.
3. Build a complete immutable registry snapshot and perform the literal all-registry **pre-placement** correlation/overlap gate. Missing or malformed references fail closed; no lattice exception or uncovered-pixel placement.
4. Only then, if still within the limit, preregister and test the assigned hypothesis using the shared cached stack/evaluator/writer; run every feature-alone leakage canary; hide buffered whole fault segments, use visible-only catalogue features and exact visible-fault masking, and report pooled DTI plus 95% CI against a frozen same-fold incumbent.
5. At most three experiments or two hours, whichever comes first. Preserve negative results. Promotion and weekly-slot selection remain separate; require local format, registry, provenance and separate quota gates before any slot is considered.
6. Refresh the organizer leaderboard only from an accessible official page and label it as a public observation; never call it an organizer-confirmed raster score absent a file-linked receipt. Build out a genuinely DrivenData-aware feed only with authorized access.

### Official review links

- [Competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem, metric and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [About / supporting context](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Competition data (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN data source](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)

This review did not directly re-fetch these external pages. For line-by-line quotes and dates from the prior evidence-backed source review, see [`evidence/official-verification-2026-10-29.json`](../evidence/official-verification-2026-10-29.json). This is not a claim that the source pages or leaderboard were refreshed in this session.

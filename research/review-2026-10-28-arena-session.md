# Repository review — Arena session, 2026-10-28

## Executive disposition

**Current release decision: no approved file — do not submit any TIFF from this repository.** This review did not generate a raster, run a geological experiment, select a competition slot, or upload anything. The branch already contains a K2 experiment and downloadable research artifact, but the K2 run card's conditional `promote` field is not a competition-slot approval. The stored `evidence/selector_result.json` is a negative assessment of earlier H1 evidence; it does not adjudicate K2. No separate K2 selector authorization is present.

The main correction in this review is release communication: the homepage, executive summary, how-to-submit guide, README and K2 research report had potentially conflicting language describing K2 as a candidate “pending selector ruling” or “conditional yes,” despite no K2 selector authorization and a literal all-registry uniqueness failure. They now say **research/audit only — NOT APPROVED — DO NOT SUBMIT**. The research artifact remains downloadable for reproducibility, clearly not as a competition-ready submission.

## Pass 1 — inventory and evidence review

Read `README.md`, `AGENTS.md`, the experiment hypotheses/preregistration, K2 and H1 run cards, the negative selector result, nine-site scorecards, current site pages, and Python/Node tests. The README contains the user's consolidated project prompt and official source links. The site includes individual summaries for all nine focus repos and a submission walkthrough.

### Nine-site top result and interpretation

The nine historical results are labelled **USER-REPORTED / UNVERIFIED** in the repository, not organizer-confirmed receipts. The supplied highest of those is the GEMSDOE32 `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` result, 0.2778. Local forensics in the existing K2 record describe a shared dotted-ridge parent with catalogue-adjacent dots pruned; this is a plausible emission/masking explanation for the reported ranking, not proof of private-test causality. The repository says the organizer's hidden labels cannot be predicted from catalogue holdout alone. Accordingly, **no leaderboard score estimate is available**; a projection is not a score.

### Existing research slate (not newly proposed or rerun here)

The prior preregistration `research/hypotheses-2026-10-28-preregistration.md` already records five hypotheses and their layer/signature, missing-fault rationale, mimic, novelty relative to prior repo methods and rough cost:

1. **B1 supervised multi-physics texture** — competition-stack magnetic/gravity/topographic/basement/conductivity layers; multi-scale edge and difference-of-Gaussian signatures. Intended to learn fault-like expressions beyond mapped traces. Main mimic: lithologic/intrusive contacts and mapping bias. Medium cost.
2. **B2 fault-tip/gap continuation** — use visible segment geometry and local strike to extend likelihood from mapped ends. Intended to capture traces truncated by cover. Main mimic: genuine segment termination or en-échelon geometry. Low–medium cost.
3. **B3 structure-tensor ridge coherence** — directional coherence of fused gradient magnitude. Intended to prefer fault-like linear features over isotropic noise. Main mimics: roads, canals, flight-line striping and bedding ridges. Low cost.
4. **B4 scarp-step asymmetry** — paired flank elevation differences persistent along strike, using the 100 m elevation layer unless official 1 m DEM access is confirmed. Intended to find covered/eroded fault scarps. Main mimics: terrace risers, shorelines and road cuts. Medium cost.
5. **B5 seismicity alignment** — seismicity/depth aggregates from the provided stack aligned with candidate structures. Intended to identify active unmapped structures. Main mimics: blasts and induced seismicity; spatial resolution is a concern. Low cost, expected weaker.

That list is carried forward from prior work, not asserted as a new slate. The available checkout records three K2 experiments already run. The task protocol caps work at three experiments and requires an assigned method lane; no coordinator-assigned single method paragraph is present in this prompt. `AGENTS.md` says not to invent a lane or continue testing after the prior experiment budget. Therefore I did **not** test a fourth idea or claim the hypotheses above beat a holdout baseline. The top prior candidate cannot be safely revalidated in this review under those constraints.

### Existing K2 artifact — scope and provenance

The tracked file `docs/downloads/gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif` exists; SHA-256 re-read in this session:

`504be4587e3bec7b81f802b4c16b6c546c683e8a4c8b514d3a9856c6e0698dfb`

The committed K2 record labels its score as **HOLDOUT-DTI**, evaluator `gems57-pooled-hide-v2`, 58,258 withheld positives, 95% CI 0.1424–0.1742, and records all 26 canaries at or below 0.6211 AUC. Those are historical, mirror-based research measurements and were not rerun here. Its reported final-dot comparison passes only against the checked submission-raster subset (430 focus-site submission rasters, maximum 68.1% within-3-px overlap and maximum absolute Spearman 0.119). The same record reports failure under the literal complete-registry scope against calibration entries (spacing-5 lattice and ctx-ridge mask). Consequently it is **not cleared as unique under the stated literal rule**. Format read-back and a hash do not repair this novelty failure, authenticate organizer inputs, establish portal acceptance, or authorize a weekly slot.

The K2 record's historical conditional promotion is preserved rather than overwritten. The current selector receipt governs release: negative / unauthorized. The existing candidate TIF is not a new artifact produced in this session and is not a recommendation to submit.

## Pass 2 — safety and documentation corrections

- Reworded `docs/index.html` to label K2 explicitly as a research artifact, state that no K2 selector has approved it, distinguish the older H1 selector assessment, and make the download label say DO NOT SUBMIT.
- Reworded `docs/executive-summary.html` and its K2 table to distinguish scoped comparison from literal-registry failure and show an explicit “NO — DO NOT SUBMIT” verdict.
- Reworded `docs/how-to-submit.html` so it no longer tells the reader to wait for / assume an unresolved selector ruling; it now says the current decision is negative and forbids uploading this artifact.
- Added a superseding-status notice and corrected the current decision in `research/review-2026-10-28-k2.md`, while leaving the original run card and numerical experiment evidence intact.
- Updated the README to clarify that K2's old run-card `promote` is historical, not current slot authorization.
- Added regression tests tying the research-only wording to the current negative selector receipt, while explicitly asserting that the old K2 run card is historical evidence only.

## Pass 3 — validation and original-request check

The corrected site states, at the beginning and on the submission guide, that no file is approved. K2's artifact is easy to download for research/audit and clearly says not to submit. The nine historical scorecards remain labelled unverified; the estimate is unavailable rather than invented. No new TIFF is claimed, no weekly slot is selected, and no experiment was run outside the protocol.

Checks run after the changes:

- `.venv/bin/pytest -q` — **126 passed, 7 skipped**, 33 subtests passed. Skips are optional tests requiring large restored inputs. 38 Rasterio `PendingDeprecationWarning`s are non-failing.
- `npm test` — **3 passed**.
- `npm run test:site` — **8 passed**, including the new K2 release-status regression test.
- `npm run test:browser` — passed desktop (1440 px) and mobile (390/320 px) checks, release lock, site navigation and fail-safe freshness states.
- Re-read the candidate TIFF and ZIP SHA-256 values; the TIFF hash matches the committed K2 run card. This verifies bytes, not scientific quality or organizer acceptance.

No submission-format checker was rerun because the authenticated organizer template is absent from this checkout; committed receipts are historical evidence only. A separate quick exploratory all-HTML link scan initially counted archived pages' relative paths as broken; it was not used as a pass/fail result. The committed static-site link tests passed in the full Python suite.

## Limitations and next work

1. Obtain the method paragraph/lane assignment from the coordinator and resolve the exact registry scope without exempting difficult entries ad hoc.
2. Authenticate the official competition inputs/template through authorized DrivenData access; verify exterior/nodata semantics against organizer guidance. Public owner mirrors are not authenticated inputs.
3. Restore a complete, current registry snapshot and a frozen incumbent evaluated on exactly matching spatial folds before any new registered experiment.
4. Only after preregistered holdout, canary, surface novelty and final-dot novelty gates pass should a separate selector evaluate account quota. Save a file-bound ORGANIZER-CONFIRMED receipt only after an actual portal submission; do not call HOLDOUT-DTI a leaderboard score.
5. Refresh leaderboard status only where network/authentication permits and mark stale/unavailable otherwise. The prompt's numbers and archived snapshots are not live values.

## Source links for manual review

Links below are listed for review; this sandbox session did not independently refresh external non-GitHub sources. Source-access and authenticity limitations above remain in force.

- [Official DrivenData GEMS competition](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem description and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official About page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Official competition data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [DOE Geothermal Data Repository submission 1391](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)

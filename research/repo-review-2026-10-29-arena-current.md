# Repository review — Arena session on `arena/02fe9ab0-gemsdoekarage2` (2026-10-29)

## Decision

**NEGATIVE: no new submission TIFF was generated or approved; do not submit any repository raster.** No competition slot was used. This review is a repository/site safety repair, not a geology experiment. The consolidated prompt and prior evidence remain in `README.md`, `AGENTS.md`, `research/2026-10-29-verification-and-blocker-review.md`, and the linked run cards.

The highest value in the user's nine-site list remains the **GEMSDOE32 0.2778 USER-REPORTED / UNVERIFIED** claim. It is not a file-linked organizer receipt, and it cannot support a calibrated prediction for another file. The user's latest public leaderboard claim and the prior repository's 0.4544 observation are time-sensitive public snapshots, not organizer-confirmed scores for any local TIFF. This session did not retrieve the external leaderboard, competition, USGS, GDR, or NLR pages; citations and source observations already in the repository are provided for manual review, not represented as refreshed.

## Pass 1 — inspect implementation and fix an unsafe release inconsistency

Read `README.md` first, then `AGENTS.md`, `SUBMISSION_STATUS.md`, previous blocker/review records, selector and release evidence, the shared writer, the public-download audit, the Pages workflow, the four-hypothesis slate, and the current generated site.

Found an important inconsistency: `docs/executive-summary.html` still advertised a "File ready for download" and a "PROMOTE" GW-NFS TIFF, while the controlling current evidence said **no file is approved**. The page had dangling run-card/audit links, claimed local registry uniqueness from only two references, omitted the literal lattice stop, and was stale relative to the current fail-closed site generator. `docs/downloads/gemsdoe-karage2-gw-nfs-h1-20261029-zeros.tif` had no corresponding run card, validator receipt, or pre-placement registry evidence; the public-download audit correctly failed closed on it as unexpected.

Repairs:

1. Quarantined the existing 762,402-byte TIFF outside `docs/`, without modifying its bytes. Its exact SHA-256 is `294ad3693c3f2f6bd84e71e2f6bf412c8b4fa7b291662bd33befba1734628e85`. The quarantine receipt explicitly says unknown provenance, no score, not eligible, and not a website download.
2. Regenerated the public desk from `scripts/build_hk3_pages.py`. The executive summary now agrees with the saved-byte negative decision: no submission-ready TIF, the only displayed raster is marked research-only, no new submission name/note, no leaderboard estimate, and no slot authorization.
3. Repaired root `index.html` to route to the current desk at `docs/index.html`, rather than the stale executive-summary route.
4. Rebuilt the published-download inventory. It now reports `PASS_RESEARCH_ONLY` for the seven registered research artifacts and `downloadable_approved_submission: null`. This is an inventory-integrity pass, **not** an approval to submit.
5. Added `evidence/session-02fe9ab0-review-run-card-2026-10-29.json` for this review. It uses nulls where no candidate measurement exists and records zero experiments/slots.

The repository's earlier evidence identifies the current strict-stop example: the prior HK3 final raster had 45,046 of 45,108 dots within 3 px of a registered lattice (99.8626%, a **REGISTRY-OVERLAP AUDIT**, not a score), over the literal >70% stop; the registry scan had one missing/invalid entry. Do not generalize the lattice lower bound beyond its measured footprint and budget. These are inherited historical measurements, not freshly rerun this session.

## Candidate hypotheses and experiment authorization

The four ranked candidates already documented in `research/2026-10-28-next-lane-slate.md` satisfy the requested hypothesis-planning format at a qualitative level: each identifies layers/signature, a rationale for faults missed by the surface catalogue, a named non-fault mimic/control, novelty relative to this repository, data availability and cost. They are proposals only, not score estimates:

1. **Topography-conditioned residual gravity step** — bands 13, 11, 12, 19; signed, blockwise terrain-residualized gravity edge at 300–900 m; sediment–bedrock contact or lake-terrace riser mimic; medium cost. This is the slate's top-ranked *qualitative* test, not a claim of expected numeric DTI gain.
2. **Conductivity saddle across an independent gravity break** — bands 17, 13, 18; cross-profile conductivity-Hessian sign change; saline groundwater/playa margin and inversion seam mimics; medium/high cost.
3. **Coarse strain-regime change interacting with persistent magnetic edges** — bands 7, 8, 2, 3; shuffled-strain control; interpolation seam or intrusive contact mimic; medium cost.
4. **Seismicity sidedness across a gravity residual edge** — bands 10, 16, 11; shuffled-seismicity control; induced/mining seismicity and smoothed-density artifacts; low implementation cost, lower expected value.

The slate itself flags possible method-family overlap between candidate 1 and prior B4, and none is an assigned lane. There is no coordinator assignment receipt in the prompt, the prior HK3 lane is retired, and the current checkout has no restored feature cache or authenticated organizer inputs. The full all-registry stop cannot be cleared. Under the binding protocol, it would be improper to choose a candidate, run its holdout/leakage tests, emit a surface, or spend an upload slot now. Therefore **no HOLDOUT-DTI, CI, withheld-positive count, feature AUC, candidate raster hash, or leaderboard estimate is claimed for this review**. The top-ranked proposal must first be formally assigned and have the prerequisites restored; it has not beaten any comparable incumbent because it has not been run.

The four ideas do not require a new data source in principle because their listed bands exist in the prior hash-pinned owner-mirror stack. However, those owner mirrors are not organizer-authenticated, and the stack/cache is absent from this checkout. No outside dataset is proposed as obtainable or used. If later hypotheses require USGS survey line metadata or LiDAR, confirm the specific official files, footprint, license, and availability before marking the hypothesis viable.

## Pass 2 — tests and edge cases

Initial verification exposed the stale executive summary, failed generated-page consistency check, failed public-download inventory, and **14 Python failures** plus **5 Node site-test failures**. The root cause was unsafe, untracked-by-evidence TIFF content and stale generated output—not a need to loosen gates. After quarantine and regeneration:

- Python: **226 passed, 8 skipped, 98 subtests passed**. The skips require optional pinned owner-mirror/shared artifacts that are absent from this lightweight checkout; the warnings are Rasterio pending deprecations.
- Node feed tests: **3 passed**.
- Node site tests: **7 passed**.
- `scripts/build_hk3_pages.py --check`: passed.
- `scripts/audit_public_downloads.py --check`: passed; inventory remains research-only, with no approved TIFF.
- `scripts/assess_release.py`: negative, slot unauthorized.
- `scripts/audit_k2_release.py`: negative, slot unauthorized.

A test pass establishes local deterministic code/content checks only. It does not authenticate mirrored data, prove the scientific hypothesis, predict hidden expert-label DTI, ensure current global registry coverage, or establish DrivenData portal acceptance.

## Pass 3 — original request checklist

| Requirement | Result |
|---|---|
| Read and preserve the user's project prompt in README | Present; README says to reread it each session. |
| Review the nine named sites and explain the leading GEMSDOE32 claim | Existing executive scorecard and pinned per-site pages; 0.2778 remains USER-REPORTED / UNVERIFIED. Mechanism is a conditional pruning/false-positive hypothesis, not proven causation. |
| 3–5 hypotheses before implementation | Four ranked research proposals are documented; no implementation authorized. |
| Validate top hypothesis on blocked holdout before any slot | Not run because there is no assigned lane, cached stack/authenticated inputs, and unresolved literal all-registry stop. No slot was spent. |
| Produce a unique, submission-safe TIF | **Not achieved and not claimed.** The orphaned apparent candidate was removed from public downloads and quarantined. |
| Estimate leaderboard score | Unavailable; no trustworthy calibration from catalogue holdout to hidden expert labels. |
| Make submission eligibility obvious | Current generated desk says **OK TO SUBMIT: NO**, with research-only link and no approved download. Root route now leads to this desk. |
| Automatically validate without human inspection | Local fail-closed tests and release checks run; actual organizer format/template/portal acceptance remains unauthenticated. |
| Open and merge a PR | This review is prepared on the assigned Arena branch; PR/merge must be attempted after local commit/push, without changing branches. |

## Official sources for manual review

The previous source-verification receipt and its exact claim scope are in [`evidence/official-verification-2026-10-29.json`](../evidence/official-verification-2026-10-29.json). The current sandbox did not refresh external non-GitHub sites. Review:

- [DrivenData competition problem and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData data tab (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [GEMSDOE32 pinned mirror/site](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)

## Next-session blockers (ordered)

1. Obtain an explicit, immutable lane assignment and confirm it is distinct from prior B4/K2/HK3 work.
2. Restore/authenticate organizer template and competition inputs; reconcile footprint, NaN-outside policy, and the prior `[0,1]` portal error from an actual organizer artifact/receipt.
3. Restore the shared cached feature stack and shared evaluator/writer at pinned revisions; do not rebuild them privately.
4. Resolve the pre-placement literal duplicate witness using a complete immutable registry scan. Do not relax 0.90 / 70% thresholds, waive lattice references, or place predictions to target uncovered cells.
5. Freeze a same-fold, visible-only incumbent; then test the assigned proposal's feature-alone AUC canaries, buffered whole-segment holdout, pooled DTI and paired spatial 95% CI, within the three-experiment/two-hour limit.
6. Only a candidate passing all gates may enter a separate quota-aware selector. A real submission still needs account quota, an actual submission-page receipt, and required generative-AI disclosure/code assets for finalist rules.
7. Refresh the public leaderboard only from an accessible official page. The repository's GitHub revision feed is not a live DrivenData leaderboard feed.

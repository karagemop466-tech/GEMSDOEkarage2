# Submission status — NO APPROVED FILE

**Release 2026-10-31: one new unique TIF exists and is cleared as *safe*, not as *forecast to win*.**
`docs/downloads/gemsdoekarage2-geo-habitat-dti-20261031.tif` (40,561 dots, float32, EPSG:32611,
100 m, values [0,1], SHA-256 `ff22311c…d0402f`) was generated from the 19-band GeoDAWN stack alone;
no published raster is an input. Measured uniqueness: **23.3%** of its dots within 3 px of any one
pinned published raster (stop threshold 70%), max Jaccard **0.0057**. HOLDOUT-DTI **0.0172**
[0.0130, 0.0227] (vendored official metric, 60,661 withheld isolated positives, 11 of 16 folds
qualified). Forward projection against the 21 USER-REPORTED scores: **0.007–0.013 (PROJECTION, not
an organizer score)**. Verdict: **OK to download and submit as a unique independent entry; NOT
expected to beat the 0.2778 focus-site high.** No slot has been spent. Receipts:
`evidence/run-card-gemsdoekarage2-geo-habitat-dti-20261031.json`,
`evidence/habitat-holdout-2026-10-31.json`, `evidence/projection-range-2026-10-31.json`.
Every other TIFF in `docs/downloads/` remains **RESEARCH ONLY / DO NOT SUBMIT**.

**Review 2026-10-31: NO FILE IS OK TO DOWNLOAD AND SUBMIT.** Official board re-read: rank 1 0.4544; kpomazi 0.3195 at rank 50 today. Review: [`research/2026-10-31-leaderboard-recheck-and-three-pass-review.md`](research/2026-10-31-leaderboard-recheck-and-three-pass-review.md). No experiment, TIFF or slot used.

**Current review (2026-10-30): NO FILE IS OK TO DOWNLOAD AND SUBMIT.** The audited public-download inventory contains research-only files and `downloadable_approved_submission: null`. No new experiment, TIFF, score estimate, upload, or slot was created. The 2026-10-30 public leaderboard snapshot shows rank 1 at 0.4544 and the user-cited 0.3195 at rank 48; these are public-board observations, not receipts for local files. Full review: [`research/2026-10-30-live-source-and-code-review.md`](research/2026-10-30-live-source-and-code-review.md); source snapshot: [`evidence/official-review-2026-10-30.json`](evidence/official-review-2026-10-30.json); review card: [`evidence/live-source-review-card-2026-10-30.json`](evidence/live-source-review-card-2026-10-30.json).

**GW-NFS audit (2026-10-29, PR #76):** the PR #61 raster is NEGATIVE: holdout DTI 0.000013 is below both same-holdout random controls, and uniqueness fails. It stays quarantined under `evidence/quarantine/`. See [the review](research/2026-10-29-gw-nfs-audit-and-three-pass-review.md).

**Session B addendum (2026-10-29):** NO FILE IS OK TO DOWNLOAD AND SUBMIT. Full-registry check (440 rasters): gw-nfs and H-A are both DUPLICATE_STOP (overlap 1.0). gw-nfs stays quarantined; H-A remains an inventoried research-only download. The nine best focus files are not unique against each other (overlap 0.976–1.000). Estimated leaderboard score for any file: Unavailable (no organizer template or labels here). Receipts: [`evidence/uniqueness/`](evidence/uniqueness/).


**Historical status (2026-10-29, lattice gate):** no file was approved; all nine focus best files fail the literal lattice gate. See [the decision memo](research/2026-10-29-lattice-gate-and-decision.md). The saved TIFFs use finite zeros outside the footprint, but the official wording and the organizer sample use NaN there (the repo's strict format check fails for HK3). The leaderboard facts in that dated review were xiaofanhu 0.4544 at rank 1 and kpomazi 0.3195 at rank 47; see [the 2026-10-29 review](research/2026-10-29-verification-and-blocker-review.md). The current public snapshot is dated 2026-10-30 above.
**Gate detail, 2026-10-29:** all nine focus files stop at the shared uniqueness gate against the
13GEMSDOE lattice (99.91–99.92% dot overlap). No file is eligible under the written rule. The
protocol owner must decide the policy; see the executive summary and
[`research/2026-10-29-focus-audit-and-next-hypotheses.md`](research/2026-10-29-focus-audit-and-next-hypotheses.md).

**Post-integration reconciliation (2026-10-29):** `origin/main` adds HR4 and its saved-byte negative audit; the regenerated inventory contains **nine research-only TIFFs**, `PASS_RESEARCH_ONLY`, with `downloadable_approved_submission: null`. The published H-A TIFF has a measured **100% within-3-pixel overlap on 1,896 in-footprint positive cells** against the lattice witness; the HR4 TIFF has **99.9787% on 4,685 in-footprint positive cells**. These are registry-geometry measurements, **not scores**, and the lattice manifest is expressly incomplete. Both stop at `DUPLICATE_STOP`; neither has HOLDOUT-DTI evidence or organizer-confirmed results. Their mixed exterior convention is not validated. The stale GW-NFS raster is retained only under `evidence/quarantine/`, not in public downloads. See [`research/repo-review-2026-10-29-d704ab87.md`](research/repo-review-2026-10-29-d704ab87.md) and its integration addendum. Both synthetic candidate generators are retired; the HR4 placeholder previously allowed a partial local uniqueness check and format-only `promote` verdict without holdout or leakage tests, so it is now disabled. No best-submission recommendation or leaderboard-score estimate is supported.

**HK3 and every other published TIFF are research-only. DO NOT SUBMIT.**
This corrects the earlier upload recommendation. The literal registry failure
cannot be waived by density, research status or chance correction. Existing TIFF
bytes are unchanged; no new unique eligible submission was generated.

- [Current executive summary and research-only download](https://karagemop466-tech.github.io/GEMSDOEkarage2/docs/executive-summary.html)
- [Corrected run card](evidence/hk3/run_card.json)
- [Negative selector](evidence/hk3/selector_result.json)
- [Reproducible review run card](evidence/hk3-protocol-review-run-card-2026-10-28.json)
- [Three-pass review, source limits and ranked untested hypotheses](research/hk3-protocol-correction-2026-10-28.md)
- [Original status text — superseded history, NOT approval](knowledge/hk3-historical-submission-status-2026-10-28.md)

The saved HK3 TIFF is finite in [0,1] and matches the pinned **owner-mirror** grid.
No authenticated organizer template, portal acceptance or cause of the reported
range rejection is established. A local validator cannot guarantee acceptance.
No validated leaderboard estimate is available; archived projections are not scores.

No experiment, TIFF, or competition slot was used in the 2026-10-29 review. The stopped HK3 lane
must not be restarted. The public DrivenData leaderboard snapshot observed on 2026-10-29
showed 0.4544 at rank 1 and 0.3195 at rank 47; these public rows are not local scores
or submission receipts. All nine focus-site GitHub main heads changed since the pinned
historical audit, which is metadata freshness only—not a score or raster re-audit.
See [`evidence/official-review-2026-10-29.json`](evidence/official-review-2026-10-29.json),
[`research/2026-10-29-scorecard-and-monitor-review.md`](research/2026-10-29-scorecard-and-monitor-review.md), and the README
for the current decision and next steps. Any future upload requires passing all mandatory
gates and a separate quota-aware selector.

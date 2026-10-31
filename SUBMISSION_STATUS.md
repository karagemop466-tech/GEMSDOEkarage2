# Submission status — NO APPROVED FILE

**Current review (2026-10-31): OK TO SUBMIT: NO. No file is approved.** The H-C TIFF `docs/downloads/gemsdoekarage2-hc-strain-seis-corridor-30k-20261031.tif` is research-only and negative: HOLDOUT-DTI 0.013668 (60,988 withheld positives, no CI), canary pass, uniqueness FAIL (0.999929 vs lattice13). No slot is used. The GEMSDOE32 0.2778 mechanism is verified from bytes (`evidence/gems32-b2-verification.json`). The literal 70% uniqueness gate is unsatisfiable on this footprint because lattice13 covers 99.87% of it; this needs a protocol-owner decision. Full write-up: [`research/2026-10-31-gems32-explanation-hypotheses-and-decision.md`](research/2026-10-31-gems32-explanation-hypotheses-and-decision.md).

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

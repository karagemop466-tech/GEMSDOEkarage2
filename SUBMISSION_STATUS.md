# Submission status — NO APPROVED FILE

**Updated 2026-10-29 (lattice gate):** no file is approved; all nine focus best files fail the literal lattice gate. See [the decision memo](research/2026-10-29-lattice-gate-and-decision.md). Still no approved file. The saved TIFFs use finite zeros outside the footprint, but the official
wording and the organizer sample use NaN there (the repo's strict format check fails for HK3). Live leaderboard top is 0.4544;
kpomazi is at rank 47 with 0.3195. See [the 2026-10-29 review](research/2026-10-29-verification-and-blocker-review.md).
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

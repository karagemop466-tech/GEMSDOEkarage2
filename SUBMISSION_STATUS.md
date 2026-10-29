# Submission status — NO APPROVED FILE

**Updated 2026-10-29:** still no approved file. A stale executive summary incorrectly advertised an orphaned raster as ready; H-A had no holdout/registry measurements; and H-R4 claimed `promote` despite null HOLDOUT-DTI, only two registry comparisons, and contradictory saved-byte validator details. All three were quarantined outside `docs/` with bytes/metadata preserved; none appears in public downloads, and the generated summary says no submission-ready TIFF. The saved research TIFFs use finite zeros outside the footprint, but the official wording and owner-mirror sample use NaN there (the repo's strict check fails for HK3). See [the current Arena review](research/repo-review-2026-10-29-arena-current.md), [H-A quarantine receipt](evidence/quarantine/hA-intersection-propensity-aad3569983ab.quarantine.json), and [the prior source-verification review](research/2026-10-29-verification-and-blocker-review.md).

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

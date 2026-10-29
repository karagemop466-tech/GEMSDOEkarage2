# Submission status — NO APPROVED FILE

**Updated 2026-10-29:** still no approved file. The saved TIFFs use finite zeros outside the footprint, but the official
wording and the organizer sample use NaN there (the repo's strict format check fails for HK3). Live leaderboard top is 0.4544;
kpomazi is at rank 47 with 0.3195. See the [current branch-specific three-pass review](research/repo-review-3983c87b-2026-10-29.md), its [read-only run card](evidence/repo-review-3983c87b-2026-10-29-run-card.json), and the [dated source claim table](evidence/official-verification-2026-10-29.json).

**HK3 and every other published TIFF are research-only. DO NOT SUBMIT.**
This corrects the earlier upload recommendation. The literal registry failure
cannot be waived by density, research status or chance correction. Existing TIFF
bytes are unchanged; no new unique eligible submission was generated.

**Export-path warning:** a local footprint-aware check in `scripts/submission_writer.py`
does not change the active runner. The runners use the hash-pinned `vendor/gems57`
writer/grid, which still requires finite arrays and zero exterior cells, contrary to
the official null/NaN wording. The shared copy remains unchanged; do not use it to
create a candidate until its output policy is corrected in the shared template or
resolved with authenticated organizer evidence. The reported portal range error is
still unexplained.

- [Current executive summary and research-only download](https://karagemop466-tech.github.io/GEMSDOEkarage2/docs/executive-summary.html)
- [Corrected run card](evidence/hk3/run_card.json)
- [Negative selector](evidence/hk3/selector_result.json)
- [Reproducible review run card](evidence/hk3-protocol-review-run-card-2026-10-28.json)
- [Earlier protocol correction — historical, superseded for current status](research/hk3-protocol-correction-2026-10-28.md)
- [Original status text — superseded history, NOT approval](knowledge/hk3-historical-submission-status-2026-10-28.md)

The saved HK3 TIFF is finite in [0,1] and matches the pinned **owner-mirror** grid.
No authenticated organizer template, portal acceptance or cause of the reported
range rejection is established. A local validator cannot guarantee acceptance.
No validated leaderboard estimate is available; archived projections are not scores.

No experiment or competition slot was used in this review. The stopped HK3 lane
must not be restarted. Required next steps are in the review and README;
any future upload requires passing all mandatory gates and a separate quota-aware selector.

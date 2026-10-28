# Submission status — GEMSDOEkarage2

## Decision: no file is cleared for submission

**DO NOT UPLOAD the HK3 TIFF or spend a DrivenData submission slot.** The file
remains available as research/audit evidence only:

- File: `docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif`
- SHA-256: `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`
- Research name: `gemsdoekarage2-hk3-edgecentrality-apron3-20261028`
- Suggested note (110 chars): `HK3: 34-feature HGB with catalogue-free edge-centrality bands; dots sep 3px, >3px off catalogue; zeros outside`
- Selector decision: [`evidence/hk3/selector_result.json`](evidence/hk3/selector_result.json)
- Retraction record: [`evidence/hk3/approval-retracted-20261028.json`](evidence/hk3/approval-retracted-20261028.json)

The earlier run card's `PROMOTE` verdict included an unauthorized exception to
the literal all-registry uniqueness rule. The saved audit reports three overlaps
above the 70% stop threshold (71.0%, 73.3%, 74.9%). The exception is retracted;
the selector verdict is negative. The broader registry scan is also incomplete,
and organizer inputs/template and lane assignment have not been authenticated.
No experiment or submission slot is authorized by this status page.

## What local raster checks establish—and do not establish

The archived TIFF has local saved-byte checks for single-band float32 format,
finite values in [0,1], and a grid matching the pinned owner-mirror template.
These are research checks only. The mirror is not authenticated as the organizer
template; the checks do not establish portal acceptance or prove the cause of
the earlier “Predicted values must be in range [0, 1]” error. No accepted-upload
receipt is present.

## Score labels

- **HOLDOUT-DTI:** archived catalogue hide-and-recover evaluation, evaluator
  `gems57-pooled-hide-v2`, 58,258 withheld positives. At the matched 1.10% budget,
  HK3 recorded 0.1845 [0.1677, 0.2015] versus its re-fitted K2 comparator at
  0.1575 [0.1417, 0.1737], paired Δ +0.0270 [+0.0206, +0.0337]. This is not a
  leaderboard score and does not clear the failed uniqueness gate.
- **PROJECTION — NOT A SCORE:** the archived 0.263–0.286 range depends on
  user-reported anchors and unvalidated transfer assumptions. It is not an
  organizer-confirmed score or a validated prediction for this file.
- **USER-REPORTED / UNVERIFIED:** the focus-site GEMSDOE32 value 0.2778 and
  leaderboard figures supplied in the prompt have no file-bound organizer
  receipt in this repository.
- **ORGANIZER-CONFIRMED:** none.

For the nine-site history, hypotheses, sources and review limitations, see the
[README](README.md), [executive summary](docs/executive-summary.html), and
[three-pass repository review](research/repo-review-2026-10-28-arena.md).
The competition's [official submission page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/)
and [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
are manual-review links; this environment has no authenticated account receipt or
quota feed.

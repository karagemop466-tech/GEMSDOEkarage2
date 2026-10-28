# Submission status — GEMSDOEkarage2

> **CURRENT VERDICT: NEGATIVE — DO NOT SUBMIT.** This status supersedes the original
> positive wording in the October 28, 2026 status sheet. No TIFF in this repository is
> approved for competition upload. The existing HK3 raster is research-only.

## Current, hash-bound decision

- Candidate: `docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif`
- SHA-256: `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`
- Current decision: [`evidence/hk3/current_release_decision.json`](evidence/hk3/current_release_decision.json)
- Current run card and selector: negative; the prior unauthorized `PROMOTE` exception is
  documented in [`evidence/hk3/approval-retracted-20261028.json`](evidence/hk3/approval-retracted-20261028.json).
  Earlier full snapshots remain in Git history.
- No competition slot was used, no new TIFF or experiment was produced, and no organizer
  submission receipt or portal acceptance was verified.

## Release blockers

| Gate | Saved evidence | Result |
|---|---|---|
| Literal registry overlap | 99.8626% of dots within 3 px of the r13 lattice witness; three more references at 70.9763%, 73.3484%, 74.9401% | **FAIL — stop; no exception** |
| Registry completeness | 452 checked of 453; one missing/invalid | **INCOMPLETE — uniqueness not certified** |
| Pre-placement surface scan | No auditable scan in committed HK3 receipts | **UNVERIFIED — required gate** |
| Lane assignment | No uniquely identifiable assigned method paragraph; lane was self-declared | **FAIL / unresolved** |
| Experiment budget | Historical work was approximately 2 h 15 min vs 2-hour limit | **FAIL** |
| Organizer input/template | Local grid comparison is to an unauthenticated owner mirror | **UNVERIFIED** |
| Portal acceptance | No authenticated submission receipt | **UNVERIFIED** |

The historical final-dot overlap already exceeds the binding stop threshold, and a
post-placement result cannot retroactively establish pre-placement clearance. Do not
resume HK3, place dots, run a new experiment, select a submission slot, or upload this
file. The shared HK3 runner now blocks new experiments and evidence rewrites after the
protocol stop.

## Historical measurements — not a leaderboard result

- HOLDOUT-DTI: **0.1845046602**, 95% CI **[0.1676914118, 0.2014839638]**; evaluator
  `gems57-pooled-hide-v2`; 58,258 withheld positives. This is a historical catalogue
  hide-and-recover evaluation, not rerun in the review and not a leaderboard score.
- Rank-correlation maximum: 0.11434 (this test alone is below its threshold; it does not
  cancel the independent dot-overlap stop).
- The 0.2628–0.2855 transfer range is an exploratory projection based on user-reported
  anchors and unverified assumptions. It is **not a score or validated leaderboard
  estimate**.
- GEMSDOE32 B2 at 0.2778 is user-reported / unverified in this checkout. The proposed
  false-positive-pruning explanation is plausible but not causally demonstrated.

## Local format diagnostics (not organizer acceptance)

The saved local receipt reports a single-band float32 TIFF, EPSG:32611, shape 3730 × 3292,
finite values in [0,1], and a transform matching the pinned owner-mirror template. The
strict outside-NaN check failed because the raster stores zero outside the mirror
footprint. Organizer template provenance and the competition portal's exterior-value
convention remain unverified. These checks do not overcome the release blockers above.

## Review and verification

See [`research/repo-review-2026-10-28-current.md`](research/repo-review-2026-10-28-current.md)
for the three-pass repository review, focus-site comparison, candidate geological
hypotheses, source links, limitations, and next-session checklist. Generated pages and
the public-download audit must continue to display `OK TO SUBMIT: NO` and
`PASS_RESEARCH_ONLY` until a future independently assigned lane clears every gate.

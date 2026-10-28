# Three-pass review — 2026-10-28 / 635ee6a9

## Outcome: negative; no approved submission

The request's literal all-registry duplicate stop takes precedence over the prior
HK3 run's self-authorized exception. No new geological experiment, TIFF, or weekly
submission was made. The prompt refers to an assigned method paragraph but does
not identify one; HK3 describes itself as self-declared. Its three experiments
are exhausted and its own time note says approximately two hours fifteen minutes,
exceeding the requested two-hour budget. Do not restart it under a new filename.

## Pass 1 — review and implementation

Read the README, AGENTS, previous review, HK3/K3 evidence and next-lane slate.
The public dashboard, HK3 run card and selector claimed PROMOTE despite a failed
literal uniqueness gate. The download auditor explicitly excluded that gate and
accepted a chance-corrected exception. This was a substantive defect, not merely
an ambiguous inspection label.

- Retracted PROMOTE in the card and selector. Preserved prior decision text in
  `evidence/hk3/approval-retracted-20261028.json`; did not change any raster bytes
  or scientific measurements.
- Centralized necessary publication checks in `scripts/hk3_release_policy.py`.
  Missing, non-boolean or false required gates fail; a recorded stop or exception
  prevents approval. This is schema checking, **not evidence authentication**.
- Reused the existing shared writer/evaluator unchanged; no private fork.
- Updated generated homepage, executive summary and submission instructions:
  research download / DO NOT SUBMIT, no approved file, no guaranteed portal
  acceptance, historical projection explicitly unvalidated.
- Retired HK3 experiment/placement/card CLI commands; saved-raster audit remains.

## Pass 2 — regression and edge cases

Independently reopened all seven hosted TIFFs and their ZIPs using the existing
saved-byte inventory. Status: `PASS_RESEARCH_ONLY`, no approved download, no score
estimate. This checks saved hashes, range, band count, float32, and grid against
the pinned mirror; it does not authenticate the organizer footprint.

HK3 saved SHA-256:
`064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`.
Its values are finite and in [0,1]. That is not a guarantee of portal acceptance.
The failure is scientific/protocol uniqueness, not the local numeric-range test.

Added tests for every required gate absent, null, false, numeric, string, list or
object; explicit stop; negative verdict; unauthorized exception; and negative-page
language. Updated prior tests which incorrectly required the exception to pass.

## Pass 3 — original-request reconciliation

- The nine-site executive table and individual local site pages remain available.
  They are historical pinned comparisons, not edits to nine external repositories.
- Current GitHub HEAD check succeeded for all nine sites; all nine changed since
  the pinned snapshot. See `docs/evidence/source-head-review-635ee6a9.json`.
  **No fresh full-raster registry audit is claimed.** Changed metadata cannot
  authenticate a score or establish uniqueness against newly added rasters.
- Existing [four ranked hypotheses](2026-10-28-next-lane-slate.md) remain proposals,
  not new experiments or assigned lanes. Top proposal: block-fitted terrain-residual
  gravity edges with shoreline nulls; no new external layer is required. B4 shares
  ingredients, so novelty/collision must be checked before it becomes viable.
- HK3's recorded HOLDOUT-DTI at matched 1.10% budget is 0.1845046602,
  95% CI [0.1676914118, 0.2014839638], `gems57-pooled-hide-v2`, 58,258 withheld
  positives. It beats its K2 comparator, **not the current K3 best by an established
  paired test**. This number is not the score of the emitted-budget file.
- GEMSDOE32's user-reported result remains the highest of the supplied nine-site
  results, not ORGANIZER-CONFIRMED. Nested dot-mask geometry suggests deleting
  catalogue-adjacent false-positive mass as an explanation; hidden-label credit
  is unavailable and the causal explanation cannot be established from scores alone.
  Replaced a categorical hidden-fault-location assertion on the dashboard accordingly.
- Lattice coverage does not imply constant per-truth kernel credit: credit varies
  with lattice phase. The calibration uses an unverified phase-distribution assumption.
  It cannot establish the hidden truth count or a validated leaderboard estimate.
- New unique, high-scoring submission **not delivered**: making one after the stop,
  or calling the research TIFF approved, would contradict the mandatory protocol.
- README retains the consolidated requirements and core values, not a verbatim copy
  of the highly duplicated prompt. No claims of exhaustive line-by-line official
  verification, current quota, or guaranteed winning performance are made.

## Verified execution

- `.venv/bin/pytest -q`: 203 passed, 7 skipped, 98 subtests passed;
  input-dependent integrations skipped; Rasterio/Affine deprecation warnings.
- `npm test`: 3 passed; `npm run test:site`: 7 passed.
- `npm run test:browser`: passed at desktop, 390px and 320px; freshness states passed.
- `python scripts/build_hk3_pages.py --check` and
  `.venv/bin/python scripts/audit_public_downloads.py --check`: generated evidence
  and saved-byte inventory checks. No fresh model training.

## Sources, limits and next session

The organizer reference [README at pinned commit](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md)
was retrieved using GitHub API this session. It directs participants to download
data from the competition and provides CPU as well as GPU environments. A GPU is
therefore not a universal prerequisite. GitHub Pages API reports the existing site
as built; publication of this change follows merge, not local generation.

[Official metric/format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/),
[official data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/),
[USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
and [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
are manual-review links, **not newly verified remote pages**: their hosts and Dropbox
are outside this environment's network allowlist. Owner mirrors are not authenticated
organizer inputs. No DrivenData credentials or current account quota are available.

Next: refresh the full registry and bind source/receipt provenance; preserve the
literal stop unless the user explicitly revises the protocol; establish an assigned
new method and frozen matched-fold current-best comparator; run feature canaries and
pre-placement registry checks before at most three experiments/two hours. Only a
candidate passing all gates may reach the separate selector step. Do not use altered
filenames, jitter, or footprint holes to disguise a duplicate.

## Concurrent-main reconciliation

The first merge attempt failed because a concurrent correction merged as
`2b1ba4b` after PR checks passed. Merged main into this same Arena branch,
retaining `SUBMISSION_STATUS.md`, the concurrent review/run card, release-history
fields, and its removal of the unverified weekly quota claim. Conflict resolution
uses this branch's stricter complete-gate schema and explicit stop, with the
exception history archived rather than treated as an active waiver. No raster
bytes changed. Reran tests and generated-file audits after reconciliation.

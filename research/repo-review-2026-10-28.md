# Repository review — 2026-10-28

## Scope and disposition

This began as a documentation, release-path, and regression review of the checkout
at `690d7dd51ae458969e82fb62855babcf90a55437` on the active Arena branch. While
this work was underway, main advanced with additional release-safety changes; those
were merged into this branch and retained. No new geological experiment, parameter
tuning, point placement, submission-slot request, or upload was performed. The
standing lane assignment is absent; the completed H1 evidence is negative and its
pre-placement registry scan stopped. Those protocol stops remain binding.

**Release verdict: negative / do not submit.** There is no eligible unique,
high-scoring final-dot TIFF. A format-valid research raster is not a competition
submission. The H1 card records HOLDOUT-DTI 0.0336729751, evaluator
`gems57-pooled-hide-v2`, 58,259 withheld positive pixels, 95% CI
[0.0286737956, 0.0392948028]. Its paired difference against the best primitive
control is -0.0309244756 (95% CI [-0.0376108572, -0.0235755843]). This is
mirror-based research evidence, not an ORGANIZER-CONFIRMED score or a private
leaderboard estimate. The release selector remains negative and slot
unauthorized in `evidence/selector_result.json`.

## Findings

### Fixed in this review

1. **High severity — stale landing and submission copy was unsafe and
   contradictory in the starting commit.** The repository root redirected to
   `docs/index.html`, whose older copy called a historical H-KARAGE-1 raster a
   “submission raster.” The old `docs/how-to-submit.html` instructed visitors
   to download and submit it and represented limited historical comparisons as
   a uniqueness pass. Main was updated concurrently to replace those pages with
   an explicit negative release banner, a research-only H1 download, and a
   guarded submission guide; those changes are retained in the merged branch.
   This review adds tests for the canonical landing page and for redirects from
   duplicate legacy per-site and research paths. The current site clearly says
   DO NOT SUBMIT.

2. **Medium severity — browser smoke test no longer matched the canonical
   page.** The test had drifted to an older `experiment-index.html` layout while
   the published front door is `docs/index.html`. Its first run failed on stale
   selectors. It now checks the actual nine-row dashboard, research-only
   download and disabled submission state, plus current guide and old-path
   behavior, at desktop and mobile widths.

3. **Medium severity — README release state overstated and confused evidence.**
   It named a different, inactive branch; called the Oct 27 public leaderboard
   observation live; said no holdout DTI could be computed despite the committed
   mirror-based H1 receipt; and suggested running a legacy generator as if it
   created a submission. README now distinguishes the dated public snapshot,
   mirror-based HOLDOUT-DTI, and organizer evidence; marks the old generator as
   a research prototype; and gives safe test commands. The historic public
   snapshot value 0.4544 is explicitly dated 2026-10-27 and has not been
   refreshed in this review.

### Open blockers — do not bypass

- The prompt supplies no single assigned geological method paragraph. Do not
  infer or invent the lane.
- The literal uniqueness policy stops the H1 surface at a lattice witness after
  59 of 440 registered files; it does not clear novelty. Final-dot checking was
  not run because no dots were placed. The current registry is incomplete.
- No frozen incumbent reconstructed under the same evaluator/folds is present.
  The H1 best primitive is not an historical champion baseline.
- Inputs are owner mirrors, not organizer-authenticated competition downloads.
  DrivenData's data tab and quota/receipt require authenticated access. Preserve
  this provenance distinction.
- The H1 score and user-supplied historical scores do not estimate the hidden
  test leaderboard. No file-bound organizer receipt is present.
- The continuous H1 surface is labeled research-only and failed both holdout
  improvement and registry novelty. The old 15,000-dot H-KARAGE-1 artifact is a
  synthetic placement prototype, not a geological detector. Neither is cleared
  for upload; do not use either as the requested competition TIF.
- Source-freshness data checked GitHub refs only. The saved public-board snapshot
  is stale, and there is no authenticated quota/score feed.

## Verification performed

- Locked Python environment: `pytest -q` — 119 passed, 6 skipped, 33 subtests
  passed. 38 Rasterio `PendingDeprecationWarning`s remain (not test failures).
- `npm test` — 3 passed; `npm run test:site` — 5 passed.
- `npm run test:browser` — passed at widths 1440, 390 and 320 px; passed nine-site
  audit navigation, legacy-path safety, release lock, and freshness fail-safe states.
- `scripts/assess_release.py` — negative, slot unauthorized. Reasons include no
  assigned lane, no paired incumbent improvement, incomplete registry,
  duplicate surface witness, no final-dot measurements, and incomplete raster
  validation evidence.
- Initial browser run caught the stale route; after the route/test correction,
  browser checks passed. Initial Python test attempts without dependencies could
  not import NumPy/pytest; the locked requirements were installed in an ignored
  local virtual environment before the successful test run.

## Next work, in priority order

1. Reconcile the lane paragraph and literal lattice/registry rule with the
   parallel-run coordinator; do not test another idea before that is resolved.
2. Land/fix integrity checks at the shared template source (not only in this
   repository), authenticate the official input/template identity, and restore a
   complete prepared stack and complete registry snapshot.
3. Reconstruct a frozen same-evaluator incumbent; preregister one method and run
   per-feature canaries, surface novelty, buffered whole-segment holdout, and
   paired spatial uncertainty. Stop immediately on a failed gate.
4. Only after novelty and holdout gates pass should a separate selector verify
   portal rules/quota and consider a slot. Record the final TIFF hash and the
   organizer's file-bound submission receipt.

## Source links for manual verification

- [Official GEMS competition](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem description and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Competition data tab (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE/USGS INGENIOUS data submission](https://gdr.openei.org/submissions/1391)
- [H33 validation claim record](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/evidence/h33_validation.json)

The archived historical site values in this repository remain labeled
USER-REPORTED / UNVERIFIED; no new external score or geology claim is asserted in
this review.

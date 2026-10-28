# Independent release review — 2026-10-28

## Decision

**Negative under the user's literal policy; DO NOT SUBMIT.** No new experiment,
parameter tuning, dot placement, competition upload or slot usage occurred.
The three-experiment K2 budget is already exhausted. No assigned single-method
paragraph was supplied. This review does not invent one or exempt calibration
rasters from the registry.

## Pass 1 — implementation and saved-byte verification

Read README, AGENTS, prior reviews, K2 preregistration, run card, tests, selector
adapter and publishing workflows. The five hypotheses already ranked in
[the preregistration](hypotheses-2026-10-28-preregistration.md) and the three
completed experiments are preserved rather than relabeled as new research.

Found a release-path mismatch: `assess_release.py` assesses H1 only, while the
front door also exposes a K2 conditional promotion card. Added a separate,
read-only `audit_k2_release.py`; no shared evaluator/writer was changed.
The historical K2 card remains unchanged as provenance. Current clearance is
explicitly negative and published independently.

Saved K2 bytes match SHA-256
`504be4587e3bec7b81f802b4c16b6c546c683e8a4c8b514d3a9856c6e0698dfb`.
Single band float32; whole array finite in [0,1]; shape/CRS/transform match the
recorded mirror grid; ZIP contains exactly one byte-identical TIFF. These are
local validation measurements, not official template authentication. Footprint
containment and scientific evaluation were not rerun in this review.

The inherited registry audit includes duplicate witnesses: lattice overlap 1.0
(two copies) and calibration-ridge overlap 0.7205226551. A format-test raster is
grid-incomparable. The new audit includes all of them without exemptions and
fails closed on missing, invalid or incomparable measurements. Registry overlap
is a geometry measurement, not a DTI score.

## Pass 2 — regression and edge cases

Added tests for threshold equality, threshold exceedance, missing/empty registry,
NaN, boolean and out-of-range measurements, calibration inclusion, deterministic
receipt generation and visible negative guidance on all three primary pages.
Initial test run caught the submission guide's different `<main>` markup;
corrected banner insertion, then reran successfully. Removed a categorical
portal-acceptance claim from the landing page: local finite values cannot prove
an organizer's parser behavior or exterior convention.

The CI evidence and Pages checks now regenerate the K2 audit before checking
for stale committed evidence. H1's separate negative selector is unchanged.

## Pass 3 — requirements reconciliation

- Nine-site historical executive tables and per-site pages remain available.
  They identify the supplied historical best files, not recommended new slots.
- The existing K2 research download remains one click, with current negative
  clearance made explicit before its historical conditional experiment section.
- Prior HOLDOUT-DTI is 0.1581207190, evaluator `gems57-pooled-hide-v2`, 58,258
  withheld positive pixels, 95% CI [0.1423739219, 0.1741535541]. It is not rerun,
  organizer-confirmed, a calibrated leaderboard estimate, or proof of beating
  the historical champion. The paired primitive win is not a same-fold champion
  comparison. Leaderboard estimate stays unavailable.
- Full project prompt is already consolidated in README; added the current
  negative release disposition and reproduction command as its starting point.
- No fresh TIFF was fabricated to satisfy a filename requirement after a stop.
  The existing candidate is not eligible under literal uniqueness. This user
  goal remains unmet, rather than reported as successful.

## Verification

Python: **137 passed, 7 skipped, 33 subtests passed**; 38 Rasterio pending
Deprecation warnings. Skips reflect unavailable restored shared/data inputs,
not passes. Node feed tests: 3 passed. Site tests: 7 passed. Browser smoke checks
passed at desktop and 390/320 px mobile widths, including release lock,
nine-site navigation and fail-safe source freshness. Site builders ran without
unexpected generated changes. No full model retraining was performed.

## Sources and access boundaries

The GitHub API confirmed the official reference repository exists on `main`
with `pushed_at=2026-06-16T13:55:36Z` during this review:
https://github.com/drivendataorg/gems-prize-reference-solution . This metadata
check does not authenticate hidden scoring logic. Scientific explanations and
exact historical raster relationships are in
[champion_explanation.md](../knowledge/champion_explanation.md) and the linked
hash-pinned local receipts.

Official links for manual review (not freshly fetched; hosts outside the
sandbox allowlist):
- https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- https://gdr.openei.org/submissions/1391

## Next session priorities

1. Resolve assigned lane and registry scope at coordinator level. Do not bypass
   the lattice or silently weaken the overlap rule.
2. Authenticate organizer inputs, footprint/exterior convention and account
   quota. Never request passwords/tokens in chat.
3. Reconstruct a frozen historical incumbent on the same visible-only buffered
   folds; preregister a new experiment budget only after the stop is resolved.
4. Separate selector can consider promotion only after all gates pass. Retain
   the organizer's file-bound receipt before claiming any confirmed score.

Current machine-readable run card:
[`evidence/k2/literal_release_audit.json`](../evidence/k2/literal_release_audit.json).

## Concurrent-main reconciliation before merge

The first PR merge attempt found conflicts because main advanced to `bd8b477`
with a parallel K2 protocol correction. Merged main into this same Arena branch,
retained its stronger negative K2 pages, corrected historical cards, selector
review and generator stop, and kept this independent byte/literal-policy audit
and banner. Both audit commands now run in Pages CI. The earlier statements
about immutable conditional cards describe this review's initial implementation;
the parallel main correction explicitly supersedes those cards. No conflicting
conditional approval copy was restored.

Rechecked the combined tree: **142 passed, 7 skipped, 34 subtests passed**;
feed 3 passed; site 7 passed; browser desktop/mobile checks passed; deterministic
site builders and whitespace checks passed. This is the final combined-tree
verification, superseding the pre-merge counts above.

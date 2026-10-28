# Selector evidence review — 2026-10-28

**Decision: negative; no TIFF is approved for submission.** This is a software
and evidence review, not a new geological experiment. It neither spends a
competition slot nor overrides the earlier pre-placement stop. The prompt does
not identify the referenced single method paragraph. The earlier K2 session's
three experiments and stop are preserved in the [protocol review](k2-protocol-review-2026-10-28.md).

## Pass 1 — implementation and evidence

Read the standing README, required prior reviews and cards, existing nine-site
summary and selector. The [prior ranked hypotheses](hypotheses-2026-10-28-preregistration.md)
were recorded before that session's implementation. They are not evidence of
fleet-wide novelty or an assigned lane. No new candidate or leaderboard estimate
was generated here. The [run card](../evidence/selector-evidence-review-2026-10-28-eee3.json)
records the negative outcome.

The selector's old schema could accept (a) a purported win without identifying
an incumbent or the same holdout split, (b) a canary dictionary omitting a model
feature, and (c) metric configuration without an explicit pooled flag. The
schema now requires a named incumbent, matching evaluator, positive count and
split SHA-256, a unique explicit model feature inventory exactly matching the
canary keys, an explicit pooled flag, and a lane-assignment receipt reference
and hash. The H1 adapter leaves unavailable fields unknown instead of inferring
them. These are **consistency checks only**:
a hash or caller assertion does not authenticate the source, prove the exact
fold inputs or verify the feature inventory, and this gate cannot independently
inspect TIFFs, rerun holdouts or authorize a weekly slot. Authentic evidence
and independent verification remain required.

## Pass 2 — correctness and site review

Added tests for wrong splits, evaluator and incumbent metadata; missing, extra,
duplicate and malformed features; and missing or non-boolean pooling. Fixed the
executive-summary table heading to identify K2 as a research file, not a file
ready for submission; an existing site test caught this stale wording. No
shared evaluator or writer was altered.

Saved-byte K2 review reran against the committed artifact. It confirms the prior
file hash and local single-band float32 finite [0,1] readback and compares its
grid to the recorded **owner mirror**, not an authenticated organizer sample.
The historical exterior-NaN diagnostic failed. The original upload and portal
receipt are unavailable, so the reported range-error cause remains unknown.

## Pass 3 — scope and verification

- Restored the pinned public research references in ignored cache and reproduced
  the nine-raster reference audit against the committed snapshot. Hashes prove
  agreement with the pinned mirrors, not official data provenance or a complete
  registry.
- After integrating concurrent main-branch safety changes: Python suite 165
  passed, including mirror-dependent checks; 78 subtests passed. Node feed:
  3 passed; site: 9 passed; browser smoke: desktop and mobile viewport checks
  passed. Rasterio emitted pending-deprecation warnings.
- K2's prior **HOLDOUT-DTI 0.1581207190**, 95% CI [0.1423739219,
  0.1741535541], `gems57-pooled-hide-v2`, 58,258 withheld positives, is a
  historical mirror-based proxy and was not independently rerun here. It is
  not a calibrated leaderboard score. The archived surface and final registry
  results exceeded the literal overlap threshold; the saved raster is not
  eligible.
- GEMSDOE32's **0.2778** is USER-REPORTED, not organizer-confirmed. Its decoded
  mask's relationship to the earlier parent is documented in
  [champion forensics](../knowledge/champion_explanation.md): pruning redundant
  nearby predictions may improve distance-tolerant precision, but hidden labels
  and the actual receipt are unavailable. Causality and an ability to exceed the
  historical value remain unknown.
- The official reference repository was read via GitHub this session; its
  [README](https://github.com/drivendataorg/gems-prize-reference-solution)
  describes both CPU and GPU options. It does not authenticate the hidden scorer,
  data mirrors, leaderboard, or portal behavior. This runtime cannot directly
  access DrivenData, Dropbox, USGS or the portal under its outbound allowlist.
  Review [competition description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
  [data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/),
  [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/),
  and [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
  when those services are accessible; no claim is made that they were fetched.

## Next session

Resolve the method lane and the literal registry/lattice conflict without a
private exemption, obtain organizer-authenticated data and exterior guidance,
restore a complete current cross-session registry, and freeze a same-split
incumbent. Then run the unchanged shared tools with canaries and surface stop
before placement. Independently authenticate evidence files and check current
quota before any separate selector considers a slot. Automated checks cannot
create missing credentials, policy decisions, hidden labels, or organizer receipts.

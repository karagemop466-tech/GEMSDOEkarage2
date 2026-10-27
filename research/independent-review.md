# Nine-site review and H33 forensic finding

This repository initially contained only a README. There was no previous local
training system, cached stack, evaluator, writer or historical result to resume.
The [machine-readable audit](../docs/data/reference-audit.json) pins nine historic
raster bytes, sample/label mirrors, the registered lattice and the exact shared
novelty/validator code. Reproduce with the commands in the README. It is a
partial registry audit, not a complete inventory of concurrent sessions.

## What the H33 file actually is

On the pinned mirrors, the GEMSDOE25 and GEMSDOE30 reference masks are exactly
equal inside the footprint. The GEMSDOE32 H33 mask is exactly the GEMSDOE25 mask
after removing dots at distance ≤2 pixels from a known-fault label. This removes
6,436 of 44,090 dots. The label pixels and reference masks were read from the
pinned TIFFs; the relation was checked directly, not inferred from filenames.
All 72 directional comparisons between the nine historical files exceed the
requested 70% within-3-pixel threshold. Historical files are **not** unique
submission candidates under this protocol.

The H33 value **0.2778 is an unverified owner claim**, not an
organizer-confirmed receipt. The original manifest says `receipt: null`, and the
contemporaneous original commit explicitly says the candidate was *unscored*.
It might have been submitted later; without the later organizer receipt and
file identity, the claim cannot be confirmed or disproved. A prior projection
is not a score. We cannot prove why the file would have achieved the claimed
value or that any new method will exceed it.

## Scientific explanation, carefully qualified

A sparse pattern can sometimes reduce redundant prediction mass while preserving
coverage of nearby truth under the organizer's triangular kernel, and the low
false-positive weight changes the recall/precision tradeoff. These are plausible
mechanisms, **not a causal finding** about H33 or hidden expert faults. The
near-catalogue removal also discards places where staff say new-fault truth may
exist; it could help or hurt. Only a controlled, leakage-free validation followed
by an organizer result can resolve that.

The official metric has **two different** nearest-neighbour sums: TP is summed
on truth pixels; FP is weighted on prediction pixels. Therefore, the identity
`DTI = TP / (0.2 * number_of_dots + 0.8 * number_of_truth_pixels)` is not
valid in general: one prediction can give partial credit to multiple truth
pixels. Do not use that simplification to forecast a score. See the
[organizer's equations](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric).

## Irregularities and constraints

- The user-provided H33 value and original unscored status conflict in time; no
  artifact-linked organizer receipt was available. Other nine-site values are
  likewise user claims and are not promoted to verified scores.
- The official text calls for null/NaN outside bounds, while the rejected file
  and server-side range check were unavailable. Owner sites give conflicting
  explanations. Our shared validator reports both official-text and strict
  whole-array diagnostics separately; no local check proves portal acceptance.
- A registered regular lattice covers 99.8713% of the mirrored footprint within
  3 pixels. Under the literal all-registry rule it forces a duplicate stop at
  the H33-sized budget. Excluding it or selecting its boundary holes would be a
  policy change or gaming, not proof of a new method. The bound does not apply
  universally to small candidates.
- The prompt specifies a single assigned method lane but does not supply its
  paragraph. It also asks for a new file regardless of gates while requiring an
  immediate stop on duplicate; this independent audit honored the stop and did
  not write a candidate. See the separate parallel experiment below.
- The shared GEMSDOE24 writer's docstring calls its zero-exterior default “portal-safe”
  and discourages the NaN variant despite the published bounds language. This
  is an unsupported assertion: neither encoding has an artifact-linked portal
  receipt here. Report this upstream; do not silently fork or treat the writer's
  default as an authorization. The GEMSDOE57 `grid.py` writer also calls
  zero-exterior the only submission-compatible mode without portal evidence.
  The local audit reports both diagnostics; neither claim is independently
  established and upstream fixes should be proposed rather than privately forked.
- The canonical shared `evaluate_holdout.py` is a frozen MTR1-specific runner;
  it is not a generic entry point for these new proposals. No shared tool was
  modified or privately forked. The cached prepared feature stack and a frozen
  same-protocol best were not available in this checkout.
- The pinned owner `example_submission.tif` has **60,988 positive pixels** and
  equals the mirrored labels inside the footprint. The organizer describes its
  sample as predicting total fault absence. This unresolved discrepancy means
  the sample's official identity and the exact validation footprint are not
  established; it may be a substituted or different-generation mirror, and no
  cause is inferred.
- We obtained a hash-matched raw 19-band owner mirror, labels and sample without
  DrivenData authentication. That removes a **research-byte** access problem,
  not the need to verify authorized data, licenses, exact units and full registry.
- Public/private expert truth, private score receipts, actual weekly capacity,
  and a justified holdout-to-leaderboard calibration are not available here.

## Next session

Supply or establish the actual lane and complete registry/policy scope; retain
the literal stop until it is changed explicitly. Rebuild the shared cached
features from authorized inputs and compare a genuinely distinct method with a
frozen matched control using the common evaluator and feature-only canaries.
Resolve exterior format with an organizer clarification or an existing receipt,
then only let the separate selector consider a slot. If the policy remains
unchanged, keep the negative result and do not advertise a download as ready.

## Concurrent experiment merged during this audit

A different session merged the H1 signed cross-field parity experiment into
`main`. Its [run card](../evidence/run_card.json) reports **HOLDOUT-DTI 0.03367**,
95% CI [0.02867, 0.03929], evaluator `gems57-pooled-hide-v2`, and 58,259
withheld positives; it reports a negative paired comparison against its best
primitive control and a literal lattice overlap stop. These are **source-recorded
results, not independently replayed in this follow-up** and not organizer
scores. No final dots or slot were selected there. The research-only surface
was preserved by that session and is prominently marked DO NOT SUBMIT.

We independently re-opened its exact TIFF through the pinned GEMSDOE24 format
checker. Its SHA-256 is `a80d59a671eccfc5d312f98901f6a3d426cd49662f847ff6d4f2375db52a7ede`;
the mirrored-grid/interior and strict all-array range diagnostics pass, while
the mirror-exterior NaN diagnostic fails. Neither establishes the official
sample identity or portal acceptance. The merged readiness adapter previously
set `outside_nodata` equal to a general local format-pass flag; it has been
corrected to unknown so it cannot silently mark the unresolved exterior
requirement as verified. This does not modify the shared writer or evaluator. The physical report calls band 15 a
basement-depth layer based on mirror metadata; the organizer instead lists a
conductive-base depth feature. The band mapping and equivalence are unverified.

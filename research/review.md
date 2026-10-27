# Review and next steps

## Checkout audit

The starting commit contained only a one-line README. It did not contain the
promised template, evaluator, prepared feature stack, generated TIFF, or previous
session pipeline. We restored a pinned public owner mirror of the four core
rasters and a pinned shared-tool manifest into the ignored `.cache/`; the
19-band raw feature file hashes to the upstream manifest's expected digest.
The cached, prepared shared feature array is not present. Files under `.cache/`
are disposable and are **not** committed. Run `scripts/bootstrap_shared.py`
again when needed; do not mistake owner mirrors for authenticated originals.
The partial shared-asset manifest is not a complete runnable template checkout:
its evaluation CLI imports additional lane-specific modules. No evaluator or
writer was copied into this repository or modified.

## Independent audit, not an experiment

`python scripts/audit_focus.py --fetch` restores the twelve pinned input files,
verifies SHA-256, Git blob hash and byte size, checks grids, and computes all 72
directional overlaps of the nine historical positive-dot masks. The same code
also audits the registered lattice. Pinned refs and checksums are in
`registry/pinned_assets.json`; machine-readable measurements are in
`docs/data/focus_audit.json`. This checks only those nine historical rasters and
one witness, not all files on those sites or all parallel sessions. It does not
check a new pre-placement surface because none exists.

On the pinned mirror footprint, 6,649 cells are outside the lattice's 3-pixel
neighborhood. For N distinct in-footprint dots, at least `max(0, N - 6649)`
are within that neighborhood. At the *reference* budget of 37,654 dots, the
minimum possible overlap is 82.34%, already greater than 70%. This is a
necessary-condition proof for this particular grid, comparator and budget;
it is not proof that all smaller candidates fail. Choosing holes to defeat the
comparator would be gaming the gate, not a scientific test.

## Why the owner-reported best might have improved

Our direct pixel audit verifies that GEMSDOE32's B2 mask equals GEMSDOE31's
solo mask after deleting 2,545 dots within 2 pixels of the owner-mirrored
catalogue; no dots were added. GEMSDOE25 and GEMSDOE30 have identical
positive-dot masks, and GEMSDOE36 contains B2 plus 1,200 additional dots.
These are geometry measurements, not proof of leaderboard scores.

The official DTI credits each truth cell by the maximum distance-weighted
prediction in the 300 m neighborhood, while each positive prediction can
contribute false-positive mass. Nearby predictions can therefore be redundant,
and pruning could improve precision relative to recall. The true labels are
hidden: a deleted dot may also have contributed true-positive credit. Hence
this observation is a **plausible mechanism**, not a causal explanation of the
unverified, owner-reported 0.2778 or evidence that a similar adjustment will
beat it. A SHA difference alone does not establish uniqueness.

## Next steps, in order

1. Reconcile the missing method-lane assignment and the calibration-control
   policy across parallel sessions; preserve the literal rule until changed.
2. Restore the shared prepared feature stack and a complete, current registry;
   verify the authentic organizer template and data provenance. Do not use
   withheld labels to derive fold features.
3. Preregister one lane, run surface novelty and feature-only leakage canaries,
   then buffered whole-segment holdout against the same-protocol best. Stop on
   a failing gate and record the negative result.
4. Only after final-dot novelty and saved-byte format checks pass should an
   independent selector consider a weekly slot. The portal, quota, actual
   acceptance and file-bound score receipt require the enrolled account.

There is no private-truth score estimate, candidate GeoTIFF, submission name,
portal acceptance or competition upload from this checkout.

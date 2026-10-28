# K2 safety review — superseding verdict

**DO NOT SUBMIT.** This is an audit of saved evidence, not a new model experiment.

1. The original K2 run reported surface positive-support overlap **1.0** against
   the registry lattice before placement (`evidence/k2/final_generation.json`).
   This exceeds the literal 0.70 stop. It nevertheless proceeded to emit dots.
   The lane was self-assigned because the requested lane paragraph was missing.
   Neither fact is fixed by describing the lattice as a calibration input.
2. The final-dot audit reports `unique: false`, maximum overlap 1.0, and an
   incomplete inventory (`evidence/k2/final_registry_audit.json`). The 430
   focus-site download comparisons are a narrower, historical subset, not a
   clearance against all requested repositories or all registry rasters.
3. The prior strict validator failed `outside_is_nan`; the writer accepted zeros
   outside the mirrored footprint. Read-back found finite values in [0,1], but
   portal acceptance and the authentic organizer template remain unverified.
4. Prior HOLDOUT-DTI is 0.1581, evaluator `gems57-pooled-hide-v2`, 58,258
   withheld positives, 95% CI [0.1424, 0.1742]. It does not establish a private
   leaderboard score or an uncontaminated win over the current best submission.
5. The prior conditional promotion is retained as historical evidence only. The
   current machine-readable negative card is `docs/evidence/k2-independent-readback.json`.
   `scripts/k2.py final` is retired to prevent repeating the stopped run.

## Three passes

- **Pass 1 — evidence:** inspected run card, saved pre-placement, final registry
  and strict-validator receipts, source code and raster read-back. No data restored
  or geological experiments run.
- **Pass 2 — correction:** retired generation of the stopped K2 candidate and
  superseded contradictory submission wording; the old run evidence is retained.
- **Pass 3 — verification:** automated tests and independent SHA/range read-back;
  see session response for actual test outcomes and PR/merge status.

## Next steps

Reconcile the registry lattice policy explicitly without gaming it; supply an
assigned method lane, complete the inventory, authenticate organizer template and
exterior-value rules, and reconstruct a leakage-clean comparable incumbent on
identical folds. Only then preregister a genuinely new, bounded experiment.
Official sources: [competition](https://www.drivendata.org/competitions/306/competition-doe-gems/),
[reference solution](https://github.com/drivendataorg/gems-prize-reference-solution),
[data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/),
and [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
DrivenData and Dropbox are outside this environment's host allowlist; no current
leaderboard, quota, authenticated receipt or source data can be independently
verified here. A SHA-256 confirms byte identity, not organizer provenance.

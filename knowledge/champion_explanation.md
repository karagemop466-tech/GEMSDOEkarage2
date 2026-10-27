# Why the reported B2 result can improve without a new geological detector

## Established from raster bytes (not leaderboard evidence)

`evidence/champion_forensics.json` establishes these exact decoded-mask relationships:

- GEMSDOE25 D2.8 equals the GEMSDOE30 historical mask.
- GEMSDOE31 B1 equals D2.8 with dots at Euclidean distance <=1 pixel from the visible full catalogue removed.
- GEMSDOE32 B2 equals D2.8 with dots at distance <=2 pixels removed. On the mirrored 100 m grid this is 200 m.
- B2 removes 6,436 D2.8 dots, including 2,545 beyond the B1 pruning step.
- GEMSDOE36 contains every B2 dot plus 1,200 additional dots.

This is an emission/masking change in a related model family. It does not demonstrate that B2 independently found new faults. The user's historical reports place B2 highest among the nine supplied best-file entries. No organizer receipt was available, so the reported ranking and values are not ORGANIZER-CONFIRMED.

## Mechanistic explanation, with explicit assumptions

Under the protocol's distance-tolerant Tversky arithmetic, let `T` be max-kernel truth credit, `F` false-positive prediction mass, `N` the number of truth pixels and `D = T + alpha F + beta(N-T)`. With alpha=0.2 and beta=0.8, `D = alpha T + alpha F + beta N`.

Deleting predictions reduces truth credit by `dT >= 0` and false-positive mass by `dF >= 0`. If the new denominator is positive, the new DTI is higher exactly when:

```
(T - dT) / (D - alpha*dT - alpha*dF) > T / D
D*dT < alpha*T*(dT + dF)
```

Thus low marginal truth credit relative to removed false-positive mass makes pruning useful. A dot can have low marginal truth credit because another nearby dot already supplies the max-kernel coverage. This explains why thinning or catalogue-apron pruning *can* outperform a dense parent. It does not prove that the removed B2 dots were actually false positives on the competition's hidden faults. The necessary hidden `dT` and `dF` are unavailable; do not invert user-reported leaderboard numbers to invent them.

Nor does a GeoTIFF value of zero outside the footprint explain a rank gain by itself: format/nodata handling and the decoded prediction field are separate questions. The portal error reported in the prompt is not a diagnostic receipt identifying which invalid value occurred.

## Why the historical number is not a transferable estimate

1. Known mapped faults are selected by visibility, access, previous surveys and mapper judgement. A hide-and-recover sample of that catalogue is not an unbiased sample of truly missing faults. This missing-not-at-random concern is a methodological limitation, not an empirically quantified effect here.
2. Removing predictions using the full catalogue before holdout would also remove withheld positives, invalidating comparison. Recompute every catalogue-based feature and masking rule from visible-only traces on identical folds.
3. Selecting among many reported submissions can overfit public leaderboard feedback. Their ranking alone does not identify a transferable geological causal mechanism or provide uncertainty.
4. A 95% spatial cluster-bootstrap interval is conditional on the chosen folds, catalogue and model. It is not a calibrated interval for the hidden leaderboard result.
5. Fault likelihood is not vent likelihood. Heat source, reservoir permeability and hydrothermal circulation require independent evidence not established by a fault-mask score.

## Can a new submission beat the historical report?

Possibly, but this run provides **no evidence that its candidate does**. H1's HOLDOUT-DTI was lower than its primitive controls on the same evaluator, and the literal registry overlap test stopped the lane. No honest leaderboard projection follows from these results. The right outcome is a negative deliverable and zero slot expenditure, not a claimed high-scoring unique submission.

## Verification sources

- Byte hashes, exact files and immutable revisions: `evidence/nine_site_best_files_audit.json` and `registry/focus_registry_manifest.json`.
- Scoring arithmetic reused unchanged: `vendor/gems57/metric.py`, `evaluate_holdout.py`; random small-grid tests compare it against the shared literal brute-force oracle. This is protocol-formula validation, not official hidden-scorer authentication.
- Official fault-detection reference: https://github.com/drivendataorg/gems-prize-reference-solution (pinned notebook and verified scope in `evidence/sources.json`). Its training-loss weights are not a substitute for obtaining the official distance-tolerant evaluation specification.

# Safety follow-up — 2026-10-28

## Pass 1: evidence reconciliation

No experiments or competition submissions were made. The prompt specifies a lane
but does not supply its method paragraph. Prior K2 self-assigned a lane; its own
run card records a 1.0 surface overlap with a registry lattice before placement.
The literal protocol mandates stop at >0.70. It also records a final overlap of
0.7205 against another registry record. The historical conditional promotion is
therefore superseded: **negative, do not submit**. No comparator was exempted.
The prior card remains unmodified as historical evidence, not authorization.

The HOLDOUT-DTI previously reported for K2 is 0.1581, 95% CI [0.1424, 0.1742],
gems57-pooled-hide-v2, 58,258 withheld positive pixels; it was not rerun here.
It is not an estimate of the private leaderboard. The nine historical scores are
user-reported, not independently authenticated organizer receipts. A pruning
mechanism for GEMSDOE32 is plausible, not proven by a hidden-label score.

## Pass 2: software review

The readiness gate accepted AUC below 0.10 even though an inverted feature can
be equally predictive. It now rejects either tail (equivalently max(AUC, 1−AUC)
> 0.90); tests exercise the lower tail. This is a local selector schema check,
not a change to the shared evaluator or proof that the prior canaries were rerun.
Site language no longer guarantees the portal will accept an all-finite file.

## Pass 3: limits and next steps

The full current registry, organizer-authenticated data/template, assigned lane,
matched current holdout incumbent and account quota are not established here.
Outbound rules prevent directly checking DrivenData, Dropbox, USGS or the live
leaderboard in this session. The original submission error cannot be diagnosed
from its message alone; zeros outside the footprint pass the prior local range
check but conflict with a local NaN-outside convention. Do not claim portal
acceptance without an organizer receipt. The previously observed lattice does not
prove every possible sparse dot budget fails because footprint-edge exceptions
exist. Coordinate any registry-policy change before a new experiment. Restore and
verify data and registry against official inputs, then run canaries, pre-placement
novelty, buffered holdout, final novelty and saved-byte validation in the assigned
lane; a separate selector checks slot availability. No prompt-authorized exemption
or competition slot is inferred.

Sources for review: [official reference](https://github.com/drivendataorg/gems-prize-reference-solution),
[competition problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/),
[leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/),
[prior K2 card](../evidence/k2/run_card.json), [prior nine-file audit](../evidence/geometry-audit.json).
The non-GitHub links were not fetched in this session.

## Verification in this follow-up

K2 saved TIFF SHA-256 was recomputed and matches its historical card. Rasterio
readback: one float32 band, shape 3730 × 3292, EPSG:32611, whole array finite,
minimum 0 and maximum 1. This is not a comparison against an authenticated
organizer template and does not validate the exterior convention or novelty.

Python tests: 126 passed, 7 skipped, 34 subtests passed. Node feed: 3 passed;
site: 7 passed; browser smoke: desktop and two mobile widths plus freshness
passed. Existing skipped optional integrations were not claimed as validated.

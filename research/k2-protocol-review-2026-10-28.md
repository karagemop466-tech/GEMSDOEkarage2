# K2 protocol and release review — 2026-10-28

**Verdict: negative. Do not submit K2.** This review ran no new experiment,
placed no dots, and used no competition slot. The prompt refers to a single
method paragraph but does not identify one. A self-assigned lane cannot be
asserted as the coordinator's lane.

## Pass 1 — evidence audit

The earlier K2 session ran three experiments and produced a TIFF. Its
[`final_generation.json`](../evidence/k2/final_generation.json) reports
positive-support overlap 1.0 against a registry lattice **before placement**.
The literal protocol says stop when overlap exceeds 0.70; it does not exempt
calibration records. The prior session proceeded to write dots, so its
conditional promotion claim is inconsistent with the requested sequence.
[`final_registry_audit.json`](../evidence/k2/final_registry_audit.json) also
reports `unique: false`, three duplicate rows, one invalid file and an incomplete
inventory certificate. Comparison with only a subset cannot establish global
uniqueness. The lattice nearly covers the footprint, which indicates a protocol
conflict rather than a license to ignore the stop. Registry policy and assigned
lane must be clarified for a future run, without gaming edge cells.

The previous measured HOLDOUT-DTI is 0.1581 (95% CI 0.1424–0.1742;
`gems57-pooled-hide-v2`, 58,258 withheld positives). This is prior
mirror-based hide-and-recover evidence, **not** an independent replication,
private leaderboard estimate, or proof of a win against a matched incumbent.
The earlier K2 report is preserved as history and amended by this review.

## Pass 2 — safeguards and reproducible checks

The K2 command previously calculated a failed pre-placement measurement but
then unconditionally emitted and wrote dots. The historical run is now closed:
the CLI stops before any subcommand and the direct final routine also stops.
Prior evidence remains available, with corrected current status. The main page,
executive summary and submission guide now identify K2 as research-only.
A saved-byte local readback confirmed its SHA-256, one float32 band, finite
values 0–1, CRS, dimensions and transform. That does not establish a match to
an authenticated organizer template or acceptance by the portal. The original
rejected submission and receipt were not available here; the range-error cause
is unknown. The prior mirror-based outside-footprint policy remains unresolved.

## Pass 3 — scope, limitations and next work

The request's 0.4413 and 0.3195 leader values disagree. Network policy allows
GitHub and package registries, not DrivenData, Dropbox, USGS or the competition
portal; neither the live leaderboard, current quota, official template bytes,
nor organizer receipts can be verified in this session. The nine supplied
historical scores remain USER-REPORTED / UNVERIFIED. The stored champion
geometry supports a common-family/pruning relationship, but does not identify
the cause of the private score or prove that any candidate will exceed it.

The prior preregistration in
[`hypotheses-2026-10-28-preregistration.md`](hypotheses-2026-10-28-preregistration.md)
contains five ranked ideas with layers, mimics and costs. No new lane or
additional experiments are invented here. Before another run, establish the
assigned method lane and registry scope, restore an authenticated organizer
reference and full current cross-session inventory, determine the exterior
convention, and freeze a matched holdout incumbent. Use the common template
and stop on the first registry failure. A future selector must independently
check the current quota; no automatic upload is performed by this repository.

Sources for manual review: [DrivenData competition](https://www.drivendata.org/competitions/306/competition-doe-gems/),
[official problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution),
[USGS GeoDAWN dataset](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and),
[INGENIOUS](https://gbcge.org/current-projects/ingenious/). Links are provided
for review, not a claim they were reachable in this session.

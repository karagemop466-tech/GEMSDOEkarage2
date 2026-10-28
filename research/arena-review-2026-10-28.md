# Repository follow-up review — 2026-10-28

## Pass 1: existing work and constraints

Read the project instructions, README, previous K2 protocol review, preregistration,
site and selector. The earlier K2 experiment exhausted its three-experiment budget
and crossed the surface novelty stop before placing dots. The requested method lane
is not identified in the prompt, and the registry inventory was not complete. This
review runs no experiment, generates no TIFF and uses no submission slot. The
research TIFFs remain explicitly **DO NOT SUBMIT**. The existing five ranked ideas
are documented in `hypotheses-2026-10-28-preregistration.md`; that historical file's
self-assigned lane and conditional promotion language are superseded by
`k2-protocol-review-2026-10-28.md`.

The historical focus-site scores are supplied by the user, not authenticated
receipts. The decoded-mask relations documented in `../knowledge/champion_explanation.md`
suggest that pruning redundant predictions near mapped faults could improve a
score, but the hidden truth is unavailable, so causation and improvement over the
reported GEMSDOE32 result are not established. Holdout is not a calibrated estimate
of the private leaderboard score. The two different leaderboard values in the
request cannot both establish the current leader.

## Pass 2: bugs and fixes

A valid-looking selector card containing an oversized JSON integer in a numeric
measurement raised `OverflowError` instead of returning a negative verdict. The
selector now rejects such values without crashing; tests cover scores, canaries,
registry measurements and confidence intervals. This is a local evidence-schema
safeguard, not a change to the shared evaluator or writer. It does not authenticate
receipts, prove registry completeness, or authorize a slot.

The executive-summary research table header said “File to download” while its test
expected a research-only label. Changed the header to “File for research only” to
make the negative release status clearer. No artifact was promoted.

## Pass 3: verification and remaining work

- Python suite: 147 passed, 7 skipped, 36 subtests passed. Skips include
  unavailable data/dependency conditions; they are not successful validations.
- Feed tests: 3 passed; site tests: 8 passed; browser smoke passed at desktop and
  narrow widths. These verify interface behavior, not competition acceptance.
- `git diff --check` passed.
- No organizer data or receipt was authenticated and no new registry or holdout
  calculation was run. Prior saved results remain conditional on owner-mirror
  provenance. Network policy permits GitHub and package registries, not the
  DrivenData portal, Dropbox or the other linked official sites.

The next scientific run needs a coordinator-assigned lane and a consistent registry
policy, a complete cross-session registry, authenticated competition template and
input bytes, an agreed exterior/nodata convention, and a comparable frozen holdout
incumbent. Reuse the shared tooling, stop immediately on a novelty failure, and
leave slot selection separate. The literal lattice stop cannot be waived by this
review. External account access and portal quota/acceptance are not established.

Manual review: [competition](https://www.drivendata.org/competitions/306/competition-doe-gems/),
[problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/),
[official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution),
[USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and).
These links are for review; access to the non-GitHub sites was not verified here.

# Release gate review — 2026-10-28

## Pass 1: review and implementation
The archived K2 protocol review remains binding: no approved TIFF, no assigned
lane and no new experiment. The existing selector accepted a bare baseline DTI
without evidence that its evaluator, withheld truth or splits matched the
candidate. It now requires a HOLDOUT-DTI baseline with CI, evaluator and
positive count, matching SHA-256 identifiers for frozen split, truth and
scoring-configuration manifests, and a baseline evidence hash. Missing or
mismatched evidence fails closed. Existing negative decisions are unchanged.

## Pass 2: adversarial checks
Added tests for missing or mismatched fields, invalid confidence intervals and
malformed hashes. The selector checks the *structure and agreement of supplied
claims*, not the contents or authenticity of manifests or rasters. A matching
hash does not establish that the cited data were actually used. Independent
receipt/byte verification is still necessary. The paired CI is still a supplied
claim, not recomputed by this gate. Also corrected a pre-existing site test
failure: the K2 research-download column now explicitly says not submission.

## Pass 3: original request and next steps
The request for a new, high-scoring, unique ready-to-upload TIFF is **not met**:
the literal pre-placement stop, incomplete registry, missing specified lane,
unauthenticated organizer inputs and missing comparable frozen incumbent block
that claim. No competition slot was used. Historical scores are user-reported,
not organizer receipts, and catalogue holdout is not a leaderboard forecast.
The existing site has nine detailed summaries, submission guidance, research
artifacts and the earlier five preregistered hypotheses. They do not override
these blockers. Next: clarify the lane and literal registry scope; obtain
organizer-authenticated template and data, exterior handling and quota; freeze a
shared matched incumbent and manifests, then run a new protocol-compliant
experiment using the shared tooling. A separate selector decides on any slot.

Sources for review (not newly accessed here): [official competition](https://www.drivendata.org/competitions/306/competition-doe-gems/),
[official reference implementation](https://github.com/drivendataorg/gems-prize-reference-solution),
[USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and).
See [prior review](k2-protocol-review-2026-10-28.md) for measured evidence and
network limitations.

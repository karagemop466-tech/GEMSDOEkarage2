# Three-pass repository review — 2026-10-28 UTC

## Outcome and scope

No new experiment, new candidate TIFF, promotion, or competition upload. The user
prompt supplies no single method paragraph, and H1 already has a mandatory
surface-novelty stop. Generating a renamed or lightly perturbed historical file
would not meet the requested uniqueness requirement. The standing consolidated
prompt remains in README.md. This review changes this repository only, not the
nine independently owned upstream sites.

## Pass 1 — reconcile implementation and evidence

Read README.md, AGENTS.md, prior reviews/hypothesis slates and committed H1 and
independent-audit cards. Current dashboard incorrectly described labels as simply
unavailable despite H1's committed mirrored-data holdout result, called a legacy
research raster unique, and had six table headings for five rendered cells.
Corrected the dashboard/executive summary, linked the existing H1 negative
surface and receipt, and added navigation to measured and independent audits.
The leaderboard observation is now explicitly dated, not claimed live.

## Pass 2 — validation and bugs

Installed pinned dependencies into an ignored virtual environment. Regression
tests now check rendered column counts and forbid the misleading missing-label
and established-uniqueness claims. The first browser run exposed a pre-existing
mismatch between the main dashboard's artifact/button and the browser contract.
Aligned the primary page with the H1 research-only download and disabled
“No approved submission TIF” control. Added responsive dashboard styles and
horizontal table scrolling rather than page overflow. A local-link test caught
a directory URL; changed it to the explicit index.html target.

Re-read the saved H1 TIFF bytes: SHA-256 matches the committed card, one band,
all pixels finite, minimum 0, maximum 0.9152089953422546, EPSG:32611,
shape 3730 × 3292. These are FORMAT/INTEGRITY measurements, not scores.
This review did not authenticate the organizer template or rerun the holdout.
The saved range does not authorize upload; the previous novelty stop remains.

## Pass 3 — full request and remaining blockers

- Python: 113 passed, six skipped (optional pinned-cache integrations), 33 subtests.
- Node feed: three passed; dashboard: seven passed.
- Browser: desktop 1440px, mobile 390px and 320px primary dashboard; audit/detail/
  guide navigation; stale and unavailable source handling; no viewport overflow.
- Existing site generators remain reproducible; no evaluator/writer fork changed.
- Preflight fails closed: no assignment, prepared cache, complete current registry,
  authenticated organizer template, or frozen same-fold incumbent in this checkout.
- No current leaderboard read or organizer score receipt was obtained. Historical
  community claims must not be labeled ORGANIZER-CONFIRMED. No defensible private
  leaderboard estimate exists for any listed file.

H1's prior HOLDOUT-DTI is 0.03367297511935826, 95% CI
[0.028673795591260962, 0.03929480282078235], evaluator
gems57-pooled-hide-v2, 58,259 withheld positive pixels. It was not rerun here;
its paired improvement against its primitive control was negative and its
registry surface overlap hit the stop. See ../evidence/h1/run_card.json.

The nine best-file geometry audit supports a plausible explanation for B2:
GEMSDOE32 deletes 2,545 catalogue-adjacent dots from the solo set. DTI can reward
removing redundant false-positive mass while preserving nearby truth coverage.
Without hidden labels and a receipt this is not a causal explanation of the
user-reported 0.2778, and does not predict that pruning will improve a new file.
See ../knowledge/champion_explanation.md and ../evidence/champion_forensics.json.

## Next session, in dependency order

1. Resolve the lane assignment and lattice comparator policy across sessions;
   preserve literal gates until coordinated policy changes are explicit.
2. Restore pinned shared prepared features and full current registry; authenticate
   organizer template, band metadata and exterior nodata. Mirror hashes alone
   establish integrity relative to a mirror, not organizer provenance.
3. Land shared continuous-prediction fixes upstream, not a private evaluator fork.
4. Reconstruct the same-protocol incumbent. Use the already recorded ranked
   hypothesis slate in hypotheses-2026-10-27.md; those ideas remain unvalidated,
   not approved lanes. No new external-data hypothesis was declared viable here.
5. Run at most three experiments/two hours, feature canaries first, surface
   novelty before placement, buffered whole-segment holdout, final novelty and
   saved-byte format validation. A separate selector checks current weekly quota.

## Official sources for later authenticated verification

- https://github.com/drivendataorg/gems-prize-reference-solution
- https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- https://docs.nlr.gov/docs/fy26osti/96647.pdf

Only GitHub and package registries are allowed outbound hosts in this session.
These links are supplied for review, not represented as newly retrieved official
verification. No credentials are requested or stored. No claim of a completed
unique, high-scoring submission is justified by this work.

## Concurrent review integration

Main advanced through PR #13 while this review was open. Integrated its safer
submission guide and release-language regression tests, preserved its corrected
data-provenance and historical-geometry wording, and retained the explicit
100% versus 70% historical lattice failure on the landing page. The primary
download remains H1, not the historical irregular raster.

### Other session review (preserved verbatim)

# Follow-on review — 2026-10-28

## Decision and scope

No additional experiment or competition submission was made. The prompt refers to a
single lane paragraph but does not identify one. The complete current registry,
organizer-authenticated template and same-fold frozen incumbent are unavailable in
this checkout. Scratch data mentioned in prior run cards is not present here. Do not
claim a unique, high-scoring or approved TIFF. Prior H1 failed its registry gate;
the historical irregular raster's own run card records 100% lattice overlap despite
its contradictory `unique_by_construction` field. Preserved that card as historical
evidence, not as a clearance.

## Three review passes

1. Read the standing instructions, prior independent review, hypotheses, run cards,
   site and historical artifact. Corrected the landing page and submission guide,
   replacing upload instructions for a failed research file with a fail-closed path.
2. Reconciled conflicting descriptions of the feature mirrors and lattice coverage;
   removed the assertion that all nine masks have identical dot geography. Replaced
   claims about the cause of the portal rejection with a diagnostic recommendation.
3. Rechecked the requested priority: no defensible score estimate, complete-registry
   uniqueness, organizer receipt, or approved download exists. Prior hypotheses are
   preserved in `hypotheses-2026-10-27.md`; no fresh geological hypothesis was tested
   or assigned. Original nine sites are separate repositories, not modified here.

## Next steps

Obtain the named lane and complete pinned registry, authenticate input/template bytes,
fix the shared continuous-probability tools upstream if needed, and reconstruct a
same-fold incumbent. Then run canaries and buffered holdout before any separate
selector decision. The competition and third-party data hosts are outside this
sandbox's network allowlist; no live leaderboard or organizer receipt was checked.

Also integrated PR #14: retired unsafe legacy generator, stricter readiness
registry coverage checks, corrected per-site links and updated submission guide.
Kept one primary TIFF download and its separately linked audit receipt.

# Three-pass review: byte-bound raster audits (2026-10-28)

## Pass 1 — evidence and task

Read the consolidated prompt, AGENTS.md, prior K2 protocol correction and selector.
No method lane is identified in the supplied prompt. The prior K2 run violated the
pre-placement stop; its 100% lattice overlap is a duplicate under the literal
rule. A changed filename or byte hash does not fix that. No experiment, new TIFF,
selector promotion, upload, or leaderboard read was performed in this review.
Existing focus-site summaries are linked from the dashboard; historical site
results are user-reported, not organizer receipts. K2's prior HOLDOUT-DTI
0.1581207190 (95% CI 0.1423739219–0.1741535541, gems57-pooled-hide-v2,
58,258 withheld positives) is a proxy, not a calibrated leaderboard estimate.
The previous source and hypothesis slate are preserved in
`research/hypotheses-2026-10-28-preregistration.md` and
`knowledge/champion_explanation.md`. The suggested explanation of the reported
GEMSDOE32 result is reduced redundant false-positive mass from pruning near known
faults; causality and generalization are not established by a score alone.

## Pass 2 — bugs

The independent novelty and format audits bound TIFF SHA-256 values but Rasterio
also reads external mask/metadata sidecars. Such files can change a dataset's
interpretation without changing the bound TIFF digest. Both audits now reject
Rasterio datasets reporting companions, rather than silently issuing a receipt
that omits them. Internal TIFF masks remain part of the hashed file. This is a
local fail-closed restriction, not a claim about organizer requirements. It does
not authenticate templates, bind transient concurrent changes, or prove registry
completeness. Tests cover external masks on template, candidate and reference.

The evidence schema gate also rejected malformed values but crashed on extremely
large integer AUCs; these now fail closed. The executive summary's K2 table header
was inconsistent with an existing regression test and insufficiently explicit;
it now calls the file research-only. No shared evaluator or writer was modified.

## Pass 3 — verification and unresolved requirements

- Python tests: 151 passed, 7 skipped, 34 subtests. Skips are not evidence of
  passing integration against unavailable data.
- Node: 3 feed and 8 site tests passed. Browser smoke: desktop and mobile passed.
- Site builders ran; no generated-page changes besides the intentional header.
- The sample/template is still not organizer-authenticated; external-host access
  is restricted to GitHub and package registries. Current official leaderboard,
  submission quotas and portal acceptance were not independently checked. The
  contradictory user-supplied leaderboard figures are not treated as current.
- Any new trial requires an actual lane assignment, a coordinated registry-scope
  ruling, a complete pinned registry and authenticated organizer data and template.
  After those prerequisites, follow canaries, pre-placement novelty, buffered
  holdout, final novelty and format validation before a separate slot selector.
  If literal lattice scope remains unchanged, the prior K2 is negative and must
  not be submitted. A valid TIFF cannot be promised from incomplete evidence.

Reference solution repository: https://github.com/drivendataorg/gems-prize-reference-solution
(GitHub metadata retrieved this review). Official manual review links:
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/,
https://www.drivendata.org/competitions/306/competition-doe-gems/data/ and
https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/.
Those DrivenData pages were not retrieved in this environment.

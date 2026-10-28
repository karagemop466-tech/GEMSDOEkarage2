# Follow-on three-pass review — 2026-10-28

## Pass 1 — inventory and decision

Read the operating README, AGENTS.md, prior reviews and K2 receipts. The prompt
contains no identifiable assigned method paragraph. The preceding K2 run used
three experiments and crossed the >70% registry stop before dot placement; its
research raster is not eligible to submit. No new experiment, placement, model
training, portal access or competition submission was performed here. The
previously preregistered five ranked ideas and their caveats are in
[`research/hypotheses-2026-10-28-preregistration.md`](../research/hypotheses-2026-10-28-preregistration.md);
that document's conditional promotion and causal claims are superseded by
[`research/k2-protocol-review-2026-10-28.md`](../research/k2-protocol-review-2026-10-28.md)
and [`research/independent-review.md`](../research/independent-review.md).

GitHub API HEAD metadata was fetched at the time recorded in
[`docs/evidence/source-head-review-2026-10-28.json`](../docs/evidence/source-head-review-2026-10-28.json).
All nine focus heads differed from the 2026-10-27 reviewed refs. A changed HEAD
means the historical snapshot needs a new audit; it does **not** establish a
new file, score, receipt, or changed competition outcome. No GitHub HEAD feed
is a leaderboard feed. The [official reference repository](https://github.com/drivendataorg/gems-prize-reference-solution)
was reachable; DrivenData, USGS, GDR and Dropbox were not reachable under the
session network allowlist. [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/),
[problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and),
and [INGENIOUS](https://gbcge.org/current-projects/ingenious/) links are for
review, not a claim of fresh access.

## Pass 2 — concrete fixes

* Independent TIFF and registry audits used a TIFF-only hash but Rasterio could
  read a separate GDAL `.msk` or other external dependency. The audit now rejects
  datasets whose GDAL file list contains external files. This is fail-closed and
  allows internal masks; it is not organizer authentication or proof against
  concurrent filesystem manipulation. Shared template code was not modified.
* `refresh_sources.py` now reuses the GitHub-only bounded reader and same-origin
  redirect guard used by `refresh_feed.py`; malformed payloads fail to unavailable.
* `prepare_data.py` previously returned success for mismatched grids and could
  leave a stale successful receipt when inputs went missing or were unreadable.
  It now reports failure and invalidates that receipt. The download helper no
  longer claims placement makes a retired pipeline ready. These remain basic
  local checks, not full validation or input authentication.
* The K2 executive-summary table header now labels the download for research,
  restoring an existing failing website test and reducing upload ambiguity.

## Pass 3 — remaining blockers

The requested unique, high-scoring submission, calibrated leaderboard estimate,
and organizer receipt do not exist here. Resolve the lane and literal registry
scope conflict before new experimentation; authenticate the template, bands,
and exterior convention; update and audit the cross-session registry and the
focus-site revisions; rebuild a leakage-safe incumbent on the same folds; then
run the canaries, holdout and pre-placement check under a fresh authorized budget.
An independent, quota-aware selector is still required. The existing [H33
forensics](../research/independent-review.md) supports a dotted-family/apron
relationship, not a proven cause of the user-reported 0.2778 or a transferable
leaderboard estimate. No explanation for the reported range rejection can be
proven without the actual rejected file and portal receipt.

Verification: the full Python suite passed after restoring hash-pinned public
research mirrors and the shared template into the ignored cache: 167 passed,
34 subtests passed, none skipped (Rasterio emitted deprecation warnings).
The nine-raster audit reproduced the published snapshot except creation time.
Node feed and site tests and the desktop/mobile browser smoke checks passed.
These are local software checks, not new geological experiments or portal
acceptance. The mirrors remain unauthenticated organizer inputs.

## Concurrent main integration

During the pull request, other sessions merged a B4 research artifact. Its
archived registry audit reports lattice overlap 1.0 and no passing pre-placement
receipt was found in the committed B4 evidence. Its generator was able to write
final dots without that required check. The historical artifact and receipts
are preserved as negative evidence, while the CLI and direct final function now
stop; the public pages no longer claim global uniqueness or a proven H33 causal
explanation. Its historical holdout is not replayed here, and differing withheld
positive counts prevent asserting exact fold identity with K2 without more evidence.

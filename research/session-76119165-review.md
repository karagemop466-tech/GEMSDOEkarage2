# Repository review — 2026-10-28, session 76119165

## Outcome

**Negative; no competition submission approved.** No experiments, dot placement,
new TIFF generation, or competition slots were used. The earlier three-experiment
K2 budget remains exhausted; the supplied prompt still has no identifiable assigned
method paragraph. Repeating training would violate the existing stop, not resolve it.

Read README.md and AGENTS.md at session start. The README already records the
consolidated project prompt, core values, nine-site scorecard, and protocol. The
prior five-hypothesis preregistration remains historical, not a fresh lane assignment:
[preregistration](hypotheses-2026-10-28-preregistration.md). Its claims of a live
leaderboard and some causal language are not independently verified by this review;
the subsequent protocol correction supersedes its proposed registry exemptions.

## Pass 1 — implementation and checks

- Reviewed existing scientific, uniqueness, release, and site evidence. No file-linked
  organizer receipts are available. The supplied nine-site values remain unverified
  user reports, not measured leaderboard estimates.
- Found a genuine failing dashboard regression: the executive summary's K2 header
  said “File to download” where the safety test required “File for research”. Fixed
  the header to explicitly say research only / DO NOT SUBMIT.
- Hardened `scripts/readiness.py`: a recorded `verdict: negative` or
  `protocol_stop_triggered: true` cannot be overridden by otherwise passing fields.
  A malformed stop declaration also fails closed. This is evidence-schema validation,
  not a replacement evaluator or writer and not evidence authentication.

## Pass 2 — edge cases and regression tests

Added regressions for negative verdict preservation and true, null, string, number,
object, and array stop declarations. Only the boolean false explicitly declares no
stop. Optional omission preserves compatibility with older evidence cards; absence
must not be mistaken for an independently audited experiment history. A future
selector still needs authenticated, file-bound receipts and full registry history.

Executed on this checkout:

- Python: 148 tests passed, 7 skipped, 40 subtests passed. Skips require unrestored
  pinned mirror rasters/shared tools. These integration checks were not executed.
  There were 38 Rasterio/Affine deprecation warnings, not validation failures.
- Node feed: 3 tests passed; site: 8 tests passed.
- Browser smoke: desktop and mobile layouts, locked release, research-only download,
  nine-site navigation, and changed/unavailable freshness states passed. Network
  freshness responses in this test are simulated, not a live source verification.
- `build_site.py` preserved the correction; `build_audit_site.py --check` passed.
- Existing H1 release assessment and K2 release audit both remained negative. The
  latter rechecked saved TIFF bytes but inherited scientific/registry measurements;
  no holdout or full registry scan was rerun.

## Pass 3 — requirements and limits

The existing executive summaries cover all nine focus sites with historical filenames,
reported results, unavailable estimates, and negative eligibility. None may honestly
be called the best *new unique* submission. GEMSDOE32's previously audited relationship
to the earlier dotted family supports pruning redundant predictions as a plausible
mechanism, not a verified cause of the hidden score. No evidence establishes that a
new raster will exceed the supplied result. Geothermal resource discovery and this
challenge's fault-prediction target should not be conflated.

The original range-error upload/receipt is absent. Local [0,1] checks cannot diagnose
that upload or prove portal acceptance; organizer template authority and exterior
encoding remain unresolved. Scientific gates cannot be waived to provide a download.

### Source status

Verified through the GitHub API this session that the official reference repository
exists, describes itself as the GEMS Prize Challenge reference solution, and uses
`main`: https://github.com/drivendataorg/gems-prize-reference-solution . This metadata
check does not authenticate the private scorer or competition input rasters.

Official links retained for manual review, **not accessed in this session** because
those hosts are outside the runtime network allowlist:

- https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- https://www.drivendata.org/competitions/306/competition-doe-gems/data/
- https://docs.nlr.gov/docs/fy26osti/96647.pdf
- https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- https://gdr.openei.org/submissions/1391

### Next session, in order

1. Obtain an explicit coordinator lane and registry policy; do not silently exempt
   calibration rasters or design edge placement to evade them.
2. Authenticate organizer template/footprint and exterior convention; obtain an actual
   submission-page receipt to bind any organizer score to a file hash.
3. Restore shared cached stack/tools, certify registry completeness and freeze a
   same-fold incumbent before any authorized new experiment budget begins.
4. Canary every feature, evaluate buffered whole segments, stop on surface duplication,
   and only then consider final placement. A separate selector must verify current
   account quota; no automatic competition submission is authorized here.

Run card: [session-76119165-run-card.json](../evidence/session-76119165-run-card.json).

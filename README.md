# GEMS Field Notes

**Current decision: NO NEW TIFF · DO NOT SUBMIT.** No prediction, holdout score,
or weekly slot has been produced in this checkout. A format-valid old file is
not a unique new submission. See the [dashboard](docs/index.html), the
[executive submission guide](docs/executive-summary.html), and the
[machine-readable run card](evidence/run-card.json).

The repository began as an empty README. This review restored a pinned **owner
mirror** of the core rasters and ran the upstream shared template's preparation
and feature-cache builder. The cache is ignored/non-persistent and the mirror is
**not organizer-authenticated**. The mirrored “sample” contains the known labels,
while the organizer describes a total-absence example. The actual authenticated
sample, a named parallel lane, a complete registry, a same-evaluator best,
feature canaries, a leakage-safe holdout and a separate selector are still
needed. The literal lattice check blocks a champion-sized dot budget; see the
[reproducible geometry audit](evidence/geometry-audit.json).

## User's operating charter — read at the start of every session

This section preserves the non-duplicated operating requirements of the user's
request. The [user-supplied historical inventory](research/user-reported-submissions.md)
preserves the submitted site/file/value claims; those claims are not receipts.
The full repeated chat text itself is not represented as a verbatim transcript.

> **Goal.** The goal of this project is to place top of the leaderboard in the
> [DOE GEMS competition](https://www.drivendata.org/competitions/306/competition-doe-gems/).
> Create a unique TIF submission, not a copy of a previous submission. The site
> should make the file easy to download and make it obvious whether it is OK to
> submit. Provide a clear executive summary, a table of the nine priority sites,
> score evidence and uniqueness, official sources, exact submission steps, a
> unique name and a note of at most 140 characters. Do not invent results.
>
> **Core Values.** Maximize P(Win): weigh tradeoffs and choose the path that
> maximizes the probability of success. Own the Outcome: own results end to end,
> treat failure and success as signals, and use them to improve.
>
> **PARALLEL-RUN PROTOCOL — read first.**
>
> 1. **LANE.** Your lane is the single method paragraph below. Stay inside it. If
>    your raster's rank-correlation with any registry raster exceeds 0.90, or
>    more than 70% of your dots fall within 3 px of one registry raster's dots,
>    log it as a duplicate and stop. Check this on the surface before placement
>    AND on the final dots.
> 2. **REUSE, DON'T REBUILD.** Use the template's cached feature stack,
>    `evaluate_holdout.py` and `submission_writer.py`. Holdout = hide-and-recover:
>    withhold whole fault segments with a buffer, derive every catalogue-based
>    feature only from the visible faults, mask visible faults pixel-exactly,
>    score pooled DTI (α 0.2, β 0.8, 300 m triangular kernel). If a shared tool
>    is wrong, fix it once in the template and report it; never keep a private fork.
> 3. **LABEL EVERY NUMBER** as HOLDOUT-DTI (evaluator version, number of withheld
>    positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page
>    receipt). A projection is never written as a score. User-reported historical
>    numbers without receipts must remain explicitly unverified, never promoted
>    into either evidence class.
> 4. **LEAKAGE CANARY.** Test each feature alone on the holdout before trusting
>    any result. AUC above 0.90 means leakage until proven otherwise.
> 5. **RUN CARD.** End with one JSON card: hypothesis; mechanism; the named
>    non-fault process that could mimic it; holdout DTI + CI; correlation/overlap
>    vs registry; raster sha256; validator output (no NaN inside the footprint,
>    values in [0,1], CRS/shape/transform match); submission name + note of at
>    most 140 characters; verdict promote / negative. Negative results are deliverables.
> 6. **BUDGET.** Stop after 3 experiments or 2 hours. Do not pick submissions:
>    promotion to a real slot is a separate selector step, within the weekly cap
>    shown on the submission page.
>
> **Research first.** Before implementing, rank 3–5 distinct geological
> hypotheses by expected DTI improvement and implementation cost, identifying
> layers, physical signatures, why they might discover uncatalogued faults,
> differences from previous work, and non-fault mimics. Check whether any needed
> free official data are obtainable. Validate the top assigned candidate on the
> spatially blocked holdout against the current comparable best before a slot.
>
> **Three passes.** Implement and verify; review for bugs, gaps and assumptions
> and fix them; then re-check the original request and improve accuracy,
> reliability, completeness and quality. Create and merge a PR when possible.
> Work autonomously, cite official trustworthy sources, flag irregularities,
> avoid hallucinations, and state limitations and next steps. Validation should
> be automated rather than dependent on a human image inspector.

The request references a “single method paragraph below” but supplies no actual
assigned lane. The ranked proposal is **not** permission to invent one. The
nine historical files all fail the literal final-dot rule against another
priority file; their user-provided values have no organizer receipts. A local
holdout estimate cannot honestly be converted to a leaderboard forecast.

## Reproduce the research preflight

Requires Python 3.11, GitHub CLI access, several GB of free disk and internet
access to the pinned GitHub mirrors. No credentials are saved in this repo.
The shared source and data remain in `.cache/`; they are not distributed here.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/bootstrap_template.py      # core mirror + shared 35-channel cache
.venv/bin/python scripts/restore_references.py    # nine fixed historical rasters + lattice
.venv/bin/python scripts/geometry_audit.py         # research-only geometry receipt
.venv/bin/python scripts/preflight.py              # expected nonzero: NO submission is approved
.venv/bin/pytest -q tests
python scripts/build_site.py
python -m http.server 4173 --bind 0.0.0.0 --directory docs
```

`bootstrap_template.py --verify-only` checks the critical shared files already
in cache; `--skip-stack` skips the larger feature build. The feature cache alone
is approximately 1.7 GB. The mirror and cached features can be recreated, but
are not guaranteed to persist between sessions. The
[preparation receipt](evidence/preparation.json) records hashes and versions.

`validate_tif.py CANDIDATE --template AUTHENTICATED_SAMPLE` reopens and checks
saved bytes; it does **not** approve a slot. The local strict check requires NaN
outside the footprint and also reports whether the whole raw array is finite and
in range. That conservative outside-footprint interpretation is not proof of
organizer acceptance; do not assume either encoding fixes a portal rejection.
The separate `check_uniqueness.py` checks a preregistered surface/support before
placement and final dots afterwards against an explicit hash-pinned registry;
a manifest's claim of completeness is not independent proof of completeness.

## Evidence and open work

* [Nine-site and DTI analysis](research/findings-2026-10-27.md); [four ranked,
  unrun hypotheses](research/hypotheses-2026-10-27.md).
* [Pinned research references](registry/focus_sites.json),
  [geometry receipt](evidence/geometry-audit.json), and
  [negative run card](evidence/run-card.json).
* The pinned upstream `evaluate_holdout.py` and `submission_writer.py` convert
  positive continuous inputs into booleans. Do not trust them for continuous
  probabilities without an **upstream** fix and tests; this repo does not fork
  them. A static candidate also does not prove fold-local feature construction.
* The hosted [source feed](docs/data/source-feed.json) tracks GitHub branch
  heads only, marks unavailable/stale sources, and does not scrape DrivenData,
  infer scores, check quota, or prove complete registry coverage. GitHub Pages
  is refreshed by [the workflow](.github/workflows/pages.yml) when enabled.
* Official sources: [problem, metric & format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
  [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf),
  [organizer leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/),
  [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution),
  [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and),
  [DOE INGENIOUS](https://gdr.openei.org/submissions/1391), and
  [known-fault masking clarification](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2).

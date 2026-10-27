# GEMS field intelligence

**Decision: NO COMPETITION FILE IS APPROVED. DO NOT SUBMIT.**
This checkout began with only a README. In this session no model, holdout score,
new candidate GeoTIFF, or weekly-slot selection was produced (tests create only temporary synthetic TIFFs). A registered calibration
lattice makes the requested strict uniqueness rule impossible at the historic
H33-sized budget. The geometry, source pins and negative run card are available
in the [executive site](docs/index.html) and [review](research/REVIEW.md).

The previous claim that only data placement was needed for an existing local
pipeline was not true of this checkout. A hash-matched owner mirror of the raw
features was fetched for research; it is not an organizer-authenticated download.
The prepared shared stack, explicit single method lane, full live parallel
registry, matched frozen holdout best, score receipts and account quota remain
unavailable. **Important discrepancy:** the mirrored `example_submission.tif`
contains 60,988 positive pixels and matches the mirrored known-fault labels,
while the organizer describes its sample as predicting total fault absence.
The mirror's grid is useful for this research audit, but its sample identity and
the official validation footprint remain unverified. Do not confuse local file validity with a high score or an approved
upload.

## Standing brief — read at the start of every session

The owner's goal is a **new, genuinely unique, evidence-led fault prediction**
for the DOE GEMS competition, with an obvious one-click download only after
scientific, format and uniqueness gates have passed. Research the strongest
historical submissions in GEMSDOE24, 25, 27, 28, 30, 31, 32, 33 and 36; provide
an executive comparison, honest uncertainty, official source links, and an
exact submission guide. Do not copy or rebrand an old submission. The target is
fault mapping; geothermal discovery motivates it, but a predicted line is not a
confirmed fault or geothermal vent. Work autonomously, flag irregularities and
perform three review passes.

The user-provided request was repeated in full in the session. This durable
charter preserves its operative requirements and verbatim protocol below rather
than presenting a duplicated list of unverified numerical claims as scores.
The session transcript remains the source for the complete original wording.

### Parallel-run protocol (verbatim operating rules)

1. **LANE.** Your lane is the single method paragraph below. Stay inside it. If
   your raster's rank-correlation with any registry raster exceeds [0.90], or
   more than [70%] of your dots fall within 3 px of one registry raster's dots,
   you have drifted into another lane: log it as a duplicate and stop. Check
   this on the surface before placement AND on the final dots.
2. **REUSE, DON'T REBUILD.** Use the template's cached feature stack,
   `evaluate_holdout.py` and `submission_writer.py`. Holdout = hide-and-recover:
   withhold whole fault segments with a buffer, derive every catalogue-based
   feature only from the visible faults, mask visible faults pixel-exactly,
   score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared
   tool is wrong, fix it once in the template and report it; never keep a
   private fork.
3. **LABEL EVERY NUMBER** as HOLDOUT-DTI (evaluator version, number of withheld
   positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page
   receipt). A projection is never written as a score.
4. **LEAKAGE CANARY.** Test each feature alone on the holdout before trusting
   any result. AUC above [0.90] means leakage until proven otherwise.
5. **RUN CARD.** End with one JSON card: hypothesis; mechanism; the named
   non-fault process that could mimic it; holdout DTI + CI; correlation/overlap
   vs registry; raster sha256; validator output (no NaN inside the footprint,
   values in [0,1], CRS/shape/transform match); submission name + note of at
   most 140 characters; verdict promote / negative. Negative results are
   deliverables.
6. **BUDGET.** Stop after [3] experiments or [2] hours. Do not pick submissions:
   promotion to a real slot is a separate selector step, within the weekly cap
   shown on the submission page.

A method paragraph assigning a lane was not present in the supplied request.
Do not manufacture one or quietly remove a registry comparator. Geometric
counts, hashes, configuration and uncertainty diagnostics are labelled by type;
none is a claimed score. A public leaderboard row is official public standings,
not evidence linking an owner file to an organizer receipt.

### Core values

- **Maximize P(Win):** weigh tradeoffs and protect scarce submission slots;
  prioritize defensible improvements over optimistic projections.
- **Own the Outcome:** verify end to end, expose blockers and correct errors
  rather than presenting an attractive but unsupported result.

## Evidence and reproducibility

- [Executive summary and nine-site table](docs/index.html)
- [Submission guide](docs/submit.html)
- [Four ranked hypotheses and the stopped test plan](research/HYPOTHESES.md)
- [Official sources and exact limits](research/SOURCES.md)
- [H33 forensic review and irregularities](research/REVIEW.md)
- [Reference audit JSON](docs/data/reference-audit.json) ·
  [negative run card](docs/data/run-card.json) ·
  [immutable input and shared-tool pins](research/reference-sources.json)

Requires Python 3.11+, `gh` authenticated or permitted to read public GitHub,
and outbound access to GitHub and PyPI. No DrivenData credentials are required
or requested for the research mirrors. Inputs are placed under ignored `.cache/`
and never committed. The audit uses the unmodified, hash-verified shared
GEMSDOE24 novelty and submission modules, not a local private metric fork.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
python scripts/bootstrap_research.py            # nine reference TIFFs, lattice, template tools
# Optional ~400 MB owner feature mirror, SHA-256 checked; not needed for preflight:
bash scripts/fetch_feature_mirror.sh
.venv/bin/python scripts/audit_references.py --output docs/data/reference-audit.json
.venv/bin/python scripts/check_submission.py path/to/a/file.tif  # format only, never authorizes
.venv/bin/pytest -q
npm ci --ignore-scripts                  # Node >=22.17; browser test dependencies
npm test && npm run test:browser       # responsive, navigation and freshness checks
python scripts/serve_site.py           # safe preview at http://localhost:8000
```

**No score estimate is available.** A local catalogue holdout is a biased proxy
for the organizer's hidden new-fault labels, and no validated transfer from one
to the other is known. See the live [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/),
[problem and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[competition rules](https://www.drivendata.org/competitions/306/competition-doe-gems/rules/),
and [official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution).
The source-freshness feed on the site checks public repository commits, not the
private submission page or the completeness of the live registry.

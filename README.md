# GEMS Research Desk

**Current decision: DO NOT SUBMIT.** A parallel session generated one new,
continuous H1 research GeoTIFF, but it failed the literal registry gate and its
holdout comparison. It is downloadable for research only; no final dots, slot
selection, organizer acceptance or competition submission exists. The later
independent audit ran **zero additional experiments**.

Parallel-session **HOLDOUT-DTI** `gems57-pooled-hide-v2`: 0.03367, 95% CI
[0.02867, 0.03929], 58,259 withheld positives; this audit did not rerun that
holdout. Independently rechecked saved bytes, owner-mirror grid and 100% positive
surface support proximity to the lattice. This is not a leaderboard forecast.

[Open the project site](https://karagemop466-tech.github.io/GEMSDOEkarage2/) ·
[Executive summary and instructions](docs/executive-summary.html) ·
[H1 negative run card](evidence/run_card.json) · [Independent surface audit](docs/data/parallel-surface-audit.json) · [Nine-site audit](docs/data/focus_audit.json)

## Standing project brief (read at the start of every session)

The objective is to make a **genuinely new, evidence-backed fault-prediction
GeoTIFF** for the [DOE GEMS Prize](https://www.drivendata.org/competitions/306/competition-doe-gems/)
that can compete for the top of the leaderboard. The task is fault mapping
relevant to geothermal exploration, **not proof of geothermal vents**. Give an
obvious executive summary with each of GEMSDOE24, 25, 27, 28, 30, 31, 32, 33
and 36, the exact research file, evidence class, honest score-estimate status,
uniqueness and submission permission. Do not present a previous submission as a
new one. If no submission is justified, say so clearly. The project should
reduce manual checking and keep a dated, failure-aware source feed.

The working principles are **Maximize P(Win)** (weigh evidence and scarce
submission slots rather than chase an unverified score) and **Own the Outcome**
(verify the entire chain, preserve negative results and disclose blockers).
Rank three to five specific, untried geological hypotheses before implementing:
name their layers, physical signature, why they might find an uncatalogued fault,
non-fault mimics, differences from prior work, likely DTI value and cost. Any
external data must be licensed for challenge use and its availability verified;
unknown fleet-wide novelty and data coverage must be called unknown. Use official
sources and links; never invent data, confidence, scores, or receipts. Follow the
[research slate](research/hypotheses.md) and [source register](research/sources.md).

### Parallel-run protocol retained from the request

1. **Lane:** use the single explicitly assigned method paragraph; if the raster's
   rank-correlation with *any* registry raster exceeds 0.90 or more than 70% of
   dots fall within 3 pixels of one registry raster's dots, log a duplicate and
   stop. Check the surface before placement and final dots. Do not silently omit
   a calibration control or alter a placement just to exploit holes.
2. **Reuse:** use the template's cached feature stack, `evaluate_holdout.py` and
   `submission_writer.py`; do not keep a private fork of shared tools. Withhold
   whole fault segments with a buffer, derive all catalogue features from visible
   faults only, mask visible faults pixel-exactly, and pool DTI using alpha 0.2,
   beta 0.8 and a 300 m triangular kernel. Fix a proven shared-tool defect in the
   shared template once, not as a private patch.
3. **Evidence:** label holdout scores `HOLDOUT-DTI` with evaluator version,
   withheld positives and 95% CI; label a score `ORGANIZER-CONFIRMED` only when
   copied from a file-bound submission-page receipt. No projection is a score.
   Existing numbers without receipts are explicitly `USER-REPORTED / UNVERIFIED`,
   never misrepresented as organizer-confirmed.
4. **Leakage canary:** test every feature alone; AUC above 0.90 is leakage until
   proven otherwise. Fail closed when the canary is missing or incomplete.
5. **Run card:** record hypothesis, mechanism, a named non-fault mimic, holdout
   DTI and CI, registry correlation/overlap, raster SHA-256, saved-byte validator
   output (finite in footprint, [0,1], CRS/shape/transform), submission name,
   note at most 140 characters, and `promote` or `negative`. A negative result
   is a deliverable, not an invitation to label it ready.
6. **Budget and selector:** stop after at most three experiments or two hours.
   Do not choose or spend a real slot in the lane; a separate selector acts only
   after all gates pass and after checking the portal's weekly cap.

Review the implementation in three passes: implement and verify; look for
bugs, missing requirements, false assumptions and edge cases and fix them; then
recheck against the full request and improve remaining reliability. No human
inspector substitutes for programmatic validation. A competition portal login,
legal eligibility decisions, file-bound receipts and official team quota cannot
be truthfully fabricated.

## Why the requested submission is blocked

* No single method paragraph was assigned in the prompt; parallel lanes cannot
  safely be inferred. The prepared shared feature cache and full parallel registry
  are absent. An optional owner-mirrored 19-band input has been hash-checked,
  but is not authenticated by the organizer. The pinned shared-tool manifest is
  only a partial download, not a complete runnable template checkout.
* The registered [r13 lattice](https://github.com/buffedlizard55-lab/13GEMSDOE/blob/92ee6f074323f161eed837b80ec3ee5b662e26f5/docs/downloads/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif)
  covers 5,160,724 of the owner-mirrored footprint's 5,167,373 cells within
  3 pixels. At the historical champion's 37,654-dot reference budget, even an
  optimal placement must overlap by at least **82.34%**, above the literal
  70% limit. This is a geometry bound, **not a score**; it does not prove every
  smaller budget impossible. Do not manufacture a pass by aiming at lattice holes.
* All nine pinned historical files are duplicates of at least one other of the
  nine under the requested rule. The highest **USER-REPORTED / UNVERIFIED**
  historical claim is GEMSDOE32 `h33-h33-2-b2` at **0.2778**. There is no
  file-bound organizer receipt or defensible estimated leaderboard score for a
  new file. The public leaderboard is separate and changes over time.
* The public owner-mirror `sample_submission.tif` has positive pixels exactly
  matching the mirrored existing faults; the official page describes a
  fault-absence sample. Grid checks against this mirror are useful for the
  limited forensic audit, but its origin and equivalence to the real sample are
  not independently authenticated. The user's prior `[0,1]` portal error
  cannot be diagnosed from this mirror alone.

These are reasons not to promote or run another experiment, not a claim that a
better geological method is impossible. H1 stopped before dot placement. [Details and next steps](research/review.md).

## Reproduce the independent audit

Python 3.11, GitHub CLI and internet access to GitHub are required. Large data
and runtime environments are ignored by Git. The following commands do **not**
make a submission or run a model:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/bootstrap_shared.py --core  # ~419 MB owner-mirror core inputs, hash checked
python scripts/audit_focus.py --fetch       # nine historical files + one lattice witness
python -m pytest -q
npm ci --ignore-scripts
npm run test:site
```

`bootstrap_shared.py` restores the pinned upstream shared-tool files and uses
unchanged upstream code to restore the public core mirrors into `.cache/`.
Their hashes establish consistency with the owner manifest, not official
provenance. The partial protocol bundle is **not** a self-contained generic
holdout runner; the prepared 32-feature array is not in the public tree. The
unchanged shared format checker can be run with `python scripts/check_format.py
PATH_TO_TIF`; it cannot authorize a submission or prove portal acceptance, and
its conservative whole-array diagnostic rejects NaN-outside files. The parallel
session also vendored a separate unchanged shared GEMSDOE32 evaluator and writer
with hashes in `vendor/NOTICE.md`; neither is a private modified fork.
`audit_focus.py` is an independent
geometry/forensic check, not a replacement holdout evaluator or a writer. Its
source-pinned input manifest is `registry/pinned_assets.json`; cached inputs are
not committed. For this checkout, the nine raster files, the lattice, the
existing-fault raster and the template mirror were independently fetched and
rechecked.

For a local site preview, run `python scripts/serve_site.py --host 0.0.0.0 --port 8000`
and open the served address. This allowlisted server publishes documentation and
research notes, but not local caches or `.git`. The browser shows only a dated leaderboard
snapshot. GitHub Pages is configured to attempt a scheduled public-source refresh;
a failed refresh is explicitly stale/unavailable, never a live score. The current
repository Pages setting uses legacy main-root builds, and changing it to Actions
was denied by the GitHub integration (HTTP 403). The Actions artifact therefore
mirrors the same root-to-`docs/` layout; either deployment serves stable paths.
A legacy rebuild can temporarily restore the committed older snapshot. This
monitor cannot access team quotas, private labels or submission receipts.

## Official starting points

[Problem and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) ·
[Official rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf) ·
[Data (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) ·
[Public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) ·
[Reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) ·
[USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) ·
[INGENIOUS / GDR](https://gdr.openei.org/submissions/1391).


## Earlier repository work retained

A concurrent `main` update added nine local per-site scorecards,
[`knowledge/project-brief.md`](knowledge/project-brief.md),
[`knowledge/review.md`](knowledge/review.md), upstream text snapshots under
`evidence/`, and [`scripts/readiness.py`](scripts/readiness.py). These remain in
the repository. Its earlier dashboard and run card are preserved as dated
snapshots; cache and automation statements in them are historical. The
readiness module checks evidence structure only; it is not an evaluator, a
raster validator, or a slot authorization. The current audit and H1 run card take
precedence where earlier snapshots are stale.


## Preserved parallel H1 research

The independently merged H1 runner, evidence and quarantined research TIFF/ZIP
are retained. See [`evidence/run_card.json`](evidence/run_card.json),
[`evidence/review.md`](evidence/review.md), and
[`knowledge/parallel-run-README.md`](knowledge/parallel-run-README.md). The
project's H1 report is generated as `docs/experiment-index.html` so rebuilding
it cannot overwrite the current research desk. Recheck its saved bytes with
`python scripts/audit_parallel_surface.py` after restoring audit inputs. Do not
rerun or tune H1 after its duplicate stop, or run any new experiment before
resolving the assigned lane, full registry, comparable incumbent and budget.
The audit-session card at `docs/data/run-card.json` is scoped to the follow-on
review; H1's actual experiment card is `evidence/run_card.json`.
The parallel session's inherited registry-fetch helper has a local integrity
fix not landed upstream; it must not be represented as a shared-template fix.
See `vendor/NOTICE.md` and resolve that upstream before relying on it in a new
experiment. The evaluator and writer themselves remain unchanged.


## Additional independent geometry audit

A separate follow-up measured the nine all-finite historical TIFF variants and
all 72 directional overlaps, restored eight pinned GEMSDOE24 shared tools without
modifying them, and rechecked the H1 surface's saved bytes. It ran no further
geological experiments and did not replay H1's holdout. Its
[linked dashboard](docs/audit.html), [audit data](docs/data/reference-audit.json),
[negative audit-scoped run card](docs/data/audit-run-card.json),
[forensic review](research/independent-review.md),
[hypotheses](research/independent-hypotheses.md),
[source register](research/independent-sources.md), and
[three-pass record](research/independent-three-pass-review.md) are retained
alongside the main research desk and H1 evidence. Different owner variants may
have different byte hashes even when their decoded positive masks match.

To reproduce this second audit without the large feature stack:

```sh
python scripts/bootstrap_research.py
python scripts/audit_references.py --output /tmp/gems-audit.json
python scripts/compare_audit.py docs/data/reference-audit.json /tmp/gems-audit.json
python scripts/check_submission.py docs/downloads/gemsdoekarage2-h1-parity-1ab65e3fb345-DO-NOT-SUBMIT-surface.tif
python scripts/build_audit_site.py --check
npm test
npm run test:browser
```

`python scripts/fetch_feature_mirror.sh` separately restores the optional
~419 MB owner-mirrored feature file and verifies its SHA-256. The owner sample
disagrees with the organizer's description, and the equivalence between the
mirror's band-15 basement label and the organizer's conductive-base-depth
feature is unknown. Neither mirror-based validator is an organizer receipt.

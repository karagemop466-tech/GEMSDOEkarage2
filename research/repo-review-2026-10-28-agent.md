# Repository review — 2026-10-28

## Executive decision

**NO APPROVED SUBMISSION. Do not upload any TIFF currently in this repository.**
No experiment or raster generation was performed during this review, and no
competition slot was used. The previously displayed HK3 “OK TO SUBMIT: YES”
status contradicted the binding literal uniqueness stop. I corrected the release
classification to **negative / research-only**, removed any submission-approved
download action, and made the saved-download inventory report
`PASS_RESEARCH_ONLY` with no approved candidate. The current Pages retain links
only for reproducible research, explicitly labeled **DO NOT SUBMIT**.

This is not a claim that no unique raster could ever be created. It means the
existing evidence cannot authorize one: the specified coordinator-assigned
method paragraph is absent, the historical HK3 lane already used three
experiments and reports about 2 h 15 min, its final dots fail a literal registry
threshold, the registry scan is incomplete, and the competition inputs/template
are owner mirrors rather than organizer-authenticated bytes. The next authorized
lane must first resolve those prerequisites. This review deliberately did not
invent a replacement lane or exceed the experiment budget.

## Highest-scoring focus-site claim and scientific interpretation

The supplied 0.2778 for GEMSDOE32's `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`
is **USER-REPORTED / UNVERIFIED** in this repository: no file-bound organizer
receipt was found. Pinned mirror forensics report that its dot mask is a pruned
variant of the D2.8 family, but that is a byte-level relationship, not a causal
explanation of a hidden-set score. Reducing redundant predictions can plausibly
help a distance-tolerant metric, especially near mapped pixels excluded from
scoring, but the available data do not prove that this caused 0.2778 or that the
removed dots had zero private-set credit.

No leaderboard estimate is defensible here. Earlier pages used the simplified
identity `T / (0.2T + 0.2F + 0.8G)` to infer hidden truth and transfer a score.
The official distance-weighted Tversky calculation uses distinct kernel-weighted
sums over truth and prediction pixels; the simplified identity is not generally
valid. The old numbers are retained only as historical arithmetic, not as a
score or calibrated estimate. See [`independent-review.md`](independent-review.md)
and the archived [`champion_forensics.json`](../evidence/champion_forensics.json).

The previously saved HK3 comparison remains a historical **HOLDOUT-DTI** result:
candidate 0.1845 [0.1677, 0.2015] versus refitted incumbent 0.1575 [0.1417,
0.1737], paired difference +0.0270 [+0.0206, +0.0337], evaluator
`gems57-pooled-hide-v2`, 58,258 withheld positives. It is a public-catalogue
hide-and-recover result, not a leaderboard score and not an upload authorization.

## Ranked geological research slate — proposals only

The existing [`2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md)
contains the requested four ranked hypotheses; their ranks are qualitative priors,
not measured DTI gains. They are not permission to experiment, and these owner-mirror
bands are not organizer-authenticated. Each proposal still needs the assigned-lane
and complete-registry gates before any holdout run.

| Rank | Hypothesis and layers/signature | Mechanism / non-fault confounder | Novelty, likely value, and cost |
|---|---|---|---|
| 1 | **Topography-conditioned residual gravity step** — bands 13, 11, 12, 19; block-fitted, label-blind terrain residual then sign-persistent oriented gravity edges. | Density offset may persist under alluvial cover beyond mapped scarps. Confounder: unfaulted sediment–bedrock contact or lake-terrace riser. | Distinct from H1's opposing gradients and K2's raw/magnitude bands; proposal says medium cost and highest relative potential. B4 shares the broad topo/gravity family, so lane collision and novelty need explicit review. |
| 2 | **Conductivity saddle across independent gravity break** — bands 17, 13, 18; conductivity-Hessian sign change across a potential-field edge. | Could indicate juxtaposed conductive strata across a covered fault. Confounder: saline groundwater/playa margin or inversion seam. | Different interaction from K2's raw conductivity and gradient magnitudes; medium/high cost, second relative potential. Exclude ambiguous band 15 until metadata is verified. |
| 3 | **Strain-regime change as coarse prior** — bands 7, 8, 2, 3; interact strain change with persistent magnetic edge and use shuffled-strain control. | A covered strand might coincide with a tectonic regime boundary. Confounder: geodetic interpolation seam or intrusive contact. | Repo has not run this exact interaction, but strain is already proposed in its research backlog and is coarse at 100 m; medium cost, lower relative potential. |
| 4 | **Seismicity-sidedness falsification** — bands 10, 16, 11; compare seismicity on flanks of a gravity residual edge. | Earthquake clustering could provide context for an unmapped active fault, not 100 m localization. Confounder: induced/mining seismicity or smoothing artifacts. | Exact local test not implemented, but related ideas exist upstream; low cost and low expected benefit. Band units/descriptions need authoritative metadata. |

No new external dataset is required by these four proposals; they use bands in a
pinned GitHub owner mirror only. The slate explicitly says that mirror does not
authenticate current DrivenData inputs and lacks units. Thus neither verified
availability of official layers nor a measured holdout ranking can be claimed.
The rational next scientific candidate *if* the gates clear is rank 1, but only
as a preregistered hypothesis; no submission is selected or promoted.

## Critical findings and fixes

### 1. Release gate overrode its own binding uniqueness rule — critical

`evidence/hk3/run_card.json` recorded `unique_literal_vs_all_registry_rasters=false`
and `literal_rule_exception_applied=true`, while marking the overall verdict
`PROMOTE`. Its registry audit reports 450 checked rasters, one error, and an
incomplete accessible scan. The three recorded final-dot overlaps were 71.0%,
73.3%, and 74.9%, each above the literal 70% stop. The historic selector then
called the artifact approved because the failures were considered non-submission
objects. That exception is incompatible with the prompt's “any registry raster”
stop rule.

**Fix:** changed the run card's current verdict to `negative`, preserved the
historic verdict and exception as explicit provenance, added a dated protocol
review override, and changed `selector_result.json` to `ok_to_submit: false`.
No raster bytes or historical holdout measurements were changed.

### 2. Site generator and published-download audit treated the exception as approval — critical

The four generated pages derived their green “OK TO SUBMIT” badge from the
`PROMOTE` string alone. The public artifact audit also excluded the literal
all-registry failure and exception flag from its hard-gate check, then certified
the selector receipt. Tests explicitly asserted the unsafe behavior.

**Fix:** `scripts/build_hk3_pages.py` now computes a fail-closed release decision
that requires literal uniqueness, no exception, an assigned method paragraph,
a complete error-free registry scan, authenticated inputs, and explicit
within-budget evidence. The current run fails these checks. The homepage,
executive summary, submission guide, and submit page show **OK TO SUBMIT: NO**;
the only HK3 file controls are explicitly labeled for research and **DO NOT
SUBMIT**. `scripts/audit_public_downloads.py` classifies every present TIFF as
research-only and returns no approved submission. Tests require that exact
research-only boundary and verify a matching selector cannot override missing
protocol evidence.

### 3. Numerical score explanation was overstated — high

Earlier generated copy described the simplified Tversky identity as exact and
used it to infer hidden truth size, dot hit counts, and a leaderboard score
range. This contradicted the independent metric review already in the repository.

**Fix:** public copy now says a leaderboard estimate is unavailable, distinguishes
holdout metrics from organizer scores, and describes the 0.2778 mechanism only
as a plausible hypothesis. The old calibration artifacts remain available for
audit but are no longer displayed as an estimate or used for release decisions.

### 4. Submission-format guidance implied unverified portal acceptance — high

Local float32/range/grid checks do not establish that a TIFF passed DrivenData's
live validator. The actual rejected upload and receipt are unavailable, and the
owner-mirror template/exterior convention is not authenticated.

**Fix:** submission guidance reports local diagnostics only and explicitly says
the earlier range error's cause and portal acceptance remain unresolved. It no
longer says the current artifact “will not trigger” the error.

### 5. Starting instructions and README contained stale approvals — high

`README.md` and `AGENTS.md` still instructed future work to download/submit HK3,
calibrate a projected score from an organizer receipt, and treat it as the best
submittable file. Those instructions conflicted with the binding protocol and
with the underlying gate receipts.

**Fix:** both now begin from the current no-approval state, preserve the old
measurements as historical research, list release blockers and require a new
assigned lane and budget before experimentation. Generated HTML remains
source-controlled through its generator; generated pages were rebuilt.

## Three-pass review record

### Pass 1 — inspect and verify

Read `AGENTS.md`, `README.md`, the HK3 and K3 cards, the independent metric
review, the page generator, public-download audit, CI definitions, and tests.
Installed the pinned Python dependencies and Node dependencies. Baseline before
changes: 201 Python tests passed, 7 skipped, and the feed tests passed; site
suite also encoded the unsafe green status. This establishes the bug was in the
release policy, not the raster format checks.

### Pass 2 — fix release safety and contradictory claims

Added a strict release decision, removed download actions for the failed
candidate, corrected selector and run-card verdicts while retaining historic
provenance, reclassified all files as research-only in the integrity inventory,
corrected the explanation/estimate language, updated README and AGENTS, and
revised tests to assert no unapproved file is offered.

### Pass 3 — regression and completeness

Rebuilt generated pages and the saved-byte audit. A first test pass after the
changes identified three remaining issues: legacy negative-evidence links were
missing from the how-to page; a generated review link did not yet have its
report file; and old tests expected a K3 “holdout-best” label or a download
button. The how-to page includes the quarantined evidence table. Tests now require
research downloads to be explicitly labeled DO NOT SUBMIT, forbid approved
submission downloads, and describe K3's highest recorded HOLDOUT-DTI as historical
rather than as a submission candidate. The review file is now present and linked from `SUBMISSION_STATUS.md`. The full
Python, Node, site, browser, generated-page, public-download, and whitespace
checks are rerun against the latest main-branch integration below.

## Remaining blockers / next session

1. Obtain the coordinator-assigned single-method paragraph. Do not infer it from
   the long prompt or declare a new lane locally.
2. Resolve the complete registry scope and inventory error, refresh pinned
   source refs, and retain the strict literal 70% / Spearman 0.90 checks before
   placement and on final dots.
3. Obtain organizer-authenticated competition inputs and template, and clarify
   the exterior NoData/range-validation contract with official evidence.
4. If and only if the first three items clear, preregister genuinely new
   geological hypotheses and run no more than three experiments or two hours,
   using the shared evaluator/writer and feature-only leakage canaries.
5. Keep leaderboard estimates unavailable until a defensible transfer procedure
   is validated against file-bound organizer receipts. Only a separate selector
   may consider a slot; actual quota and portal validation are account-side.

## Final verification

- `.venv/bin/python -m pytest -q`: **215 passed, 7 skipped**, 98 subtests; Rasterio emitted 87 pending-deprecation warnings.
- `npm test`: **3 passed**.
- `npm run test:site`: **7 passed**.
- `npm run test:browser`: passed at 1440, 390, and 320 px, including explicitly research-only download controls, navigation, and freshness fail-safe states.
- `scripts/build_hk3_pages.py --check`: pages up to date.
- `scripts/audit_public_downloads.py --check`: **PASS_RESEARCH_ONLY**, seven artifacts, no approved downloadable submission.
- `python -m compileall -q scripts vendor`, JavaScript syntax checks, and `git diff --check`: passed.

These are local software and saved-byte checks. They do not authenticate inputs,
verify current DrivenData scores, or establish portal acceptance.

## Official links for manual review

Links below identify the competition/reference context; this review did not
freshly retrieve the DrivenData pages or authenticate any account receipt.

- [DrivenData competition](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem and metric page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official data tab — login required](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE GDR submission 1391](https://gdr.openei.org/submissions/1391)
- [Competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

# GEMS discovery lab · GEMSDOEkarage2

**Start every session by reading this README, `AGENTS.md`, `knowledge/hypotheses.md`, and the current run card.**

## Executive decision — 2026-10-27

**NO APPROVED COMPETITION SUBMISSION.** One new physical hypothesis was implemented and tested, then stopped at the pre-placement registry gate. A newly calculated, format-valid research GeoTIFF is downloadable, but **it is not uniqueness-cleared, is not a high-scoring submission, and must not be submitted**. Renaming, jittering, or re-encoding a previous file is not an improvement.

- [Executive summary and downloads](https://karagemop466-tech.github.io/GEMSDOEkarage2/)
- [Nine focus-site evidence](evidence/nine_site_best_files_audit.json)
- [Run card](evidence/run_card.json) · [holdout details](evidence/holdout.json) · [validator](evidence/validator.json)
- [Hypotheses and preregistration](knowledge/hypotheses.md) · [official and community source audit](evidence/sources.json)

**HOLDOUT-DTI** `gems57-pooled-hide-v2`: **0.03367**, spatial-cluster bootstrap 95% CI **[0.02867, 0.03929]**, **58,259 withheld positive pixels**. This is not a leaderboard estimate. The paired difference against the best primitive control was negative. The generated surface has directional 3 px overlap **1.0** with a registered lattice; the literal >70% stop applies. No final dots were placed, and no competition slot was used.

## Standing project prompt (deduplicated working requirements)

The user's long request repeats the same objectives and historical submission list. The following preserves the actionable requirements in this README rather than repeating the duplicate passages. It is **not represented as a verbatim transcript**.

1. Review the repository and previous next steps first. Focus on the highest reported submissions from **GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36**. Publish an executive summary for each, identifying the exact file, estimate availability, and uniqueness status. Explain the reported GEMSDOE32 champion and investigate genuinely distinct geological mechanisms.
2. Generate a **genuinely unique single-band submission GeoTIFF**, not a copied/renamed/jittered prior. Make download and submit eligibility obvious at the top of the site. Validate automatically; do not rely on a human inspector. Check finite predictions inside the footprint, all values in [0,1], exact CRS/shape/geotransform, known-trace masking, and a ZIP containing exactly one TIFF. Use a distinctive name and a note at most 140 characters. Local format validity does not imply high performance, uniqueness, portal acceptance, or slot approval.
3. **Parallel-run protocol takes precedence over endless iteration:** stay in a declared lane; stop at >0.90 raster rank correlation or >70% directional dot proximity within 3 px. Check surface before placement and final dots if placement is allowed. Do not invent an exemption for dense priors. Reuse shared cache/evaluator/writer. Withhold whole segments/components with a spatial buffer; derive catalogue-based predictors only from visible traces; mask visible traces pixel-exactly; pool DTI components using alpha 0.2, beta 0.8 and a 300 m triangular kernel. AUC >0.90 for an individual feature is a leakage canary until explained. End with one JSON run card containing hypothesis, mechanism, named non-fault confounder, HOLDOUT-DTI + CI + evaluator + positives, registry checks, raster hash, validator, name/note and promote/negative verdict. Negative results are deliverables. Stop after three experiments or two hours; promotion to a real slot is a separate selector step within the verified weekly cap. No competition submission without beating a comparable current holdout best.
4. Before implementing, propose 3–5 ranked geological hypotheses naming layers, transform, missing-fault rationale, novelty relative to existing code, physical confounders, expected utility and cost. Check availability of any new free official data before calling a hypothesis viable. Study geological fault discovery relevant to geothermal systems; do not conflate structural predictions with verified vents/resources.
5. Never invent data, source verification, score estimates, uncertainty intervals or organizer receipts. Every measured model result must be **HOLDOUT-DTI** with evaluator version, withheld positives and CI, or **ORGANIZER-CONFIRMED** with a submission-page receipt. Supplied historical values without receipts remain clearly segregated **unverified user reports**, not confirmed results or calibration targets. A projection is never a measured score. The request contains competing leaderboard claims (0.3195 and 0.4413); neither is current-verified here.
6. Build a clean, accessible GitHub Pages site with a prominent eligibility decision, downloadable candidate when one passes, audit evidence, individual focus-site summaries, submission instructions, provenance tables, irregularities and explicit limitations. Include a freshness signal; a GitHub commit feed is not a live leaderboard feed. Work autonomously within actual access, without asking for passwords or fabricating approvals.
7. Complete three passes: implementation and tests; bug/assumption/edge-case review and fixes; original-requirement audit and final verification. Open and merge a pull request to main. Record unfinished work and concrete blockers for the next session.
8. **Maximize P(Win)** and **Own the Outcome**, as requested: prioritize honest scientific evidence, robust tests and scarce-slot protection over attractive but unsupported claims. Own failures end to end; negative results and limitations are useful outcomes.

### Competition and scientific sources supplied in the prompt

- [Competition](https://www.drivendata.org/competitions/306/competition-doe-gems/) · [problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [resources](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/) · [data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) · [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) (retrieved and pinned)
- [GeoDAWN / USGS](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [INGENIOUS](https://gbcge.org/current-projects/ingenious/) · [GDR](https://gdr.openei.org/submissions/1391) · [competition PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) · [EPSG:32611](https://epsg.io/32611)
- [GEMSDOE32 source site](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html); all nine original source-page links and immutable GitHub revisions are in the site summaries and `evidence/sources.json`.

Direct access to DrivenData, USGS, GDR, NLR, Dropbox and other non-GitHub hosts is unavailable in this sandbox. Links are for review, not a claim those pages were retrieved. Competition data were restored from **community mirrors** with hashes, not downloaded from an authenticated organizer account. The labels mirror is byte-identical to the existing-fault catalogue: it is not hidden competition truth. The mirrored sample carries known-fault ones, so only its grid and finite footprint are used, never its values as a predictor.

## Reproduce

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.lock.txt
python scripts/restore_data.py --manifest registry/core_data_manifest.json --target-dir .cache/gems_data
python scripts/fetch_focus_registry.py --jobs 6
.venv/bin/python scripts/audit_sources.py
.venv/bin/python scripts/audit_nine_site_best.py
.venv/bin/python scripts/run_experiment.py
.venv/bin/python scripts/build_site.py
.venv/bin/pytest -q
```

`gh` must already be connected to GitHub; never paste credentials. Large inputs and caches stay ignored. Downloads and their evidence are committed because they are requested deliverables. `requirements.lock.txt` records the tested environment. To reproduce the exact original registry snapshot rather than refresh live refs, use `python scripts/restore_registry_snapshot.py` with the committed manifest. The experiment writes deterministic names and refuses to overwrite existing outputs; archive/remove the generated outputs deliberately before rerunning. Do not count a rerun as new independent evidence.

To preview: `python -m http.server 8000 --bind 0.0.0.0 --directory docs`. Pages was already enabled on `main` at the repository root. A concurrent session also supplied a working Tests and Pages workflow; it is preserved, with dependency installation and the combined tests. The root redirect supports legacy publishing, and the workflow publishes `docs/`. This integration could not change Pages settings directly (HTTP 403); no successful settings update is claimed.

## What this audit established

- Original checkout: a one-line README only. The claimed pre-existing full train/inference pipeline and cached feature stack were absent. No previous sessions' next-step files existed.
- Four mirrored core files were restored and integrity-checked; **data placement is no longer the immediate blocker**. A GPU is not necessary for this physical experiment or for correctness tests.
- Nine source repositories and 440 filtered registry rasters were retrieved at pinned refs. This is **not** an exhaustive inventory of every site in the enormous historical list; exclusions and inaccessible/private history prevent global uniqueness certification.
- GEMSDOE25 and GEMSDOE30 have identical decoded dots. GEMSDOE32 equals D2.8 minus all dots within 200 m of known traces. GEMSDOE36 contains that whole B2 set plus 1,200 dots. These are tightly related emissions, not nine independent discoveries. See pixel-level evidence, not score-driven speculation.
- The shared evaluator/writer were vendored unchanged with per-file hashes and upstream links. The unavailable upstream `.cache` was not privately reconstructed. The registry fetcher's same-size cache bug was fixed locally and recorded; no upstream write access exists.
- Access to the nine other repositories is **READ**. This repository publishes nine per-site executive summaries; their original deployed sites were not modified.

## Next-session priorities and release blockers

1. Resolve the missing assigned lane and the registry protocol's near-universal lattice-overlap conflict without silently relaxing thresholds. The blocking lattice covers 99.8724% of allowed footprint cells within 3 px; this is a measured coverage fraction, **not** a universal-blocker proof or a model score.
2. Obtain organizer-authenticated input hashes/units, rules PDF, current weekly cap, current leaderboard and submission receipts through an allowed source. No secrets in chat. Do not infer these from community mirrors.
3. Rebuild the incumbent method from visible-only inputs on exactly the same folds. A precomputed submitted mask is an invalid comparator when it has already removed withheld catalogue pixels. The current primitive control is not the historical champion.
4. Expand immutable registry coverage to all named repositories and confirm format/shape/CRS. Do not claim global scientific uniqueness from a fresh file hash or a nine-repository snapshot.
5. Only after the stop condition is resolved may another preregistered lane experiment run. H1 failed performance and novelty gates; do not tune it to the same holdout or spend a slot. Deferred hypotheses are ideas, not results.
6. Promote only a positive, independently checked candidate to a separate quota-aware selector. This session neither submitted to DrivenData nor promised a prize/rank.

## Concurrent-session integration

While this session was running, other Arena branches merged a static dashboard, official-source observations and a fail-closed evidence-schema gate into main. These were not in this session's starting checkout. Their source snapshots, `scripts/readiness.py` and tests are preserved. Earlier pages are clearly archived under `docs/previous-main/`; old site-summary routes redirect to the current summaries. The earlier README is preserved in `knowledge/previous-main-README.md`. An adapter connects our real evaluator/writer/registry receipts to their readiness gate; it returns negative.

The prior session records a public leaderboard observation of 0.4544 on 2026-10-27. That is a prior-session observation, not independently retrieved by this session and not an organizer submission receipt, current verified feed or forecast. See `knowledge/review.md` for its provenance claim. It does not change this run's negative result or justify a slot.

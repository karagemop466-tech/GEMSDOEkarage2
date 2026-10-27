# Three-pass review — 2026-10-27

## Pass 1 — inventory, implementation and experiment

- Verified the starting tree: only a one-line README, no scientific implementation or previous-session next steps. The prompt's asserted complete pipeline/cache did not exist here.
- Retrieved the official DrivenData reference notebook via GitHub at a pinned revision and explicitly limited the verified claims. It is not the official hidden scorer or a source of current leaderboard receipts.
- Restored four hash-pinned mirrored core files, including the 19-band feature raster. Community provenance is explicitly weaker than organizer authentication. Labels equal the existing-fault catalogue; the sample's values are not used as predictors.
- Retrieved nine community source pages and 440 filtered historical registry rasters. Recorded immutable refs, file SHA-256 and READ-only permissions for all nine remote sites.
- Wrote four hypotheses before implementing H1. Recorded the absent assigned-method paragraph and unavailable derived cache; used selected cached source bands without privately rebuilding the upstream 35-channel feature stack.
- Used the unchanged shared spatial folds, pooled evaluator, metric, validator, writer and uniqueness tools. H1 uses no catalogue-derived predictors. Calibration percentiles are computed in the fold's buffered training region. Whole catalogue components are hidden; evaluation regions are label-blind fixed quadrants.
- Tested each primitive alone on holdout (AUC and DTI). Canary passes are not leakage guarantees. Candidate and controls share the same folds and truth counts. Primitive best-control selection is exploratory; no compatible incumbent reconstruction exists. No promotion inference is made from that selection.
- H1 was negative: HOLDOUT-DTI `gems57-pooled-hide-v2`, 58,259 withheld positive pixels, 95% spatial bootstrap interval in the run card. It underperformed the primitive controls.
- Generated a new continuous physical surface via the shared fail-closed writer, with a distinctive name and note. This is a **pre-placement research artifact**, not a final dotted submission.
- Mandatory registry stop at record 59 of 440: overlap 1.0 with a registered lattice. The scan stopped on sufficient negative evidence; no incomplete scan was used to clear uniqueness. No final dots were placed. No later lane experiments or competition slots were used.

## Pass 2 — bugs, assumptions and edge cases

### Fixed

- The inherited registry fetcher trusted equal-size cached files. The one local template copy now verifies Git blob hashes and rejects truncated trees. Unit tests cover equal-size corruption, failed re-download integrity, and truncated inventories. Initial fetch used an empty cache, so no stale-size reuse affected the run. Upstream repos are read-only; this fix is not claimed to have landed there.
- The inherited nine-site audit emitted non-standard JSON `NaN` for nodata. It now writes strict JSON with a separate printable nodata representation; browser evidence parsing works.
- The historical audit now fails closed on shape/CRS/affine/band mismatch. It explicitly records NaN/infinity counts, and does not confuse infinity with outside-footprint NaN.
- Normalized the historical correlation gate to positive Spearman >0.90 rather than absolute correlation. All measured historical relevant pairs were positive, so this did not alter scientific outcomes.
- Fixed a runner path mismatch between public artifact paths and registry-cache paths.
- Added input SHA-256 guards and a hard two-hour alarm to the runner, without rerunning or tuning H1 after its stop.
- Fixed long hashes/filenames overflowing small-screen source and per-site pages, discovered with a real headless Chromium run.
- Added explicit `download` attributes to local TIF/ZIP links and verified served bytes against the recorded SHA-256.

### Verified / retained limits

- Format-valid does not mean scientifically unique, high-scoring, organizer-accepted or promoted. The site does not claim a high-scoring ready file.
- Historical values remain unverified user reports, not ORGANIZER-CONFIRMED or HOLDOUT-DTI values. No leaderboard projection is invented.
- A lattice covering 99.8724% of allowed cells is **not** a universal-blocker proof; 6,514 allowed pixels remain uncovered. The actual candidate overlap is 1.0. The wording and certificate preserve that distinction.
- Paired 20 km spatial-cluster intervals are conditional on catalogue, folds and methods. They are not leaderboard uncertainty intervals; known catalogue faults may be missing-not-at-random relative to hidden faults.
- Range/nodata policy is conservative. The previous portal error's cause is not established from its text alone. Writer rejects NaN, infinity, out-of-range values and finite nodata sentinels rather than silently repairing them.
- The unchanged shared tools contain optional alternative diagnostic functions. The runner uses the literal gate only; no dense-prior exemption or private threshold is used.
- One non-failing third-party rasterio/affine deprecation warning remains in format tests; it does not indicate an artifact or validator failure.

## Pass 3 — original-request audit

| Requirement | Outcome |
|---|---|
| Review repo / previous next steps | Done; no previous implementation existed. |
| Executive summaries for all nine focus sites | Done as nine subpages in this repo; original sites are read-only and were not modified. |
| Exact filename / estimated score / uniqueness table | Done; unsupported estimates explicitly say “Not estimable.” Historical claims are segregated. |
| Explain reported historical best | Done using independently re-read pixel relationships and an exact pruning inequality; hidden-test causal improvement remains unproven. |
| Propose 3–5 hypotheses before coding | Four preregistered; one lane tested. Unrun ideas are not results. |
| Shared tools / cached input reuse | Shared code unchanged and hash-documented; derived upstream cache unavailable, restored source feature stack reused instead. |
| Leakage canaries and buffered whole-segment recovery | Implemented with whole connected components, fixed quadrants and training buffer; all primitives tested. |
| Unique high-scoring ready-to-submit TIF | **Not achieved.** New research TIF generated and format-validated, but failed performance and uniqueness gates. Stop rule honored instead of false approval. |
| Final dot uniqueness check | Not applicable: placement forbidden by surface stop. No final-dot clearance claimed. |
| Automatic validation without human inspector | Implemented; failed gates yield an automatic negative, not a manual-approval queue. |
| Easy download + name + <=140-character note | Done for quarantined research TIF and one-TIF ZIP. No approved submission download is offered. |
| Submission instructions subpage | Done, including range errors and quota-aware selector separation. |
| No slot use without beating holdout best | Done; no slots used. No compatible historical best exists on these folds, and candidate loses to controls. |
| Current verified leaderboard / weekly quota / official input identity | Unavailable under actual host/access constraints; explicitly unverified, no invented values. |
| Up-to-date feed | Read-only public GitHub commit freshness check; explicitly not a leaderboard feed or automatic clearance. |
| Standing prompt in README | Actionable deduplicated contract stored, clearly labeled not a verbatim transcript; AGENTS requires reading it each session. |
| Store verified knowledge and source links | Done with immutable GitHub references, source hashes and explicit official-source retrieval limits. |
| Three passes | This document records all three, with concrete fixes and final tests. |
| Open/merge PR and publish Pages | Evidence-check workflow supplied. Pages settings update was denied (HTTP 403 integration permission); existing legacy main/root hosting is preserved via root redirect. PR and build outcomes are reported separately after GitHub confirms them. |

## Final verification

- **35 Python tests passed** locally, including metric-vs-brute-force arithmetic, exact pruning condition, inclusive 3 px distance, whole-component leakage guards, pooled truth-count compatibility, bad-value writer rejection, ZIP roundtrip, actual grid/range/footprint/catalogue, source checksums, evidence schema, all static links and nine summaries.
- All **440 pinned registry files** re-verified by SHA-256 from the committed snapshot manifest.
- JavaScript syntax and Python compilation passed.
- Real Chromium checks: homepage at **1440, 390 and 320 px**, submission guide/research/sources and **all nine** per-site pages at mobile width; no horizontal page overflow and no uncaught page errors. Approved download control disabled. Research TIF fetched with HTTP 200 and a matching SHA-256. Details: `browser_checks.json`.
- No model retraining, parameter tuning, or dot placement after the registry stop. Rebuilding HTML, improving validators, running correctness tests and auditing historical masks are not additional geological experiments.

## Carry forward

Read README next session. Resolve lane/registry policy, authenticate organizer evidence, reconstruct a compatible incumbent, and expand registry scope **before** another experiment. Do not resubmit the research surface or any historical mask from this release. The goal of an eligible unique high-scoring TIF remains open.

### Publishing permission finding

GitHub reports Pages already enabled at `https://karagemop466-tech.github.io/GEMSDOEkarage2/`, sourced from main at `/`. Attempting to change build type to workflow returned `403 Resource not accessible by integration`; no successful setting change is claimed. Removed the custom deploy workflow to avoid knowingly shipping a failing job. The legacy Pages build can serve the root redirect and the docs directory after merge. Read/write Git operations are tested separately; a Pages-settings scope error is not evidence of broken Git authentication.

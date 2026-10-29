# Repository review — Arena session 2026-10-29

**Scope:** read-only code/site review and test execution on `arena/77648149-gemsdoekarage2`. No model experiment, TIFF generation, submission upload, or slot use. No source implementation was changed.

## Pass 1 — establish intent and run checks

Read `README.md` first as instructed. It contains the consolidated project prompt, binding parallel-run rules, source/status notes, and explicitly says no file is approved. Read `SUBMISSION_STATUS.md`, the existing 2026-10-29 blocker review, executive summary, hypothesis slate, and historical session card.

- Existing hypothesis preregistration: [`2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md) offers four ranked candidates with named layers, physical signatures, catalogue-miss rationale, repo-difference, mimics/controls, and availability qualifications. It explicitly is **not an assigned lane**. Candidate #1 overlaps the B4 topography/gravity family and cannot safely be treated as cleared.
- Existing release decision: **negative**. No eligible TIFF. The user-reported GEMSDOE32 0.2778 is not an organizer receipt. The purported score mechanism is conditional inference, not established causation.
- Executed `npm test`: **3/3 passed**.
- Executed `npm run test:site`: **7/7 passed** after installing locked npm dependencies.
- Executed `python scripts/build_hk3_pages.py --check`: **pages up to date**.
- Executed `npm run test:browser`: passed at 1440/390/320 px; checked visible negative/research-only labels, exact download hash, nine rows, no horizontal overflow, and fail-safe freshness states.
- Executed `.venv/bin/pytest -q` with `requirements.lock.txt`: **226 passed, 8 skipped, 98 subtests passed**. The skips reflect gated/unavailable inputs; this run does not turn mirrored data into organizer-authenticated data.
- An initial system-Python pytest attempt failed because pytest was absent; installing into a project virtual environment worked. `npm run test:site` initially failed because `jsdom` was absent; `npm ci` resolved the environment prerequisite. Neither is a code defect.

## Pass 2 — defect/assumption review

1. **No TIFF can responsibly be approved.** Existing files fail at least one mandatory criterion (including registry uniqueness and/or exterior-format gate). The blocker review enumerates files and evidence. Do not provide the download link as an endorsed competition artifact.
2. **No scientifically valid score estimate.** Historical GEMSDOE scores supplied by the user remain user-reported/unverified. HOLDOUT-DTI proxy scores are not transferable leaderboard projections. Do not label either as organizer-confirmed.
3. **Registry scope / lane unresolved.** The prompt's cited one-paragraph method is not actually supplied as an assigned lane; the full parallel registry cannot be certified from the partial/owner-mirrored collection. The prior strict uniqueness stop is binding. Do not try to place dots into lattice gaps or revive a retired method.
4. **Data authenticity unresolved.** Owner mirrors are hash-pinned, but not authenticated competition inputs. A template copy and passing local tests do not prove portal acceptance. The reported `[0,1]` upload error remains unexplained.
5. **Historic run-card branch mismatch.** `evidence/session-2026-10-29-run-card.json` names `arena/cf005210-gemsdoekarage2`, while this checkout is `arena/77648149-gemsdoekarage2`. Treat that card as an earlier session artifact, not evidence for the current branch. This review names the current branch explicitly.
6. **Generated page discipline:** the executive summary is generated; edits should go through its generator/evidence rather than manually patching HTML. The current generated-page check passes.
7. **PR/merge not performed.** This review makes no code change to propose; no PR was opened and no merge attempted. Any future code changes must stay on the Arena-assigned branch and use the explicit PR workflow.

## Pass 3 — against the original request

The repo already provides a nine-site executive-summary table, downloadable *research-only* historical artifacts, submission instructions, official-source links, hypothesis slate, writer/validator utilities, and fail-closed negative release records. It does **not** meet the user's desired outcome of an approved, demonstrably unique, high-performing TIF: the protocol's preconditions and mandatory gates are unmet. The correct outcome is to leave submission disabled rather than fabricate validation or reuse a previous raster. No weekly slot was spent.

### Next work, in order

1. Resolve the assigned single method lane and reconcile prior-art/B4 overlap; then establish a complete, current registry and pre-placement surface check.
2. Obtain authenticated organizer training features, labels, and the exact sample template through the participant data portal. Keep mirror hashes only as research fixtures.
3. With shared cached features/evaluator/writer, preregister one eligible hypothesis, run leakage canaries and spatially blocked hide-and-recover holdout, and compare to a frozen same-fold baseline with the specified pooled DTI/CI.
4. If and only if holdout beats the incumbent, perform pre-placement and final-dot checks against the complete registry, validate template footprint/exterior/CRS/shape/transform/range, and let the quota-aware selector decide whether a slot is available.
5. Establish portal exterior semantics and explain the previous range error without consuming a slot unless authorized. For a selected final entry, retain exact TIFF hash, submission receipt, source/code/assets, and required generative-AI disclosure.
6. Refresh the live leaderboard and all external site observations when making any later comparison; historical values are not live facts.

### Limitations

This environment did not run an experiment or access organizer-authenticated private data/labels, cannot observe the private leaderboard, and cannot guarantee portal acceptance from local tests. Tests confirm repository behavior on available fixtures, not scientific validity, hidden-score improvement, or a competition submission receipt.

**Verdict: NEGATIVE / no approved file.**

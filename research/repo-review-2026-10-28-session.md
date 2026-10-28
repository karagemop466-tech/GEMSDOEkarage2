# Repository review and next-experiment gate — 2026-10-28

## Executive disposition

**Release verdict: NO APPROVED TIFF — DO NOT SUBMIT.** This review did not generate or alter a submission raster, perform a geological experiment, select a candidate, or use a competition slot. The existing K2 TIFF remains a research artifact with a conditional-to-selector claim in its historical run card; it is not an approved file. Its literal all-registry audit records a lattice witness and a calibration-ridge overlap above the stated limit, while selector/quota/authentication rulings are absent. The K2 label holdout result is not a leaderboard score or a calibrated private-score estimate.

The root README already contains the consolidated project prompt and the binding parallel-run protocol. It was read before this review. The request's “single method paragraph” is not an identifiable method assignment in the supplied prompt/repo instructions; the previous repo review also records this blocker. The repo's fail-closed generator, selector and current release banner therefore remain in force. No experiments were run because the lane is unassigned and the existing literal registry rule stops the K2 candidate. The three-experiment/two-hour cap is not permission to proceed when the lane/registry stop is unresolved.

## Three-pass review

### Pass 1 — inventory and traceability

- Confirmed active branch `arena/6bda880f-gemsdoekarage2`, clean checkout at review start, README and `AGENTS.md` instructions, and the existing negative release assessment (`scripts/assess_release.py`).
- Reviewed the homepage, executive summary, historical site pages, selector input/result, generator, validator, tests, K2 run card, prior review, and preregistration.
- The nine focus-site table labels the reported score snapshots as user-reported/unverified, does not claim a leaderboard transfer estimate, and marks all historical files DO NOT SUBMIT. No organizer receipt for those numbers was identified in this checkout.
- The K2 run card reports HOLDOUT-DTI 0.1581 (95% CI 0.1424–0.1742; `gems57-pooled-hide-v2`; 58,258 withheld positives). This is a prior-run value, not an experiment in this review and not a prediction of the private leaderboard score. The current evidence does not authorize submitting it.
- The documented mirrored core inputs are hash-pinned owner mirrors, explicitly not organizer-authenticated. The competition data page is login-walled according to the repo's source ledger; no authenticated download was possible or claimed here.

### Pass 2 — safety and correctness

Found a presentation risk: the homepage called K2 a conditionally promoted “candidate” and used a primary “Download candidate TIF” CTA. Although the same block said it was not approved, that mixed language could be mistaken for submit approval. Updated the homepage and executive summary so the TIFF/ZIP links explicitly say **research artifact — DO NOT SUBMIT**, and the copy distinguishes the historical run-card conditional selector recommendation from approval. Kept artifacts available for reproducible review; did not rewrite their historical receipts or change raster bytes.

The `scripts/generate_submission.py` entry point already fails closed and does not create output. `scripts/assess_release.py` currently returns negative for the prior H1 evidence. This H1 selector result must not be misrepresented as a formal ruling on K2; the K2 candidate is still pending a separate selector decision and required scope decisions. That distinction is made explicit in the updated UI.

### Pass 3 — verification and edge cases

Ran the locked Python suite: **126 passed, 7 skipped, 33 subtests passed** (38 Rasterio `PendingDeprecationWarning`s). The seven skips are input-dependent tests in this environment; their skipped status is not a pass of organizer-data checks.

Ran `npm test`: **3 passed**; `npm run test:site`: **7 passed**; `npm run test:browser`: passed desktop and mobile checks at 1440, 390 and 320 px, including navigation, no-overflow and fail-safe freshness states.

An initial Python import check failed because dependencies were not installed in the base interpreter. Created the ignored `.venv` and installed the pinned `requirements.lock.txt`; subsequent locked tests passed. `npm ci` completed with 0 reported vulnerabilities. No official DrivenData/USGS/DOE host or competition portal was contacted for this review, and no current leaderboard value, quota, upload acceptance or new external-data availability is asserted.

## Candidate hypotheses for future preregistration (not experiments)

The ranking below is qualitative prioritization, **not a score estimate**. Candidates use layers already named in `scripts/k2.py` (`rtp`, `det_elev`, `iso_grav`, `depth_base`, `cond_surf`, and associated gradients). The owner-mirrored 19-band raster is integrity-pinned in `registry/core_data_manifest.json`, but its organizer provenance and band semantics still require authenticated confirmation. These are prospective mechanisms only; none may be run until the method lane, registry scope, shared-tool revision, and matched incumbent are resolved. “Untried” here means no run is recorded in this checkout's experiment evidence; it does not establish that no other team has attempted the idea.

| Rank | Hypothesis and exact available layers | Physical signature and missing-fault rationale | Main non-fault mimic | Difference from recorded experiments | Expected DTI upside / cost |
|---|---|---|---|---|---|
| 1 | **Cross-physics directional edge agreement** — `rtp`, `iso_grav`, `depth_base`, `cond_surf`, optionally `det_elev`; compute signed x/y derivatives, estimate local edge orientation, and score only persistent, co-oriented edges from independent channels. | A fault can juxtapose magnetic, density, basement-depth and electrical domains; agreement of independently measured edges may prioritize a buried/unmapped structural boundary over a one-channel edge. Every feature must be recomputed from label-blind rasters only. | Intrusive/lithologic contacts, basin margins, survey striping, and unrelated boundaries that coincide spatially. | K2 supplied single-channel raw values, gradient magnitudes and DoG terms to HGB; an unsupervised ridge-coherence primitive was tested. This would explicitly test cross-channel vector-orientation agreement, not merely magnitude or a learned interaction. | **Highest relative priority; moderate, unknown upside.** Medium implementation; low external-data cost (uses existing stack), but requires memory-bounded local derivative/orientation implementation. |
| 2 | **Buried basement-curvature persistence** — `depth_base` with `rtp`/`iso_grav` corroboration; compute multi-scale curvature (Hessian eigenvalue/shape index) and persistence across scales. | Fault-related basement steps may bend or terminate across cover, creating paired curvature ridges/edges where the surface DEM has little relief; multiscale persistence could capture structures absent from the catalogue. | Smooth basin-fill geometry, pluton margins and interpolation artifacts in the depth model. | K2 used a depth-base gradient magnitude but did not record a curvature-persistence feature; distinguish from the already-tested DEM/magnetic gradient terms. | **Moderate relative priority; unknown upside.** Medium implementation and modest compute; no new data if this layer is confirmed in the authenticated stack. |
| 3 | **Signed scarp-step asymmetry with geophysical confirmation** — `det_elev`/`elev_slope` across the local strike, with `rtp` or `depth_base` as an independent gate. | A fault scarp is a directional step; requiring a persistent flank-to-flank elevation contrast plus a compatible subsurface edge may find unmapped surface-breaking faults while rejecting symmetric ridges. | Shorelines, terrace risers, alluvial-fan edges, roads and erosional scarps. | K2 used elevation gradient/DoG, not an explicit signed cross-strike step; however scarp asymmetry was already proposed as B4 in the prior preregistration, so this is **previously proposed but not run**, not a novel repo concept. | **Moderate-to-low relative priority; unknown upside.** Medium implementation. Uses existing named layers. |

### Candidate-selection decision

No candidate was run or validated on holdout. The first candidate is the recommended subject for a *future preregistration only*, not a selection for a competition slot. It cannot responsibly be called “validated” or “highest scoring” yet. Before any run: obtain explicit lane assignment and written registry-scope ruling; restore/authenticate competition inputs and feature metadata; reconcile exterior-value format with the organizer template; reuse the shared feature/evaluator/writer tools; define a frozen same-evaluator baseline; then run per-feature leakage canaries and stop at the first duplicate witness. If the surface passes, evaluate buffered whole-segment hide-and-recover and re-check final dots before any separate selector decision.

No candidate above depends on new external data, so this review does not present a new-data source as obtainable. If an eventual method needs 1 m elevation tiles, use only the organizer-linked 1 m DEM manifest or official USGS 3DEP source after confirming access; no tile list or access was verified in this review. Relevant source links recorded in the project ledger: [DrivenData competition data page (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [DOE/USGS INGENIOUS data submission](https://gdr.openei.org/submissions/1391), and [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution). These links are references for future verification; this review did not re-fetch their contents.

## Irregularities and limitations

1. **No lane assignment found.** A user request to create a file conflicts with the standing no-promotion/parallel-run selector protocol; no instruction can be inferred to override a mandatory duplicate stop.
2. **K2 status is two-part:** historical run card says conditional promote-to-selector; there is no K2 approval receipt. The homepage's general negative selector evidence belongs to H1 and is not silently applied as a K2 ruling.
3. **Uniqueness scope is unresolved.** The K2 audit is positive within a subset of submission rasters but fails the literal all-registry test against calibration artifacts. Do not narrow the scope privately or call the file globally unique.
4. **Scores in the nine-site table are user-reported snapshots**, not receipts; no validated leaderboard-score estimate exists. HOLDOUT-DTI is only catalogue hide-and-recover evidence.
5. **Data provenance and portal acceptance are unverified.** Mirrors are not organizer-authenticated; zero-outside encoding's portal behavior and submission quota require account-side evidence.
6. **Skipped Python tests and warnings:** seven skipped tests leave input-dependent coverage incomplete; pending deprecation warnings are nonfatal but should be cleaned up in the shared code when appropriate.

## Next actions (no slot)

1. Keep the site release lock in place until a separate, evidence-backed selector explicitly decides all gates.
2. Resolve lane assignment and literal registry policy with the parallel-run coordinator; capture the ruling in the repo.
3. Authenticate organizer data/template; verify the official outside-footprint convention and official scorer/evaluator correspondence.
4. Rebuild candidate test features from visible faults only and use the pinned shared holdout evaluator/writer, fixing shared defects upstream rather than forking.
5. Preregister no more than three experiments after gates 1–4 are resolved; never use a hidden leaderboard projection as a score.

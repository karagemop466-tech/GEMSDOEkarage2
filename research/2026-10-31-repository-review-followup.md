# Repository review follow-up — 2026-10-31 (Arena branch)

## Executive result

**No new TIFF was generated and no submission slot was selected or used.** The repo has no competition `data/` inputs and no cached template stack at `.cache/gems_data/`; no method paragraph was assigned to this review. More importantly, the committed release surfaces disagree about which generated TIFF is the submission file. Under the binding parallel-run rule (one assigned lane; no selector/slot picking here), it would be unsafe to silently choose one. Existing files remain available only under their own recorded statuses; this review does not independently promote any of them.

The consolidated project prompt is already in `README.md` under **PROJECT PROMPT (CONSOLIDATED)**. This follow-up adds a currentness and release-status warning rather than repeating the long prompt.

## Verified claims and irregularities

1. **The official public leaderboard was re-read directly.** At the session-side observation time 2026-10-31 04:33:42 UTC, the public page showed xiaofanhu at #1 with 0.4544; 0.3195 appeared at #50 for kpomazi. The public page is time-varying and does not link rows to TIFF bytes, private-round scores, or local outputs. Receipt: [`evidence/leaderboard-live-read-2026-10-31T0433Z.json`](../evidence/leaderboard-live-read-2026-10-31T0433Z.json); source: [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
2. **GEMSDOE32's 0.2778 remains USER-REPORTED / UNVERIFIED.** The repo's byte audit verifies the pinned 37,654-dot TIFF and its lineage, not that an organizer awarded that score to those bytes. The byte comparison records it as the GEMSDOE28/GEMSDOE31 base with 2,545 dots deleted (all 2,545 were within 200 m of the mirrored catalogue); it is also a thinning of the larger shared D2.8 pool. This is evidence for a *pruning/false-positive-mass explanation*, not proof of the private-label cause. Under a Tversky-style objective, removing predictions with negligible truth credit can reduce false-positive cost while retaining most credit; the saved files do not establish the hidden truth credit of the removed dots. Sources: [`evidence/gems32-b2-verification.json`](../evidence/gems32-b2-verification.json), [`evidence/champion_forensics.json`](../evidence/champion_forensics.json), [`evidence/gems32-h33-source-excerpts.json`](../evidence/gems32-h33-source-excerpts.json).
3. **No reliable prediction that a new raster will beat 0.2778 is demonstrated.** The repo's own saved matched-policy hide-and-recover audit reports Spearman -1.00 between the nine focus-file HOLDOUT-DTI values and their user-reported scores. It therefore cannot be used as a leaderboard score estimator. The stored score-estimator outputs are labelled projections and have large residuals; do not present them as measured scores. This is a central scientific limitation, not a minor caveat.
4. **Release decision conflict (high severity):**
   - `index.html` routes to `docs/release.html`, which offers the HALO raster.
   - `docs/release-summary.html` and `docs/release-how-to-submit.html` offer the distinct GBM raster and its own submission name/note.
   - The HALO `docs/release.html` submission-guide button points to `docs/how-to-submit.html`, whose first panel calls the geo-habitat raster an alternative; the GBM-specific instructions live at the differently named `release-how-to-submit.html`.
   - `evidence/public_downloads_audit.json` reports HALO as `downloadable_approved_submission`.
   - `evidence/lane-gbm/final-run-card.json` says `verdict: promote` but `weekly_slot_used: false` and explicitly says slot promotion is separate.
   - `scripts/assess_release.py`, when run on the root `evidence/run_card.json`, returns `negative` and `slot_authorized: false` because required lane/current evidence is missing or fails its gates.
   - `AGENTS.md` describes GBM as the current release, while README and the root release route describe HALO as the single recommendation.

   These outputs are not interchangeable: format/uniqueness clearance, a research-lane `promote` verdict, a repository recommendation, and authorization to spend a competition slot are different states. The repo does not currently provide one consistent end-to-end selector receipt tying a single public recommendation to every entrypoint. **Do not infer slot authorization from either page badge.** A follow-up must reconcile the generators, README/AGENTS, `docs/release.html`, the GBM pages, and the inventory before describing a single best file.
5. **Format warning:** some existing candidates use finite zeros outside the footprint; the shared writer's recorded exterior convention has differed. Although this avoids a whole-array [0,1] NaN failure, only an organizer template/receipt can settle the portal's exact behavior. No DrivenData session or submission receipt was available in this review.
6. **Hypothesis slate:** the existing preregistered `research/hypotheses-2026-10-31-untried-slate.md` has five candidates; S1 has already been run and was negative, while S2–S5 remain proposals. S2 (block-fitted terrain-residual gravity edge) uses `iso_grav_anom`, `iso_grav_anom_vg`, `det_elev`, and `det_elev_slope`; target signature is a residual density boundary persisting beneath cover; main mimics are unfaulted bedrock/alluvium contacts and shorelines; relative cost medium. S3 combines `geod_shearrate`/`geod_dilaterate` with persistent `rtp`/`tmi_hg` edges; targets a strain-regime change collocated with a multi-scale magnetic break; likely mimics include regional interpolation seams and intrusive contacts; medium cost. S4 tests `cond_surf`/`iso_grav_anom_hg`/`tc` break coincidence; target is a conductivity-gradient ridge crossing a gravity saddle; saline playa edges are a named mimic; medium-high cost. S5 links official thermal-spring/alteration observations to radiometric alteration corridors; spring/fault correlation is a named mimic and it needs external data.

   Relative gains in that slate are qualitative, not DTI estimates. The highest remaining hypothesis by that existing slate is S2; the slate is not a lane assignment. GeoDAWN bands are only represented by owner-mirrored assets in saved evidence, not authenticated organizer data in this checkout, and the cached stack is absent. S5 is **not viable this session**: the specific USGS thermal-spring/alteration source has not been verified obtainable here. No candidate was validated in this review, so no TIFF or holdout score is asserted.

## Verification passes

### Pass 1 — repository/state review

- Confirmed assigned branch is `arena/4c01c445-gemsdoekarage2`; working tree was clean before review-generated page evidence.
- Read `README.md`, `AGENTS.md`, current run cards, focus registry/score records, public-download audit, candidate run cards, and site build scripts.
- Confirmed `data/` and `.cache/gems_data/` are absent. No geological experiment or raster generation was attempted.
- Generated-page checks passed: `build_release.py --check`, `build_release_page.py --check`, `build_site.py --check`, `build_field_notes.py --check`, `build_audit_site.py --check`, and `build_hk3_pages.py --check`.
- Release assessor returned `negative`, `slot_authorized: false`. Download inventory returned `PASS_RESEARCH_ONLY_PLUS_RELEASE`, with HALO named as the downloadable approved submission. The disagreement is preserved as an irregularity rather than papered over.

### Pass 2 — bug, edge-case, and test review

- Python suite: **302 passed, 10 skipped**, 101 Rasterio `PendingDeprecationWarning`s, 98 subtests passed.
- Node feed suite: **3 passed**.
- Initial Node site suite: **7 passed, 2 failed** because assertions still expected an obsolete download inventory and `Unavailable` score cells. Updated the tests to enumerate current evidence-backed download artifacts, require an explicit `PROJECTION ... a model, not a score` label, and enforce the fail-closed release landing. Re-run: **10 passed**.
- Initial browser smoke test timed out because it expected `/` to navigate to retired `docs/index.html`; root now routes to `docs/release.html`. Updated the root landing page to stop automatic redirect and expose the HALO/GBM conflict; updated the browser test to verify that warning, the HALO release route and byte hash, the separate GBM summary route and byte hash, nine-site table, navigation, responsive widths, and the fail-safe metadata feed. Re-run: **all checks passed** at 1440, 390, and 320 px, including two candidate downloads against their saved hashes.
- `audit_public_downloads.py --check`: `PASS_RESEARCH_ONLY_PLUS_RELEASE`, 21 inventoried artifacts.
- No new score, TIFF, organizer acceptance, or selector authorization was created by these software checks.

### Pass 3 — user-request reconciliation

- The nine-site scorecard exists and distinguishes user-reported values from projections, but its projections must not be called scores and the underlying score-response model is weak/contradicted by the reported holdout rank correlation.
- The current public rank-one observation is 0.4544, higher than 0.3195 and 0.2778, from a direct official-page read. This does not show that any local file would score similarly.
- There is no assigned method paragraph for this review, no authenticated competition input/template, no current cached feature stack, no reproduced holdout experiment, and no single consistent public release/selector decision. Therefore a new unique TIFF with a defensible estimate cannot be generated and approved in this turn without violating the lane and stop rules.
- Prompt-storage requirement is already satisfied: the consolidated prompt and values are present in README; this report is linked from the new README review notice.

## Next steps, in order

1. Reconcile the competing HALO and GBM publication paths without spending a weekly slot. Produce one selector receipt that states whether each is a format-valid research artifact, a candidate, or an authorized recommendation; make all root routes and generated pages reflect that same state.
2. Assign exactly one new method paragraph. S2/S3/S4 remain hypotheses, not results; explicitly adjudicate overlap with prior gravity/topography/conductivity work and the parallel-run uniqueness stop before experiment.
3. Obtain authenticated competition data and the exact official sample/template through authorized access; hash-pin them. Resolve exterior/nodata and reproduce the portal [0,1] validation behavior without assuming the mechanism.
4. Restore the shared cached feature stack and use the pinned shared evaluator/writer. Test each feature alone, withhold whole fault segments plus buffers, use only visible catalogues in features and pixel-exact masking, and compare paired pooled DTI with 95% CI to a frozen same-protocol incumbent. Stop at three experiments or two hours.
5. Refresh all 492+ registry references (or establish the complete current registry), gate both pre-placement surface and final dots, then run the independent selector. Only its approved state should unlock any site-wide “OK to submit” callout. The account holder alone decides whether to spend the displayed weekly slot.
6. Continue to label every number as HOLDOUT-DTI (evaluator, withheld positives, CI), ORGANIZER-CONFIRMED (receipt), USER-REPORTED / UNVERIFIED, or PROJECTION.

## Official sources

- [Official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — directly read for the dated public snapshot above.
- [Competition problem and submission description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) — authentication remains unavailable in this checkout.
- [Official DOE/NLR rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS](https://gbcge.org/current-projects/ingenious/)

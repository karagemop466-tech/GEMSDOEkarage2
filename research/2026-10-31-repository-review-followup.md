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
   - `AGENTS.md` and README contain earlier lane-local statements that treated different files as the current recommendation; the new top-level review alert supersedes those statements pending selector reconciliation.

   These outputs are not interchangeable: format/uniqueness clearance, a research-lane `promote` verdict, a repository recommendation, and authorization to spend a competition slot are different states. The repo does not currently provide one consistent end-to-end selector receipt tying a single public recommendation to every entrypoint. **Do not infer slot authorization from either page badge.** A follow-up must reconcile the generators, README/AGENTS, `docs/release.html`, the GBM pages, and the inventory before describing a single best file.
5. **Literal uniqueness stop is currently triggered for both advertised candidates under the user's rule.** The HALO saved literal scan reports 0.9983897 of its dots within 3 px of the 13GEMSDOE lattice witness (`evidence/halo/registry_rows_literal_gate.json`); the GBM full-registry scan reports 0.99666 against its space-filling reference and 0.93771 against a non-lattice raster (`evidence/lane-gbm/uniqueness-full-registry.json`). Both exceed the prompt's 0.70 stop threshold even though their Spearman measurements are below 0.90. Existing release audits excluded or separately discounted the lattice as space-filling (IR-LATTICE-01); this review follows the current user protocol literally, which says *any* registry raster and has no such exception. The root landing page now says **do not submit either**. This is an irregularity that must be resolved by the protocol owner, not bypassed by changing the denominator.
6. **Format warning:** some existing candidates use finite zeros outside the footprint; the shared writer's recorded exterior convention has differed. Although this avoids a whole-array [0,1] NaN failure, only an organizer template/receipt can settle the portal's exact behavior. No DrivenData session or submission receipt was available in this review.
7. **Hypothesis slate:** the latest ranked proposals are in `research/hypotheses-2026-10-31-untried-h2.md`; all estimates are qualitative, not DTI score predictions. S1 (the earlier seismicity/strain lane) was already tested and negative. The remaining candidates are:

   | Rank | Candidate / layers / physical signature | Why it may catch an off-catalogue fault; named mimic | Cost / viability |
   |---|---|---|---|
   | 1 | **H-N1:** low-K + high eTh/U + RTP magnetic low within a 300–900 m mapped-fault band; radiometric alteration envelope | Blind hydrothermal alteration may mark covered fluid pathways; mimic: unfaulted bedrock/alluvium contacts, shorelines, saline playa margins | Low if cache exists; cannot validate here because data and cache are absent |
   | 2 | **H-N2:** gravity horizontal-gradient × conductivity-ridge intersection (`iso_grav_anom_hg`, `cond_surf`) with 200–500 m halo | Density break plus fluid-bearing conductive strata; mimic: saline playa/intrusive contact | Low from cached bands; must check proximity to the GEMSDOE32 H47 prior before placement |
   | 3 | **H-N3:** curvature convergence along strike (`det_elev_slope`, `det_elev`) beyond catalogue tips | Blind segments may continue past mapped tips; mimic: alluvial fans, terraces, erosional scarps | Low; possible overlap with previous HALO/tip methods requires lane review |
   | 4 | **H-N4:** geodetic dilation/shear corridor (`geod_dilaterate`, `geod_shearrate`) outside mapped pixels | Strain localization may indicate covered structures; mimic: regional interpolation seams / anthropogenic strain | Low; strain is coarse, and prior S1 supervised strain use was negative |
   | 5 | **H-N5:** thermal-spring connector corridor plus radiometric alteration | Springs could mark fluid pathways between blind structures; mimic: springs aligned only with known faults | High; official external-source availability is unverified and not viable here |

   **Internal inconsistency flagged:** that slate calls H-N1 “viable” from cached bands, then explicitly says `labels.tif` / `sample_submission.tif` are unavailable and required for holdout validation. Workspace check confirms `data/`, `.cache/work/`, and `.cache/gems_data/` are absent; only vendored evaluator/writer code exists. A separate earlier S1–S5 slate is historical and does not assign the current lane. No candidate was validated, so no new TIFF or HOLDOUT-DTI is asserted.
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
- Initial browser smoke test timed out because it expected `/` to navigate to retired `docs/index.html`. Updated the root landing page to stop automatic redirect, expose the HALO/GBM conflict and literal uniqueness failures, and warn against spending a slot; updated the browser test to verify that warning, the HALO release route and byte hash, the separate GBM summary route and byte hash, nine-site table, navigation, responsive widths, and the fail-safe metadata feed. Re-run: **all checks passed** at 1440, 390, and 320 px, including two candidate downloads against their saved hashes.
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

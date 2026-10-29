# Three-pass repository review — Arena branch `arena/b1c781e7-gemsdoekarage2` (2026-10-29)

## Decision at a glance

**NO TIFF IS APPROVED FOR COMPETITION SUBMISSION.** Do not submit or describe any existing download as a verified unique candidate. This review generated no raster, ran no new experiment, made no upload, and used no competition slot. It also makes **no new-file leaderboard-score estimate**: no defensible mapping from catalogue hide-and-recover performance to private expert labels is established.

The generated public pages previously called an H-A raster “new unique submission TIF — ready to download,” even while their body said not to submit it. Its audit explicitly says uniqueness vs registry was not verified and its run card has null holdout/canary evidence. That is misleading. I regenerated the three stale public pages from the fail-closed shared renderer. The current main/executive page now leads with **“No submission-ready TIFF”** and **“DO NOT SUBMIT”** and only offers an older, negative TIFF as a research/reproducibility artifact. No TIFF bytes were changed.

## Historical GEMSDOE32 result: what can and cannot be inferred

- The supplied **0.2778** is **USER-REPORTED / UNVERIFIED**, not ORGANIZER-CONFIRMED: the GEMSDOE32 owner site itself says there is no submission-page receipt linking the raster hash to that score. See [the owner page](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) and [`evidence/official-verification-2026-10-29.json`](../evidence/official-verification-2026-10-29.json), claim SS-01.
- The local byte/geometry audit reports that this raster is the D2.8 point set after 6,436 dots were removed; it did not add a new detector. The reported count arithmetic is 44,090 − 6,436 = 37,654. This explains a *possible* way the score improved: if the two reported scores used identical hidden labels and scoring, removing low-yield predictions can reduce false-positive mass under the DTI weights. It does **not** establish the causal explanation or verify either score. Source: [`evidence/champion_forensics.json`](../evidence/champion_forensics.json).
- From the official metric equation, under a first-order independent-pixel approximation, an additional prediction has positive marginal value only when its hit probability exceeds `alpha × DTI`; at DTI 0.2778 and alpha 0.2 this is about 0.0556. This is a mathematical heuristic, **not** a measured threshold under the exact kernel or a score estimate. It supports testing selective pruning, not copying the old point set.
- The public leaderboard snapshot dated 2026-10-29 records 0.4544 at #1 and kpomazi's 0.3195 at #47, not as the highest score. These are public snapshot values, not private round results or receipts for any local raster. See official source verification OV-08/09 in [`evidence/official-verification-2026-10-29.json`](../evidence/official-verification-2026-10-29.json). The snapshot was not refreshed in this review.

## Nine-site executive scorecard

The live summary is [`docs/executive-summary.html`](../docs/executive-summary.html); it has the historical file link, reported score, new-file estimate field, directional overlap audit and explicit action for each site. All reported historical scores below are **USER-REPORTED / UNVERIFIED**; none is an organizer receipt. New-file leaderboard estimate is **Unavailable** for all nine.

| Site | Historical file | Reported value | New-file score estimate | Unique against the audited focus-site set? | Submission decision |
|---|---|---:|---|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 | Unavailable | No | DO NOT SUBMIT |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 | Unavailable | No | DO NOT SUBMIT |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 | Unavailable | No | DO NOT SUBMIT |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 | Unavailable | No | DO NOT SUBMIT |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 | Unavailable | No | DO NOT SUBMIT |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 | Unavailable | No | DO NOT SUBMIT |
| GEMSDOE32 | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 0.2778 | Unavailable | No | DO NOT SUBMIT |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 | Unavailable | No | DO NOT SUBMIT |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 | Unavailable | No | DO NOT SUBMIT |

The files are pinned in [`registry/focus_sites.json`](../registry/focus_sites.json); the measured overlap is in [`evidence/geometry-audit.json`](../evidence/geometry-audit.json). “No” means the audited file exceeds the literal 70% within-3-pixel rule against at least one pinned focus-site raster. This is a scoped audit, not proof the complete fleet registry is known. The public pages label the files as research references and do not recommend downloading them for submission.

## Four distinct candidate hypotheses, ranked qualitatively

These are research proposals—not score projections or claims of global novelty. Prior work in the repository/focus set has overlapping ingredients; novelty means the specific proposed transform/control has not been validated in this checkout. The top proposal is **not** assigned or eligible to run under the current protocol.

| Priority / expected DTI value / cost | Layers and falsifiable physical signature | Why it could reveal a catalogue-missing fault | Named non-fault mimic and control | Difference from this repo’s implemented work | Data availability |
|---|---|---|---|---|---|
| 1 · Medium expected value, medium cost | Owner-mirror band 13 `iso_grav_anom`, band 11 `iso_grav_anom_vg`, band 12 `det_elev`, band 19 `det_elev_slope`. Fit a label-blind robust terrain/regional trend **within each training block**, then detect sign-persistent residual gravity steps at 300–900 m. Use a contour/shoreline-aligned null and a regression ablation. | A density contrast associated with a buried/covered structure may continue where a mapped surface scarp is absent; residualization attempts to separate it from topographic expression. | Unfaulted sediment–bedrock contact or lake-terrace riser; test contour-following and offset-block nulls. | Not the H1 opposing elevation/depth parity, K2 supervised raw-feature HGB, or B4 paired-flank step-asymmetry. B4 shares topography/gravity ingredients, so this is a possible lane collision; the distinguishing block-fitted nuisance model and predefined null do not establish novelty by themselves. | No new external source is required in principle if official competition bands are available. The `data/` organizer bundle is absent here; the owner-mirror raster is not organizer-authenticated. Official data tab: https://www.drivendata.org/competitions/306/competition-doe-gems/data/ (login required per existing access evidence). **Not currently runnable/validated.** |
| 2 · Medium expected value, medium/high cost | Bands 17 `cond_surf`, 13 `iso_grav_anom`, 18 `iso_grav_anom_hg`: test a cross-profile conductivity Hessian saddle aligned across an independently located gravity edge; do not use band 15 until its semantics are authenticated. | An obscured conduit could juxtapose conductive units across a density boundary without a clear surface trace. | Saline groundwater/playa margin or EM inversion seam; ablate conductivity and compare against coverage boundaries. | Prior K2 uses conductivity and gradient magnitudes; this targets sign-changing cross-profile saddle geometry, not simply a high-conductivity line. | Requires official features and metadata; official data tab login-gated. No external dataset or band interpretation has been authenticated here. |
| 3 · Low/medium expected value, medium cost | Bands 7 `geod_shearrate`, 8 `geod_dilaterate`, 2 `rtp`, 3 `tmi_hg`: coarse strain-regime change interacting with persistent magnetic edges; shuffled-strain negative control. | A covered strand might lie at a tectonic regime boundary, while the magnetic edge supplies independent structural context. | Geodetic interpolation seam or unfaulted intrusive contact; require interaction to beat magnetic-only controls and shuffled strain. | The tested K2 feature set excluded these strain bands; H1 focused on elevation/depth/conductivity parity. It is not a local fault locator from strain alone. | Bands only in owner mirror currently; official inputs and data lineage absent here. No new external source needed if organizer stack includes the verified bands. |
| 4 · Low expected value, low cost | Bands 10 `deq_n100a15`, 16 `ieq_n100a15`, 11 `iso_grav_anom_vg`: earthquake-density sidedness across an independently found gravity residual edge; shuffled seismicity control. | Active unmapped structures may have asymmetric seismicity across a potential-field break. | Induced/mining seismicity or density smoothing artifacts; use shuffled seismicity and require incremental matched-fold improvement. | No previous repo holdout model tested this specific edge-flank interaction; seismicity was not part of H1/K2. | Same absent official stack/labels issue; band meanings and units require metadata. No earthquake dataset is proposed as an available substitute. |

**Why no top-candidate holdout is reported:** the prompt does not assign one method paragraph; the previous lanes are retired/negative; the official `data/` bundle is absent; the pinned owner mirror is explicitly not organizer-authenticated; and no complete immutable registry has been established. The binding policy says missing evidence fails closed and the prior protocol/experiment limits cannot be restarted by inference. Therefore I did not run a feature, count a canary, or create a candidate. No weekly slot was touched. This does not satisfy the requested validation outcome; it documents why claiming such validation would be fabricated. The next session must obtain an explicit lane assignment and authorized organizer inputs before evaluating the top proposal.

## Evidence labels and strongest local holdout (prior evidence only)

The strongest recorded K3 point estimate in the available run evidence is **HOLDOUT-DTI — evaluator `gems57-pooled-hide-v2`, 58,258 withheld positive pixels, 95% CI [0.1747386, 0.2087970], DTI 0.1915728**. This is from `evidence/k3/combined_holdout.json`; it is catalogue hide-and-recover performance, not a public or private leaderboard score. The K3 candidate fails the registry uniqueness gate, so it is **negative / do not submit**. No new experiment in this review produced a HOLDOUT-DTI.

## Three passes and verification

### Pass 1 — task implementation and initial verification

- Read the project contract (`README.md`, `AGENTS.md`, `SUBMISSION_STATUS.md`), current blocker review, candidate slate, run cards, selector evidence, public artifact inventory, and page generator.
- Found a material user-facing contradiction: stale `docs/executive-summary.html` labeled a raster “unique” and “submission TIF” while its audit said uniqueness unverified and its card had no holdout or leakage test. It also linked directly to that unsupported file as the prominent call to action.
- Regenerated `docs/index.html`, `docs/executive-summary.html`, and `docs/how-to-submit.html` with `scripts/build_hk3_pages.py`. The shared fail-closed builder verifies hashes and negatives before rendering. Generated landing copy now says no submission-ready TIFF; its only current download is clearly marked an existing research-only TIFF, with the literal registry stop linked.
- Corrected the README leaderboard snapshot text: 0.3195 was rank 47 in the recorded 2026-10-29 snapshot, not the highest score or rank 27. Linked the claim-level evidence and made clear the snapshot is not new or a private score.
- Added this review and linked it as the current branch review.

### Pass 2 — bugs, omissions and edge cases

- Checked the H-A artifact run card/audit rather than trusting its filename or page headline: holdout, leakage canary and registry uniqueness are all unverified; no organizer template provenance. It cannot be recommended.
- Checked all nine pinned files and values against `registry/focus_sites.json`; the generated summary derives its overlap decisions from `evidence/geometry-audit.json` and pins the original source revision. Historical figures remain visibly unverified and all new-file estimates remain unavailable.
- Checked the builder's own freshness mode: before regeneration it flagged `index.html`, `executive-summary.html`, and `how-to-submit.html` stale. After regeneration its `--check` is clean. No generated or historical TIFF bytes were edited.
- The first full saved-download audit exposed two previously unindexed tracked TIFFs: the H-A artifact and `gemsdoe-karage2-gw-nfs-h1-20261029-zeros.tif`. The latter had no provenance/run card in tracked text. Rather than remove or imply validity, I added a hash-bound negative inventory record that explicitly says its method, holdout and uniqueness are unknown, and registered both files as research-only. The automated audit still says `downloadable_approved_submission: null`; neither is linked as an approved submission.
- Added regression checks for the nine-artifact inventory, the unidentified artifact's negative classification, the visible four-hypothesis slate and the no-approved-TIFF messaging. Corrected the local root redirect to reach the generated submission desk, matching the published Pages landing route and browser smoke test.
- Limit: owner mirrors and hash pins prove byte integrity only, not organizer provenance, scientific validity, hidden-label performance, or upload acceptance.

### Pass 3 — original request and safety recheck

- The website now makes it obvious there is **no file OK to submit**; automated format validation is not confused with the uniqueness/holdout gates. Instructions explain the process only conditionally.
- The nine-site executive scorecard lists the reported file/value and clearly distinguishes historical claims from any estimate. It reports estimates as unavailable rather than inventing a projected score.
- Four geological proposals, physical signatures, fault-missing rationale, non-fault mimics, repo differences, costs and data limitations are documented above and linked to the existing detailed slate. Candidate ranking is qualitative, not an estimated DTI.
- No experiment or TIFF could be validated under the missing lane/authorized-input/full-registry conditions, so no candidate is selected, approved, or submitted. The user's request to generate a submittable TIFF remains unmet; the evidence-based decision is to stop rather than violate the duplicate gate or fabricate a score.
- Official-reference links are retained in the page and below. The claim-level `evidence/official-verification-2026-10-29.json` is a prior dated source read, not a claim of new external refresh during this review.

### Official sources for review

- [Competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem, metric and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition data (participant login)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS / Great Basin Center for Geothermal Energy](https://gbcge.org/current-projects/ingenious/)
- [Source claim quotes and access status](../evidence/official-verification-2026-10-29.json)

**Remaining blockers (next session):** obtain an explicit assigned method paragraph; obtain/authenticate official competition feature, label and sample rasters; resolve footprint/NoData semantics and range error against organizer artifacts; construct a complete immutable registry; then only if authorized and within limits run one preregistered top hypothesis with the shared evaluator/writer, all feature-alone canaries, buffered whole-segment holdout, paired interval, and pre-placement registry gate. Promotion and quota selection remain separate. Do not run a slot before passing these gates.

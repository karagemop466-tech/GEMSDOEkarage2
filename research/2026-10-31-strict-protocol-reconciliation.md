# Three-pass repository review — literal uniqueness recheck (2026-10-31)

## Executive decision

**Negative. No current TIFF is cleared to submit. No new TIF was generated, no geological experiment was run, and no competition slot was used.** This review reconciles saved candidate receipts with the user's binding uniqueness rule, then removes false-positive “OK TO SUBMIT” states from the public site and inventory.

The rule is literal: stop when `|Spearman| > 0.90` against **any** registry raster **or** more than 70% of candidate dots fall within 3 px of **any** registry raster. The instruction does not define an exclusion for space-filling rasters. The site previously treated lattice saturation as an exceptional/degenerate control and treated selected like-for-like comparisons as clearance; that is a different policy. This change restores the original any-registry rule without modifying the old TIFFs or their lane receipts.

## Findings from committed evidence

| Candidate | Saved evidence | Literal result | Decision |
|---|---|---:|---|
| HALO, `gemsdoe-karage2-halo39-b44090-sep2-20261031.tif` | `evidence/halo/final_generation.json` | 99.83896575% within 3 px of the r13 spacing-5 lattice; `uniqueness_literal_gate.unique=false`, `stop_required=true` | **Research only / DO NOT SUBMIT** |
| Off-catalogue GBM, `gemsdoekarage2-gbm-offcat-a5-n100000-20261031T020958Z.tif` | `evidence/lane-gbm/uniqueness-full-registry.json`; `evidence/lane-gbm/final-run-card.json` | 93.771% one-sided overlap with a non-space-filling GEMSDOE30 raster. The audit also records 99.666% overlap with a space-filling reference that its policy excluded. | **Research only / DO NOT SUBMIT** |
| K10 corridor coverage | `evidence/k10/final_registry.json`; `evidence/k10/run_card.json` | Its `literal_reading.duplicate=true`; its like-for-like clearance excludes the lattice witness. | **Research only / DO NOT SUBMIT** |
| Nine requested site-best masks | `evidence/nine_site_best_files_audit.json`, pairwise and lattice receipts | The nine files fail the saved registry/family overlap gate; GEMSDOE32's supplied 0.2778 is not linked to an organizer receipt. | **Do not resubmit** |

A negative finding is not a judgment that the candidate was copied. It is the required protocol outcome. The lattice may be a sampling probe and the one-sided metric may be scientifically crude, but those are reasons to ask the protocol owner to revise the criterion before a future run—not reasons for an agent to silently waive it. The user explicitly prohibited “gaming” around the uncovered cells.

## What changed

1. `scripts/audit_public_downloads.py` now checks the literal uniqueness receipt as well as file bytes, range and grid. Candidates that are valid files but fail the uniqueness rule remain downloadable for research only; `downloadable_approved_submission` is `null`.
2. The root page and the HALO, GBM, K10 and historical submission desks now display a negative, research-only state. Existing TIFF bytes and lane run cards were not rewritten.
3. `AGENTS.md`, `README.md` and `SUBMISSION_STATUS.md` now state the binding rule and supersede earlier “cleared” wording.
4. `tests/browser-smoke.cjs` now exercises the real root route (`docs/release.html`), checks the negative badge, and verifies the research TIFF's SHA-256. The prior smoke test waited for the historical `docs/index.html` route and failed after the root redirect changed.
5. `evidence/strict-protocol-decision-2026-10-31.json` records the decision and the evidence paths.

## Three passes

### Pass 1 — reconcile receipts and implement the fail-closed state

- Re-read the exact saved fields used by the lane pages and inventory. Kept the two lane receipts' historical `promote` / `ok_to_submit` claims intact, but did not treat those claims as overriding the literal rule.
- Added the explicit strict gate to the byte inventory; the regenerated inventory is `PASS_RESEARCH_ONLY`, with no approved download.
- Updated source generators, not only generated HTML, and regenerated the pages.
- No TIFF was built or edited. No scientific experiment or holdout was run.

### Pass 2 — inspect conflicting paths and edge cases

- Checked direct root landing, both current release pages, summary/how-to pages, submission desk, and historical/generated site pages for green submission states.
- Preserved valid local format results as format results; they are not evidence of uniqueness, authenticated organizer format, portal acceptance, or score.
- Confirmed the custom site-score table continues to mark all nine reported values `USER-REPORTED / UNVERIFIED`; estimates for these nine remain unavailable.
- Added regression tests preventing positive lane selectors from overriding a literal overlap stop and ensuring failed-but-readable candidates remain research-only rather than mislabeled as corrupt.

### Pass 3 — verification and original-request reconciliation

- Python: **305 passed, 10 skipped, 101 warnings, 98 subtests passed**. Warnings are Rasterio `PendingDeprecationWarning`s for Affine multiplication.
- Node feed: **3 passed**. Node site: **9 passed**. Browser smoke: passed at 1440, 390 and 320 px, with the strict-negative route, research download hash and responsive checks.
- Page generators: `build_release_page.py --check`, `build_release.py --check`, and `build_hk3_pages.py --check` pass. `audit_public_downloads.py --check` passes and reports `PASS_RESEARCH_ONLY`, `downloadable_approved_submission: null`. Generic release assessor remains negative; `slot_authorized: false`.
- No current candidate passes the user's uniqueness condition. Therefore the requirement for a newly generated **unique** TIFF cannot honestly be fulfilled under the current rule. The repository retains research TIFF downloads, but none is labeled okay to submit. Do not treat a local score projection as a measured score.

## Candidate hypotheses for the next assigned lane

The ranking below is carried forward from [`research/hypotheses-2026-10-31-untried-slate.md`](hypotheses-2026-10-31-untried-slate.md). S1 there has already been run and was negative; only S2–S4 below remain proposals. They are not newly validated in this repository review and must not be presented as score estimates. The cached feature stack is not present in this checkout, so layer availability here is inherited from that dated feature receipt, not freshly confirmed.

| Rank | Hypothesis | Layers and target signature | Why it might identify an uncatalogued fault | Distinctness / mimic | Expected gain / cost |
|---|---|---|---|---|---|
| 1 | Terrain-residual gravity edge (S2) | Isostatic gravity anomaly and vertical-gradient (`iso_grav_anom`, `iso_grav_anom_vg`), detrended elevation and slope (`det_elev`, `det_elev_slope`); fit blockwise label-blind gravity/elevation residual, then detect its edge/TMA. | A density offset may continue beneath alluvial cover beyond the mapped surface scarp; removing terrain carry can expose the buried break. | Different from raw-gradient or flank-asymmetry methods recorded for H1/B4. Main non-fault mimic: unfaulted bedrock/alluvium contact or pluvial shoreline. | Medium qualitative; medium implementation cost. No numerical score claim. |
| 2 | Strain-regime change × persistent magnetic edge (S3) | Geodetic shear/dilation rate (`geod_shearrate`, `geod_dilaterate`) with RTP and total magnetic horizontal gradient (`rtp`, `tmi_hg`); sign/axis transition co-located with a multi-scale magnetic edge. | A covered active strand can localize deformation near a regime boundary without a surface trace. | The joint cross-layer interaction is distinct from prior single-layer/density maps, but geodetic fields are coarse relative to 100 m. Mimics: broad tectonic gradients or magnetic lithologic contacts. | Medium-low qualitative; medium cost. |
| 3 | Gravity-Hessian saddle × conductivity-gradient ridge (S4) | Surface conductivity (`cond_surf`), isostatic gravity horizontal gradient (`iso_grav_anom_hg`) and terrain correction (`tc`); target crossing saddles/intersections, linked into strands. | A buried offset may juxtapose conductive units and create a fluid pathway without a visible scarp. | Potential lane drift: GEMSDOE32 H47 previously tried a dual-horizon corridor. Must pass a pre-placement registry check and protocol owner distinctness review. Mimics: saline playa margins and conductive basin fill. | Medium qualitative; medium-high cost. |
| Not ranked viable | Thermal-spring corridor prior (S5) | Would combine official spring/thermal occurrences and GeoDAWN alteration/radiometric evidence. | A vent can indicate fluid upflow and associated feeder structure. | H-F alteration/curvature intersection is prior art; spring corridors are a different hypothesis. Mimic: springs may simply track already-mapped faults. | Low-medium qualitative; high data cost. **Not viable to propose yet:** official point source/access, footprint, license/provenance and reachability were not verified in this review; the repo's slate says the sandbox host allowlist prevented retrieval. |

Before any next experiment, the protocol owner must decide whether to retain the literal 70% rule (which currently stops ordinary dense dot submissions) or prospectively amend it. If amended, preregister one lane paragraph, use the shared cached stack/evaluator/writer, run feature-alone leakage canaries, compare a frozen incumbent on identical spatial folds with a paired 95% CI, and apply uniqueness both before placement and to final dots. No private evaluator fork or post-hoc exemption.

## Data access and score limitation

No competition data were restored into `data/` or `.cache/` during this review. The DrivenData training/data page requires participant authentication; this review did not access an authenticated organizer template or portal receipt. Thus the current local format checks are owner-mirror checks only. No up-to-date leaderboard was fetched in this review. Official manual-review links (source links retained in the repo; not fetched anew here):

- [DrivenData GEMS problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DOE/NLR official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN survey](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GBCGE INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [DOE Geothermal Data Repository record](https://gdr.openei.org/submissions/1391)

## Run card

See the companion machine-readable card [`evidence/strict-protocol-decision-2026-10-31.json`](../evidence/strict-protocol-decision-2026-10-31.json). It records: hypothesis = no new method tested; mechanism = reconcile receipts to literal uniqueness rule; no new holdout number/CI; no raster generated or newly validated; null submission name/note; negative verdict. This matches the run-card requirement without inventing a score or copying a historical TIF.

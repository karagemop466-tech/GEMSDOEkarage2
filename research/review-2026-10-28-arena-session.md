# Repository review — Arena session, 2026-10-28

## Executive decision

**NO APPROVED SUBMISSION — DO NOT SUBMIT any repository TIFF.** This review generated no raster, ran no geological experiment, selected no competition slot, and performed no upload. The K2 research artifact is still downloadable for audit, but an explicit K2 selector receipt now records `verdict: negative`, `ok_to_submit: false`, `slot_authorized: false` at `evidence/k2/selector_result.json`.

The decisive issue is not leaderboard score or format: K2's archived pre-placement surface support overlaps the spacing-5 lattice at 1.0, exceeding the literal >0.70 stop threshold before dot placement. Its archived final scan also reports duplicates, an incomplete scan, and a 0.7205 overlap against a calibration ridge raster. The strict historical outside-footprint-NaN check fails. The registry cannot be narrowed or calibration entries exempted without an authorized protocol ruling. These gates make K2 **not eligible**, regardless of its prior holdout result or comparison with a subset of submission files.

## Pass 1 — repository and evidence review

Read the README, AGENTS instructions, nine-site audit, preregistration, K2 experiment and selector cards, current site pages, and regression suites. The README contains the consolidated project mandate and manual source links. The site has an executive summary and individual cards for the nine named focus repos.

### Nine-site score interpretation

The supplied GEMSDOE32 `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` value of **0.2778** is reported in this project as **USER-REPORTED / UNVERIFIED**, not as an organizer-confirmed receipt. The prior mirror audit describes its raster as a dot-pruned member of a shared D2.8 family. That is a plausible emission/masking explanation for why it ranked above related user-reported files, not proof of private-test causality. The 0.2778 value is not a valid score estimate for a new file. The leaderboard estimate remains **unavailable**; catalogue holdout is not calibrated to the expert-hidden leaderboard.

### Candidate slate already preregistered elsewhere

The five candidate hypotheses below come from `research/hypotheses-2026-10-28-preregistration.md`; they are not newly proposed or validated in this review. The original preregistration contains the full method differences and implementation cost assessments.

1. **Supervised multi-physics texture:** magnetic/gravity/topographic/basement/conductivity layers; multiscale gradients and difference-of-Gaussian signatures. Rationale: mapped-fault texture may recur on hidden structures. Mimics: lithologic/intrusive contacts and catalogue mapping bias. Medium cost.
2. **Fault-tip/gap continuation:** visible segment endpoints, strike and local continuation corridors. Rationale: traces can be truncated by cover. Mimics: actual segment termination or en-échelon geometry. Low–medium cost.
3. **Structure-tensor ridge coherence:** orientation coherence over fused edge magnitude. Rationale: directional lineaments may be more fault-like than isotropic noise. Mimics: roads, canals, flight-line artifacts and bedding ridges. Low cost.
4. **Scarp-step asymmetry:** paired elevation-flank differences persistent along strike. Rationale: fault scarps are steps and may remain detectable after crest erosion. Mimics: shoreline benches, terraces and road cuts. Medium cost; official 1 m DEM availability remains login-gated in the supplied references.
5. **Seismicity alignment:** provided seismicity/depth aggregates aligned with structures. Rationale: active unmapped faults may host seismicity. Mimics: blasts and induced seismicity; stack resolution is a concern. Low cost, expected weaker.

The method-lane instruction does not supply an assigned method paragraph. K2 previously self-assigned one and already used the three-experiment budget. The current instructions prohibit inventing a lane or exceeding the cap. Thus no candidate was tested or claimed to beat the current holdout best in this review. No new data source is proposed as available without verification.

### K2 evidence and limits

- The saved raster SHA-256 is `504be4587e3bec7b81f802b4c16b6c546c683e8a4c8b514d3a9856c6e0698dfb`; it matches the archived run card. This is byte identity only.
- Prior **HOLDOUT-DTI** is 0.1581207190 (95% CI [0.1423739219, 0.1741535541]), evaluator `gems57-pooled-hide-v2`, 58,258 withheld positive pixels. This is archived evidence, not independently replayed here, not an ORGANIZER-CONFIRMED score, and not a calibrated leaderboard estimate.
- The archived feature canaries reported 26/26 below the threshold, with worst symmetric AUC 0.6211. Not rerun here.
- The K2 selector receipt states the strict scope result: final overlap 1.0 against the spacing-5 calibration lattice; 0.7205 against the ctx-ridge calibration mask; registry coverage incomplete; organizer input/template and weekly account quota unavailable. It explicitly sets `ok_to_submit: false`.
- The separate review card records finite saved pixels in [0,1] and matching shape/transform against the owner-mirror metadata, but the strict exterior-NaN validation is false and the organizer template is unauthenticated. This does not establish portal acceptance.

## Pass 2 — release and code review

The current mainline includes the critical release correction: homepage and guide consistently say K2 is negative and DO NOT SUBMIT; the historical conditional recommendation is preserved only as evidence. It disables the K2 final export path, adds fail-closed release/selector receipts, and hardens the readiness and raster-integrity checks. Concurrent B4 and H2 experiments are also now present in mainline as **negative, research-only** results: B4's best documented HOLDOUT-DTI remains below K2's archived incumbent, and H2 is explicitly not approved. These later experiments are prior work from other sessions, not experiments run here. The current public pages keep the no-submit state.

This session's branch changes were reconciled with the concurrently advanced mainline before PR review; the mainline's later safety evidence and selector changes were retained. The report and tests should be judged against that newer state, not the original stale checkout.

## Pass 3 — verification and original-request check

All current downloads are research evidence only. The nine-site scores remain visibly user-reported; there is no score forecast; the downloadable K2 TIF is not cleared as unique and must not be submitted. The submission guide describes the future workflow without selecting a file or spending a slot. No human inspection is used to bypass automated gates.

Final verification on the reconciled tree:

- `.venv/bin/pytest -q` — final merged-tree run: **176 passed, 7 skipped**, 98 subtests passed; 79 non-failing Rasterio `PendingDeprecationWarning`s.
- `.venv/bin/python scripts/assess_release.py`, `scripts/audit_k2_release.py`, `scripts/review_k2_release.py`, `scripts/build_site.py`, `scripts/build_field_notes.py`, and `scripts/build_audit_site.py --check` — completed; generated-artifact check (`git diff --exit-code -- docs evidence`) passed.
- `npm test` — **3 passed**; `npm run test:site` — **9 passed**; the browser smoke suite passed on desktop and 390/320 px mobile widths, release lock and freshness states.
- `git diff --check` — passed.

No new geological experiment, TIF generation, promotion or upload was performed. The K2 run is not re-labeled as a new experiment.

## Remaining blockers / next work

1. Get an explicit coordinator-assigned lane and formal ruling on the literal registry definition. Do not exempt reference/calibration rasters privately.
2. Restore and authenticate official competition inputs and the exact official template; resolve the exterior/nodata convention from organizer evidence.
3. Build a complete, current registry and frozen matched incumbent. Only then preregister one allowed experiment, run per-feature leakage canaries, buffered whole-segment hide-and-recover, and surface and final-dot novelty checks with the shared tools.
4. A separate selector can evaluate weekly quota only after all gates pass. Capture a file-bound organizer receipt after an actual submission; do not present HOLDOUT-DTI as leaderboard score.
5. Refresh leaderboard and external-source data only if the network/authentication pathway permits; label stale or unavailable results explicitly.

## Manual-review sources

These links are provided for manual verification; this session did not fetch non-GitHub official sources due the sandbox network allowlist.

- [Official DrivenData competition](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem description and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [About page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [Official data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [DOE Geothermal Data Repository submission 1391](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)

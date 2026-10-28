# Repository review — 2026-10-28

## Executive disposition

**Release: NEGATIVE — DO NOT SUBMIT any TIFF in this checkout.** The HK3 file remains a research artifact that can be downloaded for audit, not a competition recommendation. Its historical `PROMOTE` card and selector result are preserved for provenance; a new hash-bound safety decision supersedes that recommendation because it applied an exception forbidden by the prompt's literal registry rule. No geological experiment, dot placement, submission, or competition-slot use occurred during this review.

The existing repository had an urgent user-facing safety defect: the homepage and executive summary said “OK TO SUBMIT: YES” and “Submit” even though the run card itself recorded a failed literal uniqueness gate. The page generator applied an unpermitted exception to that hard stop. The registry audit also omitted a degenerate lattice witness despite the protocol saying **any** registry raster counts. This review corrected the public release decision and generator so those contradictions fail closed.

## Three-pass review

### Pass 1 — inspect scope, artifacts, and scientific claims

Read `README.md`, `AGENTS.md`, the HK3 run card and selector result, the registry audit, strict format audit, generated site pages, build scripts, tests, data manifests, and previous reviews/preregistrations. Confirmed that the working tree initially had no local changes and the active branch was `arena/845f044c-gemsdoekarage2`.

The nine-site scores in the prompt and pinned manifests are **USER-REPORTED / UNVERIFIED**, not organizer receipts. The listed GEMSDOE32 result is 0.2778, but no current independent leaderboard value was reachable from this environment. The prompt itself gives conflicting historical leaderboard claims (0.4413, 0.3195); the README also held a previous user-reported 0.4544. No one of these is used here as current verified ground truth.

### Pass 2 — test each release gate against the binding protocol

**The HK3 artifact fails the mandatory uniqueness stop.** Saved registry evidence reports:

| Measurement | Result | Consequence |
|---|---:|---|
| Spearman rank-correlation maximum | 0.11434 | Under 0.90; this one test passes |
| Candidate dots within 3 px of r13 lattice witness | 99.8626% | Exceeds 70%; hard stop |
| Candidate dots within 3 px of `gems10-h25-ctx-ridge` | 70.9763% | Exceeds 70%; hard stop |
| Candidate dots within 3 px of GEMSDOE32 H45 KS0 | 73.3484% | Exceeds 70%; hard stop |
| Candidate dots within 3 px of the repository's K2 artifact | 74.9401% | Exceeds 70%; hard stop |
| Registry access completeness | 452 checked, 1 missing/invalid | Global uniqueness cannot be certified |
| Pre-placement surface registry check | No auditable result found in the committed HK3 receipts | Required surface-level stop cannot be verified |

The historical HK3 report called the lattice “degenerate,” excluded it from the literal test, and waived three failures because certain rasters were not confirmed scored dot submissions. The prompt says to stop for **any registry raster** over the stated threshold and contains no such exemptions. Chance correction, visual judgment, submission status, or a small rank-correlation cannot override this literal rule. Surface screening must happen before placement; a final-dot scan cannot retroactively clear a prohibited placement.

**Other independent blockers:** the prompt's “single method paragraph” is not uniquely identifiable. The HK3 card labels its lane self-declared, not coordinator-assigned. The recorded HK3 wall time is approximately 2 h 15 min, beyond the 2-hour experiment budget. Its holdout value does not beat the repository's reported current holdout-best K3 value: HK3 HOLDOUT-DTI is 0.18450 [0.16769, 0.20148] versus K3 0.19157 [0.1747, 0.2088] at the same nominal budget/evaluator; intervals overlap and there is no paired cross-session test. These are HOLDOUT-DTI values, not leaderboard estimates. The sample/grid was matched to a hash-pinned owner mirror, not an authenticated organizer download; the historical strict outside-NaN check fails, while the portal's exterior convention and acceptance remain unverified.

**The TIF itself is locally readable/format-checked in committed receipts**: SHA-256 `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`, single-band float32, EPSG:32611, 3730 × 3292, finite values in [0,1], 0 outside according to the mirror footprint. These checks do not rescue uniqueness, establish official-template provenance, or prove upload acceptance.

### Pass 3 — fix, regenerate, and verify the safety surface

Implemented a current release-safety decision bound to the candidate SHA-256. Updated the generated-page builder to consult that decision rather than the historical `PROMOTE` field, label the existing TIFF a research-only download, surface the full literal-rule failure including the lattice witness, and state that no file is approved. Corrected `audit_public_downloads.py`, which had still reported the historical HK3 TIFF as `PASS_ONE_CANDIDATE_FOR_UPLOAD`; it now respects the current negative release decision and reports `PASS_RESEARCH_ONLY` with no approved download. Updated the Pages workflow to regenerate the release-locked pages after the shared site builder. Updated README and `AGENTS.md` current status. Added regression tests requiring current fail-closed status and hash binding; preserved old run cards as immutable historical evidence.

Verification after the fix (pinned Python dependencies in ignored `.venv`; Node dependencies from the lockfile):

- CI safety sequence (`assess_release.py`, `audit_k2_release.py`, `audit_public_downloads.py --check`, `review_k2_release.py`, site builders, HK3 generator, generator `--check`): passed. `assess_release.py` remains negative; the published-download inventory is `PASS_RESEARCH_ONLY`, with no approved submission path.
- `.venv/bin/python -m pytest -q`: **201 passed, 7 skipped, 98 subtests passed**; 86 Rasterio `PendingDeprecationWarning`s remain.
- `npm test`: **3 passed**.
- `npm run test:site`: **7 passed**.
- `npm run test:browser`: **passed** desktop 1440 px and mobile 390/320 px checks plus freshness fail-safe checks.
- `python scripts/build_hk3_pages.py --check` and `python scripts/audit_public_downloads.py --check`: passed.

The seven Python skips are input-dependent tests, so they do not authenticate organizer data or establish portal acceptance.

## GEMSDOE32 0.2778: evidence-grounded interpretation

The supplied score is the highest user-reported result among the nine focus sites, but its receipt was not independently verified here. Saved pinned-byte analysis shows a related family of ridge-dot maps and reports GEMSDOE32 B2 as a parent-family map with a band near the mapped catalogue removed. This is consistent with the metric penalizing predicted mass on/near known faults that are excluded from scoring: removing low-value/false-positive predictions can raise DTI without discovering more faults. It is **not** evidence that the removed dots were all false positives, nor a causal estimate of the private score. The catalog hide-and-recover bridge does not reproduce the supplied GEMSDOE32 result (the stored same-fold HOLDOUT-DTI is only 0.0067), which is a strong warning that public-catalogue holdout performance is a weak proxy for hidden expert labels.

Consequently, the repository's historic point range 0.2628–0.2855 is an exploratory calibration/projection based on user-reported scores and transfer assumptions. It is not a validated leaderboard estimate, and this review withdraws it as a recommendation. No evidence here establishes that a newly designed raster can beat 0.2778 or the current leaderboard leader.

## Candidate hypotheses for a future, explicitly assigned lane

These are **proposals, not experiments or score estimates**. The more detailed prior-art review and access caveats are in [`research/2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md). Their layers are from the current hash-pinned owner mirror; layer semantics/provenance require organizer authentication. No candidate is eligible to run until the method lane, complete registry, official inputs, and 2-hour/three-experiment budget are resolved.

| Rank | Candidate, layers, target signature | Why it could find unmapped faults | Mimic / cost / repo distinction |
|---|---|---|---|
| 1 | Terrain-conditioned residual gravity step: bands 13 `iso_grav_anom`, 11 `iso_grav_anom_vg`, 12 `det_elev`, 19 `det_elev_slope`; fit a label-blind terrain/trend regression per training block, then test persistent signed residual edges at 300–900 m. | A buried density offset beneath alluvium can extend beyond an exposed mapped scarp. Residualization tests whether a gravity step remains after relief effects, rather than merely following the mapped trace. | Mimics: unfaulted sediment–bedrock contact or lake-terrace riser. Medium cost. Differs from K2 raw/magnitude features and B4 paired elevation-flank steps by using block-fit terrain residuals and a preregistered shoreline null; potential family collision must be tested. |
| 2 | Conductivity saddle across independent gravity break: bands 17 `cond_surf`, 13 `iso_grav_anom`, 18 `iso_grav_anom_hg`; detect a conductivity-Hessian sign change across (not simply along) a gravity edge. | A covered conduit/offset may straddle conductive strata and a density contrast while lacking a surface trace. It is a fault hypothesis, not proof of a vent or fluid. | Mimics: saline groundwater/playa margins and inversion seams. Medium-high cost. Differs from use of conductivity magnitude or simple gradients; repo previously proposed similar but did not implement this exact sign-changing cross-edge test. |
| 3 | Strain-regime change as a coarse prior: bands 7 `geod_shearrate`, 8 `geod_dilaterate`, 2 `rtp`, 3 `tmi_hg`; interact spatial strain change with magnetic-edge persistence and compare with a strain-shuffled control. | A covered strand might occur at a tectonic-regime transition, but 100 m interpolated strain is only contextual evidence. | Mimics: geodetic interpolation seams and intrusive contacts. Medium cost. Repo's K2 omitted strain; an earlier hypothesis proposed strain, so it is not novel to the project backlog. |
| 4 | Seismicity-sidedness falsification: bands 10 `deq_n100a15`, 16 `ieq_n100a15`, 11 `iso_grav_anom_vg`; test seismicity differences across independently detected gravity edges. | Active unmapped faults can host earthquake clusters; this must add value beyond an edge-only baseline. | Mimics: mining/induced seismicity and density-smoothing artifacts. Low-medium cost. This exact flank test is not an implemented local model, but related seismic ideas exist in sibling sites; no fleet-wide novelty claim. |

The proposal slate does not need a new external dataset, but the current layer stack is a non-authenticated owner mirror. An eventual lidar-morphometry method would require free official USGS 3DEP / The National Map files and footprint/hash verification before it can be called obtainable; this review did not fetch those tiles.

## Sources and verification limits

Official/manual references for follow-up (not claimed as freshly fetched in this review):

- [DrivenData competition rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData problem and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [DrivenData data page (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Current leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official reference solution on GitHub](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) and [The National Map downloader](https://apps.nationalmap.gov/downloader/)

This sandbox can contact GitHub and package registries but not DrivenData, USGS, DOE or Dropbox. Therefore current leaderboard status, organizer receipts, official data bytes, portal acceptance, account quota, and new USGS/DEM availability could not be verified from this environment. GitHub-pinned sibling-site artifacts are historical snapshots, not a complete/current organizer registry.

## Next-session checklist

1. Keep all current TIFF links marked **research-only / DO NOT SUBMIT**.
2. Obtain explicit coordinator lane assignment and clarify the exact registry inventory policy without relaxing the stated literal threshold.
3. Restore organizer-authenticated data, sample submission, band metadata, and outside-footprint convention; recover a complete, hash-pinned registry including latest site heads.
4. Select the best *same-evaluator* holdout baseline and preregister 3–5 falsifiable candidates; test each feature-alone canary first.
5. Run only the assigned top idea, use the shared stack/evaluator/writer, hide buffered whole segments, and stop at the first surface-level duplicate. No dot placement until that gate passes.
6. Respect the three-experiment / two-hour cap, whichever comes first. Require paired HOLDOUT-DTI + 95% CI to beat the incumbent before separate selector review.
7. Re-run final uniqueness and authenticated format checks. Only a complete, clean audit can create a future `OK TO SUBMIT: YES`; record any organizer result only from a submission-page receipt.

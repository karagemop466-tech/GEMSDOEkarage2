# Three-pass repository review and release ruling — 2026-10-28

## Outcome

**NO APPROVED SUBMISSION. DO NOT SUBMIT the K2 TIFF.** The file remains available only as a research artifact so its measurements can be inspected and reproduced. Its bytes pass the recorded local numeric/format checks, but its final-dot support violates the literal registry uniqueness stop rule, and the registry inventory is not certified complete. No experiment or competition slot was used during this review.

This is a correction to the earlier K2 `promote` / conditional-submit wording. The raw holdout measurements are preserved; the decision is negative because a hard release gate failed. No selector exception or calibration-record exemption is inferred or recommended.

## Pass 1 — inspect repository and receipts

- Working tree was clean at review start; active branch was `arena/31fe6ecb-gemsdoekarage2`.
- Read the README and the project protocol, K2 preregistration, experiment receipt, final registry audits, strict TIFF validator receipt, focus-site registry, current dashboard, submission guide, and existing tests.
- Recomputed the candidate file SHA-256 from its saved bytes: `504be4587e3bec7b81f802b4c16b6c546c683e8a4c8b514d3a9856c6e0698dfb`; this matches the recorded K2 receipt.
- K2's measured holdout result is **HOLDOUT-DTI 0.1581207190**, evaluator `gems57-pooled-hide-v2`, 58,258 withheld positive pixels, 95% CI [0.1423739219, 0.1741535541]. Its paired delta versus the best primitive is +0.08614, 95% CI [+0.06914, +0.10369]. These are catalogue hide-and-recover results, not a leaderboard score or a forecast.
- The final registry audit records the 5-pixel lattice at 100% of candidate dots within 3 pixels, and `gems10-h25-ctx-ridge` at 72.0523%, both above the literal 70% stop threshold. The audit says `verdict: negative`, `stop_required: true`, and `unique: false`. The lattice alone makes the threshold impossible for any in-footprint integer pixel centre because the maximum distance to its 5-spaced nodes is sqrt(8) < 3 pixels. This is an unsatisfiable rule as currently scoped, not permission to evade it.
- The audit also records `complete_accessible_scan: false`, 442/443 records checked, and one grid-incomparable 32x48 test record. Therefore no global uniqueness certificate exists. The separate focus-submission scan is narrower and does not override either this failure or the incomplete-inventory warning.
- The pre-placement surface check documented in the run card covers the nine focus best rasters and the lattice, but does not establish a ctx-ridge surface check. That is another evidence gap; it cannot repair the final-dot stop.
- Strict local TIFF validation reports 11/12 checks passing; `outside_is_nan` fails because the file encodes exterior cells as zero. The independent writer receipt reports all-finite [0,1] values and a matching grid to an owner mirror, but that mirror is not authenticated as the organizer's template. Local validity is not portal acceptance.

## Pass 2 — apply protocol literally

The protocol says stop when the final dots are within 3 pixels of more than 70% of one registry raster's dots. The K2 record crosses that threshold for two registry entries. Therefore the candidate is a duplicate under this protocol and the correct verdict is **negative**, regardless of its holdout improvement or whether the calibration rasters were intended as submissions. A project reviewer must not silently narrow the registry, exempt a record, or ask a human selector to waive a failed gate.

The prior K2 record's `verdict: promote`, `CONDITIONAL YES`, and suggestion to exempt the lattice were inconsistent with the literal protocol and its own negative registry audit. The active dashboard, run cards, README, agent instructions, and submission guide have been corrected to say **research download only — DO NOT SUBMIT**. No TIFF pixels were altered, and no new candidate was generated.

The 0.2778 GEMSDOE32 value remains **USER-REPORTED / UNVERIFIED** in the supplied historical data, not an ORGANIZER-CONFIRMED receipt. K2's HOLDOUT-DTI is not comparable to that private score. Accordingly, whether any candidate here scores above 0.2778 is **unknown**, and no leaderboard estimate is available.

## Pass 3 — verification

- `npm ci`: passed; 0 reported vulnerabilities.
- `npm test`: passed, 3/3 tests.
- `npm run test:site`: passed, 7/7 tests before adding the release-status regression test.
- `npm run test:browser`: passed at 1440, 390, and 320 px; no viewport overflow and freshness failure states remained fail-safe.
- Python scientific dependencies (`numpy`, `rasterio`, `scipy`, `scikit-learn`, `pytest`) are not installed in this runtime, and competition input data is not present under `data/`; no Python scientific rerun was possible here. The existing K2 measurements above are read from tracked receipts, not represented as freshly reproduced.
- No live DrivenData receipt, authenticated submission template, complete registry certificate, current quota, or competition upload was available. None is claimed.

## Required next steps

1. Keep K2 and prior files labelled research-only. Do not submit, rename as a new candidate, perturb dots, or spend a slot to test it.
2. Before a new experiment, obtain a coordinator-defined method lane and resolve the uniqueness rule's calibration-lattice impossibility **in the shared protocol**; until the literal registry rule changes, any in-footprint candidate necessarily triggers the stop. Do not make an ad hoc exemption.
3. Authenticate the competition inputs and exact footprint/template from DrivenData; resolve exterior encoding with official instructions. Current mirrors are owner-provided, not organizer-authenticated.
4. Obtain a complete, hash-pinned registry inventory and a comparable frozen incumbent, then preregister a fresh experiment. Respect the experiment/time budget; this review did not authorize additional experiments.
5. Preserve the distinction among USER-REPORTED site values, HOLDOUT-DTI results, projections (if ever shown, explicitly not scores), and ORGANIZER-CONFIRMED receipts.

## References

- [Competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official competition data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (authentication may be required)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) (live and time-sensitive; no current score was re-read for this review)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [K2 experiment receipt](../evidence/k2/run_card.json)
- [Final registry audit](../evidence/k2/final_registry_audit.json)
- [Strict TIFF audit](../evidence/k2/validate_tif_strict.json)
- [Nine-site evidence table](../registry/focus_sites.json)

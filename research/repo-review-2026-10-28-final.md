# Three-pass repository review — 2026-10-28

## Executive finding

**No artifact is currently approved to upload.** The repository contained a dangerous contradiction: the historical HK3 run card said `PROMOTE` and public pages said **OK TO SUBMIT**, despite a required literal-uniqueness failure. The current hash-bound assessment records 45,046/45,108 candidate dots (99.8626%) within 3 px of the r13 lattice, and an incomplete 452/453 registry scan; the historical non-degenerate scan also records three other overlaps of 71.0%, 73.3%, and 74.9%. The prior exception is preserved in [`evidence/hk3/approval-retracted-20261028.json`](../evidence/hk3/approval-retracted-20261028.json), while the current run card/selector are negative. The lane remains self-declared (not coordinator-assigned). The current prompt says any >70% overlap is a stop, with no dense-witness exception. Other prerequisites (a verifiable pre-placement surface-gate receipt, authenticated competition inputs/template, and a machine-readable runtime receipt) are also absent. The user-reported GEMSDOE32 result 0.2778 cannot be causally explained or exceeded with confidence from the evidence here.

The old HK3 GeoTIFF remains in the repository for audit/reproducibility, but is now clearly downloadable **for research only — DO NOT SUBMIT**. The how-to page refuses to provide upload steps while gates fail. No competition slot was used and no new geological experiment was run.

## Pass 1 — inspect and reconcile

Reviewed `README.md`, `AGENTS.md`, run cards and selector evidence, the shared evaluator/writer manifests, the nine-site registry audit, site generator, test suite, and existing hypotheses. Confirmed the following from committed repository artifacts:

- Historical HK3 run card: candidate HOLDOUT-DTI **0.1845 [0.1677, 0.2015]**, versus refitted incumbent **0.1575 [0.1417, 0.1737]**; evaluator `gems57-pooled-hide-v2`; 58,258 withheld positive pixels; paired difference **+0.0270 [+0.0206, +0.0337]**. This is catalogue holdout evidence, not organizer scoring.
- The full-scope HK3 assessment reports **45,046 of 45,108 dots (99.8626%)** within 3 px of the r13 lattice and an incomplete registry scan (**452/453**). The historical non-degenerate scan separately fails against three entries at **71.0%, 73.3%, and 74.9%**. The current protocol allows no dense-witness exemption; both records establish a stop, not a pass. The U1 comparison against nine named focus files passes but does **not** cancel either broader failure.
- Its `lane` field says “self-declared; no coordinator paragraph supplied.” No coordinator assignment, surface-pre-placement gate receipt bound to a surface hash, authenticated competition input/template receipt, or machine-readable elapsed-time receipt is included. The run card reports 3 experiments and approximately 2 h 15 min, which exceeds the 2-hour cap. Do not run more HK3 experiments.
- The claimed organizer estimate **0.263–0.286** in the historical run card is a LEADERBOARD-CALIBRATED ESTIMATE, not a score. It does not establish a score above 0.2778. The 0.2778, 0.3195, 0.4413 and other numbers typed in the prompt are USER-REPORTED / UNVERIFIED unless a submission-page receipt is attached.
- The explanation for the high GEMSDOE32 score remains a hypothesis. Pinned-raster lineage suggests the B2 file pruned mapped-fault-adjacent dots from a related ridge-dot family, which could reduce false-positive mass where mapped faults are excluded. This is a plausible metric mechanism, not causal proof: the exact score is not receipt-verified here, private labels are unavailable, and no valid independent replay of the hidden scoring set exists.
- Site material identifies the historical focus-site winners and their scores, but snapshots and owner mirrors do not establish the current upstream site state or current leaderboard. Exact-file dissimilarity from the nine files is not proof of unique placement against the complete registry.

## Pass 2 — fix the safety defect and review edge cases

### Implemented

1. The main-branch release correction retracts the historical HK3 approval, sets the current run card and selector negative, and preserves the prior decision and reason in a separate retraction receipt. `scripts/build_hk3_pages.py` calls the shared fail-closed `publication_eligible()` policy rather than trusting the historical `PROMOTE` string.
2. The merged main branch routes publication through `scripts/hk3_release_policy.py` into the shared `scripts/readiness.py` evidence contract, which requires complete registry coverage, a coordinator assignment receipt, verified pre-placement/final-dot comparisons, holdout provenance, organizer-input/template attestations, and the literal hard stops. This review strengthened it to require a pre-placement receipt hash bound to a surface hash and organizer provenance hashes for the input manifest and template. It also adds a machine-readable budget receipt gate: integer experiments in [0, 3], finite elapsed seconds in [0, 7,200], and a 64-character SHA-256. Missing, malformed, or over-budget records fail closed. These are schema checks; they do not independently authenticate receipt contents.
3. Regenerated the home, executive-summary, how-to-submit and submit pages. They show a negative submission badge, label the existing HK3 file **RESEARCH ONLY — DO NOT SUBMIT**, and tell users to stop and not upload or spend a slot. The guide's generic future steps are conditional on a new candidate passing all gates and are not authorization for HK3.
4. Reframed the GEMSDOE32 discussion as a cautious explanation of a user-reported result, not an established causal finding. Clarified that the historical leaderboard estimate is not a score.
5. Added regression tests for hard-stop handling, missing receipts, incomplete registry coverage, page status, and blocked upload instructions. The current run card is negative; the former PROMOTE verdict and its exception rationale are preserved in the separate approval-retraction receipt.
6. Updated the README's authoritative status and `AGENTS.md` so the next session does not encounter contradictory “approved” versus “not approved” instructions.

### Verification

- `.venv/bin/python scripts/assess_release.py`: negative; no slot authorized. `.venv/bin/python scripts/audit_k2_release.py` and `scripts/review_k2_release.py`: negative audits, with zero new experiments.
- `.venv/bin/python scripts/review_hk3_protocol.py --check`: pass; correction remains negative, research-only, zero new experiments or slots.
- `.venv/bin/python scripts/build_hk3_pages.py --check`: pass; generated home, executive summary, submission guide and nine focus summaries are synchronized and display a negative release decision.
- `.venv/bin/python scripts/audit_public_downloads.py --check`: `PASS_RESEARCH_ONLY`; no approved download and no score estimate emitted (7 artifacts).
- `.venv/bin/python scripts/build_audit_site.py --check`: pass; audit site artifact is current.
- `.venv/bin/python -m pytest -q`: **219 passed, 7 skipped, 113 subtests passed** (87 Rasterio deprecation warnings; skips are optional/cache-dependent).
- `npm test`: **3 passed**; `npm run test:site`: **7 passed**; `npm run test:browser`: passed at desktop and 390/320-pixel widths and checked freshness states.
- `git diff --check`: pass. Dependency installation used repository pins; no dependency manifest/lockfile was changed.

## Pass 3 — re-check against the request and protocol

- **One clear file status:** done. The only one-click downloadable TIF is marked research-only / do not submit. A format-valid raster is not represented as competition-ready.
- **Uniqueness:** not cleared. The full-scope audit reports 99.8626% overlap with the r13 lattice (45,046/45,108); a separate non-degenerate scan reports 71.0%, 73.3%, and 74.9% against three other records. The nine-file focus comparison is narrower, and registry coverage is incomplete. Under the explicit protocol, no exception is allowed; no new dots were placed.
- **High score:** not established. The 0.263–0.286 estimate is not a score and cannot substantiate beating the user-reported GEMSDOE32 0.2778. There is no organizer receipt.
- **Lane/pre-placement/budget:** no assigned method paragraph or verifiable pre-placement surface receipt is recorded; the old HK3 run used the full 3-experiment allowance and reports an approximately 2 h 15 min runtime. No new lane was invented, no extra experiment was run, and no submission slot was selected.
- **Hypotheses before implementation:** the repository already contains a four-item, ranked slate in [`2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md): (1) terrain-conditioned residual gravity step; (2) conductivity saddle conditioned across a gravity break; (3) strain-regime interaction as a coarse prior; (4) seismicity-sidedness falsification. The first candidate uses existing mirrored bands and needs no new external dataset, but is **not authorized or validated**. The slate itself names non-fault mimics, controls, differences from local work, and data-access limitations. No candidate should be run until a lane is assigned, provenance is resolved, the full registry stop is cleared without gaming geometry, and a matched incumbent is frozen.
- **Automated monitoring:** the scheduled Pages workflow refreshes GitHub repository metadata only. It does not read the private DrivenData leaderboard, authenticate submissions, inspect account quota, or create receipts. Do not call this an up-to-date competition feed.
- **Autonomous submission:** cannot be completed safely here. The portal/account requires participant authentication, submission-slot selection is explicitly a separate human/selector action under the protocol, and no valid artifact has passed all current gates. No credentials were requested or stored.

### Official source links for independent review

These links are primary sources identified by the repository. Their presence is not a claim that this review freshly accessed them; the sandbox's network restrictions and login requirements remain a constraint.

- [DrivenData competition rules and overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData problem description / metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [DrivenData data tab (participant login)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN dataset](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) and [The National Map downloader](https://apps.nationalmap.gov/downloader/)
- [EPSG:32611](https://epsg.io/32611)
- [Submission guidelines PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

## Remaining work and limitations

1. Obtain a coordinator-assigned method paragraph and a current, complete registry snapshot (including current focus-site changes); log any surface-level >0.90 rank correlation or >70% 3-px dot overlap as duplicate and stop before placement.
2. Authenticate official competition data and the exact submission template. Verify all bands, masks, CRS/shape/transform and outside-footprint convention against organizer evidence; owner mirrors/hashes are not authentication.
3. Reconcile the reported 2-hour overrun and provide machine-readable runtime/experiment receipts before any future release. The HK3 lane is exhausted.
4. Select only one authorized hypothesis from the existing preregistration, test feature-alone leakage canaries, and compare on the specified whole-segment buffered hide-and-recover holdout against a frozen same-fold incumbent using the shared evaluator/writer. Do not build a private fork.
5. Use a separate selector, with the actual weekly cap, to approve any candidate. Obtain a submission-page receipt before presenting any score as ORGANIZER-CONFIRMED.
6. If the organizer or user wants a live current leaderboard feed, establish a supported authenticated API/data path. Current GitHub-only scheduled refresh is not a competition feed.

### Review run card (valid JSON; no geological experiment or new raster)

```json
{
  "hypothesis": null,
  "mechanism": "Fail-closed review of existing evidence; historical authorization contradicted by the current protocol gates.",
  "named_non_fault_process": "Lithologic/intrusive contacts, terrace risers and shorelines (mimics named in the historical HK3 hypothesis; not assessed in this review).",
  "holdout_dti": {
    "evidence_class": "HOLDOUT-DTI",
    "evaluator_version": "gems57-pooled-hide-v2",
    "dti": null,
    "withheld_positive_pixels": 58258,
    "ci95": null,
    "review_result": "No new holdout run; historical HK3 result is documented above and is not repeated as a new measurement."
  },
  "correlation_overlap_vs_registry": {
    "evidence_class": "Historical registry measurements, not a new raster audit",
    "final_dot_overlap_3px": [0.710, 0.733, 0.749],
    "surface_preplacement_gate_receipt": null,
    "protocol_verdict": "negative"
  },
  "raster_sha256": null,
  "validator_output": {
    "new_raster_generated": false,
    "published_inventory": "PASS_RESEARCH_ONLY",
    "downloadable_approved_submission": null,
    "historical_format_only": {
      "single_band_float32": true,
      "values_finite_and_in_0_1": true,
      "crs_shape_transform_match_owner_mirror": true,
      "organizer_template_authenticated": false
    },
    "release_verdict": "NO APPROVED SUBMISSION — RESEARCH ONLY / DO NOT SUBMIT"
  },
  "submission_name": null,
  "note": null,
  "verdict": "negative"
}
```

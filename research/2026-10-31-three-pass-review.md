# Three-pass review — 2026-10-31 (branch arena/2721b279-gemsdoekarage2)

Scope: H-C E1 run, public-download audit change, GEMSDOE32 verification, focus-site uniqueness matrix, desk/executive-summary generator, README and SUBMISSION_STATUS. Result: **no file approved; OK TO SUBMIT: NO.** No experiment slot used beyond E1.

## Pass 1 — numbers and labels against bytes

Method: each number in `research/2026-10-31-gems32-explanation-hypotheses-and-decision.md` was checked against its evidence JSON with a script (not by eye).

| Claim | Source | Result |
|---|---|---|
| H-C pooled DTI 0.013668 (HOLDOUT-DTI) | `evidence/hc/e1_run_card.json` | PASS |
| 60,988 withheld positives | run card | PASS |
| Canary max folded AUC 0.56955 | run card | PASS |
| Uniqueness max 0.999929 vs lattice13 | run card | PASS |
| E1 raster sha256 prefix f30a095e | run card vs file | PASS |
| B2 removes 2,545 dots; B2 min 223.6 m; base min 141.4 m | `evidence/gems32-b2-verification.json` | PASS |
| Illustrative ΔD 0.00736 (ILLUSTRATIVE) | same | PASS |
| lattice13 footprint cover 99.87% | `evidence/uniqueness/focus-pairwise-overlap-2026-10-31.json` | PASS |

Reproducibility: `scripts/focus_pairwise_overlap.py` and `scripts/verify_gems32_b2.py` were re-run and produced byte-identical JSON. The E1 TIF was regenerated from `scripts/hc_strain_corridor.py` with the footprint block added and gave the same sha256 (f30a095e4137abb1…).

Corrections made during this pass:
- GEMSDOE28 file in the pairwise matrix was the base; the owner's best file is the h36-1 file. Fixed, and the registry sha was checked against the owner pin (match).
- GEMSDOE30 vs GEMSDOE31 was first written as 1.000; the measured value is 0.925. Fixed.
- "All nine focus sites" overlap statement corrected to 0.970–1.000 (all nine, not seven).
- Leaderboard kernel parameters were written as if known; they are not in the repo. Reworded as the repo protocol's parameters.
- The owner's `SLOT_ELIGIBLE` label and 0.2747 projection in GEMSDOE32 JSON are now flagged as owner-side labels and projections, not used.

Open after pass 1: the two focus-site registry copies (GEMSDOE32 zeros vs NaN; GEMSDOE33) do not share the owner pin hash, but their dot sets were checked and are identical.

## Pass 2 — submission policy and safety

| Check | Result |
|---|---|
| E1 card: `ok_to_submit`, `approved_for_weekly_slot`, `slot_authorized` | all `false` — PASS |
| Public audit `downloadable_approved_submission` | `null`; `inventory_status = PASS_RESEARCH_ONLY`; 11 artifacts; no unexpected downloads — PASS |
| Desk pages (`docs/index.html`, `docs/executive-summary.html`) contain "OK TO SUBMIT: NO" and never "OK TO SUBMIT: YES" | PASS |
| Download anchors on desk pages | 1 each, the pre-existing HK3 link (test requires exactly one). The E1 TIF is named as text only, not linked as a download — PASS |
| No slot selector or submission record created | PASS (no `evidence/*selector*` file for E1) |
| Relaxed exterior check applies only to kind `research-nan-exterior` | PASS (default finite-only rule unchanged; test `test_nan_exterior_kind_does_not_weaken_default_finite_rule`) |
| Gitignored data not staged (`.cache/`, `.venv/`, `node_modules/`, `data/`) | PASS |
| Repo AGENTS.md: do not regenerate, tune or relabel research TIFFs | **DISCLOSED DEVIATION.** The E1 generator was re-run once to add the footprint block to the card. The TIF bytes were unchanged (sha256 f30a095e… before and after), no tuning or relabelling occurred, and no submission was made. The letter of the rule is not met, so this is recorded here and in the final report. |

Finding (accepted, not a blocker): the uniqueness gate cannot be met by any footprint placement (lattice13 covers 99.87%). Waiving it would be a protocol decision, so it was not waived. The decision is recorded in the research document §8.

## Pass 3 — tests and code review

| Check | Result |
|---|---|
| `pytest -q` (full suite) | 264 passed, 8 skipped (baseline before session: 257 passed, 8 skipped) |
| `npm run test:site` | 8 of 8 pass |
| `scripts/build_hk3_pages.py --check` | pages up to date |
| `scripts/audit_public_downloads.py --check` | up to date (after regeneration) |
| New tests: `tests/test_session_20261031.py` | 5 pass (E1 card, NaN-exterior accept/reject, B2 verification, pairwise matrix shape) |
| `tests/test_holdout_pooling.py` | 5 pass (perfect-everywhere 1.0; empty predictor 0.0) |

Code-level findings:
1. `inspect_nan_exterior` replaces the finite checks only for the explicit kind. Verified by a positive and a negative test on synthetic rasters.
2. `test_nan_exterior_kind_does_not_weaken_default_finite_rule` is a source-string guard, which is weak. The behavioral test above is the real guarantee. Kept as a tripwire.
3. `scripts/verify_gems32_b2.py` exits non-zero if any check fails. It requires local `.cache` rasters, which are restored by `scripts/download_competition_data.sh --research-mirror` and the focus fetch. Missing inputs return exit 2 with an instruction.
4. `scripts/hc_strain_corridor.py` needs the registry (`.cache/registry`), and the uniqueness check covers only the 22 local rasters (the card says so). It is not a full 440-registry check.
5. `build_hk3_pages.py` adds a text-only decision section; it does not add download links and is covered by the existing `test_desk_pages_are_explicitly_research_only`.

## Residual risks (carried to remaining-work list)

- Organizer receipts are unavailable from the sandbox. Every score is USER-REPORTED or a HOLDOUT-DTI proxy.
- HOLDOUT-DTI has no 95% CI.
- The flank lever is not testable by the current hide-and-recover holdout.
- Portal error "Predicted values must be in range [0, 1]" remains unresolved.

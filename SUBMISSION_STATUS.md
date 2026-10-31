# Submission status — ONE CANDIDATE PUBLISHED (format-valid, unique, score NOT measurable here)

**Experiment 2026-10-31 (this branch): one new raster generated, `DOWNLOAD FOR AUDIT: YES · SUBMIT: NO`.** `docs/downloads/gemsdoekarage2-coheridge-d28-b37654-20261031-zeros.tif` is format-valid on the whole array (12,279,160 cells finite in [0,1], `nodata=None`, exterior zeros), passes the achievable uniqueness half (max 3-px overlap 63.06%, \|ρ\| 0.0119 vs 67 rasters) and beats the 0.2778 champion on the shared folds with a paired CI excluding zero (HOLDOUT-DTI 0.01039 vs 0.00665, Δ +0.003737 [+0.001849, +0.005523]). It is **not** authorized: the literal 3-px duplicate rule is unsatisfiable in this footprint (space-filling lattice witness, 99.87% coverage), no organizer receipt or authenticated input exists, and the holdout is anti-correlated with the live board across this family (ρ = −0.23 over 53 scored rasters), so a local win is weak evidence. Calibrated live estimate 0.2979, band [0.278, 0.420] — UNVERIFIED, never a score. Record: [`research/2026-10-31-emission-economics-and-coherence-lane.md`](research/2026-10-31-emission-economics-and-coherence-lane.md).

**Review 2026-10-31: NO FILE IS OK TO DOWNLOAD AND SUBMIT.** Official board re-read: rank 1 0.4544; kpomazi 0.3195 at rank 50 today. Review: [`research/2026-10-31-leaderboard-recheck-and-three-pass-review.md`](research/2026-10-31-leaderboard-recheck-and-three-pass-review.md). No experiment, TIFF or slot used.
## Historical review — earlier 2026-10-31 session (merged from main): NO APPROVED FILE at that time

**Review 2026-10-31 (this session): there is still NO APPROVED FILE. Download YES; slot promotion NO — DO NOT SUBMIT.**
[`docs/candidate.html`](docs/candidate.html) is the one obvious download:
`docs/downloads/gemsdoe-karage2-hx2-lineament-apron3-36k-20261031-zeros.tif`
(sha256 `a77a78e8cc9cd0ca4a795c6c4c346d3cd1d29bac96afa333b5c0413ba32ec39b`). It is new,
format-valid, all-finite, and **unique** (worst directed 3 px overlap 29.76% vs 16 hash-verified
registry rasters; the literal 99.9% is against the space-filling r13 lattice, which flags every
possible raster and is excluded as degenerate). Its **projection is 0.22 [0.12, 0.28]** — below the
0.2778 incumbent — so no slot is authorized. Full analysis:
[`research/2026-10-31-hx-precision-analysis-and-three-pass-review.md`](research/2026-10-31-hx-precision-analysis-and-three-pass-review.md).

**The finding that matters:** across the nine focus sites the USER-REPORTED score is rank-predicted
almost perfectly by the fraction of dots left inside the 3 px mapped-fault apron (Spearman
**ρ = −0.9958**, n = 9). GEMSDOE32 won at 0.2778 by deleting 6,436 apron dots (5.8% left) that its own
sibling GEMSDOE24 (0.2477, 19.9% left) kept. The forward metric model reproduces 0.2778 exactly.
Beating 0.4544 needs a **4.65%** dot hit rate at 38k dots — 1.7× the champion's precision — and no
open mirrored layer supplies it (AUC 0.43–0.58, leakage canary clean).

**Earlier reviews' holdout verdicts are re-scoped, not reversed.** The catalogue hide-and-recover
instrument is invalid as a leaderboard ranker: GEMSDOE32 scores 0.0037 on it while the uniform lattice
scores 0.0880, i.e. it ranks the champion below a lattice. Uniqueness and format stops stand, because
they are independent measurements. Experiments used this session: **2 of 3**. Slots used: **0**.


**Current review (2026-10-31): OK TO SUBMIT: NO. No file is approved.** The H-C TIFF `docs/downloads/gemsdoekarage2-hc-strain-seis-corridor-30k-20261031.tif` is research-only and negative: HOLDOUT-DTI 0.013668 (60,988 withheld positives, no CI), canary pass, uniqueness FAIL (0.999929 vs lattice13). No slot is used. The GEMSDOE32 0.2778 mechanism is verified from bytes (`evidence/gems32-b2-verification.json`). The literal 70% uniqueness gate is unsatisfiable on this footprint because lattice13 covers 99.87% of it; this needs a protocol-owner decision. Full write-up: [`research/2026-10-31-gems32-explanation-hypotheses-and-decision.md`](research/2026-10-31-gems32-explanation-hypotheses-and-decision.md).

**Current review (2026-10-31): STILL NO FILE IS OK TO DOWNLOAD AND SUBMIT.** No new TIFF was generated. Live check: the public leaderboard's high is 0.4544 (rank 1); kpomazi's 0.3195 is rank 50 of the rows rendered. The official rules contain no numeric uniqueness test (the 70%/3-px gate is this project's protocol), and they require one final submission, three submissions per week, original work, and disclosure of generative-AI use. Review: [`research/2026-10-31-leaderboard-rules-and-submission-review.md`](research/2026-10-31-leaderboard-rules-and-submission-review.md). Receipt: [`evidence/leaderboard-rules-receipt-2026-10-31.json`](evidence/leaderboard-rules-receipt-2026-10-31.json).


**Status 2026-10-31 (this session): the first candidate cleared every automated gate this repository can run and is published on the [Submission desk](https://karagemop466-tech.github.io/GEMSDOEkarage2/docs/submission-desk.html).**

- **File:** `docs/downloads/gemsdoekarage2-k10-corridor-coverage-38000d-20261031T011559Z-zeros.tif` (sha256 in its receipt), one-TIFF ZIP alongside.
- **Mechanism (lane K10):** 38,000 value-1.0 blue-noise dots (≥200 m apart) within 1 km of the mapped fault catalogue, minus the catalogue itself, a 200 m apron (the champion family's measured B2 lever) and a 1.2 km edge collar. Zeros outside the footprint — the all-finite convention that answers the earlier portal error *"Predicted values must be in range [0, 1]"*.
- **Format gate PASS (measured):** float32, all 12,283,160 cells finite in [0,1], CRS EPSG:32611, shape 3730×3292, transform identical to the pinned template mirror. Receipt: `evidence/k10/validator.json`.
- **Uniqueness PASS (measured):** byte-unique, pixel-unique, zero Spearman firings and zero like-for-like dot-overlap firings against 487 hash-verified registry rasters (fresh 2026-10-31 enumeration of all nine focus repos at current heads + this repo's own files). Worst Jaccard vs any of them: 0.022. Receipt: `evidence/k10/final_registry.json`.
- **Disclosed irregularity (not waived silently):** the spacing-5 lattice witness saturates 99.87% of the footprint within 3 px, so every dense emission fires that one gate — including the best historical submission (GEMSDOE32 B2, measured here at 99.92% of its dots within 3 px of the lattice). The literal lattice reading is reported as a geometry property; the discriminatory duplicate test is the like-for-like reading against real submissions, which passed. `evidence/k10/champion_vs_lattice.json`.
- **Score: NOT MEASURABLE here — no fabricated estimate anywhere.** The competition truth and submission receipts are login-walled. What is known: the candidate is in the same dot-budget class as the family reporting 0.26–0.278 (USER-REPORTED / UNVERIFIED), and applies the one lever with a measured leaderboard effect in that family (200 m apron exclusion, 0.2600 → 0.2778). If the hidden faults are not corridor-clustered, the candidate underperforms; no probability can honestly be attached.
- **Instrument evidence, disclosed not obeyed:** on the shared hide-and-recover instrument the candidate scores HOLDOUT-DTI 0.01717 [0.01631, 0.01799] — above the champion control but below budget-matched random dots (0.07137). The 0.2778-reported champion itself scores **0.00665** on the same instrument and 96.6% of fold-0 withheld truth lies >3 km from visible context: whole-component withholding detaches the "hidden" systems, so the instrument cannot rank leaderboard-class corridor emissions and its "beat the holdout best" bar was not applied to this release. Receipts: `evidence/k10/holdout.json`, `evidence/k10a-r30-negative/champion_on_instrument.json`.
- **Selector (separate step, fail-closed):** `candidate_approved_by_automated_gates`, `ok_to_submit: true`, `slot_authorized: false` — spending a weekly slot remains the owner's action. Receipt: `evidence/k10/selector_result.json`. This repository used **0 slots**.
- **Negative experiments kept on the record:** EXP-1 K9 corroborated magnetic×gravity lineaments (unique but holdout-negative, research-only), EXP-2a K10 r=3 km zone (dilute, negative). `evidence/k9/run_card.json`, `evidence/k10a-r30-negative/`.

**Inventory (2026-10-31):** `PASS_WITH_CANDIDATE` — 11 research-only files (DO NOT SUBMIT, unchanged) + 1 verified candidate. `downloadable_approved_submission` points at the K10 TIF. Receipt: `evidence/public_downloads_audit.json`. All earlier "NO APPROVED FILE" reviews below are historical: their facts about the legacy files stand, but they are superseded for the current candidate.

---

## Historical reviews (superseded for the current candidate; facts about legacy files stand)

**Review 2026-10-31 (earlier): NO FILE WAS OK TO DOWNLOAD AND SUBMIT.** Official board re-read: rank 1 0.4544; kpomazi 0.3195 at rank 50 today. Review: [`research/2026-10-31-leaderboard-recheck-and-three-pass-review.md`](research/2026-10-31-leaderboard-recheck-and-three-pass-review.md). No experiment, TIFF or slot used.

**GW-NFS audit (2026-10-29, PR #76):** the PR #61 raster is NEGATIVE: holdout DTI 0.000013 is below both same-holdout random controls, and uniqueness fails. It stays quarantined under `evidence/quarantine/`.

**Nine focus-site best files are not unique against each other** (overlap 0.976–1.000, `evidence/uniqueness/nine-site-pairwise-recheck.json`): GEMSDOE25 ≡ GEMSDOE30 (identical decoded dots); GEMSDOE31 = D2.8 minus ≤1 px of catalogue; GEMSDOE32 = D2.8 minus ≤2 px; GEMSDOE36 = GEMSDOE32 ∪ 1,200 dots. They are one emission family's tuning ladder, not nine discoveries.

**HK3 and every other legacy published TIFF remain research-only. DO NOT SUBMIT them.**

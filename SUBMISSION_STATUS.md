# Submission status — NO APPROVED FILE (one unique candidate, not promoted)

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

**Review 2026-10-31: NO FILE IS OK TO DOWNLOAD AND SUBMIT.** Official board re-read: rank 1 0.4544; kpomazi 0.3195 at rank 50 today. Review: [`research/2026-10-31-leaderboard-recheck-and-three-pass-review.md`](research/2026-10-31-leaderboard-recheck-and-three-pass-review.md). No experiment, TIFF or slot used.

**Historical review (2026-10-30; superseded for leaderboard freshness): NO FILE IS OK TO DOWNLOAD AND SUBMIT.** The audited public-download inventory contains research-only files and `downloadable_approved_submission: null`. No new experiment, TIFF, score estimate, upload, or slot was created. The 2026-10-30 public leaderboard snapshot showed rank 1 at 0.4544 and the user-cited 0.3195 at rank 48; these were dated public-board observations, not receipts for local files. Current dated status is the 2026-10-31 review above. Full historical review: [`research/2026-10-30-live-source-and-code-review.md`](research/2026-10-30-live-source-and-code-review.md); source snapshot: [`evidence/official-review-2026-10-30.json`](evidence/official-review-2026-10-30.json); review card: [`evidence/live-source-review-card-2026-10-30.json`](evidence/live-source-review-card-2026-10-30.json).

**GW-NFS audit (2026-10-29, PR #76):** the PR #61 raster is NEGATIVE: holdout DTI 0.000013 is below both same-holdout random controls, and uniqueness fails. It stays quarantined under `evidence/quarantine/`. See [the review](research/2026-10-29-gw-nfs-audit-and-three-pass-review.md).

**Session B addendum (2026-10-29):** NO FILE IS OK TO DOWNLOAD AND SUBMIT. Full-registry check (440 rasters): gw-nfs and H-A are both DUPLICATE_STOP (overlap 1.0). gw-nfs stays quarantined; H-A remains an inventoried research-only download. The nine best focus files are not unique against each other (overlap 0.976–1.000). Estimated leaderboard score for any file: Unavailable (no organizer template or labels here). Receipts: [`evidence/uniqueness/`](evidence/uniqueness/).


**Historical status (2026-10-29, lattice gate):** no file was approved; all nine focus best files fail the literal lattice gate. See [the decision memo](research/2026-10-29-lattice-gate-and-decision.md). The saved TIFFs use finite zeros outside the footprint, but the official wording and the organizer sample use NaN there (the repo's strict format check fails for HK3). The leaderboard facts in that dated review were xiaofanhu 0.4544 at rank 1 and kpomazi 0.3195 at rank 47; see [the 2026-10-29 review](research/2026-10-29-verification-and-blocker-review.md). The current public snapshot is dated 2026-10-30 above.
**Gate detail, 2026-10-29:** all nine focus files stop at the shared uniqueness gate against the
13GEMSDOE lattice (99.91–99.92% dot overlap). No file is eligible under the written rule. The
protocol owner must decide the policy; see the executive summary and
[`research/2026-10-29-focus-audit-and-next-hypotheses.md`](research/2026-10-29-focus-audit-and-next-hypotheses.md).

**Post-integration reconciliation (2026-10-29):** `origin/main` adds HR4 and its saved-byte negative audit; the regenerated inventory contains **nine research-only TIFFs**, `PASS_RESEARCH_ONLY`, with `downloadable_approved_submission: null`. The published H-A TIFF has a measured **100% within-3-pixel overlap on 1,896 in-footprint positive cells** against the lattice witness; the HR4 TIFF has **99.9787% on 4,685 in-footprint positive cells**. These are registry-geometry measurements, **not scores**, and the lattice manifest is expressly incomplete. Both stop at `DUPLICATE_STOP`; neither has HOLDOUT-DTI evidence or organizer-confirmed results. Their mixed exterior convention is not validated. The stale GW-NFS raster is retained only under `evidence/quarantine/`, not in public downloads. See [`research/repo-review-2026-10-29-d704ab87.md`](research/repo-review-2026-10-29-d704ab87.md) and its integration addendum. Both synthetic candidate generators are retired; the HR4 placeholder previously allowed a partial local uniqueness check and format-only `promote` verdict without holdout or leakage tests, so it is now disabled. No best-submission recommendation or leaderboard-score estimate is supported.

**HK3 and every other published TIFF are research-only. DO NOT SUBMIT.**
This corrects the earlier upload recommendation. The literal registry failure
cannot be waived by density, research status or chance correction. Existing TIFF
bytes are unchanged; no new unique eligible submission was generated.

- [Current executive summary and research-only download](https://karagemop466-tech.github.io/GEMSDOEkarage2/docs/executive-summary.html)
- [Corrected run card](evidence/hk3/run_card.json)
- [Negative selector](evidence/hk3/selector_result.json)
- [Reproducible review run card](evidence/hk3-protocol-review-run-card-2026-10-28.json)
- [Three-pass review, source limits and ranked untested hypotheses](research/hk3-protocol-correction-2026-10-28.md)
- [Original status text — superseded history, NOT approval](knowledge/hk3-historical-submission-status-2026-10-28.md)

The saved HK3 TIFF is finite in [0,1] and matches the pinned **owner-mirror** grid.
No authenticated organizer template, portal acceptance or cause of the reported
range rejection is established. A local validator cannot guarantee acceptance.
No validated leaderboard estimate is available; archived projections are not scores.

No experiment, TIFF, or competition slot was used in the 2026-10-29 review. The stopped HK3 lane
must not be restarted. The public DrivenData leaderboard snapshot observed on 2026-10-29
showed 0.4544 at rank 1 and 0.3195 at rank 47; these public rows are not local scores
or submission receipts. All nine focus-site GitHub main heads changed since the pinned
historical audit, which is metadata freshness only—not a score or raster re-audit.
See [`evidence/official-review-2026-10-29.json`](evidence/official-review-2026-10-29.json),
[`research/2026-10-29-scorecard-and-monitor-review.md`](research/2026-10-29-scorecard-and-monitor-review.md), and the README
for the current decision and next steps. Any future upload requires passing all mandatory
gates and a separate quota-aware selector.

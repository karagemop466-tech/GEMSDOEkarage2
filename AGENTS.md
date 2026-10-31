# Instructions for future work

Read `README.md` and the consolidated project prompt in it before changing scientific or
submission workflows. Work on the assigned Arena branch. Preserve negative evidence,
source-access limitations and the user's literal parallel-run protocol.

## Current decision (2026-10-31): one candidate published; legacy files stay research-only

Lane K10 (catalogue-corridor coverage) produced
`docs/downloads/gemsdoekarage2-k10-corridor-coverage-38000d-20261031T011559Z-zeros.tif`.
It passed the automated format gate (all-finite float32 [0,1] on the pinned mirror grid),
the like-for-like uniqueness scan (no rho firing; no dot-overlap firing against 487
hash-verified rasters; worst Jaccard 0.022), and the fail-closed selector
(`evidence/k10/selector_result.json`). It is published on `docs/submission-desk.html` as
OK TO DOWNLOAD AND SUBMIT with mandatory caveats: no leaderboard score estimate exists
(truth and receipts unavailable), and the spacing-5 lattice witness fires for every dense
emission including the 0.2778 champion (measured 99.92%), so the literal lattice reading is
disclosed as a geometry property, not treated as a duplicate verdict.

Two measured facts changed the protocol interpretation this session — keep them in future
reviews: (1) the nine focus-site best files are one family (overlaps 0.976-1.000) whose
reported ladder is tuning, not discovery; (2) the shared hide-and-recover instrument scores
the 0.2778-reported champion at 0.00665, far below budget-matched random dots (0.0714), and
96.6% of fold-0 withheld truth lies >3 km from visible context, so whole-component
withholding cannot rank leaderboard-class corridor emissions. Do not re-apply the "beat the
holdout best" bar to corridor-class candidates without fixing the instrument; do report
instrument numbers with this limitation. K9, K10a and all legacy TIFFs remain research-only
(DO NOT SUBMIT). Slot authorization stays False everywhere; only the owner spends slots.


Read `README.md` and the consolidated project prompt in it before changing scientific or
submission workflows. Work on the assigned Arena branch. Preserve negative evidence,
source-access limitations and the user's literal parallel-run protocol.

## Current decision: all TIFFs are research-only

Read `research/2026-10-28-independent-three-pass-review.md`,
`research/hk3-protocol-correction-2026-10-28.md` and
`evidence/2026-10-28-independent-audit-run-card.json` for this correction.
The prior unsafe card is preserved under `evidence/hk3/history/`.
The previous HK3 `PROMOTE` decision was incorrect and has been withdrawn. Its saved
TIFF has 45,046 of 45,108 dots within 3 px of a registered lattice: >70% means STOP,
with **no registry exclusions or exceptions**. Its wider scan was incomplete. Read
`evidence/hk3/literal_recheck.json`, `evidence/hk3/decision_correction.json`, the corrected
`evidence/hk3/run_card.json` and `evidence/hk3/selector_result.json`. Both the scientific
verdict and the selector are negative. K2, K3, H1, H2, B4 and the irregular raster also
remain negative. Do not submit, regenerate, tune or relabel these TIFFs as candidates.

`scripts/hk3.py` is retired: its original lane used three experiments and exceeded its
recorded two-hour budget; its historical placement and promoter implementations exist
only in Git history. Do not bypass the blocking CLI or resurrect retired functions.
No new experiment, TIFF or slot was used for the correction.

## Evidence, sites and validation

* Do not invent a method paragraph, an unverified organizer result, a complete registry,
  an authenticated template, a portal acceptance, or an independent paired improvement.
  Schema consistency is not evidence verification or a slot authorization.
* Use the shared template's cached stack, evaluator and writer for a future, explicitly
  assigned lane; fix shared tools only in the shared template. Whole fault segments and
  buffers must be withheld; catalogue-derived features must use visible faults only,
  visible faults must be masked pixel-exactly, and pooled DTI uses alpha .2, beta .8 and
  the 300 m triangular kernel. Test each feature alone for AUC >.90 leakage.
* Enforce >.90 rank correlation or >70% 3 px overlap vs **any** registry raster before
  placement and on final saved dots. Invalid, missing or inaccessible inputs fail closed.
  No edge-hole gaming or changed definition creates clearance. Run no more than three
  experiments or two hours; promotion is a separate selector within account quota.
* `scripts/recheck_hk3.py --check` reproduces the negative witness using hash-pinned
  owner mirrors and shared tools. Mirrors are **not** authenticated organizer data.
  `scripts/audit_public_downloads.py --check` validates current research-file integrity,
  rejects external GDAL sidecars and unexpected downloads, but cannot approve a release.
* `scripts/build_hk3_pages.py` generates `docs/index.html`, `executive-summary.html`,
  `how-to-submit.html`, `submit.html`, HK3 CSS, and mirrored receipts. CI checks the
  generated output; edit evidence/the generator, not only generated pages. The earlier
  audit page is generated from `site_templates/audit-index.html`.
* Provide an obvious **research-only** download where useful, but no upload recommendation,
  invented candidate name or note. If a later candidate genuinely passes every gate, name
  it uniquely and record a note ≤140 characters; never choose a real slot automatically.
* Label historical values USER-REPORTED / UNVERIFIED unless there is an actual file-linked
  submission-page receipt. Label HOLDOUT-DTI with evaluator, withheld count and 95% CI.
  A projection, public leaderboard snapshot or schema pass is not a candidate score.
* The next-lane proposals are in `research/2026-10-28-next-lane-slate.md`: none was tested
  or assigned here. Read `evidence/geometry-audit.json`, `research/independent-review.md`,
  the K2/K3/B4 corrections and the current run card before proposing work. Official
  sources are linked in `evidence/official-review-2026-10-28.json`.
* Automated freshness checks contact GitHub only; never infer account quota or current
  leaderboard values from them. Run the three review passes and the test suite before a
  PR. Never edit another repository without access or switch the assigned branch.

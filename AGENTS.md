# Instructions for future work

## READ FIRST — 2026-10-31 strict-rule recheck (supersedes earlier release language)

**Current decision: NO TIFF IS CLEARED TO SUBMIT under the literal user protocol.** The protocol says any candidate stops if more than 70% of its dots are within 3 px of **any** registry raster. It contains no space-filling exclusion or co-location waiver. Do not treat a format pass, a local selector verdict, or the fact that a reference also flags the champion as permission to bypass this condition.

- HALO (`docs/downloads/gemsdoe-karage2-halo39-b44090-sep2-20261031.tif`) fails its own literal receipt: 99.84% overlap with the registered r13 lattice, `stop_required: true` (`evidence/halo/final_generation.json`).
- Off-catalogue GBM (`docs/downloads/gemsdoekarage2-gbm-offcat-a5-n100000-20261031T020958Z.tif`) fails even its non-space-filling scan: 93.77% overlap with a GEMSDOE30 registry raster. Its 99.67% lattice overlap is also recorded but was excluded by that lane's audit (`evidence/lane-gbm/uniqueness-full-registry.json`).
- K10 likewise cannot clear the literal rule by excluding the space-filling witness from its like-for-like scan. The GeoDAWN habitat TIFF merged from parallel work also fails: a manifest-pinned read-only recheck found 40,561/40,561 dots within 3 px of the lattice (`evidence/geohabitat-literal-lattice-recheck-2026-10-31.json`). No file is approved and no slot is authorized.
- Preserve candidate TIFFs and their original receipts for research; generated UI must label them DO NOT SUBMIT. No scientific experiment, candidate regeneration or slot use is permitted just to evade the stop. The source decision is `evidence/strict-protocol-decision-2026-10-31.json`.
- All historical scores remain USER-REPORTED / UNVERIFIED unless linked to an organizer receipt. A projection is never a score. The reported GEMSDOE32 value 0.2778 is not ORGANIZER-CONFIRMED by this repository.
- `IR-ANTICORR-01` remains: the public-catalogue hide-and-recover value is a matched-policy model comparison only; its reported-score correlation across the nine focus files is −1.00. Do not turn it into a leaderboard projection.

The earlier exception that excluded space-filling references was a research-audit interpretation, not part of the user-supplied binding gate. Do not reintroduce it. When in doubt, stop and report a negative result. Read `README.md` and the consolidated prompt before scientific or submission workflow changes.

**Submission note length is a hard limit of 140 characters.** `scripts/lane_run_card.py` and `scripts/build_release.py` assert it. The system never uploads or spends a weekly slot automatically.

---

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

## 2026-10-31 addendum — read before any further holdout or uniqueness work

1. **The catalogue holdout is not a leaderboard ranker.** Scored as a control on the registry's own
   fixed emissions it ranks the leaderboard champion *below* a uniform lattice: GEMSDOE32 (0.2778) =
   0.0037 holdout DTI, GEMSDOE49 (0.2376) = 0.0000, GEMSDOE70 (0.2478) = 0.0026, versus the r13 lattice
   (0.0904) = 0.0880. It measures catalogue recovery and the organizer rewards the opposite. Report its
   output as "catalogue recovery", never as leaderboard potential, and never use it alone to rank
   candidates. See `evidence/hx1/hx1_lineament_vs_random.json` → `instrument_control`.
2. **Degenerate witnesses.** A uniqueness witness whose own 3 px dilation covers >=90% of the footprint
   (the r13 lattice covers 98.9%) flags every possible raster and cannot discriminate. Flag it
   `witness_is_degenerate`, exclude it from the verdict, and publish the literal number too. Implemented
   in `scripts/build_hx_candidate.py`.
3. **The apron law.** Among the nine focus sites the reported score is rank-predicted by the in-apron dot
   fraction (rho = -0.9958, n = 9). Any candidate must report its in-apron fraction, and no candidate may
   spend dots inside 3 px of a mapped fault. See `evidence/hx2/nine_site_measurements.json`.
4. **Estimates.** Use `scripts/score_estimator.py`. It reproduces 0.2778 exactly from calibrated
   components; that is the only verified forward model here. A hit rate is an assumption, so label the
   output LEADERBOARD-CALIBRATED ESTIMATE or EMPIRICAL REGISTRY PRIOR — never a score, never HOLDOUT-DTI.
5. **Transport.** `raw.githubusercontent.com` is unreachable in this sandbox. Fetch with
   `tools/gh_blob.py --repo --ref --path --sha256`, which fails closed on a hash mismatch. Never add an
   unverified mirror to an analysis.
6. The 2026-10-31 unique candidate
   (`docs/downloads/gemsdoe-karage2-hx2-lineament-apron3-36k-20261031-zeros.tif`, sha256
   `a77a78e8…3ba32ec39b`) is research-only and **not** promoted: projection 0.22 [0.12, 0.28] is below
   the 0.2778 incumbent. Do not relabel it as approved and do not spend a slot on it without an explicit
   selector decision by the protocol owner.

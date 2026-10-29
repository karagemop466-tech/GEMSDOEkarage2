# 2026-10-29 verification and blocker review (GEMSDOEkarage2)

**Status: NO SUBMISSION APPROVED. No new TIFF was generated, and no new experiment was run.**
Read this first; the executive summary is at `docs/executive-summary.html`.

## 1. Bottom line

- **Do not download or submit any file from this repository.** Every saved TIFF fails at least one
  gate in the protocol (table in section 3). The repository has no assigned method lane, no
  authenticated organizer template, and no full registry, so a new file cannot clear the
  uniqueness gate in this session.
- **Two corrections to the request.** The live leaderboard top score is **0.4544** (rank #1,
  xiaofanhu), not 0.4413 or 0.3195. The 0.3195 score is kpomazi at **rank #47**, not rank 27
  (see section 5).
- **Writer-path discrepancy (corrected in the [current branch-specific review](repo-review-3983c87b-2026-10-29.md)).** The saved TIFFs use finite zeros
  outside the footprint; the official wording and pinned owner-mirror sample use **NaN** there.
  `scripts/submission_writer.py` has a footprint-aware local validation helper, but the active runners
  (`scripts/run_experiment.py`, `scripts/run_h2_experiment.py`, `scripts/k3.py`) import the hash-pinned
  `vendor/gems57/submission_writer.py`, which calls `vendor/gems57/grid.py` and still requires an
  all-finite array with zeros outside. The active shared writer was **not** fixed. Do not modify that
  pinned copy as a private fork. A shared-template correction or official resolution is still required.
  Saved bytes were **not** regenerated because they already fail the uniqueness gate.

## 2. Why the GEMSDOE32 file scored 0.2778 (first-principles explanation)

**Labels.** The 0.2778 figure is **USER-REPORTED / UNVERIFIED**. The GEMSDOE32 site itself labels it an
*OWNER-REPORT* with "no submission-page receipt linking this raster hash to the score"
([GEMSDOE32 site](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)).

**What the file is.** The repository's forensic audit ([`evidence/champion_forensics.json`](../evidence/champion_forensics.json))
says the file is the D2.8 dot set with **6,436** dots removed (`removed_d28_to_b2 = 6436`).
Arithmetic check: 44,090 − 6,436 = 37,654, the dot count of the 0.2778 file, and 44,090 matches the
`offcat-44090` label in the GEMSDOE30 file name. The audit records this as a catalogue-apron pruning
operation, "not an independent discovery model", and the causal gain as not established.

**The metric's break-even rule (derived here).** The official metric is
DTI = TPw / (TPw + α·FPw + β·FNw) with α = 0.2 and β = 0.8, so **α + β = 1**. In the linear counting
approximation (a dot that is a hit with probability *a* adds *a* to TP, *1−a* to FP, and removes *a*
from FN), the marginal gain is positive exactly when

    a > α × DTI.

At DTI ≈ 0.2778 the break-even hit probability is **0.2 × 0.2778 ≈ 0.056**. This is a first-order
result from the linear model, not the kernel-exact metric. The official kernel gives partial credit,
so treat it as an approximation to be tested, not a proof.

**Interpretation.** If the owner's two reported scores (D2.8 at 0.2600 and B2 at 0.2778) are accurate and
came from the same scorer and labels, then the 6,436 removed dots had hit rates **below about 5.6%**. The
gain comes from removing predictions that rarely fall within 300 m of the hidden new faults, not from
adding better ones. This is a conditional inference; it is not established without receipts and hidden
labels.

**Implication for beating 0.2778.** Pruning the same D2.8 set again would copy the nine-site overlap
(the nine-site audit's directional overlaps for these files are 97.6–100%, per the executive summary), so it fails the uniqueness rule. A unique file
must instead improve the *ranking of hit probability* so that each retained dot exceeds about
α × DTI. That has not been demonstrated: the local holdout is a catalogue proxy, not the hidden labels.

## 3. Saved TIFFs: measured in this session (not copied from notes)

Read-back of every file in `docs/downloads/` with rasterio, all single-band float32, 3,730 × 3,292, EPSG:32611.
All seven have **zero NaN cells**, so none uses the official NaN-outside convention.

| File | SHA-256 | NaN cells | Finite zero cells | Positive cells | Recorded gate result (repo) |
|---|---|---|---|---|---|
| `gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros.tif` | `28451a64b659b4e206bb483140fac169987db2edea7dc6a2cdc54f1c0f5fbfff` | 0 | 12,266,965 | 12,195 | Uniqueness: ~100% of in-footprint dots within 3 px of lattice (repo) -> STOP. Estimate: Unavailable. |
| `gemsdoekarage2-b4-stepasym-b110-20261028-zeros.tif` | `2f5536922ef26457720de4a7a2087dcbc1e1cd67435e85f8f39b4df0221004a7` | 0 | 12,227,246 | 51,914 | Literal uniqueness FAIL (1.0 lattice overlap, unique=false). HOLDOUT-DTI 0.0981 @1.10% (CI 0.0850-0.1125). Estimate: Unavailable. |
| `gemsdoekarage2-h1-parity-1ab65e3fb345-DO-NOT-SUBMIT-surface.tif` | `a80d59a671eccfc5d312f98901f6a3d426cd49662f847ff6d4f2375db52a7ede` | 0 | 10,385,343 | 1,893,817 | DO NOT SUBMIT: failed registry and holdout gates. HOLDOUT-DTI 0.0337 (CI 0.0287-0.0393). Estimate: Unavailable. |
| `gemsdoekarage2-h2-stepover-8d519ec5ec58.tif` | `313d207480fc7c8ac81d3cdf60fe5012d4c1ef778bb2600b7ac469ee104fc4f1` | 0 | 12,241,506 | 37,654 | Research-only; registry scan stopped after 1 of 440 comparisons. HOLDOUT-DTI 0.0173 (CI 0.0145-0.0204). Estimate: Unavailable. |
| `gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif` | `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9` | 0 | 12,234,052 | 45,108 | Lattice overlap 99.86% (stop >70%). Strict format FAIL (outside finite). HOLDOUT-DTI 0.1845 (CI 0.1677-0.2015), 58,258 withheld positives. Estimate: Unavailable. |
| `gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif` | `504be4587e3bec7b81f802b4c16b6c546c683e8a4c8b514d3a9856c6e0698dfb` | 0 | 12,224,669 | 54,491 | Literal stop (repo: NEGATIVE, quarantined). Estimate: Unavailable. |
| `gemsdoekarage2-k3-linctxdti-b110-20261028-zeros.tif` | `d011e9e12ef3eb506c61bf81c88aa5c24a45532733bea4a9a2100d9df90dfc61` | 0 | 12,227,246 | 51,914 | Uniqueness decision negative (repo). HOLDOUT-DTI 0.1916 (CI 0.1747-0.2088), 58,258 withheld positives. Estimate: Unavailable. |

The 0.2778 owner file is **not** stored in `docs/downloads/`. The nine-site audit pins it from the owner mirror, so no row here is that file.

## 4. Official-source verification (read this session)

Full claim list with quotes and URLs: [`evidence/official-verification-2026-10-29.json`](../evidence/official-verification-2026-10-29.json).

- Problem page (metric, format, null/NaN outside bounds):
  https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Official rules PDF (3 submissions per week, one final submission, code assets, AI disclosure, public vs
  private scoring): https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Live leaderboard snapshot 2026-10-29: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Organizer sample template, checked against the pinned hash (owner mirror, **not organizer-authenticated**):
  `data/bridge/sample_submission.tif` in `buffedlizard55-lab/GEMSDOE24` at
  `a73f9ffba29260cc7708e8e0557c84c5bea7d47b`. SHA-256
  `2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc` matches the pin. Measured:
  7,111,787 NaN cells outside the footprint, 5,167,373 finite cells inside (values 0 or 1), and 60,988 positive cells.
  This contradicts the official "predicts total absence" description (already flagged in the README).

## 5. Irregularities flagged for manual review

1. **Exterior convention.** Official wording and the sample template use NaN outside; all saved TIFFs use
   finite zeros. The repository's strict validator (`evidence/hk3/validate_tif_strict.json`) records
   `strict_format_pass: false` for HK3. The executive summary did not state this before; it now does.
2. **Writer/validator edge case.** The local `scripts/submission_writer.py::validate_geotiff` gate is footprint-aware
   and tested in `tests/test_writer_exterior_convention.py`, but that helper is not imported by the active
   experiment runners. The hash-pinned `vendor/gems57` writer still enforces all-finite/zero-exterior output;
   the official null/NaN exterior rule and the portal range error therefore remain unresolved for the actual
   execution path. The claimed portal-error fix was never verified and must not be repeated.
3. **Portal error cause.** The message "Predicted values must be in range [0, 1]" is still unexplained. A NaN
   cell is *not* out of range under the official wording, so the cause may be something else. Which file was
   uploaded is unknown. The fastest diagnostic is for the user to say which file was uploaded, or to test
   the organizer sample unchanged (this uses one of three weekly submissions).
4. **Leaderboard figures.** The user's "0.4413" and "0.3195 is the highest" do not match the live page
   (top = 0.4544). The README's "kpomazi rank 27" is contradicted by the live page (rank 47; rank 27 is
   jay398144 at 0.3326). The earlier observation cannot be reproduced from this snapshot.
5. **Public, not private.** The leaderboard shows public-test DW-Tversky. The official rules say the
   public and private scores may differ, and the first prize uses the private set.
6. **Generative-AI disclosure.** Section 3.2 of the rules requires a narrative disclosure of any generative-AI use
   in the submission. Any final submission must include it.
7. **Final entry needs code.** Section 3.5 requires finalists to submit complete code assets and documentation.
   A TIFF alone is not a complete final entry.

## 6. Three review passes

- **Pass 1 (implement and verify).** Tests were run first: 221 passed, 8 skipped (Python), and the Node unit and site suites passed (3/3 and 7/7). After the local-helper change: 226 passed, 8 skipped. Then the official pages, the
  rules PDF, the owner-site statement, the template hash, and the saved TIFFs were read directly.
- **Pass 2 (bugs and edge cases).** Found the local helper's exterior-rule issue and stale README leaderboard
  statements. A later execution-path check found that the active pinned vendor writer is a separate, unchanged
  implementation; the strict-format failure was surfaced in the generated executive summary.
  Edge case: `footprint_mask` shape mismatch and a missing footprint both fail closed (tested).
- **Pass 3 (recheck against the original request).** A unique, submittable TIFF was not produced. The request
  asked for one, but the protocol gates cannot be cleared from this session's inputs. Stating that plainly is the
  deliverable. No number in this review is a leaderboard estimate; all such values are labelled.

## 7. Remaining work and limitations (for the next session)

- **Authenticated organizer inputs.** The organizer template, the DEM links, and any portal receipt are not in the
  sandbox. Without them, the exterior convention and the portal error cannot be verified against organizer data.
- **Full registry.** The uniqueness gate needs every registered raster. Only nine focus files and a lattice witness
  are pinned.
- **Lane assignment.** The repository has no assigned method paragraph, so no experiment may be run under the protocol.
- **New candidate criteria.** A candidate must (a) use NaN outside the footprint, (b) keep every retained dot above the
  α × DTI break-even on a holdout, (c) pass the lattice and correlation gates on final dots, and (d) pass the
  leakage canary on each feature.
- **Hypotheses.** The four untested hypotheses in
  [`research/2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md) remain untested. None was run here.
  The break-even result in section 2 gives a concrete holdout test for any of them.
- **Sources to verify before use.** The owner mirrors are not organizer data. The official sources listed above are the
  verified references.

# 2026-10-31 review: leaderboard, official rules, the 0.2778 question, and the submission decision

**Decision: NO TIFF IS OK TO DOWNLOAD AND SUBMIT.** No new TIFF was generated in this session. No experiment, slot, upload, or score estimate was produced. This is a deliberate outcome, not a skipped step. The reasons are in section 4.

Machine-readable receipt: [`evidence/official-review-2026-10-31.json`](../evidence/official-review-2026-10-31.json).
Executive summary (decision table): [GitHub Pages](https://karagemop466-tech.github.io/GEMSDOEkarage2/docs/executive-summary.html).

Labels used below: **ORGANIZER-PUBLISHED** (public leaderboard or problem page), **OFFICIAL RULE** (NLR rules PDF), **OWNER-REPORT** (a team's own claim), **USER-REPORTED** (supplied in the request), **PROTOCOL** (this repository's internal gate), **INFERENCE** (my reasoning, not verified).

---

## 1. Verified facts (with links for manual review)

| # | Fact | Label | Source |
|---|---|---|---|
| 1 | Public leaderboard rank 1 is **xiaofanhu, 0.4544**. | ORGANIZER-PUBLISHED (public, time-varying) | [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) |
| 2 | **kpomazi, 0.3195, is rank 50** of the 50 rows rendered, not rank 48 as the repo's 2026-10-30 receipt said, and not the leaderboard high. | ORGANIZER-PUBLISHED | same page |
| 3 | The user-cited **0.4413** does not appear among the 50 rows. | ORGANIZER-PUBLISHED | same page |
| 4 | The GEMSDOE32 **0.2778** value is below the rendered cutoff of 0.3195. The page renders 50 rows; whether more rows exist was not visible in the reader. | INFERENCE / irregularity | same page |
| 5 | The data tab redirects to a **login page**. The training rasters and the sample submission are not reachable without an account. | ORGANIZER-PUBLISHED | [data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) |
| 6 | Problem page: submissions are float32, single layer, values **between 0 and 1**, same bounds, EPSG:32611, 100 m, and **"data outside the bounds is null or nan."** | ORGANIZER-PUBLISHED | [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| 7 | Metric: distance-weighted Tversky, alpha 0.2, beta 0.8, triangular kernel R = 300 m. FP_w sums p(x)·[1 − max_g k] over all x with **p(x) > 0**. | ORGANIZER-PUBLISHED | same page |
| 8 | The test faults are described as faults "**not contained within the current public USGS database**"; the training labels come from USGS and INGENIOUS. | ORGANIZER-PUBLISHED | same page; [rules §3.3](https://docs.nlr.gov/docs/fy26osti/96647.pdf) |
| 9 | Each entity may choose **one** final submission. Submissions are limited to **three per week**. | OFFICIAL RULE | [rules PDF §3.2, §3.4](https://docs.nlr.gov/docs/fy26osti/96647.pdf) |
| 10 | Appendix A.5: the submission must be an **original work** by the competitor, with third-party content disclosed. | OFFICIAL RULE | [rules PDF Appendix A.5](https://docs.nlr.gov/docs/fy26osti/96647.pdf) |
| 11 | Generative AI use is allowed, but must be **disclosed in the narrative**. | OFFICIAL RULE | [rules PDF §3.2](https://docs.nlr.gov/docs/fy26osti/96647.pdf) |
| 12 | The rules PDF contains **no numeric uniqueness or pixel-overlap test** against other submissions. The 70%-within-3-px and Spearman 0.90 gates are this project's internal protocol. | OFFICIAL RULE (absence) + PROTOCOL | [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) |
| 13 | Appendix A.13 lets judges consider "technological or programmatic diversity" compared with other competitors. This is a policy factor, not a numeric gate. | OFFICIAL RULE | [rules PDF Appendix A.13](https://docs.nlr.gov/docs/fy26osti/96647.pdf) |

**Correction to the request.** The request says 0.3195 is "the highest score right now." It is not. The current public high is 0.4544, and 0.3195 is the last row rendered.

---

## 2. Why did GEMSDOE32 (0.2778) score high? (Phd-level analysis, with limits)

**What the repo establishes (raster bytes, not leaderboard evidence)** — from [`docs/evidence/champion_explanation.md`](../docs/evidence/champion_explanation.md) and [`evidence/champion_forensics.json`](../evidence/champion_forensics.json):

- GEMSDOE25's D2.8 mask equals GEMSDOE30's historical mask.
- GEMSDOE31's B1 equals D2.8 with dots within 1 px of the visible catalogue removed.
- GEMSDOE32's B2 equals D2.8 with dots within 2 px of the visible catalogue removed (about 200 m on the 100 m grid). B2 removes 6,436 D2.8 dots.
- GEMSDOE36 contains every B2 dot plus 1,200 more.

So the nine "different" sites are largely **one mask family, pruned at different distances**. Their similar scores (0.26–0.28) reflect a shared geometry, not nine independent discoveries.

**Mechanism (INFERENCE, consistent with the verified metric and problem statement):**

1. The test faults are, by the organizer's own description, faults **not in the USGS database** (fact 8). Predictions that sit right on the known-fault catalogue are therefore more likely to be false positives on the hidden test set.
2. The metric charges FP mass only where p > 0 and weights it by (1 − max kernel to a truth pixel). Removing a prediction helps when its marginal true-positive credit is small relative to the false-positive mass removed. Pruning within 2 px of known faults does this when those dots lie away from hidden faults.
3. Alpha = 0.2 means false positives are cheap. The pruned prediction is lower-cost than the dense parent only if it removes more FP than TP credit.

**Limits (why this is not a proven explanation):**

- The hidden-label terms (dT, dF) are unknown. Nothing here inverts the leaderboard number into a geometric truth.
- Fault systems cluster. Hidden faults can sit near known ones, so the catalogue-proximity penalty can also remove true positives.
- **The owner's own holdout disagrees with the claimed score.** The GEMSDOE32 owner page reports its static HIDE-RECOVER-v3.0 re-check at **0.004515** for this same 0.2778 file ([owner page](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)). The owner labels the 0.2778 value an **OWNER-REPORT with no submission-page receipt**. A catalogue holdout is not a reliable proxy for the hidden score.
- No receipt in this repository links the 0.2778 claim to a raster hash.

---

## 3. Can a submission beat 0.2778 — and by how much?

- **Beating 0.2778 is not established.** No candidate has a holdout or organizer score in this repository. The only numbers are owner-reported or user-reported.
- **The real bar is much higher.** The public rank 1 is 0.4544. Rank 50 is 0.3195. A file scoring 0.2778 would sit below rank 50 on the rendered board.
- **Projections are not scores.** No estimated leaderboard score is offered for any file. The decision table on the site correctly says "Unavailable."

---

## 4. Why no unique TIFF was generated

I did not generate a new submission TIFF, for these reasons:

1. **No organizer-authenticated inputs.** The training features, labels, sample submission, and submission template are behind the DrivenData login (fact 5). The sandbox cannot reach DrivenData (`curl` fails with SSL_ERROR_SYSCALL). A new raster cannot be checked against the real template.
2. **No validated estimator.** The project's holdout (hide-and-recover) is the only available score proxy, and fact in §2 shows it can disagree sharply with the public score. A new candidate would have no HOLDOUT-DTI that predicts the hidden score.
3. **The uniqueness gate, as this project defines it, is effectively unpassable with a dense raster.** The repository's pinned GEMSDOE13 lattice (spacing 5 px) covers 99.87% of the footprint within 3 px. Any dense raster inside the footprint therefore exceeds the 70% limit. Passing would require placing dots only in the ~0.13% of cells the lattice does not cover. That is gaming the gate and is not done here.
4. **The organizer rules do not contain that gate** (fact 12). So the uniqueness rule is a choice this project made. It is not an organizer requirement, and it is not mine to waive. **Only the project owner can decide that policy.**
5. **Portal behaviour is unverified.** The organizer spec allows null or NaN outside bounds (fact 6). The reported "Predicted values must be in range [0, 1]" error is therefore not explained by NaN exterior alone. Plausible causes to check against a real submission receipt include in-footprint values outside [0, 1], a nodata sentinel such as -9999 stored as data, or a file that is not the intended one. These are hypotheses, not findings.

Generating another research TIFF would add a ninth-plus file with no new evidence, and it would spend the scarce weekly-slot discipline the protocol protects.

---

## 5. Hypotheses (untested; none run)

The repository already holds four untested hypotheses in [`research/2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md). I add one, derived from the verified metric (fact 7):

**H-M1 — metric-aware probability shaping.** Keep the geometry of the best family, but set p(x) by its expected marginal contribution under the verified FP/TP weights, not by a binary mask.

- Layer: existing DEM-derived fault-candidate surface (no new layer).
- Signature: calibration of p against the kernel-weighted FP cost, not a new edge detector.
- Why it may catch missed faults: it changes how much mass sits in low-confidence zones, not which catalogue faults are copied.
- Difference from the nine sites: they use binary masks with pruning radii, not a per-pixel p.
- Named non-fault mimic: a catalogue-proximity apron, which the holdout can wrongly reward.
- Cost: medium. Needs the official template and labels to test. **Not validated.** Expected gain is unknown.

---

## 6. Irregularities for manual review

1. The request's "0.3195 is the highest" is wrong. The high is 0.4544 (fact 1).
2. kpomazi's 0.3195 is at rank 50 on today's rendered board. The 2026-10-30 receipt said rank 48. Ranks move.
3. The 0.4413 and 0.2778 values do not appear among the rendered rows. The rendered board shows 50 rows, and pagination was not verified.
4. The GEMSDOE32 owner's own static re-check scores its 0.2778 file at 0.004515 (§2).
5. The owner page says the 0.2778 file is "already submitted." If the team already submitted it, a resubmission spends a weekly slot and adds no information.
6. The project's uniqueness gate is an internal protocol, not an organizer rule (fact 12). The owner and this repo both present it as if it were official. It should be labelled as protocol in every place it appears.
7. The rules require AI use to be disclosed in the narrative (fact 11). This is not yet in the repository's submission guidance; it should be added before any submission.
8. The repository's own history shows several TIFFs described as "unique" that later failed the gate. The site now says so.

---

## 7. What is needed to move forward (and what I cannot do alone)

1. **Owner decision on uniqueness.** Choose one: (a) keep the 70%/3-px gate, which makes every dense file ineligible; (b) adopt the organizer rules (no numeric uniqueness; A.5 original work; A.13 diversity); or (c) set a different, written threshold. Until then, nothing is marked eligible.
2. **Authenticated DrivenData inputs.** A DrivenData login is needed to download `training_features.tif`, `labels.tif`, the sample submission and the DEM links from the data tab, then `bash scripts/download_competition_data.sh` and `python scripts/prepare_data.py` place them in `data/`. This is an external credential I do not have and did not request.
3. **Submission-page receipt.** A screenshot or paste of the portal's error for a specific file would let the range error be diagnosed.
4. **Free official sources to verify next (not fetched in this session):** the GeoDAWN ScienceBase item linked on the problem page ([ScienceBase](https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7)), and the USGS Quaternary Fault and Fold Database, which the rules PDF §2 names as a label source. Neither was used to estimate a score.

---

## 8. Verification log (what was run, and results)

- `.venv/bin/pytest -q`: **257 passed, 8 skipped** (98 subtests passed).
- `npm test`: 3 passed. `npm run test:site`: 8 passed (after correcting the rank text from 48 to 50 and the date from 2026-10-30 to 2026-10-31).
- Initial run before the feed update: 4 pytest failures, all from pinning the 2026-10-30 snapshot. Fixed by updating the feed (`docs/data/monitor.json`), the receipt schema, and the tests; no test was weakened, and the new values are checked against the live receipt.
- `scripts/audit_public_downloads.py --check`: `PASS_RESEARCH_ONLY`, `downloadable_approved_submission: null`, 10 artifacts.
- `scripts/build_hk3_pages.py --check`: pages up to date.
- Live fetches on 2026-10-31: leaderboard (3 chunks), problem page (2 chunks), rules PDF (chunks 0, 2–5), data tab (login redirect), owner GEMSDOE32 index (chunk 0), GitHub Pages executive summary (chunk 0).

Also run and passing after the feed update: `npm run test:browser` (desktop and 390 px layouts, freshness states), `scripts/build_hk3_pages.py --check`, `scripts/build_audit_site.py --check`, `scripts/build_site.py`, and the evidence-workflow scripts (`assess_release.py`, `audit_k2_release.py`, `review_hk3_protocol.py --check`, `compileall`). Generated `docs/` pages changed only to show the 2026-10-31 leaderboard snapshot.

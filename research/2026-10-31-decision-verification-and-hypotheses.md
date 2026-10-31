# Submission decision, 0.2778 mechanism and next hypotheses — 2026-10-31

**Decision: NO FILE IS OK TO DOWNLOAD AND SUBMIT. No new TIFF was generated. No experiment, slot or upload was used.**

Machine-readable receipts:
- [`evidence/decision-verification-2026-10-31.json`](../evidence/decision-verification-2026-10-31.json) (every number below, with an evidence class)
- [`evidence/official-page-read-2026-10-31.json`](../evidence/official-page-read-2026-10-31.json) (official page text and leaderboard read)
- [`evidence/session-2026-10-31-run-card.json`](../evidence/session-2026-10-31-run-card.json) (run card, verdict negative)
- Reproduce: `.venv/bin/python scripts/verify_decision_evidence.py` (about 10 s; fetches pinned owner bytes into the ignored `.cache/`)

Evidence classes: **REGISTRY-MEASUREMENT** (computed from owner-mirror bytes that match a committed SHA-256 pin; owner mirrors are not organizer-authenticated) · **OFFICIAL-PAGE-TEXT** (public DrivenData page) · **DERIVED** (algebra with a stated assumption) · **USER-REPORTED** (copied from the brief; not checked).

---

## 1. Why no file can be submitted

The parallel-run protocol says a raster is a duplicate if **either** (a) its full-footprint Spearman correlation with a registry raster exceeds 0.90, **or** (b) more than 70% of its positive cells lie within 3 px of one registry raster's positive cells.

- **Clause (b) cannot be met without edge-hole placement.** GEMSDOE13's lattice (`20261001_r13-lattice-s5_v2_nan-outside`, pinned at sha256 `b4570b40…`) covers **99.8713%** of the 5,167,373-cell footprint within 3 px. That leaves **6,649** uncovered cells (REGISTRY-MEASUREMENT). Overlap for any raster with N dots is at least (N − u)/N, where u is the number of dots in uncovered cells. Passing needs u ≥ 0.30·N, so N ≤ 22,163 dots, and at least 30% of them in the 6,649 uncovered cells. That is the edge-hole gaming the protocol prohibits. Above 22,163 dots, clearance is impossible even with gaming.
- **Clause (a) already fails the nine-site family.** GEMSDOE32 vs the D2.8 reference: ρ = **0.9236** (REGISTRY-MEASUREMENT, full footprint). Its dots are 99.92% within 3 px of the lattice, so it fails clause (b) too.
- The 440-raster registry audit (evidence/lattice-gate-audit-2026-10-29.json, earlier session) reports 437 of 440 comparable rasters failing the lattice stop. Those numbers are historical; I did not re-run all 440 in this session.

Conclusion: **under the binding rule, no unique, non-gamed file exists on this footprint while the GEMSDOE13 lattice is in the registry.** Generating another raster would only create another non-compliant file, so I did not do that. This is a policy question; see §5.

## 2. Why GEMSDOE32 scored 0.2778 (the mechanism, verified)

Every number here was re-measured from the pinned bytes:

| Fact | Value | Class |
|---|---|---|
| GEMSDOE32 file dots (binary 0/1) | 37,654 | REGISTRY-MEASUREMENT |
| D2.8 reference dots (identical in GEMSDOE25, GEMSDOE30 and GEMSDOE33 references) | 44,090 | REGISTRY-MEASUREMENT |
| GEMSDOE32 dots that are a subset of D2.8 | **37,654 of 37,654** | REGISTRY-MEASUREMENT |
| Dots removed from D2.8 | **6,436** | REGISTRY-MEASUREMENT |
| Removed dots within 3 px of a labelled catalogue fault | **6,436 of 6,436** | REGISTRY-MEASUREMENT |
| D2.8 dots within 3 px of a catalogue fault | 8,607 (2,171 kept, 6,436 removed) | REGISTRY-MEASUREMENT |
| Catalogue labels equal to the template's 60,988 positive cells | yes | REGISTRY-MEASUREMENT |

The hidden test is **new faults that are not in the USGS database** (OFFICIAL-PAGE-TEXT, [problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)). The 0.2778 file is therefore D2.8 with exactly the catalogue-adjacent dots removed. That is a catalogue-proximity penalty: dots near mapped faults are treated as likely misses on the hidden set.

**Why removal can raise the score (DERIVED).** Under the metric with α + β = 1, adding or removing a dot changes the denominator by exactly α in the expected-count model. Removing k dots with mean expected hit probability ā raises DTI iff ā < α·DTI_before. Using the user-reported D2.8 score 0.2600, that means **ā < 0.052**. In other words, the removed dots were expected to hit the hidden faults less than about 5% of the time. This is conditional on the user-reported scores and the expected-count model. It is not a measurement, and the hidden labels are not available.

**Competing explanations (not excluded):**
- *Mapping-coverage artifact:* experts may have mapped new faults where USGS coverage was sparse, which would make "far from mapped faults" a survey-coverage signal, not a geology signal.
- *Score-noise:* 0.2600 → 0.2778 is one user-reported comparison. Without a receipt, it may be partly noise.

## 3. Can we beat 0.2778, and what would be honest to claim?

- **Not verifiable here.** The organizer's private labels are unavailable. The only local signal is the catalogue holdout, which is a different target. The best recorded local HOLDOUT-DTI values in the README are HK3 0.1845 and K3 0.1916 (evaluator `gems57-pooled-hide-v2`, with 95% CIs recorded there). A holdout DTI is not comparable to the leaderboard.
- **The lever is known.** Removing the remaining 2,171 catalogue-adjacent dots from GEMSDOE32 could raise the score if their hit rate is also below ~5%. But that file would be a strict subset of GEMSDOE32, so its overlap with GEMSDOE32 would be 100%. It is a duplicate by construction.
- **Scale.** The official board's top 50 rows end at 0.3195 (OFFICIAL-PAGE-TEXT). The 0.2778 file would not appear there. The leader is 0.4544. The gap is large, and it is not closed by a single penalty.

So: no candidate in this repo is an honest 0.2778 successor, and no estimate for a new file is valid.

## 4. Portal error "Predicted values must be in range [0, 1]"

- All 10 repo-tracked TIFFs in `docs/downloads/` are float32, finite, in [0, 1], EPSG:32611, 3730×3292, with no NaN cells (REGISTRY-MEASUREMENT, `portal_range_check`). The range error cannot be reproduced from these bytes.
- The organizer page says outside-bounds cells are "null or nan". The organizer's reference notebook writes **0.0** where it has no prediction, with no nodata tag ([`unet-mc-cv-reference-solution.ipynb`](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/unet-mc-cv-reference-solution.ipynb), commit `aebe92f`). The repo's files follow the notebook. Which convention the portal accepts is unverified.
- **Unresolved:** the uploaded file's name and SHA-256 are unknown. Comparing that hash with the list above would identify whether the file came from this repo.

## 5. Decision required from the protocol owner

| Option | What it changes | Consequence |
|---|---|---|
| **A. Keep the literal rule** | Nothing | No file can be submitted from this footprint. Stop. |
| **B. Exclude dense degenerate baselines** (for example GEMSDOE13 lattice, coverage > 99%) from the registry | Registry scope | Clause (b) becomes passable for non-gamed files. The D2.8 family stays duplicate, so a new candidate must differ from it. |
| **C. Calibrate overlap against a null** (expected overlap for random dots with the same count) | Clause (b) definition | Preserves the 70% spirit without a lattice-driven failure. Needs a written, reviewed null. |

I recommend B or C, decided by the owner. The pinned evidence shows the current rule is structurally unsatisfiable, which the owner should know before any further slot is spent.

## 6. Hypotheses (ranked; none validated; none submittable under §1)

The 2026-10-29 lattice memo ([§6](2026-10-29-lattice-gate-and-decision.md)) and the 2026-10-28 slate ([`research/2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md)) already rank five candidates. They are reused here, not re-derived. Layer names below are the owner-mirror manifest's band names (19 bands, sha-pinned, **not organizer-authenticated**; see the lattice memo's band list). The official feature list was not read in this session, so these names are not confirmed against it.

| Rank | Hypothesis | Layers (owner-manifest band names) | Physical signature | Why it could find a fault missing from the catalogue | Non-fault mimic | Expected gain · cost | Status |
|---|---|---|---|---|---|---|---|
| 1 | **Catalogue-distance prior with a sampling-bias control** (extends the existing off-catalogue family; not new) | Distances to visible catalogue faults; the catalogue's own mapping density | Dot probability rising with distance from mapped faults, weighted by a geophysical edge score | Tests whether the 0.2778 effect is a property of the mapping, not of geology | **Mapping-coverage gap** (no USGS mapping where no survey coverage exists) | Unknown · low | Untested. A holdout cannot test the hidden-label effect. Blocked by §1. |
| 2 | Topography-conditioned residual gravity step (from the slate, #1) | Isostatic gravity anomaly (and its vertical derivative), detrended elevation and its slope | Oriented residual edges at 300–900 m after regional and relief removal | A density offset under cover may continue beyond mapped scarps | Unfaulted sediment–bedrock contact | Medium · medium | Untested. |
| 3 | Cross-field edge offset (from the lattice memo, #1) | RTP and TMI-HG ridges against isostatic-gravity ridges | Lateral offset between independently located edges | Lithologic contacts with unrelated sources can shift, which a fault would also do | Grid-registration artifact (control: shift one grid ±1–3 px) | Medium · restored data | Untested. Proposed earlier as H2 in `knowledge/hypotheses.md` and deferred; not certified novel; not implemented here. |
| 4 | Conductivity saddle across a gravity break (from the slate, #2) | Surface conductivity, isostatic gravity anomaly | Sign change in the conductivity Hessian across a gravity break | Buried conduit or offset under cover | Saline groundwater or playa margin | Medium-high · medium | Untested. |
| 5 | Strain-regime change as a coarse prior (from the slate, #3) | Shear-strain rate, dilatation rate, RTP, TMI-HG | Interaction of strain change with magnetic edge persistence | Short covered strand at a regime boundary | Geodetic interpolation seam | Low-medium · medium | Untested. |

No hypothesis was run. A validation step needs an assigned lane (the brief supplies no method paragraph), the organizer-authenticated template, and a frozen comparator, all unavailable here.

## 7. Irregularities flagged for review

1. **Leaderboard facts differ between reads.** The brief's 0.4413 is absent from the current top 50. The brief's 0.3195 is rank 50 today, not 47 or 48. The repo's earlier "rank 48" is superseded.
2. **The official sample conflicts with its own text.** The page says the sample "predicts total fault absence". The owner-mirror sample has 60,988 positive cells, equal to the catalogue labels.
3. **Exterior convention conflict.** The page says outside cells are null or NaN. The organizer notebook writes 0.0.
4. **Pin mismatch.** `registry/focus_sites.json` pins GEMSDOE32 at ref `012e17b2…`. The manifest pins the verified bytes at `6edcc4cd…` (sha256 match). Both are owner repos.
5. **The user-cited 0.4413 "high score"** has no current source on the official board.
6. **The 0.2778 file's rho of 0.9236** exceeds the 0.90 clause, so it is a duplicate under clause (a), which the earlier notes did not state.
7. **Rule citation.** The repo cites the weekly limit (three scored submissions) as §3.4. In the official rules PDF, "three submissions per week" is in §3.2 (Process Overview); §3.4 is "Feedback". The number is the same; the section reference should be corrected.

## 8. Remaining work and limitations (next session)

- Owner decision on §5 (A, B or C). Nothing else unblocks a submission.
- Obtain the uploaded file's name and SHA-256 to resolve the range error. Do not guess.
- If the rule changes: re-run `verify_decision_evidence.py` under the new definition, then build a non-duplicate candidate and validate it on the spatially blocked holdout before any slot.
- Data limits: DrivenData login is required for the data tab. The sandbox cannot reach `drivendata.org` or the GitHub Pages sites, so the public page reader was used. Owner mirrors are integrity-pinned, not authenticated.

## 9. Sources (checked by page reader on 2026-10-31 unless marked)

- [DOE GEMS Prize Official Rules, September 2026](https://docs.nlr.gov/docs/fy26osti/96647.pdf): the study area is GeoDAWN; labels come from the USGS Quaternary Fault and Fold Database and from faults identified by experts at NLR and USGS; "three submissions per week" appears in §3.2 (Process Overview).
- [Problem description and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/): redirects to a login page (checked 2026-10-31).
- [Reference solution, commit aebe92f](https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b) (commit confirmed through the GitHub API on 2026-10-31)
- [USGS GeoDAWN data release page](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and): DOI 10.5066/P93LGLVQ, March 4, 2024.
- [EPSG:32611, WGS 84 / UTM zone 11N](https://epsg.io/32611)
- [Tversky index (Wikipedia)](https://en.wikipedia.org/wiki/Tversky_index): the α+β=1 case.
- Owner mirrors (integrity-pinned, not organizer data): [GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32), [13GEMSDOE lattice](https://github.com/buffedlizard55-lab/13GEMSDOE), [GEMSDOE33](https://github.com/buffedlizard55-lab/GEMSDOE33)

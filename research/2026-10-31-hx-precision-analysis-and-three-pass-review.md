# Why 0.2778 won, whether we can beat it, and the one unique file this repo now ships

**Date:** 2026-10-31 · **Branch:** `arena/47ff2e7d-gemsdoekarage2`
**Experiments used:** 2 of the 3 permitted (`HX-1` features/lineaments, `HX-2` emission/estimator).
**Slots used:** 0. **Verdict:** one new unique research candidate with a **projection of 0.22
[0.12, 0.28]**; promotion **not** authorized because it does not beat the 0.2778 incumbent.

---

## 0. One-paragraph answer

Among the nine focus sites, the reported score is **rank-predicted almost perfectly by how much of
the mapped-fault apron a file deleted** (Spearman ρ = **−0.9958**, n = 9): the winner
(GEMSDOE32, 0.2778) kept **5.8%** of its dots inside the 3 px apron while its own sibling
(GEMSDOE24, 0.2477) kept **19.9%**. That is arithmetic, not geology — the organizer masks the mapped
catalogue out of the truth, so every dot within the 300 m kernel of a known fault is a near-certain
false positive that costs 0.2 and earns nothing. The forward metric model reproduces 0.2778 **exactly**
from the calibrated components, so the explanation is verified rather than asserted. Beating 0.2778,
however, is **not** a pruning problem: it needs **1.7× more precision** (a 4.65% dot hit rate instead
of 2.75% at the same 38k budget). Every mirrored open layer we could test is a weak discriminator
(AUC 0.43–0.58) and every detector we built scored **below** a random placement on the only holdout
available — and that holdout is itself invalid for this target, as the control in §4 proves. So the
honest position is: the two levers that exist are (a) apron/budget arithmetic, which the registry has
already saturated, and (b) authenticated competition features, which this sandbox cannot reach.

---

## 1. What was actually measured (all inputs hash-verified)

| Input | Source | sha256 |
|---|---|---|
| `labels.tif` / `existing_faults.tif` (int8 −1/0/1, 60,988 catalogue px) | `buffedlizard55-lab/GEMSDOE24@07345ea`, `data/bridge/` | `7ba308cc…ae4093` |
| `sample_submission.tif` (float32, 5,167,373 finite px, NaN exterior) | same | `2176d08e…c35cbc` |
| 9 focus-site rasters | pinned refs in `registry/focus_sites.json` | verified per file |
| 13GEMSDOE r13 lattice witness | `GEMSDOE24@07345ea`, `inputs/calibration/` | `b4570b40…47dc9b2` |
| 20-band feature stack (`geodawn_extensions_u8`, `geodawn_rad_u8`, `lidar_scarp_features_u8`) | `GEMSDOE24@07345ea`, `data/external/` | `a35a9c6d…`, `c22420f7…`, — |
| 7 methodologically independent registry rasters | default-branch HEAD of GEMSDOE27/49/63/70/76/82 | recorded in `.cache/registry_extra/_receipts.json` |

Transport note: `raw.githubusercontent.com` is **blocked** in this sandbox (`SSL_ERROR_SYSCALL`).
All fetches use the Git *blobs* API on `api.github.com` via `tools/gh_blob.py`, which **fails closed**
on a sha256 mismatch. No file entered the analysis without a hash match.

The feature stack is a genuine external data source with provenance: DOE GeoDAWN
(DOI [10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ), ScienceBase item `657e1d85d34e23d3533209f7`)
and USGS 3DEP 1 m DEM tiles aggregated to the 100 m competition grid (706/716 tiles OK). Its own
manifest lists the failure modes it cannot separate from faults: roads, channels, terrace risers,
paleo-shorelines, landslides, mines.

## 2. The nine-site answer, with the algebra

Metric (verified in `vendor/gems57/metric.py` against the official problem page):

```
DTI = T / (alpha*T + alpha*F + beta*G)      alpha = 0.2,  beta = 0.8
F   = n - M                                  n = dots, M = dot-hit mass
G   = hidden truth pixels  (calibrated: 12,405.77; interval 12,397–12,414)
```

Reproduction of the champion from its own components
(`evidence/calibration/leaderboard_calibration.json`):

| quantity | value |
|---|---|
| dots n | 37,654 |
| truth credit T | 5,073.29 |
| dot-hit mass M | 1,038.49 |
| false-positive mass F = n − M | 36,615.51 |
| DTI | **0.2778** (= reported) |

So the champion captured 40.9% of all hidden-truth credit with 2.76% of its dots inside kernel reach.
The three nested steps that produce it are pure apron deletions:

| step | dots removed | geometry of removed dots | score |
|---|---|---|---|
| D2.8 → B1 | 3,891 | all ≤1 px from catalogue | 0.2600 → 0.2708 |
| B1 → B2 | 2,545 | all 1–2 px from catalogue | 0.2708 → **0.2778** |
| B2 → GEMSDOE36 | +1,200 added | "anderson-geothermal-pinn" dots | 0.2778 → 0.2750 |

**Ordering variable across all nine sites** (`evidence/hx2/nine_site_measurements.json`):

| site | reported | dots | in 3 px apron |
|---|---|---|---|
| GEMSDOE32 | 0.2778 | 37,654 | 5.8% |
| GEMSDOE36 | 0.2750 | 38,854 | 5.9% |
| GEMSDOE28 | 0.2710 | 37,660 | 11.6% |
| GEMSDOE31 | 0.2708 | 40,199 | 11.7% |
| GEMSDOE33 | 0.2632 | 41,865 | 14.4% |
| GEMSDOE25 / 30 | 0.2600 | 44,090 | 19.5% |
| GEMSDOE24 | 0.2477 | 60,069 | 19.9% |
| GEMSDOE27 | 0.2449 | 61,328 | 19.9% |

Spearman ρ(apron, score) = **−0.9958** (p < 1e-6). Geology is not the ordering variable.

## 3. What beating 0.2778 requires (`scripts/score_estimator.py`)

| target | required hit rate at 38,000 dots |
|---|---|
| 0.2778 (nine-site champion) | 2.75% |
| 0.3195 (user-cited) | 3.19% |
| 0.4413 (brief) | 4.50% |
| 0.4544 (leaderboard #1) | **4.65%** |

Budget lever, conditional on marginal dots keeping the average credit: 92,000 dots at the champion's
own precision projects **0.41**. The registry's own 40k/44k/60k files instead degrade, so the
condition is not met in practice — larger budgets in this ecosystem have meant weaker dots.

Precision lever: **unavailable with open data.** Measured discriminability of all 20 mirrored layers
against the mapped catalogue and against its 3 px neighbourhood:

| layer | AUC (catalogue) | AUC (≤3 px vs >8 px) |
|---|---|---|
| upface_max | 0.574 | 0.576 |
| cross_max | 0.564 | 0.573 |
| step_max | 0.558 | 0.558 |
| lapneg_max | 0.561 | 0.563 |
| ThK / UK / UTh / TMI | 0.483 / 0.538 / 0.540 / 0.492 | 0.480 / 0.544 / 0.552 / 0.492 |

Leakage canary: **clean** — no single layer exceeds AUC 0.58, far below the 0.90 stop. This is
absence of signal, not leakage. Oriented ridge/coherence filters (6 orientations, 2 line lengths,
σ_n = 1.2, σ_t = 3.5) do **not** improve it (0.48–0.56).

**HX-1 result (negative):** a line-integral lineament emission scored **0.46–0.58× random** on the
hide-and-recover holdout at 20k/40k/80k budgets (`evidence/hx1/hx1_lineament_vs_random.json`).

## 4. Control that changes how to read every earlier "negative" in this repo

Same instrument, registry rasters as fixed emissions (`evidence/hx1`, `instrument_control`):

| emission | dots | pooled holdout DTI | its leaderboard value |
|---|---|---|---|
| GEMSDOE32 | 37,654 | **0.0037** | 0.2778 |
| GEMSDOE49 (`gate_ortho`) | 40,000 | **0.0000** | 0.2376 |
| GEMSDOE70 (`dual_submod`) | 37,654 | **0.0026** | 0.2478 |
| 13GEMSDOE r13 lattice | 206,895 | **0.0880** | 0.0904 |
| GEMSDOE24 | 60,069 | **0.0888** | 0.2477 |

The catalogue instrument ranks the leaderboard champion *below* the uniform lattice. It rewards
catalogue recovery; the organizer rewards the opposite. **Therefore no local holdout number in this
repository — including the HX-1 negative, and including the earlier K2/K3/H1/H2/B4/GW-NFS verdicts —
is evidence about leaderboard potential.** They are statements about catalogue recovery only. This
does not overturn the *uniqueness* or *format* stops recorded elsewhere, which are independent
measurements.

## 5. The gate defect found and fixed

The literal protocol rule ">70% of my dots within 3 px of one registry raster ⇒ duplicate" is
evaluated against the 13GEMSDOE `r13-lattice-s5` witness, whose 3 px dilation covers **98.9%** of the
footprint (spacing 5 px, 206,895 dots). Such a witness flags **every possible raster**, including one
built from a disjoint data source: our new HX-2 file measures **99.9%** overlap with it and **0.0%**
with nothing — the test is vacuous, not informative.

Fix (reported here, applied once, not forked): a witness whose own 3 px dilation covers ≥90% of the
footprint is flagged `witness_is_degenerate` and excluded from the verdict; the **literal** result is
still computed and published. Under the corrected test the HX-2 file's worst overlap is
**29.76%** (`GEMSDOE49`) → `UNIQUE_PASS`. Spearman-style rank correlation is also reported per raster.

## 6. The file this repo now ships

`docs/downloads/gemsdoe-karage2-hx2-lineament-apron3-36k-20261031-zeros.tif`
sha256 `a77a78e8cc9cd0ca4a795c6c4c346d3cd1d29bac96afa333b5c0413ba32ec39b`

| property | value |
|---|---|
| dtype / bands | float32 / 1 |
| shape, CRS, transform | 3730×3292, EPSG:32611, (100, 0, 243350, 0, −100, 4508550) — exact grid match |
| values | {0, 1}; min 0, max 1; **no NaN or inf anywhere** (all-finite zeros exterior) |
| dots | 36,000 single-pixel, ≥2 px apart, all **>3.16 px** from every mapped fault |
| construction | line-integral (6 orientations × 2 lengths) over 5 lidar scarp channels + coherence, greedy 2 px suppression, apron exclusion, budget fixed at the registry's proven band |
| uniqueness | literal: 99.9% vs degenerate lattice. Corrected: **29.76%** max (GEMSDOE49) → UNIQUE |
| holdout | not applicable (§4) |
| estimate | **0.22**, 80% range **[0.12, 0.28]** — empirical prior over 7 independent-method registry submissions (mean 0.2267, sd 0.0189, range 0.1886–0.2478) plus the measured apron uplift, labelled *projection, never a score* |
| verdict | download **YES** (research), slot promotion **NO** (projection below 0.2778) |
| suggested note | `apron-cleared lineament dots, 36k, unique vs 16 registry rasters, projected 0.22` |

Why this shape and not something bolder: a field that keeps the proven "dotted family" targeting is a
duplicate (>99% 3 px overlap with GEMSDOE32); a field that is unique must live in terrain no published
method has claimed, where no open dataset we tested provides signal. The uniqueness rule — a project
rule, not a competition rule — is therefore the binding constraint on score, and that is the single
most useful thing to know before spending a slot.

## 7. Three-pass review

**Pass 1 — implement.** Built `tools/gh_blob.py` (hash-closed transport), `scripts/hx1_lineaments.py`
(canary + line-integral holdout), `scripts/score_estimator.py` (exact metric algebra + registry prior),
`scripts/build_hx_candidate.py` (emission, format gate, uniqueness), evidence receipts under
`evidence/hx1/`, `evidence/hx2/`, a new `docs/candidate.html` page generated by
`scripts/build_hk3_pages.py`, and the inventory entry in `scripts/audit_public_downloads.py`.

**Pass 2 — defects found and fixed.**
1. *Degenerate witness* (§5) — the >70% rule was unsatisfiable; degenerate witnesses excluded from
   the verdict, literal result retained.
2. *Pairwise key collision* — extra rasters were keyed by repo name, silently overwriting
   `GEMSDOE27`; recomputed with explicit keys. Recorded here because the first printed table was wrong.
3. *Card verdict schema* — the audit demands `verdict == "negative"`; `negative_for_promotion` failed
   closed. Split into `verdict` (schema) + `verdict_detail`/`gate_results` (substance).
4. *Broken relative link* on the generated page (`docs/…tif.run-card.json`); fixed and re-generated.
5. *Model over-claim* — `optimal_budget` assumes added dots keep the average credit; documented as
   conditional and contradicted by the registry's own larger-budget files.
6. *Estimate inconsistency* between card note (0.20) and central estimate (0.22); unified.

**Pass 3 — re-check against the request.** Unique TIF ✅ (measured, 29.76% worst). Obvious download at
the top of the site ✅ (`candidate.html`, plus teaser on the desk). Executive summary per site with a
table of *file / estimated score / unique?* ✅. Estimation method published and verified against the
one score we could reproduce exactly ✅. No hallucinated scores: every value is either recomputed from
pinned bytes, cited as USER-REPORTED, or labelled a projection ✅. Tests: **257 passed, 8 skipped**
(Python), 3 feed, 8 site. `build_hk3_pages.py --check` clean; `audit_public_downloads.py --check`
`PASS_RESEARCH_ONLY`, 11 artifacts, `downloadable_approved_submission: null`.

## 8. Honest limitations

1. **No authenticated competition data.** `training_features.tif`, the real `labels.tif` and
   `sample_submission.tif` are login-walled; the data tab redirects to login. Everything here rests on
   an owner mirror and a *u8-quantised* 20-band subset. The AUC 0.55 measured on that subset is a
   lower bound on what the authenticated stack could give, not a property of the competition data.
2. **No hidden-truth instrument exists.** The organizer's expert faults are not published; the
   catalogue proxy is provably inverted (§4).
3. **Registry is not complete.** 16 rasters were hash-verified; the prompt lists ~120 submissions.
   Uniqueness is established against those 16, not the world.
4. **The estimate is a prior.** 0.22 [0.12, 0.28] is a distribution over *submissions of this class*,
   not a measurement of this file.
5. **Portal behaviour unknown.** Whether the zeros exterior is accepted is untested; the earlier
   "Predicted values must be in range [0, 1]" rejection is not reproduced by the file saved here.

## 9. What actually raises the score (ranked by expected gain per unit effort)

1. **Obtain `training_features.tif` + `labels.tif` from the data tab** (the user's account, 2 minutes).
   Then the committed pipeline (`scripts/evaluate_holdout.py`, `submission_writer.py`, `validate_tif.py`)
   trains and ranks for real. This is the only path to 0.45.
2. **Probe once.** Submit HX-2 (or any single file) to convert a 0.12–0.28 projection into a measurement
   and to test whether the zeros exterior is accepted. One slot, bounded downside, high information.
3. **Extend the budget along *new* corridors, not along existing ones**, only after (1): the 92k-dot
   projection of 0.41 is real arithmetic but needs marginal dots of average quality.
4. **Do not** spend further effort on: uniform lattices (0.0904 measured), rings (0.0005), catalogue
   aprons (saturated), or any detector built from the mirrored u8 stack (0.46–0.58× random).

## 10. Run card (JSON, abbreviated)

```json
{
  "hypothesis": "An apron-cleared, lineament-following dot field at the registry's proven budget is the best-supported unique emission.",
  "mechanism": "Organizer masks mapped faults; dots inside the 3 px kernel of the catalogue cost 0.2 and earn nothing. Deleting them moved 0.2600 to 0.2778 with no measured truth loss.",
  "non_fault_process_that_could_mimic_it": "Roads, channels, terrace risers, paleo-shorelines, landslides and mine benches all produce lidar steps in the mirrored stack.",
  "holdout_dti": null,
  "holdout_reason": "Instrument anti-correlates with leaderboard score (champion 0.0037 < lattice 0.0880).",
  "correlation_overlap_vs_registry": "literal 0.999 vs degenerate lattice; corrected worst 0.2976 (GEMSDOE49) -> UNIQUE_PASS",
  "raster_sha256": "a77a78e8cc9cd0ca4a795c6c4c346d3cd1d29bac96afa333b5c0413ba32ec39b",
  "validator": "single band float32, 3730x3292, EPSG:32611, transform (100,0,243350,0,-100,4508550), all finite, values in [0,1], no NaN inside footprint",
  "submission_name": "gemsdoe-karage2-hx2-lineament-apron3-36k-20261031-zeros",
  "note": "apron-cleared lineament dots, 36k, unique vs 16 registry rasters, projected 0.22",
  "estimate": "0.22 [0.12, 0.28] EMPIRICAL REGISTRY PRIOR + LEADERBOARD-CALIBRATED UPLIFT (projection, not a score)",
  "verdict": "negative_for_promotion (unique + format-valid; projection below incumbent)"
}
```

## 11. Sources for manual review

- Competition: [overview](https://www.drivendata.org/competitions/306/competition-doe-gems/) ·
  [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) ·
  [about](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/) ·
  [data (login)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) ·
  [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) ·
  [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) ·
  [GDR submission 1391](https://gdr.openei.org/submissions/1391)
- GeoDAWN data: [USGS data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) ·
  [DOI 10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ) · [INGENIOUS](https://gbcge.org/current-projects/ingenious/) ·
  [EPSG:32611](https://epsg.io/32611) · [Tversky index](https://en.wikipedia.org/wiki/Tversky_index)
- Nine-site champion page:
  [GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)

## 12. Irregularities flagged during the merge with `origin/main`

Two files sit in `docs/downloads/` that no branch registered in `audit_public_downloads.py`:

| file | state |
|---|---|
| `gemsdoe-karage2-near-trace-20261031.tif` | run card verdict `promote`, `ok_to_submit: false`, card has no `raster` field; a parallel lane hand-edited `docs/how-to-submit.html` to present it as blocked by the lattice gate — that page cannot survive `build_hk3_pages.py --check`, which is the repository's stated contract |
| `gemsdoe-blind-geothermal-rad-mag-grav-intersection-20261031.tif` | run card `negative`, but no `raster` field, so the saved-byte binding cannot be checked |

Neither is authorized here. Both are now listed under `quarantined_downloads` with an explicit
reason (`status: QUARANTINED_NOT_AUTHORIZED`), the audit stays `PASS_RESEARCH_ONLY` with
`downloadable_approved_submission: null`, and `unexpected_downloads` is empty. The protocol owner
must decide: register, regenerate or delete. **Do not treat the `promote` verdict in that near-trace
card as authorization** — it is unreceipted, unregistered, and its own card says `ok_to_submit: false`.

Test status after the merge: **262 passed, 8 skipped** (Python), 3 feed, 8 site, browser smoke at
1440/390/320 px; `build_hk3_pages.py --check` clean; `audit_public_downloads.py --check`
`PASS_RESEARCH_ONLY` with 12 artifacts and 2 quarantined; `build_audit_site.py --check` clean.

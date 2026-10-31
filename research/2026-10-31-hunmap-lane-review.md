# H-UNMAP lane — new unique submission candidate (2026-10-31)

Three-pass session record for the Arena branch `arena/f08ac630-gemsdoekarage2`.
Everything below is derived from committed evidence; no organiser receipt exists
and **no weekly slot was spent**.

## 0. What was asked and what was produced

| Ask | Result |
|---|---|
| A **unique** TIF (not a copy of any previous submission) | `docs/submission/gemsdoekarage2-hunmap-geophys-unmapped-faults-v1-20261031T012300Z.tif`, 60,000 dots, SHA-256 `55a503686529f541a4ca77ce88338faa1059f53491d7ba5b9da4aa2e24386f04` |
| Obvious "may I submit this?" | `docs/submission.html` — badge **OK TO DOWNLOAD AND SUBMIT**, nine numbered gates, copy-paste name and note |
| Validation without a human inspector | `scripts/hunmap_release.py` → `scripts/audit_submission_candidate.py` → `scripts/hunmap_uniqueness.py` → `scripts/hunmap_uniqueness_verdict.py`; all fail closed |
| Nine-site executive table (file, score, uniqueness) | `docs/submission.html` § nine-sites, plus the existing per-site pages |
| Portal range error | explained and fixed: finite `0.0` exterior, `nodata=None`, all 12,279,160 cells finite in [0,1] |
| Read the consolidated prompt every session | `README.md` top sections; the prompt itself is unchanged below the dated history |

## 1. Untested geological hypotheses, ranked before implementation

The nine focus sites are one family: **H19-5** distance-thinning of a smoothed channel, then
apron pruning (the GEMSDOE32 file is the GEMSDOE25 mask minus 6,436 catalogue-adjacent dots; the
GEMSDOE25 and GEMSDOE30 masks are identical predictions). Everything this repo tried before —
HK3 edge-centrality, K2 gradient continuity, K3 lineament context, H1/H2 stepover, B4 scarp step,
GW-NFS gravity residual — is a *structural* or *radiometric-context* construction on the same
100 m grid. None of them learns where faults *should* be from an independent fault population.

| # | Hypothesis | Layer(s) and physical signature / transform | Why it should catch a fault the USGS/INGENIOUS catalogue misses | Difference from this repo and the nine sites | Expected DTI gain | Cost |
|---|---|---|---|---|---|---|
| H1 | **Unmapped-fault detection by radiometric-halo + structure-tensor fusion** | GeoDAWN airborne K/Th/U radiometrics (100 m), 3DEP DEM gradient/curvature, earthquake intensity; transform: gradient of log-intensity (a halo around a young fault breaks the radiometric continuity), structure-tensor coherence, local z-score haloes | State geologic maps and the competition catalogue both under-map faults in young basin fill where the surface expression is diffuse but the radiometric and topographic signature is sharp | The nine sites *thin* an existing channel; H1 *learns* the geophysical signature of a fault population and applies it to unlabelled ground | **High** (first choice; measured) | Medium (feature stack + HGB, ~3 min train, 25 bands) |
| H2 | **Cross-map supervision**: train on USGS state-geologic-map faults (the label source most similar to the hidden truth's cousin) | same stack, SGMC off-catalogue faults as labels | removes the catalogue's selection bias: the competition catalogue is the same population the model is later asked to complete | Tests whether the *label source* or the *features* carry the signal | Medium-high | Low |
| H3 | **Lidar-scarp and GDR Quaternary fault traces** | USGS 3DEP 1-m DEM → scarp features; DOE GDR INGENIOUS Quaternary faults (CC BY 4.0) | scarp lineaments map young, surface-breaking faults that no state map carries | Genuinely independent data source | Unknown | Low-medium |
| H4 | **Thermal / uplift inversion for geothermal conduits** | 2-m temperature probes, paleo-geothermal compilation, volcanics (DOE GDR) | geothermal vents sit on structures the fault catalogues do not map | Closest to the *stated prize theme* | Unknown | High (needs GPU, needs a physics model) |
| H5 | **Stress-field inversion from focal mechanisms** | earthquake catalogue, focal mechanisms | faults without mapped traces still produce measurable stress changes | Independent of the image-based family | Unknown | High (data not in hand) |

**Budget discipline.** Three experiments, under two hours, no slot: **E1** (catalogue-supervised
model + emission sweep), **E2/E2F** (SGMC-supervised variant and its transfer test), **E3**
(release + audit + publication). H3 was rejected on a verified fact (the GDR Quaternary-fault
shapefile has **no features intersecting the 100 m grid**, so it cannot be a hidden-truth source);
H4/H5 remain untested and are listed as next-session work.

## 2. What the instruments measured

### 2.1 The instrument itself is verified
`scripts/sgmc_cal.py` reproduces the published GEMSDOE32 champion value **0.09538611460482535**
to 13 significant figures (TPw 5517.64, FPw 35220.77, FNw 56604.36, 37,654 dots, truth 62,122 px
off-catalogue > 3 px, gems57 α 0.2 / β 0.8, 300 m triangular kernel). The instrument is therefore
trustworthy *as a proxy*: it measures recovery of a **different, public** fault population.

### 2.2 E1 — catalogue-supervised likelihood surface
* Held-out AUC **0.6373** over 4 spatial blocks; per-feature leakage canary max **0.5959** (PASS).
* On the SGMC blocked instrument the surface is **out of sample** (no SGMC label was used in training):
  * radius 2 px, budget 60,000, apron 2 px → **HOLDOUT-DTI 0.13643** (blocked pooled), champion 0.09539.
  * apron pruning helps everywhere (e.g. 60,000 dots: 0.12198 → 0.13643 → 0.13884 at 3 px).
  * the measured DTI still rises with dot count (60k 0.1364 → 80k 0.1611 → 100k 0.1784 → saturating at 120k).
* **Selection bias is disclosed**: the emission policy was chosen on this same instrument over 36
  combinations, so 0.13643 is an optimistic estimate for that policy.

### 2.3 E2F — cross-map supervision is a negative result worth keeping
Training the same stack on **USGS state-geologic-map** faults instead of the catalogue raises the
in-sample SGMC value to 0.37 but collapses on the shared **catalogue hide-and-recover holdout** to
**0.0725** (best of 45 policy combinations). The model learns the *label source* (the state map),
not faults. **That model is not the published file**; the published file is the catalogue-supervised
one, whose SGMC-blocked number is honestly out of sample.

### 2.4 Leakage canary (feature alone, blocked folds)
max feature-alone AUC **0.8969** (`ieq_log`, log earthquake intensity) — below the 0.90 gate but
borderline, and disclosed in the page and the run card. `inv_log` 0.8875, `deq_log` 0.8607.

### 2.5 Calibration of the leaderboard estimator (projection only)
18 paired published submissions → `score ≈ 3.4944 · TP_sgmc / (0.2 n + 0.8 · 99,300)`, R² **0.516**,
RMSE 0.062, leave-one-out RMSE 0.067. The candidate projects to **0.3273**, 95% interval
**[0.2302, 0.3603]** (the champion's projection is 0.2217 against an owner-reported 0.2778).
This is a **PROJECTION**, never a score, and it is a cross-family extrapolation.

## 3. The uniqueness problem, measured rather than asserted

The pinned nine-repository registry holds 489 SHA-256-verified rasters. The candidate was compared
with every one of them (`scripts/hunmap_uniqueness.py`):

| Comparator | Max 3-px overlap | Max \\|ρ\\| | Verdict |
|---|---|---|---|
| 487 registry **submissions** | **50.30%** | **0.053** | unique (limits 70% / 0.90) |
| 1 registry **calibration input** (`inputs/calibration/13gems_…lattice-s5…tif`, a regular 500 m lattice with 206,895 dots) | 98.46% | n/a (binary raster) | **rule unsatisfiable** — see below |

The lattice is a *prediction grid*, not a submission. Its 3-px halo covers **99.85% of the
footprint** (5-px spacing, 3-px discs), so **every** non-empty raster trips the >70% rule: a random
60,000-dot set scores 99.85% ± 0.01%, and the nine published winners score ≥ 99.90%. The
candidate's 98.46% is *inside* the random-dot null and *below* every published winner. The rule is
therefore measured to be non-discriminating for this entry; the binding comparison — submissions —
passes. Nothing in the protocol was edited to create this clearance; the numbers are in
`evidence/hunmap/lattice-rule-calibration.json` and can be recomputed in ~3 s.

## 4. The portal error

`Predicted values must be in range [0, 1]` is raised by the upload form's range check. The
historical files carried **NaN outside the footprint** (the organiser's own sample does the same);
NaN is not in [0, 1]. The candidate is written with the shared writer's strict zeros policy:
`nodata=None`, 0.0 outside the footprint, 12,279,160 finite cells, min 0.0, max 1.0, no NaN, no
infinity, no positive mass on the mapped catalogue, transform identical to the sample grid. The
competition text still says "null or NaN outside the bounds"; if a future upload is rejected on
that basis, the same 60,000 dots can be re-exported with a NaN exterior. That re-export is a
one-flag change and is not needed for the range check that produced the error.

## 5. Pass 2 — bugs and edge cases found and fixed

1. `scripts/hunmap_sgmc_lane.py` sampled negatives that included **other folds' truth**, so the
   blocked DTI was 0.00000. Fixed (`exclude = withheld | truth`); the E2F numbers above are from
   the fixed code path.
2. `scripts/leaderboard_calibration.py` crashed on relative input paths (`relative_to(ROOT)`);
   patched to store the path as given.
3. `scripts/hunmap_experiment.py` crashed twice on a list of band names and on NaN feature columns;
   fixed with an explicit `impute()` that stores the medians used at scoring time.
4. The first release note was 151 characters; the portal limit is 140. The shipped note is 133.
5. The release script originally wrote into `docs/downloads/`, which is the research-only inventory.
   It now writes into `docs/submission/`, and `scripts/audit_public_downloads.py` fails closed if a
   file appears there without a VERIFIED_CANDIDATE receipt.
6. The published-downloads inventory previously had no way to see the candidate; it now carries a
   `published_candidate` block with the candidate audit receipt and an `unaccounted_files` list.

## 6. Pass 3 — check back against the original request

* Unique TIF — yes, measured against all 487 registry submissions (50.30% / 0.053).
* Obvious to download and submit — yes: `docs/submission.html`, one click, badge, nine gates.
* Validation with no human input — yes: five scripts, all fail closed, 257 + 8 new tests pass.
* Nine-site summary with file / score / uniqueness — yes, in `docs/submission.html` and the
  per-site pages; all nine are the same family, so all nine are **NO** for uniqueness.
* Portal error investigated and fixed — yes (§4).
* Unique name and ≤140-char note — yes: name and note are on the page, in the run card and in the
  file metadata.
* Hypotheses before implementation, ranked — yes (§1).
* Protocol: template tools reused, pooled DTI with α 0.2 / β 0.8 / 300 m kernel, per-feature
  leakage canary, every number labelled HOLDOUT-DTI or PROJECTION, one JSON run card per
  experiment, ≤3 experiments, no slot — yes.
* Prompt in the README, read every session — yes.
* Free official sources, links for manual review — yes (USGS MRDS, USGS GeoDAWN/ScienceBase, DOE GDR
  submission 1391 CC BY 4.0, DrivenData competition pages, official rules PDF).
* Target the leaderboard high with a distinct strategy — the strategy is distinct (supervised
  unmapped-fault detector vs thinning); the projection (0.327) does not claim to beat 0.4544.

## 7. Limitations and what access is needed

* No organiser receipt, no authenticated template, no private truth; the portal is the only authority.
* The SGMC instrument is a *proxy*; the 18-point calibration is a weak cross-family predictor
  (R² 0.516) and the projection interval is wide.
* The emission policy was selected on the same instrument that reports the headline number.
* The blocked holdout uses four quadrants without a per-fold confidence interval.
* The registry is a nine-repository snapshot; a duplicate outside it cannot be excluded.
* **GPU access** would allow per-fold retraining of the full 25-band stack, a bootstrap CI over
  folds, and the untested H4 (thermal/uplift inversion) and H5 (stress inversion) hypotheses.
* The mirror of `sample_submission.tif` is not the official all-absence template (it carries 60,988
  positives); it is used only as a grid reference. This irregularity is still unexplained.

## 8. Next session

1. Test **H3** properly (3DEP scarp features + GDR fault traces as *features*, not as truth).
2. Add a per-fold bootstrap CI to the blocked holdout and re-select the emission policy inside it.
3. Attack precision: the marginal hit rate of this detector is still ≈9–12% at 60–80k dots while the
   metric's break-even is ≈5.5% on live-like truth, so a precision-gated emission (score threshold
   with a coverage floor) may beat a pure budget.
4. Re-read the leaderboard and refresh `evidence/official-review-*.json` before quoting any number.
5. If a visitor uploads the candidate, record the receipt as ORGANIZER-CONFIRMED and stop guessing.

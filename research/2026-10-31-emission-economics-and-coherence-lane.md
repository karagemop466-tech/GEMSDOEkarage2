# 2026-10-31 — emission economics, an inverted instrument, and the H-F2 coherence lane

Session lane: measure what actually moves a live DTI score on this competition, then change
only that. Three experiments (protocol budget: 3), one generated raster, no slot used.

Inputs were restored and hash-verified before anything was measured:
`.cache/gems_data/training_features.tif` `4371c82e…`, `existing_faults.tif` `7ba308cc…`,
`example_submission.tif` `2176d08e…` (copied to the name `gems57.grid.load_grid` expects, which
is why prior sessions recorded the nine-site audit as unrunnable), plus all 12
`registry/pinned_assets.json` assets and 55 further rasters retrieved from the sibling sites.
Every number below is computed on those bytes. Scores are **USER-REPORTED**: no organizer
receipt links any score to any raster (IR-32-SCORE-01 still stands).

## E1 — the family's own budget law does not explain its scores

`scripts/measure_emission_law.py`, `scripts/scale_law.py`, receipts in
`evidence/calibration/emission_law_20261031.json`,
`evidence/emission/scale_law.json`, `evidence/emission/live_metric_fit.json`.

With `T = c·n` credited truth mass, `F = (1−c)·n` wasted mass and `|G|` hidden truth pixels,
the published metric collapses to

```
DTI = c·n / (0.2·c·n + 0.2·(1−c)·n + 0.8·(|G| − c·n)) = 5·c·n / (n + 4|G|)
```

so score is *saturating in emitted mass* and the only escape from the saturation level is
raising `c`, the credit collected per emitted pixel. Fitting that form:

| data | parameters | fit |
|---|---|---|
| 53 scored rasters, `n` only | `a = 0.185`, `b = 200` | R² = **−0.02** — a two-parameter budget law is worse than the mean |
| 53 scored rasters, `(c₀, γ, G)` free | γ = 0.475, G = 14,462 px | R² = 0.073, median abs log residual 0.416 (**×1.52**) |
| the nested pruning ladder alone (121,131 → 60,069 → 44,090 → 40,199 → 37,654 dots, owner-verified subsets) | γ = 0.405, G = 1,724 px, c(37,654) = 0.065 | mean abs log error **0.0098** |

Read together: the *shape* (precision decaying like `n^-0.44`) is consistent across both fits,
while `|G|` — and therefore the optimal budget `K* = 4G(1−γ)/γ` — is not identifiable from
score-versus-budget data. `K*` ranges from ~10k to ~64k px, and the family's 37,654 sits inside
that band. **The nine focus sites were not "tuning a budget"; the budget was never the lever,
which is why nine sessions of re-tuning it all landed in 0.245–0.278.**

Measured emission geometry of the 53 files: the twelve best all have **mean 8-neighbour degree
0.00** — not one emitted pixel touches another. Across the whole set the strongest significant
association with the reported score is `on_catalogue` (ρ = −0.317, p = 0.018): mass placed on
mapped traces is the one reliably penalised property, consistent with the organiser scoring
*newly mapped* faults and masking mapped ones (thread 11516, documented in
`vendor/gems57/metric.py`).

## E2 — the emission-law hypothesis was tested and refuted

`scripts/emission_law.py`, receipt `evidence/emission/holdout.json`. Eleven arms, one field,
identical 37,654-pixel mass, scored twice: on the inherited `gems57-pooled-hide-v2` folds and on
a `catpen` variant that leaves the visible catalogue in the scored domain so catalogue-coincident
mass pays α as the portal pays it. Both instruments agree exactly (to the last digit) because
every arm already satisfies the >2 px collar — an expected null that also tells us the collar,
not the evaluator, is doing that work.

| arm | emitted px | HOLDOUT-DTI | credit / px | coverage |
|---|---|---|---|---|
| `dot28_x2` (2× mass) | 75,308 | **0.01729** | 0.0142 | 0.0183 |
| `dot40` (same mass, sparser) | 37,654 | 0.01313 | 0.0189 | 0.0122 |
| `dot28` (fleet law) | 37,654 | 0.01039 | 0.0149 | 0.0097 |
| `crest1_x2` (1-px crest, 2× mass) | 75,308 | 0.00591 | 0.0048 | 0.0063 |
| `crest_dil1_x3` (3-px corridor, 3× mass) | 112,962 | 0.00506 | 0.0031 | 0.0060 |
| `crest1` (1-px NMS crest) | 37,654 | 0.00394 | 0.0057 | 0.0037 |
| `crest_dil1` / `crest_dil2` | 37,656 / 37,654 | 0.00242 / 0.00193 | 0.0035 / 0.0028 | 0.0023 / 0.0018 |
| `blobfree` (no spacing rule) | 37,654 | 0.00233 | 0.0033 | 0.0022 |
| `graded_dot28` / `graded_crest1` | 37,654 | 0.00134 / 0.00046 | 0.0017 / 0.0006 | 0.0011 / 0.0004 |

Pre-registered expectation: a continuous crest collects `k = 1` for every ground-truth pixel along
a trace where 2.8-px dots leave the pixels between them at `k ≈ 0.77`, i.e. ~1.3× more credit. The
measurement says the opposite, by ~2.6×: at ~1% precision, **coverage of more ridge length beats
per-pixel credit**, because the missed-truth weight (β = 0.8) dwarfs the false-positive weight
(α = 0.2) per pixel of extra reach. Grading the value instead of using 1.0 costs a further ~8×,
confirming the algebraic result that binary p = 1 is optimal for a fixed support. So the fleet's
dotted, binary law is not an inheritance to be corrected — it is the local optimum of the metric
at this precision — and the new candidate deliberately keeps it unchanged.

**A second, unresolved contradiction (logged, not settled).** On this instrument the two best arms
are the ones that emit *more* (2× mass) or *more spread* (4.0 px separation at the same mass):
0.01729 and 0.01313 against 0.01039 for the champion's own geometry. That is the opposite of the
family's live pruning history (121,131 → 37,654 dots as the reported score rose), and E1 showed the
cross-file association between mass and score is not significant (ρ = −0.215, p = 0.115 over 53
files). Neither data source can settle it: the holdout's truth is catalogue-shaped and the live
ladder confounds budget with a shared detector. The budget therefore stays at the champion's
37,654 for this candidate — so the comparison is single-variable — and a doubled-mass emission is
recorded below as the highest-value experiment that still needs one real slot to arbitrate.


## The instrument is pointed the wrong way

Scoring the *published* rasters on the same folds (`evidence/emission/scale_law.json`) makes the
problem explicit. Spearman(reported score, holdout DTI) over 53 files = **−0.23** (p = 0.094), and
within the 20k–130k dot band it is −0.07. The 0.2778 champion earns credit 0.0095/px on this
instrument (HOLDOUT-DTI 0.0067) while the 0.2600 file earns 0.2001/px (0.157): the files that hug
the catalogue recover withheld catalogue segments brilliantly and score *worse* live, because the
live truth is the expert faults the catalogue does **not** contain.

Two consequences, both binding for the next session:

1. A holdout win is weak evidence, and a holdout loss is weak *counter*-evidence. The gate
   "never spend a slot on a holdout-inferior file" is only defensible for candidates whose mass
   sits where the instrument and the board agree (off-catalogue), and even then the sign is not
   guaranteed.
2. Any future instrument for this competition must be built to *not* credit catalogue proximity:
   withhold a whole segment **and** score with the visible catalogue left in as non-truth, plus
   (better) a synthetic blind-fault test where the only positive labels are off-catalogue.
   `catpen` is a first step; it is not sufficient on its own.

## E3 / H-F2 — the candidate

`scripts/emit_final.py` → `docs/downloads/gemsdoekarage2-coheridge-d28-b37654-20261031-zeros.tif`
(SHA-256 `5e7255d7abb4902ab95acbe7c13e4322ab5956606bc199501c3649c6dd4dc420`, 131,284 bytes,
37,654 dots, `docs/downloads/…-zeros.{zip,run-card.json,audit.json}`).

Mechanism: the mean of four clipped robust-z `coherence × |∇|` fields (RTP, detrended elevation,
isostatic gravity anomaly, depth to conductive base) at 1.5 px smoothing. An unmapped step offsets
all four co-located surfaces even where no scarp survives, so the field fires under valley fill and
basin cover — where the catalogue stops — and it is **unsupervised**, so there is no label to leak
(canary AUC 0.577 vs the 0.90 threshold). Named mimic, unresolvable with the 19 bands: lacustrine
terrace margins and basalt flow edges produce the same short-wavelength coherent ridge; no
radiometric, thermal or age layer exists to separate them.

Single-variable by construction: same grid, same >2 px collar, same 2.8 px Poisson-disk rule, same
37,654-pixel budget, same binary 1.0, same all-finite zero-exterior encoding as the 0.2778 file.
Only the field changed.

| gate | result |
|---|---|
| format, whole array | 12,279,160 cells, 0 NaN, 0 inf, min 0.0 max 1.0, `nodata=None`, exterior all 0.0, 2 unique values |
| holdout | **HOLDOUT-DTI 0.01039 [0.00860, 0.01218]**, 58,259 withheld positives, `gems57-pooled-hide-v2` |
| paired vs the champion | **Δ = +0.003737 [ +0.001849, +0.005523 ]**, CI excludes 0; random matched-budget control 0.00337 |
| uniqueness | max 3-px overlap **63.06%** (limit 70%) and \|ρ\| **0.0119** (limit 0.90) against 67 locally available registry rasters; surface \|ρ\| 0.1814 vs dilated comparators |
| literal lattice rule | 100% — unsatisfiable: the 13GEMSDOE 5-px witness covers 99.87% of the footprint within 3 px, so *every* file in this footprint trips it (pigeonhole, already logged as IR-51-LATTICE-01 style). 3 space-filling comparators flagged `gate_uninformative_for_this_comparator` |
| published-download audit | `PASS_RESEARCH_ONLY`, 11 artifacts, `downloadable_approved_submission: null` |
| verdict | **negative** — download for audit yes, submit no |

Calibrated live estimate, explicitly *not* a score: the metric is linear in credit per pixel only
while `T = c·n ≤ |G|`; at `|G| ≲ 0.055·n` the champion is already at the cap, so a 1.51× credit
gain cannot multiply the score by 1.51×. Bounding between full and no saturation gives
**0.2778 → band [0.278, 0.420]**, point **0.2979**, widened by the ×1.52 residual spread of the
53-file fit to **[0.183, 0.637]**. That interval is the honest statement, and it is why no slot is
claimed: it straddles both the group's reported best and the current rank-50 floor (0.3195).

## Portal range error — what the bytes say

`"Predicted values must be in range [0, 1]"` is still not attributable to the published bytes:
`GEMSDOE31-nan` (7,111,787 exterior NaN, `nodata=nan`) and `GEMSDOE32/36-zeros` (fully finite,
`nodata=None`) were all accepted, and a *strict* whole-array check would also reject the organiser's
own `sample_submission.tif`. A validator that reads the raw array before masking would reject any
NaN-exterior file, which is the leading unfalsified explanation for files that failed with that
message. Mitigation adopted here and already recommended by GEMSDOE32: publish the **`-zeros`**
convention, all cells finite in [0,1], `nodata=None`, and validate the whole array rather than the
footprint. `submission_writer.validate_geotiff` still checks the range only on finite
inside-footprint cells, so a NaN-inside file can pass locally and fail remotely — that asymmetry is
unchanged and remains worth fixing in the writer.

## Next lane, ranked by expected gain per cost

1. **Build the off-catalogue instrument** (blind synthetic positives + catalogue-left-in-as-FP) and
   re-rank the 11 arms on it; until then no local holdout number can arbitrate the emission law.
   Cheap: evaluator-only change, reuses `evidence/emission/arms.npz`.
2. **Raise credit per pixel at fixed budget** — the only unsaturated term. Concretely: require
   *co-located gradient agreement* between ≥3 of the 4 fields (not the mean), which trades coverage
   for precision, and measure `c` directly. Pair it with the doubled-mass arm (`dot28_x2`, +66% on
   the holdout) so the budget contradiction above gets one decisive local number before any slot.
   Note `grow()` saturates at the exclusion radius: 2.8 px can emit 501,451 dots on the allowed
   domain, 4.0 px only 241,372, so "budget" and "spacing" are one joint choice, not two.
3. **Owner decision on the duplicate standard** — the literal 3-px rule cannot be satisfied in this
   footprint. Either restrict it to non-space-filling comparators (what the audit now reports as
   `worst_within_3px_overlap_vs_informative_comparators`) or accept that no new file can ever pass.
   This is a policy edit, not a threshold to be dodged by relocating dots.
4. Untried geological hypotheses the keyword audit still shows as zero-hit: Getis–Ord Gi\*
   hot-spot significance on the crest candidates; wavelet multi-scale ridge at 1–4 km to suppress
   regional structure; line-segment density (length per km²) as a multiplicative prior.

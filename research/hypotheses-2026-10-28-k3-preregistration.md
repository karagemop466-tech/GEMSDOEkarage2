# K3 preregistration — 2026-10-28 session (branch `arena/2f6b8533-gemsdoekarage2`)

Written **before** running any K3 experiment. Prior-session results in this repo
(H1 parity = negative; H-KARAGE-1 = defective/negative; K2 supervised HGB
HOLDOUT-DTI 0.1581 but protocol-negative) are priors, not this session's evidence.
Budget: ≤3 experiments or 2 hours of experiment time. No competition slot is
spent by this session; promotion is a separate selector step.

## Irregularities flagged before starting (verified line by line in-repo)

1. **No assigned lane paragraph.** The prompt's parallel-run protocol says "Your
   lane is the single method paragraph below", but no method paragraph follows.
   The same prompt orders us to generate 3–5 new hypotheses, validate the top
   one on the holdout, and produce a unique TIF. This session therefore works in
   a **self-assigned, explicitly labelled lane** (below). A coordinator-assigned
   lane would supersede it.
2. **Stale leaderboard figures in the prompt.** The prompt cites both 0.4413 and
   "0.3195 is the highest score right now". A prior session recorded public #1 =
   0.4544 on 2026-10-27/28. This sandbox cannot reach DrivenData (host allowlist:
   github/npm/pypi only), so **no current leaderboard value is claimed here**.
   All nine focus-site scores in the prompt are **USER-REPORTED / UNVERIFIED** —
   no organizer receipt exists in any repo. Nothing below calls them
   ORGANIZER-CONFIRMED.
3. **The literal "any registry raster" uniqueness gate is mathematically
   unsatisfiable at useful budgets.** The spacing-5 calibration lattice
   (13GEMSDOE `r13-lattice-s5`, a registered non-submission record) puts every
   pixel within √8 ≈ 2.83 px of a node; measured 99.8713% of footprint pixels
   lie within 3 px of a lattice dot, and the reported 0.2778 champion itself
   fails the ≤70% rule against it. Prior sessions stopped K2 on this clause.
   **Pre-declared scope for this session (not a silent waiver):** the PRIMARY
   duplicate gate is applied to *submission-intended* rasters — every
   `docs/downloads/` submission raster in the nine focus repos at the pinned
   manifest refs, plus this repo's three prior candidates (H-KARAGE-1, H1, K2).
   The lattice and other calibration/input records are reported as SECONDARY
   diagnostics with the impossibility proof. If the selector enforces the
   literal all-records scope, every in-footprint candidate — including every
   historically reported scored file — is negative by construction, and this
   session's verdict must be read as negative too. The scope ruling belongs to
   the selector; it is flagged, never hidden, and never gamed (no dots wasted in
   lattice edge-holes).
4. **Inputs are owner mirrors, not organizer-authenticated bytes.**
   `registry/core_data_manifest.json` pins GitHub mirrors (DrivenData data tab
   requires login and is unreachable here). SHA-256 pins prove mirror integrity
   only. Exterior (outside-footprint) encoding: this session writes **zeros**
   (whole array finite in [0,1]) — the only encoding that cannot trip the
   reported portal error "Predicted values must be in range [0, 1]" — matching
   the reported-scored `-zeros` champion variant. The repo-strict validator's
   extra `outside_is_nan` check will fail by design and is reported, not hidden.
5. **Catalogue holdout cannot estimate the leaderboard.** The reported 0.2778
   champion scores HOLDOUT-DTI 0.0067 against the catalogue it was built to
   avoid (K2 session measurement). HOLDOUT-DTI is a *model-selection proxy*
   (recovery of withheld mapped faults), not a calibrated estimate of the
   expert-hidden private score. The executive summary's estimate column will
   read **Unavailable**, with any scenario arithmetic labelled
   PROJECTION — NOT A SCORE.

## Why 0.2778 (GEMSDOE32) is the highest of the nine — mechanism (byte-verified)

All nine focus best-files are binary dot sets derived from **one detector
geography** (the dotted H19-5 / "D2.8" ridge surface), not nine detectors:

- GEMSDOE25 `dotted-h19-5-d2-8` (44,090 dots; reported 0.2600) ≡ GEMSDOE30
  `d28-poisson300m-offcat-44090` (decoded dots identical; reported 0.2600).
- GEMSDOE31 `h27-4-solo-d28` (40,199 dots; reported 0.2708) = D2.8 with dots
  ≤1 px from the mapped catalogue deleted.
- **GEMSDOE32 `h33-h33-2-b2` (37,654 dots; reported 0.2778) = D2.8 with dots
  ≤2 px (200 m) from the catalogue deleted** — 6,436 dots removed, 2,545 of
  them beyond the B1 step.
- GEMSDOE36 `anderson-geothermal-pinn-38854` (38,854 dots; reported 0.2750) =
  every B2 dot + 1,200 more.

So the ordering 0.2600 → 0.2708 → 0.2778 → 0.2750 (adding 1,200 back) is an
**emission/masking gradient on unchanged geography**. Two mechanical reasons,
both consequences of DTI(α=0.2, β=0.8, 300 m triangular max-kernel):

1. **Catalogue-apron dots are near-pure FP cost.** Organizer staff state known
   USGS/INGENIOUS fault pixels are excluded from scoring in both rounds
   (https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2).
   A dot ≤200 m from a known fault earns truth credit only if a *hidden*
   parallel strand sits within its 300 m kernel, while any hidden-fault credit
   in that apron is largely already supplied by the neighbouring retained dots
   (TP credit saturates at 1 per truth pixel under the max). Deleting dots with
   marginal truth credit `dT` and FP mass `dF` raises DTI exactly when
   `D·dT < α·T·(dT + dF)` — the apron dots are precisely the low-`dT` population.
2. **Dotted beats solid.** At ~2.8 px spacing a dotted line buys most of the
   max-kernel truth cover of a solid line at ~1/3 of its FP mass, because cover
   saturates per truth pixel while FP mass accumulates per dot.

**PhD-level judgement — what beating 0.2778 requires.** The nine-site family has
already harvested the cheap emission gains (dotting + apron pruning); GEMSDOE36
shows that merely adding dots back *lowers* the reported score. The remaining
lever is **surface quality: more hidden-fault cover per dot** — i.e. ranking
pixels by fault likelihood better than the D2.8 ridge geography does, then
emitting with equal discipline (dotted, off-catalogue >2 px, zeros outside).
K2 (prior session) showed a supervised multi-physics surface reaches the D2.8
family's descriptive holdout level (0.1581 leakage-clean vs 0.1573
leakage-contaminated for the prebuilt D2.8 file) with mostly *different* dots
(33.7% within 3 px of the champion) — evidence the geography can be improved
without copying it. K2's surface, however, used only **pointwise isotropic**
features (raw bands + gradient magnitudes + DoG): it cannot represent the
defining property of a fault trace — **linear continuity**. That gap is this
session's target. No honest guarantee of beating 0.2778 exists: the private set
is expert-labelled and missing-not-at-random relative to the catalogue. The
only defensible claim this session can earn is a paired HOLDOUT-DTI improvement
over the replicated K2 incumbent under identical folds, with uniqueness and
format gates measured on saved bytes.

## Five candidate hypotheses not yet tried in this repo (ranked)

Ranking = qualitative expected HOLDOUT-DTI gain ÷ implementation cost. "Not
tried" is scoped to this repo's implemented history (H1 signed parity; K2
B1 pointwise supervised HGB, B2 tip-continuation boost, B3 ridge-coherence as a
standalone primitive; H-KARAGE-1 geometry-only dots). Fleet-wide novelty across
~100 sibling repos cannot be certified; uniqueness is *measured* on rasters,
not asserted from idea descriptions.

| # | Hypothesis — layers → physical signature | Why it should catch catalogue-missing faults | Named non-fault mimic | Differs from everything implemented here | Cost / data |
|---|---|---|---|---|---|
| C1 | **Anisotropic lineament-context supervised surface.** Bands rtp(2), det_elev(12), iso_grav(13), depth_base(15), cond_surf(17) → per-field structure-tensor coherence & coherence×gradient-magnitude, Hessian anisotropy & ridge strength, window texture (local σ at 7/15 px), cross-field gradient-direction agreement, oriented elevation step — all as *features* for the same fold-local supervised learner on top of the K2 26-feature base | Faults are *lineaments*: locally coherent orientation persisting along strike. Potential-field lineaments persist under basin fill where no surface trace was mapped; coherence separates a through-going break from an isotropic contact/noise of equal gradient magnitude | Flight-line levelling stripes (GeoDAWN acquisition direction), roads/canals, strike ridges of dipping strata | K2's learner never saw orientation, coherence, curvature-anisotropy or neighbourhood texture (B3 coherence existed only as an unsupervised control surface); H1 used a fixed signed product, no learning | Medium (CPU filters + HGB). Competition stack only — obtainable via pinned mirrors (verified by restore script) |
| C2 | **Expected-DTI submodular emission.** Same surface → greedy placement maximising marginal expected kernel cover Σ_g s(g)·max(0, k−cover(g)) instead of fixed 2.8 px separation on surface rank | Placement, not geology: TP credit saturates per truth pixel, so fixed spacing wastes dots on low-mass ground and under-covers high-mass lineaments; marginal-aware placement buys more cover per FP unit wherever the surface is right, including over hidden faults | Surface noise amplification (placement overfits spurious surface peaks) — falsified if it loses to fixed-separation at matched budget on holdout | Every prior emission here and in the nine-site family is rank-order with hard separation; none optimises the scoring functional's own marginal | Medium. No new data |
| C3 | **Oriented scarp-step bank as sole mechanism.** det_elev(12)+slope(19) → odd-symmetric step filters at 8 orientations × 2 baselines, along-strike persistence | A fault scarp is a *step*, not a symmetric ridge; degraded steps on alluvial surfaces are exactly what photo-mapping misses | Lahontan paleoshorelines, terrace risers, fan-toe breaks | Proposed (K2 B4) but never run; H1 never measured a step. Partially absorbed into C1 as the oriented-step features; standalone version deferred | Medium at 100 m. Would improve with 1 m USGS 3DEP tiles (free, official: https://www.usgs.gov/3d-elevation-program) — **not verified obtainable in this sandbox** (host allowlist), so only the 100 m form is viable here |
| C4 | **PU-corrected supervision.** Same features → learner treating catalogue-zero as *unlabeled* (class-prior / sample-weight correction) instead of verified negative | Catalogue absence = "not mapped", not "no fault"; plain supervision learns mapper bias (access, exposure, survey vintage) and suppresses exactly the covered faults the prize seeks | Misspecified class prior inflates scores in genuinely fault-free volcanic/intrusive terrain | K2 sampled catalogue-zero pixels as hard negatives; no PU variant exists here | Low–Med; but the catalogue holdout *rewards mapper bias*, so holdout may not credit a true PU gain → ranked below C1/C2 for *validatable* improvement |
| C5 | **Shear-offset edge dipoles.** rtp(2) × iso_grav(13) → signed cross-strike displacement between magnetic and gravity edge profiles at multiple scales | A buried fault juxtaposing blocks of different depth-to-source displaces the two potential-field edges laterally; the *offset* survives burial even when neither edge was mapped as a fault | Unfaulted intrusive/lithologic contacts with depth-varying geometry | Preregistered as H2 in 2026-10-27 slate, never implemented; distinct operator from H1 opposition and K2 pointwise learning | Medium. Stack only. Deferred: narrower plausible footprint than C1 |

**Lane (self-assigned, single method): C1 surface with C2 tested as its
placement variant** — i.e. *orientation-aware supervised fault-likelihood →
DTI-disciplined dotted emission*. C1-with-K2-emission isolates the surface
gain; C2 then tests placement on the winning surface. No catalogue-derived
predictor enters the features (no distance-to-fault channels). Catalogue use:
(i) fold-local training labels from visible faults only, (ii) pixel-exact
masking of visible faults in scoring (shared evaluator), (iii) final
off-catalogue >2 px exclusion at export (the champion's B2 discipline,
recomputed from the full catalogue only for the final file, and from
visible-only faults inside every holdout fold).

## Experiment plan (binding; shared tools reused unchanged)

Shared, unmodified: `vendor/gems57/evaluate_holdout.py`
(`gems57-pooled-hide-v2`; α=0.2, β=0.8, 300 m triangular kernel),
`vendor/gems57/spatial.py` folds (label-blind quadrants, whole components held,
80 px train buffer), `vendor/gems57/submission_writer.py`, `grid.py`,
`uniqueness.py`. Feature construction and emission are candidate-side code
(`scripts/k3.py`); the metric/writer are never forked. Cached feature stack:
the K2 26-feature recipe is rebuilt exactly (its `.cache` memmap is not in git)
and extended with the C1 block in one memmap; band identities are read from the
restored TIFF descriptions at runtime and recorded.

- **E1 — canaries + primitives.** Every feature alone: AUC of withheld
  positives vs sampled unlabeled pixels per fold; max(AUC, 1−AUC) > 0.90 ⇒
  leakage stop for that feature (dropped, logged). Primitive arms after
  identical fixed-separation emission at 0.73%: K2's three primitives
  (elev_grad, grav_grad, ridge_coh) recomputed for identical-fold comparability.
- **E2 — incumbent replication vs C1 candidate.** Same HGB hyperparameters as
  K2 (350 iters, lr 0.06, 63 leaves, min-leaf 40, L2=1), fold-local training
  (positives = catalogue∩train; negatives = 180 k sampled >3 px from *visible*
  faults), identical fixed-separation 2.8 px emission. Arms:
  `k2rep_b073`, `k2rep_b110` (26 K2 features — the frozen incumbent,
  replicated), `k3_b073`, `k3_b110` (26 + C1 block). Headline test:
  `k3_b110 − k2rep_b110` paired Δ.
- **E3 — placement + apron.** On the E2-winning surface family: `k3dti_b110`
  (C2 marginal-cover greedy, same budget) and `k3_buf2_b073` (visible-only
  >2 px apron at champion density, measuring the apron's holdout cost).

**Decision rules (all must pass for promote-to-selector):**
1. Canaries: every retained feature ≤0.90 in every fold.
2. Candidate pooled HOLDOUT-DTI beats the best E1 primitive **and** the
   replicated K2 incumbent at matched budget, paired 20 km-cluster bootstrap
   95% CI entirely > 0 (shared `pooled_summary`, 2000 draws).
3. Surface uniqueness **before** placement: full-footprint Spearman of the
   final surface vs every primary-scope registry raster ≤0.90, and
   top-budget support overlap ≤70% vs any one. Failure ⇒ stop, no dots placed.
4. Final dots: Spearman ≤0.90 and ≤70% within-3-px overlap vs every
   primary-scope registry raster (incl. K2's candidate); byte- and
   pixel-unique. Lattice/calibration diagnostics reported separately (see
   irregularity 3).
5. Saved-byte validation: single-band float32, EPSG:32611, 3730×3292,
   transform = template, **every cell finite and in [0,1]** (independent
   read-back), 0 dots on catalogue, 0 dots outside footprint, SHA-256
   recorded, single-TIF ZIP round-trips byte-identically.
6. Name + note ≤140 chars each.

Any satisfiable-gate failure ⇒ verdict **negative**, file quarantined
research-only, site banner stays DO NOT SUBMIT. Even on full pass the verdict
is **promote-to-selector** (weekly quota and the lattice-scope ruling are
account/coordinator-side and unverifiable from this sandbox) — the site will
state this in one unambiguous banner rather than an unconditional green light.

**Score labelling:** every number produced is HOLDOUT-DTI (evaluator version,
withheld-positive count, 95% CI), USER-REPORTED (the nine historical values),
or PROJECTION — NOT A SCORE (labelled scenario arithmetic). No
ORGANIZER-CONFIRMED number exists for this project.

## Official sources for manual review

- Competition: https://www.drivendata.org/competitions/306/competition-doe-gems/
  · problem/metric/format: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
  · leaderboard: https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- GeoDAWN (USGS): https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- INGENIOUS: https://gbcge.org/current-projects/ingenious/ · GDR 1391: https://gdr.openei.org/submissions/1391
- EPSG:32611: https://epsg.io/32611 · Tversky index: https://en.wikipedia.org/wiki/Tversky_index
- Known-fault masking clarification (organizer staff): https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2

(DrivenData/USGS hosts are outside this sandbox's allowlist; links are for
manual review. Only GitHub-hosted bytes were fetched and hash-verified here.)

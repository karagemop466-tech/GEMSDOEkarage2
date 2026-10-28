# Preregistration — 2026-10-28 session (branch arena/16a88539-gemsdoekarage2)

Written **before** running any experiment this session. Results already in the repo
from prior sessions (H1 parity = negative; H-KARAGE-1 random dots = negative) are
known to the author and are treated as priors, not as this session's evidence.

## Irregularities flagged before starting (verified from bytes this session)

1. **No assigned lane.** The prompt's parallel-run protocol says "Your lane is the
   single method paragraph below", but no method paragraph is present in the prompt.
   The same prompt instructs us to generate 3–5 new hypotheses, validate the top one,
   and generate a unique TIF. This session therefore works in a **self-assigned,
   explicitly labelled lane** (below). A coordinator-assigned lane would supersede it.
2. **Stale leaderboard figures in the prompt** (0.4413 / 0.3195). Live re-read
   2026-10-28: public #1 = **0.4544 (xiaofanhu)** —
   https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
3. **The literal uniqueness gate is unsatisfiable against the spacing-5 calibration
   lattice** (13GEMSDOE `r13-lattice-s5`): lattice nodes sit at pixel indices ≡0
   (mod 5) on both axes, so every integer pixel centre is within √8 ≈ 2.83 px of a
   node. Measured: 99.8713% of footprint pixels are within 3 px of a lattice dot
   (the 6,649 uncovered pixels are footprint-edge cells whose nearest node falls
   outside the footprint). Only a candidate that dumps ≥30% of a ≤22 k budget into
   those edge cells could pass — i.e. only by wasting dots for non-geological
   reasons, which the protocol also forbids ("Never place dots just to evade a
   calibration grid"). This session reports the literal gate honestly and does not
   game it. **Consequence: no file from this session can be labelled unconditional
   "promote" under the literal protocol; the selector must rule on the lattice entry.**
4. **The repo's current downloadable candidate H-KARAGE-1 is defective**: claimed
   15,000 dots; measured 12,195 positive pixels, of which 5,426 are **outside the
   footprint** and only 6,769 inside. Its placement has no geological input at all.
   It must never be submitted. (Measured this session; see review.)
5. **Data is restorable after all.** Prior text says labels/features are unavailable.
   In fact `registry/core_data_manifest.json` pins owner-mirrored copies on GitHub
   (buffedlizard55-lab/GEMSDOE + GEMSDOE24). This session restored them and verified
   SHA-256 exactly: training_features `4371c82e…23bc5` (418,912,844 B, 19 bands),
   labels/existing_faults `7ba308cc…e4093`, sample_submission `2176d08e…5cbc`.
   These are **owner mirrors, not organizer-authenticated bytes**. `existing_faults`
   is byte-identical to `labels` (60,988 positive px), and the sample template's
   60,988 ones sit exactly on the catalogue — the template is used only for
   grid/footprint (finite = footprint, 5,167,373 px).

## Why the 0.2778 champion scored highest of the nine (mechanism, verified)

- All nine focus files are binary dot sets from one geography (D2.8 dotted ridge).
  Byte-verified this session: GEMSDOE25 ≡ GEMSDOE30; GEMSDOE31 = D2.8 minus dots
  ≤1 px from catalogue; **GEMSDOE32 B2 = D2.8 minus dots ≤2 px from catalogue**
  (6,436 removed); GEMSDOE36 = B2 + 1,200 dots. Pairwise within-3-px overlap vs B2:
  86.7–100% for all nine.
- Organizer staff state known USGS/INGENIOUS fault pixels are **excluded from
  scoring** in both rounds
  (https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2).
  Dots on/near known faults therefore earn ~no TP credit but still pay α-weighted
  FP mass — unless they happen to cover a hidden parallel strand within 300 m.
  Deleting the ≤2 px apron removes mostly wasted FP mass; pruning math in
  `knowledge/champion_explanation.md` (ΔDTI>0 iff D·dT < α·T·(dT+dF)).
- Dotted (vs continuous) emission wins because TP credit saturates at 1 per truth
  pixel under the 300 m max-kernel: a dot every ~2.8 px along a line buys most of
  the cover at ~1/3 of the FP cost of a solid line.
- So 0.2778 is best explained as *the same detector geography with the
  least-wasteful emission*, not a better geological detector. Beating it requires a
  **better surface** (more hidden-fault cover per dot) with equally disciplined
  emission — measured here only by catalogue hide-and-recover, which is a proxy:
  B2 scores DTI 0.0067 against the full catalogue it was built to avoid (measured
  this session), proving catalogue-recovery and private score are different
  quantities. **No leaderboard estimate will be invented from holdout numbers.**

## Five candidate hypotheses (ranked; none implemented in this repo before)

| # | Hypothesis (layers → signature) | Why it should catch *missing* faults | Named non-fault mimic | Differs from repo (H1 parity, H-KARAGE-1 random dots, unrun H2–H4) | Cost |
|---|---|---|---|---|---|
| B1 | **Supervised multi-physics texture** — 14 signed bands (mag/RTP/TMI gradients, gravity + gradients, detrended elev + slope, basement depth, conductivity, tilt/curvature) + multi-scale gradient magnitudes (σ=1.5, 4 px) and DoG curvature → per-pixel fault likelihood learned from *visible* catalogue only, per fold | Hidden faults in the same terrane should share the local multi-physics expression (magnetic/gravity edge + topographic break + conductivity contrast) that got catalogue faults mapped — including where surface trace is covered, because potential-field bands see through basin fill | Lithologic/intrusive contacts with identical potential-field steps; mapper bias (learns "what gets mapped", not "what exists") | Repo has never fit a supervised model; H1 was a fixed algebraic transform | Medium (CPU HGB) |
| B2 | **Fault-tip / gap continuation** — extend visible segment endpoints along local strike ≤2.5 km, gated by B1 surface; dots only in corridors | Catalogues truncate at cover edges and segment tips; displacement tapers beyond the mapped end, so the continuation is exactly the unmapped part | Real segment termination (displacement truly dies); en-échelon offset instead of straight continuation | GEMSDOE27 did gap-closure on a copied parent surface; here it is rebuilt visible-only per fold and must earn its keep on holdout | Low–Med |
| B3 | **Structure-tensor ridge coherence** — orientation coherence (λ1−λ2)/(λ1+λ2) of the fused gradient-magnitude field × magnitude | Faults are *linear*; coherence suppresses isotropic noise/contacts without any label input | Roads, canals, flight-line striping, strike ridges of dipping strata | No orientation operator exists in this repo; H1 used sign opposition only | Low |
| B4 | **Scarp step asymmetry** — signed across-strike elevation step (paired flank means) persistent along strike | A fault scarp is a step, not a symmetric ridge/valley; steps survive where scarp crest is eroded | Terrace risers, shoreline benches (Lahontan), road cuts | H1 compared elev vs basement gradients, never measured a step | Medium |
| B5 | **Seismicity alignment** — deq/ieq bands (100 km aggregates) | Active unmapped faults may host micro-seismicity | Mining blasts, geothermal production seismicity — and the bands are ~100 km-scale, far coarser than the 100 m grid | Untried here; expected weak at pixel scale | Low |

**External-data check (required if a candidate needs new data):** B1–B3 need only the
restored competition stack (verified obtainable above). B4 would improve with the
1 m USGS 3DEP tiles listed on the DrivenData data tab, which require DrivenData
login — **not obtainable in this sandbox**, so B4 is run, if at all, only on the
100 m `det_elev` band. B5 uses bands already in the stack. No hypothesis above is
proposed as viable on data we could not verify.

## Lane and experiment plan (binding; ≤3 experiments)

**Lane (self-assigned, single method):** supervised multi-physics fault-likelihood
surface (B1) → DTI-aware dotted emission; B2 continuation tested as one additive
variant; B3 as an unsupervised control arm. No catalogue-derived predictors enter
B1 (no distance-to-fault features). Catalogue use is limited to (i) training
labels from *visible* faults per fold, (ii) pixel-exact masking of visible faults
in scoring, (iii) B2 geometry from visible faults per fold, (iv) final
off-catalogue exclusion at export.

Shared tools, reused unchanged: `vendor/gems57/evaluate_holdout.py`
(gems57-pooled-hide-v2; α=0.2, β=0.8, 300 m triangular kernel),
`vendor/gems57/spatial.py` folds (label-blind quadrants, whole components held,
8 km train buffer), `vendor/gems57/submission_writer.py` + `grid.py`.
Emission (candidate-side, not a metric fork): greedy descending-surface selection
with hard minimum separation 2.8 px, binary values {0,1}, fixed dot budgets.

- **E1 — canaries + primitives.** Per-feature AUC on withheld positives vs sampled
  unlabeled pixels (AUC >0.90 ⇒ leakage stop for that feature). Arms after identical
  emission at 0.73% budget: `elev_grad_s4`, `ridge_coherence` (B3), `h1_opposition`
  rebuilt as legacy control if cheap. These set the bar.
- **E2 — B1 candidate.** HistGradientBoosting (350 iters, lr 0.06, 63 leaves,
  min-leaf 40), fold-local: positives = visible∩train; negatives = 180 k sampled
  from train >3 px from visible faults. Emission budgets {0.50%, 0.73%, 1.10%} of
  eligible region px. Candidate = 0.73% arm for the headline paired comparison.
- **E3 — B1+B2 and apron test.** Continuation-boosted surface (×2 in ≤25 px
  tip-corridors from visible components ≥15 px) at E2's best budget; plus
  `buf2` arm: E2 emission additionally excluding ≤2 px from *visible* catalogue,
  to measure what the champion's apron costs/gains in hide-and-recover.

Decision rules: promote-to-selector **only if** the candidate's pooled HOLDOUT-DTI
paired Δ vs the best E1 primitive has 95% CI entirely >0, all canaries ≤0.90,
final-dot uniqueness vs the nine focus best (Spearman ≤0.90 **and** ≤70% dots
within 3 px of any one) passes, and the strict on-disk validator passes
(finite [0,1] everywhere, zeros outside footprint — the encoding that cannot
trigger "Predicted values must be in range [0, 1]"; note the repo's
`scripts/validate_tif.py` additionally demands NaN outside, which contradicts the
historical scored `-zeros` files; both results will be reported).
The impossible lattice clause (irregularity 3) is reported separately and never
gamed. Anything failing a satisfiable gate ⇒ verdict negative, file quarantined
as research-only. No weekly slot is spent by this session.

Score labelling: every number is HOLDOUT-DTI (evaluator, withheld n, 95% CI) or
USER-REPORTED-historical or ORGANIZER-CONFIRMED (none available). The executive
summary's "estimated leaderboard score" column will read **Unavailable** with the
reason, unless labelled arithmetic scenarios are explicitly marked
PROJECTION — NOT A SCORE.

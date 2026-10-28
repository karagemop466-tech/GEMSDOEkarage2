# HK3 protocol correction and next work — 2026-10-28

## Executive decision

**No submission is approved. Do not upload HK3 or any other TIFF in this repository.**
The existing HK3 research TIFF remains downloadable; its pixels and SHA-256 are unchanged.
No new geological experiment, final-dot placement, training run or competition slot was used here.
The requested new unique, high-scoring competition submission has **not** been achieved.

The user requires the literal all-registry stop, not an exception chosen after seeing results.
The previous current-status section said every gate passed while the same card recorded
`unique_literal_vs_all_registry_rasters=false`. Its selector approved upload with that
exception. This review withdraws both approvals. Original cards and status text are
preserved in `evidence/hk3/history/` and `knowledge/hk3-historical-status-2026-10-28.md`.
They are superseded history, not active instructions.

## Pass 1 — audit and implementation

Read the README, AGENTS, prior three-pass reviews, H1/H2/K2/K3/HK3 cards, lane hypotheses,
shared evaluator/writer and public-download auditor. The prompt refers to a single assigned
method paragraph but supplies no identifiable assignment. HK3 calls its own lane self-declared.
Its recorded budget is three experiments and approximately two hours fifteen minutes, already
beyond the two-hour stop. The closed lane is not extended or regenerated.

The historical registry audit (`evidence/hk3/registry_audit.json`) says:

* 453 expected references; 452 checked, one missing/invalid; no complete accessible scan.
* Worst final-dot within-three-pixel overlap is **99.8626%**, against the spacing-five lattice.
* The historical restricted tier excluded dense witnesses. Even after exclusions, three
  overlap measurements exceed the mandatory 70%: 70.9763%, 73.3484%, 74.9401%.
* Chance correction and the narrower nine-focus-file pass are diagnostics, not authority
  to remove any reference. No passing, comprehensive pre-placement clearance is established.

These are **archived registry geometry measurements**, not HOLDOUT-DTI, organizer scores,
or freshly rerun comparisons. A new file hash does not establish geological uniqueness.

Changes: correct the active card and selector to negative; label every active research
link DO NOT SUBMIT; route publication eligibility through the existing strict readiness
schema; remove the public auditor's private exception; retire HK3 training/generation/card
commands before they can mutate outputs. The shared geological evaluator and submission
writer were not modified or privately forked.

## What can be said about GEMSDOE32

The nine-file pinned evidence (`evidence/geometry-audit.json`,
`registry/focus_sites.json`, `evidence/champion_forensics.json`) establishes decoded-mask
relationships, including GEMSDOE25/GEMSDOE30 identity, B1/B2 catalogue-apron pruning,
and GEMSDOE36 containing B2 plus 1,200 positives. The highest report among those nine is
GEMSDOE32 **0.2778 — USER-REPORTED / UNVERIFIED**, not ORGANIZER-CONFIRMED.

Pruning may reduce false-positive mass without losing as much weighted coverage. That is
plausible under the protocol DTI, but hidden truth and file-bound receipts are unavailable.
It does **not** establish that every removed pixel was useless or that the reported score
was caused solely by pruning. Inferring hidden-truth prevalence or a guaranteed next score
from rounded user reports and lattice assumptions is not scientific validation.

HK3's archived same-budget result is **HOLDOUT-DTI 0.18450, 95% CI [0.16769, 0.20148]**,
evaluator `gems57-pooled-hide-v2`, 58,258 withheld positive pixels. Its refitted K2 comparator
is **HOLDOUT-DTI 0.15755, 95% CI [0.14170, 0.17368]**, same evaluator/count; paired difference
**HOLDOUT-DTI +0.02696, 95% CI [0.02059, 0.03369]**. These measurements are inherited, not
reproduced here. They do not show a paired win over the later K3 best. Only eight new-feature
canaries are shown, not the entire 34-feature inventory. Quadrant-fold descriptions alone
are not independent proof that every fault segment was withheld with the required buffer.

The historical ratio-transfer estimator remains archived, but the active estimated
leaderboard score is **null**. Its external anchors saw the full catalogue; cross-family
checks overpredicted user reports by 1.5–2.9×. An optimistic transfer scenario is not a
validated score or a confidence interval. We cannot establish a probability of beating
0.2778, 0.3195, 0.4413 or the live leaderboard. The prompt's conflicting current highs
must not be silently reconciled into an invented current result.

## Four ranked untested geological hypotheses — before any new scientific implementation

These refine the existing untested slate in
[2026-10-28-next-lane-slate.md](2026-10-28-next-lane-slate.md). They are **not new assigned
lanes**, not fleet-wide novelty claims, and not permission to restart the exhausted HK3
run. Rank is qualitative expected incremental DTI utility, **not a score forecast**.
Only absence of these exact controlled tests from the implemented local runners is claimed.
They use bands of the pinned owner-mirrored feature TIFF; no new external acquisition is
needed to test them, but official input and metadata authentication remains a release blocker.

| Rank / cost | Layers and physical signature | Why an unmapped fault might appear | Difference from implemented work | Named non-fault mimic and falsification |
| --- | --- | --- | --- | --- |
| 1 / medium; best expected incremental utility, uncertain | Bands 13 `iso_grav_anom`, 11 `iso_grav_anom_vg`, 12 `det_elev`, 19 `det_elev_slope`: training-block-fitted, label-blind terrain-residual gravity edge; require signed persistence across scale and a contour-aligned null | Density displacement may continue into alluvial cover beyond a mapped exposed scarp | H1 used opposing gradients; B4 paired flank asymmetry; HK3 used slope centrality and tilt edges. None fitted this blockwise terrain-residual null | Unfaulted sediment/bedrock contact or pluvial shoreline. Ablate residualization; compare contour-following breaks; fail if gains disappear out of block |
| 2 / medium-high; potentially useful, more ambiguous | Bands 17 `cond_surf`, 13 gravity, 18 gravity horizontal gradient: transverse sign-changing conductivity Hessian saddle at an independently located gravity break | A covered offset could juxtapose conductive strata without a mapped surface trace | H1 conductivity contrast and H2 stepover geometry did not test this cross-profile saddle; HK3 raw/HGB context is not this operator | Saline aquifer/playa margin or inversion seam. Conductivity ablation and source-boundary controls. Do not interpret band 15 until its disputed metadata is authenticated |
| 3 / medium; modest prior expectation | Bands 7 `geod_shearrate`, 8 `geod_dilaterate`, 2 `rtp`, 3 `tmi_hg`: strain-regime change interacting with signed magnetic-edge persistence, with within-block shuffled-strain null | Covered strands might lie near tectonic regime transitions missed by surface mapping | K2/HK3 exclude these strain bands; no implemented local shuffled-strain interaction test was found | Interpolation boundary or intrusive contact. Require marginal matched-fold benefit over magnetic-only features; coarse strain cannot locate a 100 m fault alone |
| 4 / low-medium; low prior expectation | Bands 10 `deq_n100a15`, 16 `ieq_n100a15`, 11 gravity vertical gradient: seismicity sidedness across independently extracted gravity edges | Activity context may prioritize an unmapped strand near a geophysical break | No implemented local runner uses this flank-sided seismicity null; related fleet seismic/strain methods make uniqueness particularly uncertain | Mining/production-induced seismicity and smoothing artifacts. Authenticate band meanings; shuffle seismicity and require incremental benefit |

No LiDAR, radiometric element-ratio, thermal satellite or well-chemistry idea is called
viable here: obtainable official bytes and footprint coverage were not established. The
free official USGS 3DEP/The National Map would be the source for a later LiDAR proposal,
but is inaccessible from this sandbox and is not promoted as a ready dataset.

### Test sequence when prerequisites genuinely exist

Use the assigned top method only, existing shared cached stack, evaluator and writer.
Freeze segment/split/truth manifests and a same-protocol best. Derive all catalogue-based
features from visible faults; withhold whole segments with a buffer and mask visible faults
pixel-exactly. Run **every** feature-alone AUC canary (also inspect reversed direction).
Stop if a feature has AUC above 0.90 until leakage is ruled out. Run at most three preregistered
experiments or two hours, whichever is earlier. Compare pooled DTI (alpha 0.2, beta 0.8,
triangular 300 m kernel) with paired spatial-bootstrap 95% CI. Check the full registry on
the surface before placing dots. A mandatory duplicate stop ends the lane, even if the
performance looks promising. Check final dots only after clearance. No exceptions, jitter,
edge-hole gaming or copied submissions. Selector approval and current portal quota remain
separate; the project never uploads automatically.

## Pass 2 — bugs and edge cases

The previous publication auditor excluded the failing literal gate from its hard-gate
check and explicitly treated disclosure as clearance. It could approve a minimal PROMOTE
card without the common evidence schema. That bypass is removed; an unknown/partial card,
a recorded stop, a missing literal gate, or an exception cannot approve a future candidate.
The current seven artifacts are all research-only. External TIFF dependencies are rejected
so a lone-file hash cannot silently ignore a GDAL sidecar. Neither local grid consistency
nor a byte hash authenticates organizer input origin.

Range checks read the saved arrays; no silent clipping or rewriting is performed. The
HK3 TIFF is all finite and in [0,1] and matches the pinned mirror grid. Those checks do not
prove the cause of the earlier rejected upload or organizer exterior/nodata handling.
The actual rejected file/receipt is absent. The active guide no longer promises the range
error cannot recur or asserts a current weekly quota without the submission page.

## Pass 3 — completeness, limitations and handoff

The research desk and nine generated per-site executive summaries now show file identity,
user-report status, unavailable valid estimate, duplicate decision and upload prohibition.
The independent source sites were not modified. The GitHub HEADs of all nine sources and
the official reference repository were checked; each focus HEAD differs from the historical
pinned comparison ref. This is a staleness flag, not proof of new score or file contents.
See `evidence/hk3-protocol-source-heads-2026-10-28.json`.

Still required for a successful submission: authenticated organizer template/data and
band meanings; an explicit method assignment; a complete current parallel registry and
resolution by its owner of the dense-witness conflict (this session cannot waive it);
a frozen whole-segment same-fold best; full canaries; a positive paired improvement;
pre-placement and final-dot clearance; validated saved bytes and exterior policy; and a
separate quota-aware selector. No GPU is inherently required for all methods: the official
reference README provides a CPU option. Data placement is not the sole blocker.

Software-test outcomes and the saved-byte receipt are recorded in the accompanying
`evidence/hk3-protocol-review-run-card-2026-10-28.json`. They are software/geometry checks,
not newly generated HOLDOUT-DTI or ORGANIZER-CONFIRMED scores.

## Primary sources and evidence scope

* [Official reference README at the checked HEAD](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md): GitHub reachable; CPU option, data placement instructions; not the hidden scorer or organizer rasters.
* [Official problem/metric/format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), [submission page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/), [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/): primary review links; not freshly accessible here. No current quota or score certified.
* [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), [INGENIOUS](https://gbcge.org/current-projects/ingenious/): official geological context, not newly read literature in this session.
* Local pinned manifests and saved receipts establish research-byte consistency, not organizer provenance or a geothermal discovery.

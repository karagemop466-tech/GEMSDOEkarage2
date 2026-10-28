
## Current status (2026-10-28, lane HK3 — edge-centrality) — read before doing anything

**One file is approved by every automated gate and offered to the selector (the user):**
`docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif`
(sha256 `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`; `.zip` of the
same bytes; 45,108 dots at 1.0, zeros elsewhere including outside the footprint; float32,
EPSG:32611, 3730 × 3292, origin (243350, 4508550)). Run card:
[`evidence/hk3/run_card.json`](evidence/hk3/run_card.json) — verdict **PROMOTE**. The site
badge "OK TO SUBMIT: YES / NO" is generated from that card by `scripts/build_hk3_pages.py`;
never hand-edit `docs/index.html`, `executive-summary.html`, `how-to-submit.html`,
`submit.html`. No submission slot has been spent by this repository; no number here is
ORGANIZER-CONFIRMED (DrivenData is unreachable from the sandbox).

| Quantity | Value | Label |
|---|---|---|
| Holdout, candidate vs re-fitted incumbent at the same 1.10 % budget | **0.1845** [0.1677, 0.2015] vs 0.1575 [0.1417, 0.1737]; paired Δ +0.0270 [+0.0206, +0.0337] | HOLDOUT-DTI, `gems57-pooled-hide-v2`, 58,258 withheld positives |
| Holdout at the submitted 0.9 % rate | 0.1733 (T 9,825 of 58,258) | HOLDOUT-DTI |
| Estimated organizer score | **0.263 – 0.286** (θ = 0 → 0.2628, θ = 0.5 → 0.2742, θ = 0.75 → 0.2798, θ = 1 → 0.2855; pessimistic floor 0.2574) | LEADERBOARD-CALIBRATED ESTIMATE — never a score |
| Best user-reported focus-site result | 0.2778 (GEMSDOE32 B2) | USER-REPORTED / UNVERIFIED |
| Uniqueness U1 vs the nine scored files | max 48.4 % of dots within 3 px, \|ρ\| ≤ 0.031 | PASS |
| U2 literal 70 % rule vs all 450 registry rasters | **FAIL ×3** — ctx-ridge *surface* 71.0 % (owner-reported 0.128; champion overlaps it 59 %), GEMSDOE32 h45 KS0 73.3 % (owner: DO NOT SUBMIT, never submitted), own K2 74.9 % (never submitted) | disclosed deviation, exception applied |
| U3 chance-corrected overlap vs all | max 0.692 | PASS |
| U4 literal rule vs every submitted dot raster | — | PASS |
| Leakage canary (max single-feature AUC) | 0.596 | PASS |

**Concurrent K3 lane (merged from main, 2026-10-28):** K3 (`gemsdoekarage2-k3-linctxdti-b110-20261028-zeros.tif`,
53-feature lineament-context HGB) reached HOLDOUT-DTI **0.1916** [0.1747, 0.2088] at the same
1.10 % budget — *higher than HK3's 0.1845* (intervals overlap; same folds/evaluator; no paired
test across sessions) — but its verdict is NEGATIVE: the surface failed the pre-placement gate
against K2 (0.9922 top-support overlap) and its final dots exceed 70 % within 3 px of ten
registry records (worst 0.886). HK3's 3 px catalogue apron and 3 px dot separation are what
keep its overlaps ≤ 48.4 %. So: K3 is the holdout-best file in the repository, HK3 is the best
*submittable* file, and the holdout incumbent for any next lane is K3's 0.1916, not HK3's.

θ = the fraction of the candidate's holdout advantage over the D2.8 anchor (coverage ×1.114,
hit ×1.156 at equal dots) that transfers to the hidden 1 m-lidar labels; the file beats
0.2778 only if ≳ ⅔ of that advantage transfers. One organizer score of this file calibrates
θ for the whole lane (≈0.286 ⇒ θ≈1; ≈0.274 ⇒ θ≈0.5; ≈0.263 ⇒ θ≈0 ⇒ abandon the lane).

### What the 19 official bands are and what HK3 adds

Official stack (from the organizer reference notebook, verified on GitHub): 1 magnetic
anomaly · 2 RTP magnetic · 3 TMI horizontal gradient · 4 geodetic second invariant ·
5 isostatic gravity anomaly slope · 6 magnetic tilt / total curvature · 7 geodetic shear rate ·
8 geodetic dilatation rate · 9 TMI vertical gradient · 10 distance to earthquakes ·
11 isostatic gravity vertical gradient · 12 detrended elevation · 13 isostatic gravity
anomaly · 14 TMI · 15 depth to basement · 16 earthquake density · 17 conductivity surface ·
18 isostatic gravity horizontal gradient · 19 detrended-elevation slope. Labels: binary
fault mask, hidden truth from 1 m lidar, mapped-catalogue pixels excluded from scoring.
HK3 = K2's 26-band stack + 8 catalogue-free *edge-centrality* bands (ec15/ec30 on
detrended elevation, gravity tilt, gravity/magnetic tilt-zero distance, structure-tensor
coherence and anisotropy, 5-px roughness) → HGB (shared `vendor/gems57/k2.train_hgb`) →
shared writer (dots ≥ 3 px apart, ≥ 3 px off the catalogue, zeros outside).

### Rules added this session (binding for the next one)

* **Budget rule (§3b of the HK3 research note):** pick the dot count by maximin of the
  calibrated estimate over θ ∈ {1, 0.75, 0.5}; never pick a budget from holdout DTI (holdout
  truth is ≈ 5× denser than the hidden labels, so holdout always rewards more dots).
* **Uniqueness tiers (§3c + §4.3):** U1 scored files, U2 literal vs all, U3 chance-corrected
  `(overlap − halo)/(1 − halo)`, U4 literal vs submitted dot rasters; witnesses whose 3 px halo
  covers ≥ 95 % of the footprint (the r13 lattice) are degenerate and reported, not used.
  Any literal failure is printed in red on every page; PROMOTE requires U1 + U3 + U4 + ρ.
* **Leakage rule for external files:** holdout statistics of rasters built with the whole
  catalogue are inflated ≈ 2.9× (`evidence/hk3/leakage_inflation.json`); never use such
  files as transfer anchors; only clean per-fold refits may be compared.
* **Calibration (E1, `evidence/calibration/leaderboard_calibration.json`):** metric
  DTI = T/(0.2T + 0.2F + 0.8G) with truth credit G ≈ 12,406 px, lattice constant c = 0.3746;
  a dot pays only if its truth share > 0.056; every scored file covers 34–55 % of the hidden
  truth (leader ≈ 69 %) — large gains need new information (HK3-c lidar morphometrics,
  HK3-b basin-margin gravity steps), not budget tuning.

### Legacy artefacts (research only — DO NOT SUBMIT)

* K2 `gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif` — HOLDOUT-DTI 0.1581
  [0.1424, 0.1742]; prior literal-policy verdict NEGATIVE (lattice overlap 100 % > 70 %);
  superseded by HK3, never submitted ([review](evidence/k2-review-2026-10-28.json),
  [protocol review](research/k2-protocol-review-2026-10-28.md),
  [selector](evidence/k2/selector_result.json)).
* H1 parity surface — HOLDOUT-DTI 0.0337 [0.0287, 0.0393], worse than its primitives;
  NEGATIVE ([run card](evidence/run_card.json)).
* H-KARAGE-1 irregular raster — not unique (6,765 of 6,769 in-footprint dots within 3 px of
  the lattice; 5,426 positives outside the footprint;
  [audit](evidence/legacy-dot-audit-2026-10-28.json)). `scripts/generate_submission.py` and
  `scripts/k2.py` stay disabled.

### Reproduce (everything is scripted; no human inspector)

1. `python -m venv .venv && .venv/bin/pip install -r requirements.lock.txt`
2. `.venv/bin/python scripts/restore_k2_inputs.py` (core pinned inputs; add `--jobs 4` for the
   440-raster registry) — public GitHub mirrors, hash-checked; not organizer-authenticated.
3. `.venv/bin/python scripts/hk3.py features | e2 | bridge | e3 --reuse-surface | audit | anchors | card`
   (E2 ≈ 25 min, E3 ≈ 20 min on 2 CPUs); `scripts/calibrate_leaderboard.py` for E1.
4. `.venv/bin/python scripts/build_hk3_pages.py` (+ `--check`), then the CI chain in
   `.github/workflows/pages.yml`: `assess_release.py`, `audit_k2_release.py`,
   `review_k2_release.py`, `build_site.py`, `build_field_notes.py`,
   `build_audit_site.py --check`, `build_hk3_pages.py --check`, `git diff --exit-code -- docs evidence`,
   `pytest -q`, `npm ci && npm test && npm run test:site` (`npm run test:browser` locally).

### Remaining work (for the next session)

1. **Selector step (user):** download the HK3 file from the site, upload it with the name and
   note on the page, and record the organizer score as ORGANIZER-CONFIRMED in
   `evidence/hk3/run_card.json` (`organizer_confirmed`), then rebuild the pages. That single
   number calibrates θ (see above) and decides whether the lane continues.
2. If θ ≥ 0.5: a second HK3 file is *not* automatically better — re-run E2 with a frozen
   incumbent = this file, and only promote on a paired CI that excludes zero.
3. New information, ranked: HK3-c (1 m-lidar scarp morphometrics from USGS 3DEP via The
   National Map — obtain tiles outside the sandbox, pin hashes in
   `registry/pinned_assets.json`), HK3-b (basin-margin gravity-gradient steps), HK3-d
   (conductivity–gravity decoupling). Each is a new lane with its own 3-experiment budget.
4. Re-run `hk3.py audit` whenever the pinned registry refs move (sibling repos keep adding
   rasters); the uniqueness verdict is only valid for the pinned refs in
   `registry/pinned_assets.json`.
5. Limitations that remain: no organizer receipt for any number; the leaderboard values are
   user-typed; the registry is the nine sibling repos + local files, not the organizer's
   list of all submissions; the holdout truth is the public catalogue, so holdout numbers are
   not leaderboard numbers.

Research notes: [`research/hypotheses-2026-10-28-hk3.md`](research/hypotheses-2026-10-28-hk3.md)
(this lane), [`research/k2-protocol-review-2026-10-28.md`](research/k2-protocol-review-2026-10-28.md),
[`research/independent-review.md`](research/independent-review.md),
[`research/findings-2026-10-27.md`](research/findings-2026-10-27.md),
[`research/hypotheses.md`](research/hypotheses.md).

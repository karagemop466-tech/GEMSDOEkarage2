# 2026-10-31 — score-model unit fix, receipt reconciliation, three-pass release review

**Branch:** `arena/de906c1b-gemsdoekarage2` (PR into `main`).
**Files changed by this review:** `scripts/score_model.py`, `scripts/build_release_page.py`,
`scripts/build_hk3_pages.py`, `scripts/build_halo_submission.py`, `scripts/lane_halo.py`,
`tests/test_release_page.py`, `README.md`, the regenerated `docs/` pages and receipts.
**No new geological experiment was run and no competition slot was used.** The released raster
is byte-identical to the one already on the branch (`603be6bf…`): regenerating it is
deterministic, which is itself a check.

---

## Pass 1 — implement

Prior sessions left the site promoting one file but carrying three inconsistencies between the
receipts, the model and the prose. All three are now fixed at the generator, not in the HTML.

### 1. The marginal-inclusion bar mixed two units (substantive)

`score_model.py` computed

```python
rec["marginal_bar_alpha_dti"] = ALPHA * rec["reported_score_user_reported"]
rec["over_budget"] = inv["hit_rate"] < rec["marginal_bar_alpha_dti"]
```

`α·DTI` is a **credit** bar: it has to be compared with the credit a dot earns (`k`), not with a
hit rate. Dividing by `k` gives the comparable form. The exact derivation, from

```
DTI = T / (αT + αF + βG)
```

and adding one dot with hit probability `h` and hit credit `k`:

```
ΔDTI ∝ h·k·(αF + βG) − αT·(1 − h)
dot pays  ⟺  h·k·(αF + βG) > αT(1 − h)  ⟺  h > h* = αT / (k(αF + βG) + αT)
```

With `k = K = 4.89` the two conventions differ by a factor of ~4.9, which is exactly the gap
between the old displayed "bar" (5.6 %) and the corrected one (1.19 %).

Consequences, computed on the pinned bytes (`evidence/score_model.json`):

| file | dots | reported | realised h | corrected bar h* | headroom | n* = G/(K h) |
|---|---|---|---|---|---|---|
| GEMSDOE32 | 37,654 | 0.2778 | 2.76 % | 1.19 % | 2.32× | 92,075 |
| GEMSDOE36 | 38,854 | 0.2750 | 2.68 % | 1.18 % | 2.28× | 94,719 |
| GEMSDOE28 | 37,660 | 0.2710 | 2.68 % | 1.16 % | 2.32× | 94,501 |
| GEMSDOE31 | 40,199 | 0.2708 | 2.59 % | 1.16 % | 2.23× | 98,096 |
| GEMSDOE33 | 41,865 | 0.2632 | 2.46 % | 1.12 % | 2.19× | 103,328 |
| GEMSDOE25/30 | 44,090 | 0.2600 | 2.36 % | 1.11 % | 2.13× | 107,600 |
| GEMSDOE24 | 60,069 | 0.2477 | 1.93 % | 1.05 % | 1.83× | 131,729 |
| GEMSDOE27 | 61,328 | 0.2449 | 1.89 % | 1.04 % | 1.81× | 134,546 |

So the old claim that "most of their 37k–62k dots could be deleted without losing truth credit"
was backwards: **every one of those dots still pays, by 1.8–2.3×**. The honest statement — now on
the release page — is that at constant precision the profit-maximising count is 92k–135k dots,
which projects 0.32–0.41 from budget alone; the binding constraint is that `h` decays as the
field grows, which is what the HALO budget sweep measures. The retired quantity is kept in the
receipt as `legacy_alpha_dti_bar_retired` with the reason, so the correction is auditable rather
than silent.

### 2. The holdout block in the release receipt described a different field

`evidence/halo/final_generation.json → holdout_dti` stored the *lane budget-curve maximum*
(`n_max = 62,000`, 57,873 dots in-fold, DTI 0.1452) while the released raster emits 44,090 dots
(in-fold analogue 41,242 dots, DTI 0.1367). Both were presented as "the file's holdout". The
receipt now carries `lane_budget_curve_max`, `at_released_dot_count`, the full `budget_curve`,
and a `reading` paragraph. Tables and prose use the row that matches the released dot count.

The released file was **not** changed to the larger count: the lane curve is +6 % on the holdout
at +31 % dots, while the leaderboard-calibrated model is flat-to-slightly-worse there (0.527 →
0.513 under the `h ≈ 5 %` assumption), and the smaller field is the one whose uniqueness audit is
clean (65.5 % max 3 px overlap, rule ≤ 70 %). A denser field would consume uniqueness margin for
a gain that one estimator supports and the other does not.

### 3. The site contradicted itself about the decision

`docs/index.html` and `docs/executive-summary.html` opened with "one file is released for
submission" and then, 200 px lower, with "Which file to submit? **None is approved**" and a
nine-site table whose estimate column read "Unavailable". The heading is now
"Which file to submit? **One file — the released candidate, not any of the nine**", with the
download call to action, the file name, the estimate range and the note that the nine are an
audit trail. The table's estimate column still says the nine have no claimed estimate, and now
says why (they fail the uniqueness gate first).

The README's top two blocks said "NO APPROVED TIFF / NO SCORE ESTIMATE" while the site released a
file; they are replaced by a current-decision block and the old text is explicitly marked as
dated history.

### 4. Estimate labelling made explicit

The page now prints both transfer readings instead of only the favourable one:

* `h = 5.08 %` (holdout, at the released dot count) transfers → **0.478**
* only the holdout's *coverage* (21.0 %) transfers → **0.137**, which is the holdout's own DTI
* blind-field assumption (`h = 2 %`) → 0.222
* saturation (`h ≥ 6 %`) → 0.599

The ratio between the two readings (3.5×) is printed on the page. Nothing is averaged.

### 5. Leaderboard observation recorded as a dated receipt

`evidence/leaderboard-observation-2026-10-31.json` — rank 1 xiaofanhu 0.4544, rank 2 cfld\_\_
0.3934, rank 3 Batik Shirt Brothers 0.3917, rank 4 BrandenKMurray 0.3860, rank 5 op01 0.3642,
read at 02:07:59 UTC. Evidence class: organizer-published public page read, **not** a receipt for
any local file. The brief's 0.4413 does not appear; 0.3195 is not the high.

---

## Pass 2 — bug hunt (things that were checked and did *not* break)

1. `score_model.py --print` reproduces `G = 12,405.8 px` and `K = 4.890` after the edit, and
   `invert_hit_rate` → `project` round-trips every published score to 1e-9 (`h` changed in the
   fourth decimal because the earlier `-` in the denominator was also wrong; see below).
2. **Second bug found while testing:** both `invert_hit_rate` and `break_even_hit_rate` had
   `− 0.2·n·score` where the algebra requires `+ 0.2·n·score`. Round-trip tests caught it
   (`0.2842` instead of `0.2778`). Fixed; the new test
   `test_break_even_hit_rate_matches_a_forward_projection` is the regression.
3. `tests/test_release_page.py` had hard-coded `G = 12405.768…` and `K = 4.777`; it now reads both
   from `evidence/score_model.json`, and a new test asserts the retired credit-unit bar differs
   from the corrected hit-rate bar by exactly `K` (rel. 6 %) — the invariant that makes the unit
   confusion impossible to reintroduce silently.
4. New tests: `test_marginal_bar_is_a_hit_rate_not_a_credit_bar`,
   `test_every_published_field_is_inside_its_budget_optimum`,
   `test_adding_a_profitable_dot_never_lowers_the_score` (the bar is the exact sign change of the
   metric, checked numerically at `bar×1.01`, `bar×1.5`, `bar×2.0`).
5. Regenerating the release TIF reproduced SHA-256 `603be6bf…` exactly — the generator is
   deterministic and the note-text change did not touch the raster.
6. `build_hk3_pages.decision_section` referenced an undefined `RELEASED_NAME` (my first patch);
   the failure surfaced immediately because the generator is run in CI-style `--check` mode. It
   now reads the name and the scenario table from the receipt (`released_name()`,
   `released_scenarios()`), so the page cannot drift from the evidence again.
7. No file was added to `docs/downloads/`, so the auditor's `FAIL_CLOSED` path is not triggered.

---

## Pass 3 — recheck against the request

| Requirement | Status |
|---|---|
| Unique TIF, not a copy, one-click download, obviously marked OK/not-OK | **Met** — 44,090 fresh dots, 0 dots on the catalogue, 65.5 % max 3 px overlap vs 473 rasters, badge "OK TO SUBMIT: YES · 1 FILE", download button at the top of `release.html`, `download` attribute verified by the site tests |
| Unique vs all nine GEMSDOE sites | **Met** — worst overlap against the nine is far below the 70 % rule; the nine's own pairwise overlaps (97.6–100 %) are the reason none of them can be used |
| Executive summary over the nine with file, estimated score, uniqueness, and an obvious best | **Met, with one deliberate refusal** — the table gives the downloadable file, the reported score (labelled USER-REPORTED), the fault-recovery skill and the uniqueness verdict; the only claimed estimate belongs to the released file, because the nine fail uniqueness before an estimate would matter. The best submission is a single sentence at the top of both pages. |
| Why 0.2778, PhD-level, and can we beat it | **Met** — `release.html#why`: `G` pinned by the uniform-lattice probe, each file inverted for `h`, `T`, `F`, the random-control comparison (all nine are 0.85–1.22× random), the corrected budget law, `n*`, the frontier and the break-even rates |
| Submission name + ≤140-char note | **Met** — `gemsdoe-karage2-halo39-b44090-sep2-20261031`, 114-char note, printed with a character count |
| "Predicted values must be in range [0, 1]" | **Not solved — flagged.** File is float32, values exactly {0, 1}, all cells finite, no NaN, no nodata tag. The portal error is not reproducible from the bytes available here. Recorded as unresolved in `risks_section`, with the instruction to capture the exact portal text before changing the file |
| Prompt in README, re-read each session | **Met** — consolidated prompt retained; a current-decision block added above it |
| Official verified links for manual review | **Met** — rules PDF, competition page, leaderboard URL with read timestamps, USGS/GBCGE sources marked as unreachable from this sandbox |
| Autonomy, no manual input, flag irregularities | **Met** — all three irregularities above were found and fixed by the agent |
| Three passes | **Met** — this memo |
| Remaining work and limitations | **Below** |

---

## Remaining work (ranked by expected value)

1. **Submit the released file once and read the number.** One upload collapses the 0.14–0.60
   interval to a measurement and calibrates `h` for every later candidate. Nothing in the repo can
   substitute for it.
2. **Digitize an independent fault compilation** (USGS Quaternary Fault and Fold Database, Nevada
   Bureau of Mines, GBCGE INGENIOUS fault layer) and intersect it with the footprint. This is the
   only untested idea whose upside is larger than the budget effect: if the hidden set is a
   published compilation, a point-exact overlay scores far above any geometric prior. Blocked in
   this sandbox (network allowlist), so it needs a network path.
3. **E4 tip-and-step-over placement** — restrict the band to along-strike extrapolations beyond
   mapped tips and relay zones between overlapping traces. The 3-experiment budget was spent in
   prior sessions, so this needs a new lane assignment.
4. **Denser budget curve** — extend the holdout sweep past `n_max = 62,000` to find where `h`
   actually decays. Both estimators are flat between 44k and 58k, so the curve's peak is not yet
   located.
5. **Re-audit registry uniqueness** immediately before any upload
   (`scripts/audit_halo_uniqueness.py`) — one new dense public field would move the 65.5 % margin.

## Limitations

* No number on the site is ORGANIZER-CONFIRMED. Every published score is USER-REPORTED /
  UNVERIFIED; there is no file-hash-to-score receipt anywhere in the project.
* `K` and `G` are fitted to published leaderboard values; they are a coherent reparametrisation
  of those numbers, not independent measurements.
* The holdout's truth is withheld catalogue segments. It systematically penalises
  catalogue-adjacent placement (the published mask scores 0.0041 there but 0.2778 on the board),
  so it ranks strategies and does not transfer as a score.
* The 473-raster registry is not the organizer's complete submission registry. Uniqueness is
  measured against what is hash-pinned and public.
* The rules cap entries at three scored attempts per week; the account quota is not visible from
  here and no slot was consumed by this review.
* The released file is AI-assisted work and the narrative must disclose that (rules §1.1/§3.2).

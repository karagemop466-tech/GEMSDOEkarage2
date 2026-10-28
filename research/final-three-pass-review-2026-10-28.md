# Final three-pass review — 2026-10-28

## Pass 1 — implementation and evidence review

Reviewed the repository, K2 run card, saved TIFF, nine-site audit, public pages, selector schema, and test suites. The strongest local research artifact remains K2. Its measured evidence is **HOLDOUT-DTI 0.1581207190** (95% CI **0.1423739219–0.1741535541**; `gems57-pooled-hide-v2`; **58,258 withheld positives**), not an organizer score or leaderboard estimate. The candidate is byte-unique and passes the thresholds against 430 checked focus-repository submission rasters, but fails the prompt's literal any-registry-raster overlap rule against two calibration rasters.

Added a fail-closed K2 selector decision at `evidence/k2/selector_result.json` and its published copy. Verdict: **negative; no slot authorized; do not submit**. The decision does not erase the negative experiment's scientific value.

## Pass 2 — bug and contradiction review

Found that the site still described K2 as “pending selector ruling,” while the evidence supports a deterministic ruling under the prompt's literal rule. Updated the home page, executive summary, submission guide, and README to state the negative verdict and link its receipt. Preserved the research download, but labeled it **DO NOT SUBMIT**.

Checked the reported portal-range remedy: K2's saved array is finite and exactly `{0,1}`. This removes out-of-range values but does not prove portal acceptance because the organizer-authenticated template and exterior convention remain unavailable. No claim of acceptance was added.

## Pass 3 — full requirement re-check

- Three-experiment budget: respected by the K2 run (three experiments; zero submission slots).
- Leakage canaries: 26/26 pass; worst symmetric AUC 0.6211.
- Holdout improvement: positive paired confidence intervals are recorded against the frozen primitive and plain-HGB control.
- Uniqueness: passes checked submission-only registry; fails literal all-registry scope. The stricter result controls.
- TIFF validation: saved-byte format/range evidence exists; input/template authority remains unresolved.
- Leaderboard estimate: correctly shown as unavailable. No projection is called a score.
- Automated inspection: no human sign-off is used as a gate.
- Site: front page makes “OK TO SUBMIT: NO” obvious and keeps all research downloads clearly non-submittable.

## Verification

- Python: **126 passed, 7 skipped, 33 subtests passed** (`.venv/bin/pytest -q`). Skips are dependency/data-conditional tests, not failures.
- Node feed: **3 passed**.
- Site DOM: **7 passed**.
- Browser smoke: desktop and 390/320 px views passed, including release lock and freshness states.

## Blocking irregularities

1. The supplied “single method paragraph” does not actually identify a method lane; K2 self-assigned one.
2. The spacing-5 calibration raster's 3-pixel halo covers effectively the integer grid, making the literal overlap gate impossible for an in-footprint dotted candidate. The protocol nevertheless says to stop, so this review does not invent an exception.
3. Registry completeness, organizer-authenticated competition bytes, current leaderboard, weekly quota, and upload receipt are unavailable in this environment.
4. Therefore no defensible estimate above 0.3195, 0.4413, or any other private leaderboard value can be made from holdout evidence.

## Next actionable work

Obtain an explicit coordinator ruling that defines registry scope and assigns the lane; authenticate the organizer sample/data bytes; refresh the complete registry; then rerun the unchanged shared validator/audit. If the literal all-registry rule remains, K2 is final-negative and a new raster cannot overcome the spacing-5 witness without violating the requirement. If registry is formally limited to submissions, K2 may return to a separate quota-aware selector, but must not be uploaded merely because this local review passed its other gates.

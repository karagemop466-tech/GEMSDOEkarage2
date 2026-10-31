# Leaderboard recheck and three-pass repository review — 2026-10-31

**Decision: NEGATIVE. No TIFF in this repository is OK to download and submit.** This session ran no experiment, generated no new raster, used no weekly slot, and estimated no score for a new file. The reasons are the same as in the 2026-10-30 review, and the evidence checked today confirms them.

Machine-readable records: [`evidence/leaderboard-recheck-2026-10-31.json`](../evidence/leaderboard-recheck-2026-10-31.json) and [`evidence/session-2026-10-31-recheck-run-card.json`](../evidence/session-2026-10-31-recheck-run-card.json).

## 1. Answers to the brief

| Question in the brief | Answer | Source |
|---|---|---|
| Is 0.3195 the highest score right now? | **No.** The official board's rank 1 is **xiaofanhu at 0.4544**. kpomazi's 0.3195 is at rank **50** in today's read. | [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) (read in all 3 chunks, 2026-10-31 UTC) |
| Is 0.4413 the current high? | **Not on the board.** It does not appear in the 50 displayed rows. | Same page |
| Why did GEMSDOE32 score 0.2778? | **Unknown and unverified.** The owner page calls it an owner-provided submission-log claim with no submission-page receipt linking the file hash to the score, and says "already submitted – do not resubmit." No mechanism is established. The 10-30 review's pruning hypothesis (GEMSDOE32 is GEMSDOE31's mask minus 2,545 fault-adjacent pixels) is a hypothesis, not a demonstrated cause. | [GEMSDOE32 page](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html); [2026-10-30 review](2026-10-30-live-source-and-code-review.md) |
| Can we generate a unique TIF that is OK to submit? | **Not in this session.** The repo has no authenticated organizer template, no training features, and no labels. Every candidate fails or lacks the uniqueness gate. Producing one anyway would be gate-gaming. | [Release gate](../docs/evidence/public_downloads_audit.json) |
| Can we estimate a new file's leaderboard score? | **Unavailable.** Catalogue holdout cannot be calibrated to the expert-hidden set without the organizer template. | [Run card](../evidence/session-2026-10-31-recheck-run-card.json) |
| Can the data be downloaded here? | **No.** The data tab redirects to DrivenData login, and this sandbox's outbound allowlist does not include drivendata.org. | [Data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (login redirect) |
| What causes "Predicted values must be in range [0, 1]"? | **Unresolved.** The published TIFFs are finite, within [0,1], float32, one band, EPSG:32611, 3730×3292. So the cause is not an out-of-range value in the saved array. Candidate causes (exterior nodata convention, footprint/template mismatch, portal-side check) are untested without the template. | Saved-byte checks in the run card |
| Is the prompt in the README? | **Yes.** The consolidated project prompt, protocol and mandates are in [`README.md`](../README.md). | README |

## 2. Verified facts (this session)

- **Official board (read today, 2026-10-31 UTC):** rank 1 xiaofanhu 0.4544; rank 2 cfld__ 0.3925; rank 46 kinghorton42 0.3261; rank 47 danielhenshall85 0.3244; rank 48 tran.thuy.trang 0.3231; rank 49 like60986 0.3217; rank 50 kpomazi 0.3195. Display ends at 50 rows.
- **Data tab:** redirects to `accounts/login/?next=/competitions/306/competition-doe-gems/data/`. Not accessible without credentials, which were neither available nor requested.
- **Release gate:** `scripts/audit_public_downloads.py --check` → `PASS_RESEARCH_ONLY`, `downloadable_approved_submission: null`, `slot_authorized: false`, `organizer_template_authenticated: false`.
- **Published TIFFs (10 files in `docs/downloads/`):** all float32, one band, EPSG:32611, shape 3730×3292, zero NaNs, values in [0,1]. Hashes are in the run card. These are saved-byte checks. They are **not** portal acceptance.
- **Tests (this session):** `pytest` → 257 passed, 8 skipped; `npm test` → 3 pass; `npm run test:site` → 8 pass; `scripts/build_audit_site.py --check` → exit 0.

## 3. Irregularities for review

1. **Brief vs. official board.** The brief says 0.3195 is the highest score. The official board shows 0.4544 at rank 1. The brief's 0.4413 is not on the board.
2. **Rank drift in our own records.** The 2026-10-30 record placed kpomazi (0.3195) at rank 48 and like60986 (0.3217) at rank 47. Today those scores are at ranks 50 and 49. The 2026-10-30 record also listed twang at rank 50 with 0.3169, and that row is not displayed today. Ranks move as participants post, so every rank claim must carry a date. The 2026-10-30 evidence file is kept as dated history and is not edited.
3. **GEMSDOE32 0.2778 is an owner claim.** It is not on the public board and has no submission-page receipt in the repository. Its page says the file is "already submitted." Treat it as USER-REPORTED / UNVERIFIED.
4. **Portal range error is unexplained** by the saved-byte checks (see §1).
5. **Open PR collisions.** GitHub lists 16 open PRs from parallel sessions. PR #89 (`arena/d2f47b7a…`, "Document three-pass repository review (2026-10-31)") covers the same date. This session did not touch it. Reconcile before merging any competing review.
6. **Owner-mirror sample discrepancy (carried from 10-30).** The official example predicts total absence, but the owner-mirrored sample contains positive cells. Unresolved; needs authenticated organizer data.

## 4. Three passes

**Pass 1 — implement and verify.** Read `README.md`, `AGENTS.md`, `SUBMISSION_STATUS.md`, the 2026-10-30 review and the release-gate receipts. Set up a local `.venv` from the pinned `requirements.txt` (gitignored). Ran the full Python, Node, site and generator checks. Read the official leaderboard in all three chunks and the data tab. Recorded the board, the saved-byte checks and the run card.

**Pass 2 — bugs, edge cases, assumptions.** Checked whether a new `official-review-*.json` file would change the generated pages. `scripts/build_hk3_pages.py` globs `official-review-????-??-??.json` and would select it as the newest observation. So today's capture uses the name `leaderboard-recheck-2026-10-31.json` instead. Confirmed the 2026-10-30 "rank 48" wording is stale, and recorded the change in the new evidence rather than rewriting history. Confirmed that finite, [0,1] bytes do not explain the portal error, and did not claim they do.

**Pass 3 — recheck against the brief.** Every number in this document is labeled with its class: *ORGANIZER-PUBLISHED PUBLIC LEADERBOARD SNAPSHOT*, *USER-REPORTED / UNVERIFIED*, *SAVED-BYTE CHECK*, or *Unavailable*. No value is labeled HOLDOUT-DTI, since none was computed. No file is marked submit-ready. No slot was used. The brief's "OK to submit" requirement is not met, and that is stated plainly rather than papered over.

## 5. What is still needed (ranked)

1. **Authenticated organizer access** to the training features, labels, and the submission template. The DrivenData login is the single blocker for: holdout DTI, uniqueness against a full registry, and a portal-acceptance test. Without it, no file can be cleared. (Source: [data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/).)
2. **Resolve the range error empirically.** One controlled upload of a template-matched file, with the exterior convention (0 vs NaN) as the only variable, would settle it. This needs a weekly slot and an explicit selector decision.
3. **Assign a method lane.** The brief's "single method paragraph below" does not exist in the message. Without a lane assignment, the parallel-run protocol forbids a new experiment.
4. **Reconcile open PRs** (16 open) and retire superseded review branches.
5. **Freshness.** Re-read the board before any rank claim; the rank changed within one day.

## 6. Limitations

- The sandbox allowlist excludes drivendata.org data pages; the public page reader was used for the board and the login redirect.
- The public board is a time-varying snapshot, not a private-round result.
- Owner-mirror files are not authenticated organizer data.
- This review did not run a new holdout or uniqueness test, because no new candidate exists.

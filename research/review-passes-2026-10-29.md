# Three review passes — focus audit, 2026-10-29

Scope: `scripts/audit_focus_gate.py`, `scripts/build_hk3_pages.py` (new decision, nested, policy sections),
`tests/test_focus_gate.py`, the evidence under `evidence/focus-profile-2026-10-29.json` and
`evidence/lattice-gate/`, the generated pages under `docs/`, `README.md`, `SUBMISSION_STATUS.md`, and
`research/2026-10-29-focus-audit-and-next-hypotheses.md`.

## Pass 1 — Method and code

| Check | Result |
| --- | --- |
| Every input is read from a SHA-256-pinned path, and any mismatch stops the run. | Pass. The focus pins come from `registry/focus_sites.json` through the focus manifest. The lattice, template and catalogue are checked against `registry/pinned_assets.json`. |
| The gate is the shared `check_uniqueness.audit`, not a copy. | Pass. Only a one-entry manifest is added. |
| Defect found and fixed: the first run used `.cache/research/inputs/focus/*.tif`. Five of those bytes differ from the pinned reported files (GEMSDOE24, 25, 27, 28, 31). | Fixed. The script now reads the pinned paths only, and the earlier numbers were discarded. |
| Dead check removed: a dtype assertion that could never fail after the float32 cast. | Fixed. |
| Coincidence checked: the catalogue and dot-count Spearman values are identical to six decimals. | Verified by hand. The rank-difference sums are both 236, so the match is real but coincidental. The page says so. |
| Predictors correlated (catalogue vs dot count, Spearman 0.966). | Disclosed as the confound on the page. |
| Duplicate evidence: GEMSDOE25 and GEMSDOE30 share a dot set. | Disclosed. The pairs are counted but flagged as not independent. |
| Fail-closed behaviour: a missing input or a changed pin raises. Gate errors are recorded as `ERROR`, not `PASS`. | Pass. |
| Tests: 10 new tests in `tests/test_focus_gate.py` read committed JSON only. | Pass. Full suite 231 passed, 4 skipped. |

## Pass 2 — Claims against sources

| Claim on the site | Source of truth | Status |
| --- | --- | --- |
| Best reported file GEMSDOE32, 0.2778 | `registry/focus_sites.json` | Matches; labelled USER-REPORTED |
| 99.91% of GEMSDOE32 dots within 3 px of the lattice | `evidence/focus-profile-2026-10-29.json` `sites[GEMSDOE32]`; gate receipt | Matches |
| Lattice covers 99.87% of footprint; 206,895 dots | Profile `lattice_witness` | Matches |
| All nine stop at `DUPLICATE_STOP` | `gate_results`, `evidence/lattice-gate/*.json` | Matches; the shared tool was run |
| GEMSDOE32 = GEMSDOE25 minus 6,436; 2,545 vs 31; 1,200 vs 36 | `exact_subset_relations` | Matches |
| 6,436 removed dots all within 3 px of the catalogue | `removed_dot_catalogue_profile` | Matches (100%), on the mirror, not organizer labels |
| 7 of 7 non-identical nested pairs favour the smaller set | Pair list plus reported scores | Matches the list. Not an independent test. |
| Spearman −0.983 for reported score vs catalogue proximity | `correlations_nine_sites_user_reported_vs_measured` | Matches; n = 9 |
| Official: values in [0,1], float32, single layer, 100 m, NaN or null outside bounds | Problem page 967, Submission format | Verified by fetch 2026-10-29 |
| Official: three submissions per week; generative-AI narrative | NLR Official Rules §3.2 | Verified by fetch 2026-10-29 |
| Leaderboard: #1 0.4544; 0.3195 at #47 | DrivenData leaderboard, fetched 2026-10-29 | Verified; the prompt's "highest 0.3195" is wrong |
| Private test set is non-catalogue faults | Problem page 967, "Problem description" | Verified |
| Mirror sample has 60,988 positives (not all-absence) | Pinned mirror template and mirrored existing faults | Verified; flagged as an irregularity |
| Registry manifest is nine repos, 440 rasters, no completeness declared | `registry/focus_registry_manifest.json` | Verified |

Claims not made: no HOLDOUT-DTI, no organizer score, no leaderboard estimate for any file, and no
statement that catalogue avoidance causes the leader's score.

## Pass 3 — Safety and user experience

| Check | Result |
| --- | --- |
| Is any file offered as "submit"? | No. The only download is the existing HK3 research file, labelled RESEARCH ONLY. Header badge: "OK TO SUBMIT: NO". |
| Does the decision appear before the research download? | Yes. The decision block is now first on the desk and executive summary, and the research-file hero follows. Above-the-fold placement on each device was not measured. |
| Policy decision explained, with options and no agent waiver? | Pass. Three options are listed; agents will not waive or exclude the witness. |
| Browser smoke at 1440, 390 and 320 px (negative badge, research download SHA, nine rows, freshness states) | Pass (`npm run test:browser`). |
| Links from new sections resolve (`npm run test:site`) | Pass, 7/7. |
| Generated pages match the generator (`build_hk3_pages.py --check`) | Pass. |
| Remaining risk: the research file stays downloadable. | Accepted. It is labelled, hashed and not approved; removing it would be a separate owner decision. |

## Open items after review

1. Policy decision on the lattice witness and the 70% clause (owner).
2. Full-registry restore for the whole prompt list (not only nine repos) before any future candidate.
3. Portal acceptance and the cause of the range error need an organizer receipt; none is available.
4. Mirror template and labels are not organizer-authenticated.

# Three-pass review — 2026-10-31

Scope: the decision verification (`scripts/verify_decision_evidence.py`), its receipts, the page generator change, the memo and the status files. Outcome: **NO FILE OK TO DOWNLOAD OR SUBMIT**; no candidate, experiment, or slot was used.

## Pass 1 — numbers and labels

Method: a script checked every figure in the memo and README against the receipts. Each figure was either derived from a receipt or labelled as a user report. The script found 22 figures, all consistent.

Findings, all fixed:

1. **Unmeasured claim.** The memo said the D2.8 reference is "identical in GEMSDOE25, GEMSDOE30 and GEMSDOE33". The receipt did not measure this. The verification now measures it from sha-pinned bytes (`d28_family_identity`: 44,090 dots each, both identical). Test added.
2. **False source statement.** The memo said the layer names were "verified against the official page's list of provided features". No such list was read. The names are the owner-mirror manifest's band names, not organizer-authenticated. Corrected in the memo's section 6 text and table header.
3. **Wrong rule citation.** The repo cites the weekly limit (three submissions per week) as §3.4. In the official rules PDF, that sentence is in §3.2 (Process Overview), and §3.4 is "Feedback". Corrected in the memo, README (irregularity 5) and run card.
4. **Overstated novelty.** The cross-field candidate was described as "not novel". The lattice memo says it is "not certified novel" and was proposed earlier as H2. Corrected.
5. **New hypothesis overclaimed.** The catalogue-distance prior was first described as new. The repo's off-catalogue family already uses this idea. Corrected to "extends the existing off-catalogue family".

## Pass 2 — code, tests and generator

Method: reviewed the verification script (raster reading, pinned-byte fetch, Spearman on the footprint, subset logic, lemma and bound) and the generator change (`check_verification`).

Findings, all fixed:

1. **Schema mismatch caught by the fail-closed check.** The verification receipt had a `verdict` block where the generator and tests expect `decision`. The generator refused to build, and the tests failed. Renamed in the script; the block is now `decision`, with the basis stated in a comment.
2. **Brittle cross-check.** The lattice-coverage check compared a six-decimal profile value with an unrounded fraction. It now rounds to six decimals before comparing.
3. **Environment gap, not a regression.** The Node suites could not run because `node_modules` was absent. `npm ci` installed from the committed lockfile. Site tests 8/8, feed tests 3/3, and the browser smoke test passes at 1440, 390 and 320 px.
4. **Stale generated pages.** Each change to a receipt made the mirrored copies stale. The generator's `--check` caught each one. The pages were regenerated after the final receipt change.
5. **Test coverage.** 30 new tests cover the pure functions on synthetic arrays, receipt consistency, the measured D2.8 identity, and fail-closed behaviour on tampered receipts.

Software result after all fixes: Python 287 passed, 8 skipped (optional integration tests); Node feed 3/3; Node site 8/8; browser smoke passed; `build_hk3_pages.py --check` clean.

## Pass 3 — links, source authenticity and scope

Method: checked each relative link in the new and changed files, and fetched the external sources through the page reader.

Results:

- All relative links resolve.
- Verified this session: the DOE GEMS Prize Official Rules PDF (September 2026); the DrivenData leaderboard, problem page and data tab (the data tab redirects to login); the organizer reference commit `aebe92f` (GitHub API); the USGS GeoDAWN release page (DOI 10.5066/P93LGLVQ); EPSG:32611; and the Wikipedia Tversky index page (α+β=1).
- The 0.4413 and 0.2778 user figures are absent from the top 50 on the official board. That is recorded as absent, not as a score.
- Each score is labelled USER-REPORTED, OFFICIAL-PAGE-TEXT, REGISTRY-MEASUREMENT or DERIVED. No projection is written as a score.
- The 2026-10-31 official read is in its own file (`official-page-read-2026-10-31.json`). The 2026-10-30 file remains the one the monitor and generator use, so the monitor chain is unchanged.
- No TIFF was generated. No file in `docs/downloads/` was regenerated, relabelled or approved.

## Unresolved (not fixed here)

- The uniqueness rule cannot be met on this footprint without edge-hole placement. This is a policy question for the protocol owner (memo section 5, options A/B/C).
- The portal error "Predicted values must be in range [0, 1]" is not reproducible from the repo's files. The uploaded file's name and SHA-256 are unknown.
- The organizer's sample wording ("total fault absence") conflicts with the owner-mirror sample (60,988 positive cells).
- The organizer notebook writes 0.0 outside predictions; the page says null or NaN.
- `focus_sites.json` pins GEMSDOE32 at a different ref from the manifest.
- The DrivenData data tab requires login, so the official training and label files were not obtained.

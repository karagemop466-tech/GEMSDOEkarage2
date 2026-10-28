# Repository review — 2026-10-28 (Arena follow-up)

## Scope and result

Three-pass review of the current checkout and its release path, public pages,
run cards, registries, and automated tests. No new geological feature, experiment,
model fit, dot placement, competition slot, or upload was performed. This is
consistent with the run-card evidence: the HK3 three-experiment cap is used, its
recorded wall time is about 2 h 15 min, and its literal registry gate stopped.

**Release decision: NEGATIVE — DO NOT SUBMIT ANY TIFF FROM THIS REPOSITORY.**
The HK3 TIFF is retained as a research/audit download only. The pages now show
that decision before the download link. During this review the former `PROMOTE`
run-card status was superseded by a negative verdict; the prior approval rationale
is preserved separately in `evidence/hk3/approval-retracted-20261028.json`.
The selector, release-page builder, and public-download audit obey the literal
protocol rather than treating the former experiment verdict as submission
permission.

## Pass 1 — findings

### High severity: unsafe and contradictory release status

Before this review, the home page said **OK TO SUBMIT: YES** and described the
HK3 TIF as approved, while simultaneously displaying that the mandatory literal
70% registry-overlap rule failed for three records and that an exception had
been applied. The selector receipt also set `ok_to_submit: true`. This contradicted
the supplied protocol, which says any >70% overlap is a duplicate stop and forbids
picking or waiving submissions in the experiment lane. The registry audit also
reported incomplete coverage (452 of 453 expected; one missing/invalid), and the
inputs are owner mirrors, not authenticated organizer files.

The evidence distinguishes the nine focus-file comparison from the full registry:
HK3 passes the recorded comparison to the nine focus files (maximum within-3-px
overlap 48.4%), but fails the mandatory all-registry comparison at 71.0%, 73.3%,
and 74.9%. Passing the smaller comparison does not clear uniqueness. The selector
also records a self-declared lane rather than an authenticated coordinator
assignment and a wall time above the stated two-hour limit.

### High severity: a projection was presented too strongly

The former public copy presented roughly 0.263–0.286 as a “LEADERBOARD-CALIBRATED
ESTIMATE” and called HK3 the best submittable file. Its own run card says the
transfer depends on user-reported scores, calibration assumptions, and transfer
of catalogue-holdout behavior to expert-hidden labels. This is not organizer
confirmation and does not establish expected leaderboard performance. The
published copy now labels it **PROJECTION — NOT A SCORE**, states that it is
unvalidated for promotion, and makes no claim that it beats the reported 0.2778.

The 0.2778 explanation in the site was also too causal: the score and submission
history are user-reported, and the removed-dot/score arithmetic rests on
assumptions about hidden-truth credit. The executive summary now describes this
as a plausible hypothesis and conditional calculation, not a demonstrated
organizer result or confirmed cause.

### Medium severity: unsafe format-error diagnosis

The prior submission guide said the candidate “will not trigger” the portal's
range error and speculated that outside-footprint NaNs were the cause. Without
the rejected TIFF and an organizer receipt, that diagnosis is unverified. The
guide now distinguishes local finite/range checks from template provenance and
portal acceptance, and explicitly says the actual cause is unknown.

## Pass 2 — fixes made

1. Added a separate fail-closed selector decision: HK3 is `negative`,
   `ok_to_submit: false`, `slot_authorized: false`, but downloadable for research.
   It records the reasons: three literal overlap failures, an incomplete registry,
   no authenticated lane assignment, unauthenticated owner mirrors, and recorded
   runtime above budget. The TIFF bytes were not altered; the former approval rationale is preserved in the retraction receipt. A subsequent concurrent-main reconciliation also changed the current run-card verdict to negative.
2. Hardened `scripts/build_hk3_pages.py`: a `PROMOTE` run-card field alone no longer
   produces “OK TO SUBMIT: YES.” Publication requires a positive separate selector,
   unwaived literal uniqueness, complete registry, authenticated inputs, verified
   lane assignment, and compliance with the experiment/time budget. Missing or
   false attestations fail closed.
3. Changed `scripts/audit_public_downloads.py` to classify HK3 as a retained,
   selector-withheld research artifact. It cannot appear in
   `downloadable_approved_submission`; it verifies the saved bytes and records
   `PASS_RESEARCH_ONLY` instead. A future candidate must pass the literal gate,
   have an explicit positive selector, and carry the required provenance/budget
   attestations. Waiving the literal test cannot pass.
4. Regenerated the four primary pages and their evidence mirrors. The home,
   executive summary, and submission guide all visibly say **DO NOT SUBMIT**;
   the TIF/ZIP controls say research-only. The nine-site table retains reported
   results as unverified and compares uniqueness only within its stated scope.
5. Updated the README's current status and HK3/K3 comparison to withdraw the prior
   submission claim. Updated Node, Python, and browser checks to assert that the
   selector—not the experiment verdict—controls the release badge.

## Pass 3 — remaining issues and limits

- The prompt references a single assigned “method paragraph,” but no unambiguous
  assigned paragraph is present. Do not start another method until assignment and
  the exact lane scope are resolved.
- The current full registry is incomplete. Its 452/453 count is a local snapshot,
  not a complete organizer record of all submissions.
- No authenticated DrivenData sample/template, account quota, accepted upload,
  or file-bound score receipt was available in this environment. The exact reason
  for the reported portal range error remains unknown.
- Historical focus-site scores and the leaderboard figures in the prompt are
  user-reported, not organizer-confirmed in this checkout. The public research
  mirrors do not authenticate organizer provenance.
- Existing experiment results are not sufficient to claim a new submission beats
  GEMSDOE32's user-reported 0.2778 or any current leaderboard high. HOLDOUT-DTI is
  catalogue hide-and-recover performance, not a private leaderboard estimate.
- Before any next experiment: obtain the coordinator's written lane assignment
  and registry-scope ruling; authenticate competition inputs/template; restore a
  complete registry; rebuild and freeze a same-fold incumbent; verify shared
  evaluator/writer provenance; preregister one method; then spend no more than
  three experiments or two hours, whichever comes first. Stop at the first
  protocol gate failure. A separate selector—not this experiment run—must decide
  on a real weekly slot after verified evidence and quota review.

## Verification

- `.venv/bin/pytest -q` after main reconciliation: **205 passed, 7 skipped,
  98 subtests passed** (86 Rasterio deprecation warnings; skipped tests require
  optional cached inputs).
- `npm test`: **3 passed**.
- `npm run test:site`: **7 passed**.
- `npm run test:browser`: **passed** at desktop and 390/320 px widths, including
  the negative badge, research-only download, navigation, feed states, and no
  horizontal overflow.
- `scripts/assess_release.py`: **negative**, `slot_authorized: false`.
- `scripts/audit_public_downloads.py --check`: **PASS_RESEARCH_ONLY**, no
  downloadable approved submission.
- `scripts/build_hk3_pages.py --check`: pages current.
- `git diff --check`: passed.

## Source links for manual verification

- [Official GEMS competition](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Competition data tab (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN survey](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE/USGS INGENIOUS data repository record](https://gdr.openei.org/submissions/1391)
- [The nine-site user-listed history begins at GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) (owner-hosted research site; not an official organizer receipt)

## Concurrent-main reconciliation (2026-10-28)

The PR initially could not merge because `main` advanced with two independent
safety reviews. Reconciled this branch with the latest `origin/main` without
switching branches. Kept its stricter negative run-card verdict, approval
retraction record, saved-byte-only audit, policy module, source-head review and
additional status documentation. Updated `SUBMISSION_STATUS.md` because its
incoming text still contained old PROMOTE and upload instructions; it now clearly
says no file is cleared and makes no portal-range guarantee. Replaced the README's
obsolete instruction to upload HK3 with research-only next steps. Resolved all
conflicts in favor of current `main` for generated pages and overlapping policy
or test files, preserving this branch's review report and regression coverage.

The first post-merge test run exposed two stale tests importing the removed
`release_approved` helper and assuming the historical card remained PROMOTE.
Updated those tests to target `scripts.hk3_release_policy.publication_eligible`
and the current negative card. Final post-reconciliation results are recorded
below after rerunning the full verification suite.

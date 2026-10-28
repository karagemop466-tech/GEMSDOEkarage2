# Release safety review — 2026-10-28

This session did **not** run a new geological experiment, place dots, create a
submission TIFF or use a competition slot. The prompt refers to a single method
paragraph but does not identify one; the prior H1 surface already failed the
mandatory registry stop. Do not continue that lane or evade the lattice.

## Pass 1: inventory and prior work

Read the standing instructions, previous three-pass reviews, hypotheses and
cards. The prior H1 result is HOLDOUT-DTI `gems57-pooled-hide-v2`, 58,259
withheld positive pixels, 0.03367 (95% CI 0.02867–0.03929); its best primitive
control was 0.06460 (95% CI 0.05818–0.07081), on the same folds. These are
prior-session results, not independently rerun here or projections of the
hidden leaderboard. See `evidence/h1/holdout.json` and `evidence/h1/run_card.json`.
The H1 surface overlapped the lattice witness at 100% directional positive
support before placement and stopped. The complete registry and matched
incumbent remain unavailable. The historical B2 report is user-provided, not a
file-bound organizer receipt; its pruning may reduce redundant false-positive
mass but its hidden-label causal effect cannot be determined.

## Pass 2: safety defects and fixes

- The current homepage linked an older irregular-lattice artifact as a “unique
  research TIF” and suggested labels alone blocked eligibility. Replaced the
  link with the explicitly quarantined H1 research surface and surfaced the
  missing gates. The old `how-to-submit.html` instructed readers to download
  and upload that artifact despite also warning not to submit; it now redirects
  to the evidence-based guide. The older speculative hypotheses page similarly
  redirects to the documented hypotheses and caveats.
- Retired `generate_submission.py` with a nonzero, no-output fail-closed
  entrypoint. The old generator attempted to place dots to avoid a lattice,
  lacked a pre-placement full-registry stop and a valid holdout, and wrote into
  published downloads. History and artifacts remain available for research;
  no independent novelty is implied. Added a no-write regression test.
- The schema-only selector accepted holdout values without the required evidence
  class and did not require matching, unique reference IDs for surface and final
  stages. Tightened both checks. This remains a schema check: it cannot verify
  the caller's registry-completeness assertion or the truth of supplied receipts.
- Removed the invitation to rerun the stopped H1 experiment from the generated
  submission guide; corrected outdated README branch and data-placement claims.

## Pass 3: end-to-end recheck and limitations

The changed homepage retains all nine user-reported historical rows, each
labeled unverified, with unavailable transfer estimates and individual reviewed
pages. The best reported among those supplied is GEMSDOE32; no current receipt
or performance forecast was established. No local page is represented as a
change to the nine upstream sites, which are outside this repository. Pinned
community inputs authenticate bytes only; the mirrored sample has a documented
mismatch with organizer description. The network environment restricts access
to the organizer and geological hosts, Dropbox and the shared upstream's
write access; current leaderboard, competition quota, official data identity
and portal behavior were not reverified in this session. No human inspector is
used to waive checks.

Verification: Python suite, Node site/feed tests, static builds, and a real
browser smoke test at desktop and mobile widths. Details and any skipped input-
dependent tests should be reported from the actual test run, not inferred.
Before any experiment: coordinate an assigned lane and literal registry policy,
restore the shared feature stack and full cross-session registry, authenticate
template and band metadata, and reconstruct a compatible incumbent. Shared
upstream tools need the documented continuous-value handling investigated and
fixed at their source; this checkout has no push permission to that upstream.

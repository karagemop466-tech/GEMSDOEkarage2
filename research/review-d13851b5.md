# Three-pass repository review — 2026-10-28 — d13851b5

## Outcome

**NEGATIVE: no competition TIFF is approved.** No new geological experiment,
placement, training run, or weekly submission slot was performed. This review
honors the prior mandatory stop instead of promising a high private score.
The new [machine-readable review card](../evidence/review-d13851b5-run-card.json)
preserves archived K2 measurements and separates them from checks replayed here.

## Pass 1 — repository and evidence

Read the README, AGENTS instructions, prior research slates, H1/K2 cards,
independent reviews, shared-tool notes, readiness schema, site, and workflows.
The existing [five-hypothesis preregistration](hypotheses-2026-10-28-preregistration.md)
already ranks supervised multi-physics texture, tip continuation, ridge coherence,
scarp asymmetry, and seismicity alignment with layers, missing-fault rationale,
mimics, and implementation cost. It is historical, not a fresh authorization.
Its self-assigned lane and calibration exemption were superseded by the
[protocol correction](k2-protocol-review-2026-10-28.md). Do not reuse its
"portal-safe" or universal lattice-impossibility statements as verified facts.
A finite, masked lattice does not prove failure for every small candidate.

Restored pinned owner mirrors and shared tools to ignored caches. Replayed
`scripts/audit_focus.py --fetch` and the saved-byte regression tests. Hash
agreement verifies those mirror bytes, not their organizer identity or complete
registry coverage. Reopened K2 through `audit_k2_release.py` and
`review_k2_release.py`: saved SHA, one float32 band, finite [0,1] values, and
recorded mirror-grid match pass. No authentic template, exterior policy, portal
acceptance, or leaderboard estimate is established.

The historical nine-site table remains in the executive summary. GEMSDOE32's
reported result is USER-REPORTED / UNVERIFIED, not ORGANIZER-CONFIRMED. Its
measured mask is a near-catalogue pruning of the shared D2.8 family. Reduced
false-positive mass is a plausible mechanism, not a causal finding about expert
truth. Holdout results cannot be calibrated into private leaderboard estimates
from the available evidence.

## Pass 2 — defects fixed

1. `scripts/readiness.py` did not require explicit evidence that pre-placement
   clearance preceded emission, that no mandatory stop occurred earlier, or
   that organizer inputs/template were authenticated. Later passing rows could
   therefore structurally promote a stopped run. Added required assertions:
   `protocol.preplacement_passed_before_emission` must be exactly true,
   `protocol.stop_triggered` exactly false, and
   `organizer_inputs_authenticated` exactly true. Missing, null, strings and
   integer boolean lookalikes fail closed. Regression tests cover these cases.
   These are **evidence-schema assertions**, not cryptographic provenance or
   execution-order proof. The gate never authorizes a slot and cannot prevent a
   dishonest producer from supplying false assertions. Receipts and saved-byte
   audits still need verification.
2. The H1 evidence adapter now explicitly records its stop and unauthenticated
   inputs rather than relying only on other failing checks. Regenerated its
   selector receipts and published copies; verdict remains negative.
3. A pre-existing site regression failed because the executive-summary table
   said "File to download" where its research-only test required "File for
   research". Strengthened the actual heading to **File for research — DO NOT
   SUBMIT** rather than weakening the test.

No shared evaluator, writer, feature transform, or archived scientific
measurement was modified. No lane assignment or registry exemption was invented.

## Pass 3 — verification and source review

- Python, with pinned mirror inputs restored: **155 passed, zero skipped, 48
  subtests passed** (`.venv/bin/pytest -q`). Rasterio/Affine pending-deprecation
  warnings remain; these do not establish a scientific validation result.
- Node feed: **3 passed**. Site DOM: **8 passed**.
- Browser smoke passed at desktop and mobile sizes, including disabled release
  control, research-only downloads, navigation and fail-safe freshness states.
- `build_audit_site.py --check` passed. Scientific holdout was not rerun.
- Fetched the official reference README through GitHub at
  [`aebe92f7c8a990f0e3443451b7a825d9afd6336b`](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md).
  Its CPU-only instructions directly contradict the prompt's blanket claim that
  GPU hardware is necessary. GPU acceleration is useful, not mandatory.
  The exact retrieved text and hash are stored alongside the run card.

## Remaining requirements and limitations

The requested approved, unique, high-scoring new TIFF is **not delivered**.
Generating it despite a protocol stop would violate the request's stricter
parallel-run rules. Further generation requires an actual assigned lane, defined
registry scope and complete current inventory, authenticated organizer inputs,
resolved exterior convention, and a frozen comparable holdout incumbent.
Then use visible-only buffered whole-segment folds, feature canaries, surface
novelty before placement, paired holdout improvement, final-dot novelty and
saved-byte format checks. The separate selector must check the current weekly
quota before any real submission. No manual visual-inspector gate is added.

This runtime can contact GitHub and package registries, not DrivenData, USGS,
Dropbox or the other official data hosts. Those URLs remain manual-review links,
not newly verified sources. Public GitHub mirrors are obtainable but do not
resolve organizer provenance. Do not infer the current leaderboard or weekly
quota from the conflicting historical numbers in the prompt.

GitHub reports an existing Pages site at
https://karagemop466-tech.github.io/GEMSDOEkarage2/ . During this review the Pages
configuration reported legacy mode and an error while its latest legacy build
reported building and action workflows were queued/pending. This is a transient
snapshot, **not verified deployment success**. The repository also has an
Actions Pages workflow; investigate competing deployment paths if failures
persist. No concurrent workflow or other session's PR was changed here.

### Priority for next work

1. Resolve coordinator lane/registry policy without bypassing the stop.
2. Authenticate organizer bytes and exterior semantics; retain mirror mismatch
   evidence. Data placement alone is not the blocker.
3. Upstream any shared helper defects once, freeze inputs/incumbent/folds, then
   preregister a genuinely distinct operator within the assigned lane.
4. Only after every research gate passes consider quota-aware selection. Keep
   projections, HOLDOUT-DTI, and file-linked organizer receipts separate.

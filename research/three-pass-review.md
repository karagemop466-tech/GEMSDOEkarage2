# Three-pass implementation and review record

## Pass 1 — establish evidence and implement

- Recovered the nine pinned historical rasters, mirrored reference grid, fault
  labels and lattice and verified Git blob hashes plus SHA-256; independently
  reconstructed grid/mask relationships and the lattice bound.
- Restored, without modifying, the nine pinned shared protocol assets. The
  partial bundle and missing prepared features are not an executable generic
  holdout setup, and neither the template mirror nor owner-reported leaderboard
  numbers authenticate an organizer result.
- Built the read-only site, four untested research proposals, official-source
  register, fail-closed negative run card, and refresh/deploy workflows. Ran
  zero model experiments; generated and submitted no candidate TIFF.

## Pass 2 — review and repair

- Tightened the historical-dot audit to reject nonbinary interior values; added
  integer/boundary guards for the lattice lower bound.
- Prevented authenticated GitHub requests from following cross-origin redirects
  before any credential-bearing follow-up request.
- Added client-side validation of all nine audit records, safe text rendering,
  deep-link restoration, and explicit stale/unavailable source-monitor status.
- Made the shared format-check wrapper fail its exit status when the conservative
  whole-array range diagnostic fails. Its zero exit remains a local diagnostic,
  not organizer acceptance or permission to submit. Verified the historical
  all-finite B2 and NaN-outside R1 variants exhibit the expected contrasting
  local strict-range flags; neither is a new candidate.
- Exercised served page endpoints and DOM rendering, including malformed data,
  failed leaderboard refresh, disabled submit control, and dynamic site anchors.
  No real browser screenshot or responsive-viewport visual inspection was
  available in this environment.

## Pass 3 — requirement and reproducibility recheck

- Re-fetched all 12 pinned assets into a fresh cache and reproduced the complete
  nine-site JSON audit identically apart from the observation timestamp.
  Re-fetched and hash-verified the shared protocol bundle into a separate cache.
- A live source-head check found that GEMSDOE25 changed after the audit pin;
  its new H79 uses overlapping ingredient families and reports a negative
  verdict. Added an explicit novelty caveat; did not silently alter pinned results
  or represent the upstream holdout as independently reproduced.
- Rechecked the organizer's public leaderboard via the web reader: 0.4544 was
  the rank-one public snapshot on 2026-10-27, not a file-bound receipt or a
  projection. Direct runtime leaderboard access failed closed and preserved
  the last successful snapshot.
- Local regression results: 21 Python tests and five DOM tests passed. GitHub
  Actions and Pages deployment require separate remote verification.
- Every historical row is research-only; the negative card does not pretend to
  contain a holdout score, feature canaries, registry-wide pass, candidate hash
  or format approval. Smaller budgets remain possible in principle, and the
  lattice bound is not an excuse to seek artificial lattice holes.

## Concurrent main-branch integration

While the PR was open, `main` gained an independently authored dashboard,
nine site pages, evidence snapshots and a fail-closed readiness-schema gate.
These were merged on this session branch: earlier pages and their run card are
preserved as clearly dated snapshots, while the current dashboard links the
nine earlier site pages. The merged Pages workflow retains a test gate and adds
the scheduled refresh. The readiness gate still rejects this negative run card.
Post-integration local tests: 32 Python tests plus 33 unittest subtests, and
five DOM tests passed. Deployment remains subject to GitHub Pages settings.

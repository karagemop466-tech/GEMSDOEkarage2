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

## Second concurrent integration: stopped H1 experiment

A later `main` merge introduced a separate H1 geological experiment, its shared
unchanged tools, evidence, local website and a quarantined research surface.
Those assets are preserved; this review did not rerun the experiment. An
independent saved-byte check (`scripts/audit_parallel_surface.py`) confirmed the
surface SHA-256, one float32 band, mirrored grid, finite range, zero catalogue
and exterior positives, and the single-witness collision: all 1,893,817 positive
surface cells lie within 3 px of the r13 lattice, with full-footprint Spearman
-0.000057. This uses the inherited positive-support interpretation for a
continuous surface, not a final-dot comparison. The previous session's
HOLDOUT-DTI and confidence interval remain attributed to its own evidence.

The experiment report's generator now writes to separate `experiment-*` pages
instead of overwriting the current dashboard; both reports and the nine
per-site pages remain linked. Corrected the selector adapter so a local
zero-padded owner-mirror format pass does not claim that the organizer's
outside-nodata policy was verified. The combined local suite passed 70 Python
tests (33 unittest subtests) and five DOM tests, with one third-party rasterio
pending-deprecation warning. Real-browser evidence from the H1 session covers
its generated pages; the newer dashboard was exercised in DOM/HTTP tests but
not independently screenshot-tested at responsive viewport sizes here.

## Deployment review

Both legacy main-root Pages publishing and the Actions artifact deployment
succeeded, but they raced with different URL layouts (`/docs/` vs `/`). The
Pages settings API and manual workflow-dispatch API returned HTTP 403 for the
integration. The Actions artifact now stages the same root redirect plus
`docs/` layout as the legacy build, so both mechanisms publish the same paths;
no Git internals or caches are staged. A legacy build may briefly restore the
older committed monitor until the scheduled refresh runs, and the dashboard
must continue to label old or failed refreshes rather than assert live data.

## Exact-file correction and refresh diagnosis

A further publication review found that the original scorecard displayed the
NaN-padded siblings of five files next to claims for differently named
all-finite/zero files. We fetched those five exact claim-named files at the pinned
site revisions, verified Git blob hashes, sizes and SHA-256, and reran the
nine-site geometry audit. Their positive masks matched the previously inspected
siblings pixel-for-pixel; the outside encodings and bytes differ. The 72
pairwise outcomes and the site 31 → 32 reconstruction did not change. The
current JSON, dashboard, experiment overview and per-site pages now use the
claim-named files. The earlier JSON remains available with a correction
annotation; none of these score claims has a file-bound organizer receipt.

After the stable-layout deployment, an earlier refresh diagnostic reported zero
parsed rows and no recognized leaderboard headers. The underlying response was
not inspected, and no parser workaround or access bypass was attempted. A
concurrent follow-on review subsequently disabled automated DrivenData access:
the scheduled feed refreshes GitHub metadata only. The dated public 0.4544
snapshot is never relabeled as a fresh leaderboard check; consult the official
board directly for its current value.

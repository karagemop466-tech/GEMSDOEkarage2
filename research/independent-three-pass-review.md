# Three-pass independent review — 2026-10-27 UTC

This is the follow-up geometry / integration session. It did not fit a new
geological model, place dots or use a competition slot. A different session's
H1 experiment, research surface, holdout and run card were merged while this
review was in progress; those results are preserved and attributed, not
independently replayed or presented as an approved entry.

## Pass 1 — provenance, metric and geometry

- Retrieved and hash-pinned nine historical TIFFs, the lattice, mirrored labels
  and sample, and the unmodified GEMSDOE24 shared novelty/format modules.
  Re-read the organizer's problem, metric, formatting and staff clarifications
  with a page-reading tool; data files and receipts remained unauthenticated.
- Measured all 72 directional historical-pair overlaps: every one exceeds 70%.
  Verified the D2.8 equality and the exact B2 distance-filter relationship.
  Neither fact proves the reported H33 result or hidden-fault causality.
- Reproduced the literal 3-pixel lattice coverage and the 37,654-dot lower
  bound. It forces a stop for that budget but not for every smaller raster.
- Found that the sample mirror contains known-fault positives although the
  organizer describes its sample as predicting no faults, and that band 15's
  owner-mirror description should not be assumed equivalent to the official
  conductive-base description. Both are explicitly flagged, not guessed away.
- Compared the original Tversky equations: truth-side and prediction-side
  distance sums differ, so a simplified dot-count denominator is not generally
  valid. H33's 0.2778 remains an owner claim without a file-linked receipt.

## Pass 2 — implementation and failure-mode checks

- Reproduced the complete audit in a fresh cache from immutable GitHub paths,
  checking sizes, Git blobs and SHA-256. Reproduced the published JSON exactly
  except its generation timestamp. Also exercised the optional ~400 MB feature
  mirror restore and checksum; no raw inputs are committed by this follow-up.
- Exercised the actual pinned shared writer/validator with **temporary synthetic
  test files**, including negative and above-one values, interior NaN, wrong
  CRS, transform, shape, dtype and band count. Tested both incompatible exterior
  diagnostics separately and kept official portal compliance unknown.
- Re-opened the concurrently merged research TIFF: its hash, interior/grid and
  whole-array range diagnostics matched, but its exterior is zero rather than
  NaN in the mirror's outside footprint. It is not an approved submission.
- Corrected the local readiness adapter: a general mirror-based format pass can
  no longer set `outside_nodata` to true. The selector remains negative. Shared
  evaluator/writer copies were not altered; unsupported claims in their writer
  documentation are recorded for an upstream fix.
- After integrating the second independent dashboard, the combined Python run
  passed 93 tests plus 33 unittest subtests, including both real pinned-raster
  audits and the independent H1 surface recheck. One third-party
  Rasterio/Affine deprecation warning remains; it is not a raster validity or
  model score. All eight Node tests and the browser smoke checks also passed.

## Pass 3 — presentation, integration and end-to-end recheck

- GitHub Actions exposed a newer `gh` binary-response text transformation error.
  The other audit's fetcher now uses the same base64 Git blob path with verified
  size, SHA-256 and Git SHA, and a binary-byte regression test covers it.
- Reproduced the other session's nine-raster audit and its H1 saved-byte report
  exactly except creation timestamps; that session selected different NaN-outside
  variants for several historical files, so byte hashes are not interchangeable.
- Preserved concurrent-main dashboards, the research-only TIFF/ZIP, source
  snapshots, pinned tools, run cards, per-site pages and readiness tests. The
  independent audit is a separate linked page. Earlier pages are archived and
  identified as snapshots rather than silently removed.
- Tested both sites in a real headless Chromium at desktop and mobile widths
  (including 320 px for the primary site): no viewport overflow or page errors;
  navigation, no-approval controls, research-only download and downloaded
  SHA-256 passed. Mocked current, changed and unavailable freshness responses
  remain clearly scoped to public GitHub commits, not a leaderboard.
- Checked internal links and deterministic site builds. The local preview
  serves only public docs/research files, not `.git` or `.cache`; the Pages
  workflow stages the same root/docs/research layout for either legacy or
  Actions-based publishing. CI bootstraps pinned small inputs and reruns the
  format, scientific-audit and browser tests.
- No authenticated DrivenData receipt, complete fleet registry, assigned lane,
  reconstructed current matched best, or evidence for a slot is available.
  The research-only download stays **DO NOT SUBMIT**, and a prospective
  organizer score remains unavailable.

# Independent three-pass review — 2026-10-28

Scope: this repository and the nine named public sibling sites, read-only. No geological
experiment, prediction TIFF, competition submission or weekly slot was created. This
is an audit and safety correction, not a new method lane.

## Pass 1 — implementation and independent evidence

1. Restored the nine *original* pinned historical GeoTIFFs, the spacing-5 lattice,
   sample and catalogue from immutable GitHub refs into the ignored cache; each file
   matched the SHA-256 in `registry/focus_sites.json`. The smaller independent shared
   template and analysis inputs were also restored and verified with
   `scripts/bootstrap_research.py`. These are owner mirrors, not authenticated
   DrivenData files. All nine pinned direct-download routes returned GitHub 302 raw
   redirects; actual bytes were separately fetched and hashed via the GitHub API.
2. Re-ran `scripts/geometry_audit.py` on the nine original references and compared
   every field except the timestamp with `evidence/geometry-audit.json`: exact match.
   Independently repeated `scripts/audit_references.py` against its pinned converted
   research references and `scripts/compare_audit.py`: exact match except creation time.
   The directional overlap of each historical file with at least one other pinned
   focus file exceeds 70%. These are earlier submitted-variant files, useful to read
   or download for research but **not** safe to submit as new. Their reported values
   are not linked to authenticated organizer receipts.
3. The strongest reported focus value is GEMSDOE32's 0.2778, **USER-REPORTED /
   UNVERIFIED**. Its 37,654-dot B2 mask is a strict subset of D2.8's 44,090 dots,
   removing 6,436 pixels at most two pixels from mirrored catalogue traces; 25 and 30
   have identical in-footprint dot sets. Pruning low-credit positives could improve
   the distance-weighted Tversky balance. The actual hidden labels and file-linked
   receipt are unavailable, so causation and comparative scores are not established.
4. Re-read the saved HK3 bytes using the unchanged pinned template's `gems.novelty`
   and `gems.submission` functions. On the owner-mirrored footprint, **45,046 of
   45,108 dots = 0.9986255209718897** lie within the inclusive 3-pixel radius of the
   registered lattice; full-footprint Spearman is **0.000317637408** after stable
   rounding. A low rho cannot rescue a >70% overlap. Repeating with one and two
   OpenBLAS threads produced the same committed receipt. Two archived registry rows
   with the same lattice hash independently match the result.
5. HK3 is one float32 band, EPSG:32611, 3730×3292, matching the owner-mirror transform,
   with finite whole-array [0,1] values, 45,108 positives and SHA-256
   `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9`. Its exterior
   is zero rather than NaN relative to the mirror. This is **local format only**:
   the official sample and portal acceptance are unverified. The recorded previous
   range error has no authenticated file or proven cause.

## Pass 2 — bugs, edge cases and release safety

* The prior HK3 promoter excluded the lattice and waived three other literal registry
  failures. That was an unauthorized exception to the user protocol. Only eight new
  HK3 features had standalone canaries, not the full 34-feature inventory; the full
  leakage gate is unverified. Corrected the authoritative card and selector to **negative**, preserved the previous decision in
  `evidence/hk3/decision_correction.json` and Git history, and retired all CLI/direct
  entry points in `scripts/hk3.py`. Prior HK3 consumed three experiments and its
  recorded ~2h15 exceeded the two-hour cap; it was not rerun.
* A single lattice witness is sufficient to stop; the saved wider scan also reports
  one invalid-grid reference and is not a complete registry. A dense witness flags
  proximity even for unrelated maps, so this is a **literal protocol stop**, not a
  conclusion that the research raster was copied. Its pre-placement surface clearance
  was not independently rechecked. No approved candidate is advertised.
* The public download inventory now reports seven research-only artifacts and cannot
  authorize a candidate merely because an edited card/selector says `PROMOTE`. It
  verifies saved bytes, single-file GeoTIFF interpretation, ZIP identity, negative
  selectors and published metadata; unhashed GDAL sidecars, malformed inputs,
  mismatched hashes, unknown downloads, forged approvals and out-of-range pixels
  fail closed. Provenance and actual slot authorization are not inferred from these
  local integrity checks.
* Rebuilt the four main desk pages from `scripts/build_hk3_pages.py`, replaced the
  unsafe estimate and upload wording, published the negative evidence and a clearly
  labeled **research-only** download, and corrected the alternate audit template,
  `README.md`, `AGENTS.md` and the historical HK3 research-note warning. The former
  speculative leaderboard projection remains only as withdrawn historical context.
  All current HTML routes were reviewed for misleading approval language.
* Main advanced concurrently with independent negative-decision corrections. These
  were reconciled on the assigned branch: the upstream original-card/selector history,
  protocol-review receipt and policy checks, status notice and nine `docs/focus/`
  summaries were preserved. Their protocol-review receipt was regenerated against
  the reconciled card; the new literal recheck remains independent of that historical
  summary. The full leakage flag was tightened to reflect only eight recorded canaries.
* Regression tests exercise forged card/selector/receipt values, hash binding, GDAL
  external-mask sidecars, retirement entry points, portal-acceptance language and
  negative legacy decisions. Browser tests actually download and hash the research
  file at desktop and 320/390px widths, check nine rows, navigation, no horizontal
  overflow and failed/changed GitHub freshness responses.

## Pass 3 — mandate, source and limitation reconciliation

* The desk links each of the nine precise filenames and individual site summaries;
  estimates for new leaderboard scores remain unavailable, with all old values
  explicitly marked unverified. The current public leaderboard observation on
  2026-10-28 was 0.4544 for xiaofanhu, not a receipt for any local TIFF. See
  [`evidence/official-review-2026-10-28.json`](../evidence/official-review-2026-10-28.json).
* Four ranked, falsifiable geological proposals with physical transforms, named
  non-fault controls, costs, limitations, prior-art overlaps and official sources are
  in [`2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md). The first
  shares an ingredient family with B4; no fleet-wide novelty or holdout is claimed.
  The requested single method paragraph is absent; none was self-assigned here.
* Organizer problem and rules were read through the public page reader. They specify a
  single 32-bit float band, [0,1], matching CRS/resolution/bounds, null/NaN outside
  bounds, and up to three scored attempts per week with one final selection. Data and
  submissions pages require login; the account's actual remaining quota, file-linked
  score receipts and official template bytes were not available. The shell has a
  stricter outbound allowlist than the public page reader.
* Local HOLDOUT-DTI, when quoted, carries evaluator, withheld positives and 95% CI;
  it is not a leaderboard score. Previously recorded HK3 HOLDOUT-DTI is 0.1845
  [0.1677, 0.2015], evaluator `gems57-pooled-hide-v2`, 58,258 withheld positives at
  1.10%. K3's prior 0.1916 [0.1747, 0.2088] uses the same named evaluator/count but
  is also negative and has no established paired comparison against HK3.
* Future work requires an explicitly assigned lane; authenticated organizer inputs,
  metadata and exterior/portal behavior; a complete literal registry; per-feature
  leakage canaries; buffered whole-segment, visible-only, pixel-masked pooled DTI;
  a matched incumbent and CI; then a separate quota-aware selector. Do not evade the
  lattice by placing dots in its rare uncovered pixels.
* The current session card uses nulls for the unrun top hypothesis and nonexistent
  candidate/score/name/note and separately identifies the historical HK3 witness:
  [`evidence/2026-10-28-independent-audit-run-card.json`](../evidence/2026-10-28-independent-audit-run-card.json).

## Automated verification

Local post-integration run: **228 Python tests plus 98 subtests passed** (89 Rasterio/Affine
pending-deprecation warnings); **3 Node feed and 7 site tests passed**; browser
smoke tests passed at 1440, 390 and 320 px, including actual byte-hashed downloads.
Both independent geometry replays, the HK3 literal recheck (including 1/2-thread
reproducibility), download inventory, generated-page consistency, compile and shell
syntax checks passed. Optional pinned reference inputs were restored for this run.
Remote CI results and merge status are reported separately in the PR; local tests do
not prove organizer acceptance. No portal upload, user-account access or claim to
change the other repositories was made.

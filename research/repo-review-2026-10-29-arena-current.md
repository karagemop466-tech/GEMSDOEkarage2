# Repository review — Arena session on `arena/02fe9ab0-gemsdoekarage2` (2026-10-29)

## Decision

**NEGATIVE: no new submission TIFF was generated or approved; do not submit any repository raster.** No competition slot was used. This review is a repository/site safety repair, not a geology experiment. The consolidated prompt and prior evidence remain in `README.md`, `AGENTS.md`, `research/2026-10-29-verification-and-blocker-review.md`, and the linked run cards.

The highest value in the user's nine-site list remains the **GEMSDOE32 0.2778 USER-REPORTED / UNVERIFIED** claim. It is not a file-linked organizer receipt, and it cannot support a calibrated prediction for another file. The merged main branch contains a dated **ORGANIZER-PUBLISHED PUBLIC LEADERBOARD SNAPSHOT** at 2026-10-29T18:26:44Z reporting 0.4544 for xiaofanhu at rank 1 and the user's cited 0.3195 for kpomazi at rank 47; these are not receipts or local-raster scores and may now be stale. This Arena turn did not retrieve external pages; see `research/2026-10-29-scorecard-and-monitor-review.md` and `evidence/official-review-2026-10-29.json` for the prior timestamped observation. The competition, USGS, GDR, and NLR pages were not fetched in this turn; their links are provided for manual review, not represented as freshly verified.

## Pass 1 — inspect implementation and fix an unsafe release inconsistency

Read `README.md` first, then `AGENTS.md`, `SUBMISSION_STATUS.md`, previous blocker/review records, selector and release evidence, the shared writer, the public-download audit, the Pages workflow, the four-hypothesis slate, and the current generated site.

Found three related artifact/release inconsistencies while integrating current main: (1) `docs/executive-summary.html` advertised a "File ready for download" and a "PROMOTE" GW-NFS TIFF, while controlling evidence said **no file is approved**; (2) an H-A intersection-propensity TIFF had no HOLDOUT-DTI or registry measurements; and (3) an H-R4 TIFF's run card said `promote` despite null HOLDOUT-DTI, no canaries, and uniqueness checks against only two references. Direct saved-byte inspection of H-R4 found zero NaN pixels across the raster and 5,761 positive cells, contradicting its audit's outside-NaN PASS and the method narrative's 30,000-dot count. None of these files passed the full protocol. The old public-download audit failed closed on the orphaned outputs; all three rasters and their available metadata are now preserved outside `docs/downloads/`.

Repairs:

1. Quarantined the existing 762,402-byte GW-NFS TIFF outside `docs/`, without modifying its bytes. Its exact SHA-256 is `294ad3693c3f2f6bd84e71e2f6bf412c8b4fa7b291662bd33befba1734628e85`. The quarantine receipt states that no score or validation provenance is available.
2. Quarantined the 762,056-byte H-A TIFF and its existing run card/audit outside `docs/`, preserving their bytes and recording individual hashes. The run card explicitly has no HOLDOUT-DTI or registry measurements; the audit explicitly says uniqueness is unverified. This is a research hypothesis artifact, not a validated submission.
3. Quarantined the 723,767-byte H-R4 TIFF and all three metadata/audit files, retaining their hashes. Direct Rasterio read of every pixel found zero NaNs and 5,761 positive cells; the inherited audit says outside-footprint NaN passed and the method prose says 30,000 dots. Its `promote` verdict is unsupported because HOLDOUT-DTI and feature canaries are null, the two-reference registry comparison is incomplete, and no pre-placement clearance is documented. See `evidence/quarantine/hr4-intersection-20261029-nan.quarantine.json`.
4. Disabled direct execution of `scripts/generate_unique_submission_v2.py`, whose former implementation generated synthetic-data H-R4 and wrote it into public downloads, then labeled it `promote` from format/partial-registry checks despite a null holdout. A regression test confirms the generator fails closed without writing or changing downloads.
5. Regenerated the public desk from `scripts/build_hk3_pages.py`, retaining the latest main-branch timestamped leaderboard snapshot and GitHub metadata-only freshness statement. The executive summary now agrees with the saved-byte negative decision: no submission-ready TIF, the only displayed raster is marked research-only, no new submission name/note, no leaderboard estimate, and no slot authorization. It links this session's run card and report.
6. Repaired root `index.html` to route to the current desk at `docs/index.html`, rather than the stale executive-summary route.
7. Rebuilt the published-download inventory. It reports `PASS_RESEARCH_ONLY` for the seven registered research artifacts and `downloadable_approved_submission: null`. This is an inventory-integrity pass, **not** an approval to submit.
8. Added `evidence/session-02fe9ab0-review-run-card-2026-10-29.json` for this review. It uses nulls where no current candidate measurement exists and records zero experiments/slots.

The repository's earlier evidence identifies the current strict-stop example: the prior HK3 final raster had 45,046 of 45,108 dots within 3 px of a registered lattice (99.8626%, a **REGISTRY-OVERLAP AUDIT**, not a score), over the literal >70% stop; the registry scan had one missing/invalid entry. Do not generalize the lattice lower bound beyond its measured footprint and budget. These are inherited historical measurements, not freshly rerun this session.

## Candidate hypotheses and experiment authorization

Three qualitative hypothesis slates are present after integrating latest main. The current Arena review's ranked five-candidate shortlist and full layer-by-layer signatures, missing-fault rationale, novelty scope, confounders, controls, costs, and source links are in [`research/hypotheses-2026-10-29-untried.md`](hypotheses-2026-10-29-untried.md); that ranking is qualitative, not a score projection. A separate five-proposal slate was added in [`research/new_hypotheses_20261029.md`](new_hypotheses_20261029.md); it is also unvalidated and not ranked by this review. The older four-candidate slate at [`research/2026-10-28-next-lane-slate.md`](2026-10-28-next-lane-slate.md) is historical planning context; its top gravity/topography idea overlaps the broad ingredient family of prior negative B4 work.

The current five, ranked by *hypothesized* utility/cost, are:

1. **H-A — multi-scale fault-intersection propensity:** DEM curvature at three scales, K/Th radiometric ratio, and distance to mapped Quaternary faults; targets intersections/relay ramps potentially missed by surface-trace inventories. Lithologic contacts and terrace risers are named mimics. The distance-to-fault layer must be computed from visible faults per fold; otherwise it leaks withheld labels. **Cost medium; expected gain qualitative medium–high.** Its required DEM is in the participant-login data tab per the repository record; GeoDAWN radiometric availability/coverage was not checked.
2. **H-B — off-catalogue SGMC distance with basement-depth constraint:** independent SGMC fault lines, gravity-derived basement depth and magnetic analytic signal; a blind-strand hypothesis. Lithologic edges can mimic the signature, and proximity to a second fault map could leak label information. **Cost high; potential gain qualitative high only if independent source validity holds.** INGENIOUS/GDR links are listed, but no map file/extent/license was retrieved.
3. **H-C — seismicity-aligned strain-rate corridor:** earthquake density, geodetic strain and young-volcanic-center context; mining/induced events and interpolation artifacts can mimic it. **Cost low–medium; gain qualitative medium.** USGS/ANSS URLs are listed, but event access, completeness and spatial coverage were not verified.
4. **H-D — radiometric K/eU/eTh alteration index:** ternary/ratio transforms intended to flag possible hydrothermal alteration halos beyond mapped traces; lithology and weathering are plausible confounders. **Cost low; gain qualitative medium.** GeoDAWN band availability, units and extent were not checked.
5. **H-E — multiresolution, directional DEM lineaments:** four scales and eight azimuths; diffuse structural expression is the proposed signal, while drainage, bedding and anthropogenic linear features are mimics. **Cost low; gain qualitative lower–medium.** 3DEP is linked, but no intersecting tile, footprint, resolution or license was verified.

H-A and H-R4 TIFFs were present in the updated main branch. Neither is evidence of a validated hypothesis: H-A had null holdout/registry measurements and unauthenticated grid provenance; H-R4 had null HOLDOUT-DTI, no feature canaries, incomplete uniqueness checks, and direct saved-byte conflicts with its audit/prose. All TIFFs and their available sidecars are preserved under `evidence/quarantine/`, not published as submission downloads; H-R4's synthetic generator is blocked. None of the external source links in either proposed slate was fetched in this Arena turn; sources without confirmed data files, coverage, and licenses are not viable experiments.

No candidate can be run now: the request does not uniquely identify a coordinator-assigned paragraph; the prior HK3 lane is retired; the full registry and pre-placement gate are unresolved; the authenticated organizer inputs and cached shared feature stack are absent. Therefore it would violate the binding protocol to select a slate, emit a surface, run holdout/leakage tests in a self-assigned lane, or spend a slot. **No new HOLDOUT-DTI, 95% CI, withheld-positive count, feature AUC, candidate registry statistic, candidate score estimate, or submission TIFF is claimed.**

## Pass 2 — tests and edge cases

Initial verification exposed the stale executive summary, failed generated-page consistency check, failed public-download inventory, and **14 Python failures** plus **5 Node site-test failures**. After main advanced during review, the merged suite also exposed one stale assertion expecting the former root redirect; it was updated to verify the new `/docs/index.html` route. The root cause was unsafe, untracked-by-evidence TIFF content and stale generated output—not a need to loosen gates. After all three quarantines, regeneration and test correction:

- Python: **234 passed, 8 skipped, 98 subtests passed**. The skips require optional pinned owner-mirror/shared artifacts that are absent from this lightweight checkout; the warnings are Rasterio pending deprecations.
- Node feed tests: **3 passed**.
- Node site tests: **9 passed**.
- Browser smoke tests passed at 1440 px, 390 px and 320 px, including the root-to-current-desk redirect and research-only download hash.
- `scripts/build_hk3_pages.py --check`: passed.
- `scripts/audit_public_downloads.py --check`: passed; inventory remains research-only, with no approved TIFF.
- `scripts/recheck_hk3.py --check`: attempted but **not completed** because the pinned `shared-template/src/gems/__init__.py` input is absent; this is consistent with the optional mirror-backed test skips.
- `scripts/assess_release.py`: negative, slot unauthorized.
- `scripts/audit_k2_release.py`: negative, slot unauthorized.

A test pass establishes local deterministic code/content checks only. It does not authenticate mirrored data, prove the scientific hypothesis, predict hidden expert-label DTI, ensure current global registry coverage, or establish DrivenData portal acceptance.

## Pass 3 — original request checklist

| Requirement | Result |
|---|---|
| Read and preserve the user's project prompt in README | Present; README says to reread it each session. |
| Review the nine named sites and explain the leading GEMSDOE32 claim | Existing executive scorecard and pinned per-site pages; 0.2778 remains USER-REPORTED / UNVERIFIED. Mechanism is a conditional pruning/false-positive hypothesis, not proven causation. |
| 3–5 hypotheses before implementation | Five ranked research proposals are documented; a separate five-proposal slate is also preserved. No implementation is authorized. |
| Validate top hypothesis on blocked holdout before any slot | Not run because there is no assigned lane, cached stack/authenticated inputs, and unresolved literal all-registry stop. No slot was spent. |
| Produce a unique, submission-safe TIF | **Not achieved and not claimed.** Three unvalidated TIFFs were removed from public downloads and quarantined. |
| Estimate leaderboard score | Unavailable; no trustworthy calibration from catalogue holdout to hidden expert labels. |
| Make submission eligibility obvious | Current generated desk says **OK TO SUBMIT: NO**, with research-only link and no approved download. Root route now leads to this desk. |
| Automatically validate without human inspection | Local fail-closed tests and release checks run; actual organizer format/template/portal acceptance remains unauthenticated. |
| Open and merge a PR | This review is prepared on the assigned Arena branch; PR/merge must be attempted after local commit/push, without changing branches. |

## Official sources for manual review

The previous source-verification receipt and its exact claim scope are in [`evidence/official-verification-2026-10-29.json`](../evidence/official-verification-2026-10-29.json). The current sandbox did not refresh external non-GitHub sites. Review:

- [DrivenData competition problem and format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData data tab (login required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN data](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [GEMSDOE32 pinned mirror/site](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)

## Next-session blockers (ordered)

1. Obtain an explicit, immutable lane assignment and confirm it is distinct from prior B4/K2/HK3 work.
2. Restore/authenticate organizer template and competition inputs; reconcile footprint, NaN-outside policy, and the prior `[0,1]` portal error from an actual organizer artifact/receipt.
3. Restore the shared cached feature stack and shared evaluator/writer at pinned revisions; do not rebuild them privately.
4. Resolve the pre-placement literal duplicate witness using a complete immutable registry scan. Do not relax 0.90 / 70% thresholds, waive lattice references, or place predictions to target uncovered cells.
5. Freeze a same-fold, visible-only incumbent; then test the assigned proposal's feature-alone AUC canaries, buffered whole-segment holdout, pooled DTI and paired spatial 95% CI, within the three-experiment/two-hour limit.
6. Only a candidate passing all gates may enter a separate quota-aware selector. A real submission still needs account quota, an actual submission-page receipt, and required generative-AI disclosure/code assets for finalist rules.
7. Refresh the public leaderboard only from an accessible official page. The repository's GitHub revision feed is not a live DrivenData leaderboard feed.

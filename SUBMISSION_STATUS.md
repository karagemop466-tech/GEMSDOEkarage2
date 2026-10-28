# Submission status — GEMS Prize Challenge

## Current decision: NO APPROVED SUBMISSION — DO NOT UPLOAD

The repository contains a historical HK3 GeoTIFF for research and reproducibility, but **it is not approved for the DrivenData competition**. The old `PROMOTE` decision was retracted; see the [current hash-bound negative assessment](evidence/hk3/current_release_assessment.json), [`evidence/hk3/approval-retracted-20261028.json`](evidence/hk3/approval-retracted-20261028.json), the archived [`pre-correction run card`](evidence/hk3/history/run_card-before-protocol-correction.json), the [protocol correction review](research/hk3-protocol-correction-2026-10-28.md), and the [repository review/verification record](research/repo-review-2026-10-28-final.md).

| Item | Current status |
|---|---|
| Research artifact | [`docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif`](docs/downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif) |
| Download status | Research-only; do not submit |
| File SHA-256 | `064d70e8c949cbc1f5de99f26210540419eb43efd17ef9fcda9e59cbe95f74d9` |
| Historical HOLDOUT-DTI | 0.1845 [0.1677, 0.2015], evaluator `gems57-pooled-hide-v2`, 58,258 withheld positives; historical evidence only. The repository's recorded K3 value is 0.19157 [0.1747, 0.2088]; no paired cross-session test establishes an HK3 win over K3. |
| Historical leaderboard projection | 0.263–0.286 in the archived pre-correction card; LEADERBOARD-CALIBRATED ESTIMATE, not an observed score; no private-label validation |
| Literal registry uniqueness | FAIL: 45,046/45,108 dots (99.8626%) within 3 px of the r13 lattice; the archived non-degenerate scan also records 71.0%, 73.3%, and 74.9% against three other rasters. No density/lattice exception is authorized. |
| Method lane | Self-declared; no coordinator assignment receipt |
| Registry coverage | Incomplete: 452/453 expected entries in the full scan; no current complete accessible-scan certificate |
| Pre-placement surface gate | No verifiable surface-gate receipt bound to a surface hash in the release record |
| Input/template provenance | Owner mirrors only; organizer authentication absent |
| Budget/runtime | Historical run used 3 experiments and reports ~2 h 15 min; no machine-readable runtime receipt |
| Organizer receipt / slot | None; no slot used; no score is ORGANIZER-CONFIRMED |

**Why blocked:** the protocol states that a rank correlation above 0.90 or more than 70% of dots within 3 px of any one registry raster is a duplicate stop. The candidate's literal registry gate fails. Its prior exception is not authorized. A byte-valid GeoTIFF or a passing holdout does not waive the uniqueness, lane, provenance, or budget requirements.

The website keeps the file available for audit and labels it **RESEARCH ONLY — DO NOT SUBMIT**. The submission guide blocks upload steps. Do not use a competition slot for this artifact.

## Focus-site comparison

The nine site results listed on the site are historical USER-REPORTED / UNVERIFIED values, not organizer receipts or predictions. Among those reported values, GEMSDOE32's B2 submission is listed at 0.2778. A plausible explanation is that pruning dots close to already mapped faults reduces false-positive mass where mapped faults are excluded from scoring; the available evidence does not establish that as the cause of the reported score. The historical calibrated estimate above does not prove that HK3 beats 0.2778.

See the [executive summary](docs/executive-summary.html), [site-by-site table](docs/index.html#nine-sites), and [official competition leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) for review. Current leaderboard access and the submission portal require organizer access; no current score or quota is asserted here.

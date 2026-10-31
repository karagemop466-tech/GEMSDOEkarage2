# Official-source verification and review — Arena branch arena/48564c81 (2026-10-31)

**Verdict in one line:** the recommended file is safe to *download* and is format-checked, but nothing in this
repository measures that it scores higher than 0.2778. Whether to spend a weekly slot is an owner decision.
No new TIFF was generated this session, because no available instrument can rank candidates (see §4).

## 1. Official sources read this session (line-level, with links)

| # | Claim | Source (fetched 2026-10-31) | What the source says |
|---|---|---|---|
| S1 | Submission must be one single-band GeoTIFF at 100 m covering the whole GeoDAWN area | [NLR official rules PDF §3.2](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | "a single GeoTIFF with a single raster layer at 100-meter resolution containing your model's predictions of fault locations for the entirety of the GeoDAWN study area" |
| S2 | EPSG:32611, 100 m, same bounds as training data, data outside bounds null or NaN, float32, values 0–1 | [DrivenData problem page 967, "Submission format"](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | "data outside the bounds is null or nan" and "values between 0 and 1" |
| S3 | Metric: distance-weighted Tversky, α=0.2, β=0.8, 300 m triangular kernel | same page, "Mathematical representation" | DTI = TPw / (TPw + α·FPw + β·FNw + ε) |
| S4 | Public top score | [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) (ranks 1–23 read) | #1 xiaofanhu **0.4544**; #2 cfld__ 0.3934; #3 Batik Shirt Brothers 0.3917. The brief's 0.4413 and 0.3195 "highest" do not match rank 1. |
| S5 | Organizer sample is "total fault absence" | same problem page | "A sample submission that predicts total fault absence is provided for your reference on the data download page." |
| S6 | Competitors may use external data only if licensed | same page, "External datasets" | Licensing and sharing permission required. |
| S7 | Reference solution | [drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution) | Requires data "from the GEMS Prize Challenge website"; the repo ships no data. |
| S8 | Owner-reported 0.2778 for GEMSDOE32 | [GEMSDOE32 site](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) | "0.2778 OWNER-REPORT (owner-provided submission-log claim; no submission-page receipt linking this raster hash to the score is present in this repository)". |
| S9 | Data tab is login-walled | [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) | Login required; not reachable from this sandbox. Training labels, features and the official sample could not be downloaded. |

## 2. Repository file checks run this session (not inherited from prose)

Recommended file `docs/downloads/gemsdoe-karage2-halo39-b44090-sep2-20261031.tif`:

* SHA-256 `603be6bfb38eddf6be024103a75958027846a93476ecb7529ec958d4a32e5c38` (matches the release page).
* GTiff, 1 band, float32, EPSG:32611, 3730 × 3292, transform (100, 0, 243350, 0, −100, 4508550), nodata None.
* All 12,279,160 cells (3730 × 3292) finite; min 0.0, max 1.0, 0 values outside [0, 1]; **44,090 cells equal 1.0, the rest 0.0.**
* Format checks agree with `docs/downloads/gemsdoe-karage2-halo39-b44090-sep2-20261031.audit.json`.

Local test suite (`pytest`, pinned `requirements.lock.txt`, Python 3.11): **302 passed, 10 skipped.**

## 3. Irregularities flagged for review

1. **Exterior convention conflicts with the official text.** S2 says data outside the bounds is null or NaN. The
   recommended file writes finite zeros over the whole rectangle. The repo's own page builder
   (`scripts/build_hk3_pages.py`, lines 438–440) notes that the 0.2778 champion also uses zeros, with an
   owner-reported score, while GEMSDOE24/27/28/31-style files use NaN. The official text, the owner reports and the
   portal error therefore cannot be reconciled from here. The release page now says so.
2. **The portal error "Predicted values must be in range [0, 1]" is still unexplained.** The recommended file
   satisfies the range literally. The repo's test comment (`tests/test_release_page.py` line ~107) calls NaN "the
   likeliest cause"; that is a hypothesis, not a finding, and NaN is explicitly allowed by S2.
3. **The grid and footprint are unauthenticated.** `registry/core_data_manifest.json` says "owner-supplied mirror …
   NOT organizer-authenticated". The hashes match the mirror, not the organizer.
4. **The mirror's sample contradicts S5.** `evidence/owner_mirror_preflight_2026-10-28.json` records 60,988 positive
   pixels in `sample_submission.tif`, equal to the labels inside the footprint, while the organizer calls its sample
   total absence. The repo already flagged this as "confirm the exact organizer file before submission".
5. **The 0.478 central estimate is a projection, not a measurement.** It assumes a per-dot hit rate of 4.5%. The repo's
   own holdout gives the 0.2778 champion 0.0041 and a blind field 0.0427, so the instrument cannot rank
   leaderboard-class files. The 0.222 low end matches a random field (0.227 in the same table).
6. **Uniqueness measurements are from the repo's own pinned inventory,** not the organizer's registry. The literal
   lattice probe (r13, 99.8% coverage) fires for every dense file and is disclosed as a geometry property.
7. **The brief's numbers conflict with the official board.** 0.4413 is not on the board; 0.3195 is not the high
   (rank 1 = 0.4544). Ranks below 23 were not re-read this session.

## 4. Why no new candidate TIFF was generated

* The only score-like signal available is the repo's holdout, which the repo itself says cannot rank this target.
* No organizer labels, sample file or portal receipt are reachable from this sandbox (S9).
* Generating another file would add an unmeasured candidate to the pile, not a measured improvement.
* What would unlock real progress: (a) a DrivenData account login to download the official files and sample (the
  owner can do this; no credentials were requested or stored); (b) one portal submission receipt for the
  recommended file, recording the exact accept or reject message; (c) a free official fault compilation to build an
  independent holdout that is not the mirror. The official rules (§2, NLR PDF) name the USGS Quaternary Fault and
  Fold Database as a label source; its licence and download path were not checked in this session.

## 5. Answer to "why did 0.2778 score highest, and can we beat it?" (qualified)

From the repo's own analysis (not verified against the organizer): the champion is a dense 37,654-dot emission in a
300–900 m halo around mapped traces, with a 2.76% implied hit rate. Under the metric, false positives are charged
at α = 0.2 while misses cost β = 0.8, so a dense field pays when its hit rate is above about 1.1%. Whether a
candidate beats 0.2778 depends on a hit rate that no available instrument measures. The break-even for the
recommended file is 2.52%, and the file's own holdout cannot show it clears that bar.

## 6. Recommendation

* **Download:** yes, the recommended file is format-checked, all values in [0, 1], unique by the repo's measurements.
* **Submit to the leaderboard:** owner decision only. Do not treat it as a likely winner. Use one slot as a
  deliberate experiment, record the portal's exact response, and only then decide on the exterior convention.
* **Do not** spend slots on the nine focus files: their reported scores are owner-reported and they overlap each
  other (100% within 3 px in several cases).

## 7. Limitations

* This sandbox cannot reach DrivenData's data pages, the portal or the organizer; no score was measured on any
  organizer label set.
* Public-site statements (GitHub Pages sites of other teams) were read as published text, not as receipts.
* The uniqueness check is against the repo's pinned set of 473 rasters, not the full competitor registry.

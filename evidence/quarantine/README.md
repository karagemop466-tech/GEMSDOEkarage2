# Quarantined raster artifacts

These files are retained for repository provenance but are deliberately outside
`docs/downloads/`, so the GitHub Pages site does not expose them as submission
files. They have no verified run card, holdout-DTI receipt, complete registry
comparison, or organizer-template provenance in this checkout. Do not submit or
promote them. A file hash and local raster metadata are not evidence of scientific
validity or uniqueness.

## `gemsdoe-karage2-gw-nfs-h1-20261029-zeros.tif`

- SHA-256: `294ad3693c3f2f6bd84e71e2f6bf412c8b4fa7b291662bd33befba1734628e85`
- Locally read as single-band float32, 3,730 × 3,292, EPSG:32611, 100 m transform
  `(100, 0, 243350, 0, -100, 4508550)`, finite range `[0, 1]`, 30,000 positive cells.
- These facts are a local byte inspection only. No holdout score, registry uniqueness,
  template authenticity, portal acceptance, or score is established.

## `gemsdoe-karage2-near-trace-20261031.tif` (moved from `docs/downloads/` on 2026-10-31)

- SHA-256: `cc158d4248ed4b5fb64bbec7dc990a08e01993a6a91fd597d6d4578038a95811`
- Run card (unchanged): [`gemsdoe-karage2-near-trace-20261031-run-card.json`](gemsdoe-karage2-near-trace-20261031-run-card.json) with `verdict: "promote"` and `ok_to_submit: false`. The card's blocker is the lattice-overlap gate.
- Why it is quarantined: the file has 122,597 dots, and **every dot lies within 2 px of the full labels catalogue** (`labels.tif == 1`, which includes the withheld positives). The card's holdout DTI 0.624191 (fold range 0.6227–0.6273) therefore comes from a field built on unmasked positives. It is not a valid held-out result, and it sits close to the pre-fix evaluator defect value (0.625).
- The public-download audit correctly fails closed on the non-negative verdict. The card was not relabelled and the audit was not weakened.
- Do not submit or promote this file. Do not cite its 0.624 value as a holdout score.


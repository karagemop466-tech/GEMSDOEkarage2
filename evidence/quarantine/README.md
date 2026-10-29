# Quarantined raster artifacts

These files are retained for repository provenance but are deliberately outside
`docs/downloads/`, so the GitHub Pages site does not expose them as submission
files. Any original run card is historical provenance, not authorization; missing
holdout-DTI, complete-registry comparison, or organizer-template provenance remains
a failed release gate. Do not submit or promote them. A file hash and local raster
metadata are not evidence of scientific validity or uniqueness.

## `gemsdoe-karage2-gw-nfs-h1-20261029-zeros.tif`

- SHA-256: `294ad3693c3f2f6bd84e71e2f6bf412c8b4fa7b291662bd33befba1734628e85`
- Locally read as single-band float32, 3,730 × 3,292, EPSG:32611, 100 m transform
  `(100, 0, 243350, 0, -100, 4508550)`, finite range `[0, 1]`, 30,000 positive cells.
- These facts are a local byte inspection only. No holdout score, registry uniqueness,
  template authenticity, portal acceptance, or score is established.

## `gemsdoe-karage2-hr4-intersection-20261029-nan.tif`

- SHA-256: `bdb8dd78ad7f1a0b349f8e8eaf20a918a40a1ff4486e9a1fcc204ce3608f6932`
- The original sidecar run card said `promote`; that decision is **RETRACTED** by
  [`gemsdoe-karage2-hr4-intersection-20261029-nan-countermand.json`](gemsdoe-karage2-hr4-intersection-20261029-nan-countermand.json).
- The source generator documents a synthetic fault mask and all-true placeholder
  footprint when organizer data are absent. Its run card has null HOLDOUT-DTI, CI,
  and withheld-positive count; it says feature-alone leakage tests cannot run; its
  uniqueness comparison names only two local rasters; and it checks the final dots
  after placement. These fail the required evidence and pre-placement gates.
- A later pinned-byte surface audit records `DUPLICATE_STOP`: 4,684 of 4,685
  support dots (99.9787%) lie within 3 px of one 13GEMSDOE lattice witness. Its
  manifest explicitly declares itself incomplete, so this is a strong single-witness
  duplicate stop—not a claim of full-registry clearance.
- The local float32/range/CRS/grid report is not proof of scientific validity,
  uniqueness against a complete registry, organizer-template match, or portal
  acceptance. The bytes and sidecars are retained unchanged, but the TIFF is outside
  the public download directory. **Do not submit or promote it.**

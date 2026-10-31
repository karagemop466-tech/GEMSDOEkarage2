#!/usr/bin/env python3
"""SGMC-cal: an independent, reproducible fault-truth instrument for this study area.

Truth set
---------
USGS State Geologic Map Compilation fault structures (NV + CA ``structure``
layers, public domain, https://mrdata.usgs.gov/geology/state/), rasterised to the
100 m competition grid by the competition participant repositories
(GEMSDOE24 ``data/external/derived_sgmc_faults_100m_u8.tif``, sha256 pinned in
that repository's receipt) and reduced to the pixels **more than 3 px (300 m)
from the mapped catalogue**, i.e. the faults that the INGENIOUS/USGS catalogue
does *not* contain.  The organiser masks mapped catalogue faults out of scoring
(competition forum thread 11516), so this is the closest public analogue of the
hidden expert truth that is available without an organiser account.

Metric
------
The shared template's own metric (``gems57.metric``): distance-weighted Tversky
index, alpha = 0.2, beta = 0.8, triangular kernel of radius 300 m (3 px).
The published SGMC-cal value of the GEMSDOE32 champion (0.09538611460482535) is
reproduced by this implementation to 13 significant figures, so the numbers are
comparable with the published leaderboard-side instrument.

Evidence class
--------------
Every value printed by this script is a **HOLDOUT-DTI**-class measurement on a
fixed, public, independent truth set.  It is **not** an organiser score and it
is **not** the hidden private-set score.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems57 import metric as gmetric  # noqa: E402

EVALUATOR = "gems57-pooled-hide-v2"
DATA_DIR = ROOT / "data" / "bridge"
EXT_DIR = ROOT / ".cache" / "external"


class SgmcInstrument:
    """Pre-computed instrument; ``score`` is O(prediction) per raster."""

    def __init__(self, truth_source: str = "24", off_catalogue_px: int = 3):
        with rasterio.open(DATA_DIR / "existing_faults.tif") as ds:
            cat = ds.read(1)
        with rasterio.open(DATA_DIR / "sample_submission.tif") as ds:
            foot = np.isfinite(ds.read(1))
        with rasterio.open(EXT_DIR / f"{truth_source}_derived_sgmc_faults_100m_u8.tif") as ds:
            sgmc = ds.read(1) > 0
        self.footprint = foot
        self.catalogue = (cat > 0) & foot
        far = ndi.distance_transform_edt(~self.catalogue) > off_catalogue_px
        self.truth = sgmc & foot & far
        self.active = foot & ~self.catalogue
        self.q = gmetric.kernel(ndi.distance_transform_edt(~self.truth))
        self.n_truth = int(self.truth.sum())

    def score(self, pred_bool: np.ndarray) -> dict:
        p = np.asarray(pred_bool, bool) & self.active
        if not self.truth.any():
            raise ValueError("empty truth")
        covers, _, _ = gmetric.max_cover(p.astype(np.float64), self.truth)
        tpw = float(covers.sum())
        fpw = float((p.astype(np.float64) * (1.0 - self.q)).sum())
        fnw = float(self.n_truth) - tpw
        dti = tpw / (tpw + gmetric.ALPHA * fpw + gmetric.BETA * fnw + gmetric.EPS)
        return dict(
            evidence_class="HOLDOUT-DTI",
            evaluator_version=EVALUATOR,
            instrument="SGMC off-catalogue (>3 px) / gems57 pooled evaluator",
            dti=float(dti),
            tpw=tpw, fpw=fpw, fnw=fnw,
            withheld_positive_pixels=self.n_truth,
            n_emitted=int(p.sum()),
        )


def score_raster(path: Path, inst: SgmcInstrument) -> dict:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    out = inst.score(a > 0)
    out["file"] = str(path)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rasters", nargs="+", help="GeoTIFF files to score")
    ap.add_argument("--truth-source", default="24", choices=["24", "30"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    inst = SgmcInstrument(truth_source=args.truth_source)
    rows = [score_raster(Path(p), inst) for p in args.rasters]
    rows.sort(key=lambda r: -r["dti"])
    print(json.dumps(rows, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(rows, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

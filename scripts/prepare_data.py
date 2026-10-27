"""
prepare_data.py
---------------

Validate that competition data is correctly placed in data/ and summarize it.
Expected files (from the DrivenData GEMS Prize Challenge data tab, login
required - see scripts/download_competition_data.sh):

  data/training_features.tif   multi-band feature stack (EPSG:32611, 100 m)
  data/labels.tif              ground-truth fault raster (binary)
  data/sample_submission.tif   official submission format template
  data/existing_faults.tif     catalogue faults (USGS + INGENIOUS)
  data/1m_DEM_links.csv        URLs for 1 m DEM tiles

This script does NOT download anything (DrivenData authentication is required
and is not available in this sandbox).  It only checks placement and prints a
machine-readable summary used by evaluate_holdout.py and generate_submission.py.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"

EXPECTED = [
    "training_features.tif",
    "labels.tif",
    "sample_submission.tif",
    "existing_faults.tif",
    "1m_DEM_links.csv",
]


def summarize(path):
    with rasterio.open(path) as ds:
        return {
            "file": path.name,
            "bytes": path.stat().st_size,
            "shape": [ds.height, ds.width, ds.count],
            "dtype": str(ds.dtypes[0]),
            "crs": ds.crs.to_string() if ds.crs else None,
            "transform": [ds.transform.a, ds.transform.b, ds.transform.c,
                          ds.transform.d, ds.transform.e, ds.transform.f],
            "bounds": [ds.bounds.left, ds.bounds.bottom, ds.bounds.right, ds.bounds.top],
            "nodata": ds.nodata,
        }


def main():
    missing = [f for f in EXPECTED if not (DATA_DIR / f).exists()]
    if missing:
        print(f"[prepare_data] data/ not complete. Missing: {missing}", flush=True)
        print("[prepare_data] See scripts/download_competition_data.sh for how to obtain data.",
              flush=True)
        return 1

    summary = {"data_dir": str(DATA_DIR), "files": []}
    template = None
    for f in EXPECTED:
        p = DATA_DIR / f
        if f.endswith(".csv"):
            summary["files"].append({"file": f, "bytes": p.stat().st_size,
                                     "note": "DEM link list"})
            continue
        info = summarize(p)
        summary["files"].append(info)
        if f == "sample_submission.tif":
            template = info

    # Cross-check grid consistency
    grids_ok = True
    for info in summary["files"]:
        if "shape" not in info:
            continue
        same_shape = (info["shape"][0], info["shape"][1]) == (
            template["shape"][0], template["shape"][1])
        same_crs = info["crs"] == template["crs"]
        same_t = all(abs(a - b) < 1e-9 for a, b in zip(info["transform"],
                                                       template["transform"]))
        grids_ok = grids_ok and same_shape and same_crs and same_t
        info["matches_template"] = bool(same_shape and same_crs and same_t)
    summary["grids_consistent"] = bool(grids_ok)

    out = DATA_DIR / "prepared.json"
    with open(out, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[prepare_data] {len(EXPECTED) - len(missing)}/{len(EXPECTED)} files present; "
          f"grids consistent: {grids_ok}", flush=True)
    print(f"[prepare_data] summary written to {out}", flush=True)
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())

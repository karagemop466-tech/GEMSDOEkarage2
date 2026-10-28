#!/usr/bin/env python3
"""Fail-closed local raster preflight; it does not authenticate organizer data.

The full mode checks the five files named by the competition data workflow.
``--core-only`` checks the four pinned owner-mirrored rasters when the DEM link
list is unavailable. This is research-byte/schema validation, never upload
approval. No model, holdout or candidate TIFF is produced here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.errors import RasterioError

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
CORE_FILES = ("training_features.tif", "labels.tif", "existing_faults.tif", "sample_submission.tif")
DEM_LINKS = "1m_DEM_links.csv"
# Provisional grid from pinned community mirrors, not an organizer identity pin.
EXPECTED_SHAPE = (3730, 3292)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def summarize(path: Path) -> tuple[dict, tuple]:
    with rasterio.open(path) as ds:
        meta = {
            "file": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "driver": ds.driver,
            "shape": [ds.height, ds.width, ds.count],
            "dtypes": list(ds.dtypes),
            "crs": ds.crs.to_string() if ds.crs else None,
            "transform": list(ds.transform)[:6],
            "bounds": [ds.bounds.left, ds.bounds.bottom, ds.bounds.right, ds.bounds.top],
            # The mirrored sample has NaN nodata. JSON's NaN token is *invalid*;
            # represent the metadata as text without changing the raster values.
            "nodata_repr": repr(ds.nodata),
        }
        return meta, (ds.shape, ds.crs, ds.transform)


def inspect(data_dir: Path = DATA_DIR, *, core_only: bool = False,
            mirror_manifest: Path | None = None) -> dict:
    data_dir = Path(data_dir)
    files = list(CORE_FILES) + ([] if core_only else [DEM_LINKS])
    missing = [name for name in files if not (data_dir / name).is_file()]
    report = {
        "schema": "gems.input_preflight.v2",
        "evidence_class": "LOCAL-DATA-SCHEMA, NOT ORGANIZER AUTHENTICATION",
        "mode": "core-only research" if core_only else "full named-file inventory",
        "data_dir": str(data_dir),
        "missing": missing,
        "files": [],
        "checks": {},
        "irregularities": [],
        "schema_pass": False,
        "upload_authorized": False,
        "submission_generated": False,
    }
    if missing:
        report["irregularities"].append("Missing required input(s); no prepared-data success is recorded.")
        return report

    manifest_files: dict[str, dict] = {}
    if mirror_manifest is not None:
        manifest = json.loads(Path(mirror_manifest).read_text())
        manifest_files = {row["dest"]: row for row in manifest["files"]}
        if set(manifest_files) != set(CORE_FILES):
            raise ValueError("Mirror manifest must pin exactly the four core inputs")
        report["mirror_manifest"] = str(mirror_manifest)
        report["irregularities"].append("SHA-256 agrees with the selected owner mirror; official provenance is not established.")
    else:
        report["irregularities"].append("No organizer-bound source hash/receipt was provided; origin is not authenticated.")

    grids = {}
    for name in CORE_FILES:
        path = data_dir / name
        meta, grids[name] = summarize(path)
        if manifest_files:
            expected = manifest_files[name]
            meta["mirror_hash_match"] = (meta["sha256"] == expected["sha256"] and
                                         meta["bytes"] == expected["bytes"])
        report["files"].append(meta)
    by_name = {item["file"]: item for item in report["files"]}
    template_grid = grids["sample_submission.tif"]
    template_shape, template_crs, template_transform = template_grid
    report["checks"] = {
        "matching_shape_crs_transform": all(grid == template_grid for grid in grids.values()),
        "expected_mirror_shape": template_shape == EXPECTED_SHAPE,
        "expected_epsg_32611": template_crs == CRS.from_epsg(32611),
        "north_up_100m": (template_transform.a == 100 and template_transform.e == -100 and
                         template_transform.b == 0 and template_transform.d == 0),
        "all_geotiff": all(item["driver"] == "GTiff" for item in report["files"]),
        "features_19_float32_bands": (by_name["training_features.tif"]["shape"][2] == 19 and
                                      by_name["training_features.tif"]["dtypes"] == ["float32"] * 19),
        "sample_one_float32_band": (by_name["sample_submission.tif"]["shape"][2] == 1 and
                                    by_name["sample_submission.tif"]["dtypes"] == ["float32"]),
        "labels_one_band_each": all(by_name[name]["shape"][2] == 1
                                    for name in ("labels.tif", "existing_faults.tif")),
    }
    if manifest_files:
        report["checks"]["owner_mirror_hashes"] = all(
            item["mirror_hash_match"] for item in report["files"])
    if not core_only:
        size = (data_dir / DEM_LINKS).stat().st_size
        report["checks"]["dem_links_nonempty"] = size > 0
        report["files"].append({"file": DEM_LINKS, "bytes": size, "sha256": sha256(data_dir / DEM_LINKS)})

    if report["checks"]["matching_shape_crs_transform"] and report["checks"]["sample_one_float32_band"]:
        with rasterio.open(data_dir / "sample_submission.tif") as ds:
            sample = ds.read(1)
            foot = np.isfinite(sample) & (ds.read_masks(1) > 0)
        report["checks"]["nonempty_sample_footprint"] = bool(foot.any())
        report["diagnostics"] = {"footprint_pixels": int(foot.sum()),
                                 "sample_positive_pixels": int(((sample > 0) & foot).sum()),
                                 "sample_ones_outside_footprint": int(((sample == 1) & ~foot).sum())}
        if foot.any() and grids["labels.tif"][0] == template_shape:
            with rasterio.open(data_dir / "labels.tif") as ds:
                label = ds.read(1)
            report["diagnostics"]["sample_positive_equals_labels_inside"] = bool(
                np.array_equal((sample[foot] > 0), (label[foot] > 0)))
        if report["diagnostics"]["sample_positive_pixels"]:
            report["irregularities"].append(
                "The sample contains positive predictions. The organizer's published example was described as total fault absence; confirm the exact organizer file before submission.")
    else:
        report["checks"]["nonempty_sample_footprint"] = False
    report["schema_pass"] = all(report["checks"].values())
    if not report["schema_pass"]:
        report["irregularities"].append("A data-schema check failed; no model or submission is cleared.")
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", type=Path, default=DATA_DIR)
    p.add_argument("--core-only", action="store_true", help="Research mirror check without a DEM link file")
    p.add_argument("--mirror-manifest", type=Path, help="Verify SHA-256 against pinned core owner mirrors, not organizer provenance")
    args = p.parse_args(argv)
    try:
        report = inspect(args.data_dir, core_only=args.core_only, mirror_manifest=args.mirror_manifest)
    except (OSError, ValueError, KeyError, TypeError, RasterioError, json.JSONDecodeError) as exc:
        report = {"schema": "gems.input_preflight.v2", "schema_pass": False,
                  "upload_authorized": False, "submission_generated": False,
                  "irregularities": [f"Input preflight failed: {type(exc).__name__}: {exc}"]}
    if args.data_dir.is_dir():
        output = args.data_dir / "prepared.json"
        temp = output.with_suffix(".json.partial")
        temp.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        os.replace(temp, output)
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["schema_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

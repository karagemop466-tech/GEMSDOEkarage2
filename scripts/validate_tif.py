#!/usr/bin/env python3
"""Independent, read-back-only GeoTIFF format audit; not submission authorization.

No clipping or repair is performed. The strict local check requires NaN outside
the template footprint, following the published null/NaN wording. A separate
whole-array finite/range diagnostic is recorded for investigating portal errors.
An owner-mirrored template is not organizer authentication or a portal receipt.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import rasterio
from rasterio.errors import RasterioError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from restore_references import digest  # noqa: E402


def validate(candidate: Path, template: Path) -> dict:
    candidate_sha_before = digest(candidate)
    template_sha_before = digest(template)
    with rasterio.open(template) as ds:
        if ds.count != 1 or ds.crs is None:
            raise ValueError("Reference template must have one band and a CRS")
        template_grid = (ds.shape, ds.crs, ds.transform)
        ref = ds.read(1)
        foot = np.isfinite(ref) & (ds.read_masks(1) > 0)
        template_sha = digest(template)
    if not foot.any():
        raise ValueError("Reference footprint is empty")
    with rasterio.open(candidate) as ds:
        data = ds.read(1)
        mask = ds.read_masks(1)
        same_shape = ds.shape == template_grid[0]
        checks = {
            "geotiff_driver": ds.driver == "GTiff",
            "single_band": ds.count == 1,
            "float32": ds.dtypes[0] == "float32",
            "crs_matches_template": ds.crs == template_grid[1],
            "crs_epsg_32611": ds.crs == rasterio.crs.CRS.from_epsg(32611),
            "shape_matches_template": same_shape,
            "transform_matches_template": ds.transform == template_grid[2],
            "north_up_100m_resolution": (ds.transform.a == 100 and ds.transform.e == -100 and
                                         ds.transform.b == 0 and ds.transform.d == 0),
        }
        if same_shape:
            inside = data[foot]
            outside = data[~foot]
            checks.update({
                "inside_no_masked_cells": bool(np.all(mask[foot] != 0)),
                "inside_all_finite": bool(np.isfinite(inside).all()),
                "inside_in_range_0_1": bool(np.isfinite(inside).all() and np.all((inside >= 0) & (inside <= 1))),
                "outside_is_nan": bool(np.isnan(outside).all()),
            })
            finite_inside = inside[np.isfinite(inside)]
            diagnostics = {
                "footprint_pixels": int(foot.sum()),
                "inside_nan": int(np.isnan(inside).sum()),
                "inside_inf": int(np.isinf(inside).sum()),
                "inside_masked": int((mask[foot] == 0).sum()),
                "inside_below_zero": int((inside < 0).sum()),
                "inside_above_one": int((inside > 1).sum()),
                "inside_min": float(finite_inside.min()) if finite_inside.size else None,
                "inside_max": float(finite_inside.max()) if finite_inside.size else None,
                "outside_nan": int(np.isnan(outside).sum()),
                "outside_finite": int(np.isfinite(outside).sum()),
            }
        else:
            checks.update({"inside_no_masked_cells": False, "inside_all_finite": False,
                           "inside_in_range_0_1": False, "outside_is_nan": False})
            diagnostics = {"reason": "shape mismatch; footprint-level checks not possible"}
        diagnostics["whole_array_finite_in_range"] = bool(np.isfinite(data).all() and
                                                          np.all((data >= 0) & (data <= 1)))
    candidate_sha_after = digest(candidate)
    if candidate_sha_before != candidate_sha_after or template_sha_before != digest(template):
        raise ValueError("Candidate or template changed while it was being audited")
    return {"kind": "LOCAL-FORMAT-AUDIT (not a portal receipt or scientific approval)",
            "candidate": str(candidate), "candidate_sha256": candidate_sha_after,
            "reference_template": str(template), "template_sha256": template_sha,
            "template_authenticity": "not established by this check",
            "checks": checks, "diagnostics": diagnostics,
            "strict_format_pass": bool(all(checks.values())),
            "upload_authorized": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.candidate, args.template)
    except (OSError, ValueError, RasterioError) as exc:
        print(f"Validation failed closed: {exc}", file=sys.stderr)
        return 1
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0 if result["strict_format_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

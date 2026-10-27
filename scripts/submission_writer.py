"""submission_writer.py
--------------------

Writes and validates a single-band float32 GeoTIFF submission for the DOE GEMS
Prize Challenge.

Submission format (official, page 967 / Submission format):
  * single band, 32-bit float, values in [0, 1]
  * CRS: EPSG:32611 (UTM zone 11N), resolution 100 m
  * same bounds / shape / geotransform as the training template
  * data outside the footprint is null / nan

Validation gates (run before any file is labelled OK to download):
  1. CRS / shape / transform match the official template exactly
  2. dtype float32, single band
  3. every cell finite and in [0, 1]   (fixes the portal error
     "Predicted values must be in range [0, 1]")
  4. no NaN inside the footprint
  5. sha256 of saved bytes recorded
  6. uniqueness vs reference registry rasters: |Spearman| <= 0.90 and
     <= 70% of dots within 3 px of any one registry raster's dots

Outputs:
  * the GeoTIFF
  * an audit JSON receipt (format + range checks)
  * a run card JSON (hypothesis, mechanism, holdout numbers, uniqueness,
    raster sha256, validator output, submission name + note <= 140 chars,
    verdict promote / negative)
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import rasterio
from rasterio.transform import Affine
from scipy import ndimage

# Official competition grid (observed from the hash-pinned reference template
# used by the scored reference submissions: EPSG:32611, 3730 x 3292, 100 m,
# upper-left corner (243350.0, 4508550.0)).
OFFICIAL_CRS = "EPSG:32611"
OFFICIAL_PIXEL_M = 100.0
OFFICIAL_WIDTH = 3292
OFFICIAL_HEIGHT = 3730
OFFICIAL_TRANSFORM = Affine(OFFICIAL_PIXEL_M, 0.0, 243350.0,
                            0.0, -OFFICIAL_PIXEL_M, 4508550.0)
OFFICIAL_BOUNDS = (243350.0, 4135550.0, 572550.0, 4508550.0)


@dataclass
class ValidationResult:
    passed: bool
    checks: list
    message: str


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_template(path):
    """Read the official submission template raster metadata (no data required)."""
    with rasterio.open(path) as ds:
        return {
            "driver": ds.driver,
            "width": ds.width,
            "height": ds.height,
            "count": ds.count,
            "dtype": str(ds.dtypes[0]),
            "crs": ds.crs.to_string() if ds.crs else None,
            "transform": [ds.transform.a, ds.transform.b, ds.transform.c,
                          ds.transform.d, ds.transform.e, ds.transform.f],
            "bounds": [ds.bounds.left, ds.bounds.bottom, ds.bounds.right, ds.bounds.top],
            "nodata": ds.nodata,
        }


def _checks_equal(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol


def validate_geotiff(path, template_meta=None, reference_rasters=None,
                     footprint_mask=None):
    """Run all format/range/uniqueness gates on a candidate submission GeoTIFF."""
    checks = []
    ok = True

    def add(name, passed, detail=""):
        nonlocal ok
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            ok = False

    with rasterio.open(path) as ds:
        crs = ds.crs.to_string() if ds.crs else None
        transform = ds.transform
        data = ds.read(1)

    add("single_band", ds.count == 1, f"count={ds.count}")
    add("dtype_float32", str(ds.dtypes[0]) == "float32", f"dtype={ds.dtypes[0]}")
    add("shape_3730x3292", (ds.height, ds.width) == (OFFICIAL_HEIGHT, OFFICIAL_WIDTH),
        f"{ds.height}x{ds.width}")
    add("crs_EPSG_32611", crs == OFFICIAL_CRS, f"crs={crs}")
    t_ok = all(_checks_equal(getattr(transform, n), getattr(OFFICIAL_TRANSFORM, n))
               for n in ("a", "b", "c", "d", "e", "f"))
    add("geotransform_match", t_ok, str(OFFICIAL_TRANSFORM))
    b_ok = all(_checks_equal(x, y) for x, y in zip(ds.bounds, OFFICIAL_BOUNDS))
    add("bounds_match", b_ok, str(OFFICIAL_BOUNDS))

    finite_mask = np.isfinite(data)
    n_nan = int((~finite_mask).sum())
    add("all_cells_finite", n_nan == 0, f"nan_cells={n_nan}")
    if finite_mask.any():
        vmin = float(np.nanmin(data)); vmax = float(np.nanmax(data))
    else:
        vmin = vmax = float("nan")
    add("in_range_0_1",
        bool(np.all((data[finite_mask] >= 0.0) & (data[finite_mask] <= 1.0))),
        f"min={vmin} max={vmax}")

    if footprint_mask is not None:
        nan_inside = int((~finite_mask & footprint_mask).sum())
        add("no_nan_inside_footprint", nan_inside == 0, f"nan_inside={nan_inside}")
    else:
        add("no_nan_inside_footprint", n_nan == 0, "no footprint mask supplied")

    if reference_rasters:
        dots = data > 0.0
        n_dots = int(dots.sum())
        add("dots_present", n_dots > 0, f"n_dots={n_dots}")
        for ref in reference_rasters:
            with rasterio.open(ref) as rds:
                ref_data = rds.read(1)
            rname = Path(ref).name
            if ref_data.shape != data.shape:
                add(f"uniqueness_shape_match_{rname}", False,
                    f"ref shape {ref_data.shape}")
                ok = False
                continue
            rho = _spearman(data, ref_data)
            add(f"surface_spearman_{rname}", abs(rho) <= 0.90, f"rho={rho:.4f}")
            if abs(rho) > 0.90:
                ok = False
            ref_dots = ref_data > 0.0
            overlap = _dot_overlap_3px(dots, ref_dots, pixel_m=OFFICIAL_PIXEL_M)
            add(f"dots_within_3px_{rname}", overlap <= 0.70,
                f"{overlap:.4f} of {n_dots} dots")
            if overlap > 0.70:
                ok = False
    else:
        add("uniqueness_vs_registry", False, "no reference rasters supplied")
        ok = False

    return ValidationResult(passed=ok, checks=checks,
                            message="PASS" if ok else "FAIL")


def _spearman(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 2:
        return float("nan")
    ra = _rankdata(a[m]).astype(float)
    rb = _rankdata(b[m]).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    denom = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    if denom == 0:
        return 0.0
    return float((ra * rb).sum() / denom)


def _rankdata(x):
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float64)
    sorted_x = x[order]
    i = 0
    n = len(x)
    while i < n:
        j = i
        while j + 1 < n and sorted_x[j + 1] == sorted_x[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def _dot_overlap_3px(dots_a, dots_b, pixel_m=OFFICIAL_PIXEL_M):
    if not dots_a.any():
        return 0.0
    dist = ndimage.distance_transform_edt(~dots_b, sampling=pixel_m)
    near = dist[dots_a] <= 3.0 * pixel_m
    return float(near.mean())


def write_submission(array, out_path, template_meta=None,
                     crs=OFFICIAL_CRS, transform=OFFICIAL_TRANSFORM,
                     nodata=None, compress="lzw"):
    out_path = Path(out_path)
    array = np.asarray(array, dtype=np.float32)

    if template_meta is not None:
        t = template_meta["transform"]
        transform = Affine(t[0], t[1], t[2], t[3], t[4], t[5])
        crs = template_meta["crs"]
        height, width = int(template_meta["height"]), int(template_meta["width"])
    else:
        height, width = OFFICIAL_HEIGHT, OFFICIAL_WIDTH

    if array.shape != (height, width):
        raise ValueError(f"array shape {array.shape} != expected ({height}, {width})")

    profile = {
        "driver": "GTiff",
        "dtype": "float32",
        "nodata": nodata,
        "width": width,
        "height": height,
        "count": 1,
        "crs": crs,
        "transform": transform,
        "compress": compress,
        "tiled": False,
    }

    with rasterio.open(out_path, "w", **profile) as ds:
        ds.write(array, 1)

    receipt = {
        "file": str(out_path),
        "sha256": sha256_file(out_path),
        "bytes": out_path.stat().st_size,
        "crs": crs,
        "shape": [height, width],
        "transform": [transform.a, transform.b, transform.c,
                      transform.d, transform.e, transform.f],
        "dtype": "float32",
        "nodata": nodata,
        "compress": compress,
    }
    with open(out_path.with_suffix(".audit.json"), "w") as f:
        json.dump(receipt, f, indent=2)
    print(f"[submission_writer] wrote {out_path} ({receipt['bytes']} bytes, "
          f"sha256={receipt['sha256'][:16]})", flush=True)
    return receipt


def write_audit_and_run_card(tif_path, validation, run_card, out_dir=None):
    tif_path = Path(tif_path)
    out_dir = Path(out_dir) if out_dir else tif_path.parent
    audit = {
        "file": tif_path.name,
        "sha256": sha256_file(tif_path),
        "validation_passed": validation.passed,
        "validation_message": validation.message,
        "checks": validation.checks,
    }
    audit_path = out_dir / (tif_path.stem + "-audit.json")
    with open(audit_path, "w") as f:
        json.dump(audit, f, indent=2)
    card_path = out_dir / (tif_path.stem + "-run-card.json")
    with open(card_path, "w") as f:
        json.dump(run_card, f, indent=2)
    print(f"[submission_writer] audit -> {audit_path} (PASS={validation.passed})")
    print(f"[submission_writer] run card -> {card_path}")
    return {"audit": str(audit_path), "run_card": str(card_path)}

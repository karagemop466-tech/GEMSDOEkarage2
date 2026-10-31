"""Regression tests for the shared writer's exterior-convention and nodata gates.

Official problem page ("Submission format"): data outside the bounds is null or
nan. Both uniform exteriors (all-NaN and all-finite zeros) are attested among
owner-SCORED focus files (2026-10-31 evidence review), so the gate requires a
UNIFORM exterior of either kind and rejects mixed/inf exteriors. A nodata=NaN
tag on an all-finite file (the H-F signature behind the reported portal range
error) is rejected as inconsistent metadata. These tests use tiny synthetic
rasters and check only the convention-related gates; grid/CRS checks are
expected to fail on the synthetic shape and are not asserted here.
"""
import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import submission_writer as sw  # noqa: E402

CONVENTION_CHECKS = (
    "no_nan_inside_footprint",
    "finite_inside_footprint",
    "exterior_uniform_zeros_or_nan",
    "in_range_0_1",
    "nodata_tag_consistent_with_pixels",
)


def _write(path, arr, nodata=None):
    with rasterio.open(
        path, "w", driver="GTiff", dtype="float32", count=1,
        width=arr.shape[1], height=arr.shape[0], crs="EPSG:32611",
        transform=from_origin(0, 0, 100, 100), nodata=nodata,
    ) as ds:
        ds.write(arr.astype(np.float32), 1)
    return path


def _checks(path, footprint):
    result = sw.validate_geotiff(path, footprint_mask=footprint)
    checks = {c["check"]: c["passed"] for c in result.checks}
    assert all(name in checks for name in CONVENTION_CHECKS)
    return checks


@pytest.fixture()
def footprint():
    fp = np.zeros((6, 8), dtype=bool)
    fp[1:5, 2:6] = True
    return fp


def _base(footprint):
    arr = np.full(footprint.shape, np.nan, dtype=np.float32)
    arr[footprint] = 0.0
    arr[1, 2] = 0.7
    return arr


def test_nan_outside_footprint_passes_convention(tmp_path, footprint):
    path = _write(tmp_path / "nan_outside.tif", _base(footprint), nodata=np.nan)
    checks = _checks(path, footprint)
    assert checks["no_nan_inside_footprint"] is True
    assert checks["exterior_uniform_zeros_or_nan"] is True
    assert checks["in_range_0_1"] is True
    assert checks["nodata_tag_consistent_with_pixels"] is True


def test_zero_outside_footprint_passes_convention(tmp_path, footprint):
    # 2026-10-31 correction: uniform finite zeros outside the footprint are an
    # attested owner-scored convention (incl. the 0.2778 champion) and pass.
    arr = _base(footprint)
    arr[~footprint] = 0.0
    path = _write(tmp_path / "zero_outside.tif", arr)
    checks = _checks(path, footprint)
    assert checks["exterior_uniform_zeros_or_nan"] is True
    assert checks["no_nan_inside_footprint"] is True
    assert checks["nodata_tag_consistent_with_pixels"] is True


def test_mixed_exterior_fails(tmp_path, footprint):
    arr = _base(footprint)
    arr[~footprint] = 0.0
    arr[0, 0] = np.nan  # inside the uniform-zeros exterior region
    path = _write(tmp_path / "mixed_exterior.tif", arr)
    assert _checks(path, footprint)["exterior_uniform_zeros_or_nan"] is False


def test_nodata_nan_tag_with_zero_exterior_fails(tmp_path, footprint):
    # The H-F signature: nodata=NaN declared while every pixel is finite.
    arr = _base(footprint)
    arr[~footprint] = 0.0
    path = _write(tmp_path / "nodata_nan_zero_pixels.tif", arr, nodata=np.nan)
    checks = _checks(path, footprint)
    assert checks["nodata_tag_consistent_with_pixels"] is False


def test_nan_inside_footprint_fails(tmp_path, footprint):
    arr = _base(footprint)
    arr[2, 3] = np.nan
    path = _write(tmp_path / "nan_inside.tif", arr)
    assert _checks(path, footprint)["no_nan_inside_footprint"] is False


def test_infinity_outside_footprint_is_not_accepted_as_exterior(tmp_path, footprint):
    arr = _base(footprint)
    arr[0, 0] = np.inf
    path = _write(tmp_path / "infinite_outside.tif", arr)
    checks = _checks(path, footprint)
    assert checks["exterior_uniform_zeros_or_nan"] is False


def test_infinity_inside_footprint_fails_finiteness_and_range(tmp_path, footprint):
    arr = _base(footprint)
    arr[2, 3] = np.inf
    path = _write(tmp_path / "infinite_inside.tif", arr)
    checks = _checks(path, footprint)
    assert checks["finite_inside_footprint"] is False
    assert checks["in_range_0_1"] is False


def test_out_of_range_inside_value_fails(tmp_path, footprint):
    arr = _base(footprint)
    arr[2, 3] = 1.5
    path = _write(tmp_path / "out_of_range.tif", arr)
    assert _checks(path, footprint)["in_range_0_1"] is False


def test_footprint_shape_mismatch_fails_closed(tmp_path, footprint):
    path = _write(tmp_path / "wrong_fp.tif", _base(footprint))
    result = sw.validate_geotiff(path, footprint_mask=footprint[:-1, :])
    checks = {c["check"]: c["passed"] for c in result.checks}
    assert checks["no_nan_inside_footprint"] is False
    assert checks["finite_inside_footprint"] is False
    assert checks["exterior_uniform_zeros_or_nan"] is False
    assert checks["in_range_0_1"] is False
    assert result.passed is False


def test_missing_footprint_fails_closed(tmp_path, footprint):
    path = _write(tmp_path / "no_fp.tif", _base(footprint))
    result = sw.validate_geotiff(path, footprint_mask=None)
    checks = {c["check"]: c["passed"] for c in result.checks}
    assert checks["no_nan_inside_footprint"] is False
    assert checks["exterior_uniform_zeros_or_nan"] is False
    assert checks["finite_inside_footprint"] is False
    assert result.passed is False

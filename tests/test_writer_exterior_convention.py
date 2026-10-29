"""Regression tests for the shared writer's exterior (NaN-outside) convention.

Official problem page ("Submission format"): data outside the bounds is null or
nan. The organizer sample template is NaN outside its footprint. These tests use
tiny synthetic rasters and check only the convention-related gates; grid/CRS
checks are expected to fail on the synthetic shape and are not asserted here.
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
    "outside_footprint_is_nan",
    "in_range_0_1",
)


def _write(path, arr):
    with rasterio.open(
        path, "w", driver="GTiff", dtype="float32", count=1,
        width=arr.shape[1], height=arr.shape[0], crs="EPSG:32611",
        transform=from_origin(0, 0, 100, 100),
    ) as ds:
        ds.write(arr.astype(np.float32), 1)
    return path


def _checks(path, footprint):
    result = sw.validate_geotiff(path, footprint_mask=footprint)
    return {c["check"]: c["passed"] for c in result.checks}


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
    path = _write(tmp_path / "nan_outside.tif", _base(footprint))
    checks = _checks(path, footprint)
    assert checks["no_nan_inside_footprint"] is True
    assert checks["outside_footprint_is_nan"] is True
    assert checks["in_range_0_1"] is True


def test_zero_outside_footprint_fails_convention(tmp_path, footprint):
    arr = _base(footprint)
    arr[~footprint] = 0.0  # the defect found in the saved HK3/K2/K3 rasters
    path = _write(tmp_path / "zero_outside.tif", arr)
    checks = _checks(path, footprint)
    assert checks["outside_footprint_is_nan"] is False
    assert checks["no_nan_inside_footprint"] is True


def test_nan_inside_footprint_fails(tmp_path, footprint):
    arr = _base(footprint)
    arr[2, 3] = np.nan
    path = _write(tmp_path / "nan_inside.tif", arr)
    assert _checks(path, footprint)["no_nan_inside_footprint"] is False


def test_out_of_range_inside_value_fails(tmp_path, footprint):
    arr = _base(footprint)
    arr[2, 3] = 1.5
    path = _write(tmp_path / "out_of_range.tif", arr)
    assert _checks(path, footprint)["in_range_0_1"] is False


def test_missing_footprint_fails_closed(tmp_path, footprint):
    path = _write(tmp_path / "no_fp.tif", _base(footprint))
    result = sw.validate_geotiff(path, footprint_mask=None)
    checks = {c["check"]: c["passed"] for c in result.checks}
    assert checks["no_nan_inside_footprint"] is False
    assert checks["outside_footprint_is_nan"] is False
    assert result.passed is False

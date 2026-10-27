"""Exercise the actual pinned shared writer and validator, if bootstrapped."""
import json
from pathlib import Path
import numpy as np
import pytest
import rasterio
from rasterio.windows import Window
from scripts.audit_references import DEFAULT_CACHE, MANIFEST, load_shared


@pytest.fixture(scope="module")
def shared():
    sample = DEFAULT_CACHE / "inputs/sample.tif"
    if not sample.exists():
        pytest.skip("Run scripts/bootstrap_research.py for the shared-tool integration tests")
    spec = json.loads(MANIFEST.read_text())
    _, submission = load_shared(DEFAULT_CACHE, spec)
    return submission, sample


def test_real_shared_writer_validator_and_exterior_diagnostics(shared, tmp_path):
    submission, sample = shared
    with rasterio.open(sample) as ds:
        arr = ds.read(1)
    inside = np.isfinite(arr)
    first_row, first_col = (int(x) for x in np.argwhere(inside)[0])
    pred = np.zeros(arr.shape, dtype=np.float32)
    target = tmp_path / "synthetic-diagnostic-not-a-submission.tif"
    submission.write_submission(pred, sample, target, outside="nan")
    report = submission.check_variants(target, sample)
    assert report["format_valid"]
    assert report["checks"]["outside_is_nan_official_text"]["pass"]
    assert not report["checks"]["variant_strict_whole_array_no_nan_allowed"]["pass"]
    assert report["submission_authorized"] is False
    assert report["ok_to_upload"] is False
    from scripts.check_submission import check
    wrapped = check(target)
    assert wrapped["official_format_compliant"] is None
    assert wrapped["upstream_mirror_based_exterior_and_format_diagnostic"] is True
    assert wrapped["upstream_official_check_names_are_not_authenticated"] is True
    assert wrapped["submission_authorized"] is False
    for value, key in [(-0.01, "footprint_range_0_1"), (1.01, "footprint_range_0_1"), (np.nan, "footprint_all_finite")]:
        with rasterio.open(target, "r+") as ds:
            ds.write(np.array([[value]], dtype=np.float32), 1, window=Window(first_col, first_row, 1, 1))
        bad = submission.check_variants(target, sample)
        assert not bad["format_valid"] and not bad["checks"][key]["pass"]
        assert not bad["submission_authorized"]
    submission.write_submission(pred, sample, target, outside="zero")
    zero = submission.check_variants(target, sample)
    assert zero["checks"]["variant_strict_whole_array_no_nan_allowed"]["pass"]
    assert not zero["checks"]["outside_is_nan_official_text"]["pass"]
    assert not zero["official_format_compliant"] and not zero["submission_authorized"]


def test_shared_writer_rejects_invalid_values_and_shape(shared, tmp_path):
    submission, sample = shared
    with rasterio.open(sample) as ds:
        footprint = np.isfinite(ds.read(1))
    pred = np.zeros(footprint.shape, dtype=np.float32)
    pred[footprint] = -0.01
    with pytest.raises(ValueError, match=r"finite and in \[0,1\]"):
        submission.write_submission(pred, sample, tmp_path / "invalid.tif")
    with pytest.raises(ValueError, match="shape"):
        submission.write_submission(np.zeros((3, 3), dtype=np.float32), sample, tmp_path / "invalid.tif")
    assert not (tmp_path / "invalid.tif").exists()


def test_validator_rejects_wrong_crs_transform_shape_and_band_format(shared, tmp_path):
    from affine import Affine
    submission, sample = shared
    with rasterio.open(sample) as source:
        shape = source.shape
        profile = source.profile.copy()
        original_crs = source.crs
        original_transform = source.transform
    target = tmp_path / "synthetic-grid-diagnostic.tif"
    submission.write_submission(np.zeros(shape, dtype=np.float32), sample, target, outside="nan")
    with rasterio.open(target, "r+") as out:
        out.crs = "EPSG:4326"
    wrong_crs = submission.check_variants(target, sample)
    assert not wrong_crs["format_valid"] and not wrong_crs["checks"]["crs_epsg_32611"]["pass"]
    with rasterio.open(target, "r+") as out:
        out.crs = original_crs
        out.transform = original_transform @ Affine.translation(1, 0)
    wrong_transform = submission.check_variants(target, sample)
    assert not wrong_transform["format_valid"] and not wrong_transform["checks"]["geotransform_matches_template"]["pass"]
    profile.update(width=3, height=3, count=2, dtype="float64", nodata=None)
    with rasterio.open(target, "w", **profile) as out:
        out.write(np.zeros((2, 3, 3), dtype=np.float64))
    wrong_grid = submission.check_variants(target, sample)
    for name in ("shape_matches_template", "single_band", "dtype_float32"):
        assert not wrong_grid["checks"][name]["pass"]
    assert not wrong_grid["format_valid"] and not wrong_grid["submission_authorized"]


def test_check_submission_cli_fails_closed_for_missing_file(tmp_path):
    import subprocess
    import sys
    from scripts.audit_references import ROOT
    missing = tmp_path / "missing.tif"
    command = [sys.executable, str(ROOT / "scripts/check_submission.py"), str(missing)]
    result = subprocess.run(command, capture_output=True, text=True, cwd=ROOT)
    assert result.returncode != 0
    report = json.loads(result.stdout)
    assert report["format_valid"] is False
    assert report["official_format_compliant"] is None
    assert report["submission_authorized"] is False
    assert "error" in report

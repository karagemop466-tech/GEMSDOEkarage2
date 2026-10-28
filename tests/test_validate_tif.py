from pathlib import Path
import sys

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_tif import validate


def write(path, array, *, crs="EPSG:32611", transform=None, nodata=np.nan, count=1):
    array = np.asarray(array)
    with rasterio.open(path, "w", driver="GTiff", height=array.shape[0], width=array.shape[1],
                       count=count, dtype=array.dtype, crs=crs,
                       transform=transform or from_origin(100, 500, 100, 100), nodata=nodata) as ds:
        for band in range(1, count + 1):
            ds.write(array, band)


@pytest.fixture
def inputs(tmp_path):
    template = np.full((5, 6), np.nan, dtype="float32")
    template[1:4, 1:5] = 0
    template_path = tmp_path / "template.tif"
    write(template_path, template)
    candidate = template.copy()
    candidate[2, 2] = .8
    return tmp_path, template_path, candidate


def test_validity_is_not_upload_authorization(inputs):
    path, template, candidate = inputs
    write(path / "ok.tif", candidate)
    result = validate(path / "ok.tif", template)
    assert result["strict_format_pass"] is True
    assert result["diagnostics"]["inside_nan"] == 0
    assert result["diagnostics"]["whole_array_finite_in_range"] is False
    assert result["upload_authorized"] is False
    assert result["template_authenticity"] == "not established by this check"


@pytest.mark.parametrize("bad", [-3.4028235e38, -0.01, 1.01, np.nan, np.inf, -np.inf])
def test_rejects_every_bad_inside_value(inputs, bad):
    path, template, candidate = inputs
    candidate[2, 2] = bad
    write(path / "bad.tif", candidate)
    result = validate(path / "bad.tif", template)
    assert result["strict_format_pass"] is False
    assert result["checks"]["inside_in_range_0_1"] is False


def test_zero_outside_is_range_diagnostic_not_strict_pass(inputs):
    path, template, candidate = inputs
    candidate[np.isnan(candidate)] = 0
    write(path / "zeros.tif", candidate, nodata=None)
    result = validate(path / "zeros.tif", template)
    assert result["diagnostics"]["whole_array_finite_in_range"] is True
    assert result["checks"]["outside_is_nan"] is False
    assert result["strict_format_pass"] is False


@pytest.mark.parametrize("kwargs,check", [
    ({"crs": "EPSG:4326"}, "crs_matches_template"),
    ({"transform": from_origin(101, 500, 100, 100)}, "transform_matches_template"),
    ({"count": 2}, "single_band"),
])
def test_grid_and_band_failures(inputs, kwargs, check):
    path, template, candidate = inputs
    write(path / "wrong.tif", candidate, **kwargs)
    result = validate(path / "wrong.tif", template)
    assert result["checks"][check] is False
    assert result["strict_format_pass"] is False


def test_different_shape_fails_without_indexing_error(inputs):
    path, template, candidate = inputs
    write(path / "wrong.tif", candidate[:4, :])
    result = validate(path / "wrong.tif", template)
    assert result["checks"]["shape_matches_template"] is False
    assert result["strict_format_pass"] is False


def test_zero_nodata_masks_valid_predictions_and_is_rejected(inputs):
    path, template, candidate = inputs
    write(path / "masked.tif", candidate, nodata=0)
    result = validate(path / "masked.tif", template)
    assert result["checks"]["inside_no_masked_cells"] is False
    assert result["strict_format_pass"] is False


@pytest.mark.parametrize("which", ["template", "candidate"])
def test_external_mask_not_bound_by_tiff_hash_is_rejected(inputs, which):
    path, template, candidate = inputs
    candidate_path = path / "candidate.tif"
    write(candidate_path, candidate)
    target = template if which == "template" else candidate_path
    before = target.read_bytes()
    # GDAL normally honors this sidecar over the raster's nodata mask, even
    # though it is not part of the TIFF digest recorded by the receipt.
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=False):
        with rasterio.open(target, "r+") as ds:
            ds.write_mask(np.ones(ds.shape, dtype="uint8") * 255)
    assert target.read_bytes() == before
    assert Path(str(target) + ".msk").exists()
    with pytest.raises(ValueError, match="external GDAL dependencies"):
        validate(candidate_path, template)

"""The full named-file preflight is a local schema diagnostic, not organizer auth."""
import json

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from scripts import prepare_data


def write_tif(path, *, x=0, crs='EPSG:32611', count=1):
    with rasterio.open(path, 'w', driver='GTiff', height=4, width=4, count=count,
                       dtype='float32', crs=crs, nodata=np.nan,
                       transform=from_origin(x, 400, 100, 100)) as ds:
        for band in range(1, count + 1):
            ds.write(np.zeros((4, 4), dtype='float32'), band)


def data_set(tmp_path, monkeypatch):
    monkeypatch.setattr(prepare_data, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(prepare_data, 'EXPECTED_SHAPE', (4, 4))
    for name in prepare_data.CORE_FILES:
        write_tif(tmp_path / name, count=19 if name == 'training_features.tif' else 1)
    (tmp_path / prepare_data.DEM_LINKS).write_text('url\n')


def receipt(tmp_path):
    return json.loads((tmp_path / 'prepared.json').read_text(),
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def test_matched_grid_is_only_a_local_diagnostic(tmp_path, monkeypatch):
    data_set(tmp_path, monkeypatch)
    assert prepare_data.main([]) == 0
    result = receipt(tmp_path)
    assert result['schema_pass'] is True and result['upload_authorized'] is False
    assert result['checks']['matching_shape_crs_transform'] is True
    assert any('not authenticated' in text for text in result['irregularities'])


@pytest.mark.parametrize('mutation,failed_check', [
    ('offset', 'matching_shape_crs_transform'),
    ('no_crs', 'expected_epsg_32611'),
    ('multi_band', 'sample_one_float32_band'),
])
def test_inconsistent_or_invalid_template_fails_closed(tmp_path, monkeypatch, mutation, failed_check):
    data_set(tmp_path, monkeypatch)
    if mutation == 'offset':
        write_tif(tmp_path / 'labels.tif', x=1)
    elif mutation == 'no_crs':
        for name in prepare_data.CORE_FILES:
            write_tif(tmp_path / name, crs=None, count=19 if name == 'training_features.tif' else 1)
    else:
        write_tif(tmp_path / 'sample_submission.tif', count=2)
    assert prepare_data.main([]) == 1
    assert receipt(tmp_path)['checks'][failed_check] is False
    assert receipt(tmp_path)['schema_pass'] is False


def test_missing_input_invalidates_old_success(tmp_path, monkeypatch):
    data_set(tmp_path, monkeypatch)
    assert prepare_data.main([]) == 0
    (tmp_path / 'labels.tif').unlink()
    assert prepare_data.main([]) == 1
    result = receipt(tmp_path)
    assert not result['schema_pass'] and 'labels.tif' in result['missing']


def test_unreadable_input_invalidates_old_success(tmp_path, monkeypatch):
    data_set(tmp_path, monkeypatch)
    assert prepare_data.main([]) == 0
    (tmp_path / 'labels.tif').write_bytes(b'not a raster')
    assert prepare_data.main([]) == 1
    assert receipt(tmp_path)['schema_pass'] is False
    assert receipt(tmp_path)['upload_authorized'] is False

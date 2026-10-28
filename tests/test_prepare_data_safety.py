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
    for name in prepare_data.EXPECTED:
        if name.endswith('.tif'):
            write_tif(tmp_path / name)
        else:
            (tmp_path / name).write_text('url\n')


def test_matched_grid_is_only_a_local_diagnostic(tmp_path, monkeypatch):
    data_set(tmp_path, monkeypatch)
    assert prepare_data.main() == 0
    result = json.loads((tmp_path / 'prepared.json').read_text(),
                        parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    assert result['grids_consistent'] is True
    assert 'not input authentication' in result['note']


@pytest.mark.parametrize('mutation', ['offset', 'no_crs', 'multi_band'])
def test_inconsistent_or_invalid_template_fails_closed(tmp_path, monkeypatch, mutation):
    data_set(tmp_path, monkeypatch)
    if mutation == 'offset':
        write_tif(tmp_path / 'labels.tif', x=1)
    elif mutation == 'no_crs':
        for name in prepare_data.EXPECTED:
            if name.endswith('.tif'):
                write_tif(tmp_path / name, crs=None)
    else:
        write_tif(tmp_path / 'sample_submission.tif', count=2)
    assert prepare_data.main() == 1
    assert json.loads((tmp_path / 'prepared.json').read_text())['grids_consistent'] is False


def test_missing_input_invalidates_old_success(tmp_path, monkeypatch):
    data_set(tmp_path, monkeypatch)
    assert prepare_data.main() == 0
    (tmp_path / 'labels.tif').unlink()
    assert prepare_data.main() == 1
    result = json.loads((tmp_path / 'prepared.json').read_text())
    assert not result['grids_consistent'] and 'labels.tif' in result['missing_files']


def test_unreadable_input_invalidates_old_success(tmp_path, monkeypatch):
    data_set(tmp_path, monkeypatch)
    assert prepare_data.main() == 0
    (tmp_path / 'labels.tif').write_bytes(b'not a raster')
    with pytest.raises(rasterio.errors.RasterioError):
        prepare_data.main()
    assert not json.loads((tmp_path / 'prepared.json').read_text())['grids_consistent']

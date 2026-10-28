"""Scratch mirror restoration and data preflight fail closed without official auth."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from scripts import prepare_data, restore_data


GRID = from_origin(243350, 4508550, 100, 100)


@pytest.fixture(autouse=True)
def small_synthetic_shape(monkeypatch):
    # Test small arrays only; production always requires the pinned full grid.
    monkeypatch.setattr(prepare_data, 'EXPECTED_SHAPE', (5, 6))


def tif(path: Path, values: np.ndarray, *, transform=GRID, nodata=None):
    if values.ndim == 2:
        values = values[None]
    with rasterio.open(path, 'w', driver='GTiff', width=values.shape[2],
                       height=values.shape[1], count=values.shape[0],
                       dtype=values.dtype, crs='EPSG:32611', transform=transform,
                       nodata=nodata) as ds:
        ds.write(values)


def fixture_data(directory: Path):
    features = np.zeros((19, 5, 6), np.float32)
    labels = np.zeros((5, 6), np.int8)
    labels[2, 3] = 1
    sample = np.zeros((5, 6), np.float32)
    sample[0, 0] = np.nan
    sample[2, 3] = 1
    for name, data, nodata in (
        ('training_features.tif', features, -3.4028234663852886e38),
        ('labels.tif', labels, -1),
        ('existing_faults.tif', labels, -1),
        ('sample_submission.tif', sample, np.nan),
    ):
        tif(directory / name, data, nodata=nodata)
    (directory / '1m_DEM_links.csv').write_text('url\nhttps://example.invalid/test\n')


def test_core_mirror_schema_is_not_organizer_approval(tmp_path):
    fixture_data(tmp_path)
    manifest = {'files': []}
    for name in prepare_data.CORE_FILES:
        path = tmp_path / name
        manifest['files'].append({'dest': name, 'bytes': path.stat().st_size,
                                  'sha256': prepare_data.sha256(path)})
    manifest_path = tmp_path / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest))
    report = prepare_data.inspect(tmp_path, core_only=True, mirror_manifest=manifest_path)
    assert report['schema_pass'] is True
    assert report['upload_authorized'] is False
    assert report['checks']['owner_mirror_hashes'] is True
    assert report['diagnostics']['sample_positive_equals_labels_inside'] is True
    assert report['diagnostics']['sample_positive_pixels'] == 1
    assert any('sample contains positive' in entry for entry in report['irregularities'])
    assert 'nan' in json.dumps(report, allow_nan=False).lower()

    (tmp_path / 'training_features.tif').write_bytes(b'not the pinned mirror')
    assert prepare_data.main(['--data-dir', str(tmp_path), '--core-only',
                              '--mirror-manifest', str(manifest_path)]) == 1
    failed = json.loads((tmp_path / 'prepared.json').read_text())
    assert failed['schema_pass'] is False
    assert failed['upload_authorized'] is False


def test_wrong_template_dimensions_fail_even_if_all_rasters_agree(tmp_path, monkeypatch):
    fixture_data(tmp_path)
    monkeypatch.setattr(prepare_data, 'EXPECTED_SHAPE', (3730, 3292))
    report = prepare_data.inspect(tmp_path, core_only=True)
    assert report['checks']['matching_shape_crs_transform'] is True
    assert report['checks']['expected_mirror_shape'] is False
    assert report['schema_pass'] is False


def test_mismatch_and_empty_dem_list_are_not_prepared_success(tmp_path):
    fixture_data(tmp_path)
    assert prepare_data.main(['--data-dir', str(tmp_path)]) == 0
    receipt = json.loads((tmp_path / 'prepared.json').read_text())
    assert receipt['schema_pass'] is True and receipt['upload_authorized'] is False
    assert receipt['files'][3]['nodata_repr'] == 'nan'
    (tmp_path / '1m_DEM_links.csv').write_bytes(b'')
    assert prepare_data.main(['--data-dir', str(tmp_path)]) == 1
    assert json.loads((tmp_path / 'prepared.json').read_text())['checks']['dem_links_nonempty'] is False
    broken = from_origin(243450, 4508550, 100, 100)
    tif(tmp_path / 'training_features.tif', np.zeros((19, 5, 6), np.float32), transform=broken)
    assert prepare_data.main(['--data-dir', str(tmp_path)]) == 1
    assert json.loads((tmp_path / 'prepared.json').read_text())['checks']['matching_shape_crs_transform'] is False


def test_missing_data_overwrites_a_stale_positive_receipt_with_failure(tmp_path):
    (tmp_path / 'prepared.json').write_text('{"schema_pass": true}')
    report = prepare_data.inspect(tmp_path)
    assert report['schema_pass'] is False and report['missing']
    assert prepare_data.main(['--data-dir', str(tmp_path)]) == 1
    failure = json.loads((tmp_path / 'prepared.json').read_text())
    assert failure['schema_pass'] is False and failure['upload_authorized'] is False


def test_restore_default_manifest_exists_and_restore_path_is_guarded(tmp_path, monkeypatch):
    assert (restore_data.ROOT / 'registry/core_data_manifest.json').is_file()
    assert not (restore_data.ROOT / 'registry/data_manifest.json').exists()
    original = b'one known mirrored input'
    entry = dict(id='fixture', dest='sample_submission.tif',
                 sha256=hashlib.sha256(original).hexdigest(), group='core',
                 repo='fixture/repo', ref='pinned', path='file.tif')
    monkeypatch.setattr(restore_data, 'fetch', lambda _repo, _ref, _path, dest: dest.write_bytes(original))
    result = restore_data.restore_entry(entry, tmp_path)
    assert result['status'] == 'restored'
    assert restore_data.restore_entry(entry, tmp_path)['status'] == 'present'
    for bad in ('../outside.txt', 'sub/../../outside.txt', '.'):
        with pytest.raises(ValueError, match='Unsafe mirror destination'):
            restore_data.restore_entry({**entry, 'dest': bad}, tmp_path)


def test_bad_multipart_hash_leaves_no_assembly(tmp_path, monkeypatch):
    def fake_fetch(_repo, _ref, _part, dest):
        dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(b'wrong bytes')
    monkeypatch.setattr(restore_data, 'fetch', fake_fetch)
    entry = dict(id='fixture', dest='features.tif', sha256='a' * 64, group='core',
                 repo='fixture/repo', ref='pinned', parts=['one.part'])
    with pytest.raises(ValueError, match='HASH MISMATCH'):
        restore_data.restore_entry(entry, tmp_path)
    assert not (tmp_path / 'features.tif').exists()
    assert not (tmp_path / 'features.tif.assembling').exists()

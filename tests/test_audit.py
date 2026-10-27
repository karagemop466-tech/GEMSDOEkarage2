import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pytest
import rasterio
from affine import Affine
from scipy.ndimage import binary_dilation
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import audit_focus as audit


def test_exact_overlap_bound_and_boundary():
    assert audit.overlap_bound(10, 3) == 0.7  # exactly 70% is permitted
    assert audit.overlap_bound(10, 2) == 0.8
    assert audit.overlap_bound(2, 100) == 0
    assert audit.overlap_bound(37654, 6649) == pytest.approx(0.8234184947150369)
    with pytest.raises(ValueError):
        audit.overlap_bound(0, 1)
    with pytest.raises(ValueError):
        audit.overlap_bound(2, -1)
    with pytest.raises(ValueError):
        audit.overlap_bound(2.5, 1)
    with pytest.raises(ValueError):
        audit.overlap_bound(True, 1)
    assert audit.overlap_bound(22163, 6649) <= .7
    assert audit.overlap_bound(22164, 6649) > .7


def test_dilation_uses_closed_euclidean_disk_without_wrap():
    d = audit.disk(3)
    assert d.shape == (7, 7)
    assert d[3, 6] and d[5, 5] and not d[4, 6]
    arr = np.zeros((8, 8), bool)
    arr[0, 0] = True
    dilated = binary_dilation(arr, structure=d)
    assert dilated[0, 3] and not dilated[0, 4] and not dilated[-1, -1]


def test_binary_spearman_is_exact_for_ties_and_constants():
    rng = np.random.default_rng(19)
    a = rng.random((10, 12)) > .7
    b = rng.random((10, 12)) > .8
    mask = rng.random((10, 12)) > .2
    assert audit.binary_spearman(a, b, mask) == pytest.approx(spearmanr(a[mask], b[mask]).statistic)
    assert audit.binary_spearman(np.zeros_like(a), b, mask) is None


def item_for(path: Path, role: str, site: str | None = None):
    data = path.read_bytes()
    obj = {'role': role, 'repo': 'example/repo', 'ref': 'a' * 40, 'path': path.name,
           'cache_name': path.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
           'git_blob_sha1': hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()}
    if site:
        obj.update(site=site, reported_score=.1, score_evidence='USER-REPORTED / UNVERIFIED')
    return obj


def write_tif(path, arr, *, count=1, transform=None):
    with rasterio.open(path, 'w', driver='GTiff', height=arr.shape[0], width=arr.shape[1],
                       count=count, dtype='float32', crs='EPSG:32611',
                       transform=transform or Affine(100, 0, 0, 0, -100, 1200)) as ds:
        for i in range(1, count + 1):
            ds.write(arr.astype('float32'), i)


def test_read_alignment_and_single_band(tmp_path):
    a = np.zeros((4, 5), np.float32)
    write_tif(tmp_path/'a.tif', a)
    write_tif(tmp_path/'b.tif', a, transform=Affine(100, 0, 100, 0, -100, 1200))
    write_tif(tmp_path/'multiband.tif', a, count=2)
    _, _, grid, _, _ = audit.read_aligned(tmp_path/'a.tif')
    with pytest.raises(ValueError, match='Grid mismatch'):
        audit.read_aligned(tmp_path/'b.tif', grid)
    with pytest.raises(ValueError, match='single-band'):
        audit.read_aligned(tmp_path/'multiband.tif', grid)


def test_pinned_cache_detects_modification_and_path_traversal(tmp_path):
    p = tmp_path/'x.bin'
    p.write_bytes(b'expected')
    item = item_for(p, 'template')
    assert audit.restore(item, tmp_path, False) == p
    p.write_bytes(b'corrupted')
    with pytest.raises(ValueError, match='Pinned input differs'):
        audit.restore(item, tmp_path, False)
    item['cache_name'] = '../escape'
    with pytest.raises(ValueError, match='Invalid cache name'):
        audit.restore(item, tmp_path, False)


def test_end_to_end_nine_site_audit_on_synthetic_grid(tmp_path):
    shape = (12, 12)
    def raster(name, points):
        a = np.zeros(shape, np.float32)
        for y, x in points:
            a[y, x] = 1
        p = tmp_path/name
        write_tif(p, a)
        return p
    assets = [item_for(raster('template.tif', [(5, 5)]), 'template'),
              item_for(raster('faults.tif', [(5, 5)]), 'existing_faults'),
              item_for(raster('lattice.tif', [(0, 0), (6, 6)]), 'lattice')]
    sites = ['GEMSDOE24','GEMSDOE25','GEMSDOE27','GEMSDOE28','GEMSDOE30','GEMSDOE31','GEMSDOE32','GEMSDOE33','GEMSDOE36']
    masks = {'GEMSDOE25': [(2,2)], 'GEMSDOE30': [(2,2)],
             'GEMSDOE31': [(5,5), (10,10)], 'GEMSDOE32': [(10,10)],
             'GEMSDOE36': [(10,10), (0,11)]}
    for s in sites:
        assets.append(item_for(raster(s+'.tif', masks.get(s, [(3, 3)])), 'focus', s))
    manifest = tmp_path/'manifest.json'
    manifest.write_text(json.dumps({'scope': 'synthetic test', 'assets': assets}))
    result = audit.run(manifest, tmp_path, False)
    assert len(result['comparisons']) == 72
    assert result['template_anomaly']['positive_mask_equals_existing_faults'] is True
    assert result['forensics']['31_minus_fault_collar_equals_32'] is True
    assert result['forensics']['31_dots_removed_within_two_pixels'] == 1
    assert result['forensics']['25_and_30_identical_dot_masks'] is True
    assert result['forensics']['36_contains_32'] is True
    assert all(not x['submit'] for x in result['sites'])


def test_real_cached_audit_if_available():
    root = Path(__file__).resolve().parents[1]
    manifest = root/'registry/pinned_assets.json'
    assets = json.loads(manifest.read_text())['assets']
    if not all((root/'.cache/inputs'/item['cache_name']).exists() for item in assets):
        pytest.skip('pinned research rasters are optional in CI')
    result = audit.run(manifest, root/'.cache/inputs', False)
    assert result['geometry']['uncovered'] == 6649
    assert result['geometry']['minimum_overlap_at_reference_budget'] > .7
    assert result['forensics']['31_minus_fault_collar_equals_32']
    assert result['forensics']['31_dots_removed_within_two_pixels'] == 2545
    assert result['forensics']['32_dots_added_vs_31'] == 0
    assert all(not x['unique_vs_eight_historical'] for x in result['sites'])

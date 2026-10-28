#!/usr/bin/env python3
"""Recheck the legacy research raster against pinned mirrors; never write a TIFF."""
from pathlib import Path
import hashlib
import json

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
RASTER = ROOT / 'docs/downloads/gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros.tif'
EXPECTED = '28451a64b659b4e206bb483140fac169987db2edea7dc6a2cdc54f1c0f5fbfff'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(cache=ROOT / '.cache/input'):
    manifest = json.loads((ROOT / 'registry/focus_sites.json').read_text())
    paths = [RASTER, cache / 'mirror-sample.tif', cache / 'r13-lattice.tif']
    expected = [EXPECTED, manifest['mirror_template']['sha256'], manifest['witness']['sha256']]
    for path, digest in zip(paths, expected):
        if sha(path) != digest:
            raise ValueError(f'Hash mismatch: {path}')
    with rasterio.open(paths[0]) as ds:
        a = ds.read(1)
        grid = (ds.shape, ds.crs, ds.transform)
        bands, dtype = ds.count, ds.dtypes[0]
    with rasterio.open(paths[1]) as ds:
        if (ds.shape, ds.crs, ds.transform) != grid or ds.count != 1:
            raise ValueError('Template mirror grid mismatch')
        foot = np.isfinite(ds.read(1)) & (ds.read_masks(1) > 0)
    with rasterio.open(paths[2]) as ds:
        if (ds.shape, ds.crs, ds.transform) != grid or ds.count != 1:
            raise ValueError('Lattice grid mismatch')
        lattice = (ds.read(1) > 0) & foot
    if not foot.any() or not lattice.any():
        raise ValueError('Empty footprint or lattice')
    if not np.isfinite(a).all() or np.any((a < 0) | (a > 1)):
        raise ValueError('Legacy artifact has nonfinite or out-of-range values')
    dots = (a > 0) & foot
    n = int(dots.sum())
    if not n:
        raise ValueError('No positive pixels inside mirror footprint')
    near = int((distance_transform_edt(~lattice)[dots] <= 3).sum())
    return {
        'classification': 'GEOMETRY / LOCAL FORMAT AUDIT, not a score or organizer acceptance',
        'candidate_sha256': expected[0], 'mirror_template_sha256': expected[1],
        'lattice_sha256': expected[2], 'single_band': bands == 1,
        'float32': dtype == 'float32', 'mirror_grid_match': True,
        'whole_array_finite_range_0_1': True,
        'positive_inside_mirror_footprint': n,
        'positive_outside_mirror_footprint': int(((a > 0) & ~foot).sum()),
        'positive_inside_within_3px_of_lattice': near,
        'directional_overlap_fraction': near / n,
        'duplicate_stop': near / n > 0.70,
        'scope': 'Pinned owner mirrors; footprint not organizer-authenticated; full registry not checked.',
        'verdict': 'negative', 'submission_authorized': False,
    }


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2, allow_nan=False))

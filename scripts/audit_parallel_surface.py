#!/usr/bin/env python3
"""Independently recheck the parallel H1 research surface; never authorize it.

Requires the pinned mirror inputs restored by audit_focus.py --fetch. This is a
saved-byte/grid/proximity audit, not a rerun of the model or its holdout.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import rasterio
from scipy.ndimage import binary_dilation
from scipy.stats import rankdata
import audit_focus

ROOT = Path(__file__).resolve().parents[1]


def audit(cache: Path) -> dict:
    manifest = json.loads((ROOT / 'registry/pinned_assets.json').read_text())
    items = {x['role']: x for x in manifest['assets'] if x['role'] in ('template', 'lattice', 'existing_faults')}
    if set(items) != {'template', 'lattice', 'existing_faults'}:
        raise ValueError('Missing pinned mirror inputs')
    for item in items.values():
        audit_focus.verify_bytes(cache / item['cache_name'], item)
    card = json.loads((ROOT / 'evidence/run_card.json').read_text())
    path = ROOT / card['raster']
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != card['raster_sha256']:
        raise ValueError('H1 surface checksum mismatch')
    with rasterio.open(cache / items['template']['cache_name']) as ds:
        grid = (ds.height, ds.width, ds.crs, ds.transform)
        footprint = ds.read_masks(1) > 0
    with rasterio.open(path) as ds:
        if ds.count != 1 or ds.dtypes != ('float32',) or (ds.height, ds.width, ds.crs, ds.transform) != grid:
            raise ValueError('H1 surface grid or band mismatch vs owner mirror')
        surface = ds.read(1)
    lattice = audit_focus.read_aligned(cache / items['lattice']['cache_name'], grid)[0]
    labels = audit_focus.read_aligned(cache / items['existing_faults']['cache_name'], grid)[0]
    support = np.isfinite(surface) & (surface > 0) & footprint
    lattice_support = np.isfinite(lattice) & (lattice > 0) & footprint
    ys, xs = np.ogrid[-3:4, -3:4]
    near = binary_dilation(lattice_support, structure=ys * ys + xs * xs <= 9)
    count = int(support.sum())
    if not count:
        raise ValueError('Empty H1 support')
    x, y = surface[footprint], lattice_support[footprint]
    ranks = rankdata(x).astype(np.float64)
    ranks -= ranks.mean()
    n, k = len(x), int(y.sum())
    norm = np.linalg.norm(ranks) * np.sqrt(k * (n - k) / n)
    rho = float(ranks[y].sum() / norm) if norm else None
    return {
        'observed_utc': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'scope': 'Independent saved-byte, owner-mirror grid and single lattice-witness check; H1 holdout not rerun.',
        'raster': card['raster'], 'sha256': sha, 'single_band_float32': True,
        'owner_mirror_grid_match': True, 'organizer_template_authenticated': False,
        'finite_whole_array': bool(np.isfinite(surface).all()),
        'min': float(surface.min()), 'max': float(surface.max()),
        'positive_on_mirrored_catalogue': int((support & (labels > 0)).sum()),
        'positive_outside_mirrored_footprint': int(((surface > 0) & ~footprint).sum()),
        'positive_inside_mirrored_footprint': count,
        'lattice_witness_sha256': items['lattice']['sha256'],
        'support_within_3px': int((support & near).sum()),
        'support_overlap_fraction': float((support & near).sum() / count),
        'spearman_full_footprint': rho,
        'comparison_semantics': 'Continuous pre-placement surface treated as finite-positive support per inherited literal gate; no final dots were placed.',
        'holdout_reproduced_in_this_audit': False,
        'organizer_acceptance': None, 'submission_authorized': False,
        'verdict': 'negative',
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=ROOT / '.cache/inputs')
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/data/parallel-surface-audit.json')
    args = parser.parse_args()
    report = audit(args.cache)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()

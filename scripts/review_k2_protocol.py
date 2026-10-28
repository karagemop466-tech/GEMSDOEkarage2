#!/usr/bin/env python3
"""Read back K2 and report the binding protocol decision; never generates a raster.

This review uses prior evidence, not a rerun of the holdout or a complete registry
scan. An incomplete or failed check cannot authorize a competition submission.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'evidence/k2'
TIF = ROOT / 'docs/downloads/gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif'


def load(path):
    return json.loads(path.read_text())


def review():
    prior = load(E / 'run_card.json')
    surface = load(E / 'final_generation.json')['surface_registry_rows']['r13_lattice']
    final = load(E / 'final_registry_audit.json')
    strict = load(E / 'validate_tif_strict.json')
    digest = hashlib.sha256(TIF.read_bytes()).hexdigest()
    with rasterio.open(TIF) as ds:
        a = ds.read(1)
        finite_in_range = bool(np.isfinite(a).all() and (a >= 0).all() and (a <= 1).all())
        metadata = {'single_band': ds.count == 1, 'dtype': ds.dtypes[0],
                    'shape': list(ds.shape), 'crs': str(ds.crs),
                    'transform': list(ds.transform)[:6]}
    return {
        'scope': 'Repository safety review of a prior K2 experiment; no experiment or slot used',
        'hypothesis': prior['hypothesis'], 'mechanism': prior['mechanism'],
        'named_non_fault_mimic': prior['named_non_fault_mimic'],
        'holdout': prior['holdout'],
        'holdout_caveat': 'Historical receipt, not rerun; not an estimate of the private leaderboard score.',
        'registry': {
            'surface_before_placement': surface,
            'surface_stop_exceeded': surface['literal_support_overlap_gt0'] > 0.70,
            'final_max_overlap': final['worst_dot_overlap'],
            'final_max_rho': final['worst_spearman_full_footprint'],
            'final_witness': final['worst_overlap_submission'],
            'complete_accessible_scan': final['complete_accessible_scan'],
            'unique': final['unique'],
            'scope_caveat': 'Prior saved audit; inventory incomplete and excludes other teams/private history.'
        },
        'raster_sha256': digest,
        'validator_output': {
            'hash_matches_prior': digest == prior['raster_sha256'],
            'current_whole_array_finite_in_range': finite_in_range,
            'current_metadata': metadata,
            'prior_mirror_template_checks': strict['checks'],
            'prior_strict_format_pass': strict['strict_format_pass'],
            'template_authenticity': strict['template_authenticity'],
            'portal_acceptance': 'Not verified',
        },
        'submission_name': prior['submission_name'], 'note': prior['note'],
        'leaderboard_estimate': None, 'experiments_run_this_review': 0,
        'weekly_slots_used_this_review': 0, 'verdict': 'negative',
        'submission_approved': False,
        'reason': 'Literal surface stop exceeded before placement; final dots also exceed overlap limit. Registry incomplete; lane not supplied; official template and portal acceptance not authenticated.',
        'historical_record': 'evidence/k2/run_card.json: original conditional promotion is superseded, not authorization.'
    }


if __name__ == '__main__':
    print(json.dumps(review(), indent=2, allow_nan=False))

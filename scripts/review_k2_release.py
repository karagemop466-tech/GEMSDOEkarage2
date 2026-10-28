#!/usr/bin/env python3
"""Recheck K2's saved bytes and summarize archived evidence; never authorize upload.

The registry, footprint and holdout are historical receipts, not re-run here.
The reference sample is unavailable locally; its authenticity has not been shown.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
RASTER = ROOT / 'docs/downloads/gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif'
TARGETS = [ROOT / 'evidence/k2-review-2026-10-28.json', ROOT / 'docs/evidence/k2-review-2026-10-28.json']


def read_json(path):
    return json.loads((ROOT / path).read_text())


def review():
    prior = read_json('evidence/k2/run_card.json')
    hold = read_json('evidence/k2/combined_holdout.json')['scores']['hgbcont_b110']
    surface = read_json('evidence/k2/final_generation.json')['surface_registry_rows']['r13_lattice']
    audit = read_json('evidence/k2/final_registry_audit.json')
    strict = read_json('evidence/k2/validate_tif_strict.json')
    sha = hashlib.sha256(RASTER.read_bytes()).hexdigest()
    receipt_matches = (strict.get('candidate_sha256') == sha
                       and audit.get('candidate_file_sha256') == sha
                       and read_json('evidence/k2/final_generation.json').get('sha256') == sha)
    with rasterio.open(RASTER) as ds:
        values = ds.read(1)
        finite = bool(np.isfinite(values).all())
        in_range = bool(finite and values.min() >= 0 and values.max() <= 1)
        info = {'single_band': ds.count == 1, 'float32': ds.dtypes == ('float32',),
                'crs_epsg_32611': ds.crs is not None and ds.crs.to_epsg() == 32611,
                'shape_matches_recorded_mirror': (ds.height, ds.width) == (3730, 3292),
                'transform_matches_recorded_mirror': tuple(ds.transform)[:6] == (100, 0, 243350, 0, -100, 4508550),
                'all_cells_finite': finite, 'all_cells_in_0_1': in_range,
                'inside_footprint_no_nan': True if finite else None,
                'organizer_template_match': None,
                'outside_is_nan_per_historical_strict_validator': strict['checks']['outside_is_nan'] if receipt_matches else None,
                'historical_receipts_match_raster_sha': receipt_matches,
                'sha256_matches_prior_card': sha == prior['raster_sha256']}
    return {
        'schema': 'gems.parallel_run_card.v1',
        'session_date': '2026-10-28',
        'classification': 'REVIEW of archived evidence; no holdout or registry replay',
        'hypothesis': prior['hypothesis'], 'mechanism': prior['mechanism'],
        'named_non_fault_process': prior['named_non_fault_mimic'],
        'holdout': {'classification': 'HOLDOUT-DTI, prior run not independently replayed',
                    'evaluator_version': hold['evaluator_version'],
                    'withheld_positives': hold['withheld_positive_pixels'],
                    'dti': hold['dti'], 'confidence_interval_95': hold['ci95'],
                    'leaderboard_estimate': None},
        'correlation_overlap_vs_registry': {
            'surface_lattice_spearman': surface['spearman_full_footprint'],
            'surface_lattice_positive_support_within_3px': surface['literal_support_overlap_gt0'],
            'final_worst_overlap': audit['worst_dot_overlap'],
            'final_worst_overlap_reference': audit['worst_overlap_submission'],
            'final_duplicate_count': audit['duplicate_count'],
            'final_scan_complete': audit['complete_accessible_scan'],
            'caveat': 'Archived diagnostics; surface coverage is not the same complete registry as the final scan. Positive surface support is not a final dot set.'},
        'raster': str(RASTER.relative_to(ROOT)), 'raster_sha256': sha,
        'validator': info, 'submission_name': prior['submission_name'], 'note': prior['note'],
        'verdict': 'negative', 'ok_to_submit': False, 'weekly_slot_selected': False,
        'experiments_run_this_review': 0,
        'reasons': ['Pre-placement lattice support overlap exceeded the literal threshold; prior final placement should have stopped.',
                    'Historical receipt hashes must match the raster; an absent or mismatched receipt cannot clear any gate.',
                    'Final registry audit reports duplicates and incomplete accessible scan.',
                    'Strict historical exterior-NaN check failed; organizer acceptance and template authenticity are unknown.',
                    'No assigned lane or independently validated current incumbent comparison.'],
        'prior_card_notice': 'The prior conditional promotion and projected score are archived claims, not the present release decision.'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--write', action='store_true', help='update both checked-in copies')
    args = p.parse_args()
    result = review()
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if args.write:
        for target in TARGETS:
            target.write_text(text)
    else:
        for target in TARGETS:
            if not target.is_file() or target.read_text() != text:
                raise SystemExit(f'{target.relative_to(ROOT)} is missing or stale')
    print(text, end='')


if __name__ == '__main__':
    main()

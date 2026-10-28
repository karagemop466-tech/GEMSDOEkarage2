#!/usr/bin/env python3
"""Independent literal-policy release audit. Does not train, place dots or authorize slots.

Historical experimental cards are immutable provenance, not current clearance.
This audit deliberately includes calibration rows rather than changing registry scope.
"""
from pathlib import Path
import hashlib
import json
import math
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def registry_failures(audit):
    failures = []
    rows = audit.get('rows') if isinstance(audit, dict) else None
    if not isinstance(rows, list) or not rows:
        return [{'reason': 'missing registry measurements'}]
    for row in rows:
        if not isinstance(row, dict):
            failures.append({'reason': 'invalid registry measurement row'})
            continue
        reference = f"{row.get('repo')}/{row.get('submission')}"
        rho = row.get('spearman_full_footprint')
        overlap = row.get('my_dots_within_3px_of_theirs')
        valid = (not row.get('error') and
                 isinstance(rho, (int, float)) and not isinstance(rho, bool) and
                 math.isfinite(rho) and -1 <= rho <= 1 and
                 isinstance(overlap, (int, float)) and not isinstance(overlap, bool) and
                 math.isfinite(overlap) and 0 <= overlap <= 1)
        if not valid:
            failures.append({'reference': reference, 'reason': 'missing or incomparable measurement'})
        elif rho > .90 or overlap > .70:
            failures.append({'reference': reference, 'reason': 'literal duplicate gate',
                             'rank_correlation': rho, 'overlap_3px': overlap})
    return failures


def audit(root=ROOT):
    import numpy as np
    import rasterio
    card_path = root / 'evidence/k2/run_card.json'
    card = json.loads(card_path.read_text())
    tif = root / card['raster']
    digest = hashlib.sha256(tif.read_bytes()).hexdigest()
    with rasterio.open(tif) as ds:
        values = ds.read(1)
        saved_positive_pixels = int(np.count_nonzero(np.isfinite(values) & (values > 0)))
        checks = dict(single_band=ds.count == 1, float32=ds.dtypes == ('float32',),
                      finite_everywhere=bool(np.isfinite(values).all()),
                      range_0_1=bool(np.isfinite(values).all() and values.min() >= 0 and values.max() <= 1),
                      mirror_shape_match=(ds.height, ds.width) == (3730, 3292),
                      mirror_crs_match=ds.crs.to_epsg() == 32611 if ds.crs else False,
                      mirror_transform_match=tuple(ds.transform)[:6] == (100., 0., 243350., 0., -100., 4508550.),
                      sha256_match=digest == card['raster_sha256'])
    with zipfile.ZipFile(tif.with_suffix('.zip')) as archive:
        checks['zip_roundtrip'] = (archive.namelist() == [tif.name] and
                                   hashlib.sha256(archive.read(tif.name)).hexdigest() == digest)
    saved_registry = json.loads((root / 'evidence/k2/final_registry_audit.json').read_text())
    generation = json.loads((root / 'evidence/k2/final_generation.json').read_text())
    surface_witness = generation['surface_registry_rows']['r13_lattice']
    failures = registry_failures(saved_registry)
    if (saved_registry.get('candidate_file_sha256') != digest or
            saved_registry.get('my_dots') != saved_positive_pixels or
            generation.get('sha256') != digest or generation.get('dots') != saved_positive_pixels):
        failures.append({'reason': 'Saved registry/generation receipts not bound to current TIFF bytes/dot count'})
    witness = json.loads((root / 'evidence/geometry-audit.json').read_text())['witness']
    uncovered = witness['uncovered_footprint_pixels']
    # A counting lower bound, conditional on the prior evidence that all K2
    # positives are inside this owner-mirrored footprint. Not a score, and
    # *not* a claim that every small in-footprint raster must fail.
    matches_floor = max(0, saved_positive_pixels - uncovered)
    bound = {'evidence_class': 'GEOMETRY LOWER BOUND, NOT A SCORE',
             'saved_positive_pixels': saved_positive_pixels,
             'mirrored_uncovered_footprint_pixels': uncovered,
             'minimum_matches_if_all_dots_in_mirror_footprint': matches_floor,
             'minimum_overlap_if_all_dots_in_mirror_footprint': matches_floor / saved_positive_pixels if saved_positive_pixels else None,
             'first_dot_budget_guaranteed_to_exceed_70_percent': witness['first_dot_budget_guaranteed_to_exceed_70_percent'],
             'scope': 'Conditional on owner-mirror footprint and saved prior zero-exterior receipt; smaller budgets not universally blocked.'}
    # Use numeric prior receipts, not the original card's inaccurate blanket
    # "every in-footprint candidate" statement and unqualified uniqueness prose.
    prior_comparisons = {
        'surface_before_placement': {
            'source': 'evidence/k2/final_generation.json (prior recorded measurement; not rerun)',
            'vs_r13_lattice_spearman_full_footprint': surface_witness['spearman_full_footprint'],
            'vs_r13_lattice_support_overlap_within_3px': surface_witness['literal_support_overlap_gt0'],
            'duplicate_stop': surface_witness['literal_support_overlap_gt0'] > .70},
        'final_dots': {
            'source': 'evidence/k2/final_registry_audit.json (prior recorded measurement; not rerun)',
            'rasters_expected': saved_registry['registry_rasters_expected'],
            'rasters_checked': saved_registry['registry_rasters_checked'],
            'complete_accessible_scan': saved_registry['complete_accessible_scan'],
            'worst_overlap_3px': saved_registry['worst_dot_overlap'],
            'duplicate_count': saved_registry['duplicate_count'],
            'unique_under_literal_gate': saved_registry['unique']},
    }
    return dict(schema='gems.literal_release_audit.v1', evidence_class='RELEASE-AUDIT, NOT A SCORE',
                source_run_card=str(card_path.relative_to(root)), raster_sha256=digest,
                hypothesis=card['hypothesis'], mechanism=card['mechanism'],
                named_non_fault_mimic=card['named_non_fault_mimic'],
                submission_name=card['submission_name'], submission_note=card['note'],
                correlation_overlap_vs_registry=prior_comparisons,
                geometry_lower_bound=bound,
                measurement_status='Saved bytes and conditional geometry bound rechecked; registry measurements and holdout inherited, not rerun.',
                validator=checks, organizer_template_authenticated=False,
                footprint_rechecked=False, holdout=card['holdout'],
                holdout_status='Prior recorded HOLDOUT-DTI; not rerun by this audit',
                registry_failures=failures,
                reasons=['Literal all-registry uniqueness failed; no scope exemption is authorized.',
                         'Assigned lane absent; prior experiments used a self-assigned lane.',
                         'Organizer inputs, exterior convention, quota and receipt are unverified.',
                         'Primitive comparison is not a frozen same-fold historical champion comparison.'],
                experiments_run=0, submission_slots_used=0, slot_authorized=False,
                leaderboard_estimate=None, verdict='negative',
                download_policy='Research download only. DO NOT SUBMIT under the current protocol.')


if __name__ == '__main__':
    result = audit()
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    for path in ('evidence/k2/literal_release_audit.json', 'docs/evidence/k2/literal_release_audit.json'):
        (ROOT / path).write_text(text)
    print(text)

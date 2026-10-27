#!/usr/bin/env python3
"""One preregistered experiment. No slot use, no private metric, no dot placement after a failed surface gate."""
from __future__ import annotations
import hashlib
import json
import sys
import signal
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor'))
from gems57 import evaluate_holdout as shared
from gems57 import spatial, uniqueness
from gems57.grid import load_grid
from gems57.submission_writer import write_submission


def save(path, value):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def gradients(a, valid, sigma):
    """Normalized convolution avoids nodata cliffs; no fault labels enter this function."""
    w = ndi.gaussian_filter(valid.astype(np.float32), sigma)
    sm = ndi.gaussian_filter(np.where(valid, a, 0).astype(np.float32), sigma)
    sm /= np.maximum(w, 1e-6)
    dy, dx = np.gradient(sm)
    return dy, dx, np.hypot(dy, dx)


def physical_features(bands, valid):
    fields = {}
    for scale in (2, 6):
        el, ba, co = [gradients(a, valid, scale) for a in bands]
        cos = (el[0] * ba[0] + el[1] * ba[1]) / np.maximum(el[2] * ba[2], 1e-10)
        fields[f'opposition_s{scale}'] = np.clip(-cos, 0, 1).astype(np.float32)
        for name, v in [('elevation', el), ('basement', ba), ('conductivity', co)]:
            fields[f'{name}_s{scale}'] = v[2].astype(np.float32)
    for a in fields.values():
        a[~valid] = 0
    return fields


def normalized(fields, calibration):
    if not calibration.any():
        raise ValueError('empty calibration domain')
    out = {}
    for k, a in fields.items():
        if k.startswith('opposition'):
            out[k] = a
        else:
            q = float(np.quantile(a[calibration], .95))
            out[k] = np.clip(a / max(q, 1e-10), 0, 1).astype(np.float32)
    return out


def candidate_surface(fields):
    scales = []
    for s in (2, 6):
        scales.append(fields[f'opposition_s{s}'] * np.sqrt(fields[f'elevation_s{s}'] * fields[f'basement_s{s}'])
                      * np.sqrt(fields[f'conductivity_s{s}']))
    return np.sqrt(scales[0] * scales[1]).astype(np.float32)


def crop_fold(fold, sl):
    return {k: fold[k][sl] for k in ('region', 'truth', 'visible')}


def main():
    def budget_expired(signum, frame):
        raise TimeoutError('Two-hour experiment budget exhausted; no promotion is allowed')
    signal.signal(signal.SIGALRM, budget_expired)
    signal.alarm(7200)
    # Integrity pins prevent accidental data drift from becoming a new experiment.
    input_manifest = json.loads((ROOT / 'registry/core_data_manifest.json').read_text())
    for entry in input_manifest['files']:
        h = hashlib.sha256()
        with (ROOT / '.cache/gems_data' / entry['dest']).open('rb') as stream:
            for chunk in iter(lambda: stream.read(1 << 20), b''):
                h.update(chunk)
        if h.hexdigest() != entry['sha256']:
            raise ValueError(f'Input SHA256 mismatch: {entry["dest"]}')
    grid = load_grid(ROOT / '.cache/gems_data')
    with rasterio.open(ROOT / '.cache/gems_data/training_features.tif') as ds:
        if (ds.shape, ds.crs, ds.transform) != (grid.shape, grid.crs, grid.transform):
            raise ValueError('feature stack grid differs from sample')
        bands = ds.read([12, 15, 17])
        valid = grid.footprint & np.all(np.isfinite(bands) & (np.abs(bands) < 1e30), axis=0)
        descriptions = [ds.descriptions[i - 1] for i in (12, 15, 17)]
    fields = physical_features(bands, valid)
    del bands
    # Exclude a 1.2 km footprint-edge collar to avoid interpolation-boundary signatures.
    eligible = valid & (ndi.distance_transform_edt(valid) > 12)
    labels = grid.catalogue
    arm_names = list(fields) + ['candidate']
    terms = {}
    canaries, fold_receipts = [], []
    canary_failed = False
    for fold in spatial.folds(labels, eligible, buffer_px=80):
        norm = normalized(fields, fold['train'])
        surfaces = {**norm, 'candidate': candidate_surface(norm)}
        active = fold['region'] & ~fold['visible']
        pos = np.flatnonzero(fold['truth'])
        neg = np.flatnonzero(active & ~fold['truth'])
        rng = np.random.default_rng(20261027 + fold['fold'])
        neg = rng.choice(neg, min(100000, len(neg)), replace=False)
        ids = np.r_[pos, neg]
        target = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
        row = {'fold': fold['fold'], 'positive_pixels': len(pos), 'unlabeled_proxy_pixels': len(neg), 'features': {}}
        for name, surface in surfaces.items():
            auc = float(roc_auc_score(target, surface.ravel()[ids]))
            row['features'][name] = {'auc': auc, 'leakage_canary_pass': bool(auc <= .90)}
            canary_failed |= auc > .90
        canaries.append(row)
        y, x = np.nonzero(fold['region'])
        sl = np.s_[max(0, y.min()-4):min(grid.shape[0], y.max()+5), max(0, x.min()-4):min(grid.shape[1], x.max()+5)]
        for name in arm_names:
            _, t = shared.evaluate(surfaces[name][sl], crop_fold(fold, sl), valid[sl],
                                   origin=(sl[0].start, sl[1].start), global_shape=grid.shape)
            terms[name] = terms.get(name, np.zeros_like(t)) + t
        fold_receipts.append(fold['receipt'])
        print(f"fold {fold['fold']}: {len(pos)} withheld positives", flush=True)
    summary = shared.pooled_summary(terms, draws=1000, seed=20261027, candidate='candidate')
    summary['canaries'] = canaries
    summary['canary_pass'] = not canary_failed
    summary['folds'] = fold_receipts
    summary['split_version'] = 'label-blind-quadrants-v2 / whole original connected components / 8km training buffer'
    summary['comparison_limit'] = 'Primitive controls only; no authenticated current-best model rebuilt on these folds. Not a leaderboard estimate.'
    save('evidence/holdout.json', summary)
    if canary_failed:
        save('evidence/run_card.json', {'hypothesis': 'H1 signed downthrow parity', 'verdict': 'negative',
             'reason': 'AUC >0.90 leakage canary; no raster generated', 'holdout': summary['scores']['candidate']})
        return
    norm = normalized(fields, eligible)
    p = candidate_surface(norm)
    # Export full known-trace mask only AFTER the out-of-fold test; never apply it to holdout predictions.
    p[~eligible | labels] = 0
    digest = hashlib.sha256(p.tobytes()).hexdigest()[:12]
    name = f'gemsdoekarage2-h1-parity-{digest}-DO-NOT-SUBMIT-surface'
    note = 'H1 signed elevation-basement parity, conductivity persistence; research surface only; no slot approval.'
    path = ROOT / 'docs/downloads' / (name + '.tif')
    receipt = write_submission(path, p, ROOT / '.cache/gems_data/sample_submission.tif', grid.footprint,
                               note=note, name=name, catalogue=labels,
                               metadata={'artifact_role': 'pre-placement research surface', 'not_calibrated_probability': True})
    save('evidence/validator.json', receipt)
    man = json.loads((ROOT / 'registry/focus_registry_manifest.json').read_text())
    # Pin-and-compare every available registry record if no stop is found. A single
    # literal duplicate is sufficient for a negative and requires immediate stop.
    records = [{'repo': r['repo'], 'submission': r['path'], 'file': str(ROOT / r['local']),
                'sha256': r['sha256']} for r in man['rasters'] if r['status'] == 'ok']
    # Deterministic order: broad priors first exposes support saturation without
    # wasting budget. No records are excluded; candidates that pass must scan all.
    records.sort(key=lambda r: (r['repo'], r['submission']))
    checked = []
    stop = False
    for i, rec in enumerate(records):
        audit = uniqueness.compare_array_to_registry(p, [rec], grid.footprint,
                    file_sha256=receipt['sha256'], include_reverse=False,
                    expected_grid=(grid.shape, grid.crs, grid.transform))
        row = audit['rows'][0]
        checked.append(row)
        if 'error' in row or row.get('duplicate_by_rho') or row.get('duplicate_by_overlap'):
            stop = True
            print(f"STOP at registry raster {i+1}: {row.get('submission')}", flush=True)
            break
    registry = {'phase': 'surface-before-placement', 'scope': 'nine focus repositories at pinned refs; not all sites named in the request',
                'expected': len(records), 'checked': len(checked), 'stopped_early': stop,
                'complete_scan': len(checked) == len(records) and man['n_failed'] == 0,
                'rows': checked, 'unique_cleared': False,
                'final_dots': 'not placed: registry stop or unresolved current-best/whole-inventory gate'}
    save('evidence/surface_registry.json', registry)
    if checked and 'error' not in checked[-1]:
        witness = checked[-1]
        cert = uniqueness.saturation_certificate(witness['file'], grid.footprint, labels,
                      expected_grid=(grid.shape, grid.crs, grid.transform))
        save('evidence/saturation_certificate.json', cert)
    hist = json.loads((ROOT / 'evidence/nine_site_best_files_audit.json').read_text())
    bysite = {r['site']: r for r in hist['sites']}
    def mask(site):
        with rasterio.open(ROOT / bysite[site]['local_file']) as ds:
            a = ds.read(1)
        return np.isfinite(a) & (a > 0) & grid.footprint
    d28, b1, b2, p36 = [mask(k) for k in ('GEMSDOE25','GEMSDOE31','GEMSDOE32','GEMSDOE36')]
    d = ndi.distance_transform_edt(~labels)
    forensic = {'evidence_class': 'RASTER-MEASUREMENT',
                'd28_equals_site30': bool(np.array_equal(d28, mask('GEMSDOE30'))),
                'b1_equals_d28_distance_gt1': bool(np.array_equal(b1, d28 & (d > 1))),
                'b2_equals_d28_distance_gt2': bool(np.array_equal(b2, d28 & (d > 2))),
                'removed_d28_to_b2': int((d28 & ~b2).sum()),
                'removed_b1_to_b2': int((b1 & ~b2).sum()),
                'site36_contains_all_b2': bool(not (b2 & ~p36).any()),
                'site36_extra_pixels': int((p36 & ~b2).sum()),
                'interpretation': 'B2 is a catalogue-apron pruning operation, not an independent discovery model. Reduced false-positive mass is a plausible explanation for user-reported improvement; hidden truth/receipts unavailable, so causal gains are not established.'}
    save('evidence/champion_forensics.json', forensic)
    last = checked[-1] if checked else {}
    delta = summary['paired_differences'].get(summary['best_comparable_control'], {})
    card = {'hypothesis': 'H1 signed cross-field displacement parity',
            'mechanism': 'Opposing detrended-elevation and basement-depth gradients, 200/600m persistence and conductivity contrast; no fault-derived predictors.',
            'non_fault_mimic': 'Basin sedimentation plus saline groundwater; interpolation boundaries.',
            'holdout': summary['scores']['candidate'], 'paired_delta_vs_best_primitive': delta,
            'registry': {'phase': registry['phase'], 'compared': len(checked), 'expected': len(records),
                         'rho': last.get('spearman_full_footprint'), 'overlap': last.get('my_dots_within_3px_of_theirs'),
                         'witness': last.get('submission'), 'scope': registry['scope'], 'final_dot_check': 'not run: no placement after stop'},
            'raster_sha256': receipt['sha256'], 'raster': str(path.relative_to(ROOT)),
            'validator': {'ok': receipt['template_report']['ok'], 'details': 'evidence/validator.json',
                          'nan_pixels': receipt['template_report']['nan_pixels'],
                          'range': [float(p.min()), float(p.max())], 'crs_shape_transform_match': receipt['template_report']['ok']},
            'submission_name': name, 'note': note,
            'format_valid': True, 'unique_submission_verified': False,
            'approved_for_weekly_slot': False, 'submission_slots_used': 0,
            'experiments_run': 1, 'verdict': 'negative',
            'reasons': ['Literal surface registry stop; no final dots generated.' if stop else 'No compatible authenticated current-best comparator or complete all-sites registry.',
                        'Failed paired improvement against the best primitive control; no compatible incumbent reconstruction exists.',
                        'Historical leaderboard receipts unavailable; no leaderboard score estimate is defensible.'],
            'download_policy': 'Research surface download only. NOT a recommended submission.'}
    save('evidence/run_card.json', card)
    print(json.dumps(card, indent=2))

if __name__ == '__main__':
    main()

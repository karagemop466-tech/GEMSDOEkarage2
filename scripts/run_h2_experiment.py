#!/usr/bin/env python3
"""H2 experiment: dilational stepover / relay ramp detector.

No slot use, no private metric, no dot placement after a failed gate.
Reuses shared gems57 tools unchanged: evaluate_holdout, uniqueness, grid,
submission_writer.

Signature: gravity low (sedimentary basin/stepover trap) x conductivity high
(hydrothermal alteration) x magnetic edge (buried contact) x topographic
gradient reversal at stepover jogs. Differs from H1's linear signed
displacement parity across two scales.
"""
from __future__ import annotations

import hashlib
import json
import signal
import sys
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
    """Normalized convolution avoids nodata cliffs."""
    w = ndi.gaussian_filter(valid.astype(np.float32), sigma)
    sm = ndi.gaussian_filter(np.where(valid, a, 0).astype(np.float32), sigma)
    sm /= np.maximum(w, 1e-6)
    dy, dx = np.gradient(sm)
    return dy, dx, np.hypot(dy, dx)


def h2_fields(bands, valid):
    """Compute H2 physical fields at scales 2 and 6 px.

    Bands order: iso_grav_anom(12), det_elev(11), cond_surf(16), tmi_hg(2).
    """
    g_ig, g_de, g_cs, g_tm = bands
    fields = {}

    for scale in (2, 6):
        # Gravity field (raw, for inversion later)
        fields[f'ig_raw_s{scale}'] = ndi.gaussian_filter(
            np.where(valid, g_ig, 0).astype(np.float32), sigma=scale) / np.maximum(
            ndi.gaussian_filter(valid.astype(np.float32), sigma=scale), 1e-6).astype(np.float32)

        # Detrended elevation gradient magnitude
        _, _, de_m = gradients(g_de, valid, scale)
        fields[f'de_grad_s{scale}'] = de_m.astype(np.float32)

        # Conductivity gradient magnitude (alteration edge)
        _, _, cs_m = gradients(g_cs, valid, scale)
        fields[f'cs_grad_s{scale}'] = cs_m.astype(np.float32)

        # Magnetic horizontal gradient magnitude (buried contact edge)
        _, _, tm_m = gradients(g_tm, valid, scale)
        fields[f'tm_hg_s{scale}'] = tm_m.astype(np.float32)

    # Scale contrast for detrended elevation (stepover jog: small-scale vs large-scale)
    _, _, de2 = gradients(g_de, valid, 2)
    _, _, de6 = gradients(g_de, valid, 6)
    fields['de_scale_contrast'] = np.clip(
        np.abs(de2 - de6) / np.maximum(np.abs(de2 - de6).max(), 1e-10), 0, 1).astype(np.float32)

    # Gravity low indicator: inverted normalized gravity (low gravity = basin)
    ig2 = fields['ig_raw_s2']
    fields['ig_low'] = np.clip(1.0 - (ig2 - ig2.min()) / np.maximum(ig2.max() - ig2.min(), 1e-10), 0, 1).astype(np.float32)

    for a in fields.values():
        a[~valid] = 0
    return fields


def normalize(fields, calibration):
    out = {}
    for k, a in fields.items():
        if k == 'ig_low':
            out[k] = a  # already [0,1]
            continue
        if not calibration.any():
            raise ValueError('empty calibration domain')
        q = float(np.quantile(a[calibration], 0.95))
        out[k] = np.clip(a / max(q, 1e-10), 0, 1).astype(np.float32)
    return out


def h2_surface(norm_fields):
    """Combine H2 fields multiplicatively into candidate probability surface."""
    scales = []
    for s in (2, 6):
        scales.append(
            norm_fields['ig_low']
            * norm_fields[f'cs_grad_s{s}']
            * norm_fields[f'tm_hg_s{s}']
            * np.sqrt(norm_fields[f'de_grad_s{s}'] * norm_fields['de_scale_contrast'])
        )
    surf = np.sqrt(scales[0] * scales[1]).astype(np.float32)
    return surf


def crop_fold(fold, sl):
    return {k: fold[k][sl] for k in ('region', 'truth', 'visible')}


def main():
    raise RuntimeError("BLOCKED: historical H2 is closed; no assigned lane, complete registry or new experiment budget. No TIFF generated.")

    def budget_expired(signum, frame):
        raise TimeoutError('Two-hour experiment budget exhausted; no promotion is allowed')
    signal.signal(signal.SIGALRM, budget_expired)
    signal.alarm(7200)

    # Integrity pins
    input_manifest = json.loads((ROOT / 'registry/core_data_manifest.json').read_text())
    for entry in input_manifest['files']:
        h = hashlib.sha256()
        with (ROOT / 'data' / entry['dest']).open('rb') as stream:
            for chunk in iter(lambda: stream.read(1 << 20), b''):
                h.update(chunk)
        if h.hexdigest() != entry['sha256']:
            raise ValueError(f'Input SHA256 mismatch: {entry["dest"]}')

    grid = load_grid(ROOT / 'data')
    with rasterio.open(ROOT / 'data/training_features.tif') as ds:
        if (ds.shape, ds.crs, ds.transform) != (grid.shape, grid.crs, grid.transform):
            raise ValueError('feature stack grid differs from sample')
        bands = ds.read([12, 11, 16, 2])
        valid = grid.footprint & np.all(np.isfinite(bands) & (np.abs(bands) < 1e30), axis=0)
        descriptions = [ds.descriptions[i - 1] for i in (12, 11, 16, 2)]

    fields = h2_fields(bands, valid)
    del bands

    # Exclude 1.2 km footprint-edge collar
    eligible = valid & (ndi.distance_transform_edt(valid) > 12)
    labels = grid.catalogue

    arm_names = list(fields.keys()) + ['candidate']
    terms = {}
    canaries, fold_receipts = [], []
    canary_failed = False

    for fold in spatial.folds(labels, eligible, buffer_px=80):
        norm = normalize(fields, fold['train'])
        surfaces = {**norm, 'candidate': h2_surface(norm)}
        active = fold['region'] & ~fold['visible']
        pos = np.flatnonzero(fold['truth'])
        neg = np.flatnonzero(active & ~fold['truth'])
        rng = np.random.default_rng(20261028 + fold['fold'])
        neg = rng.choice(neg, min(100000, len(neg)), replace=False)
        ids = np.r_[pos, neg]
        target = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
        row = {'fold': fold['fold'], 'positive_pixels': len(pos),
               'unlabeled_proxy_pixels': len(neg), 'features': {}}
        for name, surface in surfaces.items():
            auc = float(roc_auc_score(target, surface.ravel()[ids]))
            row['features'][name] = {'auc': auc, 'leakage_canary_pass': bool(auc <= 0.90)}
            canary_failed |= auc > 0.90
        canaries.append(row)
        y, x = np.nonzero(fold['region'])
        sl = np.s_[max(0, y.min()-4):min(grid.shape[0], y.max()+5),
                   max(0, x.min()-4):min(grid.shape[1], x.max()+5)]
        for name in arm_names:
            _, t = shared.evaluate(surfaces[name][sl], crop_fold(fold, sl), valid[sl],
                                   origin=(sl[0].start, sl[1].start), global_shape=grid.shape)
            terms[name] = terms.get(name, np.zeros_like(t)) + t
        fold_receipts.append(fold['receipt'])
        print(f"fold {fold['fold']}: {len(pos)} withheld positives", flush=True)

    summary = shared.pooled_summary(terms, draws=1000, seed=20261028, candidate='candidate')
    summary['canaries'] = canaries
    summary['canary_pass'] = not canary_failed
    summary['folds'] = fold_receipts
    summary['split_version'] = 'label-blind-quadrants-v2 / whole original connected components / 8km training buffer'
    save('evidence/holdout_h2.json', summary)

    if canary_failed:
        save('evidence/run_card_h2.json', {
            'hypothesis': 'H2 dilational stepover / relay ramp detector',
            'verdict': 'negative',
            'reason': 'AUC >0.90 leakage canary; no raster generated',
            'holdout': summary['scores']['candidate'],
        })
        print('NEGATIVE: leakage canary failed')
        return

    # Build final candidate surface on eligible domain, mask known faults
    norm = normalize(fields, eligible)
    p = h2_surface(norm)
    p[~eligible | labels] = 0

    # Threshold to sparse dots: keep only top N pixels (like dotted submissions)
    n_dots = 37654  # match GEMSDOE32's budget for comparability
    flat = p.ravel()
    threshold = np.partition(flat, -n_dots)[-n_dots]
    p = np.where(p >= threshold, p, 0).astype(np.float32)
    p[~eligible | labels] = 0

    digest = hashlib.sha256(p.tobytes()).hexdigest()[:12]
    name = f'gemsdoekarage2-h2-stepover-{digest}'
    note = 'H2 dilational stepover/relay ramp detector; gravity low x conductivity high x magnetic edge; research surface.'
    path = ROOT / 'docs/downloads' / (name + '.tif')

    # Format validation first
    receipt = write_submission(path, p, ROOT / 'data/sample_submission.tif', grid.footprint,
                               note=note, name=name, catalogue=labels,
                               metadata={'artifact_role': 'pre-placement research surface', 'not_calibrated_probability': True})
    save('evidence/validator_h2.json', receipt)

    # Registry uniqueness gate (surface phase)
    man = json.loads((ROOT / 'registry/focus_registry_manifest.json').read_text())
    records = [{'repo': r['repo'], 'submission': r['path'], 'file': str(ROOT / r['local']),
                'sha256': r['sha256']} for r in man['rasters'] if r['status'] == 'ok']
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

    registry = {'phase': 'surface-before-placement',
                'scope': 'nine focus repositories at pinned refs; not all sites named in the request',
                'expected': len(records), 'checked': len(checked), 'stopped_early': stop,
                'complete_scan': len(checked) == len(records) and man['n_failed'] == 0,
                'rows': checked, 'unique_cleared': False,
                'final_dots': 'not placed: registry stop or unresolved gate'}
    save('evidence/surface_registry_h2.json', registry)

    if checked and 'error' not in checked[-1]:
        witness = checked[-1]
        cert = uniqueness.saturation_certificate(witness['file'], grid.footprint, labels,
                      expected_grid=(grid.shape, grid.crs, grid.transform))
        save('evidence/saturation_certificate_h2.json', cert)

    # Run card
    last = checked[-1] if checked else {}
    delta = summary['paired_differences'].get(summary['best_comparable_control'], {})
    card = {
        'hypothesis': 'H2 dilational stepover / relay ramp detector',
        'mechanism': 'Gravity low (basin/stepover trap) x conductivity high (hydrothermal alteration) x magnetic edge (buried contact) x topographic gradient reversal at stepover jogs; no catalogue-derived predictor.',
        'non_fault_mimic': 'Sedimentary basin fill, saline groundwater, lithologic contacts, interpolation boundaries.',
        'holdout': summary['scores']['candidate'],
        'paired_delta_vs_best_primitive': delta,
        'registry': {
            'phase': registry['phase'], 'compared': len(checked), 'expected': len(records),
            'rho': last.get('spearman_full_footprint'), 'overlap': last.get('my_dots_within_3px_of_theirs'),
            'witness': last.get('submission'), 'scope': registry['scope'], 'final_dot_check': 'not run: no placement after stop',
        },
        'raster_sha256': receipt['sha256'],
        'raster': str(path.relative_to(ROOT)),
        'validator': {'ok': receipt['template_report']['ok'], 'details': 'evidence/validator_h2.json',
                      'nan_pixels': receipt['template_report']['nan_pixels'],
                      'range': [float(p.min()), float(p.max())],
                      'crs_shape_transform_match': receipt['template_report']['ok']},
        'submission_name': name, 'note': note,
        'format_valid': True, 'unique_submission_verified': False,
        'approved_for_weekly_slot': False, 'submission_slots_used': 0,
        'experiments_run': 1,
        'verdict': 'negative',
        'reasons': ['Literal surface registry stop; no final dots generated.' if stop else 'No compatible authenticated current-best comparator or complete all-sites registry.',
                    'No paired improvement established against the best primitive control.',
                    'Historical leaderboard receipts unavailable; no leaderboard score estimate is defensible.'],
        'download_policy': 'Research surface download only. NOT a recommended submission.',
    }
    save('evidence/run_card_h2.json', card)
    print(json.dumps(card, indent=2))


if __name__ == '__main__':
    main()
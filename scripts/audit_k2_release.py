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
    rows = audit.get('rows')
    if not isinstance(rows, list) or not rows:
        return [{'reason': 'missing registry measurements'}]
    for row in rows:
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
    failures = registry_failures(json.loads((root / 'evidence/k2/final_registry_audit.json').read_text()))
    return dict(schema='gems.literal_release_audit.v1', evidence_class='RELEASE-AUDIT, NOT A SCORE',
                source_run_card=str(card_path.relative_to(root)), raster_sha256=digest,
                hypothesis=card['hypothesis'], mechanism=card['mechanism'],
                named_non_fault_mimic=card['named_non_fault_mimic'],
                submission_name=card['submission_name'], submission_note=card['note'],
                correlation_overlap_vs_registry=card['correlation_overlap_vs_registry'],
                measurement_status='Saved bytes rechecked; registry measurements and holdout inherited, not rerun.',
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

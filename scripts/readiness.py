"""Fail-closed selector gate. Evidence must be produced by shared tools, not this gate."""
import math


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def sha256_hex(value):
    return (isinstance(value, str) and len(value) == 64
            and all(c in '0123456789abcdef' for c in value))


def assess(card):
    """Return fail-closed eligibility; malformed evidence never authorizes promotion."""
    if not isinstance(card, dict):
        return {'verdict': 'negative', 'reasons': ['Evidence card must be a JSON object'],
                'slot_authorized': False}

    reasons = []
    if (not isinstance(card.get('lane'), str) or not card.get('lane')
            or not isinstance(card.get('template_commit'), str) or not card.get('template_commit')):
        reasons.append('Missing method lane or shared template pin')

    h = card.get('holdout')
    if not isinstance(h, dict):
        h = {}
    ci = h.get('ci95')
    valid_ci = isinstance(ci, (list, tuple)) and len(ci) == 2
    dti = h.get('dti')
    if (not isinstance(h.get('evaluator_version'), str) or not h.get('evaluator_version')
            or not isinstance(h.get('withheld_positives'), int)
            or isinstance(h.get('withheld_positives'), bool) or h.get('withheld_positives', 0) <= 0
            or not finite(dti) or not 0 <= dti <= 1
            or not valid_ci or not all(finite(x) for x in ci)
            or not (0 <= ci[0] <= dti <= ci[1] <= 1)):
        reasons.append('Missing or invalid HOLDOUT-DTI evidence')

    baseline = card.get('baseline_holdout_dti')
    if (not finite(baseline) or not 0 <= baseline <= 1 or not finite(dti)
            or dti <= baseline):
        reasons.append('Has not beaten comparable current holdout best')
    if card.get('hide_recover_protocol_verified') is not True:
        reasons.append('Buffered whole-segment hide-and-recover not verified')

    canaries = card.get('feature_auc')
    if (not isinstance(canaries, dict) or not canaries
            or any(not finite(x) or not 0 <= x <= .90 for x in canaries.values())):
        reasons.append('Feature leakage canary missing or failed')

    registry = card.get('registry')
    if not isinstance(registry, dict):
        registry = {}
    if (registry.get('coverage_complete') is not True
            or not sha256_hex(registry.get('snapshot_sha256'))):
        reasons.append('Registry coverage incomplete or snapshot hash invalid')
    for stage in ('surface', 'final_dots'):
        rows = registry.get(stage)
        if not isinstance(rows, list) or not rows:
            reasons.append(f'{stage}: no registry measurements')
            continue
        for row in rows:
            if not isinstance(row, dict):
                reasons.append(f'{stage}: invalid measurement')
                continue
            rho, overlap = row.get('rank_correlation'), row.get('overlap_3px')
            if (not isinstance(row.get('reference'), str) or not row.get('reference')
                    or not finite(rho) or not -1 <= rho <= 1
                    or not finite(overlap) or not 0 <= overlap <= 1):
                reasons.append(f'{stage}: invalid measurement')
            elif rho > .90 or overlap > .70:
                reasons.append(f'{stage}: duplicate lane; stop')

    validator = card.get('validator')
    if not isinstance(validator, dict):
        validator = {}
    checks = ('single_band', 'finite_inside', 'range_0_1', 'crs_match', 'shape_match', 'transform_match')
    if any(validator.get(k) is not True for k in checks):
        reasons.append('Raster validation missing or failed')

    sha = card.get('raster_sha256', '')
    if not sha256_hex(sha):
        reasons.append('Raster SHA256 missing or invalid')
    name, note = card.get('submission_name'), card.get('submission_note')
    if not isinstance(name, str) or not name or not isinstance(note, str) or not note or len(note) > 140:
        reasons.append('Submission name/note invalid')
    return {'verdict': 'negative' if reasons else 'promote', 'reasons': reasons,
            'slot_authorized': False}  # Separate selector always required.

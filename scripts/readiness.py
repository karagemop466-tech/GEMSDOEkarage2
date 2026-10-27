"""Fail-closed selector gate. Evidence must be produced by shared tools, not this gate."""
import math


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def assess(card):
    reasons = []
    if not card.get('lane') or not card.get('template_commit'):
        reasons.append('Missing method lane or shared template pin')
    h = card.get('holdout', {})
    ci = h.get('ci95', [])
    if (not h.get('evaluator_version') or not isinstance(h.get('withheld_positives'), int)
            or h.get('withheld_positives', 0) <= 0 or not finite(h.get('dti'))
            or not 0 <= h.get('dti', -1) <= 1
            or len(ci) != 2 or not all(finite(x) for x in ci)
            or not (0 <= ci[0] <= h.get('dti', -1) <= ci[1] <= 1)):
        reasons.append('Missing or invalid HOLDOUT-DTI evidence')
    if not finite(card.get('baseline_holdout_dti')) or not finite(h.get('dti')) or h.get('dti', -1) <= card.get('baseline_holdout_dti', 1):
        reasons.append('Has not beaten comparable current holdout best')
    if card.get('hide_recover_protocol_verified') is not True:
        reasons.append('Buffered whole-segment hide-and-recover not verified')
    canaries = card.get('feature_auc', {})
    if not canaries or any(not finite(x) or not 0 <= x <= .90 for x in canaries.values()):
        reasons.append('Feature leakage canary missing or failed')
    registry = card.get('registry', {})
    if registry.get('coverage_complete') is not True or not registry.get('snapshot_sha256'):
        reasons.append('Registry coverage incomplete')
    for stage in ('surface', 'final_dots'):
        rows = registry.get(stage, [])
        if not rows:
            reasons.append(f'{stage}: no registry measurements')
        for row in rows:
            rho, overlap = row.get('rank_correlation'), row.get('overlap_3px')
            if not row.get('reference') or not finite(rho) or not -1 <= rho <= 1 or not finite(overlap) or not 0 <= overlap <= 1:
                reasons.append(f'{stage}: invalid measurement')
            elif rho > .90 or overlap > .70:
                reasons.append(f'{stage}: duplicate lane; stop')
    checks = ('single_band', 'finite_inside', 'range_0_1', 'crs_match', 'shape_match', 'transform_match')
    if any(card.get('validator', {}).get(k) is not True for k in checks):
        reasons.append('Raster validation missing or failed')
    sha = card.get('raster_sha256', '')
    if len(sha) != 64 or any(c not in '0123456789abcdef' for c in sha):
        reasons.append('Raster SHA256 missing or invalid')
    if not card.get('submission_name') or not card.get('submission_note') or len(card.get('submission_note', '')) > 140:
        reasons.append('Submission name/note invalid')
    return {'verdict': 'negative' if reasons else 'promote', 'reasons': reasons,
            'slot_authorized': False}  # Separate selector always required.

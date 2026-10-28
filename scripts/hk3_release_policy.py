"""Fail-closed publication policy; no waiver of the user's registry stop."""
import re

REQUIRED_GATES = (
    'format_shared_validator_pass', 'grid_matches_example_submission',
    'whole_array_finite_in_0_1', 'no_dots_on_mapped_catalogue',
    'leakage_canary_pass', 'holdout_beats_refit_incumbent_paired_ci_excludes_zero',
    'unique_vs_nine_scored_site_files', 'unique_literal_vs_all_registry_rasters',
    'rank_correlation_below_0_90', 'lane_single_method',
)
_SHA256 = re.compile(r'[0-9a-f]{64}')


def _sha256(value):
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def publication_eligible(card):
    """Check only a strict receipt schema; this is not cryptographic verification or slot authority.

    A positive card must carry `registry_uniqueness.complete_accessible_scan`, its
    `snapshot_sha256` and no scan errors; a verified coordinator lane receipt with a
    method paragraph, receipt path and SHA-256; a passing pre-placement surface
    receipt bound to a SHA-256; a numeric elapsed time in [0, 7200] seconds and an
    integer experiment count in [0, 3]; and organizer provenance with a receipt ID,
    input-manifest and template SHA-256s. All hard gates must be literal booleans.
    These attestations must still be verified by the separate release/selector process.
    """
    if not isinstance(card, dict):
        return False
    gates = card.get('gates')
    assignment = card.get('lane_assignment_receipt')
    surface_check = card.get('surface_preplacement_check')
    provenance = card.get('provenance')
    registry = card.get('registry_uniqueness')
    if not all(isinstance(value, dict) for value in
               (gates, assignment, surface_check, provenance, registry)):
        return False

    runtime = card.get('elapsed_seconds')
    experiments = gates.get('experiments_used')
    return (
        card.get('verdict') == 'PROMOTE'
        and card.get('protocol_stop_triggered') is False
        and gates.get('literal_rule_exception_applied') is False
        and all(gates.get(key) is True for key in REQUIRED_GATES)
        and registry.get('complete_accessible_scan') is True
        and registry.get('errors') == []
        and _sha256(registry.get('snapshot_sha256'))
        and assignment.get('status') == 'verified'
        and bool(assignment.get('method_paragraph'))
        and bool(assignment.get('receipt_path'))
        and _sha256(assignment.get('receipt_sha256'))
        and surface_check.get('status') == 'pass'
        and surface_check.get('checked_before_placement') is True
        and _sha256(surface_check.get('surface_sha256'))
        and _sha256(surface_check.get('receipt_sha256'))
        and type(runtime) in (int, float) and 0 <= runtime <= 7200
        and type(experiments) is int and 0 <= experiments <= 3
        and provenance.get('organizer_authenticated_inputs') is True
        and provenance.get('organizer_authenticated_template') is True
        and bool(provenance.get('organizer_receipt_id'))
        and _sha256(provenance.get('input_manifest_sha256'))
        and _sha256(provenance.get('template_sha256'))
    )

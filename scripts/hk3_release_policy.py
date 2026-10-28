"""Common HK3 publication adapter: mandatory stops plus the shared evidence gate.

Necessary schema checks only, never organizer authentication or slot authority.
A complete nested release_evidence contract is required, not a PROMOTE string.
The byte auditor additionally binds that contract to the saved TIFF/name/note.
"""
try:
    from .readiness import assess
except ImportError:
    from readiness import assess

REQUIRED_GATES = (
    'format_shared_validator_pass', 'grid_matches_example_submission',
    'whole_array_finite_in_0_1', 'no_dots_on_mapped_catalogue',
    'leakage_canary_pass', 'holdout_beats_refit_incumbent_paired_ci_excludes_zero',
    'unique_vs_nine_scored_site_files', 'unique_literal_vs_all_registry_rasters',
    'rank_correlation_below_0_90', 'lane_single_method',
)


def publication_eligible(card):
    if not isinstance(card, dict):
        return False
    gates = card.get('gates')
    if not isinstance(gates, dict):
        return False
    return (
        card.get('verdict') in ('PROMOTE', 'promote')
        and card.get('protocol_stop_triggered') is False
        and gates.get('literal_rule_exception_applied') is False
        and all(gates.get(key) is True for key in REQUIRED_GATES)
        and all(v is True for k, v in gates.items()
                if isinstance(v, bool) and k != 'literal_rule_exception_applied')
        and assess(card.get('release_evidence'))['verdict'] == 'promote'
    )

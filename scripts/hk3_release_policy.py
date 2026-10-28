"""Fail-closed publication policy; no waiver of the user's registry stop."""
REQUIRED_GATES = (
    'format_shared_validator_pass', 'grid_matches_example_submission',
    'whole_array_finite_in_0_1', 'no_dots_on_mapped_catalogue',
    'leakage_canary_pass', 'holdout_beats_refit_incumbent_paired_ci_excludes_zero',
    'unique_vs_nine_scored_site_files', 'unique_literal_vs_all_registry_rasters',
    'rank_correlation_below_0_90', 'lane_single_method',
)


def publication_eligible(card):
    """Necessary schema checks only, not organizer authentication or slot authority."""
    gates = card.get('gates', {})
    return (
        card.get('verdict') == 'PROMOTE'
        and card.get('protocol_stop_triggered') is False
        and gates.get('literal_rule_exception_applied') is False
        and all(gates.get(key) is True for key in REQUIRED_GATES)
    )

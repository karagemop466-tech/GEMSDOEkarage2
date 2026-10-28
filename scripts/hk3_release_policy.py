"""Fail-closed publication policy; no waiver of the user's registry stop.

This is a pre-publication gate only. It does not authorize a submission slot,
prove organizer acceptance, or authenticate data merely because a card says so.
"""
from __future__ import annotations

REQUIRED_GATES = (
    "format_shared_validator_pass",
    "grid_matches_example_submission",
    "whole_array_finite_in_0_1",
    "no_dots_on_mapped_catalogue",
    "leakage_canary_pass",
    "holdout_beats_refit_incumbent_paired_ci_excludes_zero",
    "unique_vs_nine_scored_site_files",
    "unique_literal_vs_all_registry_rasters",
    "unique_chance_corrected_vs_all_registry_rasters",
    "unique_literal_vs_submitted_dot_rasters",
    "rank_correlation_below_0_90",
    "lane_single_method",
)


def release_decision(card: dict, registry_audit: dict | None = None) -> dict:
    """Return eligibility and explicit blockers; missing evidence always blocks."""
    gates = card.get("gates") if isinstance(card.get("gates"), dict) else {}
    registry_audit = registry_audit if isinstance(registry_audit, dict) else {}
    blockers: list[str] = []

    if card.get("verdict") != "PROMOTE":
        blockers.append("run card does not record PROMOTE")
    if card.get("protocol_stop_triggered") is not False:
        blockers.append("protocol stop is recorded or not explicitly false")
    for key in REQUIRED_GATES:
        if gates.get(key) is not True:
            blockers.append(f"gate not passed: {key}")
    if gates.get("literal_rule_exception_applied") is not False:
        blockers.append("literal uniqueness exception is recorded or not explicitly false")

    assignment = card.get("lane_assignment")
    if (not isinstance(assignment, dict) or not assignment.get("paragraph")
            or not assignment.get("sha256") or assignment.get("assigned_by") != "coordinator"):
        blockers.append("coordinator-assigned method paragraph is absent or unauthenticated")
    if registry_audit.get("complete_accessible_scan") is not True or registry_audit.get("errors", 1) != 0:
        blockers.append("registry scan is incomplete or has errors")
    if card.get("organizer_inputs_authenticated") is not True:
        blockers.append("competition inputs/template are not organizer-authenticated")

    experiments = gates.get("experiments_used")
    if type(experiments) is not int or not 0 <= experiments <= 3:
        blockers.append("experiment budget evidence is missing or exceeds three experiments")
    minutes = gates.get("wall_clock_minutes")
    if type(minutes) is not int or not 0 <= minutes <= 120:
        blockers.append("two-hour budget evidence is missing or exceeded")

    return {"eligible": not blockers, "blockers": blockers}


def publication_eligible(card: dict, registry_audit: dict | None = None) -> bool:
    """Boolean wrapper for callers that need only the fail-closed result."""
    return release_decision(card, registry_audit)["eligible"]

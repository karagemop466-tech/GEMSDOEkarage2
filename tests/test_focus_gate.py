"""Committed evidence for the 2026-10-29 focus audit must stay internally consistent.

These tests read only committed JSON, so they run without the git-ignored cache.
They fail if a receipt is edited so that a stop becomes a pass, or if a claimed
exact subset relation no longer matches its recorded counts.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "evidence/focus-profile-2026-10-29.json"
GATE_DIR = ROOT / "evidence/lattice-gate"
SITES = {"GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"}


@pytest.fixture(scope="module")
def profile() -> dict:
    return json.loads(PROFILE.read_text())


def test_nine_sites_pinned_and_no_file_passes_the_gate(profile):
    assert {r["site"] for r in profile["sites"]} == SITES
    assert all(r["values_unique_in_footprint"] and max(r["values_unique_in_footprint"]) <= 1.0
               for r in profile["sites"])
    gate = {g["site"]: g["status"] for g in profile["gate_results"]}
    assert gate == {s: "DUPLICATE_STOP" for s in SITES}


def test_every_receipt_is_a_duplicate_stop_above_the_70_percent_clause():
    receipts = {p.stem: json.loads(p.read_text()) for p in GATE_DIR.glob("GEMSDOE*.json")}
    assert set(receipts) == SITES
    for site, receipt in receipts.items():
        assert receipt["status"] == "DUPLICATE_STOP", site
        assert receipt["upload_authorized"] is False
        assert receipt["comparisons"][0]["overlap_fraction"] > 0.70


def test_lattice_witness_is_dense_and_the_rank_clause_never_fires(profile):
    lat = profile["lattice_witness"]
    assert lat["positive_pixels"] == 206895
    assert lat["footprint_cover_within_3px"] > 0.99
    assert all(abs(g["spearman_with_lattice"]) < 0.001 for g in profile["gate_results"])


def test_exact_subset_counts_match_the_recorded_removals(profile):
    rel = {(c["subset"], c["of"]): c["removed_dots"] for c in profile["exact_subset_relations"]}
    assert rel[("GEMSDOE32", "GEMSDOE25")] == 6436
    assert rel[("GEMSDOE32", "GEMSDOE31")] == 2545
    assert rel[("GEMSDOE32", "GEMSDOE36")] == 1200
    assert rel[("GEMSDOE31", "GEMSDOE25")] == 3891
    removed = {(r["removed_from"], r["to"]): r for r in profile["removed_dot_catalogue_profile"]}
    assert removed[("GEMSDOE25", "GEMSDOE32")]["frac_within_3px_of_catalogue"] == 1.0
    assert removed[("GEMSDOE25", "GEMSDOE32")]["n"] == 6436


def test_removed_dot_profile_is_consistent_with_the_site_profile(profile):
    by_site = {r["site"]: r for r in profile["sites"]}
    assert by_site["GEMSDOE25"]["dots_in_footprint"] - by_site["GEMSDOE32"]["dots_in_footprint"] == 6436
    assert by_site["GEMSDOE25"]["pinned_sha256"] != by_site["GEMSDOE30"]["pinned_sha256"]
    rel = {(c["subset"], c["of"]): c["removed_dots"] for c in profile["exact_subset_relations"]}
    assert rel[("GEMSDOE25", "GEMSDOE30")] == 0  # identical dot sets, different bytes


def test_nested_pairs_are_reported_as_user_reports_not_tests(profile):
    corr = profile["correlations_nine_sites_user_reported_vs_measured"]
    assert corr["n"] == 9
    assert "not evidence of causation" in corr["caveat"]
    assert "USER-REPORTED" in profile["scope"]


def test_every_candidate_measured_in_the_historical_audit_is_recorded_and_stopped(profile):
    cands = {c["name"]: c for c in profile["other_candidates"]}
    assert len(cands) == 9
    assert all(c["gate_status"] == "DUPLICATE_STOP" for c in cands.values())
    assert all(c["frac_dots_within_3px_of_lattice"] > 0.70 for c in cands.values()
               if c["frac_dots_within_3px_of_lattice"] is not None)
    assert all(c["format"]["crs"] == "EPSG:32611" and c["format"]["dtype"] == "float32" for c in cands.values())

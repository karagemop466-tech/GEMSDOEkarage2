"""Tests for the 2026-10-31 decision verification.

Part 1 exercises the pure functions in scripts/verify_decision_evidence.py on synthetic arrays.
Part 2 checks that the committed receipts agree with each other and with the pinned profile.
Part 3 checks that the generator fails closed when those receipts disagree.
No test reads the competition data or the network.
"""
import copy
import json
from pathlib import Path

import numpy as np
import pytest

import verify_decision_evidence as v

ROOT = Path(__file__).resolve().parents[1]
EVID = json.loads((ROOT / "evidence/decision-verification-2026-10-31.json").read_text())
PAGE = json.loads((ROOT / "evidence/official-page-read-2026-10-31.json").read_text())
PROFILE = json.loads((ROOT / "evidence/focus-profile-2026-10-29.json").read_text())


# ---------- Part 1: pure functions on synthetic arrays ----------

def test_disk_has_29_cells_at_3px():
    # Integer points with x^2 + y^2 <= 9.
    assert int(v.disk(3).sum()) == 29


def test_dots_are_finite_and_strictly_positive():
    arr = np.array([[np.nan, 0.0, -1.0, 0.5, 1.0]], dtype=np.float32)
    assert v.dots(arr).tolist() == [[False, False, False, True, True]]


def test_within_3px_includes_distance_3_and_excludes_4():
    support = np.zeros((11, 11), dtype=bool)
    support[5, 5] = True
    halo = v.within_3px(support)
    assert halo[5, 8] and halo[8, 5]          # distance 3, on-axis
    assert not halo[5, 9] and not halo[9, 5]  # distance 4
    assert int(halo.sum()) == 29


def test_lattice_coverage_on_synthetic_footprint():
    footprint = np.ones((20, 20), dtype=bool)
    lattice = np.zeros((20, 20), dtype=bool)
    lattice[10, 10] = True
    out = v.lattice_coverage(footprint, lattice)
    assert out["footprint_cells"] == 400
    assert out["covered_within_3px"] == 29
    assert out["uncovered_cells"] == 371
    assert out["coverage_fraction"] == pytest.approx(29 / 400)


def test_literal_rule_bound_matches_the_arithmetic():
    # Overlap >= (N - u)/N, so clearing 70% needs at least 30% of dots in uncovered cells: N <= u/0.3.
    out = v.max_dots_passing_literal_rule(6649)
    assert out["max_dots_clearable_only_by_placing_dots_in_uncovered_cells"] == 22163
    assert out["minimum_share_of_dots_in_uncovered_cells"] == pytest.approx(0.3)
    assert v.max_dots_passing_literal_rule(100, limit=0.5)[
        "max_dots_clearable_only_by_placing_dots_in_uncovered_cells"] == 200


def test_dti_formula():
    assert v.dti(10, 20, 5) == pytest.approx(10 / (10 + 0.2 * 20 + 0.8 * 5))


def test_marginal_lemma_holds_on_default_grid_and_at_threshold():
    out = v.marginal_dot_lemma()
    assert out["all_rows_match_rule"] is True
    # Exactly at the threshold alpha*DTI, the marginal change is zero.
    at = v.marginal_dot_lemma(hits=(v.ALPHA * v.dti(10.0, 20.0, 5.0),))
    assert at["all_rows_match_rule"] is True


def test_aggregate_removal_rule_is_exact_for_mean_hit_rate():
    # Removing k dots with total expected hits H raises DTI iff H/k < alpha * DTI.
    tp, fp, fn = 10.0, 20.0, 5.0
    base = v.dti(tp, fp, fn)
    k, hits = 8, 0.4  # mean 0.05 < alpha*base = 0.111: removal should raise DTI
    removed = v.dti(tp - hits, fp - (k - hits), fn + hits)
    assert (removed > base) == (hits / k < v.ALPHA * base)
    k, hits = 4, 3.0  # mean 0.75 > threshold: removal should lower DTI
    removed = v.dti(tp - hits, fp - (k - hits), fn + hits)
    assert (removed > base) == (hits / k < v.ALPHA * base)
    assert removed < base


def test_subset_analysis_on_synthetic_rasters():
    reference = np.zeros((12, 12), dtype=np.float32)
    reference[2, 2] = reference[2, 9] = reference[9, 2] = reference[9, 9] = 1.0
    candidate = reference.copy()
    candidate[9, 9] = 0.0  # removed
    candidate[2, 9] = 0.0  # removed
    catalogue = np.zeros((12, 12), dtype=bool)
    catalogue[9, 8] = True  # within 3 px of (9, 9) only
    out = v.subset_analysis(candidate, reference, catalogue)
    assert out["candidate_dots"] == 2
    assert out["reference_dots"] == 4
    assert out["candidate_subset_of_reference"] is True
    assert out["added_dots"] == 0
    assert out["removed_dots"] == 2
    assert out["removed_catalogue_adjacent_dots"] == 1
    assert out["kept_catalogue_adjacent_dots"] == 0


def test_subset_analysis_detects_added_dots():
    reference = np.zeros((5, 5), dtype=np.float32)
    candidate = np.zeros((5, 5), dtype=np.float32)
    candidate[1, 1] = 1.0
    out = v.subset_analysis(candidate, reference, np.zeros((5, 5), dtype=bool))
    assert out["candidate_subset_of_reference"] is False
    assert out["added_dots"] == 1


def test_implied_bound_is_alpha_times_reported_d28_score():
    out = v.implied_removed_hit_rate_bound(6436)
    assert out["mean_hit_probability_upper_bound"] == pytest.approx(0.2 * 0.26)
    assert "DERIVED" in out["evidence_class"]


# ---------- Part 2: committed receipts agree with each other and with the pinned profile ----------

def test_decision_flags_are_negative():
    assert EVID["decision"]["ok_to_download_and_submit_any_file"] is False
    assert PAGE["decision"]["ok_to_download_and_submit_any_file"] is False
    assert PAGE["decision"]["experiments_run"] == 0
    assert PAGE["decision"]["tifs_generated"] == 0
    assert PAGE["decision"]["competition_slots_used"] == 0


def test_lattice_coverage_matches_pinned_profile_and_bound():
    cov = EVID["lattice_coverage"]
    assert round(cov["coverage_fraction"], 6) == PROFILE["lattice_witness"]["footprint_cover_within_3px"]
    assert cov["footprint_cells"] == EVID["template_footprint_cells"] == 5167373
    assert cov["covered_within_3px"] + cov["uncovered_cells"] == cov["footprint_cells"]
    assert cov["uncovered_cells"] == 6649
    bound = EVID["literal_rule_bound"]
    assert bound["max_dots_clearable_only_by_placing_dots_in_uncovered_cells"] == v.max_dots_passing_literal_rule(
        cov["uncovered_cells"])["max_dots_clearable_only_by_placing_dots_in_uncovered_cells"]


def test_gems32_subset_arithmetic_is_consistent():
    s = EVID["gems32_vs_d28"]
    assert s["candidate_subset_of_reference"] is True
    assert s["added_dots"] == 0
    assert s["candidate_dots"] == 37654
    assert s["reference_dots"] == 44090
    assert s["candidate_dots"] + s["removed_dots"] == s["reference_dots"]
    assert s["removed_dots"] == s["removed_catalogue_adjacent_dots"] == 6436
    assert s["reference_catalogue_adjacent_dots"] == 8607
    assert s["kept_catalogue_adjacent_dots"] == s["reference_catalogue_adjacent_dots"] - s["removed_catalogue_adjacent_dots"] == 2171


def test_gems32_fails_the_rho_clause_and_the_overlap_clause():
    rho = EVID["spearman_full_footprint"]
    assert rho["gems32_vs_d28"] > rho["rho_limit"] == 0.9
    assert EVID["gems32_dots_within_3px_of_lattice"] > 0.70


def test_d28_family_is_measured_identical_across_sites():
    fam = EVID["d28_family_identity"]
    assert fam["reference_dots"] == fam["gems25_dots"] == fam["gems30_dots"] == 44090
    assert fam["gems25_equals_reference"] is True
    assert fam["gems30_equals_reference"] is True


def test_marginal_lemma_rows_match_rule_in_receipt():
    assert EVID["marginal_dot_lemma"]["all_rows_match_rule"] is True
    assert EVID["marginal_dot_lemma"]["base_dti"] == pytest.approx(v.dti(10.0, 20.0, 5.0))


def test_removed_hit_rate_bound_in_receipt_uses_user_reported_score_only():
    bound = EVID["implied_removed_hit_rate"]
    assert bound["reported_d28_dti"] == 0.26
    assert bound["mean_hit_probability_upper_bound"] == pytest.approx(0.052)
    assert "USER-REPORTED" in bound["evidence_class"]


def test_repo_tifs_are_in_range_and_grids_are_identical():
    rng = EVID["portal_range_check"]
    assert rng["files_checked"] == 10
    assert rng["files_with_values_outside_0_1_or_nan"] == []
    assert EVID["grid"]["same_grid_all"] is True
    assert EVID["grid"]["gems32"]["crs_epsg"] == 32611
    assert EVID["grid"]["gems32"]["shape"] == [3730, 3292]


def test_catalogue_equals_template_positives():
    assert EVID["catalogue_labels_equal_template_ones"] is True
    assert EVID["template_ones_inside_footprint"] == 60988


def test_no_leaderboard_or_score_estimate_is_written_as_a_result():
    text = json.dumps(EVID)
    assert "score_estimate" not in text
    assert "leaderboard_estimate" not in text


def test_official_page_read_records_leaderboard_and_quotes():
    assert PAGE["schema"] == "gems.official-page-observations.v1"
    assert PAGE["observed_date_utc"] == "2026-10-31"
    lb = next(s for s in PAGE["sources"] if "leaderboard" in s["url"])
    assert lb["rank_1"]["value"] == 0.4544
    assert lb["rank_50"]["value"] == 0.3195
    assert lb["user_cited_0_4413_present"] is False
    assert lb["user_cited_0_2778_present"] is False
    page = next(s for s in PAGE["sources"] if s["url"].endswith("/page/967/"))
    assert "new faults" in page["quoted_text"]["hidden_test_is_new_faults"] or \
        "not contained within the current public USGS database" in page["quoted_text"]["hidden_test_is_new_faults"]
    assert page["quoted_text"]["triangular_kernel"].count("300 meters") == 1


def test_official_page_read_is_not_picked_up_by_the_10_30_glob():
    # The generator's latest-observation glob must keep selecting the 2026-10-30 file.
    names = sorted(p.name for p in (ROOT / "evidence").glob("official-review-????-??-??.json"))
    assert names and names[-1] == "official-review-2026-10-30.json"


# ---------- Part 3: generator fails closed ----------

def _inputs():
    return copy.deepcopy(EVID), copy.deepcopy(PAGE), copy.deepcopy(PROFILE)


def test_generator_accepts_committed_receipts():
    from build_hk3_pages import check_verification
    check_verification(*_inputs())


@pytest.mark.parametrize("mutate", [
    lambda e, p, f: e["decision"].update(ok_to_download_and_submit_any_file=True),
    lambda e, p, f: e["gems32_vs_d28"].update(candidate_subset_of_reference=False),
    lambda e, p, f: e["spearman_full_footprint"].update(gems32_vs_d28=0.5),
    lambda e, p, f: e["lattice_coverage"].update(coverage_fraction=0.5),
    lambda e, p, f: e["portal_range_check"].update(files_with_values_outside_0_1_or_nan=["x.tif"]),
    lambda e, p, f: p["decision"].update(experiments_run=1),
])
def test_generator_rejects_inconsistent_receipts(mutate):
    from build_hk3_pages import check_verification
    e, p, f = _inputs()
    mutate(e, p, f)
    with pytest.raises(ValueError):
        check_verification(e, p, f)

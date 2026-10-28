"""Fail closed on literal policy; experimental promotion is not upload approval."""
import json
import math
from pathlib import Path

import pytest
from scripts.audit_k2_release import audit, registry_failures

ROOT = Path(__file__).resolve().parents[1]


def row(rho=0.1, overlap=0.2):
    return dict(repo='fixture', submission='inputs/calibration/example.tif',
                spearman_full_footprint=rho, my_dots_within_3px_of_theirs=overlap)


@pytest.mark.parametrize('rho,overlap', [(0.91, 0.2), (0.1, 0.71),
                                        (None, 0.2), (0.1, math.nan),
                                        (True, 0.2), (0.1, 1.1)])
def test_failed_or_unknown_measurements_block(rho, overlap):
    assert registry_failures({'rows': [row(rho, overlap)]})


def test_boundary_is_inclusive_and_calibration_not_exempt():
    assert not registry_failures({'rows': [row(.90, .70)]})
    assert registry_failures({'rows': [row(.1, .7205)]})
    assert registry_failures({'rows': []})
    assert registry_failures({'rows': [None]})
    assert registry_failures(None)


def test_current_audit_is_reproducible_and_not_authorized():
    current = audit()
    assert current == json.loads((ROOT / 'evidence/k2/literal_release_audit.json').read_text())
    assert all(current['validator'].values())
    assert current['registry_failures']
    bound = current['geometry_lower_bound']
    assert bound['saved_positive_pixels'] == 54491
    assert bound['minimum_matches_if_all_dots_in_mirror_footprint'] == 47842
    assert bound['minimum_overlap_if_all_dots_in_mirror_footprint'] > 0.70
    comparisons = current['correlation_overlap_vs_registry']
    assert 'impossible_gate' not in comparisons
    assert comparisons['surface_before_placement']['vs_r13_lattice_support_overlap_within_3px'] == 1.0
    assert comparisons['surface_before_placement']['duplicate_stop'] is True
    assert comparisons['final_dots']['unique_under_literal_gate'] is False
    assert current['verdict'] == 'negative'
    assert current['slot_authorized'] is False
    assert current['leaderboard_estimate'] is None
    assert current['experiments_run'] == 0


@pytest.mark.parametrize('page', ['index.html', 'executive-summary.html', 'how-to-submit.html'])
def test_public_current_verdict_is_explicit(page):
    text = (ROOT / 'docs' / page).read_text()
    assert 'literal_release_audit.json' in text
    assert 'Current literal-policy verdict: NEGATIVE' in text
    assert 'cannot trigger' not in text

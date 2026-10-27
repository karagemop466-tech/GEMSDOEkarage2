import pytest
from scripts.audit_references import geometry_stop


def test_real_budget_is_forced_duplicate():
    result = geometry_stop(6649, 37654)
    assert result["min_dots_within_3px"] == 31005
    assert result["min_fraction_within_3px"] == pytest.approx(0.8234184947150369)
    assert result["forced_duplicate_stop"] is True


def test_strict_threshold_and_small_budget():
    assert geometry_stop(3, 10)["min_fraction_within_3px"] == 0.7
    assert geometry_stop(3, 10)["forced_duplicate_stop"] is False
    assert geometry_stop(2, 10)["forced_duplicate_stop"] is True
    assert geometry_stop(9, 2)["forced_duplicate_stop"] is False
    assert geometry_stop(0, 1)["forced_duplicate_stop"] is True
    assert geometry_stop(6649, 22163)["forced_duplicate_stop"] is False
    assert geometry_stop(6649, 22164)["forced_duplicate_stop"] is True


@pytest.mark.parametrize("uncovered,budget", [(-1, 10), (1, 0), (1, -1), (True, 10), (1, 1.0)])
def test_invalid_counts(uncovered, budget):
    with pytest.raises(ValueError):
        geometry_stop(uncovered, budget)

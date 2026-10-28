from copy import deepcopy

from scripts.hk3_release_policy import REQUIRED_GATES, publication_eligible, release_decision


def valid_fixture():
    card = {
        "verdict": "PROMOTE",
        "protocol_stop_triggered": False,
        "organizer_inputs_authenticated": True,
        "lane_assignment": {
            "paragraph": "coordinator-assigned paragraph",
            "sha256": "a" * 64,
            "assigned_by": "coordinator",
        },
        "gates": {key: True for key in REQUIRED_GATES},
    }
    card["gates"].update(
        literal_rule_exception_applied=False,
        experiments_used=3,
        wall_clock_minutes=120,
    )
    registry = {"complete_accessible_scan": True, "errors": 0}
    return card, registry


def test_complete_explicit_evidence_is_necessary_for_eligibility():
    card, registry = valid_fixture()
    assert publication_eligible(card, registry)

    for key in REQUIRED_GATES:
        changed = deepcopy(card)
        changed["gates"][key] = False
        assert not publication_eligible(changed, registry), key

    changed = deepcopy(card)
    changed["gates"]["literal_rule_exception_applied"] = True
    assert not publication_eligible(changed, registry)

    changed = deepcopy(card)
    changed["protocol_stop_triggered"] = True
    assert not publication_eligible(changed, registry)

    changed = deepcopy(card)
    changed["lane_assignment"]["assigned_by"] = "local"
    assert not publication_eligible(changed, registry)

    changed = deepcopy(card)
    changed["organizer_inputs_authenticated"] = False
    assert not publication_eligible(changed, registry)

    changed_registry = {"complete_accessible_scan": False, "errors": 0}
    assert not publication_eligible(card, changed_registry)
    changed_registry = {"complete_accessible_scan": True, "errors": 1}
    assert not publication_eligible(card, changed_registry)

    changed = deepcopy(card)
    changed["gates"]["experiments_used"] = 4
    assert not publication_eligible(changed, registry)
    changed = deepcopy(card)
    changed["gates"]["wall_clock_minutes"] = 121
    assert not publication_eligible(changed, registry)


def test_missing_evidence_fails_closed_and_reports_reasons():
    decision = release_decision({"verdict": "NEGATIVE"}, None)
    assert decision["eligible"] is False
    assert any("registry scan" in reason for reason in decision["blockers"])
    assert any("coordinator-assigned" in reason for reason in decision["blockers"])

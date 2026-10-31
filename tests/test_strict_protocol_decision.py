"""The literal any-registry overlap stop must dominate earlier release cards."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str):
    return json.loads((ROOT / rel).read_text())


def test_strict_decision_is_negative_and_no_file_is_approved():
    decision = read("evidence/strict-protocol-decision-2026-10-31.json")
    inventory = read("evidence/public_downloads_audit.json")
    assert decision["verdict"] == "negative"
    assert decision["validator_output"]["submission_authorized"] is False
    assert decision["submission_slots_used"] == 0
    assert decision["binding_rule"]["exception_for_space_filling_reference"] is False
    assert inventory["inventory_status"] == "PASS_RESEARCH_ONLY"
    assert inventory["downloadable_approved_submission"] is None
    assert inventory["slot_authorized"] is False
    metrics = decision["correlation_overlap_vs_registry"]
    assert metrics["HALO"]["literal_gate"] == "FAIL"
    assert metrics["HALO"]["literal_overlap_including_lattice"] > 0.70
    assert metrics["off_catalogue_GBM"]["literal_gate"] == "FAIL"
    assert metrics["off_catalogue_GBM"]["max_one_sided_overlap_non_space_filling"] > 0.70
    assert metrics["K10"]["literal_gate"] == "FAIL"


def test_earlier_positive_receipts_cannot_override_the_literal_stop():
    halo = read("evidence/halo/final_generation.json")
    gbm = read("evidence/lane-gbm/final-run-card.json")
    assert halo["verdict"]["ok_to_submit"] is True  # preserved historical lane receipt
    assert halo["uniqueness_literal_gate"]["unique"] is False
    assert halo["uniqueness_literal_gate"]["stop_required"] is True
    assert gbm["verdict"] == "promote"  # preserved historical lane receipt
    assert gbm["correlation_overlap_vs_registry"]["worst_one_sided_non_space_filling"] > 0.70
    assert gbm["raster"]["sha256"] == read(
        "docs/downloads/gemsdoekarage2-gbm-offcat-a5-n100000-20261031T020958Z.run-card.json"
    )["sha256"]
    rows = {Path(row["file"]).name: row for row in inventory_rows()}
    assert rows[Path(halo["submission_file"]).name]["status"] == "VERIFIED_RESEARCH_ONLY"
    assert rows[Path(gbm["raster"]["file"]).name]["status"] == "VERIFIED_RESEARCH_ONLY"


def inventory_rows():
    return read("evidence/public_downloads_audit.json")["artifacts"]


def test_all_prominent_decision_pages_are_fail_closed_and_keep_research_downloads():
    pages = (
        "index.html",
        "docs/release.html",
        "docs/release-gbm.html",
        "docs/release-gbm-summary.html",
        "docs/release-gbm-how-to-submit.html",
        "docs/release-summary.html",
        "docs/release-how-to-submit.html",
        "docs/index.html",
        "docs/submission-desk.html",
    )
    for page in pages:
        text = (ROOT / page).read_text()
        assert "DO NOT SUBMIT" in text, page
    assert "NO FILE IS CLEARED TO SUBMIT" in (ROOT / "index.html").read_text()
    assert "NO FILE CLEARED UNDER THE LITERAL UNIQUENESS RULE" in (ROOT / "docs/release.html").read_text()
    assert "93.77%" in (ROOT / "docs/release-gbm.html").read_text()

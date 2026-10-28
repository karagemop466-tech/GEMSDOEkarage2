"""K3 (2026-10-28): holdout-best but uniqueness-negative; evidence must agree."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEM = "gemsdoekarage2-k3-linctxdti-b110-20261028-zeros"
TIF = ROOT / "docs/downloads" / f"{STEM}.tif"


def load(path):
    return json.loads(Path(path).read_text())


def test_k3_run_card_negative_and_sha_matches_bytes():
    card = load(ROOT / "evidence/k3/run_card.json")
    assert card["verdict"] == "negative"
    assert card["submission_slots_used"] == 0
    assert card["experiments_run"] == 3
    digest = hashlib.sha256(TIF.read_bytes()).hexdigest()
    assert digest == card["raster_sha256"]
    assert card["raster_bytes"] == TIF.stat().st_size
    assert len(card["note"]) <= 140 and card["note_chars"] == len(card["note"])


def test_k3_holdout_gain_and_canaries():
    card = load(ROOT / "evidence/k3/run_card.json")
    h = card["holdout"]
    assert h["evidence_class"] == "HOLDOUT-DTI"
    assert h["evaluator_version"] == "gems57-pooled-hide-v2"
    assert h["withheld_positive_pixels"] == 58258
    delta = h["paired_delta_vs_incumbent"]
    assert delta["ci95"][0] > 0  # paired gain vs replicated K2 incumbent
    assert card["leakage_canary"]["all_pass_le_0.90"]
    assert card["leakage_canary"]["worst_max_auc_or_1_minus_auc"] <= 0.90
    comb = load(ROOT / "evidence/k3/combined_holdout.json")
    assert comb["scores"]["k3dti_b110"]["dti"] == h["candidate_dti"]
    # incumbent replication is faithful to the archived K2 number
    assert abs(comb["scores"]["k2rep_b110"]["dti"] - 0.15754959003555036) < 2e-5


def test_k3_uniqueness_failure_is_recorded_not_hidden():
    card = load(ROOT / "evidence/k3/run_card.json")
    final = card["correlation_overlap_vs_registry"]["final_dots"]
    assert final["duplicates_primary_count"] >= 1
    assert max(r["overlap"] for r in final["flagged_primary"]) > 0.70
    assert all(r["k3_dots_within_3px"] <= 0.70 for r in final["vs_9_focus_best"])
    audit = load(ROOT / "evidence/k3/final_registry_audit.json")
    rows = audit["primary_submission_scope"]["rows"]
    flagged = [r for r in rows if r.get("duplicate_by_overlap") or r.get("duplicate_by_rho")]
    assert len(flagged) == final["duplicates_primary_count"]
    assert not card["correlation_overlap_vs_registry"]["surface_before_placement"]["gate_pass"]


def test_k3_site_language_is_negative():
    for page in ("index.html", "executive-summary.html"):
        text = (ROOT / "docs" / page).read_text()
        assert f"{STEM}.tif" in text
        assert "DO NOT SUBMIT" in text
        assert "CONDITIONAL YES" not in text
        assert "evidence/k3/run_card.json" in text
        # K3 is a historical research file, never offered; no repository file is approved.
        assert f'{STEM}.tif" download' not in text
        assert "repository's largest recorded point HOLDOUT-DTI" in text
        assert "No candidate is approved" in text

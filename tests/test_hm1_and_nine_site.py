"""Regression checks for the 2026-10-31 HM1 candidate and the nine-site executive receipt.

These tests read only tracked files (no .cache, no network), so they run in CI.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "docs/downloads"
STEM = "gemsdoekarage2-hm1-offcat-magridge-35079-20261031-DO-NOT-SUBMIT"
TIF = DOWNLOADS / f"{STEM}.tif"
CARD = DOWNLOADS / f"{STEM}-run-card.json"
NINE = ROOT / "docs/evidence/nine-site-executive-20261031.json"
PREREG = ROOT / "docs/evidence/hm1/preregistration.json"
UNIQ = ROOT / "docs/evidence/hm1/uniqueness_full_registry_489.json"
EXTERIOR_NAN = 7111787  # official sample_submission.tif NaN count (pinned sha 2176d08e...)


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_hm1_run_card_is_negative_and_bound_to_bytes():
    card = json.loads(CARD.read_text())
    assert card["ok_to_submit"] is False
    assert card["approved_for_weekly_slot"] is False
    assert card["slot_authorized"] is False
    assert card["verdict"] == "negative"
    assert card["raster"]["sha256"] == _sha(TIF)
    assert card["submission"]["name"] == STEM
    assert 0 < len(card["submission"]["note"]) <= 140
    assert "DO NOT SUBMIT" in card["submission"]["note"]
    assert card["holdout_DTI"]["status"] == "NOT_AVAILABLE_FOR_SCORING"


def test_hm1_uniqueness_receipt_records_duplicate_stop_against_lattice():
    u = json.loads(UNIQ.read_text())
    assert u["summary"]["status"] == "DUPLICATE_STOP"
    assert u["summary"]["upload_authorized"] is False
    assert u["summary"]["registry_items_total"] == 489
    witness = [r for r in u["comparisons"] if r.get("overlap_fraction") == 1.0]
    assert any("r13-lattice" in r["path"] for r in witness)


def test_hm1_tif_is_format_valid_and_has_exterior_nan():
    with rasterio.open(TIF) as ds:
        assert ds.count == 1 and ds.dtypes == ("float32",)
        assert ds.crs.to_string() == "EPSG:32611"
        assert (ds.height, ds.width) == (3730, 3292)
        a = ds.read(1)
    finite = np.isfinite(a)
    assert int((~finite).sum()) == EXTERIOR_NAN
    inside = a[finite]
    assert inside.min() >= 0.0 and inside.max() <= 1.0
    assert set(np.unique(inside).tolist()) <= {0.0, 1.0}
    assert int((inside == 1.0).sum()) == 35079


def test_hm1_preregistration_records_the_amendment_and_no_label_tuning():
    pre = json.loads(PREREG.read_text())
    assert pre["tuning_on_labels"] is False
    assert pre["amendments"][0]["amendment_id"] == "A1"
    assert "Feasibility" in pre["amendments"][0]["reason"]


def test_nine_site_receipt_is_measured_and_refuses_estimates():
    doc = json.loads(NINE.read_text())
    sites = [r["site"] for r in doc["sites"]]
    assert sites == sorted(sites) and len(sites) == 9
    assert set(sites) == {"GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                          "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"}
    for r in doc["sites"]:
        assert r["sha256_matches_pinned_github_bytes"] is True
        assert r["format"]["nan_inside_footprint"] == 0
        assert r["format"]["finite_inside_footprint_in_0_1"] is True
        # Exterior convention is NOT uniform across the nine files (flagged irregularity):
        # five are NaN outside the footprint, four are zeros. Both are finite inside.
        if r["format"]["outside_footprint_values"] == "NaN":
            assert r["format"]["outside_nan_count"] == EXTERIOR_NAN
        else:
            assert r["format"]["outside_footprint_values"] == "zeros"
            assert r["format"]["outside_nan_count"] == 0
        assert r["estimated_leaderboard_score"].startswith("UNAVAILABLE")
        assert r["fraction_dots_within_3px_of_registry_lattice_r13"] > 0.70
    assert doc["verdict_summary"]["any_file_passes_literal_uniqueness_gate"] is False
    assert doc["verdict_summary"]["upload_authorized"] is False

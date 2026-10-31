"""Tests for the 2026-10-31 off-catalogue GBM lane release.

These tests only read committed artifacts (the published GeoTIFF, its run card
and the JSON evidence), so they run in CI without the 419 MB feature stack.
Anything that needs ``data/core`` skips cleanly.
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
rasterio = pytest.importorskip("rasterio")


def rel(path: str) -> Path:
    return ROOT / path


def released_cards():
    cards = sorted(glob.glob(str(ROOT / "docs" / "downloads" / "*gbm-offcat*.run-card.json")))
    if not cards:
        pytest.skip("no lane release run-card present")
    return [json.loads(Path(c).read_text()) for c in cards]


def test_release_run_card_exists_and_is_self_consistent():
    card = released_cards()[-1]
    tif = ROOT / "docs" / "downloads" / card["file"]
    assert tif.is_file()
    import hashlib
    h = hashlib.sha256()
    h.update(tif.read_bytes())
    assert h.hexdigest() == card["sha256"], "run card sha256 must match the saved bytes"
    assert card["n_dots"] > 0
    assert card["apron_px"] >= 2.0


def test_release_raster_passes_every_format_gate():
    card = released_cards()[-1]
    with rasterio.open(ROOT / "docs" / "downloads" / card["file"]) as ds:
        assert ds.driver == "GTiff"
        assert ds.count == 1
        assert ds.dtypes[0] == "float32"
        assert ds.crs.to_string() == "EPSG:32611"
        assert (ds.height, ds.width) == (3730, 3292)
        assert (ds.transform.a, ds.transform.e) == (100.0, -100.0)
        assert (ds.transform.b, ds.transform.d) == (0.0, 0.0)
        assert (round(ds.transform.c, 3), round(ds.transform.f, 3)) == (243350.0, 4508550.0)
        a = ds.read(1)
    # the portal's "Predicted values must be in range [0, 1]" rejection is caused
    # by non-finite values; assert against the WHOLE array, not just the footprint.
    assert np.isfinite(a).all(), "no NaN or Inf anywhere in the array"
    assert a.min() >= 0.0 and a.max() <= 1.0
    assert int((a > 0).sum()) == card["n_dots"]


def test_release_raster_dots_stay_outside_the_catalogue_apron():
    labels = rel("data/core/labels.tif")
    if not labels.is_file():
        pytest.skip("competition labels mirror not restored")
    from scipy import ndimage
    with rasterio.open(labels) as s:
        cat = s.read(1) == 1
    card = released_cards()[-1]
    with rasterio.open(ROOT / "docs" / "downloads" / card["file"]) as s:
        a = s.read(1)
    d = ndimage.distance_transform_edt(~cat)
    dots = a > 0
    assert d[dots].min() > card["apron_px"], "no dot may sit inside the catalogue apron"


def test_release_validator_recorded_all_gates_as_passed():
    card = released_cards()[-1]
    v = card["validator"]
    for key in ("single_band", "dtype_float32", "crs_EPSG_32611", "shape_3730x3292",
                "transform_matches_template", "bounds_match", "all_values_finite",
                "all_values_in_0_1_whole_array", "no_nan_inside_footprint", "passed"):
        assert v[key] is True, key


def test_projection_is_labelled_and_never_presented_as_a_score():
    card = released_cards()[-1]
    pm = card["projection_model"]
    assert pm["K_hat"] > 0
    assert len(pm["K_hat_range"]) == 2
    assert "MODEL-PROJECTION" in json.dumps(card)
    assert "unknown" in pm["lambda_meaning"].lower() and "band" in pm["lambda_meaning"].lower()
    assert card.get("score_estimate") is None or "projection" in str(card).lower()


def test_final_run_card_carries_the_protocol_fields():
    p = rel("evidence/lane-gbm/final-run-card.json")
    if not p.is_file():
        pytest.skip("final run card not generated")
    card = json.loads(p.read_text())
    for key in ("hypothesis", "mechanism", "named_non_fault_mimic", "holdout",
                "leakage_canary", "correlation_overlap_vs_registry", "raster",
                "validator", "submission_name", "note", "verdict"):
        assert key in card, key
    assert len(card["note"]) <= 140, "submission note must be at most 140 characters"
    assert card["note_within_140"] is True
    assert card["weekly_slot_used"] is False, "this project never spends a slot"
    assert card["leakage_canary"]["max_single_feature_auc"] <= 0.90
    assert not card["leakage_canary"]["flagged"]


def test_holdout_number_is_labelled_as_a_proxy_and_carries_the_anti_correlation_warning():
    p = rel("evidence/lane-gbm/final-run-card.json")
    if not p.is_file():
        pytest.skip("final run card not generated")
    card = json.loads(p.read_text())
    hold = card["holdout"]
    assert hold["classification"].startswith("HOLDOUT-DTI-PROXY")
    assert hold["evaluator"] == "scripts/evaluate_holdout.py dti_weighted_terms"
    assert hold["protocol_number"]["withheld_positive_pixels"] > 0
    assert len(hold["protocol_number"]["interval95_fold_range"]) == 2
    assert "-1.00" in hold["anticorrelation_warning"]
    assert "NOT a quality measurement" in hold["shipped_raster_recomputed"]["why_zero"]


def test_nine_site_scorecard_is_complete_and_reports_no_unique_file():
    p = rel("docs/data/nine-site-scorecard.json")
    if not p.is_file():
        pytest.skip("nine-site scorecard not generated")
    d = json.loads(p.read_text())
    assert len(d["sites"]) == 9
    for s in d["sites"]:
        assert s["reported_unverified"] > 0
        assert s["n_dots"] > 0
        assert s["unique_vs_other_eight"] is False, (
            "all nine focus best-files belong to one dot pool")
        assert s["max_symmetric_within_3px_vs_other_eight"] > 0.70
    assert d["verified_subset_relations"]["GEMSDOE32_subset_of_GEMSDOE25"] is True
    assert d["verified_subset_relations"]["GEMSDOE31_subset_of_GEMSDOE25"] is True


def test_mask_width_calibration_records_the_negative_rank_correlation():
    p = rel("docs/data/mask-width-calibration.json")
    if not p.is_file():
        pytest.skip("mask-width calibration not generated")
    d = json.loads(p.read_text())
    assert d["sweep"], "at least one exclusion width must have been swept"
    assert d["best_spearman"] <= -0.9, (
        "catalogue rediscovery is anti-correlated with the reported leaderboard")
    assert "off-catalogue" in d["caveat"] and "not a score" in d["caveat"]


def test_release_pages_exist_and_are_reproducible():
    import subprocess
    import sys
    for page in ("release-gbm.html", "release-gbm-summary.html", "release-gbm-how-to-submit.html"):
        assert (ROOT / "docs" / page).is_file(), page
    r = subprocess.run([sys.executable, "scripts/build_release.py", "--check"],
                       cwd=str(ROOT), capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_release_pages_state_the_verdict_and_never_claim_a_measured_score():
    for page in ("release-gbm.html", "release-gbm-summary.html"):
        text = (ROOT / "docs" / page).read_text()
        assert "OK TO SUBMIT: YES" in text
        assert "MODEL-PROJECTION" in text
        assert "not a score" in text


def test_release_pages_disclose_the_one_sided_uniqueness_caveat():
    text = (ROOT / "docs" / "release-gbm.html").read_text()
    if "IR-ONESIDED-01" not in text:
        pytest.skip("one-sided caveat not applicable for this build")
    # the disclosure must be present and must name the counter-evidence
    assert "Jaccard" in text
    assert "Spearman" in text


def test_root_index_keeps_its_historical_links():
    text = (ROOT / "index.html").read_text()
    assert "docs/release.html" in text
    assert "docs/executive-summary.html" in text
    assert "docs/index.html" in text


def test_release_pages_do_not_clobber_the_published_release_desk():
    """Two lanes exist; the published release desk must not be overwritten."""
    halo = (ROOT / "docs" / "release.html").read_text()
    assert "halo39-b44090-sep2-20261031" in halo
    gbm = (ROOT / "docs" / "release-gbm.html").read_text()
    assert "gbm-offcat" in gbm
    assert "release.html" in gbm, "the GBM page must cross-link the published release desk"


def test_release_artifact_is_listed_separately_from_the_research_inventory():
    from scripts import audit_public_downloads as mod
    result = mod.audit()
    assert result["inventory_status"] in (
        "PASS_RESEARCH_ONLY", "PASS_WITH_CANDIDATE", "PASS_RESEARCH_ONLY_PLUS_RELEASE")
    assert result["unexpected_downloads"] == []
    # the lane never spends a weekly slot, whoever else the inventory names
    assert result["slot_authorized"] is False
    assert len([r for r in result["artifacts"] if r["kind"] == "release"]) <= 1, (
        "this repository publishes at most one recommended release")
    lanes = [r for r in result["artifacts"]
             if r["file"].endswith("gemsdoekarage2-gbm-offcat-a5-n100000-20261031T020958Z.tif")]
    assert lanes, "the GBM lane file must be registered in the inventory"
    assert lanes[0]["status"] == "VERIFIED_CANDIDATE_ELIGIBLE"
    assert lanes[0]["slot_authorized"] is False

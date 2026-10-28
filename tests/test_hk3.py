"""HK3 historical run evidence, strict current disposition and public pages.

Assertions use saved receipts and TIFF bytes; they do not rerun training or
reconstruct any missing feature cache.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "evidence" / "hk3"
DOCS = ROOT / "docs"
STEM = "gemsdoekarage2-hk3-edgecentrality-apron3-20261028"


def load(path):
    return json.loads(Path(path).read_text())


@pytest.fixture(scope="module")
def card():
    """The original experiment card is preserved as historical evidence."""
    return load(EV / "run_card.json")


@pytest.fixture(scope="module")
def strict():
    """Current release authority: strict negative reassessment, not a new run."""
    return load(EV / "strict_disposition.json")


def test_hk3_gate_uses_literal_rule_for_all_registry_rows_without_exceptions():
    import inspect
    from scripts import hk3

    rows = [
        {"submission": "unsubmitted.tif", "duplicate_by_rho": False, "duplicate_by_overlap": True},
        {"submission": "dense-surface.tif", "duplicate_by_rho": True, "duplicate_by_overlap": False},
        {"submission": "unique.tif", "duplicate_by_rho": False, "duplicate_by_overlap": False},
        {"submission": "unreadable.tif", "error": "missing"},
    ]
    assert [row["submission"] for row in hk3.literal_duplicate_rows(rows)] == [
        "unsubmitted.tif", "dense-surface.tif"]

    gates = {"format": True, "unique_literal_vs_all_registry_rasters": False,
             "literal_rule_exception_applied": True}
    assert hk3.strict_run_card_verdict(gates) == "NEGATIVE"
    gates["unique_literal_vs_all_registry_rasters"] = True
    assert hk3.strict_run_card_verdict(gates) == "NEGATIVE"  # disclosed exception itself is also a stop
    gates["literal_rule_exception_applied"] = False
    assert hk3.strict_run_card_verdict(gates) == "PROMOTE"

    e3_source = inspect.getsource(hk3.cmd_e3)
    assert e3_source.index("audit_preplacement_surface") < e3_source.index("dots = emit(surf")


def test_historical_and_current_receipts_are_mirrored_byte_for_byte():
    for name in ("run_card.json", "strict_disposition.json", "strict_selector_result.json",
                 "e2.json", "bridge.json", "e3_generation.json", "registry_audit.json",
                 "anchors_out_of_sample.json", "leakage_inflation.json", "validate_tif_strict.json"):
        assert load(EV / name) == load(DOCS / "evidence" / "hk3" / name), name
    observation = ROOT / "evidence/public_leaderboard_observation_2026-10-28.json"
    assert observation.read_bytes() == (DOCS / "evidence" / observation.name).read_bytes()


def test_prior_positive_decision_is_preserved_but_current_disposition_is_negative(card, strict):
    old_selector = load(EV / "selector_result.json")
    selector = load(EV / "strict_selector_result.json")
    assert card["verdict"] == "PROMOTE"
    assert card["gates"]["literal_rule_exception_applied"] is True
    assert old_selector["verdict"] == "candidate_approved_by_automated_gates"
    assert old_selector["ok_to_submit"] is True

    assert strict["prior_decision_preserved"] is True
    assert strict["historical_source_run_card"] == "evidence/hk3/run_card.json"
    assert strict["historical_selector_decision"] == "evidence/hk3/selector_result.json"
    assert strict["verdict"] == "negative"
    assert strict["current_disposition"] == "DO NOT SUBMIT; research-only download"
    assert strict["gates"]["unique_literal_vs_all_registry_rasters"] is False
    assert strict["gates"]["literal_rule_exception_applied"] is False
    assert strict["gates"]["registry_inventory_complete"] is False
    assert strict["gates"]["preplacement_surface_registry_audit_present"] is False
    assert strict["gates"]["strict_format_pass"] is False
    assert strict["gates"]["official_exterior_null_nan_pass"] is False
    assert strict["gates"]["assigned_method_lane_documented"] is False
    assert strict["gates"]["experiment_limit_3_respected"] is True
    assert strict["gates"]["two_hour_limit_respected"] is False
    assert selector["verdict"] == "negative"
    assert selector["ok_to_download_for_research"] is True
    assert selector["ok_to_submit"] is False and selector["slot_authorized"] is False
    assert selector["source_run_card"] == "evidence/hk3/strict_disposition.json"


def test_strict_literal_registry_rule_includes_degenerate_and_unsubmitted_entries(strict):
    registry = strict["registry_uniqueness"]
    u2 = registry["tiers"]["U2_literal_rule_vs_all_registry_rasters"]
    assert u2["pass"] is False
    assert u2["rasters_checked"] == 452
    assert len(u2["failures"]) == 5
    assert "degenerate_excluded" not in u2
    assert registry["registry_rasters_expected"] == 453
    assert registry["registry_rasters_checked"] == 452
    assert registry["missing_or_invalid"] == 1
    assert registry["complete_registry_inventory"] is False
    assert registry["preplacement_surface_audit_present"] is False
    lattice = [r for r in u2["failures"] if "r13-lattice" in r["submission"]]
    assert len(lattice) == 2  # two registry references to the same TIFF bytes
    assert all(r["overlap_3px"] == pytest.approx(0.9986255209718897) for r in lattice)
    assert all(r["overlap_3px"] > 0.70 for r in u2["failures"])
    assert registry["literal_rule_exception_applied"] is False
    assert registry["literal_rule_policy"].startswith("Every registry raster is in scope")


def test_historical_holdout_numbers_are_labelled_and_estimate_is_not_a_score(card):
    h = card["holdout"]
    assert h["evidence_class"] == "HOLDOUT-DTI"
    assert h["evaluator_version"] == "gems57-pooled-hide-v2"
    assert h["withheld_positive_pixels"] == 58258
    d = h["paired_differences"]["cand34_b110_minus_inc26_b110"]
    assert d["ci95"][0] > 0 and d["delta"] > 0
    assert h["candidate_same_budget_as_incumbent_b110"]["dti"] > h["incumbent_refit_b110"]["dti"]
    assert h["canary_all_pass"] and max(h["canary_max_auc_by_feature"].values()) < 0.90
    est = card["estimator"]
    assert est["evidence_class"].startswith("LEADERBOARD-CALIBRATED ESTIMATE")
    assert "NOT ORGANIZER-CONFIRMED" in est["evidence_class"]
    assert est["estimate_theta"]["0.00"] < est["estimate_theta"]["0.50"] < est["estimate_theta"]["0.75"] < est["estimate_theta"]["1.00"]
    assert est["estimate"] == pytest.approx(est["estimate_theta"]["1.00"], abs=2e-5)


def test_saved_raster_is_hash_bound_and_exterior_failure_is_explicit(card, strict):
    tif = ROOT / card["raster"]["file"]
    assert tif.exists()
    sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    assert sha == card["raster"]["sha256"] == strict["raster"]["sha256"]
    with rasterio.open(tif) as src:
        assert src.count == 1 and src.dtypes[0] == "float32"
        assert (src.height, src.width) == (3730, 3292)
        assert src.crs.to_epsg() == 32611
        assert list(tuple(src.transform)[:6]) == card["raster"]["example_submission_profile"]["transform"]
        arr = src.read(1)
    assert np.isfinite(arr).all() and arr.min() >= 0.0 and arr.max() <= 1.0
    assert int((arr > 0).sum()) == card["raster"]["dots"] == 45108
    assert set(np.unique(arr)).issubset({0.0, 1.0})
    strict_receipt = load(EV / "validate_tif_strict.json")
    assert strict_receipt["candidate_sha256"] == sha
    assert strict_receipt["checks"]["outside_is_nan"] is False
    assert strict_receipt["strict_format_pass"] is False
    assert strict_receipt["upload_authorized"] is False
    assert strict["strict_review"]["official_exterior_requirement"].startswith("null/NaN")
    assert strict["strict_review"]["saved_exterior"] == "zero-valued finite pixels"

    import zipfile
    with zipfile.ZipFile(ROOT / card["raster"]["zip"]) as archive:
        names = archive.namelist()
        assert names == [tif.name]
        assert hashlib.sha256(archive.read(names[0])).hexdigest() == sha


def test_historical_shared_validator_pass_is_not_promoted_to_strict_format_clearance(card, strict):
    sys.path.insert(0, str(ROOT))
    from vendor.gems57 import validate
    report = validate.validate(ROOT / card["raster"]["file"])
    assert all(report["checks"].values()), report["checks"]
    assert report["sha256"] == card["raster"]["sha256"]
    assert all(card["validator"]["shared_gems57"]["checks"].values())
    assert strict["gates"]["format_shared_validator_pass"] is True
    assert strict["gates"]["strict_format_pass"] is False


def test_current_research_note_is_not_an_upload_note(card, strict):
    old = card["submission"]
    current = strict["submission"]
    assert len(old["note"]) <= 140 and old["note_chars"] == len(old["note"])
    assert Path(card["raster"]["file"]).name == old["name"] + ".tif"
    assert current["name"] == old["name"]
    assert current["status"] == "NOT AUTHORIZED FOR SUBMISSION"
    assert current["note"].startswith("Research only")
    assert current["note_chars"] == len(current["note"]) <= 140
    assert current["prior_proposed_note"] == old["note"]


def test_desk_pages_use_current_negative_disposition_and_research_only_download(strict):
    subprocess.run([sys.executable, str(ROOT / "scripts/build_hk3_pages.py"), "--check"], check=True, cwd=ROOT)
    for name in ("index.html", "executive-summary.html", "how-to-submit.html", "submit.html"):
        page = (DOCS / name).read_text()
        assert "{BADGE" not in page
        assert "OK TO SUBMIT: YES" not in page
        if name in ("index.html", "executive-summary.html", "how-to-submit.html"):
            assert strict["raster"]["sha256"] in page
        downloads = re.findall(r'<a[^>]*href="([^"]+)"[^>]*\sdownload[\s>]', page)
        for href in downloads:
            assert strict["submission"]["name"] in href
            assert (DOCS / href).exists()
    home = (DOCS / "index.html").read_text()
    assert "DO NOT SUBMIT" in home and "RESEARCH ONLY" in home
    assert "HOLDOUT-DTI" in home and "LEADERBOARD-CALIBRATED ESTIMATE" in home
    assert "No complete-inventory certificate" in home
    assert "outside_is_nan: false" in home and "strict_format_pass: false" in home
    assert "Literal-rule exception applied: <b>no</b>" in home
    assert "drivendata.org/competitions/306/competition-doe-gems/page/967/" in home
    assert "historically says PROMOTE" in home

    howto = (DOCS / "how-to-submit.html").read_text()
    assert "There are no upload instructions" in howto
    assert "No weekly slot has been used or authorized" in howto
    assert "Sign in" not in howto and "Upload the TIF" not in howto


def test_current_literal_failure_records_and_percentages_are_visible(strict):
    home = (DOCS / "index.html").read_text()
    failures = strict["registry_uniqueness"]["tiers"]["U2_literal_rule_vs_all_registry_rasters"]["failures"]
    assert len(failures) == 5
    for row in failures:
        assert Path(row["submission"]).name in home
        assert f"{row['overlap_3px'] * 100:.1f}%" in home
    assert "no exception" in home.lower()


def test_current_leaderboard_observation_is_not_a_receipt():
    obs = load(ROOT / "evidence/public_leaderboard_observation_2026-10-28.json")
    assert obs["observed_rank"] == 1 and obs["observed_score"] == pytest.approx(0.4544)
    assert "not a submission-page receipt" in obs["evidence_class"]
    page = (DOCS / "index.html").read_text()
    assert "Official public leaderboard observation" in page
    assert "not a receipt" in page and "not a score for this repository's raster" in page

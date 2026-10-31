"""Independent negative HK3 decision, saved bytes and fail-closed publication.

Mirror-dependent replays are skipped if the small hash-pinned inputs have not been
bootstrapped. No test trains a model, writes a GeoTIFF or uses a submission slot.
"""
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
import zipfile

import numpy as np
import pytest
import rasterio

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "evidence" / "hk3"
DOCS = ROOT / "docs"


def load(path):
    return json.loads(Path(path).read_text())


@pytest.fixture(scope="module")
def card():
    return load(EV / "run_card.json")


def test_evidence_is_published_identically(card):
    for name in ("run_card.json", "selector_result.json", "literal_recheck.json",
                 "decision_correction.json", "e2.json", "bridge.json", "e3_generation.json",
                 "registry_audit.json", "anchors_out_of_sample.json", "leakage_inflation.json",
                 "validate_tif_strict.json"):
        assert load(EV / name) == load(DOCS / "evidence" / "hk3" / name), name


def test_registry_stop_and_previous_unsafe_exception_are_not_promoted(card):
    g = card["gates"]
    sel = load(EV / "selector_result.json")
    receipt = load(EV / "literal_recheck.json")
    assert card["verdict"] == sel["verdict"] == receipt["verdict"] == "negative"
    assert g["unique_literal_vs_all_registry_rasters"] is False
    assert g["literal_rule_exception_applied"] is False
    assert g["assigned_lane_verified"] is False and g["registry_complete"] is False
    assert card["registry_uniqueness"]["complete_accessible_scan"] is False
    assert card["registry_uniqueness"]["preplacement_clearance_verified"] is False
    assert receipt["matched_within_3_pixels"] == 45046
    assert receipt["candidate_positive_inside_footprint"] == 45108
    assert receipt["overlap_fraction"] == pytest.approx(45046 / 45108)
    assert receipt["full_footprint_spearman_vs_lattice"] == pytest.approx(0.000317637408, abs=1e-12)
    assert 10 * receipt["matched_within_3_pixels"] > 7 * receipt["candidate_positive_inside_footprint"]
    assert receipt["duplicate_stop"] is True
    assert receipt["preplacement_surface_rechecked"] is False
    assert receipt["organizer_inputs_authenticated"] is False
    assert receipt["portal_acceptance"] is None
    assert sel["ok_to_submit"] is False and sel["slot_authorized"] is False
    assert "WITHDRAWN" in card["estimator"]["status"]
    assert "NOT AUTHORIZED" in card["submission"]["status"]


def test_this_session_card_does_not_invent_candidate_evidence():
    path = ROOT / "evidence/2026-10-28-independent-audit-run-card.json"
    session = load(path)
    assert session == load(DOCS / "evidence/2026-10-28-independent-audit-run-card.json")
    for key in ("holdout_dti", "holdout_confidence_interval_95", "registry_correlation",
                "registry_overlap_3px", "raster_sha256", "format_validator_results",
                "submission_name", "note", "leaderboard_estimate", "organizer_receipt"):
        assert session[key] is None
    assert session["experiments_run"] == session["new_tiffs_created"] == session["submission_slots_used"] == 0
    assert session["verdict"] == "negative" and session["slot_authorized"] is False
    historical = session["historical_hk3_witness"]
    receipt = load(EV / "literal_recheck.json")
    assert historical["raster_sha256"] == receipt["candidate_sha256"]
    assert historical["lattice_overlap_3px"] == receipt["overlap_fraction"]
    assert historical["lattice_rank_correlation"] == receipt["full_footprint_spearman_vs_lattice"]


def test_independent_recheck_when_pinned_mirrors_are_available():
    if not (ROOT / ".cache/research/inputs/lattice.tif").is_file():
        pytest.skip("run scripts/bootstrap_research.py to restore the small owner mirrors")
    subprocess.run([sys.executable, "scripts/recheck_hk3.py", "--check"], cwd=ROOT, check=True, timeout=120)


def test_prior_holdout_is_labelled_not_a_candidate_score(card):
    h = card["holdout"]
    assert h["evidence_class"] == "HOLDOUT-DTI"
    assert h["evaluator_version"] == "gems57-pooled-hide-v2"
    assert h["withheld_positive_pixels"] == 58258
    recorded = h["candidate_same_budget_as_incumbent_b110"]
    assert recorded["ci95"][0] <= recorded["dti"] <= recorded["ci95"][1]
    d = h["paired_differences"]["cand34_b110_minus_inc26_b110"]
    assert d["ci95"][0] > 0 and d["delta"] > 0  # vs K2, NOT an HK3-vs-K3 paired test
    # Only the eight new bands were tested; a 34-feature gate cannot be called passed.
    assert len(h["canary_max_auc_by_feature"]) == 8
    assert h["canary_eight_new_features_all_pass"] is True
    assert max(h["canary_max_auc_by_feature"].values()) < 0.90
    assert h["canary_all_pass"] is False and card["gates"]["leakage_canary_pass"] is False


def test_published_research_raster_hash_grid_range_and_zip(card):
    tif = ROOT / card["raster"]["file"]
    assert hashlib.sha256(tif.read_bytes()).hexdigest() == card["raster"]["sha256"]
    with rasterio.open(tif) as src:
        assert src.count == 1 and src.dtypes[0] == "float32"
        assert (src.height, src.width) == (3730, 3292)
        assert src.crs.to_epsg() == 32611
        assert list(src.transform)[:6] == card["raster"]["example_submission_profile"]["transform"]
        arr = src.read(1)
    assert np.isfinite(arr).all() and arr.min() >= 0.0 and arr.max() <= 1.0
    assert int((arr > 0).sum()) == card["raster"]["dots"] == 45108
    with zipfile.ZipFile(ROOT / card["raster"]["zip"]) as z:
        assert z.namelist() == [tif.name]
        assert hashlib.sha256(z.read(tif.name)).hexdigest() == card["raster"]["sha256"]
    metadata = load(tif.with_suffix(".json"))
    assert metadata["sha256"] == card["raster"]["sha256"]
    assert metadata["ok_to_submit"] is False and metadata["promoted"] is False
    assert "DO NOT SUBMIT" in metadata["status"]
    assert "WITHDRAWN" in metadata["metadata"]["estimator"]["status"]
    assert len(card["submission"]["note"]) <= 140  # historical, not a proposed new upload


def test_shared_validator_is_only_a_local_format_check(card):
    from vendor.gems57 import validate
    report = validate.validate(ROOT / card["raster"]["file"])
    assert all(report["checks"].values()), report["checks"]
    assert report["sha256"] == card["raster"]["sha256"]
    assert load(EV / "literal_recheck.json")["organizer_inputs_authenticated"] is False


def test_retired_cli_and_direct_entry_points_never_write(card):
    from scripts import hk3
    files = [ROOT / card["raster"]["file"], EV / "registry_audit.json", EV / "run_card.json"]
    before = [hashlib.sha256(p.read_bytes()).digest() for p in files]
    for cmd in (hk3.cmd_features, hk3.cmd_e2, hk3.cmd_bridge, hk3.cmd_e3,
                hk3.cmd_audit, hk3.cmd_anchors, hk3.cmd_card, hk3.emit):
        with pytest.raises(RuntimeError, match="BLOCKED"):
            cmd()
    run = subprocess.run([sys.executable, "scripts/hk3.py", "e3"], cwd=ROOT,
                         text=True, capture_output=True, timeout=30)
    assert run.returncode != 0 and "BLOCKED" in run.stderr
    assert before == [hashlib.sha256(p.read_bytes()).digest() for p in files]


def test_desk_pages_are_explicitly_research_only(card):
    subprocess.run([sys.executable, "scripts/build_hk3_pages.py", "--check"], check=True, cwd=ROOT)
    for name in ("index.html", "executive-summary.html", "how-to-submit.html", "submit.html"):
        page = (DOCS / name).read_text()
        release = json.loads((ROOT / "evidence/halo/final_generation.json").read_text())
        expected = ("OK TO SUBMIT: 1 FILE · SEE RELEASE" if release["verdict"]["ok_to_submit"]
                    else "OK TO SUBMIT: NO")
        assert expected in page
        assert "DO NOT SUBMIT" in page and "RESEARCH ONLY" in page
        assert card["raster"]["sha256"] in page
        downloads = re.findall(r'<a[^>]*href="([^"]+)"[^>]*\sdownload[\s>]', page)
        # The HK3 research file is always offered; the verified current candidate
        # banner (submission desk, evidence/k10) may add its own download links.
        hk3_links = [d for d in downloads
                     if (DOCS / d).resolve() == (ROOT / card["raster"]["file"]).resolve()]
        assert len(hk3_links) == 1
        k10 = json.loads((ROOT / "evidence/k10/run_card.json").read_text())
        s1 = json.loads((ROOT / "evidence/s1/run_card.json").read_text())
        for d in downloads:
            assert (card["raster"]["file"].split("/")[-1] in d
                    or k10["submission_name"] in d or s1["submission"]["name"] in d
                    or "gemsdoekarage2-geo-habitat-dti-20261031" in d)
    home = (DOCS / "index.html").read_text()
    assert "HOLDOUT-DTI" in home and "Leaderboard estimate</th><td><b>Unavailable" in home
    assert "45,046 of 45,108" in home and "99.86%" in home
    assert "exception applied" not in home.lower()
    assert "drivendata.org/competitions/306/competition-doe-gems/page/967/" in home


def test_page_builder_refuses_a_forged_promote_card_or_selector(monkeypatch):
    from scripts import build_hk3_pages as builder
    original = builder.load

    def forged_card(path):
        data = copy.deepcopy(original(path))
        if path == builder.EV / "hk3/run_card.json":
            data["verdict"] = "PROMOTE"
            data["gates"]["unique_literal_vs_all_registry_rasters"] = True
        return data

    monkeypatch.setattr(builder, "load", forged_card)
    with pytest.raises(ValueError, match="negative literal-registry"):
        builder.gather()

    def forged_selector(path):
        data = copy.deepcopy(original(path))
        if path == builder.EV / "hk3/selector_result.json":
            data["ok_to_submit"] = True
        return data

    monkeypatch.setattr(builder, "load", forged_selector)
    with pytest.raises(ValueError, match="negative literal-registry"):
        builder.gather()

    def forged_witness(path):
        data = copy.deepcopy(original(path))
        if path == builder.EV / "hk3/literal_recheck.json":
            # Keep the boolean STOP but change the fraction shown to readers.
            data["overlap_fraction"] = 0.01
        return data

    monkeypatch.setattr(builder, "load", forged_witness)
    with pytest.raises(ValueError, match="witness counts"):
        builder.gather()

    def forged_assessment(path):
        data = copy.deepcopy(original(path))
        if path == builder.EV / "hk3/current_release_assessment.json":
            # Eight passing canaries must never be presented as the full gate.
            data["leakage_canary_passed"] = True
        return data

    monkeypatch.setattr(builder, "load", forged_assessment)
    with pytest.raises(ValueError, match="Current assessment"):
        builder.gather()

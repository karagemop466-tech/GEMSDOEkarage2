"""HK3 (edge-centrality lane) — run card, published bytes and page consistency.

Every assertion here is about the *saved* evidence; nothing is recomputed from
the feature stack, so the tests run without the cached data.
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


def load(path):
    return json.loads(Path(path).read_text())


@pytest.fixture(scope="module")
def card():
    return load(EV / "run_card.json")


def test_run_card_is_published_identically(card):
    for name in ("run_card.json", "e2.json", "bridge.json", "e3_generation.json",
                 "registry_audit.json", "anchors_out_of_sample.json", "leakage_inflation.json",
                 "validate_tif_strict.json"):
        assert load(EV / name) == load(DOCS / "evidence" / "hk3" / name), name


def test_run_card_gates_and_verdict_logic_agree(card):
    g = card["gates"]
    required = ["format_shared_validator_pass", "grid_matches_example_submission",
                "whole_array_finite_in_0_1", "no_dots_on_mapped_catalogue", "leakage_canary_pass",
                "holdout_beats_refit_incumbent_paired_ci_excludes_zero", "unique_vs_nine_scored_site_files",
                "unique_chance_corrected_vs_all_registry_rasters", "unique_literal_vs_submitted_dot_rasters",
                "rank_correlation_below_0_90", "lane_single_method"]
    assert all(g[k] is True for k in required), {k: g[k] for k in required}
    # the literal all-registry rule is the one disclosed deviation; it must be
    # visible as a failed gate without an exception, never silently passed
    assert g["unique_literal_vs_all_registry_rasters"] is False
    assert g["literal_rule_exception_applied"] is False
    assert card["verdict"] == "NEGATIVE"
    assert card["protocol_stop_triggered"] is True
    tiers = card["registry_uniqueness"]["tiers"]
    assert tiers["U1_unique_vs_nine_scored_site_files"]["pass"] and tiers["U1_unique_vs_nine_scored_site_files"]["max_overlap"] <= 0.70
    assert not tiers["U2_literal_rule_vs_all_registry_rasters"]["pass"]
    assert tiers["U3_chance_corrected_overlap_vs_all"]["pass"] and tiers["U3_chance_corrected_overlap_vs_all"]["max_corrected"] <= 0.70
    assert tiers["U4_literal_rule_vs_dot_rasters_that_were_submitted"]["pass"]
    # every literal failure is annotated with a submission status (owner-reported or never submitted)
    for row in tiers["U2_literal_rule_vs_all_registry_rasters"]["failures"]:
        assert row["overlap_3px"] > 0.70 and row["submission_status"]
    assert card["registry_uniqueness"]["tiers"]["rank_correlation"]["pass"]
    assert card["registry_uniqueness"]["worst_abs_rho"] < 0.90


def test_holdout_numbers_are_labelled_and_paired_delta_excludes_zero(card):
    h = card["holdout"]
    assert h["evidence_class"] == "HOLDOUT-DTI"
    assert h["evaluator_version"] and h["withheld_positive_pixels"] > 0
    d = h["paired_differences"]["cand34_b110_minus_inc26_b110"]
    assert d["ci95"][0] > 0 and d["delta"] > 0
    assert h["candidate_same_budget_as_incumbent_b110"]["dti"] > h["incumbent_refit_b110"]["dti"]
    assert h["canary_all_pass"] and max(h["canary_max_auc_by_feature"].values()) < 0.90
    # the estimate carries its own label and must never be presented as a score
    est = card["estimator"]
    assert est["evidence_class"].startswith("LEADERBOARD-CALIBRATED ESTIMATE")
    assert "NOT ORGANIZER-CONFIRMED" in est["evidence_class"]
    assert est["estimate_theta"]["0.00"] < est["estimate_theta"]["0.50"] < est["estimate_theta"]["0.75"] < est["estimate_theta"]["1.00"]
    assert est["estimate"] == pytest.approx(est["estimate_theta"]["1.00"], abs=2e-5)  # rounding of the printed table
    assert est["estimate_if_no_better_than_anchor"] <= est["estimate_theta"]["0.00"]  # pessimistic floor below the family baseline


def test_published_raster_matches_run_card_and_is_in_range(card):
    tif = ROOT / card["raster"]["file"]
    assert tif.exists()
    assert hashlib.sha256(tif.read_bytes()).hexdigest() == card["raster"]["sha256"]
    with rasterio.open(tif) as src:
        assert src.count == 1 and src.dtypes[0] == "float32"
        assert (src.height, src.width) == (3730, 3292)
        assert src.crs.to_epsg() == 32611
        assert list(tuple(src.transform)[:6]) == card["example_submission_profile"]["transform"] if "example_submission_profile" in card else True
        assert list(tuple(src.transform)[:6]) == card["raster"]["example_submission_profile"]["transform"]
        arr = src.read(1)
    assert np.isfinite(arr).all() and arr.min() >= 0.0 and arr.max() <= 1.0
    assert int((arr > 0).sum()) == card["raster"]["dots"] == 45108
    assert set(np.unique(arr)).issubset({0.0, 1.0})
    # zip wraps the same bytes
    import zipfile
    with zipfile.ZipFile(ROOT / card["raster"]["zip"]) as z:
        names = z.namelist()
        assert names == [tif.name]
        assert hashlib.sha256(z.read(names[0])).hexdigest() == card["raster"]["sha256"]


def test_submission_note_fits_portal_limit(card):
    s = card["submission"]
    assert len(s["note"]) <= 140 and s["note_chars"] == len(s["note"])
    assert "gemsdoekarage2-hk3" in s["name"]
    assert Path(card["raster"]["file"]).name == s["name"] + ".tif"


def test_shared_validator_passes_on_the_published_bytes(card):
    sys.path.insert(0, str(ROOT))
    from vendor.gems57 import validate  # shared tool, pinned
    report = validate.validate(ROOT / card["raster"]["file"])
    assert all(report["checks"].values()), report["checks"]
    assert report["sha256"] == card["raster"]["sha256"]
    assert all(card["validator"]["shared_gems57"]["checks"].values())


def test_desk_pages_are_generated_from_the_run_card(card):
    subprocess.run([sys.executable, str(ROOT / "scripts/build_hk3_pages.py"), "--check"], check=True, cwd=ROOT)
    for name in ("index.html", "executive-summary.html", "how-to-submit.html", "submit.html"):
        page = (DOCS / name).read_text()
        assert "{BADGE" not in page
        assert ("OK TO SUBMIT: YES" in page) == (card["verdict"] == "PROMOTE")
        if name in ("index.html", "how-to-submit.html"):
            assert card["raster"]["sha256"] in page
        downloads = re.findall(r'<a[^>]*href="([^"]+)"[^>]*\sdownload[\s>]', page)
        for href in downloads:
            assert card["submission"]["name"] in href
            assert (DOCS / href).exists()
    home = (DOCS / "index.html").read_text()
    assert "HOLDOUT-DTI" in home and "LEADERBOARD-CALIBRATED ESTIMATE" in home
    assert "ORGANIZER-CONFIRMED" in home  # the label the page says it does *not* have
    assert 'Literal 70 % rule vs all 450 non-degenerate registry rasters:</b> <b class="no">FAIL' in home
    assert "drivendata.org/competitions/306/competition-doe-gems/page/967/" in home


def test_literal_failures_on_the_desk_match_the_card(card):
    home = (DOCS / "index.html").read_text()
    for row in card["registry_uniqueness"]["tiers"]["U2_literal_rule_vs_all_registry_rasters"]["failures"]:
        assert Path(row["submission"]).name in home
        assert f"{row['overlap_3px'] * 100:.1f}%" in home


def test_publication_policy_rejects_waivers_and_incomplete_gates(card):
    from copy import deepcopy
    from scripts.hk3_release_policy import publication_eligible, REQUIRED_GATES
    assert not publication_eligible(card)
    clean = dict(verdict="PROMOTE", protocol_stop_triggered=False,
                 gates={key: True for key in REQUIRED_GATES})
    clean["gates"]["literal_rule_exception_applied"] = False
    assert publication_eligible(clean)  # necessary schema checks, not slot authorization
    for key in REQUIRED_GATES:
        for bad in (None, False, 1, "true", [], {}):
            changed = deepcopy(clean)
            changed["gates"][key] = bad
            assert not publication_eligible(changed), (key, bad)
        changed = deepcopy(clean)
        del changed["gates"][key]
        assert not publication_eligible(changed)
    for key, value in (("protocol_stop_triggered", True), ("verdict", "NEGATIVE")):
        assert not publication_eligible(dict(clean, **{key: value}))
    waived = deepcopy(clean)
    waived["gates"]["literal_rule_exception_applied"] = True
    assert not publication_eligible(waived)


def test_negative_pages_never_offer_an_approved_download():
    for name in ("index.html", "executive-summary.html", "how-to-submit.html", "submit.html"):
        page = (DOCS / name).read_text()
        assert "OK TO SUBMIT: NO" in page
        assert "Download the approved TIF" not in page
        assert "Binding duplicate stop: DO NOT SUBMIT" in page or "NO APPROVED FILE" in page

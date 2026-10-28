"""K2 session (2026-10-28) artifact tests: run-card/raster/evidence consistency.

These tests certify internal consistency of committed receipts only. They do
not re-run the holdout (needs the restored 419 MB feature mirror) and never
authorize a competition slot.
"""
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
K2 = ROOT / "evidence" / "k2"
TIF = ROOT / "docs/downloads/gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif"


def load(p):
    return json.loads(Path(p).read_text(),
                      parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))


def test_k2_run_card_matches_raster_bytes():
    c = load(K2 / "run_card.json")
    assert hashlib.sha256(TIF.read_bytes()).hexdigest() == c["raster_sha256"]
    assert TIF.stat().st_size == c["raster_bytes"]
    assert len(c["note"]) <= 140 and len(c["submission_name"]) <= 140
    assert c["experiments_run"] == 3 and c["submission_slots_used"] == 0
    assert c["verdict"] == "negative"
    assert "OK TO SUBMIT: NO" in c["download_policy"]
    audit = load(K2 / "final_registry_audit.json")
    assert audit["verdict"] == "negative" and audit["stop_required"] is True
    assert "literal protocol" in c["verdict_scope"]
    with zipfile.ZipFile(TIF.with_suffix(".zip")) as z:
        assert z.namelist() == [TIF.name]
        assert z.read(TIF.name) == TIF.read_bytes()
    receipt = load(TIF.with_suffix(".json"))
    assert receipt["sha256"] == c["raster_sha256"]
    assert receipt["validator"]["all_checks_passed"] is True
    assert receipt["approved_for_weekly_slot"] is False  # writer never self-approves


def test_k2_raster_format_and_range():
    with rasterio.open(TIF) as ds:
        a = ds.read(1)
        assert ds.count == 1 and ds.dtypes[0] == "float32"
        assert (ds.height, ds.width) == (3730, 3292)
        assert ds.crs.to_epsg() == 32611
        assert tuple(ds.transform)[:6] == (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
    assert np.isfinite(a).all() and a.min() >= 0.0 and a.max() <= 1.0
    c = load(K2 / "run_card.json")
    assert int((a > 0).sum()) == c["dots"] == 54491


def test_k2_holdout_candidate_beats_primitives_and_canaries_pass():
    h = load(K2 / "combined_holdout.json")
    s = h["scores"]
    assert h["evaluator_version"] if "evaluator_version" in h else True
    cand = s["hgbcont_b110"]
    assert cand["evidence_class"] == "HOLDOUT-DTI"
    assert cand["withheld_positive_pixels"] == 58258
    for prim in ("prim_ridge_coh", "prim_elev_grad", "prim_grav_grad"):
        assert cand["dti"] > s[prim]["dti"]
    d = h["paired_differences"]["prim_ridge_coh"]
    assert d["ci95"][0] > 0  # paired win vs best primitive
    e1 = load(K2 / "e1.json")
    assert e1["canary_all_pass"] is True
    assert max(e1["worst_canary_by_feature"].values()) <= 0.90


def test_k2_uniqueness_scopes_are_as_reported():
    a = load(K2 / "final_registry_audit.json")
    rows = a["rows"]
    errors = [r for r in rows if "error" in r]
    assert len(errors) == 1 and "FORMAT_TEST" in errors[0]["submission"]
    submission_rows = [r for r in rows if "error" not in r
                       and "inputs/calibration" not in (r.get("submission") or "")
                       and r.get("repo") != "13GEMSDOE"]
    assert submission_rows, "no submission-scope rows"
    assert max(r["my_dots_within_3px_of_theirs"] for r in submission_rows) <= 0.70
    assert max(abs(r["spearman_full_footprint"]) for r in submission_rows
               if r["spearman_full_footprint"] is not None) <= 0.90
    flagged = [r for r in rows if r.get("duplicate_by_overlap") or r.get("duplicate_by_rho")]
    # Literal-scope failures are exactly the lattice (x2 copies) + ctx-ridge calibration mask.
    assert len(flagged) == 3
    assert all(("lattice" in (r["submission"] or "")) or ("ctx-ridge" in (r["submission"] or ""))
               for r in flagged)
    delta = load(K2 / "final_registry_audit_delta.json")
    assert delta["duplicate_count"] == 0


def test_homepage_marks_k2_as_negative_research_only():
    home = (ROOT / "docs" / "index.html").read_text()
    assert "gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif" in home
    assert "NEGATIVE" in home and "DO NOT SUBMIT" in home
    assert "NO APPROVED SUBMISSION" in home
    assert "504be4587e3bec7b81f802b4c16b6c546c683e8a4c8b514d3a9856c6e0698dfb" in home
    assert "72.0523%" in home and "100%" in home

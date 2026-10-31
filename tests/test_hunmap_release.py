"""H-UNMAP lane (2026-10-31) release tests.

These tests certify the committed receipts and the published bytes only.  They
do not retrain a model, do not spend a competition slot and do not convert a
projection into a score.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EV = ROOT / "evidence" / "hunmap"


def load(name: str) -> dict:
    return json.loads((EV / name).read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_release_card_is_hash_bound_to_the_published_bytes():
    card = load("e3-release-card.json")
    tif = ROOT / card["raster"]["file"]
    assert tif.is_file() and tif.parent.name == "submission"
    assert digest(tif) == card["raster"]["sha256"]
    assert 0 < len(card["note"]) <= 140
    assert card["note_chars"] == len(card["note"])
    assert card["submission_name"].startswith("gemsdoekarage2-hunmap-")
    assert card["validator"]["checks"] and all(card["validator"]["checks"].values())
    assert card["validator"]["n_nan"] == 0 and card["validator"]["n_infinite"] == 0
    assert card["validator"]["min"] >= 0.0 and card["validator"]["max"] <= 1.0


def test_published_raster_is_a_finite_0_1_single_band_geoTIFF():
    card = load("e3-release-card.json")
    with rasterio.open(ROOT / card["raster"]["file"]) as ds:
        arr = ds.read(1)
        assert ds.count == 1 and ds.dtypes[0] == "float32"
        assert str(ds.crs) == "EPSG:32611"
        assert list(ds.shape) == [3730, 3292]
        assert list(ds.transform)[:6] == [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0]
    assert np.isfinite(arr).all()
    assert arr.min() >= 0.0 and arr.max() <= 1.0
    assert int((arr > 0).sum()) == card["raster"]["dots"]


def test_candidate_audit_is_verified_and_does_not_authorise_a_slot():
    audit = load("e3-candidate-audit.json")
    assert audit["status"] == "VERIFIED_CANDIDATE"
    assert all(audit["checks"].values())
    assert audit["ok_to_submit_by_this_project"] is False
    assert audit["slot_authorized"] is False
    assert audit["organizer_confirmed_score"] is None
    assert audit["holdout"]["evidence_class"] == "HOLDOUT-DTI"


def test_uniqueness_verdict_is_measured_and_not_assumed():
    verdict = load("hunmap-uniqueness-verdict.json")
    subs = verdict["submissions"]
    assert subs["verdict"] == "unique_vs_submissions"
    assert subs["max_overlap_fraction"] <= 0.70
    assert abs(subs["max_spearman"]) <= 0.90
    assert subs["count"] >= 400
    lattice = load("lattice-rule-calibration.json")
    # The calibration lattice is a regular 500 m grid: its 3 px halo covers the
    # footprint, so the candidate must not exceed a random dot set of the same size.
    assert lattice["candidate"]["lattice_overlap"] <= lattice["null_model"]["max_overlap"]


def test_holdout_and_projection_carry_their_evidence_class():
    holdout = load("e1-blocked-holdout.json")
    assert holdout["evidence_class"] == "HOLDOUT-DTI"
    policy = next(r for r in holdout["rows"] if r["radius_px"] == 2
                  and r["budget"] == 60000 and r["apron_px"] == 2)
    assert policy["blocked_pooled_dti"] > 0.09539  # the published champion on the same instrument
    cal = load("leaderboard_calibration.json")
    assert cal["evidence_class"].startswith("PROJECTION")
    cand = cal["candidates"][0]
    assert cand["projected_95pi"][0] < cand["projected_score"] < cand["projected_95pi"][1]


def test_leakage_canary_passes_and_is_disclosed():
    canary = load("e2-train-canary.json")
    assert canary["leakage_canary_pass"] is True
    assert canary["max_auc"] <= canary["gate_auc"]


def test_submission_page_offers_one_clear_download_and_labels_the_gates():
    page = (DOCS / "submission.html").read_text()
    card = load("e3-release-card.json")
    assert "OK TO DOWNLOAD AND SUBMIT" in page
    assert card["submission_name"] in page and card["note"] in page
    downloads = re.findall(r'<a[^>]*href="([^"]+)"[^>]*\sdownload[\s>]', page)
    assert len(downloads) == 2
    for href in downloads:
        assert (DOCS / href).is_file()
    assert "Predicted values must be in range [0, 1]" in page
    assert "HOLDOUT-DTI" in page and "PROJECTION" in page
    assert "DRIVEN DATA" not in page  # no invented organiser claim
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert site in page
    assert "DO NOT SUBMIT" in page  # the nine historical files stay blocked


def test_nine_site_rows_are_never_published_as_a_submission():
    page = (DOCS / "submission.html").read_text()
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert f"https://buffedlizard55-lab.github.io/{site}/docs/index.html" in page

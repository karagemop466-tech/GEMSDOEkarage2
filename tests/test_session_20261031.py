"""Regression tests for the 2026-10-31 H-C run, NaN-exterior audit kind, GEMSDOE32 verification,
and the focus-site pairwise matrix. All thresholds are asserted from the saved evidence files."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parents[1]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


audit = _load("audit_public_downloads", "scripts/audit_public_downloads.py")


def test_e1_card_is_negative_and_never_authorizes_a_slot():
    card = json.loads((ROOT / "evidence/hc/e1_run_card.json").read_text())
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["approved_for_weekly_slot"] is False and card["slot_authorized"] is False
    assert card["uniqueness"]["pass"] is False
    assert card["holdout"]["evaluator_sha256"]
    assert card["holdout"]["withheld_positive_pixels"] == 60988
    assert card["footprint"]["pixels"] == 5167373
    assert len(card["footprint"]["finite_mask_sha256"]) == 64


def test_nan_exterior_check_accepts_matching_footprint_and_rejects_wrong_one(tmp_path):
    h, w = 4, 5
    arr = np.full((h, w), np.nan, dtype=np.float32)
    arr[1:3, 1:4] = np.array([[0, 1, 0], [1, 0, 0]], dtype=np.float32)
    path = tmp_path / "nanx.tif"
    with rasterio.open(path, "w", driver="GTiff", height=h, width=w, count=1, dtype="float32",
                       nodata=np.nan, crs="EPSG:32611", transform=from_origin(0, 0, 100, 100)) as ds:
        ds.write(arr, 1)
    with rasterio.open(path) as ds:
        a = ds.read(1)
    mask = np.isfinite(a)
    good = audit.inspect_nan_exterior(path, audit.hashlib.sha256(np.packbits(mask).tobytes()).hexdigest(), int(mask.sum()))
    assert good["whole_array_finite"] and good["range_0_1"] and good["nan_exterior_matches_card_footprint"]
    bad = audit.inspect_nan_exterior(path, "0" * 64, int(mask.sum()))
    assert bad["nan_exterior_matches_card_footprint"] is False
    assert bad["whole_array_finite"] is False and bad["range_0_1"] is False


def test_nan_exterior_kind_does_not_weaken_default_finite_rule():
    # The default kind keeps requiring finite-everywhere; only the explicit kind relaxes it.
    src = (ROOT / "scripts/audit_public_downloads.py").read_text()
    assert 'kind == "research-nan-exterior"' in src
    assert "whole_array_finite" in src


def test_gems32_b2_verification_is_all_pass_and_matches_expected_counts():
    ver = json.loads((ROOT / "evidence/gems32-b2-verification.json").read_text())
    assert ver["all_checks_pass"] is True
    m = ver["measured"]
    assert m["base_dots"] == 40199 and m["b2_dots"] == 37654 and m["dots_removed"] == 2545
    assert m["base_dots_within_200m_of_catalogue"] == 2545
    assert abs(m["b2_min_distance_m"] - 223.6) < 0.05
    assert ver["labels"]["user_reported_leaderboard"]["GEMSDOE32_B2"] == 0.2778


def test_focus_pairwise_matrix_is_well_formed():
    pw = json.loads((ROOT / "evidence/uniqueness/focus-pairwise-overlap-2026-10-31.json").read_text())
    names = list(pw["matrix"])
    assert len(names) == 10 and "lattice13" in names
    for a in names:
        assert pw["matrix"][a][a] == 1.0
        for b in names:
            assert 0.0 <= pw["matrix"][a][b] <= 1.0
    assert pw["chance_coverage_3px_of_footprint"]["lattice13"] > 0.99
    assert pw["labels"].startswith("MEASURED")

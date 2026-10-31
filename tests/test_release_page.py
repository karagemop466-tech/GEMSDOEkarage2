"""Release-page and score-model consistency tests.

These tests never touch a network or the (git-ignored) competition cache.  They
check three things:

1. `docs/release.html` is regenerable from the committed receipts (no hand-typed
   numbers) and every relative link resolves to a published file.
2. The released GeoTIFF on disk matches its receipt: grid, dtype, range,
   finiteness, positive-cell count and SHA-256.
3. The score algebra in `scripts/score_model.py` round-trips the published
   numbers (the inversion that drives the whole decision).
"""

from __future__ import annotations

import hashlib
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

import numpy as np
import pytest
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_release_page  # noqa: E402
import score_model  # noqa: E402

REPO_RECEIPT = ROOT / "evidence" / "halo" / "final_generation.json"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.downloads: list[str] = []
        self.text: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
            if "download" in a:
                self.downloads.append(a["href"])

    def handle_data(self, data):
        self.text.append(data)


def test_release_page_is_regenerated_from_receipts_not_hand_typed():
    """`--check` fails if the committed page differs from the generated one."""
    page = ROOT / "docs" / "release.html"
    assert page.is_file()
    assert page.read_text() == build_release_page.build(), (
        "docs/release.html is stale: run python scripts/build_release_page.py")


def test_release_page_links_resolve_and_offer_the_released_file():
    parser = PageParser()
    parser.feed((ROOT / "docs" / "release.html").read_text())
    receipt = json.loads(REPO_RECEIPT.read_text())
    expected = f"downloads/{Path(receipt['submission_file']).name}"
    assert parser.downloads, "the page must offer a one-click download"
    assert set(parser.downloads) == {expected}
    for href in parser.links:
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        if href.startswith("#"):
            assert href[1:] in parser.ids
            continue
        target = (ROOT / "docs" / href.split("#")[0]).resolve()
        assert target.is_file(), href


def test_release_page_labels_are_explicit():
    text = (ROOT / "docs" / "release.html").read_text()
    for label in ("CALIBRATED-PRIVATE", "HOLDOUT-DTI", "USER-REPORTED / UNVERIFIED",
                  "not a receipt", "OK TO DOWNLOAD AND SUBMIT"):
        assert label in text, label
    # the projection must never be presented as an organizer-confirmed score
    assert "ORGANIZER-CONFIRMED score" not in text.replace("is not ORGANIZER-CONFIRMED", "")


def test_released_tiff_matches_its_receipt_and_is_submission_shaped():
    receipt = json.loads(REPO_RECEIPT.read_text())
    tif = ROOT / receipt["submission_file"]
    assert tif.is_file(), "the released raster must be committed for one-click download"
    assert sha256_file(tif) == receipt["format_checks"]["sha256"]
    with rasterio.open(tif) as ds:
        assert ds.count == 1
        assert str(ds.dtypes[0]) == "float32"
        assert (ds.height, ds.width) == (3730, 3292)
        assert str(ds.crs) == "EPSG:32611"
        assert [round(v, 6) for v in tuple(ds.transform)[:6]] == [
            100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0]
        arr = ds.read(1)
    assert np.isfinite(arr).all(), "no NaN anywhere: NaN is the likeliest cause of the portal range error"
    assert arr.min() >= 0.0 and arr.max() <= 1.0
    assert int((arr > 0).sum()) == receipt["generation"]["dots_emitted"]
    verdict = receipt["verdict"]
    assert verdict["format_valid"] and verdict["unique_vs_submission_rasters"]
    assert verdict["ok_to_submit"] is True
    # a slot is never consumed by a script
    assert "slot_authorized" not in receipt
    assert len(receipt["submission_note"]) <= 140


def test_uniqueness_receipt_is_inside_the_literal_thresholds():
    receipt = json.loads(REPO_RECEIPT.read_text())
    u = receipt["uniqueness"]
    assert u["worst_dot_overlap"] <= 0.70
    assert abs(u["worst_spearman"]) <= 0.90
    assert u["rasters_above_0_70_overlap"] == []
    assert u["rasters_above_0_90_rho"] == []
    assert u["submission_rasters_compared"] > 400
    # probes are reported, never silently used as clearance
    assert u["universal_probes"], "the lattice probe must be reported separately"
    assert u["probe_note"].startswith("r13_lattice is a uniform 5-px sampling probe")


MODEL = json.loads((ROOT / "evidence" / "score_model.json").read_text())


def test_score_model_round_trips_the_published_numbers():
    G = MODEL["hidden_truth"]["G_px"]                  # px, from the r13 lattice probe
    K = MODEL["credits_per_hit"]["value"]              # credits per hit dot
    K = MODEL["credits_per_hit"]["value"]
    for n, score in ((37654, 0.2778), (44090, 0.2600), (60069, 0.2477)):
        inv = score_model.invert_hit_rate(score, n, G, K)
        assert inv["reproduced_dti"] == pytest.approx(score, abs=1e-9)
        assert 0.0 < inv["hit_rate"] < 0.2
        # the marginal bar is a HIT RATE: h* = aT / (K(aF + bG) + aT).
        bar = score_model.marginal_hit_rate_bar(inv["T_truth_credit"],
                                               inv["F_false_positive_mass"], G, K)
        assert 0.005 < bar < 0.02
        # ... and every published file's dots are still profitable against it
        assert inv["hit_rate"] > bar


def test_projection_is_monotone_and_saturates_at_the_truth_size():
    G = MODEL["hidden_truth"]["G_px"]
    prev = -1.0
    for h in (0.01, 0.02, 0.03, 0.04, 0.05):
        p = score_model.project(44090, h, G)
        assert p["projected_dti"] > prev
        prev = p["projected_dti"]
    saturated = score_model.project(44090, 1.0, G)
    assert saturated["T"] == pytest.approx(G)
    assert saturated["projected_dti"] < 1.0


def test_break_even_hit_rate_matches_a_forward_projection():
    G = MODEL["hidden_truth"]["G_px"]
    for target in (0.2778, 0.4544):
        be = score_model.break_even_hit_rate(target, 44090, G)
        assert be["reachable"]
        forward = score_model.project(44090, be["hit_rate_needed"], G)
        assert forward["projected_dti"] == pytest.approx(target, rel=1e-6)


def test_marginal_bar_is_a_hit_rate_not_a_credit_bar():
    """Regression: alpha*DTI is a credit-unit bar and must never be compared with h."""
    G = MODEL["hidden_truth"]["G_px"]
    K = MODEL["credits_per_hit"]["value"]
    rec = MODEL["files"]["GEMSDOE32"]
    assert "marginal_bar_alpha_dti" not in rec
    assert rec["legacy_alpha_dti_bar_retired"]["value"] == pytest.approx(score_model.ALPHA * 0.2778)
    bar = rec["marginal_hit_rate_bar"]
    assert bar == pytest.approx(score_model.marginal_hit_rate_bar(
        rec["T_truth_credit"], rec["F_false_positive_mass"], G, K))
    # the two conventions differ by exactly the credit per hit dot
    assert rec["legacy_alpha_dti_bar_retired"]["value"] / bar == pytest.approx(K, rel=0.06)
    assert rec["dots_are_profitable"] is True
    assert 1.5 < rec["budget_headroom_x"] < 3.0
    assert 80_000 < rec["dots_at_constant_precision_optimum"] < 140_000


def test_every_published_field_is_inside_its_budget_optimum():
    for key, rec in MODEL["files"].items():
        if key == "r13_lattice":
            continue
        assert rec["dots"] < rec["dots_at_constant_precision_optimum"], key


def test_adding_a_profitable_dot_never_lowers_the_score():
    """The bar is the exact sign change of the metric, so a dot above it must help."""
    G = MODEL["hidden_truth"]["G_px"]
    K = MODEL["credits_per_hit"]["value"]
    T, F, n = 5073.0, 36615.0, 37654
    bar = score_model.marginal_hit_rate_bar(T, F, G, K)
    before = score_model.dti(T, F, G)
    for h in (bar * 1.01, bar * 1.5, bar * 2.0):
        after = score_model.dti(T + K * h, F + 1 - h, G)
        assert after > before
    assert score_model.dti(T + K * bar, F + 1 - bar, G) == pytest.approx(before, abs=1e-9)


def test_directed_overlap_receipt_names_the_closest_published_field():
    """The 473-raster snapshot went stale; the receipt must track files published since."""
    new = json.loads((ROOT / "evidence/halo/overlap-vs-published.json").read_text())
    assert new == json.loads((ROOT / "docs/evidence/halo/overlap-vs-published.json").read_text())
    rel = json.loads((ROOT / "evidence/halo/final_generation.json").read_text())
    assert new["release"]["sha256"] == rel["format_checks"]["sha256"]
    assert new["release"]["dots"] == rel["generation"]["dots_emitted"]
    worst = new["worst_directed_overlap"]
    assert worst["fraction"] < 0.70, worst
    # every row is a saved file on disk with a hash
    for row in new["rows"]:
        path = ROOT / row["file"]
        assert path.is_file(), row["file"]
        assert len(row["sha256"]) == 64
    # the reverse direction is recorded, and never used to excuse the forward one
    assert new["worst_reverse_overlap"]["fraction"] >= worst["fraction"]
    assert new["verdict"] == "PASS"

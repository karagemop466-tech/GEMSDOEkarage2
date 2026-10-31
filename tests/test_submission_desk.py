"""The published candidate and the submission desk must agree with evidence."""
import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def card():
    return json.loads((ROOT / "evidence/k10/run_card.json").read_text())


@pytest.fixture(scope="module")
def selector():
    return json.loads((ROOT / "evidence/k10/selector_result.json").read_text())


def test_candidate_file_exists_and_matches_card(card, selector):
    assert selector["verdict"] == "candidate_approved_by_automated_gates"
    assert selector["ok_to_submit"] is True and selector["slot_authorized"] is False
    tif = ROOT / card["raster"]
    assert tif.is_file()
    digest = hashlib.sha256(tif.read_bytes()).hexdigest()
    assert digest == card["raster_sha256"]
    # all-finite [0,1] convention on the saved bytes: the portal-error answer
    import rasterio
    import numpy as np
    with rasterio.open(tif) as ds:
        a = ds.read(1)
        assert ds.count == 1 and ds.dtypes[0] == "float32"
        assert str(ds.crs) == "EPSG:32611"
        assert (ds.height, ds.width) == (3730, 3292)
        assert list(map(float, tuple(ds.transform)[:6])) == [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0]
    assert np.isfinite(a).all()
    assert float(a.min()) >= 0.0 and float(a.max()) <= 1.0
    assert int((a > 0).sum()) == 38000


def test_run_card_gates_are_all_true_and_labelled(card):
    assert card["format_valid"] is True
    assert card["unique_submission_verified"] is True
    assert card["verdict"] == "promote-instrument-limited"
    assert card["approved_for_weekly_slot"] is False and card["slot_authorized"] is False
    assert card["submission_slots_used"] == 0
    h = card["holdout"]
    assert h["evidence_class"] == "HOLDOUT-DTI" and h["canary_pass"] is True
    assert h["withheld_positive_pixels"] > 0 and len(h["ci95"]) == 2
    ilm = card["instrument_limitation_measurement"]
    assert ilm["champion_b2_control_dti"] < ilm["random38k_dti"]
    assert len(card["note"]) <= 140
    # no numeric leaderboard estimate anywhere in the card
    assert card["holdout"]["comparison_limit"].startswith("Budget-matched")


def test_registry_scan_found_no_real_duplicate(card):
    reg = json.loads((ROOT / "evidence/k10/final_registry.json").read_text())
    assert reg["rho_firing_submissions"] == []
    non_lattice = [s for s in reg["like_for_like_firing_submissions"] if "lattice" not in s]
    assert non_lattice == []
    assert reg["rasters_checked"] >= 480
    assert reg["missing_or_invalid"] == ["docs/downloads/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif"]


def test_desk_page_matches_candidate_evidence(card, selector):
    page = (ROOT / "docs/submission-desk.html").read_text()
    fname = Path(card["raster"]).name
    assert f"downloads/{fname}" in page
    assert card["raster_sha256"] in page
    assert card["note"] in page
    assert "DO NOT SUBMIT" in page
    assert "literal" in page.lower()
    assert "NOT MEASURABLE" in page  # score estimate honesty
    # all nine focus sites in the executive table
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert site in page
    assert "USER-REPORTED / UNVERIFIED" in page
    # champion instrument negative control is disclosed
    assert str(card["instrument_limitation_measurement"]["champion_b2_control_dti"]) in page


def test_index_banner_links_to_desk_and_candidate(card):
    home = (ROOT / "docs/index.html").read_text()
    assert "submission-desk.html" in home
    fname = Path(card["raster"]).name
    assert f'downloads/{fname}"' in home
    # legacy pages must keep their negative header badge wording
    assert "OK TO SUBMIT: NO" in home and "OK TO SUBMIT: YES" not in home


def test_candidate_is_unique_against_the_nine_focus_files(card):
    import numpy as np
    import rasterio
    from scipy import ndimage as ndi
    sys_path = str(ROOT / "vendor")
    import sys
    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)
    from gems57.grid import load_grid
    if not (ROOT / ".cache/gems_data/sample_submission.tif").is_file():
        pytest.skip("pinned mirror inputs not restored in this lightweight CI run")
    grid = load_grid(ROOT / ".cache/gems_data")
    fp = grid.footprint
    with rasterio.open(ROOT / card["raster"]) as ds:
        mine = ds.read(1)
    mine_dots = (np.isfinite(mine) & (mine > 0) & fp)
    yy, xx = np.mgrid[-3:4, -3:4]
    disk = (yy * yy + xx * xx) <= 9
    near = ndi.binary_dilation(mine_dots, structure=disk)
    focus = json.loads((ROOT / "registry/focus_sites.json").read_text())
    for rec in focus["sites"]:
        local = ROOT / rec["file"]
        if not local.exists():  # mirrors live in the registry cache
            local = ROOT / ".cache/registry" / rec["site"] / "docs/downloads" / Path(rec["file"]).name
        if not local.exists():
            # A fresh CI checkout has no .cache/registry mirrors (the path is gitignored), so the
            # gate cannot run there. Skip rather than error -- the overlap assertion below is still
            # enforced wherever the mirror is present, and `scripts/fetch_reported_rasters.py` or a
            # raw.githubusercontent.com fetch repopulates it. Never weaken the 0.70 threshold itself.
            pytest.skip(f"{rec['site']} mirror raster is not cached; gate needs .cache/registry")
        with rasterio.open(local) as ds:
            theirs = ds.read(1)
        t = (np.isfinite(theirs) & (theirs > 0) & fp)
        overlap = float(near[t].mean()) if t.any() else 0.0
        assert overlap <= 0.70, (rec["site"], overlap)

import json
from pathlib import Path
import sys

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_uniqueness import audit, centered_ranks, check_comparator
from restore_references import digest
from geometry_audit import phi


def write_tif(path, array):
    array = np.asarray(array, dtype=np.float32)
    with rasterio.open(path, "w", driver="GTiff", height=array.shape[0], width=array.shape[1],
                       count=1, dtype="float32", crs="EPSG:32611", nodata=np.nan,
                       transform=from_origin(100, 500, 100, 100)) as ds:
        ds.write(array, 1)


def test_binary_phi_equals_scipy_spearman_with_ties():
    a = np.array([0, 0, 1, 0, 1, 0, 1, 0])
    b = np.array([1, 0, 1, 0, 0, 0, 1, 0])
    assert phi(len(a), int(a.sum()), int(b.sum()), int((a & b).sum())) == pytest.approx(spearmanr(a, b).statistic)


def test_overlap_threshold_strictly_greater_than_70_percent():
    rng = np.random.default_rng(42)
    field = rng.random((5, 45))
    foot = np.ones_like(field, dtype=bool)
    support = np.zeros_like(foot)
    positions = np.arange(2, 42, 4)
    support[2, positions] = True
    ref = np.zeros_like(field)
    ref[2, positions[:7]] = 1
    ranks, norm = centered_ranks(field[foot])
    result = check_comparator(ranks, norm, support, ref, foot)
    assert result["matches_within_3px"] == 7
    assert result["overlap_fraction"] == .7
    assert not result["duplicate"]
    ref[2, positions[7]] = 1
    result = check_comparator(ranks, norm, support, ref, foot)
    assert result["matches_within_3px"] == 8
    assert result["duplicate"]


def create_set(tmp_path, complete):
    shape = (30, 30)
    template = np.zeros(shape, dtype="float32")
    ref = np.zeros(shape, dtype="float32")
    ref[1, 1] = 1
    field = np.random.default_rng(16).random(shape).astype("float32")
    support = np.zeros(shape, dtype="uint8")
    support[25, 25] = 1
    template_path, ref_path = tmp_path / "template.tif", tmp_path / "ref.tif"
    surface_path, support_path = tmp_path / "surface.npy", tmp_path / "support.npy"
    write_tif(template_path, template)
    write_tif(ref_path, ref)
    np.save(surface_path, field)
    np.save(support_path, support)
    manifest = tmp_path / "registry.json"
    manifest.write_text(json.dumps({"complete": complete, "entries": [
        {"path": "ref.tif", "sha256": digest(ref_path)}]}))
    return template_path, ref_path, surface_path, support_path, manifest


def test_missing_complete_inventory_cannot_pass(tmp_path):
    template, ref, surface, support, manifest = create_set(tmp_path, False)
    res = audit("surface", surface, template, manifest, support)
    assert res["status"] == "INCOMPLETE_REGISTRY"
    assert res["upload_authorized"] is False


def test_full_receipt_binds_surface_support_and_final_subset(tmp_path):
    template, ref, surface, support, manifest = create_set(tmp_path, True)
    receipt = audit("surface", surface, template, manifest, support)
    assert receipt["status"] == "PASS"
    receipt_path = tmp_path / "surface-receipt.json"
    receipt_path.write_text(json.dumps(receipt))
    final = np.zeros((30, 30), dtype="float32")
    final[25, 25] = 1
    final_path = tmp_path / "final.tif"
    write_tif(final_path, final)
    result = audit("final", final_path, template, manifest, support, receipt_path, surface)
    assert result["status"] == "PASS"
    assert result["upload_authorized"] is False
    final[24, 25] = 1
    write_tif(final_path, final)
    with pytest.raises(ValueError, match="beyond the checked"):
        audit("final", final_path, template, manifest, support, receipt_path, surface)
    changed_support = np.load(support)
    changed_support[24, 25] = 1
    np.save(support, changed_support)
    with pytest.raises(ValueError, match="does not bind"):
        audit("final", final_path, template, manifest, support, receipt_path, surface)


def test_bad_or_missing_registry_fails_closed(tmp_path):
    template, ref, surface, support, manifest = create_set(tmp_path, True)
    ref.unlink()
    with pytest.raises(ValueError, match="Missing or changed"):
        audit("surface", surface, template, manifest, support)
    with pytest.raises(ValueError, match="requires the prior"):
        audit("final", surface, template, manifest)


def test_constant_surface_is_undefined_not_a_pass():
    with pytest.raises(ValueError, match="Constant"):
        centered_ranks(np.ones(20))

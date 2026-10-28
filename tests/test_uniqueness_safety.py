import json
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_uniqueness import audit, centered_ranks, check_comparator
from test_uniqueness import create_set, write_tif


def test_negative_correlation_does_not_meet_positive_threshold():
    ref = np.zeros((1, 20), dtype=float)
    ref[0, :5] = 1
    field = 1 - ref
    foot = np.ones_like(ref, dtype=bool)
    support = np.zeros_like(foot)
    support[0, 10:] = True
    ranks, norm = centered_ranks(field[foot])
    comparison = check_comparator(ranks, norm, support, ref, foot)
    assert comparison["spearman_full_footprint"] == pytest.approx(-1)
    assert comparison["overlap_fraction"] == 0
    assert comparison["duplicate"] is False


def test_forged_passing_receipt_cannot_skip_surface_reaudit(tmp_path):
    template, ref, surface, support, manifest = create_set(tmp_path, True)
    duplicate_surface = np.zeros((30, 30), dtype="float32")
    duplicate_surface[1, 1] = 1
    np.save(surface, duplicate_surface)
    receipt = audit("surface", surface, template, manifest, support)
    assert receipt["status"] == "DUPLICATE_STOP"
    receipt["status"] = "PASS"  # The metadata and hashes still match.
    receipt_path = tmp_path / "forged.json"
    receipt_path.write_text(json.dumps(receipt))
    final = np.zeros((30, 30), dtype="float32")
    final[25, 25] = 1
    final_path = tmp_path / "final.tif"
    write_tif(final_path, final)
    with pytest.raises(ValueError, match="surface fails re-audit"):
        audit("final", final_path, template, manifest, support, receipt_path, surface)


@pytest.mark.parametrize("which", ["template", "reference"])
def test_novelty_rejects_unhashed_external_mask(tmp_path, which):
    import rasterio
    template, ref, surface, support, manifest = create_set(tmp_path, True)
    target = template if which == "template" else ref
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=False):
        with rasterio.open(target, "r+") as ds:
            ds.write_mask(np.ones(ds.shape, dtype="uint8") * 255)
    assert Path(str(target) + ".msk").exists()
    with pytest.raises(ValueError, match="external companion"):
        audit("surface", surface, template, manifest, support)

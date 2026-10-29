"""Hide-and-recover holdout: the builder must never receive withheld segments."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_holdout import make_quadrant_folds, pooled_dti_hide_and_recover, withhold_segments  # noqa: E402


def _toy():
    H, W = 60, 80
    gt = np.zeros((H, W), dtype=bool)
    gt[10:50, 20] = True          # segment in NW/SW boundary
    gt[5:12, 60] = True           # short segment in NE
    gt[40, 5:75] = True           # long horizontal segment crossing blocks
    return H, W, gt, make_quadrant_folds(H, W)


def test_builder_never_sees_withheld_pixels():
    H, W, gt, folds = _toy()
    seen = []

    def builder(visible, i):
        withheld, vis_expected, _ = withhold_segments(gt, folds[i], 3.0)
        seen.append((i, bool((visible & withheld).any()), np.array_equal(visible, vis_expected)))
        return np.zeros((H, W))

    pooled_dti_hide_and_recover(builder, gt, folds)
    assert len(seen) == 4
    for _, touched_withheld, equals_visible in seen:
        assert not touched_withheld
        assert equals_visible


def test_oracle_visible_only_prediction_scores_lower_than_full_catalogue_leak():
    """An apron prediction built from the full catalogue (leak) scores higher than the same
    rule applied on visible faults only: the holdout must expose the difference."""
    from scipy import ndimage

    H, W, gt, folds = _toy()

    def apron(mask):
        d = ndimage.distance_transform_edt(~mask)
        p = np.zeros((H, W))
        p[(d > 0.5) & (d <= 3.0)] = 1.0
        return p

    leak = pooled_dti_hide_and_recover(lambda vis, i: apron(gt), gt, folds)
    honest = pooled_dti_hide_and_recover(lambda vis, i: apron(vis), gt, folds)
    assert leak["pooled_DTI"] > honest["pooled_DTI"]
    assert honest["protocol"].startswith("hide-and-recover")
    assert honest["n_withheld_total"] == leak["n_withheld_total"] > 0


def test_shape_mismatch_fails_closed():
    H, W, gt, folds = _toy()
    try:
        pooled_dti_hide_and_recover(lambda vis, i: np.zeros((H + 1, W)), gt, folds)
    except ValueError:
        return
    raise AssertionError("shape mismatch was accepted")

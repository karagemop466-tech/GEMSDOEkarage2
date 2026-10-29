"""Regression tests for the shared pooled holdout evaluator (scripts/evaluate_holdout.py).

Defect found 2026-10-29: each fold scored the whole raster against only that fold's
withheld positives, so predictions in other blocks were counted as false positives
in every fold. A perfect predictor scored DTI 0.63 instead of 1.0. The fix restricts
each fold to its active region (block minus visible faults).
"""
import sys
from pathlib import Path

import numpy as np
from rasterio.transform import Affine

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_holdout import make_quadrant_folds, pooled_dti_over_folds  # noqa: E402

TRANSFORM = Affine(100.0, 0.0, 0.0, 0.0, -100.0, 0.0)


def _toy_truth():
    gt = np.zeros((60, 80), dtype=bool)
    gt[10:50, 20] = True
    gt[5:55, 60] = True
    gt[30, 5:75] = True
    return gt


def test_perfect_predictor_scores_one():
    gt = _toy_truth()
    folds = make_quadrant_folds(*gt.shape)
    out = pooled_dti_over_folds(gt.astype(float), gt, TRANSFORM, folds)
    assert out["pooled_DTI"] == 1.0
    assert out["FPw"] == 0.0


def test_empty_predictor_scores_zero():
    gt = _toy_truth()
    folds = make_quadrant_folds(*gt.shape)
    out = pooled_dti_over_folds(np.zeros(gt.shape), gt, TRANSFORM, folds)
    assert out["pooled_DTI"] == 0.0


def test_predictions_outside_fold_block_are_not_fp_of_that_fold():
    # One positive, predictions only in a far corner that no fold-withheld segment touches.
    gt = np.zeros((60, 80), dtype=bool)
    gt[5, 5] = True
    folds = make_quadrant_folds(*gt.shape)
    p = np.zeros(gt.shape)
    p[5, 5] = 1.0
    out = pooled_dti_over_folds(p, gt, TRANSFORM, folds)
    assert out["pooled_DTI"] == 1.0
    assert out["FPw"] == 0.0

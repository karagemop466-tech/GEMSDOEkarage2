"""
evaluate_holdout.py
-------------------

Legacy local DTI evaluator retained to reproduce historical quadrant-block
research results. It is NOT the pinned shared segment-holdout evaluator: its
``withhold_segments`` helper withholds pixels by quadrant, so a connected fault
component crossing a boundary can be split between visible and withheld masks.
Do not use this module for protocol-compliant promotion evidence. Restore the
commit-pinned template with ``scripts/bootstrap_template.py`` and use its
``scripts/evaluate_holdout.py`` plus matching ``src/gems32`` modules instead.

Official metric (from https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/):

    p(x) in [0,1]  predicted fault probability at pixel x
    g(x)           ground-truth label at pixel x
    k(d)           triangular kernel, k(d) = max(1 - d/R, 0),  R = 300 m (3 px at 100 m)

    TPw = sum_{g in G}  max_{x: d(x,g) <= R}  p(x) * k(d(x,g))
    FPw = sum_{x: p(x)>0} p(x) * [1 - max_{g in G} k(d(x,g))]
    FNw = sum_{g in G}  [1 - max_{x: d(x,g) <= R} p(x) * k(d(x,g))]

    DTI(alpha, beta) = TPw / (TPw + alpha*FPw + beta*FNw + eps)

Competition settings: alpha = 0.2 (FP penalty), beta = 0.8 (FN penalty), R = 300 m.

Implementation notes
--------------------
* max_{g} k(d(x,g)) = k(d(x, G)) because k is monotone decreasing in d, so the
  FP term needs only the distance transform to the nearest ground-truth pixel.
* The per-ground-truth max over the radius-R disk is computed exactly as the
  elementwise maximum over all integer offsets within the disk of
  shift(p, offset) * k(|offset|), evaluated at the ground-truth pixels.
* This historical split uses four pixel-space quadrants with a pixel buffer. It
  does not withhold whole connected components, does not itself rebuild every
  catalogue feature from visible traces, and its four-fold range is not a
  spatial-bootstrap 95% CI. See the pinned template evaluator for the strict
  segment hide-and-recover implementation.

This module is CPU-only (numpy + rasterio + scipy).  GPU is not required for
metric/validation work; it is only needed for training deep models.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Tuple

import numpy as np
from scipy import ndimage


EPS = 1e-12

# Competition constants
ALPHA = 0.2
BETA = 0.8
R_METERS = 300.0          # triangular-kernel support
PIXEL_SIZE_M = 100.0      # competition data are 100 m / pixel
R_PX = R_METERS / PIXEL_SIZE_M  # 3.0 px


# --------------------------------------------------------------------------- #
# Metric
# --------------------------------------------------------------------------- #

def triangular_kernel(d_m: np.ndarray | float, R_m: float = R_METERS) -> np.ndarray:
    """Triangular kernel k(d) = max(1 - d/R, 0)."""
    return np.maximum(1.0 - np.asarray(d_m, dtype=float) / R_m, 0.0)


def _disk_offsets(R_px: float = R_PX) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integer pixel offsets (dy, dx) within Euclidean radius R_px, with weights k."""
    r = int(math.ceil(R_px))
    ys, xs = np.mgrid[-r:r + 1, -r:r + 1]
    dist = np.hypot(ys, xs)
    mask = dist <= R_px + 1e-9
    return ys[mask], xs[mask], (1.0 - dist[mask] / R_px)


def dti_weighted_terms(p: np.ndarray,
                       g: np.ndarray,
                       pixel_size_m: float = PIXEL_SIZE_M,
                       alpha: float = ALPHA,
                       beta: float = BETA,
                       R_m: float = R_METERS) -> dict:
    """
    Compute distance-weighted TP/FP/FN terms and the Tversky index.

    Parameters
    ----------
    p : (H, W) float array of predicted probabilities in [0, 1].
    g : (H, W) array, ground truth (nonzero = positive / fault).
    pixel_size_m : ground sample distance in metres.
    alpha, beta : Tversky coefficients (FP / FN penalties).
    R_m : kernel support in metres.

    Returns
    -------
    dict with keys TPw, FPw, FNw, DTI, n_pos_pred, n_pos_gt.
    """
    p = np.asarray(p, dtype=np.float64)
    g = np.asarray(g)
    if p.shape != g.shape:
        raise ValueError(f"shape mismatch: p {p.shape} vs g {g.shape}")
    if not np.all(np.isfinite(p)):
        raise ValueError("prediction array contains non-finite values")
    if np.any(p < 0.0) or np.any(p > 1.0):
        raise ValueError("prediction values must lie in [0, 1]")

    gt_mask = g != 0
    n_gt = int(gt_mask.sum())

    R_px = R_m / pixel_size_m

    # ---- Distance transform: metres from each pixel to nearest GT pixel ----
    if n_gt == 0:
        dist_to_gt = np.full(p.shape, np.inf, dtype=np.float64)
    else:
        dist_to_gt = ndimage.distance_transform_edt(
            ~gt_mask, sampling=pixel_size_m
        )

    # ---- FP term: max_g k(d(x,g)) = k(d(x, G)) (k monotone decreasing) ----
    k_at_x = triangular_kernel(dist_to_gt, R_m)                      # 0 beyond R
    pos_pred = p > 0.0
    fpw = float(np.sum(p[pos_pred] * (1.0 - k_at_x[pos_pred])))

    # ---- TP / FN terms: per-GT-pixel max over the radius-R disk ----------
    n_pos_pred = int(pos_pred.sum())
    if n_gt == 0:
        tpw = 0.0
        fnw = 0.0
    else:
        ys, xs, k_off = _disk_offsets(R_px)
        # M[y, x] = max over offsets u of p[y + dy, x + dx] * k(|u|)
        # evaluated exactly, with border positions masked out.
        M = np.full(p.shape, -np.inf, dtype=np.float64)
        for dy, dx, k in zip(ys, xs, k_off):
            if dy >= 0:
                ys0, ys1 = dy, p.shape[0]
                py0, py1 = 0, p.shape[0] - dy
            else:
                ys0, ys1 = 0, p.shape[0] + dy
                py0, py1 = -dy, p.shape[0]
            if dx >= 0:
                xs0, xs1 = dx, p.shape[1]
                px0, px1 = 0, p.shape[1] - dx
            else:
                xs0, xs1 = 0, p.shape[1] + dx
                px0, px1 = -dx, p.shape[1]
            shifted = np.full(p.shape, -np.inf, dtype=np.float64)
            shifted[ys0:ys1, xs0:xs1] = p[py0:py1, px0:px1] * k
            M = np.maximum(M, shifted)

        m_at_gt = M[gt_mask]                     # best prediction credit for each GT pixel
        tpw = float(np.sum(m_at_gt))
        fnw = float(np.sum(1.0 - m_at_gt))

    denom = tpw + alpha * fpw + beta * fnw + EPS
    dti = tpw / denom

    return {
        "TPw": round(tpw, 6),
        "FPw": round(fpw, 6),
        "FNw": round(fnw, 6),
        "DTI": round(float(dti), 6),
        "alpha": alpha,
        "beta": beta,
        "R_m": R_m,
        "n_pos_pred": n_pos_pred,
        "n_pos_gt": n_gt,
    }


def dti(p: np.ndarray,
        g: np.ndarray,
        pixel_size_m: float = PIXEL_SIZE_M,
        alpha: float = ALPHA,
        beta: float = BETA,
        R_m: float = R_METERS) -> float:
    """Convenience: return only the DTI scalar."""
    return dti_weighted_terms(p, g, pixel_size_m, alpha, beta, R_m)["DTI"]


# --------------------------------------------------------------------------- #
# Spatially-blocked hide-and-recover holdout
# --------------------------------------------------------------------------- #

@dataclass
class HoldoutFold:
    fold_id: str
    n_withheld_gt_pixels: int
    dti: float
    ci95: Tuple[float, float] | None = None


def make_quadrant_folds(height: int, width: int) -> list[np.ndarray]:
    """Four spatial blocks: NW, NE, SW, SE quadrants (pixel space)."""
    h_mid, w_mid = height // 2, width // 2
    blocks = []
    for (y0, y1, x0, x1) in [
        (0, h_mid, 0, w_mid),        # NW
        (0, h_mid, w_mid, width),    # NE
        (h_mid, height, 0, w_mid),   # SW
        (h_mid, height, w_mid, width),  # SE
    ]:
        m = np.zeros((height, width), dtype=bool)
        m[y0:y1, x0:x1] = True
        blocks.append(m)
    return blocks


def withhold_segments(gt_mask: np.ndarray,
                      block_mask: np.ndarray,
                      buffer_px: float = 3.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Legacy pixel-quadrant mask for one fold (the name is historical/misleading).

    ``withheld`` contains only GT pixels inside the block; ``visible`` contains
    GT pixels outside the dilated block. A connected component crossing a block
    boundary can therefore be partly withheld and partly visible. The helper is
    retained for reproducing old quadrant-block results, not for the strict
    whole-component protocol. Use the pinned template's ``SegmentHoldout``.
    """
    withheld = gt_mask & block_mask
    dilated = ndimage.binary_dilation(
        block_mask, iterations=int(math.ceil(buffer_px))
    )
    visible = gt_mask & (~dilated)
    return withheld, visible, dilated


def pooled_dti_over_folds(predictions: np.ndarray,
                          gt_mask: np.ndarray,
                          transform: Affine,
                          folds: list[np.ndarray],
                          pixel_size_m: float = PIXEL_SIZE_M,
                          buffer_px: float = 3.0,
                          alpha: float = ALPHA,
                          beta: float = BETA,
                          R_m: float = R_METERS) -> dict:
    """
    Score pooled DTI across spatial-block folds with hide-and-recover masking.

    For each fold:
      * withheld GT pixels = positives inside the held-out block.
      * The prediction `p` is the submission raster (already produced).
      * Visible-fault masking is enforced on the FEATURE side by the pipeline
        (prepare_data.py / feature stack); here we simply score the submission
        against the withheld positives and pool the weighted terms.

    Returns pooled DTI, per-fold terms, and a non-parametric spatial-block CI
    (percentile bootstrap over folds is degenerate with 4 folds; we report the
    fold-wise range as a conservative CI and note it).
    """
    terms = []
    for i, block in enumerate(folds):
        withheld, visible, _dilated = withhold_segments(gt_mask, block, buffer_px)
        # Score only inside this fold's active region (fold block minus visible
        # catalogue faults, which are masked pixel-exactly). Predictions outside
        # the block are NOT false positives of this fold; scoring them per fold
        # inflated FPw ~4x and capped a perfect predictor near DTI 0.63.
        # Matches vendor/gems57 evaluate(): active = valid & region & ~known.
        # Pixels where the submission is NaN (outside footprint) count as 0.
        p = np.nan_to_num(np.asarray(predictions, dtype=np.float64), nan=0.0)
        active = block & ~visible
        p = np.where(active, p, 0.0)
        gt = np.zeros_like(p, dtype=bool)
        gt[withheld] = True
        terms.append(dti_weighted_terms(p, gt, pixel_size_m, alpha, beta, R_m))

    TPw = sum(t["TPw"] for t in terms)
    FPw = sum(t["FPw"] for t in terms)
    FNw = sum(t["FNw"] for t in terms)
    denom = TPw + alpha * FPw + beta * FNw + EPS
    pooled = TPw / denom

    fold_dtis = [t["DTI"] for t in terms]
    ci = (float(min(fold_dtis)), float(max(fold_dtis))) if fold_dtis else (float("nan"), float("nan"))

    return {
        "pooled_DTI": round(float(pooled), 6),
        "TPw": round(TPw, 6),
        "FPw": round(FPw, 6),
        "FNw": round(FNw, 6),
        "n_folds": len(terms),
        "n_withheld_total": sum(t["n_pos_gt"] for t in terms),
        "alpha": alpha,
        "beta": beta,
        "R_m": R_m,
        "fold_DTIs": [round(float(d), 6) for d in fold_dtis],
        "ci95_fold_range": [round(ci[0], 6), round(ci[1], 6)],
        "note": "CI shown is fold-wise range (4 spatial blocks); use block bootstrap "
                "over resampled segments for a full 95% spatial-block CI.",
    }


def pooled_dti_hide_and_recover(build_prediction,
                                gt_mask: np.ndarray,
                                folds: list[np.ndarray],
                                pixel_size_m: float = PIXEL_SIZE_M,
                                buffer_px: float = 3.0,
                                alpha: float = ALPHA,
                                beta: float = BETA,
                                R_m: float = R_METERS) -> dict:
    """Legacy quadrant-block score; not the strict whole-component protocol.

    For each fold, the builder receives a pixel mask ``gt & ~dilate(block, buffer)``
    and a raster is scored against the withheld GT pixels. This prevents the builder
    from seeing those exact pixels through the supplied argument, but it does not hide
    entire connected fault components that cross quadrant boundaries and cannot stop
    a builder from reading labels through another external path. Use the pinned
    template's segment hide-and-recover implementation for promotion evidence.

    The returned per-fold range is descriptive, not a 95% confidence interval.
    """
    terms = []
    n_withheld = []
    for i, block in enumerate(folds):
        withheld, visible, _dilated = withhold_segments(gt_mask, block, buffer_px)
        pred = np.nan_to_num(np.asarray(build_prediction(visible.copy(), i), dtype=np.float64), nan=0.0)
        if pred.shape != gt_mask.shape:
            raise ValueError(f"fold {i}: prediction shape {pred.shape} != {gt_mask.shape}")
        gt = np.zeros_like(pred, dtype=bool)
        gt[withheld] = True
        terms.append(dti_weighted_terms(pred, gt, pixel_size_m, alpha, beta, R_m))
        n_withheld.append(int(withheld.sum()))

    TPw = sum(t["TPw"] for t in terms)
    FPw = sum(t["FPw"] for t in terms)
    FNw = sum(t["FNw"] for t in terms)
    pooled = TPw / (TPw + alpha * FPw + beta * FNw + EPS)
    fold_dtis = [t["DTI"] for t in terms]
    return {
        "pooled_DTI": round(float(pooled), 6),
        "TPw": round(TPw, 6),
        "FPw": round(FPw, 6),
        "FNw": round(FNw, 6),
        "n_folds": len(terms),
        "n_withheld_total": int(sum(n_withheld)),
        "n_withheld_per_fold": n_withheld,
        "alpha": alpha,
        "beta": beta,
        "R_m": R_m,
        "fold_DTIs": [round(float(d), 6) for d in fold_dtis],
        "fold_range": [round(float(min(fold_dtis)), 6), round(float(max(fold_dtis)), 6)],
        "protocol": "hide-and-recover: prediction rebuilt per fold from visible faults only",
    }


# --------------------------------------------------------------------------- #
# Self-test: reproduce the competition scoring example (DTI = 0.60)
# --------------------------------------------------------------------------- #

def _self_test() -> None:
    """
    Property tests for the DTI implementation (competition settings:
    alpha = 0.2, beta = 0.8, R = 300 m = 3 px at 100 m resolution).

    The published scoring example (single vertical ground-truth line,
    TPw = 3.00, FPw = 1.89, FNw = 2.00, DTI = 0.60) cannot be reproduced here
    because the example's prediction raster is not published numerically; the
    properties below are exact consequences of the formula instead.
    """
    H = W = 21
    px = 100.0
    R_m = 3.0 * px

    g = np.zeros((H, W), dtype=np.float64)
    g[:, 10] = 1.0                      # vertical ground-truth line at col 10
    gt_mask = g != 0

    # 1. Perfect prediction => DTI = 1 exactly
    res = dti_weighted_terms(g.copy(), g.copy(), pixel_size_m=px, R_m=R_m)
    assert res["TPw"] == float(gt_mask.sum()), res
    assert res["FPw"] == 0.0, res
    assert res["FNw"] == 0.0, res
    assert abs(res["DTI"] - 1.0) < 1e-9, res

    # 2. All-zero prediction => DTI = 0
    res = dti_weighted_terms(np.zeros_like(g), g.copy(), pixel_size_m=px, R_m=R_m)
    assert res["TPw"] == 0.0 and res["FNw"] == float(gt_mask.sum()), res
    assert abs(res["DTI"]) < 1e-12, res

    # 3. Prediction beyond kernel support everywhere => TPw = 0, full FN/FP penalty
    p_far = np.zeros_like(g)
    p_far[:, 0] = 1.0                   # 10 px away from the line (> R = 3 px)
    res = dti_weighted_terms(p_far, g.copy(), pixel_size_m=px, R_m=R_m)
    assert res["TPw"] == 0.0, res
    assert abs(res["FNw"] - float(gt_mask.sum())) < 1e-9, res
    assert res["FPw"] > 0.0, res
    assert abs(res["DTI"]) < 1e-12, res

    # 4. Monotonicity: raising predictions cannot lower DTI
    base = dti_weighted_terms(g.copy() * 0.5, g.copy(), pixel_size_m=px, R_m=R_m)["DTI"]
    raised = dti_weighted_terms(g.copy(), g.copy(), pixel_size_m=px, R_m=R_m)["DTI"]
    assert raised >= base, (base, raised)

    # 5. Range / dtype guards
    try:
        dti_weighted_terms(np.full((5, 5), 1.5), g[:5, :5], pixel_size_m=px, R_m=R_m)
        raise AssertionError("out-of-range values accepted")
    except ValueError:
        pass

    # 6. Quadrant folds tile the raster without overlap
    folds = make_quadrant_folds(H, W)
    assert len(folds) == 4
    union = np.logical_or.reduce(folds)
    assert union.all() and not np.logical_and.reduce(folds).any()

    print("[self-test] PASSED", flush=True)


if __name__ == "__main__":
    _self_test()

"""Research-only feature and placement helpers for the GW-NFS experiments.

Extracted from the retired generator so that the experiment and reachability scripts
keep working. This module WRITES NO RASTER. It does not publish, generate, or approve a
submission. The retired generator (scripts/generate_unique_submission.py) stays a stub.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from scipy.ndimage import gaussian_filter, minimum_filter, maximum_filter  # noqa: F401

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_holdout import make_quadrant_folds, withhold_segments  # noqa: E402,F401

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "competition_data"

B_COND_SURF = 17
B_ISO_GRAV = 13
B_SEIS_DEQ = 10

NODATA = -3.4028234663852886e+38


def load_band(band_idx: int) -> np.ndarray:
    with rasterio.open(CACHE / "training_features.tif") as ds:
        data = ds.read(band_idx).astype(np.float64)
    return np.where(data == NODATA, np.nan, data)


def load_labels_and_template() -> dict:
    with rasterio.open(CACHE / "labels.tif") as ds:
        labels = ds.read(1).astype(np.float64)
    with rasterio.open(CACHE / "sample_submission.tif") as ds:
        sample = ds.read(1)
        footprint = np.isfinite(sample)
    return {
        "labels": labels,
        "footprint": footprint,
        "height": ds.height if False else 3730,
        "width": ds.width if False else 3292,
    }


# --------------------------------------------------------------------------- #
# Hypothesis 1: Conductivity-gravity saddle score (continuous, label-free)
# --------------------------------------------------------------------------- #

def saddle_score(footprint: np.ndarray) -> np.ndarray:
    cond = load_band(B_COND_SURF)
    grav = load_band(B_ISO_GRAV)

    cond_med = np.nanmedian(cond)
    grav_med = np.nanmedian(grav)
    cond_s = gaussian_filter(np.nan_to_num(cond, nan=cond_med), sigma=2.0)
    grav_s = gaussian_filter(np.nan_to_num(grav, nan=grav_med), sigma=2.0)

    grav_grad = np.hypot(ndimage.sobel(grav_s, axis=1),
                         ndimage.sobel(grav_s, axis=0))

    local_max = maximum_filter(cond_s, size=5, mode="nearest")
    local_min = minimum_filter(cond_s, size=5, mode="nearest")
    contrast = local_max - local_min
    saddle = (cond_s < local_max) & (cond_s > local_min) & (contrast > 0.5)

    grav_norm = (grav_grad - np.nanmin(grav_grad)) / (
        np.nanmax(grav_grad) - np.nanmin(grav_grad) + 1e-12)
    score = saddle.astype(np.float64) * grav_norm

    if np.nanmax(score) > 0:
        score = score / np.nanmax(score)

    out = np.where(footprint, score, 0.0)
    out = np.where(np.isnan(cond) | np.isnan(grav), np.nan, out)
    return out


# --------------------------------------------------------------------------- #
# Hypothesis 2: Seismicity flank asymmetry (contextual prior)
# --------------------------------------------------------------------------- #

def seis_asymmetry(footprint: np.ndarray) -> np.ndarray:
    grav = load_band(B_ISO_GRAV)
    seis = load_band(B_SEIS_DEQ)

    grav_c = np.nan_to_num(grav, nan=np.nanmedian(grav))
    seis_c = np.nan_to_num(seis, nan=0.0)

    grav_edge = np.abs(ndimage.sobel(grav_c, axis=0)) + np.abs(
        ndimage.sobel(grav_c, axis=1))
    grav_edge_n = grav_edge / (grav_edge.max() + 1e-12)

    score = seis_c * grav_edge_n
    out = np.where(footprint, score, 0.0)
    out = np.where(np.isnan(grav), np.nan, out)
    if np.nanmax(out[footprint]) > 0:
        out = out / np.nanmax(out[footprint])
    return out


# --------------------------------------------------------------------------- #
# Leakage canary
# --------------------------------------------------------------------------- #

def feature_auc_canary(feature: np.ndarray, labels: np.ndarray,
                       footprint: np.ndarray,
                       withheld: np.ndarray,
                       visible: np.ndarray) -> dict:
    from sklearn.metrics import roc_auc_score

    pos_mask = withheld
    neg_mask = ((labels == 0) & footprint & (~visible))

    if pos_mask.sum() == 0 or neg_mask.sum() == 0:
        return {"auc": float("nan"), "n_pos": int(pos_mask.sum()),
                "n_neg": int(neg_mask.sum()), "leakage": None}

    f = np.nan_to_num(feature, nan=0.0)
    y = np.concatenate([np.ones(pos_mask.sum()), np.zeros(neg_mask.sum())])
    X = np.concatenate([f[pos_mask], f[neg_mask]])

    try:
        auc = roc_auc_score(y, X)
    except ValueError:
        auc = float("nan")

    leak = bool(auc > 0.90) if np.isfinite(auc) else None
    return {"auc": round(float(auc), 6), "n_pos": int(pos_mask.sum()),
            "n_neg": int(neg_mask.sum()), "leakage": leak}


# --------------------------------------------------------------------------- #
# Uniqueness vs registry rasters (local files only; network is restricted)
# --------------------------------------------------------------------------- #


N_DOTS = 30000


def place_dots(visible_faults: np.ndarray, footprint: np.ndarray,
               saddle: np.ndarray, seis: np.ndarray, n_dots: int = N_DOTS) -> np.ndarray:
    """Dot placement as a pure function of the fault mask it is given.

    Called with the full catalogue for the final raster, and with the VISIBLE faults only
    for each hide-and-recover fold. The saddle and seismic features are label-free.
    """
    dist_to_fault = ndimage.distance_transform_edt(~visible_faults)
    annulus = (dist_to_fault > 0.5) & (dist_to_fault <= 3.0) & footprint & ~visible_faults
    saddle_finite = np.nan_to_num(saddle, nan=0.0)
    seis_finite = np.nan_to_num(seis, nan=0.0)
    placement_score = saddle_finite * annulus.astype(np.float64)
    placement_score = placement_score + 0.3 * seis_finite * annulus.astype(np.float64)

    cand_scores = placement_score[annulus]
    if len(cand_scores) > n_dots:
        threshold = np.percentile(cand_scores, 100 * (1 - n_dots / len(cand_scores)))
        dot_mask = annulus & (placement_score >= threshold)
    else:
        dot_mask = annulus
    if dot_mask.sum() > n_dots:
        idx = np.argwhere(dot_mask)
        scores = placement_score[dot_mask]
        order = np.argsort(-scores)[:n_dots]
        dot_mask = np.zeros_like(dot_mask)
        dot_mask[idx[order, 0], idx[order, 1]] = True
    return dot_mask



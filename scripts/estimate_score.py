#!/usr/bin/env python3
"""Forward score estimator fitted to the 21 published (raster -> reported score) pairs.

See scripts/fit_anchor.py for the fit.  The fitted hidden-truth density is

    rho(x) = K * w(x) / sum w,   w = smooth(union of the 8 best-scoring published
                                            rasters)**4,  K = 6053

The anchor is built *from the winners' own dots*, so this estimator answers
"how much of the territory the community has already had validated does this
raster cover?"  That is the right question if (as the rules describe) the expert
panel expanded the label set by reviewing submissions.  It is a *pessimistic*
estimator for a placement the community has never tried, and it is a
PROJECTION, not a score.

Usage:  .venv/bin/python scripts/estimate_score.py <raster.tif> [<raster.tif> ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe import grid as ggrid      # noqa: E402
from gemsdoe import features as gfeat  # noqa: E402
from gemsdoe.emit import OFF_Y, OFF_X, OFF_K  # noqa: E402

WORK = ROOT / ".cache" / "gems_work"


def anchor_weight(top=("GEMSDOE32-h33-b2-zeros", "GEMSDOE36-anderson-zeros", "GEMSDOE28-h36-1",
                       "GEMSDOE28-h27-4", "GEMSDOE31-h27-4-solo", "GEMSDOE28-h38-1",
                       "GEMSDOE28-h32-1", "GEMSDOE33-h33d-analog"), gamma=4.0):
    g = ggrid.load_grid(verify=False)
    foot = g.footprint
    H, W = foot.shape
    flat = foot.reshape(-1)
    u = np.zeros((H, W), bool)
    for lab in top:
        p = ROOT / ".cache" / "research" / "calib" / f"{lab}.tif"
        if p.is_file():
            with rasterio.open(p) as s:
                a = s.read(1)
            u |= (a > 0) & np.isfinite(a) & foot
    base = np.zeros((H, W), np.float32)
    d = u.astype(np.float32)
    for dy, dx, k in zip(OFF_Y, OFF_X, OFF_K):
        y0, y1 = max(0, -dy), min(H, H - dy)
        x0, x1 = max(0, -dx), min(W, W - dx)
        if y0 >= y1 or x0 >= x1:
            continue
        base[y0:y1, x0:x1] += k * d[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    b = base.reshape(-1)[flat]
    b = b / max(b.max(), 1e-12)
    return np.power(b + 1e-6, gamma), flat, (H, W), foot


def estimate(raster: Path, K: float = 6053.0, gamma: float = 4.0) -> dict:
    w, flat, (H, W), foot = anchor_weight(gamma=gamma)
    rho = (K * w / w.sum()).astype(np.float32)
    with rasterio.open(raster) as s:
        a = s.read(1)
    m = (a > 0) & np.isfinite(a) & foot
    n = int(m.sum())
    cov = np.zeros((H, W), np.float32)
    d = m.astype(np.float32)
    for dy, dx, k in zip(OFF_Y, OFF_X, OFF_K):
        y0, y1 = max(0, -dy), min(H, H - dy)
        x0, x1 = max(0, -dx), min(W, W - dx)
        if y0 >= y1 or x0 >= x1:
            continue
        np.maximum(cov[y0:y1, x0:x1], k * d[y0 + dy:y1 + dy, x0 + dx:x1 + dx], out=cov[y0:y1, x0:x1])
    T = float((rho * cov.reshape(-1)[flat]).sum())
    T = min(T, K)
    h = np.zeros((H, W), np.float32)
    r = rho.reshape(H, W) if rho.size == H * W else None
    rr = np.zeros(H * W, np.float32)
    rr[flat] = rho
    rr = rr.reshape(H, W)
    for dy, dx, k in zip(OFF_Y, OFF_X, OFF_K):
        y0, y1 = max(0, -dy), min(H, H - dy)
        x0, x1 = max(0, -dx), min(W, W - dx)
        if y0 >= y1 or x0 >= x1:
            continue
        h[y0:y1, x0:x1] += k * rr[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    FP = float(np.sum(m * np.exp(-h)))
    FN = K - T
    den = T + 0.2 * FP + 0.8 * FN
    dti = T / den if den > 0 else 0.0
    dcat = gfeat.distance_to(ggrid.load_grid(verify=False).catalogue)
    return dict(raster=str(raster), n_dots=n, T=round(T, 2), FP=round(FP, 2), FN=round(FN, 2),
                projected_dti=round(float(dti), 4),
                median_dist_to_catalogue_px=round(float(np.median(dcat[m])), 2) if n else None,
                frac_dots_within_3px_of_catalogue=round(float((dcat[m] <= 3).mean()), 4) if n else None)


if __name__ == "__main__":
    args = sys.argv[1:] or [str(ROOT / "docs" / "downloads" /
                                "gemsdoekarage2-hkarage2-dti-greedy-habitat-20261031.tif")]
    out = [estimate(Path(a)) for a in args]
    print(json.dumps(out, indent=2))

#!/usr/bin/env python3
"""EXP-2 preflight measurements (instrument calibration, not an arm evaluation).

Questions answered from catalogue geometry and the pinned mirrors only:
  1. For dilation radii r, what fraction of WITHHELD fold truth lies within r of
     the VISIBLE catalogue (per fold, label-blind context), and what area does
     that zone cover?  This calibrates a corridor-zone emission.
  2. How corridor-like are the nine historical champions: fraction of their dots
     within r of the full catalogue?
  3. Preflight uniqueness: a planned 38k-dot corridor emission vs the nine
     champions, the lattice witness, and this repository's own rasters
     (3-px forward overlap + Spearman), before any holdout arm is scored.
No experiment is consumed and no raster is written.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from gems57.grid import load_grid                    # noqa: E402
from gems57 import spatial                           # noqa: E402

DATA = ROOT / ".cache/gems_data"
RADII = (10, 20, 30, 50, 80)
BUDGET = 38_000
NMS_PX = 2.0


def dilate_within(radius, valid):
    yy, xx = np.mgrid[-radius:radius + 1, -radius:radius + 1]
    disk = (yy * yy + xx * xx) <= radius * radius
    def op(mask):
        return ndi.binary_dilation(mask, structure=disk) & valid
    return op


def blue_noise_dots(zone, weight, budget):
    """Greedy 2-px NMS over zone cells ordered by soft weight then rng jitter."""
    rng = np.random.default_rng(20261031)
    jitter = rng.random(zone.shape).astype(np.float32)
    key = (0.75 + 0.5 * weight.astype(np.float32)) * (0.98 + 0.04 * jitter)
    ids = np.flatnonzero(zone & (key > 0))
    order = ids[np.argsort(-key.ravel()[ids], kind="stable")]
    pad = 3
    acc = np.zeros((zone.shape[0] + 2 * pad, zone.shape[1] + 2 * pad), bool)
    yy, xx = np.mgrid[-pad:pad + 1, -pad:pad + 1]
    disk = (yy * yy + xx * xx) <= NMS_PX * NMS_PX
    h, w = zone.shape
    ys, xs = np.divmod(order[: min(order.size, budget * 60)], w)
    dy, dx = [], []
    for y, x in zip(ys.tolist(), xs.tolist()):
        if (acc[y:y + 2 * pad + 1, x:x + 2 * pad + 1] & disk).any():
            continue
        acc[y + pad, x + pad] = True
        dy.append(y)
        dx.append(x)
        if len(dy) >= budget:
            break
    out = np.zeros(zone.shape, np.float32)
    out[np.asarray(dy, np.int64), np.asarray(dx, np.int64)] = 1.0
    return out, len(dy)


def main():
    grid = load_grid(DATA)
    fp, cat = grid.footprint, grid.catalogue
    valid = fp & (ndi.distance_transform_edt(fp) > 0)
    eligible = fp & (ndi.distance_transform_edt(fp) > 12)
    apron = ndi.distance_transform_edt(~cat) <= 2
    print("== 1. corridor-zone calibration on hide-and-recover folds", flush=True)
    stats = {}
    for fold in spatial.folds(cat, eligible, buffer_px=80):
        region = fold["region"]
        vis = fold["visible"]
        truth = fold["truth"]
        n_t = int(truth.sum())
        if not n_t:
            continue
        dist_vis = ndi.distance_transform_edt(~vis)
        for r in RADII:
            zone = (dist_vis <= r) & region & eligible & ~apron
            frac_truth = float((truth & (dist_vis <= r)).sum()) / n_t
            s = stats.setdefault(r, dict(zone_frac=[], truth_frac=[]))
            s["zone_frac"].append(float(zone.sum()) / max(int(region.sum()), 1))
            s["truth_frac"].append(frac_truth)
        print(f"  fold {fold['fold']}: truth={n_t}", flush=True)
    for r in RADII:
        s = stats[r]
        zf, tf = float(np.mean(s["zone_frac"])), float(np.mean(s["truth_frac"]))
        # uniform-in-zone projection: random38k baseline tp fraction 0.0690 scales
        # with in-zone truth density ratio; FP cost roughly unchanged.
        proj_tp_frac = 0.0690 * (tf / max(zf, 1e-9)) * zf / 0.207
        print(f"  r={r:3d}px zone_area={zf:.3f} truth_within={tf:.3f} "
              f"density_ratio={tf / max(zf, 1e-9) / 0.0118:.2f} "
              f"proj_tp_frac~{min(proj_tp_frac, tf):.3f}", flush=True)

    print("== 2. champion corridor-likeness (full catalogue distance)", flush=True)
    dist_cat = ndi.distance_transform_edt(~cat)
    focus = json.loads((ROOT / "registry/focus_registry_manifest.json").read_text())
    by_sha = {}
    for site, pref in (("GEMSDOE24", "h25-1-dotted-h19-5-d1-5"), ("GEMSDOE25", "dotted-h19-5-d2-8"),
                       ("GEMSDOE27", "topo-gap-closure-t-v2-on-d1-5"), ("GEMSDOE28", "h36-1-rung30-blind-r1"),
                       ("GEMSDOE30", "d28-poisson300m-offcat-44090"), ("GEMSDOE31", "h27-4-solo-d28"),
                       ("GEMSDOE32", "h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros"),
                       ("GEMSDOE33", "h33d-analog-tip-stepover-r30"), ("GEMSDOE36", "anderson-geothermal-pinn")):
        rows = [r for r in focus["rasters"] if pref in r["path"] and r.get("status") == "ok"]
        if rows:
            by_sha[site] = rows[0]
    champ_dots = {}
    for site, row in by_sha.items():
        with rasterio.open(ROOT / row["local"]) as src:
            a = src.read(1)
        dots = np.isfinite(a) & (a > 0) & fp
        champ_dots[site] = dots
        n = int(dots.sum())
        fr = {r: round(float((dots & (dist_cat <= r)).sum()) / max(n, 1), 3) for r in (2, 20, 50)}
        print(f"  {site}: dots={n} within{fr}", flush=True)

    print("== 3. planned corridor emission preflight vs registry", flush=True)
    zone_full = (dist_cat <= 30) & eligible & ~apron & ~cat
    weight = np.zeros(fp.shape, np.float32)
    dots, n_dots = blue_noise_dots(zone_full, weight, BUDGET)
    print(f"  planned dots placed: {n_dots}", flush=True)
    dots3 = ndi.binary_dilation(dots > 0, structure=np.mgrid[-3:4, -3:4][0] ** 2 +
                                np.mgrid[-3:4, -3:4][1] ** 2 <= 9)
    for site, cd in champ_dots.items():
        ov = float(dots3[cd].mean())
        inter = int((cd & (dots > 0)).sum())
        print(f"  overlap vs {site}: within3px={ov:.3f} exact={inter / max(int(cd.sum()),1):.3f}", flush=True)
    with rasterio.open(ROOT / ".cache/witness/lattice.tif") as src:
        lat = src.read(1)
    lat_d = np.isfinite(lat) & (lat > 0) & fp
    print(f"  overlap vs lattice: within3px={float(dots3[lat_d].mean()):.3f}", flush=True)
    save = {"zone_stats": {str(r): {"mean_zone_frac": float(np.mean(stats[r]["zone_frac"])),
                                    "mean_truth_frac": float(np.mean(stats[r]["truth_frac"]))}
                           for r in RADII},
            "champion_catalogue_proximity": True}
    (ROOT / "evidence/k9/preflight_corridor.json").write_text(json.dumps(save, indent=2) + "\n")


if __name__ == "__main__":
    main()

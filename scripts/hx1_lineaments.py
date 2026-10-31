#!/usr/bin/env python3
"""HX-1 experiment: structural lineament detection vs the metric's arithmetic.

Protocol rule 2 (hide-and-recover): whole catalogue components are withheld with a
3 px feature buffer; every catalogue-derived quantity uses the VISIBLE mask only;
visible faults are masked pixel-exactly at scoring time; score is pooled DTI with
alpha = 0.2, beta = 0.8 and a 300 m (3 px) triangular kernel.

Hypothesis (HX-1)
-----------------
"Unmapped faults in the GEMS study area express as elongated terrain lineaments
in the mirrored 100 m lidar/geophysical stack (12 lidar scarp channels, 4
radiometric ratio channels, 4 radiometric channels, TMI upward-continued), and a
line-integral (lineament) transform of that stack places single-pixel emissions
with materially better truth credit than a random placement at the same budget."

Falsification: if the pooled holdout DTI of the lineament emission is not
significantly above the random-placement control at the same budget, the
hypothesis is NEGATIVE and the stack must not be used to target a submission.

This script is deliberately read-only with respect to git-tracked submissions: it
writes only to ``.cache/`` and ``evidence/hx1/``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))

from gems57.grid import load_grid                      # noqa: E402
from gems57.holdout import buffered_component_draw, score  # noqa: E402

CACHE = ROOT / ".cache"
MIRROR = CACHE / "gems_mirror"
EXT = MIRROR / "external"
OUT = ROOT / "evidence" / "hx1"

LIDAR = ["ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max",
         "downface_max", "upface_max", "cross_max", "relief", "coh100", "strike", "valid"]
RAD = ["K", "Th", "U", "TC"]
RATIO = ["ThK", "UK", "UTh", "TMI"]


def load_bands() -> dict[str, np.ndarray]:
    b: dict[str, np.ndarray] = {}
    for name, path in ((LIDAR, EXT / "lidar_scarp_features_u8.tif"),
                       (RAD, EXT / "geodawn_rad_u8.tif"),
                       (RATIO, EXT / "geodawn_extensions_u8.tif")):
        with rasterio.open(path) as ds:
            for i, n in enumerate(name, 1):
                b[n] = ds.read(i).astype(np.float32)
    return b


def prank(a: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Percentile rank of every cell inside ``mask``, 0 outside."""
    out = np.zeros(a.shape, np.float32)
    v = a[mask]
    if v.size == 0:
        return out
    order = np.argsort(v, kind="stable")
    r = np.empty(v.size, np.float32)
    r[order] = np.arange(v.size, dtype=np.float32) / max(v.size - 1, 1)
    out[mask] = r
    return out


def line_kernels(lengths=(21, 31), thetas=(0, 30, 60, 90, 120, 150)):
    ks = []
    for L in lengths:
        half = L // 2
        for th in thetas:
            t = np.deg2rad(th)
            k = np.zeros((L, L), np.float32)
            for s in range(-half, half + 1):
                y = int(round(half + s * np.sin(t)))
                x = int(round(half + s * np.cos(t)))
                k[y, x] = 1.0
            k /= k.sum()
            ks.append((L, th, k))
    return ks


def line_integral(s: np.ndarray, ks) -> tuple[np.ndarray, list]:
    best = np.zeros_like(s)
    per_theta: dict[float, np.ndarray] = {}
    for L, th, k in ks:
        r = ndi.convolve(s, k, mode="nearest")
        acc = per_theta.get(th)
        per_theta[th] = r if acc is None else np.maximum(acc, r)
        best = np.maximum(best, r)
    return best, per_theta


def emit_from_ranking(rank: np.ndarray, eligible: np.ndarray, n: int) -> np.ndarray:
    idx = np.flatnonzero(eligible.ravel())
    order = idx[np.argsort(-rank.ravel()[idx], kind="stable")][:n]
    e = np.zeros(eligible.shape, bool)
    e.ravel()[order] = True
    return e


def pooled(emitted: np.ndarray, folds) -> dict:
    tp = fp = fn = 0.0
    per = []
    for f in folds:
        r = score(emitted, f, np.ones(emitted.shape, bool))
        tp += r["tp"]; fp += r["fp"]; fn += r["fn"]
        per.append(round(r["dti"], 5))
    dti = tp / (tp + 0.2 * fp + 0.8 * fn) if (tp + fp + fn) else 0.0
    return {"pooled_dti": round(float(dti), 6), "tp": round(tp, 3),
            "fp": round(fp, 3), "fn": round(fn, 3),
            "coverage": round(float(tp / (tp + fn)) if (tp + fn) else 0.0, 6),
            "per_fold_dti": per}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--budgets", default="20000,40000,80000,160000")
    ap.add_argument("--seeds", default="20")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    budgets = [int(x) for x in args.budgets.split(",")]

    grid = load_grid(MIRROR)
    bands = load_bands()
    lidar_valid = bands["valid"] > 0
    print(f"grid {grid.shape} catalogue={int(grid.catalogue.sum())} footprint={int(grid.footprint.sum())}")

    # ---- leakage canary: every single layer, alone, against catalogue proximity ----
    rng = np.random.default_rng(0)
    samp = rng.choice(np.flatnonzero((grid.catalogue | (grid.catalogue == False)).ravel() & grid.footprint.ravel()),
                      150_000, replace=False)
    dcat = ndi.distance_transform_edt(~grid.catalogue)
    near = (dcat <= 3)
    canary = {}
    for name, a in bands.items():
        if name in ("valid", "strike"):
            continue
        f = a.ravel()[samp]
        y = grid.catalogue.ravel()[samp]
        y2 = near.ravel()[samp]
        off = dcat.ravel()[samp] > 8
        sel = y2 | off
        from sklearn.metrics import roc_auc_score
        auc_cat = float(roc_auc_score(y, f)) if y.sum() > 10 else float("nan")
        auc_near = float(roc_auc_score(y2[sel], f[sel]))
        canary[name] = {"auc_catalogue": round(auc_cat, 4), "auc_within3px_vs_far": round(auc_near, 4),
                        "leakage_flag_auc_gt_0.90": bool(max(abs(auc_cat - .5), abs(auc_near - .5)) + .5 > 0.90)}
    print("canary:", {k: v["auc_within3px_vs_far"] for k, v in canary.items()})

    # ---- structural score ----
    parts = []
    for name in ("step_max", "cross_max", "upface_max", "lapneg_max", "ex_max"):
        parts.append(prank(bands[name], lidar_valid))
    parts.append(prank(bands["coh100"], lidar_valid))
    s = np.mean(parts, axis=0).astype(np.float32)
    s[~lidar_valid] = 0.0
    li, _ = line_integral(s, line_kernels())
    rank_line = (s * li).astype(np.float32)
    rank_line[~lidar_valid] = 0.0
    print("line-integral done")

    report = {"experiment": "HX-1 structural lineament vs arithmetic",
              "evidence_class": "HOLDOUT-DTI (hide-and-recover, catalogue components withheld, 3 px feature buffer)",
              "grid": {"shape": list(grid.shape), "catalogue_px": int(grid.catalogue.sum()),
                       "footprint_px": int(grid.footprint.sum())},
              "leakage_canary": canary, "budgets": {}, "random_controls": {}}

    for seed in [int(x) for x in args.seeds.split(",")]:
        folds, _ = buffered_component_draw(grid, seed=seed, hide_frac=0.20, buffer_px=3)
        visible = folds[0]["visible"]
        dvis = ndi.distance_transform_edt(~visible)
        # the organizer's rule: known faults are masked, so a dot within the kernel
        # of a visible fault is a certain false positive. 4 px = kernel + 1 px guard.
        eligible = grid.footprint & (dvis > 4.0) & lidar_valid
        rng2 = np.random.default_rng(1000 + seed)
        cand = np.flatnonzero(eligible.ravel())
        rnd_rank = np.zeros(grid.shape, np.float32)
        rnd_rank.ravel()[cand] = rng2.random(cand.size)
        withheld = int(sum(int(f["truth"].sum()) for f in folds))
        report["budgets"][str(seed)] = {"withheld_positives": withheld,
                                        "eligible_cells": int(eligible.sum()), "rows": []}
        for n in budgets:
            r_line = pooled(emit_from_ranking(rank_line, eligible, n), folds)
            r_rand = pooled(emit_from_ranking(rnd_rank, eligible, n), folds)
            row = {"budget_dots": n, "lineament": r_line, "random": r_rand,
                   "ratio_lineament_over_random": round(r_line["pooled_dti"] / max(r_rand["pooled_dti"], 1e-12), 3)}
            report["budgets"][str(seed)]["rows"].append(row)
            print(n, "lineament", r_line["pooled_dti"], "random", r_rand["pooled_dti"], "ratio", row["ratio_lineament_over_random"])

    (args.out / "hx1_lineament_vs_random.json").write_text(json.dumps(report, indent=1))
    print("wrote", args.out / "hx1_lineament_vs_random.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

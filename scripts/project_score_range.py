#!/usr/bin/env python3
"""Sensitivity bound on the forward projection.

The single-anchor estimator (estimate_score.py) uses gamma=4, which was the
extreme of the grid it searched -- a boundary optimum, i.e. plausibly optimistic.
This script refits the same forward model at several gamma values and reports the
resulting projection RANGE for a candidate raster, so the published number is a
band rather than a point.

Model:  rho(x) = K * w(x)/sum(w),  w = smooth(union of the 8 best published
rasters) ** gamma.  K is fitted by 1-D search minimising RMSE against the 21
USER-REPORTED scores.  DTI = T/(T + 0.2*FP + 0.8*FN).
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
import rasterio
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from gemsdoe import grid as ggrid, emit as gemit

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / ".cache" / "research" / "calib"
REG = json.loads((ROOT / "registry" / "calibration_rasters.json").read_text())["rasters"]
TOP8 = ["GEMSDOE32-h33-b2-zeros", "GEMSDOE36-anderson-zeros", "GEMSDOE28-h36-1",
        "GEMSDOE28-h27-4", "GEMSDOE28-h38-1", "GEMSDOE31-h27-4-solo",
        "GEMSDOE33-h33d-analog", "GEMSDOE25-dotted-d28"]


def load(label):
    with rasterio.open(CAL / f"{label}.tif") as s:
        a = s.read(1)
    return (a > 0) & np.isfinite(a)


def main():
    t0 = time.time()
    g = ggrid.load_grid(verify=False)
    H, W = g.shape
    foot = g.footprint
    flat = foot.reshape(-1)
    lut = np.flatnonzero(flat)
    recs = [r for r in REG if r.get("reported_score")]
    labels = [r["label"] for r in recs]
    y = np.array([float(r["reported_score"]) for r in recs])
    idx = {}
    for r in recs:
        m = load(r["label"]) & foot
        idx[r["label"]] = np.flatnonzero(m.reshape(-1)[flat])
        del m
    union = np.zeros((H, W), bool)
    for lab in TOP8:
        if lab in idx:
            u = np.zeros(H * W, bool); u[lut[idx[lab]]] = True
            union |= u.reshape(H, W); del u
    print(f"{len(recs)} references, union of top-8 = {int(union.sum())} px", flush=True)

    def smooth(a):
        out = np.zeros((H, W), np.float32)
        for dy, dx, k in zip(gemit.OFF_Y, gemit.OFF_X, gemit.OFF_K):
            y0, y1 = max(0, -dy), min(H, H - dy); x0, x1 = max(0, -dx), min(W, W - dx)
            if y0 >= y1 or x0 >= x1: continue
            out[y0:y1, x0:x1] += k * a[y0+dy:y1+dy, x0+dx:x1+dx]
        return out

    def max_credit(mask):
        """M(x) = max over the R=3 disk of dot*kernel  (official TP term)."""
        M = np.full((H, W), -np.inf, np.float32)
        d = mask.astype(np.float32)
        for dy, dx, k in zip(gemit.OFF_Y, gemit.OFF_X, gemit.OFF_K):
            y0, y1 = max(0, -dy), min(H, H - dy); x0, x1 = max(0, -dx), min(W, W - dx)
            if y0 >= y1 or x0 >= x1: continue
            np.maximum(M[y0:y1, x0:x1], k * d[y0+dy:y1+dy, x0+dx:x1+dx], out=M[y0:y1, x0:x1])
        return np.nan_to_num(M, nan=0.0, posinf=0.0, neginf=0.0).reshape(-1)[flat]

    # S_ref = sum_g (w/sum w)(g) * M_ref(g)  is independent of K, so precompute it.
    base = union.astype(np.float32)
    print("precomputing per-file max-credit maps ...", flush=True)
    S = {}
    for gamma in (0.25, 1.0, 2.0, 4.0):
        sm = smooth(base); wf = (sm.reshape(-1)[flat] + 1e-6) ** gamma
        wf = (wf / wf.sum()).astype(np.float32)
        S[gamma] = {}
        for lab in labels:
            u = np.zeros(H * W, bool); u[lut[idx[lab]]] = True
            M = max_credit(u.reshape(H, W)); del u
            S[gamma][lab] = float(np.sum(wf * M)); del M
    sw = {gamma: (smooth(base).reshape(-1)[flat] + 1e-6) ** gamma for gamma in S}
    sw = {gamma: (v / v.sum()).astype(np.float32) for gamma, v in sw.items()}
    Kgrid = np.exp(np.linspace(np.log(500), np.log(300000), 22))
    global S_ref, sw_ref

    def predict(wf, K):
        preds = []
        for lab in labels:
            i = idx[lab]
            T = min(K * S_ref[lab], K)
            FP = float(np.exp(-(K * sw_ref[i])).sum())
            FN = K - T
            preds.append(T / (T + 0.2 * FP + 0.8 * FN) if (T + 0.2 * FP + 0.8 * FN) > 0 else 0.0)
        return np.array(preds)

    results = {}

    for gamma in (0.25, 1.0, 2.0, 4.0):
        sm = gemit.kernel_smooth(base) if False else smooth(base)
        wf = (sm.reshape(-1)[flat] + 1e-6) ** gamma
        S_ref = S[gamma]; sw_ref = sw[gamma]
        del wf
        best = (1e9, None, None)
        for K in Kgrid:
            p = predict(None, float(K))
            r = float(np.sqrt(np.mean((p - y) ** 2)))
            if r < best[0]:
                best = (r, float(K), p)
        results[gamma] = dict(rmse=round(best[0], 5), K=round(best[1], 1),
                              preds=[round(float(v), 4) for v in best[2]])
        print(f"  gamma={gamma}: rmse={best[0]:.4f} K={best[1]:.0f}", flush=True)

    # project the candidate rasters
    cands = [p for p in sorted((ROOT / "docs" / "downloads").glob("gemsdoekarage2-*.tif"))]
    proj = {}
    for cp in cands:
        with rasterio.open(cp) as s:
            a = s.read(1)
        dots = ((a > 0) & np.isfinite(a) & foot)
        ci = np.flatnonzero(dots.reshape(-1)[flat])
        row = {"n_dots": int(dots.sum())}
        u = np.zeros(H * W, bool); u[lut[ci]] = True
        Mc = max_credit(u.reshape(H, W)); del u
        for gamma, r in results.items():
            K = r["K"]
            T = min(K * float(np.sum(sw[gamma] * Mc)), K)
            FP = float(np.exp(-(K * sw[gamma][ci])).sum()); FN = K - T
            row[f"gamma_{gamma}"] = round(T / (T + 0.2 * FP + 0.8 * FN), 4)
        del Mc
        del dots
        proj[cp.name] = row
        print(f"  {cp.name}: {row}", flush=True)

    out = dict(generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
               kind="PROJECTION (model-based; not an organizer score)",
               anchor="union of the 8 best published rasters, smoothed, raised to gamma",
               K_search=dict(grid="22 log-spaced values 500..300000", objective="RMSE vs 21 USER-REPORTED scores"),
               gamma_fits=results, candidate_projections=proj,
               reported_scores={lab: float(v) for lab, v in zip(labels, y)})
    p = ROOT / "evidence" / "projection-range-2026-10-31.json"
    p.write_text(json.dumps(out, indent=2, default=ggrid.json_default) + "\n")
    print(f"wrote {p} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()

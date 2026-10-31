#!/usr/bin/env python3
"""Fit a forward model of the hidden (expert) label set to the published
submissions whose reported leaderboard scores are known, then use it to estimate
the score of any new raster.

Why this is needed
------------------
The organiser's truth is private.  The only *measured* link between a raster and
a leaderboard number is the set of published submissions with reported scores
(all USER-REPORTED / UNVERIFIED: no submission-page receipt exists).  We can
therefore *invert* them: assume the hidden truth is a realisation of a density

    rho(x) = K * f(x) / sum(f),   f(x) = s(x)**eta * w(d_cat(x); lam)

where s(x) is our modelled fault-probability field and w(d) = 1 - exp(-d/lam)
encodes the measured fact that the best files delete every dot within 100 m of a
mapped fault, i.e. a fault adjacent to the catalogue is almost certainly already
mapped and therefore absent from the scored label set.

For a binary raster S the metric, in expectation over that density, is

    T  = sum_x rho(x) * max_{y in S} k(d(x,y))
    FP = sum_{y in S} (1 - q(y)),  q(y) = 1 - exp(-sum_g rho(g) k(d(y,g)))
    FN = K - T
    DTI = T / (T + 0.2 FP + 0.8 FN)

(K, lam, eta) are fitted by least squares to the reported scores.  The fitted
map is then a forward estimator: given any new raster it returns an estimated
DTI.  It is a PROJECTION, never a score -- every input number is user-reported
and K is a property of this model, not an organiser measurement.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsdoe import grid as ggrid          # noqa: E402
from gemsdoe import features as gfeat      # noqa: E402
from gemsdoe.emit import OFF_Y, OFF_X, OFF_K, kernel_smooth  # noqa: E402

import rasterio  # noqa: E402

CALIB = ROOT / ".cache" / "research" / "calib"
WORK = ROOT / ".cache" / "gems_work"
EVID = ROOT / "evidence"


def load_calibration(foot):
    recs = json.loads((ROOT / "registry" / "calibration_rasters.json").read_text())["rasters"]
    out = []
    for r in recs:
        p = CALIB / f"{r['label']}.tif"
        if not p.is_file():
            continue
        with rasterio.open(p) as s:
            a = s.read(1)
        dots = (a > 0) & np.isfinite(a) & foot
        out.append(dict(label=r["label"], score=float(r["reported_score"]), dots=dots,
                        n=int(dots.sum()), sha256=r["sha256"], path=r["path"], ref=r["ref"]))
    return out


def coverage(dot, shape):
    cov = np.zeros(shape, dtype=np.float32)
    d = dot.astype(np.float32)
    for dy, dx, k in zip(OFF_Y, OFF_X, OFF_K):
        y0, y1 = max(0, -dy), min(shape[0], shape[0] - dy)
        x0, x1 = max(0, -dx), min(shape[1], shape[1] - dx)
        if y0 >= y1 or x0 >= x1:
            continue
        np.maximum(cov[y0:y1, x0:x1], k * d[y0 + dy:y1 + dy, x0 + dx:x1 + dx], out=cov[y0:y1, x0:x1])
    return cov


def main():
    g = ggrid.load_grid(verify=False)
    foot, cat = g.footprint, g.catalogue
    H, W = foot.shape
    flat = foot.reshape(-1)
    dcat = gfeat.distance_to(cat)

    smap = np.load(WORK / "holdout_assembled.npy").astype(np.float32)
    lo, hi = float(np.percentile(smap[foot], 1)), float(np.percentile(smap[foot], 99))
    s01 = np.clip((smap - lo) / max(hi - lo, 1e-9), 0, 1)

    calib = load_calibration(foot)
    labels = [c["label"] for c in calib]
    scores = {c["label"]: c["score"] for c in calib}
    dot_idx = {}
    cov_f = {}
    for c in calib:
        cov = coverage(c["dots"], (H, W))
        cov_f[c["label"]] = (np.round(cov.reshape(-1)[flat] * 255)).astype(np.uint16)
        dot_idx[c["label"]] = np.flatnonzero(c["dots"].reshape(-1))
        del cov
    print(f"calibration rasters: {len(calib)}", flush=True)

    lut = np.full(H * W, -1, np.int64)
    lut[flat] = np.arange(int(flat.sum()))
    s_f = s01.reshape(-1)[flat].astype(np.float32)
    dcat_f = dcat.reshape(-1)[flat].astype(np.float32)

    def precompute(lam, eta):
        f = (np.power(s_f + 1e-3, eta) * (1.0 - np.exp(-dcat_f / lam))).astype(np.float32)
        tot = float(f.sum())
        if tot <= 0:
            return None
        full = np.zeros(H * W, dtype=np.float32)
        full[flat] = f
        hf = kernel_smooth(full.reshape(H, W)).reshape(-1)[flat]
        A = {lab: float((f * cov_f[lab]).sum()) / 255.0 for lab in labels}
        hd = {lab: hf[lut[dot_idx[lab]]] for lab in labels}
        n = {lab: int(dot_idx[lab].size) for lab in labels}
        return dict(tot=tot, A=A, hd=hd, n=n)

    def eval_K(pre, K):
        scale = K / pre["tot"]
        out = {}
        for lab in labels:
            T = scale * pre["A"][lab]
            T = min(T, K)
            q = 1.0 - np.exp(-scale * pre["hd"][lab])
            FP = float(np.sum(1.0 - q))
            FN = K - T
            den = T + 0.2 * FP + 0.8 * FN
            out[lab] = T / den if den > 0 else 0.0
        return out

    KS = [500, 1000, 2000, 3500, 5000, 7500, 10000, 15000, 20000, 30000, 45000,
          65000, 90000, 130000, 180000, 250000, 400000]
    best = None
    for eta in (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0):
        for lam in (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 18.0, 25.0, 40.0, 70.0, 150.0):
            pre = precompute(lam, eta)
            if pre is None:
                continue
            for K in KS:
                p = eval_K(pre, K)
                ss = sum((p[l] - scores[l]) ** 2 for l in labels)
                rmse = (ss / len(labels)) ** 0.5
                if best is None or rmse < best[0]:
                    best = (rmse, float(K), lam, eta, p)
            print(f"  eta={eta:<5} lam={lam:<6} best_so_far rmse={best[0]:.4f} K={best[1]:.0f}", flush=True)
    rmse, K, lam, eta, p = best
    print(f"\nFIT: rmse={rmse:.4f} K={K:.0f} lambda={lam} eta={eta}")

    rows = []
    for lab in sorted(labels, key=lambda l: -scores[l]):
        rows.append(dict(label=lab, n=int(dot_idx[lab].size), reported=scores[lab],
                         predicted=round(p[lab], 4), resid=round(p[lab] - scores[lab], 4)))
    for r in rows:
        print(f"  {r['label']:28s} n={r['n']:7d} reported={r['reported']:.4f} predicted={r['predicted']:.4f} resid={r['resid']:+.4f}")

    # leave-one-out
    loo = []
    for hold in labels:
        sub = [l for l in labels if l != hold]
        b2 = None
        for eta3 in (0.0, eta * 0.5, eta, eta * 1.5, eta * 2.0):
            for lam3 in (lam * 0.5, lam * 0.75, lam, lam * 1.5, lam * 2.0):
                pre = precompute(lam3, eta3)
                if pre is None:
                    continue
                for K3 in KS:
                    p3 = eval_K(pre, K3)
                    ss = sum((p3[l] - scores[l]) ** 2 for l in sub)
                    r3 = (ss / len(sub)) ** 0.5
                    if b2 is None or r3 < b2[0]:
                        b2 = (r3, float(K3), lam3, eta3, p3)
        loo.append(dict(held=hold, reported=scores[hold], loo_predicted=round(b2[4][hold], 4),
                        abs_err=round(abs(b2[4][hold] - scores[hold]), 4)))
    loo_rmse = float((sum(x["abs_err"] ** 2 for x in loo) / len(loo)) ** 0.5)
    print(f"leave-one-out RMSE = {loo_rmse:.4f}")

    pre = precompute(lam, eta)
    f = np.zeros(H * W, dtype=np.float32)
    f[flat] = np.power(s_f + 1e-3, eta) * (1.0 - np.exp(-dcat_f / lam))
    rho = (K * f / f.sum()).reshape(H, W)
    np.save(WORK / "hidden_truth_density.npy", rho.astype(np.float32))
    out = dict(schema="gems-score-estimator-v1",
               fitted=dict(K=float(K), lam_px=float(lam), eta=float(eta), rmse=float(rmse),
                           loo_rmse=loo_rmse, n_grid_K=len(KS)),
               inputs=dict(n_calibration=len(calib),
                           score_evidence="USER-REPORTED / UNVERIFIED (no organizer receipt)",
                           s_map="assembled 4-fold hide-and-recover model probability"),
               fit_table=rows, leave_one_out=loo,
               warning=("PROJECTION fitted to user-reported numbers, not an organizer score. "
                        "Never report as a measured result."))
    (EVID / "score-estimator-2026-10-31.json").write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", EVID / "score-estimator-2026-10-31.json")


if __name__ == "__main__":
    main()

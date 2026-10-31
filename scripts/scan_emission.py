#!/usr/bin/env python3
"""Scan the emission family and score each candidate on measured geometry, the
consensus-anchor projection, and the model's own expected DTI."""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "scripts"))
from gemsdoe import grid as ggrid, features as gfeat, emit as gemit
import run_lane as rl
import estimate_score as es

import argparse as _ap
_ap_ = _ap.ArgumentParser(); _ap_.add_argument("--habitat", default="geo"); args = _ap_.parse_args()
g = ggrid.load_grid(verify=False)
smap = np.load(rl.WORK / "holdout_assembled.npy").astype(np.float32)
dcat = gfeat.distance_to(g.catalogue)
w_flat = es.anchor_weight()[0]
K_ANCHOR = 6053.0
flat = g.footprint.reshape(-1)

def cov_of(dots):
    cov = np.zeros(g.shape, np.float32)
    d = dots.astype(np.float32)
    for dy, dx, k in zip(gemit.OFF_Y, gemit.OFF_X, gemit.OFF_K):
        y0, y1 = max(0, -dy), min(g.shape[0], g.shape[0] - dy)
        x0, x1 = max(0, -dx), min(g.shape[1], g.shape[1] - dx)
        if y0 >= y1 or x0 >= x1: continue
        np.maximum(cov[y0:y1, x0:x1], k * d[y0+dy:y1+dy, x0+dx:x1+dx], out=cov[y0:y1, x0:x1])
    return cov

rows = []
for lam in (3.0, 8.0, 20.0):
    for eta in (1.0, 2.0, 4.0, 8.0):
        f, _ = rl.target_density(g, smap, lam_px=lam, eta=eta, min_dcat=1.0, rank=True,
                                 source=args.habitat)
        for K in (8000.0, 20000.0, 50000.0, 128000.0):
            pi = (K * f / float(f.sum())).astype(np.float64)
            allowed = g.footprint & (dcat >= 1.0)
            t0 = time.time()
            dots, diag = gemit.greedy_emit(pi, allowed, max_dots=400_000, candidate_top=400_000)
            if not dots.any():
                continue
            cov = cov_of(dots)
            T = min(float((w_flat * K_ANCHOR / w_flat.sum() * cov.reshape(-1)[flat]).sum()), K_ANCHOR)
            h = gemit.kernel_smooth((w_flat * K_ANCHOR / w_flat.sum()).reshape(1, -1)) if False else None
            # anchor FP term
            rho_a = np.zeros(g.shape[0]*g.shape[1], np.float32); rho_a[flat] = (K_ANCHOR*w_flat/w_flat.sum()).astype(np.float32)
            rho_a = rho_a.reshape(g.shape)
            ha = np.zeros(g.shape, np.float32)
            for dy, dx, k in zip(gemit.OFF_Y, gemit.OFF_X, gemit.OFF_K):
                y0, y1 = max(0, -dy), min(g.shape[0], g.shape[0]-dy); x0, x1 = max(0, -dx), min(g.shape[1], g.shape[1]-dx)
                if y0>=y1 or x0>=x1: continue
                ha[y0:y1, x0:x1] += k*rho_a[y0+dy:y1+dy, x0+dx:x1+dx]
            FP = float(np.sum(dots*np.exp(-ha)))
            FN = K_ANCHOR - T
            proj = T/(T+0.2*FP+0.8*FN) if (T+0.2*FP+0.8*FN) > 0 else 0.0
            rows.append(dict(lam=lam, eta=eta, K=K, n=int(dots.sum()),
                             cover=round(float((gfeat.distance_to(dots)[g.footprint] <= 3).mean()), 4),
                             med_dcat=round(float(np.median(dcat[dots])), 1),
                             model_dti=round(diag["expected_dti"], 4),
                             anchor_proj=round(float(proj), 4),
                             secs=round(time.time()-t0, 1)))
            print(rows[-1], flush=True)
            del pi, dots, cov, ha, rho_a
Path(rl.WORK / f"emission_scan_{args.habitat}.json").write_text(json.dumps(rows, indent=2) + "\n")
print(f"\n{len(rows)} configurations written to {rl.WORK/f'emission_scan_{args.habitat}.json'}")

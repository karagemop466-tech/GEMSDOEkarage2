#!/usr/bin/env python3
"""HOLDOUT-DTI for the independent geological habitat index, scored with the
vendored official metric (scripts/evaluate_holdout.py::dti_weighted_terms).

The habitat index is built only from the 19-band GeoDAWN stack -- it is not
trained on anything -- so a spatially blocked holdout is a genuine out-of-sample
measurement.  For each of the 16 interleaved 4x4 blocks we rank that block's
footprint pixels by the index, emit the top N (N scaled so the total matches the
40,561 dots of the released raster), and score against the withheld catalogue
positives that lie inside the block and are more than 3 px from every visible
catalogue pixel (the isolated proxy for "unmapped").
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from gemsdoe import grid as ggrid, features as gfeat, habitat as ghab
import run_lane as rl
import evaluate_holdout as eh

ROOT = Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(20261031)
N_DOTS = 40561


def main():
    t0 = time.time()
    g = ggrid.load_grid(verify=False)
    H, W = g.shape
    comp, meta = ghab.geological_index_from_path(str(g.data_dir / "training_features.tif"), g.footprint)
    comp = np.nan_to_num(comp, nan=-1e30)
    dcat = gfeat.distance_to(g.catalogue)
    eligible = g.footprint & (dcat >= 1)
    n_elig = int(eligible.sum())
    per_fold, terms = [], []
    for fi, fm in enumerate([np.logical_or.reduce(f) for f in [rl.make_blocks(g.shape)[i::16] for i in range(16)]]):
        vis = g.footprint & ~fm
        dvis = gfeat.distance_to(g.catalogue & vis)
        iso = fm & g.catalogue & (dvis > 3)
        n_iso = int(iso.sum())
        cand = eligible & fm
        n_cand = int(cand.sum())
        if n_iso < 5 or n_cand < 100:
            continue
        n_emit = max(1, int(round(N_DOTS * n_cand / n_elig)))
        v = np.where(cand, comp, -np.inf)
        idx = np.argpartition(v.reshape(-1), -n_emit)[-n_emit:]
        p = np.zeros(H * W, np.float64); p[idx] = 1.0
        p = p.reshape(H, W)
        t = eh.dti_weighted_terms(p, iso.astype(np.uint8), 100.0, 0.2, 0.8, 300.0)
        terms.append([t["TPw"], t["FPw"], t["FNw"]])
        base = n_iso / n_cand
        per_fold.append(dict(fold=fi, n_emit=n_emit, n_isolated=n_iso,
                             TPw=round(t["TPw"], 3), FPw=round(t["FPw"], 2), FNw=round(t["FNw"], 2),
                             DTI=round(t["DTI"], 5),
                             enrichment=round((t["TPw"] / max(n_emit, 1)) / max(base, 1e-12), 2)))
        print(per_fold[-1], flush=True)
    a = np.array(terms)
    TPw, FPw, FNw = a.sum(axis=0)
    dti = TPw / (TPw + 0.2 * FPw + 0.8 * FNw + eh.EPS)
    boots = []
    for _ in range(2000):
        s = a[RNG.integers(0, len(a), len(a))].sum(axis=0)
        boots.append(s[0] / (s[0] + 0.2 * s[1] + 0.8 * s[2] + eh.EPS))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    out = dict(
        generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
        metric="vendored official DTI (alpha=0.2, beta=0.8, R=300 m triangular kernel)",
        method=meta,
        scoring="scripts/evaluate_holdout.py::dti_weighted_terms, pooled over 16 interleaved 4x4 spatial folds",
        withheld_positives_isolated=int(sum(f["n_isolated"] for f in per_fold)),
        emitted_total=int(sum(f["n_emit"] for f in per_fold)),
        terms=dict(TPw=round(float(TPw), 3), FPw=round(float(FPw), 2), FNw=round(float(FNw), 2)),
        HOLDOUT_DTI=dict(estimate=round(float(dti), 5), ci95=[round(float(lo), 5), round(float(hi), 5)],
                         bootstrap="block bootstrap over the 16 spatial folds, 2000 draws"),
        per_fold=per_fold,
        note="HOLDOUT-DTI against ISOLATED withheld catalogue positives. This is a PROXY for the scored unseen-fault label set, not an organizer score.",
    )
    p = ROOT / "evidence" / "habitat-holdout-2026-10-31.json"
    p.write_text(json.dumps(out, indent=2, default=ggrid.json_default) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "per_fold"}, indent=2))
    print(f"\nwrote {p} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()

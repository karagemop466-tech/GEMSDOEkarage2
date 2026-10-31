#!/usr/bin/env python3
"""E3 - the scale law: is the group's self-imposed ~37.6k dot cap leaving score on the table?

Two measured facts collide.

1. The published metric charges 0.2 per false-positive pixel and 0.8 per missed truth
   pixel, and `vendor/gems57/metric.py` records that the organiser masks mapped catalogue
   pixels out of scoring (thread 11516). The marginal rule implemented there is "include a
   pixel iff its realised kernel credit exceeds alpha * DTI" - about 0.056 at this group's
   score, i.e. anything within ~283 m of a truth pixel. That rule rewards *abundant*
   emission near predicted structures.
2. Every raster the group has ever published is capped at 0.4-1.2 % of the footprint
   (the 0.2778 leader: 37,654 of 5,167,373 px), and its name says the cap was tuned by
   pruning (121,131 -> 44,090 -> 40,199 -> 37,654 dots as the score rose).

The cap and the metric disagree, so the cap is either right (because credit per pixel
decays fast enough that extra mass is net negative) or it is an unexamined inheritance.
This script measures the decay: it sweeps the emission budget over two orders of magnitude
on one field, scores every budget with the inherited pooled-hide evaluator, and simultaneously
scores the nine focus-site rasters on the same instrument so the comparison is apples to
apples rather than "our weak field versus their strong one".

It then fits c(K) (credit per emitted pixel as a function of budget) and asks, for each
plausible size of the hidden expert label set |G|, what budget maximises
    DTI = 5*c(K)*K / (K + 4|G|).
The argmax is the scale recommendation. Nothing here is a score and nothing is promoted.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor")); sys.path.insert(0, str(ROOT / "scripts"))
from gems57 import evaluate_holdout as shared, spatial        # noqa: E402
from gems57.grid import load_grid                             # noqa: E402
from emission_law import (CACHE, EV, DATA, COLLAR_PX, grow, ensure_grid_files)  # noqa: E402

BUDGETS = [5_000, 12_500, 25_000, 37_654, 75_000, 150_000, 300_000, 600_000, 1_200_000]
SEPS = [2.8, 4.0]
GS = [5_000, 10_000, 20_000, 40_000, 58_259]


def score_field(pred_full, folds, valid):
    terms, agg = None, dict(tp=0.0, fp=0.0, fn=0.0, n_truth=0, n_emitted=0)
    for f in folds:
        y, x = np.nonzero(f["region"])
        sl = (slice(max(0, y.min() - 4), min(f["region"].shape[0], y.max() + 5)),
              slice(max(0, x.min() - 4), min(f["region"].shape[1], x.max() + 5)))
        fc = {k: f[k][sl] for k in ("region", "truth", "visible")}
        res, t = shared.evaluate(pred_full[sl].astype(np.float32), fc, valid[sl],
                                 origin=(sl[0].start, sl[1].start),
                                 global_shape=pred_full.shape)
        terms = t if terms is None else terms + t
        for k in ("tp", "fp", "fn"):
            agg[k] += res[k]
        agg["n_truth"] += res["n_truth"]; agg["n_emitted"] += res["n_emitted"]
    return terms, agg


def main() -> int:
    t0 = time.time()
    ensure_grid_files()
    grid = load_grid(DATA)
    valid = np.load(CACHE / "valid.npy"); eligible = np.load(CACHE / "eligible.npy")
    S = np.load(CACHE / "surface.npy")
    folds = list(spatial.folds(grid.catalogue, eligible, buffer_px=80))
    dcat = ndi.distance_transform_edt(~grid.catalogue)
    allowed = eligible & (dcat > COLLAR_PX)
    ys, xs = np.nonzero(allowed)
    order = np.argsort(-S[ys, xs].astype(np.float64), kind="mergesort")
    ys, xs = ys[order], xs[order]
    vals = S[ys, xs].astype(np.float64)[order]
    del order

    terms, rows = {}, {}
    for sep in SEPS:
        for K in BUDGETS:
            name = f"dot{sep}-K{K}"
            m = grow(ys, xs, allowed, K, sep_r=sep)
            t, a = score_field(m.astype(np.float32), folds, valid)
            terms[name] = t
            rows[name] = {"kind": "sweep", "sep_px": sep, "budget": K,
                          "n_emitted": a["n_emitted"], "tpw": a["tp"], "fpw": a["fp"],
                          "fnw": a["fn"], "n_truth": a["n_truth"],
                          "credit_per_px": a["tp"] / max(a["n_emitted"], 1),
                          "px_per_withheld_truth": (a["n_emitted"] / max(a["n_truth"], 1)),
                          "dti_manual": a["tp"] / max(a["tp"] + 0.2 * a["fp"] + 0.8 * a["fn"], 1e-12)}
            print(f"{name:22s} n={a['n_emitted']:>8} dti={rows[name]['dti_manual']:.5f} "
                  f"c/px={rows[name]['credit_per_px']:.4f} {time.time()-t0:.0f}s", flush=True)
            del m
    # the nine focus rasters, same folds, same evaluator
    ledger = json.loads((ROOT / "evidence/calibration/reported_raster_bytes.json").read_text())
    seen = set()
    for rec in ledger["records"]:
        if rec.get("status") != "ok":
            continue
        key = rec["sha256"][:12]
        if key in seen:
            continue
        seen.add(key)
        p = ROOT / rec["path"]
        if not p.exists():
            continue
        with rasterio.open(p) as ds:
            a = np.asarray(ds.read(1), np.float32)
        pred = np.where(grid.footprint & np.isfinite(a), np.clip(a, 0, 1), 0).astype(np.float32)
        name = f"PUB-{rec['repo'].split('/')[-1]}-{key}"
        t, ag = score_field(pred, folds, valid)
        terms[name] = t
        nz = int((pred > 0).sum())
        rows[name] = {"kind": "published", "repo": rec["repo"], "name": rec["name"],
                      "reported_score": rec["score"], "n_emitted": nz,
                      "tpw": ag["tp"], "fpw": ag["fp"], "fnw": ag["fn"],
                      "n_truth": ag["n_truth"],
                      "credit_per_px": ag["tp"] / max(nz, 1),
                      "holdout_dti_on_this_instrument": ag["tp"] / max(
                          ag["tp"] + 0.2 * ag["fp"] + 0.8 * ag["fn"], 1e-12)}
        print(f"{name:22s} n={nz:>8} c/px={rows[name]['credit_per_px']:.4f} "
              f"reported={rec['score']:.4f} {time.time()-t0:.0f}s", flush=True)
        del pred

    summ = shared.pooled_summary(terms, draws=1500, seed=20261031,
                                 candidate="dot2.8-K37654")
    for name, r in rows.items():
        r["pooled"] = summ["scores"].get(name, {})
    # fit c(K) = c0 * (K/37654)**-gamma on the sweep, per separation
    fits = {}
    for sep in SEPS:
        sel = [r for r in rows.values() if r["kind"] == "sweep" and r["sep_px"] == sep]
        K = np.array([r["n_emitted"] for r in sel], float)
        c = np.array([r["credit_per_px"] for r in sel], float)
        A = np.c_[np.ones(len(K)), np.log(K)]
        coef, *_ = np.linalg.lstsq(A, np.log(np.maximum(c, 1e-12)), rcond=None)
        c0, gamma = float(np.exp(coef[0])), float(-coef[1])
        fits[f"dot{sep}"] = {"c0_at_1px": c0, "gamma": gamma,
                             "form": "c(K) = exp(coef0) * K**coef1"}
        # express c at the champion budget for interpretability
        fits[f"dot{sep}"]["c_at_37654"] = float(np.exp(coef[0] + coef[1] * np.log(37_654)))
        rec = {}
        for G in GS:
            grid_k = np.exp(np.linspace(np.log(2_000), np.log(4e6), 220))
            ck = np.exp(coef[0]) * grid_k ** coef[1]
            dti = 5.0 * ck * grid_k / (grid_k + 4.0 * G)
            j = int(np.argmax(dti))
            rec[f"G{G}"] = {"argmax_budget_px": int(grid_k[j]),
                            "model_dti_at_argmax": float(dti[j]),
                            "model_dti_at_37654": float(np.interp(
                                np.log(37_654), np.log(grid_k), dti)),
                            "ratio": float(dti[j] / max(np.interp(
                                np.log(37_654), np.log(grid_k), dti), 1e-12))}
        fits[f"dot{sep}"]["scale_recommendation_by_hidden_truth_size"] = rec
    out = {"schema": "gemsdoe.scale-law.v1", "evidence_class": "HOLDOUT-DTI (never a score)",
           "evaluator_version": shared.VERSION,
           "withheld_positive_px": int(sum(int(f["truth"].sum()) for f in folds)),
           "surface": (ROOT / ".cache/emission/field_meta.json").read_text(),
           "rows": rows, "pooled": summ["scores"], "paired": summ["paired_differences"],
           "scale_fits": fits,
           "caveats": [
               "the swept field is an unsupervised multi-physics coherence ridge, not the "
               "supervised surface the focus sites used, so its absolute c(K) level is not "
               "the family's level - only its SHAPE transfers",
               "published rows are scored against withheld catalogue segments, which is not "
               "the organiser's hidden expert labels",
               "the |G| grid is a sensitivity band, not an estimate of the private label set",
           ]}
    (EV / "scale_law.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("\n=== scale law ===")
    for sep in SEPS:
        f = fits[f"dot{sep}"]
        print(f"dot{sep}: gamma={f['gamma']:.3f} c(37654)={f['c_at_37654']:.4f}")
        for G, v in f["scale_recommendation_by_hidden_truth_size"].items():
            print(f"   {G:8s} argmax K={v['argmax_budget_px']:>8} "
                  f"model DTI {v['model_dti_at_argmax']:.4f} vs at 37,654 "
                  f"{v['model_dti_at_37654']:.4f} (x{v['ratio']:.2f})")
    print("\n=== published rasters on this instrument (apples to apples) ===")
    pub = sorted([r for r in rows.values() if r["kind"] == "published"],
                 key=lambda r: -r["reported_score"])
    print(f"{'reported':>9} {'c/px':>8} {'holdout':>8} {'n_emitted':>10}  file")
    for r in pub[:16]:
        print(f"{r['reported_score']:9.4f} {r['credit_per_px']:8.4f} "
              f"{r['holdout_dti_on_this_instrument']:8.5f} {r['n_emitted']:10}  "
              f"{r['repo'].split('/')[-1]}:{r['name'][:40]}")
    print("wrote", EV / "scale_law.json", f"in {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

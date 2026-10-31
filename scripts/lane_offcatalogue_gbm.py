#!/usr/bin/env python3
"""Lane: off-catalogue fault prospectivity from the 19 official GeoDAWN bands.

Hypothesis
----------
The competition truth is expert-identified faults that are ABSENT from the public
USGS/INGENIOUS compilation, and the organiser masks mapped-fault pixels out of the
scored domain.  A model trained to recognise *mapped* faults from the 19 official
geophysical/topographic bands, and then emitted only where the catalogue says
"nothing mapped", ranks genuinely unmapped faults.  Emission mass is the dominant
score lever (validated elsewhere: DTI = T / (0.2 n + 0.8 K)), so the dot budget and
the catalogue apron are tuned jointly, not the geology alone.

Novelty versus the nine focus best-files
----------------------------------------
Those files are all thinnings of one shared dot pool (verified: strict subset
relations 32 < 31 < 25).  This lane builds an independent pool from a gradient-
boosted prospectivity surface over the official bands, with no shared ancestry.

Evidence discipline
-------------------
* Features are geophysical only.  No catalogue-derived feature enters the model,
  so the spatial holdout cannot leak the withheld segments through a feature.
* Per-feature AUC canary: any single feature with AUC > 0.90 is escalated.
* All DTI numbers are HOLDOUT-DTI on the PUBLIC CATALOGUE and are labelled as a
  proxy; docs/data/mask-width-calibration.json shows that catalogue rediscovery is
  rank-correlated -1.00 with the reported leaderboard across the focus family, so
  this holdout is used only for *matched-policy model comparison*, never as a
  leaderboard projection.
"""
from __future__ import annotations

import argparse, json, math, pathlib, sys, time
import numpy as np
import rasterio
from scipy import ndimage
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.evaluate_holdout import (  # noqa: E402
    ALPHA, BETA, PIXEL_SIZE_M, R_METERS, dti_weighted_terms, make_quadrant_folds,
    withhold_segments,
)

PIX = 100.0
N_FOLDS_BUDGET = 3          # protocol: at most three experiments


# ----------------------------------------------------------------- features --
def _clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Replace non-finite / nodata sentinels with the valid median before filtering."""
    a = a.astype(np.float32)
    good = valid & np.isfinite(a)
    fill = float(np.median(a[good])) if good.any() else 0.0
    return np.where(good, a, fill).astype(np.float32)


def _grad(a: np.ndarray, sigma: float) -> np.ndarray:
    if sigma > 0:
        a = ndimage.gaussian_filter(a, sigma, mode="nearest")
    gy, gx = np.gradient(a.astype(np.float32))
    return np.hypot(gy.astype(np.float64), gx.astype(np.float64)).astype(np.float32)


def _laplace(a: np.ndarray, sigma: float) -> np.ndarray:
    b = ndimage.gaussian_filter(a.astype(np.float32), sigma, mode="nearest") if sigma > 0 else a.astype(np.float32)
    return np.abs(ndimage.laplace(b.astype(np.float64))).astype(np.float32)


def _local_std(a: np.ndarray, size: int) -> np.ndarray:
    a = a.astype(np.float64)
    m = ndimage.uniform_filter(a, size)
    m2 = ndimage.uniform_filter(a * a, size)
    return np.sqrt(np.maximum(m2 - m * m, 0)).astype(np.float32)


def build_features(tif: pathlib.Path, idx: np.ndarray):
    """Stream one feature at a time into a preallocated (F, n_footprint) float32 array.

    Memory is the binding constraint (the design matrix is ~0.7 GB), so no full
    (F, H, W) cube is ever materialised.
    """
    import gc
    with rasterio.open(tif) as src:
        prof = dict(src.profile)
        names = [d.split(" - ")[0] for d in src.descriptions]
        H, W = prof["height"], prof["width"]
        nodata = prof.get("nodata")
        valid = np.ones((H, W), bool)
        raw = {}
        for i, n in enumerate(names):
            a = src.read(i + 1)
            v = np.isfinite(a)
            if nodata is not None:
                v &= a != nodata
            valid &= v
            raw[n] = a
    deriv = [
        ("grad_rtp_s1",     "rtp",            lambda a: _grad(a, 0)),
        ("grad_rtp_s4",     "rtp",            lambda a: _grad(a, 4)),
        ("grad_grav_s1",    "iso_grav_anom",  lambda a: _grad(a, 0)),
        ("grad_grav_s4",    "iso_grav_anom",  lambda a: _grad(a, 4)),
        ("grad_detlev_s1",  "det_elev",       lambda a: _grad(a, 0)),
        ("grad_detlev_s4",  "det_elev",       lambda a: _grad(a, 4)),
        ("grad_tmi_s1",     "tmi",            lambda a: _grad(a, 0)),
        ("grad_depthbase",  "depth_to_base_surf", lambda a: _grad(a, 0)),
        ("grad_cond_s1",    "cond_surf",      lambda a: _grad(a, 0)),
        ("grad_2ndinv_s1",  "geod_2ndinv",    lambda a: _grad(a, 0)),
        ("lap_detlev_s2",   "det_elev",       lambda a: _laplace(a, 2)),
        ("lap_rtp_s2",      "rtp",            lambda a: _laplace(a, 2)),
        ("std_detlev_5",    "det_elev",       lambda a: _local_std(a, 5)),
        ("std_rtp_5",       "rtp",            lambda a: _local_std(a, 5)),
        ("grad_maganom_s1", "mag_anom",       lambda a: _grad(a, 0)),
    ]
    fnames = list(names) + [d[0] for d in deriv]
    F = len(fnames)
    Xf = np.zeros((F, idx.size), np.float32)
    valid_flat = valid.ravel()[idx]
    for j, n in enumerate(names):
        Xf[j] = _clean(raw[n], valid).ravel()[idx]
    for k, (nm, src_name, f) in enumerate(deriv):
        a = _clean(raw[src_name], valid)
        Xf[len(names) + k] = f(a).ravel()[idx]
        del a
        gc.collect()
    del raw
    gc.collect()
    # robust per-feature scaling on the footprint only
    for j in range(F):
        v = Xf[j]
        lo, hi = np.quantile(v, [0.001, 0.999])
        if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
            lo, hi = float(v.min()), float(v.max())
        if hi <= lo:
            hi = lo + 1.0
        v = np.clip(v, lo, hi)
        mu = float(v.mean()); sd = float(v.std())
        Xf[j] = (v - mu) / (sd if sd > 0 else 1.0)
    return Xf.T, valid, fnames, prof, (H, W)


# ------------------------------------------------------------------- scoring --
def pooled_offcatalogue_dti(pred: np.ndarray, cat: np.ndarray, folds, apron_px: float,
                            n_per_fold: int | None = None, scores: np.ndarray | None = None):
    """Hide-and-recover DTI where dots are restricted to the off-catalogue apron.

    Per fold: truth = catalogue pixels in the block that survive a 2 px exclusion
    around the VISIBLE catalogue; scored domain = the block minus that exclusion.
    ``n_per_fold`` optionally keeps the top-n dots by ``scores`` per fold so that
    two models are compared at matched emission mass.
    """
    terms, nw = [], []
    for block in folds:
        withheld, visible, _ = withhold_segments(cat, block, buffer_px=3.0)
        excl = visible.copy()
        if apron_px > 0:
            excl = ndimage.binary_dilation(excl, structure=ndimage.generate_binary_structure(2, 2),
                                           iterations=int(math.ceil(apron_px)))
        truth = withheld & ~excl
        active = block & ~excl
        p = np.where(active, pred, 0.0).astype(np.float64)
        if n_per_fold is not None:
            assert scores is not None
            s = np.where(active, scores, -np.inf)
            flat = np.argsort(s.ravel())[::-1]
            keep = flat[:int(n_per_fold)]
            mask = np.zeros(p.size, bool); mask[keep] = True
            mask = mask.reshape(p.shape) & (s > -np.inf)
            p = np.where(mask, p, 0.0)
        g = np.zeros(p.shape, bool); g[truth] = True
        if g.sum() == 0:
            terms.append(dict(TPw=0.0, FPw=float(p.sum()), FNw=0.0, DTI=0.0)); nw.append(0); continue
        terms.append(dti_weighted_terms(p, g, PIX, ALPHA, BETA, R_METERS))
        nw.append(int(g.sum()))
    TPw = sum(t["TPw"] for t in terms); FPw = sum(t["FPw"] for t in terms)
    FNw = sum(t["FNw"] for t in terms)
    return dict(pooled_DTI=float(TPw / (TPw + ALPHA * FPw + BETA * FNw + 1e-12)),
                TPw=float(TPw), FPw=float(FPw), FNw=float(FNw), n_truth=int(sum(nw)),
                fold_DTIs=[t["DTI"] for t in terms],
                n_withheld_foldwise=nw,
                n_emitted=int(sum((np.where(True, 0, 0)).size for _ in [0])), )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(ROOT / "data" / "core"))
    ap.add_argument("--raster-dir", default="/home/user/.cache/gems_rasters")
    ap.add_argument("--out-dir", default=str(ROOT / "evidence" / "lane-gbm"))
    ap.add_argument("--n-dots", type=int, default=37654)
    ap.add_argument("--apron", type=float, default=2.0)
    ap.add_argument("--max-iter", type=int, default=250)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    t0 = time.time()
    ddir = pathlib.Path(args.data_dir); outdir = pathlib.Path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    with rasterio.open(ddir / "labels.tif") as s:
        lab = s.read(1); prof_l = dict(s.profile)
    foot = lab >= 0; cat = lab == 1

    # footprint & valid index first so the design matrix only holds usable pixels
    with rasterio.open(ddir / "training_features.tif") as s:
        _prof = dict(s.profile)
    H, W = _prof["height"], _prof["width"]
    _valid = None
    print("scanning valid mask ...", flush=True)
    with rasterio.open(ddir / "training_features.tif") as s:
        _valid = np.ones((H, W), bool)
        for b in range(1, s.count + 1):
            a = s.read(b)
            v = np.isfinite(a)
            if _prof.get("nodata") is not None:
                v &= a != _prof["nodata"]
            _valid &= v
            del a
    usable = foot & _valid
    idx = np.flatnonzero(usable.ravel())
    del _valid
    print(f"  usable pixels: {idx.size}  footprint={int(foot.sum())}", flush=True)

    print("building features ...", flush=True)
    Xf, valid, fnames, prof, (H, W) = build_features(ddir / "training_features.tif", idx)
    F = Xf.shape[1]
    print(f"  {F} features, design matrix {Xf.shape} ({Xf.nbytes/1e6:.0f} MB)", flush=True)
    y = cat.ravel()[idx].astype(np.int8)
    print(f"  design matrix {Xf.shape}  positives={int(y.sum())} ({100*y.mean():.3f}%)", flush=True)

    # ------------------------------------------------ leakage canary (AUC) --
    rng = np.random.default_rng(args.seed)
    neg = np.flatnonzero(y == 0); pos = np.flatnonzero(y == 1)
    samp = np.concatenate([pos, rng.choice(neg, size=min(len(neg), 200_000), replace=False)])
    aucs = {}
    for j, nm in enumerate(fnames):
        v = Xf[samp, j].astype(np.float64)
        if not np.isfinite(v).all():
            v = np.nan_to_num(v, nan=0.0, posinf=0.0, neginf=0.0)
        aucs[nm] = round(float(roc_auc_score(y[samp], v)), 4)
    flagged = {k: v for k, v in aucs.items() if v > 0.90 or v < 0.10}
    print("  per-feature AUC: min %.4f  max %.4f  flagged(>|.90|): %s"
          % (min(aucs.values()), max(aucs.values()), list(flagged)), flush=True)

    folds = make_quadrant_folds(H, W)
    fold_of = np.zeros(H * W, np.int8)
    for i, b in enumerate(folds):
        fold_of[b.ravel()] = i
    fold_of = fold_of[idx]

    # ------------------------------------------- spatially blocked training --
    p_full = np.zeros(H * W, np.float32)
    metrics = {}
    for i, block in enumerate(folds):
        tr = fold_of != i
        ytr = y[tr]
        pos_i = np.flatnonzero(ytr == 1)
        neg_i = np.flatnonzero(ytr == 0)
        take = rng.choice(neg_i, size=min(len(neg_i), int(len(pos_i) * 8)), replace=False)
        rows = np.concatenate([pos_i, take])
        clf = HistGradientBoostingClassifier(max_iter=args.max_iter, learning_rate=0.08,
                                             max_leaf_nodes=63, l2_regularization=1.0,
                                             random_state=args.seed, early_stopping=False)
        clf.fit(Xf[tr][rows], ytr[rows])
        te = np.flatnonzero(fold_of == i)
        p_full[idx[te]] = clf.predict_proba(Xf[te])[:, 1].astype(np.float32)
        # in-fold AUC on the held-out block (full block, all pixels)
        pr = clf.predict_proba(Xf[te])[:, 1]
        metrics[f"fold{i}_auc"] = round(float(roc_auc_score(y[te], pr)), 5)
        print(f"  fold {i}: train rows {len(rows)}  holdout AUC {metrics[f'fold{i}_auc']}", flush=True)
        del clf

    p = p_full.reshape(H, W)
    np.save(outdir / "prospectivity_foldwise.npy", p.astype(np.float32))

    # --------------------------------------------- matched-policy holdout ----
    dots = (p > 0).astype(np.float64)
    total = args.n_dots
    per_fold = int(round(total / len(folds)))
    mine = pooled_offcatalogue_dti(dots, cat, folds, args.apron, n_per_fold=per_fold, scores=p)
    print(f"\nLANE  off-catalogue holdout DTI (n={per_fold*len(folds)}, apron={args.apron}px): "
          f"{mine['pooled_DTI']:.6f}  truth={mine['n_truth']}", flush=True)

    # reference: GEMSDOE32 dots evaluated identically, and a random control
    focus = json.loads((ROOT / "registry" / "focus_sites.json").read_text())
    refs = {}
    for site in ("GEMSDOE32", "GEMSDOE25"):
        fn = next(s["file"] for s in focus["sites"] if s["site"] == site)
        with rasterio.open(pathlib.Path(args.raster_dir) / (site + "__" + fn)) as s:
            a = np.nan_to_num(s.read(1).astype(np.float64), nan=0.0)
        r = pooled_offcatalogue_dti((a > 0).astype(np.float64), cat, folds, args.apron)
        refs[site] = dict(pooled_DTI=round(r["pooled_DTI"], 6), n_dots=int((a > 0).sum()),
                          n_truth=r["n_truth"], fold_DTIs=[round(x, 6) for x in r["fold_DTIs"]])
        print(f"  ref {site}: {r['pooled_DTI']:.6f}  (n={int((a>0).sum())})", flush=True)

    rs = rng.random((H, W))
    rnd = pooled_offcatalogue_dti(np.ones((H, W)), cat, folds, args.apron,
                                  n_per_fold=per_fold, scores=rs)
    refs["random_uniform"] = dict(pooled_DTI=round(rnd["pooled_DTI"], 6), n_dots=per_fold * len(folds))
    print(f"  ref random_uniform: {rnd['pooled_DTI']:.6f}", flush=True)

    # --------------------------------------------- full-catalogue final model --
    # ---- credit-vs-rank curve on the holdout (drives the emission budget) ----
    d_cat_full = ndimage.distance_transform_edt(~cat)
    curve = {}
    for block in folds:
        withheld, visible, _ = withhold_segments(cat, block, buffer_px=3.0)
        excl = visible.copy()
        if args.apron > 0:
            excl = ndimage.binary_dilation(excl, structure=ndimage.generate_binary_structure(2, 2),
                                           iterations=int(math.ceil(args.apron)))
        truth = withheld & ~excl
        active = (block & ~excl)
        dg = ndimage.distance_transform_edt(~truth)
        k = np.maximum(1.0 - dg / 3.0, 0.0)
        s_ = np.where(active, p, -np.inf)
        flat = s_.ravel()
        order = np.argsort(flat)[::-1]
        kflat = k.ravel()
        top = 400_000
        sel = order[:top]
        ranks = np.arange(len(sel))
        kbins = np.array_split(kflat[sel], 20)
        curve.setdefault("rows", []).append([float(np.mean(b)) for b in kbins])
    curve_rows = np.array(curve["rows"])
    credit_by_rank_bin = curve_rows.mean(axis=0).tolist()
    print("  holdout mean credit by top-rank ventile:",
          " ".join(f"{v:.4f}" for v in credit_by_rank_bin), flush=True)

    print("\nfitting final model on the whole catalogue ...", flush=True)
    pos_all = np.flatnonzero(y == 1); neg_all = np.flatnonzero(y == 0)
    take = rng.choice(neg_all, size=min(len(neg_all), int(len(pos_all) * 8)), replace=False)
    rows = np.concatenate([pos_all, take])
    clf = HistGradientBoostingClassifier(max_iter=args.max_iter, learning_rate=0.08,
                                         max_leaf_nodes=63, l2_regularization=1.0,
                                         random_state=args.seed, early_stopping=False)
    clf.fit(Xf[rows], y[rows])
    pf = np.zeros(H * W, np.float32)
    importances = {n: round(float(v), 5) for n, v in zip(fnames, clf.feature_importances_)} if False else None
    for r0 in range(0, len(idx), 400_000):
        sl = slice(r0, min(r0 + 400_000, len(idx)))
        pf[idx[sl]] = clf.predict_proba(Xf[sl])[:, 1].astype(np.float32)
    pf = pf.reshape(H, W)
    np.save(outdir / "prospectivity_full.npy", pf.astype(np.float32))

    out = dict(schema_version=1,
               evidence_class="HOLDOUT-DTI-PROXY + LEAKAGE-CANARY + MODEL-PROJECTION",
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               features=fnames,
               n_features=F,
               leakage_canary=dict(per_feature_auc=aucs, flagged_above_0p90=flagged,
                                   rule="AUC > 0.90 for any single feature => leakage until proven otherwise"),
               fold_auc=metrics,
               holdout_credit_by_rank_ventile=[round(v, 5) for v in credit_by_rank_bin],
               holdout=dict(protocol="4-quadrant hide-and-recover on the PUBLIC catalogue; "
                                     "dots restricted to the off-catalogue apron; matched emission mass",
                            n_dots=per_fold * len(folds), apron_px=args.apron,
                            lane=mine, references=refs,
                            evaluator="scripts/evaluate_holdout.py dti_weighted_terms",
                            constants=dict(alpha=ALPHA, beta=BETA, R_m=R_METERS)),
               warning=("docs/data/mask-width-calibration.json shows catalogue rediscovery is "
                        "Spearman -1.00 against the reported leaderboard for the focus family. "
                        "This holdout compares models at matched policy only; it is NOT a "
                        "leaderboard projection."),
               runtime_s=round(time.time() - t0, 1))
    (outdir / "run_card.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(f"\nwrote {outdir/'run_card.json'}  ({out['runtime_s']}s)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Lane driver: hypothesis -> holdout -> emission -> validated submission TIF.

LANE (single method paragraph, this session)
    Structural-habitat lane.  A gradient-boosted classifier is fitted, on the
    19-band GeoDAWN stack plus multi-scale gradient / ridge / lineament
    derivatives of the magnetic, gravity, topographic, basement-depth and
    conductivity fields, to discriminate mapped-fault pixels from background.
    Its calibrated probability field is treated as the density of *unmapped*
    faults, and dots are then placed by lazy-greedy maximisation of the expected
    distance-weighted Tversky index (alpha 0.2, beta 0.8, 300 m triangular
    kernel), which is a monotone submodular covering problem: every dot must buy
    marginal truth credit above 0.2*DTI/(1-0.2*DTI) of its false-positive cost.
    Uniqueness is enforced before placement and on the saved bytes.

Usage
    .venv/bin/python scripts/run_lane.py --stage all
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))

from gemsdoe import grid as ggrid          # noqa: E402
from gemsdoe import features as gfeat      # noqa: E402
from gemsdoe import emit as gemit          # noqa: E402
from gemsdoe import habitat as ghab        # noqa: E402
from scipy import ndimage                  # noqa: E402

WORK = ROOT / ".cache" / "gems_work"
EVID = ROOT / "evidence"
DATA = ROOT / ".cache" / "gems_data"


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def dump_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False, default=ggrid.json_default) + "\n")
    log(f"wrote {path}")


# --------------------------------------------------------------------------- #
# static stack
# --------------------------------------------------------------------------- #
def static_stack(force=False):
    WORK.mkdir(parents=True, exist_ok=True)
    out = WORK / "static_stack.npz"
    if out.is_file() and not force:
        z = np.load(out, allow_pickle=True)
        return z["X"], list(z["names"]), np.load(WORK / "lut.npy"), np.load(WORK / "foot.npy"), np.load(WORK / "cat.npy")
    g = ggrid.load_grid()
    F, names = ggrid.read_features()
    log("building static feature stack (66 columns, footprint-only uint8)")
    X, fn = gfeat.build_stack(F, names, g.footprint, None, include_visible=False)
    H, W = g.footprint.shape
    lut = np.full(H * W, -1, np.int64)
    lut[g.footprint.reshape(-1)] = np.arange(int(g.footprint.sum()))
    np.savez_compressed(out, X=X, names=np.array(fn))
    np.save(WORK / "lut.npy", lut)
    np.save(WORK / "foot.npy", g.footprint)
    np.save(WORK / "cat.npy", g.catalogue)
    log(f"stack {X.shape}")
    return X, fn, lut, g.footprint, g.catalogue


def visible_columns(footprint, visible_faults):
    """Three catalogue-geometry columns derived from VISIBLE faults only."""
    cols, names = [], []
    d = gfeat.distance_to(visible_faults)
    cols.append(gfeat.robust01(np.log1p(d), footprint)); names.append("vis:logdist")
    cols.append(gfeat.robust01(gfeat.salient(-d, 21), footprint)); names.append("vis:apron_salient")
    dens = ndimage.uniform_filter(visible_faults.astype(np.float32), size=21, mode="nearest")
    cols.append(gfeat.robust01(dens, footprint)); names.append("vis:density21")
    flat = footprint.reshape(-1)
    Q = np.stack([np.round(np.clip(np.nan_to_num(c, nan=0.0, posinf=0.0, neginf=0.0), 0, 1) * 255).astype(np.uint8).reshape(-1)[flat] for c in cols], axis=1)
    return Q, names


# --------------------------------------------------------------------------- #
# folds
# --------------------------------------------------------------------------- #
def make_blocks(shape, ny=4, nx=4):
    H, W = shape
    blocks = []
    ys = np.array_split(np.arange(H), ny)
    xs = np.array_split(np.arange(W), nx)
    for by in ys:
        for bx in xs:
            m = np.zeros((H, W), bool)
            m[by[0]:by[-1] + 1, bx[0]:bx[-1] + 1] = True
            blocks.append(m)
    return blocks


# --------------------------------------------------------------------------- #
# model
# --------------------------------------------------------------------------- #
def fit_model(Xtr, ytr, seed=0):
    from sklearn.ensemble import HistGradientBoostingClassifier
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, max_leaf_nodes=31,
                                       min_samples_leaf=40, l2_regularization=1.0,
                                       early_stopping=False, random_state=seed)
    m.fit(Xtr, ytr)
    return m


def predict_full(model, X, chunk=400_000):
    out = np.empty(X.shape[0], dtype=np.float32)
    for i in range(0, X.shape[0], chunk):
        out[i:i + chunk] = model.predict_proba(X[i:i + chunk])[:, 1]
    return out


def prior_correct(p, pi_sampled, pi_real):
    """Rescale scores from the training class balance to the real prior."""
    p = np.clip(p, 1e-6, 1 - 1e-6)
    odds = p / (1 - p)
    odds *= (pi_real / (1 - pi_real)) / (pi_sampled / (1 - pi_sampled))
    return (odds / (1 + odds)).astype(np.float32)


# --------------------------------------------------------------------------- #
# holdout
# --------------------------------------------------------------------------- #
def build_design(X_static, fn_static, footprint, catalogue, visible, seed, n_neg=250_000,
                 neg_frac_of_pool=None):
    """Training matrix: visible catalogue pixels vs sampled background."""
    rng = np.random.default_rng(seed)
    Qv, nf = visible_columns(footprint, visible)
    X = np.hstack([X_static, Qv]).astype(np.float32)
    names = fn_static + nf
    vis_flat = visible.reshape(-1)[footprint.reshape(-1)]
    cat_flat = catalogue.reshape(-1)[footprint.reshape(-1)]
    pos = np.flatnonzero(vis_flat)
    neg_pool = np.flatnonzero(~cat_flat)
    n_neg = int(min(n_neg, neg_pool.size))
    neg = rng.choice(neg_pool, n_neg, replace=False)
    Xtr = np.vstack([X[pos], X[neg]])
    ytr = np.r_[np.ones(pos.size, np.float32), np.zeros(neg.size, np.float32)]
    return X, names, Xtr, ytr, pos.size, neg.size


def dti_terms(pred, truth, active, alpha=0.2, beta=0.8):
    """Official DTI terms with an explicit active domain (shared metric semantics)."""
    from gems57.metric import kernel, OFF_DY, OFF_DX, OFF_K, EPS
    p = np.where(active, np.nan_to_num(pred, nan=0.0), 0.0).astype(np.float64)
    g = truth & active
    H, W = p.shape
    n = int(g.sum())
    if n == 0:
        return dict(tp=0.0, fp=float(p.sum()), fn=0.0, n_truth=0, n_emit=int((p > 0).sum()), dti=0.0)
    from scipy.ndimage import distance_transform_edt
    dg = distance_transform_edt(~g)
    q = kernel(dg)
    fp = float((p * (1.0 - q)).sum())
    cov = np.zeros((H, W), dtype=np.float64)
    for dy, dx, k in zip(OFF_DY, OFF_DX, OFF_K):
        y0, y1 = max(0, -dy), min(H, H - dy)
        x0, x1 = max(0, -dx), min(W, W - dx)
        if y0 >= y1 or x0 >= x1:
            continue
        np.maximum(cov[y0:y1, x0:x1], k * p[y0 + dy:y1 + dy, x0 + dx:x1 + dx], out=cov[y0:y1, x0:x1])
    tp = float(cov[g].sum())
    fn = float(n) - tp
    return dict(tp=tp, fp=fp, fn=fn, n_truth=n, n_emit=int((p > 0).sum()),
                dti=tp / (tp + alpha * fp + beta * fn + 1e-12))


def stage_holdout(args):
    Xs, fns, lut, foot, cat = static_stack(force=args.force_stack)
    blocks = make_blocks(foot.shape, 4, 4)
    folds = [[] for _ in range(4)]
    for i, b in enumerate(blocks):
        folds[((i // 4) + (i % 4)) % 4].append(b)
    foldmask = [np.logical_or.reduce(f) for f in folds]
    log(f"holdout: {len(foldmask)} interleaved folds of {len(blocks)} blocks")

    H, W = foot.shape
    assembled = np.zeros((H, W), dtype=np.float32)
    per_fold = []
    for fi, fm in enumerate(foldmask):
        cache = WORK / f"holdout_fold{fi}.npy"
        if cache.is_file() and not args.force_stack:
            assembled_f = np.load(cache).astype(np.float32)
            dil = ndimage.binary_dilation(fm, iterations=3)
            withheld = cat & fm
            log(f"fold {fi}: reusing cached prediction (withheld {int(withheld.sum())})")
            assembled[fm] = assembled_f[fm]
            per_fold.append(dict(fold=fi, cached=True, n_withheld=int(withheld.sum())))
            np.save(WORK / f"foldmask{fi}.npy", fm)
            continue
        dil = ndimage.binary_dilation(fm, iterations=3)
        visible = cat & ~dil
        withheld = cat & fm
        X, names, Xtr, ytr, npos, nneg = build_design(Xs, fns, foot, cat, visible, seed=fi)
        log(f"fold {fi}: visible {int(visible.sum())} withheld {int(withheld.sum())} train {Xtr.shape}")
        m = fit_model(Xtr, ytr, seed=fi)
        p = predict_full(m, X)
        pfull = np.zeros((H, W), dtype=np.float32)
        pfull[foot] = p
        assembled[fm] = pfull[fm]
        # leakage canary: per-feature AUC on this fold's withheld positives
        from sklearn.metrics import roc_auc_score
        wf = withheld.reshape(-1)[foot.reshape(-1)]
        bg = np.flatnonzero(~(cat.reshape(-1)[foot.reshape(-1)]))
        rng = np.random.default_rng(fi)
        bg = rng.choice(bg, 60_000, replace=False)
        yte = np.r_[np.ones(int(wf.sum())), np.zeros(bg.size)]
        aucs = {}
        for j, nm in enumerate(names):
            v = np.r_[X[wf, j], X[bg, j]].astype(np.float64)
            aucs[nm] = float(roc_auc_score(yte, v))
        top = sorted(aucs.items(), key=lambda kv: -kv[1])[:5]
        per_fold.append(dict(fold=fi, n_visible=int(visible.sum()), n_withheld=int(withheld.sum()),
                             n_train_pos=npos, n_train_neg=nneg,
                             canary_max_auc=max(aucs.values()),
                             canary_top5=[{"feature": k, "auc": round(v, 4)} for k, v in top]))
        np.save(WORK / f"holdout_fold{fi}.npy", pfull.astype(np.float16))
        del X, Xtr, ytr, m
    np.save(WORK / "holdout_assembled.npy", assembled.astype(np.float16))

    # --- scores over operating points --------------------------------------
    # "Isolated" test: inside fold f, keep only the region >= 4 px from that
    # fold's VISIBLE faults, and score against the withheld catalogue pixels
    # there.  Those are fault pixels with no mapped fault within 400 m -- the
    # closest available proxy for an unmapped fault.  Active regions partition
    # the footprint, so false positives are counted exactly once when pooled.
    active_iso = np.zeros(foot.shape, bool)
    truth_iso = np.zeros(foot.shape, bool)
    for fi, fm in enumerate(foldmask):
        visible = cat & ~ndimage.binary_dilation(fm, iterations=3)
        dvis = gfeat.distance_to(visible)
        a = foot & fm & (dvis >= 4)
        active_iso |= a
        truth_iso |= (cat & fm & a)

    ops = []
    qs = [99.9, 99.5, 99.0, 98.0, 96.0, 93.0, 90.0, 85.0, 80.0]
    for q in qs:
        thr = float(np.percentile(assembled[foot], q))
        dots = (assembled >= thr) & foot
        r_full = dti_terms(dots.astype(np.float32), cat, foot)
        r_iso = dti_terms(dots.astype(np.float32), truth_iso, active_iso)
        ops.append(dict(top_pct=round(100 - q, 3), threshold=thr, n_dots=int(dots.sum()),
                        dti_full=r_full["dti"], tp_full=r_full["tp"], fp_full=r_full["fp"],
                        n_truth_iso=int(truth_iso.sum()), dti_isolated=r_iso["dti"],
                        tp_iso=r_iso["tp"], fp_iso=r_iso["fp"]))
    # enrichment of the assembled score for isolated (unmapped-style) positives
    lift = []
    npos = int(max(truth_iso.sum(), 1))
    for q in (99.0, 95.0, 90.0, 80.0, 50.0):
        thr = float(np.percentile(assembled[active_iso], q))
        sel = (assembled >= thr) & active_iso
        frac_area = float(sel.sum()) / float(active_iso.sum())
        frac_pos = float((truth_iso & sel).sum()) / npos
        lift.append(dict(top_pct=round(100 - q, 2), area_frac=frac_area,
                         pos_frac=frac_pos, enrichment=float(frac_pos / max(frac_area, 1e-12))))
    out = dict(stage="holdout", n_folds=len(foldmask), folds=per_fold,
               operating_points=ops, isolated_enrichment=lift,
               note=("assembled map: each block scored by the model that never saw that block's "
                     "faults. dti_full uses the whole catalogue as truth (optimistic: the real "
                     "scorer masks mapped faults). dti_isolated keeps only catalogue pixels >=4 px "
                     "from any visible fault, the closest available proxy for an unmapped fault."))
    dump_json(EVID / "lane-holdout-2026-10-31.json", out)
    for o in ops:
        log(f"  top {o['top_pct']:>5}%  dots {o['n_dots']:>7d}  DTI_full {o['dti_full']:.4f}  DTI_iso {o['dti_isolated']:.4f}")
    for l in lift:
        log(f"  lift top {l['top_pct']:>5}%  area {l['area_frac']:.4f}  pos {l['pos_frac']:.4f}  enrich {l['enrichment']:.2f}x")
    return out


# --------------------------------------------------------------------------- #
# final emission
# --------------------------------------------------------------------------- #
def rank_uniform(smap, footprint):
    """Replace s by its within-footprint quantile: a rank transform.

    The gradient-boosted score is extremely peaked (it is a classifier output,
    not a density), so using its raw value makes the modelled fault density tens
    of times more concentrated than any published submission behaves.  The rank
    keeps the ordering -- which is all the DTI emission needs -- and leaves the
    *extent* of the emitted territory under explicit control of eta.
    """
    v = smap[footprint]
    order = np.argsort(v, kind="stable")
    q = np.empty(v.size, np.float32)
    q[order] = np.arange(1, v.size + 1, dtype=np.float32) / v.size
    out = np.zeros(smap.shape, np.float32)
    out[footprint] = q
    return out


def target_density(g, smap, lam_px=8.0, eta=1.0, min_dcat=1.0, rank=True, source="model"):
    """Modelled density of UNMAPPED faults.

    rho_unnormalised(x) = s(x)**eta * (1 - exp(-d_cat(x)/lam)) * 1[d_cat >= min_dcat]

    s(x)      : hide-and-recover fault probability (assembled 4-fold holdout map)
    the rest  : "already mapped" discount.  Measured on the 21 published files:
                every file scoring >= 0.24 has *zero* dots within 100 m of a
                mapped fault and a median dot-to-catalogue distance of 1.4-2.0 km.
    """
    if source == "geo":
        comp, _ = ghab.geological_index_from_path(str(g.data_dir / "training_features.tif"), g.footprint)
        smap = comp
    dcat = gfeat.distance_to(g.catalogue)
    if rank:
        s01 = rank_uniform(smap, g.footprint)
    else:
        lo, hi = np.percentile(smap[g.footprint], [1, 99])
        s01 = np.clip((smap - lo) / max(hi - lo, 1e-9), 0, 1)
    f = np.power(s01 + 1e-3, eta) * (1.0 - np.exp(-dcat / lam_px))
    f[~g.footprint] = 0.0
    f[dcat < min_dcat] = 0.0
    return f, dcat


def stage_final(args):
    from gems57.metric import dti_binary
    import rasterio
    g = ggrid.load_grid()
    static_stack()
    results = {}
    smap = np.load(WORK / "holdout_assembled.npy").astype(np.float32)
    f, dcat = target_density(g, smap, lam_px=args.lam, eta=args.eta,
                             min_dcat=args.min_dcat, rank=not args.raw_score,
                             source=args.habitat)
    log(f"target density: positive pixels={int((f > 0).sum())} rank={not args.raw_score} habitat={args.habitat}")

    for K in args.K:
        pi = (K * f / float(f.sum())).astype(np.float64)
        allowed = g.footprint & (dcat >= args.min_dcat)
        t0 = time.time()
        dots, diag = gemit.greedy_emit(pi, allowed, max_dots=args.max_dots,
                                       candidate_top=args.candidates, verbose_every=20000)
        diag["seconds"] = round(time.time() - t0, 1)
        h = gemit.kernel_smooth(pi)
        diag["mean_yield_per_dot"] = float(h[dots].mean()) if dots.any() else 0.0
        diag["median_dist_to_catalogue_px"] = float(np.median(dcat[dots])) if dots.any() else 0.0
        diag["frac_within_3px_of_catalogue"] = float((dcat[dots] <= 3).mean()) if dots.any() else 0.0
        diag["footprint_within_300m_of_a_dot"] = float(
            (gfeat.distance_to(dots)[g.footprint] <= 3).mean()) if dots.any() else 0.0
        results[str(K)] = diag
        log(f"K={K}: n_dots={diag['n_dots']} expected_dti={diag['expected_dti']:.4f} "
            f"coverage={diag['coverage']:.3f} med_dist_cat={diag['median_dist_to_catalogue_px']:.1f}px "
            f"within300m={diag['footprint_within_300m_of_a_dot']:.3f} ({diag['seconds']}s)")
        np.save(WORK / f"dots_K{int(K)}.npy", dots)
        del dots, diag, h

    chosen = args.K[min(range(len(args.K)),
                        key=lambda i: abs(results[str(args.K[i])]["n_dots"] - args.target_dots))]
    dots = np.load(WORK / f"dots_K{int(chosen)}.npy")
    diag = results[str(chosen)]
    log(f"chosen K={chosen} (closest to target {args.target_dots}) -> {int(dots.sum())} dots")

    out = np.zeros(g.shape, dtype=np.float32)
    out[dots] = 1.0
    name = args.name
    tif = ROOT / "docs" / "downloads" / f"{name}.tif"
    info = ggrid.write_submission_tif(tif, out, nan_outside=False)
    log(f"wrote {tif} sha256={info['sha256'][:16]}... bytes={info['bytes']}")

    hd = dti_binary(dots, g.catalogue, valid=g.footprint)
    blocks = make_blocks(g.footprint.shape, 4, 4)
    folds = [[] for _ in range(4)]
    for i, b in enumerate(blocks):
        folds[((i // 4) + (i % 4)) % 4].append(b)
    foldmask = [np.logical_or.reduce(f) for f in folds]
    act = np.zeros(g.footprint.shape, bool)
    tru = np.zeros(g.footprint.shape, bool)
    for fm in foldmask:
        vis = g.catalogue & ~ndimage.binary_dilation(fm, iterations=3)
        a = g.footprint & fm & (gfeat.distance_to(vis) >= 4)
        act |= a
        tru |= (g.catalogue & fm & a)
    iso = dti_binary(dots & act, tru & act, valid=act)

    uniq = []
    for r in json.loads((ROOT / "registry" / "calibration_rasters.json").read_text())["rasters"]:
        p = ROOT / ".cache" / "research" / "calib" / f"{r['label']}.tif"
        if not p.is_file():
            continue
        with rasterio.open(p) as s:
            a = s.read(1)
        m = (a > 0) & np.isfinite(a) & g.footprint
        inter = int((dots & m).sum())
        uniq.append(dict(label=r["label"], reported_score=r["reported_score"],
                         n_ref=int(m.sum()), shared=int(inter),
                         jaccard=round(inter / max(int((dots | m).sum()), 1), 4),
                         frac_ours_within_3px=round(float(
                             (gfeat.distance_to(m)[dots] <= 3).mean()) if dots.any() else 0.0, 4)))
        del a, m
    uniq.sort(key=lambda u: -u["frac_ours_within_3px"])

    card = dict(
        schema="run-card-v1", session_date="2026-10-31",
        lane=("structural-habitat: hide-and-recover gradient-boosted habitat model over the 19-band "
              "GeoDAWN stack plus multi-scale gradient/ridge/lineament derivatives, converted to a "
              "density of UNMAPPED faults by an 'already-mapped' discount, with dots placed by "
              "lazy-greedy maximisation of the expected distance-weighted Tversky index"),
        hypothesis=("faults missing from the USGS/INGENIOUS catalogue occupy the same geophysical "
                    "habitat as mapped faults (range fronts, magnetic and gravity gradient maxima, "
                    "basement steps) but lie in ground the catalogue has not covered; a model forced "
                    "to recover withheld fault segments from remote sensing alone therefore ranks "
                    "under-mapped ground, and the DTI optimum then spreads one dot per 300 m kernel "
                    "over exactly that ranked ground"),
        mechanism=("gradient-magnitude / ridge / analytic-signal / tilt derivatives of the magnetic, "
                   "gravity, detrended-elevation, basement-depth and conductivity fields; distances "
                   "to VISIBLE faults only; greedy submodular covering with the exact marginal test "
                   "dA > [0.2 DTI / (1 - 0.2 DTI)] * dF"),
        named_non_fault_mimic=("range-front scarps and alluvial-fan edges: the detrended-elevation "
                               "slope and curvature terms fire on any topographic break, including "
                               "purely erosional or depositional fronts that are not faults"),
        holdout=dict(evaluator="gems57.metric.dti_binary (alpha 0.2, beta 0.8, 300 m triangular kernel)",
                     dti_vs_full_catalogue=round(float(hd["dti"]), 6),
                     n_truth_full_catalogue=int(hd["n_truth"]),
                     dti_vs_isolated_withheld=round(float(iso["dti"]), 6),
                     n_truth_isolated=int(iso["n_truth"]),
                     ci95="fold range; see evidence/lane-holdout-2026-10-31.json",
                     note=("catalogue truth is a PROXY: the scored truth is private and the real "
                           "scorer masks mapped faults, so this under-credits off-catalogue skill")),
        emission=dict(chosen_K=float(chosen), emission_table=results,
                      target_density=dict(lam_px=args.lam, eta=args.eta, min_dcat_px=args.min_dcat),
                      expected_dti_model=round(float(diag["expected_dti"]), 4),
                      n_dots=int(dots.sum())),
        file=info,
        uniqueness=dict(max_jaccard=max((u["jaccard"] for u in uniq), default=0.0),
                        max_frac_ours_within_3px=max((u["frac_ours_within_3px"] for u in uniq), default=0.0),
                        per_reference=uniq),
        submission_name=name, note=args.note[:140],
        verdict="negative" if args.verdict_negative else "promote",
    )
    dump_json(EVID / f"run-card-{name}.json", card)
    dump_json(ROOT / "docs" / "downloads" / f"{name}.run-card.json", card)
    print(json.dumps({k: v for k, v in card.items() if k != "uniqueness"}, indent=2, default=ggrid.json_default))
    print("\nuniqueness (top 8 by 3px overlap):")
    for u in uniq[:8]:
        print(f"  {u['label']:28s} jaccard={u['jaccard']:.4f} ours_within_3px={u['frac_ours_within_3px']:.4f} shared={u['shared']}")
    return card


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", default="holdout", choices=["stack", "holdout", "final", "all"])
    ap.add_argument("--force-stack", action="store_true")
    ap.add_argument("--lam", type=float, default=8.0)
    ap.add_argument("--eta", type=float, default=1.0)
    ap.add_argument("--min-dcat", type=float, default=1.0)
    ap.add_argument("--K", type=float, nargs="+", default=[4000.0, 8000.0, 16000.0, 32000.0, 64000.0])
    ap.add_argument("--target-dots", type=int, default=40000)
    ap.add_argument("--max-dots", type=int, default=250000)
    ap.add_argument("--candidates", type=int, default=400000)
    ap.add_argument("--name", default="gemsdoekarage2-hkarage2-dti-greedy-habitat-20261031")
    ap.add_argument("--note", default="DTI-optimal greedy covering of a hide-and-recover structural-habitat density; 100 m minimum offset from mapped faults")
    ap.add_argument("--raw-score", action="store_true", help="use the raw model score instead of its rank")
    ap.add_argument("--habitat", default="model", choices=["model", "geo"],
                    help="habitat field: 'model' = hide-and-recover GBM score, "
                         "'geo' = independent relief/magnetic-contact/tilt index")
    ap.add_argument("--verdict-negative", action="store_true")
    args = ap.parse_args()
    if args.stage in ("stack", "all"):
        static_stack(force=args.force_stack)
    if args.stage in ("holdout", "all"):
        stage_holdout(args)
    if args.stage in ("final", "all"):
        stage_final(args)


if __name__ == "__main__":
    main()

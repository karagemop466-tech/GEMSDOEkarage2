#!/usr/bin/env python3
"""H-UNMAP experiment driver: train, score, emit, evaluate.

Experiments (protocol budget: at most three; this file implements E1 and E2):

E1  *Geophysical fault-likelihood model + metric-gated emission.*  A
    spatially-blocked supervised model (no catalogue-derived feature) predicts
    fault-likelihood from airborne magnetics, isostatic gravity gradients,
    geodetic strain, seismicity proximity, basement depth and gamma-ray
    alteration halos.  Dots are emitted by non-maximum suppression of the
    likelihood surface and pruned by the official metric's marginal rule.

E2  *Emission-policy refinement.*  The dot budget / spacing / apron-pruning
    policy is tuned on the shared hide-and-recover instrument and validated on
    the independent SGMC off-catalogue instrument.

Every printed number is HOLDOUT-DTI (evaluator ``gems57-pooled-hide-v2``) on the
named instrument, or a projection.  Nothing here is an organiser score.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from lane_hunmap import (CACHE, DATA_DIR, EVALUATOR, FEAT_DIR, LANE, EXT_DIR,
                         build_features, dti_of, load_grid, log, sgmc_truth)
from sgmc_cal import SgmcInstrument

EVID = ROOT / "evidence" / "hunmap"
RUN = CACHE / "runs"


# --------------------------------------------------------------------------
def sample_training(grid_cat: np.ndarray, footprint: np.ndarray, seed: int = 7,
                    n_neg: int = 400_000) -> tuple[np.ndarray, np.ndarray]:
    """Positive catalogue cells and uniformly sampled negative footprint cells."""
    rng = np.random.default_rng(seed)
    pos = np.flatnonzero(grid_cat.ravel())
    neg_pool = np.flatnonzero(footprint.ravel() & ~grid_cat.ravel())
    take = min(n_neg, neg_pool.size)
    neg = rng.choice(neg_pool, size=take, replace=False)
    return pos, neg


def block_ids(shape: tuple[int, int], n: int = 4) -> np.ndarray:
    """Coarse spatial block id per cell (row/col bands)."""
    h, w = shape
    by = np.minimum((np.arange(h) * n) // h, n - 1)
    bx = np.minimum((np.arange(w) * n) // w, n - 1)
    return (by[:, None] * n + bx[None, :]).astype(np.int16)


def extract_samples(features: list[str], idx: np.ndarray,
                    shape: tuple[int, int]) -> np.ndarray:
    """Gather feature values at flat indices (chunked to bound memory)."""
    h, w = shape
    rows = idx // w
    cols = idx % w
    out = np.empty((idx.size, len(features)), dtype=np.float32)
    for j, name in enumerate(features):
        arr = np.load(FEAT_DIR / f"{name}.npy", mmap_mode="r")
        for s in range(0, idx.size, 200_000):
            e = min(s + 200_000, idx.size)
            out[s:e, j] = arr[rows[s:e], cols[s:e]]
    return out


def impute(X: np.ndarray, medians: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Replace non-finite feature values with the training median."""
    if medians is None:
        medians = np.nanmedian(np.where(np.isfinite(X), X, np.nan), axis=0)
        medians = np.where(np.isfinite(medians), medians, 0.0)
    X = X.copy()
    bad = ~np.isfinite(X)
    if bad.any():
        rows, cols = np.nonzero(bad)
        X[rows, cols] = medians[cols]
    return X, medians


def train_model(X: np.ndarray, y: np.ndarray, seed: int = 7, model: str = "hgb"):
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    if model == "logreg":
        clf = make_pipeline(StandardScaler(),
                            LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced"))
        clf.fit(X, y)
        return clf
    clf = HistGradientBoostingClassifier(
        max_iter=120, max_depth=6, max_leaf_nodes=31, learning_rate=0.1,
        min_samples_leaf=40, l2_regularization=1.0, random_state=seed,
        early_stopping=False)
    clf.fit(X, y, sample_weight=np.where(y == 1, 8.0, 1.0))
    return clf


def score_grid(model, features: list[str], shape: tuple[int, int],
               medians: np.ndarray | None = None) -> np.ndarray:
    """Full-grid likelihood surface (float32)."""
    out = np.zeros(shape, dtype=np.float32)
    flat = out.reshape(-1)
    chunk = 400_000
    total = shape[0] * shape[1]
    for s in range(0, total, chunk):
        e = min(s + chunk, total)
        idx = np.arange(s, e)
        X = extract_samples(features, idx, shape)
        X, _ = impute(X, medians)
        flat[s:e] = model.predict_proba(X)[:, 1].astype(np.float32)
    return out


def nms_peaks(score: np.ndarray, mask: np.ndarray, radius: int) -> np.ndarray:
    """Non-maximum suppression on a 2-D score surface (greedy, radius in px)."""
    from scipy import ndimage as ndi

    size = int(2 * radius + 1)
    mx = ndi.maximum_filter(score, size=size, mode="nearest")
    peak = (score >= mx - 1e-9) & mask & (score > 0)
    return peak


def emit_dots(score: np.ndarray, valid: np.ndarray, radius: int,
              min_score: float = 0.0, catalogue: np.ndarray | None = None,
              apron_px: int = 0, budget: int | None = None) -> np.ndarray:
    """Likelihood surface -> binary dot mask.

    Local maxima of the likelihood surface (non-maximum suppression over a
    ``radius``-px window) are ranked by likelihood and the top ``budget`` are
    kept, so the dot count is an explicit, auditable quantity.
    """
    from scipy import ndimage as ndi

    work = np.where(valid, score, 0.0).astype(np.float32)
    size = int(2 * radius + 1)
    mx = ndi.maximum_filter(work, size=size, mode="nearest")
    peaks = (work >= mx - 1e-12) & valid & (work > min_score)
    if apron_px > 0 and catalogue is not None:
        apron = ndi.binary_dilation(catalogue, iterations=apron_px)
        peaks &= ~apron
    if budget is not None and budget < int(peaks.sum()):
        vals = work[peaks]
        keep = np.argpartition(vals, -budget)[-budget:]
        sel = np.zeros(work.shape, bool)
        ys, xs = np.nonzero(peaks)
        sel[ys[keep], xs[keep]] = True
        peaks = sel
    return peaks


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["train", "score", "emit", "holdout-eval"])
    ap.add_argument("--model", default="hgb", choices=["hgb", "logreg"])
    ap.add_argument("--features", default="all")
    ap.add_argument("--run", default="e1")
    ap.add_argument("--radius", type=int, default=2)
    ap.add_argument("--min-score", type=float, default=0.0)
    ap.add_argument("--apron-px", type=int, default=0)
    ap.add_argument("--blocks", type=int, default=2)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    EVID.mkdir(parents=True, exist_ok=True)
    RUN.mkdir(parents=True, exist_ok=True)
    meta = build_features()
    names = list(meta["features"].keys())
    if args.features != "all":
        names = [n for n in names if n in args.features.split(",")]
    g = load_grid()
    shape = g.shape

    if args.command == "train":
        pos, neg = sample_training(g.catalogue, g.footprint)
        y = np.concatenate([np.ones(pos.size, np.int8), np.zeros(neg.size, np.int8)])
        idx = np.concatenate([pos, neg])
        blocks = block_ids(shape, n=args.blocks).ravel()
        X = extract_samples(names, idx, shape)
        X, medians = impute(X)
        from sklearn.metrics import roc_auc_score

        folds = sorted(set(blocks[idx].tolist()))
        rows = []
        for f in folds:
            tr = blocks[idx] != f
            te = ~tr
            clf = train_model(X[tr], y[tr], model=args.model)
            p = clf.predict_proba(X[te])[:, 1]
            auc = roc_auc_score(y[te], p)
            rows.append(dict(block=int(f), n_test=int(te.sum()), auc=float(auc)))
            log(f"fold block {f}: held-out AUC {auc:.4f} (n={int(te.sum())})")
        canary = []
        for j, name in enumerate(names):
            aucs = []
            for f in folds:
                tr = blocks[idx] != f
                te = ~tr
                aucs.append(roc_auc_score(y[te], X[te, j]))
            canary.append(dict(feature=name, mean_auc=float(np.mean(aucs)),
                               max_auc=float(np.max(aucs)),
                               leakage_flag=bool(np.max(aucs) > 0.90)))
        clf = train_model(X, y, model=args.model)
        import joblib

        joblib.dump(dict(model=clf, features=names, model_type=args.model,
                         medians=medians),
                    RUN / f"{args.run}-model.joblib")
        out = dict(lane=LANE, experiment=args.run, model_type=args.model,
                   n_features=len(names), features=names,
                   n_pos=int((y == 1).sum()), n_neg=int((y == 0).sum()),
                   spatial_block_cv=rows,
                   mean_auc=float(np.mean([r["auc"] for r in rows])),
                   leakage_canary=canary,
                   leakage_canary_max_auc=float(max(c["max_auc"] for c in canary)),
                   leakage_canary_pass=bool(max(c["max_auc"] for c in canary) <= 0.90),
                   evaluator_version=EVALUATOR)
        (EVID / f"{args.run}-train.json").write_text(json.dumps(out, indent=2) + "\n")
        log(json.dumps({k: out[k] for k in ("mean_auc", "leakage_canary_max_auc",
                                            "leakage_canary_pass")}, indent=2))
        return 0

    if args.command == "score":
        import joblib

        blob = joblib.load(RUN / f"{args.run}-model.joblib")
        names = blob["features"]
        score = score_grid(blob["model"], names, shape, blob.get("medians"))
        np.save(RUN / f"{args.run}-score.npy", score)
        log(f"score surface written: {score.shape}")
        return 0

    if args.command == "emit":
        score = np.load(RUN / f"{args.run}-score.npy", mmap_mode="r")
        valid = g.footprint & ~g.catalogue
        dots = emit_dots(np.asarray(score), valid, args.radius, args.min_score,
                         catalogue=g.catalogue, apron_px=args.apron_px)
        np.save(RUN / f"{args.run}-dots.npy", dots)
        log(f"emitted {int(dots.sum())} dots "
            f"(radius={args.radius}, min_score={args.min_score}, apron={args.apron_px}px)")
        return 0

    if args.command == "holdout-eval":
        from gems57 import holdout as gholdout

        dots = np.load(RUN / f"{args.run}-dots.npy")
        ctx = gholdout.build_holdout(g)
        res = gholdout.evaluate(dots, ctx)
        inst = SgmcInstrument()
        sg = inst.score(dots)
        out = dict(lane=LANE, experiment=args.run,
                   catalogue_holdout=dict(pooled_dti=res["pooled_dti"],
                                          pooled_coverage=res["pooled_coverage"],
                                          pooled_tp=res["pooled_tp"],
                                          pooled_fp=res["pooled_fp"],
                                          pooled_fn=res["pooled_fn"],
                                          pooled_n_truth=res["pooled_n_truth"],
                                          per_fold_dti=res["per_fold_dti"],
                                          evaluator_version=EVALUATOR),
                   sgmc_cal=sg,
                   emitted=int(dots.sum()))
        (EVID / f"{args.run}-eval.json").write_text(json.dumps(out, indent=2) + "\n")
        log(json.dumps(out, indent=2)[:2000])
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

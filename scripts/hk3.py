#!/usr/bin/env python3
"""HK3 (session 2026-10-28, karage2): catalogue-free edge-centrality surface with
calibrated off-catalogue dotted emission.

LANE (single method paragraph): a supervised multi-physics fault-likelihood
surface whose *new* inputs are catalogue-free edge-geometry transforms of the
public 19-band stack (gradient-ridge centrality of detrended elevation at two
scales, gravity tilt angle and distance to its zero crossing, distance to the
magnetic tilt-angle zero crossing (tilt formed from TMI vertical/horizontal gradients), structure-tensor coherence/anisotropy of detrended
elevation and 500 m roughness).  Emission is a binary dot field placed greedily
by descending surface value with a minimum separation, restricted to cells more
than 3 px from the mapped catalogue (the apron radius derived in E1 from the
nested D2.8->B1->B2 leaderboard steps), with the dot budget chosen by the
calibrated marginal-dot rule rather than tuned on the holdout.

Shared tools reused unchanged: vendor/gems57 evaluator (gems57-pooled-hide-v2;
alpha 0.2, beta 0.8, 300 m triangular kernel), K2 feature stack/folds/emission
(scripts/k2.py functions), gems57 submission_writer / validate / uniqueness.

Subcommands
  features   extend the K2 26-band memmap with the 8 HK3 bands (34 total)
  e2         canaries for the 8 new bands + paired incumbent(26f) vs candidate(34f)
             HistGradientBoosting on the identical label-blind quadrant folds
  bridge     score the pinned D2.8 (GEMSDOE25) dot file on the same folds (transfer anchor)
  e3         full-catalogue fit, apron+budget emission, estimator, validation,
             registry audit, shared-writer output
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))
import k2  # noqa: E402  (K2 main() is disabled; its functions are reused unchanged)
from gems57 import evaluate_holdout as shared  # noqa: E402
from gems57 import spatial  # noqa: E402
from gems57 import uniqueness as uniq  # noqa: E402
from gems57 import validate as gvalidate  # noqa: E402
from gems57.grid import load_grid  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402

DATA = ROOT / ".cache/gems_data"
WORK = ROOT / ".cache/hk3"; WORK.mkdir(parents=True, exist_ok=True)
EV = ROOT / "evidence/hk3"; EV.mkdir(parents=True, exist_ok=True)
SEED = 20261028
NEW_NAMES = ["ec15_det_elev", "ec30_det_elev", "grav_tilt", "grav_tilt_zero_dist",
             "mag_tilt_zero_dist", "st_coh_det_elev", "st_aniso_det_elev", "rough5_det_elev"]
ALL_NAMES = k2.FEATURE_NAMES + NEW_NAMES
NF_ALL = len(ALL_NAMES)  # 34
APRON_PX = 3.0           # from evidence/calibration/leaderboard_calibration.json (E1)
SEP_PX = 3.0             # minimum dot separation (metric-motivated; not the family's 2.8)
_DISC3 = [(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if (dy * dy + dx * dx) < SEP_PX * SEP_PX]


# ----------------------------------------------------------------------------- features
def feat_path():
    return WORK / "features34.f32"


def open_features(shape, mode="r"):
    return np.memmap(feat_path(), dtype=np.float32, mode=mode, shape=(NF_ALL, shape[0], shape[1]))


def _zero_cross_distance(a, valid, sigma):
    """Distance (px) to the nearest sign change of a smoothed field; large where undefined."""
    sm = k2.smooth_norm(a, valid, sigma)
    s = np.sign(sm)
    zc = np.zeros(a.shape, bool)
    zc[:, 1:] |= (s[:, 1:] * s[:, :-1] < 0)
    zc[1:, :] |= (s[1:, :] * s[:-1, :] < 0)
    zc &= valid
    d = ndi.distance_transform_edt(~zc)
    return np.minimum(d, 50.0).astype(np.float32)


def cmd_features():
    grid, valid, eligible = k2.grid_and_masks()
    if not k2.feat_path().exists():
        k2.cmd_features()
    F26 = k2.open_features(grid.shape)
    F = open_features(grid.shape, mode="w+")
    for i in range(k2.NF):
        F[i] = F26[i]
    print("copied 26 K2 bands", flush=True)
    with rasterio.open(DATA / "training_features.tif") as ds:
        det = ds.read(12).astype(np.float32)
        gvg = ds.read(11).astype(np.float32)
        ghg = ds.read(18).astype(np.float32)
        mvg = ds.read(9).astype(np.float32)   # TMI vertical gradient
        mhg = ds.read(3).astype(np.float32)   # TMI horizontal gradient
    good = lambda a: np.isfinite(a) & (np.abs(a) < 1e30)
    vdet = good(det)
    idx = k2.NF
    # 1-2: gradient-ridge centrality of detrended elevation (scarp crest = linear slope maximum)
    for sigma in (1.5, 3.0):
        sm = k2.smooth_norm(det, vdet, sigma)
        gy, gx = np.gradient(sm)
        g = np.hypot(gy, gx)
        mx = ndi.maximum_filter(g, size=5)
        F[idx] = np.where(valid, g / (mx + 1e-6), 0).astype(np.float32); idx += 1
        print(f"ec{sigma}", flush=True)
    # 3-4: gravity tilt angle and distance to its zero crossing (buried basin-bounding edges)
    vg = good(gvg) & good(ghg)
    tilt = np.arctan2(np.where(vg, gvg, 0), np.abs(np.where(vg, ghg, 0)) + 1e-9)
    F[idx] = np.where(valid & vg, tilt, 0).astype(np.float32); idx += 1
    F[idx] = np.where(valid, _zero_cross_distance(tilt, vg, 1.0), 50).astype(np.float32); idx += 1
    print("grav tilt", flush=True)
    # 5: distance to the magnetic tilt-angle zero crossing (Miller & Singh 1994 source edges).
    #    Band 6 "tc" is strictly positive (2.9-88.6) so it has no zero crossing; the tilt
    #    angle is therefore formed from the TMI vertical/horizontal gradient bands 9 and 3.
    vm = good(mvg) & good(mhg)
    mtilt = np.arctan2(np.where(vm, mvg, 0), np.abs(np.where(vm, mhg, 0)) + 1e-9)
    F[idx] = np.where(valid, _zero_cross_distance(mtilt, vm, 1.0), 50).astype(np.float32); idx += 1
    print("mag tilt zero", flush=True)
    # 6-7: structure tensor of detrended elevation (linear texture / across-strike energy)
    sm = k2.smooth_norm(det, vdet, 1.5)
    gy, gx = np.gradient(sm)
    jxx = ndi.gaussian_filter(gx * gx, 5.0); jyy = ndi.gaussian_filter(gy * gy, 5.0)
    jxy = ndi.gaussian_filter(gx * gy, 5.0)
    tr = jxx + jyy
    disc = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2)
    coh = disc / (tr + 1e-12)
    F[idx] = np.where(valid, coh, 0).astype(np.float32); idx += 1
    F[idx] = np.where(valid, 0.5 * (tr + disc), 0).astype(np.float32); idx += 1   # dominant eigenvalue
    print("structure tensor", flush=True)
    # 8: 500 m roughness of detrended elevation (bedrock vs alluvium texture)
    m1 = k2.smooth_norm(det, vdet, 5.0)
    m2 = k2.smooth_norm(det * det, vdet, 5.0)
    F[idx] = np.where(valid, np.sqrt(np.maximum(m2 - m1 * m1, 0)), 0).astype(np.float32); idx += 1
    assert idx == NF_ALL
    F.flush()
    (WORK / "feature_meta.json").write_text(json.dumps({"feature_names": ALL_NAMES, "shape": list(grid.shape)}, indent=2) + "\n")
    print("features done", flush=True)


# ----------------------------------------------------------------------------- shared helpers
def gather(F, flat_idx, nf):
    return np.stack([np.asarray(F[i]).ravel()[flat_idx] for i in range(nf)], axis=1)


def emit(surface, allowed, budget, sep_disc):
    """Greedy descending-surface binary emission with a minimum separation (K2 logic, parametrised)."""
    H, W = surface.shape
    ys, xs = np.nonzero(allowed)
    vals = surface[ys, xs].astype(np.float64)
    order = np.argsort(-vals, kind="mergesort")
    keep = min(len(order), max(budget * 12, budget + 20_000))
    order = order[:keep]
    ys, xs = ys[order], xs[order]
    blocked = np.zeros((H, W), bool)
    dots = np.zeros((H, W), bool)
    n = 0
    for y, x in zip(ys.tolist(), xs.tolist()):
        if blocked[y, x]:
            continue
        dots[y, x] = True
        n += 1
        if n >= budget:
            break
        for dy, dx in sep_disc:
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < W:
                blocked[yy, xx] = True
    return dots


def fold_train_predict(F, fold, catalogue, seed, nf):
    visible, train = fold["visible"], fold["train"]
    pos = np.flatnonzero(catalogue & train)
    dvis = ndi.distance_transform_edt(~visible)
    neg_pool = np.flatnonzero(train & ~catalogue & (dvis > 3))
    rng = np.random.default_rng(seed)
    neg = rng.choice(neg_pool, min(180_000, len(neg_pool)), replace=False)
    ids = np.r_[pos, neg]
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    model = k2.train_hgb(gather(F, ids, nf), y, seed)
    region_idx = np.flatnonzero(fold["region"] & ~visible)
    surf = np.zeros(catalogue.shape, np.float32)
    for s in range(0, len(region_idx), 400_000):
        chunk = region_idx[s:s + 400_000]
        surf.ravel()[chunk] = model.predict_proba(gather(F, chunk, nf))[:, 1]
    return surf, {"pos": int(len(pos)), "neg": int(len(neg))}


def load_ctx():
    grid, valid, _ = k2.grid_and_masks()
    eligible = np.load(k2.K2 / "eligible.npy")
    folds = list(spatial.folds(grid.catalogue, eligible, buffer_px=80))
    F = open_features(grid.shape)
    return grid, valid, eligible, folds, F


def hit_stats(dots, fold, valid):
    """Coverage and dot hit-mass on one fold (for the transfer estimator)."""
    from gems57 import metric
    active = valid & fold["region"] & ~fold["visible"]
    truth = active & fold["truth"]
    p = (dots & active).astype(np.float64)
    credit, q, _ = metric.max_cover(p, truth)
    return dict(T=float(credit.sum()), M=float((p * q).sum()), n=int(p.sum()), G=int(truth.sum()))


# ----------------------------------------------------------------------------- E2
def cmd_e2():
    from sklearn.metrics import roc_auc_score
    grid, valid, eligible, folds, F = load_ctx()
    canaries, terms, receipts, hits = [], {}, [], {}
    for fold in folds:
        f = fold["fold"]
        t0 = time.time()
        active = fold["region"] & ~fold["visible"]
        pos = np.flatnonzero(fold["truth"])
        neg_pool = np.flatnonzero(active & ~fold["truth"])
        rng = np.random.default_rng(SEED + f)
        neg = rng.choice(neg_pool, min(60_000, len(neg_pool)), replace=False)
        ids = np.r_[pos, neg]
        y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
        Xn = np.stack([np.asarray(F[k2.NF + j]).ravel()[ids] for j in range(len(NEW_NAMES))], axis=1)
        row = {"fold": f, "positives": int(len(pos)), "unlabeled_sample": int(len(neg)), "features": {}}
        for j, name in enumerate(NEW_NAMES):
            auc = float(roc_auc_score(y, Xn[:, j]))
            row["features"][name] = {"auc": auc, "canary_max_auc_1m": max(auc, 1 - auc),
                                     "pass": bool(max(auc, 1 - auc) <= 0.90)}
        canaries.append(row)
        base = int(active.sum())
        surf_inc, ntr = fold_train_predict(F, fold, grid.catalogue, SEED + f, k2.NF)
        surf_cand, _ = fold_train_predict(F, fold, grid.catalogue, SEED + f, NF_ALL)
        np.save(WORK / f"surf_cand_fold{f}.npy", surf_cand)
        for rate, tag in ((0.0073, "b073"), (0.0110, "b110"), (0.0150, "b150")):
            budget = int(round(rate * base))
            for arm, surf in (("inc26", surf_inc), ("cand34", surf_cand)):
                dots = emit(surf, active, budget, k2._DISC)
                k2.score_arm(terms, f"{arm}_{tag}", dots, fold, valid)
                hits.setdefault(f"{arm}_{tag}", []).append(hit_stats(dots, fold, valid))
        receipts.append({"fold": f, "train": ntr, "active_px": base, "seconds": round(time.time() - t0, 1)})
        print(f"fold {f} done {receipts[-1]}", flush=True)
    worst = {}
    for row in canaries:
        for n, d in row["features"].items():
            worst[n] = max(worst.get(n, 0), d["canary_max_auc_1m"])
    np.savez_compressed(WORK / "terms_e2.npz", **terms)
    summary = shared.pooled_summary(terms, draws=2000, seed=SEED, candidate="cand34_b110")
    out = {"experiment": "HK3-E2 canaries + paired incumbent(26f) vs candidate(34f) HGB",
           "evidence_class": "HOLDOUT-DTI", "evaluator_version": shared.VERSION,
           "folds": receipts, "canaries": canaries, "worst_canary_by_feature": worst,
           "canary_all_pass": bool(max(worst.values()) <= 0.90),
           "emission": "K2 emit: greedy descending surface, min separation 2.8 px, budgets 0.73/1.10/1.50% of active px",
           "model": "HistGradientBoosting 350it lr.06 leaves63 minleaf40 L2=1 (K2 hyperparameters, unchanged)",
           "pooled_summary": summary,
           "hit_stats_by_arm": {k: {"T": sum(h["T"] for h in v), "M": sum(h["M"] for h in v),
                                   "n": sum(h["n"] for h in v), "G": sum(h["G"] for h in v)} for k, v in hits.items()}}
    (EV / "e2.json").write_text(json.dumps(out, indent=2) + "\n")
    for name, s in sorted(summary["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        print(f"{name:14s} HOLDOUT-DTI {s['dti']:.5f} CI [{s['ci95'][0]:.5f},{s['ci95'][1]:.5f}] n={s['withheld_positive_pixels']}")
    for name, d in summary["paired_differences"].items():
        print(f"  d(cand34_b110-{name}) {d['delta']:+.5f} CI [{d['ci95'][0]:+.5f},{d['ci95'][1]:+.5f}]")
    print("canaries:", worst)


# ----------------------------------------------------------------------------- bridge
def cmd_bridge():
    """Transfer anchors on the identical folds + the candidate's marginal-hit curve.

    (a) pinned public dot files scored on the K2 folds (caveats recorded: built with the
        full catalogue visible -> possible leakage in their favour; no dots on catalogue
        pixels -> credit on catalogue-pixel truth capped below 1);
    (b) the candidate emitted at exactly the D2.8 per-fold dot count (equal-n ratios);
    (c) the candidate's cumulative T/M by rank band (5k-dot bands up to 2% of active px)
        for the calibrated budget rule in E3."""
    from gems57 import metric
    grid, valid, eligible, folds, _ = load_ctx()
    rows, d28_per_fold = {}, {}
    for site, name in (("GEMSDOE25", "dotted-h19-5-d2-8 (D2.8, reported 0.2600)"),
                       ("GEMSDOE32", "h33-h33-2-b2 (B2, reported 0.2778)"),
                       ("GEMSDOE24", "h25-1-dotted-h19-5-d1-5 (reported 0.2477)"),
                       ("GEMSDOE33", "h33d-analog-tip-stepover-r30 (reported 0.2632)"),
                       ("r13_lattice_nan", "r13 lattice s5 (reported 0.0904)")):
        with rasterio.open(ROOT / ".cache/registry_focus" / f"{site}.tif") as ds:
            a = ds.read(1)
        dots = np.isfinite(a) & (a > 0) & grid.footprint
        terms, hs = {}, []
        for fold in folds:
            k2.score_arm(terms, site, dots, fold, valid)
            h = hit_stats(dots, fold, valid); hs.append(h)
            if site == "GEMSDOE25":
                d28_per_fold[fold["fold"]] = h["n"]
        t = terms[site].sum(axis=0)
        rows[site] = {"label": name, "dots_total": int(dots.sum()),
                      "holdout_dti": float(shared.from_terms(t)),
                      "T": float(t[0]), "F": float(t[1]), "G": float(t[3]),
                      "hit": {"T": sum(h["T"] for h in hs), "M": sum(h["M"] for h in hs),
                              "n": sum(h["n"] for h in hs), "G": sum(h["G"] for h in hs)},
                      "evidence_class": "HOLDOUT-DTI (external file; see caveats)"}
        print(site, round(rows[site]["holdout_dti"], 5), rows[site]["hit"], flush=True)
    # (b) candidate at the D2.8 per-fold dot count, same K2 emission (sep 2.8) and with the
    #     HK3 emission (sep 3.0, apron 3 px from *visible* faults) for the final-geometry ratio
    match = {"k2emit": [], "hk3emit": []}
    curve = {}
    for fold in folds:
        f = fold["fold"]
        surf = np.load(WORK / f"surf_cand_fold{f}.npy")
        active = fold["region"] & ~fold["visible"]
        n_match = d28_per_fold[f]
        dots = emit(surf, active, n_match, k2._DISC)
        match["k2emit"].append(hit_stats(dots, fold, valid))
        dvis = ndi.distance_transform_edt(~fold["visible"])
        allowed = active & (dvis > APRON_PX)
        dots = emit(surf, allowed, n_match, _DISC3)
        match["hk3emit"].append(hit_stats(dots, fold, valid))
        # (c) marginal curve: the HK3 emission ordering up to 2% of active px, cut at the
        #     same *rate* in every fold (as a global greedy emission would), so that the
        #     pooled curve is a consistent function of total budget.
        n_act = int(active.sum())
        big = emit(surf, allowed, int(round(0.02 * n_act)), _DISC3)
        ys, xs = np.nonzero(big)
        order = np.argsort(-surf[ys, xs], kind="mergesort")
        ys, xs = ys[order], xs[order]
        truth = valid & fold["region"] & ~fold["visible"] & fold["truth"]
        for rate_i in range(2, 21):           # 0.2% ... 2.0% of active px
            rate = rate_i / 1000.0
            k = min(len(ys), int(round(rate * n_act)))
            sel = np.zeros(grid.shape, bool); sel[ys[:k], xs[:k]] = True
            p = sel.astype(np.float64)
            credit, q, _ = metric.max_cover(p, truth)
            c = curve.setdefault(rate, {"T": 0.0, "M": 0.0, "n": 0})
            c["T"] += float(credit.sum()); c["M"] += float((p * q).sum()); c["n"] += int(p.sum())
        print(f"fold {f} matched n={n_match} k2emit={match['k2emit'][-1]} hk3emit={match['hk3emit'][-1]}", flush=True)
    agg = lambda hs: {"T": sum(h["T"] for h in hs), "M": sum(h["M"] for h in hs),
                      "n": sum(h["n"] for h in hs), "G": sum(h["G"] for h in hs)}
    out = {"evaluator_version": shared.VERSION,
           "caveats": ["external files were produced with the full catalogue visible: catalogue-continuation leakage can inflate their holdout numbers",
                       "external files place no dots on catalogue pixels: their holdout credit on catalogue-pixel truth is capped below 1",
                       "numbers are HOLDOUT-DTI on label-blind quadrant folds, not leaderboard scores"],
           "rows": rows,
           "candidate_matched_to_D28_count": {k: agg(v) for k, v in match.items()},
           "candidate_marginal_curve_hk3emit": {f"{k:.3f}": v for k, v in sorted(curve.items())},
           "curve_key": "rate of active px (same rate in every fold); values pooled over the four folds",
           "holdout_truth_px_total": int(sum(int((valid & fd["region"] & ~fd["visible"] & fd["truth"]).sum()) for fd in folds)),
           "holdout_active_px_total": int(sum(int((fd["region"] & ~fd["visible"]).sum()) for fd in folds))}
    (EV / "bridge.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["candidate_matched_to_D28_count"], indent=1))


# ----------------------------------------------------------------------------- estimator
def estimate_leaderboard(n_dots, cov_ratio, hit_ratio, calib):
    """LEADERBOARD-CALIBRATED ESTIMATE by ratio transfer from the D2.8 family anchor.

    T_est = T_anchor * cov_ratio ; M_est = M_anchor * hit_ratio ; F = n - M.
    cov_ratio/hit_ratio are candidate/anchor ratios measured on identical holdout folds
    with the anchor's dot count matched (bridge.json).  Never a score.
    """
    G = calib["hidden_truth_estimate"]["G_point_px"]
    T_a = calib["b2_operating_point"]["T_truth_credit"]
    M_a = calib["b2_operating_point"]["M_dot_hit_mass"]
    n_a = calib["b2_operating_point"]["dots"]
    T = T_a * cov_ratio
    M = min(n_dots * (M_a / n_a) * hit_ratio, n_dots)   # per-dot hit rate transfers, scaled to n
    F = n_dots - M
    return T / (0.2 * T + 0.2 * F + 0.8 * G), dict(G=G, T=T, M=M, F=F)


THETA_GRID = (1.0, 0.75, 0.5)   # transfer fraction of the measured surface advantage (pre-registered)


def family_baseline(bridge, n_holdout):
    """Holdout (cov, hit) ratio of the D2.8 family itself at a given active-region dot count,
    linear between the two unpruned family anchors D2.8 (GEMSDOE25) and h25-1 (GEMSDOE24)."""
    d = bridge["rows"]["GEMSDOE25"]["hit"]; g = bridge["rows"]["GEMSDOE24"]["hit"]
    c2 = g["T"] / d["T"]; h2 = (g["M"] / g["n"]) / (d["M"] / d["n"])
    t = (n_holdout - d["n"]) / (g["n"] - d["n"])
    return 1.0 + t * (c2 - 1.0), 1.0 + t * (h2 - 1.0)


def budget_table(bridge, calib):
    """Calibrated estimate as a function of the emission rate (from bridge.json's
    per-fold-rate marginal curve, pooled over the four holdout folds).

    estimate            : measured candidate/anchor ratios transfer fully (theta = 1)
    estimate_theta[t]   : only a fraction t of the candidate's advantage over the family
                          baseline at the same count transfers (t in THETA_GRID)
    estimate_pessimistic: ratios capped at 1 (no better than D2.8 at its own count) - floor
    """
    anchor_h = bridge["rows"]["GEMSDOE25"]["hit"]          # D2.8 on the catalogue holdout
    curve = {float(k): v for k, v in bridge["candidate_marginal_curve_hk3emit"].items()}
    rows = []
    for rate in sorted(curve):
        c = curve[rate]
        cov = c["T"] / anchor_h["T"]
        hit = (c["M"] / c["n"]) / (anchor_h["M"] / anchor_h["n"]) if c["n"] else 0.0
        n_full = rate * FULL_ACTIVE_PX   # same rate basis as the holdout curve (active/eligible px)
        est, comp = estimate_leaderboard(n_full, cov, hit, calib)
        pess, _ = estimate_leaderboard(n_full, min(cov, 1.0), min(hit, 1.0), calib)
        cf, hf = family_baseline(bridge, c["n"])
        theta = {}
        for t in THETA_GRID + (0.0,):           # 0.0 = family baseline at the same count (reported, not in the rule)
            e, _ = estimate_leaderboard(n_full, cf + t * (cov - cf), hf + t * (hit - hf), calib)
            theta[f"{t:.2f}"] = e
        prev = rows[-1] if rows else None
        dT = c["T"] - (prev["holdout_T"] if prev else 0.0); dn = c["n"] - (prev["holdout_n"] if prev else 0)
        dM = c["M"] - (prev["holdout_M"] if prev else 0.0)
        rows.append(dict(rate=rate, holdout_n=c["n"], holdout_T=c["T"], holdout_M=c["M"],
                         holdout_dti=c["T"] / (0.2 * c["T"] + 0.2 * (c["n"] - c["M"]) + 0.8 * anchor_h["G"]),
                         holdout_band_truth_share=(dT / (dT + dn - dM)) if dn > 0 else None,
                         cov_ratio=cov, hit_ratio=hit, family_cov_ratio=cf, family_hit_ratio=hf,
                         n_full_map=int(round(n_full)), estimate=est, estimate_theta=theta,
                         estimate_min_over_theta=min(theta[f"{t:.2f}"] for t in THETA_GRID),
                         estimate_pessimistic=pess, components=comp))
    return rows


def choose_rate(table):
    """Pre-registered budget rule (research/hypotheses-2026-10-28-hk3.md, section 3b):
    maximise the minimum calibrated estimate over THETA_GRID; ties within 0.001 go to the
    smaller budget."""
    best_min = max(r["estimate_min_over_theta"] for r in table)
    return next(r for r in table if r["estimate_min_over_theta"] >= best_min - 0.001)


FULL_ACTIVE_PX = 5_011_946  # eligible px on the full map; equals the pooled holdout active total (bridge.json) - set at runtime


# ----------------------------------------------------------------------------- E3
def cmd_e3(name, note, rate, write=True, reuse_surface=False):
    global FULL_ACTIVE_PX
    grid, valid, eligible = k2.grid_and_masks()
    F = open_features(grid.shape)
    cat = grid.catalogue
    dcat = ndi.distance_transform_edt(~cat)
    calib = json.loads((ROOT / "evidence/calibration/leaderboard_calibration.json").read_text())
    bridge = json.loads((EV / "bridge.json").read_text())
    FULL_ACTIVE_PX = int(eligible.sum())
    assert FULL_ACTIVE_PX == bridge["holdout_active_px_total"], (FULL_ACTIVE_PX, bridge["holdout_active_px_total"])
    table = budget_table(bridge, calib)
    best = max(table, key=lambda r: r["estimate"])
    best_pess = max(table, key=lambda r: r["estimate_pessimistic"])
    knee = choose_rate(table)
    if rate is None:
        rate = knee["rate"]
    print(f"budget table (rate -> estimate / pessimistic):", flush=True)
    for r in table:
        print(f"  {r['rate']:.3f} n={r['n_full_map']:6d} holdoutDTI={r['holdout_dti']:.4f} "
              f"cov={r['cov_ratio']:.3f} hit={r['hit_ratio']:.3f} est={r['estimate']:.4f} "
              f"theta={ {k: round(v, 4) for k, v in r['estimate_theta'].items()} } pess={r['estimate_pessimistic']:.4f}")
    print(f"chosen rate {rate} (maximin rule {knee['rate']}, argmax estimate {best['rate']}, argmax pessimistic {best_pess['rate']})", flush=True)
    train = eligible
    pos = np.flatnonzero(cat & train)
    neg_pool = np.flatnonzero(train & ~cat & (dcat > 3))
    rng = np.random.default_rng(SEED)
    neg = rng.choice(neg_pool, min(360_000, len(neg_pool)), replace=False)
    allowed = valid & (dcat > APRON_PX)
    surf_path = WORK / "surface_full.npy"
    if reuse_surface and surf_path.exists():
        surf = np.load(surf_path)
        print("reusing cached full-map surface", surf_path, flush=True)
    else:
        ids = np.r_[pos, neg]
        y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
        t0 = time.time()
        model = k2.train_hgb(gather(F, ids, NF_ALL), y, SEED)
        print(f"full fit {len(pos)} pos / {len(neg)} neg in {time.time()-t0:.0f}s", flush=True)
        idx = np.flatnonzero(allowed)
        surf = np.zeros(grid.shape, np.float32)
        for s in range(0, len(idx), 400_000):
            chunk = idx[s:s + 400_000]
            surf.ravel()[chunk] = model.predict_proba(gather(F, chunk, NF_ALL))[:, 1]
        np.save(surf_path, surf)
    budget = int(round(rate * FULL_ACTIVE_PX))   # rate over active px, placed inside the apron-free allowed set
    dots = emit(surf, allowed, budget, _DISC3)
    n = int(dots.sum())
    print(f"emitted {n} dots (budget {budget}, rate {rate}, apron>{APRON_PX}px, sep {SEP_PX}px)", flush=True)
    pred = np.where(dots, 1.0, 0.0).astype(np.float32)
    pred[~grid.footprint] = 0.0
    # ---- estimator (ratio transfer at the chosen rate; see bridge.json) --------
    row = min(table, key=lambda r: abs(r["rate"] - rate))
    cov_ratio, hit_ratio = row["cov_ratio"], row["hit_ratio"]
    est, comp = estimate_leaderboard(n, cov_ratio, hit_ratio, calib)
    est_pess, _ = estimate_leaderboard(n, min(cov_ratio, 1.0), min(hit_ratio, 1.0), calib)
    # out-of-sample check of the transfer rule on the one unpruned independent anchor (GEMSDOE24)
    g24 = bridge["rows"].get("GEMSDOE24", {}).get("hit"); d28 = bridge["rows"]["GEMSDOE25"]["hit"]
    check24 = None
    if g24:
        e24, _ = estimate_leaderboard(calib["focus_dot_counts"]["GEMSDOE24"], g24["T"] / d28["T"],
                                      (g24["M"] / g24["n"]) / (d28["M"] / d28["n"]), calib)
        rep24 = calib["inputs"]["reported_scores"]["GEMSDOE24"]
        rep24 = rep24["score"] if isinstance(rep24, dict) else rep24
        check24 = {"predicted": e24, "user_reported": rep24, "ratio_reported_over_predicted": rep24 / e24}
    est_adj = est * check24["ratio_reported_over_predicted"] if check24 else None
    estimator = {"evidence_class": "LEADERBOARD-CALIBRATED ESTIMATE (ratio transfer from USER-REPORTED anchors; NOT a score; NOT ORGANIZER-CONFIRMED)",
                 "anchor": "D2.8/B2 family operating point from evidence/calibration/leaderboard_calibration.json",
                 "curve_row_used": row, "holdout_cov_ratio_cand_over_D28": cov_ratio, "holdout_hit_ratio_cand_over_D28": hit_ratio,
                 "n_dots": n, "estimate": est, "estimate_if_no_better_than_anchor": est_pess,
                 "estimate_scaled_by_GEMSDOE24_check": est_adj, "GEMSDOE24_out_of_sample_check": check24, "components": comp,
                 "budget_table": table, "rule_rate": knee["rate"], "argmax_rate": best["rate"], "argmax_rate_pessimistic": best_pess["rate"],
                 "budget_rule": "maximin of the calibrated estimate over theta in (1, 0.75, 0.5); ties within 0.001 to the smaller budget (pre-registered, section 3b)",
                 "estimate_theta": row["estimate_theta"],
                 "assumptions": ["candidate/anchor coverage and hit-mass ratios measured on catalogue holdout transfer to the expert hidden truth",
                                 "G and the anchor (T, M) come from the lattice-pinned calibration of USER-REPORTED scores",
                                 "the anchor's holdout number may be inflated by catalogue leakage, which makes this estimate conservative if so"]}
    print("estimator:", json.dumps({k: v for k, v in estimator.items() if k != "budget_table"}, indent=1, default=str), flush=True)
    result = {"name": name, "note": note, "dots": n, "budget": budget, "rate": rate, "apron_px": APRON_PX,
              "sep_px": SEP_PX, "surface_sha256": hashlib.sha256(surf.tobytes()).hexdigest(),
              "train": {"pos": int(len(pos)), "neg": int(len(neg))}, "estimator": estimator,
              "dots_within_3px_of_catalogue": int((dots & (dcat <= 3)).sum()),
              "dots_on_catalogue": int((dots & cat).sum())}
    if not write:
        (EV / "e3_dry.json").write_text(json.dumps(result, indent=2) + "\n")
        return
    out_dir = ROOT / "docs/downloads"
    tif = out_dir / f"{name}.tif"
    receipt = write_submission(tif, pred, DATA / "sample_submission.tif", grid.footprint,
                               note=note, name=name, catalogue=cat,
                               metadata=json.loads(json.dumps(result, default=str)))
    result["writer_receipt"] = receipt
    (EV / "e3_generation.json").write_text(json.dumps(result, indent=2, default=str) + "\n")
    print("written", tif, receipt["sha256"], flush=True)


def cmd_audit(name):
    grid = load_grid(DATA)
    tif = ROOT / "docs/downloads" / f"{name}.tif"
    with rasterio.open(tif) as ds:
        mine = ds.read(1)
    file_sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    man = json.loads((ROOT / "registry/focus_registry_manifest.json").read_text())
    records = [{"repo": r["repo"], "submission": r["path"], "file": r["local"], "sha256": r["sha256"]}
               for r in man["rasters"] if r["status"] == "ok"]
    pinned = json.loads((ROOT / "registry/pinned_assets.json").read_text())
    for x in pinned["assets"]:
        if x["role"] in ("focus", "lattice"):
            records.append({"repo": x["repo"].split("/")[-1], "submission": x["path"],
                            "file": f".cache/registry_focus/{x['cache_name']}", "sha256": x["sha256"]})
    for local in sorted((ROOT / "docs/downloads").glob("*.tif")):
        if local.name != tif.name:
            records.append({"repo": "karage2-local", "submission": local.name, "file": str(local), "sha256": None})
    audit = uniq.compare_array_to_registry(mine, records, grid.footprint, file_sha256=file_sha,
                                           include_reverse=False,
                                           expected_grid=(grid.shape, grid.crs, grid.transform))
    rows = [r for r in audit["rows"] if "error" not in r]
    fp_cells = int(grid.footprint.sum())
    # Degenerate-witness classification: a registry raster whose 3 px halo covers
    # (almost) the whole footprint flags every possible candidate and cannot
    # discriminate methods.  Reported, never silently dropped.
    for r in rows:
        r["their_halo_fraction_of_footprint"] = None
    degenerate = []
    for r in rows:
        if r["their_dots"] * 29 >= 0.9 * fp_cells:   # cheap upper bound screen first
            p = Path(r["file"]);  p = p if p.is_absolute() else ROOT / p
            with rasterio.open(p) as ds:
                t = ds.read(1)
            sup = np.isfinite(t) & (t > 0) & grid.footprint
            frac = float(uniq._near(sup)[grid.footprint].mean())
            r["their_halo_fraction_of_footprint"] = frac
            if frac >= 0.95:
                degenerate.append(r["submission"])
    nondeg = [r for r in rows if r["submission"] not in degenerate]
    # Dense-witness detail (pre-registered, hypotheses note section 3c): for every raster whose
    # 3 px halo covers >= 50 % of the footprint, or whose literal overlap exceeds 60 %, report the
    # halo fraction (= chance overlap of a random dot set), the chance-corrected excess
    # (overlap - halo) / (1 - halo), and the same literal overlap for the organizer-scored
    # GEMSDOE32 champion dots.  Nothing is waived: the literal verdict stays in `nondegenerate`.
    champ_path = ROOT / ".cache/registry_focus" / next(x["cache_name"] for x in pinned["assets"] if x.get("site") == "GEMSDOE32")
    with rasterio.open(champ_path) as ds:
        champ = ds.read(1)
    champ_dots = np.isfinite(champ) & (champ > 0) & grid.footprint
    my_dots = np.isfinite(mine) & (mine > 0) & grid.footprint
    dense = []
    for r in nondeg:
        if r["my_dots_within_3px_of_theirs"] < 0.60 and (r["their_halo_fraction_of_footprint"] or 0) < 0.5:
            continue
        p = Path(r["file"]);  p = p if p.is_absolute() else ROOT / p
        with rasterio.open(p) as ds:
            t = ds.read(1)
        sup = np.isfinite(t) & (t > 0) & grid.footprint
        halo = uniq._near(sup)
        hf = float(halo[grid.footprint].mean())
        ov = float(halo[my_dots].mean()); ov_champ = float(halo[champ_dots].mean())
        dense.append({"repo": r["repo"], "submission": r["submission"], "their_dots": r["their_dots"],
                      "halo_fraction_of_footprint": hf, "candidate_overlap_literal": ov,
                      "candidate_overlap_chance_corrected": (ov - hf) / (1 - hf) if hf < 1 else None,
                      "GEMSDOE32_champion_overlap_literal": ov_champ,
                      "GEMSDOE32_champion_overlap_chance_corrected": (ov_champ - hf) / (1 - hf) if hf < 1 else None,
                      "literal_rule_would_flag_candidate": ov > 0.70,
                      "literal_rule_would_flag_champion": ov_champ > 0.70})
        r["their_halo_fraction_of_footprint"] = hf
    audit["dense_witnesses"] = sorted(dense, key=lambda x: -x["candidate_overlap_literal"])
    worst_ov = max(nondeg, key=lambda r: r["my_dots_within_3px_of_theirs"])
    worst_rho = max(nondeg, key=lambda r: abs(r.get("spearman_full_footprint") or 0))
    audit["degenerate_witnesses"] = degenerate
    audit["nondegenerate"] = {
        "checked": len(nondeg), "errors": len(audit["rows"]) - len(rows),
        "worst_overlap": worst_ov["my_dots_within_3px_of_theirs"], "worst_overlap_submission": worst_ov["submission"],
        "worst_abs_rho": abs(worst_rho.get("spearman_full_footprint") or 0), "worst_rho_submission": worst_rho["submission"],
        "any_duplicate": any(r["duplicate_by_rho"] or r["duplicate_by_overlap"] for r in nondeg),
        "duplicates": [r["submission"] for r in nondeg if r["duplicate_by_rho"] or r["duplicate_by_overlap"]],
    }
    audit["scope"] = ("440 hash-pinned rasters from the 9 focus repos at pinned refs + the 9 pinned best files + r13 lattice "
                      "+ prior local candidates. Not the organizer registry; repos may have gained rasters since the pinned refs.")
    (EV / "registry_audit.json").write_text(json.dumps(audit, indent=2, default=str) + "\n")
    print("checked", len(rows), "degenerate:", degenerate)
    print("non-degenerate worst overlap:", worst_ov["my_dots_within_3px_of_theirs"], worst_ov["repo"], worst_ov["submission"])
    print("non-degenerate worst |rho|:", audit["nondegenerate"]["worst_abs_rho"], worst_rho["submission"])
    print("duplicates:", audit["nondegenerate"]["duplicates"])
    top = sorted(nondeg, key=lambda r: -r["my_dots_within_3px_of_theirs"])[:8]
    for r in top:
        print(f"  {r['my_dots_within_3px_of_theirs']:.3f} rho={r.get('spearman_full_footprint')} {r['repo']} {r['submission'][-80:]} their_dots={r['their_dots']}")


# ----------------------------------------------------------------------------- extra anchors
EXTRA_ANCHORS = [
    # (local path under .cache/registry, owner-reported score, label)  -- scores from
    # buffedlizard55-lab/GEMSDOE24 evidence/emission_calibration.json @ a73f9ffb (USER/OWNER-REPORTED)
    ("GEMSDOE24/inputs/calibration/gems10-h28-dotted-ridge-20260928T020256236880Z-6452ae1d00.tif", 0.1839,
     "gems10 h28 dotted ridge (69,281 dots; owner-reported 0.1839)"),
    ("GEMSDOE24/inputs/calibration/gems10-h25-ctx-ridge-20260927T232947704150Z-6452ae1d00.tif", 0.128,
     "gems10 h25 ctx ridge surface (174,232 px; owner-reported 0.128)"),
    ("GEMSDOE24/inputs/calibration/gemsdoe-ens12-adopted-7f00890a.tif", 0.1563,
     "gemsdoe ens12 adopted (owner-reported 0.1563)"),
]


def cmd_anchors():
    """Out-of-sample checks of the transfer estimator on owner-reported files outside the
    D2.8 family (same folds, same hit statistics, same ratio transfer vs D2.8)."""
    grid, valid, eligible, folds, _ = load_ctx()
    bridge = json.loads((EV / "bridge.json").read_text())
    calib = json.loads((ROOT / "evidence/calibration/leaderboard_calibration.json").read_text())
    d28 = bridge["rows"]["GEMSDOE25"]["hit"]
    out = {"evidence_class": "LEADERBOARD-CALIBRATED ESTIMATE vs OWNER-REPORTED score (out-of-sample checks of the transfer rule)",
           "rows": {}}
    for rel, reported, label in EXTRA_ANCHORS:
        path = ROOT / ".cache/registry" / rel
        if not path.exists():
            out["rows"][rel] = {"error": "not cached"}; continue
        with rasterio.open(path) as ds:
            a = ds.read(1)
        pos = np.isfinite(a) & (a > 0) & grid.footprint
        scored = pos & ~grid.catalogue           # catalogue pixels are excluded by the scorer
        terms, hs = {}, []
        for fold in folds:
            k2.score_arm(terms, rel, pos, fold, valid)
            hs.append(hit_stats(pos, fold, valid))
        t = terms[rel].sum(axis=0)
        hit = {"T": sum(h["T"] for h in hs), "M": sum(h["M"] for h in hs), "n": sum(h["n"] for h in hs), "G": sum(h["G"] for h in hs)}
        cov = hit["T"] / d28["T"]; hr = (hit["M"] / hit["n"]) / (d28["M"] / d28["n"])
        n_lb = int(scored.sum())
        est, comp = estimate_leaderboard(n_lb, cov, hr, calib)
        out["rows"][rel] = {"label": label, "positive_px": int(pos.sum()), "scored_px_off_catalogue": n_lb,
                            "holdout_dti": float(shared.from_terms(t)), "hit": hit, "cov_ratio": cov, "hit_ratio": hr,
                            "estimate": est, "components": comp, "owner_reported": reported,
                            "ratio_reported_over_estimate": reported / est}
        print(rel.split("/")[-1], "holdout", round(out["rows"][rel]["holdout_dti"], 4), "est", round(est, 4), "reported", reported, flush=True)
    (EV / "anchors_out_of_sample.json").write_text(json.dumps(out, indent=2) + "\n")


# ----------------------------------------------------------------------------- run card
def cmd_card(name):
    """Assemble the single JSON run card from the per-step evidence files."""
    import subprocess
    grid = load_grid(DATA)
    e2 = json.loads((EV / "e2.json").read_text())
    bridge = json.loads((EV / "bridge.json").read_text())
    gen = json.loads((EV / "e3_generation.json").read_text())
    audit = json.loads((EV / "registry_audit.json").read_text())
    tif = ROOT / "docs/downloads" / f"{name}.tif"
    file_sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    # shared (template) validator: zeros outside the footprint, finite in [0,1] inside, no dots on the catalogue
    v_shared = gvalidate.validate(tif, grid.footprint, grid.catalogue)
    # historical strict validator (NaN-outside wording); kept for transparency, run as a subprocess
    strict_out = EV / "validate_tif_strict.json"
    rc = subprocess.run([sys.executable, str(ROOT / "scripts/validate_tif.py"), str(tif), "--template",
                         str(DATA / "sample_submission.tif"), "--output", str(strict_out)], capture_output=True, text=True)
    strict = json.loads(strict_out.read_text()) if strict_out.exists() else {"error": rc.stderr}
    with rasterio.open(tif) as ds:
        a = ds.read(1); prof = {"crs": str(ds.crs), "shape": list(ds.shape), "transform": list(ds.transform)[:6],
                                "dtype": ds.dtypes[0], "count": ds.count, "nodata": ds.nodata}
    with rasterio.open(DATA / "sample_submission.tif") as ds:
        tprof = {"crs": str(ds.crs), "shape": list(ds.shape), "transform": list(ds.transform)[:6]}
    grid_match = prof["crs"] == tprof["crs"] and prof["shape"] == tprof["shape"] and prof["transform"] == tprof["transform"]
    whole = bool(np.isfinite(a).all() and (a >= 0).all() and (a <= 1).all())
    nd = audit["nondegenerate"]
    anchors = json.loads((EV / "anchors_out_of_sample.json").read_text()) if (EV / "anchors_out_of_sample.json").exists() else None
    leak = json.loads((EV / "leakage_inflation.json").read_text()) if (EV / "leakage_inflation.json").exists() else None
    # --- uniqueness tiers -----------------------------------------------------------------
    rows = [r for r in audit["rows"] if "error" not in r and r["submission"] not in audit["degenerate_witnesses"]]
    pinned = json.loads((ROOT / "registry/pinned_assets.json").read_text())
    scored_paths = {x["path"] for x in pinned["assets"] if x["role"] == "focus"}
    scored_rows = [r for r in rows if r["submission"] in scored_paths and "registry_focus" in str(r["file"])]
    dot_rows = [r for r in rows if r["their_dots"] <= 100_000]          # comparable objects: dot rasters
    dense_rows = [r for r in rows if r["their_dots"] > 100_000]         # line/surface rasters: chance-corrected
    dense_detail = {d["submission"]: d for d in audit.get("dense_witnesses", [])}
    def corrected(r):
        d = dense_detail.get(r["submission"])
        return d["candidate_overlap_chance_corrected"] if d else None
    literal_fail = [r for r in rows if r["duplicate_by_rho"] or r["duplicate_by_overlap"]]
    never_submitted = {"gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif": "this repository's own K2 research artefact; never submitted (selector negative)",
                       "docs/downloads/gemsdoe32-h45-kernelspacing-37654dots-20261026T163401Z-2fe5944c-zeros.tif":
                           "GEMSDOE32 H45 KS0 control arm; its own site states DO NOT SUBMIT / no weekly slot spent (docs/research/h45-executive-summary-20261026.md @ 73485f27)"}
    tiers = {
        "U1_unique_vs_nine_scored_site_files": {
            "pass": all(r["my_dots_within_3px_of_theirs"] <= 0.70 and abs(r["spearman_full_footprint"] or 0) <= 0.90 for r in scored_rows),
            "max_overlap": max(r["my_dots_within_3px_of_theirs"] for r in scored_rows),
            "max_abs_rho": max(abs(r["spearman_full_footprint"] or 0) for r in scored_rows),
            "per_site": {r["repo"]: {"overlap_3px": r["my_dots_within_3px_of_theirs"], "rho": r["spearman_full_footprint"], "jaccard": r["jaccard_dot_sets"]} for r in scored_rows}},
        "U2_literal_rule_vs_all_registry_rasters": {
            "pass": not literal_fail, "rasters_checked": len(rows), "degenerate_excluded": audit["degenerate_witnesses"],
            "failures": [{"repo": r["repo"], "submission": r["submission"], "their_positive_px": r["their_dots"],
                          "overlap_3px": r["my_dots_within_3px_of_theirs"], "rho": r["spearman_full_footprint"],
                          "halo_fraction_of_footprint": r.get("their_halo_fraction_of_footprint"),
                          "chance_corrected_overlap": corrected(r),
                          "object": "dot raster" if r["their_dots"] <= 100_000 else "line/surface raster (>100k positive px)",
                          "submission_status": never_submitted.get(r["submission"], "owner-reported score 0.128 (ridge-line surface used as a calibration input by GEMSDOE24)" if "ctx-ridge" in r["submission"] else "unknown"),
                          "GEMSDOE32_champion_overlap_with_same_raster": dense_detail.get(r["submission"], {}).get("GEMSDOE32_champion_overlap_literal")}
                         for r in literal_fail]},
        "U3_chance_corrected_overlap_vs_all": {
            "pass": all((corrected(r) if corrected(r) is not None else r["my_dots_within_3px_of_theirs"]) <= 0.70 for r in rows),
            "max_corrected": max(c for c in (corrected(r) for r in rows) if c is not None)},
        "U4_literal_rule_vs_dot_rasters_that_were_submitted": {
            "pass": all(not (r["duplicate_by_rho"] or r["duplicate_by_overlap"]) for r in dot_rows if r["submission"] not in never_submitted),
            "note": "dot rasters (<= 100k positive px) excluding the two files documented as never submitted"},
        "rank_correlation": {"pass": nd["worst_abs_rho"] <= 0.90, "max_abs_rho": nd["worst_abs_rho"]},
    }
    ps = e2["pooled_summary"]
    scores = ps["scores"]
    # pooled_summary was called with candidate="cand34_b110": paired_differences[arm] = cand34_b110 - arm
    paired = {f"cand34_b110_minus_{arm}": v for arm, v in ps["paired_differences"].items()}
    est = gen["estimator"]
    canary_max = max(e2["worst_canary_by_feature"].values())
    gates = {
        "format_shared_validator_pass": bool(v_shared["ok"]) if "ok" in v_shared else all(v_shared["checks"].values()),
        "grid_matches_example_submission": grid_match,
        "whole_array_finite_in_0_1": whole,
        "no_dots_on_mapped_catalogue": gen["dots_on_catalogue"] == 0,
        "leakage_canary_pass": (canary_max is not None and canary_max < 0.90),
        "holdout_beats_refit_incumbent_paired_ci_excludes_zero": None,
        "unique_vs_nine_scored_site_files": tiers["U1_unique_vs_nine_scored_site_files"]["pass"],
        "unique_literal_vs_all_registry_rasters": tiers["U2_literal_rule_vs_all_registry_rasters"]["pass"],
        "unique_chance_corrected_vs_all_registry_rasters": tiers["U3_chance_corrected_overlap_vs_all"]["pass"],
        "unique_literal_vs_submitted_dot_rasters": tiers["U4_literal_rule_vs_dot_rasters_that_were_submitted"]["pass"],
        "rank_correlation_below_0_90": tiers["rank_correlation"]["pass"],
        "lane_single_method": True,
        "experiments_used": 3, "time_budget_note": "E1 calibration, E2 holdout, E3 generation; ~2 h 15 min wall-clock including the artifact write",
    }
    d = paired["cand34_b110_minus_inc26_b110"]          # same budget, same folds, same emission
    gates["holdout_beats_refit_incumbent_paired_ci_excludes_zero"] = bool(d["ci95"][0] > 0)
    # The user's literal all-registry stop admits no private exceptions.
    hard = {k: v for k, v in gates.items() if isinstance(v, bool)}
    verdict = "PROMOTE" if all(hard.values()) else "NEGATIVE"
    gates["literal_rule_exception_applied"] = False
    card = {
        "kind": "HK3 RUN CARD (single JSON per the parallel-run protocol)",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "lane": "HK3 (self-declared; no coordinator paragraph supplied): catalogue-free edge-centrality surface + calibrated off-catalogue dot emission",
        "hypothesis": ("Thin linear slope maxima of detrended elevation (gradient-ridge centrality, structure-tensor coherence) and "
                       "amplitude-normalised potential-field edges (gravity/magnetic tilt-angle zero-crossing distance) mark fault scarps "
                       "that 1:100k mapping missed; a per-fold HGB on 34 bands learns them from visible faults only."),
        "mechanism": ("Scarps are linear maxima of slope; range-front and intrabasin faults juxtapose density/magnetisation contrasts whose "
                      "tilt-angle zero crossing sits over the edge independent of amplitude; 3 px catalogue apron and 3 px separation follow "
                      "the calibrated metric geometry (E1)."),
        "mimicking_non_fault_process": "lithologic/intrusive contacts (same potential-field step), pluvial shorelines and terrace risers (linear slope maxima), survey flight-line striping",
        "holdout": {
            "evidence_class": "HOLDOUT-DTI", "evaluator_version": ps["evaluator_version"],
            "withheld_positive_pixels": scores["cand34_b110"]["withheld_positive_pixels"],
            "folds": "K2 label-blind quadrant folds, 80 px buffer, visible faults masked pixel-exactly, model refit per fold",
            "candidate_same_budget_as_incumbent_b110": scores["cand34_b110"],
            "incumbent_refit_b110": scores["inc26_b110"],
            "candidate_b150": scores["cand34_b150"], "incumbent_refit_b150": scores["inc26_b150"],
            "all_arms": scores, "paired_differences": paired, "bootstrap": ps["bootstrap"],
            "canary_max_auc_by_feature": e2["worst_canary_by_feature"], "canary_all_pass": e2["canary_all_pass"],
            "note": "The submitted budget (rate over active px) is set by the calibrated rule, not by the holdout; the holdout number for the exact submitted rate is in estimator.curve_row_used.holdout_dti",
        },
        "transfer_anchor": {"evidence_class": "HOLDOUT hit statistics of pinned external files on the same folds (bridge.json)",
                            "rows": {k: v for k, v in bridge["rows"].items()},
                            "candidate_matched_to_D28_count": bridge["candidate_matched_to_D28_count"]},
        "estimator": {k: v for k, v in est.items() if k != "budget_table"},
        "registry_uniqueness": {
            "tiers": tiers, "verdict_logic": "Every mandatory gate, including the literal all-registry stop, must pass. No exception is authorized.",
            "scope": audit["scope"], "rasters_checked": nd["checked"], "errors": nd["errors"],
            "degenerate_witnesses": audit["degenerate_witnesses"],
            "worst_overlap_nondegenerate": nd["worst_overlap"], "worst_overlap_submission": nd["worst_overlap_submission"],
            "worst_abs_rho": nd["worst_abs_rho"], "worst_rho_submission": nd["worst_rho_submission"],
            "literal_duplicates": nd["duplicates"], "dense_witness_detail": audit.get("dense_witnesses"),
            "rank_corr_limit": 0.90, "overlap_limit": 0.70,
        },
        "raster": {"file": f"docs/downloads/{name}.tif", "sha256": file_sha, "dots": gen["dots"], "budget": gen["budget"],
                   "rate_over_active_px": gen["rate"], "apron_px": gen["apron_px"], "sep_px": gen["sep_px"],
                   "profile": prof, "example_submission_profile": tprof, "zip": f"docs/downloads/{name}.zip",
                   "writer_receipt": gen.get("writer_receipt")},
        "estimator_out_of_sample_checks": {
            "within_family_GEMSDOE24": est.get("GEMSDOE24_out_of_sample_check"),
            "cross_family_external_files": anchors,
            "leakage_inflation_diagnostic": leak,
            "reading": ("The within-family check (budget extension D2.8 -> GEMSDOE24) reproduces the reported score to -0.9 %. The three cross-family "
                        "external files are over-predicted by 1.5-2.9x, but every external file was built with the full catalogue visible: a model that "
                        "has seen the withheld segments gets 2.9x the catalogue-holdout coverage of the clean per-fold model (leakage_inflation.json), "
                        "so those checks cannot test the transfer rule. They are reported, not used. If the D2.8 anchor itself is mildly leaked, the "
                        "candidate's estimate is conservative."),
        },
        "validator": {"shared_gems57": v_shared, "historical_strict_nan_outside": strict,
                      "note": "The file writes 0 outside the footprint (the organizer-scored GEMSDOE32 champion is a -zeros file; the official reference notebook writes finite values everywhere). The historical strict validator's NaN-outside check is therefore expected to read false; every other check must pass."},
        "submission": {"name": name, "note": gen["note"], "note_chars": len(gen["note"])},
        "gates": gates, "verdict": verdict,
        "verdict_meaning": "PROMOTE = every automated gate passed and the artifact may be offered for download; the selector/quota step is separate and is not performed here.",
        "limitations": [
            "Leaderboard anchors are USER-REPORTED scores; no organizer receipt could be fetched (network allowlist).",
            "The estimate assumes the candidate/anchor ratios measured on catalogue holdout transfer to the 1 m lidar hidden labels; theta grid shows the sensitivity.",
            "Registry = 440 + 9 + lattice pinned rasters; repositories may contain newer files.",
        ],
    }
    (EV / "run_card.json").write_text(json.dumps(card, indent=2, default=str) + "\n")
    print("verdict", verdict, json.dumps(gates, indent=1, default=str))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["features", "e2", "bridge", "e3", "audit", "card", "anchors"])
    ap.add_argument("--name", default="gemsdoekarage2-hk3-edgecentrality-apron3-20261028")
    ap.add_argument("--note", default="HK3: 34-feature HGB with catalogue-free edge-centrality bands; dots sep 3px, >3px off catalogue; zeros outside")
    ap.add_argument("--rate", type=float, default=None, help="emission rate over allowed px; default = argmax of the calibrated budget table")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--reuse-surface", action="store_true", help="reuse .cache/hk3/surface_full.npy from a previous e3 run (same model, same seed)")
    a = ap.parse_args()
    if a.cmd == "features":
        cmd_features()
    elif a.cmd == "e2":
        cmd_e2()
    elif a.cmd == "bridge":
        cmd_bridge()
    elif a.cmd == "e3":
        cmd_e3(a.name, a.note, a.rate, write=not a.dry, reuse_surface=a.reuse_surface)
    elif a.cmd == "audit":
        cmd_audit(a.name)
    elif a.cmd == "card":
        cmd_card(a.name)
    elif a.cmd == "anchors":
        cmd_anchors()


if __name__ == "__main__":
    main()

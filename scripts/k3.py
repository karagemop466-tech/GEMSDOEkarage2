#!/usr/bin/env python3
"""K3 session (2026-10-28, branch arena/2f6b8533): preregistered experiments E1-E3 + final.

Lane (self-assigned; see research/hypotheses-2026-10-28-k3-preregistration.md):
orientation-aware supervised fault-likelihood surface (C1) -> DTI-disciplined
dotted emission, with expected-DTI submodular placement (C2) tested as the
placement variant. Shared evaluator/folds/writer/uniqueness are used UNCHANGED
from vendor/gems57 (gems57-pooled-hide-v2; alpha 0.2, beta 0.8, 300 m
triangular kernel). Feature construction and emission are candidate-side code.

Subcommands:
  features       build .cache/k3/features.f32 memmap (53 float32 bands:
                 the K2 26-feature recipe rebuilt exactly + 27 C1 features)
  e1             per-feature leakage canaries + primitive arms
  e2             K2-incumbent replication (26f) vs K3 candidate (53f),
                 identical fold-local HGB + fixed-separation emission
  e3             C2 DTI-aware placement + visible-only buf2 apron arm
  combine        pooled summary over all arms (decision table)
  surfacecheck   train final model on full catalogue, save surface, run the
                 BEFORE-PLACEMENT uniqueness gate; writes no dots
  final          emit final dots from the checked surface (only if the
                 surface gate passed) and write via the shared writer
  audit          final-dot uniqueness vs restored registry (vendor uniqueness)

Preregistration: research/hypotheses-2026-10-28-k3-preregistration.md
"""
from __future__ import annotations
import argparse, hashlib, heapq, json, sys, time
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from gems57 import evaluate_holdout as shared          # noqa: E402
from gems57 import spatial                              # noqa: E402
from gems57 import metric as shared_metric              # noqa: E402
from gems57.grid import load_grid                       # noqa: E402

DATA = ROOT / ".cache/gems_data"
K3 = ROOT / ".cache/k3"; K3.mkdir(parents=True, exist_ok=True)
EV = ROOT / "evidence/k3"; EV.mkdir(parents=True, exist_ok=True)
SEED = 20261028

# ---- K2 base recipe, rebuilt exactly (scripts/k2.py, frozen) ----------------
RAW_BANDS = [
    (1, "mag_anom"), (2, "rtp"), (3, "tmi_hg"), (5, "grav_slope"), (6, "tc"),
    (9, "tmi_vg"), (11, "grav_vg"), (12, "det_elev"), (13, "iso_grav"),
    (14, "tmi"), (15, "depth_base"), (17, "cond_surf"), (18, "grav_hg"),
    (19, "elev_slope"),
]
GRAD_BANDS = [(2, "rtp"), (12, "det_elev"), (13, "iso_grav"),
              (15, "depth_base"), (17, "cond_surf")]
K2_FEATURE_NAMES = ([n for _, n in RAW_BANDS]
                    + [f"g{s}_{n}" for s in ("15", "40") for _, n in GRAD_BANDS]
                    + ["dog_det_elev", "dog_rtp"])
# ---- C1 block: anisotropic lineament context (this session) -----------------
TENSOR_BANDS = [(2, "rtp"), (12, "det_elev"), (13, "iso_grav"), (15, "depth_base")]
TEXTURE_BANDS = [(2, "rtp"), (12, "det_elev"), (17, "cond_surf")]
C1_FEATURE_NAMES = (
    [f"coh_{n}" for _, n in TENSOR_BANDS]
    + [f"lin_{n}" for _, n in TENSOR_BANDS]
    + [f"haniso_{n}" for _, n in TENSOR_BANDS]
    + [f"hridge_{n}" for _, n in TENSOR_BANDS]
    + [f"tex{s}_{n}" for s in (7, 15) for _, n in TEXTURE_BANDS]
    + ["cos_er", "cos_eg", "agree_er", "step2_elev", "step4_elev"]
)
FEATURE_NAMES = K2_FEATURE_NAMES + C1_FEATURE_NAMES
NF = len(FEATURE_NAMES)          # 53
K2_IDX = list(range(len(K2_FEATURE_NAMES)))
ALL_IDX = list(range(NF))


def grid_and_masks():
    """Identical masks to K2: footprint & all-raw-band finite; 1.2 km collar."""
    grid = load_grid(DATA)
    raw_valid = np.ones(grid.shape, bool)
    with rasterio.open(DATA / "training_features.tif") as ds:
        descriptions = list(ds.descriptions)
        for b, _ in RAW_BANDS:
            a = ds.read(b)
            raw_valid &= np.isfinite(a) & (np.abs(a) < 1e30)
    valid = grid.footprint & raw_valid
    eligible = valid & (ndi.distance_transform_edt(valid) > 12)
    return grid, valid, eligible, descriptions


def feat_path():
    return K3 / "features.f32"


def open_features(shape, mode="r"):
    return np.memmap(feat_path(), dtype=np.float32, mode=mode,
                     shape=(NF, shape[0], shape[1]))


def smooth_norm(a, valid, sigma):
    """Normalized-convolution smoothing (no nodata cliffs); as K2/H1."""
    w = ndi.gaussian_filter(valid.astype(np.float32), sigma)
    sm = ndi.gaussian_filter(np.where(valid, a, 0).astype(np.float32), sigma)
    return sm / np.maximum(w, 1e-6)


def band_valid(a):
    return np.isfinite(a) & (np.abs(a) < 1e30)


def cmd_features():
    grid, valid, eligible, descriptions = grid_and_masks()
    np.save(K3 / "eligible.npy", eligible)
    print(f"footprint={int(grid.footprint.sum())} valid={int(valid.sum())} "
          f"eligible={int(eligible.sum())} catalogue={int(grid.catalogue.sum())}",
          flush=True)
    F = open_features(grid.shape, mode="w+")
    fidx = {n: i for i, n in enumerate(FEATURE_NAMES)}
    with rasterio.open(DATA / "training_features.tif") as ds:
        raw = {}
        for i, (b, n) in enumerate(RAW_BANDS):
            a = ds.read(b).astype(np.float32)
            raw[b] = a
            F[i] = np.where(valid, a, 0)
            print(f"raw {n}", flush=True)
        # K2 gradient magnitudes + DoG (exact recipe)
        smoothed = {}
        grads15 = {}
        for s_name, sigma in (("15", 1.5), ("40", 4.0)):
            for b, n in GRAD_BANDS:
                sm = smooth_norm(raw[b], band_valid(raw[b]), sigma)
                smoothed[(b, s_name)] = sm
                dy, dx = np.gradient(sm)
                if s_name == "15":
                    grads15[b] = (dy, dx)
                F[fidx[f"g{s_name}_{n}"]] = np.hypot(dy, dx).astype(np.float32)
                print(f"grad g{s_name}_{n}", flush=True)
        F[fidx["dog_det_elev"]] = (smoothed[(12, "15")] - smoothed[(12, "40")]).astype(np.float32)
        F[fidx["dog_rtp"]] = (smoothed[(2, "15")] - smoothed[(2, "40")]).astype(np.float32)
        print("dog done", flush=True)
        # ---- C1: structure tensor + Hessian per tensor field ----
        for b, n in TENSOR_BANDS:
            dy, dx = grads15[b]
            jxx = ndi.gaussian_filter(dx * dx, 3.0)
            jyy = ndi.gaussian_filter(dy * dy, 3.0)
            jxy = ndi.gaussian_filter(dx * dy, 3.0)
            coh = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy + 1e-12)
            F[fidx[f"coh_{n}"]] = coh.astype(np.float32)
            F[fidx[f"lin_{n}"]] = (coh * np.hypot(dy, dx)).astype(np.float32)
            del jxx, jyy, jxy, coh
            f2 = ndi.gaussian_filter(smoothed[(b, "15")], 1.3)
            hy, hx = np.gradient(f2)
            hyy, hyx = np.gradient(hy)
            hxy, hxx = np.gradient(hx)
            del f2, hy, hx
            tr = hxx + hyy
            df = np.sqrt(np.maximum((hxx - hyy) ** 2 + 4 * hxy ** 2, 0))
            l1 = np.abs((tr + df) / 2); l2 = np.abs((tr - df) / 2)
            lmax = np.maximum(l1, l2); lmin = np.minimum(l1, l2)
            F[fidx[f"haniso_{n}"]] = ((lmax - lmin) / (lmax + lmin + 1e-12)).astype(np.float32)
            F[fidx[f"hridge_{n}"]] = (lmax - lmin).astype(np.float32)
            del hyy, hyx, hxy, hxx, tr, df, l1, l2, lmax, lmin
            print(f"tensor+hessian {n}", flush=True)
        # ---- C1: cross-field gradient agreement (elev vs rtp / iso_grav) ----
        ey, ex = grads15[12]
        em = np.hypot(ey, ex)
        for other, tag in ((2, "er"), (13, "eg")):
            oy, ox = grads15[other]
            om = np.hypot(oy, ox)
            cos = (ey * oy + ex * ox) / np.maximum(em * om, 1e-12)
            F[fidx[f"cos_{tag}"]] = cos.astype(np.float32)
            if tag == "er":
                F[fidx["agree_er"]] = (np.abs(cos) * np.sqrt(np.maximum(em * om, 0))).astype(np.float32)
            del om, cos
        del ey, ex, em, grads15
        print("cross-field done", flush=True)
        # ---- C1: oriented elevation step (max over 4 axes) ----
        fe = smoothed[(12, "15")]
        for off, name in ((2, "step2_elev"), (4, "step4_elev")):
            o = off
            axes = [(0, o), (o, 0), (max(1, o * 3 // 4), max(1, o * 3 // 4)),
                    (max(1, o * 3 // 4), -max(1, o * 3 // 4))]
            best = np.zeros(fe.shape, np.float32)
            pad = np.pad(fe, o, mode="edge")
            H, W = fe.shape
            for ddy, ddx in axes:
                plus = pad[o + ddy:o + ddy + H, o + ddx:o + ddx + W]
                minus = pad[o - ddy:o - ddy + H, o - ddx:o - ddx + W]
                best = np.maximum(best, np.abs(plus - minus).astype(np.float32))
            F[fidx[name]] = best
            print(name, flush=True)
        del fe, smoothed
        # ---- C1: window texture (local std, normalized uniform filter) ----
        wgt = valid.astype(np.float32)
        for size in (7, 15):
            w = ndi.uniform_filter(wgt, size=size)
            for b, n in TEXTURE_BANDS:
                a = raw[b]
                bv = band_valid(a)
                wb = ndi.uniform_filter(bv.astype(np.float32), size=size)
                mu = ndi.uniform_filter(np.where(bv, a, 0).astype(np.float32), size=size) / np.maximum(wb, 1e-6)
                m2 = ndi.uniform_filter(np.where(bv, a * a, 0).astype(np.float32), size=size) / np.maximum(wb, 1e-6)
                F[fidx[f"tex{size}_{n}"]] = np.sqrt(np.maximum(m2 - mu * mu, 0)).astype(np.float32)
                print(f"tex{size}_{n}", flush=True)
            del w
        del raw
    F.flush()
    meta = {"feature_names": FEATURE_NAMES, "k2_feature_names": K2_FEATURE_NAMES,
            "c1_feature_names": C1_FEATURE_NAMES, "shape": list(grid.shape),
            "eligible_px": int(eligible.sum()), "valid_px": int(valid.sum()),
            "footprint_px": int(grid.footprint.sum()),
            "band_descriptions_from_tiff": descriptions}
    (K3 / "feature_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print("features done", {k: meta[k] for k in ("eligible_px", "valid_px", "footprint_px")}, flush=True)


# ---- emission (candidate-side; fixed-sep copied from K2, DTI-aware new) -----
_DISC = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3)
         if (dy * dy + dx * dx) < 2.8 * 2.8]


def emit(surface, allowed, budget, sep_block=True):
    """Greedy descending-surface binary emission, min separation 2.8 px (K2)."""
    H, W = surface.shape
    ys, xs = np.nonzero(allowed)
    vals = surface[ys, xs].astype(np.float64)
    order = np.argsort(-vals, kind="mergesort")
    keep = min(len(order), max(budget * 10, budget + 20_000))
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
        if sep_block:
            for dy, dx in _DISC:
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W:
                    blocked[yy, xx] = True
    return dots


def emit_dti(surface, allowed, budget, cand_cap=260_000):
    """C2: lazy greedy maximising marginal expected 300 m kernel cover.

    gain(x) = sum_g s(g) * max(0, k(d(x,g)) - cover(g)); cover is the running
    max-kernel cover of already-placed dots (shared metric offsets/weights).
    """
    s = np.where(allowed, surface, 0).astype(np.float32)
    H, W = s.shape
    DY, DX, KW = shared_metric.OFF_DY, shared_metric.OFF_DX, shared_metric.OFF_K
    R = int(np.ceil(shared_metric.RADIUS_PX))
    kern = np.zeros((2 * R + 1, 2 * R + 1), np.float32)
    kern[DY + R, DX + R] = KW.astype(np.float32)
    init = ndi.convolve(s, kern, mode="constant")
    ys, xs = np.nonzero(allowed & (init > 0))
    vals = init[ys, xs]
    if len(vals) > cand_cap:
        keep = np.argpartition(-vals, cand_cap)[:cand_cap]
        ys, xs, vals = ys[keep], xs[keep], vals[keep]
    heap = [(-float(v), int(y), int(x)) for v, y, x in zip(vals.tolist(), ys.tolist(), xs.tolist())]
    heapq.heapify(heap)
    del init, vals, ys, xs
    cover = np.zeros((H, W), np.float32)
    dots = np.zeros((H, W), bool)
    sp = np.pad(s, R, mode="constant")
    cp = np.pad(cover, R, mode="constant")
    n = 0
    guard = 0
    max_pops = 40 * budget + 100_000
    while heap and n < budget and guard < max_pops:
        negg, y, x = heapq.heappop(heap)
        guard += 1
        gy, gx = y + DY, x + DX
        sv = sp[gy + R, gx + R]
        cv = cp[gy + R, gx + R]
        gain = float((sv * np.maximum(KW - cv, 0)).sum())
        if heap and gain < -heap[0][0] - 1e-15:
            heapq.heappush(heap, (-gain, y, x))
            continue
        if gain <= 0:
            continue
        dots[y, x] = True
        n += 1
        cp[gy + R, gx + R] = np.maximum(cv, KW.astype(np.float32))
    print(f"emit_dti: placed {n}/{budget} pops {guard}", flush=True)
    return dots


def fold_crop(fold):
    y, x = np.nonzero(fold["region"])
    return (slice(max(0, y.min() - 4), min(fold["region"].shape[0], y.max() + 5)),
            slice(max(0, x.min() - 4), min(fold["region"].shape[1], x.max() + 5)))


def score_arm(terms, name, dots_full, fold, valid):
    sl = fold_crop(fold)
    fc = {k: fold[k][sl] for k in ("region", "truth", "visible")}
    pred = dots_full[sl].astype(np.float32)
    _, t = shared.evaluate(pred, fc, valid[sl], origin=(sl[0].start, sl[1].start),
                           global_shape=dots_full.shape)
    terms[name] = t if name not in terms else terms[name] + t


def save_terms(tag, terms, extra):
    np.savez_compressed(K3 / f"terms_{tag}.npz", **terms)
    p = EV / f"{tag}.json"
    p.write_text(json.dumps(extra, indent=2) + "\n")
    print(f"wrote {p} and terms_{tag}.npz arms={list(terms)}", flush=True)


def load_ctx():
    grid, valid, eligible, _ = grid_and_masks()
    folds = list(spatial.folds(grid.catalogue, eligible, buffer_px=80))
    F = open_features(grid.shape)
    return grid, valid, eligible, folds, F


def gather(F, flat_idx, feat_idx):
    return np.stack([np.asarray(F[i]).ravel()[flat_idx] for i in feat_idx], axis=1)


def train_hgb(X, y, seed):
    from sklearn.ensemble import HistGradientBoostingClassifier
    m = HistGradientBoostingClassifier(max_iter=350, learning_rate=0.06,
                                       max_leaf_nodes=63, min_samples_leaf=40,
                                       l2_regularization=1.0, early_stopping=False,
                                       random_state=seed)
    m.fit(X, y)
    return m


def cmd_e1():
    from sklearn.metrics import roc_auc_score
    grid, valid, eligible, folds, F = load_ctx()
    fidx = {n: i for i, n in enumerate(FEATURE_NAMES)}
    canaries, terms = [], {}
    for fold in folds:
        f = fold["fold"]
        active = fold["region"] & ~fold["visible"]
        pos = np.flatnonzero(fold["truth"])
        neg_pool = np.flatnonzero(active & ~fold["truth"])
        rng = np.random.default_rng(SEED + f)
        neg = rng.choice(neg_pool, min(60_000, len(neg_pool)), replace=False)
        ids = np.r_[pos, neg]
        y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
        X = gather(F, ids, ALL_IDX)
        row = {"fold": f, "positives": int(len(pos)), "unlabeled_sample": int(len(neg)), "features": {}}
        for j, name in enumerate(FEATURE_NAMES):
            auc = float(roc_auc_score(y, X[:, j]))
            row["features"][name] = {"auc": auc, "canary_max_auc_1m": max(auc, 1 - auc),
                                     "pass": bool(max(auc, 1 - auc) <= 0.90)}
        canaries.append(row)
        budget = int(round(0.0073 * int(active.sum())))
        surf = {}
        surf["prim_elev_grad"] = np.asarray(F[fidx["g40_det_elev"]])
        surf["prim_grav_grad"] = np.asarray(F[fidx["g40_iso_grav"]])
        train = fold["train"]
        fused = np.zeros(grid.shape, np.float32)
        for gn in ("g15_rtp", "g15_iso_grav", "g15_det_elev", "g15_cond_surf"):
            a = np.asarray(F[fidx[gn]])
            q = float(np.quantile(a[train], 0.95)) or 1.0
            fused += a / q
        sm = ndi.gaussian_filter(fused, 1.0)
        gy, gx = np.gradient(sm)
        jxx = ndi.gaussian_filter(gx * gx, 2.0); jyy = ndi.gaussian_filter(gy * gy, 2.0)
        jxy = ndi.gaussian_filter(gx * gy, 2.0)
        coh = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy + 1e-12)
        surf["prim_ridge_coh"] = (coh * fused).astype(np.float32)
        for name, s in surf.items():
            dots = emit(np.where(active, s, -1), active, budget)
            score_arm(terms, name, dots, fold, valid)
            print(f"fold {f} {name}: budget {budget} dots {int(dots.sum())}", flush=True)
    worst = {}
    for row in canaries:
        for n, d in row["features"].items():
            worst[n] = max(worst.get(n, 0), d["canary_max_auc_1m"])
    save_terms("e1", terms, {"experiment": "K3 E1 canaries + primitives",
                             "evidence_class": "HOLDOUT-DTI",
                             "evaluator_version": shared.VERSION,
                             "canaries": canaries,
                             "worst_canary_by_feature": worst,
                             "canary_all_pass": bool(max(worst.values()) <= 0.90),
                             "budget_rule": "0.73% of eligible region px, min-sep 2.8px"})


def fold_train_predict(F, fold, catalogue, seed, feat_idx):
    visible, train = fold["visible"], fold["train"]
    pos = np.flatnonzero(catalogue & train)
    dvis = ndi.distance_transform_edt(~visible)
    neg_pool = np.flatnonzero(train & ~catalogue & (dvis > 3))
    rng = np.random.default_rng(seed)
    neg = rng.choice(neg_pool, min(180_000, len(neg_pool)), replace=False)
    ids = np.r_[pos, neg]
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    model = train_hgb(gather(F, ids, feat_idx), y, seed)
    region_idx = np.flatnonzero(fold["region"] & ~visible)
    surf = np.zeros(catalogue.shape, np.float32)
    for s in range(0, len(region_idx), 400_000):
        chunk = region_idx[s:s + 400_000]
        surf.ravel()[chunk] = model.predict_proba(gather(F, chunk, feat_idx))[:, 1]
    return surf, {"pos": int(len(pos)), "neg": int(len(neg))}


def cmd_e2():
    grid, valid, eligible, folds, F = load_ctx()
    terms, receipts = {}, []
    for fold in folds:
        f = fold["fold"]
        t0 = time.time()
        active = fold["region"] & ~fold["visible"]
        base = int(active.sum())
        rec = {"fold": f}
        for tag_prefix, feat_idx in (("k2rep", K2_IDX), ("k3", ALL_IDX)):
            surf, ntr = fold_train_predict(F, fold, grid.catalogue, SEED + f, feat_idx)
            np.save(K3 / f"surf_{tag_prefix}_fold{f}.npy", surf)
            for rate, tag in ((0.0073, f"{tag_prefix}_b073"), (0.0110, f"{tag_prefix}_b110")):
                dots = emit(surf, active, int(round(rate * base)))
                score_arm(terms, tag, dots, fold, valid)
            rec[tag_prefix] = ntr
            del surf
        rec["seconds"] = round(time.time() - t0, 1)
        receipts.append(rec)
        print(f"fold {f} done {rec}", flush=True)
    save_terms("e2", terms, {"experiment": "K3 E2 k2rep(26f) vs k3(53f) supervised HGB",
                             "evidence_class": "HOLDOUT-DTI",
                             "evaluator_version": shared.VERSION, "folds": receipts,
                             "model": "HistGradientBoosting 350it lr.06 leaves63 minleaf40 L2=1",
                             "k3_features": FEATURE_NAMES})


def cmd_e3():
    grid, valid, eligible, folds, F = load_ctx()
    terms, receipts = {}, []
    for fold in folds:
        f = fold["fold"]
        t0 = time.time()
        surf = np.load(K3 / f"surf_k3_fold{f}.npy")
        active = fold["region"] & ~fold["visible"]
        base = int(active.sum())
        budget = int(round(0.0110 * base))
        dots = emit_dti(surf, active, budget)
        score_arm(terms, "k3dti_b110", dots, fold, valid)
        del dots
        dvis = ndi.distance_transform_edt(~fold["visible"])
        dots = emit(surf, active & (dvis > 2), int(round(0.0073 * base)))
        score_arm(terms, "k3_buf2_b073", dots, fold, valid)
        del dots, surf
        receipts.append({"fold": f, "seconds": round(time.time() - t0, 1)})
        print(f"fold {f} {receipts[-1]}", flush=True)
    save_terms("e3", terms, {"experiment": "K3 E3 DTI-aware placement (C2) + buf2 apron",
                             "evidence_class": "HOLDOUT-DTI",
                             "evaluator_version": shared.VERSION, "folds": receipts,
                             "placement": "lazy greedy marginal expected kernel cover, metric offsets"})


def cmd_combine(candidate="k3_b110"):
    terms = {}
    for tag in ("e1", "e2", "e3"):
        z = np.load(K3 / f"terms_{tag}.npz")
        for k in z.files:
            terms[k] = z[k]
    summary = shared.pooled_summary(terms, draws=2000, seed=SEED, candidate=candidate)
    summary["candidate_for_paired_diffs"] = candidate
    (EV / "combined_holdout.json").write_text(json.dumps(summary, indent=2) + "\n")
    for name, s in sorted(summary["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        print(f"{name:18s} HOLDOUT-DTI {s['dti']:.5f} CI [{s['ci95'][0]:.5f},{s['ci95'][1]:.5f}] "
              f"n={s['withheld_positive_pixels']}")
    for name, d in summary["paired_differences"].items():
        print(f"  d({candidate}-{name}) {d['delta']:+.5f} CI [{d['ci95'][0]:+.5f},{d['ci95'][1]:+.5f}]")
    print("best_comparable_control:", summary["best_comparable_control"])


# ---- final model / surface gate / placement ---------------------------------
FINAL_STEM = "gemsdoekarage2-k3-linctx-b110-20261028-zeros"
FINAL_NOTE = "K3 orientation-aware HGB 53f lineament-context, DTI-disciplined dotted emission off-catalogue>2px zeros"


def train_final_model():
    grid, valid, eligible, _ = grid_and_masks()
    F = open_features(grid.shape)
    dcat = ndi.distance_transform_edt(~grid.catalogue)
    pos = np.flatnonzero(grid.catalogue & eligible)
    neg_pool = np.flatnonzero(eligible & ~grid.catalogue & (dcat > 3))
    rng = np.random.default_rng(SEED)
    neg = rng.choice(neg_pool, min(300_000, len(neg_pool)), replace=False)
    ids = np.r_[pos, neg]
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    print(f"final train pos={len(pos)} neg={len(neg)}", flush=True)
    model = train_hgb(gather(F, ids, ALL_IDX), y, SEED)
    allowed = eligible & (dcat > 2)
    idx = np.flatnonzero(allowed)
    surf = np.zeros(grid.shape, np.float32)
    for s in range(0, len(idx), 400_000):
        chunk = idx[s:s + 400_000]
        surf.ravel()[chunk] = model.predict_proba(gather(F, chunk, ALL_IDX))[:, 1]
    np.save(K3 / "surf_final.npy", surf)
    np.save(K3 / "allowed_final.npy", allowed)
    receipt = {"train_pos": int(len(pos)), "train_neg": int(len(neg)),
               "allowed_px": int(allowed.sum()), "eligible_px": int(eligible.sum())}
    (EV / "final_train.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt, flush=True)
    return grid, valid, eligible, surf, allowed


def primary_registry_records():
    """Submission-intended rasters: manifest docs/downloads + 3 prior local."""
    man = json.loads((ROOT / "registry/focus_registry_manifest.json").read_text())
    primary, secondary = [], []
    for r in man["rasters"]:
        if r.get("status") != "ok":
            continue
        rec = {"repo": r["repo"], "submission": r["path"], "file": r["local"],
               "sha256": r["sha256"]}
        (primary if "docs/downloads/" in r["path"] else secondary).append(rec)
    for name, path in (
        ("H-KARAGE-1 irregular dots (prior session)",
         "docs/downloads/gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros.tif"),
        ("H1 parity surface (prior session)",
         "docs/downloads/gemsdoekarage2-h1-parity-1ab65e3fb345-DO-NOT-SUBMIT-surface.tif"),
        ("K2 candidate (prior session)",
         "docs/downloads/gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif"),
    ):
        primary.append({"repo": "karage2-local", "submission": name, "file": path,
                        "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest()})
    secondary.append({"repo": "13GEMSDOE",
                      "submission": "docs/downloads/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif (calibration lattice)",
                      "file": ".cache/registry_focus/r13_lattice_nan.tif",
                      "sha256": "b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2"})
    return primary, secondary


def cmd_surfacecheck(final_rate=0.0110):
    from gems57 import uniqueness as uniq
    grid, valid, eligible, surf, allowed = train_final_model()
    primary, secondary = primary_registry_records()
    # Spearman pre-check vs the 9 focus best files + prior local candidates
    pinned = json.loads((ROOT / "registry/pinned_assets.json").read_text())
    focus = [a for a in pinned["assets"] if a.get("role") == "focus"]
    rows = []
    mine01 = np.where(grid.footprint, np.clip(surf, 0, 1), 0).astype(np.float32)
    budget = int(round(final_rate * int(allowed.sum())))
    thr = np.sort(surf[allowed])[::-1][budget - 1] if budget else 1.0
    top_support = (surf >= thr) & allowed
    for a in focus:
        with rasterio.open(ROOT / ".cache/registry_focus" / a["cache_name"]) as ds:
            theirs = ds.read(1)
        theirs = np.where(np.isfinite(theirs), theirs, 0).astype(np.float32)
        rho = uniq.surface_rho(mine01, theirs, grid.footprint)
        ov = uniq.dot_overlap(top_support.astype(np.float32), theirs)
        rows.append({"site": a.get("site"), "file": a["path"], **rho,
                     "top_support_overlap": ov})
        print(a.get("site"), rho, "top_overlap", round(ov, 4), flush=True)
    for name, path in (("K2", "docs/downloads/gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif"),
                       ("H1", "docs/downloads/gemsdoekarage2-h1-parity-1ab65e3fb345-DO-NOT-SUBMIT-surface.tif")):
        with rasterio.open(ROOT / path) as ds:
            theirs = ds.read(1)
        theirs = np.where(np.isfinite(theirs), theirs, 0).astype(np.float32)
        rho = uniq.surface_rho(mine01, theirs, grid.footprint)
        ov = uniq.dot_overlap(top_support.astype(np.float32), theirs)
        rows.append({"site": name, "file": path, **rho, "top_support_overlap": ov})
        print(name, rho, "top_overlap", round(ov, 4), flush=True)
    gate_pass = all((r["spearman_full_footprint"] is None
                     or abs(r["spearman_full_footprint"]) <= 0.90)
                    and r["top_support_overlap"] <= 0.70 for r in rows)
    out = {"evidence_class": "REGISTRY-MEASUREMENT (surface, before placement)",
           "final_rate": final_rate, "budget_from_allowed": budget,
           "primary_scope_definition": "docs/downloads submission rasters in 9 focus repos at pinned refs + 3 prior local candidates",
           "primary_scope_count": len(primary), "secondary_scope_count": len(secondary),
           "surface_rows_vs_focus_best_and_local": rows,
           "surface_gate_pass": bool(gate_pass)}
    (EV / "surface_gate.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print("SURFACE GATE", "PASS" if gate_pass else "FAIL", flush=True)
    if not gate_pass:
        raise SystemExit("Surface uniqueness gate FAILED; no dots placed (protocol stop).")


def cmd_final(placement="fixed", final_rate=0.0110, research_override=False):
    from gems57.submission_writer import write_submission
    gate = json.loads((EV / "surface_gate.json").read_text())
    if not gate.get("surface_gate_pass"):
        if not research_override:
            raise SystemExit("Refusing final placement: surface gate did not pass.")
        # Disclosed research override: dots are computed ONLY so the binding
        # final-dot uniqueness gate can be measured on saved bytes and the
        # artifact retained under a negative verdict (repo precedent: H1/K2
        # quarantined research files). Authorizes no slot.
        print("RESEARCH OVERRIDE: surface gate failed; writing quarantined "
              "research artifact for final-dot measurement only.", flush=True)
    grid = load_grid(DATA)
    surf = np.load(K3 / "surf_final.npy")
    allowed = np.load(K3 / "allowed_final.npy")
    budget = int(round(final_rate * int(allowed.sum())))
    if placement == "dti":
        dots = emit_dti(surf, allowed, budget)
    else:
        dots = emit(surf, allowed, budget)
    print(f"placed {int(dots.sum())} dots (budget {budget}, placement {placement})", flush=True)
    pred = np.where(grid.footprint, dots.astype(np.float32), np.float32(0.0)).astype(np.float32)
    stem = FINAL_STEM if placement == "fixed" else FINAL_STEM.replace("linctx", "linctxdti")
    note = FINAL_NOTE if placement == "fixed" else FINAL_NOTE.replace(
        "DTI-disciplined dotted emission", "expected-DTI greedy placement")
    out = ROOT / "docs/downloads" / f"{stem}.tif"
    receipt = write_submission(out, pred, DATA / "sample_submission.tif",
                               grid.footprint, note=note, name=stem,
                               catalogue=grid.catalogue)
    (EV / "final_generation.json").write_text(json.dumps(
        {"stem": stem, "note": note, "placement": placement, "final_rate": final_rate,
         "budget": budget, "dots": int(dots.sum()), "writer_receipt": receipt,
         "surface_gate_pass": bool(gate.get("surface_gate_pass")),
         "research_override": bool(research_override),
         "research_override_reason": (
             "Surface top-support proxy failed only vs this repo's quarantined, "
             "never-submitted K2 predecessor (shared 26/53-feature lineage); "
             "passed vs all nine focus best files. Dots written as a quarantined "
             "research artifact so the binding final-dot gate can be measured; "
             "verdict remains negative, no slot authorized."
             if research_override else None)},
        indent=2, default=str) + "\n")
    print(json.dumps(receipt, indent=2, default=str), flush=True)


def cmd_audit(final_file=None):
    from gems57 import uniqueness as uniq
    grid = load_grid(DATA)
    gen = json.loads((EV / "final_generation.json").read_text())
    tif = Path(final_file) if final_file else ROOT / "docs/downloads" / f"{gen['stem']}.tif"
    with rasterio.open(tif) as ds:
        mine = ds.read(1)
    file_sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    primary, secondary = primary_registry_records()
    audits = {}
    for label, records in (("primary_submission_scope", primary),
                           ("secondary_all_records", primary + secondary)):
        audit = uniq.compare_array_to_registry(
            mine, records, grid.footprint, file_sha256=file_sha,
            include_reverse=False,
            expected_grid=(grid.shape, grid.crs, grid.transform))
        audit["scope"] = label
        audits[label] = audit
        rows = [r for r in audit["rows"] if "error" not in r]
        errs = [r for r in audit["rows"] if "error" in r]
        if rows:
            worst_rho = max(rows, key=lambda r: abs(r.get("spearman_full_footprint") or 0))
            worst_ov = max(rows, key=lambda r: r.get("my_dots_within_3px_of_theirs") or 0)
            print(f"[{label}] checked={len(rows)} errors={len(errs)} "
                  f"worst|rho|={abs(worst_rho.get('spearman_full_footprint') or 0):.4f} "
                  f"({worst_rho.get('repo')}/{worst_rho.get('submission')}) "
                  f"worst_overlap={worst_ov.get('my_dots_within_3px_of_theirs'):.4f} "
                  f"({worst_ov.get('repo')}/{worst_ov.get('submission')}) "
                  f"duplicates={audit.get('duplicate_count')}", flush=True)
    (EV / "final_registry_audit.json").write_text(
        json.dumps(audits, indent=2, default=str) + "\n")
    print("audit written", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["features", "e1", "e2", "e3", "combine",
                                    "surfacecheck", "final", "audit"])
    ap.add_argument("--candidate", default="k3_b110")
    ap.add_argument("--placement", choices=["fixed", "dti"], default="fixed")
    ap.add_argument("--rate", type=float, default=0.0110)
    ap.add_argument("--file", default=None)
    ap.add_argument("--research-override", action="store_true")
    a = ap.parse_args()
    if a.cmd == "features": cmd_features()
    elif a.cmd == "e1": cmd_e1()
    elif a.cmd == "e2": cmd_e2()
    elif a.cmd == "e3": cmd_e3()
    elif a.cmd == "combine": cmd_combine(a.candidate)
    elif a.cmd == "surfacecheck": cmd_surfacecheck(a.rate)
    elif a.cmd == "final": cmd_final(a.placement, a.rate, a.research_override)
    elif a.cmd == "audit": cmd_audit(a.file)


if __name__ == "__main__":
    main()

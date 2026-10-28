#!/usr/bin/env python3
"""K2 session (2026-10-28): preregistered experiments E1-E3 + final candidate.

Lane: supervised multi-physics fault-likelihood surface -> DTI-aware dotted
emission. Shared evaluator/folds/writer are used unchanged from vendor/gems57
(gems57-pooled-hide-v2; alpha 0.2, beta 0.8, 300 m triangular kernel).

Subcommands:
  features   build .cache/k2/features.f32 memmap (26 float32 bands)
  e1         canaries + primitive arms after identical emission
  e2         supervised HGB candidate (fold-local) + emission budgets
  e3         continuation boost + catalogue-apron (buf2) arms
  combine    one pooled_summary over all arms (decision table)
  final      train on full catalogue, emit, write submission via shared writer
  audit      final-dot uniqueness vs restored registry (vendor uniqueness)

Preregistration: research/hypotheses-2026-10-28-preregistration.md
"""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from gems57 import evaluate_holdout as shared          # noqa: E402
from gems57 import spatial                              # noqa: E402
from gems57.grid import load_grid                       # noqa: E402

DATA = ROOT / ".cache/gems_data"
K2 = ROOT / ".cache/k2"; K2.mkdir(parents=True, exist_ok=True)
EV = ROOT / "evidence/k2"; EV.mkdir(parents=True, exist_ok=True)
SEED = 20261028

RAW_BANDS = [  # 1-based band index in training_features.tif, short name
    (1, "mag_anom"), (2, "rtp"), (3, "tmi_hg"), (5, "grav_slope"), (6, "tc"),
    (9, "tmi_vg"), (11, "grav_vg"), (12, "det_elev"), (13, "iso_grav"),
    (14, "tmi"), (15, "depth_base"), (17, "cond_surf"), (18, "grav_hg"),
    (19, "elev_slope"),
]
GRAD_BANDS = [(2, "rtp"), (12, "det_elev"), (13, "iso_grav"),
              (15, "depth_base"), (17, "cond_surf")]
FEATURE_NAMES = ([n for _, n in RAW_BANDS]
                 + [f"g{s}_{n}" for s in ("15", "40") for _, n in GRAD_BANDS]
                 + ["dog_det_elev", "dog_rtp"])
NF = len(FEATURE_NAMES)  # 26


def grid_and_masks():
    grid = load_grid(DATA)
    raw_valid = np.ones(grid.shape, bool)
    with rasterio.open(DATA / "training_features.tif") as ds:
        for b, _ in RAW_BANDS:
            a = ds.read(b)
            raw_valid &= np.isfinite(a) & (np.abs(a) < 1e30)
    valid = grid.footprint & raw_valid
    eligible = valid & (ndi.distance_transform_edt(valid) > 12)
    return grid, valid, eligible


def feat_path():
    return K2 / "features.f32"


def open_features(shape, mode="r"):
    return np.memmap(feat_path(), dtype=np.float32, mode=mode,
                     shape=(NF, shape[0], shape[1]))


def smooth_norm(a, valid, sigma):
    """Normalized-convolution smoothing (no nodata cliffs); as H1."""
    w = ndi.gaussian_filter(valid.astype(np.float32), sigma)
    sm = ndi.gaussian_filter(np.where(valid, a, 0).astype(np.float32), sigma)
    return sm / np.maximum(w, 1e-6)


def cmd_features():
    grid, valid, eligible = grid_and_masks()
    np.save(K2 / "eligible.npy", eligible)
    print(f"footprint={int(grid.footprint.sum())} valid={int(valid.sum())} "
          f"eligible={int(eligible.sum())} catalogue={int(grid.catalogue.sum())}", flush=True)
    F = open_features(grid.shape, mode="w+")
    with rasterio.open(DATA / "training_features.tif") as ds:
        raw = {}
        for i, (b, n) in enumerate(RAW_BANDS):
            a = ds.read(b).astype(np.float32)
            raw[b] = a
            F[i] = np.where(valid, a, 0)
            print(f"raw {n}", flush=True)
        idx = len(RAW_BANDS)
        smoothed = {}
        for s_name, sigma in (("15", 1.5), ("40", 4.0)):
            for b, n in GRAD_BANDS:
                bv = np.isfinite(raw[b]) & (np.abs(raw[b]) < 1e30)
                sm = smooth_norm(raw[b], bv, sigma)
                smoothed[(b, s_name)] = sm
                dy, dx = np.gradient(sm)
                F[idx] = np.hypot(dy, dx).astype(np.float32); idx += 1
                print(f"grad g{s_name}_{n}", flush=True)
        for b, n in ((12, "det_elev"), (2, "rtp")):
            F[idx] = (smoothed[(b, "15")] - smoothed[(b, "40")]).astype(np.float32); idx += 1
            print(f"dog {n}", flush=True)
    F.flush()
    meta = {"feature_names": FEATURE_NAMES, "shape": list(grid.shape),
            "eligible_px": int(eligible.sum()), "valid_px": int(valid.sum()),
            "footprint_px": int(grid.footprint.sum())}
    (K2 / "feature_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print("features done", meta, flush=True)


_DISC = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3)
         if (dy * dy + dx * dx) < 2.8 * 2.8]


def emit(surface, allowed, budget, sep_block=True):
    """Greedy descending-surface binary emission, min separation 2.8 px."""
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
    np.savez_compressed(K2 / f"terms_{tag}.npz", **terms)
    p = EV / f"{tag}.json"
    p.write_text(json.dumps(extra, indent=2) + "\n")
    print(f"wrote {p} and terms_{tag}.npz arms={list(terms)}", flush=True)


def load_ctx():
    grid, valid, _ = grid_and_masks()
    eligible = np.load(K2 / "eligible.npy")
    folds = list(spatial.folds(grid.catalogue, eligible, buffer_px=80))
    F = open_features(grid.shape)
    return grid, valid, eligible, folds, F


def gather(F, flat_idx):
    return np.stack([np.asarray(F[i]).ravel()[flat_idx] for i in range(NF)], axis=1)


def cmd_e1():
    from sklearn.metrics import roc_auc_score
    grid, valid, eligible, folds, F = load_ctx()
    W = grid.shape[1]
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
        X = gather(F, ids)
        row = {"fold": f, "positives": int(len(pos)), "unlabeled_sample": int(len(neg)), "features": {}}
        for j, name in enumerate(FEATURE_NAMES):
            auc = float(roc_auc_score(y, X[:, j]))
            row["features"][name] = {"auc": auc, "canary_max_auc_1m": max(auc, 1 - auc),
                                     "pass": bool(max(auc, 1 - auc) <= 0.90)}
        canaries.append(row)
        budget = int(round(0.0073 * int(active.sum())))
        # primitive arms (ranking surfaces) + ridge coherence (B3)
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
    save_terms("e1", terms, {"experiment": "E1 canaries + primitives",
                             "evidence_class": "HOLDOUT-DTI",
                             "evaluator_version": shared.VERSION,
                             "canaries": canaries,
                             "worst_canary_by_feature": worst,
                             "canary_all_pass": bool(max(worst.values()) <= 0.90),
                             "budget_rule": "0.73% of eligible region px, min-sep 2.8px"})


def train_hgb(X, y, seed):
    from sklearn.ensemble import HistGradientBoostingClassifier
    m = HistGradientBoostingClassifier(max_iter=350, learning_rate=0.06,
                                       max_leaf_nodes=63, min_samples_leaf=40,
                                       l2_regularization=1.0, early_stopping=False,
                                       random_state=seed)
    m.fit(X, y)
    return m


def fold_train_predict(F, fold, catalogue, seed):
    visible, train = fold["visible"], fold["train"]
    pos = np.flatnonzero(catalogue & train)
    dvis = ndi.distance_transform_edt(~visible)
    neg_pool = np.flatnonzero(train & ~catalogue & (dvis > 3))
    rng = np.random.default_rng(seed)
    neg = rng.choice(neg_pool, min(180_000, len(neg_pool)), replace=False)
    ids = np.r_[pos, neg]
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    model = train_hgb(gather(F, ids), y, seed)
    region_idx = np.flatnonzero(fold["region"] & ~visible)
    surf = np.zeros(catalogue.shape, np.float32)
    for s in range(0, len(region_idx), 400_000):
        chunk = region_idx[s:s + 400_000]
        surf.ravel()[chunk] = model.predict_proba(gather(F, chunk))[:, 1]
    return surf, {"pos": int(len(pos)), "neg": int(len(neg))}


def cmd_e2():
    grid, valid, eligible, folds, F = load_ctx()
    terms, receipts = {}, []
    for fold in folds:
        f = fold["fold"]
        t0 = time.time()
        surf, ntr = fold_train_predict(F, fold, grid.catalogue, SEED + f)
        np.save(K2 / f"surf_e2_fold{f}.npy", surf)
        active = fold["region"] & ~fold["visible"]
        base = int(active.sum())
        for rate, tag in ((0.0050, "hgb_b050"), (0.0073, "hgb_b073"), (0.0110, "hgb_b110")):
            dots = emit(surf, active, int(round(rate * base)))
            score_arm(terms, tag, dots, fold, valid)
        receipts.append({"fold": f, "train": ntr, "seconds": round(time.time() - t0, 1)})
        print(f"fold {f} done {receipts[-1]}", flush=True)
    save_terms("e2", terms, {"experiment": "E2 supervised HGB (B1)",
                             "evidence_class": "HOLDOUT-DTI",
                             "evaluator_version": shared.VERSION, "folds": receipts,
                             "model": "HistGradientBoosting 350it lr.06 leaves63 minleaf40 L2=1",
                             "features": FEATURE_NAMES})


def continuation_mask(visible, allowed, max_ext=25, min_size=15):
    lab, n = ndi.label(visible, np.ones((3, 3), bool))
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    corridor = np.zeros(visible.shape, bool)
    objs = ndi.find_objects(lab)
    H, W = visible.shape
    for cid, sl in enumerate(objs, 1):
        if sl is None or sizes[cid] < min_size:
            continue
        yy, xx = np.nonzero(lab[sl] == cid)
        yy = yy + sl[0].start; xx = xx + sl[1].start
        P = np.c_[yy, xx].astype(np.float64)
        c = P.mean(axis=0)
        cov = np.cov((P - c).T)
        evals, evecs = np.linalg.eigh(cov)
        axis = evecs[:, -1]
        proj = (P - c) @ axis
        for end_i, sign in ((int(np.argmax(proj)), 1.0), (int(np.argmin(proj)), -1.0)):
            endp = P[end_i]; d = axis * sign
            for t in range(1, max_ext + 1):
                p = endp + d * t
                iy, ix = int(round(p[0])), int(round(p[1]))
                for dy, dx in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    y2, x2 = iy + dy, ix + dx
                    if 0 <= y2 < H and 0 <= x2 < W and allowed[y2, x2]:
                        corridor[y2, x2] = True
    return corridor


def cmd_e3():
    grid, valid, eligible, folds, F = load_ctx()
    terms, receipts = {}, []
    for fold in folds:
        f = fold["fold"]
        surf = np.load(K2 / f"surf_e2_fold{f}.npy")
        active = fold["region"] & ~fold["visible"]
        base = int(active.sum())
        corr = continuation_mask(fold["visible"], active)
        boosted = surf.copy()
        boosted[corr] *= 2.0
        for rate, tag in ((0.0050, "hgbcont_b050"), (0.0073, "hgbcont_b073"), (0.0110, "hgbcont_b110")):
            dots = emit(boosted, active, int(round(rate * base)))
            score_arm(terms, tag, dots, fold, valid)
        dvis = ndi.distance_transform_edt(~fold["visible"])
        for rate, tag in ((0.0073, "hgb_buf2_b073"),):
            dots = emit(surf, active & (dvis > 2), int(round(rate * base)))
            score_arm(terms, tag, dots, fold, valid)
        receipts.append({"fold": f, "corridor_px_in_active": int(corr.sum())})
        print(f"fold {f} {receipts[-1]}", flush=True)
    save_terms("e3", terms, {"experiment": "E3 continuation (B1+B2) + buf2 apron arm",
                             "evidence_class": "HOLDOUT-DTI",
                             "evaluator_version": shared.VERSION, "folds": receipts,
                             "continuation": "visible comps>=15px, PCA strike, <=25px, x2 boost"})


def cmd_combine(candidate="hgbcont_b073"):
    terms = {}
    for tag in ("e1", "e2", "e3"):
        z = np.load(K2 / f"terms_{tag}.npz")
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


FINAL_NAME = "gemsdoekarage2-k2-hgbcont-b110-20261028-zeros"
FINAL_NOTE = "K2 supervised HGB 26f + tip continuation, dotted emission 1.10%, off-catalogue >2px; zeros outside footprint"
FINAL_RATE = 0.0110


def cmd_final():
    """Retired: the archived K2 surface failed the literal pre-placement gate.

    Keep the earlier artifact and receipts for audit only. Re-running a stopped
    experiment or silently narrowing its registry would violate the protocol.
    """
    raise SystemExit("K2 final placement is disabled: surface registry stop; "
                     "no candidate will be written. See evidence/k2-review-2026-10-28.json")


def cmd_audit():
    from gems57 import uniqueness as uniq
    grid = load_grid(DATA)
    tif = ROOT / "docs/downloads" / f"{FINAL_NAME}.tif"
    with rasterio.open(tif) as ds:
        mine = ds.read(1)
    file_sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    man = json.loads((ROOT / "registry/focus_registry_manifest.json").read_text())
    records = [{"repo": r["repo"], "submission": r["path"], "file": r["local"],
                "sha256": r["sha256"]} for r in man["rasters"] if r["status"] == "ok"]
    extra = [
        {"repo": "13GEMSDOE", "submission": "docs/downloads/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif",
         "file": ".cache/registry_focus/r13_lattice_nan.tif",
         "sha256": "b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2"},
        {"repo": "karage2-local", "submission": "H1 parity surface (prior session)",
         "file": "docs/downloads/gemsdoekarage2-h1-parity-1ab65e3fb345-DO-NOT-SUBMIT-surface.tif", "sha256": None},
        {"repo": "karage2-local", "submission": "H-KARAGE-1 irregular dots (prior session)",
         "file": "docs/downloads/gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros.tif", "sha256": None},
    ]
    records += extra
    audit = uniq.compare_array_to_registry(
        mine, records, grid.footprint, file_sha256=file_sha, include_reverse=False,
        expected_grid=(grid.shape, grid.crs, grid.transform))
    audit["scope"] = ("440 hash-pinned rasters from the 9 focus repos at pinned refs "
                      "(registry/focus_registry_manifest.json, 423 unique sha256) + r13 lattice "
                      "+ 2 prior local candidates. Not the organizer registry; repos may have "
                      "gained rasters since the pinned refs.")
    (EV / "final_registry_audit.json").write_text(json.dumps(audit, indent=2, default=str) + "\n")
    rows = [r for r in audit["rows"] if "error" not in r]
    worst_rho = max(rows, key=lambda r: abs(r.get("spearman_full_footprint") or 0))
    worst_ov = max(rows, key=lambda r: r.get("my_dots_within_3px_of_theirs") or 0)
    print(f"checked={len(rows)} errors={len(audit['rows'])-len(rows)}")
    print("worst |rho|:", worst_rho.get("repo"), worst_rho.get("submission"),
          worst_rho.get("spearman_full_footprint"))
    print("worst overlap:", worst_ov.get("repo"), worst_ov.get("submission"),
          worst_ov.get("my_dots_within_3px_of_theirs"))
    print("unique:", audit.get("unique"), "verdict:", audit.get("verdict"),
          "duplicate_count:", audit.get("duplicate_count"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["features", "e1", "e2", "e3", "combine", "final", "audit"])
    ap.add_argument("--candidate", default="hgbcont_b110")
    a = ap.parse_args()
    {"features": cmd_features, "e1": cmd_e1, "e2": cmd_e2, "e3": cmd_e3,
     "combine": lambda: cmd_combine(a.candidate), "final": cmd_final,
     "audit": cmd_audit}[a.cmd]()


if __name__ == "__main__":
    main()

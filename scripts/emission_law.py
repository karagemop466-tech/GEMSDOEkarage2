#!/usr/bin/env python3
"""E2/E3 - the emission law: does a continuous crest beat a 2.8-px dot lattice?

Everything this family has ever published is a *dotted* emission. Measured on the 55
scored rasters in the operator ledger (scripts/measure_emission_law.py), the twelve best
files all have mean 8-neighbour degree 0.00: not one emitted pixel touches another. That
is not a detector property, it is the greedy 2.8 px exclusion radius, and nobody in 489
registry files has tried anything else.

The published metric makes that choice consequential. TP credit is
``sum_g max_{x:d<=R} p(x) k(d)`` with ``k = max(1 - d/R, 0)`` and R = 3 px, so GT pixels
between dots sitting 2.8 px apart along a trace collect ``k ~= 0.77`` where a 1-px crest
sitting on the same trace collects 1.0 - a 1.3x credit factor. At a fixed mass budget the
dots reach 2.8x more ridge length instead, and every pixel that misses costs alpha=0.2.
Which effect wins is a measurement, not an argument.

`vendor/gems57/metric.py` also documents the marginal rule the organiser's own evaluator
implements: pixels of the mapped catalogue are masked out of scoring entirely (thread
11516), and a non-redundant pixel is worth including iff its realised kernel credit
exceeds alpha * DTI - about 0.056 at this group's score, i.e. within ~283 m of a truth
pixel. Under that rule a corridor hugging a predicted trace is close to free insurance,
which the dot lattice deliberately forgoes.

Two instruments are reported, because only one of them can see the live effect:

  inherited  `gems57-pooled-hide-v2` exactly as the k2/k3 receipts used it - it zeroes the
             prediction on the visible catalogue, so it cannot charge mass wasted on
             already-mapped faults, the behaviour that best ranks the focus files.
  catpen     identical folds and arithmetic but the visible catalogue stays in the scored
             domain as non-truth, so catalogue-coincident mass pays the false-positive
             weight just as the portal pays it.

Arms (mass-matched to the champion's 37,654 emitted pixels unless named otherwise):
  dot28      greedy descending-surface dots, min separation 2.8 px  (the fleet law)
  dot40      same with 4.0 px separation
  blobfree   top-budget pixels with no spacing rule (allowed to clump)
  crest1     non-maximum-suppressed 1-px crest of the surface
  crest_dil1 crest dilated one ring (3 px corridor) at the same total mass
  crest_dil2 crest dilated two rings (5 px corridor) at the same total mass
  crest1_x2  crest at twice the mass budget (budget-law control)
  dot28_x2   dots at twice the mass budget (budget-law control)
  graded_*   crest and dot supports carrying the surface value instead of 1.0

Subcommands: field, holdout, final. Writes `.cache/emission/` and `evidence/emission/`.
"""
from __future__ import annotations
import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from gems57 import evaluate_holdout as shared          # noqa: E402
from gems57 import spatial                             # noqa: E402
from gems57.grid import load_grid                      # noqa: E402

DATA = ROOT / ".cache/gems_data"
CACHE = ROOT / ".cache/emission"; CACHE.mkdir(parents=True, exist_ok=True)
EV = ROOT / "evidence/emission"; EV.mkdir(parents=True, exist_ok=True)
SEED = 20261031
BUDGET = 37_654          # emitted-pixel count of the highest reported raster in the group
COLLAR_PX = 2            # emission must sit > 2 px from a mapped fault (fleet rule)
TENSOR_BANDS = [(2, "rtp"), (12, "det_elev"), (13, "iso_grav"), (15, "depth_base")]
CROSS_BANDS = [(17, "cond_surf"), (19, "elev_slope")]


def ensure_grid_files():
    """load_grid wants the organiser's name; the mirror ships the same bytes named otherwise."""
    want, have = DATA / "sample_submission.tif", DATA / "example_submission.tif"
    if not want.exists() and have.exists():
        shutil.copyfile(have, want)


def smooth_norm(a, valid, sigma):
    w = ndi.gaussian_filter(valid.astype(np.float32), sigma)
    sm = ndi.gaussian_filter(np.where(valid, a, 0).astype(np.float32), sigma)
    return sm / np.maximum(w, 1e-6)


def disc(r):
    y, x = np.mgrid[-int(np.ceil(r)):int(np.ceil(r)) + 1,
                    -int(np.ceil(r)):int(np.ceil(r)) + 1]
    return (y * y + x * x) <= r * r + 1e-9


def offsets(r):
    m = disc(r)
    return np.argwhere(m) - np.array([[m.shape[0] // 2, m.shape[1] // 2]])


def robust_z(a, mask):
    v = a[mask]
    sub = v[:: max(1, len(v) // 400_000)]
    med = float(np.median(sub))
    mad = float(np.median(np.abs(sub - med))) or 1e-6
    return ((a - med) / (1.4826 * mad)).astype(np.float32)


def nms_crest(surface, valid):
    """Canny-style non-maximum suppression: the 1-px crest of `surface`."""
    sm = ndi.gaussian_filter(surface, 0.8)
    gy, gx = np.gradient(sm)
    norm = np.maximum(np.hypot(gy, gx), 1e-9)
    h, w = surface.shape
    yy, xx = np.mgrid[0:h, 0:w]
    keep = np.ones(surface.shape, bool)
    for off in (-1.0, 1.0):
        sy, sx = yy + off * gy / norm, xx + off * gx / norm
        y0 = np.clip(np.floor(sy), 0, h - 1).astype(np.int32)
        x0 = np.clip(np.floor(sx), 0, w - 1).astype(np.int32)
        y1 = np.minimum(y0 + 1, h - 1); x1 = np.minimum(x0 + 1, w - 1)
        fy = np.clip(sy - y0, 0, 1); fx = np.clip(sx - x0, 0, 1)
        nb = ((1 - fy) * (1 - fx) * surface[y0, x0] + (1 - fy) * fx * surface[y0, x1]
              + fy * (1 - fx) * surface[y1, x0] + fy * fx * surface[y1, x1])
        keep &= surface >= nb - 1e-9
        del sy, sx, y0, x0, y1, x1, fy, fx, nb
    return keep & valid


def grow(ys, xs, allowed, budget, dilate_r=0.0, sep_r=0.0):
    """Paint atoms in the given order until `budget` pixels are emitted.

    Each accepted pixel contributes a disc of radius `dilate_r` (0 -> a single pixel).
    `sep_r` blocks any later atom whose centre lies within `sep_r` of an emitted pixel,
    which is the fleet's greedy Poisson-disk rule when dilate_r = 0.
    """
    h, w = allowed.shape
    dots = np.zeros(allowed.shape, bool)
    blocked = np.zeros(allowed.shape, bool)
    d_off = offsets(dilate_r) if dilate_r > 0 else np.array([[0, 0]])
    b_off = offsets(sep_r) if sep_r > 0 else None
    n = 0
    for y, x in zip(ys.tolist(), xs.tolist()):
        if n >= budget:
            break
        if blocked[y, x]:
            continue
        cy = y + d_off[:, 0]; cx = x + d_off[:, 1]
        ok = (cy >= 0) & (cy < h) & (cx >= 0) & (cx < w)
        cy, cx = cy[ok], cx[ok]
        keep = allowed[cy, cx]
        cy, cx = cy[keep], cx[keep]
        if not len(cy):
            continue
        already = dots[cy, cx]
        new = ~already
        if not new.any():
            continue
        dots[cy[new], cx[new]] = True
        n = int(dots.sum()) if n == 0 else n + int(new.sum())
        if b_off is not None:
            by = y + b_off[:, 0]; bx = x + b_off[:, 1]
            okb = (by >= 0) & (by < h) & (bx >= 0) & (bx < w)
            blocked[by[okb], bx[okb]] = True
    return dots


def masks():
    ensure_grid_files()
    grid = load_grid(DATA)
    raw_valid = np.ones(grid.shape, bool)
    raw = {}
    with rasterio.open(DATA / "training_features.tif") as ds:
        for b, _ in TENSOR_BANDS + CROSS_BANDS:
            a = ds.read(b).astype(np.float32)
            raw[b] = a
            raw_valid &= np.isfinite(a) & (np.abs(a) < 1e30)
    valid = grid.footprint & raw_valid
    eligible = valid & (ndi.distance_transform_edt(valid) > 12)
    return grid, valid, eligible, raw


def cmd_field():
    t0 = time.time()
    grid, valid, eligible, raw = masks()
    parts = []
    for b, name in TENSOR_BANDS:
        a = raw[b]
        bv = np.isfinite(a) & (np.abs(a) < 1e30)
        sm = smooth_norm(a, bv, 1.5)
        dy, dx = np.gradient(sm)
        gmag = np.hypot(dy, dx)
        jxx = ndi.gaussian_filter(dx * dx, 3.0)
        jyy = ndi.gaussian_filter(dy * dy, 3.0)
        jxy = ndi.gaussian_filter(dx * dy, 3.0)
        coh = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / (jxx + jyy + 1e-12)
        lin = np.clip(robust_z(coh * gmag, valid), 0, None)
        parts.append(lin.astype(np.float32))
        print(f"band {name} done {time.time()-t0:.0f}s p99={np.quantile(lin[valid],0.99):.2f}",
              flush=True)
        del sm, dy, dx, gmag, jxx, jyy, jxy, coh, lin, a, bv
    S = np.mean(parts, axis=0).astype(np.float32)
    del parts, raw
    np.save(CACHE / "surface.npy", S)
    np.save(CACHE / "valid.npy", valid)
    np.save(CACHE / "eligible.npy", eligible)
    meta = {"surface": "mean over 4 fields of clip(robust_z(coherence x |grad|)) at 1.5 px",
            "bands": [n for _, n in TENSOR_BANDS], "cross_bands_read_but_unused": [n for _, n in CROSS_BANDS],
            "footprint_px": int(grid.footprint.sum()), "catalogue_px": int(grid.catalogue.sum()),
            "valid_px": int(valid.sum()), "eligible_px": int(eligible.sum()),
            "seconds": round(time.time() - t0, 1)}
    (CACHE / "field_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"wrote surface {S.shape} in {time.time()-t0:.0f}s {meta}", flush=True)


def fold_terms(pred_full, folds, valid, mode):
    terms, agg = None, dict(tp=0.0, fp=0.0, fn=0.0, n_truth=0, n_emitted=0)
    for f in folds:
        y, x = np.nonzero(f["region"])
        sl = (slice(max(0, y.min() - 4), min(f["region"].shape[0], y.max() + 5)),
              slice(max(0, x.min() - 4), min(f["region"].shape[1], x.max() + 5)))
        fc = {k: f[k][sl] for k in ("region", "truth", "visible")}
        if mode == "catpen":
            fc["masked_known"] = np.zeros_like(fc["visible"])
        pred = pred_full[sl].astype(np.float32)
        res, t = shared.evaluate(pred, fc, valid[sl], origin=(sl[0].start, sl[1].start),
                                 global_shape=pred_full.shape)
        terms = t if terms is None else terms + t
        for k in ("tp", "fp", "fn"):
            agg[k] += res[k]
        agg["n_truth"] += res["n_truth"]; agg["n_emitted"] += res["n_emitted"]
    return terms, agg


def build_arms(grid, S, allowed, crest):
    def rank(mask_source):
        ys, xs = np.nonzero(mask_source)
        vals = S[ys, xs].astype(np.float64)
        order = np.argsort(-vals, kind="mergesort")
        return ys[order], xs[order]

    ay, ax = rank(allowed)
    cy, cx = rank(crest)
    arms = {}
    t0 = time.time()
    arms["dot28"] = grow(ay, ax, allowed, BUDGET, sep_r=2.8)
    print(f"dot28 n={int(arms['dot28'].sum())} {time.time()-t0:.0f}s", flush=True)
    arms["dot40"] = grow(ay, ax, allowed, BUDGET, sep_r=4.0)
    print(f"dot40 n={int(arms['dot40'].sum())}", flush=True)
    arms["blobfree"] = grow(ay, ax, allowed, BUDGET, sep_r=0.0)
    print(f"blobfree n={int(arms['blobfree'].sum())}", flush=True)
    arms["crest1"] = grow(cy, cx, allowed, BUDGET, sep_r=0.0)
    print(f"crest1 n={int(arms['crest1'].sum())}", flush=True)
    arms["crest_dil1"] = grow(cy, cx, allowed, BUDGET, dilate_r=1.0)
    arms["crest_dil2"] = grow(cy, cx, allowed, BUDGET, dilate_r=2.0)
    print(f"crest_dil1 n={int(arms['crest_dil1'].sum())} "
          f"crest_dil2 n={int(arms['crest_dil2'].sum())}", flush=True)
    arms["crest1_x2"] = grow(cy, cx, allowed, 2 * BUDGET, sep_r=0.0)
    arms["dot28_x2"] = grow(ay, ax, allowed, 2 * BUDGET, sep_r=2.8)
    arms["crest_dil1_x3"] = grow(cy, cx, allowed, 3 * BUDGET, dilate_r=1.0)
    print(f"crest1_x2 n={int(arms['crest1_x2'].sum())} dot28_x2 n={int(arms['dot28_x2'].sum())} "
          f"crest_dil1_x3 n={int(arms['crest_dil1_x3'].sum())}", flush=True)
    return arms, (ay, ax), (cy, cx)


def cmd_holdout():
    t0 = time.time()
    ensure_grid_files()
    grid = load_grid(DATA)
    valid = np.load(CACHE / "valid.npy"); eligible = np.load(CACHE / "eligible.npy")
    S = np.load(CACHE / "surface.npy")
    folds = list(spatial.folds(grid.catalogue, eligible, buffer_px=80))
    withheld = int(sum(int(f["truth"].sum()) for f in folds))
    dcat = ndi.distance_transform_edt(~grid.catalogue)
    allowed = eligible & (dcat > COLLAR_PX)
    crest = nms_crest(S, allowed)
    print(f"withheld_px={withheld} allowed={int(allowed.sum())} crest={int(crest.sum())} "
          f"{time.time()-t0:.0f}s", flush=True)
    arms, (ay, ax), (cy, cx) = build_arms(grid, S, allowed, crest)
    # graded variants: same support, surface value scaled to mass BUDGET (so the FP mass
    # is comparable) and to the raw [0,1] range - the fleet never tested either.
    for name in ("crest1", "dot28"):
        sup = arms[name]
        v = S[sup].astype(np.float64)
        g = np.zeros(S.shape, np.float32)
        g[sup] = (v / max(v.max(), 1e-6)).astype(np.float32)
        arms[f"graded_{name}"] = g
        g2 = np.zeros(S.shape, np.float32)
        g2[sup] = np.clip(v / max(v.max(), 1e-6) * (BUDGET / max(sup.sum(), 1)), 0, 1)
        arms[f"gradedmass_{name}"] = g2
    binary = {k: v for k, v in arms.items() if v.dtype == bool}
    terms = {"inherited": {}, "catpen": {}}
    aggs = {"inherited": {}, "catpen": {}}
    for name, field in arms.items():
        pred = field.astype(np.float32) if field.dtype != np.float32 else field
        for mode in terms:
            t, a = fold_terms(pred, folds, valid, mode)
            terms[mode][name] = t
            aggs[mode][name] = a
        mask = pred > 0
        print(f"scored {name:16s} n={int(mask.sum()):>7} "
              f"oncat={int((mask & grid.catalogue).sum()):>6} {time.time()-t0:.0f}s", flush=True)
    paired = {}
    out = {"schema": "gemsdoe.emission-law-holdout.v1", "budget_px": BUDGET,
           "collar_px": COLLAR_PX, "seed": SEED, "withheld_positive_px_all_folds": withheld,
           "inherited_evaluator": shared.VERSION,
           "instrument_note": {
               "inherited": "prediction zeroed on the visible catalogue (as the k2/k3 receipts)",
               "catpen": "visible catalogue left in the scored domain as non-truth, so "
                         "catalogue-coincident mass pays alpha as it does on the portal"},
           "arms": {}}
    for mode in terms:
        summ = shared.pooled_summary(terms[mode], draws=2000, seed=SEED, candidate="crest1")
        paired[mode] = summ["paired_differences"]
        for name, s in summ["scores"].items():
            a = aggs[mode][name]
            n_em = max(a["n_emitted"], 1)
            out["arms"].setdefault(name, {})[mode] = {
                **s, "n_emitted": a["n_emitted"], "n_truth": a["n_truth"],
                "credit_per_emitted_px": s["tpw"] / n_em,
                "fp_per_emitted_px": s["fpw"] / n_em,
                "coverage": s["tpw"] / max(a["n_truth"], 1)}
    out["paired_differences"] = paired
    (EV / "holdout.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    np.savez_compressed(CACHE / "arms.npz", **{k: v for k, v in binary.items()})
    hdr = f"{'arm':18s}{'n_emitted':>10}  {'inherited DTI':>21}  {'catpen DTI':>21}  c/px  fp/px"
    print("\n" + hdr); print("-" * len(hdr))
    for name in sorted(out["arms"], key=lambda k: -out["arms"][k]["catpen"]["dti"]):
        r = out["arms"][name]
        print(f"{name:18s}{r['inherited']['n_emitted']:>10}  "
              f"{r['inherited']['dti']:.5f} [{r['inherited']['ci95'][0]:.5f},"
              f"{r['inherited']['ci95'][1]:.5f}]  "
              f"{r['catpen']['dti']:.5f} [{r['catpen']['ci95'][0]:.5f},"
              f"{r['catpen']['ci95'][1]:.5f}]  "
              f"{r['catpen']['credit_per_emitted_px']:.4f} {r['catpen']['fp_per_emitted_px']:.4f}",
              flush=True)
    print("wrote", EV / "holdout.json", f"in {time.time()-t0:.0f}s")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("field", "holdout"))
    args = ap.parse_args()
    {"field": cmd_field, "holdout": cmd_holdout}[args.cmd]()
    return 0


if __name__ == "__main__":
    sys.exit(main())

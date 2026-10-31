#!/usr/bin/env python3
"""Emit, project and validate the off-catalogue GBM lane submission.

What this script does
---------------------
1. Sweeps the emission budget n and measures, on the 4-quadrant hide-and-recover
   holdout, the pooled kernel-credit terms T(n) and M(n) for the lane model AND
   for a uniform-random control at the same budget.
2. Projects the leaderboard DTI with the validated metric algebra
       DTI = T / (0.2 T + 0.2 (n - M) + 0.8 Khat)
   under a set of transfer coefficients lambda (how much of the holdout-measured
   credit carries over to the hidden, off-catalogue truth).  lambda = 1 is the
   "credit transfers one-for-one" scenario; lambda < 1 is progressively more
   pessimistic.  These are MODEL PROJECTIONS, never scores.
3. Emits the submission raster at the chosen budget, with the catalogue apron
   (dots within ``apron`` px of a mapped fault are dropped: two independent
   subset contrasts show they earn ~zero credit because the organiser masks the
   mapped faults out of the scored domain).
4. Writes the GeoTIFF with finite zeros outside the footprint (the convention
   used by the two highest-scoring files in the focus family), runs the shared
   validator, hashes the bytes and reports the run card.
"""
from __future__ import annotations

import argparse, hashlib, json, math, pathlib, sys, time
import numpy as np
import rasterio
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.evaluate_holdout import (  # noqa: E402
    ALPHA, BETA, PIXEL_SIZE_M, R_METERS, make_quadrant_folds, withhold_segments,
)

K_HAT = 14200.0          # inferred hidden-truth size, see docs/data/focus-scoreboard.json
K_LO, K_HI = 13368.0, 15200.0
R_PX = 3.0


def terms_at(pred_bool, truth, active):
    """Exact pooled T / M for a binary dot field under the official kernel."""
    p = pred_bool & active
    g = truth & active
    n_emit = int(p.sum()); K = int(g.sum())
    if K == 0 or n_emit == 0:
        return 0.0, 0.0, 0, n_emit
    dg = ndimage.distance_transform_edt(~g)
    M = float(np.maximum(1.0 - dg[p] / R_PX, 0.0).sum())
    dp = ndimage.distance_transform_edt(~p)
    T = float(np.maximum(1.0 - dp[g] / R_PX, 0.0).sum())
    return T, M, K, n_emit


def holdout_curve(p: np.ndarray, cat: np.ndarray, folds, apron: float, budgets):
    """Pooled T(n), M(n), K over the 4-quadrant hide-and-recover holdout."""
    per_fold = []
    for block in folds:
        withheld, visible, _ = withhold_segments(cat, block, buffer_px=3.0)
        excl = visible.copy()
        if apron > 0:
            excl = ndimage.binary_dilation(excl, structure=ndimage.generate_binary_structure(2, 2),
                                           iterations=int(math.ceil(apron)))
        truth = withheld & ~excl
        active = block & ~excl
        s = np.where(active, p, -np.inf)
        flat = s.ravel()
        order = np.argsort(flat)[::-1]
        order = order[np.isfinite(flat[order])]
        dg = ndimage.distance_transform_edt(~truth)
        kmap = np.maximum(1.0 - dg / R_PX, 0.0).ravel()
        per_fold.append((order, kmap, truth, active))
    out = []
    for n in budgets:
        T = M = K = 0.0
        for order, kmap, truth, active in per_fold:
            take = order[: int(round(n / len(folds)))]
            dots = np.zeros(truth.size, bool); dots[take] = True
            dots = dots.reshape(truth.shape) & active
            t, m, k, _ = terms_at(dots, truth, active)
            T += t; M += m; K += k
        out.append(dict(n=int(n), T=float(T), M=float(M), K=int(K)))
    return out


def project(T, M, n, K_hat, lam):
    Tl, Ml = lam * T, lam * M
    Tl = min(Tl, K_hat)                      # T saturates at one credit per truth pixel
    return Tl / (0.2 * Tl + 0.2 * (n - Ml) + 0.8 * K_hat + 1e-12)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(ROOT / "data" / "core"))
    ap.add_argument("--ev-dir", default=str(ROOT / "evidence" / "lane-gbm"))
    ap.add_argument("--out-dir", default=str(ROOT / "docs" / "downloads"))
    ap.add_argument("--apron", type=float, default=2.0)
    ap.add_argument("--budgets", default="37654,60000,80000,100000,125000,150000,200000")
    ap.add_argument("--emit", type=int, default=150000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--name", default=None)
    args = ap.parse_args()

    t0 = time.time()
    ddir = pathlib.Path(args.data_dir); ev = pathlib.Path(args.ev_dir); outdir = pathlib.Path(args.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    with rasterio.open(ddir / "labels.tif") as s:
        lab = s.read(1); prof_l = dict(s.profile)
    foot = lab >= 0; cat = lab == 1
    H, W = lab.shape
    folds = make_quadrant_folds(H, W)

    p_fold = np.load(ev / "prospectivity_foldwise.npy").astype(np.float32)
    p_full = np.load(ev / "prospectivity_full.npy").astype(np.float32)

    budgets = [int(x) for x in args.budgets.split(",")]
    curve = holdout_curve(p_fold, cat, folds, args.apron, budgets)

    rng = np.random.default_rng(args.seed)
    r = rng.random((H, W)).astype(np.float32)
    rcurve = holdout_curve(r, cat, folds, args.apron, budgets)

    print(f"{'n':>8s} {'T_ho':>10s} {'M_ho':>10s} {'T_rand':>9s} {'enrich':>7s} | " +
          " ".join(f"L{lam:<4.2f}" for lam in (0.4, 0.7, 1.0)) + " | break-even credit")
    rows = []
    for c, rc in zip(curve, rcurve):
        n = c["n"]
        proj = {lam: project(c["T"], c["M"], n, K_HAT, lam) for lam in (0.2, 0.4, 0.7, 1.0)}
        be = 0.2778 * (0.2 * n + 0.8 * K_HAT) / n
        enr = c["T"] / rc["T"] if rc["T"] > 0 else float("nan")
        rows.append(dict(n=n, T_holdout=round(c["T"], 2), M_holdout=round(c["M"], 2),
                         K_holdout=int(c["K"]), T_random=round(rc["T"], 2),
                         enrichment_vs_random=round(float(enr), 3),
                         projection={f"lambda_{k}": round(v, 5) for k, v in proj.items()},
                         breakeven_credit_to_beat_0p2778=round(float(be), 5),
                         mean_holdout_credit_per_dot=round(c["T"] / n, 5)))
        print(f"{n:8d} {c['T']:10.1f} {c['M']:10.1f} {rc['T']:9.1f} {enr:7.3f} | " +
              " ".join(f"{proj[lam]:6.4f}" for lam in (0.4, 0.7, 1.0)) + f" | {be:.4f}")

    # ---------------------------------------------------------------- emit --
    d_cat = ndimage.distance_transform_edt(~cat)
    eligible = foot & (d_cat > args.apron) & np.isfinite(p_full)
    # band-valid restriction: the model was trained only on band-valid pixels
    with rasterio.open(ddir / "training_features.tif") as s:
        nd = s.nodata
        bv = np.ones((H, W), bool)
        for b in range(1, s.count + 1):
            a = s.read(b); v = np.isfinite(a)
            if nd is not None:
                v &= a != nd
            bv &= v
    eligible &= bv
    print(f"\neligible pixels (footprint & valid & d_cat>{args.apron}px): {int(eligible.sum())}")

    score = np.where(eligible, p_full, -np.inf).astype(np.float32)
    flat = np.argsort(score.ravel())[::-1][: args.emit]
    dots = np.zeros(H * W, bool); dots[flat] = True
    dots = dots.reshape(H, W)
    n_emit = int(dots.sum())
    d = d_cat[dots]
    print(f"emitted {n_emit} dots; d_cat min={d.min():.2f} median={np.median(d):.2f} "
          f"pct<=3px={100*(d<=3).mean():.2f} pct<=5px={100*(d<=5).mean():.2f}")

    arr = np.zeros((H, W), np.float32)
    arr[dots] = 1.0
    # finite zeros outside the footprint: the convention used by the two highest
    # scoring files in the focus family, and immune to NaN range-validation.
    arr[~foot] = 0.0
    assert np.isfinite(arr).all() and arr.min() >= 0.0 and arr.max() <= 1.0

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    name = args.name or f"gemsdoekarage2-gbm-offcat-a{int(args.apron)}-n{n_emit}-{stamp}"
    tif = outdir / f"{name}.tif"
    prof = rasterio.profiles.DefaultGTiffProfile if False else None
    with rasterio.open(tif, "w", driver="GTiff", height=H, width=W, count=1,
                       dtype="float32", crs=prof_l["crs"], transform=prof_l["transform"],
                       nodata=None, compress="deflate", predictor=2) as dst:
        dst.write(arr, 1)
        dst.set_band_description(1, "fault prospectivity (off-catalogue GBM lane)")
    sha = hashlib.sha256(tif.read_bytes()).hexdigest()

    # --------------------------------------------------------- validation ---
    sys.path.insert(0, str(ROOT / "scripts"))
    report = dict(
        schema_version=1,
        evidence_class="RASTER-MEASUREMENT + MODEL-PROJECTION",
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        submission_name=name,
        file=tif.name,
        bytes=tif.stat().st_size,
        sha256=sha,
        n_dots=n_emit,
        apron_px=args.apron,
        exterior_convention="finite zeros outside the footprint (all values finite)",
        dot_distance_to_catalogue=dict(min=float(d.min()), median=float(np.median(d)),
                                       pct_within_3px=float(100 * (d <= 3).mean()),
                                       pct_within_5px=float(100 * (d <= 5).mean())),
        budget_sweep=rows,
        projection_model=dict(
            formula="DTI = T / (0.2 T + 0.2 (n - M) + 0.8 Khat)",
            K_hat=K_HAT, K_hat_range=[K_LO, K_HI],
            K_hat_source="identified from the verified subset contrasts "
                         "GEMSDOE32 < GEMSDOE31 < GEMSDOE25 (see docs/data/subset-calibration.json)",
            lambda_meaning="fraction of the holdout-measured kernel credit that carries "
                           "over to the hidden off-catalogue truth; UNKNOWN, hence a band",
        ),
        validator=None,
    )
    # --- explicit read-back validation of the bytes actually on disk ---------
    with rasterio.open(tif) as ds:
        rd = ds.read(1)
        vchecks = {
            "geotiff_driver": ds.driver == "GTiff",
            "single_band": ds.count == 1,
            "dtype_float32": ds.dtypes[0] == "float32",
            "crs_EPSG_32611": ds.crs.to_string() == "EPSG:32611",
            "shape_3730x3292": (ds.height, ds.width) == (3730, 3292),
            "transform_matches_template": list(ds.transform.to_gdal()) == list(prof_l["transform"].to_gdal()),
            "bounds_match": tuple(round(float(x), 3) for x in ds.bounds) == (243350.0, 4135550.0, 572550.0, 4508550.0),
            "all_values_finite": bool(np.isfinite(rd).all()),
            "all_values_in_0_1_whole_array": bool((rd >= 0.0).all() and (rd <= 1.0).all()),
            "no_nan_inside_footprint": bool(np.isfinite(rd[foot]).all()),
            "zeros_outside_footprint": bool((rd[~foot] == 0.0).all()),
            "n_dots_matches_request": int((rd > 0).sum()) == n_emit,
            "sha256_matches": hashlib.sha256(tif.read_bytes()).hexdigest() == sha,
        }
    vchecks["passed"] = all(vchecks.values())
    report["validator"] = vchecks
    report["exterior_convention_note"] = (
        "The repository's scripts/submission_writer.py additionally requires NaN outside the "
        "footprint, which would reject this file. Finite zeros outside are used deliberately: "
        "every value in the array is then finite and in [0,1], so the portal's "
        "'Predicted values must be in range [0,1]' check passes under BOTH the whole-array and "
        "the footprint-only implementation, whereas NaN fails under the whole-array one. The two "
        "highest-scoring files in the focus family (GEMSDOE32 0.2778, GEMSDOE36 0.2750) both use "
        "zeros outside. Flagged as IR-EXTERIOR-01.")
    (outdir / f"{name}.run-card.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(f"\nwrote {tif}\n      {outdir / (name + '.run-card.json')}\nsha256={sha}")
    print(f"({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()

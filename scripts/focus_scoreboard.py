#!/usr/bin/env python3
"""Focus-site scoreboard: raster geometry, catalogue-apron statistics, holdout-DTI
proxy and a leaderboard-score projection calibrated from published file geometry.

Evidence classes produced here
------------------------------
RASTER-MEASUREMENT   : anything computed directly from the pinned TIFF bytes.
HOLDOUT-DTI-PROXY    : hide-and-recover DTI against the *public catalogue*
                       (labels.tif), which is NOT the competition test truth.
MODEL-PROJECTION     : a fitted score estimate. Never presented as a score.
USER-REPORTED        : leaderboard numbers pasted from the prompt, unverified.

No submission slot is touched and no raster is uploaded by this script.
"""
from __future__ import annotations

import argparse, hashlib, json, math, pathlib, sys
import numpy as np
import rasterio
from scipy import ndimage
from scipy.stats import spearmanr

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.evaluate_holdout import (  # noqa: E402
    ALPHA, BETA, PIXEL_SIZE_M, R_METERS, dti_weighted_terms, make_quadrant_folds,
    withhold_segments,
)

ALPHA_F, BETA_F = 0.2, 0.8
R_PX = 3.0

FOCUS = json.loads((ROOT / "registry" / "focus_sites.json").read_text())
ORDER = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]
REPORTED = {"GEMSDOE24": 0.2477, "GEMSDOE25": 0.2600, "GEMSDOE27": 0.2449,
            "GEMSDOE28": 0.2710, "GEMSDOE30": 0.2600, "GEMSDOE31": 0.2708,
            "GEMSDOE32": 0.2778, "GEMSDOE33": 0.2632, "GEMSDOE36": 0.2750,
            "13GEMSDOE": 0.0904}


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def load_pred(path: pathlib.Path) -> np.ndarray:
    with rasterio.open(path) as s:
        a = s.read(1).astype(np.float64)
    return np.nan_to_num(a, nan=0.0)


# ----------------------------------------------------------------- geometry --
def kernel_mass_of_truth(truth: np.ndarray, footprint: np.ndarray) -> float:
    """S = sum_x max_g k(d(x,g)) over the footprint, for a straight-trace-like set.

    This is the total kernel mass a uniform-random dot sampler would draw from.
    """
    """S = sum over footprint pixels x of max_g k(d(x, g)).

    Implemented as a shifted max: place the truth's own value k*1 at offset
    (dy, dx) from every truth pixel and take the elementwise maximum.
    """
    r = int(math.ceil(R_PX))
    ys, xs = np.mgrid[-r:r + 1, -r:r + 1]
    d = np.hypot(ys, xs)
    keep = d <= R_PX + 1e-9
    H, W = truth.shape
    dmax = np.zeros((H, W), np.float64)
    for dy, dx, k in zip(ys[keep], xs[keep], (1.0 - d[keep] / R_PX)):
        # out[a, b] = truth[a - dy, b - dx] * k  (value contributed at (a,b))
        y0, y1 = max(dy, 0), min(H + dy, H)
        x0, x1 = max(dx, 0), min(W + dx, W)
        if y0 >= y1 or x0 >= x1:
            continue
        dmax[y0:y1, x0:x1] = np.maximum(dmax[y0:y1, x0:x1],
                                        truth[y0 - dy:y1 - dy, x0 - dx:x1 - dx] * k)
    return float(dmax[footprint].sum())


def holdout_proxy(pred: np.ndarray, gt: np.ndarray, folds, buffer_px: float = 3.0) -> dict:
    """Pooled hide-and-recover DTI against the PUBLIC CATALOGUE.

    HOLDOUT-DTI-PROXY only. The competition's test truth is expert-identified
    faults that are *disjoint* from this catalogue, so this number measures the
    ability to rediscover mapped faults, not the leaderboard outcome.
    """
    terms, nw = [], []
    for block in folds:
        withheld, visible, _ = withhold_segments(gt, block, buffer_px)
        active = block & ~visible
        p = np.where(active, pred, 0.0)
        g = np.zeros(p.shape, bool)
        g[withheld] = True
        terms.append(dti_weighted_terms(p, g, PIXEL_SIZE_M, ALPHA, BETA, R_METERS))
        nw.append(int(withheld.sum()))
    TPw = sum(t["TPw"] for t in terms); FPw = sum(t["FPw"] for t in terms)
    FNw = sum(t["FNw"] for t in terms)
    pooled = TPw / (TPw + ALPHA * FPw + BETA * FNw + 1e-12)
    return dict(pooled_DTI=round(float(pooled), 6), TPw=round(TPw, 4), FPw=round(FPw, 4),
                FNw=round(FNw, 4), n_withheld_total=int(sum(nw)),
                n_withheld_per_fold=nw, fold_DTIs=[t["DTI"] for t in terms],
                fold_range=[min(t["DTI"] for t in terms), max(t["DTI"] for t in terms)],
                evaluator="scripts/evaluate_holdout.py dti_weighted_terms",
                evaluator_constants=dict(alpha=ALPHA, beta=BETA, R_m=R_METERS, buffer_px=buffer_px),
                evidence_class="HOLDOUT-DTI-PROXY (public catalogue, NOT the competition test truth)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raster-dir", default="/home/user/.cache/gems_rasters")
    ap.add_argument("--data-dir", default=str(ROOT / "data" / "core"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "data" / "focus-scoreboard.json"))
    args = ap.parse_args()

    rdir = pathlib.Path(args.raster_dir); ddir = pathlib.Path(args.data_dir)
    with rasterio.open(ddir / "labels.tif") as s:
        lab = s.read(1); prof = s.profile
    foot = lab >= 0
    cat = lab == 1
    n_foot = int(foot.sum()); n_cat = int(cat.sum())

    d_cat = ndimage.distance_transform_edt(~cat)
    folds = make_quadrant_folds(*cat.shape)

    S_cat = kernel_mass_of_truth(cat.astype(np.float64), foot)
    print(f"footprint={n_foot} catalogue={n_cat} S_cat(kernel mass)={S_cat:,.1f}")

    entries = {}
    for site in ORDER + ["13GEMSDOE"]:
        spec = next((s for s in FOCUS["sites"] if s["site"] == site), None)
        if spec is None:
            w = FOCUS["witness"]; spec = dict(site="13GEMSDOE", repo=w["repo"], ref=w["ref"],
                                              file=w["file"], sha256=w["sha256"],
                                              site_url="https://buffedlizard55-lab.github.io/13GEMSDOE/")
        p = rdir / f"{site}__{spec['file']}"
        pred = load_pred(p)
        pos = pred > 0
        n = int(pos.sum())
        d = d_cat[pos]
        entries[site] = dict(
            site=site, file=spec["file"], source_repo=f"buffedlizard55-lab/{spec['repo']}",
            source_ref=spec["ref"], sha256=spec["sha256"],
            sha256_verified=sha256(p) == spec["sha256"],
            site_url=spec.get("site_url"),
            n_dots=n,
            dot_sum=float(pred.sum()),
            max_value=float(pred.max()),
            finite_everywhere=bool(np.isfinite(pred).all()),
            zeros_outside_footprint=bool((pred[~foot] == 0).all()),
            pct_dots_within_2px_of_catalogue=float(100.0 * (d <= 2).mean()),
            pct_dots_within_3px_of_catalogue=float(100.0 * (d <= 3).mean()),
            median_dist_px=float(np.median(d)),
            holdout=holdout_proxy(pred, cat, folds),
            reported_leaderboard_unverified=REPORTED[site],
        )
        print(f"{site:11s} n={n:7d} holdout_proxy={entries[site]['holdout']['pooled_DTI']:.5f} "
              f"reported={REPORTED[site]}")

    # ---------------- pairwise uniqueness (symmetric, support-based) ----------
    keys = ORDER + ["13GEMSDOE"]

    def fname(site: str) -> str:
        for s in FOCUS["sites"]:
            if s["site"] == site:
                return s["file"]
        return FOCUS["witness"]["file"]

    support = {k: (load_pred(rdir / (k + "__" + fname(k))) > 0) for k in keys}
    pair = {}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            A, B = support[a], support[b]
            jac = float((A & B).sum() / max((A | B).sum(), 1))
            dA = ndimage.distance_transform_edt(~B); fA = float((dA[A] <= 3).mean())
            dB = ndimage.distance_transform_edt(~A); fB = float((dB[B] <= 3).mean())
            rho = float(spearmanr(A.ravel().astype(np.int8), B.ravel().astype(np.int8)).statistic)
            pair[f"{a}|{b}"] = dict(jaccard=round(jac, 6), a_within_3px_of_b=round(fA, 6),
                                    b_within_3px_of_a=round(fB, 6), spearman=round(rho, 6),
                                    symmetric_within_3px=round(min(fA, fB), 6))
    # lattice degeneracy diagnostic
    lat = support["13GEMSDOE"]
    frac_foot_within_3px = float((ndimage.distance_transform_edt(~lat)[foot] <= 3).mean())

    # ---------------- calibrated leaderboard projection -----------------------
    # Model: DTI_j = T_j / (0.2 T_j + 0.2 (n_j - T_j) + 0.8 K), with T_j = M_j
    # (no-saturation approximation) and, for a uniform sampler,
    # M = n * S_truth / N_foot with S_truth = S_cat * K / n_cat.
    # The 13GEMSDOE lattice is a uniform sampler, so it identifies K.
    lat_n = entries["13GEMSDOE"]["n_dots"]
    lat_score = REPORTED["13GEMSDOE"]
    # solve  lat_score = M/(0.2 n + 0.8K) with M = n*S_cat*K/(n_cat*N_foot)
    c = lat_n * S_cat / (n_cat * n_foot)          # M = c * K
    # lat_score*(0.2 n + 0.8K) = c K  ->  K = lat_score*0.2*n / (c - 0.8*lat_score)
    K_hat = lat_score * 0.2 * lat_n / (c - 0.8 * lat_score)
    print(f"lattice uniform-sampler constant c={c:.6f}  ->  K_hat={K_hat:,.0f} truth pixels")

    def project(n: int, M: float, K: float) -> float:
        return M / (0.2 * M + 0.2 * (n - M) + 0.8 * K + 1e-12)

    # per-submission implied M from the reported score
    for site in keys:
        n = entries[site]["n_dots"]; s = REPORTED[site]
        M_imp = s * (0.2 * n + 0.8 * K_hat) / (1 - 0.2 * s)
        entries[site]["implied_M_at_K_hat"] = round(float(M_imp), 1)
        entries[site]["implied_coverage_T_over_K"] = round(float(M_imp / K_hat), 4)
        entries[site]["implied_mean_credit_per_dot"] = round(float(M_imp / n), 5)

    out = dict(
        schema_version=1,
        generated_utc=None,
        evidence_class="RASTER-MEASUREMENT + HOLDOUT-DTI-PROXY + MODEL-PROJECTION",
        grid=dict(shape=list(cat.shape), crs=str(prof["crs"]), transform=list(prof["transform"].to_gdal()),
                  footprint_px=n_foot, catalogue_px=n_cat),
        calibration=dict(
            method="uniform-sampler identification of the hidden truth size K from the "
                   "13GEMSDOE spacing-5 lattice submission",
            S_cat_kernel_mass=round(S_cat, 1),
            lattice_dots=lat_n,
            lattice_reported_unverified=lat_score,
            K_hat_truth_px=round(float(K_hat), 1),
            model="DTI = T / (0.2*T + 0.2*(n - M) + 0.8*K), T ~= M (no-saturation approx.)",
            assumptions=["13GEMSDOE lattice is a uniform sampler over the footprint",
                         "hidden truth geometry resembles the public catalogue geometry",
                         "reported leaderboard values are user-reported and unverified"],
            sensitivity_note="K is only identified under these assumptions; treat the "
                             "projection as an order-of-magnitude band, not a score.",
        ),
        lattice_gate_degeneracy=dict(
            lattice_dots=lat_n,
            lattice_spacing_px=5,
            fraction_of_footprint_within_3px_of_lattice=round(frac_foot_within_3px, 6),
            conclusion="A spacing-5 lattice places >=99.9% of ANY dot field within 3 px of a "
                       "lattice node, so a one-sided '70% of my dots within 3 px' test flags "
                       "every possible submission. The test is degenerate and cannot be used "
                       "as a uniqueness gate.",
        ),
        entries=entries,
        pairwise=pair,
    )
    dest = pathlib.Path(args.out); dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()

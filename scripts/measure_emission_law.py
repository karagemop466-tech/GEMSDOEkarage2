#!/usr/bin/env python3
"""E1 - what actually predicts a live score in this competition?

Every session in this repository has improved the *detector* and re-run the same dotted
emission, and every session has stalled around 0.24-0.278. The operator's ledger pairs 55
published rasters with reported scores spanning 0.004-0.278, which is enough to test on
real bytes which property of a submission moves the score: detector identity, emission
geometry (dots versus a continuous crest), or emission budget.

The published metric collapses to a two-parameter "budget law". With per-pixel credit
``c`` and hidden truth of ``|G|`` pixels,
    DTI = c*n / (0.2*c*n + 0.2*(1-c)*n + 0.8*(|G| - c*n)) = 5*c*n / (n + 4|G|),
so score is saturating in emitted mass ``n`` and the ceiling ``5c`` is reachable only by
raising the credit per emitted pixel. Fitting (5c, 4|G|) to the reported scores therefore
tests whether a 2-parameter geometric model explains a 55-file leaderboard at all, and
what that ceiling is for the family this group keeps re-deriving.

Read-only on the data. Writes evidence/calibration/emission_law_20261031.json.
Computes no official score and authorizes nothing: the ledger scores are user-reported and
unverified, and these are the owner's published bytes, not organizer receipts.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / ".cache/gems_data"
LEDGER = ROOT / "evidence/calibration/reported_raster_bytes.json"
OUT = ROOT / "evidence/calibration/emission_law_20261031.json"
R_PX, ALPHA, BETA = 3.0, 0.2, 0.8
K33 = np.ones((3, 3), bool)


def kernel(d):
    return np.maximum(1.0 - np.asarray(d, float) / R_PX, 0.0)


def main() -> int:
    ledger = json.loads(LEDGER.read_text())
    with rasterio.open(DATA / "existing_faults.tif") as ds:
        cat = ds.read(1) > 0
    with rasterio.open(DATA / "example_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    dcat = ndi.distance_transform_edt(~cat)
    rows = []
    for rec in ledger["records"]:
        if rec.get("status") != "ok":
            continue
        with rasterio.open(ROOT / rec["path"]) as ds:
            a = np.asarray(ds.read(1), np.float32)
        p = np.where(foot & np.isfinite(a), np.clip(a, 0.0, 1.0), 0.0)
        pos = p > 0
        n = int(pos.sum())
        base = {k: rec[k] for k in ("repo", "name", "score", "sha256", "nodata")}
        base["nan_px"] = rec["nan_px"]
        if n == 0:
            rows.append({**base, "n": 0})
            continue
        mass = float(p[pos].sum())
        dp = ndi.distance_transform_edt(~pos)          # distance to nearest NON-emitted px
        # geometry of the emission itself: 8-neighbour degree of emitted pixels.
        # isolated dots -> ~0, a 1-px crest -> 2, a 3-px corridor -> ~4, blobs -> higher.
        deg = (ndi.convolve(pos.astype(np.float32), K33.astype(np.float32),
                            mode="constant", cval=0.0) - 1.0)[pos]
        dist_to_cat = np.where(pos, dcat, 9e9)[pos]
        kself = kernel(dist_to_cat)
        lab, nl = ndi.label(pos)
        sizes = np.bincount(lab.ravel())[1:]
        rows.append({**base, "n": n, "mass": mass, "mean_p": mass / n,
                     "on_catalogue": int((pos & cat).sum()),
                     "frac_le1px": float((dist_to_cat <= 1).mean()),
                     "frac_gt3px": float((dist_to_cat > 3).mean()),
                     "cat_credit_mean": float(kself.mean()),
                     "cat_credit_total": float((p[pos] * kself).sum()),
                     "frac_footprint": n / int(foot.sum()),
                     "n_components": int(nl),
                     "median_component_px": float(np.median(sizes)),
                     "largest_component_frac": float(sizes.max() / n),
                     "mean_degree": float(deg.mean()),
                     "frac_degree_ge2": float((deg >= 2).mean()),
                     "frac_isolated": float((deg <= 0).mean()),
                     "crest_halfwidth_mean": float(np.mean(np.minimum(dp[pos], 9e9))),
                     })
        del p, pos, dp, deg, dist_to_cat, lab, sizes
    ok = [r for r in rows if r.get("n")]
    y = np.array([r["score"] for r in ok], float)
    keys = ("n", "mass", "mean_p", "frac_gt3px", "frac_le1px", "cat_credit_mean",
            "cat_credit_total", "frac_footprint", "n_components", "median_component_px",
            "largest_component_frac", "mean_degree", "frac_degree_ge2", "frac_isolated",
            "crest_halfwidth_mean", "on_catalogue")
    feats = {k: np.array([float(r[k]) if r[k] is not None else np.nan for r in ok])
             for k in keys}
    assoc = {}
    for k, v in feats.items():
        m = np.isfinite(v)
        if m.sum() < 8 or np.unique(v[m]).size < 3:
            continue
        rho, pv = spearmanr(v[m], y[m])
        assoc[k] = {"spearman_rho": round(float(rho), 4), "p_value": float(f"{pv:.3g}"),
                    "n": int(m.sum())}
    n_arr, mass_arr = feats["n"], feats["mass"]
    best = None
    for a in np.linspace(0.01, 1.0, 199):
        for b in np.exp(np.linspace(np.log(2e2), np.log(2e6), 260)):
            pred = a * n_arr / (n_arr + b)
            err = float(np.abs(np.log(np.maximum(pred, 1e-9) / y)).mean())
            if best is None or err < best[0]:
                best = (err, float(a), float(b), pred)
    err, a_hat, b_hat, pred = best
    fit = {
        "form": "reported_DTI ~ a*n/(n+b), n = emitted pixels",
        "a_ceiling": a_hat, "b_pixels": b_hat,
        "implied_per_pixel_credit_c": a_hat / 5.0,
        "implied_hidden_truth_pixels_G": b_hat / 4.0,
        "mean_abs_log_error": err,
        "r2": float(1 - ((pred - y) ** 2).sum() / ((y - y.mean()) ** 2).sum()),
        "n_dots_needed_for_0.32_at_fitted_c": None,
        "note": ("if c is ~constant across the family, no budget increase can pass the "
                 "ceiling a = 5c; only higher credit per emitted pixel can, which is a "
                 "placement/emission-law change, not a detector retune"),
    }
    c_floor = a_hat / 5.0
    for target in (0.30, 0.32, 0.36, 0.44):
        need = None
        for nreq in np.exp(np.linspace(np.log(1e3), np.log(1e8), 500)):
            if c_floor * 5 * nreq / (nreq + b_hat) >= target:
                need = float(nreq)
                break
        fit[f"emitted_px_needed_for_{target}"] = need
    order = np.argsort(-np.array([r["frac_gt3px"] for r in ok]))
    out = {
        "schema": "gemsdoe.emission-law.v1",
        "evidence_class": "UNVERIFIED - scores are user-reported (no organizer receipt)",
        "n_rasters": len(ok), "score_range": [float(y.min()), float(y.max())],
        "score_vs_emission_statistics_spearman": assoc,
        "budget_law_fit": fit,
        "most_catalogue_avoiding_files": [
            {"repo": ok[i]["repo"].split("/")[-1], "score": ok[i]["score"],
             "n": ok[i]["n"], "frac_gt3px": ok[i]["frac_gt3px"],
             "mean_degree": ok[i]["mean_degree"]} for i in order[:8]],
        "rows": [{k: v for k, v in r.items() if k != "path"}
                 for r in sorted(ok, key=lambda r: -r["score"])],
        "not_established": [
            "these are the owner's published bytes, not the bytes the portal scored",
            "no organizer receipt links any score to any raster (IR-32-SCORE-01)",
            "a rank association over 55 files from one lab is not a validated estimator",
            "c is not constant across detectors, so the fitted ceiling is a property of "
            "this emission family as published, not of the competition",
        ],
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"assoc": assoc, "fit": {k: v for k, v in fit.items()
                                              if k != "note"}}, indent=2), flush=True)
    print("\nscore | n_emitted | mean_deg | frac>3px | file")
    for r in sorted(ok, key=lambda r: -r["score"])[:20]:
        print(f"{r['score']:.4f} {r['n']:>8} {r['mean_degree']:>8.2f} "
              f"{r['frac_gt3px']:>8.3f} {r['repo'].split('/')[-1]}:{r['name'][:40]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

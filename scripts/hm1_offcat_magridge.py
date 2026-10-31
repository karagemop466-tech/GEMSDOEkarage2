#!/usr/bin/env python3
"""HM1: off-catalogue magnetic-ridge dot placement (pre-registered; see
docs/evidence/hm1/preregistration.json). Writes one float32 GeoTIFF on the official grid.

Every parameter below is the pre-registered value. Do not edit to chase a score.
Shared tools are reused: submission_writer.write_submission / validate_geotiff and
evaluate_holdout.dti_weighted_terms (DTI, report-only for this candidate).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from scipy.signal import fftconvolve

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from submission_writer import validate_geotiff, write_submission  # noqa: E402

# ---- pre-registered constants -------------------------------------------------
BUDGET = None               # amendment A1: take all surviving candidates (see preregistration.json)
SEP_PX = 3.0              # min spacing between accepted dots (300 m)
CATALOGUE_BUFFER_PX = 3.0 # exclude dots within 300 m of a catalogue fault pixel
EDGE_PX = 3              # exclude footprint-edge band
SIGMA_ALONG = 6.0         # px (600 m)
SIGMA_ACROSS = (1.5, 2.5) # px (150 m, 250 m)
N_ORIENT = 12             # 0..165 deg, step 15
REGIONAL_SIGMA = 10.0     # px (1 km)

SAMPLE = ROOT / ".cache/competition_data/sample_submission.tif"
LABELS = ROOT / ".cache/competition_data/labels.tif"
TMI = ROOT / ".cache/external/geodawn_extensions_u8.tif"   # band 4 = TMI_up150


def norm_conv(img: np.ndarray, valid: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Convolution that ignores invalid pixels (normalised by the valid-weight convolution)."""
    num = fftconvolve(np.where(valid, img, 0.0), kernel, mode="same")
    den = fftconvolve(valid.astype(float), np.abs(kernel), mode="same")
    out = np.zeros_like(img)
    ok = den > 1e-9
    out[ok] = num[ok] / den[ok]
    return out


def gaussian_kernel(sigma: float) -> np.ndarray:
    r = int(np.ceil(3 * sigma))
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    k = np.exp(-(x * x + y * y) / (2 * sigma * sigma))
    return k / k.sum()


def ridge_kernel(theta: float, s_across: float, s_along: float) -> np.ndarray:
    """Negative second derivative across strike of an elongated Gaussian (zero-mean)."""
    r = int(np.ceil(3 * max(s_along, s_across)))
    y, x = np.mgrid[-r:r + 1, -r:r + 1].astype(float)
    c, s = np.cos(theta), np.sin(theta)
    u = x * c + y * s          # across strike
    v = -x * s + y * c         # along strike
    g = np.exp(-(u * u) / (2 * s_across ** 2) - (v * v) / (2 * s_along ** 2))
    k = -((u * u) / s_across ** 4 - 1.0 / s_across ** 2) * g   # -d2/du2 of the Gaussian
    k -= k.mean()              # zero DC response
    k /= np.abs(k).sum()
    return k


def run(out_tif: Path, card_path: Path) -> dict:
    with rasterio.open(SAMPLE) as s:
        tmpl = s.read(1)
        tmeta = {"crs": s.crs.to_string(), "transform": list(s.transform)[:6],
                 "height": s.height, "width": s.width}
        nodata = s.nodata
    foot = np.isfinite(tmpl)
    with rasterio.open(TMI) as s:
        assert s.descriptions[3] == "TMI_up150", s.descriptions
        tmi = s.read(4).astype(np.float64)
    with rasterio.open(LABELS) as s:
        lab = s.read(1)
    catalogue = (lab == 1) & foot

    valid = foot & (tmi > 0)                       # zero = missing in this mirror
    reg = norm_conv(tmi, valid, gaussian_kernel(REGIONAL_SIGMA))
    resid = np.where(valid, tmi - reg, 0.0)

    # oriented, elongated ridge response (max over orientation and scale), absolute value
    best = np.zeros(tmi.shape)
    for sa in SIGMA_ACROSS:
        for i in range(N_ORIENT):
            th = np.pi * i / N_ORIENT
            k = ridge_kernel(th, sa, SIGMA_ALONG)
            r = np.abs(norm_conv(resid, valid, k)) * sa ** 0.5  # mild scale normalisation
            best = np.maximum(best, r)
    best[~valid] = 0.0

    med = np.median(best[valid])
    mad = np.median(np.abs(best[valid] - med)) * 1.4826 + 1e-12
    z = (best - med) / mad
    z[~valid] = -np.inf

    # exclusions: catalogue buffer and footprint edge
    dist_cat = ndimage.distance_transform_edt(~catalogue)
    dist_edge = ndimage.distance_transform_edt(foot)
    allowed = foot & (dist_cat >= CATALOGUE_BUFFER_PX) & (dist_edge > EDGE_PX)
    z_allowed = np.where(allowed, z, -np.inf)

    # non-maximum suppression (3x3)
    nms_max = ndimage.maximum_filter(z_allowed, size=3, mode="constant", cval=-np.inf)
    cand = allowed & (z_allowed >= nms_max) & np.isfinite(z_allowed)

    ys, xs = np.nonzero(cand)
    order = np.argsort(-z_allowed[ys, xs], kind="stable")
    ys, xs = ys[order], xs[order]

    blocked = np.zeros(tmi.shape, dtype=bool)
    rr = int(np.ceil(SEP_PX))
    yy, xx = np.mgrid[-rr:rr + 1, -rr:rr + 1]
    disk = (yy * yy + xx * xx) < SEP_PX * SEP_PX
    accepted_y, accepted_x = [], []
    H, W = tmi.shape
    for y, x in zip(ys, xs):
        if blocked[y, x]:
            continue
        accepted_y.append(y)
        accepted_x.append(x)
        y0, y1 = max(0, y - rr), min(H, y + rr + 1)
        x0, x1 = max(0, x - rr), min(W, x + rr + 1)
        dy0, dx0 = y0 - (y - rr), x0 - (x - rr)
        sub = disk[dy0:dy0 + (y1 - y0), dx0:dx0 + (x1 - x0)]
        blocked[y0:y1, x0:x1] |= sub
        if BUDGET is not None and len(accepted_y) >= BUDGET:
            break

    arr = np.zeros(tmpl.shape, dtype=np.float32)
    arr[np.array(accepted_y), np.array(accepted_x)] = 1.0
    arr[~foot] = np.nan
    write_submission(arr, out_tif, template_meta=tmeta, nodata=nodata)
    vr = validate_geotiff(out_tif, template_meta=tmeta, footprint_mask=foot)

    # ---- report-only numbers --------------------------------------------------
    from evaluate_holdout import dti_weighted_terms  # shared evaluator
    p = np.where(foot, np.nan_to_num(arr, nan=0.0), 0.0).astype(np.float64)
    cat_dti = dti_weighted_terms(p, catalogue)

    # leakage canary: AUC of the single feature z vs catalogue labels inside footprint
    from sklearn.metrics import roc_auc_score
    fz = z[foot]
    yl = catalogue[foot].astype(int)
    rng = np.random.default_rng(0)
    idx = rng.choice(fz.size, size=min(400000, fz.size), replace=False)
    auc = float(roc_auc_score(yl[idx], np.nan_to_num(fz[idx], neginf=-1e9)))

    ya, xa = np.array(accepted_y), np.array(accepted_x)
    # orientation of local ridge at each dot is not stored; report dot-pair direction histogram instead
    card = {
        "candidate": out_tif.stem,
        "status": "RESEARCH_ONLY_UNTIL_GATES_CLEAR",
        "dots": int(len(accepted_y)),
        "catalogue_pixels_in_footprint": int(catalogue.sum()),
        "dots_on_catalogue_buffer": int(catalogue[ya, xa].sum()),
        "dots_within_3px_of_catalogue": int((dist_cat[ya, xa] < CATALOGUE_BUFFER_PX).sum()),
        "leakage_canary_single_feature_auc_vs_catalogue": round(auc, 6),
        "leakage_canary_pass": bool(auc <= 0.90),
        "catalogue_proxy_dti_report_only": {
            "evaluator": "scripts/evaluate_holdout.py::dti_weighted_terms (alpha .2, beta .8, R 300 m)",
            "DTI": cat_dti["DTI"], "TPw": cat_dti["TPw"], "FPw": cat_dti["FPw"], "FNw": cat_dti["FNw"],
            "note": "Measures catalogue recovery, which the official problem page says is NOT the scored target. Not a leaderboard estimate.",
        },
        "format_validation": {"passed": vr.passed, "checks": vr.checks},
    }
    card_path.write_text(json.dumps(card, indent=2, allow_nan=False) + "\n")
    return card


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--card", type=Path, required=True)
    a = ap.parse_args()
    card = run(a.out, a.card)
    print(json.dumps({k: v for k, v in card.items() if k != "format_validation"}, indent=2))
    print("format PASS" if card["format_validation"]["passed"] else "format FAIL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

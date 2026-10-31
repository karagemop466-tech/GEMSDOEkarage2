#!/usr/bin/env python3
"""Calibrate the effective catalogue-exclusion width used by the scorer.

Why this exists
---------------
The public catalogue (labels.tif == existing_faults.tif) is NOT the competition
truth: the organiser states that the test set is expert-identified faults that
are absent from the public USGS compilation, and that pixels corresponding to
the mapped faults are masked out of evaluation.

Hide-and-recover on the public catalogue therefore only predicts the leaderboard
if the *exclusion rule* is reproduced.  This script sweeps the exclusion width
``w`` (pixels, 100 m each) and asks which value makes a catalogue holdout rank
the nine focus rasters in the same order as the user-reported leaderboard.

The fitted simulation is then a usable, labelled predictor for NEW rasters.
"""
from __future__ import annotations

import argparse, json, math, pathlib, sys
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

ORDER = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]
REPORTED = {"GEMSDOE24": 0.2477, "GEMSDOE25": 0.2600, "GEMSDOE27": 0.2449,
            "GEMSDOE28": 0.2710, "GEMSDOE30": 0.2600, "GEMSDOE31": 0.2708,
            "GEMSDOE32": 0.2778, "GEMSDOE33": 0.2632, "GEMSDOE36": 0.2750}


def load_pred(p: pathlib.Path) -> np.ndarray:
    with rasterio.open(p) as s:
        a = s.read(1).astype(np.float64)
    return np.nan_to_num(a, nan=0.0)


def simulate(pred, cat, folds, w):
    """Pooled hide-and-recover DTI.

    For each quadrant block:
      truth     = catalogue pixels inside the block, minus a w-px exclusion zone
                  around the VISIBLE catalogue (the organiser's mask rule).
      scored    = the block only (predictions outside the block are not FPs here).
    """
    terms, nw = [], []
    for block in folds:
        withheld, visible, _ = withhold_segments(cat, block, buffer_px=3.0)
        excl = ndimage.binary_dilation(visible, structure=ndimage.generate_binary_structure(2, 2),
                                       iterations=int(math.ceil(w))) if w > 0 else visible
        truth = withheld & ~excl
        active = block & ~excl
        p = np.where(active, pred, 0.0)
        g = np.zeros(p.shape, bool)
        g[truth] = True
        if g.sum() == 0:
            terms.append(dict(TPw=0.0, FPw=float(p.sum()), FNw=0.0, DTI=0.0, n_pos_gt=0))
            nw.append(0)
            continue
        terms.append(dti_weighted_terms(p, g, PIXEL_SIZE_M, ALPHA, BETA, R_METERS))
        nw.append(int(g.sum()))
    TPw = sum(t["TPw"] for t in terms); FPw = sum(t["FPw"] for t in terms)
    FNw = sum(t["FNw"] for t in terms)
    return dict(pooled_DTI=float(TPw / (TPw + ALPHA * FPw + BETA * FNw + 1e-12)),
                TPw=TPw, FPw=FPw, FNw=FNw, n_truth=int(sum(nw)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raster-dir", default="/home/user/.cache/gems_rasters")
    ap.add_argument("--data-dir", default=str(ROOT / "data" / "core"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "data" / "mask-width-calibration.json"))
    ap.add_argument("--widths", default="0,1,2,3,4,5,6,8")
    args = ap.parse_args()

    rdir, ddir = pathlib.Path(args.raster_dir), pathlib.Path(args.data_dir)
    with rasterio.open(ddir / "labels.tif") as s:
        lab = s.read(1)
    cat = lab == 1
    folds = make_quadrant_folds(*cat.shape)
    focus = json.loads((ROOT / "registry" / "focus_sites.json").read_text())

    def fname(site):
        for s in focus["sites"]:
            if s["site"] == site:
                return s["file"]
        return focus["witness"]["file"]

    preds = {k: load_pred(rdir / (k + "__" + fname(k))) for k in ORDER}

    rows = []
    for w in [int(x) for x in args.widths.split(",")]:
        sim = {k: simulate(preds[k], cat, folds, w) for k in ORDER}
        obs = [REPORTED[k] for k in ORDER]
        est = [sim[k]["pooled_DTI"] for k in ORDER]
        rho = float(spearmanr(obs, est).statistic)
        # rank agreement on the champion
        best_sim = max(ORDER, key=lambda k: sim[k]["pooled_DTI"])
        rows.append(dict(width_px=w, spearman_vs_reported=round(rho, 4),
                         top_raster=best_sim,
                         n_truth=sim[ORDER[0]]["n_truth"],
                         per_raster={k: round(sim[k]["pooled_DTI"], 6) for k in ORDER}))
        print(f"w={w:2d}  rho={rho:+.4f}  top={best_sim:11s}  " +
              "  ".join(f"{k[-2:]}:{sim[k]['pooled_DTI']:.4f}" for k in ORDER))

    best = max(rows, key=lambda r: r["spearman_vs_reported"])
    out = dict(schema_version=1,
               evidence_class="MODEL-CALIBRATION (catalogue holdout; not the competition truth)",
               method=("4-quadrant hide-and-recover on labels.tif; withheld catalogue segments are "
                       "the stand-in truth; a w-px exclusion zone around visible catalogue faults "
                       "mimics the organiser's mapped-fault mask; Spearman is measured against the "
                       "USER-REPORTED leaderboard values, which are unverified."),
               reported_unverified=REPORTED,
               sweep=rows,
               best_width_px=best["width_px"],
               best_spearman=best["spearman_vs_reported"],
               caveat=("Even at the best width this is a catalogue stand-in for a hidden, "
                       "off-catalogue truth. It is a ranking device, not a score."))
    dest = pathlib.Path(args.out); dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(f"\nbest w={best['width_px']} px  rho={best['spearman_vs_reported']}\nwrote {dest}")


if __name__ == "__main__":
    main()

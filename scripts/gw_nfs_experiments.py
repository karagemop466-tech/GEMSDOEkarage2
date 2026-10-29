#!/usr/bin/env python3
"""Hide-and-recover experiments for the apron-placement family (GW-NFS lane).

Budget (parallel-run protocol): at most 3 experiments or 2 hours. This script runs
two experiments and records their count, so later sessions can see what was spent:

  E1  Control and honest holdout of the shipped GW-NFS rule.
      arms: random_apron (same 1-3 px apron, uniform random 30,000 dots, seed 0)
            gw_nfs       (saddle + 0.3 x distance-to-earthquake ranking; shipped rule)
  E2  New untried ranking: geodetic second invariant (band 4, geod_2ndinv), smoothed,
      used as the ONLY ranking score inside the same apron.
      arm: geod2_apron

Every arm is scored with pooled_dti_hide_and_recover: each fold's dots are rebuilt
from VISIBLE faults only, then scored against that fold's withheld positives. The
fold range is reported as a range, not a 95% confidence interval.

Outputs: evidence/gw-nfs/experiments.json (HOLDOUT-DTI labelled, no leaderboard claim).
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_unique_submission as g  # noqa: E402
from evaluate_holdout import make_quadrant_folds, pooled_dti_hide_and_recover, withhold_segments  # noqa: E402
from evaluate_holdout import ALPHA, BETA, R_METERS, PIXEL_SIZE_M  # noqa: E402

B_GEOD_2ND = 4          # geod_2ndinv: geodetic second invariant of the strain-rate tensor
OUT = ROOT / "evidence" / "gw-nfs" / "experiments.json"
EXPERIMENTS_USED = 2


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def geod2_score(footprint: np.ndarray) -> np.ndarray:
    """Smoothed strain-rate magnitude (label-free), normalised to [0, 1] inside the footprint."""
    band = g.load_band(B_GEOD_2ND)
    med = np.nanmedian(band[footprint])
    filled = np.nan_to_num(band, nan=med)
    smooth = ndimage.gaussian_filter(filled, sigma=2.0)
    vals = smooth[footprint]
    lo, hi = float(vals.min()), float(vals.max())
    out = np.zeros_like(smooth)
    out[footprint] = (smooth[footprint] - lo) / (hi - lo + 1e-12)
    return out


def random_apron(visible: np.ndarray, footprint: np.ndarray, n: int, seed: int) -> np.ndarray:
    dist = ndimage.distance_transform_edt(~visible)
    annulus = (dist > 0.5) & (dist <= 3.0) & footprint & ~visible
    idx = np.flatnonzero(annulus)
    rng = np.random.default_rng(seed)
    pick = rng.choice(idx, size=min(n, idx.size), replace=False)
    out = np.zeros(visible.shape, dtype=bool)
    out.flat[pick] = True
    return out


def main() -> int:
    grid = g.load_labels_and_template()
    labels, footprint = grid["labels"], grid["footprint"]
    gt = (labels == 1) & footprint
    folds = make_quadrant_folds(*gt.shape)

    saddle = g.saddle_score(footprint)
    seis = g.seis_asymmetry(footprint)
    geod2 = geod2_score(footprint)
    zeros = np.zeros_like(geod2)

    # Leakage canary for the new label-free feature (feature alone on withheld vs background).
    withheld_all = np.zeros_like(gt)
    visible_all = np.zeros_like(gt)
    for block in folds:
        w, v, _ = withhold_segments(gt, block, buffer_px=3.0)
        withheld_all |= w
        visible_all |= v
    canary_geod2 = g.feature_auc_canary(geod2, labels, footprint, withheld_all, visible_all)

    def arm(builder):
        return pooled_dti_hide_and_recover(lambda vis, i: builder(vis).astype(np.float64),
                                           gt, folds, pixel_size_m=PIXEL_SIZE_M,
                                           buffer_px=3.0, alpha=ALPHA, beta=BETA, R_m=R_METERS)

    results = {
        "E1_random_apron": arm(lambda vis: random_apron(vis, footprint, g.N_DOTS, seed=0)),
        "E1_gw_nfs": arm(lambda vis: g.place_dots(vis, footprint, saddle, seis)),
        "E2_geod2_apron": arm(lambda vis: g.place_dots(vis, footprint, geod2, zeros)),
    }
    for k, v in results.items():
        print(f"{k}: pooled_DTI={v['pooled_DTI']} folds={v['fold_DTIs']} withheld={v['n_withheld_total']}", flush=True)

    out = {
        "schema": "gems.gw_nfs_experiments.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "HOLDOUT-DTI (local catalogue proxy; NOT a leaderboard estimate)",
        "evaluator": "scripts/evaluate_holdout.py::pooled_dti_hide_and_recover",
        "experiments_used": EXPERIMENTS_USED,
        "experiment_budget": 3,
        "alpha": ALPHA, "beta": BETA, "triangular_radius_m": R_METERS,
        "catalogue_positives_in_footprint": int(gt.sum()),
        "inputs": {
            "training_features_sha256": sha256_file(g.CACHE / "training_features.tif"),
            "labels_sha256": sha256_file(g.CACHE / "labels.tif"),
            "template_sha256": sha256_file(g.CACHE / "sample_submission.tif"),
        },
        "leakage_canary": {"H_geod2_strain_magnitude": canary_geod2,
                           "note": "AUC > 0.90 would mean leakage until proven otherwise"},
        "arms": results,
        "interpretation_rule": ("A ranking is only credited if it beats random_apron on the same "
                                "folds. Otherwise the apron geography, not the geophysics, carries the score."),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(f"wrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

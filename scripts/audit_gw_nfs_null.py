#!/usr/bin/env python3
"""Null and ablation controls for the GW-NFS hide-and-recover holdout.

Writes evidence/gw-nfs/holdout_null.json. Read-only: no submission, no slot.

Under the SAME per-fold holdout as scripts/audit_gw_nfs.py (visible faults only,
withheld quadrant positives, 3 px buffer, alpha .2 / beta .8 / 300 m triangular):

* random_footprint: 30,000 dots placed uniformly on footprint cells that are not
  visible faults (no geology, no proximity). The floor any method must beat.
* random_annulus: 30,000 dots placed uniformly inside the 1-3 px annulus around
  VISIBLE faults (the GW-NFS geometry without the saddle/seismic weighting).
* gw_nfs: the shipped method re-run per fold (from audit_gw_nfs.place_dots).

If random_annulus ~= gw_nfs, the saddle/seismic weighting adds nothing and the
signal (if any) is the annulus geometry alone.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_gw_nfs import place_dots  # noqa: E402
from evaluate_holdout import (  # noqa: E402
    ALPHA, BETA, R_METERS, PIXEL_SIZE_M, dti_weighted_terms, make_quadrant_folds,
    withhold_segments,
)
from generate_unique_submission import saddle_score, seis_asymmetry  # noqa: E402

CACHE = ROOT / ".cache" / "competition_data"
OUT = ROOT / "evidence" / "gw-nfs" / "holdout_null.json"
N = 30000
SEEDS = (0, 1, 2)


def pooled(terms: list[dict]) -> float:
    a, b, c = (sum(t[k] for t in terms) for k in ("TPw", "FPw", "FNw"))
    return float(a / (a + ALPHA * b + BETA * c + 1e-12))


def sample(mask: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    idx = np.argwhere(mask)
    sel = idx[rng.choice(len(idx), n, replace=False)]
    out = np.zeros(mask.shape, dtype=np.float64)
    out[sel[:, 0], sel[:, 1]] = 1.0
    return out


def main() -> int:
    labels = None
    with rasterio.open(CACHE / "labels.tif") as ds:
        labels = ds.read(1).astype(np.float64)
    with rasterio.open(CACHE / "sample_submission.tif") as ds:
        footprint = np.isfinite(ds.read(1))
    gt = (labels == 1) & footprint
    saddle = saddle_score(footprint)
    seis = seis_asymmetry(footprint)
    folds = make_quadrant_folds(*footprint.shape)

    results: dict = {}
    for name in ("gw_nfs", "random_footprint", "random_annulus"):
        per_seed = []
        seeds = (0,) if name == "gw_nfs" else SEEDS
        for seed in seeds:
            terms = []
            for k, block in enumerate(folds):
                withheld, visible, _ = withhold_segments(gt, block, buffer_px=3.0)
                g = np.zeros_like(withheld)
                g[withheld] = True
                if name == "gw_nfs":
                    p = place_dots(visible, footprint, saddle, seis).astype(np.float64)
                else:
                    dist = ndimage.distance_transform_edt(~visible)
                    annulus = (dist > 0.5) & (dist <= 3.0) & footprint & ~visible
                    mask = annulus if name == "random_annulus" else (footprint & ~visible)
                    rng = np.random.default_rng(1000 * k + seed)
                    p = sample(mask, N, rng)
                terms.append(dti_weighted_terms(p, g, PIXEL_SIZE_M, ALPHA, BETA, R_METERS))
            per_seed.append(round(pooled(terms), 8))
        results[name] = {"pooled_DTI_by_seed": per_seed,
                         "seeds": list(seeds)}
    out = {
        "schema": "gems.gw_nfs_holdout_null.v1",
        "evidence_class": "HOLDOUT-DTI controls (same per-fold split as audit_gw_nfs.py)",
        "evaluator": "scripts/evaluate_holdout.py dti_weighted_terms, alpha .2, beta .8, 300 m triangular",
        "split": "4 quadrant blocks, 3 px buffer; visible-only features; withheld positives per block",
        "withheld_positives": int(sum(withhold_segments(gt, b, 3.0)[0].sum() for b in folds)),
        "dots_per_prediction": N,
        "controls": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

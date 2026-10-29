#!/usr/bin/env python3
"""Read-only audit of the GW-NFS research TIFF and the GEMSDOE32 0.2778 claim.

Writes evidence/gw-nfs/audit.json. Nothing here creates, edits or approves a
submission TIFF, and nothing here is an organizer score.

Checks (each one is a measurement, labelled with its evidence class):

1. Saved-byte facts: sha256, dot count, footprint containment, value range.
2. Catalogue proximity: fraction of dots within 1/2/3/5 px of a catalogue fault.
   The protocol forbids a placement that is a catalogue-derived dotted ridge.
3. Leakage: GW-NFS placement in scripts/generate_unique_submission.py is built
   from the FULL catalogue (gt_mask). This script re-runs the same placement
   per spatial fold using only VISIBLE faults (withhold_segments) and scores it
   against the WITHHELD positives. That is the only HOLDOUT-DTI this method
   can legitimately report. Each feature is canary-tested alone (AUC > 0.90
   presumed leakage).
4. Uniqueness: Spearman and 3 px dot overlap against every pinned registry
   raster of the competition grid that is available under .cache/registry.
   Spearman uses scipy.stats.rankdata (average ties): the same Pearson-on-ranks
   value as scripts/submission_writer._spearman, computed vectorised.
5. The 0.2778 claim: h33-h33-2-b2 vs the D2.8 44,090-dot reference raster.

Prerequisites (restored by the repo's own scripts, hash-verified):
  bash scripts/download_competition_data.sh --research-mirror
  (cd scripts && python restore_registry_snapshot.py)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_holdout import (  # noqa: E402
    ALPHA, BETA, R_METERS, PIXEL_SIZE_M, dti_weighted_terms, make_quadrant_folds,
    withhold_segments,
)
from submission_writer import _dot_overlap_3px  # noqa: E402
from generate_unique_submission import (  # noqa: E402
    feature_auc_canary, saddle_score, seis_asymmetry,
)

CACHE = ROOT / ".cache" / "competition_data"
REGISTRY = ROOT / ".cache" / "registry"
TIF = ROOT / "evidence" / "quarantine" / "gemsdoe-karage2-gw-nfs-h1-20261029-zeros.tif"  # quarantined; not public
H33 = REGISTRY / "GEMSDOE32/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
D28 = REGISTRY / "GEMSDOE32/docs/downloads/gemsdoe32-d28-ref02600-repro-44090-20261004T183200Z-426073b6-zeros.tif"
OUT = ROOT / "evidence" / "gw-nfs" / "audit.json"
N_DOTS = 30000  # same budget as generate_unique_submission.py
H, W = 3730, 3292


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read1(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(1)


def spearman(a: np.ndarray, b: np.ndarray, rank_a_full: np.ndarray | None = None) -> float:
    """Pearson correlation of average ranks over jointly finite cells.

    ``rank_a_full`` (ranks of ``a`` over all cells) is an optional cache; it is
    only used when ``a`` is finite everywhere, which holds for the shipped TIFF.
    """
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 2:
        return float("nan")
    if rank_a_full is not None and m.all():
        ra = rank_a_full.ravel().astype(float)
    else:
        ra = rankdata(a[m]).astype(float)
    rb = rankdata(b[m]).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return 0.0 if denom == 0 else float((ra * rb).sum() / denom)


def place_dots(visible_gt: np.ndarray, footprint: np.ndarray,
               saddle: np.ndarray, seis: np.ndarray) -> np.ndarray:
    """Mirror of the placement in generate_unique_submission.main(), but driven by
    the faults passed in (full catalogue for the shipped file, visible-only
    faults for the holdout)."""
    dist = ndimage.distance_transform_edt(~visible_gt)
    annulus = (dist > 0.5) & (dist <= 3.0) & footprint & ~visible_gt
    s = np.nan_to_num(saddle, nan=0.0) * annulus
    s = s + 0.3 * np.nan_to_num(seis, nan=0.0) * annulus
    cand = s[annulus]
    if len(cand) > N_DOTS:
        thr = np.percentile(cand, 100 * (1 - N_DOTS / len(cand)))
        mask = annulus & (s >= thr)
    else:
        mask = annulus
    if mask.sum() > N_DOTS:
        idx = np.argwhere(mask)
        order = np.argsort(-s[mask])[:N_DOTS]
        mask = np.zeros_like(mask)
        mask[idx[order, 0], idx[order, 1]] = True
    return mask


def main() -> int:
    for p in (CACHE / "labels.tif", CACHE / "sample_submission.tif", TIF, H33, D28):
        if not p.exists():
            raise SystemExit(f"missing prerequisite: {p} (see module docstring)")

    labels = read1(CACHE / "labels.tif").astype(np.float64)
    footprint = np.isfinite(read1(CACHE / "sample_submission.tif"))
    gt = (labels == 1) & footprint
    out: dict = {
        "schema": "gems.gw_nfs_audit.v1",
        "scope": "read-only audit; no submission, no slot, no organizer score",
        "footprint_pixels": int(footprint.sum()),
        "catalogue_positive_pixels": int(gt.sum()),
    }

    # 1. saved-byte facts
    with rasterio.open(TIF) as ds:
        p = ds.read(1).astype(np.float64)
        out["tif"] = {
            "file": str(TIF.relative_to(ROOT)), "sha256": sha256(TIF),
            "shape": list(p.shape), "dtype": ds.dtypes[0], "crs": str(ds.crs),
            "nodata": ds.nodata, "nan_cells": int(np.isnan(p).sum()),
            "min": float(np.nanmin(p)), "max": float(np.nanmax(p)),
            "dots": int((p > 0).sum()),
            "dots_outside_footprint": int(((p > 0) & ~footprint).sum()),
        }
    dots = p > 0
    # reproduce the shipped dot set from the same inputs (exact-match check)
    shipped_repro = place_dots(gt, footprint, saddle_score(footprint), seis_asymmetry(footprint))
    out["tif"]["reproduces_from_inputs_exact"] = bool(np.array_equal(shipped_repro, dots))
    out["tif"]["reproduced_dot_count"] = int(shipped_repro.sum())

    # 2. catalogue proximity of the shipped dots
    d_cat = ndimage.distance_transform_edt(~gt)[dots]
    out["catalogue_proximity"] = {
        f"within_{r}px_pct": round(float((d_cat <= r).mean() * 100), 4) for r in (1, 2, 3, 5)
    }
    out["catalogue_proximity"]["dots_on_catalogue_pixels"] = int((dots & gt).sum())

    # 3a. what the shipped file scores against the FULL catalogue (self-fit, NOT a holdout)
    folds = make_quadrant_folds(H, W)
    terms = []
    for block in folds:
        withheld, _, _ = withhold_segments(gt, block, buffer_px=3.0)
        g = np.zeros_like(withheld)
        g[withheld] = True
        terms.append(dti_weighted_terms(np.nan_to_num(p), g, PIXEL_SIZE_M, ALPHA, BETA, R_METERS))
    tpw, fpw, fnw = (sum(t[k] for t in terms) for k in ("TPw", "FPw", "FNw"))
    out["shipped_file_vs_full_catalogue_self_fit"] = {
        "evidence_class": "NOT A HOLDOUT (predictions were placed using all catalogue faults)",
        "pooled_DTI": round(float(tpw / (tpw + ALPHA * fpw + BETA * fnw + 1e-12)), 6),
        "withheld_positives": int(sum(t["n_pos_gt"] for t in terms)),
    }

    # 3b. random same-count null (same scorer, same positives)
    rng = np.random.default_rng(0)
    free = np.argwhere(footprint & ~gt)
    null_dtis = []
    for seed in range(3):
        rng = np.random.default_rng(seed)
        q = np.zeros(p.shape, dtype=np.float64)
        sel = free[rng.choice(len(free), int(dots.sum()), replace=False)]
        q[sel[:, 0], sel[:, 1]] = 1.0
        t2 = [dti_weighted_terms(q, _with(gt, b), PIXEL_SIZE_M, ALPHA, BETA, R_METERS) for b in folds]
        a, b_, c = (sum(t[k] for t in t2) for k in ("TPw", "FPw", "FNw"))
        null_dtis.append(round(float(a / (a + ALPHA * b_ + BETA * c + 1e-12)), 6))
    out["random_same_count_null_vs_full_catalogue"] = {"seeds": [0, 1, 2], "pooled_DTI": null_dtis}

    # 3c. proper hide-and-recover holdout of THIS method, per spatial fold
    per_fold = []
    t_fold = []
    canary = []
    saddle_full = saddle_score(footprint)
    seis_full = seis_asymmetry(footprint)
    for k, block in enumerate(folds):
        withheld, visible, dilated = withhold_segments(gt, block, buffer_px=3.0)
        pk = place_dots(visible, footprint, saddle_full, seis_full).astype(np.float64)
        g = np.zeros_like(withheld)
        g[withheld] = True
        t = dti_weighted_terms(pk, g, PIXEL_SIZE_M, ALPHA, BETA, R_METERS)
        t_fold.append(t)
        per_fold.append({"fold": k, "withheld_positives": int(withheld.sum()),
                         "visible_faults": int(visible.sum()), "dots": int(pk.sum()),
                         "fold_DTI": round(float(t["DTI"]), 6)})
        # canary: each feature alone, positives = withheld, negatives = labels 0 outside visible
        dist_vis = ndimage.distance_transform_edt(~visible)
        for name, feat in (("saddle_score", saddle_full), ("seis_asymmetry", seis_full),
                           ("neg_distance_to_visible_faults", -dist_vis)):
            r = feature_auc_canary(feat, labels, footprint, withheld, visible)
            canary.append({"fold": k, "feature": name, **r})
    a, b_, c = (sum(t[k2] for t in t_fold) for k2 in ("TPw", "FPw", "FNw"))
    pooled = a / (a + ALPHA * b_ + BETA * c + 1e-12)
    n_wh = sum(f["withheld_positives"] for f in per_fold)
    out["holdout_hide_and_recover_this_method"] = {
        "evidence_class": "HOLDOUT-DTI",
        "evaluator": "scripts/evaluate_holdout.py dti_weighted_terms (alpha .2, beta .8, 300 m triangular)",
        "split": "4 quadrant blocks with 3 px buffer (repo withhold_segments; pixel blocks, NOT whole fault segments)",
        "pooled_DTI": round(float(pooled), 6),
        "withheld_positives": int(n_wh),
        "per_fold": per_fold,
        "fold_DTI_range": [min(f["fold_DTI"] for f in per_fold), max(f["fold_DTI"] for f in per_fold)],
    }
    out["leakage_canary"] = {
        "rule": "AUC > 0.90 presumed leakage until proven otherwise",
        "rows": canary,
        "max_auc": max((r["auc"] for r in canary if r.get("auc") == r.get("auc")), default=None),
    }

    # 4. uniqueness against every pinned competition-grid registry raster
    regs = []
    rank_p = rankdata(p.ravel()).reshape(p.shape)
    for tif in sorted(REGISTRY.rglob("*.tif")):
        try:
            with rasterio.open(tif) as ds:
                if (ds.height, ds.width) != (H, W):
                    continue
                r = ds.read(1).astype(np.float64)
        except Exception as exc:  # fail closed: record, never skip silently
            regs.append({"raster": str(tif.relative_to(REGISTRY)), "error": str(exc)})
            continue
        n_pos = int((r > 0).sum())
        rho = spearman(p, r, rank_p)
        ov = float(_dot_overlap_3px(dots, r > 0, pixel_m=PIXEL_SIZE_M))
        regs.append({"raster": str(tif.relative_to(REGISTRY)), "positive_cells": n_pos,
                     "spearman": round(rho, 6), "overlap_3px": round(ov, 6)})
    valid = [r for r in regs if "error" not in r]
    dotlike = [r for r in valid if r["positive_cells"] <= 100_000]
    worst_all = max(valid, key=lambda r: r["overlap_3px"]) if valid else None
    worst_dot = max(dotlike, key=lambda r: r["overlap_3px"]) if dotlike else None
    out["uniqueness"] = {
        "registry_rasters_scanned": len(valid),
        "errors": [r for r in regs if "error" in r],
        "rule": "fail if |Spearman| > 0.90 OR 3 px overlap > 0.70 (protocol gate)",
        "max_overlap_any_registry_raster": worst_all,
        "max_overlap_among_dot_rasters_le_100k_positive_cells": worst_dot,
        "rasters_failing_overlap_gate": sum(r["overlap_3px"] > 0.70 for r in valid),
        "rasters_failing_spearman_gate": sum(abs(r["spearman"]) > 0.90 for r in valid),
        "rasters": regs,
    }

    # 5. the GEMSDOE32 0.2778 claim
    h33 = read1(H33)
    d28 = read1(D28)
    hd, dd = h33 > 0, d28 > 0
    out["gemsdoe32_0p2778_claim"] = {
        "file": str(H33.relative_to(REGISTRY)), "sha256_zeros_variant": sha256(H33),
        "owner_stated_sha256_prefix": "c55bafc470054e82",
        "dots_h33": int(hd.sum()), "dots_d28_ref": int(dd.sum()),
        "dots_in_both": int((hd & dd).sum()),
        "dots_only_in_d28": int((dd & ~hd).sum()),
        "dots_only_in_h33": int((hd & ~dd).sum()),
        "subset_of_d28": bool((hd & ~dd).sum() == 0),
        "evidence_class": "FILE-LINKED arithmetic on pinned bytes; the 0.2778 score itself remains USER/OWNER-REPORTED",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


def _with(gt: np.ndarray, block: np.ndarray) -> np.ndarray:
    withheld, _, _ = withhold_segments(gt, block, buffer_px=3.0)
    g = np.zeros_like(withheld)
    g[withheld] = True
    return g


if __name__ == "__main__":
    raise SystemExit(main())

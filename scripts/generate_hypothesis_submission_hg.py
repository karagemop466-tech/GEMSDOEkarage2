#!/usr/bin/env python3
"""RETIRED H-G prototype; execution is deliberately disabled.

The historical H-G generator uses unverified input-band semantics and the legacy
quadrant-pixel evaluator. No committed output/run card establishes a valid result.
Do not run or promote it. Review the current protocol and reconcile experiment
budget before any newly assigned work.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_holdout import make_quadrant_folds, withhold_segments, dti_weighted_terms, PIXEL_SIZE_M, ALPHA, BETA, R_METERS

CACHE = ROOT / ".cache" / "competition_data"
OUT_DIR = ROOT / "docs" / "downloads"

OFFICIAL_CRS = "EPSG:32611"
OFFICIAL_PIXEL_M = 100.0
OFFICIAL_WIDTH = 3292
OFFICIAL_HEIGHT = 3730
OFFICIAL_TRANSFORM = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
NODATA = -3.4028234663852886e+38

B_DETREND_ELEV = 12
B_RAD_K = 4
B_RAD_TH = 6
B_RAD_RATIO = 5

SUBMISSION_NAME = "gemsdoe-hg-annulus-intersection-20261030"
SUBMISSION_NOTE = "Retired H-G prototype; unverified and not approved for submission"
TOP_K = 18000


def load_band(band_idx):
    with rasterio.open(CACHE / "training_features.tif") as ds:
        data = ds.read(band_idx).astype(np.float64)
    return np.where(data == NODATA, np.nan, data)


def load_labels():
    with rasterio.open(CACHE / "labels.tif") as ds:
        data = ds.read(1).astype(np.float64)
        nodata = ds.nodata
    if nodata is not None:
        data = np.where(data == nodata, np.nan, data)
    return data


def load_existing_faults():
    with rasterio.open(CACHE / "existing_faults.tif") as ds:
        data = ds.read(1).astype(np.float64)
        nodata = ds.nodata
    if nodata is not None:
        data = np.where(data == nodata, np.nan, data)
    return data


def load_template_footprint():
    with rasterio.open(CACHE / "sample_submission.tif") as ds:
        return np.isfinite(ds.read(1))


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm01(arr, footprint):
    fin = arr[footprint & np.isfinite(arr)]
    if fin.size == 0 or fin.max() == fin.min():
        return np.zeros_like(arr)
    out = np.clip((arr - fin.min()) / (fin.max() - fin.min()), 0.0, 1.0)
    return np.where(np.isfinite(arr), out, 0.0)


def curvature_convergence(elev, footprint):
    elev_filled = np.nan_to_num(elev, nan=np.nanmedian(elev[footprint]))
    convergence = np.zeros_like(elev, dtype=np.float64)
    for scale_m in (100.0, 500.0, 2000.0):
        sigma = scale_m / OFFICIAL_PIXEL_M
        smooth = ndimage.gaussian_filter(elev_filled, sigma=sigma, mode="nearest")
        dzdx = ndimage.sobel(smooth, axis=1)
        dzdy = ndimage.sobel(smooth, axis=0)
        grad_mag = np.hypot(dzdx, dzdy) + 1e-12
        ux, uy = dzdx / grad_mag, dzdy / grad_mag
        dzdxx = ndimage.sobel(dzdx, axis=1)
        zdyy = ndimage.sobel(dzdy, axis=0)
        dzdexy = ndimage.sobel(dzdx, axis=0)
        prof_curv = (dzdxx * ux * ux + 2.0 * dzdexy * ux * uy + zdyy * uy * uy) / grad_mag
        nx, ny = -uy, ux
        plan_curv = (dzdxx * nx * nx + 2.0 * dzdexy * nx * ny + zdyy * ny * ny) / grad_mag
        w = 1.0 / (1.0 + sigma)
        convergence += w * ((-np.clip(prof_curv, -1, 1)) ** 2 + (np.clip(plan_curv, -1, 1)) ** 2)
    fin = convergence[footprint & np.isfinite(convergence)]
    if fin.size > 0 and fin.max() > fin.min():
        convergence = (convergence - fin.min()) / (fin.max() - fin.min())
    return np.clip(convergence, 0.0, 1.0)


def radiometric_alteration(k, th, ratio, footprint):
    k_n, th_n, r_n = norm01(k, footprint), norm01(th, footprint), norm01(ratio, footprint)
    alt = (1.0 - k_n) * th_n * r_n
    fin = alt[footprint & np.isfinite(alt)]
    if fin.size > 0 and fin.max() > fin.min():
        alt = (alt - fin.min()) / (fin.max() - fin.min())
    return np.clip(alt, 0.0, 1.0)


def main():
    raise SystemExit(
        "DISABLED: H-G is a retired research prototype with unverified band semantics "
        "and no committed result card. Reconcile the experiment budget and assign a "
        "protocol-compliant lane before any new experiment."
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[H-G] Loading inputs...", flush=True)
    detrend = load_band(B_DETREND_ELEV)
    rad_k = load_band(B_RAD_K)
    rad_th = load_band(B_RAD_TH)
    rad_ratio = load_band(B_RAD_RATIO)
    labels = load_labels()
    faults = load_existing_faults()
    footprint = load_template_footprint()

    gt_mask = (labels == 1) & np.isfinite(labels)
    fault_bool = (faults == 1) & np.isfinite(faults)
    print(f"[H-G] GT positives: {int(gt_mask.sum()):,}, Fault pixels: {int(fault_bool.sum()):,}", flush=True)

    print("[H-G] Computing features...", flush=True)
    curv = curvature_convergence(detrend, footprint)
    alt = radiometric_alteration(rad_k, rad_th, rad_ratio, footprint)
    dist_fault = ndimage.distance_transform_edt(~fault_bool, sampling=OFFICIAL_PIXEL_M)

    # Annulus: 200m to 1000m from known faults
    annulus = (dist_fault >= 200.0) & (dist_fault <= 1000.0) & footprint & ~fault_bool
    print(f"[H-G] Annulus pixels: {int(annulus.sum()):,}", flush=True)

    # Propensity score within annulus
    alt = np.nan_to_num(alt, nan=0.0)
    curv = np.nan_to_num(curv, nan=0.0)
    score = np.zeros_like(detrend, dtype=np.float64)
    score[annulus] = alt[annulus] * curv[annulus]

    # Sparsify to TOP_K
    annulus_scores = score[annulus]
    n_annulus = int(annulus.sum())
    print(f"[H-G] Annulus score range: min={annulus_scores.min():.6f} max={annulus_scores.max():.6f} "
          f"nonzero={int((annulus_scores > 0).sum()):,} / {n_annulus:,}", flush=True)
    if n_annulus > TOP_K:
        threshold = np.percentile(annulus_scores, 100 * (1 - TOP_K / n_annulus))
        dot_mask = annulus & (score >= threshold)
        if int(dot_mask.sum()) > TOP_K:
            idx = np.argwhere(dot_mask)
            scores = score[dot_mask]
            order = np.argsort(-scores)[:TOP_K]
            dot_mask = np.zeros_like(dot_mask)
            dot_mask[idx[order, 0], idx[order, 1]] = True
    else:
        dot_mask = annulus

    # Build output: dots with score value, 0 elsewhere inside footprint, NaN outside
    score = np.nan_to_num(score, nan=0.0)
    output = np.where(dot_mask, score, 0.0)
    output = np.where(footprint, output, np.nan)
    output = np.clip(output, 0.0, 1.0)

    n_dots = int((output > 0).sum())
    print(f"[H-G] Dots placed: {n_dots:,}", flush=True)

    # Save TIF
    tif_path = OUT_DIR / f"{SUBMISSION_NAME}.tif"
    profile = {
        "driver": "GTiff", "dtype": "float32", "nodata": np.nan,
        "width": OFFICIAL_WIDTH, "height": OFFICIAL_HEIGHT, "count": 1,
        "crs": OFFICIAL_CRS, "transform": OFFICIAL_TRANSFORM,
        "compress": "lzw", "tiled": False,
    }
    with rasterio.open(tif_path, "w", **profile) as ds:
        ds.write(output.astype(np.float32), 1)
    tif_sha = sha256_file(tif_path)
    print(f"[H-G] Wrote {tif_path} sha256={tif_sha}", flush=True)

    # Format validation
    from validate_tif import validate as validate_tif
    val_result = validate_tif(tif_path, template=CACHE / "sample_submission.tif")
    val_passed = val_result["strict_format_pass"]
    print(f"[H-G] Format: {'PASS' if val_passed else 'FAIL'}", flush=True)

    # Uniqueness vs local registry
    import check_uniqueness as cu
    registry_path = ROOT / "registry" / "combined_registry_20261029.json"
    manifest = json.loads(registry_path.read_text())
    local_entries = [e for e in manifest["rasters"] if Path(e["local"]).is_file()]
    print(f"[H-G] Local registry rasters: {len(local_entries)} / {len(manifest['rasters'])}", flush=True)

    template, tmask, expected_grid = cu.read_tif(CACHE / "sample_submission.tif")
    foot = np.isfinite(template) & (tmask > 0)
    candidate_foot_vals = np.where(foot & np.isfinite(output), output, 0.0)
    candidate_ranks, norm = cu.centered_ranks(candidate_foot_vals[foot])

    dot_mask_bool = output > 0
    uniqueness_results = []
    max_overlap, max_rho = 0.0, 0.0
    duplicate_found = False

    for entry in local_entries:
        p = Path(entry["local"])
        try:
            ref, refmask, _ = cu.read_tif(p, expected_grid)
            if np.any(refmask[foot] == 0) or not np.isfinite(ref[foot]).all():
                continue
            if np.any((ref[foot] < 0) | (ref[foot] > 1)):
                continue
            result = cu.check_comparator(
                candidate_ranks, norm, dot_mask_bool & foot, ref, foot,
            )
            uniqueness_results.append({
                "path": str(p), "sha256": entry["sha256"],
                "spearman": result["spearman_full_footprint"],
                "overlap_fraction": result["overlap_fraction"],
                "matches_within_3px": result["matches_within_3px"],
                "support_pixels": result["support_pixels"],
                "duplicate": result["duplicate"],
            })
            max_overlap = max(max_overlap, result["overlap_fraction"])
            max_rho = max(max_rho, abs(result["spearman_full_footprint"]))
            if result["duplicate"]:
                duplicate_found = True
        except Exception as exc:
            print(f"  SKIP {p}: {exc}", flush=True)

    uniqueness_pass = (not duplicate_found) and (max_rho <= 0.90) and (max_overlap <= 0.70)
    print(f"[H-G] Uniqueness: max_rho={max_rho:.4f} max_overlap={max_overlap:.4f} "
          f"duplicate={duplicate_found} PASS={uniqueness_pass}", flush=True)

    # Holdout evaluation
    folds = make_quadrant_folds(OFFICIAL_HEIGHT, OFFICIAL_WIDTH)
    terms = []
    for i, block in enumerate(folds):
        withheld, visible, _dilated = withhold_segments(gt_mask, block, buffer_px=3.0)
        p = np.nan_to_num(output.astype(np.float64), nan=0.0)
        active = block & ~visible
        p = np.where(active, p, 0.0)
        gt = np.zeros_like(p, dtype=bool)
        gt[withheld] = True
        terms.append(dti_weighted_terms(p, gt, pixel_size_m=PIXEL_SIZE_M,
                                        alpha=ALPHA, beta=BETA, R_m=R_METERS))

    TPw = sum(t["TPw"] for t in terms)
    FPw = sum(t["FPw"] for t in terms)
    FNw = sum(t["FNw"] for t in terms)
    denom = TPw + ALPHA * FPw + BETA * FNw + 1e-12
    pooled_dti = TPw / denom
    fold_dtis = [t["DTI"] for t in terms]
    n_withheld = sum(t["n_pos_gt"] for t in terms)
    print(f"[H-G] Holdout: pooled_DTI={pooled_dti:.6f} TPw={TPw:.2f} FPw={FPw:.2f} "
          f"FNw={FNw:.2f} withheld={n_withheld:,} fold_DTIs={[round(d,4) for d in fold_dtis]}",
          flush=True)

    # Leakage canary
    from sklearn.metrics import roc_auc_score
    neg_mask = (labels == 0) & footprint & (~fault_bool) & np.isfinite(labels)

    def feature_auc(feature, name):
        pos = gt_mask
        neg = neg_mask
        if pos.sum() == 0 or neg.sum() == 0:
            return {"auc": float("nan"), "n_pos": 0, "n_neg": 0, "leakage": None}
        f = np.nan_to_num(feature, nan=0.0)
        y = np.concatenate([np.ones(int(pos.sum())), np.zeros(int(neg.sum()))])
        X = np.concatenate([f[pos], f[neg]])
        try:
            auc = roc_auc_score(y, X)
        except ValueError:
            auc = float("nan")
        leak = bool(auc > 0.90) if np.isfinite(auc) else None
        return {"auc": round(float(auc), 6), "n_pos": int(pos.sum()),
                "n_neg": int(neg.sum()), "leakage": leak}

    canary = {
        "annulus_score": feature_auc(output, "annulus_score"),
        "alteration": feature_auc(alt, "alteration"),
        "curvature": feature_auc(curv, "curvature"),
    }
    for name, r in canary.items():
        print(f"  {name}: AUC={r['auc']} leakage={r['leakage']}", flush=True)

    # Audit JSON
    audit = {
        "kind": "H-G hypothesis generation audit (not organizer acceptance)",
        "file": str(tif_path),
        "sha256": tif_sha,
        "bytes": tif_path.stat().st_size,
        "submission_name": SUBMISSION_NAME,
        "note": SUBMISSION_NOTE,
        "note_chars": len(SUBMISSION_NOTE),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "hypothesis": "H-G: Annulus-targeted fault-intersection propensity (200m-1km off known faults)",
        "mechanism": ("Dots placed 200m-1000m from known catalogue faults, weighted by "
                      "radiometric alteration x curvature convergence; on-fault pixels masked"),
        "named_non_fault_mimic": "Paleo-weathering fronts, lithologic contacts, radiometric survey striping",
        "format_validation": {"passed": val_passed, "checks": val_result["checks"],
                              "diagnostics": val_result.get("diagnostics", {})},
        "uniqueness": {
            "passed": uniqueness_pass,
            "max_spearman_abs": max_rho,
            "max_dot_overlap_3px": max_overlap,
            "duplicate_found": duplicate_found,
            "n_local_registry_compared": len(uniqueness_results),
            "comparisons": uniqueness_results,
            "note": "Only locally available registry rasters compared.",
        },
        "holdout": {
            "pooled_DTI": round(float(pooled_dti), 6),
            "TPw": round(TPw, 2), "FPw": round(FPw, 2), "FNw": round(FNw, 2),
            "n_withheld_total": n_withheld,
            "fold_DTIs": [round(d, 4) for d in fold_dtis],
            "fold_range": [round(min(fold_dtis), 4), round(max(fold_dtis), 4)],
            "evaluator": "evaluate_holdout.dti_weighted_terms (alpha=0.2, beta=0.8, R=300m)",
            "classification": "HOLDOUT-DTI proxy (fixed field)",
        },
        "leakage_canary": canary,
        "verdict": "negative" if pooled_dti < 0.05 else "promote",
        "ok_to_submit": False,
        "slot_authorized": False,
        "irregularities": [
            "Band-to-radiometric-layer mapping unverified.",
            "Holdout is a proxy, not strict hide-and-recover OOF.",
            "Only 7 of 472 registry rasters locally available.",
        ],
    }
    audit_path = OUT_DIR / f"{SUBMISSION_NAME}.audit.json"
    with open(audit_path, "w") as f:
        json.dump(audit, f, indent=2, allow_nan=False)
    print(f"[H-G] Audit -> {audit_path}", flush=True)

    # Run card
    card = {
        "schema_version": 1,
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "hypothesis": audit["hypothesis"],
        "mechanism": audit["mechanism"],
        "named_non_fault_process": audit["named_non_fault_mimic"],
        "holdout": {
            "classification": "HOLDOUT-DTI (proxy; fixed field)",
            "evaluator_version": "evaluate_holdout.dti_weighted_terms alpha=0.2 beta=0.8 R=300m",
            "withheld_positives": n_withheld,
            "dti": round(float(pooled_dti), 6),
            "confidence_interval_95": [round(min(fold_dtis), 6), round(max(fold_dtis), 6)],
            "note": "Fold-wise range over 4 spatial blocks; not a bootstrap CI.",
        },
        "correlation_and_overlap_vs_registry": {
            "candidate_surface_spearman_max_abs": round(max_rho, 6),
            "candidate_final_dot_overlap_max": round(max_overlap, 6),
            "duplicate_found": duplicate_found,
            "n_registry_compared": len(uniqueness_results),
            "threshold": "Spearman <= 0.90 AND dot overlap <= 70%",
        },
        "leakage_canary": canary,
        "raster_sha256": tif_sha,
        "validator": {"strict_format_pass": val_passed, "checks": val_result["checks"]},
        "submission_name": SUBMISSION_NAME,
        "note": SUBMISSION_NOTE,
        "verdict": audit["verdict"],
        "ok_to_submit": False,
        "slot_authorized": False,
        "experiments_run": 2,
        "budget": "Script labels H-G as experiment 2; no committed output/run card, so count and elapsed time are unverified",
    }
    card_path = OUT_DIR / f"{SUBMISSION_NAME}.run-card.json"
    with open(card_path, "w") as f:
        json.dump(card, f, indent=2)
    print(f"[H-G] Run card -> {card_path}", flush=True)
    print(f"[H-G] Verdict: {audit['verdict']} (DTI={pooled_dti:.6f})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

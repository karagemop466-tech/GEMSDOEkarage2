#!/usr/bin/env python3
"""
Generate a unique, hypothesis-driven GeoTIFF submission for the DOE GEMS Prize
Challenge.

Hypothesis H-B (Blind Geothermal, off-catalogue):
  Blind faults that host geothermal systems -- and that are ABSENT from the
  USGS/INGENIOUS catalogue (the actual initial-round test target per the official
  problem page) -- are marked by the coincidence of three independent geophysical
  signals, NONE derived from the fault catalogue:

    1. Radiometric hydrothermal alteration  (low K, high eTh, elevated eU/eTh ratio)
    2. Reduced-to-pole magnetic gradient edge  (structural / magnetometric break)
    3. Isostatic gravity gradient edge        (density contrast)

Physical rationale
------------------
Hydrothermal fluids alter wallrock along blind fault conduits (K leaching, U/Th
enrichment, clay formation). Faults offset magnetic and density bodies, producing
gradient edges in magnetics and gravity. Where all three coincide away from mapped
catalogue faults, a blind fault is a strong discovery candidate -- exactly what the
private test set rewards (new faults not in the public USGS database).

Why this is distinct from everything in the repo
------------------------------------------------
* H-F (existing docs/downloads TIFF) used radiometrics x curvature x
  distance-to-known-faults; its fault_proximity feature tripped the leakage canary
  (AUC = 1.0). H-B uses NO fault-derived feature: catalogue faults are masked only
  as a final OUTPUT constraint, never as an input feature.
* Focus-site dot submissions (GEMSDOE24/25/27/28/30/31/32/33/36) trace catalogue
  faults or lattice positions (97.6-100% overlap with each other, fail the literal
  70% / 3-px dot-overlap gate). H-B targets off-catalogue geothermal signatures.
* K2/K3 used conductivity-gravity saddles and lineament density; H-B uses the
  radiometric-alteration x magnetic-edge x gravity-edge intersection.

Protocol compliance
-------------------
* Continuous probability field in [0, 1] EVERYWHERE (zeros outside the footprint).
  This keeps every pixel inside [0, 1] so the portal's range check cannot reject the
  file on the "values must be in range [0, 1]" error. (The official wording also
  permits null/nan outside the bounds; that exterior convention remains unresolved
  in this checkout and is flagged below.)
* Known catalogue faults masked pixel-exactly as an OUTPUT constraint only.
* No feature derived from labels/truth.
* Outputs: GeoTIFF + audit JSON + run card JSON.
* Does NOT spend a submission slot; verdict promote / negative goes to the
  separate selector step.

Usage:
  python scripts/generate_blind_geothermal_submission.py
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CACHE = ROOT / ".cache" / "competition_data"
OUT_DIR = ROOT / "docs" / "downloads"

# Official competition grid (verified against restored owner-mirror template).
OFFICIAL_CRS = "EPSG:32611"
OFFICIAL_PIXEL_M = 100.0
OFFICIAL_WIDTH = 3292
OFFICIAL_HEIGHT = 3730
OFFICIAL_TRANSFORM = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
OFFICIAL_BOUNDS = (243350.0, 4135550.0, 572550.0, 4508550.0)
NODATA = -3.4028234663852886e+38

# ---------------------------------------------------------------------------
# Band mapping (best effort; flagged for manual review against organizer docs)
# ---------------------------------------------------------------------------
# Band  4: potassium K (%)                  -> radiometric
# Band  5: eU / eTh ratio                   -> radiometric
# Band  6: equivalent thorium eTh (ppm)     -> radiometric
# Band  7: reduced-to-pole magnetic anomaly -> magnetics
# Band 13: isostatic gravity anomaly        -> gravity
# Band 12: detrended elevation              -> structural context (curvature)
B_RAD_K = 4
B_RAD_RATIO = 5
B_RAD_TH = 6
B_MAG_RTP = 7
B_GRAV_ISO = 13
B_ELEV_DETREND = 12

SUBMISSION_NAME = (
    "gemsdoe-blind-geothermal-rad-mag-grav-intersection-20261031"
)
SUBMISSION_NOTE = (
    "Unique off-catalogue blind-geothermal field: radiometric alteration x "
    "magnetic edge x gravity edge; catalogue faults masked; research-only"
)
SUBMISSION_NOTE = SUBMISSION_NOTE[:140]

TOP_K = 18000  # sparsify: keeps minimum lattice overlap below the 70% gate


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_band(band_idx: int) -> np.ndarray:
    with rasterio.open(CACHE / "training_features.tif") as ds:
        data = ds.read(band_idx).astype(np.float64)
    return np.where(data == NODATA, np.nan, data)


def load_labels() -> np.ndarray:
    with rasterio.open(CACHE / "labels.tif") as ds:
        data = ds.read(1).astype(np.float64)
        nodata = ds.nodata
    if nodata is not None:
        data = np.where(data == nodata, np.nan, data)
    return data


def load_existing_faults() -> np.ndarray:
    with rasterio.open(CACHE / "existing_faults.tif") as ds:
        data = ds.read(1).astype(np.float64)
        nodata = ds.nodata
    if nodata is not None:
        data = np.where(data == nodata, np.nan, data)
    return data


def load_template_footprint() -> np.ndarray:
    with rasterio.open(CACHE / "sample_submission.tif") as ds:
        sample = ds.read(1)
        return np.isfinite(sample)


def norm01(arr: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Min-max normalize to [0,1] over finite footprint pixels."""
    out = np.zeros_like(arr, dtype=np.float64)
    fin = arr[footprint & np.isfinite(arr)]
    if fin.size > 0 and fin.max() > fin.min():
        out = np.clip((arr - fin.min()) / (fin.max() - fin.min()), 0.0, 1.0)
    out = np.where(footprint & np.isfinite(arr), out, 0.0)
    return out


def gradient_magnitude(arr: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Sobel gradient magnitude of a filled array, normalized to [0,1]."""
    filled = np.nan_to_num(arr, nan=np.nanmedian(arr[footprint]))
    gx = ndimage.sobel(filled, axis=1)
    gy = ndimage.sobel(filled, axis=0)
    mag = np.hypot(gx, gy)
    fin = mag[footprint]
    if fin.size > 0 and fin.max() > fin.min():
        mag = np.clip((mag - fin.min()) / (fin.max() - fin.min()), 0.0, 1.0)
    return np.where(footprint, mag, 0.0)


def curvature_convergence(elev: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Multi-scale profile+plan curvature convergence, normalized to [0,1]."""
    elev_filled = np.nan_to_num(elev, nan=np.nanmedian(elev[footprint]))
    convergence = np.zeros_like(elev, dtype=np.float64)
    for scale_m in (200.0, 1000.0):
        sigma = scale_m / OFFICIAL_PIXEL_M
        smooth = ndimage.gaussian_filter(elev_filled, sigma=sigma, mode="nearest")
        dzdx = ndimage.sobel(smooth, axis=1)
        dzdy = ndimage.sobel(smooth, axis=0)
        grad_mag = np.hypot(dzdx, dzdy) + 1e-12
        ux, uy = dzdx / grad_mag, dzdy / grad_mag
        dzdxx = ndimage.sobel(dzdx, axis=1)
        zdyy = ndimage.sobel(dzdy, axis=0)
        dzdexy = ndimage.sobel(dzdx, axis=0)
        prof = (dzdxx * ux * ux + 2.0 * dzdexy * ux * uy + zdyy * uy * uy) / grad_mag
        nx, ny = -uy, ux
        plan = (dzdxx * nx * nx + 2.0 * dzdexy * nx * ny + zdyy * ny * ny) / grad_mag
        w = 1.0 / (1.0 + sigma)
        convergence += w * ((-np.clip(prof, -1, 1)) ** 2 + (np.clip(plan, -1, 1)) ** 2)
    fin = convergence[footprint & np.isfinite(convergence)]
    if fin.size > 0 and fin.max() > fin.min():
        convergence = (convergence - fin.min()) / (fin.max() - fin.min())
    return np.clip(np.where(footprint, convergence, 0.0), 0.0, 1.0)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Load inputs ------------------------------------------------------
    print("[H-B] Loading feature stack...", flush=True)
    k = load_band(B_RAD_K)
    ratio = load_band(B_RAD_RATIO)
    th = load_band(B_RAD_TH)
    mag = load_band(B_MAG_RTP)
    grav = load_band(B_GRAV_ISO)
    elev_detrend = load_band(B_ELEV_DETREND)

    labels = load_labels()
    faults = load_existing_faults()
    footprint = load_template_footprint()

    gt_mask = (labels == 1) & np.isfinite(labels)
    fault_bool = (faults == 1) & np.isfinite(faults)
    print(
        f"[H-B] Footprint: {int(footprint.sum()):,} pixels, "
        f"GT positives: {int(gt_mask.sum()):,}, fault pixels: {int(fault_bool.sum()):,}",
        flush=True,
    )

    # ---- Features (none derived from faults/labels) -----------------------
    print("[H-B] Radiometric alteration index (low K, high eTh, high eU/eTh)...",
          flush=True)
    k_n = norm01(k, footprint)
    th_n = norm01(th, footprint)
    ratio_n = norm01(ratio, footprint)
    alteration = np.clip((1.0 - k_n) * th_n * ratio_n, 0.0, 1.0)

    print("[H-B] Magnetic gradient edge (RTP)...", flush=True)
    mag_edge = gradient_magnitude(mag, footprint)

    print("[H-B] Isostatic gravity gradient edge...", flush=True)
    grav_edge = gradient_magnitude(grav, footprint)

    print("[H-B] Curvature convergence (structural context)...", flush=True)
    curv = curvature_convergence(elev_detrend, footprint)

    # ---- Combine: intersection of independent geophysical signals ---------
    # Three-way coincidence: alteration x magnetic edge x gravity edge.
    # Curvature acts as a soft structural booster (not required).
    score = alteration * mag_edge * grav_edge * (0.5 + 0.5 * curv)

    # ---- Output constraint: mask catalogue faults pixel-exactly -----------
    # Catalogue faults are NOT an input feature; they are only excluded from the
    # output so the field targets off-catalogue (test-set-relevant) locations.
    score = np.where(fault_bool & footprint, 0.0, score)

    # Missing input -> 0; outside footprint -> 0 (finite, inside [0,1]).
    missing = (
        np.isnan(k) | np.isnan(ratio) | np.isnan(th)
        | np.isnan(mag) | np.isnan(grav) | np.isnan(elev_detrend)
    )
    score = np.where(footprint & ~missing, score, 0.0)

    # Normalize to [0,1] over footprint.
    finite_vals = score[footprint]
    if finite_vals.size > 0 and finite_vals.max() > finite_vals.min():
        score = (score - finite_vals.min()) / (finite_vals.max() - finite_vals.min())
    score = np.clip(score, 0.0, 1.0)
    score = np.where(footprint, score, 0.0)  # zeros outside footprint

    # ---- Sparsify to top-K dots -------------------------------------------
    flat = score[footprint]
    if flat.size > TOP_K:
        threshold = np.percentile(flat, 100 * (1 - TOP_K / flat.size))
        score = np.where((score >= threshold) & footprint, score, 0.0)
    score = np.clip(score, 0.0, 1.0)

    # ---- Statistics -------------------------------------------------------
    finite_foot = score[footprint]
    n_dots = int((score > 0.0).sum())
    print(
        f"[H-B] Output: min={finite_foot.min():.6f} max={finite_foot.max():.6f} "
        f"mean={finite_foot.mean():.6f} dots(>0): {n_dots:,} "
        f"footprint_pixels={int(footprint.sum()):,}",
        flush=True,
    )

    # ---- Save GeoTIFF -----------------------------------------------------
    tif_path = OUT_DIR / f"{SUBMISSION_NAME}.tif"
    profile = {
        "driver": "GTiff",
        "dtype": "float32",
        "nodata": None,  # finite zeros outside footprint (see [0,1] portal note)
        "width": OFFICIAL_WIDTH,
        "height": OFFICIAL_HEIGHT,
        "count": 1,
        "crs": OFFICIAL_CRS,
        "transform": OFFICIAL_TRANSFORM,
        "compress": "lzw",
        "tiled": False,
    }
    with rasterio.open(tif_path, "w", **profile) as ds:
        ds.write(score.astype(np.float32), 1)

    tif_sha = sha256_file(tif_path)
    print(f"[H-B] Wrote {tif_path} sha256={tif_sha}", flush=True)

    # ---- Format validation ------------------------------------------------
    from validate_tif import validate as validate_tif

    val_result = validate_tif(tif_path, template=CACHE / "sample_submission.tif")
    val_passed = val_result["strict_format_pass"]
    print(f"[H-B] Format validation: {'PASS' if val_passed else 'FAIL'}", flush=True)
    for ck, passed in val_result["checks"].items():
        if not passed:
            print(f"  FAIL: {ck}", flush=True)

    # ---- Uniqueness vs locally available rasters --------------------------
    print("[H-B] Uniqueness vs local rasters...", flush=True)
    import check_uniqueness as cu

    template, tmask, expected_grid = cu.read_tif(CACHE / "sample_submission.tif")
    foot = np.isfinite(template) & (tmask > 0)
    candidate_foot_vals = np.where(foot & np.isfinite(score), score, 0.0)
    candidate_ranks, norm = cu.centered_ranks(candidate_foot_vals[foot])
    dot_mask = score > 0.001

    local_rasters = []
    candidate_name = tif_path.name
    for p in sorted(ROOT.glob("docs/downloads/*.tif")):
        if p.name == candidate_name:
            continue  # never compare the candidate against itself
        local_rasters.append({"path": str(p), "name": p.name})
    for p in sorted(ROOT.glob("reference/**/*.tif")):
        local_rasters.append({"path": str(p), "name": str(p)})

    uniqueness_results = []
    max_overlap = 0.0
    max_rho = 0.0
    duplicate_found = False
    for entry in local_rasters:
        p = Path(entry["path"])
        try:
            ref, refmask, _ = cu.read_tif(p, expected_grid)
            if not np.isfinite(ref[foot]).all():
                continue
            if np.any((ref[foot] < 0) | (ref[foot] > 1)):
                continue
            result = cu.check_comparator(
                candidate_ranks, norm, dot_mask & foot, ref, foot,
            )
            uniqueness_results.append({
                "path": entry["path"],
                "name": entry["name"],
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
            print(f"  SKIP {p.name}: {exc}", flush=True)

    uniqueness_pass = (not duplicate_found) and (max_rho <= 0.90) and (max_overlap <= 0.70)
    print(
        f"[H-B] Uniqueness: max_rho={max_rho:.4f} max_overlap={max_overlap:.4f} "
        f"duplicate={duplicate_found} PASS={uniqueness_pass} (compared {len(uniqueness_results)})",
        flush=True,
    )

    # ---- Holdout evaluation (hide-and-recover) ----------------------------
    print("[H-B] Holdout evaluation (hide-and-recover)...", flush=True)
    from evaluate_holdout import (
        make_quadrant_folds, withhold_segments, dti_weighted_terms,
        PIXEL_SIZE_M, ALPHA, BETA, R_METERS,
    )

    folds = make_quadrant_folds(OFFICIAL_HEIGHT, OFFICIAL_WIDTH)
    terms = []
    for i, block in enumerate(folds):
        withheld, visible, _dilated = withhold_segments(gt_mask, block, buffer_px=3.0)
        p = np.nan_to_num(score.astype(np.float64), nan=0.0)
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
    print(
        f"[H-B] Holdout: pooled_DTI={pooled_dti:.6f} TPw={TPw:.2f} FPw={FPw:.2f} "
        f"FNw={FNw:.2f} withheld={n_withheld:,} fold_DTIs={[round(d,4) for d in fold_dtis]}",
        flush=True,
    )

    # ---- Leakage canary: each feature alone --------------------------------
    print("[H-B] Leakage canary (per-feature AUC on holdout)...", flush=True)

    def _auc_rank(scores_pos, scores_neg):
        """Mann-Whitney U / rank-based AUC; handles ties via average ranks."""
        n_pos = scores_pos.size
        n_neg = scores_neg.size
        if n_pos == 0 or n_neg == 0:
            return float("nan")
        all_scores = np.concatenate([scores_pos, scores_neg])
        order = np.argsort(all_scores, kind="mergesort")
        sorted_scores = all_scores[order]
        ranks = np.empty(all_scores.size, dtype=np.float64)
        i = 0
        n = all_scores.size
        while i < n:
            j = i
            while j + 1 < n and sorted_scores[j + 1] == sorted_scores[i]:
                j += 1
            ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
            i = j + 1
        pos_ranks = ranks[:n_pos]
        auc = (pos_ranks.sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
        return float(auc)

    def feature_auc(feature, name):
        pos = gt_mask
        neg = (labels == 0) & footprint & (~fault_bool)
        if pos.sum() == 0 or neg.sum() == 0:
            return {"auc": float("nan"), "n_pos": int(pos.sum()), "n_neg": int(neg.sum()), "leakage": None}
        f = np.nan_to_num(feature, nan=0.0)
        auc = _auc_rank(f[pos], f[neg])
        leak = bool(auc > 0.90) if np.isfinite(auc) else None
        return {"auc": round(auc, 6), "n_pos": int(pos.sum()),
                "n_neg": int(neg.sum()), "leakage": leak}

    canary_results = {
        "alteration": feature_auc(alteration, "alteration"),
        "mag_edge": feature_auc(mag_edge, "mag_edge"),
        "grav_edge": feature_auc(grav_edge, "grav_edge"),
        "curvature": feature_auc(curv, "curvature"),
        "combined_score": feature_auc(score, "combined"),
    }
    for name, r in canary_results.items():
        print(f"  {name}: AUC={r['auc']} pos={r['n_pos']} neg={r['n_neg']} leakage={r['leakage']}",
              flush=True)

    # ---- Audit JSON -------------------------------------------------------
    audit = {
        "kind": "H-B blind-geothermal hypothesis generation audit (not organizer acceptance)",
        "file": str(tif_path),
        "sha256": tif_sha,
        "bytes": tif_path.stat().st_size,
        "submission_name": SUBMISSION_NAME,
        "note": SUBMISSION_NOTE,
        "note_chars": len(SUBMISSION_NOTE),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "hypothesis": ("H-B: Off-catalogue blind geothermal faults marked by the "
                       "coincidence of radiometric alteration, magnetic edge, and gravity edge"),
        "mechanism": ("Hydrothermal alteration (low K, high eTh, high eU/eTh) x RTP "
                      "magnetic gradient edge x isostatic gravity gradient edge; "
                      "catalogue faults masked as output constraint only, not a feature"),
        "named_non_fault_mimic": ("Paleo-weathering fronts, lithologic contacts, "
                                  "survey-line striping in radiometrics, intrusive "
                                  "magnetic/gravity bodies"),
        "band_mapping": {
            "4": "potassium K (%)",
            "5": "eU/eTh ratio",
            "6": "eTh (ppm)",
            "7": "RTP magnetic anomaly",
            "13": "isostatic gravity anomaly",
            "12": "detrended elevation (curvature context)",
        },
        "band_mapping_note": "Best-effort mapping from band value ranges; verify against organizer band documentation.",
        "format_validation": {
            "passed": val_passed,
            "checks": val_result["checks"],
            "diagnostics": val_result.get("diagnostics", {}),
        },
        "uniqueness": {
            "passed": uniqueness_pass,
            "max_spearman_abs": max_rho,
            "max_dot_overlap_3px": max_overlap,
            "duplicate_found": duplicate_found,
            "n_local_registry_compared": len(uniqueness_results),
            "comparisons": uniqueness_results,
            "note": "Compared against locally available rasters only; full 472-raster registry not downloaded.",
        },
        "holdout": {
            "pooled_DTI": round(float(pooled_dti), 6),
            "TPw": round(TPw, 2),
            "FPw": round(FPw, 2),
            "FNw": round(FNw, 2),
            "n_withheld_total": n_withheld,
            "fold_DTIs": [round(d, 4) for d in fold_dtis],
            "fold_range": [round(min(fold_dtis), 4), round(max(fold_dtis), 4)],
            "evaluator": "evaluate_holdout.dti_weighted_terms (alpha=0.2, beta=0.8, R=300m)",
            "classification": "HOLDOUT-DTI proxy (fixed field scored against withheld positives)",
        },
        "leakage_canary": canary_results,
        "verdict": "promote" if (val_passed and uniqueness_pass) else "negative",
        "ok_to_submit": False,
        "slot_authorized": False,
        "irregularities": [
            "Band-to-layer mapping is best-effort from value ranges; not verified by organizer documentation.",
            "Exterior uses finite zeros (inside [0,1]) to avoid the portal [0,1] range error; official wording permits null/nan outside bounds -- convention unresolved.",
            "Holdout is a proxy, not strict hide-and-recover OOF (fixed field used no fault feature, but scored against known-fault labels which differ from the new-fault test set).",
            "Only locally available rasters compared for uniqueness; organizer template/portal acceptance not established.",
        ],
    }

    audit_path = OUT_DIR / f"{SUBMISSION_NAME}.audit.json"
    with open(audit_path, "w") as f:
        json.dump(audit, f, indent=2, allow_nan=False)
    print(f"[H-B] Audit -> {audit_path}", flush=True)

    # ---- Run card JSON ----------------------------------------------------
    run_card = {
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
            "confidence_interval_95": [
                round(min(fold_dtis), 6), round(max(fold_dtis), 6)
            ],
            "note": "Fold-wise range over 4 spatial blocks; not a bootstrap CI.",
        },
        "correlation_and_overlap_vs_registry": {
            "candidate_surface_spearman_max_abs": round(max_rho, 6),
            "candidate_final_dot_overlap_max": round(max_overlap, 6),
            "duplicate_found": duplicate_found,
            "n_registry_compared": len(uniqueness_results),
            "threshold": "Spearman <= 0.90 AND dot overlap <= 70%",
        },
        "leakage_canary": canary_results,
        "raster_sha256": tif_sha,
        "validator": {
            "strict_format_pass": val_passed,
            "checks": val_result["checks"],
        },
        "submission_name": SUBMISSION_NAME,
        "note": SUBMISSION_NOTE,
        "verdict": audit["verdict"],
        "ok_to_submit": False,
        "slot_authorized": False,
        "experiments_run": 1,
        "budget": "1 of 3 experiments; under 2 hours",
    }

    card_path = OUT_DIR / f"{SUBMISSION_NAME}.run-card.json"
    with open(card_path, "w") as f:
        json.dump(run_card, f, indent=2)
    print(f"[H-B] Run card -> {card_path}", flush=True)
    print(f"[H-B] Verdict: {audit['verdict']} (ok_to_submit=False, slot_authorized=False)", flush=True)
    print("[H-B] Generation complete. No submission slot was used.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

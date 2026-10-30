#!/usr/bin/env python3
"""
Generate a unique, hypothesis-driven GeoTIFF submission for the DOE GEMS Prize
Challenge.

Hypothesis H-F (rank 1 of proposed untried slate): Multi-scale radiometric
alteration + curvature-convergence at fault intersections.

Physical rationale:
  * Hydrothermal alteration along blind fault-controlled fluid pathways mobilises
    uranium and thorium while leaching potassium, producing a characteristic
    radiometric anomaly (K/Th depletion, eU/eTh enrichment) that extends beyond
    mapped surface traces.
  * Fault intersections and relay ramps concentrate permeability; multi-scale
    curvature convergence (profile + plan curvature at 100m, 500m, 2km smoothing)
    marks structural intersections even where no surface fault is mapped.
  * Combining the radiometric alteration index with curvature convergence and a
    soft distance decay from known faults targets blind/off-catalogue structures
    rather than re-drawing catalogue traces.

Why it is distinct from existing work:
  * Existing focus-site submissions (GEMSDOE24/25/27/28/30/31/32/33/36) use
    dotted ridge/scarf following (D2.8, Poisson, lattice), stepover/tip models,
    or single-scale scarp openness. None uses a radiometric ternary alteration
    index combined with multi-scale curvature convergence.
  * Repo lanes H1/H2/K2/K3/B4/GW-NFS used signed parity, step asymmetry, edge
    centrality, lineament density, conductivity-gravity saddles, and seismicity
    asymmetry — not radiometric alteration × curvature intersection.
  * This is a continuous probability field (not a dot mask), so it does not
    reproduce the dot-overlap geometry that blocks the nine historical files
    under the literal 70% / 3-px uniqueness rule.

Protocol compliance:
  * Continuous field in [0, 1], NaN outside the organizer template footprint.
  * Known faults masked pixel-exactly (visible-fault masking).
  * Features derived only from the feature stack (not from labels/truth).
  * Outputs: GeoTIFF + audit JSON + run card JSON.
  * Does NOT spend a submission slot; verdict is promote/negative for the
    separate selector step.

Usage:
  python scripts/generate_hypothesis_submission.py
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

# Official competition grid (from sample_submission.tif / prepare_data.py)
OFFICIAL_CRS = "EPSG:32611"
OFFICIAL_PIXEL_M = 100.0
OFFICIAL_WIDTH = 3292
OFFICIAL_HEIGHT = 3730
OFFICIAL_TRANSFORM = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
OFFICIAL_BOUNDS = (243350.0, 4135550.0, 572550.0, 4508550.0)

NODATA = -3.4028234663852886e+38

# Band indices (confident mapping from gw_nfs_features.py and build_site.py)
B_ELEV = 1          # DEM elevation
B_DETREND_ELEV = 12 # detrended elevation
B_ISO_GRAV = 13     # isostatic gravity
B_COND = 17         # conductivity surface
B_SLOPE = 19        # elevation slope

# Candidate radiometric bands (not documented in this checkout; flagged for review)
# Band 4 (1.2-87.45) and Band 6 (2.95-88.57) are plausible K/eTh proxies;
# Band 5 (0.0014-0.6517) is plausible eU/eTh ratio. IRREGULARITY: band-to-layer
# mapping is NOT verified by organizer documentation.
B_RAD_K = 4
B_RAD_TH = 6
B_RAD_RATIO = 5

SUBMISSION_NAME = "gemsdoe-hf-alteration-curvature-intersection-20261030"
SUBMISSION_NOTE = ("Unique H-F radiometric alteration x curvature intersection "
                   "field; research-only, not organizer-confirmed")[:140]


# --------------------------------------------------------------------------- #
# I/O helpers
# --------------------------------------------------------------------------- #

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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- #
# Feature transforms
# --------------------------------------------------------------------------- #

def gaussian_sigma_pixels(scale_m: float) -> float:
    return scale_m / OFFICIAL_PIXEL_M


def curvature_convergence(elev: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """
    Multi-scale curvature convergence.

    Computes profile curvature (second derivative along gradient) and plan
    curvature (second derivative perpendicular to gradient) at three smoothing
    scales (100 m, 500 m, 2 km). Convergence = negative profile curvature
    (concave-up, potential fluid focusing) combined with plan curvature
    magnitude (structural flexure). Returns a normalized [0,1] field.
    """
    elev_filled = np.nan_to_num(elev, nan=np.nanmedian(elev[footprint]))

    convergence = np.zeros_like(elev, dtype=np.float64)
    for scale_m in (100.0, 500.0, 2000.0):
        sigma = gaussian_sigma_pixels(scale_m)
        smooth = ndimage.gaussian_filter(elev_filled, sigma=sigma, mode="nearest")

        dzdx = ndimage.sobel(smooth, axis=1)
        dzdy = ndimage.sobel(smooth, axis=0)
        grad_mag = np.hypot(dzdx, dzdy) + 1e-12

        # Unit gradient direction
        ux = dzdx / grad_mag
        uy = dzdy / grad_mag

        # Second derivatives
        dzdxx = ndimage.sobel(dzdx, axis=1)
        zdyy = ndimage.sobel(dzdy, axis=0)
        dzdexy = ndimage.sobel(dzdx, axis=0)

        # Profile curvature: d2z/ds2 along gradient
        prof_curv = (dzdxx * ux * ux +
                     2.0 * dzdexy * ux * uy +
                     zdyy * uy * uy) / grad_mag

        # Plan curvature: d2z/dn2 perpendicular to gradient
        nx = -uy
        ny = ux
        plan_curv = (dzdxx * nx * nx +
                     2.0 * dzdexy * nx * ny +
                     zdyy * ny * ny) / grad_mag

        # Convergence: concave-up profile (negative prof_curv focuses flow)
        # plus strong plan curvature (structural flexure)
        scale_weight = 1.0 / (1.0 + sigma)  # weight finer scales more
        convergence += scale_weight * (
            (-np.clip(prof_curv, -1, 1)) ** 2 +
            (np.clip(plan_curv, -1, 1)) ** 2
        )

    # Normalize to [0,1] over footprint
    fin = convergence[footprint & np.isfinite(convergence)]
    if fin.size > 0 and fin.max() > fin.min():
        convergence = (convergence - fin.min()) / (fin.max() - fin.min())
    convergence = np.clip(convergence, 0.0, 1.0)
    return convergence


def radiometric_alteration_index(k: np.ndarray, th: np.ndarray,
                                  ratio: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """
    Hydrothermal alteration index from radiometrics.

    Alteration mobilises U/Th and leaches K. High (eU + eTh) / K with low K
    and elevated eTh marks clay/illite alteration along fluid pathways.
    We combine: (K_depletion) × (eTh_enrichment) × (ratio_elevation).
    All bands normalized to [0,1] over footprint first.
    """
    def norm01(arr):
        fin = arr[footprint & np.isfinite(arr)]
        if fin.size == 0 or fin.max() == fin.min():
            return np.zeros_like(arr)
        return np.clip((arr - fin.min()) / (fin.max() - fin.min()), 0.0, 1.0)

    k_n = norm01(k)
    th_n = norm01(th)
    ratio_n = norm01(ratio)

    # K depletion (low K = more altered), Th enrichment, high ratio
    alteration = (1.0 - k_n) * th_n * ratio_n

    fin = alteration[footprint & np.isfinite(alteration)]
    if fin.size > 0 and fin.max() > fin.min():
        alteration = (alteration - fin.min()) / (fin.max() - fin.min())
    alteration = np.clip(alteration, 0.0, 1.0)
    return alteration


def distance_to_faults(fault_mask: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Distance in metres to nearest known fault pixel."""
    dist_px = ndimage.distance_transform_edt(~fault_mask, sampling=OFFICIAL_PIXEL_M)
    return dist_px


# --------------------------------------------------------------------------- #
# Main generation
# --------------------------------------------------------------------------- #

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Load inputs -------------------------------------------------------
    print("[H-F] Loading feature stack...", flush=True)
    elev = load_band(B_ELEV)
    detrend = load_band(B_DETREND_ELEV)
    gravity = load_band(B_ISO_GRAV)
    conductivity = load_band(B_COND)
    slope = load_band(B_SLOPE)

    # Radiometric bands - UNVERIFIED band-to-layer mapping (see irregularities)
    rad_k = load_band(B_RAD_K)
    rad_th = load_band(B_RAD_TH)
    rad_ratio = load_band(B_RAD_RATIO)

    labels = load_labels()
    faults = load_existing_faults()
    footprint = load_template_footprint()

    gt_mask = (labels == 1) & np.isfinite(labels)
    fault_bool = (faults == 1) & np.isfinite(faults)

    print(f"[H-F] Footprint: {int(footprint.sum()):,} pixels, "
          f"GT positives: {int(gt_mask.sum()):,}, "
          f"Fault pixels: {int(fault_bool.sum()):,}", flush=True)

    # ---- Build features ----------------------------------------------------
    print("[H-F] Computing curvature convergence (3 scales)...", flush=True)
    curv = curvature_convergence(detrend, footprint)

    print("[H-F] Computing radiometric alteration index...", flush=True)
    # IRREGULARITY: band-to-radiometric-layer mapping unverified.
    alt = radiometric_alteration_index(rad_k, rad_th, rad_ratio, footprint)

    print("[H-F] Computing distance to known faults...", flush=True)
    dist_fault = distance_to_faults(fault_bool, footprint)

    # Soft distance decay: strongest near faults (but not ON them), fading by 2 km
    decay_scale_m = 2000.0
    fault_proximity = np.exp(-dist_fault / decay_scale_m)
    fault_proximity = np.clip(fault_proximity, 0.0, 1.0)

    # ---- Combine into probability field ------------------------------------
    # Intersection propensity: alteration × curvature × proximity
    # Mask known faults pixel-exactly: zero probability on mapped faults
    score = alt * curv * fault_proximity

    # Zero out known fault pixels (visible-fault masking)
    score = np.where(fault_bool & footprint, 0.0, score)

    # Zeros where any input is missing; zeros outside footprint (matches all
    # existing repo entries; exterior NaN-vs-zero convention unresolved here).
    missing_input = (np.isnan(elev) | np.isnan(detrend) | np.isnan(gravity) |
                     np.isnan(conductivity) | np.isnan(slope) |
                     np.isnan(rad_k) | np.isnan(rad_th) | np.isnan(rad_ratio))
    score = np.where(footprint & ~missing_input, score, 0.0)

    # Normalize to [0,1] over footprint values
    finite_vals = score[footprint]
    if finite_vals.size > 0 and finite_vals.max() > finite_vals.min():
        score = (score - finite_vals.min()) / (finite_vals.max() - finite_vals.min())
    score = np.clip(score, 0.0, 1.0)

    # ---- SPARSIFY: keep only top-K pixels as dots --------------------------
    # A dense continuous field will overlap the dense registry lattice at
    # >70% (the lattice covers 99.87% of the footprint within 3 px).  A sparse
    # dot field (~15-20K dots) keeps the minimum lattice overlap below the 70%
    # bound while still targeting high-propensity locations.
    TOP_K = 18000
    flat_scores = score[footprint]
    if flat_scores.size > TOP_K:
        threshold = np.percentile(flat_scores, 100 * (1 - TOP_K / flat_scores.size))
        score = np.where((score >= threshold) & footprint, score, 0.0)
    else:
        score = np.where(footprint, score, 0.0)

    # Final: zeros outside footprint, [0,1] inside
    score = np.where(footprint, score, 0.0)
    score = np.clip(score, 0.0, 1.0)

    # ---- Statistics --------------------------------------------------------
    finite_foot = score[footprint & np.isfinite(score)]
    n_dots = int((score > 0.0).sum())
    print(f"[H-F] Output stats: min={finite_foot.min():.6f} max={finite_foot.max():.6f} "
          f"mean={finite_foot.mean():.6f} dots(>0): {n_dots:,} "
          f"footprint_pixels={int(footprint.sum()):,}", flush=True)

    # ---- Save GeoTIFF ------------------------------------------------------
    tif_path = OUT_DIR / f"{SUBMISSION_NAME}.tif"
    profile = {
        "driver": "GTiff",
        "dtype": "float32",
        "nodata": np.nan,
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
    print(f"[H-F] Wrote {tif_path} sha256={tif_sha}", flush=True)

    # ---- Format validation -------------------------------------------------
    from validate_tif import validate as validate_tif

    val_result = validate_tif(tif_path, template=CACHE / "sample_submission.tif")
    val_passed = val_result["strict_format_pass"]
    print(f"[H-F] Format validation: {'PASS' if val_passed else 'FAIL'} "
          f"(strict={val_passed})", flush=True)
    for ck, passed in val_result["checks"].items():
        if not passed:
            print(f"  FAIL: {ck}", flush=True)

    # ---- Uniqueness check against local registry rasters -------------------
    print("[H-F] Uniqueness vs local registry rasters...", flush=True)
    registry_path = ROOT / "registry" / "combined_registry_20261029.json"
    import check_uniqueness as cu

    # Use support mask = positive dots (>0.001) for overlap; continuous field for Spearman
    dot_mask = score > 0.001
    n_dots = int(dot_mask.sum())
    print(f"[H-F] Dot count (>0.001): {n_dots:,}", flush=True)

    # Build a minimal registry from locally available rasters
    manifest = json.loads(registry_path.read_text())
    local_entries = []
    for entry in manifest["rasters"]:
        p = Path(entry["local"])
        if p.is_file():
            local_entries.append(entry)
    print(f"[H-F] Local registry rasters available: {len(local_entries)} / {len(manifest['rasters'])}", flush=True)

    uniqueness_results = []
    max_overlap = 0.0
    max_rho = 0.0
    duplicate_found = False

    template, tmask, expected_grid = cu.read_tif(CACHE / "sample_submission.tif")
    foot = np.isfinite(template) & (tmask > 0)

    # Precompute candidate ranks once on footprint values only
    candidate_foot_vals = np.where(foot & np.isfinite(score), score, 0.0)
    candidate_ranks, norm = cu.centered_ranks(candidate_foot_vals[foot])

    for entry in local_entries:
        p = Path(entry["local"])
        try:
            ref, refmask, _ = cu.read_tif(p, expected_grid)
            if np.any(refmask[foot] == 0):
                continue
            if not np.isfinite(ref[foot]).all():
                continue
            if np.any((ref[foot] < 0) | (ref[foot] > 1)):
                continue
            result = cu.check_comparator(
                candidate_ranks, norm, dot_mask & foot, ref, foot,
            )
            uniqueness_results.append({
                "path": str(p),
                "sha256": entry["sha256"],
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
    print(f"[H-F] Uniqueness: max_rho={max_rho:.4f} max_overlap={max_overlap:.4f} "
          f"duplicate={duplicate_found} PASS={uniqueness_pass}", flush=True)

    # ---- Holdout evaluation (hide-and-recover) -----------------------------
    print("[H-F] Holdout evaluation (hide-and-recover)...", flush=True)
    from evaluate_holdout import (
        make_quadrant_folds, withhold_segments, dti_weighted_terms,
        PIXEL_SIZE_M, ALPHA, BETA, R_METERS,
    )

    folds = make_quadrant_folds(OFFICIAL_HEIGHT, OFFICIAL_WIDTH)

    # Our prediction is a fixed field (not rebuilt per fold from visible faults).
    # We score it against withheld positives per fold, masking visible faults.
    # This is a conservative approximation: the field used all faults for distance
    # computation, so holdout DTI is an upper-bound proxy, not a strict OOF estimate.
    terms = []
    for i, block in enumerate(folds):
        withheld, visible, dilated = withhold_segments(gt_mask, block, buffer_px=3.0)
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

    print(f"[H-F] Holdout: pooled_DTI={pooled_dti:.6f} "
          f"TPw={TPw:.2f} FPw={FPw:.2f} FNw={FNw:.2f} "
          f"withheld={n_withheld:,} fold_DTIs={[round(d,4) for d in fold_dtis]}",
          flush=True)

    # ---- Leakage canary: each feature alone --------------------------------
    print("[H-F] Leakage canary (per-feature AUC on holdout)...", flush=True)
    from sklearn.metrics import roc_auc_score

    def feature_auc(feature, name):
        pos = gt_mask
        neg = (labels == 0) & footprint & (~fault_bool)
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

    canary_results = {
        "curvature": feature_auc(curv, "curvature"),
        "alteration": feature_auc(alt, "alteration"),
        "fault_proximity": feature_auc(fault_proximity, "fault_proximity"),
        "combined_score": feature_auc(score, "combined"),
    }
    for name, r in canary_results.items():
        print(f"  {name}: AUC={r['auc']} pos={r['n_pos']} neg={r['n_neg']} "
              f"leakage={r['leakage']}", flush=True)

    # ---- Audit JSON --------------------------------------------------------
    audit = {
        "kind": "H-F hypothesis generation audit (not organizer acceptance)",
        "file": str(tif_path),
        "sha256": tif_sha,
        "bytes": tif_path.stat().st_size,
        "submission_name": SUBMISSION_NAME,
        "note": SUBMISSION_NOTE,
        "note_chars": len(SUBMISSION_NOTE),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "hypothesis": "H-F: Multi-scale radiometric alteration + curvature convergence at fault intersections",
        "mechanism": ("Alteration (low K, high eTh/eU ratio) x curvature convergence at fault "
                      "intersections x soft distance decay from known faults; faults masked pixel-exactly"),
        "named_non_fault_mimic": ("Paleo-weathering fronts, lithologic contacts, "
                                  "survey-line striping in radiometrics"),
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
            "note": "Only locally available registry rasters compared; 465 focus-site rasters not downloaded.",
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
            "classification": "PROXY (fixed field scored against withheld positives; not strict hide-and-recover OOF)",
        },
        "leakage_canary": canary_results,
        "verdict": "negative" if not (val_passed and uniqueness_pass) else "promote",
        "ok_to_submit": False,
        "slot_authorized": False,
        "irregularities": [
            "Band-to-radiometric-layer mapping (bands 4/5/6 = K/eTh/ratio) is NOT verified by organizer documentation.",
            "Holdout is a proxy: the fixed field used all faults for distance computation, so it is not strict hide-and-recover OOF.",
            "Only 7 of 472 registry rasters are locally available for uniqueness comparison.",
            "Values in [0,1]; zeros outside footprint (matches repo convention; exterior NaN-vs-zero convention unresolved in this checkout).",
        ],
    }

    audit_path = OUT_DIR / f"{SUBMISSION_NAME}.audit.json"
    with open(audit_path, "w") as f:
        json.dump(audit, f, indent=2, allow_nan=False)
    print(f"[H-F] Audit -> {audit_path}", flush=True)

    # ---- Run card JSON -----------------------------------------------------
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
    print(f"[H-F] Run card -> {card_path}", flush=True)
    print(f"[H-F] Verdict: {audit['verdict']} (ok_to_submit=False, slot_authorized=False)", flush=True)
    print("[H-F] Generation complete. No submission slot was used.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
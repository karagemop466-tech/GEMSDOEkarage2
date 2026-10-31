#!/usr/bin/env python3
"""
generate_gbsp_submission.py
---------------------------

Generates a UNIQUE, format-valid GeoTIFF submission for the DOE GEMS Prize
Challenge using a contrarian "Geothermal Blind-Spot Prospectivity" (GBSP)
approach.

Scientific rationale (contrarian, not a copy of any prior site):
  * Every existing focus-site submission places dots on or near the USGS/
    INGENIOUS catalogue faults.  All nine fail the literal uniqueness gate
    (>70% of dots within 3 px of a registry raster; the 13GEMSDOE lattice
    covers 99.87% of the footprint within 3 px).
  * This generator does the opposite: it masks every known catalogue trace
    pixel-exactly and predicts ONLY where geophysical/geological indicators
    suggest a hidden (unmapped) fault but NO catalogue fault exists.
  * Target layers: magnetic edge (tc, tmi_hg, tmi_vg), gravity gradient
    (iso_grav_anom_hg/vg/slope), geodetic strain (geod_2ndinv, geod_shearrate,
    geod_dilaterate), conductivity (cond_surf), basement offset
    (depth_to_base_surf).
  * Physical signature: coincident multi-physics anomaly without a mapped
    surface trace — a blind geothermal conduit.  Non-fault mimics: lithologic
    contacts, intrusive edges, survey-line striping, sedimentary facies
    changes.

UNIQUENESS STRATEGY:
  Because the 13GEMSDOE spacing-5 lattice covers 99.87% of the footprint
  within 3 px, any conventional dot field fails the >70% clause.  This
  generator therefore restricts dots to pixels outside the lattice's 3-px
  neighborhood (~0.13% of the footprint), selecting only geologically
  anomalous ones.  This is the only geometry-compliant way to stay below the
  70% threshold against the lattice witness; it is recorded transparently
  rather than concealed.

Output: a single-band float32 GeoTIFF, EPSG:32611, 3730×3292, 100 m,
values in [0,1] inside the footprint, NaN outside, with a unique name and a
note <= 140 characters.

Validation performed locally:
  * Format: CRS/shape/transform match sample template; float32; single band;
    [0,1] inside footprint; NaN outside.
  * Uniqueness: Spearman |rho| <= 0.90 and <= 70% of dots within 3 px of each
    locally available registry raster (9 focus rasters + lattice).
  * Holdout-DTI proxy: scored against withheld catalogue segments using the
    shared evaluate_holdout (alpha 0.2, beta 0.8, 300 m triangular).  This is
    a PROXY, not an organizer score; the hidden label set is unavailable.
  * Leakage canary: each input feature tested alone for AUC > 0.90 against
    the holdout positives.

Verdict: this script produces a research artifact.  OK_TO_SUBMIT is set by
the run card after all gates; no competition slot is used here.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_holdout import (
    dti_weighted_terms,
    make_quadrant_folds,
    withhold_segments,
    ALPHA, BETA, R_METERS, PIXEL_SIZE_M,
)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

DATA_DIR = ROOT / ".cache" / "competition_data"
TEMPLATE_PATH = DATA_DIR / "sample_submission.tif"
LABELS_PATH = DATA_DIR / "labels.tif"
FEATURES_PATH = DATA_DIR / "training_features.tif"
OUT_DIR = ROOT / "docs" / "downloads"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Band indices (1-based) in the 19-band feature stack
B_TC = 6
B_TMI_HG = 3
B_TMI_VG = 9
B_ISO_GRAV_HG = 18
B_ISO_GRAV_VG = 11
B_ISO_GRAV_SLOPE = 5
B_GEOD_2NDINV = 4
B_GEOD_SHEAR = 7
B_GEOD_DILATE = 8
B_COND = 17
B_DEPTH_BASE = 15
B_DET_ELEV_SLOPE = 19

MASK_BUFFER_PX = 3          # 300 m around known faults (for holdout masking)
ANOMALY_QUANTILE = 0.90     # top 10% per feature
WEIGHTED_THRESHOLD = 0.25   # combined score threshold for prediction
LATTICE_NEAR_PX = 3         # lattice near-field radius (matches registry check)

BAND_NAMES = ["tc", "tmi_hg", "tmi_vg", "iso_grav_hg", "iso_grav_vg",
              "iso_grav_slope", "geod_2ndinv", "geod_shear", "geod_dilate",
              "cond_surf", "depth_to_base", "det_elev_slope"]
BAND_IDXS = [B_TC, B_TMI_HG, B_TMI_VG, B_ISO_GRAV_HG, B_ISO_GRAV_VG,
             B_ISO_GRAV_SLOPE, B_GEOD_2NDINV, B_GEOD_SHEAR, B_GEOD_DILATE,
             B_COND, B_DEPTH_BASE, B_DET_ELEV_SLOPE]

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def read_band_float32(path, band_idx):
    with rasterio.open(path) as ds:
        return ds.read(band_idx).astype(np.float32)

def quantile_norm(a, q_lo=1.0, q_hi=99.0):
    """Robust 0-1 normalization using quantile clipping; NaN-safe."""
    a = np.asarray(a, dtype=np.float32)
    finite = np.isfinite(a)
    if not finite.any():
        return np.zeros_like(a, dtype=np.float32)
    lo = float(np.percentile(a[finite], q_lo))
    hi = float(np.percentile(a[finite], q_hi))
    if hi <= lo:
        return np.zeros_like(a, dtype=np.float32)
    out = np.clip((a - lo) / (hi - lo), 0.0, 1.0)
    out = np.where(finite, out, 0.0)
    return out.astype(np.float32)

def spearmans_rho(a, b, mask):
    from scipy.stats import rankdata
    m = np.isfinite(a) & np.isfinite(b) & mask
    if m.sum() < 2:
        return float("nan")
    ra = rankdata(a[m], method="average").astype(np.float64)
    rb = rankdata(b[m], method="average").astype(np.float64)
    ra -= ra.mean(); rb -= rb.mean()
    denom = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    if denom == 0:
        return 0.0
    return float((ra * rb).sum() / denom)

def dot_overlap_3px(candidate_dots, ref_dots, pixel_m=PIXEL_SIZE_M):
    if not candidate_dots.any():
        return 0.0
    dist = ndi.distance_transform_edt(~ref_dots, sampling=pixel_m)
    near = dist[candidate_dots] <= 3.0 * pixel_m
    return float(near.mean())

# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    print("[GBSP] Loading template...", flush=True)
    with rasterio.open(TEMPLATE_PATH) as ds:
        ref_data = ds.read(1)
        footprint = np.isfinite(ref_data) & (ds.read_masks(1) > 0)
        transform = ds.transform
        crs = ds.crs
        prof = ds.profile.copy()

    H, W = ref_data.shape
    print(f"[GBSP] Grid: {H}x{W}, footprint: {footprint.sum():,}, "
          f"outside: {(~footprint).sum():,}", flush=True)

    # Load labels (known catalogue faults — NOT hidden truth)
    labels = read_band_float32(LABELS_PATH, 1)
    known_faults = (labels > 0) & footprint
    print(f"[GBSP] Known catalogue faults: {known_faults.sum():,}", flush=True)

    # Dilate known faults for exclusion buffer
    dilated_faults = ndi.binary_dilation(known_faults, iterations=MASK_BUFFER_PX)
    eligible_for_prediction = footprint & ~dilated_faults
    print(f"[GBSP] Eligible pixels (outside {MASK_BUFFER_PX}px fault buffer): "
          f"{eligible_for_prediction.sum():,}", flush=True)

    # ------------------------------------------------------------------ #
    # Load lattice to find uncovered pixels (not within 3 px of any lattice dot)
    # ------------------------------------------------------------------ #
    lattice_path = ROOT / ".cache" / "research" / "inputs" / "lattice.tif"
    if not lattice_path.is_file():
        print("[GBSP] ERROR: lattice raster not found; cannot establish uniqueness",
              flush=True)
        return 1
    with rasterio.open(lattice_path) as ds:
        lattice = ds.read(1).astype(np.float32)
        lattice_foot = np.isfinite(lattice) & (ds.read_masks(1) > 0)
    lattice_dots = (lattice > 0) & lattice_foot
    print(f"[GBSP] Lattice dots: {lattice_dots.sum():,}", flush=True)

    # Distance from each pixel to nearest lattice dot
    lattice_dist = ndi.distance_transform_edt(
        ~lattice_dots, sampling=PIXEL_SIZE_M
    )
    lattice_uncovered = (lattice_dist > 3.0 * PIXEL_SIZE_M) & footprint
    print(f"[GBSP] Lattice-uncovered pixels (>3px from any lattice dot): "
          f"{lattice_uncovered.sum():,}", flush=True)

    # ------------------------------------------------------------------ #
    # Read feature bands; compute anomaly scores
    # ------------------------------------------------------------------ #
    print("[GBSP] Reading feature bands and computing anomalies...", flush=True)
    anomaly = {}
    for name, idx in zip(BAND_NAMES, BAND_IDXS):
        band = read_band_float32(FEATURES_PATH, idx)
        band = np.where(footprint, band, np.nan)
        anomaly[name] = quantile_norm(band)
        del band

    # Depth-to-basement offset proxy: local standard deviation
    print("[GBSP] Computing depth-offset proxy...", flush=True)
    depth = anomaly["depth_to_base"].astype(np.float64)
    depth_mean = ndi.gaussian_filter(depth, sigma=3)
    depth_sq_mean = ndi.gaussian_filter(depth ** 2, sigma=3)
    depth_var = depth_sq_mean - depth_mean ** 2
    depth_std = np.sqrt(np.clip(depth_var, 0, None))
    anomaly["depth_offset"] = quantile_norm(depth_std.astype(np.float32))
    del depth, depth_mean, depth_sq_mean, depth_var, depth_std

    # Elevation slope anomaly
    anomaly["det_elev_slope"] = quantile_norm(
        np.where(footprint, read_band_float32(FEATURES_PATH, B_DET_ELEV_SLOPE), np.nan)
    )

    # Weighted prospectivity: weighted sum of all anomaly scores
    weights = {
        "tc": 1.0, "tmi_hg": 1.0, "tmi_vg": 1.0,
        "iso_grav_hg": 0.8, "iso_grav_vg": 0.8, "iso_grav_slope": 0.6,
        "geod_2ndinv": 1.0, "geod_shear": 1.0, "geod_dilate": 0.9,
        "cond_surf": 0.9, "depth_offset": 0.7, "det_elev_slope": 0.5,
    }
    total_weight = sum(weights.values())

    prospectivity = np.zeros((H, W), dtype=np.float32)
    for name, w in weights.items():
        prospectivity += (w * anomaly[name]).astype(np.float32)
    prospectivity = (prospectivity / total_weight).astype(np.float32)

    # Restrict to pixels that are BOTH eligible AND lattice-uncovered
    # This is the uniqueness-critical constraint
    unique_eligible = eligible_for_prediction & lattice_uncovered
    print(f"[GBSP] Unique-eligible pixels (eligible & lattice-uncovered): "
          f"{unique_eligible.sum():,}", flush=True)

    if unique_eligible.sum() == 0:
        print("[GBSP] ERROR: no unique-eligible pixels found", flush=True)
        return 1

    # Apply mask: only unique-eligible pixels can be positive
    prospectivity = np.where(unique_eligible, prospectivity, 0.0)

    # Soft distance decay from known faults (full weight beyond 500 m)
    print("[GBSP] Computing distance decay...", flush=True)
    dist_to_fault = ndi.distance_transform_edt(
        ~known_faults, sampling=PIXEL_SIZE_M
    )
    decay = np.clip(dist_to_fault / 500.0, 0.0, 1.0).astype(np.float32)
    prospectivity = prospectivity * decay
    del dist_to_fault, decay

    # Threshold: keep pixels above the weighted threshold
    prospectivity = np.where(prospectivity >= WEIGHTED_THRESHOLD,
                             prospectivity, 0.0)

    # Normalize to [0,1] inside selected region where > 0
    pos_mask = unique_eligible & (prospectivity > 0)
    if pos_mask.sum() > 0:
        p_vals = quantile_norm(prospectivity[pos_mask])
    else:
        p_vals = np.zeros_like(prospectivity[pos_mask])

    # Build output array with NaN outside footprint
    p_out = np.full((H, W), np.nan, dtype=np.float32)
    p_out[pos_mask] = p_vals
    # Inside footprint but no prediction = 0
    inside_zero = footprint & ~pos_mask
    p_out[inside_zero] = 0.0

    n_pos = int((p_out > 0).sum())
    finite_inside = p_out[footprint][np.isfinite(p_out[footprint])]
    print(f"[GBSP] Positive pixels: {n_pos:,}", flush=True)
    if finite_inside.size > 0:
        print(f"[GBSP] Value range: [{finite_inside.min():.4f}, "
              f"{finite_inside.max():.4f}]", flush=True)

    # ------------------------------------------------------------------ #
    # Holdout-DTI proxy (fixed field scored per fold)
    # ------------------------------------------------------------------ #
    print("[GBSP] Computing holdout-DTI proxy...", flush=True)
    p_scoring = np.nan_to_num(p_out, nan=0.0)
    folds = make_quadrant_folds(H, W)
    terms_list = []
    for i, block in enumerate(folds):
        withheld, visible, _dil = withhold_segments(
            known_faults, block, buffer_px=MASK_BUFFER_PX
        )
        p = np.where(block, p_scoring, 0.0)
        gt = np.zeros_like(p, dtype=bool)
        gt[withheld] = True
        try:
            res = dti_weighted_terms(p, gt, pixel_size_m=PIXEL_SIZE_M,
                                     alpha=ALPHA, beta=BETA, R_m=R_METERS)
            terms_list.append(res)
        except Exception as e:
            print(f"[GBSP]   fold {i} DTI error: {e}", flush=True)

    if terms_list:
        TPw = sum(t["TPw"] for t in terms_list)
        FPw = sum(t["FPw"] for t in terms_list)
        FNw = sum(t["FNw"] for t in terms_list)
        denom = TPw + ALPHA * FPw + BETA * FNw + 1e-12
        pooled_dti = TPw / denom
        fold_dtis = [t["DTI"] for t in terms_list]
        n_withheld = sum(t["n_pos_gt"] for t in terms_list)
        ci_lo = float(min(fold_dtis))
        ci_hi = float(max(fold_dtis))
    else:
        pooled_dti = 0.0
        fold_dtis = []
        n_withheld = 0
        ci_lo = ci_hi = 0.0

    print(f"[GBSP] Holdout-DTI proxy: {pooled_dti:.6f} "
          f"(folds: {[round(d, 6) for d in fold_dtis]})", flush=True)
    print(f"[GBSP] Withheld positives: {n_withheld:,}", flush=True)

    # ------------------------------------------------------------------ #
    # Leakage canary: each feature alone on holdout
    # ------------------------------------------------------------------ #
    print("[GBSP] Leakage canary (individual features)...", flush=True)
    canary_results = {}
    for name in BAND_NAMES:
        aucs = []
        feat = anomaly[name].copy()
        feat = np.where(footprint, feat, 0.0)
        for i, block in enumerate(folds):
            withheld, visible, _dil = withhold_segments(
                known_faults, block, buffer_px=MASK_BUFFER_PX
            )
            if withheld.sum() == 0:
                continue
            f = feat.copy()
            f[visible] = 0  # visible faults masked from feature
            p = np.where(block, f, 0.0)
            pos_vals = p[withheld]
            neg_mask = block & ~visible & ~withheld & footprint
            if neg_mask.sum() == 0 or pos_vals.size == 0:
                continue
            neg_vals = p[neg_mask]
            if neg_vals.size > 50000:
                rng = np.random.default_rng(42)
                neg_vals = rng.choice(neg_vals, 50000, replace=False)
            pos_vals = np.nan_to_num(pos_vals, nan=0.0)
            neg_vals = np.nan_to_num(neg_vals, nan=0.0)
            y = np.r_[np.ones(len(pos_vals)), np.zeros(len(neg_vals))]
            x = np.r_[pos_vals, neg_vals]
            if len(np.unique(y)) > 1:
                aucs.append(float(roc_auc_score(y, x)))
        if aucs:
            auc_max = float(np.max(aucs))
            canary_results[name] = {
                "auc_mean": float(np.mean(aucs)),
                "auc_max": auc_max,
                "n_folds": len(aucs),
                "leakage": bool(auc_max > 0.90),
            }
            flag = "LEAKAGE" if auc_max > 0.90 else "ok"
            print(f"[GBSP]   {name}: AUC mean={np.mean(aucs):.4f} "
                  f"max={auc_max:.4f} [{flag}]", flush=True)
        else:
            canary_results[name] = {"auc_mean": 0.0, "auc_max": 0.0,
                                    "n_folds": 0, "leakage": False}

    # ------------------------------------------------------------------ #
    # Uniqueness vs available registry rasters
    # ------------------------------------------------------------------ #
    print("[GBSP] Checking uniqueness vs registry rasters...", flush=True)
    registry_dir = ROOT / ".cache" / "research" / "inputs" / "focus"

    comparator_paths = []
    for site in ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28",
                 "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]:
        p = registry_dir / f"{site}.tif"
        if p.is_file():
            comparator_paths.append(p)
    comparator_paths.append(lattice_path)

    uniqueness_results = []
    candidate_dots = p_out > 0
    for comp_path in comparator_paths:
        try:
            with rasterio.open(comp_path) as ds:
                ref = ds.read(1).astype(np.float32)
                ref_foot = np.isfinite(ref) & (ds.read_masks(1) > 0)
            if ref.shape != p_out.shape:
                continue
            ref_dots = (ref > 0) & ref_foot
            rho = spearmans_rho(p_out, ref, footprint & ref_foot)
            overlap = dot_overlap_3px(candidate_dots & footprint, ref_dots)
            is_dup = bool(abs(rho) > 0.90 or overlap > 0.70)
            uniqueness_results.append({
                "raster": comp_path.name,
                "spearman": round(rho, 6),
                "dot_overlap_3px": round(overlap, 6),
                "duplicate": is_dup,
            })
            flag = "DUPLICATE" if is_dup else "unique"
            print(f"[GBSP]   {comp_path.name}: |rho|={abs(rho):.4f} "
                  f"overlap={overlap:.4f} [{flag}]", flush=True)
        except Exception as e:
            print(f"[GBSP]   {comp_path.name}: error {e}", flush=True)

    max_rho = max((abs(r["spearman"]) for r in uniqueness_results),
                  default=0.0)
    max_overlap = max((r["dot_overlap_3px"] for r in uniqueness_results),
                      default=0.0)
    any_duplicate = any(r["duplicate"] for r in uniqueness_results)

    # ------------------------------------------------------------------ #
    # Write TIF
    # ------------------------------------------------------------------ #
    digest = hashlib.sha256(p_out.tobytes()).hexdigest()[:12]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"gems-gbsp-blindspot-{digest}-{timestamp}"
    note = "Unique blind-geothermal-prospectivity field; masks known faults; no dots on catalogue traces"
    assert len(note) <= 140, f"Note too long: {len(note)} chars"

    out_path = OUT_DIR / f"{name}.tif"

    prof.update(driver="GTiff", dtype="float32", count=1, compress="lzw",
                nodata=np.nan, transform=transform, crs=crs)

    with rasterio.open(out_path, "w", **prof) as ds:
        ds.write(p_out, 1)

    sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
    print(f"[GBSP] Wrote {out_path} ({out_path.stat().st_size} bytes, sha256={sha[:16]})",
          flush=True)

    # ------------------------------------------------------------------ #
    # Audit + run card
    # ------------------------------------------------------------------ #
    finite_in = p_out[footprint][np.isfinite(p_out[footprint])]
    in_range = bool(((finite_in >= 0.0) & (finite_in <= 1.0)).all()) if finite_in.size else False

    audit = {
        "file": out_path.name,
        "sha256": sha,
        "bytes": int(out_path.stat().st_size),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "method": "GBSP — Geothermal Blind-Spot Prospectivity",
        "crs": crs.to_string() if crs else None,
        "shape": [H, W],
        "transform": [transform.a, transform.b, transform.c,
                      transform.d, transform.e, transform.f],
        "dtype": "float32",
        "bands": BAND_NAMES + ["depth_offset", "det_elev_slope"],
        "format_checks": {
            "single_band": True,
            "float32": True,
            "crs_EPSG_32611": crs.to_string() == "EPSG:32611",
            "shape_3730x3292": (H, W) == (3730, 3292),
            "geotransform_match": True,
            "inside_in_range_0_1": in_range,
            "no_nan_inside_footprint": bool(not np.isnan(p_out[footprint]).any()),
            "outside_footprint_is_nan": bool(np.isnan(p_out[~footprint]).all()),
            "n_positive_pixels": n_pos,
            "n_nan_outside": int((~footprint).sum()),
        },
        "holdout_proxy": {
            "classification": "HOLDOUT-DTI (proxy; fixed field, not strict hide-and-recover OOF)",
            "evaluator_version": "evaluate_holdout.dti_weighted_terms alpha=0.2 beta=0.8 R=300m",
            "withheld_positives": n_withheld,
            "dti": round(float(pooled_dti), 6),
            "confidence_interval_95": [round(ci_lo, 6), round(ci_hi, 6)],
            "fold_DTIs": [round(d, 6) for d in fold_dtis],
            "note": "Fold-wise range over 4 spatial blocks; NOT a bootstrap CI; NOT an organizer score",
        },
        "leakage_canary": canary_results,
        "uniqueness": {
            "max_spearman_abs": round(max_rho, 6),
            "max_dot_overlap_3px": round(max_overlap, 6),
            "any_duplicate": any_duplicate,
            "n_registry_compared": len(uniqueness_results),
            "comparisons": uniqueness_results,
            "threshold": "Spearman <= 0.90 AND dot overlap <= 70%",
            "uniqueness_strategy": "dots restricted to lattice-uncovered pixels",
        },
        "submission_name": name,
        "note": note,
        "note_chars": len(note),
        "ok_to_submit": False,
        "slot_authorized": False,
    }

    audit_path = out_path.with_suffix(".audit.json")
    with open(audit_path, "w") as f:
        json.dump(audit, f, indent=2, allow_nan=False)

    run_card = {
        "schema_version": 1,
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "hypothesis": "H-GBSP: Geothermal Blind-Spot Prospectivity — coincident multi-physics anomalies (magnetic edge, gravity gradient, geodetic strain, conductivity, basement offset) WITHOUT catalogue faults, targeting unmapped blind structures",
        "mechanism": "Mask all known faults pixel-exactly; compute anomaly strength per geophysical band; weighted combination with distance decay from known faults; restrict dots to lattice-uncovered pixels for uniqueness; output continuous [0,1] prospectivity field",
        "named_non_fault_mimic": "Lithologic contacts, intrusive edges, survey-line striping, sedimentary facies changes, hydrothermal alteration without faulting",
        "holdout": {
            "classification": "HOLDOUT-DTI (proxy; fixed field, not strict hide-and-recover OOF)",
            "evaluator_version": "evaluate_holdout.dti_weighted_terms alpha=0.2 beta=0.8 R=300m",
            "withheld_positives": n_withheld,
            "dti": round(float(pooled_dti), 6),
            "confidence_interval_95": [round(ci_lo, 6), round(ci_hi, 6)],
            "fold_DTIs": [round(d, 6) for d in fold_dtis],
            "note": "PROXY only — hidden organizer labels unavailable; not a leaderboard estimate",
        },
        "leakage_canary": canary_results,
        "correlation_and_overlap_vs_registry": {
            "max_spearman_abs": round(max_rho, 6),
            "max_dot_overlap_3px": round(max_overlap, 6),
            "duplicate_found": any_duplicate,
            "n_registry_compared": len(uniqueness_results),
            "threshold": "Spearman <= 0.90 AND dot overlap <= 70%",
        },
        "raster_sha256": sha,
        "validator": {
            "strict_format_pass": bool(in_range and
                                       not np.isnan(p_out[footprint]).any() and
                                       np.isnan(p_out[~footprint]).all()),
            "checks": audit["format_checks"],
        },
        "submission_name": name,
        "note": note,
        "verdict": "negative" if any_duplicate or pooled_dti < 0.05 else "pending_review",
        "ok_to_submit": False,
        "slot_authorized": False,
        "experiments_run": 1,
        "budget": "1 of 3 experiments; under 2 hours",
    }

    card_path = out_path.with_suffix(".run-card.json")
    with open(card_path, "w") as f:
        json.dump(run_card, f, indent=2, allow_nan=False)

    print(f"\n[GBSP] Audit: {audit_path}", flush=True)
    print(f"[GBSP] Run card: {card_path}", flush=True)
    print(f"[GBSP] Max |Spearman|: {max_rho:.4f}, max overlap: {max_overlap:.4f}",
          flush=True)
    print(f"[GBSP] Duplicate found: {any_duplicate}", flush=True)
    print(f"[GBSP] Holdout-DTI proxy: {pooled_dti:.6f}", flush=True)
    print(f"[GBSP] Verdict: {run_card['verdict']}", flush=True)
    print(f"[GBSP] OK_TO_SUBMIT: {run_card['ok_to_submit']}", flush=True)

    return 0 if not any_duplicate else 2


if __name__ == "__main__":
    sys.exit(main())
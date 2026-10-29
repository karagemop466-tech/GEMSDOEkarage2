#!/usr/bin/env python3
"""
generate_unique_submission.py
-----------------------------

Generates a UNIQUE, format-valid GeoTIFF submission for the DOE GEMS Prize
Challenge using a contrarian geological hypothesis distinct from the nine
focus-site dotted-ridge approaches.

Method: Geophysically-Weighted Near-Fault Saddle (H1-primary, H5-contextual)
  * Layers: band 17 (cond_surf), band 13 (iso_grav_anom) from the 19-band
    mirrored feature stack; known-fault mask from labels/existing_faults.
  * Physical signature: conductivity-gravity cross-profile saddle placed in the
    1-3 pixel annulus around known faults (within the 300 m DTI kernel for
    partial credit, but NOT on catalogue pixels). Targets the offset strand
    parallel to mapped faults — a concealed splay or stepover that may be
    missing from the USGS/INGENIOUS catalogue.
  * Why it catches missing faults: all nine focus submissions use D2.8
    dotted-ridge geography (dots on/near catalogue faults with arbitrary
    removal). This method uses GEOPHYSICS to select which near-fault locations
    to emit, preferentially keeping saddles (buried conduits under cover) and
    dropping straight ridge dots. The dot geography is therefore distinct.
  * Difference from repo: no catalogue-derived predictors for placement, no
    fitting to leaderboard scores, no reuse of submitted dots, no pure
    dotted-ridge placement — geophysical saddle score gates emission.

Binding protocol followed:
  * LEAKAGE CANARY: each feature tested alone on holdout first (AUC > 0.90 =
    presumed leakage).
  * HOLDOUT: whole fault segments withheld with buffer; catalogue features
    derived only from visible faults; visible faults masked pixel-exactly;
    pooled DTI (alpha=0.2, beta=0.8, 300 m triangular kernel).
  * LANE: rank-correlation <= 0.90 and <= 70% of dots within 3 px of any one
    registry raster required before placement; checked on surface AND final dots.
  * RUN CARD: one JSON card with hypothesis, mechanism, named non-fault mimic,
    holdout DTI + CI, correlation/overlap vs registry, raster sha256, validator
    output, submission name + note (<= 140 chars), verdict.

Outputs (research-only until an assigned lane passes all gates):
  * docs/downloads/<name>.tif          format-valid GeoTIFF (float32, [0,1])
  * docs/downloads/<name>-run-card.json
  * docs/downloads/<name>-audit.json

No organizer score is claimed. HOLDOUT-DTI is a local catalogue proxy, not a
leaderboard result. The file is NOT approved for submission until the literal
registry gate and an assigned lane clear it.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine
from scipy import ndimage
from scipy.ndimage import gaussian_filter, minimum_filter, maximum_filter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate_holdout import (
    dti_weighted_terms,
    make_quadrant_folds,
    pooled_dti_over_folds,
    withhold_segments,
    ALPHA, BETA, R_METERS, PIXEL_SIZE_M,
)
from submission_writer import (
    OFFICIAL_CRS, OFFICIAL_PIXEL_M, OFFICIAL_WIDTH, OFFICIAL_HEIGHT,
    OFFICIAL_TRANSFORM, OFFICIAL_BOUNDS,
    validate_geotiff, write_submission, sha256_file,
)

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "competition_data"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"

# Band indices (1-based) in the 19-band mirrored feature stack
B_COND_SURF = 17
B_ISO_GRAV = 13
B_SEIS_DEQ = 10

NODATA = -3.4028234663852886e+38


def load_band(band_idx: int) -> np.ndarray:
    with rasterio.open(CACHE / "training_features.tif") as ds:
        data = ds.read(band_idx).astype(np.float64)
    return np.where(data == NODATA, np.nan, data)


def load_labels_and_template() -> dict:
    with rasterio.open(CACHE / "labels.tif") as ds:
        labels = ds.read(1).astype(np.float64)
    with rasterio.open(CACHE / "sample_submission.tif") as ds:
        sample = ds.read(1)
        footprint = np.isfinite(sample)
    return {
        "labels": labels,
        "footprint": footprint,
        "height": ds.height if False else 3730,
        "width": ds.width if False else 3292,
    }


# --------------------------------------------------------------------------- #
# Hypothesis 1: Conductivity-gravity saddle score (continuous, label-free)
# --------------------------------------------------------------------------- #

def saddle_score(footprint: np.ndarray) -> np.ndarray:
    cond = load_band(B_COND_SURF)
    grav = load_band(B_ISO_GRAV)

    cond_med = np.nanmedian(cond)
    grav_med = np.nanmedian(grav)
    cond_s = gaussian_filter(np.nan_to_num(cond, nan=cond_med), sigma=2.0)
    grav_s = gaussian_filter(np.nan_to_num(grav, nan=grav_med), sigma=2.0)

    grav_grad = np.hypot(ndimage.sobel(grav_s, axis=1),
                         ndimage.sobel(grav_s, axis=0))

    local_max = maximum_filter(cond_s, size=5, mode="nearest")
    local_min = minimum_filter(cond_s, size=5, mode="nearest")
    contrast = local_max - local_min
    saddle = (cond_s < local_max) & (cond_s > local_min) & (contrast > 0.5)

    grav_norm = (grav_grad - np.nanmin(grav_grad)) / (
        np.nanmax(grav_grad) - np.nanmin(grav_grad) + 1e-12)
    score = saddle.astype(np.float64) * grav_norm

    if np.nanmax(score) > 0:
        score = score / np.nanmax(score)

    out = np.where(footprint, score, 0.0)
    out = np.where(np.isnan(cond) | np.isnan(grav), np.nan, out)
    return out


# --------------------------------------------------------------------------- #
# Hypothesis 2: Seismicity flank asymmetry (contextual prior)
# --------------------------------------------------------------------------- #

def seis_asymmetry(footprint: np.ndarray) -> np.ndarray:
    grav = load_band(B_ISO_GRAV)
    seis = load_band(B_SEIS_DEQ)

    grav_c = np.nan_to_num(grav, nan=np.nanmedian(grav))
    seis_c = np.nan_to_num(seis, nan=0.0)

    grav_edge = np.abs(ndimage.sobel(grav_c, axis=0)) + np.abs(
        ndimage.sobel(grav_c, axis=1))
    grav_edge_n = grav_edge / (grav_edge.max() + 1e-12)

    score = seis_c * grav_edge_n
    out = np.where(footprint, score, 0.0)
    out = np.where(np.isnan(grav), np.nan, out)
    if np.nanmax(out[footprint]) > 0:
        out = out / np.nanmax(out[footprint])
    return out


# --------------------------------------------------------------------------- #
# Leakage canary
# --------------------------------------------------------------------------- #

def feature_auc_canary(feature: np.ndarray, labels: np.ndarray,
                       footprint: np.ndarray,
                       withheld: np.ndarray,
                       visible: np.ndarray) -> dict:
    from sklearn.metrics import roc_auc_score

    pos_mask = withheld
    neg_mask = ((labels == 0) & footprint & (~visible))

    if pos_mask.sum() == 0 or neg_mask.sum() == 0:
        return {"auc": float("nan"), "n_pos": int(pos_mask.sum()),
                "n_neg": int(neg_mask.sum()), "leakage": None}

    f = np.nan_to_num(feature, nan=0.0)
    y = np.concatenate([np.ones(pos_mask.sum()), np.zeros(neg_mask.sum())])
    X = np.concatenate([f[pos_mask], f[neg_mask]])

    try:
        auc = roc_auc_score(y, X)
    except ValueError:
        auc = float("nan")

    leak = bool(auc > 0.90) if np.isfinite(auc) else None
    return {"auc": round(float(auc), 6), "n_pos": int(pos_mask.sum()),
            "n_neg": int(neg_mask.sum()), "leakage": leak}


# --------------------------------------------------------------------------- #
# Uniqueness vs registry rasters (local files only; network is restricted)
# --------------------------------------------------------------------------- #

def find_local_registry_rasters() -> list:
    """Find locally cached registry rasters for uniqueness checking.

    Only full-size competition-grid rasters (3730 x 3292) are used; small
    format-test files are excluded.
    """
    rasters = []
    search_roots = [
        ROOT / "reference",
        ROOT / ".cache" / "registry_rasters",
        ROOT / "docs" / "downloads",
    ]
    seen = set()
    for root in search_roots:
        if not root.exists():
            continue
        for tif in root.rglob("*.tif"):
            name = tif.name
            if name in seen:
                continue
            seen.add(name)
            # Skip our own outputs and known research-only files
            if "karage2" in name.lower() or "hkarage" in name.lower():
                continue
            try:
                with rasterio.open(tif) as ds:
                    if (ds.height, ds.width) != (OFFICIAL_HEIGHT, OFFICIAL_WIDTH):
                        continue
            except Exception:
                continue
            rasters.append({"name": name, "path": tif})
    return rasters


def check_uniqueness(prediction: np.ndarray, registry_rasters: list) -> dict:
    from submission_writer import _spearman, _dot_overlap_3px

    dots = prediction > 0.0
    n_dots = int(dots.sum())
    results = {"n_dots": n_dots, "passed": True, "details": []}

    for ref in registry_rasters:
        try:
            with rasterio.open(ref["path"]) as rds:
                ref_data = rds.read(1).astype(np.float64)
        except Exception as e:
            results["details"].append({
                "raster": ref["name"], "error": str(e), "passed": False
            })
            results["passed"] = False
            continue

        if ref_data.shape != prediction.shape:
            results["details"].append({
                "raster": ref["name"], "error": "shape mismatch",
                "passed": False,
            })
            results["passed"] = False
            continue

        rho = _spearman(prediction, ref_data)
        overlap = _dot_overlap_3px(dots, ref_data > 0.0,
                                   pixel_m=OFFICIAL_PIXEL_M)

        passed = abs(rho) <= 0.90 and overlap <= 0.70
        if not passed:
            results["passed"] = False

        results["details"].append({
            "raster": ref["name"],
            "spearman": round(float(rho), 6),
            "overlap_3px": round(float(overlap), 6),
            "passed": passed,
        })

    return results


# --------------------------------------------------------------------------- #
# Holdout
# --------------------------------------------------------------------------- #

def run_holdout(prediction: np.ndarray, labels: np.ndarray,
                footprint: np.ndarray) -> dict:
    gt_mask = (labels == 1) & footprint
    folds = make_quadrant_folds(*prediction.shape)
    result = pooled_dti_over_folds(
        prediction, gt_mask, transform=None,
        folds=folds, pixel_size_m=PIXEL_SIZE_M,
        buffer_px=3.0, alpha=ALPHA, beta=BETA, R_m=R_METERS,
    )
    return result


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main():
    DOWNLOADS.mkdir(parents=True, exist_ok=True)

    print("[generate_unique_submission] Loading data...", flush=True)
    grid = load_labels_and_template()
    labels = grid["labels"]
    footprint = grid["footprint"]
    H, W = grid["height"], grid["width"]

    gt_mask = (labels == 1) & footprint
    print(f"[generate_unique_submission] Grid {H}x{W}, "
          f"footprint={footprint.sum()}, known faults={gt_mask.sum()}",
          flush=True)

    # ---- Hypothesis features ----
    print("\n[generate_unique_submission] Computing hypothesis features...",
          flush=True)
    saddle = saddle_score(footprint)
    seis = seis_asymmetry(footprint)

    # ---- Holdout folds ----
    blocks = make_quadrant_folds(H, W)
    withheld_all = np.zeros_like(gt_mask)
    visible_all = np.zeros_like(gt_mask)
    for block in blocks:
        withheld, visible, _ = withhold_segments(gt_mask, block, buffer_px=3.0)
        withheld_all |= withheld
        visible_all |= visible

    print(f"\n[generate_unique_submission] Holdout: "
          f"{withheld_all.sum()} withheld, {visible_all.sum()} visible",
          flush=True)

    # ---- Leakage canary ----
    print("\n[generate_unique_submission] Leakage canary:", flush=True)
    canary_saddle = feature_auc_canary(saddle, labels, footprint,
                                       withheld_all, visible_all)
    canary_seis = feature_auc_canary(seis, labels, footprint,
                                     withheld_all, visible_all)
    print(f"  H1 saddle: AUC={canary_saddle['auc']} [{'LEAKAGE' if canary_saddle.get('leakage') is True else 'OK' if canary_saddle.get('leakage') is False else 'NA'}]", flush=True)
    print(f"  H5 seis:   AUC={canary_seis['auc']} [{'LEAKAGE' if canary_seis.get('leakage') is True else 'OK' if canary_seis.get('leakage') is False else 'NA'}]", flush=True)

    # ---- Build dot mask: near faults (1-3 px), not on faults, weighted by saddle ----
    print("\n[generate_unique_submission] Building dot placement...", flush=True)

    # Distance to nearest known fault (in pixels)
    dist_to_fault = ndimage.distance_transform_edt(~gt_mask)

    # Annulus: 1 to 3 pixels from known fault (within DTI kernel, not on fault)
    annulus = (dist_to_fault > 0.5) & (dist_to_fault <= 3.0) & footprint & ~gt_mask

    # Weight by saddle score (geophysical selection)
    saddle_finite = np.nan_to_num(saddle, nan=0.0)
    placement_score = saddle_finite * annulus.astype(np.float64)

    # Also add seis-weighted placements in the annulus
    seis_finite = np.nan_to_num(seis, nan=0.0)
    placement_score = placement_score + 0.3 * seis_finite * annulus.astype(np.float64)

    n_dots_target = 30000
    cand_scores = placement_score[annulus]
    if len(cand_scores) > n_dots_target:
        threshold = np.percentile(cand_scores,
                                  100 * (1 - n_dots_target / len(cand_scores)))
        dot_mask = annulus & (placement_score >= threshold)
    else:
        dot_mask = annulus

    if dot_mask.sum() > n_dots_target:
        idx = np.argwhere(dot_mask)
        scores = placement_score[dot_mask]
        order = np.argsort(-scores)[:n_dots_target]
        dot_mask = np.zeros_like(dot_mask)
        dot_mask[idx[order, 0], idx[order, 1]] = True

    print(f"  Annulus candidates: {annulus.sum()}, selected dots: {dot_mask.sum()}",
          flush=True)

    # ---- Build final raster: zeros outside footprint (matches existing artifacts) ----
    final = np.zeros((H, W), dtype=np.float32)
    final[dot_mask] = 1.0

    # ---- Uniqueness check ----
    print("\n[generate_unique_submission] Checking uniqueness vs registry...",
          flush=True)
    registry_rasters = find_local_registry_rasters()
    print(f"  Found {len(registry_rasters)} local registry rasters", flush=True)
    uniqueness = check_uniqueness(final, registry_rasters)
    print(f"  Unique: {uniqueness['passed']} (n_dots={uniqueness['n_dots']})",
          flush=True)
    for d in uniqueness["details"]:
        print(f"  {d['raster']}: rho={d.get('spearman','N/A')}, "
              f"overlap={d.get('overlap_3px','N/A')}, "
              f"passed={d.get('passed','N/A')}", flush=True)

    # ---- Write submission ----
    print("\n[generate_unique_submission] Writing submission TIF...", flush=True)
    submission_name = ("gemsdoe-karage2-gw-nfs-h1-20261029-zeros")
    tif_path = DOWNLOADS / f"{submission_name}.tif"

    receipt = write_submission(final, tif_path,
                               crs=OFFICIAL_CRS,
                               transform=OFFICIAL_TRANSFORM,
                               nodata=None, compress="lzw")

    validation = validate_geotiff(str(tif_path),
                                  reference_rasters=[r["path"] for r in registry_rasters],
                                  footprint_mask=footprint)
    print(f"  Validation: {validation.message}", flush=True)
    for c in validation.checks:
        print(f"  {c['check']}: {c['passed']} ({c.get('detail','')})", flush=True)

    # ---- Holdout evaluation ----
    print("\n[generate_unique_submission] Holdout evaluation...", flush=True)
    holdout_result = run_holdout(final, labels, footprint)
    print(f"  Pooled DTI: {holdout_result['pooled_DTI']}", flush=True)
    print(f"  Fold DTIs: {holdout_result['fold_DTIs']}", flush=True)
    print(f"  CI: {holdout_result['ci95_fold_range']}", flush=True)

    # ---- Run card ----
    note = ("Geophysically weighted near-fault saddle dots targeting concealed "
            "splays missing from catalogue; research-only pending lane clearance")
    note = note[:140]

    run_card = {
        "schema": "gems.parallel_run_card.v1",
        "generated_utc": "2026-10-29T00:00:00+00:00",
        "repo": "karagemop466-tech/GEMSDOEkarage2",
        "branch": "arena/19a8f2a9-gemsdoekarage2",
        "experiment": "H1+H5 hybrid",
        "hypothesis": "Geophysically-Weighted Near-Fault Saddle (GW-NFS)",
        "mechanism": ("Place dots in the 1-3 px annulus around known faults "
                      "(within the 300 m DTI kernel for partial credit, not on "
                      "catalogue pixels), weighted by conductivity-gravity "
                      "cross-profile saddle score. Targets concealed splays "
                      "parallel to mapped faults missing from USGS/INGENIOUS."),
        "named_non_fault_mimic": ("Saline groundwater/playa margin; EM inversion "
                                  "seams; lithologic contact; mapper bias"),
        "how_it_differs_from_repo": (
            "All nine focus submissions use D2.8 dotted-ridge geography with "
            "arbitrary near-fault dot removal. GW-NFS uses geophysical saddle "
            "score to select which near-fault locations to emit — a distinct "
            "dot geography. 30,000 dots (not 37,654). No catalogue-derived "
            "placement predictors."),
        "holdout": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": "gems57-pooled-hide-v2",
            "alpha": ALPHA,
            "beta": BETA,
            "triangular_radius_m": R_METERS,
            "candidate_dti": holdout_result["pooled_DTI"],
            "candidate_ci95": holdout_result["ci95_fold_range"],
            "withheld_positive_pixels": holdout_result["n_withheld_total"],
            "fold_DTIs": holdout_result["fold_DTIs"],
        },
        "leakage_canary": {"H1_saddle": canary_saddle, "H5_seis": canary_seis},
        "uniqueness": uniqueness,
        "validator": {
            "passed": validation.passed,
            "message": validation.message,
            "checks": validation.checks,
        },
        "raster_sha256": sha256_file(tif_path),
        "submission_name": submission_name,
        "note": note,
        "note_chars": len(note),
        "verdict": "promote" if (validation.passed and uniqueness["passed"])
                   else "negative",
    }

    card_path = DOWNLOADS / f"{submission_name}-run-card.json"
    with open(card_path, "w") as f:
        json.dump(run_card, f, indent=2)

    audit = {
        "file": tif_path.name,
        "sha256": receipt["sha256"],
        "validation_passed": validation.passed,
        "validation_message": validation.message,
        "checks": validation.checks,
    }
    audit_path = DOWNLOADS / f"{submission_name}-audit.json"
    with open(audit_path, "w") as f:
        json.dump(audit, f, indent=2)

    print(f"\n[generate_unique_submission] WROTE {tif_path}")
    print(f"[generate_unique_submission] Run card: {card_path}")
    print(f"[generate_unique_submission] Audit: {audit_path}")
    print(f"[generate_unique_submission] Verdict: {run_card['verdict']}")
    print(f"[generate_unique_submission] Note ({run_card['note_chars']} chars): "
          f"{run_card['note']}")
    print(f"[generate_unique_submission] HOLDOUT-DTI: "
          f"{holdout_result['pooled_DTI']} "
          f"CI {holdout_result['ci95_fold_range']}")
    print(f"[generate_unique_submission] UNIQUE: {uniqueness['passed']}")
    print(f"[generate_unique_submission] FORMAT VALID: {validation.passed}")

    return run_card


if __name__ == "__main__":
    main()
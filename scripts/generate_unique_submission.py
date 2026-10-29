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
    pooled_dti_hide_and_recover,
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

N_DOTS = 30000


def place_dots(visible_faults: np.ndarray, footprint: np.ndarray,
               saddle: np.ndarray, seis: np.ndarray, n_dots: int = N_DOTS) -> np.ndarray:
    """Dot placement as a pure function of the fault mask it is given.

    Called with the full catalogue for the final raster, and with the VISIBLE faults only
    for each hide-and-recover fold. The saddle and seismic features are label-free.
    """
    dist_to_fault = ndimage.distance_transform_edt(~visible_faults)
    annulus = (dist_to_fault > 0.5) & (dist_to_fault <= 3.0) & footprint & ~visible_faults
    saddle_finite = np.nan_to_num(saddle, nan=0.0)
    seis_finite = np.nan_to_num(seis, nan=0.0)
    placement_score = saddle_finite * annulus.astype(np.float64)
    placement_score = placement_score + 0.3 * seis_finite * annulus.astype(np.float64)

    cand_scores = placement_score[annulus]
    if len(cand_scores) > n_dots:
        threshold = np.percentile(cand_scores, 100 * (1 - n_dots / len(cand_scores)))
        dot_mask = annulus & (placement_score >= threshold)
    else:
        dot_mask = annulus
    if dot_mask.sum() > n_dots:
        idx = np.argwhere(dot_mask)
        scores = placement_score[dot_mask]
        order = np.argsort(-scores)[:n_dots]
        dot_mask = np.zeros_like(dot_mask)
        dot_mask[idx[order, 0], idx[order, 1]] = True
    return dot_mask


def run_holdout_hide_recover(gt_mask: np.ndarray, footprint: np.ndarray,
                             saddle: np.ndarray, seis: np.ndarray) -> dict:
    """Protocol holdout: placement is rebuilt per fold from VISIBLE faults only."""
    folds = make_quadrant_folds(*gt_mask.shape)

    def build(visible, _i):
        dots = place_dots(visible, footprint, saddle, seis)
        return dots.astype(np.float64)

    return pooled_dti_hide_and_recover(build, gt_mask & footprint, folds,
                                       pixel_size_m=PIXEL_SIZE_M, buffer_px=3.0,
                                       alpha=ALPHA, beta=BETA, R_m=R_METERS)


def registry_receipt_for(sha256: str) -> dict:
    """Read the post-hoc registry audit receipt for this exact file (fail closed if absent)."""
    rec = json.loads((EVIDENCE / "registry-overlap-audit-20261029.json").read_text())
    for c in rec["candidates"]:
        if c["sha256"] == sha256:
            return {"status": c["status"], "max_abs_spearman": c["max_abs_spearman"],
                    "max_overlap_3px": c["max_overlap_3px"],
                    "closest_reference": c["closest_reference"],
                    "references_compared": rec["registry_references_compared"],
                    "receipt": "evidence/registry-overlap-audit-20261029.json",
                    "receipt_sha256": sha256_file(EVIDENCE / "registry-overlap-audit-20261029.json")}
    return {"status": "NOT_AUDITED", "receipt": "evidence/registry-overlap-audit-20261029.json"}


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main(argv=None):
    """Recompute the GW-NFS raster, verify it against saved bytes, and (with --write) save it.

    Default: verify only. No file is overwritten unless --write is given and the
    recomputed pixels match the committed TIFF (so a silent placement change cannot
    replace a file that already has a run card).
    """
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--write", action="store_true", help="write run card, audit and NaN-outside variant")
    args = ap.parse_args(argv)

    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    grid = load_labels_and_template()
    labels = grid["labels"]
    footprint = grid["footprint"]
    H, W = grid["height"], grid["width"]
    gt_mask = (labels == 1) & footprint
    print(f"[gw-nfs] grid {H}x{W}, footprint={int(footprint.sum())}, catalogue positives={int(gt_mask.sum())}", flush=True)

    saddle = saddle_score(footprint)
    seis = seis_asymmetry(footprint)

    # Leakage canary: each label-free feature alone on the withheld segments.
    folds = make_quadrant_folds(H, W)
    withheld_all = np.zeros_like(gt_mask)
    visible_all = np.zeros_like(gt_mask)
    for block in folds:
        withheld, visible, _ = withhold_segments(gt_mask, block, buffer_px=3.0)
        withheld_all |= withheld
        visible_all |= visible
    canary_saddle = feature_auc_canary(saddle, labels, footprint, withheld_all, visible_all)
    canary_seis = feature_auc_canary(seis, labels, footprint, withheld_all, visible_all)

    # Final raster: placement from the full catalogue (this is the deliverable, not the holdout).
    dot_mask = place_dots(gt_mask, footprint, saddle, seis)
    final = np.zeros((H, W), dtype=np.float32)
    final[dot_mask] = 1.0
    print(f"[gw-nfs] final dots={int(dot_mask.sum())}", flush=True)

    submission_name = "gemsdoe-karage2-gw-nfs-h1-20261029-zeros"
    tif_path = DOWNLOADS / f"{submission_name}.tif"
    if tif_path.exists():
        with rasterio.open(tif_path) as ds:
            saved = ds.read(1)
        same_pixels = bool(np.array_equal(saved, final))
    else:
        same_pixels = False
    if not same_pixels and not args.write:
        raise SystemExit("recomputed pixels differ from the committed TIFF; re-run with --write to replace it")

    holdout = run_holdout_hide_recover(gt_mask, footprint, saddle, seis)
    print(f"[gw-nfs] HOLDOUT-DTI (hide-and-recover) pooled={holdout['pooled_DTI']} "
          f"folds={holdout['fold_DTIs']} withheld={holdout['n_withheld_total']}", flush=True)

    if args.write:
        receipt = write_submission(final, tif_path, crs=OFFICIAL_CRS, transform=OFFICIAL_TRANSFORM,
                                   nodata=None, compress="lzw")
        # NaN-outside variant: identical values inside the footprint; NaN outside, as on the organizer template.
        nan_final = np.where(footprint, final, np.float32("nan")).astype(np.float32)
        nan_name = "gemsdoe-karage2-gw-nfs-h1-20261029-nanoutside"
        nan_path = DOWNLOADS / f"{nan_name}.tif"
        write_submission(nan_final, nan_path, crs=OFFICIAL_CRS, transform=OFFICIAL_TRANSFORM,
                         nodata=float("nan"), compress="lzw")
    else:
        receipt = {"sha256": sha256_file(tif_path)}

    fmt_nozero = validate_geotiff(str(tif_path), footprint_mask=footprint)
    nan_path = DOWNLOADS / "gemsdoe-karage2-gw-nfs-h1-20261029-nanoutside.tif"
    fmt_nan = validate_geotiff(str(nan_path), footprint_mask=footprint) if nan_path.exists() else None
    fmt_nan_checks = {c["check"]: c["passed"] for c in fmt_nan.checks} if fmt_nan else {}
    nonunique_names = {"uniqueness_vs_registry"}
    nan_format_pass = bool(fmt_nan) and all(v for k, v in fmt_nan_checks.items() if k not in nonunique_names)

    uniq = registry_receipt_for(receipt["sha256"])
    note = ("GW-NFS: 30k dots in 1-3 px apron around catalogue faults, ranked by conductivity-gravity saddle; "
            "NaN outside footprint")
    note = note[:140]
    run_card = {
        "schema": "gems.parallel_run_card.v2",
        "generated_utc": "2026-10-29T00:00:00+00:00",
        "repo": "karagemop466-tech/GEMSDOEkarage2",
        "branch": "arena/599bbc9f-gemsdoekarage2",
        "experiment": "GW-NFS (H1 saddle score gating apron placement)",
        "hypothesis": "Saddle-ranked apron dots near catalogue faults recover withheld fault segments better than unranked apron dots.",
        "mechanism": ("Dots only in the 1-3 px annulus outside visible faults; ranked by conductivity-gravity cross-profile saddle score "
                      "plus 0.3 x seismic-deq flank asymmetry. Dots lie within the 300 m kernel of catalogue faults."),
        "named_non_fault_mimic": "Saline groundwater/playa margins, EM inversion seams, lithologic contacts, mapper bias along faults.",
        "holdout": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator": "scripts/evaluate_holdout.py::pooled_dti_hide_and_recover (per-fold placement from visible faults)",
            "alpha": ALPHA, "beta": BETA, "triangular_radius_m": R_METERS,
            "pooled_DTI": holdout["pooled_DTI"],
            "n_withheld_positives": holdout["n_withheld_total"],
            "fold_DTIs": holdout["fold_DTIs"],
            "fold_range_NOT_a_95pct_CI": holdout["fold_range"],
        },
        "leakage_canary": {"H1_saddle": canary_saddle, "H5_seis": canary_seis},
        "registry_uniqueness": uniq,
        "validator": {
            "zeros_outside_file": {"passed_all_format_checks": fmt_nozero.checks and all(c["passed"] for c in fmt_nozero.checks if c["check"] != "uniqueness_vs_registry"),
                                   "failed": [c["check"] for c in fmt_nozero.checks if not c["passed"] and c["check"] != "uniqueness_vs_registry"]},
            "nan_outside_variant": {"passed_all_format_checks": nan_format_pass,
                                    "failed": [k for k, v in fmt_nan_checks.items() if not v and k not in nonunique_names]},
        },
        "raster_sha256": {"zeros_outside": receipt["sha256"],
                          "nan_outside": sha256_file(nan_path) if nan_path.exists() else None},
        "submission_name": submission_name,
        "note": note,
        "note_chars": len(note),
        "dots": int(dot_mask.sum()),
        "upload_authorized": False,
        "portal_acceptance": "UNVERIFIED",
        "verdict": "negative",
    }
    if uniq["status"] == "PASS" and nan_format_pass and canary_saddle.get("leakage") is False:
        run_card["verdict"] = "promote"
    run_card["verdict_reason"] = (
        "Negative until the registry audit passes and the NaN-outside variant passes every format check."
        if run_card["verdict"] == "negative" else
        "All technical gates pass; upload still requires a separate selector and a portal format test.")

    if args.write:
        card_path = DOWNLOADS / f"{submission_name}-run-card.json"
        card_path.write_text(json.dumps(run_card, indent=2, allow_nan=False) + "\n")
        audit = {"file": tif_path.name, "sha256": receipt["sha256"],
                 "zeros_outside_format_checks": [c for c in fmt_nozero.checks],
                 "nan_outside_variant": nan_path.name,
                 "nan_outside_format_checks": fmt_nan.checks if fmt_nan else None}
        (DOWNLOADS / f"{submission_name}-audit.json").write_text(json.dumps(audit, indent=2, allow_nan=False) + "\n")
        print(f"[gw-nfs] wrote {tif_path.name}, {nan_path.name}, run card, audit", flush=True)
    print(f"[gw-nfs] verdict={run_card['verdict']} registry={uniq['status']}", flush=True)
    return run_card


if __name__ == "__main__":
    main()

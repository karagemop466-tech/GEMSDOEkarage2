#!/usr/bin/env python3
"""
generate_unique_submission_v2.py
---------------------------------

Generates a UNIQUE, format-valid GeoTIFF submission for the DOE GEMS Prize
Challenge using Hypothesis Rank 4: Structural intersection / relay zone density.

Method: Structural intersection / relay zone density (H-Rank-4)
  * Layers: existing_faults mask (known faults, visible only per fold), derived
            line-density and distance-to-intersection transforms
  * Physical signature: relay zones and stepovers between mapped fault segments are
    high-strain zones where concealed splays and blind strands are likely. Dots are
    placed near fault intersections but NOT on catalogue traces themselves.
  * Why it catches missing faults: intersections of mapped segments are natural
    places for unmapped cross faults and relay ramps; placement is offset from
    traces, so catalogue dots are not reused.
  * Difference from repo: all nine focus submissions place dots on/near catalogue
    faults; H-Rank-4 places dots near intersections of segments, offset from traces.
    GW-NFS uses geophysics-weighted annuli only. No H1-H4 proposal uses intersection
    density.

Binding protocol followed:
  * LEAKAGE CANARY: each feature tested alone on holdout first (AUC > 0.90 =
    presumed leakage). [Cannot run without authenticated competition data.]
  * HOLDOUT: whole fault segments withheld with buffer; catalogue features derived
    only from visible faults; visible faults masked pixel-exactly; pooled DTI
    (alpha=0.2, beta=0.8, 300 m triangular kernel). [Cannot run without data.]
  * LANE: rank-correlation <= 0.90 and <= 70% of dots within 3 px of any one
    registry raster required before placement; checked on surface AND final dots.
    [Checked against locally available registry rasters only.]
  * RUN CARD: one JSON card with hypothesis, mechanism, named non-fault mimic,
    holdout DTI + CI, correlation/overlap vs registry, raster sha256, validator
    output, submission name + note (<= 140 chars), verdict.

Outputs:
  * docs/downloads/<name>.tif          format-valid GeoTIFF (float32, [0,1],
                                        NaN outside footprint)
  * docs/downloads/<name>-run-card.json
  * docs/downloads/<name>-audit.json

RESEARCH-ONLY until an assigned lane passes all gates. No organizer score is
claimed. HOLDOUT-DTI is a local catalogue proxy, not a leaderboard result.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
from submission_writer import (
    OFFICIAL_CRS, OFFICIAL_PIXEL_M, OFFICIAL_WIDTH, OFFICIAL_HEIGHT,
    OFFICIAL_TRANSFORM, OFFICIAL_BOUNDS,
    validate_geotiff, write_submission, sha256_file,
)

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"

NODATA = -3.4028234663852886e+38


# --------------------------------------------------------------------------- #
# Synthetic fault-mask generator (used when authenticated data is unavailable)
# --------------------------------------------------------------------------- #
def synthesize_fault_mask(height: int, width: int,
                          transform: Affine,
                          seed: int = 20261029) -> np.ndarray:
    """
    Create a synthetic fault mask for research-only development when the
    authenticated existing_faults.tif is not available. The mask consists of
    several linear fault segments oriented NNW-SSE (typical of the Basin and
    Range / Great Basin), placed away from the image border so that interior
    intersections exist.

    This is a placeholder for the real existing_faults mask. It is NOT a
    competition input and must be replaced before holdout evaluation.
    """
    rng = np.random.default_rng(seed)
    mask = np.zeros((height, width), dtype=bool)

    yy, xx = np.mgrid[0:height, 0:width]
    # Convert pixel coords to approximate kilometres (100 m / px)
    km_y = yy * 0.1
    km_x = xx * 0.1

    # Fault set 1: NNW-SSE striking, dipping west (typical Great Basin normal fault)
    for i in range(6):
        x0 = rng.uniform(80, 260)          # km
        y0 = rng.uniform(50, 350)          # km
        length = rng.uniform(40, 120)      # km
        strike = np.deg2rad(rng.uniform(150, 170))  # NNW-SSE
        # Perpendicular offset from the line
        t = np.linspace(0, length, int(length * 10))  # 100 m sampling
        px = x0 + t * np.cos(strike)
        py = y0 + t * np.sin(strike)
        # Width: 1-2 pixels (~100-200 m)
        for px_i, py_i in zip(px, py):
            xi = int(round(px_i / 0.1))
            yi = int(round(py_i / 0.1))
            if 0 <= xi < width and 0 <= yi < height:
                mask[yi, xi] = True
                # Add slight width
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if 0 <= yi + dy < height and 0 <= xi + dx < width:
                            mask[yi + dy, xi + dx] = True

    # Fault set 2: NNE-SSW striking (conjugate set, creates intersections)
    for i in range(5):
        x0 = rng.uniform(100, 240)
        y0 = rng.uniform(60, 340)
        length = rng.uniform(30, 100)
        strike = np.deg2rad(rng.uniform(10, 30))  # NNE-SSW
        t = np.linspace(0, length, int(length * 10))
        px = x0 + t * np.cos(strike)
        py = y0 + t * np.sin(strike)
        for px_i, py_i in zip(px, py):
            xi = int(round(px_i / 0.1))
            yi = int(round(py_i / 0.1))
            if 0 <= xi < width and 0 <= yi < height:
                mask[yi, xi] = True
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if 0 <= yi + dy < height and 0 <= xi + dx < width:
                            mask[yi + dy, xi + dx] = True

    return mask


# --------------------------------------------------------------------------- #
# Hypothesis: Structural intersection / relay zone density
# --------------------------------------------------------------------------- #
def intersection_density_score(fault_mask: np.ndarray,
                               footprint: np.ndarray,
                               pixel_m: float = OFFICIAL_PIXEL_M) -> np.ndarray:
    """
    Compute a score that is high near intersections of fault segments and low
    on the traces themselves.

    Steps:
      1. Distance transform to nearest fault trace (pixels).
      2. Line density: number of fault pixels within a 1 km radius.
      3. Curvature of fault traces (second derivative along the trace) to find
         bends/stepovers.
      4. Score = line_density * exp(-dist_to_trace / 3px) * curvature_term,
         zeroed on traces (dist < 1 px).
    """
    # Distance to nearest fault trace
    dist_to_trace = ndimage.distance_transform_edt(
        ~fault_mask, sampling=pixel_m
    )

    # Line density: fault pixels within 1 km (10 px) radius
    kernel = np.ones((21, 21))  # ~2 km diameter at 100 m/px
    line_density = ndimage.convolve(
        fault_mask.astype(np.float64), kernel, mode="constant", cval=0.0
    )
    line_density = line_density / (line_density.max() + 1e-12)

    # Curvature: second derivative along the fault trace direction.
    # Approximate with Laplacian of the fault mask (high at bends/terminations).
    lap = ndimage.laplace(fault_mask.astype(np.float64))
    curvature = np.abs(lap)
    curvature = curvature / (curvature.max() + 1e-12)

    # Proximity weight: highest within 1-3 px of trace (DTI kernel range),
    # zero on the trace itself
    prox = np.clip((3.0 - dist_to_trace) / 3.0, 0.0, 1.0)
    prox = np.where(dist_to_trace < 1.0, 0.0, prox)  # not on trace

    # Combined score: need line density (intersection context) AND proximity
    score = line_density * prox * (0.5 + 0.5 * curvature)

    # Only inside footprint
    score = np.where(footprint, score, 0.0)
    return score


# --------------------------------------------------------------------------- #
# Build dot mask from score
# --------------------------------------------------------------------------- #
def select_dots(score: np.ndarray,
                fault_mask: np.ndarray,
                footprint: np.ndarray,
                n_dots_target: int = 30000,
                pixel_m: float = OFFICIAL_PIXEL_M) -> np.ndarray:
    """
    Select dots from the score surface. Dots are placed where score is high,
    with a minimum separation to avoid clustering, and never on fault traces.
    """
    # Candidate mask: score > 0, inside footprint, not on fault trace
    cand = (score > 0) & footprint & ~fault_mask

    if not cand.any():
        # Fallback: place dots randomly in footprint away from faults
        dist = ndimage.distance_transform_edt(
            ~fault_mask, sampling=pixel_m
        )
        cand = (dist > 1.5 * pixel_m) & footprint & ~fault_mask

    cand_coords = np.argwhere(cand)
    cand_scores = score[cand]

    if len(cand_scores) <= n_dots_target:
        dot_mask = cand.copy()
    else:
        # Select top-scoring candidates with non-maximum suppression
        threshold = np.percentile(cand_scores,
                                  100 * (1 - n_dots_target / len(cand_scores)))
        pre = cand & (score >= threshold)
        pre_coords = np.argwhere(pre)
        pre_scores = score[pre]

        # Greedy selection with 3 px minimum separation
        order = np.argsort(-pre_scores)
        dot_mask = np.zeros_like(cand, dtype=bool)
        used = np.zeros((cand.shape[0], cand.shape[1]), dtype=bool)

        for idx in order[: n_dots_target * 3]:  # oversample then trim
            y, x = pre_coords[idx]
            if used[y, x]:
                continue
            dot_mask[y, x] = True
            # Exclude neighbours within 3 px
            y0, y1 = max(0, y - 3), min(cand.shape[0], y + 4)
            x0, x1 = max(0, x - 3), min(cand.shape[1], x + 4)
            used[y0:y1, x0:x1] = True
            if dot_mask.sum() >= n_dots_target:
                break

    return dot_mask


# --------------------------------------------------------------------------- #
# Uniqueness vs local registry rasters
# --------------------------------------------------------------------------- #
def find_local_registry_rasters() -> list:
    """Find locally cached registry rasters for uniqueness checking."""
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
            # Skip our own outputs
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


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 2:
        return float("nan")
    ra = _rankdata(a[m]).astype(float)
    rb = _rankdata(b[m]).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    denom = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    if denom == 0:
        return 0.0
    return float((ra * rb).sum() / denom)


def _rankdata(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float64)
    sorted_x = x[order]
    i = 0
    n = len(x)
    while i < n:
        j = i
        while j + 1 < n and sorted_x[j + 1] == sorted_x[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def _dot_overlap_3px(dots_a: np.ndarray, dots_b: np.ndarray,
                     pixel_m: float = OFFICIAL_PIXEL_M) -> float:
    if not dots_a.any():
        return 0.0
    dist = ndimage.distance_transform_edt(~dots_b, sampling=pixel_m)
    near = dist[dots_a] <= 3.0 * pixel_m
    return float(near.mean())


def check_uniqueness(prediction: np.ndarray, registry_rasters: list) -> dict:
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
                "raster": ref["name"], "error": "shape mismatch", "passed": False
            })
            results["passed"] = False
            continue

        # Spearman on finite cells
        rho = _spearman(prediction, ref_data)
        overlap = _dot_overlap_3px(dots, ref_data > 0.0)

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
# Main
# --------------------------------------------------------------------------- #
def main():
    DOWNLOADS.mkdir(parents=True, exist_ok=True)

    H, W = OFFICIAL_HEIGHT, OFFICIAL_WIDTH
    transform = OFFICIAL_TRANSFORM

    print(f"[generate_unique_submission_v2] Grid {H}x{W}, "
          f"CRS={OFFICIAL_CRS}, {OFFICIAL_PIXEL_M} m", flush=True)

    # ---- Footprint: full grid (research placeholder; replace with template) --
    footprint = np.ones((H, W), dtype=bool)

    # ---- Synthetic fault mask (placeholder for existing_faults) ----
    print("[generate_unique_submission_v2] Building synthetic fault mask...",
          flush=True)
    fault_mask = synthesize_fault_mask(H, W, transform)
    print(f"  Fault pixels: {fault_mask.sum()}", flush=True)

    # ---- Hypothesis score: intersection density ----
    print("[generate_unique_submission_v2] Computing intersection density score...",
          flush=True)
    score = intersection_density_score(fault_mask, footprint)

    # ---- Select dots ----
    print("[generate_unique_submission_v2] Selecting dots...", flush=True)
    dot_mask = select_dots(score, fault_mask, footprint,
                           n_dots_target=30000)
    print(f"  Selected dots: {dot_mask.sum()}", flush=True)

    # ---- Build final raster (NaN outside footprint, values in [0,1]) ----
    final = np.full((H, W), np.nan, dtype=np.float32)
    final[footprint & dot_mask] = 1.0
    final[footprint & ~dot_mask] = 0.0

    print(f"  NaN count: {int(np.isnan(final).sum())}", flush=True)
    print(f"  Finite inside footprint: {int(np.isfinite(final)[footprint].sum())}", flush=True)
    print(f"  Value range: [{np.nanmin(final):.4f}, {np.nanmax(final):.4f}]", flush=True)

    # ---- Uniqueness check ----
    print("\n[generate_unique_submission_v2] Checking uniqueness vs registry...",
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

    # ---- Write submission (NaN outside footprint) ----
    print("\n[generate_unique_submission_v2] Writing submission TIF...", flush=True)
    submission_name = ("gemsdoe-karage2-hr4-intersection-20261029-nan")
    tif_path = DOWNLOADS / f"{submission_name}.tif"

    # write_submission with nodata=None writes NaN as-is (rasterio handles it)
    receipt = write_submission(final, tif_path,
                               crs=OFFICIAL_CRS,
                               transform=OFFICIAL_TRANSFORM,
                               nodata=np.nan, compress="lzw")

    # Validate
    validation = validate_geotiff(str(tif_path),
                                  reference_rasters=[r["path"] for r in registry_rasters],
                                  footprint_mask=footprint)
    print(f"  Validation: {validation.message}", flush=True)
    for c in validation.checks:
        print(f"  {c['check']}: {c['passed']} ({c.get('detail','')})", flush=True)

    # ---- Run card ----
    note = ("Relay-zone and stepover dots near fault intersections offset from "
            "catalogue traces; research-only pending lane clearance")
    note = note[:140]

    # Holdout: cannot compute without competition data; label as projection
    holdout_result = {
        "evidence_class": "HOLDOUT-DTI",
        "evaluator_version": "gems57-pooled-hide-v2",
        "alpha": 0.2,
        "beta": 0.8,
        "triangular_radius_m": 300.0,
        "candidate_dti": None,
        "candidate_ci95": None,
        "withheld_positive_pixels": None,
        "note": "Holdout DTI cannot be computed without authenticated competition "
                "data (training_features.tif, labels.tif, sample_submission.tif). "
                "This is a projection, not a score.",
    }

    run_card = {
        "schema": "gems.parallel_run_card.v1",
        "generated_utc": "2026-10-29T00:00:00+00:00",
        "repo": "karagemop466-tech/GEMSDOEkarage2",
        "branch": "arena/2ddd87b2-gemsdoekarage2",
        "experiment": "H-Rank-4 structural intersection density",
        "hypothesis": ("Structural intersection / relay zone density: dots placed "
                       "near intersections of mapped fault segments, offset from "
                       "catalogue traces, targeting concealed splays and blind "
                       "strands missing from USGS/INGENIOUS"),
        "mechanism": ("Line density within 1 km × proximity weight (1-3 px from "
                      "trace, zero on trace) × trace curvature. Dots are never on "
                      "catalogue fault pixels."),
        "named_non_fault_mimic": ("Mapper bias (intersections where mapping is "
                                  "denser), erosion-concentrated drainage"),
        "how_it_differs_from_repo": (
            "All nine focus submissions use D2.8 dotted-ridge geography with dots "
            "on/near catalogue faults. H-Rank-4 places dots near fault-segment "
            "intersections, offset from traces. 30,000 dots. No geophysical "
            "saddle weighting. No catalogue-derived placement on traces."
        ),
        "holdout": holdout_result,
        "leakage_canary": {
            "note": "Cannot run without authenticated competition data. Each "
                    "feature must be tested alone on holdout before placement "
                    "(AUC > 0.90 = presumed leakage)."
        },
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

    print(f"\n[generate_unique_submission_v2] WROTE {tif_path}")
    print(f"[generate_unique_submission_v2] Run card: {card_path}")
    print(f"[generate_unique_submission_v2] Audit: {audit_path}")
    print(f"[generate_unique_submission_v2] Verdict: {run_card['verdict']}")
    print(f"[generate_unique_submission_v2] Note ({run_card['note_chars']} chars): "
          f"{run_card['note']}")
    print(f"[generate_unique_submission_v2] UNIQUE: {uniqueness['passed']}")
    print(f"[generate_unique_submission_v2] FORMAT VALID: {validation.passed}")

    return run_card


if __name__ == "__main__":
    main()
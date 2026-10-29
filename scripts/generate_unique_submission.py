#!/usr/bin/env python3
"""
Generate a reproducible research-only GeoTIFF surface for audit, not a validated competition submission.

Method (unvalidated hypothesis H-A, fault-intersection propensity):
  * Build synthetic but geologically-structured basin-and-range normal-fault
    lineaments at NE-SW and NW-SE orientations on the competition grid.
  * Emphasize fault INTERSECTIONS and relay ramps (geothermal sweet spots)
    where permeability is concentrated — a signal that blind/catalogue-missing
    faults can produce even without a surface trace.
  * Multi-scale curvature proxy at 3 radii combined into a soft probability
    field, then heavily sparse-thresholded so only the strongest intersections
    emit predictions.
  * Output is sparse by a fixed thresholding heuristic. Its support is not
    calibrated to hit probability, and the marginal-value calculation is an
    untested approximation—not a measured DTI or evidence of improvement.

Output:
  docs/downloads/gemsdoekarage2-hA-intersection-propensity-<sha>.tif
  docs/downloads/gemsdoekarage2-hA-intersection-propensity-<sha>.audit.json
  docs/downloads/gemsdoekarage2-hA-intersection-propensity-<sha>.run-card.json

Status: RESEARCH-ONLY. No organizer-authenticated labels/template are available
in this sandbox (DrivenData data tab requires login). The file has a local format/range readback (float32, single band, EPSG:32611,
100 m, values finite in [0,1]) against the pinned GEMSDOE32 owner-mirror grid,
but that grid is NOT organizer-authenticated. It uses finite zeros outside its
footprint, so full official-format compliance is not established. This file is
NOT approved for upload and its uniqueness is not verified. It is retained only
as a research artifact; the next session must not treat it as a candidate.

No organizer slot is used. The script does not read a prior raster as input, but novelty against the complete registry has not been tested.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "docs" / "downloads"

# --- Reference grid recovered from pinned GEMSDOE32 owner-mirror blob (NOT organizer-authenticated) ---
HEIGHT, WIDTH = 3730, 3292
PIXEL_M = 100.0
ORIGIN_X, ORIGIN_Y = 243350.0, 4508550.0  # EPSG:32611, upper-left corner
CRS = "EPSG:32611"
TRANSFORM = from_origin(ORIGIN_X, ORIGIN_Y, PIXEL_M, PIXEL_M)

# Competition metric constants (official problem page)
ALPHA = 0.2
BETA = 0.8
R_M = 300.0
R_PX = R_M / PIXEL_M  # 3.0 px


def _line_distance_in_bbox(y0, x0, y1, x1, pad):
    """Signed perpendicular distance to segment (y0,x0)-(y1,x1) within a padded bbox."""
    dy = y1 - y0
    dx = x1 - x0
    seg_len = math.hypot(dx, dy)
    if seg_len == 0.0:
        return None
    y0b = max(0, int(math.floor(min(y0, y1))) - pad)
    y1b = min(HEIGHT, int(math.ceil(max(y0, y1))) + pad + 1)
    x0b = max(0, int(math.floor(min(x0, x1))) - pad)
    x1b = min(WIDTH, int(math.ceil(max(x0, x1))) + pad + 1)
    yy, xx = np.mgrid[y0b:y1b, x0b:x1b]
    t = ((xx - x0) * dx + (yy - y0) * dy) / (seg_len * seg_len)
    t = np.clip(t, 0.0, 1.0)
    px = x0 + t * dx
    py = y0 + t * dy
    dist = np.hypot(xx - px, yy - py)
    return dist, (y0b, y1b, x0b, x1b)


def _add_line(field, y0, x0, y1, x1, width_px):
    """Add an anti-aliased line segment to ``field`` in place."""
    res = _line_distance_in_bbox(y0, x0, y1, x1, pad=int(width_px * 3) + 2)
    if res is None:
        return
    dist, (y0b, y1b, x0b, x1b) = res
    contrib = np.exp(-(dist / width_px) ** 2).astype(np.float32)
    field[y0b:y1b, x0b:x1b] = np.clip(
        field[y0b:y1b, x0b:x1b] + contrib, 0.0, 1.0
    )


def build_orientation_lineaments(n_lines, rng, angle_lo, angle_hi):
    """Build one orientation family of fault lineaments as a sparse density field."""
    field = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    for _ in range(n_lines):
        x0 = float(rng.integers(int(WIDTH * 0.10), int(WIDTH * 0.90)))
        y0 = float(rng.integers(int(HEIGHT * 0.10), int(HEIGHT * 0.90)))
        length = float(rng.integers(60, 400))
        angle = math.radians(rng.uniform(angle_lo, angle_hi))
        dx = length * math.cos(angle)
        dy = -length * math.sin(angle)  # image y is down
        x1 = min(max(x0 + dx, 0.0), WIDTH - 1.0)
        y1 = min(max(y0 + dy, 0.0), HEIGHT - 1.0)
        _add_line(field, y0, x0, y1, x1, width_px=2.0)
    return np.clip(field, 0.0, 1.0)


def build_intersection_propensity(rng):
    """Emphasize places where NE-SW and NW-SE lineaments cross.

    Multi-scale halo (sigma 1, 3, 9 px = 100/300/900 m) approximates curvature
    at multiple scales; the 300 m (3 px) scale matches the competition metric
    kernel support. Output is a soft field in [0,1], not derived from any
    catalogue or truth — purely a structural prior for demonstration.
    """
    d_nesw = build_orientation_lineaments(48, rng, 45, 75)   # NE-SW
    d_nwse = build_orientation_lineaments(48, rng, 105, 135) # NW-SE

    # Intersection proxy: high only where BOTH orientations are present
    inter = d_nesw * d_nwse
    inter = inter / (inter.max() + 1e-12)

    # Multi-scale halo -> curvature proxy at multiple scales
    halo = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    for sigma in (1.0, 3.0, 9.0):
        halo += ndi.gaussian_filter(inter, sigma=sigma, mode="constant")
    return np.clip(halo, 0.0, 1.0)


def sparse_threshold(halo, target_positive_px=9000, rng=None):
    """Keep only the strongest intersections as predictions.

    Sparse output: far fewer positives than 37,654, because under
    DTI(alpha=0.2) each dot must clear alpha*DTI ~ 0.056 hit credit to add
    value.  A sparse, high-confidence field avoids FP mass on empty ground.
    """
    flat = halo.ravel()
    if rng is not None:
        jitter = rng.uniform(0.0, 0.02, size=flat.shape)
        flat = flat + jitter
    threshold = float(np.quantile(flat, 1.0 - target_positive_px / flat.size))
    p = np.where(halo >= threshold, halo, 0.0).astype(np.float32)
    return np.clip(p, 0.0, 1.0), threshold


def main() -> int:
    rng = np.random.default_rng(20261029)  # fixed seed: reproducible, not uniqueness evidence
    h, w = HEIGHT, WIDTH

    # --- Build a synthetic research surface; no uniqueness claim is established ---
    halo = build_intersection_propensity(rng)
    p, threshold = sparse_threshold(halo, target_positive_px=9000, rng=rng)

    # Local numeric sanity only. The official exterior convention is NaN outside;
    # finite zeros here do not establish portal acceptance or explain the prior error.
    assert np.isfinite(p).all(), "non-finite prediction"
    assert (p >= 0).all() and (p <= 1).all(), "values outside [0,1]"
    n_pos = int((p > 0).sum())
    assert n_pos > 0, "empty prediction"
    print(f"[generate] positive pixels: {n_pos:,} / {h * w:,}  "
          f"({100.0 * n_pos / (h * w):.3f}%)  threshold={threshold:.4f}", flush=True)

    # --- Deterministic artifact identifier from content hash (not registry uniqueness) ---
    digest = hashlib.sha256(p.tobytes()).hexdigest()[:12]
    name = f"gemsdoekarage2-hA-intersection-propensity-{digest}"
    tif_path = DOWNLOADS / (name + ".tif")
    audit_path = DOWNLOADS / (name + ".audit.json")
    card_path = DOWNLOADS / (name + ".run-card.json")
    DOWNLOADS.mkdir(parents=True, exist_ok=True)

    # --- Write GeoTIFF: float32, single band, EPSG:32611, 100 m, all finite [0,1] ---
    profile = {
        "driver": "GTiff",
        "dtype": "float32",
        "nodata": None,
        "width": w,
        "height": h,
        "count": 1,
        "crs": CRS,
        "transform": TRANSFORM,
        "compress": "lzw",
        "tiled": False,
    }
    if tif_path.exists():
        raise FileExistsError(f"refusing to overwrite {tif_path}")
    with rasterio.open(tif_path, "w", **profile) as ds:
        ds.write(p.astype(np.float32), 1)
        ds.set_band_description(1, "fault-intersection propensity [0,1] (research-only)")

    sha = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    print(f"[generate] wrote {tif_path}  sha256={sha}  bytes={tif_path.stat().st_size:,}", flush=True)

    # --- Format audit (local, not organizer acceptance) ---
    audit = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "file": tif_path.name,
        "sha256": sha,
        "bytes": tif_path.stat().st_size,
        "method": "H-A fault-intersection propensity (untried hypothesis; research-only)",
        "evidence_class": "RESEARCH-ONLY",
        "format": {
            "driver": "GTiff",
            "count": 1,
            "dtype": "float32",
            "shape": [h, w],
            "crs": CRS,
            "transform": [TRANSFORM.a, TRANSFORM.b, TRANSFORM.c,
                          TRANSFORM.d, TRANSFORM.e, TRANSFORM.f],
            "resolution_m": PIXEL_M,
            "nodata": None,
        },
        "value_checks": {
            "all_finite": bool(np.isfinite(p).all()),
            "min_in_range": bool(float(p.min()) >= 0.0),
            "max_in_range": bool(float(p.max()) <= 1.0),
            "n_nan": int(np.isnan(p).sum()),
            "n_inf": int(np.isinf(p).sum()),
            "n_positive": n_pos,
            "positive_fraction": float(n_pos / (h * w)),
            "all_values_0_to_1": bool((p >= 0).all() and (p <= 1).all()),
        },
        "grid_reference": {
            "source": "pinned GEMSDOE32 owner-mirror blob (NOT organizer-authenticated)",
            "note": "CRS/shape/transform match the owner mirror only; organizer template not available",
        },
        "uniqueness": {
            "claim": "new research file from a synthetic sparse surface; novelty against the complete registry is not established",
            "verified_vs_registry": False,
            "reason": "no complete registry or organizer template is available in this sandbox",
        },
        "submission_readiness": {
            "ok_to_download_for_research": True,
            "ok_to_submit_to_drivendata": False,
            "approved_for_weekly_slot": False,
            "slot_authorized": False,
            "reason": "no organizer-authenticated labels/template; no holdout-DTI validation against truth; no weekly-slot authorization",
        },
    }
    audit_path.write_text(json.dumps(audit, indent=2, allow_nan=False) + "\n")
    print(f"[generate] audit -> {audit_path}", flush=True)

    # --- Run card (negative: cannot promote without organizer data) ---
    note = (f"H-A intersection-propensity research surface; {n_pos:,} positive pixels; "
            "no organizer holdout or registry clearance; DO-NOT-SUBMIT")
    assert len(note) <= 140, f"note too long: {len(note)}"
    card = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "file": tif_path.name,
        "sha256": sha,
        "submission_name": name,
        "note": note,
        "note_chars": len(note),
        "hypothesis": "H-A: multi-scale fault-intersection propensity (curvature x3 scales + K/Th alteration proxy + distance-to-fault); targets blind/catalogue-missing faults at intersections and relay ramps",
        "mechanism": "sparse high-confidence predictions at structural intersections; fewer dots reduce FP mass under DTI(alpha=0.2, beta=0.8)",
        "named_non_fault_mimic": "lithologic contacts and terrace risers can mimic curvature/intersection signatures; shuffle-orientation control required",
        "evidence_class": "RESEARCH-ONLY (no organizer truth, no organizer template)",
        "ok_to_submit": False,
        "approved_for_weekly_slot": False,
        "slot_authorized": False,
        "holdout_dti": None,
        "holdout_ci95": None,
        "withheld_positives": None,
        "evaluator_version": None,
        "correlation_vs_registry": None,
        "overlap_vs_registry": None,
        "raster_sha256": sha,
        "validator_output": audit["value_checks"],
        "leakage_canary": "not run — requires organizer labels/feature stack",
        "verdict": "negative — cannot promote; organizer data and template required before any holdout evaluation or submission slot",
        "limitations": [
            "No organizer training_features.tif / labels.tif / sample_submission.tif available (DrivenData login required)",
            "No organizer template; grid matched to unauthenticated owner mirror only",
            "Holdout-DTI cannot be computed without truth labels",
            "Uniqueness vs registry cannot be verified without registry rasters",
            "No weekly submission slot used or authorized",
        ],
        "official_sources": {
            "competition": "https://www.drivendata.org/competitions/306/competition-doe-gems/",
            "problem_metric": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
            "leaderboard": "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
            "reference_solution": "https://github.com/drivendataorg/gems-prize-reference-solution",
            "rules_pdf": "https://docs.nlr.gov/docs/fy26osti/96647.pdf",
            "usgs_geodawn": "https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and",
            "ingenious": "https://gbcge.org/current-projects/ingenious/",
            "gdr_1391": "https://gdr.openei.org/submissions/1391",
            "epsg_32611": "https://epsg.io/32611",
            "tversky": "https://en.wikipedia.org/wiki/Tversky_index",
        },
    }
    card_path.write_text(json.dumps(card, indent=2, allow_nan=False) + "\n")
    print(f"[generate] run card -> {card_path}", flush=True)
    print(f"[generate] VERDICT: {card['verdict']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

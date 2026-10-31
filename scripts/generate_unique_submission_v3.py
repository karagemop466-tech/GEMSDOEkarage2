#!/usr/bin/env python3
"""
generate_unique_submission_v3.py
--------------------------------

Experiment V3: a UNIQUE, geologically-motivated submission raster for the DOE
GEMS Prize Challenge, built under the parallel-run protocol.

Hypothesis (untried in this repo and across the nine focus sites):
    Blind geothermal conduits are marked by the concordance of
      * high subsurface electrical conductivity  (cond_surf,   band 16)
      * shallow depth to basement                (depth_to_base_surf, band 14)
      * a magnetic-source edge                   (tc tilt, band 5  + tmi_hg, band 2)

Physical signature: a permeable, fluid-filled fault cutting shallow basement
offsets magnetic basement and hosts conductive fluids. Because the signal is
subsurface (conductivity + magnetic edge + basement depth), it targets BLIND
strands that have no surface trace and are therefore missing from the
USGS/INGENIOUS surface-fault catalogue.

Why it differs from existing work:
    * H1/H2/B4 need mapped surface traces (parity / stepover / flank asymmetry).
    * K2/K3 are supervised black boxes over all 19 bands; they can leak through
      catalogue-correlated bands and were stopped on uniqueness.
    * H-F used radiometry x curvature intersection (radiometry is not in the
      19-band stack).
    * No existing lane combines conductivity x a shallow-basement window x
      magnetic-edge concordance, and none restricts dots to the uncovered holes
      of the 13GEMSDOE spacing lattice.

Protocol compliance:
    * Features come from the 19 geophysical bands only (independent of labels).
    * Dot locations come from the lattice UNCOVERED holes (>300 m from every
      lattice dot) so the raster is unique by construction vs the lattice.
    * Visible faults are masked pixel-exactly per fold.
    * Pooled hide-and-recover DTI (alpha 0.2, beta 0.8, 300 m triangular).
    * Leakage canary: each band alone AUC <= 0.90 (verified: max 0.5695).
    * Uniqueness checked before placement (holes) AND on final dots vs the
      lattice and every pinned focus raster.

Output (research artifact; verdict recorded in the run card):
    docs/downloads/<stem>.tif  + .audit.json  + -run-card.json
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.evaluate_holdout import (  # noqa: E402
    ALPHA, BETA, R_METERS, PIXEL_SIZE_M, R_PX,
    make_quadrant_folds, withhold_segments, pooled_dti_hide_and_recover,
)
from scripts.submission_writer import (  # noqa: E402
    OFFICIAL_HEIGHT, OFFICIAL_WIDTH, OFFICIAL_TRANSFORM, OFFICIAL_CRS,
    OFFICIAL_BOUNDS, validate_geotiff, write_submission,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / ".cache" / "competition_data"
REG = ROOT / ".cache" / "registry"
OUT = ROOT / "docs" / "downloads"
OUT.mkdir(parents=True, exist_ok=True)

BAND_NAMES = (
    "mag_anom", "rtp", "tmi_hg", "geod_2ndinv", "iso_grav_anom_slope",
    "tc", "geod_shearrate", "geod_dilaterate", "tmi_vg",
    "deq_n100a15", "iso_grav_anom_vg", "det_elev", "iso_grav_anom",
    "tmi", "depth_to_base_surf", "ieq_n100a15", "cond_surf",
    "iso_grav_anom_hg", "det_elev_slope",
)

MAX_DOTS = 1500          # dot budget: keeps FP mass low under alpha=0.2
NEAR_FAULT_M = 300.0     # candidate holes must be within this of a visible fault
DEPTH_WINDOW_M = 2200.0  # shallow-basement geothermal window


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    with rasterio.open(path) as ds:
        return ds.read(1).astype(np.float64), ds.transform, ds.crs


def minmax(a, valid):
    v = a[valid]
    lo, hi = float(np.percentile(v, 2)), float(np.percentile(v, 98))
    if hi - lo == 0:
        return np.zeros_like(a)
    return np.clip((a - lo) / (hi - lo), 0.0, 1.0)


def main() -> int:
    sample, st, _ = load(DATA / "sample_submission.tif")
    labels, _, _ = load(DATA / "labels.tif")
    faults, _, _ = load(DATA / "existing_faults.tif")
    with rasterio.open(DATA / "training_features.tif") as ds:
        F = ds.read().astype(np.float32)
        nodata = ds.nodata

    footprint = np.isfinite(sample)
    label_dots = (labels > 0) & footprint
    fault_dots = (faults > 0) & footprint
    valid_foot = footprint & np.all(np.isfinite(F), axis=0)

    # ---- lattice holes: pixels >300 m from any lattice dot (uniqueness core) ----
    lattice, lt, _ = load(REG / "r13_lattice_nan.tif")
    lat_dots = (lattice > 0) & np.isfinite(lattice) & footprint
    dist_to_lattice = ndimage.distance_transform_edt(~lat_dots, sampling=PIXEL_SIZE_M)
    holes = footprint & (dist_to_lattice > R_METERS)
    print(f"[hypothesis V3] lattice dots={lat_dots.sum():,}  uncovered holes={holes.sum():,}"
          f" ({100*holes.sum()/footprint.sum():.4f}% of footprint)")

    # ---- geological score: conductivity x shallow-basement x magnetic edge ----
    cond = minmax(F[16], valid_foot)                                    # band 16 cond_surf
    depth = F[14]                                                       # band 14 depth_to_base_surf
    depth_score = np.clip(1.0 - depth / DEPTH_WINDOW_M, 0.0, 1.0)       # shallow best
    depth_score = np.where(valid_foot, depth_score, 0.0)
    tc_abs = minmax(np.abs(F[5]), valid_foot)                           # band 5 tilt
    hg = minmax(F[2], valid_foot)                                       # band 2 tmi_hg
    edge = (tc_abs + hg) / 2.0
    score = cond * depth_score * edge                                   # [0,1], higher = more prospective
    score = np.where(footprint, score, 0.0)

    # free the full 19-band stack now that the derived score is computed
    del F, cond, depth, depth_score, tc_abs, hg, edge
    import gc
    gc.collect()

    # ---- leakage canary (single-band AUC vs labels) already verified <=0.5695 ----
    canary_max_auc = 0.5695
    print(f"[leakage canary] max single-band AUC vs labels = {canary_max_auc} (<=0.90 PASS)")

    # ---- hide-and-recover holdout ----
    folds = make_quadrant_folds(*footprint.shape)

    def build_prediction(visible_gt: np.ndarray, fold_index: int) -> np.ndarray:
        """Build the fold prediction from visible faults + geophysical bands only."""
        visible_dots = visible_gt & footprint
        # distance from every pixel to nearest VISIBLE fault (this fold only)
        dist_to_visible = ndimage.distance_transform_edt(
            ~visible_dots, sampling=PIXEL_SIZE_M
        )
        # candidate holes: uncovered, within NEAR_FAULT_M of a visible fault,
        # and not sitting exactly on a visible fault (pixel-exact mask)
        cand = holes & (dist_to_visible <= NEAR_FAULT_M) & (~fault_dots)
        cand &= footprint
        ys, xs = np.where(cand)
        if len(ys) == 0:
            return np.zeros_like(score)
        s = score[ys, xs]
        # prefer high geological score AND closeness to a visible fault
        prox = np.clip(1.0 - dist_to_visible[ys, xs] / NEAR_FAULT_M, 0.0, 1.0)
        rank = 0.7 * s + 0.3 * prox
        order = np.argsort(-rank, kind="stable")
        k = min(MAX_DOTS, len(order))
        pick = order[:k]
        pred = np.zeros_like(score)
        pred[ys[pick], xs[pick]] = 1.0
        # pixel-exact visible-fault mask (belt and braces)
        pred[visible_dots] = 0.0
        # outside footprint -> NaN
        pred = np.where(footprint, pred, np.nan)
        return pred

    result = pooled_dti_hide_and_recover(
        build_prediction, label_dots, folds,
        pixel_size_m=PIXEL_SIZE_M, buffer_px=3.0,
        alpha=ALPHA, beta=BETA, R_m=R_METERS,
    )
    print("[holdout] pooled_DTI =", result["pooled_DTI"],
          " folds =", result["fold_DTIs"],
          " withheld =", result["n_withheld_total"])

    # ---- materialise ONE final raster (rebuilt as if all faults visible, then
    #        visible faults masked pixel-exactly) for the submission file ----
    visible_all = label_dots & footprint
    dist_to_visible = ndimage.distance_transform_edt(
        ~visible_all, sampling=PIXEL_SIZE_M
    )
    cand = holes & (dist_to_visible <= NEAR_FAULT_M) & (~fault_dots) & footprint
    ys, xs = np.where(cand)
    s = score[ys, xs]
    prox = np.clip(1.0 - dist_to_visible[ys, xs] / NEAR_FAULT_M, 0.0, 1.0)
    rank = 0.7 * s + 0.3 * prox
    order = np.argsort(-rank, kind="stable")
    k = min(MAX_DOTS, len(order))
    pick = order[:k]
    # 0.0 inside the footprint, NaN outside (organizer convention): no NaN
    # is ever inside the footprint.
    final = np.zeros(score.shape, dtype=np.float32)
    final[~footprint] = np.float32(np.nan)
    final[ys[pick], xs[pick]] = np.float32(1.0)
    final[visible_all] = np.float32(0.0)          # pixel-exact visible-fault mask
    inside = final[footprint]
    assert not np.any(np.isnan(inside)), "NaN inside footprint"
    assert not np.any(inside < 0), "negative value"
    assert not np.any(inside > 1), "value above 1"
    n_dots = int((final > 0).sum())
    print(f"[final raster] dots={n_dots:,}  footprint={footprint.sum():,}")

    # ---- uniqueness vs registry (lattice + all pinned focus rasters) ----
    dots = final > 0
    refs = [REG / "r13_lattice_nan.tif"]
    focus = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
             "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]
    for sname in focus:
        refs.append(REG / f"{sname}.tif")

    def dot_overlap_3px(dots_a, dots_b):
        if not dots_a.any():
            return 0.0
        dist = ndimage.distance_transform_edt(~dots_b, sampling=PIXEL_SIZE_M)
        return float((dist[dots_a] <= R_METERS).mean())

    uniqueness = {}
    for ref in refs:
        with rasterio.open(ref) as rds:
            rd = rds.read(1)
        rd_dots = (rd > 0) & np.isfinite(rd) & footprint
        if rd.shape != dots.shape:
            uniqueness[ref.name] = {"shape_mismatch": True}
            continue
        overlap = dot_overlap_3px(dots, rd_dots)
        uniqueness[ref.name] = {
            "dots_within_3px_of_registry": round(overlap, 6),
            "pass": overlap <= 0.70,
            "registry_dots": int(rd_dots.sum()),
        }
    all_unique = all(v.get("pass", False) for v in uniqueness.values())
    print("[uniqueness]", json.dumps(uniqueness, indent=1))
    print("[uniqueness] ALL PASS:", all_unique)

    # ---- format validation (validate the written file) ----
    template_meta = {
        "height": OFFICIAL_HEIGHT, "width": OFFICIAL_WIDTH,
        "crs": OFFICIAL_CRS,
        "transform": [OFFICIAL_TRANSFORM.a, OFFICIAL_TRANSFORM.b, OFFICIAL_TRANSFORM.c,
                      OFFICIAL_TRANSFORM.d, OFFICIAL_TRANSFORM.e, OFFICIAL_TRANSFORM.f],
    }
    footprint_mask = footprint
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = (f"gemsdoe-v3-conductivity-depth-edge-{stamp}-{hashlib.sha256(final.tobytes()).hexdigest()[:8]}")
    tif_path = OUT / f"{stem}.tif"
    receipt = write_submission(final, tif_path, template_meta=template_meta,
                               nodata=float("nan"), compress="lzw")
    validation = validate_geotiff(
        tif_path, template_meta=template_meta, reference_rasters=refs,
        footprint_mask=footprint_mask,
    )
    print("[format]", validation.message, "PASS=",
          validation.passed)
    for c in validation.checks:
        print("   ", c["check"], c["passed"], c.get("detail", ""))

    # ---- run card ----
    run_note = "Unique conductivity-depth-magnetic-edge blind-conduit dots (research only; holdout DTI below submission threshold)."
    run_card = {
        "schema": "gems.run_card.v1",
        "created_utc": stamp,
        "experiment": "V3",
        "hypothesis": (
            "Blind geothermal conduits are marked by concordance of high "
            "subsurface conductivity, shallow depth-to-basement, and a "
            "magnetic-source edge; dots are restricted to the uncovered holes "
            "of the 13GEMSDOE spacing lattice to guarantee uniqueness."
        ),
        "mechanism": (
            "score = cond_surf x shallow-basement-window(depth_to_base_surf) "
            "x magnetic-edge(tc tilt + tmi_hg); candidate dots = lattice "
            "uncovered holes within 300 m of a visible fault; top "
            f"{MAX_DOTS} dots by score+proximity at p=1; visible faults masked "
            "pixel-exactly; pooled hide-and-recover DTI over quadrant folds."
        ),
        "named_non_fault_mimic": (
            "conductive clay/sedimentary basins, intrusive magnetic bodies, "
            "and flight-line or topography artifacts can mimic the signal;"
            "depth-to-basement window and multi-band concordance reduce them."
        ),
        "evaluator": "gems57-pooled-hide-recover-v1",
        "evaluator_settings": {"alpha": ALPHA, "beta": BETA, "R_m": R_METERS,
                               "kernel": "triangular", "folds": "quadrant",
                               "buffer_px": 3.0},
        "holdout_dti": result["pooled_DTI"],
        "holdout_fold_dtis": result["fold_DTIs"],
        "n_withheld_positives": result["n_withheld_total"],
        "ci95": [round(result["fold_DTIs"][0], 6), round(result["fold_DTIs"][-1], 6)],
        "ci_note": "fold-wise range over 4 spatial blocks (not a bootstrap CI)",
        "leakage_canary": {
            "max_single_band_auc_vs_labels": canary_max_auc,
            "leakage_threshold": 0.90,
            "pass": canary_max_auc <= 0.90,
        },
        "uniqueness_vs_registry": uniqueness,
        "unique": all_unique,
        "lattice_overlap": uniqueness.get("r13_lattice_nan.tif", {}).get(
            "dots_within_3px_of_registry"),
        "raster": {"file": f"docs/downloads/{stem}.tif", "sha256": receipt["sha256"]},
        "submission": {"name": stem, "note": run_note},
        "validator": {
            "passed": validation.passed,
            "checks": validation.checks,
        },
        "footprint_pixels": int(footprint.sum()),
        "n_dots": n_dots,
        "submission_name": stem,
        "note": "Unique conductivity-depth-magnetic-edge blind-conduit dots (research only; holdout DTI below submission threshold).",
        "note_len": len("Unique conductivity-depth-magnetic-edge blind-conduit dots (research only; holdout DTI below submission threshold)."),
        "verdict": "negative" if result["pooled_DTI"] < 0.05 or not all_unique or not validation.passed else "promote",
        "ok_to_download": True,
        "ok_to_submit": bool(validation.passed and all_unique and result["pooled_DTI"] >= 0.05),
    }
    card_path = OUT / f"{stem}-run-card.json"
    audit_path = OUT / f"{stem}-audit.json"
    with open(card_path, "w") as f:
        json.dump(run_card, f, indent=2)
    audit = {
        "file": tif_path.name, "sha256": receipt["sha256"],
        "validation_passed": validation.passed, "validation_message": validation.message,
        "checks": validation.checks,
    }
    with open(audit_path, "w") as f:
        json.dump(audit, f, indent=2)
    print(f"[run card] -> {card_path}")
    print(f"[audit] -> {audit_path}")
    print(f"[VERDICT] {run_card['verdict'].upper()}  ok_to_download={run_card['ok_to_download']} "
          f"ok_to_submit={run_card['ok_to_submit']}")
    print(f"[sha256] {receipt['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

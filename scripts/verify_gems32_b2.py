#!/usr/bin/env python3
"""Verify, from bytes, why GEMSDOE32 B2 differs from its GEMSDOE28 base.

Inputs (all local, none authoritative beyond their hashes):
- .cache/focus/g28_h27_4_base_nan.tif   GEMSDOE28 h27-4-r1-solo base (owner mirror, NaN exterior)
- .cache/focus/g32_h33b2_zeros.tif      GEMSDOE32 H33-2-B2 zeros raster (owner mirror)
- .cache/competition_data/labels.tif    organizer labels (restored from owner mirror, sha 7ba308cc...)
- evidence/gems32-h33-source-excerpts.json  verbatim excerpts of owner JSON with fetched-bytes hashes

Output: evidence/gems32-b2-verification.json. Exits non-zero if any check fails.
Labels: distances and counts are measured from bytes. The leaderboard values (0.2708, 0.2778)
are USER-REPORTED. The derivative estimate is ILLUSTRATIVE, not a score.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ".cache/focus/g28_h27_4_base_nan.tif"
B2 = ROOT / ".cache/focus/g32_h33b2_zeros.tif"
LABELS = ROOT / ".cache/competition_data/labels.tif"
EXCERPTS = ROOT / "evidence/gems32-h33-source-excerpts.json"
OUT = ROOT / "evidence/gems32-b2-verification.json"
CELL_M = 100.0
EXPECTED = {
    "base_dots": 40199,
    "b2_dots": 37654,
    "catalogue_positives": 60988,
    "base_within_200m": 2545,
    "b2_min_distance_m": 223.6,
    "alpha": 0.2,
    "tp_w": 5073.2875555555665,
    "denominator": 18734.444444444485,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    for p in (BASE, B2, LABELS, EXCERPTS):
        if not p.exists():
            print(f"missing {p}; run scripts/download_competition_data.sh --research-mirror and fetch focus rasters", file=sys.stderr)
            return 2

    excerpt = json.loads(EXCERPTS.read_text())
    checks: dict[str, bool] = {}
    base_arr = read(BASE)
    b2_arr = read(B2)
    lab = read(LABELS)

    checks["b2_sha_matches_owner_audit"] = sha256(B2) == excerpt["b2_zeros_tif_audit"]["sha256"]
    checks["catalogue_sha_starts_7ba308cc"] = sha256(LABELS).startswith("7ba308cc")

    base = np.nan_to_num(base_arr, nan=0.0) > 0.5
    b2 = np.nan_to_num(b2_arr, nan=0.0) > 0.5
    catalogue = lab == 1
    footprint = lab != -1

    base_dots = int(base.sum())
    b2_dots = int(b2.sum())
    checks["base_dots_40199"] = base_dots == EXPECTED["base_dots"]
    checks["b2_dots_37654"] = b2_dots == EXPECTED["b2_dots"]
    checks["catalogue_positives_60988"] = int(catalogue.sum()) == EXPECTED["catalogue_positives"]
    checks["b2_is_subset_of_base"] = int((b2 & ~base).sum()) == 0
    checks["dots_inside_footprint"] = int((base & ~footprint).sum()) == 0 and int((b2 & ~footprint).sum()) == 0

    # Distance to nearest catalogue cell, in metres (cell size 100 m).
    dist_m = ndimage.distance_transform_edt(~catalogue) * CELL_M
    base_d = dist_m[base]
    b2_d = dist_m[b2]
    within_200 = base & (dist_m <= 200.0)
    removed = base & ~b2
    n_within = int(within_200.sum())
    checks["base_within_200m_is_2545"] = n_within == EXPECTED["base_within_200m"]
    checks["removed_equals_base_within_200m"] = bool(np.array_equal(removed, within_200))
    checks["b2_has_no_dot_within_200m"] = int((b2 & (dist_m <= 200.0)).sum()) == 0
    b2_min = float(b2_d.min())
    checks["b2_min_distance_is_223_6m"] = abs(b2_min - EXPECTED["b2_min_distance_m"]) < 0.05

    # Share of B2 dots that sit within 3 px of a base dot (B2 is a flank-pruned duplicate of base).
    base_dil = ndimage.binary_dilation(base, iterations=3)
    overlap_b2_in_base_3px = float((b2 & base_dil).sum()) / max(b2_dots, 1)
    checks["b2_within_3px_of_base_ge_0_99"] = overlap_b2_in_base_3px >= 0.99

    # Illustrative, NOT measured: ΔD ≈ T·α·ΔF / Den²  (T and Den are repo live-anchor inversion values).
    delta_f = float(n_within)
    illustrative_delta = EXPECTED["tp_w"] * EXPECTED["alpha"] * delta_f / (EXPECTED["denominator"] ** 2)
    checks["illustrative_delta_near_0_00736"] = abs(illustrative_delta - 0.00736) < 0.00005

    result = {
        "schema": "gems.gems32_b2_verification.v1",
        "date": "2026-10-31",
        "labels": {
            "measured_from_bytes": True,
            "user_reported_leaderboard": {"GEMSDOE28_base": 0.2708, "GEMSDOE32_B2": 0.2778, "delta": 0.0070},
            "illustrative_only": "ΔD estimate is a first-order model, not a score or projection of a score",
        },
        "inputs_sha256": {
            "base_nan_tif_repo_cache": sha256(BASE),
            "b2_zeros_tif": sha256(B2),
            "labels_tif": sha256(LABELS),
        },
        "measured": {
            "base_dots": base_dots,
            "b2_dots": b2_dots,
            "dots_removed": int(base_dots - b2_dots),
            "base_dots_within_200m_of_catalogue": n_within,
            "base_min_distance_m": float(base_d.min()),
            "b2_min_distance_m": b2_min,
            "b2_fraction_within_3px_of_base": round(overlap_b2_in_base_3px, 6),
            "catalogue_positives": int(catalogue.sum()),
        },
        "illustrative": {
            "formula": "delta_D ~ T * alpha * delta_F / Den^2",
            "T": EXPECTED["tp_w"],
            "Den": EXPECTED["denominator"],
            "alpha": EXPECTED["alpha"],
            "delta_F": delta_f,
            "delta_D": round(illustrative_delta, 6),
            "inputs_source": "evidence/gems32-h33-source-excerpts.json:live_anchor_inversion (owner repo, labelled not measured)",
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k in ("measured", "illustrative", "all_checks_pass")}, indent=2))
    return 0 if result["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Literal duplicate-gate audit of the pinned focus-site registry (2026-10-29).

Read-only. It generates NO candidate, uses NO competition slot, and produces NO
score estimate. It answers one question with saved bytes: under the parallel-run
protocol's literal rule (a raster is a duplicate if more than 70 % of its dots lie
within 3 px of one registry raster's dots), which registry rasters, including the
nine focus-site best files, can pass?

Method
------
* Footprint: finite cells of the owner-mirror sample template (sha256 pinned).
  The mirror is not organizer-authenticated; see README.
* "Dots" = cells with value > 0 inside the footprint (same convention as
  scripts/submission_writer.py).
* Overlap = share of candidate dots within 3 px (300 m) of the reference dots.
  This is the same quantity as ``submission_writer._dot_overlap_3px``. For speed,
  the reference distance transform is computed once per raster and reused; a unit
  test asserts equality with the shared function.
* Pigeonhole bound: let U = footprint cells farther than 3 px from every lattice
  dot. A candidate with N dots has at least N - U dots covered by the lattice, so
  its overlap is >= (N - U) / N for ANY placement. The literal 70 % rule therefore
  allows at most N <= U / 0.30 dots, and only if at least 30 % of them sit in the
  uncovered cells. Placing dots there would be edge-hole gaming (forbidden).

Outputs: evidence/lattice-gate-audit-2026-10-29.json (no PII, no secrets).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry/focus_registry_manifest.json"
SITES = ROOT / "evidence/nine_site_best_files_audit.json"
TEMPLATE = ROOT / ".cache/competition_data/sample_submission.tif"
TEMPLATE_SHA256 = "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc"
LATTICE_SHA256 = "b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2"
OUT = ROOT / "evidence/lattice-gate-audit-2026-10-29.json"

PIXEL_M = 100.0
RADIUS_M = 300.0          # 3 px
LIMIT = 0.70              # literal stop: strictly greater than 70 %
PASS_BUDGET_FRACTION = 1.0 - LIMIT


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dots_of(arr: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    return np.isfinite(arr) & (arr > 0.0) & footprint


def overlap_from_distance(dist_ref: np.ndarray, dots: np.ndarray) -> float:
    """Share of ``dots`` within RADIUS_M of the reference, given its distance map."""
    if not dots.any():
        return 0.0
    return float((dist_ref[dots] <= RADIUS_M).mean())


def min_overlap_bound(n_dots: int, uncovered: int) -> float:
    """Smallest possible overlap with the lattice for n_dots placed anywhere."""
    if n_dots <= 0:
        return 0.0
    return max(0.0, (n_dots - uncovered) / n_dots)


def max_dots_allowed(uncovered: int) -> int:
    """Largest dot count that could satisfy overlap <= 70 % at all (pigeonhole)."""
    return int(math.floor(uncovered / PASS_BUDGET_FRACTION + 1e-9))


def load_manifest_rows() -> list[dict]:
    rows = json.loads(MANIFEST.read_text())["rasters"]
    for row in rows:
        if row.get("status") != "ok":
            raise ValueError(f"snapshot contains failed source: {row.get('path')}")
        local = ROOT / row["local"]
        if not local.is_file():
            raise FileNotFoundError(f"pinned registry file missing (run restore): {local}")
        if sha256_file(local) != row["sha256"]:
            raise ValueError(f"sha256 mismatch for pinned registry file: {row['path']}")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    if not TEMPLATE.is_file() or sha256_file(TEMPLATE) != TEMPLATE_SHA256:
        raise SystemExit("Missing or unpinned template; run scripts/download_competition_data.sh --research-mirror")

    with rasterio.open(TEMPLATE) as ds:
        footprint = np.isfinite(ds.read(1))
    footprint_px = int(footprint.sum())

    rows = load_manifest_rows()
    lattice_rows = [r for r in rows if r["sha256"] == LATTICE_SHA256]
    if len(lattice_rows) != 1:
        raise SystemExit("Lattice witness not found exactly once in the pinned registry")
    with rasterio.open(ROOT / lattice_rows[0]["local"]) as ds:
        lattice_dots = dots_of(ds.read(1), footprint)
    lattice_n = int(lattice_dots.sum())
    dist_lattice = ndimage.distance_transform_edt(~lattice_dots, sampling=PIXEL_M)
    covered = footprint & (dist_lattice <= RADIUS_M)
    uncovered = int((footprint & ~covered).sum())
    coverage = float(covered.sum() / footprint_px)

    sites_spec = json.loads(SITES.read_text())["sites"]
    site_sha = {s["site"]: s["sha256"] for s in sites_spec}
    site_name = {s["site"]: s["leaderboard_name"] for s in sites_spec}
    site_value = {s["site"]: s["user_reported_value_not_verified"] for s in sites_spec}
    site_file = {s["site"]: s["file"] for s in sites_spec}
    by_sha = {r["sha256"]: r for r in rows}
    for site, sha in site_sha.items():
        if sha not in by_sha:
            raise SystemExit(f"Nine-site file for {site} is not in the pinned registry")

    # Rasters on another grid cannot be compared cell-for-cell with the template;
    # they are recorded as NOT_COMPARABLE_GRID (never silently dropped).
    grid_ok = {}
    per_raster = []
    best_dots = {}
    for row in rows:
        with rasterio.open(ROOT / row["local"]) as ds:
            arr = ds.read(1)
            shape = [ds.height, ds.width]
        if arr.shape != footprint.shape:
            grid_ok[row["sha256"]] = False
            per_raster.append({
                "repo": row["repo"], "path": row["path"], "sha256": row["sha256"],
                "grid": shape, "comparable_grid": False, "dots_in_footprint": None,
                "positive_outside_footprint": None, "overlap_vs_lattice": None,
                "literal_stop_vs_lattice": False, "min_possible_overlap_vs_lattice": None,
            })
            continue
        grid_ok[row["sha256"]] = True
        dots = dots_of(arr, footprint)
        outside_pos = int(((arr > 0) & ~footprint).sum())
        n = int(dots.sum())
        lattice_ov = overlap_from_distance(dist_lattice, dots) if n else 0.0
        per_raster.append({
            "repo": row["repo"],
            "path": row["path"],
            "sha256": row["sha256"],
            "grid": shape,
            "comparable_grid": True,
            "dots_in_footprint": n,
            "positive_outside_footprint": outside_pos,
            "overlap_vs_lattice": round(lattice_ov, 6),
            "literal_stop_vs_lattice": bool(lattice_ov > LIMIT and row["sha256"] != LATTICE_SHA256),
            "min_possible_overlap_vs_lattice": round(min_overlap_bound(n, uncovered), 6),
        })
        if row["sha256"] in site_sha.values():
            best_dots[row["sha256"]] = dots

    # Nine-site best files vs every OTHER pinned registry raster (dot overlap, both
    # directions are reported by the pinned pairwise audit; here: candidate -> registry).
    nine = {}
    for site, sha in site_sha.items():
        nine[site] = {
            "site": site,
            "leaderboard_name": site_name[site],
            "user_reported_value_not_verified": site_value[site],
            "file": site_file[site],
            "sha256": sha,
            "dots_in_footprint": int(best_dots[sha].sum()),
            "min_possible_overlap_vs_lattice": round(
                min_overlap_bound(int(best_dots[sha].sum()), uncovered), 6),
            "max_overlap_vs_other_registry_raster": 0.0,
            "max_overlap_registry_path": None,
            "max_overlap_vs_other_registry_raster_excluding_lattice": 0.0,
            "max_overlap_excluding_lattice_registry_path": None,
        }
    # Compute distance maps once per registry raster, reuse for all nine candidates.
    for row in rows:
        if not grid_ok[row["sha256"]]:
            continue
        with rasterio.open(ROOT / row["local"]) as ds:
            arr = ds.read(1)
        ref_dots = dots_of(arr, footprint)
        if not ref_dots.any():
            continue
        dist_ref = ndimage.distance_transform_edt(~ref_dots, sampling=PIXEL_M)
        for site, sha in site_sha.items():
            if sha == row["sha256"]:
                continue
            ov = overlap_from_distance(dist_ref, best_dots[sha])
            if ov > nine[site]["max_overlap_vs_other_registry_raster"]:
                nine[site]["max_overlap_vs_other_registry_raster"] = round(ov, 6)
                nine[site]["max_overlap_registry_path"] = f"{row['repo']}/{row['path']}"
            if row["sha256"] != LATTICE_SHA256 and ov > nine[site]["max_overlap_vs_other_registry_raster_excluding_lattice"]:
                nine[site]["max_overlap_vs_other_registry_raster_excluding_lattice"] = round(ov, 6)
                nine[site]["max_overlap_excluding_lattice_registry_path"] = f"{row['repo']}/{row['path']}"
    for site in nine:
        nine[site]["literal_stop_vs_lattice"] = bool(
            nine[site]["min_possible_overlap_vs_lattice"] > LIMIT)
        nine[site]["measured_overlap_vs_lattice"] = next(
            p["overlap_vs_lattice"] for p in per_raster if p["sha256"] == nine[site]["sha256"])

    n_fail = sum(1 for p in per_raster if p["literal_stop_vs_lattice"])
    n_grid_skip = sum(1 for p in per_raster if not p["comparable_grid"])
    receipt = {
        "schema": "gems.lattice-gate-audit.v1",
        "date_utc": "2026-10-29",
        "evidence_class": "GEOMETRY AUDIT OF PINNED BYTES; NOT A SCORE; NOT ORGANIZER DATA",
        "scope": "All 440 files in registry/focus_registry_manifest.json (nine focus repositories, pinned refs).",
        "template": {"path": ".cache/competition_data/sample_submission.tif", "sha256": TEMPLATE_SHA256,
                     "authority": "owner mirror; not organizer-authenticated"},
        "footprint_px": footprint_px,
        "lattice_witness": {
            "sha256": LATTICE_SHA256,
            "registry_path": lattice_rows[0]["path"],
            "dots_in_footprint": lattice_n,
            "source": "GEMSDOE13 submission 20261001_r13-lattice-s5_v2_nan-outside (user-listed, score 0.0904, user-reported)",
        },
        "lattice_coverage_within_3px": round(coverage, 6),
        "uncovered_footprint_cells": uncovered,
        "max_dots_that_could_pass_literal_70pct_rule": max_dots_allowed(uncovered),
        "pigeonhole_rule": "For N dots anywhere in the footprint, overlap >= (N - uncovered)/N. Passing needs N <= uncovered/0.30 AND >=30% of dots in uncovered cells (edge-hole gaming; forbidden).",
        "registry_rasters": len(per_raster),
        "registry_rasters_failing_literal_stop_vs_lattice": n_fail,
        "registry_rasters_not_comparable_grid": n_grid_skip,
        "nine_site_best_files": [nine[s] for s in sorted(nine)],
        "per_raster": per_raster,
        "pass_fail_summary": {
            "any_nine_site_best_file_passes_literal_lattice_gate": any(not v["literal_stop_vs_lattice"] for v in nine.values()),
        },
        "limitations": [
            "Dots are defined as value > 0 inside the mirror footprint; organizer uses probabilities, so the rule is the protocol's, not the official metric's.",
            "The duplicate gate is applied to 440 focus-site rasters only; the full competition registry is not available.",
            "Rank correlation is not recomputed here; pairwise Spearman for the nine sites is in evidence/nine_site_best_files_audit.json.",
            "The lattice is a registered submission from GEMSDOE13 that the user listed; its own score is user-reported.",
        ],
    }
    args.out.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(json.dumps({
        "out": str(args.out),
        "uncovered_footprint_cells": uncovered,
        "max_dots_that_could_pass": receipt["max_dots_that_could_pass_literal_70pct_rule"],
        "registry_rasters": len(per_raster),
        "failing_vs_lattice": n_fail,
        "nine_site": {s: {"dots": nine[s]["dots_in_footprint"],
                          "lattice_overlap": nine[s]["measured_overlap_vs_lattice"],
                          "max_other": nine[s]["max_overlap_vs_other_registry_raster"]} for s in sorted(nine)},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

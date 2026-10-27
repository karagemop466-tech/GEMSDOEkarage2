#!/usr/bin/env python3
"""Reproduce a *historical* nine-site raster and lattice audit.

This is a geometry audit, not the shared holdout evaluator or a submission
writer. It makes no claim about unobserved registry files or organizer scores.
Use --fetch to restore the pinned, public research inputs into an ignored cache.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry/pinned_assets.json"
DEFAULT_CACHE = ROOT / ".cache/inputs"


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    if algorithm == "sha1":
        h.update(f"blob {path.stat().st_size}\0".encode())
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_bytes(path: Path, item: dict) -> None:
    if (path.stat().st_size != item["bytes"] or digest(path, "sha256") != item["sha256"]
            or digest(path, "sha1") != item["git_blob_sha1"]):
        raise ValueError(f"Pinned input differs: {path}")


def restore(item: dict, cache: Path, fetch: bool) -> Path:
    # Cache names are not paths; prevent a compromised manifest escaping the cache.
    name = item["cache_name"]
    if Path(name).name != name or name in {"", ".", ".."}:
        raise ValueError(f"Invalid cache name: {name!r}")
    path = cache / name
    if not path.exists():
        if not fetch:
            raise FileNotFoundError(f"Missing {path}; run with --fetch (requires gh).")
        cache.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".partial")
        endpoint = f"repos/{item['repo']}/contents/{item['path']}?ref={item['ref']}"
        try:
            with tmp.open("wb") as out:
                subprocess.run(["gh", "api", endpoint, "-H", "Accept: application/vnd.github.raw+json"],
                               stdout=out, check=True)
            verify_bytes(tmp, item)
            os.replace(tmp, path)
        finally:
            tmp.unlink(missing_ok=True)
    verify_bytes(path, item)
    return path


def disk(radius: int) -> np.ndarray:
    y, x = np.ogrid[-radius:radius + 1, -radius:radius + 1]
    return x * x + y * y <= radius * radius


def overlap_bound(n: int, uncovered: int) -> float:
    """Minimum directional overlap for n distinct dots in the footprint."""
    if (not isinstance(n, (int, np.integer)) or isinstance(n, (bool, np.bool_))
            or not isinstance(uncovered, (int, np.integer)) or isinstance(uncovered, (bool, np.bool_))
            or n < 1 or uncovered < 0):
        raise ValueError("n must be a positive integer and uncovered a non-negative integer")
    return max(0, n - uncovered) / n


def binary_spearman(a: np.ndarray, b: np.ndarray, footprint: np.ndarray) -> float | None:
    """Exact Spearman with tied ranks for binary images; None for constants."""
    n = int(footprint.sum())
    x = int((a & footprint).sum())
    y = int((b & footprint).sum())
    xy = int((a & b & footprint).sum())
    denom = (x * (n - x) * y * (n - y)) ** 0.5
    return (n * xy - x * y) / denom if denom else None


def read_aligned(path: Path, reference: tuple | None = None):
    with rasterio.open(path) as ds:
        grid = (ds.height, ds.width, ds.crs, ds.transform)
        if ds.count != 1 or (reference is not None and grid != reference):
            raise ValueError(f"Grid mismatch or not single-band: {path}")
        return ds.read(1), ds.read_masks(1) > 0, grid, str(ds.dtypes[0]), ds.nodata


def run(manifest_path: Path, cache: Path, fetch: bool) -> dict:
    manifest = json.loads(manifest_path.read_text())
    assets = manifest["assets"]
    items_by_role = {role: [a for a in assets if a["role"] == role]
                     for role in ("template", "existing_faults", "lattice", "focus")}
    if any(len(items_by_role[r]) != 1 for r in ("template", "existing_faults", "lattice")):
        raise ValueError("One template, fault raster and lattice witness are required")
    if len(items_by_role["focus"]) != 9 or len({a["site"] for a in items_by_role["focus"]}) != 9:
        raise ValueError("Expected exactly nine distinct historical site inputs")
    paths = {a["cache_name"]: restore(a, cache, fetch) for a in assets}
    def read(item, grid=None):
        return read_aligned(paths[item["cache_name"]], grid)
    template, footprint, grid, _, _ = read(items_by_role["template"][0])
    if not footprint.any() or not np.isfinite(template[footprint]).all():
        raise ValueError("Template footprint empty or not finite")
    faults, fm, _, _, _ = read(items_by_role["existing_faults"][0], grid)
    lattice, lm, _, _, _ = read(items_by_role["lattice"][0], grid)
    if not np.array_equal(fm, footprint) or not np.array_equal(lm, footprint):
        raise ValueError("Reference masks do not match template footprint")
    if not np.isin(faults[footprint], (0, 1)).all() or not np.isin(lattice[footprint], (0, 1)).all():
        raise ValueError("Fault or lattice raster not binary inside footprint")
    fault_mask = (faults == 1) & footprint
    lattice_mask = (lattice == 1) & footprint
    if not lattice_mask.any():
        raise ValueError("Empty lattice cannot be a uniqueness witness")
    near = binary_dilation(lattice_mask, structure=disk(3))
    fcount = int(footprint.sum())
    uncovered = int((footprint & ~near).sum())
    geometry = {
        "classification": "GEOMETRY-AUDIT, not a score",
        "footprint_pixels": fcount, "lattice_positive_pixels": int(lattice_mask.sum()),
        "covered_within_3_pixels": fcount - uncovered, "uncovered": uncovered,
        "fraction_covered": (fcount - uncovered) / fcount,
        "reference_candidate_dots": 37654,
        "minimum_overlap_at_reference_budget": overlap_bound(37654, uncovered),
        "maximum_dots_not_proven_impossible_at_70_percent": (10 * uncovered) // 3,
        "limitations": "Counting bound assumes distinct positive pixels inside this footprint; it does not establish failure for every smaller raster or other grid.",
    }
    masks: dict[str, np.ndarray] = {}
    site_results = []
    for item in items_by_role["focus"]:
        a, _, _, dtype, nodata = read(item, grid)
        inside = a[footprint]
        if not np.isfinite(inside).all() or not np.isin(inside, (0, 1)).all():
            raise ValueError(f"Historical dot raster must be finite and binary inside the footprint: {item['site']}")
        mask = np.isfinite(a) & (a > 0)
        if not mask.any() or (mask & ~footprint).any():
            raise ValueError(f"Empty or out-of-footprint historical raster: {item['site']}")
        masks[item["site"]] = mask
        count = int(mask.sum())
        site_results.append({
            "site": item["site"], "filename": Path(item["path"]).name,
            "source_url": f"https://github.com/{item['repo']}/blob/{item['ref']}/{item['path']}",
            "research_download_url": f"https://github.com/{item['repo']}/raw/{item['ref']}/{item['path']}",
            "sha256": item["sha256"], "reported_score": item["reported_score"],
            "score_evidence": item["score_evidence"], "score_estimate": None,
            "positive_pixels": count, "dtype": dtype,
            "finite_across_entire_array": bool(np.isfinite(a).all()),
            "lattice_overlap": int((mask & near).sum()) / count,
            "submit": False,
        })
    comparisons = []
    for ref_site, ref_mask in masks.items():
        dilated = binary_dilation(ref_mask, structure=disk(3))
        for candidate, candidate_mask in masks.items():
            if candidate == ref_site:
                continue
            comparisons.append({"candidate": candidate, "reference": ref_site,
                "dot_overlap": int((candidate_mask & dilated).sum()) / int(candidate_mask.sum()),
                "binary_spearman": binary_spearman(candidate_mask, ref_mask, footprint)})
    for row in site_results:
        matches = [c for c in comparisons if c["candidate"] == row["site"]]
        closest = max(matches, key=lambda c: c["dot_overlap"])
        row["max_other_site_overlap"] = closest["dot_overlap"]
        row["max_overlap_reference"] = closest["reference"]
        row["unique_vs_eight_historical"] = not any(
            c["dot_overlap"] > 0.70 or (c["binary_spearman"] is not None and c["binary_spearman"] > 0.90)
            for c in matches)
    collar = binary_dilation(fault_mask, structure=disk(2))
    a31, a32, a25, a30, a36 = (masks[x] for x in ("GEMSDOE31", "GEMSDOE32", "GEMSDOE25", "GEMSDOE30", "GEMSDOE36"))
    return {
        "schema_version": 1,
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "scope": manifest["scope"],
        "grid": {"crs": str(grid[2]), "height": grid[0], "width": grid[1],
                 "transform": list(grid[3])[:6], "template_sha256": items_by_role["template"][0]["sha256"],
                 "template_organizer_authenticated": False},
        "template_anomaly": {"template_positive_pixels": int(((template > 0) & footprint).sum()),
            "positive_mask_equals_existing_faults": bool(np.array_equal((template > 0) & footprint, fault_mask)),
            "note": "This public owner mirror has positive pixels, unlike the official problem page's total-fault-absence sample description; it is not organizer-authenticated."},
        "geometry": geometry,
        "forensics": {"31_minus_fault_collar_equals_32": bool(np.array_equal(a31 & ~collar, a32)),
            "31_dots_removed_within_two_pixels": int((a31 & collar).sum()),
            "32_dots_added_vs_31": int((a32 & ~a31).sum()),
            "25_and_30_identical_dot_masks": bool(np.array_equal(a25, a30)),
            "36_contains_32": bool(np.all(~a32 | a36)),
            "36_extra_dots": int((a36 & ~a32).sum())},
        "sites": site_results,
        "comparisons": comparisons,
        "limitations": ["No pre-placement surface or full registry was audited.",
                        "Historical score claims are not organizer receipts.",
                        "No new candidate was created, scored or authorized."],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    ap.add_argument("--fetch", action="store_true", help="Fetch missing pinned assets with gh")
    ap.add_argument("--output", type=Path, default=ROOT / "docs/data/focus_audit.json")
    args = ap.parse_args()
    result = run(args.manifest, args.cache, args.fetch)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"result": "audit complete; no upload authorized", "geometry": result["geometry"],
                      "forensics": result["forensics"], "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

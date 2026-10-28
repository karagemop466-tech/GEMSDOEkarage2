#!/usr/bin/env python3
"""Audit nine historical dot rasters and one lattice witness; never build a prediction.

The input template is an owner mirror, not an authenticated organizer template.
Within-three-pixels means Euclidean distance <= 3 pixels, including the boundary.
A single exceeding reference is sufficient to prove a duplicate, but this limited
set cannot certify complete-registry uniqueness. Binary Spearman is computed
exactly over every in-footprint pixel (equivalent to the phi coefficient).
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from restore_references import digest  # noqa: E402
from raster_integrity import require_single_file_dataset  # noqa: E402


def verify_sha(path: Path, expected: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}; run scripts/restore_references.py")
    actual = digest(path)
    if actual != expected:
        raise ValueError(f"SHA-256 mismatch for {path}: expected {expected}, got {actual}")


def grid(ds):
    return (ds.shape, ds.crs, ds.transform)


def phi(n: int, n_a: int, n_b: int, n_both: int) -> float:
    """Exact Spearman rank correlation for two nonconstant binary arrays."""
    denominator = math.sqrt(n_a * n_b * (n - n_a) * (n - n_b))
    if denominator == 0:
        raise ValueError("A constant binary reference has undefined Spearman correlation")
    return (n * n_both - n_a * n_b) / denominator


def audit(input_dir: Path, manifest: dict) -> dict:
    template = input_dir / "mirror-sample.tif"
    labels = input_dir / "mirror-labels.tif"
    witness_path = input_dir / "r13-lattice.tif"
    verify_sha(template, manifest["mirror_template"]["sha256"])
    verify_sha(labels, manifest["mirror_labels"]["sha256"])
    verify_sha(witness_path, manifest["witness"]["sha256"])

    with rasterio.open(template) as source:
        require_single_file_dataset(source, template)
        expected = grid(source)
        arr = source.read(1)
        # This pinned mirror explicitly uses NaN outside. Do not assume a finite
        # nodata sentinel represents a valid cell in a different template.
        footprint = np.isfinite(arr) & (source.read_masks(1) > 0)
        template_positive = (arr > 0) & footprint
        template_info = {"shape": list(source.shape), "crs": str(source.crs),
                         "transform": list(source.transform)[:6], "sha256": digest(template)}
        require_single_file_dataset(source, template)
    verify_sha(template, manifest["mirror_template"]["sha256"])
    n_foot = int(footprint.sum())
    if not n_foot:
        raise ValueError("Empty template footprint")
    with rasterio.open(labels) as source:
        require_single_file_dataset(source, labels)
        if grid(source) != expected or source.count != 1:
            raise ValueError("Labels differ from template grid")
        label_pos = (source.read(1) > 0) & footprint
        require_single_file_dataset(source, labels)
    verify_sha(labels, manifest["mirror_labels"]["sha256"])
    template_info.update({"footprint_pixels": n_foot,
                          "positive_pixels": int(template_positive.sum()),
                          "positive_pixels_equal_label_mask": bool(np.array_equal(template_positive, label_pos))})
    del arr, template_positive  # Keep the known-label mask for the lineage distance check.

    def load_ref(path: Path, expected_hash: str):
        verify_sha(path, expected_hash)
        with rasterio.open(path) as ds:
            require_single_file_dataset(ds, path)
            if grid(ds) != expected:
                raise ValueError(f"Grid mismatch: {path}")
            if ds.count != 1:
                raise ValueError(f"Not a single-band raster: {path}")
            raster = ds.read(1)
            inside = raster[footprint]
            if not np.isfinite(inside).all() or np.any((inside < 0) | (inside > 1)):
                raise ValueError(f"Non-finite or out-of-range reference inside footprint: {path}")
            if not np.isin(inside, (0, 1)).all():
                raise ValueError(f"Binary historical comparison required, got continuous values: {path}")
            dots = (raster > 0) & footprint
            require_single_file_dataset(ds, path)
            verify_sha(path, expected_hash)
            return dots, {"sha256": expected_hash, "dot_count": int(dots.sum()),
                          "single_band": True, "dtype": ds.dtypes[0],
                          "inside_finite_and_in_range": True,
                          "outside_all_nan": bool(np.isnan(raster[~footprint]).all()),
                          "whole_array_finite_in_range": bool(np.isfinite(raster).all() and
                              np.all((raster >= 0) & (raster <= 1)))}

    lattice, lattice_info = load_ref(witness_path, manifest["witness"]["sha256"])
    lattice_distance = distance_transform_edt(~lattice)
    covered = (lattice_distance <= 3.0) & footprint
    uncovered = int((footprint & ~covered).sum())
    coverage = int(covered.sum())

    masks: dict[str, np.ndarray] = {}
    info: dict[str, dict] = {}
    for row in manifest["sites"]:
        name = row["site"]
        if name in masks:
            raise ValueError(f"Duplicate manifest site {name}")
        masks[name], info[name] = load_ref(input_dir / "focus" / f"{name}.tif", row["sha256"])
        if not 0 < info[name]["dot_count"] < n_foot:
            raise ValueError(f"Cannot audit an empty or constant reference: {name}")

    pairs = []
    # Reuse each reference's distance transform for every directional candidate.
    for reference, ref_mask in masks.items():
        near = distance_transform_edt(~ref_mask) <= 3.0
        n_b = info[reference]["dot_count"]
        for candidate, mask in masks.items():
            if candidate == reference:
                continue
            n_a = info[candidate]["dot_count"]
            matched = int((mask & near).sum())
            both = int((mask & ref_mask).sum())
            pairs.append({"candidate": candidate, "reference": reference,
                          "matches_within_3px": matched, "candidate_dots": n_a,
                          "overlap_fraction": matched / n_a,
                          "binary_spearman_full_footprint": phi(n_foot, n_a, n_b, both)})

    rows = []
    for name, mask in masks.items():
        comparisons = [p for p in pairs if p["candidate"] == name]
        closest = max(comparisons, key=lambda p: p["overlap_fraction"])
        strongest = max(comparisons, key=lambda p: p["binary_spearman_full_footprint"])
        strongest_abs = max(comparisons, key=lambda p: abs(p["binary_spearman_full_footprint"]))
        matched_witness = int((mask & covered).sum())
        n = info[name]["dot_count"]
        rows.append({"site": name, **info[name],
                     "lattice_matches_within_3px": matched_witness,
                     "lattice_overlap_fraction": matched_witness / n,
                     "closest_focus_site": closest["reference"],
                     "max_focus_overlap_fraction": closest["overlap_fraction"],
                     "max_focus_binary_spearman": strongest["binary_spearman_full_footprint"],
                     "max_abs_focus_binary_spearman": abs(strongest_abs["binary_spearman_full_footprint"]),
                     "surface_comparison": "NOT AVAILABLE; not tested",
                     "literal_result": "DUPLICATE_STOP" if (
                         10 * matched_witness > 7 * n or
                         10 * closest["matches_within_3px"] > 7 * n or
                         strongest["binary_spearman_full_footprint"] > 0.90
                     ) else "INCOMPLETE_REGISTRY_NOT_A_PASS"})

    m25, m30, m31, m32, m36 = (masks[f"GEMSDOE{k}"] for k in (25, 30, 31, 32, 36))
    removed_31_to_32 = m31 & ~m32
    known_distance = distance_transform_edt(~label_pos)
    champion_n = info["GEMSDOE32"]["dot_count"]
    lower_matches = max(0, champion_n - uncovered)
    return {
        "kind": "GEOMETRY-AUDIT (not a score or experiment)",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Nine pinned historical rasters and the 13GEMSDOE witness; not the complete registry. Original score surfaces and organizer receipts are unavailable.",
        "template": template_info,
        "witness": {**lattice_info, "covered_footprint_pixels_at_3px": coverage,
                    "uncovered_footprint_pixels": uncovered,
                    "first_dot_budget_guaranteed_to_exceed_70_percent": (10 * uncovered) // 3 + 1,
                    "champion_sized_budget": champion_n,
                    "minimum_matches_for_champion_sized_budget": lower_matches,
                    "minimum_overlap_for_champion_sized_budget": lower_matches / champion_n},
        "historical_final_dots": rows,
        "pairwise_directional_comparisons": pairs,
        "lineage": {"g25_g30_identical_in_footprint": bool(np.array_equal(m25, m30)),
                    "g32_subset_of_g31": bool(not np.any(m32 & ~m31)),
                    "g31_dots_removed_in_g32": int(removed_31_to_32.sum()),
                    "g31_removed_at_known_fault_distance_gt1_le2_pixels": int(
                        (removed_31_to_32 & (known_distance > 1) & (known_distance <= 2)).sum()),
                    "g32_dots_within_2_pixels_of_mirrored_known_faults": int((m32 & (known_distance <= 2)).sum()),
                    "g32_dots_not_in_g31": int((m32 & ~m31).sum()),
                    "g32_subset_of_g36": bool(not np.any(m32 & ~m36)),
                    "g36_dots_not_in_g32": int((m36 & ~m32).sum())},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=ROOT / ".cache" / "input")
    parser.add_argument("--manifest", type=Path, default=ROOT / "registry" / "focus_sites.json")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence" / "geometry-audit.json")
    args = parser.parse_args()
    try:
        result = audit(args.input_dir, json.loads(args.manifest.read_text()))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"output": str(args.output), "template": result["template"],
                          "witness": result["witness"], "lineage": result["lineage"]}, indent=2))
    except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
        print(f"Geometry audit failed closed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

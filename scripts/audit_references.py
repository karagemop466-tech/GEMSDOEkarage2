#!/usr/bin/env python3
"""Reproduce the nine-file and literal-registry geometry audit (not a score).

This imports the hash-pinned shared template for novelty and format checks.
It never places dots, trains a model, writes a candidate, or selects a slot.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/reference-sources.json"
DEFAULT_CACHE = ROOT / ".cache/research"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def checked_path(cache: Path, rel: str, expected: str) -> Path:
    root = cache.resolve()
    p = (root / rel).resolve()
    if not p.is_relative_to(root) or not p.is_file() or sha256_file(p) != expected:
        raise ValueError(f"Missing, unsafe or modified pinned file: {rel}")
    return p


def load_shared(cache: Path, spec: dict):
    for item in spec["template"]["files"]:
        checked_path(cache, "shared-template/" + item["path"], item["sha256"])
    template_src = str((cache / "shared-template/src").resolve())
    # Refuse preloaded modules from another copy; this keeps provenance honest.
    if "gems" in sys.modules and not str(getattr(sys.modules["gems"], "__file__", "")).startswith(template_src + "/"):
        raise RuntimeError("A different gems module is already loaded")
    if template_src not in sys.path:
        sys.path.insert(0, template_src)
    return importlib.import_module("gems.novelty"), importlib.import_module("gems.submission")


def geometry_stop(uncovered: int, budget: int, limit_numerator: int = 7, limit_denominator: int = 10) -> dict:
    """Pigeonhole lower bound for ANY set of distinct in-footprint dots.

    The stop is strict (>70%, not >=70%); exact integer comparison avoids
    floating-point boundary mistakes. It is not a geological performance test.
    """
    if (type(uncovered) is not int or type(budget) is not int or uncovered < 0 or budget <= 0
            or limit_numerator < 0 or limit_denominator <= 0 or limit_numerator > limit_denominator):
        raise ValueError("Nonnegative uncovered count, positive budget, and a probability limit required")
    unavoidable = max(0, budget - uncovered)
    forced = unavoidable * limit_denominator > budget * limit_numerator
    return {
        "budget_dots": budget,
        "uncovered_footprint_cells": uncovered,
        "min_dots_within_3px": unavoidable,
        "min_fraction_within_3px": unavoidable / budget,
        "forced_duplicate_stop": forced,
        "limit_fraction": limit_numerator / limit_denominator,
    }


def run_audit(cache: Path, spec: dict, budget: int = 37654) -> dict:
    novelty, submission = load_shared(cache, spec)
    inputs = {
        Path(item["cache_path"]).stem: checked_path(cache, item["cache_path"], item["sha256"])
        for item in spec["inputs"]
    }
    with rasterio.open(inputs["labels"]) as source, rasterio.open(inputs["sample"]) as sample:
        labels = source.read(1)
        template = sample.read(1)
        if source.count != 1 or sample.count != 1 or (source.shape, source.crs, source.transform) != (sample.shape, sample.crs, sample.transform):
            raise ValueError("Label mirror and sample mirror have different grids")
        sample_grid = (sample.shape, sample.crs, sample.transform)
    if not np.isin(labels, [-1, 0, 1]).all():
        raise ValueError("Unexpected label encoding")
    footprint = labels >= 0
    if not footprint.any() or not np.array_equal(np.isfinite(template), footprint):
        raise ValueError("The two mirrored footprints disagree")
    if np.any((template[footprint] < 0) | (template[footprint] > 1)):
        raise ValueError("Template mirror is out of range in footprint")

    with rasterio.open(inputs["lattice"]) as ref:
        if ref.count != 1 or (ref.shape, ref.crs, ref.transform) != sample_grid:
            raise ValueError("Lattice grid differs from template")
        raw = ref.read(1)
    if not np.isfinite(raw[footprint]).all() or not np.isin(raw[footprint], [0, 1]).all():
        raise ValueError("The lattice is not finite binary inside the footprint")
    lattice = np.isfinite(raw) & (raw > 0) & footprint
    geometry = novelty.classify_space_filling_control(footprint, lattice, candidate_dot_count=budget)
    bound = geometry_stop(int(geometry["footprint_3px_uncovered_pixels"]), budget)

    masks = {}
    results = []
    for item in spec["references"]:
        path = checked_path(cache, item["cache_path"], item["sha256"])
        with rasterio.open(path) as ref:
            if ref.count != 1 or (ref.shape, ref.crs, ref.transform) != sample_grid:
                raise ValueError(f"Reference grid mismatch: {item['site']}")
            data = ref.read(1)
        if not np.isfinite(data[footprint]).all() or not np.isin(data[footprint], [0, 1]).all():
            raise ValueError(f"Reference is not finite binary in footprint: {item['site']}")
        if np.any(np.isfinite(data[~footprint]) & (data[~footprint] > 0)):
            raise ValueError(f"Reference emits outside footprint: {item['site']}")
        dots = (data > 0) & footprint
        if not dots.any():
            raise ValueError(f"Empty reference: {item['site']}")
        masks[item["site"]] = dots
        validation = submission.check_variants(path, inputs["sample"])
        overlap = novelty.dot_overlap(dots, lattice)["candidate_within_3px_of_reference"]
        results.append({
            "site": item["site"], "historical_file": Path(item["path"]).name,
            "source_url": item["source_url"], "pinned_ref": item["ref"],
            "sha256": item["sha256"], "in_footprint_dots": int(dots.sum()),
            "fraction_within_3px_of_lattice": overlap,
            "local_grid_and_interior_format_valid": validation["format_valid"],
            "outside_is_nan_official_text_diagnostic": validation["checks"]["outside_is_nan_official_text"]["pass"],
            "strict_whole_array_range_diagnostic": validation["checks"]["variant_strict_whole_array_no_nan_allowed"]["pass"],
            "leaderboard_estimate": None,
            "organizer_receipt": None,
            "submission_authorized": False,
        })
    pairs = {}
    for candidate in masks:
        for reference in masks:
            if candidate != reference:
                pairs[f"{candidate}->{reference}"] = novelty.dot_overlap(
                    masks[candidate], masks[reference]
                )["candidate_within_3px_of_reference"]
    for row in results:
        candidate = row["site"]
        within = {k.split("->")[1]: v for k, v in pairs.items() if k.startswith(candidate + "->")}
        if len(within) != len(masks) - 1 or any(v is None for v in within.values()):
            raise ValueError("Incomplete pairwise comparison")
        row["maximum_overlap_other_focus"] = max(within.values())
        row["closest_other_focus"] = max(within, key=within.get)
        row["unique_vs_other_eight"] = not any(v > 0.70 for v in within.values())

    distance_known = distance_transform_edt(labels != 1)
    filtered = masks["GEMSDOE25"] & (distance_known > 2)
    relations = {
        "gems25_and_gems30_equal_inside_footprint": bool(np.array_equal(masks["GEMSDOE25"], masks["GEMSDOE30"])),
        "gems32_equals_gems25_after_gt_2px_known_fault_filter": bool(np.array_equal(masks["GEMSDOE32"], filtered)),
        "gems25_dots_removed_to_make_gems32": int(masks["GEMSDOE25"].sum() - masks["GEMSDOE32"].sum()),
    }
    return {
        "schema_version": 1,
        "session_scope": "Independent geometry/format audit; separate from the prior merged H1 experiment.",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "type": "GEOMETRY AND FORMAT AUDIT — NOT HOLDOUT-DTI OR ORGANIZER SCORE",
        "scope": spec["scope"],
        "shared_template_ref": spec["template"]["files"][0]["ref"],
        "footprint_pixels": int(footprint.sum()),
        "sample_mirror_diagnostic": {
            "positive_pixels": int((template[footprint] > 0).sum()),
            "equals_mirrored_labels_inside_footprint": bool(np.array_equal(template[footprint], labels[footprint])),
            "organizer_text_says_sample_predicts_total_fault_absence": True,
            "source_url": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format",
            "assessment": "Unresolved discrepancy: this hash-pinned owner mirror is not authenticated as the organizer's current sample."
        },
        "registered_lattice_positive_pixels": int(lattice.sum()),
        "lattice_sha256": sha256_file(inputs["lattice"]),
        "geometry": geometry, "budget_bound": bound,
        "reference_files": results, "directional_pairwise_overlap": pairs,
        "measured_family_relations": relations,
        "limitations": [
            "The nine files and lattice are a partial registry; a pass would not prove global uniqueness.",
            "Mirrored sample, labels, and features are not authenticated directly from DrivenData.",
            "Historical reference checks do not validate a new surface, a holdout, or a portal upload.",
            "The dot-budget proof applies to this budget and does not rule out every smaller raster.",
        ],
        "new_model_or_submission": False,
        "submission_authorized": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    p.add_argument("--budget", type=int, default=37654, help="Pre-registered candidate budget for the geometry bound")
    p.add_argument("--output", type=Path, help="Optional JSON result; parent must already exist")
    args = p.parse_args()
    report = run_audit(args.cache, json.loads(MANIFEST.read_text()), args.budget)
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text)


if __name__ == "__main__":
    main()

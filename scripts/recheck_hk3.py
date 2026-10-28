#!/usr/bin/env python3
"""Independently re-read HK3 and a pinned duplicate witness; never make a TIFF.

Requires ``python scripts/bootstrap_research.py`` first. The unchanged shared
GEMSDOE24 template performs the directional overlap and variant-format checks.
A single counterexample is sufficient to stop; this is not a complete registry
or an organizer-authenticated format/score check. No model is trained or run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.audit_references import checked_path, geometry_stop, load_shared, sha256_file
from scripts.raster_integrity import require_single_file_dataset

CACHE = ROOT / ".cache/research"
OUTPUTS = (ROOT / "evidence/hk3/literal_recheck.json", ROOT / "docs/evidence/hk3/literal_recheck.json")


def audit(cache: Path = CACHE) -> dict:
    spec = json.loads((ROOT / "research/reference-sources.json").read_text())
    novelty, submission = load_shared(cache, spec)
    inputs = {Path(x["cache_path"]).stem: checked_path(cache, x["cache_path"], x["sha256"])
              for x in spec["inputs"]}
    card = json.loads((ROOT / "evidence/hk3/run_card.json").read_text())
    registry = json.loads((ROOT / "evidence/hk3/registry_audit.json").read_text())
    candidate = ROOT / card["raster"]["file"]
    sha = sha256_file(candidate)
    if sha != card["raster"]["sha256"] or sha != registry["candidate_file_sha256"]:
        raise ValueError("Candidate bytes do not match both independent historical receipts")
    with rasterio.open(inputs["sample"]) as s, rasterio.open(inputs["labels"]) as lab:
        require_single_file_dataset(s, inputs["sample"])
        require_single_file_dataset(lab, inputs["labels"])
        grid = (s.shape, s.crs, s.transform)
        if s.count != 1 or lab.count != 1 or grid != (lab.shape, lab.crs, lab.transform):
            raise ValueError("Sample and labels do not share a one-band grid")
        template = s.read(1)
        footprint = np.isfinite(template) & (s.read_masks(1) > 0)
        labels = lab.read(1)
        if not np.array_equal(footprint, labels >= 0):
            raise ValueError("Mirrored sample and labels disagree on footprint")
        require_single_file_dataset(s, inputs["sample"])
        require_single_file_dataset(lab, inputs["labels"])
    with rasterio.open(inputs["lattice"]) as ref:
        require_single_file_dataset(ref, inputs["lattice"])
        if ref.count != 1 or (ref.shape, ref.crs, ref.transform) != grid:
            raise ValueError("Witness grid mismatch")
        raw = ref.read(1)
        if not np.isfinite(raw[footprint]).all() or not np.isin(raw[footprint], [0, 1]).all():
            raise ValueError("Witness is not finite and binary inside the mirrored footprint")
        witness = (raw > 0) & footprint
        require_single_file_dataset(ref, inputs["lattice"])
    with rasterio.open(candidate) as ds:
        require_single_file_dataset(ds, candidate)
        if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != grid:
            raise ValueError("Candidate grid mismatch")
        data = ds.read(1)
        mask = ds.read_masks(1)
        require_single_file_dataset(ds, candidate)
    if sha256_file(candidate) != sha:
        raise ValueError("Candidate changed during inspection")
    dots = (data > 0) & footprint
    if not dots.any() or not np.isin(data[footprint], [0, 1]).all():
        raise ValueError("Expected a nonempty, finite binary HK3 raster")
    stats = novelty.dot_overlap(dots, witness, radius_px=3.0)
    # Full-footprint Spearman, not a sampled statistic; both arrays are binary.
    rho = novelty.correlation(data[footprint], raw[footprint])
    if rho is None:
        raise ValueError("Constant arrays have undefined rank correlation")
    count = int(stats["candidate_dots"])
    overlap = float(stats["candidate_within_3px_of_reference"])
    matched = int(round(overlap * count))
    # Confirm the strict threshold using integer arithmetic, not rounded display text.
    stopped = 10 * matched > 7 * count
    geometry = novelty.classify_space_filling_control(footprint, witness, candidate_dot_count=count)
    bound = geometry_stop(int(geometry["footprint_3px_uncovered_pixels"]), count)
    variant = submission.check_variants(candidate, inputs["sample"])
    inside = data[footprint]
    outside = data[~footprint]
    validations = {
        "single_band_float32": ds.dtypes == ("float32",),
        "shape_crs_transform_match_owner_mirror": True,
        "no_masked_pixels_inside_owner_footprint": bool(np.all(mask[footprint] > 0)),
        "no_nan_or_infinity_inside_owner_footprint": bool(np.isfinite(inside).all()),
        "inside_values_in_0_1": bool(np.all((inside >= 0) & (inside <= 1))),
        "whole_array_finite_in_0_1": bool(np.isfinite(data).all() and np.all((data >= 0) & (data <= 1))),
        "outside_mirror_footprint_all_nan": bool(np.isnan(outside).all()),
        "positives_outside_mirror_footprint": int(np.sum(data[~footprint] > 0)),
        "positives_on_mirrored_catalogue": int(np.sum((data > 0) & (labels == 1))),
        "shared_variant_interior_format_valid": bool(variant["format_valid"]),
    }
    prior = [r for r in registry["rows"] if r.get("sha256") == sha256_file(inputs["lattice"])]
    if not prior or not all(
        abs(float(r["my_dots_within_3px_of_theirs"]) - overlap) < 1e-12
        and abs(float(r["spearman_full_footprint"]) - rho) < 1e-12 for r in prior
    ):
        raise ValueError("Saved HK3 registry receipt disagrees with the independent witness recheck")
    # Re-check hashes after all reads; a mirror changed while auditing is not a receipt.
    for entry in spec["inputs"]:
        checked_path(cache, entry["cache_path"], entry["sha256"])
    if sha256_file(candidate) != sha:
        raise ValueError("Candidate changed during validation")
    return {
        "schema": "gems.hk3-literal-recheck.v1",
        "evidence_class": "GEOMETRY AND LOCAL FORMAT AUDIT; NOT A SCORE",
        "method": "Unchanged hash-pinned shared GEMSDOE24 novelty.dot_overlap and submission.check_variants; saved TIFF bytes re-read.",
        "candidate_file": card["raster"]["file"],
        "candidate_sha256": sha,
        "mirror_sample_sha256": sha256_file(inputs["sample"]),
        "mirror_labels_sha256": sha256_file(inputs["labels"]),
        "witness_sha256": sha256_file(inputs["lattice"]),
        "witness_source": "https://github.com/buffedlizard55-lab/13GEMSDOE",
        "candidate_positive_inside_footprint": count,
        "matched_within_3_pixels": matched,
        "overlap_fraction": overlap,
        # BLAS reduction order can differ by platform; 12 decimals retains far
        # more precision than needed for the 0.90 gate and makes receipts stable.
        "full_footprint_spearman_vs_lattice": round(rho, 12),
        "rank_correlation_scope": "Full mirrored footprint, saved binary raster values; not a complete registry scan",
        "threshold_fraction_strictly_exceeded": 0.70,
        "duplicate_stop": stopped,
        "geometry": geometry,
        "candidate_budget_bound": bound,
        "validation": validations,
        "original_registry_comparisons_with_same_witness": len(prior),
        "original_registry_complete_accessible_scan": registry["complete_accessible_scan"],
        "preplacement_surface_rechecked": False,
        "preplacement_reason": "The original full surface/support and a valid prior surface receipt were not restored; final-dot failure alone requires STOP.",
        "organizer_inputs_authenticated": False,
        "organizer_receipt_available": False,
        "portal_acceptance": None,
        "slot_authorized": False,
        "verdict": "negative" if stopped else "incomplete",
        "limitations": [
            "The owner mirrors and footprint are hash-pinned but not authenticated against DrivenData.",
            "This is one registered witness, not proof that the full registry was checked.",
            "A dense witness can flag unrelated rasters; under the supplied literal rule it still requires a stop.",
            "The official outside-footprint convention and portal behavior remain unresolved.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the saved receipt differs from this recheck")
    args = parser.parse_args()
    result = audit()
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.check:
        if any(not p.is_file() or p.read_text() != text for p in OUTPUTS):
            raise SystemExit("HK3 recheck receipt is stale")
    else:
        for path in OUTPUTS:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(json.dumps({"verdict": result["verdict"], "matched": result["matched_within_3_pixels"],
                      "candidate_dots": result["candidate_positive_inside_footprint"],
                      "overlap": result["overlap_fraction"], "slot_authorized": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Record current prerequisites and fail closed. This never selects or publishes a TIFF."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from bootstrap_template import verify  # noqa: E402
from restore_references import digest  # noqa: E402


def inspect(root: Path = ROOT) -> dict:
    manifest = json.loads((root / "registry/template_tools.json").read_text())
    cache = root / ".cache"
    try:
        verify(manifest, cache / "template32")
        shared_tools = "available; selected critical files SHA-256 pinned"
    except (OSError, ValueError):
        shared_tools = "missing or changed"

    hashes = {
        "training_features.tif": "4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5",
        "labels.tif": "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
        "existing_faults.tif": "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
        "sample_submission.tif": "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc",
    }
    data = {}
    for name, expected in hashes.items():
        path = cache / "data" / name
        data[name] = "mirror hash matches" if path.is_file() and digest(path) == expected else "missing or hash mismatch"
    try:
        stack = np.load(cache / "work/feature_stack.npy", mmap_mode="r", allow_pickle=False)
        receipt = json.loads((cache / "work/feature_receipt.json").read_text())
        stack_ok = (stack.shape == (3730, 3292, 35) and stack.dtype == np.float32 and
                    receipt.get("n_channels") == 35 and len(receipt.get("channels", [])) == 35)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        stack_ok = False
    try:
        geom = json.loads((root / "evidence/geometry-audit.json").read_text())
        witness = geom["witness"]
        expected_witness = json.loads((root / "registry/focus_sites.json").read_text())["witness"]["sha256"]
        geometry_ok = witness["sha256"] == expected_witness
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        witness, geometry_ok = None, False

    # An assignment file can record future coordination; it cannot by itself
    # authorize an experiment or overcome the other scientific/registry gates.
    lane_path = root / "registry/assigned_lane.json"
    try:
        lane = json.loads(lane_path.read_text())
        lane_present = all(isinstance(lane.get(key), str) and lane[key].strip()
                           for key in ("method_paragraph", "assignment_source"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        lane_present = False
    blockers = [
        "The complete current cross-session registry and its independent completeness evidence are unavailable.",
        "No frozen, same-evaluator best with matched folds and baseline artifacts is present in this checkout.",
        "The organizer-authenticated example and footprint are unavailable; the owner mirror differs from the documented absence example.",
        "No feature canaries, fold-local candidate holdout, candidate uniqueness audit, saved-byte candidate validator, or separate slot selection exists.",
        "The shared evaluator and writer binarize positive float inputs; they are not safe for continuous probabilities without an upstream fix.",
    ]
    if not lane_present:
        blockers.insert(0, "No single method paragraph / assignment source was supplied for this parallel lane.")
    else:
        blockers.insert(0, "An assignment file exists but this review has not audited or executed that lane.")
    if shared_tools.startswith("missing"):
        blockers.append("Pinned shared template tools are not available.")
    if not all(v == "mirror hash matches" for v in data.values()):
        blockers.append("The pinned core mirror is missing or changed.")
    if not stack_ok:
        blockers.append("The shared feature cache is missing, incomplete, or the wrong shape.")
    if not geometry_ok:
        blockers.append("The pinned geometry-witness audit is missing or inconsistent.")

    return {
        "schema_version": 1,
        "scope": "This independent follow-on review only; a separate parallel H1 research surface and negative experiment card exist in evidence/run_card.json.",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_count": 0,
        "weekly_slots_used": 0,
        "hypothesis": ("Assignment file present, not reviewed; proposed signed cross-profile co-variation remains backlog."
                       if lane_present else "No assigned lane; proposed signed cross-profile co-variation is research backlog only."),
        "mechanism": "Compare flank changes across magnetic, gravity and conductive edges; not implemented or tested here.",
        "named_non_fault_mimic": "Intrusive or volcanic lithologic contacts and saline basin boundaries.",
        "holdout_dti": {"value": None, "evaluator_version": None, "withheld_positives": None,
                        "confidence_interval_95": None, "reason": "no experiment run"},
        "registry_comparison": {
            "candidate_surface_rank_correlation": None, "candidate_surface_overlap": None,
            "candidate_final_rank_correlation": None, "candidate_final_overlap": None,
            "reason": "no candidate or full registry; historical reference geometry is in geometry-audit.json",
            "witness_uncovered_footprint_pixels": witness["uncovered_footprint_pixels"] if geometry_ok else None,
            "first_provably_blocked_dot_budget": witness["first_dot_budget_guaranteed_to_exceed_70_percent"] if geometry_ok else None,
        },
        "raster_sha256": None,
        "validator_output": {"status": "NOT RUN: no candidate TIFF", "no_nan_inside": None,
                             "values_in_0_1": None, "crs_shape_transform_match": None},
        "submission_name": None, "submission_note": None,
        "estimated_leaderboard_score": None,
        "verdict": "negative", "download_approved": False, "upload_approved": False,
        "resources": {"shared_template": shared_tools, "core_data": data,
                      "shared_feature_cache": "available (shape and dtype checked)" if stack_ok else "missing or invalid",
                      "template_and_data_provenance": "owner mirror; not organizer authenticated; scratch cache is non-persistent"},
        "blockers": blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/run-card.json")
    args = parser.parse_args()
    try:
        card = inspect()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(card, indent=2, allow_nan=False) + "\n")
        print(json.dumps(card, indent=2, allow_nan=False))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Preflight failed closed: {exc}", file=sys.stderr)
    return 1  # This preflight cannot authorize a file or select a slot.


if __name__ == "__main__":
    raise SystemExit(main())

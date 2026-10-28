#!/usr/bin/env python3
"""Reproduce the HK3 negative protocol-review card without training or placement.

Saved TIFF checks are executed now. All holdout and registry metrics are explicitly
inherited from historical receipts, never presented as newly measured scores.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.audit_public_downloads import audit  # noqa: E402
from scripts.readiness import assess  # noqa: E402

OUTPUT = "hk3-protocol-review-run-card-2026-10-28.json"


def read(rel):
    return json.loads((ROOT / rel).read_text())


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def review():
    card_rel = "evidence/hk3/run_card.json"
    card = read(card_rel)
    old = read("evidence/hk3/history/run_card-before-protocol-correction.json")
    selector = read("evidence/hk3/selector_result.json")
    registry = read("evidence/hk3/registry_audit.json")
    inventory = audit()
    raster = card["raster"]
    entry = next(row for row in inventory["artifacts"] if row["file"] == raster["file"])
    h = card["holdout"]["candidate_same_budget_as_incumbent_b110"]
    stopped = (card.get("verdict") == "negative" and card.get("protocol_stop_triggered") is True
               and card["gates"].get("literal_rule_exception_applied") is False
               and selector.get("verdict") == "negative" and selector.get("ok_to_submit") is False
               and selector.get("slot_authorized") is False)
    checks = {
        "corrected_negative_card_and_selector": stopped,
        "common_readiness_rejects_current_card": assess(card)["verdict"] == "negative",
        "common_readiness_rejects_original_promotion": assess(old)["verdict"] == "negative",
        "raster_unchanged_since_original_card": entry["raster_sha256"] == raster["sha256"] == old["raster"]["sha256"],
        "historical_registry_bound_to_same_tiff": registry["candidate_file_sha256"] == raster["sha256"],
        "saved_download_checks_pass_research_only": entry["status"] == "VERIFIED_RESEARCH_ONLY",
        "all_downloads_research_only": inventory["inventory_status"] == "PASS_RESEARCH_ONLY",
    }
    if not all(checks.values()):
        raise ValueError(f"Protocol-review integrity failed: {checks}")
    return {
        "schema": "gems.hk3_protocol_review.v1",
        "hypothesis": "No new geological hypothesis tested; independently enforce HK3's recorded mandatory registry stop.",
        "mechanism": "Revoke the unauthorized literal-rule exception and bind research-only publication to the saved TIFF bytes.",
        "named_non_fault_process": "Lithologic contacts, pluvial shorelines, terrace risers and flight-line striping may mimic HK3's structural edges; not newly tested here.",
        "holdout_dti": None,
        "holdout_ci95": None,
        "holdout_status": "Not rerun. No new HOLDOUT-DTI or ORGANIZER-CONFIRMED score.",
        "historical_holdout": {
            "evidence_class": "HOLDOUT-DTI, ARCHIVED NOT RERUN",
            "evaluator_version": h["evaluator_version"],
            "withheld_positive_pixels": h["withheld_positive_pixels"],
            "dti": h["dti"], "ci95": h["ci95"],
            "source": card_rel, "source_sha256": sha(card_rel),
            "caveat": "K2 comparison only; no paired win over the later K3 best or new verification of whole-segment splits.",
        },
        "correlation_overlap_vs_registry": {
            "status": "ARCHIVED GEOMETRY, NOT RERUN",
            "source": "evidence/hk3/registry_audit.json",
            "source_sha256": sha("evidence/hk3/registry_audit.json"),
            "max_abs_spearman": abs(registry["worst_spearman_full_footprint"]),
            "max_final_dot_overlap_3px": registry["worst_dot_overlap"],
            "surface_clearance_before_placement_verified": False,
            "registry_coverage_complete": False,
            "references_expected": registry["registry_rasters_expected"],
            "references_checked": registry["registry_rasters_checked"],
            "literal_duplicate_stop": True,
        },
        "raster": raster["file"],
        "raster_sha256": entry["raster_sha256"],
        "raster_status": "Existing research TIFF; unchanged. No unique eligible submission generated.",
        "validator_output": {
            "evidence_class": "SAVED-BYTE LOCAL FORMAT CHECK, NOT ORGANIZER ACCEPTANCE",
            "whole_array_finite": entry["checks"]["whole_array_finite"],
            "no_nan_inside_footprint": entry["checks"]["whole_array_finite"],
            "values_in_0_1": entry["checks"]["range_0_1"],
            "single_band_float32": entry["checks"]["single_band"] and entry["checks"]["float32"],
            "mirror_crs_match": entry["checks"]["mirror_crs_match"],
            "mirror_shape_match": entry["checks"]["mirror_shape_match"],
            "mirror_transform_match": entry["checks"]["mirror_transform_match"],
            "self_contained_tiff": entry["checks"]["self_contained_tiff"],
            "organizer_template_authenticated": False,
            "organizer_crs_shape_transform_match": None,
            "portal_acceptance": None,
            "diagnostics": entry["diagnostics"],
        },
        "submission_name": card["submission"]["name"],
        "submission_note": card["submission"]["note"],
        "protocol_stop_triggered": True,
        "new_experiments_run": 0,
        "submission_slots_used": 0,
        "slot_authorized": False,
        "leaderboard_estimate": None,
        "review_integrity_checks": checks,
        "verdict": "negative",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = json.dumps(review(), indent=2, allow_nan=False) + "\n"
    for path in (ROOT / "evidence" / OUTPUT, ROOT / "docs/evidence" / OUTPUT):
        if args.check:
            if not path.exists() or path.read_text() != text:
                raise SystemExit(f"Stale protocol-review card: {path.relative_to(ROOT)}")
        else:
            path.write_text(text)
    print("HK3 protocol correction verified: negative; research only; zero new experiments or slots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

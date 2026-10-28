"""Fail-closed selector gate for evidence cards.

This module validates evidence structure only; the shared evaluator, raster
validator, writer, and registry audit must produce the evidence it consumes.
It does not calculate DTI, inspect GeoTIFF bytes, or authorize a weekly slot.
"""
from __future__ import annotations

import math


def _finite_number(value: object) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        # Arbitrarily large JSON integers cannot be converted to a C double.
        # Treat them as invalid evidence rather than crashing the selector.
        return False


def _sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def _valid_interval(value: object, *, lower: float, upper: float) -> bool:
    return (
        isinstance(value, (list, tuple))
        and len(value) == 2
        and all(_finite_number(item) for item in value)
        and lower <= value[0] <= value[1] <= upper
    )


def assess(card: object) -> dict:
    """Return a fail-closed promotion verdict from a candidate evidence card.

    ``promote`` means the research gates described here pass. It never means a
    competition slot is selected or authorized; that decision is separate.
    """
    reasons: list[str] = []
    if not isinstance(card, dict):
        return {
            "verdict": "negative",
            "reasons": ["Evidence card must be a JSON object"],
            "slot_authorized": False,
        }

    # A later schema pass must never erase a recorded scientific/protocol stop.
    # These optional fields preserve compatibility with existing receipts; their
    # absence does not establish that the experiment's history was audited.
    if card.get("verdict") == "negative":
        reasons.append("Candidate already records a negative verdict")
    if "protocol_stop_triggered" in card and card["protocol_stop_triggered"] is not False:
        reasons.append("Recorded protocol stop or invalid stop declaration; stop")

    if not isinstance(card.get("lane"), str) or not card["lane"].strip() or not isinstance(card.get("template_commit"), str) or not card["template_commit"].strip():
        reasons.append("Missing method lane or shared template pin")
    assignment = card.get("lane_assignment")
    if (not isinstance(assignment, dict)
            or not isinstance(assignment.get("source"), str)
            or not assignment["source"].strip()
            or not _sha256(assignment.get("sha256"))):
        reasons.append("Lane assignment receipt missing or invalid")

    # A later passing scan cannot erase an earlier mandatory stop. These are
    # required evidence assertions, not provenance authentication performed here.
    protocol = card.get("protocol")
    if not isinstance(protocol, dict) or (
        protocol.get("preplacement_passed_before_emission") is not True
        or protocol.get("stop_triggered") is not False
    ):
        reasons.append("Pre-placement clearance missing or mandatory protocol stop triggered")
    preplacement_receipt = protocol.get("preplacement_receipt") if isinstance(protocol, dict) else None
    if (not isinstance(preplacement_receipt, dict)
            or preplacement_receipt.get("status") != "pass"
            or preplacement_receipt.get("checked_before_emission") is not True
            or not _sha256(preplacement_receipt.get("surface_sha256"))
            or not _sha256(preplacement_receipt.get("receipt_sha256"))):
        reasons.append("Hash-bound pre-placement surface receipt missing or invalid")

    if card.get("organizer_inputs_authenticated") is not True:
        reasons.append("Organizer input/template authenticity not established")
    provenance = card.get("organizer_provenance")
    if (not isinstance(provenance, dict)
            or not isinstance(provenance.get("receipt_id"), str)
            or not provenance["receipt_id"].strip()
            or not _sha256(provenance.get("input_manifest_sha256"))
            or not _sha256(provenance.get("template_sha256"))):
        reasons.append("Authenticated organizer provenance receipt or hashes missing")

    # The numerical/receipt schema cannot prove wall-clock truth, but it must
    # fail closed when the parallel-run budget is missing, malformed, exceeded,
    # or lacks a machine-readable receipt binding the recorded limits.
    budget = card.get("budget")
    if not isinstance(budget, dict):
        reasons.append("Experiment/runtime budget receipt missing")
    else:
        experiments = budget.get("experiments_used")
        elapsed = budget.get("elapsed_seconds")
        if (type(experiments) is not int or not 0 <= experiments <= 3
                or not _finite_number(elapsed) or not 0 <= elapsed <= 7200
                or not _sha256(budget.get("receipt_sha256"))):
            reasons.append("Experiment/runtime budget exceeded or receipt invalid")

    metric = card.get("metric")
    if not isinstance(metric, dict) or any(
        metric.get(key) != expected
        for key, expected in (
            ("alpha", 0.2),
            ("beta", 0.8),
            ("kernel_radius_m", 300),
            ("kernel", "triangular"),
        )
    ) or metric.get("pooled") is not True:
        reasons.append("Pooled DTI metric configuration does not match protocol")

    holdout = card.get("holdout")
    if not isinstance(holdout, dict):
        holdout = {}
    score = holdout.get("dti")
    count = holdout.get("withheld_positives")
    raw_ci = holdout.get("ci95")
    if (
        holdout.get("evidence_class") != "HOLDOUT-DTI"
        or not isinstance(holdout.get("evaluator_version"), str)
        or not holdout["evaluator_version"].strip()
        or not isinstance(count, int)
        or isinstance(count, bool)
        or count <= 0
        or not _finite_number(score)
        or not 0 <= score <= 1
        or not _valid_interval(raw_ci, lower=0, upper=1)
        or not raw_ci[0] <= score <= raw_ci[1]
    ):
        reasons.append("Missing or invalid HOLDOUT-DTI evidence")

    baseline = card.get("baseline_holdout_dti")
    delta_ci = holdout.get("paired_delta_ci95")
    if (
        not _finite_number(baseline)
        or not 0 <= baseline <= 1
        or not _finite_number(score)
        or score <= baseline
        or not _valid_interval(delta_ci, lower=-1, upper=1)
        or delta_ci[0] <= 0
    ):
        reasons.append("Has not beaten comparable current holdout best with paired 95% CI")

    # A bare baseline number is not evidence that the comparison used the same
    # folds and targets. These hashes identify frozen split and truth manifests;
    # callers still have to authenticate their contents independently.
    baseline_evidence = card.get("baseline_holdout")
    if not isinstance(baseline_evidence, dict):
        baseline_evidence = {}
    if (
        not isinstance(baseline_evidence.get("incumbent_id"), str)
        or not baseline_evidence["incumbent_id"].strip()
        or baseline_evidence.get("evidence_class") != "HOLDOUT-DTI"
        or not _finite_number(baseline_evidence.get("dti"))
        or baseline_evidence.get("dti") != baseline
        or not _valid_interval(baseline_evidence.get("ci95"), lower=0, upper=1)
        or not isinstance(baseline_evidence.get("withheld_positives"), int)
        or isinstance(baseline_evidence.get("withheld_positives"), bool)
        or baseline_evidence.get("evaluator_version") != holdout.get("evaluator_version")
        or baseline_evidence.get("withheld_positives") != count
        or not _sha256(holdout.get("split_manifest_sha256"))
        or baseline_evidence.get("split_manifest_sha256") != holdout.get("split_manifest_sha256")
        or not _sha256(holdout.get("truth_manifest_sha256"))
        or baseline_evidence.get("truth_manifest_sha256") != holdout.get("truth_manifest_sha256")
        or not _sha256(holdout.get("scoring_config_sha256"))
        or baseline_evidence.get("scoring_config_sha256") != holdout.get("scoring_config_sha256")
        or not _sha256(baseline_evidence.get("evidence_sha256"))
        or not _sha256(holdout.get("paired_comparison_receipt_sha256"))
    ):
        reasons.append("Comparable baseline holdout provenance missing or mismatched")
    if card.get("baseline_same_protocol_verified") is not True:
        reasons.append("Comparable incumbent protocol not verified")

    if card.get("hide_recover_protocol_verified") is not True:
        reasons.append("Buffered whole-segment hide-and-recover not verified")

    # Either direction can leak: AUC near zero is equivalent to a near-one AUC
    # after reversing feature sign. Accept raw AUC or max(AUC, 1-AUC).
    canaries = card.get("feature_auc")
    model_features = card.get("model_features")
    if (
        not isinstance(model_features, list)
        or not model_features
        or any(not isinstance(name, str) or not name.strip() for name in model_features)
        or len(set(model_features)) != len(model_features)
        or not isinstance(canaries, dict)
        or not canaries
        or set(canaries) != set(model_features)
        or any(not _finite_number(value) or not 0.10 <= value <= 0.90 for value in canaries.values())
    ):
        reasons.append("Feature leakage canary missing or failed, or feature inventory does not match")

    registry = card.get("registry")
    if not isinstance(registry, dict):
        registry = {}
    if registry.get("surface_pass_before_placement_verified") is not True:
        reasons.append("Pre-placement surface pass and stop sequence not verified")
    if registry.get("coverage_complete") is not True or not _sha256(registry.get("snapshot_sha256")):
        reasons.append("Registry coverage incomplete or snapshot hash invalid")
    if (not isinstance(preplacement_receipt, dict)
            or registry.get("surface_sha256") != preplacement_receipt.get("surface_sha256")):
        reasons.append("Pre-placement registry receipt is not bound to the audited surface hash")
    for stage in ("surface", "final_dots"):
        rows = registry.get(stage)
        if not isinstance(rows, list) or not rows:
            reasons.append(f"{stage}: no registry measurements")
            continue
        for row in rows:
            if not isinstance(row, dict):
                reasons.append(f"{stage}: invalid measurement")
                continue
            rho = row.get("rank_correlation")
            overlap = row.get("overlap_3px")
            if (
                not isinstance(row.get("reference"), str)
                or not row["reference"].strip()
                or not _finite_number(rho)
                or not -1 <= rho <= 1
                or not _finite_number(overlap)
                or not 0 <= overlap <= 1
            ):
                reasons.append(f"{stage}: invalid measurement")
            elif rho > 0.90 or overlap > 0.70:
                reasons.append(f"{stage}: duplicate lane; stop")

    # Surface and final-dot comparisons must cover the same unique reference
    # identifiers. This checks card consistency, not registry completeness or
    # the truth of the measurements supplied by the caller.
    surface, final = registry.get("surface"), registry.get("final_dots")
    if isinstance(surface, list) and isinstance(final, list) and surface and final:
        def references(rows):
            return [r.get("reference") for r in rows if isinstance(r, dict)]
        surface_refs, final_refs = references(surface), references(final)
        if (len(surface_refs) != len(surface) or len(final_refs) != len(final)
                or any(not isinstance(ref, str) or not ref.strip() for ref in surface_refs + final_refs)
                or len(set(surface_refs)) != len(surface_refs)
                or len(set(final_refs)) != len(final_refs)
                or set(surface_refs) != set(final_refs)):
            reasons.append("Surface and final-dot registry references do not match uniquely")

    validator = card.get("validator")
    if not isinstance(validator, dict):
        validator = {}
    if validator.get("organizer_template_authenticated") is not True:
        reasons.append("Organizer template authentication not verified")
    required_checks = (
        "single_band",
        "finite_inside",
        "range_0_1",
        "crs_match",
        "shape_match",
        "transform_match",
        "outside_nodata",
    )
    if any(validator.get(key) is not True for key in required_checks):
        reasons.append("Raster validation missing or failed")

    if not _sha256(card.get("raster_sha256")):
        reasons.append("Raster SHA256 missing or invalid")
    name = card.get("submission_name")
    note = card.get("submission_note")
    if (
        not isinstance(name, str)
        or not name.strip()
        or not isinstance(note, str)
        or not note.strip()
        or len(note) > 140
    ):
        reasons.append("Submission name/note invalid")

    return {
        "verdict": "negative" if reasons else "promote",
        "reasons": reasons,
        "slot_authorized": False,
    }

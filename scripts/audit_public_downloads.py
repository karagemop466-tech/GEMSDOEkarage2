#!/usr/bin/env python3
"""Re-read every published TIFF/ZIP and fail closed on unexpected downloads.

This is an integrity and local-format audit of the published files, not a model
evaluation. An upload candidate needs every literal hard gate to pass, a hash-bound
current assessment and selector receipt, and a paired win over the current holdout
incumbent. A historical PROMOTE label or exception is not sufficient. No TIFF is
generated and no organizer template/receipt is authenticated here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
import rasterio
from rasterio.errors import RasterioError

ROOT = Path(__file__).resolve().parents[1]
# (stem, run card, selector, has_zip[, kind]); kind "research" = negative card required,
# kind "candidate" = PROMOTE card + explicit selector required (HK3 lane, 2026-10-28).
ARTIFACTS = (
    ("gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros",
     "docs/downloads/gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros-run-card.json",
     None, False),
    ("gemsdoekarage2-h1-parity-1ab65e3fb345-DO-NOT-SUBMIT-surface",
     "evidence/run_card.json", "evidence/selector_result.json", True),
    ("gemsdoekarage2-h2-stepover-8d519ec5ec58",
     "evidence/run_card_h2.json", None, True),
    ("gemsdoekarage2-k2-hgbcont-b110-20261028-zeros",
     "evidence/k2/run_card.json", "evidence/k2/selector_result.json", True),
    ("gemsdoekarage2-b4-stepasym-b110-20261028-zeros",
     "evidence/b4/run_card.json", None, True),
    ("gemsdoekarage2-k3-linctxdti-b110-20261028-zeros",
     "evidence/k3/run_card.json", "evidence/k3/selector_result.json", True),
    ("gemsdoekarage2-hk3-edgecentrality-apron3-20261028",
     "evidence/hk3/run_card.json", "evidence/hk3/selector_result.json", True, "candidate"),
)


def normalise_card(card: dict, rel: str, stem: str) -> dict:
    """Map the HK3 card schema (raster{file,sha256}, submission{name,note}) onto the flat
    schema the research cards use; other cards pass through unchanged."""
    if isinstance(card, dict) and isinstance(card.get("raster"), dict):
        flat = dict(card)
        flat["raster"] = card["raster"].get("file")
        flat["raster_sha256"] = card["raster"].get("sha256")
        flat["submission_name"] = card.get("submission", {}).get("name")
        flat["note"] = card.get("submission", {}).get("note")
        return flat
    return card


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def inspect_raster(path: Path, grid: dict) -> dict:
    """Inspect *saved* bytes in windows; never replace or silently clip pixels."""
    with rasterio.open(path) as ds:
        checks = {
            "single_band": ds.count == 1,
            "float32": ds.count == 1 and ds.dtypes == ("float32",),
            "geotiff": ds.driver == "GTiff",
            "mirror_shape_match": list(ds.shape) == grid["shape"],
            "mirror_crs_match": str(ds.crs) == grid["crs"],
            "mirror_transform_match": list(ds.transform)[:6] == grid["transform"],
        }
        if ds.count != 1:
            checks.update(whole_array_finite=False, range_0_1=False, no_masked_pixels=False)
            return {"checks": checks, "diagnostics": {"reason": "Expected one band"}}
        nan = inf = masked = positive = 0
        minimum, maximum = float("inf"), float("-inf")
        for _, window in ds.block_windows(1):
            a = ds.read(1, window=window)
            nan += int(np.isnan(a).sum())
            inf += int(np.isinf(a).sum())
            masked += int((ds.read_masks(1, window=window) == 0).sum())
            positive += int((a > 0).sum())
            finite = a[np.isfinite(a)]
            if finite.size:
                minimum = min(minimum, float(finite.min()))
                maximum = max(maximum, float(finite.max()))
        checks.update(whole_array_finite=nan == 0 and inf == 0,
                      range_0_1=nan == 0 and inf == 0 and minimum >= 0 and maximum <= 1,
                      no_masked_pixels=masked == 0)
        return {"checks": checks, "diagnostics": {
            "nan_pixels": nan, "infinite_pixels": inf, "masked_pixels": masked,
            "positive_pixels": positive, "finite_min": minimum if minimum != float("inf") else None,
            "finite_max": maximum if maximum != float("-inf") else None,
            "whole_array_pixels": ds.height * ds.width,
        }}


def inspect_zip(path: Path, tif: Path, expected_sha256: str) -> bool:
    if not path.is_file():
        return False
    with zipfile.ZipFile(path) as archive:
        files = archive.infolist()
        if (len(files) != 1 or files[0].filename != tif.name or files[0].is_dir()
                or files[0].file_size != tif.stat().st_size):
            return False
        # Hash streamed decompressed bytes: names, compressed size, and ZIP
        # checksum alone would not establish byte identity to the linked TIFF.
        with archive.open(files[0]) as stream:
            h = hashlib.sha256()
            for block in iter(lambda: stream.read(1 << 20), b""):
                h.update(block)
        return h.hexdigest() == expected_sha256


def audit_artifact(root: Path, stem: str, card_rel: str, selector_rel: str | None,
                   has_zip: bool, grid: dict, kind: str = "research") -> dict:
    rel = f"docs/downloads/{stem}.tif"
    candidate = kind == "candidate"
    tif = root / rel
    checks: dict[str, bool] = {"tif_exists": tif.is_file()}
    detail: dict = {}
    actual_sha = None
    if checks["tif_exists"]:
        try:
            actual_sha = digest_file(tif)
            detail = inspect_raster(tif, grid)
            checks.update(detail["checks"])
            checks["raster_unchanged_during_read"] = digest_file(tif) == actual_sha
        except (OSError, ValueError, RasterioError) as exc:
            checks["tif_readable"] = False
            detail = {"diagnostics": {"error_type": type(exc).__name__}}
    try:
        card = normalise_card(json.loads((root / card_rel).read_text()), rel, stem)
        if candidate:
            checks["card_verdict_promote"] = card.get("verdict") == "PROMOTE"
            gates = card.get("gates") or {}
            checks["card_hard_gates_all_pass"] = bool(gates) and all(
                v is True for k, v in gates.items()
                if isinstance(v, bool) and k != "literal_rule_exception_applied")
            checks["card_literal_rule_clear"] = (
                gates.get("unique_literal_vs_all_registry_rasters") is True and
                not (card.get("registry_uniqueness") or {}).get("tiers", {}).get("U2_literal_rule_vs_all_registry_rasters", {}).get("failures"))
            checks["card_holdout_labelled"] = (card.get("holdout") or {}).get("evidence_class") == "HOLDOUT-DTI"
        else:
            checks["card_verdict_negative"] = card.get("verdict") == "negative"
        checks["card_has_same_filename"] = (card.get("raster", rel) == rel and
                                            card.get("submission_name") == stem)
        checks["card_sha_matches_saved_bytes"] = actual_sha is not None and card.get("raster_sha256") == actual_sha
        checks["card_note_within_140_chars"] = (isinstance(card.get("note"), str) and
                                                0 < len(card["note"]) <= 140)
    except (OSError, ValueError, TypeError, AttributeError):
        checks["card_readable"] = False
    if selector_rel is not None:
        try:
            selector = json.loads((root / selector_rel).read_text())
            if candidate:
                checks["selector_explicit_candidate"] = (selector.get("verdict") == "candidate_approved_by_automated_gates" and
                                                         selector.get("ok_to_submit") is True and
                                                         selector.get("slot_authorized") is False and
                                                         selector.get("source_run_card") == card_rel and
                                                         selector.get("raster_sha256") == actual_sha)
                checks["selector_explicit_research_only"] = (selector.get("verdict") == "negative_research_only" and
                                                             selector.get("ok_to_submit") is False and
                                                             selector.get("ok_to_download_for_research") is True and
                                                             selector.get("slot_authorized") is False and
                                                             selector.get("source_run_card") == card_rel and
                                                             selector.get("raster_sha256") == actual_sha)
                assessment_rel = selector.get("current_release_assessment")
                try:
                    assessment = json.loads((root / assessment_rel).read_text()) if assessment_rel else {}
                    checks["current_assessment_bound"] = (
                        assessment.get("status") in ("approved", "negative_research_only") and
                        assessment.get("ok_to_submit") is (assessment.get("status") == "approved") and
                        assessment.get("raster_sha256") == actual_sha and
                        assessment.get("source_run_card") == card_rel)
                    checks["current_assessment_negative"] = (
                        assessment.get("status") == "negative_research_only" and
                        assessment.get("ok_to_submit") is False)
                    checks["current_assessment_approval_gates_pass"] = (
                        assessment.get("preplacement_surface_clearance_passed") is True and
                        assessment.get("final_dot_uniqueness_passed") is True and
                        assessment.get("current_holdout_comparison_passed") is True and
                        assessment.get("organizer_template_authenticated") is True and
                        assessment.get("source_data_authenticated") is True and
                        assessment.get("lane_assignment_authorized") is True and
                        assessment.get("registry_scan_complete") is True and
                        assessment.get("leakage_canary_passed") is True)
                    holdout_gate = next((item for item in assessment.get("blocking_findings", [])
                                         if item.get("gate") == "current_holdout_incumbent"), {})
                    checks["candidate_beats_current_holdout_best"] = holdout_gate.get("passed") is True
                except (OSError, ValueError, TypeError, AttributeError):
                    checks["current_assessment_bound_negative"] = False
            else:
                checks["selector_explicit_negative"] = (selector.get("verdict") == "negative" and
                                                        selector.get("slot_authorized") is False and
                                                        selector.get("source_run_card") == card_rel)
        except (OSError, ValueError, TypeError, AttributeError):
            checks["selector_explicit_candidate" if candidate else "selector_explicit_negative"] = False
    if has_zip:
        try:
            checks["zip_contains_exact_saved_tif"] = bool(actual_sha and
                inspect_zip(tif.with_suffix('.zip'), tif, actual_sha))
        except (OSError, ValueError, zipfile.BadZipFile, RuntimeError):
            checks["zip_contains_exact_saved_tif"] = False
    ok = all(checks.values())
    candidate_approval_keys = {
        "tif_exists", "single_band", "float32", "geotiff", "mirror_shape_match",
        "mirror_crs_match", "mirror_transform_match", "whole_array_finite", "range_0_1",
        "no_masked_pixels", "raster_unchanged_during_read", "card_verdict_promote",
        "card_hard_gates_all_pass", "card_literal_rule_clear", "card_holdout_labelled",
        "candidate_beats_current_holdout_best", "card_has_same_filename",
        "card_sha_matches_saved_bytes", "card_note_within_140_chars",
        "selector_explicit_candidate", "current_assessment_bound",
        "current_assessment_approval_gates_pass",
    }
    if has_zip:
        candidate_approval_keys.add("zip_contains_exact_saved_tif")
    candidate_approval_ok = all(checks.get(key) is True for key in candidate_approval_keys)
    integrity_keys = {
        "tif_exists", "single_band", "float32", "geotiff", "mirror_shape_match",
        "mirror_crs_match", "mirror_transform_match", "whole_array_finite", "range_0_1",
        "no_masked_pixels", "raster_unchanged_during_read", "card_has_same_filename",
        "card_sha_matches_saved_bytes", "card_note_within_140_chars",
    }
    if has_zip:
        integrity_keys.add("zip_contains_exact_saved_tif")
    integrity_ok = all(checks.get(key) is True for key in integrity_keys)
    if candidate:
        if candidate_approval_ok:
            status = "VERIFIED_CANDIDATE_FOR_UPLOAD"
        elif (integrity_ok and checks.get("selector_explicit_research_only") is True
              and checks.get("current_assessment_bound") is True
              and checks.get("current_assessment_negative") is True):
            status = "VERIFIED_RESEARCH_ONLY"
        else:
            status = "FAIL_CLOSED"
    else:
        status = "VERIFIED_RESEARCH_ONLY" if ok else "FAIL_CLOSED"
    return {
        "file": rel, "raster_sha256": actual_sha, "run_card": card_rel, "kind": kind,
        "selector": selector_rel, "zip_file": f"docs/downloads/{stem}.zip" if has_zip else None,
        "checks": checks, "diagnostics": detail.get("diagnostics", {}),
        "status": status,
        "download_for_research": status in ("VERIFIED_RESEARCH_ONLY", "VERIFIED_CANDIDATE_FOR_UPLOAD"),
        "ok_to_submit": status == "VERIFIED_CANDIDATE_FOR_UPLOAD", "slot_authorized": False,
        "template_authority": "pinned owner-mirror grid only; official template not authenticated",
        "exterior_convention": "zeros outside the footprint (finite everywhere); portal acceptance is not verified until an organizer receipt exists",
    }


def audit(root: Path = ROOT) -> dict:
    grid = json.loads((root / 'evidence/geometry-audit.json').read_text())["template"]
    downloads = root / 'docs/downloads'
    expected_tifs = {f"{a[0]}.tif" for a in ARTIFACTS}
    expected_zips = {f"{a[0]}.zip" for a in ARTIFACTS if a[3]}
    found_tifs = {p.name for suffix in ("*.tif", "*.tiff") for p in downloads.glob(suffix)}
    found_zips = {p.name for p in downloads.glob('*.zip')}
    unexpected = sorted((found_tifs - expected_tifs) | (found_zips - expected_zips))
    missing = sorted((expected_tifs - found_tifs) | (expected_zips - found_zips))
    entries = [audit_artifact(root, a[0], a[1], a[2], a[3], grid, a[4] if len(a) > 4 else "research")
               for a in ARTIFACTS]
    good = (not unexpected and not missing and
            all(row['status'] in ('VERIFIED_RESEARCH_ONLY', 'VERIFIED_CANDIDATE_FOR_UPLOAD') for row in entries))
    approved = [row['file'] for row in entries if row['status'] == 'VERIFIED_CANDIDATE_FOR_UPLOAD']
    if good and len(approved) > 1:
        good = False  # exactly one file may be offered for upload at a time
    if good and approved:
        status = "PASS_ONE_CANDIDATE_FOR_UPLOAD"
    elif good:
        status = "PASS_RESEARCH_ONLY"
    else:
        status = "FAIL_CLOSED"
    estimate = None
    if good and approved:
        card = json.loads((root / 'evidence/hk3/run_card.json').read_text())
        estimate = {"label": card["estimator"]["evidence_class"], "value": card["estimator"]["estimate"],
                    "theta_sensitivity": card["estimator"]["estimate_theta"]}
    return {
        "schema": "gems.published_downloads.v2",
        "evidence_class": "SAVED-BYTE-INTEGRITY, NOT HOLDOUT-DTI OR ORGANIZER-CONFIRMED",
        "inventory_status": status,
        "verdict": "candidate_available" if (good and approved) else "negative",
        "unexpected_downloads": unexpected, "missing_downloads": missing,
        "artifacts": entries,
        "downloadable_approved_submission": approved[0] if (good and approved) else None,
        "score_estimate": estimate,
        "organizer_template_authenticated": False,
        "format_note": "Each raster is read from disk, whole-array range and grid compared with an unauthenticated owner mirror. Footprint/exterior policy and portal acceptance require organizer evidence.",
        "slot_authorized": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true', help='Compare against committed receipt without overwriting it')
    args = p.parse_args()
    result = audit()
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    destinations = (ROOT / 'evidence/public_downloads_audit.json',
                    ROOT / 'docs/evidence/public_downloads_audit.json')
    if args.check:
        if any(not d.is_file() or d.read_text() != text for d in destinations):
            raise SystemExit('Published-downloads audit is stale; rerun scripts/audit_public_downloads.py')
    else:
        for dest in destinations:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text)
    print(json.dumps({"inventory_status": result['inventory_status'],
                      "downloadable_approved_submission": result['downloadable_approved_submission'],
                      "artifacts": len(result['artifacts'])}))
    return 0 if result['inventory_status'].startswith('PASS') else 1


if __name__ == '__main__':
    raise SystemExit(main())

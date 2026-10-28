#!/usr/bin/env python3
"""Re-read every published TIFF/ZIP and fail closed on unexpected downloads.

This is an integrity and local-format audit, not a model evaluation. The current
HK3 artifact is governed by the strict negative disposition and is research-only;
the earlier PROMOTE card remains historical evidence, not current clearance. The
generic candidate path is retained for tests/future authorized work, but this
inventory currently has no upload candidate. No TIFF is generated and no
organizer template/receipt is authenticated here.
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
# (stem, current disposition card, selector, has_zip[, kind]); kind "research" = negative card required,
# kind "candidate" = PROMOTE card + explicit selector required (kept for future authorized work).
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
     "evidence/hk3/strict_disposition.json", "evidence/hk3/strict_selector_result.json", True, "research"),
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
            # A disclosed literal failure is still a stop. The old exception path
            # was the defect this strict review closes; disclosure never equals clearance.
            checks["card_literal_rule_passed_without_exception"] = (
                gates.get("unique_literal_vs_all_registry_rasters") is True and
                gates.get("literal_rule_exception_applied") is False)
            checks["card_holdout_labelled"] = (card.get("holdout") or {}).get("evidence_class") == "HOLDOUT-DTI"
            strict_receipt = card.get("strict_format_receipt") or {}
            strict_checks = strict_receipt.get("checks") or {}
            required_strict_checks = (
                "single_band", "float32", "crs_matches_template", "shape_matches_template",
                "transform_matches_template", "inside_no_masked_cells", "inside_all_finite",
                "inside_in_range_0_1", "outside_is_nan")
            template_sha = strict_receipt.get("template_sha256")
            checks["card_strict_format_receipt_bound_to_saved_bytes"] = (
                strict_receipt.get("candidate_sha256") == actual_sha and
                strict_receipt.get("strict_format_pass") is True and
                strict_receipt.get("template_authenticity") == "organizer-authenticated" and
                isinstance(template_sha, str) and len(template_sha) == 64 and
                all(c in "0123456789abcdef" for c in template_sha) and
                card.get("organizer_template_authenticated") is True and
                all(strict_checks.get(name) is True for name in required_strict_checks))
        else:
            checks["card_verdict_negative"] = card.get("verdict") == "negative"
            if card.get("current_disposition"):
                checks["card_currently_research_only"] = card.get("current_disposition") == "DO NOT SUBMIT; research-only download"
                checks["card_literal_stop_has_no_exception"] = (
                    card.get("gates", {}).get("unique_literal_vs_all_registry_rasters") is False and
                    card.get("gates", {}).get("literal_rule_exception_applied") is False and
                    card.get("registry_uniqueness", {}).get("literal_rule_exception_applied") is False)
                checks["card_registry_incomplete_disclosed"] = (
                    card.get("registry_uniqueness", {}).get("registry_rasters_checked") == 452 and
                    card.get("registry_uniqueness", {}).get("registry_rasters_expected") == 453 and
                    card.get("registry_uniqueness", {}).get("complete_registry_inventory") is False)
                checks["card_strict_exterior_failure_disclosed"] = (
                    card.get("strict_review", {}).get("strict_outside_is_nan") is False and
                    card.get("gates", {}).get("strict_format_pass") is False)
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
                # Candidate clearance is distinct from a weekly slot; only a separate human
                # selector can authorize that slot. This branch is not used by current inventory.
                checks["selector_explicit_candidate"] = (selector.get("verdict") == "candidate_approved_by_automated_gates" and
                                                         selector.get("ok_to_submit") is True and
                                                         selector.get("slot_authorized") is False and
                                                         selector.get("source_run_card") == card_rel and
                                                         selector.get("raster_sha256") == actual_sha)
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
    # The official exterior convention is null/NaN, so a fully compliant raster
    # may fail whole-array finiteness/range diagnostics outside the footprint. For
    # candidate clearance, those two global diagnostics are informational only;
    # the hash-bound strict receipt must separately prove in-footprint range and
    # null/NaN exterior against an authenticated official template.
    non_gating_names = {"whole_array_finite", "range_0_1"} if candidate else set()
    non_gating_diagnostics = sorted(name for name in non_gating_names if checks.get(name) is False)
    ok = all(value for key, value in checks.items() if key not in non_gating_names)
    if candidate:
        status = "VERIFIED_CANDIDATE_FOR_UPLOAD" if ok else "FAIL_CLOSED"
    else:
        status = "VERIFIED_RESEARCH_ONLY" if ok else "FAIL_CLOSED"
    if stem == "gemsdoekarage2-hk3-edgecentrality-apron3-20261028":
        exterior_note = ("Saved exterior is zero-valued and finite; the official problem text requires null/NaN outside bounds, "
                         "the strict outside_is_nan check fails, and no portal acceptance or organizer receipt is available. Research-only.")
    else:
        exterior_note = "Research artifact; exterior bytes are preserved as saved. No official template or portal acceptance is authenticated."
    return {
        "file": rel, "raster_sha256": actual_sha, "run_card": card_rel, "kind": kind,
        "selector": selector_rel, "zip_file": f"docs/downloads/{stem}.zip" if has_zip else None,
        "checks": checks, "diagnostics": detail.get("diagnostics", {}),
        "non_gating_diagnostics": sorted(non_gating_diagnostics),
        "status": status,
        "download_for_research": ok,
        "ok_to_submit": bool(candidate and ok), "slot_authorized": False,
        "template_authority": "pinned owner-mirror grid only; official template not authenticated",
        "exterior_convention": exterior_note,
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
        "format_note": "Each raster is read from saved bytes and checked for local grid/range integrity against an unauthenticated owner mirror. HK3 is research-only: its zero exterior conflicts with the official null/NaN bounds instruction, its strict outside check fails, and portal acceptance is unverified.",
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

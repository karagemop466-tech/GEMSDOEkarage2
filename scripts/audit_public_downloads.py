#!/usr/bin/env python3
"""Re-read every published TIFF/ZIP and fail closed on unexpected downloads.

This is an integrity and local-format audit of published research files, not a
model evaluation, a selector, or a release-authorization system. All current
files need a negative run card. A claimed candidate fails closed: this inventory
cannot authenticate organizer inputs, prove pre-placement chronology, establish
a complete registry, or authorize a weekly slot. No TIFF is generated here.
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

try:
    from scripts.raster_integrity import require_single_file_dataset
except ModuleNotFoundError:  # direct execution as ``python scripts/...``
    from raster_integrity import require_single_file_dataset

ROOT = Path(__file__).resolve().parents[1]
# (stem, run card, selector, has_zip[, kind]); current entries are research only.
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
     "evidence/hk3/run_card.json", "evidence/hk3/selector_result.json", True),
    # Retained for research provenance only. Its own card records no organizer
    # holdout, no registry audit, and an explicit negative verdict.
    ("gemsdoekarage2-hA-intersection-propensity-aad3569983ab",
     "evidence/hA-intersection/run_card.json", None, False),
    ("gemsdoe-karage2-hr4-intersection-20261029-nan",
     "evidence/hr4-intersection/run_card.json", None, False),
    # New H-F hypothesis TIF (experiment 1): unique, format-valid, negative verdict.
    ("gemsdoe-hf-alteration-curvature-intersection-20261030",
     "docs/downloads/gemsdoe-hf-alteration-curvature-intersection-20261030.run-card.json",
     None, False, "research"),
    # HX-2 (2026-10-31): unique, format-valid, apron-cleared lineament field.
    # Research-only: the projected score does not beat the 0.2778 incumbent.
    ("gemsdoe-karage2-hx2-lineament-apron3-36k-20261031-zeros",
     "docs/downloads/gemsdoe-karage2-hx2-lineament-apron3-36k-20261031-zeros.run-card.json",
     None, False, "research"),
    # GBSP unique submission TIF (experiment 4): format-valid, uniqueness-passed,
    # not cleared to submit (holdout-DTI proxy below threshold).
    ("gems-gbsp-blindspot-2195bc570842-20261031T005323Z",
     "docs/downloads/gems-gbsp-blindspot-2195bc570842-20261031T005323Z.run-card.json",
     None, False, "research"),
)


# Files that exist in docs/downloads but are NOT registered in ARTIFACTS and are NOT
# authorized for research download. They were merged from parallel Arena lanes whose
# generators did not update this inventory. Quarantining them keeps the audit
# fail-closed (they can never be reported as VERIFIED_RESEARCH_ONLY) while making
# their presence visible instead of silently ignoring it. The protocol owner must
# decide: register, regenerate, or delete.
QUARANTINED = {
    "gemsdoe-karage2-near-trace-20261031.tif":
        "present but unregistered; its run card says verdict 'promote' and ok_to_submit false, "
        "and docs/how-to-submit.html (hand-edited in a parallel lane) records a lattice-overlap block",
    "gemsdoe-blind-geothermal-rad-mag-grav-intersection-20261031.tif":
        "present but unregistered; run card is negative, but its card has no 'raster' field so the "
        "saved-byte binding cannot be checked here",
}


def normalise_card(card: dict, rel: str, stem: str) -> dict:
    """Map nested and legacy flat card schemas onto the common audit fields."""
    if isinstance(card, dict) and isinstance(card.get("raster"), dict):
        flat = dict(card)
        flat["raster"] = card["raster"].get("file")
        flat["raster_sha256"] = card["raster"].get("sha256")
        flat["submission_name"] = card.get("submission", {}).get("name")
        flat["note"] = card.get("submission", {}).get("note")
        return flat
    if (isinstance(card, dict) and card.get("file") == Path(rel).name
            and isinstance(card.get("sha256"), str)):
        # Legacy research cards may use a flat schema. Preserve the
        # stored negative authorization fields; never infer approval from format.
        flat = dict(card)
        flat["raster"] = rel
        flat["raster_sha256"] = card["sha256"]
        flat["verdict"] = "negative" if str(card.get("verdict", "")).lower().startswith("negative") else card.get("verdict")
        flat["slot_authorized"] = card.get("slot_authorized")
        flat["approved_for_weekly_slot"] = card.get("approved_for_weekly_slot")
        flat["ok_to_submit"] = card.get("ok_to_submit")
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
        require_single_file_dataset(ds, path)
        checks = {
            "self_contained_tiff": True,
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
        checks.update(whole_array_finite=inf == 0,   # NaN outside footprint is the official convention; Inf is never OK
                      range_0_1=inf == 0 and minimum >= 0 and maximum <= 1,   # NaN ignored; finite cells must be in [0,1]
                      no_masked_pixels=masked == 0 or masked == nan)   # all masked = NaN (outside footprint convention) is OK
        require_single_file_dataset(ds, path)
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
    if kind not in ("research", "candidate"):
        raise ValueError(f"Unknown artifact kind: {kind}")
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
            checks["self_contained_tiff"] = False  # not established on an unreadable or multi-file raster
            detail = {"diagnostics": {"error_type": type(exc).__name__, "error": str(exc)}}
    try:
        card = normalise_card(json.loads((root / card_rel).read_text()), rel, stem)
        if candidate:
            # This inventory does not implement the independent, provenance-bound
            # selector required for a promotion. A claimed PROMOTE plus a matching
            # selector JSON is not evidence that the underlying gates actually ran.
            checks["independent_release_verification_implemented"] = False
        else:
            checks["card_verdict_negative"] = (card.get("verdict") == "negative"
                                                and card.get("ok_to_submit", False) is False
                                                and card.get("approved_for_weekly_slot", False) is False
                                                and card.get("slot_authorized", False) is False)
        checks["card_has_same_filename"] = (card.get("raster", rel) == rel and
                                            card.get("submission_name") == stem)
        checks["card_sha_matches_saved_bytes"] = actual_sha is not None and card.get("raster_sha256") == actual_sha
        checks["card_note_within_140_chars"] = (isinstance(card.get("note"), str) and
                                                0 < len(card["note"]) <= 140)
    except (OSError, ValueError, TypeError, AttributeError):
        checks["card_readable"] = False
    metadata_path = tif.with_suffix('.json')
    if metadata_path.exists() or card_rel == "evidence/hk3/run_card.json":
        try:
            metadata = json.loads(metadata_path.read_text())
            checks["metadata_research_only_and_hash_bound"] = (
                isinstance(metadata, dict) and metadata.get("sha256") == actual_sha
                and metadata.get("promoted") is False
                and metadata.get("approved_for_weekly_slot") is False
                and metadata.get("ok_to_submit", False) is False
            )
            if card_rel == "evidence/hk3/run_card.json":
                checks["metadata_hk3_negative_status"] = (
                    "DO NOT SUBMIT" in metadata.get("status", "")
                    and "WITHDRAWN" in metadata.get("metadata", {}).get("estimator", {}).get("status", "")
                )
        except (OSError, ValueError, TypeError, AttributeError):
            checks["metadata_research_only_and_hash_bound"] = False
    if selector_rel is not None:
        try:
            selector = json.loads((root / selector_rel).read_text())
            if candidate:
                # Matching assertions are recorded for diagnostics, never as authorization.
                checks["selector_explicit_candidate"] = (selector.get("verdict") == "candidate_approved_by_automated_gates" and
                                                         selector.get("ok_to_submit") is True and
                                                         selector.get("slot_authorized") is False and
                                                         selector.get("source_run_card") == card_rel and
                                                         selector.get("raster_sha256") == actual_sha)
            else:
                checks["selector_explicit_negative"] = (selector.get("verdict") == "negative" and
                                                        selector.get("slot_authorized") is False and
                                                        selector.get("ok_to_submit", False) is False and
                                                        selector.get("approved_for_weekly_slot", False) is False and
                                                        selector.get("source_run_card") == card_rel)
                # HK3's concurrent release review adds a current, byte-bound
                # negative assessment. If present for another research artifact,
                # do not silently ignore contradictions there either.
                if "current_release_assessment" in selector or card_rel == "evidence/hk3/run_card.json":
                    checks["current_assessment_negative_and_hash_bound"] = False
                    assessment_rel = selector.get("current_release_assessment")
                    if not isinstance(assessment_rel, str):
                        raise ValueError("Missing release assessment")
                    assessment_path = (root / assessment_rel).resolve()
                    if not assessment_path.is_relative_to((root / "evidence").resolve()):
                        raise ValueError("Release assessment outside evidence directory")
                    assessment = json.loads(assessment_path.read_text())
                    checks["current_assessment_negative_and_hash_bound"] = (
                        assessment.get("status") == "negative_research_only"
                        and assessment.get("ok_to_submit") is False
                        and assessment.get("slot_authorized") is False
                        and assessment.get("candidate") == rel
                        and assessment.get("raster_sha256") == actual_sha
                        and assessment.get("source_run_card") == card_rel
                        and (card_rel != "evidence/hk3/run_card.json"
                             or assessment_rel == "evidence/hk3/current_release_assessment.json"))
        except (OSError, ValueError, TypeError, AttributeError):
            checks["selector_explicit_candidate" if candidate else "selector_explicit_negative"] = False
    if has_zip:
        try:
            checks["zip_contains_exact_saved_tif"] = bool(actual_sha and
                inspect_zip(tif.with_suffix('.zip'), tif, actual_sha))
        except (OSError, ValueError, zipfile.BadZipFile, RuntimeError):
            checks["zip_contains_exact_saved_tif"] = False
    ok = all(checks.values()) and not candidate
    status = "VERIFIED_RESEARCH_ONLY" if ok else "FAIL_CLOSED"
    return {
        "file": rel, "raster_sha256": actual_sha, "run_card": card_rel, "kind": kind,
        "selector": selector_rel, "zip_file": f"docs/downloads/{stem}.zip" if has_zip else None,
        "checks": checks, "diagnostics": detail.get("diagnostics", {}),
        "status": status,
        "download_for_research": ok,
        "ok_to_submit": False, "slot_authorized": False,
        "template_authority": "pinned owner-mirror grid only; official template not authenticated",
        "exterior_convention": "not assessed by this saved-byte integrity auditor; no organizer-authenticated footprint is supplied",
    }


def audit(root: Path = ROOT) -> dict:
    grid = json.loads((root / 'evidence/geometry-audit.json').read_text())["template"]
    downloads = root / 'docs/downloads'
    expected_tifs = {f"{a[0]}.tif" for a in ARTIFACTS}
    expected_zips = {f"{a[0]}.zip" for a in ARTIFACTS if a[3]}
    found_tifs = {p.name for suffix in ("*.tif", "*.tiff") for p in downloads.glob(suffix)}
    found_zips = {p.name for p in downloads.glob('*.zip')}
    quarantined = sorted(n for n in (found_tifs | found_zips) if n in QUARANTINED)
    unexpected = sorted((found_tifs - expected_tifs - set(QUARANTINED)) |
                        (found_zips - expected_zips - set(QUARANTINED)))
    missing = sorted((expected_tifs - found_tifs) | (expected_zips - found_zips))
    entries = [audit_artifact(root, a[0], a[1], a[2], a[3], grid, a[4] if len(a) > 4 else "research")
               for a in ARTIFACTS]
    good = (not unexpected and not missing and
            all(row['status'] == 'VERIFIED_RESEARCH_ONLY' for row in entries))
    return {
        "schema": "gems.published_downloads.v2",
        "evidence_class": "SAVED-BYTE-INTEGRITY, NOT HOLDOUT-DTI OR ORGANIZER-CONFIRMED",
        "inventory_status": "PASS_RESEARCH_ONLY" if good else "FAIL_CLOSED",
        "verdict": "negative",
        "unexpected_downloads": unexpected, "missing_downloads": missing,
        "quarantined_downloads": [{"file": f"docs/downloads/{n}", "status": "QUARANTINED_NOT_AUTHORIZED",
                                   "reason": QUARANTINED[n]} for n in quarantined],
        "artifacts": entries,
        "downloadable_approved_submission": None,
        "score_estimate": None,
        "organizer_template_authenticated": False,
        "format_note": "Each raster is read from disk and whole-array range/grid are compared with an unauthenticated owner mirror. This inventory does not infer footprint/exterior convention; authenticated organizer footprint and portal acceptance are unavailable. Separate owner-mirror footprint diagnostics are not submission authorization.",
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

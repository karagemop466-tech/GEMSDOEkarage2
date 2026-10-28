#!/usr/bin/env python3
"""Re-read every published TIFF/ZIP and fail closed on unexpected downloads.

This is an integrity and local-format audit of historical negative *research*
files, not a model evaluation or a submission selector. No source is promoted,
no TIFF is generated, and no organizer template/receipt is authenticated.
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
ARTIFACTS = (
    ("gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros",
     "docs/downloads/gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros-run-card.json",
     None, False),
    ("gemsdoekarage2-h1-parity-1ab65e3fb345-DO-NOT-SUBMIT-surface",
     "evidence/run_card.json", "evidence/selector_result.json", True),
    ("gemsdoekarage2-k2-hgbcont-b110-20261028-zeros",
     "evidence/k2/run_card.json", "evidence/k2/selector_result.json", True),
)


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
                   has_zip: bool, grid: dict) -> dict:
    rel = f"docs/downloads/{stem}.tif"
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
        card = json.loads((root / card_rel).read_text())
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
            checks["selector_explicit_negative"] = (selector.get("verdict") == "negative" and
                                                    selector.get("slot_authorized") is False and
                                                    selector.get("source_run_card") == card_rel)
        except (OSError, ValueError, TypeError, AttributeError):
            checks["selector_explicit_negative"] = False
    if has_zip:
        try:
            checks["zip_contains_exact_saved_tif"] = bool(actual_sha and
                inspect_zip(tif.with_suffix('.zip'), tif, actual_sha))
        except (OSError, ValueError, zipfile.BadZipFile, RuntimeError):
            checks["zip_contains_exact_saved_tif"] = False
    return {
        "file": rel, "raster_sha256": actual_sha, "run_card": card_rel,
        "selector": selector_rel, "zip_file": f"docs/downloads/{stem}.zip" if has_zip else None,
        "checks": checks, "diagnostics": detail.get("diagnostics", {}),
        "status": "VERIFIED_RESEARCH_ONLY" if all(checks.values()) else "FAIL_CLOSED",
        "download_for_research": all(checks.values()),
        "ok_to_submit": False, "slot_authorized": False,
        "template_authority": "pinned owner-mirror grid only; official template not authenticated",
        "exterior_convention": "unverified; whole-array finiteness is not portal acceptance",
    }


def audit(root: Path = ROOT) -> dict:
    grid = json.loads((root / 'evidence/geometry-audit.json').read_text())["template"]
    downloads = root / 'docs/downloads'
    expected_tifs = {f"{stem}.tif" for stem, _, _, _ in ARTIFACTS}
    expected_zips = {f"{stem}.zip" for stem, _, _, has_zip in ARTIFACTS if has_zip}
    found_tifs = {p.name for suffix in ("*.tif", "*.tiff") for p in downloads.glob(suffix)}
    found_zips = {p.name for p in downloads.glob('*.zip')}
    unexpected = sorted((found_tifs - expected_tifs) | (found_zips - expected_zips))
    missing = sorted((expected_tifs - found_tifs) | (expected_zips - found_zips))
    entries = [audit_artifact(root, stem, card, selector, has_zip, grid)
               for stem, card, selector, has_zip in ARTIFACTS]
    good = not unexpected and not missing and all(row['status'] == 'VERIFIED_RESEARCH_ONLY' for row in entries)
    return {
        "schema": "gems.published_downloads.v1",
        "evidence_class": "SAVED-BYTE-INTEGRITY, NOT HOLDOUT-DTI OR ORGANIZER-CONFIRMED",
        "inventory_status": "PASS_RESEARCH_ONLY" if good else "FAIL_CLOSED",
        "verdict": "negative",
        "unexpected_downloads": unexpected, "missing_downloads": missing,
        "artifacts": entries,
        "downloadable_approved_submission": None,
        "score_estimate": None,
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
                      "downloadable_approved_submission": None,
                      "artifacts": len(result['artifacts'])}))
    return 0 if result['inventory_status'] == 'PASS_RESEARCH_ONLY' else 1


if __name__ == '__main__':
    raise SystemExit(main())

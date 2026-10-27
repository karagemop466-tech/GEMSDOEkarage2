#!/usr/bin/env python3
"""Check a TIFF using the pinned shared validator; this never authorizes upload."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import rasterio
from audit_references import DEFAULT_CACHE, MANIFEST, checked_path, load_shared


def check(path: Path, cache: Path = DEFAULT_CACHE) -> dict:
    spec = json.loads(MANIFEST.read_text())
    _, submission = load_shared(cache, spec)
    item = next(x for x in spec["inputs"] if x["cache_path"] == "inputs/sample.tif")
    template = checked_path(cache, item["cache_path"], item["sha256"])
    report = submission.check_variants(path, template)
    # The upstream key is based on an owner mirror whose content differs from
    # the organizer's description of the sample. Preserve the diagnostic but
    # do not repeat it as an authenticated official-compliance finding.
    report["upstream_mirror_based_exterior_and_format_diagnostic"] = report.pop("official_format_compliant")
    report["official_format_compliant"] = None
    report["warning"] = (
        "Local format diagnostics only; no leaderboard result, uniqueness, "
        "scientific holdout, slot authorization or portal acceptance is implied."
    )
    report["input_authority"] = "hash-pinned owner mirror, not organizer-authenticated; it differs from the organizer's sample description"
    report["upstream_official_check_names_are_not_authenticated"] = True
    report["submission_authorized"] = False
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("path", type=Path)
    p.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    args = p.parse_args()
    try:
        report = check(args.path, args.cache)
    except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
        report = {"file": str(args.path), "format_valid": False,
                  "official_format_compliant": None, "submission_authorized": False,
                  "error": str(exc)}
    print(json.dumps(report, indent=2, allow_nan=False))
    if not report["format_valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

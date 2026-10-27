#!/usr/bin/env python3
"""Run the unchanged pinned shared format checker, never authorize a submission.

This wrapper explicitly distinguishes the unverified owner-mirror template and
strict whole-array range diagnostic from organizer acceptance. No TIFF is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def checked_import(cache: Path):
    manifest = json.loads((ROOT / "registry/shared_protocol_assets.json").read_text())
    needed = {"template-__init__", "template-submission", "template-validator"}
    rows = [x for x in manifest["files"] if x["id"] in needed]
    if {x["id"] for x in rows} != needed:
        raise ValueError("Pinned checker manifest is incomplete")
    for item in rows:
        p = cache / "upstream" / item["dest"]
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Shared checker is missing or modified: {p}; run bootstrap_shared.py")
    sys.path.insert(0, str(cache / "upstream/shared_template/src"))
    from gems.submission import check_variants
    return check_variants


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("raster", type=Path)
    ap.add_argument("--cache", type=Path, default=ROOT / ".cache")
    ap.add_argument("--template", type=Path, default=None)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    template = args.template or args.cache / "competition_data/sample_submission.tif"
    checker = checked_import(args.cache)
    result = checker(args.raster, template)
    receipt = {
        "scope": "Pinned shared format checks only. No scientific gate, selector or organizer acceptance was evaluated.",
        "template_organizer_authentication": "unknown; the owner mirror is not an official receipt",
        "template_note": "The shared check name official_template_grid_and_footprint checks shape/grid/footprint, not provenance.",
        "organizer_accepted": None,
        "submission_authorized": False,
        "strict_whole_array_range_pass": result["checks"]["variant_strict_whole_array_no_nan_allowed"]["pass"],
        "shared_output": result,
    }
    output = json.dumps(receipt, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
    print(output, end="")
    # A zero exit means only the shared hard checks AND the conservative strict
    # whole-array range diagnostic passed. It still does not mean upload approval
    # or resolve the official outside-null wording. NaN-outside variants fail
    # this conservative check even when the official sample allows NaN outside.
    return 0 if result["format_valid"] and receipt["strict_whole_array_range_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

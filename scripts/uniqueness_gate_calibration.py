#!/usr/bin/env python3
"""Calibrate the literal 3-px uniqueness gate against its own registry witness.

Why this exists (2026-10-29): the literal gate in ``scripts/check_uniqueness.py``
declares DUPLICATE when more than 70% of a candidate's positive cells lie within
3 px of any positive cell of a reference raster. The only lattice witness pinned
in ``research/reference-sources.json`` (``inputs/lattice.tif``, from the 13GEMSDOE
owner mirror) covers almost the whole footprint. This script measures that
saturation with the *shared* comparator and writes a receipt. It does not
change the gate, the threshold, the support rule or any submission.

Outputs (default): ``evidence/uniqueness-gate-calibration-2026-10-29.json``.
``--check`` recomputes everything and fails if the committed receipt differs.

Inputs are read from the git-ignored cache ``.cache/research`` (populate it with
``scripts/bootstrap_research.py``). Every input is SHA-256 checked against the
pinned manifest before use; missing or changed inputs fail closed. The owner
mirrors are not organizer-authenticated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))
from check_uniqueness import centered_ranks, check_comparator  # noqa: E402  shared gate code
from gems57.uniqueness import saturation_certificate  # noqa: E402  shared vendored certificate

MANIFEST = ROOT / "research/reference-sources.json"
CACHE = ROOT / ".cache/research"
DEFAULT_OUT = ROOT / "evidence/uniqueness-gate-calibration-2026-10-29.json"
SCHEMA = "uniqueness-gate-calibration-v1"
RADIUS_PX = 3.0
OVERLAP_LIMIT = 0.70
NULL_COUNTS = (100, 10_000, 22_163, 22_164, 37_654)
NULL_SEEDS = (0, 1, 2)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def max_passing_positive_cells(uncovered_footprint_cells: int) -> int:
    """Largest candidate positive count that can pass the literal gate.

    Pass requires ``10 * matched <= 7 * n`` (see ``check_comparator``). Writing
    ``u`` for unmatched candidate cells (u <= uncovered cells, since a matched
    cell is within 3 px of the witness), the pass condition is ``3n <= 10u``.
    Hence ``n <= floor(10 * u_max / 3)``. This is a necessary condition for ANY
    content: no arrangement of dots can exceed it.
    """
    if uncovered_footprint_cells < 0:
        raise ValueError("negative uncovered count")
    return (10 * uncovered_footprint_cells) // 3


def load_manifest_inputs() -> dict:
    spec = json.loads(MANIFEST.read_text())
    by_cache = {}
    for item in spec["inputs"]:
        by_cache[item["cache_path"]] = item
    for item in spec["references"]:
        by_cache[item["cache_path"]] = item
    return by_cache


def verified_path(entries: dict, cache_path: str) -> Path:
    item = entries[cache_path]
    path = (CACHE / cache_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Missing cached input {cache_path}; run scripts/bootstrap_research.py")
    if path.stat().st_size != item["bytes"] or sha256_file(path) != item["sha256"]:
        raise ValueError(f"Cached input fails pinned hash/size: {cache_path}")
    return path


def compute(out_seed_list=NULL_SEEDS) -> dict:
    entries = load_manifest_inputs()
    template_path = verified_path(entries, "inputs/sample.tif")
    lattice_path = verified_path(entries, "inputs/lattice.tif")

    with rasterio.open(template_path) as ds:
        template = ds.read(1)
        tmask = ds.read_masks(1)
        grid = (ds.shape, ds.crs, ds.transform)
    foot = np.isfinite(template) & (tmask > 0)
    footprint_cells = int(foot.sum())

    with rasterio.open(lattice_path) as ds:
        if (ds.shape, ds.crs, ds.transform) != grid:
            raise ValueError("Lattice grid differs from the template grid")
        lattice = ds.read(1)
    lat_pos = np.isfinite(lattice) & (lattice > 0) & foot
    near = distance_transform_edt(~lat_pos) <= RADIUS_PX
    uncovered = int((foot & ~near).sum())
    coverage = float((foot & near).sum() / footprint_cells)

    # Cross-check against the vendored certificate (independent implementation).
    cert = saturation_certificate(lattice_path, foot, expected_grid=grid)
    if cert["uncovered_allowed_pixels"] != uncovered:
        raise AssertionError("Local and vendored certificates disagree on uncovered cells")

    flat_foot_idx = np.flatnonzero(foot.ravel())
    null_rows = []
    for n in NULL_COUNTS:
        for seed in out_seed_list:
            rng = np.random.default_rng(seed)
            sel = rng.choice(flat_foot_idx, size=n, replace=False)
            support_flat = np.zeros(foot.size, dtype=bool)
            support_flat[sel] = True
            support = support_flat.reshape(foot.shape)
            values = support.astype(np.float32)
            ranks, norm = centered_ranks(values[foot])
            res = check_comparator(ranks, norm, support & foot, lattice, foot)
            null_rows.append({
                "n_positive_cells": n,
                "seed": seed,
                "matched_within_3px": res["matches_within_3px"],
                "overlap_fraction": round(res["overlap_fraction"], 6),
                "spearman_full_footprint": round(res["spearman_full_footprint"], 6),
                "duplicate_by_literal_gate": res["duplicate"],
            })

    focus_rows = []
    for item in spec_focus_items(entries):
        path = verified_path(entries, item["cache_path"])
        with rasterio.open(path) as ds:
            if (ds.shape, ds.crs, ds.transform) != grid:
                raise ValueError(f"Focus raster grid differs: {item['cache_path']}")
            values = ds.read(1).astype(np.float32)
        if not np.isfinite(values[foot]).all():
            raise ValueError(f"Non-finite values inside footprint: {item['cache_path']}")
        support = (values > 0) & foot
        ranks, norm = centered_ranks(values[foot])
        res = check_comparator(ranks, norm, support, lattice, foot)
        focus_rows.append({
            "site": item["site"],
            "file": Path(item["path"]).name,
            "sha256": item["sha256"],
            "positive_cells": int(support.sum()),
            "matched_within_3px_of_lattice": res["matches_within_3px"],
            "overlap_fraction_vs_lattice": round(res["overlap_fraction"], 6),
            "spearman_vs_lattice": round(res["spearman_full_footprint"], 6),
            "duplicate_by_literal_gate": res["duplicate"],
        })

    bound = max_passing_positive_cells(uncovered)
    null_min = min(r["overlap_fraction"] for r in null_rows)
    return {
        "schema": SCHEMA,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": ("Calibration of the literal 3-px / 70% uniqueness gate against the one pinned "
                  "lattice witness. Not a score, not a submission, not a registry-completeness "
                  "claim. Owner mirrors are not organizer-authenticated."),
        "gate": {
            "radius_px": RADIUS_PX,
            "overlap_limit": OVERLAP_LIMIT,
            "rho_limit": 0.90,
            "support_rule": "finite value > 0 inside the template footprint",
            "duplicate_rule": "10 * matched > 7 * n (scripts/check_uniqueness.py::check_comparator)",
        },
        "inputs": [
            {"role": "template", "cache_path": "inputs/sample.tif",
             "sha256": entries["inputs/sample.tif"]["sha256"], "source": f"{entries['inputs/sample.tif']['repo']}@{entries['inputs/sample.tif']['ref']}"},
            {"role": "lattice_witness", "cache_path": "inputs/lattice.tif",
             "sha256": entries["inputs/lattice.tif"]["sha256"], "source": f"{entries['inputs/lattice.tif']['repo']}@{entries['inputs/lattice.tif']['ref']}"},
        ],
        "grid": {"shape": list(grid[0]), "crs": str(grid[1]), "pixel_size_m": 100},
        "footprint_cells": footprint_cells,
        "witness_lattice": {
            "positive_cells_in_footprint": int(lat_pos.sum()),
            "footprint_cells_within_3px": int((foot & near).sum()),
            "coverage_fraction": round(coverage, 6),
            "uncovered_footprint_cells": uncovered,
            "vendored_certificate_uncovered": cert["uncovered_allowed_pixels"],
            "vendored_certificate_universal_blocker": cert["universal_overlap_blocker"],
        },
        "pigeonhole_bound": {
            "max_passing_positive_cells": bound,
            "statement": ("Under the literal gate, any candidate with more than this many positive cells "
                          "is DUPLICATE regardless of its content, because at least 30% of its positive "
                          "cells would have to lie in the uncovered cells and there are only "
                          f"{uncovered} of them."),
        },
        "null_controls": null_rows,
        "null_controls_min_overlap": null_min,
        "focus_files_vs_lattice": focus_rows,
        "conclusion": ("The literal gate is saturated by this witness. Uniform random dot sets (no copying "
                       "possible) are flagged as duplicates, and every candidate above the pigeonhole bound "
                       "fails by arithmetic. The gate therefore cannot distinguish a copy from a non-copy "
                       "for this witness. A rule change, witness exclusion or null-calibrated criterion needs "
                       "explicit user approval; none has been applied."),
        "upload_authorized": False,
        "submission_generated": False,
    }


def spec_focus_items(entries: dict) -> list[dict]:
    spec = json.loads(MANIFEST.read_text())
    items = []
    for item in spec["references"]:
        if item.get("site"):
            items.append(item)
    return items


def comparable(doc: dict) -> dict:
    out = dict(doc)
    out.pop("generated_utc", None)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    p.add_argument("--check", action="store_true", help="recompute and compare with the committed receipt")
    args = p.parse_args()
    try:
        doc = compute()
    except (OSError, ValueError, KeyError, AssertionError, rasterio.errors.RasterioError) as exc:
        print(f"Calibration failed closed: {exc}", file=sys.stderr)
        return 1
    if args.check:
        if not args.output.is_file():
            print(f"Missing receipt: {args.output}", file=sys.stderr)
            return 1
        committed = json.loads(args.output.read_text())
        if comparable(committed) != comparable(json.loads(json.dumps(doc))):
            print("Committed calibration receipt differs from recomputation", file=sys.stderr)
            return 1
        print("calibration receipt up to date")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(doc, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"wrote": str(args.output.relative_to(ROOT)),
                      "uncovered_footprint_cells": doc["witness_lattice"]["uncovered_footprint_cells"],
                      "max_passing_positive_cells": doc["pigeonhole_bound"]["max_passing_positive_cells"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Literal duplicate gate of a FINAL raster against every pinned focus-registry raster.

This wraps the shared checker in ``scripts/check_uniqueness.py`` (``check_comparator``
and ``read_tif``) so there is one definition of rho / 3-px overlap. It does not
replace the surface/final receipt flow: it is a post-hoc audit of already-saved bytes
and is therefore labelled ``POST_HOC`` and can never authorise an upload.

Rules applied (PARALLEL-RUN PROTOCOL, item 1):
  * rank correlation of the candidate vs a registry raster over the template footprint > 0.90
  * more than 70% of candidate dots within 3 px of one registry raster's dots  -> duplicate

Every registry item is reported. Grid mismatches and unreadable items are recorded as
``not_comparable`` (fail-closed: they are NOT silently dropped).
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
from check_uniqueness import centered_ranks, check_comparator, read_tif  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--template", type=Path, required=True,
                    help="raster whose grid and finite footprint define the comparison")
    ap.add_argument("--manifest", type=Path, default=ROOT / "registry/focus_registry_manifest.json")
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()

    manifest = json.loads(a.manifest.read_text())
    cand, cand_mask, grid = read_tif(a.candidate)
    tmpl, tmpl_mask, tgrid = read_tif(a.template)
    if tgrid != grid:
        raise SystemExit("candidate and template grids differ")
    foot = np.isfinite(tmpl) & (tmpl_mask > 0)
    if np.any(cand_mask[foot] == 0) or not np.isfinite(cand[foot]).all():
        raise SystemExit("candidate has missing/NaN cells inside the footprint")
    if np.any((cand[foot] < 0) | (cand[foot] > 1)):
        raise SystemExit("candidate has values outside [0,1] inside the footprint")
    support = (cand > 0) & foot
    ranks, norm = centered_ranks(cand[foot])

    rows = []
    worst = {"spearman_full_footprint": -1.0, "overlap_fraction": -1.0}
    n_dup = 0
    for row in manifest["rasters"]:
        if row.get("status") != "ok":
            rows.append({"path": row["path"], "status": "not_comparable: manifest status " + str(row.get("status"))})
            continue
        path = ROOT / row["local"]
        if not (path.is_file() and sha256(path) == row["sha256"]):
            rows.append({"path": row["path"], "status": "not_comparable: missing or hash mismatch"})
            continue
        try:
            ref, ref_mask, _ = read_tif(path, expected_grid=grid)
        except Exception as exc:  # grid mismatch or unreadable -> not comparable, reported
            rows.append({"repo": row["repo"], "path": row["path"], "status": f"not_comparable: {exc}"})
            continue
        if np.any(ref_mask[foot] == 0) or not np.isfinite(ref[foot]).all():
            rows.append({"repo": row["repo"], "path": row["path"],
                         "status": "not_comparable: reference NaN/masked inside footprint"})
            continue
        res = check_comparator(ranks, norm, support, ref, foot)
        rows.append({"repo": row["repo"], "ref": row["ref"], "path": row["path"],
                     "sha256": row["sha256"], "status": "compared", **res})
        worst["spearman_full_footprint"] = max(worst["spearman_full_footprint"], res["spearman_full_footprint"])
        worst["overlap_fraction"] = max(worst["overlap_fraction"], res["overlap_fraction"])
        n_dup += int(res["duplicate"])

    compared = [r for r in rows if r.get("status") == "compared"]
    summary = {
        "candidate": a.candidate.name,
        "candidate_sha256": sha256(a.candidate),
        "candidate_positive_cells": int(support.sum()),
        "template": a.template.name,
        "registry_manifest_sha256": sha256(a.manifest),
        "registry_items_total": len(manifest["rasters"]),
        "registry_items_compared": len(compared),
        "registry_items_not_comparable": len(rows) - len(compared),
        "max_spearman_full_footprint": round(worst["spearman_full_footprint"], 6),
        "max_overlap_fraction_3px": round(worst["overlap_fraction"], 6),
        "duplicate_witnesses": n_dup,
        "status": "DUPLICATE_STOP" if n_dup else "NO_DUPLICATE_WITNESS_IN_COMPARABLE_SET",
        "scope_note": ("POST_HOC audit of saved bytes against the 440-raster focus registry only. "
                       "Not the live parallel-run registry, not a pre-placement surface receipt, "
                       "and not an upload authorisation."),
        "upload_authorized": False,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps({"summary": summary, "comparisons": rows}, indent=2,
                                   allow_nan=False) + "\n")
    print(json.dumps(summary, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

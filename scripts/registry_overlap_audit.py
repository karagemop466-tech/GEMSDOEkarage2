#!/usr/bin/env python3
"""Post-hoc uniqueness audit of finished GeoTIFFs against the focus-site registry.

This is a *post-hoc* driver around the shared fail-closed comparator in
``scripts/check_uniqueness.py`` (``centered_ranks`` and ``check_comparator``).
It loops over the registry once, so several candidate rasters can be compared
without re-ranking every reference per candidate. It does NOT replace the
placement-time surface/final receipts required by the parallel-run protocol:
it proves only that the saved bytes fail or pass the duplicate gates against
the registry rasters that were available when it ran.

Duplicate rule (protocol): Spearman |rho| > 0.90 over the template footprint, OR
more than 70% of a candidate's positive dots lying within 3 px (Euclidean,
100 m pixels) of one registry raster's positive dots. Any single duplicate
witness is enough to fail a candidate.

Inputs
  --template   competition-grid template (NaN outside footprint); footprint =
               finite AND mask > 0, exactly as in check_uniqueness.py.
  --registry   JSON manifest with a "rasters" list. Each entry needs "local"
               (path relative to the repo root) and "sha256". Entries whose
               files are missing or whose SHA-256 differs are reported and
               FAIL CLOSED (the audit exits non-zero).
  --candidate  one or more candidate GeoTIFFs.
  --exclude-sha256  candidate SHA-256 values to skip (a file is not compared
               against itself).
  --output     JSON receipt path.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_uniqueness import centered_ranks, check_comparator, within_3px_of_reference  # noqa: E402


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _grid(ds):
    return (ds.shape, ds.crs.to_string() if ds.crs else None, tuple(ds.transform)[:6])


def load_template(path: Path):
    with rasterio.open(path) as ds:
        arr = ds.read(1).astype(np.float64)
        mask = ds.read_masks(1)
        grid = _grid(ds)
    foot = np.isfinite(arr) & (mask > 0)
    if not foot.any():
        raise ValueError("empty template footprint")
    return foot, grid


def load_candidate(path: Path, foot: np.ndarray, grid):
    with rasterio.open(path) as ds:
        if ds.count != 1:
            raise ValueError(f"{path}: not single-band")
        if _grid(ds) != grid:
            raise ValueError(f"{path}: grid/CRS/transform mismatch with template")
        arr = ds.read(1).astype(np.float64)
    if not np.isfinite(arr[foot]).all():
        raise ValueError(f"{path}: non-finite values inside footprint")
    if np.any((arr[foot] < 0) | (arr[foot] > 1)):
        raise ValueError(f"{path}: values outside [0,1] inside footprint")
    support = (arr > 0) & foot
    if not support.any():
        raise ValueError(f"{path}: no positive dots inside footprint")
    return arr, support


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--template", type=Path, required=True)
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, action="append", required=True)
    ap.add_argument("--exclude-sha256", action="append", default=[])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    # Resolve every input once so that later relative_to() calls cannot fail.
    args.template = args.template.resolve()
    args.registry = args.registry.resolve()
    args.candidate = [p.resolve() for p in args.candidate]
    args.output = args.output.resolve()

    def _rel(p: Path) -> str:
        return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)

    foot, grid = load_template(args.template)
    cands = []
    for p in args.candidate:
        arr, support = load_candidate(p, foot, grid)
        ranks, norm = centered_ranks(arr[foot])
        del arr  # keep memory bounded: only ranks and support are needed later
        cands.append({"path": p, "sha256": sha256_file(p), "support": support,
                      "ranks": ranks, "norm": norm, "n_dots": int(support.sum()),
                      "results": [], "status": "PASS", "witness": None})

    manifest = json.loads(args.registry.read_text())
    entries = manifest["rasters"]
    excluded = set(args.exclude_sha256)
    failed_inputs = []
    compared_refs = 0
    seen = set()
    for e in entries:
        local = ROOT / e["local"]
        sha = e.get("sha256", "")
        if sha in excluded or (sha in seen):
            continue
        seen.add(sha)
        if not local.is_file() or sha256_file(local) != sha:
            failed_inputs.append({"path": e["local"], "reason": "missing or SHA-256 mismatch"})
            continue
        with rasterio.open(local) as ds:
            if _grid(ds) != grid:
                # Different grid: cannot be compared on the competition footprint; record, do not pass silently.
                failed_inputs.append({"path": e["local"], "reason": "grid mismatch (not comparable)"})
                continue
            ref = ds.read(1).astype(np.float64)
            rmask = ds.read_masks(1)
        if np.any(rmask[foot] == 0) or not np.isfinite(ref[foot]).all():
            failed_inputs.append({"path": e["local"], "reason": "reference has missing or non-finite pixels in footprint"})
            continue
        if np.any((ref[foot] < 0) | (ref[foot] > 1)):
            failed_inputs.append({"path": e["local"], "reason": "reference values outside [0,1] in footprint"})
            continue
        compared_refs += 1
        if compared_refs % 25 == 0:
            print(f"[audit] compared {compared_refs} references", flush=True)
        ref_dots = (ref > 0) & foot
        if not ref_dots.any():
            # A reference with no positive dots cannot form an overlap witness; record it.
            for c in cands:
                c["results"].append({"reference": e["local"], "sha256": sha, "note": "no positive dots"})
            continue
        ref_rn = None
        ref_near = None
        for c in cands:
            if c["sha256"] == sha:
                continue
            if ref_rn is None:
                ref_rn = centered_ranks(ref[foot])          # rank each reference once
                ref_near = within_3px_of_reference(ref_dots)  # dilate each reference once
            try:
                r = check_comparator(c["ranks"], c["norm"], c["support"], ref, foot,
                                     ref_ranks_norm=ref_rn, ref_near=ref_near)
            except ValueError as exc:  # fail closed per pair
                c["results"].append({"reference": e["local"], "sha256": sha, "error": str(exc)})
                c["status"] = "ERROR"
                continue
            rec = {"reference": e["local"], "sha256": sha, **r}
            c["results"].append(rec)
            if r["duplicate"] and c["status"] == "PASS":
                c["status"] = "DUPLICATE"
                c["witness"] = {"reference": e["local"], "spearman": r["spearman_full_footprint"],
                                "overlap_fraction": r["overlap_fraction"]}
        del ref, ref_dots, ref_rn, ref_near

    out = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "POST-HOC-REGISTRY-AUDIT (not a placement-time surface receipt)",
        "template": _rel(args.template),
        "template_sha256": sha256_file(args.template),
        "registry_manifest": _rel(args.registry),
        "registry_manifest_sha256": sha256_file(args.registry),
        "registry_entries_listed": len(entries),
        "registry_references_compared": compared_refs,
        "registry_inputs_failed_closed": failed_inputs,
        "rules": {"spearman_abs_max": 0.90, "overlap_3px_max": 0.70},
        "candidates": [],
        "upload_authorized": False,
    }
    for c in cands:
        errs = [r for r in c["results"] if "error" in r]
        max_rho = max((abs(r["spearman_full_footprint"]) for r in c["results"] if "spearman_full_footprint" in r), default=None)
        max_ov = max((r["overlap_fraction"] for r in c["results"] if "overlap_fraction" in r), default=None)
        argmax_ov = max((r for r in c["results"] if "overlap_fraction" in r), key=lambda r: r["overlap_fraction"], default=None)
        status = c["status"]
        if failed_inputs and status == "PASS":
            status = "INCOMPLETE_INPUTS"
        out["candidates"].append({
            "file": str(c["path"]),
            "sha256": c["sha256"],
            "n_dots": c["n_dots"],
            "status": status,
            "max_abs_spearman": None if max_rho is None else round(max_rho, 6),
            "max_overlap_3px": None if max_ov is None else round(max_ov, 6),
            "closest_reference": None if argmax_ov is None else argmax_ov["reference"],
            "duplicate_witness": c["witness"],
            "pair_errors": errs,
            "comparisons": c["results"],
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    summary = [(c["file"], c["status"], c["max_overlap_3px"], c["max_abs_spearman"]) for c in out["candidates"]]
    for row in summary:
        print(row)
    print(f"compared references: {compared_refs}; failed-closed inputs: {len(failed_inputs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check pre-placement surface/support OR final dots against an explicit raster registry.

This is a fail-closed geometry check, not an evaluator or selector. A surface
run must precede placement. Final checks require its passing, hash-bound receipt
and the identical registry manifest. A declared-complete registry is necessary
but the declaration itself cannot prove that all parallel work was registered.
Positive support means values > 0; distances are Euclidean and <= 3 pixels.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from restore_references import digest  # noqa: E402
from raster_integrity import require_single_file_dataset  # noqa: E402


def centered_ranks(values: np.ndarray) -> tuple[np.ndarray, float]:
    if not np.isfinite(values).all():
        raise ValueError("Non-finite inside-footprint values prevent a similarity check")
    ranks = rankdata(values, method="average").astype(np.float64, copy=False)
    ranks -= ranks.mean()
    norm = float(np.sqrt(np.dot(ranks, ranks)))
    if norm == 0.0:
        raise ValueError("Constant field has undefined rank correlation; fail closed")
    return ranks, norm


def check_comparator(candidate_ranks: np.ndarray, candidate_norm: float,
                     support: np.ndarray, ref: np.ndarray, foot: np.ndarray) -> dict:
    if ref.shape != foot.shape or support.shape != foot.shape:
        raise ValueError("Reference/support shape mismatch")
    values = ref[foot]
    ref_ranks, ref_norm = centered_ranks(values)
    rho = float(np.dot(candidate_ranks, ref_ranks) / (candidate_norm * ref_norm))
    ref_dots = np.isfinite(ref) & (ref > 0) & foot
    if not ref_dots.any():
        raise ValueError("Reference has no positive support")
    n = int((support & foot).sum())
    if n == 0:
        raise ValueError("Candidate support is empty")
    near = distance_transform_edt(~ref_dots) <= 3.0
    matched = int((support & foot & near).sum())
    return {"spearman_full_footprint": rho, "matches_within_3px": matched,
            "support_pixels": n, "overlap_fraction": matched / n,
            "duplicate": bool(rho > 0.90 or 10 * matched > 7 * n)}


def read_tif(path: Path, expected_grid=None):
    with rasterio.open(path) as ds:
        require_single_file_dataset(ds, path)
        if ds.count != 1 or ds.crs is None:
            raise ValueError(f"Expected single-band raster and CRS: {path}")
        grid = (ds.shape, ds.crs, ds.transform)
        if expected_grid is not None and grid != expected_grid:
            raise ValueError(f"Reference grid mismatch: {path}")
        arr = ds.read(1)
        mask = ds.read_masks(1)
    return arr, mask, grid


def audit(stage: str, field_path: Path, template_path: Path, registry_path: Path,
          support_path: Path | None = None, surface_receipt: Path | None = None,
          surface_path: Path | None = None) -> dict:
    manifest_sha = digest(registry_path)
    manifest = json.loads(registry_path.read_text())
    if digest(registry_path) != manifest_sha:
        raise ValueError("Registry changed while being read")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Registry must contain at least one pinned reference")
    template_sha = digest(template_path)
    field_sha = digest(field_path)
    support_sha_before = digest(support_path) if support_path is not None else None
    template, template_mask, expected_grid = read_tif(template_path)
    foot = np.isfinite(template) & (template_mask > 0)
    if not foot.any():
        raise ValueError("Empty template footprint")

    if stage == "surface":
        if support_path is None:
            raise ValueError("Surface stage requires a preregistered pre-placement support mask")
        field = np.load(field_path, allow_pickle=False)
        raw_support = np.load(support_path, allow_pickle=False)
        if field.shape != foot.shape or raw_support.shape != foot.shape:
            raise ValueError("Surface or support shape mismatch")
        if not np.isfinite(raw_support).all() or not np.isin(raw_support, (0, 1)).all():
            raise ValueError("Support must be a finite binary array")
        support = raw_support.astype(bool)
        if np.any(support & ~foot):
            raise ValueError("Surface support includes cells outside footprint")
        support_sha = digest(support_path)
    elif stage == "final":
        if surface_receipt is None or surface_path is None or support_path is None:
            raise ValueError("Final stage requires the prior surface receipt, surface and support")
        receipt = json.loads(surface_receipt.read_text())
        if (receipt.get("stage") != "surface" or receipt.get("status") != "PASS" or
                receipt.get("registry_sha256") != manifest_sha or
                receipt.get("registry_declared_complete") is not True or
                receipt.get("comparison_count") != len(entries) or
                receipt.get("registry_entry_count") != len(entries) or
                receipt.get("template_sha256") != template_sha or
                receipt.get("candidate_sha256") != digest(surface_path) or
                receipt.get("support_sha256") != support_sha_before):
            raise ValueError("Surface receipt does not bind the same surface, support, registry and template")
        # A JSON status can be stale or forged. Recompute the full surface gate
        # against current, pinned bytes before interpreting the final dots.
        checked_surface = audit("surface", surface_path, template_path, registry_path, support_path)
        if checked_surface["status"] != "PASS":
            raise ValueError("Prior surface fails re-audit against the current registry")
        prior_support = np.load(support_path, allow_pickle=False)
        if (prior_support.shape != foot.shape or not np.isfinite(prior_support).all() or
                not np.isin(prior_support, (0, 1)).all() or np.any(prior_support.astype(bool) & ~foot)):
            raise ValueError("Invalid pre-placement support")
        field, mask, _ = read_tif(field_path, expected_grid)
        if not np.isfinite(field[foot]).all() or np.any((field[foot] < 0) | (field[foot] > 1)):
            raise ValueError("Final raster has invalid values inside the footprint")
        if np.any(mask[foot] == 0):
            raise ValueError("Final raster is masked inside the footprint")
        support = (field > 0) & foot
        if np.any(support & ~prior_support.astype(bool)):
            raise ValueError("Final dots extend beyond the checked pre-placement support")
        support_sha = digest(support_path)
    else:
        raise ValueError("Unknown stage")

    candidate_ranks, norm = centered_ranks(field[foot])
    if not (support & foot).any():
        raise ValueError("Candidate support is empty")
    comparisons = []
    seen = set()
    for entry in entries:
        path = Path(entry["path"])
        if not path.is_absolute():
            path = registry_path.resolve().parent / path
        sha = entry["sha256"]
        if (str(path), sha) in seen:
            raise ValueError(f"Duplicate registry entry: {path}")
        seen.add((str(path), sha))
        if len(sha) != 64 or not path.is_file() or digest(path) != sha:
            raise ValueError(f"Missing or changed registry reference: {path}")
        reference, refmask, _ = read_tif(path, expected_grid)
        if np.any(refmask[foot] == 0):
            raise ValueError(f"Reference has missing pixels inside the footprint: {path}")
        if not np.isfinite(reference[foot]).all() or np.any((reference[foot] < 0) | (reference[foot] > 1)):
            raise ValueError(f"Reference has invalid values inside the footprint: {path}")
        result = check_comparator(candidate_ranks, norm, support, reference, foot)
        if digest(path) != sha:
            raise ValueError(f"Registry reference changed during audit: {path}")
        comparisons.append({"path": str(path), "sha256": sha, **result})
        # A single duplicate witness is sufficient. Do not keep placing dots.
        if result["duplicate"]:
            status = "DUPLICATE_STOP"
            break
    else:
        status = "PASS" if manifest.get("complete") is True else "INCOMPLETE_REGISTRY"
    if (digest(field_path) != field_sha or digest(template_path) != template_sha or
            digest(registry_path) != manifest_sha or support_sha != support_sha_before or
            digest(support_path) != support_sha_before):
        raise ValueError("Candidate, support, template or registry changed during audit")
    return {"generated_utc": datetime.now(timezone.utc).isoformat(), "stage": stage,
            "status": status, "candidate_sha256": field_sha,
            "support_sha256": support_sha, "template_sha256": template_sha,
            "registry_sha256": manifest_sha, "registry_declared_complete": manifest.get("complete") is True,
            "comparison_count": len(comparisons), "registry_entry_count": len(entries),
            "comparisons": comparisons,
            "scope_note": ("A manifest's completeness declaration is not independent proof of a complete "
                           "live registry; a receipt alone cannot independently prove placement chronology."),
            "upload_authorized": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("surface", "final"), required=True)
    parser.add_argument("--field", type=Path, required=True, help="surface .npy or final .tif")
    parser.add_argument("--support", type=Path, help="binary pre-placement support .npy; required at both stages")
    parser.add_argument("--surface-receipt", type=Path, help="required before final stage")
    parser.add_argument("--surface-field", type=Path, help="original surface .npy; required before final stage")
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = audit(args.stage, args.field, args.template, args.registry, args.support,
                       args.surface_receipt, args.surface_field)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(json.dumps(result, indent=2, allow_nan=False))
        return {"PASS": 0, "DUPLICATE_STOP": 2, "INCOMPLETE_REGISTRY": 1}[result["status"]]
    except (OSError, ValueError, KeyError, json.JSONDecodeError, rasterio.errors.RasterioError) as exc:
        print(f"Uniqueness audit failed closed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

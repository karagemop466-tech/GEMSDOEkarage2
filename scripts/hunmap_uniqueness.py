#!/usr/bin/env python3
"""Registry overlap / uniqueness audit for the H-UNMAP candidate.

The binding lane rule (parallel-run protocol, clause 1) is literal:

* rank correlation above **0.90** with any registry raster, **or**
* more than **70%** of the candidate's dots within **3 px** of one registry
  raster's dots

is lane drift: log it as a duplicate and stop.

This script measures both against every raster of the pinned nine-site
registry snapshot (``registry/focus_registry_manifest.json``, 489 SHA-256
verified rasters) plus the 13GEMSDOE spacing-5 lattice witness, and writes a
receipt.  It never grants clearance on its own: the registry is a filtered
snapshot of nine public repositories, not a complete global registry.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.spatial import cKDTree
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from lane_hunmap import EVALUATOR, LANE, log  # noqa: E402

REGISTRY = ROOT / ".cache" / "registry"
MANIFEST = ROOT / "registry" / "focus_registry_manifest.json"
EVID = ROOT / "evidence" / "hunmap"
RADIUS_PX = 3.0


def candidate_dots(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return np.isfinite(a) & (a > 0)


def registry_raster_paths() -> list[tuple[str, Path]]:
    man = json.loads(MANIFEST.read_text())
    out = []
    for row in man["rasters"]:
        p = ROOT / row["local"]
        if p.exists():
            out.append((f"{row['repo']}:{row['path']}", p))
    return out


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = rankdata(a)
    rb = rankdata(b)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / denom) if denom > 0 else float("nan")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", required=True, help="candidate GeoTIFF")
    ap.add_argument("--extra", nargs="*", default=[], help="extra registry rasters")
    ap.add_argument("--sample-cells", type=int, default=200_000)
    ap.add_argument("--out", default=str(EVID / "hunmap_uniqueness.json"))
    args = ap.parse_args(argv)

    EVID.mkdir(parents=True, exist_ok=True)
    cand_path = Path(args.candidate)
    with rasterio.open(cand_path) as ds:
        cfield = ds.read(1)
        cshape = ds.shape
        ctransform = tuple(ds.transform)[:6]
    my = np.isfinite(cfield) & (cfield > 0)
    my_yx = np.argwhere(my)
    tree_mine = cKDTree(my_yx)

    rng = np.random.default_rng(520810)
    n_cells = cfield.size
    idx = rng.choice(n_cells, size=min(args.sample_cells, n_cells), replace=False)
    rows_idx = idx // cfield.shape[1]
    cols_idx = idx % cfield.shape[1]
    my_sample = cfield[rows_idx, cols_idx].astype(np.float64)
    my_rank = rankdata(my_sample)

    entries = registry_raster_paths()
    for extra in args.extra:
        entries.append(("extra:" + Path(extra).name, Path(extra)))

    results = []
    for label, path in entries:
        try:
            with rasterio.open(path) as ds:
                if ds.shape != cshape or tuple(ds.transform)[:6] != ctransform:
                    results.append(dict(label=label, file=str(path),
                                        comparable=False,
                                        reason="different grid (shape or transform)"))
                    continue
                arr = ds.read(1)
        except Exception as exc:  # pragma: no cover - defensive
            results.append(dict(label=label, file=str(path), comparable=False,
                                reason=f"unreadable: {exc}"))
            continue
        dots = np.isfinite(arr) & (arr > 0)
        n_dots = int(dots.sum())
        if n_dots == 0:
            results.append(dict(label=label, file=str(path), comparable=True,
                                n_registry_dots=0, overlap_fraction=0.0,
                                spearman=0.0, verdict="no positive support"))
            continue
        ys, xs = np.nonzero(dots)
        tree = cKDTree(np.column_stack([ys, xs]))
        dist, _ = tree.query(my_yx, k=1, distance_upper_bound=RADIUS_PX)
        hit = np.isfinite(dist)
        overlap = float(hit.mean()) if my_yx.size else 0.0
        sample = arr[rows_idx, cols_idx].astype(np.float64)
        rho = spearman(my_rank, sample)
        verdict = "DUPLICATE_STOP" if (rho > 0.90 or overlap > 0.70) else "pass"
        results.append(dict(label=label, file=str(path), comparable=True,
                            n_registry_dots=n_dots,
                            overlap_fraction=overlap,
                            matched_dots=int(hit.sum()),
                            candidate_dots=int(my.sum()),
                            spearman=rho, verdict=verdict))
        if verdict == "DUPLICATE_STOP":
            log(f"DUPLICATE_STOP {label}: overlap {overlap:.4f} rho {rho:.4f}")

    comparable = [r for r in results if r.get("comparable")]
    worst_overlap = max(comparable, key=lambda r: r["overlap_fraction"]) if comparable else None
    worst_rho = max(comparable, key=lambda r: r["spearman"]) if comparable else None
    fails = [r for r in comparable if r["verdict"] == "DUPLICATE_STOP"]
    out = dict(
        lane=LANE, evidence_class="REGISTRY-OVERLAP MEASUREMENT",
        evaluator_version=EVALUATOR,
        candidate=str(cand_path),
        candidate_dots=int(my.sum()),
        rule=dict(rank_correlation_max=0.90, overlap_fraction_max=0.70,
                  radius_px=RADIUS_PX,
                  text="rank correlation > 0.90 or > 70% of dots within 3 px of "
                       "one registry raster's dots = duplicate, stop"),
        registry_size=len(entries),
        registry_note="filtered nine-repository snapshot (489 SHA-256 verified rasters); "
                      "not a complete global registry",
        comparable_count=len(comparable),
        non_comparable_count=len(results) - len(comparable),
        duplicate_stops=len(fails),
        max_overlap=worst_overlap,
        max_spearman=worst_rho,
        verdict="DUPLICATE_STOP" if fails else "unique_vs_registry_snapshot",
        rows=results,
    )
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    log(f"uniqueness audit: {out['verdict']} "
        f"(max overlap {worst_overlap['overlap_fraction'] if worst_overlap else float('nan'):.4f}, "
        f"max rho {worst_rho['spearman'] if worst_rho else float('nan'):.4f}) -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

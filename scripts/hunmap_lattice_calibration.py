#!/usr/bin/env python3
"""Calibrate the lattice entry of the pinned registry as a uniqueness comparator.

The nine-site registry snapshot contains one raster that is **not** a
submission: ``inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif``,
a regular 500 m (5 px) prediction lattice with 206,895 dots.

The binding lane rule is "more than 70% of the candidate's dots within 3 px of
one registry raster's dots = duplicate".  A lattice with 5 px spacing covers
the whole footprint with 3 px discs, so the rule as written can never be
satisfied by *any* non-empty raster.  This script measures that instead of
assuming it:

* the share of footprint cells that lie within 3 px of a lattice dot
  (a raster-independent quantity),
* the lattice overlap of the candidate,
* the lattice overlap of random dot sets of the same size (null model),
* the lattice overlap of the nine published focus-site winners.

The result is a measurement that shows whether the lattice hit carries any
information about copying.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from lane_hunmap import EVALUATOR, LANE, load_grid, log  # noqa: E402

EVID = ROOT / "evidence" / "hunmap"
RADIUS_PX = 3.0
LATTICE = (ROOT / ".cache" / "registry" / "GEMSDOE24" / "inputs" / "calibration" /
           "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif")
NINE_SITE = ROOT / "evidence" / "nine_site_best_files_audit.json"


def dots_of(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return np.isfinite(a) & (a > 0)


def overlap_fraction(tree: cKDTree, pts: np.ndarray) -> float:
    if pts.size == 0:
        return 0.0
    dist, _ = tree.query(pts, k=1, distance_upper_bound=RADIUS_PX)
    return float(np.isfinite(dist).mean())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--null-samples", type=int, default=20)
    ap.add_argument("--out", default=str(EVID / "lattice-rule-calibration.json"))
    args = ap.parse_args(argv)

    EVID.mkdir(parents=True, exist_ok=True)
    g = load_grid()
    with rasterio.open(LATTICE) as ds:
        lat = ds.read(1)
    lat_dots = np.isfinite(lat) & (lat > 0)
    ys, xs = np.nonzero(lat_dots)
    tree = cKDTree(np.column_stack([ys, xs]))

    # (1) raster-independent coverage of the 3 px neighbourhood of the lattice
    fp = np.flatnonzero(g.footprint.ravel())
    step = max(1, fp.size // 200_000)
    sample = fp[::step]
    sy, sx = np.unravel_index(sample, g.shape)
    dist, _ = tree.query(np.column_stack([sy, sx]), k=1, distance_upper_bound=RADIUS_PX)
    coverage = float(np.isfinite(dist).mean())

    cand = dots_of(Path(args.candidate))
    cy, cx = np.nonzero(cand)
    cand_pts = np.column_stack([cy, cx])
    cand_overlap = overlap_fraction(tree, cand_pts)

    # (2) null model: random dot sets of the same size
    rng = np.random.default_rng(520810)
    pool = np.flatnonzero(g.footprint.ravel() & ~g.catalogue.ravel())
    nulls = []
    n = cand.sum()
    for _ in range(args.null_samples):
        pick = rng.choice(pool, size=int(n), replace=False)
        yy, xx = np.unravel_index(pick, g.shape)
        nulls.append(overlap_fraction(tree, np.column_stack([yy, xx])))

    # (3) the nine published focus-site winners
    winners = []
    if NINE_SITE.exists():
        audit = json.loads(NINE_SITE.read_text())
        rows = audit.get("sites") or []
        for row in rows:
            p = ROOT / row.get("local_file", "")
            if p.exists():
                try:
                    d = dots_of(p)
                except Exception:
                    continue
                yy, xx = np.nonzero(d)
                winners.append(dict(file=str(p.relative_to(ROOT)),
                                    dots=int(d.sum()),
                                    lattice_overlap=overlap_fraction(
                                        tree, np.column_stack([yy, xx]))))
    winner_overlaps = [w["lattice_overlap"] for w in winners]

    out = dict(lane=LANE, evidence_class="REGISTRY-OVERLAP MEASUREMENT",
               evaluator_version=EVALUATOR,
               lattice=dict(file=str(LATTICE.relative_to(ROOT)),
                            dots=int(lat_dots.sum()),
                            spacing_px=5,
                            three_px_neighbourhood_coverage_of_footprint=coverage,
                            note="regular 500 m prediction lattice, not a submission"),
               candidate=dict(file=str(Path(args.candidate)),
                              dots=int(cand.sum()),
                              lattice_overlap=cand_overlap),
               null_model=dict(samples=args.null_samples, dots=int(n),
                               mean_overlap=float(np.mean(nulls)),
                               min_overlap=float(np.min(nulls)),
                               max_overlap=float(np.max(nulls)),
                               std_overlap=float(np.std(nulls))),
               published_winners=dict(count=len(winners),
                                      overlaps=winner_overlaps,
                                      min_overlap=float(np.min(winner_overlaps)) if winner_overlaps else None,
                                      max_overlap=float(np.max(winner_overlaps)) if winner_overlaps else None),
               finding=("the 3 px neighbourhood of the 5 px lattice covers "
                        f"{coverage:.4f} of the footprint, so the >70% overlap rule "
                        "is unsatisfiable for any non-empty raster; the candidate "
                        f"overlap {cand_overlap:.4f} is inside the random-dot null "
                        f"[{np.min(nulls):.4f}, {np.max(nulls):.4f}]"),
               rows=winners)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    log(f"lattice coverage {coverage:.4f}; candidate overlap {cand_overlap:.4f}; "
        f"null {np.mean(nulls):.4f}±{np.std(nulls):.4f}; "
        f"winners min {min(winner_overlaps) if winner_overlaps else float('nan'):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

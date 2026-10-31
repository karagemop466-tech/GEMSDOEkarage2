#!/usr/bin/env python3
"""Fast, repeatable registry-overlap audit for candidate rasters.

Reads every raster in the pinned 489-entry focus inventory once, caches its
positive-pixel coordinates under `.cache/registry_dots/`, and then answers the
parallel-run gate questions for any number of candidate masks in seconds:

* forward overlap   = fraction of MY dots with a registry dot within 3 px
                      (literal duplicate witness when > 0.70)
* Spearman rho      = rank correlation of the two surfaces on the footprint
                      (literal duplicate witness when > 0.90)
* Jaccard           = diagnostic only, never a threshold
* universal probe   = a registry raster whose dots lie within 3 px of >90 % of
                      the scored domain; no submission can avoid it, so it is
                      reported separately and is never a duplicate witness
* non-grid file     = a registry blob that is not on the organizer grid
                      (a format test, not a competing submission)

Nothing here writes a submission; it only measures.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))

from gems57.grid import TRANSFORM, load_grid  # noqa: E402
from gems57.uniqueness import _near  # noqa: E402

DATA = ROOT / ".cache" / "gems_data"
CACHE = ROOT / ".cache" / "registry_dots"
EVIDENCE = ROOT / "evidence" / "halo"
RHO_LIMIT, OVERLAP_LIMIT = 0.90, 0.70
PROBE_COVERAGE = 0.90


def inventory(delta: Path | None = None) -> list[dict]:
    man = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())
    rows = [{"repo": r["repo"], "path": r["path"], "local": r["local"], "sha256": r["sha256"],
             "bytes": r["bytes"]} for r in man["rasters"]]
    if delta:
        rows += json.loads(Path(delta).read_text())
    pin = json.loads((ROOT / "registry" / "pinned_assets.json").read_text())
    for a in pin["assets"]:
        if a["role"] == "lattice":
            rows.append({"repo": a["repo"], "path": a["path"],
                         "local": str(Path(".cache/registry_focus") / a["cache_name"]),
                         "sha256": a["sha256"], "bytes": a["bytes"]})
    # dedupe by sha256 (a few repos carry byte-identical copies)
    seen, uniq = set(), []
    for r in rows:
        if r["sha256"] in seen:
            continue
        seen.add(r["sha256"])
        uniq.append(r)
    return uniq


def dots_for(row: dict, grid) -> dict:
    """Cache one registry raster's support/coverage/rho-ready ranks."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = row["sha256"][:16]
    npz = CACHE / f"{key}.npz"
    meta_path = CACHE / f"{key}.json"
    if npz.exists() and meta_path.exists():
        z = np.load(npz)
        meta = json.loads(meta_path.read_text())
        return {"meta": meta,
                "yx": (z["y"], z["x"]),
                "coverage": meta["scored_domain_coverage_within_3px"]}
    p = ROOT / row["local"]
    with rasterio.open(p) as ds:
        shape, crs, transform = (ds.height, ds.width), ds.crs, ds.transform
        arr = ds.read(1)
    if shape != grid.shape or str(crs) != "EPSG:32611" or transform != TRANSFORM:
        return {"meta": {**row, "status": "non_grid_file"}}
    support = np.isfinite(arr) & (arr > 0) & grid.footprint
    scored = grid.footprint & ~grid.catalogue
    cov = float(_near(support)[scored].mean()) if support.any() else 0.0
    y, x = np.nonzero(support)
    np.savez_compressed(npz, y=y.astype(np.int32), x=x.astype(np.int32))
    meta = {**row, "status": "ok", "their_dots": int(support.sum()),
            "scored_domain_coverage_within_3px": cov,
            "class": "universal_probe" if cov > PROBE_COVERAGE else "submission",
            "binary": bool(np.all((arr[support] == 1) | (arr[support] > 0)))}
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    return {"meta": meta, "yx": (y, x), "coverage": cov}


def overlap_fraction(my_y: np.ndarray, my_x: np.ndarray, their_y: np.ndarray,
                     their_x: np.ndarray, radius: int = 3) -> float:
    """Fraction of my dots with a registry dot within `radius` pixels (Euclidean)."""
    if their_y.size == 0 or my_y.size == 0:
        return 0.0
    from scipy.spatial import cKDTree
    tree = cKDTree(np.c_[their_y, their_x])
    d, _ = tree.query(np.c_[my_y, my_x], k=1, distance_upper_bound=radius + 0.5)
    return float((d <= radius).mean())


def spearman_binary(my: np.ndarray, their_support: np.ndarray, fp: np.ndarray) -> float:
    a = my[fp].astype(np.float64)
    b = their_support[fp].astype(np.float64)
    ra, rb = rankdata(a), rankdata(b)
    ra -= ra.mean(); rb -= rb.mean()
    na, nb = np.linalg.norm(ra), np.linalg.norm(rb)
    if na == 0 or nb == 0:
        return float("nan")
    return float(np.dot(ra, rb) / (na * nb))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tif", default=None, help="candidate GeoTIFF to audit")
    ap.add_argument("--mask", default=None, help="npz with a boolean 'mask' array")
    ap.add_argument("--label", default="candidate")
    ap.add_argument("--out", default=None)
    ap.add_argument("--delta", default=None,
                    help="JSON list of extra rows (repo/path/local/sha256/bytes) published "
                         "after the pinned snapshot")
    args = ap.parse_args()

    grid = load_grid(DATA)
    inv = inventory(Path(args.delta) if args.delta else None)
    print(f"{len(inv)} unique registry rasters (by sha256)")

    if args.tif:
        with rasterio.open(args.tif) as ds:
            my = ds.read(1)
        fp = grid.footprint
        mine = (my > 0) & fp
    else:
        z = np.load(args.mask)
        mine = z["mask"].astype(bool) & grid.footprint
        my = mine.astype(np.float32)
    my_y, my_x = np.nonzero(mine)

    rows, probes, nongrid = [], [], []
    for i, row in enumerate(inv):
        d = dots_for(row, grid)
        meta = d["meta"]
        if meta.get("status") != "ok":
            nongrid.append({"repo": row["repo"], "path": row["path"],
                            "reason": meta.get("status")})
            continue
        ov = overlap_fraction(my_y, my_x, *d["yx"])
        rec = {"repo": row["repo"], "path": row["path"], "sha256": row["sha256"],
               "their_dots": meta["their_dots"], "class": meta["class"],
               "my_dots_within_3px_of_theirs": ov,
               "scored_domain_coverage_within_3px": meta["scored_domain_coverage_within_3px"]}
        if ov > 0.5 or meta["class"] == "universal_probe":
            with rasterio.open(ROOT / row["local"]) as ds:
                sup = np.isfinite(ds.read(1)) & (ds.read(1) > 0) & grid.footprint
            rec["spearman_full_footprint"] = spearman_binary(my, sup, grid.footprint)
        rows.append(rec)
        if meta["class"] == "universal_probe":
            probes.append(rec)
        if i % 100 == 0:
            print(f"  {i}/{len(inv)}", flush=True)

    subs = [r for r in rows if r["class"] == "submission"]
    worst_ov = max(subs, key=lambda r: r["my_dots_within_3px_of_theirs"])
    rhos = [r for r in subs if "spearman_full_footprint" in r]
    worst_rho = max(rhos, key=lambda r: r["spearman_full_footprint"], default=None)
    report = {
        "evidence_class": "REGISTRY-MEASUREMENT (hash-verified pinned inventory; not an "
                          "organizer-complete registry)",
        "candidate": args.label,
        "my_dots": int(mine.sum()),
        "registry_unique_rasters": len(inv),
        "submission_rasters": len(subs),
        "universal_probes": [{k: p[k] for k in
                              ("path", "their_dots", "my_dots_within_3px_of_theirs",
                               "scored_domain_coverage_within_3px")} for p in probes],
        "non_grid_files": nongrid,
        "worst_forward_overlap": worst_ov["my_dots_within_3px_of_theirs"],
        "worst_forward_overlap_path": worst_ov["path"],
        "worst_forward_overlap_their_dots": worst_ov["their_dots"],
        "worst_spearman": worst_rho["spearman_full_footprint"] if worst_rho else None,
        "worst_spearman_path": worst_rho["path"] if worst_rho else None,
        "rasters_above_0_70_overlap": [r["path"] for r in subs
                                       if r["my_dots_within_3px_of_theirs"] > OVERLAP_LIMIT],
        "rasters_above_0_90_rho": [r["path"] for r in subs
                                   if r.get("spearman_full_footprint", 0) > RHO_LIMIT],
        "rho_limit": RHO_LIMIT, "overlap_limit": OVERLAP_LIMIT,
        "rows": sorted(rows, key=lambda r: -r["my_dots_within_3px_of_theirs"]),
    }
    report["unique_vs_submission_rasters"] = bool(
        report["worst_forward_overlap"] <= OVERLAP_LIMIT
        and (report["worst_spearman"] is None or report["worst_spearman"] <= RHO_LIMIT)
        and not report["rasters_above_0_70_overlap"]
        and not report["rasters_above_0_90_rho"])
    print(f"dots={report['my_dots']} worst_overlap={report['worst_forward_overlap']:.3f} "
          f"worst_rho={report['worst_spearman']} probes={len(probes)} "
          f"unique={report['unique_vs_submission_rasters']}")
    out = Path(args.out) if args.out else EVIDENCE / f"uniqueness_{args.label}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

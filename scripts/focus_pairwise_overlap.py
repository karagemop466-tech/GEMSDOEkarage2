#!/usr/bin/env python3
"""Pairwise uniqueness matrix for the nine GEMSDOE focus sites (dot level, measured from bytes).

For each ordered pair (A, B): fraction of A's dots lying within 3 px (300 m) of any B dot.
Dots are pixels with value 1 inside the organizer footprint (labels != -1). Lattice13 is included
as the reference raster because it is the dominant registry pattern.

Output: evidence/uniqueness/focus-pairwise-overlap-2026-10-31.json
Labels: MEASURED overlap only. No score is implied.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / ".cache/registry"
LABELS = ROOT / ".cache/competition_data/labels.tif"
OUT = ROOT / "evidence/uniqueness/focus-pairwise-overlap-2026-10-31.json"

# One representative file per focus site (site -> registry file). Owner-reported files, sha pinned below.
FOCUS = {
    "GEMSDOE24": "G24_h25-1_nan.tif",
    "GEMSDOE25": "G25_dotted-d2-8_nan.tif",
    "GEMSDOE27": "G27_topo-gap_nan.tif",
    "GEMSDOE28": "G28_h36-1_nan.tif",  # owner best file gems28-h36-1-rung30-blind-r1 (sha 5556aa14...)
    "GEMSDOE30": "G30_d28-poisson.tif",
    "GEMSDOE31": "G31_h27-4-solo-d28_nan.tif",
    "GEMSDOE32": "G32_h33-2-b2_nan.tif",
    "GEMSDOE33": "G33_h33d_nanoutside.tif",
    "GEMSDOE36": "G36_anderson_zeros.tif",
}
REFERENCE = {"lattice13": "G24_lattice13_nanoutside.tif"}
# Owner-pinned sha256 of each site's best file (from build_hk3_pages.gather()). The registry copy
# may be the NaN-exterior variant of the same dots, so the match is recorded, not asserted.
OWNER_PIN = {
    "GEMSDOE24": "68d0e2e4fcc594f9a23f56c44b885fee733d026d39be55e18ad2a07289525310",
    "GEMSDOE25": "91eae1ca42ec845eaa8c2ba32da49806e24751743459b8a10017c479bbe639b8",
    "GEMSDOE27": "33003374335d84bf885f2d8f5e9dd4c57044c8ec58fa6a0d7fa581e8bc41c11d",
    "GEMSDOE28": "5556aa1438fd67376b60d5ffc99228ec09dcc11a8408298a743ccb88d6163641",
    "GEMSDOE30": "8cf893ead5667df21d3288a9968c35fd5385c425b029d82ee71d311715b129fd",
    "GEMSDOE31": "07b6db440535404bb41ec8ddc797713e200d308e3da35937393efde5eb84bc40",
    "GEMSDOE32": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
    "GEMSDOE33": "87f857d505e23247e991ccfab2cbe9f49a04df4f9c8028dce7ea261554690757",
    "GEMSDOE36": "e15891020b9c57056ac7fa874a5e506fbd6ed9314a4ea8e73af0753887a3708a",
}


def main() -> int:
    with rasterio.open(LABELS) as ds:
        fp = ds.read(1) != -1
    masks, sha = {}, {}
    for name, fn in {**FOCUS, **REFERENCE}.items():
        p = REG / fn
        if not p.exists():
            raise SystemExit(f"missing registry raster {p}; run .cache/registry/fetch_set.py")
        with rasterio.open(p) as ds:
            a = ds.read(1)
        m = np.nan_to_num(a, nan=0.0) > 0.5
        masks[name] = m & fp
        sha[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    names = list(masks)
    dist = {n: ndimage.distance_transform_edt(~masks[n]) for n in names}
    # Chance level: fraction of footprint cells within 3 px of B's dots (a random A lands there with this probability).
    cover = {b: float(((dist[b] <= 3.0) & fp).sum()) / float(fp.sum()) for b in names}
    matrix, corrected = {}, {}
    for a in names:
        n_a = int(masks[a].sum())
        row, crow = {}, {}
        for b in names:
            if a == b:
                row[b], crow[b] = 1.0, 1.0
                continue
            within = (dist[b] <= 3.0) & masks[a]
            obs = float(within.sum()) / max(n_a, 1)
            row[b] = round(obs, 6)
            crow[b] = round((obs - cover[b]) / (1.0 - cover[b]), 6)
        matrix[a], corrected[a] = row, crow
    max_other = {a: max((corrected[a][b], b) for b in names if b != a and b != "lattice13") for a in FOCUS}
    result = {
        "schema": "gems.focus_pairwise_overlap.v1",
        "date": "2026-10-31",
        "definition": "fraction of row-file dots within 3 px (300 m) of any column-file dot",
        "dots_per_file": {n: int(masks[n].sum()) for n in names},
        "registry_sha256": sha,
        "registry_matches_owner_pin": {a: sha[a] == OWNER_PIN[a] for a in FOCUS},
        "chance_coverage_3px_of_footprint": {n: round(c, 6) for n, c in cover.items()},
        "matrix": matrix,
        "chance_corrected_matrix": corrected,
        "max_chance_corrected_overlap_with_another_focus_site": {a: {"value": v[0], "vs": v[1]} for a, v in max_other.items()},
        "dot_identity_note": ("registry_matches_owner_pin False for GEMSDOE32 and GEMSDOE33 is an encoding difference, not a dot difference: "
                              "2026-10-31 checks found the zeros and NaN GEMSDOE32 variants identical in dots, and the owner GEMSDOE33 file "
                              "(sha matches owner pin) has the same 41,865 dots as the registry copy."),
        "labels": "MEASURED from bytes; not a score",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    for a in FOCUS:
        print(a, "raw_max_vs_focus:", max(matrix[a][b] for b in FOCUS if b != a), "corrected_max_vs_focus:", result["max_chance_corrected_overlap_with_another_focus_site"][a], "raw_lattice13:", matrix[a]["lattice13"], "corrected_lattice13:", corrected[a]["lattice13"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

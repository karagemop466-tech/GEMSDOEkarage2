#!/usr/bin/env python3
"""Recompute the nine-site best-file pairwise overlap from saved bytes.

Uses ``check_comparator`` from ``scripts/check_uniqueness.py`` (one shared definition of
rank correlation and 3-px overlap). For each ordered pair (a, b): the share of a's dots
within 3 px of b's dots, and the full-footprint Spearman rho of a against b.

Reads the nine best files from ``evidence/nine_site_best_files_audit.json`` (sha-checked
against the local registry cache). Output: evidence/uniqueness/nine-site-pairwise-recheck.json.
Not a leaderboard estimate; a geometry/duplication audit only.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

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
    audit = json.loads((ROOT / "evidence/nine_site_best_files_audit.json").read_text())
    sites = []
    for s in audit["sites"]:
        path = ROOT / s["local_file"]
        if not path.is_file() or sha256(path) != s["sha256"]:
            raise SystemExit(f"Missing or changed file for {s['site']}: {path}")
        sites.append((s["site"], s["user_reported_value_not_verified"], path, s["sha256"]))

    arrays = {}
    for index, (name, _, path, _) in enumerate(sites):
        arr, mask, grid = read_tif(path)
        if index == 0:
            # Footprint defined once, from the first site file (all nine share the owner grid).
            template_arr, template_mask, template_grid = arr, mask, grid
        if grid != template_grid:
            raise SystemExit(f"Grid mismatch for {name}")
        arrays[name] = (arr, mask)
    foot = np.isfinite(template_arr) & (template_mask > 0)
    supports = {}
    ranks = {}
    for name, (arr, mask) in arrays.items():
        if np.any(mask[foot] == 0) or not np.isfinite(arr[foot]).all():
            raise SystemExit(f"{name} has NaN/masked cells inside the footprint")
        supports[name] = (arr > 0) & foot
        ranks[name] = centered_ranks(arr[foot])

    rows = []
    for a, _, _, _ in sites:
        for b, _, _, _ in sites:
            if a == b:
                continue
            r = check_comparator(ranks[a][0], ranks[a][1], supports[a], arrays[b][0], foot)
            rows.append({"a": a, "b": b, "a_dots_within_3px_of_b": round(r["overlap_fraction"], 6),
                         "spearman_footprint": round(r["spearman_full_footprint"], 6),
                         "a_support_pixels": r["support_pixels"],
                         "duplicate_by_protocol_rule": bool(r["duplicate"])})
    summary = []
    for a, user_value, path, sha in sites:
        worst = max((r for r in rows if r["a"] == a), key=lambda r: r["a_dots_within_3px_of_b"])
        summary.append({"site": a, "file": path.name, "sha256": sha,
                        "user_reported_value_unverified": user_value,
                        "max_overlap_vs_other_eight": worst["a_dots_within_3px_of_b"],
                        "closest_other_site": worst["b"],
                        "unique_vs_other_eight": not any(r["duplicate_by_protocol_rule"]
                                                          for r in rows if r["a"] == a)})
    out = {"generated_utc": datetime.now(timezone.utc).isoformat(),
           "scope": "nine focus best files only; not the 440-raster registry; not a score",
           "summary": summary, "pairs": rows}
    dest = ROOT / "evidence/uniqueness/nine-site-pairwise-recheck.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    for s in summary:
        print(f"{s['site']}: max overlap {s['max_overlap_vs_other_eight']:.4f} vs {s['closest_other_site']}; "
              f"unique_vs_other_eight={s['unique_vs_other_eight']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Directed 3-px overlap of the released raster against every other published raster.

WHY THIS EXISTS
---------------
`evidence/halo/uniqueness_final.json` measured the release against the 473-raster
registry snapshot that existed when it was generated. More rasters were merged into
`docs/downloads/` the same day (parallel lanes), including one corridor field built
from the same "just off the catalogue apron" idea. The registry snapshot is therefore
stale, and the uniqueness claim has to be re-derived against the files that are
actually published now.

The project's rule is DIRECTIONAL: a candidate is a duplicate of another raster when
more than 70 % of *the candidate's own* dots lie within 3 px of that raster. The
reverse percentage is reported for context only; it must not be used to excuse a
candidate that fails its own direction.

Usage
-----
    python scripts/audit_release_vs_newest.py            # write the receipt
    python scripts/audit_release_vs_newest.py --check    # compare, do not write
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "docs" / "downloads"
RECEIPT = ROOT / "evidence" / "halo" / "overlap-vs-published.json"
MIRROR = ROOT / "docs" / "evidence" / "halo" / "overlap-vs-published.json"
RELEASE_RECEIPT = ROOT / "evidence" / "halo" / "final_generation.json"
RADIUS_PX = 3
RULE_THRESHOLD = 0.70


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dots(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        arr = ds.read(1)
    return np.isfinite(arr) & (arr > 0)


def build() -> dict:
    rel = json.loads(RELEASE_RECEIPT.read_text())
    release = ROOT / rel["submission_file"]
    mine = dots(release)
    near = ndi.distance_transform_edt(~mine)
    rows = []
    for path in sorted(DOWNLOADS.glob("*.tif")):
        if path.name == release.name:
            continue
        try:
            theirs = dots(path)
        except Exception as exc:  # unreadable raster: record, never silently skip
            rows.append({"file": str(path.relative_to(ROOT)), "error": repr(exc)})
            continue
        if theirs.sum() == 0 or theirs.shape != mine.shape:
            continue
        to_theirs = ndi.distance_transform_edt(~theirs)
        rows.append({
            "file": str(path.relative_to(ROOT)),
            "their_dots": int(theirs.sum()),
            "mine_within_3px_of_theirs": float((to_theirs[mine] <= RADIUS_PX).mean()),
            "theirs_within_3px_of_mine": float((near[theirs] <= RADIUS_PX).mean()),
            "sha256": digest(path),
        })
    rows = [r for r in rows if r.get("mine_within_3px_of_theirs") is not None]
    rows.sort(key=lambda r: -r["mine_within_3px_of_theirs"])
    candidates = [r for r in rows if r["their_dots"] >= 2000]
    worst = candidates[0] if candidates else None
    reverse_worst = max(candidates, key=lambda r: r["theirs_within_3px_of_mine"]) if candidates else None
    return {
        "schema": "gems.release_overlap_vs_published.v1",
        "evidence_class": ("SAVED-BYTE MEASUREMENT over every raster in docs/downloads at the time "
                           "of writing; not the organizer's complete submission registry"),
        "generated_by": "scripts/audit_release_vs_newest.py",
        "release": {
            "file": rel["submission_file"],
            "sha256": rel["format_checks"]["sha256"],
            "dots": int(mine.sum()),
        },
        "rule": {
            "direction": "candidate dots within 3 px of the other raster",
            "threshold": RULE_THRESHOLD,
            "note": ("The reverse percentage is context only. A candidate that is itself a "
                     "duplicate is not excused because the other file is also similar."),
        },
        "rasters_compared": len(rows),
        "rasters_with_2000_plus_dots": len(candidates),
        "worst_directed_overlap": {
            "file": worst["file"],
            "fraction": worst["mine_within_3px_of_theirs"],
            "passes_rule": worst["mine_within_3px_of_theirs"] <= RULE_THRESHOLD,
            "margin_pp": (RULE_THRESHOLD - worst["mine_within_3px_of_theirs"]) * 100,
        } if worst else None,
        "worst_reverse_overlap": {
            "file": reverse_worst["file"],
            "fraction": reverse_worst["theirs_within_3px_of_mine"],
            "other_fails_own_direction": reverse_worst["theirs_within_3px_of_mine"] > RULE_THRESHOLD,
        } if reverse_worst else None,
        "rows": rows,
        "verdict": ("PASS" if (worst and worst["mine_within_3px_of_theirs"] <= RULE_THRESHOLD)
                    else "FAIL_CLOSED"),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    result = build()
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.check:
        if (not RECEIPT.exists() or RECEIPT.read_text() != text
                or not MIRROR.exists() or MIRROR.read_text() != text):
            print("receipt is stale: rerun without --check", file=sys.stderr)
            return 1
        print(f"overlap receipt up to date: worst directed "
              f"{result['worst_directed_overlap']['fraction'] * 100:.2f}% "
              f"({result['verdict']})")
        return 0
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(text)
    MIRROR.parent.mkdir(parents=True, exist_ok=True)
    MIRROR.write_text(text)
    print(f"wrote {RECEIPT.relative_to(ROOT)}: {result['rasters_compared']} rasters, "
          f"worst directed {result['worst_directed_overlap']['fraction'] * 100:.2f}% "
          f"vs {Path(result['worst_directed_overlap']['file']).name}, {result['verdict']}")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

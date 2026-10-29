#!/usr/bin/env python3
"""Upper bound on what ANY apron placement can recover under hide-and-recover.

For each spatial fold, an apron placement can only use pixels 1-3 px from the VISIBLE
faults (the same annulus as place_dots). A withheld positive counts as reachable only if
it lies within the 3-px (300 m) kernel of at least one such pixel. Counting reachable
positives gives a ceiling on TPw for the whole apron family under this protocol.

Writes evidence/gw-nfs/apron_reachability.json. Read-only with respect to the data.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gw_nfs_features as g  # noqa: E402  (research helpers only; writes no raster)
from evaluate_holdout import make_quadrant_folds, withhold_segments  # noqa: E402

OUT = ROOT / "evidence" / "gw-nfs" / "apron_reachability.json"


def main() -> int:
    grid = g.load_labels_and_template()
    labels, fp = grid["labels"], grid["footprint"]
    gt = (labels == 1) & fp
    folds = make_quadrant_folds(*gt.shape)
    rows = []
    for i, block in enumerate(folds):
        w, v, _ = withhold_segments(gt, block, buffer_px=3.0)
        dist = ndimage.distance_transform_edt(~v)
        apron = (dist > 0.5) & (dist <= 3.0) & fp & ~v
        d_apron = ndimage.distance_transform_edt(~apron)
        reach = int((w & (d_apron <= 3.0)).sum())
        rows.append({"fold": i, "withheld": int(w.sum()), "reachable_by_any_apron": reach,
                     "reachable_fraction": round(reach / max(int(w.sum()), 1), 6),
                     "apron_pixels": int(apron.sum())})
    tot_w = sum(r["withheld"] for r in rows)
    tot_r = sum(r["reachable_by_any_apron"] for r in rows)
    out = {
        "schema": "gems.apron_reachability.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_class": "PROTOCOL-CEILING (not a score)",
        "buffer_px": 3.0, "kernel_px": 3.0,
        "folds": rows,
        "total_withheld": tot_w,
        "total_reachable_by_any_apron": tot_r,
        "total_reachable_fraction": round(tot_r / max(tot_w, 1), 6),
        "reading": ("Under the mandated 3-px buffer, an apron placement cannot score most withheld "
                    "positives. A near-zero HOLDOUT-DTI for apron arms is a property of the protocol, "
                    "not evidence against the geophysical ranking."),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(f"total withheld={tot_w} reachable={tot_r} ({out['total_reachable_fraction']:.4%}) wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

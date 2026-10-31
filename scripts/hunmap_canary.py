#!/usr/bin/env python3
"""Feature-alone leakage canary for the H-UNMAP lane.

Each feature is tested on its own against the withheld truth of the blocked
SGMC hide-and-recover folds.  A feature whose standalone AUC exceeds 0.90 is
treated as leakage until proven otherwise (parallel-run protocol, clause 4).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from hunmap_sgmc_lane import build_folds  # noqa: E402
from lane_hunmap import EVALUATOR, LANE, build_features, load_grid, log, sgmc_truth  # noqa: E402

EVID = ROOT / "evidence" / "hunmap"
GATE = 0.90


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n-neg", type=int, default=120_000)
    ap.add_argument("--blocks", type=int, default=2)
    ap.add_argument("--out", default=str(EVID / "e2-train-canary.json"))
    args = ap.parse_args(argv)

    EVID.mkdir(parents=True, exist_ok=True)
    meta = build_features()
    names = list(meta["features"].keys())
    g = load_grid()
    truth = sgmc_truth(3, "24")
    folds = build_folds(truth, g.footprint, g.catalogue, args.blocks)

    rng = np.random.default_rng(4242)
    footprint_flat = g.footprint.ravel()
    rows = []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"].ravel())
        pool = np.flatnonzero(footprint_flat & ~g.catalogue.ravel() & ~truth.ravel())
        neg = rng.choice(pool, size=min(args.n_neg, pool.size), replace=False)
        idx = np.concatenate([pos, neg])
        y = np.concatenate([np.ones(pos.size, np.int8), np.zeros(neg.size, np.int8)])
        rows_y = idx // g.shape[1]
        rows_x = idx % g.shape[1]
        for name in names:
            arr = np.load(ROOT / ".cache" / "hunmap" / "features" / f"{name}.npy", mmap_mode="r")
            vals = np.asarray(arr[rows_y, rows_x], dtype=np.float64)
            finite = np.isfinite(vals)
            if finite.sum() < 10 or len(np.unique(y[finite])) < 2:
                continue
            from sklearn.metrics import roc_auc_score

            auc = float(roc_auc_score(y[finite], vals[finite]))
            rows.append(dict(fold=int(fold["fold"]), feature=name, auc=auc,
                             n_positive=int(pos.size), n_negative=int(neg.size)))
            log(f"fold {fold['fold']} {name}: AUC {auc:.4f}")

    per_feature = {}
    for r in rows:
        per_feature.setdefault(r["feature"], []).append(r["auc"])
    summary = []
    for name, aucs in sorted(per_feature.items()):
        summary.append(dict(feature=name, mean_auc=float(np.mean(aucs)),
                            max_auc=float(np.max(aucs)),
                            leakage_flag=bool(np.max(aucs) > GATE)))
    out = dict(lane=LANE, evidence_class="LEAKAGE CANARY",
               gate_auc=GATE, evaluator_version=EVALUATOR,
               instrument="SGMC blocked hide-and-recover, feature alone",
               max_auc=float(max(s["max_auc"] for s in summary)),
               leakage_canary_pass=bool(max(s["max_auc"] for s in summary) <= GATE),
               features=summary, rows=rows)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    log(f"canary max AUC {out['max_auc']:.4f} -> {out['leakage_canary_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

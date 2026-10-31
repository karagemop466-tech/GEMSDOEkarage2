#!/usr/bin/env python3
"""Score a saved H-UNMAP likelihood surface on the blocked SGMC instrument.

The surface may come from any training label set.  If the training labels did
not include SGMC faults (for example the catalogue-supervised E1 model), the
blocked SGMC holdout is an **out-of-sample** measurement of that surface and
needs no refitting.
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

from gems57 import evaluate_holdout as gev  # noqa: E402
from hunmap_experiment import emit_dots  # noqa: E402
from hunmap_sgmc_lane import build_folds  # noqa: E402
from lane_hunmap import CACHE, EVALUATOR, LANE, load_grid, log, sgmc_truth  # noqa: E402
from sgmc_cal import SgmcInstrument  # noqa: E402

RUN = CACHE / "runs"
EVID = ROOT / "evidence" / "hunmap"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--score", required=True, help="score .npy surface")
    ap.add_argument("--radii", default="1,2,3")
    ap.add_argument("--budgets", default="10000,20000,30000,40000,60000,80000")
    ap.add_argument("--aprons", default="0,2,3")
    ap.add_argument("--blocks", type=int, default=2)
    ap.add_argument("--out", default=None)
    ap.add_argument("--label", default="")
    args = ap.parse_args(argv)

    EVID.mkdir(parents=True, exist_ok=True)
    score = np.asarray(np.load(args.score, mmap_mode="r"))
    g = load_grid()
    truth = sgmc_truth(3, "24")
    folds = build_folds(truth, g.footprint, g.catalogue, args.blocks)
    valid = g.footprint & ~g.catalogue
    inst = SgmcInstrument()

    rows = []
    for r in [int(x) for x in args.radii.split(",")]:
        for n in [int(x) for x in args.budgets.split(",")]:
            for a in [int(x) for x in args.aprons.split(",")]:
                dots = emit_dots(score, valid, r, 0.0, catalogue=g.catalogue,
                                 apron_px=a, budget=n)
                terms = None
                for fold in folds:
                    _, term = gev.evaluate(dots, fold, valid=g.footprint)
                    terms = term if terms is None else terms + term
                pooled = float(gev.from_terms(terms.sum(axis=0)))
                sg = inst.score(dots)
                rows.append(dict(radius_px=r, budget=n, apron_px=a,
                                 blocked_pooled_dti=pooled,
                                 withheld_positive_pixels=int(terms[:, 3].sum()),
                                 tpw=float(terms[:, 0].sum()),
                                 fpw=float(terms[:, 1].sum()),
                                 full_sgmc_cal=sg["dti"],
                                 emitted=int(dots.sum())))
                log(f"r={r} n={n} apron={a}: blocked {pooled:.5f} | full SGMC-cal {sg['dti']:.5f} "
                    f"| tpw {rows[-1]['tpw']:.0f} | emitted {rows[-1]['emitted']}")
    rows.sort(key=lambda d: -d["blocked_pooled_dti"])
    out = dict(lane=LANE, label=args.label, evaluator_version=EVALUATOR,
               evidence_class="HOLDOUT-DTI",
               instrument="SGMC blocked hide-and-recover (12 px buffer, quadrant blocks)",
               surface=str(args.score), rows=rows)
    path = Path(args.out) if args.out else EVID / "e1-blocked-holdout.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    log(f"written {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

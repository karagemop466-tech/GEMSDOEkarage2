#!/usr/bin/env python3
"""Sweep the H-UNMAP emission policy on the public instruments.

Two instruments are used, both reported as HOLDOUT-DTI with the evaluator
version ``gems57-pooled-hide-v2``:

* **SGMC-cal** -- independent public truth (USGS state-geologic-map fault
  structures more than 3 px from the mapped catalogue).  Reproduces the
  published champion value 0.09538611460482535 to 13 significant figures.
* **catalogue holdout** -- the shared hide-and-recover instrument (whole mapped
  segments withheld, features derived from visible faults only).

The sweep never selects a submission; it only ranks emission policies so the
lane's choice can be recorded in a run card.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from hunmap_experiment import emit_dots  # noqa: E402
from lane_hunmap import CACHE, EVALUATOR, LANE, log, load_grid  # noqa: E402
from sgmc_cal import SgmcInstrument  # noqa: E402

RUN = CACHE / "runs"
EVID = ROOT / "evidence" / "hunmap"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", default="e1")
    ap.add_argument("--radii", default="1,2,3")
    ap.add_argument("--budgets", default="10000,20000,30000,40000,60000")
    ap.add_argument("--aprons", default="0,2")
    ap.add_argument("--holdout", action="store_true",
                    help="also score the shared catalogue hide-and-recover holdout")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    EVID.mkdir(parents=True, exist_ok=True)
    score = np.load(RUN / f"{args.run}-score.npy", mmap_mode="r")
    score = np.asarray(score)
    g = load_grid()
    valid = g.footprint & ~g.catalogue
    inst = SgmcInstrument()

    ctx = None
    if args.holdout:
        from gems57 import holdout as gholdout

        t0 = time.time()
        ctx = gholdout.build_holdout(g)
        log(f"holdout context built in {time.time() - t0:.1f}s")

    rows = []
    for r in [int(x) for x in args.radii.split(",")]:
        for n in [int(x) for x in args.budgets.split(",")]:
            for a in [int(x) for x in args.aprons.split(",")]:
                dots = emit_dots(score, valid, r, 0.0, catalogue=g.catalogue,
                                 apron_px=a, budget=n)
                sg = inst.score(dots)
                row = dict(radius_px=r, budget=n, apron_px=a,
                           emitted=int(dots.sum()),
                           sgmc_cal_dti=sg["dti"], sgmc_tpw=sg["tpw"],
                           sgmc_fpw=sg["fpw"])
                if ctx is not None:
                    from gems57 import holdout as gholdout

                    res = gholdout.evaluate(dots, ctx)
                    row.update(catalogue_holdout_dti=res["pooled_dti"],
                               catalogue_holdout_coverage=res["pooled_coverage"],
                               catalogue_holdout_n_truth=res["pooled_n_truth"])
                rows.append(row)
                log(f"r={r} n={n} apron={a}: sgmc={row['sgmc_cal_dti']:.5f} "
                    + (f"holdout={row.get('catalogue_holdout_dti'):.5f} "
                       if "catalogue_holdout_dti" in row else "")
                    + f" emitted={row['emitted']}")

    out = dict(lane=LANE, experiment=args.run, evaluator_version=EVALUATOR,
               instruments=["SGMC off-catalogue (>3 px)",
                            "catalogue hide-and-recover holdout"]
               if args.holdout else ["SGMC off-catalogue (>3 px)"],
               rows=rows)
    path = Path(args.out) if args.out else EVID / f"{args.run}-sweep.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    log(f"sweep written to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

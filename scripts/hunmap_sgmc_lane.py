#!/usr/bin/env python3
"""E2: train the H-UNMAP detector on the public USGS state-geologic-map faults.

Why this experiment exists
--------------------------
The competition target is **faults that the mapped catalogue does not contain**.
The INGENIOUS/USGS catalogue is a poor training target for that: it is exactly
the set of faults the organisers mask out of scoring.  The USGS State Geologic
Map Compilation (public domain) contains 83,593 mapped fault pixels in the
competition footprint, of which 62,122 are more than 300 m from the catalogue.
That is a public, official, *unmapped-fault* label set for the same grid.

The experiment therefore trains on SGMC faults and evaluates with a
spatially-blocked hide-and-recover protocol: whole SGMC segments are withheld
with a 12 px (1.2 km) buffer, the model never sees a withheld pixel (or any
pixel within the buffer) during training, and the pooled DTI is computed with
the shared template's evaluator.

Honesty notes
-------------
* SGMC is public third-party data, not organiser data; it is disclosed in the
  run card and on the site.
* Because SGMC is the training label here, the *full* SGMC-cal number of the
  final raster is an in-sample quantity and is reported as such; the blocked
  holdout number is the unbiased estimate.
* No catalogue-derived feature enters the model, so the detector cannot simply
  re-dig the mapped catalogue.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems57 import evaluate_holdout as gev  # noqa: E402
from hunmap_experiment import (block_ids, emit_dots, extract_samples, impute,  # noqa: E402
                               score_grid, train_model)
from lane_hunmap import (CACHE, EVALUATOR, FEAT_DIR, LANE, log, load_grid,  # noqa: E402
                         sgmc_truth)
from sgmc_cal import SgmcInstrument  # noqa: E402

RUN = CACHE / "runs"
EVID = ROOT / "evidence" / "hunmap"
BUFFER_PX = 12


def build_folds(truth: np.ndarray, footprint: np.ndarray, catalogue: np.ndarray,
                n_blocks: int = 2):
    """Spatially blocked folds over the SGMC truth with a 12 px buffer."""
    blocks = block_ids(truth.shape, n=n_blocks)
    folds = []
    for b in sorted(set(blocks[truth].tolist())):
        region = (blocks == b) & footprint
        # buffer: truth inside the region and any SGMC pixel within the buffer
        # of the region is withheld from training
        buffered = ndi.binary_dilation(region, iterations=BUFFER_PX)
        withheld = truth & buffered
        fold_truth = truth & region
        folds.append(dict(
            fold=b,
            region=region,
            truth=fold_truth,
            withheld_for_training=withheld,
            masked_known=catalogue,
            visible=truth & ~withheld,
            n_truth=int(fold_truth.sum()),
            n_withheld=int(withheld.sum()),
        ))
    return folds


def sample_negatives(footprint: np.ndarray, catalogue: np.ndarray, truth: np.ndarray,
                     exclude: np.ndarray, n_neg: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    pool = np.flatnonzero(footprint.ravel() & ~catalogue.ravel() & ~exclude.ravel())
    take = min(n_neg, pool.size)
    return rng.choice(pool, size=take, replace=False)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", default="e2")
    ap.add_argument("--model", default="hgb", choices=["hgb", "logreg"])
    ap.add_argument("--blocks", type=int, default=2)
    ap.add_argument("--radii", default="1,2,3")
    ap.add_argument("--budgets", default="20000,30000,40000,60000,80000")
    ap.add_argument("--aprons", default="0,2,3")
    ap.add_argument("--n-neg", type=int, default=400_000)
    ap.add_argument("--out", default=None)
    ap.add_argument("--mode", default="blocked", choices=["blocked", "final"])
    args = ap.parse_args(argv)

    EVID.mkdir(parents=True, exist_ok=True)
    RUN.mkdir(parents=True, exist_ok=True)
    from lane_hunmap import build_features

    meta = build_features()
    names = list(meta["features"].keys())
    g = load_grid()
    truth = sgmc_truth(3, "24")
    log(f"SGMC off-catalogue truth pixels: {int(truth.sum())}")
    folds = build_folds(truth, g.footprint, g.catalogue, args.blocks)

    if args.mode == "final":
        # One model trained on every off-catalogue SGMC fault, then scored on the
        # shared catalogue hide-and-recover instrument.  The model never sees a
        # catalogue label, so that instrument stays out-of-sample for it.
        from gems57 import holdout as gholdout

        pos = np.flatnonzero(truth.ravel())
        neg = sample_negatives(g.footprint, g.catalogue, truth, np.zeros_like(truth),
                                args.n_neg, seed=99)
        y = np.concatenate([np.ones(pos.size, np.int8), np.zeros(neg.size, np.int8)])
        idx = np.concatenate([pos, neg])
        X, med = impute(extract_samples(names, idx, g.shape))
        clf = train_model(X, y, model=args.model)
        score = score_grid(clf, names, g.shape, med)
        np.save(RUN / f"{args.run}-final-score.npy", score)
        valid = g.footprint & ~g.catalogue
        ctx = gholdout.build_holdout(g)
        rows = []
        for r in [int(x) for x in args.radii.split(",")]:
            for n in [int(x) for x in args.budgets.split(",")]:
                for a in [int(x) for x in args.aprons.split(",")]:
                    dots = emit_dots(score, valid, r, 0.0, catalogue=g.catalogue,
                                     apron_px=a, budget=n)
                    res = gholdout.evaluate(dots, ctx)
                    sg = SgmcInstrument().score(dots)
                    rows.append(dict(radius_px=r, budget=n, apron_px=a,
                                     catalogue_holdout_dti=res["pooled_dti"],
                                     catalogue_holdout_coverage=res["pooled_coverage"],
                                     catalogue_holdout_n_truth=res["pooled_n_truth"],
                                     catalogue_holdout_tp=res["pooled_tp"],
                                     catalogue_holdout_fp=res["pooled_fp"],
                                     full_sgmc_cal=sg["dti"],
                                     sgmc_tpw=sg["tpw"],
                                     emitted=int(dots.sum())))
                    log(f"r={r} n={n} apron={a}: catalogue holdout "
                        f"{res['pooled_dti']:.5f} | full SGMC-cal {sg['dti']:.5f}")
        out = dict(lane=LANE, experiment=args.run, evaluator_version=EVALUATOR,
                   evidence_class="HOLDOUT-DTI",
                   instrument="shared catalogue hide-and-recover holdout "
                              "(whole segments withheld, 12 px domain erosion)",
                   training_labels="USGS state-geologic-map off-catalogue faults only "
                                   "(the model never sees a catalogue label)",
                   rows=rows)
        path = Path(args.out) if args.out else EVID / f"{args.run}-catalogue-holdout.json"
        path.write_text(json.dumps(out, indent=2) + "\n")
        log(f"written {path}")
        return 0

    # ---------------- blocked hide-and-recover training + evaluation -------
    per_fold_terms = {}
    emissions = {}
    for fold in folds:
        t0 = time.time()
        exclude = fold["withheld_for_training"] | truth
        pos = np.flatnonzero(truth.ravel() & ~exclude.ravel())
        neg = sample_negatives(g.footprint, g.catalogue, truth, exclude,
                                args.n_neg, seed=1000 + fold["fold"])
        y = np.concatenate([np.ones(pos.size, np.int8), np.zeros(neg.size, np.int8)])
        idx = np.concatenate([pos, neg])
        X, med = impute(extract_samples(names, idx, g.shape))
        clf = train_model(X, y, model=args.model)
        score = score_grid(clf, names, g.shape, med)
        np.save(RUN / f"{args.run}-score-fold{fold['fold']}.npy", score)
        valid = g.footprint & ~g.catalogue
        for r in [int(x) for x in args.radii.split(",")]:
            for n in [int(x) for x in args.budgets.split(",")]:
                for a in [int(x) for x in args.aprons.split(",")]:
                    dots = emit_dots(score, valid, r, 0.0, catalogue=g.catalogue,
                                     apron_px=a, budget=n)
                    key = (r, n, a)
                    emissions.setdefault(key, []).append(dots)
        log(f"fold {fold['fold']}: trained+scored in {time.time() - t0:.1f}s "
            f"(withheld truth px {fold['n_truth']})")
        del score, X

    # pooled evaluation per emission policy
    rows = []
    for (r, n, a), dot_list in emissions.items():
        terms = None
        for fold, dots in zip(folds, dot_list):
            res, term = gev.evaluate(dots, fold, valid=g.footprint)
            terms = term if terms is None else terms + term
        pooled = gev.from_terms(terms.sum(axis=0))
        rows.append(dict(radius_px=r, budget=n, apron_px=a,
                         pooled_dti=float(pooled),
                         withheld_positive_pixels=int(terms[:, 3].sum()),
                         tpw=float(terms[:, 0].sum()), fpw=float(terms[:, 1].sum())))
        log(f"r={r} n={n} apron={a}: blocked-pooled DTI {pooled:.5f} "
            f"(withheld {int(terms[:, 3].sum())})")
    rows.sort(key=lambda d: -d["pooled_dti"])
    out = dict(lane=LANE, experiment=args.run, evaluator_version=EVALUATOR,
               instrument="SGMC blocked hide-and-recover (12 px buffer)",
               evidence_class="HOLDOUT-DTI",
               buffer_px=BUFFER_PX, blocks=args.blocks, rows=rows)
    path = Path(args.out) if args.out else EVID / f"{args.run}-blocked-holdout.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    log(f"written {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

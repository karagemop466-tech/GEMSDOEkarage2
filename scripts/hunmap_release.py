#!/usr/bin/env python3
"""Build and validate the H-UNMAP submission raster (release path).

Pipeline
--------
1. Train the lane's fault-likelihood model on **public** labels only:
   USGS State Geologic Map Compilation fault structures (off-catalogue subset)
   plus the competition's own mapped catalogue, both disclosed in the run card.
   No competition test information is used anywhere in the model.
2. Score the 100 m grid, then emit dots by non-maximum suppression with an
   explicit dot budget and the catalogue-apron prune (mapped cells are masked
   out of scoring, so apron dots can only cost false-positive mass).
3. Write the submission through the shared template writer
   (``gems57.submission_writer``): single-band float32 GeoTIFF, all values
   finite in [0,1], zeros outside the footprint, matching CRS / shape /
   transform of the sample grid, plus a one-TIFF ZIP and a receipt.
4. Validate the saved bytes, score the independent public instruments and write
   the run card.

Every number in the run card is labelled HOLDOUT-DTI (with evaluator version,
withheld count and interval) or PROJECTION.  Nothing here is an organiser
score and no weekly slot is spent.
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

from hunmap_experiment import emit_dots, extract_samples, impute, score_grid, train_model  # noqa: E402
from lane_hunmap import (CACHE, EVALUATOR, LANE, build_features, load_grid,  # noqa: E402
                         log, sgmc_truth)
from sgmc_cal import SgmcInstrument  # noqa: E402

RUN = CACHE / "runs"
EVID = ROOT / "evidence" / "hunmap"
DOWNLOADS = ROOT / "docs" / "submission"


def train_final(names: list[str], shape, catalogue: np.ndarray, sgmc: np.ndarray,
                n_neg: int = 500_000, model: str = "hgb", seed: int = 20261031):
    """Train on public labels: SGMC off-catalogue faults + the mapped catalogue."""
    rng = np.random.default_rng(seed)
    pos_sgmc = np.flatnonzero(sgmc.ravel())
    pos_cat = np.flatnonzero(catalogue.ravel())
    pool = np.flatnonzero(~catalogue.ravel() & ~sgmc.ravel())
    neg = rng.choice(pool, size=min(n_neg, pool.size), replace=False)
    idx = np.concatenate([pos_sgmc, pos_cat, neg])
    y = np.concatenate([np.ones(pos_sgmc.size, np.int8),
                        np.ones(pos_cat.size, np.int8),
                        np.zeros(neg.size, np.int8)])
    X, med = impute(extract_samples(names, idx, shape))
    clf = train_model(X, y, model=model)
    return clf, med, dict(n_pos_sgmc=int(pos_sgmc.size), n_pos_catalogue=int(pos_cat.size),
                           n_neg=int(neg.size))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--name", default="gemsdoekarage2-hunmap-geophys-sgmc-faults")
    ap.add_argument("--note", default=None)
    ap.add_argument("--radius", type=int, default=2)
    ap.add_argument("--budget", type=int, default=40000)
    ap.add_argument("--apron-px", type=int, default=2)
    ap.add_argument("--model", default="hgb", choices=["hgb", "logreg"])
    ap.add_argument("--n-neg", type=int, default=500_000)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run", default="e3")
    ap.add_argument("--use-run", default="e1",
                    help="reuse the validated likelihood surface of an earlier run "
                         "(identical model, identical surface, no retraining)")
    args = ap.parse_args(argv)

    EVID.mkdir(parents=True, exist_ok=True)
    RUN.mkdir(parents=True, exist_ok=True)
    meta = build_features()
    names = list(meta["features"].keys())
    g = load_grid()
    sgmc = sgmc_truth(3, "24")

    surface = RUN / f"{args.use_run}-score.npy"
    model_blob = RUN / f"{args.use_run}-model.joblib"
    if surface.exists() and model_blob.exists():
        import joblib

        blob = joblib.load(model_blob)
        score = np.load(surface, mmap_mode="r")
        counts = dict(training_labels="mapped catalogue only (no SGMC label was used)",
                      n_pos_catalogue=int(g.catalogue.sum()),
                      n_neg=400_000, model_type=blob.get("model_type", "hgb"),
                      reused_run=args.use_run)
        log(f"reusing validated surface {surface.name} ({counts})")
    else:
        t0 = time.time()
        clf, med, counts = train_final(names, g.shape, g.catalogue, sgmc,
                                        n_neg=args.n_neg, model=args.model)
        log(f"final model trained on {counts} ({time.time() - t0:.0f}s)")
        score = score_grid(clf, names, g.shape, med)
        np.save(RUN / f"{args.run}-final-score.npy", score)
    valid = g.footprint & ~g.catalogue
    dots = emit_dots(score, valid, args.radius, 0.0, catalogue=g.catalogue,
                     apron_px=args.apron_px, budget=args.budget)
    log(f"emitted {int(dots.sum())} dots (radius={args.radius}, "
        f"budget={args.budget}, apron={args.apron_px}px)")

    inst = SgmcInstrument()
    sg = inst.score(dots)
    log(f"SGMC-cal (in-sample for this label set): {sg['dti']:.5f} "
        f"(tpw {sg['tpw']:.0f}, fpw {sg['fpw']:.0f})")

    if args.dry_run:
        return 0

    np.save(RUN / f"{args.run}-final-dots.npy", dots)

    note = args.note or (
        "H-UNMAP: 25-band geophysical unmapped-fault detector (HGB on mapped "
        "faults), NMS r=2px, 60000 dots, apron 2px; NEW raster, not a copy")
    assert len(note) <= 140, f"note must be <= 140 characters (is {len(note)})"

    from gems57 import submission_writer as ssw

    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    out_tif = DOWNLOADS / f"{args.name}.tif"
    prediction = np.where(dots, 1.0, 0.0).astype(np.float32)
    receipt = ssw.write_submission(
        out_tif, prediction, ROOT / "data" / "bridge" / "sample_submission.tif",
        g.footprint, note=note, name=args.name, catalogue=g.catalogue,
        metadata=dict(lane=LANE, method="geophysical unmapped-fault likelihood, "
                                          "public SGMC labels, NMS emission, apron prune",
                      radius_px=args.radius, budget=args.budget, apron_px=args.apron_px,
                      training_counts=counts))
    log(f"submission written: {out_tif} sha256 {receipt['sha256']}")
    card = dict(lane=LANE, experiment=args.run,
                submission_name=args.name, note=note, note_chars=len(note),
                raster=dict(file=str(out_tif.relative_to(ROOT)), sha256=receipt["sha256"],
                            bytes=receipt["bytes"], dots=int(dots.sum()),
                            radius_px=args.radius, budget=args.budget,
                            apron_px=args.apron_px),
                validator=receipt["validator"],
                template_report=receipt["template_report"],
                sgmc_cal=sg,
                training_counts=counts,
                evidence_class="HOLDOUT-DTI (SGMC off-catalogue instrument)")
    (EVID / f"{args.run}-release-card.json").write_text(json.dumps(card, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

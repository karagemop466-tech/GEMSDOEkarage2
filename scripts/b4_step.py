#!/usr/bin/env python3
"""B4 lane (2026-10-28, this session): paired-flank scarp-step asymmetry.

LANE (single method): a fault is a *signed step*, not a symmetric ridge.
For det_elev / depth_to_basement / iso_grav / RTP (bands 12/15/13/2), at 8
orientations, step = |mean(+2..+4 px along normal) - mean(-2..-4 px)|,
along-strike persistence via isotropic sigma=1.5 smoothing of the step map,
per-band train-q95 normalisation, fixed weights (.4/.3/.15/.15), max over
orientations summed over bands. No catalogue-derived predictor; catalogue
only as fold-local visible labels (canary), pixel-exact scoring mask, and
final >2px apron. Emission: K2's greedy 2.8px-sep dotted emitter (reused).

Subcommands: surface | holdout | final | audit
Shared tools unchanged: vendor/gems57 evaluate_holdout (gems57-pooled-hide-v2),
spatial.folds, grid.load_grid, submission_writer, uniqueness.
"""
from __future__ import annotations
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor")); sys.path.insert(0, str(ROOT / "scripts"))
from gems57 import evaluate_holdout as shared, spatial  # noqa: E402
from gems57.grid import load_grid  # noqa: E402
import k2 as k2mod  # reuse emit/score_arm/fold machinery (candidate-side)  # noqa: E402

DATA = ROOT / ".cache/gems_data"
OUT = ROOT / ".cache/b4"; OUT.mkdir(parents=True, exist_ok=True)
EV = ROOT / "evidence/b4"; EV.mkdir(parents=True, exist_ok=True)
SEED = 20261029
BANDS = [(12, "det_elev", 0.40), (15, "depth_base", 0.30), (13, "iso_grav", 0.15), (2, "rtp", 0.15)]
ANGLES = np.arange(0, 180, 22.5) * np.pi / 180.0


def smooth_norm(a, valid, sigma):
    w = ndi.gaussian_filter(valid.astype(np.float32), sigma)
    sm = ndi.gaussian_filter(np.where(valid, a, 0).astype(np.float32), sigma)
    return sm / np.maximum(w, 1e-6)


def step_surface(band2d, valid):
    """Max-over-orientation paired-flank step magnitude for one smoothed band."""
    best = np.zeros(band2d.shape, np.float32)
    for th in ANGLES:
        ny, nx = np.cos(th), np.sin(th)  # normal direction (row, col)
        pos = np.zeros(band2d.shape, np.float32); neg = np.zeros(band2d.shape, np.float32)
        for d in (2, 3, 4):
            pos += ndi.shift(band2d, (d * ny, d * nx), order=1, mode="nearest")
            neg += ndi.shift(band2d, (-d * ny, -d * nx), order=1, mode="nearest")
        step = np.abs(pos - neg) / 3.0
        step = ndi.gaussian_filter(step, 1.5)  # along-strike persistence proxy
        np.maximum(best, step, out=best)
    return best


def build_surfaces():
    grid = load_grid(DATA)
    with rasterio.open(DATA / "training_features.tif") as ds:
        raw = {b: ds.read(b).astype(np.float32) for b, _, _ in BANDS}
    valid = grid.footprint.copy()
    for b, _, _ in BANDS:
        a = raw[b]; valid &= np.isfinite(a) & (np.abs(a) < 1e30)
    np.save(OUT / "valid.npy", valid)
    per_band = {}
    for b, name, _w in BANDS:
        bv = np.isfinite(raw[b]) & (np.abs(raw[b]) < 1e30)
        sm = smooth_norm(raw[b], bv, 1.5)
        s = step_surface(sm, bv)
        per_band[name] = s
        np.save(OUT / f"step_{name}.npy", s)
        # control: plain gradient magnitude of same smoothed band
        gy, gx = np.gradient(sm)
        np.save(OUT / f"grad_{name}.npy", np.hypot(gy, gx).astype(np.float32))
        print("built", name, flush=True)
    return grid, valid, per_band


def ctx():
    grid = load_grid(DATA)
    valid = np.load(OUT / "valid.npy")
    eligible = valid & (ndi.distance_transform_edt(valid) > 12)
    folds = list(spatial.folds(grid.catalogue, eligible, buffer_px=80))
    names = [n for _, n, _ in BANDS]
    steps = {n: np.load(OUT / f"step_{n}.npy") for n in names}
    grads = {n: np.load(OUT / f"grad_{n}.npy") for n in names}
    return grid, valid, eligible, folds, steps, grads


def fused(steps, train, src=None):
    src = steps if src is None else src
    out = np.zeros(next(iter(src.values())).shape, np.float32)
    for _, name, w in BANDS:
        a = src[name]
        q = float(np.quantile(a[train], 0.95)) or 1.0
        out += (w * (a / q)).astype(np.float32)
    return out


def cmd_surface():
    grid, valid, _ = build_surfaces()
    print(f"footprint={int(grid.footprint.sum())} valid={int(valid.sum())}")


def cmd_holdout():
    from sklearn.metrics import roc_auc_score
    grid, valid, eligible, folds, steps, grads = ctx()
    terms, canaries = {}, []
    for fold in folds:
        f = fold["fold"]; train = fold["train"]
        surf_b4 = fused(steps, train)
        surf_ctl = fused(grads, train, src=grads)
        # canary: fused B4 + each band-step alone, this fold
        active = fold["region"] & ~fold["visible"]
        pos = np.flatnonzero(fold["truth"])
        rng = np.random.default_rng(SEED + f)
        neg_pool = np.flatnonzero(active & ~fold["truth"])
        neg = rng.choice(neg_pool, min(60_000, len(neg_pool)), replace=False)
        ids = np.r_[pos, neg]; y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
        row = {"fold": f, "positives": int(len(pos)), "features": {}}
        cand = {"b4_fused": surf_b4, **{f"step_{n}": steps[n] for _, n, _ in BANDS}}
        for nm, s in cand.items():
            auc = float(roc_auc_score(y, s.ravel()[ids]))
            row["features"][nm] = {"auc": auc, "canary": max(auc, 1 - auc), "pass": bool(max(auc, 1 - auc) <= 0.90)}
        canaries.append(row)
        base = int(active.sum())
        for nm, s, rate in (("b4_b073", surf_b4, 0.0073), ("b4_b110", surf_b4, 0.0110),
                            ("gradctl_b073", surf_ctl, 0.0073)):
            dots = k2mod.emit(np.where(active, s, -1), active, int(round(rate * base)))
            fold2 = dict(fold)
            k2mod.score_arm(terms, nm, dots, fold2, valid)
        print(f"fold {f} done canary_max={max(v['canary'] for v in row['features'].values()):.3f}", flush=True)
    np.savez_compressed(OUT / "terms.npz", **terms)
    summary = shared.pooled_summary(terms, draws=2000, seed=SEED, candidate="b4_b073")
    (EV / "holdout.json").write_text(json.dumps(
        {"experiment": "B4 paired-flank step (E1: b4 vs grad control, 2 budgets)",
         "evidence_class": "HOLDOUT-DTI", "evaluator_version": shared.VERSION,
         "canaries": canaries, "summary": summary}, indent=2, default=str) + "\n")
    for nm, s in sorted(summary["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        print(f"{nm} HOLDOUT-DTI {s['dti']:.5f} CI {s['ci95']} n={s['withheld_positive_pixels']}")
    for nm, d in summary["paired_differences"].items():
        print(f"d(b4_b073-{nm}) {d['delta']:+.5f} CI {d['ci95']}")


def cmd_holdout2():
    """E2: matched-budget check b4_b110 vs gradctl_b110 + budget 1.5%."""
    grid, valid, eligible, folds, steps, grads = ctx()
    terms = {}
    for fold in folds:
        surf_b4 = fused(steps, fold["train"]); surf_ctl = fused(grads, fold["train"], src=grads)
        active = fold["region"] & ~fold["visible"]; base = int(active.sum())
        for nm, s, rate in (("b4_b110", surf_b4, 0.0110), ("gradctl_b110", surf_ctl, 0.0110),
                            ("b4_b150", surf_b4, 0.0150)):
            dots = k2mod.emit(np.where(active, s, -1), active, int(round(rate * base)))
            k2mod.score_arm(terms, nm, dots, fold, valid)
        print(f"fold {fold['fold']} e2 done", flush=True)
    np.savez_compressed(OUT / "terms_e2.npz", **terms)
    summary = shared.pooled_summary(terms, draws=2000, seed=SEED, candidate="b4_b110")
    (EV / "holdout_e2.json").write_text(json.dumps(
        {"experiment": "B4 E2 matched budgets", "evidence_class": "HOLDOUT-DTI",
         "evaluator_version": shared.VERSION, "summary": summary}, indent=2, default=str) + "\n")
    for nm, s in sorted(summary["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        print(f"{nm} HOLDOUT-DTI {s['dti']:.5f} CI {s['ci95']} n={s['withheld_positive_pixels']}")
    for nm, d in summary["paired_differences"].items():
        print(f"d(b4_b110-{nm}) {d['delta']:+.5f} CI {d['ci95']}")


FINAL_NAME = "gemsdoekarage2-b4-stepasym-b110-20261028-zeros"
FINAL_NOTE = "B4 paired-flank scarp-step asymmetry (elev/basement/gravity/RTP), dotted 1.10%, >2px off catalogue; zeros outside"


def cmd_final():
    grid, valid, eligible, folds, steps, grads = ctx()
    surf = fused(steps, eligible)  # full-catalogue train domain = all eligible
    dcat = ndi.distance_transform_edt(~grid.catalogue)
    allowed = eligible & (dcat > 2)
    budget = int(round(0.0110 * int(allowed.sum())))
    dots = k2mod.emit(np.where(allowed, surf, -1), allowed, budget)
    np.save(OUT / "final_surface.npy", surf); np.save(OUT / "final_dots.npy", dots)
    from gems57 import submission_writer
    outtif = ROOT / "docs/downloads" / f"{FINAL_NAME}.tif"
    receipt = submission_writer.write_submission(
        outtif, dots.astype(np.float32), DATA / "sample_submission.tif",
        grid.footprint, note=FINAL_NOTE, name=FINAL_NAME, catalogue=grid.catalogue)
    (EV / "final_generation.json").write_text(json.dumps(
        {"name": FINAL_NAME, "note": FINAL_NOTE, "dots": int(dots.sum()), "budget": budget,
         "sha256": hashlib.sha256(outtif.read_bytes()).hexdigest(), "receipt": receipt},
        indent=2, default=str) + "\n")
    print(outtif, int(dots.sum()), hashlib.sha256(outtif.read_bytes()).hexdigest())


def cmd_audit():
    from gems57 import uniqueness as uniq
    grid = load_grid(DATA)
    tif = ROOT / "docs/downloads" / f"{FINAL_NAME}.tif"
    with rasterio.open(tif) as ds:
        mine = ds.read(1)
    sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    pf = ROOT / ".cache/registry_focus"
    names = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
             "GEMSDOE31", "GEMSDOE32", "GEMSDOE36", "GEMSDOE33"]
    records = [{"repo": n, "submission": str(pf / f"{n}.tif"), "file": str(pf / f"{n}.tif"), "sha256": None}
               for n in names]
    records += [
        {"repo": "13GEMSDOE-lattice", "submission": "r13-lattice", "file": str(pf / "r13_lattice_nan.tif"), "sha256": None},
        {"repo": "karage2-k2", "submission": "k2-hgbcont", "file": "docs/downloads/gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif", "sha256": None},
        {"repo": "karage2-h1", "submission": "h1-parity", "file": "docs/downloads/gemsdoekarage2-h1-parity-1ab65e3fb345-DO-NOT-SUBMIT-surface.tif", "sha256": None},
        {"repo": "karage2-hkarage1", "submission": "hkarage1", "file": "docs/downloads/gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros.tif", "sha256": None},
    ]
    audit = uniq.compare_array_to_registry(mine, records, grid.footprint, file_sha256=sha,
                                           include_reverse=False,
                                           expected_grid=(grid.shape, grid.crs, grid.transform))
    audit["scope"] = "9 focus best + r13 lattice + 3 prior local candidates (pinned focus assets). Not organizer registry."
    audit["name"] = FINAL_NAME
    (EV / "final_registry_audit.json").write_text(json.dumps(audit, indent=2, default=str) + "\n")
    rows = [r for r in audit["rows"] if "error" not in r]
    for r in rows:
        print(r.get("repo"), "rho=", r.get("spearman_full_footprint"), "overlap=", r.get("my_dots_within_3px_of_theirs"))
    print("unique:", audit.get("unique"), "verdict:", audit.get("verdict"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["surface", "holdout", "holdout2", "final", "audit"])
    a = ap.parse_args()
    {"surface": cmd_surface, "holdout": cmd_holdout, "holdout2": cmd_holdout2, "final": cmd_final, "audit": cmd_audit}[a.cmd]()

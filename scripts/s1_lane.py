#!/usr/bin/env python3
"""S1 lane (2026-10-31, arena/fe0fee78): seismicity-flank supervised lineament recovery.

Method paragraph (assigned lane, research/hypotheses-2026-10-31-untried-slate.md):

  S1 — Fold-local gradient-boosted prediction of visible catalogue faults from the
  template's cached 35-channel feature stack — with the previously unused seismicity
  bands (deq_n100a15, ieq_n100a15) and geodetic strain bands (geod_shearrate,
  geod_dilaterate) added to the potential-field/topography channels — with visible
  fault pixels masked pixel-exactly, followed by fixed-budget off-catalogue (>2 px)
  dotted emission, scored on the spatially-blocked hide-and-recover holdout with
  pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel).

Shared tools used UNCHANGED: vendor/gems57 (evaluator `gems57-pooled-hide-v2`,
folds, metric, uniqueness, submission writer) and the template's cached feature
stack at .cache/work/feature_stack.npy.  Emission helpers are reused from
scripts/k3.py (candidate-side code; k3 is not retired).  Nothing in the shared
template is forked.

Subcommands
  canary   E1: per-channel leakage canaries (AUC <= 0.90) + two primitive arms
  holdout  E2: S1 arm vs seismicity/strain ablation arm, 3 emission configs
  final    E3: full-catalogue model -> surface gate -> emission -> writer -> card
  audit    final-dot uniqueness vs the pinned registry list + local downloads

Budget: 3 experiments (canary, holdout, final) / 2 hours; no slot is selected here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT / "vendor"), str(ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from gems57 import evaluate_holdout as shared          # noqa: E402
from gems57 import spatial                             # noqa: E402
from gems57.grid import load_grid                      # noqa: E402
from k3 import emit, emit_dti, fold_crop, score_arm, train_hgb  # noqa: E402 (candidate-side reuse)

DATA = ROOT / ".cache" / "competition_data"
STACK = ROOT / ".cache" / "work" / "feature_stack.npy"
RECEIPT = ROOT / ".cache" / "work" / "feature_receipt.json"
S1 = ROOT / ".cache" / "s1"
S1.mkdir(parents=True, exist_ok=True)
EV = ROOT / "evidence" / "s1"
EV.mkdir(parents=True, exist_ok=True)
SEED = 20261031
INCUMBENT_HOLDOUT = 0.19157          # k3dti_b110, evidence/k3/combined_holdout.json
INCUMBENT_NOTE = ("k3dti_b110 recorded same-instrument HOLDOUT-DTI 0.19157 "
                  "[0.17474, 0.20880], n=58258, gems57-pooled-hide-v2")

# channels (0-based indices into the cached stack) carrying the S1 novelty
S1_NEW_CHANNELS = (6, 7, 9, 15)      # band07 geod_shearrate, band08 geod_dilaterate,
                                     # band10 deq_n100a15, band16 ieq_n100a15
FOOTPRINT_CHANNEL = 34               # mask channel: excluded from features


def load_channels() -> list[str]:
    rec = json.loads(RECEIPT.read_text())
    names = rec["channels"]
    assert len(names) == rec["n_channels"] == 35, rec
    return names


def feature_indices(names: list[str], ablate: bool) -> list[int]:
    idx = [i for i in range(len(names)) if i != FOOTPRINT_CHANNEL]
    if ablate:
        idx = [i for i in idx if i not in S1_NEW_CHANNELS]
    return idx


def grid_masks(grid):
    """valid = footprint & finite raw 19 bands; eligible = valid eroded by 12 px."""
    F = np.load(STACK, mmap_mode="r")
    assert F.shape == (grid.height, grid.width, 35), F.shape
    raw = np.asarray(F[..., :19])
    raw_valid = np.isfinite(raw).all(axis=-1) & (np.abs(raw) < 1e30).all(axis=-1)
    valid = grid.footprint & raw_valid
    eligible = valid & (ndi.distance_transform_edt(valid) > 12)
    return F, valid, eligible


def load_folds(grid, eligible):
    return list(spatial.folds(grid.catalogue, eligible, buffer_px=80))


def gather(F, flat_idx, feat_idx):
    X = np.column_stack([np.asarray(F[..., i]).ravel()[flat_idx] for i in feat_idx])
    # HistGradientBoosting supports NaN but not +/-inf; normalise infinities only.
    bad = ~np.isfinite(X)
    if bad.any():
        X[bad] = np.nan
    return X


# --------------------------------------------------------------------------- #
# E1: leakage canaries + primitive arms
# --------------------------------------------------------------------------- #
def cmd_canary() -> None:
    from sklearn.metrics import roc_auc_score
    names = load_channels()
    feat_idx = feature_indices(names, ablate=False)
    grid = load_grid(DATA)
    F, valid, eligible = grid_masks(grid)
    folds = load_folds(grid, eligible)
    canaries, terms = [], {}
    for fold in folds:
        f = fold["fold"]
        active = fold["region"] & ~fold["visible"]
        pos = np.flatnonzero(fold["truth"])
        neg_pool = np.flatnonzero(active & ~fold["truth"])
        rng = np.random.default_rng(SEED + f)
        neg = rng.choice(neg_pool, min(60_000, len(neg_pool)), replace=False)
        ids = np.r_[pos, neg]
        y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
        X = gather(F, ids, feat_idx)
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        row = {"fold": f, "positives": int(len(pos)), "unlabeled_sample": int(len(neg)),
               "features": {}}
        for j, i in enumerate(feat_idx):
            auc = float(roc_auc_score(y, X[:, j]))
            can = max(auc, 1 - auc)
            row["features"][names[i]] = {"auc": auc, "canary_max_auc_1m": can,
                                         "pass": bool(can <= 0.90)}
        canaries.append(row)
        # primitive arms (label-free surfaces, emission at 0.73% of active)
        base = int(round(0.0073 * int(active.sum())))
        surf_g = np.nan_to_num(np.asarray(F[..., 28]), nan=0.0)   # grav_edge (idx 28)
        score_arm(terms, "prim_grav_edge", emit(surf_g, active, base), fold, valid)
        q = np.nan_to_num(np.asarray(F[..., 9]) + np.asarray(F[..., 15]), nan=0.0)
        w = ndi.gaussian_filter(active.astype(np.float32), 5.0)
        surf_q = ndi.gaussian_filter(q.astype(np.float32), 5.0) / np.maximum(w, 1e-6)
        score_arm(terms, "prim_quake_rate", emit(np.float32(surf_q), active, base), fold, valid)
        print(f"fold {f} canaries+primitives done "
              f"pos={int(len(pos))} budget={base}", flush=True)
        del X
    worst: dict[str, float] = {}
    for row in canaries:
        for n, v in row["features"].items():
            worst[n] = max(worst.get(n, 0.0), v["canary_max_auc_1m"])
    out = {"experiment": "S1 E1 leakage canaries + primitives",
           "evidence_class": "HOLDOUT-DTI (primitives) / LEAKAGE-CANARY (AUC)",
           "evaluator_version": shared.VERSION, "seed": SEED,
           "channels_tested": len(worst),
           "canaries": canaries, "worst_canary_by_channel": worst,
           "canary_all_pass": bool(worst) and bool(max(worst.values()) <= 0.90),
           "worst_channel": max(worst, key=worst.get) if worst else None,
           "incumbent_reference": INCUMBENT_NOTE}
    (EV / "e1_canary.json").write_text(json.dumps(out, indent=2) + "\n")
    np.savez_compressed(S1 / "terms_e1.npz", **terms)
    print("E1 canary_all_pass:", out["canary_all_pass"],
          "worst:", out["worst_channel"], round(max(worst.values()), 4), flush=True)


# --------------------------------------------------------------------------- #
# E2: S1 vs ablation on identical folds
# --------------------------------------------------------------------------- #
def fold_train_predict(F, fold, catalogue, seed, feat_idx):
    visible, train = fold["visible"], fold["train"]
    pos = np.flatnonzero(catalogue & train)
    dvis = ndi.distance_transform_edt(~visible)
    neg_pool = np.flatnonzero(train & ~catalogue & (dvis > 3))
    rng = np.random.default_rng(seed)
    neg = rng.choice(neg_pool, min(180_000, len(neg_pool)), replace=False)
    ids = np.r_[pos, neg]
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    model = train_hgb(gather(F, ids, feat_idx), y, seed)
    region_idx = np.flatnonzero(fold["region"] & ~visible)
    surf = np.zeros(catalogue.shape, np.float32)
    for s in range(0, len(region_idx), 400_000):
        chunk = region_idx[s:s + 400_000]
        surf.ravel()[chunk] = model.predict_proba(gather(F, chunk, feat_idx))[:, 1]
    return surf, {"pos": int(len(pos)), "neg": int(len(neg))}


def cmd_holdout() -> None:
    names = load_channels()
    fi_s1 = feature_indices(names, ablate=False)
    fi_ab = feature_indices(names, ablate=True)
    grid = load_grid(DATA)
    F, valid, eligible = grid_masks(grid)
    folds = load_folds(grid, eligible)
    terms, receipts = {}, []
    for fold in folds:
        f = fold["fold"]
        t0 = time.time()
        active = fold["region"] & ~fold["visible"]
        base = int(active.sum())
        rec = {"fold": f}
        for tag_prefix, feat_idx in (("s1", fi_s1), ("ablate", fi_ab)):
            surf, ntr = fold_train_predict(F, fold, grid.catalogue, SEED + f, feat_idx)
            rec[tag_prefix] = ntr
            for rate, tag in ((0.0073, f"{tag_prefix}_b073"), (0.0110, f"{tag_prefix}_b110")):
                dots = emit(surf, active, int(round(rate * base)))
                score_arm(terms, tag, dots, fold, valid)
            dots = emit_dti(surf, active, int(round(0.0110 * base)))
            score_arm(terms, f"{tag_prefix}_b110dti", dots, fold, valid)
            del surf
        rec["seconds"] = round(time.time() - t0, 1)
        receipts.append(rec)
        print(f"fold {f} done {rec}", flush=True)
    np.savez_compressed(S1 / "terms_e2.npz", **terms)
    out = {"experiment": "S1 E2 holdout: 34ch vs seismicity/strain ablation",
           "evidence_class": "HOLDOUT-DTI", "evaluator_version": shared.VERSION,
           "seed": SEED, "model": "HistGradientBoosting 350it lr.06 leaves63 "
           "minleaf40 L2=1 (shared k3 recipe)", "folds": receipts,
           "arms": sorted(terms), "s1_new_channels": [names[i] for i in S1_NEW_CHANNELS],
           "ablated_channels": [names[i] for i in S1_NEW_CHANNELS],
           "incumbent_reference": INCUMBENT_NOTE}
    (EV / "e2_holdout.json").write_text(json.dumps(out, indent=2) + "\n")
    print("E2 terms saved:", sorted(terms), flush=True)


def combine(candidate: str) -> dict:
    terms = {}
    for tag in ("e1", "e2"):
        z = np.load(S1 / f"terms_{tag}.npz")
        for k in z.files:
            terms[k] = z[k]
    summary = shared.pooled_summary(terms, draws=2000, seed=SEED, candidate=candidate)
    summary["candidate_for_paired_diffs"] = candidate
    summary["incumbent_reference"] = INCUMBENT_NOTE
    (EV / "combined_holdout.json").write_text(json.dumps(summary, indent=2) + "\n")
    for name, s in sorted(summary["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        print(f"{name:18s} HOLDOUT-DTI {s['dti']:.5f} CI [{s['ci95'][0]:.5f},"
              f"{s['ci95'][1]:.5f}] n={s['withheld_positive_pixels']}", flush=True)
    for name, d in summary["paired_differences"].items():
        print(f"  d({candidate}-{name}) {d['delta']:+.5f} "
              f"CI [{d['ci95'][0]:+.5f},{d['ci95'][1]:+.5f}]", flush=True)
    return summary


# --------------------------------------------------------------------------- #
# E3: full-catalogue model, surface gate, emission, writer
# --------------------------------------------------------------------------- #
def train_final_model():
    names = load_channels()
    feat_idx = feature_indices(names, ablate=False)
    grid = load_grid(DATA)
    F, valid, eligible = grid_masks(grid)
    dcat = ndi.distance_transform_edt(~grid.catalogue)
    pos = np.flatnonzero(grid.catalogue & eligible)
    neg_pool = np.flatnonzero(eligible & ~grid.catalogue & (dcat > 3))
    rng = np.random.default_rng(SEED)
    neg = rng.choice(neg_pool, min(300_000, len(neg_pool)), replace=False)
    ids = np.r_[pos, neg]
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    print(f"final train pos={len(pos)} neg={len(neg)}", flush=True)
    model = train_hgb(gather(F, ids, feat_idx), y, SEED)
    allowed = eligible & (dcat > 2)
    idx = np.flatnonzero(allowed)
    surf = np.zeros(grid.shape, np.float32)
    for s in range(0, len(idx), 400_000):
        chunk = idx[s:s + 400_000]
        surf.ravel()[chunk] = model.predict_proba(gather(F, chunk, feat_idx))[:, 1]
    np.save(S1 / "surf_final.npy", surf)
    np.save(S1 / "allowed_final.npy", allowed)
    receipt = {"train_pos": int(len(pos)), "train_neg": int(len(neg)),
               "allowed_px": int(allowed.sum()), "eligible_px": int(eligible.sum()),
               "feature_channels": len(feat_idx)}
    (EV / "final_train.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt, flush=True)
    return grid, valid, surf, allowed


def focus_records(exclude_sha: str | None = None):
    """Every pinned manifest raster (status ok) + every published local download."""
    records = []
    man = json.loads((ROOT / "registry/focus_registry_manifest.json").read_text())
    for r in man["rasters"]:
        if r.get("status") != "ok":
            continue
        records.append({"repo": r["repo"], "submission": r["path"],
                        "file": str(ROOT / r["local"]), "sha256": r["sha256"]})
    for p in sorted((ROOT / "docs/downloads").glob("*.tif")):
        records.append({"repo": "karage2-local", "submission": p.name,
                        "file": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    # Byte-identical twins exist across manifest rows (same submission pinned
    # twice); the comparator is per unique raster, so dedupe on sha.
    seen: set[str] = set()
    unique = []
    for r in records:
        if r["sha256"] in seen or (exclude_sha and r["sha256"] == exclude_sha):
            continue
        seen.add(r["sha256"])
        unique.append(r)
    return unique


def cmd_surfacecheck(rate: float = 0.0110, placement: str = "dti") -> None:
    from gems57 import uniqueness as uniq
    if (rate == 0.0110 and placement == "dti"
            and (ROOT / ".cache/s1/surf_final.npy").is_file()
            and (ROOT / ".cache/s1/allowed_final.npy").is_file()):
        from gems57.grid import load_grid as _load_grid
        grid = _load_grid(DATA)
        surf = np.load(ROOT / ".cache/s1/surf_final.npy")
        allowed = np.load(ROOT / ".cache/s1/allowed_final.npy")
        print(f"reusing saved surface from .cache/s1/surf_final.npy {surf.shape}")
    else:
        grid, _valid, surf, allowed = train_final_model()
    budget = int(round(rate * int(allowed.sum())))
    if placement == "dti":
        top_support = emit_dti(surf, allowed, budget)
    else:
        top_support = emit(surf, allowed, budget)
    np.save(S1 / "top_support.npy", top_support)
    gen = json.loads((EV / "final_generation.json").read_text())
    file_sha = gen["writer_receipt"]["sha256"]
    records = focus_records(exclude_sha=file_sha)
    mine01 = np.where(grid.footprint, np.clip(surf, 0, 1), 0).astype(np.float32)
    rows = []
    for rec in records:
        with rasterio.open(rec["file"]) as ds:
            theirs = ds.read(1)
        if theirs.shape != grid.shape:
            continue
        theirs = np.where(np.isfinite(theirs), theirs, 0).astype(np.float32)
        rho = uniq.surface_rho(mine01, theirs, grid.footprint)
        ov = uniq.dot_overlap(top_support.astype(np.float32), theirs)
        rows.append({"repo": rec["repo"], "submission": rec["submission"],
                     "spearman": rho.get("spearman_full_footprint"),
                     "top_support_overlap": ov})
    worst_rho = max((abs(r["spearman"]) for r in rows if r["spearman"] is not None),
                    default=0.0)
    worst_ov = max((r["top_support_overlap"] for r in rows), default=0.0)
    n_over = sum(1 for r in rows if (r["top_support_overlap"] or 0) > 0.70)
    lattice_rows = [r for r in rows if "r13-lattice" in r["submission"]]
    out = {"evidence_class": "REGISTRY-MEASUREMENT (surface, before placement)",
           "rate": rate, "placement": placement, "budget": budget,
           "candidate_sha256": file_sha,
           "scope_count": len(rows),
           "worst_abs_spearman": worst_rho, "worst_overlap": worst_ov,
           "n_overlap_over_0p70": n_over,
           "lattice_rows": lattice_rows,
           "rows_over_0p70": [r for r in rows if (r["top_support_overlap"] or 0) > 0.70],
           "note": ("overlap gate = <=70% of my dots within 3 px of one registry "
                    "raster's dots; the spacing-5 lattice witness is a degenerate "
                    "dense witness (99.87% of footprint cells within 3 px of it), "
                    "reported separately as protocol irregularity")}
    (EV / "surface_gate.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(f"SURFACE: worst|rho|={worst_rho:.4f} worst_overlap={worst_ov:.4f} "
          f"n_over={n_over}/{len(rows)} budget={budget}", flush=True)
    for r in lattice_rows:
        print("  lattice row:", r, flush=True)


def cmd_final(rate: float = 0.0110, placement: str = "dti") -> None:
    from gems57.submission_writer import write_submission
    grid = load_grid(DATA)
    surf = np.load(S1 / "surf_final.npy")
    allowed = np.load(S1 / "allowed_final.npy")
    budget = int(round(rate * int(allowed.sum())))
    dots = emit_dti(surf, allowed, budget) if placement == "dti" else emit(surf, allowed, budget)
    n = int(dots.sum())
    print(f"placed {n} dots (budget {budget}, placement {placement})", flush=True)
    pred = np.where(grid.footprint, dots.astype(np.float32), 0.0).astype(np.float32)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    stem = f"gemsdoekarage2-s1-quakeflank-{n}d-{stamp}-zeros"
    note = "S1 seismicity-flank HGB 34ch hide-recover validated off-catalogue emission"
    assert len(note) <= 140 and len(stem) <= 140
    out = ROOT / "docs" / "downloads" / f"{stem}.tif"
    receipt = write_submission(out, pred, DATA / "sample_submission.tif",
                               grid.footprint, note=note, name=stem,
                               catalogue=grid.catalogue)
    gen = {"stem": stem, "note": note, "placement": placement, "rate": rate,
           "budget": budget, "dots": n, "writer_receipt": receipt,
           "exterior_convention": "finite zeros outside footprint, nodata tag None "
                                  "(convention of the owner-scored 0.2778 champion "
                                  "file c55bafc4...; H-F nodata=nan-tag failure flagged)",
           "generated_utc": stamp}
    (EV / "final_generation.json").write_text(json.dumps(gen, indent=2, default=str) + "\n")
    print(json.dumps({k: gen[k] for k in ("stem", "dots", "rate", "placement")}, indent=2),
          flush=True)


def cmd_audit() -> None:
    from gems57 import uniqueness as uniq
    grid = load_grid(DATA)
    gen = json.loads((EV / "final_generation.json").read_text())
    tif = ROOT / "docs" / "downloads" / f"{gen['stem']}.tif"
    with rasterio.open(tif) as ds:
        mine = ds.read(1)
    file_sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    records = focus_records(exclude_sha=file_sha)
    t0 = time.time()
    audit = uniq.compare_array_to_registry(
        mine, records, grid.footprint, file_sha256=file_sha,
        include_reverse=False, expected_grid=(grid.shape, grid.crs, grid.transform))
    audit["scope"] = "focus registry manifest (status ok) + all local published downloads"
    audit["scope_count"] = len(records)
    rows = [r for r in audit["rows"] if "error" not in r]
    errs = [r for r in audit["rows"] if "error" in r]
    worst_rho = max(rows, key=lambda r: abs(r.get("spearman_full_footprint") or 0))
    worst_ov = max(rows, key=lambda r: r.get("my_dots_within_3px_of_theirs") or 0)
    lattice = [r for r in rows if "r13-lattice" in str(r.get("submission"))]
    summary = {
        "checked": len(rows), "errors": len(errs),
        "worst_abs_spearman": abs(worst_rho.get("spearman_full_footprint") or 0),
        "worst_spearman_at": f"{worst_rho.get('repo')}/{worst_rho.get('submission')}",
        "worst_overlap": worst_ov.get("my_dots_within_3px_of_theirs"),
        "worst_overlap_at": f"{worst_ov.get('repo')}/{worst_ov.get('submission')}",
        "duplicate_count_literal": audit.get("duplicate_count"),
        "lattice_rows": [{k: r.get(k) for k in ("repo", "submission",
                                                "my_dots_within_3px_of_theirs",
                                                "spearman_full_footprint")} for r in lattice],
        "seconds": round(time.time() - t0, 1),
        "file_sha256": file_sha,
    }
    (EV / "final_registry_audit.json").write_text(
        json.dumps({"summary": summary, "audit": audit}, indent=2, default=str) + "\n")
    print(json.dumps(summary, indent=2, default=str), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["canary", "holdout", "combine", "surfacecheck",
                                    "final", "audit"])
    ap.add_argument("--candidate", default="s1_b110dti")
    ap.add_argument("--rate", type=float, default=0.0110)
    ap.add_argument("--placement", choices=["fixed", "dti"], default="dti")
    a = ap.parse_args()
    if a.cmd == "canary":
        cmd_canary()
    elif a.cmd == "holdout":
        cmd_holdout()
    elif a.cmd == "combine":
        combine(a.candidate)
    elif a.cmd == "surfacecheck":
        cmd_surfacecheck(a.rate, a.placement)
    elif a.cmd == "final":
        cmd_final(a.rate, a.placement)
    elif a.cmd == "audit":
        cmd_audit()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Lane K9 — cross-potential-field corroborated lineaments (magnetics x gravity).

One preregistered lane under the PARALLEL-RUN PROTOCOL:
  * Method (single paragraph): build two label-blind edge-strength families from
    the pinned 19-band mirror -- magnetic (tmi_hg band 3, tmi_vg band 9) and
    gravity (iso_grav_anom_hg band 18, |iso_grav_anom_vg| band 11); form a
    structure-tensor orientation + coherence field per family at 200 m and
    600 m scales; corroborate the families where their lineament orientations
    agree within ~30 degrees and both families are strong; bridge along-strike
    gaps with an oriented morphological closing; emit at most 38,000 binary
    value-1.0 dots by greedy non-maximum suppression (>= 200 m apart) on the
    corroborated surface, excluding a 200 m catalogue apron (the champion's
    measured B2 lever) and a 1.2 km footprint-edge collar.
  * Holdout: shared hide-and-recover (label-blind quadrants v2, whole original
    connected components, 8 km training buffer). Catalogue-derived features:
    NONE (the lane is geophysics-only, so the catalogue-leakage class is
    structurally absent); visible faults are still masked pixel-exactly by the
    shared evaluator. Pooled DTI alpha=0.2 beta=0.8, 300 m triangular kernel.
  * Budget: one experiment (<= 3 allowed), 2-hour watchdog, no slot use.
"""
from __future__ import annotations

import hashlib
import json
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from gems57 import evaluate_holdout as shared          # noqa: E402
from gems57 import spatial, uniqueness                  # noqa: E402
from gems57.grid import load_grid                       # noqa: E402
from gems57.submission_writer import write_submission   # noqa: E402

DATA = ROOT / ".cache/gems_data"
OUT = ROOT / "evidence/k9"
T0 = time.time()
DOT_BUDGET = 38_000
NMS_RADIUS_PX = 2.0          # >= 200 m between emitted dots
CATALOGUE_APRON_PX = 2       # champion B2 lever (200 m)
EDGE_COLLAR_PX = 12          # 1.2 km footprint-edge erosion
SCALES = (2, 6)              # 200 m / 600 m structure scales
ORIENT_SIGMA = 3.0           # structure-tensor smoothing (300 m)
CLOSE_LEN = 9                # oriented closing line length (px)


def save(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def elapsed():
    return round(time.time() - T0, 1)


def verify_inputs():
    man = json.loads((ROOT / "registry/core_data_manifest.json").read_text())
    for entry in man["files"]:
        h = hashlib.sha256((DATA / entry["dest"]).read_bytes()).hexdigest()
        if h != entry["sha256"]:
            raise ValueError(f"input sha256 mismatch: {entry['dest']}")


def qnorm(a, valid, q=0.999):
    """Quantile-normalize a field to [0,1] on the valid domain (label-blind)."""
    v = a[valid]
    cut = float(np.quantile(v, q))
    if cut <= 0:
        raise ValueError("non-positive quantile cut")
    out = np.clip(a / cut, 0.0, 1.0).astype(np.float32)
    out[~valid] = 0.0
    return out


def family_strength(band_ids, valid):
    """RMS-combined, per-scale-normalized edge strength for one physical family."""
    with rasterio.open(DATA / "training_features.tif") as ds:
        members = []
        for i in band_ids:
            b = ds.read(i).astype(np.float32)
            ok = valid & np.isfinite(b) & (np.abs(b) < 1e30)
            if not ok.any():
                raise ValueError(f"band {i} has no finite support")
            b = np.where(ok, b, 0.0)
            cut = float(np.quantile(b[ok], 0.999))
            m = np.clip(np.abs(b) / max(cut, 1e-12), 0.0, 1.0).astype(np.float32)
            m[~ok] = 0.0
            members.append(m)
    return members


def structure_tensor(field, scale):
    """Orientation (gradient-major axis) and coherence of an edge field."""
    sm = ndi.gaussian_filter(field, scale)
    gy, gx = np.gradient(sm)
    jxx = ndi.gaussian_filter(gx * gx, ORIENT_SIGMA)
    jxy = ndi.gaussian_filter(gx * gy, ORIENT_SIGMA)
    jyy = ndi.gaussian_filter(gy * gy, ORIENT_SIGMA)
    theta = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy)      # gradient-major axis
    tr = jxx + jyy
    coh = np.sqrt((jxx - jyy) ** 2 + 4.0 * jxy ** 2) / np.maximum(tr, 1e-12)
    return theta.astype(np.float32), np.clip(coh, 0.0, 1.0).astype(np.float32)


def oriented_closing(mask, valid):
    """Max over 4 line directions of a binary closing (bridges along-strike gaps)."""
    out = np.zeros_like(mask)
    k = CLOSE_LEN
    half = k // 2
    yy, xx = np.mgrid[-half:half + 1, -half:half + 1]
    for deg in (0, 45, 90, 135):
        t = np.deg2rad(deg)
        line = (np.abs(yy * np.sin(t) - xx * np.cos(t)) < 0.71) & \
               (np.abs(yy * np.cos(t) + xx * np.sin(t)) <= half)
        d = ndi.binary_dilation(mask, structure=line)
        out |= ndi.binary_erosion(d, structure=line)
    return out & valid


def place_dots(surface, eligible, budget, seed=None):
    """Greedy NMS dots on a soft surface; deterministic; >= NMS_RADIUS_PX apart."""
    ids = np.flatnonzero(eligible & (surface > 0))
    if ids.size == 0:
        raise ValueError("no eligible cells to place dots")
    order = ids[np.argsort(-surface.ravel()[ids], kind="stable")]
    top_n = min(order.size, max(budget * 40, 400_000))
    order = order[:top_n]
    pad = 3
    accepted_pad = np.zeros((surface.shape[0] + 2 * pad, surface.shape[1] + 2 * pad), bool)
    r2 = NMS_RADIUS_PX * NMS_RADIUS_PX
    yy, xx = np.mgrid[-pad:pad + 1, -pad:pad + 1]
    disk = (yy * yy + xx * xx) <= r2
    h, w = surface.shape
    ys, xs = np.divmod(order, w)
    dots_y, dots_x = [], []
    for y, x in zip(ys.tolist(), xs.tolist()):
        if (accepted_pad[y:y + 2 * pad + 1, x:x + 2 * pad + 1] & disk).any():
            continue
        accepted_pad[y + pad, x + pad] = True
        dots_y.append(y)
        dots_x.append(x)
        if len(dots_y) >= budget:
            break
    out = np.zeros(surface.shape, np.float32)
    out[np.asarray(dots_y, np.int64), np.asarray(dots_x, np.int64)] = 1.0
    return out, len(dots_y)


def random_dots(eligible, budget, seed):
    rng = np.random.default_rng(seed)
    ids = np.flatnonzero(eligible)
    pick = rng.choice(ids, size=min(budget, ids.size), replace=False)
    out = np.zeros(eligible.shape, np.float32)
    ys, xs = np.divmod(pick, eligible.shape[1])
    out[ys, xs] = 1.0
    return out


# --- shared-template control (verbatim primitives from scripts/run_experiment.py) ---
def gradients(a, valid, sigma):
    w = ndi.gaussian_filter(valid.astype(np.float32), sigma)
    sm = ndi.gaussian_filter(np.where(valid, a, 0).astype(np.float32), sigma)
    sm /= np.maximum(w, 1e-6)
    dy, dx = np.gradient(sm)
    return dy, dx, np.hypot(dy, dx)


def opposition_control(valid):
    with rasterio.open(DATA / "training_features.tif") as ds:
        el, ba, co = [ds.read(i).astype(np.float32) for i in (12, 15, 17)]
    fields = {}
    for scale in (2, 6):
        e, b, c = [gradients(a, valid, scale) for a in (el, ba, co)]
        cos = (e[0] * b[0] + e[1] * b[1]) / np.maximum(e[2] * b[2], 1e-10)
        fields[f"opposition_s{scale}"] = np.clip(-cos, 0, 1).astype(np.float32)
    for a in fields.values():
        a[~valid] = 0
    return fields["opposition_s2"]


def crop_fold(fold, sl):
    return {k: fold[k][sl] for k in ("region", "truth", "visible")}


def main():
    def budget_expired(signum, frame):
        raise TimeoutError("two-hour budget exhausted")
    signal.signal(signal.SIGALRM, budget_expired)
    signal.alarm(7200 - 600)  # leave 10 min for packaging/pages
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    verify_inputs()
    grid = load_grid(DATA)
    fp, cat = grid.footprint, grid.catalogue
    print(f"[{elapsed()}s] grid loaded: footprint={fp.sum():,} catalogue={cat.sum():,}", flush=True)

    # ---------- label-blind geophysical features ----------
    with rasterio.open(DATA / "training_features.tif") as ds:
        fin = np.ones(fp.shape, bool)
        for i in (3, 9, 11, 18):
            b = ds.read(i)
            fin &= np.isfinite(b) & (np.abs(b) < 1e30)
    valid = fp & fin
    eligible = valid & (ndi.distance_transform_edt(valid) > EDGE_COLLAR_PX)
    print(f"[{elapsed()}s] valid={valid.sum():,} eligible={eligible.sum():,}", flush=True)

    mag_hg, mag_vg = family_strength([3, 9], valid)
    grav_hg, grav_vg = family_strength([18, 11], valid)
    mag = {s: qnorm(np.sqrt((mag_hg ** 2 + mag_vg ** 2) / 2.0), valid) for s in SCALES}
    grav = {s: qnorm(np.sqrt((grav_hg ** 2 + grav_vg ** 2) / 2.0), valid) for s in SCALES}
    del mag_hg, mag_vg, grav_hg, grav_vg

    corr, mag_e, grav_e, mag_th, grav_th = {}, {}, {}, {}, {}
    for s in SCALES:
        th_m, c_m = structure_tensor(mag[s], s)
        th_g, c_g = structure_tensor(grav[s], s)
        dth = th_m - th_g
        agree = ((1.0 + np.cos(2.0 * dth)) / 2.0) ** 2
        w = np.sqrt(np.sqrt(mag[s] * grav[s]) * c_m * c_g)
        corr[s] = (w * agree).astype(np.float32)
        corr[s][~valid] = 0.0
        mag_e[s], grav_e[s] = (np.sqrt(mag[s] * c_m), np.sqrt(grav[s] * c_g))
        mag_th[s], grav_th[s] = th_m, th_g
        print(f"[{elapsed()}s] scale {s}: corr q90={np.quantile(corr[s][valid], .9):.4f}", flush=True)
    corr_multi = qnorm(np.sqrt(corr[2] * corr[6]), valid)
    mag_multi = qnorm(np.sqrt(mag_e[2] * mag_e[6]), valid)
    grav_multi = qnorm(np.sqrt(grav_e[2] * grav_e[6]), valid)

    mask90 = corr_multi >= np.quantile(corr_multi[valid], 0.90)
    closed = oriented_closing(mask90, valid)
    candidate = (corr_multi * closed).astype(np.float32)
    candidate = qnorm(candidate, valid)
    print(f"[{elapsed()}s] closed support={closed.sum():,}", flush=True)

    # ---------- hide-and-recover holdout on all preregistered arms ----------
    arms = {
        "mag_only": mag_multi,
        "grav_only": grav_multi,
        "corr_noclose": corr_multi,
        "candidate": candidate,
        "opposition_s2": opposition_control(valid),
    }
    labels = cat  # folds only need the catalogue geometry; features never see it
    arm_arrays = dict(arms)
    arm_arrays["random38k"] = random_dots(eligible, DOT_BUDGET, 20261031)
    terms = {}
    canaries, fold_receipts = [], []
    canary_failed = False
    for fold in spatial.folds(labels, eligible, buffer_px=80):
        active = fold["region"] & ~fold["visible"]
        pos = np.flatnonzero(fold["truth"])
        neg_pool = np.flatnonzero(active & ~fold["truth"])
        rng = np.random.default_rng(20261031 + fold["fold"])
        neg = rng.choice(neg_pool, min(100_000, neg_pool.size), replace=False)
        ids = np.r_[pos, neg]
        target = np.r_[np.ones(pos.size), np.zeros(neg.size)]
        row = {"fold": fold["fold"], "positive_pixels": int(pos.size), "features": {}}
        y, x = np.nonzero(fold["region"])
        sl = np.s_[max(0, y.min() - 4):min(grid.shape[0], y.max() + 5),
                   max(0, x.min() - 4):min(grid.shape[1], x.max() + 5)]
        for name, surface in arm_arrays.items():
            auc = float(roc_auc_score(target, surface.ravel()[ids]))
            ok = auc <= 0.90
            row["features"][name] = {"auc": round(auc, 4), "leakage_canary_pass": ok}
            canary_failed |= not ok
            _, t = shared.evaluate(surface[sl].astype(np.float64), crop_fold(fold, sl),
                                   valid[sl].astype(bool), origin=(sl[0].start, sl[1].start),
                                   global_shape=grid.shape)
            terms[name] = terms.get(name, np.zeros_like(t)) + t
        canaries.append(row)
        fold_receipts.append(fold["receipt"])
        print(f"[{elapsed()}s] fold {fold['fold']}: {pos.size} withheld positives", flush=True)
    # score the placed-dot realization as its own arm after folds are built
    summary = shared.pooled_summary(terms, draws=1000, seed=20261031, candidate="candidate")
    summary["canaries"] = canaries
    summary["canary_pass"] = not canary_failed
    summary["folds"] = fold_receipts
    summary["split_version"] = "label-blind-quadrants-v2 / whole original connected components / 8km training buffer"
    save("holdout.json", summary)
    cand = summary["scores"]["candidate"]
    others = {k: v for k, v in summary["scores"].items() if k != "candidate"}
    best_other = max(others.items(), key=lambda kv: kv[1]["dti"])
    delta = summary["paired_differences"].get(best_other[0], {})
    holdout_pass = bool(delta.get("ci95") and delta["ci95"][0] > 0.0)
    print(f"[{elapsed()}s] HOLDOUT candidate={cand['dti']:.5f} CI={cand['ci95']} "
          f"best_other={best_other[0]}:{best_other[1]['dti']:.5f} paired_delta={delta.get('delta')} "
          f"pass={holdout_pass}", flush=True)

    # ---------- placement (surface gate: final-dots registry scan happens pre-write) ----------
    apron = ndi.distance_transform_edt(~cat) <= CATALOGUE_APRON_PX
    eligible_final = eligible & ~apron & ~cat
    dots, n_dots = place_dots(candidate, eligible_final, DOT_BUDGET)
    print(f"[{elapsed()}s] placed {n_dots} dots", flush=True)
    terms["final_dots"] = np.zeros_like(next(iter(terms.values())))
    for fold in spatial.folds(labels, eligible, buffer_px=80):
        y, x = np.nonzero(fold["region"])
        sl = np.s_[max(0, y.min() - 4):min(grid.shape[0], y.max() + 5),
                   max(0, x.min() - 4):min(grid.shape[1], x.max() + 5)]
        _, t = shared.evaluate(dots[sl].astype(np.float64), crop_fold(fold, sl),
                               valid[sl].astype(bool), origin=(sl[0].start, sl[1].start),
                               global_shape=grid.shape)
        terms["final_dots"] = terms["final_dots"] + t
    summary2 = shared.pooled_summary(terms, draws=1000, seed=20261031, candidate="final_dots")
    save("holdout_final_dots.json", {k: v for k, v in summary2.items() if k != "folds"})
    fd = summary2["scores"]["final_dots"]
    print(f"[{elapsed()}s] final_dots holdout DTI={fd['dti']:.5f} CI={fd['ci95']}", flush=True)

    # ---------- registry uniqueness: final dots vs EVERY raster we can enumerate ----------
    focus = json.loads((ROOT / "registry/focus_registry_manifest.json").read_text())
    records = [{"repo": r["repo"], "submission": r["path"],
                "file": str(ROOT / r["local"]), "sha256": r["sha256"]}
               for r in focus["rasters"] if r.get("status") == "ok"]
    ours = sorted((ROOT / "docs/downloads").glob("*.tif"))
    for p in ours:
        records.append({"repo": "GEMSDOEkarage2", "submission": p.name,
                        "file": str(p), "sha256": None})
    lattice_meta = json.loads((ROOT / "registry/pinned_assets.json").read_text())
    lat = next(a for a in lattice_meta["assets"] if a["role"] == "lattice")
    records.append({"repo": "13GEMSDOE", "submission": lat["path"],
                    "file": str(ROOT / ".cache/witness/lattice.tif"), "sha256": lat["sha256"]})
    seen, uniq_records = set(), []
    for r in records:
        key = (r["submission"], r["sha256"])
        if key not in seen:
            seen.add(key)
            uniq_records.append(r)
    print(f"[{elapsed()}s] registry scan over {len(uniq_records)} rasters", flush=True)
    audit = uniqueness.compare_array_to_registry(
        dots, uniq_records, fp, file_sha256=None, include_reverse=False,
        expected_grid=(grid.shape, grid.crs, grid.transform))
    two = uniqueness.two_phase_summary(audit["rows"], int(fp.sum()),
                                       expected_rasters=len(uniq_records))
    missing = [r["submission"] for r in audit["rows"] if "error" in r]
    two["missing_or_invalid"] = missing
    two["expected_rasters"] = len(uniq_records)
    two["like_for_like_firing_submissions"] = [
        f["submission"] for f in two.get("literal_firings", [])
        if f["representation"] == "dot_field"]
    two["rho_firing_submissions"] = [
        r.get("submission") for r in audit["rows"]
        if r.get("spearman_full_footprint") is not None and r["spearman_full_footprint"] > 0.90]
    save("final_registry.json", two)
    print(f"[{elapsed()}s] registry: literal firings={two['literal_reading']['forward_overlap_firings']} "
          f"like-for-like firings={len(two['like_for_like_firing_submissions'])} "
          f"rho firings={len(two['rho_firing_submissions'])}", flush=True)

    # champion-vs-lattice measurement: does the 0.2778 champion trip the same gate?
    champ_rows = [r for r in focus["rasters"]
                  if "h33-h33-2-b2" in r["path"] and r.get("status") == "ok"]
    champ_row = next((r for r in champ_rows if r["path"].endswith("-zeros.tif")),
                     champ_rows[0] if champ_rows else None)
    champion_check = None
    if champ_row:
        with rasterio.open(ROOT / champ_row["local"]) as src:
            champ = src.read(1).astype(np.float32)
        champ = np.where(np.isfinite(champ), champ, 0.0)
        champ[~fp] = 0
        lat_aud = uniqueness.compare_array_to_registry(
            champ, [{"repo": "13GEMSDOE", "submission": lat["path"],
                     "file": str(ROOT / ".cache/witness/lattice.tif"),
                     "sha256": lat["sha256"]}], fp, include_reverse=False,
            expected_grid=(grid.shape, grid.crs, grid.transform))
        r0 = lat_aud["rows"][0]
        champion_check = {"champion": champ_row["path"],
                          "reported_score_user": 0.2778,
                          "champion_dots": int((champ > 0).sum()),
                          "champion_dots_within_3px_of_lattice": r0["my_dots_within_3px_of_theirs"],
                          "interpretation": "the best historical submission also saturates the "
                                            "spacing-5 lattice witness; the literal lattice gate "
                                            "does not separate duplicates from any dense emission"}
        save("champion_vs_lattice.json", champion_check)
        print(f"[{elapsed()}s] champion-vs-lattice overlap={r0['my_dots_within_3px_of_theirs']:.4f}",
              flush=True)

    # ---------- package (fail-closed writer) ----------
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"gemsdoekarage2-k9-maggrav-corr-persist-{n_dots}d-{stamp}-zeros"[:140]
    note = ("Corroborated magnetic+gravity lineaments, oriented strike persistence; "
            "38k dots, 200m catalogue apron excluded; hide-recover evaluated")[:140]
    path = ROOT / "docs/downloads" / f"{name}.tif"
    receipt = write_submission(path, dots, DATA / "sample_submission.tif", fp,
                               note=note, name=name, catalogue=cat,
                               metadata={
                                   "artifact_role": "competition candidate",
                                   "lane": "K9 corroborated potential-field lineaments",
                                   "holdout_evaluator": shared.VERSION,
                                   "experiments_run": 1,
                               })
    save("validator.json", receipt)
    print(f"[{elapsed()}s] wrote {path.name} sha256={receipt['sha256'][:16]}", flush=True)

    # ---------- run card ----------
    literal = two["literal_reading"]
    like = two["like_for_like_reading"]
    rho_fire = two["rho_firing_submissions"]
    unique_likeforlike = (not like["duplicate"]) and not rho_fire
    verdict = ("promote" if (holdout_pass and summary["canary_pass"]
                             and unique_likeforlike and receipt["validator"]["all_checks_passed"])
               else "negative")
    card = {
        "hypothesis": "K9: hidden fault strands continue along crustal lineaments that appear "
                      "independently in both magnetic and gravity gradients; corroborated, "
                      "strike-persistent lineament axes locate faults absent from the catalogue.",
        "mechanism": "RMS edge strength (tmi_hg, |tmi_vg|) x (iso_grav_anom_hg, |iso_grav_anom_vg|); "
                     "structure-tensor orientation agreement (~30 deg) and coherence at 200 m and "
                     "600 m; oriented closing bridges <=800 m along-strike gaps; greedy 200 m NMS "
                     "dots, budget 38,000, catalogue apron 200 m excluded, 1.2 km edge collar.",
        "non_fault_mimic": "Lithological contacts and dikes also juxtapose susceptibility/density "
                           "without being faults; inversion streaking and gridding seams can mimic "
                           "corroborated edges. Controls: single-family arms and budget-matched "
                           "random dots on identical folds.",
        "holdout": {"evidence_class": "HOLDOUT-DTI", "evaluator_version": shared.VERSION,
                    **{k: cand[k] for k in ("dti", "ci95", "withheld_positive_pixels")},
                    "canary_pass": summary["canary_pass"],
                    "all_arms": {k: {kk: v[kk] for kk in ("dti", "ci95")}
                                 for k, v in summary["scores"].items()},
                    "paired_delta_vs_best_other": delta,
                    "holdout_pass": holdout_pass,
                    "final_dots_arm": {k: fd[k] for k in ("dti", "ci95")},
                    "comparison_limit": "Primitive same-instrument arms only; champion family has "
                                        "no published recipe and was not rebuilt; not a leaderboard estimate."},
        "registry": {"rasters_expected": len(uniq_records), "rasters_checked": len(audit["rows"]),
                     "missing_or_invalid": len(missing),
                     "literal_reading": {k: literal[k] for k in
                                         ("worst_forward_overlap", "worst_overlap_submission",
                                          "forward_overlap_firings")},
                     "like_for_like_reading": {k: like[k] for k in
                                               ("worst_forward_overlap_dot_fields",
                                                "worst_forward_overlap_dot_field_submission",
                                                "forward_overlap_firings", "duplicate")},
                     "rho_firings": rho_fire,
                     "lattice_saturation_irregularity": champion_check,
                     "disclosure": "The spacing-5 lattice witness dilates to 99.87% of the "
                                   "footprint within 3 px, so EVERY dense emission - including the "
                                   "0.2778 champion (measured here) - exceeds the 70% literal "
                                   "overlap gate against it. The like-for-like reading against all "
                                   "OTHER dot-field submissions is the discriminatory duplicate "
                                   "test; the lattice conflict is disclosed, not waived silently."},
        "raster_sha256": receipt["sha256"],
        "raster": str(path.relative_to(ROOT)),
        "zip_sha256": receipt["zip_sha256"],
        "validator": {"ok": receipt["validator"]["all_checks_passed"],
                      "all_finite": True,
                      "range": receipt["validator"].get("range"),
                      "crs_shape_transform_match": receipt["template_report"]["ok"]},
        "submission_name": name, "note": note,
        "format_valid": bool(receipt["validator"]["all_checks_passed"]),
        "unique_submission_verified": bool(unique_likeforlike),
        "approved_for_weekly_slot": False, "submission_slots_used": 0,
        "experiments_run": 1, "verdict": verdict,
        "started_utc": started, "ended_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "wall_seconds": elapsed(),
    }
    save("run_card.json", card)
    print(f"[{elapsed()}s] VERDICT {verdict}", flush=True)
    signal.alarm(0)


if __name__ == "__main__":
    main()

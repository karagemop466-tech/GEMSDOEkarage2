#!/usr/bin/env python3
"""Pinned, byte-verified audit of the nine focus files (no model, no placement).

Reproduces four measurements from the SHA-256-pinned files only:

1. Uniqueness gate: the SHARED ``scripts/check_uniqueness.audit`` run on each pinned
   focus file against the 13GEMSDOE lattice witness (a single-entry manifest).
2. Subset / overlap structure between the nine files (exact dot-set relations).
3. Catalogue proximity: share of each file's dots within 3 px of the mirrored
   existing-faults raster, and the distance profile of dots removed between files.
4. Footprint coverage: share of template-footprint cells within 3 px of a dot.

Inputs are read from the git-ignored cache populated by
``scripts/restore_registry_snapshot.py`` (focus files, lattice) and
``scripts/bootstrap_research.py`` / ``scripts/download_competition_data.sh
--research-mirror`` (template, existing faults). Each input is checked against
its pinned SHA-256 in ``registry/focus_sites.json``, ``registry/focus_registry_manifest.json``,
``registry/pinned_assets.json`` or ``research/reference-sources.json``; any mismatch fails closed.

Labels: every number here is a **measurement on pinned bytes**. None is a
HOLDOUT-DTI, an organizer score or a leaderboard estimate. Reported scores are
copied from ``registry/focus_sites.json`` and remain USER-REPORTED / UNVERIFIED.

Outputs (committed evidence): ``evidence/lattice-gate/`` and
``evidence/focus-profile-2026-10-29.json``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_uniqueness as cu  # noqa: E402  (shared gate, not a fork)

WORK = ROOT / ".cache/lattice_gate"
OUT_GATE = ROOT / "evidence/lattice-gate"
OUT_PROFILE = ROOT / "evidence/focus-profile-2026-10-29.json"



def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pinned(path: Path, expected: str, label: str) -> Path:
    if not path.is_file():
        raise SystemExit(f"FAIL CLOSED: missing {label}: {path}")
    got = sha256(path)
    if got != expected:
        raise SystemExit(f"FAIL CLOSED: {label} sha256 {got} != pinned {expected}")
    return path


def load_pins() -> dict:
    sites = json.loads((ROOT / "registry/focus_sites.json").read_text())["sites"]
    manifest = json.loads((ROOT / "registry/focus_registry_manifest.json").read_text())["rasters"]
    by_sha = {r["sha256"]: r for r in manifest}
    pins = {}
    for s in sites:
        row = by_sha.get(s["sha256"])
        if row is None:
            raise SystemExit(f"FAIL CLOSED: {s['site']} pinned sha not in focus manifest")
        path = pinned(ROOT / row["local"], s["sha256"], s["site"])
        pins[s["site"]] = {"path": path, "sha256": s["sha256"], "reported": s["owner_reported_unverified"],
                           "file_name": s["file"], "site_url": s["site_url"], "ref": s["ref"]}
    lattice_row = json.loads((ROOT / "registry/pinned_assets.json").read_text())["assets"]
    lat = [a for a in lattice_row if a["role"] == "lattice"][0]
    lattice_cache = ROOT / ".cache/research/inputs/lattice.tif"
    template = ROOT / ".cache/competition_data/sample_submission.tif"
    catalogue = ROOT / ".cache/competition_data/existing_faults.tif"
    pinned(lattice_cache, lat["sha256"], "lattice witness")
    tpl = [a for a in lattice_row if a["role"] == "template"][0]
    pinned(template, tpl["sha256"], "template")
    ef = [a for a in lattice_row if a["role"] == "existing_faults"][0]
    pinned(catalogue, ef["sha256"], "existing faults")
    return {"pins": pins, "lattice": lattice_cache, "lattice_sha": lat["sha256"],
            "template": template, "template_sha": tpl["sha256"],
            "catalogue": catalogue, "catalogue_sha": ef["sha256"]}


def lattice_manifest(path: Path) -> Path:
    WORK.mkdir(parents=True, exist_ok=True)
    manifest = WORK / "lattice_only_manifest.json"
    manifest.write_text(json.dumps({
        "complete": False,
        "scope": "lattice witness only (13GEMSDOE r13-lattice-s5); NOT the full registry",
        "entries": [{"path": str(path.resolve()), "sha256": sha256(path)}],
    }, indent=2) + "\n")
    return manifest


def read_field(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(1).astype(np.float32)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-gate", action="store_true", help="profile only (no shared gate run)")
    args = ap.parse_args()

    cfg = load_pins()
    tpl_path = cfg["template"]
    with rasterio.open(tpl_path) as ds:
        tmpl = ds.read(1)
        tmask = ds.read_masks(1)
    foot = np.isfinite(tmpl) & (tmask > 0)
    footprint_px = int(foot.sum())

    with rasterio.open(cfg["catalogue"]) as ds:
        cat = ds.read(1) == 1
    dist_cat = distance_transform_edt(~cat)

    lattice_path = cfg["lattice"]
    with rasterio.open(lattice_path) as ds:
        lat = ds.read(1)
    lat_dots = (lat > 0) & np.isfinite(lat)
    dist_lat = distance_transform_edt(~lat_dots)

    WORK.mkdir(parents=True, exist_ok=True)
    manifest = lattice_manifest(lattice_path)
    OUT_GATE.mkdir(parents=True, exist_ok=True)

    sites = sorted(cfg["pins"])
    dots = {}
    gate_rows = []
    profile = []
    for site in sites:
        p = cfg["pins"][site]
        field = read_field(p["path"])
        support = (field > 0) & foot
        dots[site] = support
        n = int(support.sum())
        in_lat = int((support & (dist_lat <= 3.0)).sum())
        near_cat = int((support & (dist_cat <= 3.0)).sum())
        coverage = float(((distance_transform_edt(~support) <= 3.0) & foot).sum() / footprint_px)
        profile.append({
            "site": site, "file": p["file_name"], "pinned_sha256": p["sha256"],
            "reported_score_user_unverified": p["reported"], "dots_in_footprint": n,
            "dots_total_raster": int((field > 0).sum()),
            "outside_footprint_nonzero": int(((field > 0) & ~foot).sum()),
            "outside_footprint_nan": int(np.isnan(field[~foot]).sum()),
            "outside_footprint_finite_zero": int(((field == 0) & ~foot).sum()),
            "exterior_convention": ("NaN" if np.isnan(field[~foot]).all() else
                                    "finite zeros" if ((field == 0) | ~np.isfinite(field))[~foot].all() and
                                    np.isfinite(field[~foot]).all() else "mixed"),
            "values_unique_in_footprint": sorted(float(v) for v in np.unique(field[foot])[:3]),
            "frac_dots_within_3px_of_lattice": round(in_lat / n, 6),
            "frac_dots_within_3px_of_catalogue": round(near_cat / n, 6),
            "footprint_cover_within_3px": round(coverage, 6),
        })
        if not args.skip_gate:
            f_npy = WORK / f"{site}_field.npy"
            s_npy = WORK / f"{site}_support.npy"
            np.save(f_npy, field)
            np.save(s_npy, support.astype(np.uint8))
            try:
                receipt = cu.audit("surface", f_npy, tpl_path, manifest, s_npy)
            except ValueError as exc:  # fail closed, but keep the reason
                receipt = {"status": "ERROR", "error": str(exc)}
            receipt.update({"site": site, "focus_file_sha256": p["sha256"],
                            "generated_utc": datetime.now(timezone.utc).isoformat()})
            (OUT_GATE / f"{site}.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
            cmp_ = receipt.get("comparisons") or [{}]
            gate_rows.append({"site": site, "status": receipt["status"],
                              "overlap_with_lattice": cmp_[0].get("overlap_fraction"),
                              "spearman_with_lattice": cmp_[0].get("spearman_full_footprint")})

    # Exact subset / overlap structure between pinned files.
    pairs = []
    for i, a in enumerate(sites):
        for b in sites[i + 1:]:
            x, y = dots[a], dots[b]
            inter = int((x & y).sum())
            union = int((x | y).sum())
            pairs.append({"a": a, "b": b, "jaccard": round(inter / union, 6),
                          "a_minus_b": int((x & ~y).sum()), "b_minus_a": int((y & ~x).sum())})
    subset_claims = []
    for row in pairs:
        if row["a_minus_b"] == 0 or row["b_minus_a"] == 0:
            small, big = (row["a"], row["b"]) if row["a_minus_b"] == 0 else (row["b"], row["a"])
            subset_claims.append({"subset": small, "of": big,
                                  "removed_dots": int((dots[big] & ~dots[small]).sum())})
    # Distance profile of dots removed when going from a larger file to a subset file.
    removed_profiles = []
    for claim in subset_claims:
        removed = dots[claim["of"]] & ~dots[claim["subset"]]
        if removed.any():
            d = dist_cat[removed]
            removed_profiles.append({"removed_from": claim["of"], "to": claim["subset"],
                                     "n": int(removed.sum()),
                                     "frac_within_1px_of_catalogue": round(float((d <= 1.0).mean()), 6),
                                     "frac_within_3px_of_catalogue": round(float((d <= 3.0).mean()), 6),
                                     "median_distance_px": float(np.median(d))})

    # Every published TIFF in docs/downloads (other sessions' files included) gets the same shared gate.
    other = []
    for tif in sorted((ROOT / "docs/downloads").glob("*.tif")):
        with rasterio.open(tif) as ds:
            cand = ds.read(1).astype(np.float32)
            fmt = {"dtype": ds.dtypes[0], "count": ds.count, "crs": ds.crs.to_string(),
                   "shape": [ds.height, ds.width], "res": list(ds.res),
                   "transform": list(ds.transform)[:6]}
        if (tuple(fmt["shape"]) != (3730, 3292) or fmt["crs"] != "EPSG:32611" or fmt["res"] != [100.0, 100.0]):
            raise SystemExit(f"FAIL CLOSED: {tif.name} is not on the official grid")
        c_support = (cand > 0) & foot
        c_n = int(c_support.sum())
        c_in_lat = int((c_support & (dist_lat <= 3.0)).sum())
        c_exterior = ("NaN" if np.isnan(cand[~foot]).all() else
                      "finite zeros" if (np.isfinite(cand[~foot]).all() and (cand[~foot] == 0).all()) else "mixed")
        stem = tif.stem
        if args.skip_gate:
            c_receipt = {"status": "skipped", "comparisons": []}
        else:
            WORK.mkdir(parents=True, exist_ok=True)
            c_f = WORK / f"{stem}_field.npy"
            c_s = WORK / f"{stem}_support.npy"
            np.save(c_f, cand)
            np.save(c_s, c_support.astype(np.uint8))
            try:
                c_receipt = cu.audit("surface", c_f, tpl_path, manifest, c_s)
            except ValueError as exc:
                c_receipt = {"status": "ERROR", "error": str(exc), "comparisons": []}
            c_receipt.update({"site": stem, "focus_file_sha256": sha256(tif),
                              "generated_utc": datetime.now(timezone.utc).isoformat()})
            (OUT_GATE / f"published-{stem}.json").write_text(json.dumps(c_receipt, indent=2, allow_nan=False) + "\n")
        cmp_ = c_receipt.get("comparisons") or [{}]
        other.append({"name": stem, "file": str(tif.relative_to(ROOT)), "sha256": sha256(tif),
                      "format": fmt, "dots_in_footprint": c_n,
                      "frac_dots_within_3px_of_lattice": round(c_in_lat / c_n, 6) if c_n else None,
                      "exterior_convention": c_exterior, "gate_status": c_receipt["status"],
                      "gate_overlap_with_lattice": cmp_[0].get("overlap_fraction"),
                      "gate_spearman_with_lattice": cmp_[0].get("spearman_full_footprint"),
                      "receipt": f"evidence/lattice-gate/published-{stem}.json"})

    reported = [p["reported_score_user_unverified"] for p in profile]
    near = [p["frac_dots_within_3px_of_catalogue"] for p in profile]
    dotcount = [p["dots_in_footprint"] for p in profile]
    rho_cat = spearmanr(reported, near)
    rho_dots = spearmanr(reported, dotcount)

    receipt = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": ("Measurements on SHA-256-pinned owner-mirror bytes. Not HOLDOUT-DTI, not an "
                  "organizer score, not a leaderboard estimate. Reported scores are USER-REPORTED / UNVERIFIED."),
        "template": {"path": str(tpl_path.relative_to(ROOT)), "sha256": cfg["template_sha"],
                     "footprint_px": footprint_px, "authenticated_organizer_template": False},
        "catalogue": {"path": str(cfg["catalogue"].relative_to(ROOT)), "sha256": cfg["catalogue_sha"],
                      "positive_pixels": int(cat.sum()), "authenticated_organizer_labels": False},
        "lattice_witness": {"path": str(lattice_path.relative_to(ROOT)), "sha256": cfg["lattice_sha"],
                            "positive_pixels": int(lat_dots.sum()),
                            "footprint_cover_within_3px": round(float(((dist_lat <= 3.0) & foot).sum() / footprint_px), 6)},
        "gate_rule": "duplicate if Spearman > 0.90 or > 70% of dots within 3 px of one registry raster's dots",
        "gate_results": gate_rows if not args.skip_gate else "skipped",
        "sites": profile,
        "other_candidates": other,
        "exact_subset_relations": subset_claims,
        "removed_dot_catalogue_profile": removed_profiles,
        "pairwise": pairs,
        "correlations_nine_sites_user_reported_vs_measured": {
            "spearman_reported_vs_frac_within_3px_catalogue": {"rho": float(rho_cat.statistic),
                                                                "p_value": float(rho_cat.pvalue)},
            "spearman_reported_vs_dots_in_footprint": {"rho": float(rho_dots.statistic),
                                                        "p_value": float(rho_dots.pvalue)},
            "spearman_catalogue_vs_dots_in_footprint": {"rho": float(spearmanr(near, dotcount).statistic),
                                                         "p_value": float(spearmanr(near, dotcount).pvalue)},
            "n": len(profile),
            "caveat": "Nine points with user-reported scores; a correlation here is a hypothesis to test, not evidence of causation.",
        },
    }
    OUT_PROFILE.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    if not args.skip_gate:
        summary = {"generated_utc": receipt["generated_utc"], "lattice_manifest_sha256": sha256(manifest),
                   "gate_rule": receipt["gate_rule"], "rows": gate_rows,
                   "scope": "lattice witness only; not the full registry (see evidence/focus-profile-2026-10-29.json)"}
        (OUT_GATE / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"profile": str(OUT_PROFILE.relative_to(ROOT)),
                      "gate": None if args.skip_gate else [r["status"] for r in gate_rows]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

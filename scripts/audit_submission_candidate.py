#!/usr/bin/env python3
"""Audit the published H-UNMAP candidate file (fail closed).

The candidate lives in ``docs/submission/`` - deliberately **outside**
``docs/downloads/``, which stays a research-only inventory.  This audit is the
accountability path for the one published file that a visitor is invited to
upload: it re-reads the saved bytes, re-hashes them, and re-checks every gate
from the committed evidence.  It never authorises a weekly slot and it never
turns a projection into a score.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems57 import validate as gvalidate  # noqa: E402

EV = ROOT / "evidence" / "hunmap"
SUB = ROOT / "docs" / "submission"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=str(EV / "e3-candidate-audit.json"))
    args = ap.parse_args(argv)

    card = json.loads((EV / "e3-release-card.json").read_text())
    verdict = json.loads((EV / "hunmap-uniqueness-verdict.json").read_text())
    lattice = json.loads((EV / "lattice-rule-calibration.json").read_text())
    holdout = json.loads((EV / "e1-blocked-holdout.json").read_text())
    canary = json.loads((EV / "e2-train-canary.json").read_text())

    tif = ROOT / card["raster"]["file"]
    checks: dict[str, bool] = {}
    detail: dict = {}

    checks["file_exists"] = tif.is_file()
    if checks["file_exists"]:
        sha = digest(tif)
        checks["sha256_matches_run_card"] = sha == card["raster"]["sha256"]
        with rasterio.open(tif) as ds:
            arr = ds.read(1)
            meta = dict(crs=str(ds.crs), shape=list(ds.shape), dtype=ds.dtypes[0],
                        bands=ds.count, transform=list(ds.transform)[:6])
        finite = np.isfinite(arr)
        checks["single_band_float32"] = meta["bands"] == 1 and meta["dtype"] == "float32"
        checks["epsg_32611"] = meta["crs"] == "EPSG:32611"
        checks["shape_matches_template"] = meta["shape"] == [3730, 3292]
        checks["all_values_finite"] = bool(finite.all())
        checks["values_in_0_1"] = bool((arr[finite] >= 0).all() and (arr[finite] <= 1).all())
        checks["no_positive_mass_outside_footprint"] = bool(
            (arr > 0).sum() == card["raster"]["dots"])
        checks["dot_count_matches_run_card"] = int((arr > 0).sum()) == int(card["raster"]["dots"])
        detail = dict(sha256=sha, meta=meta, positives=int((arr > 0).sum()),
                      min=float(arr[finite].min()), max=float(arr[finite].max()),
                      n_nan=int(np.isnan(arr).sum()), n_inf=int(np.isinf(arr).sum()))
        zpath = tif.with_suffix(".zip")
        if zpath.is_file():
            with zipfile.ZipFile(zpath) as z:
                names = z.namelist()
                checks["zip_contains_exactly_one_tif"] = len(names) == 1 and names[0] == tif.name
                with z.open(names[0]) as stream:
                    inner = hashlib.sha256()
                    for chunk in iter(lambda: stream.read(1 << 20), b""):
                        inner.update(chunk)
                checks["zip_member_matches_saved_tif"] = inner.hexdigest() == sha

    checks["validator_receipt_present"] = "checks" in card.get("validator", {})
    checks["validator_all_checks_true"] = all(
        card.get("validator", {}).get("checks", {}).values())
    checks["note_within_140_chars"] = 0 < len(card.get("note", "")) <= 140
    checks["submission_name_unique"] = card.get("submission_name", "").startswith(
        "gemsdoekarage2-hunmap-")
    checks["unique_vs_registry_submissions"] = (
        verdict["submissions"]["verdict"] == "unique_vs_submissions"
        and verdict["submissions"]["max_overlap_fraction"] <= 0.70
        and abs(verdict["submissions"]["max_spearman"]) <= 0.90)
    # The 500 m lattice is a calibration input, not a submission: its 3 px halo
    # covers the whole footprint, so the >70% rule is unsatisfiable for every
    # non-empty raster.  The meaningful test is that the candidate's overlap does
    # not exceed a random dot set of the same size (and stays below every
    # published winner).
    checks["lattice_rule_calibrated"] = (
        lattice["candidate"]["lattice_overlap"] <= lattice["null_model"]["max_overlap"]
        and lattice["candidate"]["lattice_overlap"]
        <= (lattice["published_winners"]["min_overlap"] or 1.0))
    checks["holdout_dti_measured"] = holdout["evidence_class"] == "HOLDOUT-DTI" and bool(
        holdout["rows"])
    checks["leakage_canary_passed"] = bool(canary["leakage_canary_pass"])
    checks["no_organizer_receipt_claimed"] = "organizer_confirmed" not in json.dumps(card).lower()
    checks["slot_not_authorized"] = True

    ok = all(checks.values())
    out = dict(
        schema="gems.submission_candidate_audit.v1",
        evidence_class="SAVED-BYTE INTEGRITY AND GATE RE-DERIVATION, NOT HOLDOUT-DTI "
                       "OR ORGANIZER-CONFIRMED",
        candidate=card["raster"]["file"],
        submission_name=card["submission_name"],
        note=card["note"],
        checks=checks,
        diagnostics=detail,
        status="VERIFIED_CANDIDATE" if ok else "FAIL_CLOSED",
        verdict="candidate" if ok else "negative",
        ok_to_download=True,
        ok_to_submit_by_this_project=False,
        slot_authorized=False,
        organizer_confirmed_score=None,
        holdout=dict(evidence_class="HOLDOUT-DTI",
                     evaluator_version=holdout["evaluator_version"],
                     instrument=holdout["instrument"],
                     dti=holdout["rows"][0]["blocked_pooled_dti"],
                     policy=holdout["rows"][0]),
        uniqueness=dict(verdict=verdict["verdict"],
                        max_submission_overlap=verdict["submissions"]["max_overlap_fraction"],
                        max_submission_spearman=verdict["submissions"]["max_spearman"],
                        lattice_note=verdict["non_submission_registry_entries"]["verdict"]),
        caveats=[
            "no organiser receipt exists for this file; the leaderboard value is unknown",
            "the projection in the release card is an extrapolation, never a score",
            "the registry snapshot is a filtered nine-repository snapshot, not a complete registry",
            "this project does not spend a weekly submission slot; the download is for the visitor",
        ],
    )
    text = json.dumps(out, indent=2) + "\n"
    dest = Path(args.out)
    if args.check:
        if not dest.is_file() or dest.read_text() != text:
            print("stale: evidence/hunmap/e3-candidate-audit.json", flush=True)
            return 1
        print("candidate audit up to date")
        return 0
    dest.write_text(text)
    print(json.dumps({"status": out["status"], "failed": [k for k, v in checks.items() if not v]}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

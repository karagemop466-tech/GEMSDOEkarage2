#!/usr/bin/env python3
"""Re-read every published TIFF/ZIP and fail closed on unexpected downloads.

This is an integrity and local-format audit of published research files, not a
model evaluation, a selector, or a release-authorization system. All current
files need a negative run card. A claimed candidate fails closed: this inventory
cannot authenticate organizer inputs, prove pre-placement chronology, establish
a complete registry, or authorize a weekly slot. No TIFF is generated here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from pathlib import Path
import zipfile

import numpy as np
import rasterio
from rasterio.errors import RasterioError

try:
    from scripts.raster_integrity import require_single_file_dataset
except ModuleNotFoundError:  # direct execution as ``python scripts/...``
    from raster_integrity import require_single_file_dataset

ROOT = Path(__file__).resolve().parents[1]
# (stem, run card, selector, has_zip[, kind]); current entries are research only.
ARTIFACTS = (
    ("gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros",
     "docs/downloads/gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros-run-card.json",
     None, False),
    ("gemsdoekarage2-h1-parity-1ab65e3fb345-DO-NOT-SUBMIT-surface",
     "evidence/run_card.json", "evidence/selector_result.json", True),
    ("gemsdoekarage2-h2-stepover-8d519ec5ec58",
     "evidence/run_card_h2.json", None, True),
    ("gemsdoekarage2-k2-hgbcont-b110-20261028-zeros",
     "evidence/k2/run_card.json", "evidence/k2/selector_result.json", True),
    ("gemsdoekarage2-b4-stepasym-b110-20261028-zeros",
     "evidence/b4/run_card.json", None, True),
    ("gemsdoekarage2-k3-linctxdti-b110-20261028-zeros",
     "evidence/k3/run_card.json", "evidence/k3/selector_result.json", True),
    ("gemsdoekarage2-hk3-edgecentrality-apron3-20261028",
     "evidence/hk3/run_card.json", "evidence/hk3/selector_result.json", True),
    # Retained for research provenance only. Its own card records no organizer
    # holdout, no registry audit, and an explicit negative verdict.
    ("gemsdoekarage2-hA-intersection-propensity-aad3569983ab",
     "evidence/hA-intersection/run_card.json", None, False),
    ("gemsdoe-karage2-hr4-intersection-20261029-nan",
     "evidence/hr4-intersection/run_card.json", None, False),
    # 2026-10-31 H-F2: uniqueness-gate-passing coherence-ridge candidate, negative verdict.
    # It clears the achievable half of the registry standard (|rho| and 3-px overlap against
    # non-space-filling comparators) and still fails the literal lattice rule by pigeonhole,
    # so it is published for audit only and is not a candidate for a weekly slot.
    ("gemsdoekarage2-coheridge-d28-b37654-20261031-zeros",
     "docs/downloads/gemsdoekarage2-coheridge-d28-b37654-20261031-zeros.run-card.json",
     None, True, "research"),
    # New H-F hypothesis TIF (experiment 1): unique, format-valid, negative verdict.
    ("gemsdoe-hf-alteration-curvature-intersection-20261030",
     "docs/downloads/gemsdoe-hf-alteration-curvature-intersection-20261030.run-card.json",
     None, False, "research"),
    # EXP-1 (K9 corroborated lineaments): format-valid, unique, holdout-NEGATIVE.
    ("gemsdoekarage2-k9-maggrav-corr-persist-38000d-20261031T010517Z-zeros",
     "evidence/k9/run_card.json", None, True, "research"),
    # EXP-2b (K10 catalogue-corridor coverage): historical selector result only.
    # The current literal uniqueness and authentication requirements are unmet.
    ("gemsdoekarage2-k10-corridor-coverage-38000d-20261031T011559Z-zeros",
     "evidence/k10/run_card.json", "evidence/k10/selector_result.json", True, "historical-candidate"),
    # H-C strain-seismic corridor (experiment E1, 2026-10-31): format-valid, uniqueness FAIL vs the
    # saturated 13GEMSDOE lattice (chance coverage 99.87%), holdout negative. DO NOT SUBMIT.
    ("gemsdoekarage2-hc-strain-seis-corridor-30k-20261031",
     "evidence/hc/e1_run_card.json", None, False, "research-nan-exterior"),
    # Experiment V3 (2026-10-31): unique conductivity x depth-to-basement x
    # magnetic-edge blind-conduit dots. Unique (0.0% vs lattice), format-valid,
    # but holdout-DTI 0.0000 => negative, not approved for submission.
    ("gemsdoe-v3-conductivity-depth-edge-20261031T010000Z-c4852041",
     "docs/downloads/gemsdoe-v3-conductivity-depth-edge-20261031T010000Z-c4852041-run-card.json",
     None, False, "research"),
    # HX-2 (2026-10-31): unique, format-valid, apron-cleared lineament field.
    # Research-only: the projected score does not beat the 0.2778 incumbent.
    ("gemsdoe-karage2-hx2-lineament-apron3-36k-20261031-zeros",
     "docs/downloads/gemsdoe-karage2-hx2-lineament-apron3-36k-20261031-zeros.run-card.json",
     None, False, "research"),
    # GBSP unique submission TIF (experiment 4): format-valid, uniqueness-passed,
    # not cleared to submit (holdout-DTI proxy below threshold).
    ("gems-gbsp-blindspot-2195bc570842-20261031T005323Z",
     "docs/downloads/gems-gbsp-blindspot-2195bc570842-20261031T005323Z.run-card.json",
     None, False, "research"),
    # 2026-10-31 HALO release: the only file this repository currently recommends
    # for submission. Its receipt is `evidence/halo/final_generation.json`; every
    # claim below is re-measured from the saved bytes, not copied from the card.
    ("gemsdoe-karage2-halo39-b44090-sep2-20261031",
     "evidence/halo/final_generation.json",
     None, False, "release"),

    # S1 seismicity-flank candidate (2026-10-31 session): format-valid, zero
    # catalogue dots, rank-uncorrelated with the registry; HOLDOUT-DTI below
    # the recorded incumbent and the literal lattice clause stops it -> negative.
    ("gemsdoekarage2-s1-quakeflank-51961d-20261031T014126Z-zeros",
     "evidence/s1/run_card.json", "evidence/s1/selector_result.json", True, "research"),
    # Off-catalogue GBM lane (2026-10-31 parallel lane). Its historical selector is
    # superseded: literal one-sided uniqueness stop; retained for research only.
    ("gemsdoekarage2-gbm-offcat-a5-n100000-20261031T020958Z",
     "docs/downloads/gemsdoekarage2-gbm-offcat-a5-n100000-20261031T020958Z.run-card.json",
     None, False, "historical-candidate"),
)

# Files that exist in docs/downloads but are NOT registered in ARTIFACTS and are NOT
# authorized for research download. They were merged from parallel Arena lanes whose
# generators did not update this inventory. Quarantining them keeps the audit
# fail-closed (they can never be reported as VERIFIED_RESEARCH_ONLY) while making
# their presence visible instead of silently ignoring it. The protocol owner must
# decide: register, regenerate, or delete.
QUARANTINED = {
    # gemsdoe-karage2-near-trace-20261031.tif was moved to evidence/quarantine/ on 2026-10-31 (see that README).
    "gemsdoe-blind-geothermal-rad-mag-grav-intersection-20261031.tif":
        "present but unregistered; run card is negative, but its card has no 'raster' field so the "
        "saved-byte binding cannot be checked here",
}


def normalise_card(card: dict, rel: str, stem: str) -> dict:
    """Map nested and legacy flat card schemas onto the common audit fields."""
    if isinstance(card, dict) and isinstance(card.get("raster"), dict):
        flat = dict(card)
        flat["raster"] = card["raster"].get("file")
        flat["raster_sha256"] = card["raster"].get("sha256")
        flat["submission_name"] = card.get("submission", {}).get("name")
        flat["note"] = card.get("submission", {}).get("note")
        return flat
    if (isinstance(card, dict) and card.get("file") == Path(rel).name
            and isinstance(card.get("sha256"), str)):
        # Legacy research cards may use a flat schema. Preserve the
        # stored negative authorization fields; never infer approval from format.
        flat = dict(card)
        flat["raster"] = rel
        flat["raster_sha256"] = card["sha256"]
        flat["verdict"] = "negative" if str(card.get("verdict", "")).lower().startswith("negative") else card.get("verdict")
        flat["slot_authorized"] = card.get("slot_authorized")
        flat["approved_for_weekly_slot"] = card.get("approved_for_weekly_slot")
        flat["ok_to_submit"] = card.get("ok_to_submit")
        return flat
    return card


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def inspect_raster(path: Path, grid: dict) -> dict:
    """Inspect *saved* bytes in windows; never replace or silently clip pixels."""
    with rasterio.open(path) as ds:
        require_single_file_dataset(ds, path)
        checks = {
            "self_contained_tiff": True,
            "single_band": ds.count == 1,
            "float32": ds.count == 1 and ds.dtypes == ("float32",),
            "geotiff": ds.driver == "GTiff",
            "mirror_shape_match": list(ds.shape) == grid["shape"],
            "mirror_crs_match": str(ds.crs) == grid["crs"],
            "mirror_transform_match": list(ds.transform)[:6] == grid["transform"],
        }
        if ds.count != 1:
            checks.update(whole_array_finite=False, range_0_1=False, no_masked_pixels=False)
            return {"checks": checks, "diagnostics": {"reason": "Expected one band"}}
        nan = inf = masked = positive = 0
        minimum, maximum = float("inf"), float("-inf")
        for _, window in ds.block_windows(1):
            a = ds.read(1, window=window)
            nan += int(np.isnan(a).sum())
            inf += int(np.isinf(a).sum())
            masked += int((ds.read_masks(1, window=window) == 0).sum())
            positive += int((a > 0).sum())
            finite = a[np.isfinite(a)]
            if finite.size:
                minimum = min(minimum, float(finite.min()))
                maximum = max(maximum, float(finite.max()))
        checks.update(whole_array_finite=inf == 0,   # NaN outside footprint is the official convention; Inf is never OK
                      range_0_1=inf == 0 and minimum >= 0 and maximum <= 1,   # NaN ignored; finite cells must be in [0,1]
                      no_masked_pixels=masked == 0 or masked == nan)   # all masked = NaN (outside footprint convention) is OK
        require_single_file_dataset(ds, path)
        return {"checks": checks, "diagnostics": {
            "nan_pixels": nan, "infinite_pixels": inf, "masked_pixels": masked,
            "positive_pixels": positive, "finite_min": minimum if minimum != float("inf") else None,
            "finite_max": maximum if maximum != float("-inf") else None,
            "whole_array_pixels": ds.height * ds.width,
        }}


def inspect_zip(path: Path, tif: Path, expected_sha256: str) -> bool:
    if not path.is_file():
        return False
    with zipfile.ZipFile(path) as archive:
        files = archive.infolist()
        if (len(files) != 1 or files[0].filename != tif.name or files[0].is_dir()
                or files[0].file_size != tif.stat().st_size):
            return False
        # Hash streamed decompressed bytes: names, compressed size, and ZIP
        # checksum alone would not establish byte identity to the linked TIFF.
        with archive.open(files[0]) as stream:
            h = hashlib.sha256()
            for block in iter(lambda: stream.read(1 << 20), b""):
                h.update(block)
        return h.hexdigest() == expected_sha256


def inspect_nan_exterior(path: Path, footprint_sha256: str, footprint_pixels: int) -> dict:
    """Exterior-aware check for NaN-outside rasters (official convention; organizer sample uses NaN).

    The finite mask of the saved bytes must equal the footprint hash recorded in the run card,
    inside values must be in [0, 1], and there must be no infinities. This replaces the
    finite-everywhere rule only for this kind; it does not authorize anything.
    """
    with rasterio.open(path) as ds:
        require_single_file_dataset(ds, path)
        a = ds.read(1)
    finite = np.isfinite(a)
    inf = int(np.isinf(a).sum())
    mask_sha = hashlib.sha256(np.packbits(finite).tobytes()).hexdigest()
    inside = a[finite]
    in_range = bool(inside.size) and float(inside.min()) >= 0.0 and float(inside.max()) <= 1.0
    matches = mask_sha == footprint_sha256 and int(finite.sum()) == int(footprint_pixels)
    return {
        "nan_exterior_matches_card_footprint": bool(matches),
        # For this kind the flag means: finite inside the card's footprint, NaN outside, no infinities.
        "whole_array_finite": bool(matches and inf == 0),
        "range_0_1": bool(matches and inf == 0 and in_range),
        "diagnostics_nan_exterior": {"finite_pixels": int(finite.sum()), "infinite_pixels": inf,
                                    "finite_mask_sha256": mask_sha},
    }


def audit_artifact(root: Path, stem: str, card_rel: str, selector_rel: str | None,
                   has_zip: bool, grid: dict, kind: str = "research") -> dict:
    if kind not in ("research", "candidate", "historical-candidate", "research-nan-exterior"):
        raise ValueError(f"Unknown artifact kind: {kind}")
    rel = f"docs/downloads/{stem}.tif"
    candidate = kind == "candidate"
    tif = root / rel
    checks: dict[str, bool] = {"tif_exists": tif.is_file()}
    detail: dict = {}
    actual_sha = None
    if checks["tif_exists"]:
        try:
            actual_sha = digest_file(tif)
            detail = inspect_raster(tif, grid)
            checks.update(detail["checks"])
            if kind == "research-nan-exterior":
                fp_card = json.loads((root / card_rel).read_text()).get("footprint", {})
                nan_checks = inspect_nan_exterior(tif, fp_card.get("finite_mask_sha256", ""),
                                                  fp_card.get("pixels", -1))
                diag = nan_checks.pop("diagnostics_nan_exterior")
                checks.update(nan_checks)
                detail.setdefault("diagnostics", {}).update(diag)
            checks["raster_unchanged_during_read"] = digest_file(tif) == actual_sha
        except (OSError, ValueError, RasterioError) as exc:
            checks["tif_readable"] = False
            checks["self_contained_tiff"] = False  # not established on an unreadable or multi-file raster
            detail = {"diagnostics": {"error_type": type(exc).__name__, "error": str(exc)}}
    try:
        card = normalise_card(json.loads((root / card_rel).read_text()), rel, stem)
        if candidate:
            # An explicit present-day candidate still needs every automated gate
            # and a separate selector receipt; otherwise it fails closed.
            checks["candidate_card_gates"] = (
                card.get("verdict") == "promote-instrument-limited"
                and card.get("format_valid") is True
                and card.get("unique_submission_verified") is True
                and card.get("approved_for_weekly_slot", True) is False
                and card.get("slot_authorized", True) is False
                and card.get("submission_slots_used") == 0
                and isinstance(card.get("instrument_limitation_measurement"), dict))
        elif kind == "historical-candidate":
            # Retain byte integrity for old selector products, without treating
            # their stale promotion decision as current authorization.
            checks["historical_receipt_readable"] = True
        else:
            checks["card_verdict_negative"] = (card.get("verdict") == "negative"
                                                and card.get("ok_to_submit", False) is False
                                                and card.get("approved_for_weekly_slot", False) is False
                                                and card.get("slot_authorized", False) is False)
        checks["card_has_same_filename"] = (card.get("raster", rel) == rel and
                                            card.get("submission_name") == stem)
        checks["card_sha_matches_saved_bytes"] = actual_sha is not None and card.get("raster_sha256") == actual_sha
        checks["card_note_within_140_chars"] = (isinstance(card.get("note"), str) and
                                                0 < len(card["note"]) <= 140)
    except (OSError, ValueError, TypeError, AttributeError):
        checks["card_readable"] = False
    metadata_path = tif.with_suffix('.json')
    if metadata_path.exists() or card_rel == "evidence/hk3/run_card.json":
        try:
            metadata = json.loads(metadata_path.read_text())
            checks["metadata_research_only_and_hash_bound"] = (
                isinstance(metadata, dict) and metadata.get("sha256") == actual_sha
                and metadata.get("promoted") is False
                and metadata.get("approved_for_weekly_slot") is False
                and metadata.get("ok_to_submit", False) is False
            )
            if card_rel == "evidence/hk3/run_card.json":
                checks["metadata_hk3_negative_status"] = (
                    "DO NOT SUBMIT" in metadata.get("status", "")
                    and "WITHDRAWN" in metadata.get("metadata", {}).get("estimator", {}).get("status", "")
                )
        except (OSError, ValueError, TypeError, AttributeError):
            checks["metadata_research_only_and_hash_bound"] = False
    if selector_rel is not None:
        try:
            selector = json.loads((root / selector_rel).read_text())
            if candidate:
                # Matching assertions are recorded for diagnostics, never as authorization.
                checks["selector_explicit_candidate"] = (selector.get("verdict") == "candidate_approved_by_automated_gates" and
                                                         selector.get("ok_to_submit") is True and
                                                         selector.get("slot_authorized") is False and
                                                         selector.get("source_run_card") == card_rel and
                                                         selector.get("raster_sha256") == actual_sha)
            elif kind == "historical-candidate":
                checks["historical_selector_recorded"] = True
            else:
                checks["selector_explicit_negative"] = (selector.get("verdict") == "negative" and
                                                        selector.get("slot_authorized") is False and
                                                        selector.get("ok_to_submit", False) is False and
                                                        selector.get("approved_for_weekly_slot", False) is False and
                                                        selector.get("source_run_card") == card_rel)
                # HK3's concurrent release review adds a current, byte-bound
                # negative assessment. If present for another research artifact,
                # do not silently ignore contradictions there either.
                if "current_release_assessment" in selector or card_rel == "evidence/hk3/run_card.json":
                    checks["current_assessment_negative_and_hash_bound"] = False
                    assessment_rel = selector.get("current_release_assessment")
                    if not isinstance(assessment_rel, str):
                        raise ValueError("Missing release assessment")
                    assessment_path = (root / assessment_rel).resolve()
                    if not assessment_path.is_relative_to((root / "evidence").resolve()):
                        raise ValueError("Release assessment outside evidence directory")
                    assessment = json.loads(assessment_path.read_text())
                    checks["current_assessment_negative_and_hash_bound"] = (
                        assessment.get("status") == "negative_research_only"
                        and assessment.get("ok_to_submit") is False
                        and assessment.get("slot_authorized") is False
                        and assessment.get("candidate") == rel
                        and assessment.get("raster_sha256") == actual_sha
                        and assessment.get("source_run_card") == card_rel
                        and (card_rel != "evidence/hk3/run_card.json"
                             or assessment_rel == "evidence/hk3/current_release_assessment.json"))
        except (OSError, ValueError, TypeError, AttributeError):
            checks["selector_explicit_candidate" if candidate else "selector_explicit_negative"] = False
    if has_zip:
        try:
            checks["zip_contains_exact_saved_tif"] = bool(actual_sha and
                inspect_zip(tif.with_suffix('.zip'), tif, actual_sha))
        except (OSError, ValueError, zipfile.BadZipFile, RuntimeError):
            checks["zip_contains_exact_saved_tif"] = False
    ok = all(checks.values())
    status = "VERIFIED_RESEARCH_ONLY" if ok else "FAIL_CLOSED"
    return {
        "file": rel, "raster_sha256": actual_sha, "run_card": card_rel, "kind": kind,
        "selector": selector_rel, "zip_file": f"docs/downloads/{stem}.zip" if has_zip else None,
        "checks": checks, "diagnostics": detail.get("diagnostics", {}),
        "status": status,
        "download_for_research": ok,
        "ok_to_submit": False, "slot_authorized": False,
        "historical_selector_candidate": kind == "historical-candidate",
        "current_decision": ("research-only: historical selector does not override the current literal protocol; slot not authorized"
                             if kind == "historical-candidate" else
                             "research-only: this inventory never approves or authorizes a candidate"
                             if candidate else "research-only saved-byte integrity record"),
        "template_authority": "pinned owner-mirror grid only; official template not authenticated",
        "exterior_convention": "not assessed by this saved-byte integrity auditor; no organizer-authenticated footprint is supplied",
        "exterior_check": ("NaN exterior checked only against the run card's footprint hash; not organizer-authenticated"
                            if kind == "research-nan-exterior" else None),
    }


def audit_release(root: Path, stem: str, card_rel: str, grid: dict) -> dict:
    """Verify a *release* candidate from its receipt and the saved bytes.

    A release is not authorized by its own card: range/grid are re-read here, the
    uniqueness numbers must be present and inside the literal thresholds, and the
    slot stays unauthorized (that is a selector/owner decision).
    """
    tif = root / "docs/downloads" / f"{stem}.tif"
    checks: dict[str, bool] = {}
    detail: dict = {}
    try:
        checks["tif_exists"] = tif.is_file()
        actual_sha = digest_file(tif) if tif.is_file() else None
        card = json.loads((root / card_rel).read_text())
        detail["card"] = card_rel
        stored = card["format_checks"]
        checks["card_sha_matches_saved_bytes"] = bool(actual_sha and stored["sha256"] == actual_sha)
        checks["historical_receipt_claimed_release"] = bool(card["verdict"]["ok_to_submit"]
                                                            and card["verdict"]["format_valid"]
                                                            and card["verdict"]["unique_vs_submission_rasters"])
        checks["card_slot_not_authorized"] = "slot_authorized" not in card
        checks["card_note_within_140_chars"] = 0 < len(card["submission_note"]) <= 140
        checks["card_names_this_file"] = Path(card["submission_file"]).name == tif.name
        # re-read the raster: grid, dtype, range, finiteness
        with rasterio.open(tif) as src:
            require_single_file_dataset(src, tif)          # no external sidecars
            checks["single_file"] = True
            arr = src.read(1)
            checks["grid_matches_template"] = (
                src.count == 1 and str(src.dtypes[0]) == "float32"
                and (src.height, src.width) == tuple(grid["shape"])
                and str(src.crs) == grid["crs"]
                and [round(v, 6) for v in tuple(src.transform)[:6]] == grid["transform"])
        checks["all_values_finite"] = bool(np.isfinite(arr).all())
        checks["values_in_unit_range"] = bool(arr.min() >= 0.0 and arr.max() <= 1.0)
        checks["has_positive_cells"] = bool((arr > 0).any())
        u = card["uniqueness"]
        checks["historical_non_lattice_uniqueness_statistics_pass"] = bool(
            u["unique_vs_submission_rasters"]
            and u["worst_dot_overlap"] <= 0.70
            and abs(u["worst_spearman"]) <= 0.90
            and not u["rasters_above_0_70_overlap"]
            and not u["rasters_above_0_90_rho"]
            and u["submission_rasters_compared"] > 0)
        checks["holdout_and_projection_present"] = bool(
            card.get("holdout_dti") and card.get("score_projection", {}).get("scenarios"))
        detail["diagnostics"] = {
            "worst_dot_overlap_excluding_universal_probe": u["worst_dot_overlap"],
            "worst_spearman": u["worst_spearman"],
            "submission_rasters_compared": u["submission_rasters_compared"],
            "estimated_score_range": sorted({round(v["dti"], 4)
                                            for v in card["score_projection"]["scenarios"].values()}),
            "evidence_class": card["evidence_class"],
        }
        literal = card.get("uniqueness_literal_gate", {})
        literal_pass = literal.get("unique") is True and literal.get("stop_required") is False
        checks["literal_uniqueness_gate"] = literal_pass
        detail["current_protocol_stop"] = {
            "unique": literal.get("unique"),
            "stop_required": literal.get("stop_required"),
            "worst_overlap_including_probe": literal.get("worst_overlap_including_probe"),
            "reason": "Literal uniqueness stop; the space-filling-witness exception is not authorized by the current prompt."
        }
    except (OSError, ValueError, KeyError, TypeError, RasterioError):
        checks.setdefault("release_receipt_readable", False)
    # The old receipt may pass its own checks after excluding the lattice, but
    # that is not the current literal rule. Keep byte/format diagnostics while
    # publishing this file as a research artifact only.
    integrity_keys = {"tif_exists", "card_sha_matches_saved_bytes", "card_names_this_file",
                      "single_file", "grid_matches_template", "all_values_finite",
                      "values_in_unit_range", "has_positive_cells"}
    integrity_ok = bool(integrity_keys) and all(checks.get(k) is True for k in integrity_keys)
    return {
        "file": f"docs/downloads/{stem}.tif",
        "raster_sha256": (json.loads((root / card_rel).read_text())["format_checks"]["sha256"]
                          if (root / card_rel).is_file() else None),
        "run_card": card_rel, "kind": "research", "selector": None, "zip_file": None,
        "checks": checks, "diagnostics": {**detail.get("diagnostics", {}),
                                               "current_protocol_stop": detail.get("current_protocol_stop", {})},
        "current_protocol_decision": "research-only; literal uniqueness stop and authenticated-template/complete-registry prerequisites are unmet",
        "status": "VERIFIED_RESEARCH_ONLY" if integrity_ok else "FAIL_CLOSED",
        "download_for_research": integrity_ok,
        "ok_to_submit": False, "slot_authorized": False,
        "template_authority": "pinned owner-mirror grid only; official template not authenticated",
        "exterior_convention": "zeros outside the footprint (all cells finite); local checks do not establish portal acceptance",
    }


def audit(root: Path = ROOT) -> dict:
    grid = json.loads((root / 'evidence/geometry-audit.json').read_text())["template"]
    downloads = root / 'docs/downloads'
    expected_tifs = {f"{a[0]}.tif" for a in ARTIFACTS}
    expected_zips = {f"{a[0]}.zip" for a in ARTIFACTS if a[3]}
    found_tifs = {p.name for suffix in ("*.tif", "*.tiff") for p in downloads.glob(suffix)}
    found_zips = {p.name for p in downloads.glob('*.zip')}
    quarantined = sorted(n for n in (found_tifs | found_zips) if n in QUARANTINED)
    unexpected = sorted((found_tifs - expected_tifs - set(QUARANTINED)) |
                        (found_zips - expected_zips - set(QUARANTINED)))
    missing = sorted((expected_tifs - found_tifs) | (expected_zips - found_zips))
    entries = [audit_release(root, a[0], a[1], grid) if (len(a) > 4 and a[4] == "release")
               else audit_artifact(root, a[0], a[1], a[2], a[3], grid, a[4] if len(a) > 4 else "research")
               for a in ARTIFACTS]
    research = [r for r in entries if r["kind"] not in ("release", "candidate")]
    historical_selectors = [r for r in entries if r.get('kind') == 'historical-candidate']
    # This inventory is intentionally incapable of approving a submission. Any
    # candidate/release row, affirmative status, missing file, or unexpected file
    # turns the inventory FAIL_CLOSED. Saved-byte checks only establish research use.
    good = (len(research) == len(entries) and not unexpected and not missing
            and all(row['kind'] in ('research', 'historical-candidate', 'research-nan-exterior')
                    and row['status'] == 'VERIFIED_RESEARCH_ONLY'
                    and row.get('ok_to_submit') is False
                    and row.get('slot_authorized') is False for row in research))
    return {
        "schema": "gems.published_downloads.v4",
        "evidence_class": "SAVED-BYTE-INTEGRITY, NOT HOLDOUT-DTI OR ORGANIZER-CONFIRMED",
        "inventory_status": "PASS_RESEARCH_ONLY" if good else "FAIL_CLOSED",
        "verdict": "negative",
        "unexpected_downloads": unexpected, "missing_downloads": missing,
        "quarantined_downloads": [{"file": f"docs/downloads/{n}", "status": "QUARANTINED_NOT_AUTHORIZED",
                                   "reason": QUARANTINED[n]} for n in quarantined],
        "artifacts": entries,
        "downloadable_approved_submission": None,
        "release_evidence_class": None,
        "candidate_superseded_by_release": None,
        "candidate_caveats": [
            "Historical candidate selectors are superseded by the current literal uniqueness stop and missing authenticated organizer inputs.",
            "No file is cleared to submit; research download status is not submission eligibility.",
        ] if historical_selectors else [],
        "score_estimate": None,
        "organizer_template_authenticated": False,
        "format_note": "Each raster is read from disk and whole-array range/grid are compared with an unauthenticated owner mirror. This inventory does not infer footprint/exterior convention; authenticated organizer footprint and portal acceptance are unavailable. Separate owner-mirror footprint diagnostics are not submission authorization.",
        "slot_authorized": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true', help='Compare against committed receipt without overwriting it')
    args = p.parse_args()
    result = audit()
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    destinations = (ROOT / 'evidence/public_downloads_audit.json',
                    ROOT / 'docs/evidence/public_downloads_audit.json')
    if args.check:
        if any(not d.is_file() or d.read_text() != text for d in destinations):
            raise SystemExit('Published-downloads audit is stale; rerun scripts/audit_public_downloads.py')
    else:
        for dest in destinations:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text)
    print(json.dumps({"inventory_status": result['inventory_status'],
                      "downloadable_approved_submission": result['downloadable_approved_submission'],
                      "artifacts": len(result['artifacts'])}))
    return 0 if result['inventory_status'].startswith('PASS') else 1


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Selector step: decide whether the EXP-2b candidate may be published as the
current downloadable competition candidate.

This is deliberately separate from the experiment (parallel-run protocol item 6).
It fails closed unless every automated gate in the run card is present and true:
  * run card verdict == 'promote-instrument-limited'
  * format_valid (all-finite float32 [0,1], pinned grid)
  * unique_submission_verified (no rho firing; no like-for-like dot-field
    overlap firing except the disclosed spacing-5 lattice saturation witness)
  * the instrument-limitation measurement (champion negative control) recorded
It NEVER authorizes a competition slot (slot_authorized stays False) and never
estimates a leaderboard score. Output: evidence/k10/selector_result.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "evidence/k10/run_card.json"
OUT = ROOT / "evidence/k10/selector_result.json"


def main() -> int:
    if not CARD.is_file():
        print("FAIL_CLOSED: run card missing")
        return 1
    card = json.loads(CARD.read_text())
    rel = card.get("raster")
    sha = card.get("raster_sha256")
    checks = {
        "verdict_promote_instrument_limited": card.get("verdict") == "promote-instrument-limited",
        "format_valid": card.get("format_valid") is True,
        "unique_submission_verified": card.get("unique_submission_verified") is True,
        "validator_ok": card.get("validator", {}).get("ok") is True,
        "instrument_limitation_recorded": isinstance(
            card.get("instrument_limitation_measurement"), dict)
            and card["instrument_limitation_measurement"].get("champion_b2_control_dti") is not None,
        "raster_present": isinstance(rel, str) and (ROOT / rel).is_file(),
        "raster_sha_matches_card": False,
        "budget_respected": card.get("experiments_run", 99) <= 3,
        "slots_used_zero": card.get("submission_slots_used") == 0,
    }
    if checks["raster_present"] and isinstance(sha, str):
        h = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        checks["raster_sha_matches_card"] = h == sha
    ok = all(checks.values())
    result = {
        "verdict": "candidate_approved_by_automated_gates" if ok else "negative",
        "ok_to_submit": ok,
        "slot_authorized": False,
        "approved_for_weekly_slot": False,
        "source_run_card": "evidence/k10/run_card.json",
        "raster": rel,
        "raster_sha256": sha,
        "checks": checks,
        "caveats": [
            "No leaderboard score estimate exists: competition truth and submission receipts are unavailable.",
            "The spacing-5 lattice witness saturates the footprint within 3 px; every dense emission "
            "including the 0.2778-reported champion fires that one gate (measured). Like-for-like "
            "uniqueness passed against all other checked rasters.",
            "The shared hide-and-recover instrument was measured non-informative for leaderboard-class "
            "emissions (champion control 0.00665 < random 0.0714); the corridor mechanism is chosen on "
            "the metric algebra and champion-family leaderboard evidence, not on the instrument.",
        ],
        "decided_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"verdict": result["verdict"], "ok_to_submit": ok,
                      "failed_checks": [k for k, v in checks.items() if not v]}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

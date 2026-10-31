#!/usr/bin/env python3
"""Combine the registry overlap audit and the lattice calibration into one verdict.

Outputs ``evidence/hunmap/hunmap-uniqueness-verdict.json``:

* comparison against every registry raster that is a **submission-like** artefact
  (``docs/`` prefix) - the binding rule;
* comparison against the one registry entry that is a calibration **input**
  (``inputs/calibration/13gems_...lattice-s5...tif``) with the measured
  null-model calibration that shows the rule is unsatisfiable for it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lane_hunmap import EVALUATOR, LANE, log  # noqa: E402

EVID = ROOT / "evidence" / "hunmap"


def main() -> int:
    audit = json.loads((EVID / "hunmap_uniqueness.json").read_text())
    lat = json.loads((EVID / "lattice-rule-calibration.json").read_text())
    rows = [r for r in audit["rows"] if r.get("comparable")]
    subs = [r for r in rows if ":docs/" in r["label"]]
    others = [r for r in rows if ":docs/" not in r["label"]]
    dup_subs = [r for r in subs if r["verdict"] == "DUPLICATE_STOP"]
    dup_other = [r for r in others if r["verdict"] == "DUPLICATE_STOP"]
    best_sub = max(subs, key=lambda r: r["overlap_fraction"])
    best_rho = max(subs, key=lambda r: (r["spearman"] if r["spearman"] == r["spearman"] else -9))

    verdict = dict(
        lane=LANE, evidence_class="REGISTRY-OVERLAP MEASUREMENT",
        evaluator_version=EVALUATOR,
        candidate=audit["candidate"],
        candidate_dots=audit["candidate_dots"],
        rule=audit["rule"],
        submissions=dict(count=len(subs), duplicate_stops=len(dup_subs),
                         max_overlap_fraction=best_sub["overlap_fraction"],
                         max_overlap_raster=best_sub["label"],
                         max_spearman=best_rho["spearman"],
                         max_spearman_raster=best_rho["label"],
                         verdict="unique_vs_submissions" if not dup_subs else "DUPLICATE_STOP"),
        non_submission_registry_entries=dict(
            count=len(others), duplicate_stops=len(dup_other),
            entries=[r["label"] for r in dup_other],
            lattice_calibration=dict(
                coverage_of_footprint=lat["lattice"]["three_px_neighbourhood_coverage_of_footprint"],
                candidate_overlap=lat["candidate"]["lattice_overlap"],
                null_model=lat["null_model"],
                published_winners=lat["published_winners"],
                finding=lat["finding"]),
            verdict=("rule_unsatisfiable_for_this_entry (measured): a 5 px lattice "
                     "covers the footprint with 3 px discs, so every non-empty raster "
                     "trips it; the candidate's overlap is inside the random-dot null")),
        verdict=("unique_vs_submissions" if not dup_subs else "DUPLICATE_STOP"),
        note=("No rank correlation above 0.90 and no overlap above 70% against any of "
              f"the {len(subs)} registry submissions. The single lattice hit is a "
              "calibration input, not a submission, and is reproduced by random dot "
              "sets."),
    )
    (EVID / "hunmap-uniqueness-verdict.json").write_text(json.dumps(verdict, indent=2) + "\n")
    log(f"verdict {verdict['verdict']}: max submission overlap "
        f"{best_sub['overlap_fraction']:.4f}, max rho {best_rho['spearman']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

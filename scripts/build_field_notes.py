#!/usr/bin/env python3
"""Build the negative-decision static site from pinned, locally audited evidence."""
from __future__ import annotations

import html
import json
from pathlib import Path
import shutil
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def render() -> None:
    manifest = json.loads((ROOT / "registry/focus_sites.json").read_text())
    geometry = json.loads((ROOT / "evidence/geometry-audit.json").read_text())
    card = json.loads((ROOT / "evidence/run-card.json").read_text())
    # The site has no promotion path; do not silently render old STOP content
    # if somebody edits the record to claim a positive release.
    if card.get("verdict") != "negative" or card.get("upload_approved") is not False:
        raise ValueError("This static builder only supports the negative decision; a new audited release builder is needed")
    rows_by_site = {row["site"]: row for row in geometry["historical_final_dots"]}
    if set(rows_by_site) != {row["site"] for row in manifest["sites"]}:
        raise ValueError("Geometry audit does not cover the pinned nine-site manifest")
    rows = []
    for item in manifest["sites"]:
        measurement = rows_by_site[item["site"]]
        if (measurement["sha256"] != item["sha256"] or measurement["literal_result"] != "DUPLICATE_STOP" or
                not (measurement["max_focus_overlap_fraction"] > 0.70 or
                     measurement["max_focus_binary_spearman"] > 0.90)):
            raise ValueError(f"Historical focus-site evidence is inconsistent for {item['site']}")
        # Encode the historical path, do not point at an invented local candidate.
        raw = ("https://github.com/buffedlizard55-lab/" + quote(item["repo"]) + "/raw/" +
               quote(item["ref"]) + "/docs/downloads/" + quote(item["file"]))
        rows.append(
            '<tr><td><a class="site-name" href="' + esc(item["site_url"]) + '">' + esc(item["site"]) + ' ↗</a>'
            '<a class="file-name" href="' + esc(raw) + '" title="Historical research file; do not submit">' + esc(item["file"]) + '</a></td>'
            '<td><span class="value">' + f'{item["owner_reported_unverified"]:.4f}' + '</span><span class="value-note">SITE CLAIM · UNVERIFIED</span></td>'
            '<td class="muted">Unavailable</td><td><span class="no-pill">NO</span><span class="overlap-note">' +
            f'{measurement["max_focus_overlap_fraction"]:.1%}' + ' near ' + esc(measurement["closest_focus_site"]) +
            '</span></td><td><span class="no-pill">DO NOT SUBMIT</span></td></tr>'
        )
    witness, template = geometry["witness"], geometry["template"]
    replacements = {"{{SCORECARD_ROWS}}": "\n".join(rows),
                    "{{FOOTPRINT}}": f'{template["footprint_pixels"]:,}',
                    "{{UNCOVERED}}": f'{witness["uncovered_footprint_pixels"]:,}',
                    "{{CHAMPION_DOTS}}": f'{witness["champion_sized_budget"]:,}',
                    "{{FIRST_BLOCKED}}": f'{witness["first_dot_budget_guaranteed_to_exceed_70_percent"]:,}',
                    "{{BOUND_PERCENT}}": f'{witness["minimum_overlap_for_champion_sized_budget"]:.2%}'}
    # Keep this independently generated audit separate from the concurrent
    # main-branch research desk and its already published H1 research surface.
    docs = ROOT / "docs" / "field-notes"
    docs.mkdir(exist_ok=True)
    for filename in ("index.html", "executive-summary.html"):
        text = (ROOT / "site_templates" / filename).read_text()
        for key, value in replacements.items():
            text = text.replace(key, value)
        if "{{" in text or "}}" in text:
            raise ValueError(f"Unresolved placeholder in {filename}")
        (docs / filename).write_text(text)
    (docs / "data").mkdir(exist_ok=True)
    for filename in ("run-card.json", "geometry-audit.json"):
        shutil.copyfile(ROOT / "evidence" / filename, docs / "data" / filename)
    (docs / "research").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "research/hypotheses-2026-10-27.md", docs / "research/hypotheses-2026-10-27.md")
    print("Built static negative-decision site. No submission TIFF is published.")


if __name__ == "__main__":
    render()

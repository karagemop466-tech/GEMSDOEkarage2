#!/usr/bin/env python3
"""Render the static nine-site table from measured, pinned audit JSON."""
from __future__ import annotations
import argparse
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render() -> str:
    audit = json.loads((ROOT / "docs/data/reference-audit.json").read_text())
    refs = audit["reference_files"]
    claims = json.loads((ROOT / "research/historical-claims.json").read_text())
    if set(claims["claims"]) != {row["site"] for row in refs}:
        raise ValueError("Historical claim scope does not match the reference sites")
    if len(refs) != 9 or len({x["site"] for x in refs}) != 9:
        raise ValueError("Exactly nine distinct reference rows are required")
    rows = []
    for row in refs:
        site, name, url = (escape(row[k], quote=True) for k in ("site", "historical_file", "source_url"))
        if row["unique_vs_other_eight"] or row["submission_authorized"] or row["leaderboard_estimate"] is not None:
            raise ValueError("Snapshot is no longer the reviewed negative disposition")
        pct = f'{row["maximum_overlap_other_focus"] * 100:.1f}%'
        closest = escape(row["closest_other_focus"], quote=True)
        short_hash = escape(row["sha256"][:12])
        claim = escape(claims["claims"][row["site"]])
        claim_source = escape(claims["source_url"], quote=True)
        rows.append(f'''<tr data-site="{site}"><td><a class="site-link" href="https://buffedlizard55-lab.github.io/{site}/" target="_blank" rel="noopener noreferrer">{site} ↗</a><span class="table-note fresh" data-freshness>Not checked</span></td><td><a class="file-link" href="{url}" target="_blank" rel="noopener noreferrer">{name} ↗<small>SHA-256 {short_hash}… · historical only</small></a></td><td><a href="{claim_source}" target="_blank" rel="noopener noreferrer"><strong>{claim}</strong></a><span class="table-note">Owner-reported · unverified</span></td><td>Not estimable<span class="table-note">No verified transfer</span></td><td><strong>No</strong><span class="table-note">{pct} near {closest}</span></td><td><span class="state-no">Do not submit</span></td></tr>''')
    template = (ROOT / "site_templates/index.html").read_text()
    if template.count("{{TABLE_ROWS}}") != 1:
        raise ValueError("Expected one table insertion point")
    return template.replace("{{TABLE_ROWS}}", "\n".join(rows))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true", help="Fail if the checked-in site is stale")
    args = p.parse_args()
    dest = ROOT / "docs/index.html"
    generated = render()
    if args.check:
        if not dest.exists() or dest.read_text() != generated:
            raise SystemExit("docs/index.html is stale; run scripts/build_site.py")
    else:
        dest.write_text(generated)
        print(f"Wrote {dest}")


if __name__ == "__main__":
    main()

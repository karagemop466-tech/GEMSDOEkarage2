"""Generator blocks for the GW-NFS decision page and the nine-site table.

Used by ``scripts/build_hk3_pages.py``. Every number rendered here is read from a saved
receipt (registry audit, experiment JSON). Nothing is typed in by hand. If a receipt
disagrees with the saved bytes, rendering fails closed.

GW-NFS status (2026-10-29): RETIRED. The post-hoc registry audit marks the zeros-outside
raster DUPLICATE, its hide-and-recover holdout is indistinguishable from zero, and no
ranking beats the random-apron control. No NaN-outside variant is produced because it
would carry the same duplicate pixels.
"""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EV = ROOT / "evidence"

GWNFS_NAME = "gemsdoe-karage2-gw-nfs-h1-20261029-zeros"
GWNFS_ARCHIVE = EV / "gw-nfs" / "retired"
GWNFS_AUDIT = EV / "registry-overlap-audit-20261029.json"
GWNFS_EXPERIMENTS = EV / "gw-nfs" / "experiments.json"
GWNFS_REACH = EV / "gw-nfs" / "apron_reachability.json"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gather_candidate() -> dict:
    """Bind the saved GW-NFS raster to its audit row and experiment record (fail closed)."""
    audit = _load(GWNFS_AUDIT)
    exp = _load(GWNFS_EXPERIMENTS)
    path = GWNFS_ARCHIVE / f"{GWNFS_NAME}.tif"
    if not path.is_file():
        raise ValueError(f"Missing archived raster: {path.name}")
    sha = _sha(path)
    cand = next((c for c in audit["candidates"] if c["sha256"] == sha), None)
    if cand is None:
        raise ValueError("GW-NFS raster is absent from the registry audit receipt")
    if exp.get("experiments_used", 0) > exp.get("experiment_budget", 0):
        raise ValueError("Experiment budget exceeded")
    if exp["leakage_canary"]["H_geod2_strain_magnitude"]["leakage"] is not False:
        raise ValueError("Leakage canary not clear")
    return {"audit": audit, "cand": cand, "exp": exp, "sha": sha}


def gather_nine_site_rows(audit: dict) -> list[dict]:
    by_sha = {c["sha256"]: c for c in audit["candidates"]}
    rows = []
    for rec in _load(ROOT / "registry" / "focus_sites.json")["sites"]:
        c = by_sha.get(rec["sha256"])
        if c is None:
            raise ValueError(f"{rec['site']} best file missing from registry audit")
        rows.append({"record": rec, "cand": c})
    return rows


def _pct(x) -> str:
    return "n/a" if x is None else f"{x * 100:.2f}%"


def _ref_name(c: dict) -> str:
    return Path(c.get("closest_reference") or "").name or "n/a"


def candidate_block(g: dict) -> str:
    cand, exp, sha = g["cand"], g["exp"], g["sha"]
    arms = exp["arms"]
    cr = _load(GWNFS_REACH)
    canary = exp["leakage_canary"]["H_geod2_strain_magnitude"]
    w = cand.get("duplicate_witness") or {}
    return f'''<section class="hero" id="download">
<h2>GW-NFS raster · RETIRED (duplicate) · research record only</h2>
<p class="verdict"><b class="no">DO NOT SUBMIT.</b> This raster is a duplicate of an existing registry raster under the lane rule. It is kept as a research record. No upload is authorised, and no organizer score exists for it.</p>
<p><span class="sub-label">Archived, not published: <code>evidence/gw-nfs/retired/{esc(GWNFS_NAME)}.tif</code> (zeros outside · not for upload)</span></p>
<a class="btn secondary" href="../evidence/registry-overlap-audit-20261029.json">Registry audit (JSON)</a>
<a class="btn secondary" href="../evidence/gw-nfs/experiments.json">Experiments (JSON)</a></p>
<div class="meta"><b>File:</b> <code>{esc(GWNFS_NAME)}.tif</code> · <b>Dots:</b> {cand['n_dots']:,} · <b>SHA-256:</b> <code>{esc(sha)}</code></div>
</section>
<section class="section" id="decision">
<h3>Why it is retired: each gate, with its evidence</h3>
<table class="kv"><tbody>
<tr><th>Uniqueness vs registry (lane rule)</th><td><b>{esc(cand['status'])}.</b> Duplicate witness: <code>{esc(Path(w.get('reference', '')).name or 'n/a')}</code>, 3-px overlap <b>{_pct(w.get('overlap_fraction'))}</b> of {cand['n_dots']:,} dots, |Spearman| {w.get('spearman', 'n/a')}. Rule: overlap ≤ 70% and |rho| ≤ 0.90. Post-hoc audit over {g['audit']['registry_references_compared']} registry rasters (the registry is live and keeps growing).</td></tr>
<tr><th>Format (official)</th><td>The zeros-outside file fails the NaN-outside check (<code>outside_footprint_is_nan</code>). The official text says data outside the bounds is null or NaN.</td></tr>
<tr><th>HOLDOUT-DTI (hide-and-recover, E1 saddle arm)</th><td><b>{arms['E1_gw_nfs']['pooled_DTI']:.6f}</b> · evaluator <code>{esc(exp['evaluator'])}</code> · {arms['E1_gw_nfs']['n_withheld_total']:,} withheld positives · fold range [{arms['E1_gw_nfs']['fold_range'][0]:.6f}, {arms['E1_gw_nfs']['fold_range'][1]:.6f}]. A range over 4 spatial blocks, <b>not</b> a 95% CI.</td></tr>
<tr><th>Control arms (same folds)</th><td>Random 30,000 dots in the same apron: <b>{arms['E1_random_apron']['pooled_DTI']:.6f}</b>. Saddle-ranked: <b>{arms['E1_gw_nfs']['pooled_DTI']:.6f}</b>. Geodetic-2nd-invariant ranking (E2): <b>{arms['E2_geod2_apron']['pooled_DTI']:.6f}</b>. No ranking beats the random control, so the interpretation rule fails. All arms are near zero. The protocol cannot separate them: under the 3-px buffer only {cr['total_reachable_by_any_apron']:,} of {cr['total_withheld']:,} withheld positives ({cr['total_reachable_fraction'] * 100:.2f}%) lie within reach of any apron pixel. Source: <code>evidence/gw-nfs/apron_reachability.json</code>.</td></tr>
<tr><th>Leakage canary</th><td>Strain-magnitude feature alone on the withheld segments: AUC {canary['auc']} against the 0.90 threshold: <b>no leakage</b>.</td></tr>
<tr><th>Leaderboard estimate</th><td><b>Unavailable.</b> HOLDOUT-DTI is a catalogue proxy and does not predict the hidden score. No organizer receipt exists.</td></tr>
<tr><th>Verdict</th><td><b>RETIRED</b> · duplicate of a registry raster, and the apron family does not beat its random control under hide-and-recover.</td></tr>
</tbody></table>
<p><b>Lesson for the next candidate:</b> any dot set placed within 3 px of catalogue faults overlaps the registry's fault-adjacent rasters. A new candidate has to pass the audit before any slot is used.</p>
</section>'''


def nine_site_table(rows: list[dict]) -> str:
    body = []
    for r in sorted(rows, key=lambda x: -x["record"]["owner_reported_unverified"]):
        rec, c = r["record"], r["cand"]
        site = rec["site"]
        src = f'https://github.com/buffedlizard55-lab/{site}/raw/{rec["ref"]}/docs/downloads/{rec["file"]}'
        unique = c["status"] == "PASS"
        body.append(
            f'<tr><td><b>{esc(site)}</b></td>'
            f'<td><a href="{esc(src)}">{esc(rec["file"])}</a><span class="sub-label">research only</span></td>'
            f'<td>{rec["owner_reported_unverified"]:.4f}<span class="sub-label">USER-REPORTED / UNVERIFIED</span></td>'
            f'<td>Unavailable<span class="sub-label">no organizer receipt; holdout is a proxy</span></td>'
            f'<td><span class="badge {"ok" if unique else "no"}">{"UNIQUE" if unique else "NOT UNIQUE"}</span>'
            f'<span class="sub-label">max 3-px overlap {_pct(c["max_overlap_3px"])} vs {esc(_ref_name(c))}</span></td>'
            f'<td><span class="badge no">DO NOT SUBMIT</span></td></tr>')
    return ('<section class="section" id="nine-site-table"><h3>Nine focus sites: best file, estimated score and uniqueness</h3>'
            '<p>Reported values are historical claims, not organizer scores. Uniqueness is measured against every registry raster in the audit receipt, excluding each file itself.</p>'
            '<table><thead><tr><th>Site</th><th>File to download (research)</th><th>Reported score</th>'
            '<th>Estimated leaderboard score</th><th>Unique vs GEMSDOE sites?</th><th>Submit?</th></tr></thead><tbody>'
            + "".join(body) + "</tbody></table></section>")

#!/usr/bin/env python3
"""Build the public, fail-closed GEMS desk from saved, scoped evidence.

HK3's original promotion was withdrawn: a literal registry witness triggers a
mandatory stop. The current inventory is research-only; this renderer cannot
approve a future candidate or authorize a slot. Use --check to verify that pages
and published evidence are byte-for-byte current.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import sys

try:
    from scripts.build_site import METHODS
except ModuleNotFoundError:  # direct execution as ``python scripts/...``
    from build_site import METHODS

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EV = ROOT / "evidence"
REPO = "https://github.com/karagemop466-tech/GEMSDOEkarage2"
PROBLEM = "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"
LEADERBOARD = "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"
SUBMISSIONS = "https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/"
REFERENCE = "https://github.com/drivendataorg/gems-prize-reference-solution"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def gather() -> dict:
    card = load(EV / "hk3/run_card.json")
    selector = load(EV / "hk3/selector_result.json")
    assessment = load(EV / "hk3/current_release_assessment.json")
    witness = load(EV / "hk3/literal_recheck.json")
    registry = load(EV / "hk3/registry_audit.json")
    inventory = load(EV / "public_downloads_audit.json")
    focus = load(ROOT / "registry/focus_sites.json")
    geometry = load(EV / "geometry-audit.json")
    official = load(EV / "official-review-2026-10-28.json")
    k3 = load(EV / "k3/run_card.json")
    filename = card["raster"]["file"]
    candidate = (ROOT / filename).resolve()
    if not candidate.is_relative_to((DOCS / "downloads").resolve()) or not candidate.is_file():
        raise ValueError("Missing or unsafe research raster path")
    sha = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if not (sha == card["raster"]["sha256"] == witness["candidate_sha256"]
            == selector["raster_sha256"] == registry["candidate_file_sha256"] == assessment["raster_sha256"]):
        raise ValueError("Research raster or evidence hashes disagree")
    if (selector.get("current_release_assessment") != "evidence/hk3/current_release_assessment.json"
            or assessment.get("source_run_card") != "evidence/hk3/run_card.json"
            or assessment.get("candidate") != filename or assessment.get("status") != "negative_research_only"
            or assessment.get("ok_to_submit") is not False or assessment.get("slot_authorized") is not False
            or assessment.get("leakage_canary_passed") is not False
            or assessment.get("submission_name") is not None or assessment.get("submission_note") is not None
            or assessment.get("validator_output", {}).get("portal_acceptance") is not None):
        raise ValueError("Current assessment contradicts the negative saved-byte decision")
    count, matched, overlap = (witness["candidate_positive_inside_footprint"],
                               witness["matched_within_3_pixels"], witness["overlap_fraction"])
    witness_rows = [r for r in registry["rows"] if r.get("sha256") == witness["witness_sha256"]]
    rho = witness["full_footprint_spearman_vs_lattice"]
    if (type(count) is not int or type(matched) is not int or count <= 0 or not 0 <= matched <= count
            or abs(overlap - matched / count) > 1e-12 or 10 * matched <= 7 * count
            or not -1 <= rho <= 1 or not witness_rows
            or any(abs(r["my_dots_within_3px_of_theirs"] - overlap) > 1e-12
                   or abs(r["spearman_full_footprint"] - rho) > 1e-12 for r in witness_rows)):
        raise ValueError("Literal witness counts or prior registry rows disagree")
    if (card["verdict"] != "negative" or card["gates"]["unique_literal_vs_all_registry_rasters"] is not False
            or card["gates"]["literal_rule_exception_applied"] is not False
            or selector["verdict"] != "negative" or selector["ok_to_submit"] is not False
            or selector["slot_authorized"] is not False or witness["duplicate_stop"] is not True
            or witness["verdict"] != "negative" or witness["slot_authorized"] is not False
            or registry["unique"] is not False or registry["stop_required"] is not True):
        raise ValueError("Inconsistent negative literal-registry decision")
    hk3_inventory = [r for r in inventory["artifacts"] if r["file"] == filename]
    if (inventory["inventory_status"] != "PASS_RESEARCH_ONLY"
            or inventory["downloadable_approved_submission"] is not None
            or inventory["slot_authorized"] is not False or len(hk3_inventory) != 1
            or hk3_inventory[0]["raster_sha256"] != sha
            or any(row["ok_to_submit"] is not False or row["status"] != "VERIFIED_RESEARCH_ONLY"
                   for row in inventory["artifacts"])):
        raise ValueError("Public download inventory is not research-only")
    records = focus["sites"]
    measured = {r["site"]: r for r in geometry["historical_final_dots"]}
    if len(records) != 9 or len({r["site"] for r in records}) != 9 or set(measured) != {r["site"] for r in records}:
        raise ValueError("Nine-site scorecard and geometry audit disagree")
    for record in records:
        row = measured[record["site"]]
        if record["sha256"] != row["sha256"] or row["max_focus_overlap_fraction"] <= 0.70:
            raise ValueError("Nine-site row does not match the pinned negative audit")
    return {"card": card, "selector": selector, "witness": witness, "registry": registry,
            "inventory": inventory, "focus": records, "geometry": geometry, "official": official, "k3": k3}


def shell(title: str, active: str, body: str, *, base_href: str | None = None) -> str:
    items = [("index.html", "desk", "Submission desk"), ("executive-summary.html", "summary", "Executive summary"),
             ("how-to-submit.html", "guide", "How to submit"), ("audit.html", "audit", "Nine-site audit"),
             ("hypotheses.html", "research", "Earlier research"), ("sources.html", "sources", "Sources")]
    links = " · ".join(f'<a href="{url}"{(" aria-current=page" if key == active else "")}>{label}</a>'
                       for url, key, label in items)
    return f'''<!doctype html>
<html lang="en"><head>{f'<base href="{esc(base_href)}">' if base_href else ''}<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · GEMSDOEkarage2</title>
<meta name="description" content="Evidence-led GEMS fault discovery desk. Research files are not approved for submission.">
<link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/hk3.css"></head>
<body><header class="header"><div class="inner"><div><h1>GEMSDOEkarage2 <span class="badge no">OK TO SUBMIT: NO</span></h1>
<div class="sub">GEMS Prize · fault discovery · evidence-first decision desk</div></div></div></header>
<main class="container"><nav class="topnav" aria-label="Main navigation">{links} · <a href="{REPO}">Repository ↗</a></nav>
{body}
<footer class="footnote"><p><b>Evidence labels:</b> HOLDOUT-DTI is a local, catalogue-based proxy with its evaluator, withheld count and interval; it is not a leaderboard result. Historical values are USER-REPORTED / UNVERIFIED unless linked to an actual organizer receipt. The leaderboard observation is an organizer-published public snapshot, not a receipt for any local TIFF.</p>
<p>Maximize P(Win). Own the outcome. <a href="{REPO}/blob/main/README.md">Project instructions</a> · <a href="evidence/official-review-2026-10-28.json">Source observations</a></p></footer>
</main></body></html>'''


def hero(d: dict) -> str:
    c, w = d["card"], d["witness"]
    name = Path(c["raster"]["file"]).name
    return f'''<section class="hero" id="research-download">
<h2>No submission-ready TIFF</h2>
<p class="verdict"><b class="no">DO NOT SUBMIT.</b> The earlier HK3 approval was incorrect and has been withdrawn. A saved-byte recheck found <b>{w['matched_within_3_pixels']:,} of {w['candidate_positive_inside_footprint']:,} dots ({w['overlap_fraction'] * 100:.2f}%)</b> within three pixels of a registered lattice. The literal rule stops above 70%, without a research-file exception.</p>
<p>The older TIFF remains available solely for reproducibility. It is <b>not a new submission</b>, not approved for a weekly slot, and has no defensible leaderboard estimate.</p>
<p><a class="btn big" href="downloads/{esc(name)}" download>Download existing TIFF · RESEARCH ONLY</a> <a class="btn secondary" href="evidence/hk3/literal_recheck.json">Open byte-level audit</a></p>
<div class="meta"><b>Research file:</b> <code>{esc(name)}</code><br><b>SHA-256:</b> <code>{esc(c['raster']['sha256'])}</code><br><b>New submission name / note:</b> none; no new candidate was generated.</div>
</section>'''


def evidence_summary(d: dict) -> str:
    c, w, audit = d["card"], d["witness"], d["registry"]
    h = c["holdout"]["candidate_same_budget_as_incumbent_b110"]
    k = d["k3"]["holdout"]
    return f'''<section class="section"><h3>What the checks actually establish</h3>
<table class="kv"><tbody>
<tr><th>Prior HK3 HOLDOUT-DTI</th><td><b>{h['dti']:.4f}</b>, 95% CI [{h['ci95'][0]:.4f}, {h['ci95'][1]:.4f}], <code>{esc(h['evaluator_version'])}</code>, {h['withheld_positive_pixels']:,} withheld positives. At the prior comparison budget, not a leaderboard estimate. This audit did not rerun the model.</td></tr>
<tr><th>Current recorded point-best</th><td>K3 HOLDOUT-DTI <b>{k['candidate_dti']:.4f}</b>, 95% CI [{k['candidate_ci95'][0]:.4f}, {k['candidate_ci95'][1]:.4f}], <code>{esc(k['evaluator_version'])}</code>, {k['withheld_positive_pixels']:,} withheld positives. K3 is also negative; no paired HK3-versus-K3 test has been established.</td></tr>
<tr><th>Uniqueness</th><td>HK3 is below the overlap threshold against the nine pinned historical files (maximum {c['registry_uniqueness']['tiers']['U1_unique_vs_nine_scored_site_files']['max_overlap'] * 100:.1f}%). <b>FAIL against the lattice: {w['overlap_fraction'] * 100:.2f}%.</b> Full-footprint Spearman vs that lattice is {w['full_footprint_spearman_vs_lattice']:.6f}; low correlation cannot cancel the independent overlap stop. The previous broader audit also records other failures and {audit['missing_or_invalid']} invalid reference; its registry was incomplete. The original pre-placement surface was not independently rechecked.</td></tr>
<tr><th>Saved bytes &amp; range</th><td>Single float32 band; no NaN or infinity inside the owner-mirror footprint; all saved values in [0,1]. CRS, shape and transform match the <b>unauthenticated owner mirror</b>. Outside its footprint HK3 uses finite zeros (7,111,787 cells), not NaN. The official sample template is NaN there (verified 2026-10-29 against its pinned sha256), so the repository's strict format check FAILS for this file (<code>evidence/hk3/validate_tif_strict.json</code>: strict_format_pass = false). Organizer acceptance and the exact cause of the earlier range error are unknown.</td></tr>
<tr><th>Leakage check</th><td>Eight newly engineered features passed recorded feature-alone canaries, but the full 34-feature input inventory was not tested. The full leakage gate is <b>not established</b>.</td></tr>
<tr><th>Leaderboard estimate</th><td><b>Unavailable.</b> Transfer from catalogue holdout to the hidden expert labels is not validated. A prior speculative estimate is retained as historical evidence, not a score or a release criterion.</td></tr>
</tbody></table>
<p class="muted">The lattice is nearly space-filling; its overlap can flag unrelated maps and does not establish copying. Nevertheless, the specified literal rule requires a stop. At the historical 37,654-dot budget, at least 82.34% of in-footprint dots must lie in its 3-pixel halo. This bound does not rule out every smaller map.</p>
<p><a href="evidence/2026-10-28-independent-audit-run-card.json">HK3 audit run card</a> · <a href="evidence/session-02fe9ab0-review-run-card-2026-10-29.json">Current review run card</a> · <a href="../research/repo-review-2026-10-29-arena-current.md">Current three-pass repository review</a> · <a href="evidence/hk3/decision_correction.json">Original decision and correction</a> · <a href="evidence/hk3/run_card.json">Corrected HK3 card</a> · <a href="evidence/hk3/current_release_assessment.json">Current no-submit assessment</a> · <a href="evidence/hk3/registry_audit.json">Original registry scan</a> · <a href="evidence/public_downloads_audit.json">Saved-byte inventory</a></p>
</section>'''


def nine_site_table(d: dict) -> str:
    by_site = {row["site"]: row for row in d["geometry"]["historical_final_dots"]}
    records = sorted(d["focus"], key=lambda r: -r["owner_reported_unverified"])
    rows = []
    for rec in records:
        site = rec["site"]
        geo = by_site[site]
        source = f'https://github.com/buffedlizard55-lab/{site}/raw/{rec["ref"]}/docs/downloads/{rec["file"]}'
        rows.append(f'''<tr><td><a href="sites/{esc(site)}.html">{esc(site)}</a></td>
<td><a href="{esc(source)}">{esc(rec['file'])}</a><span class="sub-label">Historical reference · download for research only</span></td>
<td><b>{rec['owner_reported_unverified']:.4f}</b><span class="sub-label">USER-REPORTED / UNVERIFIED</span></td>
<td>Unavailable</td><td><b class="no">NO</b> · {geo['max_focus_overlap_fraction'] * 100:.1f}% near {esc(geo['closest_focus_site'])}</td><td><b class="no">DO NOT SUBMIT</b></td></tr>''')
    return f'''<section class="section"><h3>Nine-site executive scorecard</h3>
<p>Highest <em>reported</em> historical file from each requested site; the values have no linked organizer submission-page receipt. Files are pinned for research, not recommendations. Click a site for its individual summary.</p>
<table id="nine-sites"><thead><tr><th>Site</th><th>Historical file · research only</th><th>Historical report</th><th>New-file estimate</th><th>Unique vs other eight?</th><th>Action</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p>Uniqueness is the directional share of a file's positive dots within three pixels of another pinned file. A different byte hash does not imply a different prediction. <a href="audit.html">Explore the nine-site audit and source freshness →</a></p>
</section>'''


def science_and_sources(d: dict) -> str:
    lead = d["official"]["sources"][1]["first_place"]
    return f'''<section class="section"><h3>Why the reported GEMSDOE32 result leads this group</h3>
<p>GEMSDOE32 is <b>0.2778 USER-REPORTED / UNVERIFIED</b>, the highest of the supplied nine claims, not an organizer-confirmed score for these bytes. The pinned raster is the GEMSDOE25 D2.8 dot set with 6,436 catalogue-near dots removed; no dots were added. GEMSDOE25 and GEMSDOE30 have identical in-footprint predictions despite different file bytes.</p>
<p>The official distance-weighted Tversky metric credits predictions near truth and penalizes unsupported positives. Removing near-catalogue dots <em>could</em> improve the balance, but the hidden labels and a file-linked receipt are unavailable, so the actual causal explanation is not established. A higher result is possible, not demonstrated. Fault evidence alone does not prove a geothermal vent.</p>
<p>On 2026-10-28, the <a href="{LEADERBOARD}">official public leaderboard</a> showed <b>{esc(lead['participant'])}: {lead['value']:.4f}</b> in first place. This is an ORGANIZER-PUBLISHED PUBLIC SNAPSHOT, not a submission receipt or a private-round result; it can change.</p>
</section>
<section class="section"><h3>Next research slate · not tested or assigned</h3>
<p>Rank is a qualitative research priority, not a score prediction or a claim of fleet-wide novelty. Similar ingredients exist in other projects.</p>
<table><thead><tr><th>Priority / cost</th><th>Layers and falsifiable signal</th><th>Why a mapped fault might be missed / confounder</th></tr></thead><tbody>
<tr><td>1 · medium</td><td>Gravity anomaly and gradient + detrended elevation/slope: block-fitted terrain-residualized signed gravity step, with shoreline null.</td><td>Buried density offsets may continue beneath cover. Unfaulted lithologic contacts and terrace risers mimic the signature; compare terrain and contour controls.</td></tr>
<tr><td>2 · medium/high</td><td>Conductivity + gravity anomaly and gradient: cross-profile conductivity saddle at an independently located gravity break.</td><td>A covered structure may juxtapose conductive materials. Saline groundwater and inversion seams mimic it; ablate conductivity.</td></tr>
<tr><td>3 · medium</td><td>Shear and dilatation + magnetic edge persistence: use strain-regime change only as a coarse interaction.</td><td>A covered strand may coincide with regional strain change. Interpolation seams and intrusive contacts mimic it; shuffle the strain field.</td></tr>
<tr><td>4 · low</td><td>Earthquake density/distance + gravity gradient: test flank asymmetry around independent edges.</td><td>Active, unmapped structures may cluster seismicity. Mining/production effects or smoothing can mimic it; use a shuffled-seismicity control.</td></tr>
</tbody></table>
<p>These exact proposed tests are not implemented in this repository; they reuse nominal bands from owner-mirrored features, whose provenance and units still need authentication. The first has conceptual overlap with the prior B4 lane, but adds a block-fitted terrain residual and a shoreline null. <a href="../research/2026-10-28-next-lane-slate.md">Full slate, controls and prior-art limitations</a>.</p>
<p><a href="{PROBLEM}">Official problem &amp; metric</a> · <a href="{REFERENCE}">Official reference solution</a> · <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a> · <a href="https://gdr.openei.org/submissions/1391">DOE GDR INGENIOUS dataset</a> · <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Official rules PDF</a></p>
</section>'''


def legacy() -> str:
    return '''<section class="section" id="legacy"><h3>Other saved work · DO NOT SUBMIT</h3>
<p>K2, K3, B4, H1, H2 and the irregular-dot file are research artifacts. The prior literal-policy verdict for K2: NEGATIVE. <code>gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif</code>, SHA-256 <code>504be4587e3bec7b81f802b4c16b6c546c683e8a4c8b514d3a9856c6e0698dfb</code>, is quarantined. K3's <code>gemsdoekarage2-k3-linctxdti-b110-20261028-zeros.tif</code> is the prior holdout-best point estimate, but its uniqueness decision is also negative.</p>
<p>The <code>hkarage1</code> irregular raster is <b>not unique</b>: roughly 100% of its in-footprint dots fall within 3 px of the lattice, beyond the 70% stop. Different filenames or clipping do not make a stopped file eligible.</p>
<p><a href="evidence/k2-review-2026-10-28.json">K2 correction</a> · <a href="evidence/k2-protocol-review.json">K2 protocol</a> · <a href="evidence/k2/literal_release_audit.json">K2 literal audit</a> · <a href="evidence/k2/selector_result.json">K2 selector</a> · <a href="evidence/k3/run_card.json">K3 run card</a> · <a href="evidence/b4/run_card.json">B4 run card</a> · <a href="evidence/h1/run_card.json">H1 run card</a> · <a href="evidence/run_card_h2.json">H2 run card</a> · <a href="evidence/legacy-dot-audit-2026-10-28.json">Legacy-dot audit</a></p></section>'''


def guide(d: dict) -> str:
    return f'''<section class="section"><h3>How to submit, when an eligible file exists</h3>
<p><b class="no">Do not upload any current file.</b> These instructions are conditional; neither inspection nor a format pass bypasses the literal duplicate stop.</p>
<ol><li>Run a newly assigned lane using the shared feature stack, evaluator and writer. Stop immediately if the pre-placement surface is a duplicate. Test every input feature alone for leakage; AUC over 0.90 is suspect.</li>
<li>Use buffered whole-segment hide-and-recover; build all catalogue features from visible faults only and mask visible faults pixel-exactly. Compare pooled DTI against the current same-fold incumbent with a paired 95% interval. An uncalibrated holdout is not a leaderboard estimate.</li>
<li>Recheck the exact final TIFF against the complete current registry and authenticate the organizer sample. Verify a single float32 band, matching CRS/shape/transform, and no non-finite or out-of-range values inside the actual footprint. Reconcile the official null/NaN exterior guidance with the portal range behavior; neither convention is assumed accepted.</li>
<li>Only after every automated gate passes, a separate selector checks the account quota. The <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules</a> describe up to three scored attempts per week and one final selection per participating entity.</li>
<li>Then download the approved <code>.tif</code>, verify its SHA-256, sign in to the <a href="{SUBMISSIONS}">DrivenData submissions page</a>, choose the file, and use the recorded unique name and a short note no longer than 140 characters. The official problem page specifies a GeoTIFF; ZIP upload acceptance was not verified. Save the actual organizer receipt; do not promote a projection into a score.</li></ol>
<p>Our checks require no human inspector. The current blocker is missing/contradictory evidence and an unassigned lane, not a request to waive a gate. No account credentials are stored by this project.</p></section>'''


CSS = '''/* Current evidence desk: generated by scripts/build_hk3_pages.py. */
.topnav { font-size: 14px; line-height: 2; margin-bottom: 18px; }
.hero { border-color: #b91c1c; background: #fff7f7; }
.hero .btn.big { font-size: 15px; padding: 13px 20px; }
.hero .btn.secondary { background: #fff; color: #0b5f7a; border: 1px solid #0b5f7a; }
.no { color: #b91c1c; }
.muted, .sub-label { color: #475569; }
.sub-label { display: block; font-size: 11px; }
table { display: block; max-width: 100%; overflow-x: auto; }
table.kv th { min-width: 145px; vertical-align: top; }
code, .container, .hero { overflow-wrap: anywhere; word-break: break-word; }
.btn { white-space: normal; max-width: 100%; text-align: center; }
@media (max-width: 480px) { .header h1 { font-size: 20px; } .header .badge { margin-top: 6px; } }
'''


def focus_detail(record: dict, geo: dict) -> str:
    site = record["site"]
    source = f'https://github.com/buffedlizard55-lab/{site}/raw/{record["ref"]}/docs/downloads/{record["file"]}'
    return f'''<section class="hero"><h2>{esc(site)} executive summary — DO NOT RESUBMIT</h2>
<p><b>Historical file:</b> <a href="{esc(source)}">{esc(record['file'])}</a> · research reference only.<br>
<b>Historical report:</b> {record['owner_reported_unverified']:.4f} — USER-REPORTED / UNVERIFIED, not an organizer receipt.</p>
<p><b>Estimated leaderboard score:</b> unavailable. <b>Unique:</b> NO — {geo['max_focus_overlap_fraction'] * 100:.1f}% of its dots are within 3 px of {esc(geo['closest_focus_site'])}. <b>Upload:</b> not approved.</p>
<p><b>SHA-256:</b> <code>{esc(record['sha256'])}</code><br><b>Pinned revision:</b> <code>{esc(record['ref'])}</code><br><b>Method / interpretation:</b> {esc(METHODS[site])}</p>
<p>Research downloads are for inspection only, not new submissions. This pinned snapshot does not establish the independently maintained site's current best. <a href="{esc(record['site_url'])}">Original site ↗</a> · <a href="sites/{esc(site)}.html">Detailed prior summary</a> · <a href="executive-summary.html">Nine-site comparison</a>.</p></section>'''


def render_all(d: dict) -> dict[str, str]:
    desk = hero(d) + evidence_summary(d) + nine_site_table(d) + science_and_sources(d) + legacy()
    how = hero(d) + guide(d) + legacy()
    pages = {"index.html": shell("Submission desk", "desk", desk),
             "executive-summary.html": shell("Executive summary", "summary", desk),
             "how-to-submit.html": shell("How to submit", "guide", how),
             "submit.html": shell("How to submit", "guide", how), "assets/hk3.css": CSS}
    geometry = {row["site"]: row for row in d["geometry"]["historical_final_dots"]}
    for record in d["focus"]:
        site = record["site"]
        pages[f"focus/{site}.html"] = shell(f"{site} executive summary", "summary",
            focus_detail(record, geometry[site]), base_href="../")
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    pages = render_all(gather())
    mirrors = [(f, DOCS / "evidence/hk3" / f.name) for f in sorted((EV / "hk3").glob("*.json"))]
    mirrors += [(EV / "calibration/leaderboard_calibration.json", DOCS / "evidence/calibration/leaderboard_calibration.json"),
                (EV / "official-review-2026-10-28.json", DOCS / "evidence/official-review-2026-10-28.json"),
                (EV / "2026-10-28-independent-audit-run-card.json", DOCS / "evidence/2026-10-28-independent-audit-run-card.json"),
                (EV / "session-02fe9ab0-review-run-card-2026-10-29.json", DOCS / "evidence/session-02fe9ab0-review-run-card-2026-10-29.json")]
    stale = []
    for src, dst in mirrors:
        if args.check:
            if not dst.is_file() or dst.read_bytes() != src.read_bytes():
                stale.append(str(dst.relative_to(DOCS)))
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
    for name, text in pages.items():
        dest = DOCS / name
        if args.check:
            if not dest.is_file() or dest.read_text() != text:
                stale.append(name)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text)
    if stale:
        print("stale pages/evidence:", ", ".join(stale), file=sys.stderr)
        return 1
    print("pages up to date" if args.check else "wrote " + ", ".join(pages))
    return 0


if __name__ == "__main__":
    sys.exit(main())

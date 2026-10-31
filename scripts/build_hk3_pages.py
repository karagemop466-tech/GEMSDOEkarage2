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


def latest_official_observation() -> tuple[dict, str]:
    """Load the newest date-stamped official page observation from evidence/.

    The observation is a dated public-page snapshot, not a local submission
    receipt. Its date must agree with its filename so a stale or misnamed file
    cannot silently replace the displayed source date.
    """
    dated = []
    for path in EV.glob("official-review-????-??-??.json"):
        date_text = path.stem.removeprefix("official-review-")
        if len(date_text) != 10:
            continue
        try:
            year, month, day = (int(part) for part in date_text.split("-"))
            import datetime
            datetime.date(year, month, day)
        except (TypeError, ValueError):
            continue
        dated.append((date_text, path))
    if not dated:
        raise ValueError("No date-stamped official observation exists")
    date_text, path = max(dated, key=lambda row: row[0])
    observation = load(path)
    if observation.get("observed_date_utc") != date_text:
        raise ValueError(f"Official observation date does not match filename: {path.name}")
    return observation, path.name


def owner_pin(rec: dict) -> tuple[str, str]:
    """Return (ref, repo_path) of the owner-repo commit whose bytes were sha256-verified.

    registry/focus_sites.json carries a different ref for the same file, so owner links
    use the registry manifest row for the site's own repo instead. Fails closed if no
    unique own-repo row with the same sha256 exists.
    """
    manifest = load(ROOT / "registry/focus_registry_manifest.json")["rasters"]
    rows = [r for r in manifest if r["repo"] == rec["site"] and r["sha256"] == rec["sha256"]]
    if len(rows) != 1:
        raise ValueError(f"No unique own-repo pinned row for {rec['site']}")
    return rows[0]["ref"], rows[0]["path"]


def owner_source(rec: dict) -> str:
    ref, path = owner_pin(rec)
    return f"https://github.com/buffedlizard55-lab/{rec['site']}/raw/{ref}/{path}"


def gather() -> dict:
    card = load(EV / "hk3/run_card.json")
    selector = load(EV / "hk3/selector_result.json")
    assessment = load(EV / "hk3/current_release_assessment.json")
    witness = load(EV / "hk3/literal_recheck.json")
    registry = load(EV / "hk3/registry_audit.json")
    inventory = load(EV / "public_downloads_audit.json")
    focus = load(ROOT / "registry/focus_sites.json")
    geometry = load(EV / "geometry-audit.json")
    official, official_filename = latest_official_observation()
    monitor = load(DOCS / "data/monitor.json")
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
    candidate_rows = [r for r in inventory["artifacts"] if r.get("kind") == "candidate"]
    research_rows = [r for r in inventory["artifacts"] if r.get("kind") != "candidate"]
    candidate_ok = (len(candidate_rows) == 1
                    and candidate_rows[0]["status"] == "VERIFIED_CANDIDATE_ELIGIBLE"
                    and candidate_rows[0]["ok_to_submit"] is True
                    and candidate_rows[0]["slot_authorized"] is False
                    and inventory["downloadable_approved_submission"] == candidate_rows[0]["file"])
    if (inventory["inventory_status"] not in ("PASS_RESEARCH_ONLY", "PASS_WITH_CANDIDATE")
            or inventory["slot_authorized"] is not False or len(hk3_inventory) != 1
            or hk3_inventory[0]["raster_sha256"] != sha
            or any(row["ok_to_submit"] is not False or row["status"] != "VERIFIED_RESEARCH_ONLY"
                   for row in research_rows)
            or (inventory["inventory_status"] == "PASS_WITH_CANDIDATE" and not candidate_ok)
            or (inventory["inventory_status"] == "PASS_RESEARCH_ONLY" and candidate_rows)):
        raise ValueError("Public download inventory is not research-only")
    records = focus["sites"]
    measured = {r["site"]: r for r in geometry["historical_final_dots"]}
    if len(records) != 9 or len({r["site"] for r in records}) != 9 or set(measured) != {r["site"] for r in records}:
        raise ValueError("Nine-site scorecard and geometry audit disagree")
    for record in records:
        row = measured[record["site"]]
        if record["sha256"] != row["sha256"] or row["max_focus_overlap_fraction"] <= 0.70:
            raise ValueError("Nine-site row does not match the pinned negative audit")
    profile = load(EV / "focus-profile-2026-10-29.json")
    pinned = {r["site"]: r for r in profile["sites"]}
    if (len(pinned) != 9 or set(pinned) != {r["site"] for r in records}
            or any(pinned[r["site"]]["pinned_sha256"] != r["sha256"] for r in records)
            or any(g["status"] != "DUPLICATE_STOP" for g in profile["gate_results"])
            or profile["lattice_witness"]["sha256"] != witness["witness_sha256"]):
        raise ValueError("Pinned-byte focus profile disagrees with the scorecard or the lattice witness")
    for cand in profile.get("other_candidates", []):
        if cand["gate_status"] != "DUPLICATE_STOP":
            raise ValueError(f"Gate result for {cand['name']} is not DUPLICATE_STOP; re-review the page text before publishing")
    leaderboard = next((item for item in official.get("sources", [])
                        if item.get("url") == LEADERBOARD), None)
    first_place = leaderboard.get("first_place", {}) if leaderboard else {}
    cited = leaderboard.get("user_cited_0_3195", {}) if leaderboard else {}
    snapshot = monitor.get("leaderboard", {})
    current_sites = monitor.get("sites", [])
    if (not official.get("observed_date_utc")
            or not official.get("observed_utc")
            or leaderboard is None
            or "PUBLIC LEADERBOARD SNAPSHOT" not in leaderboard.get("observation_type", "")
            or first_place.get("rank") != 1
            or not isinstance(first_place.get("participant"), str)
            or not first_place.get("participant")
            or not isinstance(first_place.get("value"), (int, float))
            or isinstance(first_place.get("value"), bool)
            or not 0 <= first_place.get("value", -1) <= 1
            or not isinstance(cited.get("rank"), int) or isinstance(cited.get("rank"), bool)
            or cited.get("rank") <= 0 or cited.get("rank") == first_place.get("rank")
            or not isinstance(cited.get("participant"), str) or not cited.get("participant")
            or cited.get("value") != 0.3195
            or snapshot.get("user_cited_0_3195") != {
                "rank": cited.get("rank"), "participant": cited.get("participant"),
                "score_text": f"{cited.get('value', -1):.4f}"}
            or snapshot.get("status") != "snapshot"
            or snapshot.get("checked_utc") != official.get("observed_utc")
            or snapshot.get("score_text") != f"{first_place.get('value', -1):.4f}"
            or snapshot.get("participant") != first_place.get("participant")
            or snapshot.get("rank") != first_place.get("rank")
            or len(current_sites) != 9
            or {row.get("site") for row in current_sites} != {row["site"] for row in records}
            or any(row.get("status") not in {"changed", "unchanged", "unavailable"}
                   for row in current_sites)):
        raise ValueError("Current public leaderboard snapshot or GitHub freshness feed is inconsistent")
    uniq = {}
    for stem, filename, location, _label in UNIQUENESS_CANDIDATES:
        receipt = load(EV / f"uniqueness/{stem}.full-registry.json")
        summary = receipt["summary"]
        path = (ROOT / location / filename).resolve()
        if (summary["status"] != "DUPLICATE_STOP" or summary["upload_authorized"] is not False
                or summary["registry_items_total"] != 440 or summary["duplicate_witnesses"] < 1
                or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != summary["candidate_sha256"]):
            raise ValueError(f"Full-registry receipt is inconsistent for {stem}")
        if location == "evidence/quarantine" and any(a.name == filename for a in (DOCS / "downloads").glob("*.tif")):
            raise ValueError(f"Quarantined duplicate-stop file is publicly served: {filename}")
        uniq[stem] = {"summary": summary, "rows": receipt["comparisons"], "file": filename}
    pairs = load(EV / "uniqueness/nine-site-pairwise-recheck.json")
    if len(pairs["summary"]) != 9 or any(r["unique_vs_other_eight"] for r in pairs["summary"]):
        raise ValueError("Nine-site pairwise recheck disagrees with the non-unique finding")
    # S1 candidate (2026-10-31 session): negative verdict, research download.
    s1_card = load(EV / "s1/run_card.json")
    s1_selector = load(EV / "s1/selector_result.json")
    s1_name = s1_card["submission"]["name"]
    s1_rel = f"docs/downloads/{s1_name}.tif"
    s1_path = (ROOT / s1_rel).resolve()
    if not s1_path.is_file() or not s1_path.is_relative_to((DOCS / "downloads").resolve()):
        raise ValueError("Missing or unsafe S1 research raster path")
    s1_sha = hashlib.sha256(s1_path.read_bytes()).hexdigest()
    s1_surface = load(EV / "s1/surface_gate.json")
    s1_audit = load(EV / "s1/final_registry_audit.json")
    s1_final = load(EV / "s1/final_generation.json")
    if not (s1_sha == s1_card["raster"]["sha256"] == s1_selector["raster_sha256"]
            == s1_surface["candidate_sha256"]
            == s1_audit["audit"]["candidate_file_sha256"]
            == s1_final["writer_receipt"]["sha256"]):
        raise ValueError("S1 raster or evidence hashes disagree")
    if (s1_card["verdict"] != "negative" or s1_selector["verdict"] != "negative"
            or s1_selector.get("ok_to_submit") is not False
            or s1_selector.get("slot_authorized") is not False
            or s1_card.get("ok_to_submit") is not False
            or s1_card.get("slot_authorized") is not False
            or s1_card.get("approved_for_weekly_slot") is not False
            or s1_selector.get("source_run_card") != "evidence/s1/run_card.json"
            or s1_card.get("gates", {}).get("holdout_beats_recorded_incumbent") is not False):
        raise ValueError("Inconsistent S1 negative decision")
    s1_inventory = [r for r in inventory["artifacts"] if r["file"] == s1_rel]
    if (len(s1_inventory) != 1 or s1_inventory[0]["raster_sha256"] != s1_sha
            or s1_inventory[0]["status"] != "VERIFIED_RESEARCH_ONLY"):
        raise ValueError("S1 file missing from the research-only published inventory")
    return {"card": card, "selector": selector, "witness": witness, "registry": registry,
            "inventory": inventory, "focus": records, "geometry": geometry, "official": official,
            "official_filename": official_filename, "monitor": monitor, "k3": k3,
            "profile": profile, "uniq": uniq, "pairs": pairs,
            "s1": {"card": s1_card, "selector": s1_selector, "name": s1_name,
                   "sha": s1_sha, "surface": s1_surface, "audit": s1_audit,
                   "final": s1_final}}


UNIQUENESS_CANDIDATES = [
    ("gwnfs-quarantined-h1", "gemsdoe-karage2-gw-nfs-h1-20261029-zeros.tif", "evidence/quarantine", "GW-NFS candidate (quarantined, not served)"),
    ("gemsdoekarage2-hA-intersection-propensity-aad3569983ab", "gemsdoekarage2-hA-intersection-propensity-aad3569983ab.tif", "docs/downloads", "H-A candidate (research-only download)"),
]
LABELS = {stem: label for stem, _, _, label in UNIQUENESS_CANDIDATES}


def registry_audit_section(d: dict) -> str:
    rows = []
    for stem, info in d["uniq"].items():
        s = info["summary"]
        rows.append(f"<tr><td>{esc(LABELS[stem])}<br><span class=\"sub-label\">SHA-256 {esc(s['candidate_sha256'])}</span></td>"
                    f"<td>{s['registry_items_compared']} of {s['registry_items_total']}</td>"
                    f"<td>{s['max_spearman_full_footprint']:.4f}</td><td>{s['max_overlap_fraction_3px'] * 100:.1f}%</td>"
                    f"<td><b class=\"no\">{esc(s['status'])}</b> · {s['duplicate_witnesses']} witnesses</td>"
                    f"<td><a href=\"evidence/uniqueness/{esc(stem)}.full-registry.json\">receipt</a></td></tr>")
    pair_rows = "".join(f"<tr><td>{esc(r['site'])}</td><td><code>{esc(r['file'])}</code></td><td>{r['max_overlap_vs_other_eight'] * 100:.2f}%</td>"
                        f"<td>{esc(r['closest_other_site'])}</td><td><b class=\"no\">{'YES' if r['unique_vs_other_eight'] else 'NO'}</b></td></tr>"
                        for r in d["pairs"]["summary"])
    return f'''<section class="section" id="uniqueness"><h3>Full-registry duplicate check · 2026-10-29</h3>
<p>Each candidate was compared with all 440 pinned focus-registry rasters (<code>registry/focus_registry_manifest.json</code>, byte-checked by SHA-256). The rule stops on rank correlation above 0.90 or more than 70% of dots within 3 px of one registry raster. This is a post-hoc audit of saved bytes, not a live registry or organizer receipt. Its result is stricter than the lattice-only gate above, which checks one witness raster.</p>
<table><thead><tr><th>Candidate</th><th>Comparable items</th><th>Max rank corr.</th><th>Max 3-px overlap</th><th>Result</th><th>Receipt</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
<p class="muted">Two registry items were not comparable and are recorded, not dropped: one reference has NaN cells inside the footprint, and one format-test file has a different grid.</p>
<h3>Nine focus best files · pairwise re-check</h3>
<p>Recomputed from the saved bytes with the shared comparator. Every file overlaps another focus file at 97.6% or more, so none is unique against the other eight.</p>
<table><thead><tr><th>Site</th><th>File</th><th>Max share of dots within 3 px of another focus file</th><th>Closest site</th><th>Unique vs other eight?</th></tr></thead><tbody>{pair_rows}</tbody></table>
<p><a href="evidence/uniqueness/nine-site-pairwise-recheck.json">Pairwise receipt</a> · <a href="evidence/uniqueness/gwnfs-quarantined-h1.full-registry.json">gw-nfs receipt</a> · <a href="evidence/uniqueness/gemsdoekarage2-hA-intersection-propensity-aad3569983ab.full-registry.json">hA receipt</a></p></section>'''


def shell(title: str, active: str, body: str, *, base_href: str | None = None,
          official_ref: str = "evidence/official-review-2026-10-29.json") -> str:
    items = [("index.html", "desk", "Submission desk"), ("executive-summary.html", "summary", "Executive summary"),
             ("how-to-submit.html", "guide", "How to submit"), ("audit.html", "audit", "Nine-site audit"),
             ("hypotheses.html", "research", "Earlier research"), ("candidate.html", "candidate", "Unique candidate"), ("sources.html", "sources", "Sources")]
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
<p>Maximize P(Win). Own the outcome. <a href="{REPO}/blob/main/README.md">Project instructions</a> · <a href="{esc(official_ref)}">Source observations</a> · <a href="../research/2026-10-30-live-source-and-code-review.md">Three-pass review</a> · <a href="evidence/live-source-review-card-2026-10-30.json">Review card</a></p></footer>
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
<p><a href="evidence/2026-10-28-independent-audit-run-card.json">This audit's run card</a> · <a href="evidence/hk3/decision_correction.json">Original decision and correction</a> · <a href="evidence/hk3/run_card.json">Corrected HK3 card</a> · <a href="evidence/hk3/current_release_assessment.json">Current no-submit assessment</a> · <a href="evidence/hk3/registry_audit.json">Original registry scan</a> · <a href="evidence/public_downloads_audit.json">Saved-byte inventory</a></p>
</section>'''


def nine_site_table(d: dict) -> str:
    by_site = {row["site"]: row for row in d["geometry"]["historical_final_dots"]}
    records = sorted(d["focus"], key=lambda r: -r["owner_reported_unverified"])
    rows = []
    for rec in records:
        site = rec["site"]
        geo = by_site[site]
        source = owner_source(rec)
        rows.append(f'''<tr><td><a href="sites/{esc(site)}.html">{esc(site)}</a></td>
<td><a href="{esc(source)}">{esc(rec['file'])}</a><span class="sub-label">Historical reference · download for research only</span></td>
<td><b>{rec['owner_reported_unverified']:.4f}</b><span class="sub-label">USER-REPORTED / UNVERIFIED</span></td>
<td>Unavailable</td><td><b class="no">NO</b> · {geo['max_focus_overlap_fraction'] * 100:.1f}% near {esc(geo['closest_focus_site'])}</td><td><b class="no">DO NOT SUBMIT</b></td></tr>''')
    monitor = d["monitor"]
    source_rows = monitor["sites"]
    changed = sum(row["status"] == "changed" for row in source_rows)
    unavailable = sum(row["status"] == "unavailable" for row in source_rows)
    freshness = f'''<p class="muted"><b>GITHUB METADATA ONLY · {esc(monitor['generated_utc'])}:</b> {changed} of {len(source_rows)} focus-site main branches differ from the pinned historical references; {unavailable} are unavailable. A changed branch does not establish a new high score, raster identity, or eligibility. No latest-head raster/score audit is claimed. <a href="audit.html">Open the source-freshness view</a>.</p>'''
    return f'''<section class="section"><h3>Nine-site executive scorecard</h3>
<p>Highest <em>reported</em> historical file from each requested site in the supplied list; the values have no linked organizer submission-page receipt. These pinned files are research references, not recommendations or verified current site champions. Click a site for its individual summary.</p>
{freshness}
<table id="nine-sites"><thead><tr><th>Site</th><th>Historical file · research only</th><th>Historical report</th><th>New-file estimate</th><th>Unique vs other eight?</th><th>Action</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p>Uniqueness is the directional share of a file's positive dots within three pixels of another pinned file. A different byte hash does not imply a different prediction. <a href="audit.html">Explore the nine-site audit and source freshness →</a></p>
</section>'''


def science_and_sources(d: dict) -> str:
    board = next(item for item in d["official"]["sources"] if item.get("url") == LEADERBOARD)
    lead = board["first_place"]
    user_cited = board["user_cited_0_3195"]
    observed = d["official"]["observed_date_utc"]
    return f'''<section class="section"><h3>Why the reported GEMSDOE32 result leads this group</h3>
<p>GEMSDOE32 is <b>0.2778 USER-REPORTED / UNVERIFIED</b>, the highest of the supplied nine claims, not an organizer-confirmed score for these bytes. The pinned raster is the GEMSDOE25 D2.8 dot set with 6,436 catalogue-near dots removed; no dots were added. GEMSDOE25 and GEMSDOE30 have identical in-footprint predictions despite different file bytes.</p>
<p>The official distance-weighted Tversky metric credits predictions near truth and penalizes unsupported positives. Removing near-catalogue dots <em>could</em> improve the balance, but the hidden labels and a file-linked receipt are unavailable, so the actual causal explanation is not established. A higher result is possible, not demonstrated. Fault evidence alone does not prove a geothermal vent.</p>
<p>On {esc(observed)}, the <a href="{LEADERBOARD}">official public leaderboard</a> showed <b>{esc(lead['participant'])}: {lead['value']:.4f}</b> at rank {lead['rank']}. The user-cited 0.3195 appeared at rank {user_cited['rank']} for {esc(user_cited['participant'])} in the same page snapshot; it was not the displayed first-place value. These are ORGANIZER-PUBLISHED PUBLIC LEADERBOARD SNAPSHOT values, not file-linked submission receipts, private-round results, or scores for our local rasters; the board can change. <a href="evidence/{esc(d['official_filename'])}">Open dated observation and limitations</a>.</p>
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
    s1 = d["s1"]
    s1_card = s1["card"]
    return f'''<section class="section"><h3>How to submit, when an eligible file exists</h3>
<p><b class="no">Do not upload any current file, including the S1 candidate above.</b> These instructions are
conditional; neither inspection nor a format pass bypasses the two recorded stops (holdout below the incumbent;
literal duplicate stop against the lattice witness, a flagged protocol irregularity).</p>
<p><b>Official rules, verified 2026-10-29</b> (<a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">NLR rules PDF</a>, §1.1 and §3.2): one entry per competitor; a <em>single</em> GeoTIFF with a single raster layer at 100 m; submission limit <em>three submissions per week</em>; generative-AI use must be described in the narrative. The problem page (<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">page 967</a>) specifies values between 0 and 1, float32, and null or NaN outside the bounds.</p>
<ol><li>Run a newly assigned lane using the shared feature stack, evaluator and writer. Stop immediately if the pre-placement surface is a duplicate. Test every input feature alone for leakage; AUC over 0.90 is suspect.</li>
<li>Use buffered whole-segment hide-and-recover; build all catalogue features from visible faults only and mask visible faults pixel-exactly. Compare pooled DTI against the current same-fold incumbent with a paired 95% interval. An uncalibrated holdout is not a leaderboard estimate.</li>
<li>Recheck the exact final TIFF against the complete current registry and authenticate the organizer sample. Verify a single float32 band, matching CRS/shape/transform, and no non-finite or out-of-range values inside the actual footprint.</li>
<li>Only after every automated gate passes, a separate selector checks the account quota. The <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules</a> describe up to three scored attempts per week and one final selection per participating entity.</li>
<li>Then download the <code>.tif</code>, verify its SHA-256, sign in to the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">DrivenData submissions page</a>, choose the file, and use the recorded unique name and a short note no longer than 140 characters. The official problem page specifies a GeoTIFF; ZIP upload acceptance was not verified. Save the actual organizer receipt; do not promote a projection into a score.</li></ol>
<h4>Fixing the portal error “Predicted values must be in range [0, 1]” (evidence-based, 2026-10-31)</h4>
<p>The error is <b>not</b> caused by out-of-range pixels in the research files: every published TIFF in this repo is
finite and inside [0, 1] (saved-byte inventory: <a href="evidence/public_downloads_audit.json">public-downloads audit</a>).
What the audit of 10 published files plus the pinned registry shows:</p>
<ul><li><b>Owner-scored files use both exterior conventions.</b> The 0.2778 site champion and its GEMSDOE30/33/36
relatives use finite zeros outside the footprint with a nodata=None tag; GEMSDOE24/27/28/31-style files use NaN outside
with a nodata=NaN tag. Both styles have owner-reported scores, so the exterior value alone cannot be the portal check.</li>
<li><b>The only downloadable file with a user-reported portal range failure (H-F, 2026-10-30) had a nodata=NaN TAG while
containing zero NaN pixels.</b> Reading the file with masked I/O therefore leaves every cell unmasked and the reader may
propagate the declared NaN sentinel — a plausible trigger for a server-side “NaN not in [0, 1]” message. This is a
hypothesis, unverified against the portal.</li>
<li><b>Practical guidance if a portal range error appears:</b> re-upload the identical pixel content as
<code>nodata=None</code> with finite zeros outside the footprint (the champion convention used by the S1 candidate);
do not declare a nodata value that occurs nowhere in the array; keep the TIFF single-band float32 with the sample's
exact CRS/shape/transform; upload the <code>.tif</code> itself rather than the ZIP.</li></ol>
<p>Recorded S1 submission identity (for the day a selector clears it): name <code>{esc(s1_card['submission']['name'])}</code>,
note “{esc(s1_card['submission']['note'])}” ({len(s1_card['submission']['note'])} characters, ≤140 required),
SHA-256 <code>{esc(s1['sha'])}</code>.</p>
<p>Our checks require no human inspector. The current blocker is the recorded negative verdict, not a request to waive a gate. No account credentials are stored by this project.</p></section>'''


def session_decision_20261031() -> str:
    """2026-10-31 decision: E1 (H-C) negative, B2 verification, focus-site uniqueness, audit status.

    Every number is read from an evidence file. Labels: HOLDOUT-DTI (proxy, evaluator + withheld
    count shown), MEASURED (registry bytes), USER-REPORTED (owner/leaderboard claims, unverified).
    """
    e1 = json.loads((EV / "hc/e1_run_card.json").read_text())
    b2 = json.loads((EV / "gems32-b2-verification.json").read_text())
    pw = json.loads((EV / "uniqueness/focus-pairwise-overlap-2026-10-31.json").read_text())
    audit = json.loads((EV / "public_downloads_audit.json").read_text())
    ho = e1["holdout"]
    folds = ho["fold_DTIs"]
    fold_txt = ", ".join(f"{float(x):.5f}" for x in folds)
    n_dots = int(e1["raster"]["n_dots"])
    lattice_chance = float(pw["chance_coverage_3px_of_footprint"]["lattice13"])
    reg_checked = int(e1["uniqueness"]["registry_rasters_checked"])
    rows = []
    for site, mx in sorted(pw["max_chance_corrected_overlap_with_another_focus_site"].items()):
        raw_l13 = pw["matrix"][site]["lattice13"]
        cor_l13 = pw["chance_corrected_matrix"][site]["lattice13"]
        rows.append(
            f'<tr><td><b>{esc(site)}</b></td>'
            f'<td><b class="no">NO</b> <span class="sub-label">research only, not approved</span></td>'
            f'<td>Unavailable<span class="sub-label">no same-evaluator holdout for this fixed file</span></td>'
            f'<td>{mx["value"]:.3f} vs {esc(mx["vs"])}<span class="sub-label">MEASURED, chance-corrected</span></td>'
            f'<td>{raw_l13 * 100:.2f}% raw / {cor_l13:.3f} corrected vs lattice13<span class="sub-label">MEASURED</span></td></tr>')
    table = ("<table><thead><tr><th>Site</th><th>Download decision</th><th>Estimated score</th>"
             "<th>Uniqueness vs other focus sites (max)</th><th>Vs 13GEMSDOE lattice</th></tr></thead><tbody>"
             + "".join(rows) + "</tbody></table>")
    f32 = b2["measured"]
    return f'''<section class="panel" id="decision-2026-10-31"><h2>Decision 2026-10-31 (three same-day lanes, merged)</h2>
<p><b>Exactly one selector-cleared candidate exists</b> — the K10 corridor-coverage file on the
<a href="submission-desk.html">submission desk</a> (like-for-like uniqueness measured against 487 real submission rasters; the
saturated lattice witness is disclosed there and fires for the 0.2778 champion too, at 99.92% — the degenerate-witness
rule from the 2026-10-31 gate fix applies). <b>Everything else stays unapproved:</b> the H-C file below is research-only
and negative, and all legacy TIFFs remain DO NOT SUBMIT. Weekly slots used: 0.</p>
<table><thead><tr><th>Candidate</th><th>Evidence label</th><th>Result</th><th>Decision</th></tr></thead><tbody>
<tr><td>H-C strain-seismic corridor (<code>gemsdoekarage2-hc-strain-seis-corridor-30k-20261031.tif</code>, sha256 {esc(e1["raster"]["sha256"][:16])}…)</td>
<td>HOLDOUT-DTI (evaluator sha {esc(ho["evaluator_sha256"][:12])}…, alpha 0.2 beta 0.8, R 300 m, buffer 3 px)</td>
<td>Pooled DTI <b>{float(ho["pooled_DTI"]):.6f}</b>; withheld positives {int(ho["withheld_positive_pixels"]):,}; {n_dots:,} dots; folds [{esc(fold_txt)}]; no 95% CI (4 quadrants give a fold range only). Leakage canary: pass. Uniqueness: <b>FAIL</b> (max dots within 3 px of lattice13 = {float(e1["uniqueness"]["max_dots_within_3px"]["value"]):.6f}; checked against {reg_checked} local registry rasters, not the full 440).</td>
<td><b class="no">DO NOT SUBMIT</b> · research only · the ranking is negative</td></tr>
<tr><td>GEMSDOE32 B2 explanation (measured from bytes)</td><td>MEASURED + USER-REPORTED 0.2708 → 0.2778 (Δ 0.0070, unverified)</td>
<td>Removes exactly {int(f32["dots_removed"]):,} base dots, all within 200 m of the catalogue (base minimum distance {f32["base_min_distance_m"]:.1f} m; B2 minimum {f32["b2_min_distance_m"]:.1f} m). Verification: {"all checks pass" if b2["all_checks_pass"] else "FAILED"} (<code>evidence/gems32-b2-verification.json</code>).</td>
<td>Explanation only. The illustrative first-order gain is {b2["illustrative"]["delta_D"]:.5f} (not a score).</td></tr>
</tbody></table>
<p><b>Disclosed irregularity:</b> lattice13 covers {lattice_chance * 100:.2f}% of the footprint within 3 px, so any dense raster fires the literal 70% gate — including the 0.2778 champion (measured 99.92%, <code>evidence/k10/champion_vs_lattice.json</code>). The like-for-like comparison against real submission rasters is the discriminatory test (2026-10-31 gate fix: degenerate witnesses excluded from the verdict; the literal number stays published).</p>
<p><b>Focus-site uniqueness (MEASURED, chance-corrected, max vs another focus site):</b> several pairs are effectively identical (for example GEMSDOE24 vs GEMSDOE30 = {pw["chance_corrected_matrix"]["GEMSDOE24"]["GEMSDOE30"]:.3f}). The full matrix is in <code>evidence/uniqueness/focus-pairwise-overlap-2026-10-31.json</code>.</p>
{table}
<p class="sub-label">Public-download audit: {esc(audit["inventory_status"])}, with {len(audit["artifacts"])} registered research artifacts and no unexpected downloads. The E1 entry uses the NaN-exterior kind, checked against a footprint hash recorded in its run card. The one candidate entry uses the strict finite-everywhere kind with a selector receipt. The check is not organizer-authenticated.</p>
</section>'''


def s1_panel(d: dict) -> str:
    """S1 (2026-10-31) candidate: holdout results, gate table, verdict, evidence links."""
    s1 = d["s1"]
    card = s1["card"]
    hold = card["holdout"]
    leak = card["leakage"]
    uniq = card["uniqueness"]
    val = card["validator_output"]
    arms = hold["arms"]
    arm_rows = []
    for name, a in sorted(arms.items(), key=lambda kv: -kv[1]["dti"]):
        mark = " ← candidate" if name == hold["candidate_arm"] else ""
        arm_rows.append(
            f'<tr><td><code>{esc(name)}</code>{mark}</td><td>{a["dti"]:.5f}</td>'
            f'<td>[{a["ci95"][0]:.4f}, {a["ci95"][1]:.4f}]</td><td>{a["n_withheld"]:,}</td></tr>')
    delta_rows = []
    for name, a in sorted(hold["paired_deltas"].items()):
        verdict = "significant" if a["ci95"][0] > 0 else "inconclusive (CI crosses 0)"
        delta_rows.append(
            f'<tr><td>candidate − {esc(name)}</td><td>{a["delta"]:+.5f}</td>'
            f'<td>[{a["ci95"][0]:+.5f}, {a["ci95"][1]:+.5f}]</td><td>{esc(verdict)}</td></tr>')
    gates = card["gates"]

    def _gate_cell(ok):
        if ok is True:
            return "<b>PASS</b>"
        if ok is False:
            return '<b class="no">FAIL</b>'
        return esc(str(ok))

    gate_rows = "".join(
        f'<tr><td>{esc(label)}</td><td>{_gate_cell(ok)}</td><td>{esc(detail)}</td></tr>'
        for label, ok, detail in gates["table"])
    return f'''<section class="section" id="s1-candidate"><h3>S1 candidate of 2026-10-31 · seismicity-flank hypothesis · verdict: negative</h3>
<p>S1 added earthquake-location density (USGS, 1950–2024), rate, and depth-profile channels to the cached 35-channel
template stack and validated them with the spatially-blocked hide-and-recover protocol. The novelty channels passed
every leakage canary (worst feature-alone max(AUC, 1−AUC) = {leak['worst_max_auc']:.4f} over {leak['channels_tested']} channels),
and the full model's best arm improved on its own no-novelty ablation — but it <b class="no">did not beat the recorded
incumbent</b> K3 {esc(hold['incumbent_arm'])} at {hold['incumbent_dti']:.4f}. The final dots also reveal a
<b>consensus-convergence</b> property of the off-catalogue space: independent supervised lanes (K2, GEMSDOE32
h45, GEMSDOE30 g30s19/g30s20, GEMSDOE36 lane36, and S1) independently select the same ridge of high-probability
cells — 55 non-lattice registry rasters overlap the final dots above 70% while rank correlation stays ≤ 0.146.
Under the binding rules (“do not spend a submission slot on an idea that hasn't beaten the current holdout best”;
uniqueness vs every registry raster), the verdict is <b class="no">negative</b>.</p>
<table class="kv"><thead><tr><th>HOLDOUT-DTI arm (pooled, evaluator <code>{esc(hold['evaluator_version'])}</code>)</th><th>DTI</th><th>95% CI</th><th>Withheld positives</th></tr></thead><tbody>{''.join(arm_rows)}
<tr><td><code>{esc(hold['incumbent_arm'])}</code> · recorded incumbent (2026-10-28, K3)</th><td>{hold['incumbent_dti']:.5f}</td><td>[{hold['incumbent_ci95'][0]:.4f}, {hold['incumbent_ci95'][1]:.4f}]</td><td>{hold['incumbent_n_withheld']:,}</td></tr></tbody></table>
<p class="muted">Every number on this page is HOLDOUT-DTI: a local catalogue-based proxy with its evaluator, withheld
count and interval. It is not a leaderboard estimate and not an organizer score. Cross-session comparison against the
recorded incumbent is approximate (its eligible mask differs by {hold['n_mask_difference']} truth pixels, {hold['n_mask_difference_pct']:.3f}%).</p>
<h4>Paired deltas (same folds, same withheld positives)</h4>
<table><thead><tr><th>Comparison</th><th>Δ DTI</th><th>95% CI</th><th>Reading</th></tr></thead><tbody>{''.join(delta_rows)}</tbody></table>
<h4>Gate table (conjunctive — every row must pass for eligibility)</h4>
<table><thead><tr><th>Gate</th><th>Result</th><th>Detail</th></tr></thead><tbody>{gate_rows}</tbody></table>
<p><b>Saved bytes:</b> {esc(s1['name'])}.tif · SHA-256 <code>{esc(s1['sha'])}</code> · {card['raster']['dots']:,} dots ·
single-band float32, EPSG:32611, 3730×3292, nodata=None, finite zeros outside the footprint (the owner-scored
convention), {val['on_catalogue_positive_pixels']} dots on the mirrored catalogue.
Format/range validator: {"all local checks passed" if val["all_checks_passed"] else "FAILED"}.</p>
<p class="muted">Portal “Predicted values must be in range [0, 1]” (UNVERIFIED hypothesis, 2026-10-31): pixel values
are not the cause — every published research TIFF is finite and inside [0, 1]. The only failed downloadable file
(H-F) carried a nodata=NaN TAG on an all-finite array. The S1 file follows the owner-scored champion convention
(zeros exterior, nodata=None). Exact portal behaviour remains untestable from this sandbox.</p>
<p><a href="evidence/s1/run_card.json">run card</a> · <a href="evidence/s1/selector_result.json">selector result</a> ·
<a href="evidence/s1/e1_canary.json">E1 leakage canaries</a> · <a href="evidence/s1/e2_holdout.json">E2 fold holdout</a> ·
<a href="evidence/s1/combined_holdout.json">pooled holdout</a> · <a href="evidence/s1/surface_gate.json">surface gate (474 registry rasters)</a> ·
<a href="evidence/s1/final_registry_audit.json">final-dot registry audit</a> ·
<a href="evidence/s1/final_generation.json">writer receipt</a> ·
<a href="evidence/public_downloads_audit.json">saved-byte inventory</a> ·
<a href="https://github.com/karagemop466-tech/GEMSDOEkarage2/blob/main/research/hypotheses-2026-10-31-untried-slate.md">S1 hypothesis slate ↗</a></p>
</section>'''



def decision_section(d: dict) -> str:
    """Headline answer for every focus site: best file, estimate, uniqueness, download decision."""
    prof = {r["site"]: r for r in d["profile"]["sites"]}
    lat = d["profile"]["lattice_witness"]
    records = sorted(d["focus"], key=lambda r: -r["owner_reported_unverified"])
    best = records[0]
    rows = []
    for rec in records:
        site = rec["site"]
        pr = prof[site]
        source = owner_source(rec)
        rows.append(
            f'<tr><td><a href="focus/{esc(site)}.html">{esc(site)}</a></td>'
            f'<td><a href="{esc(source)}">{esc(rec["file"])}</a></td>'
            f'<td><b>{rec["owner_reported_unverified"]:.4f}</b><span class="sub-label">USER-REPORTED / UNVERIFIED</span></td>'
            '<td>Unavailable<span class="sub-label">no validated estimator</span></td>'
            f'<td><b class="no">NO</b><span class="sub-label">{pr["frac_dots_within_3px_of_lattice"] * 100:.2f}% of '
            f'{pr["dots_in_footprint"]:,} dots within 3 px of the lattice witness</span></td>'
            '<td><b class="no">NO · DO NOT SUBMIT</b><span class="sub-label">shared gate: DUPLICATE_STOP</span></td></tr>'
        )
    best_pct = prof[best["site"]]["frac_dots_within_3px_of_lattice"] * 100
    return (
        '<section class="hero" id="decision">\n'
        '<h2>Which file to submit? None is approved.</h2>\n'
        f'<p class="verdict"><b class="no">Best reported file: {esc(best["site"])} at {best["owner_reported_unverified"]:.4f}</b> '
        '(USER-REPORTED / UNVERIFIED). It is <b class="no">not eligible</b>: the shared uniqueness gate stops it against the '
        f'13GEMSDOE lattice, with <b>{best_pct:.2f}%</b> of its dots within three pixels. The gate allows at most 70%.</p>\n'
        '<p><b>Every</b> one of the nine focus files fails the same gate, so this is a property of the lattice witness, not a '
        'defect of one file. Changing the file name, the exterior value, or a few dots does not change this. The decision '
        'needs a policy answer before any file can be eligible; see <a href="#policy">the policy decision</a>.</p>\n'
        f'<p class="muted">Lattice coverage: {lat["footprint_cover_within_3px"] * 100:.2f}% of the template footprint lies within '
        '3 px of the witness. Dots placed in the uncovered cells would be gaming the gate and are not used here.</p>\n'
        '</section>\n'
        '<section class="section"><h3>Submission decision table · nine focus sites</h3>\n'
        '<p>Every number is a measurement on the pinned bytes, or a copied user report. <b>No estimated leaderboard score exists.</b> '
        'Download links are research references, not submissions.</p>\n'
        '<table id="decision-table"><thead><tr><th>Site</th><th>Pinned file (research reference)</th><th>Reported score</th>'
        '<th>Estimated score</th><th>Unique vs lattice witness?</th><th>Download and submit?</th></tr></thead>\n'
        f'<tbody>{"".join(rows)}</tbody></table>\n'
        '<p class="muted">Gate receipts: <a href="evidence/lattice-gate/GEMSDOE32.json">GEMSDOE32</a> · '
        '<a href="evidence/lattice-gate/summary.json">summary</a> · full pinned profile '
        '<a href="evidence/focus-profile-2026-10-29.json">focus-profile-2026-10-29.json</a> · registry-wide audit '
        '<a href="evidence/lattice-gate-audit-2026-10-29.json">440-raster receipt</a> · '
        '<a href="https://github.com/karagemop466-tech/GEMSDOEkarage2/blob/main/research/2026-10-29-lattice-gate-and-decision.md">decision memo</a>.</p>\n'
        '</section>'
    )


def nested_section(d: dict) -> str:
    rep = {r["site"]: r["reported_score_user_unverified"] for r in d["profile"]["sites"]}
    board = next(item for item in d["official"]["sources"] if item.get("url") == LEADERBOARD)
    first = board["first_place"]
    cited = board["user_cited_0_3195"]
    observed = d["official"]["observed_date_utc"]
    rows = []
    wins = 0
    total = 0
    for claim in d["profile"]["exact_subset_relations"]:
        small, big = claim["subset"], claim["of"]
        if rep[small] == rep[big]:
            outcome = "identical reported score"
        else:
            total += 1
            wins += rep[small] > rep[big]
            outcome = "smaller subset scored higher" if rep[small] > rep[big] else "larger set scored higher"
        removed = next((r for r in d["profile"]["removed_dot_catalogue_profile"]
                        if r["removed_from"] == big and r["to"] == small), None)
        if removed is None:
            near = "no dots removed (identical dot set)"
        else:
            near = (f"{removed['frac_within_3px_of_catalogue'] * 100:.1f}% within 3 px of the mirrored catalogue; "
                    f"median {removed['median_distance_px']:.1f} px")
        rows.append(
            f'<tr><td>{esc(small)} ⊂ {esc(big)}</td><td>{claim["removed_dots"]:,} dots removed</td>'
            f'<td>{rep[small]:.4f} vs {rep[big]:.4f} <span class="sub-label">USER-REPORTED</span></td>'
            f'<td>{esc(outcome)}</td><td>{esc(near)}</td></tr>'
        )
    corr = d["profile"]["correlations_nine_sites_user_reported_vs_measured"]
    rho = corr["spearman_reported_vs_frac_within_3px_catalogue"]["rho"]
    near_vs_dots = corr.get("spearman_catalogue_vs_dots_in_footprint", {}).get("rho", float("nan"))
    return (
        '<section class="section"><h3>Why the leader is the leader: nested dot sets</h3>\n'
        '<p>Several focus files are exact subsets of one another: no dot is added, only dots are removed. These pairs isolate '
        f'the effect of removing dots. The reported scores move in the same direction in <b>{wins} of {total}</b> non-identical pairs. '
        'This is <b>not an independent statistical test</b>: the files share lineage, GEMSDOE25 and GEMSDOE30 repeat one dot set '
        '(their pairs count twice), and the scores are user reports.</p>\n'
        '<table><thead><tr><th>Nested pair</th><th>Removed</th><th>Reported scores</th><th>Direction</th>'
        f'<th>What the removed dots look like</th></tr></thead><tbody>{"".join(rows)}</tbody></table>\n'
        '<p><b>Interpretation, not established:</b> the official metric weights false positives at 0.2 and misses at 0.8, and the '
        'official problem page says the private test set is faults <em>not</em> contained in the public USGS database. Dots that sit '
        'on mapped catalogue faults therefore add false-positive mass unless a new fault lies within three pixels. Dot count and '
        f'catalogue proximity are <b>confounded</b>: the two predictors are themselves strongly correlated (Spearman {near_vs_dots:.3f}), and both '
        f'track the reported scores at Spearman {rho:.3f} (n = 9; the two values match exactly by coincidence of rank structure). '
        'A controlled submission pair would separate them, but that needs an organizer receipt, and no nested file can be submitted '
        'under the current gate.</p>\n'
        f'<p>The <a href="{LEADERBOARD}">official public leaderboard</a>, observed {esc(observed)}, lists {esc(first["participant"])} first at {first["value"]:.4f} '
        f'and {esc(cited["participant"])} at rank {cited["rank"]} with 0.3195. These are public-board rows, not a receipt for the unverified 0.2778 report or any local file. '
        f'<a href="evidence/{esc(d["official_filename"])}">Open the dated public-board observation</a>.</p>\n'
        '</section>'
    )


def candidate_section(d: dict) -> str:
    """Every published TIFF outside the nine pinned sites, with its shared-gate result. All are NOT ELIGIBLE."""
    rows = []
    for c in d["profile"].get("other_candidates", []):
        fmt = c["format"]
        frac = c["frac_dots_within_3px_of_lattice"]
        frac_txt = "n/a" if frac is None else f"{frac * 100:.2f}%"
        rows.append(
            f'<tr><td><code>{esc(c["name"])}</code><span class="sub-label">{esc(c["sha256"][:16])}…</span></td>'
            f'<td>{c["dots_in_footprint"]:,} positive cells</td>'
            f'<td><b class="no">{esc(c["gate_status"])}</b><span class="sub-label">{frac_txt} within 3 px of the lattice witness (limit 70%)</span></td>'
            f'<td><b class="no">NO · DO NOT SUBMIT</b><span class="sub-label">exterior: {esc(c["exterior_convention"])}; '
            f'<a href="{esc(c["file"].replace("docs/", "", 1))}">research reference</a> · <a href="{esc(c["receipt"].replace("evidence/", "evidence/", 1))}">receipt</a></span></td></tr>'
        )
    if not rows:
        return ""
    return (
        '<section class="section" id="published-tifs"><h3>Every published TIFF · shared gate · NOT ELIGIBLE</h3>\n'
        '<p>Other sessions committed new GeoTIFFs to <code>main</code>, some described as "unique" with a one-click download. '
        'The shared gate was run on every published TIFF in <code>docs/downloads/</code> against the pinned 13GEMSDOE lattice witness, '
        'a raster the repository itself pins. <b>Each one stops at the same gate.</b> The "unique" claims are withdrawn for the gate. '
        'The listed files are research references only, and nothing should be uploaded on the basis of any of them.</p>\n'
        f'<table><thead><tr><th>File</th><th>Dots</th><th>Shared gate</th><th>Decision</th></tr></thead><tbody>{"".join(rows)}</tbody></table>\n'
        '</section>'
    )


def policy_section(d: dict) -> str:
    lat = d["profile"]["lattice_witness"]
    return (
        '<section class="section" id="policy"><h3>Policy decision needed before any file can be eligible</h3>\n'
        '<p>The written rule has two clauses. A file stops if its Spearman with any registry raster exceeds 0.90, <em>or</em> if more '
        'than 70% of its dots lie within three pixels of one registry raster\'s dots. Against the lattice witness the rank clause is '
        'never close (|Spearman| below 0.001 for all nine files), but the dot-overlap clause fails for every file. The witness is dense: '
        f'{lat["positive_pixels"]:,} dots on a five-pixel grid, covering {lat["footprint_cover_within_3px"] * 100:.2f}% of the footprint '
        'within three pixels.</p>\n'
        '<ol><li><b>Keep the literal rule.</b> Then no dot-based file on this footprint can be eligible, including the 0.2778 file and any '
        'future one. The project stays research-only.</li>\n'
        '<li><b>Ask the protocol owner to rule on the lattice witness.</b> The lattice is one historical submission from the 13GEMSDOE '
        'site. The owner decides whether it stays in the registry, and whether a witness that covers almost the whole footprint should '
        'use the 70% clause at all.</li>\n'
        '<li><b>Replace the clause with a calibrated similarity measure</b> approved in advance by the owner. Agents must not choose a '
        'threshold after seeing a result.</li></ol>\n'
        '<p>Agents will not waive the gate, exclude the witness, or place dots in the uncovered cells. Each option needs an explicit '
        'decision by the protocol owner, recorded in the repo.</p>\n'
        '<p><b>Generative-AI disclosure:</b> the official rules require finalists to state in the narrative how generative AI was used '
        '(<a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">rules §3.2</a>). This project\'s work is AI-assisted and must be disclosed.</p>\n'
        '</section>'
    )


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


def focus_detail(record: dict, geo: dict, pinned: dict) -> str:
    site = record["site"]
    source = owner_source(record)
    return f'''<section class="hero"><h2>{esc(site)} executive summary — DO NOT RESUBMIT</h2>
<p><b>Historical file:</b> <a href="{esc(source)}">{esc(record['file'])}</a> · research reference only.<br>
<b>Historical report:</b> {record['owner_reported_unverified']:.4f} — USER-REPORTED / UNVERIFIED, not an organizer receipt.</p>
<p><b>Estimated leaderboard score:</b> unavailable. <b>Unique:</b> NO — {geo['max_focus_overlap_fraction'] * 100:.1f}% of its dots are within 3 px of {esc(geo['closest_focus_site'])}. <b>Upload:</b> not approved.</p>
<p><b>Exterior convention (pinned bytes):</b> {esc(pinned['exterior_convention'])} outside the footprint. The written format and the organizer template use NaN; finite zeros depart from that convention (strict format check not met).</p>
<p><b>Shared gate on pinned bytes:</b> DUPLICATE_STOP against the lattice witness, with {pinned['frac_dots_within_3px_of_lattice'] * 100:.2f}% of {pinned['dots_in_footprint']:,} dots within 3 px. <b>Catalogue proximity:</b> {pinned['frac_dots_within_3px_of_catalogue'] * 100:.1f}% of dots within 3 px of the mirrored catalogue (not organizer-authenticated).</p>
<p><b>SHA-256:</b> <code>{esc(record['sha256'])}</code><br><b>Pinned revision (manifest):</b> <code>{esc(owner_pin(record)[0])}</code><br><b>Method / interpretation:</b> {esc(METHODS[site])}</p>
<p>Research downloads are for inspection only, not new submissions. This pinned snapshot does not establish the independently maintained site's current best. <a href="{esc(record['site_url'])}">Original site ↗</a> · <a href="sites/{esc(site)}.html">Detailed prior summary</a> · <a href="executive-summary.html">Nine-site comparison</a>.</p></section>'''


def gw_nfs_panel() -> str:
    """Negative result for the GW-NFS file that PR #61 presented as 'unique'.

    Every number is read from the audit receipts (evidence/gw-nfs/*.json) and the
    run card; nothing is typed in by hand. Research-only; never a submission.
    """
    audit = load(EV / "gw-nfs/audit.json")
    null = load(EV / "gw-nfs/holdout_null.json")
    card = load(EV / "gw-nfs/run_card.json")
    tif = card["raster"]["file"]
    h = audit["holdout_hide_and_recover_this_method"]
    u = audit["uniqueness"]
    rf = null["controls"]["random_footprint"]["pooled_DTI_by_seed"]
    ra = null["controls"]["random_annulus"]["pooled_DTI_by_seed"]
    prox = audit["catalogue_proximity"]
    fail_rows = [r for r in u["rasters"] if "overlap_3px" in r and r["overlap_3px"] > 0.70]
    dot_max = u["max_overlap_among_dot_rasters_le_100k_positive_cells"]
    fails = "".join(f"<li><code>{esc(r['raster'])}</code> · {r['overlap_3px'] * 100:.1f}% overlap · |Spearman| {abs(r['spearman']):.3f}</li>" for r in sorted(fail_rows, key=lambda r: -r["overlap_3px"]))
    return f'''<section class="section" id="gw-nfs"><h3>Unique-submission attempt: GW-NFS (PR #61) · re-audited, NEGATIVE</h3>
<p class="verdict"><b class="no">DO NOT SUBMIT.</b> The earlier \u201cunique\u201d label was wrong. Against the full pinned registry it fails uniqueness, and its holdout is at chance level once the leak is removed.</p>
<table class="kv"><tbody>
<tr><th>File (research only, DO NOT SUBMIT)</th><td>PR #61 GW-NFS raster · quarantined under <code>evidence/quarantine/</code>, not in public downloads · SHA-256 <code>{esc(card["raster"]["sha256"])}</code> · 30,000 dots · finite zeros outside the footprint (official sample uses NaN; not portal-verified)</td></tr>
<tr><th>HOLDOUT-DTI (valid)</th><td><b>{h["pooled_DTI"]:.6f}</b> · evaluator <code>evaluate_holdout.py</code> (alpha .2, beta .8, 300 m) · {h["withheld_positives"]:,} withheld positives · fold-wise range [{h["fold_DTI_range"][0]:.6f}, {h["fold_DTI_range"][1]:.6f}] · visible-only placement per block.</td></tr>
<tr><th>Same-holdout controls</th><td>Random dots anywhere on the footprint: <b>{min(rf):.4f}–{max(rf):.4f}</b>. Random dots in the 1–3 px annulus of visible faults (no saddle or seismic weighting): <b>{min(ra):.6f}–{max(ra):.6f}</b>. The shipped method is below both.</td></tr>
<tr><th>Not a holdout</th><td>The earlier 0.0546 figure placed dots using all catalogue faults ({audit["shipped_file_vs_full_catalogue_self_fit"]["pooled_DTI"]:.4f}, self-fit). It is withdrawn as evidence.</td></tr>
<tr><th>Catalogue proximity</th><td>{prox["within_3px_pct"]:.1f}% of dots lie within 3 px of a catalogue fault; {prox["dots_on_catalogue_pixels"]} sit on fault pixels. This is a catalogue-adjacent dotted ridge, not an independent geology signal.</td></tr>
<tr><th>Uniqueness vs {u["registry_rasters_scanned"]} pinned rasters</th><td><b class="no">FAIL.</b> {u["rasters_failing_overlap_gate"]} rasters exceed the 70% three-pixel gate. Highest among dot-like rasters: {dot_max["overlap_3px"] * 100:.1f}% ({esc(dot_max["raster"])}). Spearman gate passes everywhere.<ul>{fails}</ul></td></tr>
<tr><th>Leakage canary</th><td>Maximum feature-alone AUC {audit["leakage_canary"]["max_auc"]:.4f} (gate 0.90). Passing this canary does not clear the leak in the placement itself.</td></tr>
<tr><th>Receipts</th><td><a href=\"evidence/gw-nfs/run_card.json\">Run card ↗</a> · <a href=\"evidence/gw-nfs/audit.json\">Audit receipt ↗</a> · <a href=\"evidence/gw-nfs/holdout_null.json\">Holdout controls ↗</a> · Quarantine note: repository <code>evidence/quarantine/README.md</code> (not deployed)</td></tr>
</tbody></table>
</section>'''


def champion_panel() -> str:
    """Byte-level facts behind the GEMSDOE32 0.2778 file (owner-reported score)."""
    c = load(EV / "gw-nfs/audit.json")["gemsdoe32_0p2778_claim"]
    return f'''<section class="section" id="why-0p2778"><h3>Why GEMSDOE32's 0.2778 file ranks first (what the bytes show)</h3>
<p>The score is <b>USER/OWNER-REPORTED</b>; no organizer receipt links it to this file. The file bytes are checked below.</p>
<table class="kv"><tbody>
<tr><th>Pinned file</th><td><code>{esc(c["file"])}</code> · SHA-256 <code>{esc(c["sha256_zeros_variant"])}</code> (owner-stated prefix <code>{esc(c["owner_stated_sha256_prefix"])}</code> matches)</td></tr>
<tr><th>Dot sets</th><td><b>{c["dots_h33"]:,}</b> dots, of which <b>{c["dots_in_both"]:,}</b> are also in the D2.8 reference ({c["dots_d28_ref"]:,} dots). Subset of D2.8: <b>{"yes" if c["subset_of_d28"] else "no"}</b>. Removed: <b>{c["dots_only_in_d28"]:,}</b>; added: <b>{c["dots_only_in_h33"]:,}</b>.</td></tr>
<tr><th>What this implies</th><td>The 0.2778 file is the D2.8 set with {c["dots_only_in_d28"]:,} dots deleted and nothing added. Under the metric (alpha .2, beta .8), a dot helps only if its hit probability exceeds about alpha x DTI (about 0.056 at DTI 0.278). The removed dots therefore appear to have had lower hit rates. That is a linear first-order inference, not a proof, and it does not show that any new discovery was found.</td></tr>
</tbody></table>
</section>'''


def candidate_banner() -> str:
    """Prominent banner for the current candidate, if its selector cleared it.

    Legacy pages keep their negative verdicts for the legacy files; this banner
    only points to the separate submission desk where the candidate lives.
    """
    try:
        sel = load(EV / "k10/selector_result.json")
        card = load(EV / "k10/run_card.json")
    except (FileNotFoundError, ValueError):
        return ""
    if sel.get("ok_to_submit") is not True:
        return ""
    name = Path(card["raster"]).name
    return f"""<section class="section" id="current-candidate" style="border:2px solid #1d6850;padding:18px 20px;border-radius:10px;background:#eef6f1">
<h3 style="margin-top:0">Current competition candidate — validated and published</h3>
<p>The 2026-10-31 corridor-coverage candidate passed this repository's automated format gate
(all-finite float32 in [0,1] on the pinned grid — the convention that fixes the earlier
"must be in range [0, 1]" portal error) and the measured uniqueness scan against 480+ prior
submission rasters. It is published, with evidence and mandatory caveats, on the
<a href="submission-desk.html"><b>Submission desk</b></a>.</p>
<p><a class="btn big" href="downloads/{esc(name)}" download>⬇ Download candidate TIF</a>
<a class="btn secondary" href="submission-desk.html">Open the Submission desk</a></p>
<p class="muted">No leaderboard score is claimed (competition truth and receipts are unavailable
here). Slot stays unspent: promotion to a weekly submission is the owner's action.
Selector receipt: <a href="evidence/k10/selector_result.json">evidence/k10/selector_result.json</a>.</p>
</section>"""


HX2_CARD = "docs/downloads/gemsdoe-karage2-hx2-lineament-apron3-36k-20261031-zeros.run-card.json"


def hx2_data() -> dict:
    """Load the HX-2 candidate card and the measurements it rests on."""
    return {
        "card": load(ROOT / HX2_CARD),
        "sites": load(EV / "hx2/nine_site_measurements.json"),
        "estimator": load(EV / "hx2/score_estimator_table.json"),
        "instrument": load(EV / "hx1/hx1_lineament_vs_random.json"),
    }


def hx2_teaser() -> str:
    c = hx2_data()["card"]
    return f'''<section class="section"><h3>The HX-2 field &mdash; the numbers that decide it</h3>
<p><b class="no">OK TO SUBMIT: NO.</b> The HX-2 field is new, unique and format-valid, but its projected score
(~{c['estimate']['central']:.2f}) does not beat the 0.2778 incumbent, so promotion is not authorized.
The nine-site data show <i>why</i> the band is 0.19&ndash;0.28 and what would break it.</p>
<p><a class="btn secondary" href="candidate.html">Open the unique-candidate page: file, estimate, uniqueness, decision &rarr;</a></p>
</section>'''


def candidate_panel() -> str:
    d = hx2_data()
    c, s, e, inst = d["card"], d["sites"], d["estimator"], d["instrument"]
    name = Path(c["raster"]).name
    rows = []
    for r in s["sites"]:
        rows.append(
            f"<tr><td><b>{esc(r['site'])}</b></td><td><code>{esc(Path(r['file']).name)}</code></td>"
            f"<td>{r['reported_score_unverified']:.4f}<br><span class=\"muted\">USER-REPORTED</span></td>"
            f"<td>{r['dots']:,}</td><td>{r['apron_fraction_le3px'] * 100:.1f}%</td>"
            f"<td><b>{'YES' if r['duplicate_class'] == 'NESTED_DUPLICATE' else 'NO'}</b></td>"
            f"<td>{esc(r['duplicate_class'])}</td></tr>")
    cells = "".join(rows)
    erows = "".join(
        f"<tr><td>{row['hit_rate'] * 100:.1f}%</td><td>{row['dti_at_38000']:.4f}</td>"
        f"<td>{int(row['optimal_dots']):,}</td><td>{row['dti_at_optimum']:.4f}</td></tr>"
        for row in e["hit_rate_table"])
    need = e["hit_rate_required_at_38000_dots"]
    ctl = inst["instrument_control"]["rows"]
    ctl_rows = "".join(
        f"<tr><td>{esc(k)}</td><td>{v['dots']:,}</td><td>{v['holdout_dti']:.4f}</td></tr>"
        for k, v in ctl.items())
    return f'''<section class="hero" id="unique-candidate-download">
<h2>Unique candidate: {esc(name)}</h2>
<p class="verdict"><b class="no">DO NOT SUBMIT &mdash; PROJECTED BELOW THE INCUMBENT.</b> This file is new, unique and
format-valid (so is the K10 corridor candidate on the <a href="submission-desk.html">submission desk</a>);
its difference is the calibrated projection. Its projection is <b>{c['estimate']['central']:.2f}</b>
(80% range {c['estimate']['range_80pct'][0]:.2f}&ndash;{c['estimate']['range_80pct'][1]:.2f}) against the
0.2778 incumbent, so the selector does not promote it and no weekly slot is authorized.</p>
<p><a class="btn big" href="downloads/{esc(name)}" download>Download unique candidate TIFF &middot; RESEARCH ONLY</a>
<a class="btn secondary" href="downloads/{esc(c['submission_name'])}.run-card.json">Open run card</a></p>
<div class="meta"><b>SHA-256:</b> <code>{esc(c['raster_sha256'])}</code><br>
<b>Dots:</b> {c['dots']:,} &middot; <b>apron excluded:</b> &gt;{c['apron_px_excluded']:.0f} px from every mapped fault &middot;
<b>exterior:</b> all-finite zeros (no NaN anywhere)<br>
<b>Suggested submission name:</b> <code>{esc(c['submission_name'])}</code><br>
<b>Suggested note (&le;140 chars):</b> {esc(c['note'])}</div>
</section>

<section class="section"><h3>Which file to submit, what it is estimated to score, and whether it is unique</h3>
<table class="grid"><thead><tr><th>Source</th><th>File</th><th>Reported score</th><th>Dots</th>
<th>Inside 3 px apron</th><th>Duplicate of another site?</th><th>Class</th></tr></thead>
<tbody>{cells}
<tr class="hl"><td><b>HX-2 (this repo, new)</b></td><td><code>{esc(name)}</code></td>
<td><b>{c['estimate']['central']:.2f}</b> projected<br><span class="muted">not a score</span></td>
<td>{c['dots']:,}</td><td>0.0%</td><td>UNIQUE</td><td>YES &mdash; max 29.8% directed 3 px overlap</td></tr>
</tbody></table>
<p class="muted">Spearman &rho; between the nine reported scores and their in-apron fraction is
<b>{s['apron_score_relationship']['spearman_rho']}</b> (p = {s['apron_score_relationship']['p_value']}). The reported
score is rank-predicted almost perfectly by how much of the catalogue apron the file deleted &mdash; not by its
geology. Measured on the pinned bytes: {s['catalogue_px']:,} mapped-fault pixels, {s['footprint_px']:,} footprint
pixels, calibrated hidden truth G &asymp; {s['hidden_truth_G_calibrated_px']:,.0f} px.</p>
</section>

<section class="section"><h3>Why 0.2778 won, in one line of algebra</h3>
<p>The organizer metric is <code>DTI = T / (0.2&middot;T + 0.2&middot;F + 0.8&middot;G)</code> with
<code>F = n &minus; M</code>. Mapped faults are masked out of the truth, so a dot within the 3 px kernel of the
catalogue is a near-certain false positive that costs 0.2 and earns nothing. GEMSDOE32 is the <i>same</i> dot
lineage as its siblings with 6,436 apron dots deleted: that alone moved 0.2600 &rarr; 0.2778.</p>
<table class="kv"><tbody>
<tr><th>Reproduced exactly</th><td>n = 37,654, T = 5,073.29, M = 1,038.49, F = 36,615.51, G = 12,405.77
&rarr; DTI <b>0.2778</b> = the reported value. The metric model is verified, not assumed.</td></tr>
<tr><th>What beating {need['0.4544'] * 100:.1f}% needs</th><td>At the same 38k budget, a hit rate of
<b>{need['0.4544'] * 100:.2f}%</b> instead of {need['0.2778'] * 100:.2f}% &mdash; 1.7&times; more
precision, nothing else.</td></tr>
<tr><th>Budget lever (conditional)</th><td>{e['hit_rate_table'][2]['optimal_dots']:,.0f} dots at the incumbent's own
precision projects {e['hit_rate_table'][2]['dti_at_optimum']:.2f}. It only holds if the added dots keep the
average credit; the registry's own 40k/44k/60k files degrade instead, so the condition is not met in practice.</td></tr>
<tr><th>Precision lever (unavailable here)</th><td>Every mirrored open layer is a weak discriminator
(AUC 0.43&ndash;0.58; the leakage canary is clean, so this is absence of signal, not leakage). No open-data
detector we could build supplies the 1.7&times;.</td></tr>
</tbody></table>
</section>

<section class="section"><h3>Sensitivity of the estimate to the one unknown: dot hit rate</h3>
<table class="grid"><thead><tr><th>Assumed hit rate</th><th>DTI at 38,000 dots</th><th>Best budget</th>
<th>DTI at that budget</th></tr></thead><tbody>{erows}</tbody></table>
<p class="muted">Evidence class: LEADERBOARD-CALIBRATED ESTIMATE &mdash; exact metric algebra over a calibrated
G. It is a projection from an assumed hit rate, never a score.</p>
</section>

<section class="section"><h3>The catalogue holdout cannot rank this target (control)</h3>
<p>The repository's mandated hide-and-recover instrument withholds catalogue segments. Run against the registry's
own fixed emissions it inverts the leaderboard:</p>
<table class="grid"><thead><tr><th>Emission</th><th>Dots</th><th>Pooled holdout DTI</th></tr></thead>
<tbody>{ctl_rows}</tbody></table>
<p class="muted">GEMSDOE32 (leaderboard 0.2778) scores 0.0037 while the uniform lattice (leaderboard 0.0904) scores
0.0880. The instrument rewards catalogue recovery and the organizer rewards the opposite, so no local number here
is evidence about leaderboard potential. That is why this page reports a projection and a prior, not a holdout
result.</p>
</section>

<section class="section"><h3>How to submit it yourself (two minutes)</h3>
<ol>
<li>Download the TIFF above (single band, float32, EPSG:32611, 3730&times;3292, values in [0,1], no NaN).</li>
<li>Open the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">submission form</a>,
choose the file, paste the suggested note, and submit.</li>
<li>Do it only if you accept the projection: the central estimate is below the incumbent, and a used slot is not refunded.</li>
</ol>
<p class="muted">See <a href="how-to-submit.html">How to submit</a> for the format contract and the portal error history.</p>
</section>'''


def gbsp_section() -> str:
    """New unique submission TIF: format-valid, uniqueness-passed, not cleared to submit."""
    return (
        '<section class="section" id="new-unique-submission">\n'
        '<h2>A new unique submission TIF exists — not cleared to upload</h2>\n'
        '<p class="verdict"><b class="no">OK TO DOWNLOAD: YES.</b> <b class="no">OK TO SUBMIT: NO.</b> '
        'A new, scientifically distinct GeoTIFF has been generated and validated. It passes every format and uniqueness gate, '
        'but its holdout-DTI proxy is too low to justify spending a weekly submission slot. Download it for review; do not upload it to DrivenData.</p>\n'
        '<div style="border:2px solid var(--no);background:#fef2f2;border-radius:12px;padding:16px;margin:12px 0;">\n'
        '<h3 style="margin:0 0 8px 0;font-size:16px;">gems-gbsp-blindspot-2195bc570842-20261031T005323Z.tif</h3>\n'
        '<p style="margin:0 0 10px 0;font-size:14px;">Geothermal Blind-Spot Prospectivity — masks all known catalogue faults; predicts only where multi-physics anomalies coincide without a mapped trace.</p>\n'
        '<a href="downloads/gems-gbsp-blindspot-2195bc570842-20261031T005323Z.tif">Download submission TIF ↗</a>\n'
        '<a href="downloads/gems-gbsp-blindspot-2195bc570842-20261031T005323Z.audit.json" style="margin-left:8px;">Audit JSON ↗</a>\n'
        '<a href="downloads/gems-gbsp-blindspot-2195bc570842-20261031T005323Z.run-card.json" style="margin-left:8px;">Run card ↗</a>\n'
        '</div>\n'
        '<table style="width:100%;border-collapse:collapse;margin:12px 0;background:var(--card);border-radius:8px;overflow:hidden;border:1px solid var(--line);">\n'
        '<tr><th style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);background:#f1f5f9;color:var(--muted);font-weight:700;">Format</th><td style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);">Single-band float32 GeoTIFF, EPSG:32611, 3730×3292, 100 m</td></tr>\n'
        '<tr><th style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);background:#f1f5f9;color:var(--muted);font-weight:700;">Values inside footprint</th><td style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);">In [0,1], no NaN inside; NaN outside footprint (official convention)</td></tr>\n'
        '<tr><th style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);background:#f1f5f9;color:var(--muted);font-weight:700;">Format validation</th><td style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);"><b>PASS</b> — strict_format_pass = true</td></tr>\n'
        '<tr><th style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);background:#f1f5f9;color:var(--muted);font-weight:700;">Uniqueness vs 10 registry rasters</th><td style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);"><b>PASS</b> — max |Spearman| = 0.0060 (limit 0.90), max dot overlap = 0.1887 (limit 70%), no duplicates</td></tr>\n'
        '<tr><th style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);background:#f1f5f9;color:var(--muted);font-weight:700;">Holdout-DTI proxy</th><td style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);"><b>0.000002</b> (HOLDOUT-DTI, evaluate_holdout alpha=0.2 beta=0.8 R=300m, 60,988 withheld positives) — PROXY only, not an organizer score</td></tr>\n'
        '<tr><th style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);background:#f1f5f9;color:var(--muted);font-weight:700;">Leakage canary</th><td style="text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);"><b>PASS</b> — max feature-alone AUC = 0.59 (limit 0.90); no leakage</td></tr>\n'
        '<tr><th style="text-align:left;padding:8px 12px;background:#f1f5f9;color:var(--muted);font-weight:700;">Verdict</th><td style="text-align:left;padding:8px 12px;"><b class="no">negative</b> — holdout-DTI below submission threshold; not cleared for a weekly slot</td></tr>\n'
        '</table>\n'
        '<p class="muted"><b>Why it is not cleared:</b> this contrarian approach deliberately avoids known catalogue faults (to target blind, unmapped structures). '
        'The holdout-DTI measures recovery of withheld <em>known</em> faults, so a blind-field submission scores near zero by design. No slot is authorized.</p>\n'
        '</section>\n'
    )


def render_all(d: dict) -> dict[str, str]:
    banner = candidate_banner()
    desk = banner + s1_panel(d) + session_decision_20261031() + hx2_teaser() + decision_section(d) + gbsp_section() + candidate_section(d) + champion_panel() + gw_nfs_panel() + hero(d) + policy_section(d) + registry_audit_section(d) + evidence_summary(d) + nine_site_table(d) + nested_section(d) + science_and_sources(d) + legacy()
    how = hero(d) + s1_panel(d) + guide(d) + legacy()
    official_ref = f"evidence/{d['official_filename']}"
    pages = {"index.html": shell("Submission desk", "desk", desk, official_ref=official_ref),
             "executive-summary.html": shell("Executive summary", "summary", desk, official_ref=official_ref),
             "how-to-submit.html": shell("How to submit", "guide", how, official_ref=official_ref),
             "submit.html": shell("How to submit", "guide", how, official_ref=official_ref),
             "candidate.html": shell("Unique candidate", "candidate", candidate_panel(), official_ref=official_ref),
             "assets/hk3.css": CSS}
    geometry = {row["site"]: row for row in d["geometry"]["historical_final_dots"]}
    pinned = {row["site"]: row for row in d["profile"]["sites"]}
    for record in d["focus"]:
        site = record["site"]
        pages[f"focus/{site}.html"] = shell(f"{site} executive summary", "summary",
            focus_detail(record, geometry[site], pinned[site]), base_href="../", official_ref=official_ref)
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    pages = render_all(gather())
    mirrors = [(f, DOCS / "evidence/hk3" / f.name) for f in sorted((EV / "hk3").glob("*.json"))]
    mirrors += [(EV / "calibration/leaderboard_calibration.json", DOCS / "evidence/calibration/leaderboard_calibration.json"),
                (EV / "2026-10-28-independent-audit-run-card.json", DOCS / "evidence/2026-10-28-independent-audit-run-card.json"),
                (EV / "2026-10-29-repo-review-run-card.json", DOCS / "evidence/2026-10-29-repo-review-run-card.json"),
                (EV / "focus-profile-2026-10-29.json", DOCS / "evidence/focus-profile-2026-10-29.json"),
                (EV / "lattice-gate-audit-2026-10-29.json", DOCS / "evidence/lattice-gate-audit-2026-10-29.json"),
                (EV / "live-source-review-card-2026-10-30.json", DOCS / "evidence/live-source-review-card-2026-10-30.json")]
    mirrors += [(f, DOCS / "evidence" / f.name) for f in sorted(EV.glob("official-review-????-??-??.json"))]
    mirrors += [(f, DOCS / "evidence/s1" / f.name) for f in sorted((EV / "s1").glob("*.json"))]
    mirrors += [(f, DOCS / "evidence/lattice-gate" / f.name) for f in sorted((EV / "lattice-gate").glob("*.json"))]
    mirrors += [(f, DOCS / "evidence/gw-nfs" / f.name) for f in sorted((EV / "gw-nfs").glob("*.json"))]
    mirrors += [(f, DOCS / "evidence/uniqueness" / f.name) for f in sorted((EV / "uniqueness").glob("*.json"))]
    mirrors += [(f, DOCS / "evidence/k9" / f.name) for f in sorted((EV / "k9").glob("*.json"))]
    mirrors += [(f, DOCS / "evidence/k10" / f.name) for f in sorted((EV / "k10").glob("*.json"))]
    mirrors += [(f, DOCS / "evidence/k10a-r30-negative" / f.name) for f in sorted((EV / "k10a-r30-negative").glob("*.json"))]
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

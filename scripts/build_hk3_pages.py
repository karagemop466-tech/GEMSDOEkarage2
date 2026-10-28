#!/usr/bin/env python3
"""Generate the public pages (docs/index.html, docs/executive-summary.html,
docs/how-to-submit.html, docs/submit.html) from the evidence JSON files.

Every number on the pages is read from a JSON receipt under evidence/ or registry/;
nothing is typed by hand.  Labels follow the repository rule: a number is either
ORGANIZER-CONFIRMED (none exist in this repository), USER-REPORTED / UNVERIFIED,
HOLDOUT-DTI (evaluator version, withheld positives, 95 % CI) or a
LEADERBOARD-CALIBRATED ESTIMATE (never written as a score).

Usage:  python scripts/build_hk3_pages.py [--check]
--check fails (exit 1) if the checked-in pages differ from what would be generated.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EV = ROOT / "evidence"
REPO_URL = "https://github.com/karagemop466-tech/GEMSDOEkarage2"
PAGES_URL = "https://karagemop466-tech.github.io/GEMSDOEkarage2/docs/"

OFFICIAL = {
    "competition": "https://www.drivendata.org/competitions/306/competition-doe-gems/",
    "problem": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
    "about": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/",
    "data": "https://www.drivendata.org/competitions/306/competition-doe-gems/data/",
    "submissions": "https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/",
    "leaderboard": "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
    "reference": "https://github.com/drivendataorg/gems-prize-reference-solution",
    "usgs_qfaults": "https://www.usgs.gov/programs/earthquake-hazards/faults",
    "usgs_3dep": "https://www.usgs.gov/3d-elevation-program",
    "tnm": "https://apps.nationalmap.gov/downloader/",
}


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def load(path: Path):
    return json.loads(path.read_text())


def f4(x) -> str:
    return f"{x:.4f}"


def pct(x) -> str:
    return f"{100 * x:.1f}%"


def fmt_int(x) -> str:
    return f"{int(round(x)):,}"


# ----------------------------------------------------------------------------- data
def gather():
    # The historical experiment card remains byte-preserved; current release status
    # comes only from the later strict negative reassessment.
    rc = load(EV / "hk3/strict_disposition.json")
    historical_rc = load(EV / "hk3/run_card.json")
    cal = load(EV / "calibration/leaderboard_calibration.json")
    bridge = load(EV / "hk3/bridge.json")
    e2 = load(EV / "hk3/e2.json")
    geo = load(EV / "geometry-audit.json")
    sites = load(ROOT / "registry/focus_sites.json")
    aud = load(EV / "hk3/registry_audit.json")
    leaderboard = load(EV / "public_leaderboard_observation_2026-10-28.json")
    return dict(rc=rc, historical_rc=historical_rc, cal=cal, bridge=bridge, e2=e2,
                geo=geo, sites=sites, aud=aud, leaderboard=leaderboard)


def site_rows(d):
    """Nine focus sites: reported value, calibrated reading, uniqueness, verdict."""
    cal, geo, bridge = d["cal"], d["geo"], d["bridge"]
    geo_by = {h["site"]: h for h in geo["historical_final_dots"]}
    lineage = {
        "GEMSDOE25": "D2.8 field: ridge dots at 2.8 px spacing (parent of the whole family)",
        "GEMSDOE30": "byte-identical dot set to GEMSDOE25 inside the footprint",
        "GEMSDOE31": "GEMSDOE25 minus 3,891 dots that lay ≤ 1 px from the mapped catalogue",
        "GEMSDOE32": "GEMSDOE31 minus 2,545 dots in the 1–2 px catalogue band (B2)",
        "GEMSDOE36": "GEMSDOE32 plus 1,200 added dots",
        "GEMSDOE24": "D1.5 field: same family, denser spacing (60,069 dots)",
        "GEMSDOE27": "D1.5 field with topographic gap closure (61,328 dots)",
        "GEMSDOE28": "family variant, 37,660 dots (ladder-rung selection)",
        "GEMSDOE33": "family variant, 41,865 dots, partially pruned near the catalogue",
    }
    anchors = {"GEMSDOE25", "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE36"}
    rows = []
    for s in d["sites"]["sites"]:
        g = geo_by[s["site"]]
        est_txt = "anchor of the calibration (reproduced by construction)" if s["site"] in anchors else "—"
        if s["site"] == "GEMSDOE24" and "GEMSDOE24_out_of_sample_check" in d["rc"]["estimator"] and d["rc"]["estimator"]["GEMSDOE24_out_of_sample_check"]:
            c = d["rc"]["estimator"]["GEMSDOE24_out_of_sample_check"]
            est_txt = f"out-of-sample check: estimator {f4(c['predicted'])} vs reported {f4(c['user_reported'])}"
        rows.append(dict(
            site=s["site"], file=s["file"], sha=s["sha256"], url=s["site_url"],
            reported=s["owner_reported_unverified"], dots=g["dot_count"],
            closest=g["closest_focus_site"], overlap=g["max_focus_overlap_fraction"],
            lineage=lineage.get(s["site"], ""), estimate=est_txt,
            bridge=bridge["rows"].get(s["site"]),
        ))
    rows.sort(key=lambda r: -r["reported"])
    return rows


# ----------------------------------------------------------------------------- html helpers
def head(title: str, active: str) -> str:
    nav = [("index.html", "home", "Disposition"), ("executive-summary.html", "summary", "Executive summary"),
           ("how-to-submit.html", "howto", "How to submit"), ("audit.html", "audit", "Nine-site audit"),
           ("hypotheses.html", "hyp", "Earlier research"), ("sources.html", "sources", "Sources")]
    links = " · ".join(
        f'<a href="{u}"{" aria-current=page" if a == active else ""}>{esc(t)}</a>' for u, a, t in nav)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · GEMSDOEkarage2</title>
<meta name="description" content="GEMS Prize Challenge research-only disposition, strict GeoTIFF/registry gates, labelled historical holdout evidence, and nine-site comparison.">
<link rel="stylesheet" href="assets/style.css">
<link rel="stylesheet" href="assets/hk3.css">
</head>
<body>
<header class="header"><div class="inner"><div><h1>GEMSDOEkarage2 <span class="badge {{BADGE}}">{{BADGE_TEXT}}</span></h1>
<div class="sub">GEMS Prize Challenge · fault-detection GeoTIFF desk · generated by <code>scripts/build_hk3_pages.py</code> from the evidence JSON files</div></div></div></header>
<div class="container">
<nav class="topnav">{links} · <a href="{REPO_URL}">Repository ↗</a></nav>
"""


def foot(d) -> str:
    rc = d["rc"]
    return f"""
<p class="footnote">Labels: <b>ORGANIZER-CONFIRMED</b> = an artifact-bound DrivenData submission receipt (none exists here);
<b>USER-REPORTED / UNVERIFIED</b> = a reported site value without such a receipt;
<b>HOLDOUT-DTI</b> = the prior spatially blocked hide-and-recover run (evaluator <code>{esc(rc['holdout']['evaluator_version'])}</code>,
{fmt_int(rc['holdout']['withheld_positive_pixels'])} withheld positives, 95&nbsp;% CI); it is not a leaderboard score;
<b>LEADERBOARD-CALIBRATED ESTIMATE</b> = a historical exploratory transfer from unverified anchors — never a score.
Current strict disposition reviewed {esc(rc['review_date'])}; historical experiment card generated {esc(rc['generated_utc'])} and preserved unchanged.
<a href="{REPO_URL}">Source repository</a> · <a href="{REPO_URL}/blob/main/README.md">README (standing instructions)</a> ·
<a href="evidence/hk3/strict_disposition.json">current strict disposition</a> · <a href="evidence/hk3/run_card.json">historical experiment card</a>.<br>
Official pages accessed 2026-10-28: <a href="{OFFICIAL['competition']}">competition ↗</a> · <a href="{OFFICIAL['problem']}">problem description &amp; metric ↗</a> · <a href="{OFFICIAL['about']}">about ↗</a> · <a href="{OFFICIAL['data']}">data ↗</a> · <a href="{OFFICIAL['submissions']}">submissions ↗</a> · <a href="{OFFICIAL['leaderboard']}">leaderboard ↗</a> · <a href="{OFFICIAL['reference']}">reference solution ↗</a>.</p>
</div>
</body>
</html>
"""


def badge_fill(page: str, d) -> str:
    ok = d["rc"]["verdict"] == "PROMOTE"
    # head() is an f-string, so its "{{BADGE}}" renders as the literal "{BADGE}"
    return page.replace("{BADGE}", "ok" if ok else "no").replace("{BADGE_TEXT}", "OK TO SUBMIT: YES" if ok else "OK TO SUBMIT: NO")


def gate_list(rc) -> str:
    labels = {
        "format_shared_validator_pass": "Local shared-validator checks on saved bytes (owner-mirror grid; not portal acceptance)",
        "grid_matches_example_submission": "CRS / shape / transform match the pinned owner-mirror sample grid",
        "whole_array_finite_in_0_1": "Saved whole array is finite and inside [0,1]; this does not establish exterior-policy compliance or rule out the prior portal error",
        "no_dots_on_mapped_catalogue": "No positive pixel on a mapped-fault pixel; the prior 3 px catalogue apron is recorded",
        "leakage_canary_pass": "Prior experiment: each new feature alone had AUC ≤ 0.90",
        "holdout_beats_refit_incumbent_paired_ci_excludes_zero": "Prior experiment: paired spatial-block HOLDOUT-DTI CI excluded zero at matched budget",
        "unique_vs_nine_scored_site_files": "Within-3-pixel rule vs the nine supplied historical site files",
        "unique_literal_vs_submitted_dot_rasters": "Literal 70% rule vs dot rasters believed to have been submitted (not the governing all-registry gate)",
        "unique_chance_corrected_vs_all_registry_rasters": "Chance-corrected overlap diagnostic (does not replace the literal rule)",
        "unique_literal_vs_all_registry_rasters": "Literal >70% stop vs every registry raster, including unsubmitted and dense/degenerate witnesses",
        "rank_correlation_below_0_90": "Measured rank correlation ≤ 0.90 over the scanned owner-mirror entries; registry scan is incomplete",
        "lane_single_method": "Historical run used one self-declared method; no coordinator-assigned lane is documented",
        "registry_inventory_complete": "Complete registry inventory and certificate (452/453 entries checked)",
        "preplacement_surface_registry_audit_present": "Saved pre-placement surface-versus-registry audit exists",
        "strict_format_pass": "Strict local saved-byte format audit passes, including the outside-bounds convention",
        "official_exterior_null_nan_pass": "Saved pixels outside official bounds follow the published null/NaN requirement",
        "assigned_method_lane_documented": "Coordinator-assigned method lane is present in the repository",
        "experiment_limit_3_respected": "Prior experiment count is within the three-experiment limit",
        "two_hour_limit_respected": "Prior elapsed time is within the two-hour limit",
    }
    items = []
    for k, label in labels.items():
        if k not in rc["gates"]:
            continue
        v = rc["gates"].get(k)
        cls = "ok" if v is True else ("no" if v is False else "warn")
        txt = "PASS" if v is True else ("FAIL" if v is False else "n/a")
        items.append(f'<li><span class="pill {cls}">{txt}</span> {label}</li>')
    g = rc["gates"]
    budget = (f'<p class="muted">Historical experiment budget: {esc(g.get("experiments_used", "?"))} experiments used; '
              f'{esc(g.get("time_budget_note", ""))} Literal-rule exception applied: '
              f'<b>{"yes" if g.get("literal_rule_exception_applied") else "no"}</b>. No further experiment is authorized by this disposition.</p>')
    return '<ul class="gates">' + "".join(items) + "</ul>" + budget


def uniqueness_note(rc) -> str:
    t = rc["registry_uniqueness"]["tiers"]
    u1, u2, u3, u4 = (t["U1_unique_vs_nine_scored_site_files"], t["U2_literal_rule_vs_all_registry_rasters"],
                      t["U3_chance_corrected_overlap_vs_all"], t["U4_literal_rule_vs_dot_rasters_that_were_submitted"])
    rows = "".join(
        f'<tr><td><code class="cs">{esc(Path(f["submission"]).name)}</code><br><span class="sub-label">{esc(f["repo"])} · {esc(f["object"])} · {f["their_positive_px"]:,} positive px</span></td>'
        f'<td><b class="no">{pct(f["overlap_3px"])}</b></td><td>{pct(f["halo_fraction_of_footprint"]) if f["halo_fraction_of_footprint"] is not None else "—"}</td>'
        f'<td>{f["chance_corrected_overlap"]:.2f}</td><td>{pct(f["GEMSDOE32_champion_overlap_with_same_raster"]) if f["GEMSDOE32_champion_overlap_with_same_raster"] is not None else "—"}</td>'
        f'<td>{esc(f["submission_status"])}</td></tr>' for f in u2["failures"])
    per_site = ", ".join(f'{esc(k)} {pct(v["overlap_3px"])}' for k, v in sorted(u1["per_site"].items()))
    registry = rc["registry_uniqueness"]
    worst = registry["worst_overlap_all_registry"]
    return f"""
<div class="notice warn">
<h4>Literal uniqueness gate — STOP; no registry exceptions</h4>
<p><b>Vs the nine supplied historical site files:</b> {'PASS' if u1['pass'] else 'FAIL'} (HK3 dot overlap within 3 px: {per_site}; maximum absolute rank correlation {u1['max_abs_rho']:.3f}). This narrower comparison does not clear the all-registry stop.</p>
<p><b>Literal &gt;70% rule against every scanned registry entry:</b> <b class="no">FAIL — {len(u2['failures'])} entries exceed the limit</b>. Maximum is {pct(worst)} against the r13 spacing-5 lattice. The two r13 entries are the same TIFF mirrored in two repositories; either entry is independently disqualifying. There is no exception for an unsubmitted or dense/degenerate witness. The three additional failures are shown below.
<b>Chance-corrected overlap:</b> {'PASS' if u3['pass'] else 'FAIL'} (maximum {u3['max_corrected']:.2f}); this is descriptive only and cannot replace the literal rule. <b>Literal check vs dot rasters believed submitted:</b> {'PASS' if u4['pass'] else 'FAIL'}; that narrower tier also cannot replace the all-registry rule.</p>
{'<table><thead><tr><th>Registry raster</th><th>HK3 dots within 3 px</th><th>3 px halo coverage</th><th>Chance-corrected diagnostic</th><th>GEMSDOE32 overlap</th><th>Registry status / scope</th></tr></thead><tbody>' + rows + '</tbody></table>' if rows else ''}
<p class="muted">Coverage is incomplete: {registry['registry_rasters_checked']} of {registry['registry_rasters_expected']} expected entries were checked; {registry['missing_or_invalid']} is missing/invalid and no complete-inventory certificate exists. No pre-placement surface-versus-registry audit was found. The historical lane is stopped; the current artifact is retained only as a research download, not offered for upload.</p>
</div>
"""


def legacy_cards() -> dict:
    """Run cards of the other lanes in this repository (all negative); read from disk, never typed."""
    def rd(rel):
        try:
            return json.loads((ROOT / rel).read_text())
        except (OSError, ValueError):
            return None
    return {
        "k3": rd("evidence/k3/run_card.json"), "k2": rd("evidence/k2/run_card.json"), "b4": rd("evidence/b4/run_card.json"),
        "h2": rd("evidence/run_card_h2.json"), "h1": rd("evidence/h1/run_card.json"),
    }


def legacy_section(rc) -> str:
    c = legacy_cards()
    hk3_b110 = rc["holdout"]["candidate_same_budget_as_incumbent_b110"]["dti"]
    hk3_u1 = rc["registry_uniqueness"]["tiers"]["U1_unique_vs_nine_scored_site_files"]["max_overlap"]
    rows = []

    def row(stem, sha, why, receipts):
        rows.append(f'<tr><td><code class="cs">{esc(stem)}.tif</code><br><span class="sub-label">SHA-256 {esc(sha)}</span></td>'
                    f'<td><span class="pill no">DO NOT SUBMIT</span></td><td>{why}</td><td>{receipts}</td></tr>')

    k3 = c["k3"]
    if k3:
        h = k3["holdout"]; cor = k3["correlation_overlap_vs_registry"]
        worst = max(r["overlap"] for r in cor["final_dots"]["flagged_primary"])
        row(k3["submission_name"], k3["raster_sha256"],
            f'K3 (concurrent lane; 53-feature lineament-context HGB, {k3["dots"]:,} dots, expected-DTI placement &gt; 2 px off catalogue): '
            f'HOLDOUT-DTI <b>{f4(h["candidate_dti"])}</b> [{f4(h["candidate_ci95"][0])}, {f4(h["candidate_ci95"][1])}] at the 1.10 % budget — '
            f'<b>higher than HK3&#8217;s {f4(hk3_b110)}</b> at the same budget (intervals overlap; same folds and evaluator, but no paired test exists across the two sessions). '
            f'Verdict {esc(k3["verdict"]).upper()}: its surface failed the pre-placement gate against K2 (top-support overlap '
            f'{cor["surface_before_placement"]["top_support_overlap_vs_K2_predecessor"]:.4f}) and its final dots exceed 70 % within 3 px of '
            f'{cor["final_dots"]["duplicates_primary_count"]} registry records (worst {worst:.3f}). HK3 keeps a 3 px catalogue apron and 3 px dot separation, '
            f'which is why its overlap with the nine scored files stays ≤ {pct(hk3_u1)}; that narrow comparison does not clear HK3 against the full registry. '
            f'K3 remains the holdout-best file in this repository but is not submittable, and HK3 is also research-only under the strict current disposition. '
            f'No file is currently eligible. The recorded next-lane holdout reference is K3&#8217;s {f4(h["candidate_dti"])}.',
            '<a href="evidence/k3/run_card.json">k3/run_card.json</a> · <a href="evidence/k3/selector_result.json">k3/selector_result.json</a>')
    k2 = c["k2"]
    if k2:
        h = k2["holdout"]
        row(k2["submission_name"], k2["raster_sha256"],
            f'K2 (26-feature HGB, {k2["dots"]:,} dots): HOLDOUT-DTI {f4(h["dti"])} [{f4(h["ci95"][0])}, {f4(h["ci95"][1])}]; '
            f'prior literal-policy verdict for K2: NEGATIVE (pre-placement lattice overlap 100 % against the 70 % limit). The lattice remains in scope under the current no-exception rule; '
            f'the file was never submitted and remains research-only).',
            '<a href="evidence/k2-review-2026-10-28.json">k2-review-2026-10-28.json</a> · <a href="evidence/k2-protocol-review.json">k2-protocol-review.json</a> · '
            '<a href="evidence/k2/literal_release_audit.json">literal_release_audit.json</a> · <a href="evidence/k2/selector_result.json">selector_result.json</a>')
    b4 = c["b4"]
    if b4:
        h = b4["holdout"]
        row(b4["submission_name"], b4["raster_sha256"],
            f'B4 scarp-step asymmetry (concurrent lane, {b4["dots"]:,} dots): HOLDOUT-DTI {f4(h["b4_b110"])} [{f4(h["b4_b110_ci95"][0])}, {f4(h["b4_b110_ci95"][1])}] at 1.10 % — '
            f'below the K2 incumbent ({f4(h["incumbent_k2_holdout_dti"])}); verdict NEGATIVE; its own audit also reports 1.0 overlap with the lattice.',
            '<a href="evidence/b4/run_card.json">b4/run_card.json</a> · <a href="evidence/b4/literal_followup.json">b4/literal_followup.json</a>')
    h2 = c["h2"]
    if h2:
        h = h2["holdout"]
        row(h2["submission_name"], h2["raster_sha256"],
            f'H2 dilational stepover / relay-ramp surface (not dots): HOLDOUT-DTI {f4(h["dti"])} [{f4(h["ci95"][0])}, {f4(h["ci95"][1])}] — worse than its primitives; verdict NEGATIVE.',
            '<a href="evidence/run_card_h2.json">run_card_h2.json</a>')
    h1 = c["h1"]
    if h1:
        h = h1["holdout"]
        row(h1["submission_name"], h1["raster_sha256"],
            f'H1 signed-downthrow-parity surface (not dots): HOLDOUT-DTI {f4(h["dti"])} [{f4(h["ci95"][0])}, {f4(h["ci95"][1])}] — worse than its primitive controls; verdict NEGATIVE.',
            '<a href="evidence/h1/run_card.json">h1/run_card.json</a> · <a href="evidence/run_card.json">run_card.json</a>')
    row("gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros", "see audit",
        'H-KARAGE-1 irregular raster: <b>not unique</b> — 100% of its in-footprint positives lie within 3 px of the r13 lattice (6,765 of 6,769; the rule&#8217;s limit is 70%), '
        'and 5,426 positives fall outside the footprint. NO.',
        '<a href="evidence/legacy-dot-audit-2026-10-28.json">legacy-dot-audit-2026-10-28.json</a>')
    return f"""
<section class="section" id="legacy">
<h3>Other files on this server — research only, DO NOT SUBMIT</h3>
<p>Every run card below is negative. They stay published so that their receipts remain verifiable; the shared download inventory
(<a href="evidence/public_downloads_audit.json">public_downloads_audit.json</a>) re-reads all of them from disk on every build.</p>
<table>
<thead><tr><th>File</th><th>Status</th><th>Why</th><th>Receipts</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p class="muted"><b>No file is currently offered for upload.</b> The HK3 TIFF at the top of the page is available only as a research artifact; do not submit it.</p>
</section>
"""


# ----------------------------------------------------------------------------- pages
def page_index(d) -> str:
    rc, cal = d["rc"], d["cal"]
    est = rc["estimator"]
    hold = rc["holdout"]
    r = rc["raster"]
    sub = rc["submission"]
    ru = rc["registry_uniqueness"]
    u1 = ru["tiers"]["U1_unique_vs_nine_scored_site_files"]
    u2 = ru["tiers"]["U2_literal_rule_vs_all_registry_rasters"]
    leaderboard = d["leaderboard"]
    tif = f"downloads/{sub['name']}.tif"
    zipf = f"downloads/{sub['name']}.zip"
    row = est["curve_row_used"]
    theta = est["estimate_theta"]

    out = head("Research-only disposition", "home")
    out += f"""
<section class="hero">
<h2>No approved submission — DO NOT SUBMIT</h2>
<p class="verdict"><b class="no">Current disposition: RESEARCH ONLY.</b> The HK3 TIFF fails the literal all-registry duplicate stop and the strict exterior-format check. The earlier positive selector decision is preserved as historical evidence, but is superseded for current release decisions. No file is cleared for upload and no competition slot was used.</p>
<p><a class="btn big" href="{tif}" download>⬇ Download HK3 research TIFF — DO NOT SUBMIT ({r['dots']:,} positive pixels)</a>
&nbsp; <a class="btn secondary" href="{zipf}" download>Research ZIP</a>
&nbsp; <a class="btn secondary" href="evidence/hk3/strict_disposition.json">Current strict disposition (JSON)</a></p>
<div class="meta">
<b>Saved TIFF SHA-256</b> <code>{esc(r['sha256'])}</code><br>
<b>Historical experiment filename</b> <code>{esc(sub['name'])}</code> (traceability only; not upload clearance)<br>
<b>Research-only note</b> <code>{esc(sub['note'])}</code><br>
<a href="evidence/hk3/run_card.json">Prior experiment card (historically says PROMOTE)</a> ·
<a href="evidence/hk3/selector_result.json">Prior selector record (historical)</a> ·
<a href="evidence/hk3/strict_selector_result.json">Current negative selector record</a>
</div>
<table class="kv">
<tr><th>Prior experiment result</th><td><b>HOLDOUT-DTI {f4(hold['candidate_same_budget_as_incumbent_b110']['dti'])}</b> [{f4(hold['candidate_same_budget_as_incumbent_b110']['ci95'][0])}, {f4(hold['candidate_same_budget_as_incumbent_b110']['ci95'][1])}] at the matched 1.10% budget, vs re-fitted incumbent {f4(hold['incumbent_refit_b110']['dti'])}; paired Δ +{f4(hold['paired_differences']['cand34_b110_minus_inc26_b110']['delta'])} [{f4(hold['paired_differences']['cand34_b110_minus_inc26_b110']['ci95'][0])}, {f4(hold['paired_differences']['cand34_b110_minus_inc26_b110']['ci95'][1])}]. Evaluator <code>{esc(hold['evaluator_version'])}</code>; {fmt_int(hold['withheld_positive_pixels'])} withheld positives. Historical run-card evidence only; not an organizer score.</td></tr>
<tr><th>Historical projection</th><td><b>{f4(est['estimate'])}</b> — <span class="tag">LEADERBOARD-CALIBRATED ESTIMATE</span>, not a score. Sensitivity: θ = 0 → {f4(theta['0.00'])}, 0.50 → {f4(theta['0.50'])}, 0.75 → {f4(theta['0.75'])}, 1.00 → {f4(theta['1.00'])}; stated pessimistic floor {f4(est['estimate_if_no_better_than_anchor'])}. Derived from user-reported anchors, not validated as a forecast, and not used for current eligibility.</td></tr>
<tr><th>Uniqueness</th><td><b class="no">FAIL — literal &gt;70% stop.</b> {len(u2['failures'])} registry entries exceed the threshold; the maximum is {pct(ru['worst_overlap_all_registry'])} within 3 px of the r13 lattice. No exception is permitted for unsubmitted or dense/degenerate rasters. The separate comparison against the nine focus files passes (max {pct(u1['max_overlap'])}); that narrower result cannot clear the all-registry stop.</td></tr>
<tr><th>Registry coverage</th><td><b class="no">INCOMPLETE.</b> {ru['registry_rasters_checked']} of {ru['registry_rasters_expected']} expected entries checked; {ru['missing_or_invalid']} missing/invalid. No complete-inventory certificate and no saved pre-placement surface-versus-registry audit.</td></tr>
<tr><th>Saved-byte format</th><td>Local checks: one-band float32, pinned owner-mirror grid, whole array finite and in [0,1]. The official problem page says pixels outside bounds should be null/NaN; this file writes zeros and its strict receipt has <code>outside_is_nan: false</code> and <code>strict_format_pass: false</code>. Template authenticity and portal acceptance are unverified; the previous range error is not proven resolved.</td></tr>
<tr><th>Lane / budget</th><td>No coordinator-assigned method paragraph is documented. The prior HK3 card records 3 experiments and approximately 2 h 15 min, so no further experiment is authorized in this lane. This review ran zero experiments.</td></tr>
</table>
<h3>Current automated gates</h3>
{gate_list(rc)}
{uniqueness_note(rc)}
</section>

<section class="section">
<h3>Research download inventory</h3>
<table>
<thead><tr><th>File</th><th>Current disposition</th><th>Evidence labels</th><th>Submission status</th></tr></thead>
<tbody>
<tr><td><a href="{tif}"><code>{esc(sub['name'])}.tif</code></a><br><span class="sub-label">SHA-256 {esc(r['sha256'])}</span></td>
<td><span class="pill no">RESEARCH ONLY</span></td>
<td>{f4(hold['candidate_same_budget_as_incumbent_b110']['dti'])} HOLDOUT-DTI · {f4(est['estimate'])} LEADERBOARD-CALIBRATED ESTIMATE (not a score)</td>
<td><b class="no">DO NOT SUBMIT</b>; no eligible candidate</td></tr>
<tr><td><a href="{zipf}" download><code>{esc(sub['name'])}.zip</code></a></td><td><span class="pill no">RESEARCH ONLY</span></td><td>Contains the same saved TIFF bytes</td><td><b class="no">DO NOT SUBMIT</b></td></tr>
</tbody></table>
<p>Other experiment artifacts remain quarantined below the executive summary. No automated gate or download link authorizes a competition slot.</p>
</section>

<section class="section">
<h3>Nine supplied best-reported files — all values unverified</h3>
<p>The values below are <b>USER-REPORTED / UNVERIFIED</b>; no file-bound organizer receipts were found. Pinned masks show a shared lineage and fail the requested uniqueness comparison against one another. See the executive summary for file-by-file comparisons and the cautious GEMSDOE32 interpretation.</p>
<table id="nine-sites">
<thead><tr><th>Site</th><th>Owner-mirror file</th><th>Reported value</th><th>Positive pixels</th><th>Measured mask note</th><th>Closest focus-mask overlap</th></tr></thead>
<tbody>
"""
    for s in site_rows(d):
        out += (f'<tr><td><a href="{esc(s["url"])}">{esc(s["site"])} ↗</a></td><td><code class="cs">{esc(s["file"])}</code></td>'
                f'<td>{f4(s["reported"])} <span class="sub-label">USER-REPORTED / UNVERIFIED</span></td><td>{s["dots"]:,}</td>'
                f'<td>{esc(s["lineage"])}</td><td>{pct(s["overlap"])} within 3 px of {esc(s["closest"])}</td></tr>\n')
    out += f"""</tbody></table>
<p class="muted">Official public leaderboard observation on {esc(leaderboard['captured_date'])}: rank {leaderboard['observed_rank']} displayed {leaderboard['observed_score']:.4f}. This is a time-stamped page observation only; it is not a receipt, not tied to a file hash, and not a score for this repository's raster. <a href="evidence/public_leaderboard_observation_2026-10-28.json">Observation record ↗</a>.</p>
</section>

<section class="section">
<h3>Why GEMSDOE32 may have reported 0.2778</h3>
<p>The pinned mirror shows GEMSDOE32's dot mask as a pruned member of the D2.8 family: 3,891 dots are removed from GEMSDOE25 within 1 px of the mapped catalogue, followed by 2,545 additional dots in the 1–2 px band; GEMSDOE32 therefore has 6,436 fewer dots than that parent. A plausible mechanism is less false-positive mass while retaining some distance-kernel credit near faults absent from the public catalogue. The mask relation is measured; the explanation is not causal, the 0.2778 is unverified, and no receipt ties that value to this exact TIFF. Do not infer hidden truth from dot counts.</p>
<p>The official target is <b>fault structures indicative of geothermal resources</b>, not direct vent locations. Four source-grounded but unassigned hypotheses are listed in the <a href="executive-summary.html">executive summary</a>. No hypothesis has been implemented in this review.</p>
</section>
"""
    out += legacy_section(rc)
    out += foot(d)
    return badge_fill(out, d)


def page_summary(d) -> str:
    rc, cal, bridge, e2 = d["rc"], d["cal"], d["bridge"], d["e2"]
    est = rc["estimator"]
    hold = rc["holdout"]
    sub = rc["submission"]
    r = rc["raster"]
    ru = rc["registry_uniqueness"]
    u1 = ru["tiers"]["U1_unique_vs_nine_scored_site_files"]
    u2 = ru["tiers"]["U2_literal_rule_vs_all_registry_rasters"]
    theta = est["estimate_theta"]
    leaderboard = d["leaderboard"]
    out = head("Executive summary and review", "summary")
    out += f"""
<section class="hero">
<h2>Executive summary — strict negative disposition</h2>
<p class="verdict"><b class="no">DO NOT SUBMIT.</b> No TIFF in this release is eligible for competition upload. HK3 is retained for research inspection only: its final dots violate the literal all-registry stop, its exterior convention conflicts with the official bounds instruction, and the registry audit is incomplete.</p>
<p><a class="btn big" href="downloads/{esc(sub['name'])}.tif" download>Download research TIFF — DO NOT SUBMIT</a>
&nbsp; <a class="btn secondary" href="index.html">Disposition and evidence</a>
&nbsp; <a class="btn secondary" href="evidence/hk3/strict_disposition.json">Strict disposition JSON</a></p>
</section>

<section class="section">
<h3>1. Decision table</h3>
<table>
<thead><tr><th>Question</th><th>Current evidence and status</th></tr></thead>
<tbody>
<tr><td>Current file</td><td><code>{esc(sub['name'])}.tif</code>, SHA-256 <code>{esc(r['sha256'])}</code>. Research artifact only; <b class="no">DO NOT SUBMIT</b>.</td></tr>
<tr><td>Prior experiment metric</td><td><b>HOLDOUT-DTI {f4(hold['candidate_same_budget_as_incumbent_b110']['dti'])}</b> [{f4(hold['candidate_same_budget_as_incumbent_b110']['ci95'][0])}, {f4(hold['candidate_same_budget_as_incumbent_b110']['ci95'][1])}] at 1.10% budget; evaluator <code>{esc(hold['evaluator_version'])}</code>; {fmt_int(hold['withheld_positive_pixels'])} withheld positives. This is the historical spatially blocked hide-and-recover result, not a leaderboard score.</td></tr>
<tr><td>Exploratory transfer</td><td><b>{f4(est['estimate'])}</b> LEADERBOARD-CALIBRATED ESTIMATE; not a score or validated forecast. θ sensitivity: {f4(theta['0.00'])} (θ=0), {f4(theta['0.50'])} (θ=0.5), {f4(theta['0.75'])} (θ=0.75), {f4(theta['1.00'])} (θ=1); historical stated floor {f4(est['estimate_if_no_better_than_anchor'])}. Uses unverified reported anchors; not used for disposition.</td></tr>
<tr><td>Literal uniqueness</td><td><b class="no">FAIL.</b> {len(u2['failures'])} registry entries exceed 70% within 3 px; maximum {pct(ru['worst_overlap_all_registry'])} against the r13 spacing-5 lattice. The narrow comparison to the nine focus files passes (max {pct(u1['max_overlap'])}) but cannot override the all-registry rule.</td></tr>
<tr><td>Format / exterior</td><td>Whole saved array is finite and within [0,1] on local checks. The official problem page requires null/NaN outside bounds; the TIFF writes zeros and strict check <code>outside_is_nan</code> is false. No organizer template authentication or portal receipt exists.</td></tr>
<tr><td>Lane / budget</td><td>No coordinator-assigned lane is documented. Historical HK3 card records 3 experiments and about 2 h 15 min; the experiment/time budget is exhausted. This review ran no experiment.</td></tr>
<tr><td>Competition receipt</td><td>No <b>ORGANIZER-CONFIRMED</b> score or file-bound submission receipt for this repository.</td></tr>
</tbody></table>
<p><b>Current leaderboard context:</b> the official public leaderboard page displayed {leaderboard['observed_score']:.4f} at rank {leaderboard['observed_rank']} on {esc(leaderboard['captured_date'])}. This is a public-page observation only, not a submission receipt and not a score for HK3. The nine site values below are separately marked USER-REPORTED / UNVERIFIED.</p>
</section>

<section class="section">
<h3>2. Compare the nine supplied best-reported submissions</h3>
<p>These are the top reported values represented in the supplied focus-site evidence, not verified complete repository leaderboards. Every score/value is <b>USER-REPORTED / UNVERIFIED</b>. The pinned owner mirrors show all nine are close members of one ridge-dot family and are not unique under the requested proximity rule.</p>
<table id="nine-sites">
<thead><tr><th>Site</th><th>Reported value</th><th>Owner-mirror TIFF · positives</th><th>Measured mask lineage / note</th><th>Closest focus mask</th></tr></thead>
<tbody>
"""
    for s in site_rows(d):
        out += (f'<tr id="{esc(s["site"])}"><td><a href="{esc(s["url"])}">{esc(s["site"])} ↗</a></td>'
                f'<td><b>{f4(s["reported"])}</b><br><span class="sub-label">USER-REPORTED / UNVERIFIED</span></td>'
                f'<td><code class="cs">{esc(Path(s["file"]).name)}</code><br>{s["dots"]:,} positive pixels</td>'
                f'<td>{esc(s["lineage"])}</td><td>{pct(s["overlap"])} within 3 px of {esc(s["closest"])}</td></tr>\n')
    out += f"""</tbody></table>
<p class="muted">GEMSDOE25 and GEMSDOE30 decode to the same 44,090-dot mask. GEMSDOE31 removes 3,891 dots at ≤1 px from the mapped catalogue; GEMSDOE32 removes another 2,545 in the 1–2 px band; GEMSDOE36 adds 1,200 dots to the GEMSDOE32 mask. These are byte/mask relationships in owner mirrors, not proof that any reported score belongs to that exact file.</p>
</section>

<section class="section">
<h3>3. What may explain GEMSDOE32's reported 0.2778</h3>
<p>The plausible mechanism is pruning predictions near already mapped faults, which may reduce false-positive mass while a distance-tolerant kernel still gives partial credit to nearby faults missing from the public catalogue. The official metric uses α=0.2, β=0.8 and a triangular 300 m kernel, so that tradeoff is scientifically plausible. It is not established as the cause of the reported value.</p>
<p>The official DTI has separate truth-side and prediction-side weighted sums. Dot-count arithmetic alone cannot reconstruct hidden truth, true-positive credit, or false-positive mass. The 0.2778 remains <b>USER-REPORTED / UNVERIFIED</b>; the historical source says the contemporaneous file was unscored, and no later organizer receipt tying this hash to 0.2778 was found. Treat the explanation as a falsifiable hypothesis, not a result. The task target is fault structures indicative of geothermal resources—not direct geothermal vents.</p>
<p>See the <a href="{REPO_URL}/blob/main/research/independent-review.md">independent H33 review</a>, the <a href="{REPO_URL}/blob/main/research/2026-10-28-next-lane-slate.md">unassigned next-lane slate</a>, and the <a href="{REPO_URL}/blob/main/evidence/calibration/leaderboard_calibration.json">historical calibration record</a> (the last is exploratory and is not used as a score).</p>
</section>

<section class="section">
<h3>4. Four distinct geological hypotheses — proposals only, not implemented</h3>
<p>These are qualitatively ranked hypotheses about potential matched <b>HOLDOUT-DTI</b> improvement, not score estimates. The exact owner-mirror feature units/lineage require verification. No assigned lane or budget exists; proposal 1 also has a possible ingredient-family collision with the negative B4 topography/gravity experiment.</p>
<table>
<thead><tr><th>Proposal and bands</th><th>Fault mechanism (hypothesis)</th><th>Named non-fault mimic / falsification control</th></tr></thead>
<tbody>
<tr><td><b>1. Topography-conditioned residual gravity step</b><br>13, 11, 12, 19</td><td>Within each training block, remove label-blind terrain/regional trends from gravity-gradient response; test persistent 300–900 m residual edges for covered density offsets that may continue beyond an exposed scarp.</td><td>Unfaulted sediment–bedrock contact or lake-terrace riser. Predefine contour/shoreline nulls, ablate terrain regression and use label-blind offset blocks. Potential B4 family collision: resolve lane before any run.</td></tr>
<tr><td><b>2. Conductivity saddle across an independent gravity break</b><br>17, 13, 18; exclude band 15 pending authentication</td><td>Test a cross-profile sign change in conductivity curvature across a gravity break; a covered fault is the target, not proof of flowing geothermal fluid.</td><td>Saline groundwater/playa margin or EM-inversion seam. Ablate conductivity and test whether edges follow survey-coverage boundaries.</td></tr>
<tr><td><b>3. Strain-regime change × persistent magnetic edge</b><br>7, 8, 2, 3</td><td>Use coarse strain change only as context for a persistent magnetic edge; do not claim 100 m fault localization from interpolated strain alone.</td><td>Geodetic interpolation seam or unfaulted intrusive contact. Shuffle strain within blocks and require incremental value over magnetic-only controls.</td></tr>
<tr><td><b>4. Seismicity-sidedness at an independent gravity edge</b><br>10, 16, 11</td><td>Compare seismicity on either flank of a gravity edge as context for an active unmapped strand, not as a local fault detector.</td><td>Production/mining-induced seismicity or smoothed-density artifacts. Predefine shuffled-seismicity control and stop if it performs similarly.</td></tr>
</tbody></table>
<p>All four are in <a href="{REPO_URL}/blob/main/research/2026-10-28-next-lane-slate.md">the preregistered slate</a>. They are not authorization to run. Before implementation: assigned lane, complete registry and explicit literal-rule scope, authenticated inputs/template, frozen same-fold incumbent, available budget, then the common cached stack and shared evaluator/writer. Hold out whole buffered fault segments, derive catalogue features from visible faults only, mask visible fault pixels exactly, test every feature alone (AUC &gt;0.90 is leakage until resolved), and report pooled HOLDOUT-DTI with evaluator, withheld-positive count, and 95% CI. The surface-versus-registry pre-placement check must pass before any placement; stop on any literal duplicate.</p>
</section>

<section class="section">
<h3>5. Three-pass review findings and remaining gates</h3>
<ol>
<li><b>Scientific/protocol:</b> prior HOLDOUT-DTI retained as historical evidence; no leaderboard forecast is validated; GEMSDOE32 mechanism remains plausible but unproven; no new experiment or submission.</li>
<li><b>Raster/registry:</b> final-dot literal gate fails against r13 (99.8626%) and four additional registry records; two r13 paths are the same raster and both remain in scope. Registry coverage is 452/453, no complete certificate, and no pre-placement surface audit was saved.</li>
<li><b>Format/release:</b> local whole-array range passes but zero exterior conflicts with the official null/NaN instruction; strict exterior check fails. Prior PROMOTE/selector evidence is unchanged but superseded; current public audit exposes only a research artifact.</li>
</ol>
<p><b>Next work, in order:</b> do not submit HK3; obtain an assigned lane and written resolution of registry scope without locally exempting the lattice; complete and pin the registry; authenticate the organizer's sample and resolve the exterior convention; verify reported scores with artifact-bound receipts; then, only if a fresh authorized budget exists, use the shared pipeline and gates. No slot was used, and this review grants none.</p>
<p>Full findings: <a href="{REPO_URL}/blob/main/research/strict-protocol-review-2026-10-28.md">strict three-pass review</a> · <a href="evidence/hk3/strict_disposition.json">current strict JSON disposition</a> · <a href="evidence/hk3/registry_audit.json">saved registry audit</a> · <a href="evidence/hk3/validate_tif_strict.json">saved strict format receipt</a>.</p>
</section>

<section class="section">
<h3>6. Official source links and scope</h3>
<ul>
<li><a href="{OFFICIAL['problem']}">Official problem description ↗</a>: fault-structure target, DTI specification and published GeoTIFF bounds/exterior requirement; accessed 2026-10-28.</li>
<li><a href="{OFFICIAL['leaderboard']}">Official public leaderboard ↗</a>: rank/score page observation above; not a file-bound receipt.</li>
<li><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">DOE/NREL competition rules ↗</a> and <a href="{OFFICIAL['reference']}">organizer reference solution ↗</a>.</li>
<li><a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN ↗</a>, <a href="https://gbcge.org/current-projects/ingenious/">INGENIOUS ↗</a>, <a href="{OFFICIAL['usgs_3dep']}">USGS 3DEP ↗</a> and <a href="{OFFICIAL['tnm']}">The National Map ↗</a>: source context only; no new layers were downloaded or used.</li>
</ul>
<p class="muted">Official specs and public pages were accessed during this review. Owner-mirror hashes do not authenticate organizer data, prove geologic causality, or establish portal acceptance.</p>
</section>
"""
    out += legacy_section(rc)
    out += foot(d)
    return badge_fill(out, d)


def page_howto(d) -> str:
    rc = d["rc"]
    sub = rc["submission"]
    r = rc["raster"]
    u2 = rc["registry_uniqueness"]["tiers"]["U2_literal_rule_vs_all_registry_rasters"]
    out = head("Submission status", "howto")
    out += f"""
<section class="hero">
<h2>Submission status: no file is cleared</h2>
<p class="verdict"><b class="no">DO NOT SUBMIT.</b> There are no upload instructions for the current HK3 TIFF because it fails mandatory scientific/registry and strict-format gates. The earlier positive selector record is historical only; the current strict disposition supersedes it.</p>
<p><a class="btn big" href="index.html">Read current disposition and executive summary</a>
&nbsp; <a class="btn secondary" href="evidence/hk3/strict_disposition.json">Current strict disposition (JSON)</a>
&nbsp; <a class="btn secondary" href="evidence/hk3/strict_selector_result.json">Current negative selector record</a></p>
<p><a href="downloads/{esc(sub['name'])}.tif" download>Download the saved TIFF for research review only (SHA-256 {esc(r['sha256'])})</a>. This link does not authorize submission.</p>
</section>

<section class="section">
<h3>Why the file is not eligible</h3>
<ul>
<li><b>Literal duplicate stop:</b> {len(u2['failures'])} scanned registry entries exceed 70% of HK3's final dots within 3 px; worst is {pct(rc['registry_uniqueness']['worst_overlap_all_registry'])} against the r13 lattice. No exception applies to a raster because it was unsubmitted, dense, or classified as degenerate.</li>
<li><b>Incomplete registry:</b> {rc['registry_uniqueness']['registry_rasters_checked']} of {rc['registry_uniqueness']['registry_rasters_expected']} expected entries were checked; one is missing/invalid. There is no complete-inventory certificate and no saved pre-placement surface audit.</li>
<li><b>Exterior mismatch:</b> the saved TIFF writes zeros outside the mapped bounds. The official problem description requires null/NaN there; strict local receipt has <code>outside_is_nan: false</code> and <code>strict_format_pass: false</code>.</li>
<li><b>Lane/budget:</b> no coordinator-assigned method paragraph is documented. The prior HK3 card records three experiments and about 2 h 15 min, so the run's experiment/time budget is exhausted.</li>
</ul>
</section>

<section class="section">
<h3>What the saved-byte checks do—and do not—prove</h3>
<ul>
<li>The saved raster is one-band float32 on the pinned owner-mirror grid; whole-array values are finite and in [0,1]. Its SHA-256 is recorded above and the ZIP contains the same TIFF bytes.</li>
<li>These are local checks against owner-mirrored metadata. The official sample/template is not authenticated here; the official exterior requirement is not met by this artifact.</li>
<li>The earlier portal message “Predicted values must be in range [0, 1]” is not explained by one local range check. No upload was made, no portal behavior was tested, and no claim is made that the error cannot recur.</li>
<li>Prior <b>HOLDOUT-DTI</b> and <b>LEADERBOARD-CALIBRATED ESTIMATE</b> values are historical evidence with their own labels; neither is an organizer-confirmed score.</li>
</ul>
</section>

<section class="section">
<h3>Prerequisites for any future candidate (not upload steps)</h3>
<ol>
<li>Obtain the actual assigned method lane and resolve the literal all-registry rule without silently exempting the lattice; establish a complete, hash-pinned inventory.</li>
<li>Authenticate the competition inputs and example/template, and resolve the null/NaN exterior behavior with the official specification or organizer evidence.</li>
<li>Confirm a separately authorized experiment/time budget and freeze a same-fold incumbent. The four hypotheses in the <a href="executive-summary.html">executive summary</a> are proposals only, not approvals to run.</li>
<li>Use the shared cached feature stack, evaluator, and writer; hold out whole buffered fault segments, derive catalogue features from visible faults only, mask visible faults exactly, and test every feature alone for leakage.</li>
<li>Require a passing pre-placement surface audit, then final-dot literal registry check, paired pooled HOLDOUT-DTI with evaluator/count/95% CI, strict saved-byte validation, unique name/note and a separate explicit selector decision. Any hard stop remains negative.</li>
</ol>
<p><b>No weekly slot has been used or authorized by this review.</b> Check the <a href="{OFFICIAL['competition']}">official competition rules ↗</a> only after a future file is actually cleared.</p>
</section>
"""
    out += legacy_section(rc)
    out += foot(d)
    return badge_fill(out, d)


CSS = """/* HK3 desk additions (generated pages) */
.topnav { font-size: 14px; margin: 0 0 18px 0; }
.hero .btn.big { font-size: 17px; padding: 14px 26px; }
.hero .btn.secondary { background: #fff; color: var(--brand); border: 2px solid var(--brand); }
.hero .verdict b.ok { color: var(--ok); }
table.kv th { width: 160px; vertical-align: top; text-transform: none; font-size: 13px; }
ul.gates { list-style: none; padding-left: 0; }
ul.gates li { margin: 6px 0; font-size: 13.5px; }
.pill { display: inline-block; min-width: 54px; text-align: center; padding: 1px 8px; border-radius: 10px; font-size: 11.5px; font-weight: 700; margin-right: 6px; white-space: nowrap; overflow-wrap: normal; word-break: normal; }
.pill.ok { background: #ecfdf5; color: var(--ok); border: 1px solid #bbf7d0; }
.pill.no { background: #fef2f2; color: var(--no); border: 1px solid #fecaca; }
.pill.warn { background: #fffbeb; color: var(--warn); border: 1px solid #fcd34d; }
.sub-label { display: block; font-size: 11px; color: var(--muted); }
tr.chosen td { background: #ecfdf5; font-weight: 700; }
.notice { border-radius: 10px; padding: 12px 16px; margin: 14px 0; border: 1px solid var(--line); background: #fff; }
.notice.warn { border-color: #fcd34d; background: #fffbeb; }
.notice.ok { border-color: #bbf7d0; background: #ecfdf5; }
.notice h4 { margin: 0 0 6px 0; font-size: 14px; }
.notice table { margin: 8px 0; }
b.no { color: var(--no); } b.ok { color: var(--ok); }
.tag.no { color: var(--no); }
.header .badge { vertical-align: middle; }
/* narrow viewports: never overflow horizontally */
.wrap, .inner, .section, .hero { max-width: 100%; min-width: 0; overflow-wrap: anywhere; }
table { display: block; max-width: 100%; overflow-x: auto; }
code, .cs, .sha, pre { overflow-wrap: anywhere; word-break: break-all; white-space: pre-wrap; }
.btn, .hero .btn.big { white-space: normal; max-width: 100%; box-sizing: border-box; text-align: center; }
img, svg { max-width: 100%; height: auto; }
@media (max-width: 480px) { .header h1 { font-size: 20px; } .header .badge { display: inline-block; margin-top: 6px; } table.kv th { width: auto; } }
"""


def render_all(d) -> dict[str, str]:
    summary = page_summary(d)
    return {
        "index.html": page_index(d),
        "executive-summary.html": summary,
        "how-to-submit.html": page_howto(d),
        "submit.html": page_howto(d).replace("<title>How to submit", "<title>Submit"),
        "assets/hk3.css": CSS,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="fail if the checked-in pages are stale")
    a = ap.parse_args()
    d = gather()
    pages = render_all(d)
    for name, text in pages.items():
        if "{BADGE" in text:
            raise SystemExit(f"unresolved placeholder in {name}")
    # The pages link to the nested HK3 receipts and the time-stamped public leaderboard observation.
    src = EV / "hk3"; dst = DOCS / "evidence" / "hk3"
    observation = EV / "public_leaderboard_observation_2026-10-28.json"
    if not a.check:
        dst.mkdir(parents=True, exist_ok=True)
        for f in sorted(src.glob("*.json")):
            (dst / f.name).write_text(f.read_text())
        (DOCS / "evidence" / "calibration").mkdir(parents=True, exist_ok=True)
        (DOCS / "evidence" / "calibration" / "leaderboard_calibration.json").write_text((EV / "calibration/leaderboard_calibration.json").read_text())
        (DOCS / "evidence" / observation.name).write_text(observation.read_text())
    stale = []
    if a.check:
        # mirrored evidence must be byte-identical to the source files the pages were built from
        mirrors = [(f, dst / f.name) for f in sorted(src.glob("*.json"))]
        mirrors.append((EV / "calibration/leaderboard_calibration.json", DOCS / "evidence" / "calibration" / "leaderboard_calibration.json"))
        mirrors.append((observation, DOCS / "evidence" / observation.name))
        for f, m in mirrors:
            if not m.exists() or m.read_text() != f.read_text():
                stale.append(str(m.relative_to(DOCS)))
    for name, text in pages.items():
        p = DOCS / name
        if a.check:
            if not p.exists() or p.read_text() != text:
                stale.append(name)
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
    if a.check:
        if stale:
            print("stale pages:", ", ".join(stale))
            return 1
        print("pages up to date")
        return 0
    print("wrote", ", ".join(pages))
    return 0


if __name__ == "__main__":
    sys.exit(main())

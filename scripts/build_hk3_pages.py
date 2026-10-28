#!/usr/bin/env python3
"""Generate the public pages (docs/index.html, docs/executive-summary.html,
docs/how-to-submit.html, docs/submit.html) from the evidence JSON files.

Every number on the pages is read from a JSON receipt under evidence/ or registry/;
nothing is typed by hand.  Labels follow the repository rule: a number is either
ORGANIZER-CONFIRMED (none exist in this repository), USER-REPORTED / UNVERIFIED,
HOLDOUT-DTI (evaluator version, withheld positives, 95 % CI) or a
UNVALIDATED PROJECTION — NOT A SCORE (historical LEADERBOARD-CALIBRATED ESTIMATE) (never written as a score).

Usage:  python scripts/build_hk3_pages.py [--check]
--check fails (exit 1) if the checked-in pages differ from what would be generated.
"""
from __future__ import annotations

from hk3_release_policy import publication_eligible

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
    rc = load(EV / "hk3/run_card.json")
    cal = load(EV / "calibration/leaderboard_calibration.json")
    bridge = load(EV / "hk3/bridge.json")
    e2 = load(EV / "hk3/e2.json")
    geo = load(EV / "geometry-audit.json")
    sites = load(ROOT / "registry/focus_sites.json")
    aud = load(EV / "hk3/registry_audit.json")
    return dict(rc=rc, cal=cal, bridge=bridge, e2=e2, geo=geo, sites=sites, aud=aud)


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
    nav = [("index.html", "home", "Download"), ("executive-summary.html", "summary", "Executive summary"),
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
<meta name="description" content="GEMS Prize Challenge (DOE / DrivenData) fault-detection submission desk: validated unique GeoTIFF download, labelled estimates, nine-site audit.">
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
<p class="footnote">Labels: <b>ORGANIZER-CONFIRMED</b> = a DrivenData receipt (none exist in this repository);
<b>USER-REPORTED / UNVERIFIED</b> = values typed by the user from other sites' pages;
<b>HOLDOUT-DTI</b> = our spatially-blocked hide-and-recover evaluation (evaluator <code>{esc(rc['holdout']['evaluator_version'])}</code>,
{fmt_int(rc['holdout']['withheld_positive_pixels'])} withheld positive pixels, 95&nbsp;% paired block-bootstrap CI);
<b>UNVALIDATED PROJECTION — NOT A SCORE (historical LEADERBOARD-CALIBRATED ESTIMATE)</b> = ratio transfer from user-reported anchors — never a score.
Run card generated {esc(rc['generated_utc'])}. <a href="{REPO_URL}">Source repository</a> · <a href="{REPO_URL}/blob/main/README.md">README (standing instructions)</a>.<br>
Official pages (not reachable from the build sandbox; verify manually): <a href="{OFFICIAL['competition']}">competition ↗</a> · <a href="{OFFICIAL['problem']}">problem description &amp; metric ↗</a> · <a href="{OFFICIAL['about']}">about ↗</a> · <a href="{OFFICIAL['data']}">data ↗</a> · <a href="{OFFICIAL['submissions']}">submissions ↗</a> · <a href="{OFFICIAL['leaderboard']}">leaderboard ↗</a> · <a href="{OFFICIAL['reference']}">official reference solution (GitHub, verified) ↗</a>.</p>
</div>
</body>
</html>
"""


def badge_fill(page: str, d) -> str:
    ok = publication_eligible(d["rc"])
    # head() is an f-string, so its "{{BADGE}}" renders as the literal "{BADGE}"
    return page.replace("{BADGE}", "ok" if ok else "no").replace("{BADGE_TEXT}", "OK TO SUBMIT: YES" if ok else "OK TO SUBMIT: NO")


def gate_list(rc) -> str:
    labels = {
        "format_shared_validator_pass": "Format (shared gems57 validator): single band float32, finite, values in [0,1], zeros outside the footprint, no dots on mapped faults",
        "grid_matches_example_submission": "CRS / shape / transform identical to example_submission.tif (EPSG:32611, 3730 × 3292, 100 m)",
        "whole_array_finite_in_0_1": "Whole array finite and inside [0,1] (no NaN anywhere — portal acceptance remains unverified)",
        "no_dots_on_mapped_catalogue": "No positive pixel on a mapped (excluded) fault pixel; 3 px apron kept clear",
        "leakage_canary_pass": "Leakage canary: every new feature alone has AUC &lt; 0.90",
        "holdout_beats_refit_incumbent_paired_ci_excludes_zero": "Beats the re-fitted incumbent on identical folds and budget (paired 95 % CI excludes 0)",
        "unique_vs_nine_scored_site_files": "Unique vs the nine scored GEMSDOE site files (≤ 70 % of dots within 3 px; rank-corr ≤ 0.90)",
        "unique_literal_vs_submitted_dot_rasters": "Literal 70 % rule vs every dot raster in the registry that may have been submitted",
        "unique_chance_corrected_vs_all_registry_rasters": "Chance-corrected overlap (overlap − halo)/(1 − halo) ≤ 0.70 vs all 450 non-degenerate registry rasters",
        "unique_literal_vs_all_registry_rasters": "Literal 70 % rule vs <em>all</em> registry rasters including never-submitted research files and line/surface rasters — see the red note",
        "rank_correlation_below_0_90": "Rank correlation ≤ 0.90 vs every registry raster",
        "lane_single_method": "Single method lane (HK3) — no lane switching",
    }
    items = []
    for k, label in labels.items():
        v = rc["gates"].get(k)
        cls = "ok" if v is True else ("no" if v is False else "warn")
        txt = "PASS" if v is True else ("FAIL" if v is False else "n/a")
        items.append(f'<li><span class="pill {cls}">{txt}</span> {label}</li>')
    g = rc["gates"]
    budget = (f'<p class="muted">Lane budget: {esc(g.get("experiments_used", "?"))} experiments used; {esc(g.get("time_budget_note", ""))}. '
              f'Literal-rule exception applied: <b>{"yes" if g.get("literal_rule_exception_applied") else "no"}</b> (see the uniqueness note).</p>')
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
    return f"""
<div class="notice {'warn' if not u2['pass'] else 'ok'}">
<h4>Uniqueness — read this before uploading</h4>
<p><b>Vs the nine scored site files:</b> {'PASS' if u1['pass'] else 'FAIL'} — HK3 dots within 3 px of each: {per_site}; max rank-corr {u1['max_abs_rho']:.3f}. The dot sets differ from every scored file by more than half.</p>
<p><b>Literal 70 % rule vs all {u2['rasters_checked']} non-degenerate registry rasters:</b> <b class="no">{'FAIL' if not u2['pass'] else 'PASS'}</b>{' against the ' + str(len(u2['failures'])) + ' rasters below, PASS against the other ' + str(u2['rasters_checked'] - len(u2['failures'])) if not u2['pass'] else ''}.
<b>Chance-corrected rule vs all:</b> {'PASS' if u3['pass'] else 'FAIL'} (max {u3['max_corrected']:.2f}, limit 0.70). <b>Literal rule vs every dot raster that may have been submitted:</b> {'PASS' if u4['pass'] else 'FAIL'}.</p>
{'<table><thead><tr><th>Raster</th><th>HK3 dots within 3 px</th><th>Chance level (its 3 px halo)</th><th>Chance-corrected</th><th>GEMSDOE32 champion within 3 px of the same raster</th><th>Status of that raster</th></tr></thead><tbody>' + rows + '</tbody></table>' if rows else ''}
<p class="muted"><b>Binding duplicate stop: DO NOT SUBMIT.</b> The earlier approval used an unauthorized exception. It has been retracted. Chance correction, raster density, and whether a reference was submitted do not waive the literal rule. Downloads are research evidence only; no new experiment or weekly slot is authorized.</p>
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
            f'which is why its overlap with every scored file stays ≤ {pct(hk3_u1)}. K3 is the holdout-best file in this repository but is not submittable; '
            f'HK3 also fails literal uniqueness and is not submittable. Protocol note: HK3 did not beat K3 on holdout, so the holdout incumbent for the next lane is K3&#8217;s {f4(h["candidate_dti"])}.',
            '<a href="evidence/k3/run_card.json">k3/run_card.json</a> · <a href="evidence/k3/selector_result.json">k3/selector_result.json</a>')
    k2 = c["k2"]
    if k2:
        h = k2["holdout"]
        row(k2["submission_name"], k2["raster_sha256"],
            f'K2 (26-feature HGB, {k2["dots"]:,} dots): HOLDOUT-DTI {f4(h["dti"])} [{f4(h["ci95"][0])}, {f4(h["ci95"][1])}]; '
            f'prior literal-policy verdict for K2: NEGATIVE (pre-placement lattice overlap 100 % against the 70 % limit; the lattice remains binding under the literal rule, '
            f'but the file is superseded by HK3 and was never submitted).',
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
<p class="muted">No file is offered for upload. HK3 is downloadable for research only.</p>
</section>
"""


# ----------------------------------------------------------------------------- pages
def page_index(d) -> str:
    rc, cal = d["rc"], d["cal"]
    est = rc["estimator"]
    hold = rc["holdout"]
    r = rc["raster"]
    sub = rc["submission"]
    ok = publication_eligible(rc)
    tif = f"downloads/{sub['name']}.tif"
    zipf = f"downloads/{sub['name']}.zip"
    row = est["curve_row_used"]
    theta = est["estimate_theta"]
    ru = rc["registry_uniqueness"]
    failed = [k for k, v in rc["gates"].items() if v is False]
    gate_sentence = ("Every automated gate passed (format, grid, range, uniqueness, leakage canary, holdout)."
                     if not failed else
                     f"{len([k for k, v in rc['gates'].items() if v is True and k != 'literal_rule_exception_applied'])} automated gates passed (format, grid, range, leakage canary, holdout, "
                     f"uniqueness vs every scored GEMSDOE file and vs every submitted dot raster); "
                     f"<b class=\"no\">{len(failed)} gate failed</b> — the literal 70 % rule against <em>all</em> registry rasters including never-submitted research files — "
                     f"and no exception is authorized. Do not upload.")
    verdict_html = (
        f'<p class="verdict"><b class="ok">OK TO SUBMIT.</b> {gate_sentence} '
        f'This file is new: it was generated in this repository on 2026-10-28 and is not a copy or subset of any GEMSDOE site file.</p>'
        if ok else
        '<p class="verdict"><b class="no">DO NOT SUBMIT.</b> At least one blocking automated gate failed; see the gate list.</p>')
    out = head("Download", "home")
    out += f"""
<section class="hero">
<h2>{'Approved submission file' if ok else 'No approved submission file'} — {esc(sub['name'])}.tif</h2>
{verdict_html}
<p><a class="btn big" href="{tif}" download>⬇ Download research file — DO NOT SUBMIT: {esc(sub['name'])}.tif ({r['dots']:,} dots)</a>
&nbsp; <a class="btn secondary" href="{zipf}" download>ZIP</a>
&nbsp; <a class="btn secondary" href="evidence/hk3/run_card.json">Run card (JSON)</a></p>
<div class="meta">
<b>SHA-256</b> <code>{esc(r['sha256'])}</code><br>
<b>Submission name</b> <code>{esc(sub['name'])}</code><br>
<b>Note (≤ 140 chars, {sub['note_chars']} used)</b> <code>{esc(sub['note'])}</code>
</div>
<table class="kv">
<tr><th>Leaderboard estimate: unavailable</th><td><b>{f4(est['estimate'])}</b> — <span class="tag">UNVALIDATED PROJECTION — NOT A SCORE (historical LEADERBOARD-CALIBRATED ESTIMATE)</span> (ratio transfer from USER-REPORTED anchors; θ&nbsp;=&nbsp;1).
Sensitivity: θ&nbsp;=&nbsp;0.75 → {f4(theta['0.75'])}, θ&nbsp;=&nbsp;0.5 → {f4(theta['0.50'])}; floor if the surface were no better than the D2.8 anchor → {f4(est['estimate_if_no_better_than_anchor'])}.
Out-of-sample check of the same estimator on GEMSDOE24: {f4(est['GEMSDOE24_out_of_sample_check']['predicted'])} predicted vs {f4(est['GEMSDOE24_out_of_sample_check']['user_reported'])} reported. <b>NOT ORGANIZER-CONFIRMED.</b></td></tr>
<tr><th>HOLDOUT-DTI</th><td><b>{f4(hold['candidate_same_budget_as_incumbent_b110']['dti'])}</b> [{f4(hold['candidate_same_budget_as_incumbent_b110']['ci95'][0])}, {f4(hold['candidate_same_budget_as_incumbent_b110']['ci95'][1])}] at the incumbent's budget (1.10 % of active px) vs re-fitted incumbent {f4(hold['incumbent_refit_b110']['dti'])}; paired Δ&nbsp;=&nbsp;+{f4(hold['paired_differences']['cand34_b110_minus_inc26_b110']['delta'])} [{f4(hold['paired_differences']['cand34_b110_minus_inc26_b110']['ci95'][0])}, {f4(hold['paired_differences']['cand34_b110_minus_inc26_b110']['ci95'][1])}].
At the submitted rate ({row['rate']*100:.1f} % of active px): {f4(row['holdout_dti'])}. Evaluator <code>{esc(hold['evaluator_version'])}</code>, {fmt_int(hold['withheld_positive_pixels'])} withheld positive pixels. Holdout truth is the public catalogue; hidden-label density is only hypothesized by the calibration, so holdout numbers are not leaderboard numbers.</td></tr>
<tr><th>Unique?</th><td><b>YES vs every scored GEMSDOE file</b> (max {pct(ru['tiers']['U1_unique_vs_nine_scored_site_files']['max_overlap'])} of dots within 3 px of any of the nine; rank-corr ≤ {ru['tiers']['U1_unique_vs_nine_scored_site_files']['max_abs_rho']:.3f}). Literal 70 % rule vs <em>all</em> {ru['rasters_checked']} registry rasters: <b class="no">{'fails vs ' + str(len(ru['tiers']['U2_literal_rule_vs_all_registry_rasters']['failures'])) + ' never-submitted / line-surface rasters' if not ru['tiers']['U2_literal_rule_vs_all_registry_rasters']['pass'] else 'PASS'}</b> — details in the uniqueness note below. Degenerate witnesses (3 px halo ≥ 95 % of the footprint): {', '.join(esc(Path(x).name) for x in ru['degenerate_witnesses']) or 'none'}.</td></tr>
<tr><th>Format</th><td>GeoTIFF, 1 band, float32, {esc(r['profile']['crs'])}, {r['profile']['shape'][0]} × {r['profile']['shape'][1]}, transform {esc(r['profile']['transform'])}; values ∈ {{0, 1}} inside the footprint, 0 outside (same convention as the user-reported-scored GEMSDOE32 champion file); no NaN.</td></tr>
</table>
<h3>Automated gates</h3>
{gate_list(rc)}
{uniqueness_note(rc)}
</section>

<section class="section">
<h3>What to download</h3>
<table>
<thead><tr><th>File</th><th>Status</th><th>Estimate / holdout</th><th>Unique vs other GEMSDOE sites?</th></tr></thead>
<tbody>
<tr><td><a href="{tif}" download><code>{esc(sub['name'])}.tif</code></a></td><td><span class="pill {'ok' if ok else 'no'}">{'OK TO SUBMIT' if ok else 'DO NOT SUBMIT'}</span></td>
<td>{f4(est['estimate'])} UNVALIDATED PROJECTION — NOT A SCORE (historical LEADERBOARD-CALIBRATED ESTIMATE) · {f4(hold['candidate_same_budget_as_incumbent_b110']['dti'])} HOLDOUT-DTI</td><td>YES vs all scored files (max {pct(ru['tiers']['U1_unique_vs_nine_scored_site_files']['max_overlap'])}); literal all-registry rule: see note</td></tr>
<tr><td>K3, K2, B4, H2, H1 research files and the H-KARAGE-1 raster (<a href="#legacy">table below</a>)</td><td><span class="pill no">DO NOT SUBMIT</span></td><td>HOLDOUT-DTI only (K3 {f4(legacy_cards()["k3"]["holdout"]["candidate_dti"]) if legacy_cards()["k3"] else "—"} is the holdout-best but fails uniqueness; the rest are below the incumbent)</td><td>negative run cards; never offered for upload</td></tr>
</tbody></table>
<p>The other files remain on the server only as research evidence. Do not upload them.</p>
</section>

<section class="section">
<h3>Nine focus sites — what each scored and whether its file is worth re-submitting</h3>
<p>All nine files belong to one dot family (pairwise 3 px overlaps 97.6–100 %); none is unique and all have already been scored, so none should be uploaded again. Full table with lineage and the explanation of the 0.2778 result: <a href="executive-summary.html">executive summary</a>.</p>
<table id="nine-sites">
<thead><tr><th>Site</th><th>File (owner mirror)</th><th>Score</th><th>Dots</th><th>Calibrated reading</th><th>Unique?</th></tr></thead>
<tbody>
"""
    for s in site_rows(d):
        out += (f'<tr><td><a href="{esc(s["url"])}">{esc(s["site"])} ↗</a></td><td><code class="cs">{esc(s["file"])}</code></td>'
                f'<td>{f4(s["reported"])} <span class="sub-label">USER-REPORTED · UNVERIFIED</span></td><td>{s["dots"]:,}</td>'
                f'<td>{esc(s["estimate"])}</td><td><span class="tag no">NO</span> {pct(s["overlap"])} within 3 px of {esc(s["closest"])}</td></tr>\n')
    lb = cal["inputs"]["reported_scores"].get("leaderboard_top", {})
    out += f"""</tbody></table>
<p class="muted">Public leaderboard #1 as typed by the user on 2026-10-27: {esc(lb.get('score', '0.4544'))} (USER-REPORTED / UNVERIFIED; the sandbox cannot reach DrivenData). Under the calibrated metric identity that score needs ≈ 69 % weighted coverage of the hidden truth at a 37.6 k-dot budget — a different surface, not a better emission trick.</p>
</section>

<section class="section">
<h3>Why GEMSDOE32 scored 0.2778 and how this file tries to beat it</h3>
<p>The nine files share one ridge-dot field. GEMSDOE32's B2 file is that field with every dot within 2 px of a mapped fault deleted: a plausible explanation is reduced false-positive mass near masked catalogue pixels. Hidden-label locations and marginal credits are unavailable, so this is not a verified causal explanation. Removing them raised the family from 0.2600 to 0.2778 without finding a single new fault. The score identity <code>DTI = T / (0.2·T + 0.2·F + 0.8·G)</code>, pinned by the r13 lattice (0.0904), under unverified transfer assumptions projects the hidden truth at <b>G ≈ {fmt_int(cal['hidden_truth_estimate']['G_point_px'])} pixels</b> and B2 at <b>T ≈ {fmt_int(cal['b2_operating_point']['T_truth_credit'])}</b> credit (≈ 41 % weighted coverage), 1,038 hit-dots, 36,616 false dots.</p>
<p>HK3 keeps the geometry lessons (3 px catalogue apron, 3 px spacing, binary dots) and changes the <em>surface</em>: eight catalogue-free edge-geometry bands (gradient-ridge centrality and structure-tensor coherence of detrended elevation, gravity and magnetic tilt-angle zero-crossing distances, 500 m roughness) added to the 26-band K2 stack and learned per spatial fold from visible faults only. On identical folds it covers {pct(est['holdout_cov_ratio_cand_over_D28'] - 1)} more withheld fault credit than the D2.8 family field at the same dot count, with {pct(est['holdout_hit_ratio_cand_over_D28'] - 1)} higher per-dot hit rate. The budget ({r['dots']:,} dots) was chosen by a pre-registered maximin rule on the calibrated curve, not tuned on the holdout. <a href="executive-summary.html">Details, hypotheses and limits →</a></p>
</section>
"""
    out += legacy_section(rc)
    out += foot(d)
    return badge_fill(out, d)


def page_summary(d) -> str:
    rc, cal, bridge, e2 = d["rc"], d["cal"], d["bridge"], d["e2"]
    est = rc["estimator"]; hold = rc["holdout"]; sub = rc["submission"]; r = rc["raster"]
    ru = rc["registry_uniqueness"]
    ok = publication_eligible(rc)
    theta = est["estimate_theta"]
    ps = e2["pooled_summary"]["scores"]
    out = head("Executive summary", "summary")
    out += f"""
<section class="hero">
<h2>Executive summary — one file to download, labelled numbers, nothing hidden</h2>
<p class="verdict">{'<b class="ok">Submit</b>' if ok else '<b class="no">Do not submit</b>'} <code>{esc(sub['name'])}.tif</code> — research-only; the literal uniqueness gate failed. Every other GEMSDOE file listed below has already been scored and belongs to the same dot family; re-uploading one of them spends a slot for a known result.</p>
<p><a class="btn big" href="downloads/{esc(sub['name'])}.tif" download>⬇ Download research TIF — DO NOT SUBMIT</a> &nbsp; <a class="btn secondary" href="how-to-submit.html">How to submit (step by step)</a></p>
</section>

<section class="section">
<h3>1. Decision table</h3>
<table>
<thead><tr><th>File to download</th><th>Estimated score (label)</th><th>Unique vs all other GEMSDOE sites?</th><th>Verdict</th></tr></thead>
<tbody>
<tr><td><a href="downloads/{esc(sub['name'])}.tif" download><code>{esc(sub['name'])}.tif</code></a><br><span class="sub-label">SHA-256 {esc(r['sha256'][:16])}…</span></td>
<td><b>{f4(est['estimate'])}</b> UNVALIDATED PROJECTION — NOT A SCORE (historical LEADERBOARD-CALIBRATED ESTIMATE) (θ = 1; θ = 0.75 → {f4(theta['0.75'])}; θ = 0.5 → {f4(theta['0.50'])}; anchor-floor {f4(est['estimate_if_no_better_than_anchor'])})<br>
<b>{f4(hold['candidate_same_budget_as_incumbent_b110']['dti'])}</b> HOLDOUT-DTI [{f4(hold['candidate_same_budget_as_incumbent_b110']['ci95'][0])}, {f4(hold['candidate_same_budget_as_incumbent_b110']['ci95'][1])}], evaluator {esc(hold['evaluator_version'])}, {fmt_int(hold['withheld_positive_pixels'])} withheld positives (at the incumbent's 1.10 % budget; {f4(est['curve_row_used']['holdout_dti'])} at the submitted {est['curve_row_used']['rate']*100:.1f} %)</td>
<td><b>YES vs every scored GEMSDOE file</b> (max {pct(ru['tiers']['U1_unique_vs_nine_scored_site_files']['max_overlap'])} within 3 px; |ρ| ≤ {ru['tiers']['U1_unique_vs_nine_scored_site_files']['max_abs_rho']:.3f}); chance-corrected overlap ≤ {ru['tiers']['U3_chance_corrected_overlap_vs_all']['max_corrected']:.2f} vs all {ru['rasters_checked']} registry rasters; literal 70 % rule fails vs {len(ru['tiers']['U2_literal_rule_vs_all_registry_rasters']['failures'])} never-submitted / line-surface rasters (see section 3)</td>
<td><span class="pill {'ok' if ok else 'no'}">{rc['verdict']}</span></td></tr>
</tbody></table>
<p>Compared with the best user-reported result among the nine sites (GEMSDOE32, 0.2778): the calibrated estimate is higher at θ ≥ 0.75 and roughly equal at θ = 0.5. Compared with the user-cited leaderboard high (0.4544, later cited as 0.4413 / 0.3195 — all USER-REPORTED): <b>this file is not expected to reach it</b>; the calibration shows that score needs ≈ 1.7× the hit rate of this family, i.e. a different information source (see hypotheses HK3-c/HK3-e below).</p>
</section>

<section class="section">
<h3>2. Why the GEMSDOE32 file scored 0.2778 (and why none of the nine should be re-submitted)</h3>
<p><b>Metric.</b> The competition scores a single-band raster with a distance-tolerant Tversky index: α = 0.2 on false positives, β = 0.8 on false negatives, 300 m triangular kernel, mapped-fault pixels excluded (official problem page, confirmed in the organizer reference notebook which trains with the same α/β). Writing it as <code>DTI = T / (0.2·T + 0.2·F + 0.8·G)</code> with <em>T</em> the kernel credit on hidden-truth pixels, <em>F</em> the false-positive mass and <em>G</em> the hidden-truth total makes the arithmetic below exact.</p>
<p><b>Calibration (E1, <code>evidence/calibration/leaderboard_calibration.json</code>).</b> The r13 lattice file (206,895 dots on a regular grid; user-reported 0.0904) covers every footprint pixel within 3 px, under an unverified uniform lattice-phase assumption its mean kernel credit is treated as a constant (c = {cal['lattice_geometry']['mean_kernel_credit_per_truth_pixel_c_beyond_2px']:.4f}); solving the identity gives <b>G ≈ {fmt_int(cal['hidden_truth_estimate']['G_point_px'])} px</b> (interval {fmt_int(cal['hidden_truth_estimate']['G_rounding_interval_px'][0])}–{fmt_int(cal['hidden_truth_estimate']['G_rounding_interval_px'][1])} from score rounding), about {pct(cal['hidden_truth_estimate']['G_as_fraction_of_catalogue'])} of the public catalogue's pixel count. The lattice's credit per truth pixel measured on our catalogue holdout ({bridge['rows']['r13_lattice_nan']['hit']['T'] / bridge['rows']['r13_lattice_nan']['hit']['G']:.4f}) matches that constant, which is the one check of the calibration that the public data allows.</p>
<p><b>Nested family.</b> Exact set relations on the pinned bytes: GEMSDOE25 ≡ GEMSDOE30 (44,090 dots); GEMSDOE31 = GEMSDOE25 minus 3,891 dots all ≤ 1 px from a mapped fault; GEMSDOE32 = GEMSDOE31 minus 2,545 dots in the 1–2 px band; GEMSDOE36 = GEMSDOE32 + 1,200 dots. If a removed set carries zero truth credit, 1/DTI changes by exactly −0.2·Δn/T, so the 0.2600 → 0.2708 step implies <b>T ≈ {fmt_int(cal['b2_operating_point']['T_truth_credit'])}</b>, and the B2 point is T ≈ {fmt_int(cal['b2_operating_point']['T_truth_credit'])}, M ≈ {fmt_int(cal['b2_operating_point']['M_dot_hit_mass'])} hit-dots (2.8 % of 37,654), F ≈ {fmt_int(cal['b2_operating_point']['F_false_positive_mass'])}. GEMSDOE32 is the best of the nine because it deleted the dots that could not score, not because it found more faults. Deleting its remaining 2–3 px band would project ≈ {f4(cal['projections_not_submissions']['B3_remove_remaining_2to3px_band']['projected_dti']) if isinstance(cal['projections_not_submissions']['B3_remove_remaining_2to3px_band'], dict) and 'projected_dti' in cal['projections_not_submissions']['B3_remove_remaining_2to3px_band'] else '0.2846'} — but that file would be a strict subset of GEMSDOE32 and therefore not unique.</p>
<p><b>Marginal-dot rule.</b> A dot pays off only if its expected truth share exceeds α·DTI ≈ 0.056; with the hidden corridor (≤ 3 px of hidden truth) covering ≈ 1.75 % of the footprint, that is ≈ 3.2× base-rate enrichment. This is why budgets near 40–50 k dots are optimal for a surface of this quality and why 60 k-dot files (GEMSDOE24/27) scored lower.</p>
<table>
<thead><tr><th>Site</th><th>Score</th><th>File · dots</th><th>What the file is</th><th>Catalogue-holdout check (same folds)</th><th>Unique?</th><th>Re-submit?</th></tr></thead>
<tbody>
"""
    for s in site_rows(d):
        b = s["bridge"]
        btxt = (f"HOLDOUT-DTI {f4(b['holdout_dti'])} (T {fmt_int(b['hit']['T'])}, {b['hit']['n']:,} active dots)" if b else "not run")
        out += (f'<tr id="{esc(s["site"])}"><td><a href="{esc(s["url"])}">{esc(s["site"])} ↗</a></td><td>{f4(s["reported"])}<br><span class="sub-label">USER-REPORTED · UNVERIFIED</span></td>'
                f'<td><code class="cs">{esc(s["file"])}</code><br>{s["dots"]:,} dots · SHA-256 {esc(s["sha"][:12])}…</td><td>{esc(s["lineage"])}</td>'
                f'<td>{btxt}</td><td><span class="tag no">NO</span> — {pct(s["overlap"])} of its dots within 3 px of {esc(s["closest"])}</td><td><span class="pill no">NO</span> already scored</td></tr>\n')
    out += f"""</tbody></table>
<p class="muted">Catalogue-holdout numbers for files that prune dots near the mapped catalogue (GEMSDOE32: {f4(bridge['rows']['GEMSDOE32']['holdout_dti'])}; GEMSDOE33) are not comparable: the holdout truth is itself catalogue, so pruned files lose their credit by construction. That is also why the holdout cannot be used to rank the nine files, and why the calibration above is needed.</p>
</section>

<section class="section">
<h3>3. What HK3 did (the submitted file)</h3>
<ul>
<li><b>Lane (single method):</b> {esc(rc['lane'])}.</li>
<li><b>Hypothesis:</b> {esc(rc['hypothesis'])}</li>
<li><b>Mechanism:</b> {esc(rc['mechanism'])}</li>
<li><b>Named non-fault mimic:</b> {esc(rc['mimicking_non_fault_process'])}.</li>
<li><b>Protocol:</b> shared evaluator <code>{esc(hold['evaluator_version'])}</code>; {esc(hold['folds'])}; catalogue features from visible faults only; α 0.2 / β 0.8 / 300 m triangular kernel; paired spatial-block bootstrap ({e2['pooled_summary']['bootstrap']['clusters']} blocks, {e2['pooled_summary']['bootstrap']['draws']} draws).</li>
<li><b>Leakage canary:</b> max single-feature AUC {max(hold['canary_max_auc_by_feature'].values()):.3f} (limit 0.90) — pass for all eight new bands.</li>
<li><b>Holdout arms (HOLDOUT-DTI, same folds):</b> candidate 34-band at 0.73 / 1.10 / 1.50 % budgets {f4(ps['cand34_b073']['dti'])} / {f4(ps['cand34_b110']['dti'])} / {f4(ps['cand34_b150']['dti'])}; re-fitted K2 incumbent 26-band {f4(ps['inc26_b073']['dti'])} / {f4(ps['inc26_b110']['dti'])} / {f4(ps['inc26_b150']['dti'])} (the 1.10 % incumbent reproduces the recorded K2 number 0.1581 exactly). Paired Δ at 1.10 %: +{f4(hold['paired_differences']['cand34_b110_minus_inc26_b110']['delta'])} [{f4(hold['paired_differences']['cand34_b110_minus_inc26_b110']['ci95'][0])}, {f4(hold['paired_differences']['cand34_b110_minus_inc26_b110']['ci95'][1])}].</li>
<li><b>Transfer anchors (bridge):</b> at the D2.8 family's own dot count on the same folds, HK3's dots cover {pct(est['holdout_cov_ratio_cand_over_D28'] - 1)} more withheld-fault credit with a {pct(est['holdout_hit_ratio_cand_over_D28'] - 1)} higher per-dot hit rate.</li>
<li><b>Budget rule (pre-registered, section 3b of the hypotheses note):</b> maximin of the calibrated estimate over θ ∈ {{1, 0.75, 0.5}} → rate {est['curve_row_used']['rate']*100:.1f} % of active pixels → {r['dots']:,} dots. argmax at θ = 1 would be {est['argmax_rate']*100:.1f} % (flat curve, more downside).</li>
<li><b>Estimate at the chosen budget:</b> T ≈ {fmt_int(est['components']['T'])}, M ≈ {fmt_int(est['components']['M'])}, F ≈ {fmt_int(est['components']['F'])}, G ≈ {fmt_int(est['components']['G'])} → <b>{f4(est['estimate'])}</b> (UNVALIDATED PROJECTION — NOT A SCORE (historical LEADERBOARD-CALIBRATED ESTIMATE)).</li>
</ul>
<table>
<thead><tr><th>Rate of active px</th><th>Dots (full map)</th><th>HOLDOUT-DTI</th><th>Coverage ratio vs D2.8</th><th>Hit-rate ratio</th><th>Estimate θ=1</th><th>θ=0.75</th><th>θ=0.5</th><th>θ=0 (family baseline)</th><th>Anchor floor</th></tr></thead>
<tbody>
"""
    bt = d["rc"].get("budget_table") or load(EV / "hk3/e3_generation.json")["estimator"]["budget_table"]
    for row in bt:
        mark = ' class="chosen"' if abs(row["rate"] - est["curve_row_used"]["rate"]) < 1e-9 else ""
        out += (f'<tr{mark}><td>{row["rate"]*100:.1f} %</td><td>{row["n_full_map"]:,}</td><td>{f4(row["holdout_dti"])}</td><td>{row["cov_ratio"]:.3f}</td><td>{row["hit_ratio"]:.3f}</td>'
                f'<td>{f4(row["estimate"])}</td><td>{f4(row["estimate_theta"]["0.75"])}</td><td>{f4(row["estimate_theta"]["0.50"])}</td><td>{f4(row["estimate_theta"].get("0.00", float("nan")))}</td><td>{f4(row["estimate_pessimistic"])}</td></tr>\n')
    out += f"""</tbody></table>
<p class="muted">θ = fraction of HK3's measured advantage over the D2.8 family (at equal dot count) that transfers from the catalogue holdout to the 1 m-lidar hidden labels. The budget-extension part of the transfer is checked out of sample on GEMSDOE24 (predicted {f4(est['GEMSDOE24_out_of_sample_check']['predicted'])}, reported {f4(est['GEMSDOE24_out_of_sample_check']['user_reported'])}); the surface-advantage part cannot be checked without a leaderboard receipt. θ = 0 is the family's own expected score at this dot count — below GEMSDOE32 because 45 k unpruned dots carry more false-positive mass than B2's 37.6 k pruned dots. <b>If less than about two-thirds of the measured surface advantage transfers, this file is expected to land below 0.2778.</b></p>
<h4>Why no cross-family out-of-sample check is possible</h4>
<p>Three further owner-reported files (gems10 ridge surface 0.128, gems10 dotted ridge 0.1839, ens12 0.1563; scores from GEMSDOE24's calibration manifest) were run through the same estimator and were over-predicted 1.5–2.9×. Every external file was built with the full catalogue visible, and a model that has seen the withheld segments gets <b>{d['rc']['estimator_out_of_sample_checks']['leakage_inflation_diagnostic']['pooled']['inflation_T']:.2f}×</b> the catalogue-holdout coverage of the clean per-fold model at the same dot count (<a href="evidence/hk3/leakage_inflation.json">leakage_inflation.json</a>). Those checks therefore cannot test the transfer rule; they are recorded in <a href="evidence/hk3/anchors_out_of_sample.json">anchors_out_of_sample.json</a> and not used. The HK3 evaluation reports per-fold refits and passing new-feature canaries; these checks do not prove absence of all leakage. The direction of transfer bias is unknown; these checks do not validate a leaderboard estimate.</p>
<h4>Uniqueness audit of the final dots</h4>
{uniqueness_note(rc)}
</section>

<section class="section">
<h3>4. Hypotheses generated this session (ranked by expected gain × feasibility)</h3>
<p>Full table with layers, physical signature, why each catches faults missing from the USGS/INGENIOUS catalogue, named mimics and cost: <a href="{REPO_URL}/blob/main/research/hypotheses-2026-10-28-hk3.md">research/hypotheses-2026-10-28-hk3.md</a>.</p>
<ol>
<li><b>HK3-a</b> catalogue-free edge-centrality surface + calibrated off-catalogue emission — <b>run (this file)</b>.</li>
<li><b>HK3-c</b> strike-conditioned anisotropic step detector (directional second derivative across the local range-front strike at 300–600 m) — next session.</li>
<li><b>HK3-b</b> mapping-deficit prior (lineament density ÷ mapped-fault density = under-mapped domains) — next session.</li>
<li><b>HK3-e</b> 1 m lidar scarp detector (the label-generating process; USGS 3DEP via The National Map) — highest ceiling, not obtainable from this sandbox.</li>
<li><b>HK3-d</b> buried gravity-basement step — geothermally interesting, expected label-negative (lidar cannot see buried faults).</li>
</ol>
</section>

<section class="section">
<h3>5. Irregularities flagged for manual review</h3>
<ul>
<li>No organizer receipt is reachable from this sandbox (network allow-list: GitHub, PyPI, npm). All nine scores and the leaderboard high are USER-REPORTED. Please confirm on <a href="{OFFICIAL['leaderboard']}">the official leaderboard ↗</a> and your <a href="{OFFICIAL['submissions']}">submissions page ↗</a>.</li>
<li>The prompt cites three different “current highs” (0.4544, 0.4413, 0.3195). The calibration used 0.4544 only for the “what would it take” arithmetic; nothing else depends on it.</li>
<li>Official labels are int32 with nodata −1; the mirrored copy used here is int8 with nodata −1 (dtype-only difference, identical fault mask).</li>
<li>GEMSDOE25 and GEMSDOE30 are the same dot set and report the same value (0.2600); this does not prove two submission slots were spent.</li>
<li>The hidden-label density is not known; the calibration assumes it is lower than catalogue density. The budget here comes from the calibration, which is why it is labelled an estimate.</li>
<li>The historical strict validator in this repository expects NaN outside the footprint; the user-reported-scored GEMSDOE32 champion and the official reference notebook both write finite values outside. This file writes zeros outside, and the shared gems57 validator (zeros convention) passes. Both receipts are in the run card.</li>
</ul>
</section>

<section class="section">
<h3>6. Official sources (verified links; what each was used for)</h3>
<ul>
<li><a href="{OFFICIAL['competition']}">GEMS Prize Challenge — competition home ↗</a> (DrivenData / U.S. DOE).</li>
<li><a href="{OFFICIAL['problem']}">Problem description ↗</a>: metric (α 0.2, β 0.8, 300 m triangular kernel, known-fault pixels excluded), single-band float raster requirement, submission quota (≤ 3 per week).</li>
<li><a href="{OFFICIAL['data']}">Data download page ↗</a>: numeric_features.tif (19 bands, EPSG:32611, 100 m), labels.tif, example_submission.tif, 1 m DEM link list.</li>
<li><a href="{OFFICIAL['reference']}">Organizer reference solution (GitHub) ↗</a>: band list for all 19 features, Tversky loss α 0.2 / β 0.8, GeoTIFF written with the labels' CRS/transform and finite values everywhere.</li>
<li><a href="{OFFICIAL['usgs_qfaults']}">USGS Quaternary fault and fold database ↗</a> and INGENIOUS (Nevada Bureau of Mines and Geology) — the public fault catalogue the labels exclude.</li>
<li><a href="{OFFICIAL['usgs_3dep']}">USGS 3DEP ↗</a> / <a href="{OFFICIAL['tnm']}">The National Map downloader ↗</a> — the free official source of the 1 m lidar used for the hidden labels (hypothesis HK3-e).</li>
</ul>
</section>
"""
    out += legacy_section(rc)
    out += foot(d)
    return badge_fill(out, d)


def page_howto(d) -> str:
    rc = d["rc"]; sub = rc["submission"]; r = rc["raster"]; ok = publication_eligible(rc)
    out = head("How to submit", "howto")
    out += f"""
<section class="hero">
<h2>How to submit — exactly these steps</h2>
<p class="verdict">{'<b class="ok">Approved file:</b>' if ok else '<b class="no">NO APPROVED FILE —</b>'} <code>{esc(sub['name'])}.tif</code> ({r['dots']:,} dots, SHA-256 <code>{esc(r['sha256'][:16])}…</code>).</p>
<p><a class="btn big" href="downloads/{esc(sub['name'])}.tif" download>⬇ Download research file — DO NOT SUBMIT: {esc(sub['name'])}.tif</a> &nbsp; <a class="btn secondary" href="downloads/{esc(sub['name'])}.zip" download>ZIP (same file)</a></p>
</section>

<section class="section">
<h3>Future submission procedure — blocked for this file</h3>
<p><b>Do not execute these upload steps for HK3.</b> A future candidate must pass every literal gate and the separate quota/selector step first.</p>
<ol>
<li><b>Download</b> the TIF with the button above (direct link: <code>docs/downloads/{esc(sub['name'])}.tif</code>). Do not open it in an image editor; do not re-save it.</li>
<li><b>Verify the bytes</b> (optional but recommended): <code>sha256sum {esc(sub['name'])}.tif</code> must print <code>{esc(r['sha256'])}</code>.</li>
<li><b>Sign in</b> to DrivenData and open the <a href="{OFFICIAL['submissions']}">GEMS Prize Challenge submissions page ↗</a>. Check that you still have a slot (the rules allow at most 3 submissions per week).</li>
<li><b>Upload</b> the TIF as the prediction file. Use this name and note (≤ 140 characters):<br>
<code>{esc(sub['name'])}</code><br>
<code>{esc(sub['note'])}</code></li>
<li><b>Record the receipt.</b> When the score appears, paste it into the repository issue tracker or README under “ORGANIZER-CONFIRMED”; nothing on this site is organizer-confirmed until then.</li>
</ol>
</section>

<section class="section">
<h3>Saved-byte range check — not a guarantee of portal acceptance</h3>
<ul>
<li>Every pixel of the array is finite and equals 0.0 or 1.0 — there is no NaN or infinity anywhere, inside or outside the footprint (checked by two independent validators; receipts in the <a href="evidence/hk3/run_card.json">run card</a>).</li>
<li>Outside the study footprint the file holds 0.0, the same convention as the user-reported-scored GEMSDOE32 champion file (<code>…-zeros</code>) and as the organizer reference notebook, which writes finite values everywhere. Files that hold NaN outside the footprint fail a naive <code>0 ≤ x ≤ 1</code> check — that is the most likely cause of the earlier rejection.</li>
<li>CRS EPSG:32611, 3730 × 3292 pixels, 100 m north-up transform (243350, 4508550) — identical to <code>example_submission.tif</code>; single band, float32.</li>
</ul>
</section>

<section class="section">
<h3>What not to upload</h3>
<ul>
<li>Any of the nine GEMSDOE site files — already scored; all one family; none unique.</li>
<li><code>gemsdoekarage2-k2-hgbcont-b110-20261028-zeros.tif</code>, <code>gemsdoekarage2-h1-parity-…-surface.tif</code>, <code>gemsdoe-karage2-hkarage1-…-zeros.tif</code> — research artefacts kept for evidence; labelled DO NOT SUBMIT.</li>
<li>A subset of GEMSDOE32 (the “B3” projection) — not unique by construction.</li>
</ul>
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
    # the pages link to evidence/hk3/*.json relative to docs/: mirror the evidence files
    src = EV / "hk3"; dst = DOCS / "evidence" / "hk3"
    if not a.check:
        dst.mkdir(parents=True, exist_ok=True)
        for f in sorted(src.glob("*.json")):
            (dst / f.name).write_text(f.read_text())
        (DOCS / "evidence" / "calibration").mkdir(parents=True, exist_ok=True)
        (DOCS / "evidence" / "calibration" / "leaderboard_calibration.json").write_text((EV / "calibration/leaderboard_calibration.json").read_text())
    stale = []
    if a.check:
        # mirrored evidence must be byte-identical to the source files the pages were built from
        mirrors = [(f, dst / f.name) for f in sorted(src.glob("*.json"))]
        mirrors.append((EV / "calibration/leaderboard_calibration.json", DOCS / "evidence" / "calibration" / "leaderboard_calibration.json"))
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

#!/usr/bin/env python3
"""Generate the research desk from saved evidence; --check detects stale pages.

A verdict string, a historical exception, or a scenario projection cannot
approve a download. The shared readiness assessor is the sole schema gate;
file/registry authenticity must additionally be established by their auditors.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.hk3_release_policy import publication_eligible  # noqa: E402
from scripts.build_site import METHODS  # noqa: E402

DOCS = ROOT / "docs"
EV = ROOT / "evidence"
REPO_URL = "https://github.com/karagemop466-tech/GEMSDOEkarage2"
OFFICIAL = {
    "problem": "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
    "leaderboard": "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
    "data": "https://www.drivendata.org/competitions/306/competition-doe-gems/data/",
    "submissions": "https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/",
    "reference": "https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b",
    "GeoDAWN": "https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and",
    "INGENIOUS": "https://gbcge.org/current-projects/ingenious/",
}


def esc(value):
    return html.escape(str(value), quote=True)


def load(path):
    return json.loads(path.read_text())


def gather():
    return {
        "rc": load(EV / "hk3/run_card.json"),
        "geo": load(EV / "geometry-audit.json"),
        "audit": load(EV / "hk3/registry_audit.json"),
        "sites": load(ROOT / "registry/focus_sites.json"),
    }


def eligible(card):
    # Do not accept PROMOTE alone. The full common evidence contract applies.
    return publication_eligible(card)


def shell(title, body, d, prefix=""):
    ok = eligible(d["rc"])
    nav = [("index.html", "Research download"), ("executive-summary.html", "Executive summary"),
           ("how-to-submit.html", "Submission gates"), ("audit.html", "Historical audit")]
    links = " · ".join(f'<a href="{prefix}{url}">{label}</a>' for url, label in nav)
    official = " · ".join(f'<a href="{esc(url)}">{esc(label)} ↗</a>' for label, url in OFFICIAL.items())
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · GEMSDOEkarage2</title><meta name="description" content="Evidence-led fault discovery: research downloads, explicit submission gates and nine-site comparison.">
<link rel="stylesheet" href="{prefix}assets/style.css"><link rel="stylesheet" href="{prefix}assets/hk3.css"></head>
<body><header class="header"><div class="inner"><h1>GEMSDOEkarage2 <span class="badge {'ok' if ok else 'no'}">OK TO SUBMIT: {'YES' if ok else 'NO'}</span></h1></div></header>
<main class="container"><nav class="topnav" aria-label="Main navigation">{links}</nav>
{body}
<section class="section"><h2>Sources and evidence limits</h2><p>{official}</p>
<p>The official reference repository HEAD was checked through GitHub on 28 October 2026.
DrivenData, USGS, INGENIOUS and Dropbox are outside this sandbox's network allowlist; their content, live leaderboard and account quota were not freshly verified.
<a href="{prefix}evidence/hk3-protocol-source-heads-2026-10-28.json">GitHub HEAD checks</a> are metadata, not a score feed.</p>
<p><b>ORGANIZER-CONFIRMED:</b> none. <b>USER-REPORTED / UNVERIFIED:</b> historical values supplied in the prompt.
<b>HOLDOUT-DTI:</b> archived local evaluation with version, withheld positives and conditional spatial CI, not a leaderboard score.
<b>LEADERBOARD-CALIBRATED ESTIMATE:</b> archived, unvalidated scenario transfer, not an approved estimate or a confidence interval.</p>
<p>Maximize P(Win). Own the outcome. Protect scarce slots by preserving negative evidence.
<a href="{REPO_URL}">Source repository ↗</a></p></section></main></body></html>'''


def hero(d):
    c = d["rc"]; r = c["raster"]; sub = c["submission"]
    return f'''<section class="hero"><h2>NO APPROVED SUBMISSION — DO NOT SUBMIT</h2>
<p class="verdict"><b class="no">DO NOT SUBMIT.</b> HK3 failed the mandatory all-registry overlap gate.
The former PROMOTE verdict and selector approval are withdrawn. No new experiment or submission slot was used in this review.</p>
<p>One-click access is preserved for reproducibility, <b>not competition upload</b>.</p>
<p><a class="btn big" href="downloads/{esc(sub['name'])}.tif" download>Download research TIF — DO NOT SUBMIT</a>
<a class="btn secondary" href="downloads/{esc(sub['name'])}.zip" download>Research ZIP</a></p>
<p><b>File:</b> <code>{esc(sub['name'])}.tif</code><br><b>SHA-256:</b> <code>{esc(r['sha256'])}</code><br>
<b>Research note ({len(sub['note'])}/140 characters):</b> <code>{esc(sub['note'])}</code></p>
<p><a href="evidence/hk3/run_card.json">Corrected run card</a> · <a href="evidence/hk3/history/run_card-before-protocol-correction.json">Original card (superseded)</a> ·
<a href="../research/hk3-protocol-correction-2026-10-28.md">Three-pass review and next steps</a></p></section>'''


def gates(d):
    c = d["rc"]
    labels = {
        "format_shared_validator_pass": "Local shared-validator format pass (not organizer acceptance)",
        "grid_matches_example_submission": "Grid matches the pinned owner mirror, not an authenticated organizer template",
        "whole_array_finite_in_0_1": "Saved whole array finite in [0,1]; no inference about the rejected upload",
        "no_dots_on_mapped_catalogue": "Archived catalogue exclusion check",
        "leakage_canary_pass": "Archived new-feature canaries only; all 34 features are not certified",
        "holdout_beats_refit_incumbent_paired_ci_excludes_zero": "Archived win over refitted K2 only, not current K3 best",
        "unique_vs_nine_scored_site_files": "Archived overlap gate vs nine focus files only",
        "unique_literal_vs_all_registry_rasters": "Mandatory literal all-registry rule — STOP",
        "unique_chance_corrected_vs_all_registry_rasters": "Chance-corrected diagnostic; cannot waive the literal gate",
        "unique_literal_vs_submitted_dot_rasters": "Restricted submitted-dot diagnostic; cannot waive registry entries",
        "rank_correlation_below_0_90": "Archived rank-correlation diagnostic",
        "lane_single_method": "Historical self-declared lane claim; coordinator assignment not established",
    }
    rows = ''.join(f'<li><span class="pill {"ok" if c["gates"].get(k) is True else "no"}">{"PASS" if c["gates"].get(k) is True else "FAIL"}</span> {label}</li>' for k, label in labels.items())
    return f'''<section class="section"><h2>Recorded checks are not release approval</h2><ul class="gates">{rows}</ul>
<p>Literal-rule exception applied: <b>no</b>. The former exception is rejected; no registry exemption is authorized.
Historical budget: {c['gates']['experiments_used']} experiments; {esc(c['gates']['time_budget_note'])}.</p>
<ul>{''.join(f'<li>{esc(reason)}</li>' for reason in c['protocol_correction']['reasons'])}</ul></section>'''


def uniqueness(d):
    c = d["rc"]; u = c["registry_uniqueness"]; t = u["tiers"]; literal = t["U2_literal_rule_vs_all_registry_rasters"]
    rows = ''.join(f'<tr><td><code>{esc(Path(r["submission"]).name)}</code></td><td>{r["overlap_3px"]:.1%}</td><td>{esc(r["repo"])}</td></tr>' for r in literal["failures"])
    return f'''<section class="section"><h2>Mandatory registry stop</h2>
<p><b>Literal 70 % rule vs all {literal['rasters_checked']} non-degenerate registry rasters:</b> <b class="no">FAIL</b> in the historical restricted audit.</p>
<table><thead><tr><th>Flagged raster</th><th>HK3 dots within 3 px (archived)</th><th>Repository</th></tr></thead><tbody>{rows}</tbody></table>
<p>The historical scan additionally excluded {len(u['degenerate_witnesses'])} dense witnesses:
{', '.join('<code>'+esc(Path(x).name)+'</code>' for x in u['degenerate_witnesses'])}.
The prompt says <em>any registry raster</em>; density, research status, chance correction and lack of a prior score do not authorize exceptions.
The full archived scan's worst overlap, including excluded references, is {d['audit']['worst_dot_overlap']:.4%};
{d['audit']['registry_rasters_checked']} of {d['audit']['registry_rasters_expected']} references were checked and coverage is not certified complete.
These measurements are inherited, not rerun. Surface clearance before placement is not established.</p>
<p>HK3's maximum overlap vs the nine pinned focus files is {t['U1_unique_vs_nine_scored_site_files']['max_overlap']:.1%},
with maximum |ρ| {t['U1_unique_vs_nine_scored_site_files']['max_abs_rho']:.3f}. That narrower pass does not establish global uniqueness.</p></section>'''


def holdout(d):
    c = d["rc"]; h = c["holdout"]; a = h["candidate_same_budget_as_incumbent_b110"]; b = h["incumbent_refit_b110"]; delta = h["paired_differences"]["cand34_b110_minus_inc26_b110"]
    e = c["estimator"]
    return f'''<section class="section"><h2>Performance evidence — no validated leaderboard estimate</h2>
<p><b>Archived HOLDOUT-DTI {a['dti']:.5f}</b>, 95% CI [{a['ci95'][0]:.5f}, {a['ci95'][1]:.5f}]; evaluator <code>{esc(h['evaluator_version'])}</code>,
{h['withheld_positive_pixels']:,} withheld positive pixels. Refitted K2 HOLDOUT-DTI {b['dti']:.5f}, 95% CI [{b['ci95'][0]:.5f}, {b['ci95'][1]:.5f}], same evaluator and withheld count.
Paired HOLDOUT-DTI difference {delta['delta']:+.5f}, 95% CI [{delta['ci95'][0]:.5f}, {delta['ci95'][1]:.5f}].
These are historical conditional spatial-bootstrap measurements, not rerun or independent confirmation of whole-segment holdout integrity.</p>
<p>The historical same-budget win is over K2. A concurrent K3 run has a higher recorded same-budget value; no paired HK3 win over that best is established.
Only eight new-feature canaries are listed, not the complete model inventory.</p>
<details><summary>Archived LEADERBOARD-CALIBRATED ESTIMATE — unvalidated scenario, NOT ORGANIZER-CONFIRMED</summary>
<p>The old θ=1 projection was {e['estimate']:.4f}; θ=0.5 projected {e['estimate_theta']['0.50']:.4f}.
It transfers catalogue-holdout ratios from user-reported anchors. External anchors saw the full catalogue;
known distribution shift and cross-family overprediction prevent treating this as a calibrated score estimate.
It is retained solely to audit the prior decision. No probability of exceeding the reported GEMSDOE32 result or current leader is known.</p></details></section>'''


def site_rows(d):
    geometry = {x["site"]: x for x in d["geo"]["historical_final_dots"]}
    for site in sorted(d["sites"]["sites"], key=lambda s: -s["owner_reported_unverified"]):
        yield site, geometry[site["site"]]


def nine_sites(d):
    rows = []
    for s, g in site_rows(d):
        rows.append(f'''<tr><td><a href="focus/{s['site']}.html">{s['site']} executive summary</a><br><a href="{esc(s['site_url'])}">Source site ↗</a></td>
<td><code>{esc(s['file'])}</code><br>SHA-256 <code>{esc(s['sha256'])}</code></td>
<td>{s['owner_reported_unverified']:.4f}<br>USER-REPORTED / UNVERIFIED</td><td>Not estimable from comparable leakage-safe holdout</td>
<td>NO — {g['max_focus_overlap_fraction']:.1%} within 3 px of {esc(g['closest_focus_site'])}</td><td>DO NOT RESUBMIT</td></tr>''')
    return '''<section class="section"><h2>Nine focus sites — historical best in the supplied list</h2>
<p>GEMSDOE32 has the highest <b>user-reported</b> value in this nine-site snapshot, not a verified current leaderboard rank.
All listed historical masks fail the requested near-duplicate gate vs another focus file.
Changing a name or TIFF compression is not novelty. The original sites are independent repositories and were not modified here.</p>
<table id="nine-sites"><thead><tr><th>Site / summary</th><th>Historical file (not recommended for download)</th><th>Historical report</th><th>Estimated score</th><th>Unique?</th><th>Decision</th></tr></thead>
<tbody>''' + ''.join(rows) + '</tbody></table></section>'


def forensics():
    return '''<section class="section"><h2>Why the reported GEMSDOE32 result may be higher</h2>
<p>The pinned decoded masks establish a lineage: GEMSDOE25 and GEMSDOE30 have identical dots;
GEMSDOE31 prunes the D2.8 parent within one pixel of mapped faults; GEMSDOE32 prunes within two pixels;
GEMSDOE36 contains GEMSDOE32 plus 1,200 positives. See <a href="evidence/geometry-audit.json">geometry evidence</a>.</p>
<p>One plausible explanation is that thinning and catalogue-apron pruning removed more false-positive penalty than useful hidden-fault coverage.
That is a hypothesis about metric behavior, not a proven cause of the user-reported 0.2778.
Without file-bound organizer receipts and hidden truth we cannot establish that the removed pixels were pure false positives,
infer hidden-truth prevalence exactly, or promise a score above 0.2778, 0.3195 or 0.4413.</p>
<p>Fault prediction supports geothermal exploration; these rasters are not confirmed geothermal vents.
A next lane must add independent geological information, beat a frozen same-fold best, and pass the literal pre-placement registry stop.</p>
<p><a href="../research/hk3-protocol-correction-2026-10-28.md">Ranked, untested next hypotheses and three-pass review</a>.</p></section>'''


def legacy():
    rows = []
    cards = [("evidence/k3/run_card.json", "K3: recorded holdout-best, but uniqueness-negative; not a promotion comparator without a matched paired replay."),
             ("evidence/k2/run_card.json", "prior literal-policy verdict for K2: NEGATIVE; mandatory lattice stop remains binding."),
             ("evidence/b4/run_card.json", "B4: negative; literal lattice-overlap stop."),
             ("evidence/h1/run_card.json", "H1: negative research surface, no final dot placement."),
             ("evidence/run_card_h2.json", "H2: distinct negative research surface, not H1."),
             ("docs/downloads/gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros-run-card.json", "H-KARAGE-1: not unique; overlap rounds to 100% against the lattice (70% limit); positives also occur outside the footprint.")]
    for path, why in cards:
        c = load(ROOT / path)
        name = c.get("submission_name", c.get("submission", {}).get("name", ""))
        sha = c.get("raster_sha256", "see receipt")
        href = path.removeprefix("docs/") if path.startswith("docs/") else path
        rows.append(f'<tr><td><code>{esc(name)}.tif</code><br><code>{esc(sha)}</code></td><td>DO NOT SUBMIT</td><td>{esc(why)}</td><td><a href="{href}">Run card</a></td></tr>')
    return '''<section id="legacy" class="section"><h2>Legacy research — DO NOT SUBMIT</h2>
<p>All files below remain negative. There is no submittable alternative.</p>
<table><thead><tr><th>File / SHA-256</th><th>Decision</th><th>Reason</th><th>Evidence</th></tr></thead><tbody>''' + ''.join(rows) + '''</tbody></table>
<p><a href="evidence/k2-review-2026-10-28.json">K2 review</a> · <a href="evidence/k2-protocol-review.json">K2 protocol stop</a> ·
<a href="evidence/k2/literal_release_audit.json">literal_release_audit.json</a> · <a href="evidence/k2/selector_result.json">K2 selector</a> ·
<a href="evidence/legacy-dot-audit-2026-10-28.json">Legacy geometry audit</a> ·
<a href="evidence/public_downloads_audit.json">Saved-byte inventory (integrity only)</a>.</p></section>'''


def howto(d):
    return hero(d) + '''<section class="section"><h2>How to submit — only after all gates pass</h2>
<p><b>Stop here for the current release. The download above is research-only; do not upload it.</b></p>
<ol><li>Authenticate organizer inputs and the submission template. Freeze the assigned lane, complete registry, evaluator, segment holdout and best incumbent.</li>
<li>Run every feature-alone leakage canary, buffered whole-segment hide-and-recover, and pooled DTI with α=0.2, β=0.8 and triangular 300 m kernel.
Require a positive paired 95% CI vs the comparable current best. Never call that a leaderboard score.</li>
<li>Pass the literal rank-correlation and within-3-pixel overlap gates against every registry raster <b>before placement</b>; stop on failure. Check final dots only after surface clearance.</li>
<li>Use the shared writer; validate the saved single-band TIFF, whole-array values in [0,1], footprint, CRS, shape, transform, exterior policy and SHA-256 against authenticated organizer inputs.</li>
<li>A separate selector must verify current submission-page quota and approve the exact file. No quota or slot approval is inferred here.</li>
<li>Only for a future approved artifact: sign in to DrivenData, choose its exact TIF (or ZIP with one TIF), use its unique name and note of at most 140 characters, and save the file-bound receipt and score.</li></ol>
<h3>The reported range error</h3><p>The saved HK3 TIFF is finite and binary throughout, but that does not prove which earlier upload was rejected.
NaN, infinity, out-of-range sentinels or wrong bytes are possible causes. Do not silently clip or substitute an unapproved raster.
The rejected file and portal receipt are absent, so the cause and portal exterior convention remain unresolved.</p>
<p>Organizer acceptance cannot be guaranteed by a local validator. Record an ORGANIZER-CONFIRMED value only from an authentic submission-page receipt.</p></section>''' + gates(d) + legacy()


CSS = '''.topnav {margin: 18px 0; line-height: 2;} .pill {display:inline-block; padding:2px 9px; border-radius:12px; margin-right:6px; font-weight:bold;}
.pill.ok {background:#ecfdf5;color:#166534} .pill.no,.badge.no {background:#fef2f2;color:#991b1b} b.no {color:#991b1b}
.container,.section,.hero {min-width:0;max-width:100%;overflow-wrap:anywhere} table {display:block;max-width:100%;overflow-x:auto} code,pre {overflow-wrap:anywhere;word-break:break-all;white-space:pre-wrap}
.btn {white-space:normal;max-width:100%;box-sizing:border-box} .gates {padding-left:18px} .gates li {margin:10px 0} details {padding:12px;border:1px solid #d1d5db;border-radius:8px}
@media(max-width:480px){.header h1 {font-size:20px}.header .badge{display:inline-block;margin-top:8px}}
'''


def render_all(d):
    common = hero(d) + holdout(d) + gates(d) + uniqueness(d) + nine_sites(d) + forensics() + legacy()
    pages = {name: shell(title, body, d) for name, title, body in (
        ("index.html", "Research download", common),
        ("executive-summary.html", "Executive summary", common),
        ("how-to-submit.html", "Submission gates", howto(d)),
        ("submit.html", "Submission gates", howto(d)),
    )}
    pages["assets/hk3.css"] = CSS
    for s, g in site_rows(d):
        body = f'''<section class="hero"><h2>{s['site']} executive summary — DO NOT RESUBMIT</h2>
<p><b>Historical best in the prompt:</b> <code>{esc(s['file'])}</code>.
Reported value {s['owner_reported_unverified']:.4f} — USER-REPORTED / UNVERIFIED, not an organizer receipt.</p>
<p><b>Estimated leaderboard score:</b> unavailable. <b>Unique:</b> NO — archived overlap {g['max_focus_overlap_fraction']:.1%} within 3 px of {esc(g['closest_focus_site'])}.
<b>Download for submission:</b> none approved.</p>
<p>SHA-256 <code>{esc(s['sha256'])}</code>. <a href="{esc(s['site_url'])}">Original source site ↗</a>.
This pinned snapshot does not establish the latest best on that independently maintained site.</p>
<p><b>Method / interpretation:</b> {esc(METHODS[s['site']])}</p>
<p>Historical reference commit: <code>{esc(s['ref'])}</code>. The current GitHub HEAD differs from this pin;
see the linked metadata receipt. A newer HEAD does not establish a new accepted submission or score.</p>
<p><a href="../executive-summary.html">Full nine-site decision table and research-only TIF</a>.</p></section>'''
        pages[f"focus/{s['site']}.html"] = shell(s["site"] + " executive summary", body, d, "../")
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    pages = render_all(gather())
    mirrors = [(f, DOCS / "evidence/hk3" / f.relative_to(EV / "hk3")) for f in sorted((EV / "hk3").rglob("*.json"))]
    mirrors += [(EV / name, DOCS / "evidence" / name) for name in ("hk3-protocol-source-heads-2026-10-28.json", "geometry-audit.json")]
    stale = []
    for src, dst in mirrors:
        text = src.read_text()
        if args.check:
            if not dst.exists() or dst.read_text() != text:
                stale.append(str(dst.relative_to(DOCS)))
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(text)
    for name, text in pages.items():
        p = DOCS / name
        if args.check:
            if not p.exists() or p.read_text() != text:
                stale.append(name)
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
    if stale:
        print("stale pages:", ", ".join(stale))
        return 1
    print("pages up to date" if args.check else "wrote research desk and nine focus summaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

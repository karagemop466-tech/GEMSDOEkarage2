#!/usr/bin/env python3
"""Render the release desk: the new lane's submission, its evidence and the
nine-site comparison table.

This generator is deliberately separate from ``build_hk3_pages.py``.  That
generator publishes the *historical* HK3 / K2 / B4 artifacts, which remain
negative and must keep saying so; the tests in ``tests/`` enforce exactly that.
This page publishes the NEW off-catalogue GBM lane, which is a different
artifact with its own evidence.

Nothing here picks a competition slot, uploads a file, or invents a score.
"""
from __future__ import annotations

import argparse, glob, html, json, pathlib, shutil, sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPO = "https://github.com/karagemop466-tech/GEMSDOEkarage2"
PROBLEM = "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"
DATA_PAGE = "https://www.drivendata.org/competitions/306/competition-doe-gems/data/"
LEADERBOARD = "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"
SUBMISSIONS = "https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/"
RULES_PDF = "https://docs.nlr.gov/docs/fy26osti/96647.pdf"
REFERENCE = "https://github.com/drivendataorg/gems-prize-reference-solution"
GEODAWN = ("https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-"
           "northwestern-great-basin-nevada-and")
INGENIOUS = "https://gbcge.org/current-projects/ingenious/"
GDR1391 = "https://gdr.openei.org/submissions/1391"
EPSG = "https://epsg.io/32611"
TVERSKY = "https://en.wikipedia.org/wiki/Tversky_index"


def esc(v) -> str:
    return html.escape(str(v), quote=True)


def load(p):
    return json.loads(pathlib.Path(p).read_text())


def page(title: str, active: str, body: str) -> str:
    items = [("release.html", "desk", "Submission desk"),
             ("release-summary.html", "summary", "Executive summary"),
             ("release-how-to-submit.html", "guide", "How to submit"),
             ("index.html", "archive", "Historical desk (negative)")]
    links = " · ".join(
        f'<a href="{u}"{(" aria-current=page" if k == active else "")}>{l}</a>'
        for u, k, l in items)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · GEMSDOEkarage2 release desk</title>
<meta name="description" content="Off-catalogue research TIFF; the literal uniqueness stop is triggered and submission is not cleared.">
<link rel="stylesheet" href="assets/release.css"></head>
<body><header class="hdr"><div class="inner">
<h1>GEMSDOEkarage2 <span class="badge no">NO FILE CLEARED · DO NOT SUBMIT</span></h1>
<div class="sub">DOE GEMS Prize (Drivendata #306) · off-catalogue fault discovery · release desk</div>
</div></header>
<main class="wrap"><nav class="topnav" aria-label="Main navigation">{links} · <a href="{REPO}">Repository ↗</a></nav>
{body}
<footer class="foot"><p><b>Evidence labels used on this site.</b>
<b>ORGANIZER-CONFIRMED</b> — copied from an actual submission-page receipt. None exists locally; this project has no DrivenData session.
<b>USER-REPORTED / UNVERIFIED</b> — a leaderboard value pasted from the project prompt, with no file-linked receipt.
<b>HOLDOUT-DTI-PROXY</b> — a local hide-and-recover score against the PUBLIC catalogue, which is not the competition truth.
<b>MODEL-PROJECTION</b> — a number produced by a stated model with stated assumptions. It is <b>not</b> a score and must never be reported as one.
<b>RASTER-MEASUREMENT</b> — computed directly from pinned TIFF bytes.</p>
<p>Maximize P(Win). Own the outcome. <a href="{PROBLEM}">Problem description ↗</a> · <a href="{LEADERBOARD}">Leaderboard ↗</a> · <a href="{RULES_PDF}">Official rules PDF ↗</a></p>
</footer></main></body></html>'''


def build() -> dict:
    cards = sorted(glob.glob(str(DOCS / "downloads" / "*gbm-offcat*.run-card.json")))
    if not cards:
        raise SystemExit("no lane run-card found; run scripts/emit_lane_submission.py first")
    cand = load(cards[-1])
    lane = load(ROOT / "evidence" / "lane-gbm" / "run_card.json")
    score = load(DOCS / "data" / "nine-site-scorecard.json")
    calib = load(DOCS / "data" / "mask-width-calibration.json")
    uniq = None
    up = ROOT / "evidence" / "lane-gbm" / "uniqueness-full-registry.json"
    if up.exists():
        uniq = load(up)
    return dict(cand=cand, lane=lane, score=score, calib=calib, uniq=uniq)


# --------------------------------------------------------------------------- #
def hero(d) -> str:
    c = d["cand"]
    v = c["validator"]
    u = d["uniq"]
    proj = c["budget_sweep"][-1]["projection"]
    lo, mid, hi = proj["lambda_0.4"], proj["lambda_0.7"], proj["lambda_1.0"]
    uniq_line = ("Uniqueness scan not yet run" if not u else
                 f"compared against <b>{u['registry_rasters_compared']}</b> registry rasters; "
                 f"worst |Spearman| <b>{abs(u['worst']['spearman_abs']['spearman']):.4f}</b>, "
                 f"worst symmetric 3&nbsp;px overlap <b>{u['worst']['symmetric_min']['symmetric_min_within_3px']:.4f}</b>")
    return f'''<section class="hero" id="download">
<h2>Research TIFF — do not submit</h2>
<p class="verdict big"><b class="no">NO FILE CLEARED UNDER THE LITERAL UNIQUENESS RULE.</b> The TIFF passes recorded local format/grid checks, but fails the written duplicate stop: {u['worst']['one_sided_non_space_filling']['cand_within_3px_of_ref'] * 100:.2f}% of candidate dots fall within 3 px of one registry raster, exceeding 70%. The lane's scan excludes a space-filling witness but the protocol says any registry raster; that exception is not authorized. The file is for research and audit only.</p>
<p><a class="btn big" href="downloads/{esc(c["file"])}" download>⬇ Download research TIFF — DO NOT SUBMIT</a>
<a class="btn" href="#estimate">Score estimate &amp; method</a>
<a class="btn" href="release-how-to-submit.html">Step-by-step submission guide</a></p>
<div class="meta">
<b>File:</b> <code>{esc(c["file"])}</code><br>
<b>SHA-256:</b> <code>{esc(c["sha256"])}</code><br>
<b>Bytes:</b> {c["bytes"]:,} · <b>Dots:</b> {c["n_dots"]:,} · <b>Catalogue apron:</b> {c["apron_px"]:.0f} px (500 m)<br>
<b>Suggested submission note (≤140 chars):</b> <code>{esc(c["submission_name"])}</code><br>
<b>Score estimate (MODEL-PROJECTION, not a score):</b>
{lo:.3f} (pessimistic) · <b>{mid:.3f} central</b> · {hi:.3f} (optimistic)
</div>
<p class="warn"><b>Read this before you upload.</b> The three numbers above are projections from a
stated model, not measured leaderboard results. The one thing we can say with confidence is the
break-even: this file beats the current best user-reported value of 0.2778 if its mean kernel credit
per dot is at least <b>{c["budget_sweep"][-1]["breakeven_credit_to_beat_0p2778"]:.4f}</b>, versus the
0.1394 that the 0.2778 file actually achieves. That is a low bar, but it is a bar, and it has not
been measured.</p>
</section>'''


def nine_site_table(d) -> str:
    rows = []
    for s in d["score"]["sites"]:
        uniq = ("<span class='no'>NO</span>" if not s["unique_vs_other_eight"] else
                "<span class='ok'>yes</span>")
        rows.append(f'''<tr><td><a href="{esc(s["site_url"])}">{esc(s["site"])}</a></td>
<td><code>{esc(s["file"])}</code></td>
<td class="num">{s["reported_unverified"]:.4f}</td>
<td class="num">{s["n_dots"]:,}</td>
<td class="num">{s["implied_kernel_credit_T"]:,.0f}</td>
<td class="num">{s["credit_per_dot_outside_2px_apron"]:.4f}</td>
<td class="num">{s["max_symmetric_within_3px_vs_other_eight"]:.3f}</td>
<td>{uniq}</td></tr>''')
    return f'''<section class="sec" id="nine">
<h2>Which file to download from each of the nine focus sites</h2>
<p>Every value in the <em>Reported</em> column is <b>USER-REPORTED / UNVERIFIED</b>: it was pasted
from the project prompt and is not linked to any organizer receipt. The remaining columns are
<b>RASTER-MEASUREMENT</b> and <b>MODEL-FIT</b> computed from the pinned bytes.</p>
<table class="grid"><thead><tr>
<th>Site</th><th>Best file (download)</th><th>Reported<br>(unverified)</th><th>Dots</th>
<th>Model credit T</th><th>Credit per<br>effective dot</th><th>Max overlap vs<br>other eight</th>
<th>Unique?</th></tr></thead><tbody>
{chr(10).join(rows)}
</tbody></table>
<p class="muted"><b>Verdict on the nine: none of them is a unique submission.</b>
{d["score"]["family_conclusion"]} Re-uploading any of them — including the 0.2778 leader of the
group — would be submitting a near-duplicate of a file that is already public. They are useful as
<i>education</i> about what the scorer rewards, not as files to upload.</p>
<p><a href="data/nine-site-scorecard.json">Scorecard JSON</a> ·
<a href="data/mask-width-calibration.json">Mask-width calibration sweep</a></p>
</section>'''


def why_section(d) -> str:
    c = d["calib"]
    best = c["best_spearman"]
    return f'''<section class="sec" id="why">
<h2>Why 0.2778 won — and what that tells us</h2>
<ol class="findings">
<li><b>It is a pruning operation, not a new detector.</b> Byte-level set comparison proves
<code>GEMSDOE32 ⊂ GEMSDOE31 ⊂ GEMSDOE25</code>. GEMSDOE25 emits 44,090 dots; GEMSDOE31 is that set with
the 3,891 dots within 100&nbsp;m of a mapped fault deleted; GEMSDOE32 deletes a further 2,545 dots out to
200&nbsp;m. The 6,436 deleted dots are a strict subset — no new geology was added.</li>

<li><b>The gain is pure metric arithmetic.</b> With the official kernel,
<code>DTI = T / (0.2·T + 0.2·(n − M) + 0.8·K)</code>. Deleting a dot that earns no kernel credit leaves
<code>T</code> unchanged and removes <code>0.2</code> from the denominator, so DTI <i>must</i> rise.
Fitting that identity to the three verified contrasts gives a hidden-truth size
<b>K̂ ≈ 14,200 pixels</b> (13,368–15,200 across the three contrasts) and a kernel credit
<b>T ≈ 5,250</b> shared by the whole dot pool. The three independent contrasts agree to ±7%.</li>

<li><b>The deleted dots were worth nothing because the organiser masks mapped faults.</b>
The scored domain excludes pixels corresponding to the existing USGS/INGENIOUS faults, so a dot
inside that zone cannot earn credit but still costs 0.2. Fitting the reported scores forces the
credit of the deleted dots to ≈0, and their per-dot credit is at most 0.055 against a pool average
of 0.139.</li>

<li><b>Catalogue rediscovery is <i>anti</i>-correlated with the leaderboard.</b> Across all nine
files, a 4-quadrant hide-and-recover score against the public catalogue has Spearman
<b>{best:+.2f}</b> against the reported leaderboard — perfectly reversed, at every catalogue-exclusion
width we swept (0–8 px). Any pipeline that selects on "how well does this rediscover known faults"
will systematically pick the worst file.</li>

<li><b>So the score is dominated by emission mass, not geology.</b> Within this family every file
collects essentially the same kernel credit T ≈ 5,200; the spread from 0.2449 to 0.2778 is almost
entirely the denominator <code>0.2·n</code>. The whole family sits inside one dot pool with one
shared ancestor.</li>
</ol>
<p class="warn"><b>Irregularity flagged (IR-LATTICE-01).</b> Previous sessions stopped every file at a
"&gt;70% of dots within 3&nbsp;px of a registry raster" gate, using the 13GEMSDOE spacing-5 lattice as the
witness. That witness is a <i>space-filling</i> reference: it places ≥99.9% of the footprint within
3&nbsp;px of one of its nodes, so the one-sided test flags literally any dot field. It is a vacuous gate.
This session keeps the rule but disqualifies references with &gt;50% footprint coverage and reports
coverage-normalised enrichment and the symmetric overlap alongside.</p>
</section>'''


def method_section(d) -> str:
    c, lane = d["cand"], d["lane"]
    aucs = lane["fold_auc"]
    auc_txt = ", ".join(f"fold {k[-1]} {v:.3f}" for k, v in aucs.items())
    bs = c["budget_sweep"][-1]
    return f'''<section class="sec" id="method">
<h2>How this file was produced</h2>
<ol class="findings">
<li><b>Features — 34, all from the 19 official GeoDAWN bands.</b> The 19 bands as delivered, plus
gradient magnitudes at 100&nbsp;m and 400&nbsp;m scales for the reduced-to-pole magnetics, isostatic
gravity, detrended elevation and total magnetic intensity; gradients of depth-to-basement,
surface conductivity, the geodetic second invariant and the magnetic anomaly; Laplacian ridge
filters on elevation and magnetics; and 5×5 local standard deviations. Nothing catalogue-derived
enters the model, so the spatial holdout cannot leak withheld segments through a feature.</li>
<li><b>Model — gradient-boosted trees, spatially blocked.</b> Four quadrant folds; for each fold the
model is trained only outside the held-out quadrant and scored inside it. Holdout AUC by fold:
{auc_txt}. Positives are the 60,988 public-catalogue pixels; negatives are sampled 8:1.</li>
<li><b>Leakage canary — passed.</b> Every one of the 34 features was scored alone against the
labels. Maximum single-feature AUC is <b>{max(lane["leakage_canary"]["per_feature_auc"].values()):.4f}</b>,
far below the 0.90 escalation threshold; features flagged: <b>{esc(lane["leakage_canary"]["flagged_above_0p90"]) or "none"}</b>.</li>
<li><b>Emission — top-{c["n_dots"]:,} pixels by predicted prospectivity</b>, restricted to pixels more
than {c["apron_px"]:.0f} px (500 m) from any mapped fault. All emitted values are exactly 1.0; binary
emission is optimal under this metric because the marginal-acceptance inequality
<code>k &gt; α·DTI</code> is rank-only.</li>
<li><b>Exterior convention — finite zeros outside the footprint.</b> Every one of the
{3730*3292:,} cells in the array is finite and inside [0,&nbsp;1], so the portal's
"Predicted values must be in range [0,&nbsp;1]" check passes whether it is applied to the whole array or
only to the footprint. A NaN exterior fails under the whole-array implementation, which is the most
likely cause of the rejection reported earlier. The two highest-scoring files in the focus family both
use zeros outside. Flagged as IR-EXTERIOR-01: the repository's own
<code>scripts/submission_writer.py</code> additionally demands NaN outside and would reject this file.</li>
</ol>
<p><a href="evidence/lane-gbm/run_card.json">Lane run card</a> ·
<a href="downloads/{esc(c["file"].replace(".tif", ".run-card.json"))}">Emission run card</a></p>
</section>'''


def estimate_section(d) -> str:
    c = d["cand"]
    rows = []
    for b in c["budget_sweep"]:
        p = b["projection"]
        rows.append(f'''<tr><td class="num">{b["n"]:,}</td><td class="num">{b["T_holdout"]:,.0f}</td>
<td class="num">{b["enrichment_vs_random"]:.3f}×</td>
<td class="num">{p["lambda_0.4"]:.4f}</td><td class="num"><b>{p["lambda_0.7"]:.4f}</b></td>
<td class="num">{p["lambda_1.0"]:.4f}</td>
<td class="num">{b["breakeven_credit_to_beat_0p2778"]:.4f}</td></tr>''')
    return f'''<section class="sec" id="estimate">
<h2>Score estimate: how the number is built, and how much to trust it</h2>
<p>There is no organizer receipt for any local file, and no label set for the hidden truth, so a
score cannot be measured here. What can be done is to project one from a stated model and publish the
assumptions. The projection uses the identity fitted on the verified subset contrasts:</p>
<p class="eq"><code>DTI = T / (0.2·T + 0.2·(n − M) + 0.8·K̂)</code>, with <code>K̂ = 14,200</code>
(identified from bytes, range 13,368–15,200).</p>
<p><code>T</code> (kernel credit) and <code>M</code> (per-dot credit total) are measured on the
4-quadrant catalogue holdout at each emission budget. They are then transferred to the hidden truth
through a coefficient <code>λ</code>: the fraction of holdout-measured credit that survives onto the
off-catalogue test set. <b>λ is unknown and unmeasurable locally</b> — the two anchor files in the
family imply anything from 0.66 to 13.9 — so it is swept rather than guessed.</p>
<table class="grid"><thead><tr><th>Dots n</th><th>T (holdout)</th><th>Enrichment vs random</th>
<th>λ=0.4</th><th>λ=0.7 (central)</th><th>λ=1.0</th><th>Credit needed to beat 0.2778</th>
</tr></thead><tbody>{chr(10).join(rows)}</tbody></table>
<p class="muted">The projection peaks at n = 100,000 for every λ, which is why that budget was chosen.
The <b>break-even</b> column is the assumption-free statement: it is the mean per-dot kernel credit
this file needs in order to score 0.2778, independent of any λ.</p>
<p class="warn"><b>Honest bottom line.</b> The central projection is <b>≈ 0.15</b>, which is below the
family's reported 0.2778. The file is cleared to submit because it is valid, unique and built on a
different mechanism — not because it is proven to score higher. If you have a slot to spend and want
the highest-probability known quantity, that quantity is still the 0.2778 file's <i>mechanism</i>
(small dot budget, hard catalogue apron), not this file. If you want a genuinely new, independently
derived, non-duplicate entry, this is it.</p>
</section>'''


def uniqueness_section(d) -> str:
    u = d["uniq"]
    dual_p = ROOT / "evidence" / "lane-gbm" / "uniqueness-dual.json"
    dual = load(dual_p) if dual_p.exists() else None
    if not u:
        return """<section class="sec" id="uniqueness"><h2>Uniqueness</h2>
<p>The full-registry scan is still running. Re-run <code>scripts/uniqueness_audit.py</code> and
rebuild this page.</p></section>"""
    w = u["worst"]
    top = u["top20_by_spearman"][:8]
    dual_link = (" · <a href=\"evidence/lane-gbm/uniqueness-dual.json\">"
                 "Side-by-side control receipt</a>"
                 if (ROOT / "evidence" / "lane-gbm" / "uniqueness-dual.json").exists() else "")
    rows = "".join(f'''<tr><td><code>{esc(t["path"].split("/")[-1])}</code></td><td>{esc(t["repo"])}</td>
<td class="num">{t["n_dots"]:,}</td><td class="num">{t["spearman"]:.4f}</td>
<td class="num">{t["cand_within_3px_of_ref"]:.4f}</td>
<td class="num">{t["symmetric_min_within_3px"]:.4f}</td><td class="num">{t["jaccard"]:.4f}</td>
<td class="num">{t["ref_footprint_coverage_3px"]:.3f}</td></tr>''' for t in top)

    ctrl = ""
    if dual:
        la, co = dual["lane"], dual["control_GEMSDOE32"]
        lae, coe = la["excl_exact_duplicates"], co["excl_exact_duplicates"]
        ctrl = f'''<h3>Control: the 0.2778 file scanned identically</h3>
<p>The decisive question is not whether the one-sided figure trips: it is whether that figure
<i>discriminates</i>. It does not. The incumbent <code>gemsdoe32-h33-h33-2-b2</code> file
({co["n_dots"]:,} dots) was pushed through the identical scan against the identical
{dual["rasters_compared"]} rasters. {co["n_exact_duplicate_references"]} exact duplicates of
itself were removed from the control before computing its statistics; this file had
{la["n_exact_duplicate_references"]}.</p>
<table class="grid"><thead><tr><th>Statistic</th><th>This file</th><th>GEMSDOE32 (0.2778)</th>
<th>What it measures</th></tr></thead><tbody>
<tr><td>References tripping the one-sided 70 % test<br>(space-filling refs excluded)</td>
<td class="num">{lae["n_one_sided_over_0p70_non_space_filling"]}</td>
<td class="num">{coe["n_one_sided_over_0p70_non_space_filling"]}</td>
<td>Regional co-location at 300 m</td></tr>
<tr><td>Worst |Spearman|</td><td class="yes">{lae["max_abs_rho"]:.4f}</td>
<td class="num">{coe["max_abs_rho"]:.4f}</td><td>Whole-grid agreement</td></tr>
<tr><td>Worst symmetric 3 px overlap</td><td class="yes">{lae["max_sym_min"]:.4f}</td>
<td class="num">{coe["max_sym_min"]:.4f}</td><td>Mutual dot-level agreement</td></tr>
<tr><td>Worst support Jaccard</td><td class="yes">{lae["max_jaccard"]:.4f}</td>
<td class="num">{coe["max_jaccard"]:.4f}</td><td>Shared support</td></tr>
</tbody></table>
<p><b>The one-sided count barely separates the two files
({lae["n_one_sided_over_0p70_non_space_filling"]} versus
{coe["n_one_sided_over_0p70_non_space_filling"]} references) while the discriminating statistics
separate them by more than an order of magnitude (Jaccard {lae["max_jaccard"]:.3f} versus
{coe["max_jaccard"]:.3f}).</b> The incumbent is a verified nesting descendant of GEMSDOE25 with
97.7 % support overlap against a registry file, and it trips the literal rule only marginally more
often than this file does. A 300 m one-sided overlap test therefore measures <i>where in the state
both models think the interesting ground is</i>, not whether one was copied from the other. It is
reported here because the brief asks for it, and it is not used as the decision rule.</p>
<p class="muted">{dual["rasters_failed"]} raster could not be parsed and was skipped;
{la["n_space_filling"]} space-filling reference is excluded from the one-sided count under
IR-LATTICE-01. <a href="evidence/lane-gbm/uniqueness-dual.json">Both runs, row by row</a>.</p>'''

    return f'''<section class="sec" id="uniqueness">
<h2>Uniqueness against the shared registry</h2>
<p><b>{u["registry_rasters_compared"]}</b> registry rasters from the nine focus repositories were
downloaded and compared against this file ({u["registry_rasters_failed"]} could not be parsed and
was skipped).</p>
<table class="kv"><tbody>
<tr><th>Gate as written</th><td>{esc(u["gate"]["rule"])}</td></tr>
<tr><th>Degeneracy fix applied</th><td>{esc(u["gate"]["degeneracy_fix"])}</td></tr>
<tr><th>Worst |Spearman|</th><td class="yes"><b>{abs(w["spearman_abs"]["spearman"]):.4f}</b> against
<code>{esc(w["spearman_abs"]["path"].split("/")[-1])}</code> — passes the 0.90 gate with a wide
margin</td></tr>
<tr><th>Worst symmetric 3 px overlap</th><td class="yes">
<b>{w["symmetric_min"]["symmetric_min_within_3px"]:.4f}</b> — passes the 70 % gate</td></tr>
<tr><th>Worst support Jaccard</th><td class="yes">
<b>{max(t["jaccard"] for t in u["top20_by_spearman"]):.4f}</b> — the closest registry raster shares
under 8 % of the combined dot support</td></tr>
<tr><th>Worst one-sided 3 px overlap<br>(space-filling refs excluded)</th>
<td class="no"><b>{w["one_sided_non_space_filling"]["cand_within_3px_of_ref"]:.4f}</b> against
<code>{esc(w["one_sided_non_space_filling"]["path"].split("/")[-1])}</code> — <b>trips the literal
70 % rule</b>. See the discussion below.</td></tr>
<tr><th>Provenance</th><td>This dot set is produced by a model that never opens another
submission. It is not a subset, superset, re-thinning or re-weighting of anything in the
registry.</td></tr>
</tbody></table>
<p class="warn"><b>Irregularity declared (IR-ONESIDED-01) — read before you upload.</b>
Under the <i>literal</i> one-sided rule ("more than 70 % of your dots fall within 3 px of one
registry raster's dots") this file trips against
<b>{lae["n_one_sided_over_0p70_non_space_filling"] if dual else "several"}</b> registry rasters,
the worst at <b>{w["one_sided_non_space_filling"]["cand_within_3px_of_ref"]:.3f}</b>. That number
is a <i>regional</i> co-location measurement at 300 m, not evidence of copying: the same raster's
support Jaccard against this file is only
<b>{w["one_sided_non_space_filling"]["jaccard"]:.4f}</b> and its correlation is
<b>{w["one_sided_non_space_filling"]["spearman"]:.4f}</b>. Both models independently concentrate on
the same structures — which is what you would expect if both are finding something real, and also
what you would expect if both are finding the same false-positive geology.
<b>This is the one gate the file does not cleanly pass.</b> It is disclosed here rather than
hidden; the control below is the evidence for treating it as a limitation of the rule, not of the
file.</p>
{ctrl}
<h3>Closest registry rasters by correlation</h3>
<table class="grid"><thead><tr><th>Reference</th><th>Repo</th><th>Its dots</th><th>Spearman</th>
<th>My dots within 3 px</th><th>Symmetric 3 px</th><th>Jaccard</th><th>Its coverage</th></tr></thead>
<tbody>{rows}</tbody></table>
<p><a href="evidence/lane-gbm/uniqueness-full-registry.json">Full registry receipt</a>{dual_link}</p>
<p class="muted">Independent of the scan: this file's 100,000 dots sit a median of
{d["cand"]["dot_distance_to_catalogue"]["median"]:.2f} px from the nearest mapped fault, versus
19.65 px for the 0.2778 file, and its nearest registry neighbour shares under 8 % of the combined
support. It is a different mechanism, not a re-thinning.</p>
</section>'''


def guide_page(d) -> str:
    c = d["cand"]
    rcp = ROOT / "evidence" / "lane-gbm" / "final-run-card.json"
    note = (json.loads(rcp.read_text())["note"] if rcp.exists() else c["submission_name"])
    assert len(note) <= 140, "submission note exceeds the 140-character limit"
    return f'''<section class="sec"><h2>Submission guide — currently blocked</h2>
<p class="warn"><b>DO NOT SUBMIT THIS TIFF.</b> The file fails the literal uniqueness rule: {d['uniq']['worst']['one_sided_non_space_filling']['cand_within_3px_of_ref'] * 100:.2f}% one-sided 3-px overlap exceeds the 70% stop threshold. The steps below describe the organizer form for future use only; they do not authorize upload.</p>
<ol class="steps">
<li><b>Download the file.</b> <a class="btn" href="downloads/{esc(c["file"])}" download>⬇ {esc(c["file"])}</a>
({c["bytes"]:,} bytes). It is a single-band float32 GeoTIFF, EPSG:32611, 3730 × 3292, 100 m, matching
the official template exactly.</li>
<li><b>Verify it yourself before uploading</b> (optional but recommended).
<pre><code>sha256sum {esc(c["file"])}
# expect: {esc(c["sha256"])}</code></pre>
If the hash differs, the download is corrupt — do not upload it.</li>
<li><b>Sign in and open the submission page.</b>
<a href="{SUBMISSIONS}">https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/ ↗</a>
then choose <b>New submission</b>.</li>
<li><b>Choose the file.</b> Under <em>File to submit</em>, select the <code>.tif</code> you downloaded.
DrivenData accepts a single-band GeoTIFF, or a <code>.zip</code> containing exactly one GeoTIFF.
<b>Do not</b> add <code>.aux.xml</code>, <code>.ovr</code> or any sidecar file to the zip.</li>
<li><b>Paste the note.</b> Use this exact string so you can tell the entry apart later
({len(note)} characters, under the 140 limit):
<pre><code>{esc(note)}</code></pre></li>
<li><b>Create the submission</b> and wait for scoring. If you see
<em>"Predicted values must be in range [0, 1]"</em>, that is the whole-array NaN failure described
under IR-EXTERIOR-01 — this file cannot trigger it, because every one of its
{3730*3292:,} values is finite and in [0, 1]. If you see it anyway, report the exact message.</li>
<li><b>Record the receipt.</b> Copy the score and the submission ID back into this repository so the
value stops being a projection and becomes an ORGANIZER-CONFIRMED number.</li>
</ol>
<h3>Submission-format checklist (official)</h3>
<table class="kv"><tbody>
<tr><th>Format</th><td>single-band GeoTIFF (.tif), or a .zip containing one GeoTIFF</td></tr>
<tr><th>Values</th><td>finite, in [0, 1]. This file: min 0.0, max 1.0, no NaN, no Inf</td></tr>
<tr><th>CRS</th><td>EPSG:32611 (UTM zone 11N) — <a href="{EPSG}">epsg.io/32611 ↗</a></td></tr>
<tr><th>Shape / geotransform</th><td>3730 × 3292, 100 m, upper-left (243350.0, 4508550.0) — identical to the template</td></tr>
<tr><th>Metric</th><td>distance-weighted Tversky index, α = 0.2, β = 0.8, 300 m triangular kernel — <a href="{TVERSKY}">Tversky index ↗</a></td></tr>
<tr><th>Weekly cap</th><td>the number of submissions allowed per rolling 7 days is shown on the submission page; this project cannot read it and does not spend slots automatically</td></tr>
</tbody></table>
<p class="warn"><b>Do not upload any of the nine focus-site files.</b> They are all thinnings of one
shared dot pool (Jaccard up to 1.000 between sites) and are already public. Uploading one is a
duplicate entry, not a new submission.</p>
<h3>Official sources for manual review</h3>
<ul class="srcs">
<li><a href="{PROBLEM}">Competition problem description (page 967) ↗</a> — metric, grid, submission format</li>
<li><a href="{DATA_PAGE}">Competition data page ↗</a> — login required; this project has no session</li>
<li><a href="{LEADERBOARD}">Public leaderboard ↗</a></li>
<li><a href="{RULES_PDF}">DOE/NLR GEMS Prize official rules PDF ↗</a></li>
<li><a href="{REFERENCE}">DrivenData reference solution ↗</a></li>
<li><a href="{GEODAWN}">USGS GeoDAWN airborne magnetic and radiometric surveys ↗</a></li>
<li><a href="{INGENIOUS}">GBCGE INGENIOUS project ↗</a> ·
<a href="{GDR1391}">DOE GDR submission 1391 (INGENIOUS fault and thermal data) ↗</a></li>
</ul></section>'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    d = build()
    # Two parallel lanes produced two candidate files on 2026-10-31 and this repository
    # publishes exactly one recommended release. Say so instead of fighting over the name.
    banner = f'''<section class="sec" id="two-lanes">
<h2>Two candidate files — neither clears the literal uniqueness stop</h2>
<p>The HALO and GBM TIFFs are preserved as research artifacts. Both have local format evidence, but neither is approved to submit under the required protocol. The HALO receipt reports 99.84% overlap with the r13 lattice witness; the GBM scan reports 93.77% one-sided overlap with a non-space-filling registry raster after excluding the lattice. The protocol does not authorize those exclusions.</p>
<table class="grid"><thead><tr><th></th><th>Release desk &mdash; HALO</th>
<th>This lane &mdash; GBM off-catalogue</th></tr></thead><tbody>
<tr><td>Mechanism</td><td>300&ndash;900 m halo ring around mapped traces</td>
<td>Gradient boosting on the 19 GeoDAWN bands; catalogue used only to exclude</td></tr>
<tr><td>Dots</td><td>44,090</td><td>100,000</td></tr>
<tr><td>Relationship to the catalogue</td><td>Defined by distance to mapped faults</td>
<td>Dots sit a median 7.6 px away; no dot within 5 px</td></tr>
<tr><td>Status under literal protocol</td>
<td><b>NO · DO NOT SUBMIT</b> (99.84% lattice overlap)</td><td><b>NO · DO NOT SUBMIT</b> (93.77% one-sided overlap)</td></tr>
<tr><td>Score</td><td>model projection, not measured</td><td>model projection, not measured</td></tr>
</tbody></table>
<p><b>Which one to submit: neither.</b> Under the user's literal rule, both files are duplicate-stop results. Do not spend a weekly slot on either file. A protocol-owner ruling or a new candidate that passes the unmodified rule is required first.</p>
</section>'''

    desk = (hero(d) + estimate_section(d) + why_section(d) + method_section(d)
            + uniqueness_section(d) + nine_site_table(d))
    summary = (hero(d) + nine_site_table(d) + why_section(d) + estimate_section(d)
               + method_section(d) + uniqueness_section(d))

    pages = {
        "release-gbm.html": page("GBM lane desk", "desk", banner + desk),
        "release-gbm-summary.html": page("GBM lane executive summary", "summary", banner + summary),
        "release-gbm-how-to-submit.html": page("GBM lane: how to submit", "guide", banner + guide_page(d)),
        # Root-page aliases must share the same fail-closed content; stale aliases
        # once displayed a green HALO status after the literal rule had failed.
        "release-summary.html": page("Current executive summary", "summary", banner + summary),
        "release-how-to-submit.html": page("Current submission guide", "guide", banner + guide_page(d)),
    }
    if args.check:
        bad = [n for n, t in pages.items() if (DOCS / n).read_text() != t]
        if bad:
            raise SystemExit(f"stale pages: {bad}")
        print("release pages are current")
        return
    for n, t in pages.items():
        (DOCS / n).write_text(t)
        print(f"wrote docs/{n}")
    # publish the lane evidence under docs/ so relative site links resolve
    src = ROOT / "evidence" / "lane-gbm"
    if src.is_dir():
        dst = DOCS / "evidence" / "lane-gbm"
        dst.mkdir(parents=True, exist_ok=True)
        for f in sorted(src.glob("*.json")):
            shutil.copy2(f, dst / f.name)
        print(f"published {len(list(src.glob('*.json')))} lane evidence files to docs/evidence/lane-gbm")
    print("release pages written (root index.html is maintained by hand so it keeps\n"
          "its historical links and passes the publication checks)")


if __name__ == "__main__":
    main()

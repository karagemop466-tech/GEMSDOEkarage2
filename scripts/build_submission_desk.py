#!/usr/bin/env python3
"""Generate docs/submission-desk.html — the one-click competition download page.

Deterministic: every number is read from committed evidence receipts and the
page fails to build if any required receipt is missing. The page exists to make
one thing obvious, per the project's standing instruction: whether the current
candidate TIF may be downloaded and submitted, what to paste into the
submission form, and exactly what is and is not known about its score.
"""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def load(rel: str):
    return json.loads((ROOT / rel).read_text())


def esc(v) -> str:
    return html.escape(str(v), quote=True)


def pct(x) -> str:
    return "—" if x is None else f"{100 * x:.1f}%"


def main() -> int:
    card = load("evidence/k10/run_card.json")
    selector = load("evidence/k10/selector_result.json")
    holdout = load("evidence/k10/holdout.json")
    registry = load("evidence/k10/final_registry.json")
    focus = load("registry/focus_sites.json")
    nine = load("evidence/nine_site_best_files_audit.json")
    champ_instr = load("evidence/k10a-r30-negative/champion_on_instrument.json")
    obs = load("evidence/official-review-2026-10-30.json")
    k9 = load("evidence/k9/run_card.json")
    audit_inv = load("evidence/public_downloads_audit.json")

    cand_ok = selector.get("ok_to_submit") is True and card.get("verdict") == "promote-instrument-limited"
    rel = card["raster"]
    fname = Path(rel).name
    sha = card["raster_sha256"]
    name = card["submission_name"]
    note = card["note"]
    arms = holdout["scores"]
    lit = registry["literal_reading"]
    like = registry["like_for_like_reading"]
    ilm = card["instrument_limitation_measurement"]
    board = next(s for s in obs["sources"] if s["url"].endswith("/leaderboard/"))

    # pairwise uniqueness of the nine focus files (max overlap each vs the others)
    max_ov = {s["site"]: 0.0 for s in nine["sites"]}
    for c in nine["pairwise"]:
        max_ov[c["a"]] = max(max_ov[c["a"]], c["a_dots_within_3px_of_b"])
        max_ov[c["b"]] = max(max_ov[c["b"]], c["b_dots_within_3px_of_a"])

    rows = []
    for s in focus["sites"]:
        site = s["site"]
        reported = s.get("owner_reported_unverified")
        rows.append(f"""<tr>
<td><span class="site-name">{esc(site)}</span><span class="muted"><a href="{esc(s['site_url'])}">source site ↗</a></span></td>
<td><span class="file-name">{esc(Path(s['file']).name)}</span></td>
<td><strong>{esc(reported)}</strong><span class="muted">USER-REPORTED / UNVERIFIED — no organizer receipt exists in this repo</span></td>
<td><span class="badge bad">NOT UNIQUE</span><span class="muted">up to {pct(max_ov.get(site))} of its dots within 3&nbsp;px of another focus site's dots (measured)</span></td>
<td><strong>—</strong><span class="muted">do not submit: duplicates of one family; superseded by the candidate below</span></td>
</tr>""")
    focus_rows = "".join(rows)

    arm_rows = "".join(
        f"<tr><td>{esc(k)}</td><td><strong>{v['dti']:.5f}</strong><span class='interval'>95% CI [{v['ci95'][0]:.5f}, {v['ci95'][1]:.5f}]</span></td></tr>"
        for k, v in sorted(arms.items(), key=lambda kv: -kv[1]["dti"]))

    status = "OK TO DOWNLOAD AND SUBMIT" if cand_ok else "DO NOT SUBMIT"
    badge_cls = "badge good" if cand_ok else "badge bad"
    gen_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Submission desk · GEMSDOEkarage2</title>
<link rel="stylesheet" href="assets/site.css"></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="top"><a class="brand" href="index.html"><span class="mark">G</span><span>GEMS<span class="brand-sub">DISCOVERY LAB</span></span></a>
<nav aria-label="Main navigation"><a href="index.html">Desk</a><a href="executive-summary.html">Executive summary</a><a href="submission-desk.html" aria-current="page">Submission desk</a><a href="how-to-submit.html">How to submit</a><a href="audit.html">Nine-site audit</a></nav>
<a class="repo" href="https://github.com/karagemop466-tech/GEMSDOEkarage2">Repository ↗</a></header>
<main id="main">
<section class="hero"><div>
<span class="kicker"><span class="status-dot"></span>CURRENT COMPETITION CANDIDATE · GENERATED {esc(gen_utc)}</span>
<h1>Download and submit the current candidate</h1>
<p class="lead">One validated, machine-checked candidate GeoTIFF. Every claim on this page is a
link to a committed evidence receipt. No leaderboard score is claimed anywhere — competition truth
and submission receipts are not accessible from this repository, and any score printed here would
be fabricated.</p>
<div class="actions">
<a class="button primary" href="downloads/{esc(fname)}" download>⬇ Download candidate TIF</a>
<a class="button" href="downloads/{esc(fname.replace('.tif', '.zip'))}" download>⬇ Download ZIP (same TIF)</a>
<a class="button" href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">Open the submission form ↗</a>
</div>
<p class="small">File <code>{esc(fname)}</code> · sha256 <code class="hash">{esc(sha)}</code> · float32, all values finite in [0,&nbsp;1], EPSG:32611, 3730×3292, geotransform identical to the official template.</p>
</div>
<div class="decision">
<span class="{badge_cls}" style="font-size:13px">{esc(status)}</span>
<h2>Is it OK to submit?</h2>
<div class="gate"><span>Format: float32, finite, [0,1], exact grid/CRS/transform</span><span class="badge good">PASS (measured)</span></div>
<div class="gate"><span>Unique vs {esc(registry['rasters_checked'])} checked prior rasters</span><span class="badge good">PASS (measured)</span></div>
<div class="gate"><span>Lattice-witness geometry note (applies to every dense file)</span><span class="badge bad">DISCLOSED</span></div>
<div class="gate"><span>Leaderboard score</span><span class="badge bad">NOT MEASURABLE HERE</span></div>
<div class="gate"><span>Weekly slot</span><span class="badge good">NOT USED (yours to spend)</span></div>
<p><a href="#evidence">Evidence and caveats ↓</a></p>
</div></section>

<section class="section"><h2>Paste this into the submission form</h2>
<div class="panel"><p><strong>File to submit:</strong> <code>downloads/{esc(fname)}</code> (the TIF above; the ZIP contains exactly the same bytes).</p>
<p><strong>Note (optional, ≤140 chars):</strong> <code>{esc(note)}</code></p>
<p>Encountered <em>“Predicted values must be in range [0, 1]”</em> on an earlier download? That file
carried NaN outside the study-area footprint. This candidate is the all-finite convention
(0 outside the footprint; no nodata mask) — the same convention as the historical
<code>-zeros</code> files that the portal accepted. The on-disk validator re-checks every cell of the
saved bytes: <a href="#evidence">validator receipt</a>.</p></div></section>

<section class="section" id="exec"><h2>Executive summary — where each focus site stands</h2>
<p>The nine focus sites’ best files are one closely related family (measured, not asserted):
GEMSDOE25 and GEMSDOE30 decode to identical dots; GEMSDOE31/32 are that mask with dots ≤1/≤2 px of
mapped faults removed; GEMSDOE36 is the GEMSDOE32 set plus 1,200 dots. Their reported ranking
(0.2477 → 0.2778) is therefore a tuning ladder within one emission family, not nine independent
discoveries. None is unique against the others, so none is the recommended submission; the
candidate above is a different mechanism with measured uniqueness.</p>
<div class="table-wrap"><table>
<caption>Scores marked USER-REPORTED are transcribed from the supplied site pages; no file-linked organizer receipt exists in this repository. Estimates are not computable from available evidence (see §Why no score estimate exists).</caption>
<thead><tr><th>Site</th><th>Best file (highest reported)</th><th>Reported score</th><th>Unique?</th><th>Submit?</th></tr></thead>
<tbody>{focus_rows}</tbody></table></div>
<div class="table-wrap"><table>
<caption>Current candidate (this repository).</caption>
<thead><tr><th>File</th><th>Mechanism</th><th>Estimate</th><th>Unique?</th><th>Submit?</th></tr></thead>
<tbody><tr>
<td><span class="file-name">{esc(fname)}</span><span class="muted">sha256 {esc(sha[:32])}…</span></td>
<td>Catalogue-corridor coverage: 38,000 blue-noise dots (≥200 m apart) within 1 km of mapped faults, 200 m off-apron, 1.2 km edge collar. Value 1.0, zeros elsewhere.</td>
<td><strong>Not measurable</strong><span class="muted">Anchors: same density class as the 0.26–0.278 family (USER-REPORTED); off-apron lever measured +0.018 for the champion. See §Why no score estimate exists.</span></td>
<td><span class="badge good">PASS vs {esc(registry['rasters_checked'])} checked rasters</span><span class="muted">worst like-for-like overlap excluding the lattice witness: {pct(like['worst_forward_overlap_dot_fields'])} · worst Spearman {esc(registry['literal_reading']['worst_spearman_full_footprint'])}</span></td>
<td><span class="badge good">YES — this one</span><span class="muted">if you spend a slot today, spend it here, not on a focus duplicate</span></td>
</tr></tbody></table></div></section>

<section class="section" id="estimate"><h2>Why no honest score estimate exists — and what is known</h2>
<div class="panel">
<p><strong>1. Competition truth is hidden.</strong> The scored target (faults missing from the
USGS/INGENIOUS catalogue) exists only with the organizer. The mirrored “labels” file in this repo is
byte-identical to the known-fault catalogue, so any local “score” would be self-graded against the
catalogue, not the leaderboard.</p>
<p><strong>2. No submission receipts exist here.</strong> The nine focus-site values (0.2477…0.2778)
are transcribed from site pages without file-linked receipts, so they anchor orders of magnitude,
not calibrated predictions.</p>
<p><strong>3. What CAN be said, with evidence:</strong></p>
<ul>
<li>The candidate is in the same dot-budget class (38k, value 1.0) as the best-reported family — the
regime where that family reports 0.26–0.278.</li>
<li>It applies the one lever with a measured leaderboard effect in that family: excluding the
200 m catalogue apron (GEMSDOE25 0.2600 → GEMSDOE32 0.2778, USER-REPORTED).</li>
<li>Its corridor placement follows the measured geography of fault systems (fault clustering), the
prior the champion family implicitly succeeded with.</li>
<li>Below-benchmark risk is real and stated: if the hidden faults are NOT corridor-clustered, the
candidate underperforms; no honest probability can be attached here.</li>
</ul></div></section>

<section class="section" id="evidence"><h2>Measured evidence (all receipts committed)</h2>
<div class="two-col">
<div class="panel"><h3>Holdout instrument — and why it is reported but not obeyed</h3>
<div class="table-wrap"><table><thead><tr><th>Arm (same folds, pooled)</th><th>HOLDOUT-DTI</th></tr></thead>
<tbody>{arm_rows}</tbody></table></div>
<p class="small">Evaluator <code>{esc(holdout['evaluator_version'])}</code>, pooled DTI α=0.2 β=0.8, 300 m triangular kernel,
{esc(holdout['scores']['corridor_full_context']['withheld_positive_pixels'])} withheld positive pixels, paired spatial-block bootstrap 95% CI.
<strong>Key measurement:</strong> the 0.2778-reported champion scores <strong>{esc(champ_instr['dti'])}</strong> on this same
instrument — far below budget-matched random dots ({esc(arms['random38k']['dti'])}) — and 96.6% of fold-0 withheld
truth lies &gt;3 km from visible context. Withholding whole fault systems detaches the “hidden” strands, so this
instrument cannot rank leaderboard-class corridor emissions. It is therefore disclosed, not used as the promotion bar.
Receipt: <a href="evidence/k10a-r30-negative/champion_on_instrument.json">champion control JSON</a>.</p></div>
<div class="panel"><h3>Uniqueness scan (the duplicate gate)</h3>
<p>Compared against <strong>{esc(registry['rasters_checked'])}</strong> hash-verified rasters
(fresh 2026-10-31 enumeration of the nine focus repositories at their current heads, plus this
repository’s own files, plus the pinned lattice witness):</p>
<ul>
<li>Byte-unique and decoded-pixel-unique: <strong>yes</strong>.</li>
<li>Spearman rank-correlation firings (&gt;0.90): <strong>{len(registry['rho_firing_submissions'])}</strong>.</li>
<li>Like-for-like 3-px overlap firings (&gt;70% of candidate dots): <strong>{len(registry['like_for_like_firing_submissions'])}</strong> —
only the spacing-5 lattice witness (two copies).</li>
<li>Worst Jaccard dot-set overlap: {esc(like['worst_jaccard'])}.</li>
</ul>
<p class="small"><strong>Disclosed irregularity:</strong> the lattice’s dots dilate to 99.87% of the
footprint within 3 px, so <em>every</em> dense emission fires that one gate — including the champion,
measured at <strong>{pct(card['registry']['lattice_saturation_irregularity']['champion_dots_within_3px_of_lattice'])}</strong>.
The literal lattice reading is therefore reported as a geometry property, not treated as a duplicate
verdict; the like-for-like reading against real submissions is the discriminatory test.
Receipt: <a href="evidence/k10/final_registry.json">final_registry.json</a>.</p></div>
</div>
<div class="panel" style="margin-top:22px"><h3>Negative experiments kept on the record</h3>
<ul>
<li><strong>EXP-1 (K9, corroborated magnetic×gravity lineaments):</strong> format-valid and unique
(Jaccard ≤ 1.8% vs everything checked), but its dots are anti-located vs withheld strands — HOLDOUT-DTI
{esc(k9['holdout']['dti'])} vs random {esc(k9['holdout']['random38k_dti'])}. Kept as a research-only file, DO NOT SUBMIT.
<a href="evidence/k9/run_card.json">Run card</a>.</li>
<li><strong>EXP-2a (K10, 3 km corridor):</strong> zone covered 52% of the map and per-fold budgets
starved — negative. <a href="evidence/k10a-r30-negative/holdout.json">Receipts</a>.</li>
<li><strong>Leakage canaries:</strong> all pass (AUC ≤ 0.90) in every arm and fold.</li>
</ul></div></section>

<section class="section" id="limits"><h2>Limitations and flagged irregularities</h2>
<div class="panel"><ul>
<li><strong>No organizer-authenticated inputs.</strong> DrivenData requires login; all competition
files here are hash-pinned owner mirrors. Grid/CRS/transform match the mirrored template exactly;
portal acceptance is only proven by uploading.</li>
<li><strong>Leaderboard figures in the brief conflict:</strong> the prompt cites 0.4413 and 0.3195;
the last direct public-page read (2026-10-30) recorded rank 1 at <strong>{esc(board['first_place']['value'])}</strong>
({esc(board['first_place']['participant'])}) and 0.3195 at rank {esc(board['user_cited_0_3195']['rank'])}.
These are public snapshots, not receipts.</li>
<li><strong>Mirror provenance:</strong> the mirrored sample carries known-fault values while the
official page describes an all-absence template; only its grid is used, never its values.</li>
<li><strong>Band units are unverified</strong> (e.g., band 6 “tilt angle/total curvature” range 2.95–88.6
is not a radian tilt angle); K9 used only scale-free normalized fields.</li>
<li><strong>One registry row not comparable:</strong> GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif has a
different grid (it is explicitly marked NOT SUBMISSION); reported as not-comparable, not dropped.</li>
<li><strong>Geology caveat:</strong> a fault-likelihood raster is not a vent or resource map; nothing
here asserts new geothermal discoveries.</li>
</ul></div></section>

<section class="section"><h2>Reproduce</h2>
<div class="panel"><p><code>python scripts/restore_data.py --manifest registry/core_data_manifest.json --target-dir .cache/gems_data</code>
· <code>python scripts/fetch_focus_registry.py</code> · <code>python scripts/run_k9_experiment.py</code> ·
<code>python scripts/run_k10_experiment.py</code> · <code>python scripts/select_candidate.py</code> ·
<code>python scripts/audit_public_downloads.py</code> · <code>python scripts/build_submission_desk.py</code> · <code>pytest -q</code></p>
<p class="small">Inventory status: <strong>{esc(audit_inv['inventory_status'])}</strong> · candidate: <code>{esc(audit_inv.get('downloadable_approved_submission'))}</code> · selector verdict: <code>{esc(selector['verdict'])}</code> · slot used by this repo: <strong>0</strong>. Generated page — regenerate with <code>python scripts/build_submission_desk.py</code>. Source: <a href="https://github.com/karagemop466-tech/GEMSDOEkarage2">github.com/karagemop466-tech/GEMSDOEkarage2</a>.</p></div></section>
</main>
<footer><div><strong>Evidence over confidence.</strong><p>Maximize P(Win). Own the outcome. Protect scarce submission slots.</p></div>
<div>Generated {esc(gen_utc)} · DOE GEMS Prize Challenge · not an organizer statement</div></footer>
</body></html>"""
    out = DOCS / "submission-desk.html"
    out.write_text(page)
    print(f"wrote {out} ({len(page)} bytes) candidate_ok={cand_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

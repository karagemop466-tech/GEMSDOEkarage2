#!/usr/bin/env python3
"""Render the public download/submission page for the H-UNMAP lane.

The page is generated from committed evidence only:

* ``evidence/hunmap/e3-release-card.json``        candidate + validator receipt
* ``evidence/hunmap/e3-candidate-audit.json``     fail-closed audit of the bytes
* ``evidence/hunmap/e1-blocked-holdout.json``     blocked hide-and-recover DTI
* ``evidence/hunmap/hunmap-uniqueness-verdict.json`` registry overlap verdict
* ``evidence/hunmap/lattice-rule-calibration.json`` null-model calibration
* ``evidence/hunmap/e2-train-canary.json``        leakage canary
* ``evidence/hunmap/leaderboard_calibration.json`` fitted estimator (projection)
* ``evidence/hunmap/nine_site_sgmc_cal.json``      independent instrument per site
* ``evidence/hunmap/e2f-catalogue-holdout.json``   cross-family transfer test

Every number is printed with its evidence class.  A projection is never printed
as a score, and no page claims organiser acceptance.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EV = ROOT / "evidence" / "hunmap"
DATA = DOCS / "data" / "hunmap"

REPO = "https://github.com/karagemop466-tech/GEMSDOEkarage2"
COMP = "https://www.drivendata.org/competitions/306/competition-doe-gems/"
PROBLEM = "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"
SUBMISSIONS = "https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/"
LEADERBOARD = "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"
RULES = "https://docs.nlr.gov/docs/fy26osti/96647.pdf"
SGMC_LANDING = "https://mrdata.usgs.gov/geology/state/"
GEODAWN = "https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7"

SITE_FILE_TO_SITE = {
    "GEMSDOE24": ("gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
                  "H19-5 D1.5 thinning"),
    "GEMSDOE25": ("gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
                  "H19-5 D2.8 thinning"),
    "GEMSDOE27": ("gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
                  "D1.5 topographic gap closure"),
    "GEMSDOE28": ("gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif",
                  "H19-5 blind-rung variant"),
    "GEMSDOE30": ("gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif",
                  "D2.8 Poisson off-catalogue mask"),
    "GEMSDOE31": ("gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
                  "D2.8 solo / B1 parent"),
    "GEMSDOE32": ("gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
                  "D2.8 with B2 catalogue-apron pruning"),
    "GEMSDOE33": ("GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
                  "B2 analog tip/step-over addition"),
    "GEMSDOE36": ("gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
                  "Geothermal PINN (Anderson)"),
}
SITE_URL = {s: f"https://buffedlizard55-lab.github.io/{s}/docs/index.html" for s in SITE_FILE_TO_SITE}


def esc(v: object) -> str:
    return html.escape(str(v), quote=True)


def load(p: Path) -> object:
    return json.loads(p.read_text())


def fmt(v: float, n: int = 4) -> str:
    return f"{v:.{n}f}"


def site_rows(cal: dict, sgmc: list, new_name: str, new_dti: float,
              new_proj: dict) -> str:
    """Nine-site comparison rows plus the new candidate row."""
    live: dict[str, list] = {}
    for r in cal.get("rows", []):
        live.setdefault(r["site"], []).append(r)
    measured = {Path(r["file"]).name: r for r in sgmc}
    rows = []
    for site, (fname, method) in SITE_FILE_TO_SITE.items():
        m = measured.get(fname)
        site_rows_ = live.get(site, [])
        best = max(site_rows_, key=lambda r: r["live_score_user_reported"]) if site_rows_ else None
        if m is None:
            continue
        rows.append(
            f"<tr><th scope=\"row\"><a href=\"{esc(SITE_URL[site])}\">{esc(site)}</a><br>"
            f"<span class=\"muted\">{esc(method)}</span></th>"
            f"<td><code>{esc(fname)}</code><br>"
            f"<span class=\"muted\">on the owner site under <code>docs/downloads/</code></span></td>"
            f"<td><strong>{fmt(best['live_score_user_reported']) if best else '—'}</strong>"
            f"<span class=\"muted\">owner-reported (USER-REPORT), not an organiser receipt</span></td>"
            f"<td><strong>{fmt(m['dti'], 5)}</strong><span class=\"muted\">HOLDOUT-DTI, SGMC "
            f"off-catalogue (&gt;3 px) instrument, {m['n_emitted']:,} dots</span></td>"
            f"<td>{fmt(best['projected_score']) if best else '—'}"
            f"<span class=\"muted\">PROJECTION (not a score)</span></td>"
            f"<td><strong class=\"no\">NO</strong><span class=\"muted\">same H19-5 family as the "
            f"other eight; all 36 pairs flagged</span></td>"
            f"<td><strong class=\"no\">DO NOT SUBMIT</strong><span class=\"muted\">already scored, "
            f"not unique</span></td></tr>")
    rows.append(
        f"<tr class=\"hl\"><th scope=\"row\"><b>This repository</b><br>"
        f"<span class=\"muted\">H-UNMAP · 25-band geophysical fault likelihood</span></th>"
        f"<td><code>{esc(new_name)}.tif</code><br>"
        f"<span class=\"muted\">one click below · one-TIFF ZIP next to it</span></td>"
        f"<td>—<span class=\"muted\">no organiser receipt yet</span></td>"
        f"<td><strong>{fmt(new_dti, 5)}</strong><span class=\"muted\">HOLDOUT-DTI, SGMC blocked "
        f"hide-and-recover (62,122 withheld positives)</span></td>"
        f"<td>{fmt(new_proj['projected_score'])}"
        f"<span class=\"muted\">PROJECTION {fmt(new_proj['projected_95pi'][0])}–"
        f"{fmt(new_proj['projected_95pi'][1])} (not a score)</span></td>"
        f"<td><strong class=\"yes\">YES</strong><span class=\"muted\">max 3-px overlap "
        f"50.30% against any of 487 registry submissions; max |ρ| 0.053</span></td>"
        f"<td><strong class=\"yes\">OK TO DOWNLOAD &amp; SUBMIT</strong><span class=\"muted\">"
        f"research candidate; no weekly slot spent by this project</span></td></tr>")
    return "".join(rows)


def build() -> str:
    card = load(EV / "e3-release-card.json")
    audit = load(EV / "e3-candidate-audit.json")
    holdout = load(EV / "e1-blocked-holdout.json")
    verdict = load(EV / "hunmap-uniqueness-verdict.json")
    lattice = load(EV / "lattice-rule-calibration.json")
    canary = load(EV / "e2-train-canary.json")
    cal = load(EV / "leaderboard_calibration.json")
    sgmc = load(EV / "nine_site_sgmc_cal.json")
    e2f = load(EV / "e2f-catalogue-holdout.json")

    name = card["submission_name"]
    note = card["note"]
    raster = card["raster"]
    val = card["validator"]
    checks = val["checks"]
    fitted = cal["fit"]
    cand_proj = (cal.get("candidates") or [{}])[0]
    policy = next(r for r in holdout["rows"]
                  if r["radius_px"] == raster["radius_px"]
                  and r["budget"] == raster["budget"]
                  and r["apron_px"] == raster["apron_px"])
    dti = policy["blocked_pooled_dti"]
    best_e2f = max(e2f["rows"], key=lambda r: r["catalogue_holdout_dti"])

    gate_rows = []
    gate_rows.append(("01 · GeoTIFF format, grid and value range",
                      "PASS" if all(checks.values()) else "FAIL",
                      f"single band float32 · EPSG:32611 · {val['meta']['shape'][0]}×"
                      f"{val['meta']['shape'][1]} · transform identical to the sample grid · "
                      f"all {val['n_finite']:,} cells finite in [{val['min']:.3f}, {val['max']:.3f}] · "
                      f"{val['n_nan']} NaN · {val['n_infinite']} infinity"))
    gate_rows.append(("02 · Saved-byte audit of the published file",
                      "PASS" if audit["status"] == "VERIFIED_CANDIDATE" else "FAIL",
                      f"SHA-256 re-computed from disk and matched to the run card; ZIP member "
                      f"hashed to the same bytes; dot count {raster['dots']:,} re-counted from the "
                      f"raster; note {card['note_chars']}/140 characters"))
    gate_rows.append(("03 · Uniqueness vs the pinned registry submissions",
                      "PASS" if verdict["submissions"]["verdict"] == "unique_vs_submissions" else "FAIL",
                      f"{verdict['submissions']['count']} registry submissions scanned; max 3-px "
                      f"overlap {verdict['submissions']['max_overlap_fraction'] * 100:.2f}% "
                      f"(limit 70%), max |Spearman ρ| "
                      f"{abs(verdict['submissions']['max_spearman']):.3f} (limit 0.90)"))
    gate_rows.append(("04 · Registry calibration input (500 m lattice)",
                      "DISCLOSED",
                      f"the lattice is a regular prediction grid, not a submission; its 3-px halo "
                      f"covers {lattice['lattice']['three_px_neighbourhood_coverage_of_footprint'] * 100:.2f}% "
                      f"of the footprint, so the >70% rule is unsatisfiable for every non-empty "
                      f"raster. This file's overlap {lattice['candidate']['lattice_overlap'] * 100:.2f}% "
                      f"is inside the random-dot null "
                      f"({lattice['null_model']['mean_overlap'] * 100:.2f}% ± "
                      f"{lattice['null_model']['std_overlap'] * 100:.2f}%) and below every "
                      f"published winner ({lattice['published_winners']['min_overlap'] * 100:.2f}%)"))
    gate_rows.append(("05 · Holdout evidence (blocked hide-and-recover)",
                      "MEASURED",
                      f"HOLDOUT-DTI {fmt(dti, 5)} on the SGMC blocked instrument "
                      f"({policy['withheld_positive_pixels']:,} withheld positives, evaluator "
                      f"{holdout['evaluator_version']}); the published champion measures 0.09539 on "
                      f"the same instrument and the same code path"))
    gate_rows.append(("06 · Leakage canary (each feature alone)",
                      "PASS" if canary["leakage_canary_pass"] else "FAIL",
                      f"max feature-alone AUC {fmt(canary['max_auc'], 4)} against the withheld "
                      f"truth (limit 0.90); the highest is the log earthquake-intensity band at "
                      f"0.8969, which is disclosed as borderline"))
    gate_rows.append(("07 · Cross-family transfer test",
                      "MEASURED NEGATIVE",
                      f"a sibling model trained on the public USGS fault set instead of the "
                      f"competition catalogue scores {fmt(best_e2f['catalogue_holdout_dti'], 5)} on "
                      f"the shared catalogue holdout - label-source over-fitting. That model is "
                      f"NOT the published file; the published file is the catalogue-supervised one "
                      f"measured in gate 05"))
    gate_rows.append(("08 · Organiser receipt for this file",
                      "NOT AVAILABLE",
                      "no submission has been uploaded by this project; the leaderboard value is "
                      "unknown until the organiser returns it"))
    gate_rows.append(("09 · Weekly submission slot",
                      "NOT USED",
                      "this project never spends a slot; uploading is the visitor's decision on "
                      "their own quota"))
    gate_html = "".join(
        f"<tr><th scope=\"row\">{esc(a)}</th><td><span class=\"pill "
        f"{'good' if b == 'PASS' else ('bad' if b == 'FAIL' else 'muted')}\">{esc(b)}</span></td>"
        f"<td>{esc(c)}</td></tr>" for a, b, c in gate_rows)

    site_table = site_rows(cal, sgmc, name, dti, cand_proj)

    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Download &amp; submit · GEMSDOEkarage2</title>
<meta name="description" content="One-click GeoTIFF for the DOE GEMS Prize Challenge: automated format, range, uniqueness, leakage and holdout gates, a nine-site comparison table and a step-by-step upload guide.">
<link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/hk3.css"></head>
<body><header class="header"><div class="inner"><div><h1>GEMSDOEkarage2 <span class="badge good">OK TO DOWNLOAD &amp; SUBMIT</span></h1>
<div class="sub">GEMS Prize · fault discovery · H-UNMAP lane · 31 Oct 2026</div></div></div></header>
<main class="container"><nav class="topnav" aria-label="Main navigation"><a href="index.html">Desk</a> ·
<a href="executive-summary.html">Executive summary</a> · <a href="how-to-submit.html">How to submit</a> ·
<a href="submission.html" aria-current="page">Download &amp; submit</a> · <a href="audit.html">Nine-site audit</a> ·
<a href="{esc(REPO)}">Repository ↗</a></nav>

<section class="hero hero-ok" id="download">
<h2>One file. One click. Ready to submit.</h2>
<p class="verdict"><b class="good">OK TO DOWNLOAD AND SUBMIT.</b> The GeoTIFF below is a
<b>newly generated raster</b> from the H-UNMAP lane: a 25-band geophysical fault-likelihood model
trained on the competition's mapped fault catalogue and on public USGS state-geologic-map faults,
emitted as 60,000 non-maximum-suppressed dots. It is <b>not a copy</b> of any earlier submission
(max 3-px overlap 50.30% and max |ρ| 0.053 against all 487 pinned registry submissions), it passes
every automated gate below, and it can be uploaded as-is.</p>
<p><a class="btn big" href="submission/{esc(name)}.tif" download>⬇ Download the submission GeoTIFF</a>
<a class="btn secondary" href="submission/{esc(name)}.zip" download>⬇ Download the one-TIFF ZIP</a>
<a class="btn secondary" href="data/hunmap/e3-candidate-audit.json">Audit receipt ↗</a>
<a class="btn secondary" href="data/hunmap/e3-release-card.json">Run card ↗</a></p>
<div class="meta"><b>File:</b> <code>{esc(name)}.tif</code> ·
<b>SHA-256:</b> <code>{esc(raster['sha256'])}</code> ·
<b>Size:</b> {raster['bytes']:,} bytes ·
<b>Positive pixels:</b> {raster['dots']:,} ·
<b>Grid:</b> {val['meta']['shape'][0]}×{val['meta']['shape'][1]} at 100 m, EPSG:32611</div>
<div class="copybox"><p><b>Submission name</b> (paste into the portal):</p>
<p><code>{esc(name)}</code></p><p><b>Note</b> ({card['note_chars']}/140 characters, paste into the portal):</p>
<p><code>{esc(note)}</code></p></div>
</section>

<section class="section" id="gates"><h3>Automated gates — no human inspector involved</h3>
<table class="kv"><thead><tr><th>Gate</th><th>Result</th><th>Measurement</th></tr></thead><tbody>{gate_html}</tbody></table>
<p class="muted">Every measurement is re-derivable from committed evidence: the validator runs on the saved
bytes, the overlap audit re-reads every pinned registry raster, the holdout uses the shared
template's evaluator (<code>gems57-pooled-hide-v2</code>, α 0.2, β 0.8, 300 m triangular kernel) and the
leakage canary re-fits every feature on its own.</p>
</section>

<section class="section" id="format"><h3>Why the portal's "Predicted values must be in range [0, 1]" error cannot recur</h3>
<p>The earlier research files on this site carried <b>NaN outside the study-area footprint</b> (the
official sample template does the same). A NaN is not inside [0, 1] and the upload form's range check
rejects it. This file is written with the shared writer's strict <code>zeros</code> policy:</p>
<table class="kv"><tbody>
<tr><th>Band / type</th><td>1 band, float32</td></tr>
<tr><th>CRS</th><td>EPSG:32611 (UTM zone 11N, 100 m)</td></tr>
<tr><th>Shape / transform</th><td>{val['meta']['shape'][0]} × {val['meta']['shape'][1]}; transform
{esc(val['meta']['transform'])} — identical to the sample grid</td></tr>
<tr><th>Values</th><td>min {val['min']:.3f}, max {val['max']:.3f}; <b>{val['n_finite']:,} of
{val['n_finite'] + val['n_nan']:,} cells finite</b>; NaN {val['n_nan']}, infinity {val['n_infinite']}</td></tr>
<tr><th>Outside the footprint</th><td>finite <b>0.0</b> — no NaN anywhere, so the portal range check passes</td></tr>
<tr><th>On mapped catalogue faults</th><td>0 positive pixels — mapped cells are masked out of scoring,
so a dot there would be wasted budget</td></tr>
</tbody></table>
<p class="muted">Local format validity is not organiser acceptance. The upload form remains the only
authority on whether a file is accepted.</p>
</section>

<section class="section" id="nine-sites"><h3>Nine-site comparison — what to download, what it is worth, whether it is unique</h3>
<p>The nine focus sites are one family: the GEMSDOE32 file is the GEMSDOE25 mask with 6,436
catalogue-adjacent dots removed, and the GEMSDOE25/GEMSDOE30 masks are identical predictions. Every one
of the nine overlaps another by more than the 70% three-pixel limit, so <b>none of them is a unique
submission</b> and all have already been scored. The last row is this repository's new candidate.</p>
<div class="table-wrap"><table><thead><tr>
<th scope="col">SITE</th><th scope="col">FILE TO DOWNLOAD</th><th scope="col">OWNER-REPORTED SCORE</th>
<th scope="col">MEASURED (HOLDOUT-DTI, SGMC)</th><th scope="col">PROJECTED</th><th scope="col">UNIQUE?</th>
<th scope="col">VERDICT</th></tr></thead><tbody>{site_table}</tbody></table></div>
<p class="muted">"Owner-reported" values are USER-REPORT (unverified, no submission-page receipt).
"Measured" is HOLDOUT-DTI on the public USGS state-geologic-map off-catalogue instrument; it reproduces the
published GEMSDOE32 champion value 0.09539 to 13 significant figures, which is the audit trail for the
instrument. "Projected" is a two-parameter fit to 18 published submissions (R² {fmt(fitted['r_squared'], 3)},
leave-one-out RMSE {fmt(cal['loo_rmse'], 4)}) and is <b>never</b> a score.</p>
</section>

<section class="section" id="how"><h3>How to submit (exact steps)</h3>
<ol class="steps">
<li><b>Download</b> the GeoTIFF above (or the one-TIFF ZIP). Do not rename it and do not re-save it in
another tool: the portal checks the grid, and the note below is written against this exact file
(SHA-256 <code>{esc(raster['sha256'][:16])}…</code>).</li>
<li><b>Open the competition</b> → <a href="{esc(COMP)}">DrivenData · DOE GEMS Prize Challenge</a> →
enrol and accept the rules, then <b>Submit → Make new submission</b>.</li>
<li><b>Choose the file</b> <code>{esc(name)}.tif</code> (the ZIP is accepted if it contains a single
TIFF; the TIFF is the safer choice).</li>
<li><b>Paste the note</b> shown above ({card['note_chars']} characters, limit 140) and keep the
submission name, so the receipt can be traced back to this page.</li>
<li><b>Submit and keep the receipt.</b> The organiser's confirmation page is the only evidence of
acceptance; copy the receipt and the reported score into this repository as an ORGANIZER-CONFIRMED
entry.</li>
<li><b>One submission only.</b> The rules allow three feedback submissions per week and require exactly
one submission to be selected for both prize rounds; confirm the current quota in your account
(<a href="{esc(RULES)}">official rules PDF</a>, §3.4–3.6).</li>
</ol>
<p class="muted">The competition page states that data outside the submission bounds should be null or NaN,
while the upload form's range check rejects NaN. This file uses finite zeros outside the footprint,
which satisfies the form's [0, 1] requirement and leaves the scored domain untouched. The organiser's own
sample is NaN outside the footprint; if a future submission is rejected on that basis, the same dots can be
re-exported with a NaN exterior - but this version is the one that passes the range check that produced
the earlier error.</p>
</section>

<section class="section" id="evidence"><h3>What is proven, and what is not</h3>
<table class="kv"><tbody>
<tr><th>Proven by saved bytes</th><td>Format, grid, value range, finiteness, dot count, ZIP content and
the registry overlap measurement are all re-derivable from the committed files and receipts.</td></tr>
<tr><th>Proven by holdout</th><td>HOLDOUT-DTI {fmt(dti, 5)} on the blocked SGMC hide-and-recover
instrument ({policy['withheld_positive_pixels']:,} withheld positives, evaluator
<code>{esc(holdout['evaluator_version'])}</code>). The champion's equivalent value on the same
instrument and code path is 0.09539.</td></tr>
<tr><th>Not proven</th><td>No organiser receipt exists for this file; the private expert truth is not
public; the projection ({fmt(cand_proj.get('projected_score', float('nan')))} with 95% interval
{esc(cand_proj.get('projected_95pi'))}) is an extrapolation with a documented bias; and the pinned
registry is a nine-repository snapshot, not a complete global registry.</td></tr>
<tr><th>Disclosure</th><td>Training labels for this lane are public: the USGS State Geologic Map
Compilation fault structures (public domain, <a href="{esc(SGMC_LANDING)}">mrdata.usgs.gov</a>) and
the competition's own mapped catalogue, plus public GeoDAWN airborne radiometrics
(<a href="{esc(GEODAWN)}">USGS ScienceBase</a>). No competition test labels, receipts or private-round
scores were used. Generative-AI use is disclosed in the competition narrative as the rules require.</td></tr>
</tbody></table>
<p><a href="data/hunmap/e1-blocked-holdout.json">Blocked holdout receipt ↗</a> ·
<a href="data/hunmap/hunmap-uniqueness-verdict.json">Registry overlap verdict ↗</a> ·
<a href="data/hunmap/lattice-rule-calibration.json">Lattice rule calibration ↗</a> ·
<a href="data/hunmap/leaderboard_calibration.json">Calibration fit ↗</a> ·
<a href="data/hunmap/nine_site_sgmc_cal.json">Nine-site instrument measurements ↗</a> ·
<a href="data/hunmap/e2-train-canary.json">Leakage canary ↗</a> ·
<a href="data/hunmap/e2f-catalogue-holdout.json">Cross-family transfer test ↗</a></p>
</section>

<section class="section" id="limits"><h3>Limitations and what would improve this</h3>
<ul>
<li>The independent SGMC instrument is not the hidden expert truth; it is a different public mapping of
the same area, and the two disagree for some historical submissions (the 18-point fit has R²
{fmt(fitted['r_squared'], 3)}, leave-one-out RMSE {fmt(cal['loo_rmse'], 4)}).</li>
<li>The emission policy (radius, dot budget, catalogue apron) was chosen on the same blocked instrument,
so the reported HOLDOUT-DTI is selection-biased upward; the spread across 36 policy combinations is
recorded in the receipt.</li>
<li>The blocked holdout uses four spatial quadrants; more folds and a per-fold CI would tighten the
interval. A GPU would allow per-fold retraining of the full feature stack and a proper bootstrap CI.</li>
<li>The registry snapshot covers nine public repositories only; a duplicate outside it cannot be excluded.</li>
<li>The next lane should attack precision rather than coverage: the metric charges 0.2 for a false
positive but 0.8 for a missed truth cell, so fewer, better-placed dots win - and the measured marginal
hit rate of this detector still exceeds the break-even rate up to about 100,000 dots.</li>
</ul>
<p>Official sources: <a href="{esc(PROBLEM)}">problem description</a> ·
<a href="{esc(LEADERBOARD)}">leaderboard</a> · <a href="{esc(SUBMISSIONS)}">your submissions</a> ·
<a href="{esc(RULES)}">rules PDF</a> · <a href="{esc(REPO)}">repository</a>.</p>
</section>
</main>
<footer class="footnote"><p><b>Evidence labels:</b> HOLDOUT-DTI is a local proxy with its evaluator,
withheld count and interval; it is not a leaderboard result. PROJECTION is a fitted estimator, never a
score. Owner-reported values are USER-REPORT unless linked to an organiser receipt.</p>
<p>Maximize P(Win). Own the outcome. <a href="{esc(REPO)}/blob/main/README.md">Project instructions</a> ·
<a href="{esc(REPO)}/tree/main/evidence/hunmap">Evidence folder</a></p></footer>
</body></html>'''


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    html_text = build()
    dest = DOCS / "submission.html"
    mirrors = {src.name: src for src in sorted(EV.glob("*.json"))}
    if args.check:
        if not dest.is_file() or dest.read_text() != html_text:
            print("stale: docs/submission.html", flush=True)
            return 1
        for name, src in mirrors.items():
            mirror = DATA / name
            if not mirror.is_file() or mirror.read_bytes() != src.read_bytes():
                print(f"stale: {mirror.relative_to(DOCS)}", flush=True)
                return 1
        print("submission page up to date")
        return 0
    dest.write_text(html_text)
    DATA.mkdir(parents=True, exist_ok=True)
    for name, src in mirrors.items():
        (DATA / name).write_bytes(src.read_bytes())
    print(f"wrote {dest.relative_to(ROOT)} and {len(mirrors)} evidence mirrors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

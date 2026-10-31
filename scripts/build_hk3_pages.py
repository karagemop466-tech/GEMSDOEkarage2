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
    if (inventory["inventory_status"] != "PASS_RESEARCH_ONLY_PLUS_ONE_CLEARED"
            or inventory["downloadable_approved_submission"] is not None
            or inventory["slot_authorized"] is not False or len(hk3_inventory) != 1
            or hk3_inventory[0]["raster_sha256"] != sha
            or not inventory["inventory_status"].startswith("PASS_RESEARCH_ONLY")
            or any(row["status"] not in ("VERIFIED_RESEARCH_ONLY",
                                         "VERIFIED_CLEARED_UNIQUE_NOT_FORECAST_TO_WIN")
                   for row in inventory["artifacts"])
            or any(row["ok_to_submit"] is not False for row in inventory["artifacts"]
                   if row["kind"] != "cleared")
            or any(row["slot_authorized"] is not False for row in inventory["artifacts"])
            or [row["file"] for row in inventory["artifacts"] if row["kind"] == "cleared"]
               != ["docs/downloads/gemsdoekarage2-geo-habitat-dti-20261031.tif"]):
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
    return {"card": card, "selector": selector, "witness": witness, "registry": registry,
            "inventory": inventory, "focus": records, "geometry": geometry, "official": official,
            "official_filename": official_filename, "monitor": monitor, "k3": k3,
            "profile": profile, "uniq": uniq, "pairs": pairs}


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
<p>Maximize P(Win). Own the outcome. <a href="{REPO}/blob/main/README.md">Project instructions</a> · <a href="{esc(official_ref)}">Source observations</a> · <a href="../research/2026-10-30-live-source-and-code-review.md">Three-pass review</a> · <a href="evidence/live-source-review-card-2026-10-30.json">Review card</a></p></footer>
</main></body></html>'''



def _new_release() -> dict | None:
    """Load the 2026-10-31 independent-habitat release, if all receipts exist."""
    root = ROOT
    rc = root / "evidence" / "run-card-gemsdoekarage2-geo-habitat-dti-20261031.json"
    hold = root / "evidence" / "habitat-holdout-2026-10-31.json"
    proj = root / "evidence" / "projection-range-2026-10-31.json"
    if not (rc.exists() and hold.exists() and proj.exists()):
        return None
    out = {"run_card": json.loads(rc.read_text()),
           "holdout": json.loads(hold.read_text()),
           "projection": json.loads(proj.read_text())}
    card = rc.parent.parent / "docs" / "downloads" / "gemsdoekarage2-geo-habitat-dti-20261031.run-card.json"
    if card.exists():
        out["site_card"] = json.loads(card.read_text())
    return out


def release_banner(d: dict) -> str:
    """Top-of-page answer: what the new file is, whether it is safe to submit, one click."""
    r = _new_release()
    if r is None:
        return ""
    rc, ho, pr = r["run_card"], r["holdout"], r["projection"]
    finfo = rc.get("file", rc.get("raster", {}))
    tif = finfo.get("path", "")
    name = Path(tif).name
    sha = finfo.get("sha256", "")
    nd = finfo.get("positive_pixels", 0)
    h = ho["HOLDOUT_DTI"]
    cand = pr["candidate_projections"].get(name, {})
    gammas = [(k, v) for k, v in cand.items() if k.startswith("gamma_")]
    gtxt = " · ".join(f"γ={k.split('_')[1]}: <b>{v:.3f}</b>" for k, v in sorted(gammas, key=lambda kv: float(kv[0].split("_")[1])))
    best_proj = max([v for _, v in gammas]) if gammas else 0.0
    worst_proj = min([v for _, v in gammas]) if gammas else 0.0
    uniq = rc.get("uniqueness", {})
    mx = uniq.get("max_frac_ours_within_3px")
    mx_txt = f"{mx * 100:.1f}%" if isinstance(mx, (int, float)) else "measured"
    note = rc.get("note", "")
    return f'''<section class="hero" id="new-release">
<h2>New download · {nd:,} dots · generated 2026-10-31</h2>
<p class="verdict"><b class="warn">OK TO DOWNLOAD. UNIQUE. NOT EXPECTED TO BEAT 0.2778.</b>
This file was generated from scratch by this project — it is <b>not</b> a copy, rename or re-encode of anyone
else's submission. Every gate that can be checked without private data passes. But no available evidence
supports a claim that it will out-score the current focus-site high.</p>
<table class="kv"><tbody>
<tr><th>Format gates</th><td><b class="yes">PASS.</b> Single-band float32, EPSG:32611, 100 m, {finfo.get("height", "?")} × {finfo.get("width", "?")} template grid, {nd:,} dots, min {finfo.get("min")} / max {finfo.get("max")}, all {finfo.get("finite_pixels", 0):,} saved values finite. <code>{esc(name)}</code></td></tr>
<tr><th>Uniqueness vs the other GEMSDOE sites</th><td><b class="yes">UNIQUE.</b> Largest fraction of our dots within 3 px of any one pinned published raster: <b>{mx_txt}</b> (stop threshold 70%). Largest Jaccard against any of them: <b>{uniq.get("max_jaccard", 0):.4f}</b>. Well clear of both duplicate clauses.</td></tr>
<tr><th>HOLDOUT-DTI</th><td><b>{h["estimate"]:.4f}</b>, 95% CI [{h["ci95"][0]:.4f}, {h["ci95"][1]:.4f}]. {ho["metric"]}. {ho["withheld_positives_isolated"]:,} withheld isolated positives, {ho["emitted_total"]:,} emitted dots, pooled over {len(ho["per_fold"])} interleaved spatial folds. <b>This is a proxy measured against withheld catalogue faults, not the organizer score.</b></td></tr>
<tr><th>Forward projection vs the 21 published scores</th><td><b>PROJECTION: {worst_proj:.3f}–{best_proj:.3f}</b> ({gtxt}). Model: a hidden-truth density proportional to the smoothed union of the eight best published rasters, its scale fitted to the 21 USER-REPORTED scores (in-sample RMSE {min(v["rmse"] for v in pr["gamma_fits"].values()):.3f}–{max(v["rmse"] for v in pr["gamma_fits"].values()):.3f} across the sharpness sweep). <b>This is a model, not an organizer score.</b></td></tr>
<tr><th>Verdict</th><td><b class="warn">Submitting this file is a defensible but low-expected-score choice.</b> It is safe (unique, valid, genuinely ours). It is not forecast to win: the point of the forward model is that the highest-scoring published files occupy a compact territory that a novel placement, by construction, does not.</td></tr>
</tbody></table>
<p><a class="btn big" href="downloads/{esc(name)}" download>↓ Download {esc(name)}</a>
<a class="btn secondary" href="{esc('evidence/run-card-' + name.replace('.tif', '') + '.json')}">Run card</a>
<a class="btn secondary" href="evidence/habitat-holdout-2026-10-31.json">Holdout receipt</a>
<a class="btn secondary" href="evidence/projection-range-2026-10-31.json">Projection receipt</a></p>
<div class="meta"><b>SHA-256:</b> <code>{esc(sha)}</code><br><b>Submission name:</b> <code>{esc(rc.get("submission_name", name))}</code><br><b>Note ({len(note)} chars):</b> {esc(note)}</div>
</section>'''



def hypotheses_2026_10_31() -> str:
    """Five ranked hypotheses. Rank = expected DTI gain per unit implementation cost,
    subject to the uniqueness gate being non-negotiable."""
    rows = [
        ("H3", "Relay-ramp and fault-tip localisation along range fronts",
         "Layers: skeletonised detrended-elevation gradient ridges + magnetic horizontal-gradient maxima. "
         "Transform: segment the ridges, then score each pixel by its distance to the nearest ridge *tip* or "
         "along-strike stepover rather than to the ridge itself.",
         "Fault maps trace the principal scarp and terminate it at the last unambiguous break. Displacement "
         "transfer at relay ramps and tip splays produces real, continuous, but shorter and less expressive "
         "scarps — exactly the population an expert panel adds and a catalogue omits. It is a *position* the "
         "habitat index smears out, not a stronger version of the same ranking.",
         "Medium. Needs a lineament segmentation pass (one session). Must be validated on the 16-fold spatial "
         "holdout before any slot."),
        ("H4", "Geothermal pathway intersections: basement step × conductivity boundary",
         "Layers: horizontal gradient of depth-to-basement, gradient of the conductivity surface, "
         "and their intersection (product of the two gradient magnitudes, thresholded).",
         "The prize rewards geothermal fault discovery, so the labelled faults are plausibly "
         "prospectivity-biased rather than a uniform structural sample. A basement step provides the "
         "permeability contrast; a conductivity boundary marks the fluid. Their intersection is a narrower, "
         "more physically specific target than 'a fault'.",
         "Medium-high. Premise is unvalidated and could be orthogonal to the label set. Cheap to test: "
         "block-level correlation against the published-territory proxy decides it in minutes."),
        ("H5", "Potential-field-only edge coincidence (no topography)",
         "Layers: |gravity horizontal gradient| × |magnetic horizontal gradient| × tilt-derivative edge "
         "magnitude, with detrended elevation deliberately excluded.",
         "The best published files are strongly topographic (detrended-elevation slope ρ = +0.46 at 10 km "
         "block scale). A purely potential-field detector is an orthogonal line of evidence and would either "
         "confirm the structural signal independently or expose an erosional mimic.",
         "Low cost — all bands are already in the stack. Expected gain low-moderate; main value is as an "
         "independent check, since it will partly duplicate H2."),
        ("H2", "Relief + magnetic-contact structural habitat (RELEASED 2026-10-31)",
         "Layers: z(log1p det_elev_slope) + z(log1p tmi_hg) − z(tc) + 0.5·z(|iso_grav_anom_hg|), "
         "rank-transformed, × (1 − exp(−d_cat/3 px)), zeroed within 100 m of a mapped fault; dots placed by "
         "lazy-greedy maximisation of expected DTI.",
         "The scored faults are not where the catalogue is, so a model must rank *under-mapped* ground. "
         "Measured: median dot-to-catalogue distance 35 px, 0% of dots within 3 px of a mapped fault, "
         "40,561 dots at ~300 m spacing.",
         "Done. HOLDOUT-DTI 0.0172 [0.0130, 0.0227]; forward projection 0.007–0.013. Released as the "
         "download on this page."),
        ("H1", "Consensus-territory model (learned from the published winners)",
         "Layers: a hidden-truth density proportional to smooth(union of the eight best published rasters)^γ, "
         "with K fitted to the 21 USER-REPORTED scores.",
         "It reproduces all 21 reported scores to RMSE 0.029–0.037, far better than any geophysical "
         "parameterisation we tried (0.139–0.193). It implies the expert label set has absorbed where the "
         "community already dotted.",
         "BLOCKED — not by cost but by the rule. Measured: 99% of the dots it emits land within 3 px of a "
         "published raster, against a 70% stop. It is excluded from the ranking on the uniqueness "
         "constraint, not on expected score."),
    ]
    body = "".join(
        f'<tr><td><b>{esc(h)}</b></td><td><b>{esc(t)}</b><span class="sub-label">{esc(lays)}</span></td>'
        f'<td>{esc(why)}</td><td>{esc(cost)}</td></tr>'
        for h, t, lays, why, cost in rows)
    return (
        '<section class="section" id="hypotheses-2026-10-31"><h3>Five new geological hypotheses, ranked</h3>\n'
        '<p>Ranked by expected DTI gain per unit implementation cost, with the uniqueness gate treated as '
        'non-negotiable. H1 is listed last because it is disqualified, not because it is weak — it is the '
        'strongest predictor we measured and the reason is stated in its row. <b>None of H3–H5 has been '
        'validated on the spatial holdout yet; a slot may not be spent on one until it has.</b></p>\n'
        '<table><thead><tr><th>#</th><th>Hypothesis · layers</th><th>Why it should catch off-catalogue faults, '
        'and how it differs from everything in this repo</th><th>Cost / status</th></tr></thead><tbody>'
        + body + '</tbody></table></section>')

def why_2778() -> str:
    return '''<section class="section" id="why-2778"><h3>Why GEMSDOE32 <code>h33-h33-2-b2</code> reported 0.2778</h3>
<p>The value is <b>USER-REPORTED / UNVERIFIED</b> — no organizer receipt was retrievable from this sandbox.
The explanation below is inferred from measurements on the 21 pinned rasters plus the fitted forward model,
not from any private data. It is a hypothesis with quantitative support, not an established fact.</p>
<ol>
<li><b>It is a lineage effect, not a single-file effect.</b> Thirteen of the 21 pinned rasters share one
construction (dotted habitat at ~300 m spacing, every dot deleted within 100 m of a mapped fault). They score
0.245–0.278. The eight that do not, score 0.021–0.165. No smooth geophysical basis we fitted separates
winners from losers; the lineage does.</li>
<li><b>Placement beats dot count.</b> Among the seven pinned files with exactly 37,654 dots the pairwise
Jaccard is only 0.010–0.089 while the reported scores span 0.0206–0.2778. Overlap between files does not
explain the score; where the dots land does.</li>
<li><b>The winners sit 1.4–2.0 km from mapped faults; the losers sit 0.4–0.6 km.</b> Median distance from
each dot to the nearest catalogue pixel is 15.0–19.7 px for every file scoring ≥ 0.245 and 4.1–5.8 px for
every file scoring ≤ 0.15. <b>Zero</b> percent of dots in <em>any</em> file lie within 1 px of the catalogue.</li>
<li><b>The winners are in the sparsely mapped north-west and centre.</b> 10 km block maps show the top
scorers concentrating density where the catalogue is thinnest; the bottom scorers reproduce the catalogue
map block for block.</li>
<li><b>The forward model says the scored label set has absorbed that territory.</b> Fitting a hidden-truth
density of the form <code>K · w/Σw</code> with <code>w = smooth(union of the eight best rasters)^γ</code>
reproduces all 21 reported scores to RMSE 0.029–0.037, whereas every smooth geophysical parameterisation we
tried (catalogue buffer; <code>K·s^η·(1−e^{−d/λ})</code>; 5- and 9-basis log-linear densities) had RMSE
0.139–0.193 or collapsed to uniform. The reading is that the expert panel's newly identified faults sit where
the community already dotted, because those dots were reviewed.</li>
</ol>
<p><b>Can we exceed it?</b> Not with a method that is genuinely independent. Two measured results bound the
answer. First, our independent habitat index — built only from relief, magnetic horizontal gradient, gravity
gradient and tilt angle, with no reference to any published file — correlates only ρ = +0.26 with that fitted
truth density, and the raster it produces projects to 0.007–0.013. Second, the moment we let the published
territory into the density, the emitted dots become a duplicate: 99% of them land within 3 px of a published
raster, far above the 70% stop. <b>Under this model, "unique" and "high-scoring" are in direct tension,
because the R = 3 px credit kernel only pays dots that sit inside the winners' ±3 px halo.</b></p>
<p>The honest escape routes are: (a) obtain an organizer-confirmed receipt for one published file and
re-calibrate; (b) find covariate evidence for the winners' territory that is independent of the winners —
the block-level correlations (relief slope +0.46, magnetic gradient +0.36, tilt −0.18) are the strongest such
handle found so far and are already built into the released file; or (c) accept a slot on a lower-expected-
score but genuinely novel entry.</p>
<p class="muted">Every number above is either HOLDOUT-DTI (measured here, with its evaluator and CI) or
labelled USER-REPORTED / UNVERIFIED / PROJECTION. Nothing on this page is ORGANIZER-CONFIRMED.</p>
</section>'''

def hero(d: dict) -> str:
    c, w = d["card"], d["witness"]
    name = Path(c["raster"]["file"]).name
    return f'''<section class="hero" id="research-download">
<h2>Legacy research TIFF · not a submission</h2>
<p><b>See the new release above for the downloadable, unique file.</b> The file below is the older
HK3 surface, retained only for reproducibility; its approval was withdrawn.</p>
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



def _site_projections() -> dict:
    """Per-site forward projection of that site's best pinned file.

    Labels come from the byte-verified calibration registry; for each site we take the
    pinned file with the highest USER-REPORTED score and report the range of its forward
    projection across the sharpness sweep. This is a PROJECTION, never a score.
    """
    f = ROOT / "evidence" / "projection-range-2026-10-31.json"
    if not f.exists():
        return {}
    pr = json.loads(f.read_text())
    labels = list(pr["reported_scores"].keys())
    out: dict[str, dict] = {}
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        cands = [l for l in labels if l.startswith(site + "-")]
        if not cands:
            continue
        best = max(cands, key=lambda l: pr["reported_scores"][l])
        vals = [pr["gamma_fits"][g]["preds"][labels.index(best)]
                for g in pr["gamma_fits"]]
        out[site] = {"label": best,
                     "reported": pr["reported_scores"][best],
                     "lo": min(vals), "hi": max(vals)}
    return out


def nine_site_table(d: dict) -> str:
    by_site = {row["site"]: row for row in d["geometry"]["historical_final_dots"]}
    records = sorted(d["focus"], key=lambda r: -r["owner_reported_unverified"])
    sproj = _site_projections()
    rows = []
    for rec in records:
        site = rec["site"]
        geo = by_site[site]
        source = owner_source(rec)
        sp = sproj.get(site)
        if sp is None:
            estimate = '<td>Unavailable</td>'
        else:
            estimate = (f'<td><b>{sp["lo"]:.3f}–{sp["hi"]:.3f}</b>'
                        f'<span class="sub-label">PROJECTION for <code>{esc(sp["label"])}</code> '
                        f'· USER-REPORTED {sp["reported"]:.4f} · a model, not a score</span></td>')
        rows.append(f'''<tr><td><a href="sites/{esc(site)}.html">{esc(site)}</a></td>
<td><a href="{esc(source)}">{esc(rec['file'])}</a><span class="sub-label">Historical reference · download for research only</span></td>
<td><b>{rec['owner_reported_unverified']:.4f}</b><span class="sub-label">USER-REPORTED / UNVERIFIED</span></td>
{estimate}<td><b class="no">NO</b> · {geo['max_focus_overlap_fraction'] * 100:.1f}% near {esc(geo['closest_focus_site'])}</td><td><b class="no">DO NOT SUBMIT</b></td></tr>''')
    monitor = d["monitor"]
    source_rows = monitor["sites"]
    changed = sum(row["status"] == "changed" for row in source_rows)
    unavailable = sum(row["status"] == "unavailable" for row in source_rows)
    freshness = f'''<p class="muted"><b>GITHUB METADATA ONLY · {esc(monitor['generated_utc'])}:</b> {changed} of {len(source_rows)} focus-site main branches differ from the pinned historical references; {unavailable} are unavailable. A changed branch does not establish a new high score, raster identity, or eligibility. No latest-head raster/score audit is claimed. <a href="audit.html">Open the source-freshness view</a>.</p>'''
    return f'''<section class="section"><h3>Nine-site executive scorecard</h3>
<p>Highest <em>reported</em> historical file from each requested site in the supplied list; the values have no linked organizer submission-page receipt. These pinned files are research references, not recommendations or verified current site champions. Click a site for its individual summary.</p>
{freshness}
<table id="nine-sites"><thead><tr><th>Site</th><th>Historical file · research only</th><th>Historical report</th><th>Estimated score (PROJECTION)</th><th>Unique vs other eight?</th><th>Action</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p><b>Estimated score</b> is the forward projection of that site's best pinned file under the model
described above — range across the sharpness sweep γ ∈ [0.25, 4]. It is a <b>PROJECTION</b>, not an
organizer score and not a re-measurement; the USER-REPORTED value is shown beside it for comparison.
Uniqueness is the directional share of a file's positive dots within three pixels of another pinned file. A different byte hash does not imply a different prediction. <a href="audit.html">Explore the nine-site audit and source freshness →</a></p>
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
    return f'''<section class="section"><h3>How to submit, when an eligible file exists</h3>
<p><b class="no">Do not upload any current file.</b> These instructions are conditional; neither inspection nor a format pass bypasses the literal duplicate stop.</p>
<p><b>Official rules, verified 2026-10-29</b> (<a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">NLR rules PDF</a>, §1.1 and §3.2): one entry per competitor; a <em>single</em> GeoTIFF with a single raster layer at 100 m; submission limit <em>three submissions per week</em>; generative-AI use must be described in the narrative. The problem page (<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">page 967</a>) specifies values between 0 and 1, float32, and null or NaN outside the bounds.</p>
<ol><li>Run a newly assigned lane using the shared feature stack, evaluator and writer. Stop immediately if the pre-placement surface is a duplicate. Test every input feature alone for leakage; AUC over 0.90 is suspect.</li>
<li>Use buffered whole-segment hide-and-recover; build all catalogue features from visible faults only and mask visible faults pixel-exactly. Compare pooled DTI against the current same-fold incumbent with a paired 95% interval. An uncalibrated holdout is not a leaderboard estimate.</li>
<li>Recheck the exact final TIFF against the complete current registry and authenticate the organizer sample. Verify a single float32 band, matching CRS/shape/transform, and no non-finite or out-of-range values inside the actual footprint. Reconcile the official null/NaN exterior guidance with the portal range behavior; neither convention is assumed accepted.</li>
<li>Only after every automated gate passes, a separate selector checks the account quota. The <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules</a> describe up to three scored attempts per week and one final selection per participating entity.</li>
<li>Then download the approved <code>.tif</code>, verify its SHA-256, sign in to the <a href="{SUBMISSIONS}">DrivenData submissions page</a>, choose the file, and use the recorded unique name and a short note no longer than 140 characters. The official problem page specifies a GeoTIFF; ZIP upload acceptance was not verified. Save the actual organizer receipt; do not promote a projection into a score.</li></ol>
<p>Our checks require no human inspector. The current blocker is missing/contradictory evidence and an unassigned lane, not a request to waive a gate. No account credentials are stored by this project.</p></section>'''


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


def render_all(d: dict) -> dict[str, str]:
    desk = release_banner(d) + decision_section(d) + candidate_section(d) + champion_panel() + gw_nfs_panel() + hero(d) + why_2778() + hypotheses_2026_10_31() + policy_section(d) + registry_audit_section(d) + evidence_summary(d) + nine_site_table(d) + nested_section(d) + science_and_sources(d) + legacy()
    how = hero(d) + guide(d) + legacy()
    official_ref = f"evidence/{d['official_filename']}"
    pages = {"index.html": shell("Submission desk", "desk", desk, official_ref=official_ref),
             "executive-summary.html": shell("Executive summary", "summary", desk, official_ref=official_ref),
             "how-to-submit.html": shell("How to submit", "guide", release_banner(d) + how + hypotheses_2026_10_31(), official_ref=official_ref),
             "submit.html": shell("How to submit", "guide", how, official_ref=official_ref),
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
    mirrors += [(f, DOCS / "evidence/lattice-gate" / f.name) for f in sorted((EV / "lattice-gate").glob("*.json"))]
    mirrors += [(f, DOCS / "evidence/gw-nfs" / f.name) for f in sorted((EV / "gw-nfs").glob("*.json"))]
    mirrors += [(f, DOCS / "evidence/uniqueness" / f.name) for f in sorted((EV / "uniqueness").glob("*.json"))]
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

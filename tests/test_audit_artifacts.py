import json
from pathlib import Path
import subprocess
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def load(rel):
    return json.loads((ROOT / rel).read_text())


def test_audit_and_run_card_are_consistent_and_negative():
    audit = load("docs/data/reference-audit.json")
    card = load("docs/data/run-card.json")
    assert len(audit["reference_files"]) == 9
    assert len(audit["directional_pairwise_overlap"]) == 72
    assert min(audit["directional_pairwise_overlap"].values()) > 0.70
    assert all(not x["unique_vs_other_eight"] and not x["submission_authorized"] for x in audit["reference_files"])
    assert all(x["organizer_receipt"] is None and x["leaderboard_estimate"] is None for x in audit["reference_files"])
    assert audit["sample_mirror_diagnostic"]["positive_pixels"] == 60988
    assert audit["sample_mirror_diagnostic"]["equals_mirrored_labels_inside_footprint"] is True
    assert audit["measured_family_relations"]["gems25_and_gems30_equal_inside_footprint"]
    assert audit["measured_family_relations"]["gems32_equals_gems25_after_gt_2px_known_fault_filter"]
    assert card["preplacement_geometry"]["uncovered_footprint_cells"] == audit["budget_bound"]["uncovered_footprint_cells"]
    assert card["preplacement_geometry"]["minimum_possible_directional_overlap"] == audit["budget_bound"]["min_fraction_within_3px"]
    assert card["preplacement_geometry"]["duplicate_stop"] is audit["budget_bound"]["forced_duplicate_stop"] is True
    assert card["holdout_dti"] is None and card["raster_sha256"] is None
    assert card["submission_name"] is None and card["submission_note"] is None
    assert card["verdict"] == "negative" and not card["new_submission_tiff_generated"] and not card["weekly_slot_selected"]
    from scripts.readiness import assess
    assert assess(card)["verdict"] == "negative"
    assert assess(card)["slot_authorized"] is False


def test_manifest_pins_both_references_and_shared_tools():
    manifest = load("research/reference-sources.json")
    assert len(manifest["references"]) == 9
    assert len({x["site"] for x in manifest["references"]}) == 9
    assert len(manifest["template"]["files"]) == 8
    for obj in manifest["references"] + manifest["inputs"] + manifest["template"]["files"]:
        assert len(obj["sha256"]) == 64 and len(obj["ref"]) == 40
    assert all(not x["cache_path"].startswith("/") for x in manifest["references"] + manifest["inputs"])


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.downloads = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and "download" in attrs:
            self.downloads.append(attrs.get("href"))
        for name in ("href", "src"):
            if name in attrs:
                self.urls.append(attrs[name])


def test_all_internal_site_links_exist():
    pages = [ROOT / "index.html", *sorted((ROOT / "docs").glob("*.html"))]
    for page in pages:
        parser = Links()
        parser.feed(page.read_text())
        for raw in parser.urls:
            url = urlsplit(raw)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (page.parent / unquote(url.path)).resolve()
            assert target.is_relative_to(ROOT) and target.exists(), f"{page}: {raw}"


def test_website_is_derived_from_audit_and_has_no_download_link():
    subprocess.run([sys.executable, str(ROOT / "scripts/build_audit_site.py"), "--check"], check=True, cwd=ROOT)
    page = (ROOT / "docs/audit.html").read_text()
    assert page.count('<tr data-site="GEMSDOE') == 9
    assert "Download unavailable" in page and "No approved file yet" in page
    parser = Links()
    parser.feed(page)
    assert parser.downloads == []
    assert "Do not submit" in page

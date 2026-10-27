from html.parser import HTMLParser
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_site import render


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.disabled = []
        self.text = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids
            self.ids.add(attrs["id"])
        if tag in ("a", "link", "script"):
            ref = attrs.get("href") or attrs.get("src")
            if ref:
                self.links.append(ref)
        if tag == "button" and "disabled" in attrs:
            self.disabled.append(attrs)
    def handle_data(self, data):
        self.text.append(data)


def test_static_pages_are_consistent_and_local_links_resolve():
    render()
    for name in ("index.html", "executive-summary.html"):
        page = ROOT / "docs" / name
        parser = PageParser()
        parser.feed(page.read_text())
        for href in parser.links:
            if href.startswith("#"):
                assert href[1:] in parser.ids, (name, href)
            elif not (href.startswith("https://") or href.startswith("mailto:")):
                path = href.split("#")[0].split("?")[0]
                if path:
                    assert (page.parent / path).exists(), (name, href)
        text = page.read_text()
        assert text.count("DO NOT SUBMIT</span>") == 9
        assert "UNVERIFIED" in text
        assert "{{" not in text
        if name == "index.html":
            assert parser.disabled and "Download submission TIFF" in text
    assert not list((ROOT / "docs").rglob("*.tif"))


def test_site_receipts_match_evidence_and_never_authorize_upload():
    card = json.loads((ROOT / "docs/data/run-card.json").read_text())
    audit = json.loads((ROOT / "docs/data/geometry-audit.json").read_text())
    assert card == json.loads((ROOT / "evidence/run-card.json").read_text())
    assert audit == json.loads((ROOT / "evidence/geometry-audit.json").read_text())
    assert card["verdict"] == "negative" and card["upload_approved"] is False
    assert len(audit["historical_final_dots"]) == 9
    assert all(r["literal_result"] == "DUPLICATE_STOP" for r in audit["historical_final_dots"])
    lineage = audit["lineage"]
    assert lineage["g31_removed_at_known_fault_distance_gt1_le2_pixels"] == lineage["g31_dots_removed_in_g32"] == 2545
    assert lineage["g32_dots_within_2_pixels_of_mirrored_known_faults"] == 0

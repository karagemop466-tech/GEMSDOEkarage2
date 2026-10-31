"""A known duplicate must not be rebuilt or advertised for upload."""
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_legacy_generator_stops_before_modifying_outputs():
    target = ROOT / 'docs/downloads/gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros.tif'
    before = hashlib.sha256(target.read_bytes()).digest()
    run = subprocess.run([sys.executable, str(ROOT / 'scripts/generate_submission.py')],
                         cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert run.returncode != 0
    assert 'BLOCKED' in run.stderr and 'No TIFF generated or published' in run.stderr
    assert hashlib.sha256(target.read_bytes()).digest() == before


def test_primary_pages_do_not_offer_legacy_file_for_upload():
    import json
    import re
    card = json.loads((ROOT / 'evidence/hk3/run_card.json').read_text())
    hb = json.loads((ROOT / 'docs/downloads/gemsdoe-blind-geothermal-rad-mag-grav-intersection-20261031.run-card.json').read_text())
    allowed = {
        'downloads/gemsdoekarage2-hk3-edgecentrality-apron3-20261028.tif',
        'downloads/gemsdoe-blind-geothermal-rad-mag-grav-intersection-20261031.tif',
    }
    for name in ('index.html', 'executive-summary.html', 'how-to-submit.html'):
        text = (ROOT / 'docs' / name).read_text()
        assert 'unique research TIF' not in text
        assert 'DO NOT SUBMIT' in text
        downloads = re.findall(r'<a[^>]*href="([^"]+)"[^>]*\sdownload[\s>]', text)
        assert set(downloads).issubset(allowed)
        assert all('hkarage1' not in href and 'h1-parity' not in href and 'k2-hgbcont' not in href for href in downloads)
        if name in ('index.html', 'executive-summary.html'):
            assert len(downloads) == 2
        else:
            assert len(downloads) == 1 and hb['submission_name'] in downloads[0]
        assert 'uniqueness not established' in text
        # The literal-stop receipt prevents any card from reviving approval.
        assert card['verdict'] == 'negative'
        assert 'OK TO SUBMIT: NO' in text and 'OK TO SUBMIT: YES' not in text

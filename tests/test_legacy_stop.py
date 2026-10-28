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
    for name in ('index.html', 'executive-summary.html', 'how-to-submit.html'):
        text = (ROOT / 'docs' / name).read_text()
        assert 'unique research TIF' not in text
        assert 'DO NOT SUBMIT' in text
        for href in re.findall(r'<a[^>]*href="([^"]+)"[^>]*\sdownload[\s>]', text):
            assert 'hkarage1' not in href and 'h1-parity' not in href and 'k2-hgbcont' not in href
            assert card['submission']['name'] in href
        # Historical PROMOTE is superseded by the current hard-stop gate.
        assert 'NO APPROVED SUBMISSION' in text
        assert 'OK TO SUBMIT: YES' not in text

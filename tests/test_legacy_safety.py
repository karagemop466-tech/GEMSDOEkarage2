import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_legacy_generator_fails_closed():
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/generate_submission.py')],
                            cwd=ROOT, capture_output=True, text=True, timeout=20)
    assert result.returncode != 0
    assert 'BLOCKED' in result.stderr
    assert 'No TIFF generated or published' in result.stderr


def test_legacy_audit_reproduces_committed_receipt():
    if not (ROOT / '.cache/input/r13-lattice.tif').exists():
        pytest.skip('Restore pinned mirrors to run saved-byte geometry audit')
    from scripts.audit_legacy_dots import audit
    report = audit()
    expected = json.loads((ROOT / 'evidence/legacy-dot-audit-2026-10-28.json').read_text())
    assert report == expected
    assert report['duplicate_stop'] and not report['submission_authorized']
    assert report['positive_outside_mirror_footprint'] > 0


def test_legacy_audit_published_identically_and_not_promoted():
    local = json.loads((ROOT / 'evidence/legacy-dot-audit-2026-10-28.json').read_text())
    published = json.loads((ROOT / 'docs/evidence/legacy-dot-audit-2026-10-28.json').read_text())
    assert local == published
    assert local['verdict'] == 'negative' and not local['submission_authorized']
    assert 'not unique' in (ROOT / 'docs/index.html').read_text().lower()
    assert 'NO APPROVED FILE' in (ROOT / 'docs/how-to-submit.html').read_text()

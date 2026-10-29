"""The 2026-10-29 unique-submission generator is retired: it must not write any TIFF.

Its two outputs (gw-nfs, H-A) fail the full 440-raster duplicate gate and were quarantined.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_retired_unique_generator_writes_nothing():
    before = {p.name: p.stat().st_mtime_ns for p in (ROOT / 'docs/downloads').iterdir()}
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/generate_unique_submission.py')],
                            cwd=ROOT, capture_output=True, text=True)
    after = {p.name: p.stat().st_mtime_ns for p in (ROOT / 'docs/downloads').iterdir()}
    assert result.returncode != 0
    assert 'retired' in result.stderr
    assert before == after

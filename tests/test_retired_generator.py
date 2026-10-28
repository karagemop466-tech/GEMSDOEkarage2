import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_legacy_generator_cannot_write_a_new_file():
    before = {p.name: (p.stat().st_size, p.stat().st_mtime_ns)
              for p in (ROOT / 'docs/downloads').iterdir()}
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/generate_submission.py')],
                            cwd=ROOT, capture_output=True, text=True)
    after = {p.name: (p.stat().st_size, p.stat().st_mtime_ns)
             for p in (ROOT / 'docs/downloads').iterdir()}
    assert result.returncode != 0
    assert 'No TIFF generated or published' in result.stderr
    assert before == after

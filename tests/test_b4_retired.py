import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_b4_cli_cannot_place_or_run_more_experiments():
    before = {p.name: p.stat().st_mtime_ns for p in (ROOT / 'docs/downloads').iterdir()}
    for command in ('surface', 'holdout', 'holdout2', 'final', 'audit'):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/b4_step.py'), command],
                                cwd=ROOT, capture_output=True, text=True)
        assert result.returncode != 0 and 'BLOCKED' in result.stderr
    assert before == {p.name: p.stat().st_mtime_ns for p in (ROOT / 'docs/downloads').iterdir()}


def test_b4_final_function_is_blocked():
    from scripts.b4_step import cmd_final
    with pytest.raises(RuntimeError, match='BLOCKED'):
        cmd_final()

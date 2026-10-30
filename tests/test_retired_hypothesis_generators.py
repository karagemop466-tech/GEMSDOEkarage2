"""Safety regressions for archived, negative hypothesis generators."""

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        (
            "generate_hypothesis_submission.py",
            "DISABLED: H-F is a negative research artifact",
        ),
        (
            "generate_hypothesis_submission_hg.py",
            "DISABLED: H-G is a retired research prototype",
        ),
    ],
)
def test_retired_generator_entrypoint_fails_closed(filename, expected):
    path = ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(f"retired_{filename[:-3]}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with pytest.raises(SystemExit, match=expected):
        module.main()

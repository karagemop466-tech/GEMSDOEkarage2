#!/usr/bin/env python3
"""Retired HK3 lane: no experiments, placement, audits or promotions may run.

The historical runner excluded registered witnesses and promoted a duplicate;
its lane also exhausted the experiment/time budget. The original scientific
implementation remains in Git history (parent commit cc1ed0d), and its saved
measurements remain under evidence/hk3/. Read-only independent rechecking is
available via scripts/recheck_hk3.py; it cannot generate a TIFF or grant a slot.
"""
from __future__ import annotations


MESSAGE = ("BLOCKED: HK3 is retired; the lane is stopped and its experiment budget is exhausted; "
           "no experiment, TIFF, audit overwrite, or promotion generated")


def _retired(*_args, **_kwargs):
    raise RuntimeError(MESSAGE)


# Block direct imports as well as the CLI, including helpers which placed dots
# or replaced the original registry evidence. Do not resurrect this lane.
cmd_features = cmd_e2 = cmd_bridge = cmd_e3 = cmd_audit = cmd_anchors = cmd_card = _retired
emit = _retired


def main() -> None:
    raise SystemExit(MESSAGE)


if __name__ == "__main__":
    main()

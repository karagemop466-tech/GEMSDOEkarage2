#!/usr/bin/env python3
"""Retired H-Rank-4 mock generator — intentionally cannot write a TIFF.

The previous implementation used a synthetic fault mask and an all-true
footprint, did not run holdout or leakage checks, and produced a raster that
fails the strict exterior check and the literal 3-px lattice-overlap stop.
See evidence/hr4-main-merge-reaudit-2026-10-29.json. This stub preserves the
historical entry-point name so automation fails closed instead of regenerating
or overwriting the research artifact.
"""
from __future__ import annotations

import sys

BLOCK_MESSAGE = (
    "No TIFF generated: H-Rank-4 v2 is retired; its synthetic-mask artifact "
    "fails strict exterior and literal uniqueness gates and has no holdout. "
    "Do not use or submit it."
)


def main() -> int:
    print(BLOCK_MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

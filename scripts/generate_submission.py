#!/usr/bin/env python3
"""Retired H-KARAGE-1 generator; deliberately fail closed.

The former implementation tried to steer placements around a registry control,
used an approximate lattice, lacked pre-placement novelty and holdout evidence,
and wrote directly into the public downloads directory. Its existing artifact
and receipts remain archived for reproducibility, not for competition use.

A future assigned lane must use the pinned shared template and satisfy the
protocol in README.md. This entry point must not place dots or publish a TIFF.
"""
import sys


def main() -> int:
    print("BLOCKED: retired generator lacks an assigned lane and required pre-placement, "
          "holdout and full-registry evidence. No TIFF generated or published. "
          "See README.md and evidence/run_card.json.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

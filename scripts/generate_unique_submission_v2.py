#!/usr/bin/env python3
"""Retired prototype; cannot generate or approve a GEMS submission.

The historical H-Rank-4 artifact was generated from a synthetic fault-mask
placeholder and an all-true footprint when organizer inputs were absent. Its
run card's ``promote`` verdict was retracted: HOLDOUT-DTI and canaries were not
run, and the uniqueness comparison covered only two local rasters after dot
placement. See ``evidence/quarantine/`` for the preserved TIFF, original
sidecars, and hash-bound countermand.

Do not resurrect or adapt this generator as a private pipeline. A future,
explicitly assigned lane must use the shared cached feature stack, evaluator,
writer, complete registry and all pre-placement/holdout gates.
"""


def main() -> int:
    raise SystemExit(
        "No TIFF generated: H-Rank-4 is retired and quarantined. Its historical "
        "PROMOTE decision was retracted; no authenticated-data holdout, leakage "
        "test, or complete pre-placement registry gate was run."
    )


if __name__ == "__main__":
    main()

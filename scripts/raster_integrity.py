"""Reject unbound GDAL sidecars in hash-bound local TIFF audits.

GDAL can use external .msk and .aux.xml files to change masks or georeferencing
without changing the TIFF's SHA-256. These audits pin the TIFF bytes only, so
external dependencies must not be silently consumed. Internal masks are fine.
This is not organizer authentication or a defense against concurrent filesystem
modification; run on a stable, trusted local copy.
"""
from pathlib import Path


def require_self_contained(dataset):
    primary = Path(dataset.name).resolve()
    extras = [name for name in dataset.files if Path(name).resolve() != primary]
    if extras:
        raise ValueError(f"Raster has external GDAL dependencies not covered by TIFF SHA-256: {extras}")

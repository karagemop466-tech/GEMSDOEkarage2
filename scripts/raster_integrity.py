"""Reject GeoTIFFs whose interpretation depends on unhashed companion files.

Receipts in the local audits hash the TIFF itself, not external GDAL masks,
auxiliary metadata or overviews. Refuse multi-file datasets instead of claiming
that one digest binds their contents. This is not organizer authentication.
"""
from pathlib import Path


def require_single_file_dataset(dataset, path: Path) -> None:
    primary = Path(path).resolve()
    files = {Path(name).resolve() for name in dataset.files}
    if files != {primary}:
        raise ValueError(f"Raster has external companion files not bound by TIFF hash: {path}")

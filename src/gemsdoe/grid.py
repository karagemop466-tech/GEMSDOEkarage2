"""Pinned competition grid, footprint, catalogue and feature stack loader.

Every constant is read from the SHA-pinned owner mirrors restored by
``scripts/restore_data.py`` (``registry/core_data_manifest.json``). They are
byte-verified mirrors of the login-walled DrivenData files and are NOT
organizer-authenticated.

Verified (2026-10-31, from restored bytes):
  sample_submission.tif  sha256 2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc
  labels.tif             sha256 7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093
  existing_faults.tif    sha256 7ba308cc...  (byte-identical to labels.tif)
  training_features.tif  sha256 4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5

Grid: EPSG:32611, 3730 x 3292, 100 m, transform (100, 0, 243350, 0, -100, 4508550).
Footprint (sample_submission finite): 5,167,373 px. Catalogue positives: 60,988 px.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio

EPSG = 32611
HEIGHT, WIDTH = 3730, 3292
TRANSFORM = (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
PIXEL_M = 100.0
NODATA = -3.4028234663852886e38

SHA = {
    "sample_submission.tif": "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc",
    "labels.tif": "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
    "existing_faults.tif": "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
    "training_features.tif": "4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5",
}
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = REPO_ROOT / ".cache" / "gems_data"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class Grid:
    footprint: np.ndarray      # bool (H, W) scored study area
    catalogue: np.ndarray      # bool (H, W) mapped faults inside footprint
    transform: tuple
    crs: str
    height: int = HEIGHT
    width: int = WIDTH
    data_dir: Path = DEFAULT_DATA

    @property
    def shape(self):
        return (self.height, self.width)

    @property
    def inside(self):
        """Non-catalogue footprint cells (where a new fault could be scored)."""
        return self.footprint & ~self.catalogue


def _check(src, name):
    if str(src.crs) != f"EPSG:{EPSG}":
        raise ValueError(f"{name}: CRS {src.crs} != EPSG:{EPSG}")
    if (src.height, src.width) != (HEIGHT, WIDTH):
        raise ValueError(f"{name}: shape {src.height}x{src.width} != {HEIGHT}x{WIDTH}")
    if tuple(float(v) for v in tuple(src.transform)[:6]) != TRANSFORM:
        raise ValueError(f"{name}: transform {tuple(src.transform)[:6]} != {TRANSFORM}")


def load_grid(data_dir: Path | str | None = None, verify: bool = True) -> Grid:
    d = Path(data_dir) if data_dir else DEFAULT_DATA
    if verify:
        for name, want in SHA.items():
            p = d / name
            if not p.is_file():
                raise FileNotFoundError(f"missing pinned input {p}; run scripts/restore_data.py")
            got = sha256_file(p)
            if got != want:
                raise ValueError(f"sha256 mismatch for {name}: {got} != {want}")
    with rasterio.open(d / "sample_submission.tif") as src:
        _check(src, "sample_submission.tif")
        sub = src.read(1)
        crs = str(src.crs)
    with rasterio.open(d / "existing_faults.tif") as src:
        _check(src, "existing_faults.tif")
        cat = src.read(1)
    foot = np.isfinite(sub)
    return Grid(footprint=foot, catalogue=(cat > 0) & foot, transform=TRANSFORM,
                crs=crs, data_dir=d)


def read_features(data_dir: Path | str | None = None) -> tuple[np.ndarray, list[str]]:
    """Return (bands, names) for the 19-band GeoDAWN stack, NaN outside data."""
    d = Path(data_dir) if data_dir else DEFAULT_DATA
    p = d / "training_features.tif"
    with rasterio.open(p) as src:
        _check(src, "training_features.tif")
        names = [src.tags(i + 1).get("band_name") or f"band{i + 1}" for i in range(src.count)]
        F = src.read().astype(np.float32)
    F[~np.isfinite(F)] = np.nan
    F[F <= NODATA / 2] = np.nan
    return F, names


def write_submission_tif(path, values, *, nan_outside: bool = False) -> dict:
    """Write a float32 single-band GeoTIFF on the pinned grid; re-read and report."""
    import rasterio
    from affine import Affine

    values = np.asarray(values, dtype=np.float32)
    if values.shape != (HEIGHT, WIDTH):
        raise ValueError(f"shape {values.shape} != {(HEIGHT, WIDTH)}")
    fin = np.isfinite(values)
    if (values[fin] < 0).any() or (values[fin] > 1).any():
        raise ValueError("finite values must be within [0, 1]")
    if not nan_outside and not fin.all():
        raise ValueError("all-finite mode requires finite values everywhere")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    profile = dict(driver="GTiff", height=HEIGHT, width=WIDTH, count=1, dtype="float32",
                   crs=f"EPSG:{EPSG}", transform=Affine(*TRANSFORM),
                   tiled=True, blockxsize=256, blockysize=256,
                   compress="deflate", predictor=2)
    if nan_outside:
        profile["nodata"] = float("nan")
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(values, 1)
        dst.set_band_description(1, "predicted_new_fault_probability")
    with rasterio.open(path) as src:
        a = src.read(1)
        info = dict(path=str(path), bytes=path.stat().st_size,
                    sha256=sha256_file(path), bands=src.count, dtype=src.dtypes[0],
                    height=src.height, width=src.width, crs=str(src.crs),
                    transform=[float(v) for v in tuple(src.transform)[:6]],
                    nodata=src.nodata,
                    positive_pixels=int((a > 0).sum()),
                    finite_pixels=int(np.isfinite(a).sum()))
        f = np.isfinite(a)
        info["min"] = float(a[f].min()) if f.any() else None
        info["max"] = float(a[f].max()) if f.any() else None
        info["all_finite"] = bool(f.all())
    return info


def json_default(o):
    if isinstance(o, Path):
        return str(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_, np.integer)):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(str(type(o)))

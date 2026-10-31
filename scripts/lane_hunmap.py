#!/usr/bin/env python3
"""H-UNMAP lane: geophysical fault-likelihood model with metric-gated emission.

Lane (single method paragraph, this session)
--------------------------------------------
*H-UNMAP (Unmapped-fault likelihood from geophysical edge/strain/radiometric
consensus, emitted under the official DTI marginal rule).*  Candidate fault
cells are scored by a spatially-blocked supervised model that uses **only
geophysical and geochemical evidence** (airborne magnetic edge/tilt/gradient
fields, isostatic-gravity gradients, geodetic strain-rate fields, basement
depth, seismicity-proximity fields and GeoDAWN gamma-ray alteration ratios) and
**never** any catalogue-derived feature, so the model cannot re-dig the mapped
fault catalogue.  The resulting fault-likelihood surface is converted into dots
by non-maximum suppression and then filtered by the *official metric's own
marginal rule* (a dot is kept only if its modelled probability of covering a
new truth cell clears the DTI break-even hit rate implied by alpha=0.2,
beta=0.8), with mapped-catalogue apron dots removed because mapped cells are
masked out of scoring.  Development uses the shared hide-and-recover
(catalogue) instrument; validation uses the independent public USGS
state-geologic-map (SGMC) off-catalogue fault set as an objective-matched
truth.

This script is the lane's only implementation; the shared template's
``gems57`` metric / holdout / writer are used unmodified.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "src"))

from gems57 import grid as ggrid          # noqa: E402
from gems57 import metric as gmetric       # noqa: E402

CACHE = ROOT / ".cache" / "hunmap"
FEAT_DIR = CACHE / "features"
DATA_DIR = ROOT / "data" / "bridge"
EXT_DIR = ROOT / ".cache" / "external"

LANE = "H-UNMAP"
EVALUATOR = "gems57-pooled-hide-v2"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _sobel_mag(a: np.ndarray) -> np.ndarray:
    from scipy import ndimage as ndi

    gy = ndi.sobel(a, axis=0, mode="nearest")
    gx = ndi.sobel(a, axis=1, mode="nearest")
    return np.hypot(gy, gx).astype(np.float32)


def _coherence(mag: np.ndarray, sigma: float = 3.0) -> np.ndarray:
    """Structure-tensor coherence (linearity) of a gradient-magnitude field."""
    from scipy import ndimage as ndi

    gy = ndi.sobel(mag, axis=0, mode="nearest")
    gx = ndi.sobel(mag, axis=1, mode="nearest")
    jxx = ndi.gaussian_filter(gx * gx, sigma, mode="nearest")
    jyy = ndi.gaussian_filter(gy * gy, sigma, mode="nearest")
    jxy = ndi.gaussian_filter(gx * gy, sigma, mode="nearest")
    num = np.sqrt((jxx - jyy) ** 2 + 4.0 * jxy * jxy)
    den = jxx + jyy
    out = np.zeros_like(num, dtype=np.float32)
    good = den > 1e-12
    out[good] = num[good] / den[good]
    return out


def _safe_log(a: np.ndarray) -> np.ndarray:
    out = np.full(a.shape, np.nan, dtype=np.float32)
    good = np.isfinite(a) & (a > 0)
    out[good] = np.log10(a[good])
    return out


def _zscore(a: np.ndarray, sigma: float = 8.0) -> np.ndarray:
    """Local z-score of a band (halo/anomaly contrast at ~800 m)."""
    from scipy import ndimage as ndi

    a = np.where(np.isfinite(a), a, 0.0).astype(np.float32)
    mu = ndi.gaussian_filter(a, sigma, mode="nearest")
    var = ndi.gaussian_filter(a * a, sigma, mode="nearest") - mu * mu
    sd = np.sqrt(np.maximum(var, 0.0))
    out = np.zeros_like(a)
    good = sd > 1e-9
    out[good] = (a[good] - mu[good]) / sd[good]
    return np.clip(out, -6.0, 6.0)


# --------------------------------------------------------------------------
# feature construction
# --------------------------------------------------------------------------
BAND_INDEX = {
    "rtp": 2,
    "tmi_hg": 3,
    "geod_2ndinv": 4,
    "iso_grav_anom_slope": 5,
    "tc": 6,
    "geod_shearrate": 7,
    "geod_dilaterate": 8,
    "tmi_vg": 9,
    "deq_n100a15": 10,
    "iso_grav_anom_vg": 11,
    "det_elev": 12,
    "iso_grav_anom": 13,
    "tmi": 14,
    "depth_to_base_surf": 15,
    "ieq_n100a15": 16,
    "cond_surf": 17,
    "iso_grav_anom_hg": 18,
    "det_elev_slope": 19,
}

# feature name -> (source band key, transform)
BAND_FEATURES = {
    "tmi_hg_abs": ("tmi_hg", "abs_log"),
    "tmi_vg_abs": ("tmi_vg", "abs_log"),
    "tc_abs": ("tc", "abs_log"),
    "rtp_grad": ("rtp", "grad_log"),
    "rtp_coh": ("rtp", "coh_grad"),
    "rtp_curv": ("rtp", "curv_abs_log"),
    "dem_grad": ("det_elev", "grad_log"),
    "dem_coh": ("det_elev", "coh_grad"),
    "dem_curv": ("det_elev", "curv_abs_log"),
    "dem_slope_abs": ("det_elev_slope", "abs_log"),
    "grav_hg_abs": ("iso_grav_anom_hg", "abs_log"),
    "grav_vg_abs": ("iso_grav_anom_vg", "abs_log"),
    "grav_slope_abs": ("iso_grav_anom_slope", "abs_log"),
    "shear_log": ("geod_shearrate", "log1p"),
    "dilate_log": ("geod_dilaterate", "log1p"),
    "inv_log": ("geod_2ndinv", "log1p"),
    "deq_log": ("deq_n100a15", "log"),
    "ieq_log": ("ieq_n100a15", "log1p"),
    "depth_base": ("depth_to_base_surf", "linear"),
    "cond_log": ("cond_surf", "log1p"),
    "tmi_log": ("tmi", "log1p_abs"),
}

RAD_FEATURES = {
    "rad_k_halo": ("K", "halo"),
    "rad_th_halo": ("Th", "halo"),
    "rad_u_halo": ("U", "halo"),
    "rad_thk_halo": ("ThK", "halo"),
}


def _band_transform(name: str, arr: np.ndarray) -> np.ndarray:
    if name == "abs_log":
        return np.log1p(np.abs(arr)).astype(np.float32)
    if name == "log1p":
        return np.log1p(np.maximum(arr, 0.0)).astype(np.float32)
    if name == "log1p_abs":
        return np.log1p(np.abs(arr)).astype(np.float32)
    if name == "log":
        return _safe_log(arr)
    if name == "grad_log":
        return np.log1p(_sobel_mag(arr)).astype(np.float32)
    if name == "coh_grad":
        return _coherence(_sobel_mag(arr)).astype(np.float32)
    if name == "curv_abs_log":
        from scipy import ndimage as ndi

        lap = ndi.laplace(arr, mode="nearest")
        return np.log1p(np.abs(lap)).astype(np.float32)
    if name == "linear":
        return arr.astype(np.float32)
    raise ValueError(f"unknown transform {name}")


def build_features(force: bool = False) -> dict:
    """Compute every feature band once and memoise it on disk."""
    import rasterio
    from scipy import ndimage as ndi

    FEAT_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = CACHE / "features.json"
    if meta_path.exists() and not force:
        meta = json.loads(meta_path.read_text())
        if all((FEAT_DIR / f"{k}.npy").exists() for k in meta["features"]):
            log(f"features cached ({len(meta['features'])} bands)")
            return meta

    src = DATA_DIR / "training_features.tif"
    nodata = -3.4028234663852886e+38
    features: dict[str, str] = {}
    want = sorted({v[0] for v in BAND_FEATURES.values()})

    with rasterio.open(src) as ds:
        height, width = ds.height, ds.width
        for key in want:
            idx = BAND_INDEX[key]
            arr = ds.read(idx).astype(np.float32)
            arr[arr <= nodata / 2] = np.nan
            for fname, (bkey, tr) in BAND_FEATURES.items():
                if bkey != key:
                    continue
                out = _band_transform(tr, arr)
                path = FEAT_DIR / f"{fname}.npy"
                np.save(path, out)
                features[fname] = str(path.relative_to(ROOT))
                log(f"feature {fname} written")
            del arr

    # radiometric gamma-ray channels (GeoDAWN area-2 mosaic, 100 m, uint8)
    rad_path = EXT_DIR / "24_geodawn_rad_u8.tif"
    if rad_path.exists():
        with rasterio.open(rad_path) as ds:
            names = list(ds.descriptions) or ["K", "Th", "U", "TC"]
            log(f"radiometric bands: {names}")
            bands = {n: ds.read(i + 1).astype(np.float32) for i, n in enumerate(names[:4])}
        k = bands.get("K")
        th = bands.get("Th")
        u = bands.get("U")
        for fname, (chan, mode) in RAD_FEATURES.items():
            if chan == "ThK":
                if th is None or k is None:
                    continue
                a = th / np.maximum(k, 1e-6)
            else:
                a = bands.get(chan)
                if a is None:
                    continue
            halo = _zscore(a, 8.0)
            path = FEAT_DIR / f"{fname}.npy"
            np.save(path, halo)
            features[fname] = str(path.relative_to(ROOT))
            log(f"feature {fname} written")
        del bands

    meta = {
        "lane": LANE,
        "features": features,
        "band_index": BAND_INDEX,
        "radiometric_source": "GEMSDOE24 data/external/geodawn_rad_u8.tif (GeoDAWN area-2 mosaic, uint8)",
        "shape": [height, width],
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    return meta


def load_feature_stack(names: list[str]) -> np.ndarray:
    """Return an (n_features, H, W) float32 memmap-backed stack."""
    import numpy.lib.format as npformat

    arrays = []
    for n in names:
        arrays.append(np.load(FEAT_DIR / f"{n}.npy", mmap_mode="r"))
    return np.stack(arrays, axis=0)


# --------------------------------------------------------------------------
# truth / instrument helpers
# --------------------------------------------------------------------------
def load_grid() -> ggrid.Grid:
    return ggrid.load_grid(DATA_DIR)


def sgmc_truth(off_catalogue_px: int = 3, source: str = "24") -> np.ndarray:
    """Public USGS state-geologic-map (SGMC) fault pixels, off-catalogue."""
    import rasterio
    from scipy import ndimage as ndi

    path = EXT_DIR / f"{source}_derived_sgmc_faults_100m_u8.tif"
    with rasterio.open(path) as ds:
        sg = ds.read(1) > 0
    g = load_grid()
    far = ndi.distance_transform_edt(~g.catalogue) > off_catalogue_px
    return sg & g.footprint & far


def dti_of(pred_bool: np.ndarray, truth: np.ndarray, known: np.ndarray,
           valid: np.ndarray) -> dict:
    """Exact DTI with the shared template's metric (alpha .2, beta .8, 300 m)."""
    active = np.asarray(valid, bool) & ~np.asarray(known, bool)
    p = np.where(active, np.asarray(pred_bool, bool), False)
    g = active & np.asarray(truth, bool)
    if not g.any():
        return dict(dti=0.0, tpw=0.0, fpw=0.0, fnw=0.0, n_truth=0, n_emitted=int(p.sum()))
    covers, q, _ = gmetric.max_cover(p.astype(np.float64), g)
    tpw = float(covers.sum())
    fpw = float((p.astype(np.float64) * (1.0 - q)).sum())
    fnw = float(g.sum()) - tpw
    dti = tpw / (tpw + gmetric.ALPHA * fpw + gmetric.BETA * fnw + gmetric.EPS)
    return dict(dti=float(dti), tpw=tpw, fpw=fpw, fnw=fnw,
                n_truth=int(g.sum()), n_emitted=int(p.sum()))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=["features", "sgmc-truth"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    if args.command == "features":
        meta = build_features(force=args.force)
        log(json.dumps({"n_features": len(meta["features"])}, indent=2))
    elif args.command == "sgmc-truth":
        t = sgmc_truth()
        g = load_grid()
        log(f"SGMC off-catalogue truth pixels: {int(t.sum())} "
            f"(catalogue {int(g.catalogue.sum())}, footprint {int(g.footprint.sum())})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

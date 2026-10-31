"""Feature engineering for the structural-habitat lane (memory-disciplined).

Physical premise
----------------
The 19 raw GeoDAWN bands are smooth regional fields; at the pixel level their
values on mapped faults differ from background by |z| <= 0.29 (measured 2026-10-31,
see evidence/).  The *fault* information in potential-field and topographic data
is carried by the **derivatives and their lineaments**, not by amplitudes:

* horizontal-gradient maxima   -> steep contacts / offset source bodies
* analytic-signal amplitude    -> depth-to-source edges (magnetic and gravity)
* tilt-angle magnitude         -> edge loci, comparatively depth-independent
* ridge strength (2nd directional derivative along the gradient) -> lineaments
* basement-depth gradient      -> buried steps in the sediment/basement interface
* detrended-elevation slope    -> range fronts, which are frequently faults

Everything is computed from the 19-band stack, plus a *visible* fault mask
supplied per holdout fold (never the withheld segments), so no catalogue
information can cross a fold boundary.

The stack is stored **footprint-only and uint8-quantised** (~1 byte/feature/pixel)
because the full 3730x3292 float32 stack for ~60 features exceeds the sandbox RAM.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

NOD = -3.4028234663852886e38


def fill_nan(b: np.ndarray) -> np.ndarray:
    b = np.asarray(b, dtype=np.float32)
    bad = ~np.isfinite(b) | (b <= NOD / 2)
    if bad.any():
        m = float(np.nanmedian(b[~bad])) if (~bad).any() else 0.0
        b = np.where(bad, m, b).astype(np.float32)
    return b


def robust01(b: np.ndarray, mask: np.ndarray | None = None, lo=1.0, hi=99.0) -> np.ndarray:
    """Percentile-clipped [0,1] rescaling; robust to the heavy tails in these fields."""
    b = b.astype(np.float32)
    v = b[mask] if mask is not None else b.ravel()
    a, c = np.percentile(v, [lo, hi])
    if not np.isfinite(a) or not np.isfinite(c) or c <= a:
        a, c = float(np.min(v)), float(np.max(v))
        if c <= a:
            return np.zeros_like(b)
    return np.clip((b - a) / (c - a), 0.0, 1.0).astype(np.float32)


def gm(b, s):
    b = fill_nan(b)
    gy = ndimage.gaussian_filter(b, s, order=[1, 0], mode="nearest")
    gx = ndimage.gaussian_filter(b, s, order=[0, 1], mode="nearest")
    return np.hypot(gy, gx).astype(np.float32)


def ridge(b, s):
    """-d2/ds2 along the gradient direction, positive on crests/ridges."""
    b = fill_nan(b)
    gy = ndimage.gaussian_filter(b, s, order=[1, 0], mode="nearest")
    gx = ndimage.gaussian_filter(b, s, order=[0, 1], mode="nearest")
    n = np.hypot(gy, gx) + 1e-12
    uy, ux = gy / n, gx / n
    byy = ndimage.gaussian_filter(b, s, order=[2, 0], mode="nearest")
    bxx = ndimage.gaussian_filter(b, s, order=[0, 2], mode="nearest")
    bxy = ndimage.gaussian_filter(b, s, order=[1, 1], mode="nearest")
    d2 = uy * uy * byy + 2.0 * uy * ux * bxy + ux * ux * bxx
    return np.maximum(-d2, 0.0).astype(np.float32)


def salient(b, size=7):
    """Excess over a large mean filter: how much a pixel stands above its setting."""
    b = fill_nan(b)
    mean = ndimage.uniform_filter(b, size=size, mode="nearest")
    return np.maximum(b - mean, 0.0).astype(np.float32)


def thin(f, size=7):
    f = fill_nan(f)
    mx = ndimage.maximum_filter(f, size=size, mode="nearest")
    return np.where((f >= mx) & (f > 0), f, 0.0).astype(np.float32)


def distance_to(mask: np.ndarray) -> np.ndarray:
    return ndimage.distance_transform_edt(~np.asarray(mask, bool)).astype(np.float32)


# Bands carrying structural geometry rather than a smooth regional level.
DERIV_BANDS = ("tmi", "mag_anom", "iso_grav_anom", "det_elev",
               "depth_to_base_surf", "cond_surf")
SCALES = (1.0, 2.0, 4.0)


def build_stack(F: np.ndarray, names: list[str], footprint: np.ndarray,
                visible_faults: np.ndarray | None = None,
                deriv_bands=DERIV_BANDS, scales=SCALES,
                include_visible: bool = True) -> tuple[np.ndarray, list[str]]:
    """Return (X, feat_names) with X uint8, shape (n_footprint_pixels, n_features)."""
    idx = {n: i for i, n in enumerate(names)}
    cols: list[np.ndarray] = []
    fnames: list[str] = []
    flat = footprint.reshape(-1)

    def add(arr: np.ndarray, name: str) -> None:
        q = np.round(np.clip(arr, 0.0, 1.0) * 255.0).astype(np.uint8)
        cols.append(q.reshape(-1)[flat])
        fnames.append(name)
        del q

    for n in names:
        add(robust01(F[idx[n]], footprint), f"raw:{n}")

    for n in deriv_bands:
        if n not in idx:
            continue
        b = F[idx[n]]
        for s in scales:
            add(robust01(gm(b, s), footprint), f"gm{s:g}:{n}")
            add(robust01(ridge(b, s), footprint), f"ridge{s:g}:{n}")
        add(robust01(salient(b, 7), footprint), f"salient:{n}")

    if "tmi_hg" in idx and "tmi_vg" in idx:
        vg, hg = fill_nan(F[idx["tmi_vg"]]), fill_nan(F[idx["tmi_hg"]])
        asa = np.hypot(hg, vg)
        add(robust01(asa, footprint), "asa:mag")
        add(robust01(thin(asa, 7), footprint), "worm:mag")
        add(robust01(np.abs(np.arctan2(vg, np.abs(hg) + 1e-12)), footprint), "tiltmag:mag")
    if "iso_grav_anom_hg" in idx and "iso_grav_anom_vg" in idx:
        gh = fill_nan(F[idx["iso_grav_anom_hg"]])
        gv = fill_nan(F[idx["iso_grav_anom_vg"]])
        gasa = np.hypot(gh, gv)
        add(robust01(gasa, footprint), "asa:grav")
        add(robust01(thin(gasa, 7), footprint), "worm:grav")

    if include_visible and visible_faults is not None:
        d = distance_to(visible_faults)
        add(robust01(np.log1p(d), footprint), "vis:logdist")
        add(robust01(salient(-d, 21), footprint), "vis:apron_salient")
        dens = ndimage.uniform_filter(visible_faults.astype(np.float32), size=21, mode="nearest")
        add(robust01(dens, footprint), "vis:density21")

    X = np.stack(cols, axis=1)
    return X, fnames

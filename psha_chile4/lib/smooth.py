import numpy as np
import pandas as pd

from lib.dc import hav


def kernel(lon, lat, nn, floor):
    """Adaptive bandwidth: distance to the nn-th neighbour, at least floor km."""
    if len(lon) < 2:
        raise ValueError("need at least 2 events")
    d = np.sort(hav(lon[:, None], lat[:, None], lon[None, :], lat[None, :]), axis=1)
    return np.maximum(d[:, min(nn, len(lon) - 1)], floor)


def field(elon, elat, w, h, glon, glat, power, dmax):
    """
    Smoothed rate on grid cells: each event spreads its weight with
    K = 1 / (r^2 + h^2)^power, normalized over the cells within dmax.
    Cells not in the grid receive nothing, so masking cells before this
    call renormalizes the rate onto the remaining domain.
    """
    out = np.zeros(len(glon))
    for i in range(len(elon)):
        r = hav(elon[i], elat[i], glon, glat)
        m = r <= dmax
        if not m.any():
            continue
        k = 1.0 / (r[m] ** 2 + h[i] ** 2) ** power
        out[m] += k * (w[i] / k.sum())
    return out


def slab_top(glon, glat, path):
    """
    Depth (km, positive down) of the nearest Slab2 node to each cell and the
    distance to that node (km).
    """
    from scipy.spatial import cKDTree
    s = pd.read_csv(path, header=None, names=["lon", "lat", "depth"]).dropna()
    s["lon"] = np.where(s["lon"] > 180, s["lon"] - 360, s["lon"])
    xyz = lambda lo, la: np.column_stack([np.cos(np.radians(la)) * np.cos(np.radians(lo)),
                                          np.cos(np.radians(la)) * np.sin(np.radians(lo)),
                                          np.sin(np.radians(la))])
    d, i = cKDTree(xyz(s["lon"].to_numpy(), s["lat"].to_numpy())).query(xyz(glon, glat))
    return -s["depth"].to_numpy()[i], 2 * 6371.0 * np.arcsin(np.clip(d / 2, 0, 1))


def edges(mmin, mmax, dm):
    return np.round(mmin + dm * np.arange(int(np.ceil((mmax - mmin) / dm - 1e-9)) + 1), 6)


def tgr_bins(shape, rate, b, e, mmax):
    """
    Per-cell incremental rates of the GR with N(>=e[0]) = rate, cut at mmax
    without renormalization (total = rate * (1 - 10^-b(mmax - e[0]))), spread
    by shape.

    Returns
    -------
    array (n_cells, n_bins)
    """
    lo, hi = np.minimum(e[:-1], mmax), np.minimum(e[1:], mmax)
    frac = 10 ** (-b * (lo - e[0])) - 10 ** (-b * (hi - e[0]))
    return (shape / shape.sum() * rate)[:, None] * frac[None, :]


def write(cells, rb, e, path):
    df = cells.copy()
    for i, (lo, hi) in enumerate(zip(e[:-1], e[1:])):
        df[f"rate_M{lo:.2f}_{hi:.2f}"] = rb[:, i]
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def read(path):
    df = pd.read_csv(path)
    cols = [k for k in df.columns if k.startswith("rate_M")]
    lo = np.array([float(k.split("_")[1][1:]) for k in cols])
    hi = float(cols[-1].split("_")[2])
    return df, df[cols].to_numpy(), np.append(lo, hi)

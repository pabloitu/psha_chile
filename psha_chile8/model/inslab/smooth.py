"""Adaptive power-law kernel of Helmstetter et al. (2007) for the in-slab rate pattern (S2).

Ported from psha_chile7/lib/smooth.py (`kernel`, `field`), which gives the same field as `adaptive_radii` and
`compute_ssm` of smoothed_seismicity/ssm/smoothing.py (tests/test_smooth.py): K = 1 / (r² + d²)^1.5, d the distance
of the event to its n-th nearest neighbour, at least H_MIN km; each event spreads its weight over the cells within
D_MAX km, normalised to its weight, so that the cells of a domain hold the whole weight of every event that reaches
them. The calibration score is the spatial Poisson log-likelihood of the CSEP S-test (`optimize_kernel` of ssm).
"""
import numpy as np
from scipy.spatial import cKDTree

R = 6371.0
POWER, H_MIN, D_MAX = 1.5, 5.0, 500.0


def hav(lon1, lat1, lon2, lat2):
    p = np.pi / 180
    a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def xyz(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


def bandwidth(lon, lat, n, hmin=H_MIN):
    """Distance of every event to its n-th nearest other event (km), at least hmin; hmin with fewer than two events."""
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    if lon.size < 2:
        return np.full(lon.size, float(hmin))
    p = xyz(lon, lat)
    c = cKDTree(p).query(p, k=min(n, lon.size - 1) + 1)[0][:, -1]
    return np.maximum(2 * R * np.arcsin(np.clip(c / 2, 0, 1)), hmin)


def field(elon, elat, w, h, glon, glat, power=POWER, dmax=D_MAX, chunk=400):
    """
    Smoothed weight on the cells.

    Parameters
    ----------
    elon, elat, w, h : arrays
        Epicentres, weights and bandwidths (km) of the events.
    glon, glat : arrays
        Cells of the domain; cells not passed receive nothing.

    Returns
    -------
    array (cells,)
        Sum over the events of w K / ΣK, K = 1 / (r² + h²)^power over the cells within dmax.
    """
    elon, elat, w, h = (np.asarray(v, float) for v in (elon, elat, w, h))
    glon, glat = np.asarray(glon, float), np.asarray(glat, float)
    out = np.zeros(glon.size)
    for a in range(0, elon.size, chunk):
        s = slice(a, a + chunk)
        r = hav(elon[s, None], elat[s, None], glon[None, :], glat[None, :])
        k = np.where(r <= dmax, 1.0 / (r ** 2 + h[s, None] ** 2) ** power, 0.0)
        t = k.sum(1, keepdims=True)
        out += np.divide(k * w[s, None], t, out=np.zeros_like(k), where=t > 0).sum(0)
    return out


def cell_of(lon, lat, glon, glat):
    """Index of the nearest cell to every point."""
    return cKDTree(xyz(glon, glat)).query(xyz(np.asarray(lon, float), np.asarray(lat, float)))[1]


def loglik(p, obs):
    """S-test log-likelihood of the observed counts per cell under the pattern p scaled to the observed total (the
    count-factorial term left out): -N + Σ n_j log(N p_j)."""
    n = float(obs.sum())
    return float(-n + np.sum(obs * np.log(n * p / p.sum() + 1e-300)))


def calibrate(train, test, glon, glat, candidates):
    """
    Log-likelihood of the test events for each candidate n, the pattern built from the training events.

    train, test : DataFrames with lon, lat, w (class weight). Test events count in their nearest cell.
    Returns a list of (n, log-likelihood).
    """
    obs = np.bincount(cell_of(test.lon, test.lat, glon, glat), test.w.to_numpy(), minlength=glon.size)
    out = []
    for n in candidates:
        h = bandwidth(train.lon, train.lat, n)
        out.append((n, loglik(field(train.lon, train.lat, train.w, h, glon, glat), obs)))
    return out


def first_max(n, ll):
    """The n of the first local maximum of the log-likelihood, from small n."""
    i = np.argsort(n)
    n, ll = np.asarray(n)[i], np.asarray(ll, float)[i]
    up, down = np.r_[True, ll[1:] >= ll[:-1]], np.r_[ll[:-1] >= ll[1:], True]
    return n[np.argmax(up & down)]

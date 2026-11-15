"""Smoothed seismicity with the adaptive power-law kernel of Helmstetter et al. (2007), and its calibration on a
train / test split.

Kernel and field ported from psha_chile7/lib/smooth.py: K = 1 / (r^2 + d^2)^1.5, d the distance of an event to its
n-th nearest neighbour (at least 5 km), cut at 500 km, each event normalised over the grid cells it reaches.
smoothed_seismicity/ssm/smoothing.py (compute_ssm) gives the same field (tests). Its optimize_kernel puts every test
event in the nearest grid node, also when the event lies outside the grid, and counts events, not weights; here a
test event counts only inside a cell, with its class weight.
"""
import numpy as np
from scipy.spatial import cKDTree

R = 6371.0
POWER, FLOOR, DMAX = 1.5, 5.0, 500.0


def hav(lon1, lat1, lon2, lat2):
    p = np.pi / 180
    a = np.sin((lat1 - lat2) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon1 - lon2) * p / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def radii(lon, lat, n, floor=FLOOR):
    """Bandwidth of every event: distance to its n-th nearest other event, at least floor km."""
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    if len(lon) < 2:
        return np.full(len(lon), float(floor))
    d = np.sort(hav(lon[:, None], lat[:, None], lon[None, :], lat[None, :]), axis=1)
    return np.maximum(d[:, min(n, len(lon) - 1)], floor)


def dist(elon, elat, glon, glat):
    """Distances (km) from every event to every cell, (n_events, n_cells)."""
    return hav(np.asarray(elon, float)[:, None], np.asarray(elat, float)[:, None], np.asarray(glon)[None, :],
               np.asarray(glat)[None, :])


def field(D, w, h, power=POWER, dmax=DMAX, kind="power"):
    """
    Smoothed rate on the cells: every event spreads its weight w with K = 1 / (r^2 + h^2)^power (kind "power") or
    K = exp(-r^2 / 2 h^2) (kind "gauss") over the cells within dmax, normalised there, so the field holds the summed
    weight of the events that reach a cell.

    Parameters
    ----------
    D : array (n_events, n_cells)
        Distances, from `dist`.
    w, h : arrays (n_events,)
        Weights and bandwidths (km).
    """
    h = np.asarray(h, float)[:, None]
    k = np.exp(-D ** 2 / (2 * h ** 2)) if kind == "gauss" else 1.0 / (D ** 2 + h ** 2) ** power
    k = np.where(D <= dmax, k, 0.0)
    s = k.sum(axis=1)
    ok = s > 0
    return (k[ok] * (np.asarray(w, float)[ok] / s[ok])[:, None]).sum(axis=0)


def cells(glon, glat, lon, lat, step=0.1):
    """Cell of a regular grid (spacing step) holding each point, -1 outside the grid."""
    t = cKDTree(np.c_[glon, glat])
    _, i = t.query(np.c_[lon, lat])
    ok = (np.abs(np.asarray(glon)[i] - lon) <= step / 2 + 1e-9) & (np.abs(np.asarray(glat)[i] - lat) <= step / 2 + 1e-9)
    return np.where(ok, i, -1)


def loglik(rate, idx, w):
    """
    Spatial Poisson log-likelihood of the test events (CSEP S-test): the forecast scaled to the observed count,
    without the term of the counts alone. idx are the cells of the test events (-1 outside), w their weights.
    """
    ok = idx >= 0
    n = np.bincount(idx[ok], np.asarray(w, float)[ok], minlength=rate.size)
    N = n.sum()
    lam = N * rate / rate.sum()
    u = n > 0
    if np.any(lam[u] <= 0):
        return -np.inf
    return float((n[u] * np.log(lam[u])).sum() - N)


def calibrate(train, test, glon, glat, cands, power=POWER, floor=FLOOR, dmax=DMAX, kind="power"):
    """
    Log-likelihood of the test events for every candidate n, the forecast smoothed from the training events with
    equal weights times their class weight.

    train, test : (lon, lat, w) arrays.

    Returns
    -------
    list of (n, log-likelihood)
    """
    D = dist(train[0], train[1], glon, glat)
    idx = cells(glon, glat, test[0], test[1])
    out = []
    for n in cands:
        f = field(D, train[2], radii(train[0], train[1], n, floor), power, dmax, kind)
        out.append((n, loglik(f, idx, test[2])))
    return out

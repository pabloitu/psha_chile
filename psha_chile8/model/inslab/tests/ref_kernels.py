"""Copies of the two kernel codes, for the port test only (not imported anywhere else).

psha: psha_chile7/lib/smooth.py, kernel and field (Oct 2026), with hav from psha_chile7/lib/dc.py.
ssm: /data/PyCharmProjects/smoothed_seismicity/ssm/smoothing.py, adaptive_radii and compute_ssm (May 2026), with
gc_dist from ssm/distances.py; prints removed, DataFrame inputs kept.
"""
import numpy as np


def hav(lon1, lat1, lon2, lat2):
    p = np.pi / 180
    a = (np.sin((lat1 - lat2) * p / 2) ** 2
         + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon1 - lon2) * p / 2) ** 2)
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def psha_kernel(lon, lat, nn, floor):
    if len(lon) < 2:
        return np.full(len(lon), float(floor))
    d = np.sort(hav(lon[:, None], lat[:, None], lon[None, :], lat[None, :]), axis=1)
    return np.maximum(d[:, min(nn, len(lon) - 1)], floor)


def psha_field(elon, elat, w, h, glon, glat, power, dmax):
    out = np.zeros(len(glon))
    for i in range(len(elon)):
        r = hav(elon[i], elat[i], glon, glat)
        m = r <= dmax
        if not m.any():
            continue
        k = 1.0 / (r[m] ** 2 + h[i] ** 2) ** power
        if k.sum() <= 0:
            continue
        out[m] += k * (w[i] / k.sum())
    return out


def gc_dist(lon1, lat1, lon2, lat2):
    lo1, la1, lo2, la2 = np.deg2rad(lon1), np.deg2rad(lat1), np.deg2rad(lon2), np.deg2rad(lat2)
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2.0 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def ssm_adaptive_radii(events, n=25, min_km=5.0):
    lon, lat = events["lon"].to_numpy(float), events["lat"].to_numpy(float)
    d = np.sort(gc_dist(lon[:, None], lat[:, None], lon[None, :], lat[None, :]), axis=1)
    return np.maximum(d[:, min(n, len(events) - 1)], min_km)


def ssm_compute(events, grid, weights, radii, max_dist_km=500.0, power=1.5):
    lon_g, lat_g = grid["lon"].to_numpy(float), grid["lat"].to_numpy(float)
    lon_e, lat_e = events["lon"].to_numpy(float), events["lat"].to_numpy(float)
    rates = np.zeros(len(grid))
    for i in range(len(events)):
        w, d = weights[i], radii[i]
        if not (np.isfinite(w) and np.isfinite(d)) or w == 0.0:
            continue
        r = gc_dist(lon_e[i], lat_e[i], lon_g, lat_g)
        m = r <= max_dist_km
        if not np.any(m):
            continue
        k = 1.0 / np.maximum(r[m] ** 2 + d ** 2, 1e-12) ** power
        s = k.sum()
        if s <= 0 or not np.isfinite(s):
            continue
        rates[m] += k * (w / s)
    return rates

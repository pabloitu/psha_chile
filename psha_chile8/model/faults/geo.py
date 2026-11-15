"""Geodesic helpers for fault traces: densified points, lengths, distances between traces."""
import numpy as np
from pyproj import Geod
from scipy.spatial import cKDTree

GEOD = Geod(ellps="WGS84")
R = 6371.0


def lines(g):
    """The parts of a LineString or MultiLineString as arrays of (lon, lat)."""
    parts = g.geoms if g.geom_type == "MultiLineString" else [g]
    return [np.asarray(p.coords)[:, :2] for p in parts]


def length(g):
    """Geodesic length of a trace on WGS84, km."""
    return sum(GEOD.line_length(c[:, 0], c[:, 1]) for c in lines(g)) / 1e3


def dense(g, step=0.1):
    """
    Points along a trace at most `step` km apart, and the length each point stands for.

    Returns
    -------
    (array, array)
        (n, 2) lon, lat and (n,) weights in km that sum to the trace length.
    """
    pts, w = [], []
    for c in lines(g):
        for (x0, y0), (x1, y1) in zip(c[:-1], c[1:]):
            d = GEOD.line_length([x0, x1], [y0, y1]) / 1e3
            n = max(int(np.ceil(d / step)), 1)
            t = (np.arange(n) + 0.5) / n
            pts.append(np.c_[x0 + t * (x1 - x0), y0 + t * (y1 - y0)])
            w.append(np.full(n, d / n))
    if not pts:
        return np.empty((0, 2)), np.empty(0)
    return np.vstack(pts), np.concatenate(w)


def xyz(p):
    """Lon, lat to Cartesian km on a sphere of radius R; chords equal arcs to 1e-6 at fault distances."""
    lo, la = np.radians(p[:, 0]), np.radians(p[:, 1])
    return R * np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


def tree(g, step=0.1):
    return cKDTree(xyz(dense(g, step)[0]))


def near(a, b, d, step=0.1):
    """Share of the length of trace a that lies within d km of trace b (b a geometry or a cKDTree)."""
    p, w = dense(a, step)
    t = b if isinstance(b, cKDTree) else tree(b, step)
    dist, _ = t.query(xyz(p), distance_upper_bound=d + step)
    return float(w[dist <= d].sum() / w.sum())


def dist_km(g, lon, lat, step=0.1):
    """Shortest distance from a point to a trace, km."""
    return float(tree(g, step).query(xyz(np.array([[lon, lat]])))[0][0])


def azimuth(g):
    """Azimuth of the line from the first to the last point of the trace, degrees."""
    c = np.vstack(lines(g))
    return GEOD.inv(c[0, 0], c[0, 1], c[-1, 0], c[-1, 1])[0] % 360.0


def trace(geoms, step=2.0, tol=0.5):
    """
    One simplified trace through a set of strands: points binned every `step` km along their main axis, the median
    across the axis in each bin, the line through the bin medians simplified to `tol` km.

    Returns
    -------
    LineString
    """
    from shapely.geometry import LineString
    p = np.vstack([dense(g, 0.25)[0] for g in geoms])
    lo0, la0 = p.mean(axis=0)
    k = np.cos(np.radians(la0))
    xy = np.c_[(p[:, 0] - lo0) * 111.195 * k, (p[:, 1] - la0) * 111.195]
    u = np.linalg.svd(xy - xy.mean(axis=0), full_matrices=False)[2]
    s, t = xy @ u[0], xy @ u[1]
    b = np.floor((s - s.min()) / step).astype(int)
    q = np.array([[np.median(s[b == i]), np.median(t[b == i])] for i in np.unique(b)])
    if len(q) == 1:
        q = np.r_[q, q]
    q[0, 0], q[-1, 0] = s.min(), s.max()
    line = LineString(q[:, :1] * u[0] + q[:, 1:] * u[1]).simplify(tol)
    c = np.asarray(line.coords)
    return LineString(np.c_[c[:, 0] / (111.195 * k) + lo0, c[:, 1] / 111.195 + la0])

"""In-slab depth model (plan C14): the distance of well-located in-slab events below the Slab2 top, spread onto the
grid cells with the kernel of the in-slab rate pattern. Per cell: the seismogenic zone from the slab top to the
fraction of the Slab2 thickness that holds 95 % of all events, three equal layers inside it, the share of the events
in each layer and their median depth in it.

Inputs are the dated copies in psha_chile8/data and the frozen catalogue 2026-11-16c (depth runs up to 2026-11-16b read 2026-11-16, 2026-11-15e read 2026-11-14c). Entry scripts: bench.py (step 1),
run.py (steps 2-4).
"""
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT.parent
DATA = ROOT / "data"
sys.path[:0] = [str(ROOT / "catalog"), str(ROOT)]
import classify as C  # noqa: E402

CAT = ROOT / "catalog" / "frozen" / "2026-11-17g" / "catalog_2026-11-17g.csv"
LINKS = ROOT / "catalog" / "merged" / "links_2026-11-11.csv"
SRC = ROOT / "catalog" / "sources"
RH = DATA / "riedel_hornig_primary_2026-11-14.csv"
SLAB = {k: DATA / f"sam_slab2_{k}_02.23.18_2026-11-15.xyz" for k in ("dep", "thk", "unc")}
GRID = DATA / "inslab_grid_01_2026-11-15.csv"
OLD_FRAC = (0.30, 0.65)
CHILE = REPO / "data" / "shapefiles" / "chile.shp"
R_EARTH = 6371.0

# Riedel-Hornig: completeness Ml 2.5 (their section 3); depth error at most SIG_MAX km
RH_ML = 2.5
SIG_MAX = 5.0
# matching (A3 rules, simple form)
DT, DD = 10.0, 50.0
FLAT = (-33.0, -27.0)
# kernel of the in-slab rate pattern (psha_chile7 intraslab/config.py, DECISIONS In-slab): 1 / (r² + h²)^POWER, h the
# distance to the NN-th neighbour, at least H_MIN km, cells within D_MAX km
NN, POWER, H_MIN, D_MAX = 25, 1.5, 5.0, 500.0
# zone and layers: lower depth at the fraction of the Slab2 thickness below the top that holds Q_LOW % of all events
# (one number for the margin); three equal layers; hypocentre at the layer middle where the layer holds fewer than
# MIN_LAYER events (effective number)
Q_LOW, MIN_LAYER, EDGE = 95.0, 5.0, 0.5
BINS = np.arange(-50.0, 201.0, 1.0)


# inputs
@lru_cache(None)
def slab_grids():
    from scipy.interpolate import RegularGridInterpolator
    from scipy.spatial import cKDTree
    g = {}
    for k, f in SLAB.items():
        a = pd.read_csv(f, header=None, names=["x", "y", "z"])
        z = a.pivot(index="y", columns="x", values="z")
        g[k] = RegularGridInterpolator((z.index.to_numpy(), z.columns.to_numpy()), z.to_numpy(), bounds_error=False)
        g[k + "_v"] = a.z.to_numpy()
    ok = np.isfinite(g["dep_v"])
    g["ok"] = ok
    g["tree"] = cKDTree(np.c_[a.x.to_numpy()[ok] * np.cos(np.radians(30)), a.y.to_numpy()[ok]])
    return g


def slab_at(lon, lat):
    """Slab2 top (km, positive down), thickness and top uncertainty at the points: bilinear, and the nearest node within
    C.SLAB_KM at the edge of the model (the rule of catalog/classify.py). NaN where there is no slab."""
    g = slab_grids()
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    p = np.c_[lat, np.mod(lon, 360)]
    d, j = g["tree"].query(np.c_[np.mod(lon, 360) * np.cos(np.radians(30)), lat])
    near = d * 111.195 <= C.SLAB_KM
    out = []
    for k in ("dep", "thk", "unc"):
        v = g[k](p)
        out.append(np.where(np.isfinite(v), v, np.where(near, g[k + "_v"][g["ok"]][j], np.nan)))
    return -out[0], out[1], out[2]


def catalog():
    c = pd.read_csv(CAT, low_memory=False)
    c["t"] = C.tsec(c.time)
    return c


def riedel():
    r = pd.read_csv(RH)
    r["t"] = C.tsec(r.Date + "T" + r.Time)
    r = r.dropna(subset=["t"]).sort_values("t").reset_index(drop=True)
    r["z"], r["sig"] = -r.Dep, r.Dep_Error
    return r


def xyz(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return R_EARTH * np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


def hav(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lo2 - lo1) / 2) ** 2
    return 2 * R_EARTH * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


@lru_cache(None)
def border():
    """Eastern edge of Chile (longitude) every 0.05° of latitude."""
    import geopandas as gpd
    import shapely
    g = gpd.read_file(CHILE, engine="fiona").geometry.union_all()
    la = np.arange(-56.0, -17.0, 0.05)
    x = np.full(la.size, np.nan)
    for i, y in enumerate(la):
        c = shapely.get_coordinates(g.intersection(shapely.LineString([(-80, y), (-60, y)])))
        if len(c):
            x[i] = c[:, 0].max()
    k = np.isfinite(x)
    return la[k], x[k]


def east_km(lon, lat):
    """Distance east of the Chile-Argentina (Bolivia) border at the same latitude, km (negative inside Chile)."""
    la, x = border()
    return (np.asarray(lon, float) - np.interp(lat, la, x)) * 111.195 * np.cos(np.radians(lat))


def match(ta, lata, lona, tb, latb, lonb, dt=DT, dd=DD):
    """
    One-to-one pairs of two catalogues within dt seconds and dd km, closest first by dt / DT + dd / DD.

    Returns
    -------
    ia, ib : int arrays
        Indices into a and b (b sorted by time).
    """
    ta, tb = np.asarray(ta, float), np.asarray(tb, float)
    lo, hi = np.searchsorted(tb, ta - dt), np.searchsorted(tb, ta + dt, side="right")
    n = hi - lo
    ia = np.repeat(np.arange(ta.size), n)
    ib = np.concatenate([np.arange(a, b) for a, b in zip(lo, hi)]) if n.sum() else np.zeros(0, int)
    s = np.abs(tb[ib] - ta[ia]) / dt
    d = hav(np.asarray(lata)[ia], np.asarray(lona)[ia], np.asarray(latb)[ib], np.asarray(lonb)[ib])
    k = d <= dd
    ia, ib, s = ia[k], ib[k], s[k] + d[k] / dd
    o = np.argsort(s, kind="stable")
    ia, ib = ia[o], ib[o]
    keep = np.zeros(ia.size, bool)
    usea, useb = np.zeros(ta.size, bool), np.zeros(tb.size, bool)
    for j in range(ia.size):
        if not usea[ia[j]] and not useb[ib[j]]:
            usea[ia[j]] = useb[ib[j]] = keep[j] = True
    return ia[keep], ib[keep]


# classes
def inslab_weight(z, s, top, hard=C.HARD):
    """
    In-slab weight of events without a class from their depth alone, by the rules of A7 (catalog/classify.py):
    over the slab top ≤ C.IF_TOP the scores of Haynie et al. (2026) with the interface band ± C.W, averaged over the
    depth error; deeper, crustal only above the slab top and not deeper than C.CAP; a weight ≥ hard becomes 1.

    Returns
    -------
    q : (n, 3) array
        Interface, in-slab and crustal weights.
    """
    from scipy.special import ndtr
    z, s, top = (np.asarray(v, float) for v in (z, s, top))
    s = np.maximum(s, C.SIG_MIN)
    q = np.zeros((z.size, 3))
    sh = top <= C.IF_TOP
    if sh.any():
        q[sh] = C.by_depth(z[sh], s[sh], top[sh], np.full(sh.sum(), C.W), np.ones(sh.sum()))
    f0 = ndtr(-z / s)
    above = np.clip((ndtr((top - z) / s) - f0) / (1 - f0), 0, 1)
    pcr = np.where(z <= C.CAP, above, 0.0)
    q[~sh] = np.c_[np.zeros((~sh).sum()), 1 - pcr[~sh], pcr[~sh]]
    one = q.max(1) >= hard
    q[one] = np.eye(3)[np.argmax(q[one], 1)]
    return q


def nest(lon, lat, z):
    n = C.NEST
    lat = np.asarray(lat, float)
    return (np.hypot((np.asarray(lon) - n["lon"]) * np.cos(np.radians(lat)), lat - n["lat"]) <= n["radius_deg"]) & \
        (np.asarray(z) >= n["depth"][0]) & (np.asarray(z) <= n["depth"][1])


# kernel depth model
def wquant(x, w, q):
    o = np.argsort(x)
    x, c = x[o], np.cumsum(w[o])
    return np.interp(np.asarray(q) / 100 * c[-1], c - w[o] / 2, x)


def bandwidth(lon, lat, nn=NN, hmin=H_MIN):
    """Adaptive bandwidth of every event: distance to its nn-th neighbour, at least hmin km."""
    from scipy.spatial import cKDTree
    p = xyz(lon, lat)
    d = cKDTree(p).query(p, k=min(nn + 1, len(p)))[0][:, -1]
    return np.maximum(2 * R_EARTH * np.arcsin(np.clip(d / (2 * R_EARTH), 0, 1)), hmin)


def histograms(ev, grid, bins=BINS, chunk=400):
    """
    Distance below the top spread from the events onto the cells with the kernel of the rate pattern: each event
    spreads its weight over the cells within D_MAX, normalised to its weight, into the bin of its distance.

    Returns
    -------
    H : (cells, bins - 1) array
        Kernel weight per cell and 1 km bin of distance below the top.
    neff : (cells,) array
        Effective number of events per cell, (Σk)² / Σk².
    """
    g = xyz(grid.lon.to_numpy(), grid.lat.to_numpy())
    e = xyz(ev.lon.to_numpy(), ev.lat.to_numpy())
    h = bandwidth(ev.lon.to_numpy(), ev.lat.to_numpy())
    b = np.clip(np.digitize(ev.d.to_numpy(), bins) - 1, 0, len(bins) - 2)
    w = ev.w.to_numpy()
    H, s2 = np.zeros((len(g), len(bins) - 1)), np.zeros(len(g))
    for a in range(0, len(e), chunk):
        sl = slice(a, a + chunk)
        c = np.linalg.norm(e[sl, None, :] - g[None, :, :], axis=2)
        r = 2 * R_EARTH * np.arcsin(np.clip(c / (2 * R_EARTH), 0, 1))
        k = np.where(r <= D_MAX, 1.0 / (r ** 2 + h[sl, None] ** 2) ** POWER, 0.0)
        tot = k.sum(1, keepdims=True)
        k = np.divide(k * w[sl, None], tot, out=np.zeros_like(k), where=tot > 0)
        s2 += (k ** 2).sum(0)
        for j in np.unique(b[sl]):
            H[:, j] += k[b[sl] == j].sum(0)
    S = H.sum(1)
    return H, np.divide(S ** 2, s2, out=np.zeros_like(S), where=s2 > 0)


def fraction(d, thk, w, q=Q_LOW):
    """The fraction of the Slab2 thickness below the top that holds q % of the events (weights w)."""
    return float(wquant(np.asarray(d) / np.asarray(thk), np.asarray(w, float), q))


def zone(H, neff, lsd, bins=BINS):
    """
    Depth model of every cell from its kernel histogram of distance below the top.

    The zone runs from the top to lsd (km below the top, one value per cell: the fraction of the Slab2 thickness of
    fraction()) and is cut into three equal layers.
    Events above the top count in the top layer, events below the zone are not counted. Shares are kernel weights
    with one event added to each layer (Laplace's rule, on the effective number of events); the hypocentre of a layer
    is its weighted median distance, the layer middle with fewer than MIN_LAYER effective events, kept EDGE km inside.

    Returns
    -------
    DataFrame with lsd, w1-w3, h1-h3, h_one, neff; distances in km below the top.
    """
    C_ = np.c_[np.zeros(len(H)), np.cumsum(H, 1)]
    tot = C_[:, -1]
    out = []
    for i in range(len(H)):
        if tot[i] <= 0:
            out.append([lsd[i]] + [np.nan] * 7 + [0.0])
            continue
        z = max(float(lsd[i]), 3 * (1 + 2 * EDGE))
        bb = np.array([0.0, z / 3, 2 * z / 3, z])
        # cumulative mass at the slice limits, linear inside a bin; events above the top count in the top slice
        cb = np.interp(bb, bins, C_[i])
        cb[0] = 0.0
        n = np.diff(cb)
        ne = neff[i] * n.sum() / tot[i]
        p = (n / n.sum() * ne + 1) / (ne + 3)
        hy = []
        for l in range(3):
            ok = ne * n[l] / max(n.sum(), 1e-12) >= MIN_LAYER and n[l] > 0
            hv = np.interp((cb[l] + cb[l + 1]) / 2, C_[i], bins) if ok else (bb[l] + bb[l + 1]) / 2
            hy.append(np.clip(hv, bb[l] + EDGE, bb[l + 1] - EDGE))
        one = np.clip(np.interp(cb[3] / 2, C_[i], bins), EDGE, z - EDGE)
        out.append([z, *p, *hy, one, neff[i]])
    return pd.DataFrame(out, columns=["lsd", "w1", "w2", "w3", "h1", "h2", "h3", "h_one", "neff"])


def neighbours(ev, lon, lat, k=None, radius=None):
    """Indices of the k nearest events, or of the events within radius km, of every point (list of arrays)."""
    from scipy.spatial import cKDTree
    t = cKDTree(xyz(ev.lon.to_numpy(), ev.lat.to_numpy()))
    p = xyz(np.asarray(lon, float), np.asarray(lat, float))
    if k is not None:
        return list(t.query(p, k=min(k, len(ev)))[1])
    return t.query_ball_point(p, r=2 * R_EARTH * np.sin(radius / (2 * R_EARTH)))


def layer_of(d, b):
    return np.clip(np.searchsorted(b, d, side="right") - 1, 0, 2)


def heldout(model, test, cell):
    """Mean log-likelihood per test event of its layer under the shares of the cell it falls in (cell index);
    events below the lower depth of their cell are not scored. Returns (log-likelihood, events scored)."""
    m = model.iloc[cell].reset_index(drop=True)
    d = test.d.to_numpy()
    ok = (d <= m.lsd.to_numpy()) & m.w1.notna().to_numpy()
    L = (np.clip(d, 0, None) >= m.lsd.to_numpy() / 3).astype(int) + (d >= 2 * m.lsd.to_numpy() / 3)
    p = m[["w1", "w2", "w3"]].to_numpy()[np.arange(len(m)), L]
    w = test.w.to_numpy()
    return float(np.sum(np.log(p[ok]) * w[ok]) / w[ok].sum()), int(ok.sum())

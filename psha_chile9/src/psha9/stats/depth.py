"""T9: in-slab depth model (D-IS-04), ported from psha_chile8 model/inslab/depth.py, run.py and options.py (C14,
C15). The distance of the in-slab events below the Slab2 top, each with its in-slab class weight, is spread onto the
in-slab grid with the kernel of the rate pattern. Per cell: the zone from the slab top to the fraction of the Slab2
thickness that holds 95 % of the events, three equal slices, the share of the events in each slice and their median
depth in it, and the one-layer hypocentre.
"""
from functools import lru_cache

import numpy as np
import pandas as pd
import shapely
from scipy.spatial import cKDTree
from scipy.special import ndtr

from ..catalog import classify as C
from .gr import CFG, ROOT

Z = CFG["depth"]
K = Z["kernel"]
R_EARTH = 6371.0
BINS = np.arange(*Z["bins"])


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
    g = gpd.read_file(ROOT / Z["chile"]).geometry.union_all()
    la = np.arange(-56.0, -17.0, 0.05)
    x = np.full(la.size, np.nan)
    for i, y in enumerate(la):
        c = shapely.get_coordinates(g.intersection(shapely.LineString([(-80, y), (-60, y)])))
        if len(c):
            x[i] = c[:, 0].max()
    k = np.isfinite(x)
    return la[k], x[k]


def east_km(lon, lat):
    """Distance east of the Chile border at the same latitude, km (negative inside Chile)."""
    la, x = border()
    return (np.asarray(lon, float) - np.interp(lat, la, x)) * 111.195 * np.cos(np.radians(lat))


def match(ta, lata, lona, tb, latb, lonb, dt, dd):
    """One-to-one pairs within dt seconds and dd km, closest first by dt and distance; b sorted by time. Returns the
    indices into a and b."""
    lo, hi = np.searchsorted(tb, ta - dt), np.searchsorted(tb, ta + dt, side="right")
    n = hi - lo
    ia = np.repeat(np.arange(ta.size), n)
    ib = np.concatenate([np.arange(a, b) for a, b in zip(lo, hi)]) if n.sum() else np.zeros(0, int)
    d = hav(lata[ia], lona[ia], latb[ib], lonb[ib])
    k = d <= dd
    ia, ib = ia[k], ib[k]
    o = np.argsort(np.abs(tb[ib] - ta[ia]) / dt + d[k] / dd, kind="stable")
    ua, ub, keep = np.zeros(ta.size, bool), np.zeros(tb.size, bool), []
    for i, j in zip(ia[o], ib[o]):
        if not ua[i] and not ub[j]:
            ua[i] = ub[j] = True
            keep.append((i, j))
    return np.array(keep, int).reshape(-1, 2).T


def inslab_weight(z, s, top):
    """
    In-slab weight of events without a class from their depth alone, by the catalogue rules (D-CLS-03): over a slab
    top ≤ the interface top the scores of Haynie et al. (2026) with the ± w band, averaged over the depth error;
    deeper, crustal only above the slab top and not below the crustal cap; a weight ≥ hard becomes 1.
    """
    S = C.S
    s = np.maximum(s, S["sig_min"])
    q = np.zeros((z.size, 3))
    sh = top <= S["interface"]["top"]
    q[sh] = C.by_depth(z[sh], s[sh], top[sh], S["interface"]["w"], S["interface"]["offset"], 1.0)
    f0 = ndtr(-z / s)
    pcr = np.where(z <= S["crustal"]["cap"], np.clip((ndtr((top - z) / s) - f0) / (1 - f0), 0, 1), 0.0)
    q[~sh] = np.c_[np.zeros((~sh).sum()), 1 - pcr[~sh], pcr[~sh]]
    one = q.max(1) >= S["hard"]
    q[one] = np.eye(3)[np.argmax(q[one], 1)]
    return q[:, 1]


def nest(lon, lat, z):
    n = C.SS["nest"]
    return (np.hypot((lon - n["lon"]) * np.cos(np.radians(lat)), lat - n["lat"]) <= n["radius_deg"]) & (z >= n["depth"][0]) & (z <= n["depth"][1])


def events(cat, yr):
    """
    Depth events: the catalogue (measured depth, from `since`, in-slab weight > 0, nest out, no depths from `drop`,
    no local-network depths east of the Chile border) and Riedel-Hornig inside Chile (Ml and depth-error cuts, slab
    at the epicentre, east of the edge, nest out, in-slab weight of the depth rule > 0). Each event with its in-slab
    weight; `dup` marks catalogue events also in Riedel-Hornig.

    Returns
    -------
    ev : DataFrame
        source, id, lon, lat, z, top, thk, d (km below the top), w, yr, depth_src, dup.
    log : DataFrame
        Events left after each step.
    """
    R, log = Z["rh"], []
    note = lambda src, step, m: log.append(dict(source=src, step=step, events=int(np.sum(m))))
    r = pd.read_csv(ROOT / R["file"])
    r["t"] = (pd.to_datetime(r.Date + "T" + r.Time, errors="coerce") - pd.Timestamp("1970-01-01")).dt.total_seconds()
    r = r.dropna(subset=["t"]).sort_values("t").reset_index(drop=True)
    lon, lat, z, sig = (r[k].to_numpy(float) for k in ("Lon", "Lat", "Dep", "Dep_Error"))
    z = -z
    n = np.ones(len(r), bool)
    note("Riedel-Hornig", "all", n)
    n &= r.Ml.to_numpy() >= R["ml"]
    note("Riedel-Hornig", f"Ml ≥ {R['ml']}", n)
    n &= sig <= R["sig"]
    note("Riedel-Hornig", f"depth error ≤ {R['sig']:g} km", n)
    n &= east_km(lon, lat) <= 0
    note("Riedel-Hornig", "inside Chile", n)
    top, thk = C.slab_at(lon, lat)[:2]
    n &= np.isfinite(top) & ~C.west_of_edge(lon, lat)
    note("Riedel-Hornig", "slab at the epicentre, east of the edge", n)
    n &= ~nest(lon, lat, z)
    note("Riedel-Hornig", "Jujuy nest out", n)
    w = np.zeros(len(r))
    w[n] = inslab_weight(z[n], sig[n], top[n])
    n &= w > 0
    note("Riedel-Hornig", "in-slab weight > 0 (depth rule)", n)
    rh = pd.DataFrame(dict(source="rh", id=r.id.astype(str), lon=lon, lat=lat, z=z, top=top, thk=thk, w=w, mw=r.Ml,
                           yr=1970 + r.t / (365.2425 * 86400), depth_src="rh", dup=False))[n]

    c = cat
    m = (c.depth_kind == "measured").to_numpy() & c.depth.notna().to_numpy()
    note("catalogue", "measured depth", m)
    m &= (c.w_inslab > 0).to_numpy()
    note("catalogue", "in-slab weight > 0", m)
    m &= yr >= Z["since"]
    note("catalogue", f"from {Z['since']}", m)
    m &= np.isfinite(c.top.to_numpy(float))
    note("catalogue", "slab at the epicentre", m)
    m &= (c.sub_inslab != "jujuy_nest").to_numpy()
    note("catalogue", "Jujuy nest out", m)
    m &= ~(c.depth_src.isin(Z["local"]).to_numpy() & (east_km(c.lon, c.lat) > 0))
    note("catalogue", "local depths east of the Chile border out", m)
    m &= ~c.depth_src.isin(Z["drop"]).to_numpy()
    note("catalogue", f"without depths from {', '.join(Z['drop'])}", m)
    q = c[m].reset_index(drop=True)
    tq = (pd.to_datetime(q.time.str[:23]) - pd.Timestamp("1970-01-01")).dt.total_seconds().to_numpy()
    tr = r.t.to_numpy()[n]
    ia, ib = match(tq, q.lat.to_numpy(), q.lon.to_numpy(), tr, lat[n], lon[n], R["dt"], R["dd"])
    dup = np.zeros(len(q), bool)
    dup[ia] = True
    note("catalogue", "of them also in Riedel-Hornig", dup)
    ca = pd.DataFrame(dict(source="catalogue", id=q.event_id, lon=q.lon, lat=q.lat, z=q.depth, top=q.top, thk=q.thk,
                           w=q.w_inslab, mw=q.mw, yr=yr[m], depth_src=q.depth_src, dup=dup))
    ev = pd.concat([ca, rh], ignore_index=True)
    ev["d"] = ev.z - ev.top
    return ev, pd.DataFrame(log)


def pick(ev, which):
    """Depth set (Q-59): catalogue, rh (Riedel-Hornig inside Chile) or both (an event in both counts once, with the
    Riedel-Hornig depth)."""
    if which == "catalogue":
        return ev[ev.source == "catalogue"].reset_index(drop=True)
    if which == "rh":
        return ev[ev.source == "rh"].reset_index(drop=True)
    return ev[~ev.dup].reset_index(drop=True)


def wquant(x, w, q):
    o = np.argsort(x)
    x, c = x[o], np.cumsum(w[o])
    return np.interp(np.asarray(q) / 100 * c[-1], c - w[o] / 2, x)


def histograms(ev, grid, chunk=400):
    """
    Distance below the top spread from the events onto the cells with the kernel of the rate pattern,
    1 / (r² + h²)^power, h the distance to the nn-th neighbour (at least hmin), cells within dmax; each event spreads
    its weight, into the 1 km bin of its distance.

    Returns
    -------
    H : (cells, bins - 1) array
    neff : (cells,) effective number of events, (Σk)² / Σk².
    """
    g = xyz(grid.lon.to_numpy(), grid.lat.to_numpy())
    e = xyz(ev.lon.to_numpy(), ev.lat.to_numpy())
    dk = cKDTree(e).query(e, k=min(K["nn"] + 1, len(e)))[0][:, -1]
    h = np.maximum(2 * R_EARTH * np.arcsin(np.clip(dk / (2 * R_EARTH), 0, 1)), K["hmin"])
    b = np.clip(np.digitize(ev.d.to_numpy(), BINS) - 1, 0, len(BINS) - 2)
    w = ev.w.to_numpy()
    H, s2 = np.zeros((len(g), len(BINS) - 1)), np.zeros(len(g))
    for a in range(0, len(e), chunk):
        sl = slice(a, a + chunk)
        c = np.linalg.norm(e[sl, None, :] - g[None, :, :], axis=2)
        r = 2 * R_EARTH * np.arcsin(np.clip(c / (2 * R_EARTH), 0, 1))
        k = np.where(r <= K["dmax"], 1.0 / (r ** 2 + h[sl, None] ** 2) ** K["power"], 0.0)
        tot = k.sum(1, keepdims=True)
        k = np.divide(k * w[sl, None], tot, out=np.zeros_like(k), where=tot > 0)
        s2 += (k ** 2).sum(0)
        oh = np.zeros((k.shape[0], len(BINS) - 1))
        oh[np.arange(k.shape[0]), b[sl]] = 1.0
        H += k.T @ oh
    S = H.sum(1)
    return H, np.divide(S ** 2, s2, out=np.zeros_like(S), where=s2 > 0)


def zone(H, neff, lsd):
    """
    Depth model of every cell from its histogram: the zone from the top to lsd (km below the top) in three equal
    slices; events above the top count in the top slice, events below the zone are not counted. Shares with one
    event added to each slice (Laplace); hypocentre the median of the slice, the slice middle with fewer than
    `min_layer` effective events, kept `edge` km inside; h_one the median of the zone.
    """
    Cm = np.c_[np.zeros(len(H)), np.cumsum(H, 1)]
    tot = Cm[:, -1]
    e, out = Z["edge"], []
    for i in range(len(H)):
        if tot[i] <= 0:
            out.append([lsd[i]] + [np.nan] * 7 + [0.0])
            continue
        zz = max(float(lsd[i]), 3 * (1 + 2 * e))
        bb = np.array([0.0, zz / 3, 2 * zz / 3, zz])
        cb = np.interp(bb, BINS, Cm[i])
        cb[0] = 0.0
        n = np.diff(cb)
        ne = neff[i] * n.sum() / tot[i]
        p = (n / n.sum() * ne + 1) / (ne + 3)
        hy = []
        for l in range(3):
            ok = ne * n[l] / max(n.sum(), 1e-12) >= Z["min_layer"] and n[l] > 0
            hv = np.interp((cb[l] + cb[l + 1]) / 2, Cm[i], BINS) if ok else (bb[l] + bb[l + 1]) / 2
            hy.append(np.clip(hv, bb[l] + e, bb[l + 1] - e))
        one = np.clip(np.interp(cb[3] / 2, Cm[i], BINS), e, zz - e)
        out.append([zz, *p, *hy, one, neff[i]])
    return pd.DataFrame(out, columns=["lsd", "w1", "w2", "w3", "h1", "h2", "h3", "h_one", "neff"])


def model(ev, g):
    """Cell table (depths in km, positive down) of the events ev on the grid g, and the zone and one-layer
    fractions of the thickness (95 % and 50 % of the in-slab weight)."""
    r = (ev.d / ev.thk).to_numpy()
    f = float(wquant(r, ev.w.to_numpy(), Z["q_low"]))
    f1 = float(wquant(r, ev.w.to_numpy(), 50))
    z = zone(*histograms(ev, g), lsd=f * g.thk.to_numpy())
    res = g[["lon", "lat", "top", "thk"]].copy()
    for k in ("lsd", "h1", "h2", "h3"):
        res[k] = z[k].to_numpy() + g.top.to_numpy()
    res["usd"] = g.top
    res[["w1", "w2", "w3"]] = z[["w1", "w2", "w3"]].to_numpy()
    res["h_one"] = g.top + f1 * g.thk
    res["h_one_median"] = z.h_one.to_numpy() + g.top.to_numpy()
    res["n_events"] = z.neff.round(1)
    return res[["lon", "lat", "top", "thk", "usd", "lsd", "w1", "w2", "w3", "h1", "h2", "h3", "h_one", "h_one_median", "n_events"]], f, f1


def grid(dat):
    g = pd.read_csv(dat / "inslab_grid.csv")
    g["top"], g["thk"] = C.slab_at(g.lon, g.lat)[:2]
    return g[np.isfinite(g.top)].reset_index(drop=True)

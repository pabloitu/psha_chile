"""C7: tectonic class of every event, as weights (D-CLS-01 to 13, D-CAT-22, 23).

Each event gets a weight for interface, in-slab, crustal, outer rise and non-earthquake that add up to 1, a sub-class
by position and the rule that decided. Ported from psha_chile8 catalog/classify.py on the DATA geometry: the western
edge replaces the trench, the crustal classes are polygons, the interface band reaches a slab top of 60 km.

Usage: python -m psha9.catalog.classify [out_dir]
"""
import datetime
import json
import sys
from functools import lru_cache

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import yaml
from pyproj import Transformer
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree
from scipy.special import ndtr, ndtri

from . import locate
from .match import CFG, ROOT, tsec, year

S = CFG["classify"]
SI, SC, SS = S["interface"], S["crustal"], S["inslab"]
CLS = ["interface", "in-slab", "crustal", "outer rise", "non-earthquake"]
COLS = ["w_interface", "w_inslab", "w_crustal", "w_outer_rise", "w_nonquake"]
FIELDS = ["event_id"] + COLS + ["cls", "cls_auto", "rule", "basis", "sub_interface", "sub_inslab", "sub_crustal", "top",
                                "thk", "unc", "d", "mech_kind", "mech_m", "n_candidates", "depth_assigned",
                                "depth_assigned_sigma"]


# geometry
@lru_cache(None)
def slab():
    g, a = {}, None
    for k in ("dep", "thk", "dip", "str", "unc"):
        a = pd.read_csv(ROOT / S["slab"].format(k=k), header=None, names=["x", "y", "z"])
        z = a.pivot(index="y", columns="x", values="z")
        g[k] = RegularGridInterpolator((z.index.to_numpy(), z.columns.to_numpy()), z.to_numpy(), bounds_error=False)
        g[k + "_v"] = a.z.to_numpy()
    ok = np.isfinite(g["dep_v"])
    g["ok"] = ok
    g["tree"] = cKDTree(np.c_[a.x.to_numpy(), a.y.to_numpy()][ok] * [np.cos(np.radians(30)), 1])
    return g


def slab_at(lon, lat):
    """
    Slab2 at the epicentres: bilinear, and the nearest node within slab_km at the sides of the grid.

    Returns top (km, positive down), thk, dip, str (nearest node) and unc; NaN where there is no slab.
    """
    g = slab()
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    p = np.c_[lat, np.mod(lon, 360)]
    d, j = g["tree"].query(np.c_[np.mod(lon, 360) * np.cos(np.radians(30)), lat])
    near = d * 111.195 <= S["slab_km"]
    out = {}
    for k in ("dep", "thk", "dip", "unc"):
        v = g[k](p)
        out[k] = np.where(np.isfinite(v), v, np.where(near, g[k + "_v"][g["ok"]][j], np.nan))
    st = np.where(np.isfinite(out["dep"]), g["str_v"][g["ok"]][j], np.nan)
    return -out["dep"], out["thk"], out["dip"], st, np.where(np.isfinite(out["dep"]), out["unc"], np.nan)


def utm(lon, lat):
    return Transformer.from_crs(4326, 32719, always_xy=True).transform(lon, lat)


def to_utm(g):
    return shapely.transform(g, lambda c: np.c_[utm(c[:, 0], c[:, 1])])


@lru_cache(None)
def shapes():
    """
    The DATA geometry the rules read.

    Returns edge (lat, lon of the western edge, south to north), area (crustal area), classes (name -> polygon),
    ocean (east of the edge and west of the crustal area: the Chile Rise inset and the sea south-west of Patagonia),
    lines (PB2002 name -> line, and "mf" the Magallanes-Fagnano traces, in UTM).
    """
    d = ROOT / S["data"]
    e = np.array(gpd.read_file(d / "edge.geojson").geometry.iloc[0].coords)
    e = e[np.argsort(e[:, 1])]
    area = gpd.read_file(d / "crustal_area.geojson").union_all()
    cl = gpd.read_file(d / "crustal_classes.geojson")
    x0, y0, x1, y1 = area.bounds
    east = shapely.Polygon(np.vstack([e, [[x1 + 5, e[-1, 1]], [x1 + 5, e[0, 1]]]])).buffer(0)
    rest = east.intersection(shapely.box(x0 - 5, y0, x1 + 5, y1)).difference(area.buffer(1e-6))
    line = shapely.LineString(e).buffer(1e-3)
    ocean = shapely.union_all([p for p in getattr(rest, "geoms", [rest]) if p.intersects(line) and p.area > 1e-4])
    pb = {f["properties"]["Name"]: to_utm(shapely.geometry.shape(f["geometry"]))
          for f in json.load(open(ROOT / S["pb2002"]))["features"]}
    f = gpd.read_file(ROOT / S["faults"])
    pb["mf"] = to_utm(f[f.fid.isin(S["outer_rise"]["mf"])].union_all())
    return {"edge": e, "area": area, "classes": dict(zip(cl.cls, cl.geometry)), "ocean": ocean, "lines": pb}


def west_of_edge(lon, lat):
    e = shapes()["edge"]
    return np.asarray(lon, float) < np.interp(np.asarray(lat, float), e[:, 1], e[:, 0])


def zone(lon, lat):
    """Crustal class by position (forearc, arc, backarc, patagonia), `outside` out of the crustal area."""
    z = np.full(len(lon), "outside", object)
    for k, p in shapes()["classes"].items():
        z[shapely.contains_xy(p, np.asarray(lon, float), np.asarray(lat, float))] = k
    return z


def dist(lon, lat, name):
    """Distance (km) to a line of shapes()['lines']."""
    return shapely.distance(shapely.points(*utm(np.asarray(lon, float), np.asarray(lat, float))), shapes()["lines"][name]) / 1e3


def nu(s, d, k):
    """Normal and slip vector (north, east, down) of a plane with strike, dip, rake in degrees."""
    s, d, k = (np.radians(np.asarray(v, float)) for v in (s, d, k))
    n = np.stack([-np.sin(d) * np.sin(s), np.sin(d) * np.cos(s), -np.cos(d)], -1)
    u = np.stack([np.cos(k) * np.cos(s) + np.cos(d) * np.sin(k) * np.sin(s),
                  np.cos(k) * np.sin(s) - np.cos(d) * np.sin(k) * np.cos(s), -np.sin(k) * np.sin(d)], -1)
    return n, u


def skew(s, d, k, ss, sd, tol=None, az=None):
    """
    Misfit of mechanisms to the interface mechanism at their epicentres (D-CLS-04).

    The interface mechanism has the Slab2 plane and slips along the plate convergence laid on that plane. A double
    couple has four equivalent descriptions (normal, slip); for each, the rotation to the interface is a swing of
    the normal onto the slab normal and a twist of the slip about it.

    Parameters
    ----------
    s, d, k : array
        Strike, dip, rake of one nodal plane (degrees).
    ss, sd : array
        Slab2 strike and dip at the epicentre.

    Returns
    -------
    array
        Smallest of sqrt((swing / tol[0])² + (twist / tol[1])²) over the four descriptions.
    """
    tol, az = SI["tol"] if tol is None else tol, SI["az"] if az is None else az
    ang = lambda a, b: np.degrees(np.arccos(np.clip((a * b).sum(-1), -1, 1)))
    n, u = nu(s, d, k)
    N = nu(ss, sd, 90.0)[0]
    h = np.array([np.cos(np.radians(az)), np.sin(np.radians(az)), 0.0])
    V = h - (h * N).sum(-1, keepdims=True) * N
    V /= np.linalg.norm(V, axis=-1, keepdims=True)
    m = np.full(len(N), np.inf)
    for a, b in ((n, u), (-n, -u), (u, n), (-u, -n)):
        sw = ang(a, N)
        ax = np.cross(a, N)
        ax /= np.maximum(np.linalg.norm(ax, axis=-1, keepdims=True), 1e-12)
        t = np.radians(sw)[:, None]
        b = b * np.cos(t) + np.cross(ax, b) * np.sin(t) + ax * (ax * b).sum(-1, keepdims=True) * (1 - np.cos(t))
        m = np.minimum(m, np.hypot(sw / tol[0], ang(b, V) / tol[1]))
    return m


def rejected(run, ids):
    """Smallest of the depths the sources give these events, and how many (for an event without a measured depth
    every one of them was rejected in C3)."""
    e = pd.read_csv(run / "events_matched.csv", low_memory=False)
    L = pd.read_csv(run / "links.csv", low_memory=False, dtype={"src_id": str, "origin_id": str})
    R = locate.records(e, L[L.event_id.isin(ids)])[0]
    return R[np.isfinite(R.z)].groupby("event_id").z.agg(["min", "count"])


def has_depth(c):
    """Events whose depth was solved for: measured, and the low-quality depths with their large sigma (D-CAT-14)."""
    return c.depth_kind.isin(["measured", "low quality"]) & c.depth.notna()


def geometry(c, rej):
    """
    The catalogue with what the rules need.

    Returns one row per event: z, sig (measured depths only), known, top, thk, dip, sstr, unc, d (z − top), sea
    (outer rise by position: west of the edge whatever the depth, D-CLS-01; shallow in the inset and on the
    Scotia-Antarctic boundary, D-CLS-09), zone, south, an (Antarctic interface by position), em (misfit to the interface
    mechanism, NaN without mechanism or slab), hint, nonquake, zrej and nrej (smallest and number of the rejected
    depths), yr.
    """
    A = SI["antarctic"]
    lon, lat = c.lon.to_numpy(float), c.lat.to_numpy(float)
    known = has_depth(c).to_numpy()
    g = pd.DataFrame({"event_id": c.event_id, "time": c.time, "yr": year(tsec(c.time)), "lon": lon, "lat": lat, "mw": c.mw,
                      "z": np.where(known, c.depth, np.nan),
                      "sig": np.where(known, c.depth_sigma.clip(lower=S["sig_min"]).fillna(S["sig_min"]), np.nan),
                      "known": known, "depth_src": c.depth_src, "offshore": c.offshore, "in_box": c.in_box,
                      "nonquake": c.nonquake.fillna("").ne("").to_numpy()})
    g["top"], g["thk"], g["dip"], g["sstr"], g["unc"] = slab_at(lon, lat)
    g["d"] = g.z - g.top
    sh = shapes()
    slab_, shallow = g.top.notna().to_numpy(), ~(known & (g.z > SC["cap"]).to_numpy())
    g["zone"] = zone(lon, lat)
    g["west"] = west_of_edge(lon, lat)
    g["ocean"] = shapely.contains_xy(sh["ocean"], lon, lat)
    south = lat < A["south_lat"]
    k = south & ~slab_ & ~g.west.to_numpy() & ~g.ocean.to_numpy() & (g.zone == "outside").to_numpy()
    sco = np.zeros(len(c), bool)
    ds = dist(lon[k], lat[k], S["outer_rise"]["scotia"])
    sco[k] = (ds < dist(lon[k], lat[k], A["name"])) & (ds < dist(lon[k], lat[k], "mf"))
    g["scotia"] = sco
    g["sea"] = g.west.to_numpy() | ((g.ocean | g.scotia).to_numpy() & shallow)
    mech = c[["strike1", "dip1", "rake1"]].notna().all(axis=1).to_numpy()
    rev = mech & (c[["rake1", "rake2"]].ge(A["rake"][0]) & c[["rake1", "rake2"]].le(A["rake"][1])).any(axis=1).to_numpy()
    k = mech & slab_
    g["em"] = np.nan
    g.loc[k, "em"] = skew(c.strike1[k], c.dip1[k], c.rake1[k], g.sstr[k], g.dip[k])
    g["mech_kind"] = np.where(np.isfinite(g.em), np.where(g.em <= 1, "interface-like", "other"), np.where(mech, "no slab", "none"))
    g["south"] = south
    g["d_an"] = np.where(south, dist(lon, lat, A["name"]), np.nan)
    g["an"] = south & ~g.sea & (g.d_an <= A["width"]) & ~(g.z > A["z"]).to_numpy() & ~(mech & ~rev)
    g["hint"] = c.a6_class_hint if "a6_class_hint" in c else None
    g["zrej"], g["nrej"] = c.event_id.map(rej["min"]).to_numpy(), c.event_id.map(rej["count"]).fillna(0).to_numpy()
    return g


# rules
def bins(g):
    """Bin of every event for the shares: slab-top range, latitude band, magnitude range (events outside the bands
    take the nearest one; no Mw counts as the lower range)."""
    Q = S["shares"]
    return (np.digitize(g.top.to_numpy(float), [SI["top"]] + Q["top"], right=True), np.digitize(-g.lat.to_numpy(float), Q["lat"]),
            np.digitize(np.nan_to_num(g.mw.to_numpy(float)), Q["mag"]))


def shares(g, P, base):
    """
    Shares of interface, in-slab and crustal among the classified events of each bin.

    P : weights (n, 3) of the events; base : the events that count. A bin with fewer than n of them adds the other
    magnitude range, then the neighbouring latitude bands (both ranges).

    Returns T[top, lat, mag] -> three shares, and the table of bins (n of the bin itself, n used, what was borrowed).
    """
    Q = S["shares"]
    it, il, im = bins(g)
    e = [0.0, SI["top"]] + Q["top"] + [np.inf]
    top = [f"{a:g}–{b:g} km" if np.isfinite(b) else f"> {a:g} km" for a, b in zip(e[:-1], e[1:])]
    e = [15.5] + Q["lat"] + [58.0]
    la = [f"{a:g}–{b:g}° S" for a, b in zip(e[:-1], e[1:])]
    e = [Q["m_min"]] + Q["mag"]
    mg = [f"Mw {a:g}–{b:g}" for a, b in zip(e[:-1], e[1:])] + [f"Mw ≥ {e[-1]:g}"]
    T, rows = np.full((len(top), len(la), len(mg), 3), np.nan), []
    for a in range(T.shape[0]):
        for b in range(T.shape[1]):
            for m in range(T.shape[2]):
                k = base & (it == a) & (il == b) & (im == m)
                n0, how = int(k.sum()), ""
                if k.sum() < Q["n"]:
                    k, how = base & (it == a) & (il == b), "magnitude"
                if k.sum() < Q["n"]:
                    k, how = base & (it == a) & (np.abs(il - b) <= 1), "magnitude and latitude"
                s = P[k].sum(0)
                T[a, b, m] = s / s.sum() if s.sum() > 0 else np.nan
                rows.append({"slab_top": top[a], "lat": la[b], "mag": mg[m], "n": n0, "n_used": int(k.sum()), "borrowed": how,
                             "interface": T[a, b, m, 0], "inslab": T[a, b, m, 1], "crustal": T[a, b, m, 2]})
    return T, pd.DataFrame(rows)


def ramp(x, x1, x2, p1, p2):
    return np.where(x < x1, p1, np.where(x > x2, p2, p1 + (p2 - p1) * (x - x1) / (x2 - x1)))


def by_depth(z, s, top, w, off, pk):
    """
    Interface, in-slab and crustal scores after Haynie et al. (2026) for a depth z ± s over a slab top, averaged
    over the depth error (normal, cut at the ground). The interface band is top + off ± w; pk : factor on the
    interface from the mechanism. Their Moho grid is replaced by one depth, and the band has no lower fade: it ends
    where the slab top passes interface.top (D-CLS-08).
    """
    lo = ndtr(-z / s)
    out, nq = np.zeros((len(z), 3)), SC["nq"]
    for u in (np.arange(nq) + 0.5) / nq:
        x = z + s * ndtri(lo + u * (1 - lo))
        d = x - top
        pif = (np.abs(d - off) <= w) * pk
        pcr = (1 - pif) * ramp(d, *SC["diff"], 1.0, 0.0) * ramp(x, SC["moho"], np.maximum(top, SC["moho"] + 1e-6), 1.0, 0.0)
        out += np.c_[pif, 1 - pif - pcr, pcr]
    return out / nq


def lift(Q, k, lr):
    """Interface odds of the rows k times lr; in-slab and crustal keep their ratio."""
    p = np.where(k, Q[:, 0] * lr / (Q[:, 0] * lr + 1 - Q[:, 0]), Q[:, 0])
    r = Q[:, 1:] / np.maximum(Q[:, 1:].sum(1, keepdims=True), 1e-12)
    return np.c_[p, (1 - p)[:, None] * r]


def classify(g, w=None, off=None, hard=S["hard"], mech=True):
    """
    Class weights of every event.

    Parameters
    ----------
    g : DataFrame
        Output of geometry().
    w, off : float
        Half-width and offset below Slab2 of the interface band, km (default: the config).
    hard : float or None
        A class with this weight or more becomes 1 (events with a measured depth only).
    mech : bool
        False: mechanisms not used (for the band measurement and the calibration).

    Returns
    -------
    out : DataFrame
        The five weights, cls (the class with weight 1, else split), cls_auto (the same from the rules alone, for
        events with a literature class), rule, basis, n_candidates.
    tab : DataFrame
        The bins of the shares.
    """
    w, off = SI["w"] if w is None else w, SI["offset"] if off is None else off
    n = len(g)
    z, s, top, mw = g.z.to_numpy(float), g.sig.to_numpy(float), g.top.to_numpy(float), g.mw.to_numpy(float)
    known, slab_, sea, an = g.known.to_numpy(), np.isfinite(top), g.sea.to_numpy(), g.an.to_numpy()
    em = g.em.to_numpy(float) if mech else np.full(n, np.nan)
    pk = np.where(em > 1, 0.0, 1.0)
    ins = np.isfinite(em) & (em <= 1)
    ifok = slab_ & (top <= SI["top"]) & (pk > 0)
    P, rule = np.zeros((n, 5)), np.full(n, "", object)

    def put(m, j, name):
        m = m & (rule == "")
        P[m, j], rule[m] = 1.0, name

    put(g.nonquake.to_numpy(), 4, "non_earthquake")
    put(sea, 3, "outer_rise")
    put(an, 0, "antarctic")
    put(~known & (mw >= S["m_interface"] - 0.05), 0, "great_no_depth")
    # no slab under it: crustal, whatever its depth says, down to the deep-focus limit; below it the slab beyond Slab2
    put(known & ~slab_ & (z <= SS["deep"]), 2, "no_slab")
    put(known & ~slab_, 1, "no_slab_deep")
    put(~known & ~slab_, 2, "nodepth_no_slab")
    # depth and its error against the slab surface, where the slab top is below the interface band
    with np.errstate(invalid="ignore"):
        f0 = ndtr(-z / s)
        b = np.clip((ndtr((top - z) / s) - f0) / (1 - f0), 0, 1)
    pcr = np.where(z <= SC["cap"], b, 0.0)
    Q = np.c_[np.zeros(n), 1 - pcr, pcr]
    m = known & slab_ & (top <= SI["top"])
    Q[m] = lift(by_depth(z[m], s[m], top[m], w, off, pk[m]), ins[m], SI["lr"])
    m = known & (rule == "")
    one = Q.max(1) >= (1 - 1e-9 if hard is None else hard)
    P[m, :3] = np.where(one[:, None], np.eye(3)[np.argmax(np.nan_to_num(Q), 1)], Q)[m]
    rule[m] = np.where(one[m], "depth", "depth_split")
    # no measured depth
    put(~known & (top > SI["top"]) & (g.nrej.to_numpy() > 0) & (g.zrej.to_numpy() >= SS["deep_rej"]), 1, "nodepth_deep")
    hj = g.hint.map({q: i for i, q in enumerate(CLS[:4])}).to_numpy(float)
    hinted = np.isfinite(hj) & (rule != "non_earthquake")
    H = np.zeros((n, 5))
    H[hinted, hj[hinted].astype(int)] = 1.0
    B = np.where(hinted[:, None], H, P)
    base = (hinted | (rule != "")) & slab_ & ~sea & ~an & g.in_box.to_numpy() & (mw >= S["shares"]["m_min"] - 0.05) & \
        (g.yr.to_numpy() >= S["shares"]["from"]) & (B[:, :3].sum(1) > 0) & (rule != "great_no_depth")
    T, tab = shares(g, B[:, :3], base)
    m = ~known & (rule == "")
    old = (g.yr.to_numpy() < S["old"]) & ((top <= SI["top"]) | (g.zone.to_numpy() == "forearc"))
    q = T[bins(g)][m] * np.c_[ifok * pk, np.ones(n), ~old][m]
    q = np.where(np.nan_to_num(q).sum(1, keepdims=True) > 0, np.nan_to_num(q), np.c_[ifok, np.ones(n), ~old][m])
    P[m, :3], rule[m] = lift(q / q.sum(1, keepdims=True), ins[m], SI["lr"]), "nodepth_share"
    auto = P.copy()
    P[hinted], rule[hinted] = H[hinted], "hint"
    name = lambda X: np.where(X.max(1) > 1 - 1e-9, np.array(CLS)[np.argmax(X, 1)], "split")
    out = pd.DataFrame(np.round(P, 4), columns=COLS, index=g.index)
    out["cls"], out["cls_auto"], out["rule"] = name(P), name(auto), rule
    # D-CAT-23: what the class rests on
    out["basis"] = np.where(rule == "hint", "literature", np.where(rule == "non_earthquake", "source flag", np.where(
        known & (s < S["review"]["sig"]), "depth", "rule")))
    for i, c in enumerate(COLS):
        out[c.replace("w_", "a_")] = np.round(auto[:, i], 4)
    out["n_candidates"] = np.where(sea | an | ~slab_, 1, 1 + ifok + (~known | (z <= SC["cap"])))
    return out, tab


def subs(g, out):
    """Sub-class of each family the event has weight in, by position (D-CLS-07, 10)."""
    N = SS["nest"]
    r = np.hypot((g.lon - N["lon"]) * np.cos(np.radians(g.lat)), g.lat - N["lat"])
    nest = g.known & (r <= N["radius_deg"]) & (g.z >= N["depth"][0]) & (g.z <= N["depth"][1])
    si = np.where(g.south, "antarctic_interface", "interface")
    ss = np.where(nest, "jujuy_nest", np.where(g.known & (g.z > SS["deep"]), "deep_focus",
                                               np.where(g.top <= SS["shallow_top"], "intraslab_shallow", "intraslab_intermediate")))
    return pd.DataFrame({"sub_interface": np.where(out.w_interface > 0, si, ""), "sub_inslab": np.where(out.w_inslab > 0, ss, ""),
                         "sub_crustal": np.where(out.w_crustal > 0, g.zone, "")}, index=g.index)


def assigned(g, out):
    """Depth of the events with a literature class and no measured depth (D-CLS-02): interface on the slab top
    within the band's range, in-slab at frac of the thickness below the top, crustal at assigned_z. Never read by
    the rules."""
    k = (out.rule == "hint") & ~g.known
    z = np.where(k & (out.cls == "interface") & g.top.notna(), g.top.clip(upper=SI["top"]),
                 np.where(k & (out.cls == "in-slab") & g.top.notna(), g.top + SS["frac"] * g.thk,
                          np.where(k & (out.cls == "crustal"), SC["assigned_z"], np.nan)))
    return pd.DataFrame({"depth_assigned": np.round(z, 1), "depth_assigned_sigma": np.where(np.isfinite(z), S["sig_assigned"], np.nan)},
                        index=g.index)


def run(c, rej, **kw):
    """Geometry, weights, sub-classes and assigned depths of a catalogue: (g, classes table, bins of the shares)."""
    g = geometry(c, rej)
    out, tab = classify(g, **kw)
    out = pd.concat([out, subs(g, out), assigned(g, out)], axis=1)
    out["d"] = g.d.round(2)
    for k in ("top", "thk", "unc"):
        out[k] = g[k].round(2)
    out["mech_kind"], out["mech_m"] = g.mech_kind, g.em.round(3)
    out.insert(0, "event_id", g.event_id)
    return g, out, tab


def review(cat):
    """D-CAT-23: events of Mw >= m in the collection box whose class comes from a rule."""
    k = (cat.mw >= S["review"]["m"] - 0.05) & cat.in_box & (cat.basis == "rule")
    cols = ["event_id", "time", "lat", "lon", "mw", "depth", "depth_sigma", "depth_src", "top"] + COLS[:4] + [
        "cls", "rule", "sub_interface", "sub_inslab", "sub_crustal"]
    return cat.loc[k, cols].sort_values("time")


def main(out=None):
    out = ROOT / "runs" / "catalog" / S["run"] if out is None else ROOT / out
    if (out / "run.yaml").exists():
        raise SystemExit(f"{out} exists; a run is never edited")
    out.mkdir(parents=True, exist_ok=True)
    src = ROOT / S["catalog"]
    c = pd.read_csv(src / "catalog.csv", low_memory=False)
    g, o, tab = run(c, rejected(src, c.event_id[~has_depth(c)]))
    assert np.allclose(o[COLS].sum(axis=1), 1, atol=2e-4) and (o.rule != "").all() and o.event_id.is_unique
    cl = o[FIELDS]
    cat = c.merge(cl, on="event_id", how="left")
    k = cat.depth_assigned.notna()
    cat.loc[k, "depth"], cat.loc[k, "depth_sigma"] = cat.depth_assigned[k], cat.depth_assigned_sigma[k]
    cat.loc[k, "depth_kind"], cat.loc[k, "depth_src"] = "assigned", "assigned"
    geo = g[["event_id", "zone", "west", "ocean", "scotia", "sea", "an", "d_an", "dip", "sstr", "zrej", "nrej"]]
    files = {"catalog": cat, "classes": cl, "class_shares": tab.round(4), "class_geometry": geo, "m7_by_rule": review(cat)}
    for name, d in files.items():
        d.to_csv(out / f"{name}.csv", index=False)
    info = {"date": datetime.date.today().isoformat(), "reads": {"catalog": S["catalog"], "data": S["data"]}, "settings": S}
    (out / "run.yaml").write_text(yaml.safe_dump(info, sort_keys=False, allow_unicode=True))
    x = cl[(c.mw >= 4.45).to_numpy()]
    print("events", len(cl), "| Mw >= 4.5", len(x), "| split", int((x.cls == "split").sum()))
    print("summed weights:", x[COLS].sum().round(1).to_dict())
    print("rules:", x.rule.value_counts().to_dict())
    print("assigned depths:", int(k.sum()), "| Mw >= 7 by rule:", len(files["m7_by_rule"]))
    return out


if __name__ == "__main__":
    print(main(sys.argv[1] if len(sys.argv) > 1 else None))

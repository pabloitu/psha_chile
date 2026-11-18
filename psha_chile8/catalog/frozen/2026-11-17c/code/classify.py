"""Tectonic class of every earthquake, as weights (plan A7).

Each event gets a weight for interface, in-slab, crustal and outer rise that add up to 1, a sub-class by position and
the rule that decided. A class from the literature (class hints of overrides_A6.csv) comes first. West of the trench
is outer rise. Over the shallow slab the depth against the Slab2 surface gives scores after Haynie et al. (2026),
averaged over the depth error of the event (a normal error that cannot put the event above the ground). A mechanism
is compared with the interface mechanism at the epicentre (the Slab2 plane, slip along the plate convergence): the
misfit of the plane and of the slip, each with its own tolerance, give one measure; inside the ellipse the interface
odds are raised, outside it the interface weight is 0. Over the deeper slab the depth with its error says
above or below the slab surface. A weight of HARD or more becomes 1. An event without a measured depth is decided
by position where position is enough and otherwise takes the shares of the classified events of its bin. Checks
and figures in classify_check.py; method note in CLASSIFICATION.md; tests of the rule in explore/X5.
"""
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from match import OUT, tsec, year
from magnitude import sha

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

# settings
RUN, CAT = "2026-11-17c", "2026-11-17c"
SLAB, SLAB_V = REPO / "data" / "slab_2.0", "02.23.18"
TRENCH = REPO / "data" / "shapefiles" / "sam_nazca_trench.shp"
TRENCH_AN = REPO / "data" / "shapefiles" / "sam_antarctica_trench.shp"
ARC = REPO / "data" / "intraarc.shp"
SLAB_KM = 15.0
# interface: possible where the slab top is not deeper than IF_TOP. Half-width of the band around the slab top: a
# number of km, or "unc" (the Slab2 depth uncertainty at the epicentre; W_NONE where the grid has none). 15 km gives
# the right interface total on the events whose mechanism tells the class (merged/class_blind); "unc" gives 20 % less
IF_TOP, W, W_NONE = 50.0, 15.0, 15.0
# scores by depth over the shallow slab (Haynie et al. 2026, Table 1): interface fades between the depths SZ, crustal
# fades from DIFF[0] above to DIFF[1] below the slab top and from MOHO down to the slab top; NQ quantiles of the
# depth error
SZ, DIFF, MOHO, NQ = (50.0, 65.0), (-20.0, 20.0), 40.0, 61
# interface mechanism: plane misfit and slip misfit scaled by TOL (degrees), AZ the azimuth of the upper plate over
# the lower one; measure up to 1: interface odds times LR; beyond 1 the interface weight falls to 0 at EDGE (1: at once)
TOL, AZ, LR, EDGE = (20.0, 45.0), 257.0, 3.9, 1.0
# thrust on the plate contact of the runs up to 13 Nov: one nodal plane within NORM_CONE of the Slab2 plane, rake
# inside RAKE
NORM_CONE, RAKE = 35.0, (45.0, 135.0)
# mechanisms: "ellipse" (the measure above), "scores" (the depth scores without mechanisms), "add" (a thrust on the contact over a slab top within IF_TOP is
# interface, another mechanism rules the interface out), "exclude" (only the second part), "none" (not used)
MECH = "ellipse"
# a class with this weight or more becomes 1 (None: weights kept as they are)
HARD = 0.8
SIG_MIN = 5.0
# crustal; south of SOUTH_LAT the trench is the Antarctic one; the arc class ends where the arc polygon ends
CAP = 50.0
SOUTH_LAT, GAP_LAT = -46.15, -44.0
AN_WIDTH, AN_Z = 150.0, 60.0
# Chile Ridge fracture zones at the triple junction: between this latitude and SOUTH_LAT the events within this many
# km east of the trench are outer rise (strike-slip and normal mechanisms, one cluster with the events west of it)
RIDGE = (-45.5, 75.0)
# Scotia–Antarctic boundary: an event without a slab that is nearer to the SC/AN boundary of PB2002 (Bird 2003) than to
# the AN\SA trench and to the Magallanes–Fagnano traces MF of the fault database is outer rise (the boundary has no
# source in the model)
PB = HERE.parent / "data" / "pb2002_antarctic_trench_2026-11-15.geojson"
FAULTS = HERE.parent / "data" / "faults" / "faults_gem_extra_2026-11-15.shp"
MF = ("CL-056b", "CL-056c", "CL-056d", "AR-0056a", "AR-0056b", "AR-0056d", "AR-0056g")
# crustal grid of the source model (cell centres, 0.1°): a crustal event outside it keeps its weight and takes the
# sub-class "outside", which no fit, pattern or source reads
GRID = HERE.parent / "data" / "crustal_grid_01_2026-11-15.csv"
# no measured depth: in-slab where the slab top is below IF_TOP and every rejected depth is DEEP_REJ or more;
# otherwise the shares of the classified events (Mw >= SHARE_MMIN, from SHARE_FROM, in the domain) of the same bin
DEEP_REJ = 70.0
TOP_BINS, LAT_BINS, MAG_BINS = [50.0, 100.0], [24.0, 30.0, 38.0], [5.5]
# before OLD an event without a depth over the shallow slab or in the forearc takes no crustal share
OLD = 1900
TOP_LAB, LAT_LAB, MAG_LAB = ["≤ 50 km", "50–100 km", "> 100 km"], ["17–24° S", "24–30° S", "30–38° S", "38–46° S"], ["Mw 4.5–5.5", "Mw ≥ 5.5"]
SHARE_FROM, SHARE_MMIN, SHARE_N = 1976, 4.5, 30
# in-slab sub-classes
NEST = {"lon": -66.9, "lat": -24.0, "radius_deg": 0.8, "depth": (150.0, 320.0)}
# assigned depths of events with a literature class and no measured depth: interface on the slab top within IF_Z;
# in-slab at SLAB_FRAC of the Slab2 thickness below the top (the hypocentre of the in-slab sources)
IF_Z, SLAB_FRAC, SIG_ASSIGNED = (10.0, 50.0), 0.30, 20.0

CLS = ["interface", "in-slab", "crustal", "outer rise", "unclassified"]
COLS = ["w_interface", "w_inslab", "w_crustal", "w_outer_rise", "w_unclassified"]


# geometry
@lru_cache(None)
def slab():
    from scipy.interpolate import RegularGridInterpolator
    from scipy.spatial import cKDTree
    g, a = {}, None
    for k in ("dep", "thk", "dip", "str", "unc"):
        a = pd.read_csv(SLAB / f"sam_slab2_{k}_{SLAB_V}.xyz", header=None, names=["x", "y", "z"])
        z = a.pivot(index="y", columns="x", values="z")
        g[k] = RegularGridInterpolator((z.index.to_numpy(), z.columns.to_numpy()), z.to_numpy(), bounds_error=False)
        g[k + "_v"] = a.z.to_numpy()
    ok = np.isfinite(g["dep_v"])
    g["xy"], g["ok"] = np.c_[a.x.to_numpy(), a.y.to_numpy()][ok], ok
    g["tree"] = cKDTree(g["xy"] * [np.cos(np.radians(30)), 1])
    return g


def slab_at(lon, lat):
    """
    Slab2 at the epicentres: bilinear, and the nearest node within SLAB_KM at the edge of the model.

    Returns top (depth of the slab surface, km, positive down), thk, dip, str (from the nearest node, no averaging
    across 0 / 360) and unc (depth uncertainty of the surface, km); NaN where there is no slab.
    """
    g = slab()
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    p = np.c_[lat, np.mod(lon, 360)]
    d, j = g["tree"].query(np.c_[np.mod(lon, 360) * np.cos(np.radians(30)), lat])
    near = d * 111.195 <= SLAB_KM
    out = {}
    for k in ("dep", "thk", "dip", "unc"):
        v = g[k](p)
        out[k] = np.where(np.isfinite(v), v, np.where(near, g[k + "_v"][g["ok"]][j], np.nan))
    out["str"] = np.where(np.isfinite(out["dep"]), g["str_v"][g["ok"]][j], np.nan)
    return -out["dep"], out["thk"], out["dip"], out["str"], np.where(np.isfinite(out["dep"]), out["unc"], np.nan)


def utm(lon, lat):
    from pyproj import Transformer
    return Transformer.from_crs(4326, 32719, always_xy=True).transform(lon, lat)


def geoms(f):
    import cartopy.io.shapereader as shp
    import shapely
    return shapely.union_all(list(shp.Reader(str(f)).geometries()))


def trench_side(lon, lat, f):
    """Distance to a trench (km) and True on its seaward side (west of the trench at that latitude; south of its
    last point for the Antarctic trench, which turns east)."""
    import shapely
    import shapely.ops
    g = geoms(f)
    c = shapely.get_coordinates(g)
    o = np.argsort(c[:, 1])
    west = np.asarray(lon, float) < np.interp(np.asarray(lat, float), c[o, 1], c[o, 0])
    tl = shapely.ops.transform(lambda a, b: utm(np.asarray(a), np.asarray(b)), g)
    return shapely.distance(shapely.points(*utm(np.asarray(lon, float), np.asarray(lat, float))), tl) / 1e3, west


@lru_cache(None)
def scotia_lines():
    """SC/AN and AN\\SA of PB2002 and the Magallanes–Fagnano traces, in UTM."""
    import json
    import cartopy.io.shapereader as shp
    import shapely
    import shapely.ops
    pb = {f["properties"]["Name"]: shapely.geometry.shape(f["geometry"]) for f in json.load(open(PB))["features"]}
    mf = shapely.union_all([r.geometry for r in shp.Reader(str(FAULTS)).records() if r.attributes["fid"] in MF])
    return [shapely.ops.transform(lambda a, b: utm(np.asarray(a), np.asarray(b)), q) for q in (pb["SC/AN"], pb["AN\\SA"], mf)]


def on_scotia(lon, lat):
    """True where the SC/AN boundary is the nearest of the three lines of scotia_lines()."""
    import shapely
    p = shapely.points(*utm(np.asarray(lon, float), np.asarray(lat, float)))
    d = [shapely.distance(p, q) for q in scotia_lines()]
    return (d[0] < d[1]) & (d[0] < d[2])


def in_grid(lon, lat, f=GRID):
    """True where the point falls in a cell of the crustal grid (cell centres, half-width 0.05°)."""
    g = pd.read_csv(f)
    cells = set(zip(np.round(g.lon * 10).astype(int), np.round(g.lat * 10).astype(int)))
    q = zip(np.round(np.asarray(lon, float) * 10).astype(int), np.round(np.asarray(lat, float) * 10).astype(int))
    return np.array([k in cells for k in q], bool)


def arc_end(f=ARC):
    """Latitude of the southern end of the arc polygon; the arc class of events and faults ends there."""
    import shapely
    return shapely.bounds(geoms(f))[1]


def arc_zone(lon, lat, f=ARC):
    """forearc / arc / backarc from the arc polygon: inside it, or west / east of its edges at that latitude. North
    and south of the polygon its end edges are continued."""
    import shapely
    g = geoms(f)
    c = shapely.get_coordinates(shapely.boundary(g))
    b = np.round(c[:, 1] / 0.2)
    east, west = pd.Series(c[:, 0]).groupby(b).max(), pd.Series(c[:, 0]).groupby(b).min()
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    xe = np.interp(lat, east.index.to_numpy() * 0.2, east.to_numpy())
    xw = np.interp(lat, west.index.to_numpy() * 0.2, west.to_numpy())
    ins = shapely.contains_xy(g, lon, lat)
    return np.where(ins, "arc", np.where(lon > xe, "backarc", np.where(lon < xw, "forearc",
                    np.where(lon > (xe + xw) / 2, "backarc", "forearc"))))


def normal(strike, dip):
    th, di = np.radians(np.asarray(strike, float)), np.radians(np.asarray(dip, float))
    return np.stack([np.cos(th) * np.sin(di), -np.sin(th) * np.sin(di), np.cos(di)], -1)


def on_contact(m, sstr, sdip):
    """Thrust on the plate contact: one nodal plane within NORM_CONE of the slab plane (strike and dip from Slab2)
    with a rake inside RAKE."""
    ns = normal(sstr, sdip)
    ok = np.zeros(len(m), bool)
    for s, d, r in (("strike1", "dip1", "rake1"), ("strike2", "dip2", "rake2")):
        a = m[[s, d, r]].to_numpy(float)
        ang = np.degrees(np.arccos(np.clip(np.abs((normal(a[:, 0], a[:, 1]) * ns).sum(1)), 0, 1)))
        ok |= np.isfinite(a).all(1) & (ang <= NORM_CONE) & (a[:, 2] >= RAKE[0]) & (a[:, 2] <= RAKE[1])
    return ok


def nu(s, d, k):
    """Normal and slip vector (north, east, down) of a plane with strike, dip, rake in degrees."""
    s, d, k = (np.radians(np.asarray(v, float)) for v in (s, d, k))
    n = np.stack([-np.sin(d) * np.sin(s), np.sin(d) * np.cos(s), -np.cos(d)], -1)
    u = np.stack([np.cos(k) * np.cos(s) + np.cos(d) * np.sin(k) * np.sin(s),
                  np.cos(k) * np.sin(s) - np.cos(d) * np.sin(k) * np.cos(s), -np.sin(k) * np.sin(d)], -1)
    return n, u


def skew(s, d, k, ss, sd, tol=TOL, az=AZ):
    """
    Misfit of mechanisms to the interface mechanism at their epicentres.

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


def rejected(ids):
    """Smallest of the depths the sources give for these events, and how many there are (for an event without a
    measured depth every one of them was rejected in A4)."""
    import locate
    R = locate.records()[1]
    R = R[R.event_id.isin(ids) & np.isfinite(R.z)]
    return R.groupby("event_id").z.agg(["min", "count"])


def geometry(c, rej=None):
    """
    The catalogue with what the rules need.

    Returns one row per event: z, sig (measured depths only), known, top, thk, dip, sstr, unc, d (z − top), sea,
    zone, south, pat, an (Antarctic interface by position), em (misfit to the interface mechanism, NaN without
    mechanism or slab), mech_kind (thrust: on the plate contact by NORM_CONE and RAKE; other; none), hint, zrej and nrej (smallest and number of the rejected depths), yr.
    """
    known = ((c.depth_kind == "measured") & c.depth.notna()).to_numpy()
    g = pd.DataFrame({"event_id": c.event_id, "time": c.time, "yr": year(tsec(c.time)), "lon": c.lon, "lat": c.lat, "mw": c.mw,
                      "z": np.where(known, c.depth, np.nan), "sig": np.where(known, c.depth_sigma.clip(lower=SIG_MIN).fillna(SIG_MIN), np.nan),
                      "known": known, "depth_src": c.depth_src, "offshore": c.offshore, "in_domain": c.in_domain})
    g["top"], g["thk"], g["dip"], g["sstr"], g["unc"] = slab_at(c.lon, c.lat)
    g["d"] = g.z - g.top
    dnz, wnz = trench_side(c.lon, c.lat, TRENCH)
    dan, wan = trench_side(c.lon, c.lat, TRENCH_AN)
    south = (c.lat < SOUTH_LAT).to_numpy()
    ridge = ~south & (c.lat < RIDGE[0]).to_numpy() & (dnz <= RIDGE[1])
    g["d_trench"], g["sea"], g["south"] = np.where(south, dan, dnz), np.where(south, wan, wnz) | ridge, south
    g["zone"] = arc_zone(c.lon, c.lat)
    g["pat"] = (c.lat < arc_end()).to_numpy() | (g.top.isna() & (c.lat < GAP_LAT) & (g.zone != "arc")).to_numpy()
    mech = c[["strike1", "dip1", "rake1"]].notna().all(axis=1).to_numpy()
    thr = np.zeros(len(c), bool)
    k = mech & g.top.notna().to_numpy()
    thr[k] = on_contact(c[k], g.sstr[k], g.dip[k])
    g["em"] = np.nan
    g.loc[k, "em"] = skew(c.strike1[k], c.dip1[k], c.rake1[k], g.sstr[k], g.dip[k])
    rev = mech & (c[["rake1", "rake2"]].ge(RAKE[0]) & c[["rake1", "rake2"]].le(RAKE[1])).any(axis=1).to_numpy()
    g["mech_kind"] = np.where(thr, "thrust", np.where(mech, "other", "none"))
    g["an"] = south & ~g.sea & (dan <= AN_WIDTH) & ~(g.z > AN_Z).to_numpy() & ~(mech & ~rev)
    k = (g.top.isna() & ~g.an & ~g.sea).to_numpy()
    g.loc[k, "sea"] = on_scotia(c.lon[k], c.lat[k])
    g["hint"] = c.a6_class_hint if "a6_class_hint" in c else None
    rej = rejected(c.event_id[~known]) if rej is None else rej
    g["zrej"], g["nrej"] = c.event_id.map(rej["min"]).to_numpy(), c.event_id.map(rej["count"]).fillna(0).to_numpy()
    return g


# rules
def bins(g):
    """Bin of every event for the shares: slab-top range, latitude band, magnitude range (events outside the bands
    take the nearest one; no Mw counts as the lower range)."""
    return (np.digitize(g.top.to_numpy(float), TOP_BINS, right=True), np.digitize(-g.lat.to_numpy(float), LAT_BINS),
            np.digitize(np.nan_to_num(g.mw.to_numpy(float)), MAG_BINS))


def shares(g, P, base):
    """
    Shares of interface, in-slab and crustal among the classified events of each bin.

    P : weights (n, 3) of the events; base : the events that count. A bin with fewer than SHARE_N of them adds the
    other magnitude range, then the neighbouring latitude bands (both ranges).

    Returns S[top, lat, mag] -> three shares, and the table of bins (n of the bin itself, n used, what was borrowed).
    """
    it, il, im = bins(g)
    S, rows = np.full((len(TOP_BINS) + 1, len(LAT_BINS) + 1, len(MAG_BINS) + 1, 3), np.nan), []
    for a in range(S.shape[0]):
        for b in range(S.shape[1]):
            for m in range(S.shape[2]):
                k = base & (it == a) & (il == b) & (im == m)
                n0, how = int(k.sum()), ""
                if k.sum() < SHARE_N:
                    k, how = base & (it == a) & (il == b), "magnitude"
                if k.sum() < SHARE_N:
                    k, how = base & (it == a) & (np.abs(il - b) <= 1), "magnitude and latitude"
                s = P[k].sum(0)
                S[a, b, m] = s / s.sum() if s.sum() > 0 else np.nan
                rows.append({"slab_top": TOP_LAB[a], "lat": LAT_LAB[b], "mag": MAG_LAB[m], "n": n0, "n_used": int(k.sum()), "borrowed": how,
                             "interface": S[a, b, m, 0], "inslab": S[a, b, m, 1], "crustal": S[a, b, m, 2]})
    return S, pd.DataFrame(rows)


def ramp(x, x1, x2, p1, p2):
    return np.where(x < x1, p1, np.where(x > x2, p2, p1 + (p2 - p1) * (x - x1) / (x2 - x1)))


def by_depth(z, s, top, w, pk):
    """
    Interface, in-slab and crustal scores of Haynie et al. (2026) for a depth z ± s over a slab top, averaged over
    the depth error (normal, cut at the ground). w : half-width of the interface zone; pk : factor on the interface
    from the mechanism. Their Moho grid is replaced by MOHO.
    """
    from scipy.special import ndtr, ndtri
    lo = ndtr(-z / s)
    out = np.zeros((len(z), 3))
    for u in (np.arange(NQ) + 0.5) / NQ:
        x = z + s * ndtri(lo + u * (1 - lo))
        d = x - top
        pif = (np.abs(d) <= w) * ramp(x, *SZ, 1.0, 0.0) * pk
        pcr = (1 - pif) * ramp(d, *DIFF, 1.0, 0.0) * ramp(x, MOHO, np.maximum(top, MOHO + 1e-6), 1.0, 0.0)
        out += np.c_[pif, 1 - pif - pcr, pcr]
    return out / NQ


def lift(Q, k, lr=LR):
    """Interface odds of the rows k times lr; in-slab and crustal keep their ratio."""
    p = np.where(k, Q[:, 0] * lr / (Q[:, 0] * lr + 1 - Q[:, 0]), Q[:, 0])
    r = Q[:, 1:] / np.maximum(Q[:, 1:].sum(1, keepdims=True), 1e-12)
    return np.c_[p, (1 - p)[:, None] * r]


def classify(g, w=W, hard=HARD, if_top=IF_TOP, mech=MECH):
    """
    Class weights of every event.

    Parameters
    ----------
    g : DataFrame
        Output of geometry().
    w : "unc" or float
        Half-width of the interface band around the Slab2 top, km.
    hard : float or None
        A class with this weight or more becomes 1 (events with a measured depth only).
    if_top : float
        Interface is possible where the slab top is not deeper than this.
    mech : {"ellipse", "scores", "add", "exclude", "none"}
        See MECH.

    Returns
    -------
    out : DataFrame
        The five weights, cls (the class with weight 1, else split), cls_auto (the same from the rules alone, for
        events with a class hint), rule, W, n_candidates.
    tab : DataFrame
        The bins of the shares.
    """
    from scipy.special import ndtr
    n = len(g)
    z, s, top = g.z.to_numpy(float), g.sig.to_numpy(float), g.top.to_numpy(float)
    known, slab, sea, an = g.known.to_numpy(), np.isfinite(top), g.sea.to_numpy(), g.an.to_numpy()
    kind = g.mech_kind.to_numpy() if mech in ("add", "exclude") else np.full(n, "none")
    em = g.em.to_numpy(float) if mech == "ellipse" and "em" in g else np.full(n, np.nan)
    pk = np.where(em > 1, np.clip((EDGE - em) / max(EDGE - 1, 1e-9), 0, 1), 1.0) * (kind != "other")
    ins = np.isfinite(em) & (em <= 1)
    Wk = g.unc.to_numpy(float) if w == "unc" else np.full(n, float(w))
    Wk = np.where(slab, np.where(np.isfinite(Wk), Wk, W_NONE), np.nan)
    ifok = slab & (top <= if_top) & (pk > 0)
    P, rule = np.zeros((n, 5)), np.full(n, "", object)

    def put(m, j, name):
        m = m & (rule == "")
        P[m, j], rule[m] = 1.0, name

    put(sea, 3, "outer_rise")
    put(an, 0, "antarctic")
    if mech == "add":
        put(ifok & (kind == "thrust"), 0, "thrust")
    put(known & ~slab & (z <= CAP), 2, "no_slab")
    put(known & ~slab, 4, "no_slab_deep")
    put(~known & ~slab, 2, "nodepth_no_slab")
    # depth and its error (normal, cut at the Earth's surface): above the band, the band above and below the slab
    # surface, below the band
    with np.errstate(invalid="ignore"):
        f0 = ndtr(-z / s)
        a, b, c = (np.clip((ndtr((q - z) / s) - f0) / (1 - f0), 0, 1) for q in (top - Wk, top, top + Wk))
    pif = np.where(ifok, c - a, 0.0)
    pcr = np.where(z <= CAP, a + np.where(ifok, 0.0, b - a), 0.0)
    Q = np.c_[pif, 1 - pif - pcr, pcr]
    if mech in ("ellipse", "scores"):
        m = known & slab & (top <= if_top)
        Q[m] = lift(by_depth(z[m], s[m], top[m], Wk[m], pk[m]), ins[m])
    m = known & (rule == "")
    one = Q.max(1) >= (1 - 1e-9 if hard is None else hard)
    P[m, :3] = np.where(one[:, None], np.eye(3)[np.argmax(np.nan_to_num(Q), 1)], Q)[m]
    rule[m] = np.where(one[m], "depth", "depth_split")
    # no measured depth
    put(~known & (top > if_top) & (g.nrej.to_numpy() > 0) & (g.zrej.to_numpy() >= DEEP_REJ), 1, "nodepth_deep")
    hj = g.hint.map({q: i for i, q in enumerate(CLS[:4])}).to_numpy(float)
    hinted = np.isfinite(hj)
    H = np.zeros((n, 5))
    H[hinted, hj[hinted].astype(int)] = 1.0
    B = np.where(hinted[:, None], H, P)
    base = (hinted | (rule != "")) & slab & ~sea & ~an & g.in_domain.to_numpy() & (g.mw.to_numpy() >= SHARE_MMIN - 0.05) & \
        (g.yr.to_numpy() >= SHARE_FROM) & (B[:, :3].sum(1) > 0)
    S, tab = shares(g, B[:, :3], base)
    m = ~known & (rule == "")
    old = (g.yr.to_numpy() < OLD) & ((top <= if_top) | (g.zone.to_numpy() == "forearc"))
    q = S[bins(g)][m] * np.c_[ifok * pk, np.ones(n), ~old][m]
    q = np.where(np.nan_to_num(q).sum(1, keepdims=True) > 0, np.nan_to_num(q), np.c_[ifok, np.ones(n), ~old][m])
    P[m, :3], rule[m] = lift(q / q.sum(1, keepdims=True), ins[m]), "nodepth_share"
    auto = P.copy()
    P[hinted], rule[hinted] = H[hinted], "hint"
    name = lambda X: np.where(X.max(1) > 1 - 1e-9, np.array(CLS)[np.argmax(X, 1)], "split")
    out = pd.DataFrame(np.round(P, 4), columns=COLS, index=g.index)
    out["cls"], out["cls_auto"], out["rule"], out["W"] = name(P), name(auto), rule, np.round(Wk, 2)
    for i, c in enumerate(COLS):
        out[c.replace("w_", "a_")] = np.round(auto[:, i], 4)
    out["n_candidates"] = np.where(sea | an | ~slab, 1, 1 + ifok + (~known | (z <= CAP)))
    return out, tab


def subs(g, out):
    """Sub-class of each family the event has weight in, by position: sub_interface, sub_inslab, sub_crustal."""
    r = np.hypot((g.lon - NEST["lon"]) * np.cos(np.radians(g.lat)), g.lat - NEST["lat"])
    nest = g.known & (r <= NEST["radius_deg"]) & (g.z >= NEST["depth"][0]) & (g.z <= NEST["depth"][1])
    si = np.where(g.south, "antarctic_interface", "interface")
    ss = np.where(nest, "jujuy_nest", np.where(g.top <= IF_TOP, "intraslab_shallow", "intraslab_intermediate"))
    sc = np.where(in_grid(g.lon, g.lat), np.where(g.pat, "patagonia", g.zone), "outside")
    return pd.DataFrame({"sub_interface": np.where(out.w_interface > 0, si, ""), "sub_inslab": np.where(out.w_inslab > 0, ss, ""),
                         "sub_crustal": np.where(out.w_crustal > 0, sc, "")}, index=g.index)


def assigned(g, out):
    """Depth of the events with a literature class and no measured depth: interface on the slab top kept within
    IF_Z, in-slab at SLAB_FRAC of the thickness below the top; σ SIG_ASSIGNED. Never read by the rules."""
    k = (out.rule == "hint") & ~g.known & g.top.notna()
    z = np.where(k & (out.cls == "interface"), g.top.clip(*IF_Z), np.where(k & (out.cls == "in-slab"), g.top + SLAB_FRAC * g.thk, np.nan))
    return pd.DataFrame({"depth_assigned": np.round(z, 1), "depth_assigned_sigma": np.where(np.isfinite(z), SIG_ASSIGNED, np.nan)}, index=g.index)


def run(c, **kw):
    """Geometry, weights, sub-classes and assigned depths of a catalogue: (g, classes table, bins of the shares)."""
    g = geometry(c)
    out, tab = classify(g, **kw)
    out = pd.concat([out, subs(g, out), assigned(g, out)], axis=1)
    out["d"] = g.d.round(2)
    for k in ("top", "thk", "unc"):
        out[k] = g[k].round(2)
    out["mech_kind"], out["mech_m"] = g.mech_kind, g.em.round(3)
    out.insert(0, "event_id", g.event_id)
    return g, out, tab


FIELDS = ["event_id"] + COLS + ["cls", "cls_auto", "rule", "sub_interface", "sub_inslab", "sub_crustal", "top", "thk", "unc", "d", "W",
                                "mech_kind", "mech_m", "n_candidates", "depth_assigned", "depth_assigned_sigma"]


def manifest(files):
    f = OUT / "MANIFEST.csv"
    m = pd.read_csv(f)
    new = pd.DataFrame([{"file": str(p.relative_to(OUT)), "run": RUN, "rows": len(d), "sha256": sha(p)} for p, d in files.items()])
    pd.concat([m[~m.file.isin(new.file)], new], ignore_index=True).to_csv(f, index=False)


def main():
    c = pd.read_csv(OUT / f"catalog_{CAT}.csv", low_memory=False)
    g, out, tab = run(c)
    cl = out[FIELDS]
    cat = c.merge(cl, on="event_id", how="left")
    k = cat.depth_assigned.notna()
    cat.loc[k, "depth"], cat.loc[k, "depth_sigma"] = cat.depth_assigned[k], cat.depth_assigned_sigma[k]
    cat.loc[k, "depth_kind"], cat.loc[k, "depth_src"] = "assigned", "assigned"
    files = {OUT / f"classes_{RUN}.csv": cl, OUT / f"catalog_{RUN}.csv": cat, OUT / f"class_shares_{RUN}.csv": tab.round(4)}
    for p, d in files.items():
        d.to_csv(p, index=False)
    manifest(files)
    x = cl[(g.in_domain & (g.mw >= 4.45)).to_numpy()]
    print("events", len(cl), "| Mw >= 4.5 in the domain", len(x), "| split", int((x.cls == "split").sum()))
    print("summed weights:", x[COLS].sum().round(1).to_dict())
    print("rules:", x.rule.value_counts().to_dict())
    print("assigned depths:", int(k.sum()))
    print(tab.round(3).to_string())


if __name__ == "__main__":
    main()

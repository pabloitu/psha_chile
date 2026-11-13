"""X4 (classification): every event of the merged catalogue against Slab2, the trench and the arc polygon, under a
grid of rule variants. Exploration only: reads catalog/merged, writes to explore/X4/tables and cache."""
import itertools
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT))

# inputs
RUN, A3 = "2026-11-13", "2026-11-11"
CAT = ROOT / "catalog" / "merged" / f"catalog_{RUN}.csv"
SLAB = REPO / "data" / "slab_2.0"
TRENCH = REPO / "data" / "shapefiles" / "sam_nazca_trench.shp"
TRENCH_AN = REPO / "data" / "shapefiles" / "sam_antarctica_trench.shp"
ARC = REPO / "data" / "intraarc.shp"
RM = ROOT / "catalog" / "merged" / "review" / f"rm18_matches_{A3}.csv"
TAB, CACHE = HERE / "tables", HERE / "cache"

# interface
IF_TOP = 50.0
W = [10.0, 15.0, 20.0]
MECH_TOP, MECH_EXTRA = 65.0, 10.0
NORM_CONE, RAKE = 35.0, (45.0, 135.0)
# crustal
CAP = 50.0
SOUTH_LAT, GAP_LAT = -46.15, -44.0
AN_WIDTH, AN_Z = 150.0, 60.0
# slab
SLAB_KM = 15.0
# in-slab classes: shallow where the slab top is above SHALLOW_TOP, the Jujuy nest (as cat_handler_2), intermediate the rest
SHALLOW_TOP = 50.0
NEST = {"lon": -66.9, "lat": -24.0, "radius_deg": 0.8, "depth": (170.0, 320.0)}
# Ruiz and Madariaga (2018) classes, set after the rules
RM_CLASS = {"interface": "interface", "intraslab": "in-slab", "crustal": "crustal", "outer_rise": "outer rise"}
# variants and the one the others are compared with
GRID = {"w": W, "sig": [False, True], "mech": [False, True], "below": ["in-slab", "unclassified"]}
BASE = {"w": 15.0, "sig": False, "mech": True, "below": "in-slab"}
MMIN = 4.5
BIG = [4.5, 5.5, 7.0]

CLASSES = ["interface", "in-slab", "crustal forearc", "crustal arc", "crustal backarc", "crustal Patagonia",
           "outer rise", "below slab", "unknown depth", "unclassified"]
SUB = ["intraslab_shallow", "intraslab_intermediate", "jujuy_nest"]
FAMILY = {"interface": "interface", "in-slab": "in-slab", "crustal forearc": "crustal", "crustal arc": "crustal",
          "crustal backarc": "crustal", "crustal Patagonia": "crustal", "outer rise": "none", "below slab": "none",
          "unknown depth": "none", "unclassified": "none"}


def tag(v):
    return f"w{v['w']:.0f}_{'sig' if v['sig'] else 'nosig'}_{'mech' if v['mech'] else 'nomech'}_{'belowslab' if v['below'] == 'in-slab' else 'belowout'}"


def variants():
    return [dict(zip(GRID, q)) for q in itertools.product(*GRID.values())]


# geometry
@lru_cache(None)
def slab():
    from scipy.interpolate import RegularGridInterpolator
    from scipy.spatial import cKDTree
    g, a = {}, None
    for k in ("dep", "thk", "dip", "str"):
        a = pd.read_csv(SLAB / f"sam_slab2_{k}_02.23.18.xyz", header=None, names=["x", "y", "z"])
        z = a.pivot(index="y", columns="x", values="z")
        g[k] = RegularGridInterpolator((z.index.to_numpy(), z.columns.to_numpy()), z.to_numpy(), bounds_error=False)
        g[k + "_v"] = a.z.to_numpy()
    ok = np.isfinite(g["dep_v"])
    g["xy"], g["ok"] = np.c_[a.x.to_numpy(), a.y.to_numpy()][ok], ok
    g["tree"] = cKDTree(g["xy"] * [np.cos(np.radians(30)), 1])
    return g


def slab_at(lon, lat):
    """Slab2 top (km, positive down), thickness, dip and strike at the epicentres: bilinear, and the nearest node
    within SLAB_KM at the edge of the model. The strike comes from the nearest node (no averaging across 0 / 360)."""
    g = slab()
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    p = np.c_[lat, np.mod(lon, 360)]
    d, j = g["tree"].query(np.c_[np.mod(lon, 360) * np.cos(np.radians(30)), lat])
    near = d * 111.195 <= SLAB_KM
    out = {}
    for k in ("dep", "thk", "dip"):
        v = g[k](p)
        out[k] = np.where(np.isfinite(v), v, np.where(near, g[k + "_v"][g["ok"]][j], np.nan))
    out["str"] = np.where(np.isfinite(out["dep"]), g["str_v"][g["ok"]][j], np.nan)
    return -out["dep"], out["thk"], out["dip"], out["str"]


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


def interface_like(m, sstr, sdip):
    """Thrust on the interface plane: one nodal plane within NORM_CONE of the slab plane (strike and dip from Slab2)
    with a rake inside RAKE."""
    ns = normal(sstr, sdip)
    ok = np.zeros(len(m), bool)
    for s, d, r in (("strike1", "dip1", "rake1"), ("strike2", "dip2", "rake2")):
        a = m[[s, d, r]].to_numpy(float)
        ang = np.degrees(np.arccos(np.clip(np.abs((normal(a[:, 0], a[:, 1]) * ns).sum(1)), 0, 1)))
        ok |= np.isfinite(a).all(1) & (ang <= NORM_CONE) & (a[:, 2] >= RAKE[0]) & (a[:, 2] <= RAKE[1])
    return ok


def geometry(c):
    """The catalogue with everything the rules need: z, sig, known, top, thk, dip, dn, sea, zone, pat, mech, ifl."""
    g = pd.DataFrame({"event_id": c.event_id, "time": c.time, "lon": c.lon, "lat": c.lat, "mw": c.mw,
                      "z": c.depth, "sig": c.depth_sigma, "known": (c.depth_kind == "measured") & c.depth.notna(),
                      "depth_src": c.depth_src, "in_domain": c.in_domain})
    g["top"], g["thk"], g["dip"], g["sstr"] = slab_at(c.lon, c.lat)
    g["d"] = g.z - g.top
    g["dn"] = g.d * np.cos(np.radians(g.dip))
    dnz, wnz = trench_side(c.lon, c.lat, TRENCH)
    dan, wan = trench_side(c.lon, c.lat, TRENCH_AN)
    south = (c.lat < SOUTH_LAT).to_numpy()
    g["d_trench"] = np.where(south, dan, dnz)
    g["sea"] = np.where(south, wan, wnz)
    g["zone"] = arc_zone(c.lon, c.lat)
    g["pat"] = south | (g.top.isna() & (c.lat < GAP_LAT) & (g.zone != "arc")).to_numpy()
    g["an_if"] = g.pat & ~g.sea & (dan <= AN_WIDTH) & ~(g.z > AN_Z)
    g["mech"] = c[["strike1", "dip1", "rake1"]].notna().all(axis=1).to_numpy()
    g["ifl"] = False
    k = (g.mech & g.top.notna()).to_numpy()
    g.loc[k, "ifl"] = interface_like(c[k], g.sstr[k], g.dip[k])
    g["rake1"] = c.rake1
    return g


# rules
def classify(g, w=15.0, sig=False, mech=True, below="in-slab"):
    """
    Class of every event under one rule variant.

    Parameters
    ----------
    g : DataFrame
        Output of geometry().
    w : float
        Half-width of the interface band around the Slab2 top, km.
    sig : bool
        Widen the band, and the bottom of the plate, by the event's own depth sigma.
    mech : bool
        Use mechanisms: an interface-like mechanism makes the event interface within the band plus MECH_EXTRA where
        the slab top is above MECH_TOP (also with unknown depth); another mechanism inside the band takes it out
        (in-slab below the top, crustal above).
    below : {"in-slab", "unclassified"}
        What an event deeper than top + thickness becomes: in-slab, or the class "below slab".

    Returns
    -------
    cls, rule : arrays of str
    """
    z, top, thk = g.z.to_numpy(float), g.top.to_numpy(float), g.thk.to_numpy(float)
    known, slab, sea, pat = g.known.to_numpy(), np.isfinite(g.top.to_numpy(float)), g.sea.to_numpy(), g.pat.to_numpy()
    s = np.nan_to_num(g.sig.to_numpy(float)) if sig else 0.0
    tol, d = w + s, z - top
    hm, ifl = g.mech.to_numpy() & mech, g.ifl.to_numpy() & mech
    crust = "crustal " + g.zone.to_numpy().astype(object)
    band = known & slab & (np.abs(d) <= tol)
    rules = [
        ("outer_rise", sea, "outer rise"),
        ("unk_mech", ~known & ifl & (top <= MECH_TOP), "interface"),
        ("unk", ~known, "unknown depth"),
        ("pat", pat & (z <= CAP), "crustal Patagonia"),
        ("pat_deep", pat, "unclassified"),
        ("noslab", ~slab & (z <= CAP), crust),
        ("noslab_deep", ~slab, "unclassified"),
        ("below", d > thk + s, "in-slab" if below == "in-slab" else "below slab"),
        ("mech_if", ifl & (top <= MECH_TOP) & (np.abs(d) <= tol + MECH_EXTRA), "interface"),
        ("band_other_mech", band & (top <= IF_TOP) & hm, np.where((d < 0) & (z <= CAP), crust, "in-slab")),
        ("band", band & (top <= IF_TOP), "interface"),
        ("above", (d < -tol) & (z <= CAP), crust),
        ("above_deep", d < -tol, "unclassified"),
        ("slab", np.ones(len(g), bool), "in-slab"),
    ]
    cls, rule = np.full(len(g), None, object), np.full(len(g), None, object)
    for name, m, v in rules:
        m = m & (cls == None)  # noqa: E711
        cls[m] = v[m] if isinstance(v, np.ndarray) else v
        rule[m] = name
    return cls, rule


def sub(g, cls):
    """In-slab class of the in-slab events: jujuy_nest inside NEST (measured depth), intraslab_shallow where the slab top
    is above SHALLOW_TOP, intraslab_intermediate elsewhere; empty for the other classes."""
    r = np.hypot((g.lon - NEST["lon"]) * np.cos(np.radians(g.lat)), g.lat - NEST["lat"])
    nest = g.known & (r <= NEST["radius_deg"]) & (g.z >= NEST["depth"][0]) & (g.z <= NEST["depth"][1])
    out = np.where(nest, "jujuy_nest", np.where(g.top < SHALLOW_TOP, "intraslab_shallow", "intraslab_intermediate"))
    return np.where(np.asarray(cls) == "in-slab", out, "")


def rm18(g, cls, f=RM):
    """Classes with the events Ruiz and Madariaga (2018) name set to the class of the paper (crustal: sub-class by
    position). Returns the classes and a mask of the events set."""
    r = pd.read_csv(f)
    c = g.event_id.map(r.set_index("event_id").rm_class.map(RM_CLASS))
    c = np.where(c == "crustal", np.where(g.pat, "crustal Patagonia", "crustal " + g.zone.astype(str)), c)
    k = pd.notna(c)
    return np.where(k, c, cls), np.asarray(k)


def p_interface(g, w=15.0):
    """Probability that the true depth lies inside the band, for a normal depth error of the event's sigma."""
    from scipy.stats import norm
    s = g.sig.to_numpy(float)
    d = (g.z - g.top).to_numpy(float)
    p = norm.cdf((w - d) / s) - norm.cdf((-w - d) / s)
    return np.where(g.known & (g.top <= IF_TOP) & ~g.sea & ~g.pat, p, np.nan)


def changes(a, b, mw):
    k = a != b
    fa, fb = pd.Series(a).map(FAMILY).to_numpy(), pd.Series(b).map(FAMILY).to_numpy()
    out = {}
    for m in BIG:
        out[f"class_m{m:g}"] = int((k & (mw >= m)).sum())
        out[f"family_m{m:g}"] = int(((fa != fb) & (mw >= m)).sum())
    return out


def run():
    TAB.mkdir(exist_ok=True)
    CACHE.mkdir(exist_ok=True)
    c = pd.read_csv(CAT, low_memory=False)
    g = geometry(c)
    V = variants()
    for v in V:
        c, r = classify(g, **v)
        g[tag(v)], k = rm18(g, c)
        if v == BASE:
            g["cls_auto"], g["cls"], g["rule"] = c, g[tag(v)], np.where(k, "rm18", r)
    g["sub"] = sub(g, g.cls)
    g["p_if"] = p_interface(g)
    g.to_csv(CACHE / "x4b_events.csv.gz", index=False)
    x = g[g.in_domain & (g.mw >= MMIN)].reset_index(drop=True)
    x.to_csv(TAB / "x4b_events_m45.csv", index=False)
    mw = x.mw.to_numpy()
    cols = [tag(v) for v in V]

    # counts per class and variant
    rows = []
    for v in V:
        for m in BIG:
            n = x[tag(v)][mw >= m].value_counts().reindex(CLASSES, fill_value=0)
            rows.append({**v, "variant": tag(v), "mmin": m, **n.to_dict()})
    pd.DataFrame(rows).to_csv(TAB / "x4b_counts.csv", index=False)
    n = pd.concat({f"Mw ≥ {m:g}": x.cls[mw >= m].value_counts() for m in BIG}, axis=1).reindex(CLASSES).fillna(0).astype(int)
    n.insert(0, "all events in the domain", g.cls[g.in_domain].value_counts().reindex(CLASSES).fillna(0).astype(int))
    n.to_csv(TAB / "x4b_counts_baseline.csv")
    n = pd.concat({f"Mw ≥ {m:g}": x["sub"][(x["sub"] != "") & (mw >= m)].value_counts() for m in BIG}, axis=1).reindex(SUB).fillna(0).astype(int)
    n.insert(0, "all events in the domain", g["sub"][g.in_domain & (g["sub"] != "")].value_counts().reindex(SUB).fillna(0).astype(int))
    n.to_csv(TAB / "x4b_counts_inslab.csv")
    pd.crosstab(x.rule, x.cls).to_csv(TAB / "x4b_rules_baseline.csv")

    # each variant against the baseline, and one factor at a time
    rows = [{**v, "variant": tag(v), "against": "baseline", **changes(x[tag(BASE)].to_numpy(), x[tag(v)].to_numpy(), mw)} for v in V]
    for f, vals in GRID.items():
        for a, b in itertools.combinations(vals, 2):
            va, vb = {**BASE, f: a}, {**BASE, f: b}
            rows.append({"variant": f"{f}: {a} → {b}", "against": "one factor, others as baseline",
                         **changes(x[tag(va)].to_numpy(), x[tag(vb)].to_numpy(), mw)})
            t = pd.crosstab(x[tag(va)], x[tag(vb)])
            t.to_csv(TAB / f"x4b_transition_{f}_{a}_{b}.csv".replace(" ", ""))
    for f, vals in GRID.items():
        hi = {m: [] for m in BIG}
        for o in [dict(zip([q for q in GRID if q != f], q)) for q in itertools.product(*[GRID[q] for q in GRID if q != f])]:
            for a, b in itertools.combinations(vals, 2):
                ch = changes(x[tag({**o, f: a})].to_numpy(), x[tag({**o, f: b})].to_numpy(), mw)
                for m in BIG:
                    hi[m].append(ch[f"class_m{m:g}"])
        rows.append({"variant": f"{f}: range over all settings of the other factors", "against": "min–max of the pairwise changes",
                     **{f"class_m{m:g}": f"{min(hi[m])}–{max(hi[m])}" for m in BIG}})
    nun = x[cols].nunique(axis=1).to_numpy()
    fun = x[cols].apply(lambda q: q.map(FAMILY)).nunique(axis=1).to_numpy()
    rows.append({"variant": "any of the 24", "against": "events with more than one class",
                 **{f"class_m{m:g}": int(((nun > 1) & (mw >= m)).sum()) for m in BIG},
                 **{f"family_m{m:g}": int(((fun > 1) & (mw >= m)).sum()) for m in BIG}})
    pd.DataFrame(rows).to_csv(TAB / "x4b_changes.csv", index=False)

    # the large events, class by class
    b = x[mw >= 7.0].copy()
    b["n_classes"] = b[cols].nunique(axis=1)
    b["classes"] = b[cols].apply(lambda q: " / ".join(sorted(set(q))), axis=1)
    b[["event_id", "time", "lon", "lat", "z", "sig", "depth_src", "mw", "top", "d", "mech", "ifl", "cls_auto", "cls", "sub", "rule", "n_classes",
       "classes"]].round(2).to_csv(TAB / "x4b_m7.csv", index=False)
    return g


if __name__ == "__main__":
    run()

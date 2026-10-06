# Tectonic class of every event from Slab2, the intra-arc polygon, the trench
# and the focal mechanism. Rules, in order (cls_rule names the one applied):
#   remark      Cabello flags the event crustal: forearc, or intraarc inside the polygon
#   nest        inside a deep nest (depth known)
#   pat_*       south of SOUTH_LAT (Antarctic plate, no Slab2): seaward of TRENCH_AN
#               outer_rise; within PAT_WIDTH_KM of it patagonia_interface; else
#               patagonia_crustal
#   outer_rise  seaward of the trench (side of the local trench segment, not west)
#   arc_*       inside the intra-arc polygon: by depth against the slab top
#   backarc     east of the polygon, shallower than BACKARC_MAX_Z: backarc; depth unknown there:
#               unresolved, then the neighbour vote (unk_vote) decides crustal or in-slab
#   no_slab     no Slab2 node within SLAB_MAX_KM
#   below       deeper than slab top + thickness
#   cone        depth known, slab top < IF_MECH_MAX_TOP, interface-like mechanism and
#               within the band plus MECH_EXTRA: interface
#   band_*      slab top < IF_MAX_TOP, depth known: above the band forearc, below
#               intra_slab, inside it interface unless the mechanism says otherwise
#   deep_*      slab top >= IF_MAX_TOP: slab_deep from DEEP_TOL above the top or deeper
#               than FOREARC_MAX_Z (deep_above), else forearc
#   unk_*       depth unknown (UNKNOWN_DEPTH), slab top < IF_MAX_TOP (IF_MAX_TOP_HIST
#               for assigned depths): interface if the mechanism is interface-like
#               (up to IF_MECH_MAX_TOP) or missing; else intra_slab when normal
#               faulting, forearc otherwise
#   unk_deep    depth unknown over a slab top >= IF_MAX_TOP: unresolved
#   unk_vote    still unresolved: the class of the located events around it (VOTE_*)
#   pre_year    intra_slab before PRE_YEAR -> interface

import numpy as np
import pandas as pd
import shapely
from scipy.spatial import cKDTree

from cat_handler_2 import config as C

R = 6371.0


def unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]


def slab():
    d = [pd.read_csv(C.SLAB[k], header=None, names=["lon", "lat", k]) for k in ("dep", "str", "dip", "thk")]
    s = d[0].merge(d[1], on=["lon", "lat"]).merge(d[2], on=["lon", "lat"]).merge(d[3], on=["lon", "lat"], how="left")
    s = s.dropna(subset=["dep", "str", "dip"]).reset_index(drop=True)
    s["lon"] = np.where(s["lon"] > 180, s["lon"] - 360, s["lon"])
    s["dep"] = -s["dep"]
    return s, cKDTree(unit(s["lon"], s["lat"]))


def seaward(tr, lon, lat):
    """
    True on the ocean side of the trench: the point and a point LAND_EAST degrees
    east of its nearest trench point lie on opposite sides of the local trench segment.
    """
    tr = shapely.line_merge(tr)
    p = shapely.points(lon, lat)
    s = shapely.line_locate_point(tr, p)
    a = shapely.line_interpolate_point(tr, np.maximum(s - 0.01, 0))
    b = shapely.line_interpolate_point(tr, s + 0.01)
    ax, ay, bx, by = shapely.get_x(a), shapely.get_y(a), shapely.get_x(b), shapely.get_y(b)
    cx, cy = (ax + bx) / 2, (ay + by) / 2
    side = lambda x, y: np.sign((bx - ax) * (y - ay) - (by - ay) * (x - ax))
    return side(np.asarray(lon), np.asarray(lat)) * side(cx + C.LAND_EAST, cy) < 0


def footprint():
    """
    Antarctic trench (merged line) and the patagonia_interface footprint: the band
    PAT_WIDTH_KM landward of it, as a polygon in lon/lat.
    """
    import geopandas as gpd
    tr = shapely.line_merge(shapely.union_all(gpd.read_file(C.TRENCH_AN).to_crs(4326).geometry.values))
    crs = "+proj=aeqd +lat_0=-52 +lon_0=-72 +units=m"
    g = gpd.GeoSeries([tr], crs=4326).to_crs(crs)
    line = g.iloc[0]
    off = [shapely.offset_curve(line, s * C.PAT_WIDTH_KM * 1000) for s in (1, -1)]
    east = [gpd.GeoSeries([o], crs=crs).to_crs(4326).iloc[0].centroid.x for o in off]
    o = list(off[int(np.argmax(east))].coords)
    a = list(line.coords)
    if np.hypot(*np.subtract(o[0], a[0])) > np.hypot(*np.subtract(o[-1], a[0])):
        o = o[::-1]
    poly = shapely.make_valid(shapely.Polygon(a + o[::-1]))
    return tr, gpd.GeoSeries([poly], crs=crs).to_crs(4326).iloc[0]


def axes(strike, dip):
    th, di = np.radians(strike), np.radians(dip)
    us = np.stack([np.sin(th), np.cos(th), 0 * th], 1)
    ud = np.stack([np.cos(th) * np.cos(di), -np.sin(th) * np.cos(di), -np.sin(di)], 1)
    n = np.cross(ud, us)
    return us, ud, n / np.linalg.norm(n, axis=1, keepdims=True)


def interface_like(ev, sstr, sdip):
    """Either nodal plane within NORM_CONE of the slab plane and slipping with the convergence (ENU, as before)."""
    _, _, ns = axes(sstr, sdip)
    az = np.radians(C.CONV_AZ)
    vc = np.array([np.sin(az), np.cos(az), 0.0])
    ok = np.zeros(len(ev), bool)
    for s, d, r in (("strike1", "dip1", "rake1"), ("strike2", "dip2", "rake2")):
        a = ev[[s, d, r]].to_numpy(float)
        us, ud, n = axes(a[:, 0], a[:, 1])
        geo = np.abs((n * ns).sum(1)) >= np.cos(np.radians(C.NORM_CONE))
        ra = np.radians(a[:, 2])[:, None]
        v = np.cos(ra) * us + np.sin(ra) * ud
        e = vc - (n @ vc)[:, None] * n
        e /= np.linalg.norm(e, axis=1, keepdims=True)
        slip = (v * e).sum(1) >= np.cos(np.radians(C.SLIP_CONE)) - 1e-9
        ok |= np.isfinite(a).all(1) & geo & slip
    return ok


def classify(ev):
    """
    Class and deciding rule of every event.

    Parameters
    ----------
    ev : DataFrame
        Output of the mech stage.

    Returns
    -------
    ev : DataFrame
        With class, cls_rule, slab_top, slab_thk, slab_str, slab_dip, dz (depth - slab_top),
        dist_an (km to the Antarctic trench).
    info : dict
    """
    import geopandas as gpd
    ev = ev.reset_index(drop=True).copy()
    lon, lat = ev["longitude"].to_numpy(float), ev["latitude"].to_numpy(float)
    z = pd.to_numeric(ev["depth"], errors="coerce").to_numpy(float)
    known = ~ev["depth_status"].isin(C.UNKNOWN_DEPTH).to_numpy() & np.isfinite(z)

    s, tree = slab()
    dist, j = tree.query(unit(lon, lat))
    near = 2 * R * np.arcsin(np.clip(dist / 2, 0, 1)) <= C.SLAB_MAX_KM
    for k, c in (("dep", "slab_top"), ("thk", "slab_thk"), ("str", "slab_str"), ("dip", "slab_dip")):
        ev[c] = np.where(near, s[k].to_numpy()[j], np.nan)
    top, thk = ev["slab_top"].to_numpy(), ev["slab_thk"].to_numpy()
    ev["dz"] = np.where(known, z - top, np.nan)

    arc = shapely.union_all(gpd.read_file(C.INTRAARC_SHP).to_crs(4326).geometry.values)
    tr = shapely.union_all(gpd.read_file(C.TRENCH_SHP).to_crs(4326).geometry.values)
    pts = shapely.points(lon, lat)
    inarc = shapely.contains_xy(arc, lon, lat)
    west = seaward(tr, lon, lat)
    bd = arc.boundary
    east = ~inarc & (lon > shapely.get_x(shapely.line_interpolate_point(bd, shapely.line_locate_point(bd, pts))))

    an = shapely.line_merge(shapely.union_all(gpd.read_file(C.TRENCH_AN).to_crs(4326).geometry.values))
    q = shapely.line_interpolate_point(an, shapely.line_locate_point(an, pts))
    ev["dist_an"] = np.round(2 * R * np.arcsin(np.clip(np.linalg.norm(unit(lon, lat) - unit(shapely.get_x(q), shapely.get_y(q)), axis=1) / 2, 0, 1)), 1)
    south = lat < C.SOUTH_LAT
    pat_if = south & (ev["dist_an"].to_numpy() <= C.PAT_WIDTH_KM) & (~known | (z <= C.PAT_MAX_Z))

    nest = np.zeros(len(ev), bool)
    for n in C.NESTS:
        r = np.hypot((lon - n["lon"]) * np.cos(np.radians(lat)), lat - n["lat"])
        nest |= known & (r <= n["radius_deg"]) & (z >= n["depth"][0]) & (z <= n["depth"][1])

    mech = ev[["strike1", "dip1", "rake1"]].notna().all(axis=1).to_numpy()
    ifl = np.zeros(len(ev), bool)
    k = mech & near
    ifl[k] = interface_like(ev[k], ev.loc[k, "slab_str"].to_numpy(), ev.loc[k, "slab_dip"].to_numpy())
    normal = ev["rake1"].between(*C.NORMAL_RAKE).to_numpy()
    tol = ev["depth_status"].map(C.IF_TOL).fillna(max(C.IF_TOL.values())).to_numpy()
    below = known & near & ((z > top + thk) | ~np.isfinite(thk))
    shallow = near & (top < C.IF_MAX_TOP)
    mdom = near & (top < C.IF_MECH_MAX_TOP)
    hist = ev["depth_status"].eq("assigned").to_numpy()
    ushal = near & (top < np.where(hist, C.IF_MAX_TOP_HIST, C.IF_MAX_TOP))
    crust = ev["general_remarks"].eq("Crustal").to_numpy()

    rules = [
        ("remark", crust, np.where(inarc, "intraarc", "forearc")),
        ("nest", nest, "deep_nest"),
        ("pat_outer", south & seaward(an, lon, lat), "outer_rise"),
        ("pat_interface", pat_if, "patagonia_interface"),
        ("pat_crustal", south, "patagonia_crustal"),
        ("outer_rise", west, "outer_rise"),
        ("arc_unknown", inarc & ~known, "unresolved"),
        ("arc_below", inarc & near & below, "deep_unknown"),
        ("arc_slab", inarc & near & known & (z >= top - C.DEEP_TOL), "slab_deep"),
        ("arc_shallow", inarc & known & (z <= C.INTRAARC_SHALLOW), "intraarc"),
        ("arc_deep", inarc & known & ((z <= 90) | near), "intraarc"),
        ("arc_noslab", inarc & known, "slab_deep"),
        ("backarc", east & known & (z < C.BACKARC_MAX_Z), "backarc"),
        ("backarc_unknown", east & ~known, "unresolved"),
        ("no_slab", ~near, "unclassified"),
        ("below", below, "deep_unknown"),
        ("cone", known & mdom & ifl & (np.abs(z - top) <= tol + C.MECH_EXTRA), "slab_interface"),
        ("band_forearc", known & shallow & (z <= top - tol), "forearc"),
        ("band_intraslab", known & shallow & (z >= top + tol), "intra_slab"),
        ("band_mech", known & shallow & mech, np.where(z < top, "forearc", "intra_slab")),
        ("band_nomech", known & shallow, "slab_interface"),
        ("deep_slab", known & (z >= top - C.DEEP_TOL), "slab_deep"),
        ("deep_above", known & (z > C.FOREARC_MAX_Z), "slab_deep"),
        ("deep_forearc", known, "forearc"),
        ("unk_cone", mdom & ifl, "slab_interface"),
        ("unk_normal", ushal & mech & normal, "intra_slab"),
        ("unk_mech", ushal & mech, "forearc"),
        ("unk_nomech", ushal, "slab_interface"),
        ("unk_deep", np.ones(len(ev), bool), "unresolved"),
    ]
    cls = np.full(len(ev), None, object)
    rule = np.full(len(ev), None, object)
    for name, m, c in rules:
        m = m & (cls == None)
        cls[m] = c[m] if isinstance(c, np.ndarray) else c
        rule[m] = name
    fam = {c: f for f, cs in C.VOTE_FAMILIES.items() for c in cs}
    pool = np.flatnonzero(known & np.isin(cls.astype(str), list(fam)))
    todo = np.flatnonzero(cls == "unresolved")
    if len(pool) and len(todo):
        t = cKDTree(unit(lon[pool], lat[pool]))
        r = 2 * np.sin(C.VOTE_KM / R / 2)
        for i, nb in zip(todo, t.query_ball_point(unit(lon[todo], lat[todo]), r)):
            if len(nb) < C.VOTE_MIN:
                continue
            c = pd.Series(cls[pool[nb]])
            f = c.map(fam).value_counts(normalize=True)
            if f.iloc[0] >= C.VOTE_SHARE:
                cls[i] = c[c.map(fam) == f.index[0]].value_counts().index[0]
                rule[i] = "unk_vote"
    pre = (cls == "intra_slab") & (ev["year"].to_numpy() < C.PRE_YEAR)
    cls[pre], rule[pre] = "slab_interface", "pre_year"
    ev["class"], ev["cls_rule"] = cls, rule
    info = {"class": ev["class"].value_counts().to_dict(),
            "class_M>=5.5": ev.loc[ev["mag"] >= 5.5, "class"].value_counts().to_dict(),
            "rule": ev["cls_rule"].value_counts().to_dict()}
    return ev, info
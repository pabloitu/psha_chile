"""C3: one epicentre, origin time, depth and mechanism per earthquake (D-CAT-12-14, 16).

A local catalogue (Potin, CSN web) comes first only inside its own network; elsewhere, and before 1982, the global
sources come first, and a local record further than far_km from every teleseismic and GCCEL member is not used. The
depth is the first measured depth in the same order (offshore GCCEL and ISC-EHB L1 / L2 before the local catalogue):
fixed depths, ISC-EHB L3, unconstrained GCCEL depths and depths on a default bin of their agency are skipped, and an
event with none left has an unknown depth. A fixed ISC-EHB L1 depth is held at its depth-phase value and counts.
Before 1964 only the depths their catalogue marks as constrained count. Ported from psha_chile8 catalog/locate.py.
"""
import numpy as np
import pandas as pd

from .match import CFG, ROOT, table, tsec, tstr, year

C = CFG["locate"]
NM = lambda m0: (2 / 3) * (np.log10(m0) - 9.1)


def records(e, L):
    """
    The origin each source gives each event (the one matched on; the reference hypocentre for GCMT, never the
    centroid).

    Returns
    -------
    R : one row per event and source slot: key (potin, csn, gccel, ehb1-3, isc, comcat, csn_isc, iscgem, cent_ehb,
        centennial, gcmt, cabello), src, src_id, origin_id, agency, t, yr, lat, lon, z, fixed, quality
    allo : every origin of every source (src, agency, z, yr), for the default-depth table
    """
    L = L[L.used.astype(str).eq("True") & (L.src != "rm2018")][["event_id", "src", "src_id", "origin_id", "dt", "dd"]]
    rows, allo = [], []
    for s in L.src.unique():
        x = pd.read_csv(table(s, "events"), low_memory=False, dtype={"src_id": str, "origin_id": str})
        x = x[["src", "src_id", "origin_id", "prime", "time", "lon", "lat", "depth", "depth_fixed", "depth_err",
               "depth_quality", "agency"]]
        x["agency"] = "ISC-EHB " + x.depth_quality.fillna("L3") if s == "iscehb" else x.agency.fillna(s)
        x["t"] = tsec(x.time)
        cen = (s == "gcmt") & x.prime.astype(str).eq("True")
        allo.append(pd.DataFrame({"src": s, "agency": np.where(cen, "GCMT centroid", x.agency), "z": x.depth,
                                  "yr": year(x.t)}))
        if s == "isc":
            # an origin of the ISC event from a listed agency: the prime if listed, else the first in list order
            ag = C["isc_agencies"]
            x = x[x.agency.isin(ag)].assign(r=lambda d: d.agency.map({a: i for i, a in enumerate(ag)}) - 100 * d.prime.astype(str).eq("True"))
            x = x.sort_values("r", kind="stable").drop_duplicates("src_id").drop(columns="r")
            rows.append(L[L.src == s].drop(columns="origin_id").merge(x, on=["src", "src_id"]))
            continue
        rows.append(L[L.src == s].merge(x[~cen], on=["src", "src_id", "origin_id"]))
    R = pd.concat(rows, ignore_index=True).rename(columns={"depth": "z", "depth_quality": "quality"})
    R["fixed"] = R.depth_fixed.astype(str).eq("True")
    R["yr"] = year(R.t)
    key = R.src.replace({"iscehb": "ehb"})
    eh = R.src == "iscehb"
    key[eh] = "ehb" + R.quality[eh].fillna("L3").str[-1]
    ce = (R.src == "centennial") & (R.agency == "EHB") & np.any([(R.yr >= a) & (R.yr < b) for a, b in C["cent_ehb_years"]], axis=0)
    key[ce] = "cent_ehb"
    R["key"] = key
    R = R.sort_values(["dt", "dd"], key=lambda c: c.abs(), kind="stable").drop_duplicates(["event_id", "key"])
    cols = ["event_id", "key", "src", "src_id", "origin_id", "agency", "t", "yr", "lat", "lon", "z", "fixed", "quality",
            "depth_err"]
    return R[cols].reset_index(drop=True), pd.concat(allo, ignore_index=True)


# default depths
def spikes(z):
    """1 km depth bins whose count exceeds k times the median of the bins within 5 km: bin, modal value, n, share,
    ratio."""
    p = C["spikes"]
    z = z[np.isfinite(z) & (z >= -5) & (z < 700)]
    if len(z) < p["n_min"]:
        return []
    c = np.bincount(np.floor(z).astype(int) + 5, minlength=720).astype(float)
    out = []
    for i in np.flatnonzero(c >= p["n_spike"]):
        med = max(np.median(np.r_[c[max(i - 5, 0):i], c[i + 1:i + 6]]), 1.0)
        if c[i] > p["k"] * med and c[i] / len(z) >= p["share"]:
            v, n = np.unique(np.round(z[np.floor(z) == i - 5], 2), return_counts=True)
            out.append((i - 5, float(v[np.argmax(n)]), int(c[i]), c[i] / len(z), c[i] / med))
    return out


def defaults(allo):
    """Default-depth table per source and agency, over the whole record and per period, plus the documented ones."""
    rows = []
    for (s, ag), x in allo.groupby(["src", "agency"]):
        if len(x) < C["spikes"]["n_min"]:
            continue
        for lo, hi in [(-1e9, 1e9)] + C["periods"]:
            y = x[(x.yr >= lo) & (x.yr < hi)]
            for d, v, n, sh, r in spikes(y.z.to_numpy(float)):
                rows.append({"src": s, "agency": ag, "period": "all" if lo < 0 else f"{lo}–{hi}", "depth": d, "value": v,
                             "n": n, "share": round(sh, 4), "ratio": round(r, 1), "n_agency": len(y), "how": "spike"})
    t = pd.DataFrame(rows)
    f = pd.DataFrame([{"src": s, "agency": a, "period": "all", "depth": d, "value": float(d), "how": "documented"}
                      for s, a, d in C["forced"]])
    f = f[~pd.MultiIndex.from_frame(f[["src", "agency", "depth"]]).isin(
        pd.MultiIndex.from_frame(t[t.period == "all"][["src", "agency", "depth"]]))]
    return pd.concat([t, f], ignore_index=True)


def on_default(R, dflt):
    """True where a depth equals the modal value of a default bin of its source and agency (whole record or its
    period)."""
    per = np.full(len(R), "", object)
    for lo, hi in C["periods"]:
        per[(R.yr >= lo) & (R.yr < hi)] = f"{lo}–{hi}"
    d = dflt.assign(depth=dflt.depth.astype(int))
    zb = np.floor(R.z.to_numpy(float))
    out = np.zeros(len(R), bool)
    for q in ("all", None):
        x = pd.DataFrame({"src": R.src.to_numpy(), "agency": R.agency.to_numpy(), "period": per if q is None else q,
                          "depth": np.nan_to_num(zb, nan=-999).astype(int)})
        v = x.merge(d[["src", "agency", "period", "depth", "value"]], how="left").value.to_numpy(float)
        out |= np.abs(R.z.to_numpy(float) - v) < 0.05
    return out


# geography
def backarc(lon, lat):
    """East of the arc polygon: further east than its eastern edge at that latitude (0.2 degree steps)."""
    import geopandas as gpd
    import shapely
    c = shapely.get_coordinates(gpd.read_file(ROOT / CFG["inputs"]["arc"]).union_all().boundary)
    east = pd.Series(c[:, 0]).groupby(np.round(c[:, 1] / 0.2)).max()
    return np.asarray(lon, float) > np.interp(np.asarray(lat, float), east.index.to_numpy() * 0.2, east.to_numpy())


def offshore(lon, lat):
    """Epicentre in the sea and more than offshore_km from the coast."""
    import geopandas as gpd
    import shapely
    g = gpd.read_file(ROOT / CFG["inputs"]["land"], bbox=(-90, -65, -50, -8)).clip(shapely.box(-90, -65, -50, -8))
    g = g.to_crs(32719).union_all().buffer(C["offshore_km"] * 1e3)
    shapely.prepare(g)
    p = gpd.GeoSeries(gpd.points_from_xy(lon, lat), crs=4326).to_crs(32719)
    ok = np.isfinite(np.asarray(lon, float)) & np.isfinite(np.asarray(lat, float))
    out = np.zeros(len(p), bool)
    out[ok] = ~shapely.contains(g, p.values[ok])
    return out


def first(W, v, keys, ok=None):
    """Value v of the first key that has it (and is ok); returns values and the keys."""
    out, src = np.full(len(W), np.nan), np.full(len(W), None, object)
    for k in keys:
        if (v, k) not in W:
            continue
        x = W[(v, k)].to_numpy(float)
        m = np.isnan(out) & np.isfinite(x) & (True if ok is None else W[(ok, k)].to_numpy() == True)  # noqa: E712
        out[m], src[m] = x[m], k
    return out, src


# location
def wide(e, R, dflt):
    """One row per event with lat, lon, z, t and the measured flag of every source slot."""
    q = R.quality.fillna("").astype(str)
    old = np.any([(R.key == k) & q.str.startswith(tuple(v)) for k, v in C["old_ok"].items()], axis=0)
    ok = R.z.notna() & (R.key != "ehb3") & ~R.key.isin(C["never"]) & ~on_default(R, dflt) \
        & ~(R.key.isin(["centennial", "cent_ehb"]) & (R.z == 0)) & ~((R.yr < C["old_before"]) & ~old)
    R = R.assign(meas=ok & (~R.fixed | (R.key == "ehb1")))
    lq = C["low_quality"]
    low = np.any([(R.key == k) & q.str.startswith(tuple(lq[k])) for k in ("iscgem", "ehb3")], axis=0)
    R["low"] = R.z.notna() & low & ~R.meas & ~on_default(R, dflt) & ~R.fixed & ~R.key.isin(C["never"])
    W = R.pivot(index="event_id", columns="key", values=["lat", "lon", "z", "t", "meas", "low", "depth_err"]).reindex(e.event_id)
    return W, R


def inside_network(e, W):
    """Events of the local catalogues inside their network: from the network year, latitude inside and not in the
    backarc (on the first teleseismic member, else the local record), and the local record not further than far_km
    from the closest teleseismic or GCCEL member (D-CAT-12, 13)."""
    tele, loc = C["tele"], C["local"]
    la, lo = first(W, "lat", tele + loc)[0], first(W, "lon", tele + loc)[0]
    pa, po = first(W, "lat", loc)[0], first(W, "lon", loc)[0]
    d = np.full(len(W), np.nan)
    for k in tele + ["gccel"]:
        if ("lat", k) in W:
            a, o = W[("lat", k)].to_numpy(float), W[("lon", k)].to_numpy(float)
            d = np.fmin(d, np.hypot((a - pa) * 111.2, (o - po) * 111.2 * np.cos(np.radians(pa))))
    n, fs = C["network"], C["flat_slab"]
    pz = first(W, "z", loc)[0]
    flat = (la >= fs["lat"][0]) & (la <= fs["lat"][1]) & (pz >= fs["z"])
    return np.isfinite(pa) & ~(d > C["far_km"]) & (e.yr.to_numpy() >= n["from"]) & (la >= n["lat"][0]) \
        & (la <= n["lat"][1]) & ~backarc(lo, la) & ~flat


def locate(e, W, ins):
    """
    Epicentre and origin time from the first source of the event's order; depth from the first source of the same
    order with a measured depth (offshore inside events: the sea order).

    Returns a table in the order of e: lat, lon, t, loc_key, depth, depth_key, depth_first (the depth of the location
    source), first_meas, inside_network, offshore.
    """
    yr = e.yr.to_numpy()
    out = pd.DataFrame({"lat": np.nan, "lon": np.nan, "t": np.nan, "loc_key": None, "depth": np.nan, "depth_key": None,
                        "depth_first": np.nan, "inside_network": ins}, index=e.index)
    orders = [C["hist"], C["old"], C["inside"], C["outside"], C["sea"]]
    cat = np.where(yr < C["hist_before"], 0, np.where(yr < C["old_before"], 1, np.where(ins, 2, 3)))
    for c, order in enumerate(orders[:4]):
        k = cat == c
        la, src = first(W, "lat", order)
        out.loc[k, "lat"], out.loc[k, "loc_key"] = la[k], src[k]
    for v, c in (("lon", "lon"), ("t", "t"), ("z", "depth_first"), ("meas", "first_meas")):
        x = np.full(len(e), np.nan)
        for q in pd.unique(out.loc_key.dropna()):
            m = (out.loc_key == q).to_numpy()
            x[m] = W[(v, q)].to_numpy(float)[m]
        out[c] = x
    out["first_meas"] = out.first_meas == 1
    out["offshore"] = offshore(out.lon.to_numpy(), out.lat.to_numpy())
    pz = first(W, "z", C["local"])[0]
    cat = np.where((cat == 2) & (pz < C["potin_shallow"]), 3, cat)
    cat = np.where((cat == 2) & out.offshore.to_numpy(), 4, cat)
    out["low"] = False
    for c, order in enumerate(orders):
        k = cat == c
        z, zs = first(W, "z", order, ok="meas")
        out.loc[k, "depth"], out.loc[k, "depth_key"] = z[k], zs[k]
    z, zs = first(W, "z", ["iscgem", "ehb3"], ok="low")
    k = out.depth.isna().to_numpy() & np.isfinite(z)
    out.loc[k, "depth"], out.loc[k, "depth_key"], out.loc[k, "low"] = z[k], zs[k], True
    er = np.full(len(e), np.nan)
    for q in ("iscgem", "ehb3"):
        if ("depth_err", q) in W:
            m = k & (zs == q)
            er[m] = W[("depth_err", q)].to_numpy(float)[m]
    out["low_err"] = er
    return out


def sigma(key, z, off, old):
    """Depth σ per event (D-CAT-14): the X3 table (below 70 km) and the X1 values (from 70 km) by depth source and
    range; the largest σ of the range where a source is not covered (flag); a fixed value for GCCEL; floors for the
    others, offshore and before 1964."""
    s = C["sigma"]
    lab = s["labels"]
    m = pd.read_csv(ROOT / CFG["inputs"]["sigma_x3"])
    m = m[(m.n_z >= s["n_min"]) & (m.sigma_z_net > 0) & m.src.isin(s["names"])]
    tab = {(s["names"][a], d): v for a, d, v in zip(m.src, m.depth, m.sigma_z_net) if d != lab[2]}
    x1 = pd.read_csv(ROOT / CFG["inputs"]["sigma_x1"])
    x1 = x1[(x1.group == "all") & (x1.sigma < s["x1_none"]) & x1.src.isin(s["names"].values())]
    tab.update({(a, lab[2]): v for a, v in zip(x1.src, x1.sigma)})
    top = {d: max(v for (a, q), v in tab.items() if q == d) for d in lab}
    rng = np.array(lab, object)[np.digitize(np.nan_to_num(z, nan=0.0), s["bins"])]
    sg = np.array([tab.get((k, r), np.nan) for k, r in zip(key, rng)])
    miss = np.isnan(sg) & np.isfinite(z) & (key != "gccel")
    sg[miss] = [top[r] for r in rng[miss]]
    g = key == "gccel"
    sg[g] = s["gccel"]
    sg[~g] = np.maximum(sg[~g], s["floor"])
    low = off & np.isfinite(z) & (sg < s["offshore"])
    sg[low] = s["offshore"]
    sg = np.maximum(sg, np.where(old, s["old"], 0.0))
    sg[~np.isfinite(z)] = np.nan
    return sg, miss, low


# mechanisms
def tensor_m0(m):
    d = m[["mrr", "mtt", "mpp"]].astype(float).pow(2).sum(axis=1, min_count=3)
    o = m[["mrt", "mrp", "mtp"]].astype(float).pow(2).sum(axis=1, min_count=3)
    return np.sqrt((d + 2 * o) / 2)


def mechanisms(R):
    """
    One mechanism per event (D-CAT-16): GCMT (our file, then its copies in ComCat), a ComCat W-phase tensor, another
    ComCat tensor, a ComCat focal mechanism (nodal planes only), then a literature mechanism listed by ISC-GEM
    (agency bibliog). Within a rank a product whose listed moment agrees with its tensor comes first. M0 is the moment
    of the tensor.
    """
    p = CFG["mech"]
    c = pd.read_csv(table("comcat_mt", "mechs"), dtype={"src_id": str})
    g = pd.read_csv(table("gcmt", "mechs"), dtype={"src_id": str})
    b = pd.read_csv(table("iscgem", "mechs"), dtype={"src_id": str})
    b = b[(b.agency == "bibliog") & b.strike1.notna()]
    ft = c.code.str.startswith("focal-mechanism")
    c["rank"] = np.where(ft, 4, np.where(c.code.str.contains(p["gcmt_copy"]), 1, np.where(c.code.str.contains(p["wphase"]), 2, 3)))
    g["rank"], b["rank"] = 0, 5
    ev = lambda s: R[R.src == s].drop_duplicates("src_id").set_index("src_id").event_id
    m = pd.concat([c.assign(event_id=c.src_id.map(ev("comcat"))), g.assign(event_id=g.src_id.map(ev("gcmt"))),
                   b.assign(event_id=b.src_id.map(ev("iscgem")))], ignore_index=True)
    m = m[m.event_id.notna()]
    m["m0_tensor"] = tensor_m0(m)
    m["m0"] = pd.to_numeric(m.m0, errors="coerce")
    m["bad"] = (m.m0 / m.m0_tensor - 1).abs() > p["m0_tol"]
    m = m.sort_values(["rank", "bad"], kind="stable").drop_duplicates("event_id")
    m["mech_flag"] = np.where(m.bad, "m0_listed_differs_from_tensor", np.where(m["rank"] == 4, "nodal_planes_only", ""))
    m["mech_m0"] = m.m0_tensor.fillna(m.m0).where(m["rank"] < 4)
    m["mech_mw"] = NM(m.mech_m0).round(2)
    m["mech_src"] = np.select([m.src == "gcmt", m.src == "iscgem"], ["GCMT", "ISC-GEM literature"],
                              "ComCat " + m.agency.astype(str))
    cols = ["event_id", "mech_src", "code", "strike1", "dip1", "rake1", "strike2", "dip2", "rake2", "mrr", "mtt", "mpp",
            "mrt", "mrp", "mtp", "mech_m0", "mech_mw", "mech_flag"]
    return m[cols].rename(columns={"code": "mech_id"})


def run(e, L):
    """Locations table (one row per event), the default-depth table and the records."""
    e = e.assign(yr=year(e.t))
    R, allo = records(e, L)
    dflt = defaults(allo)
    W, R = wide(e, R, dflt)
    x = locate(e, W, inside_network(e, W))
    rec = R.set_index(["event_id", "key"])
    a = rec.reindex(pd.MultiIndex.from_arrays([e.event_id, x.loc_key]))
    b = rec.reindex(pd.MultiIndex.from_arrays([e.event_id, x.depth_key]))
    o = x.offshore.to_numpy()
    s, miss, low = sigma(x.depth_key.to_numpy(), x.depth.to_numpy(), o, (e.yr < C["old_before"]).to_numpy())
    lq = x.low.to_numpy()
    s[lq] = np.fmax(x.low_err.to_numpy(float)[lq], C["low_quality"]["sigma_min"])
    fl = [";".join(f for f, k in (("fallback_source", lk in C["tail"] and yr >= C["old_before"]),
                                  ("depth_from_another_source", dk is not None and dk != lk),
                                  ("loc_src_depth_not_measured", not fm), ("depth_unknown", dk is None),
                                  ("depth_low_quality", lw),
                                  ("sigma_largest_of_range", mi), ("sigma_offshore_floor", lo_)) if k)
          for lk, dk, yr, mi, lo_, fm, lw in zip(x.loc_key, x.depth_key, e.yr, miss, low, x.first_meas, x.low)]
    out = pd.DataFrame({
        "event_id": e.event_id.to_numpy(), "time": tstr(x.t.to_numpy()), "lon": x.lon.round(4).to_numpy(),
        "lat": x.lat.round(4).to_numpy(), "loc_src": x.loc_key.to_numpy(), "loc_src_id": a.src_id.to_numpy(),
        "depth": x.depth.round(2).to_numpy(), "depth_sigma": np.round(s, 1), "depth_src": x.depth_key.to_numpy(),
        "depth_src_id": b.src_id.to_numpy(), "depth_kind": np.where(x.low, "low quality", np.where(np.isfinite(x.depth), "measured", "unknown")),
        "depth_of_loc_src": x.depth_first.round(2).to_numpy(), "inside_network": x.inside_network.to_numpy(),
        "offshore": o, "nonquake": e.nonquake.to_numpy()})
    out = out.merge(mechanisms(R), on="event_id", how="left")
    out["loc_flags"] = fl
    return out, dflt, R

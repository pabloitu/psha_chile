"""One epicentre, origin time, depth and mechanism per earthquake (plan A4).

A local catalogue (Potin et al., CSN web) comes first only inside its own network; elsewhere, and before 1982,
the global sources come first, and a local record further than FAR_KM from every teleseismic member is not used.
The depth is the first measured depth in the same order (offshore GCCEL and ISC-EHB L1 / L2 before the local
catalogue): fixed depths, ISC-EHB L3, unconstrained GCCEL depths, depths on a default bin of their agency and round
depths before 1964 are skipped, and an event with none left has an unknown depth. A fixed ISC-EHB L1 depth is held
at its depth-phase value and counts as measured; a fixed L2 depth is the GCMT depth and is the last resort.
Checks and figures in locate_check.py.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from match import SRC, OUT, FROZEN, DATES, tsec, tstr, year
from magnitude import manifest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

# settings
RUN = "2026-11-13"
A3 = "2026-11-11"
MW = "2026-11-13"
ARC = REPO / "data" / "intraarc.shp"
LAND = Path.home() / ".local/share/cartopy/shapefiles/natural_earth/physical/ne_10m_land.shp"
X3_SIGMA = HERE.parent / "explore" / "X3" / "tables" / "x3_depth_error_model.csv"
X1_SIGMA = HERE.parent / "explore" / "X1" / "tables" / "t2_depth_sigma_used_for_L-d.csv"
NET_LAT, NET_FROM = (-46.0, -18.0), 1982
FAR_KM = 50.0
TELE = ["ehb1", "ehb2", "ehb3", "isc", "comcat"]
LOCAL = ["potin", "csn"]
TAIL = ["ehb3", "iscgem", "cent_ehb", "centennial", "gcmt", "cabello"]
INSIDE = LOCAL + ["gccel", "ehb1", "ehb2", "isc", "comcat", "csn_isc"] + TAIL
OUTSIDE = ["gccel", "ehb1", "ehb2", "isc", "comcat"] + LOCAL + ["csn_isc"] + TAIL
SEA = ["gccel", "ehb1", "ehb2"] + [k for k in INSIDE if k not in ("gccel", "ehb1", "ehb2")]
OLD = ["cent_ehb", "iscgem", "isc", "centennial", "comcat", "ehb1", "ehb2", "ehb3", "gcmt", "cabello"]
HIST = ["cabello"] + OLD[:-1]
OLD_BEFORE, HIST_BEFORE = 1964, 1904
OLD_ROUND = 5.0
LAST = "ehb2"
CENT_EHB = [(1918, 1943), (1956, 2100)]
NEVER = ["cabello"]
K, MIN_N, MIN_SPIKE, MIN_SHARE = 5, 300, 10, 0.003
PERIODS = [(1964, 1980), (1980, 2000), (2000, 2012), (2012, 2100)]
FORCED = [("comcat", "us", 10), ("comcat", "us", 33), ("comcat", "us", 35), ("isc", "ISC", 35), ("iscgem", "ISC-GEM", 15),
          ("iscgem", "ISC-GEM", 35), ("iscehb", "ISC-EHB L1", 10), ("iscehb", "ISC-EHB L1", 15), ("iscehb", "ISC-EHB L2", 10),
          ("iscehb", "ISC-EHB L2", 15)]
SIG_NAME = {"Potin et al.": "potin", "CSN web": "csn", "ISC-EHB L1": "ehb1", "ISC-EHB L2": "ehb2", "ISC prime": "isc",
            "ComCat": "comcat", "CSN in ISC": "csn_isc", "ISC-GEM": "iscgem", "Centennial": "centennial",
            "GCMT hypocentre": "gcmt"}
SIG_BINS, SIG_LAB, SIG_MIN_N = [30.0, 70.0], ["< 30 km", "30–70 km", "≥ 70 km"], 20
SIG_X1_NONE, SIG_GCCEL, SIG_OFF = 25.0, 3.0, 10.0
SIG_MIN, SIG_LAST, SIG_OLD = 5.0, 15.0, 20.0
OFF_KM = 20.0
DOMAIN = {"lat": (-58.0, -17.0), "lon": (-78.5, -65.0)}
M0_TOL = 0.10
MECH_DIFF = 0.4
WPHASE = r"(?i)(?:_mww$|_WCMT$|^moment-tensor:duputel)"
GCMT_COPY = r"(?i)(?:_GCMT$|_HRV$|_gcmt$|_mwc$|gcmt)"
NM = lambda m0: (2 / 3) * (np.log10(m0) - 9.1)


# inputs
def records(d=SRC, out=OUT):
    """
    The events of the A3 run and the origin each source gives them (the one A3 matched on; the reference
    hypocentre for GCMT, never the centroid).

    Returns
    -------
    e : events (event_id, yr)
    R : one row per event and source slot: key (potin, csn, gccel, ehb1-3, isc, comcat, csn_isc, iscgem,
        cent_ehb, centennial, gcmt, cabello), src, src_id, origin_id, agency, t, lat, lon, z, fixed, quality
    allo : every origin of every source (src, agency, z, yr), for the default-depth table
    """
    e = pd.read_csv(Path(out) / f"events_{A3}.csv", usecols=["event_id", "time", "mmax"], low_memory=False)
    e["yr"] = year(tsec(e.time))
    L = pd.read_csv(Path(out) / f"links_{A3}.csv", dtype={"src_id": str, "origin_id": str}, low_memory=False)
    L = L[L.used.astype(str).eq("True") & (L.src != "rm2018")][["event_id", "src", "src_id", "origin_id", "dt", "dd"]]
    rows, allo = [], []
    for s in L.src.unique():
        x = pd.read_csv(Path(d) / f"{s}_{DATES.get(s, FROZEN)}_events.csv", low_memory=False, dtype={"src_id": str, "origin_id": str})
        x = x[["src", "src_id", "origin_id", "prime", "time", "lon", "lat", "depth", "depth_fixed", "depth_quality", "agency"]]
        x["agency"] = "ISC-EHB " + x.depth_quality.fillna("L3") if s == "iscehb" else x.agency.fillna(s)
        x["t"] = tsec(x.time)
        cen = (s == "gcmt") & x.prime.astype(str).eq("True")
        allo.append(pd.DataFrame({"src": s, "agency": np.where(cen, "GCMT centroid", x.agency), "z": x.depth, "yr": year(x.t)}))
        rows.append(L[L.src == s].merge(x[~cen], on=["src", "src_id", "origin_id"]))
    R = pd.concat(rows, ignore_index=True).rename(columns={"depth": "z", "depth_quality": "quality"})
    R["fixed"] = R.depth_fixed.astype(str).eq("True")
    R["yr"] = year(R.t)
    key = R.src.replace({"iscehb": "ehb"})
    eh = R.src == "iscehb"
    key[eh] = "ehb" + R.quality[eh].fillna("L3").str[-1]
    ce = (R.src == "centennial") & (R.agency == "EHB") & np.any([(R.yr >= a) & (R.yr < b) for a, b in CENT_EHB], axis=0)
    key[ce] = "cent_ehb"
    R["key"] = key
    R = R.sort_values(["dt", "dd"], key=lambda c: c.abs(), kind="stable").drop_duplicates(["event_id", "key"])
    cols = ["event_id", "key", "src", "src_id", "origin_id", "agency", "t", "yr", "lat", "lon", "z", "fixed", "quality"]
    return e, R[cols].reset_index(drop=True), pd.concat(allo, ignore_index=True)


# default depths
def spikes(z, k=K):
    """1 km depth bins whose count exceeds k times the median of the bins within 5 km: bin, modal value, n,
    share, ratio."""
    z = z[np.isfinite(z) & (z >= -5) & (z < 700)]
    if len(z) < MIN_N:
        return []
    c = np.bincount(np.floor(z).astype(int) + 5, minlength=720).astype(float)
    out = []
    for i in np.flatnonzero(c >= MIN_SPIKE):
        med = max(np.median(np.r_[c[max(i - 5, 0):i], c[i + 1:i + 6]]), 1.0)
        if c[i] > k * med and c[i] / len(z) >= MIN_SHARE:
            v, n = np.unique(np.round(z[np.floor(z) == i - 5], 2), return_counts=True)
            out.append((i - 5, float(v[np.argmax(n)]), int(c[i]), c[i] / len(z), c[i] / med))
    return out


def defaults(allo):
    """Default-depth table per source and agency, over the whole record and per period, plus the documented
    defaults of FORCED (whole record)."""
    rows = []
    for (s, ag), x in allo.groupby(["src", "agency"]):
        if len(x) < MIN_N:
            continue
        for lo, hi in [(-1e9, 1e9)] + PERIODS:
            y = x[(x.yr >= lo) & (x.yr < hi)]
            for d, v, n, sh, r in spikes(y.z.to_numpy(float)):
                rows.append({"src": s, "agency": ag, "period": "all" if lo < 0 else f"{lo}–{hi}", "depth": d, "value": v, "n": n,
                             "share": round(sh, 4), "ratio": round(r, 1), "n_agency": len(y), "how": "spike"})
    t = pd.DataFrame(rows)
    f = pd.DataFrame([{"src": s, "agency": a, "period": "all", "depth": d, "value": float(d), "how": "documented"} for s, a, d in FORCED])
    f = f[~pd.MultiIndex.from_frame(f[["src", "agency", "depth"]]).isin(pd.MultiIndex.from_frame(t[t.period == "all"][["src", "agency", "depth"]]))]
    return pd.concat([t, f], ignore_index=True)


def on_default(R, dflt):
    """True where a depth equals the modal value of a default bin of its source and agency, for the whole
    record or for its period."""
    per = np.full(len(R), "", object)
    for lo, hi in PERIODS:
        per[(R.yr >= lo) & (R.yr < hi)] = f"{lo}–{hi}"
    val = {(s, a, p, d): v for s, a, p, d, v in zip(dflt.src, dflt.agency, dflt.period, dflt.depth, dflt.value)}
    zb = np.floor(R.z.to_numpy(float))
    out = np.zeros(len(R), bool)
    for i, (s, a, p, b, z) in enumerate(zip(R.src, R.agency, per, zb, R.z)):
        for q in ("all", p):
            v = val.get((s, a, q, b))
            out[i] |= v is not None and abs(z - v) < 0.05
    return out


# geography
def backarc(lon, lat, arc=ARC):
    """East of the arc polygon: further east than its eastern edge at that latitude (0.2 degree steps)."""
    import cartopy.io.shapereader as shp
    import shapely
    c = shapely.get_coordinates(shapely.boundary(shapely.union_all(list(shp.Reader(str(arc)).geometries()))))
    east = pd.Series(c[:, 0]).groupby(np.round(c[:, 1] / 0.2)).max()
    return np.asarray(lon, float) > np.interp(np.asarray(lat, float), east.index.to_numpy() * 0.2, east.to_numpy())


def offshore(lon, lat, land=LAND):
    """Epicentre in the sea and more than OFF_KM from the coast."""
    import cartopy.io.shapereader as shp
    import shapely
    import shapely.ops
    from pyproj import Transformer
    tf = Transformer.from_crs(4326, 32719, always_xy=True)
    box = shapely.box(-90, -65, -50, -8)
    g = shapely.union_all([q.intersection(box) for q in shp.Reader(str(land)).geometries() if q.intersects(box)])
    g = shapely.ops.transform(lambda a, b: tf.transform(np.asarray(a), np.asarray(b)), g).buffer(OFF_KM * 1e3)
    shapely.prepare(g)
    x, y = tf.transform(np.asarray(lon, float), np.asarray(lat, float))
    ok = np.isfinite(x) & np.isfinite(y)
    out = np.zeros(len(x), bool)
    out[ok] = ~shapely.contains(g, shapely.points(x[ok], y[ok]))
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
    """One row per event with lat, lon, z, t, the measured flag and the last-resort flag (a fixed depth of LAST)
    of every source slot."""
    ok = R.z.notna() & (R.key != "ehb3") & ~R.key.isin(NEVER) & ~on_default(R, dflt) \
        & ~(R.key.isin(["centennial", "cent_ehb"]) & (R.z == 0)) & ~((R.yr < OLD_BEFORE) & (R.z % OLD_ROUND == 0))
    R = R.assign(meas=ok & (~R.fixed | (R.key == "ehb1")), last=ok & R.fixed & (R.key == LAST))
    W = R.pivot(index="event_id", columns="key", values=["lat", "lon", "z", "t", "meas", "last"]).reindex(e.event_id)
    return W, R


def inside_network(e, W, back=backarc):
    """Events of the local catalogues that lie inside their network: from NET_FROM, latitude within NET_LAT and
    not in the backarc, tested on the epicentre of the first teleseismic member, else on the local record; and
    the local record not further than FAR_KM from the closest teleseismic or GCCEL member."""
    la, lo = first(W, "lat", TELE + LOCAL)[0], first(W, "lon", TELE + LOCAL)[0]
    pa, po = first(W, "lat", LOCAL)[0], first(W, "lon", LOCAL)[0]
    d = np.full(len(W), np.nan)
    for k in TELE + ["gccel"]:
        if ("lat", k) in W:
            a, o = W[("lat", k)].to_numpy(float), W[("lon", k)].to_numpy(float)
            d = np.fmin(d, np.hypot((a - pa) * 111.2, (o - po) * 111.2 * np.cos(np.radians(pa))))
    near = ~(d > FAR_KM)
    return np.isfinite(pa) & near & (e.yr.to_numpy() >= NET_FROM) & (la >= NET_LAT[0]) & (la <= NET_LAT[1]) & ~back(lo, la)


def locate(e, W, ins, off=None):
    """
    Epicentre and origin time from the first source of the event's order; depth from the first source of the
    same order with a measured depth, else the fixed depth of LAST.

    Orders: HIST before HIST_BEFORE, OLD before OLD_BEFORE, INSIDE for events inside the network, OUTSIDE else.
    With off (a function of lon, lat) the depth of inside events that lie offshore follows SEA.

    Returns a table in the order of e: lat, lon, t, loc_key, depth, depth_key, depth_first (the depth of the
    location source, measured or not), first_meas (whether that depth is measured), last (depth from the fixed
    depth of LAST), inside_network, offshore.
    """
    yr = e.yr.to_numpy()
    out = pd.DataFrame({"lat": np.nan, "lon": np.nan, "t": np.nan, "loc_key": None, "depth": np.nan, "depth_key": None,
                        "depth_first": np.nan, "inside_network": ins}, index=e.index)
    cat = np.where(yr < HIST_BEFORE, 0, np.where(yr < OLD_BEFORE, 1, np.where(ins, 2, 3)))
    for c, order in enumerate((HIST, OLD, INSIDE, OUTSIDE)):
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
    out["offshore"] = np.zeros(len(e), bool) if off is None else off(out.lon.to_numpy(), out.lat.to_numpy())
    cat = np.where((cat == 2) & out.offshore.to_numpy(), 4, cat)
    for c, order in enumerate((HIST, OLD, INSIDE, OUTSIDE, SEA)):
        k = cat == c
        z, zs = first(W, "z", order, ok="meas")
        out.loc[k, "depth"], out.loc[k, "depth_key"] = z[k], zs[k]
    z, zs = first(W, "z", [LAST], ok="last")
    k = out.depth.isna().to_numpy() & np.isfinite(z)
    out.loc[k, "depth"], out.loc[k, "depth_key"] = z[k], zs[k]
    out["last"] = k
    return out


def sigma(key, z, off, last, old):
    """Depth error per event from the X3 model (below 70 km) and the X1 values (from 70 km), by depth source and
    depth range; the largest σ of the range where a source is not covered (flag); SIG_GCCEL for GCCEL (its own
    depth bound); at least SIG_MIN for the others (their tabled values are spreads between catalogues that share
    data), SIG_OFF offshore, SIG_LAST for a fixed depth of LAST and SIG_OLD before OLD_BEFORE."""
    m = pd.read_csv(X3_SIGMA)
    m = m[(m.n_z >= SIG_MIN_N) & (m.sigma_z_net > 0) & m.src.isin(SIG_NAME)]
    tab = {(SIG_NAME[s], d): v for s, d, v in zip(m.src, m.depth, m.sigma_z_net) if d != SIG_LAB[2]}
    x1 = pd.read_csv(X1_SIGMA)
    x1 = x1[(x1.group == "all") & (x1.sigma < SIG_X1_NONE) & x1.src.isin(SIG_NAME.values())]
    tab.update({(s, SIG_LAB[2]): v for s, v in zip(x1.src, x1.sigma)})
    top = {d: max(v for (s, q), v in tab.items() if q == d) for d in SIG_LAB}
    rng = np.array(SIG_LAB, object)[np.digitize(np.nan_to_num(z, nan=0.0), SIG_BINS)]
    s = np.array([tab.get((k, r), np.nan) for k, r in zip(key, rng)])
    miss = np.isnan(s) & np.isfinite(z) & (key != "gccel")
    s[miss] = [top[r] for r in rng[miss]]
    g = key == "gccel"
    s[g] = SIG_GCCEL
    s[~g] = np.maximum(s[~g], SIG_MIN)
    low = off & np.isfinite(z) & (s < SIG_OFF)
    s[low] = SIG_OFF
    s = np.maximum(s, np.where(old, SIG_OLD, np.where(last, SIG_LAST, 0.0)))
    s[~np.isfinite(z)] = np.nan
    return s, miss, low


# mechanisms
def tensor_m0(m):
    """Scalar moment of a moment tensor (mrr, mtt, mpp, mrt, mrp, mtp)."""
    d = m[["mrr", "mtt", "mpp"]].astype(float).pow(2).sum(axis=1, min_count=3)
    o = m[["mrt", "mrp", "mtp"]].astype(float).pow(2).sum(axis=1, min_count=3)
    return np.sqrt((d + 2 * o) / 2)


def mechanisms(R, d=SRC):
    """
    One mechanism per event: a ComCat W-phase tensor, then another ComCat tensor of the USGS, then GCMT (our
    file, then its copies in ComCat), then a ComCat focal mechanism (nodal planes only). Within a rank a product
    whose scalar moment agrees with its tensor within M0_TOL comes first. M0 is the moment of the tensor; a
    listed moment that differs is flagged.
    """
    c = pd.read_csv(Path(d) / f"comcat_mt_{FROZEN}_mechs.csv", dtype={"src_id": str})
    g = pd.read_csv(Path(d) / f"gcmt_{FROZEN}_mechs.csv", dtype={"src_id": str})
    ft = c.code.str.startswith("focal-mechanism")
    c["rank"] = np.where(ft, 4, np.where(c.code.str.contains(WPHASE), 0, np.where(c.code.str.contains(GCMT_COPY), 3, 1)))
    g["rank"] = 2
    ev = lambda s: R[R.src == s].drop_duplicates("src_id").set_index("src_id").event_id
    m = pd.concat([c.assign(event_id=c.src_id.map(ev("comcat"))), g.assign(event_id=g.src_id.map(ev("gcmt")))], ignore_index=True)
    m = m[m.event_id.notna()]
    m["m0_tensor"] = tensor_m0(m)
    m["m0"] = pd.to_numeric(m.m0, errors="coerce")
    m["bad"] = (m.m0 / m.m0_tensor - 1).abs() > M0_TOL
    m = m.sort_values(["rank", "bad"], kind="stable").drop_duplicates("event_id")
    m["mech_flag"] = np.where(m.bad, "m0_listed_differs_from_tensor", np.where(m["rank"] == 4, "nodal_planes_only", ""))
    m["mech_m0"] = m.m0_tensor.fillna(m.m0).where(m["rank"] < 4)
    m["mech_mw"] = NM(m.mech_m0).round(2)
    m["mech_src"] = np.where(m.src == "gcmt", "GCMT", "ComCat " + m.agency.astype(str))
    cols = ["event_id", "mech_src", "code", "strike1", "dip1", "rake1", "strike2", "dip2", "rake2", "mrr", "mtt", "mpp", "mrt",
            "mrp", "mtp", "mech_m0", "mech_mw", "mech_flag"]
    return m[cols].rename(columns={"code": "mech_id"})


def build(e, R, dflt, back=backarc, off=offshore):
    """locations table (columns of the brief) from the records and the default table."""
    W, R = wide(e, R, dflt)
    x = locate(e, W, inside_network(e, W, back), off)
    rec = R.set_index(["event_id", "key"])
    a = rec.reindex(pd.MultiIndex.from_arrays([e.event_id, x.loc_key]))
    b = rec.reindex(pd.MultiIndex.from_arrays([e.event_id, x.depth_key]))
    o = x.offshore.to_numpy()
    s, miss, low = sigma(x.depth_key.to_numpy(), x.depth.to_numpy(), o, x["last"].to_numpy(), (e.yr < OLD_BEFORE).to_numpy())
    fl = [";".join(f for f, k in (("fallback_source", lk in TAIL and yr >= OLD_BEFORE), ("depth_from_another_source", dk is not None and dk != lk),
                                  ("loc_src_depth_not_measured", not fm),
                                  ("depth_unknown", dk is None), ("depth_fixed_gcmt", la_), ("sigma_largest_of_range", mi), ("sigma_offshore_floor", lo_))
                   if k) for lk, dk, yr, mi, lo_, fm, la_ in zip(x.loc_key, x.depth_key, e.yr, miss, low, x.first_meas, x["last"])]
    out = pd.DataFrame({
        "event_id": e.event_id.to_numpy(), "time": tstr(x.t.to_numpy()), "lon": x.lon.round(4).to_numpy(), "lat": x.lat.round(4).to_numpy(),
        "loc_src": x.loc_key.to_numpy(), "loc_src_id": a.src_id.to_numpy(), "depth": x.depth.round(2).to_numpy(),
        "depth_sigma": np.round(s, 1), "depth_src": x.depth_key.to_numpy(), "depth_src_id": b.src_id.to_numpy(),
        "depth_kind": np.where(np.isfinite(x.depth), "measured", "unknown"), "depth_of_loc_src": x.depth_first.round(2).to_numpy(),
        "inside_network": x.inside_network.to_numpy(), "offshore": o,
        "in_domain": ((x.lat >= DOMAIN["lat"][0]) & (x.lat <= DOMAIN["lat"][1]) & (x.lon >= DOMAIN["lon"][0]) & (x.lon <= DOMAIN["lon"][1])).to_numpy()})
    out = out.merge(mechanisms(R), on="event_id", how="left")
    out["flags"] = fl
    return out, W, R


def main():
    e, R, allo = records()
    dflt = defaults(allo)
    loc, W, R = build(e, R, dflt)
    loc = loc.sort_values("time", kind="stable").reset_index(drop=True)
    files = {OUT / f"locations_{RUN}.csv": loc, OUT / f"defaults_{RUN}.csv": dflt}
    bad = loc[loc.mech_flag == "m0_listed_differs_from_tensor"][["event_id", "time", "lat", "lon", "mech_src", "mech_id", "mech_m0", "mech_mw"]]
    files[OUT / "review" / f"mech_m0_mismatch_{RUN}.csv"] = bad
    f = OUT / f"mw_{MW}.csv"
    if f.exists():
        cat = loc.merge(pd.read_csv(f, low_memory=False), on="event_id", how="left", suffixes=("", "_mw"))
        cat = cat.rename(columns={"flags": "loc_flags", "flags_mw": "mw_flags"})
        files[OUT / f"catalog_{RUN}.csv"] = cat
        d = cat[(cat.mech_mw - cat.mw).abs() >= MECH_DIFF]
        files[OUT / "review" / f"mech_mw_differs_{RUN}.csv"] = d[["event_id", "time", "lat", "lon", "mw", "mw_agency", "mw_type", "mech_mw", "mech_src", "mech_id"]]
        k = cat.mw >= 4.45
        print("final Mw >= 4.5:", int(k.sum()), "| in the domain:", int((k & cat.in_domain).sum()),
              "| of these with a measured depth:", int((k & cat.in_domain & (cat.depth_kind == "measured")).sum()))
    for p, d in files.items():
        d.to_csv(p, index=False)
    manifest(files)
    print("events", len(loc), "| inside the network", int(loc.inside_network.sum()), "| depth unknown", int((loc.depth_kind == "unknown").sum()),
          "| with a mechanism", int(loc.mech_src.notna().sum()))
    print("location source:", loc.loc_src.value_counts().to_dict())
    print("depth source:", loc.depth_src.value_counts().to_dict())
    print("default bins (whole record):", len(dflt[dflt.period == "all"]), "| records on a default:", int(on_default(R, dflt).sum()))


if __name__ == "__main__":
    main()

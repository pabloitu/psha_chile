"""Record table for the subduction GMM residuals (task GM1, step 1).

Flatfiles of Bastías et al. (2026) matched to the frozen catalogue; Mw, hypocentre and class from the catalogue,
distances, spectra and site data from the flatfiles; rupture parameters the flatfiles do not hold (rake, dip, width,
ztor) from the catalogue mechanism and the OpenQuake scaling relations. One row per record.
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent
TAB = HERE / "tables"

# settings
DATE = "2026-11-15"
FF = REPO / "data" / "ground_motion"
F_EV, F_ST, F_REC = (FF / "Flatfile_chileanEvents_v11.csv", FF / "Flatfile_chileanSiteStation_v7(1).csv",
                     FF / "Flatfile_chileanRecord_v10.csv")
CAT = ROOT / "catalog" / "frozen" / "2026-11-14" / "catalog_2026-11-14c.csv"
ARC = REPO / "data" / "intraarc.shp"
PASS1 = dict(dt=90.0, km=150.0, dmw=None)
PASS2 = dict(dt=330.0, km=50.0, dmw=0.3)
MW_TOL, MW_REVIEW = 0.5, 5.5
BIG = 6.5
MW_MIN, RRUP_MAX = 5.0, 300.0
LOC_KM, LOC_DZ = 30.0, 20.0
IMTS = {"PGA": 0.01, "SA(0.2)": 0.2, "SA(1.0)": 1.0}
# no mechanism: dip, rake per class
MECH0 = {"interface": (20.0, 90.0), "inslab": (45.0, -90.0)}
MSR = {"interface": "ThingbaijamInterface", "inslab": "StrasserIntraslab"}
# Idini et al. (2017) soil classes by predominant period TG = 1/f0 (s): flat H/V is sI with Vs30 >= 900, else sII
IDINI_TG = [(0.2, 2), (0.4, 3), (0.8, 4), (np.inf, 6)]
HV_FLAT = 2.0
# flatfile class names
FF_CLS = {"Interface": "interface", "Inslab": "inslab", "ShallowCrust": "crustal"}


def vec(s):
    """A flatfile vector field such as "['0.01'; '0.05']" as a float array; -999 and empty fields give NaN."""
    if not isinstance(s, str) or not s.startswith("["):
        return np.array([np.nan])
    v = np.array([float(x.strip(" '\"")) for x in s.strip("[]").split(";") if x.strip(" '\"")])
    v[v == -999] = np.nan
    return v


def km(lon1, lat1, lon2, lat2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def secs(t):
    return np.array([np.datetime64(s[:23], "ms") for s in t]).astype(np.int64) / 1e3


def load_events():
    e = pd.read_csv(F_EV, dtype={"EventID": str}).replace(-999, np.nan)
    sec = e.Second.fillna(0)
    t = pd.to_datetime(dict(year=e.Year, month=e.Month, day=e.Day, hour=e.Hour, minute=e.Minute,
                            second=np.floor(sec).astype(int))) + pd.to_timedelta(sec % 1, unit="s")
    e["t"] = secs(t.dt.strftime("%Y-%m-%dT%H:%M:%S.%f"))
    return e


def load_catalogue():
    cols = ["event_id", "time", "lon", "lat", "depth", "depth_sigma", "depth_kind", "mw", "mw_kind", "w_interface",
            "w_inslab", "w_crustal", "w_outer_rise", "cls", "sub_inslab", "strike1", "dip1", "rake1", "strike2",
            "dip2", "rake2", "depth_assigned"]
    c = pd.read_csv(CAT, usecols=cols)
    c["t"] = secs(c.time)
    return c.sort_values("t").reset_index(drop=True)


def match(e, c):
    """Catalogue index per flatfile event: nearest in time inside the windows of PASS1, then PASS2 for the rest.
    Returns the index (-1 unmatched), the time offset (s) and the pass."""
    ct = c.t.to_numpy()
    idx, dts, how = np.full(len(e), -1), np.full(len(e), np.nan), np.zeros(len(e), int)
    for k, p in enumerate((PASS1, PASS2), 1):
        for i in np.flatnonzero(idx < 0):
            r = e.iloc[i]
            a, b = np.searchsorted(ct, [r.t - p["dt"], r.t + p["dt"]])
            if b == a:
                continue
            j = np.arange(a, b)
            ok = km(r.Longitude_deg, r.Latitude_deg, c.lon.to_numpy()[j], c.lat.to_numpy()[j]) <= p["km"]
            if p["dmw"] is not None:
                ok &= np.abs(c.mw.to_numpy()[j] - r.Mw) <= p["dmw"]
            if ok.any():
                j = j[ok]
                m = j[np.argmin(np.abs(ct[j] - r.t))]
                idx[i], dts[i], how[i] = m, r.t - ct[m], k
    return idx, dts, how


def arc_zone(lon, lat, f=ARC):
    """forearc / arc / backarc from the arc polygon (copy of catalog/classify.py)."""
    import cartopy.io.shapereader as shp
    import shapely
    g = shapely.union_all(list(shp.Reader(str(f)).geometries()))
    c = shapely.get_coordinates(shapely.boundary(g))
    b = np.round(c[:, 1] / 0.2)
    east, west = pd.Series(c[:, 0]).groupby(b).max(), pd.Series(c[:, 0]).groupby(b).min()
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    xe = np.interp(lat, east.index.to_numpy() * 0.2, east.to_numpy())
    xw = np.interp(lat, west.index.to_numpy() * 0.2, west.to_numpy())
    ins = shapely.contains_xy(g, lon, lat)
    return np.where(ins, "arc", np.where(lon > xe, "backarc", np.where(lon < xw, "forearc",
                    np.where(lon > (xe + xw) / 2, "backarc", "forearc"))))


def idini_soil(f0, a0, kind, vs30):
    """Idini et al. (2017) soil type 1–6 from f0, the H/V amplitude and the curve type; 0 where f0 is missing."""
    f0, a0, vs30 = (np.asarray(x, float) for x in (f0, a0, vs30))
    kind = np.asarray(kind, object)
    flat = np.where(pd.isna(kind) | ~np.isin(kind, ["flat", "peak"]), a0 < HV_FLAT, kind == "flat")
    tg = 1.0 / np.where(f0 > 0, f0, np.nan)
    st = np.zeros(len(f0), int)
    for hi, k in IDINI_TG[::-1]:
        st[tg < hi] = k
    st[flat] = np.where(vs30[flat] >= 900, 1, 2)
    st[~(f0 > 0)] = 0
    return st


def class_of(c):
    """Class used for the residuals (interface, inslab or None) and the rule that gave it."""
    cls = c.cls.map({"interface": "interface", "in-slab": "inslab"})
    w = c[["w_interface", "w_inslab", "w_crustal", "w_outer_rise"]].to_numpy()
    top = np.array(["interface", "inslab", "crustal", "outer_rise"])[np.nanargmax(np.nan_to_num(w, nan=-1), 1)]
    big = (c.cls == "split") & (c.mw >= BIG) & np.isin(top, ["interface", "inslab"])
    cls[big] = top[big]
    rule = np.where(c.cls.isin(["interface", "in-slab"]), "class", np.where(big, "split, larger weight", "dropped"))
    return cls.where(cls.notna(), None), rule


def mechanism(c, cls):
    """strike, dip, rake of the plane used: interface the shallower plane, in-slab the steeper; defaults without
    a mechanism."""
    s = c[["strike1", "dip1", "rake1"]].to_numpy(float)
    t = c[["strike2", "dip2", "rake2"]].to_numpy(float)
    shallow = s[:, 1] <= t[:, 1]
    take1 = np.where(cls == "interface", shallow, ~shallow)
    p = np.where(take1[:, None], s, t)
    none = np.isnan(p).any(1)
    for k, (dip, rake) in MECH0.items():
        m = none & (cls == k)
        p[m] = [np.nan, dip, rake]
    return p, ~none


def width(mag, cls):
    from openquake.hazardlib.scalerel import get_available_scalerel
    sr = get_available_scalerel()
    w = np.full(len(mag), np.nan)
    for k, n in MSR.items():
        m = cls == k
        r = sr[n]()
        w[m] = r.get_median_width(mag[m]) if hasattr(r, "get_median_width") else np.sqrt(r.get_median_area(mag[m], 0))
    return w


def ztor_nodes(s):
    if not isinstance(s, str) or "[" not in s:
        return np.nan
    v = np.array([x.strip(" []").split() for x in s.split(";") if x.strip(" []")], float)
    return np.nanmin(v[:, 2])


def build():
    """Run step 1: match, merge, class, selection; write the record table, review_mw and the count table."""
    e, c = load_events(), load_catalogue()
    i, dt, how = match(e, c)
    e["cat_idx"], e["dt"], e["pass"] = i, dt, how
    un = e[i < 0]
    un[["EventID", "Latitude_deg", "Longitude_deg", "Depth_km", "Mw", "NoRecords"]].to_csv(
        TAB / "unmatched_events.csv", index=False)
    e = e[i >= 0].copy()
    ce = c.iloc[e.cat_idx].reset_index(drop=True)
    e = e.reset_index(drop=True)
    for k in ["event_id", "lon", "lat", "depth", "depth_kind", "depth_assigned", "mw", "mw_kind", "cls",
              "sub_inslab", "w_interface", "w_inslab", "w_crustal", "w_outer_rise", "strike1", "dip1", "rake1",
              "strike2", "dip2", "rake2"]:
        e["c_" + k] = ce[k].to_numpy()
    e["n_ff"] = e.groupby("c_event_id").EventID.transform("size")
    pairs = e[e.n_ff > 1].sort_values(["c_event_id", "t"])[["c_event_id", "EventID", "dt", "Mw", "c_mw", "NoRecords"]]
    pairs.to_csv(TAB / "duplicate_pairs.csv", index=False)

    # records
    cols = ["RecordID", "EventID", "StationID", "StationLatitude_deg", "StationLongitude_deg", "StationVs30_m_s",
            "Vs30Ind", "Repi_km_", "Rhyp_km_", "Rjb_km_", "Rrup_km_", "LowFrec_Filter_Hz_", "Tn", "PSa_RotD50",
            "EventLatitude_deg", "EventLongitude_deg", "EventDepth_km", "Mw"]
    r = pd.read_csv(F_REC, usecols=cols, dtype={"EventID": str})
    n_all = len(r)
    tn = vec(r.Tn.iloc[0])
    assert (r.Tn == r.Tn.iloc[0]).all()
    sa = np.vstack([vec(s) if isinstance(s, str) else np.full(len(tn), np.nan) for s in r.PSa_RotD50])
    lc = np.vstack([vec(s)[:2] if isinstance(s, str) else [np.nan, np.nan] for s in r.LowFrec_Filter_Hz_])
    r["f_lc"] = np.nanmax(lc, 1)
    r["t_max"] = 1.0 / (1.25 * r.f_lc)
    for k, T in IMTS.items():
        j = int(np.argmin(np.abs(tn - T)))
        assert abs(tn[j] - T) < 1e-6
        r[k] = np.where(sa[:, j] > 0, sa[:, j], np.nan)
    r = r.drop(columns=["Tn", "PSa_RotD50", "LowFrec_Filter_Hz_"])
    r = r.merge(e[["EventID", "t", "dt", "pass", "n_ff"] + [k for k in e if k.startswith("c_")]], on="EventID",
                how="inner")

    # duplicates: one record per station, from the flatfile entry closest in time to the catalogue origin
    r["adt"] = r.dt.abs()
    n_before = len(r)
    r = r.sort_values(["c_event_id", "StationID", "adt"]).drop_duplicates(["c_event_id", "StationID"])
    n_dup = n_before - len(r)

    # Mw check, flatfile against catalogue
    ev = r.groupby("c_event_id").agg(EventID=("EventID", "first"), mw_ff=("Mw", "first"), mw=("c_mw", "first"),
                                    cls=("c_cls", "first"), n=("RecordID", "size")).reset_index()
    bad = ev[(np.abs(ev.mw_ff - ev.mw) >= MW_TOL) & (np.maximum(ev.mw_ff, ev.mw) >= MW_REVIEW)]
    bad.assign(dmw=bad.mw_ff - bad.mw).to_csv(TAB / "review_mw.csv", index=False)

    st = pd.read_csv(F_ST).replace(-999, np.nan)
    st = st.rename(columns={"CodeSta": "StationID"})[["StationID", "f0_HVSR", "A0_HVSR", "TypeCurveHVSR"]]
    r = r.merge(st, on="StationID", how="left")

    # class
    cc = r.rename(columns={k: k[2:] for k in r if k.startswith("c_")})
    cls, rule = class_of(cc)
    r["cls"], r["cls_rule"] = cls.to_numpy(), rule

    # counts at each step
    steps = []

    def count(lab, d):
        for k in ["interface", "inslab"]:
            g = d[d.cls == k]
            steps.append(dict(step=lab, cls=k, events=g.c_event_id.nunique(), records=len(g)))
        steps.append(dict(step=lab, cls="all", events=d.c_event_id.nunique(), records=len(d)))

    steps.append(dict(step="flatfile records", cls="all", events=pd.read_csv(F_EV).shape[0], records=n_all))
    steps.append(dict(step="matched to the catalogue", cls="all", events=int((i >= 0).sum()), records=n_before))
    steps.append(dict(step="after merging duplicate entries", cls="all", events=r.c_event_id.nunique(),
                      records=len(r)))
    r = r[~r.c_event_id.isin(bad.c_event_id)]
    steps.append(dict(step=f"|ΔMw| < {MW_TOL}", cls="all", events=r.c_event_id.nunique(), records=len(r)))
    r = r[r.cls.notna()].copy()
    count("interface or in-slab", r)
    r = r[r.c_mw >= MW_MIN]
    count(f"Mw ≥ {MW_MIN}", r)
    r = r[r.Rrup_km_ <= RRUP_MAX]
    count(f"Rrup ≤ {RRUP_MAX:.0f} km", r)
    r = r[r[list(IMTS)].notna().any(axis=1)]
    count("RotD50 present", r)
    for k, T in IMTS.items():
        ok = r[k].notna() & ((k == "PGA") | (T <= r.t_max))
        r[k] = r[k].where(ok)
        g = r[ok]
        for q in ["interface", "inslab"]:
            h = g[g.cls == q]
            steps.append(dict(step=f"usable at {k}", cls=q, events=h.c_event_id.nunique(), records=len(h)))
    r = r[r[list(IMTS)].notna().any(axis=1)].copy()

    # event and rupture parameters
    out = pd.DataFrame({"record_id": r.RecordID, "event_id": r.c_event_id, "ff_event_id": r.EventID,
                        "station": r.StationID, "cls": r.cls, "cls_rule": r.cls_rule, "sub_inslab": r.c_sub_inslab,
                        "mw": r.c_mw, "mw_ff": r.Mw, "mw_kind": r.c_mw_kind, "time": r.t, "dt_ff": r.dt,
                        "match_pass": r["pass"], "hypo_lon": r.c_lon, "hypo_lat": r.c_lat})
    d = r.c_depth.to_numpy(float)
    src = np.where(np.isfinite(d), "catalogue", "")
    a = np.isnan(d) & np.isfinite(r.c_depth_assigned.to_numpy(float))
    d[a], src[a] = r.c_depth_assigned.to_numpy(float)[a], "catalogue, assigned"
    f = np.isnan(d)
    d[f], src[f] = r.EventDepth_km.to_numpy(float)[f], "flatfile"
    out["hypo_depth"], out["depth_src"] = d, src
    dh = km(r.EventLongitude_deg.to_numpy(), r.EventLatitude_deg.to_numpy(), r.c_lon.to_numpy(), r.c_lat.to_numpy())
    out["loc_dh"], out["loc_dz"] = dh, r.EventDepth_km.to_numpy() - d
    out["loc_flag"] = (dh > LOC_KM) | (np.abs(out.loc_dz) > LOC_DZ)
    p, has = mechanism(r.rename(columns={k: k[2:] for k in r if k.startswith("c_")}), r.cls.to_numpy())
    out["strike"], out["dip"], out["rake"], out["mech"] = p[:, 0], p[:, 1], p[:, 2], has
    out["width"] = width(out.mw.to_numpy(), out.cls.to_numpy())
    ev_nodes = load_events().set_index("EventID").Rupture_Lat_Lon_Dep_deg_deg_km
    zn = r.EventID.map(ev_nodes).map(ztor_nodes).to_numpy(float)
    zc = np.maximum(d - 0.5 * out.width * np.sin(np.radians(out.dip)), 0)
    out["ztor"] = np.where(np.isfinite(zn), zn, zc)
    out["ztor_src"] = np.where(np.isfinite(zn), "rupture nodes", "hypocentre at mid-width")
    for k, n in [("repi", "Repi_km_"), ("rhypo", "Rhyp_km_"), ("rjb", "Rjb_km_"), ("rrup", "Rrup_km_")]:
        out[k] = r[n]
    out["sta_lon"], out["sta_lat"] = r.StationLongitude_deg, r.StationLatitude_deg
    out["vs30"], out["vs30_code"] = r.StationVs30_m_s, r.Vs30Ind
    out["vs30measured"] = r.Vs30Ind == 1
    out["f0"], out["a0_hv"], out["hv_curve"] = r.f0_HVSR, r.A0_HVSR, r.TypeCurveHVSR
    out["arc_zone"] = arc_zone(out.sta_lon, out.sta_lat)
    out["backarc"] = out.arc_zone == "backarc"
    out["soiltype"] = idini_soil(out.f0, out.a0_hv, out.hv_curve, out.vs30)
    out["rvolc"] = 0.0
    out["f_lc"], out["t_max"] = r.f_lc, r.t_max
    for k in IMTS:
        out[k] = r[k]
    out = out.sort_values(["time", "station"]).reset_index(drop=True)
    out.to_csv(TAB / f"records_{DATE}.csv", index=False)
    cnt = pd.DataFrame(steps)
    cnt.to_csv(TAB / f"selection_counts_{DATE}.csv", index=False)
    return out, cnt, dict(unmatched=un, pairs=pairs, review=bad, n_dup=n_dup)


if __name__ == "__main__":
    out, cnt, x = build()
    print(cnt.to_string(index=False))
    print(f"unmatched events {len(x['unmatched'])}, records {int(x['unmatched'].NoRecords.sum())}")
    print(f"catalogue events with two flatfile entries {x['pairs'].c_event_id.nunique()}, records dropped {x['n_dup']}")
    print(f"review_mw {len(x['review'])} events")

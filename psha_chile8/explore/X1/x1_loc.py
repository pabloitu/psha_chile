"""X1 tier 2: default depths, location agreement on matched events, location-priority variants (A4 exploration)."""
import time

import numpy as np
import pandas as pd

import x1_io as io

# settings
KS = [3, 5, 10]
K_USE = 5
MIN_N = 300
MIN_SPIKE = 10
MIN_SHARE = 0.003
LABELS = ["baseline", "nb_order", "nb_calibrated"]
LOCS = ["potin", "csn", "ehb1", "ehb2", "ehb3", "iscgem", "centennial", "isc", "comcat", "csn_isc", "gcmt", "gcmt_c"]
LNAME = {"potin": "Potin et al.", "csn": "CSN web", "ehb1": "ISC-EHB L1", "ehb2": "ISC-EHB L2", "ehb3": "ISC-EHB L3",
         "iscgem": "ISC-GEM", "centennial": "Centennial", "isc": "ISC prime", "comcat": "ComCat",
         "csn_isc": "CSN in ISC", "gcmt": "GCMT hypocentre", "gcmt_c": "GCMT centroid"}
FALL = ["ehb1", "ehb2", "iscgem", "centennial", "isc", "comcat", "csn_isc", "ehb3", "gcmt"]
ARC_LON = None
SECTIONS = [-20.0, -23.0, -27.0, -31.0, -33.5, -37.0]
CLASSES = ["above slab, shallow", "interface band", "in slab", "below slab", "above slab, deep", "outside Slab2",
           "unknown depth"]
CCOL = dict(zip(CLASSES, ["#2e8b57", "#e0641e", "#2166ac", "#6a3d9a", "#c9a227", "#bdbdbd", "#f0f0f0"]))


# default depths
def spikes(z, k):
    """Depth bins (1 km) whose count exceeds k times the median of the ±5 km neighbours."""
    z = z[np.isfinite(z) & (z >= -5) & (z < 700)]
    if len(z) < MIN_N:
        return []
    b = np.floor(z).astype(int) + 5
    c = np.bincount(b, minlength=720).astype(float)
    out = []
    for i in np.flatnonzero(c >= MIN_SPIKE):
        nb = np.r_[c[max(i - 5, 0):i], c[i + 1:i + 6]]
        med = max(np.median(nb), 1.0)
        if c[i] > k * med and c[i] / len(z) >= MIN_SHARE:
            out.append((i - 5, int(c[i]), c[i] / len(z), c[i] / med))
    return out


def agency_periods(src, ag):
    p = [(-1e9, 1964), (1964, 1980), (1980, 2000), (2000, 2012), (2012, 1e9)]
    if src == "gcmt":
        p = [(1976, 1981), (1981, 1986), (1986, 2004), (2004, 1e9)]
    return p


def defaults(o):
    f = io.load("defaults")
    if f is not None:
        return f
    allo = io.events("isc", all_origins=True)
    t = [pd.DataFrame({"src": "isc", "agency": allo.agency, "z": allo.depth, "yr": io.year(allo.t.to_numpy()),
                       "fix": allo.depth_fixed})]
    for s in io.SOURCES:
        if s == "isc":
            continue
        x = o[o.src == s]
        ag = x.agency.fillna(s) if s not in ("iscehb",) else x.zq.fillna("?").radd("ISC-EHB ")
        t.append(pd.DataFrame({"src": s, "agency": ag.to_numpy(), "z": x.z.to_numpy(), "yr": io.year(x.t.to_numpy()),
                               "fix": x.zfix.to_numpy()}))
    g = io.events("gcmt", all_origins=True)
    g = g[g.prime.astype(bool)]
    t.append(pd.DataFrame({"src": "gcmt", "agency": "GCMT centroid", "z": g.depth, "yr": io.year(g.t.to_numpy()),
                           "fix": g.depth_fixed}))
    t = pd.concat(t, ignore_index=True)
    rows = []
    for (s, ag), x in t.groupby(["src", "agency"]):
        if len(x) < MIN_N:
            continue
        for lo, hi in [(-1e9, 1e9)] + agency_periods(s, ag):
            y = x[(x.yr >= lo) & (x.yr < hi)]
            for k in KS:
                for d, n, sh, r in spikes(y.z.to_numpy(float), k):
                    fx = pd.to_numeric(y.fix[np.floor(y.z) == d].map({True: 1, False: 0, "True": 1, "False": 0}),
                                       errors="coerce").mean()
                    rows.append({"src": s, "agency": ag, "period": "all" if lo < -1e8 and hi > 1e8 else
                                 f"{max(lo, 1900):.0f}–{min(hi, 2026):.0f}", "k": k, "depth": d, "n": n, "share": sh,
                                 "ratio": r, "n_agency": len(y), "flag_fixed": fx})
    f = pd.DataFrame(rows)
    io.save(f, "defaults")
    return f


def default_mask(o, dflt, k=K_USE):
    """True where an origin's depth sits on a detected default bin of its source / agency (whole record)."""
    d = dflt[(dflt.k == k) & (dflt.period == "all")]
    key = set(zip(d.src, d.agency, d.depth))
    ag = np.where(o.src == "iscehb", "ISC-EHB " + o.zq.fillna("?").astype(str), o.agency.fillna(o.src).astype(str))
    zb = np.floor(o.z.to_numpy())
    m = np.array([(s, a, z) in key for s, a, z in zip(o.src, ag, zb)])
    # whole-km depths of the relocated / web catalogs are not defaults
    return m


# location table per event
def loctable(o, lab, dm):
    """Wide table: one row per event, lat / lon / depth / unknown-depth flag per location source."""
    o = o.assign(ev=lab, dflt=dm)
    unk = o.z.isna() | (o.zfix.astype(str) == "True") | o.dflt
    unk |= (o.src == "centennial") & (o.z == 0)
    o["unk"] = unk
    key = o.src.copy()
    eh = o.src == "iscehb"
    key[eh] = "ehb" + o.zq[eh].astype(str).str[-1].replace({"?": "3"})
    o["key"] = key
    w = o.pivot_table(index="ev", columns="key", values=["lat", "lon", "z", "unk", "t"], aggfunc="first")
    w.columns = [f"{b}_{a}" for a, b in w.columns]
    g = io.events("gcmt", all_origins=True)
    g = g[g.prime.astype(bool)].set_index("src_id")
    hyp = o[o.src == "gcmt"]
    c = g.loc[hyp.sid.to_numpy()]
    cc = pd.DataFrame({"lat": c.lat.to_numpy(), "lon": c.lon.to_numpy(), "z": c.depth.to_numpy(),
                       "unk": (c.depth_fixed.astype(str) == "True").to_numpy() | (c.depth.to_numpy() == 12.0)},
                      index=hyp.ev.to_numpy())
    cc = cc[~cc.index.duplicated()]
    for v in cc.columns:
        w[f"gcmt_c_{v}"] = cc[v].reindex(w.index)
    m = o.groupby("ev").agg(md=("mmed", "max"), mx=("mmax", "max"))
    w = w.join(m)
    for s in LOCS:
        for v in ("lat", "lon", "z", "unk", "t"):
            if f"{s}_{v}" not in w:
                w[f"{s}_{v}"] = np.nan
    w["t"] = w[[f"{s}_t" for s in LOCS if s != "gcmt_c"]].bfill(axis=1).iloc[:, 0]
    w["yr"] = io.year(w.t.to_numpy())
    return w


def regions(w, la, lo):
    sl, th, dip = io.slab_at(lo, la)
    dtr, st = io.setting(lo, la)
    return pd.DataFrame({"band": io.latband(la), "setting": st, "trench_km": dtr, "slab": sl, "thk": th, "dip": dip,
                         "s44": la < -44, "s46": la < -46}, index=w.index)


# agreement
def agreement(w, reg):
    rows = []
    pairs = [("potin", "ehb1"), ("potin", "ehb2"), ("potin", "isc"), ("potin", "comcat"), ("potin", "iscgem"),
             ("potin", "gcmt_c"), ("ehb1", "isc"), ("ehb1", "comcat"), ("ehb1", "iscgem"), ("ehb1", "gcmt_c"),
             ("ehb1", "centennial"), ("isc", "comcat"), ("iscgem", "centennial"), ("csn", "ehb1"), ("csn", "comcat"),
             ("csn", "potin"), ("ehb2", "isc"), ("ehb3", "isc"), ("comcat", "gcmt_c")]
    d = {}
    for a, b in pairs:
        ok = w[f"{a}_lat"].notna() & w[f"{b}_lat"].notna()
        dh = io.hav(w[f"{a}_lat"], w[f"{a}_lon"], w[f"{b}_lat"], w[f"{b}_lon"])
        dz = w[f"{a}_z"] - w[f"{b}_z"]
        free = (w[f"{a}_unk"] != True) & (w[f"{b}_unk"] != True)  # noqa: E712
        d[(a, b)] = pd.DataFrame({"dh": dh, "dz": dz.where(free), "ok": ok})
        for by in ("all", "band", "setting", "period", "mband"):
            if by == "all":
                grp = pd.Series("all", index=w.index)
            elif by == "period":
                grp = pd.Series(io.label(w.yr.to_numpy(), io.PERIODS), index=w.index)
            elif by == "mband":
                grp = pd.Series(io.label(w.md.fillna(0).to_numpy(), io.MBANDS), index=w.index)
            else:
                grp = reg[by]
            x = d[(a, b)][ok].assign(g=grp[ok])
            for gv, y in x.groupby("g"):
                if len(y) < 10:
                    continue
                z = y.dz.dropna()
                rows.append({"a": a, "b": b, "by": by, "group": gv, "n": len(y), "dh_med": y.dh.median(),
                             "dh_p90": y.dh.quantile(0.9), "n_dz": len(z), "dz_med": z.median() if len(z) else np.nan,
                             "dz_mad": 1.4826 * (z - z.median()).abs().median() if len(z) else np.nan})
    return pd.DataFrame(rows), d


def triple(w, trios, by=None, reg=None):
    """Depth errors per source by triple collocation of free depths (robust variances of the differences)."""
    rows = []
    for a, b, c in trios:
        ok = np.ones(len(w), bool)
        for s in (a, b, c):
            ok &= w[f"{s}_z"].notna().to_numpy() & (w[f"{s}_unk"] != True).to_numpy()  # noqa: E712
        x = w[ok]
        grp = pd.Series("all", index=x.index) if by is None else reg.loc[x.index, by]
        for gv, y in x.groupby(grp):
            if len(y) < 50:
                continue
            rv = lambda u: (1.4826 * np.median(np.abs(u - np.median(u)))) ** 2  # noqa: E731
            ab, ac, bc = rv(y[f"{a}_z"] - y[f"{b}_z"]), rv(y[f"{a}_z"] - y[f"{c}_z"]), rv(y[f"{b}_z"] - y[f"{c}_z"])
            s = {a: (ab + ac - bc) / 2, b: (ab + bc - ac) / 2, c: (ac + bc - ab) / 2}
            rows.append({"trio": f"{a}|{b}|{c}", "group": gv, "n": len(y),
                         **{f"sig_{k}": np.sqrt(max(v, 0.25)) for k, v in s.items()}})
    return pd.DataFrame(rows)


# location variants
def choose(w, reg, order, potin_ok=None, sig=None):
    """Epicentre from the first source in order; depth from the first free depth in order, else unknown."""
    n = len(w)
    lat, lon, z, src, zsrc = (np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan),
                              np.full(n, None, object), np.full(n, None, object))
    unk = np.ones(n, bool)
    for s in order:
        ok = w[f"{s}_lat"].notna().to_numpy()
        if s in ("potin", "csn") and potin_ok is not None:
            ok &= potin_ok
        e = ok & np.isnan(lat)
        lat[e], lon[e], src[e] = w[f"{s}_lat"].to_numpy()[e], w[f"{s}_lon"].to_numpy()[e], s
        f = ok & unk & w[f"{s}_z"].notna().to_numpy() & (w[f"{s}_unk"] != True).to_numpy()  # noqa: E712
        z[f], zsrc[f], unk[f] = w[f"{s}_z"].to_numpy()[f], s, False
    for s in order:
        f = np.isnan(z) & w[f"{s}_z"].notna().to_numpy() & (src == s)
        z[f], zsrc[f] = w[f"{s}_z"].to_numpy()[f], s
    return pd.DataFrame({"lat": lat, "lon": lon, "z": z, "unk": unk, "src": src, "zsrc": zsrc}, index=w.index)


def choose_sigma(w, reg, sig):
    """L-d: per event the free depth (and its epicentre) of the source with the smallest σ in the event's band."""
    n = len(w)
    best = np.full(n, np.inf)
    pick = np.full(n, None, object)
    for s in LOCS:
        if s == "gcmt_c":
            continue
        sv = reg.band.map(sig.get(s, {})).astype(float).fillna(sig.get(s, {}).get("all", np.inf)).to_numpy()
        ok = w[f"{s}_z"].notna().to_numpy() & (w[f"{s}_unk"] != True).to_numpy() & (sv < best)  # noqa: E712
        best[ok], pick[ok] = sv[ok], s
    out = choose(w, reg, ["potin", "csn"] + FALL)
    for s in set(pick[pick != None]):  # noqa: E711
        k = pick == s
        out.loc[k, ["lat", "lon", "z"]] = w.loc[k, [f"{s}_lat", f"{s}_lon", f"{s}_z"]].to_numpy()
        out.loc[k, "src"] = s
        out.loc[k, "zsrc"] = s
        out.loc[k, "unk"] = False
    return out


def proxy(c):
    s, th, _ = io.slab_at(c.lon.to_numpy(), c.lat.to_numpy())
    z = c.z.to_numpy()
    k = np.full(len(c), "unknown depth", dtype=object)
    ok = ~c.unk.to_numpy() & np.isfinite(z)
    k[ok & np.isnan(s)] = "outside Slab2"
    m = ok & np.isfinite(s)
    th = np.where(np.isfinite(th), th, 40.0)
    shallow = m & (z < 30) & (z < s - 15)
    band = m & (np.abs(z - s) <= 15) & (s < 60)
    ins = m & ~band & (z >= s - 15) & (z <= s + th)
    k[m & (z > s + th)] = "below slab"
    k[m & (z < s - 15) & (z >= 30)] = "above slab, deep"
    k[ins] = "in slab"
    k[band] = "interface band"
    k[shallow] = "above slab, shallow"
    return k, s, th


def variants(w, reg, sig):
    arc_e = None
    la, lo = w.potin_lat.fillna(w.csn_lat), w.potin_lon.fillna(w.csn_lon)
    dtr, st = io.setting(lo.fillna(-70).to_numpy(), la.fillna(-30).to_numpy())
    west = ~np.isin(st, ["backarc"])
    v = {"L-a": choose(w, reg, ["potin", "csn"] + FALL)}
    for south in (44, 46):
        ok = (la.to_numpy() <= -18) & (la.to_numpy() >= -south) & west
        v[f"L-b {south}°S"] = choose(w, reg, ["potin", "csn"] + FALL, potin_ok=ok)
        ok2 = (la.to_numpy() <= -18) & (la.to_numpy() >= -south) & (lo.to_numpy() <= LON_CUT)
        v[f"L-b {south}°S, lon ≤ {LON_CUT}"] = choose(w, reg, ["potin", "csn"] + FALL, potin_ok=ok2)
    v["L-c"] = choose(w, reg, ["ehb1", "potin", "csn"] + FALL[1:])
    v["L-d"] = choose_sigma(w, reg, sig)
    return v


LON_CUT = -68.0


def run():
    T0 = time.time()
    o = io.load("origins", dtype={"sid": str})
    lab = io.load("labels")
    dflt = defaults(o)
    dflt.to_csv(io.TAB / "t2_default_depths.csv", index=False)
    dm = default_mask(o, dflt)
    print("defaults", len(dflt), dm.sum(), round(time.time() - T0), flush=True)
    res = {}
    for nm in LABELS:
        w = loctable(o, lab[nm].to_numpy(), dm)
        la = w[[f"{s}_lat" for s in ["potin", "csn", "ehb1", "ehb2", "iscgem", "centennial", "isc", "comcat",
                                     "csn_isc", "ehb3", "gcmt"]]].bfill(axis=1).iloc[:, 0]
        lo = w[[f"{s}_lon" for s in ["potin", "csn", "ehb1", "ehb2", "iscgem", "centennial", "isc", "comcat",
                                     "csn_isc", "ehb3", "gcmt"]]].bfill(axis=1).iloc[:, 0]
        reg = regions(w, la.to_numpy(), lo.to_numpy())
        res[nm] = (w, reg)
        print("loctable", nm, len(w), round(time.time() - T0), flush=True)
    w, reg = res["baseline"]
    w.to_csv(io.CACHE / "loc_wide_baseline.csv.gz")
    reg.to_csv(io.CACHE / "regions_baseline.csv.gz")
    ag, dd = agreement(w, reg)
    ag.to_csv(io.TAB / "t2_location_agreement.csv", index=False)
    trios = [("potin", "ehb1", "comcat"), ("potin", "ehb1", "isc"), ("potin", "isc", "comcat"), ("ehb1", "isc", "comcat"),
             ("potin", "ehb2", "comcat"), ("potin", "comcat", "gcmt_c"), ("ehb1", "comcat", "gcmt_c"),
             ("potin", "ehb1", "gcmt_c"), ("csn", "comcat", "isc"), ("iscgem", "isc", "comcat"),
             ("potin", "iscgem", "comcat"), ("csn", "potin", "comcat")]
    tc = pd.concat([triple(w, trios), triple(w, trios, "band", reg).assign(by="band"),
                    triple(w, trios, "setting", reg).assign(by="setting")])
    tc.to_csv(io.TAB / "t2_depth_triple_collocation.csv", index=False)
    l1 = ag[(ag.b == "ehb1") & ag.by.isin(["all", "band"])]
    sig = {}
    for a, x in l1.groupby("a"):
        sig[a] = dict(zip(x.group, x.dz_mad))
    sig["ehb1"] = {"all": 1.65}
    for s, rows in tc[tc.group == "all"].groupby("trio"):
        pass
    tca = tc[(tc.get("by").isna()) | (tc.group == "all")] if "by" in tc else tc
    for s in LOCS:
        col = f"sig_{s}"
        if col in tc and s not in sig:
            v = tc[col].dropna()
            if len(v):
                sig[s] = {"all": float(v.median())}
    for s in ("isc", "comcat", "iscgem", "centennial", "csn_isc", "ehb2", "ehb3", "gcmt", "csn"):
        sig.setdefault(s, {"all": 25.0})
    pd.DataFrame([{"src": k, "group": g, "sigma": v} for k, d in sig.items() for g, v in d.items()]).to_csv(
        io.TAB / "t2_depth_sigma_used_for_L-d.csv", index=False)
    out, cls = [], {}
    for nm in LABELS:
        w, reg = res[nm]
        v = variants(w, reg, sig)
        for vn, c in v.items():
            k, s, th = proxy(c)
            c["cls"], c["slab"], c["thk"] = k, s, th
            c["md"], c["yr"] = w.md.to_numpy(), w.yr.to_numpy()
            c["band"], c["setting"] = reg.band.to_numpy(), reg.setting.to_numpy()
            cls[(nm, vn)] = c
            for m in (4.5, 5.5):
                x = c[c.md >= m]
                out.append({"match": nm, "loc": vn, "mmin": m, "n": len(x), **x.cls.value_counts().to_dict(),
                            "unknown_share": float((x.cls == "unknown depth").mean())})
    pd.DataFrame(out).to_csv(io.TAB / "t2_proxy_class_counts.csv", index=False)
    ch = []
    for nm in LABELS:
        base = cls[(nm, "L-a")]
        for (n2, vn), c in cls.items():
            if n2 != nm or vn == "L-a":
                continue
            d = base.cls.to_numpy() != c.cls.to_numpy()
            for by in ("band", "setting", "period"):
                g = base[by] if by != "period" else pd.Series(io.label(base.yr.to_numpy(), io.PERIODS), index=base.index)
                for m in (4.5, 5.5):
                    k = base.md.to_numpy() >= m
                    t = pd.DataFrame({"g": g.to_numpy()[k], "d": d[k]}).groupby("g").d.agg(["sum", "size"])
                    for gv, r in t.iterrows():
                        ch.append({"match": nm, "loc": vn, "by": by, "group": gv, "mmin": m, "changed": int(r["sum"]),
                                   "n": int(r["size"])})
    pd.DataFrame(ch).to_csv(io.TAB / "t2_proxy_class_changes.csv", index=False)
    tr = []
    for (nm, vn), c in cls.items():
        for a in sorted(set(c.cls)):
            for b in sorted(set(c.cls)):
                pass
    for nm in LABELS:
        a = cls[(nm, "L-a")]
        for vn in [v for (n2, v) in cls if n2 == nm and v != "L-a"]:
            b = cls[(nm, vn)]
            k = a.md >= 4.5
            x = pd.crosstab(a.cls[k], b.cls[k])
            x.to_csv(io.TAB / f"t2_transition_{nm}_{vn.replace(' ', '_').replace('°', '').replace(',', '')}.csv")
    unk = []
    for (nm, vn), c in cls.items():
        x = c[c.md >= 4.5].assign(per=lambda d: io.label(d.yr.to_numpy(), io.PERIODS))
        for by in ("per", "band", "setting"):
            for gv, y in x.groupby(by):
                unk.append({"match": nm, "loc": vn, "by": by, "group": gv, "n": len(y), "unknown": int(y.unk.sum()),
                            "share": float(y.unk.mean())})
    pd.DataFrame(unk).to_csv(io.TAB / "t2_unknown_depths.csv", index=False)
    allc = []
    for (nm, vn), c in cls.items():
        allc.append(c.assign(match=nm, loc=vn).reset_index())
    pd.concat(allc).to_csv(io.CACHE / "locvariants.csv.gz", index=False)
    print("variants done", round(time.time() - T0), flush=True)
    plt = io.fig_setup()
    figs(plt, o, dflt, res["baseline"][0], res["baseline"][1], ag, dd, cls)
    print("tier 2 done", round(time.time() - T0), flush=True)


# figures
def figs(plt, o, dflt, w, reg, ag, dd, cls):
    for f in (fig_spikes, fig_offset_maps, fig_dz_lat, fig_changes, fig_sections):
        try:
            if f is fig_spikes:
                f(plt, o, dflt)
            elif f is fig_offset_maps:
                f(plt, w, reg)
            elif f is fig_dz_lat:
                f(plt, w, reg)
            elif f is fig_changes:
                f(plt, cls)
            else:
                f(plt, w, cls)
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            with open(io.CACHE / "failures.log", "a") as fh:
                fh.write(f"tier 2 {f.__name__}: {e!r}\n")


def fig_spikes(plt, o, dflt):
    allo = io.events("isc", all_origins=True)
    show = [("isc", "ISC"), ("isc", "NEIC"), ("isc", "GUC"), ("isc", "IDC"), ("isc", "SJA"), ("comcat", None),
            ("iscgem", None), ("iscehb", None), ("gcmt", "GCMT centroid"), ("centennial", None), ("csn_isc", None),
            ("cabello", None)]
    fig, ax = plt.subplots(4, 3, figsize=(16, 14), layout="constrained")
    for a, (s, ag) in zip(ax.flat, show):
        if s == "isc":
            z = allo.depth[allo.agency == ag].to_numpy(float)
            key = ("isc", ag)
        elif s == "gcmt":
            g = io.events("gcmt", all_origins=True)
            z = g.depth[g.prime.astype(bool)].to_numpy(float)
            key = ("gcmt", ag)
        elif s == "cabello":
            z = io.events("cabello").depth.to_numpy(float)
            key = None
        else:
            z = o.z[o.src == s].to_numpy(float)
            key = (s, None)
        z = z[np.isfinite(z)]
        a.hist(np.clip(z, -1, 300), bins=np.arange(-1, 301, 1), color="0.55", lw=0)
        a.set_yscale("log")
        if key:
            d = dflt[(dflt.src == key[0]) & (dflt.k == K_USE) & (dflt.period == "all")]
            if key[1]:
                d = d[d.agency == key[1]]
            d = d.groupby("depth").n.sum()
            for dep, n in d.items():
                a.plot(dep + 0.5, n, "v", color="#e0641e", ms=6)
            lab = ", ".join(f"{int(x)}" for x in d.sort_values(ascending=False).index[:8])
        else:
            sp = spikes(z, K_USE)
            for dep, n, _, _ in sp:
                a.plot(dep + 0.5, n, "v", color="#e0641e", ms=6)
            lab = ", ".join(str(x[0]) for x in sorted(sp, key=lambda x: -x[1])[:8])
        a.set_title(f"{io.NAME.get(s, s)}{' ' + ag if ag and s == 'isc' else ''} ({len(z)}): {lab} km", fontsize=10)
        a.set_xlim(-2, 300)
    for a in ax[-1]:
        a.set_xlabel("depth [km]")
    fig.suptitle(f"Which depths are agency defaults? 1 km histograms, spikes (k = {K_USE}) marked", x=0.01, ha="left")
    io.savefig(fig, "t2_depth_spikes", "Depth histograms per source / agency with the automatically detected "
               "default-depth spikes (k = 5)")


def fig_offset_maps(plt, w, reg):
    import cartopy.crs as ccrs
    from pituplots.maps import dress_map
    fig = plt.figure(figsize=(14, 10), layout="constrained")
    for j, ref in enumerate(["ehb1", "ehb2"]):
        ok = w.potin_lat.notna() & w[f"{ref}_lat"].notna()
        x = w[ok]
        dh = io.hav(x.potin_lat, x.potin_lon, x[f"{ref}_lat"], x[f"{ref}_lon"])
        free = (x[f"{ref}_unk"] != True)  # noqa: E712
        dz = (x.potin_z - x[f"{ref}_z"]).where(free)
        cell = pd.DataFrame({"i": np.floor(x.potin_lat), "j": np.floor(x.potin_lon), "dh": dh, "dz": dz})
        g = cell.groupby(["i", "j"]).agg(dh=("dh", "median"), dz=("dz", "median"), n=("dh", "size")).reset_index()
        g = g[g.n >= 5]
        for i, (v, cm, lim, lab) in enumerate((("dh", "viridis", (0, 30), "median epicentre offset [km]"),
                                               ("dz", "RdBu_r", (-25, 25), "median depth, Potin − ref [km]"))):
            ax = fig.add_subplot(1, 4, 2 * j + i + 1, projection=ccrs.PlateCarree())
            dress_map(ax, [-76, -64, -46, -17], coastline=True, gridlines=True)
            sc = ax.scatter(g.j + 0.5, g.i + 0.5, c=g[v], s=np.clip(g.n, 5, 200) * 0.6 + 10, marker="s", cmap=cm,
                            vmin=lim[0], vmax=lim[1], transform=ccrs.PlateCarree(), edgecolor="0.3", lw=0.3)
            plt.colorbar(sc, ax=ax, shrink=0.5, label=lab, orientation="horizontal", pad=0.03)
            ax.set_title(f"Potin vs {LNAME[ref]}\n{len(x)} events", fontsize=10)
    fig.suptitle("Where do Potin et al. and ISC-EHB disagree in epicentre and depth? Medians per 1° cell (≥ 5 events)",
                 x=0.01, ha="left")
    io.savefig(fig, "t2_potin_vs_ehb_maps", "Median epicentre offset and depth difference per 1° cell, Potin "
               "against ISC-EHB L1 and L2")


def fig_dz_lat(plt, w, reg):
    fig, ax = plt.subplots(2, 3, figsize=(16, 9), layout="constrained", sharex=True)
    lat = w[[f"{s}_lat" for s in ("potin", "ehb1", "isc")]].bfill(axis=1).iloc[:, 0]
    for a, s in zip(ax.flat, ["potin", "comcat", "isc", "iscgem", "gcmt_c", "csn"]):
        ok = w[f"{s}_z"].notna() & w.ehb1_z.notna() & (w[f"{s}_unk"] != True) & (w.ehb1_unk != True)  # noqa: E712
        dz = (w[f"{s}_z"] - w.ehb1_z)[ok]
        la = lat[ok]
        dep = w.ehb1_z[ok]
        sc = a.scatter(la, dz, c=dep, s=4, cmap="viridis", vmin=0, vmax=200, alpha=0.6, lw=0)
        b = pd.DataFrame({"b": np.round(la), "dz": dz}).groupby("b").dz.agg(["median", "size"])
        b = b[b["size"] >= 10]
        a.plot(b.index, b["median"], color="#e0641e", lw=2)
        a.axhline(0, color="0.3", lw=0.7)
        a.set_ylim(-60, 60)
        a.set_title(f"{LNAME[s]} − ISC-EHB L1 ({ok.sum()} events, free depths)", fontsize=10)
        a.set_ylabel("Δ depth [km]")
    for a in ax[-1]:
        a.set_xlabel("latitude [°]")
    plt.colorbar(sc, ax=ax, label="ISC-EHB L1 depth [km]", shrink=0.6)
    fig.suptitle("How do depth differences against ISC-EHB L1 vary along the margin? (orange: median per 1°)",
                 x=0.01, ha="left")
    io.savefig(fig, "t2_dz_vs_lat", "Depth differences against ISC-EHB L1 by latitude per source, coloured by L1 depth")


def fig_changes(plt, cls):
    fig, ax = plt.subplots(2, 1, figsize=(15, 9), layout="constrained")
    base = cls[("baseline", "L-a")]
    vs = [v for (n, v) in cls if n == "baseline" and v != "L-a"]
    for a, m in zip(ax, (4.5, 5.5)):
        k = base.md.to_numpy() >= m
        bands = sorted(set(base.band[k].dropna()), key=lambda s: float(s.split("–")[0]))
        wd = 0.8 / len(vs)
        for i, v in enumerate(vs):
            c = cls[("baseline", v)]
            d = (base.cls.to_numpy() != c.cls.to_numpy()) & k
            n = pd.Series(d).groupby(base.band.to_numpy()).sum().reindex(bands).fillna(0)
            a.bar(np.arange(len(bands)) + i * wd, n.values, wd, color=io.palette.SERIES[i], label=v)
        a.set_xticks(np.arange(len(bands)) + 0.4 - wd / 2, bands, rotation=45, ha="right")
        a.set_ylabel(f"events M ≥ {m} changing class")
        a.set_title(f"M ≥ {m}: events whose depth proxy class differs from L-a (Potin first everywhere)", fontsize=11)
    ax[0].legend(ncol=3, fontsize=9)
    fig.suptitle("How many events change depth-proxy class when the location priority changes? By 2° band",
                 x=0.01, ha="left")
    io.savefig(fig, "t2_class_changes", "Events changing depth-proxy class against L-a, per 2° latitude band, "
               "for each location-priority variant (M ≥ 4.5 and M ≥ 5.5)")


def fig_sections(plt, w, cls):
    import shapely
    import shapely.ops
    from pituplots.io import read_slab2
    from pituplots.sections import add_slab, profiles_from_line, project
    tr, _, _ = io.shapes()
    line = shapely.union_all(tr)
    if line.geom_type != "LineString":
        line = shapely.ops.linemerge(line)
    if line.geom_type != "LineString":
        line = max(line.geoms, key=lambda g: g.length)
    top = read_slab2(io.REPO / "data/slab_2.0/sam_slab2_dep_02.23.18.xyz")
    thk = read_slab2(io.REPO / "data/slab_2.0/sam_slab2_thk_02.23.18.xyz")
    prof = profiles_from_line(line, SECTIONS, width=100, side=(-60, -30), length=(-60, 400))
    fig, ax = plt.subplots(len(SECTIONS), 1, figsize=(13, 3.6 * len(SECTIONS)), layout="constrained")
    for a, p, lat in zip(ax, prof, SECTIONS):
        for s, col, mk in (("comcat", "#c9a227", "^"), ("ehb1", "#2166ac", "o"), ("ehb2", "#4393c3", "o"),
                           ("potin", "#a50f15", ".")):
            ok = w[f"{s}_z"].notna() & (w.md >= (3.0 if s == "potin" else 0))
            x = w[ok]
            u, v = project(x[f"{s}_lon"].to_numpy(), x[f"{s}_lat"].to_numpy(), p)
            k = (np.abs(v) <= 50) & (u >= -60) & (u <= 400)
            fx = (x[f"{s}_unk"] == True).to_numpy()  # noqa: E712
            sz = np.clip((x.md.fillna(3).to_numpy() - 2.5), 0.3, 6) ** 2 * 2
            o_ = np.argsort(x.md.fillna(0).to_numpy()[k])
            a.scatter(u[k][o_], x[f"{s}_z"].to_numpy()[k][o_], s=sz[k][o_], marker=mk,
                      facecolor=np.where(fx[k][o_], "none", col), edgecolor=col, lw=0.4, alpha=0.6,
                      label=f"{LNAME[s]} ({k.sum()})")
            big = k & (x.md.to_numpy() >= 7)
            for uu, zz, mm in zip(u[big], x[f"{s}_z"].to_numpy()[big], x.md.to_numpy()[big]):
                if s == "ehb1" or (s == "potin"):
                    a.annotate(f"M{mm:.1f}", (uu, zz), fontsize=8, xytext=(3, 3), textcoords="offset points")
        add_slab(a, p, top, thk)
        a.set_xlim(-60, 400)
        a.set_ylim(250, -5)
        a.set_aspect(0.5)
        a.set_ylabel("depth [km]")
        a.set_title(f"{-lat:.1f}°S, ±50 km", fontsize=11)
        a.legend(loc="lower left", fontsize=8, ncol=4, markerscale=2)
    ax[-1].set_xlabel("distance from the trench [km]")
    fig.suptitle("Do Potin, ISC-EHB and ComCat depths sit on the same slab? Trench-normal sections, hollow = fixed / "
                 "default depth", x=0.01, ha="left")
    io.savefig(fig, "t2_sections", "Trench-perpendicular sections at six latitudes: Potin, ISC-EHB L1/L2 and ComCat "
               "depths against the Slab2 top and bottom (50 km strip either side)")


if __name__ == "__main__":
    run()

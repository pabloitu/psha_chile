"""X3: GCCEL calibrated hypocentres as the location benchmark (task A2b).

GCCEL events are linked to the X1 baseline events with the X1 baseline windows (5 s / 50 km, x1.5 at M 6,
x2 at M 7, x3 at M 8, one-to-one). For every source the epicentre and depth differences against GCCEL are
summarised by depth range, cluster, latitude band, flat slab and period; a depth-error model per source,
the Potin vs ISC-EHB test at depth (X1 finding 6) and the X1 location variants plus L-e are scored.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "X1"))
import x1_io as io  # noqa: E402
import x1_loc as xl  # noqa: E402

CACHE, TAB, FIG = HERE / "cache", HERE / "tables", HERE / "figs"
for d in (CACHE, TAB, FIG):
    d.mkdir(exist_ok=True)

# settings
GCCEL = io.SRC / "gccel_2026-11-11_events.csv"
GMAG = io.SRC / "gccel_2026-11-11_mags.csv"
TW, DW = 5.0, 50.0
SCALE = [(6, 1.5), (7, 2.0), (8, 3.0)]
WIDE_T, WIDE_D = 120.0, 450.0
ZBINS = [(-99, 30, "< 30 km"), (30, 70, "30–70 km"), (70, 120, "70–120 km"), (120, 999, "> 120 km")]
FLAT = (-34.0, -30.0)
SRCS = ["potin", "csn", "csn_isc", "isc", "ehb1", "ehb2", "ehb3", "comcat", "iscgem", "gcmt", "gcmt_c", "centennial"]
NAME = dict(xl.LNAME, gccel="GCCEL")
DEEP = 70.0
CORE = [36.0, 37.0]
GROUPS = ["crustal onshore", "crustal backarc", "interface / slab onshore", "offshore (interface / slab)"]
CNAME = {"illapel": "Illapel", "iquique": "Iquique", "maule": "Maule", "sanjuan": "San Juan", "sanpedro": "San Pedro",
         "serena": "La Serena", "tabuco": "Tabuco", "tirua": "Tirúa", "tocopilla": "Tocopilla", "tome": "Tomé",
         "vallenar": "Vallenar", "valparaiso": "Valparaíso"}
L_E0 = ["potin", "csn", "ehb1", "ehb2", "isc", "comcat", "iscgem", "centennial", "csn_isc", "ehb3", "gcmt"]
L_F_DEPTH = ["ehb1", "potin", "csn", "ehb2", "isc", "comcat", "iscgem", "centennial", "csn_isc", "ehb3", "gcmt"]
L_E_DEEP = ["ehb1", "ehb2", "potin", "csn", "isc", "comcat", "iscgem", "centennial", "csn_isc", "ehb3", "gcmt"]


def stat(x):
    """n, median, robust spread (1.4826 MAD), 90th percentile and mean of |x|."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if not len(x):
        return dict(n=0, med=np.nan, rsd=np.nan, p90=np.nan, mean_abs=np.nan)
    m = np.median(x)
    return dict(n=len(x), med=m, rsd=1.4826 * np.median(np.abs(x - m)), p90=np.percentile(np.abs(x), 90),
                mean_abs=np.abs(x).mean())


def fac(m):
    f = np.ones(len(m))
    m = np.nan_to_num(m, nan=0)
    for thr, x in SCALE:
        f = np.where(m >= thr, x, f)
    return f


def gccel():
    g = pd.read_csv(GCCEL, dtype={"src_id": str})
    m = pd.read_csv(GMAG, dtype={"src_id": str})
    g["t"] = io.tsec_fast(g.time)
    g["m"] = g.src_id.map(m.groupby("src_id").mag.max())
    g["zr"] = io.label(g.depth.to_numpy(), ZBINS)
    g["flat"] = np.where(g.lat.between(*FLAT), "in flat slab (30–34° S)", "outside")
    g["band"] = io.latband(g.lat)
    g["period"] = io.label(io.year(g.t.to_numpy()), io.PERIODS)
    return g


def classes(g):
    """Group of each GCCEL event from its own hypocentre: crustal (more than 15 km above the Slab2 top), split into
    backarc and the rest; otherwise interface / slab, split by an offshore epicentre (no depth used there)."""
    sl, _, _ = io.slab_at(g.lon.to_numpy(), g.lat.to_numpy())
    _, st = io.setting(g.lon.to_numpy(), g.lat.to_numpy())
    crust = np.isnan(sl) | (g.depth.to_numpy() < sl - 15)
    grp = np.where(crust, np.where(st == "backarc", GROUPS[1], GROUPS[0]), np.where(st == "offshore", GROUPS[3], GROUPS[2]))
    return g.assign(slab=sl, setting=st, grp=grp)


def link(g, o, lab):
    """
    One-to-one link of GCCEL events to baseline events.

    An event is a candidate when any of its origins is within the scaled window of the GCCEL hypocentre
    (scale by the larger magnitude of the two); cost = min over its origins of hypot(dt / T, dd / D).

    Returns
    -------
    g with columns ev (baseline event or NaN), why (reason when not linked), dt_best, dd_best
    """
    o = o.sort_values("t")
    ot, ola, olo, om = (o[c].to_numpy() for c in ("t", "lat", "lon", "mmax"))
    oev = lab[o.index.to_numpy()]
    rows, near = [], []
    for i, r in enumerate(g.itertuples()):
        a, b = np.searchsorted(ot, [r.t - WIDE_T, r.t + WIDE_T])
        if a == b:
            near.append((np.nan, np.nan))
            continue
        dt = np.abs(ot[a:b] - r.t)
        dd = io.hav(r.lat, r.lon, ola[a:b], olo[a:b])
        k = dd <= WIDE_D
        near.append((dt[k].min(), dd[k][np.argmin(dt[k])]) if k.any() else (np.nan, np.nan))
        f = fac(np.fmax(np.nan_to_num(om[a:b], nan=0), np.nan_to_num(r.m, nan=0)))
        ok = (dt <= TW * f) & (dd <= DW * f)
        c = np.hypot(dt / (TW * f), dd / (DW * f))
        for e, cc in zip(oev[a:b][ok], c[ok]):
            rows.append((i, e, cc))
    c = pd.DataFrame(rows, columns=["i", "ev", "c"]).groupby(["i", "ev"]).c.min().reset_index()
    ue = np.unique(c.ev)
    big = 1e6
    M = np.full((len(g), len(ue)), big)
    M[c.i, np.searchsorted(ue, c.ev)] = c.c
    ri, ci = linear_sum_assignment(M)
    k = M[ri, ci] < big
    g = g.copy()
    g["ev"] = np.nan
    g.loc[g.index[ri[k]], "ev"] = ue[ci[k]]
    g["dt_best"], g["dd_best"] = np.array(near).T
    has = np.isin(np.arange(len(g)), c.i)
    g["why"] = np.where(g.ev.notna(), "linked",
                        np.where(has, "candidate taken by another GCCEL event",
                                 np.where(np.isfinite(g.dt_best), "nearest origin outside the baseline window",
                                          f"no origin within {WIDE_T:.0f} s / {WIDE_D:.0f} km")))
    return g


def diffs(g, w):
    """Long table: one row per linked GCCEL event and source with dh, dz and the measured-depth flag."""
    x = g[g.ev.notna()]
    v = w.loc[x.ev.astype(int)]
    out = []
    for s in SRCS:
        la, lo, z = v[f"{s}_lat"].to_numpy(), v[f"{s}_lon"].to_numpy(), v[f"{s}_z"].to_numpy()
        k = np.isfinite(la)
        if not k.any():
            continue
        u = (v[f"{s}_unk"].astype(str) == "True").to_numpy()
        out.append(pd.DataFrame({"gid": x.src_id.to_numpy()[k], "src": s,
                                 "dh": io.hav(x.lat.to_numpy()[k], x.lon.to_numpy()[k], la[k], lo[k]),
                                 "dz": z[k] - x.depth.to_numpy()[k], "z": z[k], "meas": ~u[k] & np.isfinite(z[k])}))
    d = pd.concat(out, ignore_index=True)
    keep = ["src_id", "depth", "depth_fixed", "depth_err", "lat_err", "zr", "flat", "band", "period", "cluster", "m",
            "lat", "lon", "slab", "setting", "grp"]
    d = d.merge(x[keep].rename(columns={"src_id": "gid"}), on="gid")
    d.loc[d.depth_fixed.astype(bool), "dz"] = np.nan
    return d


def summary(d):
    rows = []
    for by in ("all", "zr", "grp", "cluster", "band", "flat", "period"):
        for (s, gv), y in d.assign(all="all").groupby(["src", by]):
            h, z = stat(y.dh), stat(y.dz[y.meas])
            rows.append({"src": NAME[s], "by": by, "group": gv, "n": len(y), "n_z_measured": z["n"],
                         "dh_med": h["med"], "dh_rsd": h["rsd"], "dh_p90": h["p90"],
                         "dz_med": z["med"], "dz_rsd": z["rsd"], "dz_p90": z["p90"],
                         "dz_all_med": stat(y.dz)["med"], "share_unmeasured": 1 - y.meas.mean()})
    return pd.DataFrame(rows)


def error_model(d, g):
    """Per source and depth range: bias and spread of dz (measured depths), net σ after GCCEL's own σ."""
    sg_z = np.nanmedian(g.depth_err)
    sg_h = np.nanmedian(g.lat_err) / 2.15
    rows = []
    zr = np.where(d.depth >= DEEP, "≥ 70 km", d.zr)
    for (s, b), y in d.groupby(["src", zr]):
        z, h = stat(y.dz[y.meas]), stat(y.dh)
        rows.append({"src": NAME[s], "depth": b, "n_z": z["n"], "bias_z": z["med"], "rsd_z": z["rsd"],
                     "sigma_z_net": np.sqrt(max(z["rsd"] ** 2 - sg_z ** 2, 0)) if z["n"] else np.nan,
                     "p90_z": z["p90"], "n_h": h["n"], "med_h": h["med"], "p90_h": h["p90"],
                     "sigma_h": h["med"] / 1.1774 if h["n"] else np.nan, "share_unmeasured": 1 - y.meas.mean()})
    return pd.DataFrame(rows), sg_z, sg_h


def paired(d):
    """Pairs of sources on the same GCCEL events (both depths measured): mean |dz|, mean dh, share a closer."""
    rows = []
    pairs = [("potin", "ehb1"), ("potin", "ehb2"), ("potin", "isc"), ("potin", "comcat"), ("potin", "csn_isc"),
             ("ehb1", "isc"), ("ehb1", "comcat")]
    for a, b in pairs:
        p = d[(d.src == a) & d.meas].set_index("gid")
        q = d[(d.src == b) & d.meas].set_index("gid")
        j = p.index.intersection(q.index)
        x = p.loc[j].assign(dz_b=q.loc[j, "dz"], dh_b=q.loc[j, "dh"], all="all")
        for by in ("all", "zr", "grp", "flat", "cluster"):
            if by == "grp":
                y = x.assign(grp=x.grp + ", " + x.zr)
                for gv, yy in y.groupby("grp"):
                    rows.append({"a": NAME[a], "b": NAME[b], "by": "grp, depth", "group": gv, "n": len(yy),
                                 "mean_abs_dz_a": yy.dz.abs().mean(), "mean_abs_dz_b": yy.dz_b.abs().mean(),
                                 "a_closer_z": (yy.dz.abs() < yy.dz_b.abs()).mean(), "mean_dh_a": yy.dh.mean(),
                                 "mean_dh_b": yy.dh_b.mean(), "a_closer_h": (yy.dh < yy.dh_b).mean()})
            for gv, y in x.groupby(by):
                rows.append({"a": NAME[a], "b": NAME[b], "by": by, "group": gv, "n": len(y),
                             "mean_abs_dz_a": y.dz.abs().mean(), "mean_abs_dz_b": y.dz_b.abs().mean(),
                             "a_closer_z": (y.dz.abs() < y.dz_b.abs()).mean(), "mean_dh_a": y.dh.mean(),
                             "mean_dh_b": y.dh_b.mean(), "a_closer_h": (y.dh < y.dh_b).mean()})
    return pd.DataFrame(rows)


def slab_check(d):
    """Depth minus the Slab2 top for GCCEL and other sources on shared offshore and coastal events (selected by
    epicentre only, so GCCEL's depth does not choose the events)."""
    rows = []
    for st in ("offshore", "coast"):
        y = d[d.setting == st]
        for ss in (["potin", "isc"], ["potin", "ehb1", "isc", "comcat"]):
            ids = set.intersection(*[set(y[(y.src == s) & y.meas].gid) for s in ss])
            q = y[(y.src == ss[0]) & y.gid.isin(ids)]
            rows.append({"setting": st, "set": "+".join(ss), "src": "GCCEL", "n": len(q),
                         **{k: v for k, v in stat(q.depth - q.slab).items() if k in ("med", "rsd")}})
            for s in ss:
                q = y[(y.src == s) & y.gid.isin(ids)]
                rows.append({"setting": st, "set": "+".join(ss), "src": NAME[s], "n": len(q),
                             **{k: v for k, v in stat(q.z - q.slab).items() if k in ("med", "rsd")}})
    return pd.DataFrame(rows)


def shifts(g, w):
    """Median north and east offset (km, source − GCCEL) per cluster and source."""
    x = g[g.ev.notna()]
    v = w.loc[x.ev.astype(int)]
    rows = []
    for s in SRCS:
        dn = (v[f"{s}_lat"].to_numpy() - x.lat.to_numpy()) * io.KM
        de = (v[f"{s}_lon"].to_numpy() - x.lon.to_numpy()) * io.KM * np.cos(np.radians(x.lat.to_numpy()))
        for cl in sorted(x.cluster.unique()):
            k = (x.cluster == cl).to_numpy() & np.isfinite(dn)
            if k.sum() >= 3:
                rows.append({"src": NAME[s], "cluster": cl, "n": int(k.sum()), "dn_med": np.median(dn[k]),
                             "de_med": np.median(de[k])})
    return pd.DataFrame(rows)


def deep_test(d, zmin):
    """Potin vs ISC-EHB L1 / L2: which is closer to GCCEL depth, events with both measured, GCCEL z ≥ zmin."""
    p = d[(d.src == "potin") & d.meas & (d.depth >= zmin)].set_index("gid")
    rows = []
    for e in ("ehb1", "ehb2"):
        q = d[(d.src == e) & d.meas & (d.depth >= zmin)].set_index("gid")
        j = p.index.intersection(q.index)
        for gid in j:
            rows.append({"gid": gid, "ehb": e, "depth": p.at[gid, "depth"], "flat": p.at[gid, "flat"],
                         "cluster": p.at[gid, "cluster"], "dz_potin": p.at[gid, "dz"], "dz_ehb": q.at[gid, "dz"]})
    t = pd.DataFrame(rows, columns=["gid", "ehb", "depth", "flat", "cluster", "dz_potin", "dz_ehb"])
    t["closer"] = np.where(t.dz_potin.abs() < t.dz_ehb.abs(), "Potin", "ISC-EHB")
    return t


def variants(w, x):
    """X1 variants L-a … L-d from the X1 cache, the two orders of L-e and L-f (epicentre as L-e0, depth from
    EHB L1 first); GCCEL is left out of every order, it is the reference."""
    v = {}
    for ch in pd.read_csv(io.CACHE / "locvariants.csv.gz", usecols=["ev", "lat", "lon", "z", "unk", "match", "loc"],
                          chunksize=1_000_000):
        ch = ch[(ch.match == "baseline") & ch.ev.isin(x.ev)]
        for k, y in ch.groupby("loc"):
            v.setdefault(k, []).append(y)
    v = {k: pd.concat(y).set_index("ev") for k, y in v.items() if k in ("L-a", "L-b 44°S", "L-c", "L-d")}
    ww = w.loc[x.ev.astype(int)]
    e0 = xl.choose(ww, None, L_E0)
    dp = xl.choose(ww, None, L_E_DEEP)
    deep = (e0.z >= DEEP) & ~e0.unk
    e = e0.copy()
    e[deep] = dp[deep]
    v["L-e0 (DECISIONS order)"] = e0
    v["L-e (EHB below 70 km)"] = e
    f = xl.choose(ww, None, L_F_DEPTH)
    v["L-f (depth EHB L1 first)"] = e0.assign(z=f.z, unk=f.unk)
    la, lo = ww.potin_lat.fillna(ww.csn_lat).to_numpy(), ww.potin_lon.fillna(ww.csn_lon).to_numpy()
    _, st = io.setting(np.nan_to_num(lo, nan=-70), np.nan_to_num(la, nan=-30))
    for c in CORE:
        ok = (la <= -18) & (la >= -c) & (st != "backarc")
        v[f"L-g (Potin only 18–{c:.0f}° S, not backarc)"] = xl.choose(ww, None, L_E0, potin_ok=ok)
    return v, int(deep.sum())


def scores(v, x, by="zr"):
    rows = []
    gx = x.set_index(x.ev.astype(int))
    for k, c in v.items():
        c = c.reindex(gx.index)
        dh = io.hav(gx.lat, gx.lon, c.lat, c.lon)
        ok = ~c.unk.astype(bool) & ~gx.depth_fixed.astype(bool)
        dz = (c.z - gx.depth)[ok]
        for zr in ["all"] + ([b[2] for b in ZBINS] if by == "zr" else GROUPS):
            s = (gx[by] == zr) if zr != "all" else np.ones(len(gx), bool)
            rows.append({"variant": k, "depth": zr, "n": int(np.isfinite(dh[s]).sum()),
                         "mean_dh": np.nanmean(dh[s]) if s.any() else np.nan,
                         "median_dh": np.nanmedian(dh[s]) if s.any() else np.nan,
                         "n_z": int(np.isfinite(dz[s[ok]]).sum()) if s.any() else 0,
                         "mean_abs_dz": np.nanmean(np.abs(dz[s[ok]])) if s[ok].any() else np.nan,
                         "median_abs_dz": np.nanmedian(np.abs(dz[s[ok]])) if s[ok].any() else np.nan,
                         "unknown_depth": int((~ok & s & ~gx.depth_fixed.astype(bool)).sum())})
    return pd.DataFrame(rows)


# figures
def fig_map(plt, g):
    import cartopy.crs as ccrs
    import cartopy.feature as cf
    fig = plt.figure(figsize=(9.5, 10))
    a = fig.add_subplot(1, 2, 1, projection=ccrs.PlateCarree())
    a.set_extent([-76, -64, -40, -17], ccrs.PlateCarree())
    a.add_feature(cf.LAND.with_scale("50m"), color="0.93")
    a.add_feature(cf.COASTLINE.with_scale("50m"), lw=0.4, ec="0.4")
    a.add_feature(cf.BORDERS.with_scale("50m"), lw=0.3, ec="0.6")
    s = g.sort_values("depth")
    sc = a.scatter(s.lon, s.lat, c=s.depth, s=6 + 3 * np.nan_to_num(s.m - 3, nan=0).clip(0) ** 2, cmap="viridis_r",
                   vmin=0, vmax=100, lw=0.2, ec="0.3", transform=ccrs.PlateCarree(), zorder=3)
    for cl, y in g.groupby("cluster"):
        a.text(y.lon.max() + 0.4, y.lat.median(), CNAME.get(cl.split(".")[0].rstrip("0123456789"), cl), fontsize=9,
               va="center", transform=ccrs.PlateCarree())
    a.axhspan(*FLAT, color="#c9a227", alpha=0.12, zorder=1)
    gl = a.gridlines(draw_labels=True, lw=0.2, color="0.7")
    gl.top_labels = gl.right_labels = False
    fig.colorbar(sc, ax=a, shrink=0.5, label="GCCEL depth (km)")
    a.set_title(f"GCCEL in the box: {len(g)} events, {g.cluster.nunique()} clusters")
    b = fig.add_subplot(1, 2, 2)
    b.scatter(g.lat, g.depth, c=g.depth, cmap="viridis_r", vmin=0, vmax=100, s=8, lw=0)
    b.axvspan(*FLAT, color="#c9a227", alpha=0.12)
    for z in (30, 70):
        b.axhline(z, color="0.6", lw=0.6, ls="--")
    b.invert_yaxis()
    b.invert_xaxis()
    b.set_xlabel("latitude (°)")
    b.set_ylabel("depth (km)")
    b.set_title("depth along the margin (flat slab shaded)")
    fig.tight_layout()
    fig.savefig(FIG / "x3_gccel_map.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_box(plt, d):
    import palette
    show = [s for s in SRCS if (d.src == s).sum() >= 5]
    zr = [b[2] for b in ZBINS if (d.zr == b[2]).any()]
    fig, ax = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    wd = 0.8 / len(zr)
    for j, b in enumerate(zr):
        col = palette.SERIES[j]
        for k, (v, a) in enumerate((("dh", ax[0]), ("dz", ax[1]))):
            data = [d[(d.src == s) & (d.zr == b) & (d.meas if v == "dz" else True)][v].dropna() for s in show]
            pos = np.arange(len(show)) + (j - (len(zr) - 1) / 2) * wd
            ok = [i for i, x in enumerate(data) if len(x) >= 3]
            bp = a.boxplot([data[i] for i in ok], positions=pos[ok], widths=wd * 0.85, patch_artist=True,
                           showfliers=False, whis=(5, 95), medianprops=dict(color="white", lw=1.4))
            for p in bp["boxes"]:
                p.set(facecolor=col, edgecolor=col)
            for p in bp["whiskers"] + bp["caps"]:
                p.set(color=col)
            if k == 0:
                a.plot([], [], color=col, lw=6, label=f"GCCEL depth {b}")
    ax[0].set_ylabel("epicentre distance to GCCEL (km)")
    ax[0].set_ylim(0, 60)
    ax[1].axhline(0, color="0.5", lw=0.6)
    ax[1].set_ylabel("depth − GCCEL depth (km)\n(measured depths only)")
    ax[1].set_ylim(-45, 45)
    ax[1].set_xticks(range(len(show)), [NAME[s] for s in show], rotation=30, ha="right")
    ax[0].legend(ncol=3, loc="upper left")
    ax[0].set_title("Differences against GCCEL by depth range (box 25–75 %, whiskers 5–95 %)")
    fig.tight_layout()
    fig.savefig(FIG / "x3_diff_by_depth.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_deep(plt, d):
    import palette
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    for a, fl in zip(ax, ["in flat slab (30–34° S)", "outside"]):
        for k, (s, mk) in enumerate((("potin", "o"), ("ehb1", "s"), ("ehb2", "D"))):
            y = d[(d.src == s) & d.meas & (d.flat == fl) & (d.depth >= 40)]
            a.scatter(y.depth, y.dz, s=18, marker=mk, color=palette.SERIES[k], alpha=0.8, lw=0,
                      label=f"{NAME[s]} ({len(y)})")
        a.axhline(0, color="0.5", lw=0.6)
        a.axvline(DEEP, color="0.6", lw=0.6, ls="--")
        a.set_xlabel("GCCEL depth (km)")
        a.set_title(fl)
        a.legend(loc="upper left")
    ax[0].set_ylabel("depth − GCCEL depth (km)")
    fig.suptitle("Potin and ISC-EHB depths against GCCEL, GCCEL depth ≥ 40 km", x=0.06, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / "x3_potin_ehb_depth.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_scores(plt, sc):
    import palette
    s = sc[sc.depth.isin(["all", "< 30 km", "30–70 km", "70–120 km"])]
    vs = list(dict.fromkeys(s.variant))
    zs = list(dict.fromkeys(s.depth))
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    wd = 0.8 / len(zs)
    for j, z in enumerate(zs):
        y = s[s.depth == z].set_index("variant").reindex(vs)
        x = np.arange(len(vs)) + (j - (len(zs) - 1) / 2) * wd
        n = int(y.n.iloc[0])
        ax[0].bar(x, y.mean_dh, wd, color=palette.SERIES[j], label=f"{z} ({n} events)")
        ax[1].bar(x, y.mean_abs_dz, wd, color=palette.SERIES[j], label=z)
    for a, t in zip(ax, ("mean epicentre distance to GCCEL (km)", "mean |depth − GCCEL depth| (km)")):
        a.set_xticks(range(len(vs)), vs, rotation=25, ha="right")
        a.set_ylabel(t)
    fig.legend(*ax[0].get_legend_handles_labels(), title="GCCEL depth", loc="lower center", ncol=4,
               bbox_to_anchor=(0.5, -0.12))
    ax[0].set_title("Location variants scored against GCCEL (GCCEL itself left out)")
    fig.tight_layout()
    fig.savefig(FIG / "x3_variant_scores.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def run():
    g = gccel()
    f = CACHE / "gccel_linked.csv"
    if f.exists():
        g = pd.read_csv(f, dtype={"src_id": str})
    else:
        o = io.load("origins", dtype={"sid": str})
        lab = io.load("labels").baseline.to_numpy()
        g = link(g, o, lab)
        g.to_csv(f, index=False)
    w = pd.read_csv(io.CACHE / "loc_wide_baseline.csv.gz", index_col="ev", low_memory=False)
    g = classes(g)
    lk = g.why.value_counts().rename_axis("why").reset_index(name="n")
    lk.to_csv(TAB / "x3_link_counts.csv", index=False)
    by = g.groupby(["cluster", "why"]).size().unstack(fill_value=0)
    by.to_csv(TAB / "x3_link_by_cluster.csv")
    g[g.why != "linked"][["src_id", "time", "lat", "lon", "depth", "m", "cluster", "why", "dt_best", "dd_best"]] \
        .to_csv(TAB / "x3_unlinked.csv", index=False)
    print(lk.to_string(index=False))
    d = diffs(g, w)
    d.to_csv(CACHE / "x3_diffs.csv.gz", index=False)
    sm = summary(d)
    sm.to_csv(TAB / "x3_diff_summary.csv", index=False)
    em, sgz, sgh = error_model(d, g)
    em.to_csv(TAB / "x3_depth_error_model.csv", index=False)
    print(f"GCCEL median depth error {sgz:.1f} km, epicentre σ ≈ {sgh:.1f} km")
    paired(d).to_csv(TAB / "x3_paired.csv", index=False)
    shifts(g, w).to_csv(TAB / "x3_cluster_shifts.csv", index=False)
    slab_check(d).to_csv(TAB / "x3_slab_check.csv", index=False)
    dt = pd.concat([deep_test(d, z).assign(zmin=z) for z in (50.0, DEEP)])
    dt.to_csv(TAB / "x3_potin_vs_ehb_deep.csv", index=False)
    x = g[g.ev.notna()]
    v, nd = variants(w, x)
    sc = scores(v, x)
    sc.to_csv(TAB / "x3_variant_scores.csv", index=False)
    scores(v, x, "grp").rename(columns={"depth": "group"}).to_csv(TAB / "x3_variant_scores_by_group.csv", index=False)
    print(f"L-e: {nd} linked events switched to EHB first (base depth ≥ {DEEP:.0f} km)")
    plt = io.fig_setup()
    fig_map(plt, g)
    fig_box(plt, d)
    fig_deep(plt, d)
    fig_scores(plt, sc)
    return g, d, sm, em, dt, sc


if __name__ == "__main__":
    run()

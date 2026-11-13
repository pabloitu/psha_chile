"""Checks and figures of the A4 locations (task brief A4, checks 1 to 5).

Reads the outputs of locate.py and writes merged/loc_checks_<date>.csv, merged/loc_gccel_<date>.csv,
merged/loc_sources_<date>.csv and the figures in figs/locate/.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import locate as G
from match import OUT, hav

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import palette  # noqa: E402

# settings
RUN = G.RUN
FIG = HERE / "figs" / "locate"
SLAB = G.REPO / "data" / "slab_2.0"
TRENCH = G.REPO / "data" / "shapefiles" / "sam_nazca_trench.shp"
PER = [(0, 1964, "before 1964"), (1964, 1982, "1964–1981"), (1982, 2000, "1982–1999"), (2000, 2011, "2000–2010"), (2011, 2100, "2011–today")]
MMIN = 4.5
SECTIONS = [-20.0, -23.0, -27.0, -31.0, -33.5, -37.0]
STRIP, XLIM, ZMAX, LAND_CAP = 50.0, (-60.0, 400.0), 250.0, 400.0
FAR_T, FAR_D = 30.0, 100.0
GROUPS = ["crustal onshore", "crustal backarc", "interface / slab onshore", "offshore"]
NAME = {"potin": "Potin et al.", "csn": "CSN web", "gccel": "GCCEL", "ehb1": "ISC-EHB L1", "ehb2": "ISC-EHB L2", "ehb3": "ISC-EHB L3",
        "isc": "ISC Bulletin", "comcat": "ComCat", "csn_isc": "CSN in ISC", "iscgem": "ISC-GEM", "cent_ehb": "Centennial (EHB)",
        "centennial": "Centennial", "gcmt": "GCMT hypocentre", "cabello": "Cabello et al."}
COL = dict(zip(NAME, palette.SERIES + ["#555555", "#bbbbbb"]))


def slab_top(lon, lat):
    from scipy.interpolate import RegularGridInterpolator
    a = pd.read_csv(SLAB / "sam_slab2_dep_02.23.18.xyz", header=None, names=["x", "y", "z"])
    z = a.pivot(index="y", columns="x", values="z")
    f = RegularGridInterpolator((z.index.to_numpy(), z.columns.to_numpy()), z.to_numpy(), bounds_error=False)
    return -f(np.c_[lat, np.mod(lon, 360)])


def new(nr, nc, w, h, **kw):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    palette.apply()
    return plt.subplots(nr, nc, figsize=(w, h), layout="constrained", squeeze=False, **kw)


def save(fig, name, dpi=200):
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=dpi)
    plt.close(fig)


# check 1
def depth_shares(c):
    """Share of unknown depths and events saved from a fixed or default depth by a later source, by period,
    2 degree band, network and magnitude set."""
    unk = (c.depth_kind == "unknown").to_numpy()
    nofirst = c.loc_flags.fillna("").str.contains("loc_src_depth_not_measured").to_numpy()
    saved = nofirst & ~unk
    sets = {"all events": np.ones(len(c), bool), f"native M ≥ {MMIN}": (c.mmax >= MMIN).to_numpy()}
    if "mw" in c:
        sets[f"final Mw ≥ {MMIN}"] = (c.mw >= MMIN - 0.05).to_numpy()
    band = np.floor(c.lat / 2) * 2
    by = {"period": pd.Series(np.select([(c.yr >= a) & (c.yr < b) for a, b, _ in PER], [p for _, _, p in PER], None), index=c.index),
          "band": pd.Series([f"{-b - 2:.0f}–{-b:.0f}° S" if np.isfinite(b) else None for b in band], index=c.index),
          "network": pd.Series(np.where(c.inside_network, "inside the network", "outside the network"), index=c.index),
          "all": pd.Series("all", index=c.index)}
    rows = []
    for sn, k in sets.items():
        for bn, g in by.items():
            for v in pd.unique(g[k].dropna()):
                m = k & (g == v).to_numpy()
                rows.append({"check": 1, "set": sn, "by": bn, "group": v, "n": int(m.sum()), "unknown": int((m & unk).sum()),
                             "unknown_share": round(float(unk[m].mean()), 4), "loc_src_depth_not_measured": int((m & nofirst).sum()),
                             "saved_by_a_later_source": int((m & saved).sum())})
    return pd.DataFrame(rows)


def fig_depths(t):
    fig, ax = new(1, 2, 15, 5)
    sets = list(dict.fromkeys(t["set"]))
    for a, bn in zip(ax[0], ("period", "band")):
        x = t[t.by == bn]
        grp = [p for _, _, p in PER] if bn == "period" else sorted(x.group.unique(), key=lambda s: float(s.split("–")[0]))
        for i, sn in enumerate(sets):
            y = x[x["set"] == sn].set_index("group").reindex(grp)
            a.bar(np.arange(len(grp)) + (i - 1) * 0.27, 100 * y.unknown_share, 0.25, color=palette.SERIES[i], label=sn)
            a.bar(np.arange(len(grp)) + (i - 1) * 0.27, 100 * y.saved_by_a_later_source / y.n, 0.25, bottom=100 * y.unknown_share,
                  color=palette.SERIES[i], alpha=0.3)
        a.set_xticks(range(len(grp)), grp, rotation=0 if bn == "period" else 60, fontsize=9)
        a.set_ylabel("events [%]")
        a.set_title("Depth unknown (solid) and saved by a later source (light), by " + ("period" if bn == "period" else "latitude"))
    ax[0, 0].legend()
    save(fig, "depth_unknown")


# check 2
def gccel_scores(D):
    """Mean epicentre distance and |Δz| to GCCEL of the A4 rule and of 'Potin first everywhere', both without
    GCCEL in the order, by group of the GCCEL hypocentre."""
    e, R, W = D["e"], D["R"], D["W"]
    g = R[R.key == "gccel"].set_index("event_id")
    k = e.event_id.isin(g.index).to_numpy()
    es, W2 = e[k].reset_index(drop=True), W[k].drop(columns=[c for c in W.columns if c[1] == "gccel"])
    g = g.reindex(es.event_id)
    sl = slab_top(g.lon.to_numpy(), g.lat.to_numpy())
    crust = np.isnan(sl) | (g.z.to_numpy() < sl - 15)
    grp = np.where(crust, np.where(G.backarc(g.lon, g.lat), GROUPS[1], GROUPS[0]), np.where(G.offshore(g.lon, g.lat), GROUPS[3], GROUPS[2]))
    var = {"this rule": G.locate(es, W2, G.inside_network(es, W2), G.offshore), "Potin first everywhere": G.locate(es, W2, np.ones(len(es), bool))}
    rows = []
    for nm, x in var.items():
        dh = hav(x.lat.to_numpy(), x.lon.to_numpy(), g.lat.to_numpy(), g.lon.to_numpy())
        dz = np.abs(x.depth.to_numpy() - g.z.to_numpy())
        okz = np.isfinite(dz) & ~g.fixed.to_numpy()
        for q in ["all"] + GROUPS:
            m = np.isfinite(dh) & ((grp == q) | (q == "all"))
            rows.append({"check": 2, "rule": nm, "group": q, "n": int(m.sum()), "mean_epicentre_km": round(float(dh[m].mean()), 2),
                         "median_epicentre_km": round(float(np.median(dh[m])), 2), "n_depth": int((m & okz).sum()),
                         "mean_abs_dz_km": round(float(dz[m & okz].mean()), 2), "median_abs_dz_km": round(float(np.median(dz[m & okz])), 2),
                         "local_first": int((m & x.loc_key.isin(G.LOCAL).to_numpy()).sum())})
    return pd.DataFrame(rows)


def fig_gccel(t):
    fig, ax = new(1, 2, 13, 4.8)
    grp = ["all"] + GROUPS
    for a, (v, lab) in zip(ax[0], (("mean_epicentre_km", "mean epicentre distance to GCCEL [km]"), ("mean_abs_dz_km", "mean |depth difference| to GCCEL [km]"))):
        for i, nm in enumerate(dict.fromkeys(t.rule)):
            x = t[t.rule == nm].set_index("group").reindex(grp)
            a.bar(np.arange(len(grp)) + (i - 0.5) * 0.38, x[v], 0.36, color=palette.SERIES[i], label=nm)
        n = t[t.rule == "this rule"].set_index("group").reindex(grp).n
        a.set_xticks(range(len(grp)), [f"{q}\n({k})" for q, k in zip(grp, n)], fontsize=9)
        a.set_ylabel(lab)
    ax[0, 0].legend()
    ax[0, 0].set_title("Against the calibrated locations of GCCEL (GCCEL itself left out of both orders)")
    save(fig, "gccel")


# check 3
def sources(c, big):
    per = pd.Series(np.select([(c.yr >= a) & (c.yr < b) for a, b, _ in PER], [p for _, _, p in PER], None), index=c.index)
    rows = []
    for sn, k in (("all events", np.ones(len(c), bool)), (f"M ≥ {MMIN}", big)):
        for prop in ("loc_src", "depth_src"):
            t = pd.crosstab(c[prop][k].fillna("unknown"), per[k]).reindex(columns=[p for _, _, p in PER], fill_value=0)
            t["total"] = t.sum(axis=1)
            rows.append(t.reset_index().rename(columns={prop: "source"}).assign(check=3, set=sn, property=prop))
    return pd.concat(rows, ignore_index=True)


def fig_map(c, big):
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    from pituplots.maps import dress_map
    palette.apply()
    x = c[big & c.lat.notna()]
    keys = [k for k in NAME if (x.loc_src == k).any()]
    fig = plt.figure(figsize=(15, 11), layout="constrained")
    for j, (lab, m) in enumerate((("Inside the network", x.inside_network), ("Outside the network, and before 1982", ~x.inside_network))):
        ax = fig.add_subplot(1, 2, j + 1, projection=ccrs.PlateCarree())
        dress_map(ax, [-80, -62, -58, -15], coastline=True, gridlines=True)
        for k in keys:
            y = x[m & (x.loc_src == k)]
            if len(y):
                ax.scatter(y.lon, y.lat, s=5, color=COL[k], lw=0, alpha=0.7, transform=ccrs.PlateCarree(), label=f"{NAME[k]} ({len(y):,})",
                           rasterized=True)
        ax.set_title(f"{lab} ({int(m.sum()):,})")
        ax.legend(loc="lower right", markerscale=3, fontsize=9)
    fig.suptitle(f"Source of the epicentre, M ≥ {MMIN}", x=0.01, ha="left")
    save(fig, "who_decides", dpi=160)


# check 4
def fig_sections(c, big):
    import cartopy.io.shapereader as shp
    import shapely
    import shapely.ops
    from pituplots.io import read_slab2
    from pituplots.sections import add_slab, profiles_from_line, project
    line = shapely.union_all(list(shp.Reader(str(TRENCH)).geometries()))
    line = shapely.ops.linemerge(line) if line.geom_type != "LineString" else line
    line = max(line.geoms, key=lambda q: q.length) if line.geom_type != "LineString" else line
    top, thk = read_slab2(SLAB / "sam_slab2_dep_02.23.18.xyz"), read_slab2(SLAB / "sam_slab2_thk_02.23.18.xyz")
    prof = profiles_from_line(line, SECTIONS, width=2 * STRIP, side=(-60, -30), length=XLIM)
    x = c[big & c.lat.notna()]
    m = x.mw.fillna(x.mmax).to_numpy() if "mw" in x else x.mmax.to_numpy()
    fig, ax = new(len(SECTIONS), 1, 12, 6.9 * len(SECTIONS))
    for a, p, lat in zip(ax[:, 0], prof, SECTIONS):
        u, v = project(x.lon.to_numpy(), x.lat.to_numpy(), p)
        k = (np.abs(v) <= STRIP) & (u >= XLIM[0]) & (u <= min(XLIM[1], LAND_CAP))
        unk = (x.depth_kind == "unknown").to_numpy()
        for key in [q for q in NAME if (x.depth_src[k] == q).any()]:
            s = k & (x.depth_src == key).to_numpy()
            o = np.argsort(m[s])
            a.scatter(u[s][o], x.depth.to_numpy()[s][o], s=np.clip(m[s][o] - 3.5, 0.5, 6) ** 2 * 4, color=COL[key], alpha=0.75, lw=0.3,
                      edgecolor="white", label=f"{NAME[key]} ({s.sum()})", zorder=3)
        a.scatter(u[k & unk], np.full((k & unk).sum(), -8.0), s=14, marker="v", color="0.5", lw=0, label=f"depth unknown ({(k & unk).sum()})",
                  clip_on=False, zorder=3)
        for i in np.flatnonzero(k & ~unk & (m >= 7)):
            a.annotate(f"M {m[i]:.1f}", (u[i], x.depth.to_numpy()[i]), fontsize=9, xytext=(4, 4), textcoords="offset points", zorder=5)
        add_slab(a, p, top, thk)
        a.set_xlim(*XLIM)
        a.set_ylim(ZMAX, -12)
        a.set_aspect(1)
        a.set_ylabel("depth [km]")
        a.set_title(f"{-lat:.1f}° S, {STRIP:.0f} km either side, M ≥ {MMIN}")
        a.legend(loc="lower left", ncol=3, fontsize=9)
    ax[-1, 0].set_xlabel("distance from the trench [km]")
    save(fig, "sections", dpi=130)


# check 5
def distant(c):
    """The A3 list of events with a member more than FAR_T s or FAR_D km from the reference member, and the
    source that now locates them."""
    L = pd.read_csv(OUT / f"links_{G.A3}.csv", usecols=["event_id", "src", "dt", "dd", "used"], low_memory=False)
    far = L[L.used.astype(str).eq("True") & ((L.dt.abs() > FAR_T) | (L.dd > FAR_D))].event_id.unique()
    e = pd.read_csv(OUT / f"events_{G.A3}.csv", usecols=["event_id", "ref_src"], low_memory=False)
    x = c[c.event_id.isin(far)].merge(e, on="event_id")
    x["now"] = np.where(x.loc_src.isin(G.LOCAL), "local catalogue", "global source")
    t = pd.crosstab(x.ref_src, x.now).reset_index()
    return t.assign(check=5), x


def main():
    e, R, allo = G.records()
    dflt = pd.read_csv(OUT / f"defaults_{RUN}.csv")
    W, R = G.wide(e, R, dflt)
    f = OUT / f"catalog_{RUN}.csv"
    c = pd.read_csv(f if f.exists() else OUT / f"locations_{RUN}.csv", low_memory=False)
    if "loc_flags" not in c:
        c = c.rename(columns={"flags": "loc_flags"})
    c = c.merge(e[["event_id", "yr", "mmax"]], on="event_id")
    big = ((c.mw >= MMIN - 0.05) if "mw" in c else (c.mmax >= MMIN)).to_numpy()
    t1 = depth_shares(c)
    t2 = gccel_scores({"e": e, "R": R, "W": W})
    t3 = sources(c, big)
    t5, far = distant(c)
    files = {OUT / f"loc_checks_{RUN}.csv": pd.concat([t1, t5], ignore_index=True), OUT / f"loc_gccel_{RUN}.csv": t2,
             OUT / f"loc_sources_{RUN}.csv": t3, OUT / "review" / f"distant_events_{RUN}.csv": far.drop(columns=["yr"])}
    for p, d in files.items():
        d.to_csv(p, index=False)
    G.manifest(files)
    fig_depths(t1)
    fig_gccel(t2)
    fig_map(c, big)
    fig_sections(c, big)
    pd.set_option("display.width", 250, "display.max_rows", 200, "display.max_columns", 30)
    print(t1[t1.by.isin(["all", "period", "network"])].to_string())
    print(t2.to_string())
    print(t3[(t3["set"] != "all events")].to_string())
    print(t5.to_string(), len(far))
    s = c[(c.lat.between(-32, -30)) & (c.depth_src == "potin") & c.depth.between(100, 170) & big]
    top = slab_top(s.lon.to_numpy(), s.lat.to_numpy())
    print("Potin depths at 30–32° S, 100–170 km, M >=", MMIN, ":", len(s), "| more than 20 km below the Slab2 top:", int((s.depth.to_numpy() - top > 20).sum()))


if __name__ == "__main__":
    main()

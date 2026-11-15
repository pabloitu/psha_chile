"""B9 addition: completeness of the whole catalogue, not per class. Mc per period by region and depth, and on a map,
with the events from Mw 3.5 of the frozen file so that the roll-off is in view. A check only: no fit uses the small
events. Writes tables/mc_all_regions.csv, cache/mc_all_grid_*.csv and figs/mc_all_map_*.png."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import b9_lib as L

MLOW = 3.5
WINDOWS = [(1964, 1976), (1976, 1990), (1990, 2000), (2000, 2007), (2007, 2012), (2012, 2020), (2020, 2027)]
DEEP = 70.0
NMIN = 100
# map
# step in degrees, radius in km, file tag; the coarse grid is the one to read
GRIDS = [(1.0, 250.0, "1deg"), (0.5, 150.0, "05deg")]
NNODE = 150
MAPS = [(1976, 2000), (2000, 2012), (2012, 2027)]
KS = dict(nsim=100, ncap=1000, nmin=50)
FORCE = False


def load():
    f = L.CACHE / "m35.pkl"
    if f.exists():
        return pd.read_pickle(f)
    d = pd.read_csv(L.CAT, usecols=["event_id", "time", "lon", "lat", "depth", "mw", "in_domain"], low_memory=False)
    d = d[(d.mw >= MLOW - 1e-9) & d.in_domain].copy()
    d["t"] = d.time.str[:4].astype(int) + 0.5
    d.to_pickle(f)
    return d


def mc(m, **kw):
    w = np.ones(m.size)
    r = dict(n=m.size, n45=int((m >= 4.45).sum()), n50=int((m >= 4.95).sum()))
    if m.size >= NMIN:
        r.update(bstab=L.mc_bstab(m, w), ks=L.mc_ks(m, w, rng=np.random.default_rng(5), **kw))
    return r


def regions(d):
    m, t, lat, z = (d[c].to_numpy() for c in ("mw", "t", "lat", "depth"))
    sets = {"all": np.ones(len(d), bool), "shallower than 70 km": z < DEEP, "70 km and deeper": z >= DEEP}
    rows = []
    for rg, (la0, la1) in {"whole margin": (-90, 0), **L.REG}.items():
        for dn, dk in sets.items():
            for a, b in WINDOWS:
                s = (t >= a) & (t < b) & (lat >= la0) & (lat < la1) & dk
                rows.append(dict(region=rg, depth=dn, start=a, end=b, **mc(m[s])))
        print(rg, flush=True)
    x = pd.DataFrame(rows)
    x.to_csv(L.TAB / "mc_all_regions.csv", index=False)
    return x


def grid(d, STEP, RADIUS, tag):
    m, t, lon, lat = (d[c].to_numpy() for c in ("mw", "t", "lon", "lat"))
    rows = []
    for a, b in MAPS:
        s = np.where((t >= a) & (t < b))[0]
        for la in np.arange(-56, -16.9, STEP):
            band = s[np.abs(lat[s] - la) < RADIUS / 100]
            for lo in np.arange(-77, -64.4, STEP):
                near = band[L.km(lo, la, lon[band], lat[band]) <= RADIUS]
                r = dict(start=a, end=b, lon=lo, lat=la, n=near.size)
                if near.size >= NNODE:
                    w = np.ones(near.size)
                    r.update(bstab=L.mc_bstab(m[near], w), ks=L.mc_ks(m[near], w, rng=np.random.default_rng(5), **KS))
                rows.append(r)
        print(a, b, flush=True)
    x = pd.DataFrame(rows)
    x["mc"] = x[["bstab", "ks"]].max(axis=1, skipna=False)
    x.to_csv(L.CACHE / f"mc_all_grid_{tag}.csv", index=False)
    return x


def figure(g, STEP, RADIUS, tag):
    import sys
    import shapefile
    sys.path.insert(0, str(L.ROOT))
    import palette as P
    P.apply()
    land = [np.array(sh.points[a:b]) for sh in shapefile.Reader(str(L.ROOT.parent / "data/shapefiles/chile.shp")).shapes()
            for a, b in zip(sh.parts, list(sh.parts[1:]) + [len(sh.points)]) if b - a > 200]
    fig, ax = plt.subplots(1, len(MAPS), figsize=(4.6 * len(MAPS), 10.5), sharey=True)
    for a, (y0, y1) in zip(ax, MAPS):
        q = g[(g.start == y0)]
        q = q[q.mc.notna()]
        sc = a.scatter(q.lon, q.lat, c=q.mc, s=42 * (STEP / 0.5) ** 2, marker="s", lw=0, cmap="viridis_r", vmin=3.5, vmax=5.5)
        hi = q[q.mc > 4.55]
        a.scatter(hi.lon, hi.lat, s=42 * (STEP / 0.5) ** 2, marker="s", facecolor="none", edgecolor="k", lw=0.6)
        for ln in land:
            a.plot(ln[:, 0], ln[:, 1], color="0.35", lw=0.5)
        a.set_title(f"{y0}–{y1 - 1}", fontsize=11)
        a.set_xlim(-77.5, -64)
        a.set_ylim(-56.5, -16.5)
        a.set_aspect(1 / np.cos(np.radians(36)))
    fig.colorbar(sc, ax=ax, shrink=0.45, pad=0.02, label="Mc (larger of b-stability and KS)")
    fig.suptitle(f"Completeness of the whole catalogue: cells of {STEP}°, events of Mw ≥ {MLOW} within {RADIUS:.0f} km "
                 f"(at least {NNODE})\nblack outline: Mc above 4.5; blank: too few events", x=0.02, ha="left", fontsize=11)
    fig.savefig(L.FIG / f"mc_all_map_{tag}.png", dpi=150, bbox_inches="tight", pad_inches=0.25)


def run():
    pd.set_option("display.width", 250, "display.max_rows", 300)
    d = load()
    L.M0 = MLOW
    f = L.TAB / "mc_all_regions.csv"
    x = pd.read_csv(f) if f.exists() and not FORCE else regions(d)
    print(x.pivot_table(index=["region", "depth"], columns="start", values="ks", sort=False).to_string())
    print(x.pivot_table(index=["region", "depth"], columns="start", values="bstab", sort=False).to_string())
    print(x.pivot_table(index=["region", "depth"], columns="start", values="n50", sort=False).to_string())
    for step, radius, tag in GRIDS:
        f = L.CACHE / f"mc_all_grid_{tag}.csv"
        g = pd.read_csv(f) if f.exists() and not FORCE else grid(d, step, radius, tag)
        for (a, b), q in g.groupby(["start", "end"]):
            v = q.mc.dropna()
            print(tag, a, b, "cells", len(v), "median", round(v.median(), 1), "share above 4.5:", round((v > 4.55).mean(), 3),
                  "above 5.0:", round((v > 5.05).mean(), 3), "latitudes", q[q.mc.notna()].lat.min(), q[q.mc.notna()].lat.max())
        figure(g, step, radius, tag)

if __name__ == "__main__":
    run()

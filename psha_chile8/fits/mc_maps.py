"""Draft: Mc in space and time, measured with the estimators of table.py (b-stability, Cao and Gao 2002 / Woessner and
Wiemer 2005; Kolmogorov-Smirnov, Clauset et al. 2009; the larger), on nodes every 1 degree with the events within R km
(Wiemer and Wyss 2000 map Mc the same way), per network window of table.WINDOWS, all events from Mw 3.5.
Also the instrumental table from these Mc with no floor, by the rule of table.instrumental, for the five regions and
for the nodes.

Run from psha_chile8/fits/: OMP_NUM_THREADS=1 python mc_maps.py (supplement figure FIGURES/completeness/mc_maps.png)
"""
import sys
from multiprocessing import Pool
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import gr as G
import run as R
import table as TB
import palette as P
from plots import maps as M

R_KM, NMIN, STEP = 250.0, 100, 1.0


def km(lon1, lat1, lon2, lat2):
    p = np.pi / 180
    a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def one(a):
    (t0, t1), m, t, lon, lat, nodes = a
    s = (t >= t0) & (t < t1)
    m, lon, lat = m[s], lon[s], lat[s]
    rows = []
    for x, y in nodes:
        k = km(x, y, lon, lat) <= R_KM
        r = dict(start=t0, end=t1, lon=x, lat=y, n=int(k.sum()), bstab=np.nan, ks=np.nan)
        if k.sum() >= NMIN:
            w = np.ones(int(k.sum()))
            r.update(bstab=TB.mc_bstab(m[k], w), ks=TB.mc_ks(m[k], w, rng=np.random.default_rng(5), **TB.KS))
        rows.append(r)
    return rows


if __name__ == "__main__":
    P.apply()
    d = G.load()
    te = G.tend(d)
    m, t, lon, lat = (d[c].to_numpy(float) for c in ("mw", "t", "lon", "lat"))
    gx, gy = np.meshgrid(np.arange(-76.5, -63.4, STEP), np.arange(-56.5, -16.4, STEP))
    nodes = [(x, y) for x, y in zip(gx.ravel(), gy.ravel()) if (km(x, y, lon, lat) <= R_KM).sum() >= NMIN]
    with Pool(len(TB.WINDOWS)) as p:
        res = p.map(one, [(w, m, t, lon, lat, nodes) for w in TB.WINDOWS])
    x = pd.DataFrame([r for rr in res for r in rr])
    x["mc"] = x[["bstab", "ks"]].max(axis=1)
    x.to_csv(R.TAB / f"mc_nodes_{R.DATE}.csv", index=False)
    reg = TB.mc_windows(m, t, lat)
    reg.to_csv(R.TAB / f"mc_regions_{R.DATE}.csv", index=False)
    print("regions, no floor:", TB.instrumental(reg, floor=G.M0))
    xn = x.dropna(subset=["mc"]).rename(columns={"lon": "region"})
    print("nodes (largest node), no floor:", TB.instrumental(xn, floor=G.M0))
    s = x.groupby(["start", "end"]).agg(nodes=("mc", "size"), measured=("mc", lambda v: v.notna().sum()),
                                        median=("mc", "median"), p90=("mc", lambda v: v.quantile(0.9)), max=("mc", "max"),
                                        above45=("mc", lambda v: (v > 4.5).mean()), above50=("mc", lambda v: (v > 5.0).mean()))
    print(s.round(2).to_string())
    cmap = plt.get_cmap("viridis_r", 10)
    norm = matplotlib.colors.BoundaryNorm(np.arange(3.5, 5.51, 0.2), cmap.N)
    ext = [-77.0, -63.0, -57.0, -16.5]
    fig = plt.figure(figsize=(21, 9.5))
    for i, (a, b) in enumerate(TB.WINDOWS):
        ax = M.domain_map(fig, (1, len(TB.WINDOWS), i + 1), ext, labels="inside" if i else "left")
        q = x[(x.start == a) & x.mc.notna()]
        ax.scatter(q.lon, q.lat, c=q.mc, cmap=cmap, norm=norm, s=46, marker="s", transform=M.PC, zorder=4, edgecolors="none")
        r = reg[reg.start == a].mc.max()
        ax.text(0.04, 0.02, f"{a}–{b - 1}\nlargest region {r:.1f}", transform=ax.transAxes, fontsize=9, va="bottom", zorder=6)
    cax = fig.add_axes([0.35, 0.05, 0.3, 0.018])
    fig.colorbar(matplotlib.cm.ScalarMappable(norm, cmap), cax=cax, orientation="horizontal", label=f"Mc (events within {R_KM:.0f} km, at least {NMIN})")
    (R.PAPER / "completeness").mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(R.PAPER / "completeness" / f"mc_maps.{ext}", dpi=300, bbox_inches="tight", pad_inches=0.05)

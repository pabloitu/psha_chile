"""B9 addition: Mc per window with the events of Mw 4.0-4.4 of the frozen file, which the other B9 scripts leave out.
A completeness check only: no fit uses these events. Writes tables/mc_from_40.csv and figs/mc_from_40.png."""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import b9_lib as L

sys.path.insert(0, str(L.ROOT))
import palette as P

MLOW = 4.0
WINDOWS = [(1964, 1976), (1976, 1990), (1990, 2000), (2000, 2007), (2007, 2012), (2012, 2020), (2020, 2027)]
KLASS = L.FIT + ["all events"]
NMIN = 50


def load():
    f = L.CACHE / "m40.pkl"
    if f.exists():
        return pd.read_pickle(f)
    d = pd.read_csv(L.CAT, low_memory=False)
    d = d[(d.mw >= MLOW - 1e-9) & d.in_domain].copy()
    d["t"] = d.time.str[:4].astype(int) + 0.5
    for c, (w, s, v) in L.CLASSES.items():
        d["W_" + c] = d[w] * (1 if s is None else (d[s] == v))
    d.to_pickle(f)
    return d


def row(m, w, **key):
    """Mc by the three methods and the count ratios of neighbouring half-unit bands (about 3 for b = 1)."""
    n = lambda a: w[(m >= a - 1e-6) & (m < a + 0.5 - 1e-6)].sum()
    r = dict(key, n40=n(4.0), n45=n(4.5), n50=n(5.0), n55=n(5.5))
    r["r40_45"] = r["n40"] / r["n45"] if r["n45"] else np.nan
    r["r45_50"] = r["n45"] / r["n50"] if r["n50"] else np.nan
    r["r50_55"] = r["n50"] / r["n55"] if r["n55"] else np.nan
    if w.sum() >= NMIN:
        r.update(maxc=L.mc_maxc(m, w), bstab=L.mc_bstab(m, w), ks=L.mc_ks(m, w, rng=np.random.default_rng(5)))
        for c in (4.0, 4.5, 5.0):
            r[f"b{int(c * 10)}"] = L.tinti(m, w, c)[0]
    return r


def figure(d):
    P.apply()
    fig, ax = plt.subplots(2, 4, figsize=(16.8, 7.4), sharex=True)
    edges = np.arange(MLOW - 0.05, 7.06, 0.1)
    x = edges[:-1] + 0.05
    for a, c in zip(ax.ravel(), L.FIT):
        for (y0, y1), col in zip(WINDOWS, plt.cm.viridis(np.linspace(0, 0.92, len(WINDOWS)))):
            s = (d.t >= y0) & (d.t < y1)
            h = np.histogram(d.mw[s], edges, weights=d["W_" + c][s])[0] / (y1 - y0)
            a.plot(x[h > 0], h[h > 0], "-o", ms=2.5, lw=1.1, color=col, label=f"{y0}–{y1 - 1}")
        a.axvline(4.45, color="0.4", lw=0.8, ls="--")
        a.set_yscale("log")
        a.set_title(P.CLASS_NAME.get(c, c), fontsize=11)
    for a in ax[:, 0]:
        a.set_ylabel("events per year per 0.1 bin")
    for a in ax[-1]:
        a.set_xlabel("Mw")
    ax[0, 0].legend(fontsize=8, frameon=False)
    fig.suptitle("Magnitude distribution per period from Mw 4.0 (dashed: the cut of the statistics at 4.5)", y=0.99)
    fig.tight_layout()
    fig.savefig(L.FIG / "mc_from_40.png", dpi=150, bbox_inches="tight", pad_inches=0.25)


def run():
    d = load()
    L.M0 = MLOW
    m, t = d.mw.to_numpy(), d.t.to_numpy()
    rows = []
    for c in KLASS:
        w = np.ones(len(d)) if c == "all events" else d["W_" + c].to_numpy()
        for a, b in WINDOWS:
            s = (t >= a) & (t < b) & (w > 0)
            rows.append(row(m[s], w[s], cls=c, region="all", start=a, end=b))
        if c == "interface":
            for rg, (la0, la1) in L.REG.items():
                for a, b in WINDOWS[3:]:
                    s = (t >= a) & (t < b) & (w > 0) & (d.lat.to_numpy() >= la0) & (d.lat.to_numpy() < la1)
                    rows.append(row(m[s], w[s], cls=c, region=rg, start=a, end=b))
        print(c, flush=True)
    pd.DataFrame(rows).round(3).to_csv(L.TAB / "mc_from_40.csv", index=False)
    figure(d)


if __name__ == "__main__":
    run()

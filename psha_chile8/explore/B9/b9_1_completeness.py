"""B9 part 1: completeness in time per class. Stepp, change points of the yearly counts per magnitude threshold, and
Mc per window (maximum curvature, b-stability, Kolmogorov-Smirnov). Writes cache/comp_*.csv."""
import time

import numpy as np
import pandas as pd

import b9_lib as L

THR = [4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0]
Y0 = 1900
WINDOWS = {"network": [(1964, 1976), (1976, 1990), (1990, 2000), (2000, 2007), (2007, 2012), (2012, 2027)],
           "decade": [(y, y + 10) for y in range(1960, 2020, 10)] + [(2020, 2027)]}
MODES = ["all", "w1"]
# the completeness years are also read on declustered counts: Stepp assumes a Poisson process
BASIS = ["full", "gk", "nn"]
KLASS = list(L.CLASSES) + ["all events"]


def weights(d, c, mode):
    w = np.ones(len(d)) if c == "all events" else d["W_" + c].to_numpy()
    return np.where(w >= 1 - 1e-9, w, 0.0) if mode == "w1" else w


def run():
    d = L.load()
    te = L.tend(d)
    t, m = d.t.to_numpy(), d.mw.to_numpy()
    yrs = np.arange(1500, int(te) + 1)
    dc = pd.read_pickle(L.CACHE / "decluster.pkl")
    rows, mcs, yc = [], [], []
    for c in KLASS:
        for mode in MODES:
            w = weights(d, c, mode)
            for basis in BASIS:
                keep = np.ones(len(d), bool) if basis == "full" else dc[basis].to_numpy()
                for thr in THR:
                    s = (m >= thr - 1e-6) & (w > 0) & keep
                    cnt = np.bincount((np.floor(t[s]) - yrs[0]).astype(int), w[s], minlength=yrs.size)
                    yc.append(pd.DataFrame(dict(cls=c, mode=mode, basis=basis, thr=thr, year=yrs, n=cnt)))
                    y0 = Y0 if thr < 7 else 1513
                    u = s & (t >= y0)
                    ys, _ = L.stepp(t[u], w[u], te, tref=20 if thr < 6.5 else 60)
                    k = yrs >= y0
                    if cnt[k].sum() >= 10:
                        ycp, br, rates, phi = L.complete_since(yrs[k], cnt[k], min_len=5 if thr < 7 else 15)
                    else:
                        ycp, br, rates, phi = np.nan, [], [], np.nan
                    rows.append(dict(cls=c, mode=mode, basis=basis, thr=thr, n=w[u].sum(), stepp=ys, changepoint=ycp,
                                     breaks=" ".join(map(str, br)), rates=" ".join(f"{r:.2f}" for r in rates), phi=phi))
            for wn, wins in WINDOWS.items():
                for a, b in wins:
                    s = (t >= a) & (t < b) & (w > 0)
                    n = w[s].sum()
                    r = dict(cls=c, mode=mode, windows=wn, start=a, end=b, n=n)
                    if n >= 50:
                        r.update(maxc=L.mc_maxc(m[s], w[s]), bstab=L.mc_bstab(m[s], w[s]),
                                 ks=L.mc_ks(m[s], w[s], rng=np.random.default_rng(5)))
                        for q in ("bstab", "ks"):
                            if np.isfinite(r[q]):
                                r["b_" + q] = L.tinti(m[s], w[s], r[q])[0]
                    mcs.append(r)
        print(c, flush=True)
    pd.DataFrame(rows).to_csv(L.CACHE / "comp_years.csv", index=False)
    pd.DataFrame(mcs).to_csv(L.CACHE / "comp_mc_windows.csv", index=False)
    pd.concat(yc).to_pickle(L.CACHE / "yearly_counts.pkl")


if __name__ == "__main__":
    t0 = time.time()
    run()
    print(f"{time.time() - t0:.0f} s")

"""B9: the checks that decide, as tables. Stationarity of the rate per period, the share removed by declustering,
all events against weight-1 events, the large-event check and the tornado of N(>= 7). Needs cache/fits_*.csv.
Writes tables/*.csv."""
import numpy as np
import pandas as pd
from scipy import stats

import b9_lib as L
import b9_3_fits as F
import b9_tables as TB

# magnitude from, first period used
STAT = [(5.5, 1964), (5.0, 1976), (4.5, 2000)]


def poisson_band(mu, p=(0.05, 0.95)):
    return stats.poisson.ppf(p[0], mu), stats.poisson.ppf(p[1], mu)


def stationarity(d, dc, W):
    te = L.tend(d)
    t, m = d.t.to_numpy(), d.mw.to_numpy()
    keep = {"full": np.ones(len(d), bool), "gk": dc.gk.to_numpy(), "nn": dc.nn.to_numpy()}
    rows = []
    for c, w in W.items():
        for mf, y0 in STAT:
            for basis, kp in keep.items():
                per = [(a, min(b, te)) for a, b in L.PERIODS if a >= y0]
                n = np.array([w[kp & (m >= mf - 1e-6) & (t >= a) & (t < b)].sum() for a, b in per])
                T = np.array([b - a for a, b in per])
                if n.sum() < 5 or len(per) < 2:
                    continue
                e = n.sum() * T / T.sum()
                chi = ((n - e) ** 2 / e).sum()
                yc = np.bincount((np.floor(t[kp & (m >= mf - 1e-6) & (t >= y0)]) - y0).astype(int),
                                 w[kp & (m >= mf - 1e-6) & (t >= y0)], minlength=int(te) - y0 + 1)
                r = dict(cls=c, m_from=mf, since=y0, basis=basis, n=n.sum(), rate=n.sum() / T.sum(), chi2=chi,
                         p=stats.chi2.sf(chi, len(per) - 1), fano=yc.var() / max(yc.mean(), 1e-9),
                         max_ratio=(n / T).max() / max((n / T).min(), 1e-9))
                for (a, b), x, tt in zip(per, n, T):
                    r[f"rate_{a}"] = x / tt
                rows.append(r)
    return pd.DataFrame(rows)


def removed(d, dc, W):
    m = d.mw.to_numpy()
    rows = []
    for c, w in W.items():
        for mf in (4.5, 5.5, 7.0):
            s = m >= mf - 1e-6
            rows.append(dict(cls=c, m_from=mf, n=w[s].sum(), **{k: 1 - (w * dc[k])[s].sum() / max(w[s].sum(), 1e-9) for k in ("gk", "gk_fs0", "nn")}))
    return pd.DataFrame(rows)


def run():
    d = L.load()
    dc = pd.read_pickle(L.CACHE / "decluster.pkl")
    W = F.classes(d)
    L.TAB.mkdir(exist_ok=True)
    stationarity(d, dc, W).round(4).to_csv(L.TAB / "stationarity.csv", index=False)
    removed(d, dc, W).round(4).to_csv(L.TAB / "declustering_removed.csv", index=False)
    f = pd.read_csv(L.CACHE / "fits_main.csv")
    key = ["cls", "table", "mode", "basis", "corr"]
    cols = ["b", "b_lo", "b_hi", "rate", "m_lo", "n", "N5", "N6", "N7", "N7_lo", "N7_hi", "N7.5", "N8", "N8_lo", "N8_hi"]
    f[key + cols].round(5).to_csv(L.TAB / "fits_main.csv", index=False)

    # weights: weight-1 events against all, same table
    a = f[(f.basis == "full") & (f["corr"] == "none")].pivot_table(index=["cls", "table"], columns="mode", values=["b", "N5", "N7", "n"])
    a.columns = [f"{x}_{y}" for x, y in a.columns]
    a["db"] = a.b_w1 - a.b_all
    for q in ("N5", "N7", "n"):
        a[q + "_ratio"] = a[q + "_w1"] / a[q + "_all"]
    a.round(4).reset_index().to_csv(L.TAB / "weights_effect.csv", index=False)

    # declustered against full
    a = f[(f["mode"] == "all") & (f["corr"] == "none")].pivot_table(index=["cls", "table"], columns="basis", values=["b", "N5", "N7"])
    a.columns = [f"{x}_{y}" for x, y in a.columns]
    a.round(4).reset_index().to_csv(L.TAB / "declustered_fits.csv", index=False)

    # magnitude-error correction
    a = f[(f["mode"] == "all") & (f.basis == "full")].pivot_table(index=["cls", "table"], columns="corr", values=["b", "N5", "N7"])
    a.columns = [f"{x}_{y}" for x, y in a.columns]
    for q in ("N5", "N7"):
        for c in ("ceus", "plain"):
            a[f"{q}_{c}_ratio"] = a[f"{q}_{c}"] / a[f"{q}_none"]
    a.round(4).reset_index().to_csv(L.TAB / "error_correction.csv", index=False)

    # large events: expected against observed inside each table, fit on all magnitudes and fit below 7 or 6.5
    g = pd.read_csv(L.CACHE / "fits_below.csv")
    f["top"] = np.nan
    big = pd.concat([f, g])
    for M in ("7", "7.5", "8"):
        lo, hi = poisson_band(big["exp" + M].clip(lower=1e-9))
        big[f"lo{M}"], big[f"hi{M}"] = lo, hi
        big[f"in{M}"] = (big["obs" + M] >= lo - 0.5) & (big["obs" + M] <= hi + 0.5)
    big[key + ["top", "b"] + [f"{q}{M}" for M in ("7", "7.5", "8") for q in ("exp", "obs", "lo", "hi", "in", "T")]].round(3).to_csv(L.TAB / "large_events.csv", index=False)

    # tornado of N(>= 7): one change at a time against the baseline of fits_sens
    s = pd.read_csv(L.CACHE / "fits_sens.csv")
    rows = []
    for c in s.cls.unique():
        b0 = s[(s.cls == c) & (s.case == "baseline")].iloc[0]
        base = b0.table
        for _, r in s[(s.cls == c) & (s.case != "baseline")].iterrows():
            rows.append(dict(cls=c, group="catalogue", case=r.case, N7=r.N7, b=r.b))
        q = f[f.cls == c]

        def pick(**kw):
            x = dict(table=base, **F.BASE)
            x.update(kw)
            y = q[(q.table == x["table"]) & (q["mode"] == x["mode"]) & (q.basis == x["basis"]) & (q["corr"] == x["corr"])]
            return y.iloc[0] if len(y) else None

        alt = [("weights", "weight-1 events only", dict(mode="w1")), ("declustering", "Gardner–Knopoff", dict(basis="gk")),
               ("declustering", "nearest neighbour", dict(basis="nn")), ("magnitude error", "CEUS-SSC correction", dict(corr="ceus")),
               ("magnitude error", "plain weight", dict(corr="plain"))]
        alt += [("completeness table", "table: " + n, dict(table=n)) for n in TB.tables(c) if n != base]
        for grp, name, kw in alt:
            r = pick(**kw)
            if r is not None:
                rows.append(dict(cls=c, group=grp, case=name, N7=r.N7, b=r.b))
        fl = pd.read_csv(L.CACHE / "fits_floors.csv")
        fl = fl[(fl.cls == c) & (fl.table == "network") & (fl.basis == "full") & (fl["corr"] == "none")]
        for v in (5.0, 5.5, 6.0):
            r = fl[np.isclose(fl.floor, v)]
            if len(r):
                rows.append(dict(cls=c, group="fit floor", case=f"floor {v:.1f} (network table)", N7=r.N7.iloc[0], b=r.b.iloc[0]))
        for r in rows:
            if r["cls"] == c:
                r.update(N7_base=b0.N7, b_base=b0.b, base=base, N7_lo=b0.N7_lo, N7_hi=b0.N7_hi)
    t = pd.DataFrame(rows)
    t["ratio"] = t.N7 / t.N7_base
    t.round(5).to_csv(L.TAB / "tornado_N7.csv", index=False)
    print("tables written")


if __name__ == "__main__":
    run()

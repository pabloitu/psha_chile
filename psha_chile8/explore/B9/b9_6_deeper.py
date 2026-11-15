"""B9: follow-up of the surprises. (1) large events before and after 1976 per class and magnitude source;
(2) why a table of unequal windows raises the interface b; (3) the magnitude-error correction on the historical
events; (4) one-window tables with the long record only for the large events. Writes tables/deeper_*.csv."""
import numpy as np
import pandas as pd
from scipy import stats

import b9_lib as L
import b9_3_fits as F
import b9_tables as TB

ERAS = [(1900, 1930), (1930, 1964), (1964, 1976), (1976, 2000), (2000, 2027)]


def run():
    d = L.load()
    te = L.tend(d)
    W = F.classes(d)
    t, k, m, sig = d.t.to_numpy(), d.k.to_numpy(), d.mw.to_numpy(), d.mw_sigma.fillna(0.2).to_numpy()

    # 1 large events per era
    rows = []
    for c in ["interface", "intraslab_shallow", "intraslab_intermediate", "intraslab", "crustal", "outer_rise"]:
        w = W[c]
        for M in (6.5, 7.0, 7.5):
            r = dict(cls=c, m_from=M)
            for a, b in ERAS:
                s = (m >= M - 1e-6) & (t >= a) & (t < b)
                r[f"n_{a}"] = w[s].sum()
                r[f"rate_{a}"] = w[s].sum() / (min(b, te) - a)
            n1, T1 = w[(m >= M - 1e-6) & (t >= 1900) & (t < 1976)].sum(), 76.0
            n2, T2 = w[(m >= M - 1e-6) & (t >= 1976)].sum(), te - 1976
            r["ratio_before_after_1976"] = (n1 / T1) / max(n2 / T2, 1e-9)
            # conditional binomial test of equal rates
            r["p_equal"] = stats.binomtest(int(round(n1)), int(round(n1 + n2)), T1 / (T1 + T2)).pvalue if n1 + n2 >= 1 else np.nan
            rows.append(r)
    pd.DataFrame(rows).round(3).to_csv(L.TAB / "deeper_large_by_era.csv", index=False)
    rows = []
    for c in ["interface", "intraslab_shallow", "intraslab_intermediate"]:
        w = W[c]
        s = (m >= 7 - 1e-6) & (w > 0) & (t >= 1900)
        x = d[s].assign(w=w[s], era=np.where(t[s] < 1976, "1900–1975", "1976 on"))
        g = x.groupby(["era", "mw_kind", "depth_kind"]).agg(n=("w", "sum"), events=("w", "size"), mean_mw=("mw", "mean"), w1=("w", lambda v: (v >= 1).sum())).reset_index()
        rows.append(g.assign(cls=c))
    pd.concat(rows).round(2).to_csv(L.TAB / "deeper_large_by_source.csv", index=False)

    # 2 unequal windows, interface and the others: the same class on one-window and two-window tables
    rows = []
    tabs = {"4.5 from 2000": [(4.5, 2000)], "5.0 from 1964": [(5.0, 1964)], "5.5 from 1964": [(5.5, 1964)],
            "5.0 from 2000": [(5.0, 2000)], "5.5 from 2000": [(5.5, 2000)],
            "4.5 from 2000 + 5.5 from 1964": [(4.5, 2000), (5.5, 1964)], "network": TB.NETWORK,
            "5.0 from 1964 + 7.0 from 1900": [(5.0, 1964), (7.0, 1900)],
            "5.0 from 1964 + 7.0 from 1900 + counts": [(5.0, 1964), (7.0, 1900), (7.5, 1820), (8.0, 1730)],
            "5.2 from 1964 + 7.0 from 1900 + counts": [(5.2, 1964), (7.0, 1900), (7.5, 1820), (8.0, 1730)],
            "5.5 from 1964 + 7.0 from 1900 + counts": [(5.5, 1964), (7.0, 1900), (7.5, 1820), (8.0, 1730)],
            "5.0 from 1976 + 5.5 from 1964 + 7.0 from 1900": [(5.0, 1976), (5.5, 1964), (7.0, 1900)]}
    for c, w in W.items():
        for name, tb in tabs.items():
            for mode in ("all", "w1"):
                rows.append(dict(cls=c, table=name, mode=mode, **F.one(k, t, F.mode_w(w, mode), sig, tb, te, nboot=200)))
        for a, b in ((1964, 2000), (2000, 2027)):
            s = (t >= a) & (t < b) & (m >= 5.45)
            rows.append(dict(cls=c, table=f"rate of M >= 5.5, {a}-{b}", mode="all", rate=w[s].sum() / (min(b, te) - a)))
    x = pd.DataFrame(rows)
    for M in ("7", "8"):
        lo, hi = stats.poisson.ppf(0.05, x["exp" + M].clip(lower=1e-9)), stats.poisson.ppf(0.95, x["exp" + M].clip(lower=1e-9))
        x["in" + M] = (x["obs" + M] >= lo - 0.5) & (x["obs" + M] <= hi + 0.5)
    x.round(4).to_csv(L.TAB / "deeper_windows.csv", index=False)

    # 3 magnitude-error correction on the long tables: all events, sigma capped, instrumental events only
    rows = []
    for c in ["interface", "intraslab_intermediate", "intraslab_shallow"]:
        w = W[c]
        for name in ("network", "network+counts", "network+Lomnitz"):
            tb = TB.tables(c)[name]
            for lab, sg in (("none", None), ("as catalogued", sig), ("sigma capped at 0.25", np.minimum(sig, 0.25)),
                            ("only events from 1964", np.where(t >= 1964, sig, 0.0))):
                r = F.one(k, t, w, sig if sg is None else sg, tb, te, "none" if sg is None else "ceus", nboot=0)
                rows.append(dict(cls=c, table=name, correction=lab, **r))
    pd.DataFrame(rows).round(4).to_csv(L.TAB / "deeper_error_correction.csv", index=False)
    q = d[(m >= 7.5) & (W["interface"] > 0)]
    be = 1.0 * L.LN10
    pd.DataFrame(dict(time=q.time.str[:10], mw=q.mw, sigma=q.mw_sigma, kind=q.mw_kind, w_interface=q.W_interface.round(2),
                      moved_to=(q.mw - be * q.mw_sigma ** 2).round(2), counts_as=np.exp(be ** 2 * q.mw_sigma ** 2 / 2).round(2))).to_csv(
        L.TAB / "deeper_ceus_large_interface.csv", index=False)
    print("deeper tables written")


if __name__ == "__main__":
    run()

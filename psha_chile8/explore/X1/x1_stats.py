"""X1 tier 4: preview of B9 — Mc, b and rates across the matching, location and magnitude variants."""
import itertools
import time

import numba as nb
import numpy as np
import pandas as pd
from scipy.optimize import brentq

import x1_io as io

# settings
FAMILIES = {"crustal shallow": ("above slab, shallow", None), "interface band": ("interface band", None),
            "in slab": ("in slab", None), "in slab < 70 km": ("in slab", (0, 70)), "in slab ≥ 70 km": ("in slab", (70, 999))}
WINDOWS = [(1900, 1964), (1964, 1976), (1976, 2000), (2000, 2010), (2010, 2027)]
T_END = 2026.86
FLOORS = np.round(np.arange(4.5, 6.01, 0.1), 1)
DM = 0.1
MC_METHODS = ["maxc", "bstab", "ks"]
LOC_V = ["L-a", "L-b 44°S"]
MIN_MC = 50
STEP = 0.3
DELTA_BPOS = 0.2
REF = {"match": "baseline", "loc": "L-a", "variant": "M0", "weights": False, "declust": False, "mc": "maxc", "floor": 5.0}
MMIN_DECL = 3.5


# estimators
def mc_maxc(m):
    if len(m) < MIN_MC:
        return np.nan
    b = np.round(m / DM).astype(int)
    v, c = np.unique(b, return_counts=True)
    return v[np.argmax(c)] * DM + 0.2


def aki(m, mc, w=None):
    """Aki–Utsu b for binned magnitudes ≥ mc (bin width DM), optionally weighted."""
    k = m >= mc - 1e-9
    if k.sum() < 2:
        return np.nan
    w = np.ones(k.sum()) if w is None else w[k]
    mean = np.sum(w * m[k]) / w.sum()
    return np.log10(np.e) / (mean - (mc - DM / 2))


def mc_bstab(m):
    if len(m) < MIN_MC:
        return np.nan
    for mc in np.round(np.arange(3.0, 7.5, DM), 1):
        k = m >= mc - 1e-9
        if k.sum() < MIN_MC:
            return np.nan
        bs = [aki(m, mc + j * DM) for j in range(6)]
        bav = np.nanmean(bs)
        mm = m[k]
        dbs = 2.3 * bs[0] ** 2 * np.sqrt(np.sum((mm - mm.mean()) ** 2) / (len(mm) * (len(mm) - 1)))
        if abs(bav - bs[0]) <= dbs:
            return mc
    return np.nan


def mc_ks(m):
    """Clauset et al. (2009): Mc minimising the KS distance between the binned data above Mc and its fitted GR."""
    if len(m) < MIN_MC:
        return np.nan
    best = (np.inf, np.nan)
    for mc in np.round(np.arange(3.0, 7.5, DM), 1):
        x = m[m >= mc - 1e-9]
        if len(x) < MIN_MC:
            break
        b = aki(m, mc)
        if not np.isfinite(b) or b <= 0:
            continue
        g = np.round(np.arange(mc, x.max() + DM / 2, DM), 1)
        emp = np.array([(x <= q + 1e-9).mean() for q in g])
        mod = 1 - 10 ** (-b * (g + DM / 2 - (mc - DM / 2)))
        d = np.max(np.abs(emp - mod))
        if d < best[0]:
            best = (d, mc)
    return best[1]


MCF = {"maxc": mc_maxc, "bstab": mc_bstab, "ks": mc_ks}


def ctable(mcs):
    """Completeness table from per-window Mc: no later window above an earlier one, steps ≥ STEP."""
    mc = np.array([np.nan if v is None else v for v in mcs], float)
    for i in range(len(mc)):
        if np.isnan(mc[i]):
            mc[i] = mc[i - 1] if i else 7.0
    for i in range(1, len(mc)):
        mc[i] = min(mc[i], mc[i - 1])
    out = [[WINDOWS[0][0], mc[0]]]
    for (y0, _), v in zip(WINDOWS[1:], mc[1:]):
        if out[-1][1] - v >= STEP - 1e-9:
            out.append([y0, v])
    return out


def weichert(m, yr, tab, floor, w=None, mmax=9.6):
    """
    Weichert (1980) maximum likelihood b and rate with a completeness table.

    Parameters
    ----------
    m, yr : magnitudes (binned at DM) and decimal years
    tab : list of [start year, Mc], Mc decreasing with time
    floor : lowest magnitude fitted
    w : event weights (Tinti–Mulargia), default 1

    Returns
    -------
    b, sd(b), rate of M ≥ floor per year, number of events used
    """
    w = np.ones(len(m)) if w is None else w
    mb = np.round(np.arange(floor, mmax + DM / 2, DM), 1)
    T = np.zeros(len(mb))
    for i, q in enumerate(mb):
        st = [y for y, c in tab if c <= q + 1e-9]
        T[i] = T_END - min(st) if st else 0.0
    keep = T > 0
    mb, T = mb[keep], T[keep]
    if len(mb) < 3:
        return np.nan, np.nan, np.nan, 0
    bi = np.clip(np.round((m - floor) / DM).astype(int), -1, None)
    ok = (bi >= 0) & (bi < len(mb))
    ok[ok] &= yr[ok] >= T_END - T[bi[ok]]
    n = np.bincount(bi[ok], weights=w[ok], minlength=len(mb))
    N = n.sum()
    if N < 10:
        return np.nan, np.nan, np.nan, int(N)
    mbar = np.sum(n * mb) / N

    def f(beta):
        e = T * np.exp(-beta * mb)
        return np.sum(mb * e) / np.sum(e) - mbar

    try:
        beta = brentq(f, 0.05, 8.0)
    except ValueError:
        return np.nan, np.nan, np.nan, int(N)
    e = T * np.exp(-beta * mb)
    var = (np.sum(e) ** 2) / (N * (np.sum(mb * e) ** 2 - np.sum(e) * np.sum(mb ** 2 * e)))
    sb = np.sqrt(abs(var)) / np.log(10)
    g = np.exp(-beta * (mb - floor))
    rate = N * g.sum() / np.sum(T * g)
    return beta / np.log(10), sb, rate, int(N)


def bpos(m, t, floor):
    """b-positive (van der Elst 2021) on time-ordered magnitudes ≥ floor, binned at DM."""
    k = m >= floor - 1e-9
    x = m[k][np.argsort(t[k])]
    d = np.diff(x)
    d = d[d >= DELTA_BPOS - 1e-9]
    if len(d) < 20:
        return np.nan
    return np.log10(np.e) / (d.mean() - (DELTA_BPOS - DM / 2))


@nb.njit(cache=True)
def gk_flags(t, la, lo, m):
    """Gardner–Knopoff (1974) window declustering; t in days, returns True for dependent events."""
    n = len(t)
    order = np.argsort(-m)
    dep = np.zeros(n, np.bool_)
    ts = np.argsort(t)
    tsorted = t[ts]
    for i in order:
        if dep[i]:
            continue
        M = m[i]
        T = 10 ** (0.032 * M + 2.7389) if M >= 6.5 else 10 ** (0.5409 * M - 0.547)
        L = 10 ** (0.1238 * M + 0.983)
        j0 = np.searchsorted(tsorted, t[i])
        j1 = np.searchsorted(tsorted, t[i] + T)
        for jj in range(j0, j1):
            j = ts[jj]
            if j == i or dep[j] or m[j] > M:
                continue
            p1, p2 = np.radians(la[i]), np.radians(la[j])
            a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lo[j] - lo[i]) / 2) ** 2
            if 2 * 6371.0 * np.arcsin(np.sqrt(min(a, 1.0))) <= L:
                dep[j] = True
    return dep


# data
def catalogs():
    MW = io.load("mw_variants")
    lv = io.load("locvariants")
    lv = lv[lv["loc"].isin(LOC_V)]
    ev_t = {}
    for nm in ("baseline", "nb_order", "nb_calibrated"):
        e = io.load(f"events_{nm}")
        ev_t[nm] = e.set_index("ev").t
    return MW, lv, ev_t


def family_mask(c, fam):
    cls, zr = FAMILIES[fam]
    k = c.cls.to_numpy() == cls
    if zr:
        k &= (c.z.to_numpy() >= zr[0]) & (c.z.to_numpy() < zr[1])
    return k


def run():
    T0 = time.time()
    MW, lv, ev_t = catalogs()
    rows, mcrows, obs = [], [], []
    combos = []
    for (nm, var), mw in MW.groupby(["match", "variant"]):
        for loc in LOC_V:
            combos.append((nm, var, loc))
    print("combos", len(combos), flush=True)
    for nm, var, loc in combos:
        mw = MW[(MW["match"] == nm) & (MW.variant == var)].set_index("ev")
        c = lv[(lv["match"] == nm) & (lv["loc"] == loc)].set_index("ev")
        c = c[~c.index.duplicated()]
        d = c.join(mw[["mw", "sig"]], how="inner")
        d = d[np.isfinite(d.mw)]
        d["m"] = np.round(d.mw / DM) * DM
        d["t"] = ev_t[nm].reindex(d.index).to_numpy() / 86400.0
        d = d[(d.yr >= 1900) & (d.m >= MMIN_DECL)]
        dep = gk_flags(d.t.to_numpy(), d.lat.to_numpy(), d.lon.to_numpy(), d.m.to_numpy())
        for decl in (False, True):
            dd = d[~dep] if decl else d
            for fam in FAMILIES:
                x = dd[family_mask(dd, fam)]
                m, yr, sg = x.m.to_numpy(), x.yr.to_numpy(), x.sig.fillna(0.2).to_numpy()
                tabs = {}
                for mcm in MC_METHODS:
                    mcs = []
                    for y0, y1 in WINDOWS:
                        k = (yr >= y0) & (yr < y1)
                        v = MCF[mcm](m[k])
                        mcs.append(v)
                        mcrows.append({"match": nm, "variant": var, "loc": loc, "declust": decl, "family": fam,
                                       "mc": mcm, "window": f"{y0}–{y1 - 1}", "Mc": v, "n": int(k.sum())})
                    tabs[mcm] = ctable(mcs)
                for wt in (False, True):
                    for mcm, tab in tabs.items():
                        for fl in FLOORS:
                            w = None
                            if wt:
                                b0 = 1.0
                                for _ in range(2):
                                    w = np.exp(-((b0 * np.log(10) * sg) ** 2) / 2)
                                    bb = weichert(m, yr, tab, fl, w)[0]
                                    b0 = bb if np.isfinite(bb) else 1.0
                            b, sb, rate, n = weichert(m, yr, tab, fl, w)
                            r = {"match": nm, "variant": var, "loc": loc, "declust": decl, "weights": wt, "mc": mcm,
                                 "family": fam, "floor": fl, "b": b, "sb": sb, "rate": rate, "n": n,
                                 "table": " ".join(f"{y}:{v:.1f}" for y, v in tab)}
                            if np.isfinite(b):
                                for q in (6.0, 7.0, 8.0):
                                    r[f"N≥{q}/yr"] = rate * 10 ** (-b * (q - fl))
                            rows.append(r)
                for fl in FLOORS:
                    k = yr >= 1964
                    rows.append({"match": nm, "variant": var, "loc": loc, "declust": decl, "weights": False,
                                 "mc": "b-positive", "family": fam, "floor": fl, "b": bpos(m[k], x.t.to_numpy()[k], fl),
                                 "n": int((m[k] >= fl).sum())})
                for q in (6.0, 7.0, 8.0):
                    k = m >= q - 1e-9
                    for y0 in (1904, 1964, 1976):
                        obs.append({"match": nm, "variant": var, "loc": loc, "declust": decl, "family": fam, "M": q,
                                    "from": y0, "n_obs": int((k & (yr >= y0)).sum()), "years": T_END - y0})
        print(nm, var, loc, round(time.time() - T0), flush=True)
    R = pd.DataFrame(rows)
    R.to_csv(io.CACHE / "stats_fits.csv.gz", index=False)
    pd.DataFrame(mcrows).to_csv(io.TAB / "t4_mc_windows.csv", index=False)
    pd.DataFrame(obs).to_csv(io.TAB / "t4_observed_large.csv", index=False)
    summarize(R, pd.DataFrame(obs))
    plt = io.fig_setup()
    fig_bfloor(plt, R)
    fig_tornado(plt, R)
    fig_large(plt, R, pd.DataFrame(obs))
    print("tier 4 done", round(time.time() - T0), flush=True)


def sel(R, **kw):
    q = dict(REF)
    q.update(kw)
    k = np.ones(len(R), bool)
    for c, v in q.items():
        k &= (R[c] == v).to_numpy()
    return R[k]


def tornado_table(R):
    out = []
    for fam in FAMILIES:
        base = sel(R, family=fam)
        if not len(base):
            continue
        b0 = base.b.iloc[0]
        n0 = base["N≥6.0/yr"].iloc[0]
        alts = {"matching": [{"match": "nb_order"}, {"match": "nb_calibrated"}],
                "location": [{"loc": "L-b 44°S"}],
                "magnitude variant": [{"variant": f"M{i}"} for i in range(1, 9)],
                "TM weights": [{"weights": True}],
                "declustering": [{"declust": True}],
                "Mc method": [{"mc": "bstab"}, {"mc": "ks"}],
                "fit floor ±0.3": [{"floor": 4.7}, {"floor": 5.3}]}
        for fac, al in alts.items():
            for a in al:
                x = sel(R, family=fam, **a)
                if not len(x):
                    continue
                out.append({"family": fam, "factor": fac, "alt": str(list(a.values())[0]), "b0": b0, "b": x.b.iloc[0],
                            "db": x.b.iloc[0] - b0, "N6_0": n0, "N6": x["N≥6.0/yr"].iloc[0],
                            "rN6": x["N≥6.0/yr"].iloc[0] / n0 if n0 else np.nan})
    return pd.DataFrame(out)


def summarize(R, obs):
    t = tornado_table(R)
    t.to_csv(io.TAB / "t4_tornado.csv", index=False)
    k = (R.mc != "b-positive")
    s = R[k].groupby(["family", "floor"]).b.describe()[["count", "mean", "std", "min", "max"]]
    s.to_csv(io.TAB / "t4_b_spread_by_floor.csv")
    bp = R[(R.mc == "b-positive")].groupby(["family", "floor", "variant"]).b.median().unstack()
    bp.to_csv(io.TAB / "t4_bpositive.csv")
    ref = R[(R["match"] == "baseline") & (R["loc"] == "L-a") & (R.weights == False) & (R.mc == "maxc")]  # noqa: E712
    ref.pivot_table(index=["family", "floor"], columns=["variant", "declust"], values="b").to_csv(
        io.TAB / "t4_b_by_variant.csv")
    o = obs[(obs["from"] == 1904)]
    f = R[(R.mc == "maxc") & (R.weights == False) & R.floor.isin([5.0, 5.5])]  # noqa: E712
    m = f.merge(o[o.M == 7.0][["match", "variant", "loc", "declust", "family", "n_obs", "years"]],
                on=["match", "variant", "loc", "declust", "family"])
    m["N7_fit"] = m["N≥7.0/yr"] * m.years
    m = m.merge(o[o.M == 8.0][["match", "variant", "loc", "declust", "family", "n_obs"]].rename(
        columns={"n_obs": "n_obs8"}), on=["match", "variant", "loc", "declust", "family"])
    m["N8_fit"] = m["N≥8.0/yr"] * m.years
    m[["match", "variant", "loc", "declust", "family", "floor", "b", "n_obs", "N7_fit", "n_obs8", "N8_fit"]].to_csv(
        io.TAB / "t4_large_fit_vs_obs.csv", index=False)


def fig_bfloor(plt, R):
    fams = list(FAMILIES)
    fig, ax = plt.subplots(2, len(fams), figsize=(4.2 * len(fams), 9), layout="constrained", sharex=True)
    for j, fam in enumerate(fams):
        for i, decl in enumerate((False, True)):
            a = ax[i, j]
            x = R[(R.family == fam) & (R.declust == decl) & (R.mc != "b-positive")]
            env = x.groupby("floor").b.quantile([0.05, 0.95]).unstack()
            a.fill_between(env.index, env[0.05], env[0.95], color="0.85", label="all combinations, 5–95 %")
            for k_, (v, col) in enumerate((("M0", "#2166ac"), ("M1", "#e0641e"), ("M2", "#2e8b57"), ("M4", "#a50f15"),
                                           ("M7", "#7f7f7f"))):
                y = sel(R, family=fam, declust=decl, variant=v).set_index("floor") if True else None
                yy = R[(R.family == fam) & (R.declust == decl) & (R.variant == v) & (R["match"] == "baseline")
                       & (R["loc"] == "L-a") & (R.weights == False) & (R.mc == "maxc")].set_index("floor")  # noqa: E712
                a.plot(yy.index, yy.b, color=col, lw=1.6, label={"M0": "M0 (DECISIONS line)", "M1": "M1 OLS",
                                                                "M2": "M2 linear", "M4": "M4 published",
                                                                "M7": "M7 Cabello"}[v])
                _ = y
            bp = R[(R.family == fam) & (R.declust == decl) & (R.mc == "b-positive") & (R.variant == "M0")
                   & (R["match"] == "baseline") & (R["loc"] == "L-a")].set_index("floor")
            a.plot(bp.index, bp.b, "k:", lw=1.4, label="b-positive, M0")
            a.set_ylim(0.4, 1.8)
            a.set_title(f"{fam}{', declustered' if decl else ''}", fontsize=10)
            if j == 0:
                a.set_ylabel("b (Weichert, max. curvature table)")
    for a in ax[-1]:
        a.set_xlabel("fit floor Mw")
    ax[0, -1].legend(fontsize=7)
    fig.suptitle("Does b depend on the fit floor, and how far do the upstream choices spread it?", x=0.01, ha="left")
    io.savefig(fig, "t4_b_vs_floor", "b against fit floor per family for selected Mw variants, the spread over all "
               "combinations (grey) and b-positive")


def fig_tornado(plt, R):
    t = tornado_table(R)
    fams = list(FAMILIES)
    fig, ax = plt.subplots(2, len(fams), figsize=(4.4 * len(fams), 8), layout="constrained")
    for j, fam in enumerate(fams):
        x = t[t.family == fam]
        if not len(x):
            continue
        g = x.groupby("factor").agg(lo=("db", "min"), hi=("db", "max"), rlo=("rN6", "min"), rhi=("rN6", "max"))
        g["span"] = g.hi.clip(lower=0) - g.lo.clip(upper=0)
        g = g.sort_values("span")
        a = ax[0, j]
        a.barh(range(len(g)), g.hi.clip(lower=0), left=0, color="#e0641e")
        a.barh(range(len(g)), g.lo.clip(upper=0), left=0, color="#2166ac")
        a.set_yticks(range(len(g)), g.index, fontsize=9)
        a.axvline(0, color="0.2", lw=0.8)
        a.set_title(f"{fam}: b0 = {x.b0.iloc[0]:.2f}", fontsize=10)
        a.set_xlabel("Δb")
        a = ax[1, j]
        g = g.sort_values("span")
        a.barh(range(len(g)), np.log10(g.rhi.clip(lower=1)), color="#e0641e")
        a.barh(range(len(g)), np.log10(g.rlo.clip(upper=1)), color="#2166ac")
        a.set_yticks(range(len(g)), g.index, fontsize=9)
        a.axvline(0, color="0.2", lw=0.8)
        a.set_xlabel("log10 of N(≥ 6) ratio")
    fig.suptitle("Which upstream choice moves b and N(≥ 6) most? One-at-a-time from the X1 reference "
                 "(baseline matching, L-a, M0, full catalog, max. curvature, floor 5.0)", x=0.01, ha="left")
    io.savefig(fig, "t4_tornado", "Tornado per family: range of Δb and of the N(≥ 6) ratio for each upstream choice "
               "changed one at a time")


def fig_large(plt, R, obs):
    m = pd.read_csv(io.TAB / "t4_large_fit_vs_obs.csv")
    m = m[(m.floor == 5.0) & (m["match"] == "baseline") & (m["loc"] == "L-a")]
    fams = list(FAMILIES)
    fig, ax = plt.subplots(1, 2, figsize=(15, 6), layout="constrained")
    for a, (col, oc, q) in zip(ax, (("N7_fit", "n_obs", 7), ("N8_fit", "n_obs8", 8))):
        for i, fam in enumerate(fams):
            x = m[m.family == fam]
            for dcl, mk in ((False, "o"), (True, "s")):
                y = x[x.declust == dcl]
                a.scatter(np.full(len(y), i) + (0.15 if dcl else -0.15) + np.linspace(-0.1, 0.1, len(y)), y[col],
                          marker=mk, s=25, color=[io.palette.SERIES[int(v[1])] for v in y.variant], alpha=0.8)
            a.scatter([i], [x[oc].iloc[0]] if len(x) else [np.nan], marker="_", s=600, color="k", lw=2)
        a.set_yscale("log")
        a.set_xticks(range(len(fams)), fams, rotation=20)
        a.set_ylabel(f"N(≥ {q}) since 1904")
        a.set_title(f"M ≥ {q}: fitted (dots: M0–M8, circles full, squares declustered) vs observed (bar)", fontsize=10)
    fig.suptitle("Do the fits reproduce the large events? Floor 5.0, baseline matching, L-a", x=0.01, ha="left")
    io.savefig(fig, "t4_large_events", "Fitted against observed N(≥ 7) and N(≥ 8) since 1904 per family and Mw "
               "variant, full and declustered")


if __name__ == "__main__":
    run()

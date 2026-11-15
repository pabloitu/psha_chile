"""B9: figures from the cached results. Run after b9_1 ... b9_6. Writes figs/*.png."""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import b9_lib as L
import b9_3_fits as F
import b9_tables as TB

sys.path.insert(0, str(L.ROOT))
import palette as P

P.apply()
KL = L.FIT
NAME = dict(P.CLASS_NAME, intraslab="in-slab, shallow and intermediate", crustal="crustal, all")
COL = dict(P.CLASS_COLOR, intraslab="#a50f15", crustal="#8c6d1f")
for s in L.SEG:
    NAME[s], COL[s] = "interface, " + s.split(" ", 1)[1], P.CLASS_COLOR["interface"]
S = P.SERIES
BASE7 = "5.0 from 1964 + 7.0 from 1900 + counts"
TNAME = {"table: recent": "table: 4.5 from 2000 only", "table: isc": "table: 5.0 from 1964 only", "table: data": "table: change points",
         "table: network": "table: network", r"\+Lomnitz": " + 7.5 from 1535", r"\+counts": " + 7.5 from 1820, 8.0 from 1730",
         r"\+long": " + 7.0 from 1819, 8.0 from 1570", "M >= 7": "Mw ≥ 7"}


def save(fig, name):
    L.FIG.mkdir(exist_ok=True)
    fig.savefig(L.FIG / f"{name}.png", dpi=150, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print(name)


def grid(n, ncol=4, w=4.2, h=3.4, **kw):
    nrow = int(np.ceil(n / ncol))
    fig, ax = plt.subplots(nrow, ncol, figsize=(w * ncol, h * nrow), squeeze=False, **kw)
    for a in ax.ravel()[n:]:
        a.axis("off")
    return fig, ax.ravel()


def fig_cumulative(d):
    yc = pd.read_pickle(L.CACHE / "yearly_counts.pkl")
    yc = yc[(yc["mode"] == "all") & (yc.year >= 1960)]
    ks = KL + ["outer_rise", "antarctic_interface"]
    for basis, lab in (("full", "all events"), ("gk", "declustered (Gardner–Knopoff)")):
        fig, ax = grid(len(ks), 5, 3.6, 3.2, sharex=True)
        for a, c in zip(ax, ks):
            for i, thr in enumerate((4.5, 5.0, 5.5, 6.0)):
                q = yc[(yc.cls == c) & (yc.basis == basis) & (yc.thr == thr)]
                if q.n.sum() < 5:
                    continue
                a.plot(q.year + 1, q.n.cumsum() / q.n.sum(), color=S[i], lw=1.6, label=f"Mw ≥ {thr}")
            a.plot([1960, 2027], [0, 1], color="0.7", lw=0.7, ls=":")
            for y in L.NETWORK:
                a.axvline(y, color="0.85", lw=0.6, zorder=0)
            a.set_title(NAME[c], color=COL[c], fontsize=11)
            a.set_xlim(1960, 2027)
            a.set_ylim(0, 1)
        ax[0].legend(loc="upper left")
        fig.supylabel("share of the events since 1960")
        fig.suptitle(f"Cumulative count against time, {lab}; grey lines 1964, 1976, 1990, 2000, 2007, 2012", x=0.02, ha="left")
        fig.tight_layout()
        save(fig, f"cumulative_counts_{basis}")


def fig_large(d, W):
    ks = ["interface"] + list(L.SEG) + ["intraslab_shallow", "intraslab_intermediate", "crustal"]
    fig, ax = grid(len(ks), 4, 4.3, 3.3, sharex=True)
    t, m = d.t.to_numpy(), d.mw.to_numpy()
    for a, c in zip(ax, ks):
        for i, thr in enumerate((7.0, 7.5, 8.0)):
            s = (m >= thr - 1e-6) & (W[c] > 0)
            o = np.argsort(t[s])
            a.step(np.r_[1500, t[s][o], 2027], np.r_[0, np.cumsum(W[c][s][o]), W[c][s].sum()], where="post", color=S[i], lw=1.5,
                   label=f"Mw ≥ {thr:g}")
        for y in (1730, 1820, 1900):
            a.axvline(y, color="0.85", lw=0.6, zorder=0)
        a.set_title(NAME[c], color=COL[c], fontsize=11)
        a.set_xlim(1500, 2027)
    ax[0].legend(loc="upper left")
    fig.supylabel("cumulative count (class weights)")
    fig.suptitle("Large events against time; grey lines 1730, 1820, 1900", x=0.02, ha="left")
    fig.tight_layout()
    save(fig, "cumulative_large_events")


def tx(t):
    t = np.asarray(t, float)
    return np.where(t < 1900, (t - 1500) / 400 * 0.3, 0.3 + (t - 1900) / 127 * 0.7)


def fig_mt(d, W):
    fig, ax = grid(len(KL), 2, 8.5, 3.8)
    t, m = d.t.to_numpy(), d.mw.to_numpy()
    sty = {"network": ("-", S[3], "network history"), "data": ("--", S[2], "change points"),
           "counts": (":", S[5], "historical: counts"), "Lomnitz": ("-.", S[1], "historical: Lomnitz (2004)"),
           "long": ((0, (1, 3)), "0.3", "historical: long")}
    for a, c in zip(ax, KL):
        w = W[c]
        s = w > 0
        o = np.argsort(m[s])
        a.scatter(tx(t[s][o]), m[s][o], s=np.clip(m[s][o] - 4, 0.3, 6) ** 2 * 1.2, color=COL[c], alpha=np.clip(0.15 + 0.6 * w[s][o], 0, 0.8),
                  lw=0, rasterized=True)
        tbs = {"network": TB.NETWORK, "data": TB.data_table(c)}
        if c in TB.HIST_CLASSES:
            tbs.update({h: TB.NETWORK[-1:] + TB.HIST[h] for h in ("counts", "Lomnitz", "long")})
        for n, tb in tbs.items():
            tb = sorted(tb)
            xs, ys = [], []
            for i, (mf, y) in enumerate(tb):
                top = tb[i + 1][0] if i + 1 < len(tb) else 9.6
                xs += [tx(y), tx(y)]
                ys += [mf - 0.05, top - 0.05]
            xs, ys = [tx(2027)] + xs, [tb[0][0] - 0.05] + ys
            a.plot(xs, ys, ls=sty[n][0], color=sty[n][1], lw=1.4, label=sty[n][2])
        a.set_xticks(tx([1500, 1600, 1700, 1800, 1900, 1930, 1964, 1990, 2010]), [1500, 1600, 1700, 1800, 1900, 1930, 1964, 1990, 2010])
        a.axvline(0.3, color="0.8", lw=0.6)
        a.set_xlim(0, 1)
        a.set_ylim(4.4, 9.7)
        a.set_title(NAME[c], color=COL[c], fontsize=11)
        a.set_ylabel("Mw")
    h, l = ax[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=5)
    fig.suptitle("Magnitude against time with the candidate completeness tables (time axis stretched after 1900)", x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "magnitude_time_tables")


def fig_fmd(d, W, ks, name):
    te = L.tend(d)
    t, k = d.t.to_numpy(), d.k.to_numpy()
    m = L.centres()
    fig, ax = grid(len(ks), 4, 4.3, 3.9, sharex=True)
    for a, c in zip(ax, ks):
        hist = c in TB.HIST_CLASSES or c.startswith("seg")
        tabs = {"network history": TB.NETWORK, "change points": TB.data_table("interface" if c.startswith("seg") else c),
                "4.5 from 2000": TB.RECENT, "5.0 from 1964, 7.0 from 1900" + (" and historical" if hist else ""):
                [(5.0, 1964), (7.0, 1900)] + (TB.HIST["counts"] if hist else [])}
        for i, (n, tb) in enumerate(tabs.items()):
            r = L.fit(k, t, W[c], tb, te)
            use = r["T"] > 0
            lam = np.where(use, r["cnt"] / np.where(use, r["T"], 1), 0)
            cum = lam[::-1].cumsum()[::-1]
            if i in (0, 3):
                a.scatter(m[use & (cum > 0)], cum[use & (cum > 0)], s=14, marker="os"[i > 0], facecolor="none", edgecolor=S[i], lw=0.9, zorder=3)
            mm = np.linspace(tb[0][0] if tb is not TB.NETWORK else 4.5, 9.5, 50)
            mm = np.linspace(r["m_lo"] + 0.05, 9.5, 50)
            a.plot(mm, L.n_ge(r["b"], r["rate"], r["m_lo"], mm), color=S[i], lw=1.4, label=f"{n}: b {r['b']:.2f}")
        a.set_yscale("log")
        a.set_ylim(1e-3, 300)
        a.set_xlim(4.4, 9.6)
        a.set_title(NAME[c], color=COL[c], fontsize=11)
        a.legend(loc="lower left", fontsize=7.5)
    fig.supxlabel("Mw")
    fig.supylabel("events per year at and above Mw")
    fig.suptitle("Frequency–magnitude with Weichert fits; circles and squares: observed rates under the first and the last table", x=0.02, ha="left")
    fig.tight_layout()
    save(fig, name)


def fig_bfloor(ks, name):
    fl = pd.read_csv(L.CACHE / "fits_floors.csv")
    bp = pd.read_csv(L.CACHE / "fits_bpos.csv")
    fig, ax = grid(len(ks), 4, 4.2, 3.3, sharex=True)
    for a, c in zip(ax, ks):
        for i, (tb, basis, lab) in enumerate((("network", "full", "network table, all events"), ("data", "full", "change-point table, all events"),
                                             ("network", "gk", "network table, declustered"))):
            q = fl[(fl.cls == c) & (fl.table == tb) & (fl.basis == basis) & (fl["corr"] == "none")]
            a.plot(q.floor, q.b, color=S[i], lw=1.5, marker="o", ms=3, label=lab)
            if i == 0:
                a.fill_between(q.floor, q.b_lo, q.b_hi, color=S[i], alpha=0.15, lw=0)
        q = bp[(bp.cls == c) & (bp["mode"] == "all") & (bp.start == 1964) & (bp.dmc == 0.2)]
        if len(q):
            a.axhspan(q.b_lo.iloc[0], q.b_hi.iloc[0], color="0.6", alpha=0.25, lw=0, label="b-positive, 1964 on")
        a.set_ylim(0.4, 1.7)
        a.set_title(NAME[c], color=COL[c], fontsize=11)
    ax[0].legend(loc="lower left", fontsize=8)
    fig.supxlabel("fit floor (Mw)")
    fig.supylabel("b")
    fig.suptitle("b against the fit floor (band: 5–95 % of the bootstrap)", x=0.02, ha="left")
    fig.tight_layout()
    save(fig, name)


def fig_periods():
    p = pd.read_csv(L.CACHE / "fits_periods.csv")
    p = p[(p.basis == "full") & p.start.isin([a for a, _ in L.PERIODS]) & (p.end - p.start < 30)]
    fig, ax = grid(len(KL), 4, 4.2, 3.2, sharex=True)
    lab = [f"{a}–{str(b - 1)[2:]}" for a, b in L.PERIODS]
    for a, c in zip(ax, KL):
        for i, fl in enumerate((4.5, 5.0, 5.5)):
            q = p[(p.cls == c) & (p.floor == fl)].sort_values("start")
            x = np.arange(len(q)) + (i - 1) * 0.2
            ok = q.n.to_numpy() >= 20
            a.errorbar(x[ok], q.b[ok], yerr=[(q.b - q.b_lo)[ok], (q.b_hi - q.b)[ok]], fmt="o", ms=4, color=S[i], lw=1, label=f"floor {fl}")
        a.set_xticks(range(len(lab)), lab, fontsize=8)
        a.set_ylim(0.3, 1.8)
        a.set_title(NAME[c], color=COL[c], fontsize=11)
    ax[0].legend(loc="lower right", fontsize=8)
    fig.supylabel("b")
    fig.suptitle("b per period, all events (periods with at least 20 events)", x=0.02, ha="left")
    fig.tight_layout()
    save(fig, "b_per_period")


def fig_big():
    f = pd.read_csv(L.CACHE / "fits_main.csv")
    f = f[(f["mode"] == "all") & (f.basis == "full") & (f["corr"] == "none")]
    g = pd.read_csv(L.CACHE / "fits_below.csv")
    g = g[(g["mode"] == "all") & (g.basis == "full") & (g["corr"] == "none") & (g.top == 7.0)]
    x = pd.read_csv(L.TAB / "deeper_windows.csv")
    x = x[(x["mode"] == "all") & x.table.isin(["5.0 from 1964 + 7.0 from 1900", BASE7])]
    f = pd.concat([f, x])
    order = ["recent", "isc", "network", "data", "network+counts", "network+Lomnitz", "network+long", "5.0 from 1964 + 7.0 from 1900", BASE7]
    short = ["4.5 from 2000", "5.0 from 1964", "network", "change points", "network + counts", "network + Lomnitz", "network + long",
             "5.0 from 1964,\n7.0 from 1900", "… + counts"]
    ks = ["interface"] + list(L.SEG) + ["intraslab_shallow", "intraslab_intermediate", "forearc", "backarc", "crustal"]
    for M in ("7", "8"):
        fig, ax = grid(len(ks), 5, 3.9, 3.9)
        for a, c in zip(ax, ks):
            for i, tb in enumerate(order):
                q = f[(f.cls == c) & (f.table == tb)]
                if not len(q):
                    continue
                e, o = q["exp" + M].iloc[0], q["obs" + M].iloc[0]
                lo, hi = stats.poisson.ppf([0.05, 0.95], max(e, 1e-9))
                ok = lo - 0.5 <= o <= hi + 0.5
                a.plot([lo, hi], [i, i], color=S[0], lw=5, alpha=0.35, solid_capstyle="butt")
                a.plot(e, i, "|", color=S[0], ms=10, mew=2)
                a.plot(o, i, "o", color=S[2] if ok else S[3], ms=6)
                h = g[(g.cls == c) & (g.table == tb)]
                if len(h):
                    a.plot(h["exp" + M].iloc[0], i, "|", color="0.4", ms=8, mew=1.2)
            a.set_yticks(range(len(order)), short if a in ax[::5] else [], fontsize=8)
            a.set_ylim(len(order) - 0.5, -0.5)
            a.set_xlim(left=0)
            a.set_title(NAME[c], color=COL[c], fontsize=10.5)
        fig.supxlabel(f"number of events of Mw ≥ {M} inside each table")
        fig.suptitle(f"Large-event check, Mw ≥ {M}: fitted count with its Poisson 5–95 % band (blue), observed (dot: green inside, red outside); "
                     "grey tick: fit that saw only Mw < 7", x=0.02, ha="left", fontsize=12)
        fig.tight_layout()
        save(fig, f"large_event_check_M{M}")


def fig_maps():
    import shapefile
    g = pd.read_csv(L.CACHE / "space_grid.csv")
    land = [np.array(sh.points[a:b]) for sh in shapefile.Reader(str(L.ROOT.parent / "data/shapefiles/chile.shp")).shapes()
            for a, b in zip(sh.parts, list(sh.parts[1:]) + [len(sh.points)]) if b - a > 200]
    fig, ax = plt.subplots(2, 4, figsize=(15, 15), sharex=True, sharey=True)
    for i, fam in enumerate(("interface", "in-slab")):
        for j, (col, y0, lab) in enumerate((("bstab", 1990, "Mc, b-stability"), ("bstab", 2010, "Mc, b-stability"),
                                            ("ratio", 1990, "count 4.5–4.9 over 5.0–5.4"), ("ratio", 2010, "count 4.5–4.9 over 5.0–5.4"))):
            a = ax[i, j]
            q = g[(g.fam == fam) & (g.start == y0)]
            for ln in land:
                a.plot(ln[:, 0], ln[:, 1], color="0.5", lw=0.5)
            kw = dict(cmap="viridis_r", vmin=4.5, vmax=5.1) if col == "bstab" else dict(cmap="RdYlBu", vmin=1, vmax=5)
            sc = a.scatter(q.lon, q.lat, c=q[col], s=75, marker="s", lw=0, **kw)
            a.set_title(f"{fam}, from {y0}\n{lab}", fontsize=11)
            a.set_xlim(-77.5, -64.5)
            a.set_ylim(-47, -16.5)
            a.set_aspect(1 / np.cos(np.radians(32)))
            fig.colorbar(sc, ax=a, shrink=0.5, pad=0.02)
    fig.suptitle("Completeness in space: cells of 0.5°, events within 150 km (at least 60)", x=0.02, ha="left")
    fig.tight_layout()
    save(fig, "mc_maps")


def fig_regions():
    r = pd.read_csv(L.CACHE / "space_regions.csv")
    r["ratio"] = r.n45 / r.n50.where(r.n50 >= 5)
    fig, ax = plt.subplots(1, 3, figsize=(15, 3.8))
    for a, fam in zip(ax, ("interface", "in-slab", "crustal")):
        q = r[r.fam == fam].pivot(index="region", columns="start", values="ratio").reindex(list(L.REG))
        im = a.imshow(q.to_numpy(), cmap="RdYlBu", vmin=1, vmax=5, aspect="auto")
        for (i, j), v in np.ndenumerate(q.to_numpy()):
            if np.isfinite(v):
                a.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=10)
        a.set_xticks(range(q.shape[1]), [f"{c}" for c in q.columns])
        a.set_yticks(range(len(q)), q.index if a is ax[0] else [])
        a.set_title(fam)
    fig.colorbar(im, ax=ax, shrink=0.8, label="count 4.5–4.9 over 5.0–5.4")
    fig.suptitle("Count of Mw 4.5–4.9 over Mw 5.0–5.4 per region and period (period start); about 3 for b = 1, 3.8 for b = 1.15",
                 x=0.02, ha="left", y=1.05)
    save(fig, "regions_band_ratio")


def fig_tornado():
    t = pd.read_csv(L.TAB / "tornado_N7.csv")
    gc = {"catalogue": S[0], "weights": S[5], "declustering": S[2], "magnitude error": S[4], "completeness table": S[1], "fit floor": S[3]}
    fig, ax = grid(len(KL), 4, 5.6, 6.4)
    for a, c in zip(ax, KL):
        q = t[(t.cls == c) & t.ratio.notna()].copy()
        q = q[~q.case.str.contains("old")]
        q["case"] = q.case.replace(TNAME, regex=True)
        q["dev"] = np.abs(np.log(q.ratio))
        q = q.sort_values("dev")
        a.barh(range(len(q)), q.ratio - 1, left=1, color=[gc[g] for g in q.group], height=0.7)
        b0 = q.iloc[0]
        a.axvspan(b0.N7_lo / b0.N7_base, b0.N7_hi / b0.N7_base, color="0.85", zorder=0, lw=0)
        a.axvline(1, color="0.3", lw=0.8)
        a.set_yticks(range(len(q)), q.case, fontsize=7.5)
        a.set_xscale("log")
        a.set_xlim(0.2, 5)
        a.set_xticks([0.25, 0.5, 1, 2, 4], ["0.25", "0.5", "1", "2", "4"])
        a.set_title(f"{NAME[c]}\nbaseline {b0.N7_base:.3f} per year, b {b0.b_base:.2f}", color=COL[c], fontsize=10.5)
    h = [plt.Rectangle((0, 0), 1, 1, color=v) for v in gc.values()]
    fig.legend(h, gc.keys(), loc="lower center", ncol=6)
    fig.supxlabel("N(Mw ≥ 7) over the baseline (network table, with the historical steps 'counts' for interface and in-slab; all events; no correction)", y=0.035, fontsize=11)
    fig.suptitle("What moves the fitted rate of Mw ≥ 7 (grey: 5–95 % of the baseline bootstrap)", x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save(fig, "tornado_N7")


def fig_stationarity():
    s = pd.read_csv(L.TAB / "stationarity.csv")
    s = s[(s.m_from == 5.5)]
    fig, ax = grid(len(KL), 4, 4.2, 3.2, sharex=True)
    lab = [f"{a}–{str(b - 1)[2:]}" for a, b in L.PERIODS]
    T = np.array([b - a for a, b in L.PERIODS], float)
    T[-1] = 2026.87 - 2011
    for a, c in zip(ax, KL):
        for i, (basis, nm) in enumerate((("full", "all events"), ("gk", "declustered"))):
            q = s[(s.cls == c) & (s.basis == basis)]
            if not len(q):
                continue
            r = q[[f"rate_{y}" for y, _ in L.PERIODS]].to_numpy()[0]
            mean = q.rate.iloc[0]
            lo, hi = stats.poisson.ppf(0.05, mean * T) / T, stats.poisson.ppf(0.95, mean * T) / T
            x = np.arange(len(T)) + (i - 0.5) * 0.25
            a.vlines(x, lo / mean, hi / mean, color=S[i], lw=6, alpha=0.25)
            a.plot(x, r / mean, "o", color=S[i], ms=5, label=f"{nm} (p {q.p.iloc[0]:.2f})")
        a.axhline(1, color="0.5", lw=0.6)
        a.set_xticks(range(len(lab)), lab, fontsize=8)
        a.set_ylim(0, 2.6)
        a.set_title(NAME[c], color=COL[c], fontsize=11)
        a.legend(loc="upper left", fontsize=8)
    fig.supylabel("rate of Mw ≥ 5.5 over its 1964–2026 mean")
    fig.suptitle("Stationarity of the rate of Mw ≥ 5.5 per period, with the Poisson 5–95 % band (p: chi-square against a constant rate)", x=0.02, ha="left")
    fig.tight_layout()
    save(fig, "stationarity")


def fig_decluster(d):
    r = pd.read_csv(L.TAB / "declustering_removed.csv")
    f = pd.read_csv(L.CACHE / "fits_floors.csv")
    f = f[(f.table == "network") & (f["corr"] == "none") & np.isclose(f.floor, 5.0)]
    m = pd.read_csv(L.CACHE / "fits_main.csv")
    m = m[(m.table == "isc") & (m["mode"] == "all") & (m["corr"] == "none")]
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
    x = np.arange(len(KL))
    for i, (k, lab) in enumerate((("gk", "Gardner–Knopoff"), ("nn", "nearest neighbour"))):
        q = r[(r.m_from == 4.5)].set_index("cls").reindex(KL)
        ax[0].bar(x + (i - 0.5) * 0.38, q[k], 0.36, color=S[i], label=lab)
        q = r[(r.m_from == 5.5)].set_index("cls").reindex(KL)
        ax[0].plot(x + (i - 0.5) * 0.38, q[k], "_", color="k", ms=12, mew=1.5)
    ax[0].set_title("share of the events removed (bars Mw ≥ 4.5, marks Mw ≥ 5.5)")
    for i, (k, lab) in enumerate((("full", "all events"), ("gk", "Gardner–Knopoff"), ("nn", "nearest neighbour"))):
        q = m[m.basis == k].set_index("cls").reindex(KL)
        ax[1].errorbar(x + (i - 1) * 0.22, q.b, yerr=[q.b - q.b_lo, q.b_hi - q.b], fmt="o", color=["0.2", S[0], S[1]][i], ms=5, lw=1, label=lab)
        ax[2].errorbar(x + (i - 1) * 0.22, q.N7, yerr=[q.N7 - q.N7_lo, q.N7_hi - q.N7], fmt="o", color=["0.2", S[0], S[1]][i], ms=5, lw=1, label=lab)
    ax[1].set_title("b, Mw ≥ 5.0 from 1964")
    ax[2].set_title("fitted rate of Mw ≥ 7 per year, Mw ≥ 5.0 from 1964")
    ax[2].set_yscale("log")
    for a in ax:
        a.set_xticks(x, [NAME[c].replace(", ", ",\n") for c in KL], fontsize=8)
        a.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "declustering")
    dc = pd.read_pickle(L.CACHE / "decluster.pkl")
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    e = np.log10(dc.eta[np.isfinite(dc.eta) & (d.t.to_numpy() >= 1964)])
    ax[0].hist(e, bins=80, color=S[0])
    ax[0].axvline(dc.attrs["thr"], color=S[3])
    ax[0].set_xlabel("log10 of the nearest-neighbour distance η")
    ax[0].set_title("nearest-neighbour distances, 1964 on (red: threshold)")
    k = np.isfinite(dc.eta) & (d.t.to_numpy() >= 1964)
    ax[1].scatter(np.log10(dc.nn_T[k]), np.log10(dc.nn_R[k]), s=2, color=S[0], alpha=0.3, lw=0, rasterized=True)
    xs = np.linspace(-8, 0, 10)
    ax[1].plot(xs, dc.attrs["thr"] - xs, color=S[3])
    ax[1].set_xlabel("log10 rescaled time")
    ax[1].set_ylabel("log10 rescaled distance")
    ax[1].set_title("rescaled time and distance to the parent")
    fig.tight_layout()
    save(fig, "nearest_neighbour")


def fig_weights_corr():
    w = pd.read_csv(L.TAB / "weights_effect.csv")
    e = pd.read_csv(L.TAB / "error_correction.csv")
    w, e = w[w.table == "network"].set_index("cls").reindex(KL), e[e.table == "network"].set_index("cls").reindex(KL)
    x = np.arange(len(KL))
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
    ax[0].bar(x - 0.3, w.n_ratio, 0.28, color="0.6", label="events used")
    ax[0].bar(x, w.N5_ratio, 0.28, color=S[0], label="N(Mw ≥ 5)")
    ax[0].bar(x + 0.3, w.N7_ratio, 0.28, color=S[1], label="N(Mw ≥ 7)")
    ax[0].set_title("weight-1 events only, over all events")
    ax[1].plot(x - 0.1, w.b_all, "o", color="0.2", label="all events")
    ax[1].plot(x + 0.1, w.b_w1, "o", color=S[5], label="weight-1 events only")
    ax[1].set_title("b, network table")
    for i, (k, lab) in enumerate((("ceus", "CEUS-SSC: move and count N*"), ("plain", "plain weight"))):
        ax[2].bar(x + (i - 0.5) * 0.4 - 0.1, e[f"N5_{k}_ratio"], 0.18, color=S[i], label=f"{lab}, N(Mw ≥ 5)")
        ax[2].bar(x + (i - 0.5) * 0.4 + 0.1, e[f"N7_{k}_ratio"], 0.18, color=S[i], alpha=0.5, label=f"{lab}, N(Mw ≥ 7)")
    ax[2].set_title("magnitude-error correction over no correction")
    ax[2].set_ylim(0.5, 1.05)
    for a in ax:
        a.set_xticks(x, [NAME[c].replace(", ", ",\n") for c in KL], fontsize=8)
        a.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    save(fig, "weights_and_error_correction")


def fig_hist():
    f = pd.read_csv(L.CACHE / "fits_main.csv")
    f = f[(f["mode"] == "all") & (f.basis == "full") & (f["corr"] == "none")]
    x = pd.read_csv(L.TAB / "deeper_windows.csv")
    x = x[x["mode"] == "all"]
    ks = ["interface"] + list(L.SEG)
    tabs = [("network", "network, Mw ≥ 7 from 1900"), ("network+Lomnitz", "+ 7.5 from 1535 (Lomnitz 2004)"), ("network+counts", "+ 7.5 from 1820, 8.0 from 1730"),
            ("network+long", "+ 7.0 from 1819, 8.0 from 1570"), ("network+old", "+ 8.3 from 1513 (psha_chile6)"),
            ("5.0 from 1964 + 7.0 from 1900", "5.0 from 1964, 7.0 from 1900"), (BASE7, "5.0 from 1964, 7.0 from 1900, 7.5 from 1820, 8.0 from 1730")]
    fig, ax = plt.subplots(2, len(ks), figsize=(4.0 * len(ks), 7.6), sharey="row")
    for j, c in enumerate(ks):
        for r, M in enumerate(("7.5", "8")):
            a = ax[r, j]
            for i, (tb, lab) in enumerate(tabs):
                q = pd.concat([f[(f.cls == c) & (f.table == tb)], x[(x.cls == c) & (x.table == tb)]])
                if not len(q):
                    continue
                q = q.iloc[0]
                a.errorbar(i, q["N" + M], yerr=[[q["N" + M] - q[f"N{M}_lo"]], [q[f"N{M}_hi"] - q["N" + M]]] if M == "8" else None, fmt="o",
                           color=S[i], ms=6, lw=1.2, label=lab if (r == 0 and j == 0) else None)
                o, T = q["obs" + M], q["T" + M]
                a.plot(i, o / T, "_", color="k", ms=14, mew=1.6)
            a.set_yscale("log")
            a.set_xticks([])
            a.set_title(f"{NAME[c]}, Mw ≥ {M}", fontsize=10.5)
    ax[0, 0].set_ylabel("events per year")
    ax[1, 0].set_ylabel("events per year")
    fig.legend(loc="lower center", ncol=3, fontsize=9)
    fig.suptitle("Historical tables: fitted rate of Mw ≥ 7.5 and Mw ≥ 8 (dots), and the observed count over the years the table covers (black marks)", x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    save(fig, "historical_tables_rates")


def fig_era():
    e = pd.read_csv(L.TAB / "deeper_large_by_era.csv")
    eras = [(1900, 1930), (1930, 1964), (1964, 1976), (1976, 2000), (2000, 2026.87)]
    ks = ["interface", "intraslab_shallow", "intraslab_intermediate", "crustal"]
    fig, ax = plt.subplots(1, len(ks), figsize=(4.3 * len(ks), 4), sharey=True)
    for a, c in zip(ax, ks):
        for i, M in enumerate((6.5, 7.0, 7.5)):
            q = e[(e.cls == c) & (e.m_from == M)].iloc[0]
            n = np.array([q[f"n_{y}"] for y, _ in eras])
            T = np.array([b - y for y, b in eras])
            lo, hi = stats.chi2.ppf(0.05, 2 * np.maximum(n, 1e-9)) / 2, stats.chi2.ppf(0.95, 2 * (n + 1)) / 2
            x = np.arange(len(eras)) + (i - 1) * 0.22
            a.errorbar(x, np.maximum(n / T, 2e-3), yerr=[np.clip(n - lo, 0, None) / T, (hi - n) / T], fmt="o", color=S[i], ms=5, lw=1, label=f"Mw ≥ {M:g}")
        a.set_yscale("log")
        a.set_ylim(1.5e-3, 3)
        a.set_xticks(range(len(eras)), ["1900–29", "1930–63", "1964–75", "1976–99", "2000–26"], fontsize=9)
        a.set_title(NAME[c], color=COL[c], fontsize=11)
    ax[0].legend(loc="lower left")
    ax[0].set_ylabel("events per year")
    fig.suptitle("Rate of the large events per era (class weights; bars: Poisson 5–95 %)", x=0.02, ha="left")
    fig.tight_layout()
    save(fig, "large_events_per_era")


def fig_windows():
    x = pd.read_csv(L.TAB / "deeper_windows.csv")
    x = x[(x["mode"] == "all") & x.b.notna()]
    ks = ["interface", "intraslab_intermediate", "intraslab_shallow", "forearc"]
    fig, ax = plt.subplots(1, len(ks), figsize=(4.6 * len(ks), 5), sharey=True)
    for a, c in zip(ax, ks):
        q = x[x.cls == c].reset_index(drop=True)
        col = [S[2] if v else S[3] for v in q.in7]
        a.hlines(range(len(q)), q.b_lo, q.b_hi, color=col, lw=2)
        a.scatter(q.b, range(len(q)), color=col, s=28, zorder=3)
        for i, r in q.iterrows():
            a.text(1.42, i, f"{r.exp7:.0f} / {r.obs7:.0f}", va="center", fontsize=8)
        a.set_yticks(range(len(q)), q.table if a is ax[0] else [], fontsize=8.5)
        a.set_ylim(len(q) - 0.5, -0.5)
        a.set_xlim(0.8, 1.6)
        a.set_title(NAME[c], color=COL[c], fontsize=11)
        a.set_xlabel("b")
    fig.suptitle("One window against mixed windows: b (5–95 %), and fitted / observed count of Mw ≥ 7 inside the table (green: inside the Poisson band)",
                 x=0.02, ha="left")
    fig.tight_layout()
    save(fig, "tables_one_window_or_mixed")


ONLY = None


def run():
    d = L.load()
    W = F.classes(d)
    if ONLY:
        for f in ONLY:
            globals()[f]() if f not in ("fig_decluster",) else globals()[f](d)
        return
    fig_cumulative(d)
    fig_large(d, W)
    fig_mt(d, W)
    fig_fmd(d, W, KL, "frequency_magnitude_classes")
    fig_fmd(d, W, list(L.SEG) + ["intraslab", "crustal", "outer_rise", "antarctic_interface"], "frequency_magnitude_segments")
    fig_bfloor(KL, "b_against_floor_classes")
    fig_bfloor(list(L.SEG) + ["intraslab", "crustal"], "b_against_floor_segments")
    fig_periods()
    fig_big()
    fig_maps()
    fig_regions()
    fig_tornado()
    fig_stationarity()
    fig_decluster(d)
    fig_weights_corr()
    fig_hist()
    fig_era()
    fig_windows()


if __name__ == "__main__":
    run()

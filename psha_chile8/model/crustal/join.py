"""S3 step 3: the join of faults and background (DECISIONS, Crustal and faults) and its check against the catalogue.

Per crustal class the background is the catalogue fit below Mw 6.0 and, from the bin 6.0 on, the fit minus the summed
fault MFD of the class (weighted mean over the fault tree), bin by bin, and zero from the first bin where the faults
reach the fit (Pablo, 15 Nov: the background does not come back above the faults). The background keeps its
smoothed pattern everywhere. Where the faults alone exceed the fit (the bulge) the background is zero and the faults
set the rate. The no-faults baseline is the full fit (LEARNINGS).

Writes tables/background_mfd_<DATE>.csv (the lists of every database, shape and class), tables/join_<DATE>.csv,
tables/jump_<DATE>.csv, tables/events_near_faults_<DATE>.csv, tables/cities_<DATE>.csv and figs/mfd_<db>_<DATE>.png,
figs/fault_share_<DATE>.png.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import background as BG
import faults as F

sys.path.insert(0, str(F.ROOT / "model" / "faults"))
import geo  # noqa: E402
import gr  # noqa: E402
from chaf import CITIES  # noqa: E402

TAB, FIG = F.HERE / "tables", F.HERE / "figs"

# settings
DATE = "2026-11-16e"
MJOIN = 6.0
REF = (6.0, 6.5, 7.0)
NEAR_EVENT_KM, NEAR_CITY_KM = 10.0, 50.0
SHARE_CELL = 0.5
CENTRES = np.round(BG.MMIN + gr.DM * np.arange(50), 2)
DB_NAMES = F.NAMES


def on(c, r):
    """Rates on CENTRES."""
    out = np.zeros(CENTRES.size)
    k = np.rint((np.asarray(c) - CENTRES[0]) / gr.DM).astype(int)
    np.add.at(out, k, r)
    return out


def fits():
    return {(c, sh): on(*BG.mfd(c, sh)) for c in BG.CLASSES for sh in BG.SHAPES}


def fault_classes():
    """Per database and class: weighted-mean rates on CENTRES and the branch rates (branches, CENTRES)."""
    s = pd.read_csv(TAB / f"fault_sources_{DATE}.csv")
    out = {}
    for db, (base, _) in F.VARIANTS.items():
        z = np.load(TAB / f"fault_rates_{db}_{DATE}.npz", allow_pickle=True)
        cls = s[s.db == base].set_index("fid").loc[z["fid"], "cls"].to_numpy()
        k = np.rint((F.R.MMIN - CENTRES[0]) / gr.DM).astype(int)
        for c in BG.CLASSES:
            br = np.zeros((len(F.BR), CENTRES.size))
            br[:, k:k + F.NB] = z["rates"][cls == c].sum(axis=0)[:, :CENTRES.size - k]
            out[(db, c)] = (z["weights"] @ br, br)
    return out


def background(fit, fault):
    """
    The join: the fit below MJOIN; from the bin MJOIN on, fit - faults, and zero from the first bin where the faults
    reach the fit (the background does not come back above the faults; Pablo, 15 Nov).
    """
    up = CENTRES >= MJOIN - 1e-6
    full = up & (fault >= fit) & (fault > 0)
    stop = CENTRES >= CENTRES[full].min() - 1e-6 if full.any() else np.zeros(CENTRES.size, bool)
    return np.where(up, np.where(stop, 0.0, np.maximum(fit - fault, 0.0)), fit)


def nge(r, M):
    return float(r[CENTRES >= M - 1e-6].sum())


def mom(r):
    return float((r * gr.moment(CENTRES)).sum())


def observed():
    """Yearly observed rate per bin and class inside the completeness table (full catalogue, class weight times
    the magnitude-error count with the class b), on CENTRES, and per completeness period for the figures."""
    d = gr.load(BG.CAT, mlow=BG.MMIN)
    te = gr.tend(gr.load(BG.CAT))
    yr, T = gr.table_years(BG.TABLE, te)
    k = gr.kbin(d.mw)
    b = F.bvals()
    out, per = {}, {}
    for c in BG.CLASSES:
        w = d[f"W_{c}"].to_numpy() * gr.magw(d.mw_sigma.to_numpy(), b[c])
        ok = (w > 0) & (d.t.to_numpy() >= yr[k])
        n = np.bincount(k[ok], w[ok], minlength=yr.size)
        r = np.where(T > 0, n / np.where(T > 0, T, 1), 0.0)
        out[c] = on(gr.centres()[gr.centres() >= BG.MMIN - 1e-6], r[gr.centres() >= BG.MMIN - 1e-6])
        pp = []
        ends = [te] + [y for _, y in sorted(BG.TABLE)[:-1]]
        for (mc, y0), y1 in zip(sorted(BG.TABLE), ends):
            s = ok & (d.t.to_numpy() >= y0) & (d.t.to_numpy() < y1) & (d.mw.to_numpy() >= mc - 1e-6)
            m = np.sort(np.unique(np.round(d.mw.to_numpy()[s], 1)))
            if len(m):
                pp.append((f"{y0:.0f}–{int(min(y1, te))}, Mw ≥ {mc:g}", m,
                           np.array([w[s & (d.mw.to_numpy() >= x - 1e-6)].sum() for x in m]) / (min(y1, te) - y0)))
        per[c] = pp
    return out, per


def bulge(fit, fault):
    up = (CENTRES >= MJOIN - 1e-6) & (fault > fit)
    ex = np.where(up, fault - fit, 0.0)
    bins = CENTRES[up]
    txt = "" if not up.any() else f"{bins.min():.1f}–{bins.max():.1f}" + ("" if np.all(np.diff(bins) < 0.15) else " (gaps)")
    return txt, ex


def tables(ft, fc, obs):
    rows, jump, mfds = [], [], []
    for db in list(F.VARIANTS) + ["none"]:
        for sh in BG.SHAPES:
            for c in BG.CLASSES:
                fm = fc[(db, c)][0] if db != "none" else np.zeros(CENTRES.size)
                bg = background(ft[(c, sh)], fm)
                for m, r in zip(CENTRES, bg):
                    if r > 0:
                        mfds.append(dict(db=db, shape=sh, cls=c, mag=m, rate=r))
    mfd = pd.DataFrame(mfds)
    for db in F.VARIANTS:
        tot = {}
        for c in list(BG.CLASSES) + ["all"]:
            cs = list(BG.CLASSES) if c == "all" else [c]
            fm = sum(fc[(db, k)][0] for k in cs)
            fb = sum(fc[(db, k)][1] for k in cs)
            ob = sum(obs[k] for k in cs)
            for sh in BG.SHAPES:
                fit = sum(ft[(k, sh)] for k in cs)
                bg = sum(background(ft[(k, sh)], fc[(db, k)][0]) for k in cs)
                txt, ex = (bulge(fit, fm) if c != "all" else
                           ("", sum(bulge(ft[(k, sh)], fc[(db, k)][0])[1] for k in BG.CLASSES)))
                if c == "all":
                    txt = "; ".join(f"{k}: {bulge(ft[(k, sh)], fc[(db, k)][0])[0]}" for k in BG.CLASSES
                                    if bulge(ft[(k, sh)], fc[(db, k)][0])[0])
                for M in REF:
                    fb_ = fb[:, CENTRES >= M - 1e-6].sum(axis=1)
                    rows.append(dict(db=db, cls=c, shape=sh, M=M, fit=nge(fit, M), observed=nge(ob, M),
                                     faults=nge(fm, M), faults_lo=fb_.min(), faults_hi=fb_.max(), background=nge(bg, M),
                                     total=nge(bg + fm, M), ratio=nge(bg + fm, M) / nge(fit, M), bulge_bins=txt,
                                     bulge_N=nge(ex, M), bulge_mo=mom(np.where(CENTRES >= M - 1e-6, ex, 0.0)),
                                     fit_mo=mom(np.where(CENTRES >= M - 1e-6, fit, 0.0))))
                i5, i6 = np.argmin(np.abs(CENTRES - 5.9)), np.argmin(np.abs(CENTRES - 6.0))
                jump.append(dict(db=db, cls=c, shape=sh, fit59=fit[i5], fit60=fit[i6], bg59=bg[i5], bg60=bg[i6],
                                 faults60=fm[i6], total60=bg[i6] + fm[i6], step=(bg[i6] + fm[i6]) / bg[i5]))
    return pd.DataFrame(rows), pd.DataFrame(jump), mfd


def near_events():
    """Events of Mw >= 6 with a crustal weight within NEAR_EVENT_KM of a fault trace of A or B."""
    d = gr.load(BG.CAT, mlow=6.0)
    w = d[[f"W_{c}" for c in BG.CLASSES]]
    d = d[w.sum(axis=1) > 0].copy()
    d["cls"] = w.loc[d.index].idxmax(axis=1).str[2:]
    d["w_crustal"] = w.loc[d.index].sum(axis=1)
    rows = []
    srcs = {db: F.read(db) for db in ("A", "B")}
    trees = {db: [geo.tree(g, 0.5) for g in f.geometry] for db, f in srcs.items()}
    for e in d.itertuples():
        o = dict(event_id=e.event_id, year=int(e.time[:4]), date=e.time[:10], mw=e.mw, cls=e.cls, w_crustal=e.w_crustal,
                 lon=e.lon, lat=e.lat)
        hit = False
        for db, f in srcs.items():
            p = geo.xyz(np.array([[e.lon, e.lat]]))
            dd = np.array([t.query(p)[0][0] for t in trees[db]])
            j = int(np.argmin(dd))
            o[f"fault_{db}"], o[f"km_{db}"] = f["name"].iloc[j], float(dd[j])
            hit |= dd[j] <= NEAR_EVENT_KM
        if hit:
            rows.append(o)
    return pd.DataFrame(rows).sort_values("mw", ascending=False)


def fault_points(db, rates_n6):
    """Points along the traces of the sources of a database (1 km) with their share of the source N(>= 6)."""
    s, _, _ = F.load(db) if not isinstance(db, tuple) else db
    pts, val = [], []
    from shapely.geometry import LineString
    for q, n in zip(s.itertuples(), rates_n6):
        p, w = geo.dense(LineString(q.trace), 1.0)
        pts.append(p)
        val.append(n * w / w.sum())
    return np.vstack(pts), np.concatenate(val)


def cities(fc, ft, pats, pts):
    """Per city and database: fault N(>= 6) within NEAR_CITY_KM (the share of each trace inside), background N(>= 6)
    there (tapered fits, both declustering options), and the fault share."""
    import smooth as S
    rows = []
    g = pats["gk"]
    for city, (lon, lat) in CITIES.items():
        d = S.hav(g.lon.to_numpy(), g.lat.to_numpy(), lon, lat) <= NEAR_CITY_KM
        o = dict(city=city)
        for db in list(F.VARIANTS) + ["none"]:
            bg = 0.0
            for m, wm in BG.W_DECL.items():
                for c in BG.CLASSES:
                    fm = fc[(db, c)][0] if db != "none" else np.zeros(CENTRES.size)
                    bg += wm * pats[m][c].to_numpy()[d].sum() * nge(background(ft[(c, "taper")], fm), 6.0)
            o[f"bg_{db}"] = bg
            if db != "none":
                p, v = pts[db]
                fl = float(v[S.hav(p[:, 0], p[:, 1], lon, lat) <= NEAR_CITY_KM].sum())
                o[f"faults_{db}"], o[f"share_{db}"] = fl, fl / (fl + bg) if fl + bg > 0 else np.nan
                o[f"total_{db}"] = fl + bg
        rows.append(o)
    return pd.DataFrame(rows)


def figures(ft, fc, obs, per, pats, pts):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(F.ROOT))
    import palette as P
    P.apply()
    t = pd.read_csv(BG.FITS)
    cum = lambda r: np.cumsum(r[::-1])[::-1]
    for db in F.VARIANTS:
        f, ax = plt.subplots(2, 2, figsize=(13, 10), sharex=True)
        for a, c in zip(ax.ravel(), BG.CLASSES):
            fit = ft[(c, "taper")]
            r = t[(t.unit == c) & (t["shape"] == "taper")].iloc[0]
            ms = np.array([5.0, 6.0, 7.0])
            lo = np.interp(CENTRES, ms, np.log10([r.N5_lo / r.N5, r.N6_lo / r.N6, r.N7_lo / r.N7]))
            hi = np.interp(CENTRES, ms, np.log10([r.N5_hi / r.N5, r.N6_hi / r.N6, r.N7_hi / r.N7]))
            cf = cum(fit)
            a.fill_between(CENTRES - 0.05, cf * 10 ** lo, cf * 10 ** hi, color="0.85", lw=0, label="fit, 5–95 %")
            a.plot(CENTRES - 0.05, cf, color="0.3", lw=1.6, label="fit, tapered")
            a.plot(CENTRES - 0.05, cum(ft[(c, "trunc")]), color="0.3", lw=1.0, ls="--", label="fit, cut at Mmax")
            for i, (lab, m, n) in enumerate(per[c]):
                a.plot(m - 0.05, n, "o", ms=4, color=P.SERIES[i], mfc="none" if i else P.SERIES[i], label=lab)
            fm, fb = fc[(db, c)]
            cb = np.array([cum(x) for x in fb])
            a.fill_between(CENTRES - 0.05, cb.min(0), cb.max(0), color=P.SERIES[1], alpha=0.15, lw=0)
            a.plot(CENTRES - 0.05, cum(fm), color=P.SERIES[1], lw=1.8, label="faults, mean and range")
            bg = background(fit, fm)
            a.plot(CENTRES - 0.05, cum(bg), color=P.CLASS_COLOR[c], lw=1.8, label="background")
            a.plot(CENTRES - 0.05, cum(bg + fm), color="k", lw=2.2, ls=":", label="faults + background")
            a.set_yscale("log")
            a.set_ylim(1e-5, 10)
            a.set_xlim(4.9, 8.9)
            a.set_title(P.CLASS_NAME[c])
            a.set_ylabel("N(≥ Mw) per year")
        for a in ax[1]:
            a.set_xlabel("Mw")
        ax[0, 0].legend(loc="lower left", fontsize=8.5)
        f.suptitle(f"Crustal MFDs, fault database {DB_NAMES[db]}", x=0.07, ha="left")
        f.tight_layout()
        f.savefig(FIG / f"mfd_{db}_{DATE}.png", dpi=160)
        plt.close(f)

    g = pats["gk"]
    e = np.arange(-80, -59.9, SHARE_CELL), np.arange(-58, -16.9, SHARE_CELL)
    f, ax = plt.subplots(1, 3, figsize=(15, 11), sharey=True)
    for a, db in zip(ax, F.DBS):
        bg = np.zeros(len(g))
        for m, wm in BG.W_DECL.items():
            for c in BG.CLASSES:
                bg += wm * pats[m][c].to_numpy() * nge(background(ft[(c, "taper")], fc[(db, c)][0]), 6.0)
        hb = np.histogram2d(g.lon, g.lat, e, weights=bg)[0]
        p, v = pts[db]
        hf = np.histogram2d(p[:, 0], p[:, 1], e, weights=v)[0]
        sh = np.where(hb + hf > 0, hf / np.where(hb + hf > 0, hb + hf, 1), np.nan)
        sh[np.histogram2d(g.lon, g.lat, e)[0] == 0] = np.nan
        im = a.pcolormesh(e[0], e[1], sh.T, cmap="viridis", vmin=0, vmax=1, rasterized=True)
        a.plot(p[:, 0], p[:, 1], ",", color="w", alpha=0.6)
        a.set_aspect(1 / np.cos(np.radians(37)))
        a.set_xlim(-77, -64)
        a.set_ylim(-56.5, -17)
        a.set_title(DB_NAMES[db])
        for city, (lo_, la_) in CITIES.items():
            a.plot(lo_, la_, "s", ms=3, color="crimson")
    f.colorbar(im, ax=ax, shrink=0.5, label="fault share of N(Mw ≥ 6), 0.5° cells")
    f.savefig(FIG / f"fault_share_{DATE}.png", dpi=160, bbox_inches="tight")
    plt.close(f)


def main():
    ft, fc = fits(), fault_classes()
    obs, per = observed()
    jt, jump, mfd = tables(ft, fc, obs)
    mfd.to_csv(TAB / f"background_mfd_{DATE}.csv", index=False, float_format="%.6e")
    jt.round(6).to_csv(TAB / f"join_{DATE}.csv", index=False)
    jump.round(6).to_csv(TAB / f"jump_{DATE}.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_colwidth", 40):
        x = jt[(jt["shape"] == "taper")]
        print(x[["db", "cls", "M", "fit", "observed", "faults", "faults_lo", "faults_hi", "background", "total", "ratio",
                 "bulge_bins", "bulge_N"]].round(4).to_string(index=False))
        print(jump[jump["shape"] == "taper"].round(4).to_string(index=False))
    ne = near_events()
    ne.round(3).to_csv(TAB / f"events_near_faults_{DATE}.csv", index=False)
    print(ne.round(2).to_string(index=False))
    pats = {m: pd.read_csv(TAB / f"pattern_{m}_{DATE}.csv") for m in BG.DECL}
    s = pd.read_csv(TAB / f"fault_sources_{DATE}.csv")
    pts = {}
    for base in F.DBS:
        L = F.load(base)
        x = s[s.db == base].set_index("fid").loc[L[0].fid]
        pts[base] = fault_points(L, x["N6"].to_numpy())
        pts[base + "_cm"] = fault_points(L, x["N6_clsmax"].to_numpy())
    ct = cities(fc, ft, pats, pts)
    ct.round(6).to_csv(TAB / f"cities_{DATE}.csv", index=False)
    with pd.option_context("display.width", 250):
        print(ct.round(4).to_string(index=False))
    figures(ft, fc, obs, per, pats, pts)


if __name__ == "__main__":
    main()

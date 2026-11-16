"""Checks of the crustal model against the catalogue (S3): the multi-fault trade-off, a map of the Liquine-Ofqui
multi-fault ruptures, the fault share of N(>= 6) per cell, counts at several magnitudes, moment rates per class, and
the fault share against the share of observed events near faults. Writes figs/<DATE>/check_*.png."""
import numpy as np
import pandas as pd
from scipy import stats

import background as BG
import faults as F
import join as J
import multifault as MF
import gr
from figs_s3 import BASEMAP, DH, FIG, plt_, save
import palette

# basemap of the scenario pages (Pablo may point it to one without the trench)
SCEN_BASEMAP = BASEMAP
DB_COLOR = {"A": palette.SERIES[0], "B": palette.SERIES[1], "Bmm": palette.SERIES[2]}
DB_NAME = {"A": "A", "B": "B", "Bmm": "B, MASCSN moment"}
# observation windows per magnitude: the crustal table (5.0 from 1976) and the historical steps (MF.HIST), out of the fit
WIN = ((5.0, 1976.0),) + MF.HIST
MS = (5.0, 5.5, 6.0, 6.5, 7.0, 7.5)
NEAR_KM = 20.0
JUMP, PSI_MAP = 15.0, 0.8


def start(M):
    """Start year of the observation window of magnitude M: the step of the largest magnitude not above M."""
    return max((m, y) for m, y in WIN if M >= m - 1e-6)[1]


def data():
    """Catalogue, end time, fits, faults per class and variant, and the A multi-fault MFDs (psi-weighted mean)."""
    d = gr.load(BG.CAT, mlow=4.95)
    te = gr.tend(gr.load(BG.CAT))
    ft, fc = J.fits(), J.fault_classes()
    z = np.load(BG.TAB / f"mf_A_lofs_mfd_{BG.DATE}.npz")
    w = {p: F.R.PSI[p] for p in MF.PSIS}
    mf = {dz: sum(w[p] * z[f"j{JUMP:g}_z{dz:g}_psi{p:g}"].mean(0) for p in w) / sum(w.values()) for dz in MF.DEPTHS_LOFS}
    return d, te, ft, fc, mf


def models(c, ft, fc, mf):
    """Total crustal MFD of class c on J.CENTRES for every model of the checks."""
    fit = ft[(c, "taper")]
    out = {"catalogue fit": ("0.45", "o", fit)}
    for db in F.DBS:
        fm = fc[(db, c)][0]
        out[f"{DB_NAME[db]}, single faults"] = (DB_COLOR[db], "o", fm + J.background(fit, fm))
    if c == "arc":
        for dz, m in mf.items():
            out[f"A, multi-fault, {dz:g} km"] = (palette.SERIES[4], "D" if dz > 10 else "s", m + J.background(fit, m))
    return out


def tradeoff():
    """Expected arc Mw >= 6 since 1976 against Mw >= 7 since 1905 for every multi-fault case and the single faults,
    with the observed counts and the range of expectations they allow (Poisson 5-95 %)."""
    import arc
    plt = plt_()
    d, te, ft, fc, mf = data()
    n, T = arc.observed()
    s6, s7 = J.CENTRES >= 5.95, J.CENTRES >= 6.95
    fit = ft[("arc", "taper")]
    t = {db: pd.read_csv(BG.TAB / f"mf_{db}_lofs_{BG.DATE}.csv").groupby(["jump", "depth", "psi"]).mean(numeric_only=True)
         for db in F.DBS}
    o6, o7 = float(t["A"].obs6.iloc[0]), float(t["A"].obs7_hist.iloc[0])
    band = lambda k: (stats.chi2.ppf(0.05, 2 * k) / 2, stats.chi2.ppf(0.95, 2 * (k + 1)) / 2)
    fig, ax = plt.subplots(figsize=(12.5, 7.5), layout="constrained")
    (a0, a1), (b0, b1) = band(round(o6)), band(round(o7))
    ax.axvspan(a0, a1, color="0.85", zorder=0)
    ax.axhspan(b0, b1, color="0.85", zorder=0)
    ax.fill_between([a0, a1], b0, b1, color="0.7", zorder=0, label="consistent with both counts (Poisson 5–95 %)")
    ax.plot(o6, o7, "*", ms=16, color="k", zorder=6, label="observed")
    for db, x in t.items():
        for (jk, dz, ps), r in x.iterrows():
            ax.scatter(r.exp6, r.exp7_hist, s=12 + r.longest_km / 6, marker="o" if dz == 10 else "s",
                       facecolor=DB_COLOR[db], edgecolor="k", lw=0.4, alpha=0.75, zorder=4)
            if ps == 0.8:
                ax.annotate(f"{jk:g}", (r.exp6, r.exp7_hist), xytext=(4, 3), textcoords="offset points", fontsize=7.5, zorder=5)
        fm = fc[(db, "arc")][0]
        tot = fm + J.background(fit, fm)
        ax.scatter(float((tot[s6] * T[s6]).sum()), float(tot[s7].sum() * (te - 1905.0)), s=140, marker="X",
                   color=DB_COLOR[db], edgecolor="k", zorder=5)
    for db in F.DBS:
        ax.scatter([], [], s=60, color=DB_COLOR[db], label=f"database {DB_NAME[db]}")
    ax.scatter([], [], s=60, marker="o", color="0.5", label="multi-fault, thickness 10 km")
    ax.scatter([], [], s=60, marker="s", color="0.5", label="multi-fault, thickness 20 km")
    ax.scatter([], [], s=100, marker="X", color="0.5", edgecolor="k", label="single faults (mean of the tree)")
    for L in (250, 500, 1000):
        ax.scatter([], [], s=12 + L / 6, color="white", edgecolor="k", lw=0.6, label=f"longest chain {L} km")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("expected arc events Mw ≥ 6, 1976–2026")
    ax.set_ylabel("expected arc events Mw ≥ 7, 1905–2026")
    ax.legend(fontsize=8.5, loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False)
    ax.set_title("Crustal arc: count tests of every fault model (numbers: jump in km, at ψ 0.8; ψ 0.6–1.0 unlabelled)",
                 loc="left", fontsize=11)
    save(fig, "check_tradeoff")


def lofs_map():
    """A, jump JUMP, psi PSI_MAP, one seed per depth: each Liquine-Ofqui trace coloured by the share of its slip rate
    released in multi-fault ruptures, width by slip rate, starved traces (NMS share over 0.3) dashed; the other arc
    faults in grey; Aysen 1960 and 1927 marked."""
    import cartopy.crs as ccrs
    import geopandas as gpd
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import Normalize
    from pituplots.maps import dress_map
    plt = plt_()
    pc = ccrs.PlateCarree()
    gpd.options.io_engine = "fiona"
    s, _, _ = F.load("A")
    sysn = gpd.read_file(F.DBS["A"]["file"]).set_index("fid")["system"]
    isl = s.fid.map(sysn).eq(MF.LOFS).to_numpy()
    sl = s[isl].reset_index(drop=True)
    MF.MIN_SR, MF.JUMP_KM, MF.PSI = MF.MAIN_SR["A"], JUMP, PSI_MAP
    ch = MF.chains(sl, MF.links(sl))
    b = F.bvals()["arc"]
    d = gr.load(BG.CAT, mlow=6.95)
    big = d[(d.W_arc > 0.3) | (d.W_patagonia > 0.3)]
    big = big[(big.lat < -38) & (big.lat > -48)]
    cm, nrm = plt.get_cmap("viridis"), Normalize(0, 1)
    fig = plt.figure(figsize=(12, 9.5), layout="constrained")
    for j, dz in enumerate(MF.DEPTHS_LOFS):
        src, mx, rate, nms = MF.run(dz, sl, ch, b, np.random.default_rng(1))
        m0 = F.R.m0(F.R.MMIN + F.R.DM * np.arange(F.NB))
        used = np.zeros(len(sl))
        for q, r in zip(src, rate):
            if len(q["members"]) > 1 and r.sum() > 0:
                slip = (r * m0).sum() / (F.R.MU * q["area"]) * 1e3
                used[list(q["members"])] += slip
        bud = MF.budget(sl, dz)
        share = np.where(bud > 0, used / bud, 0)
        ns = np.where(bud > 0, nms / bud, 0)
        ax = fig.add_subplot(1, 2, j + 1, projection=pc)
        dress_map(ax, [-76.0, -70.5, -48.0, -37.5], basemap=str(BASEMAP) if BASEMAP.exists() else None, gridlines=j == 0)
        for q in s[~isl & s.cls.isin(["arc", "patagonia"]).to_numpy()].itertuples():
            t = np.asarray(q.trace)
            ax.plot(t[:, 0], t[:, 1], color="0.45", lw=0.8, transform=pc, zorder=3)
        for i, q in enumerate(sl.itertuples()):
            t = np.asarray(q.trace)
            ax.plot(t[:, 0], t[:, 1], color=cm(nrm(share[i])), lw=0.8 + 0.5 * q.sr_used, ls="--" if ns[i] > 0.3 else "-",
                    transform=pc, zorder=4, solid_capstyle="round")
        ax.scatter(big.lon, big.lat, s=40 * 2.2 ** (big.mw - 7), marker="*", color=palette.SERIES[3], edgecolor="k",
                   lw=0.5, transform=pc, zorder=6)
        for r in big.itertuples():
            ax.annotate(f"{r.time[:4]} {r.mw:.1f}", (r.lon, r.lat), xytext=(5, -3), textcoords="offset points", fontsize=8,
                        transform=pc, zorder=7)
        lng = max((float(sl.L[list(q["members"])].sum()) for q, r in zip(src, rate) if len(q["members"]) > 1 and r.sum() > 0), default=0)
        ax.set_title(f"thickness {dz:g} km: {int(sum(1 for q, r in zip(src, rate) if len(q['members']) > 1 and r.sum() > 0))} "
                     f"chains with rate, longest {lng:.0f} km, Mmax {max(q['hi'] for q, r in zip(src, rate) if r.sum() > 0):.1f}",
                     fontsize=11)
    fig.colorbar(ScalarMappable(nrm, cm), ax=fig.axes, orientation="horizontal", shrink=0.5, pad=0.02,
                 label="share of the slip rate released in multi-fault ruptures (dashed: over 30 % not released)")
    fig.suptitle(f"Liquiñe–Ofqui multi-fault ruptures, database A, jump ≤ {JUMP:g} km, ψ {PSI_MAP:g} (width: slip rate; "
                 "grey: other faults; stars: Mw ≥ 7)", x=0.01, ha="left")
    save(fig, "check_lofs_map")


def share_map():
    """Fault share of N(>= 6) per 0.5 degree cell (faults over faults plus background), single faults of A, B and B-mm,
    tapered fits, both declustering options."""
    import cartopy.crs as ccrs
    from pituplots import plot_grid
    from pituplots.io.containers import Grid
    from pituplots.maps import dress_map
    plt = plt_()
    pc = ccrs.PlateCarree()
    d, te, ft, fc, mf = data()
    pats = {m: pd.read_csv(BG.TAB / f"pattern_{m}_{BG.DATE}.csv") for m in BG.DECL}
    g = pats["gk"]
    srcs = pd.read_csv(BG.TAB / f"fault_sources_{BG.DATE}.csv")
    e = np.arange(-80, -59.9, 0.5), np.arange(-58, -16.9, 0.5)
    fig = plt.figure(figsize=(14, 10.5), layout="constrained")
    for j, db in enumerate(F.DBS):
        bg = np.zeros(len(g))
        for m, wm in BG.W_DECL.items():
            for c in BG.CLASSES:
                bg += wm * pats[m][c].to_numpy() * J.nge(J.background(ft[(c, "taper")], fc[(db, c)][0]), 6.0)
        s, _, _ = F.load(db)
        n6 = srcs[srcs.db == db].set_index("fid").loc[s.fid, "N6"].to_numpy()
        p, v = J.fault_points((s, None, None), n6)
        hb = np.histogram2d(g.lon, g.lat, e, weights=bg)[0]
        hf = np.histogram2d(p[:, 0], p[:, 1], e, weights=v)[0]
        ok = np.histogram2d(g.lon, g.lat, e)[0] > 0
        sh = np.where(ok & (hb + hf > 0), hf / np.where(hb + hf > 0, hb + hf, 1), np.nan)
        X, Y = np.meshgrid(e[0][:-1] + 0.25, e[1][:-1] + 0.25, indexing="ij")
        k = np.isfinite(sh)
        ax = fig.add_subplot(1, 3, j + 1, projection=pc)
        dress_map(ax, [-77.0, -65.0, -56.5, -17.0], basemap=str(BASEMAP) if BASEMAP.exists() else None, gridlines=j == 0)
        plot_grid(Grid.from_points(X[k], Y[k], np.clip(sh[k], 1e-3, 1), dh=0.5), ax=ax, colorbar=False, vmin=0, vmax=1,
                  rasterized=True, zorder=3)
        fig.colorbar(ax.collections[-1], ax=ax, orientation="horizontal", shrink=0.85, pad=0.02, label="fault share of N(≥ 6)")
        ax.set_title(f"database {DB_NAME[db]}, single faults", fontsize=11)
    fig.suptitle("Crustal faults: share of the rate of Mw ≥ 6 per 0.5° cell (faults / (faults + background))", x=0.01, ha="left")
    save(fig, "check_fault_share_map")


def counts():
    """Per class: expected N(>= M) in the observation window of M (WIN) for every model, with its Poisson 5-95 %
    range, against the observed weighted count (class and magnitude-error weights)."""
    from pituplots.style.axes import darkgrid
    plt = plt_()
    d, te, ft, fc, mf = data()
    fits = pd.read_csv(BG.FITS)
    fig, axs = plt.subplots(1, 4, figsize=(19, 5.6), layout="constrained")
    for ax, c in zip(axs, BG.CLASSES):
        b = float(fits[(fits.unit == c) & (fits["shape"] == "taper")].b.iloc[0])
        w = d[f"W_{c}"].to_numpy() * gr.magw(d.mw_sigma.to_numpy(), b)
        mo = models(c, ft, fc, mf)
        dx = np.linspace(-0.15, 0.15, len(mo))
        for i, M in enumerate(MS):
            y = start(M)
            obs = float(w[(d.mw.to_numpy() >= M - 0.05) & (d.t.to_numpy() >= y)].sum())
            ax.plot([i - 0.25, i + 0.25], [obs, obs], color="k", lw=2.5, zorder=6, label="observed" if i == 0 else None)
            for x, (lab, (col, mk, r)) in zip(dx, mo.items()):
                e = J.nge(r, M) * (te - y)
                lo, hi = stats.poisson.ppf([0.05, 0.95], e)
                ax.plot([i + x, i + x], [max(lo, 0.05), max(hi, 0.05)], color=col, lw=4, alpha=0.35, zorder=3)
                ax.plot(i + x, e, mk, color=col, mec="k", mew=0.4, ms=6, zorder=4, label=lab if i == 0 else None)
        ax.set_xticks(range(len(MS)), [f"≥ {M:g}\n{start(M):.0f}–" for M in MS])
        ax.set_yscale("log")
        ax.set_ylim(0.05, 1e3)
        darkgrid(ax)
        ax.set_title(palette.CLASS_NAME[c], fontsize=12)
        ax.legend(fontsize=8, loc="upper right", frameon=False)
    axs[0].set_ylabel("events in the window (bar: Poisson 5–95 % of the model)")
    fig.suptitle("Crustal models against the catalogue: counts above each magnitude in its observation window", x=0.01, ha="left")
    save(fig, "check_counts")


def moments():
    """Per class: observed seismic moment rate (class weights; each 0.1 bin over the window of its magnitude, and over
    1976-2026 alone) against the moment rate of the fit, the faults alone and faults plus background."""
    from pituplots.style.axes import darkgrid
    plt = plt_()
    d, te, ft, fc, mf = data()
    m0 = gr.moment(d.mw.to_numpy())
    fig, axs = plt.subplots(1, 4, figsize=(19, 5.8), layout="constrained", sharey=True)
    for ax, c in zip(axs, BG.CLASSES):
        w = d[f"W_{c}"].to_numpy()
        ys = np.array([start(round(x, 1)) for x in d.mw.to_numpy()])
        ok = d.t.to_numpy() >= ys
        bars = {"observed, windows by magnitude": float((w * m0 / (te - ys))[ok].sum()),
                "observed, 1976–2026": float((w * m0)[d.t.to_numpy() >= 1976.0].sum() / (te - 1976.0)),
                "catalogue fit": J.mom(ft[(c, "taper")])}
        cols = ["k", "0.35", "0.6"]
        for db in F.DBS:
            fm = fc[(db, c)][0]
            bars[f"{DB_NAME[db]}: faults"] = J.mom(fm)
            bars[f"{DB_NAME[db]}: faults + background"] = J.mom(fm + J.background(ft[(c, 'taper')], fm))
            cols += [DB_COLOR[db], DB_COLOR[db]]
        if c == "arc":
            for dz, m in mf.items():
                bars[f"A multi-fault {dz:g} km + background"] = J.mom(m + J.background(ft[("arc", "taper")], m))
                cols.append(palette.SERIES[4])
        x = np.arange(len(bars))
        for i, ((lab, v), col) in enumerate(zip(bars.items(), cols)):
            ax.bar(i, v, color=col, edgecolor="k", lw=0.5, alpha=0.85, hatch=".." if "background" in lab else "")
        ax.set_xticks(x, list(bars), rotation=60, ha="right", fontsize=8.5)
        ax.set_yscale("log")
        darkgrid(ax)
        ax.set_title(palette.CLASS_NAME[c], fontsize=12)
    axs[0].set_ylabel("seismic moment rate [N m / yr]")
    fig.suptitle("Crustal moment rates: catalogue (Mw < 7 since 1976, 7–7.4 since 1905, ≥ 7.5 since 1830) against the models "
                 "(dotted: with background)", x=0.01, ha="left")
    save(fig, "check_moments")


def near_share():
    """Per class: the share of the observed Mw >= 6 weight within NEAR_KM of a fault of each database (since 1976, and
    since 1905) against the model share of N(>= 6) on faults."""
    import geopandas as gpd
    import shapely
    from pituplots.style.axes import darkgrid
    plt = plt_()
    d, te, ft, fc, mf = data()
    d = d[d.mw >= 5.95]
    pts = gpd.GeoSeries(gpd.points_from_xy(d.lon, d.lat), crs="EPSG:4326").to_crs("EPSG:32719")
    fig, axs = plt.subplots(1, 4, figsize=(18, 5.6), layout="constrained", sharey=True)
    near = {}
    for db in F.DBS:
        s, _, _ = F.load(db)
        tr = gpd.GeoSeries([shapely.LineString(t) for t in s.trace], crs="EPSG:4326").to_crs("EPSG:32719")
        u = shapely.union_all(tr.values)
        near[db] = np.array([u.distance(p) for p in pts]) / 1e3 <= NEAR_KM
    for ax, c in zip(axs, BG.CLASSES):
        w = d[f"W_{c}"].to_numpy()
        rows = []
        for db in F.DBS:
            fm = fc[(db, c)][0]
            tot = fm + J.background(ft[(c, "taper")], fm)
            for y in (1976.0, 1905.0):
                k = d.t.to_numpy() >= y
                rows.append((db, f"observed since {y:.0f}", float((w * near[db])[k].sum() / max(w[k].sum(), 1e-9)), float(w[k].sum())))
            rows.append((db, "model", J.nge(fm, 6.0) / J.nge(tot, 6.0), np.nan))
        if c == "arc":
            for dz, m in mf.items():
                tot = m + J.background(ft[("arc", "taper")], m)
                rows.append(("A", f"model, multi-fault {dz:g} km", J.nge(m, 6.0) / J.nge(tot, 6.0), np.nan))
        for i, (db, lab, v, n) in enumerate(rows):
            ax.bar(i, v, color=DB_COLOR[db], alpha=0.35 if lab.startswith("observed") else 0.9, edgecolor="k", lw=0.5,
                   hatch="//" if "1905" in lab else "")
            if lab.startswith("observed"):
                ax.text(i, v + 0.02, f"{n:.1f}", ha="center", fontsize=7.5)
        ax.set_xticks(range(len(rows)), [f"{DB_NAME[r[0]]}: {r[1]}" for r in rows], rotation=60, ha="right", fontsize=8)
        ax.set_ylim(0, 1.08)
        darkgrid(ax)
        ax.set_title(palette.CLASS_NAME[c], fontsize=12)
    axs[0].set_ylabel("share of Mw ≥ 6 on faults")
    fig.suptitle(f"Crustal faults: observed Mw ≥ 6 within {NEAR_KM:g} km of a trace against the model share of N(≥ 6) on "
                 "faults (numbers: observed events by weight)", x=0.01, ha="left")
    save(fig, "check_near_share")


def run():
    tradeoff()
    lofs_map()
    share_map()
    counts()
    moments()
    near_share()


if __name__ == "__main__":
    run()


def splay_map(jump=15.0):
    """Liquine-Ofqui traces of database A with the links of the UCERF3 filters at `jump` km: main traces only (the
    rule of 15 Nov) against all traces; groups of main traces in colour, links in grey (main only) and red (new with
    the secondary traces), the secondary traces that join two main groups labelled. Whole system and Aysen."""
    import cartopy.crs as ccrs
    import geopandas as gpd
    from pituplots.maps import dress_map
    plt = plt_()
    pc = ccrs.PlateCarree()
    gpd.options.io_engine = "fiona"
    s, _, _ = F.load("A")
    sysn = gpd.read_file(F.DBS["A"]["file"]).set_index("fid")["system"]
    sl = s[s.fid.map(sysn).eq(MF.LOFS).to_numpy()].reset_index(drop=True)
    main = (sl.sr >= MF.MAIN_SR["A"]).to_numpy()
    MF.JUMP_KM = jump
    res = {}
    for tag, msr in (("main", MF.MAIN_SR["A"]), ("all", 0.0)):
        MF.MIN_SR = msr
        lk = MF.links(sl)
        ch = MF.chains(sl, lk)
        res[tag] = (lk, ch, MF.components(len(sl), [dict(members=c) for c in ch]))
    gm = res["main"][2]
    gid = {g: k for k, g in enumerate(sorted({gm[i] for i in range(len(sl)) if main[i]}))}
    bridges = [i for i in np.where(~main)[0]
               if len({gm[j] for (a, j) in res["all"][0] if a == i and main[j]}) > 1]
    d = gr.load(BG.CAT, mlow=5.95)
    d = d[(d.W_arc > 0.3) & (d.lat < -38) & (d.lat > -48)]
    cols = plt.get_cmap("tab20").colors
    fig = plt.figure(figsize=(14, 9.5), layout="constrained")
    for j, ext in enumerate(([-75.8, -70.8, -48.0, -37.6], [-74.6, -71.8, -47.0, -44.4])):
        ax = fig.add_subplot(1, 2, j + 1, projection=pc)
        dress_map(ax, ext, basemap=str(BASEMAP) if BASEMAP.exists() else None, gridlines=True)
        for i, q in sl.iterrows():
            t = np.asarray(q.trace)
            c = cols[gid[gm[i]] % 20] if main[i] else "0.15"
            ax.plot(t[:, 0], t[:, 1], color=c, lw=2.6 if main[i] else 1.4, ls="-" if main[i] else "--", transform=pc, zorder=4)
        for tag, col, lw in (("main", "0.35", 1.2), ("all", "crimson", 1.4)):
            for (a, b), (pa, pb) in res[tag][0].items():
                if a < b and (tag == "main" or not (main[a] and main[b])):
                    ax.plot([pa[0], pb[0]], [pa[1], pb[1]], color=col, lw=lw, transform=pc, zorder=5)
        for i in bridges:
            t = np.asarray(sl.trace[i])
            ax.plot(t[:, 0], t[:, 1], color="crimson", lw=3, transform=pc, zorder=6)
            ax.text(t[len(t) // 2][0] + 0.05, t[len(t) // 2][1], sl.name[i].replace("Falla ", ""), fontsize=9, color="crimson",
                    transform=pc, zorder=7, clip_on=True)
        ax.scatter(d.lon, d.lat, s=12 * 2.2 ** (d.mw - 6), marker="*", color=palette.SERIES[3], edgecolor="k", lw=0.4,
                   transform=pc, zorder=8)
        for r in d[d.mw >= 6.5].itertuples():
            ax.text(r.lon + 0.05, r.lat - 0.08, f"{r.time[:4]} {r.mw:.1f}", fontsize=8, transform=pc, zorder=9, clip_on=True)
    txt = []
    for tag, lab in (("main", "main traces only"), ("all", "with secondary traces")):
        ch = res[tag][1]
        A = {z: max(float(sum(sl.L[k] * z / np.sin(np.radians(sl.dip[k])) for k in c)) for c in ch) for z in (10.0, 20.0)}
        L = max(float(sl.L[list(c)].sum()) for c in ch)
        txt.append(f"{lab}: {len(res[tag][0]) // 2} links, {len(ch)} chains, longest {L:.0f} km, Leonard Mw "
                   f"{F.R.on_grid(F.R.leonard(A[10.0], 180.0)):.1f} (10 km) / {F.R.on_grid(F.R.leonard(A[20.0], 180.0)):.1f} (20 km)")
    fig.suptitle(f"Liquiñe–Ofqui, database A, jump ≤ {jump:g} km\n" + "\n".join(txt), x=0.01, ha="left", fontsize=11)
    fig.supxlabel("colours: groups of main traces; dashed: secondary traces; grey: links of main traces; red: new links "
                  "with secondary traces (bridging traces thick); stars: arc Mw ≥ 6", fontsize=9.5)
    save(fig, f"check_splays_j{jump:g}")
    return res, bridges


def rupture_maps(jump=15.0, n=3):
    """The largest potential multi-fault ruptures of database A at `jump` km (UCERF3 filters, maximal chains, no rates):
    Liquine-Ofqui with main traces only, Liquine-Ofqui with the secondary traces, and the arc faults north of it. One
    map per rupture: its main traces red, secondary traces orange, the other faults grey; length and Leonard Mw."""
    import cartopy.crs as ccrs
    import geopandas as gpd
    from pituplots.maps import dress_map
    plt = plt_()
    pc = ccrs.PlateCarree()
    gpd.options.io_engine = "fiona"
    s, _, _ = F.load("A")
    s["sysn"] = s.fid.map(gpd.read_file(F.DBS["A"]["file"]).set_index("fid")["system"])
    lofs = s[s.sysn.eq(MF.LOFS)].reset_index(drop=True)
    north = s[(s.cls == "arc") & (s.lat > -38.0) & ~s.sysn.eq(MF.LOFS)].reset_index(drop=True)
    MF.JUMP_KM = jump
    rows = []
    for lab, t, msr in (("Liquiñe–Ofqui, main traces", lofs, MF.MAIN_SR["A"]), ("Liquiñe–Ofqui, with secondary traces", lofs, 0.0),
                        ("arc faults north of Liquiñe–Ofqui", north, 0.0)):
        MF.MIN_SR = msr
        ch = MF.chains(t, MF.links(t))
        sets = [frozenset(c) for c in ch]
        mx = sorted([c for c, a in zip(ch, sets) if not any(a < b for b in sets)], key=lambda c: -t.L[list(c)].sum())
        pick = []
        for c in mx:
            if all(len(set(c) & set(p)) < 0.5 * len(c) for p in pick):
                pick.append(c)
            if len(pick) == n:
                break
        rows.append((lab, t, pick))
    fig = plt.figure(figsize=(4.6 * n, 6.2 * len(rows)), layout="constrained")
    for r, (lab, t, pick) in enumerate(rows):
        for k, c in enumerate(pick):
            ax = fig.add_subplot(len(rows), n, r * n + k + 1, projection=pc)
            tr = np.vstack([np.asarray(t.trace[i]) for i in c])
            x0, x1, y0, y1 = tr[:, 0].min(), tr[:, 0].max(), tr[:, 1].min(), tr[:, 1].max()
            pad = max(0.4, 0.15 * max(x1 - x0, y1 - y0))
            dress_map(ax, [x0 - pad, x1 + pad, y0 - pad, y1 + pad], basemap=str(BASEMAP) if BASEMAP.exists() else None,
                      gridlines=True)
            for q in s.itertuples():
                g = np.asarray(q.trace)
                ax.plot(g[:, 0], g[:, 1], color="0.55", lw=0.8, transform=pc, zorder=3)
            for i in c:
                g = np.asarray(t.trace[i])
                main = t.sr[i] >= MF.MAIN_SR["A"]
                ax.plot(g[:, 0], g[:, 1], color="crimson" if main else "darkorange", lw=3, transform=pc, zorder=5,
                        solid_capstyle="round")
            L = float(t.L[list(c)].sum())
            A = {z: float(sum(t.L[i] * z / np.sin(np.radians(t.dip[i])) for i in c)) for z in (10.0, 20.0)}
            ns = sum(1 for i in c if t.sr[i] < MF.MAIN_SR["A"])
            ax.set_title(f"{L:.0f} km, {len(c)} traces ({ns} secondary)\nLeonard Mw {F.R.on_grid(F.R.leonard(A[10.0], t.rake[c[0]])):.1f}"
                         f" (10 km) / {F.R.on_grid(F.R.leonard(A[20.0], t.rake[c[0]])):.1f} (20 km)", fontsize=10)
            if k == 0:
                ax.text(-0.08, 0.5, lab, transform=ax.transAxes, rotation=90, va="center", ha="right", fontsize=11)
    fig.suptitle(f"Largest potential multi-fault ruptures, database A, jump ≤ {jump:g} km (red: main traces; orange: "
                 "secondary traces; grey: other faults; no rates)", x=0.01, ha="left")
    save(fig, f"check_ruptures_j{jump:g}")


def strict_maps(pkl=BG.TAB / "rupsets_A_2026-11-16e.pkl", n=4):
    """The largest whole-fault scenarios of the strict UCERF3 rupture set (rupset.py) per jump distance, database A,
    depth 10 km, main traces only and main plus splays; red: main traces, orange: secondary traces, grey: other faults.
    Panel titles: length, member count, Leonard Mw at 10 / 20 km thickness."""
    import pickle
    import cartopy.crs as ccrs
    from pituplots.maps import dress_map
    plt = plt_()
    pc = ccrs.PlateCarree()
    d = pickle.load(open(pkl, "rb"))
    sl, keep = d["sl"], d["keep"]
    s, _, _ = F.load("A")
    cases = [(jk, tag) for jk in (5.0, 10.0, 15.0) for tag in ("main", "all")]
    fig = plt.figure(figsize=(4.4 * n, 5.6 * len(cases)), layout="constrained")
    for r, (jk, tag) in enumerate(cases):
        sc = keep[(10.0, jk, tag)]["sc"]
        pick = sorted(sc, key=lambda q: -sl.L[list(q["faults"])].sum())
        sel = []
        for q in pick:
            if all(len(set(q["faults"]) & set(p["faults"])) < 0.5 * len(q["faults"]) for p in sel):
                sel.append(q)
            if len(sel) == n:
                break
        for k, q in enumerate(sel):
            ax = fig.add_subplot(len(cases), n, r * n + k + 1, projection=pc)
            tr = np.vstack([np.asarray(sl.trace[i]) for i in q["faults"]])
            x0, x1, y0, y1 = tr[:, 0].min(), tr[:, 0].max(), tr[:, 1].min(), tr[:, 1].max()
            pad = max(0.4, 0.15 * max(x1 - x0, y1 - y0))
            dress_map(ax, [x0 - pad, x1 + pad, y0 - pad, y1 + pad], basemap=str(BASEMAP) if BASEMAP.exists() else None, gridlines=True)
            for g in s.trace:
                g = np.asarray(g)
                ax.plot(g[:, 0], g[:, 1], color="0.55", lw=0.8, transform=pc, zorder=3)
            for i in q["faults"]:
                g = np.asarray(sl.trace[i])
                ax.plot(g[:, 0], g[:, 1], color="crimson" if sl.sr[i] >= MF.MAIN_SR["A"] else "darkorange", lw=3,
                        transform=pc, zorder=5, solid_capstyle="round")
            L = float(sl.L[list(q["faults"])].sum())
            A = {z: float(sum(sl.L[i] * z / np.sin(np.radians(sl.dip[i])) for i in q["faults"])) for z in (10.0, 20.0)}
            ax.set_title(f"{L:.0f} km, {len(q['faults'])} faults\nLeonard Mw {F.R.on_grid(F.R.leonard(A[10.0], 180.0)):.1f} (10 km) / "
                         f"{F.R.on_grid(F.R.leonard(A[20.0], 180.0)):.1f} (20 km thickness)", fontsize=10)
            if k == 0:
                ax.text(-0.1, 0.5, f"jump ≤ {jk:g} km, {'main traces' if tag == 'main' else 'main + splays'}\n{len(sc)} scenarios",
                        transform=ax.transAxes, rotation=90, va="center", ha="right", fontsize=10)
    fig.suptitle("Largest whole-fault scenarios of the strict UCERF3 rupture set, database A, subsections 5 km (thickness 10 km)",
                 x=0.01, ha="left")
    save(fig, "check_strict_scenarios")


def scenario_pages(jump=15.0, traces="main", pkl=None, outdir=None, first_only=False):
    """One page per whole-fault scenario of the strict UCERF3 set (database A, 5 km subsections), largest extent first:
    the Liquine-Ofqui faults as the base map, the scenario's faults in colour with their ids, arc Mw >= 6 as stars
    (Mw >= 6.3 labelled), length and Mmax in a box, legend. Files figs/<DATE>/scenarios_<jump>_<traces>/<rank>.png."""
    import pickle
    import cartopy.crs as ccrs
    from matplotlib.lines import Line2D
    from pituplots.maps import dress_map
    plt = plt_()
    pc = ccrs.PlateCarree()
    pkl = pkl or BG.TAB / "rupsets_A_2026-11-16e.pkl"
    d = pickle.load(open(pkl, "rb"))
    sl, sc = d["sl"], d["keep"][(10.0, jump, traces)]["sc"]
    main = (sl.sr >= MF.MAIN_SR["A"]).to_numpy()
    sc = sorted(sc, key=lambda q: -sl.L[list(q["faults"])].sum())
    ev = gr.load(BG.CAT, mlow=5.95)
    ev = ev[(ev.W_arc > 0.3) & (ev.lat < -37.5) & (ev.lat > -48.5)]
    out = outdir or FIG / f"scenarios_j{jump:g}_{traces}"
    out.mkdir(parents=True, exist_ok=True)
    base, mainc, secc = "#1f5f8b", "crimson", "darkorange"
    for rank, q in enumerate(sc[:1] if first_only else sc, 1):
        fig = plt.figure(figsize=(7.5, 11), layout="constrained")
        ax = fig.add_subplot(1, 1, 1, projection=pc)
        dress_map(ax, [-76.0, -70.5, -48.2, -37.6], basemap=str(SCEN_BASEMAP) if SCEN_BASEMAP.exists() else None,
                  coastline=False, gridlines=True)
        for i, tr in enumerate(sl.trace):
            tr = np.asarray(tr)
            ax.plot(tr[:, 0], tr[:, 1], color=base, lw=1.5 if main[i] else 1.0, ls="-" if main[i] else (0, (3, 2)),
                    transform=pc, zorder=4, alpha=0.9)
        for i in q["faults"]:
            tr = np.asarray(sl.trace[i])
            ax.plot(tr[:, 0], tr[:, 1], color=mainc if main[i] else secc, lw=4, transform=pc, zorder=6, solid_capstyle="round")
            m = tr[len(tr) // 2]
            ax.text(m[0] - 0.08, m[1], sl.fid[i].replace("CL-", ""), fontsize=8, color=mainc if main[i] else secc,
                    ha="right", va="center", transform=pc, zorder=8, clip_on=True,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75))
        ax.scatter(ev.lon, ev.lat, s=16 * 2.2 ** (ev.mw - 6), marker="*", color=palette.SERIES[3], edgecolor="k", lw=0.4,
                   transform=pc, zorder=7)
        for r in ev[ev.mw >= 6.3].itertuples():
            ax.text(r.lon + 0.07, r.lat - 0.04, f"{r.time[:4]} {r.mw:.1f}", fontsize=9, transform=pc, zorder=8, clip_on=True,
                    bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.6))
        L = float(sl.L[list(q["faults"])].sum())
        A = {z: float(sum(sl.L[i] * z / np.sin(np.radians(sl.dip[i])) for i in q["faults"])) for z in (10.0, 20.0)}
        ax.text(0.03, 0.97, f"scenario {rank} of {len(sc)}\n{len(q['faults'])} faults, {L:.0f} km\n"
                f"Mw {F.R.on_grid(F.R.leonard(A[10.0], 180.0)):.1f} at 10 km thickness\nMw {F.R.on_grid(F.R.leonard(A[20.0], 180.0)):.1f} at 20 km thickness",
                transform=ax.transAxes, va="top", ha="left", fontsize=11,
                bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="0.6", alpha=0.9), zorder=9)
        hd = [Line2D([], [], color=mainc, lw=4, label="rupture, main trace"),
              Line2D([], [], color=secc, lw=4, label="rupture, secondary trace"),
              Line2D([], [], color=base, lw=1.5, label="Liquiñe–Ofqui main trace"),
              Line2D([], [], color=base, lw=1.0, ls=(0, (3, 2)), label="secondary trace"),
              Line2D([], [], marker="*", color=palette.SERIES[3], mec="k", mew=0.4, ls="", ms=11, label="arc Mw ≥ 6")]
        ax.legend(handles=hd, loc="lower left", fontsize=9, frameon=True, framealpha=0.9)
        ax.set_title(f"Liquiñe–Ofqui multi-fault scenario, database A, jump ≤ {jump:g} km, "
                     f"{'main traces' if traces == 'main' else 'main + splays'}", fontsize=10, loc="left")
        fig.savefig(out / f"{rank:03d}.png", dpi=140)
        plt.close(fig)
    return out

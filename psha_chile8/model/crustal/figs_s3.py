"""Figures of S3 in the pituplots style of model/inslab/figs_s2.py: rate pattern maps per class and declustering
option, the class fits against the catalogue, and the kernel calibration. Reads the tables of background.py.
Writes figs/<DATE>/pattern_<option>.png, mfd_classes.png and kernel_loglik.png."""
import sys

import numpy as np
import pandas as pd

import background as BG
import gr

sys.path.insert(0, str(BG.ROOT))
sys.path.insert(0, str(BG.ROOT / "catalog"))
import palette  # noqa: E402

FIG = BG.FIG / BG.DATE
BASEMAP = BG.ROOT.parent / "data" / "basemaps" / "basemap_chile_gray" / "basemap_gray.tif"
EXTENT = [-77.0, -65.0, -56.5, -17.0]
DH = 0.1
VMIN, VMAX = -6.0, -2.0
DECL_NAME = {"gk": "Gardner–Knopoff", "nn": "nearest neighbour"}


def plt_():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    palette.apply()
    return plt


def save(fig, name, dpi=150):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=dpi)
    fig.clf()


def maps():
    """N(>= 5) per cell of every class and of the four together, one figure per declustering option, one colour scale
    for all panels."""
    import cartopy.crs as ccrs
    import shapely
    import classify as K
    from pituplots import plot_grid
    from pituplots.io.containers import Grid
    from pituplots.maps import dress_map
    plt = plt_()
    pc = ccrs.PlateCarree()
    tr = [shapely.get_coordinates(K.geoms(f)) for f in (K.TRENCH, K.TRENCH_AN)]
    n5 = {c: BG.mfd(c, "taper")[1].sum() for c in BG.CLASSES}
    for k in BG.DECL:
        p = pd.read_csv(BG.TAB / f"pattern_{k}_{BG.DATE}.csv")
        v = {c: p[c].to_numpy() * n5[c] for c in BG.CLASSES}
        v["all"] = sum(v.values())
        fig = plt.figure(figsize=(17, 10.5), layout="constrained")
        for j, c in enumerate(list(BG.CLASSES) + ["all"]):
            ax = fig.add_subplot(1, 5, j + 1, projection=pc)
            dress_map(ax, EXTENT, basemap=str(BASEMAP) if BASEMAP.exists() else None, gridlines=j == 0)
            for t in tr:
                ax.plot(t[:, 0], t[:, 1], color="0.35", lw=0.8, transform=pc)
            on = v[c] > 0
            plot_grid(Grid.from_points(p.lon[on], p.lat[on], v[c][on], dh=DH), ax=ax, log=True, colorbar=False,
                      vmin=VMIN, vmax=VMAX, rasterized=True, zorder=3)
            fig.colorbar(ax.collections[-1], ax=ax, orientation="horizontal", shrink=0.85, pad=0.02,
                         label="log₁₀ N(≥ 5) per cell and year")
            t = "all crustal classes" if c == "all" else palette.CLASS_NAME[c]
            ax.set_title(f"{t}\nN(≥ 5) {sum(n5.values()) if c == 'all' else n5[c]:.2f} per year", fontsize=11)
        fig.suptitle(f"Crustal rate pattern, {DECL_NAME[k]} declustering", x=0.01, ha="left")
        save(fig, f"pattern_{k}")


def catalogue(ax, d, c, b, st):
    """Observed N(>= M) of class c: cumulative steps (each 0.1 bin over its own completeness period, class and
    magnitude-error weights) and the completeness periods as dots."""
    te = gr.tend(d)
    tb = sorted(BG.TABLE, key=lambda q: -q[1])
    per = [(m, y, te if i == 0 else tb[i - 1][1]) for i, (m, y) in enumerate(tb)]
    mw, t = d.mw.to_numpy(), d.t.to_numpy()
    w = d[f"W_{c}"].to_numpy() * gr.magw(d.mw_sigma.to_numpy(), b)
    mb = np.round(np.arange(5.0, mw[w > 0].max() + 0.05, 0.1), 1)
    yc = np.array([min((y for m, y in tb if x >= m - 1e-6), default=np.inf) for x in mb])
    kb = np.rint((mw - 5.0) / 0.1).astype(int)
    r = np.array([w[(kb == i) & (t >= y)].sum() / (te - y) if np.isfinite(y) else 0.0 for i, y in enumerate(yc)])
    cum = np.cumsum(r[::-1])[::-1]
    ax.step(mb, np.where(cum > 0, cum, np.nan), where="mid", color="0.45", lw=1.4, label="catalogue", zorder=4)
    for i, (mc, y0, y1) in enumerate(per):
        k = (t >= y0) & (t < y1) & (mw >= mc - 1e-6) & (w > 0)
        m = np.round(np.arange(mc, mw[k].max() + 0.05, 0.1), 1)
        n = np.array([w[k][mw[k] >= x - 1e-6].sum() for x in m]) / (y1 - y0)
        ax.plot(m, n, "o", ms=st["ms"], color=st["colors"][i], mec="black", mew=st["mew"], alpha=st["alpha"], zorder=3,
                label=f"{y0:.0f}–{min(y1, 2026):.0f}")


def old_events(d, c, b, m):
    """Per 0.1 bin on m, the observed rate of Mw >= 7 before 1976, out of the fit: each bin over the historical step of
    its magnitude (multifault.HIST), class and magnitude-error weights."""
    import multifault as MF
    te = gr.tend(d)
    w = d[f"W_{c}"].to_numpy() * gr.magw(d.mw_sigma.to_numpy(), b)
    k = np.rint((d.mw.to_numpy() - m[0]) / gr.DM).astype(int)
    out = np.zeros(m.size)
    for i, x in enumerate(m):
        st = [(M, yy) for M, yy in MF.HIST if x >= M - 1e-6]
        y = max(st)[1] if st else None
        if y is not None:
            out[i] = w[(k == i) & (d.t.to_numpy() >= y)].sum() / (te - y)
    return out


def joins(db="A"):
    """
    The join per class, as rates per 0.1 bin: catalogue fit, observed rate (complete since 1976, class and
    magnitude-error weights), faults of database db (weighted mean and range of the tree), background after the join
    and the sum. For A the arc is drawn twice: single faults, and faults with the Liquine-Ofqui multi-fault
    ruptures (15 km, depth 10 km, psi-weighted mean of 10 seeds).
    """
    import faults as F
    import join as J
    from pituplots.style.axes import darkgrid
    from pituplots.style.defaults import resolve
    st = resolve("fmd")
    plt = plt_()
    d = gr.load(BG.CAT, mlow=4.45)
    te = gr.tend(d)
    y0 = min(y for _, y in BG.TABLE)
    ft, fc = J.fits(), J.fault_classes()
    fits = pd.read_csv(BG.FITS)
    m = J.CENTRES
    pos = lambda r: np.where(np.asarray(r) > 0, r, np.nan)
    mf = np.load(BG.TAB / f"mf_A_lofs_mfd_{BG.DATE}.npz") if db == "A" else None
    panels = [(c, False) for c in BG.CLASSES]
    if mf is not None:
        panels.insert(2, ("arc", True))
    fig, axs = plt.subplots(1, len(panels), figsize=(4.3 * len(panels), 5.4), layout="constrained", sharey=True)
    for ax, (c, multi) in zip(axs, panels):
        q = fits[(fits.unit == c) & (fits["shape"] == "taper")].iloc[0]
        fit, (fm, fb) = ft[(c, "taper")], fc[(db, c)]
        lo, hi = fb.min(0), fb.max(0)
        if multi:
            w = {p: F.R.PSI[p] for p in (0.6, 0.8, 1.0)}
            fm = sum(w[p] * mf[f"j15_z10_psi{p:g}"].mean(axis=0) for p in w) / sum(w.values())
            r = np.array([mf[f"j15_z10_psi{p:g}"].mean(axis=0) for p in w])
            lo, hi = r.min(0), r.max(0)
        bg = J.background(fit, fm)
        w = d[f"W_{c}"].to_numpy() * gr.magw(d.mw_sigma.to_numpy(), q.b)
        k = np.rint((d.mw.to_numpy() - m[0]) / gr.DM).astype(int)
        ok = (w > 0) & (d.t.to_numpy() >= y0) & (k >= 0) & (k < m.size)
        obs = np.bincount(k[ok], w[ok], minlength=m.size) / (te - y0)
        ax.plot(m, pos(fit), color="0.55", lw=3, label="catalogue fit", zorder=3)
        ax.fill_between(m, pos(lo), pos(hi), color=palette.SERIES[1], alpha=0.18, lw=0,
                        label="faults, ψ range" if multi else "faults, range of the tree", zorder=2)
        ax.plot(m, pos(fm), color=palette.SERIES[1], lw=2, marker="o", ms=3, label="faults", zorder=5)
        ax.plot(m, pos(bg), color=palette.CLASS_COLOR[c], lw=2, marker="o", ms=3, label="background", zorder=5)
        ax.plot(m, pos(bg + fm), color="black", lw=1.2, ls="--", label="faults + background", zorder=6)
        ax.plot(m, pos(obs), "o", ms=st["ms"] + 1, color=st["colors"][0], mec="black", mew=st["mew"], zorder=7,
                label=f"observed {y0:.0f}–2026")
        ax.plot(m, pos(old_events(d, c, q.b, m)), "D", ms=st["ms"] + 1, mfc="white", mec=st["colors"][1], mew=1.2, zorder=7,
                label="Mw ≥ 7 since 1905 (≥ 7.5 since 1830), not in the fit")
        ax.axvline(5.95, color="0.6", lw=0.8, ls=":")
        darkgrid(ax)
        sub = "Liquiñe–Ofqui multi-fault" if multi else ("single faults" if c == "arc" and mf is not None else "")
        ax.set_title(f"{palette.CLASS_NAME[c]}{', ' + sub if sub else ''}\nN(≥ 6): fit {fit[m >= 5.95].sum():.3f}, "
                     f"faults {fm[m >= 5.95].sum():.3f}", fontsize=11)
        ax.set_xlabel("Mw (0.1 bins)")
        ax.set_ylabel("")
        ax.set_yscale("log")
        ax.set_ylim(1e-5, 1)
        ax.set_xlim(4.9, 8.4)
    axs[0].set_ylabel("events per year in the bin")
    axs[0].legend(fontsize=9, loc="lower left", frameon=False)
    fig.suptitle(f"Crustal faults, database {F.NAMES[db]}, and the background after the join", x=0.01, ha="left")
    save(fig, f"join_{db}")


def lofs_study(db="A"):
    """Liquine-Ofqui multi-fault branch of database db per jump distance and depth, per 0.1 bin: faults plus background
    for each psi (mean of the seeds, band their range), the arc fit, the observed rates, and the arc count tests."""
    import join as J
    import multifault as MF
    from pituplots.style.axes import darkgrid
    from pituplots.style.defaults import resolve
    st = resolve("fmd")
    plt = plt_()
    d = gr.load(BG.CAT, mlow=4.45)
    te = gr.tend(d)
    y0 = min(y for _, y in BG.TABLE)
    fits = pd.read_csv(BG.FITS)
    q = fits[(fits.unit == "arc") & (fits["shape"] == "taper")].iloc[0]
    fit = J.fits()[("arc", "taper")]
    m = J.CENTRES
    pos = lambda r: np.where(np.asarray(r) > 0, r, np.nan)
    import faults as F
    z = np.load(BG.TAB / f"mf_{db}_lofs_mfd_{BG.DATE}.npz")
    t = pd.read_csv(BG.TAB / f"mf_{db}_lofs_{BG.DATE}.csv").groupby(["jump", "depth", "psi"]).mean(numeric_only=True)
    w = d.W_arc.to_numpy() * gr.magw(d.mw_sigma.to_numpy(), q.b)
    k = np.rint((d.mw.to_numpy() - m[0]) / gr.DM).astype(int)
    ok = (w > 0) & (d.t.to_numpy() >= y0) & (k >= 0) & (k < m.size)
    obs = np.bincount(k[ok], w[ok], minlength=m.size) / (te - y0)
    old = old_events(d, "arc", q.b, m)
    J_, Z_ = MF.JUMPS_STUDY, MF.DEPTHS_LOFS
    J_ = [j for j in J_ if any(k.startswith(f"j{j:g}_") for k in z.files)]
    fig, axs = plt.subplots(len(Z_), len(J_), figsize=(4.4 * len(J_), 4.6 * len(Z_)), layout="constrained", sharex=True, sharey=True, squeeze=False)
    for r, zz in enumerate(Z_):
        for c, jk in enumerate(J_):
            ax = axs[r, c]
            ax.plot(m, pos(fit), color="0.55", lw=3, label="catalogue fit", zorder=3)
            txt = []
            for col, ps in zip(palette.SERIES, MF.PSIS):
                x = z[f"j{jk:g}_z{zz:g}_psi{ps:g}"]
                tot = x + np.array([J.background(fit, y) for y in x])
                ax.fill_between(m, pos(tot.min(0)), pos(tot.max(0)), color=col, alpha=0.2, lw=0, zorder=2)
                ax.plot(m, pos(tot.mean(0)), color=col, lw=1.8, label=f"faults + background, ψ {ps:g}", zorder=5)
                g = t.loc[(jk, zz, ps)]
                txt.append(f"ψ {ps:g}: {g.exp6:.1f} (p {g.p6:.2f}), ≥ 7 hist. {g.exp7_hist:.1f}")
            ax.plot(m, pos(obs), "o", ms=st["ms"] + 1, color=st["colors"][0], mec="black", mew=st["mew"], zorder=7,
                    label=f"observed {y0:.0f}–2026")
            ax.plot(m, pos(old), "D", ms=st["ms"] + 1, mfc="white", mec=st["colors"][1], mew=1.2, zorder=7,
                    label="Mw ≥ 7 since 1905 (≥ 7.5 since 1830)")
            g = t.loc[(jk, zz, MF.PSIS[1])]
            ax.text(0.98, 0.98, f"expected Mw ≥ 6 since 1976 (obs. {g.obs6:.1f}):\n" + "\n".join(txt) +
                    f"\nobs. ≥ 7 hist. {g.obs7_hist:.1f}; longest {g.longest_km:.0f} km, Mmax {g.mmax:.1f}",
                    transform=ax.transAxes, ha="right", va="top", fontsize=8)
            ax.axvline(5.95, color="0.6", lw=0.8, ls=":")
            darkgrid(ax)
            ax.set_yscale("log")
            ax.set_ylim(1e-5, 1)
            ax.set_xlim(4.9, 8.4)
            ax.set_title(f"jump ≤ {jk:g} km, thickness {zz:g} km", fontsize=11)
            ax.set_xlabel("Mw (0.1 bins)" if r == len(Z_) - 1 else "")
            ax.set_ylabel("events per year in the bin" if c == 0 else "")
    axs[-1, 0].legend(fontsize=8, loc="lower left", frameon=False)
    fig.suptitle(f"Crustal arc, database {F.NAMES[db]}: Liquiñe–Ofqui multi-fault ruptures\nby jump distance and seismogenic "
                 "thickness (band: 10 seeds)", x=0.01, ha="left", fontsize=11)
    save(fig, f"mf_lofs_study_{db}")


def mfds():
    """Class fits against the catalogue: cumulative steps (each 0.1 bin over its own completeness period, class and
    magnitude-error weights), the completeness periods as dots, the tapered and cut lists, the 5-95 % band of the
    tapered line from the (a, b) covariance of the fit."""
    from pituplots.stats.catalogs import plot_mfd
    from pituplots.style.axes import darkgrid
    from pituplots.style.defaults import resolve
    st = resolve("fmd")
    plt = plt_()
    d = gr.load(BG.CAT, mlow=4.45)
    fits = pd.read_csv(BG.FITS)
    fig, axs = plt.subplots(1, 4, figsize=(19, 5.6), layout="constrained", sharey=True)
    for ax, c in zip(axs, BG.CLASSES):
        q = fits[(fits.unit == c) & (fits["shape"] == "taper")].iloc[0]
        catalogue(ax, d, c, q.b, st)
        cc, nn = BG.mfd(c, "taper")
        x = cc - gr.DM / 2
        cn = np.cumsum(nn[::-1])[::-1]
        sd = 1.645 * np.sqrt(q.var_a + x ** 2 * q.var_b - 2 * x * q.cov_ab)
        ax.fill_between(x, cn * 10 ** -sd, cn * 10 ** sd, color="0.55", alpha=0.3, lw=0, label="(a, b) 5–95 %", zorder=2)
        for sh, ls, lab in (("taper", "-", "tapered"), ("trunc", "--", "cut")):
            cc, nn = BG.mfd(c, sh)
            plot_mfd(cc - gr.DM / 2, nn, ax=ax, label=lab, color="black", ls=ls, lw=st["fit_lw"], legend=False, zorder=5)
        darkgrid(ax)
        ax.set_title(f"{palette.CLASS_NAME[c]}, b {q.b:.2f}, Mmax {q.mmax:.1f}", fontsize=12)
        ax.set_xlabel("Mw")
        ax.set_ylabel("")
        ax.set_yscale("log")
        ax.set_ylim(1e-5, 20)
        ax.set_xlim(4.9, 8.5)
    axs[0].set_ylabel("N(≥ Mw) per year")
    axs[0].legend(fontsize=9, loc="lower left", frameon=False)
    fig.suptitle("Crustal sources against the catalogue", x=0.01, ha="left")
    save(fig, "mfd_classes")


def kernel_ll():
    """Test log-likelihood against n relative to the best, per class and declustering option; n used circled, n below
    N_MIN shaded."""
    plt = plt_()
    cal = pd.read_csv(BG.TAB / f"calibration_{BG.DATE}.csv")
    pick = pd.read_csv(BG.TAB / f"kernel_n_{BG.DATE}.csv")
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True, layout="constrained")
    for ax, k in zip(axs, BG.DECL):
        for c in list(BG.CLASSES) + ["crustal"]:
            q = cal[(cal.option == k) & (cal.unit == c)].sort_values("n")
            name, col = (palette.CLASS_NAME[c], palette.CLASS_COLOR[c]) if c in BG.CLASSES else ("all crustal (reference)", "0.4")
            ax.plot(q.n, q.dloglik, "--" if c == "crustal" else "-", marker="o", ms=4, color=col,
                    label=f"{name} ({q.test.iloc[0]:.0f} test events)")
            if c in BG.CLASSES:
                b = q[q.n == int(pick[(pick.option == k) & (pick.unit == c)].n.iloc[0])]
                ax.plot(b.n, b.dloglik, "o", ms=9, mfc="none", mec=col, mew=1.5)
        ax.axvspan(0.85, BG.N_MIN * 0.9, color="0.93", zorder=0, lw=0)
        ax.set_xscale("log")
        ax.set_xlim(0.85, 118)
        ax.set_xticks(BG.CANDS, [str(n) for n in BG.CANDS])
        ax.minorticks_off()
        ax.set_ylim(-25, 2)
        ax.axhline(-2, color="0.6", lw=0.8, ls=":")
        ax.set_xlabel("kernel n (neighbour of the bandwidth)")
        ax.set_title(f"{DECL_NAME[k]} declustering")
        ax.legend(fontsize=9, loc="lower left", frameon=False)
    axs[0].set_ylabel("test log-likelihood − best")
    fig.suptitle("Crustal kernel calibration: events before 2010 against 2010–2026 (circled: n used; shaded: scored, "
                 "not chosen)", x=0.01, ha="left")
    save(fig, "kernel_loglik")


def grid_events():
    """The crustal grid against the complete events (Mw >= 5 from 1976) of every class: filled inside the grid, open
    outside; size by Mw, opacity by class weight; the share of class weight outside the grid in the title."""
    import cartopy.crs as ccrs
    import shapely
    from shapely.geometry import box
    from pituplots.maps import dress_map
    plt = plt_()
    pc = ccrs.PlateCarree()
    g = BG.grid()
    h = DH / 2
    poly = shapely.union_all([box(x - h, y - h, x + h, y + h) for x, y in zip(g.lon, g.lat)]).buffer(0.01).buffer(-0.01)
    d = BG.events()
    d = d[d.complete]
    ins = BG.S.cells(g.lon.to_numpy(), g.lat.to_numpy(), d.lon.to_numpy(), d.lat.to_numpy()) >= 0
    fig = plt.figure(figsize=(17, 10.5), layout="constrained")
    for j, c in enumerate(BG.CLASSES):
        ax = fig.add_subplot(1, 4, j + 1, projection=pc)
        dress_map(ax, [-77.0, -63.0, -59.0, -17.0], basemap=str(BASEMAP) if BASEMAP.exists() else None, gridlines=j == 0)
        for q in getattr(poly, "geoms", [poly]):
            x, y = q.exterior.xy
            ax.fill(x, y, color="0.15", alpha=0.15, lw=0, transform=pc, zorder=2)
            ax.plot(x, y, color="0.15", lw=1.2, transform=pc, zorder=3)
        w = d[f"W_{c}"].to_numpy()
        col = palette.CLASS_COLOR[c]
        from matplotlib.colors import to_rgba
        for k, lab in enumerate(("inside the grid", "outside the grid")):
            s = (w > 0) & (ins if k == 0 else ~ins)
            ec = np.tile(to_rgba(col), (s.sum(), 1))
            ec[:, 3] = np.clip(w[s], 0.5, 1)
            fc = ec.copy() if k == 0 else np.zeros_like(ec)
            ax.scatter(d.lon[s], d.lat[s], s=6 * 2.2 ** (d.mw[s] - 4), facecolors=fc, edgecolors=ec, lw=1.0,
                       transform=pc, zorder=5, label=lab)
        out = w[~ins].sum() / w.sum()
        ax.set_title(f"{palette.CLASS_NAME[c]}\n{w.sum():.0f} events by weight, {out:.0%} outside the grid", fontsize=11)
        if j == 0:
            ax.legend(loc="lower left", fontsize=9, frameon=True)
    fig.suptitle("Crustal grid against the complete events (Mw ≥ 5 since 1976; size by Mw, opacity by class weight)", x=0.01, ha="left")
    save(fig, "grid_events")


def run():
    maps()
    mfds()
    kernel_ll()
    grid_events()
    for db in ("A", "B", "Bmm"):
        joins(db)
    for db in ("A", "B", "Bmm"):
        lofs_study(db)


if __name__ == "__main__":
    run()

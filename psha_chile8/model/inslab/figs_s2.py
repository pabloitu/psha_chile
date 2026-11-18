"""Figures of S2: pattern maps per class and declustering option, depth sections through the sources, MFDs of the
summed sources over the observed series per completeness period. Reads the tables of build.py."""
import numpy as np
import pandas as pd

import figs as F7  # C14 figures, before build puts fits/ on the path
import palette
import build as B  # noqa: E402

F7.FIG = B.OUT / "figs" / B.DATE
DH = 0.1
SECT = [-20.0, -23.0, -30.0, -33.0, -38.0]
NEST_EXT = [-68.6, -65.2, -25.6, -22.4]
DECL_NAME = {"gk": "Gardner–Knopoff", "nn": "nearest neighbour"}
PERIOD_COLOR = palette.SERIES[:5]


def maps(pat, F):
    import cartopy.crs as ccrs
    from pituplots import plot_grid
    from pituplots.io.containers import Grid
    from pituplots.maps import dress_map
    plt = F7.plt_()
    pc = ccrs.PlateCarree()
    tr = __import__("shapely").get_coordinates(F7.D.C.geoms(F7.D.C.TRENCH))
    for k in B.DECL:
        n5 = {s["short"]: pat[f"p_{s['short']}_{k}"] * F[(c, "taper")].rate_mlo for c, s in B.CLASSES.items()}
        n5["all"] = sum(n5.values())
        fig = plt.figure(figsize=(17, 9.5), layout="constrained")
        for j, (q, t) in enumerate([("shallow", "in-slab, shallow"), ("intermediate", "in-slab, intermediate depth"),
                                    ("nest", "Jujuy nest"), ("all", "all in-slab classes")]):
            ax = fig.add_subplot(1, 4, j + 1, projection=pc)
            ext = NEST_EXT if q == "nest" else F7.EXTENT
            dress_map(ax, ext, basemap=str(F7.BASEMAP) if F7.BASEMAP.exists() else None, gridlines=j in (0, 2))
            ax.plot(tr[:, 0], tr[:, 1], color="0.35", lw=0.8, transform=pc)
            v = n5[q].to_numpy()
            on = v > 0
            grid = Grid.from_points(pat.lon[on], pat.lat[on], v[on], dh=DH)
            # pituplots grid style: magma with its alpha ramp, so low rates let the relief through
            plot_grid(grid, ax=ax, log=True, colorbar=False, vmin=-5.5 if q != "nest" else -3.5,
                      vmax=-2.0 if q != "nest" else -1.3, rasterized=True, zorder=3)
            fig.colorbar(ax.collections[-1], ax=ax, orientation="horizontal", shrink=0.85, pad=0.02, label="log₁₀ N(≥ 5) per cell and year")
            ax.set_title(t, fontsize=12)
        fig.suptitle(f"In-slab rate pattern, {DECL_NAME[k]} declustering", x=0.01, ha="left")
        F7.save(fig, f"pattern_{k}")


def sections(pat, F):
    import shapely.ops
    from pituplots.io import read_slab2
    from pituplots.sections import add_slab, profiles_from_line, project
    plt = F7.plt_()
    D = F7.D
    top, thk = (read_slab2(D.SLAB[q]) for q in ("dep", "thk"))
    t = D.C.geoms(D.C.TRENCH)
    t = shapely.ops.linemerge(t) if t.geom_type != "LineString" else t
    line = max(t.geoms, key=lambda q: q.length) if t.geom_type != "LineString" else t
    prof = profiles_from_line(line, SECT, width=2 * F7.STRIP, side=(-60, -30), length=F7.XLIM)
    g = B.cells()
    n5 = sum(B.DECL_W[k] * sum(pat[f"p_{s['short']}_{k}"] * F[(c, "taper")].rate_mlo for c, s in B.CLASSES.items()) for k in B.DECL)
    cat = B.G.load(mlow=4.45)
    cat = cat[(cat.w_inslab >= 0.5) & (cat.depth_kind == "measured")].sort_values("mw")
    fig, axs = plt.subplots(len(SECT), 1, figsize=(12, 3.3 * len(SECT)), layout="constrained")
    for ax, p, lat in zip(axs, prof, SECT):
        u, v = project(cat.lon.to_numpy(), cat.lat.to_numpy(), p)
        k = (np.abs(v) <= F7.STRIP) & (u >= F7.XLIM[0]) & (u <= F7.XLIM[1])
        ax.scatter(u[k], cat.depth.to_numpy()[k], s=3, color="0.6", lw=0, alpha=0.5, rasterized=True, label="in-slab events, Mw ≥ 4.5")
        big = k & (cat.mw.to_numpy() >= 7)
        ax.scatter(u[big], cat.depth.to_numpy()[big], s=90, marker="*", color=palette.SERIES[3], edgecolor="k", lw=0.4, zorder=8,
                   label="Mw ≥ 7")
        for x, z, m, tm in zip(u[big], cat.depth.to_numpy()[big], cat.mw.to_numpy()[big], cat.time.to_numpy()[big]):
            ax.annotate(f"{tm[:4]} {m:.1f}", (x, z), xytext=(4, -6), textcoords="offset points", fontsize=8, zorder=9)
        add_slab(ax, p, top, thk)
        cu, cv = project(g.lon.to_numpy(), g.lat.to_numpy(), p)
        c = np.flatnonzero((np.abs(cv) <= 5.0) & (cu >= F7.XLIM[0]) & (cu <= F7.XLIM[1]))
        c = c[np.argsort(cu[c])]
        ax.fill_between(cu[c], g.usd.to_numpy()[c], g.lsd.to_numpy()[c], color=palette.SERIES[0], alpha=0.12, lw=0,
                        label="seismogenic zone of the sources")
        r = n5.to_numpy()[c] / n5.max()
        for l in range(3):
            ax.scatter(cu[c], g[f"h{l + 1}"].to_numpy()[c], s=150 * g[f"w{l + 1}"].to_numpy()[c] * np.sqrt(r) + 1,
                       color=F7.LAYER[l], edgecolor="white", lw=0.3, zorder=5, label=f"hypocentre {l + 1} (size: weight × rate)")
        ax.plot(cu[c], g.h_one.to_numpy()[c], color="k", lw=1.0, ls=":", zorder=6, label="one-layer hypocentre")
        ax.set_xlim(*F7.XLIM)
        ax.set_ylim(F7.ZMAX, -5)
        ax.set_aspect(1)
        ax.set_ylabel("depth [km]")
        ax.set_title(f"{-lat:.0f}° S", fontsize=12)
    axs[0].legend(loc="lower left", ncol=4, fontsize=8, markerscale=1.2)
    axs[-1].set_xlabel("distance from the trench [km]")
    fig.suptitle("In-slab point sources: zone and hypocentres (cells within 5 km), events within 50 km", x=0.01, ha="left")
    F7.save(fig, "sections_sources", dpi=130)


def mfds(F):
    """Summed sources against the observed rates, in the pituplots FMD style: the whole catalogue as cumulative steps
    (each 0.1 bin over its own completeness period), the completeness periods as dots, the source lines on top."""
    from pituplots.stats.catalogs import plot_mfd
    from pituplots.style.axes import darkgrid
    from pituplots.style.defaults import resolve
    st = resolve("fmd")
    plt = F7.plt_()
    d = B.G.load(B.CAT, mlow=4.45)
    te = B.G.tend(d)
    tb = sorted(B.TABLE, key=lambda q: -q[1])
    per = [(m, y, te if i == 0 else tb[i - 1][1]) for i, (m, y) in enumerate(tb)]
    mw, t = d.mw.to_numpy(), d.t.to_numpy()
    fig, axs = plt.subplots(1, 3, figsize=(16, 5.5), layout="constrained")
    for ax, (c, s) in zip(axs, B.CLASSES.items()):
        w = d["W_" + c].to_numpy() * B.G.magw(d.mw_sigma.to_numpy(), F[(c, "taper")].b)
        mb = np.round(np.arange(5.0, mw[w > 0].max() + 0.05, 0.1), 1)
        yc = np.array([min(y for m, y in tb if x >= m - 1e-6) for x in mb])
        kb = np.rint((mw - 5.0) / 0.1).astype(int)
        r = np.array([w[(kb == i) & (t >= y)].sum() / (te - y) for i, y in enumerate(yc)])
        cum = np.cumsum(r[::-1])[::-1]
        ax.step(mb, np.where(cum > 0, cum, np.nan), where="mid", color="0.45", lw=1.4, label="catalogue", zorder=4)
        for i, (mc, y0, y1) in enumerate(per):
            k = (t >= y0) & (t < y1) & (mw >= mc - 1e-6) & (w > 0)
            if not k.any():
                continue
            m = np.round(np.arange(mc, mw[k].max() + 0.05, 0.1), 1)
            n = np.array([w[k][mw[k] >= x - 1e-6].sum() for x in m]) / (y1 - y0)
            ax.plot(m, n, "o", ms=st["ms"], color=st["colors"][i], mec="black", mew=st["mew"], alpha=st["alpha"], zorder=3,
                    label=f"{y0:.0f}–{min(y1, 2026):.0f}")
        cc = B.mfd(F[(c, "taper")])[1]
        lo, hi = (np.cumsum(B.mfd(F[(c, "taper")], ab)[2][::-1])[::-1] for ab in ("p05", "p95"))
        ax.fill_between(cc - B.G.DM / 2, lo, hi, color="0.55", alpha=0.3, lw=0, label="(a, b) 5–95 %", zorder=2)
        for sh, ls, lab in (("taper", "-", "tapered"), ("trunc", "--", "cut")):
            f, cc, nn = B.mfd(F[(c, sh)])
            plot_mfd(cc - B.G.DM / 2, nn, ax=ax, label=lab, color="black", ls=ls, lw=st["fit_lw"], legend=False, zorder=5)
        darkgrid(ax)
        q = F[(c, "taper")]
        ax.set_title(f"{palette.CLASS_NAME.get(c, c)}, b {q.b:.2f}, Mmax {q.mmax:.1f}", fontsize=12)
        ax.set_xlabel("Mw")
        ax.set_ylabel("")
        ax.set_ylim(1e-5, 60)
        ax.set_xlim(4.9, 9.1)
    axs[0].set_ylabel("N(≥ Mw) per year")
    axs[0].legend(fontsize=9, loc="lower left", frameon=False)
    fig.suptitle("In-slab sources against the catalogue", x=0.01, ha="left")
    F7.save(fig, "mfd_sources")


def kernel_ll():
    """Test log-likelihood against the kernel n, per class and declustering option, relative to the best n."""
    plt = F7.plt_()
    cal = pd.read_csv(B.TAB / f"calibration_{B.DATE}.csv")
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True, layout="constrained")
    for ax, k in zip(axs, B.DECL):
        for c in list(B.CLASSES) + ["family"]:
            q = cal[(cal.decl == k) & (cal.unit == c)].sort_values("n")
            name, col = (palette.CLASS_NAME[c], palette.CLASS_COLOR[c]) if c in B.CLASSES else ("all in-slab", "0.4")
            ls = "--" if c == "family" else "-"
            ax.plot(q.n, q.dll, ls, marker="o", ms=4, color=col, label=f"{name} ({q.n_test.iloc[0]:.0f} test events)")
            b = q[q.best]
            ax.plot(b.n, b.dll, "o", ms=9, mfc="none", mec=col, mew=1.5)
        ax.axvspan(0.85, B.N_MIN * 0.9, color="0.93", zorder=0, lw=0)
        ax.set_xscale("log")
        ax.set_xlim(0.85, 118)
        ax.set_xticks(B.CANDIDATES, [str(n) for n in B.CANDIDATES])
        ax.minorticks_off()
        ax.set_ylim(-40, 3)
        ax.axhline(-2, color="0.6", lw=0.8, ls=":")
        ax.set_xlabel("kernel n (neighbour of the bandwidth)")
        ax.set_title(f"{DECL_NAME[k]} declustering")
        ax.legend(fontsize=9, loc="lower left", frameon=False)
    axs[0].set_ylabel("test log-likelihood − best")
    fig.suptitle("Kernel calibration: events before 2010 against 2010–2026 (circled: chosen n; shaded: scored, not chosen)", x=0.01, ha="left")
    F7.save(fig, "kernel_loglik")


def run():
    pat = pd.read_csv(B.TAB / f"pattern_{B.DATE}.csv")
    F = B.fits()
    maps(pat, F)
    sections(pat, F)
    mfds(F)
    kernel_ll()


if __name__ == "__main__":
    run()

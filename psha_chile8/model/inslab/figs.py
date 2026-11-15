"""Figures of C14 (run.py calls all_figs)."""
import numpy as np

import depth as D
import palette

FIG = D.HERE / "figs"
BASEMAP = D.REPO / "data" / "basemaps" / "basemap_chile_gray" / "basemap_gray.tif"
EXTENT = [-76.0, -63.0, -44.0, -17.0]
SECT_EVENTS = [-20.0, -21.5, -23.0, -27.0, -30.0, -33.0, -36.0, -38.0]
SECT_CELLS = [-20.0, -23.0, -30.0, -33.0, -38.0]
STRIP, XLIM, ZMAX = 50.0, (-60.0, 400.0), 260.0
SRC_COLOR = {"Riedel-Hornig": palette.SERIES[0], "catalogue": palette.SERIES[1]}
LAYER = ["#2166ac", "#7f7f7f", "#a50f15"]


def plt_():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    palette.apply()
    return plt


def save(fig, name, dpi=150):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=dpi)
    fig.clf()


def fig_hist(ev):
    plt = plt_()
    bands = np.arange(-44.0, -16.0, 2.0)[::-1]
    fig, axs = plt.subplots(4, 4, figsize=(15, 13), layout="constrained", sharex=True)
    bins = np.arange(-40, 121, 2.5)
    for ax, lo in zip(axs.flat, bands):
        k = (ev.lat >= lo) & (ev.lat < lo + 2)
        for src in ("catalogue", "Riedel-Hornig"):
            q = ev[k & (ev.source == src)]
            if len(q):
                ax.hist(q.d, bins, histtype="step", lw=1.6, color=SRC_COLOR[src], label=f"{src} ({len(q):,})")
        if k.sum() >= 20:
            ax.axvline(np.percentile(ev.d[k], D.Q_LOW), color="0.3", lw=0.8, ls="--")
        ax.axvline(0, color="k", lw=0.8)
        ax.set_title(f"{-lo - 2:.0f}–{-lo:.0f}° S", fontsize=12)
        ax.legend(fontsize=8, loc="upper right")
        ax.set_yticks([])
    for ax in axs.flat[len(bands):]:
        ax.set_visible(False)
    for ax in axs[-1]:
        ax.set_xlabel("km below the Slab2 top")
    fig.suptitle(f"Distance of the in-slab events below the Slab2 top (dashed: {D.Q_LOW:.0f} % of the band)", x=0.01, ha="left")
    save(fig, "hist_d_lat")


def sections(ev, lats, name, title, cells=None):
    import shapely.ops
    from pituplots.io import read_slab2
    from pituplots.sections import add_slab, profiles_from_line, project
    plt = plt_()
    top, thk = (read_slab2(D.SLAB[q]) for q in ("dep", "thk"))
    t = D.C.geoms(D.C.TRENCH)
    t = shapely.ops.linemerge(t) if t.geom_type != "LineString" else t
    line = max(t.geoms, key=lambda q: q.length) if t.geom_type != "LineString" else t
    prof = profiles_from_line(line, lats, width=2 * STRIP, side=(-60, -30), length=XLIM)
    fig, axs = plt.subplots(len(lats), 1, figsize=(12, 3.3 * len(lats)), layout="constrained")
    x = ev.sort_values("mw")
    for ax, p, lat in zip(axs, prof, lats):
        u, v = project(x.lon.to_numpy(), x.lat.to_numpy(), p)
        for src in ("catalogue", "Riedel-Hornig"):
            k = (np.abs(v) <= STRIP) & (u >= XLIM[0]) & (u <= XLIM[1]) & (x.source == src).to_numpy()
            ax.scatter(u[k], x.z.to_numpy()[k], s=3 if src == "Riedel-Hornig" else 5, color=SRC_COLOR[src],
                       alpha=0.35 if cells is None else 0.18, lw=0, rasterized=True, label=f"{src} ({k.sum():,})")
        add_slab(ax, p, top, thk)
        if cells is not None:
            cu, cv = project(cells.lon.to_numpy(), cells.lat.to_numpy(), p)
            k = (np.abs(cv) <= 5.0) & (cu >= XLIM[0]) & (cu <= XLIM[1])
            for l in range(3):
                ax.scatter(cu[k], cells[f"h{l + 1}"].to_numpy()[k], s=60 * cells[f"w{l + 1}"].to_numpy()[k] + 2,
                           color=LAYER[l], edgecolor="white", lw=0.3, zorder=5, label=f"hypocentre, layer {l + 1} (size: weight)")
            ax.plot(cu[k], cells.lsd.to_numpy()[k], color="k", lw=0.8, ls="--", zorder=4, label="lower seismogenic depth")
        ax.set_xlim(*XLIM)
        ax.set_ylim(ZMAX, -5)
        ax.set_aspect(1)
        ax.set_ylabel("depth [km]")
        ax.set_title(f"{-lat:.1f}° S, ± {STRIP:.0f} km", fontsize=12)
        ax.legend(loc="lower left", ncol=3, fontsize=8, markerscale=2)
    axs[-1].set_xlabel("distance from the trench [km]")
    fig.suptitle(title, x=0.01, ha="left")
    save(fig, name, dpi=130)


def maps(res, cols, titles, name, title, cmaps, lims):
    import cartopy.crs as ccrs
    from pituplots.maps import dress_map
    plt = plt_()
    fig = plt.figure(figsize=(4.2 * len(cols), 9.5), layout="constrained")
    pc = ccrs.PlateCarree()
    tr = __import__("shapely").get_coordinates(D.C.geoms(D.C.TRENCH))
    for j, (c, t, cm, lim) in enumerate(zip(cols, titles, cmaps, lims)):
        ax = fig.add_subplot(1, len(cols), j + 1, projection=pc)
        dress_map(ax, EXTENT, basemap=str(BASEMAP) if BASEMAP.exists() else None, gridlines=j == 0)
        ax.plot(tr[:, 0], tr[:, 1], color="0.35", lw=0.8, transform=pc)
        sc = ax.scatter(res.lon, res.lat, c=res[c], s=1.6, marker="s", cmap=cm, vmin=lim[0], vmax=lim[1], lw=0,
                        transform=pc, rasterized=True, zorder=3)
        fig.colorbar(sc, ax=ax, orientation="horizontal", shrink=0.85, pad=0.02)
        ax.set_title(t, fontsize=12)
    fig.suptitle(title, x=0.01, ha="left")
    save(fig, name)


def all_figs(ev, res):
    fig_hist(ev)
    sections(ev, SECT_EVENTS, "sections_events", "In-slab events used for the depth model, with the Slab2 top and bottom")
    sections(ev, SECT_CELLS, "sections_cells", "Cell hypocentres and layer weights over the events", cells=res)
    maps(res, ["w1", "w2", "w3", "dz_index"], ["top layer", "middle layer", "bottom layer", "double-zone index"],
         "maps_weights", "Layer weights per cell; index = mean of top and bottom weight − middle weight",
         ["viridis"] * 3 + ["RdBu_r"], [(0, 0.7)] * 3 + [(-0.4, 0.4)])
    r = res.assign(zone=res.lsd - res.top, dh=(res.w1 * res.h1 + res.w2 * res.h2 + res.w3 * res.h3) - res.old_hypo,
                   d1=res.h_one - res.old_hypo)
    maps(r, ["zone", "dh", "d1"], ["zone below the slab top", "mean hypocentre − old", "one-layer hypocentre − old"],
         "maps_zone", "Seismogenic zone (fraction of the Slab2 thickness) and hypocentres against psha_chile7 (km)",
         ["magma_r", "RdBu_r", "RdBu_r"], [(10, 50), (-20, 20), (-20, 20)])

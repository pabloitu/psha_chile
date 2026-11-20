"""Check figures of T8 and T9 (docs/FIGURE_STYLE.md): mechanism types per class on the Frohlich ternary, the class of
the crustal cells, the depth slices of the in-slab cells, and the depth cells against psha_chile8."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import shapely

from . import mech as M
from .figs import rc, save
from ..catalog.class_figs import CLASS
from ..catalog.figs import MERC, PC, basemap

CORNER = {"reverse": (1.2247, -0.7071), "normal": (-1.2247, -0.7071), "strike-slip": (0.0, 1.4142)}
EXT = [-77.0, -62.0, -56.5, -16.5]


def fig_ternary(out, ev, npd):
    q0 = ev[ev.inside]
    cls = list(dict.fromkeys(q0.cls))
    fig, axs = plt.subplots(2, 4, figsize=(6.9, 3.9))
    g = np.linspace(0, np.pi / 2, 100)
    for ax, c in zip(axs.flat, cls + [None]):
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_xlim(-1.45, 1.45)
        ax.set_ylim(-0.95, 1.6)
        if c is None:
            for m in (5, 6, 7):
                ax.scatter([], [], s=(m - 4.2) ** 3 * 2, color="0.5", alpha=0.6, label=f"Mw {m}")
            ax.scatter([], [], marker="*", s=80, color="0.7", edgecolor="0.1", lw=0.6, label="table plane\n(type weight)")
            ax.legend(loc="center", frameon=False, labelspacing=1.2, fontsize=6)
            continue
        q = q0[q0.cls == c].sort_values("mw")
        for i, k in enumerate(M.TYPES[:3]):
            lim = M.P["limits"][k]
            pl = np.zeros((g.size, 3))
            pl[:, i] = lim
            pl[:, [j for j in range(3) if j != i]] = np.degrees(np.arcsin(np.cos(np.radians(lim)) * np.c_[np.cos(g), np.sin(g)]))
            ax.plot(*M.ternary(pl), color="0.75", lw=0.5, zorder=1)
        tri = np.array([CORNER["normal"], CORNER["reverse"], CORNER["strike-slip"], CORNER["normal"]])
        ax.plot(*tri.T, color="0.4", lw=0.6, zorder=1)
        ax.scatter(q.x, q.y, s=(q.mw - 4.2) ** 3 * 2, color=CLASS[c][1], alpha=0.2 + 0.5 * q.w, edgecolor="white", lw=0.2, zorder=2)
        r = npd[npd.cls == c]
        fx, fy = M.ternary(M.plunges(*r[["strike", "dip", "rake"]].to_numpy(float).T))
        ax.scatter(fx, fy, marker="*", s=40 + 160 * r.weight, color=CLASS[c][1], edgecolor="0.1", lw=0.6, zorder=3)
        for x, y, w in zip(fx, fy, r.weight):
            ax.text(x + 0.08, y + 0.05, f"{w:.2f}", fontsize=5.5, zorder=4)
        for k, (x, y) in CORNER.items():
            ax.text(x, y + (0.08 if k == "strike-slip" else -0.1), k, ha="center", va="bottom" if k == "strike-slip" else "top", fontsize=5.5, color="0.35")
        ax.text(-1.4, 1.5, f"{CLASS[c][0]}\n{q.w.sum():.0f} by weight", fontsize=6, va="top")
    fig.tight_layout(pad=0.3)
    save(fig, out / "figs" / "ternary.png")


def mesh(ax, df, col, **kw):
    q = df.pivot_table(index="lat", columns="lon", values=col)
    lo, la = q.columns.to_numpy(), q.index.to_numpy()
    return ax.pcolormesh(np.r_[lo - 0.05, lo[-1] + 0.05], np.r_[la - 0.05, la[-1] + 0.05], q.to_numpy(float), transform=PC, zorder=3, **kw)


def panels(n, ext=EXT, w=6.9, h=4.6):
    fig = plt.figure(figsize=(w, h))
    axs = []
    for i in range(n):
        ax = fig.add_axes([0.005 + i * 0.99 / n, 0.12, 0.99 / n - 0.006, 0.87], projection=MERC)
        ax.set_extent(ext, PC)
        basemap(ax, ext, px=500)
        axs.append(ax)
    return fig, axs


def bar(fig, ax, sc, label):
    p = ax.get_position()
    cax = fig.add_axes([p.x0 + 0.1 * p.width, 0.07, 0.8 * p.width, 0.015])
    cb = fig.colorbar(sc, cax=cax, orientation="horizontal")
    cb.set_label(label, fontsize=6)
    cb.ax.tick_params(labelsize=5.5)


def fig_cells(out, cells, dat):
    cls = ["forearc", "arc", "backarc", "patagonia"]
    x = cells.assign(k=cells.cls.map({c: i for i, c in enumerate(cls)}))
    fig, (ax,) = panels(1, w=2.6)
    cmap = matplotlib.colors.ListedColormap([CLASS[c][1] for c in cls])
    mesh(ax, x, "k", cmap=cmap, vmin=-0.5, vmax=3.5, alpha=0.85)
    for f in json.loads((dat / "crustal_classes.geojson").read_text())["features"]:
        for p in getattr(shapely.geometry.shape(f["geometry"]), "geoms", [shapely.geometry.shape(f["geometry"])]):
            ax.plot(*p.exterior.xy, color="0.15", lw=0.4, transform=PC, zorder=4)
    h = [plt.Rectangle((0, 0), 1, 1, color=CLASS[c][1]) for c in cls]
    fig.legend(h, [CLASS[c][0] for c in cls], loc="lower center", ncol=2, fontsize=5.5, frameon=False)
    save(fig, out / "figs" / "crustal_cells.png")


def fig_depth(out, res, name="depth_slices.png"):
    r = res.assign(zone=res.lsd - res.top, one=res.h_one - res.top)
    cols = [("zone", "zone below the slab top (km)", "magma_r", (10, 50)), ("w1", "top slice weight", "viridis", (0, 0.7)),
            ("w2", "middle slice weight", "viridis", (0, 0.7)), ("w3", "bottom slice weight", "viridis", (0, 0.7)),
            ("one", "one layer below the top (km)", "magma_r", (5, 30))]
    ext = [-76.0, -62.0, -46.5, -16.5]
    fig, axs = panels(len(cols), ext)
    for ax, (c, lab, cm, lim) in zip(axs, cols):
        bar(fig, ax, mesh(ax, r, c, cmap=cm, vmin=lim[0], vmax=lim[1]), lab)
    save(fig, out / "figs" / name)


def fig_vs8(out, res, old, j, k):
    o = old.iloc[j[k]].reset_index(drop=True)
    r = res[k].reset_index(drop=True)
    mh = lambda x: x.w1 * x.h1 + x.w2 * x.h2 + x.w3 * x.h3
    r = r.assign(dz=(r.lsd - r.top) - (o.lsd - o.top), d1=r.w1 - o.w1, d2=r.w2 - o.w2, d3=r.w3 - o.w3, dh=mh(r) - mh(o))
    cols = [("dz", "zone, km", 10), ("d1", "top weight", 0.3), ("d2", "middle weight", 0.3), ("d3", "bottom weight", 0.3), ("dh", "mean hypocentre, km", 10)]
    ext = [-76.0, -62.0, -46.5, -16.5]
    fig, axs = panels(len(cols), ext)
    for ax, (c, lab, v) in zip(axs, cols):
        bar(fig, ax, mesh(ax, r, c, cmap="RdBu_r", vmin=-v, vmax=v), f"{lab}: now − 18 Nov")
    save(fig, out / "figs" / "depth_vs_psha8.png")


def run(out, ev, npd, cells, dat, dev, res, old, j, k):
    rc()
    fig_ternary(out, ev, npd)
    fig_cells(out, cells, dat)
    from .depth import Z
    fig_depth(out, res[Z["set"]])
    fig_vs8(out, res[Z["set"]], old, j, k)

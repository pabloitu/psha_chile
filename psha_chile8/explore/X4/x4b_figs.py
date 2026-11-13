"""X4 (classification): maps per class, sections at six latitudes coloured by class, and the changes between rule
variants. Needs the tables of x4b_classify.py."""
import numpy as np
import pandas as pd

import x4b_classify as X

FIG = X.HERE / "figs"
SECTIONS = [-20.0, -23.0, -27.0, -31.0, -33.5, -37.0]
STRIP, XLIM, ZMAX, LAND_CAP = 50.0, (-60.0, 400.0), 250.0, 400.0
EXTENT = [-80, -62, -58, -16]
# draft colours and display names for the new classes (palette.py has none yet)
COL = {"interface": "#2166ac", "intraslab_shallow": "#f0505a", "intraslab_intermediate": "#a50f15", "jujuy_nest": "#6b3d1a",
       "crustal forearc": "#ffb000", "crustal arc": "#2e8b57", "crustal backarc": "#8c6d1f", "crustal Patagonia": "#8c510a",
       "outer rise": "#17a2a2", "below slab": "#4d4d4d", "unknown depth": "#9a9a9a", "unclassified": "#111111"}
NAME = {"intraslab_shallow": "in-slab, shallow (slab top < 50 km)", "intraslab_intermediate": "in-slab, intermediate depth",
        "jujuy_nest": "Jujuy nest", "unclassified": "between crust and slab, or no slab model"}
PANELS = [("Interface", ["interface"]), ("In-slab", X.SUB),
          ("Crustal: forearc and arc", ["crustal forearc", "crustal arc"]), ("Crustal: backarc and Patagonia", ["crustal backarc", "crustal Patagonia"]),
          ("Outer rise", ["outer rise"]), ("Depth unknown", ["unknown depth"]),
          ("Below the plate, or unclassified", ["below slab", "unclassified"])]


def size(m):
    return np.clip(m - 3.5, 0.5, 6) ** 2 * 4


def load():
    x = pd.read_csv(X.TAB / "x4b_events_m45.csv", low_memory=False)
    x["show"] = np.where(x["sub"].fillna("") != "", x["sub"], x.cls)
    x.loc[(x.cls == "in-slab") & (x[X.tag({**X.BASE, "below": "unclassified"})] == "below slab"), "show"] = "below slab"
    return x.sort_values("mw").reset_index(drop=True)


def trench_line():
    import shapely
    import shapely.ops
    g = X.geoms(X.TRENCH)
    g = shapely.ops.linemerge(g) if g.geom_type != "LineString" else g
    return max(g.geoms, key=lambda q: q.length) if g.geom_type != "LineString" else g


def fig_maps(plt, x):
    import cartopy.crs as ccrs
    import shapely
    from pituplots.maps import dress_map
    tr = [shapely.get_coordinates(X.geoms(f)) for f in (X.TRENCH, X.TRENCH_AN)]
    arc = shapely.get_coordinates(shapely.boundary(X.geoms(X.ARC)))
    fig = plt.figure(figsize=(21, 8.6), layout="constrained")
    for j, (title, keys) in enumerate(PANELS):
        ax = fig.add_subplot(1, len(PANELS), j + 1, projection=ccrs.PlateCarree())
        dress_map(ax, EXTENT, coastline=True, gridlines=j == 0)
        for c in tr:
            ax.plot(c[:, 0], c[:, 1], color="0.35", lw=0.8, transform=ccrs.PlateCarree())
        ax.plot(arc[:, 0], arc[:, 1], color="0.55", lw=0.6, ls="--", transform=ccrs.PlateCarree())
        for k in keys:
            y = x[x.show == k]
            ax.scatter(y.lon, y.lat, s=size(y.mw) * 0.6, color=COL[k], lw=0.2, edgecolor="white", alpha=0.8, transform=ccrs.PlateCarree(),
                       label=f"{NAME.get(k, k)}\n{len(y):,} events, {(y.mw >= 7).sum()} of Mw ≥ 7", rasterized=True, zorder=3)
        ax.set_title(title, fontsize=12)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.03), fontsize=9, markerscale=0.8)
    fig.suptitle(f"Classes of the baseline rule, Mw ≥ {X.MMIN} (lines: trenches; dashed: arc polygon)", x=0.01, ha="left")
    fig.savefig(FIG / "x4b_maps.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def section(ax, p, x, top, thk, band=None, label=True, s=None, zmax=ZMAX):
    from pituplots.sections import add_slab, project, sample, unproject
    u, v = project(x.lon.to_numpy(), x.lat.to_numpy(), p)
    k = (np.abs(v) <= STRIP) & (u >= XLIM[0]) & (u <= min(XLIM[1], LAND_CAP))
    unk = (~x.known).to_numpy()
    z, m = x.z.to_numpy(), x.mw.to_numpy()
    for key in [q for q in COL if ((x.show == q).to_numpy() & k & ~unk).any()]:
        q = k & ~unk & (x.show == key).to_numpy()
        ax.scatter(u[q], z[q], s=size(m[q]) if s is None else s, color=COL[key], alpha=0.8, lw=0.3 if s is None else 0, edgecolor="white",
                   label=f"{NAME.get(key, key)} ({q.sum()})", zorder=3, rasterized=s is not None)
    q = k & unk
    if q.any():
        ax.scatter(u[q], np.full(q.sum(), -8.0), s=14, marker="v", color=np.where(x.show[q] == "outer rise", COL["outer rise"], COL["unknown depth"]),
                   lw=0, label=f"depth unknown ({q.sum()})", clip_on=False, zorder=3)
    if label:
        for i in np.flatnonzero(k & ~unk & (m >= 7)):
            ax.annotate(f"M {m[i]:.1f}", (u[i], z[i]), fontsize=9, xytext=(4, 4), textcoords="offset points", zorder=5)
    add_slab(ax, p, top, thk)
    if band:
        sx = np.arange(XLIM[0], XLIM[1], 5.0)
        zt = sample(top, *unproject(sx, sx * 0, p))
        for sg in (-1, 1):
            ax.plot(sx, np.where(zt <= X.IF_TOP, zt + sg * band, np.nan), color="0.3", lw=0.7, ls=":", zorder=4)
    ax.set_xlim(*XLIM)
    ax.set_ylim(zmax, -12)
    ax.set_aspect(1)
    ax.set_ylabel("depth [km]")
    return int(k.sum())


def fig_sections(plt, x):
    from pituplots.io import read_slab2
    from pituplots.sections import profiles_from_line
    top, thk = read_slab2(X.SLAB / "sam_slab2_dep_02.23.18.xyz"), read_slab2(X.SLAB / "sam_slab2_thk_02.23.18.xyz")
    prof = profiles_from_line(trench_line(), SECTIONS, width=2 * STRIP, side=(-60, -30), length=XLIM)
    fig, ax = plt.subplots(len(SECTIONS), 1, figsize=(12, 6.9 * len(SECTIONS)), layout="constrained")
    for a, p, lat in zip(ax, prof, SECTIONS):
        section(a, p, x, top, thk, band=X.BASE["w"])
        a.set_title(f"{-lat:.1f}° S, {STRIP:.0f} km either side, Mw ≥ {X.MMIN} (dotted: interface band ± {X.BASE['w']:.0f} km)")
        a.legend(loc="lower left", ncol=3, fontsize=9)
    ax[-1].set_xlabel("distance from the trench [km]")
    fig.savefig(FIG / "x4b_sections.png", dpi=130)
    plt.close(fig)


def fig_variants(plt):
    c = pd.read_csv(X.TAB / "x4b_changes.csv")
    c = c[c.against == "baseline"].reset_index(drop=True)
    lab = [f"± {r.w:.0f} km, {'with' if r.sig else 'no'} σ, {'with' if r.mech else 'no'} mechanisms, below the plate {'in-slab' if r.below == 'in-slab' else 'apart'}"
           for r in c.itertuples()]
    fig, ax = plt.subplots(1, 3, figsize=(15, 8.5), layout="constrained", sharey=True)
    y = np.arange(len(c))[::-1]
    for a, m in zip(ax, X.BIG):
        v = c[f"class_m{m:g}"].astype(float)
        a.barh(y, v, color=np.where(c.variant == X.tag(X.BASE), "0.2", "#4292c6"), height=0.7)
        for yy, vv in zip(y, v):
            a.text(vv, yy, f" {vv:.0f}", va="center", fontsize=9)
        a.set_title(f"Mw ≥ {m:g}")
        a.set_xlabel("events in another class than under the baseline")
        a.set_xlim(0, v.max() * 1.15 + 1)
    ax[0].set_yticks(y, lab, fontsize=9)
    fig.suptitle("How many events change class with the rule (baseline: ± 15 km, no σ, with mechanisms, below the plate in-slab)", x=0.01, ha="left")
    fig.savefig(FIG / "x4b_variants.png", dpi=150)
    plt.close(fig)


def run():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import palette
    palette.apply()
    FIG.mkdir(exist_ok=True)
    x = load()
    fig_maps(plt, x)
    fig_sections(plt, x)
    fig_variants(plt)


if __name__ == "__main__":
    run()

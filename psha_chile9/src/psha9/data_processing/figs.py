"""DATA check figures: overview map, zoom on 45-47° S, new areas against the psha_chile8 domains.

Usage: python -m psha9.data_processing.figs run_dir
"""
import sys
from pathlib import Path

import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import from_bounds

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[3]
BASEMAP = ROOT / "data/raw/basemaps/basemap_chile_2026-11-21/basemap_color_trench.tif"
CAT = ROOT / "trials/data_qgis/catalog_17g.gpkg"
OLD = ROOT / "trials/data_qgis/psha8_class_domains.geojson"
PB = ROOT / "data/raw/trenches/pb2002_antarctic_trench_2026-11-15.geojson"
PC = ccrs.PlateCarree()
MERC = ccrs.Mercator()

# class colours and names (psha_chile8 palette.py, until psha9.common.plots exists)
CLASS = {"interface": ("interface", "#4682b4"), "antarctic_interface": ("Antarctic interface", "#9dc3e0"),
         "intraslab_shallow": ("in-slab, shallow", "#b23a3a"), "intraslab_intermediate": ("in-slab, intermediate", "#7f1d1d"),
         "jujuy_nest": ("Jujuy nest", "#4a0f0f"), "forearc": ("crustal, forearc", "#e8c21c"),
         "arc": ("crustal, arc", "#5e7a2a"), "backarc": ("crustal, backarc", "#a3b81f"),
         "patagonia": ("crustal, Patagonia", "#6b4423"), "outside": ("crustal, outside", "#c8cdbf"),
         "outer_rise": ("outer rise", "#85638e"), "unclassified": ("unclassified", "#111111")}
CR, IS, IF, ANT = "#5e7a2a", "#7f1d1d", "#4682b4", "#9dc3e0"
plt.rcParams.update({"font.family": "Ubuntu", "font.size": 7})


def catalog(mmin=4.5):
    layers = ["events_crustal", "events_inslab", "events_interface", "events_other"]
    c = pd.concat([gpd.read_file(CAT, layer=k, ignore_geometry=True) for k in layers])
    return c[c.mw >= mmin].sort_values("mw")


def size(mw):
    return 2.0 * 3.5 ** (mw - 4.5)


def basemap(ax, ext, px=1600):
    with rasterio.open(BASEMAP) as r:
        w = from_bounds(ext[0], ext[2], ext[1], ext[3], r.transform).intersection(
            rasterio.windows.Window(0, 0, r.width, r.height))
        n = max(1, int(w.height / px))
        a = r.read([1, 2, 3, 4], window=w, out_shape=(4, int(w.height / n), int(w.width / n)), resampling=Resampling.average)
        b = rasterio.windows.bounds(w, r.transform)
    ax.imshow(np.moveaxis(a, 0, -1), extent=[b[0], b[2], b[1], b[3]], transform=PC, origin="upper", zorder=0)


def events(ax, c, alpha=0.55):
    ax.scatter(c.lon, c.lat, s=size(c.mw), c=[CLASS.get(k, ("", "#999999"))[1] for k in c.subclass],
               alpha=alpha, lw=0.15, edgecolor="#333333", transform=PC, zorder=3)


def outline(ax, g, color, lw=0.8, ls="-", z=4):
    for geom in gpd.GeoSeries(g).explode(index_parts=False):
        if geom.is_empty:
            continue
        x, y = geom.exterior.xy if geom.geom_type == "Polygon" else geom.xy
        ax.plot(x, y, color=color, lw=lw, ls=ls, transform=PC, zorder=z)


def legend_classes(fig, keys, extra=(), ncol=7, y=0.01):
    h = [Line2D([], [], ls="", marker="o", ms=5, mfc=CLASS[k][1], mec="#333333", mew=0.3, label=CLASS[k][0]) for k in keys]
    fig.legend(handles=h + list(extra), loc="lower center", ncol=ncol, frameon=False, bbox_to_anchor=(0.5, y), fontsize=6)


def axes(fig, rect, ext):
    ax = fig.add_axes(rect, projection=MERC)
    ax.set_extent(ext, crs=PC)
    gl = ax.gridlines(draw_labels=True, lw=0.2, color="w", alpha=0.6)
    gl.top_labels = gl.right_labels = False
    return ax


def layers(run):
    d = {k: gpd.read_file(run / f"{k}.geojson") for k in ("edge", "crustal_area", "inslab_area", "interface_footprints",
                                                         "interface_segment_limits", "antarctic_plane")}
    return d


def overview(run, c, d):
    fig = plt.figure(figsize=(6.9, 6.6))
    fp = d["interface_footprints"]
    fp = fp[(fp.top == 0) & (fp.bottom == 50) & (fp.segment != "margin")]
    for i, ext in enumerate([(-76.5, -63, -36, -15.5), (-76.5, -63, -56.5, -36)]):
        ax = axes(fig, [0.04 + 0.49 * i, 0.16, 0.45, 0.83], ext)
        basemap(ax, ext)
        events(ax, c)
        outline(ax, d["crustal_area"].geometry, CR, 1.0)
        outline(ax, d["inslab_area"].geometry, IS, 1.0, "--")
        outline(ax, fp.geometry, IF, 0.9)
        outline(ax, d["antarctic_plane"].geometry, ANT, 0.9)
        outline(ax, d["interface_segment_limits"].geometry, IF, 0.6, ":")
        outline(ax, d["edge"].geometry, "k", 1.2, z=5)
    extra = [Line2D([], [], color="k", lw=1.2, label="western edge"), Line2D([], [], color=CR, lw=1, label="crustal area"),
             Line2D([], [], color=IS, lw=1, ls="--", label="in-slab area"),
             Line2D([], [], color=IF, lw=0.9, label="interface segments, edge–50 km"),
             Line2D([], [], color=ANT, lw=0.9, label="Antarctic plane")]
    legend_classes(fig, [k for k in CLASS if k in set(c.subclass)], extra, ncol=5)
    fig.savefig(run / "figs" / "overview.png", dpi=300)
    plt.close(fig)


def zoom(run, c, d, ext=(-79, -71, -47.5, -44.5)):
    fig = plt.figure(figsize=(5.5, 3.7))
    ax = axes(fig, [0.08, 0.2, 0.88, 0.78], ext)
    basemap(ax, ext, 800)
    x = c[c.lon.between(ext[0], ext[1]) & c.lat.between(ext[2], ext[3])]
    events(ax, x, 0.8)
    outline(ax, d["crustal_area"].geometry, CR, 1.0)
    outline(ax, d["inslab_area"].geometry, IS, 1.0, "--")
    fp = d["interface_footprints"]
    outline(ax, fp[(fp.top == 0) & (fp.bottom == 50) & (fp.segment == "seg1")].geometry, IF, 0.9)
    outline(ax, d["antarctic_plane"].geometry, ANT, 0.9)
    outline(ax, d["edge"].geometry, "k", 1.2, z=5)
    for la in (-45.6, -46.15):
        ax.plot([ext[0], ext[1]], [la, la], color="#555555", lw=0.6, ls=(0, (4, 3)), transform=PC, zorder=5)
        ax.text(ext[0] + 0.1, la + 0.04, f"{-la:.2f}° S", transform=PC, fontsize=6, zorder=6)
    extra = [Line2D([], [], color="k", lw=1.2, label="western edge"), Line2D([], [], color=CR, lw=1, label="crustal area"),
             Line2D([], [], color=IS, lw=1, ls="--", label="in-slab area"), Line2D([], [], color=IF, lw=0.9, label="seg1, edge–50 km"),
             Line2D([], [], color=ANT, lw=0.9, label="Antarctic plane")]
    legend_classes(fig, [k for k in CLASS if k in set(x.subclass)], extra, ncol=5)
    fig.savefig(run / "figs" / "zoom_45_47S.png", dpi=300)
    plt.close(fig)
    return x


def versus(run, d):
    old = gpd.read_file(OLD)
    fig = plt.figure(figsize=(6.9, 6.0))
    ext = (-80, -60, -58, -15.5)
    for i, (fam, new, col) in enumerate([("crustal", "crustal_area", CR), ("in-slab", "inslab_area", IS)]):
        ax = axes(fig, [0.03 + 0.49 * i, 0.1, 0.46, 0.88], ext)
        basemap(ax, ext, 1200)
        outline(ax, old[old.family == fam].union_all(), "#555555", 0.8, "--")
        outline(ax, d[new].geometry, col, 1.1)
        outline(ax, d["edge"].geometry, "k", 0.8, z=5)
        ax.text(0.03, 0.03, fam, transform=ax.transAxes, fontsize=8)
    h = [Line2D([], [], color=CR, lw=1.1, label="new crustal area"), Line2D([], [], color=IS, lw=1.1, label="new in-slab area"),
         Line2D([], [], color="#555555", lw=0.8, ls="--", label="psha_chile8 domain"), Line2D([], [], color="k", lw=0.8, label="western edge")]
    fig.legend(handles=h, loc="lower center", ncol=4, frameon=False)
    fig.savefig(run / "figs" / "areas_vs_psha8.png", dpi=300)
    plt.close(fig)


def classes(run, d, mmin=4.0):
    """Crustal classes (Q-75) with the crustal events of the newest classified catalogue, coloured by the class
    polygon they fall in (the catalogue's own sub-class may come from older shapes)."""
    import shapely
    col = {"forearc": "#ffb000", "arc": "#2e8b57", "backarc": "#8c6d1f", "patagonia": "#c2a5cf"}
    cl = gpd.read_file(run / "crustal_classes.geojson").set_index("cls").geometry
    c = pd.read_csv(sorted((ROOT / "runs/catalog").glob("cat-*/catalog.csv"))[-1], low_memory=False,
                    usecols=["lon", "lat", "mw", "w_crustal"])
    c = c[(c.mw >= mmin) & (c.w_crustal >= 0.5)].sort_values("mw")
    k = np.full(len(c), "outside", object)
    for n, g in cl.items():
        k[shapely.contains_xy(g, c.lon.to_numpy(), c.lat.to_numpy())] = n
    fig = plt.figure(figsize=(6.9, 6.6))
    for i, ext in enumerate([(-76.5, -63, -36, -15.5), (-76.5, -63, -56.5, -36)]):
        ax = axes(fig, [0.04 + 0.49 * i, 0.12, 0.45, 0.87], ext)
        basemap(ax, ext)
        for n, g in cl.items():
            ax.add_geometries([g], PC, fc=col[n], alpha=0.25, ec=col[n], lw=0.8, zorder=1)
        ax.scatter(c.lon, c.lat, s=size(c.mw), c=[col.get(x, "#c8cdbf") for x in k], alpha=0.8, lw=0.2,
                   edgecolor="w", transform=PC, zorder=3)
        outline(ax, d["edge"].geometry, "k", 1.0, z=5)
    h = [Line2D([], [], ls="", marker="o", ms=6, mfc=v, mec="w", label=f"crustal, {'Patagonia' if n == 'patagonia' else n}")
         for n, v in col.items()]
    h += [Line2D([], [], ls="", marker="o", ms=6, mfc="#c8cdbf", mec="w", label="crustal, outside the area"),
          Line2D([], [], color="k", lw=1.0, label="western edge")]
    fig.legend(handles=h, loc="lower center", ncol=6, frameon=False, fontsize=6.5)
    fig.savefig(run / "figs" / "crustal_classes.png", dpi=300)
    plt.close(fig)


def main(run):
    run = Path(run)
    (run / "figs").mkdir(exist_ok=True)
    c, d = catalog(), layers(run)
    overview(run, c, d)
    zoom(run, c, d)
    versus(run, d)
    classes(run, d)


if __name__ == "__main__":
    main(sys.argv[1])

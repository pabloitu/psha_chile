"""Maps of the catalogue domain on the gray basemap, without pituPLOTS: the domain in Mercator, a north and a south
panel of equal height, the marker size by magnitude, and the legends."""
import sys
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import rasterio
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "catalog"))
from locate import DOMAIN

BASEMAP = ROOT.parent / "data" / "basemaps" / "basemap_chile_gray" / "basemap_gray.tif"
EXTENT = [*DOMAIN["lon"], *DOMAIN["lat"]]
# extent of the catalogue figures: the domain without the far-west outer rise and the Scotia events south of Cape
# Horn (figures only; the catalogue keeps them)
FIG_EXTENT = [-76.5, DOMAIN["lon"][1], -56.0, DOMAIN["lat"][1]]
PROJ = ccrs.Mercator(central_longitude=sum(DOMAIN["lon"]) / 2)
PC = ccrs.PlateCarree()
COAST = {"color": "black", "lw": 0.6, "scale": "50m"}
GRID = {"color": "0.55", "lw": 0.4, "alpha": 0.5}
DLON = 2.0
ALPHA = 0.55
# growth of the marker area per magnitude unit
GROW = 3.5


def size(m, k=1.0, grow=GROW):
    """Marker area (pt²): 2 at Mw 4.5, grow times larger per magnitude unit; no magnitude drawn as Mw 3."""
    return k * 2.0 * grow ** (np.clip(np.nan_to_num(np.asarray(m, float), nan=3.0), 3, 9.5) - 4.5)


def bands(n=2, ext=FIG_EXTENT, proj=PROJ):
    """n latitude bands of ext, north first, of equal height in the map projection."""
    y = proj.transform_points(PC, np.full(2, ext[0]), np.array(ext[2:]))[:, 1]
    la = [PC.transform_point(ext[0], v, proj)[1] for v in np.linspace(y[1], y[0], n + 1)]
    la[0], la[-1] = ext[3], ext[2]
    return [[ext[0], ext[1], la[i + 1], la[i]] for i in range(n)]


def halves(ext=FIG_EXTENT, proj=PROJ):
    """North and south extents, split at the middle of the height in the map projection."""
    n, s = bands(2, ext, proj)
    return [("north", n), ("south", s)]


def panel_size(ext, width, proj=PROJ):
    """Width and height (inches) of a map axes on ext, width given."""
    p = proj.transform_points(PC, np.array(ext[:2]), np.array(ext[2:]))
    return width, width * (p[1, 1] - p[0, 1]) / (p[1, 0] - p[0, 0])


def basemap(ax, ext, f=BASEMAP, px=1600):
    """Draw the window of the GeoTIFF that covers ext, read at about px pixels along its longer side."""
    with rasterio.open(f) as r:
        w = from_bounds(ext[0] - 0.5, ext[2] - 0.5, ext[1] + 0.5, ext[3] + 0.5, r.transform).round_offsets().round_lengths()
        s = max(w.width, w.height) / px
        a = r.read(window=w, out_shape=(r.count, max(1, int(w.height / s)), max(1, int(w.width / s))), boundless=True, fill_value=0)
        b = r.window_bounds(w)
    ax.imshow(np.moveaxis(a, 0, -1), extent=(b[0], b[2], b[1], b[3]), origin="upper", transform=PC, zorder=0,
              interpolation="lanczos")


def box(ext, proj=None, n=60):
    """Projected bounding box (x0, x1, y0, y1) of the lon/lat box ext, from its densified outline."""
    proj = proj or PROJ
    t = np.linspace(0, 1, n)
    lo = np.r_[ext[0] + (ext[1] - ext[0]) * t, np.full(n, ext[1]), ext[0] + (ext[1] - ext[0]) * t, np.full(n, ext[0])]
    la = np.r_[np.full(n, ext[2]), ext[2] + (ext[3] - ext[2]) * t, np.full(n, ext[3]), ext[2] + (ext[3] - ext[2]) * t]
    q = proj.transform_points(PC, lo, la)[:, :2]
    return q[:, 0].min(), q[:, 0].max(), q[:, 1].min(), q[:, 1].max()


def domain_map(fig, pos, ext, labels="left", coast=True, dlat=3.0, fs=8, pbox=None):
    """A map axes on ext (lon/lat box) in PROJ with the basemap, coastline and gridlines. The axes shows the projected
    bounding box of ext, or pbox (x0, x1, y0, y1 in PROJ) when given; ext is then taken as the lon/lat range of pbox.
    labels: "left" or "right" (outside the frame), "inside" (where the grid lines meet the left and bottom edges,
    inside the map) or None."""
    ax = fig.add_subplot(*pos, projection=PROJ)
    if pbox is not None:
        x0, x1, y0, y1 = pbox
        t = np.linspace(0, 1, 60)
        q = PC.transform_points(PROJ, np.r_[x0 + (x1 - x0) * t, np.full(60, x1), x0 + (x1 - x0) * t, np.full(60, x0)],
                                np.r_[np.full(60, y0), y0 + (y1 - y0) * t, np.full(60, y1), y0 + (y1 - y0) * t])
        ext = [q[:, 0].min(), q[:, 0].max(), q[:, 1].min(), q[:, 1].max()]
    else:
        x0, x1, y0, y1 = box(ext)
    ax.set_extent((x0, x1, y0, y1), crs=PROJ)
    basemap(ax, [ext[0] - 1.5, ext[1] + 1.5, ext[2] - 0.5, ext[3] + 0.5])
    if coast:
        ax.add_feature(cf.COASTLINE.with_scale(COAST["scale"]), edgecolor=COAST["color"], linewidth=COAST["lw"], zorder=2)
    xs, ys = np.arange(-180, 180, DLON), np.arange(-90, 90, dlat)
    out = labels in ("left", "right")
    gl = ax.gridlines(crs=PC, draw_labels=out, zorder=1, xlocs=xs, ylocs=ys, **GRID)
    if out:
        gl.top_labels = False
        gl.left_labels, gl.right_labels = labels == "left", labels == "right"
    elif labels == "inside":
        kw = dict(fontsize=fs, color="0.25", zorder=6, clip_on=True)
        dx, dy = 0.01 * (x1 - x0), 0.01 * (y1 - y0)
        la = np.linspace(ext[2] - 3, ext[3] + 3, 400)
        lo = np.linspace(ext[0] - 3, ext[1] + 3, 400)
        for x in xs[(xs > ext[0] - 3) & (xs < ext[1] + 3)]:
            q = PROJ.transform_points(PC, np.full(400, x), la)
            xb = np.interp(y0, q[:, 1], q[:, 0])
            if x0 + 6 * dx < xb < x1 - 6 * dx:
                ax.text(xb, y0 + dy, f"{abs(x):g}°W", ha="center", va="bottom", **kw)
        for y in ys[(ys > ext[2] - 3) & (ys < ext[3] + 3)]:
            q = PROJ.transform_points(PC, lo, np.full(400, y))
            yb = np.interp(x0, q[:, 0], q[:, 1])
            if y0 + 6 * dy < yb < y1 - 3 * dy:
                ax.text(x0 + dx, yb, f"{abs(y):g}°S", ha="left", va="center", **kw)
    return ax


def size_handles(ms, k=1.0, color="0.4"):
    """Legend handles of marker sizes, one per magnitude in ms."""
    return [plt.scatter([], [], s=size(m, k), c=color, edgecolors="none", label=f"{m:g}") for m in ms]


def color_handles(colors, labels):
    """Legend handles of colours."""
    return [plt.Line2D([], [], ls="", marker="o", ms=7, mfc=c, mec="none", label=t) for c, t in zip(colors, labels)]

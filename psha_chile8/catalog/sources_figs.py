"""The source catalogs at a glance: figs/sources/<RUN_DATE>/sources_maps (preferred epicentres per source on the
catalogue domain) and sources_time (one time lane per source), PNG and PDF.

Every event of every source is drawn, coloured by the largest magnitude the source gives (as figs/profile/) and sized
by area growing 2.5 times per magnitude unit. Run from catalog/: /data/miniforge3/envs/psha_renta/bin/python sources_figs.py
"""
import sys
from pathlib import Path

import matplotlib
import matplotlib.path
matplotlib.use("Agg")
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import palette as pal
from locate import DOMAIN
from profile import TITLE, band
from pituplots.maps import dress_map
from pituplots.style.axes import darkgrid

# settings
SRC = HERE / "sources"
RUN_DATE = "2026-11-17"
FIGS = HERE / "figs" / "sources" / RUN_DATE
BASEMAP = HERE.parent.parent / "data" / "basemaps" / "basemap_chile_gray" / "basemap_gray.tif"
EXTENT = [*DOMAIN["lon"], *DOMAIN["lat"]]
PROJ = ccrs.Mercator(central_longitude=sum(DOMAIN["lon"]) / 2)
RUN = ["comcat", "isc", "csn_isc", "csn", "potin", "iscehb", "iscgem", "centennial", "gccel", "gcmt", "cabello", "rm2018"]
NAMES = {"csn_isc": "CSN in ISC", "csn": "CSN (sismologia.cl)", "gccel": "GCCEL", "centennial": "Centennial",
         "comcat": "ComCat", "isc": "ISC Bulletin"}
BAND = dict(pal.BAND, **{"no magnitude": "#9a9a9a"})
ALPHA = 0.55
LEG = [("M 5", 5.0), ("6", 6.0), ("7", 7.0), ("8", 8.0), ("9", 9.0)]


def size(m):
    """Marker area in pt², 0.5 at M 3 and 2.5 times larger per magnitude unit; no magnitude drawn as M 3."""
    return 0.5 * 2.5 ** (np.clip(np.nan_to_num(m, nan=3.0), 3, 9.5) - 3)


def handles():
    return [plt.scatter([], [], s=size(m), c=BAND[band(pd.Series([m])).iloc[0]], edgecolors="none", label=k)
            for k, m in LEG]


pal.apply()
FIGS.mkdir(parents=True, exist_ok=True)
d = {}
for s in RUN:
    ev = pd.read_csv(sorted(SRC.glob(f"{s}_2*_events.csv"))[-1], low_memory=False)
    mg = pd.read_csv(sorted(SRC.glob(f"{s}_2*_mags.csv"))[-1], low_memory=False)
    ev = ev[ev.prime.astype(str) == "True"].copy()
    ev["m"] = ev.src_id.map(mg.groupby("src_id").mag.max())
    ev["year"] = pd.to_numeric(ev.time.astype(str).str[:4], errors="coerce")
    ev["b"] = band(ev.m)
    d[s] = ev.sort_values("m", na_position="first")

# maps
pc = ccrs.PlateCarree()
t = np.linspace(0, 1, 60)
lo, la = EXTENT[0] + (EXTENT[1] - EXTENT[0]) * t, EXTENT[2] + (EXTENT[3] - EXTENT[2]) * t
ll = np.r_[np.c_[lo, np.full(60, EXTENT[2])], np.c_[np.full(60, EXTENT[1]), la], np.c_[lo[::-1], np.full(60, EXTENT[3])],
           np.c_[np.full(60, EXTENT[0]), la[::-1]]]
box = matplotlib.path.Path(PROJ.transform_points(pc, ll[:, 0], ll[:, 1])[:, :2])
fig = plt.figure(figsize=(10, 11.6), layout="constrained")
fig.get_layout_engine().set(w_pad=0.02, h_pad=0.04, wspace=0.0, hspace=0.0)
for i, s in enumerate(RUN):
    ev = d[s]
    ax = fig.add_subplot(2, 6, i + 1, projection=PROJ)
    dress_map(ax, EXTENT, basemap=str(BASEMAP), gridlines=False)
    ax.set_boundary(box, transform=ax.transData)
    ax.set_extent(EXTENT, crs=pc)
    ax.scatter(ev.lon, ev.lat, s=size(ev.m), c=ev.b.map(BAND), alpha=ALPHA, edgecolors="none", transform=pc, zorder=3,
               rasterized=True)
    n = (ev.lon.between(*DOMAIN["lon"]) & ev.lat.between(*DOMAIN["lat"])).sum()
    ax.set_title(f"{NAMES.get(s, TITLE[s])}\n{n:,} of {len(ev):,}\n{int(ev.year.min())}–{int(ev.year.max())}",
                 fontsize=8.5, pad=3)
fig.legend(handles=handles(), loc="outside lower center", ncol=5, columnspacing=1.0,
           title="largest magnitude the source gives; M < 5 as dots")
for e in ("png", "pdf"):
    fig.savefig(FIGS / f"sources_maps.{e}", dpi=150)

# time lanes
fig, ax = plt.subplots(figsize=(12, 6), layout="constrained")
darkgrid(ax)
for i, s in enumerate(RUN):
    ev = d[s]
    t = pd.to_datetime(ev.time, errors="coerce", format="ISO8601")
    x = (t.dt.year + (t.dt.dayofyear - 0.5) / 365.25).fillna(ev.year + 0.5)
    y = i + np.random.default_rng(0).uniform(-0.32, 0.32, len(ev))
    ax.scatter(x, y, s=size(ev.m), c=ev.b.map(BAND), alpha=ALPHA, edgecolors="none", rasterized=True)
ax.set_yticks(range(len(RUN)), [NAMES.get(s, TITLE[s]) for s in RUN])
ax.invert_yaxis()
ax.set_xlim(1500, 2027)
ax.set_xscale("function", functions=(lambda x: np.sign(x - 1500) * np.abs(x - 1500) ** 3,
                                     lambda x: 1500 + np.sign(x) * np.abs(x) ** (1 / 3)))
ax.set_xticks([1500, 1700, 1800, 1850, 1900, 1950, 1975, 2000, 2025])
ax.set_xlabel("year (stretched towards the present)")
fig.legend(handles=handles(), loc="outside lower center", ncol=5, columnspacing=1.0, title="M < 5 as dots")
for e in ("png", "pdf"):
    fig.savefig(FIGS / f"sources_time.{e}", dpi=150)

"""Paper candidate: focal mechanisms of the final catalogue in three latitude bands, each panel on its own
longitude range at one map scale, the compressional quadrants in the class colour. Mechanisms: the catalogue's (GCMT,
ComCat from 1976; before, the literature mechanisms listed by ISC-GEM). Named events
without any mechanism (catalog/named_events.csv) as circles of the same size rule; labels for the named events marked
label = 1; the events of Mw >= 4.5 as gray dots behind."""
import sys
from pathlib import Path

import matplotlib

# settings
# EDIT = True opens the map with draggable labels (run from PyCharm); closing the window writes their positions to
# label_lon, label_lat of named_events.csv. A label with a position there is drawn there; the others are placed
# automatically.
EDIT = False
matplotlib.use("QtAgg" if EDIT else "Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Circle
from obspy.imaging.beachball import beach

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "catalog")]
from plots import colors as C
from plots import maps as M
import cartopy.crs as ccrs

RUN = "2026-11-17g"
CAT = ROOT / "catalog" / "frozen" / RUN / f"catalog_{RUN}.csv"
# map projection: "utm" (EPSG:32719, UTM 19 S) or "mercator" (plots.maps); labels are stored in lon/lat and follow it
PROJ = "utm"
# UTM panels (km, x0, x1, y0, y1): three equal boxes, 930 km wide, 1381 km high, from 17° S to 54.4° S; the north box
# reaches the east edge of the Jujuy nest (66.1° W)
UTM_BOX = [(-120, 810, 6739, 8120), (-250, 680, 5357, 6739), (-225, 705, 3896, 5277)]
NAMED = ROOT / "catalog" / "named_events.csv"
OUT = ROOT / "catalog" / "FIGURES" / "maps"
# figure width (inches, two journal columns) and the extent of each panel, north to south (lon west, east, lat south,
# north); the band edges keep the Aysén 2007 swarm (45.2-45.9° S) inside one panel
FIG_W = 7.1
EXT = [(-76.6, -65.0, -31.47, -17.0), (-77.8, -67.2, -44.0, -31.47), (-75.8, -66.5, -54.36, -44.0)]
# smallest magnitude with a beachball, per class family (crustal events are smaller)
MMIN = {"crustal": 5.0, "other": 6.0}
# diameter (km) at Mw 5, growing by sqrt(GROW) per magnitude unit (gentler than the point maps, so the great events
# do not cover their neighbours)
D5, GROW = 12.0, 2.5
FM_ALPHA, CIRCLE_ALPHA = 0.55, 0.45
LEFT = ["interface", "outer_rise"]
# classes of this figure: in-slab as one, the crustal sub-classes without the prefix; a crustal event outside the
# crustal grid is drawn as backarc east of OUT_LON, else forearc
FAM = {"interface": "w_interface", "inslab": "w_inslab", "crustal": "w_crustal", "outer_rise": "w_outer_rise"}
COLOR = {k: C.CLASS_COLOR[k] for k in ("interface", "forearc", "arc", "backarc", "patagonia", "outer_rise")}
COLOR["inslab"] = C.FAMILY_COLOR["inslab"]
NAME = {"interface": "Interface", "inslab": "In-slab", "forearc": "Forearc",
        "arc": "Arc", "backarc": "Backarc", "patagonia": "Patagonia", "outer_rise": "Outer rise"}
OUT_LON = -70.0
# crustal events are drawn above the others (a deep in-slab event often lies under the same epicentre)
CRUSTAL = ("forearc", "arc", "backarc", "patagonia")
# labels next to their event (offshore events to the west, onshore to the east), PAD_PT from the event's edge,
# moved apart vertically by at least GAP_PT (points); dx, dy of named_events.csv shift one label (km)
GAP_PT, PAD_PT = 6.0, 6.0
LABEL = dict(fontsize=4.8, color="0.1", zorder=7)
# class legend inside the southern panel (upper right corner of the box, axes fraction); the space below it is kept
# for the fault legend
LEG_AT = (0.97, 0.60)


def diam(m):
    return D5 * 1e3 * np.sqrt(GROW) ** (m - 5.0)


C.apply()
OUT.mkdir(parents=True, exist_ok=True)
c = pd.read_csv(CAT, low_memory=False)
c = c[c.in_domain & (c.mw >= 4.45)].copy()
f = pd.Series(list(FAM))[c[list(FAM.values())].to_numpy().argmax(axis=1)].to_numpy()
cr = c.sub_crustal.where(c.sub_crustal != "outside", np.where(c.lon > OUT_LON, "backarc", "forearc"))
c["lab"] = np.select([f == "interface", f == "inslab", f == "crustal"], ["interface", "inslab", cr.fillna("forearc")],
                     "outer_rise")
c = c[c.w_unclassified < 0.5]
nm = pd.read_csv(NAMED, dtype={"dx": float, "dy": float, "label_lon": float, "label_lat": float}).set_index("event_id")
c = c.join(nm, on="event_id")
m0 = np.where(c.cls == "crustal", MMIN["crustal"], MMIN["other"])
fm = c[c.strike1.notna() & ((c.mw >= m0 - 0.05) | c.name.notna())]
ci = c[c.name.notna() & c.strike1.isna()]
big = pd.concat([fm.assign(kind="fm"), ci.assign(kind="circle")]).sort_values("mw", ascending=False)

ext3 = [list(e) for e in EXT]
drag = []
if PROJ == "utm":
    # EPSG:32719 (UTM 19 S) written out: cartopy's EPSG object is limited to the zone (72-66° W)
    M.PROJ = ccrs.TransverseMercator(central_longitude=-69.0, central_latitude=0.0, false_easting=500000.0,
                                     false_northing=10000000.0, scale_factor=0.9996, approx=False)
    PB = [tuple(v * 1e3 for v in b) for b in UTM_BOX]
else:
    PB = [M.box(e) for e in ext3]
xy = [np.array(b).reshape(2, 2).T for b in PB]
big["py"] = M.PROJ.transform_points(M.PC, big.lon.to_numpy(), big.lat.to_numpy())[:, 1]
dx = [p[1, 0] - p[0, 0] for p in xy]
s = (FIG_W - 0.1) / sum(dx)
h = s * max(p[1, 1] - p[0, 1] for p in xy)
fig = plt.figure(figsize=(FIG_W, h + 0.05), layout="constrained")
fig.get_layout_engine().set(w_pad=0.01, h_pad=0.02, wspace=0.0, hspace=0.0)
gs = fig.add_gridspec(1, 3, width_ratios=dx)
for i, ext in enumerate(ext3):
    ax = M.domain_map(fig, (gs[i],), ext, labels="inside", fs=6, coast=False, pbox=PB[i])
    ax.set_anchor("N")
    bg = c[~c.event_id.isin(big.event_id)]
    ax.scatter(bg.lon, bg.lat, s=M.size(bg.mw) * 0.35, c=bg.lab.map(COLOR), alpha=0.35, edgecolors="none", transform=M.PC,
               zorder=3, rasterized=True)
    b = big[big.py.between(PB[i][2] - 2e5, PB[i][3] + 2e5)]
    p = M.PROJ.transform_points(M.PC, b.lon.to_numpy(), b.lat.to_numpy())[:, :2]
    for (x, y), r in zip(p, b.itertuples()):
        d, col = diam(r.mw), COLOR[r.lab]
        if r.kind == "fm":
            q = beach((r.strike1, r.dip1, r.rake1), xy=(x, y), width=d, linewidth=0.3, facecolor=col, edgecolor="0.15",
                      alpha=FM_ALPHA)
            q.set_zorder(4.5 if r.lab in CRUSTAL else 4)
            ax.add_collection(q)
        else:
            q = Circle((x, y), d / 2, facecolor=col, edgecolor="0.15", linewidth=0.4, alpha=CIRCLE_ALPHA,
                       zorder=4.4 if r.lab in CRUSTAL else 3.5)
            ax.add_patch(q)
    t = b[(b.label == 1) & b.py.between(PB[i][2], PB[i][3])].copy()
    t["x"], t["y"] = M.PROJ.transform_points(M.PC, t.lon.to_numpy(), t.lat.to_numpy())[:, :2].T
    x0, x1, y0, y1 = ax.get_extent()
    pt = (x1 - x0) / (s * dx[i] * 72)
    t["side"] = np.where(t.offshore.astype(bool) | t.lab.isin(LEFT), "left", "right")
    wd = (t.name.str.len() + 5) * 0.52 * LABEL["fontsize"] * pt + t.mw.map(diam) / 2 + PAD_PT * pt
    t.loc[(t.side == "right") & (t.x + wd > x1), "side"] = "left"
    t.loc[(t.side == "left") & (t.x - wd < x0), "side"] = "right"
    for side, u in t.groupby("side"):
        u = u.sort_values("y", ascending=False)
        sg = -1 if side == "left" else 1
        ty = np.minimum(u.y.to_numpy() + np.nan_to_num(u.dy.to_numpy()) * 1e3, y1 - GAP_PT * pt)
        for j in range(1, len(ty)):
            ty[j] = min(ty[j], ty[j - 1] - GAP_PT * pt)
        lo = y0 + 2.5 * GAP_PT * pt
        for j in range(len(ty) - 1, -1, -1):
            ty[j] = max(ty[j], lo)
            lo = ty[j] + GAP_PT * pt
        for r, yy in zip(u.itertuples(), ty):
            txt = f"{r.name}, {r.mw:.1f}"
            rad = diam(r.mw) / 2
            tx = r.x + sg * (rad + PAD_PT * pt)
            ha = "right" if side == "left" else "left"
            if np.isfinite(r.label_lon):
                tx, yy = M.PROJ.transform_point(r.label_lon, r.label_lat, M.PC)
                ha = "right" if tx < r.x else "left"
            w_ = (len(txt) * 0.52 * LABEL["fontsize"] + 3) * pt
            if ha == "left" and tx + w_ > x1:
                ha = "right"
            elif ha == "right" and tx - w_ < x0:
                ha = "left"
            far = np.hypot(tx - r.x, yy - r.y) - rad > 1.5 * PAD_PT * pt
            arrow = dict(arrowstyle="-", color="0.3", lw=0.3, shrinkA=1.0, shrinkB=rad / pt) if EDIT or far else None
            tt = ax.annotate(txt, xy=(r.x, r.y), xytext=(tx, yy), textcoords="data", ha=ha, va="center",
                             annotation_clip=False, arrowprops=arrow, **LABEL)
            tt.set_in_layout(False)
            ln, e = None, None
            drag.append((tt, r.Index, ln, e))
n = big.lab.value_counts()
keys = [o for o in NAME if n.get(o, 0)]
hc = M.color_handles([COLOR[o] for o in keys], [NAME[o] for o in keys])
fig.axes[2].legend(handles=hc, loc="upper right", bbox_to_anchor=LEG_AT, ncol=1, fontsize=6, markerscale=0.8, frameon=False,
                   labelspacing=0.4, handletextpad=0.3)
if EDIT:
    def save(*_):
        nm = pd.read_csv(NAMED)
        for tt, i, _, _ in drag:
            lon, lat = M.PC.transform_point(*tt.xyann, M.PROJ)
            nm.loc[nm.event_id == big.loc[i, "event_id"], ["label_lon", "label_lat"]] = round(lon, 3), round(lat, 3)
        nm.to_csv(NAMED, index=False)
        print("label positions saved to", NAMED, flush=True)

    keep = [tt.draggable(True) for tt, *_ in drag]
    fig.canvas.mpl_connect("button_release_event", save)
    print("drag the labels; every release saves the positions", flush=True)
    plt.show(block=True)
else:
    fig.savefig(OUT / f"mechanisms_{PROJ}.png", dpi=300)
    fig.savefig(OUT / f"mechanisms_{PROJ}.pdf")
print("beachballs", len(fm), f"(ISC-GEM literature {int((fm.mech_src == 'ISC-GEM literature').sum())})", "| circles", len(ci), "| labels",
      int((big.label == 1).sum()), "| size", fig.get_size_inches().round(2))

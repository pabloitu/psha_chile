"""A9: classes of the events around the Chile triple junction, with the new rules of classify.py on the frozen
catalogue and the accepted hints. Run from catalog/ with PYTHONPATH=.:.."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely

import classify as C
import palette as PAL

BOX, MMIN, LAB = (-80.0, -70.5, -50.0, -42.5), 4.5, 6.4
OUT = C.HERE / "figs" / "classify" / "triple_junction.png"
SHP = C.REPO / "data" / "shapefiles"

c = pd.read_csv(C.HERE / "merged" / "catalog_2026-11-14c.csv", low_memory=False)
o = pd.read_csv(C.HERE / "overrides_A6.csv")
h = o[(o.status == "accepted") & (o.property == "class_hint")].set_index("event_id").new_value
c["a6_class_hint"] = c.event_id.map(h).where(c.event_id.isin(h.index), c.a6_class_hint)
g, t, _ = C.run(c)
k = ((c.lon > BOX[0]) & (c.lon < BOX[1]) & (c.lat > BOX[2]) & (c.lat < BOX[3]) & (c.mw >= MMIN)).to_numpy()
x = c[k].assign(**{q: t[q].to_numpy()[k] for q in C.COLS + ["cls", "rule", "sub_interface", "sub_inslab", "sub_crustal"]},
                d_trench=g.d_trench.to_numpy()[k])
x["key"] = np.select([x.cls == "interface", x.cls == "in-slab", x.cls == "crustal", x.cls == "outer rise", x.cls == "unclassified"],
                     [x.sub_interface, x.sub_inslab, x.sub_crustal, "outer_rise", "unclassified"], "split")
x = x.sort_values("mw")

PAL.apply()
fig, ax = plt.subplots(figsize=(9.5, 10.5))
def lines(f):
    q = C.geoms(f)
    q = q if q.geom_type.endswith("LineString") else shapely.boundary(q)
    return [np.asarray(p.coords) for p in shapely.get_parts(q)]


for p in lines(SHP / "chile.shp"):
    ax.plot(*p.T, color="0.55", lw=0.4, zorder=0)
for p in lines(C.ARC):
    ax.plot(*p.T, color=PAL.CLASS_COLOR["arc"], lw=1.0, ls="--", zorder=1)
for f, ls in ((C.TRENCH, "-"), (C.TRENCH_AN, "-"), (SHP / "chile_rise.shp", ":")):
    for p in lines(f):
        ax.plot(*p.T, color="0.2", lw=1.2, ls=ls, zorder=1)
ax.axhline(C.SOUTH_LAT, color="0.5", lw=0.7, ls="-.", zorder=1)
for key, y in x.groupby("key", sort=False):
    ax.scatter(y.lon, y.lat, s=6 + 9 * (y.mw - 4.4) ** 2.2, color=PAL.CLASS_COLOR[key], edgecolor="k", lw=0.4, alpha=0.9,
               label=f"{PAL.CLASS_NAME[key]} ({len(y)})", zorder=3)
for r in x[x.mw >= LAB].itertuples():
    ax.annotate(f"{r.time[:10]}  {r.mw:.1f}", (r.lon, r.lat), xytext=(6, 5), textcoords="offset points", fontsize=8.5, zorder=4)
ax.text(BOX[0] + 0.15, C.SOUTH_LAT + 0.06, "46.15° S: Antarctic trench used south of here", fontsize=8.5, color="0.35")
ax.set(xlim=BOX[:2], ylim=BOX[2:], aspect=1 / np.cos(np.radians(46)), xlabel="Longitude", ylabel="Latitude",
       title=f"Classes around the Chile triple junction, Mw ≥ {MMIN} (labels: Mw ≥ {LAB})")
ax.legend(loc="lower left", fontsize=9, frameon=True, framealpha=0.9)
fig.savefig(OUT, dpi=160, bbox_inches="tight")
x[["event_id", "time", "lon", "lat", "depth", "mw", "key", "rule", "d_trench"]].sort_values("time").to_csv(
    C.HERE.parent / "explore" / "A9" / "tj_events.csv", index=False)
print(x.key.value_counts().to_string())
print(x[x.mw >= 5.5].sort_values("time")[["time", "lon", "lat", "depth", "mw", "key", "rule", "d_trench"]].round(1).to_string(index=False))

# Beachball images of every catalog event with a focal mechanism, for the QGIS
# seismicity map, and a points table that links each event to its image.
# Reads results/cat_handler_2/catalog.csv; writes results/cat_handler_2/beachballs/:
#   <id>.png         one transparent beachball per event, filled with the colour
#                    of its class (file name: the catalog id, characters other
#                    than letters, digits, . _ - replaced by _)
#   beachballs.csv   id, png (absolute path), longitude, latitude, depth, mag,
#                    class, mech_src, mech_type and the nodal planes
# In QGIS: load beachballs.csv as delimited text (x longitude, y latitude,
# EPSG:4326) and set the marker to a raster image fill whose path is the
# field png (data-defined override), size scaled with mag if wanted.

import re
import sys
from concurrent.futures import ProcessPoolExecutor

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from obspy.imaging.beachball import MomentTensor, beachball, mt2plane

from cat_handler_2 import config as C

OUT = C.OUT / "beachballs"
SIZE_PT, DPI = 220, 50
PLANE = 1
COLORS = {"slab_interface": "#00bfff", "patagonia_interface": "#1e90ff", "intra_slab": "#008080", "slab_deep": "#008080",
          "deep_nest": "#006464", "forearc": "#ffa500", "intraarc": "#b22222", "backarc": "#9370db",
          "patagonia_crustal": "#cd853f", "outer_rise": "#deb887", "unclassified": "#6495ed", "deep_unknown": "#969696",
          "unresolved": "#969696"}
SDR = ["strike1", "dip1", "rake1", "strike2", "dip2", "rake2"]
MT = ["Mrr", "Mtt", "Mpp", "Mrt", "Mrp", "Mtp"]


def name(i):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(i).strip())


def sdr(r):
    """Nodal plane PLANE of the row, else a nodal plane of its moment tensor; None without either."""
    p = SDR[:3] if PLANE == 1 else SDR[3:]
    if all(np.isfinite(r[k]) for k in p):
        return tuple(float(r[k]) for k in p)
    if all(np.isfinite(r.get(k, np.nan)) for k in MT):
        n = mt2plane(MomentTensor([r[k] for k in MT], 1))
        return n.strike, n.dip, n.rake
    return None


def draw(job):
    path, plane, color = job
    fig = plt.figure(figsize=(SIZE_PT / 72, SIZE_PT / 72), dpi=72)
    beachball(plane, width=SIZE_PT, facecolor=color, edgecolor="black", linewidth=0.8, bgcolor="w", fig=fig)
    for a in fig.axes:
        a.set_axis_off()
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close(fig)
    return path


def main(src=None):
    OUT.mkdir(parents=True, exist_ok=True)
    ev = pd.read_csv(src or C.OUT / "catalog.csv", dtype={"id": str}, low_memory=False)
    for c in SDR + MT:
        ev[c] = pd.to_numeric(ev.get(c), errors="coerce")
    pl = ev.apply(sdr, axis=1)
    ev = ev[pl.notna()].assign(plane=pl[pl.notna()])
    ev["png"] = [str((OUT / f"{name(i)}.png").resolve()) for i in ev["id"]]
    jobs = [(p, pl_, COLORS.get(c, "#7f7f7f")) for p, pl_, c in zip(ev["png"], ev["plane"], ev["class"])]
    with ProcessPoolExecutor() as ex:
        n = sum(1 for _ in ex.map(draw, jobs, chunksize=50))
    cols = ["id", "png", "longitude", "latitude", "depth", "mag", "time_iso", "class", "cls_rule", "mech_src", "mech_type"] + SDR
    ev[[c for c in cols if c in ev]].to_csv(OUT / "beachballs.csv", index=False)
    print(f"{n} beachballs -> {OUT}; points table {OUT / 'beachballs.csv'}")
    print(ev["class"].value_counts().to_string())


if __name__ == "__main__":
    main(*sys.argv[1:2])
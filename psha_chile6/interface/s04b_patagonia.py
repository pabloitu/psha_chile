# Antarctic interface south of the Slab2 coverage, only with PATAGONIA: the PB2002 AN\SA trench
# resampled every PAT_STEP_KM, a plane of dip PAT_DIP to the right of the line (east), the band between
# PAT_Z_TOP and PAT_Z_BOTTOM, and the rate that releases the geodetic moment PAT_CHI * MU * A * PAT_V in
# each MFD form with the b of PAT_B_FROM. s05 writes the source into every interface branch file.
# Outputs: patagonia/patagonia.json, figures/s04b_patagonia.png

import json
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib import cfg, gr, nrml
from lib.dc import hav
from interface import config
from interface.s00_geometry import area

FORMS = ("tgr", "tapered")


def trench_line(path, name, lat_north, step_km):
    """
    Boundary `name` of a PB2002 geojson, south to north, extended or cut at lat_north and
    resampled every step_km.

    Returns
    -------
    lon, lat : arrays
    """
    g = json.loads(Path(path).read_text())
    f = next(x for x in g["features"] if x["properties"].get("Name") == name)
    xy = np.array(f["geometry"]["coordinates"], float)[:, :2]
    if xy[0, 1] > xy[-1, 1]:
        xy = xy[::-1]
    if xy[-1, 1] < lat_north:
        xy = np.vstack([xy, xy[-1] + (xy[-1] - xy[-2]) * (lat_north - xy[-1, 1]) / (xy[-1, 1] - xy[-2, 1])])
    elif xy[-1, 1] > lat_north:
        k = np.where(xy[:, 1] < lat_north)[0].max()
        p = xy[k] + (xy[k + 1] - xy[k]) * (lat_north - xy[k, 1]) / (xy[k + 1, 1] - xy[k, 1])
        xy = np.vstack([xy[:k + 1], p])
    d = np.r_[0.0, np.cumsum(hav(xy[:-1, 0], xy[:-1, 1], xy[1:, 0], xy[1:, 1]))]
    s = np.linspace(0.0, d[-1], max(int(round(d[-1] / step_km)), 1) + 1)
    return np.interp(s, d, xy[:, 0]), np.interp(s, d, xy[:, 1])


def bearing(lon, lat):
    """Azimuth (degrees from north) of the line at every node, by central differences."""
    dx = np.gradient(lon) * np.cos(np.radians(lat))
    return np.degrees(np.arctan2(dx, np.gradient(lat))) % 360.0


def destination(lon, lat, az, dist):
    """Great-circle point dist km from (lon, lat) along azimuth az (degrees)."""
    d, a, la1, lo1 = dist / 6371.0, np.radians(az), np.radians(lat), np.radians(lon)
    la2 = np.arcsin(np.sin(la1) * np.cos(d) + np.cos(la1) * np.sin(d) * np.cos(a))
    lo2 = lo1 + np.arctan2(np.sin(a) * np.sin(d) * np.cos(la1), np.cos(d) - np.sin(la1) * np.sin(la2))
    return np.degrees(lo2), np.degrees(la2)


def locked_edges(lon, lat, dip, z_trench, z_top, z_bottom, n_edges):
    """
    Edges of the band between z_top and z_bottom of a plane that dips to the right of the line
    and meets depth z_trench on it.

    Returns
    -------
    ndarray (n_edges, n_nodes, 3)
        lon, lat, depth; edge 0 is the top.
    """
    az = (bearing(lon, lat) + 90.0) % 360.0
    e = np.empty((n_edges, len(lon), 3))
    for i, z in enumerate(np.linspace(z_top, z_bottom, n_edges)):
        e[i, :, 0], e[i, :, 1] = destination(lon, lat, az, (z - z_trench) / np.tan(np.radians(dip)))
        e[i, :, 2] = z
    return e


def mmax_area(a_km2):
    """Maximum magnitude from the rupture area, Thingbaijam et al. (2017) interface, to 0.1."""
    return round((np.log10(a_km2) + 3.292) / 0.949, 1)


def source(c, pat, form, sid):
    """NRML complex fault of the Antarctic interface for one MFD form; its moment is checked."""
    inc, e = gr.inc(pat["lam"][form], form, pat["b"], c.MMIN_HAZ, pat["mmax"], c.BIN_W, c.M0_C, c.CORNER)
    mom = (inc * gr.m0(gr.mid(e, c.BIN_W), c.M0_C)).sum()
    if abs(mom / pat["m0_rate"] - 1) > 0.03:
        raise RuntimeError(f"{sid}: MFD moment {mom:.3e} vs {pat['m0_rate']:.3e}")
    edges = [[tuple(p) for p in ed] for ed in pat["edges"]]
    return nrml.complex_fault(sid, edges, c.TRT, nrml.mfd(inc, c.MMIN_HAZ, c.BIN_W), c.MSR, c.ASPECT, c.RAKE)


def main(c=None):
    c = c or cfg.load(config)
    if not c.PATAGONIA:
        return
    od = c.OUT / "patagonia"
    od.mkdir(parents=True, exist_ok=True)
    c.FIG.mkdir(parents=True, exist_ok=True)
    lon, lat = trench_line(c.PAT_TRENCH, c.PAT_NAME, c.PAT_LAT_NORTH, c.PAT_STEP_KM)
    e = locked_edges(lon, lat, c.PAT_DIP, c.PAT_Z_TRENCH, c.PAT_Z_TOP, c.PAT_Z_BOTTOM, c.N_EDGES)
    if e[-1, :, 0].mean() <= e[0, :, 0].mean():
        raise RuntimeError("the plane dips away from the continent: the line must run south to north")
    a = area(e)
    b = json.loads((c.OUT / "ab" / "ab.json").read_text())["segments"][c.PAT_B_FROM][c.AB_ESTIMATOR]["b"]
    mmax = c.PAT_MMAX or mmax_area(a)
    m0 = c.PAT_CHI * c.MU * a * 1e6 * c.PAT_V
    lam = {f: m0 / gr.mpr(f, b, c.MMIN_HAZ, mmax, c.M0_C, corner=c.CORNER) for f in FORMS}
    pat = {"area_km2": a, "length_km": float(np.sum(hav(lon[:-1], lat[:-1], lon[1:], lat[1:]))), "b": b, "mmax": mmax,
           "m0_rate": m0, "lam": lam, "dip": c.PAT_DIP, "v": c.PAT_V, "chi": c.PAT_CHI,
           "N7": {f: lam[f] * float(gr.cum(f, b, c.MMIN_HAZ, mmax, 7.0, c.M0_C, c.CORNER)) for f in FORMS},
           "N8": {f: lam[f] * float(gr.cum(f, b, c.MMIN_HAZ, mmax, 8.0, c.M0_C, c.CORNER)) for f in FORMS},
           "edges": e.round(5).tolist()}
    (od / "patagonia.json").write_text(json.dumps(pat))
    print(f"Antarctic interface {lat.min():.2f} to {lat.max():.2f} S: {pat['length_km']:.0f} km long, area {a:.0f} km2, "
          f"dip {c.PAT_DIP:g}, v {c.PAT_V * 1000:g} mm/yr, coupling {c.PAT_CHI:g}\n"
          f"  moment rate {m0:.3e} N m/yr, b {b:.3f} (from {c.PAT_B_FROM}), Mmax {mmax}\n"
          + "\n".join(f"  {f}: N(>={c.MMIN_HAZ}) {lam[f]:.4f}, N(>=7) {pat['N7'][f]:.4f}, N(>=8) {pat['N8'][f]:.4f} per year" for f in FORMS))
    f, ax = plt.subplots(figsize=(5, 9))
    ax.plot(lon, lat, "k", lw=1.5, label="PB2002 AN\\SA trench")
    ax.plot(e[0, :, 0], e[0, :, 1], "C0", label=f"top {c.PAT_Z_TOP:g} km")
    ax.plot(e[-1, :, 0], e[-1, :, 1], "C3", label=f"bottom {c.PAT_Z_BOTTOM:g} km")
    ax.set_aspect(1 / np.cos(np.radians(lat.mean())))
    ax.legend(fontsize=8)
    ax.set_title(f"dip {c.PAT_DIP:g}, {a:.0f} km2, Mmax {mmax}", fontsize=9)
    f.tight_layout()
    f.savefig(c.FIG / "s04b_patagonia.png", dpi=200)
    plt.close(f)
    cfg.snapshot(c, "s04b")


if __name__ == "__main__":
    main()

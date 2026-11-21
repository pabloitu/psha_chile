"""DATA build: western edge, areas cut to it, interface footprints, Antarctic plane, source grids and sites.

Usage: python -m psha9.data_processing.build [out_dir]
"""
import datetime
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml
import shapely
from shapely.geometry import Polygon


ROOT = Path(__file__).resolve().parents[3]
CFG = ROOT / "config" / "data.yaml"
R = 6371.0
CRS = "EPSG:4326"


def slab_grid(f):
    """Slab2 top as a regular grid: lon (-180..180), lat, depth (km, negative down, NaN off the slab)."""
    s = pd.read_csv(f, header=None, names=["x", "y", "z"])
    s["x"] = np.where(s.x > 180, s.x - 360, s.x)
    xs, ys = np.sort(s.x.unique()), np.sort(s.y.unique())
    z = s.pivot_table(index="y", columns="x", values="z", dropna=False).reindex(index=ys, columns=xs).values
    return xs, ys, z


def clean(g):
    """Geometry without repeated or collinear nodes (cutting at the edge repeats the shared nodes)."""
    return shapely.remove_repeated_points(g, 1e-9).simplify(0)


def trench(pb, name, lat_north=None, step=None):
    """PB2002 boundary `name`, south to north, optionally cut or extended to lat_north and resampled every step km."""
    xy = np.array(next(f for f in pb["features"] if f["properties"]["Name"] == name)["geometry"]["coordinates"])[:, :2]
    if xy[0, 1] > xy[-1, 1]:
        xy = xy[::-1]
    if lat_north is None:
        return xy
    if xy[-1, 1] < lat_north:
        xy = np.vstack([xy, xy[-1] + (xy[-1] - xy[-2]) * (lat_north - xy[-1, 1]) / (xy[-1, 1] - xy[-2, 1])])
    elif xy[-1, 1] > lat_north:
        k = np.where(xy[:, 1] < lat_north)[0].max()
        xy = np.vstack([xy[:k + 1], xy[k] + (xy[k + 1] - xy[k]) * (lat_north - xy[k, 1]) / (xy[k + 1, 1] - xy[k, 1])])
    la1, la2, dl = np.radians(xy[:-1, 1]), np.radians(xy[1:, 1]), np.radians(xy[1:, 0] - xy[:-1, 0])
    h = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin(dl / 2) ** 2
    s = np.r_[0.0, np.cumsum(2 * R * np.arcsin(np.sqrt(h)))]
    t = np.linspace(0.0, s[-1], max(int(round(s[-1] / step)), 1) + 1)
    return np.c_[np.interp(t, s, xy[:, 0]), np.interp(t, s, xy[:, 1])]


def plane(xy, dip, z0, top, bot, n):
    """
    Edges of the band top-bot of a plane dipping `dip` degrees to the right of the line xy (south to north), at
    depth z0 on the line.

    Returns
    -------
    ndarray (n, nnode, 3)
        lon, lat, depth; edge 0 is the top.
    """
    lon, lat = xy[:, 0], xy[:, 1]
    az = np.radians((np.degrees(np.arctan2(np.gradient(lon) * np.cos(np.radians(lat)), np.gradient(lat))) + 90) % 360)
    la1, lo1 = np.radians(lat), np.radians(lon)
    e = np.empty((n, len(lon), 3))
    for i, z in enumerate(np.linspace(top, bot, n)):
        d = (z - z0) / np.tan(np.radians(dip)) / R
        la2 = np.arcsin(np.sin(la1) * np.cos(d) + np.cos(la1) * np.sin(d) * np.cos(az))
        lo2 = lo1 + np.arctan2(np.sin(az) * np.sin(d) * np.cos(la1), np.cos(d) - np.sin(la1) * np.sin(la2))
        e[i] = np.c_[np.degrees(lo2), np.degrees(la2), np.full(len(lon), z)]
    return e


def grid(area, step, tol=1e-7):
    """Cell centres on multiples of step that lie inside area or on its boundary (within tol degrees, so float noise
    in the shapes or the cut at the edge does not decide a boundary row)."""
    x0, y0, x1, y1 = area.bounds
    xs = np.round(np.arange(np.floor(x0 / step), np.ceil(x1 / step) + 1) * step, 6)
    ys = np.round(np.arange(np.floor(y0 / step), np.ceil(y1 / step) + 1) * step, 6)
    X, Y = np.meshgrid(xs, ys)
    k = shapely.dwithin(shapely.points(X.ravel(), Y.ravel()), area, tol)
    return pd.DataFrame({"lon": X.ravel()[k], "lat": Y.ravel()[k]}).round(4).sort_values(["lat", "lon"], ascending=[False, True])


def main(out=None):
    cfg = yaml.safe_load(CFG.read_text())
    out = Path(out) if out else ROOT / "runs" / "data" / cfg["run"]
    if (out / "run.yaml").exists():
        raise SystemExit(f"{out} exists; a run is never edited")
    out.mkdir(parents=True, exist_ok=True)
    f = {k: ROOT / v for k, v in cfg["inputs"].items()}
    pb = json.loads(f["pb2002"].read_text())
    ec = cfg["edge"]

    # western edge: frozen as data (Pablo, 19 Nov), copied; everything east of it is kept
    eg = gpd.read_file(f["western_edge"])
    xy = np.array(eg.geometry.iloc[0].coords)
    east = Polygon(np.vstack([xy, [[ec["east"], xy[-1, 1]], [ec["east"], xy[0, 1]]]])).buffer(0)
    eg.to_file(out / "edge.geojson", driver="GeoJSON")
    pd.DataFrame({"lon": xy[:, 0], "lat": xy[:, 1]}).round(4).to_csv(out / "edge.csv", index=False)

    # areas: as drawn in data/raw/shapes (already cut to the edge by trials/data_shapes/cut_areas.py), cut to the edge
    areas = {}
    for k in ("crustal", "inslab"):
        a = clean(gpd.read_file(f[f"{k}_area"]).union_all().intersection(east))
        areas[k] = a
        gpd.GeoDataFrame([{"area": k, "geometry": a}], crs=CRS).to_file(out / f"{k}_area.geojson", driver="GeoJSON")
    if f["crustal_classes"].exists():
        c = gpd.read_file(f["crustal_classes"])
        c["geometry"] = c.geometry.intersection(areas["crustal"]).apply(clean)
        c.to_file(out / "crustal_classes.geojson", driver="GeoJSON")

    # interface footprints and segment limits: frozen as data (Pablo, 19 Nov), copied
    ic = cfg["interface"]
    fp = gpd.read_file(f["interface_footprints"])
    fp["area_km2"] = fp.to_crs("+proj=cea +lat_ts=-33").area.div(1e6).round(0)
    fp.to_file(out / "interface_footprints.geojson", driver="GeoJSON")
    gpd.read_file(f["segment_limits"]).to_file(out / "interface_segment_limits.geojson", driver="GeoJSON")

    # Antarctic plane
    a = ic["antarctic"]
    e = plane(trench(pb, a["name"], a["lat_north"], a["step"]), a["dip"], a["z0"], a["top"], a["bottom"], a["n"])
    pd.DataFrame([dict(edge=i, lon=p[0], lat=p[1], depth=p[2]) for i, ed in enumerate(e) for p in ed]).round(4).to_csv(
        out / "antarctic_plane_edges.csv", index=False)
    gpd.GeoDataFrame([{"segment": "antarctic", "top": a["top"], "bottom": a["bottom"],
                       "geometry": Polygon(np.vstack([e[0, :, :2], e[-1, ::-1, :2]]))}], crs=CRS).to_file(
        out / "antarctic_plane.geojson", driver="GeoJSON")

    # grids and sites
    for k, step in cfg["grids"].items():
        grid(areas[k], step).to_csv(out / f"{k}_grid.csv", index=False)
    c = gpd.read_file(f["cities"])
    pd.DataFrame({"name": c.name, "lon": c.geometry.x, "lat": c.geometry.y}).to_csv(out / "sites_cities.csv", index=False)
    pd.read_csv(f["site_grid"], usecols=["lon", "lat"]).round(5).to_csv(out / "sites_grid.csv", index=False)

    run = {"date": datetime.date.today().isoformat(), "reads": {k: str(v.relative_to(ROOT)) for k, v in f.items()
                                                                if v.exists() and k != "slab_top"}, "settings": cfg}
    (out / "run.yaml").write_text(yaml.safe_dump(run, sort_keys=False, allow_unicode=True))
    return out


if __name__ == "__main__":
    print(main(sys.argv[1] if len(sys.argv) > 1 else None))

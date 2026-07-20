# s00_geometry.py
# Build the global locked-interface geometry from Slab2, cut it into
# segments at exact boundary latitudes, compute true 3D areas, and export:
#   geometry/global_geometry.json      edges of the full locked interface
#   geometry/segments.json             per-segment sliced edges + areas
#   geometry/segments.shp              segment outline polygons (team review)
#   geometry/segment_areas.csv
#   figures/s00_*.png

import json

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Polygon

import sub_config as C

R_EARTH = 6371.0


# slab loading

def load_slab(path):
    df = pd.read_csv(path, header=None, names=["lon", "lat", "depth"])
    df["lon"] = np.where(df["lon"] > 180.0, df["lon"] - 360.0, df["lon"])
    df["depth"] = -df["depth"]
    return df[np.isfinite(df["depth"])].reset_index(drop=True)


# edge construction

def lon_at_depth(lon, depth, z):
    for i in range(len(depth) - 1):
        d1, d2 = depth[i], depth[i + 1]
        if min(d1, d2) <= z <= max(d1, d2):
            if d1 == d2:
                return float(lon[i])
            t = (z - d1) / (d2 - d1)
            return float(lon[i] + t * (lon[i + 1] - lon[i]))
    return None


def build_edges(df, lat_min, lat_max, z_top, z_bot, lat_step, n_edges):
    """
    Down-dip edges of the locked interface, sampled every lat_step.

    Per latitude the top node sits at max(z_top, slab top) and the bottom
    node at min(z_bot, slab max depth); n_edges nodes are interpolated
    linearly between them.

    Returns
    -------
    edges : ndarray (n_edges, n_lats, 3)
        lon, lat, depth per node, edge 0 = top, south -> north.
    """
    df = df[(df["lat"] >= lat_min) & (df["lat"] <= lat_max)]
    lats = np.sort(df["lat"].unique())
    keep = [lats[0]]
    for la in lats[1:]:
        if la - keep[-1] >= lat_step - 1e-6:
            keep.append(la)

    rows = []
    for la in keep:
        g = df[df["lat"] == la].sort_values("lon")
        lon, dep = g["lon"].to_numpy(), g["depth"].to_numpy()
        if len(lon) < 2 or dep.max() < C.MIN_SLAB_DEPTH:
            continue
        zt = max(z_top, float(dep.min()))
        zb = min(z_bot, float(dep.max()))
        lt = lon_at_depth(lon, dep, zt)
        lb = lon_at_depth(lon, dep, zb)
        if lt is None or lb is None:
            continue
        rows.append((la, lt, lb, zt, zb))

    if len(rows) < 3:
        raise RuntimeError(f"only {len(rows)} usable latitudes")

    la, lt, lb, zt, zb = map(np.asarray, zip(*rows))
    fr = np.linspace(0.0, 1.0, n_edges)
    edges = np.empty((n_edges, len(la), 3))
    for i, t in enumerate(fr):
        edges[i, :, 0] = lt + t * (lb - lt)
        edges[i, :, 1] = la
        edges[i, :, 2] = zt + t * (zb - zt)
    return edges


# segment slicing (exact cuts)

def cut_edges(edges, lat_lo, lat_hi):
    """
    Slice edges to [lat_lo, lat_hi], interpolating boundary nodes at the
    exact cut latitudes so adjacent segments share nodes (no gap/overlap).
    """
    lats = edges[0, :, 1]
    out = []
    for e in edges:
        pts = [_interp_node(e, lats, lat_lo)]
        inside = e[(lats > lat_lo + 1e-9) & (lats < lat_hi - 1e-9)]
        pts.extend(inside.tolist())
        pts.append(_interp_node(e, lats, lat_hi))
        out.append(np.array(pts))
    return out


def _interp_node(edge, lats, lat):
    lat = min(max(lat, lats[0]), lats[-1])
    j = np.searchsorted(lats, lat)
    if j == 0:
        return edge[0].copy()
    if lats[j - 1] == lat:
        return edge[j - 1].copy()
    t = (lat - lats[j - 1]) / (lats[j] - lats[j - 1])
    return edge[j - 1] + t * (edge[j] - edge[j - 1])


# area on the 3D mesh

def to_xyz(nodes):
    lon, lat, dep = np.radians(nodes[:, 0]), np.radians(nodes[:, 1]), nodes[:, 2]
    r = R_EARTH - dep
    return np.column_stack([
        r * np.cos(lat) * np.cos(lon),
        r * np.cos(lat) * np.sin(lon),
        r * np.sin(lat),
    ])


def mesh_area_km2(edges):
    """
    Area of the surface spanned by consecutive edges, each quad split into
    two triangles in ECEF coordinates.
    """
    area = 0.0
    for a, b in zip(edges[:-1], edges[1:]):
        pa, pb = to_xyz(np.asarray(a)), to_xyz(np.asarray(b))
        for j in range(len(pa) - 1):
            for t1, t2, t3 in ((pa[j], pa[j + 1], pb[j]),
                               (pb[j], pa[j + 1], pb[j + 1])):
                area += 0.5 * np.linalg.norm(np.cross(t2 - t1, t3 - t1))
    return area


# exports

def edges_to_json(edges):
    return [
        {
            "edge_index": i,
            "edge_type": "top" if i == 0 else
                         "bottom" if i == len(edges) - 1 else "intermediate",
            "nodes": [
                {"lon": float(p[0]), "lat": float(p[1]), "depth_km": float(p[2])}
                for p in e
            ],
        }
        for i, e in enumerate(edges)
    ]


def outline(edges):
    top, bot = np.asarray(edges[0]), np.asarray(edges[-1])
    ring = np.vstack([top[:, :2], bot[::-1, :2]])
    return Polygon(ring)


def main():
    C.GEOM_DIR.mkdir(parents=True, exist_ok=True)
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = load_slab(C.SLAB_XYZ)
    lat_min, lat_max = C.SEG_BOUNDS[0], C.SEG_BOUNDS[-1]
    edges = build_edges(df, lat_min, lat_max, C.Z_TOP, C.Z_BOTTOM,
                        C.LAT_STEP, C.N_EDGES)

    full_area = mesh_area_km2(edges)
    geom = {
        "geometry_id": "locked_interface_global",
        "lat_min": lat_min, "lat_max": lat_max,
        "locked_depth_range_km": [C.Z_TOP, C.Z_BOTTOM],
        "lat_step_deg": C.LAT_STEP,
        "area_km2": full_area,
        "edges": edges_to_json(edges),
    }
    (C.GEOM_DIR / "global_geometry.json").write_text(json.dumps(geom, indent=2))

    # segments
    segs, recs, polys = {}, [], []
    for sid, lo, hi in zip(C.SEG_IDS, C.SEG_BOUNDS[:-1], C.SEG_BOUNDS[1:]):
        se = cut_edges(edges, lo, hi)
        a = mesh_area_km2(se)
        segs[sid] = {"lat_min": lo, "lat_max": hi, "area_km2": a,
                     "edges": edges_to_json(se)}
        recs.append({"seg_id": sid, "lat_min": lo, "lat_max": hi,
                     "area_km2": round(a, 1)})
        polys.append(outline(se))

    (C.GEOM_DIR / "segments.json").write_text(json.dumps(segs, indent=2))

    tab = pd.DataFrame(recs)
    tab.loc[len(tab)] = {"seg_id": C.FULL_ID, "lat_min": lat_min,
                         "lat_max": lat_max, "area_km2": round(full_area, 1)}
    tab.to_csv(C.GEOM_DIR / "segment_areas.csv", index=False)

    gdf = gpd.GeoDataFrame(recs, geometry=polys, crs="EPSG:4326")
    gdf.to_file(C.GEOM_DIR / "segments.shp")

    # closure check: segment areas must sum to the global area
    sum_seg = sum(s["area_km2"] for s in segs.values())
    err = abs(sum_seg - full_area) / full_area
    print(tab.to_string(index=False))
    print(f"area closure: sum(segments)/global = {sum_seg / full_area:.6f}")
    if err > 1e-3:
        raise RuntimeError(f"segment areas do not close ({err:.2e})")

    # figures
    fig, ax = plt.subplots(figsize=(7, 10))
    piv = df.pivot_table(index="lat", columns="lon", values="depth")
    ax.pcolormesh(piv.columns, piv.index, piv.values, shading="auto",
                  cmap="viridis_r")
    for i, (sid, s) in enumerate(segs.items()):
        col = f"C{i}"
        for e in s["edges"]:
            xs = [n["lon"] for n in e["nodes"]]
            ys = [n["lat"] for n in e["nodes"]]
            ax.plot(xs, ys, col, lw=0.8)
        ax.text(np.mean(xs) + 1.5, 0.5 * (s["lat_min"] + s["lat_max"]),
                f"{sid}\n{s['area_km2']:.0f} km2", color=col, fontsize=8)
    for b in C.SEG_BOUNDS:
        ax.axhline(b, color="k", ls="--", lw=0.8)
    ax.set_xlabel("lon")
    ax.set_ylabel("lat")
    ax.set_title(f"locked interface {C.Z_TOP:.0f}-{C.Z_BOTTOM:.0f} km, "
                 f"exact cuts at {C.SEG_BOUNDS}")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / "s00_segments_map.png", dpi=200)

    fig, ax = plt.subplots(figsize=(7, 4))
    for i, (sid, s) in enumerate(segs.items()):
        top = s["edges"][0]["nodes"]
        bot = s["edges"][-1]["nodes"]
        ax.plot([n["lat"] for n in top], [n["depth_km"] for n in top], f"C{i}-")
        ax.plot([n["lat"] for n in bot], [n["depth_km"] for n in bot], f"C{i}-",
                label=sid)
    ax.invert_yaxis()
    ax.set_xlabel("lat")
    ax.set_ylabel("depth km")
    ax.legend(fontsize=8)
    ax.set_title("top/bottom edge depths along strike")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / "s00_edge_depths.png", dpi=200)

    print(f"wrote geometry to {C.GEOM_DIR}")


if __name__ == "__main__":
    main()
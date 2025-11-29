# geometry.py
"""
Subduction interface geometry preprocessor (no OpenQuake dependencies).

Steps
-----
1. Load slab grid CSV (lon[0–360], lat, depth negative downward, NaN=no slab)
2. Convert to lon[-180,180], depth_km positive downward
3. Plot:
   - slab depth colormap
   - locked region (depth in [z_top_locked, z_bottom_locked] and lat within
     the geometry extent)
4. Build down-dip edges:
   - For each latitude:
       * find z_min (top of slab) and z_max_raw (deepest point)
       * ignore lats where z_max_raw < 20 km
       * define bottom depth z_bottom = min(z_bottom_locked, z_max_raw)
       * find lon at z_min and at z_bottom
       * linearly interpolate N edges between top and bottom
   - N is given by len(depth_levels); depth_levels themselves are "nominal"
     and no longer enforced as iso-depth contours.
5. Plot edges on slab
6. Export geometry to JSON text file for later use

Geometry is always built as ONE global locked interface. Later, segments are
defined by slicing these edges in latitude, so they automatically share
down-dip edges.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from subduction.config import GEOMETRY_CONFIG, GeometryConfig


# ---------------------------------------------------------------------------
# 1. Load and preprocess the slab grid
# ---------------------------------------------------------------------------

def load_slab_grid(csv_path: str | Path) -> pd.DataFrame:
    """
    Load slab grid and convert:
      - lon_raw in [0, 360) -> lon in [-180, 180]
      - depth_raw negative downward -> depth_km positive downward

    Expects CSV with 3 columns and no header:
        lon_raw, lat, depth_raw

    Returns DataFrame with columns:
        lon, lat, depth_km
    """
    df = pd.read_csv(
        csv_path,
        header=None,
        names=["lon_raw", "lat", "depth_raw"],
    )

    # lon: 0–360 -> -180–180
    lon = df["lon_raw"].to_numpy(float)
    lon = np.where(lon > 180.0, lon - 360.0, lon)

    # depth: negative downward -> positive downward; NaN stays NaN
    depth_raw = df["depth_raw"].to_numpy(float)
    depth_km = np.where(np.isfinite(depth_raw), -depth_raw, np.nan)

    df["lon"] = lon
    df["depth_km"] = depth_km

    df = df[["lon", "lat", "depth_km"]]
    return df


# ---------------------------------------------------------------------------
# 2. Grid/plot helpers
# ---------------------------------------------------------------------------

def build_depth_grid(df_slab: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Turn slab points into a regular 2D grid for plotting:
        depth_grid[ilat, ilon], lon_grid, lat_grid

    Assumes the input is a regular lon/lat grid.
    """
    pivot = df_slab.pivot(index="lat", columns="lon", values="depth_km")
    lats = pivot.index.values
    lons = pivot.columns.values
    depth_grid = pivot.values

    lon_grid, lat_grid = np.meshgrid(lons, lats)
    return lon_grid, lat_grid, depth_grid


def plot_slab_with_locked_region(
    df_slab: pd.DataFrame,
    z_top_locked: float,
    z_bottom_locked: float,
    lat_min_geom: float,
    lat_max_geom: float,
) -> None:
    """
    Plot slab depth as a colormap, and overlay the locked portion
    as a constant semi-transparent color.

    Locked region is defined by:
        depth_km in [z_top_locked, z_bottom_locked]
        AND lat in [lat_min_geom, lat_max_geom]
    """
    lon_grid, lat_grid, depth_grid = build_depth_grid(df_slab)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Full slab depth
    im = ax.pcolormesh(
        lon_grid, lat_grid, depth_grid,
        shading="auto",
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Depth (km, positive downward)")

    # Locked mask: depth band + latitude window
    locked_mask = (
        np.isfinite(depth_grid)
        & (depth_grid >= z_top_locked)
        & (depth_grid <= z_bottom_locked)
        & (lat_grid >= lat_min_geom)
        & (lat_grid <= lat_max_geom)
    )
    locked_grid = np.where(locked_mask, 1.0, np.nan)

    ax.pcolormesh(
        lon_grid, lat_grid, locked_grid,
        shading="auto",
        alpha=0.3,
    )

    ax.set_xlabel("Longitude (deg)")
    ax.set_ylabel("Latitude (deg)")
    ax.set_title(
        f"Slab depth and locked portion "
        f"({z_top_locked}–{z_bottom_locked} km, "
        f"{lat_min_geom}° ≤ lat ≤ {lat_max_geom}°)"
    )
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# 3. Helpers for top–bottom interpolation
# ---------------------------------------------------------------------------

def find_lon_at_depth(
    lon: np.ndarray,
    depth: np.ndarray,
    z: float,
) -> Optional[float]:
    """
    Given depth(lon) along one latitude, find the longitude where depth
    crosses z (by linear interpolation). Returns lon_z or None if no crossing.

    Assumes depth is roughly monotonic in the dip direction.
    """
    mask = np.isfinite(depth)
    lon = lon[mask]
    depth = depth[mask]
    if len(depth) < 2:
        return None

    for i in range(len(depth) - 1):
        d1, d2 = depth[i], depth[i + 1]

        # Skip if z is not between d1 and d2
        if (z < min(d1, d2)) or (z > max(d1, d2)):
            continue

        # If exactly equal
        if d1 == z:
            return float(lon[i])
        if d2 == z:
            return float(lon[i + 1])

        # Linear interpolation in lon
        t = (z - d1) / (d2 - d1)
        lon_z = lon[i] + t * (lon[i + 1] - lon[i])
        return float(lon_z)

    return None


def build_edges_from_slab(
    df_slab: pd.DataFrame,
    depth_levels: np.ndarray,
    z_top_locked: float,
    z_bottom_locked: float,
    lat_min: Optional[float] = None,
    lat_max: Optional[float] = None,
    lat_step_deg: float = 0.5,
    min_points: int = 3,
) -> Tuple[List[List[Tuple[float, float, float]]], List[float]]:
    """
    Build down-dip edges by interpolating between top and (locked) bottom
    of the slab at each latitude.

    For each latitude:
      - find z_min, z_max_raw (finite depths)
      - if z_max_raw < 20 km: skip this latitude (slab too shallow)
      - define bottom depth as:
            z_bottom = min(z_bottom_locked, z_max_raw)
      - top depth is z_min (actual top of slab)
      - find lon at z_min and at z_bottom
      - interpolate N edges between these two points

    N (number of down-dip edges) is taken as len(depth_levels), so
    existing calling code does not need to change. The values in
    depth_levels themselves are *nominal* and are no longer enforced
    as iso-depth contours.

    Args
    ----
    df_slab
        DataFrame with columns lon, lat, depth_km.
    depth_levels
        Array whose length defines the number of edges, N = len(depth_levels).
    z_top_locked
        Top of locked depth range (km, positive downward). Used only for
        diagnostics/plotting; the actual top edge uses z_min at each lat.
    z_bottom_locked
        Target bottom depth for the locked zone (e.g. 50 km).
    lat_min, lat_max
        Latitude window for the geometry. If None, the full slab extent
        is used on that side.
    lat_step_deg
        Approximate spacing between sampled latitudes.
    min_points
        Minimum number of latitudes required to build edges.

    Returns
    -------
    edges
        List of edges; each edge is a list of (lon, lat, depth_km) nodes
        ordered south → north.
    used_lats
        Sorted list of latitudes at which nodes were sampled.
    """
    # Restrict to finite depths
    df = df_slab[np.isfinite(df_slab["depth_km"])].copy()

    # Latitude window
    if lat_min is not None:
        df = df[df["lat"] >= lat_min]
    if lat_max is not None:
        df = df[df["lat"] <= lat_max]

    if df.empty:
        raise RuntimeError("No finite slab depths in requested latitude range")

    # Build per-lat profiles
    profiles: Dict[float, Tuple[np.ndarray, np.ndarray]] = {}
    for lat, group in df.groupby("lat"):
        g = group.sort_values("lon")
        lon = g["lon"].to_numpy(float)
        depth = g["depth_km"].to_numpy(float)
        if len(lon) >= 2:
            profiles[float(lat)] = (lon, depth)

    if not profiles:
        raise RuntimeError("No latitudes with at least two slab points")

    # Sort all latitudes (south → north) and subsample to ~lat_step_deg
    all_lats = sorted(profiles.keys())

    sampled_lats = [all_lats[0]]
    for lat in all_lats[1:]:
        if lat - sampled_lats[-1] >= lat_step_deg - 1e-6:
            sampled_lats.append(lat)

    # For each sampled latitude, find top (z_min) and locked bottom (z_bottom)
    # and corresponding longitudes. Skip if z_max_raw < 20 km (hardcoded).
    MIN_DEPTH_MAX = 20.0  # km

    used_lats: List[float] = []
    lon_top_list: List[float] = []
    lon_bot_list: List[float] = []
    z_min_list: List[float] = []
    z_bot_list: List[float] = []

    for lat in sampled_lats:
        lon_arr, depth_arr = profiles[lat]

        mask = np.isfinite(depth_arr)
        if mask.sum() < 2:
            continue

        lon_valid = lon_arr[mask]
        depth_valid = depth_arr[mask]

        z_min = float(depth_valid.min())
        z_max_raw = float(depth_valid.max())

        # Skip very shallow lats: slab never gets deep enough
        if z_max_raw < MIN_DEPTH_MAX:
            continue

        # Bottom of locked zone for this latitude:
        #   - If slab reaches z_bottom_locked, clamp at z_bottom_locked
        #   - Otherwise, use the deepest available depth (z_max_raw)
        z_bottom = min(float(z_bottom_locked), z_max_raw)

        # Top longitude: at z_min (first occurrence)
        idx_min = int(depth_valid.argmin())
        lon_top = float(lon_valid[idx_min])

        # Bottom longitude: at z_bottom (interpolate if needed)
        lon_bot = find_lon_at_depth(lon_valid, depth_valid, z_bottom)
        if lon_bot is None:
            # Fallback: use lon at max depth
            idx_max = int(depth_valid.argmax())
            lon_bot = float(lon_valid[idx_max])

        used_lats.append(float(lat))
        lon_top_list.append(lon_top)
        lon_bot_list.append(float(lon_bot))
        z_min_list.append(z_min)
        z_bot_list.append(z_bottom)

    if len(used_lats) < min_points:
        raise RuntimeError(
            f"Too few latitudes with sufficient depth coverage: "
            f"{len(used_lats)} found (min_points={min_points})"
        )

    # Interpolate N edges between top and bottom along each latitude
    n_edges = int(len(depth_levels))
    if n_edges < 2:
        raise ValueError("depth_levels must contain at least two values")

    fractions = np.linspace(0.0, 1.0, n_edges)  # 0 = top, 1 = bottom
    edges: List[List[Tuple[float, float, float]]] = []

    for t in fractions:
        edge_nodes: List[Tuple[float, float, float]] = []
        for lat, lon_top, lon_bot, z_min, z_bottom in zip(
            used_lats, lon_top_list, lon_bot_list, z_min_list, z_bot_list
        ):
            lon_i = lon_top + t * (lon_bot - lon_top)
            depth_i = z_min + t * (z_bottom - z_min)
            edge_nodes.append((float(lon_i), float(lat), float(depth_i)))
        edges.append(edge_nodes)

    return edges, used_lats


# ---------------------------------------------------------------------------
# 4. Plot iso-depth(-ish) edges over the slab
# ---------------------------------------------------------------------------

def plot_edges_on_slab(
    df_slab: pd.DataFrame,
    edges: List[List[Tuple[float, float, float]]],
    title: Optional[str] = None,
) -> None:
    """
    Plot slab depth background and overlay edges.
    """
    lon_grid, lat_grid, depth_grid = build_depth_grid(df_slab)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Background slab depth
    im = ax.pcolormesh(
        lon_grid, lat_grid, depth_grid,
        shading="auto",
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Depth (km, positive downward)")

    # Overlay edges
    for edge in edges:
        xs = [p[0] for p in edge]  # lon
        ys = [p[1] for p in edge]  # lat
        ax.plot(xs, ys, "-", linewidth=1.5, color="k")

    ax.set_xlabel("Longitude (deg)")
    ax.set_ylabel("Latitude (deg)")
    ax.set_title(title or "Interpolated edges on slab")

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# 5. Export geometry to text (JSON)
# ---------------------------------------------------------------------------

def export_geometry_to_json(
    edges: List[List[Tuple[float, float, float]]],
    depth_levels: np.ndarray,
    used_lats: List[float],
    z_top_locked: float,
    z_bottom_locked: float,
    lat_max_locked: float,
    out_path: str | Path,
    geometry_id: str = "locked_interface_main",
    extra_metadata: Optional[dict] = None,
) -> None:
    """
    Export the interface geometry to a JSON text file.

    Structure (one global "segment"):

    {
      "segment_id": "segment_01",
      "name": "segment_01",
      "lat_min": ...,
      "lat_max": ...,
      "lat_min_geom": ...,
      "lat_max_geom": ...,
      "locked_depth_range_km": [z_top_locked, z_bottom_locked],
      "depth_levels_km": [...],   # nominal, for indexing
      "lat_step_deg_approx": ...,
      "edges": [
        {
          "edge_index": 0,
          "edge_type": "top",
          "depth_km": <nominal depth from depth_levels>,
          "nodes": [
            {"lon": ..., "lat": ..., "depth_km": ...},
            ...
          ]
        },
        ...
      ]
    }

    Note: node depths are the actual interpolated values; 'depth_km' per edge
    is a nominal value (from depth_levels) kept for convenience.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if len(edges) != len(depth_levels):
        raise ValueError("edges and depth_levels must have the same length")

    # Basic lat range from the used nodes
    all_lats = [p[1] for edge in edges for p in edge]
    lat_min = float(min(all_lats))
    lat_max = float(max(all_lats))

    # Approximate lat step from used_lats (if available)
    if len(used_lats) >= 2:
        lat_diffs = np.diff(sorted(used_lats))
        lat_step_deg_approx = float(np.median(lat_diffs))
    else:
        lat_step_deg_approx = None

    geom_obj = {
        "geometry_id": geometry_id,
        "name": geometry_id,
        "lat_min": lat_min,
        "lat_max": lat_max,
        "lat_max_locked": float(lat_max_locked),
        "locked_depth_range_km": [float(z_top_locked), float(z_bottom_locked)],
        "depth_levels_km": [float(d) for d in depth_levels],
        "lat_step_deg_approx": lat_step_deg_approx,
        "edges": [],
    }
    if extra_metadata:
        geom_obj["metadata"] = extra_metadata

    n_edges = len(edges)
    for ie, (edge, z_nominal) in enumerate(zip(edges, depth_levels)):
        if ie == 0:
            edge_type = "top"
        elif ie == n_edges - 1:
            edge_type = "bottom"
        else:
            edge_type = "intermediate"

        nodes = [
            {"lon": float(lon), "lat": float(lat), "depth_km": float(d)}
            for (lon, lat, d) in edge
        ]

        geom_obj["edges"].append(
            {
                "edge_index": ie,
                "edge_type": edge_type,
                "depth_km": float(z_nominal),  # nominal
                "nodes": nodes,
            }
        )

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(geom_obj, f, indent=2)


# ---------------------------------------------------------------------------
# 6. Config-driven entry point
# ---------------------------------------------------------------------------

def build_geometry_from_config(cfg: GeometryConfig = GEOMETRY_CONFIG) -> Path:
    """
    Build global locked-interface geometry using a GeometryConfig.

    Returns
    -------
    Path
        Path to the written JSON file.
    """
    # 1) Load and preprocess slab geometry
    df_slab = load_slab_grid(cfg.slab_csv)

    # 2) Determine geometry latitude extent from segments (if any)
    if cfg.segments:
        lat_mins = [s.lat_min for s in cfg.segments if s.lat_min is not None]
        lat_maxs = [s.lat_max for s in cfg.segments if s.lat_max is not None]

        if lat_mins:
            lat_min_geom = float(min(lat_mins))
        else:
            lat_min_geom = float(df_slab["lat"].min())

        if lat_maxs:
            lat_max_geom = float(max(lat_maxs))
        else:
            lat_max_geom = float(df_slab["lat"].max())
    else:
        lat_min_geom = float(df_slab["lat"].min())
        lat_max_geom = float(df_slab["lat"].max())

    # 3) Depth levels (only used to define N edges, not strict iso-depths)
    depth_levels = np.arange(
        cfg.z_top_locked,
        cfg.z_bottom_locked + cfg.depth_step_km * 1.0001,
        cfg.depth_step_km,
    )

    # 4) Plot slab + locked band (optional but handy)
    plot_slab_with_locked_region(
        df_slab,
        z_top_locked=cfg.z_top_locked,
        z_bottom_locked=cfg.z_bottom_locked,
        lat_min_geom=lat_min_geom,
        lat_max_geom=lat_max_geom,
    )

    # 5) Build edges for the full geometry extent
    edges, used_lats = build_edges_from_slab(
        df_slab,
        depth_levels=depth_levels,
        z_top_locked=cfg.z_top_locked,
        z_bottom_locked=cfg.z_bottom_locked,
        lat_min=lat_min_geom,
        lat_max=lat_max_geom,
        lat_step_deg=cfg.lat_step_deg,
        min_points=cfg.min_points_per_edge,
    )

    # 6) Plot edges over slab
    plot_edges_on_slab(
        df_slab,
        edges,
        title="Interpolated edges within locked portion (config-driven)",
    )

    # 7) Export geometry to JSON
    # For the *geometry* we just use the first segment's id as label,
    # since this is a global geometry that segments will later slice.
    out_path = cfg.output_dir / f"{cfg.geometry_id}_geometry.json"

    export_geometry_to_json(
        edges=edges,
        depth_levels=depth_levels,
        used_lats=used_lats,
        z_top_locked=cfg.z_top_locked,
        z_bottom_locked=cfg.z_bottom_locked,
        lat_max_locked=cfg.segments[0].lat_max,
        out_path=out_path,
        geometry_id=cfg.geometry_id,
        extra_metadata={
            "description": (
                "Global locked portion of the subduction interface "
                "used as base geometry; segments are defined later "
                "by lat_min / lat_max on these edges."
            ),
        },
    )

    return out_path


if __name__ == "__main__":
    out_json = build_geometry_from_config()
    print(f"Geometry written to {out_json}")

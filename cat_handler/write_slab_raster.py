import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS as RioCRS

import pyvista as pv
from pyproj import CRS, Transformer

from cat_handler import paths


def lon_0360_to_180(lon):
    lon = float(lon)
    return lon - 360.0 if lon > 180.0 else lon


def _read_xyz(p):
    arr = pd.read_csv(p, header=None, names=["lon", "lat", "val"])
    arr["lon"] = arr["lon"].astype(float).apply(lon_0360_to_180)
    arr["lat"] = arr["lat"].astype(float)
    return arr


def xyz_to_geotiff(xyz_path: str, out_tif: str, dtype="float32"):
    """Create a north-up GeoTIFF from an XYZ file where (lon,lat) are cell centers."""
    df = _read_xyz(xyz_path)

    lons = np.sort(df["lon"].unique())
    lats = np.sort(df["lat"].unique())

    if len(lons) < 2 or len(lats) < 2:
        raise ValueError("Need at least a 2x2 grid of lon/lat to define raster resolution.")

    dx = float(np.median(np.diff(lons)))
    dy = float(np.median(np.diff(lats)))
    if dx <= 0 or dy <= 0:
        raise ValueError("Non-positive grid spacing detected. Check coordinate values.")

    grid = df.pivot(index="lat", columns="lon", values="val").reindex(index=lats, columns=lons)
    data = np.flipud(grid.to_numpy())

    west_edge = lons.min() - dx / 2.0
    north_edge = lats.max() + dy / 2.0
    transform = Affine.translation(west_edge, north_edge) * Affine.scale(dx, -dy)

    height, width = data.shape
    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,
        "dtype": dtype,
        "crs": RioCRS.from_epsg(4326),
        "transform": transform,
        "tiled": True,
        "compress": "deflate",
        "nodata": np.nan,
    }

    data_to_write = data.astype(dtype)
    with rasterio.open(out_tif, "w", **profile) as dst:
        dst.write(data_to_write, 1)


def _to_m(values, units: str):
    u = units.strip().lower()
    if u == "km":
        return values * 1000.0
    if u == "m":
        return values
    raise ValueError("units must be 'km' or 'm'.")


def _project_xy(lons, lats, in_crs: str, out_crs: str | None):
    LON, LAT = np.meshgrid(lons, lats)
    if out_crs is None:
        return LON.astype(float), LAT.astype(float)

    tfm = Transformer.from_crs(
        CRS.from_user_input(in_crs),
        CRS.from_user_input(out_crs),
        always_xy=True,
    )
    X, Y = tfm.transform(LON.ravel(), LAT.ravel())
    X = np.asarray(X, dtype=float).reshape(LON.shape)
    Y = np.asarray(Y, dtype=float).reshape(LAT.shape)
    return X, Y


def xyz_depth_to_vtp(
    xyz_path: str,
    out_vtp: str,
    *,
    in_crs: str = "EPSG:4326",
    out_crs: str | None = "EPSG:32719",
    lon_range: tuple[float, float] | None = None,
    lat_range: tuple[float, float] | None = None,
    max_depth: float | None = None,
    depth_units: str = "km",
):
    """
    Write the *top* slab surface as a triangulated VTP.

    Assumptions
    -----------
    - The XYZ third column stores Z in *kilometers* (or meters if depth_units="m")
    - Z is **positive up** (your file has negative values at depth)
      e.g. -10 means 10 km below reference level.
    - NaNs represent missing cells; any quad touching a NaN is skipped.

    Parameters
    ----------
    max_depth : float, optional
        Maximum depth in *km* (or in depth_units). This is applied as:
          keep points with (-z) <= max_depth.
    """
    df = _read_xyz(xyz_path)

    if lon_range is not None:
        lo0, lo1 = float(lon_range[0]), float(lon_range[1])
        df = df[(df["lon"] >= lo0) & (df["lon"] <= lo1)]
    if lat_range is not None:
        la0, la1 = float(lat_range[0]), float(lat_range[1])
        df = df[(df["lat"] >= la0) & (df["lat"] <= la1)]
    if df.empty:
        raise ValueError("Crop removed all points (empty dataframe).")

    if max_depth is not None:
        md = float(max_depth)
        # depth (positive down) = -z_value  (since z is positive up)
        df.loc[df["val"].notna() & ((-df["val"]) > md), "val"] = np.nan

    lons = np.sort(df["lon"].unique())
    lats = np.sort(df["lat"].unique())
    if len(lons) < 2 or len(lats) < 2:
        raise ValueError("Need at least a 2x2 grid of lon/lat to define a surface.")

    grid = df.pivot(index="lat", columns="lon", values="val").reindex(index=lats, columns=lons)
    z = grid.to_numpy(dtype=float)  # z positive up (typically negative at depth)

    z_m = _to_m(z, depth_units)  # geometry z in meters
    depth_m = -z_m               # depth positive down in meters

    ny, nx = z_m.shape
    X, Y = _project_xy(lons, lats, in_crs, out_crs)

    z_filled = np.where(np.isfinite(z_m), z_m, 0.0)
    pts = np.c_[X.ravel(), Y.ravel(), z_filled.ravel()]

    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            z00, z10 = z_m[j, i], z_m[j, i + 1]
            z01, z11 = z_m[j + 1, i], z_m[j + 1, i + 1]
            if not (np.isfinite(z00) and np.isfinite(z10) and np.isfinite(z01) and np.isfinite(z11)):
                continue

            p00 = j * nx + i
            p10 = j * nx + (i + 1)
            p01 = (j + 1) * nx + i
            p11 = (j + 1) * nx + (i + 1)

            faces.append([3, p00, p10, p11])
            faces.append([3, p00, p11, p01])

    if not faces:
        raise ValueError("No valid cells found (all values are NaN or grid too sparse).")

    poly = pv.PolyData(pts, np.asarray(faces, dtype=np.int64).ravel())
    poly.point_data["z_m"] = z_m.ravel()
    poly.point_data["depth_m"] = depth_m.ravel()
    poly.point_data["depth_km"] = (depth_m / 1000.0).ravel()
    poly.point_data["valid"] = np.isfinite(z_m).astype(np.uint8).ravel()
    poly.save(out_vtp)


def xyz_depth_thickness_to_vtp(
    depth_xyz_path: str,
    thickness_xyz_path: str,
    out_vtp: str,
    *,
    in_crs: str = "EPSG:4326",
    out_crs: str | None = "EPSG:32719",
    lon_range: tuple[float, float] | None = None,
    lat_range: tuple[float, float] | None = None,
    max_bottom_depth: float | None = None,
    depth_units: str = "km",
    thickness_units: str = "km",
):
    """
    Write the *bottom* slab surface as a triangulated VTP.

    Assumptions
    -----------
    - Depth file third column stores Z **positive up** (negative at depth).
      Top surface z_top_m is obtained directly from file (unit converted).
    - Thickness file third column stores thickness as a positive scalar (downward).
    - Bottom surface: z_bot = z_top - thickness

    Parameters
    ----------
    max_bottom_depth : float, optional
        Maximum bottom depth in km (or in depth_units). Applied as:
          keep points with depth_bottom <= max_bottom_depth.
    """
    ddf = _read_xyz(depth_xyz_path)
    tdf = _read_xyz(thickness_xyz_path)

    if lon_range is not None:
        lo0, lo1 = float(lon_range[0]), float(lon_range[1])
        ddf = ddf[(ddf["lon"] >= lo0) & (ddf["lon"] <= lo1)]
        tdf = tdf[(tdf["lon"] >= lo0) & (tdf["lon"] <= lo1)]
    if lat_range is not None:
        la0, la1 = float(lat_range[0]), float(lat_range[1])
        ddf = ddf[(ddf["lat"] >= la0) & (ddf["lat"] <= la1)]
        tdf = tdf[(tdf["lat"] >= la0) & (tdf["lat"] <= la1)]
    if ddf.empty or tdf.empty:
        raise ValueError("Crop removed all points from depth and/or thickness dataframe.")

    lons = np.sort(ddf["lon"].unique())
    lats = np.sort(ddf["lat"].unique())
    if len(lons) < 2 or len(lats) < 2:
        raise ValueError("Need at least a 2x2 grid of lon/lat to define a surface.")

    z_top = ddf.pivot(index="lat", columns="lon", values="val").reindex(index=lats, columns=lons).to_numpy(float)
    thick = tdf.pivot(index="lat", columns="lon", values="val").reindex(index=lats, columns=lons).to_numpy(float)

    z_top_m = _to_m(z_top, depth_units)          # positive up
    thick_m = _to_m(thick, thickness_units)      # positive thickness
    z_bot_m = z_top_m - thick_m                  # bottom is below top

    depth_bot_m = -z_bot_m                       # depth positive down

    if max_bottom_depth is not None:
        mb = float(max_bottom_depth)
        mb_m = mb * 1000.0 if depth_units.strip().lower() == "km" else mb
        z_bot_m = np.where(np.isfinite(depth_bot_m) & (depth_bot_m > mb_m), np.nan, z_bot_m)

    ny, nx = z_bot_m.shape
    X, Y = _project_xy(lons, lats, in_crs, out_crs)

    z_filled = np.where(np.isfinite(z_bot_m), z_bot_m, 0.0)
    pts = np.c_[X.ravel(), Y.ravel(), z_filled.ravel()]

    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            z00, z10 = z_bot_m[j, i], z_bot_m[j, i + 1]
            z01, z11 = z_bot_m[j + 1, i], z_bot_m[j + 1, i + 1]
            if not (np.isfinite(z00) and np.isfinite(z10) and np.isfinite(z01) and np.isfinite(z11)):
                continue

            p00 = j * nx + i
            p10 = j * nx + (i + 1)
            p01 = (j + 1) * nx + i
            p11 = (j + 1) * nx + (i + 1)

            faces.append([3, p00, p10, p11])
            faces.append([3, p00, p11, p01])

    if not faces:
        raise ValueError("No valid cells found for bottom surface (NaNs too extensive).")

    poly = pv.PolyData(pts, np.asarray(faces, dtype=np.int64).ravel())
    poly.point_data["z_top_m"] = z_top_m.ravel()
    poly.point_data["thickness_m"] = thick_m.ravel()
    poly.point_data["z_bottom_m"] = z_bot_m.ravel()
    poly.point_data["depth_bottom_m"] = (-z_bot_m).ravel()
    poly.point_data["depth_bottom_km"] = ((-z_bot_m) / 1000.0).ravel()
    poly.point_data["valid"] = np.isfinite(z_bot_m).astype(np.uint8).ravel()
    poly.save(out_vtp)


if __name__ == "__main__":
    xyz_depth_to_vtp(
        paths.slab_depth,
        "slab_top_surface.vtp",
        out_crs="EPSG:32719",
        depth_units="km",
        lon_range=(-74.0, -50.0),
        lat_range=(-32.0, -17.0),
        max_depth=200.0,  # km
    )

    xyz_depth_thickness_to_vtp(
        depth_xyz_path=paths.slab_depth,
        thickness_xyz_path=paths.slab_thickness,
        out_vtp="slab_bottom_surface.vtp",
        out_crs="EPSG:32719",
        depth_units="km",
        thickness_units="km",
        lon_range=(-74.0, -50.0),
        lat_range=(-32.0, -17.0),
        max_bottom_depth=200.0,  # km
    )

    xyz_to_geotiff(paths.slab_depth, "depth.tif")
    xyz_to_geotiff(paths.slab_strike, "strike.tif")
    xyz_to_geotiff(paths.slab_dip, "dip.tif")
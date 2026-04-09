# Add/replace inside write_topo_vtp.py

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pyvista as pv
import rasterio
from pyproj import CRS, Transformer


def _to_m(values: np.ndarray, units: str) -> np.ndarray:
    u = str(units).strip().lower()
    if u == "m":
        return values
    if u == "km":
        return values * 1000.0
    raise ValueError("units must be 'm' or 'km'.")


def geotiff_to_surface(
    tif_path: str | Path,
    out_path: str | Path,
    *,
    out_crs: Optional[str] = None,
    lon_range: Optional[Tuple[float, float]] = None,
    lat_range: Optional[Tuple[float, float]] = None,
    z_units: str = "m",
    z_positive: str = "up",
    band: int = 1,
    z_min: Optional[float] = None,
    z_max: Optional[float] = None,
    target_spacing: Optional[float] = None,
    target_size: Optional[Tuple[int, int]] = None,
    resampling: str = "nearest",
) -> None:
    """
    Convert a GeoTIFF raster to a triangulated surface.

    Parameters
    ----------
    tif_path : str or Path
        Input GeoTIFF.
    out_path : str or Path
        Output mesh path. Use .vtp (PolyData) or .vtu (UnstructuredGrid).
    out_crs : str, optional
        CRS for output X/Y (e.g., "EPSG:32719"). If None, uses the raster CRS.
    lon_range, lat_range : (min, max), optional
        Crop in degrees (EPSG:4326). Provide both or neither.
    z_units : str
        Units for output Z: 'm' or 'km'. Raster band values are assumed to be in these units.
    z_positive : str
        'up' or 'down'. If 'down', Z is flipped.
    band : int
        Raster band index for Z values (default 1).
    z_min, z_max : float, optional
        Clamp/filter Z values (in z_units). Values outside are masked out.
    target_spacing : float, optional
        Resample spacing in destination CRS units (meters for projected CRS).
        Example: 1000.0 for 1 km grid in UTM meters.
    target_size : (width, height), optional
        Alternative to target_spacing: explicitly set output raster size.
    resampling : str
        One of: 'nearest', 'bilinear', 'cubic'.

    Notes
    -----
    Resampling is done in the destination CRS (out_crs), then triangulated.
    Faces are created only where all 4 corners are valid, preserving holes.
    """
    tif_path = Path(tif_path)
    out_path = Path(out_path)

    zp = str(z_positive).strip().lower()
    if zp not in ("up", "down"):
        raise ValueError("z_positive must be 'up' or 'down'.")

    if target_spacing is not None and target_size is not None:
        raise ValueError("Use either target_spacing or target_size, not both.")

    resampling = str(resampling).strip().lower()
    resampling_map = {
        "nearest": rasterio.enums.Resampling.nearest,
        "bilinear": rasterio.enums.Resampling.bilinear,
        "cubic": rasterio.enums.Resampling.cubic,
    }
    if resampling not in resampling_map:
        raise ValueError("resampling must be one of: 'nearest', 'bilinear', 'cubic'.")

    with rasterio.open(tif_path) as ds:
        src_crs = ds.crs
        if src_crs is None:
            raise ValueError("GeoTIFF has no CRS.")

        dst_crs = CRS.from_user_input(out_crs) if out_crs is not None else CRS.from_user_input(src_crs)

        if lon_range is not None or lat_range is not None:
            if lon_range is None or lat_range is None:
                raise ValueError("Provide both lon_range and lat_range, or neither.")

        bounds = None
        if lon_range is not None:
            to_dst = Transformer.from_crs(CRS.from_epsg(4326), dst_crs, always_xy=True)
            lon0, lon1 = float(lon_range[0]), float(lon_range[1])
            lat0, lat1 = float(lat_range[0]), float(lat_range[1])

            x0, y0 = to_dst.transform(lon0, lat0)
            x1, y1 = to_dst.transform(lon1, lat1)
            left, right = (min(x0, x1), max(x0, x1))
            bottom, top = (min(y0, y1), max(y0, y1))
            bounds = (left, bottom, right, top)

        if bounds is None:
            b = rasterio.warp.transform_bounds(src_crs, dst_crs, *ds.bounds, densify_pts=21)
            bounds = b

        left, bottom, right, top = bounds

        if target_size is not None:
            width = int(target_size[0])
            height = int(target_size[1])
            if width <= 1 or height <= 1:
                raise ValueError("target_size must be (width,height) with both > 1.")
            dst_transform = rasterio.transform.from_bounds(left, bottom, right, top, width, height)
        elif target_spacing is not None:
            s = float(target_spacing)
            if s <= 0:
                raise ValueError("target_spacing must be > 0.")
            width = int(np.ceil((right - left) / s))
            height = int(np.ceil((top - bottom) / s))
            width = max(width, 2)
            height = max(height, 2)
            dst_transform = rasterio.transform.from_origin(left, top, s, s)
        else:
            dst_transform, width, height = rasterio.warp.calculate_default_transform(
                src_crs, dst_crs, ds.width, ds.height, *ds.bounds
            )

        dst = np.full((height, width), np.nan, dtype=np.float32)

        src_nodata = ds.nodata
        if src_nodata is None and isinstance(ds.read(1, masked=True), np.ma.MaskedArray):
            src_nodata = None

        rasterio._warp._reproject(
            source=rasterio.band(ds, band),
            destination=dst,
            src_transform=ds.transform,
            src_crs=src_crs,
            src_nodata=src_nodata,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            dst_nodata=np.nan,
            resampling=resampling_map[resampling],
        )

    z = dst.astype(float)

    if z_min is not None:
        z = np.where(z >= float(z_min), z, np.nan)
    if z_max is not None:
        z = np.where(z <= float(z_max), z, np.nan)

    z_m = _to_m(z, z_units)
    if zp == "down":
        z_m = -z_m

    ny, nx = z_m.shape
    if ny < 2 or nx < 2:
        raise ValueError("Resampled raster is too small to triangulate (need at least 2x2).")

    cols = np.arange(nx, dtype=float)
    rows = np.arange(ny, dtype=float)
    cc, rr = np.meshgrid(cols, rows)

    a = dst_transform.a
    b = dst_transform.b
    c = dst_transform.c
    d = dst_transform.d
    e = dst_transform.e
    f = dst_transform.f

    x = a * (cc + 0.5) + b * (rr + 0.5) + c
    y = d * (cc + 0.5) + e * (rr + 0.5) + f

    valid = np.isfinite(z_m)
    z_fill = np.where(valid, z_m, 0.0)
    pts = np.c_[x.ravel(), y.ravel(), z_fill.ravel()]

    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            if not (valid[j, i] and valid[j, i + 1] and valid[j + 1, i] and valid[j + 1, i + 1]):
                continue
            p00 = j * nx + i
            p10 = j * nx + (i + 1)
            p01 = (j + 1) * nx + i
            p11 = (j + 1) * nx + (i + 1)
            faces.append([3, p00, p10, p11])
            faces.append([3, p00, p11, p01])

    if not faces:
        raise ValueError("No valid faces created. Check nodata mask, crop bounds, or z_min/z_max.")

    poly = pv.PolyData(pts, np.asarray(faces, dtype=np.int64).ravel())
    poly.point_data["topo_m"] = z_m.ravel()
    poly.point_data["valid"] = valid.astype(np.uint8).ravel()

    ext = out_path.suffix.lower()
    if ext == ".vtp":
        poly.save(str(out_path))
        return
    if ext == ".vtu":
        poly.cast_to_unstructured_grid().save(str(out_path))
        return
    raise ValueError("out_path must end with .vtp or .vtu")


geotiff_to_surface('../data/basemaps/basemap_chile/topo_masked.tif', './topo.vtp', out_crs="epsg:32719",
                   lat_range=(-32,-17),lon_range=(-58, -75), z_units='m', target_spacing='1000')
geotiff_to_surface('../data/basemaps/basemap_chile/bathy_masked.tif', './bathy.vtp', out_crs="epsg:32719",
                   lat_range=(-32,-17),lon_range=(-58, -75), z_units='m', target_spacing='1000')

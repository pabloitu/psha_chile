import numpy as np
import pandas as pd
import pyvista as pv
import triangle as tr
from pyproj import CRS, Transformer
from scipy.ndimage import (
    distance_transform_edt,
    gaussian_filter,
    gaussian_filter1d,
    map_coordinates,
)
from shapely.geometry import Polygon, box
from skimage.measure import find_contours

from cat_handler import paths


# xyz reading

def lon_0360_to_180(lon):
    lon = float(lon)
    return lon - 360.0 if lon > 180.0 else lon


def _read_xyz(p):
    arr = pd.read_csv(p, header=None, names=["lon", "lat", "val"])
    arr["lon"] = arr["lon"].astype(float).apply(lon_0360_to_180)
    arr["lat"] = arr["lat"].astype(float)
    return arr


def _grid_from_xyz(df):
    lons = np.sort(df["lon"].unique())
    lats = np.sort(df["lat"].unique())
    if len(lons) < 2 or len(lats) < 2:
        raise ValueError("Need at least a 2x2 grid.")
    Z = (
        df.pivot(index="lat", columns="lon", values="val")
        .reindex(index=lats, columns=lons)
        .to_numpy(dtype=float)
    )
    return lons, lats, Z


def _pixel_km(lons, lats):
    lat0 = float(np.mean(lats))
    km_per_deg_lat = 111.32
    km_per_deg_lon = 111.32 * np.cos(np.deg2rad(lat0))
    dlon_km = float(np.median(np.diff(lons))) * km_per_deg_lon
    dlat_km = float(np.median(np.diff(lats))) * km_per_deg_lat
    return 0.5 * (abs(dlon_km) + abs(dlat_km))


# depth-field smoothing

def _smooth_field(Z, lons, lats, smoothing_km):
    if smoothing_km is None or smoothing_km <= 0:
        return Z
    sigma = max(smoothing_km / _pixel_km(lons, lats), 0.5)
    valid = np.isfinite(Z).astype(float)
    filled = np.where(np.isfinite(Z), Z, 0.0)
    num = gaussian_filter(filled, sigma=sigma, mode="nearest")
    den = gaussian_filter(valid, sigma=sigma, mode="nearest")
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.where(den > 1e-6, num / den, np.nan)
    out[~np.isfinite(Z) & (den < 0.5)] = np.nan
    return out


# polygon extraction and processing

def extract_slab_polygon(mask, lons, lats):
    """
    Walk the outer boundary of a raster valid-pixel mask. Returns
    a closed ``(N, 2)`` lon/lat array with no smoothing or
    resampling applied.
    """
    padded = np.pad(mask, 1, constant_values=False)
    contours = find_contours(padded.astype(float), level=0.5)
    if not contours:
        raise ValueError("No valid region found in the mask.")
    contour = max(contours, key=len) - 1.0
    lon0, dlon = float(lons[0]), float(lons[1] - lons[0])
    lat0, dlat = float(lats[0]), float(lats[1] - lats[0])
    poly = np.c_[
        lon0 + contour[:, 1] * dlon,
        lat0 + contour[:, 0] * dlat,
    ]
    if len(poly) > 2 and np.allclose(poly[0], poly[-1]):
        poly = poly[:-1]
    return poly


def resample_polygon(xy, step):
    """
    Resample a closed polyline at uniform arc-length ``step`` (same
    units as ``xy``). Input must not repeat the first vertex.
    """
    closed = np.vstack([xy, xy[:1]])
    diffs = np.diff(closed, axis=0)
    seg = np.hypot(diffs[:, 0], diffs[:, 1])
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = cum[-1]
    n = max(int(round(total / step)), 3)
    s = np.linspace(0.0, total, n + 1)[:-1]
    x = np.interp(s, cum, closed[:, 0])
    y = np.interp(s, cum, closed[:, 1])
    return np.c_[x, y]


def smooth_polygon(xy, sigma):
    """
    Gaussian-smooth a closed polyline vertex sequence. ``sigma`` is
    in vertex indices. Returns the input unchanged if sigma <= 0.
    """
    if sigma is None or sigma <= 0:
        return xy
    x = gaussian_filter1d(xy[:, 0], sigma, mode="wrap")
    y = gaussian_filter1d(xy[:, 1], sigma, mode="wrap")
    return np.c_[x, y]


def clip_polygon_to_bbox(xy, lon_range, lat_range):
    """
    Intersect a lon/lat polygon with an axis-aligned bbox rectangle.
    Returns the clipped exterior as an ``(N, 2)`` array.
    """
    lo0, lo1 = float(lon_range[0]), float(lon_range[1])
    la0, la1 = float(lat_range[0]), float(lat_range[1])
    clipped = Polygon(xy).intersection(box(lo0, la0, lo1, la1))
    if clipped.is_empty:
        raise ValueError("Polygon does not intersect the bbox.")
    if clipped.geom_type == "MultiPolygon":
        clipped = max(clipped.geoms, key=lambda g: g.area)
    coords = np.array(clipped.exterior.coords)
    if len(coords) > 1 and np.allclose(coords[0], coords[-1]):
        coords = coords[:-1]
    return coords


def save_boundary_csv(xy, path):
    np.savetxt(path, xy, delimiter=",", header="lon,lat", comments="")


# triangulation

def _project_xy(lons, lats, in_crs, out_crs):
    if out_crs is None:
        return np.asarray(lons, float), np.asarray(lats, float)
    tfm = Transformer.from_crs(
        CRS.from_user_input(in_crs),
        CRS.from_user_input(out_crs),
        always_xy=True,
    )
    X, Y = tfm.transform(np.asarray(lons, float), np.asarray(lats, float))
    return np.asarray(X, float), np.asarray(Y, float)


def _triangulate(verts2d, target_edge_km, min_angle_deg):
    n = len(verts2d)
    segments = np.c_[np.arange(n), (np.arange(n) + 1) % n].astype(np.int32)
    edge_m = target_edge_km * 1000.0
    max_area = np.sqrt(3) / 4 * edge_m * edge_m
    opts = f"pq{min_angle_deg}a{max_area:.1f}"
    result = tr.triangulate(
        {"vertices": verts2d, "segments": segments}, opts,
    )
    return result["vertices"], result["triangles"]


# depth sampling and 3D lift

def _sample_depth(lons, lats, Z, sample_lons, sample_lats):
    lo0, lo1 = float(lons.min()), float(lons.max())
    la0, la1 = float(lats.min()), float(lats.max())
    frac_x = (sample_lons - lo0) / (lo1 - lo0) * (len(lons) - 1)
    frac_y = (sample_lats - la0) / (la1 - la0) * (len(lats) - 1)
    if not np.all(np.isfinite(Z)):
        _, (ii, jj) = distance_transform_edt(
            ~np.isfinite(Z), return_indices=True,
        )
        Z_filled = Z[ii, jj]
    else:
        Z_filled = Z
    return map_coordinates(
        Z_filled, [frac_y, frac_x], order=1, mode="nearest",
    )


def _lift_mesh(verts_xy, tris, in_crs, out_crs, lons, lats, Z_field):
    if out_crs is None:
        sample_lons = verts_xy[:, 0]
        sample_lats = verts_xy[:, 1]
    else:
        back = Transformer.from_crs(
            CRS.from_user_input(out_crs),
            CRS.from_user_input(in_crs),
            always_xy=True,
        )
        sample_lons, sample_lats = back.transform(
            verts_xy[:, 0], verts_xy[:, 1],
        )
        sample_lons = np.asarray(sample_lons, float)
        sample_lats = np.asarray(sample_lats, float)

    z_vals = _sample_depth(lons, lats, Z_field, sample_lons, sample_lats)

    points = np.c_[verts_xy[:, 0], verts_xy[:, 1], z_vals]
    cells = np.c_[
        np.full(len(tris), 3, dtype=np.int64),
        tris.astype(np.int64),
    ].ravel()
    cell_types = np.full(len(tris), pv.CellType.TRIANGLE, dtype=np.uint8)
    ug = pv.UnstructuredGrid(cells, cell_types, points)
    ug.point_data["z_m"] = z_vals
    ug.point_data["depth_m"] = -z_vals
    ug.point_data["depth_km"] = -z_vals / 1000.0
    return ug


# top-level pipeline

def xyz_to_mesh(
    xyz_path,
    out_vtu,
    *,
    lon_range,
    lat_range,
    max_depth_km,
    target_edge_km=5.0,
    smooth_sigma=0.0,
    depth_smoothing_km=5.0,
    min_angle_deg=30.0,
    boundary_out=None,
    in_crs="EPSG:4326",
    out_crs="EPSG:32719",
    depth_units="km",
):
    """
    Build an unstructured triangular mesh of a slab surface from an
    XYZ depth raster.

    Workflow:

    1. Read the raster, mask pixels deeper than ``max_depth_km``.
    2. Extract the raw staircase polygon of the valid region.
    3. Resample the polygon at ``target_edge_km`` arc-length steps
       so boundary vertex spacing matches the triangle size.
    4. Optionally Gaussian-smooth the resampled polygon.
    5. Clip with the lon/lat bbox so slab-limited sides stay curved
       and bbox-limited sides become straight and sharp.
    6. Mesh the polygon interior with Triangle.
    7. Sample the depth field at mesh vertices and lift to 3D.

    Parameters
    ----------
    xyz_path : str
        Path to an XYZ file with columns ``lon, lat, z``.
    out_vtu : str
        Output mesh path.
    lon_range, lat_range : tuple of (float, float)
        Study-area bounding box in degrees.
    max_depth_km : float
        Deepest slab depth to include, km positive down.
    target_edge_km : float
        Target triangle edge length in km. Also the resampling
        arc-length step for the boundary polygon.
    smooth_sigma : float
        Gaussian sigma (in vertex indices) applied to the resampled
        polygon. Default 0 disables smoothing.
    depth_smoothing_km : float
        Gaussian sigma in km for the depth field before sampling
        vertex z values. Set to 0 to sample raw z.
    min_angle_deg : float
        Minimum triangle angle enforced by Triangle.
    boundary_out : str, optional
        If set, write the final polygon as a ``lon,lat`` CSV.
    in_crs, out_crs : str
        Input and output CRS. ``out_crs=None`` keeps lon/lat.
    depth_units : str
        ``"km"`` or ``"m"`` for the z column in the XYZ file.
    """
    df = _read_xyz(xyz_path)
    lons, lats, Z = _grid_from_xyz(df)

    Z_m = Z * 1000.0 if depth_units.strip().lower() == "km" else Z
    Z_m = np.where((-Z_m) > max_depth_km * 1000.0, np.nan, Z_m)

    mask = np.isfinite(Z_m)
    print(f"  valid pixels after depth clip: {mask.sum()}")

    raw = extract_slab_polygon(mask, lons, lats)
    print(f"  raw polygon: {len(raw)} vertices")

    # resample in projected meters so step is in km
    px, py = _project_xy(raw[:, 0], raw[:, 1], in_crs, out_crs)
    resampled = resample_polygon(np.c_[px, py], target_edge_km * 1000.0)
    print(f"  after resampling: {len(resampled)} vertices")

    if smooth_sigma and smooth_sigma > 0:
        resampled = smooth_polygon(resampled, smooth_sigma)
        print(f"  smoothed with sigma={smooth_sigma}")

    # back to lon/lat for bbox clip
    back = Transformer.from_crs(
        CRS.from_user_input(out_crs),
        CRS.from_user_input(in_crs),
        always_xy=True,
    )
    blon, blat = back.transform(resampled[:, 0], resampled[:, 1])
    resampled_lonlat = np.c_[np.asarray(blon), np.asarray(blat)]

    clipped_lonlat = clip_polygon_to_bbox(
        resampled_lonlat, lon_range, lat_range,
    )
    print(f"  after bbox clip: {len(clipped_lonlat)} vertices")

    if boundary_out is not None:
        save_boundary_csv(clipped_lonlat, boundary_out)
        print(f"  wrote boundary CSV: {boundary_out}")

    # project back to meters for triangulation
    cpx, cpy = _project_xy(
        clipped_lonlat[:, 0], clipped_lonlat[:, 1], in_crs, out_crs,
    )
    clipped_m = np.c_[cpx, cpy]

    Z_field = _smooth_field(Z_m, lons, lats, depth_smoothing_km)

    tri_verts, tris = _triangulate(clipped_m, target_edge_km, min_angle_deg)
    print(f"  triangulation: {len(tri_verts)} vertices, {len(tris)} cells")

    mesh = _lift_mesh(tri_verts, tris, in_crs, out_crs, lons, lats, Z_field)
    mesh.save(out_vtu)
    print(f"  wrote mesh: {out_vtu}")


if __name__ == "__main__":
    xyz_to_mesh(
        paths.slab_depth,
        "slab_top_surface.vtu",
        lon_range=(-79.0, -68.0),
        lat_range=(-48, -18.0),
        max_depth_km=70.0,
        target_edge_km=10.0,
        smooth_sigma=5.0,
        depth_smoothing_km=5.0,
        boundary_out="slab_boundary.csv",
        out_crs="EPSG:32719",
    )
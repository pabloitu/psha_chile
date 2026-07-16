from dataclasses import dataclass

from matplotlib import pyplot as plt

from cat_no_mech_handler import paths as cat_paths
from ssm import paths as ssm_paths
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
import numpy as np


@dataclass
class SSMConfig:
    # Catalog settings
    mc_min: float = 5.0
    b_completeness: float | None = 1.0

    # Kernel / smoothing
    n_neighbors: int = 15
    kernel_power: float = 1.5
    max_event_grid_dist_km: float = 500.0
    min_kernel_km: float = 5.0      # NEW: minimum kernel radius

    # Grid (for bbox)
    lon_min: float = -80.0
    lon_max: float = -60.0
    lat_min: float = -60.0
    lat_max: float = -17.0

    # Debug / output
    max_events_debug: int | None = None
    outdir: Path = Path("ssm_crustal_outputs")

def pairwise_dist(lon_deg: np.ndarray, lat_deg: np.ndarray) -> np.ndarray:
    """
    Compute pairwise great-circle distances (km) between all points in lon/lat.

    This mirrors the logic of your old deg_dist / dist_p2points functions:
    spherical law of cosines on a sphere of radius 6371 km.
    """
    R = 6371.0  # Earth radius in km
    # Convert to radians
    lon = np.deg2rad(lon_deg)
    lat = np.deg2rad(lat_deg)

    # Broadcast to (N, N)
    lon1 = lon[:, np.newaxis]
    lon2 = lon[np.newaxis, :]
    lat1 = lat[:, np.newaxis]
    lat2 = lat[np.newaxis, :]

    # Spherical law of cosines
    dtheta = (
        np.sin(lat1) * np.sin(lat2) +
        np.cos(lat1) * np.cos(lat2) * np.cos(lon2 - lon1)
    )
    # Numerical safety: round/clip into [-1, 1]
    dtheta = np.clip(dtheta, -1.0, 1.0)
    dist = R * np.arccos(dtheta)

    return dist


def point_to_grid_dist(
    lon_ev: float,
    lat_ev: float,
    lon_grid: np.ndarray,
    lat_grid: np.ndarray,
) -> np.ndarray:
    """
    Great-circle distance (km) from a single event (lon_ev, lat_ev) to all grid points.

    Uses the same spherical law of cosines as pairwise_dist, but vectorized
    for one point vs many.
    """
    R = 6371.0
    lon1 = np.deg2rad(lon_ev)
    lat1 = np.deg2rad(lat_ev)
    lon2 = np.deg2rad(lon_grid)
    lat2 = np.deg2rad(lat_grid)

    dtheta = (
        np.sin(lat1) * np.sin(lat2) +
        np.cos(lat1) * np.cos(lat2) * np.cos(lon2 - lon1)
    )
    dtheta = np.clip(dtheta, -1.0, 1.0)
    dist = R * np.arccos(dtheta)
    return dist



def load_catalog(
    path: Path,
    bbox: tuple[float, float, float, float] | None = None,
    *,
    only_mainshocks: bool = True,
    class_filter: Optional[str] = None,
    max_events: Optional[int] = None,
) -> pd.DataFrame:
    """
    Load declustered catalog CSV and apply simple filters.
    """
    df = pd.read_csv(path)
    before = len(df)

    # Optional class filter (in case you point to all_classes_dc_main later)
    if class_filter is not None and "class" in df.columns:
        df = df[df["class"] == class_filter]

    # Filter to mainshocks only
    if only_mainshocks and "is_mainshock" in df.columns:
        df = df[df["is_mainshock"] == True]

    # Apply bbox
    if bbox is not None:
        lon_min, lon_max, lat_min, lat_max = bbox
        df = df[
            (df["longitude"] >= lon_min) &
            (df["longitude"] <= lon_max) &
            (df["latitude"] >= lat_min) &
            (df["latitude"] <= lat_max)
        ]

    # Optional debug limit on number of events
    if max_events is not None and len(df) > max_events:
        df = df.sort_values("time_iso").head(max_events)

    after = len(df)

    print(
        f"[load_catalog] Loaded {before} rows from {path}. "
        f"Kept {after} after filters."
    )
    print(
        "[load_catalog] Head:\n",
        df[["id", "time_iso", "longitude", "latitude", "mag",
            "tc_years", "mc_window"]].head()
    )

    return df


def load_grid(
    path: Path,
    bbox: Optional[Tuple[float, float, float, float]] = None,
) -> pd.DataFrame:
    """
    Load a lon/lat grid exported from QGIS and optionally filter by bounding box.

    Parameters
    ----------
    path : Path
        Path to a CSV with *only* columns 'lon' and 'lat'.
    bbox : (lon_min, lon_max, lat_min, lat_max), optional
        If given, only keep grid points inside this box.

    Returns
    -------
    grid_df : pandas.DataFrame
        DataFrame with columns:
        - 'lon'
        - 'lat'
    """
    path = Path(path)

    grid_df = pd.read_csv(path)
    print(f"[load_grid] Loaded grid CSV from {path} with {len(grid_df)} points.")

    if list(grid_df.columns) != ["lon", "lat"]:
        print(
            "[load_grid] WARNING: expected exactly two columns: 'lon','lat'. "
            f"Got columns: {list(grid_df.columns)}"
        )

    if bbox is not None:
        lon_min, lon_max, lat_min, lat_max = bbox
        mask = (
            (grid_df["lon"] >= lon_min)
            & (grid_df["lon"] <= lon_max)
            & (grid_df["lat"] >= lat_min)
            & (grid_df["lat"] <= lat_max)
        )
        before = len(grid_df)
        grid_df = grid_df[mask].reset_index(drop=True)
        print(
            f"[load_grid] Applied bbox "
            f"lon=[{lon_min}, {lon_max}], lat=[{lat_min}, {lat_max}]. "
            f"Kept {len(grid_df)} / {before} points."
        )

    print("[load_grid] Head of grid:")
    print(grid_df.head())

    return grid_df

import numpy as np


def compute_event_weights(
    df_events: pd.DataFrame,
    config: SSMConfig,
    *,
    write_debug: bool = True,
) -> np.ndarray:
    """
    Compute per-event weights based on completeness window length (tc_years)
    and magnitude of completeness (mc_window).

    The basic idea is:
      - base weight ~ 1 / tc_years
      - if b_completeness is not None, multiply by 10^(b * (mc - mc_min))

    This matches the original Helmstetter-style completeness correction with
    b ~ 1, but we keep b as a parameter.
    """
    if "tc_years" not in df_events.columns or "mc_window" not in df_events.columns:
        raise ValueError(
            "[compute_event_weights] Expected 'tc_years' and 'mc_window' "
            "columns in the catalog."
        )

    tc = df_events["tc_years"].to_numpy(dtype=float)
    mc = df_events["mc_window"].to_numpy(dtype=float)

    # Avoid division by zero
    if np.any(tc <= 0):
        raise ValueError(
            "[compute_event_weights] Found non-positive tc_years values."
        )

    # Base: 1 / tc
    weights = 1.0 / tc

    # Completeness correction: 10^(b (Mc - mc_min))
    if config.b_completeness is not None:
        b = config.b_completeness
        # For NaN mc, treat factor as 1
        mc_clean = np.where(np.isnan(mc), config.mc_min, mc)
        factor = 10.0 ** (b * (mc_clean - config.mc_min))
        weights = weights * factor

    # Debug prints
    print("[compute_event_weights] Weight statistics:")
    print(f"  min   = {weights.min():.3e}")
    print(f"  max   = {weights.max():.3e}")
    print(f"  median= {np.median(weights):.3e}")
    print(
        f"  tc_years: min={tc.min():.2f}, max={tc.max():.2f}, "
        f"mc_window: finite min={np.nanmin(mc):.2f}, max={np.nanmax(mc):.2f}"
    )

    # Optional debug CSV for QGIS
    if write_debug:
        config.outdir.mkdir(parents=True, exist_ok=True)
        df_dbg = df_events[
            ["longitude", "latitude", "mag", "tc_years", "mc_window"]
        ].copy()
        df_dbg["weight"] = weights
        out_csv = config.outdir / "events_with_weights.csv"
        df_dbg.to_csv(out_csv, index=False)
        print(f"[compute_event_weights] Wrote events_with_weights.csv to {out_csv}")

    return weights


def estimate_kernel(
    df_events: pd.DataFrame,
    config: SSMConfig,
    *,
    write_debug: bool = True,
) -> np.ndarray:
    """
    Estimate adaptive kernel radii for each event as the distance (km)
    to its N-th nearest neighbour.

    - Uses great-circle distances (same idea as your previous distance code).
    - If there are fewer than N+1 events, it falls back to the max available.

    Returns
    -------
    kernel_r_km : np.ndarray
        1D array of length len(df_events) with kernel radius (km) per event.
    """
    if "longitude" not in df_events.columns or "latitude" not in df_events.columns:
        raise ValueError(
            "[estimate_kernel_radii] Expected 'longitude' and 'latitude' "
            "columns in the catalog."
        )

    lon = df_events["longitude"].to_numpy(dtype=float)
    lat = df_events["latitude"].to_numpy(dtype=float)
    n_events = len(df_events)

    if n_events < 2:
        raise ValueError(
            "[estimate_kernel_radii] Need at least 2 events to estimate "
            "nearest-neighbour distances."
        )

    print(f"[estimate_kernel_radii] Computing pairwise distances for {n_events} events...")

    # --- 1. Pairwise distance matrix ---
    dist_mat = pairwise_dist(lon, lat)  # shape (N, N)
    # dist_mat[i, i] = 0 (distance to self)

    # --- 2. Sort distances per row ---
    # Each row: 0 = distance to self, then nearest neighbours in ascending order.
    dist_sorted = np.sort(dist_mat, axis=1)

    # --- 3. Pick distance to N-th neighbour (excluding self at index 0) ---
    # If we have fewer than N+1 events, fallback to largest available index.
    nN = config.n_neighbors
    max_index = min(nN, n_events - 1)  # ensure index within bounds

    kernel_r_km = dist_sorted[:, max_index]

    print("[estimate_kernel_radii] Kernel radius stats (km):")
    print(f"  N-neighbours = {nN}")
    print(f"  min   = {kernel_r_km.min():.2f}")
    print(f"  max   = {kernel_r_km.max():.2f}")
    print(f"  median= {np.median(kernel_r_km):.2f}")

    # --- 4. Optional debug CSV for QGIS ---
    if write_debug:
        config.outdir.mkdir(parents=True, exist_ok=True)
        df_dbg = df_events[["longitude", "latitude", "mag"]].copy()
        df_dbg["kernel_r_km"] = kernel_r_km
        out_csv = config.outdir / "events_with_kernels.csv"
        df_dbg.to_csv(out_csv, index=False)
        print(f"[estimate_kernel_radii] Wrote events_with_kernels.csv to {out_csv}")

    return kernel_r_km
def compute_ssm(
    df_events: pd.DataFrame,
    df_grid: pd.DataFrame,
    weights: np.ndarray,
    kernel_r_km: np.ndarray,
    config: SSMConfig,
    *,
    write_debug: bool = True,
) -> np.ndarray:
    """
    Compute smoothed seismicity rates on the grid.

    For each event i:
      - compute distances r_ij to all grid points
      - keep only r_ij <= max_event_grid_dist_km
      - kernel: K_ij = 1 / (r_ij^2 + d_i^2)^p
      - normalize per event: sum_j K_ij = 1
      - scale by event weight w_i (1/yr, already includes tc/Mc correction)
      - add to lambda_j
    """
    if not {"lon", "lat"}.issubset(df_grid.columns):
        raise ValueError("[compute_ssm] Grid must have 'lon' and 'lat' columns.")

    if len(df_events) != len(weights) or len(df_events) != len(kernel_r_km):
        raise ValueError(
            "[compute_ssm] Length mismatch between events, weights, and kernel radii."
        )

    lon_grid = df_grid["lon"].to_numpy(dtype=float)
    lat_grid = df_grid["lat"].to_numpy(dtype=float)

    n_events = len(df_events)
    n_cells = len(df_grid)

    rates = np.zeros(n_cells, dtype=float)

    max_dist = config.max_event_grid_dist_km
    p = config.kernel_power
    eps = 1e-6  # small number to avoid exact zeros

    print(
        f"[compute_ssm] Starting kernel summation for {n_events} events "
        f"and {n_cells} grid points."
    )
    print(
        f"[compute_ssm] Kernel power p = {p}, "
        f"max_event_grid_dist_km = {max_dist}, "
        f"min_kernel_km = {config.min_kernel_km}, "
        f"mc_min = {config.mc_min}"
    )

    lon_ev = df_events["longitude"].to_numpy(dtype=float)
    lat_ev = df_events["latitude"].to_numpy(dtype=float)

    for i in range(n_events):
        # Enforce a minimum kernel radius
        d_i = max(kernel_r_km[i], config.min_kernel_km)
        w_i = weights[i]

        # distances from event i to all grid points (km)
        r = point_to_grid_dist(lon_ev[i], lat_ev[i], lon_grid, lat_grid)

        # apply cutoff
        mask = r <= max_dist
        if not np.any(mask):
            continue

        r_sub = r[mask]

        # kernel values: 1 / (r^2 + d^2)^p
        r2_plus_d2 = r_sub**2 + d_i**2
        # avoid exact zeros for numerical safety
        r2_plus_d2 = np.maximum(r2_plus_d2, eps**2)

        kernel_vals = 1.0 / (r2_plus_d2 ** p)

        # guard against non-finite values
        if not np.all(np.isfinite(kernel_vals)):
            bad = np.where(~np.isfinite(kernel_vals))[0]
            print(
                f"[compute_ssm] WARNING: non-finite kernel_vals for event {i}, "
                f"indices (first few): {bad[:5]}"
            )
            # replace inf/nan with zero
            kernel_vals[~np.isfinite(kernel_vals)] = 0.0

        sum_kernel = kernel_vals.sum()
        if sum_kernel <= 0.0 or not np.isfinite(sum_kernel) or w_i == 0.0:
            continue

        contrib = kernel_vals * (w_i / sum_kernel)

        # guard against non-finite contrib (extra safety)
        if not np.all(np.isfinite(contrib)):
            bad = np.where(~np.isfinite(contrib))[0]
            print(
                f"[compute_ssm] WARNING: non-finite contrib for event {i}, "
                f"indices (first few): {bad[:5]}"
            )
            contrib[~np.isfinite(contrib)] = 0.0

        rates[mask] += contrib

        if (i + 1) % 50 == 0 or i == n_events - 1:
            print(
                f"[compute_ssm] Processed event {i+1}/{n_events} "
                f"(current total rate sum = {rates.sum():.3f} /yr)"
            )

    print("[compute_ssm] Finished kernel summation.")
    print(
        f"[compute_ssm] Total rate (sum over all cells) = {rates.sum():.3f} events/year"
    )
    print(
        f"[compute_ssm] Non-zero cells: {(rates > 0).sum()} / {len(rates)}"
    )

    if write_debug:
        config.outdir.mkdir(parents=True, exist_ok=True)
        grid_out = df_grid.copy()
        grid_out["rate_MgeMcmin_per_year"] = rates
        out_csv = config.outdir / "ssm_grid_rates.csv"
        grid_out.to_csv(out_csv, index=False)
        print(f"[compute_ssm] Wrote ssm_grid_rates.csv to {out_csv}")

    return rates

def truncated_gr_on_grid(
    rates_raw: np.ndarray,
    *,
    a: float,
    b: float,
    mmin: float,
    mmax: float,
    delta_m: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Apply a truncated Gutenberg–Richter MFD to the SSM grid.

    Parameters
    ----------
    rates_raw : array (n_cells,)
        SSM output from compute_ssm. Used as a spatial shape; will be
        rescaled to the global rate implied by (a,b,mmin).
    a, b : float
        GR parameters such that log10 lambda(M>=M) = a - b M.
    mmin : float
        Forecast minimum magnitude (Mmin_forecast), e.g. 4.9.
    mmax : float
        Truncation magnitude Mmax (no rates above this).
    delta_m : float
        Magnitude bin width for the discrete MFD.

    Returns
    -------
    rates_bins : array (n_cells, n_bins)
        Annual rates per cell and per magnitude bin [M_i, M_{i+1}).
    mag_edges : array (n_bins + 1,)
        Magnitude bin edges used (from mmin to mmax).
    """
    if rates_raw.ndim != 1:
        raise ValueError("[truncated_gr_on_grid] rates_raw must be 1D (n_cells,)")

    total_shape = rates_raw.sum()
    if total_shape <= 0 or not np.isfinite(total_shape):
        raise ValueError(
            "[truncated_gr_on_grid] Cannot normalize SSM: "
            "sum(rates_raw) must be positive and finite."
        )

    # 1) Global rate from (a,b) for M >= mmin
    lambda_global = 10.0 ** (a - b * mmin)

    # 2) Spatial shape and per-cell total rate for M >= mmin
    shape = rates_raw / total_shape
    rates_mge_mmin = shape * lambda_global  # (n_cells,)

    # 3) Magnitude bin edges
    mag_edges = np.arange(mmin, mmax + 1e-6, delta_m)
    if mag_edges[-1] < mmax - 1e-5:
        mag_edges = np.append(mag_edges, mmax)
    n_bins = len(mag_edges) - 1
    n_cells = rates_mge_mmin.size

    rates_bins = np.zeros((n_cells, n_bins), dtype=float)

    # 4) Fill per-bin rates
    for i in range(n_bins):
        M_lo = mag_edges[i]
        M_hi = mag_edges[i + 1]

        # cumulative above lower bound
        if M_lo < mmin:
            raise ValueError("[truncated_gr_on_grid] M_lo < mmin not supported.")
        fac_lo = 10.0 ** (b * (mmin - M_lo))

        # cumulative above upper bound
        if M_hi < mmax:
            fac_hi = 10.0 ** (b * (mmin - M_hi))
        else:
            # truncated: no events above Mmax
            fac_hi = 0.0

        lam_lo = rates_mge_mmin * fac_lo
        lam_hi = rates_mge_mmin * fac_hi

        rates_bins[:, i] = np.maximum(lam_lo - lam_hi, 0.0)

    # Quick sanity prints
    print("[truncated_gr_on_grid] MFD on grid:")
    print(f"  a = {a:.3f}, b = {b:.3f}, mmin = {mmin:.2f}, mmax = {mmax:.2f}, "
          f"delta_m = {delta_m:.2f}")
    print(f"  Global lambda(M>=mmin) from (a,b) = {lambda_global:.4f} /yr")
    print(
        f"  Sum over grid of rates(M>=mmin) = {rates_mge_mmin.sum():.4f} /yr "
        "(should match global)"
    )
    print(
        f"  Sum over grid & bins (total) = {rates_bins.sum():.4f} /yr "
        "(<= lambda_global due to truncation)"
    )

    return rates_bins, mag_edges

def write_ssm_mfd_csv(
    df_grid: pd.DataFrame,
    rates_bins: np.ndarray,
    mag_edges: np.ndarray,
    *,
    depth_value: float = 0.0,
    out_path: Path = Path("ssm_outputs/ssm_mfd_grid.csv"),
) -> None:
    """
    Write the smoothed seismicity model with per-bin rates to a CSV.

    Columns:
      lon, lat, depth, rate_M{lo}_{hi}  (for each magnitude bin)
    """
    out_path = Path(out_path)

    if not {"lon", "lat"}.issubset(df_grid.columns):
        raise ValueError("[write_ssm_mfd_csv] df_grid must have 'lon' and 'lat' columns.")

    n_cells = len(df_grid)
    if rates_bins.shape[0] != n_cells:
        raise ValueError(
            "[write_ssm_mfd_csv] rates_bins first dimension must match number of grid cells."
        )

    n_bins = rates_bins.shape[1]
    if len(mag_edges) != n_bins + 1:
        raise ValueError(
            "[write_ssm_mfd_csv] mag_edges length must be n_bins + 1."
        )

    df_out = df_grid.copy()
    df_out["depth"] = depth_value

    for i in range(n_bins):
        M_lo = mag_edges[i]
        M_hi = mag_edges[i + 1]
        col = f"rate_M{M_lo:.1f}_{M_hi:.1f}"
        df_out[col] = rates_bins[:, i]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_path, index=False)
    print(f"[write_ssm_mfd_csv] Wrote {out_path}")
def safe_log10(
    values: np.ndarray,
    *,
    fill_value: float = np.nan,
) -> np.ndarray:
    """
    Take log10 of an array but avoid -inf / NaN explosions.

    - For values > 0: return log10(values)
    - For values <= 0 or non-finite: return `fill_value` (default NaN)

    This is handy before writing a log10 raster so that QGIS
    doesn't get huge negative values from log10(0).
    """
    values = np.asarray(values, dtype=float)
    out = np.full_like(values, fill_value, dtype=float)

    mask = (values > 0.0) & np.isfinite(values)
    out[mask] = np.log10(values[mask])

    return out

def write_ssm_raster(
    df_grid: pd.DataFrame,
    values: np.ndarray,
    *,
    out_path: Path = Path("ssm_outputs/ssm_rate_MgeMmin.tif"),
) -> None:
    """
    Write a raster (GeoTIFF) from SSM grid points, treating each point
    as the center of a pixel. Pixels with no SSM point remain NaN.

    Parameters
    ----------
    df_grid : DataFrame with 'lon', 'lat'
        Regular grid of SSM points.
    values : array (n_cells,)
        Values to rasterize (e.g. total rate M>=Mmin in each cell).
    out_path : Path
        Output GeoTIFF path.
    """
    import rasterio
    from rasterio.transform import from_origin

    out_path = Path(out_path)

    if not {"lon", "lat"}.issubset(df_grid.columns):
        raise ValueError("[write_ssm_raster] df_grid must have 'lon' and 'lat' columns.")

    lons = df_grid["lon"].to_numpy(dtype=float)
    lats = df_grid["lat"].to_numpy(dtype=float)

    if lons.size != values.size:
        raise ValueError("[write_ssm_raster] values length must match number of grid cells.")

    # Infer resolution from unique coords
    unique_lons = np.sort(np.unique(lons))
    unique_lats = np.sort(np.unique(lats))
    if unique_lons.size < 2 or unique_lats.size < 2:
        raise ValueError("[write_ssm_raster] Need at least 2 unique lon/lat values to infer resolution.")

    dx = np.median(np.diff(unique_lons))
    dy = np.median(np.diff(unique_lats))

    lon_min = unique_lons.min()
    lon_max = unique_lons.max()
    lat_min = unique_lats.min()
    lat_max = unique_lats.max()

    n_cols = int(round((lon_max - lon_min) / dx)) + 1
    n_rows = int(round((lat_max - lat_min) / dy)) + 1

    # Initialize with NaN
    arr = np.full((n_rows, n_cols), np.nan, dtype=float)

    # Map each point to row/col (row 0 = north)
    for lon, lat, val in zip(lons, lats, values):
        col = int(round((lon - lon_min) / dx))
        row = int(round((lat_max - lat) / dy))
        if 0 <= row < n_rows and 0 <= col < n_cols:
            arr[row, col] = val

    # Pixel centers: lon_min..lon_max, lat_min..lat_max
    # from_origin(west, north, xsize, ysize)
    transform = from_origin(
        lon_min - dx / 2.0,
        lat_max + dy / 2.0,
        dx,
        dy,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        out_path,
        "w",
        driver="GTiff",
        height=n_rows,
        width=n_cols,
        count=1,
        dtype=arr.dtype,
        crs="EPSG:4326",
        transform=transform,
        nodata=np.nan,
    ) as dst:
        dst.write(arr, 1)

    print(
        f"[write_ssm_raster] Wrote {out_path} "
        f"(n_rows={n_rows}, n_cols={n_cols}, dx={dx:.4f}, dy={dy:.4f})"
    )

def histogram_rates(
    values: np.ndarray,
    *,
    n_bins: int = 50,
    log10_x: bool = True,
    out_csv: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Build a histogram of grid rates (e.g. SSM total rates).

    Parameters
    ----------
    values : array-like
        1D array of rates per cell (e.g. rates_mge_mmin).
    n_bins : int, optional
        Number of histogram bins.
    log10_x : bool, optional
        If True, build the histogram in log10(rate) space, ignoring
        non-positive values.
    out_csv : Path, optional
        If given, write the histogram as CSV with columns:
        'bin_left', 'bin_right', 'count'.

    Returns
    -------
    df_hist : pandas.DataFrame
        Histogram table.
    """
    arr = np.asarray(values, dtype=float)
    mask = np.isfinite(arr)

    if log10_x:
        mask = mask & (arr > 0.0)
        data = np.log10(arr[mask])
        space = "log10"
    else:
        mask = mask & (arr >= 0.0)
        data = arr[mask]
        space = "linear"

    if data.size == 0:
        raise ValueError("[histogram_rates] No valid data points for histogram.")

    counts, edges = np.histogram(data, bins=n_bins)
    bin_left = edges[:-1]
    bin_right = edges[1:]

    df_hist = pd.DataFrame(
        {
            "bin_left": bin_left,
            "bin_right": bin_right,
            "count": counts,
        }
    )

    print(f"[histogram_rates] Built histogram in {space} space:")
    print(f"  n_points = {data.size}")
    print(f"  min = {data.min():.3f}, max = {data.max():.3f}")
    print(
        f"  median = {np.median(data):.3f}, "
        f"p10 = {np.percentile(data, 10):.3f}, "
        f"p90 = {np.percentile(data, 90):.3f}"
    )

    if out_csv is not None:
        out_csv = Path(out_csv)
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df_hist.to_csv(out_csv, index=False)
        print(f"[histogram_rates] Wrote histogram to {out_csv}")

    return df_hist


def plot_rate_histogram(
    values: np.ndarray,
    *,
    n_bins: int = 50,
    log10_x: bool = True,
    out_path: Path = Path("ssm_outputs/ssm_rate_hist.png"),
) -> None:
    """
    Plot a histogram of grid rates (e.g. SSM total rates) and save as PNG.

    Parameters
    ----------
    values : array-like
        1D array of rates per cell (e.g. total rate M>=Mmin).
    n_bins : int, optional
        Number of histogram bins.
    log10_x : bool, optional
        If True, plot histogram of log10(rate) for rate > 0.
    out_path : Path, optional
        Output PNG path.
    """
    arr = np.asarray(values, dtype=float)
    mask = np.isfinite(arr)

    if log10_x:
        mask = mask & (arr > 0.0)
        data = np.log10(arr[mask])
        xlabel = "log10(rate [1/yr])"
    else:
        mask = mask & (arr >= 0.0)
        data = arr[mask]
        xlabel = "rate [1/yr]"

    if data.size == 0:
        print("[plot_rate_histogram] No valid data points to plot.")
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(data, bins=n_bins, edgecolor="black")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Number of cells")
    ax.set_title("Histogram of grid rates")
    ax.grid(True, alpha=0.3)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[plot_rate_histogram] Wrote histogram plot to {out_path}")
if __name__ == "__main__":
    from get_ab_crustal import read_mc, pick_windows, load_mfd_catalog, estimate_ab

    cfg = SSMConfig(n_neighbors=15)
    bbox = (cfg.lon_min, cfg.lon_max, cfg.lat_min, cfg.lat_max)

    # 1) Load grid
    df_grid = load_grid(ssm_paths.grid_01_crustal, bbox=bbox)

    # 2) Load catalogs and build SSM (spatial shape)
    df_forearc = load_catalog(
        cat_paths.cat_forearc_dc,
        bbox=bbox,
        only_mainshocks=True,
        class_filter=None,
        max_events=cfg.max_events_debug,
    )
    df_intraarc = load_catalog(
        cat_paths.cat_intraarc_dc,
        bbox=bbox,
        only_mainshocks=True,
        class_filter=None,
        max_events=cfg.max_events_debug,
    )
    df_unclassified = load_catalog(
        cat_paths.cat_unclassified_dc,
        bbox=bbox,
        only_mainshocks=True,
        class_filter=None,
        max_events=cfg.max_events_debug,
    )


    df_forearc["tect_class"] = "forearc"
    df_intraarc["tect_class"] = "intraarc"
    df_unclassified["tect_class"] = "unclassified"


    df_all = pd.concat([df_forearc, df_intraarc], ignore_index=True)

    print(f"[main] Combined catalog has {len(df_all)} events.")

    weights_all = compute_event_weights(df_all, cfg, write_debug=True)
    kernel_all = estimate_kernel(df_all, cfg, write_debug=True)
    rates_raw = compute_ssm(
        df_events=df_all,
        df_grid=df_grid,
        weights=weights_all,
        kernel_r_km=kernel_all,
        config=cfg,
        write_debug=True,
    )

    # 3) Get global MFD parameters (a,b) and mmin from get_ab
    mc_df = read_mc(cat_paths.MC_SUMMARY)
    mc_sel = pick_windows(mc_df, start_index=-5)
    df_mfd = load_mfd_catalog(mc_sel, mmin=mc_sel.mc, only_mainshocks=True)
    ab = estimate_ab(df_mfd, mc_sel, mmin_forecast=4.9, delta_m=0.1)

    a = ab["a"]
    b = ab["b"]
    mmin_forecast = ab["mmin_forecast"]

    # Choose truncation magnitude and bin width for hazard
    mmax = 8.0      # example; you choose this
    delta_m = 0.1   # or 0.2

    # 4) Apply truncated GR to the SSM grid
    rates_bins, mag_edges = truncated_gr_on_grid(
        rates_raw,
        a=a,
        b=b,
        mmin=mmin_forecast,
        mmax=mmax,
        delta_m=delta_m,
    )

    # 5) Write CSV with full SSM+MFD
    write_ssm_mfd_csv(
        df_grid,
        rates_bins,
        mag_edges,
        depth_value=0.0,
        out_path=cfg.outdir / "ssm_mfd_grid.csv",
    )

    # Total rate (M >= Mmin) per cell
    rates_mge_mmin = rates_bins.sum(axis=1)
    plot_rate_histogram(
        rates_mge_mmin,
        n_bins=50,
        log10_x=True,
        out_path=cfg.outdir / "ssm_rate_MgeMmin_hist.png",
    )
    # Histogram in log10 space
    histogram_rates(
        rates_mge_mmin,
        n_bins=50,
        log10_x=True,
        out_csv=cfg.outdir / "ssm_rate_MgeMmin_hist.csv",
    )
    # Log10 version, with zeros -> NaN
    rates_log10 = safe_log10(rates_mge_mmin)

    # Linear-rate raster (optional, for sanity)
    write_ssm_raster(
        df_grid,
        rates_mge_mmin,
        out_path=cfg.outdir / "ssm_rate_MgeMmin.tif",
    )

    # Log10 raster for nicer visualization
    write_ssm_raster(
        df_grid,
        rates_log10,
        out_path=cfg.outdir / "ssm_log10_rate_MgeMmin.tif",
    )


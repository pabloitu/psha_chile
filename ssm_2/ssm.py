from dataclasses import dataclass
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
import rasterio
from rasterio.transform import from_origin

@dataclass
class SSMConfig:
    """

    Model configuration class
    """
    # Build forecast
    a_value = 5
    b_value = 1
    m_min: float = 5.0
    m_max: float = 8.0
    dm: float = 0.1

    # Completeness parameters
    mc_min: float = 4.4    # Minimum completeness of the entire catalog
    b_completeness: float | None = 1.0    # Estimated for variable M_c (e.g., Weichert)

    n_neighbors: int = 25
    kernel_power: float = 1.5
    max_event_grid_dist_km: float = 500.0
    min_kernel_km: float = 5.0

    lon_min: float = -80.0
    lon_max: float = -60.0
    lat_min: float = -56.0
    lat_max: float = -17.0

    outdir: Path = Path("output")


def pairwise_dist(lon_deg: np.ndarray, lat_deg: np.ndarray) -> np.ndarray:
    """
    Distance between events of a catalog
    """
    R = 6371.0

    lon = np.deg2rad(lon_deg)
    lat = np.deg2rad(lat_deg)

    lon1 = lon[:, np.newaxis]
    lon2 = lon[np.newaxis, :]
    lat1 = lat[:, np.newaxis]
    lat2 = lat[np.newaxis, :]

    dtheta = (
        np.sin(lat1) * np.sin(lat2) +
        np.cos(lat1) * np.cos(lat2) * np.cos(lon2 - lon1)
    )
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
    Distance (km) between catalog events and grid centers
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
) -> pd.DataFrame:
    """
    Load declustered catalog CSV and apply filters.
    """
    df = pd.read_csv(path)
    before = len(df)

    # Apply bbox
    if bbox is not None:
        lon_min, lon_max, lat_min, lat_max = bbox
        df = df[
            (df["longitude"] >= lon_min) &
            (df["longitude"] <= lon_max) &
            (df["latitude"] >= lat_min) &
            (df["latitude"] <= lat_max)
        ]

    after = len(df)

    print(
        f"[load_catalog] Loaded {before} rows from {path}. "
        f"Kept {after} after filters."
    )

    return df


def load_grid(
    path: Path,
    bbox: Optional[Tuple[float, float, float, float]] = None,
) -> pd.DataFrame:
    """
    Load a lon/lat grid in csv and optionally filter by bounding box.

    Parameters
    ----------
    path : Path
        Path to a CSV with columns 'lon' and 'lat'.
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


    if bbox is not None:
        lon_min, lon_max, lat_min, lat_max = bbox
        mask = (
            (grid_df["lon"] >= lon_min)
            & (grid_df["lon"] <= lon_max)
            & (grid_df["lat"] >= lat_min)
            & (grid_df["lat"] <= lat_max)
        )
        grid_df = grid_df[mask].reset_index(drop=True)


    return grid_df


def compute_event_weights(
    df_events: pd.DataFrame,
    config: SSMConfig,
) -> np.ndarray:
    tc = df_events["tc_years"].to_numpy(dtype=float)
    mc = df_events["mc_window"].to_numpy(dtype=float)

    weights = 1.0 / tc

    if config.b_completeness is not None:
        b = config.b_completeness
        mc_clean = np.where(np.isnan(mc), config.mc_min, mc)
        factor = 10.0 ** (b * (mc_clean - config.mc_min))
        weights = weights * factor

    # ---------- DEBUG BLOCK ----------
    print("[compute_event_weights] DEBUG:")
    print(f"  tc_years:   min={np.nanmin(tc):.4g}, max={np.nanmax(tc):.4g}")
    print(f"  mc_window:  finite_min={np.nanmin(mc):.4g}, finite_max={np.nanmax(mc):.4g}")

    n_nan_w = np.isnan(weights).sum()
    n_inf_w = np.isinf(weights).sum()
    print(f"  weights:    min={np.nanmin(weights):.4g}, "
          f"max={np.nanmax(weights):.4g}, "
          f"median={np.nanmedian(weights):.4g}")
    print(f"  weights:    n_nan={n_nan_w}, n_inf={n_inf_w}")

    if n_nan_w or n_inf_w:
        bad_idx = np.where(~np.isfinite(weights))[0]
        # Show first few problematic events
        print("[compute_event_weights] Non-finite weights at indices (first 10):",
              bad_idx[:10])
        for i in bad_idx[:5]:
            print(
                f"    i={i}, tc_years={tc[i]}, mc_window={mc[i]}, "
                f"weight={weights[i]}"
            )
    # ---------- END DEBUG BLOCK ----------

    return weights


def estimate_kernel(
    df_events: pd.DataFrame,
    config: SSMConfig,
) -> np.ndarray:
    """
    Estimate adaptive kernel radii for each event as the distance (km)
    to its N-th nearest neighbour.

    Returns
    -------
    kernel_r_km : np.ndarray
        1D array of length len(df_events) with kernel radius (km) per event.
    """

    lon = df_events["longitude"].to_numpy(dtype=float)
    lat = df_events["latitude"].to_numpy(dtype=float)
    n_events = len(df_events)

    print(f"[estimate_kernel] Computing pairwise distances for {n_events} events...")

    dist_mat = pairwise_dist(lon, lat)

    dist_sorted = np.sort(dist_mat, axis=1)

    nN = config.n_neighbors
    max_index = min(nN, n_events - 1)

    kernel_r_km = dist_sorted[:, max_index]

    return kernel_r_km


def compute_ssm(
    df_events: pd.DataFrame,
    df_grid: pd.DataFrame,
    weights: np.ndarray,
    kernel_r_km: np.ndarray,
    config: SSMConfig,
) -> np.ndarray:
    """
    Compute smoothed seismicity rates on the grid.

    For each event i:
      - compute distances r_ij to all grid points
      - keep only r_ij <= max_event_grid_dist_km
      - kernel: K_ij = 1 / (r_ij^2 + d_i^2)^p
      - normalize per event: sum_j K_ij = 1
      - scale by event weight w_i
      - add to lambda_j
    """

    lon_grid = df_grid["lon"].to_numpy(dtype=float)
    lat_grid = df_grid["lat"].to_numpy(dtype=float)

    n_events = len(df_events)
    n_cells = len(df_grid)

    rates = np.zeros(n_cells, dtype=float)

    max_dist = config.max_event_grid_dist_km
    p = config.kernel_power
    eps = 1e-6

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
        #  minimum kernel radius
        d_i = max(kernel_r_km[i], config.min_kernel_km)
        w_i = weights[i]

        r = point_to_grid_dist(lon_ev[i], lat_ev[i], lon_grid, lat_grid)

        # apply dist cutoff
        mask = r <= max_dist
        if not np.any(mask):
            continue

        r_sub = r[mask]

        r2_plus_d2 = r_sub**2 + d_i**2
        r2_plus_d2 = np.maximum(r2_plus_d2, eps**2)

        kernel_vals = 1.0 / (r2_plus_d2 ** p)

        sum_kernel = kernel_vals.sum()
        if sum_kernel <= 0.0 or not np.isfinite(sum_kernel) or w_i == 0.0:
            continue

        contrib = kernel_vals * (w_i / sum_kernel)

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

    return rates


def truncated_gr_on_grid(
    rates: np.ndarray,
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
    rates : array (n_cells,)
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

    total_shape = rates.sum()
    lambda_global = 10.0 ** (a - b * mmin)

    shape = rates / total_shape
    rates_mge_mmin = shape * lambda_global

    mag_edges = np.arange(mmin, mmax + 1e-6, delta_m)
    if mag_edges[-1] < mmax - 1e-5:
        mag_edges = np.append(mag_edges, mmax)
    n_bins = len(mag_edges) - 1
    n_cells = rates_mge_mmin.size

    rates_bins = np.zeros((n_cells, n_bins), dtype=float)

    for i in range(n_bins):
        M_lo = mag_edges[i]
        M_hi = mag_edges[i + 1]

        fac_lo = 10.0 ** (b * (mmin - M_lo))

        if M_hi < mmax:
            fac_hi = 10.0 ** (b * (mmin - M_hi))
        else:
            fac_hi = 0.0

        lam_lo = rates_mge_mmin * fac_lo
        lam_hi = rates_mge_mmin * fac_hi

        rates_bins[:, i] = np.maximum(lam_lo - lam_hi, 0.0)

    return rates_bins, mag_edges


def write_ssm(
    df_grid: pd.DataFrame,
    rates_bins: np.ndarray,
    mag_edges: np.ndarray,
    depth_value: float = 0.0,
    out_path: Path = Path("output/ssm_grid.csv"),
) -> None:
    """
    Write the smoothed seismicity model with per-bin rates to a CSV.

    Columns:
      lon, lat, depth, rate_M  (for each magnitude bin)
    """
    out_path = Path(out_path)

    n_bins = rates_bins.shape[1]


    df_out = df_grid.copy()
    df_out["depth"] = depth_value

    for i in range(n_bins):
        M_lo = mag_edges[i]
        M_hi = mag_edges[i + 1]
        col = f"rate_M{M_lo:.1f}_{M_hi:.1f}"
        df_out[col] = rates_bins[:, i]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_path, index=False)
    print(f"[write_ssm] Wrote {out_path}")


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
    out_path: Path = Path("output/ssm.tif"),
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


    out_path = Path(out_path)


    lons = df_grid["lon"].to_numpy(dtype=float)
    lats = df_grid["lat"].to_numpy(dtype=float)

    unique_lons = np.sort(np.unique(lons))
    unique_lats = np.sort(np.unique(lats))

    dx = np.median(np.diff(unique_lons))
    dy = np.median(np.diff(unique_lats))

    lon_min = unique_lons.min()
    lon_max = unique_lons.max()
    lat_min = unique_lats.min()
    lat_max = unique_lats.max()

    n_cols = int(round((lon_max - lon_min) / dx)) + 1
    n_rows = int(round((lat_max - lat_min) / dy)) + 1

    arr = np.full((n_rows, n_cols), np.nan, dtype=float)

    for lon, lat, val in zip(lons, lats, values):
        col = int(round((lon - lon_min) / dx))
        row = int(round((lat_max - lat) / dy))
        if 0 <= row < n_rows and 0 <= col < n_cols:
            arr[row, col] = val

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


if __name__ == "__main__":

    grid_path = './grid.csv'
    input_cat = './cat.csv'

    cfg = SSMConfig()

    bbox = (cfg.lon_min, cfg.lon_max, cfg.lat_min, cfg.lat_max)

    df_grid = load_grid(grid_path, bbox=bbox)
    df_cat = load_catalog(input_cat,bbox=bbox)

    weights_all = compute_event_weights(df_cat, cfg)
    kernel_all = estimate_kernel(df_cat, cfg)
    total_rates = compute_ssm(
        df_events=df_cat,
        df_grid=df_grid,
        weights=weights_all,
        kernel_r_km=kernel_all,
        config=cfg
    )

    a_val = cfg.a_value
    b_val = cfg.b_value
    m_min = cfg.m_min
    m_max = cfg.m_max
    delta_m = cfg.dm

    rates_bins, mag_edges = truncated_gr_on_grid(
        total_rates,
        a=a_val,
        b=b_val,
        mmin=m_min,
        mmax=m_max,
        delta_m=delta_m,
    )

    write_ssm(
        df_grid,
        rates_bins,
        mag_edges,
        depth_value=0.0,
        out_path=cfg.outdir / "ssm.csv",
    )

    rates = rates_bins.sum(axis=1)
    rates_log10 = safe_log10(rates)

    # Log10 raster
    write_ssm_raster(
        df_grid,
        rates_log10,
        out_path=cfg.outdir / "ssm_log10.tif",
    )


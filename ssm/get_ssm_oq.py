# ps_pointsource_from_xml.py

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd

from openquake.hazardlib import nrml
from openquake.hazardlib.sourceconverter import SourceConverter
from openquake.hazardlib.source.point import PointSource
from openquake.hazardlib.mfd import TruncatedGRMFD

from ssm import paths

import matplotlib.pyplot as plt

def safe_log10(values: np.ndarray, *, fill_value: float = np.nan) -> np.ndarray:
    """
    Safe log10 for arrays: values <= 0 or non-finite -> fill_value (default NaN).
    """
    values = np.asarray(values, dtype=float)
    out = np.full_like(values, fill_value, dtype=float)
    mask = (values > 0.0) & np.isfinite(values)
    out[mask] = np.log10(values[mask])
    return out


def read_point_sources(xml_path: Path) -> List[PointSource]:
    """
    Read a NRML source model and return a list of OpenQuake PointSource objects
    for all <pointSource> elements.
    """
    xml_path = Path(xml_path)
    model = nrml.read(xml_path)
    ns = "{" + model.attrib["xmlns"] + "}"
    sm = model[0]
    # Collect only <pointSource> nodes
    ps_nodes = []
    for src_grp in sm:
        for src in src_grp:
            tag_name = src.tag.split(ns)[1]
            if tag_name == "pointSource":
                ps_nodes.append(src)

    conv = SourceConverter()
    sources: List[PointSource] = [
        conv.convert_node(node) for node in ps_nodes if node
    ]
    for src in sources:
        if isinstance(src.mfd, TruncatedGRMFD):
            src.mfd.bin_width = 0.1

    print(
        f"[read_point_sources] Loaded {len(sources)} PointSource objects "
        f"from {xml_path}"
    )
    return sources


def point_sources_to_dataframe(sources: List[PointSource]) -> pd.DataFrame:
    """
    Convert a list of PointSource objects into a DataFrame with:

      lon, lat, rate_total, depth_mean, min_mag, max_mag,
      mfd_type, magnitude_scaling_relationship, rupture_aspect_ratio,
      upper_seismogenic_depth, lower_seismogenic_depth

    Assumes MFDs support get_annual_occurrence_rates() returning
    (mag, rate) pairs (like EvenlyDiscretizedMFD, TruncatedGRMFD, etc.).
    """
    records = []
    mfd_min_mags = []
    mfd_dMs = []
    mfd_nbins = []

    for src in sources:
        # location
        lon = float(src.location.longitude)
        lat = float(src.location.latitude)

        # --- MFD ---
        mfd = src.mfd
        mfd_type = mfd.__class__.__name__

        if not hasattr(mfd, "get_annual_occurrence_rates"):
            raise ValueError(
                f"[point_sources_to_dataframe] MFD of type {mfd_type} has no "
                f"'get_annual_occurrence_rates' method."
            )

        # get_annual_occurrence_rates returns list of (mag, rate)
        mag_rate_pairs = mfd.get_annual_occurrence_rates()
        mags = np.array([mr[0] for mr in mag_rate_pairs], dtype=float)
        rates = np.array([mr[1] for mr in mag_rate_pairs], dtype=float)

        nbins = rates.size
        rate_total = float(rates.sum())

        # basic mag grid properties inferred from mags
        min_mag = float(mags.min())
        max_mag = float(mags.max())
        if nbins > 1:
            dM = float(np.median(np.diff(mags)))
        else:
            dM = np.nan  # degenerate case (unlikely here)

        mfd_min_mags.append(min_mag)
        mfd_dMs.append(dM)
        mfd_nbins.append(nbins)

        # --- hypocentral depth: probability-weighted mean ---
        hd = src.hypocenter_distribution
        probs = []
        depths = []
        for item in hd.data:
            p = float(item[0])
            z = float(item[1])
            probs.append(p)
            depths.append(z)

        probs = np.asarray(probs, dtype=float)
        depths = np.asarray(depths, dtype=float)
        if probs.sum() > 0:
            probs = probs / probs.sum()
        depth_mean = float(np.sum(probs * depths))

        # source parameters
        msr_name = src.magnitude_scaling_relationship.__class__.__name__
        rar = float(src.rupture_aspect_ratio)
        usd = float(src.upper_seismogenic_depth)
        lsd = float(src.lower_seismogenic_depth)

        rec = {
            "lon": lon,
            "lat": lat,
            "rate_total": rate_total,
            "depth_mean": depth_mean,
            "min_mag": min_mag,
            "max_mag": max_mag,
            "mfd_type": mfd_type,
            "magnitude_scaling_relationship": msr_name,
            "rupture_aspect_ratio": rar,
            "upper_seismogenic_depth": usd,
            "lower_seismogenic_depth": lsd,
        }
        records.append(rec)

    df = pd.DataFrame(records)
    print(f"[point_sources_to_dataframe] Built table with {len(df)} rows.")

    # Quick check: consistent MFD grid?
    mfd_min_mags = np.asarray(mfd_min_mags)
    mfd_dMs = np.asarray(mfd_dMs)
    mfd_nbins = np.asarray(mfd_nbins)

    if not np.allclose(mfd_min_mags, mfd_min_mags[0], atol=1e-6, equal_nan=True):
        print(
            "[point_sources_to_dataframe] WARNING: min_mag varies across sources. "
            "Global GR fit will use the global min_mag from the aggregated MFD."
        )
    if not np.allclose(mfd_dMs[~np.isnan(mfd_dMs)], mfd_dMs[~np.isnan(mfd_dMs)][0], atol=1e-6):
        print(
            "[point_sources_to_dataframe] WARNING: dM varies across sources. "
            "Global GR fit will require uniform dM (or error out)."
        )
    if not np.all(mfd_nbins == mfd_nbins[0]):
        print(
            "[point_sources_to_dataframe] WARNING: number of bins varies across "
            "sources. This is expected when mmax differs."
        )

    return df
def _build_global_incremental_mfd(
    sources: list[PointSource],
) -> tuple[np.ndarray, np.ndarray, float]:
    """
    Sum incremental MFDs from all PointSource objects to build a global
    incremental MFD on a common magnitude grid.

    Assumes each MFD has get_annual_occurrence_rates() -> [(mag, rate), ...].

    Steps:
      - for each source, read mags_src, rates_src from (mag, rate) pairs
      - infer dM_src from mags_src and check binWidth consistency
      - define a global grid from global_minMag to global_maxMag with dM
      - project each source's incremental rates onto this grid

    Returns
    -------
    mags_global : array
        Global bin centres (Mw).
    rates_global : array
        Global incremental rates per bin (events/yr), summed over all sources.
    dM : float
        Bin width (common across all sources).
    """
    if not sources:
        raise ValueError("[_build_global_incremental_mfd] No sources given.")

    min_mags = []
    max_mags = []
    dMs = []

    # --- 1. Collect per-source minMag, maxMag, dM from the actual (mag, rate) grid ---
    per_source_mags = []  # keep for reuse

    for src in sources:
        mfd = src.mfd
        if not hasattr(mfd, "get_annual_occurrence_rates"):
            raise ValueError(
                "[_build_global_incremental_mfd] MFD has no get_annual_occurrence_rates()."
            )

        mag_rate_pairs = mfd.get_annual_occurrence_rates()
        mags_src = np.array([mr[0] for mr in mag_rate_pairs], dtype=float)

        if mags_src.size < 1:
            raise ValueError("[_build_global_incremental_mfd] Empty MFD for a source.")

        if mags_src.size > 1:
            dM_src = float(np.median(np.diff(mags_src)))
        else:
            dM_src = np.nan  # edge case; we'll ignore in dM consistency

        mmin_src = float(mags_src.min())
        mmax_src = float(mags_src.max())

        min_mags.append(mmin_src)
        max_mags.append(mmax_src)
        dMs.append(dM_src)
        per_source_mags.append(mags_src)

    min_mags = np.array(min_mags)
    max_mags = np.array(max_mags)
    dMs = np.array(dMs)

    # --- 2. Check binWidth consistency (ignore NaN from 1-bin sources) ---
    dMs_finite = dMs[~np.isnan(dMs)]
    if dMs_finite.size == 0:
        raise ValueError("[_build_global_incremental_mfd] Could not infer dM from any source.")
    dM_ref = float(np.median(dMs_finite))

    if not np.allclose(dMs_finite, dM_ref, rtol=1e-6, atol=1e-6):
        print("[_build_global_incremental_mfd] WARNING: binWidth not uniform across sources.")
        print(f"  Bin widths (finite): {np.unique(np.round(dMs_finite, 5))}")
        raise NotImplementedError(
            "Different binWidth values across point sources "
            "(e.g., incremental vs truncated with weird binning). "
            "Fix the NRML or implement resampling."
        )

    dM = dM_ref

    # --- 3. Global min and max mag from all sources ---
    global_min_mag = float(min_mags.min())
    global_max_mag = float(max_mags.max())

    # Define global grid
    n_bins_global = int(round((global_max_mag - global_min_mag) / dM)) + 1
    mags_global = global_min_mag + np.arange(n_bins_global) * dM
    rates_global = np.zeros(n_bins_global, dtype=float)

    # --- 4. Project each source MFD onto the global grid ---
    for src, mags_src in zip(sources, per_source_mags):
        mfd = src.mfd
        mag_rate_pairs = mfd.get_annual_occurrence_rates()
        # mags_src already computed; we only need the rates now
        rates_src = np.array([mr[1] for mr in mag_rate_pairs], dtype=float)

        if mags_src.size != rates_src.size:
            raise RuntimeError(
                "[_build_global_incremental_mfd] mags_src and rates_src size mismatch."
            )

        # Map each source bin centre onto global index
        idx_global = np.rint((mags_src - global_min_mag) / dM).astype(int)

        for idx, rate in zip(idx_global, rates_src):
            # DEBUG print if needed:
            # print(idx, rate)
            if 0 <= idx < n_bins_global:
                rates_global[idx] += float(rate)
            else:
                print(
                    "[_build_global_incremental_mfd] WARNING: bin centre outside global grid "
                    f"(M={float(mags_src)}, idx={idx}). Ignoring."
                )

    print("[_build_global_incremental_mfd] Global incremental MFD:")
    print(f"  n_bins = {n_bins_global}, dM = {dM:.3f}")
    print(f"  M range = [{mags_global.min():.2f}, {mags_global.max():.2f}]")
    print(f"  Total rate (sum over bins) = {rates_global.sum():.3f} /yr")

    return mags_global, rates_global, dM

def print_mfd_grid_summary(sources: list[PointSource]) -> None:
    """
    Print summary of min_mag, max_mag, and dM across all point sources,
    inferred from each MFD's (mag, rate) pairs.
    """
    min_mags = []
    max_mags = []
    dMs = []
    classes = []
    for src in sources:
        mfd = src.mfd
        if not hasattr(mfd, "get_annual_occurrence_rates"):
            continue

        mag_rate_pairs = mfd.get_annual_occurrence_rates()
        mags = np.array([mr[0] for mr in mag_rate_pairs], dtype=float)
        if mags.size == 0:
            continue

        mmin = float(mags.min())
        mmax = float(mags.max())
        if mags.size > 1:
            dM = float(np.median(np.diff(mags)))
        else:
            dM = np.nan
        classes.append(mfd.__class__.__name__)
        min_mags.append(mmin)
        max_mags.append(mmax)
        dMs.append(dM)

    if not min_mags:
        print("[print_mfd_grid_summary] No MFDs with annual rates found.")
        return

    min_mags = np.array(min_mags)
    max_mags = np.array(max_mags)
    dMs = np.array(dMs)

    print("[print_mfd_grid_summary] MFD grid summary over point sources:")

    uniq_classes = set(classes)
    uniq_min = np.unique(np.round(min_mags, 3))
    uniq_max = np.unique(np.round(max_mags, 3))
    uniq_dM = np.unique(np.round(dMs[~np.isnan(dMs)], 5))

    print(f"  Unique MFDs   : {uniq_classes}")
    print(f"  Unique minMag values: {uniq_min}")
    print(f"  Unique maxMag values: {uniq_max}")
    print(f"  Unique dM values    : {uniq_dM}")

    print("  (minMag, maxMag, dM) combinations and counts:")
    combos = {}
    for mmin, mmax, dm in zip(min_mags, max_mags, dMs):
        print(dm, mmin, mmax)
        key = (round(mmin, 3), round(mmax, 3), None if np.isnan(dm) else round(dm, 5))
        combos[key] = combos.get(key, 0) + 1
    for (mmin, mmax, dm), count in sorted(combos.items()):
        print(
            f"    minMag={mmin:.3f}, maxMag={mmax:.3f}, "
            f"dM={dm if dm is not None else 'NaN'} : {count} sources"
        )

import matplotlib.pyplot as plt


def plot_global_mfd(
    mags: np.ndarray,
    rates_inc: np.ndarray,
    *,
    out_path: Path,
) -> None:
    """
    Plot incremental and cumulative MFD (log10 rates vs M) for diagnostics.

    - Incremental: log10(lambda_i) vs M_i
    - Cumulative: log10 N(M>=m) vs M

    Only bins with positive rates are shown.
    """
    mags = np.asarray(mags, dtype=float)
    rates_inc = np.asarray(rates_inc, dtype=float)

    mask = rates_inc > 0.0
    if not np.any(mask):
        print("[plot_global_mfd] No positive rates to plot.")
        return

    m = mags[mask]
    inc = rates_inc[mask]

    # cumulative from the right
    cum = np.cumsum(inc[::-1])[::-1]

    fig, ax = plt.subplots(figsize=(6, 5))

    ax.plot(m, np.log10(inc), "o-", label="incremental", alpha=0.7)
    ax.plot(m, np.log10(cum), "s-", label="cumulative", alpha=0.7)

    ax.set_xlabel("Magnitude")
    ax.set_ylabel("log10(rate [1/yr])")
    ax.set_title("Global MFD (point-source model)")
    ax.grid(True, alpha=0.3)
    ax.legend()

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[plot_global_mfd] Wrote global MFD plot to {out_path}")
def fit_global_gr_from_sources(
    sources: list[PointSource],
    *,
    mfd_plot_path: Path | None = None,
) -> dict[str, float]:
    """
    Fit a global Gutenberg–Richter relation:

      log10 N(M>=m) = a - b m

    from the sum of all point-source incremental MFDs.
    """
    mags, rates_inc, dM = _build_global_incremental_mfd(sources)

    # Optional diagnostic plot
    if mfd_plot_path is not None:
        plot_global_mfd(mags, rates_inc, out_path=mfd_plot_path)

    # Fit incremental GR as before
    mask = rates_inc > 0.0
    mags_fit = mags[mask]
    inc_fit = rates_inc[mask]
    if mags_fit.size < 2:
        raise ValueError("[fit_global_gr_from_sources] Not enough positive-rate bins.")

    x = mags_fit
    y = np.log10(inc_fit)

    c1, c0 = np.polyfit(x, y, 1)
    b = -float(c1)
    a_incr = float(c0)

    factor = 1.0 - 10.0 ** (-b * dM)
    if factor <= 0:
        raise RuntimeError("[fit_global_gr_from_sources] Invalid factor in GR conversion.")
    import math
    a_cum_1yr = a_incr - math.log10(factor)

    cum_rates = np.cumsum(inc_fit[::-1])[::-1]
    y_cum = np.log10(cum_rates)
    N_pred = 10.0 ** (a_cum_1yr - b * mags_fit)
    y_pred = np.log10(N_pred)

    resid = y_cum - y_pred
    rms_log10 = float(np.sqrt(np.mean(resid ** 2)))
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y_cum - np.mean(y_cum)) ** 2))
    r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else np.nan

    mmin = float(mags_fit.min())
    mmax = float(mags_fit.max())
    dm = float(dM)

    print("[fit_global_gr_from_sources] Global GR fit (point-source model):")
    print(f"  a (cum, per year) = {a_cum_1yr:.3f}")
    print(f"  b                 = {b:.3f}")
    print(f"  mmin              = {mmin:.2f}")
    print(f"  mmax              = {mmax:.2f}")
    print(f"  dM                = {dm:.3f}")
    print(f"  R^2 (log10 cum)   = {r2:.4f}")
    print(f"  RMS misfit (log10 cum) = {rms_log10:.4f}")

    return {
        "a": a_cum_1yr,
        "b": b,
        "mmin": mmin,
        "mmax": mmax,
        "dm": dm,
        "r2_log10": r2,
        "rms_log10": rms_log10,
    }

def write_points_csv(df: pd.DataFrame, out_path: Path) -> None:
    """
    Write parsed point-source information to CSV for debugging / QGIS.

    Columns include:
      lon, lat, rate_total, depth_mean, min_mag, max_mag, mfd_type, ...
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"[write_points_csv] Wrote parsed point sources to {out_path}")


def write_raster_from_points(
    df: pd.DataFrame,
    values: np.ndarray,
    *,
    out_path: Path,
) -> None:
    """
    Write a GeoTIFF raster from lon/lat points and associated values.

    Each point is treated as the center of a pixel. Grid is inferred from
    the unique lon/lat values. Cells without a point remain NaN.
    """
    import rasterio
    from rasterio.transform import from_origin

    out_path = Path(out_path)

    if not {"lon", "lat"}.issubset(df.columns):
        raise ValueError("[write_raster_from_points] df must have 'lon' and 'lat' columns.")

    lons = df["lon"].to_numpy(dtype=float)
    lats = df["lat"].to_numpy(dtype=float)

    if lons.size != values.size:
        raise ValueError("[write_raster_from_points] values length must match number of rows in df.")

    unique_lons = np.sort(np.unique(lons))
    unique_lats = np.sort(np.unique(lats))
    if unique_lons.size < 2 or unique_lats.size < 2:
        raise ValueError("[write_raster_from_points] Need at least 2 unique lon/lat values.")

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
        f"[write_raster_from_points] Wrote {out_path} "
        f"(n_rows={n_rows}, n_cols={n_cols}, dx={dx:.4f}, dy={dy:.4f})"
    )

def build_regular_grid_from_points(
    df_points: pd.DataFrame,
    dx: float,
    dy: float,
) -> pd.DataFrame:
    """
    Build a regular lon/lat grid covering the extent of the point sources.

    Parameters
    ----------
    df_points : DataFrame
        Must have 'lon' and 'lat' columns (point-source locations).
    dx, dy : float
        Grid spacing in degrees for longitude and latitude.

    Returns
    -------
    grid_df : DataFrame
        Columns:
        - 'lon'
        - 'lat'

    Notes
    -----
    - Grid cell centers run from lon_min..lon_max and lat_min..lat_max
      with step dx, dy.
    """
    if not {"lon", "lat"}.issubset(df_points.columns):
        raise ValueError("[build_regular_grid_from_points] df_points must have 'lon' and 'lat' columns.")

    lons = df_points["lon"].to_numpy(dtype=float)
    lats = df_points["lat"].to_numpy(dtype=float)

    lon_min = float(lons.min())
    lon_max = float(lons.max())
    lat_min = float(lats.min())
    lat_max = float(lats.max())

    # make sure we hit the max by rounding
    n_cols = int(np.floor((lon_max - lon_min) / dx)) + 1
    n_rows = int(np.floor((lat_max - lat_min) / dy)) + 1

    lon_vec = lon_min + np.arange(n_cols) * dx
    lat_vec = lat_min + np.arange(n_rows) * dy

    lon_grid, lat_grid = np.meshgrid(lon_vec, lat_vec)

    grid_df = pd.DataFrame(
        {
            "lon": lon_grid.ravel(),
            "lat": lat_grid.ravel(),
        }
    )

    print(
        "[build_regular_grid_from_points] Built grid "
        f"lon=[{lon_min:.3f},{lon_max:.3f}], lat=[{lat_min:.3f},{lat_max:.3f}], "
        f"dx={dx}, dy={dy}, n_points={len(grid_df)}"
    )

    return grid_df

def summarize_source_parameters(df: pd.DataFrame) -> None:
    """
    Print value counts for magnitude_scaling_relationship, rupture_aspect_ratio,
    upper_seismogenic_depth, lower_seismogenic_depth (if present).
    """
    cols = [
        "magnitude_scaling_relationship",
        "rupture_aspect_ratio",
        "upper_seismogenic_depth",
        "lower_seismogenic_depth",
    ]
    for col in cols:
        if col in df.columns:
            print(f"[summarize_source_parameters] {col} value counts:")
            print(df[col].value_counts(dropna=False))
        else:
            print(f"[summarize_source_parameters] Column '{col}' not found in table.")

def haversine_distance_km(
    lon1_deg: float,
    lat1_deg: float,
    lon2_deg: np.ndarray,
    lat2_deg: np.ndarray,
) -> np.ndarray:
    """
    Great-circle distance (km) from one point to many points,
    using the haversine formula.
    """
    R = 6371.0
    lon1 = np.deg2rad(lon1_deg)
    lat1 = np.deg2rad(lat1_deg)
    lon2 = np.deg2rad(lon2_deg)
    lat2 = np.deg2rad(lat2_deg)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * np.arcsin(np.sqrt(a))
    return R * c


def interpolate_points_to_grid(
    df_points: pd.DataFrame,
    values: np.ndarray,
    grid_df: pd.DataFrame,
    *,
    max_dist_km: float | None = None,
) -> np.ndarray:
    """
    Nearest-neighbour interpolation from scattered points to a regular grid.

    Parameters
    ----------
    df_points : DataFrame
        Must have 'lon' and 'lat' columns (point-source locations).
    values : array-like, shape (N_points,)
        Values at each point (e.g. total rates, mean depths).
    grid_df : DataFrame
        Target grid with 'lon' and 'lat' columns for cell centres.
    max_dist_km : float or None, optional
        If given, grid cells farther than this from any point will be NaN.
        If None, every cell gets the value of its nearest point.

    Returns
    -------
    grid_values : np.ndarray, shape (N_grid,)
        Interpolated values at each grid point, in the same order as grid_df.
    """
    if not {"lon", "lat"}.issubset(df_points.columns):
        raise ValueError("[interpolate_points_to_grid] df_points must have 'lon' and 'lat' columns.")
    if not {"lon", "lat"}.issubset(grid_df.columns):
        raise ValueError("[interpolate_points_to_grid] grid_df must have 'lon' and 'lat' columns.")

    values = np.asarray(values, dtype=float)
    if len(values) != len(df_points):
        raise ValueError(
            "[interpolate_points_to_grid] values length must match number of df_points rows."
        )

    lon_p = df_points["lon"].to_numpy(dtype=float)
    lat_p = df_points["lat"].to_numpy(dtype=float)

    lon_g = grid_df["lon"].to_numpy(dtype=float)
    lat_g = grid_df["lat"].to_numpy(dtype=float)

    n_grid = len(grid_df)
    n_points = len(df_points)

    grid_vals = np.full(n_grid, np.nan, dtype=float)

    print(
        f"[interpolate_points_to_grid] Interpolating {n_points} points "
        f"to {n_grid} grid cells (nearest neighbour)."
    )

    for j in range(n_grid):
        dists = haversine_distance_km(lon_g[j], lat_g[j], lon_p, lat_p)
        k = int(np.argmin(dists))
        dmin = float(dists[k])
        if (max_dist_km is None) or (dmin <= max_dist_km):
            grid_vals[j] = values[k]

        if (j + 1) % 5000 == 0 or j == n_grid - 1:
            print(
                f"[interpolate_points_to_grid] Processed {j+1}/{n_grid} grid cells "
                f"(closest distance last cell = {dmin:.2f} km)"
            )

    return grid_vals
def aggregate_depth_to_grid(
    df_points: pd.DataFrame,
    grid_df: pd.DataFrame,
    *,
    rate_col: str = "rate_total",
    depth_col: str = "depth_mean",
) -> np.ndarray:
    """
    Compute a rate-weighted average depth per grid cell by (lon, lat).

    If multiple point sources share the same lon/lat (e.g., crustal + slab),
    this returns sum(rate_i * depth_i) / sum(rate_i) for that cell.

    Cells with no sources become NaN.
    """
    required_cols = {"lon", "lat", rate_col, depth_col}
    if not required_cols.issubset(df_points.columns):
        raise ValueError(
            f"[aggregate_depth_to_grid] df_points must contain {required_cols}."
        )
    if not {"lon", "lat"}.issubset(grid_df.columns):
        raise ValueError("[aggregate_depth_to_grid] grid_df must have 'lon' and 'lat'.")

    def _weighted_depth(group: pd.DataFrame) -> float:
        r = group[rate_col].to_numpy(dtype=float)
        z = group[depth_col].to_numpy(dtype=float)
        if np.all(r <= 0):
            # fallback: simple mean if all rates are zero (shouldn't happen often)
            return float(np.nanmean(z))
        return float(np.sum(r * z) / np.sum(r))

    # groupby(...).apply(...) -> Series with index (lon, lat) and values = depth
    grouped = (
        df_points
        .groupby(["lon", "lat"])
        .apply(_weighted_depth)
        .reset_index(name="depth_weighted")
    )

    # Merge onto target grid (left join keeps all grid cells)
    merged = grid_df.merge(grouped, on=["lon", "lat"], how="left")

    values_on_grid = merged["depth_weighted"].to_numpy(dtype=float)
    return values_on_grid

def split_by_depth(
    df: pd.DataFrame,
    *,
    depth_col: str = "depth_mean",
    threshold_km: float = 50.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split point sources into shallow and deep subsets based on a depth threshold.

    Parameters
    ----------
    df : DataFrame
        Must contain `depth_col` (e.g. 'depth_mean').
    depth_col : str
        Column with depth in km (positive down).
    threshold_km : float
        Depth threshold (km). Shallow: depth < threshold_km, Deep: >=.

    Returns
    -------
    df_shallow, df_deep : DataFrame, DataFrame
    """
    if depth_col not in df.columns:
        raise ValueError(f"[split_by_depth] Column '{depth_col}' not in DataFrame.")

    df_shallow = df[df[depth_col] < threshold_km].copy()
    df_deep = df[df[depth_col] >= threshold_km].copy()

    print(f"[split_by_depth] threshold = {threshold_km} km")
    print(f"  shallow (<{threshold_km} km): {len(df_shallow)} points")
    print(f"  deep    (≥{threshold_km} km): {len(df_deep)} points")

    if "rate_total" in df.columns:
        print("  shallow total rate =", df_shallow["rate_total"].sum(), "/yr")
        print("  deep    total rate =", df_deep["rate_total"].sum(), "/yr")
        print("  ALL     total rate =", df["rate_total"].sum(), "/yr")

    return df_shallow, df_deep


def aggregate_rates_to_grid(
    df_points: pd.DataFrame,
    grid_df: pd.DataFrame,
    *,
    value_col: str = "rate_total",
) -> np.ndarray:
    """
    Sum rates from point sources into the cells of a target grid by (lon, lat).

    Assumes:
      - df_points has columns ['lon', 'lat', value_col]
      - grid_df has columns ['lon', 'lat'] (your SSM/grid points)

    Returns
    -------
    values_on_grid : np.ndarray
        1D array of length len(grid_df), where each element is the sum of
        `value_col` for all point sources exactly at that (lon, lat).
        Cells with no point sources become NaN.
    """
    required_cols = {"lon", "lat", value_col}
    if not required_cols.issubset(df_points.columns):
        raise ValueError(
            f"[aggregate_rates_to_grid] df_points must contain {required_cols}."
        )
    if not {"lon", "lat"}.issubset(grid_df.columns):
        raise ValueError("[aggregate_rates_to_grid] grid_df must have 'lon' and 'lat'.")

    # 1) Group by lon/lat and sum the rates
    grouped = (
        df_points
        .groupby(["lon", "lat"], as_index=False)[value_col]
        .sum()
        .rename(columns={value_col: "rate_sum"})
    )

    # 2) Merge onto grid
    merged = grid_df.merge(grouped, on=["lon", "lat"], how="left")

    values_on_grid = merged["rate_sum"].to_numpy(dtype=float)
    # cells with no sources -> NaN
    return values_on_grid
def build_pointsource_rasters_and_summary(
    xml_path: Path,
    *,
    rate_out_tif: Path,
    rate_log10_out_tif: Path,
    depth_out_tif: Path,
    grid_df: pd.DataFrame | None = None,
    target_grid: pd.DataFrame | None = None,
    points_csv_out: Path | None = None,
    depth_threshold_km: float = 50.0,
) -> dict[str, float]:
    """
    High-level:

      - read pointSources from NRML
      - build a DataFrame with lon/lat, rate_total, depth_mean, min_mag, max_mag, etc.
      - fit a global GR (a,b,mmin,mmax,dm)
      - write:
          * total-rate raster (sum over all MFD bins, events/year)
          * log10(total-rate) raster
          * depth raster (mean hypocentral depth)
      - print value counts for MSR, RAR, USD, LSD

    Parameters
    ----------
    xml_path : Path
        Path to the NRML pointSource model (XML).
    rate_out_tif : Path
        GeoTIFF: total rate (events/yr) on grid.
    rate_log10_out_tif : Path
        GeoTIFF: log10(total rate) on grid.
    depth_out_tif : Path
        GeoTIFF: mean hypocentral depth (km) on grid.
    grid_df : DataFrame, optional
        Grid with columns 'lon','lat' (e.g. your SSM grid_01). If given,
        takes precedence if target_grid is None.
    target_grid : DataFrame, optional
        Alternative way to pass the grid (same format as grid_df). If not None,
        overrides grid_df.
    points_csv_out : Path, optional
        If given, write the parsed point sources to CSV and produce scatter plots.
    depth_threshold_km : float, optional
        Currently only printed as info; can be used for further shallow/deep
        diagnostics if needed.

    Returns
    -------
    ab_info : dict
        {'a', 'b', 'mmin', 'mmax', 'dm', 'r2_log10', 'rms_log10}
        for the total point-source model.
    """
    # ---- 1. Read XML and convert to PointSource objects ----
    sources = read_point_sources(xml_path)
    print_mfd_grid_summary(sources)

    # ---- 2. Convert to DataFrame of point sources ----
    df = point_sources_to_dataframe(sources)

    # Optional CSV + scatter diagnostics
    if points_csv_out is not None:
        points_csv_out = Path(points_csv_out)
        points_csv_out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(points_csv_out, index=False)
        print(
            f"[build_pointsource_rasters_and_summary] Wrote points CSV to "
            f"{points_csv_out}"
        )

        # depth + rate scatter on raw points
        plot_depth_scatter(df, points_csv_out.parent / "ps_depth_scatter_all.png")
        plot_rate_log10_scatter(
            df, points_csv_out.parent / "ps_rate_log10_scatter_all.png"
        )

    # ---- 3. Global GR fit from summed incremental MFDs ----
    ab_info = fit_global_gr_from_sources(
        sources,
        mfd_plot_path=rate_out_tif.parent / "pointsource_global_mfd.png",
    )

    # Total rate and depth at point-source locations
    rates_total = df["rate_total"].to_numpy(dtype=float)
    depths = df["depth_mean"].to_numpy(dtype=float)

    # ---- 4. Choose grid for rasterization ----
    # Priority:
    #   1) target_grid if not None
    #   2) grid_df if not None
    #   3) fallback: sparse rasters directly at point locations
    if target_grid is not None:
        grid = target_grid
        print(
            "[build_pointsource_rasters_and_summary] Using 'target_grid' "
            f"with {len(grid)} points."
        )
    elif grid_df is not None:
        grid = grid_df
        print(
            "[build_pointsource_rasters_and_summary] Using 'grid_df' "
            f"with {len(grid)} points."
        )
    else:
        grid = None

    # ---- 5. If no grid, fallback to sparse rasters on point locations ----
    if grid is None:
        print(
            "[build_pointsource_rasters_and_summary] No grid_df/target_grid given: "
            "writing rasters directly on point locations (sparse)."
        )
        write_raster_from_points(df, rates_total, out_path=rate_out_tif)
        rates_total_log10 = safe_log10(rates_total)
        write_raster_from_points(df, rates_total_log10, out_path=rate_log10_out_tif)
        write_raster_from_points(df, depths, out_path=depth_out_tif)

        summarize_source_parameters(df)
        print("[build_pointsource_rasters_and_summary] Global GR parameters:")
        print(
            f"  a = {ab_info['a']:.3f}, "
            f"b = {ab_info['b']:.3f}, "
            f"mmin = {ab_info['mmin']:.2f}, "
            f"mmax = {ab_info['mmax']:.2f}, "
            f"dM = {ab_info['dm']:.3f}"
        )
        # NOTE: depth_threshold_km not used here (only for potential extra diagnostics)
        return ab_info

    # Ensure grid has lon/lat
    if not {"lon", "lat"}.issubset(grid.columns):
        raise ValueError(
            "[build_pointsource_rasters_and_summary] grid_df/target_grid must "
            "have 'lon' and 'lat' columns."
        )

    # ---- 6. Aggregate onto target grid by (lon, lat) ----
    print(
        f"[build_pointsource_rasters_and_summary] Aggregating point-source "
        f"rates/depths onto grid with {len(grid)} cells."
    )

    # These functions should:
    #   - for each grid cell, sum rate_total of all sources in that cell (rates)
    #   - for depth: rate-weighted mean depth (or simple mean) per cell
    rates_on_grid = aggregate_rates_to_grid(df_points=df, grid_df=grid)
    depths_on_grid = aggregate_depth_to_grid(df_points=df, grid_df=grid)
    # ---- 7. Write rasters on the grid ----
    write_raster_from_points(grid, rates_on_grid, out_path=rate_out_tif)
    write_raster_from_points(
        grid,
        safe_log10(rates_on_grid),
        out_path=rate_log10_out_tif,
    )
    write_raster_from_points(grid, depths_on_grid, out_path=depth_out_tif)

    summarize_source_parameters(df)

    print("[build_pointsource_rasters_and_summary] Global GR parameters:")
    print(
        f"  a = {ab_info['a']:.3f}, "
        f"b = {ab_info['b']:.3f}, "
        f"mmin = {ab_info['mmin']:.2f}, "
        f"mmax = {ab_info['mmax']:.2f}, "
        f"dM = {ab_info['dm']:.3f}"
    )
    print(
        f"[build_pointsource_rasters_and_summary] depth_threshold_km = "
        f"{depth_threshold_km:.1f} (currently only informational)."
    )

    return ab_info


def plot_depth_scatter(df: pd.DataFrame, out_path: Path) -> None:
    """
    Scatter plot of lon/lat colored by mean hypocentral depth.

    Useful to see the raw geometry of the point-source model
    before any interpolation / rasterization.
    """
    if not {"lon", "lat", "depth_mean"}.issubset(df.columns):
        raise ValueError(
            "[plot_depth_scatter] df must have 'lon', 'lat', and 'depth_mean' columns."
        )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lons = df["lon"].to_numpy(dtype=float)
    lats = df["lat"].to_numpy(dtype=float)
    depths = df["depth_mean"].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(6, 8))

    sc = ax.scatter(
        lons,
        lats,
        c=depths,
        s=10,
        cmap="viridis",
        edgecolor="none",
    )
    cb = plt.colorbar(sc, ax=ax)
    cb.set_label("Mean hypocentral depth (km)")

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Point-source depths (raw points)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[plot_depth_scatter] Wrote depth scatter plot to {out_path}")
def plot_rate_log10_scatter(df: pd.DataFrame, out_path: Path) -> None:
    """
    Scatter plot of lon/lat colored by log10(total rate).

    Uses df['rate_total'] and applies safe_log10.
    """
    if not {"lon", "lat", "rate_total"}.issubset(df.columns):
        raise ValueError(
            "[plot_rate_log10_scatter] df must have 'lon', 'lat', and 'rate_total' columns."
        )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lons = df["lon"].to_numpy(dtype=float)
    lats = df["lat"].to_numpy(dtype=float)
    rates = df["rate_total"].to_numpy(dtype=float)
    rates_log10 = safe_log10(rates)

    fig, ax = plt.subplots(figsize=(6, 8))

    sc = ax.scatter(
        lons,
        lats,
        c=rates_log10,
        s=10,
        cmap="viridis",
        edgecolor="none",
    )
    cb = plt.colorbar(sc, ax=ax)
    cb.set_label("log10(total rate [1/yr])")

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Point-source total rates (raw points)")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[plot_rate_log10_scatter] Wrote {out_path}")


if __name__ == "__main__":
    xml_path = Path("./data/pointsources.xml")
    outdir = Path("ps_pointsource_outputs")
    outdir.mkdir(parents=True, exist_ok=True)
    df_grid = pd.read_csv(paths.grid_01)  # must have columns: lon, lat
    ab_ps = build_pointsource_rasters_and_summary(
        xml_path=xml_path,
        rate_out_tif=outdir / "ps_rate_total.tif",
        rate_log10_out_tif=outdir / "ps_log10_rate_total.tif",
        depth_out_tif=outdir / "ps_depth_mean.tif",
        grid_df=df_grid,  # your SSM grid_01 or similar
        points_csv_out=outdir / "ps_points.csv",
        depth_threshold_km=50.0,  # currently just informational
    )

    print("Point-source GR summary:", ab_ps)
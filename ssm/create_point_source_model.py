# create_point_source_model.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from openquake.hazardlib.geo.point import Point
from openquake.hazardlib.source.point import PointSource
from openquake.hazardlib.mfd.evenly_discretized import EvenlyDiscretizedMFD
from openquake.hazardlib.geo.nodalplane import NodalPlane
from openquake.hazardlib.pmf import PMF
from openquake.hazardlib.scalerel.strasser2010 import StrasserIntraslab
from openquake.hazardlib.tom import PoissonTOM
from openquake.hazardlib import sourcewriter


@dataclass
class PointSourceModelConfig:
    """
    Configuration for building the point-source model from SSM + slab.

    All values here can be tuned if needed.
    """
    # tectonic setting
    tectonic_region_type: str = "Subduction IntraSlab"

    # rupture mesh spacing
    rupture_mesh_spacing: float = 5.0  # km

    # magnitude scaling relationship
    msr_class: type = StrasserIntraslab

    # rupture aspect ratio
    rupture_aspect_ratio: float = 1.5

    # nodal-plane distribution: two conjugate planes
    npd_spec: Tuple[Tuple[float, NodalPlane], ...] = (
        (0.5, NodalPlane(0.0, 60.0, 90.0)),
        (0.5, NodalPlane(180.0, 60.0, 90.0)),
    )

    # depth offset from slab surface to hypocenter (km)
    depth_offset_km: float = 7.5

    # seismogenic thickness half-widths (km)
    half_thickness_0_50: float = 7.5   # for hypo < 50 km
    half_thickness_50_90: float = 10.0  # for 50–90 km
    half_thickness_90_plus: float = 15.0  # for > 90 km

    # Poisson time window (years)
    investigation_time_yr: float = 1.0


# ----------------------------------------------------------------------
# Helpers: read SSM MFD grid and parse magnitude bins
# ----------------------------------------------------------------------

def load_ssm_mfd_grid(ssm_csv: Path) -> tuple[pd.DataFrame, np.ndarray, float]:
    """
    Read the SSM grid with per-bin rates.

    Expected columns:
        lon, lat, depth (ignored/overwritten), rate_Mx_y, rate_My_z, ...

    Returns
    -------
    df : DataFrame
        Contains at least lon, lat and the rate_... columns.
    rates_matrix : np.ndarray, shape (n_cells, n_bins)
        Per-cell occurrence rates per magnitude bin.
    mag_edges : np.ndarray, shape (n_bins + 1,)
        Magnitude bin edges (e.g., [4.9, 5.0, 5.1, ...]).
    dM : float
        Bin width (assumed constant).
    """
    ssm_csv = Path(ssm_csv)
    df = pd.read_csv(ssm_csv)
    print(f"[load_ssm_mfd_grid] Loaded {len(df)} rows from {ssm_csv}")

    if not {"lon", "lat"}.issubset(df.columns):
        raise ValueError(
            "[load_ssm_mfd_grid] SSM CSV must contain 'lon' and 'lat' columns."
        )

    # identify magnitude-bin columns
    rate_cols = [c for c in df.columns if c.startswith("rate_M")]
    if not rate_cols:
        raise ValueError(
            "[load_ssm_mfd_grid] No 'rate_Mx_y' columns found in SSM CSV."
        )

    # parse edges from column names
    pattern = re.compile(r"rate_M([0-9]+(?:\.[0-9]+)?)_([0-9]+(?:\.[0-9]+)?)")
    edges_list: List[Tuple[str, float, float]] = []
    for col in rate_cols:
        m = pattern.fullmatch(col)
        if not m:
            raise ValueError(
                f"[load_ssm_mfd_grid] Column '{col}' does not match 'rate_Mx_y' pattern."
            )
        lo = float(m.group(1))
        hi = float(m.group(2))
        edges_list.append((col, lo, hi))

    # sort by lower edge
    edges_list.sort(key=lambda x: x[1])
    sorted_cols = [c for (c, _, _) in edges_list]
    mag_lows = np.array([lo for (_, lo, _) in edges_list], dtype=float)
    mag_highs = np.array([hi for (_, _, hi) in edges_list], dtype=float)

    # build edges array
    # e.g. lows=[4.9,5.0,5.1], highs=[5.0,5.1,5.2] -> edges=[4.9,5.0,5.1,5.2]
    mag_edges = np.concatenate([mag_lows[:1], mag_highs])
    dM_array = mag_highs - mag_lows
    dM = np.round(float(np.median(dM_array)), 1)

    if not np.allclose(dM_array, dM, atol=1e-6, rtol=1e-6):
        raise ValueError(
            f"[load_ssm_mfd_grid] Inconsistent bin widths: {np.unique(np.round(dM_array, 3))}"
        )

    print(
        "[load_ssm_mfd_grid] Magnitude bins: "
        f"min={mag_edges[0]:.2f}, max={mag_edges[-1]:.2f}, dM={dM:.3f}, n_bins={len(mag_edges)-1}"
    )

    rates_matrix = df[sorted_cols].to_numpy(dtype=float)
    return df, rates_matrix, mag_edges, dM


# ----------------------------------------------------------------------
# Slab depths and assignment to SSM points
# ----------------------------------------------------------------------

def load_slab_depth_grid(slab_csv: Path) -> pd.DataFrame:
    """
    Load the slab depth grid.

    Expected format (no header or with header you can adjust):
        lon, lat, depth

    - lon is in [0, 360] degrees -> converted to [-180, 180]
    - depth is negative (downwards) -> converted to positive (km, downwards)
    - NaNs indicate no slab.
    """
    slab_csv = Path(slab_csv)
    # robust: if file has a header, the first row becomes data but that won't break too much
    slab = pd.read_csv(slab_csv, header=None, names=["lon", "lat", "depth"])
    print(f"[load_slab_depth_grid] Loaded {len(slab)} rows from {slab_csv}")

    # convert lon from 0–360 to -180–180
    lon = slab["lon"].to_numpy(dtype=float)
    lon = np.where(lon > 180.0, lon - 360.0, lon)
    slab["lon"] = lon

    depth_raw = slab["depth"].to_numpy(dtype=float)
    depth_pos = -depth_raw  # flip sign: positive downwards
    slab["depth_km"] = depth_pos  # may contain NaN

    print(
        "[load_slab_depth_grid] Depth stats (finite only): "
        f"min={np.nanmin(depth_pos):.1f} km, max={np.nanmax(depth_pos):.1f} km"
    )

    return slab


def assign_depths_from_slab(
    df_ssm: pd.DataFrame,
    rates_matrix: np.ndarray,
    slab_df: pd.DataFrame,
    cfg: PointSourceModelConfig,
) -> pd.DataFrame:
    """
    For each SSM point, find the nearest slab point with finite depth,
    then assign hypocentral depth and seismogenic bounds.

    - slab depths are positive (km, downwards).
    - hypocenter depth = slab_depth + cfg.depth_offset_km
    - usd/lsd depend on hypo depth:
        * hypo <  50 km => ± cfg.half_thickness_0_50
        * 50–90 km     => ± cfg.half_thickness_50_90
        * > 90 km      => ± cfg.half_thickness_90_plus

    Any cell with:
      - no finite slab depth in the whole slab grid, OR
      - all-zero MFD rates
    will later be skipped in PointSource construction.
    """
    if not {"lon", "lat"}.issubset(df_ssm.columns):
        raise ValueError(
            "[assign_depths_from_slab] df_ssm must contain 'lon' and 'lat'."
        )

    # slab finite depths only
    mask_finite = np.isfinite(slab_df["depth_km"].to_numpy(dtype=float))
    if not np.any(mask_finite):
        raise ValueError("[assign_depths_from_slab] No finite depths in slab grid.")

    slab_lon = slab_df["lon"].to_numpy(dtype=float)[mask_finite]
    slab_lat = slab_df["lat"].to_numpy(dtype=float)[mask_finite]
    slab_depth = slab_df["depth_km"].to_numpy(dtype=float)[mask_finite]

    # use a KDTree in lon/lat space for nearest neighbour
    try:
        from scipy.spatial import cKDTree
        use_kdtree = True
    except ImportError:  # pragma: no cover
        print(
            "[assign_depths_from_slab] WARNING: scipy not available; "
            "falling back to slower brute-force nearest neighbour."
        )
        use_kdtree = False

    lon_ssm = df_ssm["lon"].to_numpy(dtype=float)
    lat_ssm = df_ssm["lat"].to_numpy(dtype=float)
    n_cells = len(df_ssm)

    hypo_depth = np.full(n_cells, np.nan, dtype=float)
    usd = np.full(n_cells, np.nan, dtype=float)
    lsd = np.full(n_cells, np.nan, dtype=float)

    if use_kdtree:
        tree = cKDTree(np.column_stack([slab_lon, slab_lat]))
        dist_deg, idx = tree.query(
            np.column_stack([lon_ssm, lat_ssm]), k=1
        )
        # base depth from slab
        base_depth = slab_depth[idx]  # km, positive downwards
    else:
        # brute-force nearest neighbour (slow for large grids)
        base_depth = np.empty(n_cells, dtype=float)
        for i in range(n_cells):
            dlon = slab_lon - lon_ssm[i]
            dlat = slab_lat - lat_ssm[i]
            dist2 = dlon**2 + dlat**2
            k = int(np.argmin(dist2))
            base_depth[i] = slab_depth[k]

    hypo_depth = base_depth + cfg.depth_offset_km  # km

    # assign usd / lsd by depth regime
    for i in range(n_cells):
        d = hypo_depth[i]
        if not np.isfinite(d):
            continue

        if d < 50.0:
            half_thick = cfg.half_thickness_0_50
        elif d < 90.0:
            half_thick = cfg.half_thickness_50_90
        else:
            half_thick = cfg.half_thickness_90_plus

        usd[i] = d - half_thick
        lsd[i] = d + half_thick

    df_out = df_ssm.copy()
    df_out["hypo_depth_km"] = hypo_depth
    df_out["usd_km"] = usd
    df_out["lsd_km"] = lsd

    # basic stats
    finite_mask = np.isfinite(hypo_depth)
    print(
        "[assign_depths_from_slab] Assigned hypocentral depths (finite only): "
        f"min={hypo_depth[finite_mask].min():.1f} km, "
        f"max={hypo_depth[finite_mask].max():.1f} km"
    )

    # also note how many cells have all-zero rates; they will be skipped later
    all_zero_mask = (rates_matrix.sum(axis=1) <= 0.0)
    print(
        "[assign_depths_from_slab] Cells with all-zero MFD rates: "
        f"{all_zero_mask.sum()} / {n_cells}"
    )

    return df_out


def plot_assigned_depths(
    df: pd.DataFrame,
    depth_col: str,
    out_path: Path,
) -> None:
    """
    Quick lon/lat scatter of assigned depths for sanity checking.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not {"lon", "lat", depth_col}.issubset(df.columns):
        raise ValueError(
            f"[plot_assigned_depths] df must contain 'lon', 'lat', and '{depth_col}'."
        )

    lons = df["lon"].to_numpy(dtype=float)
    lats = df["lat"].to_numpy(dtype=float)
    depths = df[depth_col].to_numpy(dtype=float)

    mask = np.isfinite(depths)
    lons = lons[mask]
    lats = lats[mask]
    depths = depths[mask]

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
    cb.set_label(f"{depth_col} (km)")

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"Assigned depths: {depth_col}")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"[plot_assigned_depths] Wrote depth plot to {out_path}")


# ----------------------------------------------------------------------
# PointSource construction
# ----------------------------------------------------------------------

def build_point_sources_from_ssm(
    df_ssm: pd.DataFrame,
    rates_matrix: np.ndarray,
    mag_edges: np.ndarray,
    dM: float,
    cfg: PointSourceModelConfig,
) -> List[PointSource]:
    """
    Build a list of PointSource objects from SSM grid + depths.

    Only cells with:
      - non-zero MFD (at least one positive rate), AND
      - finite hypocentral depth
    are converted to sources.
    """
    if not {"lon", "lat", "hypo_depth_km", "usd_km", "lsd_km"}.issubset(df_ssm.columns):
        raise ValueError(
            "[build_point_sources_from_ssm] df_ssm must contain "
            "'lon', 'lat', 'hypo_depth_km', 'usd_km', 'lsd_km'."
        )

    n_cells, n_bins = rates_matrix.shape
    if len(df_ssm) != n_cells:
        raise ValueError(
            "[build_point_sources_from_ssm] rates_matrix rows must match df_ssm length."
        )
    if len(mag_edges) != n_bins + 1:
        raise ValueError(
            "[build_point_sources_from_ssm] mag_edges length must be n_bins + 1."
        )

    min_mag = float(mag_edges[0])

    # Common attributes
    msr = cfg.msr_class()
    npd_pmf = PMF(cfg.npd_spec)

    sources: List[PointSource] = []
    n_skipped_zero = 0
    n_skipped_depth = 0

    for idx in range(n_cells):
        rates_row = rates_matrix[idx, :]
        if not np.any(rates_row > 0.0):
            n_skipped_zero += 1
            continue

        lon = float(df_ssm.at[idx, "lon"])
        lat = float(df_ssm.at[idx, "lat"])
        depth_hypo = float(df_ssm.at[idx, "hypo_depth_km"])
        usd = float(df_ssm.at[idx, "usd_km"])
        lsd = float(df_ssm.at[idx, "lsd_km"])

        if not np.isfinite(depth_hypo) or not np.isfinite(usd) or not np.isfinite(lsd):
            n_skipped_depth += 1
            continue

        # Hypocenter distribution: single depth with probability 1
        hd_pmf = PMF([(1.0, depth_hypo)])

        # Evenly discretized MFD
        mfd = EvenlyDiscretizedMFD(
            min_mag=min_mag,
            bin_width=dM,
            occurrence_rates=rates_row.tolist(),
        )

        source_id = f"ps_{len(sources):05d}"
        name = f"ps_{len(sources):05d}"

        src = PointSource(
            source_id=source_id,
            name=name,
            tectonic_region_type=cfg.tectonic_region_type,
            mfd=mfd,
            rupture_mesh_spacing=cfg.rupture_mesh_spacing,
            magnitude_scaling_relationship=msr,
            rupture_aspect_ratio=cfg.rupture_aspect_ratio,
            temporal_occurrence_model=PoissonTOM(cfg.investigation_time_yr),
            upper_seismogenic_depth=usd,
            lower_seismogenic_depth=lsd,
            location=Point(lon, lat),
            nodal_plane_distribution=npd_pmf,
            hypocenter_distribution=hd_pmf,
        )

        sources.append(src)

    print(f"[build_point_sources_from_ssm] Built {len(sources)} PointSource objects.")
    print(f"  Skipped cells with all-zero MFD: {n_skipped_zero}")
    print(f"  Skipped cells with invalid depths: {n_skipped_depth}")

    return sources

def check_mfd_consistency(
    rates_matrix: np.ndarray,
    mag_edges: np.ndarray,
    sources: list[PointSource],
    *,
    rtol: float = 1e-10,
) -> None:
    """
    Quick consistency check between SSM MFD (rates_matrix) and
    the MFDs stored in the PointSource objects.

    Assumes:
      - rates_matrix shape = (n_cells, n_bins)
      - each PointSource has an EvenlyDiscretizedMFD with
        the same min_mag, bin_width and number of bins
        as implied by mag_edges.

    Prints:
      - global total rate from SSM vs from PointSources
      - per-bin max absolute and relative differences.
    """
    if rates_matrix.ndim != 2:
        raise ValueError("[check_mfd_consistency] rates_matrix must be 2D.")
    n_cells, n_bins = rates_matrix.shape

    if len(mag_edges) != n_bins + 1:
        raise ValueError(
            "[check_mfd_consistency] mag_edges length must be n_bins + 1."
        )

    # --- 1. SSM totals per bin ---
    ssm_bin_totals = rates_matrix.sum(axis=0)  # shape (n_bins,)
    ssm_global = float(ssm_bin_totals.sum())

    # --- 2. PointSource totals per bin ---
    ps_bin_totals = np.zeros_like(ssm_bin_totals, dtype=float)

    for src in sources:
        mfd = src.mfd
        # EvenlyDiscretizedMFD: occurrence_rates is a flat list
        rates = np.asarray(mfd.occurrence_rates, dtype=float)
        if rates.size != n_bins:
            raise ValueError(
                "[check_mfd_consistency] MFD bin count mismatch: "
                f"{rates.size} (PointSource) vs {n_bins} (SSM)."
            )
        ps_bin_totals += rates

    ps_global = float(ps_bin_totals.sum())

    # --- 3. Differences ---
    abs_diff_bins = ps_bin_totals - ssm_bin_totals
    # avoid division by zero in relative diff
    denom = np.where(ssm_bin_totals != 0.0, ssm_bin_totals, 1.0)
    rel_diff_bins = abs_diff_bins / denom

    max_abs_diff = float(np.max(np.abs(abs_diff_bins)))
    max_rel_diff = float(np.max(np.abs(rel_diff_bins)))

    print("[check_mfd_consistency] Global MFD consistency check:")
    print(f"  SSM total rate (sum over all bins)   = {ssm_global:.6e} /yr")
    print(f"  PS total rate  (sum over all sources) = {ps_global:.6e} /yr")
    if ssm_global != 0.0:
        rel_global = (ps_global - ssm_global) / ssm_global
    else:
        rel_global = np.nan
    print(f"  Global relative difference           = {rel_global:.3e}")

    print("[check_mfd_consistency] Per-bin differences:")
    print(f"  max |abs_diff| = {max_abs_diff:.6e} /yr")
    print(f"  max |rel_diff| = {max_rel_diff:.3e}")

    if np.allclose(ps_bin_totals, ssm_bin_totals, rtol=rtol, atol=0.0):
        print(f"[check_mfd_consistency] PASS: PointSource MFDs match SSM within rtol={rtol}.")
    else:
        print(f"[check_mfd_consistency] WARNING: MFD mismatch exceeds rtol={rtol}.")

def create_point_source_model(
    ssm_mfd_csv: Path,
    slab_depth_csv: Path,
    xml_out: Path,
    depth_plot_png: Path,
    cfg: PointSourceModelConfig | None = None,
) -> List[PointSource]:
    """
    High-level driver:

      - read SSM MFD grid
      - read slab depth grid
      - assign hypocentral depths and usd/lsd to SSM points
      - make a depth sanity plot
      - build PointSource objects
      - write NRML source model

    Returns
    -------
    sources : list[PointSource]
        The list of constructed sources (for further inspection if desired).
    """
    if cfg is None:
        cfg = PointSourceModelConfig()

    ssm_mfd_csv = Path(ssm_mfd_csv)
    slab_depth_csv = Path(slab_depth_csv)
    xml_out = Path(xml_out)
    depth_plot_png = Path(depth_plot_png)

    # 1) SSM MFD grid
    df_ssm, rates_matrix, mag_edges, dM = load_ssm_mfd_grid(ssm_mfd_csv)
    # 2) Slab grid
    slab_df = load_slab_depth_grid(slab_depth_csv)

    # 3) Assign depths & seismogenic bounds
    df_ssm_depth = assign_depths_from_slab(df_ssm, rates_matrix, slab_df, cfg)

    # 4) Plot depths (always, as per request)
    plot_assigned_depths(df_ssm_depth, "hypo_depth_km", depth_plot_png)

    # 5) Build PointSources
    sources = build_point_sources_from_ssm(
        df_ssm_depth, rates_matrix, mag_edges, dM, cfg
    )
    # 5b) Quick MFD consistency check
    check_mfd_consistency(
        rates_matrix=rates_matrix,
        mag_edges=mag_edges,
        sources=sources,
    )

    # 6) Write NRML source model
    xml_out.parent.mkdir(parents=True, exist_ok=True)
    sourcewriter.write_source_model(
        dest=str(xml_out),
        sources_or_groups=sources,
        name="SSM point-source model",
        investigation_time=cfg.investigation_time_yr,
    )
    print(f"[create_point_source_model] Wrote point-source model to {xml_out}")

    return sources


# ----------------------------------------------------------------------
# Simple CLI example (adapt paths as needed)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    from cat_no_mech_handler import paths as cat_paths

    cfg = PointSourceModelConfig()

    # Path to the SSM grid with MFDs you wrote with write_ssm_mfd_csv
    ssm_csv = Path("ssm_outputs/ssm_mfd_grid.csv")

    slab_csv = cat_paths.slab_depth
    xml_out = Path("ssm_outputs/ssm_point_sources.xml")
    depth_png = Path("ssm_outputs/ssm_point_depths.png")

    create_point_source_model(
        ssm_mfd_csv=ssm_csv,
        slab_depth_csv=slab_csv,
        xml_out=xml_out,
        depth_plot_png=depth_png,
        cfg=cfg,
    )

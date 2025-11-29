# config.py
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from subduction.paths import paths


@dataclass
class SegmentConfig:
    """
    Latitude extent for one along-strike subduction segment.

    Notes
    -----
    - lat_min, lat_max are in decimal degrees.
    - Use None for lat_min / lat_max to span the full slab extent.
    """
    segment_id: str
    lat_min: Optional[float] = None
    lat_max: Optional[float] = None
    description: str = ""


@dataclass
class GeometryConfig:
    """Configuration for building subduction interface geometry."""
    # NEW: ID for the *global* locked interface geometry
    geometry_id: str = "locked_interface_main"

    slab_csv: Path = paths.slab_depth
    output_dir: Path = Path("out") / "geometry"
    z_top_locked: float = 5.0
    z_bottom_locked: float = 50.0
    depth_step_km: float = 5.0
    lat_step_deg: float = 0.5
    min_points_per_edge: int = 3
    segments: List[SegmentConfig] = field(
        default_factory=lambda: [
            SegmentConfig(
                segment_id="seg0_full",
                lat_min=-45.6,
                lat_max=-17.6,
                description="Full locked interface (no segmentation)",
            )
        ]
    )


GEOMETRY_CONFIG = GeometryConfig()



# ---------------------------------------------------------------------------
# Kijko–Smit a–b configuration
# ---------------------------------------------------------------------------

@dataclass
class ABConfig:
    """
    Configuration for Kijko–Smit a–b estimation.

    Parameters
    ----------
    catalog_path
        Path to declustered slab-interface catalog.
    mc_summary_path
        Path to MC summary table (Mc, start_iso, etc.).
    output_dir
        Directory where plots and JSON will be written.
    hazard_mref
        Reference minimum magnitude for hazard (Mmin_hazard >= hazard_mref).
    delta_m
        Magnitude bin width for KS + MFD.
    segments
        Latitude-based segments. Use lat_min/lat_max=None for full patch.
    max_depth_km
        If not None, filter catalog to depth <= max_depth_km using
        the given depth_column.
    depth_column
        Name of the depth column in km. For your catalog: "depth".
    """
    catalog_path: Path = paths.catalog
    mc_summary_path: Path = paths.MC_SUMMARY
    output_dir: Path = Path("ab_calc")

    hazard_mref: float = 6.0
    delta_m: float = 0.1

    segments: List[SegmentConfig] = field(
        default_factory=lambda: [
            SegmentConfig(
                segment_id="seg0_full",
                lat_min=None,
                lat_max=None,
                description="Full interface (no segmentation)",
            )
        ]
    )
    mfd_period_count: int = 8
    # Will be wired to GEOMETRY_CONFIG.z_bottom_locked below
    max_depth_km: Optional[float] = None
    # Will be set to "depth" below
    depth_column: Optional[str] = None


AB_CONFIG = ABConfig()

# Wire depth filtering to geometry config:
#   - use locked bottom depth as max_depth_km
#   - use catalog column "depth"
AB_CONFIG.max_depth_km = GEOMETRY_CONFIG.z_bottom_locked
AB_CONFIG.depth_column = "depth"

# ---------------------------------------------------------------------------
# Subduction source model configuration (ComplexFaultSource / NRML)
# ---------------------------------------------------------------------------

@dataclass
class SourceModelConfig:
    """
    Configuration for building the subduction interface source model
    (ComplexFaultSource objects for OpenQuake).

    geometry_json
        Path to the global locked-interface geometry JSON produced by
        geometry.build_geometry_from_config(GEOMETRY_CONFIG).

    ab_json
        Path to the a–b JSON produced by ab_kijko.run_ab_from_config(AB_CONFIG).

    output_nrml
        Path to the NRML source model XML to be written (if you call
        write_source_model in __main__ of source_model.py).

    The other parameters control rupture discretisation and MFD details.
    """
    # Default: geometry builder writes:
    #   GEOMETRY_CONFIG.output_dir / f"{GEOMETRY_CONFIG.geometry_id}_geometry.json"
    geometry_json: Path = GEOMETRY_CONFIG.output_dir / f"{GEOMETRY_CONFIG.geometry_id}_geometry.json"

    # Default: a–b code writes:
    #   AB_CONFIG.output_dir / "subduction_ab_results.json"
    ab_json: Path = AB_CONFIG.output_dir / "subduction_ab_results.json"

    # Optional NRML output file (used only in source_model.__main__)
    output_nrml: Path = Path("subduction_interface_sources.xml")

    # Rupture geometry parameters
    rupture_mesh_spacing: float = 5.0
    rupture_aspect_ratio: float = 1.0
    rake: float = 90.0  # pure thrust

    # Time span (years) for PoissonTOM; rates are per year already
    investigation_time: float = 1.0

    # Source IDs will look like "i00", "i01", ...
    source_id_prefix: str = "i"

    # MFD parameters
    max_mag_default: float = 9.6
    bin_width: float = 0.1
    segments_shapefile: Optional[Path] = Path("subduction_segments.shp")

SOURCE_CONFIG = SourceModelConfig()

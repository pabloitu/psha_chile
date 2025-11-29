"""
Build subduction interface ComplexFaultSource objects for OpenQuake.

This module:
- reads global interface geometry (edges) from JSON,
- reads a–b results per segment from the Kijko–Taroni JSON,
- slices the global geometry by lat_min/lat_max for each segment,
- constructs a TruncatedGRMFD per segment,
- instantiates ComplexFaultSource objects suitable for OpenQuake.

Configuration:
    - All paths and parameters come from SOURCE_CONFIG in subduction.config.

Usage:
    - import `build_subduction_interface_sources` from other code, or
    - run this module as a script to produce an NRML source model XML.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import json

from openquake.hazardlib.geo.line import Line
from openquake.hazardlib.geo.point import Point
from openquake.hazardlib.mfd.truncated_gr import TruncatedGRMFD
from openquake.hazardlib.source.complex_fault import ComplexFaultSource
from openquake.hazardlib.tom import PoissonTOM
from openquake.hazardlib.scalerel.strasser2010 import StrasserInterface
from openquake.hazardlib.sourcewriter import write_source_model

from subduction.config_seg import SOURCE_CONFIG, SourceModelConfig


TECTONIC_REGION_TYPE = "Subduction Interface"


# ---------------------------------------------------------------------------
# DATA CLASS FOR SEGMENT MFD + LAT RANGE
# ---------------------------------------------------------------------------

@dataclass
class SegmentMFDConfig:
    name: str
    a: float
    b: float
    mmin_hazard: float
    max_mag: float
    bin_width: float
    lat_min: Optional[float] = None
    lat_max: Optional[float] = None


# ---------------------------------------------------------------------------
# HELPERS: GEOMETRY
# ---------------------------------------------------------------------------

def _parse_single_geometry_object(obj: dict) -> List[Line]:
    """
    Parse a global geometry JSON object of the form:

    {
      "geometry_id": "locked_interface_main",
      "name": "locked_interface_main",
      "lat_min": ...,
      "lat_max": ...,
      "locked_depth_range_km": [...],
      "depth_levels_km": [...],
      "edges": [
        {
          "edge_index": 0,
          "edge_type": "top",
          "depth_km": 10.0,
          "nodes": [
            {"lon": ..., "lat": ..., "depth_km": ...},
            ...
          ]
        },
        ...
      ],
      ...
    }

    Returns:
        [Line(...), Line(...), ...] ordered top -> bottom by edge_index.
    """
    edges_json = obj["edges"]

    # Sort edges by edge_index (or depth_km as fallback)
    edges_json_sorted = sorted(
        edges_json,
        key=lambda e: e.get("edge_index", e.get("depth_km", 0.0)),
    )

    edges_lines: List[Line] = []
    for e in edges_json_sorted:
        nodes = e["nodes"]
        pts = [
            Point(float(p["lon"]), float(p["lat"]), float(p["depth_km"]))
            for p in nodes
        ]
        edges_lines.append(Line(pts))

    return edges_lines


def load_global_geometry(path: Path) -> List[Line]:
    """
    Load the *global* locked-interface geometry from JSON and return
    the list of edges as Line objects (top -> bottom).

    Currently we assume the geometry JSON is a single object as produced
    by geometry.build_geometry_from_config(GEOMETRY_CONFIG).
    """
    with path.open("r") as f:
        data = json.load(f)

    if "edges" not in data:
        raise ValueError(
            f"Geometry JSON {path} does not contain 'edges' "
            "in the expected format."
        )

    return _parse_single_geometry_object(data)


def slice_edges_by_lat(
    edges: List[Line],
    lat_min: Optional[float],
    lat_max: Optional[float],
    tol: float = 1e-6,
) -> List[Line]:
    """
    Slice a list of edges (Lines) by latitude into a segment window.

    - If lat_min / lat_max are None, the full edge is returned.
    - Otherwise we keep only nodes with lat_min <= lat <= lat_max (±tol).
    - If fewer than 2 points remain on an edge, that edge is dropped.

    NOTE
    ----
    This keeps the existing node positions. If the segment boundary does
    not coincide exactly with a node latitude, the cut will happen at the
    nearest available node. This is usually fine for hazard modeling, but
    if you ever need exact shared nodes at the boundary, we could add
    interpolation on the Line later.
    """
    if lat_min is None and lat_max is None:
        return edges  # no slicing needed

    seg_edges: List[Line] = []

    for line in edges:
        pts_segment: List[Point] = []
        for p in line.points:
            lat = p.latitude
            if lat_min is not None and lat < lat_min - tol:
                continue
            if lat_max is not None and lat > lat_max + tol:
                continue
            pts_segment.append(p)

        if len(pts_segment) >= 2:
            seg_edges.append(Line(pts_segment))

    return seg_edges


# ---------------------------------------------------------------------------
# HELPERS: LOAD a–b JSON
# ---------------------------------------------------------------------------

def load_ab_segments(
    ab_json: Path,
    max_mag_default: float,
    bin_width: float,
) -> Dict[str, SegmentMFDConfig]:
    """
    Load a–b / hazard parameters per segment from the JSON produced by
    ab_kijko.run_ab_from_config, and convert to SegmentMFDConfig objects.

    Expected JSON structure (flattened KS/Taroni fields), e.g.:

    {
      "segments": [
        {
          "name": "seg1_south",
          "lat_min": -46.0,
          "lat_max": -30.0,
          "a": 5.0514,
          "b": 0.8388,
          "std_b": ...,
          "mc0": 4.4,
          "year0": 1513,
          "rate_at_mc0": 22.95,
          "last_year": 2022,
          "T_eff": 509.0,
          "delta_m": 0.1,
          "ncomplete": 1104,
          "hazard_params": {
            "Mmin_hazard": 6.0,
            "lambda_Mmin": 1.04,
            ...
          }
        },
        ...
      ]
    }

    Returns:
        dict[name] -> SegmentMFDConfig (including lat_min/lat_max).
    """
    with ab_json.open("r") as f:
        data = json.load(f)

    seg_configs: Dict[str, SegmentMFDConfig] = {}

    for s in data["segments"]:
        name = s["name"]
        a = float(s["a"])
        b = float(s["b"])
        lat_min = s.get("lat_min")
        lat_max = s.get("lat_max")

        haz = s.get("hazard_params", {})
        mmin_hazard = float(haz.get("Mmin_hazard", s.get("mc0", 6.0)))

        seg_configs[name] = SegmentMFDConfig(
            name=name,
            a=a,
            b=b,
            mmin_hazard=mmin_hazard,
            max_mag=max_mag_default,
            bin_width=bin_width,
            lat_min=lat_min,
            lat_max=lat_max,
        )

    return seg_configs


def build_truncated_gr_mfd(seg_cfg: SegmentMFDConfig) -> TruncatedGRMFD:
    """
    Build a TruncatedGRMFD for a given segment using its a, b, and Mmin_hazard.
    """
    mfd = TruncatedGRMFD(
        min_mag=seg_cfg.mmin_hazard,
        max_mag=seg_cfg.max_mag,
        bin_width=seg_cfg.bin_width,
        a_val=seg_cfg.a,
        b_val=seg_cfg.b,
    )
    return mfd


# ---------------------------------------------------------------------------
# MAIN BUILDER
# ---------------------------------------------------------------------------

def build_subduction_interface_sources(
    cfg: SourceModelConfig | None = None,
) -> Dict[str, ComplexFaultSource]:
    """
    Build one ComplexFaultSource per segment, using:

      - global geometry from cfg.geometry_json,
      - per-segment a–b values & lat ranges from cfg.ab_json,
      - TruncatedGRMFD with (a, b, Mmin_hazard, max_mag_default),
      - StrasserInterface MSR,
      - PoissonTOM(investigation_time).

    Returns:
        dict[name] -> ComplexFaultSource

    Works for:
      - single segment ("seg0_full" with lat_min=lat_max=None), and
      - multiple along-strike segments (each with lat_min / lat_max).
    """
    if cfg is None:
        cfg = SOURCE_CONFIG

    # 1) Load global geometry and a–b configs
    global_edges = load_global_geometry(cfg.geometry_json)
    seg_mfd_configs = load_ab_segments(
        cfg.ab_json, max_mag_default=cfg.max_mag_default, bin_width=cfg.bin_width
    )

    print(f"[SOURCE] Loaded global geometry from {cfg.geometry_json}")
    print(f"[SOURCE] Loaded {len(seg_mfd_configs)} a–b segments from {cfg.ab_json}")

    # 2) Build ComplexFaultSource per segment
    sources: Dict[str, ComplexFaultSource] = {}
    msr = StrasserInterface()

    for idx, (name, seg_cfg) in enumerate(sorted(seg_mfd_configs.items())):
        seg_edges = slice_edges_by_lat(
            global_edges,
            lat_min=seg_cfg.lat_min,
            lat_max=seg_cfg.lat_max,
        )

        if not seg_edges:
            raise RuntimeError(
                f"No geometry edges found for segment '{name}' "
                f"(lat_min={seg_cfg.lat_min}, lat_max={seg_cfg.lat_max}). "
                f"Check that geometry and segment ranges overlap."
            )

        lats_all = [p.latitude for edge in seg_edges for p in edge.points]
        print(
            f"[SOURCE] Segment '{name}': "
            f"{len(seg_edges)} edges, "
            f"lat range in geometry = [{min(lats_all):.2f}, {max(lats_all):.2f}]"
        )
        if seg_cfg.lat_min is not None or seg_cfg.lat_max is not None:
            print(
                f"          requested lat window = "
                f"[{seg_cfg.lat_min}, {seg_cfg.lat_max}]"
            )

        # MFD & TOM
        mfd = build_truncated_gr_mfd(seg_cfg)
        tom = PoissonTOM(cfg.investigation_time)

        # Build source_id and name, e.g. i00, i01, ...
        source_id = f"{cfg.source_id_prefix}{idx:02d}"
        src_name = f"Interface {name}"

        src = ComplexFaultSource(
            source_id=source_id,
            name=src_name,
            tectonic_region_type=TECTONIC_REGION_TYPE,
            mfd=mfd,
            rupture_mesh_spacing=cfg.rupture_mesh_spacing,
            magnitude_scaling_relationship=msr,
            rupture_aspect_ratio=cfg.rupture_aspect_ratio,
            temporal_occurrence_model=tom,
            edges=seg_edges,
            rake=cfg.rake,
        )

        sources[name] = src

    return sources


# ---------------------------------------------------------------------------
# SCRIPT ENTRY POINT (optional NRML writer)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """
    Example usage:

    - Build complex-fault sources
    - Write a single NRML source model file

    Configuration is taken from SOURCE_CONFIG in subduction.config.
    """
    cfg = SOURCE_CONFIG
    sources_by_name = build_subduction_interface_sources(cfg)

    sources_list = list(sources_by_name.values())
    write_source_model(
        dest=str(cfg.output_nrml),
        sources_or_groups=sources_list,
        name="Subduction interface complex-fault model",
        investigation_time=cfg.investigation_time,
    )

    print(
        f"Wrote {len(sources_list)} ComplexFaultSource objects "
        f"to {cfg.output_nrml}"
    )

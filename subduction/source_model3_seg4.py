"""
Build subduction interface ComplexFaultSource objects for OpenQuake.

This module:
- reads global interface geometry (edges) from JSON,
- reads a–b results per segment from the Kijko–Taroni JSON,
- slices the global geometry by lat_min/lat_max for each segment,
- constructs a TruncatedGRMFD per segment,
- instantiates ComplexFaultSource objects suitable for OpenQuake,
- (optionally) writes a shapefile with one polygon per segment.

Configuration:
    - All paths and parameters come from SOURCE_CONFIG in subduction.config_seg.

Usage:
    - import `build_subduction_interface_sources` from other code, or
    - run this module as a script to produce an NRML source model XML.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

def _interpolate_point_at_lat(p0: Point, p1: Point, target_lat: float) -> Optional[Point]:
    """
    Interpolate a new Point between p0 and p1 at a given target latitude.

    Assumes lat varies approximately linearly between p0 and p1
    (which is fine for our small edge segments).
    """
    lat0, lat1 = p0.latitude, p1.latitude
    if lat0 == lat1:
        return None

    # Check if target_lat lies strictly between lat0 and lat1
    if not (min(lat0, lat1) < target_lat < max(lat0, lat1)):
        return None

    t = (target_lat - lat0) / (lat1 - lat0)

    lon = p0.longitude + t * (p1.longitude - p0.longitude)
    depth = p0.depth + t * (p1.depth - p0.depth)

    return Point(lon, target_lat, depth)


def refine_edges_with_lat_boundaries(
    edges: List[Line],
    boundaries: List[float],
    tol: float = 1e-6,
) -> List[Line]:
    """
    Refine edges by inserting intersection nodes at each segment boundary latitude.

    After this step, slicing by lat_min/lat_max using simple >=/<=
    will not drop any piece of the original edge between segments:
    segments will be strictly adjacent (sharing their boundary line).
    """
    # Filter and sort unique boundaries
    boundaries = sorted({b for b in boundaries if b is not None})
    if not boundaries:
        return edges

    refined_edges: List[Line] = []

    for line in edges:
        # Work on a sorted copy (south -> north)
        pts = list(line.points)
        pts.sort(key=lambda p: p.latitude)

        new_pts: List[Point] = [pts[0]]

        for i in range(len(pts) - 1):
            p0 = pts[i]
            p1 = pts[i + 1]
            lat0, lat1 = p0.latitude, p1.latitude

            # Insert intersection points for all boundaries strictly between p0 and p1
            for b in boundaries:
                # Skip if boundary is (almost) at endpoints; existing nodes are fine
                if abs(b - lat0) <= tol or abs(b - lat1) <= tol:
                    continue

                # Insert only if boundary is strictly between lat0 and lat1
                if (lat0 < b < lat1) or (lat1 < b < lat0):
                    p_int = _interpolate_point_at_lat(p0, p1, b)
                    if p_int is not None:
                        new_pts.append(p_int)

            new_pts.append(p1)

        # Re-sort by latitude and de-duplicate near-identical points
        new_pts.sort(key=lambda p: p.latitude)

        dedup_pts: List[Point] = [new_pts[0]]
        for p in new_pts[1:]:
            last = dedup_pts[-1]
            if (
                abs(p.latitude - last.latitude) > tol
                or abs(p.longitude - last.longitude) > tol
                or abs((p.depth or 0.0) - (last.depth or 0.0)) > tol
            ):
                dedup_pts.append(p)

        refined_edges.append(Line(dedup_pts))

    return refined_edges

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
          ...
          "hazard_params": {"Mmin_hazard": 6.0, ...}
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
# NEW: BUILD POLYGON FROM TOP + BOTTOM EDGE
# ---------------------------------------------------------------------------

def build_segment_polygon_from_edges(seg_edges: List[Line]) -> List[Tuple[float, float]]:
    """
    Build a simple surface polygon for a segment from its edges:

      - use the shallowest edge as "top" (seg_edges[0]),
      - use the deepest edge as "bottom" (seg_edges[-1]),
      - connect top S->N, then bottom N->S, and close the ring.

    Returns:
        List of (lon, lat) coordinates forming a closed polygon ring.
    """
    if len(seg_edges) < 2:
        raise ValueError("Need at least two edges (top and bottom) to build a polygon.")

    top_pts = sorted(seg_edges[0].points, key=lambda p: p.latitude)
    bottom_pts = sorted(seg_edges[-1].points, key=lambda p: p.latitude)

    coords: List[Tuple[float, float]] = []

    # Top edge: south -> north
    for p in top_pts:
        coords.append((p.longitude, p.latitude))

    # Bottom edge: north -> south
    for p in reversed(bottom_pts):
        coords.append((p.longitude, p.latitude))

    # Close polygon
    if coords[0] != coords[-1]:
        coords.append(coords[0])

    return coords


def write_segments_shapefile(
    path: Path,
    polygons: Dict[str, List[Tuple[float, float]]],
    seg_cfgs: Dict[str, SegmentMFDConfig],
) -> None:
    """
    Write one polygon per segment to a shapefile.

    Attributes per polygon:
      - name
      - a, b
      - Mmin (hazard mmin)
      - Mmax (max_mag)
      - lat_min, lat_max (from a–b config)
    """
    try:
        import shapefile  # pyshp
    except ImportError as exc:
        raise ImportError(
            "The 'shapefile' package (pyshp) is required to write segments shapefile. "
            "Install it with 'pip install pyshp'."
        ) from exc

    path.parent.mkdir(parents=True, exist_ok=True)

    # shapefile.Writer wants a base filename without extension, but passing
    # "foo.shp" is fine; it will create .shp/.shx/.dbf alongside.
    w = shapefile.Writer(str(path), shapeType=shapefile.POLYGON)

    w.field("name", "C", size=64)
    w.field("a", "F", decimal=6)
    w.field("b", "F", decimal=6)
    w.field("Mmin", "F", decimal=3)
    w.field("Mmax", "F", decimal=3)
    w.field("lat_min", "F", decimal=3)
    w.field("lat_max", "F", decimal=3)

    for name, coords in polygons.items():
        cfg = seg_cfgs[name]

        # pyshp expects [ [ (x,y), ... ] ] for polygon(s)
        w.poly([coords])

        lat_min = cfg.lat_min if cfg.lat_min is not None else -999.0
        lat_max = cfg.lat_max if cfg.lat_max is not None else 999.0

        w.record(
            name,
            cfg.a,
            cfg.b,
            cfg.mmin_hazard,
            cfg.max_mag,
            lat_min,
            lat_max,
        )

    w.close()
    print(f"[SOURCE] Wrote segments shapefile to {path}")


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

    Also (optionally) builds a shapefile with one polygon per segment.

    Returns:
        dict[name] -> ComplexFaultSource
    """
    if cfg is None:
        cfg = SOURCE_CONFIG

    # 1) Load global geometry and a–b configs
    global_edges = load_global_geometry(cfg.geometry_json)
    seg_mfd_configs = load_ab_segments(
        cfg.ab_json, max_mag_default=cfg.max_mag_default, bin_width=cfg.bin_width
    )
    # >>> NEW: collect all lat boundaries and refine edges <<<
    lat_boundaries: List[float] = []
    for seg_cfg in seg_mfd_configs.values():
        if seg_cfg.lat_min is not None:
            lat_boundaries.append(seg_cfg.lat_min)
        if seg_cfg.lat_max is not None:
            lat_boundaries.append(seg_cfg.lat_max)

    refined_edges = refine_edges_with_lat_boundaries(global_edges, lat_boundaries)

    print(f"[SOURCE] Loaded global geometry from {cfg.geometry_json}")
    print(f"[SOURCE] Loaded {len(seg_mfd_configs)} a–b segments from {cfg.ab_json}")

    # 2) Build ComplexFaultSource per segment
    sources: Dict[str, ComplexFaultSource] = {}
    segment_polygons: Dict[str, List[Tuple[float, float]]] = {}
    msr = StrasserInterface()

    for idx, (name, seg_cfg) in enumerate(sorted(seg_mfd_configs.items())):cfg = SOURCE_CONFIG

    # 1) Load global geometry and a–b configs
    global_edges = load_global_geometry(cfg.geometry_json)
    seg_mfd_configs = load_ab_segments(
        cfg.ab_json, max_mag_default=cfg.max_mag_default, bin_width=cfg.bin_width
    )

    print(f"[SOURCE] Loaded global geometry from {cfg.geometry_json}")
    print(f"[SOURCE] Loaded {len(seg_mfd_configs)} a–b segments from {cfg.ab_json}")

    # >>> NEW: collect all lat boundaries and refine edges <<<
    lat_boundaries: List[float] = []
    for seg_cfg in seg_mfd_configs.values():
        if seg_cfg.lat_min is not None:
            lat_boundaries.append(seg_cfg.lat_min)
        if seg_cfg.lat_max is not None:
            lat_boundaries.append(seg_cfg.lat_max)

    refined_edges = refine_edges_with_lat_boundaries(global_edges, lat_boundaries)

    # 2) Build ComplexFaultSource per segment
    sources: Dict[str, ComplexFaultSource] = {}
    segment_polygons: Dict[str, List[Tuple[float, float]]] = {}
    msr = StrasserInterface()

    for idx, (name, seg_cfg) in enumerate(sorted(seg_mfd_configs.items())):
        seg_edges = slice_edges_by_lat(
            refined_edges,
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

        # Build polygon for this segment (surface projection)
        try:
            poly_coords = build_segment_polygon_from_edges(seg_edges)
            segment_polygons[name] = poly_coords
        except Exception as exc:  # noqa: BLE001
            # Don't kill the whole build if polygon creation fails;
            # just warn. If you want it strict, re-raise instead.
            print(f"[SOURCE] WARNING: could not build polygon for segment '{name}': {exc}")

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

    # 3) Optional: write segments shapefile
    if cfg.segments_shapefile is not None and segment_polygons:
        write_segments_shapefile(
            cfg.segments_shapefile,
            polygons=segment_polygons,
            seg_cfgs=seg_mfd_configs,
        )

    return sources


# ---------------------------------------------------------------------------
# SCRIPT ENTRY POINT (optional NRML writer)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """
    Example usage:

    - Build complex-fault sources
    - Write a single NRML source model file

    Configuration is taken from SOURCE_CONFIG in subduction.config_seg.
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

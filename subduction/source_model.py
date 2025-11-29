"""
Build subduction interface ComplexFaultSource objects for OpenQuake.

This module:
- reads interface geometry (edges) from JSON,
- reads a–b results from the Kijko–Smit JSON,
- constructs a TruncatedGRMFD per segment,
- instantiates ComplexFaultSource objects suitable for OpenQuake.

You can:
- import `build_subduction_interface_sources` from other code, or
- run this module as a script to produce an NRML source model XML.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import json

from openquake.hazardlib.const import TRT
from openquake.hazardlib.geo.line import Line
from openquake.hazardlib.geo.point import Point
from openquake.hazardlib.mfd.truncated_gr import TruncatedGRMFD
from openquake.hazardlib.source.complex_fault import ComplexFaultSource
from openquake.hazardlib.tom import PoissonTOM
from openquake.hazardlib.scalerel.strasser2010 import StrasserInterface
from openquake.hazardlib.sourcewriter import write_source_model


# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

# Paths – adjust to your project structure
GEOMETRY_JSON = Path("./out/subduction_interface_segment_01.json")
AB_JSON = Path("./subduction_ab_results/subduction_ab_results.json")

# Default modeling parameters
DEFAULT_MAX_MAG = 9.6          # as in your example XML
DEFAULT_BIN_WIDTH = 0.1
DEFAULT_RUPTURE_MESH_SPACING = 20.0  # km (can tweak later)
DEFAULT_RUPTURE_ASPECT_RATIO = 1.0
DEFAULT_RAKE = 90.0            # pure thrust
DEFAULT_INVESTIGATION_TIME = 1.0  # years, PoissonTOM time span
DEFAULT_SOURCE_ID_PREFIX = "i"    # e.g. i01, i02, ...

TECTONIC_REGION_TYPE = "Subduction Interface"


# ---------------------------------------------------------------------------
# DATA CLASSES FOR CONFIG
# ---------------------------------------------------------------------------

@dataclass
class SegmentMFDConfig:
    name: str
    a: float
    b: float
    mmin_hazard: float
    max_mag: float
    bin_width: float


@dataclass
class SubductionSourceConfig:
    geometry_json: Path = GEOMETRY_JSON
    ab_json: Path = AB_JSON
    rupture_mesh_spacing: float = DEFAULT_RUPTURE_MESH_SPACING
    rupture_aspect_ratio: float = DEFAULT_RUPTURE_ASPECT_RATIO
    rake: float = DEFAULT_RAKE
    investigation_time: float = DEFAULT_INVESTIGATION_TIME
    source_id_prefix: str = DEFAULT_SOURCE_ID_PREFIX
    max_mag_default: float = DEFAULT_MAX_MAG
    bin_width: float = DEFAULT_BIN_WIDTH


# ---------------------------------------------------------------------------
# HELPERS: LOAD GEOMETRY
# ---------------------------------------------------------------------------

def _parse_single_segment_object(seg_obj: dict) -> tuple[str, List[Line]]:
    """
    Parse a single segment JSON object of the form you showed:

    {
      "segment_id": "segment_01",
      "lat_min": ...,
      "lat_max": ...,
      "lat_max_locked": ...,
      "locked_depth_range_km": [...],
      "depth_levels_km": [...],
      "lat_step_deg_approx": ...,
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
      "metadata": {...}
    }

    Returns:
        (segment_id, [Line(...), Line(...), ...]) where
        lines are ordered top -> bottom by edge_index.
    """
    seg_id = seg_obj.get("segment_id") or seg_obj.get("name")
    if seg_id is None:
        raise ValueError("Segment JSON must have 'segment_id' or 'name'")

    edges_json = seg_obj["edges"]

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

    return seg_id, edges_lines


def load_geometry_segments(path: Path) -> Dict[str, List[Line]]:
    """
    Load geometry segments from JSON.

    Supports three layouts:

    1) A directory with multiple segment files:
         path/segment_01.json, path/segment_02.json, ...
       Each file has the structure you showed (segment_id, edges, ...).

    2) A single file with a single segment object (as you pasted).

    3) A single file with:
         { "segments": [ {segment_obj}, {segment_obj}, ... ] }

    Returns:
        dict[segment_id] -> list of Line objects (edges top->bottom).
    """
    segments_edges: Dict[str, List[Line]] = {}

    if path.is_dir():
        # Case 1: directory of segment_XX.json files
        for p in sorted(path.glob("*.json")):
            with p.open("r") as f:
                data = json.load(f)

            if "segments" in data:
                # nested multi-segment file inside directory (rare, but supported)
                for seg_obj in data["segments"]:
                    seg_id, lines = _parse_single_segment_object(seg_obj)
                    if seg_id in segments_edges:
                        raise ValueError(
                            f"Duplicate segment_id '{seg_id}' across files"
                        )
                    segments_edges[seg_id] = lines
            else:
                # single segment per file (your current use case)
                seg_id, lines = _parse_single_segment_object(data)
                if seg_id in segments_edges:
                    raise ValueError(
                        f"Duplicate segment_id '{seg_id}' across files"
                    )
                segments_edges[seg_id] = lines

    else:
        # Case 2 or 3: single JSON file
        with path.open("r") as f:
            data = json.load(f)

        if "segments" in data:
            for seg_obj in data["segments"]:
                seg_id, lines = _parse_single_segment_object(seg_obj)
                if seg_id in segments_edges:
                    raise ValueError(
                        f"Duplicate segment_id '{seg_id}' in 'segments' array"
                    )
                segments_edges[seg_id] = lines
        else:
            # single segment object
            seg_id, lines = _parse_single_segment_object(data)
            segments_edges[seg_id] = lines

    return segments_edges


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
    the Kijko–Smit module, and convert to SegmentMFDConfig objects.

    Returns dict[name] -> SegmentMFDConfig.
    """
    with ab_json.open("r") as f:
        data = json.load(f)

    seg_configs: Dict[str, SegmentMFDConfig] = {}

    for s in data["segments"]:
        name = s["name"]
        ks = s["ks_results"]
        haz = s["hazard_params"]

        a = float(ks["a"])
        b = float(ks["b"])
        mmin_hazard = float(haz["Mmin_hazard"])

        seg_configs[name] = SegmentMFDConfig(
            name=name,
            a=a,
            b=b,
            mmin_hazard=mmin_hazard,
            max_mag=max_mag_default,
            bin_width=bin_width,
        )

    return seg_configs


def build_truncated_gr_mfd(seg_cfg: SegmentMFDConfig) -> TruncatedGRMFD:
    """
    Build a TruncatedGRMFD for a given segment using its a, b, mmin_hazard.
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
    cfg: SubductionSourceConfig | None = None,
) -> Dict[str, ComplexFaultSource]:
    """
    Build one ComplexFaultSource per segment, using:

    - geometry from cfg.geometry_json,
    - a–b values from cfg.ab_json,
    - TruncatedGRMFD with (a, b, Mmin_hazard, max_mag_default),
    - StrasserInterface MSR,
    - PoissonTOM(investigation_time).

    Returns:
        dict[name] -> ComplexFaultSource
    """
    if cfg is None:
        cfg = SubductionSourceConfig()

    # 1) Load geometry and a–b configs
    geom_segments = load_geometry_segments(cfg.geometry_json)
    ab_segments = load_ab_segments(
        cfg.ab_json, max_mag_default=cfg.max_mag_default, bin_width=cfg.bin_width
    )

    # 2) Consistency check: segment names must match
    geom_names = set(geom_segments.keys())
    ab_names = set(ab_segments.keys())

    missing_geom = ab_names - geom_names
    missing_ab = geom_names - ab_names

    if missing_geom:
        raise ValueError(
            f"Segments found in a–b JSON but missing in geometry: {sorted(missing_geom)}"
        )
    if missing_ab:
        raise ValueError(
            f"Segments found in geometry but missing in a–b JSON: {sorted(missing_ab)}"
        )

    # 3) Build ComplexFaultSource per segment
    sources: Dict[str, ComplexFaultSource] = {}
    msr = StrasserInterface()

    for idx, name in enumerate(sorted(geom_names)):
        print(idx)
        edges_lines = geom_segments[name]
        seg_ab_cfg = ab_segments[name]

        # MFD
        mfd = build_truncated_gr_mfd(seg_ab_cfg)

        # Temporal occurrence model: rates are annual, time span is 1 year
        tom = PoissonTOM(cfg.investigation_time)

        # Build source_id and name similar to your XML, e.g. i01, i02, ...
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
            edges=edges_lines,
            rake=cfg.rake,
        )

        sources[name] = src

    return sources


# ---------------------------------------------------------------------------
# OPTIONAL: SCRIPT ENTRY POINT (write NRML)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """
    Example usage:

    - Build complex-fault sources
    - Write a single NRML source model file

    Adjust NRML_OUT as needed or comment out the write step if you only
    want the Python objects.
    """
    NRML_OUT = Path("subduction_interface_sources.xml")

    cfg = SubductionSourceConfig(
        geometry_json=Path("./out/subduction_interface_segment_01.json"),  # <--- your JSON above
        ab_json=Path("./subduction_ab_results/subduction_ab_results.json"),
        rupture_mesh_spacing=5.0,
        rupture_aspect_ratio=1.0,
        rake=90.0,
        investigation_time=1.0,
        source_id_prefix="i",
        max_mag_default=9.6,
        bin_width=0.1,
    )
    sources_by_name = build_subduction_interface_sources(cfg)

    # Collect sources as a list for sourcewriter
    sources_list = list(sources_by_name.values())

    # Write NRML source model (if you want)
    write_source_model(
        dest=str(NRML_OUT),
        sources_or_groups=sources_list,
        name="Subduction interface complex-fault model",
        investigation_time=cfg.investigation_time,
    )

    print(f"Wrote {len(sources_list)} ComplexFaultSource objects to {NRML_OUT}")

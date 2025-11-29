# subduction/paths.py
"""
Centralised paths for the subduction workflow.

This module should be the *only* place where we hard-code filenames
and directory structure. Other modules import from here.

Layout (relative to ROOT):

data/
  geom/
    slab_interp_depth.csv
  catalog/
    cat_slab_interface_dc.csv
  MC_SUMMARY.tsv

outputs/
  geometry/      # geometry JSON, rasters, etc.
  ab/           # a–b estimates, MFD diagnostics
  sources/      # OpenQuake source models
  figures/      # generic figures (if not already under ab/ or geometry/)
"""

from __future__ import annotations

from pathlib import Path

# Project root (one level above the subduction/ package)
ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Input data directories
# ---------------------------------------------------------------------------

DATA_DIR = ROOT / "data"
SLAB_DIR = DATA_DIR / "slab_2.0"
RESULTS_DIR = ROOT / "results"
FINAL_CATALOG_DIR = RESULTS_DIR / "catalogs" / "integrated" / "final"
DC_CATALOG_DIR = FINAL_CATALOG_DIR / "declustered"


# Input files
SLAB_DEPTH = SLAB_DIR / "sam_slab2_dep_02.23.18.xyz"
MC_SUMMARY = FINAL_CATALOG_DIR / "mc_over_time_ks.txt"
CAT_SLAB_INTERFACE_DC = DC_CATALOG_DIR / "cat_slab_interface_dc.csv"

# ---------------------------------------------------------------------------
# Output base directories
# ---------------------------------------------------------------------------

OUTPUT_DIR = ROOT / "subduction" / "outputs"
GEOM_OUTPUT_DIR = OUTPUT_DIR / "geometry"
AB_OUTPUT_DIR = OUTPUT_DIR / "ab"
SOURCE_OUTPUT_DIR = OUTPUT_DIR / "sources"
FIGURE_OUTPUT_DIR = OUTPUT_DIR / "figures"


def ensure_output_dirs() -> None:
    """
    Create standard output directories if they do not exist.
    """
    for d in (
        GEOM_OUTPUT_DIR,
        AB_OUTPUT_DIR,
        SOURCE_OUTPUT_DIR,
        FIGURE_OUTPUT_DIR,
    ):
        d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers for specific files (segment-aware where useful)
# ---------------------------------------------------------------------------

def segment_geom_json(segment_id: str) -> Path:
    """
    Geometry JSON for a given subduction segment.

    Example:
        segment_geom_json("segment_01")
        -> outputs/geometry/subduction_interface_segment_01.json
    """
    return GEOM_OUTPUT_DIR / f"subduction_interface_{segment_id}.json"


def ab_results_json(name: str = "subduction_ab_results") -> Path:
    """
    JSON with Kijko–Smit a–b results for all segments.
    """
    return AB_OUTPUT_DIR / f"{name}.json"


def segment_magtime_png(segment_name: str) -> Path:
    """
    Magnitude–time diagnostic plot for a segment.
    """
    return AB_OUTPUT_DIR / f"{segment_name}_magtime.png"


def segment_mfd_png(segment_name: str, mmin: float) -> Path:
    """
    Cumulative MFD diagnostic plot for a segment for a given Mmin.
    """
    return AB_OUTPUT_DIR / f"{segment_name}_mfd_Mmin{mmin:.1f}.png"


def oq_source_yaml(model_name: str = "subduction_interface") -> Path:
    """
    OpenQuake source model file (YAML or XML).
    """
    return SOURCE_OUTPUT_DIR / f"{model_name}.xml"

# ---------------------------------------------------------------------------
# Backwards compatibility shim (optional)
# ---------------------------------------------------------------------------


class paths:  # noqa: N801 - keep the original name for now
    """
    Thin wrapper to keep existing imports working, e.g.:

        from subduction import paths
        paths.slab_depth

    New code should prefer the module-level names and helper functions.
    """
    data = DATA_DIR
    geom = SLAB_DIR
    outputs = OUTPUT_DIR

    catalog = CAT_SLAB_INTERFACE_DC
    MC_SUMMARY = MC_SUMMARY
    slab_depth = SLAB_DEPTH

    # Historic single-geometry path; keep pointing at segment_01 by default
    slab_segment_geom = segment_geom_json("segment_01")

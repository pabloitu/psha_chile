# ssm_config.py  (INTRASLAB)
# All paths and parameters for the intraslab SSM/SM pipeline. Edit here only.
# Run order: s00_mc -> s01_build_ssm -> s02_build_sm
# There is no fault handoff for the slab: no buffers, no Mmax cap.

from pathlib import Path

try:
    from cat_no_mech_handler import paths as cat_paths
    from ssm import paths as ssm_paths
except ImportError:          # allows importing the module outside the project
    cat_paths = ssm_paths = None

# grid (full-domain slab grid, not the crustal one)
GRID_CSV = ssm_paths.grid_01 if ssm_paths else Path("grid.csv")
BBOX = (-80.0, -60.0, -56.0, -17.0)   # lon_min, lon_max, lat_min, lat_max

# classes, smoothed separately and superposed (continuous total field).
# The old ssm_intraslab.py pooled these two under one national (a, b); they
# have different b and different Mmax, so they are fit and scaled separately.
CLASSES = {
    "intra_slab": {"catalog": cat_paths.cat_intra_slab_dc if cat_paths else None,
                   "region": None},
    "slab_deep":  {"catalog": cat_paths.cat_slab_deep_dc if cat_paths else None,
                   "region": None},
}

# borrow the b-value of other class(es) (shape only; the rate stays local).
# Value: a class name, or a list of classes -> b fit on their pooled catalog.
B_SOURCE = {
    # "slab_deep": "intra_slab",
}

# completeness per class: (Mc, since_year) steps, read off s00_mc.py figures.
# The mc_window / tc_years columns on the catalogs are IGNORED.
# Observation period for magnitude M is PRESENT_YEAR - since_year + 1 of the
# lowest Mc <= M.
COMPLETENESS = {
    "intra_slab": [(4.4,2015),
(4.8,2005),
(5.0,1995),
(5.1,1960),],
    "slab_deep": [(5.2,2020),
(5.3,2015),
(5.4,2010),
(5.5,1995),
(5.6,1955)],
}
PRESENT_YEAR = 2023

MIN_EVENTS_PER_WINDOW = 8
B_ERR_WARN = 0.15

# magnitude frequency
MMIN_FORECAST = 4.9
DM = 0.1
MC_MIN_FIT = 5.0
MMAX_PAD = 0.2
MMAX_OVERRIDE = {}       # e.g. {"slab_deep": 7.5}

# kernel / smoothing (Helmstetter-style adaptive)
N_NEIGHBORS = 25
KERNEL_POWER = 1.5
MAX_EVENT_GRID_DIST_KM = 500.0
MIN_KERNEL_KM = 5.0
B_COMPLETENESS = None    # None -> each class uses its own b for event weights

# sm (point sources). Depths come from the slab geometry, not a constant:
# s02_build_sm delegates to the existing intraslab builder.
TRT = "Subduction IntraSlab"
RUPTURE_MESH_SPACING = 5.0
RUPTURE_ASPECT_RATIO = 1.0
INVESTIGATION_TIME_YR = 1.0

# outputs
OUT = Path("ssm_intraslab_outputs")
FIG = OUT / "figures"
SSM_GRID = OUT / "ssm_mfd_grid.csv"
SM_XML = OUT / "ssm_intraslab_point_sources.xml"

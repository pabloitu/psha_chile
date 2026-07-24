# ssm_config.py  (INTRASLAB)
# All paths and parameters for the intraslab SSM/SM pipeline. Edit here only.
# Run order: s00_decluster -> (review removed_large.csv, fill DC_KEEP_IDS)
#            -> s01_mc -> (paste approved COMPLETENESS below)
#            -> s01_build_ssm -> s02_build_sm
# Single upstream input: the classified catalog. The catalog handler's
# *_mc.csv / *_dc.csv files and its mc.py / decluster.py are NOT used.
# There is no fault handoff for the slab: no buffers, no Mmax cap.

from pathlib import Path

try:
    from cat_no_mech_handler import paths as cat_paths
    from ssm import paths as ssm_paths
except ImportError:          # allows importing the module outside the project
    cat_paths = ssm_paths = None

# outputs
OUT = Path("ssm_intraslab_outputs")
FIG = OUT / "figures"
OUT_DIR = OUT               # aliases used by s00_decluster / s01_mc
FIG_DIR = FIG
SSM_GRID = OUT / "ssm_mfd_grid.csv"
SM_XML = OUT / "ssm_intraslab_point_sources.xml"

# input: classified catalog BEFORE any Mc filtering or declustering
CAT_CLASSIFIED = (Path(cat_paths.cat_classified) if cat_paths
                  else Path("cat_classified.csv"))

# declustering (s00_decluster) — per class, inside this pipeline.
# gk74_sym (fs=1.0) reproduces the upstream symmetric-foreshock choice;
# all variants are written, DC_METHOD picks the one used downstream.
DC_METHODS = ["gk74", "gk74_sym", "uhrhammer", "gruenthal"]
DC_METHOD = "gk74"
DC_FS = 0.1
DC_FROM_YEAR = 1900          # pre-1900 events pass through as mainshocks
DC_MPROT = 7.0               # removed events >= this go to the review table
DC_KEEP_IDS = []             # TEAM INPUT after reviewing removed_large.csv

# completeness estimation (s01_mc) — UNdeclustered catalog, regular windows:
# one historical block HIST_START_YEAR -> REGULAR_FROM, then WINDOW_YEARS
# steps. Windows under MC_MIN_EVENTS fall to MC_HIST_FLOOR (flagged, not
# estimated).
WINDOW_YEARS = 10
REGULAR_FROM = 1900
HIST_START_YEAR = 1513
MC_P_VALUE = 0.1
MC_MIN_EVENTS = 50
MC_B_FIXED = 1.0             # KS with fixed b
MC_KS_N = 2500               # KS simulations per candidate
MC_MAX_SAMPLE = 3000         # subsample cap per window (seeded); None = all
MC_HIST_FLOOR = 7.5

# grid (full-domain slab grid, not the crustal one)
GRID_CSV = ssm_paths.grid_01 if ssm_paths else Path("grid.csv")
BBOX = (-80.0, -60.0, -56.0, -17.0)   # lon_min, lon_max, lat_min, lat_max

# classes, smoothed separately and superposed (continuous total field).
# The old ssm_intraslab.py pooled these two under one national (a, b); they
# have different b and different Mmax, so they are fit and scaled separately.
# Catalogs are THIS module's declustered outputs from s00_decluster.
CLASSES = {
    "intra_slab": {"catalog": OUT / "decluster" / f"cat_dc_intra_slab_{DC_METHOD}.csv",
                   "region": None},
    "slab_deep":  {"catalog": OUT / "decluster" / f"cat_dc_slab_deep_{DC_METHOD}.csv",
                   "region": None},
}

# borrow the b-value of other class(es) (shape only; the rate stays local).
# Value: a class name, or a list of classes -> b fit on their pooled catalog.
B_SOURCE = {
    # "slab_deep": "intra_slab",
}

# completeness per class: (Mc, since_year) steps — paste from
# outputs/mc/completeness_proposal.txt after reading the s01_mc figures.
# Current values predate the standalone s01_mc and MUST be re-derived.
COMPLETENESS = {
    "intra_slab": [(7.5, 1513), (5.6, 1960), (5.3, 1990)],
    "slab_deep": [(7.5, 1513), (6.1, 1950), (6.0, 1960), (5.8, 2000), (5.4, 2010)],
}
PRESENT_YEAR = 2023

MIN_EVENTS_PER_WINDOW = 8    # Weichert fit windows (ssm_lib), not s01_mc
B_ERR_WARN = 0.15

# magnitude frequency
MMIN_FORECAST = 4.9
DM = 0.1
DELTA_M = DM                 # alias used by s01_mc
MC_MIN_FIT = 5.5
MMAX_PAD = 0.2
MMAX_OVERRIDE = {}           # e.g. {"slab_deep": 7.5}
MMAX_SANITY = 8.4            # build must stop above this without an override

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
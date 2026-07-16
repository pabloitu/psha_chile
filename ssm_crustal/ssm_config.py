# ssm_config.py
# All paths and parameters for the crustal SSM/SM pipeline. Edit here only.
# Run order: s01_build_ssm -> s02_fault_buffers -> s03_cap_ssm_mmax -> s04_build_sm

from pathlib import Path

try:
    from cat_no_mech_handler import paths as cat_paths
    from ssm import paths as ssm_paths
except ImportError:          # allows importing the module outside the project
    cat_paths = ssm_paths = None

# grid
GRID_CSV = ssm_paths.grid_01_crustal if ssm_paths else Path("grid.csv")
BBOX = (-80.0, -60.0, -60.0, -17.0)   # lon_min, lon_max, lat_min, lat_max

# ssm classes, smoothed separately and superposed (continuous total field).
#   catalog: declustered class catalog (mainshocks)
#   region:  optional (lon_min, lon_max, lat_min, lat_max) restriction, or None
CLASSES = {
    "forearc":      {"catalog": cat_paths.cat_forearc_dc if cat_paths else None,
                     "region": None},
    "intraarc":     {"catalog": cat_paths.cat_intraarc_dc if cat_paths else None,
                     "region": None},
    "backarc":      {"catalog": cat_paths.cat_backarc_dc if cat_paths else None,
                     "region": None},
    "unclassified": {"catalog": cat_paths.cat_unclassified_dc if cat_paths else None,
                     "region": (-76.0, -64.0, -56.0, -47.0)},  # S Patagonia only
}

# borrow the b-value of other class(es) (shape only; the rate stays local).
# Value: a class name, or a list of classes -> b is fit on their pooled
# catalog (ESHM20 TECTO logic: b at domain scale, activity at class scale).
# Set after reading ssm_class_summary.csv / the completeness audit.
B_SOURCE = {
    "unclassified": "forearc",
    "backarc": "forearc",
}

# completeness per class: (Mc, since_year) steps, read off s00_mc.py figures.
# The mc_window / tc_years columns on the catalogs are IGNORED; this is the
# only completeness the model uses. Observation period for magnitude M is
# PRESENT_YEAR - since_year of the lowest Mc <= M.
# Example: [(4.5, 2010), (5.0, 1990), (5.5, 1965), (6.5, 1900)]
COMPLETENESS = {
    "forearc": [(4.4, 2015), (4.6, 2015), (4.7, 1990), (4.8, 1985), (5.0, 1980), (5.1, 1965)],
    "intraarc": [(4.4, 2015), (4.6, 2015), (4.7, 1990), (4.8, 1985), (5.0, 1980), (5.1, 1965)],
    "backarc": [ (5.3, 1975)],
    "unclassified": [(4.5, 1995)],
}
PRESENT_YEAR = 2023      # last year of catalog coverage

# a completeness step with fewer events than this is dropped from a class fit
MIN_EVENTS_PER_WINDOW = 8
B_ERR_WARN = 0.15        # bootstrap b_err above this -> warn, consider B_SOURCE

# magnitude frequency
MMIN_FORECAST = 4.9      # first bin lower edge of the forecast
DM = 0.1
MC_MIN_FIT = 4.5         # lowest magnitude used in the Weichert fits
MMAX_PAD = 0.2           # class Mmax = max observed in class + pad
MMAX_OVERRIDE = {"backarc": 7.2,
                 "forearc": 7.2,
                 "intraarc": 7.2,
                 "unclassified": 7.2}    # e.g. {"backarc": 7.5}

# kernel / smoothing (Helmstetter-style adaptive)
N_NEIGHBORS = 15
KERNEL_POWER = 1.5
MAX_EVENT_GRID_DIST_KM = 500.0
MIN_KERNEL_KM = 5.0
B_COMPLETENESS = None    # None -> each class uses its own b for event weights

# fault handoff
CAP_MAG = 6.0            # smoothed Mmax inside fault buffers
BUFFER_MARGIN_KM = 10.0
FAULTS_SHP = Path("../data/active_faults/crustal_faults_chile_updated.shp")

# sm (point sources)
TRT = "Active Shallow Crust"
RUPTURE_MESH_SPACING = 5.0
RUPTURE_ASPECT_RATIO = 1.0
HYPO_DEPTH_KM = 15.0
USD_KM = 0.0
LSD_KM = 30.0
INVESTIGATION_TIME_YR = 1.0

# outputs
OUT = Path("ssm_crustal_outputs")
FIG = OUT / "figures"
SSM_GRID = OUT / "ssm_mfd_grid.csv"
SSM_GRID_CAPPED = OUT / "ssm_mfd_grid_capped.csv"
BUFFERS_GEOJSON = OUT / "fault_buffers.geojson"
BUFFERS_UNION = OUT / "fault_buffers_union.geojson"
SM_XML = OUT / "ssm_crustal_point_sources.xml"

# Baseline (no faults), written by s05_build_sm_nofaults.py from the UNCAPPED
# s01 grid: the smoothed model keeps M up to each class's own Mmax everywhere,
# with no fault handoff. Same kernel, (a, b), cells and depths as the fault
# run -> any hazard difference is attributable to the merger alone.
# Hazard branches:
#   with faults : SM_XML          (s04) + the fault XMLs
#   baseline    : SM_XML_BASELINE (s05) alone
SM_XML_BASELINE = OUT / "ssm_crustal_point_sources_nofaults.xml"
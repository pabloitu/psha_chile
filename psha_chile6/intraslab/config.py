# In-slab smoothed seismicity: every parameter of s00-s03. Variants override
# these through hazard/variants.py.

import paths

OUT_ROOT = paths.OUT / "intraslab"
CAT = paths.CAT_CLASSIFIED
# alternative classification: catalog read from <catalog folder>/<CAT_VARIANT>/ (same file name)
CAT_VARIANT = None
SLAB_XYZ = paths.SLAB_XYZ
SLAB_THK = paths.SLAB_THK
SLAB_STR = paths.SLAB_STR
GRID_CSV = paths.GRID_CSV
BBOX = (-80.0, -60.0, -56.0, -17.0)

# classes in the classified catalog, fitted and smoothed separately
CLASSES = ["intra_slab", "slab_deep", "deep_nest"]

# historical cutoff: pre-instrumental depths cannot support a slab class
HIST_CUTOFF = 1900
HIST_CUTOFF_BY_CLASS = {}

# declustering (s00)
DC_METHODS = ["gk74", "gk74_sym", "uhrhammer", "gruenthal"]
DC_METHOD = "gk74"
DC_FS = 0.1
DC_FROM_YEAR = 1900
DC_MPROT = 7.0
DC_KEEP_IDS = []

# completeness (s01 proposes, COMPLETENESS is the approved table).
# The values below predate the standalone s01 and must be re-derived.
WINDOW_YEARS = 10
WINDOW_YEARS_BY_CLASS = {}
MC_ON_DECLUSTERED = False
DM = 0.1
MC_P_VALUE = 0.1
MC_MIN_EVENTS = 50
MC_B_FIXED = 1.0
MC_KS_N = 2500
MC_MAX_SAMPLE = 3000
MC_HIST_FLOOR = 7.5
MC_OUTLIER_DROP = 0.4
COMPLETENESS = {
    'intra_slab': [(7.5, 1900), (5.1, 1970), (4.8, 1990), (4.7, 2010)],
    'slab_deep': [(7.5, 1900), (6.5, 1950), (5.1, 1960), (4.7, 1990), (4.5, 2010)],
    'deep_nest': [(7.5, 1900), (4.8, 1970), (4.7, 1990), (4.6, 2000)],
}

T_END = None

# a-b and Mmax (s02)
MMIN_FIT = 5.0
MMIN_FIT_BY_CLASS = {"slab_deep": 5.8, "intra_slab": 5.6}
N_BOOT = 200
B_ERR_WARN = 0.15
B_SOURCE = {"deep_nest": "slab_deep"}
MMAX_PAD = 0.2
MMAX_OVERRIDE = {}
MMAX_SANITY = 8.4

# smoothing (s02)
MMIN = 4.9
N_NEIGHBORS = 25
KERNEL_POWER = 1.5
KERNEL = "power"            # "power": 1 / (r^2 + h^2)^KERNEL_POWER, "gauss": exp(-r^2 / 2 h^2)
# events that draw the spatial pattern: "floor" = the fit events (above MMIN_FIT),
# "complete" = every complete declustered event above the completeness magnitude
# of its period, weighted by its period (many more events, b and rate unchanged)
SMOOTH_EVENTS = "floor"
# choose KERNEL, N_NEIGHBORS and MAX_DIST_KM per class by time-block
# cross-validation of the spatial log-likelihood (s02), from KERNEL_CV_GRID
KERNEL_CV = False
KERNEL_CV_GRID = {"KERNEL": ["power", "gauss"], "N_NEIGHBORS": [10, 25, 50], "MAX_DIST_KM": [150.0, 300.0, 500.0]}
KERNEL_CV_BLOCK = 5.0       # years per held-out block
KERNEL_CV_MIN = 20          # events a block needs to be scored
MAX_DIST_KM = 500.0
MIN_KERNEL_KM = 5.0
KERNEL_BY_CLASS = {"deep_nest": {"MIN_KERNEL_KM": 20.0, "N_NEIGHBORS": 10}}

# domain (s02): cells need a slab node within MAX_SLAB_DIST_KM; with MASK_ZTOP
# set, cells whose slab top is shallower are removed before smoothing, so the
# rate is renormalized onto the deeper domain instead of deleted
MAX_SLAB_DIST_KM = 50.0
MASK_ZTOP = None
# per class: (min, max) slab-top depth km of the cells the class is smoothed
# onto, None = open; the class rate is renormalized onto those cells
MASK_BY_CLASS = {}

# point sources (s03)
TRT = "Subduction IntraSlab"
MSR = "StrasserIntraslab"
ASPECT = 1.0
DEPTH_OFFSET = 7.5
HALF_THICK = [(50.0, 7.5), (90.0, 10.0), (1e9, 15.0)]
LSD_EXTRA = 20.0
USD_AT_SLAB_TOP = True      # upper seismogenic depth not above the Slab2 top
# depths of the point sources, measured from the Slab2 top (intraslab/depth_profile.py):
# BAND "catalog": hypocentre and lower seismogenic depth from the in-slab catalog,
#   CATALOG_DEPTH "frac" as fractions of the Slab2 thickness (FRAC), or "regime"
#   in km by slab-top depth (REGIME: top below the key -> (hypocentre, lsd) km)
# BAND "plate": top to top + thickness; BAND "rule": HALF_THICK and LSD_EXTRA
# HYPO ("plate", "rule"): "mid" top + thickness / 2, "offset" top + DEPTH_OFFSET
BAND = "catalog"
CATALOG_DEPTH = "frac"
FRAC = (0.30, 0.65)
REGIME = {50.0: (22.0, 48.0), 1e9: (24.0, 57.0)}
HYPO = "offset"
NPD = [(0.5, 0.0, 60.0, 90.0), (0.5, 180.0, 60.0, 90.0)]
# In-slab smoothed seismicity: every parameter of s00-s03. Variants override
# these through hazard/variants.py.

import paths

OUT_ROOT = paths.OUT / "intraslab"
CAT = paths.CATALOG
# events of this family of paths.FAMILIES, CLASSES of them fitted
FAMILY = "in-slab"
CLASS_MAP = {}
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
# Marzocchi and Taroni (2014): rates, b and Mmax from the full catalog (DC_METHOD
# "none"); the spatial pattern from the declustered one (PATTERN_DC), so aftershock
# sequences do not shape the map; the pattern is normalized and scaled to the full rate
DC_METHODS = ["none", "gk74", "gk74_sym", "uhrhammer", "gruenthal"]
DC_METHOD = "none"
PATTERN_DC = "gk74"
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
# recomputed with fit_check.py (KS as s01_mc) on the catalog with sha256 bf47b653cb76f28f
COMPLETENESS = {
    "intra_slab": [(7.5, 1900), (6.0, 1960), (5.1, 1970), (4.9, 1990), (4.7, 2000), (4.4, 2010)],
    "slab_deep": [(7.5, 1900), (6.0, 1950), (5.1, 1960), (4.8, 1990), (4.7, 2000), (4.6, 2010)],
    "deep_nest": [(7.5, 1900), (5.1, 1960), (4.8, 1970), (4.7, 1990), (4.5, 2000), (4.2, 2010)],
}

T_END = None

# a-b and Mmax (s02)
# fit floors at the start of the b plateau per class (fit_check.py)
MMIN_FIT = 5.0
MMIN_FIT_BY_CLASS = {"intra_slab": 5.7, "slab_deep": 6.0, "deep_nest": 5.6}
N_BOOT = 200
B_ERR_WARN = 0.15
B_SOURCE = {}
# one b for these classes (joint Weichert at their own floors); the equality test
# does not reject it (p 0.26-0.67). Each class keeps its own rate, pattern and Mmax
B_POOL = ["intra_slab", "slab_deep"]
MMAX_PAD = 0.2
MMAX_OVERRIDE = {}
MMAX_SANITY = 8.4

# smoothing (s02)
MMIN = 4.9
N_NEIGHBORS = 25
KERNEL_POWER = 1.5
KERNEL = "power"            # "power": 1 / (r^2 + h^2)^KERNEL_POWER, "gauss": exp(-r^2 / 2 h^2)
# events that draw the spatial pattern (rate and b are unchanged):
# "complete" every complete declustered event, weighted by the rate it stands for
#   at the fit floor, 10^(b (Mc of its step - floor)) / T of its step, so the few
#   large events of the long early steps weigh as much as a whole modern band
# "floor" the same, only the events above the fit floor
# "all" every complete declustered event, weight 1: the maximum-likelihood pattern
#   when the pattern does not depend on magnitude (counts in every step scale with
#   the same density), old large events count as one event each
# "period" the events since SMOOTH_FROM with M >= SMOOTH_MC, equal weights
# "window" events complete in the completeness window they occur in (the table as
#   disjoint time windows), weight 10^(b (Mc of that window - floor)), as the inflation
#   1 + zeta(t) of Mizrahi et al. (2021); "window_T" the same divided by the window's
#   length, as eq. 4 of Hiemer et al. (2014)
# reference "all": every complete event of the declustered catalog with weight 1.
# "window_T" (Hiemer et al. 2014) corrects spatially varying completeness; with one
# table per class it only reweights eras, and the 1900-1970 window (one event,
# 1953 M7.7) drew 28 % of the intra_slab map and 79 % of Concepcion's rate. The
# retrospective test (pattern_test.py) also scored "all" 3-20 % higher. Variant
# smooth_window_T
SMOOTH_EVENTS = "all"
SMOOTH_FROM, SMOOTH_MC = 1990, 4.8
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
# two representative nodal planes: north-south strike, 60 dipping west normal and 30 dipping east reverse
NPD = [(0.5, 180.0, 60.0, -90.0), (0.5, 0.0, 30.0, 90.0)]
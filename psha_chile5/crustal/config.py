# Crustal model: smoothed seismicity per class plus active-fault sources,
# joined by capping the smoothed Mmax at CAP_MAG inside fault buffers.
# Variants override these through variants.py.

import paths

OUT_ROOT = paths.OUT / "crustal"
CAT = paths.CAT_CLASSIFIED
# alternative classification: catalog read from <catalog folder>/<CAT_VARIANT>/ (same file name)
CAT_VARIANT = None
GRID_CSV = paths.GRID_CRUSTAL_CSV
FAULTS_SHP = paths.FAULTS_SHP
BBOX = (-80.0, -60.0, -60.0, -17.0)

# classes in the classified catalog -> optional (lon_min, lon_max, lat_min, lat_max).
# The 07-24 classifier merges backarc into unclassified; the 07-16 model boxed
# unclassified to southern Patagonia (-76, -64, -56, -47), which would now drop
# the backarc events.
CLASSES = {"forearc": None, "intraarc": None, "unclassified": None}

HIST_CUTOFF = None
HIST_CUTOFF_BY_CLASS = {}

# declustering (s00), per class
DC_METHODS = ["gk74", "gk74_sym", "uhrhammer", "gruenthal"]
DC_METHOD = "gk74"
DC_FS = 0.1
DC_FROM_YEAR = 1900
DC_MPROT = 6.5
DC_KEEP_IDS = []

# completeness (s01 proposes, COMPLETENESS is the approved table)
WINDOW_YEARS = 10
WINDOW_YEARS_BY_CLASS = {}
MC_ON_DECLUSTERED = False
DM = 0.1
MC_P_VALUE = 0.1
MC_MIN_EVENTS = 50
MC_B_FIXED = 1.0
MC_KS_N = 2500
MC_MAX_SAMPLE = 3000
MC_HIST_FLOOR = 7.0
MC_OUTLIER_DROP = 0.4
COMPLETENESS = {
    "forearc": [(4.4, 2015), (4.7, 1990), (4.8, 1985), (5.0, 1980), (5.1, 1965)],
    "intraarc": [(4.4, 2015), (4.7, 1990), (4.8, 1985), (5.0, 1980), (5.1, 1965)],
    "unclassified": [(4.5, 1995)],
}
T_END = None

# a-b and Mmax (s02)
MMIN_FIT = 4.5
MMIN_FIT_BY_CLASS = {}
N_BOOT = 200
B_ERR_WARN = 0.15
B_SOURCE = {"unclassified": "forearc"}
MMAX_PAD = 0.2
MMAX_OVERRIDE = {"forearc": 7.2, "intraarc": 7.2, "unclassified": 7.2}
MMAX_SANITY = 8.0

# smoothing (s02)
MMIN = 4.9
N_NEIGHBORS = 15
KERNEL_POWER = 1.5
MAX_DIST_KM = 500.0
MIN_KERNEL_KM = 5.0
KERNEL_BY_CLASS = {}

# faults (s03): moment rate phi * mu * L * W * slip, branches PHI x MMAX x MFD
MU = 30.0e9
M0_C = 9.1
M0_AT_EDGE = True           # moment of each bin at its lower edge (reference crustalfaults.xml)
FAULT_MMIN = 6.0            # lower edge of the first fault bin; equals CAP_MAG
MMAX_ADD = 0.2              # mobs = max_mag + MMAX_ADD
TAPER_PAD = 0.5
DEFAULT_B = 0.8
DEFAULT_RAKE = 90.0
DISP_LENGTH_RATIO = 1.25e-5
ORIENT_BY_DIP_DIR = True    # reverse traces whose right-hand dip contradicts dip_dir
ZONE_DEPTH = (0.0, 20.0)    # depths of the reference branch
PHI = {"phi050": (0.50, 0.25), "phi075": (0.75, 0.50), "phi100": (1.00, 0.25)}
MMAX = {"mobs": 0.5, "mgeo": 0.5}
MFD = {"tgr": 0.5, "tap": 0.5, "al1": 0.0, "al2": 0.0, "al3": 0.0, "yc": 0.0}
W_REFERENCE = 0.0
W_NOFAULTS = 0.0
FAULT_MSR = "WC1994"
FAULT_ASPECT = 2.0
FIELDS = {"id": "id_seg", "name": "name", "dip": "dip", "dip_dir": "dip_dir", "rup_type": "rup_type",
          "usd": "upp_sd", "lsd": "low_sd", "max_mag": "max_mag", "b": "b_val", "slip": "slip_rate"}

# handoff and point sources (s04)
CAP_MAG = 6.0
BUFFER_MARGIN_KM = 10.0
TRT = "Active Shallow Crust"
MSR = "WC1994"
ASPECT = 1.0
HYPO_DEPTH = 15.0
USD = 0.0
LSD = 30.0
NPD = [(0.5, 0.0, 60.0, 90.0), (0.5, 180.0, 60.0, 90.0)]

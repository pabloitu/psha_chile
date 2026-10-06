# Crustal model: smoothed seismicity per class plus active-fault sources,
# joined by capping the smoothed Mmax at CAP_MAG inside fault buffers.
# Variants override these through variants.py.

import paths

OUT_ROOT = paths.OUT / "crustal"
CAT = paths.CATALOG
# events of this family of paths.FAMILIES. The campaign's unclassified held the
# backarc and the Patagonian events (07-24 classifier); catalog.csv names them, and
# CLASS_MAP reads them as unclassified until their own classes are fitted (D13)
FAMILY = "crustal"
CLASS_MAP = {}
# alternative classification: catalog read from <catalog folder>/<CAT_VARIANT>/ (same file name)
CAT_VARIANT = None
GRID_CSV = paths.GRID_CRUSTAL_CSV
FAULTS_SHP = paths.FAULTS_SHP
BBOX = (-80.0, -60.0, -60.0, -17.0)

# events left out of rates, pattern and Mmax: class -> rules, each a date (time_iso
# prefix) or {"box": (lon_min, lon_max, lat_min, lat_max), "mmin": M}. The 6 June 1960
# Aysen event (Mw 7.7, slow, probably a multiple rupture; Kanamori) would set the
# large-magnitude rate of intraarc; the large Magallanes-Fagnano earthquakes (1879,
# 1949, 1950) belong to that fault, not to the Patagonian background
EXCLUDE = {"intraarc": ["1960-06-06"],
           "patagonia_crustal": [{"box": (-72.5, -64.0, -55.5, -52.5), "mmin": 7.0}, "1950-01-30"]}

# classes (after CLASS_MAP) -> optional (lon_min, lon_max, lat_min, lat_max)
CLASSES = {"forearc": None, "intraarc": None, "backarc": None, "patagonia_crustal": None, "unclassified": None}

HIST_CUTOFF = None
HIST_CUTOFF_BY_CLASS = {}

# declustering (s00), per class
# Marzocchi and Taroni (2014): rates, b and Mmax from the full catalog (DC_METHOD
# "none"); the spatial pattern from the declustered one (PATTERN_DC), so aftershock
# sequences do not shape the map; the pattern is normalized and scaled to the full rate
DC_METHODS = ["none", "gk74", "gk74_sym", "uhrhammer", "gruenthal"]
DC_METHOD = "none"
PATTERN_DC = "gk74"
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
# forearc and backarc recomputed on the 30 Sep 2026 catalog (fit_check.py, KS as
# s01_mc); intraarc and Patagonia keep the earlier table (too few events before 1987)
COMPLETENESS = {
    "forearc": [(7.0, 1906), (4.4, 1986), (4.0, 2016)],
    "intraarc": [(5.1, 1965), (5.0, 1980), (4.8, 1985), (4.7, 1990), (4.4, 2015)],
    "backarc": [(7.0, 1894), (5.2, 1974), (4.8, 2004), (4.7, 2014)],
    "patagonia_crustal": [(5.1, 1965), (5.0, 1980), (4.8, 1985), (4.7, 1990), (4.4, 2015)],
    "unclassified": [(4.5, 1995)],
}
T_END = None

# a-b and Mmax (s02)
# fit floors at the start of the b plateau per class (fit_check.py)
MMIN_FIT = 4.5
MMIN_FIT_BY_CLASS = {"forearc": 5.5, "intraarc": 4.6, "backarc": 5.5, "patagonia_crustal": 4.5}
N_BOOT = 200
B_ERR_WARN = 0.15
B_SOURCE = {"unclassified": "forearc"}
MMAX_PAD = 0.2
MMAX_OVERRIDE = {}          # Mmax = observed maximum per class + MMAX_PAD
MMAX_SANITY = 8.0

# smoothing (s02)
MMIN = 4.9
# events that draw the spatial pattern, as in intraslab/config.py: "all" every complete
# event with weight 1 (reference); "window_T" weights by the completeness window
# (Hiemer et al. 2014); "complete" the old weights by magnitude step
SMOOTH_EVENTS = "all"
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

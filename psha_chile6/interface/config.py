# Subduction interface: every parameter of s00-s05. Variants override these
# through hazard/variants.py; do not edit a copy per run.

import paths

OUT_ROOT = paths.OUT / "interface"
CAT = paths.CATALOG
# events of this family of paths.FAMILIES; CLASS_MAP renames a class the model has no
# source for. patagonia_interface is read and falls outside SEG_BOUNDS (source: D7)
FAMILY = "interface"
CLASS_MAP = {}
# alternative classification: catalog read from <catalog folder>/<CAT_VARIANT>/ (same file name)
CAT_VARIANT = None
SLAB_XYZ = paths.SLAB_XYZ

# geometry (s00)
Z_TOP = 10.0                 # below the trench floor (5-8 km); campaign axis 4-5 %
Z_BOTTOM = 50.0
LAT_STEP = 0.25
N_EDGES = 10
MIN_SLAB_DEPTH = 20.0

# segments: exact cut latitudes S -> N (team input)
SEG_BOUNDS = [-45.6, -37.0, -32.0, -26.0, -17.6]
SEG_IDS = ["seg1_south", "seg2", "seg3", "seg4_north"]
FULL_ID = "seg0_full"

# declustering (s01)
# rates and b from the full catalog (DC_METHOD "none"), following Marzocchi and Taroni
# (2014); the declustered versions are written for comparison
DC_METHODS = ["none", "gk74", "gk74_sym", "uhrhammer", "gruenthal"]
DC_METHOD = "none"
DC_FS = 0.1
DC_FROM_YEAR = 1900
DC_MPROT = 7.0
DC_KEEP_IDS = []
WATCH_IDS = {887: "1960 M8.1 Arauco", 1009: "1962 M7.2", 28776: "1998 M7.0",
             110687: "2012 M7.1 Constitucion"}

# completeness (s02 proposes, COMPLETENESS is the approved table)
MC_WINDOWS = [(1513, 1900), (1900, 1950), (1950, 1976), (1976, 1986), (1986, 1997),
              (1997, 2002), (2002, 2007), (2007, 2010), (2010, 2013), (2013, 2016),
              (2016, None)]
DM = 0.1
MC_P_VALUE = 0.1
MC_MIN_EVENTS = 50
MC_B_FIXED = 1.0
MC_KS_N = 2500
MC_MAX_SAMPLE = 3000
MC_HIST_FLOOR = 7.5
MC_OUTLIER_DROP = None
# recomputed on the 30 Sep 2026 catalog (fit_check.py, KS as s02_mc)
COMPLETENESS = [(8.3, 1513), (6.8, 1900), (6.0, 1950), (5.2, 1976), (5.1, 1997), (4.8, 2002),
                (4.4, 2013), (4.0, 2016)]
T_END = None

# a-b (s03)
AB_ESTIMATOR = "weichert"
# fit floors at the start of the b plateau (fit_check.py); seg2 (Maule) one step higher
MMIN_FIT = 5.8
MMIN_FIT_BY_SEG = {"seg2": 6.0}
# (a, b) branch: None for the maximum-likelihood pair, else the percentile (16, 84, ...)
# of the bootstrap rate at AB_CTRL_M (capped at Mmax - 0.3) whose bootstrap pair is used
AB_PCT = None
AB_CTRL_M = 8.8
N_BOOT = 200
B_ERR_WARN = 0.15
REF_MAGS = [6.5, 7.0, 7.5, 8.0]

# rates (s04)
MU = 30.0e9
MMIN_HAZ = 6.5
BIN_W = 0.1
M0_C = 9.05
V_CONV = {"seg1_south": 0.066, "seg2": 0.066, "seg3": 0.066, "seg4_north": 0.066}
CHI = {"seg1_south": 0.8, "seg2": 0.8, "seg3": 0.8, "seg4_north": 0.8}
DCHI = 0.1
CHI_W = {"lo": 0.25, "mid": 0.5, "hi": 0.25}
MMAX = {"seg1_south": 9.5, "seg2": 9.1, "seg3": 8.5, "seg4_north": 8.8}
MMAX_TOL = 0.05

# logic tree
W_GEOM = {"segmented": 0.5, "non_segmented": 0.5}
W_RATE = {"seismic": 0.5, "geodetic": 0.5}
# tapered GR only, corner Mw 9.6 (Bird and Kagan 2004), cut at the segment Mmax
W_MFD = {"tgr": 0.0, "tapered": 1.0}
CORNER = 9.6

# Antarctic interface south of the Slab2 coverage (s04b): the PB2002 AN\SA trench, an assumed dip, the band
# between PAT_Z_TOP and PAT_Z_BOTTOM (km below sea level, the plane meets the sea floor at PAT_Z_TRENCH on the
# trench), and a rate from the geodetic moment only (coupling PAT_CHI, velocity PAT_V in m/yr: about 1.8 cm/yr
# Antarctic-South America; Frontiers in Earth Science 2021, doi 10.3389/feart.2021.782458, Nazca-South America
# 6.6 cm/yr north of the junction). b from a Nazca segment, Mmax from the area (Thingbaijam et al. 2017) unless set.
# With PATAGONIA the source is written into every interface branch file by s05.
PATAGONIA = True
PAT_TRENCH = paths.REPO / "data" / "shapefiles" / "pb2002_antarctic_trench.geojson"
PAT_NAME = "AN\\SA"
PAT_LAT_NORTH = SEG_BOUNDS[0]
PAT_DIP = 30.0
PAT_Z_TRENCH = 5.0
PAT_Z_TOP = 10.0
PAT_Z_BOTTOM = 50.0
PAT_STEP_KM = 10.0
PAT_V = 0.018
PAT_CHI = 0.5
PAT_B_FROM = "seg1_south"
PAT_MMAX = None

# sources (s05)
TRT = "Subduction Interface"
MSR = "StrasserInterface"
ASPECT = 1.0
RAKE = 90.0

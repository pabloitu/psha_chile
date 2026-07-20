# sub_config.py
# Config for the subduction interface pipeline. All decisions from the
# logic-tree review are encoded here; team-editable inputs are marked.

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# paths
SLAB_XYZ = ROOT / "data" / "slab_2.0" / "sam_slab2_dep_02.23.18.xyz"
# classified interface catalog BEFORE any Mc filtering or declustering —
# the upstream *_mc.csv/*_dc.csv variants embed the national per-epoch Mc
# stamps and are not used
CAT_INTERFACE = ROOT / "results" / "catalogs" / "integrated" / "cat_slab_interface.csv"
OUT_DIR = ROOT / "sub_interface" / "outputs"
GEOM_DIR = OUT_DIR / "geometry"
FIG_DIR = OUT_DIR / "figures"

# geometry
Z_TOP = 5.0            # km, top of locked interface
Z_BOTTOM = 60.0        # km, bottom of locked interface
LAT_STEP = 0.25        # deg, along-strike sampling of edges
N_EDGES = 10           # down-dip edges (top..bottom)
MIN_SLAB_DEPTH = 20.0  # km, skip lats where slab never reaches this

# segments — TEAM INPUT. Boundaries are exact cut latitudes (S -> N);
# len(SEG_BOUNDS) = len(SEG_IDS) + 1. Non-segmented branch uses the full span.
SEG_BOUNDS = [-45.6, -37.0, -32.0, -26.0, -17.6]
SEG_IDS = ["seg1_south", "seg2", "seg3", "seg4_north"]
FULL_ID = "seg0_full"

# completeness (s01)
# Windows seeded from cat_no_mech_handler/mc.py FIXED_WINDOWS; edit freely.
MC_WINDOWS = [
    ("1513-01-01", "1900-01-01"),
    ("1900-01-01", "1950-01-01"),
    ("1950-01-01", "1976-01-01"),
    ("1976-01-01", "1986-01-01"),
    ("1986-01-01", "1997-01-01"),
    ("1997-01-01", "2002-01-01"),
    ("2002-01-01", "2007-01-01"),
    ("2007-01-01", "2010-01-01"),
    ("2010-01-01", "2013-01-01"),
    ("2013-01-01", "2016-01-01"),
    ("2016-01-01", None),
]
DELTA_M = 0.1
MC_P_VALUE = 0.1
MC_MIN_EVENTS = 50
MC_B_FIXED = 1.0       # KS estimator with fixed b (handoff: MAXC rejected)
PRESENT_YEAR = 2025
MC_HIST_FLOOR = 7.5    # assumed Mc where KS has too few events (historical windows)

# TEAM INPUT — hand-built completeness steps (Mc, since_year) for the FULL
# interface catalog, read off the s02 plots; applied to every segment at
# the rate step. Empty = proposal not yet reviewed; s03 refuses to run.
COMPLETENESS = [(8.3, 1513), (6.8, 1900), (6.0, 1950), (5.3, 1976), (5.2, 1986), (5.0, 1997), (4.8, 2002), (4.4, 2013)]

# declustering (s01) — done HERE, not upstream (GEM practice: the window is
# an analysis choice). Variants all written; DC_METHOD picks the one used
# downstream, the rest feed the s03 sensitivity table.
DC_METHODS = ["gk74", "gk74_sym", "uhrhammer", "gruenthal"]
DC_METHOD = "gk74"
DC_FS = 0.1            # foreshock window fraction (gk74_sym uses 1.0 = upstream)
DC_FROM_YEAR = 1900    # pre-1900 events pass through as mainshocks
DC_MPROT = 7.0         # removed events >= this go to the review table
DC_KEEP_IDS = []       # TEAM INPUT after reviewing removed_large.csv

# a-b (s03)
AB_ESTIMATOR = "weichert"  # or "kijko_smit" — TEAM decision after s03 review
MMIN_FIT = 5.6            # fit floor; None = lowest completeness step.
                           # pick from figures/s03_b_stability.png
N_BOOT = 200
B_ERR_WARN = 0.15
AB_REF_MAGS = [6.5, 7.5, 8.0]

# rate models
MU = 30.0e9            # Pa, consistent with crustal SSM
MMIN_HAZ = 6.5         # interface sources start here
BIN_W = 0.1

# per-segment TEAM INPUTS (order = SEG_IDS), placeholders until assigned:
#   V_CONV: trench-normal convergence, m/yr (Angermann et al. 1999 defaults)
#   CHI:    coupling coefficient (Scholz & Campos 2012); branches CHI +/- 0.1
#   MMAX:   observed Mmax incl. historical record (single value, no branches;
#           southern segment fixed at 9.5 = Valdivia)
V_CONV = {"seg1_south": 0.066, "seg2": 0.066, "seg3": 0.066, "seg4_north": 0.066}
CHI = {"seg1_south": 0.8, "seg2": 0.8, "seg3": 0.8, "seg4_north": 0.8}
MMAX = {"seg1_south": 9.5, "seg2": 9.1, "seg3": 8.5, "seg4_north": 8.8}
DCHI = 0.1
CHI_W = {"lo": 0.25, "mid": 0.5, "hi": 0.25}

# logic tree weights
W_GEOM = {"segmented": 0.5, "non_segmented": 0.5}
W_RATE = {"seismic": 0.5, "geodetic": 0.5}
W_MFD = {"tgr": 0.5, "tapered": 0.5}

# source building
TRT = "Subduction Interface"
RUPT_MESH = 5.0
ASPECT = 1.0
RAKE = 90.0
INV_TIME = 1.0
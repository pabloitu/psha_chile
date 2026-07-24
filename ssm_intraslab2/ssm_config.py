# ssm_intraslab/ssm_config.py
# All paths and parameters for the intraslab SSM/SM pipeline. Edit here only.
# Run order: s00_decluster -> (review s00_decluster_removed_large.csv, fill
#            DC_KEEP_IDS) -> s01_mc -> (read figures, paste COMPLETENESS)
#            -> s02_build_ssm -> s03_build_sm
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

# historical cutoff (s00_decluster, applied before everything else).
# Pre-instrumental events have macroseismic locations with no depth
# constraint, so their assignment to a slab class is unconstrained — and
# a large one leaking in sets Mmax = M_obs + pad off a depth nobody
# measured. Chilean historical M8+ events are almost certainly interface.
# Events before HIST_CUTOFF are DROPPED from the class catalog; the
# completeness table then starts at the cutoff (no historical block).
# Per-class override via HIST_CUTOFF_BY_CLASS. Set to None to keep all.
# TEAM INPUT — decisions register entry, with the dropped events listed
# in s00_decluster_dropped_historical.csv.
HIST_CUTOFF = 1900
HIST_CUTOFF_BY_CLASS = {
    # "slab_deep": 1920,
}
# one historical block HIST_START_YEAR -> REGULAR_FROM, then WINDOW_YEARS
# steps. Windows under MC_MIN_EVENTS fall to MC_HIST_FLOOR (flagged, not
# estimated).
WINDOW_YEARS = 10
# per-class override: slab_deep is sparse and floors on most 10-yr windows.
# Widen it there rather than accepting a table built from floors. Classes
# absent from this dict use WINDOW_YEARS. Set to {} to disable.
WINDOW_YEARS_BY_CLASS = {
    # "slab_deep": 20,
}
REGULAR_FROM = 1900
# first year of the historical block. With HIST_CUTOFF set, there is no
# pre-cutoff data, so s01_mc starts the windows at the cutoff instead and
# this value is only used when HIST_CUTOFF is None.
HIST_START_YEAR = 1513
MC_P_VALUE = 0.1
MC_MIN_EVENTS = 50
MC_B_FIXED = 1.0             # KS with fixed b
MC_KS_N = 2500               # KS simulations per candidate
MC_MAX_SAMPLE = 3000         # subsample cap per window (seeded); None = all
MC_HIST_FLOOR = 7.5
# Mc basis. Detection is a network property, so Mc is estimated on the
# UNdeclustered catalog by default — a declustered catalog inherits the
# algorithm's deletions as fake incompleteness. But the RATES are fitted
# on the declustered catalog, and in a window containing a large
# aftershock sequence (1960 Valdivia, 2010 Maule) the sequence supplies
# many well-recorded small events, so the undeclustered roll-off drops
# and the table claims a completeness the declustered catalog cannot
# support — which the fit then absorbs as a steep b.
# MC_COMPARE_BASIS runs both and writes s01_mc_basis_{class}.png;
# MC_ON_DECLUSTERED switches which one feeds the proposal.
MC_COMPARE_BASIS = True
MC_ON_DECLUSTERED = False
# Mc method. "window" estimates Mc decade by decade and turns the result
# into a cumulative table with a reverse running maximum — which is where
# one contaminated decade leaks into every later epoch. "cumulative"
# estimates Mc on [y0, present] for a grid of start years, answering the
# table's own question directly: each estimate pools decades, so no single
# sequence dominates and no running maximum is needed.
# MC_CUMULATIVE always computes it as a diagnostic; MC_METHOD chooses
# which one feeds the proposal.
MC_CUMULATIVE = True
MC_METHOD = "window"      # "window" | "cumulative"
# A window whose KS Mc sits this far below the median of its neighbours is
# flagged and excluded from the proposal. The proposal takes a reverse
# running maximum, so without this a single bad estimate becomes a
# permanent floor for every later window — one window contaminating
# decades. Only downward excursions are flagged: a genuine Mc increase
# (network degradation) persists across windows and is not an outlier.
# Set to None to disable.
MC_OUTLIER_DROP = 0.4
# window-length multipliers for the s01_mc stability figure. Each extra
# factor reruns the full KS sweep — set to [1.0] if runtime bites.
MC_STAB_FACTORS = [0.5, 1.0, 2.0]

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
    # concentrated deep nest (Jujuy, ~24S), separated upstream by the
    # classifier. Fitted as its own class so its recurrence does not
    # contaminate the distributed slab statistics: it has its own Mmax
    # (~6.7 vs M8.0 for slab_deep) and its own a and b, and pooling it
    # would inflate the local a-value into a hazard bullseye. Comment out
    # to drop it from the model entirely.
    "deep_nest":  {"catalog": OUT / "decluster" / f"cat_dc_deep_nest_{DC_METHOD}.csv",
                   "region": None},
}

# per-class kernel overrides, merged over the module defaults below.
# A nest is spatially concentrated, so the adaptive bandwidth collapses to
# very small distances and the smoothed field becomes a spike. A floor on
# the kernel is more defensible than letting the bandwidth follow the
# cluster's own density.
KERNEL_BY_CLASS = {
    "deep_nest": {"MIN_KERNEL_KM": 20.0, "N_NEIGHBORS": 10},
}

# borrow the b-value of other class(es) (shape only; the rate stays local).
# Value: a class name, or a list of classes -> b fit on their pooled catalog.
B_SOURCE = {
    # "slab_deep": "intra_slab",
}

# completeness per class: (Mc, since_year) steps — paste from
# outputs/mc/s01_mc_completeness_proposal.txt after reading the s01_mc
# figures. Current values PREDATE the standalone s01_mc and are kept only
# so the re-derived table can be diffed against them. Do not trust them.
COMPLETENESS = {
    "intra_slab": [(7.5, 1900), (5.6, 1970)],
    "slab_deep":  [(7.5, 1900), (6.1, 1950), (5.9, 1970)],
    "deep_nest":  [(7.5, 1900), (5.6, 1990)],
}
# must match the catalog end; rates divide by (PRESENT_YEAR - step_year).
# s01_mc warns if the catalog ends more than 1.5 yr away from this.
PRESENT_YEAR = 2023

MIN_EVENTS_PER_WINDOW = 8    # Weichert fit windows (ssm_lib), not s01_mc
B_ERR_WARN = 0.15

# magnitude frequency
MMIN_FORECAST = 4.9
DM = 0.1
DELTA_M = DM                 # alias used by s01_mc
MC_MIN_FIT = 5.0
# per-class fit floor. The b-stability figure (s02_bstab_{class}.png) is
# the evidence for these: a floor inside the complete range gives a stable
# b, a floor below completeness drags b up because the missing small events
# steepen the apparent slope. Look for the plateau.
MC_MIN_FIT_BY_CLASS = {}
# run the b-vs-floor sweep in s02 (cheap; it refits each class ~16 times)
B_STABILITY = True
# cross-check b and rate with Kijko-Smit and the table-free positive
# estimators (van der Elst 2021, 2023; b-positive is USGS 2023 practice).
# Reported beside Weichert as assurance, never as the model value.
METHOD_COMPARE = True
# refit each completeness epoch alone (s02_epochs_{class}.png). The pooled
# Weichert fit weights bands by their observation period, so a short recent
# band with a large count can set the slope while constraining nothing
# above its own magnitude range. Per-epoch fits localise that to a band.
EPOCH_FITS = True
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
# s03_build_sm delegates to the existing intraslab builder.
TRT = "Subduction IntraSlab"
RUPTURE_MESH_SPACING = 5.0
RUPTURE_ASPECT_RATIO = 1.0
INVESTIGATION_TIME_YR = 1.0
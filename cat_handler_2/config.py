# Paths, and the windows and preference rules of the data preparation
# (prepare.py). The classification parameters live in params.py.

import os

import numpy as np
from pathlib import Path


def _root():
    p = Path(__file__).resolve().parent
    for q in (p, *p.parents):
        if (q / ".git").exists() or (q / "pyproject.toml").exists():
            return q
    return p.parent


ROOT = Path(os.environ.get("PROJECT_ROOT", _root()))
CAT = ROOT / "data" / "catalogs"
OUT = ROOT / "results" / "cat_handler_2"
PREP = OUT / "prepare"
HERE = Path(__file__).resolve().parent

# inputs, frozen
CABELLO = CAT / "Integrated_Seismic_Catalog_complete.csv"
POTIN = CAT / "CHILE_SEISMICITY_RELOCATED.csv"
GCMT = [CAT / "gcmt_jan76_dec20.txt", CAT / "gcmt_jan21_aug25.txt"]
ANSS = CAT / "anss_fm.csv"
GEM = CAT / "cat_gem_chile.csv"
# hand decisions, each row with a reason and a reference
OVERRIDES = HERE / "overrides.csv"            # prepare: row fixes (time, location) and magnitudes
ADDITIONS = HERE / "additions.csv"            # prepare: events missing from Cabello
CLASS_OVERRIDES = HERE / "class_overrides.csv"  # classify: class decisions
RM = CAT / "ruiz_madariaga_2018.csv"
SLAB = {k: ROOT / "data" / "slab_2.0" / f"sam_slab2_{k}_02.23.18.xyz" for k in ("dep", "str", "dip", "thk")}
INTRAARC_SHP = ROOT / "data" / "shapefiles" / "intra_arc.shp"
TRENCH_SHP = ROOT / "data" / "shapefiles" / "sam_nazca_trench.shp"
# Antarctic (and Scotia-Antarctic) trench south of the Chile triple junction:
# the AN\\SA and SC/AN segments of Bird (2003) PB2002, frozen
TRENCH_AN = ROOT / "data" / "shapefiles" / "pb2002_antarctic_trench.geojson"
# classification of the old pipeline, for compare.py and the slides
OLD_CLASSIFIED = ROOT / "results" / "catalogs" / "integrated" / "cat_classified.csv"
# copy of catalog.csv as it was on 29 Sep 2026, before the crustal depth cap
# (DECISIONS 34) and the north cut; the hand-off counts the changes against it
CATALOG_PREV = OUT / "catalog_v1.csv"

# output: events with Cabello magnitude above MMIN; the dedup reads rows down
# to MMIN - DUP_DM so that a twin below the cut can still merge
MMIN = 3.9

# north limit of the study region: Cabello rows north of it are dropped
# before anything else, so that Peruvian seismicity stays out
LAT_MAX = -17.0
# region of the GCMT and ANSS reads (lat min, lat max, lon min, lon max),
# wider than REGION so that matching near its edges still works
BOX = (-60.0, -10.0, -82.0, -60.0)

# GCMT rows of Cabello carry the centroid; matched to the ndk centroid within
GC_DT, GC_KM = 3.0, 10.0

# duplicates: rows of different agencies, from DUP_FROM, merge when the pair
# is inside any of these windows (dt s, distance km, |dM|, larger magnitude of
# the pair at least). The wide |dM| window is for large events only, whose
# agency magnitudes differ most after conversion; for small events it merged
# M 4 rows into M 2 rows and dropped them below the cut
DUP_FROM = 1900
DUP_RULES = [(15.0, 50.0, 0.8, 0.0), (10.0, 30.0, 2.0, 5.5)]
DUP_DT, DUP_KM, DUP_DM = (max(r[k] for r in DUP_RULES) for k in range(3))
# pairs beyond these are kept but flagged loose in the group table
DUP_TIGHT_DT, DUP_TIGHT_KM = 10.0, 30.0

# magnitude of a duplicate group: always a Cabello magnitude, taken from the
# row of the first agency in MAG_PREF present in the group, else from a row
# with a native Mw, else by MAG_FALLBACK
MAG_PREF = ["GCMT", "ISC-GEM"]
# after those and a native Mw: the national network (local magnitudes, best for
# small events), then the teleseismic agencies; the location row is no longer
# the fallback (its ISC or USGS magnitude pushed ~2 000 events below the cut)
MAG_FALLBACK = ["CSN-improved", "USGS", "ISC", "CERESIS-GEM"]

# location of a duplicate group: first row in this order; "relocated" means a
# CSN row that Cabello took from Potin
LOC_PREF = ["relocated", "ISC-GEM", "ISC", "USGS", "CSN-improved", "GCMT", "CERESIS-GEM"]

# windows of the merge check (check.py): unmerged cross-agency pairs inside
# these are listed as possible missed duplicates
WIDE_DT, WIDE_KM, WIDE_DM = 60.0, 150.0, 1.5

# depth stage: agency default depths (km). Detected as spikes in each agency's
# depth histogram of the Cabello rows above MMIN: an integer depth carrying at
# least 30 rows and 5 times the median count of its neighbours (+/- 3 km).
# ISC and USGS fix shallow events at 0/5/10/33/35 km and intermediate ones at
# regional values (100, 150, 169, 181, 195, 200, 222, 250, 262); ISC-GEM at
# 5 km steps from 15 to 35; GCMT centroids at 12 and 15. CSN flags a fixed
# depth with depth_error = 0. GCMT fills a depth only where Cabello's is
# missing or at one of these values
FIXED_DEPTHS = {"ISC": [0, 10, 33, 35, 100, 150, 169, 181, 195, 200, 222, 250, 251, 262],
                "USGS": [0, 5, 10, 33, 35, 100, 150, 200],
                "ISC-GEM": [15, 20, 25, 30, 35],
                "GCMT": [12, 15],
                "CSN-improved": [0, 10, 150, 200, 220, 230]}
FIXED_ERROR_ZERO = ["CSN-improved"]

# locate: Potin for CSN rows Cabello did not relocate, and for fixed or
# missing depths of the other agencies (one-to-one)
POT_DT, POT_KM, POT_DM = 5.0, 30.0, 1.0
POT_FIX_DT, POT_FIX_KM = 10.0, 50.0
# GCMT centroid depth (FREE only) for fixed or missing depths left after Potin
GC_FILL_DT, GC_FILL_KM, GC_FILL_DM = 10.0, 50.0, 0.8

# mech: first source in MECH_ORDER with a complete pair of nodal planes;
# windows (dt s, km, |dM|) of the one-to-one matches per source
MECH_ORDER = ["anss", "gcmt", "gem", "cabello"]
# events located by a Cabello GCMT row (the centroid) take the ComCat
# hypocentre of their ANSS match, as the old merge did (ANSS preferred); the
# centroid stays in c_lon, c_lat, c_depth. A default ComCat depth keeps the
# centroid depth. ComCat's time for large events is often its W-phase centroid
# time, up to a minute after the GCMT PDE origin, hence the wider window
GCMT_TO_ANSS = True
ANSS_LOC_WIN = (90.0, 100.0, 0.5)
MECH_WIN = {"anss": (10.0, 50.0, 0.8), "gcmt": (10.0, 50.0, 0.8), "gem": (20.0, 100.0, 1.0)}

# classification parameters (params.py) are re-exported here so that every
# module sees one namespace
from cat_handler_2.params import *  # noqa: E402,F403

# review against Ruiz and Madariaga (2018): an event of the paper matches the
# catalog event closest in day, magnitude and distance (+/- 1 day; month or year when that is
# all the paper gives) within RM_KM, or within RM_DLAT degrees of latitude
# when the paper gives no longitude
RM_KM, RM_DLAT = 150.0, 2.0
# matches whose magnitude differs from the paper's by more than this are flagged weak
RM_DM = 0.5
REVIEW_M = 7.0

# cities of the hazard model, for the slide maps
CITIES = {"Iquique": (-70.15, -20.22), "Antofagasta": (-70.40, -23.65), "Copiapo": (-70.33, -27.37),
          "Valparaiso": (-71.62, -33.05), "Santiago": (-70.65, -33.45), "Concepcion": (-73.05, -36.83),
          "Pucon": (-71.95, -39.28), "Puerto Montt": (-72.94, -41.47), "Puerto Aysen": (-72.70, -45.40)}

# check.py sections: one transect perpendicular to the trench per section,
# centred on the trench every 2 deg of latitude (Nazca, SECTION_LATS) or every
# 2 x SECTION_HALF_KM along the Antarctic trench; the section holds the events
# between two lines parallel to the transect SECTION_HALF_KM (1 deg) either
# side, projected onto the transect; SECTION_X is its extent (negative seaward)
SECTION_LATS = np.arange(-15.0, -46.0, -2.0)
SECTION_HALF_KM = 111.2
SECTION_X = {"nazca": (-150.0, 900.0), "antarctic": (-150.0, 450.0)}
# labels: event magnitude at least this, by class family (sections and map)
LABEL_M = {"interface": 7.8, "in-slab": 6.8, "other": 5.5}
# map.png: at most MAP_LABEL_N labels per panel, largest first, none closer
# than MAP_LABEL_DEG to one already placed
MAP_LABEL_N, MAP_LABEL_DEG = 20, 1.0
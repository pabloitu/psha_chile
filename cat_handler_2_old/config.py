# Paths, windows and preference rules of the catalog build. Every choice that
# changes the catalog is a constant here; the stages read nothing else.

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
HERE = Path(__file__).resolve().parent

# inputs, frozen
CABELLO = CAT / "Integrated_Seismic_Catalog_complete.csv"
POTIN = CAT / "CHILE_SEISMICITY_RELOCATED.csv"
GCMT = [CAT / "gcmt_jan76_dec20.txt", CAT / "gcmt_jan21_aug25.txt"]
ANSS = CAT / "anss_fm.csv"
GEM = CAT / "cat_gem_chile.csv"
OVERRIDES = HERE / "overrides.csv"
ADDITIONS = HERE / "additions.csv"
RM = CAT / "ruiz_madariaga_2018.csv"
SLAB = {k: ROOT / "data" / "slab_2.0" / f"sam_slab2_{k}_02.23.18.xyz" for k in ("dep", "str", "dip", "thk")}
INTRAARC_SHP = ROOT / "data" / "shapefiles" / "intra_arc.shp"
TRENCH_SHP = ROOT / "data" / "shapefiles" / "sam_nazca_trench.shp"
# Antarctic (and Scotia-Antarctic) trench south of the Chile triple junction:
# the AN\\SA and SC/AN segments of Bird (2003) PB2002, frozen
TRENCH_AN = ROOT / "data" / "shapefiles" / "pb2002_antarctic_trench.geojson"
# classification of the old pipeline, for the transition table of check.py
OLD_CLASSIFIED = ROOT / "results" / "catalogs" / "integrated" / "cat_classified.csv"

# output: events with Cabello magnitude above MMIN; the dedup reads rows down
# to MMIN - DUP_DM so that a twin below the cut can still merge
MMIN = 3.9

# region of the GCMT and ANSS reads (lat min, lat max, lon min, lon max)
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

# depth stage: agency default depths, only for these agencies; GCMT fills a
# depth only where Cabello's is missing or at one of these values
FIXED_DEPTHS = [0.0, 10.0, 33.0, 35.0]
FIXED_AGENCIES = ["USGS", "ISC", "ISC-GEM"]

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

# classify
# depths the classifier cannot use: the event goes by mechanism, else to the
# interface where the interface exists (slab top < IF_MAX_TOP)
UNKNOWN_DEPTH = ["fixed", "missing", "assigned"]
# half-width of the interface band around the Slab2 top, per depth status
IF_TOL = {"relocated_cabello": 11.0, "relocated_potin": 11.0, "free": 15.0, "filled": 15.0}
IF_MAX_TOP = 50.0
# an interface-like mechanism makes the event interface up to this slab-top
# depth (deep interface, domain C) and up to MECH_EXTRA km beyond the band
IF_MECH_MAX_TOP = 65.0
MECH_EXTRA = 10.0
# assigned (historical) depths: Cabello's epicentres come from damage and sit
# landward of the rupture; the unknown-depth rule reaches this slab-top depth
IF_MAX_TOP_HIST = 65.0
DEEP_TOL = 15.0
# above a deep slab (top >= IF_MAX_TOP) and deeper than this: not crustal,
# slab_deep (mislocated), rule deep_above
FOREARC_MAX_Z = 70.0
# landward side of the trench: this many degrees east of the trench
LAND_EAST = 2.0
SLAB_MAX_KM = 15.0
INTRAARC_SHALLOW = 40.0
BACKARC_MAX_Z = 70.0
# south of the Chile triple junction (46.15 S, Bourgois et al. 2000) there is
# no Slab2; the Antarctic plate subducts at the trench TRENCH_AN. Events there:
# seaward of the trench outer_rise; within PAT_WIDTH_KM landward of it (and not
# deeper than PAT_MAX_Z) patagonia_interface; the rest patagonia_crustal
SOUTH_LAT = -46.15
PAT_WIDTH_KM = 150.0
PAT_MAX_Z = 60.0
CONV_AZ, NORM_CONE, SLIP_CONE = 78.0, 35.0, 90.0
# unknown depth, mechanism not interface-like: normal faulting -> intra_slab,
# otherwise forearc (rake of plane 1 inside NORMAL_RAKE)
NORMAL_RAKE = (-135.0, -45.0)
# unknown depth left unresolved: take the class of the located events around
# it (known depth, within VOTE_KM, at least VOTE_MIN of them) when one family,
# crustal (forearc, intraarc, backarc) or in-slab (intra_slab, slab_deep),
# holds VOTE_SHARE of them; the event gets the most common class of that family
VOTE_KM, VOTE_MIN, VOTE_SHARE = 50.0, 5, 0.7
VOTE_FAMILIES = {"crustal": ["forearc", "intraarc", "backarc"], "in-slab": ["intra_slab", "slab_deep"]}
# intra_slab events before this year go to the interface (old depths)
PRE_YEAR = 1930
NESTS = [{"name": "jujuy", "lon": -66.9, "lat": -24.0, "radius_deg": 0.8, "depth": (170.0, 320.0)}]


# review against Ruiz and Madariaga (2018): an event of the paper matches the
# catalog event closest in day, magnitude and distance (+/- 1 day; month or year when that is
# all the paper gives) within RM_KM, or within RM_DLAT degrees of latitude
# when the paper gives no longitude
RM_KM, RM_DLAT = 150.0, 2.0
# matches whose magnitude differs from the paper's by more than this are flagged weak
RM_DM = 0.5
REVIEW_M = 7.0

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
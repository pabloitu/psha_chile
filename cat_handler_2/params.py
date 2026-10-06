# Classification parameters: the choices that decide which source family an
# event feeds, i.e. the ones that matter for the hazard. classify.py reads
# these and nothing else numeric. Paths and the settings of the data
# preparation are in config.py.

# depth status the classifier cannot trust (agency default, missing,
# historical estimate): the event is classified without its depth where the
# interface exists (slab top < IF_MAX_TOP); over a deeper slab it is
# unresolved, in no family (poorly constrained data)
UNKNOWN_DEPTH = ["fixed", "missing", "assigned"]

# interface band: half-width in km around the Slab2 top, per depth status
IF_TOL = {"relocated_cabello": 11.0, "relocated_potin": 11.0, "free": 15.0, "filled": 15.0}
# the interface exists where the slab top is shallower than this (km)
IF_MAX_TOP = 50.0
# an interface-like mechanism makes the event interface up to this slab-top
# depth (deep interface) and up to MECH_EXTRA km beyond the band
IF_MECH_MAX_TOP = 65.0
MECH_EXTRA = 10.0
# historical (assigned) depths: the epicentre comes from damage reports and
# sits landward of the rupture; the unknown-depth rule reaches this slab top
IF_MAX_TOP_HIST = 65.0
# interface-like mechanism: one nodal plane within NORM_CONE deg of the slab
# normal and slip within SLIP_CONE deg of the convergence direction CONV_AZ
CONV_AZ, NORM_CONE, SLIP_CONE = 78.0, 35.0, 90.0
# unknown depth, mechanism not interface-like: normal faulting (rake of plane
# 1 inside NORMAL_RAKE) -> intra_slab, otherwise forearc
NORMAL_RAKE = (-135.0, -45.0)

# in-slab: below the interface band, down to the plate bottom (top + Slab2
# thickness); where the slab top is deeper than IF_MAX_TOP, slab_deep from
# DEEP_TOL km above the top; above a deep slab and deeper than FOREARC_MAX_Z
# the event is slab_deep too (mislocated), never crustal
DEEP_TOL = 15.0
FOREARC_MAX_Z = 70.0
# intra_slab events before this year go to the interface (old depths)
PRE_YEAR = 1930
# deep nests, kept apart from slab_deep
NESTS = [{"name": "jujuy", "lon": -66.9, "lat": -24.0, "radius_deg": 0.8, "depth": (170.0, 320.0)}]

# crustal classes (forearc, intraarc, backarc, patagonia_crustal,
# unclassified) hold events with a real depth of at most CRUSTAL_MAX_Z km;
# deeper events go through the slab tests, and unknown depths never go
# crustal where a slab exists. Cabello's 'Crustal' remarks and
# class_overrides.csv are the only exceptions
CRUSTAL_MAX_Z = 30.0
# landward side of the trench: towards a point this many degrees east of it
LAND_EAST = 2.0
# no Slab2 node within this distance: unclassified
SLAB_MAX_KM = 15.0

# south of the Chile triple junction (Bourgois et al. 2000) there is no Slab2;
# the Antarctic plate subducts at the trench TRENCH_AN. Seaward of it
# outer_rise; within PAT_WIDTH_KM landward and not deeper than PAT_MAX_Z
# patagonia_interface; the rest patagonia_crustal
SOUTH_LAT = -46.15
PAT_WIDTH_KM = 150.0
PAT_MAX_Z = 60.0

# source families the hazard model reads (the rest is excluded)
FAMILIES = {"interface": ["slab_interface", "patagonia_interface"],
            "in-slab": ["intra_slab", "slab_deep", "deep_nest"],
            "crustal": ["forearc", "intraarc", "backarc", "patagonia_crustal", "unclassified"]}

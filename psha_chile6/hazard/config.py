# Hazard input and post-processing settings.

import os

import paths

# site condition of the whole campaign: one named profile, one output tree
# (outputs/hazard/<SITE>, outputs/report/<SITE>). Z1.0 and Z2.5 from the
# ASK14 / CB14 reference relations for that Vs30.
SITE = "rock800"
PROFILES = {"rock800": {"VS30": 800.0, "Z1PT0": 40.0, "Z2PT5": 0.6}}
# SMOKE=1 in the environment: two cities, own output tree, for a quick end-to-end test
SMOKE = bool(os.environ.get("SMOKE"))
# FINAL=1 in the environment: the final run (full logic tree, spectral periods, 2475 yr,
# 500 km, point-source distance 100 km), own output tree. PRELIM=1: the final tree at PGA
# and 475 yr only, all cities, own output tree (hazard/prelim.py reads it)
FINAL = bool(os.environ.get("FINAL"))
PRELIM = bool(os.environ.get("PRELIM"))
# LEVEL2=1: the full-size family jobs and the sampled joint job at ten cities of different distances
# to the sources (hazard/check_tree.py, level 2), own output tree
LEVEL2 = bool(os.environ.get("LEVEL2"))
# TORNADO=1: the final one-at-a-time sensitivity (hazard/logic_tree.py TORN, hazard/tornado_final.py), own tree
TORNADO = bool(os.environ.get("TORNADO"))
TREE = ("_smoke" if SMOKE else "_level2" if LEVEL2 else "_tornado" if TORNADO else "_final" if FINAL
        else "_prelim" if PRELIM else "")
OUT_ROOT = paths.OUT / "hazard" / (SITE + TREE)
REPORT = paths.OUT / "report" / (SITE + TREE)

# sites: "cities" or "grid"
SITES = "cities"
CITIES = {"iquique": (-70.1357, -20.2133), "antofagasta": (-70.4000, -23.6500),
          "copiapo": (-70.3314, -27.3668), "valparaiso": (-71.6127, -33.0472),
          "santiago_centro": (-70.6693, -33.4489), "santiago_penalolen": (-70.52, -33.46),
          "concepcion": (-73.0503, -36.8269), "pucon": (-71.9600, -39.2822),
          "puerto_montt": (-72.9423, -41.4693), "puerto_aysen": (-72.7020, -45.4028)}
GRID_BBOX = (-76.0, -66.0, -46.0, -17.5)
GRID_STEP = 0.2
GRID_CSV = None            # csv with lon,lat; overrides GRID_BBOX/GRID_STEP
# Hornopiren (town, Los Lagos; on the Liquine-Ofqui fault), Puerto Williams (NGA gazetteer), Calama (in-slab
# only) and La Serena (segment 3): in the PRELIM, FINAL, LEVEL2 and TORNADO city sets, not in the campaign set
CITIES_EXTRA = {"hornopiren": (-72.4706, -41.9662), "puerto_williams": (-67.6096, -54.9336),
                "calama": (-68.9333, -22.4667), "la_serena": (-71.2519, -29.9027)}
CITIES_LEVEL2 = ("iquique", "antofagasta", "copiapo", "valparaiso", "santiago_centro", "concepcion", "pucon",
                 "hornopiren", "puerto_aysen", "puerto_williams")
if SMOKE:
    CITIES = {k: CITIES[k] for k in ("iquique", "santiago_centro", "puerto_aysen")}
elif LEVEL2:
    CITIES = {k: {**CITIES, **CITIES_EXTRA}[k] for k in CITIES_LEVEL2}
elif PRELIM or FINAL or TORNADO:
    CITIES = {**CITIES, **CITIES_EXTRA}

# site parameters of the profile. The cities are generic reference-rock sites, not
# measured ones, so the Vs30 flag is "inferred" (ASK14 and CY14 use the larger phi).
# Z1.0 and Z2.5 are the reference-relation values at this Vs30 (ASK14 36 m, CY14 31 m,
# CB14 0.57 km), so the crustal basin terms are neutral
VS30, Z1PT0, Z2PT5 = (PROFILES[SITE][k] for k in ("VS30", "Z1PT0", "Z2PT5"))
VS30_MEASURED = False

# intensity measures and outputs
IMTL = {"PGA": (0.005, 3.0)}
# IMTL = {"PGA": (0.005, 3.0), "SA(0.2)": (0.005, 4.0), "SA(0.5)": (0.005, 3.0), "SA(1.0)": (0.002, 2.0)}
N_LEVELS = 30
# 475 yr while the model is built; the final run adds 2475 yr (0.000404)
POES = [0.002105]
INV_TIME = 1.0

# calculation
TRUNC = 3.0
MAX_DIST = 400.0
MESH = 10.0
PS_DIST = 40.0
INDIVIDUAL_RLZS = True
STORE_RUPTURES = False     # True keeps rupture data for a later disaggregation (<= 10 sites)
MAX_DIST_TRT = {}
if FINAL or PRELIM or LEVEL2 or TORNADO:
    MAX_DIST = 500.0
    PS_DIST = 100.0
    # per tectonic region (the same in every job): interface ground motion matters to 600 km, crustal
    # ground motion beyond 300 km does not and the NGA-West2 models stop there; the in-slab uses MAX_DIST
    MAX_DIST_TRT = {"Subduction Interface": 600.0, "Active Shallow Crust": 300.0}
if FINAL:
    IMTL = {"PGA": (0.005, 3.0), "SA(0.1)": (0.005, 4.0), "SA(0.2)": (0.005, 4.0), "SA(0.5)": (0.005, 3.0),
            "SA(1.0)": (0.002, 2.0), "SA(2.0)": (0.001, 1.5)}
    POES = [0.002105, 0.000404]

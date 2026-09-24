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
OUT_ROOT = paths.OUT / "hazard" / (SITE + ("_smoke" if SMOKE else ""))
REPORT = paths.OUT / "report" / (SITE + ("_smoke" if SMOKE else ""))

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
if SMOKE:
    CITIES = {k: CITIES[k] for k in ("iquique", "santiago_centro")}

# site parameters of the profile
VS30, Z1PT0, Z2PT5 = (PROFILES[SITE][k] for k in ("VS30", "Z1PT0", "Z2PT5"))

# intensity measures and outputs
IMTL = {"PGA": (0.005, 3.0)}
# IMTL = {"PGA": (0.005, 3.0), "SA(0.2)": (0.005, 4.0), "SA(0.5)": (0.005, 3.0), "SA(1.0)": (0.002, 2.0)}
N_LEVELS = 30
POES = [0.002105, 0.000404]
INV_TIME = 1.0

# calculation
TRUNC = 3.0
MAX_DIST = 400.0
MESH = 10.0
PS_DIST = 40.0
INDIVIDUAL_RLZS = True
STORE_RUPTURES = False     # True keeps rupture data for a later disaggregation (<= 10 sites)
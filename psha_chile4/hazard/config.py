# Hazard input and post-processing settings.

import paths

OUT_ROOT = paths.OUT / "hazard"

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

# site parameters
VS30 = 380.0
Z1PT0 = 100.0
Z2PT5 = 5.0

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
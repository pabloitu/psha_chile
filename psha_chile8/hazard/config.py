# Hazard settings of S5a (DECISIONS, Hazard runs; psha_chile7 hazard/config.py with TORNADO=1)

from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
JOBS_DIR = HERE / "jobs"
OUT = HERE / "out"
OQ_PATH = "/data/PyCharmProjects/psha_renta/oq-engine"

# 15 cities (DECISIONS, Hazard runs, 30 Sep; Ushuaia for Puerto Williams and Punta Arenas added, 17 Nov)
CITIES = {"Iquique": (-70.1357, -20.2133), "Calama": (-68.9333, -22.4667), "Antofagasta": (-70.4000, -23.6500),
          "Copiapó": (-70.3314, -27.3668), "La Serena": (-71.2519, -29.9027), "Valparaíso": (-71.6127, -33.0472),
          "Santiago centro": (-70.6693, -33.4489), "Santiago Peñalolén": (-70.52, -33.46),
          "Concepción": (-73.0503, -36.8269), "Pucón": (-71.9600, -39.2822), "Puerto Montt": (-72.9423, -41.4693),
          "Hornopirén": (-72.4706, -41.9662), "Puerto Aysén": (-72.7020, -45.4028),
          "Punta Arenas": (-70.91, -53.16), "Ushuaia": (-68.30, -54.80)}
# final-run grid: lon, lat of data/grids/chile_005.csv (0.05°, 17.5–55.9° S); its vs30 column is not used
GRID = HERE / "sites" / "grid_005_2026-11-18.csv"

# site: generic rock, Vs30 inferred; Z1.0 and Z2.5 the reference-relation values at 800 m/s
VS30, Z1PT0, Z2PT5 = 800.0, 40.0, 0.6

# intensity measures and outputs
IMTL = {"PGA": (0.001, 3.0)}
N_LEVELS = 38
POES = [0.002105]
POES_FINAL = [0.002105, 0.000404]
INV_TIME = 1.0

# calculation
TRUNC = 3.0
MAX_DIST = {"Subduction Interface": 600.0, "Subduction IntraSlab": 500.0, "Active Shallow Crust": 300.0}
PS_DIST = 100.0
MESH = 10.0
MFD_BIN = 0.1
INDIVIDUAL_RLZS = True

# source families: folder of the NRML files with tree.json and tornado.json, tectonic region; folders read from
# CURRENT.md (the "sources" row of each family)
def current(section, row):
    import re
    txt = (ROOT / "CURRENT.md").read_text().split("\n## ")
    sec = next(x for x in txt if x.startswith(section))
    line = next(x for x in sec.splitlines() if x.startswith(f"| {row}"))
    return ROOT / re.search(r"`(model/[^`]+?)/?`", line).group(1)


FAMILIES = {
    "interface": {"short": "if", "trt": "Subduction Interface", "dir": current("Interface", "sources")},
    "inslab": {"short": "is", "trt": "Subduction IntraSlab", "dir": current("In-slab", "sources")},
    "crustal": {"short": "cr", "trt": "Active Shallow Crust", "dir": current("Crustal", "sources")},
}
# interface rupture scaling: the setMSRAbsolute level of source_lt_interface.xml of the interface folder
MSR = {"msr_strasser": ("StrasserInterface", 1 / 3), "msr_thingbaijam": ("ThingbaijamInterface", 1 / 3),
       "msr_allenhayes": ("AllenHayesInterfaceBilinear", 1 / 3)}

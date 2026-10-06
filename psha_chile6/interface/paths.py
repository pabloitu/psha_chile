# External inputs and the output root. psha_chile6 sits inside the repo
# root, so REPO is its parent; every step reads its inputs from here.

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent

# classified catalog of cat_handler_2 and its classification parameters;
# FAMILIES (family -> classes) comes from there, not from a copy
CATALOG = REPO / "results" / "cat_handler_2" / "catalog.csv"
CAT_PARAMS = REPO / "cat_handler_2" / "params.py"
_s = importlib.util.spec_from_file_location("cat_params", CAT_PARAMS)
_p = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_p)
FAMILIES = _p.FAMILIES

# the sensitivity campaign (frozen) and its catalogs, for the comparison only
PREV = REPO / "psha_chile5"
CAT_INTERFACE = REPO / "results" / "catalogs" / "integrated" / "cat_slab_interface.csv"
CAT_CLASSIFIED = REPO / "results" / "catalogs" / "integrated" / "cat_classified.csv"

SLAB_XYZ = REPO / "data" / "slab_2.0" / "sam_slab2_dep_02.23.18.xyz"
SLAB_THK = REPO / "data" / "slab_2.0" / "sam_slab2_thk_02.23.18.xyz"
SLAB_STR = REPO / "data" / "slab_2.0" / "sam_slab2_str_02.23.18.xyz"
GRID_CSV = REPO / "ssm" / "data" / "grid_01.csv"
GRID_CRUSTAL_CSV = REPO / "ssm" / "data" / "grid_01_crustal.csv"
FAULTS_SHP = REPO / "data" / "active_faults" / "crustal_faults_chile_updated.shp"

OUT = ROOT / "outputs"

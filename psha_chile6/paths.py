# External inputs and the output root. psha_chile4 sits inside the repo
# root, so REPO is its parent; every step reads its inputs from here.

from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent

CAT_INTERFACE = REPO / "results" / "catalogs" / "integrated" / "cat_slab_interface.csv"
CAT_CLASSIFIED = REPO / "results" / "catalogs" / "integrated" / "cat_classified.csv"
SLAB_XYZ = REPO / "data" / "slab_2.0" / "sam_slab2_dep_02.23.18.xyz"
SLAB_THK = REPO / "data" / "slab_2.0" / "sam_slab2_thk_02.23.18.xyz"
SLAB_STR = REPO / "data" / "slab_2.0" / "sam_slab2_str_02.23.18.xyz"
GRID_CSV = REPO / "ssm" / "data" / "grid_01.csv"
GRID_CRUSTAL_CSV = REPO / "ssm" / "data" / "grid_01_crustal.csv"
FAULTS_SHP = REPO / "data" / "active_faults" / "crustal_faults_chile_updated.shp"

OUT = ROOT / "outputs"
import os
from pathlib import Path

def find_project_root(start=None) -> Path:
    p = Path(start or __file__).resolve()
    for parent in [p] + list(p.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd().resolve()

# Directories
ROOT = Path(os.environ.get("PROJECT_ROOT", find_project_root()))
DATA = ROOT / "data"
CATALOG_DIR = DATA / "catalogs"
SLAB_DIR = DATA / "slab_2.0"
SHAPEFILE_DIR = DATA / "shapefiles"

SSM_DIR = ROOT / "ssm"
SSM_DATA = SSM_DIR / "data"

grid_01 = SSM_DATA / "grid_01.csv"
grid_05 = SSM_DATA / "grid_05.csv"

grid_01_crustal = SSM_DATA / "grid_01_crustal.csv"

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

# Shapefiles
intraarc_shp = SHAPEFILE_DIR / "intra_arc.shp"
trench_shp = SHAPEFILE_DIR / "sam_nazca_trench.shp"

# Slab 2.0
slab_depth =  SLAB_DIR / "sam_slab2_dep_02.23.18.xyz"
slab_strike = SLAB_DIR / "sam_slab2_str_02.23.18.xyz"
slab_dip =  SLAB_DIR / "sam_slab2_dip_02.23.18.xyz"

# Raw Catalogs
rawcat_anss = CATALOG_DIR / "ANSS.csv"
rawcat_gcmt_1976_2020 = CATALOG_DIR / "gcmt_jan76_dec20.txt"
rawcat_gcmt_2020_2025 = CATALOG_DIR / "gcmt_jan21_aug25.txt"

raw_potin = CATALOG_DIR / "CHILE_SEISMICITY_RELOCATED.csv"
rawcat_integrated = CATALOG_DIR / "Integrated_Seismic_Catalog_complete.csv"

# Output paths
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
CATALOGS = RESULTS / "catalogs"
FORMATTED_CATALOGS = CATALOGS / "formatted"
MERGED_CATALOGS = CATALOGS / "merge"
RELOCATED_CATALOGS = CATALOGS / "relocated"
INTEGRATED_CATALOGS =  CATALOGS / "integrated"
BEACHBALLS = INTEGRATED_CATALOGS / "beachballs"
CLASSIFIED_CATALOGS = CATALOGS / "classified"
FINAL_CATALOGS = INTEGRATED_CATALOGS / "final"
DECLUSTERED_CATALOGS = FINAL_CATALOGS / "declustered"
for d in (RESULTS, FIGURES, FORMATTED_CATALOGS, MERGED_CATALOGS, CLASSIFIED_CATALOGS,
          BEACHBALLS, RELOCATED_CATALOGS, FINAL_CATALOGS, DECLUSTERED_CATALOGS):
    d.mkdir(parents=True, exist_ok=True)

# Processed Catalogs
cat_anss = FORMATTED_CATALOGS / "anss.csv"
cat_gcmt_perez = FORMATTED_CATALOGS / "gcmt_perez.csv"
cat_gcmt = FORMATTED_CATALOGS / "gcmt.csv"
cat_isc = FORMATTED_CATALOGS / "isc.txt"
cat_gem = FORMATTED_CATALOGS / "cat_gem_chile.csv"
cat_potin = FORMATTED_CATALOGS / "potin.csv"
cat_integrated = FORMATTED_CATALOGS / "integrated.csv"

# Merge
cat_merged = MERGED_CATALOGS / "cat_merged.csv"
cat_full = MERGED_CATALOGS / "cat_full.csv"

# Relocated
cat_relocated = RELOCATED_CATALOGS / "cat_relocated.csv"
cat_integrated_relocated = RELOCATED_CATALOGS / "cat_integrated_relocated.csv"

# Classified

cat_classified = INTEGRATED_CATALOGS / "cat_classified.csv"
cat_intraarc = INTEGRATED_CATALOGS / "cat_intraarc.csv"
cat_slab_interface = INTEGRATED_CATALOGS / "cat_slab_interface.csv"
cat_intra_slab = INTEGRATED_CATALOGS / "cat_intra_slab.csv"
cat_slab_deep = INTEGRATED_CATALOGS / "cat_slab_deep.csv"
cat_forearc = INTEGRATED_CATALOGS / "cat_forearc.csv"
cat_unclassified = INTEGRATED_CATALOGS / "cat_unclassified.csv"


anss_classified = CLASSIFIED_CATALOGS / "anss_classified.csv"
gcmt_classified = CLASSIFIED_CATALOGS / "gcmt_classified.csv"
merged_classified = CLASSIFIED_CATALOGS / "merged_classified.csv"
full_classified = CLASSIFIED_CATALOGS / "full_classified.csv"
relocated_classified = CLASSIFIED_CATALOGS / "relocated_classified.csv"
selected_classified = CLASSIFIED_CATALOGS / "selected_classified.csv"

### MC estimate
cat_full_mc = FINAL_CATALOGS / "cat_full_mc.csv"
cat_intraarc_mc = FINAL_CATALOGS / "cat_intraarc_mc.csv"
cat_slab_interface_mc = FINAL_CATALOGS / "cat_slab_interface_mc.csv"
cat_intra_slab_mc = FINAL_CATALOGS / "cat_intra_slab_mc.csv"
cat_slab_deep_mc = FINAL_CATALOGS / "cat_slab_deep_mc.csv"
cat_outer_rise_mc = FINAL_CATALOGS / "cat_outer_rise_mc.csv"
cat_forecarc_mc = FINAL_CATALOGS / "cat_forecarc_mc.csv"
cat_unclassified_mc = FINAL_CATALOGS / "cat_unclassified_mc.csv"
MC_SUMMARY = FINAL_CATALOGS / "mc_over_time_ks.txt"
MC_FILTER_SUMMARY = FINAL_CATALOGS / "mc_filter_summary.txt"

## declustered
cat_merged_dc = DECLUSTERED_CATALOGS / "cat_merged_dc.csv"
cat_intraarc_dc = DECLUSTERED_CATALOGS / "cat_intraarc_dc.csv"
cat_slab_interface_dc = DECLUSTERED_CATALOGS / "cat_slab_interface_dc.csv"
cat_intra_slab_dc = DECLUSTERED_CATALOGS / "cat_intraslab_dc.csv"
cat_slab_deep_dc = DECLUSTERED_CATALOGS / "cat_slab_deep_dc.csv"
cat_outer_rise_dc = DECLUSTERED_CATALOGS / "cat_outer_rise_dc.csv"
cat_forearc_dc = DECLUSTERED_CATALOGS / "cat_forearc_dc.csv"
cat_unclassified_dc = DECLUSTERED_CATALOGS / "cat_unclassified.csv"


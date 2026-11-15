"""Final GEM fault file after Pablo's edits (D16).

Reads Pablo's hand-edited copy of the database (data/faults/faults_gem_extra_pablo_<DATE>.shp: traces cleaned, redundant
faults removed by deleting their geometry), drops the rows without a trace and those of REMOVE, recomputes the lengths, sets the
Magallanes–Fagnano slip rate from GPS (DECISIONS) and writes data/faults/faults_gem_extra_<DATE>.shp and .csv.
"""
from pathlib import Path

import geopandas as gpd

import geo

HERE = Path(__file__).resolve().parent
DIR = HERE.parents[1] / "data" / "faults"

# settings
DATE = "2026-11-15"
# Pablo's edits in order: the first (traces cleaned, 12 removed), the second (7 far Argentine faults removed)
IN = DIR / f"faults_gem_extra_pablo_{DATE}b.shp"
OUT = DIR / f"faults_gem_extra_{DATE}"
# faults removed by Pablo after an edit (AR-0028a is already gone from the second edit): the Magallanes–Fagnano strands
# beside the main trace (b, c, d, AR-0056a, b, d, g), which would count the GPS rate of the whole zone again
REMOVE = ("CL-056e", "CL-056f", "CL-056g", "CL-056h", "CL-056i", "CL-056j")
# Magallanes–Fagnano slip rate from GPS (REPORT_D16.md section 3): Mendoza et al. 2015 Table 3; bounds Mendoza et al.
# 2011 and Mendoza et al. 2015 Model 1
FAGNANO_SR = (5.9, 4.4, 6.8)
FAGNANO_SRC = "GPS: Mendoza et al. 2015, Table 3 (5.8-6.0); bounds Mendoza et al. 2011 (4.4), 2015 Model 1 (6.8)"


def main():
    f = gpd.read_file(IN)
    gone = f.geometry.isna() | f.geometry.is_empty | f.fid.isin(REMOVE)
    print("removed (no trace):", ", ".join(f.fid[gone]))
    f = f[~gone].reset_index(drop=True)
    L = f.geometry.apply(geo.length)
    ed = (L - f["length"]).abs() > 0.05
    for r in f[ed].itertuples():
        print(f"{r.fid} {r.name}: {r.length:.1f} -> {L[r.Index]:.1f} km")
    f.loc[ed, "note"] = [("; ".join(x for x in (n, "trace edited by Pablo (15 Nov)") if x)) for n in f.note[ed].fillna("")]
    print("faults per source:", f.src.value_counts().to_dict())
    f["length"] = L
    k = f.system == "Magallanes–Fagnano"
    f.loc[k, ["sr", "sr_lo", "sr_hi"]] = FAGNANO_SR
    f.loc[k, ["sr_kind", "sr_txt", "sr_src"]] = "measured", "4.4-6.8", FAGNANO_SRC
    f.to_file(OUT.with_suffix(".shp"), encoding="UTF-8")
    f.drop(columns="geometry").to_csv(OUT.with_suffix(".csv"), index=False)
    print(f"{len(f)} faults written to {OUT}.shp / .csv")


if __name__ == "__main__":
    main()

# Alternative classified catalogs for the hazard sensitivity. classify_events.py
# and the reference catalogs are not touched; per variant this writes
#   results/catalogs/integrated/<tag>/cat_classified.csv
#   results/catalogs/integrated/<tag>/cat_slab_interface.csv
# which psha_chile5 reads through CAT_VARIANT = <tag>.
#   tol_m5, tol_p5   interface depth tolerance shifted by -5 / +5 km: the
#                    half-width of the band around the Slab2 top separating
#                    slab_interface from forearc above and intra_slab below
#   fixdep_if        reference tolerances; events at an agency default depth
#                    (FIXED_DEPTHS), not relocated and without a mechanism,
#                    classified intra_slab or forearc over a slab top within
#                    the interface domain, are moved to slab_interface

import os

import numpy as np
import pandas as pd

from cat_no_mech_handler import classify_events as ce
from cat_no_mech_handler import paths

# settings
FIXED_DEPTHS = [0.0, 10.0, 33.0, 35.0]
MOVE_FROM = ["intra_slab", "forearc"]
TOL = {"tol_m5": -5.0, "tol_p5": 5.0}


def fixed_to_interface(df):
    """Unknown-depth events in the interface domain -> slab_interface; returns their former class."""
    dep = pd.to_numeric(df["depth"], errors="coerce").round(1)
    mech = df[["strike1", "dip1", "rake1", "Mrr"]].apply(pd.to_numeric, errors="coerce").notna().any(axis=1)
    top = pd.to_numeric(df["sub_depth"], errors="coerce")
    m = (dep.isin(FIXED_DEPTHS) & (df["depth_error"].astype(str) != "relocated") & ~mech
         & df["class"].isin(MOVE_FROM) & np.isfinite(top) & (top <= ce.SUBDUCTION_CLASSIFY_MAX_SLAB_DEPTH))
    was = df.loc[m, "class"].copy()
    df.loc[m, "class"] = "slab_interface"
    df.loc[m, "class_raw"] = "slab_interface"
    return was


def write(df, tag):
    od = paths.INTEGRATED_CATALOGS / tag
    os.makedirs(od, exist_ok=True)
    df.to_csv(od / "cat_classified.csv", index=False)
    df[df["class"] == "slab_interface"].to_csv(od / "cat_slab_interface.csv", index=False)
    print(f"[{tag}] -> {od}")


def main():
    intra_poly = ce.load_union(str(paths.intraarc_shp))
    trench_line = ce.load_union(str(paths.trench_shp))
    slab = ce.load_slab_xyz(str(paths.slab_depth), str(paths.slab_strike), str(paths.slab_dip),
                            str(paths.slab_thk) if hasattr(paths, "slab_thk") else None)
    tmp = str(paths.INTEGRATED_CATALOGS / "_tmp_classified.csv")
    run = lambda: ce.classify_catalog(in_csv=str(paths.cat_integrated_relocated), out_csv_all=tmp,
                                      intra_poly=intra_poly, trench_line=trench_line, slab=slab)
    counts = {}
    t0, s0 = ce.INTERFACE_DEPTH_TOL, ce.STRICT_INTERFACE_DEPTH_TOL
    for tag, dz in TOL.items():
        ce.INTERFACE_DEPTH_TOL, ce.STRICT_INTERFACE_DEPTH_TOL = t0 + dz, s0 + dz
        df = run()
        write(df, tag)
        counts[tag] = df["class"].value_counts()
    ce.INTERFACE_DEPTH_TOL, ce.STRICT_INTERFACE_DEPTH_TOL = t0, s0

    df = run()
    was = fixed_to_interface(df)
    mv = df.loc[was.index]
    print(f"[fixdep_if] {len(was)} events moved to slab_interface, {int((mv['mag'] >= 5.5).sum())} with M>=5.5")
    print(pd.crosstab([was.rename("from"), mv["mag"] >= 5.5], pd.to_numeric(mv["depth"]).round(1)).to_string())
    write(df, "fixdep_if")
    counts["fixdep_if"] = df["class"].value_counts()
    os.remove(tmp)

    ref = pd.read_csv(paths.cat_classified, low_memory=False)["class"].value_counts()
    print("\nevents per class")
    print(pd.DataFrame({"ref": ref, **counts}).fillna(0).astype(int).to_string())


if __name__ == "__main__":
    main()
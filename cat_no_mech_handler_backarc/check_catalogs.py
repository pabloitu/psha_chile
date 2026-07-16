from cat_no_mech_handler.parsers import read_csep
from cat_no_mech_handler import paths


# catalog = read_csep.load_csep(paths.cat_integrated)
# # catalog.plot(show=True, figsize=(4,12))
#
# from csep.plots import plot_magnitude_versus_time
#
# plot_magnitude_versus_time(catalog, show=True)
import pandas as pd
from cat_no_mech_handler import paths

integ = pd.read_csv(paths.cat_integrated)

def has_any_mech(df):
    return df[["Mrr","Mtt","Mpp","Mrt","Mrp","Mtp","strike1","dip1","rake1","strike2","dip2","rake2"]].notna().any(axis=1)

print("Integrated (before):")
print("  total events:", len(integ))
print("  with any MT/SDR:", has_any_mech(integ).sum())
reloc = pd.read_csv(paths.cat_integrated_relocated)

print("Integrated relocated (after):")
print("  total events:", len(reloc))
print("  with any MT/SDR:", has_any_mech(reloc).sum())

merged = integ.merge(
    reloc[["id","time_iso","mag"]],
    on="id",
    suffixes=("_orig","_new"),
    how="inner",
)

print("time changed:", (merged["time_iso_orig"] != merged["time_iso_new"]).sum())
print("mag changed:", (merged["mag_orig"] != merged["mag_new"]).sum())

import numpy as np

before = integ[["id","longitude","latitude","depth"]].set_index("id")
after  = reloc[["id","longitude","latitude","depth"]].set_index("id")

joined = before.join(after, lsuffix="_orig", rsuffix="_new", how="inner")

print("lon changed:", np.isfinite(joined["longitude_orig"] - joined["longitude_new"]).sum())
print("lat changed:", np.isfinite(joined["latitude_orig"] - joined["latitude_new"]).sum())
print("depth changed:", np.isfinite(joined["depth_orig"] - joined["depth_new"]).sum())

from csep.plots import plot_magnitude_versus_time
catalog = read_csep.load_csep(paths.cat_integrated_relocated)
ax = plot_magnitude_versus_time(catalog, show=True)
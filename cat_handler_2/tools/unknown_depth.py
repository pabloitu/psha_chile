# Are the unknown-depth events sent to the slab (rule unk_slab) really
# intermediate-depth, or crustal? For each of them: the located events (real
# depth) within RADIUS_KM, and the share of those that are crustal, in-slab or
# other. Prints the counts by that share, by latitude band, by magnitude and by
# agency, and writes check/unknown_depth.csv with one row per event.
# usage: python -m cat_handler_2.tools.unknown_depth [radius_km]

import sys

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from cat_handler_2 import classify as K
from cat_handler_2 import config as C

RADIUS_KM = 50.0
MIN_NB = 5


def main(radius=RADIUS_KM):
    radius = float(radius)
    ev = pd.read_csv(C.OUT / "catalog.csv", dtype={"id": str}, low_memory=False)
    fam = {c: f for f, cs in C.FAMILIES.items() for c in cs}
    ev["family"] = ev["class"].map(fam).fillna("excluded")
    known = ~ev["depth_status"].isin(C.UNKNOWN_DEPTH)
    pool = ev[known & ev["family"].isin(["crustal", "in-slab"])]
    u = ev[ev["cls_rule"] == "unk_slab"].copy()
    t = cKDTree(K.unit(pool["longitude"].to_numpy(), pool["latitude"].to_numpy()))
    r = 2 * np.sin(radius / K.R / 2)
    nb = t.query_ball_point(K.unit(u["longitude"].to_numpy(), u["latitude"].to_numpy()), r)
    pf = pool["family"].to_numpy()
    pz = pool["depth"].to_numpy()
    u["n_nb"] = [len(i) for i in nb]
    u["crustal_share"] = [np.mean(pf[i] == "crustal") if len(i) >= MIN_NB else np.nan for i in nb]
    u["nb_depth_median"] = [np.median(pz[i]) if len(i) >= MIN_NB else np.nan for i in nb]
    u["verdict"] = np.select([u["crustal_share"].isna(), u["crustal_share"] >= 0.7, u["crustal_share"] <= 0.3],
                             ["few neighbours", "neighbours crustal", "neighbours in-slab"], "mixed")
    u["band"] = pd.cut(u["latitude"], np.arange(-58, -16, 4))
    u["period"] = np.where(u["year"] < 1964, "<1964", np.where(u["year"] < 2000, "1964-1999", ">=2000"))
    cols = ["id", "time_iso", "latitude", "longitude", "depth", "depth_status", "mag", "agency", "class", "slab_top",
            "n_nb", "crustal_share", "nb_depth_median", "verdict"]
    u[cols].sort_values("mag", ascending=False).to_csv(C.OUT / "check" / "unknown_depth.csv", index=False)
    print(f"unknown-depth events sent to the slab (unk_slab): {len(u)}, M >= 5.5: {int((u['mag'] >= 5.5).sum())}, "
          f"M >= 6: {int((u['mag'] >= 6).sum())}; located neighbours within {radius:.0f} km, at least {MIN_NB}\n")
    for name, key in (("verdict", "verdict"), ("verdict x magnitude", None), ("latitude band", "band"), ("agency", "agency"), ("period", "period")):
        if key is None:
            print(pd.crosstab(u["verdict"], pd.cut(u["mag"], [3.9, 4.5, 5.0, 5.5, 6.0, 7.0, 9.0]), margins=True).to_string(), "\n")
        else:
            print(pd.crosstab(u[key], u["verdict"], margins=True).to_string(), "\n")
    print("median depth of the located neighbours, by verdict:")
    print(u.groupby("verdict")["nb_depth_median"].median().round(0).to_string())
    print(f"\n-> {C.OUT / 'check' / 'unknown_depth.csv'}")


if __name__ == "__main__":
    main(*sys.argv[1:2])
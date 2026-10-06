# Which section holds an event. Looks the event up in catalog.csv by date
# (YYYY-MM-DD, or a date prefix) and a minimum magnitude, and prints for each
# match its position, class and the sections whose bounds contain it, with the
# distance from the trench and the offset across the transect.
# usage: python -m cat_handler_2.tools.where 2014-04-01 [mmin]

import sys

import numpy as np
import pandas as pd

from cat_handler_2 import check as K
from cat_handler_2 import config as C


def main(date, mmin=6.0):
    ev = pd.read_csv(C.OUT / "catalog.csv", dtype={"id": str}, low_memory=False)
    e = ev[ev["time_iso"].str.startswith(date) & (ev["mag"] >= float(mmin))]
    ts = K.transects()
    for _, r in e.iterrows():
        print(f"{r['id']} {r['time_iso']} M{r['mag']:.1f} lat {r['latitude']:.2f} lon {r['longitude']:.2f} depth {r['depth']} "
              f"({r['depth_status']}) class {r['class']} rule {r['cls_rule']} loc {r['loc_src']}")
        hit = False
        for t in ts:
            x, y = K.proj(t, r["longitude"], r["latitude"])
            x0, x1 = C.SECTION_X[t["fam"]]
            if abs(y) <= t["half"] and x0 <= x <= x1:
                print(f"   in {t['label']} ({t['fam']} trench at {t['lat0']:.1f} deg): {x:.0f} km from the trench, {y:+.0f} km across")
                hit = True
        if not hit:
            print("   in no section (between the bounds of two neighbours; see sections_missing.csv)")


if __name__ == "__main__":
    main(*sys.argv[1:3])

"""S3 step 4 (report only): the large crustal events near faults and the background Mmax with and without them.

Background Mmax = largest event of the class with class weight >= 0.5 (fits/run.observed) + 0.2. "Near a fault": within
NEAR_KM of a trace of A or B. Writes tables/large_events_<DATE>.csv and tables/mmax_rules_<DATE>.csv.
"""
import sys

import numpy as np
import pandas as pd

import background as BG
import faults as F

sys.path.insert(0, str(F.ROOT / "model" / "faults"))
import geo  # noqa: E402
import gr  # noqa: E402

TAB = F.HERE / "tables"

# settings
DATE = BG.DATE
M_LARGE, NEAR_KM, PAD, W_MIN = 6.5, 10.0, 0.2, 0.5


def main():
    d = gr.load(BG.CAT, mlow=M_LARGE)
    db = {k: F.read(k) for k in ("A", "B")}
    tr = {k: [geo.tree(g, 0.5) for g in f.geometry] for k, f in db.items()}
    rows = []
    for c in BG.CLASSES:
        x = d[d[f"W_{c}"] > 0]
        for e in x.itertuples():
            p = geo.xyz(np.array([[e.lon, e.lat]]))
            o = dict(cls=c, event_id=e.event_id, date=e.time[:10], mw=e.mw, w=getattr(e, f"W_{c}"), lon=e.lon, lat=e.lat)
            for k in db:
                dd = np.array([t.query(p)[0][0] for t in tr[k]])
                j = int(np.argmin(dd))
                o[f"fault_{k}"], o[f"km_{k}"] = db[k]["name"].iloc[j], float(dd[j])
            o["near"] = min(o["km_A"], o["km_B"]) <= NEAR_KM
            rows.append(o)
    t = pd.DataFrame(rows).sort_values(["cls", "mw"], ascending=[True, False])
    t.round(3).to_csv(TAB / f"large_events_{DATE}.csv", index=False)
    mm = []
    for c in BG.CLASSES:
        x = t[(t.cls == c) & (t.w >= W_MIN)]
        y = x[~x.near]
        mm.append(dict(cls=c, mmax=x.mw.max() + PAD, event=x.iloc[0].date if len(x) else "",
                       mmax_without_near=(y.mw.max() + PAD) if len(y) else np.nan,
                       event_without=y.iloc[0].date if len(y) else "", near_dropped=int(x.near.sum())))
    m = pd.DataFrame(mm)
    m.to_csv(TAB / f"mmax_rules_{DATE}.csv", index=False)
    with pd.option_context("display.width", 250):
        print(t[t.w >= 0.3].round(2).to_string(index=False))
        print(m.to_string(index=False))


if __name__ == "__main__":
    main()

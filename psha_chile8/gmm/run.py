"""Entry script of task GM1: record table, screening, residuals, scores, subsets, figures."""
import os
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
import pandas as pd

import records as B
import residuals as R
import scores as S
import screen as C

HERE = Path(__file__).resolve().parent
TAB = HERE / "tables"

# settings
DATE = "2026-11-15"
REBUILD = True
IMTS = list(R.IMT_PERIOD)
NBOOT = 200
CLASSES = ["interface", "inslab"]
SUBSETS = {"a": ("base", lambda d: d),
           "b": ("Mw ≥ 6.5", lambda d: d[d.mw >= 6.5]),
           "c": ("events from 2017 on", lambda d: d[d.time >= np.datetime64("2017-01-01", "s").astype(np.int64)]),
           "d": ("measured Vs30 only", lambda d: d[d.vs30measured]),
           "e": ("without loc_flag events", lambda d: d[~d.loc_flag]),
           "f1": ("in-slab shallow", lambda d: d[d.sub_inslab == "intraslab_shallow"]),
           "f2": ("in-slab intermediate", lambda d: d[d.sub_inslab == "intraslab_intermediate"]),
           "g": ("backarc all False", lambda d: d.assign(backarc=False)),
           "h": ("ztor = hypocentral depth", lambda d: d.assign(ztor=d.hypo_depth))}


def common(res):
    """Records every GMM of the class can be evaluated on, per intensity measure."""
    n = res.groupby(["imt", "record_id"]).gmm.nunique()
    full = n[n == res.gmm.nunique()].index
    return res.set_index(["imt", "record_id"]).loc[lambda x: x.index.isin(full)].reset_index()


def main():
    d = B.build()[0] if REBUILD or not (TAB / f"records_{DATE}.csv").exists() else pd.read_csv(TAB / f"records_{DATE}.csv")
    C.screen()
    summ, trend, tbins, sc, own, subs, allres = [], [], [], [], [], [], {}
    for cls in CLASSES:
        dc = d[d.cls == cls]
        res = R.residuals(dc, C.CAND[cls], IMTS)
        allres[cls] = res
        com = common(res)
        summ.append(R.summary(com).assign(cls=cls))
        t, b = R.trends(com, dc)
        trend.append(t.assign(cls=cls))
        tbins.append(b.assign(cls=cls))
        sc.append(S.score(com, NBOOT).assign(cls=cls, records="common"))
        own.append(S.score(res, NBOOT).assign(cls=cls, records="own"))
        for k, (lab, f) in SUBSETS.items():
            if k == "a" or (k.startswith("f") and cls != "inslab"):
                continue
            ds = f(dc)
            rs = common(R.residuals(ds, C.CAND[cls], IMTS)) if k in ("g", "h") else com[com.record_id.isin(ds.record_id)]
            if rs.event_id.nunique() < 5:
                continue
            subs.append(S.score(rs, NBOOT).assign(cls=cls, subset=k, label=lab))
        res.to_csv(TAB / f"residuals_{cls}_{DATE}.csv.gz", index=False)
    pd.concat(summ).to_csv(TAB / f"residuals_summary_{DATE}.csv", index=False)
    pd.concat(trend).to_csv(TAB / f"trends_{DATE}.csv", index=False)
    pd.concat(tbins).to_csv(TAB / f"trends_bins_{DATE}.csv", index=False)
    pd.concat(sc + own).to_csv(TAB / f"scores_{DATE}.csv", index=False)
    pd.concat(subs).to_csv(TAB / f"scores_subsets_{DATE}.csv", index=False)
    import figs
    figs.main(d, allres)


if __name__ == "__main__":
    main()

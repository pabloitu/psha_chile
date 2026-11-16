"""Tornado row: the crustal background from the declustered fits (fits_declustered_<DATE>.csv, gk_family and
nn_family, table full, own b), a lower bound on the rates, not the model (Pablo, 16 Nov). The same join with the
faults of every database as join.py. Writes tables/background_mfd_decl_<DATE>.csv and tables/join_decl_<DATE>.csv.
"""
import pandas as pd

import background as BG
import join as J

DATE = J.DATE


def main():
    fc = J.fault_classes()
    obs, _ = J.observed()
    jt, mf = [], []
    for k in BG.DECL_ROWS:
        ft = {(c, sh): J.on(*BG.mfd(c, sh, k)) for c in BG.CLASSES for sh in BG.SHAPES}
        t, _, m = J.tables(ft, fc, obs)
        jt.append(t.assign(decl=k))
        mf.append(m.assign(decl=k))
    jt, mf = pd.concat(jt), pd.concat(mf)
    mf.to_csv(BG.TAB / f"background_mfd_decl_{DATE}.csv", index=False, float_format="%.6e")
    jt.round(6).to_csv(BG.TAB / f"join_decl_{DATE}.csv", index=False)
    x = jt[(jt["shape"] == "taper") & jt.db.isin(["A", "B", "Bmm"]) & (jt.M == 6.0)]
    with pd.option_context("display.width", 200):
        print(x.pivot_table(index=["decl", "cls"], columns="db", values="faults").div(
            x.pivot_table(index=["decl", "cls"], columns="db", values="fit")).round(2).to_string())


if __name__ == "__main__":
    main()

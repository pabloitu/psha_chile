"""Sensitivity of the fits to the pad added to the largest observed event for Mmax (tornado factor). The fits of
run.py, same catalogue, table and rules, with another pad for every unit; the corner of the tapered line follows
from Mmax by the Kagan rule. Maximum-likelihood rows only: no bootstrap, no (a, b) branches, full catalogue.
Writes tables/fits_<DATE>_pad<NN>.csv and tables/fits_<DATE>_pad_compare.csv (against the fits of run.py)."""
import numpy as np
import pandas as pd

import gr as G
import run as R
import table as TB

# settings
DATE = R.DATE
PADS = (0.0, 0.4)
REF = (5.0, 6.0, 7.0, 8.0)


def rows(d, te, pad):
    for s in R.UNITS.values():
        s["pad"] = pad
    out = []
    for sh in R.SHAPES:
        F, _ = R.fits(d, te, sh, nboot=0)
        for u in R.ORDER:
            f = F[u]
            o = dict(unit=u, name=R.name(u), shape=f["shape"], pad=pad, events=f["nev"], counted=f["n"],
                     mmax=round(f["mmax"] - G.DM / 2, 1), corner=f["corner"], b=f["b"], b_from=R.UNITS[u].get("b_from", ""),
                     a=G.a_value(f), rate_mlo=f["rate"], m_lo=f["m_lo"], steps=TB.text(R.table_of(u)))
            o.update({f"N{M:g}": float(G.n_ge(f, M)) for M in REF})
            for M in (7.0, 8.0):
                o[f"exp{M:g}"], o[f"obs{M:g}"], o[f"ok{M:g}"] = G.check(f, M)
            out.append(o)
    return pd.DataFrame(out)


def run():
    pd.set_option("display.width", 250, "display.max_columns", 40)
    d = G.load()
    d["cl"] = R.clusters(d)
    te = G.tend(d)
    ref = pd.read_csv(R.TAB / f"fits_{DATE}.csv")
    cmp = []
    for pad in PADS:
        x = rows(d, te, pad)
        x.round(5).to_csv(R.TAB / f"fits_{DATE}_pad{round(pad * 10):02d}.csv", index=False)
        m = x.merge(ref, on=["unit", "shape"], suffixes=("", "_ref"))
        cmp.append(pd.DataFrame(dict(unit=m.unit, shape=m["shape"], pad=pad, mmax=m.mmax, mmax_ref=m.mmax_ref, corner=m.corner,
                                     corner_ref=m.corner_ref, b=m.b, b_ref=m.b_ref, db=m.b - m.b_ref, r_N5=m.N5 / m.N5_ref,
                                     r_N6=m.N6 / m.N6_ref, r_N7=m.N7 / m.N7_ref, r_N8=m.N8 / m.N8_ref, ok7=m.ok7, ok7_ref=m.ok7_ref,
                                     ok8=m.ok8, ok8_ref=m.ok8_ref)))
    c = pd.concat(cmp, ignore_index=True)
    c.round(5).to_csv(R.TAB / f"fits_{DATE}_pad_compare.csv", index=False)
    print(c.round(3).to_string(index=False))


if __name__ == "__main__":
    run()

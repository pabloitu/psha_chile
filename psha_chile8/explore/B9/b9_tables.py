"""B9: candidate completeness tables. A table is a list of (magnitude from, complete since). Settings per class."""
import numpy as np
import pandas as pd

import b9_lib as L

# network history, the same for every class: CSN and Potin stable from 2000, GCMT 1976, ISC 1964, Centennial
# complete to MS 6.5 from 1930 and to 7.0 from 1900 (Engdahl and Villasenor 2002)
NETWORK = [(4.5, 2000), (5.0, 1976), (5.5, 1964), (6.5, 1930), (7.0, 1900)]
# one period, the simplest tables
RECENT = [(4.5, 2000)]
ISC = [(5.0, 1964)]
# psha_chile7/interface/config.py, cut at 4.5; reference only
OLD = [(4.8, 2002), (5.1, 1997), (5.2, 1976), (6.0, 1950), (6.8, 1900), (8.3, 1513)]
# historical steps for the large events, laid over a base table
HIST = {"none": [],
        "Lomnitz": [(7.5, 1535)],
        "counts": [(7.5, 1820), (8.0, 1730)],
        "long": [(7.0, 1819), (8.0, 1570)],
        "old": [(8.3, 1513)]}
HIST_CLASSES = ["interface", "intraslab_shallow", "intraslab_intermediate", "intraslab"]
THR = [4.5, 5.0, 5.5, 6.0, 7.0]


def data_table(cls, mode="all"):
    """Steps from the change points of the yearly counts (cache/comp_years.csv): per threshold the latest year
    over the full, Gardner-Knopoff and nearest-neighbour counts, not before 1900, never later than the step below."""
    y = pd.read_csv(L.CACHE / "comp_years.csv")
    y = y[(y.cls == cls) & (y["mode"] == mode)]
    tb, prev = [], None
    for thr in THR:
        v = y[y.thr == thr].changepoint.max()
        if not np.isfinite(v):
            continue
        v = max(int(v), 1900)
        if prev is not None and v >= prev:
            continue
        tb.append((thr, v))
        prev = v
    return tb or [(4.5, 1964)]


def with_hist(base, name):
    """Base table below 7, plus M >= 7 from 1900 and the historical steps."""
    h = HIST[name]
    tb = dict(base)
    for mf, y in h:
        for m in [m for m in tb if m >= mf - 1e-6 and tb[m] > y]:
            del tb[m]
        tb[mf] = y
    return sorted(tb.items())


def tables(cls):
    """Candidate tables of a class: name -> table."""
    src = {"intraslab": "intraslab_intermediate"}.get(cls, "interface" if cls.startswith("seg") else cls)
    out = {"network": NETWORK, "data": data_table(src), "recent": RECENT, "isc": ISC}
    if cls == "interface" or cls.startswith("seg"):
        out["old"] = OLD
    if cls in HIST_CLASSES or cls.startswith("seg"):
        for h in HIST:
            if h != "none":
                out["network+" + h] = with_hist(NETWORK, h)
                out["data+" + h] = with_hist(out["data"], h)
    return out


def text(tb):
    return ", ".join(f"{m:.1f} from {y}" for m, y in sorted(tb))

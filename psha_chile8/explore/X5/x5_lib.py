"""X5: class scores in the style of the USGS catalogue separation tool (Haynie et al. 2026), with the depth error
of each event. Exploration only: reads catalog/merged, writes to explore/X5."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "catalog"))
import classify as C  # noqa: E402

CAT = "2026-11-13e"
TAB, FIG = HERE / "tables", HERE / "figs"
MMIN = 4.5
BEST = ["gccel", "ehb1"]


def axes(strike, dip, rake):
    """T, P and B axes (north, east, down) of double couples; arrays of shape (n, 3)."""
    f, d, l = (np.radians(np.asarray(v, float)) for v in (strike, dip, rake))
    n = np.stack([-np.sin(d) * np.sin(f), np.sin(d) * np.cos(f), -np.cos(d)], -1)
    s = np.stack([np.cos(l) * np.cos(f) + np.cos(d) * np.sin(l) * np.sin(f), np.cos(l) * np.sin(f) - np.cos(d) * np.sin(l) * np.cos(f),
                  -np.sin(l) * np.sin(d)], -1)
    return (n + s) / np.sqrt(2), (n - s) / np.sqrt(2), np.cross(n, s)


def kagan(s1, d1, r1, s2, d2, r2):
    """Smallest rotation angle (degrees) that takes one double couple into another (Kagan 1991)."""
    A, B = np.stack(axes(s1, d1, r1), -1), np.stack(axes(s2, d2, r2), -1)
    out = np.full(len(A), 180.0)
    for sg in ((1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1)):
        tr = np.einsum("nij,nij->n", A, B * np.array(sg))
        out = np.minimum(out, np.degrees(np.arccos(np.clip((tr - 1) / 2, -1, 1))))
    return out


def load():
    """Catalogue geometry of classify.py plus the Kagan angle between each mechanism and a pure thrust on the Slab2
    plane at the epicentre (kag; NaN without mechanism or slab), and the skewed measure of x5_skew (em, sw, tw)."""
    c = pd.read_csv(C.OUT / f"catalog_{CAT}.csv", low_memory=False)
    g = C.geometry(c)
    g["kag"] = np.nan
    k = (c.strike1.notna() & g.top.notna()).to_numpy()
    g.loc[k, "kag"] = kagan(c.strike1[k], c.dip1[k], c.rake1[k], g.sstr[k], g.dip[k], np.full(k.sum(), 90.0))
    import x5_skew as K
    g["em"], g["sw"], g["tw"] = np.nan, np.nan, np.nan
    g.loc[k, ["em", "sw", "tw"]] = K.skew(*(v[k].to_numpy(float) for v in (c.strike1, c.dip1, c.rake1, g.sstr, g.dip))).T
    return c, g


def m45(g):
    return (g.in_domain & (g.mw >= MMIN - 0.05)).to_numpy()

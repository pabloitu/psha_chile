"""S3 step 1: fault MFDs of databases A, B (our rules) and B on the MASCSN moment (our MFD rules), per fault and per
branch of the fault tree (psi x seismogenic depth x MFD shape, DECISIONS), with the Leonard Mmax and, as a
sensitivity (variants <db>_cm), with the class maximum.

The sources come from model/faults/compare.sources (D16b): the Magallanes–Fagnano main trace is one system source, every
other row alone; class from the midpoint; b the tapered-fit b of the class (Patagonia the forearc b). The MFD of a
branch repeats model/faults/rates.source term by term, so its weighted mean is that function's result (test). In the
MASCSN-moment variant a MASCSN row carries its FaultQuake budget (their thickness and length cap) times psi in every
depth branch; the depth branch sets Mmax and the rupture width, as in compare.sources. The class-maximum sensitivity
replaces the Leonard Mmax by the background Mmax of the class. A source whose trace lies wholly outside the crustal
grid is dropped (crustal domain, DECISIONS).

Writes tables/fault_sources_<DATE>.csv, tables/fault_classes_<DATE>.csv and tables/fault_rates_<db>_<DATE>.npz.
"""
import math
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "model" / "faults"))
sys.path.append(str(ROOT / "fits"))
gpd.options.io_engine = "fiona"
import background as BG  # noqa: E402
import compare as CP  # noqa: E402
import rates as R  # noqa: E402

TAB = HERE / "tables"

# settings
# tag and inputs of background.py (CURRENT.md)
DATE = BG.DATE
FA, FB = BG.current("fault database A")[0], BG.current("fault database B")[0]
DBS = {"A": dict(file=FA, mm=False, name="A (GEM, D16)"),
       "B": dict(file=FB, mm=False, name="B, our rules"),
       "Bmm": dict(file=FB, mm=True, name="B, MASCSN moment")}
# b of the faults: the fits table of the model (pad 0.2), whatever pad background.py is switched to
FITS = BG.FITS0
# Mmax pad rows (Pablo, 16 Nov): single faults Leonard + FAULT_PAD; the class Mmax of the multi-fault cap follows
# background.CLASSES (set_pad)
FAULT_PAD = 0.0
# crustal domain (DECISIONS): a fault whose trace lies wholly outside the crustal grid is not a source (Pablo, 16 Nov)
GRID = BG.GRID
# fault models: database and Mmax rule (Leonard, or the class maximum of the sensitivity)
VARIANTS = {"A": ("A", False), "B": ("B", False), "Bmm": ("Bmm", False),
            "A_cm": ("A", True), "B_cm": ("B", True), "Bmm_cm": ("Bmm", True)}
NAMES = {**{k: v["name"] for k, v in DBS.items()}, **{k + "_cm": v["name"] + ", class-maximum Mmax" for k, v in DBS.items()}}
CLASSES = ("forearc", "arc", "backarc", "patagonia")
CLASS_MMAX = {c: BG.CLASSES[c]["mmax"] for c in CLASSES}


def class_mmax(c):
    return BG.CLASSES[c]["mmax"]


NB = 40
# seismogenic thickness of the model: 20 km in the tree and every tornado row (Pablo, 18 Nov, CR); rates.DEPTH keeps
# 10 / 20 km for the A / B comparison of model/faults
THICK = {20.0: 1.0}
BR = [(p, z, k) for p, z, k in product(R.PSI, THICK, R.SHAPES)]
W = np.array([R.PSI[p] * THICK[z] / len(R.SHAPES) for p, z, k in BR])
SYSTEM = "Magallanes–Fagnano system"


def read(db):
    f = DBS[db]["file"]
    g = gpd.read_file(f, layer="faults") if f.suffix == ".gpkg" else gpd.read_file(f)
    return g.to_crs("EPSG:4326").reset_index(drop=True)


def bvals():
    t = pd.read_csv(FITS)
    return {c: float(t[(t.unit == c) & (t["shape"] == "taper")].b.iloc[0]) for c in CLASSES}


def branch(L, dip, rake, sr, b, z, psi, k, fixed=0.0, Lsr=None, mx=None):
    """Rates on the grid MMIN + DM k of one branch, its Mmax and its moment rate (N m / yr)."""
    Lsr = L if Lsr is None else Lsr
    W_ = z / math.sin(math.radians(dip))
    mx = R.on_grid(R.leonard(L * W_, rake) + FAULT_PAD) if mx is None else mx
    mo = psi * (R.MU * Lsr * 1e3 * W_ * 1e3 * sr * 1e-3 + fixed)
    return R.grid(*R.mfd(k, b, mx, mo), NB), mx, mo


def bearing(p, q):
    lo1, la1, lo2, la2 = map(math.radians, (*p, *q))
    y = math.sin(lo2 - lo1) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(lo2 - lo1)
    return math.degrees(math.atan2(y, x)) % 360.0


def trace(x):
    """
    Trace of a source as a list of (lon, lat), dipping to its right (OpenQuake). One row: reversed where its right
    side contradicts dip_dir. Joined system: the segments ordered west to east, each run west to east, joined end
    to end (the gaps bridged by a straight line).
    """
    segs = []
    for y in x.itertuples():
        c = [p[:2] for p in y.geometry.coords]
        segs.append(c if c[0][0] <= c[-1][0] else c[::-1])
    if len(segs) > 1:
        segs.sort(key=lambda c: c[0][0])
        return [p for c in segs for p in c]
    c, y = segs[0], x.iloc[0]
    if pd.notna(y.dip_dir) and y.dip < 90:
        right = (bearing(c[0], c[-1]) + 90.0) % 360.0
        if abs((right - float(y.dip_dir) + 180.0) % 360.0 - 180.0) > 90.0:
            c = c[::-1]
    return c


def load(db, split_system=False):
    """
    Sources of a database with the rates of every branch. With split_system the Magallanes–Fagnano measured traces
    are separate sources instead of one joined system (the multi-fault row of Fagnano, Pablo, 16 Nov).

    Returns
    -------
    (DataFrame, array (n, len(BR), NB), array (n, len(BR), NB))
        Sources (compare.sources columns plus moment terms and trace), branch rates with the Leonard Mmax and with
        the class maximum (sensitivity).
    """
    f = read(db)
    b = bvals()
    if split_system:
        f = f.copy()
        f.loc[f.system == "Magallanes–Fagnano", "sr_kind"] = "split"
    s = CP.sources(f, b, mm=DBS[db]["mm"]).reset_index(drop=True)
    rr, cm, tr, fx, ls, sg = np.zeros((len(s), len(BR), NB)), np.zeros((len(s), len(BR), NB)), [], [], [], []
    for i, q in s.iterrows():
        x = f[f.fid.isin(q.fid.split("+"))]
        tr.append(trace(x))
        if DBS[db]["mm"]:
            m, g = x[x.src == "MASCSN26"], x[x.src != "MASCSN26"]
            Lg = float(g["length"].sum())
            fixed, Lsr, sr = CP.budget(m), Lg, float((g.sr * g["length"]).sum() / Lg) if Lg > 0 else 0.0
        else:
            fixed, Lsr, sr = 0.0, float(q.L), float(q.sr)
        fx.append(fixed), ls.append(Lsr), sg.append(sr)
        for j, (p, z, k) in enumerate(BR):
            rr[i, j] = branch(q.L, q.dip, q.rake, sr, b[q.cls], z, p, k, fixed, Lsr)[0]
            cm[i, j] = branch(q.L, q.dip, q.rake, sr, b[q.cls], z, p, k, fixed, Lsr, mx=CLASS_MMAX[q.cls])[0]
    s["fixed"], s["Lsr"], s["sr_used"], s["trace"] = fx, ls, sg, tr
    s["b"] = [b[c] for c in s.cls]
    s["system"] = s.name == SYSTEM
    import smooth as S
    g = pd.read_csv(GRID)
    keep = np.array([(S.cells(g.lon.to_numpy(), g.lat.to_numpy(), *np.asarray(t).T) >= 0).any() for t in s.trace])
    if (~keep).any():
        print(db, "outside the crustal grid, not sources:", ", ".join(s.fid[~keep]))
    return s[keep].reset_index(drop=True), rr[keep], cm[keep]


def n_ge(r, M):
    c = R.MMIN + R.DM * np.arange(r.shape[-1])
    return r[..., c >= M - 1e-6].sum(axis=-1)


def moment(r):
    return (r * R.m0(R.MMIN + R.DM * np.arange(r.shape[-1]))).sum(axis=-1)


def summary(db, s, rr, cm):
    """Per class and domain-wide: weighted mean, lowest and highest branch of N(>= 6, 6.5, 7) and moment, and the
    class-maximum sensitivity."""
    out = []
    for cl in CLASSES + ("all",):
        k = np.ones(len(s), bool) if cl == "all" else (s.cls == cl).to_numpy()
        tot = rr[k].sum(axis=0)
        o = dict(db=db, cls=cl, sources=int(k.sum()))
        for M, key in ((6.0, "N6"), (6.5, "N65"), (7.0, "N7")):
            v = n_ge(tot, M)
            o[key], o[key + "_lo"], o[key + "_hi"] = float(W @ v), float(v.min()), float(v.max())
            o[key + "_clsmax"] = float(W @ n_ge(cm[k].sum(axis=0), M))
        v = moment(tot)
        o["mo"], o["mo_lo"], o["mo_hi"] = float(W @ v), float(v.min()), float(v.max())
        out.append(o)
    return out


def main():
    TAB.mkdir(exist_ok=True)
    rows, srcs = [], []
    for db in DBS:
        s, rr, cm = load(db)
        mean = np.tensordot(W, rr, axes=(0, 1))
        for v, r_ in ((db, rr), (db + "_cm", cm)):
            np.savez_compressed(TAB / f"fault_rates_{v}_{DATE}.npz", rates=r_, weights=W,
                                branches=np.array([f"psi{p:g}_z{z:g}_{k}" for p, z, k in BR]), fid=s.fid.to_numpy())
        rows += summary(db, s, rr, cm)
        n6 = n_ge(rr, 6.0)
        srcs.append(pd.DataFrame({"db": db, "fid": s.fid, "name": s.name, "cls": s.cls, "L": s.L, "dip": s.dip,
                                  "rake": s.rake, "sr": s.sr_used, "b": s.b, "mmax10": s.mmax10, "mmax20": s.mmax20,
                                  "N6": n_ge(mean, 6.0), "N6_lo": n6.min(1), "N6_hi": n6.max(1), "N65": n_ge(mean, 6.5),
                                  "N7": n_ge(mean, 7.0), "mo": moment(mean), "N6_clsmax": n_ge(np.tensordot(W, cm, axes=(0, 1)), 6.0),
                                  "lon": s.lon, "lat": s.lat}))
        print(db, len(s), "sources;", int(s.system.sum()), "system source")
    t = pd.DataFrame(rows)
    t.round(6).to_csv(TAB / f"fault_classes_{DATE}.csv", index=False)
    pd.concat(srcs).round(6).to_csv(TAB / f"fault_sources_{DATE}.csv", index=False)
    with pd.option_context("display.width", 250):
        print(t[["db", "cls", "sources", "N6", "N6_lo", "N6_hi", "N65", "N7", "mo", "N6_clsmax", "N7_clsmax"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()

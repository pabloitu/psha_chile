"""Fits on the declustered catalogues (plan B12), with the code of B11 unchanged (run.py, gr.py, table.py).

For every declustered catalogue of decluster.py: the automatic completeness table (read on the declustered events
from Mw 3.5), compared with the table of the full catalogue; the fits of run.py on the declustered events (both
shapes, class weights, magnitude-error weight, event bootstrap, interface (a, b) branches) with the full-catalogue
table, and also with the declustered table where it differs at a step by more than DMAG or DYEAR; the interface
segments also with one b shared by the four segments. Mmax of every unit is that of the full catalogue. The full
catalogue goes through the same steps (method "full").

Writes tables/fits_declustered_<DATE>.csv, tables/declustered_tables_<DATE>.csv, tables/declustered_removed_<DATE>.csv,
tables/declustered_compare_<DATE>.csv, tables/declustered_floor_<DATE>.csv and figs/declustered_*.png.
"""
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

import decluster as D
import gr as G
import run as R
import table as TB

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "tables", HERE / "figs"

# settings
DATE = "2026-11-16e"
DC_DATE = D.DATE
METHODS = {"full": "full catalogue", "gk": "Gardner–Knopoff", "gk_family": "Gardner–Knopoff per family",
           "nn": "nearest neighbour", "nn_depth": "nearest neighbour, with depth",
           "nn_family": "nearest neighbour per family"}
# the declustered table is used (as well) where it differs from the full one by more than this at a step
DMAG, DYEAR = 0.2, 10
FLOORS = (5.0, 5.2, 5.4, 5.6, 5.8, 6.0)
# Fano factor of the yearly counts: magnitude from, since
FANO = [(5.0, 1976), (5.5, 1964)]
SEGS = ["seg1", "seg2", "seg3", "seg4"]
NPROC = 10


def flags(name, mmin=D.MMIN):
    f = D.OUT / (f"{name}_{DC_DATE}.csv" if mmin == D.MMIN else f"{name}_m{mmin * 10:.0f}_{DC_DATE}.csv")
    return pd.read_csv(f, usecols=["event_id", "mainshock"]).set_index("event_id").mainshock


def keep(d, name, mmin=D.MMIN):
    """Mainshock flag of every event of d (all True for the full catalogue); events below mmin are dropped."""
    if name == "full":
        return np.ones(len(d), bool)
    return d.event_id.map(flags(name, mmin)).astype("boolean").fillna(False).to_numpy(bool)


def declustered(d, k):
    """The catalogue with the class weights of the removed events set to 0."""
    x = d.copy()
    for c in [q for q in x.columns if q.startswith("W_")]:
        x[c] = x[c] * k
    return x


def years(tb, ms):
    yr, _ = G.table_years(tb, 2027.0)
    return np.array([yr[G.kbin(m)] for m in ms])


def differ(tb, ref):
    """Largest difference in years at the magnitudes of the steps of either table, and in magnitude at their years."""
    ms = sorted({m for m, _ in tb + ref})
    dy = np.abs(years(tb, ms) - years(ref, ms))
    mag = lambda t, y: min([m for m, yy in t if yy <= y], default=np.inf)
    ys = sorted({y for _, y in tb + ref})
    dm = [abs(mag(tb, y) - mag(ref, y)) for y in ys if np.isfinite(mag(tb, y)) and np.isfinite(mag(ref, y))]
    return float(np.nanmax(np.where(np.isfinite(dy), dy, np.nan))), float(max(dm))


def shared(d, te, shape, table, F):
    """Interface segments with one b: the family mean of the segment b (random effects, as B11's pooled b), in each
    bootstrap replicate the same mean of the replicate b."""
    b, s = [F[u]["b"] for u in SEGS], [np.nanstd(F[u]["bb"]) for u in SEGS]
    mu, tau2, _ = G.shrink(b, s)
    w = 1 / (np.array(s) ** 2 + tau2)
    bb = (w[:, None] * np.array([F[u]["bb"] for u in SEGS])).sum(0) / w.sum()
    out = {}
    for u in SEGS:
        f = R.fit(d, u, te, shape, table, bfix=mu, bboot=bb)
        f1 = R.fit(d, u, te, shape, table, split=False, nboot=0, bfix=mu)
        out[u] = (f, f1)
    return out, mu, np.sqrt(tau2)


def full_mmax(d):
    """Mmax of every unit from the full catalogue (a declustered catalogue may lack the largest event)."""
    for u, s in R.UNITS.items():
        if "mmax" not in s:
            s["mmax"] = round(R.observed(d, u) + s["pad"], 1)


def fit_all(a):
    """All units and shapes on one catalogue and table."""
    name, tname, table = a
    d0 = G.load()
    te = G.tend(d0)
    full_mmax(d0)
    d = declustered(d0, keep(d0, name))
    rows, F = [], {}
    for sh in ("trunc", "taper"):
        F[sh] = R.fits(d, te, sh, table)
        rows += [dict(R.row(d, u, F[sh][0][u], F[sh][1][u], te, table), b_option="own") for u in R.ORDER]
        sb, mu, tau = shared(d, te, sh, table, F["trunc"][0])
        rows += [dict(R.row(d, u, f, f1, te, table), b_option="shared", family_b=mu, family_tau=tau) for u, (f, f1) in sb.items()]
    for r in rows:
        r.update(method=name, table=tname)
    # b against the floor, line cut at Mmax
    m, t, sig = d.mw.to_numpy(), d.t.to_numpy(), d.mw_sigma.to_numpy()
    fl = []
    for u in R.ORDER:
        if R.UNITS[u].get("b_from"):
            continue
        for x in FLOORS:
            g = G.fit(m, t, R.weights(d, u), R.table_of(u, table), te, sig=sig, shape="trunc", top=R.top(d0, u), floor=x, nboot=300,
                      rng=np.random.default_rng(1))
            fl.append(dict(method=name, table=tname, unit=u, floor=x, b=g["b"], b_sd=np.nanstd(g["bb"]), n=g["n"]))
    return rows, fl


def fano(d, name):
    """Fano factor (variance over mean) of the yearly weighted counts per unit."""
    k = keep(d, name)
    m, t = d.mw.to_numpy(), d.t.to_numpy()
    te = G.tend(d)
    rows = []
    for u in R.ORDER:
        w = R.weights(d, u) * k
        for mf, y0 in FANO:
            s = (m >= mf - 1e-6) & (t >= y0) & (w > 0)
            yc = np.bincount((np.floor(t[s]) - y0).astype(int), w[s], minlength=int(te) - y0)[:int(te) - y0]
            rows.append(dict(method=name, unit=u, m_from=mf, since=y0, mean=yc.mean(), fano=yc.var() / max(yc.mean(), 1e-9)))
    return rows


def removed(d, name):
    k = keep(d, name)
    m = d.mw.to_numpy()
    rows = []
    for c in ["interface", "intraslab_shallow", "intraslab_intermediate", "jujuy_nest", "forearc", "arc", "backarc", "patagonia"]:
        w = d["W_" + c].to_numpy()
        for mf in (4.5, 5.0, 5.5, 7.0):
            s = m >= mf - 1e-6
            rows.append(dict(method=name, cls=c, m_from=mf, n=w[s].sum(), kept=(w * k)[s].sum(),
                             removed=1 - (w * k)[s].sum() / max(w[s].sum(), 1e-9)))
    return rows


def run():
    pd.set_option("display.width", 250, "display.max_columns", 40)
    d = G.load()
    te = G.tend(d)
    full_mmax(d)
    # completeness on the declustered catalogues from Mw 3.5
    tabs, todo = [], []
    for name in METHODS:
        k = keep(d, name, D.M35)
        e = d[k]
        tb, _ = TB.auto(e.mw.to_numpy(), e.t.to_numpy(), e.lat.to_numpy(), te)
        dy, dm = differ(tb, R.TABLE)
        use = name != "full" and (dy > DYEAR or dm > DMAG + 1e-6)
        tabs.append(dict(method=name, table=TB.text(tb), max_dyear=dy, max_dmag=dm, also_fitted=use))
        print(f"{name}: {TB.text(tb)} (differs by {dy:g} years, {dm:.1f} units)")
        todo.append((name, "full", R.TABLE))
        if use:
            todo.append((name, "declustered", tb))
    tabs = pd.DataFrame(tabs)
    tabs.to_csv(TAB / f"declustered_tables_{DATE}.csv", index=False)
    with Pool(min(NPROC, len(todo))) as p:
        res = p.map(fit_all, todo)
    x = pd.DataFrame([r for rows, _ in res for r in rows])
    cols = ["method", "table", "b_option"] + [c for c in x.columns if c not in ("method", "table", "b_option")]
    x = x[cols]
    x.round(5).to_csv(TAB / f"fits_declustered_{DATE}.csv", index=False)
    fl = pd.DataFrame([r for _, f in res for r in f])
    fl.round(5).to_csv(TAB / f"declustered_floor_{DATE}.csv", index=False)
    rm = pd.DataFrame([r for n in METHODS for r in removed(d, n)])
    rm.round(4).to_csv(TAB / f"declustered_removed_{DATE}.csv", index=False)
    fa = pd.DataFrame([r for n in METHODS for r in fano(d, n)])
    c = compare(x, fa)
    c.round(5).to_csv(TAB / f"declustered_compare_{DATE}.csv", index=False)
    print(c.to_string(index=False))
    import figs_declustered as F
    F.run(d, x, fl, c)


def compare(x, fa):
    """Per unit and method (tapered, own b, full-catalogue table): b, N(>= 5, 7, 8), the large-event check, and the
    Fano factors."""
    q = x[(x["shape"] == "taper") & (x.b_option == "own") & (x.table == "full")]
    q = q[["method", "unit", "name", "events", "counted", "b", "b_sd", "N5", "N7", "N7_lo", "N7_hi", "N8", "exp7", "obs7", "ok7", "exp8",
           "obs8", "ok8"]].copy()
    for mf, y0 in FANO:
        f = fa[(fa.m_from == mf) & (fa.since == y0)].set_index(["method", "unit"]).fano
        q[f"fano_{mf:g}_{y0}"] = [f.loc[(a, b)] for a, b in zip(q.method, q.unit)]
    return q


if __name__ == "__main__":
    run()

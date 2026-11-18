"""Final fits per class and interface segment (plan B11, methods of DECISIONS, Statistics).

Two shapes per unit, both fitted by maximum likelihood on the automatic completeness table (Weichert 1980 for the
line cut at Mmax; the tapered line of Kagan 2002 with its corner fixed), class weights, every event counted
exp(-beta^2 sigma^2 / 2), event bootstrap. Writes tables/fits_<DATE>.csv, tables/fits_sensitivity_<DATE>.csv (the alternatives of
compare.py), tables/table_<DATE>.csv, tables/mc_windows_<DATE>.csv and the figures of figs.py.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import gr as G
import table as TB

HERE = Path(__file__).resolve().parent
# settings
DATE = "2026-11-18"
TAB, FIG = HERE / "tables", HERE / "figs" / DATE
# paper and supplement figures (FIGURES.md), one folder per kind: completeness, fits, declustering
PAPER = HERE / "FIGURES"
# the table of the fits (DECISIONS), from the fit floor 5.0; every run also writes the table measured from Mc(t) per
# latitude segment (table.auto) and the published checks of the historical steps (FITS.md section 2)
TABLE = [(5.0, 1981), (5.1, 1964), (7.0, 1905), (7.5, 1830), (8.5, 1550)]
# instrumental steps of each interface segment, from the Mc(t) of the segment (table.SEG); historical steps as TABLE
SEG_INST = {"seg4": [(5.0, 1964)], "seg3": [(5.0, 1976), (5.2, 1964)], "seg2": [(5.0, 1964)], "seg1": [(5.0, 1999), (5.2, 1964)]}
SEG_MC = {"seg4": "north", "seg3": "central-north", "seg2": "central", "seg1": "south"}
NBOOT = 2000
REF = (5.0, 6.0, 7.0, 8.0)
# shapes fitted for every unit: tapered (preferred) and cut at Mmax
SHAPES = ("taper", "trunc")
# interface (a, b) branches: percentiles of N(>= controlling M) and their weights; controlling M capped at Mmax - 0.3.
# The pair of a branch is the mean of (a, b) given that rate, from the bootstrap covariance of (a, b)
AB_PCT, AB_W, AB_M = (5, 95), (0.185, 0.63, 0.185), 8.8
BPOS = dict(since=1976, floor=5.0, dmc=0.2)
# the largest observed event of a unit is taken among the events that belong to it for certain (class weight 1)
MMAX_W = 1.0
# the bootstrap draws whole clusters of this declustering (decluster.py, same DATE as its files)
CLUSTER = "nn_family"

# units: class of the weights, latitude band of the epicentre, pad added to the observed maximum for Mmax, b taken
# from another unit. One rule for every unit (DECISIONS, Statistics): Mmax = largest observed event + 0.2; the corner
# of the tapered line from Mmax and the b of the unit (Kagan 2002b, eq. 12)
# interface: the margin and the four segments
UNITS = {"interface": dict(cls="interface", pad=0.2, family="interface"),
         "seg1": dict(cls="interface", lat=(-45.6, -37.0), pad=0.2, name="interface, 45.6–37° S", family="segments"),
         "seg2": dict(cls="interface", lat=(-37.0, -32.0), pad=0.2, name="interface, 37–32° S", family="segments"),
         "seg3": dict(cls="interface", lat=(-32.0, -26.0), pad=0.2, name="interface, 32–26° S", family="segments"),
         "seg4": dict(cls="interface", lat=(-26.0, -17.6), pad=0.2, name="interface, 26–17.6° S", family="segments")}
# in-slab: Mmax observed maximum + 0.2; fitted from 1964 only (ISC Bulletin start; the deep Abe (1982) Mw of 1905-1963 run 0.36 high; DECISIONS, Statistics)
UNITS.update({c: dict(cls=c, pad=0.2, since=1964, family="in-slab") for c in ("intraslab_shallow", "intraslab_intermediate", "jujuy_nest")})
# crustal: the same Mmax rule (the largest event of any year). One b for the four classes, that of the crustal
# family fitted as one unit (all crustal weight together); each class its own rate.
# The crustal classes are fitted on the steps of the table from 1976 on only: 1964-1975 is short of events at
# Mw 5.5-5.9 in these classes, and the historical steps rest on one or two events in regions with no early record
CRUSTAL = ("forearc", "arc", "backarc", "patagonia")
UNITS["crustal"] = dict(cls="crustal", classes=CRUSTAL, pad=0.2, since=1976, name="crustal, all classes", family="crustal family")
UNITS.update({c: dict(cls=c, pad=0.2, since=1976, b_from="crustal", family="crustal") for c in CRUSTAL})
ORDER = ["interface", "seg1", "seg2", "seg3", "seg4", "intraslab_shallow", "intraslab_intermediate", "jujuy_nest", "forearc",
         "arc", "backarc", "patagonia", "crustal"]


def name(u):
    sys.path.insert(0, str(HERE.parent))
    import palette as P
    return UNITS[u].get("name") or P.CLASS_NAME[UNITS[u]["cls"]]


def weights(d, u, split=True):
    """Class weight of every event in a unit; split=False keeps the events with weight 1 only."""
    s = UNITS[u]
    w = sum(d["W_" + c].to_numpy() for c in s.get("classes", (s["cls"],))).copy()
    if "lat" in s:
        w *= ((d.lat >= s["lat"][0]) & (d.lat < s["lat"][1])).to_numpy()
    return w if split else np.where(w >= 0.999, 1.0, 0.0)


def observed(d, u):
    return round(float(d.mw[weights(d, u) >= MMAX_W - 1e-3].max()), 1)


def top(d, u):
    """First magnitude bin above the Mmax of the unit."""
    s = UNITS[u]
    return round((s["mmax"] if "mmax" in s else observed(d, u) + s["pad"]) + G.DM, 1)


def clusters(d):
    """Cluster of every event from the CLUSTER file of decluster.py (an event not in it is its own cluster)."""
    import decluster as D
    c = pd.read_csv(D.OUT / f"{CLUSTER}_{D.DATE}.csv", usecols=["event_id", "cluster"]).set_index("event_id").cluster
    return pd.factorize(d.event_id.map(c).fillna(d.event_id))[0]


def table_of(u, table=None):
    """The completeness table of a unit: TABLE (an interface segment with its own instrumental steps, SEG_INST), or the
    table given; every year moved to the unit's `since` year at the earliest."""
    if table is None:
        table = TABLE if u not in SEG_INST else SEG_INST[u] + [q for q in TABLE if q[1] < TB.HIST_FROM]
    y0 = UNITS[u].get("since")
    if y0 is None:
        return list(table)
    tb = []
    for mf, y in sorted(table):
        if not tb or max(y, y0) < tb[-1][1]:
            tb.append((mf, max(y, y0)))
    return tb


def corner(d, u, b):
    """Corner of the tapered line: the moment rate of the line cut at Mmax with the same b."""
    return round(float(G.kagan_corner(top(d, u) - G.DM / 2, b)), 3)


def fit(d, u, te, shape="taper", table=None, done=None, split=True, nboot=NBOOT, own_b=False, **kw):
    """Fit of a unit with one shape; `done` holds the fits already made (for a b taken from another unit)."""
    s = UNITS[u]
    if shape == "taper" and "corner" not in kw:
        kw["corner"] = corner(d, u, fit(d, u, te, "trunc", table, done, split, 0, own_b, **kw)["b"])
    if "b_from" in s and not own_b:
        r = done[s["b_from"]]
        kw.update(bfix=r["b"], bboot=r.get("bb") if nboot else None)
    return G.fit(d.mw.to_numpy(), d.t.to_numpy(), weights(d, u, split), table_of(u, table), te, sig=d.mw_sigma.to_numpy(), shape=shape,
                 top=top(d, u), nboot=nboot, rng=np.random.default_rng(1), cl=d["cl"].to_numpy() if "cl" in d else None, **kw)


def row(d, u, f, f1, te, table=None):
    """Every number of one unit and shape: f the fit on all events, f1 on the events with weight 1."""
    q = G.boot(f)
    a, aa = G.a_value(f), G.a_value(q)
    c = np.cov(np.c_[aa, q["b"]][np.isfinite(q["b"])].T)
    o = dict(unit=u, name=name(u), shape=f["shape"], events=f["nev"], counted=f["n"], mmax=round(f["mmax"] - G.DM / 2, 1),
             corner=f["corner"], b=f["b"], b_sd=np.nanstd(q["b"]), b_from=UNITS[u].get("b_from", ""), a=a, a_sd=np.sqrt(c[0, 0]),
             var_a=c[0, 0], var_b=c[1, 1], cov_ab=c[0, 1], corr_ab=c[0, 1] / np.sqrt(c[0, 0] * c[1, 1]) if c[1, 1] > 0 else np.nan,
             rate_mlo=f["rate"], m_lo=f["m_lo"], steps=TB.text(table_of(u, table)))
    for M in REF:
        v = G.n_ge(q, M)
        o[f"N{M:g}"] = G.n_ge(f, M)
        o[f"N{M:g}_lo"], o[f"N{M:g}_hi"] = np.nanpercentile(v, [5, 95])
    for M in (7.0, 8.0):
        o[f"exp{M:g}"], o[f"obs{M:g}"], o[f"ok{M:g}"] = G.check(f, M)
        o[f"phi{M:g}"] = G.dispersion(f, M)
    m, t = d.mw.to_numpy(), d.t.to_numpy()
    if not UNITS[u].get("b_from"):
        o["b_kijko"] = G.kijko_smit(m, t, f["w"], table_of(u, table), te)
        s = (t >= BPOS["since"]) & (m >= BPOS["floor"] - 1e-6) & (f["w"] > 0)
        o["b_positive"], o["n_pairs"] = G.bpositive(m[s], f["w"][s], BPOS["dmc"])
    if UNITS[u]["cls"] == "interface":
        # log10 N(>= M) = a - b (M - DM / 2) + a term of the shape: its variance and the (a, b) to expect at its
        # percentile follow from the covariance of (a, b)
        mc = round(min(AB_M, f["mmax"] - G.DM / 2 - 0.3), 1)
        g = np.array([1.0, -(mc - G.DM / 2)])
        sd = np.sqrt(g @ c @ g)
        o["ab_M"], o["ab_sd_logN"] = mc, sd
        for p in AB_PCT:
            da, db = stats.norm.ppf(p / 100) * (c @ g) / sd
            o[f"a_p{p:02d}"], o[f"b_p{p:02d}"] = a + da, f["b"] + db
            o[f"Nctrl_p{p:02d}"] = float(G.n_ge(branch(f, a + da, f["b"] + db), mc))
        o["Nctrl_ml"] = float(G.n_ge(f, mc))
    # weight-1 events only
    o.update(events_w1=f1["nev"], b_w1=f1["b"], a_w1=G.a_value(f1), **{f"N{M:g}_w1": float(G.n_ge(f1, M)) for M in REF})
    return o


def branch(f, a, b):
    """The fit with another (a, b)."""
    r = 10 ** (a - b * f["m_lo"])
    return dict(f, b=b, rate=r * (1 - 10 ** (-b * (f["mmax"] - f["m_lo"]))) if f["shape"] == "trunc" else r)


def fits(d, te, shape="taper", table=None, nboot=NBOOT, **kw):
    F, F1 = {}, {}
    for u in sorted(ORDER, key=lambda q: "b_from" in UNITS[q]):
        F[u] = fit(d, u, te, shape, table, F, nboot=nboot, **kw)
        F1[u] = fit(d, u, te, shape, table, F1, split=False, nboot=0, **kw)
    return {u: F[u] for u in ORDER}, {u: F1[u] for u in ORDER}


def run():
    import compare as C
    import figs
    pd.set_option("display.width", 300, "display.max_columns", 60)
    TAB.mkdir(exist_ok=True), FIG.mkdir(parents=True, exist_ok=True)
    d = G.load()
    d["cl"] = clusters(d)
    te = G.tend(d)
    tb, ms, mc = TB.auto(d.mw.to_numpy(), d.t.to_numpy(), d.lat.to_numpy(), te)
    ck = TB.checks(d.mw.to_numpy(), d.t.to_numpy(), te)
    inst = lambda q: sorted(x for x in q if x[1] >= TB.HIST_FROM)
    print("measured Mc steps:", {k: TB.text(v) for k, v in ms.items()})
    print("automatic historical:", TB.text([q for q in tb if q[1] < TB.HIST_FROM]), "| table of the fits:", TB.text(TABLE))
    print(ck.to_string(index=False))
    assert TB.cut(ms["margin"]) == inst(TABLE), "the measured margin steps are not those of TABLE"
    for u, k in SEG_MC.items():
        assert TB.cut(ms[k]) == sorted(SEG_INST[u]), f"the measured steps of {k} are not those of SEG_INST[{u}]"
    pd.DataFrame([dict(series=k, mw_from=a, complete_since=b) for k, v in ms.items() for a, b in v]).to_csv(TAB / f"mc_table_{DATE}.csv",
                                                                                                            index=False)
    mc.to_csv(TAB / f"mc_series_{DATE}.csv", index=False)
    pd.DataFrame(sorted(TABLE), columns=["mw_from", "complete_since"]).to_csv(TAB / f"table_{DATE}.csv", index=False)
    ck.assign(automatic=[min((y for q, y in tb if q <= b + 1e-6), default=np.nan) for b in ck.mw_from],
              table=[min((y for q, y in TABLE if q <= b + 1e-6), default=np.nan) for b in ck.mw_from]).to_csv(
        TAB / f"table_checks_{DATE}.csv", index=False)
    F = {sh: fits(d, te, sh) for sh in SHAPES}
    x = pd.DataFrame([row(d, u, F[sh][0][u], F[sh][1][u], te) for sh in SHAPES for u in ORDER])
    x.round(5).to_csv(TAB / f"fits_{DATE}.csv", index=False)
    print(x[["unit", "shape", "events", "counted", "mmax", "corner", "b", "b_sd", "a", "a_sd", "corr_ab", "N5", "N6", "N7", "N8"]].round(3).to_string(index=False))
    print(x[["unit", "shape", "exp7", "obs7", "ok7", "exp8", "obs8", "ok8", "b_w1", "N5_w1", "N7_w1", "a_p05", "b_p05", "a_p95", "b_p95"]].round(3).to_string(index=False))
    s = C.real(d, te, F)
    s.round(5).to_csv(TAB / f"fits_sensitivity_{DATE}.csv", index=False)
    figs.run(d, te, F, x, s)
    figs.P.apply()
    figs.fig_mc(mc, te)
    figs.fig_historical(G.load(mlow=6.95), te)


if __name__ == "__main__":
    run()

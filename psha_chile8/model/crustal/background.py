"""S3 step 2: smoothed background per crustal class.

Pattern: the declustered catalogue (both options of the declustering factor), complete events as rates (class weight
over the completeness period of the magnitude), Helmstetter et al. (2007) kernel, exponent 1.5. n per class: the S-test
log-likelihood on one split (before 2010 against 2010 to the end of the catalogue) scored at CANDS, n the first local
maximum from N_MIN; each class its own n, Patagonia fixed (CLASSES). The crustal family is scored for reference only.
The final pattern uses every complete declustered event, normalised to 1 over the grid. Rates: the full-catalogue fits
(CURRENT.md), both shapes, as evenly discretised lists from gr.rates, min_mag the first bin centre. Inputs from
CURRENT.md; DATE tags the outputs of this build.

Writes tables/calibration_<DATE>.csv, tables/kernel_n_<DATE>.csv, tables/pattern_<option>_<DATE>.csv (figures: figs_s3.py).
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.append(str(ROOT / "fits"))
import gr  # noqa: E402
import smooth as S  # noqa: E402

TAB, FIG = HERE / "tables", HERE / "figs"

def current(row, sec=None):
    """Paths named in backticks in the "current" column of a row of CURRENT.md, under section `sec` if given (a bare
    file name sits in the folder of the first; a `*` is kept for the caller to fill)."""
    ls = (ROOT / "CURRENT.md").read_text().splitlines()
    if sec:
        ls = ls[next(i for i, x in enumerate(ls) if x.startswith(f"## {sec}")):]
    ln = next(x for x in ls if x.startswith(f"| {row} |"))
    f = [x for x in re.findall(r"`([^`]+)`", ln.split("|")[2]) if "/" in x or "." in x]
    p = [ROOT / f[0]]
    return p + [ROOT / x if "/" in x else p[0].parent / x for x in f[1:]]


# settings
# tag of this build: tables, pkl caches (mfsource.py) and the NRML folder (build.py)
DATE = "2026-11-18b"
# inputs, read from CURRENT.md at import (CLAUDE.md)
CAT = current("catalogue the fits and models are built on")[0]
FITS0 = FITS = current("fits, full catalogue")[0]
DECL_FITS = current("fits, declustered")[0]
GRID = current("crustal grid")[0]
NPD = current("nodal planes, all classes")[0]
DECL_M = {"gk": "gk_family", "nn": "nn_family"}
DECL = {k: Path(str(current("declustered catalogues")[0]).replace("*", m)) for k, m in DECL_M.items()}
# one declustering algorithm for the pattern, no GK / NN branch (DECISIONS, Logic tree, 17 Nov); DC is a placeholder
# until the team chooses, the other pattern is a tornado row
DC = "nn"
W_DECL = {k: float(k == DC) for k in DECL}
# Mmax pad tornado rows (DECISIONS, 16 Nov): pad 0.0 and 0.4 against the 0.2 of the main table; set_pad() switches
# the fits table and the class Mmax
PAD = 0.2
_p = current("Mmax pad 0.0 / 0.4")[0]
PAD_FITS = {0.0: _p, 0.4: Path(str(_p).replace("_pad00", "_pad04"))}
# tornado row (Pablo, 16 Nov): background from the declustered fits, a lower bound on the rates, not the model
DECL_ROWS = {k: dict(method=m, table="full", b_option="own") for k, m in DECL_M.items()}
SPLIT = 2010.0
# n scored at all candidates, chosen as the first local maximum from N_MIN up (DECISIONS, S2 rule, 16 Nov)
CANDS = (1, 3, 5, 10, 15, 25, 50, 100)
N_MIN = 5
# exponent fixed at Helmstetter et al. (2007), 1.5 (Pablo, 15 Nov, after the joint search of n and exponent)
EXPS = (1.5,)
# first bin of the background lists: the lowest crustal source Mmin considered (4.9 or 5.0, DECISIONS, 17 Nov;
# build.MMIN_SRC); the fits start at 5.0, the 4.9 bin is the fitted line one bin down
MMIN = 4.9
SHAPES = ("taper", "trunc")
# crustal classes; Mmax from the fits (largest weight-1 event + pad, set_pad); n: each class its own calibrated n
# (Pablo, 16 Nov: only b pools); Patagonia fixed at the floor (9-12 test events)
CLASSES = {"forearc": {}, "arc": {}, "backarc": {}, "patagonia": dict(n=5)}


def set_pad(pad):
    """Switch the fits table and the class Mmax to the Mmax pad `pad` (0.0, 0.2 or 0.4); returns the fits path."""
    global PAD, FITS
    PAD = pad
    FITS = PAD_FITS.get(pad, FITS0)
    t = pd.read_csv(FITS)
    for c in CLASSES:
        CLASSES[c]["mmax"] = float(t[(t.unit == c) & (t["shape"] == "taper")].mmax.iloc[0])
    return FITS


def steps():
    """Completeness steps (m, year) of the crustal fits rows, one table for every class (stops if they differ)."""
    t = pd.read_csv(FITS0)
    s = set(t[t.unit.isin(list(CLASSES))].steps)
    assert len(s) == 1, s
    return [(float(m), float(y)) for m, y in (x.split(" from ") for x in s.pop().split(", "))]


set_pad(PAD)
# completeness steps of the crustal classes, as fitted (DECISIONS, Statistics; from 1976 on)
TABLE = steps()
# the tapered list ends this far above Mmax, its last bin carrying the rate of the line above (DECISIONS, Statistics)
TAPER_END = 0.2


def npds():
    t = pd.read_csv(NPD)
    return {c: t[t["class"] == c][["weight", "strike", "dip", "rake"]].to_numpy() for c in CLASSES}


def mix(w, nd):
    """Nodal planes of a cell: the class distributions weighted by w (class rates there), probabilities in 1e-4."""
    ps = np.concatenate([w[i] / w.sum() * nd[c][:, 0] for i, c in enumerate(CLASSES)])
    pl = np.concatenate([nd[c][:, 1:] for c in CLASSES])
    q = np.floor(ps * 1e4).astype(int)
    q[np.argmax(ps)] += 10000 - q.sum()
    k = q > 0
    return [(f"{a / 1e4:.4f}", s, d, r) for a, (s, d, r) in zip(q[k], pl[k])]


def events():
    """Crustal events of the frozen catalogue from Mw 4.5 with class weights, completeness flag and the mainshock
    flag of each declustering option."""
    d = gr.load(CAT, mlow=4.5)
    yr, _ = gr.table_years(TABLE, gr.tend(d))
    d = d[d[[f"W_{c}" for c in CLASSES]].sum(axis=1) > 0].copy()
    k = gr.kbin(d.mw)
    ok = (k >= 0) & (k < yr.size)
    ok[ok] = d.t.to_numpy()[ok] >= yr[k[ok]]
    d["complete"] = ok
    d["yc"] = np.where(ok, yr[np.clip(k, 0, yr.size - 1)], np.nan)
    d.attrs["tend"] = gr.tend(gr.load(CAT))
    for m, f in DECL.items():
        x = pd.read_csv(f)
        d[f"keep_{m}"] = d.event_id.isin(set(x.event_id[x.mainshock]))
    return d.reset_index(drop=True)


def grid():
    return pd.read_csv(GRID)[["lon", "lat"]]


def sel(d, c, m, t0=-np.inf, t1=np.inf, until=None):
    """(lon, lat, w) of the complete declustered events of class c (c 'crustal': all four classes) in [t0, t1). With
    `until`, w is a rate: the class weight over the completeness period of the event's magnitude, until - T_c(m)."""
    w = d[[f"W_{k}" for k in CLASSES]].sum(axis=1) if c == "crustal" else d[f"W_{c}"]
    s = d.complete & d[f"keep_{m}"] & (w > 0) & (d.t >= t0) & (d.t < t1)
    w = w[s].to_numpy()
    if until is not None:
        w = w / (until - d.yc[s].to_numpy())
    return d.lon[s].to_numpy(), d.lat[s].to_numpy(), w


def calibration(d, g):
    """Log-likelihood against n per class, the crustal family and declustering option, and the n used per class."""
    rows, pick = [], []
    gl, ga = g.lon.to_numpy(), g.lat.to_numpy()
    e = EXPS[0]
    for m in DECL:
        for c in list(CLASSES) + ["crustal"]:
            tr, ts = sel(d, c, m, t1=SPLIT, until=SPLIT), sel(d, c, m, t0=SPLIT)
            idx = S.cells(gl, ga, ts[0], ts[1])
            uni = S.loglik(np.ones(len(g)), idx, ts[2])
            for n, ll in S.calibrate(tr, ts, gl, ga, CANDS, power=e):
                rows.append(dict(option=m, unit=c, n=n, exponent=e, loglik=ll, gain_uniform=ll - uni,
                                 train_events=len(tr[2]), test=ts[2].sum(), test_events=len(ts[2]),
                                 test_outside=float(ts[2][idx < 0].sum())))
    t = pd.DataFrame(rows)
    for (m, c), q in t.groupby(["option", "unit"]):
        r = q[q.n >= N_MIN]
        t.loc[q.index, "best"] = q.n == S.first_max(r.n, r.loglik)
        t.loc[q.index, "best_all"] = q.n == S.first_max(q.n, q.loglik)
        t.loc[q.index, "dloglik"] = q.loglik - q.loglik.max()
    for m in DECL:
        fam = int(t[(t.option == m) & (t.unit == "crustal") & t.best].n.iloc[0])
        for c in CLASSES:
            q = t[(t.option == m) & (t.unit == c)]
            own = int(q[q.best].n.iloc[0])
            n = CLASSES[c].get("n", own)
            lon, lat, _ = sel(d, c, m, t1=SPLIT)
            pick.append(dict(option=m, unit=c, test=q.test.iloc[0], n_own=own, n_all=int(q[q.best_all].n.iloc[0]),
                             n_family=fam, n=n, exponent=e, source="fixed" if "n" in CLASSES[c] else "own",
                             median_d_train=float(np.median(S.radii(lon, lat, n)))))
    return t, pd.DataFrame(pick)


def patterns(d, g, pick):
    """Final pattern per option and class (all complete declustered events), each summing to 1 over the grid."""
    out = {}
    for m in DECL:
        p = g.copy()
        for c in CLASSES:
            lon, lat, w = sel(d, c, m, until=d.attrs["tend"])
            k = pick[(pick.option == m) & (pick.unit == c)].iloc[0]
            f = S.field(S.dist(lon, lat, p.lon, p.lat), w, S.radii(lon, lat, int(k.n)), power=float(k.exponent))
            p[c] = f / f.sum()
        out[m] = p
    return out


def outside(d, g, pick):
    """
    How much of each final pattern the grid pulls in: the same field on a grid extended to the whole box
    (lon -80 to -60, the grid's latitudes, same nodes), the share of it that falls outside the crustal grid, and the
    share inside the eastern 0.5 degrees of the grid with and without the extension.
    """
    lo = np.round(np.arange(-80.04, -59.95, 0.1), 3)
    la = np.round(np.arange(g.lat.min(), g.lat.max() + 1e-6, 0.1), 3)
    X, Y = np.meshgrid(lo, la)
    x = pd.DataFrame({"lon": X.ravel(), "lat": Y.ravel()})
    ing = S.cells(g.lon.to_numpy(), g.lat.to_numpy(), x.lon.to_numpy(), x.lat.to_numpy()) >= 0
    east = g.groupby(np.round(g.lat, 3)).lon.transform("max")
    edge_g = (g.lon >= east - 0.5).to_numpy()
    rows = []
    for m in DECL:
        for c in CLASSES:
            lon, lat, w = sel(d, c, m, until=d.attrs["tend"])
            k = pick[(pick.option == m) & (pick.unit == c)].iloc[0]
            h = S.radii(lon, lat, int(k.n))
            fx = S.field(S.dist(lon, lat, x.lon, x.lat), w, h, power=float(k.exponent))
            fg = S.field(S.dist(lon, lat, g.lon, g.lat), w, h, power=float(k.exponent))
            i = S.cells(g.lon.to_numpy(), g.lat.to_numpy(), lon, lat)
            gi = S.cells(x.lon.to_numpy(), x.lat.to_numpy(), g.lon.to_numpy(), g.lat.to_numpy())
            rows.append(dict(option=m, unit=c, events_outside=float(w[i < 0].sum() / w.sum()),
                             mass_outside=float(fx[~ing].sum() / fx.sum()),
                             edge_share_grid=float(fg[edge_g].sum() / fg.sum()),
                             edge_share_extended=float(fx[gi[edge_g]].sum() / fx.sum())))
    return pd.DataFrame(rows)


def fit(c, shape, decl=None):
    """The fit of a class as a gr dict (mmax the upper edge of the last bin); with decl, the declustered fit of that
    option (DECL_ROWS)."""
    t = pd.read_csv(FITS if decl is None else DECL_FITS)
    s = (t.unit == c) & (t["shape"] == shape)
    for k, v in (DECL_ROWS[decl].items() if decl else ()):
        s &= t[k] == v
    assert s.sum() == 1, (c, shape, decl)
    r = t[s].iloc[0]
    return dict(shape=shape, b=float(r.b), rate=float(r.rate_mlo), m_lo=float(r.m_lo), mmax=float(r.mmax) + gr.DM / 2,
                corner=float(r.corner) if shape == "taper" else None, row=r)


def mfd(c, shape, decl=None):
    """
    Evenly discretised list of the class fit from MMIN: bin centres and yearly rates. The cut line ends at Mmax; the
    tapered line at Mmax + TAPER_END, its last bin carrying the whole rate of the line from that bin up.
    """
    f = fit(c, shape, decl)
    m = gr.centres()
    top = round(f["mmax"] - gr.DM / 2 + (TAPER_END if shape == "taper" else 0.0), 2)
    s = (m >= MMIN - 1e-6) & (m <= top + 1e-6)
    r = gr.rates(f)[s]
    if shape == "taper":
        r[-1] = float(gr.n_ge(f, top))
    return np.round(m[s], 2), r


def main():
    TAB.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    for c, s in CLASSES.items():
        assert abs(fit(c, "trunc")["mmax"] - gr.DM / 2 - s["mmax"]) < 1e-6, c
    d, g = events(), grid()
    cal, pick = calibration(d, g)
    cal.round(4).to_csv(TAB / f"calibration_{DATE}.csv", index=False)
    pick.to_csv(TAB / f"kernel_n_{DATE}.csv", index=False)
    with pd.option_context("display.width", 200):
        print(cal.pivot_table(index=["option", "unit"], columns="n", values="dloglik").round(1).to_string())
        print(pick.to_string(index=False))
    pats = patterns(d, g, pick)
    for m, p in pats.items():
        p.to_csv(TAB / f"pattern_{m}_{DATE}.csv", index=False, float_format="%.6e")
    o = outside(d, g, pick)
    o.round(4).to_csv(TAB / f"grid_outside_{DATE}.csv", index=False)
    print(o.round(3).to_string(index=False))


if __name__ == "__main__":
    main()

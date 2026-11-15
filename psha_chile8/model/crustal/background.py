"""S3 step 2: smoothed background per crustal class.

Pattern: the declustered catalogue (both options of the declustering factor), events complete in the table of
DECISIONS, equal event weights times the class weight, Helmstetter et al. (2007) kernel with n and the exponent
calibrated together per class (Pablo, 15 Nov) on one train / test split (before 2010-01-01 against 2010 to the end of the catalogue, CSEP S-test log-likelihood); a class
with fewer than MIN_TEST weighted test events takes the (n, exponent) of the crustal family (the four classes together). The final
pattern uses every complete declustered event, normalised to 1 over the grid. Rates: the full-catalogue fits
(fits_2026-11-15b.csv), both shapes, as evenly discretised lists from gr.rates, min_mag the first bin centre.

Writes tables/calibration_<DATE>.csv, tables/kernel_n_<DATE>.csv, tables/pattern_<option>_<DATE>.csv and
figs/background_N5_<DATE>.png.
"""
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

# settings
DATE = "2026-11-15"
GRID = ROOT / "data" / f"crustal_grid_01_{DATE}.csv"
FITS = ROOT / "fits" / "tables" / f"fits_{DATE}b.csv"
DECL = {"gk": ROOT / "catalog" / "declustered" / f"gk_family_{DATE}.csv",
        "nn": ROOT / "catalog" / "declustered" / f"nn_family_{DATE}.csv"}
W_DECL = {"gk": 0.5, "nn": 0.5}
TABLE = [(5.0, 1976), (5.2, 1964), (7.0, 1905), (7.5, 1830), (8.0, 1500)]
SPLIT = 2010.0
CANDS = (5, 10, 15, 25, 50, 100)
# exponent fixed at Helmstetter et al. (2007), 1.5 (Pablo, 15 Nov, after the joint search of n and exponent)
EXPS = (1.5,)
MIN_TEST = 20.0
MMIN = 5.0
SHAPES = ("taper", "trunc")
# crustal classes: Mmax of DECISIONS (observed maximum + 0.2), checked against the fit table
CLASSES = {"forearc": dict(mmax=7.4), "arc": dict(mmax=7.9), "backarc": dict(mmax=7.7), "patagonia": dict(mmax=8.0)}
# the tapered list ends this far above Mmax, its last bin carrying the rate of the line above (DECISIONS, Statistics)
TAPER_END = 0.2


def events():
    """Crustal events of the frozen catalogue from Mw 4.5 with class weights, completeness flag and the mainshock
    flag of each declustering option."""
    d = gr.load(mlow=4.5)
    yr, _ = gr.table_years(TABLE, gr.tend(d))
    d = d[d[[f"W_{c}" for c in CLASSES]].sum(axis=1) > 0].copy()
    k = gr.kbin(d.mw)
    ok = (k >= 0) & (k < yr.size)
    ok[ok] = d.t.to_numpy()[ok] >= yr[k[ok]]
    d["complete"] = ok
    for m, f in DECL.items():
        x = pd.read_csv(f)
        d[f"keep_{m}"] = d.event_id.isin(set(x.event_id[x.mainshock]))
    return d.reset_index(drop=True)


def grid():
    return pd.read_csv(GRID)[["lon", "lat"]]


def sel(d, c, m, t0=-np.inf, t1=np.inf):
    """(lon, lat, w) of the complete declustered events of class c (c 'crustal': all four classes) in [t0, t1)."""
    w = d[[f"W_{k}" for k in CLASSES]].sum(axis=1) if c == "crustal" else d[f"W_{c}"]
    s = d.complete & d[f"keep_{m}"] & (w > 0) & (d.t >= t0) & (d.t < t1)
    return d.lon[s].to_numpy(), d.lat[s].to_numpy(), w[s].to_numpy()


def calibration(d, g):
    """Log-likelihood against (n, exponent) per class, family and declustering option, and the pair used per class."""
    rows, pick = [], []
    for m in DECL:
        best = {}
        for c in list(CLASSES) + ["crustal"]:
            tr, ts = sel(d, c, m, t1=SPLIT), sel(d, c, m, t0=SPLIT)
            idx = S.cells(g.lon.to_numpy(), g.lat.to_numpy(), ts[0], ts[1])
            sc = [(n, e, ll) for e in EXPS for n, ll in S.calibrate(tr, ts, g.lon.to_numpy(), g.lat.to_numpy(), CANDS, power=e)]
            top = max(sc, key=lambda q: q[2])
            uni = S.loglik(np.ones(len(g)), idx, ts[2])
            best[c] = (top[:2], ts[2].sum(), np.median(S.radii(tr[0], tr[1], top[0])))
            for n, e, ll in sc:
                rows.append(dict(option=m, unit=c, n=n, exponent=e, loglik=ll, dloglik=ll - top[2],
                                 gain_uniform=ll - uni, train=tr[2].sum(), train_events=len(tr[2]), test=ts[2].sum(),
                                 test_events=len(ts[2]), test_outside=float(ts[2][idx < 0].sum())))
        for c in CLASSES:
            own = best[c][1] >= MIN_TEST
            n, e = best[c][0] if own else best["crustal"][0]
            pick.append(dict(option=m, unit=c, test=best[c][1], n_own=best[c][0][0], exp_own=best[c][0][1], n=n, exponent=e,
                             source="own" if own else "crustal family", median_d_train=best[c][2]))
    return pd.DataFrame(rows), pd.DataFrame(pick)


def patterns(d, g, pick):
    """Final pattern per option and class (all complete declustered events), each summing to 1 over the grid."""
    out = {}
    for m in DECL:
        p = g.copy()
        for c in CLASSES:
            lon, lat, w = sel(d, c, m)
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
            lon, lat, w = sel(d, c, m)
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


def fit(c, shape):
    """The fit of a class as a gr dict (mmax the upper edge of the last bin)."""
    t = pd.read_csv(FITS)
    r = t[(t.unit == c) & (t["shape"] == shape)].iloc[0]
    return dict(shape=shape, b=float(r.b), rate=float(r.rate_mlo), m_lo=float(r.m_lo), mmax=float(r.mmax) + gr.DM / 2,
                corner=float(r.corner) if shape == "taper" else None, row=r)


def mfd(c, shape):
    """
    Evenly discretised list of the class fit from MMIN: bin centres and yearly rates. The cut line ends at Mmax; the
    tapered line at Mmax + TAPER_END, its last bin carrying the whole rate of the line from that bin up.
    """
    f = fit(c, shape)
    m = gr.centres()
    top = round(f["mmax"] - gr.DM / 2 + (TAPER_END if shape == "taper" else 0.0), 2)
    s = (m >= MMIN - 1e-6) & (m <= top + 1e-6)
    r = gr.rates(f)[s]
    if shape == "taper":
        r[-1] = float(gr.n_ge(f, top))
    return np.round(m[s], 2), r


def maps(pats, fname):
    """N(>= 5) per class and declustering option, tapered fits."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(ROOT))
    import palette as P
    P.apply()
    f, ax = plt.subplots(2, 4, figsize=(15, 13), sharex=True, sharey=True)
    names = {"gk": "Gardner–Knopoff", "nn": "nearest neighbour"}
    for i, m in enumerate(pats):
        p = pats[m]
        for j, c in enumerate(CLASSES):
            n5 = mfd(c, "taper")[1].sum() * p[c].to_numpy()
            a = ax[i, j]
            sc = a.scatter(p.lon, p.lat, c=np.log10(np.maximum(n5, 1e-9)), s=1.2, cmap="magma_r", vmin=-6.5, vmax=-1.5,
                           rasterized=True)
            a.set_aspect(1 / np.cos(np.radians(37)))
            a.set_title(f"{P.CLASS_NAME[c]}\n{names[m]}", fontsize=11)
    f.colorbar(sc, ax=ax, shrink=0.5, label="log10 N(Mw ≥ 5) per year and cell")
    f.savefig(fname, dpi=160, bbox_inches="tight")
    plt.close(f)


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
        print(cal.pivot_table(index=["option", "unit", "exponent"], columns="n", values="dloglik").round(1).to_string())
        print(pick.to_string(index=False))
    pats = patterns(d, g, pick)
    for m, p in pats.items():
        p.to_csv(TAB / f"pattern_{m}_{DATE}.csv", index=False, float_format="%.6e")
    maps(pats, FIG / f"background_N5_{DATE}.png")
    o = outside(d, g, pick)
    o.round(4).to_csv(TAB / f"grid_outside_{DATE}.csv", index=False)
    print(o.round(3).to_string(index=False))


if __name__ == "__main__":
    main()

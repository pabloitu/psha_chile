"""Gutenberg-Richter fitting methods compared (plan B11, step 3). Same completeness table, class weights and
magnitude-error weight for all.

real(): every method on every class and interface segment of the frozen catalogue, with all events and with the
weight-1 events only; called by run.py, which writes tables/fits_sensitivity_<date>.csv.
run(): recovery on synthetic catalogues built like ours (synth.py): bias and interval coverage per method, the
pooled b on a family of small classes, and the automatic table. Writes tables/synth_*.csv.
"""
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

import gr as G
import synth as S
import table as TB

HERE = Path(__file__).resolve().parent
TAB = HERE / "tables"

# settings
INSTR = dict(mc=5.0, since=1976)
# detection windows of the joint fit: the network windows of the table from 1976
WINDOWS = [q for q in TB.WINDOWS if q[0] >= INSTR["since"]]
OK_FROM = (3.5, 4.5)
FLOORS = (5.0, 5.2, 5.4, 5.6, 5.8, 6.0)
CORNER = 9.6
TAPER = ["interface", "seg1", "seg2", "seg3", "seg4", "intraslab_shallow", "intraslab_intermediate", "jujuy_nest"]
REF = (5.0, 7.0, 8.0)
# synthetic catalogues: b, events of Mw >= 5 per year, class whose weights are drawn, largest magnitude as in run.py
NSIM, NB, NB_SLOW, NPROC = 400, 200, 60, 14
SCEN = {"large class (interface)": dict(b=0.96, n5=25.0, cls="interface", pad=None),
        "small class (forearc)": dict(b=1.0, n5=3.5, cls="forearc", pad=0.2)}
# family for the pooled b: rates of the four crustal classes, equal b and unequal b
FAMILY = dict(n5=(3.5, 1.3, 2.3, 0.64), cls="forearc", cases={"equal b": (1.0, 1.0, 1.0, 1.0), "unequal b": (0.9, 1.0, 1.1, 1.0)})
# the automatic table: all events of a margin in four regions
MARGIN = dict(b=1.05, n5=70.0, nsim=40, lat=(-21.0, -29.0, -34.5, -41.0), share=(0.4, 0.25, 0.25, 0.1))


def out(f, **key):
    o = dict(key, b=f["b"], **{f"N{M:g}": float(G.n_ge(f, M)) for M in REF})
    if "T" in f:
        for M in (7.0, 8.0):
            o[f"exp{M:g}"], o[f"obs{M:g}"], o[f"ok{M:g}"] = G.check(f, M)
    return o


def real(d, te, F):
    """Every method on every unit of run.py. F: the fits of run.py per shape (all events, weight-1 events)."""
    import run as R
    m, t, sig = d.mw.to_numpy(), d.t.to_numpy(), d.mw_sigma.to_numpy()
    rows = []
    for split in (True, False):
        ev = "all" if split else "weight 1"
        ref, tap, free = {}, {}, {}
        for u in ["forearc"] + [q for q in R.ORDER if q != "forearc"]:
            ref[u] = F["trunc"][0][u] if split else R.fit(d, u, te, "trunc", done=ref, split=False, nboot=0)
            tap[u] = F["taper"][0][u] if split else R.fit(d, u, te, "taper", done=tap, split=False, nboot=0)
        for u in R.ORDER:
            w, tp, f0 = R.weights(d, u, split), R.top(d, u), ref[u]
            bf = dict(bfix=f0["b"]) if R.UNITS[u].get("b_from") else {}
            kw = dict(sig=sig, bw=f0["b"])
            yr, Tf = G.table_years(R.TABLE, te)
            nf = np.bincount(G.kbin(m), f0["w"], minlength=yr.size)[:yr.size]
            add = lambda f, method, **k: rows.append(out(f, unit=u, events=ev, method=method, npar=f.get("npar"),
                                                         lnL=G.loglik(f, nf, Tf) if "npar" in f else np.nan, **k))
            add(f0, "line cut at Mmax (reference)", mmax=f0["mmax"])
            add(tap[u], "tapered, corner of run.py", corner=tap[u]["corner"])
            add(G.fit(m, t, w, R.TABLE, te, top=tp, **kw, **bf), "open line")
            add(G.fit(m, t, w, R.TABLE, te, **kw, **bf), "open line, no largest magnitude in the likelihood")
            if u in TAPER:
                if tap[u]["corner"] != CORNER:
                    add(G.fit(m, t, w, R.TABLE, te, shape="taper", corner=CORNER, top=tp, **kw), f"tapered, corner {CORNER}", corner=CORNER)
                g = G.fit(m, t, w, R.TABLE, te, shape="taper_free", top=tp, **kw)
                add(g, "tapered, corner free", corner=g["corner"])
            if not bf:
                free[u] = f0 if split else R.fit(d, u, te, "trunc", done=ref, split=False, nboot=300)
                add(G.aki_utsu(m, t, w, te=te, sig=sig, **INSTR), "Aki–Utsu, Mw ≥ 5.0 from 1976")
                for ml in OK_FROM:
                    g = G.ogata_katsura(m, t, w, WINDOWS, te, mlow=ml, sig=sig)
                    add(g, f"Ogata–Katsura, Mw ≥ {ml} from 1976", mc95=g["mc95"].max(), width=g["s"].max())
                add(G.least_squares(f0), "least squares, cumulative")
                for fl in FLOORS[1:]:
                    add(G.fit(m, t, w, R.TABLE, te, sig=sig, shape="trunc", top=tp, floor=fl), f"line cut at Mmax, floor {fl}", floor=fl)
            else:
                free[u] = R.fit(d, u, te, "trunc", done=ref, split=split, nboot=300, own_b=True)
                add(free[u], "line cut at Mmax, own b")
        # b pooled over the units of a family, the rate refitted
        for fam in ("segments", "in-slab", "crustal"):
            us = [u for u in R.ORDER if R.UNITS[u]["family"] == fam]
            mu, tau2, bs = G.shrink([free[u]["b"] for u in us], [np.nanstd(free[u]["bb"]) for u in us])
            for u, b in zip(us, bs):
                g = G.fit(m, t, R.weights(d, u, split), R.TABLE, te, sig=sig, shape="trunc", top=R.top(d, u), bfix=b)
                rows.append(out(g, unit=u, events=ev, method="pooled b (shrinkage)", family_b=mu, tau=np.sqrt(tau2)))
    x = pd.DataFrame(rows)
    x["aic"] = 2 * x.npar - 2 * x.lnL
    x.insert(2, "name", x.unit.map(R.name))
    return x


# synthetic catalogues
def interval(v):
    return tuple(np.nanpercentile(v, [5, 95]))


def one_sim(a):
    """Every method on one synthetic catalogue of a scenario, with bootstrap intervals."""
    sc, i, P, wp = a
    s = SCEN[sc]
    rng = np.random.default_rng(1000 + i)
    c = S.catalogue(s["b"], s["n5"], rng, P, wpool=wp)
    m, t, w, sig = c["m"], c["t"], c["w"], c["sig"]
    tp = None if s["pad"] is None else round(float(m[w >= 0.5].max()) + s["pad"] + G.DM, 1)
    rows = []

    def add(method, f, q=None):
        o = dict(scenario=sc, sim=i, method=method, b=f["b"], **{f"N{M:g}": float(G.n_ge(f, M)) for M in REF})
        if q is not None:
            o["b_lo"], o["b_hi"] = interval(q["b"])
            for M in (5.0, 7.0):
                o[f"N{M:g}_lo"], o[f"N{M:g}_hi"] = interval(G.n_ge(q, M))
        rows.append(o)

    f = G.fit(m, t, w, S.TABLE, S.TE, sig=sig, top=tp, nboot=NB, rng=rng)
    add("Weichert, open line (reference)", f, G.boot(f))
    add("Weichert, no magnitude-error weight", G.fit(m, t, w, S.TABLE, S.TE, top=tp))
    ttop = tp or 9.6
    g = G.fit(m, t, w, S.TABLE, S.TE, sig=sig, shape="trunc", top=ttop, nboot=NB, rng=rng)
    add("Weichert, line cut at Mmax", g, G.boot(g))
    g = G.fit(m, t, w, S.TABLE, S.TE, sig=sig, shape="taper", corner=CORNER, top=tp, nboot=NB_SLOW, rng=rng)
    add(f"tapered, corner {CORNER}", g, G.boot(g))
    mult = rng.poisson(1.0, (NB, m.size))
    g = G.aki_utsu(m, t, w, te=S.TE, sig=sig, **INSTR)
    q = [G.aki_utsu(m, t, g["w"] * k, te=S.TE, **INSTR) for k in mult]
    add("Aki–Utsu, Mw ≥ 5.0 from 1976", g, dict(g, b=np.array([v["b"] for v in q]), rate=np.array([v["rate"] for v in q])))
    g = G.ogata_katsura(m, t, w, WINDOWS, S.TE, sig=sig)
    q = [G.ogata_katsura(m, t, g["w"] * k, WINDOWS, S.TE, start=g["p"]) for k in mult[:NB_SLOW]]
    add("Ogata–Katsura, Mw ≥ 3.5 from 1976", g, dict(g, b=np.array([v["b"] for v in q]), rate=np.array([v["rate"] for v in q])))
    g = G.least_squares(f)
    q = [G.least_squares(G.fit(m, t, f["w"] * k, S.TABLE, S.TE, top=tp)) for k in mult[:NB_SLOW]]
    add("least squares, cumulative", g, dict(g, b=np.array([v["b"] for v in q]), rate=np.array([v["rate"] for v in q])))
    return rows


def one_family(a):
    """Own b against the pooled b on a family of four small classes."""
    case, i, P, wp = a
    rng = np.random.default_rng(5000 + i)
    bt = FAMILY["cases"][case]
    cs = [S.catalogue(b, n5, rng, P, wpool=wp) for b, n5 in zip(bt, FAMILY["n5"])]
    tops = [round(float(c["m"][c["w"] >= 0.5].max()) + 0.2 + G.DM, 1) for c in cs]
    fs = [G.fit(c["m"], c["t"], c["w"], S.TABLE, S.TE, sig=c["sig"], top=tp, nboot=NB, rng=rng) for c, tp in zip(cs, tops)]
    sd = [np.nanstd(f["bb"]) for f in fs]
    mu, tau2, bs = G.shrink([f["b"] for f in fs], sd)
    # replicates: the b of every unit pooled again in each replicate
    bsb = np.array([G.shrink([f["bb"][j] for f in fs], sd)[2] for j in range(NB)])
    rows = []
    for k, (c, f, tp) in enumerate(zip(cs, fs, tops)):
        g = G.fit(c["m"], c["t"], c["w"], S.TABLE, S.TE, sig=c["sig"], top=tp, bfix=bs[k], nboot=NB, bboot=bsb[:, k], rng=rng)
        for method, h in (("own b", f), ("pooled b (shrinkage)", g)):
            q = G.boot(h)
            lo, hi = interval(G.n_ge(q, 7.0))
            rows.append(dict(case=case, sim=i, unit=k, method=method, b_true=bt[k], n5_true=FAMILY["n5"][k], b=h["b"],
                             N5=float(G.n_ge(h, 5.0)), N7=float(G.n_ge(h, 7.0)), b_lo=interval(q["b"])[0], b_hi=interval(q["b"])[1],
                             N7_lo=lo, N7_hi=hi))
    return rows


def since(tb, mf):
    y = [y for q, y in tb if q <= mf + 1e-6]
    return min(y) if y else np.nan


def one_table(a):
    """The automatic table on a synthetic margin with the table of DECISIONS, by the rule of DECISIONS (larger of
    the two Mc methods) and with the smaller of the two."""
    roll, i, P = a
    rng = np.random.default_rng(9000 + i)
    c = S.catalogue(MARGIN["b"], MARGIN["n5"], rng, P, roll=roll)
    lat = rng.choice(MARGIN["lat"], c["m"].size, p=MARGIN["share"])
    x = TB.mc_windows(c["m"], c["t"], lat)
    k = c["m"] >= TB.FLOOR - 1e-6
    f0 = G.fit(c["m"], c["t"], c["w"], S.TABLE, S.TE, sig=c["sig"])
    rows = []
    for rule, mc in (("larger of KS and b-stability (DECISIONS)", x.mc), ("smaller of KS and b-stability", x[["bstab", "ks"]].min(axis=1))):
        inst = TB.instrumental(x.assign(mc=mc))
        tb = sorted(inst + TB.historical(c["m"][k], c["t"][k], c["w"][k], S.TE, inst))
        f = G.fit(c["m"], c["t"], c["w"], tb, S.TE, sig=c["sig"])
        rows.append(dict(roll=roll, sim=i, rule=rule, table=TB.text(tb), exact=tb == sorted(S.TABLE),
                         instrumental_exact=inst == [q for q in sorted(S.TABLE) if q[1] >= TB.HIST_FROM],
                         **{f"y{mf:g}": since(tb, mf) for mf in (5.0, 5.2, 5.5, 6.0, 7.0, 7.5, 8.0)}, db=f["b"] - f0["b"],
                         db_true=f["b"] - MARGIN["b"], **{f"r{M:g}": float(G.n_ge(f, M) / G.n_ge(f0, M)) for M in REF},
                         **{f"t{M:g}": float(G.n_ge(f, M) / S.truth(MARGIN["b"], MARGIN["n5"], M)) for M in REF}))
    return rows


def summary(x):
    """Bias, scatter and coverage of the 5-95 % intervals per scenario and method."""
    rows = []
    for (sc, me), g in x.groupby(["scenario", "method"], sort=False):
        s = SCEN[sc]
        o = dict(scenario=sc, method=me, n=len(g), b_bias=g.b.mean() - s["b"], b_sd=g.b.std(), b_cover=((g.b_lo <= s["b"]) & (s["b"] <= g.b_hi)).mean() if g.b_lo.notna().any() else np.nan)
        for M in REF:
            tr = S.truth(s["b"], s["n5"], M)
            o[f"N{M:g}_bias"], o[f"N{M:g}_sd"] = g[f"N{M:g}"].mean() / tr - 1, g[f"N{M:g}"].std() / tr
            if f"N{M:g}_lo" in g and g[f"N{M:g}_lo"].notna().any():
                o[f"N{M:g}_cover"] = ((g[f"N{M:g}_lo"] <= tr) & (tr <= g[f"N{M:g}_hi"])).mean()
        rows.append(o)
    return pd.DataFrame(rows)


def run():
    pd.set_option("display.width", 300, "display.max_columns", 60, "display.max_colwidth", 90)
    TAB.mkdir(exist_ok=True)
    d = G.load()
    P = S.pool(d)
    wp = {s["cls"]: S.weights(d, s["cls"]) for s in SCEN.values()}
    with Pool(NPROC) as pool:
        x = pd.DataFrame([r for rs in pool.map(one_sim, [(sc, i, P, wp[SCEN[sc]["cls"]]) for sc in SCEN for i in range(NSIM)]) for r in rs])
        x.round(5).to_csv(TAB / "synth_methods_runs.csv", index=False)
        sm = summary(x)
        sm.round(4).to_csv(TAB / "synth_methods.csv", index=False)
        print(sm.round(3).to_string(index=False))
        y = pd.DataFrame([r for rs in pool.map(one_family, [(c, i, P, wp[FAMILY["cls"]]) for c in FAMILY["cases"] for i in range(NSIM // 2)]) for r in rs])
        y["N7_true"] = S.truth(y.b_true, y.n5_true, 7.0)
        g = y.assign(db=y.b - y.b_true, r7=np.log10(y.N7 / y.N7_true), cb=(y.b_lo <= y.b_true) & (y.b_true <= y.b_hi),
                     c7=(y.N7_lo <= y.N7_true) & (y.N7_true <= y.N7_hi)).groupby(["case", "unit", "method"], sort=False)
        fam = g.agg(b_true=("b_true", "first"), n5=("n5_true", "first"), b_bias=("db", "mean"), b_rmse=("db", lambda v: np.sqrt((v ** 2).mean())),
                    logN7_bias=("r7", "mean"), logN7_rmse=("r7", lambda v: np.sqrt((v ** 2).mean())), b_cover=("cb", "mean"),
                    N7_cover=("c7", "mean")).reset_index()
        fam.round(4).to_csv(TAB / "synth_pooled.csv", index=False)
        print(fam.round(3).to_string(index=False))
        z = pd.DataFrame([r for rs in pool.map(one_table, [(roll, i, P) for roll in ("normal", "exp") for i in range(MARGIN["nsim"])]) for r in rs])
        z.to_csv(TAB / "synth_table_runs.csv", index=False)
        g = z.groupby(["roll", "rule"], sort=False)
        ts = g.agg(n=("sim", "size"), exact=("exact", "mean"), instrumental_exact=("instrumental_exact", "mean"),
                   y5_median=("y5", "median"), y5_1976=("y5", lambda v: (v == 1976).mean()), y5p2_1964=("y5.2", lambda v: (v == 1964).mean()),
                   y7_median=("y7", "median"), y7_lo=("y7", lambda v: v.quantile(0.1)), y7_hi=("y7", lambda v: v.quantile(0.9)),
                   y7p5_median=("y7.5", "median"), y8_median=("y8", "median"), db=("db", "mean"), db_sd=("db", "std"),
                   r5=("r5", "mean"), r7=("r7", "mean"), r8=("r8", "mean"), r7_sd=("r7", "std")).reset_index()
        ts.round(4).to_csv(TAB / "synth_table.csv", index=False)
        print(ts.round(3).to_string(index=False))


if __name__ == "__main__":
    run()

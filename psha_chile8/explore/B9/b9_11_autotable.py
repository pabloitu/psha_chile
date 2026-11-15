"""B9 addition: an automatic completeness table.

Two rules, both with larger magnitudes complete no later than smaller ones.

joint: the catalogue is cut into magnitude bands and time blocks. With a Gutenberg-Richter line (stationary Poisson
rates) each band is complete from one year on: after it the counts follow the line, before it a step function of
lower rates, each step paid with a BIC penalty. The line is refitted with Weichert on the chosen table until nothing
moves; several starting tables are tried. It needs stationary rates.

hybrid: from HIST_FROM on, the steps come from the shape of the magnitude distribution (Mc per window and region of
b9_10_mc_all.py: a magnitude is complete from the window after the last one whose Mc is above it). Before HIST_FROM
the rate rule above is used with the line of the instrumental fit held fixed.

Also the Kijko and Smit (2012) estimator on a table, next to Weichert. Writes tables/auto_*.csv, figs/auto_table.png."""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.special import gammaln

import b9_lib as L

BANDS = np.round(np.arange(4.5, 8.01, 0.5), 1)
Y0, DT = 1500, 5
STARTS = {"4.5 from 2000": [(4.5, 2000)], "5.0 from 1964": [(5.0, 1964)], "5.5 from 1964": [(5.5, 1964)],
          "network": [(4.5, 2000), (5.0, 1976), (5.5, 1964), (6.5, 1930), (7.0, 1900)],
          "long": [(5.0, 1964), (7.0, 1900), (7.5, 1820), (8.0, 1730)]}
UNITS = {"all events": None, "interface": ["interface"],
         "in-slab": ["intraslab_shallow", "intraslab_intermediate", "jujuy_nest"],
         "crustal": ["forearc", "arc", "backarc", "patagonia"]}
BASES = ["nn", "full"]
HIST_FROM = 1964
MC_NMIN = 100
CANDIDATE = [(5.0, 1964), (7.0, 1900), (7.5, 1820), (8.0, 1730)]
NSYN = 30
SYN = {"long record": [(5.0, 1964), (7.0, 1900), (7.5, 1820), (8.0, 1730)],
       "network steps": [(4.5, 2000), (5.0, 1976), (5.5, 1964), (6.5, 1930), (7.0, 1900)]}
SYN_B, SYN_N5 = 0.93, 26.5


def cells(m, t, w, te):
    """Weighted counts per magnitude band and time block, and the length of each block in years."""
    yb = np.arange(Y0, te + DT, DT)
    yb[-1] = te
    j = np.searchsorted(BANDS, m + 1e-6, side="right") - 1
    k = np.searchsorted(yb, t, side="right") - 1
    ok = (j >= 0) & (k >= 0) & (k < yb.size - 1)
    n = np.zeros((BANDS.size, yb.size - 1))
    np.add.at(n, (j[ok], k[ok]), w[ok])
    return n, np.diff(yb), yb


def pois(n, e):
    return n * np.log(np.maximum(e, 1e-300)) - e - gammaln(n + 1)


def cuts(n, dt, lam, pen):
    """Penalised log-likelihood of every band for every first complete block (last index: never complete).

    Before the cut the rate is a step function below the line, each step costing pen; from the cut on it is the
    line. Returns an array (band, cut)."""
    J, K = n.shape
    S = np.empty((J, K + 1))
    cn, ct = np.c_[np.zeros(J), np.cumsum(n, 1)], np.r_[0, np.cumsum(dt)]
    for j in range(J):
        e = lam[j] * dt
        tail = np.r_[np.cumsum(pois(n[j], e)[::-1])[::-1], 0.0]
        fact = np.r_[0, np.cumsum(gammaln(n[j] + 1) - n[j] * np.log(dt))]
        F = np.zeros(K + 1)
        for c in range(1, K + 1):
            s = np.arange(c)
            N, T = cn[j, c] - cn[j, s], ct[c] - ct[s]
            r = np.minimum(N / T, lam[j])
            seg = np.where(N > 0, N * np.log(np.maximum(r, 1e-300)), 0.0) - r * T - (fact[c] - fact[s])
            F[c] = np.max(F[s] + seg - pen)
        S[j] = F + tail
    return S


def monotone(S):
    """Cut per band with the best total, larger magnitudes complete no later than smaller ones."""
    J, K1 = S.shape
    G, arg = np.empty_like(S), np.zeros((J, K1), int)
    G[0] = S[0]
    for j in range(1, J):
        # best of the band below over cuts at or after c
        best = np.maximum.accumulate(G[j - 1][::-1])[::-1]
        idx = np.array([c + int(np.argmax(G[j - 1][c:])) for c in range(K1)])
        G[j], arg[j] = S[j] + best, idx
    c = np.empty(J, int)
    c[-1] = int(np.argmax(G[-1]))
    for j in range(J - 1, 0, -1):
        c[j - 1] = arg[j][c[j]]
    return c, G[-1].max()


def to_table(c, yb):
    tb = [(float(BANDS[j]), int(yb[c[j]])) for j in range(BANDS.size) if c[j] < yb.size - 1]
    out = []
    for mf, y in tb:
        if not out or y < out[-1][1]:
            out.append((mf, y))
    return out


def rates(r):
    N = np.array([L.n_ge(r["b"], r["rate"], r["m_lo"], M) for M in BANDS])
    return N - np.r_[N[1:], 0.0]


def auto(m, t, w, te, starts=STARTS, niter=30):
    """Automatic table. Returns the best run (table, b, rate, m_lo, score, start) and all runs."""
    n, dt, yb = cells(m, t, w, te)
    pen = np.log(n.size)
    k = L.kbin(m)
    runs = []
    for name, tb in starts.items():
        seen = []
        for _ in range(niter):
            r = L.fit(k, t, w, tb, te)
            if not np.isfinite(r["b"]):
                break
            c, score = monotone(cuts(n, dt, rates(r), pen))
            new = to_table(c, yb)
            if not new or new in seen:
                break
            seen.append(new)
            tb = new
        r = L.fit(k, t, w, tb, te)
        if np.isfinite(r["b"]):
            c, score = monotone(cuts(n, dt, rates(r), pen))
            runs.append(dict(start=name, table=tb, b=r["b"], rate=r["rate"], m_lo=r["m_lo"], score=score, n=r["n"],
                             N5=L.n_ge(r["b"], r["rate"], r["m_lo"], 5.0), N7=L.n_ge(r["b"], r["rate"], r["m_lo"], 7.0)))
    return max(runs, key=lambda q: q["score"]), runs


def instrumental(f=None):
    """Steps of the instrumental era from Mc per window and region (larger of KS and b-stability, largest region):
    a magnitude on the 0.1 grid is complete from the window after the last one whose Mc is above it."""
    x = pd.read_csv(f or L.TAB / "mc_all_regions.csv")
    x = x[(x.depth == "all") & (x.region != "whole margin") & (x.n >= MC_NMIN)]
    x = x.assign(mc=x[["ks", "bstab"]].max(axis=1))
    w = x.groupby(["start", "end"]).mc.max().reset_index().sort_values("start")
    tb = []
    for mf in np.round(np.arange(4.5, w.mc.max() + 0.01, 0.1), 1):
        bad = w[w.mc > mf + 1e-6]
        y = int(w.start.min()) if bad.empty else int(bad.end.max())
        if y < w.end.max() and (not tb or y < tb[-1][1]):
            tb.append((float(mf), y))
    return tb, w


def historical(m, t, w, te, inst):
    """Steps before HIST_FROM for the 0.5 bands above the top instrumental step, rates of the instrumental fit.
    A band with no event at or above it gets no step: nothing can be said about it."""
    r = L.fit(L.kbin(m), t, w, inst, te)
    top = max(mf for mf, _ in inst)
    s = t < HIST_FROM
    n, dt, yb = cells(m[s], t[s], w[s], HIST_FROM)
    # bands above the top instrumental step that hold at least one event (by weight) at or above them
    use = (BANDS >= np.ceil(top * 2 - 1e-6) / 2) & (np.array([w[m >= q - 1e-6].sum() for q in BANDS]) >= 1)
    lam = rates(r)
    c, _ = monotone(cuts(n[use], dt, lam[use], np.log(n[use].size)))
    tb = []
    for mf, cj in zip(BANDS[use], c):
        if cj < yb.size - 1 and (not tb or yb[cj] < tb[-1][1]):
            tb.append((float(mf), int(yb[cj])))
    return tb, r


def hybrid(m, t, w, te, inst):
    hist, r = historical(m, t, w, te, inst)
    return sorted(inst + hist)


def kijko_smit(m, t, w, table, te):
    """Kijko and Smit (2012): b from the Aki-Utsu values of the periods of a table, weighted by their events, and
    the rate at the lowest step from all events and the periods scaled to that magnitude."""
    tb = sorted(table)
    ends = [te] + [y for _, y in tb[:-1]]
    num, den, tsum, bs = 0.0, 0.0, [], []
    for (mc, y0), y1 in zip(tb, ends):
        s = (t >= y0) & (t < y1) & (m >= mc - 1e-6)
        bi, ni = L.tinti(m[s], w[s], mc)
        if ni > 1 and np.isfinite(bi):
            num, den = num + ni, den + ni / bi
        tsum.append((mc, y1 - y0, w[s].sum()))
    b = num / den
    rate = sum(q[2] for q in tsum) / sum(T * 10 ** (-b * (mc - tb[0][0])) for mc, T, _ in tsum)
    return b, rate, tb[0][0] - L.DM / 2


def text(tb):
    return ", ".join(f"{mf:.1f} / {y}" for mf, y in tb)


def synthetic():
    rows = []
    for name, tb in SYN.items():
        for i in range(NSYN):
            rng = np.random.default_rng(100 + i)
            t, m = L.synth(SYN_B, SYN_N5 * 10 ** (SYN_B * 0.5), tb, Y0, 2026.9, rng)
            best, _ = auto(m, t, np.ones(m.size), 2026.9)
            tr = L.fit(L.kbin(m), t, np.ones(m.size), tb, 2026.9)
            got = dict(best["table"])
            o = dict(case=name, sim=i, table=text(best["table"]), start=best["start"], b=best["b"], db=best["b"] - tr["b"],
                     r5=best["N5"] / L.n_ge(tr["b"], tr["rate"], tr["m_lo"], 5.0),
                     r7=best["N7"] / L.n_ge(tr["b"], tr["rate"], tr["m_lo"], 7.0))
            for mf in BANDS:
                # year from which a band counts in a table: the step at or below it
                yt = [y for q, y in tb if q <= mf + 1e-6]
                yg = [y for q, y in got.items() if q <= mf + 1e-6]
                o[f"dy{mf:g}"] = (min(yg) - min(yt)) if yt and yg else (np.nan if not yt and not yg else np.inf if yt else -np.inf)
            # hybrid: the instrumental steps given, the historical ones searched
            inst = [q for q in tb if q[1] >= HIST_FROM]
            hy = hybrid(m, t, np.ones(m.size), 2026.9, inst)
            rh = L.fit(L.kbin(m), t, np.ones(m.size), hy, 2026.9)
            o.update(h_table=text(hy), h_db=rh["b"] - tr["b"],
                     h_r5=L.n_ge(rh["b"], rh["rate"], rh["m_lo"], 5.0) / L.n_ge(tr["b"], tr["rate"], tr["m_lo"], 5.0),
                     h_r7=L.n_ge(rh["b"], rh["rate"], rh["m_lo"], 7.0) / L.n_ge(tr["b"], tr["rate"], tr["m_lo"], 7.0))
            for mf in BANDS[BANDS >= 5.5]:
                yt, yg = [y for q, y in tb if q <= mf + 1e-6], [y for q, y in hy if q <= mf + 1e-6]
                o[f"h_dy{mf:g}"] = min(yg) - min(yt)
            rows.append(o)
        print("synthetic", name, flush=True)
    x = pd.DataFrame(rows)
    x.to_csv(L.TAB / "auto_synthetic.csv", index=False)
    return x


def compare(m, t, w, tb, te, **key):
    """Weichert and Kijko-Smit on one table, and the large-event check of the Weichert line."""
    r = L.fit(L.kbin(m), t, w, tb, te, nboot=200, rng=np.random.default_rng(1))
    bk, rk, mk = kijko_smit(m, t, w, tb, te)
    lam = rates(r)
    yr, T = L.table_years(tb, te)
    cen = L.centres()
    o = dict(key, table=text(tb), n=r["n"], b_weichert=r["b"], b_sd=np.nanstd(r["bb"]), b_kijko=bk,
             N5_weichert=L.n_ge(r["b"], r["rate"], r["m_lo"], 5.0), N5_kijko=L.n_ge(bk, rk, mk, 5.0),
             N7_weichert=L.n_ge(r["b"], r["rate"], r["m_lo"], 7.0), N7_kijko=L.n_ge(bk, rk, mk, 7.0))
    for M in (7.0, 8.0):
        q = cen >= M - 1e-6
        mass = 10 ** (-r["b"] * (cen - L.DM / 2 - r["m_lo"])) - 10 ** (-r["b"] * (cen + L.DM / 2 - r["m_lo"]))
        o[f"exp{M:g}"], o[f"obs{M:g}"] = (r["rate"] * mass * T)[q].sum(), r["cnt"][q].sum()
    return o


def real(d, dc):
    te = L.tend(d)
    m, t = d.mw.to_numpy(), d.t.to_numpy()
    inst, win = instrumental()
    print("Mc per window (largest region):", win.round(1).to_dict("records"))
    print("instrumental steps:", text(inst))
    rows, allruns = [], []
    for u, cs in UNITS.items():
        w0 = np.ones(len(d)) if cs is None else sum(d["W_" + c].to_numpy() for c in cs)
        s = w0 > 0
        for basis in BASES:
            w = w0 * (dc[basis].to_numpy() if basis != "full" else 1)
            q = w > 0
            best, runs = auto(m[q], t[q], w[q], te)
            for v in runs:
                allruns.append(dict(unit=u, basis=basis, start=v["start"], table=text(v["table"]), b=v["b"], N5=v["N5"],
                                    N7=v["N7"], score=v["score"], best=v is best))
            rows.append(compare(m[s], t[s], w0[s], best["table"], te, unit=u, rule=f"joint, {basis} counts"))
        hy = hybrid(m[s], t[s], w0[s], te, inst)
        rows.append(compare(m[s], t[s], w0[s], hy, te, unit=u, rule="hybrid"))
        h5 = [q for q in hy if q[0] >= 5.0 - 1e-6]
        rows.append(compare(m[s], t[s], w0[s], h5, te, unit=u, rule="hybrid, floor 5.0"))
        rows.append(compare(m[s], t[s], w0[s], [(5.0, 1964)], te, unit=u, rule="5.0 from 1964 only"))
        rows.append(compare(m[s], t[s], w0[s], CANDIDATE, te, unit=u, rule="B9 candidate, long record"))
        print(u, flush=True)
    x, a = pd.DataFrame(rows), pd.DataFrame(allruns)
    x.round(4).to_csv(L.TAB / "auto_tables.csv", index=False)
    a.round(4).to_csv(L.TAB / "auto_runs.csv", index=False)
    return x, a


def figure(d, dc, x):
    sys.path.insert(0, str(L.ROOT))
    import palette as P
    P.apply()
    te = L.tend(d)
    fig, ax = plt.subplots(1, len(UNITS), figsize=(4.6 * len(UNITS), 4.6), sharey=True)
    for a, (u, cs) in zip(ax, UNITS.items()):
        w0 = np.ones(len(d)) if cs is None else sum(d["W_" + c].to_numpy() for c in cs)
        s = w0 > 0
        a.scatter(d.t[s], d.mw[s], s=3 + 12 * (d.mw[s] >= 7), c="0.7", lw=0, rasterized=True)
        for rule, col in zip(("hybrid", "joint, nn counts"), (P.SERIES[0], P.SERIES[1])):
            q = x[(x.unit == u) & (x.rule == rule)].iloc[0]
            tb = [tuple(float(v) for v in p.split(" / ")) for p in q.table.split(", ")]
            xs, ys = [te], [tb[0][0] - 0.05]
            for (mf, y), nxt in zip(tb, tb[1:] + [(9.7, None)]):
                xs += [y, y]
                ys += [mf - 0.05, nxt[0] - 0.05]
            a.plot(xs, ys, color=col, lw=1.6, label="hybrid rule" if rule == "hybrid" else "joint rule, declustered counts")
        a.set_title(u, fontsize=11)
        a.set_xlim(1500, 2030)
        a.set_ylim(4.4, 9.7)
        a.set_xlabel("year")
    ax[0].set_ylabel("Mw")
    ax[0].legend(frameon=False, fontsize=9, loc="upper left")
    fig.suptitle("Automatic completeness table: events count to the right of and above the line", x=0.02, ha="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(L.FIG / "auto_table.png", dpi=150, bbox_inches="tight", pad_inches=0.25)


def run():
    pd.set_option("display.width", 280, "display.max_colwidth", 80, "display.max_rows", 200)
    sx = synthetic()
    print(sx.groupby("case")[["db", "r5", "r7", "h_db", "h_r5", "h_r7"]].agg(["mean", "std"]).round(3).T.to_string())
    print(sx.groupby("case")[[c for c in sx.columns if "dy" in c]].median().T.to_string())
    d = L.load()
    dc = pd.read_pickle(L.CACHE / "decluster.pkl")
    x, a = real(d, dc)
    print(a[a.best].round(3).to_string(index=False))
    print(a.groupby(["unit", "basis"]).table.nunique().to_string())
    print(x.round(3).to_string(index=False))
    figure(d, dc, x)


if __name__ == "__main__":
    run()

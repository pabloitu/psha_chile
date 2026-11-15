"""B9 addition: the magnitude-error weight on instrumental events only. Each instrumental event counts
exp(-beta^2 sigma^2 / 2) (CEUS-SSC 2012, eq. 3.3.1-1, per event); no magnitude is moved; historical events count 1.
Fits with and without the weight, a synthetic test and a test on events that have a measured and a converted Mw.
Writes tables/magerr_*.csv and figs/magerr_weight.png."""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import b9_lib as L

# kinds of the catalogue that count as instrumental, and the stricter set of the ISC era
INSTR = ["direct", "proxy", "iscgem", "centennial"]
MODERN = ["direct", "proxy"]
VARIANTS = {"none": [], "instrumental": INSTR, "modern only": MODERN, "all events": None}
# candidate tables of the report ("one window + long record")
ONE = [(5.0, 1964)]
LONG = [(5.0, 1964), (7.0, 1900)]
IFACE = [(5.0, 1964), (7.0, 1900), (7.5, 1820), (8.0, 1730)]
TABLES = {"interface": IFACE, "intraslab_shallow": LONG, "intraslab_intermediate": ONE, "jujuy_nest": ONE,
          "forearc": LONG, "arc": LONG, "backarc": LONG, "patagonia": LONG}
NBOOT = 300
REF = (5.0, 7.0, 8.0)
# synthetic test
NSIM = 200
ERAS = [1730, 1820, 1900, 1964, 1976, 2000, 2027]
GEN_FROM = {1730: 6.45, 1820: 5.95, 1900: 5.45, 1964: 3.45, 1976: 3.75, 2000: 3.75}
BANDS = [0, 5.5, 7.0, 99]
CASES = ["errors as listed", "historical exact", "historical from regression"]
# paired test
PAIR_FROM = [2000, 1976]
PAIR_M = np.round(np.arange(5.5, 6.61, 0.1), 1)
PAIR_BOOT = 2000
PAIR_B = 1.0


def magw(sig, kind, b, kinds):
    """Count of an event: exp(-beta^2 sigma^2 / 2) for the kinds listed (None: every kind), else 1."""
    f = np.exp(-(b * L.LN10) ** 2 * np.asarray(sig, float) ** 2 / 2)
    return f if kinds is None else np.where(np.isin(kind, kinds), f, 1.0)


def fitw(k, t, w, sig, kind, table, te, kinds, nboot=0, seed=1):
    """Weichert fit with the weight; b of the weight iterated from the unweighted fit."""
    r = L.fit(k, t, w, table, te)
    if kinds == []:
        return L.fit(k, t, w, table, te, nboot=nboot, rng=np.random.default_rng(seed))
    for _ in range(4):
        r = L.fit(k, t, w * magw(sig, kind, r["b"], kinds), table, te)
    return L.fit(k, t, w * magw(sig, kind, r["b"], kinds), table, te, nboot=nboot, rng=np.random.default_rng(seed))


def gr(r):
    o = dict(b=r["b"], a=np.log10(r["rate"]) + r["b"] * r["m_lo"], n=r["n"])
    for M in REF:
        o[f"N{M:g}"] = L.n_ge(r["b"], r["rate"], r["m_lo"], M)
    return o


def fits(d):
    te = L.tend(d)
    t, k, sig, kind = d.t.to_numpy(), d.k.to_numpy(), d.mw_sigma.to_numpy(), d.mw_kind.to_numpy()
    W = {c: d["W_" + c].to_numpy() for c in TABLES}
    for s, (a, b) in L.SEG.items():
        W[s] = W["interface"] * ((d.lat >= a) & (d.lat < b)).to_numpy()
    rows = []
    for c, w in W.items():
        tb = TABLES.get(c, IFACE)
        base = None
        for v, kinds in VARIANTS.items():
            r = fitw(k, t, w, sig, kind, tb, te, kinds, nboot=NBOOT if v == "none" else 0)
            o = dict(cls=c, variant=v, **gr(r))
            if v == "none":
                base = o
                o["b_sd"] = np.nanstd(r["bb"])
                o["N5_sd_rel"] = np.nanstd(L.n_ge(r["bb"], r["rr"], r["m_lo"], 5.0)) / o["N5"]
            o.update(db=o["b"] - base["b"], da=o["a"] - base["a"], **{f"r{M:g}": o[f"N{M:g}"] / base[f"N{M:g}"] for M in REF})
            rows.append(o)
    x = pd.DataFrame(rows)
    x.round(4).to_csv(L.TAB / "magerr_fits.csv", index=False)
    return x


def pool(d):
    """(kind, sigma) of the real events per era and magnitude band, to dress the synthetic events."""
    P = {}
    for a, b in zip(ERAS[:-1], ERAS[1:]):
        for lo, hi in zip(BANDS[:-1], BANDS[1:]):
            s = d[(d.t >= a) & (d.t < b) & (d.mw >= lo) & (d.mw < hi)]
            if len(s) < 5:
                s = d[(d.t >= a) & (d.t < b) & (d.mw >= lo)]
            if len(s) < 5:
                s = d[(d.t >= a) & (d.t < b)]
            P[a, lo] = (s.mw_kind.to_numpy(), s.mw_sigma.to_numpy())
    return P


def synthetic(d, b0, n5):
    """Catalogues with the b and rate of the interface fit, the table of the interface and the errors of the real
    catalogue. Case 'errors as listed': every magnitude is the true one plus its listed error. Case 'historical
    exact': non-instrumental magnitudes carry no error although an error is listed. Case 'historical from
    regression': non-instrumental magnitudes are expected values given an uncertain size measure, M + error -
    beta sigma^2 (CEUS-SSC eq. 3.3.1-5), the kind for which the count is too low, not too high."""
    te, P = L.tend(d), pool(d)
    rng = np.random.default_rng(11)
    rows = []
    for case in CASES:
        for i in range(NSIM):
            T, Mt, K, S = [], [], [], []
            for a, b in zip(ERAS[:-1], ERAS[1:]):
                b = min(b, te)
                g = GEN_FROM[a]
                n = rng.poisson(n5 * 10 ** (b0 * (4.95 - g)) * (b - a))
                m = g + rng.exponential(1 / (b0 * L.LN10), n)
                m = m[m < 9.6]
                bd = np.digitize(m, BANDS[1:-1])
                kk, ss = np.empty(m.size, object), np.empty(m.size)
                for j, lo in enumerate(BANDS[:-1]):
                    q = bd == j
                    pk, ps = P[a, lo]
                    idx = rng.integers(0, pk.size, q.sum())
                    kk[q], ss[q] = pk[idx], ps[idx]
                T.append(rng.uniform(a, b, m.size)), Mt.append(m), K.append(kk), S.append(ss)
            t, mt, kind, sig = (np.concatenate(v) for v in (T, Mt, K, S))
            err = rng.normal(0, sig)
            if case == "historical exact":
                err = np.where(np.isin(kind, INSTR), err, 0.0)
            if case == "historical from regression":
                err = np.where(np.isin(kind, INSTR), err, err - b0 * L.LN10 * sig ** 2)
            k, kt = L.kbin(np.rint((mt + err) * 10) / 10), L.kbin(np.rint(mt * 10) / 10)
            w = np.ones(k.size)
            tr = gr(L.fit(kt, t, w, IFACE, te))
            for v, kinds in VARIANTS.items():
                o = gr(fitw(k, t, w, sig, kind, IFACE, te, kinds))
                rows.append(dict(case=case, variant=v, sim=i, b=o["b"], **{f"N{M:g}": o[f"N{M:g}"] for M in REF},
                                 db_true=o["b"] - tr["b"], **{f"r{M:g}": o[f"N{M:g}"] / tr[f"N{M:g}"] for M in REF}))
            r = L.fit(k, t, w, IFACE, te)
            kc, wc, ii = L.ceus(k, w, sig, r["b"], "ceus")
            o = gr(L.fit(kc, t[ii], wc, IFACE, te, grp=ii))
            rows.append(dict(case=case, variant="move and N*, all events", sim=i, b=o["b"], **{f"N{M:g}": o[f"N{M:g}"] for M in REF},
                             db_true=o["b"] - tr["b"], **{f"r{M:g}": o[f"N{M:g}"] / tr[f"N{M:g}"] for M in REF}))
    x = pd.DataFrame(rows)
    g = x.groupby(["case", "variant"], sort=False)[["db_true", "r5", "r7", "r8"]]
    s = g.mean().join(g.std(), rsuffix="_sd").reset_index()
    s.round(4).to_csv(L.TAB / "magerr_synthetic.csv", index=False)
    return s


def paired(d):
    """Events with a measured Mw and a converted value of their own. Above a threshold where the measured Mw is
    complete, the converted values should give more events by exp(beta^2 (s_p^2 - s_d^2) / 2); with the weights the
    two counts should agree."""
    sys.path.insert(0, str(L.ROOT / "catalog"))
    import magnitude as G
    e, M, rm = G.load()
    R, tab, W = G.reference(M)
    F = G.relations(M, R, e, quiet=True, boot=0)
    prio = [s for s in (G.PRIORITY or G.priority(F)) if s in F]
    Pr = G.proxies(e, M, F, prio)
    y, s = pd.Series(np.nan, index=e.index), pd.Series(np.nan, index=e.index)
    for sc in prio[::-1]:
        q = Pr[sc]
        k = q.ok & q.y.notna()
        y[k], s[k] = q.y[k], q.s[k]
    e["yp"], e["sp"] = y.round(1), s
    j = d[d.mw_kind == "direct"].merge(e[["event_id", "yp", "sp"]], on="event_id")
    chk = d[d.mw_kind == "proxy"].merge(e[["event_id", "yp"]], on="event_id")
    print("converted values rebuilt: same as the frozen Mw for", f"{(np.abs(chk.yp - chk.mw) < 0.051).mean():.4f}", "of", len(chk))
    j = j[j.yp.notna()]
    be = PAIR_B * L.LN10
    wd, wp = np.exp(-be ** 2 * j.mw_sigma.to_numpy() ** 2 / 2), np.exp(-be ** 2 * j.sp.to_numpy() ** 2 / 2)
    md, mp, t = j.mw.to_numpy(), j.yp.to_numpy(), j.t.to_numpy()
    rng = np.random.default_rng(3)
    rows = []
    for y0 in PAIR_FROM:
        for m in PAIR_M:
            u = t >= y0
            a, b = u & (md >= m - 1e-6), u & (mp >= m - 1e-6)
            mult = rng.poisson(1.0, (PAIR_BOOT, u.size))
            raw = (mult * b).sum(1) / np.maximum((mult * a).sum(1), 1)
            wt = (mult * (b * wp)).sum(1) / np.maximum((mult * (a * wd)).sum(1), 1e-9)
            pred = np.exp(be ** 2 * (np.mean(j.sp[b] ** 2) - np.mean(j.mw_sigma[a] ** 2)) / 2)
            rows.append(dict(since=y0, m=m, n_measured=int(a.sum()), n_converted=int(b.sum()), ratio=b.sum() / a.sum(),
                             ratio_lo=np.percentile(raw, 5), ratio_hi=np.percentile(raw, 95), predicted=pred,
                             weighted=(b * wp).sum() / (a * wd).sum(), weighted_lo=np.percentile(wt, 5),
                             weighted_hi=np.percentile(wt, 95), sigma_converted=np.sqrt(np.mean(j.sp[b] ** 2)),
                             diff_sd=np.std((mp - md)[a | b])))
    x = pd.DataFrame(rows)
    x.round(4).to_csv(L.TAB / "magerr_paired.csv", index=False)
    return x


def figure(fx, sx, px):
    sys.path.insert(0, str(L.ROOT))
    import palette as P
    P.apply()
    fig, ax = plt.subplots(1, 3, figsize=(17.5, 5.2))
    a = ax[0]
    f = fx[(fx.variant == "instrumental") & fx.cls.isin(TABLES)]
    yy = np.arange(len(f))[::-1]
    a.barh(yy + 0.2, (f.r5 - 1) * 100, 0.38, color=P.SERIES[0], label="N(≥ 5)")
    a.barh(yy - 0.2, (f.r7 - 1) * 100, 0.38, color=P.SERIES[1], label="N(≥ 7)")
    b0 = fx[(fx.variant == "none") & fx.cls.isin(TABLES)]
    a.errorbar(np.zeros(len(f)), yy + 0.2, xerr=b0.N5_sd_rel.to_numpy() * 100, fmt="none", ecolor="0.3", capsize=3, lw=1)
    a.set_yticks(yy, [P.CLASS_NAME.get(c, c) for c in f.cls])
    a.axvline(0, color="0.3", lw=0.8)
    a.set_xlabel("change of the fitted rate with the weight, %")
    a.set_title("Weight on instrumental events\n(whisker: bootstrap sd of N(≥ 5) without it)", fontsize=11)
    a.legend(frameon=False, fontsize=9)
    a = ax[1]
    vs = list(sx.variant.unique())
    for i, case in enumerate(sx.case.unique()):
        s = sx[sx.case == case].set_index("variant").loc[vs]
        xx = np.arange(len(vs)) + (i - 1) * 0.27
        a.bar(xx, (s.r7 - 1) * 100, 0.25, yerr=s.r7_sd * 100, color=P.SERIES[2 + i], label=case, error_kw=dict(lw=0.8, capsize=2))
    a.set_xticks(np.arange(len(vs)), [v.replace(", ", ",\n") for v in vs], fontsize=8.5)
    a.axhline(0, color="0.3", lw=0.8)
    a.set_ylabel("N(≥ 7) fitted over true, % (whisker: sd of one catalogue)")
    a.set_title(f"Synthetic interface catalogues ({NSIM} per case)", fontsize=11)
    a.legend(frameon=False, fontsize=9)
    a = ax[2]
    p = px[px.since == PAIR_FROM[0]]
    a.fill_between(p.m, p.ratio_lo, p.ratio_hi, color=P.SERIES[0], alpha=0.2, lw=0)
    a.plot(p.m, p.ratio, "-o", ms=3, color=P.SERIES[0], label="converted over measured, counts")
    a.plot(p.m, p.predicted, "--", color=P.SERIES[0], lw=1, label="expected from the listed errors")
    a.fill_between(p.m, p.weighted_lo, p.weighted_hi, color=P.SERIES[1], alpha=0.2, lw=0)
    a.plot(p.m, p.weighted, "-s", ms=3, color=P.SERIES[1], label="with the weights")
    a.axhline(1, color="0.3", lw=0.8)
    a.set_xlabel("Mw at and above")
    a.set_ylabel("ratio of the counts")
    a.set_title(f"Same events, measured and converted Mw, from {PAIR_FROM[0]}\n(bands: 5–95 % of a bootstrap)", fontsize=11)
    a.legend(frameon=False, fontsize=9)
    fig.tight_layout(w_pad=3)
    fig.savefig(L.FIG / "magerr_weight.png", dpi=150, bbox_inches="tight", pad_inches=0.25)


def run():
    pd.set_option("display.width", 250)
    d = L.load()
    fx = fits(d)
    print(fx[["cls", "variant", "b", "a", "N5", "N7", "N8", "db", "da", "r5", "r7", "r8", "b_sd", "N5_sd_rel"]].round(3).to_string(index=False))
    i0 = fx[(fx.cls == "interface") & (fx.variant == "none")].iloc[0]
    sx = synthetic(d, i0.b, i0.N5)
    print(sx.round(3).to_string(index=False))
    px = paired(d)
    print(px.round(3).to_string(index=False))
    figure(fx, sx, px)


if __name__ == "__main__":
    run()

"""B9 addition: every class on the single completeness table of 15 Nov (Mc of the whole catalogue from 1964, rate
rule before), with the magnitude-error weight on every event. Weichert with an event bootstrap, Kijko-Smit and
b-positive next to it, the large-event check, and the fit without the weight for comparison. Writes tables/refit_single_table.csv and figs/refit_single_table.png."""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import b9_lib as L
import b9_9_magerr as E
import b9_11_autotable as A

TABLE = [(5.0, 1976), (5.2, 1964), (7.0, 1905), (7.5, 1830), (8.0, 1500)]
NBOOT = 500
# magnitude-error weight on every event (DECISIONS, 15 Nov); False for no correction
MAGERR = True
# largest magnitude in the likelihood: DECISIONS for the interface segments, observed maximum + PAD for the classes
SEG_MMAX = dict(zip(L.SEG, (9.5, 9.1, 8.5, 8.8)))
PAD = 0.2
# b not fitted: taken from another unit
BFIX = {"patagonia": "forearc"}
BPOS = dict(since=1976, floor=5.0, dmc=0.2)
SHOW = L.FIT


def units(d):
    W = {c: d["W_" + c].to_numpy() for c in L.FIT}
    W["crustal"] = sum(W[c] for c in ("forearc", "arc", "backarc", "patagonia"))
    for s, (a, b) in L.SEG.items():
        W[s] = W["interface"] * ((d.lat >= a) & (d.lat < b)).to_numpy()
    return W


def top_of(u, m, w):
    if u == "interface":
        return None
    if u in SEG_MMAX:
        return SEG_MMAX[u] + L.DM
    return round(float(m[w >= 0.5].max()) + PAD + L.DM, 1)


def one(u, m, t, k, w0, sig, kind, te, bfix=None):
    top = top_of(u, m, w0)
    kw = dict(top=top, bfix=bfix)
    N = lambda q, M: L.n_ge(q["b"], q["rate"], q["m_lo"], M)
    r0 = L.fit(k, t, w0, TABLE, te, **kw)
    # each event counts exp(-beta^2 sigma^2 / 2); beta from the fit itself
    w, r = w0, r0
    if MAGERR:
        for _ in range(5):
            w = w0 * E.magw(sig, kind, r["b"], None)
            r = L.fit(k, t, w, TABLE, te, **kw)
    r = L.fit(k, t, w, TABLE, te, nboot=NBOOT, rng=np.random.default_rng(1), **kw)
    o = dict(unit=u, events=r0["n"], n=r["n"], mmax=None if top is None else round(top - L.DM, 1), b=r["b"],
             b_sd=np.nanstd(r["bb"]), a=np.log10(r["rate"]) + r["b"] * r["m_lo"])
    for M in (5.0, 7.0, 8.0):
        o[f"N{M:g}"] = N(r, M)
        o[f"N{M:g}_lo"], o[f"N{M:g}_hi"] = np.nanpercentile(L.n_ge(r["bb"], r["rr"], r["m_lo"], M), [5, 95])
    # fitted against observed inside the table
    cen = L.centres()
    mass = 10 ** (-r["b"] * (cen - L.DM / 2 - r["m_lo"])) - 10 ** (-r["b"] * (cen + L.DM / 2 - r["m_lo"]))
    for M in (7.0, 8.0):
        q = cen >= M - 1e-6
        e, ob = (r["rate"] * mass * r["T"])[q].sum(), r["cnt"][q].sum()
        lo, hi = stats.poisson.ppf([0.05, 0.95], e)
        o[f"exp{M:g}"], o[f"obs{M:g}"], o[f"ok{M:g}"] = e, ob, bool(lo - 0.5 <= ob <= hi + 0.5)
    if bfix is None:
        o["b_kijko"] = A.kijko_smit(m, t, w, TABLE, te)[0]
        s = (t >= BPOS["since"]) & (m >= BPOS["floor"] - 1e-6) & (w > 0)
        o["b_positive"], o["n_pairs"] = L.bpositive(m[s], w[s], BPOS["dmc"])
    o.update(b_none=r0["b"], N5_none=N(r0, 5.0), N7_none=N(r0, 7.0), N8_none=N(r0, 8.0))
    return o, r


def figure(d, W, fits):
    sys.path.insert(0, str(L.ROOT))
    import palette as P
    P.apply()
    te = L.tend(d)
    yr, T = L.table_years(TABLE, te)
    cen = L.centres()
    fig, ax = plt.subplots(2, 4, figsize=(16.5, 7.6), sharex=True)
    for a, u in zip(ax.ravel(), SHOW):
        o, r = fits[u]
        col = P.CLASS_COLOR.get(u, "0.3")
        use = (r["T"] > 0) & (r["cnt"] > 0)
        rate = np.where(r["T"] > 0, r["cnt"] / np.where(r["T"] > 0, r["T"], 1), 0)
        cum = np.cumsum(rate[::-1])[::-1]
        a.plot(cen[use], cum[use], "o", ms=3.5, color=col, label="observed, per period of the table")
        x = np.arange(5.0, (o["mmax"] or 9.6) + 0.01, 0.1)
        a.plot(x, L.n_ge(r["b"], r["rate"], r["m_lo"], x), "-", color="0.15", lw=1.2, label="Weichert")
        lo, hi = (np.nanpercentile(L.n_ge(r["bb"][:, None], r["rr"][:, None], r["m_lo"], x[None, :]), q, axis=0) for q in (5, 95))
        a.fill_between(x, lo, hi, color="0.15", alpha=0.15, lw=0)
        a.set_yscale("log")
        fx = " (b fixed)" if u in BFIX else ""
        a.set_title(f"{P.CLASS_NAME.get(u, u)}\nb {o['b']:.2f}{fx}, N(≥ 5) {o['N5']:.3g} per year", fontsize=10.5)
    for a in ax[:, 0]:
        a.set_ylabel("events per year at and above Mw")
    for a in ax[-1]:
        a.set_xlabel("Mw")
    ax[0, 0].legend(frameon=False, fontsize=8.5)
    fig.suptitle("Fits on the single completeness table: " + A.text(TABLE) + " (band: 5–95 % of the bootstrap)" + ("; events counted with the magnitude-error weight" if MAGERR else ""), x=0.02, ha="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(L.FIG / "refit_single_table.png", dpi=150, bbox_inches="tight", pad_inches=0.25)


def run():
    pd.set_option("display.width", 300, "display.max_columns", 50)
    d = L.load()
    te = L.tend(d)
    m, t, k, sig, kind = (d[c].to_numpy() for c in ("mw", "t", "k", "mw_sigma", "mw_kind"))
    W = units(d)
    fits = {}
    for u in ["crustal"] + [q for q in W if q != "crustal"]:
        bf = fits[BFIX[u]][0]["b"] if u in BFIX else None
        fits[u] = one(u, m, t, k, W[u], sig, kind, te, bf)
        if u in BFIX:
            fits[u][0]["b_free"] = one(u, m, t, k, W[u], sig, kind, te)[0]["b"]
    x = pd.DataFrame([fits[u][0] for u in list(L.FIT) + ["crustal"] + list(L.SEG)])
    x.round(4).to_csv(L.TAB / "refit_single_table.csv", index=False)
    print(x[["unit", "events", "n", "mmax", "b", "b_sd", "b_kijko", "b_positive", "a", "N5", "N5_lo", "N5_hi", "N7", "N7_lo", "N7_hi", "N8"]].round(3).to_string(index=False))
    print(x[["unit", "exp7", "obs7", "ok7", "exp8", "obs8", "ok8", "b_none", "N5_none", "N7_none", "N8_none", "b_free"]].round(3).to_string(index=False))
    figure(d, W, fits)


if __name__ == "__main__":
    run()

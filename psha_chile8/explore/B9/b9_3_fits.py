"""B9: b-values and rates per class. Weichert on every candidate table, all events and weight-1 events, full and
declustered, with and without the magnitude-error correction; b against the fit floor; fits per period; b-positive;
the fit below 7 that predicts the large events; the sensitivity cases. Writes cache/fits_*.csv."""
import time

import numpy as np
import pandas as pd

import b9_lib as L
import b9_tables as TB

NBOOT = 300
MODES = ["all", "w1"]
BASIS = ["full", "gk", "nn"]
CORR = ["none", "ceus", "plain"]
FLOORS = np.round(np.arange(4.5, 6.01, 0.1), 1)
REF = [5.0, 6.0, 7.0, 7.5, 8.0]
BASE = dict(mode="all", basis="full", corr="none")
# ISC-GEM proxies of the four old in-slab events left as they are (A6 report)
OLD4 = {"cl19180520175507": 6.9, "cl19250515115705": 6.3, "cl19480511085546": 6.5, "cl19710617210041": 6.3}
FORCE = False


def classes(d):
    """Weight per event for every fitted unit: the classes, the interface segments and two pooled families."""
    W = {c: d["W_" + c].to_numpy() for c in L.CLASSES}
    for s, (a, b) in L.SEG.items():
        W[s] = W["interface"] * ((d.lat >= a) & (d.lat < b)).to_numpy()
    W["intraslab"] = W["intraslab_shallow"] + W["intraslab_intermediate"]
    W["crustal"] = W["forearc"] + W["arc"] + W["backarc"] + W["patagonia"]
    return W


def mode_w(w, mode):
    return np.where(w >= 1 - 1e-9, w, 0.0) if mode == "w1" else w


def row(r, T, cnt_all):
    """Numbers of one fit: b, rates at the reference magnitudes with the 5-95 % range, and the expected against the
    observed count of large events inside the table (T, cnt_all: the table without a top cut)."""
    o = dict(b=r["b"], rate=r["rate"], m_lo=r["m_lo"], n=r["n"], nev=r["nev"])
    has = "bb" in r
    if has:
        o["b_lo"], o["b_hi"] = np.nanpercentile(r["bb"], [5, 95])
        o["b_sd"] = np.nanstd(r["bb"])
    for M in REF:
        o[f"N{M:g}"] = L.n_ge(r["b"], r["rate"], r["m_lo"], M)
        if has:
            o[f"N{M:g}_lo"], o[f"N{M:g}_hi"] = np.nanpercentile(L.n_ge(r["bb"], r["rr"], r["m_lo"], M), [5, 95])
    m = L.centres()
    lam = r["rate"] * (10 ** (-r["b"] * (m - L.DM / 2 - r["m_lo"])) - 10 ** (-r["b"] * (m + L.DM / 2 - r["m_lo"])))
    for M in (7.0, 7.5, 8.0):
        s = m >= M - 1e-6
        o[f"exp{M:g}"], o[f"obs{M:g}"] = (lam * T)[s].sum(), cnt_all[s].sum()
        o[f"T{M:g}"] = T[s].max()
    return o


def one(k, t, w, sig, table, te, corr="none", nboot=NBOOT, seed=1, **kw):
    """Weichert fit with the chosen magnitude-error correction (beta from the uncorrected fit)."""
    r = L.fit(k, t, w, table, te, nboot=0 if corr != "none" else nboot, rng=np.random.default_rng(seed), **kw)
    kk, ww, tt, grp = k, w, t, None
    if corr != "none" and np.isfinite(r["b"]):
        kk, ww, ii = L.ceus(k, w, sig, r["b"], corr)
        tt, grp = t[ii], ii
        r = L.fit(kk, tt, ww, table, te, nboot=nboot, rng=np.random.default_rng(seed), grp=grp, **kw)
    kw2 = {a: b for a, b in kw.items() if a != "top"}
    f = L.fit(kk, tt, ww, table, te, grp=grp, **kw2) if "top" in kw else r
    return row(r, f["T"], f["cnt"])


def cached(name, fn):
    f = L.CACHE / f"fits_{name}.csv"
    if f.exists() and not FORCE:
        print(name, "cached")
        return pd.read_csv(f)
    t0 = time.time()
    x = pd.DataFrame(fn())
    x.to_csv(f, index=False)
    print(name, len(x), f"{time.time() - t0:.0f} s", flush=True)
    return x


def run():
    d = L.load()
    dc = pd.read_pickle(L.CACHE / "decluster.pkl")
    te = L.tend(d)
    t, k, sig = d.t.to_numpy(), d.k.to_numpy(), d.mw_sigma.fillna(0.2).to_numpy()
    W = classes(d)
    keep = {"full": np.ones(len(d), bool), "gk": dc.gk.to_numpy(), "nn": dc.nn.to_numpy()}

    def main():
        for c, w0 in W.items():
            for name, tb in TB.tables(c).items():
                for mode in MODES:
                    for basis in BASIS:
                        for corr in CORR:
                            w = mode_w(w0, mode) * keep[basis]
                            try:
                                yield dict(cls=c, table=name, mode=mode, basis=basis, corr=corr, **one(k, t, w, sig, tb, te, corr))
                            except Exception as e:
                                print("failed", c, name, mode, basis, corr, repr(e))

    def floors():
        for c, w0 in W.items():
            tbs = TB.tables(c)
            for name in ("network", "data"):
                for basis in ("full", "gk"):
                    for corr in ("none", "ceus"):
                        for fl in FLOORS:
                            w = w0 * keep[basis]
                            yield dict(cls=c, table=name, mode="all", basis=basis, corr=corr, floor=fl,
                                       **one(k, t, w, sig, tbs[name], te, corr, nboot=100, floor=fl))

    def periods():
        for c, w0 in W.items():
            for a, b in L.PERIODS + [(1964, 2027), (1990, 2027), (2000, 2027)]:
                for basis in ("full", "gk"):
                    for fl in (4.5, 5.0, 5.5):
                        w = w0 * keep[basis]
                        e = min(b, te)
                        r = one(k, t, w, sig, [(fl, a)], e, nboot=100)
                        s = (t >= a) & (t < e) & (w > 0)
                        o = np.argsort(t[s])
                        bp, nbp = L.bpositive(d.mw.to_numpy()[s][o], w[s][o], 0.2)
                        yield dict(cls=c, start=a, end=b, basis=basis, floor=fl, bpos=bp, n_bpos=nbp, **r)

    def bpos():
        m = d.mw.to_numpy()
        rng = np.random.default_rng(3)
        for c, w0 in W.items():
            for mode in MODES:
                for start in (1964, 1990, 2000, 2012):
                    for dmc in (0.1, 0.2, 0.3, 0.5):
                        w = mode_w(w0, mode)
                        s = (t >= start) & (w > 0)
                        mm, ww = m[s], w[s]
                        dm = np.rint(np.diff(mm) / L.DM) * L.DM
                        pw = ww[1:] * ww[:-1]
                        b, n = L.tinti(dm, pw, dmc)
                        bs = []
                        for _ in range(200):
                            i = rng.integers(0, dm.size, dm.size)
                            bs.append(L.tinti(dm[i], pw[i], dmc)[0])
                        lo, hi = np.nanpercentile(bs, [5, 95]) if dm.size > 5 else (np.nan, np.nan)
                        yield dict(cls=c, mode=mode, start=start, dmc=dmc, b=b, b_lo=lo, b_hi=hi, n=n)

    def below():
        # the fit sees only M < 7 and has to predict the large events of each table
        for c, w0 in W.items():
            for name, tb in TB.tables(c).items():
                if name in ("recent", "isc", "old"):
                    continue
                for mode in MODES:
                    for basis in ("full", "gk"):
                        for corr in ("none", "ceus"):
                            for top in (6.5, 7.0):
                                w = mode_w(w0, mode) * keep[basis]
                                yield dict(cls=c, table=name, mode=mode, basis=basis, corr=corr, top=top,
                                           **one(k, t, w, sig, tb, te, corr, top=top))

    def sens():
        mb = d.relation_id.fillna("").str.contains("mb").to_numpy() & (t < 1990)
        old = d.event_id.isin(OLD4).to_numpy()
        kp = k.copy()
        kp[old] = L.kbin(d.event_id[old].map(OLD4).to_numpy())
        bands = pd.read_pickle(L.CACHE / "bands.pkl") if (L.CACHE / "bands.pkl").exists() else None
        for c, w0 in W.items():
            tbs = TB.tables(c)
            hist = c in TB.HIST_CLASSES or c.startswith("seg")
            base = "network+counts" if hist else "network"
            tb = tbs[base]
            cases = {"baseline": (k, w0, tb),
                     "mb before 1990 lowered by 0.1": (np.where(mb, k - 1, k), w0, tb),
                     "floor 5.5 before 1990": (k, w0, [(m, 1990 if m == 5.0 else y) for m, y in tb]),
                     "four old in-slab events at the ISC-GEM value": (kp, w0, tb),
                     "four old in-slab events left out": (k, np.where(old, 0.0, w0), tb),
                     "no events before 1976 at M >= 7": (k, w0, [(m, max(y, 1976) if m >= 7 else y) for m, y in TB.NETWORK])}
            if bands is not None:
                for bw in (10, 20):
                    def wb(x):
                        return bands[f"W_{x}_{bw}"].to_numpy()
                    if c in L.CLASSES:
                        wc = wb(c)
                    elif c.startswith("seg"):
                        a, b = L.SEG[c]
                        wc = wb("interface") * ((d.lat >= a) & (d.lat < b)).to_numpy()
                    elif c == "intraslab":
                        wc = wb("intraslab_shallow") + wb("intraslab_intermediate")
                    else:
                        wc = sum(wb(x) for x in ("forearc", "arc", "backarc", "patagonia"))
                    cases[f"interface band ± {bw} km"] = (k, wc, tb)
            for name, (kk, ww, tt) in cases.items():
                yield dict(cls=c, case=name, table=base, **one(kk, t, ww, sig, tt, te))

    for name, fn in (("main", main), ("floors", floors), ("periods", periods), ("bpos", bpos), ("below", below), ("sens", sens)):
        cached(name, fn)


if __name__ == "__main__":
    t0 = time.time()
    run()
    print(f"{time.time() - t0:.0f} s")

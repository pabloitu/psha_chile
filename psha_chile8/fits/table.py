"""The completeness table, read on all events (DECISIONS, Statistics).

From HIST_FROM the steps come from the shape of the magnitude distribution: Mc per network window and region with
the events from Mw 3.5 (b-stability and a Kolmogorov-Smirnov test, the larger; the largest region), and a magnitude
is complete from the window after the last one whose Mc is above it. Before HIST_FROM a step of a 0.5 band is the
earliest year from which its counts in 5-year blocks stay consistent with the Gutenberg-Richter line of the
instrumental fit (a step function of lower rates before it, each step paid with a BIC penalty). A larger magnitude
is never complete later than a smaller one. A historical step that reaches less than MIN_BACK years before
HIST_FROM is not kept.
"""
import numpy as np
import pandas as pd
from scipy.special import gammaln

import gr as G

# settings
FLOOR = 5.0
WINDOWS = [(1964, 1976), (1976, 1990), (1990, 2000), (2000, 2007), (2007, 2012), (2012, 2020), (2020, 2027)]
REG = {"north": (-26.0, -15.0), "central-north": (-32.0, -26.0), "central": (-37.0, -32.0), "south": (-46.0, -37.0),
       "far south": (-60.0, -46.0)}
NMIN = 100
KS = dict(p=0.1, nsim=200, ncap=3000, nmin=50)
HIST_FROM, Y0, DT, MIN_BACK = 1964, 1500, 5, 10
BANDS = np.round(np.arange(5.0, 8.01, 0.5), 1)


def shibolt(m, w, mc, b):
    ok = m >= mc - 1e-6
    sw = w[ok].sum()
    mean = (m[ok] * w[ok]).sum() / sw
    return 2.3 * b * b * np.sqrt((w[ok] * (m[ok] - mean) ** 2).sum() / max(sw * (sw - 1), 1))


def mc_bstab(m, w, span=0.5, nmin=50):
    """Lowest cut where b differs from the mean b of the next `span` by less than its Shi-Bolt error (Cao and Gao
    2002; Woessner and Wiemer 2005)."""
    cuts = np.arange(G.M0, 7.01, G.DM)
    b = np.array([G.tinti(m, w, c)[0] for c in cuts])
    nn = np.array([w[m >= c - 1e-6].sum() for c in cuts])
    ns = int(round(span / G.DM))
    for i, c in enumerate(cuts[:-ns]):
        if nn[i] < nmin or np.isnan(b[i]):
            break
        if abs(np.nanmean(b[i:i + ns + 1]) - b[i]) <= shibolt(m, w, c, b[i]):
            return round(float(c), 1)
    return np.nan


def mc_ks(m, w, p=0.1, nsim=200, ncap=3000, nmin=50, rng=None):
    """Lowest cut where a Kolmogorov-Smirnov test does not reject the binned exponential with the fitted b (Clauset
    et al. 2009); the p-value from simulated samples of the weighted size, capped at ncap."""
    rng = rng or np.random.default_rng(2)
    for c in np.arange(G.M0, 7.01, G.DM):
        ok = m >= c - 1e-6
        sw = w[ok].sum()
        if sw < nmin:
            break
        b, _ = G.tinti(m, w, c)
        if np.isnan(b):
            break
        kk = G.kbin(m[ok]) - G.kbin(c)
        nb = kk.max() + 30
        grid = np.arange(nb) + 1
        D = np.abs(np.cumsum(np.bincount(kk, w[ok], minlength=nb)) / sw - (1 - 10 ** (-b * G.DM * grid))).max()
        n = int(min(sw, ncap))
        s = np.minimum(np.floor(rng.exponential(1 / (b * G.LN10), (nsim, n)) / G.DM).astype(int), nb - 1)
        bj = np.log(1 + 1 / s.mean(1)) / G.DM / G.LN10
        Ds = np.array([np.abs(np.cumsum(np.bincount(s[j], minlength=nb)) / n - (1 - 10 ** (-bj[j] * G.DM * grid))).max()
                       for j in range(nsim)])
        if (Ds >= D).mean() >= p:
            return round(float(c), 1)
    return np.nan


def mc_windows(m, t, lat, windows=WINDOWS, reg=REG):
    """Mc per window and region: n, b-stability, KS and the larger of the two (NaN where under NMIN events)."""
    rows = []
    for rg, (la0, la1) in reg.items():
        for a, b in windows:
            s = (t >= a) & (t < b) & (lat >= la0) & (lat < la1)
            r = dict(region=rg, start=a, end=b, n=int(s.sum()), bstab=np.nan, ks=np.nan)
            if s.sum() >= NMIN:
                w = np.ones(int(s.sum()))
                r.update(bstab=mc_bstab(m[s], w), ks=mc_ks(m[s], w, rng=np.random.default_rng(5), **KS))
            rows.append(r)
    x = pd.DataFrame(rows)
    x["mc"] = x[["bstab", "ks"]].max(axis=1)
    return x


def instrumental(x, floor=FLOOR):
    """Steps from the Mc of the windows: a magnitude on the 0.1 grid is complete from the window after the last
    one whose Mc (largest region) is above it."""
    w = x.groupby(["start", "end"]).mc.max().reset_index().sort_values("start")
    tb = []
    for mf in np.round(np.arange(floor, max(w.mc.max(), floor) + 0.01, 0.1), 1):
        bad = w[w.mc > mf + 1e-6]
        y = int(w.start.min()) if bad.empty else int(bad.end.max())
        if y < w.end.max() and (not tb or y < tb[-1][1]):
            tb.append((float(mf), y))
    return tb


def cells(m, t, w, te):
    """Weighted counts per magnitude band and time block, and the length of each block in years."""
    yb = np.arange(Y0, te + DT, DT, dtype=float)
    yb[-1] = te
    j = np.searchsorted(BANDS, m + 1e-6, side="right") - 1
    k = np.searchsorted(yb, t, side="right") - 1
    ok = (j >= 0) & (k >= 0) & (k < yb.size - 1)
    n = np.zeros((BANDS.size, yb.size - 1))
    np.add.at(n, (j[ok], k[ok]), w[ok])
    return n, np.diff(yb), yb


def cuts(n, dt, lam, pen):
    """Penalised log-likelihood of every band for every first complete block (last index: never complete).

    From the cut on the rate is the line; before it a step function below the line, each step costing pen."""
    J, K = n.shape
    S = np.empty((J, K + 1))
    cn, ct = np.c_[np.zeros(J), np.cumsum(n, 1)], np.r_[0, np.cumsum(dt)]
    for j in range(J):
        e = lam[j] * dt
        pois = n[j] * np.log(np.maximum(e, 1e-300)) - e - gammaln(n[j] + 1)
        tail = np.r_[np.cumsum(pois[::-1])[::-1], 0.0]
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
    G_, arg = np.empty_like(S), np.zeros((J, K1), int)
    G_[0] = S[0]
    for j in range(1, J):
        arg[j] = [c + int(np.argmax(G_[j - 1][c:])) for c in range(K1)]
        G_[j] = S[j] + np.maximum.accumulate(G_[j - 1][::-1])[::-1]
    c = np.empty(J, int)
    c[-1] = int(np.argmax(G_[-1]))
    for j in range(J - 1, 0, -1):
        c[j - 1] = arg[j][c[j]]
    return c


def historical(m, t, w, te, inst):
    """Steps before HIST_FROM for the 0.5 bands above the top instrumental step, with the line of the fit on the
    instrumental steps held fixed. A band with no event at or above it gets no step."""
    f = G.fit(m, t, w, inst, te)
    N = np.array([G.n_ge(f, M) for M in BANDS])
    lam = N - np.r_[N[1:], 0.0]
    s = t < HIST_FROM
    n, dt, yb = cells(m[s], t[s], w[s], HIST_FROM)
    top = max(mf for mf, _ in inst)
    use = (BANDS >= np.ceil(top * 2 - 1e-6) / 2) & (np.array([w[m >= q - 1e-6].sum() for q in BANDS]) >= 1)
    c = monotone(cuts(n[use], dt, lam[use], np.log(n[use].size)))
    tb = []
    for mf, cj in zip(BANDS[use], c):
        if cj < yb.size - 1 and yb[cj] <= HIST_FROM - MIN_BACK and (not tb or yb[cj] < tb[-1][1]):
            tb.append((float(mf), int(yb[cj])))
    return tb


def auto(m, t, lat, te, windows=WINDOWS, reg=REG):
    """The automatic table of a catalogue (all events from Mw 3.5, no weights) and the Mc of the windows."""
    x = mc_windows(m, t, lat, windows, reg)
    inst = instrumental(x)
    s = m >= FLOOR - 1e-6
    return sorted(inst + historical(m[s], t[s], np.ones(int(s.sum())), te, inst)), x


def text(tb):
    return ", ".join(f"{mf:.1f} from {y}" for mf, y in sorted(tb))

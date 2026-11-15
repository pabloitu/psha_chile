"""Synthetic catalogues built like the frozen one: a Gutenberg-Richter line of true magnitudes, each event dressed
with the magnitude kind and error of a real event of its period and size, the observed magnitude rounded to 0.1,
events below the completeness table thinned, and class weights drawn from the real weights of a class."""
import numpy as np
from scipy.special import ndtr

import gr as G

TABLE = [(5.0, 1976), (5.2, 1964), (7.0, 1905), (7.5, 1830), (8.0, 1500)]
TE = 2026.86
# periods and the lowest true magnitude generated in each (well below the table, for the magnitude errors)
ERAS = [1500, 1830, 1905, 1964, 1976, 2000]
GEN_FROM = {1500: 5.95, 1830: 5.45, 1905: 4.45, 1964: 3.45, 1976: 3.45, 2000: 3.45}
MMAX = 9.6
# an event takes the kind and error of a real event of its period within NEAR of its magnitude (the NMIN nearest
# where there are fewer)
NEAR, NMIN = 0.25, 8
# detection below the table: a cumulative normal ending ROLL[0] below the step with width ROLL[1] ("normal"), or
# one event in ten per 0.5 magnitude ("exp")
ROLL = (0.3, 0.15)


def pool(d):
    """Magnitude, kind and sigma of the real events per period, sorted by magnitude; `d` from gr.load()."""
    P = {}
    for a, b in zip(ERAS, ERAS[1:] + [9999]):
        e = d[(d.t >= a) & (d.t < b) & d.mw_sigma.notna()].sort_values("mw")
        P[a] = (e.mw.to_numpy(), e.mw_kind.to_numpy(), e.mw_sigma.to_numpy())
    return P


def dress(m, P, rng):
    """Kind and sigma of a real event near each magnitude of m."""
    pm, pk, ps = P
    lo, hi = np.searchsorted(pm, m - NEAR), np.searchsorted(pm, m + NEAR)
    few = hi - lo < NMIN
    c = np.clip(np.searchsorted(pm, m[few]), NMIN // 2, max(pm.size - NMIN // 2, NMIN // 2))
    lo[few], hi[few] = c - NMIN // 2, np.minimum(c + NMIN // 2, pm.size)
    i = np.minimum(lo + (rng.uniform(size=m.size) * (hi - lo)).astype(int), pm.size - 1)
    return pk[i], ps[i]


def weights(d, cls, table=TABLE):
    """The class weights of the real events of a class inside the table."""
    w, m, t = d["W_" + cls].to_numpy(), d.mw.to_numpy(), d.t.to_numpy()
    yr, _ = G.table_years(table, TE)
    return w[(w > 0) & (t >= yr[np.clip(G.kbin(m), 0, yr.size - 1)])]


def catalogue(b, n5, rng, P, table=TABLE, te=TE, wpool=None, errors=True, roll="normal", gen_from=GEN_FROM):
    """
    One synthetic catalogue.

    Parameters
    ----------
    b, n5 : float
        b and the yearly number of events at Mw >= 5 (bin 5.0 and above) of the class.
    P : dict
        Error pool of pool().
    wpool : array, optional
        Class weights to draw from. The events are then candidates of the class, each a member with a probability
        equal to its weight, so the weights sum to the number of members and n5 stays the rate of the class.
    roll : "normal" or "exp"
        Detection below the table (ROLL).
    errors : bool
        False: observed magnitude = true magnitude (the listed sigma is kept).

    Returns
    -------
    dict of arrays in time order: m (observed, 0.1 grid), mt (true), t, sig, kind, w
    """
    wbar = 1.0 if wpool is None else wpool.mean()
    T, M, K, S = [], [], [], []
    for a, e in zip(ERAS, ERAS[1:] + [te]):
        g = gen_from[a]
        n = rng.poisson(n5 / wbar * 10 ** (b * (4.95 - g)) * (e - a))
        m = g + rng.exponential(1 / (b * G.LN10), n)
        m = m[m < MMAX]
        kk, ss = dress(m, P[a], rng)
        T.append(rng.uniform(a, e, m.size)), M.append(m), K.append(kk), S.append(ss)
    t, mt, kind, sig = (np.concatenate(v) for v in (T, M, K, S))
    m = np.round(np.rint((mt + (rng.normal(0, sig) if errors else 0)) / G.DM) * G.DM, 1)
    # completeness: every event at or above the table is kept
    mc = np.full(m.size, 99.0)
    for mf, y in sorted(table)[::-1]:
        mc[t >= y] = mf
    below = ndtr((m - mc + ROLL[0]) / ROLL[1]) if roll == "normal" else 10 ** (-(mc - m) / 0.5)
    keep = (m >= G.M0 - 1e-6) & (rng.uniform(size=m.size) < np.where(m >= mc - 1e-6, 1.0, below))
    o = np.argsort(t[keep])
    w = np.ones(o.size) if wpool is None else rng.choice(wpool, o.size)
    return dict(m=m[keep][o], mt=mt[keep][o], t=t[keep][o], sig=sig[keep][o], kind=kind[keep][o], w=w)


def truth(b, n5, M):
    return n5 * 10 ** (-b * (np.asarray(M, float) - 5.0))

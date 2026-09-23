import numpy as np

LN10 = np.log(10.0)


# completeness

def since(m, steps):
    """Completeness start year per magnitude: the step with the largest Mc <= m."""
    s = sorted(steps)
    mc = np.array([x[0] for x in s], float)
    y0 = np.array([x[1] for x in s], float)
    i = np.searchsorted(mc, np.asarray(m, float) + 1e-6, side="right") - 1
    return np.where(i >= 0, y0[np.clip(i, 0, None)], np.nan)


def mc_of(m, steps):
    """Mc of the completeness step each magnitude falls in."""
    s = sorted(steps)
    mc = np.array([x[0] for x in s], float)
    i = np.searchsorted(mc, np.asarray(m, float) + 1e-6, side="right") - 1
    return np.where(i >= 0, mc[np.clip(i, 0, None)], np.nan)


def complete(df, steps):
    """Mask of events recorded after the completeness year of their magnitude."""
    y = since(df["mag"].to_numpy(), steps)
    return np.isfinite(y) & (df["year"].to_numpy() >= y)


def obs_cum(df, steps, t_end, grid):
    """Observed N(>=M) per year from complete events, each weighted 1/T(M)."""
    m = df["mag"].to_numpy()
    w = 1.0 / (t_end - since(m, steps))
    return np.array([w[m >= g - 1e-6].sum() for g in grid])


def audit(df, steps, t_end):
    """Band rate density per completeness step; it must fall with magnitude."""
    s = sorted(steps)
    rows, msg, prev = [], [], None
    for i, (mc, y0) in enumerate(s):
        hi = s[i + 1][0] if i + 1 < len(s) else 11.0
        n = int(((df["mag"] >= mc - 1e-6) & (df["mag"] < hi - 1e-6) & (df["year"] >= y0)).sum())
        r = n / (t_end - y0) / max(hi - mc, 0.1)
        rows.append({"mc": mc, "since": y0, "band_hi": hi, "n": n, "rate_density": r})
        if prev is not None and prev > 0 and r > 1.3 * prev:
            msg.append(f"band {mc}-{hi}: rate density rises {prev:.3g} -> {r:.3g}; "
                       f"step {mc}@{y0} likely too early")
        prev = r
    return rows, msg


# a-b estimation

def _beta(ctr, n, t):
    beta = LN10
    mbar = (n * ctr).sum() / n.sum()
    for _ in range(200):
        w = t * np.exp(-beta * ctr)
        s1, s2, s3 = w.sum(), (w * ctr).sum(), (w * ctr ** 2).sum()
        step = (s2 / s1 - mbar) / ((s2 / s1) ** 2 - s3 / s1)
        beta -= step
        if abs(step) < 1e-10:
            break
    return beta


def weichert(m, steps, t_end, mmin, dm, nboot=0, seed=0, b=None):
    """
    Weichert (1980) maximum-likelihood b and rate for unequal periods.

    Pass complete events only (see complete). Bin k covers
    [mmin + k dm, mmin + (k+1) dm) and is observed from the completeness
    year of its lower edge to t_end.

    Parameters
    ----------
    m : array
        Magnitudes of complete events.
    steps : list of (Mc, since_year)
    t_end : float
        End of the catalog, decimal year.
    mmin, dm : float
        Fit floor and bin width.
    nboot : int
        Bootstrap resamples for b_err (0 = none).
    b : float, optional
        Fixed b: only the rate is estimated (for classes borrowing b).

    Returns
    -------
    dict
        b, b_err, rate (annual N(M >= mmin)), mmin, n.
    """
    m = np.asarray(m, float)
    m = m[m >= mmin - 1e-6]
    out = {"b": np.nan, "b_err": np.nan, "rate": np.nan, "mmin": mmin, "n": int(len(m))}
    if len(m) < (1 if b is not None else 10):
        return out
    nb = int(np.floor((m.max() - mmin) / dm + 1e-6)) + 1
    lo = mmin + dm * np.arange(nb)
    ctr = lo + dm / 2
    t = t_end - since(lo, steps)
    if not np.all(np.isfinite(t) & (t > 0)):
        raise ValueError(f"fit floor {mmin} below the completeness table or t_end too early")
    k = np.floor((m - mmin) / dm + 1e-6).astype(int)
    n = np.bincount(k, minlength=nb).astype(float)
    beta = _beta(ctr, n, t) if b is None else b * LN10
    w = np.exp(-beta * ctr)
    out["b"] = beta / LN10
    out["rate"] = n.sum() * w.sum() / (t * w).sum()
    if nboot and b is None:
        rng = np.random.default_rng(seed)
        bs = []
        with np.errstate(all="ignore"):
            for _ in range(nboot):
                x = _beta(ctr, np.bincount(rng.choice(k, len(k)), minlength=nb).astype(float), t)
                if np.isfinite(x) and 0 < x < 5 * LN10:
                    bs.append(x)
        out["b_err"] = float(np.std(bs) / LN10) if len(bs) > nboot / 2 else np.nan
    return out


def kijko_smit(df, steps, t_end, mmin, dm):
    """
    Kijko & Smit (2012): Aki-Utsu b per completeness period, combined, and
    the Poisson rate of M >= mmin given that b. Comparison only.
    """
    s = sorted(steps, key=lambda x: x[1])
    ends = [y for _, y in s[1:]] + [t_end]
    ns, bet, ts, mcs = [], [], [], []
    for (mc, y0), y1 in zip(s, ends):
        mc = max(mc, mmin)
        sub = df[(df["year"] >= y0) & (df["year"] < y1) & (df["mag"] >= mc - 1e-6)]
        if len(sub) < 5:
            continue
        ns.append(len(sub))
        bet.append(1.0 / (sub["mag"].mean() - (mc - dm / 2)))
        ts.append(y1 - y0)
        mcs.append(mc)
    if not ns:
        return np.nan, np.nan
    ns = np.array(ns, float)
    b = ns.sum() / (ns / np.array(bet)).sum() / LN10
    rate = ns.sum() / (np.array(ts) * 10 ** (-b * (np.array(mcs) - mmin))).sum()
    return b, rate


# magnitude-frequency shapes

def m0(m, c=9.05):
    """Seismic moment in N m; c = 9.05 (Hanks & Kanamori) or 9.1 (IASPEI)."""
    return 10 ** (1.5 * np.asarray(m, float) + c)


def cum(form, b, mmin, mmax, m, c=9.05):
    """
    N(>=m) for unit rate at mmin, both forms hard-truncated at mmax.

    tgr is the doubly truncated GR. tapered is the Kagan tapered Pareto with
    corner moment at mmax, truncated and renormalized at mmax (beta = 2b/3).
    """
    m = np.asarray(m, float)
    if form == "tgr":
        n = (10 ** (-b * m) - 10 ** (-b * mmax)) / (10 ** (-b * mmin) - 10 ** (-b * mmax))
        return np.where(m > mmax, 0.0, np.clip(n, 0, None))
    be = 2.0 * b / 3.0
    tap = lambda x: (m0(mmin, c) / m0(x, c)) ** be * np.exp((m0(mmin, c) - m0(x, c)) / m0(mmax, c))
    n = (tap(m) - tap(mmax)) / (1.0 - tap(mmax))
    return np.where(m > mmax, 0.0, np.clip(n, 0, None))


def mpr(form, b, mmin, mmax, c=9.05, dm=0.01):
    """Total moment rate of the MFD per unit rate at mmin (N m / yr)."""
    g = mmin + dm * np.arange(int(round((mmax - mmin) / dm)) + 1)
    n = cum(form, b, mmin, mmax, g, c)
    return (np.maximum(n[:-1] - n[1:], 0) * m0(g[:-1] + dm / 2, c)).sum()


def inc(lam, form, b, mmin, mmax, dm, c=9.05):
    """Incremental rates on bins of width dm from mmin to mmax."""
    e = mmin + dm * np.arange(int(round((mmax - mmin) / dm)) + 1)
    n = lam * cum(form, b, mmin, mmax, e, c)
    return np.maximum(n[:-1] - n[1:], 0.0), e

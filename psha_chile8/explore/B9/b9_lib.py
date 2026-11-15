"""B9: data access and estimators shared by the B9 scripts. Every estimator takes event weights."""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAT = ROOT / "catalog/frozen/2026-11-14/catalog_2026-11-14c.csv"
CACHE, FIG, TAB = HERE / "cache", HERE / "figs", HERE / "tables"

DM, M0 = 0.1, 4.5
MTOP = 9.7
LN10 = np.log(10)
# family weight column, sub-class column, sub-class value
CLASSES = {"interface": ("w_interface", "sub_interface", "interface"),
           "antarctic_interface": ("w_interface", "sub_interface", "antarctic_interface"),
           "intraslab_shallow": ("w_inslab", "sub_inslab", "intraslab_shallow"),
           "intraslab_intermediate": ("w_inslab", "sub_inslab", "intraslab_intermediate"),
           "jujuy_nest": ("w_inslab", "sub_inslab", "jujuy_nest"),
           "forearc": ("w_crustal", "sub_crustal", "forearc"), "arc": ("w_crustal", "sub_crustal", "arc"),
           "backarc": ("w_crustal", "sub_crustal", "backarc"), "patagonia": ("w_crustal", "sub_crustal", "patagonia"),
           "outer_rise": ("w_outer_rise", None, None)}
FIT = ["interface", "intraslab_shallow", "intraslab_intermediate", "jujuy_nest", "forearc", "arc", "backarc", "patagonia"]
# interface segments of psha_chile7/interface/config.py (S to N), Mmax of DECISIONS
SEG = {"seg1 45.6–37° S": (-45.6, -37.0), "seg2 37–32° S": (-37.0, -32.0), "seg3 32–26° S": (-32.0, -26.0),
       "seg4 26–17.6° S": (-26.0, -17.6)}
REG = {"north": (-26.0, -15.0), "central-north": (-32.0, -26.0), "central": (-37.0, -32.0), "south": (-46.0, -37.0),
       "far south": (-60.0, -46.0)}
PERIODS = [(1964, 1976), (1976, 1990), (1990, 2000), (2000, 2011), (2011, 2027)]
NETWORK = [1964, 1976, 1990, 2000, 2007, 2012]


def load():
    """Events of Mw >= 4.5 in the domain with decimal year `t`, bin index `k` and one weight column per class."""
    f = CACHE / "m45.pkl"
    if f.exists():
        return pd.read_pickle(f)
    d = pd.read_csv(CAT, low_memory=False)
    d = d[(d.mw >= M0 - 1e-9) & d.in_domain].copy()
    y = d.time.str[:4].astype(int)
    rest = pd.to_datetime("2000" + d.time.str[4:19], errors="coerce")
    d["t"] = y + ((rest.dt.dayofyear - 1) + rest.dt.hour / 24 + rest.dt.minute / 1440) / 366
    d["k"] = np.rint((d.mw - M0) / DM).astype(int)
    for c, (w, s, v) in CLASSES.items():
        d["W_" + c] = d[w] * (1 if s is None else (d[s] == v))
    d = d.sort_values("t").reset_index(drop=True)
    CACHE.mkdir(exist_ok=True)
    d.to_pickle(f)
    return d


def tend(d):
    return float(d.t.max()) + 1 / 366


def kbin(m):
    return np.rint((np.asarray(m, float) - M0) / DM).astype(int)


def nbins():
    return kbin(MTOP) + 1


def centres():
    return M0 + DM * np.arange(nbins())


# completeness tables: list of (magnitude from, complete since), any order
def table_years(table, t_end):
    """Year of completeness per 0.1 bin (inf below the first step) and the observation time per bin."""
    m = centres()
    tb = sorted(table)
    yr = np.full(m.size, np.inf)
    for mf, y in tb:
        yr[m >= mf - 1e-6] = y
    T = np.where(np.isfinite(yr), t_end - yr, 0.0)
    return yr, T


def counts(k, t, w, yr):
    """Weighted count per bin of the events inside the completeness table."""
    ok = (k >= 0) & (k < yr.size)
    k, t, w = k[ok], t[ok], w[ok]
    ok = t >= yr[k]
    return np.bincount(k[ok], w[ok], minlength=yr.size)


def weichert(n, T, bfix=None):
    """Weichert (1980) for binned counts with unequal observation times.

    Parameters
    ----------
    n : array (..., nbin)
        Weighted counts per 0.1 bin; leading axes are replicates.
    T : array (nbin,)
        Observation time per bin, 0 where the bin is not used.
    bfix : float, optional
        b held fixed; the rate is refitted.

    Returns
    -------
    b, rate : arrays
        b-value and yearly rate at and above the lower edge of the first used bin.
    """
    n = np.atleast_2d(np.asarray(n, float))
    m = centres()
    use = T > 0
    m, T, n = m[use], T[use], n[:, use]
    N = n.sum(1)
    mbar = (n * m).sum(1) / np.where(N > 0, N, 1)
    if bfix is None:
        be = np.full(n.shape[0], 2.0)
        for _ in range(60):
            e = T * np.exp(-np.outer(be, m - m[0]))
            s0, s1, s2 = e.sum(1), (e * m).sum(1), (e * m * m).sum(1)
            g = s1 / s0 - mbar
            dg = -(s2 / s0 - (s1 / s0) ** 2)
            step = np.clip(g / np.where(dg != 0, dg, -1e-9), -1, 1)
            be = np.clip(be - step, 0.05, 12)
            if np.all(np.abs(step) < 1e-9):
                break
    else:
        be = np.full(n.shape[0], bfix * LN10)
    e = np.exp(-np.outer(be, m - m[0]))
    rate = N * e.sum(1) / (T * e).sum(1)
    # e sums the bin masses up to MTOP; the rate is for M >= m[0] - DM/2
    b = be / LN10
    b = np.where(N > 1, b, np.nan)
    return b, rate, m[0] - DM / 2


def n_ge(b, rate, m_lo, M):
    """Yearly rate of M >= M (bin centre M and above) from a fit anchored at the edge m_lo."""
    return rate * 10 ** (-b * (M - DM / 2 - m_lo))


def fit(k, t, w, table, t_end, nboot=0, rng=None, bfix=None, floor=None, top=None, grp=None):
    """Weichert fit of one class on one completeness table, with an event bootstrap.

    floor cuts the table from below; top leaves out the bins at and above that magnitude (the rate is still the
    rate of the whole Gutenberg-Richter line above the first bin); events at or after t_end are not counted; grp
    numbers the events the rows belong to (rows of one event are resampled together).
    Returns a dict with b, rate, m_lo, n (weighted events used) and, with nboot > 0, the replicates `bb`, `rr`.
    """
    tb = [(max(mf, floor), y) for mf, y in table] if floor is not None else list(table)
    tb = sorted({mf: y for mf, y in sorted(tb, key=lambda q: (q[0], -q[1]))}.items())
    yr, T = table_years(tb, t_end)
    if top is not None:
        T[centres() >= top - 1e-6] = 0.0
        yr[centres() >= top - 1e-6] = np.inf
    grp = np.arange(k.size) if grp is None else grp
    ok = (k >= 0) & (k < yr.size)
    k, t, w, grp = k[ok], t[ok], w[ok], grp[ok]
    ok = (t >= yr[k]) & (w > 0) & (t < t_end)
    k, w, grp = k[ok], w[ok], np.unique(grp[ok], return_inverse=True)[1]
    n = np.bincount(k, w, minlength=yr.size)

    def full(b, r, m_lo):
        return r if top is None else r / (1 - 10 ** (-b * (top - DM / 2 - m_lo)))

    b, r, m_lo = weichert(n, T, bfix)
    r = full(b, r, m_lo)
    out = dict(b=b[0], rate=r[0], m_lo=m_lo, n=n.sum(), nev=int(grp.max() + 1) if grp.size else 0, T=T, cnt=n)
    if nboot and k.size > 2:
        rng = rng or np.random.default_rng(1)
        # Poisson bootstrap of the events, weights carried
        mult = rng.poisson(1.0, (nboot, grp.max() + 1))
        nb = np.zeros((nboot, yr.size))
        for j in range(nboot):
            nb[j] = np.bincount(k, w * mult[j][grp], minlength=yr.size)
        bb, rr, _ = weichert(nb, T, bfix)
        out.update(bb=bb, rr=full(bb, rr, m_lo))
    return out


def tinti(m, w, mc):
    """Maximum-likelihood b for 0.1-binned magnitudes at and above the bin centre mc (Tinti and Mulargia 1987)."""
    ok = m >= mc - 1e-6
    sw = w[ok].sum()
    if sw <= 1:
        return np.nan, sw
    mean = (m[ok] * w[ok]).sum() / sw
    if mean - mc <= 0:
        return np.nan, sw
    return np.log(1 + DM / (mean - mc)) / DM / LN10, sw


def shibolt(m, w, mc, b):
    ok = m >= mc - 1e-6
    sw = w[ok].sum()
    mean = (m[ok] * w[ok]).sum() / sw
    var = (w[ok] * (m[ok] - mean) ** 2).sum() / max(sw * (sw - 1), 1)
    return 2.3 * b * b * np.sqrt(var)


def bpositive(m, w, dmc=0.2):
    """b-positive (van der Elst 2021): b from the positive magnitude differences of consecutive events.

    m in time order. A pair counts with the product of the two weights. Differences at and above dmc.
    """
    d = np.rint(np.diff(m) / DM) * DM
    ww = w[1:] * w[:-1]
    return tinti(d, ww, dmc)


def mc_maxc(m, w, corr=0.2):
    h = np.bincount(kbin(m), w)
    return M0 + DM * np.argmax(h) + corr


def mc_bstab(m, w, span=0.5, nmin=50):
    """Lowest cut where b differs from the mean b of the next `span` by less than its Shi-Bolt error (Cao and Gao
    2002; Woessner and Wiemer 2005)."""
    cuts = np.arange(M0, 7.01, DM)
    b = np.array([tinti(m, w, c)[0] for c in cuts])
    nn = np.array([w[m >= c - 1e-6].sum() for c in cuts])
    ns = int(round(span / DM))
    for i, c in enumerate(cuts[:-ns]):
        if nn[i] < nmin or np.isnan(b[i]):
            break
        if abs(np.nanmean(b[i:i + ns + 1]) - b[i]) <= shibolt(m, w, c, b[i]):
            return c
    return np.nan


def mc_ks(m, w, p=0.1, nsim=200, ncap=3000, nmin=50, rng=None):
    """Lowest cut where a Kolmogorov-Smirnov test does not reject the binned exponential with the fitted b (Clauset
    et al. 2009). The p-value comes from simulated samples of the weighted size, capped at ncap."""
    rng = rng or np.random.default_rng(2)
    for c in np.arange(M0, 7.01, DM):
        ok = m >= c - 1e-6
        sw = w[ok].sum()
        if sw < nmin:
            break
        b, _ = tinti(m, w, c)
        if np.isnan(b):
            break
        kk = kbin(m[ok]) - kbin(c)
        nb = kk.max() + 30
        cdf = 1 - 10 ** (-b * DM * (np.arange(nb) + 1))
        emp = np.cumsum(np.bincount(kk, w[ok], minlength=nb)) / sw
        D = np.abs(emp - cdf).max()
        n = int(min(sw, ncap))
        s = np.floor(rng.exponential(1 / (b * LN10), (nsim, n)) / DM).astype(int)
        s = np.minimum(s, nb - 1)
        Ds = np.empty(nsim)
        for j in range(nsim):
            bj = np.log(1 + 1 / s[j].mean()) / DM / LN10
            Ds[j] = np.abs(np.cumsum(np.bincount(s[j], minlength=nb)) / n - (1 - 10 ** (-bj * DM * (np.arange(nb) + 1)))).max()
        if (Ds >= D).mean() >= p:
            return c
    return np.nan


def stepp(t, w, t_end, k=2.0, tref=20.0, step=1.0):
    """Stepp (1972) for one magnitude band: the longest span back from the end over which the mean rate stays
    within k standard errors of the reference rate (the last `tref` years). Returns the year and the curve."""
    T = np.arange(step, t_end - np.floor(t.min()) + step, step) if t.size else np.array([])
    if not T.size or w[t >= t_end - tref].sum() < 3:
        return np.nan, None
    N = np.array([w[t >= t_end - x].sum() for x in T])
    lam = N / T
    ref = w[t >= t_end - tref].sum() / tref
    ok = np.abs(lam - ref) <= k * np.sqrt(ref / T)
    ok |= T <= tref
    bad = np.where(~ok & (lam < ref))[0]
    Tc = T[bad[0] - 1] if bad.size else T[-1]
    return t_end - Tc, pd.DataFrame(dict(T=T, lam=lam, sd=np.sqrt(lam / T), ref=ref))


def changepoint(y, c, phi=None, min_len=5):
    """Change points of yearly counts by binary segmentation of a Poisson likelihood with a BIC penalty, the
    penalty scaled by the dispersion phi (variance over mean of the detrended counts; 1 = Poisson).

    Returns the list of break years (first year of each new segment) and the segment rates.
    """
    c = np.asarray(c, float)
    if phi is None:
        r = pd.Series(c).rolling(11, center=True, min_periods=3).mean().to_numpy()
        phi = max(1.0, np.nanmean((c - r) ** 2) / max(np.nanmean(r), 1e-9))

    def ll(x):
        s = x.sum()
        return s * np.log(s / x.size) - s if s > 0 else 0.0

    pen = phi * np.log(max(c.size, 2)) * 1.5
    segs, out = [(0, c.size)], []
    while segs:
        a, b = segs.pop()
        best, at = 0, None
        for i in range(a + min_len, b - min_len + 1):
            g = ll(c[a:i]) + ll(c[i:b]) - ll(c[a:b])
            if g > best:
                best, at = g, i
        if at is not None and best > pen:
            out.append(at)
            segs += [(a, at), (at, b)]
    out = sorted(out)
    ed = [0] + out + [c.size]
    return [int(y[i]) for i in out], [c[ed[i]:ed[i + 1]].mean() for i in range(len(ed) - 1)], phi


def complete_since(y, c, drop=0.6, **kw):
    """Year from which the yearly rate of a band is steady: the last change point at which the rate rises so that
    the rate before is below `drop` times the rate after it."""
    br, rates, phi = changepoint(y, c, **kw)
    yr = y[0]
    for i, b in enumerate(br):
        if rates[i] < drop * np.mean(rates[i + 1:]):
            yr = b
    return yr, br, rates, phi


# magnitude error
def ceus(k, w, sig, b, mode="ceus"):
    """Counts corrected for magnitude error (CEUS-SSC 2012, section 3.3.1, observed magnitudes).

    ceus: the event moves to E[M] = M - beta sigma^2 and counts N* = exp(beta^2 sigma^2 / 2); the moved magnitude
    is shared linearly between the two neighbouring 0.1 bins. plain: no move, weight exp(-beta^2 sigma^2 / 2).
    Returns bin indices and weights (twice the length for ceus).
    """
    be = b * LN10
    if mode == "plain":
        return k, w * np.exp(-be ** 2 * sig ** 2 / 2), np.arange(k.size)
    x = k - be * sig ** 2 / DM
    lo = np.floor(x).astype(int)
    f = x - lo
    ns = np.exp(be ** 2 * sig ** 2 / 2)
    i = np.arange(k.size)
    return np.r_[lo, lo + 1], np.r_[w * ns * (1 - f), w * ns * f], np.r_[i, i]


# declustering
def km(lon1, lat1, lon2, lat2):
    p = np.pi / 180
    a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def gk_window(m):
    """Gardner and Knopoff (1974) windows as fitted by van Stiphout et al. (2012): km, days."""
    d = 10 ** (0.1238 * m + 0.983)
    tt = np.where(m >= 6.5, 10 ** (0.032 * m + 2.7389), 10 ** (0.5409 * m - 0.547))
    return d, tt


def gardner_knopoff(t, lon, lat, m, fs=1.0):
    """Mainshock flags by the window method, largest event first; foreshock window = fs times the aftershock one."""
    main = np.ones(t.size, bool)
    done = np.zeros(t.size, bool)
    for i in np.argsort(-m, kind="stable"):
        if done[i]:
            continue
        d, tt = gk_window(m[i])
        dt = (t - t[i]) * 365.25
        near = (dt <= tt) & (dt >= -fs * tt) & ~done
        near[i] = False
        idx = np.where(near)[0]
        idx = idx[km(lon[i], lat[i], lon[idx], lat[idx]) <= d]
        main[idx] = False
        done[idx] = True
        done[i] = True
    return main


def nearest_neighbour(t, lon, lat, m, b=1.0, df=1.6):
    """Zaliapin and Ben-Zion (2013): nearest-neighbour distance eta, rescaled time and distance, parent index.
    t in years, time order."""
    n = t.size
    eta, T, R, par = np.full(n, np.inf), np.full(n, np.nan), np.full(n, np.nan), np.full(n, -1)
    for j in range(1, n):
        dt = t[j] - t[:j]
        r = np.maximum(km(lon[j], lat[j], lon[:j], lat[:j]), 1.0)
        dt = np.maximum(dt, 1e-7)
        e = dt * r ** df * 10 ** (-b * m[:j])
        i = np.argmin(e)
        eta[j], par[j] = e[i], i
        T[j] = dt[i] * 10 ** (-0.5 * b * m[i])
        R[j] = r[i] ** df * 10 ** (-0.5 * b * m[i])
    return eta, T, R, par


def nn_threshold(eta):
    """Threshold of log10 eta between the clustered and background modes (two-Gaussian mixture, equal posterior)."""
    from sklearn.mixture import GaussianMixture
    x = np.log10(eta[np.isfinite(eta)]).reshape(-1, 1)
    g = GaussianMixture(2, random_state=0, n_init=3).fit(x)
    lo, hi = np.sort(g.means_.ravel())
    xs = np.linspace(lo, hi, 2000).reshape(-1, 1)
    p = g.predict_proba(xs)[:, np.argmin(g.means_.ravel())]
    return float(xs[np.argmin(np.abs(p - 0.5)), 0])


# synthetic catalogues
def synth(b, rate, table, t0, t_end, rng, sigma=0.0, mmax=9.5):
    """Gutenberg-Richter catalogue on the 0.1 grid, thinned by a completeness table: below the table an event is
    kept with a probability that falls by a factor 10 per 0.5 magnitude. rate is per year at M >= M0 - DM/2."""
    n = rng.poisson(rate * (t_end - t0))
    m = M0 - DM / 2 + rng.exponential(1 / (b * LN10), n)
    m = m[m < mmax]
    t = rng.uniform(t0, t_end, m.size)
    if sigma:
        m = m + rng.normal(0, sigma, m.size)
    m = np.round(np.rint(m / DM) * DM, 1)
    keep = m >= M0 - 1e-6
    m, t = m[keep], t[keep]
    tb = sorted(table)
    mc = np.full(m.size, 99.0)
    for mf, y in tb[::-1]:
        mc[t >= y] = mf
    p = np.where(m >= mc - 1e-6, 1.0, 10 ** (-(mc - m) / 0.5 * 1.0))
    keep = rng.uniform(size=m.size) < p
    o = np.argsort(t[keep])
    return t[keep][o], m[keep][o]

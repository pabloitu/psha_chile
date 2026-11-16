"""Gutenberg-Richter estimators on a completeness table (plan B11).

Every estimator takes event weights (the class weight of the event) and, where `sig` is given, counts each event
exp(-beta^2 sigma^2 / 2) with the beta of its own fit (DECISIONS, Magnitudes). Magnitudes are 0.1 bin centres; a
completeness table is a list of (magnitude from, complete since). A fit is a dict with the shape of the line
("gr" open, "trunc" cut at mmax, "taper" with a corner magnitude), b, the yearly rate at and above the edge m_lo,
and what the large-event check needs (T, cnt).
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats
from scipy.special import ndtr

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "catalog/frozen/2026-11-16c/catalog_2026-11-16c.csv"

DM, M0, MTOP = 0.1, 3.5, 9.7
LN10 = np.log(10)
# family weight column, sub-class column, sub-class value
CLASSES = {"interface": ("w_interface", "sub_interface", "interface"),
           "intraslab_shallow": ("w_inslab", "sub_inslab", "intraslab_shallow"),
           "intraslab_intermediate": ("w_inslab", "sub_inslab", "intraslab_intermediate"),
           "jujuy_nest": ("w_inslab", "sub_inslab", "jujuy_nest"),
           "forearc": ("w_crustal", "sub_crustal", "forearc"), "arc": ("w_crustal", "sub_crustal", "arc"),
           "backarc": ("w_crustal", "sub_crustal", "backarc"), "patagonia": ("w_crustal", "sub_crustal", "patagonia")}


def load(f=CAT, mlow=M0):
    """Events of the frozen catalogue in the domain from Mw `mlow`, with decimal year `t` and a weight column
    `W_<class>` per class, in time order."""
    d = pd.read_csv(f, low_memory=False)
    d = d[(d.mw >= mlow - 1e-9) & d.in_domain].copy()
    rest = pd.to_datetime("2000" + d.time.str[4:19], errors="coerce")
    d["t"] = d.time.str[:4].astype(int) + ((rest.dt.dayofyear - 1) + rest.dt.hour / 24 + rest.dt.minute / 1440) / 366
    for c, (w, s, v) in CLASSES.items():
        d["W_" + c] = d[w] * (d[s] == v)
    return d.sort_values("t").reset_index(drop=True)


def tend(d):
    return float(d.t.max()) + 1 / 366


def kbin(m):
    return np.rint((np.asarray(m, float) - M0) / DM).astype(int)


def centres():
    return M0 + DM * np.arange(kbin(MTOP) + 1)


def table_years(table, te, floor=None, top=None):
    """Year of completeness per 0.1 bin (inf where the bin is not used) and the observation time per bin.

    floor cuts the table from below; top leaves out the bins at and above that magnitude."""
    m = centres()
    yr = np.full(m.size, np.inf)
    for mf, y in sorted(table):
        yr[m >= max(mf, floor or mf) - 1e-6] = y
    if top is not None:
        yr[m >= top - 1e-6] = np.inf
    return yr, np.where(np.isfinite(yr), te - yr, 0.0)


def magw(sig, b):
    """Count of an event with magnitude error sigma: exp(-beta^2 sigma^2 / 2) (CEUS-SSC 2012, eq. 3.3.1-1)."""
    return np.exp(-(b * LN10) ** 2 * np.asarray(sig, float) ** 2 / 2)


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
        b and the yearly rate of the used bins together (a line cut at the last used bin).
    m_lo : float
        Lower edge of the first used bin.
    """
    n = np.atleast_2d(np.asarray(n, float))
    use = T > 0
    m, T, n = centres()[use], T[use], n[:, use]
    N = n.sum(1)
    mbar = (n * m).sum(1) / np.where(N > 0, N, 1)
    if bfix is None:
        be = np.full(n.shape[0], 2.0)
        for _ in range(60):
            e = T * np.exp(-np.outer(be, m - m[0]))
            s0, s1, s2 = e.sum(1), (e * m).sum(1), (e * m * m).sum(1)
            dg = -(s2 / s0 - (s1 / s0) ** 2)
            step = np.clip((s1 / s0 - mbar) / np.where(dg != 0, dg, -1e-9), -1, 1)
            be = np.clip(be - step, 0.05, 12)
            if np.all(np.abs(step) < 1e-9):
                break
    else:
        be = np.broadcast_to(np.asarray(bfix, float) * LN10, n.shape[:1]).copy()
    e = np.exp(-np.outer(be, m - m[0]))
    return np.where(N > 1, be / LN10, np.nan), N * e.sum(1) / (T * e).sum(1), m[0] - DM / 2


def moment(m):
    return 10 ** (1.5 * np.asarray(m, float) + 9.05)


def kagan_corner(mx, b):
    """Corner magnitude of the tapered line with the moment rate of a line cut at the magnitude edge mx and the
    same b and rate above the threshold (Kagan 2002b, eq. 12): M0c = M0x (beta / Gamma(2 - beta))^(1 / (1 - beta)),
    beta = 2b / 3."""
    from scipy.special import gamma
    be = 2 * np.asarray(b, float) / 3
    return mx + np.log10(be / gamma(2 - be)) / (1 - be) / 1.5


def surv(f, x):
    """Share of the events of a fit at and above the magnitude x (an edge), 1 at m_lo."""
    x = np.asarray(x, float)
    b, lo = np.asarray(f["b"], float), f["m_lo"]
    s = 10 ** (-b * (x - lo))
    if f["shape"] == "trunc":
        c = 10 ** (-b * (f["mmax"] - lo))
        s = np.clip((s - c) / (1 - c), 0, None)
    if f["shape"] == "taper":
        s = s * np.exp((moment(lo) - moment(x)) / moment(np.asarray(f["corner"], float)))
    return s


def n_ge(f, M):
    """Yearly rate at and above the bin centre M."""
    return f["rate"] * surv(f, np.asarray(M, float) - DM / 2)


def rates(f):
    """Yearly rate per 0.1 bin of the grid."""
    c = centres()
    return f["rate"] * (surv(f, c - DM / 2) - surv(f, c + DM / 2))


def loglik(f, n, T):
    """Poisson log-likelihood of binned counts under a fit, without the terms that do not depend on the fit."""
    lam = rates(f) * T
    u = T > 0
    if np.any((lam[u] <= 0) & (n[u] > 0)):
        return -np.inf
    ok = u & (lam > 0)
    return float((n[ok] * np.log(lam[ok])).sum() - lam[u].sum())


def ml_shape(n, T, m_lo, shape, corner=None, mmax=None, bfix=None):
    """Maximum-likelihood b of a tapered or truncated line on binned counts, the rate profiled out (b held at
    bfix where given)."""
    c = centres()
    u = T > 0
    N = n[u].sum()

    def nll(b):
        f = dict(shape=shape, b=b, m_lo=m_lo, corner=corner, mmax=mmax)
        p = (surv(f, c - DM / 2) - surv(f, c + DM / 2))[u]
        if np.any((p <= 0) & (n[u] > 0)):
            return 1e12
        k = p > 0
        return -(n[u][k] * np.log(p[k] * T[u][k])).sum() + N * np.log((p * T[u]).sum())

    b = bfix if bfix is not None else optimize.minimize_scalar(nll, bounds=(0.2, 3.0), method="bounded", options=dict(xatol=1e-6)).x
    f = dict(shape=shape, b=b, m_lo=m_lo, corner=corner, mmax=mmax)
    p = surv(f, c - DM / 2) - surv(f, c + DM / 2)
    return b, N / (p * T).sum(), -nll(b)


def fit(m, t, w, table, te, sig=None, shape="gr", top=None, corner=None, bfix=None, floor=None, nboot=0, rng=None,
        bw=None, bboot=None):
    """Fit of one unit on a completeness table, with an event bootstrap.

    Parameters
    ----------
    m, t, w : arrays
        Magnitude (0.1 grid), decimal year and class weight of the events.
    table : list of (magnitude, year)
    te : float
        End of the catalogue.
    sig : array, optional
        Magnitude error; each event then counts exp(-beta^2 sigma^2 / 2), beta from this fit.
    bw : float, optional
        b of that count instead of the b of this fit (to compare shapes on the same counts).
    shape : "gr", "trunc", "taper" or "taper_free"
        gr: Weichert (1980), an open line. trunc: the same likelihood, the line ends at top - DM / 2 (needs top).
        taper: tapered Gutenberg-Richter (Kagan 2002) with the corner magnitude given; taper_free: corner fitted.
    top : float, optional
        Bins at and above this magnitude are left out of the likelihood (the largest magnitude of the class plus
        one bin). For gr and taper the rate is still that of the whole line.
    bfix : float, optional
        b held fixed, the rate refitted (gr and trunc).
    nboot : int
        Poisson bootstrap of the events, the weights carried.
    bboot : array (nboot,), optional
        With bfix: the b of each replicate (the replicates of the unit the b is taken from).

    Returns
    -------
    dict : shape, b, rate (yearly, at and above m_lo), m_lo, mmax, corner, n (weighted events), nev, T, cnt, lnL,
        npar, w (the count of every event used in the fit, 0 outside the table) and, with nboot, bb, rr (and cc).
    """
    m, t, w = np.asarray(m, float), np.asarray(t, float), np.asarray(w, float)
    yr, T = table_years(table, te, floor, top)
    k = kbin(m)
    inb = (k >= 0) & (k < yr.size)
    ok = inb & (w > 0) & (t < te)
    ok[ok] = t[ok] >= yr[k[ok]]
    free = shape == "taper_free"
    shp = "taper" if free else shape
    mmax = top - DM / 2 if top is not None else None

    def one(n, bfix=bfix):
        if shp == "taper":
            m_lo = centres()[T > 0][0] - DM / 2
            if free:
                best = max((ml_shape(n, T, m_lo, shp, c) + (c,) for c in np.arange(7.5, 10.51, 0.05)), key=lambda q: q[2])
                return best[0], best[1], m_lo, best[3]
            b, r, _ = ml_shape(n, T, m_lo, shp, corner, bfix=bfix)
            return b, r, m_lo, corner
        b, r, m_lo = weichert(n, T, bfix)
        if shp == "gr" and top is not None:
            r = r / (1 - 10 ** (-b * (mmax - m_lo)))
        return b[0], r[0], m_lo, None

    cnt = lambda ww: np.bincount(k[ok], ww[ok], minlength=yr.size)
    ww = w
    b, r, m_lo, cor = one(cnt(ww))
    if sig is not None:
        for _ in range(6 if bw is None else 1):
            ww = w * magw(sig, b if bw is None else bw)
            b, r, m_lo, cor = one(cnt(ww))
    n = cnt(ww)
    f = dict(shape=shp, b=b, rate=r, m_lo=m_lo, mmax=mmax, corner=cor, n=n.sum(), nev=int(ok.sum()), T=T, cnt=n,
             npar=(1 if bfix is not None else 2) + free, w=np.where(ok, ww, 0.0))
    f["lnL"] = loglik(f, n, T)
    if nboot and ok.sum() > 2:
        rng = rng or np.random.default_rng(1)
        mult = rng.poisson(1.0, (nboot, int(ok.sum())))
        nb = np.zeros((nboot, yr.size))
        for j in range(nboot):
            nb[j] = np.bincount(k[ok], ww[ok] * mult[j], minlength=yr.size)
        if shp == "taper":
            q = [one(x) if bboot is None else one(x, bboot[j]) for j, x in enumerate(nb)]
            f.update(bb=np.array([v[0] for v in q]), rr=np.array([v[1] for v in q]), cc=np.array([v[3] for v in q], float))
        else:
            bb, rr, _ = weichert(nb, T, bfix if bboot is None else bboot)
            f.update(bb=bb, rr=rr / (1 - 10 ** (-bb * (mmax - m_lo))) if shp == "gr" and top is not None else rr)
    return f


def boot(f):
    """The bootstrap replicates of a fit as a fit (arrays in b, rate and corner)."""
    return dict(f, b=f["bb"], rate=f["rr"], corner=f.get("cc", f["corner"]))


def a_value(f):
    """a of the fit: N(>= M) = 10^(a - b M) for an open line, 10^(a - b M) - 10^(a - b mmax) for a line cut at mmax,
    and 10^(a - b M) times the taper (1 at m_lo) for a tapered line; M an edge."""
    r = f["rate"] / (1 - 10 ** (-f["b"] * (f["mmax"] - f["m_lo"]))) if f["shape"] == "trunc" else f["rate"]
    return np.log10(r) + f["b"] * f["m_lo"]


def check(f, M, q=(0.05, 0.95)):
    """Large-event check: events the fit expects inside the table at and above M, the weighted count observed
    there, and whether the count lies in the Poisson band of the expected number."""
    s = centres() >= M - 1e-6
    e, o = (rates(f) * f["T"])[s].sum(), f["cnt"][s].sum()
    lo, hi = stats.poisson.ppf(q, e)
    return e, o, bool(lo - 0.5 <= o <= hi + 0.5)


# estimators without the table
def aki_utsu(m, t, w, mc, since, te, sig=None):
    """Aki (1965) with the binning correction of Utsu (1965), on the events at and above the bin centre mc from
    `since`: b = log10(e) / (mean - (mc - DM / 2))."""
    s = (m >= mc - 1e-6) & (t >= since) & (t < te) & (w > 0)
    ww, b = w[s], np.nan
    for _ in range(6 if sig is not None else 1):
        b = np.log10(np.e) / ((m[s] * ww).sum() / ww.sum() - (mc - DM / 2))
        if sig is not None:
            ww = w[s] * magw(sig[s], b)
    wf = np.zeros(m.size)
    wf[s] = ww
    return dict(shape="gr", b=b, rate=ww.sum() / (te - since), m_lo=mc - DM / 2, mmax=None, corner=None, n=ww.sum(), w=wf)


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


def kijko_smit(m, t, w, table, te):
    """Kijko and Smit (2012): b from the Aki-Utsu values of the periods of a table, weighted by their events. A
    check of the table: it agrees with Weichert on a table that fits the catalogue."""
    tb = sorted(table)
    num, den = 0.0, 0.0
    for (mc, y0), y1 in zip(tb, [te] + [y for _, y in tb[:-1]]):
        s = (t >= y0) & (t < y1) & (m >= mc - 1e-6)
        bi, ni = tinti(m[s], w[s], mc)
        if ni > 1 and np.isfinite(bi):
            num, den = num + ni, den + ni / bi
    return num / den if den else np.nan


def bpositive(m, w, dmc=0.2):
    """b-positive (van der Elst 2021): b from the positive magnitude differences of consecutive events (m in time
    order); a pair counts with the product of the two weights. A check of b."""
    d = np.rint(np.diff(m) / DM) * DM
    return tinti(d, w[1:] * w[:-1], dmc)


def ogata_katsura(m, t, w, windows, te, mlow=M0, sig=None, start=None):
    """Joint fit of b and the detection of small events (Ogata and Katsura 1993): the magnitude density is the
    Gutenberg-Richter density times a cumulative normal with mean mu and width s. One detection curve per time
    window (the network changes), one b and one rate for all windows; binned Poisson likelihood on the events
    from `mlow`. The rate is that of the full line.

    Returns a fit dict with mu, s and mc95 (mu + 1.645 s) per window and the parameter vector p (a start for a
    refit) added."""
    win = [(a, min(e, te)) for a, e in windows if a < te]
    sel = (m >= mlow - 1e-6) & (t >= win[0][0]) & (t < te) & (w > 0)
    k = kbin(m[sel]) - kbin(mlow)
    j = np.searchsorted([a for a, _ in win], t[sel], side="right") - 1
    K, nb = len(win), k.max() + 1
    c = mlow + DM * np.arange(nb)
    lo = mlow - DM / 2
    T = np.array([e - a for a, e in win])[:, None]

    def lam(p):
        g = 10 ** (-p[0] * (c - DM / 2 - lo)) - 10 ** (-p[0] * (c + DM / 2 - lo))
        return T * g * ndtr((c - p[1:K + 1, None]) / np.exp(p[K + 1:, None]))

    def run(ww):
        n = np.zeros((K, nb))
        np.add.at(n, (j, k), ww)

        def nll(p):
            q = np.maximum(lam(p), 1e-300)
            return -(n * np.log(q)).sum() + n.sum() * np.log(q.sum())

        x0 = np.r_[1.0, np.full(K, 4.5), np.full(K, np.log(0.3))] if start is None else np.asarray(start)
        r = optimize.minimize(nll, x0, method="L-BFGS-B", bounds=[(0.3, 3.0)] + [(2.0, 7.0)] * K + [(np.log(0.03), np.log(1.5))] * K)
        return r.x, n.sum() / lam(r.x).sum()

    ww = w[sel]
    p, r = run(ww)
    if sig is not None:
        for _ in range(4):
            ww = w[sel] * magw(sig[sel], p[0])
            p, r = run(ww)
    wf = np.zeros(m.size)
    wf[sel] = ww
    mu, sd = p[1:K + 1], np.exp(p[K + 1:])
    return dict(shape="gr", b=p[0], rate=r, m_lo=lo, mmax=None, corner=None, n=ww.sum(), mu=mu, s=sd, mc95=mu + 1.645 * sd,
                w=wf, p=p)


def least_squares(f, floor=5.0):
    """Straight line through log10 of the cumulative yearly rates of a fit's counts (rate per bin = count over
    its observation time). For contrast only: the points are not independent and the fit is biased."""
    c, u = centres(), f["T"] > 0
    rate = np.where(u, f["cnt"] / np.where(u, f["T"], 1), 0.0)
    cum = np.cumsum(rate[::-1])[::-1]
    s = u & (cum > 0) & (c >= floor - 1e-6) & (f["cnt"] > 0)
    sl, ic = np.polyfit(c[s] - DM / 2, np.log10(cum[s]), 1)
    lo = c[s][0] - DM / 2
    return dict(shape="gr", b=-sl, rate=10 ** (ic + sl * lo), m_lo=lo, mmax=None, corner=None, n=f["n"], T=f["T"], cnt=f["cnt"])


def shrink(b, s):
    """Random-effects pooling of the b of the units of a family (DerSimonian and Laird 1986): family mean,
    between-unit variance and the b of every unit pulled toward the mean by its own error."""
    b, s = np.asarray(b, float), np.asarray(s, float)
    w = 1 / s ** 2
    mu = (w * b).sum() / w.sum()
    tau2 = max(0.0, ((w * (b - mu) ** 2).sum() - (b.size - 1)) / (w.sum() - (w ** 2).sum() / w.sum()))
    ws = 1 / (s ** 2 + tau2)
    mu = (ws * b).sum() / ws.sum()
    k = tau2 / (tau2 + s ** 2)
    return mu, tau2, mu + k * (b - mu)

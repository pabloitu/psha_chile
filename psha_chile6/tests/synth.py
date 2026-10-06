# Synthetic catalogs with a known truth, written without lib.gr so the tests do not check the
# code against itself: a doubly truncated GR in true magnitude, observed through a completeness
# table and optionally rounded to the nearest 0.1 as the real catalog is.

import numpy as np

STEPS = [(8.3, 1513), (6.8, 1900), (6.0, 1950), (5.2, 1976), (5.1, 1997), (4.8, 2002), (4.4, 2013), (4.0, 2016)]
TE, FLOOR, B, LAM, MMAX = 2023.0, 5.8, 0.92, 5.43, 9.5


def n_true(m, b=B, lam=LAM, floor=FLOOR, mmax=MMAX):
    """True N(>=m) per year of a GR truncated at mmax with N(>=floor) = lam."""
    m = np.asarray(m, float)
    n = lam * (10 ** (-b * (m - floor)) - 10 ** (-b * (mmax - floor))) / (1 - 10 ** (-b * (mmax - floor)))
    return np.where(m > mmax, 0.0, np.clip(n, 0, None))


def m0(m):
    return 10 ** (1.5 * np.asarray(m, float) + 9.05)


def moment_true(b=B, lam=LAM, floor=FLOOR, mmax=MMAX, lo=5.0):
    """Moment rate of the true GR above lo by numerical integration (fine steps)."""
    g = np.linspace(lo, mmax, 20001)
    n = n_true(g, b, lam, floor, mmax)
    return float(((n[:-1] - n[1:]) * m0((g[:-1] + g[1:]) / 2)).sum())


def simulate(rng, round_to=None, steps=STEPS, te=TE, b=B, lam=LAM, floor=FLOOR, mmax=MMAX, lo=5.5):
    """
    Complete events of one catalog. With round_to the completeness steps hold for the rounded
    value (a recorded 6.0 is complete from the year of the step, true magnitudes from 5.95).
    """
    h = round_to / 2 if round_to else 0.0
    s = sorted(steps)
    out = []
    for i, (mc, y0) in enumerate(s):
        a = max(mc - h, lo)
        z = min((s[i + 1][0] if i + 1 < len(s) else mmax + h) - h, mmax)
        if z <= a:
            continue
        k = (n_true(a, b, lam, floor, mmax) - n_true(z, b, lam, floor, mmax)) * (te - y0)
        n = rng.poisson(k)
        u = rng.random(n)
        fa, fz = 10 ** (-b * (a - floor)), 10 ** (-b * (z - floor))
        out.append(-np.log10(fa - u * (fa - fz)) / b + floor)
    m = np.concatenate(out)
    return np.round(m / round_to) * round_to if round_to else m

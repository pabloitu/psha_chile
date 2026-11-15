"""FaultQuake (Tavakolizadeh et al. 2024, Computers & Geosciences 191:105659), the tool MASCSN26 used for its fault
sources: Mmax, moment budget and truncated GR rates, ported from github.com/GeoSignalAnalysis/FaultQuake (main,
src/SeismicActivityRate.py `momentbudget`, `sactivityrate`; src/FaultQuake_functions.py `kin2coeff`, `coeff2mag`,
`conflate_pdfs`, `TruncatedGR`; MIT licence). Only the Truncated Gutenberg-Richter branch, without observed magnitude.

FaultQuake conventions kept as they are: M0 = 10^(1.5 M + 9.1); the moment rate is M0(Mmax) / Tmean with Tmean rounded
to whole years; the rate points Mmin, Mmin + bin, ..., Mmax are the lower edges of the bins and the moment is balanced
at those points; Mmax is the mode of the conflated magnitude pdfs rounded to 0.1.
"""
import math

import numpy as np
from scipy.stats import norm

D, C = 9.1, 1.5
WC94 = {"N": [4.34, 1.54, 0.31, 3.93, 1.02, 0.25], "R": [4.49, 1.49, 0.26, 4.33, 0.90, 0.25],
        "S": [4.33, 1.49, 0.24, 3.98, 1.02, 0.23], "A": [4.38, 1.49, 0.26, 4.07, 0.98, 0.24]}
LE10 = {"D": [2.5, 7.53, 8.51, 1.5, 5.69, 6.6], "S": [1.5, 12.01, 12.88, 1.5, 5.69, 6.47],
        "SCR": [2.5, 7.87, 8.28, 1.5, 6.22, 6.52]}
# aspect-ratio rows (Pace and Peruzza 2002) and the row each scaling relation takes in coeff2mag
AR = [[3.0939, 1.2501, 0.25], [-4.4543, 2.1992, 0.25], [-7.096, 2.9807, 0.25], [-2.3725, 1.9354, 0.25]]
AR_ROW = {"WC94-N": 0, "WC94-R": 1, "WC94-S": 2, "WC94-A": 3, "LE10-D": 3, "LE10-S": 2, "LE10-SCR": 3}


def m0(m):
    return 10 ** (C * np.asarray(m, float) + D)


def lar(scr, W):
    """Aspect-ratio length (km) for a down-dip width W (km)."""
    a = AR[AR_ROW[scr]]
    return a[0] + a[1] * W


def mmax(scr, L, dip, T, mu=3e10, sd=3e-5, sig=0.3):
    """
    Mmax of FaultQuake (`momentbudget`, no observed magnitude): MMO (strain drop), MAR (aspect-ratio length, only if
    shorter than the fault), and the length and area relation of `scr`, each a normal pdf scaled to peak 1, conflated;
    the mode rounded to 0.1. L and T in km, dip in degrees.
    """
    Lm, W = L * 1e3, T * 1e3 / math.sin(math.radians(dip))
    a = AR[AR_ROW[scr]]
    LAR = (a[0] + a[1] * W / 1e3) * 1e3
    MAR = (2 / 3) * (math.log10(sd * mu * LAR ** 2 * W) - 9.05)
    if scr.startswith("WC94"):
        wc = WC94[scr[-1]]
        MRLD, MRA = wc[0] + wc[1] * math.log10(L), wc[3] + wc[4] * math.log10(L * W / 1e3)
        dRLD, dRA = wc[2], wc[5]
    else:
        le = LE10[scr.split("-")[1]]
        lo = (2 / 3) * math.log10(10 ** (le[1] + le[0] * math.log10(Lm))) - 6.07
        hi = (2 / 3) * math.log10(10 ** (le[2] + le[0] * math.log10(Lm))) - 6.07
        if scr == "LE10-SCR":
            alo = (2 / 3) * math.log10(10 ** (le[4] + le[3] * math.log10(Lm * W)) - 6.07)
            ahi = (2 / 3) * math.log10(10 ** (le[5] + le[3] * math.log10(Lm * W)) - 6.07)
        else:
            alo = (2 / 3) * math.log10(10 ** (le[4] + le[3] * math.log10(Lm * W))) - 6.07
            ahi = (2 / 3) * math.log10(10 ** (le[5] + le[3] * math.log10(Lm * W))) - 6.07
        MRLD, MRA, dRLD, dRA = (lo + hi) / 2, (alo + ahi) / 2, (hi - lo) / 2, (ahi - alo) / 2
    MMO = (1 / C) * (np.log10(sd * mu * Lm ** 2 * W) - D)
    M = np.round(np.array([MMO, MAR, MRLD, MRA]) * 100) / 100
    dM = np.round(np.array([sig, a[2], dRLD, dRA]) * 100) / 100
    x = np.arange(np.floor(np.min(M - dM)), np.ceil(np.max(M + dM)) + 0.01, 0.01)
    p = np.array([norm.pdf(x, m, s) for m, s in zip(M, dM)])
    p /= p.max(axis=1)[:, None]
    if LAR >= Lm:
        p = np.delete(p, 1, axis=0)
    c = np.ones(x.shape) / (x[-1] - x[0])
    for q in p:
        c = c * q / np.trapezoid(q, x)
    return round(x[np.argmax(c)] * 10) / 10


def tmean(mx, V, L, dip, T, scr, mu=3e10, scc=1.0):
    """Mean recurrence of Mmax, whole years (V slip rate mm/yr; L, T km)."""
    W = T * 1e3 / math.sin(math.radians(dip))
    Le = min(L, lar(scr, W / 1e3)) * 1e3
    t = np.round(m0(mx) / (mu * V * 1e-3 * Le * W))
    return float(np.round(t / scc))


def rates(mx, tm, b, mmin=6.0, dm=0.1):
    """
    Truncated GR rates of FaultQuake (`TruncatedGR`) on the points mmin..mx, moment-balanced to M0(mx) / tm at the
    points.

    Returns
    -------
    (array, array)
        Points (lower bin edges in FaultQuake; written by MASCSN as `minMag` of an incremental MFD) and rates.
    """
    m = np.round(np.arange(mmin, mx + dm / 2, dm), 6)
    M, Mt, Mx = m0(m), m0(mmin), m0(mx + dm)
    B = (2 / 3) * b
    S = ((Mt / M) ** B - (Mt / Mx) ** B) / (1 - (Mt / Mx) ** B)
    inc = np.r_[S[:-1] - S[1:], S[-1]]
    return m, inc * (m0(mx) / tm) / (inc * M).sum()

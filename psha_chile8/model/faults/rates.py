"""Fault MFDs with the rules of DECISIONS (Crustal and faults), for the comparison of databases A and B (D16b).

Moment rate psi mu L W slip, mu 30 GPa, W = depth / sin(dip) with the fault from the surface to 10 or 20 km; Mmax
Leonard (2014) from the fault area (system area for a joined system), on the 0.1 bin grid of fits/gr.py (bin centres
6.0, 6.1, ...; the last bin is the one that holds the Leonard value, at least the first); six MFD shapes, each scaled
so that the moment at the bin centres is the target; b of the crustal class. The weighted mean over the fault tree
uses psi 0.6 / 0.8 / 1.0 (0.25 / 0.5 / 0.25), depth 10 / 20 km (0.5 / 0.5, weights not in DECISIONS) and the shapes
1/6 each. Shapes ported from psha_chile7/crustal/s03_faults.py (read only).
"""
import math

import numpy as np

MU, C, DM, MMIN = 3.0e10, 9.05, 0.1, 6.0
PSI = {0.6: 0.25, 0.8: 0.5, 1.0: 0.25}
DEPTH = {10.0: 0.5, 20.0: 0.5}
SHAPES = ("al1", "al2", "al3", "yc", "tap", "hyb")
TAPER_PAD, HYB_R, HYB_SIG = 0.5, 0.5, 0.12


def m0(m):
    return 10 ** (1.5 * np.asarray(m, float) + C)


def leonard(area, rake):
    from openquake.hazardlib.scalerel.leonard2014 import Leonard2014_Interplate
    return Leonard2014_Interplate().get_median_mag(area, rake)


def on_grid(m):
    """Last bin centre: the bin of the 0.1 grid (centres 6.0, 6.1, ...) that holds m; at least MMIN."""
    return max(MMIN, round(MMIN + DM * math.floor((m - MMIN) / DM + 0.5 + 1e-9), 6))


def shape(kind, b, mmax):
    """
    Unscaled incremental rates of one MFD shape on the bin centres MMIN..mmax (cut at the edge mmax + DM / 2).

    al1, al2, al3: Anderson and Luco (1983) cumulative forms; yc: Youngs and Coppersmith (1985), box of 0.5 below the
    top edge (al2 where Mmax < MMIN + 0.6); tap: tapered GR with the corner at Mmax, extended by TAPER_PAD (al2 where
    Mmax < MMIN + 0.2); hyb: Gaussian characteristic (sigma HYB_SIG, centred 2 sigma below Mmax, cut at 2 sigma) with
    the moment share HYB_R over a truncated GR.

    Returns
    -------
    (array, array)
        Bin centres and rates.
    """
    if (kind == "yc" and mmax - MMIN < 0.6 - 1e-9) or (kind == "tap" and mmax - MMIN < 0.2 - 1e-9):
        kind = "al2"
    bb = b * math.log(10.0)
    if kind == "tap":
        top = mmax + DM / 2 + TAPER_PAD
        e = np.round(np.arange(MMIN - DM / 2, top + DM / 2, DM), 6)
        cum = 10 ** (-b * (e - e[0])) * np.exp((m0(e[0]) - m0(e)) / m0(mmax))
        cum[-1] = 0.0
        return e[:-1] + DM / 2, cum[:-1] - cum[1:]
    top = mmax + DM / 2
    e = np.round(np.arange(MMIN - DM / 2, top + DM / 2, DM), 6)
    c = e[:-1] + DM / 2
    d = np.clip(top - e, 0.0, None)
    if kind == "al1":
        cum = np.exp(bb * d)
    elif kind == "al2":
        cum = np.exp(bb * d) - 1.0
    elif kind == "al3":
        cum = np.exp(bb * d) - 1.0 - bb * d
    elif kind == "yc":
        bx = top - 0.5
        f = lambda m: np.exp(-bb * m)
        cum = (f(e) - f(bx)) / bb + 0.5 * f(bx - 1.0)
        k = e >= bx - 1e-9
        cum[k] = (top - e[k]) * f(bx - 1.0)
    elif kind == "hyb":
        mc = mmax - 2 * HYB_SIG
        wc = np.where(np.abs(c - mc) <= 2 * HYB_SIG + 1e-9, np.exp(-0.5 * ((c - mc) / HYB_SIG) ** 2), 0.0)
        wg = np.where(c < mc - 2 * HYB_SIG - 1e-9, 10 ** (-b * c), 0.0)
        r = HYB_R if wg.sum() > 0 else 1.0
        nu = r * wc / (wc * m0(c)).sum()
        if r < 1:
            nu = nu + (1 - r) * wg / (wg * m0(c)).sum()
        return c, nu
    else:
        raise ValueError(kind)
    cum[-1] = 0.0
    return c, np.maximum(cum[:-1] - cum[1:], 0.0)


def mfd(kind, b, mmax, mo):
    """Rates of a shape scaled to the moment rate mo (N m / yr) at the bin centres."""
    c, r = shape(kind, b, mmax)
    return c, r * mo / (r * m0(c)).sum()


def grid(c, r, n=40):
    """Rates on the fixed grid of centres MMIN + DM k, k < n."""
    out = np.zeros(n)
    k = np.rint((c - MMIN) / DM).astype(int)
    np.add.at(out, k[k < n], r[k < n])
    return out


def source(L, dip, rake, sr, b, n=40, fixed=0.0, Lsr=None):
    """
    Weighted-mean rates of one fault or joined system over the fault tree, on the grid MMIN + DM k.

    L, dip: length (km, summed over the segments of a system; it sets Mmax) and dip; sr slip rate (mm/yr) or, for a
    system, the length-weighted mean. The moment of each branch is psi (mu Lsr W sr + fixed): Lsr the length that
    carries sr (L by default), fixed a moment rate (N m / yr) taken as given in every depth branch, e.g. the MASCSN
    budget of the MASCSN traces. Returns (rates, Mmax at 10 km, Mmax at 20 km).
    """
    Lsr = L if Lsr is None else Lsr
    out, mm = np.zeros(n), []
    for z, wz in DEPTH.items():
        W = z / math.sin(math.radians(dip))
        mx = on_grid(leonard(L * W, rake))
        mm.append(mx)
        mo = sum(wp * p for p, wp in PSI.items()) * (MU * Lsr * 1e3 * W * 1e3 * sr * 1e-3 + fixed)
        for k in SHAPES:
            out += wz / len(SHAPES) * grid(*mfd(k, b, mx, mo), n)
    return out, mm[0], mm[1]


def published(mags, rates, scc=0.75, n=40):
    """MASCSN rates times the weighted mean SCC (1 / 0.75 / 0.5, weights 0.25 / 0.5 / 0.25: 0.75)."""
    return scc * grid(np.asarray(mags), np.asarray(rates), n)


def n_ge(r, M, n=40):
    c = MMIN + DM * np.arange(n)
    return float(r[c >= M - 1e-6].sum())


def moment(r, n=40):
    return float((r * m0(MMIN + DM * np.arange(n))).sum())

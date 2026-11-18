"""One Mw per earthquake (plan A5).

Every native magnitude of the frozen source tables is joined to its event through the A3 links. Measured Mw
(GCMT, W-phase and regional moment magnitudes) is put on one scale and is the reference. Every other agency and
scale is converted by a relation fitted on Chilean pairs: the native magnitude is regressed on the reference Mw,
the slope corrected for the reference error, and the relation inverted. From 1976 each event takes its measured
Mw, else Ruiz and Madariaga (2018), else the first converted scale of a fixed priority list (surface-wave scales
only for events not deeper than 60 km). Before 1976 a moment-based value goes before a converted one and the
Centennial catalogue before ISC-GEM inside each level: Ruiz and Madariaga, a Centennial Mw, an ISC-GEM direct Mw,
a Centennial Ms or mB converted, an ISC-GEM proxy Mw, Cabello. Method note in MAGNITUDES.md; checks in
magnitude_check.py.
"""
import hashlib
import json
import re
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from match import SRC, OUT, FROZEN, DATES, tsec, year

# settings
RUN = "2026-11-17c"
A3 = "2026-11-11"
LOC = "2026-11-17c"
SEED = 1
SRCS = ["gcmt", "isc", "csn", "comcat", "iscgem", "centennial", "cabello"]
CODA, CODA_AG, CODA_BEFORE = ["md", "mc", "c"], ["GUC", "CSN", "guc", "GUC;NEIC"], 1990
GC = "GCMT Mw"
WFAM = ["NEIC Mww", "GUC Mwr", "CSN web Mw", "NEIC Mwr", "GFZ Mw", "CSN Mww"]
# the CSN moment magnitude of the ISC Bulletin: not used to fit relations or the offsets of the others; as the Mw of
# an event it comes after every other measured moment magnitude
LAST = "GUC MW"
# relations are fitted on pairs whose reference Mw reaches FIT_MIN (the offsets use pairs from BINS[0] on)
FIT_MIN = 4.0
M_HI, M_CSN = 5.4, 5.0
# a regional Mw of the CSN further than REG_TOL from the median of the event's other moment magnitudes is not used
# when the event has REG_N of them or more; with fewer the pair goes to the review list and the order decides
REG, REG_OTHER, REG_TOL, REG_N = ["GUC Mwr", "CSN web Mw", "GUC MW"], [GC, "NEIC Mww", "NEIC Mwr", "NEIC Mwb", "GFZ Mw", "CSN Mww"], 0.3, 2
SY = {"G": 0.08, "W": 0.10}
BINS = np.round(np.arange(4.5, 6.51, 0.25), 2)
GBINS = [4.5, 4.75, 5.0, 5.25, 5.4]
NBIN, FLAT, DMAX = 30, 0.05, 0.5
N_ALL, N_LINE = 100, 30
MIN_SIDE, NFOLD, NBOOT = 20, 5, 200
KNOTS, KREF = np.round(np.arange(4.6, 6.61, 0.1), 1), 5.5
B_SAT, S_MAX, GROW = 0.3, 1.0, 0.1
ZCUT, PCUT, PERIOD_SPLIT = 50.0, 1990, ["ISC mb", "NEIC mb"]
AT = [4.5, 5.0, 5.5, 6.0]
ML, WEB_ML, WEB_MLV = "GUC ML", "CSN Ml", "CSN Mlv"
MB_FAMILY = ["ISC mb", "NEIC mb"]
NOT_BELOW, NOT_BELOW_MW = r"^(?:.* [Mm][Ss]\w*|MOS [Mm][Bb]|BJI mB)$", 5.0
# surface-wave scales (SW). 'depth': no magnitude limit, only events not deeper than SW_Z (Di Giacomo et al. 2015);
# 'own': NOT_BELOW_MW judged on the scale's own converted value (the brief); 'other': on the first other scale
SW, SW_Z = r".* [Mm][Ss]\w*$", 60.0
JUDGE = "depth"
# 'first': the first eligible scale of PRIORITY; 'mean': the weighted mean of the eligible scales (Lolli et al. 2014)
COMBINE, N_MEAN = "first", 300
# GCMT against the W family: 'step' one offset per bin below M_HI; 'ramp' a line in the GCMT value, down to where
# it reaches zero; 'ramp0' a line that is zero at M_HI; 'none'
LOWER, RAMP = "ramp0", (4.75, 6.0)
# converted scales: the global references (ISC, NEIC: mb and surface-wave types) and the national networks of
# Chile and Argentina (CSN / GUC ML with the web Ml and Mlv, INPRES / SJA ML); every other agency is left out
PROXY = r"^(?:(?:ISC|NEIC) (?:mb|MS|MSZ|Ms_20)|GUC ML|CSN Mlv?|SJA ML)$"
# before PRE76: a moment-based value before a converted one, the Centennial before ISC-GEM inside each level
# (S. Ruiz, 13 Nov). Centennial: an Mw, else its preferred magnitude converted; an entry with mb only leaves the
# event to the next source. ISC-GEM: direct (flag d of its table), else proxy
PRE76, OLD = 1976, ["Centennial Mw", "ISC-GEM direct", "Centennial converted", "ISC-GEM proxy"]
CENT_TY = {"Mw": 0, "mB": 1, "Ms": 2, "UK": 3}
CAB_BEFORE = 1904
# corrections of the large-event review (plan A6): rows with status 'accepted' are applied as the last step
A6 = Path(__file__).resolve().parent / "overrides_A6.csv"
A6_MW = {"mw": "mw"}
A6_ALSO = {"mw": {"mw_kind": "a6"}, "depth": {"depth_kind": "measured", "depth_src": "a6"}, "lon": {"loc_src": "a6"},
           "lat": {"loc_src": "a6"},
           "strike1": {"mech_src": "a6"}}
SIG_RM, SIG_GEM, SIG_CENT, SIG_MB, SIG_CAB = 0.2, 0.2, 0.25, 0.3, 0.5
BIG, BIG_DIFF = 7.0, 0.3
PROXY_REVIEW = 6.5
# priority of the converted scales, by the σ of their relations (written by the run of RUN; an empty list
# takes the order of the current fit; a different order is reported)
PRIORITY = ["NEIC Ms_20", "ISC MS", "NEIC MS", "NEIC MSZ", "GUC ML", "CSN Ml", "CSN Mlv", "ISC mb", "NEIC mb", "SJA ML"]

COMCAT = {("us", "mww"): "NEIC Mww", ("us", "mwr"): "NEIC Mwr", ("us", "mwb"): "NEIC Mwb", ("us", "mb"): "NEIC mb",
          ("us", "ms"): "NEIC MS", ("guc", "ml"): "GUC ML", ("guc", "md"): "GUC MD", ("guc", "mwr"): "GUC Mwr",
          ("guc", "m"): "GUC M", ("san", "md"): "SAN md", ("hrv", "mwc"): GC, ("hrv", "mw"): GC, ("gcmt", "mwc"): GC,
          ("iscgem", "mw"): "ISC-GEM Mw", ("iscgemsup", "mw"): "ISC-GEM Mw"}
ALIAS = {("isc", "GCMT", "MW"): GC, ("gcmt", "GCMT", "Mw"): GC, ("isc", "GUC", "Mww"): "CSN Mww",
         ("csn", "CSN", "Mww"): "CSN Mww", ("csn", "CSN", "Mw"): "CSN web Mw"}
MS_DG15 = lambda x: np.exp(-0.222 + 0.233 * x) + 2.863
# Abe (1982): log M0 = 2.4 mB + 10.0 (deep and intermediate, eq. 5) or + 9.6 (shallow, eq. 7), M0 in dyn cm
MB_A82 = lambda x, deep: (2.4 * x + np.where(deep, 10.0, 9.6) - 16.1) / 1.5


# inputs
def scale(src, ag, ty):
    if (src, ag, ty) in ALIAS:
        return ALIAS[(src, ag, ty)]
    if src == "comcat":
        return COMCAT.get((ag, ty), f"ComCat {ag} {ty}")
    if src == "iscgem":
        return "ISC-GEM Mw"
    if src == "centennial":
        return f"Cent {ag} {ty}"
    if src == "cabello":
        return "Cabello final" if ag == "cabello" else f"Cabello {ty}"
    return f"{ag} {ty}"


def load(d=SRC, out=OUT):
    """
    Events of the A3 run and every native magnitude on them.

    Returns
    -------
    e : events (event_id, t, yr, lat, lon, z)
    M : one row per event and scale (the first source in SRCS that gives it; ISC-GEM from its own table, which
        has the direct / proxy flag, before its copy in ComCat): event_id, scale, mag, err, src, src_id, agency,
        mag_type, note
    rm : Ruiz and Madariaga (2018) values on the events they name: event_id, src_id, mag, sig, flags
    """
    e = pd.read_csv(Path(out) / f"events_{A3}.csv", usecols=["event_id", "time", "lon", "lat", "depth"], low_memory=False)
    e["t"] = tsec(e.time)
    e["yr"] = year(e.t)
    e = e.rename(columns={"depth": "z"})
    f = Path(out) / f"locations_{LOC}.csv"
    if f.exists():
        z = e.event_id.map(pd.read_csv(f, usecols=["event_id", "depth"]).set_index("event_id").depth)
        e["z"] = z.fillna(e.z)
    L = pd.read_csv(Path(out) / f"links_{A3}.csv", usecols=["event_id", "src", "src_id"], dtype=str).drop_duplicates(["src", "src_id"])
    yr = e.set_index("event_id").yr
    rows = []
    for s in SRCS:
        m = pd.read_csv(Path(d) / f"{s}_{DATES.get(s, FROZEN)}_mags.csv", dtype=str)
        m = m.merge(L[L.src == s], on=["src", "src_id"])
        m["mag"] = pd.to_numeric(m.mag, errors="coerce")
        m = m[m.mag.notna()]
        if s == "gcmt":
            m = m[m.agency == "GCMT"]
        key = m[["agency", "mag_type"]].drop_duplicates()
        key["scale"] = [scale(s, a, t) for a, t in zip(key.agency, key.mag_type)]
        m = m.merge(key, on=["agency", "mag_type"])
        coda = m.agency.isin(CODA_AG) & m.mag_type.str.lower().isin(CODA) & (m.event_id.map(yr) < CODA_BEFORE).to_numpy()
        rows.append(m[~coda])
    M = pd.concat(rows, ignore_index=True)
    M["o"] = M.src.map({s: i for i, s in enumerate(SRCS)})
    M.loc[(M.src == "iscgem") & (M.scale == "ISC-GEM Mw"), "o"] = -1
    M["p"] = M.note.eq("preferred")
    M = M.sort_values(["o", "p"], ascending=[True, False], kind="stable").drop_duplicates(["event_id", "scale"])
    M["err"] = pd.to_numeric(M.mag_err, errors="coerce")
    M = M[["event_id", "scale", "mag", "err", "src", "src_id", "agency", "mag_type", "note"]].reset_index(drop=True)
    return e, M, rm18(d, L)


def rm18(d, L):
    """Ruiz and Madariaga Mw from the frozen table: a number as given; a range by its middle, '>' and '<' by the
    bound, '~' by the value, '(Ms)' as Mw; all but the plain numbers flagged."""
    m = pd.read_csv(Path(d) / f"rm2018_{FROZEN}_mags.csv", dtype=str).merge(L[L.src == "rm2018"], on=["src", "src_id"])
    rows = []
    for r in m.itertuples():
        v = [float(q) for q in re.findall(r"\d+\.?\d*", str(r.note).split("(")[0])]
        if not v:
            continue
        fl = [f for f, k in (("rm18_range", len(v) > 1), ("rm18_bound", r.note[0] in "<>"), ("rm18_approx", r.note[0] == "~"),
                             ("rm18_ms", "(Ms)" in r.note)) if k]
        sig = max(SIG_RM, (max(v) - min(v)) / 2) if len(v) > 1 else SIG_RM + 0.1 * bool(fl)
        rows.append({"event_id": r.event_id, "src_id": r.src_id, "mag": float(np.mean(v)), "sig": sig, "note": r.note,
                     "flags": ";".join(fl)})
    return pd.DataFrame(rows)


# reference Mw
def first(cands):
    """First finite value along a list of (name, values); returns values and names."""
    v, nm = np.full(len(cands[0][1]), np.nan), np.full(len(cands[0][1]), None, object)
    for c, x in cands:
        k = np.isnan(v) & np.isfinite(x)
        v[k], nm[k] = x[k], c
    return v, nm


def offsets(W):
    """
    Offsets of the reference members to NEIC Mww on shared events.

    Per 0.25 bin of the pair mean from 4.5 to 6.5: n, mean and median of member − NEIC Mww (the mean is used:
    the values are rounded to 0.1, so medians jump). A member is flat when no bin with NBIN pairs departs from
    its overall mean by more than FLAT and two standard errors; it then gets one constant, else its bin means.

    Returns the table and, per member, the shift (to add) per bin of BINS.
    """
    rows, off = [], {WFAM[0]: np.zeros(len(BINS) - 1)}
    for c in [GC] + WFAM[1:] + [LAST]:
        x = W[[WFAM[0], c]].dropna()
        d, mm = (x[c] - x[WFAM[0]]).to_numpy(), x.mean(axis=1).to_numpy()
        k = (mm >= BINS[0]) & (mm < BINS[-1])
        d = np.clip(d, -DMAX, DMAX)
        med = float(np.mean(d[k])) if k.sum() >= NBIN else 0.0
        bm, far = [], False
        for lo, hi in zip(BINS[:-1], BINS[1:]):
            kb = (mm >= lo) & (mm < hi)
            v, se = (float(np.mean(d[kb])), float(np.std(d[kb]) / np.sqrt(kb.sum()))) if kb.sum() >= NBIN else (np.nan, np.nan)
            far |= abs(v - med) > max(FLAT, 2 * se)
            bm.append(v)
            rows.append({"member": c, "against": WFAM[0], "lo": lo, "hi": hi, "n": int(kb.sum()), "mean": v, "se": se,
                         "median": float(np.median(d[kb])) if kb.any() else np.nan})
        bm = np.array(bm)
        off[c] = -np.round(np.where(np.isnan(bm), med, bm), 2) if far else np.full(len(bm), -round(med, 2))
        rows.append({"member": c, "against": WFAM[0], "lo": BINS[0], "hi": BINS[-1], "n": int(k.sum()), "mean": med,
                     "median": float(np.median(d[k])) if k.any() else np.nan, "sd": float(np.std(d[k])) if k.any() else np.nan,
                     "flat": not far, "shift": np.nan if far or c == GC else -round(med, 2)})
    return pd.DataFrame(rows), off


def outliers(M):
    """CSN regional Mw values (REG) further than REG_TOL from the median of the event's other moment
    magnitudes (REG_OTHER): event_id, scale, mag, others, n (how many others), dropped (n >= REG_N)."""
    W = M[M.scale.isin(REG + REG_OTHER)].pivot(index="event_id", columns="scale", values="mag").reindex(columns=REG + REG_OTHER)
    med = W[REG_OTHER].median(axis=1)
    x = W[REG].stack().rename("mag").reset_index()
    x["others"], x["n"] = x.event_id.map(med), x.event_id.map(W[REG_OTHER].notna().sum(axis=1))
    x["dropped"] = x.n >= REG_N
    return x[(x.mag - x.others).abs() > REG_TOL + 1e-9].reset_index(drop=True)


def reference(M, gcmt_first=False, lower=LOWER):
    """
    Reference Mw per event, on the NEIC Mww scale. The CSN regional values of outliers() are left out, after
    the offsets are measured.

    GCMT at M_HI and above, then the W family in the order of WFAM (each member shifted to NEIC Mww). Below M_HI
    the W family, then GCMT lowered by its measured offset to the W family (lower: a line in the GCMT value that
    is zero at M_HI, a free line, one step per bin, or nothing), with CSN Mww after GCMT below M_CSN. Above or below is judged on the GCMT value, else on the W value.
    gcmt_first puts the unshifted GCMT first at every size. LAST (shifted by its own offset) is taken only where
    nothing else exists, and those events are marked fit = False.

    Returns
    -------
    R : per event y, sig, scale (the member taken), flag, fit (usable as a pair for the relations)
    tab : offsets table
    W : member values per event
    """
    W = M[M.scale.isin([GC] + WFAM + [LAST])].pivot(index="event_id", columns="scale", values="mag").reindex(columns=[GC] + WFAM + [LAST])
    tab, off = offsets(W)
    for r in outliers(M).query("dropped").itertuples():
        W.loc[r.event_id, r.scale] = np.nan
    g = W[GC].to_numpy()
    sh = {}
    for c in WFAM + [LAST]:
        v = W[c].to_numpy()
        sh[c] = v + off[c][np.clip(np.digitize(np.nan_to_num(v, nan=5.0), BINS) - 1, 0, len(BINS) - 2)]
    main, cw = first([(c, sh[c]) for c in WFAM[:-1]]), sh[WFAM[-1]]
    comp = np.where(np.isfinite(main[0]), main[0], cw)
    low, n = [], []
    for lo, hi in zip([-9] + GBINS[1:-1], GBINS[1:]):
        k = (g >= lo) & (g < hi) & np.isfinite(comp)
        n.append(int(k.sum()))
        low.append(float(np.mean(np.clip(g - comp, -DMAX, DMAX)[k])) if k.sum() >= NBIN else np.nan)
    low = pd.Series(low).bfill().ffill().fillna(0.0).round(2).to_numpy()
    tab = pd.concat([tab, pd.DataFrame({"member": GC, "against": "W family (by GCMT value)", "lo": GBINS[:-1], "hi": GBINS[1:],
                                        "n": n, "mean": low, "shift": -low})], ignore_index=True)
    gl = g - low[np.clip(np.digitize(np.nan_to_num(g, nan=5.0), GBINS[1:-1]), 0, len(low) - 1)]
    gh = g
    if lower in ("ramp", "ramp0"):
        k = np.isfinite(g) & np.isfinite(comp) & (g >= RAMP[0]) & (g < (RAMP[1] if lower == "ramp" else M_HI))
        d = np.clip(g - comp, -DMAX, DMAX)[k]
        if k.sum() < NBIN:
            a, b = 0.0, 0.0
        elif lower == "ramp":
            b, a = np.polyfit(g[k], d, 1)
        else:
            b = -np.sum(d * (M_HI - g[k])) / np.sum((M_HI - g[k]) ** 2)
            a = -b * M_HI
        gl = g - np.clip(a + b * np.clip(g, RAMP[0], None), 0, None)
        gh = gl
        tab = pd.concat([tab, pd.DataFrame([{"member": GC, "against": "W family (line in the GCMT value)", "lo": RAMP[0],
                                             "hi": -a / b if b else np.nan, "n": int(k.sum()), "mean": a + b * RAMP[0], "shift": b}])], ignore_index=True)
    elif lower == "none":
        gl = g
    judge = np.where(np.isfinite(g), g, comp)
    fam = [(c, sh[c]) for c in WFAM[:-1]]
    if gcmt_first:
        y, nm = first([(GC, g)] + fam + [(WFAM[-1], cw)])
    else:
        hi, _ = first([(GC, gh)] + fam + [(WFAM[-1], cw)])
        mid = first(fam + [(WFAM[-1], cw), (GC + " lowered", gl)])
        lo = first(fam + [(GC + " lowered", gl), (WFAM[-1], cw)])
        y = np.where(judge >= M_HI, hi, np.where(judge >= M_CSN, mid[0], lo[0]))
        nm = np.where(judge >= M_HI, first([(GC, g)] + fam + [(WFAM[-1], cw)])[1], np.where(judge >= M_CSN, mid[1], lo[1]))
    k = np.isnan(y) & np.isfinite(sh[LAST])
    y, nm = np.where(k, sh[LAST], y), np.where(k, LAST, nm)
    R = pd.DataFrame({"y": y, "scale": nm, "fit": ~k}, index=W.index)
    R["flag"] = np.where((R.scale == GC + " lowered") | ((R.scale == GC).to_numpy() & (g - y > 0.005)), "gcmt_lowered", "")
    R["scale"] = R.scale.replace(GC + " lowered", GC)
    R["sig"] = np.where(R.scale == GC, SY["G"], SY["W"])
    return R[np.isfinite(R.y)], tab, W


def ref_sigma(W):
    """Error of GCMT, NEIC Mww and GUC Mwr from the variances of their pairwise differences on events that
    have all three (three-cornered hat)."""
    x = W[[GC, "NEIC Mww", "GUC Mwr"]].dropna()
    v = {(a, b): np.var(x[a] - x[b]) for a in x for b in x if a < b}
    g = lambda a, b: v.get((a, b), v.get((b, a)))
    out = {"n": len(x)}
    for a, b, c in ((0, 1, 2), (1, 0, 2), (2, 0, 1)):
        a, b, c = x.columns[a], x.columns[b], x.columns[c]
        out[a] = float(np.sqrt(max((g(a, b) + g(a, c) - g(b, c)) / 2, 0)))
    return out


# relations: native = a + b1 (Mw - k) below the knot k, b2 above; a straight line has b1 = b2
def pl(p, y):
    a, b1, b2, k = p
    return a + np.where(y < k, b1, b2) * (y - k)


def fit_inv(y, x, sy, form="linear"):
    """
    Native magnitude on reference Mw by least squares, slopes divided by λ = 1 − sy² / var(y) for the error of y.

    Selection of the pairs on y (an incomplete reference) does not bias this direction. A hinge is kept only
    where the slope drops above the knot; otherwise the straight line is returned.

    Returns p = (a, b1, b2, k), the residual sd s of the native value, sy and n.
    """
    lam = max(1 - sy ** 2 / max(np.var(y), 1e-6), 0.5)
    c = np.linalg.lstsq(np.c_[np.ones_like(y), y - KREF], x, rcond=None)[0]
    best = (np.inf, KREF, c[1], c[1])
    if form == "hinge":
        best = (float(np.sum((x - c[0] - c[1] * (y - KREF)) ** 2)), *best[1:])
        for k in KNOTS:
            if (y < k).sum() < MIN_SIDE or (y >= k).sum() < MIN_SIDE:
                continue
            A = np.c_[np.ones_like(y), np.minimum(y - k, 0), np.maximum(y - k, 0)]
            c = np.linalg.lstsq(A, x, rcond=None)[0]
            sse = float(np.sum((x - A @ c) ** 2))
            if sse < best[0] and 0 < c[2] < c[1]:
                best = (sse, k, c[1], c[2])
    _, k, b1, b2 = best
    b1, b2 = b1 / lam, b2 / lam
    a = float(np.mean(x - np.where(y < k, b1, b2) * (y - k)))
    p = (a, float(b1), float(b2), float(k))
    return {"p": p, "s": float(np.std(x - pl(p, y))), "sy": float(sy), "n": len(y)}


def fit_fwd(x, y, sx, sy):
    """Mw on native, straight line, chi-square (Deming) regression with error ratio η = sy² / sx²; stored in
    the same form as fit_inv, with the residual sd of Mw as its σ."""
    eta = sy ** 2 / sx ** 2
    sxx, syy, sxy = np.var(x), np.var(y), np.cov(x, y, bias=True)[0, 1]
    b = (syy - eta * sxx + np.sqrt((syy - eta * sxx) ** 2 + 4 * eta * sxy ** 2)) / (2 * sxy)
    a = y.mean() - b * x.mean()
    return {"p": ((KREF - a) / b, 1 / b, 1 / b, KREF), "s": float(np.std(x - (KREF - a) / b - (y - KREF) / b)), "sy": float(sy),
            "n": len(y), "sig": float(np.std(y - a - b * x))}


def conv(f, x):
    """Mw from native x by inverting the relation. σ is the scatter of the native value over the local slope,
    with the part of the residual that comes from the reference error taken out, and never below that error."""
    a, b1, b2, k = f["p"]
    b = np.where(x < a, b1, max(b2, B_SAT))
    s = np.maximum(np.sqrt(np.maximum(f["s"] ** 2 - (b * f["sy"]) ** 2, 0)) / b, f["sy"])
    return k + (x - a) / b, np.minimum(np.full(len(x), f["sig"]) if "sig" in f else s, S_MAX)


def groups(split, z, yr):
    if split == "depth":
        return np.where(np.isfinite(z) & (z > ZCUT), "deep", "shallow")
    if split == "period":
        return np.where(yr < PCUT, f"before {PCUT}", f"{PCUT} on")
    return np.full(len(z), "all")


def cv(x, y, yr, z, sy, form, split):
    """Squared residual of the native value on the held-out time block, per pair; None if a group is too small."""
    o = np.argsort(yr, kind="stable")
    fo = np.empty(len(yr), int)
    fo[o] = np.arange(len(yr)) * NFOLD // len(yr)
    g = groups(split, z, yr)
    out = np.full(len(x), np.nan)
    for i in range(NFOLD):
        for q in np.unique(g):
            a, b = (fo != i) & (g == q), (fo == i) & (g == q)
            if a.sum() < N_LINE:
                return None
            out[b] = (x[b] - pl(fit_inv(y[a], x[a], sy, form)["p"], y[b])) ** 2
    return out


def candidates(sc, n):
    c = [("linear", "none")]
    if n >= N_ALL:
        c += [("hinge", "none"), ("linear", "depth")] + [("linear", "period")] * (sc in PERIOD_SPLIT) + \
             [("hinge", "depth")] + [("hinge", "period")] * (sc in PERIOD_SPLIT)
    return c


def fit_scale(sc, x, y, yr, z, sy, forms=("linear", "hinge"), method="inv", boot=NBOOT):
    """
    Relation of one scale: the simplest candidate whose cross-validation loss in time blocks is within one
    standard error of the best one (paired differences), fitted on all pairs, with bootstrap intervals of Mw at
    the native values AT. method 'fwd' gives the forward chi-square line instead (no choice).
    """
    cand = [c for c in candidates(sc, len(x)) if c[0] in forms] if method == "inv" else [("linear", "none")]
    loss = {c: v for c in cand if len(cand) > 1 and (v := cv(x, y, yr, z, sy, *c)) is not None}
    sel = cand[0]
    if loss:
        mean = {c: float(np.mean(v)) for c, v in loss.items()}
        ref = loss[min(mean, key=mean.get)]
        sel = next(c for c in cand if c in loss and np.mean(loss[c] - ref) <= np.std(loss[c] - ref) / np.sqrt(len(ref)))
    form, split = sel
    g = groups(split, z, yr)
    rng = np.random.default_rng(SEED)
    parts = {}
    for q in np.unique(g):
        k = g == q
        if method == "fwd":
            f0 = fit_inv(y[k], x[k], sy)
            f = fit_fwd(x[k], y[k], np.sqrt(max(f0["s"] ** 2 - (f0["p"][1] * sy) ** 2, 0.05 ** 2)), sy)
        else:
            f = fit_inv(y[k], x[k], sy, form)
        f.update(xmin=float(np.percentile(x[k], 1)), xmax=float(np.percentile(x[k], 99)), ymin=float(y[k].min()),
                 ymax=float(y[k].max()))
        f["sigma"] = float(conv(f, np.array([f["p"][0] - 0.5]))[1][0])
        if boot and method == "inv":
            i = np.flatnonzero(k)
            b = np.array([conv(fit_inv(y[j], x[j], sy, form), np.array(AT))[0]
                          for j in (rng.choice(i, len(i)) for _ in range(boot))])
            f["ci"] = np.percentile(b, [2.5, 97.5], axis=0).T.round(3).tolist()
        parts[q] = f
    n = sum(f["n"] for f in parts.values())
    return {"scale": sc, "form": form, "split": split, "parts": parts, "n": n, "method": method,
            "sigma": float(np.sqrt(sum(f["n"] * f["sigma"] ** 2 for f in parts.values()) / n)),
            "cv": {f"{a} | {b}": float(np.mean(v)) for (a, b), v in loss.items()}}


def relations(M, R, e, sy=None, quiet=False, floor=FIT_MIN, **kw):
    """
    Relations of the scales of PROXY with at least N_LINE pairs against the reference (kw to fit_scale).
    sy overrides the reference error (default: the rms of the reference σ of the pairs). Pairs whose reference is
    LAST, or below floor, are left out.

    CSN web Ml takes the GUC ML relation. CSN web Mlv gets its own with N_ALL pairs; otherwise the ML relation
    after subtracting its median residual against it (flagged).
    """
    a = e.set_index("event_id")
    R = R[R.fit] if "fit" in R else R
    P = M[M.scale.str.contains(PROXY)].join(R[["y", "sig"]][R.y >= (-9 if floor is None else floor)], on="event_id", how="inner")
    P = P.join(a[["yr", "z"]], on="event_id")
    P = P[P.yr.notna()]
    F = {}
    for sc, p in P.groupby("scale"):
        if len(p) < N_LINE or sc == WEB_ML or (sc == WEB_MLV and len(p) < N_ALL):
            continue
        s = float(np.sqrt(np.mean(p.sig ** 2))) if sy is None else sy
        F[sc] = fit_scale(sc, p.mag.to_numpy(), p.y.to_numpy(), p.yr.to_numpy(), p.z.to_numpy(), s, **kw)
        if not quiet:
            print(f"{sc:16s} n {len(p):6d}  {F[sc]['form']:6s} {F[sc]['split']:6s} sigma {F[sc]['sigma']:.3f}", flush=True)
    if ML in F:
        F[WEB_ML] = {**F[ML], "scale": WEB_ML, "via": ML}
        p = P[P.scale == WEB_MLV]
        if WEB_MLV not in F:
            F[WEB_MLV] = {**F[ML], "scale": WEB_MLV, "via": ML}
        if "via" in F[WEB_MLV] and len(p) >= N_LINE:
            g = groups(F[ML]["split"], p.z.to_numpy(), p.yr.to_numpy())
            d = np.concatenate([p.mag[g == q] - pl(f["p"], p.y[g == q].to_numpy()) for q, f in F[ML]["parts"].items()])
            F[WEB_MLV] = {**F[ML], "scale": WEB_MLV, "via": ML, "shift": round(float(np.median(d)), 2), "n_shift": len(d)}
    return F


def rel_table(F):
    rows = []
    for sc, r in F.items():
        for g, f in r["parts"].items():
            ag, _, ty = sc.partition(" ")
            row = {"relation_id": sc if g == "all" else f"{sc} | {g}", "agency": ag, "type": ty, "via": r.get("via", ""),
                   "shift": r.get("shift", 0.0), "n_shift": r.get("n_shift"), "split": r["split"], "group": g, "form": r["form"], "a": f["p"][0],
                   "b1": f["p"][1], "b2": f["p"][2], "knot": f["p"][3], "native_min": f["xmin"], "native_max": f["xmax"],
                   "mw_min": f["ymin"], "mw_max": f["ymax"], "n": f["n"], "sd_native": f["s"], "sy": f["sy"], "sigma": f["sigma"]}
            for i, v in enumerate(AT):
                row[f"mw_at_{v}"] = float(conv(f, np.array([v]))[0][0])
                if "ci" in f:
                    row[f"lo_{v}"], row[f"hi_{v}"] = f["ci"][i]
            row["cv_chosen"] = r["cv"].get(f"{r['form']} | {r['split']}")
            row.update({f"cv {k}": v for k, v in r["cv"].items()})
            rows.append(row)
    return pd.DataFrame(rows).round(4)


def priority(F):
    """Scales ordered by the σ of their relation; ISC mb and NEIC mb are one family at the place of the better
    of the two, ISC first; a scale that borrows a relation follows its lender."""
    s = {sc: r["sigma"] for sc, r in F.items() if "via" not in r}
    fam = [sc for sc in MB_FAMILY if sc in s]
    for sc in fam:
        s[sc] = min(s[q] for q in fam)
    out = sorted(s, key=lambda sc: (s[sc], MB_FAMILY.index(sc) if sc in fam else 0, sc))
    for sc, r in F.items():
        if "via" in r:
            out.insert(out.index(r["via"]) + 1 + (sc == WEB_MLV), sc)
    return out


# one Mw per event
def convert(r, x, z, yr):
    """Mw and σ of native values with a relation; σ grows by GROW per unit outside the fitted native range.
    Also returns the group of each value and whether it lies outside the range."""
    x = x - r.get("shift", 0.0)
    g = groups(r["split"], z, yr)
    y, s, out = np.full(len(x), np.nan), np.full(len(x), np.nan), np.zeros(len(x), bool)
    for q, f in r["parts"].items():
        k = g == q
        y[k], s[k] = conv(f, x[k])
        d = np.clip(f["xmin"] - x[k], 0, None) + np.clip(x[k] - f["xmax"], 0, None)
        s[k], out[k] = np.minimum(s[k] + GROW * d, S_MAX), d > 0
    return y, s, g, out


def proxies(e, M, F, scales=None, judge=None):
    """
    Converted value of every scale with a relation, per event.

    Values on the 0.1 grid are dithered within their bin (uniform, seed from SEED and the scale name) before
    conversion. Returns scale -> table indexed like e: x, raw (undithered Mw), y (dithered), s, rel, out, res
    (a scale of NOT_BELOW) and ok. With judge 'depth' a surface-wave scale is ok for events not deeper than SW_Z;
    otherwise a scale of NOT_BELOW is ok where its raw value reaches NOT_BELOW_MW.
    """
    P, judge = {}, judge or JUDGE
    z, yr = e.z.to_numpy(float), e.yr.to_numpy(float)
    for sc in scales or F:
        x = e.event_id.map(M[M.scale == sc].set_index("event_id").mag).to_numpy(float)
        k = np.isfinite(x)
        if not k.any():
            continue
        u = np.random.default_rng(SEED + zlib.crc32(sc.encode())).uniform(-0.05, 0.05, len(x))
        xd = np.where(np.abs(x * 10 - np.round(x * 10)) < 1e-6, x + u, x)
        d = pd.DataFrame({"x": x, "raw": np.nan, "y": np.nan, "s": np.nan, "rel": None, "out": False}, index=e.index)
        raw, s, g, out = convert(F[sc], x[k], z[k], yr[k])
        base = F[sc].get("via", sc)
        d.loc[k, "raw"], d.loc[k, "s"], d.loc[k, "out"] = raw, s, out
        d.loc[k, "y"] = convert(F[sc], xd[k], z[k], yr[k])[0]
        d.loc[k, "rel"] = np.where(g == "all", base, base + " | " + g)
        d["res"] = bool(re.match(NOT_BELOW, sc))
        d["ok"] = k & ~(z > SW_Z) if judge == "depth" and re.match(SW, sc) else k & ~(d.res & (d.raw < NOT_BELOW_MW))
        P[sc] = d
    return P


def assign(e, M, R, F, rm, prio, old=OLD, P=None, judge=None):
    """
    One Mw per event. From PRE76: the reference Mw, else Ruiz and Madariaga, else the first eligible scale of
    prio, else none. Before PRE76: Ruiz and Madariaga, else the reference Mw, else the levels of old in their order
    and Cabello before CAB_BEFORE (Centennial: an Mw as given, else its preferred magnitude, mB by Abe (1982) with
    the depth limit SW_Z, Ms and untyped values (less 0.2) by Di Giacomo et al. (2015); ISC-GEM: direct where its
    table flags the value d, proxy otherwise), else the first eligible scale of prio. A scale of NOT_BELOW
    is eligible when its own converted value reaches NOT_BELOW_MW; with judge 'other' when the converted value
    of the event's first other scale does (its own value if there is no other scale).

    Returns the mw table (columns of the brief) in the order of e.
    """
    n = len(e)
    raw, mw, sig = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan)
    kind, sc, rel = np.full(n, "none", object), np.full(n, None, object), np.full(n, "", object)
    flags = np.full(n, "", object)
    add = lambda k, f: flags.__setitem__(k, np.where(flags[k] == "", f, flags[k] + ";" + f))
    Mi = M.set_index(["event_id", "scale"])
    wide = lambda c: e.event_id.map(M[M.scale == c].set_index("event_id").mag).to_numpy(float)
    judge = judge or JUDGE
    P = proxies(e, M, F, prio, judge) if P is None else P
    oth = first([(c, P[c].raw.to_numpy()) for c in prio if c in P and not P[c].res.iloc[0]] + [("", np.full(n, np.nan))])[0]
    for c in prio[::-1]:
        if c not in P:
            continue
        d = P[c]
        k = d.ok.to_numpy()
        if judge == "other" and d.res.iloc[0]:
            k = np.isfinite(d.raw.to_numpy()) & (np.where(np.isfinite(oth), oth, d.raw) >= NOT_BELOW_MW)
        raw[k], mw[k], sig[k], kind[k], sc[k], rel[k], flags[k] = d.raw[k], d.y[k], d.s[k], "proxy", c, d.rel[k], ""
        add(k & d.out.to_numpy(), "outside_fitted_range")
        if "via" in F[c]:
            add(k, f"relation_of_{F[c]['via'].replace(' ', '_')}" + ("_shifted" if F[c].get("shift") else ""))
    yr = e.yr.to_numpy()
    # before 1976
    cab = first([(c, wide(c)) for c in ["Cabello Mw", "Cabello final"]])
    k = (yr < CAB_BEFORE) & np.isfinite(cab[0])
    raw[k], mw[k], sig[k], kind[k], sc[k], rel[k], flags[k] = cab[0][k], cab[0][k], SIG_CAB, "cabello", cab[1][k], "", ""
    cent = M[M.scale.str.startswith("Cent ")].assign(ty=lambda d: d.mag_type.map(CENT_TY))
    cent = cent[(cent.ty == 0) | (cent.ty.notna() & cent.note.eq("preferred"))]
    cent = cent.sort_values("ty", kind="stable").drop_duplicates("event_id").set_index("event_id")
    deep = e.set_index("event_id").z.reindex(cent.index).to_numpy(float) > SW_Z
    cv = np.select([cent.ty == 0, cent.ty == 1], [cent.mag, MB_A82(cent.mag, deep)], MS_DG15(cent.mag - 0.2 * (cent.ty == 3)))
    cm = e.event_id.map(pd.Series(cv, index=cent.index)).to_numpy(float)
    cs = e.event_id.map(pd.Series(np.where(cent.ty == 1, SIG_MB, SIG_CENT), index=cent.index)).to_numpy(float)
    cmw = e.event_id.isin(cent.index[cent.ty == 0]).to_numpy()
    cn = e.event_id.map(cent.scale).to_numpy()
    g = M[M.scale == "ISC-GEM Mw"].set_index("event_id")
    gem, gs = wide("ISC-GEM Mw"), e.event_id.map(g.err).fillna(SIG_GEM).to_numpy()
    gd = e.event_id.isin(g.index[g.note.astype(str).str.contains("s=d")]).to_numpy()
    lev = {"Centennial Mw": (cm, cs, cmw), "Centennial converted": (cm, cs, ~cmw), "ISC-GEM direct": (gem, gs, gd),
           "ISC-GEM proxy": (gem, gs, ~gd)}
    for nm in old[::-1]:
        v, s, ok = lev[nm]
        k = (yr < PRE76) & np.isfinite(v) & ok
        gm = nm.startswith("ISC-GEM")
        raw[k], mw[k], sig[k], kind[k], rel[k], flags[k] = v[k], v[k], s[k], "iscgem" if gm else "centennial", "", ""
        sc[k] = "ISC-GEM Mw" if gm else cn[k]
        if nm == "ISC-GEM proxy":
            add(k, "iscgem_proxy")
        if nm == "Centennial converted":
            add(k & e.event_id.isin(cent.index[cent.ty >= 2]).to_numpy(), "converted_from_ms")
            add(k & e.event_id.isin(cent.index[cent.ty == 1]).to_numpy(), "converted_from_mb")
    # measured Mw
    r = R.reindex(e.event_id)
    k = r.y.notna().to_numpy()
    raw[k], mw[k], sig[k], kind[k], sc[k], rel[k], flags[k] = r.y[k], r.y[k], r.sig[k], "direct", r.scale[k], "", r.flag[k]
    r = rm.drop_duplicates("event_id").set_index("event_id").reindex(e.event_id)
    k = r.mag.notna().to_numpy() & ((yr < PRE76) | (kind != "direct"))
    raw[k], mw[k], sig[k], kind[k], sc[k], rel[k], flags[k] = r.mag[k], r.mag[k], r.sig[k], "rm18", "rm2018", "", r["flags"][k]
    add(kind == "none", "no_mw")
    src = Mi.reindex(pd.MultiIndex.from_arrays([e.event_id, sc]))
    out = pd.DataFrame({"event_id": e.event_id.to_numpy(), "mw": np.round(mw + 1e-9, 1), "mw_sigma": np.round(sig, 3),
                        "mw_kind": kind, "mw_src": src.src.to_numpy(), "mw_src_id": src.src_id.to_numpy(),
                        "mw_agency": src.agency.to_numpy(), "mw_type": src.mag_type.to_numpy(),
                        "native_value": src.mag.to_numpy(), "relation_id": rel, "mw_raw": np.round(raw, 3), "flags": flags})
    k = (kind == "rm18")
    out.loc[k, ["mw_src", "mw_src_id", "mw_agency", "mw_type"]] = np.c_[np.full(k.sum(), "rm2018"), r.src_id[k],
                                                                       np.full(k.sum(), "rm2018"), np.full(k.sum(), "Mw")]
    out.loc[k, "native_value"] = r.mag[k].to_numpy(float)
    return out


def combine(e, R, F, P, prio, mw, corr=True):
    """
    Converted events take the weighted mean of their eligible scales instead of the first one.

    Scales with at least N_MEAN pairs (and those that borrow their relation) enter. corr=True weights by the
    inverse covariance, with the correlation between scales of the conversion residuals (converted minus
    reference Mw, 4.5 to 6); corr=False is the inverse-variance mean of Lolli et al. (2014). Source columns
    stay those of the first scale; flag 'mean_of_scales' where more than one scale entered.
    """
    sc = [s for s in prio if s in P and F[s]["n"] >= N_MEAN and "via" not in F[s]]
    sc += [s for s in prio if s in P and F[s].get("via") in sc]
    y = e.event_id.map(R.y).to_numpy(float)
    res = pd.DataFrame({s: np.where((y >= 4.5) & (y < 6.0), P[s].raw - y, np.nan) for s in sc})
    C = res.corr(min_periods=100).fillna(0.0).to_numpy() if corr else np.eye(len(sc))
    np.fill_diagonal(C, 1.0)
    for i, s in enumerate(sc):
        if "via" in F[s]:
            j = sc.index(F[s]["via"])
            C[i], C[:, i] = C[j], C[:, j]
            C[i, i], C[i, j], C[j, i] = 1.0, 0.99, 0.99
    ok = np.vstack([P[s].ok.to_numpy() for s in sc])
    Y = np.vstack([np.where(o, P[s].y, np.nan) for o, s in zip(ok, sc)])
    Yr = np.vstack([np.where(o, P[s].raw, np.nan) for o, s in zip(ok, sc)])
    S = np.vstack([P[s].s.to_numpy(float) for s in sc])
    has = np.isfinite(Y)
    out = mw.copy()
    px = (mw.mw_kind == "proxy").to_numpy() & has.any(axis=0)
    pat, inv = np.unique(has[:, px].T, axis=0, return_inverse=True)
    inv = np.ravel(inv)
    val, raw, sig = (np.full(px.sum(), np.nan) for _ in range(3))
    for q, row in enumerate(pat):
        i, k = np.flatnonzero(row), np.flatnonzero(inv == q)
        w, v = np.linalg.eigh(C[np.ix_(i, i)])
        Ci = (v * (1 / np.maximum(w, 0.05))) @ v.T
        s = S[i][:, px][:, k].T
        A = (Ci[None] / (s[:, :, None] * s[:, None, :])).sum(axis=2)
        den = A.sum(axis=1)
        val[k], raw[k] = (A * Y[i][:, px][:, k].T).sum(axis=1) / den, (A * Yr[i][:, px][:, k].T).sum(axis=1) / den
        sig[k] = 1 / np.sqrt(den)
    out.loc[px, "mw"], out.loc[px, "mw_sigma"], out.loc[px, "mw_raw"] = np.round(val + 1e-9, 1), np.round(sig, 3), np.round(raw, 3)
    many = np.zeros(len(mw), bool)
    many[px] = has[:, px].sum(axis=0) > 1
    fl = out["flags"].to_numpy(object)
    fl[many] = np.where(fl[many] == "", "mean_of_scales", fl[many] + ";mean_of_scales")
    out["flags"] = fl
    return out


def old_big(e, M, mw):
    """Events before PRE76 with ISC-GEM or Centennial at BIG or more whose values differ by BIG_DIFF or more."""
    w = M[M.scale.eq("ISC-GEM Mw") | M.scale.str.startswith("Cent ")]
    g = w[w.scale == "ISC-GEM Mw"].set_index("event_id").mag
    c = w[w.scale != "ISC-GEM Mw"].sort_values("mag", ascending=False).drop_duplicates("event_id").set_index("event_id")
    d = pd.DataFrame({"iscgem": g, "centennial": c.mag, "cent_scale": c.scale}).dropna()
    d = d[(d[["iscgem", "centennial"]].max(axis=1) >= BIG) & ((d.iscgem - d.centennial).abs() >= BIG_DIFF)]
    x = e.set_index("event_id").join(mw.set_index("event_id")[["mw", "mw_kind"]])
    d = d.join(x[["time", "lat", "lon", "yr", "mw", "mw_kind"]])
    return d[d.yr < PRE76].drop(columns="yr").sort_values("time").reset_index()


def overrides(d, cols, flag="flags", f=A6):
    """
    Accepted rows of the A6 table applied to d (one row per event).

    cols maps a property of the table to a column of d (created if missing). The value replaces the column's,
    the row's sigma goes to <column>_sigma where d has it, the columns of A6_ALSO are set, and the flag
    a6_<property> is added. Returns the table and the number of rows applied.
    """
    if not Path(f).exists():
        return d, 0
    o = pd.read_csv(f, dtype=str)
    o = o[(o.status == "accepted") & o.property.isin(list(cols)) & o.event_id.isin(d.event_id)]
    d = d.copy()
    at = pd.Series(d.index, index=d.event_id)
    for r in o.itertuples():
        j, c = at[r.event_id], cols[r.property]
        if c not in d:
            d[c] = None
        num = pd.api.types.is_numeric_dtype(d[c])
        d.loc[j, c] = (float(r.new_value) if pd.notna(r.new_value) else np.nan) if num else r.new_value
        if c + "_sigma" in d and pd.notna(r.sigma):
            d.loc[j, c + "_sigma"] = float(r.sigma)
        for k, v in A6_ALSO.get(r.property, {}).items():
            if k in d:
                d.loc[j, k] = v
        old = d.loc[j, flag]
        d.loc[j, flag] = f"{old};a6_{r.property}" if isinstance(old, str) and old else f"a6_{r.property}"
    return d, len(o)


def sha(f):
    return hashlib.sha256(Path(f).read_bytes()).hexdigest()


def manifest(files):
    f = OUT / "MANIFEST.csv"
    m = pd.read_csv(f) if f.exists() else pd.DataFrame(columns=["file", "run", "rows", "sha256"])
    new = pd.DataFrame([{"file": str(p.relative_to(OUT)), "run": RUN, "rows": len(d), "sha256": sha(p)} for p, d in files.items()])
    pd.concat([m[~m.file.isin(new.file)], new], ignore_index=True).to_csv(f, index=False)


def main():
    e, M, rm = load()
    R, tab, W = reference(M)
    print("events", len(e), "magnitude rows", len(M), "with a reference Mw", len(R), R.scale.value_counts().to_dict())
    print("reference σ from three members:", {k: round(v, 3) for k, v in ref_sigma(W).items()})
    F = relations(M, R, e)
    F0 = relations(M, R, e, quiet=True, floor=None, boot=0)
    at = [f"mw_at_{v}" for v in AT[:3]]
    fl = rel_table(F).set_index("relation_id")[["form", "n"] + at].join(
        rel_table(F0).set_index("relation_id")[["form", "n"] + at], how="outer", lsuffix="", rsuffix="_no_floor").reset_index()
    prio = priority(F)
    print("priority by σ:", json.dumps(prio))
    if PRIORITY and PRIORITY != prio:
        print("PRIORITY at the top of the file differs from the order of this fit; the setting is used")
    prio = [s for s in (PRIORITY or prio) if s in F]
    P = proxies(e, M, F, prio)
    mw = assign(e, M, R, F, rm, prio, P=P)
    if COMBINE == "mean":
        mw = combine(e, R, F, P, prio, mw)
    mw, n6 = overrides(mw, A6_MW)
    print("A6 corrections applied:", n6)
    big = old_big(e, M, mw)
    none = e.merge(mw[mw.mw_kind == "none"][["event_id"]], on="event_id").drop(columns=["t", "yr"])
    x = mw[(mw.mw_kind == "proxy") & (mw.mw >= PROXY_REVIEW) & (e.yr >= PRE76).to_numpy()]
    large = e[["event_id", "time", "lat", "lon", "z"]].merge(x, on="event_id").sort_values("mw", ascending=False)
    json.dump({k: {**r, "cv": r["cv"]} for k, r in F.items()}, open(OUT / f"relations_{RUN}.json", "w"), default=float)
    files = {OUT / f"mw_{RUN}.csv": mw, OUT / f"relations_{RUN}.csv": rel_table(F), OUT / f"mw_offsets_{RUN}.csv": tab.round(3),
             OUT / f"relations_floor_{RUN}.csv": fl,
             OUT / "review" / f"mw_iscgem_centennial_{RUN}.csv": big, OUT / "review" / f"no_mw_{RUN}.csv": none,
             OUT / "review" / f"mw_large_proxy_{RUN}.csv": large, OUT / "review" / f"mw_reference_dropped_{RUN}.csv": outliers(M)}
    for f, d in files.items():
        d.to_csv(f, index=False)
    manifest(files)
    k = mw.mw >= 4.45
    print("kinds:", mw.mw_kind.value_counts().to_dict())
    print("Mw >= 4.5:", int(k.sum()), mw[k].mw_kind.value_counts().to_dict())
    print("proxy scales, Mw >= 4.5:", mw[k & (mw.mw_kind == "proxy")].relation_id.value_counts().head(12).to_dict())
    print("no Mw:", len(none), "| M >= 7 with ISC-GEM and Centennial apart:", len(big),
          f"| converted Mw >= {PROXY_REVIEW} from {PRE76} on:", len(large))


if __name__ == "__main__":
    main()

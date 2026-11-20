"""C4: one Mw per earthquake (D-CAT-15, D-MAG-01-11).

Every native magnitude of the frozen tables is joined to its event. Measured Mw (GCMT, W-phase and regional moment
magnitudes) is put on one scale and is the reference. Every converted agency and scale gets a relation fitted on
Chilean pairs: the native magnitude regressed on the reference Mw, the slope corrected for the reference error, the
relation inverted. From 1976 each event takes its measured Mw, else Ruiz and Madariaga (2018), else the first
converted scale of the priority list (surface-wave scales only for events not deeper than 60 km). Before 1976 a
moment-based value goes before a converted one and Centennial before ISC-GEM inside each level. Abe's mB in the
Centennial catalogue is converted with our own relation (D-CAT-15). Ported from psha_chile8 catalog/magnitude.py.
"""
import re
import zlib

import numpy as np
import pandas as pd

from .match import CFG, table

C = CFG["magnitude"]
GC = "GCMT Mw"
WFAM, LAST = C["wfam"], C["last"]
BINS, GBINS = np.array(C["bins"]), C["gbins"]
KNOTS = np.round(np.arange(*C["knots"]) if len(C["knots"]) == 3 else C["knots"], 1)
COMCAT = {("us", "mww"): "NEIC Mww", ("us", "mwr"): "NEIC Mwr", ("us", "mwb"): "NEIC Mwb", ("us", "mb"): "NEIC mb",
          ("us", "ms"): "NEIC MS", ("guc", "ml"): "GUC ML", ("guc", "md"): "GUC MD", ("guc", "mwr"): "GUC Mwr",
          ("guc", "m"): "GUC M", ("san", "md"): "SAN md", ("hrv", "mwc"): GC, ("hrv", "mw"): GC, ("gcmt", "mwc"): GC,
          ("iscgem", "mw"): "ISC-GEM Mw", ("iscgemsup", "mw"): "ISC-GEM Mw"}
ALIAS = {("isc", "GCMT", "MW"): GC, ("gcmt", "GCMT", "Mw"): GC, ("isc", "GUC", "Mww"): "CSN Mww",
         ("csn", "CSN", "Mww"): "CSN Mww", ("csn", "CSN", "Mw"): "CSN web Mw"}
ABE = f"Cent {C['abe_agency']} mB"
# Ms of the Centennial catalogue: Di Giacomo et al. (2015); Abe (1982) eqs. 5 and 7 for mB (option abe1982)
MS_DG15 = lambda x: np.exp(-0.222 + 0.233 * x) + 2.863
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


def load(e, L):
    """
    Every native magnitude on the events: one row per event and scale (the first source in the source list that
    gives it; ISC-GEM from its own table, which has the direct / proxy flag). Coda and duration magnitudes of the
    CSN before 1990 are left out. Returns M and the Ruiz and Madariaga values.
    """
    L = L[["event_id", "src", "src_id"]].drop_duplicates(["src", "src_id"])
    yr = e.set_index("event_id").yr
    cd = C["coda"]
    rows = []
    for s in C["sources"]:
        m = pd.read_csv(table(s, "mags"), dtype=str).merge(L[L.src == s], on=["src", "src_id"])
        m["mag"] = pd.to_numeric(m.mag, errors="coerce")
        m = m[m.mag.notna()]
        if s == "gcmt":
            m = m[m.agency == "GCMT"]
        key = m[["agency", "mag_type"]].drop_duplicates()
        key["scale"] = [scale(s, a, t) for a, t in zip(key.agency, key.mag_type)]
        m = m.merge(key, on=["agency", "mag_type"])
        coda = m.agency.isin(cd["agencies"]) & m.mag_type.str.lower().isin(cd["types"]) & \
            (m.event_id.map(yr) < cd["before"]).to_numpy()
        rows.append(m[~coda])
    M = pd.concat(rows, ignore_index=True)
    M["o"] = M.src.map({s: i for i, s in enumerate(C["sources"])})
    M.loc[(M.src == "iscgem") & (M.scale == "ISC-GEM Mw"), "o"] = -1
    M["p"] = M.note.eq("preferred")
    M = M.sort_values(["o", "p"], ascending=[True, False], kind="stable").drop_duplicates(["event_id", "scale"])
    M["err"] = pd.to_numeric(M.mag_err, errors="coerce")
    M = M[["event_id", "scale", "mag", "err", "src", "src_id", "agency", "mag_type", "note"]].reset_index(drop=True)
    return M, rm18(L)


def rm18(L):
    """Ruiz and Madariaga Mw: a number as given; a range by its middle, '>' and '<' by the bound, '~' by the value,
    '(Ms)' as Mw; all but the plain numbers flagged and given a larger σ."""
    m = pd.read_csv(table("rm2018", "mags"), dtype=str).merge(L[L.src == "rm2018"], on=["src", "src_id"])
    rows = []
    for r in m.itertuples():
        v = [float(q) for q in re.findall(r"\d+\.?\d*", str(r.note).split("(")[0])]
        if not v:
            continue
        fl = [f for f, k in (("rm18_range", len(v) > 1), ("rm18_bound", r.note[0] in "<>"),
                             ("rm18_approx", r.note[0] == "~"), ("rm18_ms", "(Ms)" in r.note)) if k]
        s0 = C["sigma"]["rm"]
        sig = max(s0, (max(v) - min(v)) / 2) if len(v) > 1 else s0 + 0.1 * bool(fl)
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

    Per 0.25 bin of the pair mean: n, mean, median of member − NEIC Mww (the mean is used: the values are rounded to
    0.1, so medians jump). A member is flat when no bin with n_bin pairs departs from its overall mean by more than
    `flat` and two standard errors; it then gets one constant, else its bin means. Returns the table and, per member,
    the shift (to add) per bin.
    """
    rows, off = [], {WFAM[0]: np.zeros(len(BINS) - 1)}
    nb, dm = C["n_bin"], C["dmax"]
    for c in [GC] + WFAM[1:] + [LAST]:
        x = W[[WFAM[0], c]].dropna()
        d, mm = np.clip((x[c] - x[WFAM[0]]).to_numpy(), -dm, dm), x.mean(axis=1).to_numpy()
        k = (mm >= BINS[0]) & (mm < BINS[-1])
        med = float(np.mean(d[k])) if k.sum() >= nb else 0.0
        bm, far = [], False
        for lo, hi in zip(BINS[:-1], BINS[1:]):
            kb = (mm >= lo) & (mm < hi)
            v, se = (float(np.mean(d[kb])), float(np.std(d[kb]) / np.sqrt(kb.sum()))) if kb.sum() >= nb else (np.nan, np.nan)
            far |= abs(v - med) > max(C["flat"], 2 * se)
            bm.append(v)
            rows.append({"member": c, "against": WFAM[0], "lo": lo, "hi": hi, "n": int(kb.sum()), "mean": v, "se": se})
        bm = np.array(bm)
        off[c] = -np.round(np.where(np.isnan(bm), med, bm), 2) if far else np.full(len(bm), -round(med, 2))
        rows.append({"member": c, "against": WFAM[0], "lo": BINS[0], "hi": BINS[-1], "n": int(k.sum()), "mean": med,
                     "sd": float(np.std(d[k])) if k.any() else np.nan, "flat": not far,
                     "shift": np.nan if far or c == GC else -round(med, 2)})
    return pd.DataFrame(rows), off


def outliers(M):
    """CSN regional Mw values further than tol from the median of the event's other moment magnitudes (D-MAG-06):
    event_id, scale, mag, others, n (how many others), dropped (n reaches the minimum)."""
    g = C["reg"]
    W = M[M.scale.isin(g["scales"] + g["others"])].pivot(index="event_id", columns="scale", values="mag") \
        .reindex(columns=g["scales"] + g["others"])
    med = W[g["others"]].median(axis=1)
    x = W[g["scales"]].stack().rename("mag").reset_index()
    x["others"], x["n"] = x.event_id.map(med), x.event_id.map(W[g["others"]].notna().sum(axis=1))
    x["dropped"] = x.n >= g["n"]
    return x[(x.mag - x.others).abs() > g["tol"] + 1e-9].reset_index(drop=True)


def reference(M):
    """
    Reference Mw per event, on the NEIC Mww scale (D-MAG-02). The CSN outliers are left out after the offsets are
    measured. GCMT at m_hi and above, then the W family in order (each member shifted to NEIC Mww). Below m_hi the W
    family, then GCMT lowered by a line in the GCMT value that is zero at m_hi, with CSN Mww after GCMT below m_csn.
    The CSN Mw of the ISC Bulletin only where nothing else exists, and those events are no pairs (fit False).

    Returns R (y, sig, scale, flag, fit per event), the offsets table and the member values W.
    """
    cols = [GC] + WFAM + [LAST]
    W = M[M.scale.isin(cols)].pivot(index="event_id", columns="scale", values="mag").reindex(columns=cols)
    tab, off = offsets(W)
    for r in outliers(M).query("dropped").itertuples():
        W.loc[r.event_id, r.scale] = np.nan
    g = W[GC].to_numpy()
    sh = {}
    for c in WFAM + [LAST]:
        v = W[c].to_numpy()
        sh[c] = v + off[c][np.clip(np.digitize(np.nan_to_num(v, nan=5.0), BINS) - 1, 0, len(BINS) - 2)]
    fam = [(c, sh[c]) for c in WFAM[:-1]]
    cw = sh[WFAM[-1]]
    main = first(fam)[0]
    comp = np.where(np.isfinite(main), main, cw)
    hi_m = C["m_hi"]
    k = np.isfinite(g) & np.isfinite(comp) & (g >= C["ramp_lo"]) & (g < hi_m)
    d = np.clip(g - comp, -C["dmax"], C["dmax"])[k]
    b = -np.sum(d * (hi_m - g[k])) / np.sum((hi_m - g[k]) ** 2) if k.sum() >= C["n_bin"] else 0.0
    a = -b * hi_m
    gl = g - np.clip(a + b * np.clip(g, C["ramp_lo"], None), 0, None)
    tab = pd.concat([tab, pd.DataFrame([{"member": GC, "against": "W family (line in the GCMT value, zero at m_hi)",
                                         "lo": C["ramp_lo"], "hi": hi_m, "n": int(k.sum()), "mean": a + b * C["ramp_lo"],
                                         "shift": b}])], ignore_index=True)
    judge = np.where(np.isfinite(g), g, comp)
    top = first([(GC, gl)] + fam + [(WFAM[-1], cw)])
    mid = first(fam + [(WFAM[-1], cw), (GC + " lowered", gl)])
    low = first(fam + [(GC + " lowered", gl), (WFAM[-1], cw)])
    y = np.where(judge >= hi_m, top[0], np.where(judge >= C["m_csn"], mid[0], low[0]))
    nm = np.where(judge >= hi_m, top[1], np.where(judge >= C["m_csn"], mid[1], low[1]))
    k = np.isnan(y) & np.isfinite(sh[LAST])
    y, nm = np.where(k, sh[LAST], y), np.where(k, LAST, nm)
    R = pd.DataFrame({"y": y, "scale": nm, "fit": ~k}, index=W.index)
    R["flag"] = np.where((R.scale == GC + " lowered") | ((R.scale == GC).to_numpy() & (g - y > 0.005)), "gcmt_lowered", "")
    R["scale"] = R.scale.replace(GC + " lowered", GC)
    R["sig"] = np.where(R.scale == GC, C["sigma_ref"]["gcmt"], C["sigma_ref"]["w"])
    return R[np.isfinite(R.y)], tab, W


# relations: native = a + b1 (Mw - k) below the knot k, b2 above; a straight line has b1 = b2
def pl(p, y):
    a, b1, b2, k = p
    return a + np.where(y < k, b1, b2) * (y - k)


def fit_inv(y, x, sy, form="linear"):
    """
    Native magnitude on reference Mw by least squares, slopes divided by λ = 1 − sy² / var(y) for the error of y
    (D-MAG-07). Selection of the pairs on y (an incomplete reference) does not bias this direction. A hinge is kept
    only where the slope drops above the knot. Returns p = (a, b1, b2, k), the residual sd s of the native value, sy
    and n.
    """
    lam = max(1 - sy ** 2 / max(np.var(y), 1e-6), 0.5)
    kr = C["kref"]
    c = np.linalg.lstsq(np.c_[np.ones_like(y), y - kr], x, rcond=None)[0]
    best = (np.inf, kr, c[1], c[1])
    if form == "hinge":
        best = (float(np.sum((x - c[0] - c[1] * (y - kr)) ** 2)), *best[1:])
        for k in KNOTS:
            if (y < k).sum() < C["min_side"] or (y >= k).sum() < C["min_side"]:
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


def conv(f, x):
    """Mw from native x by inverting the relation. σ is the scatter of the native value over the local slope, with
    the part from the reference error taken out, never below that error."""
    a, b1, b2, k = f["p"]
    b = np.where(x < a, b1, max(b2, C["b_sat"]))
    s = np.maximum(np.sqrt(np.maximum(f["s"] ** 2 - (b * f["sy"]) ** 2, 0)) / b, f["sy"])
    return k + (x - a) / b, np.minimum(s, C["s_max"])


def groups(split, z, yr):
    if split == "depth":
        return np.where(np.isfinite(z) & (z > C["z_cut"]), "deep", "shallow")
    if split == "depth3":
        return np.select([np.isfinite(z) & (z > C["z_nest"]), np.isfinite(z) & (z > C["z_cut"])],
                         [f"below {C['z_nest']:.0f} km", "deep"], "shallow")
    if split == "sw":
        return np.where(np.isfinite(z) & (z > C["sw_z"]), "deep", "shallow")
    if split == "period":
        return np.where(yr < C["p_cut"], f"before {C['p_cut']}", f"{C['p_cut']} on")
    return np.full(len(z), "all")


def cv(x, y, yr, z, sy, form, split):
    """Squared residual of the native value on the held-out time block, per pair; None if a group is too small."""
    o = np.argsort(yr, kind="stable")
    fo = np.empty(len(yr), int)
    fo[o] = np.arange(len(yr)) * C["n_fold"] // len(yr)
    g = groups(split, z, yr)
    out = np.full(len(x), np.nan)
    for i in range(C["n_fold"]):
        for q in np.unique(g):
            a, b = (fo != i) & (g == q), (fo == i) & (g == q)
            if a.sum() < C["n_line"]:
                return None
            out[b] = (x[b] - pl(fit_inv(y[a], x[a], sy, form)["p"], y[b])) ** 2
    return out


def fit_scale(sc, x, y, yr, z, sy, cand=None, boot=None):
    """
    Relation of one scale: the simplest candidate (form, split) whose cross-validation loss in time blocks is within
    one standard error of the best one, fitted on all pairs, with bootstrap intervals of Mw at the native values `at`.
    """
    if cand is None:
        cand = [("linear", "none")]
        if len(x) >= C["n_all"]:
            cand += [("hinge", "none"), ("linear", "depth")] + [("linear", "period")] * (sc in C["period_split"]) + \
                [("hinge", "depth")] + [("hinge", "period")] * (sc in C["period_split"]) + \
                [("linear", "depth3"), ("hinge", "depth3")]
    loss = {c: v for c in cand if len(cand) > 1 and (v := cv(x, y, yr, z, sy, *c)) is not None}
    sel = cand[0]
    if loss:
        mean = {c: float(np.mean(v)) for c, v in loss.items()}
        ref = loss[min(mean, key=mean.get)]
        sel = next(c for c in cand if c in loss and np.mean(loss[c] - ref) <= np.std(loss[c] - ref) / np.sqrt(len(ref)))
    form, split = sel
    g = groups(split, z, yr)
    rng = np.random.default_rng(C["seed"])
    boot = C["n_boot"] if boot is None else boot
    parts = {}
    for q in np.unique(g):
        k = g == q
        f = fit_inv(y[k], x[k], sy, form)
        f.update(xmin=float(np.percentile(x[k], 1)), xmax=float(np.percentile(x[k], 99)), ymin=float(y[k].min()),
                 ymax=float(y[k].max()))
        f["sigma"] = float(conv(f, np.array([f["p"][0] - 0.5]))[1][0])
        if boot:
            i = np.flatnonzero(k)
            b = np.array([conv(fit_inv(y[j], x[j], sy, form), np.array(C["at"]))[0]
                          for j in (rng.choice(i, len(i)) for _ in range(boot))])
            f["ci"] = np.percentile(b, [2.5, 97.5], axis=0).T.round(3).tolist()
        parts[q] = f
    if split.startswith("depth"):
        f = fit_inv(y, x, sy, form)
        f.update(xmin=float(np.percentile(x, 1)), xmax=float(np.percentile(x, 99)), ymin=float(y.min()), ymax=float(y.max()))
        f["sigma"] = float(conv(f, np.array([f["p"][0] - 0.5]))[1][0])
        parts["no depth"] = f
    n = sum(f["n"] for q, f in parts.items() if q != "no depth")
    return {"scale": sc, "form": form, "split": split, "parts": parts, "n": n,
            "sigma": float(np.sqrt(sum(f["n"] * f["sigma"] ** 2 for q, f in parts.items() if q != "no depth") / n)),
            "cv": {f"{a} | {b}": float(np.mean(v)) for (a, b), v in loss.items()}}


def relations(M, R, e, floor=None, ref_scales=None, boot=None):
    """
    Relations of the converted scales with at least n_line pairs against the reference (pairs below the floor and
    pairs on the CSN Mw of the ISC Bulletin left out). ref_scales keeps only pairs whose reference is one of those
    scales (Q-67 trial). CSN web Ml takes the GUC ML relation; CSN web Mlv its own with n_all pairs, otherwise the ML
    relation shifted by its median residual.
    """
    a = e.set_index("event_id")
    floor = C["fit_min"] if floor is None else floor
    R = R[R.fit & (R.y >= floor)]
    if ref_scales is not None:
        R = R[R.scale.isin(ref_scales)]
    P = M[M.scale.str.contains(C["proxy"])].join(R[["y", "sig"]], on="event_id", how="inner")
    P = P.join(a[["yr", "z"]], on="event_id")
    P = P[P.yr.notna()]
    ml, web, mlv = C["ml"], C["web_ml"], C["web_mlv"]
    F = {}
    for sc, p in P.groupby("scale"):
        if len(p) < C["n_line"] or sc == web or (sc == mlv and len(p) < C["n_all"]):
            continue
        s = float(np.sqrt(np.mean(p.sig ** 2)))
        F[sc] = fit_scale(sc, p.mag.to_numpy(), p.y.to_numpy(), p.yr.to_numpy(), p.z.to_numpy(), s, boot=boot)
    if ml in F:
        F[web] = {**F[ml], "scale": web, "via": ml}
        p = P[P.scale == mlv]
        if mlv not in F:
            F[mlv] = {**F[ml], "scale": mlv, "via": ml}
        if "via" in F[mlv] and len(p) >= C["n_line"]:
            g = groups(F[ml]["split"], p.z.to_numpy(), p.yr.to_numpy())
            d = np.concatenate([p.mag[g == q] - pl(f["p"], p.y[g == q].to_numpy()) for q, f in F[ml]["parts"].items()
                                if q != "no depth"])
            F[mlv] = {**F[ml], "scale": mlv, "via": ml, "shift": round(float(np.median(d)), 2), "n_shift": len(d)}
    return F


def abe_offset(M, R, rm, e):
    """
    Offset of a measured Mw (Ruiz and Madariaga, an ISC-GEM direct Mw, or the reference Mw) to Abe's mB of the
    Centennial catalogue on the same events deeper than sw_z (D-CAT-15): the median of Mw − mB, slope held at 1
    because the pairs are few. Returns the offset, its number of pairs and all pairs.
    """
    x = M[M.scale == ABE].set_index("event_id").mag
    g = M[(M.scale == "ISC-GEM Mw") & M.note.astype(str).str.contains("s=d")].set_index("event_id").mag
    y = rm.drop_duplicates("event_id").set_index("event_id").mag.reindex(x.index)
    for v in (R.y, g):
        y = y.fillna(v.reindex(x.index))
    p = pd.DataFrame({"x": x, "y": y}).dropna().join(e.set_index("event_id")[["yr", "z"]])
    d = p[p.z > C["sw_z"]]
    return float(np.median(d.y - d.x)), len(d), p


def rel_table(F):
    rows = []
    for sc, r in F.items():
        for g, f in r["parts"].items():
            ag, _, ty = sc.partition(" ")
            row = {"relation_id": sc if g == "all" else f"{sc} | {g}", "agency": ag, "type": ty, "via": r.get("via", ""),
                   "shift": r.get("shift", 0.0), "split": r["split"], "group": g, "form": r["form"], "a": f["p"][0],
                   "b1": f["p"][1], "b2": f["p"][2], "knot": f["p"][3], "native_min": f["xmin"], "native_max": f["xmax"],
                   "mw_min": f["ymin"], "mw_max": f["ymax"], "n": f["n"], "sd_native": f["s"], "sy": f["sy"],
                   "sigma": f["sigma"]}
            for i, v in enumerate(C["at"]):
                row[f"mw_at_{v}"] = float(conv(f, np.array([v]))[0][0])
                if "ci" in f:
                    row[f"lo_{v}"], row[f"hi_{v}"] = f["ci"][i]
            row["cv_chosen"] = r["cv"].get(f"{r['form']} | {r['split']}")
            rows.append(row)
    return pd.DataFrame(rows).round(4)


def priority(F):
    """Scales ordered by the σ of their relation; ISC mb and NEIC mb one family at the place of the better, ISC
    first; a scale that borrows a relation follows its lender."""
    s = {sc: r["sigma"] for sc, r in F.items() if "via" not in r}
    fam = [sc for sc in C["mb_family"] if sc in s]
    for sc in fam:
        s[sc] = min(s[q] for q in fam)
    out = sorted(s, key=lambda sc: (s[sc], C["mb_family"].index(sc) if sc in fam else 0, sc))
    for sc, r in F.items():
        if "via" in r:
            out.insert(out.index(r["via"]) + 1 + (sc == C["web_mlv"]), sc)
    return out


# one Mw per event
def convert(r, x, z, yr):
    """Mw and σ of native values with a relation; σ grows by `grow` per unit outside the fitted native range. Also
    returns the group of each value and whether it lies outside the range."""
    x = x - r.get("shift", 0.0)
    g = groups(r["split"], z, yr)
    if "no depth" in r["parts"]:
        g = np.where(np.isfinite(z), g, "no depth")
    y, s, out = np.full(len(x), np.nan), np.full(len(x), np.nan), np.zeros(len(x), bool)
    for q, f in r["parts"].items():
        k = g == q
        y[k], s[k] = conv(f, x[k])
        d = np.clip(f["xmin"] - x[k], 0, None) + np.clip(x[k] - f["xmax"], 0, None)
        s[k], out[k] = np.minimum(s[k] + C["grow"] * d, C["s_max"]), d > 0
    return y, s, g, out


def dither(x, name, ids):
    """Values on the 0.1 grid moved uniformly within their bin (D-MAG-08). The draw is fixed per event and scale
    (a hash of seed, scale and event id), so it does not change when other events enter or leave."""
    h = np.array([zlib.crc32(f"{C['seed']}|{name}|{i}".encode()) for i in ids], float)
    u = (h / 2 ** 32 - 0.5) * 0.1
    return np.where(np.abs(x * 10 - np.round(x * 10)) < 1e-6, x + u, x)


def proxies(e, M, F, scales):
    """
    Converted value of every scale with a relation, per event: x, raw (undithered Mw), y (dithered), s, rel, out and
    ok (a surface-wave scale only for events not deeper than sw_z, D-MAG-05).
    """
    P = {}
    z, yr = e.z.to_numpy(float), e.yr.to_numpy(float)
    for sc in scales:
        x = e.event_id.map(M[M.scale == sc].set_index("event_id").mag).to_numpy(float)
        k = np.isfinite(x)
        if not k.any():
            continue
        d = pd.DataFrame({"x": x, "raw": np.nan, "y": np.nan, "s": np.nan, "rel": None, "out": False}, index=e.index)
        raw, s, g, out = convert(F[sc], x[k], z[k], yr[k])
        base = F[sc].get("via", sc)
        d.loc[k, "raw"], d.loc[k, "s"], d.loc[k, "out"] = raw, s, out
        d.loc[k, "y"] = convert(F[sc], dither(x, sc, e.event_id.to_numpy())[k], z[k], yr[k])[0]
        d.loc[k, "rel"] = np.where(g == "all", base, base + " | " + g)
        d["ok"] = k & ~(z > C["sw_z"]) if re.match(C["sw"], sc) else k
        P[sc] = d
    return P


def assign(e, M, R, F, rm, prio, abe=None):
    """
    One Mw per event (D-MAG-02, 03). From 1976: the reference Mw, else Ruiz and Madariaga, else the first eligible
    scale of prio, else none. Before 1976: Ruiz and Madariaga, the reference Mw, a Centennial Mw, an ISC-GEM direct
    Mw, the preferred Centennial magnitude converted, an ISC-GEM proxy Mw, Cabello before 1904, else the first
    eligible scale of prio. Centennial: Ms and untyped values (less 0.2) by Di Giacomo et al. (2015); Mw values that are
    conversions by their authors left out; Abe's mB deeper than sw_z plus the measured offset `abe` (option native),
    shallower or without depth only where nothing else exists, or by Abe (1982). Returns the mw table in the order of e.
    """
    n = len(e)
    raw, mw, sig = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan)
    kind, sc, rel = np.full(n, "none", object), np.full(n, None, object), np.full(n, "", object)
    flags = np.full(n, "", object)
    add = lambda k, f: flags.__setitem__(k, np.where(flags[k] == "", f, flags[k] + ";" + f))
    wide = lambda c: e.event_id.map(M[M.scale == c].set_index("event_id").mag).to_numpy(float)
    S = C["sigma"]
    yr = e.yr.to_numpy()
    cent = M[M.scale.str.startswith("Cent ")].assign(ty=lambda d: d.mag_type.map(C["cent_types"]))
    cent = cent[~((cent.ty == 0) & cent.agency.isin(C["cent_not_native"]))]
    cent = cent[(cent.ty == 0) | (cent.ty.notna() & cent.note.eq("preferred"))]
    cent = cent.sort_values("ty", kind="stable").drop_duplicates("event_id").set_index("event_id")
    ze = e.set_index("event_id").z.reindex(cent.index).to_numpy(float)
    mb = (cent.ty == 1).to_numpy()
    ab = mb & (cent.scale == ABE).to_numpy()
    deep = ze > C["sw_z"]
    if C["abe"] == "native":
        xa = dither(cent.mag.to_numpy(float), ABE, cent.index.to_numpy()) + abe
        fb = e.event_id.map(pd.Series(np.where(ab & ~deep, xa, np.nan), index=cent.index)).to_numpy(float)
        k = (yr < C["pre76"]) & np.isfinite(fb)
        raw[k], mw[k], sig[k], kind[k], rel[k] = fb[k], fb[k], C["abe_sigma_shallow"], "centennial", ""
        sc[k] = ABE
        add(k, "abe_mb_shallow_or_no_depth")
    P = proxies(e, M, F, prio)
    for c in prio[::-1]:
        if c not in P:
            continue
        d = P[c]
        k = d.ok.to_numpy()
        raw[k], mw[k], sig[k], kind[k], sc[k], rel[k], flags[k] = d.raw[k], d.y[k], d.s[k], "proxy", c, d.rel[k], ""
        add(k & d.out.to_numpy(), "outside_fitted_range")
        if "via" in F[c]:
            add(k, f"relation_of_{F[c]['via'].replace(' ', '_')}" + ("_shifted" if F[c].get("shift") else ""))
    # before 1976
    cab = first([(c, wide(c)) for c in ["Cabello Mw", "Cabello final"]])
    k = (yr < C["cab_before"]) & np.isfinite(cab[0])
    raw[k], mw[k], sig[k], kind[k], sc[k], rel[k], flags[k] = cab[0][k], cab[0][k], S["cabello"], "cabello", cab[1][k], "", ""
    cv = np.select([cent.ty == 0, mb], [cent.mag, MB_A82(cent.mag, deep)], MS_DG15(cent.mag - 0.2 * (cent.ty == 3)))
    cs = np.where(mb, S["mb"], S["cent"])
    if C["abe"] == "native":
        cv = np.where(ab, np.where(deep, xa, np.nan), cv)
        cs = np.where(ab, C["abe_sigma"], cs)
    cm = e.event_id.map(pd.Series(cv, index=cent.index)).to_numpy(float)
    cs = e.event_id.map(pd.Series(cs, index=cent.index)).to_numpy(float)
    cmw = e.event_id.isin(cent.index[cent.ty == 0]).to_numpy()
    cn = e.event_id.map(cent.scale).to_numpy()
    g = M[M.scale == "ISC-GEM Mw"].set_index("event_id")
    gem, gs = wide("ISC-GEM Mw"), e.event_id.map(g.err).fillna(S["iscgem"]).to_numpy()
    gd = e.event_id.isin(g.index[g.note.astype(str).str.contains("s=d")]).to_numpy()
    lev = {"Centennial Mw": (cm, cs, cmw), "Centennial converted": (cm, cs, ~cmw), "ISC-GEM direct": (gem, gs, gd),
           "ISC-GEM proxy": (gem, gs, ~gd)}
    for nm in C["old"][::-1]:
        v, s, ok = lev[nm]
        k = (yr < C["pre76"]) & np.isfinite(v) & ok
        gm = nm.startswith("ISC-GEM")
        raw[k], mw[k], sig[k], kind[k], rel[k], flags[k] = v[k], v[k], s[k], "iscgem" if gm else "centennial", "", ""
        sc[k] = "ISC-GEM Mw" if gm else cn[k]
        if nm == "ISC-GEM proxy":
            add(k, "iscgem_proxy")
        if nm == "Centennial converted":
            add(k & e.event_id.isin(cent.index[cent.ty >= 2]).to_numpy(), "converted_from_ms")
            add(k & e.event_id.isin(cent.index[mb & ~ab]).to_numpy(), "converted_from_mb")
            add(k & e.event_id.isin(cent.index[ab]).to_numpy(), "converted_from_abe_mb")
    # measured Mw
    r = R.reindex(e.event_id)
    k = r.y.notna().to_numpy()
    raw[k], mw[k], sig[k], kind[k], sc[k], rel[k], flags[k] = r.y[k], r.y[k], r.sig[k], "direct", r.scale[k], "", r.flag[k]
    r = rm.drop_duplicates("event_id").set_index("event_id").reindex(e.event_id)
    k = r.mag.notna().to_numpy() & ((yr < C["pre76"]) | (kind != "direct"))
    rd = dither(r.mag.to_numpy(float), "rm2018", e.event_id.to_numpy())
    raw[k], mw[k], sig[k], kind[k], sc[k], rel[k], flags[k] = r.mag[k], rd[k], r.sig[k], "rm18", "rm2018", "", r["flags"][k]
    add(kind == "none", "no_mw")
    src = M.set_index(["event_id", "scale"]).reindex(pd.MultiIndex.from_arrays([e.event_id, sc]))
    out = pd.DataFrame({"event_id": e.event_id.to_numpy(), "mw": np.round(mw + 1e-9, 1), "mw_sigma": np.round(sig, 3),
                        "mw_kind": kind, "mw_src": src.src.to_numpy(), "mw_src_id": src.src_id.to_numpy(),
                        "mw_agency": src.agency.to_numpy(), "mw_type": src.mag_type.to_numpy(),
                        "native_value": src.mag.to_numpy(), "relation_id": rel, "mw_raw": np.round(raw, 3),
                        "mw_flags": flags})
    k = kind == "rm18"
    out.loc[k, ["mw_src", "mw_src_id", "mw_agency", "mw_type"]] = np.c_[np.full(k.sum(), "rm2018"), r.src_id[k],
                                                                       np.full(k.sum(), "rm2018"), np.full(k.sum(), "Mw")]
    out.loc[k, "native_value"] = r.mag[k].to_numpy(float)
    return out


def run(e, L):
    """C4 on the located events e (event_id, yr, z = final depth): the mw table, relations, offsets and the lists."""
    M, rm = load(e, L)
    R, tab, W = reference(M)
    F = relations(M, R, e)
    prio = [s for s in C["priority"] if s in F]
    off, na, pa = abe_offset(M, R, rm, e)
    mw = assign(e, M, R, F, rm, prio, off)
    return {"mw": mw, "M": M, "R": R, "W": W, "F": F, "abe": {"offset": off, "n_deep_pairs": na}, "abe_pairs": pa,
            "offsets": tab, "rm": rm,
            "priority_fit": priority(F), "outliers": outliers(M)}

"""X1 tier 3: magnitude inventory, pairs, per-scale errors, conversion fits, published relations, checks and the
M0–M8 Mw catalogue variants (A5 exploration)."""
import itertools
import json
import time
import warnings

import numpy as np
import pandas as pd
from scipy.optimize import brentq, least_squares

import x1_io as io

warnings.filterwarnings("ignore", category=RuntimeWarning)

# settings
LABELS = ["baseline", "nb_order", "nb_calibrated"]
MIN_PAIRS = 30
MIN_TC = 100
NBOOT = 200
NBOOT_NB = 0
SIG_DEFAULT = 0.25
SIG_RM = 0.2
FORMS = ["linear", "quadratic", "exponential"]
METHODS = ["OLS", "CSQ η(TC)", "CSQ η=1", "CSQ η(TC) + eq. error"]
SPLITS = ["none", "depth", "period", "depth+period"]
ZCUT = 50.0
MREF_LOW = 5.4
NPROC = 14
SEED = 1
COMCAT_MAP = {("us", "mww"): "NEIC Mww", ("us", "mwr"): "NEIC Mwr", ("us", "mwb"): "NEIC Mwb", ("us", "mb"): "NEIC mb",
              ("guc", "ml"): "GUC ML", ("guc", "md"): "GUC MD", ("guc", "mwr"): "GUC Mwr", ("san", "md"): "SAN md",
              ("guc", "m"): "GUC M"}
SKIP_ISC = {"GCMT", "IDC", "EIDC"}
PUB = {
    "ISC mb": {"L23 exp": lambda x: np.exp(0.082 + 0.266 * x) + 1.039,
               "L23 CBL-R": lambda x: np.where(x > 4.98, 1.390 * x - 1.942, x),
               "L14 exp": lambda x: np.exp(0.741 + 0.210 * x) - 0.785,
               "DG15 exp": lambda x: np.exp(-4.664 + 0.859 * x) + 4.555, "W16 ODR": lambda x: 1.084 * x - 0.142,
               "S06": lambda x: 0.85 * x + 1.03, "P19 Chile": lambda x: 1.227 * x - 1.005,
               "C25 ISC mb": lambda x: 0.87 * x + 0.75},
    "NEIC mb": {"L23 exp": lambda x: np.exp(0.948 + 0.179 * x) - 1.240,
                "L23 CBL-R": lambda x: np.where(x > 5.47, 1.508 * x - 2.780, x),
                "W16 ODR": lambda x: 1.159 * x - 0.659, "S06": lambda x: 0.85 * x + 1.03,
                "P19 Chile": lambda x: 1.227 * x - 1.005, "C25 pooled": lambda x: 1.04 * x - 0.02,
                "C25 file": lambda x: 1.03 * x + 0.28},
    "ISC MS": {"L23 exp": lambda x: np.exp(-0.137 + 0.229 * x) + 2.673,
               "L14": lambda x: np.where(x <= 5.5, np.exp(2.133 + 0.063 * x) - 6.205, np.exp(-0.109 + 0.229 * x) + 2.586),
               "DG15 exp": lambda x: np.exp(-0.222 + 0.233 * x) + 2.863,
               "W16 ODR": lambda x: np.where(x <= 6.0, 0.616 * x + 2.369, 0.994 * x + 0.100),
               "S06": lambda x: np.where(x <= 6.1, 0.67 * x + 2.07, 0.99 * x + 0.08), "P19 Chile": lambda x: 0.935 * x + 0.585},
    "NEIC MS": {"W16 ODR": lambda x: np.where(x <= 6.47, 0.723 * x + 1.798, 1.005 * x - 0.026),
                "S06": lambda x: np.where(x <= 6.1, 0.67 * x + 2.07, 0.99 * x + 0.08),
                "P19 Chile": lambda x: 0.935 * x + 0.585},
    "NEIC Ms_20": {"L23 exp": lambda x: np.exp(1.108 + 0.124 * x) - 0.246},
    "GUC ML": {"P19 Chile ML": lambda x: 0.899 * x + 0.676, "C25 CSN ML ≤ 50 km": lambda x: 0.80 * x + 1.15,
               "C25 CSN ML > 50 km": lambda x: 0.94 * x + 0.30},
    "CSN web Ml": {"P19 Chile ML": lambda x: 0.899 * x + 0.676, "C25 CSN ML ≤ 50 km": lambda x: 0.80 * x + 1.15},
    "GUC MW": {"C25 CSN Mw": lambda x: 0.92 * x + 0.43},
    "NEIC Mww": {"C25 USGS Mw": lambda x: 0.94 * x + 0.35},
}


# core: regression and triple collocation
def model(form, p, x):
    if form == "linear":
        return p[0] + p[1] * x
    if form == "quadratic":
        return p[0] + p[1] * x + p[2] * x ** 2
    return np.exp(p[0] + p[1] * x) + p[2]


def dmodel(form, p, x):
    if form == "linear":
        return np.full_like(x, p[1], dtype=float)
    if form == "quadratic":
        return p[1] + 2 * p[2] * x
    return p[1] * np.exp(p[0] + p[1] * x)


def start(form, x, y):
    b1, b0 = np.polyfit(x, y, 1)
    if form == "linear":
        return np.array([b0, b1])
    if form == "quadratic":
        return np.polyfit(x, y, 2)[::-1].copy()
    best = None
    for b in np.r_[np.linspace(0.02, 2.0, 60)]:
        A = np.c_[np.exp(b * (x - x.mean())), np.ones_like(x)]
        c, res, *_ = np.linalg.lstsq(A, y, rcond=None)
        r = np.sum((A @ c - y) ** 2)
        if c[0] > 0 and (best is None or r < best[0]):
            best = (r, b, c)
    if best is None:
        return np.array([0.0, 0.3, y.mean() - 1])
    _, b, c = best
    return np.array([np.log(c[0]) - b * x.mean(), b, c[1]])


def fit(x, y, form="linear", method="CSQ", sx=0.2, sy=0.1, eqerr=False):
    """
    Fit Mw = f(x) by OLS or chi-square (effective-variance) regression.

    Parameters
    ----------
    x, y : arrays of native and reference magnitudes
    form : 'linear', 'quadratic' or 'exponential' (Mw = exp(a + b x) + c)
    method : 'OLS' or 'CSQ'; CSQ weights each residual by sy^2 + se^2 + f'(x)^2 sx^2
    sx, sy : measurement errors (scalars or arrays)
    eqerr : add an equation error se so that the reduced chi-square is 1 (Gasperini et al. 2025)

    Returns
    -------
    dict with p, se (equation error), sigma (residual sd), chi2, m2ll, aic, bic, n, k
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    sx, sy = np.broadcast_to(sx, x.shape).astype(float), np.broadcast_to(sy, x.shape).astype(float)
    p = start(form, x, y)
    k = len(p)
    se = 0.0

    def var(p_, se_):
        return sy ** 2 + se_ ** 2 + dmodel(form, p_, x) ** 2 * sx ** 2

    def res(p_, se_):
        r = y - model(form, p_, x)
        return r if method == "OLS" else r / np.sqrt(var(p_, se_))

    for it in range(8 if eqerr else 1):
        sol = least_squares(lambda q: res(q, se), p, method="lm" if len(x) > k + 2 else "trf", max_nfev=4000)
        p = sol.x
        if not eqerr:
            break
        dof = max(len(x) - k, 1)
        f = lambda s: np.sum((y - model(form, p, x)) ** 2 / var(p, s)) / dof - 1  # noqa: E731
        new = 0.0 if f(0.0) <= 0 else brentq(f, 0.0, 3.0)
        if abs(new - se) < 1e-4:
            se = new
            break
        se = new
    r = y - model(form, p, x)
    if method == "OLS":
        v = np.full_like(x, np.var(r))
    else:
        v = var(p, se)
    chi2 = float(np.sum(r ** 2 / v))
    m2ll = float(np.sum(r ** 2 / v + np.log(2 * np.pi * v)))
    kk = k + (1 if eqerr else 0) + (1 if method == "OLS" else 0)
    n = len(x)
    return {"p": p, "se": se, "sigma": float(np.std(r)), "chi2": chi2, "m2ll": m2ll, "aic": m2ll + 2 * kk,
            "bic": m2ll + kk * np.log(n), "n": n, "k": kk}


def tc(a, b, c):
    """Error sd of three collocated measurements (Stoffelen 1998 covariance form), each in its own units."""
    C = np.cov(np.c_[a, b, c].T)
    s = [C[0, 0] - C[0, 1] * C[0, 2] / C[1, 2], C[1, 1] - C[0, 1] * C[1, 2] / C[0, 2],
         C[2, 2] - C[0, 2] * C[1, 2] / C[0, 1]]
    return np.sqrt(np.clip(s, 1e-6, None))


# long magnitude table on events
def long_table(o, lab):
    """Every native magnitude of every origin of an event: ev, scale, mag, err, nsta."""
    key = pd.Series(np.arange(len(o)), index=pd.MultiIndex.from_arrays([o.src, o.sid]))
    rows = []
    for s in ["isc", "comcat", "iscgem", "gcmt", "centennial", "potin", "csn"]:
        m = io.mags(s)
        idx = key.reindex(pd.MultiIndex.from_arrays([np.full(len(m), s), m.src_id.astype(str)])).to_numpy()
        m = m.assign(i=idx)
        m = m[m.i.notna() & m.mag.notna()]
        if s == "isc":
            m = m[~m.agency.isin(SKIP_ISC)]
            sc = m.agency + " " + m.mag_type
        elif s == "comcat":
            sc = pd.Series([COMCAT_MAP.get((a, t)) for a, t in zip(m.agency, m.mag_type)], index=m.index)
        elif s == "iscgem":
            sc = pd.Series("ISC-GEM Mw", index=m.index)
        elif s == "gcmt":
            m = m[m.agency == "GCMT"]
            sc = pd.Series("GCMT Mw", index=m.index)
        elif s == "centennial":
            sc = "Cent " + m.agency + " " + m.mag_type
        elif s == "potin":
            sc = "Potin " + m.mag_type
        else:
            sc = "CSN web " + m.mag_type
        m = m.assign(scale=sc.to_numpy())
        m = m[m.scale.notna()]
        rows.append(pd.DataFrame({"ev": lab[m.i.astype(int).to_numpy()], "scale": m.scale.to_numpy(),
                                  "mag": m.mag.to_numpy(), "err": pd.to_numeric(m.mag_err, errors="coerce").to_numpy(),
                                  "nsta": pd.to_numeric(m.n_sta, errors="coerce").to_numpy(), "src": s,
                                  "note": m.note.to_numpy()}))
    L = pd.concat(rows, ignore_index=True)
    L.loc[L.scale.isin(["GUC Mww", "CSN web Mww"]), "scale"] = "CSN Mww"
    order = {"isc": 0, "gcmt": 0, "csn": 1, "comcat": 2}
    L["o"] = L.src.map(order).fillna(3)
    L = L.sort_values("o").drop_duplicates(["ev", "scale"]).drop(columns="o")
    return L


def wide(L, scales):
    return L[L.scale.isin(scales)].pivot_table(index="ev", columns="scale", values="mag", aggfunc="first")


def inventory():
    o = io.load("origins", dtype={"sid": str})
    lab = np.arange(len(o))
    L = long_table(o, lab)
    L["yr"] = np.floor(io.year(o.t.to_numpy()[L.ev.to_numpy()]))
    L["band"] = io.label(L.mag.to_numpy(), [(-9, 3.5, "< 3.5"), (3.5, 4.5, "3.5–4.5"), (4.5, 5.5, "4.5–5.5"),
                                            (5.5, 6.5, "5.5–6.5"), (6.5, 99, "≥ 6.5")])
    t = L.groupby("scale").agg(n=("mag", "size"), first=("yr", "min"), last=("yr", "max"), mmin=("mag", "min"),
                               mmax=("mag", "max"), median=("mag", "median")).sort_values("n", ascending=False)
    b = L.pivot_table(index="scale", columns="band", values="mag", aggfunc="size").fillna(0).astype(int)
    t = t.join(b)
    t.to_csv(io.TAB / "t3_inventory.csv")
    y = L.pivot_table(index="scale", columns="yr", values="mag", aggfunc="size").fillna(0)
    y.to_csv(io.CACHE / "inventory_year.csv.gz")
    return t, y


# events: depth, year, references
def event_attrs(nm):
    lv = io.load("locvariants")
    x = lv[(lv["match"] == nm) & (lv["loc"] == "L-a")].set_index("ev")
    return x


def refs(W):
    """Reference Mw per event: GCMT, CSN Mww and USGS Mww, the latter two raw and shifted by their median offset."""
    R = pd.DataFrame(index=W.index)
    R["gcmt"] = W.get("GCMT Mw")
    off = {}
    for nm, col in (("csn", "CSN Mww"), ("usgs", "NEIC Mww"), ("gucr", "GUC Mwr"), ("neicr", "NEIC Mwr")):
        v = W.get(col)
        if v is None:
            continue
        R[f"{nm}_raw"] = v
        d = (R.gcmt - v).dropna()
        off[nm] = float(d.median()) if len(d) >= 20 else 0.0
        R[nm] = v + off[nm]
    return R, off


# fits per scale
def split_groups(ev, attrs, how):
    z = attrs.z.reindex(ev).to_numpy()
    yr = attrs.yr.reindex(ev).to_numpy()
    dz = np.where(np.isfinite(z) & (z > ZCUT), "> 50 km", "≤ 50 km")
    per = io.label(np.nan_to_num(yr, nan=1990), io.PERIODS)
    if how == "none":
        return np.full(len(ev), "all", object)
    if how == "depth":
        return dz.astype(object)
    if how == "period":
        return per
    return np.char.add(np.char.add(dz.astype(str), " | "), per.astype(str)).astype(object)


def fit_scale(args):
    sc, x, y, ev, attrs, sig, boot, seed = args
    rng = np.random.default_rng(seed)
    out = []
    sx0, sy0 = sig.get(sc, SIG_DEFAULT), sig.get("GCMT Mw", 0.1)
    for method in METHODS:
        for form in FORMS:
            for sp in SPLITS:
                g = split_groups(ev, attrs, sp)
                tot = {"m2ll": 0.0, "k": 0, "n": 0}
                parts = []
                ok = True
                for gv in np.unique(g):
                    k = g == gv
                    if k.sum() < MIN_PAIRS:
                        ok = False
                        continue
                    if method == "OLS":
                        kw = {"method": "OLS"}
                    elif method == "CSQ η=1":
                        kw = {"method": "CSQ", "sx": 0.2, "sy": 0.2}
                    else:
                        kw = {"method": "CSQ", "sx": sx0, "sy": sy0, "eqerr": "eq." in method}
                    try:
                        r = fit(x[k], y[k], form, **kw)
                    except Exception:  # noqa: BLE001
                        ok = False
                        continue
                    pr = {}
                    if boot and sp in ("none", "depth+period") or (boot and method == "CSQ η(TC)"):
                        bs = []
                        for _ in range(boot if sp == "none" else max(boot // 4, 20)):
                            j = rng.integers(0, k.sum(), k.sum())
                            try:
                                bs.append(fit(x[k][j], y[k][j], form, **kw)["p"])
                            except Exception:  # noqa: BLE001
                                pass
                        if len(bs) > 10:
                            bs = np.array(bs)
                            for q in (4.5, 5.0, 5.5, 6.0):
                                pv = np.array([model(form, b, q) for b in bs])
                                pr[f"ci_{q}"] = (float(np.percentile(pv, 2.5)), float(np.percentile(pv, 97.5)))
                            pr["p_lo"] = list(np.percentile(bs, 2.5, axis=0))
                            pr["p_hi"] = list(np.percentile(bs, 97.5, axis=0))
                    rr = y[k] - model(form, r["p"], x[k])
                    parts.append({"group": gv, "n": int(k.sum()), "p": list(r["p"]), "se": r["se"], "sigma": r["sigma"],
                                  "aic": r["aic"], "bic": r["bic"], "chi2": r["chi2"], "xmin": float(x[k].min()),
                                  "xmax": float(x[k].max()), "res_slope_t": float(np.polyfit(
                                      attrs.yr.reindex(ev[k]).fillna(2000).to_numpy(), rr, 1)[0]) if k.sum() > 3 else np.nan,
                                  **pr})
                    tot["m2ll"] += r["m2ll"]
                    tot["k"] += r["k"]
                    tot["n"] += r["n"]
                if not parts:
                    continue
                out.append({"scale": sc, "method": method, "form": form, "split": sp, "complete": ok, "n": tot["n"],
                            "aic": tot["m2ll"] + 2 * tot["k"], "bic": tot["m2ll"] + tot["k"] * np.log(max(tot["n"], 1)),
                            "sx": sx0, "sy": sy0, "parts": parts})
    return out


def predict(fr, x, ev, attrs):
    """Converted Mw and its sd for native values x of events ev, by the fit record fr (groups by its split).
    Outside the fitted range the relation continues linearly: slope 1 below, the end slope (1–2) above; the sd grows
    by 0.1 per unit beyond the range."""
    g = split_groups(ev, attrs, fr["split"])
    y = np.full(len(x), np.nan)
    s = np.full(len(x), np.nan)
    parts = {p["group"]: p for p in fr["parts"]}
    whole = parts.get("all")
    for gv in np.unique(g):
        p = parts.get(gv, whole)
        if p is None:
            p = max(fr["parts"], key=lambda q: q["n"])
        k = g == gv
        pp = np.array(p["p"])
        lo, hi = p["xmin"], p["xmax"]
        xx = np.clip(x[k], lo, hi)
        yy = model(fr["form"], pp, xx)
        up = np.clip(dmodel(fr["form"], pp, np.array([hi]))[0], 1.0, 2.0)
        yy = np.where(x[k] < lo, yy + (x[k] - lo), np.where(x[k] > hi, yy + up * (x[k] - hi), yy))
        y[k] = yy
        d = dmodel(fr["form"], pp, xx)
        sk = np.sqrt((d * fr["sx"]) ** 2 + p["se"] ** 2) if "CSQ" in fr["method"] else np.full(k.sum(), p["sigma"])
        sk = np.where(np.isfinite(sk), np.maximum(sk, 0.08), p["sigma"])
        s[k] = sk + 0.1 * np.abs(x[k] - xx)
    return y, s


def valid(fr):
    for p in fr["parts"]:
        if not np.isfinite(p["sigma"]) or p["sigma"] > 1.0:
            return False
        g = np.linspace(p["xmin"], p["xmax"], 25)
        d = dmodel(fr["form"], np.array(p["p"]), g)
        if not np.all(np.isfinite(d)) or d.min() <= 0.05:
            return False
    return True


def choose_fit(F, sc, method, forms=FORMS, splits=SPLITS):
    c = [f for f in F if f["scale"] == sc and f["method"] == method and f["form"] in forms and f["split"] in splits
         and f["complete"] and valid(f)]
    if not c:
        c = [f for f in F if f["scale"] == sc and f["method"] == method and f["form"] in forms and f["split"] == "none"
             and valid(f)]
    return min(c, key=lambda f: f["bic"]) if c else None


def fit_all(L, R, attrs, sig, boot, ref="gcmt"):
    scales = [s for s in L.scale.unique() if s not in ("GCMT Mw",)]
    W = wide(L, scales)
    yref = R[ref] if ref in R else R.gcmt
    jobs = []
    for i, sc in enumerate(scales):
        x = W[sc].dropna()
        ev = x.index.intersection(yref.dropna().index)
        if len(ev) < MIN_PAIRS:
            continue
        jobs.append((sc, W.loc[ev, sc].to_numpy(float), yref.loc[ev].to_numpy(float), ev.to_numpy(), attrs, sig, boot,
                     SEED + i))
    import multiprocessing as mp
    with mp.get_context("fork").Pool(NPROC) as pool:
        res = pool.map(fit_scale, jobs)
    return [r for rr in res for r in rr]


# Mw catalogue variants
def build_mw(L, R, attrs, F, sig, rm, cab, variant, F_alt=None):
    """
    One Mw per event for a variant (M0–M8). Returns DataFrame ev, mw, sig, how.
    """
    rng = np.random.default_rng(SEED)
    scales = sorted({f["scale"] for f in F if not f["scale"].startswith(("Potin ", "Cent ")) and f["scale"] not in
                     ("ISC-GEM Mw", "GCMT Mw", "CSN Mww", "NEIC Mww")})
    W = wide(L, scales + ["ISC-GEM Mw"])
    cent = L[L.scale.str.startswith("Cent ")].pivot_table(index="ev", columns="scale", values="mag", aggfunc="first")
    ev = attrs.index.to_numpy()
    yr = attrs.yr.to_numpy()
    n = len(ev)
    mw, sg = np.full(n, np.nan), np.full(n, np.nan)
    how = np.full(n, None, object)
    method = {"M1": "OLS"}.get(variant, "CSQ η(TC) + eq. error")
    forms = ["linear"] if variant == "M2" else FORMS
    splits = ["none"] if variant == "M3" else SPLITS
    FF = F_alt if (variant == "M6" and F_alt is not None) else F
    # proxies
    prox = []
    for sc in scales:
        if sc not in W:
            continue
        x = W[sc].reindex(ev).to_numpy(float)
        k = np.isfinite(x)
        if not k.any():
            continue
        xd = x + rng.uniform(-0.05, 0.05, n)
        fr = choose_fit(FF, sc, method, forms, splits)
        if fr is None:
            continue
        y, s = np.full(n, np.nan), np.full(n, np.nan)
        if variant == "M4" and sc in PUB:
            nm = PUBBEST.get(sc)
            if nm:
                y[k] = PUB[sc][nm](xd[k])
                s[k] = fr["parts"][0]["sigma"]
            else:
                y[k], s[k] = predict(fr, xd[k], ev[k], attrs)
        else:
            y[k], s[k] = predict(fr, xd[k], ev[k], attrs)
        prox.append((sc, y, s))
    if prox:
        Y = np.vstack([p[1] for p in prox])
        S = np.vstack([p[2] for p in prox])
        Sm = np.where(np.isfinite(Y), S, np.inf)
        j = np.argmin(Sm, axis=0)
        best = Y[j, np.arange(n)]
        bs = S[j, np.arange(n)]
        ok = np.isfinite(best)
        names = np.array([p[0] for p in prox])
        if variant == "M5":
            w = np.where(np.isfinite(Y), 1 / np.where(np.isfinite(S), S, np.inf) ** 2, 0)
            sw = w.sum(axis=0)
            wm = np.where(sw > 0, np.nansum(np.where(w > 0, Y, 0) * w, axis=0) / np.where(sw > 0, sw, 1), np.nan)
            mw[sw > 0], sg[sw > 0], how[sw > 0] = wm[sw > 0], 1 / np.sqrt(sw[sw > 0]), "weighted proxies"
        else:
            mw[ok], sg[ok], how[ok] = best[ok], bs[ok], names[j[ok]]
    # before 1976
    old = yr < 1976
    gem = W["ISC-GEM Mw"].reindex(ev).to_numpy(float) if "ISC-GEM Mw" in W else np.full(n, np.nan)
    cm = np.full(n, np.nan)
    for c in cent.columns:
        v = cent[c].reindex(ev).to_numpy(float)
        if c.endswith(" Mw"):
            cv = v
        elif c.endswith(" Ms") or c.endswith(" UK"):
            vv = v - (0.2 if c.endswith(" UK") else 0.0)
            cv = PUB["ISC MS"]["DG15 exp"](vv)
        elif c.endswith(" mB"):
            cv = v
        else:
            cv = np.full(n, np.nan)
        cm = np.where(np.isnan(cm) & np.isfinite(cv), cv, cm)
    order = [("Centennial", cm, 0.25), ("ISC-GEM", gem, 0.2)] if variant == "M8" else [("ISC-GEM", gem, 0.2),
                                                                                       ("Centennial", cm, 0.25)]
    for nm, v, s in order[::-1]:
        k = old & np.isfinite(v)
        mw[k], sg[k], how[k] = v[k], s, nm
    # direct Mw
    for nm, col, s in (("USGS Mww", "usgs", sig.get("NEIC Mww", 0.1)), ("CSN Mww", "csn", sig.get("CSN Mww", 0.1)),
                       ("GCMT", "gcmt", sig.get("GCMT Mw", 0.07))):
        if col in R:
            v = R[col].reindex(ev).to_numpy(float)
            k = np.isfinite(v)
            mw[k], sg[k], how[k] = v[k], s, nm
    v = rm.reindex(ev).to_numpy(float)
    k = np.isfinite(v)
    mw[k], sg[k], how[k] = v[k], SIG_RM, "RM18"
    if variant == "M7":
        v = cab.reindex(ev).to_numpy(float)
        mw, sg, how = v, np.full(n, 0.2), np.where(np.isfinite(v), "Cabello", None)
    mw = np.where(np.isfinite(mw), mw + rng.uniform(-0.05, 0.05, n) * (how != "RM18") * 0, mw)
    return pd.DataFrame({"ev": ev, "mw": mw, "sig": sg, "how": how})


PUBBEST = {}


def cabello_on_events(o, lab):
    """Cabello's final magnitude on the events, by nearest Cabello row within 10 s and 50 km of any member origin."""
    import x1_match as X
    cab = io.events("cabello")
    cm = io.mags("cabello")
    cab["mw"] = cab.src_id.map(cm[cm.agency == "cabello"].set_index("src_id").mag)
    cab = cab[cab.t > io.tsec(["1903-12-31"])[0]].sort_values("t").reset_index(drop=True)
    ot = o.sort_values("t")
    tb = cab.t.to_numpy()
    lo = np.searchsorted(tb, ot.t.to_numpy() - 10)
    hi = np.searchsorted(tb, ot.t.to_numpy() + 10)
    nn = hi - lo
    ia = np.repeat(ot.index.to_numpy(), nn)
    ib = (np.arange(nn.sum()) - np.repeat(np.cumsum(nn) - nn, nn)) + np.repeat(lo, nn)
    d = io.hav(o.lat.to_numpy()[ia], o.lon.to_numpy()[ia], cab.lat.to_numpy()[ib], cab.lon.to_numpy()[ib])
    k = d < 50
    ia, ib, d = ia[k], ib[k], d[k]
    evl = lab[ia]
    dt = np.abs(o.t.to_numpy()[ia] - tb[ib])
    c = pd.DataFrame({"ev": evl, "j": ib, "c": dt / 10 + d / 50}).sort_values("c").drop_duplicates(["ev", "j"])
    sel = X.assign(c.ev.to_numpy(), c.j.to_numpy(), c.c.to_numpy(), "greedy")
    c = c[sel]
    return pd.Series(cab.mw.to_numpy()[c.j], index=c.ev.to_numpy())


def run():
    T0 = time.time()
    o = io.load("origins", dtype={"sid": str})
    labs = io.load("labels")
    inv, invy = inventory()
    print("inventory", len(inv), round(time.time() - T0), flush=True)
    rm18 = pd.read_csv(io.TAB / "t1_rm18_matches.csv")
    rm18 = rm18[(rm18["where"] == "event") & rm18.rm_mw.notna()]
    rm_rep = {}
    base = io.load("events_baseline")
    rep = base.set_index("ev").rep
    for _, r in rm18.iterrows():
        rm_rep[int(rep[int(r.ev)])] = r.rm_mw
    store = {}
    for nm in LABELS:
        lab = labs[nm].to_numpy()
        L = long_table(o, lab)
        attrs = event_attrs(nm)
        attrs = attrs[~attrs.index.duplicated()]
        W = wide(L, L.scale.unique())
        R, off = refs(W)
        rm = pd.Series({int(lab[k]): v for k, v in rm_rep.items()})
        cab = cabello_on_events(o, lab)
        store[nm] = dict(L=L, attrs=attrs, W=W, R=R, off=off, rm=rm, cab=cab)
        print("tables", nm, len(L), round(time.time() - T0), flush=True)
    S = store["baseline"]
    L, W, R, attrs = S["L"], S["W"], S["R"], S["attrs"]
    json.dump(S["off"], open(io.TAB / "t3_reference_offsets.json", "w"), indent=1)
    sig, tct = errors(W)
    tct.to_csv(io.TAB / "t3_triple_collocation.csv", index=False)
    pd.Series(sig).to_csv(io.TAB / "t3_sigma_per_scale.csv", header=["sigma"])
    print("tc", len(tct), round(time.time() - T0), flush=True)
    pairs_report(store)
    mww_report(R, attrs)
    print("pairs", round(time.time() - T0), flush=True)
    fits = {}
    if (io.CACHE / "fits.json").exists():
        fits = json.load(open(io.CACHE / "fits.json"))
    for nm in LABELS:
        if nm in fits:
            continue
        s = store[nm]
        fits[nm] = fit_all(s["L"], s["R"], s["attrs"], sig, NBOOT if nm == "baseline" else NBOOT_NB)
        print("fits", nm, len(fits[nm]), round(time.time() - T0), flush=True)
    json.dump(fits, open(io.CACHE / "fits.json", "w"), default=float)
    s = store["baseline"]
    R6 = s["R"].copy()
    low = R6.gcmt.isna() | (R6.gcmt < MREF_LOW)
    alt = R6[["csn", "usgs"]].bfill(axis=1).iloc[:, 0] if "usgs" in R6 else R6.csn
    R6["m6ref"] = np.where(low & alt.notna() & (alt < MREF_LOW), alt, R6.gcmt)
    f6 = io.CACHE / "fits_m6.json"
    F6 = json.load(open(f6)) if f6.exists() else fit_all(s["L"], R6, s["attrs"], sig, 0, ref="m6ref")
    json.dump(F6, open(f6, "w"), default=float)
    print("fits M6", round(time.time() - T0), flush=True)
    fit_tables(fits)
    pub_bias(store["baseline"], fits["baseline"])
    checks(store["baseline"], o, labs["baseline"].to_numpy())
    print("checks", round(time.time() - T0), flush=True)
    allv = []
    for nm in LABELS:
        s = store[nm]
        for v in [f"M{i}" for i in range(9)]:
            try:
                m = build_mw(s["L"], s["R"], s["attrs"], fits[nm], sig, s["rm"], s["cab"], v,
                             F_alt=F6 if nm == "baseline" else None)
                if v == "M6" and nm != "baseline":
                    continue
                allv.append(m.assign(match=nm, variant=v))
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                with open(io.CACHE / "failures.log", "a") as fh:
                    fh.write(f"tier 3 build {nm} {v}: {e!r}\n")
    MW = pd.concat(allv, ignore_index=True)
    MW.to_csv(io.CACHE / "mw_variants.csv.gz", index=False)
    print("variants", round(time.time() - T0), flush=True)
    compare(MW, store["baseline"]["attrs"])
    plt = io.fig_setup()
    for f in (fig_raster, fig_pairs, fig_resid_time, fig_mww, fig_tc, fig_dmw, fig_fmd, fig_checks):
        try:
            f(plt, store, fits, sig, MW, invy, tct)
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            with open(io.CACHE / "failures.log", "a") as fh:
                fh.write(f"tier 3 {f.__name__}: {e!r}\n")
    print("tier 3 done", round(time.time() - T0), flush=True)


def errors(W):
    cols = [c for c in W.columns if W[c].notna().sum() >= MIN_TC and not c.startswith("Cent ")]
    cols = sorted(cols, key=lambda c: -W[c].notna().sum())[:24]
    rows = []
    for a, b, c in itertools.combinations(cols, 3):
        if {"GCMT Mw", "ISC-GEM Mw"} <= {a, b, c}:
            continue
        x = W[[a, b, c]].dropna()
        if len(x) < MIN_TC:
            continue
        s = tc(x[a].to_numpy(), x[b].to_numpy(), x[c].to_numpy())
        cc = np.corrcoef(x.to_numpy().T)
        rows.append({"a": a, "b": b, "c": c, "n": len(x), "sa": s[0], "sb": s[1], "sc": s[2],
                     "rmin": float(cc[np.triu_indices(3, 1)].min())})
    t = pd.DataFrame(rows)
    long = pd.concat([t.rename(columns={k: "scale", v: "s"})[["scale", "s", "n", "rmin"]]
                      for k, v in (("a", "sa"), ("b", "sb"), ("c", "sc"))])
    long = long[long.rmin > 0.5]
    sig = long.groupby("scale").s.median().clip(0.05, 0.6).to_dict()
    return sig, t


def pairs_report(store):
    rows = []
    for nm, s in store.items():
        W, R, at = s["W"], s["R"], s["attrs"]
        for ref in ("gcmt", "csn", "usgs", "csn_raw", "usgs_raw"):
            if ref not in R:
                continue
            y = R[ref].dropna()
            for sc in W.columns:
                if sc == "GCMT Mw":
                    continue
                ev = W[sc].dropna().index.intersection(y.index)
                if len(ev) < 10:
                    continue
                z = at.z.reindex(ev)
                yr = at.yr.reindex(ev)
                d = (y[ev] - W.loc[ev, sc])
                row = {"match": nm, "ref": ref, "scale": sc, "n": len(ev), "n_shallow": int((~(z > ZCUT)).sum()),
                       "n_deep": int((z > ZCUT).sum()), "dmed": float(d.median()), "dsd": float(d.std())}
                for lo, hi, pn in io.PERIODS:
                    row[f"n {pn}"] = int(((yr >= lo) & (yr < hi)).sum())
                if len(ev) >= MIN_PAIRS:
                    r = fit(W.loc[ev, sc].to_numpy(), y[ev].to_numpy(), "linear", "CSQ", 0.2, 0.1)
                    row["a"], row["b"] = r["p"]
                rows.append(row)
    pd.DataFrame(rows).to_csv(io.TAB / "t3_pairs.csv", index=False)


def mww_report(R, at):
    rows = []
    for col in ("csn_raw", "usgs_raw", "gucr_raw", "neicr_raw"):
        if col not in R:
            continue
        x = R[[col, "gcmt"]].dropna()
        for by, v in (("GCMT band", x.gcmt), ("Mww band", x[col])):
            b = io.label(v.to_numpy(), [(0, 5.0, "< 5.0"), (5.0, 5.4, "5.0–5.4"), (5.4, 6, "5.4–6"), (6, 7, "6–7"),
                                        (7, 10, "≥ 7")])
            for bn in ["< 5.0", "5.0–5.4", "5.4–6", "6–7", "≥ 7"]:
                y = x[b == bn]
                if len(y) < 5:
                    continue
                d = y.gcmt - y[col]
                sl = np.polyfit(y[col], y.gcmt, 1)[0] if len(y) > 10 and np.ptp(y[col]) > 0.3 else np.nan
                rows.append({"mww": col, "by": by, "band": bn, "n": len(y), "offset_med": d.median(),
                             "offset_mean": d.mean(), "sd": d.std(), "slope_ols": sl})
    pd.DataFrame(rows).to_csv(io.TAB / "t3_mww_vs_gcmt_bands.csv", index=False)


def fit_tables(fits):
    rows = []
    for nm, F in fits.items():
        for f in F:
            for p in f["parts"]:
                rows.append({"match": nm, "scale": f["scale"], "method": f["method"], "form": f["form"],
                             "split": f["split"], "complete": f["complete"], "valid": valid(f), "n_total": f["n"], "aic": f["aic"],
                             "bic": f["bic"], "group": p["group"], "n": p["n"],
                             "p": " ".join(f"{v:.4f}" for v in p["p"]), "se": p["se"], "sigma": p["sigma"],
                             "xmin": p["xmin"], "xmax": p["xmax"], "res_trend_per_yr": p["res_slope_t"],
                             **{f"Mw({q})": model(f["form"], np.array(p["p"]), q) for q in (4.0, 4.5, 5.0, 5.5, 6.0)},
                             **{f"CI {q}": p.get(f"ci_{q}") for q in (4.5, 5.0, 5.5, 6.0)}})
    t = pd.DataFrame(rows)
    t.to_csv(io.TAB / "t3_fits.csv", index=False)
    b = t[(t["match"] == "baseline") & (t.group.isin(["all"]) | (t.split != "none"))]
    sel = []
    for sc, x in t[t["match"] == "baseline"].groupby("scale"):
        for m, y in x.groupby("method"):
            yy = y[y.valid & y.complete].drop_duplicates(["form", "split"])
            if not len(yy):
                continue
            best = yy.loc[yy.bic.idxmin()]
            sel.append({"scale": sc, "method": m, "best_form": best.form, "best_split": best.split,
                        "dbic_exp_vs_lin": float(yy[(yy.form == "exponential") & (yy.split == "none")].bic.min()
                                                 - yy[(yy.form == "linear") & (yy.split == "none")].bic.min())})
    pd.DataFrame(sel).to_csv(io.TAB / "t3_best_form_split.csv", index=False)
    # same relation under the three matchings
    c = t[(t.method == "CSQ η(TC) + eq. error") & (t.split == "none")]
    c = c.pivot_table(index=["scale", "form"], columns="match", values=["n", "Mw(4.5)", "Mw(5.0)", "Mw(6.0)"])
    c.to_csv(io.TAB / "t3_fits_by_matching.csv")
    _ = b


def pub_bias(s, F):
    W, R = s["W"], s["R"]
    rows = []
    for sc, rel in PUB.items():
        if sc not in W:
            continue
        ev = W[sc].dropna().index.intersection(R.gcmt.dropna().index)
        x, y = W.loc[ev, sc].to_numpy(), R.gcmt[ev].to_numpy()
        best = None
        for nm, f in rel.items():
            r = y - f(x)
            row = {"scale": sc, "relation": nm, "n": len(x), "bias_all": float(np.median(r)), "sd": float(np.std(r))}
            for q in (4.5, 5.0, 5.5, 6.0):
                k = np.abs(x - q) <= 0.25
                row[f"bias@{q}"] = float(np.median(r[k])) if k.sum() >= 5 else np.nan
                row[f"n@{q}"] = int(k.sum())
            score = np.nanmean(np.abs([row[f"bias@{q}"] for q in (4.5, 5.0, 5.5, 6.0)]))
            row["score"] = score
            if best is None or score < best[0]:
                best = (score, nm)
            rows.append(row)
        PUBBEST[sc] = best[1] if best else None
    pd.DataFrame(rows).to_csv(io.TAB / "t3_published_bias.csv", index=False)
    json.dump(PUBBEST, open(io.TAB / "t3_published_best.json", "w"), indent=1)


def checks(s, o, lab):
    W, R, at, L = s["W"], s["R"], s["attrs"], s["L"]
    out = {}
    # Potin codes against references
    rows = []
    for code in ("Potin l", "Potin c", "Potin W", "Potin ww", "Potin B"):
        for ref in ("GCMT Mw", "CSN Mww", "NEIC Mww", "GUC ML", "GUC MD", "GUC Mwr", "GUC MW", "GUC md", "ISC mb",
                    "NEIC mb"):
            if code not in W or ref not in W:
                continue
            x = W[[code, ref]].dropna()
            if len(x) < 5:
                continue
            d = x[code] - x[ref]
            rows.append({"code": code, "ref": ref, "n": len(x), "diff_med": d.median(), "diff_sd": d.std(),
                         "frac_identical": float((d.abs() < 0.05).mean()), "years": f"{at.yr.reindex(x.index).min():.0f}–"
                                                                                    f"{at.yr.reindex(x.index).max():.0f}"})
    pd.DataFrame(rows).to_csv(io.TAB / "t3_check_potin_codes.csv", index=False)
    # Potin c and l in time against GUC ML / ISC mb
    rows = []
    for code in ("Potin c", "Potin l"):
        for ref in ("ISC mb", "GUC ML", "NEIC mb"):
            if code not in W or ref not in W:
                continue
            x = W[[code, ref]].dropna()
            yr = np.floor(at.yr.reindex(x.index))
            for y, g in (x[code] - x[ref]).groupby(yr.to_numpy()):
                if len(g) >= 10:
                    rows.append({"code": code, "ref": ref, "year": y, "n": len(g), "diff_med": g.median(),
                                 "frac_below_2": float((x.loc[g.index, code] < 2).mean())})
    pd.DataFrame(rows).to_csv(io.TAB / "t3_check_potin_by_year.csv", index=False)
    # CSN coda MD to ML
    rows = []
    for a, b in (("GUC MD", "GUC ML"), ("GUC md", "GUC ML"), ("Potin c", "Potin l"), ("GUC MD", "ISC mb"),
                 ("GUC ML", "ISC mb"), ("GUC md", "ISC mb")):
        if a in W and b in W:
            x = W[[a, b]].dropna()
            yr = at.yr.reindex(x.index)
            for lo, hi in ((1988, 2000), (2000, 2003), (2003, 2011), (2011, 2027)):
                k = (yr >= lo) & (yr < hi)
                if k.sum() >= 20:
                    r = fit(x[a][k].to_numpy(), x[b][k].to_numpy(), "linear", "CSQ", 0.2, 0.2)
                    rows.append({"x": a, "y": b, "period": f"{lo}–{hi - 1}", "n": int(k.sum()),
                                 "median_y_minus_x": float((x[b] - x[a])[k].median()), "a": r["p"][0], "b": r["p"][1]})
    pd.DataFrame(rows).to_csv(io.TAB / "t3_check_coda_ml.csv", index=False)
    # CSN web Ml vs Mlv
    rows = []
    for c in ("CSN web Ml", "CSN web Mlv", "CSN web Mw"):
        for ref in ("GCMT Mw", "NEIC mb", "NEIC Mww", "CSN Mww", "GFZ mb", "GFZ M", "SJA ML", "GUC ML"):
            if c in W and ref in W:
                x = W[[c, ref]].dropna()
                yr = at.yr.reindex(x.index)
                for lo, hi in ((2020, 2025), (2025, 2026), (2026, 2027)):
                    k = (yr >= lo) & (yr < hi)
                    if k.sum() >= 10:
                        d = (x[c] - x[ref])[k]
                        rows.append({"csn": c, "ref": ref, "period": f"{lo}–{hi - 1}", "n": int(k.sum()),
                                     "diff_med": d.median(), "diff_sd": d.std()})
    pd.DataFrame(rows).to_csv(io.TAB / "t3_check_ml_mlv.csv", index=False)
    cw = L[L.scale.isin(["CSN web Ml", "CSN web Mlv"])].copy()
    cw["t"] = at.yr.reindex(cw.ev).to_numpy()
    k = cw.t >= 2025.5
    cw[k].groupby([np.floor((cw.t[k] - 2025.5) * 12), "scale"]).mag.agg(["size", "median", lambda v: (v >= 3).mean()]
                                                                         ).to_csv(io.TAB / "t3_check_ml_mlv_monthly.csv")
    # ISC mb saturation
    rows = []
    for sc in ("ISC mb", "NEIC mb", "IDC mb", "GFZ mb", "MOS mb", "BJI mB"):
        if sc in W:
            x = W[[sc, "GCMT Mw"]].dropna()
            b = np.round(x["GCMT Mw"] * 4) / 4
            for bv, g in (x[sc] - x["GCMT Mw"]).groupby(b.to_numpy()):
                if len(g) >= 8:
                    rows.append({"scale": sc, "mw": bv, "n": len(g), "mb_minus_mw": g.median(),
                                 "q25": g.quantile(0.25), "q75": g.quantile(0.75)})
    sat = pd.DataFrame(rows)
    mbg = np.linspace(3.5, 7.0, 400)
    mwl = PUB["ISC mb"]["L23 exp"](mbg)
    sat["L23_mb_minus_mw"] = np.interp(sat.mw, mwl, mbg - mwl)
    sat.to_csv(io.TAB / "t3_check_mb_saturation.csv", index=False)
    # NEIC Ms before / after 2013
    rows = []
    for sc in ("NEIC MS", "NEIC Ms_20", "NEIC MSZ", "ISC MS", "IDC MS", "BJI Ms", "MOS MS"):
        if sc in W:
            x = W[[sc, "GCMT Mw"]].dropna()
            yr = at.yr.reindex(x.index)
            sh = (at.z.reindex(x.index) <= 70) | at.z.reindex(x.index).isna()
            for lo, hi in ((1976, 2000), (2000, 2013.6), (2013.6, 2027)):
                k = (yr >= lo) & (yr < hi) & sh
                if k.sum() >= 15:
                    r = fit(x[sc][k].to_numpy(), x["GCMT Mw"][k].to_numpy(), "linear", "CSQ", 0.2, 0.1)
                    rows.append({"scale": sc, "period": f"{lo:.0f}–{hi:.1f}", "n": int(k.sum()),
                                 "mw_minus_ms_med": float((x["GCMT Mw"] - x[sc])[k].median()),
                                 "Mw(5.5)": model("linear", r["p"], 5.5), "Mw(6.5)": model("linear", r["p"], 6.5)})
    pd.DataFrame(rows).to_csv(io.TAB / "t3_check_neic_ms.csv", index=False)
    # heaping
    rows = []
    for sc in ("GUC ML", "CSN web Ml", "ISC mb", "NEIC mb", "Potin l", "Potin c", "GUC MD"):
        if sc in W:
            v = W[sc].dropna()
            frac = np.round((v * 10) % 10).astype(int) % 10
            for d, n in frac.value_counts().sort_index().items():
                rows.append({"scale": sc, "decimal": d, "n": n, "share": n / len(v)})
    pd.DataFrame(rows).to_csv(io.TAB / "t3_check_heaping_decimals.csv", index=False)
    # GCMT and ISC-EHB Mw in 1985–1998
    em, ee = io.mags("iscehb"), io.events("iscehb")
    ee["yr"] = np.floor(io.year(ee.t.to_numpy()))
    mwid = set(em[em.mag_type.str.lower() == "mw"].src_id)
    g = io.events("gcmt")
    gy = np.floor(io.year(g.t.to_numpy()))
    rows = [{"year": int(y), "iscehb_events": int((ee.yr == y).sum()),
             "iscehb_with_mw": int(((ee.yr == y) & ee.src_id.isin(mwid)).sum()), "gcmt_events": int((gy == y).sum()),
             "iscehb_events_with_gcmt_match": int(W.reindex(at.index[(at.yr >= y) & (at.yr < y + 1)])["GCMT Mw"].notna().sum())}
            for y in range(1976, 2022)]
    pd.DataFrame(rows).to_csv(io.TAB / "t3_check_gcmt_1985_1998.csv", index=False)
    _ = (o, lab, out)


def compare(MW, at):
    m = MW[MW["match"] == "baseline"].pivot_table(index="ev", columns="variant", values="mw")
    yr = at.yr.reindex(m.index)
    rows = []
    for v in m.columns:
        d = m[v] - m["M0"]
        for lo, hi, pn in io.PERIODS:
            k = (yr >= lo) & (yr < hi) & d.notna()
            if k.sum():
                rows.append({"variant": v, "period": pn, "n": int(k.sum()), "dmed": d[k].median(), "dmean": d[k].mean(),
                             "dsd": d[k].std(), "d_q05": d[k].quantile(0.05), "d_q95": d[k].quantile(0.95),
                             "cross_45": int(((m[v] >= 4.5) != (m["M0"] >= 4.5))[k].sum())})
    pd.DataFrame(rows).to_csv(io.TAB / "t3_variant_delta.csv", index=False)
    rows = []
    dec = (np.floor(yr / 10) * 10)
    for v in m.columns:
        for dv in sorted(dec.dropna().unique()):
            k = dec == dv
            rows.append({"variant": v, "decade": int(dv), **{f"N≥{q}": int((m[v][k] >= q).sum())
                                                              for q in (4.5, 5.0, 6.0, 7.0)}})
    pd.DataFrame(rows).to_csv(io.TAB / "t3_variant_counts_decade.csv", index=False)
    h = MW[MW["match"] == "baseline"].groupby(["variant", "how"]).size().unstack(0).fillna(0).astype(int)
    h.to_csv(io.TAB / "t3_variant_sources.csv")


# figures
MAIN = ["GUC ML", "ISC mb", "NEIC mb", "ISC MS", "NEIC MS", "GUC MD", "NEIC Mww", "CSN Mww", "GUC Mwr", "NEIC Mwr",
        "IDC mb", "SJA MW", "SJA ML", "CSN web Ml", "GUC MW", "BJI mB"]


def fig_raster(plt, store, fits, sig, MW, invy, tct):
    t = invy.loc[invy.sum(axis=1).sort_values(ascending=False).index[:60]]
    t = t[[c for c in t.columns if c >= 1900]]
    fig, ax = plt.subplots(figsize=(16, 14), layout="constrained")
    im = ax.imshow(np.log10(t.to_numpy() + 0.0) , aspect="auto", cmap="viridis", interpolation="nearest",
                   extent=(t.columns.min() - 0.5, t.columns.max() + 0.5, len(t) - 0.5, -0.5), vmin=0)
    ax.set_yticks(range(len(t)), t.index, fontsize=8)
    plt.colorbar(im, ax=ax, label="log10 events per year", shrink=0.5)
    ax.set_title("Which magnitude types exist when? 60 most used agency / type pairs in the frozen tables (box)")
    io.savefig(fig, "t3_type_year_raster", "Magnitude type × year raster of the frozen source tables (60 most used "
               "agency / type pairs)")


def fig_pairs(plt, store, fits, sig, MW, invy, tct):
    s = store["baseline"]
    W, R = s["W"], s["R"]
    F = fits["baseline"]
    sc_ = [c for c in MAIN if c in W and W[c].reindex(R.gcmt.dropna().index).notna().sum() >= MIN_PAIRS][:16]
    nc = 4
    fig, ax = plt.subplots(int(np.ceil(len(sc_) / nc)), nc, figsize=(18, 4.6 * np.ceil(len(sc_) / nc)),
                           layout="constrained")
    for a, sc in zip(ax.flat, sc_):
        ev = W[sc].dropna().index.intersection(R.gcmt.dropna().index)
        x, y = W.loc[ev, sc], R.gcmt[ev]
        a.scatter(x + np.random.default_rng(0).uniform(-0.03, 0.03, len(x)), y, s=5, color="0.6", alpha=0.5, lw=0)
        g = np.linspace(x.min() - 0.2, x.max() + 0.2, 100)
        for i, form in enumerate(FORMS):
            for m, ls in (("CSQ η(TC) + eq. error", "-"), ("OLS", ":")):
                f = [q for q in F if q["scale"] == sc and q["method"] == m and q["form"] == form and q["split"] == "none"]
                if f:
                    a.plot(g, model(form, np.array(f[0]["parts"][0]["p"]), g), ls, color=io.palette.SERIES[i], lw=1.8,
                           label=f"{form}{' OLS' if m == 'OLS' else ''}")
        for j, (nm, fn) in enumerate(PUB.get(sc, {}).items()):
            a.plot(g, fn(g), "--", color=io.palette.SERIES[3 + j % 8], lw=1, label=nm)
        a.plot(g, g, color="0.2", lw=0.6)
        a.set_title(f"{sc} (n = {len(ev)}, σ_TC = {sig.get(sc, np.nan):.2f})", fontsize=10)
        a.set_xlabel(sc)
        a.set_ylabel("GCMT Mw")
        a.legend(fontsize=6.5, loc="upper left")
    for a in ax.flat[len(sc_):]:
        a.axis("off")
    fig.suptitle("How does each native scale map to GCMT Mw? Chi-square fits (solid), OLS (dotted), published (dashed)",
                 x=0.01, ha="left")
    io.savefig(fig, "t3_pairs_fits", "Native magnitude against GCMT Mw per scale with our linear / quadratic / "
               "exponential fits (chi-square with TC errors and OLS), the published relations and the 1:1 line")


def fig_resid_time(plt, store, fits, sig, MW, invy, tct):
    s = store["baseline"]
    W, R, at = s["W"], s["R"], s["attrs"]
    F = fits["baseline"]
    sc_ = [c for c in MAIN if c in W and W[c].reindex(R.gcmt.dropna().index).notna().sum() >= MIN_PAIRS][:12]
    fig, ax = plt.subplots(3, 4, figsize=(18, 11), layout="constrained", sharey=True)
    for a, sc in zip(ax.flat, sc_):
        f = choose_fit(F, sc, "CSQ η(TC) + eq. error", FORMS, ["none"])
        ev = W[sc].dropna().index.intersection(R.gcmt.dropna().index)
        y, _ = predict(f, W.loc[ev, sc].to_numpy(), ev.to_numpy(), at)
        r = R.gcmt[ev] - y
        yr = at.yr.reindex(ev)
        z = at.z.reindex(ev)
        a.scatter(yr, r, s=5, c=np.where(z > ZCUT, "#2166ac", "#e0641e"), alpha=0.5, lw=0)
        b = pd.Series(r.to_numpy()).groupby(np.floor(yr.to_numpy() / 3) * 3).median()
        a.plot(b.index + 1.5, b.values, color="0.1", lw=1.8)
        a.axhline(0, color="0.4", lw=0.6)
        a.set_ylim(-1, 1)
        a.set_title(f"{sc}: {f['form']}", fontsize=10)
    for a in ax.flat[len(sc_):]:
        a.axis("off")
    fig.suptitle("Do the conversion residuals drift in time? GCMT − converted, orange ≤ 50 km, blue > 50 km, "
                 "3-yr medians", x=0.01, ha="left")
    io.savefig(fig, "t3_residuals_time", "Residuals of the preferred unsplit chi-square fit against time per scale, "
               "by depth class")


def fig_mww(plt, store, fits, sig, MW, invy, tct):
    R = store["baseline"]["R"]
    fig, ax = plt.subplots(1, 4, figsize=(19, 5), layout="constrained")
    for a, (col, nm) in zip(ax, (("csn_raw", "CSN Mww"), ("usgs_raw", "USGS Mww"), ("gucr_raw", "CSN Mwr"),
                                 ("neicr_raw", "USGS Mwr"))):
        if col not in R:
            continue
        x = R[[col, "gcmt"]].dropna()
        a.scatter(x[col], x.gcmt - x[col], s=8, alpha=0.5, color="0.4", lw=0)
        b = np.round(x[col] * 5) / 5
        q = (x.gcmt - x[col]).groupby(b).agg(["median", "size"])
        q = q[q["size"] >= 5]
        a.plot(q.index, q["median"], "o-", color="#e0641e")
        a.axhline(0, color="0.3", lw=0.6)
        a.axvline(MREF_LOW, color="0.6", ls=":", lw=0.8)
        a.set_ylim(-0.8, 0.8)
        a.set_xlabel(nm)
        a.set_title(f"GCMT − {nm} (n = {len(x)}, median {np.median(x.gcmt - x[col]):+.2f})", fontsize=10)
    ax[0].set_ylabel("GCMT Mw − W-phase / regional Mw")
    fig.suptitle("Can W-phase Mw extend the reference below 5.4? GCMT minus CSN / USGS moment magnitudes, medians per 0.2",
                 x=0.01, ha="left")
    io.savefig(fig, "t3_mww_vs_gcmt", "GCMT Mw minus CSN and USGS Mww / Mwr against their own magnitude, with "
               "medians per 0.2 unit")


def fig_tc(plt, store, fits, sig, MW, invy, tct):
    lg = pd.concat([tct.rename(columns={k: "scale", v: "s"})[["scale", "s", "n", "rmin"]]
                    for k, v in (("a", "sa"), ("b", "sb"), ("c", "sc"))])
    lg = lg[lg.rmin > 0.5]
    st = lg.groupby("scale").s.agg(["median", lambda v: v.quantile(0.25), lambda v: v.quantile(0.75), "size"])
    st.columns = ["med", "q25", "q75", "ntri"]
    st = st.sort_values("med")
    fig, ax = plt.subplots(figsize=(10, 0.32 * len(st) + 1.5), layout="constrained")
    ax.barh(range(len(st)), st.med, xerr=[st.med - st.q25, st.q75 - st.med], color="#4393c3", ecolor="0.4")
    ax.set_yticks(range(len(st)), [f"{i} ({n} triples)" for i, n in zip(st.index, st.ntri)], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("measurement error σ (median over triples, bars 25–75 %)")
    ax.set_title("How noisy is each magnitude scale? Triple collocation over all triples with ≥ 100 shared events")
    io.savefig(fig, "t3_tc_sigma", "Triple-collocation measurement error per magnitude scale (median and IQR over "
               "triples with ≥ 100 shared events)")


def fig_dmw(plt, store, fits, sig, MW, invy, tct):
    at = store["baseline"]["attrs"]
    m = MW[MW["match"] == "baseline"].pivot_table(index="ev", columns="variant", values="mw")
    yr = at.yr.reindex(m.index)
    vs = [v for v in m.columns if v != "M0"]
    fig, ax = plt.subplots(1, len(io.PERIODS), figsize=(19, 5.5), layout="constrained", sharey=True)
    for a, (lo, hi, pn) in zip(ax, io.PERIODS):
        k = (yr >= lo) & (yr < hi) & (m.M0 >= 4.0)
        data = [(m[v] - m.M0)[k].dropna() for v in vs]
        a.boxplot(data, vert=False, showfliers=False, whis=(5, 95))
        a.set_yticks(range(1, len(vs) + 1), vs)
        a.axvline(0, color="0.4", lw=0.7)
        a.set_xlim(-0.8, 0.8)
        a.set_title(f"{pn} (M0 ≥ 4)", fontsize=10)
        a.set_xlabel("Mw − M0 Mw")
    fig.suptitle("How much does each Mw variant move the events? Δ against M0 (box 25–75 %, whiskers 5–95 %)",
                 x=0.01, ha="left")
    io.savefig(fig, "t3_dmw_variants", "Distributions of Mw differences of variants M1–M8 against M0 per period")


def fig_fmd(plt, store, fits, sig, MW, invy, tct):
    at = store["baseline"]["attrs"]
    m = MW[MW["match"] == "baseline"].pivot_table(index="ev", columns="variant", values="mw")
    yr = at.yr.reindex(m.index)
    fig, ax = plt.subplots(1, len(io.PERIODS), figsize=(20, 5.5), layout="constrained")
    g = np.arange(3.0, 9.6, 0.1)
    for a, (lo, hi, pn) in zip(ax, io.PERIODS):
        k = (yr >= lo) & (yr < hi)
        for i, v in enumerate(sorted(m.columns)):
            x = m[v][k].dropna().to_numpy()
            n = [(x >= q - 0.05).sum() for q in g]
            a.semilogy(g, np.where(np.array(n) > 0, n, np.nan), color=io.palette.SERIES[i], lw=2 if v == "M0" else 1,
                       label=v)
        a.axvline(4.5, color="0.6", ls=":", lw=0.8)
        a.set_title(pn, fontsize=11)
        a.set_xlabel("Mw")
        a.set_xlim(3.5, 9.6)
    ax[0].set_ylabel("N(≥ Mw)")
    ax[-1].legend(fontsize=8)
    fig.suptitle("Do the Mw variants change the magnitude–frequency distribution? Cumulative counts per period",
                 x=0.01, ha="left")
    io.savefig(fig, "t3_fmd_variants", "Cumulative frequency–magnitude distributions per period for M0–M8")


def fig_checks(plt, store, fits, sig, MW, invy, tct):
    s = store["baseline"]
    W, at = s["W"], s["attrs"]
    fig, ax = plt.subplots(2, 3, figsize=(18, 10), layout="constrained")
    sat = pd.read_csv(io.TAB / "t3_check_mb_saturation.csv")
    a = ax[0, 0]
    for i, (sc, x) in enumerate(sat.groupby("scale")):
        a.plot(x.mw, x.mb_minus_mw, "o-", color=io.palette.SERIES[i], label=sc, ms=4)
    g = np.linspace(3.5, 7.2, 200)
    mw = PUB["ISC mb"]["L23 exp"](g)
    a.plot(mw, g - mw, "k--", label="Lolli 2023, ISC mb")
    a.plot([5.5, 6.5], [-0.19, -0.43], "kx", ms=9)
    a.axhline(0, color="0.5", lw=0.6)
    a.set_xlabel("GCMT Mw")
    a.set_ylabel("mb − Mw (median)")
    a.set_title("Does mb saturate as Lolli et al. (2023) say?", fontsize=11)
    a.legend(fontsize=8)
    a = ax[0, 1]
    p = pd.read_csv(io.TAB / "t3_check_potin_by_year.csv")
    for i, ((c, r), x) in enumerate(p.groupby(["code", "ref"])):
        a.plot(x.year, x.diff_med, "o-", ms=3, color=io.palette.SERIES[i], label=f"{c} − {r}")
    a.axhline(0, color="0.5", lw=0.6)
    a.set_title("Are Potin magnitudes stable in time? Median difference", fontsize=11)
    a.set_xlabel("year")
    a.legend(fontsize=8)
    a = ax[0, 2]
    for i, sc in enumerate(("CSN web Ml", "CSN web Mlv")):
        if sc in W:
            v = W[sc].dropna()
            yr = at.yr.reindex(v.index)
            k = yr >= 2024
            a.scatter(yr[k], v[k], s=2, alpha=0.3, color=io.palette.SERIES[i], label=sc.replace("CSN web ", "CSN "))
    a.set_title("When does CSN switch from Ml to Mlv?", fontsize=11)
    a.set_ylabel("magnitude")
    a.legend(markerscale=5, fontsize=8)
    a = ax[1, 0]
    for i, (sc) in enumerate(("GUC ML", "ISC mb", "Potin l", "Potin c")):
        if sc in W:
            v = W[sc].dropna()
            v = v[(v >= 2.5) & (v <= 5.5)]
            h = np.bincount(np.round(v * 10).astype(int) - 25, minlength=31)
            a.step(np.arange(25, 56) / 10, h / h.sum(), where="mid", color=io.palette.SERIES[i], label=sc)
    a.set_title("Are native values heaped? Share per 0.1 bin", fontsize=11)
    a.legend(fontsize=8)
    a = ax[1, 1]
    if "GUC ML" in W:
        F = fits["baseline"]
        f = choose_fit(F, "GUC ML", "CSQ η(TC) + eq. error", ["linear"], ["none"])
        v = W["GUC ML"].dropna()
        v = v[v >= 3]
        ev = v.index.to_numpy()
        y0, _ = predict(f, v.to_numpy(), ev, at)
        y1, _ = predict(f, v.to_numpy() + np.random.default_rng(0).uniform(-0.05, 0.05, len(v)), ev, at)
        for i, (y, nm) in enumerate(((y0, "no dithering"), (y1, "dithered"))):
            h = np.bincount(np.round(y * 10).astype(int) - 30, minlength=40)[:40]
            a.step(np.arange(30, 70) / 10, h, where="mid", color=io.palette.SERIES[i], label=nm)
        a.set_yscale("log")
        a.set_title(f"Does dithering remove heaping? GUC ML → Mw (slope {f['parts'][0]['p'][1]:.2f})", fontsize=11)
        a.legend(fontsize=8)
    a = ax[1, 2]
    c = pd.read_csv(io.TAB / "t3_check_neic_ms.csv")
    for i, (sc, x) in enumerate(c.groupby("scale")):
        a.plot(range(len(x)), x.mw_minus_ms_med, "o-", color=io.palette.SERIES[i], label=f"{sc}")
        for j, (pp, n) in enumerate(zip(x.period, x.n)):
            a.annotate(f"{pp}\n{n}", (j, x.mw_minus_ms_med.iloc[j]), fontsize=6)
    a.set_title("Did NEIC Ms change in 2013? Mw − Ms (median), h ≤ 70 km", fontsize=11)
    a.legend(fontsize=8)
    fig.suptitle("Specific magnitude checks from A2", x=0.01, ha="left")
    io.savefig(fig, "t3_checks", "mb saturation against Lolli 2023; Potin codes against ISC / GUC in time; CSN Ml→Mlv "
               "switch; heaping of native values and the effect of dithering; NEIC Ms before / after 2013")


if __name__ == "__main__":
    run()

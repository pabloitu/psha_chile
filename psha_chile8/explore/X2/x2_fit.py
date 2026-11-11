"""X2: Mw conversions that allow for the incomplete reference (inverse and truncated regression), chosen by
time-block cross-validation, and the Mw catalogue variants built from them."""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "X1"))
import x1_mag as xm  # noqa: E402

CACHE, TAB = HERE / "cache", HERE / "tables"
TAB.mkdir(exist_ok=True)

# settings
SEED = 1
MIN_PAIRS = 30
MIN_SIDE = 20
NFOLD = 5
KNOTS = np.round(np.arange(4.6, 6.61, 0.1), 1)
KREF = 5.5
B_SAT = 0.3
S_MAX = 1.0
SY = {"G": 0.08, "W": 0.10}
GC = [(1900, 1990, 5.6), (1990, 2004, 5.4), (2004, 2015, 5.3), (2015, 2100, 5.2)]
WFAM = ["NEIC Mww", "CSN Mww", "GUC Mwr", "CSN web Mw", "NEIC Mwr", "GFZ Mw"]
DIRECT = ["GCMT Mw", "ISC-GEM Mw", "NEIC Mww", "CSN Mww"]
ZCUT = 50.0


# data
def load():
    L = pd.read_csv(CACHE / "L.csv.gz", low_memory=False)
    a = pd.read_csv(CACHE / "attrs.csv.gz", index_col=0)
    R = pd.read_csv(CACHE / "refs.csv.gz", index_col=0)
    W = L.pivot_table(index="ev", columns="scale", values="mag", aggfunc="first").reindex(a.index)
    R = R.reindex(a.index)
    return L, W, R, a


def wref(W):
    """Composite regional/W-phase Mw on the NEIC Mww scale: members shifted by their median offset to NEIC Mww
    (pairs with mean ≥ 5); GCMT where no member exists."""
    off, y = {}, pd.Series(np.nan, index=W.index)
    for c in WFAM:
        if c not in W:
            continue
        x = W[["NEIC Mww", c]].dropna()
        x = x[(x.sum(axis=1) / 2) >= 5.0]
        off[c] = 0.0 if c == "NEIC Mww" else float(np.median(x["NEIC Mww"] - x[c])) if len(x) >= 20 else 0.0
        y = y.fillna(W[c] + off[c])
    return y.fillna(W["GCMT Mw"]), off


# relations: piecewise linear with one knot (k); linear when b1 = b2
def pl(p, v):
    a, b1, b2, k = p
    return a + np.where(v < k, b1, b2) * (v - k)


def fit_inv(y, x, sy, form):
    """
    Native magnitude on reference Mw, x = g(y), by least squares; slopes corrected for the error of y.
    Unbiased when the pairs are selected on y (an incomplete reference), unlike Mw-on-native regression.

    Returns
    -------
    p = (a, b1, b2, k) of g, residual sd of x
    """
    lam = max(1 - sy ** 2 / max(np.var(y), 1e-6), 0.5)
    best = None
    ks = [KREF] if form == "linear" else [k for k in KNOTS if (y < k).sum() >= MIN_SIDE and (y >= k).sum() >= MIN_SIDE]
    for k in ks:
        A = np.c_[np.ones_like(y), np.minimum(y - k, 0), np.maximum(y - k, 0)] if form != "linear" else \
            np.c_[np.ones_like(y), y - k]
        c = np.linalg.lstsq(A, x, rcond=None)[0]
        r = x - A @ c
        sse = float(r @ r)
        if best is None or sse < best[0]:
            best = (sse, k, c)
    if best is None:
        return None
    _, k, c = best
    b1, b2 = (c[1], c[1]) if form == "linear" else (c[1], c[2])
    b1, b2 = b1 / lam, b2 / lam
    A = np.where(y < k, b1, b2) * (y - k)
    a = float(np.mean(x - A))
    p = (a, b1, b2, k)
    return {"p": [float(v) for v in p], "s": float(np.std(x - pl(p, y))), "n": len(y)}


def conv_inv(f, x):
    """Mw from native x by inverting g; sd = residual sd of x over the local slope (capped)."""
    a, b1, b2, k = f["p"]
    b = np.where(x < a, b1, max(b2, B_SAT))
    y = k + (x - a) / b
    s = np.minimum(f["s"] / b, S_MAX)
    return y, s


def fit_trunc(x, y, c, form):
    """
    Mw on native, y = f(x) + e, e ~ N(0, s), with the likelihood truncated at the reference completeness c
    (pairs with y < c dropped). Gives the conditional mean of Mw, corrected for the selection on y.
    """
    k0 = y >= c
    x, y, c = x[k0], y[k0], c[k0]
    if len(x) < MIN_PAIRS:
        return None
    ks = [KREF] if form == "linear" else [k for k in np.round(np.arange(3.8, 6.61, 0.2), 1)
                                           if (x < k).sum() >= MIN_SIDE and (x >= k).sum() >= MIN_SIDE]
    best = None
    for k in ks:
        def nll(q):
            a, b1, b2, ls = q
            if form == "linear":
                b2 = b1
            f = a + np.where(x < k, b1, b2) * (x - k)
            s = np.exp(ls)
            return -np.sum(norm.logpdf(y, f, s) - norm.logsf(c, f, s))
        b, a = np.polyfit(x, y, 1)
        q0 = [a + b * k, b, b, np.log(0.25)]
        r = minimize(nll, q0, method="L-BFGS-B", bounds=[(2, 9), (0.05, 3), (0.05, 3), (np.log(0.03), np.log(1.5))])
        if best is None or r.fun < best[0]:
            best = (r.fun, k, r.x)
    if best is None:
        return None
    v, k, q = best
    b2 = q[1] if form == "linear" else q[2]
    return {"p": [float(q[0]), float(q[1]), float(b2), float(k)], "s": float(np.exp(q[3])), "n": int(len(x)),
            "nll": float(v)}


def conv_trunc(f, x):
    return pl(f["p"], x), np.full(len(x), f["s"])


def trunc_nll(f, x, y, c):
    k = y >= c
    m = pl(f["p"], x[k])
    return -(norm.logpdf(y[k], m, f["s"]) - norm.logsf(c[k], m, f["s"]))


# cross-validation by time blocks
def folds(yr):
    o = np.argsort(yr, kind="stable")
    g = np.empty(len(yr), int)
    g[o] = np.arange(len(yr)) * NFOLD // len(yr)
    return g


def cv(method, x, y, yr, z, sy, c, form, split):
    """Holdout loss per pair (squared x residual for 'inv', negative log-likelihood for 'trunc')."""
    fo = folds(yr)
    out = np.full(len(x), np.nan)
    grp = np.where(np.isfinite(z) & (z > ZCUT), 1, 0) if split == "depth" else np.zeros(len(x), int)
    for i in range(NFOLD):
        tr, te = fo != i, fo == i
        for g in np.unique(grp):
            a, b = tr & (grp == g), te & (grp == g)
            if a.sum() < MIN_PAIRS or not b.any():
                return None
            if method == "inv":
                f = fit_inv(y[a], x[a], sy, form)
                if f is None:
                    return None
                out[b] = (x[b] - pl(f["p"], y[b])) ** 2
            else:
                f = fit_trunc(x[a], y[a], c[a], form)
                if f is None:
                    return None
                kk = b & (y >= c)
                out[kk] = trunc_nll(f, x[kk], y[kk], c[kk])
    return out[np.isfinite(out)] if np.isfinite(out).any() else None


def select(method, x, y, yr, z, sy, c):
    """Simplest model whose CV loss is within one standard error of the best."""
    cand = [("linear", "none"), ("hinge", "none"), ("linear", "depth"), ("hinge", "depth")]
    res = {}
    for form, split in cand:
        try:
            v = cv(method, x, y, yr, z, sy, c, form, split)
        except Exception:  # noqa: BLE001
            v = None
        if v is not None and len(v) > 10:
            res[(form, split)] = v
    if not res:
        return None, {}
    mean = {k: float(np.mean(v)) for k, v in res.items()}
    kb = min(mean, key=mean.get)
    ref = res[kb]
    for k in cand:
        if k not in res:
            continue
        if len(res[k]) == len(ref):
            d = res[k] - ref
            if np.mean(d) <= np.std(d) / np.sqrt(len(d)):
                return k, mean
        elif k == kb:
            return k, mean
    return kb, mean


def fit_scale(method, sc, x, y, yr, z, sy, c):
    sel, cvm = select(method, x, y, yr, z, sy, c)
    if sel is None:
        return None
    form, split = sel
    grp = np.where(np.isfinite(z) & (z > ZCUT), "deep", "shallow") if split == "depth" else np.full(len(x), "all")
    parts = {}
    for g in np.unique(grp):
        k = grp == g
        f = fit_inv(y[k], x[k], sy, form) if method == "inv" else fit_trunc(x[k], y[k], c[k], form)
        if f is None:
            return None
        f.update({"xmin": float(x[k].min()), "xmax": float(x[k].max()), "ymin": float(y[k].min()),
                  "ymax": float(y[k].max())})
        parts[g] = f
    return {"scale": sc, "method": method, "form": form, "split": split, "parts": parts,
            "cv": {f"{a} | {b}": v for (a, b), v in cvm.items()}, "n": int(len(x))}


def completeness(yr):
    c = np.full(len(yr), np.nan)
    for y0, y1, v in GC:
        c[(yr >= y0) & (yr < y1)] = v
    return c


def fit_all(W, R, a, ref, method):
    y_ref = W["GCMT Mw"] if ref == "G" else wref(W)[0]
    skip = set(DIRECT) | (set(WFAM) if ref == "W" else set())
    scales = [s for s in W.columns if s not in skip and not s.startswith(("Potin ", "Cent "))]
    out = []
    for sc in scales:
        k = W[sc].notna() & y_ref.notna() & a.yr.notna()
        if k.sum() < MIN_PAIRS * 2:
            continue
        x, y = W.loc[k, sc].to_numpy(float), y_ref[k].to_numpy(float)
        yr, z = a.yr[k].to_numpy(float), a.z[k].to_numpy(float)
        c = completeness(yr) if method == "trunc" else np.zeros(len(x))
        if method == "trunc" and (y >= c).sum() < MIN_PAIRS * 2:
            continue
        f = fit_scale(method, sc, x, y, yr, z, SY[ref], c)
        if f is not None:
            f["ref"] = ref
            out.append(f)
    return out


# catalogue
def convert(f, x, z):
    y, s = np.full(len(x), np.nan), np.full(len(x), np.nan)
    grp = np.where(np.isfinite(z) & (z > ZCUT), "deep", "shallow") if f["split"] == "depth" else np.full(len(x), "all")
    for g in np.unique(grp):
        k = grp == g
        p = f["parts"].get(g) or next(iter(f["parts"].values()))
        y[k], s[k] = (conv_inv if f["method"] == "inv" else conv_trunc)(p, x[k])
        lo, hi = (p["xmin"], p["xmax"])
        s[k] = s[k] + 0.1 * (np.clip(lo - x[k], 0, None) + np.clip(x[k] - hi, 0, None))
    return y, s


def build(F, W, R, a, L, direct="G", combine="best", proxy_only=False):
    """
    One Mw per event. Direct Mw by the X1 hierarchy (RM18 > GCMT > CSN Mww > USGS Mww), or with direct="W" the
    regional/W-phase family first and GCMT last; before 1976 ISC-GEM > Centennial; else proxies converted by F,
    the smallest-sd one ('best') or their inverse-variance mean ('wmean').
    """
    rng = np.random.default_rng(SEED)
    n = len(a)
    z = a.z.to_numpy(float)
    mw, sg, how = np.full(n, np.nan), np.full(n, np.nan), np.full(n, None, object)
    Y, S, names = [], [], []
    for f in F:
        if f["scale"] not in W:
            continue
        x = W[f["scale"]].to_numpy(float)
        k = np.isfinite(x)
        if not k.any():
            continue
        x = x + rng.uniform(-0.05, 0.05, n)
        y, s = np.full(n, np.nan), np.full(n, np.nan)
        y[k], s[k] = convert(f, x[k], z[k])
        Y.append(y)
        S.append(s)
        names.append(f["scale"])
    if Y:
        Y, S = np.vstack(Y), np.vstack(S)
        fin = np.isfinite(Y) & np.isfinite(S)
        if combine == "wmean":
            w = np.where(fin, 1 / np.where(fin, S, 1) ** 2, 0)
            sw = w.sum(axis=0)
            k = sw > 0
            mw[k] = (np.where(fin, Y, 0) * w).sum(axis=0)[k] / sw[k]
            sg[k] = 1 / np.sqrt(sw[k])
            how[k] = "weighted proxies"
        else:
            j = np.argmin(np.where(fin, S, np.inf), axis=0)
            k = fin.any(axis=0)
            mw[k] = Y[j, np.arange(n)][k]
            sg[k] = S[j, np.arange(n)][k]
            how[k] = np.array(names)[j[k]]
    if proxy_only:
        return pd.DataFrame({"ev": a.index, "mw": mw, "sig": sg, "how": how})
    old = a.yr.to_numpy() < 1976
    cent = L[L.scale.str.startswith("Cent ")].pivot_table(index="ev", columns="scale", values="mag", aggfunc="first")
    cm = np.full(n, np.nan)
    for c in cent.columns:
        v = cent[c].reindex(a.index).to_numpy(float)
        if c.endswith((" Mw", " mB")):
            cv = v
        elif c.endswith((" Ms", " UK")):
            cv = xm.PUB["ISC MS"]["DG15 exp"](v - (0.2 if c.endswith(" UK") else 0.0))
        else:
            continue
        cm = np.where(np.isnan(cm) & np.isfinite(cv), cv, cm)
    gem = W["ISC-GEM Mw"].to_numpy(float)
    for nm, v, s in (("Centennial", cm, 0.25), ("ISC-GEM", gem, 0.2)):
        k = old & np.isfinite(v)
        mw[k], sg[k], how[k] = v[k], s, nm
    if direct == "G":
        seq = [("USGS Mww", R.usgs, 0.08), ("CSN Mww", R.csn, 0.08), ("GCMT", R.gcmt, 0.07)]
    else:
        wr, off = wref(W)
        seq = [("GCMT", R.gcmt, 0.07)] + [(c, W[c] + off.get(c, 0.0), 0.10) for c in WFAM[::-1] if c in W]
    for nm, v, s in seq:
        v = v.to_numpy(float)
        k = np.isfinite(v)
        mw[k], sg[k], how[k] = v[k], s, nm
    v = R.rm.to_numpy(float)
    k = np.isfinite(v)
    mw[k], sg[k], how[k] = v[k], 0.2, "RM18"
    return pd.DataFrame({"ev": a.index, "mw": mw, "sig": sg, "how": how})


VARIANTS = {
    "INV-G": ("inv", "G", "G", "best"),
    "INV-G mean": ("inv", "G", "G", "wmean"),
    "INV-W": ("inv", "W", "W", "best"),
    "INV-W mean": ("inv", "W", "W", "wmean"),
    "TRUNC-G": ("trunc", "G", "G", "best"),
    "INV-G linear": ("inv-lin", "G", "G", "best"),
    "INV-W linear": ("inv-lin", "W", "W", "best"),
    "INV-W linear mean": ("inv-lin", "W", "W", "wmean"),
}


def run():
    T0 = time.time()
    L, W, R, a = load()
    _, off = wref(W)
    json.dump(off, open(TAB / "x2_wref_offsets.json", "w"), indent=1)
    fits = {}
    fp = CACHE / "fits_x2.json"
    if fp.exists():
        fits = json.load(open(fp))
    for key in ("inv G", "inv W", "trunc G"):
        if key not in fits:
            m, r = key.split()
            fits[key] = fit_all(W, R, a, r, m)
            json.dump(fits, open(fp, "w"), default=float)
            print("fits", key, len(fits[key]), round(time.time() - T0), flush=True)
    for r in ("G", "W"):
        if f"inv-lin {r}" in fits:
            continue
        F = []
        y_ref = W["GCMT Mw"] if r == "G" else wref(W)[0]
        for f in fits[f"inv {r}"]:
            sc = f["scale"]
            k = W[sc].notna() & y_ref.notna()
            x, y = W.loc[k, sc].to_numpy(float), y_ref[k].to_numpy(float)
            g = fit_inv(y, x, SY[r], "linear")
            g.update({"xmin": float(x.min()), "xmax": float(x.max()), "ymin": float(y.min()), "ymax": float(y.max())})
            F.append({"scale": sc, "method": "inv", "form": "linear", "split": "none", "parts": {"all": g}, "ref": r,
                      "n": int(len(x))})
        fits[f"inv-lin {r}"] = F
        json.dump(fits, open(fp, "w"), default=float)
    tab = []
    for key, F in fits.items():
        for f in F:
            for g, p in f["parts"].items():
                tab.append({"fit": key, "scale": f["scale"], "form": f["form"], "split": f["split"], "group": g,
                            "n": p["n"], "a": p["p"][0], "b1": p["p"][1], "b2": p["p"][2], "knot": p["p"][3],
                            "s": p["s"], "xmin": p["xmin"], "xmax": p["xmax"]})
    pd.DataFrame(tab).to_csv(TAB / "x2_fits.csv", index=False)
    out = []
    for nm, (m, r, d, comb) in VARIANTS.items():
        out.append(build(fits[f"{m} {r}"], W, R, a, L, d, comb).assign(variant=nm))
        print("built", nm, round(time.time() - T0), flush=True)
    x1 = pd.read_csv(HERE.parent / "X1" / "cache" / "mw_variants.csv.gz")
    x1 = x1[x1["match"] == "baseline"]
    for v, nm in (("M0", "X1 M0"), ("M2", "X1 M2 linear"), ("M6", "X1 M6"), ("M7", "Cabello")):
        out.append(x1[x1.variant == v][["ev", "mw", "sig", "how"]].assign(variant=nm))
    pd.concat(out, ignore_index=True).to_csv(CACHE / "mw_x2.csv.gz", index=False)
    print("done", round(time.time() - T0), flush=True)


if __name__ == "__main__":
    run()

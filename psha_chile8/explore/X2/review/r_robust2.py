"""Catalogue-level robustness: alternative X2 variants scored with the X2 checks."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
X2 = HERE.parent
sys.path.insert(0, str(X2))
import x2_eval as xe  # noqa: E402
import x2_fit as xf  # noqa: E402

OUT = HERE / "tables"
pd.set_option("display.width", 220)
MS = ("ISC MS", "BJI Ms", "BJI MS", "BJI Ms7", "BJI Msz", "MOS MS", "MOS Ms", "NEIC MS", "NEIC MSZ", "NEIC Ms_20",
      "LDG Ms", "PEK MS")


def refit(W, a, sub, sy=0.10):
    y_ref = xf.wref(W)[0]
    F = []
    for f in json.load(open(X2 / "cache" / "fits_x2.json"))["inv-lin W"]:
        sc = f["scale"]
        k = W[sc].notna() & y_ref.notna()
        x, y = W.loc[k, sc].to_numpy(float), y_ref[k].to_numpy(float)
        c = xf.completeness(a.yr[k].to_numpy(float))
        kk = {"all": np.ones(len(x), bool), "cap": y < 6.2, "window": (y >= c + 0.1) & (y < 6.2)}[sub]
        if kk.sum() < 60:
            kk = np.ones(len(x), bool)
        g = xf.fit_inv(y[kk], x[kk], sy, "linear")
        g.update({"xmin": float(x[kk].min()), "xmax": float(x[kk].max()), "ymin": float(y[kk].min()),
                  "ymax": float(y[kk].max())})
        F.append({"scale": sc, "method": "inv", "form": "linear", "split": "none", "parts": {"all": g}, "ref": "W"})
    return F


def gcmt_to_w(W, R):
    """GCMT on the W scale: median W − GCMT per GCMT bin, applied below 5.4."""
    y = xf.wref(W.drop(columns="GCMT Mw").assign(**{"GCMT Mw": np.nan}))[0]
    g = R.gcmt
    d = (y - g).dropna()
    out = g.copy()
    rows = []
    for lo, hi in ((4.0, 4.8), (4.8, 5.0), (5.0, 5.2), (5.2, 5.4)):
        k = (g[d.index] >= lo) & (g[d.index] < hi)
        v = float(d[k].median()) if k.sum() >= 15 else 0.0
        rows.append((lo, hi, round(v, 3), int(k.sum())))
        kk = (g >= lo) & (g < hi)
        out[kk] = g[kk] + v
    print("GCMT → W offsets by GCMT bin (lo, hi, offset, n):", rows)
    return out


def score(name, mv, a):
    B, Lg, Rt = xe.stats([(name, mv, a)])
    r = {"variant": name}
    for decl in (False, True):
        g = Lg[(Lg.declust == decl) & (Lg.family == "all") & (Lg.period == "1976–2026")]
        for lo in (5.0, 5.3):
            q = g[g.fit_from == lo].iloc[0]
            r[f"N7 {'decl' if decl else 'full'} {lo}"] = q.N7_pred / q.N7_obs
    b = B[B.declust & (B.family == "all") & (B.period == "2011–2026")].set_index("floor").b
    r["b range decl"] = b.loc[4.7:5.8].max() - b.loc[4.7:5.8].min()
    q = Rt[Rt.declust & (Rt.M == 5.0)].iloc[0][[c for c in Rt.columns if "–" in c]].astype(float)
    r["rate5 cv"] = q.std() / q.mean()
    for c in q.index:
        r[f"r5 {c}"] = q[c]
    fams = {}
    for fam in ("interface band", "in slab", "crustal shallow"):
        q = Lg[(~Lg.declust) & (Lg.family == fam) & (Lg.period == "1976–2026") & (Lg.fit_from == 5.0)]
        if len(q):
            fams[fam] = f"{q.N7_pred.iloc[0]:.1f}/{q.N7_obs.iloc[0]}"
    r["fam N7"] = fams
    return r


if __name__ == "__main__":
    L, W, R, a = xf.load()
    fits = json.load(open(X2 / "cache" / "fits_x2.json"))
    Fw = fits["inv-lin W"]
    base = xf.build(Fw, W, R, a, L, "W", "wmean")
    V = {"INV-W linear mean (recommended)": base,
         "W fits, GCMT-first direct": xf.build(Fw, W, R, a, L, "G", "wmean"),
         "W fits, GCMT on W scale, W first": xf.build(Fw, W, R.assign(gcmt=gcmt_to_w(W, R)), a, L, "W", "wmean"),
         "W fits capped y < 6.2": xf.build(refit(W, a, "cap"), W, R, a, L, "W", "wmean"),
         "W fits in the jointly complete window": xf.build(refit(W, a, "window"), W, R, a, L, "W", "wmean"),
         "W fits, no lambda correction": xf.build(refit(W, a, "all", 0.0), W, R, a, L, "W", "wmean"),
         "W fits, lambda with sy 0.15": xf.build(refit(W, a, "all", 0.15), W, R, a, L, "W", "wmean")}
    Wm = W.copy()
    for c in MS:
        if c in Wm:
            Wm.loc[Wm[c] < 5.0, c] = np.nan
    V["no MS proxies below MS 5.0"] = xf.build(Fw, Wm, R, a, L, "W", "wmean")
    rows, shift = [], []
    m0 = base.mw.to_numpy()
    for nm, d in V.items():
        rows.append(score(nm, d.mw.to_numpy(), a))
        mv = d.mw.to_numpy()
        r = {"variant": nm}
        for lo in (4.5, 5.0, 5.5):
            k = (m0 >= lo) & (m0 < lo + 0.5) & (a.yr.to_numpy() >= 1976)
            r[f"mean ΔMw {lo}–{lo + 0.5}"] = float(np.nanmean(mv[k] - m0[k]))
        shift.append(r)
        print("done", nm, flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "H_variants.csv", index=False)
    print(t.round(3).drop(columns="fam N7").to_string())
    print(t[["variant", "fam N7"]].to_string())
    s = pd.DataFrame(shift).round(3)
    s.to_csv(OUT / "H_shift.csv", index=False)
    print(s.to_string())

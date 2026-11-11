"""Robustness checks of the X2 homogenization (review of 2026-11-11)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
X2 = HERE.parent
sys.path.insert(0, str(X2))
import x2_fit as xf  # noqa: E402

OUT = HERE / "tables"
OUT.mkdir(exist_ok=True)
SC = ["ISC mb", "NEIC mb", "VAO mb", "MOS mb", "BJI mB", "ISC MS", "GUC ML", "SJA ML"]
pd.set_option("display.width", 220)


def mw_at(f, v):
    return xf.conv_inv(f, np.asarray(v, float))[0]


# A synthetic: is the lambda slope correction right under a GR prior?
def synth():
    rows = []
    rng = np.random.default_rng(0)
    for sel in ("obs", "true"):
        for sy in (0.08, 0.10, 0.15):
            for rep in range(20):
                n = 60000
                m = 3.5 + rng.exponential(1 / np.log(10), n)
                y = m + rng.normal(0, sy, n)
                x = 0.5 + 0.9 * m + rng.normal(0, 0.2, n)
                q = y if sel == "obs" else m
                k = rng.random(n) < 1 / (1 + np.exp(-(q - 5.3) / 0.12))
                k &= m < 6.5
                for c in (0.0, sy):
                    f = xf.fit_inv(y[k], x[k], c, "linear")
                    rows.append({"selection": sel, "sy": sy, "corr": c > 0, "slope": f["p"][1],
                                 "Mw@x4.5": mw_at(f, [4.5])[0] - (4.5 - 0.5) / 0.9})
    t = pd.DataFrame(rows).groupby(["selection", "sy", "corr"]).mean().round(3)
    t.to_csv(OUT / "A_lambda_synthetic.csv")
    print("A: true slope 0.9; Mw@x4.5 is the bias of the converted Mw at native 4.5\n", t)


# B real: refit with the pairs restricted to where both members are complete
def restrict(W, a):
    rows = []
    for ref in ("G", "W"):
        y_ref = W["GCMT Mw"] if ref == "G" else xf.wref(W)[0]
        for sc in SC:
            k = W[sc].notna() & y_ref.notna()
            x, y, yr = W.loc[k, sc].to_numpy(float), y_ref[k].to_numpy(float), a.yr[k].to_numpy(float)
            c = xf.completeness(yr)
            for nm, kk in (("all pairs", np.ones(len(x), bool)), ("y < 6.2", y < 6.2),
                           ("y >= Mc(GCMT)+0.1", y >= c + 0.1), ("Mc+0.1 <= y < 6.2", (y >= c + 0.1) & (y < 6.2))):
                if kk.sum() < 60:
                    continue
                for sy in (0.0, xf.SY[ref]):
                    f = xf.fit_inv(y[kk], x[kk], sy, "linear")
                    v = mw_at(f, [4.0, 4.5, 5.0, 5.5])
                    rows.append({"ref": ref, "scale": sc, "subset": nm, "sy": sy, "n": int(kk.sum()),
                                 "slope": f["p"][1], "Mw@4.0": v[0], "Mw@4.5": v[1], "Mw@5.0": v[2], "Mw@5.5": v[3]})
    t = pd.DataFrame(rows).round(3)
    t.to_csv(OUT / "B_restricted.csv", index=False)
    print("B\n", t[t.sy > 0].to_string())


# C coverage: is the native scale missing at low reference Mw (selection on x)?
def coverage(W):
    y = xf.wref(W)[0]
    bins = np.arange(3.5, 7.01, 0.5)
    rows = []
    for sc in SC:
        r = {"scale": sc}
        for lo in bins[:-1]:
            k = (y >= lo) & (y < lo + 0.5)
            r[f"{lo}"] = round(float(W.loc[k, sc].notna().mean()), 2) if k.sum() >= 30 else np.nan
        rows.append(r)
    gl = W["GUC ML"]
    reg = W[["GUC Mwr", "CSN web Mw", "CSN Mww", "NEIC Mww"]].notna().any(axis=1)
    r = {"scale": "share of GUC ML events with a W member, by ML"}
    for lo in bins[:-1]:
        k = (gl >= lo) & (gl < lo + 0.5)
        r[f"{lo}"] = round(float(reg[k].mean()), 2) if k.sum() >= 30 else np.nan
    rows.append(r)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "C_coverage.csv", index=False)
    print("C: share of events in each W-composite Mw bin that have the native scale\n", t.to_string())


# D bootstrap of the linear W relations
def boot(W, nb=300):
    y_ref = xf.wref(W)[0]
    rng = np.random.default_rng(3)
    rows = []
    for sc in SC:
        k = W[sc].notna() & y_ref.notna()
        x, y = W.loc[k, sc].to_numpy(float), y_ref[k].to_numpy(float)
        v = []
        for _ in range(nb):
            i = rng.integers(0, len(x), len(x))
            v.append(mw_at(xf.fit_inv(y[i], x[i], 0.10, "linear"), [4.5, 5.0]))
        v = np.array(v)
        rows.append({"scale": sc, "n": len(x), "Mw@4.5 sd": v[:, 0].std(), "Mw@5.0 sd": v[:, 1].std()})
    t = pd.DataFrame(rows).round(3)
    t.to_csv(OUT / "D_bootstrap.csv", index=False)
    print("D\n", t.to_string())


# E drift of the native scale at fixed Mw (inverse residuals, Mw bins where GCMT is complete)
def drift(W, a):
    y = W["GCMT Mw"].fillna(xf.wref(W)[0])
    rows = []
    for sc in ["ISC mb", "NEIC mb", "ISC MS", "GUC ML"]:
        for lo in (5.0, 5.6, 6.0):
            r = {"scale": sc, "Mw bin": f"{lo}–{lo + 0.4}"}
            for y0, y1 in ((1976, 1990), (1990, 2000), (2000, 2011), (2011, 2027)):
                k = W[sc].notna() & (y >= lo) & (y < lo + 0.4) & (a.yr >= y0) & (a.yr < y1)
                r[f"{y0}–{y1 - 1}"] = f"{(W.loc[k, sc] - y[k]).median():+.2f} ({k.sum()})" if k.sum() >= 15 else ""
            rows.append(r)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "E_drift.csv", index=False)
    print("E: median native − Mw at fixed Mw, by period (n)\n", t.to_string())


# F offsets of the W members and GCMT to NEIC Mww by magnitude
def offsets(W):
    bins = [(4.0, 4.5), (4.5, 5.0), (5.0, 5.4), (5.4, 5.8), (5.8, 6.5), (6.5, 9.5)]
    rows = []
    for c in ["GCMT Mw", "CSN Mww", "GUC Mwr", "CSN web Mw", "NEIC Mwr", "GFZ Mw"]:
        x = W[["NEIC Mww", c]].dropna()
        mm = x.mean(axis=1)
        r = {"member": c}
        for lo, hi in bins:
            k = (mm >= lo) & (mm < hi)
            r[f"{lo}–{hi}"] = f"{(x[c] - x['NEIC Mww'])[k].median():+.2f} ({k.sum()})" if k.sum() >= 15 else ""
        rows.append(r)
    x = W[["GCMT Mw", "GUC Mwr"]].dropna()
    mm = x.mean(axis=1)
    r = {"member": "GCMT − GUC Mwr"}
    for lo, hi in bins:
        k = (mm >= lo) & (mm < hi)
        r[f"{lo}–{hi}"] = f"{(x['GCMT Mw'] - x['GUC Mwr'])[k].median():+.2f} ({k.sum()})" if k.sum() >= 15 else ""
    rows.append(r)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "F_offsets.csv", index=False)
    print("F: member − NEIC Mww, median (n), by mean magnitude\n", t.to_string())


# G correlation of conversion errors between proxies (is the inverse-variance mean over-confident?)
def corr(W, a, fits):
    y = xf.wref(W)[0]
    F = {f["scale"]: f for f in fits["inv-lin W"]}
    R = {}
    for sc in ["ISC mb", "NEIC mb", "VAO mb", "MOS mb", "BJI mB", "ISC MS", "GUC ML"]:
        x = W[sc].to_numpy(float)
        k = np.isfinite(x)
        v = np.full(len(x), np.nan)
        v[k] = xf.convert(F[sc], x[k], a.z.to_numpy(float)[k])[0]
        R[sc] = pd.Series(v, index=W.index) - y
    R = pd.DataFrame(R)
    R = R[(y >= 4.5) & (y < 6.0)]
    c = R.corr(min_periods=100).round(2)
    c.to_csv(OUT / "G_resid_corr.csv")
    print("G: correlation of converted − W Mw residuals, 4.5 ≤ Mw < 6\n", c.to_string())
    print("residual sd", R.std().round(3).to_dict())
    sig = {f["scale"]: f["parts"]["all"]["s"] / f["parts"]["all"]["p"][1] for f in fits["inv-lin W"]}
    print("claimed sd", {k: round(sig[k], 3) for k in R.columns})
    k = R[["ISC mb", "NEIC mb", "VAO mb", "MOS mb"]].dropna()
    s = np.array([sig[c] for c in k.columns])
    w = 1 / s ** 2
    mean = (k * w).sum(axis=1) / w.sum()
    print("4-mb mean: claimed sd", round(1 / np.sqrt(w.sum()), 3), "actual sd of residual", round(mean.std(), 3),
          "n", len(k))


if __name__ == "__main__":
    L, W, R, a = xf.load()
    fits = json.load(open(X2 / "cache" / "fits_x2.json"))
    synth()
    restrict(W, a)
    coverage(W)
    boot(W)
    drift(W, a)
    offsets(W)
    corr(W, a, fits)

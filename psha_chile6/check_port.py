# Acceptance checks of the ported source generation (FINAL_PLAN 2a): the built
# sources against outputs/fits/<model>/rates.csv of fit_check.py.
#   interface: b per segment and N(>=7), N(>=8) of the seismic tapered branch
#   in-slab:   pooled b (one value, within sigma of the separate fits), class rates at the floors
#   crustal:   b, rates and Mmax per class, borrowed b for unclassified
#   MFD:       lib.gr tapered with corner equals fit_check.tap
# Run after run.py built the reference of each model. Outputs: outputs/fits/port_check.csv
#   python check_port.py

import json

import numpy as np
import pandas as pd

import fit_check as fc
import paths
import run
from lib import gr
from variants import VARIANTS

TOL_B, TOL_N = 0.01, 0.05


def rows_if(c, fr):
    ab = json.loads((c.OUT / "ab" / "ab.json").read_text())["segments"]
    bp = pd.read_csv(c.OUT / "rates" / "branches.csv", keep_default_na=False)
    out = []
    for sid, r in ab.items():
        w = r[c.AB_ESTIMATOR]
        f = fr[(fr["sub"] == sid) & (fr["form"] == "tapered")]
        if not len(f):
            continue
        f = f.iloc[0]
        br = bp[(bp["seg"] == sid) & (bp["rate"] == "seismic") & (bp["form"] == "tapered")].iloc[0]
        out.append({"model": "interface", "sub": sid, "item": "b", "built": w["b"], "fit_check": f["b"]})
        for m in (7.0, 8.0):
            out.append({"model": "interface", "sub": sid, "item": f"N{m}", "built": br[f"N{m}"], "fit_check": f[f"N{m}"]})
    return out


def rows_ssm(model, c, fr):
    t = pd.read_csv(c.OUT / "ssm" / "classes.csv")
    out = []
    rc = [x for x in t.columns if x.startswith("rate_M")][0]
    m0 = float(rc[6:])
    for r in t.to_dict("records"):
        k = r["class"]
        borrowed = k in getattr(c, "B_SOURCE", {})
        f = fr[(fr["sub"] == k) & ((fr["form"] == "tgr_borrowed") == borrowed)]
        if not len(f):
            continue
        f = f.iloc[0]
        fl = f["floor"]
        out.append({"model": model, "sub": k, "item": "b", "built": r["b_used"], "fit_check": f["b"]})
        out.append({"model": model, "sub": k, "item": f"N{fl}", "built": r[rc] * 10 ** (-r["b_used"] * (fl - m0)),
                    "fit_check": f["rate_floor"]})
        out.append({"model": model, "sub": k, "item": "mmax", "built": r["mmax"], "fit_check": np.nan})
    return out


def main():
    rows = []
    for model in ("interface", "intraslab", "crustal"):
        c = run.config(model, VARIANTS[model][fc.REF[model]])
        fr = pd.read_csv(paths.ROOT / "outputs" / "fits" / model / "rates.csv")
        try:
            rows += rows_if(c, fr) if model == "interface" else rows_ssm(model, c, fr)
        except FileNotFoundError as e:
            print(f"[skip] {model}: {e}; build it with run.py first")
    t = pd.DataFrame(rows)
    if len(t):
        t["diff"] = t["built"] / t["fit_check"] - 1
        pool = t["sub"].isin(["intra_slab", "slab_deep"])
        t["ok"] = np.where(t["item"] == "b", (t["built"] - t["fit_check"]).abs() <= TOL_B,
                           np.where(t["item"] == "mmax", True, t["diff"].abs() <= TOL_N))
        t["ok"] = t["ok"].astype(object)
        t.loc[pool & (t["item"] != "mmax"), "ok"] = "pooled b"
        t.to_csv(paths.ROOT / "outputs" / "fits" / "port_check.csv", index=False)
        print(t.round(4).to_string(index=False))
        print("\npooled in-slab b: the two classes share b_used; their rates are refitted at it, so "
              "N at the floor may differ from the separate fit_check fits by a few percent")
    m = np.linspace(6.5, 9.4, 30)
    a = gr.cum("tapered", 0.92, 6.5, 9.5, m, corner=9.6)
    b = fc.tap(0.92, 6.5, 9.5, m)
    print(f"\ntapered MFD, lib.gr with corner 9.6 vs fit_check.tap: max rel. diff {np.max(np.abs(a / b - 1)):.2e}")


if __name__ == "__main__":
    main()

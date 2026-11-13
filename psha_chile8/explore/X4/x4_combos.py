"""X4, second part: the two published rules for the surface-wave scales and the ways of putting GCMT on the
scale of the W family, in every combination, with the six agencies of A5.

Scores as in x4_surface_wave.py: A5 tests 1, 2, 3 and 5 on the catalogue each combination gives, and the
converted value of the events that have a measured Mw with that value withheld.
"""
import numpy as np
import pandas as pd

import x4_surface_wave as X
from x4_surface_wave import C, G, TAB

# settings
LOWER = {"step per bin (A5 as run)": "step", "line, zero at Mw 5.4": "ramp0", "line, to where it reaches zero": "ramp", "not lowered": "none"}
# rule: (judge, mean, correlations)
RULES = {"own value reaches Mw 5, first scale (A5 as run)": ("own", False, True),
         "depth limit, first scale": ("depth", False, True),
         "depth limit, inverse-variance mean": ("depth", True, False),
         "depth limit, mean with correlations": ("depth", True, True)}


def blind(D, R, F, P, prio, mean, corr):
    mw = G.assign(D.e, D.M, R.iloc[:0], F, D.rm.iloc[:0], prio, P=P)
    if mean:
        mw = G.combine(D.e, R, F, P, prio, mw, corr)
    y, v = D.e.event_id.map(R.y).to_numpy(float), mw.mw.to_numpy(float)
    k = np.isfinite(y) & (D.e.yr.to_numpy() >= X.FROM) & np.isfinite(v) & (mw.mw_kind == "proxy").to_numpy()
    y, v = y[k], v[k]
    out = {f"events >= {q}, converted / measured": float((v >= q - 0.05).sum() / (np.round(y, 1) >= q - 0.05).sum()) for q in (5.0, 5.5)}
    for lo, hi in zip(X.TRUE_BINS[:-1], X.TRUE_BINS[1:]):
        kb = (y >= lo) & (y < hi)
        out[f"bias at measured {lo}–{hi}"] = float((v - y)[kb].mean())
    kb = (v >= 4.95) & (v < 5.35)
    out["bias at converted 5.0–5.3"] = float((v - y)[kb].mean())
    return out


def main():
    D = C.Data()
    rows = []
    for ln, lower in LOWER.items():
        R, tab, _ = G.reference(D.M, lower=lower)
        if lower.startswith("ramp"):
            print(ln, tab.tail(1).round(3).to_dict("records"), flush=True)
        F = G.relations(D.M, R, D.e, quiet=True, boot=0)
        prio = [s for s in D.prio if s in F]
        for rn, (judge, mean, corr) in RULES.items():
            P = G.proxies(D.e, D.M, F, prio, judge)
            mw = G.assign(D.e, D.M, R, F, D.rm, prio, P=P, judge=judge)
            if mean:
                mw = G.combine(D.e, R, F, P, prio, mw, corr)
            s = X.score(D, f"{ln} | {rn}", mw)
            rows.append({"GCMT below 5.4": ln, "surface-wave rule": rn, **{k: v for k, v in s.items() if k != "rule"},
                         **blind(D, R, F, P, prio, mean, corr)})
            print("  ", ln, "|", rn, flush=True)
    S = pd.DataFrame(rows)
    S.to_csv(TAB / "x4_combos.csv", index=False)
    pd.set_option("display.width", 300, "display.max_columns", 40, "display.max_colwidth", 44)
    print(S.drop(columns=["failed"]).round(3).T.to_string())
    print(S[["GCMT below 5.4", "surface-wave rule", "failed"]].to_string(max_colwidth=200))


if __name__ == "__main__":
    main()

"""X4: does the rule for the surface-wave magnitudes cause the failed A5 tests?

The A5 fits are repeated for two sets of converted scales (the six agencies of the second A5 run, and every
agency as in the first run) and the same events are given their Mw under seven rules for the surface-wave
scales. Each rule is scored with the A5 tests 1, 2, 3 and 5 and, on the events that also have a measured Mw,
by what the rule would have given them had the measured value not existed.
"""
import copy
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "catalog"))
import magnitude as G  # noqa: E402
import magnitude_check as C  # noqa: E402

TAB, FIG = HERE / "tables", HERE / "figs"
for d in (TAB, FIG):
    d.mkdir(exist_ok=True)

# settings
SIX = G.PROXY
ALL = r"^(?!GCMT Mw$|NEIC Mww$|GUC Mwr$|CSN web Mw$|NEIC Mwr$|GFZ Mw$|CSN Mww$|ISC-GEM|Cent |Cabello )"
SETS = {"six agencies": (SIX, G.PRIORITY), "all agencies": (ALL, [])}
SW = r".* [Mm][Ss]\w*$"
Z_SW = 60.0
FROM = 1976
TRUE_BINS = np.round(np.arange(4.5, 6.01, 0.25), 2)
GIVEN = np.round(np.arange(4.8, 5.41, 0.1), 1)
AT = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5]
PUB = {"Scordilis (2006)": lambda x: np.where(x <= 6.1, 0.67 * x + 2.07, 0.99 * x + 0.08),
       "Di Giacomo et al. (2015)": lambda x: np.exp(-0.222 + 0.233 * x) + 2.863,
       "Weatherill et al. (2016)": lambda x: np.where(x <= 6.0, 0.616 * x + 2.369, 0.994 * x + 0.100),
       "Lolli et al. (2014)": lambda x: np.where(x <= 5.5, np.exp(2.133 + 0.063 * x) - 6.205, np.exp(-0.109 + 0.229 * x) + 2.586),
       "Lolli et al. (2023)": lambda x: np.exp(-0.137 + 0.229 * x) + 2.673}
# rule: (limit at Mw 5, shallow only, mean of the scales)
RULES = {"1 own value reaches Mw 5 (A5 as run)": ("own", False, False),
         "2 another scale reaches Mw 5": ("other", False, False),
         "3 no limit, shallow events only": (None, True, False),
         "4 not used": ("never", False, False),
         "5 weighted mean, own value reaches Mw 5": ("own", False, True),
         "6 weighted mean, another scale reaches Mw 5": ("other", False, True),
         "7 weighted mean, no limit, shallow only": (None, True, True)}


def tables(D, limit, shallow):
    """Converted values per scale with the eligibility of the surface-wave scales set by the rule."""
    P = {s: d.copy() for s, d in D.P.items()}
    n = len(D.e)
    oth = G.first([(c, P[c].raw.to_numpy()) for c in D.prio if not P[c].res.iloc[0]] + [("", np.full(n, np.nan))])[0]
    z = D.e.z.to_numpy(float)
    for s, d in P.items():
        if not re.match(SW, s):
            continue
        raw = d.raw.to_numpy()
        k = np.isfinite(raw)
        if limit == "own":
            k &= raw >= G.NOT_BELOW_MW
        elif limit == "other":
            k &= np.where(np.isfinite(oth), oth, raw) >= G.NOT_BELOW_MW
        elif limit == "never":
            k &= False
        if shallow:
            k &= ~(z > Z_SW)
        d["ok"], d["res"] = k, False
    return P


def give(D, rule, R=None, rm=None):
    limit, shallow, mean = RULES[rule]
    D2 = copy.copy(D)
    D2.P = tables(D, limit, shallow)
    mw = G.assign(D.e, D.M, D.R if R is None else R, D.F, D.rm if rm is None else rm, D.prio, P=D2.P)
    return C.gls_mean(D2, mw) if mean else mw


def score(D, name, mw):
    c = D.e[["t", "yr", "lat", "lon", "cls"]]
    T = C.tests123(name, mw.mw, c, D.t_end)[0]
    h = C.headline(T, name)
    z = C.histogram(D, mw, name)[0]
    z = z[z.passed.notna()]
    i = z.value.astype(float).idxmax()
    m, yr = mw.mw.to_numpy(float), D.e.yr.to_numpy()
    sw = mw.mw_type.astype(str).str.fullmatch(r"(?i)ms\w*").to_numpy() & (mw.mw_kind == "proxy").to_numpy()
    k = yr >= FROM
    return {"rule": name, "b range 1976 on": h["b range 1976 to today, declustered"], "b range 2011 on": h["b range 2011 to today, declustered"],
            "rate M>=5.5": h["rate M>=5.5 departure"], "rate M>=5.0": h["rate M>=5.0 departure"],
            "N>=7 from 5.0 (decl.)": h["N >= 7 pred/obs, declustered, from 5.0"],
            "N 6.5-7 from 5.0 (decl.)": h["N 6.5–7 pred/obs, declustered, from 5.0"],
            "N 6.5-7 from 5.0 (full)": h["N 6.5–7 pred/obs, full, from 5.0"],
            "histogram z": float(z.value[i]), "z where": f"{z.subset[i]}, {z.quantity[i][-3:]}",
            "n Mw>=4.5": int((k & (m >= 4.45)).sum()), "n Mw>=5.0": int((k & (m >= 4.95)).sum()),
            "from surface waves, Mw>=4.5": int((k & sw & (m >= 4.45)).sum()), "failed": h["failed (all events)"]}


def blind(D, name):
    """What the rule gives to the events that have a measured Mw, with that value withheld."""
    R0 = D.R.iloc[:0]
    rm0 = D.rm.iloc[:0]
    mw = give(D, name, R0, rm0)
    y = D.e.event_id.map(D.R.y).to_numpy(float)
    k = np.isfinite(y) & (D.e.yr.to_numpy() >= FROM) & np.isfinite(mw.mw.to_numpy(float)) & (mw.mw_kind == "proxy").to_numpy()
    d, v = (mw.mw.to_numpy(float) - y)[k], mw.mw.to_numpy(float)[k]
    y = y[k]
    rows = []
    for lo, hi in zip(TRUE_BINS[:-1], TRUE_BINS[1:]):
        kb = (y >= lo) & (y < hi)
        rows.append({"rule": name, "by": "measured Mw", "bin": f"{lo}–{hi}", "n": int(kb.sum()), "converted − measured": float(d[kb].mean())})
    for g in GIVEN:
        kb = np.abs(v - g) < 1e-6
        rows.append({"rule": name, "by": "converted Mw", "bin": f"{g:.1f}", "n": int(kb.sum()), "converted − measured": float(d[kb].mean())})
    kb = (v >= 4.95) & (v < 5.35)
    rows.append({"rule": name, "by": "converted Mw", "bin": "5.0–5.3", "n": int(kb.sum()), "converted − measured": float(d[kb].mean())})
    for q in (5.0, 5.5):
        rows.append({"rule": name, "by": "count", "bin": f">= {q}", "n": int((v >= q - 0.05).sum()),
                     "converted − measured": float((v >= q - 0.05).sum() / max((np.round(y, 1) >= q - 0.05).sum(), 1))})
    return pd.DataFrame(rows)


def published(D):
    """Mw of our surface-wave relations at fixed native values, next to the published relations."""
    x = np.array(AT)
    rows = []
    for s in [s for s in D.F if re.match(SW, s) and D.F[s]["n"] >= 300]:
        y = G.convert(D.F[s], x, np.full(len(x), 20.0), np.full(len(x), 2015.0))[0]
        rows.append({"relation": f"this study, {s} (n {D.F[s]['n']})", **{f"{a}": round(float(v), 2) for a, v in zip(AT, y)}})
    for k, f in PUB.items():
        rows.append({"relation": k, **{f"{a}": round(float(v), 2) for a, v in zip(AT, f(x))}})
    return pd.DataFrame(rows)


def main():
    S, B = [], []
    for nm, (px, prio) in SETS.items():
        G.PROXY, G.PRIORITY = px, prio
        D = C.Data()
        z = D.e.z.to_numpy(float)
        sw = [s for s in D.prio if re.match(SW, s)]
        deep = sum(int((np.isfinite(D.P[s].raw.to_numpy()) & (z > Z_SW) & (D.e.yr.to_numpy() >= FROM)).sum()) for s in sw)
        tot = sum(int((np.isfinite(D.P[s].raw.to_numpy()) & (D.e.yr.to_numpy() >= FROM)).sum()) for s in sw)
        print(nm, "| scales", len(D.prio), "| surface-wave scales", len(sw), "| their values from", FROM, tot, f"of them deeper than {Z_SW:.0f} km", deep, flush=True)
        if nm == "six agencies":
            published(D).to_csv(TAB / "x4_published.csv", index=False)
        for r in RULES:
            mw = give(D, r)
            S.append({"set": nm, **score(D, r, mw)})
            B.append(blind(D, r).assign(set=nm))
            if nm == "six agencies":
                h = C.histogram(D, mw, r)[1]
                h.reset_index(names="mw").to_csv(TAB / f"x4_histogram_rule{r[0]}.csv", index=False)
            print("  ", r, flush=True)
    S, B = pd.DataFrame(S), pd.concat(B, ignore_index=True)
    S.to_csv(TAB / "x4_scores.csv", index=False)
    B.to_csv(TAB / "x4_blind.csv", index=False)
    pd.set_option("display.width", 260, "display.max_columns", 40, "display.max_rows", 400, "display.max_colwidth", 60)
    print(S.drop(columns="failed").round(3).to_string())
    print(pd.read_csv(TAB / "x4_published.csv").to_string())
    print(B.pivot_table(index=["set", "by", "bin"], columns="rule", values="converted − measured", sort=False).round(3).to_string())


if __name__ == "__main__":
    main()

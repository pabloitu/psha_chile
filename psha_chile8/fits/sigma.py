"""The magnitude error of the catalogue, now that it sets event counts (plan B11, step 1). A report: nothing is
changed. Writes tables/sigma_kinds.csv (sigma and count per Mw kind and period), sigma_proxy.csv (per converted
scale), sigma_iscgem.csv (the ISC-GEM values by quality), sigma_iscgem_events.csv (those with sigma >= HIGH) and
sigma_large.csv (large events per unit and period, by count and by weight)."""
from pathlib import Path

import numpy as np
import pandas as pd

import gr as G
import run as R

HERE = Path(__file__).resolve().parent
ISCGEM = HERE.parent / "catalog/sources/iscgem_2026-11-10_mags.csv"

# settings
BETA = 2.2
MMIN, HIGH = 5.0, 0.6
PERIODS = [(0, 1904), (1904, 1964), (1964, 1976), (1976, 1990), (1990, 2000), (2000, 2011), (2011, 2100)]
LARGE = [(0, 1904), (1904, 1976), (1976, 2100)]
# where the sigma of each kind comes from (catalog/magnitude.py)
ORIGIN = {"direct": "set: 0.08 GCMT, 0.10 W-phase and regional Mw (SY)",
          "proxy": "scatter of the conversion relation less the reference error, larger outside the fitted range (relations table)",
          "iscgem": "the ISC-GEM uncertainty column of Mw (unc); 0.2 where empty (SIG_GEM)",
          "centennial": "set: 0.25, 0.30 for a converted mB (SIG_CENT, SIG_MB)",
          "cabello": "set: 0.5 (SIG_CAB)",
          "rm18": "set: 0.2, +0.1 for bounds and approximate values, half the range for a range (SIG_RM)",
          "a6": "the sigma column of overrides_A6.csv; else that of the value replaced"}


def label(lo, hi):
    return f"before {hi}" if lo == 0 else f"from {lo}" if hi == 2100 else f"{lo}–{hi - 1}"


def stats(g):
    w = np.exp(-BETA ** 2 * g.mw_sigma ** 2 / 2)
    return pd.Series(dict(n=len(g), sigma_min=g.mw_sigma.min(), sigma_median=g.mw_sigma.median(), sigma_max=g.mw_sigma.max(),
                          count_mean=w.mean(), count_min=w.min(), n_sigma_high=int((g.mw_sigma >= HIGH).sum())))


def run():
    pd.set_option("display.width", 250, "display.max_rows", 300, "display.max_colwidth", 60)
    d = G.load(mlow=MMIN)
    te = G.tend(d)
    d["period"] = pd.cut(d.t, [p[0] for p in PERIODS] + [2100], right=False, labels=[label(*p) for p in PERIODS])
    k = d.groupby(["mw_kind", "period"], observed=True).apply(stats, include_groups=False).reset_index()
    k["sigma_from"] = k.mw_kind.map(ORIGIN)
    k.round(3).to_csv(R.TAB / "sigma_kinds.csv", index=False)
    print(k.drop(columns="sigma_from").round(3).to_string(index=False))
    p = d[d.mw_kind == "proxy"].groupby("relation_id").apply(stats, include_groups=False).reset_index()
    p.round(3).to_csv(R.TAB / "sigma_proxy.csv", index=False)
    print(p.round(3).to_string(index=False))
    # ISC-GEM: quality (A-D) and source (d direct, p proxy) of the Mw
    q = pd.read_csv(ISCGEM, dtype={"src_id": str})
    q["quality"], q["source"] = q.note.str.extract(r"q=(\w)")[0], q.note.str.extract(r"s=(\w)")[0]
    x = d[d.mw_kind == "iscgem"].assign(src_id=lambda v: v.mw_src_id.astype(str)).merge(q[["src_id", "agency", "quality", "source", "mag_err"]], on="src_id", how="left")
    assert x.quality.notna().all() and np.allclose(x.mag_err.fillna(0.2), x.mw_sigma)
    g = x.groupby(["period", "agency", "quality", "source"], observed=True).apply(stats, include_groups=False).reset_index()
    g.round(3).to_csv(R.TAB / "sigma_iscgem.csv", index=False)
    print(g.round(3).to_string(index=False))
    hi = x[x.mw_sigma >= HIGH].assign(count=lambda v: np.exp(-BETA ** 2 * v.mw_sigma ** 2 / 2))
    hi[["event_id", "time", "lat", "lon", "depth", "mw", "mw_sigma", "agency", "quality", "source", "count", "cls"]].round(3).to_csv(R.TAB / "sigma_iscgem_events.csv", index=False)
    print(len(hi), "ISC-GEM values with sigma >=", HIGH, "at Mw >=", MMIN, "; by quality:", hi.quality.value_counts().to_dict())
    print("quality D at Mw >=", MMIN, ":", int((x.quality == "D").sum()), "; from the Supplement:", int((x.agency == "ISC-GEM-suppl").sum()))
    # all ISC-GEM values of the source file, for the reading of the column
    print(q.groupby(["agency", "quality", "source"]).mag_err.describe().round(2).to_string())
    # large events by count and by weight
    F, _ = R.fits(G.load(), te, nboot=0)
    rows = []
    for u in R.ORDER:
        w = R.weights(d, u)
        cw = w * G.magw(d.mw_sigma.to_numpy(), F[u]["b"])
        for M in (7.0, 8.0):
            o = dict(unit=u, name=R.name(u), mw=M, b=F[u]["b"])
            for lo, hi_ in LARGE:
                s = ((d.t >= lo) & (d.t < hi_) & (d.mw >= M - 1e-6)).to_numpy()
                o[f"count, {label(lo, hi_)}"], o[f"weighted, {label(lo, hi_)}"] = w[s].sum(), cw[s].sum()
            s = (d.mw >= M - 1e-6).to_numpy()
            o["count, all"], o["weighted, all"] = w[s].sum(), cw[s].sum()
            o["ratio"] = o["weighted, all"] / o["count, all"] if o["count, all"] else np.nan
            rows.append(o)
    L = pd.DataFrame(rows)
    L.round(3).to_csv(R.TAB / "sigma_large.csv", index=False)
    print(L.drop(columns="name").round(2).to_string(index=False))


if __name__ == "__main__":
    run()

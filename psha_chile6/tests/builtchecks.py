# Checks of built source models against the rates they were meant to carry. Plain functions on
# folders and tables, used by test_built.py on real outputs and on a synthetic folder.

import numpy as np
import pandas as pd

from lib import gr, nrml, smooth

TOL = {"N7": 1e-3, "N8": 1e-3, "M0": 5e-3, "c0": 1e-6, "total": 1e-6}
RATES = [("seis", "seismic", "-"), ("geo_lo", "geodetic", "lo"), ("geo_mid", "geodetic", "mid"), ("geo_hi", "geodetic", "hi")]


def n_ge(c, r, m):
    """N(recorded >= m) of written bins: the bins centred at or above m."""
    return float(r[c >= m - 1e-6].sum())


def interface_vs_table(nrml_dir, bp, m0c=9.05, mmin=5.5, pat=None):
    """
    N(>=7), N(>=8), moment and the first bin centre (the recorded mmin) of every interface NRML
    against s04; pat is the content of patagonia.json when the Antarctic interface is in the files.
    """
    out = []
    for gt, geom in (("seg", "segmented"), ("full", "non_segmented")):
        for rt, rate, chi in RATES:
            for form in ("tgr", "tapered"):
                c, r, _ = nrml.mfd_rates(nrml_dir / f"sub__{gt}__{rt}__{form}.xml")
                s = bp[(bp["geom"] == geom) & (bp["rate"] == rate) & (bp["chi"] == chi) & (bp["form"] == form)]
                x = (pat["N7"][form], pat["N8"][form], pat["m0_rate"]) if pat else (0.0, 0.0, 0.0)
                out.append({"file": f"sub__{gt}__{rt}__{form}", "N7": n_ge(c, r, 7.0) / (s["N7.0"].sum() + x[0]) - 1,
                            "N8": n_ge(c, r, 8.0) / (s["N8.0"].sum() + x[1]) - 1,
                            "M0": float((r * gr.m0(c, m0c)).sum()) / (s["m0_rate"].sum() + x[2]) - 1, "c0": float(c[0] - mmin)})
    return pd.DataFrame(out)


def points_vs_grid(nrml_dir, grid_csv):
    """Total rate of each uncapped point-source file against the smoothed grid it was written from."""
    _, rb, _ = smooth.read(grid_csv)
    out = []
    for f in sorted(nrml_dir.glob("*.xml")):
        if f.name.startswith("faults") or "capped" in f.name:
            continue
        c, r, _ = nrml.mfd_rates(f)
        out.append({"file": f.name, "total": float(r.sum()) / float(rb.sum()) - 1 if f.name in ("intraslab.xml", "points_all.xml") else np.nan})
    return pd.DataFrame(out)


def class_totals(out, model):
    """
    N(recorded >= m) of each class as written (in-slab: its NRML file; crustal: its grid), m the larger of the
    fit floor and the first bin of the grid (MMIN), against rate_floor * (10^(-b (m - floor)) - 10^(-b (top(mmax) - floor)))
    from ssm/classes.csv, the rate of an un-renormalized cut at mmax.
    """
    t = pd.read_csv(out / "ssm" / "classes.csv")
    rows = []
    for _, r in t.iterrows():
        k = r["class"]
        if model == "intraslab":
            c, x, _ = nrml.mfd_rates(out / "nrml" / f"intraslab_{k}.xml")
            m = max(r["floor"], c[0])
            n = float(x[c >= m - 1e-6].sum())
        else:
            _, rb, e = smooth.read(out / "ssm" / f"grid_{k}.csv")
            m = max(r["floor"], e[0])
            n = float(rb[:, e[:-1] >= m - 1e-6].sum())
        exp = r["rate_floor"] * (10 ** (-r["b_used"] * (m - r["floor"])) - 10 ** (-r["b_used"] * (gr.top(r["mmax"]) - r["floor"])))
        rows.append({"class": k, "written": n, "expected": exp, "total": n / exp - 1})
    return pd.DataFrame(rows)


def worst(t, tol=TOL):
    """Largest |difference| beyond its tolerance per column, as a dict."""
    return {k: float(t[k].abs().max()) for k in tol if k in t and t[k].abs().max() > tol[k]}

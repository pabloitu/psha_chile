# The fits on disk (outputs/fits/<model>/rates.csv, from fit_check.py) against a fresh refit from the
# current catalog.csv, with the completeness table fit_check used (tables.json, else the config).
# A difference means the catalog or the config changed after fit_check ran, or the code did.

import json

import numpy as np
import pandas as pd
import pytest

pytestmark = [pytest.mark.data, pytest.mark.built]

B_TOL, N_TOL = 2e-3, 5e-3


def refit(paths):
    import fit_check as fc
    import run
    from lib import cat, gr
    from variants import VARIANTS
    trig = cat.load(paths.CATALOG)
    te_all = float(trig["year"].max())
    trig = trig[(trig["mag"] >= fc.MASK_M) & (trig["year"] >= fc.MASK_FROM)]
    rows = []
    for model in fc.MODELS:
        f = paths.ROOT / "outputs" / "fits" / model / "rates.csv"
        if not f.exists():
            continue
        disk = pd.read_csv(f)
        c = run.config(model, VARIANTS[model][fc.REF[model]])
        tj = paths.ROOT / "outputs" / "fits" / model / "tables.json"
        tabs = json.loads(tj.read_text()) if tj.exists() else {}
        te = c.T_END or te_all
        sub = fc.subsets(model, c)
        for k, s in sub.items():
            r = disk[(disk["sub"] == k) & (disk["form"] != "tgr_borrowed")]
            if not len(r):
                continue
            tab = [tuple(x) for x in tabs[s["tab"]]] if s["tab"] in tabs else fc.cfg_table(model, c, k)
            d = s["df"][~fc.mask(s["df"], trig, tab)]
            fl = float(r["floor"].iloc[0])
            m = d.loc[gr.complete(d, tab), "mag"].to_numpy()
            w = gr.weichert(m, tab, te, fl, c.DM)
            rows.append({"model": model, "sub": k, "n": w["n"], "b": w["b"], "b_disk": float(r["b"].iloc[0]),
                         "rate": w["rate"], "rate_disk": float(r["rate_floor"].iloc[0])})
    return pd.DataFrame(rows)


def test_fits_on_disk_come_from_the_current_catalog(paths):
    if not paths.CATALOG.exists():
        pytest.skip("no catalog")
    t = refit(paths)
    if not len(t):
        pytest.skip("no outputs/fits/*/rates.csv: run fit_check.py")
    t["db"], t["dN"] = t["b"] - t["b_disk"], t["rate"] / t["rate_disk"] - 1
    pool = t["sub"].isin(["intra_slab", "slab_deep"])         # pooled b: rates refitted at the common b
    bad = t[~pool & ((t["db"].abs() > B_TOL) | (t["dN"].abs() > N_TOL))]
    assert not len(bad), "fits on disk differ from a refit of the current catalog:\n" + bad.round(4).to_string(index=False)

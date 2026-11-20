"""T8 and T9: one run of the nodal-plane tables, the class of every crustal cell and the in-slab depth model, with
their check figures and the comparison with psha_chile8 (npd_2026-11-18, depth cells of 18 Nov). Settings: the
`planes` and `depth` sections of config/stats.yaml.

Usage: python -m psha9.stats.planes [out_dir]
"""
import datetime
import sys
import time

import numpy as np
import pandas as pd
import yaml
from scipy.spatial import cKDTree

from . import depth as DP
from . import mech as M
from .gr import CFG, ROOT
from .run import decyear, geometry, load, newest, units

P, Z = CFG["planes"], CFG["depth"]


def compare_npd(npd, old):
    """Type weights and first planes per class and type against the psha_chile8 table (oblique there went to the
    type of its largest plunge)."""
    old = old.rename(columns={"class": "cls"})
    old["kind"] = M.kind(M.plunges(*old[["strike", "dip", "rake"]].to_numpy(float).T), False)[0]
    out = []
    for c in npd.cls.unique():
        for k in M.TYPES:
            a, b = old[(old.cls == c) & (old.kind == k)], npd[(npd.cls == c) & (npd.kind == k)]
            if not len(a) and not len(b):
                continue
            pa, pb = (tuple(x.iloc[0][["strike", "dip", "rake"]].astype(float)) if len(x) else None for x in (a, b))
            out.append(dict(cls=c, kind=k, w_psha8=round(a.weight.sum(), 3), w_now=round(b.weight.sum(), 3),
                            plane_psha8="/".join(f"{v:.0f}" for v in pa) if pa else "", plane_now="/".join(f"{v:.0f}" for v in pb) if pb else "",
                            kagan=round(M.kagan(pa, pb), 1) if pa and pb else np.nan))
    return pd.DataFrame(out)


def compare_cells(res, old):
    """Per-cell change against the psha_chile8 cells (nearest cell within 0.07°): median, 16 %, 84 %."""
    d, j = cKDTree(old[["lon", "lat"]].to_numpy()).query(res[["lon", "lat"]].to_numpy())
    k = d <= 0.07
    rows = []
    for c in ("lsd", "w1", "w2", "w3", "h1", "h2", "h3", "h_one"):
        x = res[c].to_numpy()[k] - old[c].to_numpy()[j[k]]
        rows.append({"quantity": c, "median": np.median(x), "16 %": np.percentile(x, 16), "84 %": np.percentile(x, 84),
                     "max |change|": np.abs(x).max(), "cells": int(k.sum())})
    return pd.DataFrame(rows).round(3), j, k


def main(out=None):
    t0 = time.time()
    cat, dat = (ROOT / CFG[k] if CFG.get(k) else newest(k) for k in ("catalog", "data"))
    st = ROOT / "runs" / "stats" / P["stats_in"]
    out = ROOT / (out or f"runs/stats/{P['run']}")
    (out / "figs").mkdir(parents=True, exist_ok=False)
    print("reads", cat.name, dat.name, st.name, "->", out, flush=True)

    # T8 nodal planes
    lim, area = geometry(dat)
    U = units(lim)
    fam = {c: "inslab" for c in CFG["inslab"]["units"]} | {c: "crustal" for c in CFG["crustal"]["units"]}
    d = load(cat, lim, area, U, mlow=P["mlow"])
    tb = pd.read_csv(st / "completeness.csv")
    tables = {c: list(zip(tb[tb.unit == c].mw_from, tb[tb.unit == c].complete_since)) for c in fam}
    ev = M.events(d, fam, tables)
    ev.drop(columns=[c for c in ev if c.startswith("W_")]).to_csv(out / "mech_events.csv", index=False)
    npd, cnt, sh, pairs = M.table(ev, P["oblique"], P["fallback"])
    npd.to_csv(out / "npd.csv", index=False)
    pairs.to_csv(out / "npd_representative.csv", index=False)
    cnt.to_csv(out / "npd_counts.csv", index=False)
    sh.to_csv(out / "npd_shares.csv", index=False)
    old = pd.read_csv(ROOT / P["compare"])
    compare_npd(pairs, old).to_csv(out / "npd_compare_psha8.csv", index=False)
    cells = M.cells(dat)
    cells.to_csv(out / "crustal_cell_class.csv", index=False)
    print(cnt.to_string(), sh.to_string(), npd.to_string(), sep="\n\n", flush=True)
    print(f"T8 done, {time.time() - t0:.0f} s", flush=True)

    # T9 depth model
    c = pd.read_csv(cat / "catalog.csv", low_memory=False)
    dev, log = DP.events(c, decyear(c.time))
    dev.to_csv(out / "depth_events.csv", index=False)
    log.to_csv(out / "depth_events_log.csv", index=False)
    print(log.to_string(), flush=True)
    g = DP.grid(dat)
    fr, res = [], {}
    for k in Z["sets"]:
        e = DP.pick(dev, k)
        res[k], f, f1 = DP.model(e, g)
        res[k].round(3).to_csv(out / ("depth_cells.csv" if k == Z["set"] else f"depth_cells_{k}.csv"), index=False)
        fr.append(dict(set=k, events=len(e), weight=round(e.w.sum(), 1), fraction=round(f, 4), one_layer=round(f1, 4)))
        print(fr[-1], f"{time.time() - t0:.0f} s", flush=True)
    pd.DataFrame(fr).to_csv(out / "depth_fractions.csv", index=False)
    oldc = pd.read_csv(ROOT / Z["compare"])
    cmp, j, k = compare_cells(res[Z["set"]], oldc)
    cmp.to_csv(out / "depth_compare_psha8.csv", index=False)
    print(cmp.to_string(), flush=True)

    from . import planes_figs as FG
    FG.run(out, ev, npd, cells, dat, dev, res, oldc, j, k)
    meta = dict(date=datetime.date.today().isoformat(), reads=dict(catalog=cat.name, data=dat.name, stats=st.name),
                settings=dict(planes=P, depth=Z), seconds=round(time.time() - t0))
    (out / "run.yaml").write_text(yaml.safe_dump(meta, sort_keys=False, allow_unicode=True))
    print(f"done, {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:])

"""C15: depth options on the cells of run 2026-11-16. One layer at one fraction of the Slab2 thickness (the median of
all events), lower-depth options with the reference hypocentres, and the check of the top-slice weight over the
shallow slab. Writes tables/depth_cells_<RUN>.csv (reference with the new one layer), depth_cells_lsd<tag>_<RUN>.csv
and the tables and figure of REPORT_C15.md."""
import numpy as np
import pandas as pd

import depth as D

# settings
RUN = "2026-11-16d"
BASE = "2026-11-16d"
TAB, FIG = D.HERE / "tables", D.HERE / "figs" / RUN
# lower-depth options, fraction of the Slab2 thickness: psha_chile7, and the 95 % fraction with all depth sources
# kept (C14 sensitivity, tables/fraction_2026-11-16.csv)
LSD = {"065": 0.65, "0615": 0.615}
# shallow slab and the A7 interface band (catalog/classify.py: ± 15 km of the top where the top is at most 50 km,
# fading to 65 km)
SHALLOW, BAND = 50.0, 15.0
SECTIONS = [-19.0, -21.0, -23.0, -25.0, -27.0, -29.0, -31.0, -32.5]
SOUTH = [-33.5, -34.5, -35.5, -36.5, -37.5, -38.5, -40.0, -42.0]


def one_layer(ev):
    """The fraction of the Slab2 thickness below the top that holds half of the events, and the same per group."""
    thk = D.slab_at(ev.lon, ev.lat)[1]
    f = D.fraction(ev.d, thk, ev.w, q=50)
    e = ev.assign(r=ev.d / thk, lb=pd.cut(ev.lat, np.arange(-46.0, -15.0, 2.0)), shallow=ev.top <= SHALLOW)
    rows = [("all", "", len(e), f)]
    for k, q in [("source", "source"), ("slab top ≤ 50 km", "shallow"), ("latitude", "lb")]:
        for v, x in e.groupby(q, observed=True):
            if len(x) >= 50:
                rows.append((k, str(v), len(x), float(D.wquant(x.r.to_numpy(), x.w.to_numpy(), 50))))
    return f, pd.DataFrame(rows, columns=["group", "value", "events", "median d / thickness"]).round(3)


def w1_check(ev, g, ref):
    """Top-slice weight of the cells over the shallow slab from all events and from the events over the deeper slab
    alone (kernel spill-over), against the width of the top slice and the interface band."""
    s = (ref.top <= SHALLOW).to_numpy()
    gs = g[s].reset_index(drop=True)
    lsd = (ref.lsd - ref.top).to_numpy()[s]
    out = {}
    for k, e in [("all events", ev), ("events over the deeper slab only", ev[ev.top > SHALLOW]),
                 ("events over the shallow slab only", ev[ev.top <= SHALLOW])]:
        z = D.zone(*D.histograms(e.reset_index(drop=True), gs), lsd=lsd)
        out[k] = z
    rows = []
    for k, z in out.items():
        rows.append({"events": k, "cells": len(z), "w1 median": z.w1.median(), "w2 median": z.w2.median(),
                     "w3 median": z.w3.median(), "n_eff median": z.neff.median()})
    t = pd.DataFrame(rows)
    t["top slice km (median)"] = np.median(lsd / 3)
    t["top slice inside the ± 15 km band"] = float(np.mean(lsd / 3 <= BAND))
    e = ev[ev.top <= SHALLOW]
    t["shallow-slab in-slab weight above 15 km below the top"] = float(np.sum(e.w * (e.d < BAND)) / e.w.sum())
    return t.round(3)


def main():
    import figs
    TAB.mkdir(exist_ok=True)
    ev = pd.read_csv(TAB / f"depth_events_{BASE}.csv", low_memory=False)
    ref = pd.read_csv(TAB / f"depth_cells_{BASE}.csv")
    f, t1 = one_layer(ev)
    t1.to_csv(TAB / f"onelayer_{RUN}.csv", index=False)
    new = ref.copy()
    new["h_one_median"] = ref.h_one
    new["h_one"] = (ref.top + f * ref.thk).round(3)
    new.to_csv(TAB / f"depth_cells_{RUN}.csv", index=False)
    for tag, fr in LSD.items():
        x = new.drop(columns="h_one_median")
        x["lsd"] = (x.top + fr * x.thk).round(3)
        x.to_csv(TAB / f"depth_cells_lsd{tag}_{RUN}.csv", index=False)
    w1_check(ev, ref[["lon", "lat"]], ref).to_csv(TAB / f"w1_check_{RUN}.csv", index=False)
    pd.DataFrame([{"run": RUN, "one-layer fraction": round(f, 4), **{f"lsd {k}": v for k, v in LSD.items()}}]).to_csv(
        TAB / f"options_{RUN}.csv", index=False)
    figs.FIG = FIG
    r = new.assign(a=new.h_one_median - new.top, b=new.h_one - new.top, c=new.h_one - new.h_one_median)
    figs.maps(r, ["a", "b", "c"], ["median of the zone (C14)", f"top + {f:.3f} × thickness", "new − C14"],
              "maps_onelayer", "One-layer hypocentre, km below the slab top", ["magma_r", "magma_r", "RdBu_r"],
              [(5, 30), (5, 30), (-15, 15)])
    figs.sections_layers(ev, new, SECTIONS)
    figs.sections_layers(ev, new, SOUTH, "sections_layers_south")


if __name__ == "__main__":
    main()

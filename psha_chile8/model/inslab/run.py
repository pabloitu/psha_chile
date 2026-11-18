"""C14 steps 2-4: distance of the in-slab events below the Slab2 top, spread onto the grid with the kernel of the
in-slab rate pattern; per cell the seismogenic zone (slab top to the fraction of the Slab2 thickness that holds 95 %
of all events), three equal layers, their weights and hypocentres; checks. Writes tables/depth_cells_<RUN>.csv and the tables and figures of REPORT_C14.md."""
import numpy as np
import pandas as pd

import depth as D

# settings
RUN = "2026-11-18"
TAB, FIG = D.HERE / "tables", D.HERE / "figs"
# instrumental period of the depths (start of the in-slab rate pattern of psha_chile7, SMOOTH_FROM)
T_FROM = 1990.0
TEST_FROM = 2020.0
KNN = 50
# local-network depths (Potin, CSN web, Riedel-Hornig) are left out east of the Chile border
LOCAL = ["potin", "csn"]
# catalogue depths left out: their distances below the slab top have long tails (95 % at 56-91 km against 35-40 km
# for Potin, ISC-EHB and Riedel-Hornig; C14 run 2026-11-15b); the sensitivity case keeps them (Pablo, 15 Nov)
DROP = ["isc", "csn", "csn_isc", "comcat"]
V1 = TAB / "depth_cells_2026-11-15_v1.csv"
# events count with their in-slab class weight, as in the rates (Pablo, 16 Nov); False: in-slab weight 1 only (runs
# up to 2026-11-16c)
CLASS_W = True
# previous run, compared per cell (2026-11-16d: class weights; 2026-11-16c: weight-1 events)
PREV = TAB / "depth_cells_2026-11-16d.csv"


def events(drop=DROP):
    """
    Events of the depth model: in-slab events of the final catalogue (measured depth, from T_FROM) and of
    Riedel-Hornig inside Chile (Ml ≥ 2.5, depth error ≤ 5 km, in-slab by the A7 depth rule), each with its in-slab
    weight (CLASS_W) or only those of weight 1. An event in both counts once, with the Riedel-Hornig depth.

    Returns
    -------
    ev : DataFrame
        source, id, lon, lat, z, top, d (km below the top), w, yr, depth_src.
    log : DataFrame
        Events left at each step.
    """
    log = []

    def note(src, step, m):
        log.append({"source": src, "step": step, "events": int(np.sum(m))})

    r = D.riedel()
    n = np.ones(len(r), bool)
    note("Riedel-Hornig", "all", n)
    n &= (r.Ml >= D.RH_ML).to_numpy()
    note("Riedel-Hornig", f"Ml ≥ {D.RH_ML}", n)
    n &= (r.sig <= D.SIG_MAX).to_numpy()
    note("Riedel-Hornig", f"depth error ≤ {D.SIG_MAX:.0f} km", n)
    n &= D.east_km(r.Lon, r.Lat) <= 0
    note("Riedel-Hornig", "inside Chile", n)
    rtop = D.slab_at(r.Lon, r.Lat)[0]
    sea = D.C.trench_side(r.Lon.to_numpy(), r.Lat.to_numpy(), D.C.TRENCH)[1]
    n &= np.isfinite(rtop) & ~sea
    note("Riedel-Hornig", "slab at the epicentre, east of the trench", n)
    n &= ~D.nest(r.Lon, r.Lat, r.z)
    note("Riedel-Hornig", "Jujuy nest left out", n)
    q = np.zeros((len(r), 3))
    q[n] = D.inslab_weight(r.z[n], r.sig[n], rtop[n])
    n &= q[:, 1] > 0 if CLASS_W else q[:, 1] == 1
    note("Riedel-Hornig", "in-slab by the A7 depth rule" + ("" if CLASS_W else " (weight 1)"), n)

    c = D.catalog()
    k = (c.t >= r.t.min() - 60) & (c.t <= r.t.max() + 60)
    ia, ib = D.match(c.t[k].to_numpy(), c.lat[k].to_numpy(), c.lon[k].to_numpy(), r.t.to_numpy(), r.Lat.to_numpy(), r.Lon.to_numpy())
    dup = np.zeros(len(c), bool)
    dup[np.flatnonzero(k)[ia[n[ib]]]] = True
    yr = D.C.year(c.t)
    m = (c.depth_kind == "measured").to_numpy() & c.in_domain.to_numpy() & c.depth.notna().to_numpy()
    note("catalogue", "measured depth, in the domain", m)
    m &= (c.w_inslab > 0).to_numpy() if CLASS_W else (c.cls == "in-slab").to_numpy()
    note("catalogue", "in-slab weight > 0" if CLASS_W else "in-slab, class weight 1", m)
    m &= yr >= T_FROM
    note("catalogue", f"from {T_FROM:.0f}", m)
    top = D.slab_at(c.lon, c.lat)[0]
    m &= np.isfinite(top)
    note("catalogue", "slab at the epicentre", m)
    m &= (c.sub_inslab != "jujuy_nest").to_numpy()
    note("catalogue", "Jujuy nest left out", m)
    m &= ~(c.depth_src.isin(LOCAL).to_numpy() & (D.east_km(c.lon, c.lat) > 0))
    note("catalogue", "Potin / CSN web depths east of the Chile border left out", m)
    m &= ~dup
    note("catalogue", "events also in Riedel-Hornig left out (counted there)", m)
    if len(drop):
        m &= ~c.depth_src.isin(drop).to_numpy()
        note("catalogue", f"without depths from {', '.join(drop)}", m)
    cat = pd.DataFrame({"source": "catalogue", "id": c.event_id, "lon": c.lon, "lat": c.lat, "z": c.depth, "top": top,
                        "mw": c.mw, "yr": yr, "depth_src": c.depth_src, "w": c.w_inslab if CLASS_W else 1.0})[m]
    rh = pd.DataFrame({"source": "Riedel-Hornig", "id": r.id.astype(str), "lon": r.Lon, "lat": r.Lat, "z": r.z, "top": rtop,
                       "mw": r.Ml, "yr": D.C.year(r.t), "depth_src": "rh", "w": q[:, 1] if CLASS_W else 1.0})[n]
    ev = pd.concat([cat, rh], ignore_index=True)
    ev["d"] = ev.z - ev.top
    return ev, pd.DataFrame(log)


def grid():
    g = pd.read_csv(D.GRID)
    g["top"], g["thk"], _ = D.slab_at(g.lon, g.lat)
    return g[np.isfinite(g.top)].reset_index(drop=True)


def model(ev, g):
    """Depth model of the cells g from the events ev; depths below the top (columns as depth.zone). The lower depth
    is the fraction of the Slab2 thickness that holds 95 % of all events. Returns the model and the fraction."""
    f = D.fraction(ev.d, D.slab_at(ev.lon, ev.lat)[1], ev.w)
    return D.zone(*D.histograms(ev, g), lsd=f * g.thk.to_numpy()), f


def heldout(ev, g):
    """Train on the events before TEST_FROM, score the layers of the later events: kernel, KNN nearest events
    (same layers), and equal shares."""
    from scipy.spatial import cKDTree
    tr, te = ev[ev.yr < TEST_FROM].reset_index(drop=True), ev[ev.yr >= TEST_FROM].reset_index(drop=True)
    mk, _ = model(tr, g)
    cell = cKDTree(D.xyz(g.lon.to_numpy(), g.lat.to_numpy())).query(D.xyz(te.lon.to_numpy(), te.lat.to_numpy()))[1]
    rows = [("kernel of the rate pattern", *D.heldout(mk, te, cell))]
    nb = D.neighbours(tr, g.lon, g.lat, k=KNN)
    mn = mk.copy()
    for i in np.unique(cell):
        z = mk.loc[i, "lsd"]
        x = tr.d.to_numpy()[nb[i]]
        x = np.clip(x[x <= z], 0, None)
        cnt = np.bincount(D.layer_of(x, np.array([0, z / 3, 2 * z / 3, z])), minlength=3)
        mn.loc[i, ["w1", "w2", "w3"]] = (cnt + 1) / (cnt.sum() + 3)
    rows.append((f"{KNN} nearest events", *D.heldout(mn, te, cell)))
    eq = mk.copy()
    eq[["w1", "w2", "w3"]] = 1 / 3
    rows.append(("equal shares", *D.heldout(eq, te, cell)))
    return pd.DataFrame(rows, columns=["shares", "log-likelihood per event", "events scored"])


def table(g, z):
    res = g[["lon", "lat", "top", "thk"]].copy()
    cols = ["lsd", "h1", "h2", "h3", "h_one"]
    res[cols] = z[cols].to_numpy() + g.top.to_numpy()[:, None]
    res["usd"] = g.top
    res[["w1", "w2", "w3"]] = z[["w1", "w2", "w3"]].to_numpy()
    res["n_events"] = z.neff.round(1)
    res["dz_index"] = (res.w1 + res.w3) / 2 - res.w2
    res["old_hypo"], res["old_lsd"] = g.top + D.OLD_FRAC[0] * g.thk, g.top + D.OLD_FRAC[1] * g.thk
    return res[["lon", "lat", "top", "thk", "usd", "lsd", "w1", "w2", "w3", "h1", "h2", "h3", "h_one", "n_events",
                "dz_index", "old_hypo", "old_lsd"]]


def summary(res):
    res = res.assign(lb=pd.cut(res.lat, np.arange(-46.0, -15.0, 2.0)), tb=pd.cut(res.top, [0, 50, 150, 700]),
                     zone=res.lsd - res.top, mh=res.w1 * res.h1 + res.w2 * res.h2 + res.w3 * res.h3)
    res["dh"], res["dl"] = res.mh - res.old_hypo, res.lsd - res.old_lsd
    t = res.groupby(["lb", "tb"], observed=True).agg(cells=("lon", "size"), zone_km=("zone", "median"), w1=("w1", "median"),
                                                     w2=("w2", "median"), w3=("w3", "median"), index=("dz_index", "median"),
                                                     n_eff=("n_events", "median"), mean_hypo_minus_old=("dh", "median"),
                                                     lsd_minus_old=("dl", "median")).reset_index()
    t["lat"] = [f"{-i.right:.0f}–{-i.left:.0f}° S" for i in t.lb]
    t["slab top"] = [f"{i.left:.0f}–{i.right:.0f} km" for i in t.tb]
    return t.drop(columns=["lb", "tb"]).round(2)


def compare(res, ref):
    """Per-cell change against an earlier cell table: median, 16, 84 % and largest absolute change."""
    if not ref.exists():
        return pd.DataFrame()
    x = res.merge(pd.read_csv(ref), on=["lon", "lat"], suffixes=("", "_ref"))
    rows = []
    for c in ("lsd", "h1", "h2", "h3", "h_one", "w1", "w2", "w3", "dz_index", "n_events"):
        d = x[c] - x[c + "_ref"]
        rows.append({"quantity": c, "median new − ref": d.median(), "16 %": d.quantile(0.16), "84 %": d.quantile(0.84),
                     "max |change|": d.abs().max(), "cells": len(d)})
    return pd.DataFrame(rows).round(3)


def main():
    import figs
    TAB.mkdir(exist_ok=True)
    ev, log = events()
    ev.to_csv(TAB / f"depth_events_{RUN}.csv", index=False)
    log.to_csv(TAB / f"events_log_{RUN}.csv", index=False)
    g = grid()
    z, f = model(ev, g)
    res = table(g, z)
    res.round(3).to_csv(TAB / f"depth_cells_{RUN}.csv", index=False)
    summary(res).to_csv(TAB / f"depth_summary_{RUN}.csv", index=False)
    compare(res, V1).to_csv(TAB / f"compare_v1_{RUN}.csv", index=False)
    compare(res, PREV).to_csv(TAB / f"compare_{PREV.stem[12:]}_{RUN}.csv", index=False)
    heldout(ev, g).round(4).to_csv(TAB / f"heldout_{RUN}.csv", index=False)
    es, _ = events(())
    zs, fs = model(es, g)
    s = table(g, zs)
    pd.DataFrame([{"run": RUN, "fraction": f, "fraction_all_depths": fs, "events": len(ev), "weight": ev.w.sum(), "events_all_depths": len(es)}]).round(4).to_csv(
        TAB / f"fraction_{RUN}.csv", index=False)
    sens = pd.DataFrame({c: (s[c] - res[c]).describe(percentiles=[0.05, 0.5, 0.95]) for c in ("lsd", "w1", "w2", "w3", "h_one", "dz_index")})
    sens.round(3).to_csv(TAB / f"sensitivity_all_depths_{RUN}.csv")
    s.round(3).to_csv(TAB / f"depth_cells_all_depths_{RUN}.csv", index=False)
    figs.FIG = FIG / RUN
    figs.all_figs(ev, res)


if __name__ == "__main__":
    main()

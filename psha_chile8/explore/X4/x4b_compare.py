"""X4 (classification): the baseline classes against the old classifier (cat_handler_2, frozen 2026-11-04), Ruiz and
Madariaga (2018) and Candia and Macedo (2026). Needs tables/x4b_events_m45.csv (x4b_classify.py)."""
import numpy as np
import pandas as pd

import x4b_classify as X

# inputs (read only)
OLD = X.REPO / "results" / "cat_handler_2" / "frozen" / "2026-11-04" / "catalog.csv"
RM = X.ROOT / "catalog" / "merged" / "review" / f"rm18_matches_{X.A3}.csv"
CM = X.ROOT / "catalog" / "cache" / "candia_macedo.csv"
# an event of the other catalogue is the same earthquake within DT s and DD km (before 1964: DT0, DD0)
DT, DD, DT0, DD0 = 15.0, 100.0, 90.0, 300.0
BIG_PASS = [(6.0, 120.0), (7.0, 36 * 3600.0)]
OLD_NAME = {"slab_interface": "interface", "antarctic_interface": "Antarctic interface", "intra_slab": "in-slab (slab top < 50 km)",
            "slab_deep": "in-slab (deeper)", "deep_nest": "in-slab (Jujuy nest)", "forearc": "crustal forearc", "intraarc": "crustal arc",
            "backarc": "crustal backarc", "patagonia_crustal": "crustal Patagonia", "outer_rise": "outer rise", "sub_slab": "below slab",
            "unresolved": "unresolved", "unclassified": "no slab model"}
OLD_FAM = {"slab_interface": "interface", "antarctic_interface": "interface", "intra_slab": "in-slab", "slab_deep": "in-slab",
           "deep_nest": "in-slab", "forearc": "crustal", "intraarc": "crustal", "backarc": "crustal", "patagonia_crustal": "crustal"}
CM_NAME = {"IF": "interface", "SL": "in-slab", "SC": "crustal", "OR": "outer rise", "UN": "unknown"}
RM_FAM = {"interface": "interface", "intraslab": "in-slab", "crustal": "crustal", "outer_rise": "outer rise"}
FAM = {**X.FAMILY, "outer rise": "outer rise", "unknown depth": "unknown depth", "below slab": "below slab", "unclassified": "unclassified"}


def tsec(s):
    """Seconds since 1900 from ISO strings (numpy, so years before 1677 work)."""
    s = pd.Series(s).astype(str).str.replace("Z", "", regex=False).str.replace(" ", "T", regex=False)
    out = np.full(len(s), np.nan)
    for i, v in enumerate(s.to_numpy()):
        try:
            out[i] = (np.datetime64(v, "ms") - np.datetime64("1900-01-01", "ms")) / np.timedelta64(1, "s")
        except ValueError:
            pass
    return out


def hav(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def match(t, lat, lon, t2, lat2, lon2, dt=None, dd=None, free=None):
    """Index into the second catalogue of the same earthquake for every event of the first (-1: none): closest pairs
    first, one to one. dt, dd: window per event (default DT, DD; DT0, DD0 before 1964; NaN: not matched)."""
    if dt is None:
        old = t < 64 * 365.2425 * 86400
        dt, dd = np.where(old, DT0, DT), np.where(old, DD0, DD)
    free = np.ones(len(t2), bool) if free is None else free
    o = np.argsort(t2)
    o = o[free[o] & np.isfinite(t2[o])]
    ts = t2[o]
    cand = []
    for i in np.flatnonzero(np.isfinite(t) & np.isfinite(dt)):
        a, b = np.searchsorted(ts, [t[i] - dt[i], t[i] + dt[i]])
        for j in o[a:b]:
            d = hav(lat[i], lon[i], lat2[j], lon2[j])
            if d <= dd[i]:
                cand.append((abs(t[i] - t2[j]) / dt[i] + d / dd[i], i, j))
    out, used = np.full(len(t), -1), set()
    for _, i, j in sorted(cand):
        if out[i] < 0 and j not in used:
            out[i] = j
            used.add(j)
    return out


def old(x):
    o = pd.read_csv(OLD, low_memory=False)
    o = o[o.mag >= X.MMIN].reset_index(drop=True)
    a = (x.t.to_numpy(), x.lat.to_numpy(), x.lon.to_numpy(), tsec(o.time_iso), o.latitude.to_numpy(), o.longitude.to_numpy())
    j = match(*a)
    # the old catalogue carries centroid times and some dates a day off for large events: two wider passes
    for mmin, dt in BIG_PASS:
        free = np.ones(len(o), bool)
        free[j[j >= 0]] = False
        j2 = match(*a, dt=np.where((j < 0) & (x.mw.to_numpy() >= mmin), dt, np.nan), dd=np.full(len(x), DD0), free=free & (o.mag.to_numpy() >= mmin - 1))
        j = np.where(j >= 0, j, j2)
    k = j >= 0
    x = x.assign(old_class=None, old_rule=None, old_depth=np.nan, old_status=None, old_mag=np.nan)
    for a, b in (("old_class", "class"), ("old_rule", "cls_rule"), ("old_depth", "depth"), ("old_status", "depth_status"), ("old_mag", "mag")):
        x.loc[k, a] = o[b].to_numpy()[j[k]]
    info = {"old events M ≥ 4.5": len(o), "new events Mw ≥ 4.5 in the domain": len(x), "matched": int(k.sum()),
            "old not in new": len(o) - int(k.sum()), "new not in old": int((~k).sum()),
            "new not in old, to the end of 2022": int((~k & (x.time < "2023")).sum())}
    return x, info


def cm(x):
    c = pd.read_csv(CM, low_memory=False)
    c["mwf"] = c.mw.fillna(c.mag)
    c = c.sort_values("mwf", ascending=False).groupby("group", as_index=False).agg(
        time=("time", "first"), lat=("lat", "first"), lon=("lon", "first"), mw=("mwf", "max"), mech=("mech", lambda q: q.mode().iloc[0]),
        n_mech=("mech", "nunique"))
    c = c[c.mw >= X.MMIN - 0.5].reset_index(drop=True)
    j = match(x.t.to_numpy(), x.lat.to_numpy(), x.lon.to_numpy(), tsec(c.time), c.lat.to_numpy(), c.lon.to_numpy())
    k = j >= 0
    x = x.assign(cm_class=None)
    x.loc[k, "cm_class"] = c.mech.map(CM_NAME).to_numpy()[j[k]]
    return x, {"Candia and Macedo groups with M ≥ 4.0": len(c), "matched to Candia and Macedo": int(k.sum()), "groups with more than one class": int((c.n_mech > 1).sum())}


def run():
    x = pd.read_csv(X.TAB / "x4b_events_m45.csv", low_memory=False)
    x["t"] = tsec(x.time)
    x["fam"] = x.cls.map(FAM)
    x, io = old(x)
    x, ic = cm(x)
    r = pd.read_csv(RM)
    x = x.merge(r[["event_id", "rm18", "rm_class", "rm_mw"]], on="event_id", how="left")
    pd.Series({**io, **ic, "Ruiz and Madariaga events matched in A3": len(r), "of them Mw ≥ 4.5 in the domain": int(x.rm18.notna().sum())}).to_csv(
        X.TAB / "x4b_compare_info.csv", header=["n"])

    for m in (4.5, 5.5, 7.0):
        k = x.mw >= m
        t = pd.crosstab(x.old_class[k].map(OLD_NAME).fillna("not in the old catalogue"), x.cls[k], margins=True)
        t.to_csv(X.TAB / f"x4b_old_m{m:g}.csv")
        y = x[k & (x["sub"].fillna("") != "")]
        pd.crosstab(y.old_class.map(OLD_NAME).fillna("not in the old catalogue"), y["sub"], margins=True).to_csv(X.TAB / f"x4b_old_inslab_m{m:g}.csv")
        t = pd.crosstab(x.cm_class[k].fillna("not matched"), x.fam[k], margins=True)
        t.to_csv(X.TAB / f"x4b_candia_macedo_m{m:g}.csv")
    # agreement at family level, both classified
    rows = []
    for m in (4.5, 5.5, 6.5, 7.0):
        k = (x.mw >= m)
        of = x.old_class.map(OLD_FAM)
        b = k & of.notna() & x.fam.isin(["interface", "in-slab", "crustal"])
        cf = x.cm_class.where(x.cm_class.isin(["interface", "in-slab", "crustal"]))
        c = k & cf.notna() & x.fam.isin(["interface", "in-slab", "crustal"])
        rows.append({"mmin": m, "old: both in a family": int(b.sum()), "old: same family": int((of[b] == x.fam[b]).sum()),
                     "old: interface → in-slab": int(((of == "interface") & (x.fam == "in-slab") & b).sum()),
                     "old: in-slab → interface": int(((of == "in-slab") & (x.fam == "interface") & b).sum()),
                     "old: interface → crustal": int(((of == "interface") & (x.fam == "crustal") & b).sum()),
                     "old in a family, new unknown depth": int((k & of.notna() & (x.cls == "unknown depth")).sum()),
                     "old unresolved, new in a family": int((k & (x.old_class == "unresolved") & x.fam.isin(["interface", "in-slab", "crustal"])).sum()),
                     "C&M: both in a family": int(c.sum()), "C&M: same family": int((cf[c] == x.fam[c]).sum()),
                     "C&M: interface → in-slab": int(((cf == "interface") & (x.fam == "in-slab") & c).sum()),
                     "C&M: in-slab → interface": int(((cf == "in-slab") & (x.fam == "interface") & c).sum()),
                     "C&M in a family, new unknown depth": int((k & cf.notna() & (x.cls == "unknown depth")).sum())})
    pd.DataFrame(rows).to_csv(X.TAB / "x4b_agreement.csv", index=False)

    # depth differences behind the family changes against the old catalogue
    b = x[x.old_class.map(OLD_FAM).notna() & x.fam.isin(["interface", "in-slab", "crustal"]) & (x.old_class.map(OLD_FAM) != x.fam)]
    b.assign(dz=b.z - b.old_depth)[["event_id", "time", "lon", "lat", "mw", "z", "sig", "depth_src", "old_depth", "old_status", "dz", "top", "d", "ifl",
                                    "cls", "rule", "old_class", "old_rule"]].sort_values("mw", ascending=False).round(2).to_csv(
        X.TAB / "x4b_old_family_changes.csv", index=False)

    # Ruiz and Madariaga, event by event
    q = x[x.rm18.notna()].copy()
    q["rm_family"] = q.rm_class.map(RM_FAM)
    q["agree"] = np.where(q.rm_family.isna(), "no class in the paper", np.where(q.cls_auto == "unknown depth", "unknown depth",
                          np.where(q.rm_family == q.cls_auto.map(FAM), "yes", "no")))
    q[["rm18", "rm_class", "rm_mw", "time", "lon", "lat", "mw", "z", "sig", "depth_src", "top", "d", "ifl", "cls_auto", "agree", "cls", "sub",
       "old_class", "cm_class"]].sort_values("time").round(2).to_csv(X.TAB / "x4b_rm18.csv", index=False)
    x[x.mw >= 7.0][["event_id", "time", "lon", "lat", "mw", "z", "sig", "depth_src", "top", "d", "ifl", "cls_auto", "cls", "sub", "rule", "rm18", "rm_class",
                    "old_class", "cm_class"]].round(2).to_csv(X.TAB / "x4b_m7_compare.csv", index=False)
    x[["event_id", "old_class", "old_rule", "old_depth", "old_status", "cm_class", "rm18", "rm_class"]].to_csv(
        X.TAB / "x4b_compare_events.csv", index=False)
    print(pd.read_csv(X.TAB / "x4b_compare_info.csv").to_string())
    print(pd.DataFrame(rows).T.to_string())
    print(q.agree.value_counts().to_dict())


if __name__ == "__main__":
    run()

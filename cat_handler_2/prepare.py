# Data preparation: the frozen sources -> catalog_base.csv, one row per
# earthquake with location, depth status, magnitude and focal mechanism, no
# class. This is the mid-way product the classification (classify.py) reads.
#   overrides  overrides.csv row fixes (time, location) and additions.csv are
#              applied to the Cabello rows before anything else
#   dedup      cross-agency duplicates inside Cabello: one row per earthquake
#   locate     Potin for unrelocated CSN rows; depth status; fixed or missing
#              depths from the group, Potin, GCMT
#   mech       focal mechanisms ANSS > GCMT > GEM > Cabello; ComCat location
#              for GCMT-located events
#   magnitudes overrides.csv magnitude decisions on the final events
# Writes results/cat_handler_2/prepare/ (stage tables, prepare.json) and
# results/cat_handler_2/catalog_base.csv.

import json

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from cat_handler_2 import config as C
from cat_handler_2 import sources as S


# dedup
# GCMT rows of Cabello carry the centroid, so each is first tied to its ndk
# entry and matched on the PDE hypocentre. Rows of different agencies within
# the config windows form groups; each group becomes one event with the
# location of one row and the Cabello magnitude of one row (LOC_PREF, MAG_PREF).
def tie_gcmt(x, g):
    """GCMT rows of x -> ndk entry: gcmt_id, centroid columns and the PDE hypocentre as th, lon_h, lat_h."""
    x = x.assign(th=x["t"], lon_h=x["longitude"], lat_h=x["latitude"], gcmt_id=None)
    i = np.flatnonzero(x["agency"].to_numpy() == "GCMT")
    xg = x.iloc[i].reset_index(drop=True)
    q = S.one_to_one(S.pairs(xg, g, C.GC_DT, C.GC_KM, 0.5, tb="ct", xb=("c_lon", "c_lat")), C.GC_DT, C.GC_KM)
    r, j = x.index[i[q["ia"]]], q["ib"].to_numpy()
    x.loc[r, ["th", "lon_h", "lat_h"]] = g[["t", "longitude", "latitude"]].to_numpy()[j]
    x.loc[r, "gcmt_id"] = g["id"].to_numpy()[j]
    return x, len(i), len(q)


def dedup(x, g):
    """
    Remove cross-agency duplicates from the Cabello catalog.

    Parameters
    ----------
    x : DataFrame
        read.cabello().
    g : DataFrame
        read.gcmt().

    Returns
    -------
    ev : DataFrame
        One row per event: the location row of each group with its Cabello
        magnitude replaced by the chosen one; loc_src, mag_src, dup_ids, n_rows.
    grp : DataFrame
        One row per member of a group of two or more rows, with the group id,
        the pair distances to the kept row and the flags.
    info : dict
    rows : DataFrame
        The rows read, with the group label grp and the hypocentre used for
        matching (th, lon_h, lat_h); for check.py.
    """
    x = x[x["mag"] > C.MMIN - C.DUP_DM]
    x, n_gc, n_tied = tie_gcmt(x.reset_index(drop=True), g)
    ok = np.flatnonzero(x["year"].to_numpy() >= C.DUP_FROM)
    y = x.iloc[ok]
    p = S.pairs(y, y, C.DUP_DT, C.DUP_KM, C.DUP_DM, ta="th", tb="th", xa=("lon_h", "lat_h"), xb=("lon_h", "lat_h"))
    ag = y["agency"].to_numpy()
    inside = np.zeros(len(p), bool)
    mg = y["mag"].to_numpy()
    mx = np.fmax(mg[p["ia"]], mg[p["ib"]])
    for dt, km, dm, m0 in C.DUP_RULES:
        inside |= ((p["dt"] <= dt) & (p["dkm"] <= km) & ~(p["dm"].abs() > dm)).to_numpy() & (mx >= m0)
    p = p[inside & (p["ia"] < p["ib"]).to_numpy() & (ag[p["ia"]] != ag[p["ib"]])]
    a, b = ok[p["ia"]], ok[p["ib"]]
    n = len(x)
    _, lab = connected_components(coo_matrix((np.ones(len(a)), (a, b)), shape=(n, n)), directed=False)
    x["grp"] = lab
    size = x.groupby("grp")["id"].transform("size")

    key = np.where(x["relocated"].eq("Relocated_Potin"), "relocated", x["agency"])
    x["loc_rank"] = pd.Series(key).map({k: r for r, k in enumerate(C.LOC_PREF)}).fillna(len(C.LOC_PREF)).to_numpy()
    mr = x["agency"].map({k: r for r, k in enumerate(C.MAG_PREF)}).fillna(len(C.MAG_PREF))
    x["mag_rank"] = np.where(mr < len(C.MAG_PREF), mr, np.where(x["Mw_native"].notna(), len(C.MAG_PREF), len(C.MAG_PREF) + 1))
    fb = x["agency"].map({k: r for r, k in enumerate(C.MAG_FALLBACK)}).fillna(len(C.MAG_FALLBACK)).to_numpy()
    x["mag_rank"] = x["mag_rank"] + fb / 100 + x["loc_rank"] / 10000

    m = x[size > 1]
    kl = m.sort_values(["grp", "loc_rank", "t"]).drop_duplicates("grp").set_index("grp")
    km = m.sort_values(["grp", "mag_rank"]).drop_duplicates("grp").set_index("grp")
    ids = m.groupby("grp")["id"].agg(";".join)
    same = m.groupby("grp")["agency"].agg(lambda s: s.duplicated().any())
    gc = m.dropna(subset=["gcmt_id"]).drop_duplicates("grp").set_index("grp")["gcmt_id"]

    ev = x[size == 1].assign(loc_src=x["agency"], mag_src=x["agency"], dup_ids="", n_rows=1)
    kept = kl.assign(mag=km["mag"], mag_src=km["agency"], loc_src=kl["agency"], dup_ids=ids,
                     n_rows=m.groupby("grp").size(), gcmt_id=kl["gcmt_id"].fillna(gc))
    ev = pd.concat([ev, kept.reset_index()], ignore_index=True).sort_values(["t", "id"], ignore_index=True)
    ev = ev.drop(columns=["loc_rank", "mag_rank", "th", "lon_h", "lat_h"])

    g2 = m.merge(kl[["id", "th", "lon_h", "lat_h", "mag"]].rename(columns=lambda c: c + "_k"), left_on="grp",
                 right_index=True).reset_index(drop=True)
    g2["dt_k"] = (g2["th"] - g2["th_k"]).abs().round(1)
    g2["dkm_k"] = S.hav(g2["lon_h"], g2["lat_h"], g2["lon_h_k"], g2["lat_h_k"]).round(1)
    g2["kept"] = g2["id"] == g2["id_k"]
    g2["mag_kept"] = g2["grp"].map(km["mag"])
    g2["n_rows"] = g2["grp"].map(m.groupby("grp").size())
    g2["same_agency"] = g2["grp"].map(same)
    g2["loose"] = g2["grp"].map(g2.groupby("grp").apply(
        lambda s: bool((s["dt_k"] > C.DUP_TIGHT_DT).any() or (s["dkm_k"] > C.DUP_TIGHT_KM).any()), include_groups=False))
    g2["m_max"] = g2.groupby("grp")["mag"].transform("max")
    cols = ["grp", "n_rows", "kept", "id", "agency", "relocated", "time_iso", "longitude", "latitude", "depth", "mag",
            "Mw_native", "gcmt_id", "dt_k", "dkm_k", "mag_kept", "same_agency", "loose", "m_max"]
    g2 = g2[g2["mag_kept"] > C.MMIN]
    grp = g2.sort_values(["m_max", "grp", "kept"], ascending=[False, True, False])[cols].reset_index(drop=True)
    ev = ev[ev["mag"] > C.MMIN].reset_index(drop=True)
    info = {"rows_read": n, "gcmt_rows": n_gc, "gcmt_tied": n_tied, "pairs": len(p), "groups": int(m["grp"].nunique()),
            "rows_in_groups": len(m), "events": len(ev)}
    return ev, grp, info, x


# locate
# A CSN row Cabello did not relocate takes Potin's location and depth when a
# Potin event not used by Cabello matches one-to-one. A depth is fixed when the
# row sits at one of its agency's default depths (FIXED_DEPTHS) or the agency
# reports a zero depth error (FIXED_ERROR_ZERO). A fixed or missing depth is
# replaced, in this order, by: another non-GCMT row of the same group with a
# free depth (its location and depth), Potin (location and depth), the GCMT
# centroid depth when GCMT solved for it (depth only).
def fixed(df):
    z = pd.to_numeric(df["depth"], errors="coerce").round(1).to_numpy()
    ag = df["agency"].to_numpy()
    out = np.zeros(len(df), bool)
    for a, vals in C.FIXED_DEPTHS.items():
        out |= (ag == a) & np.isin(z, np.round(vals, 1))
    if "depth_error" in df:
        e = pd.to_numeric(df["depth_error"], errors="coerce").to_numpy()
        out |= np.isin(ag, C.FIXED_ERROR_ZERO) & (e == 0)
    return out


def locate(ev, rows, pt, g):
    """
    Location, depth and depth status of every event.

    Parameters
    ----------
    ev, rows : DataFrame
        Events and rows from dedup.
    pt, g : DataFrame
        sources.potin(), sources.gcmt().

    Returns
    -------
    ev : DataFrame
        With depth_status (relocated_cabello, relocated_potin, free, assigned,
        fixed, missing, filled), depth_src, potin_id, depth_orig, and loc_src
        updated where the location changed.
    info : dict
    """
    ev = ev.reset_index(drop=True).copy()
    z = pd.to_numeric(ev["depth"], errors="coerce")
    ev["depth_orig"] = z
    ev["lon_orig"], ev["lat_orig"] = ev["longitude"], ev["latitude"]
    ev["depth_src"] = ev["loc_src"]
    ev["potin_id"] = None
    ev["potin_dt"], ev["potin_dkm"] = np.nan, np.nan
    ev["depth_status"] = np.select([ev["relocated"].eq("Relocated_Potin"), ev["obs_depth"].notna(), z.isna(), fixed(ev)],
                                   ["relocated_cabello", "assigned", "missing", "fixed"], "free")
    rc = ev[ev["depth_status"] == "relocated_cabello"]
    taken = set(S.pairs(rc, pt, 1.0, 1.0)["ib"])
    free_pt = np.array([k not in taken for k in range(len(pt))])
    info = {"potin_used_by_cabello": len(taken)}

    def take(i, src, j, kind):
        k = ev.index[i]
        ev.loc[k, ["longitude", "latitude", "depth"]] = src[["longitude", "latitude", "depth"]].to_numpy()[j]
        ev.loc[k, ["loc_src", "depth_src"]] = kind

    m = (ev["agency"].eq("CSN-improved") & ev["relocated"].ne("Relocated_Potin")).to_numpy()
    a = ev[m]
    pf = pt[free_pt]
    q = S.one_to_one(S.pairs(a, pf, C.POT_DT, C.POT_KM, C.POT_DM), C.POT_DT, C.POT_KM)
    take(np.flatnonzero(m)[q["ia"]], pf, q["ib"].to_numpy(), "potin")
    ev.loc[ev.index[np.flatnonzero(m)[q["ia"]]], "potin_id"] = pf["id"].to_numpy()[q["ib"]]
    ev.loc[ev.index[np.flatnonzero(m)[q["ia"]]], "depth_status"] = "relocated_potin"
    ev.loc[ev.index[np.flatnonzero(m)[q["ia"]]], ["potin_dt", "potin_dkm"]] = q[["dt", "dkm"]].round(1).to_numpy()
    free_pt[np.flatnonzero(free_pt)[q["ib"]]] = False
    info["csn_relocated_here"] = len(q)

    bad = ev["depth_status"].isin(["fixed", "missing"]).to_numpy()
    info["fixed_or_missing"] = int(bad.sum())
    zr = pd.to_numeric(rows["depth"], errors="coerce")
    ok = rows[rows["agency"].ne("GCMT") & zr.notna() & ~fixed(rows) & rows["obs_depth"].isna()]
    ok = ok.assign(r=ok["relocated"].eq("Relocated_Potin").map({True: 0, False: 1})).sort_values(["grp", "r"])
    ok = ok.drop_duplicates("grp").set_index("grp")
    i = np.flatnonzero(bad & ev["grp"].isin(ok.index).to_numpy())
    w = ok.loc[ev["grp"].to_numpy()[i]]
    ev.loc[ev.index[i], ["longitude", "latitude", "depth"]] = w[["longitude", "latitude", "depth"]].to_numpy()
    ev.loc[ev.index[i], ["loc_src", "depth_src"]] = w["agency"].to_numpy()[:, None].repeat(2, 1)
    ev.loc[ev.index[i], "depth_status"] = "filled"
    info["filled_from_group"] = len(i)

    bad = ev["depth_status"].isin(["fixed", "missing"]).to_numpy()
    pf = pt[free_pt]
    q = S.one_to_one(S.pairs(ev[bad], pf, C.POT_FIX_DT, C.POT_FIX_KM, C.POT_DM), C.POT_FIX_DT, C.POT_FIX_KM)
    i = np.flatnonzero(bad)[q["ia"]]
    take(i, pf, q["ib"].to_numpy(), "potin")
    ev.loc[ev.index[i], "potin_id"] = pf["id"].to_numpy()[q["ib"]]
    ev.loc[ev.index[i], ["potin_dt", "potin_dkm"]] = q[["dt", "dkm"]].round(1).to_numpy()
    ev.loc[ev.index[i], "depth_status"] = "filled"
    info["filled_from_potin"] = len(q)

    bad = ev["depth_status"].isin(["fixed", "missing"]).to_numpy()
    gi = pd.Series(np.arange(len(g)), index=g["id"])
    j = ev["gcmt_id"].map(gi).to_numpy()
    rest = np.flatnonzero(bad & pd.isna(j))
    q = S.one_to_one(S.pairs(ev.iloc[rest], g, C.GC_FILL_DT, C.GC_FILL_KM, C.GC_FILL_DM), C.GC_FILL_DT, C.GC_FILL_KM)
    j[rest[q["ia"]]] = q["ib"]
    i = np.flatnonzero(bad & ~pd.isna(j))
    jj = j[i].astype(int)
    fr = g["c_dtype"].to_numpy()[jj] == "FREE"
    i, jj = i[fr], jj[fr]
    ev.loc[ev.index[i], "depth"] = g["c_depth"].to_numpy()[jj]
    ev.loc[ev.index[i], "depth_src"] = "gcmt"
    ev.loc[ev.index[i], "gcmt_id"] = g["id"].to_numpy()[jj]
    ev.loc[ev.index[i], "depth_status"] = "filled"
    info["filled_from_gcmt"] = len(i)
    info["status"] = ev["depth_status"].value_counts().to_dict()
    info["status_M>=5.5"] = ev.loc[ev["mag"] >= 5.5, "depth_status"].value_counts().to_dict()
    return ev, info


# mech
# Focal mechanism of every event from the first source in MECH_ORDER with
# both nodal planes: ANSS (ComCat moment tensors), GCMT (the ndk entry tied in
# dedup or locate, else matched on the PDE hypocentre), Cabello's own planes
# (any row of the group), GEM. Matches are one-to-one within MECH_WIN, on the
# hypocentre (GCMT-only events use their PDE hypocentre). The ids of every
# source found are kept so the sources can be compared.
def mech(ev, rows, g, an, gm):
    """
    Focal mechanism, its source and the ids of all sources that have one.

    Returns
    -------
    ev : DataFrame
        strike1..rake2 and Mrr..Mtp of the chosen source (tensor only when
        that source has one), mech_src, mech_type, anss_id, gcmt_id, gem_id,
        cab_mech_id, and per source the match dt and km.
    info : dict
    """
    ev = ev.reset_index(drop=True).copy()
    gi = pd.Series(np.arange(len(g)), index=g["id"])
    h = ev[["id", "t", "longitude", "latitude", "mag"]].copy()
    j = ev["gcmt_id"].map(gi)
    k = ev["agency"].eq("GCMT").to_numpy() & j.notna().to_numpy()
    h.loc[k, ["t", "longitude", "latitude"]] = g[["t", "longitude", "latitude"]].to_numpy()[j[k].astype(int)]
    h["depth"] = ev["depth"]

    full = lambda d: d[S.SDR].apply(pd.to_numeric, errors="coerce").notna().all(axis=1).to_numpy()
    hit = {}
    for src, d in (("anss", an), ("gem", gm)):
        d = d[full(d)].reset_index(drop=True)
        dt, km, dm = C.MECH_WIN[src]
        q = S.one_to_one(S.pairs(h, d, dt, km, dm), dt, km)
        hit[src] = (d, q)
        ev[f"{src}_id"], ev[f"{src}_dt"], ev[f"{src}_km"] = None, np.nan, np.nan
        ev.loc[q["ia"], f"{src}_id"] = d["id"].to_numpy()[q["ib"]]
        ev.loc[q["ia"], [f"{src}_dt", f"{src}_km"]] = q[["dt", "dkm"]].round(1).to_numpy()

    moved = 0
    if C.GCMT_TO_ANSS:
        d, q = hit["anss"]
        gl = ev["agency"].eq("GCMT").to_numpy()
        todo = np.flatnonzero(gl & ev["anss_id"].isna().to_numpy())
        dt, km, dm = C.ANSS_LOC_WIN
        free_a = ~np.isin(np.arange(len(d)), q["ib"].to_numpy())
        w = S.one_to_one(S.pairs(h.iloc[todo].reset_index(drop=True), d[free_a].reset_index(drop=True), dt, km, dm), dt, km)
        i = np.r_[q["ia"].to_numpy()[gl[q["ia"].to_numpy()]], todo[w["ia"].to_numpy()]]
        jj = np.r_[q["ib"].to_numpy()[gl[q["ia"].to_numpy()]], np.flatnonzero(free_a)[w["ib"].to_numpy()]]
        z = pd.to_numeric(d["depth"], errors="coerce").to_numpy()[jj]
        dflt = ~np.isfinite(z) | np.isin(np.round(z, 1), C.FIXED_DEPTHS["USGS"])
        ev["anss_loc_id"] = None
        ev.loc[i, "anss_loc_id"] = d["id"].to_numpy()[jj]
        ev.loc[i, ["longitude", "latitude"]] = d[["longitude", "latitude"]].to_numpy(float)[jj]
        ev.loc[i, ["time_iso", "t"]] = d[["time_iso", "t"]].to_numpy()[jj]
        ev.loc[i[~dflt], "depth"] = z[~dflt]
        ev.loc[i[~dflt], "depth_status"] = "free"
        ev.loc[i, "loc_src"] = "ANSS"
        moved = len(i)

    ev["gcmt_dt"], ev["gcmt_km"] = np.nan, np.nan
    free = ~ev["gcmt_id"].notna().to_numpy()
    used = set(ev["gcmt_id"].dropna())
    gf = g[~g["id"].isin(used)].reset_index(drop=True)
    dt, km, dm = C.MECH_WIN["gcmt"]
    q = S.one_to_one(S.pairs(h[free].reset_index(drop=True), gf, dt, km, dm), dt, km)
    r = np.flatnonzero(free)[q["ia"]]
    ev.loc[r, "gcmt_id"] = gf["id"].to_numpy()[q["ib"]]
    ev.loc[r, ["gcmt_dt", "gcmt_km"]] = q[["dt", "dkm"]].round(1).to_numpy()
    j = ev["gcmt_id"].map(gi)

    cr = rows[full(rows)].copy()
    cr["own"] = cr["id"].isin(ev["id"])
    cr = cr.sort_values(["grp", "own"], ascending=[True, False]).drop_duplicates("grp").set_index("grp")
    ev["cab_mech_id"] = ev["grp"].map(cr["id"])

    for col in S.SDR + S.MT:
        ev[col] = np.nan
    ev["mech_src"], ev["mech_type"] = None, None
    for src in C.MECH_ORDER:
        need = ev["mech_src"].isna().to_numpy()
        if src in ("anss", "gem"):
            d, q = hit[src]
            i, jj = q["ia"].to_numpy(), q["ib"].to_numpy()
            ok = need[i]
            i, jj = i[ok], jj[ok]
            ev.loc[i, S.SDR] = d[S.SDR].to_numpy(float)[jj]
            mt = [c for c in S.MT if c in d]
            ev.loc[i, mt] = d[mt].apply(pd.to_numeric, errors="coerce").to_numpy()[jj]
            ev.loc[i, "mech_type"] = d["mag_type"].to_numpy()[jj] if "mag_type" in d else None
        elif src == "gcmt":
            i = np.flatnonzero(need & j.notna().to_numpy())
            jj = j.to_numpy()[i].astype(int)
            ev.loc[i, S.SDR + S.MT] = g[S.SDR + S.MT].to_numpy(float)[jj]
            ev.loc[i, "mech_type"] = "gcmt"
        else:
            i = np.flatnonzero(need & ev["cab_mech_id"].notna().to_numpy())
            w = cr.loc[ev["grp"].to_numpy()[i]]
            ev.loc[i, S.SDR] = w[S.SDR].apply(pd.to_numeric, errors="coerce").to_numpy()
            ev.loc[i, "mech_type"] = w["agency"].to_numpy()
        ev.loc[i, "mech_src"] = src
    info = {"with_mech": int(ev["mech_src"].notna().sum()), "gcmt_located_to_anss": moved,
            "by_source": ev["mech_src"].value_counts().to_dict(),
            "found": {s: int(ev[c].notna().sum()) for s, c in
                      (("anss", "anss_id"), ("gcmt", "gcmt_id"), ("cabello", "cab_mech_id"), ("gem", "gem_id"))},
            "M>=5.5": {"events": int((ev["mag"] >= 5.5).sum()), "with_mech": int(ev.loc[ev["mag"] >= 5.5, "mech_src"].notna().sum())}}
    return ev, info


# overrides
# overrides.csv holds one decision per row (id, field, value, reason,
# reference). Fields other than mag change the Cabello row before the dedup,
# so a corrected time or location takes part in every match; mag is set on the
# final event (mag_src override, mag_cabello keeps the value before).
# additions.csv holds events missing from Cabello, with their reference.
def pre_overrides(x):
    for p in (C.OVERRIDES, C.ADDITIONS):
        print(f"[overrides] {p}: {'found' if p.exists() else 'NOT FOUND, nothing applied'}")
    o = pd.read_csv(C.OVERRIDES, dtype=str) if C.OVERRIDES.exists() else pd.DataFrame(columns=["id", "field", "value"])
    o = o[o["field"] != "mag"]
    x = x.copy()
    x["override"] = ""
    miss = sorted(set(o["id"]) - set(x["id"]))
    for _, r in o[o["id"].isin(x["id"])].iterrows():
        k = x.index[x["id"] == r["id"]]
        if r["field"] == "time_iso":
            t = pd.Timestamp(r["value"])
            x.loc[k, ["year", "month", "day", "hour", "minute", "second"]] = [t.year, t.month, t.day, t.hour, t.minute, t.second]
        else:
            num = pd.api.types.is_numeric_dtype(x[r["field"]])
            x.loc[k, r["field"]] = float(r["value"]) if num else r["value"]
        x.loc[k, "override"] += r["field"] + ";"
    if C.ADDITIONS.exists():
        a = pd.read_csv(C.ADDITIONS, dtype={"id": str})
        t = pd.to_datetime(a["time_iso"])
        a = a.assign(year=t.dt.year, month=t.dt.month, day=t.dt.day, hour=t.dt.hour, minute=t.dt.minute,
                     second=t.dt.second, mag=a["magnitude"], Mw_native=a["magnitude"], override="added")
        x = pd.concat([x, a.drop(columns=["time_iso", "reason"])], ignore_index=True)
    x = S.finish(x, S.stamp(x))
    return x, {"files": {str(p): p.exists() for p in (C.OVERRIDES, C.ADDITIONS)}, "row_overrides": int(((x["override"].str.len() > 0) & (x["override"] != "added")).sum()), "ids_not_found": miss,
               "added": int((x["override"] == "added").sum())}


def magnitudes(ev):
    """overrides.csv rows with field mag, applied to the final events (a group's magnitude may come from
    another row than the one named); mag_cabello keeps the value before."""
    o = pd.read_csv(C.OVERRIDES, dtype=str) if C.OVERRIDES.exists() else pd.DataFrame(columns=["id", "field", "value"])
    o = o[o["field"] == "mag"]
    ev = ev.copy()
    ev["mag_cabello"] = ev["mag"]
    kept = {m: k for k, d in zip(ev["id"], ev["dup_ids"].fillna("")) for m in d.split(";") if m}
    kept.update({k: k for k in ev["id"]})
    miss = []
    for _, r in o.iterrows():
        k = kept.get(r["id"])
        if k is None:
            miss.append(r["id"])
            continue
        ev.loc[ev["id"] == k, ["mag", "mag_src"]] = [float(r["value"]), "override"]
    return ev, {"mag_overrides": int((ev["mag_src"] == "override").sum()), "ids_not_found": miss}


# columns of catalog_base.csv (the stage tables in prepare/ keep everything)
BASE = ["id", "time_iso", "year", "longitude", "latitude", "depth", "depth_status", "depth_src",
        "mag", "mag_src", "mag_cabello", "Mw_native", "agency", "loc_src", "relocated", "n_rows", "dup_ids",
        "general_remarks", "reference", "override", "lon_orig", "lat_orig", "depth_orig",
        "gcmt_id", "anss_id", "anss_loc_id", "gem_id", "potin_id", "cab_mech_id", "mech_src", "mech_type",
        *S.SDR, *S.MT]


def main():
    C.PREP.mkdir(parents=True, exist_ok=True)
    log = {}
    x, g = S.cabello(), S.gcmt()
    log["read"] = {"lat_max": C.LAT_MAX, "cabello_rows_north_dropped": S.N_NORTH, "cabello_south_of_it": len(x), f"cabello_M>{C.MMIN}": int((x["mag"] > C.MMIN).sum()),
                   "gcmt": len(g)}
    x, log["overrides"] = pre_overrides(x)
    ev, grp, log["dedup"], rows = dedup(x, g)
    ev.to_csv(C.PREP / "01_dedup.csv", index=False)
    grp.to_csv(C.PREP / "01_dedup_groups.csv", index=False)
    log["dedup"]["by_mag"] = {f"M>={m}": [int((x["mag"] >= m).sum()), int((ev["mag"] >= m).sum())]
                              for m in (4.5, 5.0, 5.5, 6.0, 6.5, 7.0)}
    ev, log["locate"] = locate(ev, rows, S.potin(), g)
    ev.to_csv(C.PREP / "02_locate.csv", index=False)
    ev, log["mech"] = mech(ev, rows, g, S.anss(), S.gem())
    ev.to_csv(C.PREP / "03_mech.csv", index=False)
    ev, log["magnitudes"] = magnitudes(ev)
    ev[BASE].to_csv(C.OUT / "catalog_base.csv", index=False)
    (C.PREP / "prepare.json").write_text(json.dumps(log, indent=1, default=str))
    print(json.dumps(log, indent=1, default=str))
    return ev


if __name__ == "__main__":
    main()
"""Checks and figures of the classification (plan A7): the band around the slab surface measured on thrust events,
counts, the events with a literature class, the large events, the sensitivity to the settings, maps and sections.
Reads the catalogue of classify.CAT and classifies it again (no file of classify.py is needed)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import classify as C
from match import OUT, tsec

sys.path.insert(0, str(C.HERE.parent))
import palette  # noqa: E402

# settings
RUN = C.RUN
FIG = C.HERE / "figs" / "classify"
# figures of the paper and supplement go to FIGURES/classes; the other check figures stay in FIG
OFFICIAL, FIG_OUT = {"maps", "sections", "band", "nest", "sensitivity"}, C.HERE / "FIGURES" / "classes"
MMIN, BIG = 4.5, [4.5, 5.5, 7.0]
BEST = ["gccel", "ehb1"]
D_TOP = [(0, 20), (20, 35), (35, 50)]
D_LAT = [(17, 24), (24, 30), (30, 38), (38, 46)]
W_FIXED = [10.0, 15.0, 20.0]
TWO_THIRDS = 2 / 3
# comparisons
X4 = C.HERE.parent / "explore" / "X4" / "tables" / "x4b_events_m45.csv"
OLD = C.REPO / "results" / "cat_handler_2" / "frozen" / "2026-11-04" / "catalog.csv"
A6 = C.HERE / "overrides_A6.csv"
DT, DD, DT0, DD0 = 15.0, 100.0, 90.0, 300.0
BIG_PASS = [(6.0, 120.0), (7.0, 36 * 3600.0)]
OLD_FAM = {"slab_interface": "interface", "antarctic_interface": "interface", "intra_slab": "in-slab", "slab_deep": "in-slab",
           "deep_nest": "in-slab", "forearc": "crustal", "intraarc": "crustal", "backarc": "crustal", "patagonia_crustal": "crustal",
           "outer_rise": "outer rise"}
X4_FAM = {"interface": "interface", "in-slab": "in-slab", "crustal forearc": "crustal", "crustal arc": "crustal",
          "crustal backarc": "crustal", "crustal Patagonia": "crustal", "outer rise": "outer rise", "unknown depth": "unknown depth"}
THRUST_MMIN = 6.5
# depth σ against the scatter of the thrust events: groups (depth source, offshore) with at least SIG_N events
SIG_N = 15
# figures
SECTIONS = [-20.0, -23.0, -27.0, -31.0, -33.5, -37.0]
STRIP, XLIM, ZMAX = 50.0, (-60.0, 400.0), 250.0
EXTENT = [-80, -62, -58, -16]
PANELS = [("Interface", ["interface", "antarctic_interface"]), ("In-slab", ["intraslab_shallow", "intraslab_intermediate", "jujuy_nest"]),
          ("Crustal: forearc and arc", ["forearc", "arc"]), ("Crustal: backarc and Patagonia", ["backarc", "patagonia"]),
          ("Outer rise", ["outer_rise"]), ("Shared between classes", ["split"])]
NEST_BOX, NEST_Z = 2.5, (100.0, 400.0)


def m45(g):
    return (g.in_domain & (g.mw >= MMIN - 0.05)).to_numpy()


def show(o):
    """One label per event for the figures: the sub-class of the class with weight 1, else split."""
    return np.select([o.cls == "interface", o.cls == "in-slab", o.cls == "crustal", o.cls == "outer rise", o.cls == "unclassified"],
                     [o.sub_interface, o.sub_inslab, o.sub_crustal, "outer_rise", "unclassified"], "split")


# 0 the Slab2 grids
def grids(g):
    import shapely
    c = shapely.get_coordinates(C.geoms(C.TRENCH))
    c = c[(c[:, 1] > -45) & (c[:, 1] < -18)]
    t = C.slab_at(c[:, 0], c[:, 1])[0]
    x = g[m45(g) & g.top.notna()]
    rows = [{"quantity": "slab top on the Nazca trench line, 18–45° S (km)", "n": int(np.isfinite(t).sum()), "median": np.nanmedian(t),
             "p10": np.nanpercentile(t, 10), "p90": np.nanpercentile(t, 90)}]
    for lab, k in (("slab top", x.top), ("thickness", x.thk), ("dip", x.dip), ("depth uncertainty", x.unc),
                   ("depth uncertainty, slab top ≤ 20 km", x.unc[x.top <= 20]), ("depth uncertainty, slab top 20–50 km", x.unc[(x.top > 20) & (x.top <= 50)]),
                   ("depth uncertainty, slab top 50–100 km", x.unc[(x.top > 50) & (x.top <= 100)]), ("depth uncertainty, slab top > 100 km", x.unc[x.top > 100])):
        rows.append({"quantity": f"{lab} at the epicentres, Mw ≥ {MMIN}", "n": int(k.notna().sum()), "median": k.median(), "p10": k.quantile(0.1), "p90": k.quantile(0.9)})
    d = np.linspace(0, 300, 7)
    rows.append({"quantity": "correlation of slab top with distance from the trench (events east of it)", "n": int((~x.sea).sum()),
                 "median": np.corrcoef(x.d_trench[~x.sea], x.top[~x.sea])[0, 1]})
    return pd.DataFrame(rows).round(2)


# 1 band measurement
def band(g, hint_if):
    """
    Distance d of the events that are interface without their depth (thrust on the plate contact; interface by the
    literature) from the Slab2 surface, against the Slab2 depth uncertainty.

    Returns the table (per depth quality, latitude band and slab-top range) and the reference events.
    """
    k = m45(g) & g.known & ~g.sea & g.top.notna() & (g.top <= C.IF_TOP)
    ref = k & ((g.mech_kind == "thrust") | hint_if)
    oth = k & (g.mech_kind == "other")
    best = g.depth_src.isin(BEST).to_numpy()
    rows = []

    def row(group, sub, q):
        x = g[q]
        d, a = x.d.to_numpy(), np.abs(x.d.to_numpy())
        if len(x) < 5:
            return
        sd = 1.4826 * np.median(np.abs(d - np.median(d)))
        rows.append({"events": group, "subset": sub, "n": len(x), "median_d": np.median(d), "robust_sd": sd, "sd": np.std(d),
                     "median_sigma": x.sig.median(), "sd_without_sigma": np.sqrt(max(sd ** 2 - np.mean(x.sig ** 2), 0)),
                     "half_width_68": np.percentile(a, 68), "half_width_90": np.percentile(a, 90), "median_unc": x.unc.median(),
                     "within_unc": np.mean(a <= x.unc), "within_unc_plus_sigma": np.mean(a <= x.unc + x.sig),
                     **{f"within_{w:g}": np.mean(a <= w) for w in W_FIXED}})

    for group, q in (("thrust on the contact, all depths", ref), ("thrust on the contact, best depths", ref & best),
                     ("thrust on the contact, other depths", ref & ~best), ("other mechanisms, all depths", oth),
                     ("other mechanisms, best depths", oth & best)):
        row(group, "all", q)
        for a, b in D_LAT:
            row(group, f"{a}–{b}° S", q & (g.lat <= -a).to_numpy() & (g.lat > -b).to_numpy())
        for a, b in D_TOP:
            row(group, f"slab top {a}–{b} km", q & (g.top > a).to_numpy() & (g.top <= b).to_numpy())
        for s in sorted(g.depth_src[q].dropna().unique()):
            row(group, f"depth from {s}", q & (g.depth_src == s).to_numpy())
    return pd.DataFrame(rows).round(3), ref, oth, best


# 2 counts
def counts(g, o):
    k, mw = m45(g), g.mw.to_numpy()
    rows = []
    fam = [("interface", "w_interface", "sub_interface"), ("in-slab", "w_inslab", "sub_inslab"), ("crustal", "w_crustal", "sub_crustal")]
    for m in BIG:
        q = k & (mw >= m - 0.05)
        x = o[q]
        r = {"mmin": m, "events": int(q.sum())}
        for nm, w, s in fam:
            r[nm] = x[w].sum()
            for sub, v in x.groupby(s)[w].sum().items():
                if sub:
                    r[f"{nm}: {sub}"] = v
        r.update({"outer rise": x.w_outer_rise.sum(), "unclassified": x.w_unclassified.sum(), "weight 1": int((x.cls != "split").sum()),
                  "split, near the band": int((x.rule == "depth_split").sum()), "split, no depth": int(((x.rule == "nodepth_share") & (x.cls == "split")).sum()),
                  "no depth, by position": int(x.rule.isin(["nodepth_deep", "nodepth_no_slab"]).sum() + ((x.rule == "nodepth_share") & (x.cls != "split")).sum()),
                  "literature class": int((x.rule == "hint").sum()), "below the plate (in-slab)": int((g.d[q] > g.thk[q]).sum())})
        rows.append(r)
    return pd.DataFrame(rows).set_index("mmin").T.round(1)


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


def old_class(x):
    """Family of the old classifier (frozen catalogue of 2026-11-04) for the events x, matched by time and distance
    with two wider passes for large events (the old catalogue carries centroid times and dates a day off)."""
    o = pd.read_csv(OLD, low_memory=False)
    o = o[o.mag >= MMIN].reset_index(drop=True)
    a = (tsec(x.time), x.lat.to_numpy(), x.lon.to_numpy(), tsec(o.time_iso), o.latitude.to_numpy(), o.longitude.to_numpy())
    j = match(*a)
    for mmin, dt in BIG_PASS:
        free = np.ones(len(o), bool)
        free[j[j >= 0]] = False
        j2 = match(*a, dt=np.where((j < 0) & (x.mw.to_numpy() >= mmin), dt, np.nan), dd=np.full(len(x), DD0), free=free & (o.mag.to_numpy() >= mmin - 1))
        j = np.where(j >= 0, j, j2)
    out = np.full(len(x), "not in the old catalogue", object)
    out[j >= 0] = o["class"].map(OLD_FAM).fillna("no family (unresolved, below slab, no slab)").to_numpy()[j[j >= 0]]
    return out


def compare(g, o):
    k = m45(g)
    x, y = g[k].reset_index(drop=True), o[k].reset_index(drop=True)
    y["old"] = old_class(x)
    x4 = pd.read_csv(X4, usecols=["event_id", "cls"]).set_index("event_id").cls
    y["x4"] = x.event_id.map(x4).map(X4_FAM).fillna(x.event_id.map(x4).notna().map({True: "unclassified", False: "not in the X4 run"})).to_numpy()
    rows = []
    for src in ("old", "x4"):
        for m in BIG:
            q = (x.mw >= m - 0.05).to_numpy()
            t = y[q].groupby(src)[C.COLS].sum()
            t["events"], t["split"] = y[q].groupby(src).size(), y[q & (y.cls == "split")].groupby(src).size()
            t["same class, weight 1"] = [int(((y.cls == f) & (y[src] == f) & q).sum()) if f in C.CLS else np.nan for f in t.index]
            rows.append(t.reset_index(names="earlier class").assign(against="old classifier (2026-11-04)" if src == "old" else "X4 baseline (run 2026-11-13b)", mmin=m))
    t = pd.concat(rows, ignore_index=True).fillna({"split": 0})
    return t[["against", "mmin", "earlier class", "events"] + C.COLS + ["split", "same class, weight 1"]].round(1), y[["old", "x4"]].set_index(x.event_id)


# 3 named events
def named(g, o):
    a = pd.read_csv(A6, dtype=str)
    a = a[(a.property == "class_hint") & (a.status == "accepted")].set_index("event_id")
    k = (o.rule == "hint").to_numpy()
    x = g[k][["event_id", "time", "lon", "lat", "mw", "z", "sig", "depth_src", "top", "unc", "d", "mech_kind", "zone", "d_trench", "sea"]].copy()
    y = o[k]
    x["name"] = x.event_id.map(a.reason).str.split(":").str[0]
    x["reference"] = x.event_id.map(a.reference)
    x["literature"], x["rules_alone"] = y.cls.to_numpy(), y.cls_auto.to_numpy()
    for c in ("a_interface", "a_inslab", "a_crustal", "a_outer_rise"):
        x[c] = y[c].to_numpy()
    nodepth = ~g.known[k].to_numpy() & ~g.sea[k].to_numpy()
    x["verdict"] = np.where(x.rules_alone == x.literature, "right", np.where(nodepth, "no depth", np.where(x.rules_alone == "split", "split", "wrong")))
    x["depth_assigned"] = y.depth_assigned.to_numpy()
    return x.sort_values("time").round(2)


# 4 large events
def large(g, o, m=7.0):
    k = m45(g) & (g.mw >= m - 0.05).to_numpy()
    x = g[k][["event_id", "time", "lon", "lat", "mw", "z", "sig", "depth_src", "top", "d", "mech_kind"]].copy()
    y = o[k]
    x["depth_kind"] = np.where(g.known[k], "measured", np.where(y.depth_assigned.notna(), "assigned", "unknown"))
    for c in C.COLS + ["cls", "cls_auto", "rule", "W", "sub_interface", "sub_inslab", "sub_crustal", "depth_assigned"]:
        x[c] = y[c].to_numpy()
    return x.sort_values("time").round(2)


# 5 sensitivity
def sensitivity(g, base):
    k, mw = m45(g), g.mw.to_numpy()
    var = {f"baseline (W = {C.W:g} km, hardening 0.8, interface to 50 km, mechanism misfit)": {},
           "W = Slab2 depth uncertainty": {"w": "unc"}, **{f"W = {w:g} km": {"w": w} for w in W_FIXED if w != C.W},
           "hardening 0.7": {"hard": 0.7}, "hardening 0.9": {"hard": 0.9}, "no hardening": {"hard": None},
           "interface down to a slab top of 60 km": {"if_top": 60.0},
           "mechanisms not used": {"mech": "scores"},
           "rules of run 2026-11-13j (depth band, a thrust decides)": {"mech": "add"}}
    P0 = base[C.COLS].to_numpy()
    rows, ch = [], {}
    for name, kw in var.items():
        o = C.classify(g, **kw)[0]
        P = o[C.COLS].to_numpy()
        r = {"variant": name}
        for m in BIG[:2]:
            q = k & (mw >= m - 0.05)
            r.update({f"interface, Mw ≥ {m:g}": P[q, 0].sum(), f"in-slab, Mw ≥ {m:g}": P[q, 1].sum(), f"crustal, Mw ≥ {m:g}": P[q, 2].sum()})
        dom = np.argmax(P, 1) != np.argmax(P0, 1)
        r.update({"split events, Mw ≥ 4.5": int((k & (o.cls == "split")).sum()), "split events, Mw ≥ 5.5": int((k & (mw >= 5.45) & (o.cls == "split")).sum()),
                  "split near the band, Mw ≥ 4.5": int((k & (o.rule == "depth_split")).sum())})
        for m in BIG:
            q = k & (mw >= m - 0.05)
            r[f"largest class changes, Mw ≥ {m:g}"] = int((q & dom).sum())
            r[f"a weight changes by 0.2 or more, Mw ≥ {m:g}"] = int((q & (np.abs(P - P0).max(1) >= 0.2)).sum())
        ch[name] = k & (mw >= 6.95) & (np.abs(P - P0).max(1) >= 0.2)
        rows.append(r)
    # events without depth left out of the class sums
    q0 = base.rule.to_numpy() != "nodepth_share"
    r = {"variant": "events without depth that take the bin shares left out"}
    for m in BIG[:2]:
        q = k & (mw >= m - 0.05) & q0
        r.update({f"interface, Mw ≥ {m:g}": P0[q, 0].sum(), f"in-slab, Mw ≥ {m:g}": P0[q, 1].sum(), f"crustal, Mw ≥ {m:g}": P0[q, 2].sum()})
    r.update({"split events, Mw ≥ 4.5": int((k & q0 & (base.cls == "split")).sum()), "split events, Mw ≥ 5.5": int((k & q0 & (mw >= 5.45) & (base.cls == "split")).sum()),
              "split near the band, Mw ≥ 4.5": int((k & (base.rule == "depth_split")).sum())})
    for m in BIG:
        r[f"largest class changes, Mw ≥ {m:g}"] = int((k & (mw >= m - 0.05) & ~q0).sum())
    rows.append(r)
    t = pd.DataFrame(rows).round(1)
    big = pd.DataFrame({n: v for n, v in ch.items() if v.any()}, index=g.index)
    big = g[["event_id", "time", "mw"]].join(big)[big.any(axis=1)]
    return t, big


# blind test
def blind(g):
    """
    The depth rule tested on the events whose mechanism tells the answer.

    Events over the shallow slab with a measured depth and a mechanism are classified without their mechanism. A thrust
    on the plate contact counts as interface, another mechanism as not interface. Per band width and hardening: the
    mean interface weight of each group, the summed interface weight over the number of thrusts (1 = unbiased total),
    and the Brier score (mean squared error of the interface weight; base_rate is the score of giving every event the
    share of thrusts). Subsets for the baseline width.
    """
    k = m45(g) & g.known.to_numpy() & ~g.sea.to_numpy() & ~g.an.to_numpy() & (g.top <= C.IF_TOP).to_numpy()
    thr, oth = k & (g.mech_kind == "thrust").to_numpy(), k & (g.mech_kind == "other").to_numpy()
    m = thr | oth
    off, mw, lat, top = g.offshore.to_numpy(bool), g.mw.to_numpy(), g.lat.to_numpy(), g.top.to_numpy()
    sub = {"all": m, "offshore": m & off, "onshore": m & ~off, "Mw < 5.5": m & (mw < 5.45), "Mw ≥ 5.5": m & (mw >= 5.45),
           "17–24° S": m & (lat > -24), "24–30° S": m & (lat <= -24) & (lat > -30), "30–38° S": m & (lat <= -30) & (lat > -38),
           "slab top ≤ 20 km": m & (top <= 20), "slab top 20–50 km": m & (top > 20)}
    rows = []
    for w in ["unc"] + W_FIXED:
        for hard in (0.8, None):
            wi = C.classify(g, w=w, hard=hard, mech="none")[0].w_interface.to_numpy()
            for nm, q in sub.items():
                if nm != "all" and (hard is None or w not in ("unc", 15.0)):
                    continue
                p = thr[q].mean()
                rows.append({"W": w, "hardening": "none" if hard is None else hard, "subset": nm, "events": int(q.sum()), "thrusts": int((thr & q).sum()),
                             "interface_weight_thrusts": wi[thr & q].mean(), "interface_weight_others": wi[oth & q].mean(),
                             "summed_weight_over_thrusts": wi[q].sum() / (thr & q).sum(), "brier": np.mean((wi[q] - thr[q]) ** 2), "brier_base_rate": p * (1 - p)})
    h = g[g.hint.notna() & (g.mech_kind != "none")]
    return pd.DataFrame(rows).round(3), pd.crosstab(h.hint, h.mech_kind)


# depth σ
def rsd(v):
    return 1.4826 * np.median(np.abs(v - np.median(v)))


def sigma_check(g, o):
    """
    The depth σ of the catalogue against the scatter of the thrust events about the Slab2 surface, per depth source
    and offshore flag, and the classification under other σ.

    The scatter holds the depth error, the error of Slab2 and thrusts off the contact, so it is an upper bound of σ.
    Variants: the tabled σ of A4 without the offshore floor, and σ set to the measured scatter per depth source and
    offshore flag (not independent: the same events are then classified).

    Returns the table per group and the table of variants.
    """
    import locate as L
    k = m45(g)
    shallow = k & g.known.to_numpy() & ~g.sea.to_numpy() & (g.top <= C.IF_TOP).to_numpy()
    ref = shallow & (g.mech_kind == "thrust").to_numpy()
    z, key, old, off = g.z.to_numpy(float), g.depth_src.to_numpy(object), (g.yr < L.OLD_BEFORE).to_numpy(), g.offshore.to_numpy(bool)
    s0 = np.maximum(L.sigma(key, z, np.zeros(len(g), bool), old)[0], C.SIG_MIN)
    rows, meas = [], g.sig.to_numpy(float).copy()
    for of in (True, False):
        for src in ["all"] + sorted(g.depth_src[ref].dropna().unique()):
            q = (off == of) & ((g.depth_src == src).to_numpy() | (src == "all"))
            x = g[ref & q]
            if len(x) < SIG_N:
                continue
            v = rsd(x.d.to_numpy())
            if src != "all":
                meas[q & g.known.to_numpy()] = v
            rows.append({"offshore": of, "depth_src": src, "thrust_events": len(x), "median_d": x.d.median(), "scatter": v,
                         "sigma": x.sig.median(), "sigma_tabled": np.median(s0[ref & q]), "scatter_over_sigma": rsd((x.d / x.sig).to_numpy()),
                         "within_sigma": np.mean(np.abs(x.d - x.d.median()) <= x.sig), "events_shallow_slab": int((shallow & q).sum())})
    var = {"depth σ of the catalogue (baseline)": g.sig.to_numpy(float), "tabled σ, minimum 5 km": s0,
           "σ = scatter per depth source and offshore flag": meas}
    out = []
    for name, sg in var.items():
        for hard in (C.HARD, 0.7):
            y = C.classify(g.assign(sig=np.where(g.known, sg, np.nan)), hard=hard)[0][k]
            t = y[ref[k]]
            out.append({"depth σ": name, "hardening": hard, "interface": y.w_interface.sum(), "in-slab": y.w_inslab.sum(), "crustal": y.w_crustal.sum(),
                        "interface, Mw ≥ 5.5": y.w_interface[(g.mw[k] >= 5.45).to_numpy()].sum(), "split events": int((y.cls == "split").sum()),
                        "split near the band": int((y.rule == "depth_split").sum()), "thrusts at interface 1": int((t.cls == "interface").sum()),
                        "thrusts split": int((t.cls == "split").sum()), "thrusts in another class": int((~t.cls.isin(["interface", "split"])).sum())})
    return pd.DataFrame(rows).round(2), pd.DataFrame(out).round(1)


# jujuy nest
def nest(g):
    n = C.NEST
    r = np.hypot((g.lon - n["lon"]) * np.cos(np.radians(g.lat)), g.lat - n["lat"]).to_numpy()
    z = g.z.to_numpy()
    k = m45(g) & g.known.to_numpy()
    inz, inr = (z >= n["depth"][0]) & (z <= n["depth"][1]), r <= n["radius_deg"]
    rows = [("inside the circle and the depth range (the nest)", k & inr & inz),
            ("inside the circle, 20 km above the range", k & inr & (z >= n["depth"][0] - 20) & (z < n["depth"][0])),
            ("inside the circle, 20 km below the range", k & inr & (z > n["depth"][1]) & (z <= n["depth"][1] + 20)),
            ("in the depth range, 0.8–1.0° from the centre", k & inz & (r > n["radius_deg"]) & (r <= 1.0)),
            ("in the depth range, 1.0–1.5° from the centre", k & inz & (r > 1.0) & (r <= 1.5)),
            ("in the depth range, 1.5–2.5° from the centre", k & inz & (r > 1.5) & (r <= 2.5))]
    t = pd.DataFrame([{"where": a, "events": int(q.sum()), "Mw ≥ 5.5": int((q & (g.mw >= 5.45).to_numpy()).sum()),
                       "per 1000 km²": q.sum() / ar * 1000} for (a, q), ar in zip(rows, np.pi * 111.195 ** 2 * np.array(
                           [0.64, 0.64, 0.64, 1.0 - 0.64, 1.5 ** 2 - 1.0, 2.5 ** 2 - 1.5 ** 2]))])
    x = g[k & inr & inz]
    info = {"median lon": x.lon.median(), "median lat": x.lat.median(), "median depth": x.z.median(), "depth p2": x.z.quantile(0.02), "depth p98": x.z.quantile(0.98),
            "radius p95 (deg)": float(np.percentile(r[k & inr & inz], 95))}
    return t.round(2), info, r


# figures
def new(nr, nc, w, h, **kw):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    palette.apply()
    return plt.subplots(nr, nc, figsize=(w, h), layout="constrained", squeeze=False, **kw)


def save(fig, name, dpi=160, **kw):
    import matplotlib.pyplot as plt
    d = FIG_OUT if name in OFFICIAL else FIG
    d.mkdir(parents=True, exist_ok=True)
    fig.savefig(d / f"{name}.png", dpi=dpi, **kw)
    plt.close(fig)


def size(m):
    return np.clip(np.nan_to_num(m, nan=4.5) - 3.5, 0.5, 6) ** 2 * 4


def fig_band(g, ref, oth, best):
    fig, ax = new(1, 2, 14.5, 5.6)
    b = np.arange(-50, 51, 2.5)
    a = ax[0, 0]
    a.hist(g.d[oth], b, color="0.75", label=f"other mechanisms ({oth.sum()})")
    a.hist(g.d[ref], b, color=palette.CLASS_COLOR["interface"], alpha=0.85, label=f"thrust on the plate contact ({ref.sum()})")
    a.hist(g.d[ref & best], b, color="#08306b", label=f"of these, calibrated or depth-phase depths ({(ref & best).sum()})")
    u = g.unc[ref].median()
    for s in (-1, 1):
        a.axvline(s * u, color=palette.INK, lw=1, ls="--", label=f"± median Slab2 depth uncertainty ({u:.0f} km)" if s > 0 else None)
    if C.W != "unc":
        for s in (-1, 1):
            a.axvline(s * C.W, color="#e6550d", lw=1.2, label=f"interface band, ± {C.W:g} km" if s > 0 else None)
    a.axvline(0, color=palette.INK, lw=0.8)
    a.set_xlabel("event depth − Slab2 surface [km] (positive: below the surface)")
    a.set_ylabel("events")
    a.set_title(f"Slab top ≤ {C.IF_TOP:.0f} km, Mw ≥ {MMIN}, measured depths")
    a.legend(loc="upper left", fontsize=9)
    a = ax[0, 1]
    x = g[ref]
    a.scatter(x.top, x.d, s=size(x.mw) * 0.5, color=np.where(best[ref], "#08306b", palette.CLASS_COLOR["interface"]), alpha=0.6, lw=0)
    e = np.arange(5, 51, 5.0)
    i = np.digitize(x.top, e)
    mid, med, un = [], [], []
    for j in range(1, len(e)):
        if (i == j).sum() >= 10:
            mid.append((e[j - 1] + e[j]) / 2), med.append(x.d[i == j].median()), un.append(x.unc[i == j].median())
    a.plot(mid, med, color="#e6550d", lw=2, marker="o", label="median of the thrust events")
    a.plot(mid, un, color=palette.INK, lw=1, ls="--", label="± Slab2 depth uncertainty (median)")
    a.plot(mid, -np.array(un), color=palette.INK, lw=1, ls="--")
    a.axhline(0, color=palette.INK, lw=0.8)
    a.set_ylim(40, -40)
    a.set_xlabel("Slab2 surface at the epicentre [km]")
    a.set_ylabel("event depth − Slab2 surface [km]")
    a.set_title("Thrust events against the depth of the surface")
    a.legend(loc="lower left", fontsize=9)
    save(fig, "band")


def fig_maps(g, o):
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    import shapely
    from pituplots.maps import dress_map
    palette.apply()
    k = m45(g)
    x = g[k].assign(show=show(o[k]), rule=o.rule[k]).sort_values("mw")
    tr = [shapely.get_coordinates(C.geoms(f)) for f in (C.TRENCH, C.TRENCH_AN)]
    arc = shapely.get_coordinates(shapely.boundary(C.geoms(C.ARC)))
    fig = plt.figure(figsize=(19, 8.8), layout="constrained")
    for j, (title, keys) in enumerate(PANELS):
        ax = fig.add_subplot(1, len(PANELS), j + 1, projection=ccrs.PlateCarree())
        dress_map(ax, EXTENT, coastline=True, gridlines=j == 0)
        for c in tr:
            ax.plot(c[:, 0], c[:, 1], color="0.35", lw=0.8, transform=ccrs.PlateCarree())
        ax.plot(arc[:, 0], arc[:, 1], color="0.55", lw=0.6, ls="--", transform=ccrs.PlateCarree())
        for key in keys:
            for lab, q in ((("near the band", x.rule == "depth_split"), ("no depth", x.rule == "nodepth_share")) if key == "split" else (("", x.mw > 0),)):
                y = x[(x.show == key) & q]
                ax.scatter(y.lon, y.lat, s=size(y.mw) * 0.6, color=palette.CLASS_COLOR[key] if lab != "no depth" else "#d0d0d0", lw=0.2, edgecolor="white",
                           alpha=0.8, transform=ccrs.PlateCarree(), rasterized=True, zorder=3,
                           label=f"{palette.CLASS_NAME[key] if not lab else lab}\n{len(y):,} events, {(y.mw >= 6.95).sum()} of Mw ≥ 7")
        ax.set_title(title, fontsize=12)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.03), fontsize=9, markerscale=0.8)
    fig.suptitle(f"Tectonic classes, Mw ≥ {MMIN} (lines: trenches; dashed: arc polygon)", x=0.01, ha="left")
    save(fig, "maps", dpi=150, bbox_inches="tight")


def trench_line():
    import shapely.ops
    t = C.geoms(C.TRENCH)
    t = shapely.ops.linemerge(t) if t.geom_type != "LineString" else t
    return max(t.geoms, key=lambda q: q.length) if t.geom_type != "LineString" else t


def fig_sections(g, o):
    import matplotlib.pyplot as plt
    from pituplots.io import read_slab2
    from pituplots.sections import add_slab, profiles_from_line, project, sample, unproject
    palette.apply()
    top, thk, unc = (read_slab2(C.SLAB / f"sam_slab2_{q}_{C.SLAB_V}.xyz") for q in ("dep", "thk", "unc"))
    k = m45(g)
    x = g[k].assign(show=show(o[k])).sort_values("mw").reset_index(drop=True)
    prof = profiles_from_line(trench_line(), SECTIONS, width=2 * STRIP, side=(-60, -30), length=XLIM)
    fig, axs = plt.subplots(len(SECTIONS), 1, figsize=(12, 6.9 * len(SECTIONS)), layout="constrained")
    for ax, p, lat in zip(axs, prof, SECTIONS):
        u, v = project(x.lon.to_numpy(), x.lat.to_numpy(), p)
        q = (np.abs(v) <= STRIP) & (u >= XLIM[0]) & (u <= XLIM[1])
        kn, z, m = x.known.to_numpy(), x.z.to_numpy(), x.mw.to_numpy()
        for key in [c for c in palette.CLASS if ((x.show == c).to_numpy() & q & kn).any()]:
            j = q & kn & (x.show == key).to_numpy()
            ax.scatter(u[j], z[j], s=size(m[j]), color=palette.CLASS_COLOR[key], alpha=0.8, lw=0.3, edgecolor="white",
                       label=f"{palette.CLASS_NAME[key]} ({j.sum()})", zorder=3)
        j = q & ~kn
        if j.any():
            ax.scatter(u[j], np.full(j.sum(), -8.0), s=14, marker="v", color=[palette.CLASS_COLOR[c] for c in x.show[j]], lw=0,
                       label=f"no measured depth ({j.sum()})", clip_on=False, zorder=3)
        for i in np.flatnonzero(q & kn & (m >= 6.95)):
            ax.annotate(f"M {m[i]:.1f}", (u[i], z[i]), fontsize=9, xytext=(4, 4), textcoords="offset points", zorder=5)
        add_slab(ax, p, top, thk)
        sx = np.arange(XLIM[0], XLIM[1], 5.0)
        lo, la = unproject(sx, sx * 0, p)
        zt, zu = np.abs(sample(top, lo, la)), sample(unc, lo, la) if C.W == "unc" else C.W
        for sg in (-1, 1):
            ax.plot(sx, np.where(zt <= C.IF_TOP, zt + sg * zu, np.nan), color="0.3", lw=0.7, ls=":", zorder=4)
        ax.set_xlim(*XLIM)
        ax.set_ylim(ZMAX, -12)
        ax.set_aspect(1)
        ax.set_ylabel("depth [km]")
        ax.set_title(f"{-lat:.1f}° S, {STRIP:.0f} km either side, Mw ≥ {MMIN} (dotted: interface band)")
        ax.legend(loc="lower left", ncol=3, fontsize=9)
    axs[-1].set_xlabel("distance from the trench [km]")
    save(fig, "sections", dpi=130)


def fig_sensitivity(t):
    fig, ax = new(1, 2, 15, 6.2, sharey=True)
    y = np.arange(len(t) - 1)[::-1]
    col = [palette.CLASS_COLOR[c] for c in ("interface", "intraslab_intermediate", "forearc")]
    for a, m in zip(ax[0], BIG[:2]):
        for i, (nm, c) in enumerate(zip(("interface", "in-slab", "crustal"), col)):
            v = t[f"{nm}, Mw ≥ {m:g}"].to_numpy()
            a.barh(y + 0.27 * (1 - i), 100 * (v[1:] / v[0] - 1), height=0.25, color=c, label=nm)
        a.axvline(0, color=palette.INK, lw=0.8)
        a.set_xlabel("summed weight against the baseline [%]")
        a.set_title(f"Mw ≥ {m:g}")
    ax[0, 0].set_yticks(y, t.variant[1:], fontsize=10)
    ax[0, 0].legend(loc="lower right")
    fig.suptitle("Class totals under other settings of the rules", x=0.01, ha="left")
    save(fig, "sensitivity")


def fig_nest(g, r):
    n = C.NEST
    fig, ax = new(1, 3, 16, 5.4)
    k = m45(g) & g.known.to_numpy() & (np.abs(g.lon - n["lon"]) <= NEST_BOX).to_numpy() & (np.abs(g.lat - n["lat"]) <= NEST_BOX).to_numpy()
    x, rr = g[k], r[k]
    deep = (x.z >= NEST_Z[0]).to_numpy()
    inz = ((x.z >= n["depth"][0]) & (x.z <= n["depth"][1])).to_numpy()
    a = ax[0, 0]
    a.scatter(x.lon[deep & ~inz], x.lat[deep & ~inz], s=6, color="0.7", lw=0, label="other depths below 100 km")
    a.scatter(x.lon[inz], x.lat[inz], s=size(x.mw[inz]) * 0.5, color=palette.CLASS_COLOR["jujuy_nest"], alpha=0.6, lw=0, label=f"{n['depth'][0]:.0f}–{n['depth'][1]:.0f} km")
    th = np.linspace(0, 2 * np.pi, 200)
    a.plot(n["lon"] + n["radius_deg"] * np.cos(th) / np.cos(np.radians(n["lat"])), n["lat"] + n["radius_deg"] * np.sin(th), color=palette.INK, lw=1.2)
    a.set_xlabel("longitude"), a.set_ylabel("latitude"), a.set_title("Epicentres and the nest circle"), a.legend(loc="lower left", fontsize=9)
    a = ax[0, 1]
    a.hist(x.z[(rr <= n["radius_deg"]) & deep], np.arange(100, 401, 10), color=palette.CLASS_COLOR["jujuy_nest"], label="inside the circle")
    a.hist(x.z[(rr > n["radius_deg"]) & (rr <= 2 * n["radius_deg"]) & deep], np.arange(100, 401, 10), color="0.6", histtype="step", lw=1.5, label="ring out to twice the radius")
    for v in n["depth"]:
        a.axvline(v, color=palette.INK, lw=1.2, ls="--")
    a.set_xlabel("depth [km]"), a.set_ylabel("events"), a.set_title("Depths (dashed: limits)"), a.legend(fontsize=9)
    a = ax[0, 2]
    e = np.arange(0, 2.51, 0.1)
    h = np.histogram(rr[inz], e)[0] / (np.pi * (e[1:] ** 2 - e[:-1] ** 2) * 111.195 ** 2) * 1000
    a.step(e[:-1], h, where="post", color=palette.CLASS_COLOR["jujuy_nest"], lw=1.8)
    a.axvline(n["radius_deg"], color=palette.INK, lw=1.2, ls="--")
    a.set_xlabel("distance from the centre [°]"), a.set_ylabel("events per 1000 km²"), a.set_title("Density in the depth range (dashed: radius)")
    fig.suptitle(f"Jujuy nest, Mw ≥ {MMIN}, measured depths", x=0.01, ha="left")
    save(fig, "nest")


def main():
    pd.set_option("display.width", 250, "display.max_columns", 40, "display.max_rows", 400, "display.max_colwidth", 70)
    c = pd.read_csv(OUT / f"catalog_{C.CAT}.csv", low_memory=False)
    g, o, tab = C.run(c)
    k = m45(g)
    # 7 weights add to 1, every event has a row
    assert len(o) == len(c) and o.event_id.is_unique and set(o.event_id) == set(c.event_id)
    assert np.allclose(o[C.COLS].sum(axis=1), 1, atol=2e-4) and (o[C.COLS] >= 0).all().all() and (o.rule != "").all()
    f = OUT / f"classes_{RUN}.csv"
    if f.exists():
        assert pd.read_csv(f, usecols=["event_id", "cls"]).equals(o[["event_id", "cls"]].reset_index(drop=True)), "classes file is of another run"
    gr = grids(g)
    bt, ref, oth, best = band(g, (g.hint == "interface").to_numpy())
    cnt = counts(g, o)
    cmp_, earlier = compare(g, o)
    nm = named(g, o)
    m7 = large(g, o)
    sens, big = sensitivity(g, o)
    nt, ninfo, r = nest(g)
    sg, sgv = sigma_check(g, o)
    bl, blh = blind(g)
    thr = g[k & (g.mech_kind == "thrust") & (g.mw >= THRUST_MMIN - 0.05) & (o.w_interface < 0.5)][
        ["event_id", "time", "lon", "lat", "mw", "z", "sig", "depth_src", "top", "unc", "d"]].join(o[C.COLS + ["cls", "rule"]]).round(2)
    files = {OUT / f"class_grids_{RUN}.csv": gr, OUT / f"class_band_{RUN}.csv": bt, OUT / f"class_counts_{RUN}.csv": cnt.reset_index(names="quantity"),
             OUT / f"class_compare_{RUN}.csv": cmp_, OUT / f"class_named_{RUN}.csv": nm, OUT / f"class_m7_{RUN}.csv": m7,
             OUT / f"class_sensitivity_{RUN}.csv": sens, OUT / f"class_nest_{RUN}.csv": nt,
             OUT / f"class_sigma_{RUN}.csv": sg, OUT / f"class_sigma_variants_{RUN}.csv": sgv, OUT / f"class_blind_{RUN}.csv": bl,
             OUT / "review" / f"class_m7_sensitive_{RUN}.csv": big, OUT / "review" / f"class_thrust_not_interface_{RUN}.csv": thr}
    for p, d in files.items():
        d.to_csv(p, index=False)
    C.manifest(files)
    fig_band(g, ref, oth, best)
    fig_maps(g, o)
    fig_sections(g, o)
    fig_sensitivity(sens)
    fig_nest(g, r)
    print(gr.to_string())
    print(bt.to_string())
    print(cnt.to_string())
    print(o[k].groupby("rule")[C.COLS].sum().round(1).assign(events=o[k].groupby("rule").size()).to_string())
    print(cmp_.to_string())
    print(nm.verdict.value_counts().to_dict())
    print(nm[nm.verdict.isin(["wrong", "split"])][["name", "time", "mw", "z", "sig", "top", "unc", "d", "mech_kind", "literature", "rules_alone", "a_interface",
                                                    "a_inslab", "a_crustal", "a_outer_rise", "verdict"]].to_string())
    print(m7[m7.cls == "split"][["time", "mw", "z", "sig", "top", "d", "W", "mech_kind", "w_interface", "w_inslab", "w_crustal", "rule"]].to_string())
    print(m7.cls.value_counts().to_dict(), m7.rule.value_counts().to_dict())
    print(sens.T.to_string())
    print(big.to_string())
    print(nt.to_string(), ninfo)
    print(sg.to_string())
    print(sgv.to_string())
    print(bl.to_string())
    print(blh.to_string())
    print(tab[tab.borrowed != ""].to_string())
    print(thr.to_string())


if __name__ == "__main__":
    main()

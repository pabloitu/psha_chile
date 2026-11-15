"""X1 tier 1: matching events across the source catalogs (A3 exploration).

Origin table of all sources, ISC-ID backbone, windows calibrated on known same-event pairs, a grid of matching
variants with split / false-merge diagnostics, hot-spot sequences, RM18 matching and the X1 baseline.
"""
import itertools
import json
import time

import numba as nb
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

import x1_io as io

# settings
TMAX, DMAX = 120.0, 450.0
TW = [5, 10, 20, 40]
DW = [25, 50, 100, 150]
SCALE = {"fixed": [(99, 1.0)], "x2 M7, x3 M8": [(7, 2.0), (8, 3.0)],
         "x1.5 M6, x2 M7, x3 M8": [(6, 1.5), (7, 2.0), (8, 3.0)]}
ASSIGN = ["greedy", "hungarian"]
ORDER = ["anchor", "cluster"]
STAGES = ["potin", "csn", "comcat", "gcmt", "centennial", "iscgem", "iscehb", "csn_isc"]
PRIO = {"potin": 0, "iscehb": 1, "iscgem": 2, "centennial": 3, "csn": 4, "isc": 5, "comcat": 6, "csn_isc": 7,
        "gcmt": 8}
EXACT = {"comcat": ["NEIC", "USCGS", "NEIS", "NEIC-US"], "centennial": ["CENT"], "csn": ["GUC"],
         "gcmt_cen": ["GCMT"]}
EXACT_T, EXACT_D = 1.5, 10.0
NPROC = 14
HOT = {"Maule 2010": ("2010-02-27T06:00", 30, -40.0, -32.0), "Illapel 2015": ("2015-09-16T22:00", 30, -33.5, -29.0),
       "Iquique 2014": ("2014-03-15T00:00", 46, -21.5, -18.5), "Arauco 2011": ("2011-01-02T00:00", 3, -40.0, -36.0)}
SPLIT_T, SPLIT_D, SPLIT_M = 10.0, 50.0, 5.0
SRCI = {s: i for i, s in enumerate(io.SOURCES)}


# origin table
def origins():
    o = io.load("origins", dtype={"sid": str})
    if o is not None:
        return o
    rows = []
    for s in io.SOURCES:
        e = io.events(s)
        m = io.mags(s)
        if s == "isc":
            m = m[~m.agency.isin(["IDC", "EIDC"]) | ~m.mag_type.str.lower().str.startswith("mb")]
        g = m.groupby("src_id").mag
        e["mmax"] = e.src_id.map(g.max())
        e["mmed"] = e.src_id.map(g.median())
        isc_id = e.src_id if s in ("isc", "iscgem", "csn_isc") else pd.Series(None, index=e.index)
        if s == "iscehb":
            a = io.events("isc", all_origins=True)
            isc_id = e.origin_id.map(pd.Series(a.src_id.to_numpy(), index=a.origin_id.to_numpy()))
        if s == "comcat":
            isc_id = e.src_id.str.extract(r"^iscgem(?:sup)?(\d+)$")[0]
        rows.append(pd.DataFrame({"src": s, "sid": e.src_id, "t": e.t, "lat": e.lat, "lon": e.lon, "z": e.depth,
                                  "zfix": e.depth_fixed, "zq": e.depth_quality, "agency": e.agency, "etype": e.etype,
                                  "mmax": e.mmax, "mmed": e.mmed, "isc_id": isc_id}))
    o = pd.concat(rows, ignore_index=True)
    o = o[np.isfinite(o.t) & np.isfinite(o.lat) & np.isfinite(o.lon)].reset_index(drop=True)
    o["isc_id"] = pd.to_numeric(o.isc_id, errors="coerce")
    io.save(o, "origins")
    return o


def nearest_exact(a, b):
    """One-to-one links between origins a and b within EXACT_T s and EXACT_D km (index pairs)."""
    a, b = a.sort_values("t"), b.sort_values("t")
    tb = b.t.to_numpy()
    lo = np.searchsorted(tb, a.t.to_numpy() - EXACT_T)
    hi = np.searchsorted(tb, a.t.to_numpy() + EXACT_T)
    n = hi - lo
    ia = np.repeat(np.arange(len(a)), n)
    ib = np.concatenate([np.arange(x, y) for x, y in zip(lo, hi)]) if n.sum() else np.array([], int)
    if not len(ia):
        return pd.DataFrame(columns=["a", "b", "dt", "dd"])
    d = io.hav(a.lat.to_numpy()[ia], a.lon.to_numpy()[ia], b.lat.to_numpy()[ib], b.lon.to_numpy()[ib])
    dt = np.abs(a.t.to_numpy()[ia] - tb[ib])
    k = pd.DataFrame({"a": a.index.to_numpy()[ia], "b": b.index.to_numpy()[ib], "dt": dt, "dd": d})
    k = k[k.dd <= EXACT_D]
    k["c"] = k.dt / EXACT_T + k.dd / EXACT_D
    k = k.sort_values("c").drop_duplicates("a").drop_duplicates("b")
    return k


# ID backbone
def backbone(o):
    """Edges (global origin index pairs) from ISC event IDs and exact foreign-origin links, with their kind."""
    f = io.load("backbone")
    if f is not None:
        return f
    ed = []
    isc = o[o.src == "isc"]
    pos = pd.Series(isc.index, index=isc.isc_id)
    for s in ("iscgem", "iscehb", "csn_isc", "comcat"):
        x = o[(o.src == s) & o.isc_id.notna()]
        if s == "comcat":
            gem = o[o.src == "iscgem"]
            pg = pd.Series(gem.index, index=gem.isc_id)
            j = x.isc_id.map(pg)
            ok = j.notna()
            ed.append(pd.DataFrame({"a": x.index[ok], "b": j[ok].astype(int), "kind": "id comcat-iscgem"}))
        j = x.isc_id.map(pos)
        ok = j.notna()
        ed.append(pd.DataFrame({"a": x.index[ok], "b": j[ok].astype(int), "kind": f"id {s}-isc"}))
    allo = io.events("isc", all_origins=True)
    allo = allo[np.isfinite(allo.t)]
    for s, ags in EXACT.items():
        if s == "gcmt_cen":
            g = io.events("gcmt", all_origins=True)
            g = g[g.prime.astype(bool)]
            hyp = o[o.src == "gcmt"]
            hp = pd.Series(hyp.index, index=hyp.sid.to_numpy())
            a = pd.DataFrame({"t": g.t.to_numpy(), "lat": g.lat.to_numpy(), "lon": g.lon.to_numpy()},
                             index=g.src_id.map(hp).to_numpy())
            a = a[a.index.notna()]
            a.index = a.index.astype(int)
        else:
            a = o[o.src == s][["t", "lat", "lon"]]
        b = allo[allo.agency.isin(ags)][["t", "lat", "lon", "src_id"]].reset_index(drop=True)
        k = nearest_exact(a, b)
        j = b.src_id.to_numpy()[k.b.to_numpy().astype(int)].astype(float)
        jj = pd.Series(j).map(pos)
        ok = jj.notna().to_numpy()
        ed.append(pd.DataFrame({"a": k.a.to_numpy()[ok].astype(int), "b": jj[ok].astype(int).to_numpy(),
                                "kind": f"origin {s.replace('_cen', '')}-isc"}))
    ed = pd.concat(ed, ignore_index=True).drop_duplicates(["a", "b"])
    io.save(ed, "backbone")
    return ed


def backbone_report(o, ed):
    o = o.assign(yr=io.year(o.t))
    o["per"] = io.label(o.yr.to_numpy(), io.PERIODS)
    linked = set(ed.a) | set(ed.b)
    o["linked"] = o.index.isin(linked)
    tab = o.groupby(["src", "per"]).linked.agg(["size", "mean"]).reset_index()
    a, b = o.loc[ed.a], o.loc[ed.b]
    ed = ed.assign(dt=np.abs(a.t.to_numpy() - b.t.to_numpy()),
                   dd=io.hav(a.lat.to_numpy(), a.lon.to_numpy(), b.lat.to_numpy(), b.lon.to_numpy()),
                   dz=a.z.to_numpy() - b.z.to_numpy(), m=np.fmax(a.mmax.to_numpy(), b.mmax.to_numpy()),
                   yr=a.yr.to_numpy())
    bad = ed[(ed.dt > 30) | (ed.dd > 100)]
    return tab, ed, bad


# candidate pairs at the widest window
def cands(o):
    c = io.load("cands")
    if c is not None:
        return {k: c[k].to_numpy() for k in c.columns}
    out = []
    srt = {s: o[o.src == s].sort_values("t") for s in io.SOURCES}
    for s1, s2 in itertools.combinations(io.SOURCES, 2):
        a, b = srt[s1], srt[s2]
        tb = b.t.to_numpy()
        ta = a.t.to_numpy()
        lo = np.searchsorted(tb, ta - TMAX)
        hi = np.searchsorted(tb, ta + TMAX)
        n = hi - lo
        if n.sum() == 0:
            continue
        ia = np.repeat(np.arange(len(a)), n)
        ib = (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)) + np.repeat(lo, n)
        d = io.hav(a.lat.to_numpy()[ia], a.lon.to_numpy()[ia], b.lat.to_numpy()[ib], b.lon.to_numpy()[ib])
        k = d <= DMAX
        ia, ib, d = ia[k], ib[k], d[k]
        out.append(pd.DataFrame({"a": a.index.to_numpy()[ia], "b": b.index.to_numpy()[ib],
                                 "dt": np.abs(ta[ia] - tb[ib]).astype(np.float32), "dd": d.astype(np.float32)}))
        print(s1, s2, k.sum(), flush=True)
    c = pd.concat(out, ignore_index=True)
    c["m"] = np.fmax(o.mmax.to_numpy()[c.a], o.mmax.to_numpy()[c.b]).astype(np.float32)
    io.save(c, "cands")
    return {k: c[k].to_numpy() for k in c.columns}


def lsa_pairs(o, s1, s2, tmax=60.0, dmax=300.0, ts=10.0, ds=50.0, period=None, C=None):
    """One-to-one pairs between two sources by minimum cost (no ID), used for calibration only."""
    a, b = C["a"], C["b"]
    src = o.src.to_numpy()
    k = (((src[a] == s1) & (src[b] == s2)) | ((src[a] == s2) & (src[b] == s1))) & (C["dt"] <= tmax) & (C["dd"] <= dmax)
    if period is not None:
        t = o.t.to_numpy()[a]
        k &= (t >= period[0]) & (t < period[1])
    ia, ib = a[k], b[k]
    sw = src[ia] == s2
    ia, ib = np.where(sw, ib, ia), np.where(sw, ia, ib)
    cost = np.hypot(C["dt"][k] / ts, C["dd"][k] / ds)
    sel = assign(ia, ib, cost, "hungarian")
    return ia[sel], ib[sel]


# assignment
@nb.njit(cache=True)
def greedy_nb(ia, ib, order, na, nb_):
    ua = np.zeros(na, np.bool_)
    ub = np.zeros(nb_, np.bool_)
    sel = np.zeros(len(ia), np.bool_)
    for k in order:
        if not ua[ia[k]] and not ub[ib[k]]:
            ua[ia[k]] = True
            ub[ib[k]] = True
            sel[k] = True
    return sel


def assign(ia, ib, cost, how):
    """One-to-one selection among candidate edges (ia, ib) by greedy cost order or Hungarian per block."""
    if not len(ia):
        return np.zeros(0, bool)
    ua, ra = np.unique(ia, return_inverse=True)
    ub, rb = np.unique(ib, return_inverse=True)
    if how == "greedy":
        return greedy_nb(ra, rb, np.argsort(cost, kind="stable"), len(ua), len(ub))
    na = len(ua)
    g = coo_matrix((np.ones(len(ra)), (ra, rb + na)), shape=(na + len(ub),) * 2)
    _, lab = connected_components(g, directed=False)
    bl = lab[ra]
    da = np.bincount(ra, minlength=na)
    db = np.bincount(rb, minlength=len(ub))
    sel = (da[ra] == 1) & (db[rb] == 1)
    hard = ~sel
    if hard.any():
        idx = np.flatnonzero(hard)
        idx = idx[np.argsort(bl[idx], kind="stable")]
        cut = np.flatnonzero(np.diff(bl[idx])) + 1
        for grp in np.split(idx, cut):
            xa, xa_i = np.unique(ra[grp], return_inverse=True)
            xb, xb_i = np.unique(rb[grp], return_inverse=True)
            M = np.full((len(xa), len(xb)), 1e6)
            M[xa_i, xb_i] = cost[grp]
            r, c = linear_sum_assignment(M)
            ok = M[r, c] < 1e6
            pos = {(i, j): g_ for i, j, g_ in zip(xa_i, xb_i, grp)}
            for i, j in zip(r[ok], c[ok]):
                sel[pos[(i, j)]] = True
    return sel


# union-find with one origin per source
@nb.njit(cache=True)
def find(p, x):
    r = x
    while p[r] != r:
        r = p[r]
    while p[x] != r:
        nx = p[x]
        p[x] = r
        x = nx
    return r


@nb.njit(cache=True)
def union_all(p, mask, rep, pr, ea, eb, force):
    n_ok = 0
    ok = np.zeros(len(ea), np.bool_)
    for k in range(len(ea)):
        ra, rb = find(p, ea[k]), find(p, eb[k])
        if ra == rb:
            ok[k] = True
            continue
        if (mask[ra] & mask[rb]) != 0 and not force:
            continue
        p[rb] = ra
        mask[ra] |= mask[rb]
        if pr[rep[rb]] < pr[rep[ra]]:
            rep[ra] = rep[rb]
        ok[k] = True
        n_ok += 1
    return ok


@nb.njit(cache=True)
def roots(p):
    out = np.empty(len(p), np.int64)
    for i in range(len(p)):
        out[i] = find(p, i)
    return out


def windows(C, o, tw, dw, scale, cal=None):
    """Effective time and distance windows per candidate edge."""
    f = np.ones(len(C["a"]), np.float32)
    m = np.nan_to_num(C["m"], nan=0)
    for thr, x in scale:
        f = np.where(m >= thr, x, f)
    if cal is None:
        T, D = np.float32(tw) * f, np.float32(dw) * f
    else:
        T, D = cal["T"] * f, cal["D"] * f
    return np.minimum(T, TMAX), np.minimum(D, DMAX)


def cal_edges(C, o, wt):
    """Per-edge calibrated windows from the per source-pair table wt."""
    src = o.src.to_numpy()
    key = np.char.add(np.char.add(src[C["a"]].astype(str), "|"), src[C["b"]].astype(str))
    T = pd.Series(key).map(wt.T_).fillna(wt.T_.max()).to_numpy(np.float32)
    D = pd.Series(key).map(wt.D_).fillna(wt.D_.max()).to_numpy(np.float32)
    return {"T": T, "D": D}


def match(o, C, ed, tw, dw, scale, how, order, cal=None, use_bb=True):
    """
    One matching variant.

    Returns
    -------
    ev : event label per origin; rep : representative origin per event label; wl : window-linked edge flags
    """
    n = len(o)
    src = o.src.map(SRCI).to_numpy()
    p = np.arange(n, dtype=np.int64)
    mask = (1 << src).astype(np.int64)
    rep = np.arange(n, dtype=np.int64)
    pr = o.src.map(PRIO).to_numpy().astype(np.int64)
    if use_bb:
        union_all(p, mask, rep, pr, ed.a.to_numpy().astype(np.int64), ed.b.to_numpy().astype(np.int64), False)
    T, D = windows(C, o, tw, dw, SCALE[scale], cal)
    ok = (C["dt"] <= T) & (C["dd"] <= D)
    a, b = C["a"][ok].astype(np.int64), C["b"][ok].astype(np.int64)
    cost = np.hypot(C["dt"][ok] / T[ok], C["dd"][ok] / D[ok])
    sa, sb = src[a], src[b]
    if order == "cluster":
        keep = np.zeros(len(a), bool)
        pk = sa * 16 + sb
        for v in np.unique(pk):
            j = np.flatnonzero(pk == v)
            keep[j[assign(a[j], b[j], cost[j], how)]] = True
        j = np.flatnonzero(keep)
        j = j[np.argsort(cost[j], kind="stable")]
        union_all(p, mask, rep, pr, a[j], b[j], False)
    else:
        for s in STAGES:
            si = SRCI[s]
            r = roots(p)
            single = np.bincount(r, minlength=n)
            fa = (sa == si) & (single[r[a]] == 1)
            fb = (sb == si) & (single[r[b]] == 1)
            x = np.where(fa, a, b)
            y = np.where(fa, b, a)
            k = (fa | fb) & (src[y] != si)
            x, y, c = x[k], y[k], cost[k]
            ry = r[y]
            k = (rep[ry] == y) & ((mask[ry] & (1 << si)) == 0)
            x, ry, c = x[k], ry[k], c[k]
            sel = assign(x, ry, c, how)
            union_all(p, mask, rep, pr, x[sel], ry[sel], False)
    r = roots(p)
    return r, rep


def diagnostics(o, r, rep, ed, p99, name, bbr):
    """Counts of one variant: events, links per pair, splits, false merges, M >= 6 merges."""
    t, la, lo = o.t.to_numpy(), o.lat.to_numpy(), o.lon.to_numpy()
    mm = o.mmax.to_numpy()
    md = o.mmed.to_numpy()
    src = o.src.to_numpy()
    ev = pd.DataFrame({"r": r, "src": src, "m": mm})
    emax = ev.groupby("r").m.max()
    roots_ = emax.index.to_numpy()
    e = pd.DataFrame({"r": roots_, "rep": rep[roots_], "m": emax.to_numpy()})
    e["t"], e["lat"], e["lon"] = t[e.rep], la[e.rep], lo[e.rep]
    e["yr"] = np.floor(io.year(e.t.to_numpy())).astype(int)
    e["nsrc"] = ev.groupby("r").size().to_numpy()
    out = {"variant": name, "n_events": len(e), "n_ge45": int((e.m >= 4.5).sum())}
    # splits
    e = e.sort_values("t").reset_index(drop=True)
    tt, ll, oo, m = e.t.to_numpy(), e.lat.to_numpy(), e.lon.to_numpy(), e.m.to_numpy()
    sp = []
    for k in range(1, 40):
        i = np.arange(len(e) - k)
        j = i + k
        w = tt[j] - tt[i] < SPLIT_T
        if not w.any():
            break
        i, j = i[w], j[w]
        d = io.hav(ll[i], oo[i], ll[j], oo[j])
        w = (d < SPLIT_D) & (np.fmax(m[i], m[j]) >= SPLIT_M)
        sp.append(np.c_[i[w], j[w]])
    sp = np.vstack(sp) if sp else np.zeros((0, 2), int)
    out["splits"] = len(sp)
    # members against the representative
    idx = np.flatnonzero(rep[r] != np.arange(len(r)))
    rp = rep[r[idx]]
    dt = np.abs(t[idx] - t[rp])
    dd = io.hav(la[idx], lo[idx], la[rp], lo[rp])
    key = pd.Series([f"{min(x, y)}|{max(x, y)}" for x, y in zip(src[idx], src[rp])])
    T99 = key.map(p99["dt"]).fillna(p99["dt"].max()).to_numpy()
    D99 = key.map(p99["dd"]).fillna(p99["dd"].max()).to_numpy()
    dm = np.abs(md[idx] - md[rp])
    dm[(src[idx] == "potin") | (src[rp] == "potin")] = np.nan
    win = bbr[idx] != bbr[rp]
    fm = ((dt > T99) | (dd > D99) | (dm > 1)) & win
    out["false_merges"] = int(fm.sum())
    out["fm_time_dist"] = int((((dt > T99) | (dd > D99)) & win).sum())
    out["fm_mag"] = int(((dm > 1) & win).sum())
    out["fm_incl_id"] = int(((dt > T99) | (dd > D99) | (dm > 1)).sum())
    emed = pd.Series(md).groupby(r).max()
    m6r = np.unique(r[idx[win & (emed.reindex(r[idx]).to_numpy() >= 6)]])
    m6 = list(m6r)
    out["m6_window_merges"] = len(m6)
    out["window_links"] = int(win.sum())
    out["linked_origins"] = len(idx)
    out["multi_events"] = int((e.nsrc > 1).sum())
    lk = pd.DataFrame({"a": src[idx], "b": src[rp]})
    lk["pair"] = [f"{min(x, y)}|{max(x, y)}" for x, y in zip(lk.a, lk.b)]
    out["links"] = lk.pair.value_counts().to_dict()
    yr = e[e.m >= 4.5].groupby("yr").size()
    out["per_year"] = {int(k): int(v) for k, v in yr.items()}
    det = {"splits": sp, "e": e, "fm": np.c_[idx[fm], rp[fm], dt[fm], dd[fm], dm[fm]], "m6": m6}
    return out, det


def ambiguous(C, o, tw, dw, scale, cal=None):
    T, D = windows(C, o, tw, dw, SCALE[scale], cal)
    ok = (C["dt"] <= T) & (C["dd"] <= D)
    src = o.src.map(SRCI).to_numpy()
    a, b = C["a"][ok], C["b"][ok]
    ka = pd.Series(a * 16 + src[b]).value_counts()
    kb = pd.Series(b * 16 + src[a]).value_counts()
    return int((ka >= 2).sum() + (kb >= 2).sum())


# calibration on known same-event pairs
def known_pairs(o, ed, C):
    f = io.load("known_pairs")
    if f is not None:
        return f
    n = len(o)
    p = np.arange(n, dtype=np.int64)
    mask = (1 << o.src.map(SRCI).to_numpy()).astype(np.int64)
    rep = np.arange(n, dtype=np.int64)
    pr = o.src.map(PRIO).to_numpy().astype(np.int64)
    union_all(p, mask, rep, pr, ed.a.to_numpy().astype(np.int64), ed.b.to_numpy().astype(np.int64), True)
    r = roots(p)
    g = pd.DataFrame({"r": r, "i": np.arange(n)})
    g = g[g.groupby("r").i.transform("size") > 1]
    rows = []
    for _, grp in g.groupby("r").i:
        for x, y in itertools.combinations(sorted(grp.to_numpy(), key=lambda v: o.src.iat[v]), 2):
            rows.append((x, y, "id"))
    k = pd.DataFrame(rows, columns=["a", "b", "kind"])
    for s1, s2, per in [("potin", "csn_isc", None), ("csn", "potin", (io.tsec(["2020-01-01"])[0], io.tsec(["2020-07-17"])[0])),
                        ("gcmt", "comcat", None), ("csn", "csn_isc", None)]:
        ia, ib = lsa_pairs(o, s1, s2, period=per, C=C)
        k = pd.concat([k, pd.DataFrame({"a": ia, "b": ib, "kind": "nearest one-to-one"})])
    g = io.events("gcmt", all_origins=True)
    hyp = o[o.src == "gcmt"]
    cen = g[g.prime.astype(bool)].set_index("src_id")
    a, b = o.loc[k.a.to_numpy()], o.loc[k.b.to_numpy()]
    k = k.assign(sa=a.src.to_numpy(), sb=b.src.to_numpy(), dt=np.abs(a.t.to_numpy() - b.t.to_numpy()),
                 dd=io.hav(a.lat.to_numpy(), a.lon.to_numpy(), b.lat.to_numpy(), b.lon.to_numpy()),
                 dz=a.z.to_numpy() - b.z.to_numpy(), m=np.fmax(a.mmax.to_numpy(), b.mmax.to_numpy()),
                 yr=io.year(a.t.to_numpy()))
    c = cen.loc[hyp.sid.to_numpy()]
    cc = pd.DataFrame({"a": hyp.index, "b": -1, "kind": "centroid", "sa": "gcmt centroid", "sb": "gcmt",
                       "dt": np.abs(c.t.to_numpy() - hyp.t.to_numpy()),
                       "dd": io.hav(c.lat.to_numpy(), c.lon.to_numpy(), hyp.lat.to_numpy(), hyp.lon.to_numpy()),
                       "dz": c.depth.to_numpy() - hyp.z.to_numpy(), "m": hyp.mmax.to_numpy(), "yr": io.year(hyp.t.to_numpy())})
    k = pd.concat([k, cc], ignore_index=True)
    s = np.sort(np.c_[k.sa.astype(str), k.sb.astype(str)], axis=1)
    k["pair"] = [f"{x}|{y}" for x, y in s]
    io.save(k, "known_pairs")
    return k


def percentiles(k):
    k = k.assign(per=io.label(k.yr.to_numpy(), io.PERIODS), mb=io.label(np.nan_to_num(k.m.to_numpy()), io.MBANDS))
    rows = []
    for by in (["pair"], ["pair", "per"], ["pair", "mb"]):
        for key, g in k.groupby(by):
            key = key if isinstance(key, tuple) else (key,)
            d = dict(zip(by, key))
            d.update(n=len(g), **{f"{v}_p{q}": float(np.nanpercentile(np.abs(g[v]), q)) if g[v].notna().any() else np.nan
                                  for v in ("dt", "dd", "dz") for q in (50, 95, 99)})
            rows.append(d)
    return pd.DataFrame(rows)


def cal_table(pc):
    w = pc[pc.per.isna() & pc.mb.isna() & (pc.n >= 30) & ~pc.pair.str.contains("centroid")].set_index("pair")
    T = w.dt_p99.clip(5, TMAX)
    D = w.dd_p99.clip(25, DMAX)
    def via(s1, s2):
        best = (np.inf, np.inf, None)
        for h in io.SOURCES:
            k1, k2 = f"{min(s1, h)}|{max(s1, h)}", f"{min(s2, h)}|{max(s2, h)}"
            if k1 in T.index and k2 in T.index:
                t_, d_ = np.hypot(T[k1], T[k2]), np.hypot(D[k1], D[k2])
                if d_ < best[1]:
                    best = (t_, d_, h)
        return best
    rows = []
    for s1, s2 in itertools.combinations(io.SOURCES, 2):
        k = f"{min(s1, s2)}|{max(s1, s2)}"
        if k in T.index:
            t_, d_, how = T[k], D[k], "calibrated"
        else:
            t_, d_, h = via(s1, s2)
            how = f"via {h}"
            if not np.isfinite(t_):
                t_, d_, how = 20.0, 100.0, "default"
            t_, d_ = np.clip(t_, 5, TMAX), np.clip(d_, 25, DMAX)
        for a_, b_ in ((s1, s2), (s2, s1)):
            rows.append({"key": f"{a_}|{b_}", "pair": k, "T_": t_, "D_": d_, "how": how})
    return pd.DataFrame(rows).set_index("key")


# baseline, RM18 and figures
RM_FIX = {"Copiapo 1959": "1859-10-05"}
RM_SWAP = {"Mejillones 1994": "1994-12-10"}


def grid_table():
    g = pd.DataFrame([json.loads(ln) for ln in open(io.CACHE / "grid.jsonl")])
    h = pd.json_normalize(g.hot.tolist())
    h.index = g.index
    g["hot_ok"] = h.filter(like="main_one_event").sum(axis=1)
    g["score"] = g.splits + g.false_merges
    return g, h


def pick(g):
    ok = g[g.hot_ok == len(HOT)].sort_values(["score", "assign"], ascending=[True, False])
    b = ok.iloc[0]
    n1 = ok[ok.order != b.order].iloc[0]
    n2 = ok[(ok.tw == "cal")].iloc[0]
    return {"baseline": b, "nb_order": n1, "nb_calibrated": n2}


def event_table(o, r, rep):
    """One row per event: representative origin, magnitude proxies and member sources."""
    d = pd.DataFrame({"ev": r, "src": o.src.to_numpy(), "m": o.mmax.to_numpy(), "md": o.mmed.to_numpy()})
    g = d.groupby("ev")
    e = pd.DataFrame({"m": g.m.max(), "md": g.md.max(), "n": g.size(), "srcs": g.src.agg(lambda x: ",".join(sorted(x)))})
    e["rep"] = rep[e.index.to_numpy()]
    for c in ("t", "lat", "lon", "z", "src"):
        e[c] = o[c].to_numpy()[e.rep]
    return e.reset_index()


def rm18(o, r, rep):
    """RM18 events against the catalog events (and Cabello rows): ±1 day, latitude within 2°, one-to-one,
    closest magnitude to the RM18 Mw (largest where RM18 gives none), larger RM18 events first."""
    e = io.events("rm2018")
    m = io.mags("rm2018").set_index("src_id").mag
    e["mw"] = e.src_id.map(m)
    ev = event_table(o, r, rep)
    cab = io.events("cabello")
    cm = io.mags("cabello")
    cab["mw"] = cab.src_id.map(cm[cm.agency == "cabello"].set_index("src_id").mag)
    cab["ev"] = cab.src_id
    rows, taken = [], {"event": set(), "cabello": set()}
    for _, x in e.sort_values("mw", ascending=False, na_position="last").iterrows():
        tm = RM_FIX.get(x.src_id, str(x.time))
        tries = [("table", tm)] + ([("swapped", RM_SWAP[x.src_id])] if x.src_id in RM_SWAP else [])
        hit = False
        for how, ts in tries:
            if len(ts) < 10:
                continue
            t0 = io.tsec([ts])[0]
            for tab, lab, col in ((ev, "event", "md"), (cab, "cabello", "mw")):
                w = tab[(tab.t >= t0 - 86400) & (tab.t < t0 + 2 * 86400) & ((tab.lat - x.lat).abs() <= 2)
                        & ~tab.ev.isin(taken[lab]) & (tab[col].fillna(0) >= 5.5)]
                if not len(w):
                    continue
                key = (w[col] - x.mw).abs() if np.isfinite(x.mw) else -w[col]
                y = w.loc[key.idxmin()]
                taken[lab].add(y.ev)
                hit = True
                rows.append({"rm18": x.src_id, "date": ts, "how": how, "where": lab, "rm_lat": x.lat, "rm_lon": x.lon,
                             "rm_mw": x.mw, "ev": y.ev if lab == "event" else None, "time": io.tstr(y.t)[0],
                             "lat": y.lat, "lon": y.lon, "mag": y[col], "srcs": y.srcs if lab == "event" else "cabello",
                             "n_cand": len(w)})
        if not hit:
            rows.append({"rm18": x.src_id, "date": tm, "how": "unmatched", "rm_lat": x.lat, "rm_mw": x.mw})
    return pd.DataFrame(rows).sort_values("date", key=lambda c: c.astype(str))


def side_by_side(o, r, rm):
    """Values of every source for the RM18 events matched to a catalog event."""
    mt = rm[(rm["where"] == "event")].drop_duplicates("rm18")
    rows = []
    allm = {s: io.mags(s) for s in io.SOURCES}
    for _, x in mt.iterrows():
        mem = o[r == x.ev]
        for _, y in mem.iterrows():
            mm = allm[y.src]
            mm = mm[mm.src_id == y.sid]
            if y.src == "isc":
                mm = mm[mm.agency.isin(["ISC", "NEIC", "GCMT", "ISC-GEM", "GUC", "PAS", "B&D", "G&R", "ABE1", "AN2"])]
            ms = "; ".join(f"{a} {b} {c:.1f}" for a, b, c in mm[["agency", "mag_type", "mag"]].dropna().head(5).itertuples(index=False))
            rows.append({"rm18": x.rm18, "rm_mw": x.rm_mw, "src": io.NAME[y.src],
                         "time": io.tstr(y.t)[0],
                         "lat": round(y.lat, 2), "lon": round(y.lon, 2), "depth": y.z, "mags": ms})
    return pd.DataFrame(rows)


def finish(o, k, pc):
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm  # noqa: F401
    g, h = grid_table()
    keep = ["variant", "tw", "dw", "scale", "assign", "order", "n_events", "n_ge45", "splits", "false_merges",
            "fm_time_dist", "fm_mag", "fm_incl_id", "m6_window_merges", "ambiguous", "window_links", "hot_ok", "score"]
    pd.concat([g[keep], h], axis=1).to_csv(io.TAB / "t1_grid.csv", index=False)
    lk = pd.DataFrame(g.links.tolist(), index=g.variant).fillna(0).astype(int)
    lk.to_csv(io.TAB / "t1_links_per_pair.csv")
    sel = pick(g)
    labs = {}
    for nm, row in sel.items():
        tw, dw = (row.tw, row.dw) if row.tw == "cal" else (int(row.tw), int(row.dw))
        cal = G["cal"] if tw == "cal" else None
        r, rep = match(o, G["C"], G["ed"], 0 if cal else tw, 0 if cal else dw, row.scale, row.assign, row.order, cal)
        labs[nm] = (r, rep)
        out, det = diagnostics(o, r, rep, G["ed"], G["p99"], nm, G["bbr"])
        e = event_table(o, r, rep)
        e.to_csv(io.CACHE / f"events_{nm}.csv.gz", index=False)
        if nm == "baseline":
            m6 = e[e.ev.isin(det["m6"])].copy()
            m6["time"] = io.tstr(m6.t)
            m6.sort_values("t")[["ev", "time", "lat", "lon", "z", "m", "md", "n", "srcs"]].to_csv(
                io.TAB / "t1_baseline_m6_window_merges.csv", index=False)
            fm = pd.DataFrame(det["fm"], columns=["i", "j", "dt", "dd", "dm"])
            fm["si"], fm["sj"] = o.src.to_numpy()[fm.i.astype(int)], o.src.to_numpy()[fm.j.astype(int)]
            fm["time"] = io.tstr(o.t.to_numpy()[fm.i.astype(int)])
            fm.to_csv(io.TAB / "t1_baseline_false_merges.csv", index=False)
            sp = det["e"]
            spl = pd.DataFrame({"t1": sp.t.to_numpy()[det["splits"][:, 0]], "t2": sp.t.to_numpy()[det["splits"][:, 1]],
                                "src1": o.src.to_numpy()[sp.rep.to_numpy()[det["splits"][:, 0]]],
                                "src2": o.src.to_numpy()[sp.rep.to_numpy()[det["splits"][:, 1]]],
                                "m1": sp.m.to_numpy()[det["splits"][:, 0]], "m2": sp.m.to_numpy()[det["splits"][:, 1]]})
            spl["time"] = io.tstr(spl.t1)
            spl.to_csv(io.TAB / "t1_baseline_splits.csv", index=False)
    pd.DataFrame({nm: v[0] for nm, v in labs.items()}).to_csv(io.CACHE / "labels.csv.gz", index=False)
    json.dump({nm: {kk: str(vv) for kk, vv in row[["variant", "tw", "dw", "scale", "assign", "order", "splits",
                                                   "false_merges", "n_ge45"]].items()} for nm, row in sel.items()},
              open(io.TAB / "t1_selected_variants.json", "w"), indent=1)
    r, rep = labs["baseline"]
    rm = rm18(o, r, rep)
    rm.to_csv(io.TAB / "t1_rm18_matches.csv", index=False)
    sb = side_by_side(o, r, rm)
    sb.to_csv(io.TAB / "t1_rm18_side_by_side.csv", index=False)
    plt_ = io.fig_setup()
    fig_windows(plt_, k, pc)
    fig_per_year(plt_, o, g, sel)
    fig_heat(plt_, g)
    fig_hot(plt_, o, labs)
    fig_rm18(plt_, rm)


def fig_windows(plt, k, pc):
    pairs = ["isc|iscehb", "isc|iscgem", "comcat|isc", "csn_isc|isc", "csn_isc|potin", "csn|potin", "gcmt|isc",
             "centennial|iscgem", "comcat|gcmt", "gcmt|gcmt centroid"]
    fig, ax = plt.subplots(1, 3, figsize=(15, 5), layout="constrained")
    nm = lambda p: " – ".join(io.NAME.get(x, x.replace("gcmt centroid", "GCMT centroid")) for x in p.split("|"))
    for i, p in enumerate(pairs):
        x = k[k.pair == p]
        for a, v, lab in zip(ax, ("dt", "dd", "dz"), ("|Δt| [s]", "Δ epicentre [km]", "|Δ depth| [km]")):
            y = np.sort(np.abs(x[v].dropna().to_numpy()))
            y = np.clip(y, 0.01, None)
            a.plot(y, np.linspace(0, 1, len(y)), color=io.palette.SERIES[i % 12], lw=1.6, label=f"{nm(p)} ({len(x)})")
            a.set_xscale("log")
            a.set_xlabel(lab)
    for a in ax:
        a.axhline(0.95, color="0.6", lw=0.8, ls="--")
        a.axhline(0.99, color="0.6", lw=0.8, ls=":")
        a.set_ylim(0.5, 1.001)
    ax[0].set_ylabel("cumulative fraction of pairs")
    ax[0].set_xlim(0.05, 200)
    ax[1].set_xlim(0.1, 1000)
    ax[2].set_xlim(0.1, 200)
    ax[2].legend(loc="lower right", fontsize=8)
    fig.suptitle("How far apart are origins of the same earthquake? Known pairs per source pair (dashed 95 %, dotted 99 %)",
                 x=0.01, ha="left")
    io.savefig(fig, "t1_window_calibration", "Δt, Δepicentre and Δdepth distributions of known same-event pairs per "
               "source pair, with the 95th / 99th percentile levels")
    # p99 by period and magnitude band, main pairs
    fig, ax = plt.subplots(1, 2, figsize=(13, 5), layout="constrained")
    for i, p in enumerate(pairs[:9]):
        for a, by, order_ in ((ax[0], "per", [x[2] for x in io.PERIODS]), (ax[1], "mb", [x[2] for x in io.MBANDS])):
            y = pc[(pc.pair == p) & pc[by].notna() & (pc.n >= 20)].set_index(by).reindex(order_)
            a.plot(range(len(order_)), y.dd_p99, "o-", color=io.palette.SERIES[i], label=nm(p))
            a.set_xticks(range(len(order_)), order_)
    for a in ax:
        a.set_yscale("log")
        a.set_ylabel("99th percentile of Δ epicentre [km]")
    ax[0].set_title("by period")
    ax[1].set_title("by magnitude band (largest native M)")
    ax[1].legend(fontsize=8, ncol=2)
    fig.suptitle("Do same-event distances depend on period and size?", x=0.01, ha="left")
    io.savefig(fig, "t1_window_p99_period_mag", "99th percentile of the epicentre difference of known pairs by period "
               "and by magnitude band, per source pair")


def fig_per_year(plt, o, g, sel):
    fig, ax = plt.subplots(2, 1, figsize=(13, 8), layout="constrained", sharex=True)
    show = {"baseline": sel["baseline"].variant, "nb_order": sel["nb_order"].variant,
            "nb_calibrated": sel["nb_calibrated"].variant}
    tight = g.loc[(g.tw == "5") & (g.dw == "25") & (g.order == "anchor") & (g.scale == "fixed")].iloc[0].variant
    wide = g.loc[(g.tw == "40") & (g.dw == "150") & (g.order == "cluster") & (g.scale == "x2 M7, x3 M8")].iloc[0].variant
    base = pd.Series(g.set_index("variant").per_year[show["baseline"]]).sort_index()
    base.index = base.index.astype(int)
    lab = {"baseline": "X1 baseline", "nb_order": "nearest, other order", "nb_calibrated": "nearest calibrated"}
    for i, (nm, v) in enumerate(list(show.items()) + [("tight", tight), ("wide", wide)]):
        y = pd.Series(g.set_index("variant").per_year[v])
        y.index = y.index.astype(int)
        y = y.sort_index()
        y = y[y.index >= 1960]
        l = f"{lab.get(nm, nm)}: {v}"
        ax[0].plot(y.index, y.values, color=io.palette.SERIES[i], lw=1.4, label=l)
        ax[1].plot(y.index, (y - base.reindex(y.index)).values, color=io.palette.SERIES[i], lw=1.4)
    ax[0].set_ylabel("events with any native M ≥ 4.5")
    ax[1].set_ylabel("difference to the baseline")
    ax[0].legend(fontsize=8)
    ax[0].set_title("How many M ≥ 4.5 events per year does each matching variant give?")
    io.savefig(fig, "t1_events_per_year", "Events per year with any native M ≥ 4.5 for the baseline, its neighbours "
               "and the tightest and widest grid corners, and the difference to the baseline")


def fig_heat(plt, g):
    x = g[(g.tw != "cal") & (g["assign"] == "hungarian")]
    fig, ax = plt.subplots(3, 4, figsize=(17, 11), layout="constrained")
    for j, (sc, order) in enumerate([("fixed", "anchor"), ("x2 M7, x3 M8", "anchor"), ("fixed", "cluster"),
                                     ("x2 M7, x3 M8", "cluster")]):
        y = x[(x.scale == sc) & (x.order == order)]
        for i, (v, cm) in enumerate((("splits", "Blues"), ("false_merges", "Oranges"), ("n_ge45", "Greens"))):
            p = y.pivot(index="tw", columns="dw", values=v)
            p = p.reindex(index=["5", "10", "20", "40"], columns=["25", "50", "100", "150"])
            a = ax[i, j]
            im = a.imshow(p.to_numpy(float), cmap=cm, aspect="auto")
            for (r_, c_), val in np.ndenumerate(p.to_numpy()):
                a.text(c_, r_, f"{int(val)}", ha="center", va="center", fontsize=9,
                       color="white" if val > np.nanpercentile(p.to_numpy(float), 70) else "0.1")
            a.set_xticks(range(4), [f"{c} km" for c in p.columns])
            a.set_yticks(range(4), [f"{c} s" for c in p.index])
            a.spines[:].set_visible(False)
            if i == 0:
                a.set_title(f"{'anchor-first' if order == 'anchor' else 'all-pairs clustering'}, "
                            f"{'fixed windows' if sc == 'fixed' else '×2 at M 7, ×3 at M 8'}", fontsize=11)
            if j == 0:
                a.set_ylabel({"splits": "probable splits", "false_merges": "probable false merges",
                              "n_ge45": "events M ≥ 4.5"}[v])
    fig.suptitle("How do the time and distance windows trade split events against false merges? (Hungarian assignment)",
                 x=0.01, ha="left")
    io.savefig(fig, "t1_grid_heatmap", "Probable splits, probable false merges and M ≥ 4.5 event counts over the "
               "time × distance window grid, for both source orders and two scalings")


def fig_hot(plt, o, labs):
    import cartopy.crs as ccrs
    from pituplots.maps import dress_map
    from matplotlib.lines import Line2D
    srcc = {s: io.palette.SERIES[i] for i, s in enumerate(io.SOURCES)}
    mk = {"isc": "o", "potin": "s", "csn_isc": "D", "comcat": "^", "gcmt": "*", "iscehb": "v", "iscgem": "P",
          "centennial": "X", "csn": "h"}
    nv = list(labs)
    seqs = {"Maule 2010": (1, 5.2), "Illapel 2015": (1, 5.0), "Iquique 2014": (3, 4.8), "Arauco 2011": (2, 3.5)}
    fig = plt.figure(figsize=(5.0 * len(nv), 4.6 * len(seqs)), layout="constrained")
    for i, (nm, (days, mmin)) in enumerate(seqs.items()):
        t0s, _, s, n_ = HOT[nm]
        t0 = io.tsec([t0s])[0]
        if nm == "Iquique 2014":
            t0 = io.tsec(["2014-04-01T23:00"])[0]
        w = (o.t >= t0) & (o.t < t0 + days * 86400) & (o.lat >= s) & (o.lat <= n_)
        w &= o.mmax.fillna(0) >= mmin
        x = o[w]
        ext = [x.lon.min() - 0.3, x.lon.max() + 0.3, x.lat.min() - 0.3, x.lat.max() + 0.3]
        for j, v in enumerate(nv):
            r, rep = labs[v]
            ax = fig.add_subplot(len(seqs), len(nv), i * len(nv) + j + 1, projection=ccrs.PlateCarree())
            dress_map(ax, ext, coastline=True, gridlines=False)
            rr = r[x.index]
            u, inv = np.unique(rr, return_inverse=True)
            cols = plt.get_cmap("tab20")(inv % 20)
            for q, (ix, y) in enumerate(x.iterrows()):
                rp = rep[r[ix]]
                ax.plot([y.lon, o.lon.iat[rp]], [y.lat, o.lat.iat[rp]], color=cols[q], lw=0.6, alpha=0.7,
                        transform=ccrs.PlateCarree())
            for sname, gg in x.groupby("src"):
                q = np.flatnonzero(x.src.to_numpy() == sname)
                ax.scatter(gg.lon, gg.lat, s=8 + 3 * (gg.mmax.fillna(4) - 3) ** 2, c=cols[q], marker=mk[sname],
                           edgecolor="0.2", lw=0.3, transform=ccrs.PlateCarree(), zorder=3)
            ax.set_title(f"{nm}, first {days} d: {len(u)} events from {len(x)} origins\n{v}", fontsize=9)
    hd = [Line2D([], [], marker=mk[s], color="0.4", ls="", label=io.NAME[s]) for s in io.SOURCES]
    fig.legend(handles=hd, loc="outside lower center", ncol=9, fontsize=9)
    fig.suptitle("Which origins does each variant put into one event? Colour = event, lines join origins to the "
                 "event's representative", x=0.01, ha="left")
    io.savefig(fig, "t1_hotspot_maps", "Hot-spot sequences (Maule, Illapel, Iquique, Arauco 2011) coloured by event "
               "label for the baseline and its two neighbours")


def fig_rm18(plt, rm):
    t = rm.sort_values(["rm18", "where"]).copy()
    t = t[t["where"].ne("cabello") | t.rm18.isin(t[t["where"] != "event"].rm18)]
    t["time"] = t.time.astype(str).str[:19]
    cols = ["rm18", "rm_mw", "how", "where", "time", "lat", "lon", "mag", "srcs"]
    t = t[cols].fillna("")
    for c in ("lat", "lon", "mag", "rm_mw"):
        t[c] = [f"{v:.2f}" if isinstance(v, float) else v for v in t[c]]
    t["srcs"] = t.srcs.str.replace("csn_isc", "csnisc").str.slice(0, 55)
    n = len(t)
    fig, ax = plt.subplots(figsize=(17, 0.26 * n + 1.2))
    ax.axis("off")
    tb = ax.table(cellText=t.to_numpy(), colLabels=["RM18 event", "RM18 Mw", "date", "matched in", "time (UTC)",
                                                     "lat", "lon", "M (median)", "sources"], loc="upper left",
                  cellLoc="left", colWidths=[0.13, 0.05, 0.06, 0.06, 0.13, 0.05, 0.06, 0.06, 0.4])
    tb.auto_set_font_size(False)
    tb.set_fontsize(7.5)
    tb.scale(1, 1.15)
    ax.set_title("Which catalog event is each Ruiz & Madariaga (2018) event? (±1 day, latitude within 2°)", loc="left")
    io.savefig(fig, "t1_rm18_table", "RM18 events with their matched baseline event (or Cabello row before 1904) and "
               "the sources in that event")


# grid
G = {}


def run_variant(v):
    o, C, ed, p99 = G["o"], G["C"], G["ed"], G["p99"]
    tw, dw, sc, how, order = v
    cal = G["cal"] if tw == "cal" else None
    t0 = time.time()
    r, rep = match(o, C, ed, 0 if cal else tw, 0 if cal else dw, sc, how, order, cal)
    name = f"{tw}s {dw}km | {sc} | {how} | {order}" if cal is None else f"calibrated | {sc} | {how} | {order}"
    out, det = diagnostics(o, r, rep, ed, p99, name, G["bbr"])
    out.update(tw=str(tw), dw=str(dw), scale=sc, assign=how, order=order, secs=round(time.time() - t0, 1))
    out["ambiguous"] = ambiguous(C, o, 0 if cal else tw, 0 if cal else dw, sc, cal)
    out["hot"] = hot_metrics(o, r, rep, det)
    np.save(io.CACHE / "variants" / f"{abs(hash(name)) % 10**10}.npy", r.astype(np.int32))
    out["file"] = f"{abs(hash(name)) % 10**10}.npy"
    return out


def hot_metrics(o, r, rep, det):
    t, la = o.t.to_numpy(), o.lat.to_numpy()
    e, sp, fm = det["e"], det["splits"], det["fm"]
    res = {}
    for nm, (t0s, days, s, n_) in HOT.items():
        t0 = io.tsec([t0s])[0]
        inw = lambda tt, ll: (tt >= t0) & (tt < t0 + days * 86400) & (ll >= s) & (ll <= n_)
        ew = e[inw(e.t.to_numpy(), e.lat.to_numpy())]
        spw = int(inw(e.t.to_numpy()[sp[:, 0]], e.lat.to_numpy()[sp[:, 0]]).sum()) if len(sp) else 0
        fmw = int(inw(t[fm[:, 0].astype(int)], la[fm[:, 0].astype(int)]).sum()) if len(fm) else 0
        big = ew.sort_values("m", ascending=False).head(1)
        ok = None
        if len(big):
            b = big.iloc[0]
            near = (np.abs(t - b.t) < 120) & (io.hav(la, o.lon.to_numpy(), b.lat, b.lon) < 300) & (o.mmax.to_numpy() >= b.m - 1.0)
            ok = int(len(np.unique(r[near])) == 1)
            nsrc = int(near.sum())
        res[nm] = {"events": len(ew), "ge45": int((ew.m >= 4.5).sum()), "splits": spw, "false_merges": fmw,
                   "main_one_event": ok, "main_origins": nsrc if len(big) else 0}
    return res


def init(o, C, ed, p99, cal, bbr):
    G.update(o=o, C=C, ed=ed, p99=p99, cal=cal, bbr=bbr)


def bb_roots(o, ed):
    n = len(o)
    p = np.arange(n, dtype=np.int64)
    mask = np.zeros(n, np.int64)
    rep = np.arange(n, dtype=np.int64)
    union_all(p, mask, rep, np.zeros(n, np.int64), ed.a.to_numpy().astype(np.int64), ed.b.to_numpy().astype(np.int64), True)
    return roots(p)


if __name__ == "__main__":
    import multiprocessing as mp
    T0 = time.time()
    (io.CACHE / "variants").mkdir(exist_ok=True)
    o = origins()
    print("origins", len(o), o.src.value_counts().to_dict(), flush=True)
    ed = backbone(o)
    print("backbone", ed.kind.value_counts().to_dict(), flush=True)
    tab, edx, bad = backbone_report(o, ed)
    tab.to_csv(io.TAB / "t1_backbone_linked.csv", index=False)
    bad.to_csv(io.TAB / "t1_backbone_bad.csv", index=False)
    edx.groupby("kind").agg(n=("dt", "size"), dt50=("dt", "median"), dd50=("dd", "median"),
                            bad=("dt", lambda x: int(((x > 30) | (edx.loc[x.index, "dd"] > 100)).sum()))
                            ).to_csv(io.TAB / "t1_backbone_kinds.csv")
    C = cands(o)
    print("cands", len(C["a"]), round(time.time() - T0), flush=True)
    k = known_pairs(o, ed, C)
    pc = percentiles(k)
    pc.to_csv(io.TAB / "t1_window_percentiles.csv", index=False)
    cal = cal_table(pc)
    cal.to_csv(io.TAB / "t1_calibrated_windows.csv")
    w = pc[pc.per.isna() & pc.mb.isna()].set_index("pair")
    p99 = {"dt": w.dt_p99.clip(lower=5), "dd": w.dd_p99.clip(lower=25)}
    ce = cal_edges(C, o, cal)
    grid = [(a, b, c, d, e) for a in TW for b in DW for c in SCALE for d in ASSIGN for e in ORDER]
    grid += [("cal", "cal", c, d, e) for c in SCALE for d in ASSIGN for e in ORDER]
    done = {}
    jf = io.CACHE / "grid.jsonl"
    if jf.exists():
        for ln in jf.read_text().splitlines():
            d = json.loads(ln)
            done[(d["tw"], d["dw"], d["scale"], d["assign"], d["order"])] = d
    todo = [g for g in grid if (str(g[0]), str(g[1]), g[2], g[3], g[4]) not in done]
    print("variants to run", len(todo), flush=True)
    with mp.get_context("fork").Pool(NPROC, initializer=init, initargs=(o, C, ed, p99, ce, bb_roots(o, ed))) as pool:
        with open(jf, "a") as f:
            for out in pool.imap_unordered(run_variant, todo):
                f.write(json.dumps(out, default=int) + "\n")
                f.flush()
                print(out["variant"], out["n_events"], out["splits"], out["false_merges"], out["secs"], flush=True)
    print("grid done", round(time.time() - T0), flush=True)
    init(o, C, ed, p99, ce, bb_roots(o, ed))
    finish(o, k, pc)
    print("tier 1 done", round(time.time() - T0), flush=True)

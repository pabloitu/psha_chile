"""C1-C2: read the frozen source tables and match them into earthquakes, one id each.

Identity links first (ISC event and origin ids, each agency's own solution inside the ISC event), then one-to-one
window matching of what is left, a second pass on the leftovers, copies of one earthquake merged (D-CAT-09), and
Ruiz and Madariaga (2018) attached to located events (D-CAT-11). Magnitude never decides a match (D-CAT-08).
Events a source flags as non-earthquakes are kept and marked (D-CAT-10). Ported from psha_chile8 catalog/match.py.
"""
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import linear_sum_assignment
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parents[3]
CFG = yaml.safe_load((ROOT / "config" / "catalog.yaml").read_text())
C = CFG["match"]
SRC = ROOT / CFG["inputs"]["sources"]
SOURCES = C["sources"]
SI = {s: i for i, s in enumerate(SOURCES)}
RULES = ["ref", "id", "foreign", "window", "second_pass", "same_source"]
T0 = np.datetime64("1900-01-01T00:00:00", "ms")


def table(s, kind):
    return SRC / f"{s}_{CFG['frozen'].get(s, CFG['frozen']['default'])}_{kind}.csv"


def tsec(s):
    """Seconds since 1900 from ISO strings (years before 1677 and partial dates work; unreadable gives NaN)."""
    s = pd.Series(s, dtype=object).reset_index(drop=True)
    t = pd.to_datetime(s, format="ISO8601", errors="coerce", utc=True).dt.tz_localize(None)
    v = (t - pd.Timestamp("1900-01-01")).dt.total_seconds().to_numpy()
    for i in np.flatnonzero(np.isnan(v) & s.notna().to_numpy()):
        try:
            v[i] = (np.datetime64(str(s[i]).replace("Z", ""), "ms") - T0) / np.timedelta64(1, "s")
        except ValueError:
            pass
    return v


def tstr(t, unit="ms"):
    t = np.atleast_1d(np.asarray(t, float))
    out = np.full(len(t), "", dtype=object)
    k = np.isfinite(t)
    out[k] = np.datetime_as_string(T0 + np.round(t[k] * 1000).astype("int64").astype("timedelta64[ms]"), unit=unit)
    return out


def year(t):
    return 1900 + np.asarray(t) / (365.2425 * 86400)


T_OLD = tsec([f"{C['old']['year']}-01-01"])[0]


def hav(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lo2 - lo1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def near(t1, la1, lo1, t2, la2, lo2, tmax, dmax):
    """Index pairs (i, j) of two origin sets within tmax s and dmax km, with dt = t2 - t1 and dd [km]."""
    k = np.argsort(t2, kind="stable")
    ts = t2[k]
    lo, hi = np.searchsorted(ts, t1 - tmax), np.searchsorted(ts, t1 + tmax, "right")
    n = hi - lo
    i = np.repeat(np.arange(len(t1)), n)
    j = k[np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n) + np.repeat(lo, n)]
    dd = hav(la1[i], lo1[i], la2[j], lo2[j])
    ok = dd <= dmax
    return i[ok], j[ok], (t2[j] - t1[i])[ok], dd[ok]


# C1 read
def load():
    """
    Records and origins of the frozen source tables.

    Returns
    -------
    o : one row per source event, with the origin used for matching (the preferred one; for GCMT the reference
        hypocentre) and its largest native magnitude (for the window widths only)
    A : every origin of those events
    """
    nm = CFG["read"]["not_max"]
    rec, org = [], []
    for s in SOURCES:
        e = pd.read_csv(table(s, "events"), low_memory=False, dtype={"src_id": str, "origin_id": str})
        e["t"] = tsec(e.time)
        if s == "cabello":
            e = e[year(e.t) < CFG["read"]["cabello_before"]]
        e["prime"] = e.prime.astype(str).str.lower().eq("true")
        m = pd.read_csv(table(s, "mags"), low_memory=False, dtype={"src_id": str})
        m["mag"] = pd.to_numeric(m.mag, errors="coerce")
        m = m[m.mag.notna() & m.src_id.isin(e.src_id)]
        m = m[~(m.agency.isin(nm["agencies"]) & m.mag_type.astype(str).str.lower().str.startswith(nm["type"]))]
        top = m.sort_values("mag", ascending=False, kind="stable").drop_duplicates("src_id").set_index("src_id")
        x = (e[~e.prime] if s == "gcmt" else e[e.prime]).drop_duplicates("src_id")
        rec.append(pd.DataFrame({
            "src": s, "sid": x.src_id.to_numpy(), "oid": x.origin_id.to_numpy(), "t": x.t.to_numpy(),
            "lat": x.lat.to_numpy(), "lon": x.lon.to_numpy(), "z": x.depth.to_numpy(),
            "etype": x.etype.fillna("earthquake").to_numpy(), "mmax": x.src_id.map(top.mag).to_numpy(),
            "mtype": x.src_id.map(top.mag_type).to_numpy(), "magency": x.src_id.map(top.agency).to_numpy(),
            "mmed": x.src_id.map(m.groupby("src_id").mag.median()).to_numpy()}))
        org.append(pd.DataFrame({"src": s, "sid": e.src_id.to_numpy(), "oid": e.origin_id.to_numpy(),
                                 "agency": e.agency.to_numpy(), "prime": e.prime.to_numpy(), "t": e.t.to_numpy(),
                                 "lat": e.lat.to_numpy(), "lon": e.lon.to_numpy(), "z": e.depth.to_numpy()}))
    o = pd.concat(rec, ignore_index=True)
    o = o.sort_values(["src", "sid"], key=lambda c: c.map(SI) if c.name == "src" else c, kind="stable")
    return o.reset_index(drop=True), pd.concat(org, ignore_index=True)


def candidates(o):
    """All pairs of records of different sources within the cap windows: a, b, dt = t_b - t_a, dd."""
    t, la, lo = o.t.to_numpy(), o.lat.to_numpy(), o.lon.to_numpy()
    src = o.src.map(SI).to_numpy()
    k = np.flatnonzero(np.isfinite(t) & np.isfinite(la) & np.isfinite(lo))
    out = []
    for c in np.array_split(k, max(1, len(k) // 50000)):
        i, j, dt, dd = near(t[c], la[c], lo[c], t[k], la[k], lo[k], C["cap"]["t"], C["cap"]["d"])
        i, j = c[i], k[j]
        ok = (i < j) & (src[i] != src[j])
        out.append(pd.DataFrame({"a": i[ok], "b": j[ok], "dt": dt[ok], "dd": dd[ok]}))
    return pd.concat(out, ignore_index=True)


class Groups:
    """Union-find over the records, with members, source mask and largest magnitude per group."""

    def __init__(self, o):
        n = len(o)
        self.p = np.arange(n)
        self.mem = [[i] for i in range(n)]
        self.mask = (1 << o.src.map(SI).to_numpy()).astype(np.int64)
        self.gm = np.nan_to_num(o.mmax.to_numpy(float), nan=0.0)
        self.edges = []

    def find(self, x):
        p = self.p
        r = x
        while p[r] != r:
            r = p[r]
        while p[x] != r:
            p[x], x = r, p[x]
        return r

    def join(self, a, b, rule):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if len(self.mem[ra]) < len(self.mem[rb]):
            ra, rb = rb, ra
        self.p[rb] = ra
        self.mem[ra] += self.mem[rb]
        self.mem[rb] = None
        self.mask[ra] |= self.mask[rb]
        self.gm[ra] = max(self.gm[ra], self.gm[rb])
        self.edges.append((a, b, RULES.index(rule)))

    def roots(self):
        p = self.p.copy()
        while True:
            q = p[p]
            if (q == p).all():
                return p
            p = q


def refs(o, r):
    """Reference member of each group: the best-located source; of several records of that source the one closest
    to the median origin time of the group. Indexed by root."""
    t = o.t.to_numpy()
    off = np.abs(t - pd.Series(t).groupby(r).transform("median").to_numpy())
    k = np.lexsort((o.sid.to_numpy(), np.nan_to_num(off), o.src.map(SI).to_numpy(), r))
    first = np.r_[True, r[k][1:] != r[k][:-1]]
    ref = np.full(len(o), -1)
    ref[r[k][first]] = k[first]
    return ref


def factor(m):
    f = np.ones(len(m))
    for thr, x in sorted(C["scale"]):
        f = np.where(m >= thr, x, f)
    return f


def window(sa, sb, m, tmin, W):
    """Windows of candidate pairs: the pair's table value widened by magnitude and capped; fixed old windows when
    either origin is before the old year. Returns T, D and the old flag."""
    f = factor(m)
    T, D = np.minimum(W[0][sa, sb] * f, C["cap"]["t"]), np.minimum(W[1][sa, sb] * f, C["cap"]["d"])
    old = tmin < T_OLD
    return np.where(old, C["old"]["t"], T), np.where(old, C["old"]["d"], D), old


def assign(x, g, cost):
    """One-to-one selection among candidate edges (x, g): minimum total cost per connected block (Hungarian)."""
    if not len(x):
        return np.zeros(0, bool)
    ux, rx = np.unique(x, return_inverse=True)
    ug, rg = np.unique(g, return_inverse=True)
    nx = len(ux)
    _, lab = connected_components(coo_matrix((np.ones(len(rx)), (rx, rg + nx)), shape=(nx + len(ug),) * 2),
                                  directed=False)
    sel = (np.bincount(rx, minlength=nx)[rx] == 1) & (np.bincount(rg, minlength=len(ug))[rg] == 1)
    idx = np.flatnonzero(~sel)
    idx = idx[np.argsort(lab[rx[idx]], kind="stable")]
    big = cost.max() * (len(idx) + 1) + 1 if len(idx) else 1.0
    for grp in np.split(idx, np.flatnonzero(np.diff(lab[rx[idx]])) + 1) if len(idx) else []:
        _, i = np.unique(rx[grp], return_inverse=True)
        _, j = np.unique(rg[grp], return_inverse=True)
        M = np.full((i.max() + 1, j.max() + 1), big)
        M[i, j] = cost[grp]
        pos = np.full(M.shape, -1)
        pos[i, j] = grp
        rr, cc = linear_sum_assignment(M)
        ok = M[rr, cc] < big
        sel[pos[rr[ok], cc[ok]]] = True
    return sel


# identity links
def identity(o, A):
    """Edges between records from ISC event / origin ids (kind id) and from an agency's own solution found inside an
    ISC event within the id windows (kind foreign); dt, dd between the two matching origins."""
    t, la, lo = o.t.to_numpy(), o.lat.to_numpy(), o.lon.to_numpy()
    idx = lambda s: pd.Series(o.index[o.src == s], index=o.sid[o.src == s])
    isc, gem = idx("isc"), idx("iscgem")
    ed = []
    for s in ("iscgem", "csn_isc"):
        x = o[o.src == s]
        ed.append(pd.DataFrame({"a": x.index, "b": x.sid.map(isc).to_numpy(), "kind": "id"}))
    x = o[o.src == "iscehb"]
    io = A[A.src == "isc"]
    ev = x.oid.map(pd.Series(io.sid.to_numpy(), index=io.oid.to_numpy()))
    ed.append(pd.DataFrame({"a": x.index, "b": ev.map(isc).to_numpy(), "kind": "id"}))
    x = o[o.src == "comcat"]
    num = x.sid.str.extract(r"^iscgem(?:sup)?(\d+)$")[0]
    ed.append(pd.DataFrame({"a": x.index, "b": num.map(gem).to_numpy(), "kind": "id"}))
    ed.append(pd.DataFrame({"a": x.index, "b": num.map(isc).to_numpy(), "kind": "id"}))
    cen = A[(A.src == "gcmt") & A.prime]
    T, D = C["id"]["t"], C["id"]["d"]
    for s, ags in C["foreign"].items():
        x = o[o.src == s]
        if s == "gcmt":
            c = cen.set_index("sid").reindex(x.sid)
            xt, xa, xo = c.t.to_numpy(), c.lat.to_numpy(), c.lon.to_numpy()
        else:
            xt, xa, xo = x.t.to_numpy(), x.lat.to_numpy(), x.lon.to_numpy()
        b = io[io.agency.isin(ags) & io.sid.isin(isc.index)]
        if not len(x) or not len(b):
            continue
        i, j, dt, dd = near(xt, xa, xo, b.t.to_numpy(), b.lat.to_numpy(), b.lon.to_numpy(), T, D)
        k = pd.DataFrame({"a": x.index.to_numpy()[i], "j": j, "c": np.abs(dt) / T + dd / D})
        k = k.sort_values("c", kind="stable").drop_duplicates("a").drop_duplicates("j")
        ed.append(pd.DataFrame({"a": k.a.to_numpy(), "b": b.sid.map(isc).to_numpy()[k.j.to_numpy()],
                                "kind": "foreign", "c": k.c.to_numpy()}))
    ed = pd.concat(ed, ignore_index=True).dropna(subset=["b"]).reindex(columns=["a", "b", "kind", "c"])
    ed["b"] = ed.b.astype(int)
    ed["k"] = ed.kind.eq("foreign")
    ed = ed.sort_values(["k", "c", "a", "b"], kind="stable").drop_duplicates(["a", "b"]).reset_index(drop=True)
    a, b = ed.a.to_numpy(), ed.b.to_numpy()
    ed["dt"], ed["dd"] = t[a] - t[b], hav(la[a], lo[a], la[b], lo[b])
    return ed.drop(columns=["c", "k"])


def backbone(o, ed, G):
    """Join the identity edges. Two records of one source end in one event only if they lie within the second-pass
    window of each other; otherwise the edge is refused."""
    t, la, lo, src = o.t.to_numpy(), o.lat.to_numpy(), o.lon.to_numpy(), o.src.to_numpy()
    sp = C["second_pass"]
    for a, b, kind in zip(ed.a.to_numpy(), ed.b.to_numpy(), ed.kind.to_numpy()):
        ra, rb = G.find(a), G.find(b)
        if ra != rb and G.mask[ra] & G.mask[rb]:
            f = factor(np.array([max(G.gm[ra], G.gm[rb])]))[0]
            same = [(i, j) for i in G.mem[ra] for j in G.mem[rb] if src[i] == src[j]]
            if any(abs(t[i] - t[j]) > sp["t"] * f or hav(la[i], lo[i], la[j], lo[j]) > sp["d"] * f for i, j in same):
                continue
        G.join(a, b, kind)


# windows from known same-event pairs
def known_pairs(o, bb, Cp):
    """Pairs of records that are the same event: members of one identity group, and for the nearest source pairs the
    one-to-one nearest pairs within the old windows."""
    src = o.src.to_numpy()
    g = pd.DataFrame({"g": bb, "i": np.arange(len(o))})
    g = g[g.groupby("g").i.transform("size") > 1]
    k = g.merge(g, on="g")
    k = k[k.i_x < k.i_y].rename(columns={"i_x": "a", "i_y": "b"})[["a", "b"]].assign(kind="id")
    sa, sb = src[Cp.a.to_numpy()], src[Cp.b.to_numpy()]
    close = ((Cp.dt.abs() <= C["old"]["t"]) & (Cp.dd <= C["old"]["d"])).to_numpy()
    for s1, s2 in C["nearest"]:
        c = Cp[(((sa == s1) & (sb == s2)) | ((sa == s2) & (sb == s1))) & close]
        sw = src[c.a.to_numpy()] == s2
        x, y = np.where(sw, c.b, c.a), np.where(sw, c.a, c.b)
        sel = assign(x, y, np.hypot(c.dt.to_numpy() / C["floor"]["t"], c.dd.to_numpy() / C["floor"]["d"]))
        k = pd.concat([k, pd.DataFrame({"a": x[sel], "b": y[sel], "kind": "nearest"})], ignore_index=True)
    k = k[src[k.a.to_numpy()] != src[k.b.to_numpy()]]
    a, b = o.iloc[k.a.to_numpy()], o.iloc[k.b.to_numpy()]
    k["pair"] = ["|".join(sorted(p)) for p in zip(a.src.to_numpy(), b.src.to_numpy())]
    k["dt"] = np.abs(a.t.to_numpy() - b.t.to_numpy())
    k["dd"] = hav(a.lat.to_numpy(), a.lon.to_numpy(), b.lat.to_numpy(), b.lon.to_numpy())
    k["old"] = np.minimum(a.t.to_numpy(), b.t.to_numpy()) < T_OLD
    return k[np.isfinite(k.dt) & np.isfinite(k.dd)].drop_duplicates(["a", "b"]).reset_index(drop=True)


def windows(k):
    """
    Window table per pair of sources.

    The 99th percentile of the same-event offsets from the old year on, between the floor and the cap. A pair with
    too few known pairs combines the two windows through the shared source that gives the smallest distance
    (quadrature sum); the no-pair default if there is none.
    """
    q = lambda v, p: float(np.percentile(v, p)) if len(v) else np.nan
    fl, cap = C["floor"], C["cap"]
    rows = {}
    for pair, g in k.groupby("pair"):
        n, old = g[~g.old], g[g.old]
        rows[pair] = {"n": len(n), **{f"{v}_p{p}": q(n[v], p) for v in ("dt", "dd") for p in (50, 95, 99)},
                      "n_old": len(old), "dt_p99_old": q(old.dt, 99), "dd_p99_old": q(old.dd, 99)}
    key = lambda a, b: "|".join(sorted((a, b)))
    cal = {p: (float(np.clip(r["dt_p99"], fl["t"], cap["t"])), float(np.clip(r["dd_p99"], fl["d"], cap["d"])))
           for p, r in rows.items() if r["n"] >= C["n_min"]}
    out = []
    for i, a in enumerate(SOURCES):
        for b in SOURCES[i + 1:]:
            p = key(a, b)
            if p in cal:
                T, D, how = *cal[p], "measured"
            else:
                via = [(np.hypot(cal[key(a, h)][1], cal[key(b, h)][1]), np.hypot(cal[key(a, h)][0], cal[key(b, h)][0]), h)
                       for h in SOURCES if h not in (a, b) and key(a, h) in cal and key(b, h) in cal]
                D, T, h = min(via) if via else (C["nopair"]["d"], C["nopair"]["t"], None)
                T, D = min(max(T, fl["t"]), cap["t"]), min(max(D, fl["d"]), cap["d"])
                how = f"via {h}" if h else "default"
            out.append({"pair": p, "T": round(T, 2), "D": round(D, 1), "how": how, **rows.get(p, {"n": 0, "n_old": 0})})
    return pd.DataFrame(out)


def wmat(wt):
    W = np.full((2, len(SOURCES), len(SOURCES)), np.nan)
    for p, T, D in zip(wt.pair, wt["T"], wt["D"]):
        a, b = (SI[s] for s in p.split("|"))
        W[:, a, b] = W[:, b, a] = T, D
    return W


# window matching
def attach(o, G, Cp, W, s, among):
    """
    Attach the single records of source s to the groups that have no record of s, one-to-one.

    A record and a group are candidates if the record lies within the window of a member of the group; the cost is
    the smallest hypot(dt / T, dd / D) over those members. Only groups holding a source of the mask `among` are
    targets. Returns the accepted links with dt, dd, T, D, cost, old and n (number of candidates).
    """
    src, t = o.src.map(SI).to_numpy(), o.t.to_numpy()
    r = G.roots()
    size = np.bincount(r, minlength=len(o))
    si = SI[s]
    a, b = Cp.a.to_numpy(), Cp.b.to_numpy()
    fa = (src[a] == si) & (size[r[a]] == 1) & ((G.mask[r[b]] >> si) & 1 == 0)
    fb = (src[b] == si) & (size[r[b]] == 1) & ((G.mask[r[a]] >> si) & 1 == 0)
    k = (fa | fb) & ((G.mask[r[np.where(fa, b, a)]] & among) != 0)
    x, y = np.where(fa, a, b)[k], np.where(fa, b, a)[k]
    dt, dd = np.where(fa, Cp.dt.to_numpy(), -Cp.dt.to_numpy())[k], Cp.dd.to_numpy()[k]
    g = r[y]
    T, D, old = window(src[x], src[y], np.maximum(G.gm[r[x]], G.gm[g]), np.minimum(t[x], t[y]), W)
    k = (np.abs(dt) <= T) & (dd <= D)
    c = pd.DataFrame({"x": x[k], "y": y[k], "g": g[k], "dt": dt[k], "dd": dd[k], "T": T[k], "D": D[k], "old": old[k]})
    c["cost"] = np.hypot(c.dt / c["T"], c.dd / c["D"])
    c = c.sort_values(["cost", "x", "y"], kind="stable").drop_duplicates(["x", "g"]).reset_index(drop=True)
    if not len(c):
        return c.assign(n=[], src=s)
    c["sel"] = assign(c.x.to_numpy(), c.g.to_numpy(), c.cost.to_numpy())
    c["n"] = np.maximum(c.groupby("x").g.transform("size"), c.groupby("g").x.transform("size"))
    c = c[c.sel].drop(columns=["sel", "g"]).reset_index(drop=True)
    for xi, yi in zip(c.x.to_numpy(), c.y.to_numpy()):
        G.join(xi, yi, "window")
    return c.assign(src=s)


def second_pass(o, G, Cp):
    """Merge groups that share no source and have members within the second-pass windows of each other, widened by
    magnitude (the old windows before the old year); closest pairs first."""
    r = G.roots()
    a, b = Cp.a.to_numpy(), Cp.b.to_numpy()
    k = (r[a] != r[b]) & ((G.mask[r[a]] & G.mask[r[b]]) == 0)
    c = Cp[k].copy()
    f = factor(np.maximum(G.gm[r[c.a.to_numpy()]], G.gm[r[c.b.to_numpy()]]))
    c["old"] = np.minimum(o.t.to_numpy()[c.a.to_numpy()], o.t.to_numpy()[c.b.to_numpy()]) < T_OLD
    sp, cap = C["second_pass"], C["cap"]
    c["T"] = np.where(c.old, C["old"]["t"], np.minimum(sp["t"] * f, cap["t"]))
    c["D"] = np.where(c.old, C["old"]["d"], np.minimum(sp["d"] * f, cap["d"]))
    c = c[(c.dt.abs() <= c["T"]) & (c.dd <= c["D"])]
    c["cost"] = np.hypot(c.dt / c["T"], c.dd / c["D"])
    done = []
    for row in c.sort_values(["cost", "a", "b"], kind="stable").itertuples(index=False):
        ra, rb = G.find(row.a), G.find(row.b)
        if ra != rb and not G.mask[ra] & G.mask[rb]:
            G.join(row.a, row.b, "second_pass")
            done.append(row)
    return pd.DataFrame(done, columns=c.columns)


def same_source(o, G):
    """Merge two groups that share sources when, for every shared source, their records of that source lie within
    same_t and the second-pass distance of each other (widened by magnitude): one earthquake listed twice."""
    t, la, lo, src = o.t.to_numpy(), o.lat.to_numpy(), o.lon.to_numpy(), o.src.map(SI).to_numpy()
    k = np.flatnonzero(np.isfinite(t))
    i, j, dt, dd = near(t[k], la[k], lo[k], t[k], la[k], lo[k], C["same_t"] * max(x for _, x in C["scale"]),
                        C["cap"]["d"])
    i, j = k[i], k[j]
    w = (i < j) & (src[i] == src[j])
    c = pd.DataFrame({"a": i[w], "b": j[w], "dt": dt[w], "dd": dd[w]})
    r = G.roots()
    c = c[r[c.a.to_numpy()] != r[c.b.to_numpy()]]
    done = []
    for row in c.sort_values(["dt", "dd", "a", "b"], key=lambda v: v.abs(), kind="stable").itertuples(index=False):
        ra, rb = G.find(row.a), G.find(row.b)
        if ra == rb:
            continue
        f = factor(np.array([max(G.gm[ra], G.gm[rb])]))[0]
        T, D = C["same_t"] * f, min(C["second_pass"]["d"] * f, C["cap"]["d"])
        ok = True
        for q in np.flatnonzero([(G.mask[ra] & G.mask[rb]) >> n & 1 for n in range(len(SOURCES))]):
            xa, xb = [m for m in G.mem[ra] if src[m] == q], [m for m in G.mem[rb] if src[m] == q]
            ok &= any(abs(t[u] - t[v]) <= T and hav(la[u], lo[u], la[v], lo[v]) <= D for u in xa for v in xb)
        if ok:
            G.join(row.a, row.b, "same_source")
            done.append(row)
    return pd.DataFrame(done, columns=c.columns)


def match(o, A):
    """
    Group the records of all sources into events.

    Returns a dict: ev (group label per record), ref (reference record per label), rule (per record, the weakest link
    on its path to the reference member), wt (window table), wl (window links), sp (second-pass merges).
    """
    Cp = candidates(o)
    G = Groups(o)
    backbone(o, identity(o, A), G)
    wt = windows(known_pairs(o, G.roots(), Cp))
    W = wmat(wt)
    st = [s for s in C["stages"] if (o.src == s).any()]
    wl = [attach(o, G, Cp, W, s, sum(1 << SI[q] for q in ["isc"] + st[:k])) for k, s in enumerate(st)]
    wl = pd.concat(wl, ignore_index=True)
    sp = second_pass(o, G, Cp)
    same_source(o, G)
    ev = G.roots()
    ref = refs(o, ev)
    adj = [[] for _ in range(len(o))]
    for a, b, k in G.edges:
        adj[a].append((b, k))
        adj[b].append((a, k))
    rule = np.zeros(len(o), int)
    seen = np.zeros(len(o), bool)
    for i in np.unique(ref[ev]):
        seen[i] = True
        q = deque([i])
        while q:
            u = q.popleft()
            for v, k in adj[u]:
                if not seen[v]:
                    seen[v], rule[v] = True, max(rule[u], k)
                    q.append(v)
    return {"ev": ev, "ref": ref, "rule": np.array(RULES)[rule], "wt": wt, "wl": wl, "sp": sp}


# tables
def nonquake(o, ev):
    """Per record: the non-earthquake type of its event (first flagged member, as 'src id: type'), else empty."""
    bad = o.etype.str.lower().ne("earthquake").to_numpy()
    why = pd.Series(np.where(bad, o.src + " " + o.sid + ": " + o.etype, None)).groupby(ev).transform("first")
    return why.fillna("").to_numpy()


def lone_dups(o, ev, ref):
    """
    Events of one lone source (Potin, CSN web) that duplicate an ISC event located far away.

    Two events within the wide windows and at least lone d apart, with no source in common and no other event inside
    the wide windows of either; one has only records of a lone source, the other an ISC record; the larger native
    magnitude reaches lone m. Returns the record mask and, per record, the reference record it duplicates.
    """
    L = C["lone"]
    lab = np.unique(ev)
    i = ref[lab]
    t, la, lo = (o[c].to_numpy(float)[i] for c in ("t", "lat", "lon"))
    bit = (1 << o.src.map(SI).to_numpy()).astype(np.int64)
    mask = pd.Series(bit).groupby(ev).agg(np.bitwise_or.reduce).reindex(lab).to_numpy()
    m = pd.Series(o.mmax.to_numpy(float)).groupby(ev).max().reindex(lab).fillna(0).to_numpy()
    ok = np.isfinite(t) & np.isfinite(la) & np.isfinite(lo)
    a, b, dt, dd = near(t[ok], la[ok], lo[ok], t[ok], la[ok], lo[ok], L["wide_t"], L["wide_d"])
    k = (a < b) & (np.abs(dt) < L["wide_t"]) & (dd < L["wide_d"])
    a, b, dd = np.flatnonzero(ok)[a[k]], np.flatnonzero(ok)[b[k]], dd[k]
    n = np.bincount(np.r_[a, b], minlength=len(lab))
    k = (n[a] == 1) & (n[b] == 1) & (mask[a] & mask[b] == 0) & (dd >= L["d"]) & (np.maximum(m[a], m[b]) >= L["m"])
    a, b = a[k], b[k]
    lone = np.isin(mask, [1 << SI[s] for s in L["sources"]])
    isc = (mask >> SI["isc"]) & 1 == 1
    x = np.r_[a[lone[a] & isc[b]], b[lone[b] & isc[a]]]
    y = np.r_[b[lone[a] & isc[b]], a[lone[b] & isc[a]]]
    of = pd.Series(ev).map(pd.Series(i[y], index=lab[x])).fillna(-1).astype(int).to_numpy()
    return of >= 0, of


def event_ids(o, ev, ref, keep):
    """cl + origin time of the reference member to the second, letters on collisions (by time, lat, source)."""
    lab = np.unique(ev[keep])
    i = ref[lab]
    base = pd.Series(tstr(np.floor(o.t.to_numpy()[i]), "s")).str.replace(r"[-:T]", "", regex=True).radd("cl")
    d = pd.DataFrame({"lab": lab, "base": base.to_numpy(), "t": o.t.to_numpy()[i], "lat": o.lat.to_numpy()[i],
                      "src": o.src.to_numpy()[i], "sid": o.sid.to_numpy()[i]})
    d = d.sort_values(["base", "t", "lat", "src", "sid"], kind="stable")
    n, k = d.groupby("base").base.transform("size"), d.groupby("base").cumcount()
    d["id"] = np.where(n > 1, d.base + k.map(lambda v: chr(97 + v % 26) * (1 + v // 26)), d.base)
    return pd.Series(d.id.to_numpy(), index=d.lab.to_numpy())


def tables(o, A, res):
    """events, links and dropped tables. dropped holds the records of the lone-source duplicates of ISC events."""
    ev, ref, wl, sp = res["ev"], res["ref"], res["wl"], res["sp"]
    dup, of = lone_dups(o, ev, ref)
    j = of[dup]
    far = hav(o.lat.to_numpy()[dup], o.lon.to_numpy()[dup], o.lat.to_numpy()[j], o.lon.to_numpy()[j])
    why = [f"same earthquake as {s} {q} ({dt:+.1f} s, {dd:.0f} km)" for s, q, dt, dd in
           zip(o.src.to_numpy()[j], o.sid.to_numpy()[j], o.t.to_numpy()[dup] - o.t.to_numpy()[j], far)]
    ids = event_ids(o, ev, ref, ~dup)
    o = o.assign(ev=ev, rule=res["rule"], event_id=pd.Series(ev).map(ids).to_numpy(), ri=ref[ev], nq=nonquake(o, ev))
    dropped = o[dup].assign(reason=why)[["src", "sid", "oid", "reason", "t", "lat", "lon", "mmax"]]
    dropped = dropped.assign(time=tstr(dropped.t)).drop(columns="t").rename(columns={"sid": "src_id", "oid": "origin_id"})
    k = o[~dup]
    top = k.sort_values("mmax", ascending=False, kind="stable").drop_duplicates("ev").set_index("ev")
    g = k.groupby("ev")
    flag = lambda rows: pd.Series(True, index=np.unique(ev[np.asarray(rows, int)])) if len(rows) else pd.Series(dtype=bool)
    r = k[k.index == k.ri].set_index("ev").sort_index()
    e = pd.DataFrame({
        "event_id": r.event_id, "time": pd.Series(tstr(r.t), index=r.index), "lon": r.lon, "lat": r.lat, "depth": r.z,
        "ref_src": r.src, "ref_id": r.sid, "sources": g.src.agg(lambda s: ",".join(sorted(set(s), key=SI.get))),
        "n_sources": g.src.nunique(), "n_members": g.size(), "mmax": top.mmax, "mmax_type": top.mtype,
        "mmax_agency": top.magency, "nonquake": r.nq})
    e["pre1964_window"] = flag(list(wl.x[wl.old]) + list(sp.a[sp.old])).reindex(e.index, fill_value=False)
    e["ambiguous"] = flag(wl.x[wl.n > 1]).reindex(e.index, fill_value=False)
    e["t"] = r.t
    e = e.sort_values(["t", "event_id"]).reset_index(drop=True)
    rec = k[["src", "sid", "event_id", "rule", "ri"]].rename(columns={"sid": "src_id"})
    L = A.rename(columns={"sid": "src_id", "oid": "origin_id"}).merge(rec, on=["src", "src_id"])
    rt, ra, ro, rz = (o[c].to_numpy()[L.ri.to_numpy()] for c in ("t", "lat", "lon", "z"))
    L["dt"], L["dd"] = (L.t - rt).round(2), hav(L.lat.to_numpy(), L.lon.to_numpy(), ra, ro).round(2)
    L["dz"] = (L.z - rz).round(2)
    used = set(zip(o.src, o.oid))
    L["used"] = [p in used for p in zip(L.src, L.origin_id)]
    L = L.sort_values(["event_id", "src", "src_id", "origin_id"], key=lambda c: c.map(SI) if c.name == "src" else c,
                      kind="stable")
    return e, L[["event_id", "src", "src_id", "origin_id", "rule", "dt", "dd", "dz", "used", "agency"]], dropped, o


def rm18(e, o):
    """
    Ruiz and Madariaga (2018) events on located events (D-CAT-11).

    Dates fixed first. One event each, larger events first: date within the day window, latitude within the latitude
    window, event magnitude (largest per-source median) at least m_min, closest to the RM18 Mw (the largest where it
    gives none). Returns the matches, the unmatched rows and the link rows.
    """
    R = C["rm"]
    x = pd.read_csv(table("rm2018", "events"), dtype=str)
    m = pd.read_csv(table("rm2018", "mags"), dtype=str).drop_duplicates("src_id").set_index("src_id")
    x["mw"] = pd.to_numeric(x.src_id.map(m.mag), errors="coerce")
    x["date"] = x.src_id.map(R["dates"]).fillna(x.time)
    x["lat"] = pd.to_numeric(x.lat, errors="coerce")
    e = e.assign(med=e.event_id.map(o.groupby("event_id").mmed.max()))
    taken, hit, miss = set(), [], []
    for r in x.sort_values("mw", ascending=False, na_position="last", kind="stable").itertuples():
        base = {"rm18": r.src_id, "rm_date": r.date, "rm_lat": r.lat, "rm_mw": r.mw, "rm_class": r.rm_class}
        if len(r.date) < 10:
            miss.append({**base, "why": "year or month only"})
            continue
        t0 = tsec([r.date[:10]])[0]
        w = e[(e.t >= t0 - R["days"] * 86400) & (e.t < t0 + (R["days"] + 1) * 86400) & ((e.lat - r.lat).abs() <= R["lat"])
              & (e.med.fillna(0) >= R["m_min"]) & ~e.event_id.isin(taken)]
        if not len(w):
            miss.append({**base, "why": "no event within the date, latitude and magnitude limits"})
            continue
        y = w.loc[(w.med - r.mw).abs().idxmin() if np.isfinite(r.mw) else w.med.idxmax()]
        taken.add(y.event_id)
        hit.append({**base, "event_id": y.event_id, "time": y.time, "lat": y.lat, "lon": y.lon, "m_event": y.med,
                    "n_candidates": len(w)})
    hit, miss = pd.DataFrame(hit), pd.DataFrame(miss)
    lk = pd.DataFrame({"event_id": hit.event_id, "src": "rm2018", "src_id": hit.rm18, "origin_id": hit.rm18,
                       "rule": "rm18", "used": True, "agency": "rm2018"})
    return hit, miss, lk


def merges(e, L, f):
    """
    Duplicate events and the event their records join (D-CAT-09): the accepted rows of the duplicates file, then the
    lone ISC copies (one ISC record whose prime origin is not ISC's own) within the isc_copy windows of the nearest
    event with records from two or more sources. Returns event_id, into, reason, dt, dd.
    """
    rows = []
    if Path(f).exists():
        d = pd.read_csv(f, dtype=str)
        rows += [(r.event_id, r.into, "reviewed (duplicates.csv)", np.nan, np.nan)
                 for r in d[d.status == "accepted"].itertuples()]
    isc = pd.read_csv(table("isc", "events"), dtype={"src_id": str}, usecols=["src_id", "agency", "prime"])
    own = set(isc.src_id[isc.prime.astype(str).eq("True") & isc.agency.ne("ISC")])
    L = L[L.src != "rm2018"].drop_duplicates(["event_id", "src", "src_id"])
    n = L.groupby("event_id").src.nunique()
    r1 = L.drop_duplicates("event_id").set_index("event_id").reindex(n.index)
    lone = set(n.index[(n == 1) & r1.src.eq("isc") & r1.src_id.isin(own)]) - {r[0] for r in rows}
    x = e.sort_values("t")
    t, lo, la, ev = x.t.to_numpy(), x.lon.to_numpy(), x.lat.to_numpy(), x.event_id.to_numpy()
    full = n.reindex(ev).fillna(0).to_numpy() >= 2
    dt, dkm = C["isc_copy"]["t"], C["isc_copy"]["d"]
    for i in np.flatnonzero(np.isin(ev, list(lone))):
        j = np.arange(*np.searchsorted(t, [t[i] - dt, t[i] + dt]))
        j = j[full[j]]
        km = 111.2 * np.hypot((lo[j] - lo[i]) * np.cos(np.radians(la[i])), la[j] - la[i])
        if (km <= dkm).any():
            k = j[np.argmin(km)]
            rows.append((ev[i], ev[k], "single-agency ISC copy", round(t[k] - t[i], 2), round(km.min(), 1)))
    return pd.DataFrame(rows, columns=["event_id", "into", "reason", "dt", "dd"])


def merged(L, e, m):
    """Links and events after the merges m: the records of each duplicate carry the kept event's id, except records
    of a source the kept event already has (one record per source is kept)."""
    mp = m.set_index("event_id").into
    has = set(zip(L.event_id, L.src))
    cp = L.event_id.isin(mp.index)
    dup = cp.to_numpy() & np.array([(k, s) in has for k, s in zip(L.event_id.map(mp), L.src)], bool)
    L = L[~dup].assign(event_id=L.event_id[~dup].replace(mp))
    keep = e[~e.event_id.isin(mp.index)].copy()
    nq = e[e.event_id.isin(mp.index) & e.nonquake.ne("")].assign(into=lambda d: d.event_id.map(mp))
    keep.loc[keep.event_id.isin(nq.into) & keep.nonquake.eq(""), "nonquake"] = keep.event_id.map(
        nq.set_index("into").nonquake)
    return L, keep


def run():
    """C1-C2: events (after the merges), links, dropped records, windows, merges, Ruiz and Madariaga matches."""
    o, A = load()
    res = match(o, A)
    e, L, dropped, ox = tables(o, A, res)
    hit, miss, lk = rm18(e, ox[ox.event_id.notna()])
    L = pd.concat([L, lk], ignore_index=True)
    own = L[L.src != "rm2018"]
    assert not own.duplicated(["src", "src_id", "origin_id"]).any()
    assert own.groupby(["src", "src_id"]).event_id.nunique().max() == 1
    assert set(own.event_id) == set(e.event_id) and e.event_id.is_unique
    assert len(own) + A.set_index(["src", "sid"]).index.isin(
        pd.MultiIndex.from_frame(dropped[["src", "src_id"]])).sum() == len(A)
    m = merges(e, L, ROOT / CFG["inputs"]["duplicates"])
    L, e = merged(L, e, m)
    return {"events": e, "links": L, "dropped": dropped, "windows": res["wt"], "merges": m, "rm_matches": hit,
            "rm_missing": miss}

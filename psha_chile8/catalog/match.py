"""Match the frozen source catalogues into earthquakes, one ID each (plan A3).

Identity links first (ISC event and origin IDs, each agency's own solution inside the ISC event), then
one-to-one window matching of what is left, a second pass on the leftovers, and Ruiz and Madariaga (2018)
attached to located events. Nothing is chosen: no location, depth or magnitude. Method and references in
merged/METHOD.md; outputs in merged/, review lists in merged/review/.
"""
import hashlib
import re
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

HERE = Path(__file__).resolve().parent

# settings
RUN = "2026-11-11"
FROZEN = "2026-11-10"
DATES = {"gccel": "2026-11-11"}
SRC = HERE / "sources"
OUT = HERE / "merged"
FIG = HERE / "figs" / "match"
# best-located first: the reference member of an event is its first source in this list
SOURCES = ["potin", "gccel", "iscehb", "iscgem", "centennial", "csn", "isc", "comcat", "csn_isc", "gcmt", "cabello"]
# attach order of the single records: leftovers of the sources with identity links, then the window-only sources
STAGES = ["iscehb", "iscgem", "centennial", "comcat", "csn_isc", "gcmt", "gccel", "potin", "csn", "cabello"]
CABELLO_BEFORE = 1904
FOREIGN = {"comcat": ["NEIC", "USCGS", "NEIS", "NEIC-US", "GUC", "SJA", "LIM"], "gcmt": ["GCMT"], "centennial": ["CENT"], "csn": ["GUC"]}
ID_T, ID_D = 1.5, 10.0
BAD_T, BAD_D = 30.0, 100.0
FLOOR_T, FLOOR_D = 10.0, 50.0
TMAX, DMAX = 120.0, 450.0
NOPAIR_T, NOPAIR_D = 20.0, 100.0
NMIN = 100
SCALE = [(8.0, 3.0), (7.0, 2.0), (6.0, 1.5)]
OLD_YEAR, OLD_T, OLD_D = 1964, 60.0, 300.0
SP_T, SP_D = 10.0, 50.0
SAME_T = 2.0
WIDE_T, WIDE_D = 30.0, 150.0
NEAREST = [("potin", "csn_isc"), ("csn", "potin"), ("gcmt", "comcat"), ("csn", "csn_isc"), ("gccel", "isc")]
LINK = "member"
NOT_MAX = (["IDC", "EIDC"], "mb")
RM_DATE = {"Copiapo 1918": "1918-12-04", "Arauco 1975": "1975-05-10", "Copiapo 1983": "1983-10-04",
           "Antofagasta 1995": "1995-07-30", "Copiapo 1959": "1859-10-05", "Mejillones 1994": "1994-12-10"}
RM_DAYS, RM_LAT, RM_MMIN = 1, 2.0, 5.5
KEEP = []
SLIDES = [-1200.0, -600.0, 600.0, 1200.0]
BLIND = ["comcat", "gcmt", "iscehb", "iscgem", "centennial", "csn_isc"]

SI = {s: i for i, s in enumerate(SOURCES)}
RULES = ["ref", "id", "foreign", "window", "second_pass", "same_source"]
T0 = np.datetime64("1900-01-01T00:00:00", "ms")
NAME = {"potin": "Potin et al.", "gccel": "GCCEL", "iscehb": "ISC-EHB", "iscgem": "ISC-GEM", "centennial": "Centennial",
        "csn": "CSN web", "isc": "ISC Bulletin", "comcat": "ComCat", "csn_isc": "CSN in ISC", "gcmt": "GCMT",
        "cabello": "Cabello et al."}


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


T64 = tsec([f"{OLD_YEAR}-01-01"])[0]


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


# inputs
def load(d=SRC, sources=SOURCES):
    """
    Records and origins of the frozen source tables.

    Returns
    -------
    o : one row per source event, with the origin used for matching (the preferred one; for GCMT the
        reference hypocentre) and its largest native magnitude
    A : every origin of those events
    """
    rec, org = [], []
    for s in sources:
        f = Path(d) / f"{s}_{DATES.get(s, FROZEN)}_events.csv"
        if not f.exists():
            print("no frozen table, skipped:", s)
            continue
        e = pd.read_csv(f, low_memory=False, dtype={"src_id": str, "origin_id": str})
        e["t"] = tsec(e.time)
        if s == "cabello":
            e = e[year(e.t) < CABELLO_BEFORE]
        e["prime"] = e.prime.astype(str).str.lower().eq("true")
        m = pd.read_csv(str(f).replace("_events", "_mags"), low_memory=False, dtype={"src_id": str})
        m["mag"] = pd.to_numeric(m.mag, errors="coerce")
        m = m[m.mag.notna() & m.src_id.isin(e.src_id)]
        m = m[~(m.agency.isin(NOT_MAX[0]) & m.mag_type.astype(str).str.lower().str.startswith(NOT_MAX[1]))]
        top = m.sort_values("mag", ascending=False, kind="stable").drop_duplicates("src_id").set_index("src_id")
        x = e[~e.prime] if s == "gcmt" else e[e.prime]
        x = x.drop_duplicates("src_id")
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
    """All pairs of records of different sources within TMAX and DMAX: a, b, dt = t_b - t_a, dd."""
    t, la, lo = o.t.to_numpy(), o.lat.to_numpy(), o.lon.to_numpy()
    src = o.src.map(SI).to_numpy()
    k = np.flatnonzero(np.isfinite(t) & np.isfinite(la) & np.isfinite(lo))
    out = []
    for c in np.array_split(k, max(1, len(k) // 50000)):
        i, j, dt, dd = near(t[c], la[c], lo[c], t[k], la[k], lo[k], TMAX, DMAX)
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
    """Reference member of each group: the best-located source; of several records of that source the one
    closest to the median origin time of the group. Indexed by root."""
    t = o.t.to_numpy()
    off = np.abs(t - pd.Series(t).groupby(r).transform("median").to_numpy())
    k = np.lexsort((o.sid.to_numpy(), np.nan_to_num(off), o.src.map(SI).to_numpy(), r))
    first = np.r_[True, r[k][1:] != r[k][:-1]]
    ref = np.full(len(o), -1)
    ref[r[k][first]] = k[first]
    return ref


def factor(m):
    f = np.ones(len(m))
    for thr, x in sorted(SCALE):
        f = np.where(m >= thr, x, f)
    return f


def window(sa, sb, m, tmin, W):
    """Time and distance windows of candidate pairs: the pair's table value, widened by magnitude, capped;
    fixed OLD_T / OLD_D when either origin is before OLD_YEAR. Returns T, D and the old flag."""
    f = factor(m)
    T, D = np.minimum(W[0][sa, sb] * f, TMAX), np.minimum(W[1][sa, sb] * f, DMAX)
    old = tmin < T64
    return np.where(old, OLD_T, T), np.where(old, OLD_D, D), old


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
    """Edges between records from ISC event / origin IDs (kind id) and from an agency's own solution found
    inside an ISC event within ID_T and ID_D (kind foreign); dt, dd between the two matching origins."""
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
    for s, ags in FOREIGN.items():
        x = o[o.src == s]
        if s == "gcmt":
            c = cen.set_index("sid").reindex(x.sid)
            xt, xa, xo = c.t.to_numpy(), c.lat.to_numpy(), c.lon.to_numpy()
        else:
            xt, xa, xo = x.t.to_numpy(), x.lat.to_numpy(), x.lon.to_numpy()
        b = io[io.agency.isin(ags) & io.sid.isin(isc.index)]
        if not len(x) or not len(b):
            continue
        i, j, dt, dd = near(xt, xa, xo, b.t.to_numpy(), b.lat.to_numpy(), b.lon.to_numpy(), ID_T, ID_D)
        k = pd.DataFrame({"a": x.index.to_numpy()[i], "j": j, "c": np.abs(dt) / ID_T + dd / ID_D})
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
    """Join the identity edges. Two records of one source end in the same event only if they lie within the
    second-pass window of each other; otherwise the edge is refused and listed."""
    t, la, lo, src = o.t.to_numpy(), o.lat.to_numpy(), o.lon.to_numpy(), o.src.to_numpy()
    refused, dup = [], []
    for a, b, kind in zip(ed.a.to_numpy(), ed.b.to_numpy(), ed.kind.to_numpy()):
        ra, rb = G.find(a), G.find(b)
        if ra != rb and G.mask[ra] & G.mask[rb]:
            f = factor(np.array([max(G.gm[ra], G.gm[rb])]))[0]
            same = [(i, j) for i in G.mem[ra] for j in G.mem[rb] if src[i] == src[j]]
            far = [abs(t[i] - t[j]) > SP_T * f or hav(la[i], lo[i], la[j], lo[j]) > SP_D * f for i, j in same]
            if any(far):
                refused.append((a, b, kind, *same[int(np.argmax(far))]))
                continue
            dup += same
        G.join(a, b, kind)
    return refused, dup


# windows from known same-event pairs
def known_pairs(o, bb, C):
    """Pairs of records that are the same event: members of one identity group, and for NEAREST source pairs
    the one-to-one nearest pairs within OLD_T / OLD_D."""
    src = o.src.to_numpy()
    g = pd.DataFrame({"g": bb, "i": np.arange(len(o))})
    g = g[g.groupby("g").i.transform("size") > 1]
    k = g.merge(g, on="g")
    k = k[k.i_x < k.i_y].rename(columns={"i_x": "a", "i_y": "b"})[["a", "b"]].assign(kind="id")
    sa, sb = src[C.a.to_numpy()], src[C.b.to_numpy()]
    close = ((C.dt.abs() <= OLD_T) & (C.dd <= OLD_D)).to_numpy()
    for s1, s2 in NEAREST:
        c = C[(((sa == s1) & (sb == s2)) | ((sa == s2) & (sb == s1))) & close]
        sw = src[c.a.to_numpy()] == s2
        x, y = np.where(sw, c.b, c.a), np.where(sw, c.a, c.b)
        sel = assign(x, y, np.hypot(c.dt.to_numpy() / FLOOR_T, c.dd.to_numpy() / FLOOR_D))
        k = pd.concat([k, pd.DataFrame({"a": x[sel], "b": y[sel], "kind": "nearest"})], ignore_index=True)
    k = k[src[k.a.to_numpy()] != src[k.b.to_numpy()]]
    a, b = o.iloc[k.a.to_numpy()], o.iloc[k.b.to_numpy()]
    k["pair"] = ["|".join(sorted(p)) for p in zip(a.src.to_numpy(), b.src.to_numpy())]
    k["dt"] = np.abs(a.t.to_numpy() - b.t.to_numpy())
    k["dd"] = hav(a.lat.to_numpy(), a.lon.to_numpy(), b.lat.to_numpy(), b.lon.to_numpy())
    k["old"] = np.minimum(a.t.to_numpy(), b.t.to_numpy()) < T64
    return k[np.isfinite(k.dt) & np.isfinite(k.dd)].drop_duplicates(["a", "b"]).reset_index(drop=True)


def windows(k):
    """
    Window table per pair of sources.

    The 99th percentile of the same-event offsets from OLD_YEAR on, never below FLOOR_T / FLOOR_D and capped
    at TMAX / DMAX. A pair with fewer than NMIN known pairs combines the two windows through the shared
    source that gives the smallest distance (quadrature sum); NOPAIR_T / NOPAIR_D if there is none.
    """
    q = lambda v, p: float(np.percentile(v, p)) if len(v) else np.nan
    rows = {}
    for pair, g in k.groupby("pair"):
        n, old, al = g[~g.old], g[g.old], g
        rows[pair] = {"n": len(n), **{f"{v}_p{p}": q(n[v], p) for v in ("dt", "dd") for p in (50, 95, 99)},
                      "n_old": len(old), "dt_p99_old": q(old.dt, 99), "dd_p99_old": q(old.dd, 99),
                      "dt_p99_all": q(al.dt, 99), "dd_p99_all": q(al.dd, 99)}
    key = lambda a, b: "|".join(sorted((a, b)))
    cal = {p: (float(np.clip(r["dt_p99"], FLOOR_T, TMAX)), float(np.clip(r["dd_p99"], FLOOR_D, DMAX)))
           for p, r in rows.items() if r["n"] >= NMIN}
    out = []
    for i, a in enumerate(SOURCES):
        for b in SOURCES[i + 1:]:
            p = key(a, b)
            if p in cal:
                T, D, how = *cal[p], "measured"
            else:
                via = [(np.hypot(cal[key(a, h)][1], cal[key(b, h)][1]), np.hypot(cal[key(a, h)][0], cal[key(b, h)][0]), h)
                       for h in SOURCES if h not in (a, b) and key(a, h) in cal and key(b, h) in cal]
                D, T, h = min(via) if via else (NOPAIR_D, NOPAIR_T, None)
                T, D, how = min(max(T, FLOOR_T), TMAX), min(max(D, FLOOR_D), DMAX), f"via {h}" if h else "default"
            out.append({"pair": p, "T": round(T, 2), "D": round(D, 1), "how": how, **rows.get(p, {"n": 0, "n_old": 0})})
    return pd.DataFrame(out)


def wmat(wt):
    W = np.full((2, len(SOURCES), len(SOURCES)), np.nan)
    for p, T, D in zip(wt.pair, wt["T"], wt["D"]):
        a, b = (SI[s] for s in p.split("|"))
        W[:, a, b] = W[:, b, a] = T, D
    return W


# window matching
def attach(o, G, C, W, s, link=LINK, src_t=None, among=None):
    """
    Attach the single records of source s to the groups that have no record of s, one-to-one.

    A record and a group are candidates if the record lies within the window of a member of the group (of
    its reference member only with link 'ref'); the cost is the smallest hypot(dt / T, dd / D) over those
    members. Windows widen with the largest native magnitude of record and group. Magnitude is not a criterion.
    With among (a source mask), only groups that hold one of those sources are targets: single records of
    the sources attached later wait for their own turn.

    Returns the accepted links: x, y (the member it was tied to), dt, dd, T, D, cost, old, n (candidates of
    the record or of the group, whichever is larger) and alt (the cost of the best alternative).
    """
    src, t = o.src.map(SI).to_numpy(), (o.t.to_numpy() if src_t is None else src_t)
    r = G.roots()
    size = np.bincount(r, minlength=len(o))
    si = SI[s]
    a, b = C.a.to_numpy(), C.b.to_numpy()
    fa = (src[a] == si) & (size[r[a]] == 1) & ((G.mask[r[b]] >> si) & 1 == 0)
    fb = (src[b] == si) & (size[r[b]] == 1) & ((G.mask[r[a]] >> si) & 1 == 0)
    k = fa | fb
    if among is not None:
        k &= (G.mask[r[np.where(fa, b, a)]] & among) != 0
    x, y = np.where(fa, a, b)[k], np.where(fa, b, a)[k]
    dt, dd = np.where(fa, C.dt.to_numpy(), -C.dt.to_numpy())[k], C.dd.to_numpy()[k]
    if link == "ref":
        k = refs(o, r)[r[y]] == y
        x, y, dt, dd = x[k], y[k], dt[k], dd[k]
    g = r[y]
    T, D, old = window(src[x], src[y], np.maximum(G.gm[r[x]], G.gm[g]), np.minimum(t[x], t[y]), W)
    k = (np.abs(dt) <= T) & (dd <= D)
    c = pd.DataFrame({"x": x[k], "y": y[k], "g": g[k], "dt": dt[k], "dd": dd[k], "T": T[k], "D": D[k], "old": old[k]})
    c["cost"] = np.hypot(c.dt / c["T"], c.dd / c["D"])
    c = c.sort_values(["cost", "x", "y"], kind="stable").drop_duplicates(["x", "g"]).reset_index(drop=True)
    if not len(c):
        return c.assign(n=[], alt=[], src=s)
    c["sel"] = assign(c.x.to_numpy(), c.g.to_numpy(), c.cost.to_numpy())
    c["n"] = np.maximum(c.groupby("x").g.transform("size"), c.groupby("g").x.transform("size"))
    alt = np.full(len(c), np.inf)
    for col in ("x", "g"):
        rest = c.cost.where(~c.sel).groupby(c[col]).transform("min").to_numpy()
        alt = np.fmin(alt, rest)
    c["alt"] = alt
    c = c[c.sel].drop(columns=["sel", "g"]).reset_index(drop=True)
    for xi, yi in zip(c.x.to_numpy(), c.y.to_numpy()):
        G.join(xi, yi, "window")
    return c.assign(src=s)


def second_pass(o, G, C, link=LINK):
    """Merge groups that share no source and have members (reference members with link 'ref') within SP_T
    and SP_D of each other, widened by magnitude (OLD_T and OLD_D before OLD_YEAR); closest pairs first."""
    r = G.roots()
    a, b = C.a.to_numpy(), C.b.to_numpy()
    k = r[a] != r[b]
    if link == "ref":
        ref = refs(o, r)
        k &= (ref[r[a]] == a) & (ref[r[b]] == b)
    k &= (G.mask[r[a]] & G.mask[r[b]]) == 0
    c = C[k].copy()
    f = factor(np.maximum(G.gm[r[c.a.to_numpy()]], G.gm[r[c.b.to_numpy()]]))
    c["old"] = np.minimum(o.t.to_numpy()[c.a.to_numpy()], o.t.to_numpy()[c.b.to_numpy()]) < T64
    c["T"], c["D"] = np.where(c.old, OLD_T, np.minimum(SP_T * f, TMAX)), np.where(c.old, OLD_D, np.minimum(SP_D * f, DMAX))
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
    """Merge two groups that share sources when, for every shared source, their records of that source lie
    within SAME_T and SP_D of each other (widened by magnitude): one earthquake listed twice by a source."""
    t, la, lo, src = o.t.to_numpy(), o.lat.to_numpy(), o.lon.to_numpy(), o.src.map(SI).to_numpy()
    k = np.flatnonzero(np.isfinite(t))
    i, j, dt, dd = near(t[k], la[k], lo[k], t[k], la[k], lo[k], SAME_T * max(x for _, x in SCALE), DMAX)
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
        T, D = SAME_T * f, min(SP_D * f, DMAX)
        ok = True
        for q in np.flatnonzero([(G.mask[ra] & G.mask[rb]) >> n & 1 for n in range(len(SOURCES))]):
            xa, xb = [m for m in G.mem[ra] if src[m] == q], [m for m in G.mem[rb] if src[m] == q]
            ok &= any(abs(t[u] - t[v]) <= T and hav(la[u], lo[u], la[v], lo[v]) <= D for u in xa for v in xb)
        if ok:
            G.join(row.a, row.b, "same_source")
            done.append(row)
    return pd.DataFrame(done, columns=c.columns)


def match(o, A, W=None, C=None, link=LINK, stages=None, quiet=False):
    """
    Group the records of all sources into events.

    Returns a dict: ev (event label per record), ref (reference record per label), rule (per record, the
    weakest link on its path to the reference member), wt (window table), wl (window links), sp (second-pass
    merges), ed (identity edges), bb (identity groups), refused and dup (identity edges between two records
    of one source), C (candidate pairs).
    """
    say = (lambda *a: None) if quiet else print
    C = candidates(o) if C is None else C
    say("records", len(o), "candidate pairs", len(C))
    ed = identity(o, A)
    G = Groups(o)
    refused, dup = backbone(o, ed, G)
    bb = G.roots()
    say("identity edges", ed.kind.value_counts().to_dict(), "groups", len(np.unique(bb)))
    wt = windows(known_pairs(o, bb, C)) if W is None else W
    Wm = wmat(wt)
    stages = [s for s in (stages or STAGES) if (o.src == s).any()]
    wl = [attach(o, G, C, Wm, s, link, among=sum(1 << SI[q] for q in ["isc"] + stages[:k])) for k, s in enumerate(stages)]
    wl = pd.concat(wl, ignore_index=True)
    say("window links", wl.src.value_counts().to_dict())
    sp = second_pass(o, G, C, link)
    ss = same_source(o, G)
    say("second-pass merges", len(sp), "same-source duplicates", len(ss))
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
    return {"ev": ev, "ref": ref, "rule": np.array(RULES)[rule], "wt": wt, "wl": wl, "sp": sp, "ss": ss, "ed": ed, "bb": bb,
            "refused": refused, "dup": dup, "C": C, "G": G}


# tables
def drop_types(o, ev):
    """Records of events with a member flagged as not an earthquake by its source."""
    bad = o.etype.str.lower().ne("earthquake").to_numpy() & ~pd.Series(zip(o.src, o.sid)).isin(KEEP).to_numpy()
    hit = pd.Series(bad).groupby(ev).transform("any").to_numpy()
    why = pd.Series(np.where(bad, o.src + " " + o.sid + ": " + o.etype, None)).groupby(ev).transform("first")
    return hit, np.where(bad, "flagged by the source", "same event as " + why.astype(str))


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
    """events, links and dropped tables from a match result."""
    ev, ref, wl, sp = res["ev"], res["ref"], res["wl"], res["sp"]
    hit, why = drop_types(o, ev)
    ids = event_ids(o, ev, ref, ~hit)
    o = o.assign(ev=ev, rule=res["rule"], event_id=pd.Series(ev).map(ids).to_numpy(), ri=ref[ev])
    dropped = o[hit].assign(reason=why[hit])[["src", "sid", "oid", "etype", "reason", "t", "lat", "lon", "mmax"]]
    dropped = dropped.assign(time=tstr(dropped.t)).drop(columns="t").rename(columns={"sid": "src_id", "oid": "origin_id"})
    k = o[~hit]
    top = k.sort_values("mmax", ascending=False, kind="stable").drop_duplicates("ev").set_index("ev")
    g = k.groupby("ev")
    flag = lambda rows: pd.Series(True, index=np.unique(ev[np.asarray(rows, int)])) if len(rows) else pd.Series(dtype=bool)
    amb = wl[wl.n > 1]
    r = k[k.index == k.ri].set_index("ev").sort_index()
    e = pd.DataFrame({
        "event_id": r.event_id, "time": pd.Series(tstr(r.t), index=r.index), "lon": r.lon, "lat": r.lat, "depth": r.z, "ref_src": r.src,
        "ref_id": r.sid, "sources": g.src.agg(lambda s: ",".join(sorted(set(s), key=SI.get))), "n_sources": g.src.nunique(),
        "n_members": g.size(), "mmax": top.mmax, "mmax_type": top.mtype, "mmax_agency": top.magency,
        "mmax_src": top.src.where(top.mmax.notna())})
    e["pre1964_window"] = flag(list(wl.x[wl.old]) + list(sp.a[sp.old])).reindex(e.index, fill_value=False)
    e["second_pass"] = flag(sp.a).reindex(e.index, fill_value=False) if len(sp) else False
    e["ambiguous"] = flag(amb.x).reindex(e.index, fill_value=False)
    e["same_source"] = (e.n_members > e.n_sources)
    e["t"] = r.t
    e = e.sort_values(["t", "event_id"]).reset_index(drop=True)
    rec = k[["src", "sid", "event_id", "rule", "ri"]].rename(columns={"sid": "src_id"})
    L = A.rename(columns={"sid": "src_id", "oid": "origin_id"}).merge(rec, on=["src", "src_id"])
    rt, ra, ro, rz = (o[c].to_numpy()[L.ri.to_numpy()] for c in ("t", "lat", "lon", "z"))
    L["dt"], L["dd"], L["dz"] = (L.t - rt).round(2), hav(L.lat.to_numpy(), L.lon.to_numpy(), ra, ro).round(2), (L.z - rz).round(2)
    used = set(zip(o.src, o.oid))
    L["used"] = [p in used for p in zip(L.src, L.origin_id)]
    L = L.sort_values(["event_id", "src", "src_id", "origin_id"], key=lambda c: c.map(SI) if c.name == "src" else c,
                      kind="stable")
    return e, L[["event_id", "src", "src_id", "origin_id", "rule", "dt", "dd", "dz", "used", "agency"]], dropped, o


def rm18(d, e, L, o):
    """
    Ruiz and Madariaga (2018) events on located events.

    Dates corrected first (RM_DATE). One event each, larger RM18 events first: date within RM_DAYS, latitude
    within RM_LAT, event magnitude (largest per-source median) at least RM_MMIN, closest to the RM18 Mw
    (the largest left where it gives no Mw).
    """
    f = Path(d) / f"rm2018_{FROZEN}_events.csv"
    if not f.exists():
        return [pd.DataFrame()] * 3
    x = pd.read_csv(f, dtype=str)
    m = pd.read_csv(str(f).replace("_events", "_mags"), dtype=str).drop_duplicates("src_id").set_index("src_id")
    x["mw"] = pd.to_numeric(x.src_id.map(m.mag), errors="coerce")
    x["date"] = x.src_id.map(RM_DATE).fillna(x.time)
    x["note"] = x.src_id.map(m.note)
    x["lat"] = pd.to_numeric(x.lat, errors="coerce")
    med = o.groupby("event_id").mmed.max()
    e = e.assign(med=e.event_id.map(med))
    taken, hit, miss = set(), [], []
    for r in x.sort_values("mw", ascending=False, na_position="last", kind="stable").itertuples():
        base = {"rm18": r.src_id, "rm_date": r.date, "rm_table_date": r.time, "rm_lat": r.lat, "rm_mw": r.mw,
                "rm_class": r.rm_class}
        if len(r.date) < 10:
            miss.append({**base, "why": "year or month only"})
            continue
        t0 = tsec([r.date[:10]])[0]
        w = e[(e.t >= t0 - RM_DAYS * 86400) & (e.t < t0 + (RM_DAYS + 1) * 86400) & ((e.lat - r.lat).abs() <= RM_LAT)
              & (e.med.fillna(0) >= RM_MMIN) & ~e.event_id.isin(taken)]
        if not len(w):
            miss.append({**base, "why": "no event within the date, latitude and magnitude limits"})
            continue
        y = w.loc[(w.med - r.mw).abs().idxmin() if np.isfinite(r.mw) else w.med.idxmax()]
        taken.add(y.event_id)
        hit.append({**base, "rm_note": r.note, "event_id": y.event_id, "time": y.time, "lat": y.lat, "lon": y.lon,
                    "m_event": y.med, "sources": y.sources, "n_candidates": len(w),
                    "other_candidates": " ".join(w.event_id[w.event_id != y.event_id])})
    hit, miss = pd.DataFrame(hit), pd.DataFrame(miss)
    lk = pd.DataFrame({"event_id": hit.event_id, "src": "rm2018", "src_id": hit.rm18, "origin_id": hit.rm18,
                       "rule": "rm18", "used": True, "agency": "rm2018"}) if len(hit) else pd.DataFrame()
    return hit, miss, lk


def side_by_side(hit, L, A, d=SRC):
    """RM18 values next to every source's values for the matched event."""
    mg = {}
    rows = []
    org = A.set_index(["src", "oid"])
    for r in hit.sort_values("rm_date").itertuples():
        rows.append({"rm18": r.rm18, "event_id": r.event_id, "src": "Ruiz & Madariaga", "time": r.rm_date,
                     "lat": r.rm_lat, "mags": f"Mw {r.rm_mw}" if np.isfinite(r.rm_mw) else str(r.rm_note),
                     "class": r.rm_class})
        for y in L[(L.event_id == r.event_id) & L.used & (L.src != "rm2018")].itertuples():
            if y.src not in mg:
                m = pd.read_csv(Path(d) / f"{y.src}_{DATES.get(y.src, FROZEN)}_mags.csv", low_memory=False, dtype={"src_id": str})
                mg[y.src] = m[m.mag.notna()].groupby("src_id")
            m = mg[y.src].get_group(y.src_id) if y.src_id in mg[y.src].groups else pd.DataFrame(columns=["agency", "mag_type", "mag"])
            m = m.sort_values("mag", ascending=False).head(6)
            q = org.loc[(y.src, y.origin_id)]
            q = q.iloc[0] if isinstance(q, pd.DataFrame) else q
            rows.append({"rm18": r.rm18, "event_id": r.event_id, "src": NAME[y.src], "time": tstr(q.t, "s")[0],
                         "lat": round(q.lat, 2), "lon": round(q.lon, 2), "depth": q.z, "rule": y.rule,
                         "mags": "; ".join(f"{a} {b} {c:.1f}" for a, b, c in zip(m.agency, m.mag_type, m.mag))})
    return pd.DataFrame(rows)


# checks
def near_events(e, tmax, dmax, mmin):
    """Pairs of events within tmax s and dmax km (reference members), one of them with mmax >= mmin."""
    t, la, lo, m = e.t.to_numpy(), e.lat.to_numpy(), e.lon.to_numpy(), e.mmax.fillna(0).to_numpy()
    i, j, dt, dd = near(t, la, lo, t, la, lo, tmax, dmax)
    k = (i < j) & (np.abs(dt) < tmax) & (dd < dmax) & (np.maximum(m[i], m[j]) >= mmin)
    a, b = e.iloc[i[k]].reset_index(drop=True), e.iloc[j[k]].reset_index(drop=True)
    return pd.DataFrame({"event_a": a.event_id, "event_b": b.event_id, "time_a": a.time, "dt": dt[k].round(2),
                         "dd": dd[k].round(1), "m_a": a.mmax, "m_b": b.mmax, "sources_a": a.sources,
                         "sources_b": b.sources, "shared": [",".join(sorted(set(p.split(",")) & set(q.split(","))))
                                                            for p, q in zip(a.sources, b.sources)]})


def x1_diagnostics(o, res, wt, e):
    """Split and false-merge counts as defined in X1 (explore/X1/REPORT.md, tier 1), for the comparison with
    its baseline: different events within 10 s and 50 km with one M >= 5; members tied by a window whose
    offset to the reference exceeds the all-period p99 of the pair (floors 5 s, 25 km) or |dM| > 1."""
    sp = near_events(e, 10.0, 50.0, 5.0)
    ev, ref, bb = res["ev"], res["ref"], res["bb"]
    i = np.flatnonzero(ref[ev] != np.arange(len(o)))
    j = ref[ev[i]]
    t, la, lo, md, src = o.t.to_numpy(), o.lat.to_numpy(), o.lon.to_numpy(), o.mmed.to_numpy(), o.src.to_numpy()
    dt, dd = np.abs(t[i] - t[j]), hav(la[i], lo[i], la[j], lo[j])
    p = wt.set_index("pair")
    key = pd.Series(["|".join(sorted(q)) for q in zip(src[i], src[j])])
    T = key.map(p.dt_p99_all.clip(lower=5)).fillna(p.dt_p99_all.max()).to_numpy()
    D = key.map(p.dd_p99_all.clip(lower=25)).fillna(p.dd_p99_all.max()).to_numpy()
    dm = np.abs(md[i] - md[j])
    dm[(src[i] == "potin") | (src[j] == "potin")] = np.nan
    fm = ((dt > T) | (dd > D) | (dm > 1)) & (bb[i] != bb[j])
    f = pd.DataFrame({"src": src[i], "src_id": o.sid.to_numpy()[i], "ref_src": src[j], "time": tstr(t[i], "s"),
                      "dt": dt.round(2), "dd": dd.round(1), "dm": dm, "p99_T": T, "p99_D": D, "rule": res["rule"][i],
                      "inside": (dt <= FLOOR_T) & (dd <= FLOOR_D) & ~(dm > 1)})[fm]
    return sp, f


def detach(o, res, s):
    """The final events without the records of source s, which become single records again."""
    src = o.src.to_numpy()
    xs = np.flatnonzero(src == s)
    G = Groups(o)
    r = res["ev"].copy()
    r[xs] = xs
    rest = np.flatnonzero(src != s)
    first = pd.Series(rest).groupby(r[rest]).transform("first").to_numpy()
    r[rest] = first
    G.p = r.copy()
    G.mask[:] = 0
    np.bitwise_or.at(G.mask, r, 1 << o.src.map(SI).to_numpy())
    G.gm[:] = 0
    np.maximum.at(G.gm, r, np.nan_to_num(o.mmax.to_numpy(float)))
    return G, xs


def blind(o, res, s, link=LINK):
    """
    Hide the identity links of source s and match it by windows alone, against the truth of those links.

    The records of s are taken out of the final events and attached again by time and distance only.
    Counts over the records of s that have an identity link: same (back in the event of their identity
    partners), wrong (in another event), missed (left single).
    """
    bb, src = res["bb"], o.src.to_numpy()
    G, xs = detach(o, res, s)
    attach(o, G, res["C"], wmat(res["wt"]), s, link)
    r = G.roots()
    d = pd.DataFrame({"i": np.arange(len(o)), "bb": bb})[src != s].drop_duplicates("bb").set_index("bb").i
    mate = pd.Series(bb[xs]).map(d).to_numpy()
    k = np.isfinite(mate)
    x, mate = xs[k], mate[k].astype(int)
    size = np.bincount(r, minlength=len(o))[r[x]]
    out = pd.DataFrame({"x": x, "res": np.where(r[x] == r[mate], "same", np.where(size > 1, "wrong", "missed")),
                        "m": o.mmax.to_numpy()[x], "old": o.t.to_numpy()[x] < T64})
    rows = []
    for lab, w in (("all", out.x >= 0), ("M >= 4.5", out.m >= 4.5), (f"before {OLD_YEAR}", out.old),
                   (f"{OLD_YEAR} on, M >= 4.5", ~out.old & (out.m >= 4.5))):
        c = out[w].res.value_counts()
        rows.append({"src": s, "subset": lab, "n": int(w.sum()), **{q: int(c.get(q, 0)) for q in ("same", "wrong", "missed")}})
    bad = out[out.res != "same"]
    bad = bad.assign(src=s, src_id=o.sid.to_numpy()[bad.x], time=tstr(o.t.to_numpy()[bad.x], "s"),
                     true_event=res["ev"][bad.x], put_with=r[bad.x])
    return pd.DataFrame(rows), bad


def slide(o, res, s, shift, link=LINK):
    """Chance matches of source s: its records shifted in time by shift s and matched to the final events of
    the other sources with the same windows and assignment. None of these matches can be real."""
    G, xs = detach(o, res, s)
    ys = np.flatnonzero(o.src.to_numpy() != s)
    t = o.t.to_numpy().copy()
    t[xs] += shift
    la, lo = o.lat.to_numpy(), o.lon.to_numpy()
    i, j, dt, dd = near(t[xs], la[xs], lo[xs], t[ys], la[ys], lo[ys], TMAX, DMAX)
    wl = attach(o, G, pd.DataFrame({"a": xs[i], "b": ys[j], "dt": dt, "dd": dd}), wmat(res["wt"]), s, link, src_t=t)
    return len(wl), int((o.mmax.to_numpy()[wl.x.to_numpy()] >= 4.5).sum()) if len(wl) else 0


def figure(e, wl, o, f):
    import sys
    sys.path.insert(0, str(HERE.parent))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import palette
    palette.apply()
    fig = plt.figure(figsize=(14, 9.5), layout="constrained")
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1])
    ax = fig.add_subplot(gs[0, :])
    x = e[e.mmax >= 4.5].assign(yr=lambda d: np.floor(year(d.t)).astype(int))
    x = x[x.yr >= 1900]
    bins = [(1, 1, "1 source"), (2, 2, "2"), (3, 4, "3–4"), (5, 6, "5–6"), (7, 99, "7 or more")]
    col = ["#d9d9d9", "#9ecae1", "#4292c6", "#08519c", "#e6550d"]
    yrs = np.arange(1900, x.yr.max() + 1)
    bot = np.zeros(len(yrs))
    for (lo, hi, lab), c in zip(bins, col):
        n = x[x.n_sources.between(lo, hi)].groupby("yr").size().reindex(yrs, fill_value=0).to_numpy()
        ax.bar(yrs, n, bottom=bot, width=1.0, color=c, label=lab, lw=0)
        bot += n
    ax.set_yscale("symlog", linthresh=10)
    ax.set_yticks([0, 5, 10, 100, 1000], ["0", "5", "10", "100", "1000"])
    ax.set_xlim(1900, yrs.max() + 1)
    ax.set_ylabel("events per year")
    ax.set_title(f"Events with a native magnitude ≥ 4.5, by number of catalogues that list them ({len(x):,} events since 1900)")
    ax.legend(ncol=5, loc="upper left", title="listed by")
    w = wl[~wl.old]
    grp = [("Potin et al.", w.src == "potin", palette.SERIES[0]), ("CSN web", w.src == "csn", palette.SERIES[1]),
           ("other catalogues", ~w.src.isin(["potin", "csn"]), palette.SERIES[2])]
    for k, (v, lim, floor, unit, name) in enumerate((("dt", TMAX, FLOOR_T, "s", "origin-time difference"),
                                                    ("dd", DMAX, FLOOR_D, "km", "epicentre distance"))):
        a = fig.add_subplot(gs[1, k])
        edges = np.geomspace(0.05 if v == "dt" else 0.3, lim, 60)
        for lab, sel, c in grp:
            y = np.clip(w[v][sel].abs(), edges[0], None)
            a.hist(y, bins=edges, histtype="step", color=c, lw=1.6, label=f"{lab} ({sel.sum():,})")
        a.axvline(floor, color="0.3", lw=1, ls="--")
        a.text(floor, 0.97, f" smallest window\n {floor:.0f} {unit}", transform=a.get_xaxis_transform(), va="top", fontsize=10)
        a.axvspan(w["T" if v == "dt" else "D"].max(), lim, color="0.93", lw=0)
        a.set_xscale("log")
        a.set_yscale("log")
        a.set_xlim(edges[0], lim)
        a.set_xlabel(f"{name} to the matched member [{unit}]")
        a.set_ylabel("window matches")
        a.set_title(f"Matches by time and distance ({OLD_YEAR} on): {name}")
        if k == 0:
            a.legend(loc="lower left")
    f.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(f, dpi=200)
    plt.close(fig)


def sha(f):
    return hashlib.sha256(Path(f).read_bytes()).hexdigest()


def pair_rows(o, eid, a, b, **kw):
    """Two records side by side (review lists): a against b."""
    a, b = np.asarray(a, int), np.asarray(b, int)
    m = np.fmax(o.mmax.to_numpy(float)[a], o.mmax.to_numpy(float)[b]) if len(a) else []
    d = pd.DataFrame({"event_id": eid[a], "src": o.src.to_numpy()[a], "src_id": o.sid.to_numpy()[a],
                      "time": tstr(o.t.to_numpy()[a], "s"), "to_src": o.src.to_numpy()[b], "to_id": o.sid.to_numpy()[b],
                      "to_event": eid[b], "dt": np.round(o.t.to_numpy()[a] - o.t.to_numpy()[b], 2),
                      "dd": np.round(hav(o.lat.to_numpy()[a], o.lon.to_numpy()[a], o.lat.to_numpy()[b], o.lon.to_numpy()[b]), 1),
                      "m_pair": m})
    for k, v in kw.items():
        d[k] = np.asarray(v)
    return d


def review(o, A, res, e, L, dropped, eid, hit, miss):
    """Review lists, name -> table."""
    wl, sp, ss, ed = res["wl"], res["sp"], res["ss"], res["ed"]
    em = e.set_index("event_id")
    add = lambda d: d.assign(mmax=d.event_id.map(em.mmax), sources=d.event_id.map(em.sources))
    big = lambda d: d.sort_values(["mmax", "time"], ascending=[False, True])
    out = {}
    d = pair_rows(o, eid, ed.a, ed.b, kind=ed.kind)
    out["id_disagree"] = big(add(d[(d.dt.abs() > BAD_T) | (d.dd > BAD_D)]))
    w = add(pair_rows(o, eid, wl.x, wl.y, T=wl["T"], D=wl["D"], cost=wl.cost.round(3), n_candidates=wl.n,
                      next_cost=wl.alt.round(3), old=wl.old)).drop(columns="to_event")
    s2 = add(pair_rows(o, eid, sp.a, sp.b, T=sp["T"], D=sp["D"], cost=sp.cost.round(3), old=sp.old)).drop(columns="to_event")
    both = pd.concat([w.assign(step="window"), s2.assign(step="second_pass")])
    out["pre1964_window"] = both[both.old].sort_values("time").drop(columns="old")
    out["ambiguous"] = big(w[w.n_candidates > 1]).drop(columns="old")
    out["second_pass_m5"] = big(s2[s2.mmax >= 5]).drop(columns="old")
    out["merges_m6"] = big(both[both.mmax >= 6]).drop(columns=["old", "n_candidates", "next_cost"])
    out["rm18"] = side_by_side(hit, L, A)
    out["rm18_matches"] = hit
    out["rm18_unmatched"] = miss
    out["dropped_types"] = dropped
    bx, by = (np.array([p[k] for p in res["dup"]], int) for k in (0, 1))
    out["same_source"] = big(add(pd.concat([pair_rows(o, eid, ss.a, ss.b, step="same-source pass"),
                                            pair_rows(o, eid, bx, by, step="identity")]).drop(columns="to_event")))
    rf = res["refused"]
    out["id_refused"] = pair_rows(o, eid, [r[3] for r in rf], [r[4] for r in rf], kind=[r[2] for r in rf],
                                  edge=[f"{o.src[r[0]]} {o.sid[r[0]]} = {o.src[r[1]]} {o.sid[r[1]]}" for r in rf])
    nb = near_events(e, SP_T, SP_D, 4.5)
    out["close_events_m45"] = nb.sort_values("m_a", ascending=False)
    wide = near_events(e, WIDE_T, WIDE_D, 0.0)
    n = pd.concat([wide.event_a, wide.event_b]).value_counts()
    wide["only_neighbours"] = (wide.event_a.map(n) == 1) & (wide.event_b.map(n) == 1)
    wide = wide[(wide.shared == "") & (np.fmax(wide.m_a.fillna(0), wide.m_b.fillna(0)) >= 4.5)]
    out["possible_splits"] = wide.sort_values(["only_neighbours", "m_a"], ascending=False)
    return out


def validate(o, res, e):
    """Checks of the result: X1 diagnostics, blind recovery of the identity links, chance matches."""
    wl = res["wl"]
    xs, xf = x1_diagnostics(o, res, res["wt"], e)
    bl, bad = zip(*[blind(o, res, s) for s in BLIND if (o.src == s).any()])
    bl = pd.concat(bl, ignore_index=True)
    bl["wrong_pct"], bl["missed_pct"] = (100 * bl.wrong / bl.n).round(3), (100 * bl.missed / bl.n).round(3)
    m45 = o.mmax.to_numpy() >= 4.5
    sl = []
    for s in ("potin", "csn", "gccel"):
        k = wl.x[wl.src == s].to_numpy()
        for sh in SLIDES if (o.src == s).any() else []:
            n, m = slide(o, res, s, sh)
            sl.append({"src": s, "shift_s": sh, "records": int((o.src == s).sum()), "records_m45": int(((o.src == s) & m45).sum()),
                       "window_links": len(k), "window_links_m45": int(m45[k].sum()), "chance": n, "chance_m45": m})
    return {"x1_splits": xs, "x1_false_merges": xf, "blind_failures": pd.concat(bad).drop(columns="x")
            .sort_values("m", ascending=False)}, bl, pd.DataFrame(sl)


def main():
    rev = OUT / "review"
    rev.mkdir(parents=True, exist_ok=True)
    o, A = load()
    res = match(o, A)
    e, L, dropped, ox = tables(o, A, res)
    eid = ox.event_id.to_numpy()
    hit, miss, lk = rm18(SRC, e, L, ox[ox.event_id.notna()])
    L = pd.concat([L, lk], ignore_index=True)
    check(A, e, L, dropped)
    lists = review(o, A, res, e, L, dropped, eid, hit, miss)
    more, bl, sl = validate(o, res, e)
    figure(e, res["wl"], o, FIG / "summary.png")

    own = L[L.used & (L.src != "rm2018")]
    by = own.groupby(["src", "rule"]).size().unstack(fill_value=0)
    by = by.reindex(index=[s for s in SOURCES if s in by.index], columns=[r for r in RULES if r in by.columns])
    by.insert(0, "records", own.groupby("src").size())
    by.insert(1, "alone", own[own.event_id.map(e.set_index("event_id").n_members) == 1].groupby("src").size())
    by = by.fillna(0).astype(int).reset_index()
    out = {OUT / f"{k}_{RUN}.csv": v for k, v in (("events", e.drop(columns="t")), ("links", L), ("windows", res["wt"]),
                                                  ("counts", by), ("check_blind", bl), ("check_chance", sl))}
    out.update({rev / f"{k}_{RUN}.csv": v for k, v in {**lists, **more}.items()})
    for f, df in out.items():
        df.to_csv(f, index=False)
    pd.DataFrame([{"file": str(f.relative_to(OUT)), "run": RUN, "rows": len(df), "sha256": sha(f)} for f, df in out.items()]) \
        .to_csv(OUT / "MANIFEST.csv", index=False)

    mt = SRC / f"comcat_mt_{FROZEN}_mechs.csv"
    if mt.exists():
        ids = set(pd.read_csv(mt, usecols=["src_id"], dtype=str).src_id)
        print("comcat_mt events:", len(ids), "with an event_id:", len(ids & set(L.src_id[L.src == "comcat"])))
    xf = more["x1_false_merges"]
    print(by.to_string(index=False))
    print("events", len(e), "| M >= 4.5 (any native)", int((e.mmax >= 4.5).sum()), "| dropped records", len(dropped))
    print("X1 diagnostics: splits", len(more["x1_splits"]), "false merges", len(xf), "of which outside",
          f"{FLOOR_T:.0f} s / {FLOOR_D:.0f} km or dM > 1:", int((~xf.inside).sum()))
    print("review lists:", {k: len(v) for k, v in {**lists, **more}.items()})
    print(bl.to_string(index=False))
    print(sl.groupby("src").mean(numeric_only=True).drop(columns="shift_s").round(1).to_string())
    print("RM18 matched", len(hit), "not matched", len(miss))


def check(A, e, L, dropped):
    """Every origin of the inputs is in exactly one event or in the dropped list; one event per source event."""
    own = L[L.src != "rm2018"]
    key = lambda d, a, b: pd.MultiIndex.from_frame(d[["src", a, b]].astype(str))
    assert not key(own, "src_id", "origin_id").duplicated().any()
    assert own.groupby(["src", "src_id"]).event_id.nunique().max() == 1
    assert own.event_id.notna().all() and set(own.event_id) == set(e.event_id) and e.event_id.is_unique
    gone = pd.MultiIndex.from_frame(A[["src", "sid"]].astype(str)).isin(pd.MultiIndex.from_frame(dropped[["src", "src_id"]].astype(str)))
    assert len(own) + gone.sum() == len(A)
    assert not pd.MultiIndex.from_frame(own[["src", "src_id"]].astype(str)).isin(
        pd.MultiIndex.from_frame(dropped[["src", "src_id"]].astype(str))).any()


if __name__ == "__main__":
    main()

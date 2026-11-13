import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import match as M

D = Path(__file__).resolve().parent / "data" / "match"


def synth(n=400, seed=1, st=1.0, sd=10.0, keep=0.8, burst=True):
    """Two catalogues of the same n earthquakes with independent errors; each lists a random part of them."""
    g = np.random.default_rng(seed)
    t = np.sort(g.uniform(0, 30 * 86400, n)) + 3.2e9
    if burst:
        t[: n // 4] = t[0] + np.sort(g.exponential(900, n // 4))
    lat, lon = g.uniform(-34, -32, n), g.uniform(-72.5, -71, n)
    rows = []
    for s in ("isc", "potin"):
        k = np.flatnonzero(g.random(n) < keep)
        rows.append(pd.DataFrame({"src": s, "sid": [f"{s}{i}" for i in k], "oid": [f"{s}{i}" for i in k],
                                  "t": t[k] + g.normal(0, st, len(k)), "lat": lat[k] + g.normal(0, sd / 111, len(k)),
                                  "lon": lon[k] + g.normal(0, sd / 93, len(k)), "z": 30.0, "etype": "earthquake",
                                  "mmax": 4.0, "mtype": "mb", "magency": "X", "mmed": 4.0, "true": k}))
    o = pd.concat(rows, ignore_index=True)
    A = o.assign(agency="X", prime=True)[["src", "sid", "oid", "agency", "prime", "t", "lat", "lon", "z"]]
    return o, A


def table(T=M.FLOOR_T, D=M.FLOOR_D):
    p = ["|".join(sorted((a, b))) for i, a in enumerate(M.SOURCES) for b in M.SOURCES[i + 1:]]
    return pd.DataFrame({"pair": p, "T": T, "D": D})


def parts(o, ev):
    return {frozenset(zip(g.src, g.sid)) for _, g in o.assign(ev=ev).groupby("ev")}


@pytest.fixture(scope="module")
def real():
    o, A = M.load(D)
    res = M.match(o, A, W=pd.read_csv(D / "windows.csv"), quiet=True)
    e, L, dropped, ox = M.tables(o, A, res)
    return o, A, res, e, L, dropped, ox


def event(e, start):
    x = e[e.time.str.startswith(start)]
    return x.loc[x.mmax.idxmax()]


# assignment and windows
def test_assign_one_to_one():
    # two events 4 s and 20 km apart, both in the window of both records of the other source
    o = pd.DataFrame({"src": ["isc", "isc", "potin", "potin"], "sid": list("abcd"), "oid": list("abcd"),
                      "t": [3.2e9, 3.2e9 + 4, 3.2e9 + 0.5, 3.2e9 + 4.4], "lat": [-33.0, -33.18, -33.01, -33.17],
                      "lon": -72.0, "z": 20.0, "etype": "earthquake", "mmax": 5.0, "mtype": "mb", "magency": "X", "mmed": 5.0})
    A = o.assign(agency="X", prime=True)
    res = M.match(o, A, W=table(), quiet=True)
    assert parts(o, res["ev"]) == {frozenset({("isc", "a"), ("potin", "c")}), frozenset({("isc", "b"), ("potin", "d")})}
    assert (res["wl"].n == 2).all()


def test_assign_minimum_total_cost():
    # greedy would take (0, 0) and leave record 1 with the expensive group
    x, g = np.array([0, 0, 1, 1]), np.array([0, 1, 0, 1])
    sel = M.assign(x, g, np.array([0.10, 0.12, 0.11, 0.90]))
    assert sel.tolist() == [False, True, True, False]


def test_window_scaling():
    W = M.wmat(table())
    sa = np.zeros(6, int)
    m = np.array([5.9, 6.0, 7.0, 8.0, 9.5, 8.0])
    t = np.r_[np.full(5, M.T64 + 1), M.T64 - 1]
    T, Dk, old = M.window(sa, sa + 1, m, t, W)
    assert T.tolist() == [10, 15, 20, 30, 30, M.OLD_T]
    assert Dk.tolist() == [50, 75, 100, 150, 150, M.OLD_D]
    assert old.tolist() == [False] * 5 + [True]
    W[:, 0, 1] = 100.0, 400.0
    T, Dk, _ = M.window(sa[:1], sa[:1] + 1, np.array([8.0]), t[:1], W)
    assert (T[0], Dk[0]) == (M.TMAX, M.DMAX)


def test_windows_table():
    g = np.random.default_rng(0)
    k = pd.DataFrame({"pair": "comcat|isc", "dt": np.abs(g.normal(0, 1, 5000)), "dd": np.abs(g.normal(0, 40, 5000)), "old": False})
    few = pd.DataFrame({"pair": "gcmt|isc", "dt": 50.0, "dd": 400.0, "old": False}, index=range(M.NMIN - 1))
    w = M.windows(pd.concat([k, few])).set_index("pair")
    assert w.loc["comcat|isc", "T"] == M.FLOOR_T
    assert w.loc["comcat|isc", "D"] == pytest.approx(np.percentile(k.dd, 99), abs=0.06)
    assert w.loc["gcmt|isc", "how"] != "measured"
    assert (w["T"] >= M.FLOOR_T).all() and (w["D"] >= M.FLOOR_D).all() and (w["T"] <= M.TMAX).all() and (w["D"] <= M.DMAX).all()


def test_magnitude_is_not_a_criterion():
    o, A = synth(60, burst=False)
    a = parts(o, M.match(o, A, W=table(), quiet=True)["ev"])
    o2 = o.assign(mmax=np.where(o.src == "isc", 3.0, 5.9), mmed=np.where(o.src == "isc", 3.0, 5.9))
    assert parts(o2, M.match(o2, A, W=table(), quiet=True)["ev"]) == a


# recovery on synthetic catalogues
def test_synthetic_recovery():
    o, A = synth()
    res = M.match(o, A, W=table(), quiet=True)
    d = o.assign(ev=res["ev"])
    both = d.groupby("true").src.nunique() == 2
    one = d[d.true.isin(both.index[both])].groupby("true").ev.nunique() == 1
    wrong = d.groupby("ev").true.nunique() > 1
    assert one.mean() > 0.97
    assert wrong.sum() <= 0.01 * len(wrong)
    # two true events within SAME_T of each other in the burst may be taken as one listed twice
    assert (d.groupby(["ev", "src"]).size() > 1).sum() <= 2


def test_order_does_not_matter():
    o, A = synth(200, seed=3)
    a = parts(o, M.match(o, A, W=table(), quiet=True)["ev"])
    p = np.random.default_rng(5).permutation(len(o))
    o2 = o.iloc[p].reset_index(drop=True)
    assert parts(o2, M.match(o2, A, W=table(), quiet=True)["ev"]) == a


def test_chance_matches_are_few():
    o, A = synth(400, burst=False)
    res = M.match(o, A, W=table(), quiet=True)
    n = np.mean([M.slide(o, res, "potin", s)[0] for s in M.SLIDES])
    assert n < 0.02 * len(res["wl"])


def test_blind_on_synthetic():
    # identity links for half of the pairs; hidden, the windows must put them back
    o, A = synth(300, seed=7, burst=False)
    res = M.match(o, A, W=table(), quiet=True)
    isc = pd.Series(o.index[o.src == "isc"], index=o.true[o.src == "isc"])
    k = [i for i in o.index[o.src == "potin"] if o.true[i] in isc.index][::2]
    bb = np.arange(len(o))
    bb[k] = isc[o.true[k]].to_numpy()
    res["bb"] = bb
    tb, bad = M.blind(o, res, "potin")
    r = tb[tb.subset == "all"].iloc[0]
    assert r.n == len(k) and r.same >= 0.97 * r.n and r.wrong <= 2


# duplicates inside one source
def dup_case(dt, n_src):
    srcs = ["isc", "comcat", "iscehb"][:n_src]
    rows = [{"src": s, "sid": f"{s}{k}", "t": 3.2e9 + k * dt + 0.2 * i, "lat": -33.0 - 0.05 * k} for k in (0, 1)
            for i, s in enumerate(srcs)]
    rows = rows if n_src > 1 else rows + [{"src": "comcat", "sid": "c", "t": 3.2e9 + 0.3, "lat": -33.0}]
    o = pd.DataFrame(rows).assign(lon=-72.0, z=20.0, etype="earthquake", mmax=5.0, mtype="mb", magency="X", mmed=5.0)
    o["oid"] = o.sid
    return o, o.assign(agency="X", prime=True)


def test_same_source_duplicate_merged():
    o, A = dup_case(1.0, 1)
    res = M.match(o, A, W=table(), quiet=True)
    assert len(np.unique(res["ev"])) == 1 and len(res["ss"]) == 1


def test_doublet_listed_by_all_stays_two():
    o, A = dup_case(5.0, 3)
    res = M.match(o, A, W=table(), quiet=True)
    assert len(np.unique(res["ev"])) == 2 and len(res["ss"]) == 0
    assert o.assign(ev=res["ev"]).groupby("ev").src.nunique().tolist() == [3, 3]


# single-source duplicates of ISC events
def lone_case(dd=100.0, src="potin", other=("isc", "comcat"), m=5.0, third=None):
    rows = [{"src": s, "sid": f"{s}0", "t": 3.2e9 + 0.1 * i, "lat": -33.0, "mmax": m} for i, s in enumerate(other)]
    rows.append({"src": src, "sid": "x", "t": 3.2e9 + 8.0, "lat": -33.0 - dd / 111.19, "mmax": np.nan})
    if third is not None:
        rows.append({"src": "isc", "sid": "isc9", "t": 3.2e9 + third, "lat": -33.3, "mmax": 3.0})
    o = pd.DataFrame(rows).assign(lon=-72.0, z=20.0, etype="earthquake", mtype="mb", magency="X")
    o["oid"], o["mmed"] = o.sid, o.mmax
    A = o.assign(agency="X", prime=True)
    res = M.match(o, A, W=table(), quiet=True)
    e, L, dropped, ox = M.tables(o, A, res)
    M.check(A, e, L, dropped)
    return e, dropped


def test_lone_duplicate_removed():
    for s in M.LONE:
        e, d = lone_case(src=s)
        assert len(e) == 1 and e.sources.iloc[0] == "isc,comcat"
        assert d.src.tolist() == [s] and d.step.iloc[0] == "duplicate" and d.reason.iloc[0].startswith("same earthquake as isc isc0")


@pytest.mark.parametrize("kw, n", [({"dd": 30.0}, 1), ({"dd": 200.0}, 2), ({"src": "gccel"}, 2), ({"other": ("comcat",)}, 2),
                                   ({"m": 4.0}, 2), ({"third": 20.0}, 3)])
def test_lone_record_kept(kw, n):
    e, d = lone_case(**kw)
    assert len(d) == 0 and len(e) == n


def test_lone_duplicate_with_far_third_event():
    e, d = lone_case(third=300.0)
    assert len(d) == 1 and len(e) == 2


# identifiers
def test_event_ids():
    o = pd.DataFrame({"src": ["isc", "isc", "potin"], "sid": list("abc"), "t": M.tsec(["2010-02-27T06:34:11.9"] * 2 + ["1730-07-08T10:00"]),
                      "lat": [-36.0, -35.0, -33.0]})
    ids = M.event_ids(o, np.arange(3), np.arange(3), np.ones(3, bool))
    assert ids[[0, 1, 2]].tolist() == ["cl20100227063411a", "cl20100227063411b", "cl17300708100000"]


# the known cases on real samples
@pytest.mark.parametrize("start, n_min, srcs", [
    ("2010-02-27T06:34", 7, "gccel,iscehb,iscgem,isc,comcat,csn_isc,gcmt"),
    ("2015-09-16T22:54", 7, "gccel,iscehb,iscgem,isc,comcat,csn_isc,gcmt"),
    ("2014-04-01T23:46", 8, "potin,gccel,iscehb,iscgem,isc,comcat,csn_isc,gcmt"),
    ("2011-01-02T20:20", 8, "potin,gccel,iscehb,iscgem,isc,comcat,csn_isc,gcmt")])
def test_mainshock_is_one_event(real, start, n_min, srcs):
    o, A, res, e, L, dropped, ox = real
    x = event(e, start)
    assert x.sources == srcs and x.n_members >= n_min
    own = L[(L.event_id == x.event_id) & L.used]
    assert set(own.src) == set(srcs.split(",")) and own.dt.abs().max() < 30


@pytest.mark.parametrize("start, hours", [("2010-02-27T06:34", 1.0), ("2015-09-16T22:54", 1.0), ("2014-04-01T23:46", 1.0)])
def test_first_hour_aftershocks_stay_separate(real, start, hours):
    o, A, res, e, L, dropped, ox = real
    x = event(e, start)
    t0 = M.tsec([x.time])[0]
    k = ox[(ox.t > t0 + 60) & (ox.t < t0 + hours * 3600) & ox.event_id.notna()]
    assert x.event_id not in set(k.event_id)
    most = k.groupby("src").size().max()
    assert k.event_id.nunique() >= most > 5
    own = L[(L.event_id == x.event_id) & L.used]
    assert own.dt.abs().max() < 30


def test_arauco_2011_duplicate_merged(real):
    o, A, res, e, L, dropped, ox = real
    day = e[e.time.str.startswith("2011-01-02T20:2") & (e.mmax >= 6.5)]
    assert len(day) == 1
    m = L[(L.event_id == day.event_id.iloc[0]) & L.used].set_index("src")
    assert {"csn_isc", "gcmt"} <= set(m.index)
    a, b = (o[(o.src == s) & o.sid.isin(m.loc[[s]].src_id)].iloc[0] for s in ("csn_isc", "gcmt"))
    assert abs(a.t - b.t) > 5 and M.hav(a.lat, a.lon, b.lat, b.lon) > 50


def test_pre1964(real):
    o, A, res, e, L, dropped, ox = real
    x = e[e.time.str.startswith("1912-12-07")]
    assert len(x) == 1 and x.sources.iloc[0] == "iscgem,centennial,isc,comcat" and x.pre1964_window.iloc[0]
    main, fore = event(e, "1960-05-22T19:11"), event(e, "1960-05-22T18:56")
    assert main.event_id != fore.event_id and "centennial" in main.sources and "centennial" in fore.sources


def test_non_earthquake_dropped_with_its_members(real):
    o, A, res, e, L, dropped, ox = real
    d = dropped[dropped.time.str.startswith("2009-10-05T13:18")]
    assert {"isc", "csn_isc", "iscehb", "comcat", "potin"} <= set(d.src)
    assert not e.time.str.startswith("2009-10-05T13:18").any()


def test_isc_listed_twice(real):
    o, A, res, e, L, dropped, ox = real
    x = e[e.time.str.startswith("2025-04-18T00:10") & (e.mmax >= 6)]
    assert len(x) == 1 and x.same_source.iloc[0]


def test_rm18(real):
    o, A, res, e, L, dropped, ox = real
    hit, miss, lk = M.rm18(D, e, L, ox[ox.event_id.notna()])
    h = hit.set_index("rm18")
    assert h.loc["Mejillones 1994", "time"].startswith("1994-12-10") and h.loc["Mejillones 1994", "m_event"] >= 5.5
    assert h.loc["Maule 2010", "event_id"] == event(e, "2010-02-27T06:34").event_id
    assert h.loc["Maule outer rise 2010", "event_id"] != h.loc["Maule 2010", "event_id"]
    assert h.loc["Valdivia 1960", "time"].startswith("1960-05-22T19:11")
    assert h.loc["Valdivia 1960 foreshock", "time"].startswith("1960-05-22T18:56")
    assert hit.event_id.is_unique and set(lk.rule) == {"rm18"}
    assert {"Taltal 1887", "Tarapaca 1543"} <= set(miss.rm18)


# every origin once
def test_partition(real):
    o, A, res, e, L, dropped, ox = real
    M.check(A, e, L, dropped)
    own = L.groupby(["src", "src_id", "origin_id"]).event_id.nunique()
    assert own.max() == 1
    got = set(zip(L.src, L.src_id, L.origin_id)) | {(r.src, r.sid, r.oid) for r in A.itertuples()
                                                    if (r.src, r.sid) in set(zip(dropped.src, dropped.src_id))}
    assert got == set(zip(A.src, A.sid, A.oid))
    assert set(L.rule) <= set(M.RULES)
    assert (L[(L.rule == "ref") & L.used].dt == 0).all()


def test_one_record_per_source_unless_flagged(real):
    o, A, res, e, L, dropped, ox = real
    n = L[L.used].groupby(["event_id", "src"]).size().groupby("event_id").max()
    assert set(n.index[n > 1]) == set(e.event_id[e.same_source])

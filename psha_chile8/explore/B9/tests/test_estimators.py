"""Estimators of b9_lib on synthetic Gutenberg-Richter catalogues: known Mc, b and a come back."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import b9_lib as L

TB = [(4.5, 1995), (5.5, 1964), (7.0, 1900)]
T0, T1 = 1900.0, 2026.0
B, RATE = 1.0, 300.0


def cat(seed, b=B, rate=RATE, table=TB, sigma=0.0):
    return L.synth(b, rate, table, T0, T1, np.random.default_rng(seed), sigma)


def test_weichert_time_varying_table():
    bs, rs = [], []
    for s in range(20):
        t, m = cat(s)
        r = L.fit(L.kbin(m), t, np.ones(m.size), TB, T1)
        bs.append(r["b"]), rs.append(r["rate"])
    assert abs(np.mean(bs) - B) < 0.01
    assert abs(np.mean(rs) / RATE - 1) < 0.02
    assert r["m_lo"] == 4.45


def test_weichert_wrong_table_is_biased():
    t, m = cat(0)
    r = L.fit(L.kbin(m), t, np.ones(m.size), [(4.5, 1900)], T1)
    assert r["b"] < B - 0.1


def test_weichert_weights():
    t, m = cat(1)
    k, w = L.kbin(m), np.ones(m.size)
    a = L.fit(k, t, w, TB, T1)
    # every event cut in two parts
    h = L.fit(np.r_[k, k], np.r_[t, t], np.r_[0.3 * w, 0.7 * w], TB, T1)
    assert abs(a["b"] - h["b"]) < 1e-9 and abs(a["rate"] / h["rate"] - 1) < 1e-9
    # a class holding 40 % of every event
    p = L.fit(k, t, 0.4 * w, TB, T1)
    assert abs(p["b"] - a["b"]) < 1e-9 and abs(p["rate"] / a["rate"] - 0.4) < 1e-9
    # random membership, mean weight 0.5
    ww = np.random.default_rng(3).choice([0, 0.25, 0.75, 1], m.size)
    q = L.fit(k, t, ww, TB, T1)
    assert abs(q["b"] - B) < 0.05 and abs(q["rate"] / RATE - 0.5) < 0.04


def test_bootstrap_covers_truth():
    hit = 0
    for s in range(40):
        t, m = cat(100 + s, rate=40.0)
        r = L.fit(L.kbin(m), t, np.ones(m.size), TB, T1, nboot=200, rng=np.random.default_rng(s))
        lo, hi = np.nanpercentile(r["bb"], [5, 95])
        hit += lo <= B <= hi
    assert 30 <= hit <= 40


def test_fixed_b_keeps_total_rate():
    t, m = cat(2)
    k, w = L.kbin(m), np.ones(m.size)
    a = L.fit(k, t, w, [(5.0, 1964)], T1)
    f = L.fit(k, t, w, [(5.0, 1964)], T1, bfix=0.8)
    assert abs(f["rate"] / a["rate"] - 1) < 1e-9


def test_floor_cuts_table():
    t, m = cat(4)
    r = L.fit(L.kbin(m), t, np.ones(m.size), TB, T1, floor=5.0)
    assert r["m_lo"] == 4.95 and abs(r["b"] - B) < 0.05
    assert abs(L.n_ge(r["b"], r["rate"], r["m_lo"], 4.5) / RATE - 1) < 0.1


def test_bpositive_table_free():
    bs = []
    for s in range(10):
        t, m = cat(s)
        bs.append(L.bpositive(m, np.ones(m.size), 0.2)[0])
    # a static thinning below Mc leaves a small low bias (0.04 here); the method is exact for short-term loss only
    assert abs(np.mean(bs) - B) < 0.06
    # the plain estimate at 4.5 on the same thinned catalogue is low
    assert L.tinti(m, np.ones(m.size), 4.5)[0] < B - 0.1


def test_bpositive_weights():
    t, m = cat(5, table=[(4.5, 1900)])
    w = np.random.default_rng(1).choice([0.3, 1.0], m.size)
    assert abs(L.bpositive(m, w, 0.2)[0] - B) < 0.03


def test_tinti_binned():
    t, m = cat(6, table=[(4.5, 1900)])
    for c in (4.5, 5.0, 5.5):
        assert abs(L.tinti(m, np.ones(m.size), c)[0] - B) < 0.04


def test_mc_methods():
    for mc in (5.0, 5.4):
        t, m = cat(7, rate=400.0, table=[(mc, 1900)])
        w = np.ones(m.size)
        assert abs(L.mc_maxc(m, w) - mc) <= 0.21
        assert abs(L.mc_bstab(m, w) - mc) <= 0.21
        assert abs(L.mc_ks(m, w, rng=np.random.default_rng(0)) - mc) <= 0.21


def test_mc_weights():
    t, m = cat(8, rate=400.0, table=[(5.2, 1900)])
    w = np.random.default_rng(2).choice([0.2, 0.6, 1.0], m.size)
    assert abs(L.mc_bstab(m, w) - 5.2) <= 0.21
    assert abs(L.mc_ks(m, w, rng=np.random.default_rng(0)) - 5.2) <= 0.21


def test_stepp_and_changepoint_year():
    t, m = cat(9)
    w = np.ones(m.size)
    for lo, hi, yr in ((4.5, 5.0, 1995), (5.5, 6.0, 1964)):
        s = (m >= lo - 1e-6) & (m < hi - 1e-6)
        ys, _ = L.stepp(t[s], w[s], T1)
        assert abs(ys - yr) <= 6
        y = np.arange(1900, 2026)
        c = np.bincount((np.floor(t[s]) - 1900).astype(int), w[s], minlength=y.size)
        yc = L.complete_since(y, c)[0]
        assert abs(yc - yr) <= 3


def test_changepoint_none_when_steady():
    rng = np.random.default_rng(0)
    y = np.arange(1900, 2026)
    assert L.changepoint(y, rng.poisson(8, y.size), phi=1.0)[0] == []


def test_magnitude_error_correction():
    sig, out = 0.25, {"raw": [], "ceus": [], "plain": []}
    for s in range(10):
        t, m = cat(20 + s, table=[(4.5, 1900)], sigma=sig)
        k, w = L.kbin(m), np.ones(m.size)
        f0 = L.fit(k, t, w, [(5.0, 1900)], T1)
        out["raw"].append(f0["rate"])
        for mode in ("ceus", "plain"):
            kk, ww, ii = L.ceus(k, w, np.full(m.size, sig), f0["b"], mode)
            out[mode].append(L.fit(kk, t[ii], ww, [(5.0, 1900)], T1)["rate"])
    true = RATE * 10 ** (-B * 0.5)
    assert np.mean(out["raw"]) / true > 1.12
    assert abs(np.mean(out["ceus"]) / true - 1) < 0.04
    assert abs(np.mean(out["plain"]) / true - 1) < 0.04


def test_gardner_knopoff_removes_aftershocks():
    rng = np.random.default_rng(0)
    n = 300
    t = np.sort(rng.uniform(1990, 2020, n))
    lon, lat, m = rng.uniform(-75, -68, n), rng.uniform(-45, -18, n), np.full(n, 4.6)
    # a M 8 with 50 aftershocks within 30 days and 50 km
    ta = 2005 + rng.uniform(0, 30 / 365.25, 50)
    t2, lon2, lat2 = np.r_[t, 2005.0, ta], np.r_[lon, -72.0, -72 + rng.normal(0, 0.2, 50)], np.r_[lat, -35.0, -35 + rng.normal(0, 0.2, 50)]
    m2 = np.r_[m, 8.0, np.full(50, 5.0)]
    o = np.argsort(t2)
    main = L.gardner_knopoff(t2[o], lon2[o], lat2[o], m2[o])
    assert main[m2[o] == 8.0].all()
    assert (~main[m2[o] == 5.0]).sum() >= 48
    assert main[m2[o] == 4.6].mean() > 0.9

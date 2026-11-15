import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import x1_mag as M  # noqa: E402
import x1_match as X  # noqa: E402


def test_assign_one_to_one():
    ia = np.array([0, 0, 1, 1, 2])
    ib = np.array([10, 11, 10, 11, 12])
    c = np.array([0.1, 0.2, 0.15, 0.9, 0.5])
    g = X.assign(ia, ib, c, "greedy")
    h = X.assign(ia, ib, c, "hungarian")
    assert g.tolist() == [True, False, False, True, True]
    assert h.tolist() == [False, True, True, False, True]
    for s in (g, h):
        assert len(set(ia[s])) == s.sum() and len(set(ib[s])) == s.sum()


def test_union_one_per_source():
    p = np.arange(4, dtype=np.int64)
    mask = np.array([1, 2, 2, 4], dtype=np.int64)
    rep = np.arange(4, dtype=np.int64)
    pr = np.array([0, 1, 1, 2], dtype=np.int64)
    X.union_all(p, mask, rep, pr, np.array([0, 0, 0]), np.array([1, 2, 3]), False)
    r = X.roots(p)
    assert r[0] == r[1] == r[3] and r[2] != r[0]


def synth(n=3000, sx=0.25, sy=0.08, seed=0):
    rng = np.random.default_rng(seed)
    t = rng.uniform(4.0, 7.0, n)
    return t, t + rng.normal(0, sx, n), rng.normal(0, sy, n), rng


def test_csq_linear_recovers_slope():
    t, x, ey, _ = synth()
    a, b = 0.7, 0.88
    y = a + b * t + ey
    r = M.fit(x, y, "linear", "CSQ", sx=0.25, sy=0.08)
    o = M.fit(x, y, "linear", "OLS")
    assert abs(r["p"][1] - b) < 0.03
    assert o["p"][1] < b - 0.03


def test_csq_exponential_recovers_curve():
    t, x, ey, _ = synth(4000, 0.2, 0.05, 1)
    p = (-4.6, 0.86, 4.55)
    y = M.model("exponential", p, t) + ey
    r = M.fit(x, y, "exponential", "CSQ", sx=0.2, sy=0.05)
    g = np.linspace(4.5, 6.0, 4)
    assert np.max(np.abs(M.model("exponential", r["p"], g) - M.model("exponential", p, g))) < 0.08


def test_equation_error():
    t, x, ey, rng = synth(3000, 0.2, 0.05, 2)
    y = 0.5 + 0.9 * t + ey + rng.normal(0, 0.15, len(t))
    r = M.fit(x, y, "linear", "CSQ", sx=0.2, sy=0.05, eqerr=True)
    assert 0.1 < r["se"] < 0.2


def test_triple_collocation():
    rng = np.random.default_rng(3)
    t = rng.uniform(4, 7, 20000)
    s = M.tc(t + rng.normal(0, 0.1, t.size), 0.9 * t + 0.5 + rng.normal(0, 0.3, t.size), t + rng.normal(0, 0.2, t.size))
    assert np.allclose(s, [0.1, 0.3, 0.2], atol=0.02)


def gr(n, b, mc, rng):
    return np.round((mc - 0.05 + rng.exponential(1 / (b * np.log(10)), n)) / 0.1) * 0.1


def test_weichert_recovers_b_and_rate():
    import x1_stats as S
    rng = np.random.default_rng(4)
    b, rate = 0.9, 20.0
    yr0 = {3.0: 2000, 4.0: 1964, 5.0: 1900}
    m, yr = [], []
    for mc, y0 in yr0.items():
        lo, hi = mc, {3.0: 4.0, 4.0: 5.0, 5.0: 9.9}[mc]
        T = S.T_END - y0
        n = rng.poisson(rate * T * (10 ** (-b * (lo - 3.0)) - 10 ** (-b * (hi - 3.0))))
        x = gr(n * 3, b, lo, rng)
        x = x[(x >= lo - 1e-9) & (x < hi - 1e-9)][:n]
        m.append(x)
        yr.append(rng.uniform(y0, S.T_END, len(x)))
    m, yr = np.concatenate(m), np.concatenate(yr)
    tab = [[1900, 5.0], [1964, 4.0], [2000, 3.0]]
    bb, sb, r, n = S.weichert(m, yr, tab, 3.0)
    assert abs(bb - b) < 3 * sb + 0.02
    assert abs(r / rate - 1) < 0.1


def test_bpositive_recovers_b():
    import x1_stats as S
    rng = np.random.default_rng(5)
    m = gr(20000, 1.1, 3.0, rng)
    t = np.arange(len(m), dtype=float)
    assert abs(S.bpos(m, t, 3.0) - 1.1) < 0.06

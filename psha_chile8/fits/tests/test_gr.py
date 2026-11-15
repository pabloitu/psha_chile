"""Estimators of gr.py on synthetic catalogues built like the frozen one (synth.py): the table of DECISIONS, class
weights, the magnitude errors of the real events per kind and period, 0.1 bins."""
import numpy as np
import pytest

import gr as G
import synth as S

B, N5 = 0.96, 25.0
TB, TE = S.TABLE, S.TE
REF = (5.0, 7.0, 8.0)


@pytest.fixture(scope="module")
def cats(cat, pool):
    wp = S.weights(cat, "interface")
    return [S.catalogue(B, N5, np.random.default_rng(s), pool, wpool=wp) for s in range(24)]


def recovered(fits, tol_b, tol_n):
    """Mean b, a and N(>= 5, 7, 8) over the catalogues against the true line."""
    assert abs(np.mean([f["b"] for f in fits]) - B) < tol_b
    assert abs(np.mean([G.a_value(f) for f in fits]) - (np.log10(N5) + B * 4.95)) < tol_b * 6
    for M, tol in zip(REF, tol_n):
        assert abs(np.mean([G.n_ge(f, M) for f in fits]) / S.truth(B, N5, M) - 1) < tol, M


def test_weichert(cats):
    recovered([G.fit(c["m"], c["t"], c["w"], TB, TE, sig=c["sig"]) for c in cats], 0.01, (0.02, 0.06, 0.08))


def test_weichert_without_the_error_weight_is_high(cats):
    f = [G.fit(c["m"], c["t"], c["w"], TB, TE) for c in cats]
    assert np.mean([G.n_ge(q, 5.0) for q in f]) / N5 > 1.06


def test_truncated_and_tapered(cats):
    tr = [G.fit(c["m"], c["t"], c["w"], TB, TE, sig=c["sig"], shape="trunc", top=9.7) for c in cats]
    tp = [G.fit(c["m"], c["t"], c["w"], TB, TE, sig=c["sig"], shape="taper", corner=11.0) for c in cats]
    recovered(tr, 0.01, (0.02, 0.06, 0.09))
    recovered(tp, 0.01, (0.02, 0.06, 0.09))
    f = G.fit(cats[0]["m"], cats[0]["t"], cats[0]["w"], TB, TE, sig=cats[0]["sig"])
    assert abs(tr[0]["b"] - f["b"]) < 1e-3 and abs(tp[0]["b"] - f["b"]) < 2e-3
    # a line cut at mmax holds nothing above it and the same number below
    q = G.fit(cats[0]["m"], cats[0]["t"], cats[0]["w"], TB, TE, shape="trunc", top=8.6)
    assert G.n_ge(q, 8.6) == 0 and abs(G.n_ge(q, 5.0) - q["rate"]) < 1e-12
    # a corner lowers the rate of the largest events only
    lo = G.fit(cats[0]["m"], cats[0]["t"], cats[0]["w"], TB, TE, shape="taper", corner=8.5, bfix=None)
    assert G.n_ge(dict(lo, b=f["b"], rate=f["rate"]), 9.0) < 0.5 * G.n_ge(f, 9.0)


def test_aki_utsu(cats):
    recovered([G.aki_utsu(c["m"], c["t"], c["w"], 5.0, 1976, TE, sig=c["sig"]) for c in cats], 0.03, (0.05, 0.15, 0.25))


def test_ogata_katsura(cats):
    f = [G.ogata_katsura(c["m"], c["t"], c["w"], [(1976, 2000), (2000, 2027)], TE, sig=c["sig"]) for c in cats[:8]]
    assert abs(np.mean([q["b"] for q in f]) - B) < 0.04
    assert abs(np.mean([G.n_ge(q, 5.0) for q in f]) / N5 - 1) < 0.08


def test_least_squares_runs_and_is_rough(cats):
    f = [G.least_squares(G.fit(c["m"], c["t"], c["w"], TB, TE, sig=c["sig"])) for c in cats]
    assert abs(np.mean([q["b"] for q in f]) - B) < 0.15


def test_kijko_smit_agrees_with_weichert(cats):
    c = cats[0]
    ww = c["w"] * G.magw(c["sig"], B)
    assert abs(G.kijko_smit(c["m"], c["t"], ww, TB, TE) - G.fit(c["m"], c["t"], ww, TB, TE)["b"]) < 0.04


def test_weights():
    rng = np.random.default_rng(0)
    m = np.round(5.0 + np.floor(rng.exponential(1 / G.LN10, 4000) / 0.1) * 0.1, 1)
    t, w = rng.uniform(1976, TE, m.size), np.ones(m.size)
    a = G.fit(m, t, w, TB, TE)
    h = G.fit(np.r_[m, m], np.r_[t, t], np.r_[0.3 * w, 0.7 * w], TB, TE)
    p = G.fit(m, t, 0.4 * w, TB, TE)
    assert abs(a["b"] - h["b"]) < 1e-9 and abs(a["rate"] / h["rate"] - 1) < 1e-9
    assert abs(a["b"] - p["b"]) < 1e-9 and abs(p["rate"] / a["rate"] - 0.4) < 1e-9
    assert abs(G.magw(0.5, 2.2 / G.LN10) - 0.546) < 1e-3
    # b fixed: the total rate above the floor does not move
    one = [(5.0, 1976)]
    assert abs(G.fit(m, t, w, one, TE, bfix=a["b"] + 0.2)["rate"] / G.fit(m, t, w, one, TE)["rate"] - 1) < 1e-9


def test_large_event_check(cats):
    c = cats[1]
    f = G.fit(c["m"], c["t"], c["w"], TB, TE, sig=c["sig"])
    e, o, ok = G.check(f, 7.0)
    assert ok and abs(e - G.n_ge(f, 7.0) * (TE - 1905)) / e < 0.35
    assert not G.check(dict(f, rate=3 * f["rate"]), 7.0)[2]


def test_shrink():
    mu, tau2, b = G.shrink([1.0, 1.0, 1.0], [0.05, 0.1, 0.2])
    assert tau2 == 0 and np.allclose(b, 1.0)
    mu, tau2, b = G.shrink([0.8, 1.0, 1.4], [0.02, 0.02, 0.3])
    assert tau2 > 0 and abs(b[0] - 0.8) < 0.01 and 0.9 < b[2] < 1.4


def test_bootstrap_covers_the_truth(cat, pool):
    """5-95 % intervals of b, N(>= 5) and N(>= 7) hold the true values in 75 to 90 % of the catalogues (the rate
    keeps a bias of a few per cent from the magnitude errors; coverage on more catalogues in compare.py)."""
    wp = S.weights(cat, "forearc")
    hit, n = np.zeros(3), 80
    for s in range(n):
        c = S.catalogue(1.0, 3.5, np.random.default_rng(500 + s), pool, wpool=wp)
        f = G.fit(c["m"], c["t"], c["w"], TB, TE, sig=c["sig"], nboot=300, rng=np.random.default_rng(s))
        q = G.boot(f)
        for i, (v, tr) in enumerate([(q["b"], 1.0), (G.n_ge(q, 5.0), 3.5), (G.n_ge(q, 7.0), S.truth(1.0, 3.5, 7.0))]):
            lo, hi = np.nanpercentile(v, [5, 95])
            hit[i] += lo <= tr <= hi
    print("coverage of the 5-95 % interval (b, N5, N7):", hit / n)
    assert np.all(hit / n >= 0.7) and np.all(hit / n <= 0.99)

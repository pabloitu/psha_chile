"""The automatic completeness table on synthetic catalogues with a known table."""
import numpy as np

import gr as G
import synth as S
import table as T


def since(tb, mf):
    y = [y for q, y in tb if q <= mf + 1e-6]
    return min(y) if y else np.inf


def test_instrumental_steps_from_mc():
    import pandas as pd
    x = pd.DataFrame(dict(start=[1964, 1976, 1990, 1964, 1976, 1990], end=[1976, 1990, 2000] * 2,
                          mc=[5.2, 5.0, 4.6, 5.1, 4.8, 4.9]))
    assert T.instrumental(x) == [(5.0, 1976), (5.2, 1964)]
    assert T.instrumental(x, floor=4.5) == [(4.9, 1990), (5.0, 1976), (5.2, 1964)]


def test_mc_of_a_thinned_sample():
    rng = np.random.default_rng(1)
    m = np.round(3.5 + np.floor(rng.exponential(1 / G.LN10, 60000) / 0.1) * 0.1, 1)
    m = m[rng.uniform(size=m.size) < np.where(m >= 4.95, 1, 10 ** (-(5.0 - m) / 0.5))]
    w = np.ones(m.size)
    assert 4.8 <= T.mc_bstab(m, w) <= 5.2
    assert 4.8 <= T.mc_ks(m, w) <= 5.2


def test_historical_steps_with_the_instrumental_ones_given(pool):
    """The rate rule finds the steps of Mw 7.0, 7.5 and 8.0 at or before the true year, never more than a block
    late; it cannot see mild incompleteness of few events, so a step can come out early."""
    inst = [q for q in S.TABLE if q[1] >= T.HIST_FROM]
    for s in range(3):
        c = S.catalogue(1.05, 70.0, np.random.default_rng(40 + s), pool, roll="exp")
        k = c["m"] >= T.FLOOR - 1e-6
        tb = sorted(inst + T.historical(c["m"][k], c["t"][k], c["w"][k], S.TE, inst))
        assert all(q in tb for q in inst)
        ys = [y for _, y in tb]
        assert all(a > b for a, b in zip(ys, ys[1:]))
        assert -80 <= since(tb, 7.0) - 1905 <= T.DT and since(tb, 7.5) <= 1830 + T.DT and since(tb, 8.0) == 1500


def test_automatic_table_on_a_known_table(pool):
    """All events of a margin, the table of DECISIONS. The table never starts below the floor, and the fit on it
    is close to the fit on the true table; single steps scatter (reported by compare.py)."""
    c = S.catalogue(1.05, 70.0, np.random.default_rng(40), pool, roll="exp")
    tb, x = T.auto(c["m"], c["t"], np.full(c["m"].size, -30.0), S.TE, reg={"all": (-90, 0)})
    assert since(tb, 5.0) == 1976 and since(tb, 5.2) == 1964 and since(tb, 4.9) == np.inf
    assert since(tb, 7.0) == 1905 and since(tb, 8.0) == 1500
    for s in (41, 42):
        c = S.catalogue(1.05, 70.0, np.random.default_rng(s), pool, roll="exp")
        tb, x = T.auto(c["m"], c["t"], np.full(c["m"].size, -30.0), S.TE, reg={"all": (-90, 0)})
        f, f0 = (G.fit(c["m"], c["t"], c["w"], q, S.TE, sig=c["sig"]) for q in (tb, S.TABLE))
        assert min(q for q, _ in tb) >= T.FLOOR
        assert abs(f["b"] - f0["b"]) < 0.05 and abs(G.n_ge(f, 5.0) / G.n_ge(f0, 5.0) - 1) < 0.05

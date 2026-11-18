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


def test_mc_series_on_a_known_table(pool, monkeypatch):
    """One segment with the instrumental steps of the synthetic table (5.2 from 1964, 5.0 from 1976): Mc(t) reads about
    5.0-5.2 before 1976 and at most 5.0 after (median of the windows). The step found for 5.0 by the last-window rule
    can come out years late where Mc sits at 5.0 (synthetic test of 17 Nov, FITS.md section 2), so it is not tested."""
    monkeypatch.setattr(T, "NBOOT_MC", 3)
    c = S.catalogue(1.05, 70.0, np.random.default_rng(40), pool, roll="exp")
    x = T.mc_series(c["m"], c["t"])
    assert 4.95 <= x[x.t < 1976].mc.median() <= 5.25 and x[x.t > 1980].mc.median() <= 5.0
    tb = T.envelope({"all": T.steps_series(x, S.TE)}, S.TE)
    assert since(T.cut(tb), 5.0) >= 1976


def test_published_checks_find_a_known_start():
    """Hakimhashemi and Grünthal (2012) and Albarello et al. (2001) on a band of about 0.2 events a year (the Mw 7
    band), complete from 1900, one event in five kept before: medians over 40 catalogues within 25 years."""
    r = []
    for s in range(40):
        rng = np.random.default_rng(s)
        t = np.sort(rng.uniform(1600, 2026, 90))
        t = t[(t >= 1900) | (rng.uniform(size=t.size) < 0.2)]
        r.append((T.hg2012(t), T.albarello2001(t, 2026.0)))
    h, a = np.median(np.array(r), 0)
    assert abs(h - 1900) < 25 and abs(a - 1900) < 25

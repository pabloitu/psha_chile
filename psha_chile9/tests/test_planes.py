import numpy as np
import pandas as pd

from psha9.stats import depth as DP
from psha9.stats import mech as M


def test_types():
    m = np.array([[0, 30, 90], [0, 60, -90], [0, 90, 0], [223, 61, 164]], float)
    k, obl = M.kind(M.plunges(*m.T))
    assert list(k) == ["reverse", "normal", "strike-slip", "oblique"]
    assert list(obl) == [False, False, False, True]


def test_auxiliary_and_kagan():
    for m in [(10, 40, 90), (110, 90, 0), (200, 25, -80), (35, 70, 145)]:
        a = M.aux(m)
        assert M.kagan(m, a) < 1e-4
        b = M.aux(a)
        assert M.kagan(m, b) < 1e-4
    assert abs(M.kagan((0, 90, 0), (90, 90, 0)) - 90) < 1e-3


def test_representative_of_one_mechanism():
    e = pd.DataFrame([dict(strike1=20, dip1=35, rake1=100, w=1.0)])
    e[["strike2", "dip2", "rake2"]] = M.aux((20, 35, 100))
    p, a = M.representative(e)
    assert M.kagan(p, (20, 35, 100)) < 1e-3


def test_slices_sum_to_one():
    H = np.zeros((2, len(DP.BINS) - 1))
    H[0, 60:90] = 1.0
    H[1, 50:52] = 3.0
    z = DP.zone(H, np.array([30.0, 3.0]), lsd=np.array([30.0, 30.0]))
    assert np.allclose(z[["w1", "w2", "w3"]].sum(1), 1)
    assert (z.h1 < z.h2).all() and (z.h2 < z.h3).all()

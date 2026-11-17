import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

T = Path(__file__).resolve().parent
sys.path.insert(0, str(T.parent))
import npd as N  # noqa: E402

TAB = T.parent / f"npd_{N.DATE}.csv"


@pytest.mark.skipif(not TAB.exists(), reason="run npd.py first")
def test_table():
    t = pd.read_csv(TAB)
    assert (np.isclose(t.groupby("class").weight.sum(), 1).all() and t.strike.between(0, 359.99).all()
            and t.dip.between(5, 90).all() and t.rake.between(-180, 180).all() and set(t["class"]) == set(N.CLASSES))


def test_types_and_planes():
    k, obl, _ = N.kind(np.array([0.0, 0.0, 0.0]), np.array([45.0, 60.0, 90.0]), np.array([90.0, -90.0, 0.0]))
    assert list(k) == ["reverse", "normal", "strike-slip"] and not obl.any()
    n, s = N.vectors(30.0, 40.0, 70.0)
    a = N.plane(s, n)
    n2, s2 = N.vectors(a[0][0], a[1][0], a[2][0])
    assert np.allclose(np.abs(n2 @ s), 1) and np.allclose(np.abs(s2 @ n), 1)
    assert np.allclose([x[0] for x in N.plane(n, s)], [30, 40, 70])
    x, y = N.ternary(np.array([[0.0, 90.0, 0.0], [0.0, 0.0, 90.0]]))
    assert np.allclose([x[0], y[1]], [1.2247, 1.4142], atol=1e-3)


def test_kagan():
    m = (30.0, 40.0, 70.0)
    n, s = N.vectors(*m)
    aux = tuple(x[0] for x in N.plane(s, n))
    assert N.kagan(m, m) < 1e-4 and N.kagan(m, aux) < 1e-4
    assert abs(N.kagan((0.0, 45.0, 90.0), (0.0, 45.0, -90.0)) - 180) < 1e-4 or N.kagan((0.0, 45.0, 90.0), (0.0, 45.0, -90.0)) > 89


@pytest.mark.skipif(not TAB.exists(), reason="run npd.py first")
def test_fault_classes():
    t = pd.read_csv(TAB)
    c = pd.read_csv(T.parent / f"tables/counts_{N.DATE}.csv").set_index("cls")
    for k in c.index[c.w_inside < N.MIN_N]:
        r = t[t["class"] == k]
        assert len(r) == 2 and np.allclose(r.weight, 0.5) and np.allclose(r.iloc[0, 1:4], N.FAULT[k])
        assert N.kagan(tuple(r.iloc[0, 1:4]), tuple(r.iloc[1, 1:4])) < 10
    assert N.kind(*np.array([N.FAULT["backarc"], N.FAULT["patagonia"]]).T)[0].tolist() == ["reverse", "strike-slip"]

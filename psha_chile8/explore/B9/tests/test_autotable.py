"""The automatic completeness table of b9_11_autotable on synthetic catalogues with a known table."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import b9_lib as L
import b9_11_autotable as A

TB = [(4.5, 2000), (5.0, 1976), (5.5, 1964), (6.5, 1930), (7.0, 1900)]
B, N45, TE = 0.93, 77.0, 2026.9


def cat(seed):
    t, m = L.synth(B, N45, TB, A.Y0, TE, np.random.default_rng(seed))
    return m, t, np.ones(m.size)


def since(tb, mf):
    return min(y for q, y in tb if q <= mf + 1e-6)


def test_joint_rule_finds_the_table():
    m, t, w = cat(3)
    best, runs = A.auto(m, t, w, TE)
    assert abs(best["b"] - B) < 0.03
    for mf in (4.5, 5.0, 5.5):
        assert abs(since(best["table"], mf) - since(TB, mf)) <= A.DT
    ys = [y for _, y in sorted(best["table"])]
    assert all(a > b for a, b in zip(ys, ys[1:]))


def test_historical_steps_with_the_instrumental_ones_given():
    m, t, w = cat(4)
    inst = [q for q in TB if q[1] >= A.HIST_FROM]
    hy = A.hybrid(m, t, w, TE, inst)
    assert all(q in hy for q in inst)
    assert abs(since(hy, 7.0) - 1900) <= 2 * A.DT
    r = L.fit(L.kbin(m), t, w, hy, TE)
    assert abs(r["b"] - B) < 0.03


def test_kijko_smit_agrees_with_weichert_on_the_true_table():
    m, t, w = cat(5)
    bk, rk, mk = A.kijko_smit(m, t, w, TB, TE)
    r = L.fit(L.kbin(m), t, w, TB, TE)
    assert abs(bk - r["b"]) < 0.02
    assert abs(L.n_ge(bk, rk, mk, 5.0) / L.n_ge(r["b"], r["rate"], r["m_lo"], 5.0) - 1) < 0.03
    b1, _, _ = A.kijko_smit(m, t, w, [(4.5, 2000)], TE)
    s = t >= 2000
    assert abs(b1 - L.tinti(m[s], w[s], 4.5)[0]) < 1e-9

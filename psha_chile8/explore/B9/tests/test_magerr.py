"""The magnitude-error weight of b9_9_magerr on synthetic catalogues with a known rate."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import b9_lib as L
import b9_9_magerr as E

TB = [(5.0, 1964)]
T0, T1 = 1964.0, 2026.0
B, N5, SIG = 1.0, 40.0, 0.25


def cat(seed, sig=SIG):
    rng = np.random.default_rng(seed)
    g = 3.45
    n = rng.poisson(N5 * 10 ** (B * (4.95 - g)) * (T1 - T0))
    m = g + rng.exponential(1 / (B * L.LN10), n)
    k = L.kbin(np.rint((m + rng.normal(0, sig, n)) * 10) / 10)
    return k, rng.uniform(T0, T1, n), np.full(n, sig), np.full(n, "proxy", object)


def test_error_inflates_the_rate_and_the_weight_removes_it():
    raw, wtd, bs = [], [], []
    for s in range(10):
        k, t, sig, kind = cat(s)
        w = np.ones(k.size)
        raw.append(E.gr(E.fitw(k, t, w, sig, kind, TB, T1, []))["N5"])
        r = E.gr(E.fitw(k, t, w, sig, kind, TB, T1, E.INSTR))
        wtd.append(r["N5"]), bs.append(r["b"])
    g2 = (B * L.LN10) ** 2 * SIG ** 2 / 2
    assert abs(np.mean(raw) / N5 / np.exp(g2) - 1) < 0.02
    assert abs(np.mean(wtd) / N5 - 1) < 0.02
    assert abs(np.mean(bs) - B) < 0.01


def test_weight_only_for_the_listed_kinds():
    sig, kind = np.array([0.5, 0.2, 0.2]), np.array(["cabello", "proxy", "direct"], object)
    w = E.magw(sig, kind, 1.0, E.MODERN)
    assert w[0] == 1.0
    assert np.allclose(w[1:], np.exp(-L.LN10 ** 2 * 0.04 / 2))
    assert np.all(E.magw(sig, kind, 1.0, None) < 1)
    k, t, s, kd = cat(1)
    r0 = E.fitw(k, t, np.ones(k.size), s, np.full(k.size, "cabello", object), TB, T1, E.INSTR)
    r1 = E.fitw(k, t, np.ones(k.size), s, kd, TB, T1, [])
    assert r0["rate"] == r1["rate"]

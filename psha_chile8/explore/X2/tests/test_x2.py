import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import x2_fit as xf  # noqa: E402


def gr_pairs(n=20000, sx=0.2, sy=0.08, seed=0):
    rng = np.random.default_rng(seed)
    m = 4.0 + rng.exponential(1 / np.log(10), n)
    x = 0.3 + 0.9 * m + rng.normal(0, sx, n)
    y = m + rng.normal(0, sy, n)
    return m, x, y, rng


def test_inverse_unbiased_under_reference_floor():
    m, x, y, rng = gr_pairs()
    k = rng.random(len(y)) < 1 / (1 + np.exp(-(y - 5.0) / 0.1))
    f = xf.fit_inv(y[k], x[k], 0.08, "linear")
    assert abs(f["p"][1] - 0.9) < 0.04
    mw = xf.conv_inv(f, np.array([4.0]))[0][0]
    assert abs(mw - (4.0 - 0.3) / 0.9) < 0.08


def test_forward_biased_under_reference_floor():
    m, x, y, rng = gr_pairs()
    k = y >= 5.0
    b, a = np.polyfit(x[k], y[k], 1)
    assert a + b * 4.0 - (4.0 - 0.3) / 0.9 > 0.2


def test_hinge_recovers_saturation():
    rng = np.random.default_rng(1)
    y = rng.uniform(4.5, 7.5, 5000)
    x = np.where(y < 6.0, y, 6.0 + 0.4 * (y - 6.0)) + rng.normal(0, 0.1, len(y))
    f = xf.fit_inv(y, x, 0.0, "hinge")
    a, b1, b2, k = f["p"]
    assert abs(k - 6.0) < 0.15 and abs(b1 - 1.0) < 0.05 and abs(b2 - 0.4) < 0.05


def test_trunc_recovers_conditional_mean():
    rng = np.random.default_rng(2)
    x = rng.uniform(4.0, 7.0, 8000)
    y = 0.5 + 0.9 * x + rng.normal(0, 0.2, len(x))
    c = np.full(len(x), 5.5)
    f = xf.fit_trunc(x, y, c, "linear")
    assert abs(f["p"][1] - 0.9) < 0.05 and abs(f["s"] - 0.2) < 0.03

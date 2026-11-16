"""The corner of the tapered line from Mmax and b (Kagan 2002b, eq. 12) gives the moment rate of the line cut at
Mmax with the same b and the same rate above the threshold."""
import numpy as np
import pytest

import gr as G


def moment_rate(f, lo=4.95, hi=13.0, dm=0.001):
    e = np.arange(lo, hi, dm)
    n = f["rate"] * -np.diff(G.surv(f, e))
    return (n * G.moment(e[:-1] + dm / 2)).sum()


@pytest.mark.parametrize("b, mx", [(0.96, 9.75), (0.92, 8.75), (1.15, 8.25), (1.0, 7.45), (1.23, 7.45)])
def test_corner_keeps_the_moment_rate(b, mx):
    c = float(G.kagan_corner(mx, b))
    cut = dict(shape="trunc", b=b, rate=25.0, m_lo=4.95, mmax=mx, corner=None)
    tap = dict(shape="taper", b=b, rate=25.0, m_lo=4.95, mmax=None, corner=c)
    assert abs(moment_rate(tap) / moment_rate(cut) - 1) < 0.01


def test_corner_values():
    # DECISIONS: about 0.21 below Mmax for b 1.15, about 0.27 for b 0.96
    assert abs(G.kagan_corner(8.25, 1.15) - 8.25 + 0.21) < 0.01
    assert abs(G.kagan_corner(9.75, 0.96) - 9.75 + 0.27) < 0.01

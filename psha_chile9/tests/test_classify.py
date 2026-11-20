import numpy as np

from psha9.catalog import classify as C


def test_scores_by_depth():
    z, s, top = np.array([30.0, 5.0, 90.0]), np.full(3, 5.0), np.full(3, 30.0)
    q = C.by_depth(z, s, top, 15.0, 0.0, np.ones(3))
    assert np.allclose(q.sum(1), 1) and (q >= 0).all()
    assert q.argmax(1).tolist() == [0, 2, 1]
    assert C.by_depth(z[:1], s[:1], top[:1], 15.0, 0.0, np.zeros(1))[0, 0] == 0


def test_band_offset_moves_the_band():
    z, s, top = np.array([52.0]), np.array([1.0]), np.array([30.0])
    assert C.by_depth(z, s, top, 5.0, 0.0, np.ones(1))[0, 0] < 0.01
    assert C.by_depth(z, s, top, 5.0, 20.0, np.ones(1))[0, 0] > 0.9


def test_interface_mechanism_has_no_misfit():
    ss, sd = np.array([10.0, 350.0]), np.array([20.0, 15.0])
    n = C.nu(ss, sd, 90.0)[0]
    h = np.array([np.cos(np.radians(C.SI["az"])), np.sin(np.radians(C.SI["az"])), 0.0])
    v = h - (h * n).sum(-1, keepdims=True) * n
    # rake of the convergence direction on the slab plane
    k = np.degrees(np.arctan2(-v[:, 2] / np.sin(np.radians(sd)), v[:, 0] * np.cos(np.radians(ss)) + v[:, 1] * np.sin(np.radians(ss))))
    assert np.allclose(C.skew(ss, sd, k, ss, sd), 0, atol=1e-4)
    assert (C.skew(ss, sd, k - 180, ss, sd) > 1).all()


def test_lift_keeps_the_sum():
    q = C.lift(np.array([[0.2, 0.5, 0.3]]), np.array([True]), 3.9)
    assert np.isclose(q.sum(), 1) and q[0, 0] > 0.2 and np.isclose(q[0, 1] / q[0, 2], 5 / 3)


def test_west_of_the_edge():
    assert C.west_of_edge([-80.0, -70.0], [-30.0, -30.0]).tolist() == [True, False]

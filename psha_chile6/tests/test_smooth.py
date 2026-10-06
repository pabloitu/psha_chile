# Smoothing kernel, spatial mass and the per-cell magnitude bins of lib.smooth.

import numpy as np

from lib import gr, smooth


def test_kernel_is_the_distance_to_the_nth_neighbour_with_a_floor():
    lon = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
    h = smooth.kernel(lon, np.zeros(5), 2, 1.0)
    d = lambda a, b: float(smooth.hav(a, 0, b, 0))
    assert abs(h[0] - d(0.0, 0.2)) < 1e-6 and abs(h[2] - d(0.2, 0.3)) < 1e-6
    assert (smooth.kernel(lon, np.zeros(5), 2, 50.0) == 50.0).all()


def test_kernel_of_one_event_is_the_floor():
    assert smooth.kernel(np.array([-70.0]), np.array([-33.0]), 25, 5.0).tolist() == [5.0]
    gl, ga = np.meshgrid(np.arange(-70.5, -69.5, 0.1), np.arange(-33.5, -32.5, 0.1))
    f = smooth.field(np.array([-70.0]), np.array([-33.0]), np.array([1.0]), np.array([5.0]), gl.ravel(), ga.ravel(), 1.5, 500.0)
    assert abs(f.sum() - 1.0) < 1e-12


def test_field_conserves_the_weight_of_every_event():
    rng = np.random.default_rng(0)
    gl, ga = np.meshgrid(np.arange(-72, -68, 0.1), np.arange(-35, -31, 0.1))
    gl, ga = gl.ravel(), ga.ravel()
    el, ea, w = rng.uniform(-71, -69, 12), rng.uniform(-34, -32, 12), rng.uniform(0.5, 2, 12)
    h = smooth.kernel(el, ea, 3, 5.0)
    for kind in ("power", "gauss"):
        f = smooth.field(el, ea, w, h, gl, ga, 1.5, 500.0, kind)
        assert abs(f.sum() / w.sum() - 1) < 1e-12


def test_field_renormalizes_events_near_the_edge_of_the_domain():
    gl, ga = np.meshgrid(np.arange(-70, -69.5, 0.1), np.arange(-33, -32.5, 0.1))
    f = smooth.field(np.array([-70.2]), np.array([-33.1]), np.array([2.0]), np.array([10.0]), gl.ravel(), ga.ravel(), 1.5, 500.0)
    assert abs(f.sum() - 2.0) < 1e-12


def test_tgr_bins_total_and_top_cut():
    e = smooth.edges(4.9, 7.4, 0.1)
    assert e[-1] >= gr.top(7.4) - 1e-9
    shape = np.array([1.0, 3.0])
    rb = smooth.tgr_bins(shape, 2.0, 0.9, e, 7.4)
    assert abs(rb.sum() - 2.0 * (1 - 10 ** (-0.9 * (gr.top(7.4) - 4.9)))) < 1e-12
    assert np.allclose(rb.sum(axis=1), [0.25 * rb.sum(), 0.75 * rb.sum()])
    assert rb[:, e[:-1] >= gr.top(7.4) - 1e-9].sum() == 0.0


def test_binned_gr_equals_the_continuous_gr():
    e = smooth.edges(4.9, 7.4, 0.1)
    rb = smooth.tgr_bins(np.ones(1), 1.0, 0.9, e, 7.4).ravel()
    n_ge = lambda x: rb[e[:-1] >= x - 1e-9].sum()
    cont = lambda x: (10 ** (-0.9 * (x - 4.9)) - 10 ** (-0.9 * (gr.top(7.4) - 4.9)))
    for x in (5.5, 6.5, 7.3):
        assert abs(n_ge(x) / cont(x) - 1) < 1e-9

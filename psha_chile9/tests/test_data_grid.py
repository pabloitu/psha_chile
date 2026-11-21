import numpy as np
from shapely.geometry import box

from psha9.data_processing.build import grid


def test_grid_centres_and_boundary():
    g = grid(box(-70.0, -30.0, -69.5, -29.5), 0.1)
    assert len(g) == 36
    assert np.allclose(g.lon * 10, np.round(g.lon * 10)) and np.allclose(g.lat * 10, np.round(g.lat * 10))
    assert ((g.lon == -70.0) & (g.lat == -30.0)).any()


def test_grid_outside_excluded():
    g = grid(box(-70.05, -30.05, -69.95, -29.95), 0.1)
    assert len(g) == 1 and g.lon.iloc[0] == -70.0 and g.lat.iloc[0] == -30.0


def test_grid_boundary_row_with_float_noise():
    for d in (1e-11, -1e-11):
        g = grid(box(-70.05, -30.05, -69.95, -15.5 + d), 0.1)
        assert np.isclose(g.lat.max(), -15.5)
    g = grid(box(-70.05, -30.05, -69.95, -15.5 - 1e-4), 0.1)
    assert np.isclose(g.lat.max(), -15.6)

import matplotlib
import numpy as np

from plots import colors as C
from plots import maps as M


def test_every_palette_is_registered_both_ways():
    n = C.colormaps()
    assert len(n) == sum(len(C.DATA[g]) for g in C.GROUPS) and "pp.pt_sea" in n
    assert all(k in matplotlib.colormaps and k + "_r" in matplotlib.colormaps for k in n)
    assert C.source("pp.thermal_r").startswith("Thyng")


def test_depth_classes_and_unknown_depth():
    c = C.depth_color([5, 20, 45, 650, np.nan])
    d = C.depth_colors()
    assert len(d) == len(C.DEPTH_EDGES) - 1
    assert c.tolist() == [d[0], d[1], d[2], d[-1], C.NODATA]


def test_categorical_palette_refuses_too_many():
    assert len(C.palette("tol_muted", 3)) == 3
    try:
        C.palette("tol_muted", 20)
        assert False
    except ValueError:
        pass


def test_size_grows_by_magnitude_and_halves_split_the_height():
    assert np.isclose(M.size(5.0) / M.size(4.0), M.GROW) and M.size(4.5) == 2.0 and M.size(np.nan) == M.size(3.0)
    (n, a), (s, b) = M.halves()
    assert n == "north" and a[3] == M.FIG_EXTENT[3] and b[2] == M.FIG_EXTENT[2] and a[2] == b[3]
    y = M.PROJ.transform_points(M.PC, np.full(3, M.FIG_EXTENT[0]), np.array([b[2], a[2], a[3]]))[:, 1]
    assert np.isclose(y[1] - y[0], y[2] - y[1])


def test_bands_tile_the_extent_with_equal_heights():
    b = M.bands(3)
    assert b[0][3] == M.FIG_EXTENT[3] and b[-1][2] == M.FIG_EXTENT[2] and all(b[i][2] == b[i + 1][3] for i in range(2))
    h = [np.diff(M.PROJ.transform_points(M.PC, np.full(2, e[0]), np.array(e[2:]))[:, 1])[0] for e in b]
    assert np.allclose(h, h[0])

# Declustering windows and the window algorithm of lib.dc.

import numpy as np
import pandas as pd
import pytest

from lib import dc


def test_haversine_known_distances():
    assert abs(float(dc.hav(0, 0, 0, 1)) - 111.195) < 0.01
    assert abs(float(dc.hav(0, 0, 90, 0)) - 10007.54) < 0.1
    assert float(dc.hav(-70, -33, -70, -33)) == 0.0


def test_gk74_windows_are_the_published_formulas():
    m = np.array([5.0, 6.0, 7.0, 8.0])
    L, T = dc.windows(m, "gk74")
    assert np.allclose(L, 10 ** (0.1238 * m + 0.983))
    assert np.allclose(T, [10 ** (0.5409 * 5 - 0.547), 10 ** (0.5409 * 6 - 0.547), 10 ** (0.032 * 7 + 2.7389), 10 ** (0.032 * 8 + 2.7389)])


def test_gk74_windows_are_close_to_the_gardner_knopoff_table():
    L, T = dc.windows(np.array([6.0, 7.0]), "gk74")
    assert abs(L[0] / 54 - 1) < 0.05 and abs(T[0] / 510 - 1) < 0.05
    assert abs(L[1] / 76 - 1) < 0.10 and abs(T[1] / 960 - 1) < 0.10


def test_other_windows_are_the_van_stiphout_formulas():
    m = np.array([6.0, 7.0])
    L, T = dc.windows(m, "uhrhammer")
    assert np.allclose(L, np.exp(-1.024 + 0.804 * m)) and np.allclose(T, np.exp(-2.87 + 1.235 * m))
    L, T = dc.windows(m, "gruenthal")
    assert np.allclose(L, np.exp(1.77 + np.sqrt(0.037 + 1.02 * m)))
    assert np.allclose(T, [abs(np.exp(-3.95 + np.sqrt(0.62 + 17.32 * 6.0))), 10 ** (2.8 + 0.024 * 7.0)])


def test_windows_of_great_earthquakes_stay_small_known_limit():
    # a point-source window for M9.5 is about 144 km and 3 years, far below the rupture and the
    # aftershock duration: the declustered catalog keeps aftershocks of great earthquakes
    L, T = dc.windows(np.array([9.5]), "gk74")
    assert 100 < L[0] < 200 and 2 < T[0] / 365.25 < 4


def cluster():
    # main M7 at day 1000; 30 aftershocks within 20 km and 100 days; a foreshock 3 days before;
    # an event 300 km away; one 10 years later at the same place
    rng = np.random.default_rng(0)
    n = 30
    t = np.r_[1000.0, 1000 + rng.uniform(0.1, 100, n), 997.0, 1050.0, 1000 + 3650.0]
    m = np.r_[7.0, rng.uniform(4.5, 5.5, n), 5.0, 5.0, 5.0]
    lon = np.r_[-70.0, -70 + rng.uniform(-0.1, 0.1, n), -70.02, -67.0, -70.0]
    lat = np.r_[-33.0, -33 + rng.uniform(-0.1, 0.1, n), -33.01, -33.0, -33.0]
    return t, m, lon, lat, n


def test_window_algorithm_on_a_known_cluster():
    t, m, lon, lat, n = cluster()
    main, cid = dc.gk(t, m, lon, lat, "gk74", 0.1)
    assert main[0]
    assert not main[1:n + 1].any()
    assert not main[n + 1]                      # foreshock inside 0.1 of the time window
    assert main[n + 2] and main[n + 3]          # far event and the event after the window
    assert main.sum() == 3


def test_symmetric_foreshock_window_and_order_invariance():
    t, m, lon, lat, n = cluster()
    p = np.random.default_rng(1).permutation(len(t))
    a, _ = dc.gk(t, m, lon, lat, "gk74", 0.1)
    b, _ = dc.gk(t[p], m[p], lon[p], lat[p], "gk74", 0.1)
    assert (a[p] == b).all()


def test_run_none_keeps_everything_and_methods_remove_events():
    t, m, lon, lat, n = cluster()
    df = pd.DataFrame({"year": 1990 + t / 365.25, "mag": m, "longitude": lon, "latitude": lat, "id": np.arange(len(t)).astype(str)})
    out, rev = dc.run(df, "none", 0.1, 1900)
    assert out["is_mainshock"].all() and len(rev) == 0
    for method in ("gk74", "uhrhammer", "gruenthal"):
        out, rev = dc.run(df, method, 0.1, 1900)
        assert 0 < out["is_mainshock"].sum() < len(df)
    out, _ = dc.run(df, "gk74", 0.1, 1900, keep=["5"])
    assert out.loc[out["id"] == "5", "is_mainshock"].iloc[0]


def test_events_before_the_start_year_pass_through():
    df = pd.DataFrame({"year": [1700.0, 1700.001], "mag": [8.0, 6.0], "longitude": [-70.0, -70.0], "latitude": [-33.0, -33.0]})
    out, _ = dc.run(df, "gk74", 0.1, 1900)
    assert out["is_mainshock"].all()

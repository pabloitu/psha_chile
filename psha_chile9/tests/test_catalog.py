import numpy as np

from psha9.catalog import magnitude as G


def test_dither_in_bin_and_fixed_per_event():
    x = np.round(np.arange(4.0, 6.0, 0.1), 1)
    ids = np.array([f"cl{i}" for i in range(len(x))])
    d = G.dither(x, "ISC mb", ids)
    assert np.all(np.abs(d - x) <= 0.05) and np.ptp(d - x) > 0.05
    assert np.allclose(G.dither(x[5:], "ISC mb", ids[5:]), d[5:])
    assert np.allclose(G.dither(np.array([4.234]), "ISC mb", ids[:1]), 4.234)


def test_inverse_fit_recovers_line():
    rng = np.random.default_rng(0)
    y = rng.uniform(4.0, 6.5, 20000)
    x = 0.5 + 0.9 * y + rng.normal(0, 0.2, len(y))
    yo = y + rng.normal(0, 0.1, len(y))
    f = G.fit_inv(yo, x, 0.1)
    mw = G.conv(f, np.array([4.6, 5.9]))[0]
    assert np.allclose(mw, (np.array([4.6, 5.9]) - 0.5) / 0.9, atol=0.03)


def test_unknown_depth_takes_the_all_depth_relation():
    rng = np.random.default_rng(1)
    y = rng.uniform(4.0, 6.5, 6000)
    z = np.where(np.arange(len(y)) % 2, 20.0, 100.0)
    x = np.where(z > 50, 0.3, 0.0) + y + rng.normal(0, 0.15, len(y))
    f = G.fit_scale("test", x, y, np.full(len(y), 2000.0), z, 0.1, cand=[("linear", "depth")], boot=0)
    mw, _, g, _ = G.convert(f, np.array([5.0, 5.0, 5.0]), np.array([20.0, 100.0, np.nan]), np.full(3, 2000.0))
    assert list(g) == ["shallow", "deep", "no depth"]
    assert mw[1] < mw[2] < mw[0]


def test_added_event_from_overrides():
    import pandas as pd
    from psha9.catalog.build import added
    cols = ["event_id", "property", "old_value", "new_value", "sigma", "reference", "page", "reason", "status"]
    rows = [["cl1", "exists", "", "true", "", "", "", "", "accepted"], ["cl1", "time", "", "1768-01-01T00:00:00.000", "", "", "", "", "accepted"],
            ["cl1", "lat", "", "-20.48", "", "", "", "", "accepted"], ["cl1", "lon", "", "-69.33", "", "", "", "", "accepted"],
            ["cl1", "mw", "", "7.7", "0.5", "", "", "", "accepted"], ["cl1", "class_hint", "", "in-slab", "", "", "", "", "accepted"],
            ["cl2", "exists", "", "true", "", "", "", "", "proposed"], ["cl0", "exists", "", "true", "", "", "", "", "accepted"]]
    o = pd.DataFrame(rows, columns=cols)
    cat = pd.DataFrame({"event_id": ["cl0"], "time": ["2000"], "lon": [0.0], "lat": [0.0], "mw": [5.0], "mw_sigma": [0.1],
                        "a6_class_hint": [None], "depth": [10.0]})
    n = added(o, cat)
    assert list(n.event_id) == ["cl1"]
    r = n.iloc[0]
    assert (r.lat, r.lon, r.mw, r.mw_sigma, r.a6_class_hint) == (-20.48, -69.33, 7.7, 0.5, "in-slab") and pd.isna(r.depth)

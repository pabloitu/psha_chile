"""Declustering on synthetic clustered catalogues: mainshocks Poisson in time and space, each with aftershocks inside a
fraction of its Gardner-Knopoff window; the number of mainshocks is recovered within 5 %."""
import numpy as np
import pandas as pd
import pytest

import decluster as D


def clustered(seed, nmain=600, prod=0.5, years=(1964.0, 2024.0)):
    rng = np.random.default_rng(seed)
    m = np.round(4.45 + rng.exponential(1 / np.log(10), nmain * 3), 1)
    m = m[m < 7.6][:nmain]
    t = rng.uniform(*years, m.size)
    lon, lat, z = rng.uniform(-76, -64, m.size), rng.uniform(-45, -18, m.size), rng.uniform(5, 200, m.size)
    rows = [dict(t=t, lon=lon, lat=lat, mw=m, depth=z, fam=rng.integers(0, 3, m.size), main=np.ones(m.size, bool))]
    for i in range(m.size):
        k = rng.poisson(prod * 10 ** (0.8 * (m[i] - 4.5)))
        if k == 0 or m[i] < 4.8:
            continue
        d, tt = D.gk_window(m[i])
        ma = np.round(4.45 + rng.exponential(1 / np.log(10), 4 * k), 1)
        ma = ma[ma <= m[i] - 0.3][:k]
        k = ma.size
        r, az = np.abs(rng.normal(0, 0.15 * d, k)), rng.uniform(0, 2 * np.pi, k)
        rows.append(dict(t=t[i] + tt / 365.25 * 0.3 * rng.uniform(0, 1, k) ** 3, mw=ma,
                         lon=lon[i] + r * np.sin(az) / (111.2 * np.cos(np.radians(lat[i]))), lat=lat[i] + r * np.cos(az) / 111.2,
                         depth=z[i] + rng.normal(0, 5, k), fam=np.full(k, rows[0]["fam"][i]), main=np.zeros(k, bool)))
    d = pd.concat([pd.DataFrame(q) for q in rows]).sort_values("t").reset_index(drop=True)
    d.loc[rng.uniform(size=len(d)) < 0.1, "depth"] = np.nan
    for j, c in enumerate(D.FAMILY.values()):
        d[c] = (d.fam == j).astype(float)
    return d


@pytest.fixture(scope="module")
def cats():
    return [clustered(s) for s in range(3)]


@pytest.mark.parametrize("method", ["gk", "gk_family"])
def test_gardner_knopoff_recovers_the_mainshocks(cats, method):
    for d in cats:
        assert d.main.sum() < 0.7 * len(d)
        x = D.decluster(d, **D.METHODS[method])
        assert abs(x.mainshock.sum() / d.main.sum() - 1) < 0.05, (method, x.mainshock.sum(), d.main.sum())
        assert (x.mainshock[d.main.to_numpy()]).mean() > 0.95
        # every aftershock points to a true mainshock
        assert d.main.to_numpy()[x.cl.to_numpy()].all()


@pytest.mark.parametrize("depth", [False, True])
def test_nearest_neighbour_recovers_the_mainshocks(cats, depth):
    """With a threshold in the gap between the two modes (log10 eta -4.0 on these catalogues)."""
    for d in cats:
        z = d.depth.to_numpy() if depth else None
        eta, par = D.nearest_neighbour(d.t.to_numpy(), d.lon.to_numpy(), d.lat.to_numpy(), d.mw.to_numpy(), z)
        main, root = D.nn_clusters(eta, par, -4.0)
        assert abs(main.sum() / d.main.sum() - 1) < 0.05, (main.sum(), d.main.sum())
        assert d.main.to_numpy()[root].mean() > 0.95


@pytest.mark.parametrize("method", ["nn", "nn_depth"])
def test_mixture_threshold_takes_background_events(cats, method):
    """The threshold of B9 (two-Gaussian mixture, equal posterior) lies in the lower tail of the background mode:
    5-15 % of the mainshocks are taken as clustered (B12, DECLUSTER.md)."""
    for d in cats:
        x = D.decluster(d, **D.METHODS[method])
        assert -0.15 < x.mainshock.sum() / d.main.sum() - 1 < -0.02
        assert not x.mainshock[~d.main.to_numpy()].any()


def test_gardner_knopoff_keeps_the_largest():
    t = np.array([2000.0, 2000.01, 2000.02])
    m = np.array([5.0, 6.5, 5.5])
    main, cl = D.gardner_knopoff(t, np.full(3, -70.0), np.array([-30.0, -30.05, -30.1]), m)
    assert list(main) == [False, True, False] and list(cl) == [1, 1, 1]
    # per group: an event of another group is not removed
    main, _ = D.gardner_knopoff(t, np.full(3, -70.0), np.array([-30.0, -30.05, -30.1]), m, group=[0, 0, 1])
    assert list(main) == [False, True, True]


def test_nearest_neighbour_keeps_the_first():
    rng = np.random.default_rng(0)
    t = np.sort(rng.uniform(1964, 2020, 200))
    lon, lat = rng.uniform(-76, -64, 200), rng.uniform(-45, -18, 200)
    t = np.r_[t[:100], 2000.0, 2000.001, 2000.002, t[100:] + 21]
    lon = np.r_[lon[:100], -70.0, -70.01, -70.02, lon[100:]]
    lat = np.r_[lat[:100], -30.0, -30.01, -30.02, lat[100:]]
    m = np.r_[np.full(100, 5.0), 5.0, 6.0, 5.0, np.full(100, 5.0)]
    eta, par = D.nearest_neighbour(t, lon, lat, m)
    main, root = D.nn_clusters(eta, par, -3.0)
    assert main[100] and not main[101] and not main[102] and root[102] == 100 and par[102] == 101


def test_nearest_neighbour_keeps_the_largest():
    rng = np.random.default_rng(0)
    t = np.r_[np.sort(rng.uniform(1964, 2020, 100)), 2021.0, 2021.001, 2021.002]
    lon, lat = np.r_[rng.uniform(-76, -64, 100), -70.0, -70.01, -70.02], np.r_[rng.uniform(-45, -18, 100), -30.0, -30.01, -30.02]
    m = np.r_[np.full(100, 5.0), 5.0, 6.0, 5.0]
    eta, par = D.nearest_neighbour(t, lon, lat, m)
    main, cl = D.nn_clusters(eta, par, -3.0, m)
    assert not main[100] and main[101] and not main[102] and list(cl[100:]) == [101, 101, 101]


def test_nearest_neighbour_per_family(cats):
    for d in cats:
        x = D.decluster(d, **D.METHODS["nn_family"])
        f = d.fam.to_numpy()
        assert (f[x.cl.to_numpy()] == f).all() and (f[x.parent[x.parent >= 0].to_numpy()] == f[x.parent >= 0]).all()
        assert -0.15 < x.mainshock.sum() / d.main.sum() - 1 < 0.02
        # the largest event of a cluster stays: aftershocks are smaller than their mainshock
        assert d.main.to_numpy()[x.cl.to_numpy()].mean() > 0.95


def test_nearest_neighbour_no_parent_at_the_same_time():
    t, lon, lat, m = np.array([2000.0, 2000.0, 2000.5]), np.full(3, -70.0), np.full(3, -30.0), np.array([6.0, 5.0, 5.0])
    eta, par = D.nearest_neighbour(t, lon, lat, m)
    assert np.isinf(eta[1]) and par[1] == -1 and par[2] == 0


def test_windows_of_van_stiphout():
    """Eqs. 1-3 of van Stiphout et al. (2012) at Mw 7: Gardner-Knopoff 70 km, 915 days (their Table 2); Uhrhammer
    (1986) wider (100 km) but far shorter (322 days); Gruenthal 86 km, 929 days."""
    d0, t0 = D.gk_window(np.array([7.0]))
    du, tu = D.gk_window(np.array([7.0]), "uhrhammer")
    dg, tg = D.gk_window(np.array([7.0]), "gruenthal")
    assert abs(d0[0] - 70) < 3 and abs(t0[0] - 915) < 40
    assert abs(du[0] - 100) < 2 and abs(tu[0] - 322) < 3 and abs(dg[0] - 86) < 2 and abs(tg[0] - 929) < 5

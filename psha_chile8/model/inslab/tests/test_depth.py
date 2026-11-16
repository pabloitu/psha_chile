import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import depth as D  # noqa: E402

TABLE = sorted((D.HERE / "tables").glob("depth_cells_2026-11-1[56]*.csv"))
CELLS = pd.DataFrame({"lon": [-69.0, -69.0], "lat": [-21.0, -29.0]})
LSD = np.array([40.0, 25.4])


def synthetic(n=6000, seed=3):
    """A slab with a double zone north of 25° S (60 % of the events 0-12 km and 40 % 28-40 km below the top) and a
    single zone south of it (14-26 km)."""
    rng = np.random.default_rng(seed)
    lat = rng.uniform(-31, -19, n)
    lon = rng.uniform(-70, -68, n)
    north = lat > -25
    up = rng.random(n) < 0.6
    d = np.where(north, np.where(up, rng.uniform(0, 12, n), rng.uniform(28, 40, n)), rng.uniform(14, 26, n))
    return pd.DataFrame({"lon": lon, "lat": lat, "d": d, "w": 1.0})


def test_synthetic_double_zone():
    z = D.zone(*D.histograms(synthetic(), CELLS), lsd=LSD)
    n, s = z.iloc[0], z.iloc[1]
    assert n.w1 == pytest.approx(0.6, abs=0.08) and n.w3 == pytest.approx(0.4, abs=0.08) and n.w2 < 0.08
    assert s.w1 < 0.05 and s.w2 == pytest.approx(0.25, abs=0.06) and s.w3 == pytest.approx(0.75, abs=0.06)
    assert (n.w1 + n.w3) / 2 - n.w2 > 0.3 > (s.w1 + s.w3) / 2 - s.w2


def test_weights_and_hypocentres():
    z = D.zone(*D.histograms(synthetic(), CELLS), lsd=LSD)
    assert np.allclose(z[["w1", "w2", "w3"]].sum(1), 1)
    b = np.c_[np.zeros(len(z)), z.lsd / 3, 2 * z.lsd / 3, z.lsd]
    for l in range(3):
        h = z[f"h{l + 1}"].to_numpy()
        assert (h >= b[:, l]).all() and (h <= b[:, l + 1]).all()
    H = z[["h1", "h2", "h3", "h_one"]].to_numpy()
    assert (H > 0).all() and (H < z.lsd.to_numpy()[:, None]).all()
    assert np.allclose(z.lsd, LSD)


def test_fraction_of_thickness():
    d = np.linspace(0, 40, 4001)
    assert D.fraction(d, np.full(d.size, 80.0), np.ones(d.size)) == pytest.approx(0.475, abs=0.002)
    z = D.zone(*D.histograms(synthetic(), CELLS), lsd=np.array([30.0, 30.0]))
    assert z.w1[0] == pytest.approx(0.75, abs=0.06) and z.w3[0] == pytest.approx(0.10, abs=0.05)


def test_few_events_take_layer_middle():
    ev = pd.DataFrame({"lon": [-69.0] * 4, "lat": [-21.0] * 4, "d": [1.0, 2.0, 3.0, 60.0], "w": 1.0})
    z = D.zone(*D.histograms(ev, CELLS.iloc[:1]), lsd=np.array([30.0]))
    assert z.neff[0] == pytest.approx(4)
    assert z.h2[0] == pytest.approx(15.0)


def test_kernel_spreads_event_weight_once():
    ev = synthetic(500)
    g = pd.DataFrame({"lon": np.repeat(np.linspace(-70, -68, 9), 9), "lat": np.tile(np.linspace(-31, -19, 9), 9)})
    H, neff = D.histograms(ev, g)
    assert H.sum() == pytest.approx(len(ev))


def test_heldout_prefers_local_shares():
    ev = synthetic(8000)
    tr, te = ev.iloc[:6000], ev.iloc[6000:].reset_index(drop=True)
    z = D.zone(*D.histograms(tr, CELLS), lsd=LSD)
    cell = np.where(te.lat > -25, 0, 1)
    ll, n = D.heldout(z, te, cell)
    assert ll > np.log(1 / 3) + 0.3 and n > 1500


def test_match_one_to_one():
    ia, ib = D.match(np.array([0.0, 5.0, 100.0]), [-30] * 3, [-70] * 3, np.array([1.0, 2.0, 300.0]), [-30] * 3, [-70] * 3)
    assert sorted(zip(ia, ib)) == [(0, 0), (1, 1)]


def test_inslab_weight():
    q = D.inslab_weight([100.0, 30.0, 40.0], [3.0, 3.0, 3.0], [60.0, 30.0, 120.0])
    assert np.allclose(q.sum(1), 1)
    assert q[0, 1] == 1 and q[1, 0] == 1 and q[2, 2] == 1


@pytest.mark.skipif(not TABLE, reason="no cell table")
def test_cell_table():
    t = pd.read_csv(TABLE[-1])
    assert np.allclose(t[["w1", "w2", "w3"]].sum(1), 1, atol=2e-3)
    H = t[["h1", "h2", "h3", "h_one"]].to_numpy()
    assert (t.usd.to_numpy()[:, None] < H).all() and (H < t.lsd.to_numpy()[:, None]).all()
    z, b1, b2 = t.lsd - t.top, t.top + (t.lsd - t.top) / 3, t.top + 2 * (t.lsd - t.top) / 3
    assert (t.h1 <= b1 + 1e-3).all() and (t.h2 >= b1 - 1e-3).all() and (t.h2 <= b2 + 1e-3).all() and (t.h3 >= b2 - 1e-3).all()
    assert np.allclose(t.usd, t.top)
    f = z / t.thk
    assert f.max() - f.min() < 0.01


OPT = D.HERE / "tables" / "depth_cells_2026-11-16b.csv"


@pytest.mark.skipif(not OPT.exists(), reason="no C15 tables")
def test_options():
    t = pd.read_csv(OPT)
    f = (t.h_one - t.top) / t.thk
    assert f.max() - f.min() < 0.01 and (t.h_one > t.usd).all() and (t.h_one < t.lsd).all()
    ref = pd.read_csv(D.HERE / "tables" / "depth_cells_2026-11-16.csv")
    assert np.allclose(t[["lsd", "w1", "w2", "w3", "h1", "h2", "h3"]], ref[["lsd", "w1", "w2", "w3", "h1", "h2", "h3"]])
    for tag, fr in (("065", 0.65), ("0615", 0.615)):
        x = pd.read_csv(D.HERE / "tables" / f"depth_cells_lsd{tag}_2026-11-16b.csv")
        assert np.allclose((x.lsd - x.top) / x.thk, fr, atol=1e-3) and (x.h3 < x.lsd).all()
        assert np.allclose(x[["h1", "h2", "h3", "h_one", "w1"]], t[["h1", "h2", "h3", "h_one", "w1"]])


def test_weights_continuous_in_lsd():
    H, ne = D.histograms(synthetic(), CELLS)
    a, b = D.zone(H, ne, lsd=LSD), D.zone(H, ne, lsd=LSD + 0.02)
    assert np.abs(a[["w1", "w2", "w3"]].to_numpy() - b[["w1", "w2", "w3"]].to_numpy()).max() < 0.005

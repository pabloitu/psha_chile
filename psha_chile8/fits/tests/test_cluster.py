"""Bootstrap of whole clusters and the large-event band with clusters (gr.fit cl=, gr.dispersion, gr.band)."""
import numpy as np

import gr as G

TABLE = [(5.0, 1976)]


def catalogue(seed, nmain=400, kids=0):
    rng = np.random.default_rng(seed)
    m = np.round(4.95 + rng.exponential(1 / G.LN10, nmain), 1)
    t = rng.uniform(1976, 2026, nmain)
    cl = np.arange(nmain)
    if kids:
        m = np.r_[m, np.repeat(m, kids)]
        t = np.r_[t, np.repeat(t, kids) + 0.01]
        cl = np.r_[cl, np.repeat(cl, kids)]
    return m, t, np.ones(m.size), cl


def test_singleton_clusters_give_the_event_bootstrap():
    m, t, w, cl = catalogue(0)
    a = G.fit(m, t, w, TABLE, 2026.0, nboot=200, rng=np.random.default_rng(3))
    b = G.fit(m, t, w, TABLE, 2026.0, nboot=200, rng=np.random.default_rng(3), cl=cl)
    assert np.allclose(a["bb"], b["bb"]) and np.allclose(a["rr"], b["rr"])


def test_clusters_widen_the_rate_interval():
    m, t, w, cl = catalogue(1, kids=3)
    a = G.fit(m, t, w, TABLE, 2026.0, nboot=400, rng=np.random.default_rng(3))
    b = G.fit(m, t, w, TABLE, 2026.0, nboot=400, rng=np.random.default_rng(3), cl=cl)
    # four copies of every event: the sd of the rate doubles
    assert 1.7 < np.std(b["rr"]) / np.std(a["rr"]) < 2.3


def test_dispersion_and_band():
    m, t, w, cl = catalogue(2, kids=2)
    f = G.fit(m, t, w, TABLE, 2026.0, cl=cl)
    assert abs(G.dispersion(f, 5.0) - 3.0) < 1e-9
    assert G.dispersion(dict(f, cl=None), 5.0) == 1.0
    lo, hi = G.band(10.0, 3.0)
    plo, phi = G.band(10.0, 1.0)
    assert lo <= plo and hi > phi


def test_predictive_band_holds_the_observed_points():
    """A catalogue drawn from a Gutenberg-Richter line: its own observed cumulative rates lie inside the 5-95 %
    predictive band of its fit at most magnitudes, and the band widens with clusters."""
    m, t, w, cl = catalogue(3, nmain=800)
    f = G.fit(m, t, w, TABLE, 2026.0, shape="gr", top=8.0, nboot=300, rng=np.random.default_rng(4))
    use, n = f["T"] > 0, f["cnt"]
    obs = np.cumsum((n / np.where(use, f["T"], 1))[::-1])[::-1]
    lo, hi = G.predictive(f)
    k = use & (obs > 0)
    assert ((obs[k] >= lo[k]) & (obs[k] <= hi[k])).mean() >= 0.8
    m, t, w, cl = catalogue(3, nmain=800, kids=2)
    g = G.fit(m, t, w, TABLE, 2026.0, shape="gr", top=8.0, nboot=300, rng=np.random.default_rng(4), cl=cl)
    h = dict(g, cl=None)
    lo2, hi2 = G.predictive(g)
    lo3, hi3 = G.predictive(h)
    j = use & (lo3 > 0)
    assert np.median((hi2 - lo2)[j] / (hi3 - lo3)[j]) > 1.15

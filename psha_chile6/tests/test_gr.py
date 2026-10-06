# Numerical tests of lib.gr: completeness lookups, Weichert fits, observed rates and the MFD shapes.

import numpy as np
import pandas as pd
import pytest

import synth
from lib import gr

NREP = 120


def fit_all(round_to=None, floor=synth.FLOOR, seed=1):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(NREP):
        w = gr.weichert(synth.simulate(rng, round_to), synth.STEPS, synth.TE, floor, 0.1)
        out.append((w["b"], w["rate"]))
    return np.array(out)


def test_since_and_complete():
    s = synth.STEPS
    assert gr.since(5.8, s) == 1976 and gr.since(6.0, s) == 1950 and gr.since(4.0, s) == 2016
    assert np.isnan(gr.since(3.9, s))
    assert gr.mc_of(6.3, s) == 6.0 and gr.mc_of(9.0, s) == 8.3
    df = pd.DataFrame({"mag": [5.9, 5.9, 6.0, 6.0, 3.0], "year": [1975, 1977, 1949, 1951, 2020]})
    assert gr.complete(df, s).tolist() == [False, True, False, True, False]


def test_weichert_unbiased_on_continuous_magnitudes():
    r = fit_all()
    assert abs(r[:, 0].mean() / synth.B - 1) < 0.01
    assert abs(r[:, 1].mean() / synth.LAM - 1) < 0.015


def test_weichert_floor_recovers_the_rate_at_any_floor():
    for fl in (5.6, 6.0, 6.4):
        r = fit_all(floor=fl, seed=2)
        truth = float(synth.n_true(fl))
        assert abs(r[:, 1].mean() / truth - 1) < 0.02, fl
        assert abs(r[:, 0].mean() / synth.B - 1) < 0.015, fl


def test_bootstrap_b_err_matches_spread_of_b():
    rng = np.random.default_rng(3)
    be = [gr.weichert(synth.simulate(rng), synth.STEPS, synth.TE, synth.FLOOR, 0.1, nboot=100)["b_err"] for _ in range(30)]
    assert 0.8 < np.mean(be) / fit_all()[:, 0].std() < 1.2


def test_weichert_fixed_b_returns_that_b_and_the_rate():
    rng = np.random.default_rng(4)
    r = [gr.weichert(synth.simulate(rng), synth.STEPS, synth.TE, synth.FLOOR, 0.1, b=synth.B) for _ in range(NREP)]
    assert all(abs(x["b"] - synth.B) < 1e-12 for x in r)
    assert abs(np.mean([x["rate"] for x in r]) / synth.LAM - 1) < 0.01


def test_weichert_needs_enough_events_and_a_covered_floor():
    assert np.isnan(gr.weichert(np.full(5, 6.0), synth.STEPS, synth.TE, 5.8, 0.1)["b"])
    with pytest.raises(ValueError):
        gr.weichert(np.full(50, 4.0) + np.linspace(0, 1, 50), [(5.0, 1980)], synth.TE, 4.0, 0.1)


def test_weichert_joint_pools_equal_b():
    rng = np.random.default_rng(5)
    g = [(synth.simulate(rng), synth.STEPS, synth.TE, synth.FLOOR) for _ in range(2)]
    assert abs(gr.weichert_joint(g, 0.1)["b"] / synth.B - 1) < 0.08


def test_recorded_labels_are_self_consistent():
    # rounded magnitudes, read as recorded values: the fit is N(recorded >= 5.8) = N(true >= 5.75)
    r = fit_all(0.1)
    assert abs(r[:, 1].mean() / float(synth.n_true(5.75)) - 1) < 0.02
    assert abs(r[:, 0].mean() / synth.B - 1) < 0.015


def test_obs_cum_is_unbiased_on_recorded_thresholds():
    rng = np.random.default_rng(6)
    for g in (6.5, 7.5):
        o = np.mean([float(gr.obs_cum(pd.DataFrame({"mag": synth.simulate(rng, 0.1)}), synth.STEPS, synth.TE, [g])[0]) for _ in range(NREP)])
        assert abs(o / float(synth.n_true(g - 0.05)) - 1) < 0.06, g


@pytest.mark.parametrize("form", ["tgr", "tapered"])
def test_cum_is_a_normalized_decreasing_distribution(form):
    m = np.linspace(6.5, 9.7, 321)
    n = gr.cum(form, 0.92, 6.5, 9.5, m, corner=9.6)
    assert abs(n[0] - 1) < 1e-12
    assert np.all(np.diff(n) <= 1e-12)
    assert n[m > gr.top(9.5) + 1e-9].max() == 0.0 and n[(m > 9.5) & (m < gr.top(9.5) - 1e-9)].min() > 0


def test_tapered_tends_to_truncated_gr_for_a_distant_corner():
    m = np.linspace(6.5, 9.5, 100)
    assert np.abs(gr.cum("tapered", 0.92, 6.5, 9.5, m, corner=60.0) - gr.cum("tgr", 0.92, 6.5, 9.5, m)).max() < 1e-10


def test_tapered_against_the_kagan_formula_written_out():
    b, mn, mx, mc = 0.92, 6.5, 9.5, 9.6
    m = np.array([7.0, 8.0, 9.0, 9.4])
    f = lambda x: (synth.m0(mn) / synth.m0(x)) ** (2 * b / 3) * np.exp((synth.m0(mn) - synth.m0(x)) / synth.m0(mc))
    top = mx + 2 * gr.HALF
    assert np.allclose(gr.cum("tapered", b, mn, mx, m, corner=mc), (f(m) - f(top)) / (1 - f(top)), rtol=1e-12)


@pytest.mark.parametrize("form", ["tgr", "tapered"])
def test_binned_moment_matches_mpr(form):
    inc, e = gr.inc(1.0, form, 0.92, 5.5, 9.5, 0.1, corner=9.6)
    mom = (inc * gr.m0(gr.mid(e, 0.1))).sum()
    assert abs(mom / gr.mpr(form, 0.92, 5.5, 9.5, corner=9.6) - 1) < 0.003


def test_inc_rates_sum_to_the_rate_and_end_at_the_top_bin():
    inc, e = gr.inc(0.8, "tgr", 0.92, 5.5, 9.5, 0.1)
    assert abs(inc.sum() - 0.8) < 1e-12
    assert abs(gr.mid(e, 0.1)[-1] - 9.5) < 1e-9 and abs(gr.mid(e, 0.1)[0] - 5.5) < 1e-9


def test_window_weights_follow_the_hiemer_form():
    df = pd.DataFrame({"mag": [5.0, 6.0, 6.1], "year": [1990.0, 1960.0, 1990.0]})
    keep, w = gr.window_weights(df, [(6.0, 1950), (5.0, 1980)], 1.0, 5.0, 2020.0)
    assert keep.tolist() == [True, True, True]
    assert np.allclose(w, [10 ** 0 / 40, 10 ** 1 / 30, 10 ** 0 / 40])

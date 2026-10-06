# Bin precision: the catalog magnitudes are the nearest 0.1, so a recorded value is the centre of
# its bin. Fit, MFD, NRML, read back, and compared with the true GR in true magnitude. With exact
# inputs the written rates must equal the truth; the edge convention (gr.HALF = 0) must be off by
# 10^(0.05 b), which is why the test exists.

import numpy as np

import synth
from lib import gr, nrml

NREP = 120


def written(lam, b):
    inc, e = gr.inc(lam, "tgr", b, synth.FLOOR, synth.MMAX, 0.1)
    return nrml.mfd_rates(nrml.mfd(inc, synth.FLOOR, 0.1))[:2]


def n_ge(c, r, x):
    """N(>=x) of the written sources: bins whose lower edge is at or above x."""
    return r[c - 0.05 >= x - 1e-6].sum()


def test_nrml_bins_sit_at_the_recorded_value():
    c, r, dm = nrml.mfd_rates(nrml.mfd([1.0, 0.5], 5.5, 0.1))
    assert np.allclose(c, [5.5, 5.6]) and dm == 0.1
    c, _, _ = nrml.mfd_rates(nrml.mfd([1.0, 0.5], 6.0, 0.1, 0.0))
    assert np.allclose(c, [6.05, 6.15])


def test_exact_inputs_give_exact_rates_in_true_magnitude():
    lam = float(synth.n_true(5.75))              # N(recorded >= 5.8) of a catalog with N(true >= 5.8) = LAM
    c, r = written(lam, synth.B)
    for x in (6.45, 7.45, 8.05, 8.75):
        assert abs(n_ge(c, r, x) / float(synth.n_true(x)) - 1) < 0.03, x


def test_edge_convention_overstates_by_ten_to_the_half_bin_b(monkeypatch):
    monkeypatch.setattr(gr, "HALF", 0.0)
    lam = float(synth.n_true(5.75))
    c, r = written(lam, synth.B)
    for x in (6.5, 7.5):
        assert abs(n_ge(c, r, x) / float(synth.n_true(x)) - 10 ** (0.05 * synth.B)) < 0.02, x


def chain(seed=1):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(NREP):
        w = gr.weichert(synth.simulate(rng, 0.1), synth.STEPS, synth.TE, synth.FLOOR, 0.1)
        out.append(written(w["rate"], w["b"]))
    return out


def test_fitted_sources_reproduce_the_true_rates():
    rows = chain()
    for x in (6.45, 7.45, 8.05, 8.75):
        assert abs(np.mean([n_ge(c, r, x) for c, r in rows]) / float(synth.n_true(x)) - 1) < 0.08, x


def test_fitted_sources_with_the_edge_convention_are_too_high(monkeypatch):
    monkeypatch.setattr(gr, "HALF", 0.0)
    rows = chain()
    for x in (6.5, 7.5):
        assert np.mean([n_ge(c, r, x) for c, r in rows]) / float(synth.n_true(x)) > 1.08, x


def test_mmax_bin_is_written_and_nothing_above_it():
    inc, e = gr.inc(1.0, "tgr", 0.92, 5.5, 9.5, 0.1)
    c, r, _ = nrml.mfd_rates(nrml.mfd(inc, 5.5, 0.1))
    assert abs(c[-1] - 9.5) < 1e-9 and r[-1] > 0

# The combination of family jobs: exact in rate space for the mean, exact enumeration for the
# fractiles, Monte Carlo as a fallback.

import itertools

import numpy as np

from hazard import combine

LV = np.logspace(-2, 0.5, 20)
Q = (0.05, 0.5, 0.95)


def fam(rng, nr, scale, ns=2):
    a = np.exp(rng.normal(0, 0.3, (ns, nr)))
    return 1 - np.exp(-scale * a[:, :, None, None] * (LV / 0.1) ** -2.0), (lambda w: w / w.sum())(rng.random(nr))


def joint(parts):
    sh = [len(p[1]) for p in parts]
    idx = list(itertools.product(*[range(n) for n in sh]))
    w = np.array([np.prod([parts[k][1][i] for k, i in enumerate(ix)]) for ix in idx])
    c = np.stack([1 - np.prod([1 - parts[k][0][:, i] for k, i in enumerate(ix)], axis=0) for ix in idx], axis=1)
    return c, w


def wq(c, w, q):
    o = np.argsort(c, axis=0)
    cs = np.cumsum(w[o], axis=0) - 0.5 * w[o]
    return np.array([[np.interp(q, cs[:, l], np.take_along_axis(c, o, 0)[:, l]) for l in range(c.shape[1])] for _ in [0]])[0].T


def test_mean_is_the_enumerated_mean():
    rng = np.random.default_rng(0)
    parts = [fam(rng, 5, 1e-3), fam(rng, 3, 5e-4), fam(rng, 4, 2e-4)]
    c, w = joint(parts)
    assert np.allclose(combine.mean(parts)[:, 0], np.einsum("r,srl->sl", w, c[:, :, 0]), rtol=1e-12)


def test_exact_quantiles_equal_the_weighted_quantiles_of_the_joint_tree():
    rng = np.random.default_rng(1)
    parts = [fam(rng, 5, 1e-3), fam(rng, 3, 5e-4), fam(rng, 4, 2e-4)]
    c, w = joint(parts)
    e = combine.exact(parts, Q)
    for s in range(2):
        for k, q in enumerate(Q):
            o = np.argsort(c[s, :, 0, :], axis=0)
            cs = np.cumsum(w[o], axis=0) - 0.5 * w[o]
            ref = [np.interp(q, cs[:, l], np.take_along_axis(c[s, :, 0, :], o, 0)[:, l]) for l in range(len(LV))]
            assert np.allclose(e[k, s, 0], ref, rtol=1e-10)


def test_monte_carlo_is_within_noise_of_exact():
    rng = np.random.default_rng(2)
    parts = [fam(rng, 20, 1e-3), fam(rng, 4, 5e-4), fam(rng, 12, 2e-4)]
    e, m = combine.exact(parts, Q), combine.fractiles(parts, Q, n=30000)
    ok = (combine.mean(parts) > 1e-4) & (combine.mean(parts) < 1e-2)
    assert np.abs(m[:, ok] / e[:, ok] - 1).max() < 0.03

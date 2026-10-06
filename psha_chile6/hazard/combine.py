# Combination of family jobs into the full model. The families share no
# logic-tree branch (source branches are per family, the GMM branch set is per
# tectonic region type), so their realizations are independent and
#   PoE_total = 1 - prod_f (1 - PoE_f)
# holds realization by realization. The mean follows exactly: mean PoE_total =
# 1 - prod_f (1 - mean PoE_f), i.e. the family mean rates -ln(1 - mean PoE_f) add.
# Fractiles are weighted quantiles over the joint realizations, which are all the
# combinations of one realization per family with the product of their weights:
# exact() enumerates them (18 432 for the current tree), fractiles() draws them at
# random when the product is too large.

import numpy as np

QUANTILES = (0.05, 0.16, 0.5, 0.84, 0.95)


def rate(p):
    return -np.log(1 - np.clip(np.asarray(p, float), 0, 1 - 1e-12))


def mean(parts):
    """Exact mean PoE curves (sites, imts, levels) of independent parts, each (curves, w)."""
    r = sum(rate(np.einsum("r,srml->sml", w / w.sum(), c)) for c, w in parts)
    return 1 - np.exp(-r)


def fractiles(parts, q=QUANTILES, n=10000, seed=0):
    """
    Weighted Monte Carlo fractiles of the combined PoE curves.

    Parameters
    ----------
    parts : list of (curves (sites, rlzs, imts, levels), weights (rlzs))
    q : quantiles
    n : draws; each draw picks one realization per part with its weight

    Returns
    -------
    array (len(q), sites, imts, levels)
    """
    rng = np.random.default_rng(seed)
    tot = np.zeros((n,) + parts[0][0].shape[:1] + parts[0][0].shape[2:])
    for c, w in parts:
        k = rng.choice(len(w), size=n, p=w / w.sum())
        tot += rate(c[:, k]).transpose(1, 0, 2, 3)
    return np.quantile(1 - np.exp(-tot), q, axis=0)


def exact(parts, q=QUANTILES, nmax=5e6):
    """
    Exact weighted quantiles over all combinations of one realization per part.

    Same quantile definition as hazard.post.wquant (cumulative weight minus half the
    weight, linear interpolation), so the result is what a job enumerating the joint
    tree would give from its realization curves.

    Parameters
    ----------
    parts : list of (curves (sites, rlzs, imts, levels), weights (rlzs))
    q : quantiles
    nmax : largest number of combinations accepted

    Returns
    -------
    array (len(q), sites, imts, levels)
    """
    n = int(np.prod([len(w) for _, w in parts]))
    if n > nmax:
        raise ValueError(f"{n} combinations; use fractiles()")
    k = len(parts)
    w = np.ones([1] * k)
    for i, (_, wi) in enumerate(parts):
        w = w * (wi / wi.sum()).reshape([len(wi) if j == i else 1 for j in range(k)])
    w = np.broadcast_to(w, [len(p[1]) for p in parts]).reshape(n)
    o = np.zeros((len(q),) + parts[0][0].shape[:1] + parts[0][0].shape[2:])
    for s in range(o.shape[1]):
        for m in range(o.shape[2]):
            t = 0
            for i, (c, _) in enumerate(parts):
                t = t + rate(c[s, :, m]).reshape([len(c[s]) if j == i else 1 for j in range(k)] + [-1])
            t = 1 - np.exp(-t.reshape(n, -1))
            r = np.argsort(t, axis=0)
            cs = np.cumsum(w[r], axis=0) - 0.5 * w[r]
            v = np.take_along_axis(t, r, axis=0)
            for l in range(t.shape[1]):
                o[:, s, m, l] = np.interp(q, cs[:, l], v[:, l])
    return o


def quantiles(parts, q=QUANTILES, nmax=5e6, **kw):
    """Exact when the product of realizations is at most nmax, else Monte Carlo (fractiles)."""
    return exact(parts, q, nmax) if np.prod([len(w) for _, w in parts]) <= nmax else fractiles(parts, q, **kw)


def convergence(parts, q=QUANTILES, ns=(1000, 3000, 10000, 30000), band=(1e-4, 1e-2)):
    """
    Monte Carlo noise of the fractiles: largest relative difference between two
    independent runs at each draw count, over the levels where the mean PoE of
    the combined model lies in band (the tails below are not reported).
    """
    ok = (mean(parts) > band[0]) & (mean(parts) < band[1])
    out = []
    for n in ns:
        a, b = fractiles(parts, q, n, 0), fractiles(parts, q, n, 1)
        out.append((n, float(np.max(np.abs(a[:, ok] / b[:, ok] - 1)))))
    return out

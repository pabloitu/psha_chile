"""Scores of the GMMs (task GM1, step 4): LLH (Scherbaum et al. 2009), LLH weights, EDR (Kale & Akkar 2013), event
bootstrap."""
import numpy as np
import pandas as pd
from scipy.stats import norm

DD = 0.01


def llh(obs, mu, sig):
    """LLH = −(1/N) Σ log2 g(x_i), g the normal density of the GMM at the observation (ln units)."""
    return -np.mean(norm.logpdf(obs, mu, sig)) / np.log(2)


def llh_weights(v):
    w = 2.0 ** (-np.asarray(v, float))
    return w / w.sum()


def mde(obs, mu, sig):
    """Modified Euclidean distance of each record (Kale & Akkar 2013): D = obs − model is normal with mean a − μ and
    σ; MDE_i = Σ_j |d_j| [P(|D| < |d_j| + dd/2) − P(|D| < |d_j| − dd/2)], bins of width dd up to max |μ_D ± 3σ_D|."""
    from scipy.special import ndtr
    md, s = np.asarray(obs - mu, float), np.asarray(sig, float)
    dmax = np.maximum(np.abs(md + 3 * s), np.abs(md - 3 * s))
    x = np.arange(0, dmax.max() + 2 * DD, DD)
    d = x[:-1] + DD / 2
    out = np.zeros(len(md))
    for a in range(0, len(md), 1000):
        m, ss, dm = md[a:a + 1000, None], s[a:a + 1000, None], dmax[a:a + 1000, None]
        F = ndtr((x - m) / ss) - ndtr((-x - m) / ss)
        out[a:a + 1000] = (d * np.diff(F, axis=1) * (d <= dm)).sum(1)
    return out


def kappa(obs, mu):
    """κ = DE_orig / DE_corr, the medians corrected by the straight line fitted between observed and predicted."""
    b1, b0 = np.polyfit(mu, obs, 1)
    return np.sqrt(((obs - mu) ** 2).sum() / ((obs - (b0 + b1 * mu)) ** 2).sum())


def edr(obs, mu, sig, m=None):
    """MDE (root mean square of the record MDE), κ and EDR = √(κ · mean MDE²)."""
    m = mde(obs, mu, sig) if m is None else m
    k = kappa(obs, mu)
    return np.sqrt(np.mean(m ** 2)), k, np.sqrt(k * np.mean(m ** 2))


def score(res, nboot=200, seed=1):
    """LLH, MDE, κ, EDR per GMM and intensity measure on the records of res, with the 16–84 % range of an event
    bootstrap and the share of resamples where each GMM ranks first (lowest LLH, lowest EDR)."""
    rng = np.random.default_rng(seed)
    rows, boots = [], []
    for imt, f in res.groupby("imt", sort=False):
        ev = np.unique(f.event_id)
        gm = list(dict.fromkeys(f.gmm))
        pre = {}
        for k in gm:
            g = f[f.gmm == k]
            m = g.mde.to_numpy() if "mde" in g else mde(g.obs.to_numpy(), g.mu.to_numpy(), g.sig.to_numpy())
            lp = -norm.logpdf(g.obs, g.mu, g.sig) / np.log(2)
            pre[k] = (g.event_id.to_numpy(), g.obs.to_numpy(), g.mu.to_numpy(), m, lp)
            M, K, E = edr(g.obs.to_numpy(), g.mu.to_numpy(), g.sig.to_numpy(), m)
            rows.append(dict(imt=imt, gmm=k, n_rec=len(g), n_ev=g.event_id.nunique(), llh=lp.mean(), mde=M,
                             kappa=K, edr=E))
        cnt = np.stack([np.bincount(rng.integers(0, len(ev), len(ev)), minlength=len(ev)) for _ in range(nboot)])
        B = np.zeros((nboot, len(gm), 2))
        for j, k in enumerate(gm):
            e, o, mu, m, lp = pre[k]
            W = cnt[:, np.searchsorted(ev, e)].astype(float)
            sw = W.sum(1)
            mean = lambda x: (W * x).sum(1) / sw
            mx, my = mean(mu), mean(o)
            b1 = mean((mu - mx[:, None]) * (o - my[:, None])) / mean((mu - mx[:, None]) ** 2)
            fit = my[:, None] + b1[:, None] * (mu - mx[:, None])
            kap = np.sqrt(mean((o - mu) ** 2) / mean((o - fit) ** 2))
            B[:, j] = np.c_[mean(lp), np.sqrt(kap * mean(m ** 2))]
        for j, k in enumerate(gm):
            boots.append(dict(imt=imt, gmm=k, llh_16=np.percentile(B[:, j, 0], 16),
                              llh_84=np.percentile(B[:, j, 0], 84), edr_16=np.percentile(B[:, j, 1], 16),
                              edr_84=np.percentile(B[:, j, 1], 84), first_llh=np.mean(B[:, :, 0].argmin(1) == j),
                              first_edr=np.mean(B[:, :, 1].argmin(1) == j)))
    t = pd.DataFrame(rows).merge(pd.DataFrame(boots), on=["imt", "gmm"])
    t["w_llh"] = t.groupby("imt").llh.transform(llh_weights)
    return t

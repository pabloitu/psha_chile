"""X5: clusters of nodal planes in the manner of ACE (Specht et al. 2017): a mixture of components, each a normal
distribution of strike and rake on the circle times a beta distribution of the dip, with one uniform component for
noise, fitted by expectation–maximisation. Left out from ACE: the merging and removal of components (the number is
chosen by BIC here) and the truncation along the rake. The strike is taken against the Slab2 strike. With DEPTH the
depth against the Slab2 surface is a further normal dimension of every component (not in ACE)."""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import betaln

import x5_lib as X
import x5_models as M

KS, NINIT, NIT, SEED = range(2, 9), 12, 300, 1
DLIM = (-45.0, 70.0)
wrap = lambda a: (a + 180) % 360 - 180


def data():
    c, g = X.load()
    k = M.subset(g) & g.em.notna().to_numpy()
    x, cc = g[k], c[k]
    P = np.concatenate([np.c_[wrap(cc[f"strike{i}"] - x.sstr), wrap(cc[f"rake{i}"]), cc[f"dip{i}"].clip(0.5, 89.5), x.d.clip(*DLIM)]
                        for i in (1, 2)]).astype(float)
    return x, P


def dens(P, th, depth):
    """Density of each nodal plane under one component th = (mean strike, mean rake, 2 x 2 covariance, beta a, b,
    mean and sd of depth)."""
    mu, S, a, b, dm, ds = th
    r = np.c_[wrap(P[:, 0] - mu[0]), wrap(P[:, 1] - mu[1])]
    Si = np.linalg.inv(S)
    f = np.exp(-0.5 * np.einsum("ni,ij,nj->n", r, Si, r)) / (2 * np.pi * np.sqrt(np.linalg.det(S)))
    u = P[:, 2] / 90
    f = f * np.exp((a - 1) * np.log(u) + (b - 1) * np.log1p(-u) - betaln(a, b)) / 90
    if depth:
        f = f * np.exp(-0.5 * ((P[:, 3] - dm) / ds) ** 2) / (ds * np.sqrt(2 * np.pi))
    return f


def fit(P, K, depth, rng):
    """EM for K components and noise. Returns (log-likelihood, weights, components, responsibilities (n, K + 1))."""
    n = len(P)
    f0 = 1 / (360 * 360 * 90) / ((DLIM[1] - DLIM[0]) if depth else 1)
    th = [(P[i, :2].copy(), np.eye(2) * 25.0 ** 2, 2.0, 2.0, P[i, 3], 10.0) for i in rng.choice(n, K, replace=False)]
    w, ll = np.full(K + 1, 1 / (K + 1)), -np.inf
    for _ in range(NIT):
        F = np.c_[[dens(P, t, depth) for t in th] + [np.full(n, f0)]].T * w
        new = np.log(F.sum(1)).sum()
        R = F / F.sum(1, keepdims=True)
        w = R.mean(0)
        for j in range(K):
            q = R[:, j] / max(R[:, j].sum(), 1e-9)
            mu = np.degrees(np.arctan2((q[:, None] * np.sin(np.radians(P[:, :2]))).sum(0), (q[:, None] * np.cos(np.radians(P[:, :2]))).sum(0)))
            r = np.c_[wrap(P[:, 0] - mu[0]), wrap(P[:, 1] - mu[1])]
            S = (q[:, None, None] * r[:, :, None] * r[:, None, :]).sum(0) + np.eye(2) * 4.0
            u = P[:, 2] / 90
            m, v = (q * u).sum(), max((q * u ** 2).sum() - (q * u).sum() ** 2, 1e-4)
            t = max(m * (1 - m) / v - 1, 0.5)
            dm = (q * P[:, 3]).sum()
            th[j] = (mu, S, m * t, (1 - m) * t, dm, max(np.sqrt((q * (P[:, 3] - dm) ** 2).sum()), 2.0))
        if abs(new - ll) < 1e-5 * abs(new):
            break
        ll = new
    return new, w, th, R


def best(P, depth):
    rng, rows, keep = np.random.default_rng(SEED), [], None
    for K in KS:
        r = max((fit(P, K, depth, rng) for _ in range(NINIT)), key=lambda q: q[0])
        bic = -2 * r[0] + (K * (9 if depth else 7) + K) * np.log(len(P))
        rows.append({"K": K, "loglik": r[0], "BIC": bic})
        if keep is None or bic < keep[0]:
            keep = (bic, K) + r
    return pd.DataFrame(rows), keep


def main():
    x, P = data()
    n = len(x)
    ins = (x.em <= 1).to_numpy()
    for depth in (False, True):
        tab, (bic, K, ll, w, th, R) = best(P, depth)
        tag = "with depth" if depth else "mechanism only"
        print(f"\n{tag}: BIC by K", dict(zip(tab.K, tab.BIC.round(0))), "-> K =", K)
        E = (R[:n] + R[n:]) / 2
        lab = E.argmax(1)
        rows = []
        for j in range(K + 1):
            q = lab == j
            t = th[j] if j < K else None
            rows.append({"cluster": j if j < K else "noise", "weight": w[j], "strike − slab": t[0][0] if t else np.nan, "rake": t[0][1] if t else np.nan,
                         "dip": 90 * t[2] / (t[2] + t[3]) if t else np.nan, "sd strike": np.sqrt(t[1][0, 0]) if t else np.nan,
                         "sd rake": np.sqrt(t[1][1, 1]) if t else np.nan, "depth − slab": t[4] if t and depth else np.nan,
                         "sd depth": t[5] if t and depth else np.nan, "events": q.sum(), "inside ellipse": (q & ins).sum(),
                         "median d": np.median(x.d[q]) if q.any() else np.nan, "within 15 km": (np.abs(x.d[q]) <= 15).mean() if q.any() else np.nan})
        T = pd.DataFrame(rows).round(2)
        print(T.to_string(index=False))
        T.to_csv(X.TAB / f"x5_ace_{'depth' if depth else 'mech'}.csv", index=False)
        pd.DataFrame(np.c_[E.round(4), lab], index=x.event_id, columns=[f"p{j}" for j in range(K)] + ["p_noise", "cluster"]).to_csv(
            X.TAB / f"x5_ace_{'depth' if depth else 'mech'}_events.csv")


if __name__ == "__main__":
    main()

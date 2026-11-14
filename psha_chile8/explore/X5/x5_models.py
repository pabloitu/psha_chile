"""X5: four ways to score interface / in-slab / crustal for events over the shallow slab with a measured depth, and
the checks that can be made with the data on disk. Run after x5_lib.load() (cached in g.pkl)."""
import numpy as np
import pandas as pd
from scipy.special import ndtr
from scipy.stats import norm

import x5_lib as X
from x5_lib import C

# CatSep (Haynie et al. 2026, Table 1): flex zone, seismogenic depth ramp, Kagan ramp, crustal ramp; Moho fixed here
FLEX, SZ, SZ_MAX, KAG, KAG_P, DIFF, MOHO = 15.0, 50.0, 65.0, (30.0, 53.0), (1.0, 0.25), (-20.0, 20.0), 40.0
KBINS = [30.0, 53.0]
NQ = 61
# what a thrust-like mechanism (Kagan angle up to 30°) is worth for the interface odds: among events with calibrated or
# depth-phase depths, its share within 5 km of the slab surface (0.75) over its share beyond 15 km (0.23)
LR = 3.3
# the same for a mechanism inside the ellipse (skewed measure up to 1): 0.74 over 0.19
LR_F = 3.9
# soft edge of the ellipse: full weight up to 1, none from EDGE
EDGE = 1.5


def ramp(x, x1, x2, p1, p2):
    return np.where(x < x1, p1, np.where(x > x2, p2, p1 + (p2 - p1) * (x - x1) / (x2 - x1)))


def catsep(z, top, kag, use_mech=True, pk=None):
    """Scores of Haynie et al. (2026) for depth z over a slab top: interface, in-slab, crustal. The Moho is a constant
    (their CRUST1.0 grid is not on disk) and the ramp below the Moho towards the flex zone is left out."""
    d = z - top
    if pk is None:
        pk = np.where(np.isfinite(kag) & use_mech, ramp(kag, *KAG, *KAG_P), 1.0)
    pif = (np.abs(d) <= FLEX) * ramp(z, SZ, SZ_MAX, 1.0, 0.0) * pk
    pcr = (1 - pif) * ramp(d, *DIFF, 1.0, 0.0) * ramp(z, MOHO, np.maximum(top, MOHO + 1e-6), 1.0, 0.0)
    return np.c_[pif, 1 - pif - pcr, pcr]


def catsep_err(z, sig, top, kag, use_mech=True, pk=None):
    """The same scores averaged over the depth error of the event (normal, cut at the ground), as the paper does over
    a depth distribution for events with a default depth."""
    q = (np.arange(NQ) + 0.5) / NQ
    lo = ndtr(-z / sig)
    out = np.zeros((len(z), 3))
    for u in q:
        out += catsep(z + sig * norm.ppf(lo + u * (1 - lo)), top, kag, use_mech, pk)
    return out / NQ


def raise_odds(P, k, lr):
    """Interface odds of the rows k multiplied by lr; in-slab and crustal keep their ratio."""
    pif = np.where(k, P[:, 0] * lr / (P[:, 0] * lr + 1 - P[:, 0]), P[:, 0])
    rest = P[:, 1:] / np.maximum(P[:, 1:].sum(1, keepdims=True), 1e-12)
    return np.c_[pif, (1 - pif)[:, None] * rest]


class Mixture:
    """
    Three classes as normal distributions of d = depth − slab top, with a mechanism bin (Kagan angle up to 30°, to 53°,
    beyond) where there is a mechanism. Fitted by expectation–maximisation without labels. The interface width is
    fitted per depth quality (best, other): it is the combined error of event depth and slab depth as the data show
    it. The class shares are fitted apart for events with and without a mechanism.
    """

    def fit(self, d, best, kb, n_iter=300):
        self.mu, self.s = np.array([2.0, 15.0, -15.0]), np.array([[7.0, 12.0, 10.0], [9.0, 12.0, 10.0]])
        self.a = np.array([[0.8, 0.15, 0.05], [0.2, 0.4, 0.4], [0.2, 0.4, 0.4]])
        self.pi = np.array([[0.6, 0.25, 0.15], [0.6, 0.25, 0.15]])
        hm = kb >= 0
        for _ in range(n_iter):
            r = self.post(d, best, kb)
            for j in (0, 1):
                self.pi[j] = r[hm == bool(1 - j)].mean(0)
            w = r.sum(0)
            self.mu = (r * d[:, None]).sum(0) / w
            self.mu[1], self.mu[2] = max(self.mu[1], 5.0), min(self.mu[2], -5.0)
            for b in (0, 1):
                k = best == bool(1 - b)
                self.s[b] = np.sqrt((r[k] * (d[k, None] - self.mu) ** 2).sum(0) / r[k].sum(0))
            self.s[:, 1:] = np.sqrt((r[:, 1:] * (d[:, None] - self.mu[1:]) ** 2).sum(0) / w[1:])
            for c in range(3):
                self.a[c] = [(r[hm & (kb == q), c]).sum() for q in range(3)]
                self.a[c] /= self.a[c].sum()
        return self

    def post(self, d, best, kb, use_mech=True, pi=None):
        s = self.s[np.where(best, 0, 1)]
        hm = (kb >= 0) & use_mech
        p = (self.pi[np.where(kb >= 0, 0, 1)] if pi is None else pi) * norm.pdf(d[:, None], self.mu, s)
        p = p * np.where(hm[:, None], self.a[:, np.clip(kb, 0, 2)].T, 1.0)
        return p / p.sum(1, keepdims=True)


def subset(g):
    return X.m45(g) & g.known.to_numpy() & ~g.sea.to_numpy() & ~g.an.to_numpy() & (g.top <= C.IF_TOP).to_numpy()


def scores(g, use_mech=True):
    """Interface, in-slab and crustal scores of the four models for the events of subset(g): dict name -> (n, 3)."""
    k = subset(g)
    x = g[k]
    z, sig, top, kag, d = (x[c].to_numpy(float) for c in ("z", "sig", "top", "kag", "d"))
    best, kb = x.depth_src.isin(X.BEST).to_numpy(), np.where(np.isfinite(kag), np.digitize(kag, KBINS), -1)
    out = {}
    o = C.classify(g, hard=0.8, mech="add" if use_mech else "none")[0][k]
    auto = o[["a_interface", "a_inslab", "a_crustal"]].to_numpy()
    out["A run j: thrust decides alone"] = auto
    o = C.classify(g, hard=0.8, mech="exclude" if use_mech else "none")[0][k]
    out["A2 run j rules, mechanism only excludes"] = o[["a_interface", "a_inslab", "a_crustal"]].to_numpy()
    out["B USGS CatSep"] = catsep(z, top, kag, use_mech)
    out["C CatSep with the event depth error"] = catsep_err(z, sig, top, kag, use_mech)
    # E: C, and a thrust-like mechanism multiplies the interface odds (the taper the paper names as future work)
    P = out["C CatSep with the event depth error"].copy()
    if use_mech:
        t = kb == 0
        pif = np.where(t, P[:, 0] * LR / (P[:, 0] * LR + 1 - P[:, 0]), P[:, 0])
        rest = P[:, 1:] / np.maximum(P[:, 1:].sum(1, keepdims=True), 1e-12)
        P = np.c_[pif, (1 - pif)[:, None] * rest]
    out["E as C, thrust-like mechanism raises the odds"] = P
    # F: interface mechanism by the ellipse of swing and twist; outside it interface is 0, inside the odds are raised
    em = x.em.to_numpy(float)
    ok = np.isfinite(em) & (em <= 1)
    pk = np.where(np.isfinite(em) & (em > 1) & use_mech, 0.0, 1.0)
    P = catsep_err(z, sig, top, kag, use_mech, pk)
    out["F0 depth error, ellipse only excludes"] = P
    out["F depth error, ellipse excludes and raises"] = raise_odds(P, ok, LR_F) if use_mech else P
    pk = np.where(np.isfinite(em) & use_mech, np.clip((EDGE - em) / (EDGE - 1), 0, 1), 1.0)
    P = catsep_err(z, sig, top, kag, use_mech, pk)
    out["F1 as F, soft edge"] = raise_odds(P, ok, LR_F) if use_mech else P
    # G: F1 as it stands in catalog/classify.py, where a weight of 0.8 or more becomes 1
    P = out["F1 as F, soft edge"]
    out["G as F1, weight of 0.8 or more becomes 1"] = np.where((P.max(1) >= 0.8)[:, None], np.eye(3)[P.argmax(1)], P)
    m = Mixture().fit(d, best, kb)
    out["D fitted mixture"] = m.post(d, best, kb, use_mech, pi=None if use_mech else m.pi[0])
    return x, out, m

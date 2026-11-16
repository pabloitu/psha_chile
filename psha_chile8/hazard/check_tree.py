# Does running the families separately equal one joint logic tree? Level 1 (ported from psha_chile7
# hazard/check_tree.py, two families): the joint job c_all_small against the family jobs c_if_small and c_is_small,
# which it enumerates completely. With P_f(phi_f) the curve of family f for one of its realizations phi_f, the joint
# realization (phi_I, phi_S) must be
#   P = 1 - prod_f (1 - P_f(phi_f))      and      W = prod_f W_f(phi_f).
# Four views, so that a failure says what failed:
#   mean      joint mean against 1 - prod(1 - mean_f)
#   paired    each joint curve against the product of the family curves with the same branches
#   partner   each joint curve against all products: if every one has an exact partner the set of curves is right and
#             only the pairing (labels) is wrong
#   quantiles PGA at fixed PoE of the weighted 5 / 50 / 95 % curves, joint against combine.exact
# The interface realizations carry their scaling branch (msr_*), which belongs to the interface family.
# Output: hazard/out/check_tree.txt

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from hazard import combine, post
from hazard import config as hc

JOINT = "c_all_small"
FAM = [("c_if_small", ("if_", "msr_"), "Subduction Interface"), ("c_is_small", ("is_",), "Subduction IntraSlab")]
IMT = "PGA"
POES = (0.1, 0.02, 0.002105, 0.000404, 1e-4)
Q = (0.05, 0.5, 0.95)
BANDS = [(1e-2, 1.0), (1e-4, 1e-2), (1e-6, 1e-4)]
LO = 1e-6
TOL = {"mean": 1e-4, "paired": 1e-3, "partner": 1e-3, "quantiles": 1e-3}


def imls(c, lv, p):
    flat = c.reshape(-1, c.shape[-1])
    return np.array([post.iml(x, lv, p) for x in flat]).reshape(c.shape[:-1])


def key(src, gmm, pre, trt):
    return tuple(b for b in src if b.startswith(pre)), gmm[trt]


def level1(out):
    j = post.load(JOINT)
    m = list(j["imtls"]).index(IMT)
    lv, pj = j["imtls"][IMT], j["curves"][:, :, m, :]
    S, N, L = pj.shape
    fams = []
    for job, pre, trt in FAM:
        r = post.load(job)
        mi = list(r["imtls"]).index(IMT)
        fams.append((r, r["curves"][:, :, mi, :], pre, trt))
    sizes = [f[1].shape[1] for f in fams]
    out.append(f"joint realizations {N}; family parts {sizes}; sites {S}")
    rt = [combine.rate(f[1]) for f in fams]
    allp = 1 - np.exp(-(rt[0][:, :, None, :] + rt[1][:, None, :, :])).reshape(S, -1, L)
    idx = []
    for r, _, pre, trt in fams:
        d = {key(s, g, pre, trt): i for i, (s, g) in enumerate(zip(r["src"], r["gmm"]))}
        idx.append(np.array([d[key(s, g, pre, trt)] for s, g in zip(j["src"], j["gmm"])]))
    n = idx[0] * sizes[1] + idx[1]
    res = {}

    mj = np.einsum("r,srl->sl", j["w"], pj)
    mp = 1 - np.exp(-sum(combine.rate(np.einsum("r,srl->sl", f[0]["w"], f[1])) for f in fams))
    ok = mj > LO
    res["mean"] = float(np.abs(mp[ok] / mj[ok] - 1).max())
    out.append(f"mean: joint against 1 - prod(1 - mean_f), PoE > {LO:g}: max relative difference {res['mean']:.2e}")
    wp = fams[0][0]["w"][idx[0]] * fams[1][0]["w"][idx[1]]
    out.append(f"weights: joint against the product of the family weights: max relative difference "
               f"{np.abs(wp / j['w'] - 1).max():.2e}")
    res["weights"] = float(np.abs(wp / j["w"] - 1).max())

    pp = allp[:, n, :]
    d = np.abs(pp / np.where(pj > 0, pj, np.nan) - 1)
    worst = 0.0
    for lo, hi in BANDS:
        k = (pj > lo) & (pj <= hi)
        v = d[k]
        if not len(v):
            continue
        out.append(f"paired, PoE {lo:g}-{hi:g}: n {k.sum()}, median {np.median(v):.1e}, 99 % {np.quantile(v, 0.99):.1e}, "
                   f"max {v.max():.1e}")
        if lo >= 1e-4:
            worst = max(worst, float(v.max()))
    res["paired"] = worst

    lj, la = np.log(np.where(pj > 0, pj, 1.0)), np.log(np.where(allp > 0, allp, 1.0))
    best, hit = [], 0
    for a in range(N):
        msk = (pj[:, a, :] > LO) & (pj[:, a, :] < 1 - 1e-6)
        dist = np.where(msk[:, None, :], np.abs(la - lj[:, a, :][:, None, :]), 0).max(axis=(0, 2))
        best.append(dist.min())
        hit += int(dist.argmin() == n[a])
    res["partner"] = float(np.max(best))
    out.append(f"partner: every joint curve has a product within max |ln ratio| {res['partner']:.2e}; "
               f"best partner is the paired one for {hit} of {N} realizations")

    parts = [(f[1][:, :, None, :], f[0]["w"]) for f in fams]
    ex = combine.exact(parts, Q)
    wq = np.array([post.wquant(pj[s], j["w"], Q) for s in range(S)]).transpose(1, 0, 2)
    rows = []
    for p in POES:
        for qi in range(len(Q)):
            ie, ij = imls(ex[qi, :, 0, :], lv, p), imls(wq[qi], lv, p)
            rows.append(np.nanmax(np.abs(ij / ie - 1)))
    res["quantiles"] = float(np.nanmax(rows))
    out.append(f"quantiles 5/50/95 %: PGA at PoE {POES}: max relative difference joint against exact {res['quantiles']:.2e}")
    return res


def main():
    out = []
    res = level1(out)
    tol = {**TOL, "weights": 1e-6}
    bad = {k: v for k, v in res.items() if v > tol[k]}
    out.append("LEVEL 1: " + ("PASS" if not bad else f"FAIL {bad}") + f" (tolerances {tol})")
    hc.OUT.mkdir(parents=True, exist_ok=True)
    (hc.OUT / "check_tree.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))
    return res, bad


if __name__ == "__main__":
    main()

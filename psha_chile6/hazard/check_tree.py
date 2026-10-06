# Does running the families separately equal one joint logic tree? Level 1 (PRELIM=1, small tree):
# the joint job c_all_small against the family jobs c_if_small, c_is_final, c_cr_small, which it
# enumerates completely. With P_f(phi_f) the curve of family f for one of its realizations phi_f,
# the joint realization (phi_I, phi_S, phi_C) must be
#   P = 1 - prod_f (1 - P_f(phi_f))      and      W = prod_f W_f(phi_f).
# Four views, so that a failure says what failed:
#   mean      joint mean against 1 - prod(1 - mean_f)
#   paired    each joint curve against the product of the family curves with the same branches
#   partner   each joint curve against ALL 256 products: if every one has an exact partner the set of
#             curves is right and only the pairing (labels) is wrong
#   quantiles PGA at fixed PoE of the weighted 5 / 50 / 95 % curves, joint against combine.exact
# Level 2 (optional): the sampled joint job c_all_final_sample against the exact quantiles of the
# full-size family jobs c_if_final, c_is_final, c_cr_final, if all are present in the same tree.
# Output: outputs/hazard/rock800_<tree>/_prelim/check_tree.txt. Run: PRELIM=1 python hazard/check_tree.py
# (SMOKE=1 PRELIM=1 for the smoke tree)

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from hazard import config as hc
from hazard import combine, post

JOINT = "c_all_small"
FAM = [("c_if_small", "if", "gmm:sinter"), ("c_is_final", "is", "gmm:sslab"), ("c_cr_small", "cr", "gmm:asc")]
FULL = [("c_if_final", "interface"), ("c_is_final", "in-slab"), ("c_cr_final", "crustal")]
SAMPLED = "c_all_final_sample"
IMT = "PGA"
POES = (0.1, 0.02, 0.002105, 0.000404, 1e-4)
Q = (0.05, 0.5, 0.95)
BANDS = [(1e-2, 1.0), (1e-4, 1e-2), (1e-6, 1e-4)]
LO = 1e-6
TOL = {"mean": 1e-4, "paired": 1e-3, "partner": 1e-3, "quantiles": 1e-3}
TOL2 = {"mean": 3.0, "quantiles": 8.0}


def imls(c, lv, p):
    """PGA at probability p of every curve in c (..., levels), NaN outside the curve."""
    flat = c.reshape(-1, c.shape[-1])
    return np.array([post.iml(x, lv, p) for x in flat]).reshape(c.shape[:-1])


def level1(out):
    j = post.load(JOINT)
    m = list(j["imtls"]).index(IMT)
    lv, pj = j["imtls"][IMT], j["curves"][:, :, m, :].astype(float)
    S, N, L = pj.shape
    fams = []
    for job, pre, gcol in FAM:
        r = post.load(job)
        mi = list(r["imtls"]).index(IMT)
        fams.append((r, r["curves"][:, :, mi, :].astype(float), pre, gcol))
    sizes = [len(f[1][0]) for f in fams]
    out.append(f"joint realizations {N}; family parts {sizes}; sites {S}")
    rt = [combine.rate(f[1]) for f in fams]
    allp = 1 - np.exp(-(rt[0][:, :, None, None, :] + rt[1][:, None, :, None, :] + rt[2][:, None, None, :, :])).reshape(S, -1, L)
    key = []
    for r, c, pre, gcol in fams:
        idx = {(s, g): i for i, (s, g) in enumerate(zip(r["src"], r["axes"][gcol]))}
        key.append(np.array([idx[(next(p for p in s.split("_x_") if p.startswith(pre + "-")), g)]
                             for s, g in zip(j["src"], j["axes"][gcol])]))
    n = (key[0] * sizes[1] + key[1]) * sizes[2] + key[2]
    res = {}

    mj = np.einsum("r,srl->sl", j["w"], pj)
    mp = 1 - np.exp(-sum(combine.rate(np.einsum("r,srl->sl", f[0]["w"], f[1])) for f in fams))
    ok = mj > LO
    res["mean"] = float(np.abs(mp[ok] / mj[ok] - 1).max())
    out.append(f"mean: joint against 1 - prod(1 - mean_f), levels with PoE > {LO:g}: max relative difference {res['mean']:.2e}")

    pp = allp[:, n, :]
    d = np.abs(pp / np.where(pj > 0, pj, np.nan) - 1)
    worst = 0.0
    for lo, hi in BANDS:
        k = (pj > lo) & (pj <= hi)
        v = d[k]
        out.append(f"paired, PoE {lo:g}-{hi:g}: n {k.sum()}, median {np.median(v):.1e}, 99 % {np.quantile(v, 0.99):.1e}, max {v.max():.1e}")
        if lo >= 1e-4:
            worst = max(worst, float(v.max()))
    res["paired"] = worst
    k = (pj > 1e-4) & (pj < 1 - 1e-6)
    dd = np.where(k, d, 0).reshape(-1)
    for i in np.argsort(dd)[::-1][:3]:
        s, a, l = np.unravel_index(i, d.shape)
        out.append(f"  worst paired: site {j['names'][s]}, rlz {a} ({j['src'][a].split('_x_')[0]} ... {[f[0]['axes'][f[3]].iloc[key[q][a]] for q, f in enumerate(fams)]}), "
                   f"PGA {lv[l]:.3g} g: joint {pj[s, a, l]:.4e}, product {pp[s, a, l]:.4e}")

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
    worst = 0.0
    for qi, q in enumerate(Q):
        ie, ij = imls(ex[qi, :, 0, :], lv, POES[2]), imls(wq[qi], lv, POES[2])
        worst = max(worst, float(np.nanmax(np.abs(ij / ie - 1))))
    rows = []
    for p in POES:
        for qi in range(len(Q)):
            ie, ij = imls(ex[qi, :, 0, :], lv, p), imls(wq[qi], lv, p)
            rows.append(np.nanmax(np.abs(ij / ie - 1)))
    res["quantiles"] = float(np.nanmax(rows))
    out.append(f"quantiles 5/50/95 %: PGA at PoE {POES}: max relative difference joint against exact {res['quantiles']:.2e}")
    return res


def level2(out):
    miss = [j for j in [x[0] for x in FULL] + [SAMPLED] if not (hc.OUT_ROOT / j / "build.json").exists()]
    if miss:
        out.append(f"level 2 skipped: jobs not built in this tree: {miss} (LEVEL2=1 bash hazard/run_all.sh builds and runs them)")
        return {}
    try:
        full = [post.load(job) for job, _ in FULL]
        s = post.load(SAMPLED)
    except SystemExit as e:
        out.append(f"level 2 skipped: {e}")
        return {}
    if any(r["names"] != s["names"] for r in full):
        out.append("level 2 skipped: the jobs list the sites in a different order")
        return {}
    m = list(s["imtls"]).index(IMT)
    lv = s["imtls"][IMT]
    mis = [list(r["imtls"]).index(IMT) for r in full]
    parts = [(r["curves"][:, :, [mi], :].astype(float), r["w"]) for r, mi in zip(full, mis)]
    ex = combine.exact(parts, Q)
    cj = s["curves"][:, :, m, :].astype(float)
    wq = np.array([post.wquant(cj[i], s["w"], Q) for i in range(cj.shape[0])]).transpose(1, 0, 2)
    mj = np.einsum("r,srl->sl", s["w"], cj)
    me = combine.mean(parts)[:, 0, :]
    mf = [np.einsum("r,srl->sl", r["w"], r["curves"][:, :, mi, :].astype(float)) for r, mi in zip(full, mis)]
    p = POES[2]
    xe, xm = imls(me, lv, p), imls(mj, lv, p)
    xq = [(imls(ex[i, :, 0, :], lv, p), imls(wq[i], lv, p)) for i in range(len(Q))]
    out.append(f"level 2: sampled joint job ({len(s['w'])} samples) against the exact combination of the full-size family jobs, "
               f"PGA at PoE {p:g} (sampling noise only expected)")
    out.append(f"  {'site':18s} {'PGA mean g':>10s} {'mean':>7s} {'q5':>7s} {'q50':>7s} {'q95':>7s}   share interface / in-slab / crustal (%)")
    worst = {"mean": 0.0, "quantiles": 0.0}
    for i, name in enumerate(s["names"]):
        if not np.isfinite(xe[i]):
            out.append(f"  {name:18s} {'curve does not reach the PoE':>10s}")
            continue
        rt = [combine.rate(np.exp(np.interp(np.log(xe[i]), np.log(lv), np.log(np.maximum(f[i], 1e-300))))) for f in mf]
        sh = 100 * np.array(rt) / np.sum(rt)
        dq = [100 * (b[i] / a[i] - 1) for a, b in xq]
        dm = 100 * (xm[i] / xe[i] - 1)
        worst["mean"] = max(worst["mean"], abs(dm))
        worst["quantiles"] = max(worst["quantiles"], max(abs(x) for x in dq))
        out.append(f"  {name:18s} {xe[i]:10.4f} {dm:+6.1f}% {dq[0]:+6.1f}% {dq[1]:+6.1f}% {dq[2]:+6.1f}%   {sh[0]:5.1f} / {sh[1]:5.1f} / {sh[2]:5.1f}")
    bad = {k: round(v, 1) for k, v in worst.items() if v > TOL2[k]}
    out.append("LEVEL 2: " + ("PASS" if not bad else f"FAIL (percent, beyond sampling noise) {bad}") + f" (tolerances {TOL2} %)")
    return worst


def main():
    out = []
    res = level1(out)
    bad = {k: v for k, v in res.items() if v > TOL[k]}
    out.append("LEVEL 1: " + ("PASS" if not bad else f"FAIL {bad}") + f" (tolerances {TOL})")
    d = hc.OUT_ROOT / "_prelim"
    d.mkdir(parents=True, exist_ok=True)
    (d / "check_tree.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))
    n = len(out)
    level2(out)
    (d / "check_tree.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out[n:]))


if __name__ == "__main__":
    main()

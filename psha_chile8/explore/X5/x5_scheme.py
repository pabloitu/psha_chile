"""X5: schematic figure of method E at one epicentre, drawn with the functions of x5_models."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import x5_models as M
from x5_lib import ROOT

import sys
sys.path.insert(0, str(ROOT))
from palette import CLASS_COLOR  # noqa: E402

TOP, SIG = 30.0, 10.0
# depth, sigma, Kagan angle (nan = no mechanism), label
EV = [(32, 5, 10, "thrust-like"), (32, 15, np.nan, "no mechanism"), (32, 10, 80, "other mechanism"),
      (50, 10, 10, "thrust-like"), (10, 10, np.nan, "no mechanism")]
COL = [CLASS_COLOR[k] for k in ("interface", "intraslab_shallow", "forearc")]
OUT = Path(__file__).parent / "figs" / "scheme_E.png"


def method_e(z, sig, top, kag):
    """Interface, in-slab and crustal scores of method E."""
    z, sig, top, kag = (np.atleast_1d(np.asarray(v, float)) for v in (z, sig, top, kag))
    P = M.catsep_err(z, sig, top, kag)
    t = np.isfinite(kag) & (kag <= M.KAG[0])
    pif = np.where(t, P[:, 0] * M.LR / (P[:, 0] * M.LR + 1 - P[:, 0]), P[:, 0])
    rest = P[:, 1:] / np.maximum(P[:, 1:].sum(1, keepdims=True), 1e-12)
    return np.c_[pif, (1 - pif)[:, None] * rest]


def main():
    plt.rcParams.update({"font.family": "Ubuntu", "font.size": 11})
    f, ax = plt.subplots(1, 4, figsize=(17, 6.2), gridspec_kw={"width_ratios": [1.0, 1.25, 1.0, 1.45]})
    z = np.linspace(0, 80, 321)
    o = np.ones_like(z)

    # column under one epicentre
    a = ax[0]
    a.axhspan(0, TOP - M.FLEX, color=COL[2], alpha=0.18, lw=0)
    a.axhspan(TOP - M.FLEX, TOP + M.FLEX, color=COL[0], alpha=0.18, lw=0)
    a.axhspan(TOP + M.FLEX, 80, color=COL[1], alpha=0.18, lw=0)
    a.axhline(TOP, color="k", lw=2)
    a.text(0.25, TOP - 1, "Slab2 surface", fontsize=10, va="bottom")
    a.text(0.25, 4, "crust", color="#8a6000", fontsize=10, va="center")
    a.text(0.25, TOP + 12.5, "interface zone\n± 15 km", color=COL[0], fontsize=10, va="center")
    a.text(0.25, 70, "slab", color=COL[1], fontsize=10, va="center")
    for i, (zz, s, k, lab) in enumerate(EV):
        a.errorbar(i + 2.4, zz, yerr=[[min(s, zz)], [s]], fmt="o", color="k", ms=7, capsize=4, lw=1.3)
        a.text(i + 2.4, max(zz - s, 0) - 2, str(i + 1), ha="center", va="bottom", fontweight="bold")
    a.set(xlim=(0, 7.2), ylim=(80, -6), xticks=[], ylabel="Depth (km)", title="1. Event depth ± its error")

    # interface score against depth
    a = ax[1]
    a.plot(M.catsep(z, TOP * o, np.nan * o)[:, 0], z, color="0.45", ls="--", lw=1.5, label="USGS: depth taken as exact")
    a.plot(M.catsep_err(z, SIG * o, TOP * o, np.nan * o)[:, 0], z, color=COL[0], lw=2,
           label="averaged over the depth error\n(no mechanism)")
    a.plot(method_e(z, SIG * o, TOP * o, 10 * o)[:, 0], z, color="#08306b", lw=3, label="thrust-like mechanism: odds × 3.3")
    a.plot(method_e(z, SIG * o, TOP * o, 80 * o)[:, 0], z, color="#9ecae1", lw=2, label="other mechanism: × 0.25")
    a.axhline(TOP, color="k", lw=1)
    a.set(xlim=(0, 1.02), ylim=(80, -6), xlabel="Interface score", yticklabels=[],
          title=f"2. Score by depth (σ = {SIG:.0f} km)")
    a.legend(loc="lower right", fontsize=9, frameon=False)

    # what the factor does
    a = ax[2]
    p = np.linspace(0, 1, 101)
    a.plot(p, p, color=COL[0], lw=2, label="no change")
    a.plot(p, p * M.LR / (p * M.LR + 1 - p), color="#08306b", lw=3, label="thrust-like")
    for p0 in (0.1, 0.5, 0.9):
        p1 = p0 * M.LR / (p0 * M.LR + 1 - p0)
        a.annotate("", (p0, p1), (p0, p0), arrowprops=dict(arrowstyle="->", color="0.3"))
        a.text(min(p0 + 0.03, 0.72), (p0 + p1) / 2 - 0.02 - 0.1 * (p0 > 0.8), f"{p0:.1f} to {p1:.2f}", fontsize=9)
    a.set(xlim=(0, 1), ylim=(0, 1.02), xlabel="Score from depth alone", ylabel="Score with a thrust-like mechanism",
          title="3. A thrust raises, never decides")
    a.legend(loc="lower right", fontsize=9, frameon=False)

    # the example events
    a = ax[3]
    zz, s, k = (np.array([e[j] for e in EV], float) for j in range(3))
    P = method_e(zz, s, TOP * np.ones(len(EV)), k)
    y = np.arange(len(EV))
    left = np.zeros(len(EV))
    for j, n in enumerate(("interface", "in-slab", "crustal")):
        a.barh(y, P[:, j], left=left, color=COL[j], label=n, height=0.6)
        for i in y:
            if P[i, j] >= 0.08:
                a.text(left[i] + P[i, j] / 2, i, f"{P[i, j]:.2f}", ha="center", va="center", color="w", fontsize=10)
        left += P[:, j]
    a.set_yticks(y, [f"{i + 1}  {e[0]} ± {e[1]} km\n{e[3]}" for i, e in enumerate(EV)], fontsize=9.5)
    a.set(xlim=(0, 1), ylim=(len(EV) - 0.5, -0.9), xlabel="Class weights (add to 1)", title="4. Result for the five events")
    a.legend(loc="upper center", ncol=3, fontsize=9, frameon=False, bbox_to_anchor=(0.5, 1.0))

    f.suptitle(f"Method E at one epicentre, Slab2 surface at {TOP:.0f} km", fontsize=14, y=0.99)
    f.tight_layout(rect=(0, 0, 1, 0.96))
    OUT.parent.mkdir(exist_ok=True)
    f.savefig(OUT, dpi=160)
    print(np.round(P, 2))


if __name__ == "__main__":
    main()

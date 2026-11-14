"""X5: spread of our mechanisms about the interface mechanism, as swing and twist and as the measure m."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import x5_lib as X
import x5_models as M

sys.path.insert(0, str(X.ROOT))
from palette import CLASS_COLOR  # noqa: E402

TOL, EDGE, NEAR = X.C.TOL, 1.5, 10.0
OUT = Path(__file__).parent / "figs" / "spread.png"


def main():
    c, g = X.load()
    x = g[M.subset(g) & g.em.notna().to_numpy()]
    m, sw, tw, d = (x[q].to_numpy(float) for q in ("em", "sw", "tw", "d"))
    near = np.abs(d) <= NEAR
    col = (CLASS_COLOR["interface"], CLASS_COLOR["intraslab_shallow"])
    lab = (f"within {NEAR:.0f} km of the slab surface", "farther from it")
    plt.rcParams.update({"font.family": "Ubuntu", "font.size": 11})
    f, ax = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1.1, 1.0]})

    a = ax[0]
    for q, cl, lb in ((~near, col[1], lab[1]), (near, col[0], lab[0])):
        a.scatter(sw[q], tw[q], s=14, color=cl, alpha=0.6, lw=0, label=f"{lb} ({q.sum()})")
    e = np.linspace(0, np.pi / 2, 100)
    a.plot(TOL[0] * np.cos(e), TOL[1] * np.sin(e), color="k", lw=2.2, label="m = 1")
    a.plot(EDGE * TOL[0] * np.cos(e), EDGE * TOL[1] * np.sin(e), color="k", lw=1.5, ls="--", label=f"m = {EDGE}")
    a.set(xlim=(0, 90), ylim=(0, 180), xlabel="Tilt of the fault plane from the Slab2 plane (°)",
          ylabel="Turn of the slip from the convergence direction (°)", title="1. Each mechanism against the interface mechanism")
    a.legend(loc="upper right", frameon=False, fontsize=10)

    a = ax[1]
    b = np.arange(0, 5.01, 0.25)
    a.hist([np.minimum(m[near], 4.99), np.minimum(m[~near], 4.99)], bins=b, stacked=True, color=col, label=lab)
    for v, ls in ((1, "-"), (EDGE, "--")):
        a.axvline(v, color="k", lw=1.5, ls=ls)
    top = a.get_ylim()[1]
    for lo, hi, xt in ((0, 1, 0.5), (1, EDGE, 1.25), (EDGE, np.inf, 3.2)):
        q = (m > lo) & (m <= hi) if lo else m <= hi
        a.text(xt, top * 1.03, f"{q.sum()} events\n{near[q].mean():.0%} near", ha="center", fontsize=10)
    a.set(xlim=(0, 5), ylim=(0, top * 1.15), xlabel="Misfit m (last bar: 5 or more)", ylabel="Events", title="2. Spread of the misfit")
    a.legend(loc="center right", frameon=False, fontsize=10)

    f.suptitle(f"Mechanisms of the {len(m)} events over the shallow slab", fontsize=13)
    f.tight_layout(rect=(0, 0, 1, 0.96))
    f.savefig(OUT, dpi=160)
    for lo, hi in ((0, 1), (1, EDGE), (EDGE, np.inf)):
        q = (m > lo) & (m <= hi) if lo else m <= hi
        print(lo, hi, q.sum(), near[q].mean().round(2), np.median(np.abs(d[q])).round(1))


if __name__ == "__main__":
    main()

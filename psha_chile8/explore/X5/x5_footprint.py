"""X5: every event over the shallow slab by its depth against the Slab2 surface, and the misfit of its mechanism."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import x5_lib as X
import x5_models as M

sys.path.insert(0, str(X.ROOT))
from palette import CLASS_COLOR  # noqa: E402

W, EDGE, LIM = X.C.W, 1.5, (-45.0, 70.0)
OUT = Path(__file__).parent / "figs" / "footprint.png"


def main():
    c, g = X.load()
    x = g[M.subset(g)]
    m, d, mw = (x[q].to_numpy(float) for q in ("em", "d", "mw"))
    hm = np.isfinite(m)
    plt.rcParams.update({"font.family": "Ubuntu", "font.size": 11})
    f, ax = plt.subplots(1, 2, figsize=(14, 6.4), gridspec_kw={"width_ratios": [1.6, 1.0]}, sharey=True)

    a = ax[0]
    a.axhspan(-W, W, color=CLASS_COLOR["interface"], alpha=0.12, lw=0)
    o = np.argsort(mw[hm])
    a.scatter(np.minimum(m[hm], 4.95)[o], d[hm][o], s=4 + 3 * (mw[hm][o] - 4.4) ** 2.5, color="0.25", alpha=0.55, lw=0)
    big = hm & (mw >= 6.95)
    a.scatter(np.minimum(m[big], 4.95), d[big], s=4 + 3 * (mw[big] - 4.4) ** 2.5, facecolor="none", edgecolor="#c0392b", lw=1.4, label="Mw ≥ 7")
    a.axhline(0, color="k", lw=1.5)
    for v, ls in ((1, "-"), (EDGE, "--")):
        a.axvline(v, color="k", lw=1.2, ls=ls)
    a.text(4.9, -W + 1, f"buffer ± {W:.0f} km", ha="right", va="top", color=CLASS_COLOR["interface"], fontsize=10)
    a.text(4.9, 1.5, "Slab2 surface", ha="right", va="top", fontsize=10)
    for lo, hi, xt in ((0, 1, 0.5), (1, EDGE, 1.25), (EDGE, np.inf, 3.2)):
        q = hm & (m > lo) & (m <= hi) if lo else hm & (m <= hi)
        n = [int((q & r).sum()) for r in (d < -W, np.abs(d) <= W, d > W)]
        a.text(xt, LIM[0] + 2, f"{n[0]}", ha="center", va="top", fontsize=10, fontweight="bold")
        a.text(xt, -1.5, f"{n[1]}", ha="center", va="bottom", fontsize=10, fontweight="bold", color="#08306b")
        a.text(xt, LIM[1] - 2, f"{n[2]}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    a.set(xlim=(0, 5), ylim=(LIM[1], LIM[0]), xlabel="Misfit m of the mechanism (5 = 5 or more); solid m = 1, dashed m = 1.5",
          ylabel="Depth − Slab2 surface (km); negative is above", title=f"1. Events with a mechanism ({hm.sum()})")
    a.legend(loc="upper right", frameon=False, fontsize=10, bbox_to_anchor=(1, 0.93))

    a = ax[1]
    b = np.arange(LIM[0], LIM[1] + 0.1, 2.5)
    a.hist([np.clip(d[hm], *LIM), np.clip(d[~hm], *LIM)], bins=b, stacked=True, orientation="horizontal", color=["0.25", "0.7"],
           label=[f"with a mechanism ({hm.sum()})", f"without ({(~hm).sum()})"])
    a.axhspan(-W, W, color=CLASS_COLOR["interface"], alpha=0.12, lw=0)
    a.axhline(0, color="k", lw=1.5)
    a.set(xlabel="Events", title=f"2. All events ({len(d)})")
    a.legend(loc="lower right", frameon=False, fontsize=10)

    f.suptitle("Events over the shallow slab (Slab2 surface above 50 km), Mw ≥ 4.5, with a measured depth", fontsize=13)
    f.tight_layout(rect=(0, 0, 1, 0.96))
    f.savefig(OUT, dpi=160)
    print("above / in / below the buffer:", [int(r.sum()) for r in (d < -W, np.abs(d) <= W, d > W)])


if __name__ == "__main__":
    main()

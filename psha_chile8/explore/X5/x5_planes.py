"""X5: the nodal planes of our mechanisms in strike, rake and dip, as in the cluster analysis of Specht et al. (2017)."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import x5_lib as X
import x5_models as M

OUT = Path(__file__).parent / "figs" / "planes.png"


def main():
    c, g = X.load()
    k = M.subset(g) & g.em.notna().to_numpy()
    x, cc = g[k], c[k]
    ins = (x.em <= 1).to_numpy()
    plt.rcParams.update({"font.family": "Ubuntu", "font.size": 11})
    f, ax = plt.subplots(1, 2, figsize=(14, 6.2), sharey=True)
    for a, q, t in ((ax[0], ins, "inside the ellipse (m ≤ 1)"), (ax[1], ~ins, "outside the ellipse (m > 1)")):
        for s, d, r in (("strike1", "dip1", "rake1"), ("strike2", "dip2", "rake2")):
            ds = (cc[s].to_numpy(float)[q] - x.sstr.to_numpy(float)[q] + 180) % 360 - 180
            sc = a.scatter(ds, cc[r].to_numpy(float)[q], c=cc[d].to_numpy(float)[q], cmap="viridis", vmin=0, vmax=90, s=12, alpha=0.7, lw=0)
        a.set(xlim=(-180, 180), ylim=(-180, 180), xticks=np.arange(-180, 181, 60), yticks=np.arange(-180, 181, 45),
              xlabel="Strike of the nodal plane − strike of Slab2 (°)", title=f"{q.sum()} events {t}")
        a.grid(color="0.85", lw=0.6)
    ax[0].set_ylabel("Rake (°): 90 reverse, −90 normal, 0 and ±180 strike-slip")
    f.colorbar(sc, ax=ax, label="Dip of the nodal plane (°)", shrink=0.85, pad=0.02)
    f.suptitle("Both nodal planes of every mechanism over the shallow slab", fontsize=13)
    f.savefig(OUT, dpi=160, bbox_inches="tight")
    r1, r2 = cc.rake1.to_numpy(float), cc.rake2.to_numpy(float)
    rev, nor = (r1 > 45) & (r1 < 135) & (r2 > 45) & (r2 < 135), (r1 < -45) & (r1 > -135) & (r2 < -45) & (r2 > -135)
    for nm, q in (("reverse", rev), ("normal", nor), ("other", ~rev & ~nor)):
        print(nm, q.sum(), "inside ellipse", (q & ins).sum(), "median d", np.median(x.d[q]).round(1))


if __name__ == "__main__":
    main()

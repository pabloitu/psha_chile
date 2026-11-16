# Matrix of the tornado levels: cities (north to south) by levels, the columns grouped by tectonic setting
# (interface, in-slab, crustal) and, inside each group, ordered by the mean change over the cities. Cell = the
# largest |change| of the total PGA 475 yr (all tectonic settings) over the branches of the level (%). Reads hazard/out/tornado_prelim/<city>.csv; writes hazard/out/tornado_matrix/

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import palette
from hazard import config as hc
from hazard.tornado_prelim import COL, NAME

# settings
OUT = hc.OUT / "tornado_matrix"
VMAX = 30.0
CELL = 0.42
PANELS = {"combined_pct": "all tectonic settings"}


def table():
    rows = []
    for c in hc.CITIES:
        g = pd.read_csv(hc.OUT / "tornado_prelim" / f"{c.replace(' ', '_')}.csv")
        g = g[g.kind != "set"]
        for (f, a), q in g.groupby(["family", "axis"], sort=False):
            rows.append({"site": c, "family": f, "axis": a, **{k: np.nanmax(np.abs(q[k])) for k in PANELS}})
    return pd.DataFrame(rows)


def main():
    palette.apply(size=13)
    OUT.mkdir(parents=True, exist_ok=True)
    t = table()
    t.to_csv(OUT / "matrix.csv", index=False)
    o = t.groupby(["family", "axis"], sort=False).combined_pct.mean().reset_index()
    o["k"] = o.family.map({f: i for i, f in enumerate(COL)})
    o = o.sort_values(["k", "combined_pct"], ascending=[True, False])
    cols = list(zip(o.family, o.axis))
    sites = list(hc.CITIES)
    nc, nr = len(cols), len(sites)
    fig, ax0 = plt.subplots(figsize=(CELL * nc + 3.2, CELL * nr + 3.0), layout="constrained")
    axs = [ax0]
    for ax, (k, title) in zip(axs, PANELS.items()):
        m = t.pivot_table(index="site", columns=["family", "axis"], values=k).reindex(index=sites, columns=cols)
        v = m.to_numpy()
        im = ax.imshow(np.clip(v, 0, VMAX), cmap="Reds", vmin=0, vmax=VMAX, aspect="auto")
        for i in range(nr):
            for j in range(nc):
                if np.isfinite(v[i, j]):
                    ax.text(j, i, f"{v[i, j]:.0f}", ha="center", va="center", fontsize=8,
                            color="white" if v[i, j] > 0.6 * VMAX else "0.15")
        # group bands and separators
        b = 0
        for f in COL:
            n = sum(x[0] == f for x in cols)
            if not n:
                continue
            ax.axvline(b - 0.5, color="k", lw=1.6)
            ax.add_patch(plt.Rectangle((b - 0.5, -1.25), n, 0.6, color=COL[f], clip_on=False))
            ax.text(b - 0.5 + n / 2, -0.95, NAME[f], ha="center", va="center", fontsize=13, color="white",
                    fontweight="bold")
            b += n
        ax.set_xticks(range(nc))
        ax.set_xticklabels([a for _, a in cols], rotation=60, ha="right", fontsize=11)
        ax.set_yticks(range(nr))
        ax.set_yticklabels(sites, fontsize=12)
        ax.set_ylim(nr - 0.5, -1.3)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.colorbar(im, ax=axs, shrink=0.8, label=f"largest |change| of PGA 475 yr (%), scale capped at {VMAX:g}")
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"matrix.{ext}", dpi=150, facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

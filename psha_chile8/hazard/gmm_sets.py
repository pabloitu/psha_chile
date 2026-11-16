# The four GMM sets of DECISIONS (E17) as wholes: PGA 475 yr per family on its reference source branch, and the total
# with every family on the same set (the GM1 top-four crustal set is the current crustal tree).
# Outputs in hazard/out/gmm_sets/: pga475.csv, gmm_sets.png

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pituplots.style.axes import darkgrid

import palette
from hazard import combine, post
from hazard import config as hc

# settings
CITIES = ["Iquique", "Antofagasta", "Copiapó", "Valparaíso", "Santiago centro", "Concepción"]
OUT = hc.OUT / "gmm_sets"
POE = 0.002105
SETS = {"GMM-1R": "ref", "GMM-FIT": "set_gm1top4", "GMM-CSN": "set_mascsn26",
        "GMM-GEM": "set_gem_sam"}
FAM = {"interface": "if", "in-slab": "is", "crustal": "cr"}
COL = ["0.25", palette.SERIES[0], palette.SERIES[1], palette.SERIES[2]]


def job(f, s):
    if s == "ref" or (f == "cr" and s == "set_gm1top4"):
        return f"t_{f}_ref"
    return f"t_{f}_{s}"


def main():
    palette.apply()
    OUT.mkdir(parents=True, exist_ok=True)
    cache, rows = {}, []
    for k, s in SETS.items():
        rt = 0
        for name, f in FAM.items():
            j = job(f, s)
            if j not in cache:
                r = post.load(j)
                cache[j] = post.mean(r)
                lv = r["imtls"]["PGA"]
            m = cache[j]
            rt = rt + combine.rate(m)
            rows += [{"set": k, "model": name, "site": c, "pga": post.iml(m[i], lv, POE)}
                     for i, c in enumerate(hc.CITIES)]
        rows += [{"set": k, "model": "all three", "site": c, "pga": post.iml(1 - np.exp(-rt[i]), lv, POE)}
                 for i, c in enumerate(hc.CITIES)]
    d = pd.DataFrame(rows)
    d.to_csv(OUT / "pga475.csv", index=False, float_format="%.4f")
    w = d[d.site.isin(CITIES)].pivot_table(index=["model", "site"], columns="set", values="pga", sort=False)
    print(w[list(SETS)].round(3).to_string())

    fig, axs = plt.subplots(1, 4, figsize=(18, 5.5), sharey=False, layout="constrained")
    x = np.arange(len(CITIES))
    bw = 0.2
    for ax, mdl in zip(axs, ["interface", "in-slab", "crustal", "all three"]):
        for i, (k, c) in enumerate(zip(SETS, COL)):
            v = [d[(d.set == k) & (d.model == mdl) & (d.site == s)].pga.iloc[0] for s in CITIES]
            ax.bar(x + (i - 1.5) * bw, v, bw, color=c, label=k)
        ax.set_xticks(x)
        ax.set_xticklabels(CITIES, rotation=40, ha="right")
        darkgrid(ax)
        ax.text(0.02, 0.97, mdl, transform=ax.transAxes, ha="left", va="top", fontsize=13)
    axs[0].set_ylabel("PGA 475 yr (g)")
    fig.legend(*axs[0].get_legend_handles_labels(), loc="outside lower center", ncol=4, frameon=False)
    fig.savefig(OUT / "gmm_sets.png", dpi=200, facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

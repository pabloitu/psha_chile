# Share of each family in the hazard at the total PGA 475 yr of the references (rate of the family over the total rate
# at that ground motion), and the tornado change of the family alone against the change of the total, coloured by that
# share. Outputs in hazard/out/shares/: shares.csv, shares.png, scatter.png

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

OUT = hc.OUT / "shares"
POE = 0.002105
REF = {"interface": "t_if_ref", "inslab": "t_is_ref", "crustal": "t_cr_ref"}
NAME = {"interface": "interface", "inslab": "in-slab", "crustal": "crustal"}
COL = {"interface": palette.CLASS_COLOR["interface"], "inslab": palette.CLASS_COLOR["intraslab_intermediate"],
       "crustal": palette.CLASS_COLOR["forearc"]}
LIM = 100.0


def shares():
    m, lv = {}, None
    for f, j in REF.items():
        r = post.load(j)
        m[f], lv = post.mean(r), r["imtls"]["PGA"]
    rt = {f: combine.rate(v) for f, v in m.items()}
    tot = sum(rt.values())
    rows = []
    for s, c in enumerate(hc.CITIES):
        x = post.iml(1 - np.exp(-tot[s]), lv, POE)
        r = {f: np.exp(np.interp(np.log(x), np.log(lv), np.log(np.maximum(v[s], 1e-300)))) for f, v in rt.items()}
        rows.append({"site": c, "pga": x, **{f: r[f] / sum(r.values()) for f in REF}})
    return pd.DataFrame(rows)


def main():
    palette.apply()
    OUT.mkdir(parents=True, exist_ok=True)
    d = shares()
    d.to_csv(OUT / "shares.csv", index=False, float_format="%.4f")
    print(d.round(3).to_string(index=False))

    fig, ax = plt.subplots(figsize=(12, 5), layout="constrained")
    x = np.arange(len(d))
    b = np.zeros(len(d))
    for f in REF:
        ax.bar(x, 100 * d[f], 0.7, bottom=b, color=COL[f], label=NAME[f])
        b += 100 * d[f]
    for i, p in enumerate(d.pga):
        ax.text(i, 101, f"{p:.2f} g", ha="center", va="bottom", fontsize=9, color="0.25")
    ax.set_xticks(x)
    ax.set_xticklabels(d.site, rotation=40, ha="right")
    ax.set_ylabel("share of the hazard at PGA 475 yr (%)")
    ax.set_ylim(0, 108)
    darkgrid(ax)
    fig.legend(*ax.get_legend_handles_labels(), loc="outside lower center", ncol=3, frameon=False)
    fig.savefig(OUT / "shares.png", dpi=200, facecolor="white")
    plt.close(fig)

    t = pd.read_csv(hc.OUT / "tornado" / "tornado.csv").dropna(subset=["family_pct", "combined_pct"])
    sh = d.set_index("site")
    t["share"] = [sh.loc[s, f] for s, f in zip(t.site, t.family)]
    fig, axs = plt.subplots(1, 3, figsize=(16, 5.5), sharex=True, sharey=True, layout="constrained")
    for ax, f in zip(axs, REF):
        g = t[t.family == f]
        sc = ax.scatter(np.clip(g.family_pct, -LIM, LIM), np.clip(g.combined_pct, -LIM, LIM), c=100 * g.share,
                        cmap="viridis", vmin=0, vmax=100, s=22, edgecolor="0.2", lw=0.3, zorder=3)
        ax.plot([-LIM, LIM], [-LIM, LIM], color="0.3", lw=0.8, ls="--")
        ax.axhspan(-5, 5, color="0.5", alpha=0.15, lw=0)
        ax.set_xlim(-LIM, LIM)
        ax.set_ylim(-LIM, LIM)
        darkgrid(ax)
        ax.text(0.03, 0.97, NAME[f], transform=ax.transAxes, ha="left", va="top", fontsize=13)
        ax.set_xlabel("change of the family alone (%)")
    axs[0].set_ylabel("change of the total (%)")
    cb = fig.colorbar(sc, ax=axs, shrink=0.8)
    cb.set_label("share of the family at the city (%)")
    fig.savefig(OUT / "scatter.png", dpi=200, facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

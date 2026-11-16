# Contribution of each tectonic setting to the hazard of every city: at the total PGA 475 yr of the three references,
# the annual rate of exceedance of each family over the total rate (rates add, so the shares sum to 1). One stacked
# bar per city, north to south, the total PGA 475 yr written at the right. Writes hazard/out/shares/contribution.png/.pdf

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
from hazard.tornado_prelim import COL, NAME, FAM

# settings
OUT = hc.OUT / "shares"
POE = 0.002105
SHOW = 6.0


def shares():
    r = {f: post.load(f"t_{a}_ref") for f, (a, _) in FAM.items()}
    lv = r["interface"]["imtls"]["PGA"]
    rt = {f: combine.rate(post.mean(v)) for f, v in r.items()}
    tot = sum(rt.values())
    rows = []
    for s, c in enumerate(hc.CITIES):
        x = post.iml(1 - np.exp(-tot[s]), lv, POE)
        lx = np.log(x)
        sh = {f: np.exp(np.interp(lx, np.log(lv), np.log(np.maximum(rt[f][s], 1e-30)))) for f in FAM}
        n = sum(sh.values())
        rows.append({"site": c, "pga475": x, **{f: 100 * v / n for f, v in sh.items()}})
    return pd.DataFrame(rows)


def main():
    palette.apply(size=13)
    OUT.mkdir(parents=True, exist_ok=True)
    d = shares()
    d.to_csv(OUT / "contribution.csv", index=False)
    n = len(d)
    fig, ax = plt.subplots(figsize=(10.5, 0.5 * n + 1.6), layout="constrained")
    y = np.arange(n)
    for i, r in d.iterrows():
        left = 0.0
        for f in FAM:
            v = r[f]
            ax.barh(i, v, left=left, height=0.62, color=COL[f], edgecolor="0.9", lw=1.5)
            if v >= SHOW:
                ax.text(left + v / 2, i, f"{v:.0f}", ha="center", va="center", fontsize=11,
                        color="0.1" if f == "crustal" else "white")
            left += v
        g = f"{r.pga475:.2f} g" if np.isfinite(r.pga475) else "–"
        ax.text(102.5, i, g, ha="left", va="center", fontsize=12, color="0.15")
    ax.set_yticks(y)
    ax.set_yticklabels(d.site, fontsize=13, color="0.15")
    ax.set_ylim(n - 0.4, -1.4)
    ax.set_xlim(0, 113)
    darkgrid(ax)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0", "25", "50", "75", "100 %"], fontsize=11, color="0.35")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", which="minor", visible=False)
    ax.tick_params(length=0, pad=6)
    x = 0
    for f in FAM:
        ax.text(x, -1.05, "■", color=COL[f], fontsize=15, va="center", ha="left")
        ax.text(x + 3.2, -1.05, NAME[f], color="0.15", fontsize=13, va="center", ha="left")
        x += 17
    ax.text(100, -1.05, "share of the 475-yr hazard (%)", color="0.45", fontsize=11, va="center", ha="right")
    ax.text(102.5, -1.05, "PGA 475 yr", color="0.45", fontsize=11, va="center", ha="left")
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"contribution.{ext}", dpi=170, facecolor="white")
    plt.close(fig)
    print(d.round(2).to_string(index=False))


if __name__ == "__main__":
    main()

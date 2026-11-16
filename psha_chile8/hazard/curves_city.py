# Hazard curves per city and tectonic setting with the epistemic spread of the tornado: solid line = reference of the
# family (and the total of the three references, black), band = envelope of every tornado branch of the family (source
# rows, single GMMs of each set, truncation); the total band is the envelope of every branch of every family combined
# in rate space with the references of the other two. PGA, rock. Writes hazard/out/curves/<city>.png and all.png

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from pituplots.style.axes import darkgrid

import palette
from hazard import combine, post
from hazard import config as hc
from hazard import jobs as J
from hazard.tornado_prelim import COL, NAME, FAM

# settings
OUT = hc.OUT / "curves"
POE = 0.002105
XLIM, YLIM = (0.005, 3.0), (1e-5, 0.2)
CACHE = {}


def load(j):
    if j not in CACHE:
        CACHE[j] = post.load(j)
    return CACHE[j]


def branches(f):
    """Curves (sites, levels) of every tornado branch of family f: the mean of each row job and each single GMM."""
    a, trt = FAM[f]
    out = [post.mean(load(j)) for j, r in J.ROWS.items() if r[0] == f and "skip" not in J.JOBS[j]]
    for j in [n for n in J.JOBS if n.startswith(f"t_{a}_set_")] + [f"t_{a}_ref"]:
        r = load(j)
        c = r["curves"][:, :, 0, :]
        for g in dict.fromkeys(x[trt] for x in r["gmm"]):
            i = np.array([x[trt] == g for x in r["gmm"]])
            out.append(np.einsum("r,srl->sl", r["w"][i], c[:, i]) / r["w"][i].sum())
    return out


def style(ax):
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    darkgrid(ax)
    ax.grid(True, which="minor", lw=0.4)
    ax.axhline(POE, color="k", lw=0.8, ls="--")
    ax.text(XLIM[0] * 1.15, POE * 1.15, "10% in 50 yr", fontsize=10, color="0.15")


def panel(ax, s, ref, band, tot, tband, lv, name, fs=1.0):
    style(ax)
    for f in FAM:
        if np.nanmax(ref[f][s]) <= 0:
            continue
        ax.fill_between(lv, band[f][0][s], band[f][1][s], color=COL[f], alpha=0.3, lw=0)
        ax.plot(lv, ref[f][s], color=COL[f], lw=2)
    ax.fill_between(lv, tband[0][s], tband[1][s], color="0.3", alpha=0.18, lw=0)
    ax.plot(lv, tot[s], color="k", lw=2.4)
    x = post.iml(tot[s], lv, POE)
    if np.isfinite(x):
        ax.plot(x, POE, "o", ms=5, color="0.1", zorder=5)
        ax.annotate(f"{x:.2f} g", (x, POE), xytext=(9, -20), textcoords="offset points", fontsize=10 * fs,
                    color="0.1", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    ax.set_title(name, fontsize=15 * fs, loc="left")


def main():
    palette.apply(size=12)
    OUT.mkdir(parents=True, exist_ok=True)
    lv = load("t_if_ref")["imtls"]["PGA"]
    ref = {f: post.mean(load(f"t_{FAM[f][0]}_ref")) for f in FAM}
    rt = {f: combine.rate(v) for f, v in ref.items()}
    tot = 1 - np.exp(-sum(rt.values()))
    band, tb = {}, []
    for f in FAM:
        b = np.array(branches(f) + [ref[f]])
        band[f] = (b.min(0), b.max(0))
        oth = sum(rt[x] for x in FAM if x != f)
        tb.append(1 - np.exp(-(combine.rate(b) + oth)))
    tb = np.concatenate(tb)
    tband = (tb.min(0), tb.max(0))
    hnd = [Line2D([], [], color=COL[f], lw=2, label=NAME[f]) for f in FAM] + [
        Line2D([], [], color="k", lw=2.4, label="all tectonic settings"),
        Patch(facecolor="0.6", edgecolor="none", alpha=0.5, label="range of the tornado branches")]
    for s, c in enumerate(hc.CITIES):
        # one slide figure per city: 16:9, large fonts, legend outside on the right
        fig, ax = plt.subplots(figsize=(12, 6.75), layout="constrained")
        panel(ax, s, ref, band, tot, tband, lv, c, fs=1.6)
        ax.set_xlabel("PGA $[g]$", fontsize=18)
        ax.set_ylabel("Probability of exceedance - 1 year", fontsize=18)
        ax.tick_params(labelsize=15)
        ax.texts[0].set_fontsize(14)
        ax.legend(handles=hnd, loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=True, facecolor="white",
                  edgecolor="none", fontsize=15)
        fig.savefig(OUT / f"{c.replace(' ', '_')}.png", dpi=170, facecolor="white")
        plt.close(fig)
    fig, axs = plt.subplots(4, 4, figsize=(16, 14), sharex=True, sharey=True, layout="constrained")
    for k, ax in enumerate(axs.flat):
        if k >= len(hc.CITIES):
            ax.axis("off")
            continue
        panel(ax, k, ref, band, tot, tband, lv, list(hc.CITIES)[k])
        if k % 4 == 0:
            ax.set_ylabel("Probability of exceedance - 1 year")
        if k >= 10:
            ax.set_xlabel("PGA $[g]$")
            ax.xaxis.set_tick_params(labelbottom=True)
    fig.legend(handles=hnd, loc="center", frameon=True, facecolor="white", edgecolor="none", fontsize=14, bbox_to_anchor=(0.75, 0.13))
    fig.savefig(OUT / "all.png", dpi=150, facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

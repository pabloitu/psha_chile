"""Figures of B12, called by run_declustered.py: frequency-magnitude per unit for the full and the declustered
catalogues, b against the fit floor, and N(>= 7) per unit and method."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import gr as G
import run as R
import run_declustered as RD

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import palette as P

COL = {"full": P.INK, "gk": P.SERIES[1], "gk_family": P.SERIES[4], "nn": P.SERIES[0], "nn_depth": P.SERIES[2],
       "nn_family": P.SERIES[5]}
MK = {"full": "o", "gk": "s", "gk_family": "D", "nn": "^", "nn_depth": "v", "nn_family": "P"}


def save(fig, name):
    fig.savefig(RD.FIG / f"{name}.png", dpi=150, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def fig_mfd(d):
    te = G.tend(d)
    fig, ax = plt.subplots(3, 4, figsize=(18, 12), sharex=True)
    for name, lab in RD.METHODS.items():
        F = R.fits(RD.declustered(d, RD.keep(d, name)), te, "taper", nboot=0)[0]
        for a, u in zip(ax.ravel(), R.ORDER):
            f = F[u]
            use = f["T"] > 0
            cum = np.cumsum(np.where(use, f["cnt"] / np.where(use, f["T"], 1), 0)[::-1])[::-1]
            s = use & (f["cnt"] > 0)
            xx = np.arange(5.0, f["mmax"] + 0.05 + 1e-6, 0.1)
            a.plot(G.centres()[s], cum[s], MK[name], ms=3.5, color=COL[name], alpha=0.8, zorder=3 if name == "full" else 2)
            a.plot(xx, G.n_ge(f, xx), color=COL[name], lw=1.4 if name == "full" else 1.1, label=f"{lab}, b {f['b']:.2f}")
    for a, u in zip(ax.ravel(), R.ORDER):
        a.set_yscale("log")
        a.set_ylim(1e-4, 80)
        a.set_title(R.name(u), fontsize=11)
        a.legend(fontsize=7.5, loc="upper right", frameon=False)
    for a in ax[:, 0]:
        a.set_ylabel("events per year at and above Mw")
    for a in ax[-1]:
        a.set_xlabel("Mw")
    fig.suptitle("Full against declustered catalogues: observed rates and tapered fits on the full-catalogue completeness table",
                 x=0.02, ha="left", fontsize=13)
    fig.tight_layout()
    save(fig, "declustered_fmd")


def fig_floor(fl):
    q = fl[fl.table == "full"]
    us = [u for u in R.ORDER if u in set(q.unit)]
    fig, ax = plt.subplots(2, 6, figsize=(19, 6.8), sharex=True, sharey=True)
    for a, u in zip(ax.ravel(), us):
        for name, lab in RD.METHODS.items():
            z = q[(q.unit == u) & (q.method == name)]
            a.fill_between(z.floor, z.b - z.b_sd, z.b + z.b_sd, color=COL[name], alpha=0.10, lw=0)
            a.plot(z.floor, z.b, "-" + MK[name], ms=3.5, color=COL[name], label=lab)
        a.set_title(R.name(u), fontsize=10)
    for a in ax.ravel()[len(us):]:
        a.axis("off")
    ax[0, 0].set_ylim(0.4, 1.7)
    ax.ravel()[-1].legend(*ax[0, 0].get_legend_handles_labels(), fontsize=9, loc="center", frameon=False)
    for a in ax[:, 0]:
        a.set_ylabel("b")
    for a in ax[-1]:
        a.set_xlabel("lowest magnitude fitted")
    fig.suptitle("b against the fit floor, full and declustered catalogues (line cut at Mmax; band ± one bootstrap sd)",
                 x=0.02, ha="left", fontsize=12)
    fig.tight_layout()
    save(fig, "declustered_b_floor")


def fig_n7(x):
    q = x[(x["shape"] == "taper") & (x.b_option == "own") & (x.table == "full")]
    fig, ax = plt.subplots(figsize=(16, 5.6))
    n = len(RD.METHODS)
    for j, (name, lab) in enumerate(RD.METHODS.items()):
        z = q[q.method == name].set_index("unit").loc[R.ORDER]
        xx = np.arange(len(R.ORDER)) + (j - (n - 1) / 2) * 0.135
        ax.bar(xx, z.N7, 0.125, color=COL[name], label=lab)
        ax.errorbar(xx, z.N7, yerr=[z.N7 - z.N7_lo, z.N7_hi - z.N7], fmt="none", ecolor="0.3", lw=0.8, capsize=2)
    ax.set_yscale("log")
    ax.set_xticks(np.arange(len(R.ORDER)), [R.name(u).replace(", ", ",\n") for u in R.ORDER], fontsize=9.5)
    ax.set_ylabel("N(≥ 7) per year (tapered fit)")
    ax.legend(fontsize=9.5, ncol=3, loc="upper right", frameon=False)
    ax.set_title("Yearly rate of Mw ≥ 7 per unit and catalogue (whiskers: 5–95 % of the bootstrap)", fontsize=12)
    fig.tight_layout()
    save(fig, "declustered_N7")


def run(d, x, fl, c):
    P.apply()
    fig_mfd(d)
    fig_floor(fl)
    fig_n7(x)


if __name__ == "__main__":
    import pandas as pd
    d = G.load()
    RD.full_mmax(d)
    x = pd.read_csv(RD.TAB / f"fits_declustered_{RD.DATE}.csv")
    fl = pd.read_csv(RD.TAB / f"declustered_floor_{RD.DATE}.csv")
    run(d, x, fl, None)

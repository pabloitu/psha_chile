"""Figures of B12, called by run_declustered.py: frequency-magnitude per unit for the full and the declustered
catalogues, b against the fit floor, and N(>= 7) per unit and method."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pituplots.style.axes import darkgrid

import gr as G
import run as R
import run_declustered as RD

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import palette as P
from figs import tag

COL = {"full": P.INK, "gk": P.SERIES[1], "gk_family": P.SERIES[4], "gk_gruenthal_family": P.SERIES[6], "gk_uhrhammer_family": P.SERIES[7],
       "nn": P.SERIES[0], "nn_depth": P.SERIES[2], "nn_family": P.SERIES[5]}
MK = {"full": "o", "gk": "s", "gk_family": "D", "gk_gruenthal_family": "<", "gk_uhrhammer_family": ">", "nn": "^", "nn_depth": "v",
      "nn_family": "P"}
# the four algorithms per family and their display names (paper figures)
ALG = {"full": ("Full catalogue", "#1f2a36"), "gk_family": ("Gardner–Knopoff", P.SERIES[0]), "gk_gruenthal_family": ("Grünthal", P.SERIES[4]),
       "gk_uhrhammer_family": ("Uhrhammer", P.SERIES[2]), "nn_family": ("Nearest neighbour", P.SERIES[1])}


def save(fig, name):
    RD.FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(RD.FIG / f"{name}.png", dpi=150, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


SHOWN = ("full", "gk_family", "nn_family")


def fig_mfd(d):
    """Full against the two declustering options of the logic tree: cumulative and per-bin rates and tapered fits."""
    te = G.tend(d)
    fig, ax = plt.subplots(3, 4, figsize=(18, 12))
    for name, lab in ((k, RD.METHODS[k]) for k in SHOWN):
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
        a.set_ylim(1e-5, 80)
        darkgrid(a)
        a.set_xlim(4.9, R.UNITS[u]["mmax"] + 0.35)
        tag(a, R.name(u))
        a.legend(fontsize=7.5, loc="lower left", frameon=False)
    for a in ax[:, 0]:
        a.set_ylabel("events per year at and above Mw")
    for a in ax[-1]:
        a.set_xlabel("Mw")
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
        darkgrid(a)
        tag(a, R.name(u))
    for a in ax.ravel()[len(us):]:
        a.axis("off")
    ax[0, 0].set_ylim(0.4, 1.7)
    ax.ravel()[-1].legend(*ax[0, 0].get_legend_handles_labels(), fontsize=9, loc="center", frameon=False)
    for a in ax[:, 0]:
        a.set_ylabel("b")
    for a in ax[-1]:
        a.set_xlabel("lowest magnitude fitted")
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
    darkgrid(ax)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", ncol=len(RD.METHODS), bbox_to_anchor=(0.5, 0))
    save(fig, "declustered_N7")


def fig_margin(d0, te):
    """Whole-margin interface fit, one panel per catalogue, in the style of figs.fmd."""
    import figs
    figs.rcpaper()
    fig, ax = plt.subplots(2, 3, figsize=(6.9, 4.6), sharex=True, sharey=True)
    for a, (k, (name, _)) in zip(ax.ravel(), ALG.items()):
        d = d0 if k == "full" else RD.declustered(d0, RD.keep(d0, k))
        f = R.fit(d, "interface", te, "taper", nboot=500)
        figs.fmd(a, "interface", f, name=name)
        e7, o7, _ = G.check(f, 7.0)
        e8, o8, _ = G.check(f, 8.0)
        a.text(0.96, 0.80, f"$N(M \\geq 7)$ {e7:.0f} / {o7:.0f}\n$N(M \\geq 8)$ {e8:.1f} / {o8:.1f}", transform=a.transAxes, ha="right",
               va="top", fontsize=6, color="0.25", linespacing=1.4)
        a.set_ylim(*figs.SEG_YLIM)
        a.set_xlim(4.9, 9.85)
        a.set_xticks([5, 6, 7, 8, 9])
    for a in ax[:, 0]:
        a.set_ylabel("Annual rate", fontsize=7)
    for a in list(ax[-1, :2]) + [ax[0, 2]]:
        a.set_xlabel(r"$M_\mathrm{w}$", fontsize=7)
    ax[0, 2].tick_params(labelbottom=True)
    ax[1, 2].axis("off")
    h, l, kw = figs.handles("interface")
    ax[1, 2].legend(h + [plt.Line2D([], [], ls="")], l + ["$N$: fitted / observed"], loc="center", fontsize=6.5, frameon=False, handlelength=2.8,
                    **kw)
    fig.tight_layout(pad=0.4, h_pad=0.5, w_pad=0.5)
    figs.save(fig, "interface_margin_declustered", "declustering")


def fig_segments(d0, te):
    """Interface margin and segments, cumulative observed rates and tapered fits of the full catalogue and the four
    algorithms, one figure."""
    import figs
    from matplotlib.gridspec import GridSpec
    from matplotlib.legend_handler import HandlerTuple
    figs.rcpaper()
    F = {k: R.fits(d0 if k == "full" else RD.declustered(d0, RD.keep(d0, k)), te, "taper", nboot=0)[0] for k in ALG}
    fig = plt.figure(figsize=(6.9, 4.9))
    gs = GridSpec(2, 3, figure=fig, wspace=0.08, hspace=0.12)
    for n, u in enumerate(figs.SEGS):
        a = fig.add_subplot(gs[n // 3, n % 3])
        bs = []
        for k, (_, col) in ALG.items():
            f = F[k][u]
            use = f["T"] > 0
            cum = np.cumsum(np.where(use, f["cnt"] / np.where(use, f["T"], 1), 0.0)[::-1])[::-1]
            s = use & (f["cnt"] > 0)
            xx = np.arange(5.0, f["mmax"] + 0.05 + 1e-6, 0.01)
            a.plot(xx, G.n_ge(f, xx), color=col, lw=1.2 if k == "full" else 0.9, zorder=3)
            a.plot(G.centres()[s], cum[s], "o", ms=2.6 if k == "full" else 2.2, color=col, mec="white", mew=0.25, zorder=4)
            bs.append(f"{f['b']:.2f}")
        for mf, y in R.table_of(u):
            a.axvline(mf - 0.05, color="0.6", lw=0.4, zorder=0)
            a.text(mf - 0.02, 0.985, str(y), transform=a.get_xaxis_transform(), fontsize=5, color="0.4", va="top", ha="left", rotation=90)
        name = "Whole margin" if u == "interface" else R.name(u).replace("interface, ", "")
        a.text(0.04, 0.04, f"{name}\n$b$: " + " / ".join(bs), transform=a.transAxes, ha="left", va="bottom", fontsize=6, color=P.INK, linespacing=1.4)
        a.set_yscale("log")
        a.set_ylim(*figs.SEG_YLIM)
        a.set_xlim(4.9, 9.85)
        a.set_xticks([5, 6, 7, 8, 9])
        darkgrid(a, major_length=2, minor_length=1)
        a.tick_params(labelsize=6.5, labelleft=not n % 3, labelbottom=n >= 2)
        if not n % 3:
            a.set_ylabel("Annual rate", fontsize=7)
        if n >= 2:
            a.set_xlabel(r"$M_\mathrm{w}$", fontsize=7)
    lg = fig.add_subplot(gs[1, 2])
    lg.axis("off")
    h = [(plt.Line2D([], [], color=c, lw=1.0), plt.Line2D([], [], ls="", marker="o", ms=2.6, color=c, mec="white", mew=0.25)) for _, c in ALG.values()]
    lg.legend(h, [l for l, _ in ALG.values()], loc="center", fontsize=6.5, frameon=False, handlelength=2.6,
              title="Cumulative, tapered fit\n$b$ in this order in each panel", title_fontsize=6.5, handler_map={tuple: HandlerTuple(ndivide=None, pad=0.6)})
    figs.save(fig, "interface_segments_declustered", "declustering")


def run(d, x, fl, c):
    P.apply()
    fig_mfd(d)
    fig_floor(fl)
    fig_n7(x)
    te = G.tend(d)
    fig_margin(d, te)
    fig_segments(d, te)
    P.apply()


if __name__ == "__main__":
    import pandas as pd
    d = G.load()
    RD.full_mmax(d)
    x = pd.read_csv(RD.TAB / f"fits_declustered_{RD.DATE}.csv")
    fl = pd.read_csv(RD.TAB / f"declustered_floor_{RD.DATE}.csv")
    run(d, x, fl, None)

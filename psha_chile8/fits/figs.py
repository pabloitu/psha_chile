"""Figures of the fits (plan B11), called by run.py: frequency-magnitude per class and per interface segment, the
large-event check, b against the fit floor, the methods compared, and their recovery on synthetic catalogues."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
from scipy import stats

import gr as G
import run as R

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import palette as P

CLASSES = ["interface", "intraslab_shallow", "intraslab_intermediate", "jujuy_nest", "forearc", "arc", "backarc", "patagonia"]
SEGS = ["interface", "seg1", "seg2", "seg3", "seg4"]
SHORT = {"line cut at Mmax (reference)": "line cut at Mmax", "open line": "open line",
         "Aki–Utsu, Mw ≥ 5.0 from 1976": "Aki–Utsu, from 1976", "Ogata–Katsura, Mw ≥ 3.5 from 1976": "joint Mc–b (Ogata–Katsura)",
         "pooled b (shrinkage)": "pooled b", "least squares, cumulative": "least squares"}
# names of compare.py's synthetic runs
SYN = {"Weichert, open line (reference)": "Weichert, open line", "Weichert, line cut at Mmax": "line cut at Mmax",
       "tapered, corner 9.6": "tapered, corner 9.6", "Aki–Utsu, Mw ≥ 5.0 from 1976": "Aki–Utsu, from 1976",
       "Ogata–Katsura, Mw ≥ 3.5 from 1976": "joint Mc–b (Ogata–Katsura)", "least squares, cumulative": "least squares",
       "Weichert, no magnitude-error weight": "no magnitude-error weight"}


def color(u):
    return P.CLASS_COLOR[R.UNITS[u]["cls"]]


def save(fig, name):
    fig.savefig(R.FIG / f"{name}.png", dpi=150, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def fmd(ax, u, f, r, alt=()):
    """Observed yearly rates at and above Mw (each bin over its own observation time) and the fitted lines; f the
    tapered fit with its bootstrap, r its row of the table."""
    c = G.centres()
    use = f["T"] > 0
    rate = np.where(use, f["cnt"] / np.where(use, f["T"], 1), 0.0)
    cum = np.cumsum(rate[::-1])[::-1]
    s = use & (f["cnt"] > 0)
    xx = np.arange(5.0, f["mmax"] + 0.05 + 1e-6, 0.1)
    q = G.boot(f)
    lo, hi = (np.nanpercentile(G.n_ge(dict(q, b=q["b"][:, None], rate=q["rate"][:, None], corner=f["corner"]), xx[None, :]), p, axis=0) for p in (5, 95))
    ax.fill_between(xx, lo, hi, color="0.2", alpha=0.15, lw=0)
    ax.plot(xx, G.n_ge(f, xx), color="0.15", lw=1.3, label="tapered, 5–95 %")
    for g, lab, ls in alt:
        y = G.n_ge(g, xx)
        ax.plot(xx[y > 0], y[y > 0], color="0.15", lw=1.0, ls=ls, label=lab)
    ax.plot(c[s], cum[s], "o", ms=3.8, color=color(u), label="observed", zorder=3)
    for mf, y in R.TABLE:
        if mf <= xx[-1]:
            ax.axvline(mf - 0.05, color="0.75", lw=0.6, zorder=0)
            ax.text(mf - 0.02, 0.985, str(y), transform=ax.get_xaxis_transform(), fontsize=7.5, color="0.45", va="top", rotation=90)
    ax.set_yscale("log")
    fx = " (forearc)" if R.UNITS[u].get("b_from") else f" ± {r.b_sd:.2f}"
    ax.set_title(f"{R.name(u)}\nb {r.b:.2f}{fx}, N(≥ 5) {r.N5:.3g} per year, corner {r.corner:g}", fontsize=10.5)
    ax.set_ylim(max(1e-4, 0.3 * min(cum[s].min(), lo[-1])), 3 * cum[s].max())


def fig_fmd(F, x):
    xt = x[x["shape"] == "taper"].set_index("unit")
    fig, ax = plt.subplots(2, 4, figsize=(17, 8.2), sharex=True)
    for a, u in zip(ax.ravel(), CLASSES):
        fmd(a, u, F["taper"][0][u], xt.loc[u], [(F["trunc"][0][u], "cut at Mmax", "--")])
    ax[0, 0].legend(fontsize=8.5, loc="lower left")
    for a in ax[:, 0]:
        a.set_ylabel("events per year at and above Mw")
    for a in ax[-1]:
        a.set_xlabel("Mw")
    fig.suptitle("Frequency–magnitude distributions and fits per class (grey lines: steps of the completeness table, complete since)",
                 x=0.02, ha="left", fontsize=12)
    fig.tight_layout()
    save(fig, "fmd_classes")
    fig, ax = plt.subplots(1, 5, figsize=(19, 4.6), sharex=True)
    for a, u in zip(ax, SEGS):
        r, f = xt.loc[u], F["taper"][0][u]
        br = [(R.branch(f, r[f"a_p{p:02d}"], r[f"b_p{p:02d}"]), lab, ls) for p, lab, ls in ((5, "5th percentile branch", "--"), (95, "95th percentile branch", ":"))]
        fmd(a, u, f, r, br)
        a.set_xlabel("Mw")
    ax[0].legend(fontsize=8.5, loc="lower left")
    ax[0].set_ylabel("events per year at and above Mw")
    fig.suptitle("Interface, tapered line: the margin and the four segments, with the (a, b) branches at the 5th and 95th percentile of the rate of the controlling magnitude",
                 x=0.02, ha="left", fontsize=12)
    fig.tight_layout()
    save(fig, "fmd_interface_segments")


def fig_check(x):
    x = x[x["shape"] == "taper"].reset_index(drop=True)
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.6), sharey=True)
    yy = np.arange(len(x))[::-1]
    for a, M in zip(ax, (7, 8)):
        e, o = x[f"exp{M}"].to_numpy(), x[f"obs{M}"].to_numpy()
        lo, hi = stats.poisson.ppf(0.05, e), stats.poisson.ppf(0.95, e)
        for y, u, ei, l, h, oi, ok in zip(yy, x.unit, e, lo, hi, o, x[f"ok{M}"]):
            if ei < 0.05 and oi == 0:
                continue
            a.plot([l, h], [y, y], color="0.6", lw=5, solid_capstyle="butt", alpha=0.6)
            a.plot(ei, y, "|", color="0.15", ms=13, mew=1.5)
            a.plot(oi, y, "o", color=color(u), ms=7, mec="k" if not ok else "none", mew=1.4)
        a.set_xscale("symlog", linthresh=1)
        a.set_xlim(-0.2, 90)
        a.set_xticks([0, 1, 3, 10, 30], ["0", "1", "3", "10", "30"])
        a.set_xlabel(f"events of Mw ≥ {M} inside the completeness table")
        a.set_title(f"Mw ≥ {M}")
    ax[0].set_yticks(yy, x.name)
    ax[0].plot([], [], "|", color="0.15", ms=12, mew=1.5, label="fitted")
    ax[0].plot([], [], color="0.6", lw=5, alpha=0.6, label="Poisson 5–95 % of the fitted number")
    ax[0].plot([], [], "o", color="0.4", ms=7, label="observed (weighted count)")
    ax[0].plot([], [], "o", color="0.4", ms=7, mec="k", mew=1.4, label="observed, outside the band")
    ax[1].legend(*ax[0].get_legend_handles_labels(), fontsize=9, loc="center right")
    fig.suptitle("Large-event check, tapered line: events the fit expects against events observed", x=0.02, ha="left", fontsize=12)
    fig.tight_layout()
    save(fig, "large_event_check")


def fig_floor(x, s):
    x = x[x["shape"] == "trunc"]
    fig, ax = plt.subplots(2, 6, figsize=(19, 6.6), sharex=True, sharey=True)
    a_ = s[s.events == "all"]
    for a, u in zip(ax.ravel(), R.ORDER):
        r = x[x.unit == u].iloc[0]
        q = a_[(a_.unit == u) & a_.method.str.contains("floor")]
        a.axhspan(r.b - r.b_sd, r.b + r.b_sd, color="0.2", alpha=0.12, lw=0)
        if len(q):
            a.plot(np.r_[5.0, q.floor], np.r_[r.b, q.b], "-o", ms=4, color=color(u))
        else:
            a.plot(5.0, r.b, "o", ms=4, color=color(u))
            a.text(0.5, 0.1, "b of the forearc", transform=a.transAxes, ha="center", fontsize=9, color="0.4")
        a.set_title(R.name(u), fontsize=10)
    ax[0, 0].set_ylim(0.6, 1.6)
    for a in ax[:, 0]:
        a.set_ylabel("b")
    for a in ax[-1]:
        a.set_xlabel("lowest magnitude fitted")
    fig.suptitle("b against the fit floor (band: b at floor 5.0 ± its bootstrap standard deviation)", x=0.02, ha="left", fontsize=12)
    fig.tight_layout()
    save(fig, "b_floor")


def fig_methods(x, s):
    x = x[x["shape"] == "taper"]
    me = [k for k in SHORT if k in set(s.method)]
    a_ = s[(s.events == "all") & s.method.isin(me)]
    fig, ax = plt.subplots(1, 3, figsize=(18, 6.4), sharey=True)
    yy = {u: i for i, u in enumerate(R.ORDER[::-1])}
    for j, k in enumerate(me):
        q = a_[a_.method == k]
        ref = x.set_index("unit").loc[q.unit]
        off = (j - (len(me) - 1) / 2) * 0.11
        y = q.unit.map(yy).to_numpy() - off
        kw = dict(ms=5, color=P.SERIES[j], label=SHORT[k], ls="none", marker="o")
        ax[0].plot(q.b, y, **kw)
        ax[1].plot(q.N5.to_numpy() / ref.N5.to_numpy(), y, **kw)
        ax[2].plot(q.N7.to_numpy() / ref.N7.to_numpy(), y, **kw)
    r = x.set_index("unit").loc[R.ORDER[::-1]]
    ax[0].errorbar(r.b, np.arange(len(r)), xerr=1.645 * r.b_sd, fmt="D", ms=7, color="0.1", ecolor="0.1", lw=1, capsize=3, zorder=0, label="tapered (preferred)")
    ax[1].plot([], [])
    for a, c in ((ax[1], "N5"), (ax[2], "N7")):
        a.errorbar(np.ones(len(r)), np.arange(len(r)), xerr=[1 - r[c + "_lo"] / r[c], r[c + "_hi"] / r[c] - 1], fmt="none", ecolor="0.1", lw=1, capsize=3, zorder=0)
        a.axvline(1, color="0.6", lw=0.7, zorder=0)
        a.set_xscale("log")
        a.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax[1].set_xticks([0.7, 1, 1.5, 2], ["0.7", "1", "1.5", "2"])
    ax[1].set_xlim(0.6, 2.2)
    ax[2].set_xticks([0.3, 0.5, 1, 2, 3], ["0.3", "0.5", "1", "2", "3"])
    ax[2].set_xlim(0.25, 3.5)
    ax[0].set_yticks(np.arange(len(r)), r.name)
    ax[0].set_xlabel("b")
    ax[0].set_xlim(0.7, 1.7)
    ax[1].set_xlabel("N(≥ 5) over the tapered fit")
    ax[2].set_xlabel("N(≥ 7) over the tapered fit")
    fig.legend(*ax[0].get_legend_handles_labels(), fontsize=9.5, loc="lower center", ncol=len(me) + 1, bbox_to_anchor=(0.5, -0.05))
    fig.suptitle("Fitting methods compared on the same table and weights (whiskers: 5–95 % of the bootstrap of the tapered fit; points outside the axis are cut)",
                 x=0.02, ha="left", fontsize=12)
    fig.tight_layout()
    save(fig, "methods")


def fig_synth():
    f = R.TAB / "synth_methods.csv"
    if not f.exists():
        return
    z = pd.read_csv(f)
    sc = list(z.scenario.unique())
    fig, ax = plt.subplots(1, 4, figsize=(19, 5.4), sharey=True)
    me = [k for k in SYN if k in set(z.method)]
    yy = np.arange(len(me))[::-1]
    for i, s_ in enumerate(sc):
        q = z[z.scenario == s_].set_index("method").loc[me]
        kw = dict(fmt="o" if i == 0 else "s", color=P.SERIES[i], ms=6, capsize=3, lw=1, label=s_)
        ax[0].errorbar(q.b_bias, yy + 0.15 * (0.5 - i), xerr=q.b_sd, **kw)
        ax[1].errorbar(q.N5_bias * 100, yy + 0.15 * (0.5 - i), xerr=q.N5_sd * 100, **kw)
        ax[2].errorbar(q.N7_bias * 100, yy + 0.15 * (0.5 - i), xerr=q.N7_sd * 100, **kw)
        ax[3].plot(q.b_cover * 100, yy + 0.15 * (0.5 - i), "o" if i == 0 else "s", color=P.SERIES[i], ms=6)
        ax[3].plot(q.N7_cover * 100, yy + 0.15 * (0.5 - i), "o" if i == 0 else "s", color=P.SERIES[i], ms=6, mfc="none")
    for a in ax[:3]:
        a.axvline(0, color="0.5", lw=0.8)
    ax[3].axvline(90, color="0.5", lw=0.8)
    ax[0].set_yticks(yy, [SYN[k] for k in me])
    ax[0].set_xlabel("b − true (whisker: scatter of one catalogue)")
    ax[1].set_xlabel("N(≥ 5) fitted over true, %")
    ax[2].set_xlabel("N(≥ 7) fitted over true, %")
    ax[2].set_xlim(-60, 80)
    ax[3].set_xlabel("5–95 % interval holds the truth, % of catalogues\n(filled: b, open: N(≥ 7); line: nominal 90 %)")
    ax[0].legend(fontsize=9, loc="upper right")
    fig.suptitle(f"Recovery on synthetic catalogues built like the frozen one ({int(z.n.iloc[0])} per case)", x=0.02, ha="left", fontsize=12)
    fig.tight_layout()
    save(fig, "synthetic_methods")


def run(d, te, F, x, s):
    P.apply()
    fig_fmd(F, x)
    fig_check(x)
    fig_floor(x, s)
    fig_methods(x, s)
    fig_synth()

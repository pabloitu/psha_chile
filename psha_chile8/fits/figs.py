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
from pituplots.style.axes import darkgrid
from scipy import stats

import gr as G
import run as R

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import palette as P

CLASSES = ["interface", "intraslab_shallow", "intraslab_intermediate", "jujuy_nest", "forearc", "arc", "backarc", "patagonia"]
# interface figure: the margin, then the segments north to south; shared y range; the source outlines of the segments
# (model/interface/geometry, the geometry of the interface sources in CURRENT.md)
SEGS = ["interface", "seg4", "seg3", "seg2", "seg1"]
SEG_YLIM = (8e-5, 300)
EDGES = Path(__file__).resolve().parents[1] / "model/interface/geometry/edges_2026-11-16c.json"
SHORT = {"line cut at Mmax (reference)": "line cut at Mmax", "open line": "open line",
         "Aki–Utsu, Mw ≥ 5.0 from 1976": "Aki–Utsu, from 1976", "Ogata–Katsura, Mw ≥ 3.5 from 1976": "joint Mc–b (Ogata–Katsura)",
         "pooled b (shrinkage)": "pooled b", "least squares, cumulative": "least squares"}
# events drawn for reference only, not in the catalogue: unit, Mw, label (1907 Magallanes: Cabello et al. 2025;
# CERESIS-GEM Mw 5.47 +- 0.6; Lomnitz 1970; Pablo, 17 Nov)
REF_EVENTS = {"patagonia": [(5.5, "1907 Magallanes, M 5.5 (reference)")]}
# names of compare.py's synthetic runs
SYN = {"Weichert, open line (reference)": "Weichert, open line", "Weichert, line cut at Mmax": "line cut at Mmax",
       "tapered, corner 9.6": "tapered, corner 9.6", "Aki–Utsu, Mw ≥ 5.0 from 1976": "Aki–Utsu, from 1976",
       "Ogata–Katsura, Mw ≥ 3.5 from 1976": "joint Mc–b (Ogata–Katsura)", "least squares, cumulative": "least squares",
       "Weichert, no magnitude-error weight": "no magnitude-error weight"}


def color(u):
    c = R.UNITS[u]["cls"]
    return P.CLASS_COLOR.get(c) or P.FAMILY_COLOR.get(c, "0.35")


def tag(ax, text, loc="upper right"):
    """Short tag in a corner of a panel (no titles, FIGURE_STYLE.md)."""
    x, ha = (0.97, "right") if "right" in loc else (0.03, "left")
    y, va = (0.97, "top") if "upper" in loc else (0.03, "bottom")
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=9.5, color=P.INK)


def save(fig, name, kind=None):
    """Save to the figures of the run; a paper or supplement figure (kind) also to FIGURES/<kind>/, PNG and PDF."""
    R.FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(R.FIG / f"{name}.png", dpi=300, bbox_inches="tight", pad_inches=0.05)
    if kind:
        (R.PAPER / kind).mkdir(parents=True, exist_ok=True)
        for ext in ("png", "pdf"):
            fig.savefig(R.PAPER / kind / f"{name}.{ext}", dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def tones(u):
    """Cumulative (darker) and incremental (lighter) tone of the class colour of a unit."""
    c = np.array(matplotlib.colors.to_rgb(color(u)))
    return tuple(c * 0.72), tuple(c + (1 - c) * 0.38)


def rcpaper():
    P.apply(size=8)
    matplotlib.rcParams.update({"mathtext.fontset": "custom", "mathtext.rm": "Ubuntu", "mathtext.it": "Ubuntu:italic",
                                "mathtext.bf": "Ubuntu:bold"})


def band(f, x, cum=True, q=(2.5, 97.5)):
    """95 % confidence band of the fit from its bootstrap replicates of b, rate and corner; cumulative, or the rate of a
    0.1 bin centred at x."""
    B = G.boot(f)
    cor = np.broadcast_to(np.asarray(B["corner"], float), np.shape(B["b"])) if B["corner"] is not None else [None] * len(B["b"])
    ys = [G.n_ge(g, x) if cum else inc(g, x) for g in (dict(f, b=b, rate=r, corner=co) for b, r, co in zip(B["b"], B["rate"], cor)
                                                       if np.isfinite(b) and np.isfinite(r))]
    return np.percentile(np.array(ys), q, axis=0)


def inc(f, x):
    """Fitted rate in a 0.1 bin centred at x."""
    return G.n_ge(f, x - G.DM / 2) - np.where(x + G.DM / 2 < f["mmax"] + G.DM / 2, G.n_ge(f, x + G.DM / 2), 0.0)


def fmd(ax, u, f, alt=(), fs=6.5, years=True, name=None, loc="lower left", table=None):
    """One unit: cumulative (filled points, solid line) and incremental (open points, dashed line) in two tones of the
    class colour, each fit with its 95 % confidence band; observed incremental rates with a Poisson 1-sigma interval;
    completeness steps as thin lines with their year. f the tapered fit with its bootstrap; alt further fits drawn
    cumulative as (fit, line style)."""
    cu, ic = tones(u)
    c = G.centres()
    use = f["T"] > 0
    T = np.where(use, f["T"], 1)
    r = np.where(use, f["cnt"] / T, 0.0)
    cum = np.cumsum(r[::-1])[::-1]
    s = use & (f["cnt"] > 0)
    xx = np.arange(5.0, f["mmax"] + 0.05 + 1e-6, 0.01)
    lo, hi = band(f, xx)
    ax.fill_between(xx, lo, hi, color=cu, alpha=0.18, lw=0)
    ax.plot(xx, G.n_ge(f, xx), color=cu, lw=1.0)
    for g, ls in alt:
        y = G.n_ge(g, xx)
        ax.plot(xx[y > 0], y[y > 0], color=cu, lw=0.7, ls=ls)
    xi = np.arange(4.95, f["mmax"] + 1e-6, 0.01)
    lo, hi = band(f, xi, cum=False)
    ax.fill_between(xi, lo, hi, color=ic, alpha=0.2, lw=0)
    ax.plot(xi, inc(f, xi), color=ic, lw=0.8, ls=(0, (4, 2)))
    ax.plot(c[s], cum[s], "o", ms=2.8, color=cu, mec="white", mew=0.35, zorder=4)
    n = f["cnt"][s]
    elo = stats.chi2.ppf(0.16, 2 * n) / 2 / T[s]
    ehi = stats.chi2.ppf(0.84, 2 * (n + 1)) / 2 / T[s]
    ax.vlines(c[s], elo, ehi, color=ic, lw=0.5, alpha=0.6, zorder=3)
    ax.plot(c[s], r[s], "o", ms=2.4, mfc="white", mec=ic, mew=0.6, zorder=4)
    for mf, y in R.table_of(u, table):
        if mf <= xx[-1]:
            ax.axvline(mf - 0.05, color="0.6", lw=0.4, zorder=0)
            if years:
                ax.text(mf - 0.02, 0.985, str(y), transform=ax.get_xaxis_transform(), fontsize=5, color="0.4", va="top", ha="left", rotation=90)
    for mw, lab in REF_EVENTS.get(u, []):
        ax.plot(mw, 0.06, "v", ms=5, mfc="none", mec=P.INK, mew=0.8, transform=ax.get_xaxis_transform(), zorder=4)
        ax.text(mw + 0.12, 0.06, lab, transform=ax.get_xaxis_transform(), fontsize=5, color="0.25", va="center")
    q = G.boot(f)
    fam = " (family)" if R.UNITS[u].get("b_from") else ""
    name = name or R.name(u)[0].upper() + R.name(u)[1:]
    x, ha = (0.96, "right") if "right" in loc else (0.04, "left")
    y, va = (0.80, "top") if "upper" in loc else (0.04, "bottom")
    ax.text(x, y, f"{name}\n$b = {f['b']:.2f} \\pm {np.nanstd(q['b']):.2f}${fam}\n"
            f"$M_\\mathrm{{max}} = {f['mmax'] - 0.05:.1f}$", transform=ax.transAxes, ha=ha, va=va, fontsize=fs, color=P.INK, linespacing=1.4)
    ax.set_yscale("log")
    ax.set_xlim(4.9, f["mmax"] + 0.15)
    darkgrid(ax, major_length=2, minor_length=1)
    ax.tick_params(labelsize=fs)
    return cum[s].max(), float(np.nanmin(np.r_[elo[elo > 0], cum[s]]))


def handles(u, alt=()):
    """Legend of fmd: line and marker together per curve."""
    from matplotlib.legend_handler import HandlerTuple
    cu, ic = tones(u)
    h = [(plt.Line2D([], [], color=cu, lw=1.0), plt.Line2D([], [], ls="", marker="o", ms=2.8, color=cu, mec="white", mew=0.35)),
         (plt.Line2D([], [], color=ic, lw=0.8, ls=(0, (4, 2))), plt.Line2D([], [], ls="", marker="o", ms=2.4, mfc="white", mec=ic, mew=0.6)),
         plt.Rectangle((0, 0), 1, 1, color="0.5", alpha=0.3, lw=0), plt.Line2D([], [], color="0.4", lw=0.6),
         plt.Line2D([], [], color="0.6", lw=0.4, marker="|", ms=8, mew=0.5, ls="")]
    l = ["Cumulative", "Incremental", "95 % confidence", r"Poisson $1\sigma$", "Completeness year"]
    for lab, ls in alt:
        h.append(plt.Line2D([], [], color="0.3", lw=0.7, ls=ls))
        l.append(lab)
    return h, l, dict(handler_map={tuple: HandlerTuple(ndivide=None, pad=0.6)})


def segmap(ax):
    """The interface segments as the outlines of their sources (top edge at 10 km and bottom edge at 50 km of the
    complex-fault surfaces on the Slab2 top)."""
    import json
    from plots import maps as M
    g = json.loads(EDGES.read_text())
    tn = ["#9dc3e0", "#5b9bd5"]
    for i, u in enumerate(SEGS[1:]):
        e = np.array(g[u])
        ax.add_patch(plt.Polygon(np.r_[e[0][:, :2], e[-1][::-1, :2]], closed=True, transform=M.PC, fc=tn[i % 2], ec=tones("interface")[0],
                                 lw=0.4, alpha=0.85, zorder=3))
        ax.text(float(e[-1][:, 0].max()) + 0.4, e[0][:, 1].mean(), R.name(u).replace("interface, ", ""), transform=M.PC, fontsize=5.5,
                rotation=90, ha="left", va="center", color=P.INK, zorder=5)


def fig_fmd(F, x):
    """Frequency-magnitude distributions per class (fmd_classes) and of the interface margin and segments with a map of
    the segments (fmd_interface_segments), page width."""
    from matplotlib.gridspec import GridSpec
    from cartopy.mpl.gridliner import Gridliner
    from plots import maps as M
    rcpaper()
    alt = [("Cut at $M_\\mathrm{max}$", ":")]
    fig, ax = plt.subplots(2, 4, figsize=(6.9, 3.9))
    for a, u in zip(ax.ravel(), CLASSES):
        top, low = fmd(a, u, F["taper"][0][u], [(F["trunc"][0][u], ":")], loc="upper right")
        a.set_ylim(max(1e-5, 0.3 * low), 30 * top)
        a.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))
    for a in ax[:, 0]:
        a.set_ylabel("Annual rate", fontsize=7)
    for a in ax[-1]:
        a.set_xlabel(r"$M_\mathrm{w}$", fontsize=7)
    fig.tight_layout(rect=(0, 0.07, 1, 1), pad=0.4, h_pad=0.6, w_pad=0.6)
    h, l, kw = handles("intraslab_intermediate", alt)
    fig.legend(h, l, loc="lower center", ncol=len(h), fontsize=6, frameon=False, handlelength=2.8, bbox_to_anchor=(0.5, 0), **kw)
    save(fig, "fmd_classes", "fits")
    fig = plt.figure(figsize=(6.9, 4.9))
    gs = GridSpec(2, 3, figure=fig, wspace=0.08, hspace=0.12)
    axs = []
    for k, u in enumerate(SEGS):
        a = fig.add_subplot(gs[k // 3, k % 3], sharey=axs[0] if axs else None)
        fmd(a, u, F["taper"][0][u], name="Whole margin" if u == "interface" else R.name(u).replace("interface, ", ""))
        a.set_ylim(*SEG_YLIM)
        a.set_xlim(4.9, 9.85)
        a.set_xticks([5, 6, 7, 8, 9])
        a.tick_params(labelleft=not k % 3, labelbottom=k >= 2)
        if not k % 3:
            a.set_ylabel("Annual rate", fontsize=7)
        if k >= 2:
            a.set_xlabel(r"$M_\mathrm{w}$", fontsize=7)
        axs.append(a)
    sub = gs[1, 2].subgridspec(1, 2, width_ratios=[1.25, 1], wspace=0.05)
    M.DLON = 4.0
    m = M.domain_map(fig, (sub[1],), [-76.0, -68.0, -46.0, -16.8], labels="right", dlat=5.0, fs=5)
    segmap(m)
    for gl in [q for q in m.artists if isinstance(q, Gridliner)]:
        gl.bottom_labels = False
        gl.ylabel_style = dict(size=5.5, color="0.3")
    lg = fig.add_subplot(sub[0])
    lg.axis("off")
    h, l, kw = handles("interface")
    lg.legend(h, l, loc="lower left", fontsize=6, frameon=False, handlelength=2.8, borderaxespad=0.0, **kw)
    save(fig, "fmd_interface_segments", "fits")
    P.apply()


def fig_check(x):
    x = x[x["shape"] == "taper"].reset_index(drop=True)
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.6), sharey=True)
    yy = np.arange(len(x))[::-1]
    for a, M in zip(ax, (7, 8)):
        e, o = x[f"exp{M}"].to_numpy(), x[f"obs{M}"].to_numpy()
        ph = x[f"phi{M}"].to_numpy() if f"phi{M}" in x else np.ones(len(x))
        lo, hi = np.array([G.band(a_, p_) for a_, p_ in zip(e, ph)]).T
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
        darkgrid(a)
    ax[0].set_yticks(yy, x.name)
    ax[0].plot([], [], "|", color="0.15", ms=12, mew=1.5, label="fitted")
    ax[0].plot([], [], color="0.6", lw=5, alpha=0.6, label="5–95 % of the fitted number, clusters drawn whole")
    ax[0].plot([], [], "o", color="0.4", ms=7, label="observed (weighted count)")
    ax[0].plot([], [], "o", color="0.4", ms=7, mec="k", mew=1.4, label="observed, outside the band")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.legend(*ax[0].get_legend_handles_labels(), loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0))
    save(fig, "large_event_check")


def fig_floor(x, s):
    x = x[x["shape"] == "trunc"]
    fig, ax = plt.subplots(2, 6, figsize=(19, 6.6), sharex=True, sharey=True)
    a_ = s[s.events == "all"]
    for a, u in zip(ax.ravel(), [q for q in R.ORDER if q != "patagonia"]):
        r = x[x.unit == u].iloc[0]
        q = a_[(a_.unit == u) & a_.method.str.contains("floor")]
        a.axhspan(r.b - r.b_sd, r.b + r.b_sd, color="0.2", alpha=0.12, lw=0)
        if len(q):
            a.plot(np.r_[5.0, q.floor], np.r_[r.b, q.b], "-o", ms=4, color=color(u))
        else:
            a.plot(5.0, r.b, "o", ms=4, color=color(u))
            a.text(0.5, 0.1, "b of the crustal family", transform=a.transAxes, ha="center", fontsize=9, color="0.4")
        darkgrid(a)
        tag(a, R.name(u))
    ax[0, 0].set_ylim(0.6, 1.6)
    for a in ax[:, 0]:
        a.set_ylabel("b")
    for a in ax[-1]:
        a.set_xlabel("lowest magnitude fitted")
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
    for a in ax:
        darkgrid(a)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.legend(*ax[0].get_legend_handles_labels(), loc="lower center", ncol=len(me) + 1, bbox_to_anchor=(0.5, 0))
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
    for a in ax:
        darkgrid(a)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.legend(*ax[0].get_legend_handles_labels(), loc="lower center", ncol=len(sc), bbox_to_anchor=(0.5, 0))
    save(fig, "synthetic_methods")


def fig_mc(mc, te):
    """Mc(t) of the whole margin and of each segment (moving windows of table.NWIN events, bootstrap 16-84 %), the steps
    measured from each series, and the instrumental steps of the fits (from the fit floor)."""
    import table as TB
    rcpaper()
    series = [("margin", "Whole margin", "interface")] + [(k, f"{k[0].upper() + k[1:]}, {abs(b):g}–{abs(a):g}° S", u)
                                                          for u, k in R.SEG_MC.items() for a, b in [TB.SEG[k]]][::-1]
    fig, ax = plt.subplots(1, 5, figsize=(6.9, 2.3), sharey=True)
    cu, ic = tones("interface")
    for a, (k, name, u) in zip(ax, series):
        q = mc[mc.segment == k].sort_values("t")
        a.fill_between(q.t, q.lo, q.hi, color=ic, alpha=0.35, lw=0, step="mid")
        a.plot(q.t, q.mc, color=cu, lw=0.5, drawstyle="steps-mid")
        st = TB.envelope({k: TB.steps_series(q, te)}, te)
        z = sorted(st, key=lambda v: v[1])
        a.step([z[0][1]] + [y for _, y in z[1:]] + [te], [z[0][0]] + [mf for mf, _ in z[1:]] + [z[-1][0]], where="post", color=P.INK, lw=0.9)
        fit = [x for x in R.table_of(u if k != "margin" else "interface") if x[1] >= TB.HIST_FROM]
        z = sorted(fit, key=lambda v: v[1])
        a.step([z[0][1]] + [y for _, y in z[1:]] + [te], [z[0][0]] + [mf for mf, _ in z[1:]] + [z[-1][0]], where="post", color=P.INK,
               lw=0.8, ls=(0, (3, 2)))
        a.text(0.96, 0.96, name, transform=a.transAxes, ha="right", va="top", fontsize=6, color=P.INK)
        a.set_xlim(1964, te)
        a.set_xticks([1970, 1990, 2010])
        a.set_xlabel("Year", fontsize=7)
        a.tick_params(labelsize=6)
        darkgrid(a, major_length=2, minor_length=1)
    ax[0].set_ylim(3.4, 5.8)
    ax[0].set_ylabel(r"$M_\mathrm{c}$", fontsize=7)
    h = [(plt.Rectangle((0, 0), 1, 1, color=ic, alpha=0.35, lw=0), plt.Line2D([], [], color=cu, lw=0.5)), plt.Line2D([], [], color=P.INK, lw=0.9),
         plt.Line2D([], [], color=P.INK, lw=0.8, ls=(0, (3, 2)))]
    from matplotlib.legend_handler import HandlerTuple
    fig.tight_layout(rect=(0, 0.1, 1, 1), pad=0.4, w_pad=0.3)
    fig.legend(h, [r"$M_\mathrm{c}(t)$, bootstrap 16–84 %", "Measured steps", "Fits, from $M_\\mathrm{w}$ 5.0"], loc="lower center", ncol=3,
               fontsize=6, frameon=False, handlelength=2.6, handler_map={tuple: HandlerTuple(ndivide=1)})
    save(fig, "mc_time", "completeness")
    P.apply()


def fig_historical(d, te):
    """Historical completeness: per class (Mw 7.0-7.4, 7.5-8.4, >= 8.5; all events of the domain, no weights) the
    cumulative number in time (the slope method, Hakimhashemi and Grünthal 2012, p. 2530), the step of the table, the
    years of the two published checks and the rate from the step."""
    import table as TB
    rcpaper()
    m, t = d.mw.to_numpy(), d.t.to_numpy()
    st = sorted(q for q in R.TABLE if q[1] < TB.HIST_FROM)
    cls = [(mf, (st[i + 1][0] if i + 1 < len(st) else 10.0), y) for i, (mf, y) in enumerate(st)]
    fig, ax = plt.subplots(1, len(cls), figsize=(6.9, 2.5))
    col = tones("interface")[0]
    for a, (lo, hi, y0) in zip(ax, cls):
        tt = np.sort(t[(m >= lo - 0.05) & (m < hi - 0.05)])
        a.step(np.r_[1500, tt, te], np.r_[0, np.arange(1, tt.size + 1), tt.size], where="post", color=col, lw=1.0)
        rate = (tt >= y0).sum() / (te - y0)
        n0 = (tt < y0).sum()
        a.plot([y0, te], [n0, n0 + rate * (te - y0)], color=P.INK, lw=0.8, ls=(0, (4, 2)))
        a.axvline(y0, color=P.INK, lw=0.7)
        hg, al = TB.hg2012(tt), TB.albarello2001(tt, te)
        for v, ls in ((hg, ":"), (al, "-.")):
            if np.isfinite(v):
                a.axvline(v, color="0.45", lw=0.6, ls=ls)
        lab = f"$M_\\mathrm{{w}}$ {lo:.1f}–{hi - 0.1:.1f}" if hi < 10 else f"$M_\\mathrm{{w}} \\geq$ {lo:.1f}"
        hgt = f"{hg:.0f}" if np.isfinite(hg) else "too few events"
        a.text(0.04, 0.96, f"{lab}\ntable {y0}; H&G {hgt}; Albarello {al:.0f}\n{tt.size} events, {rate * 100:.1f} per century from {y0}",
               transform=a.transAxes, ha="left", va="top", fontsize=6, color=P.INK, linespacing=1.4)
        a.set_xlim(1500, te)
        a.set_xlabel("Year", fontsize=7)
        a.tick_params(labelsize=6.5)
        darkgrid(a, major_length=2, minor_length=1)
    ax[0].set_ylabel("Cumulative number", fontsize=7)
    h = [plt.Line2D([], [], color=col, lw=1.0), plt.Line2D([], [], color=P.INK, lw=0.8, ls=(0, (4, 2))),
         plt.Line2D([], [], color=P.INK, lw=0.7), plt.Line2D([], [], color="0.45", lw=0.6, ls=":"), plt.Line2D([], [], color="0.45", lw=0.6, ls="-.")]
    l = ["Observed", "Rate from the completeness year", "Completeness year", "Hakimhashemi and Grünthal (2012)", "Albarello et al. (2001)"]
    fig.tight_layout(rect=(0, 0.12, 1, 1), pad=0.4, w_pad=0.6)
    fig.legend(h, l, loc="lower center", ncol=5, fontsize=6, frameon=False, handlelength=2.4)
    save(fig, "historical", "completeness")
    P.apply()


def run(d, te, F, x, s):
    P.apply()
    fig_fmd(F, x)
    fig_check(x)
    fig_floor(x, s)
    fig_methods(x, s)
    fig_synth()

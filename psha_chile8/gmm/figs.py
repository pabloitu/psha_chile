"""Figures of task GM1, called by run.py: data, z histograms, residual trends, score summary, τ and φ."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

import residuals as R
import screen as C

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import palette as P

FIG, TAB = HERE / "figures", HERE / "tables"
DATE = "2026-11-15"
CLS = {"interface": ("interface", P.CLASS_COLOR["interface"]),
       "inslab": ("in-slab", P.CLASS_COLOR["intraslab_intermediate"])}
IMT_C = dict(zip(R.IMT_PERIOD, P.SERIES[:3]))
XLAB = {"mw": "Mw", "rrup": "Rrup (km)", "hypo_depth": "hypocentral depth (km)", "vs30": "Vs30 (m/s)"}


def save(fig, name):
    fig.savefig(FIG / f"{name}.png", dpi=150, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def gname(k):
    return C.NAME[k] + (" *" if k in C.TREE else "")


def data(d):
    fig, ax = plt.subplots(2, 2, figsize=(11, 8.5))
    for a, (k, (lab, col)) in zip(ax[0], CLS.items()):
        g = d[d.cls == k]
        m = g.vs30measured
        a.scatter(g.rrup[~m], g.mw[~m], s=9, facecolor="none", edgecolor=col, lw=0.6, alpha=0.6, label="Vs30 inferred")
        a.scatter(g.rrup[m], g.mw[m], s=9, color=col, alpha=0.7, lw=0, label="Vs30 measured")
        a.set(xscale="log", xlim=(5, 320), xlabel="Rrup (km)", ylabel="Mw",
              title=f"{lab}: {g.event_id.nunique()} events, {len(g)} records")
        a.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="none", markerscale=2)
    ev = d.drop_duplicates("event_id")
    for k, (lab, col) in CLS.items():
        ax[1, 0].hist(ev[ev.cls == k].hypo_depth, bins=np.arange(0, 200, 5), color=col, alpha=0.6, label=lab)
    ax[1, 0].set(xlabel="hypocentral depth (km)", ylabel="events", title="Depth")
    ax[1, 0].legend()
    st = d.drop_duplicates("station")
    bins = np.arange(100, 2000, 50)
    ax[1, 1].hist([st.vs30[st.vs30measured], st.vs30[~st.vs30measured]], bins=bins, stacked=True,
                  color=["0.25", "0.7"], label=["measured", "inferred"])
    ax[1, 1].set(xlabel="Vs30 (m/s)", ylabel="stations", title=f"Vs30 of the {len(st)} stations")
    ax[1, 1].legend()
    fig.tight_layout()
    save(fig, "data")


def zhist(res, cls):
    gm = list(dict.fromkeys(res.gmm))
    x = np.linspace(-5, 5, 200)
    for imt, f in res.groupby("imt", sort=False):
        fig, ax = plt.subplots(4, 4, figsize=(13, 11), sharex=True, sharey=True)
        for a, k in zip(ax.flat, gm):
            z = f[f.gmm == k].z
            a.hist(z, bins=np.arange(-5, 5.01, 0.25), density=True, color=CLS[cls][1], alpha=0.55)
            a.plot(x, norm.pdf(x), color="0.15", lw=1)
            a.set_title(gname(k), fontsize=10)
            a.text(0.03, 0.95, f"mean {z.mean():.2f}\nsd {z.std():.2f}", transform=a.transAxes, va="top", fontsize=9)
        for a in ax.flat[len(gm):]:
            a.axis("off")
        for a in ax[-1]:
            a.set_xlabel("z = r / σ")
        fig.suptitle(f"Normalised residuals, {CLS[cls][0]}, {imt} (* current tree)", x=0.02, ha="left")
        fig.tight_layout()
        save(fig, f"z_{cls}_{imt.replace('(', '').replace(')', '')}")


def trends(res, d, cls, bins):
    gm = list(dict.fromkeys(res.gmm))
    rec = d.set_index("record_id")
    for imt, f in res.groupby("imt", sort=False):
        fig, ax = plt.subplots(len(gm), 4, figsize=(13, 1.55 * len(gm)), sharex="col", sharey=True)
        for i, k in enumerate(gm):
            g = f[f.gmm == k].join(rec[["mw", "hypo_depth", "rrup", "vs30"]], on="record_id")
            sp = g.db.notna().all()
            ev = g.groupby("event_id").agg(mw=("mw", "first"), hypo_depth=("hypo_depth", "first"),
                                          y=("db", "first") if sp else ("r", "mean"))
            for j, (x, xs, ys) in enumerate([("mw", ev.mw, ev.y), ("hypo_depth", ev.hypo_depth, ev.y),
                                             ("rrup", g.rrup, g.dw if sp else g.r), ("vs30", g.vs30, g.dw if sp else g.r)]):
                a = ax[i, j]
                a.scatter(xs, ys, s=2, color="0.6", lw=0, alpha=0.5, rasterized=True)
                b = bins[(bins.gmm == k) & (bins.imt == imt) & (bins["var"] == x)]
                a.errorbar(b.x, b["mean"], yerr=b.se, fmt="o-", ms=3, lw=1, color=CLS[cls][1])
                a.axhline(0, color="0.2", lw=0.6)
                if x in ("rrup", "vs30"):
                    a.set_xscale("log")
                if i == 0:
                    a.set_title(("event term vs " if j < 2 else "within-event vs ") + XLAB[x].split(" (")[0], fontsize=10)
                if i == len(gm) - 1:
                    a.set_xlabel(XLAB[x])
            ax[i, 0].set_ylabel(gname(k), fontsize=8, rotation=0, ha="right", va="center")
        ax[0, 0].set_ylim(-3, 3)
        fig.suptitle(f"Residual trends, {CLS[cls][0]}, {imt} (ln units; δB and δW, or r and event mean of r for "
                     f"total-σ models; * current tree)", x=0.02, ha="left", fontsize=11)
        fig.tight_layout(rect=(0, 0, 1, 0.985))
        save(fig, f"trends_{cls}_{imt.replace('(', '').replace(')', '')}")


def summary(sc):
    sc = sc[sc.records == "common"]
    fig, ax = plt.subplots(2, 2, figsize=(13, 10), sharey="row")
    for j, cls in enumerate(CLS):
        s = sc[sc.cls == cls]
        gm = list(dict.fromkeys(s.gmm))
        y = np.arange(len(gm))[::-1]
        for i, (v, lab) in enumerate([("llh", "LLH"), ("edr", "EDR")]):
            a = ax[i, j]
            hi = {"llh": 4.0, "edr": 2.4}[v]
            for m, imt in enumerate(R.IMT_PERIOD):
                t = s[s.imt == imt].set_index("gmm").loc[gm]
                yy = y + (m - 1) * 0.27
                a.errorbar(t[v], yy, xerr=[t[v] - t[f"{v}_16"], t[f"{v}_84"] - t[v]], fmt="o", ms=4,
                           color=IMT_C[imt], lw=1, label=imt)
                for x_, y_ in zip(t[v], yy):
                    if x_ > hi:
                        a.annotate(f"{x_:.1f} →", (hi, y_), ha="right", va="center", fontsize=7, color=IMT_C[imt])
            a.set_xlim(right=hi)
            a.set_yticks(y, [gname(k) for k in gm], fontsize=9)
            for tl, k in zip(a.get_yticklabels(), gm):
                tl.set_fontweight("bold" if k in C.TREE else "normal")
            a.set(xlabel=lab + (" (bits)" if v == "llh" else " (ln units)"), title=f"{lab}, {CLS[cls][0]}")
            if v == "llh":
                a.axvline(np.log2(np.sqrt(2 * np.pi * np.e)), color="0.6", lw=0.8, ls=":")
    ax[0, 1].legend(loc="upper right", frameon=True, facecolor="white", edgecolor="none")
    fig.text(0.01, 0.005, "Bars: 16–84 % of 200 event resamples; bold and *: current tree; dotted: LLH of a perfect "
             "model with σ = 1", fontsize=9)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    save(fig, "scores")


def tauphi(sm):
    s = sm[sm.tau_model.notna()]
    fig, ax = plt.subplots(1, 2, figsize=(11, 5.3))
    mk = dict(zip(R.IMT_PERIOD, "o^s"))
    for a, v, lab in [(ax[0], "tau", "τ"), (ax[1], "phi", "φ")]:
        for cls, (cl, col) in CLS.items():
            for imt in R.IMT_PERIOD:
                t = s[(s.cls == cls) & (s.imt == imt)]
                a.scatter(t[f"{v}_model"], t[f"{v}_data"], marker=mk[imt], color=col, s=28, alpha=0.8,
                          label=f"{cl}, {imt}")
        a.plot([0.2, 1.3], [0.2, 1.3], color="0.4", lw=0.8)
        a.set(xlim=(0.2, 1.3), ylim=(0.2, 1.3), xlabel=f"{lab} of the model (ln units)",
              ylabel=f"{lab} from the data, maximum likelihood", title=lab)
        a.set_aspect("equal")
    ax[1].legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    save(fig, "tau_phi")


def main(d, allres):
    P.apply()
    FIG.mkdir(exist_ok=True)
    data(d)
    bins = pd.read_csv(TAB / f"trends_bins_{DATE}.csv")
    import run
    for cls, res in allres.items():
        com = run.common(res)
        zhist(com, cls)
        trends(com, d[d.cls == cls], cls, bins[bins.cls == cls])
    summary(pd.read_csv(TAB / f"scores_{DATE}.csv"))
    tauphi(pd.read_csv(TAB / f"residuals_summary_{DATE}.csv"))

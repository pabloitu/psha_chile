# Trial tornado for one city: horizontal bars, largest change of the total at the top. The GMM axes are one per GMM
# set (GMM-1R, GMM-FIT, GMM-MASCSN, GMM-GEM): the line spans the single models of the set (each model's curve read
# from the realizations of the set job), a diamond marks the set as a whole. Thick line = total, pale line = family
# alone, dots = rows; labels above the TOP axes, spread apart with leader lines. Writes hazard/out/tornado_trial/

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pituplots.style.axes import darkgrid

import palette
from hazard import combine, post
from hazard import config as hc

# settings
CITY = "Iquique"
OUT = hc.OUT / "tornado_trial"
POE = 0.002105
MIN, LIM = 5.0, 100.0
TOP = 10
NCOL = 18
FAM = {"interface": ("if", "Subduction Interface"), "inslab": ("is", "Subduction IntraSlab"),
       "crustal": ("cr", "Active Shallow Crust")}
NAME = {"interface": "interface", "inslab": "in-slab", "crustal": "crustal"}
COL = {"interface": palette.CLASS_COLOR["interface"], "inslab": palette.CLASS_COLOR["intraslab_intermediate"],
       "crustal": palette.CLASS_COLOR["forearc"]}
SETS = {"GMM-1R": "ref", "GMM-FIT": "set_gm1top4", "GMM-MASCSN": "set_mascsn26", "GMM-GEM": "set_gem_sam"}
GSIM = {"AbrahamsonGulerce2020": "AG20", "ParkerEtAl2020": "Parker", "KuehnEtAl2020": "Kuehn",
        "MontalvaEtAl2017": "Montalva17", "MontalvaEtAl2016": "Montalva16", "ZhaoEtAl2016": "Zhao16",
        "ZhaoEtAl2006": "Zhao06", "YoungsEtAl1997": "Youngs97", "IdiniEtAl2017": "Idini17",
        "AbrahamsonEtAl2015SInterHigh": "BCHydro high", "AbrahamsonEtAl2015": "BCHydro",
        "AbrahamsonEtAl2014": "ASK14", "BooreEtAl2014": "BSSA14", "CampbellBozorgnia2014": "CB14",
        "ChiouYoungs2014": "CY14", "ArtetaEtAl2023_Vs30": "Arteta23", "AkkarEtAlRjb2014": "Akkar14",
        "BindiEtAl2014Rjb": "Bindi14"}


def short(g):
    c = g.split("]")[0].strip("[")
    for k in sorted(GSIM, key=len, reverse=True):
        if c.startswith(k):
            return GSIM[k]
    return c


def gmm_rows(s):
    """Rows of the GMM-set axes at site index s: every model of every set, and each set as a whole."""
    cache = {}

    def load(j):
        if j not in cache:
            cache[j] = post.load(j)
        return cache[j]
    ref = {f: post.mean(load(f"t_{a}_ref"))[s] for f, (a, _) in FAM.items()}
    lv = load("t_if_ref")["imtls"]["PGA"]
    rt = {f: combine.rate(v) for f, v in ref.items()}
    tot0 = post.iml(1 - np.exp(-sum(rt.values())), lv, POE)
    rows = []
    for f, (a, trt) in FAM.items():
        oth = sum(rt[x] for x in FAM if x != f)
        x0 = post.iml(ref[f], lv, POE)
        for k, j in SETS.items():
            if f == "crustal" and k == "GMM-FIT":
                continue
            r = load(f"t_{a}_{j}")
            c = r["curves"][s, :, 0, :]
            curves = [("set", k, r["w"] @ c)]
            for g in dict.fromkeys(x[trt] for x in r["gmm"]):
                i = np.array([x[trt] == g for x in r["gmm"]])
                curves.append(("model", short(g), r["w"][i] @ c[i] / r["w"][i].sum()))
            for kind, lab, cv in curves:
                x, y = post.iml(cv, lv, POE), post.iml(1 - np.exp(-(combine.rate(cv) + oth)), lv, POE)
                rows.append({"family": f, "axis": k, "row": lab, "kind": kind,
                             "family_pct": 100 * (x / x0 - 1), "combined_pct": 100 * (y / tot0 - 1)})
    return pd.DataFrame(rows)


def clip(v):
    return float(np.clip(v, -LIM, LIM)) if np.isfinite(v) else 0.0


def labels(ax, xs, labs, y, lim):
    """Labels above the row at y, spread so they do not overlap, with leader lines to their dots."""
    o = np.argsort(xs)
    xs, labs = np.asarray(xs)[o], [labs[i] for i in o]
    ch = 2 * lim / 150
    p = []
    for i, (x, l) in enumerate(zip(xs, labs)):
        w = ch * len(l)
        p.append(x if not p else max(x, p[-1] + ch * (len(labs[i - 1]) + len(l)) / 2 + ch * 2))
    over = p[-1] + ch * len(labs[-1]) / 2 - lim
    if over > 0:
        p = [v - over for v in p]
    for x, px, l in zip(xs, p, labs):
        ax.annotate(l, (x, y), xytext=(px, y + 0.42), textcoords="data", ha="center", va="bottom", fontsize=7.5,
                    color="0.15", arrowprops=dict(arrowstyle="-", color="0.45", lw=0.6, shrinkA=0, shrinkB=2))


def main():
    palette.apply()
    OUT.mkdir(parents=True, exist_ok=True)
    s = list(hc.CITIES).index(CITY)
    t = pd.read_csv(hc.OUT / "tornado" / "tornado.csv")
    t = t[(t.site == CITY) & ~t.axis.isin(["GMM set", "GMM-1R models"])].assign(kind="row")
    g = pd.concat([t[["family", "axis", "row", "kind", "family_pct", "combined_pct"]], gmm_rows(s)], ignore_index=True)
    g.to_csv(OUT / f"{CITY.replace(' ', '_')}.csv", index=False)
    ax_ = []
    for (f, a), q in g.groupby(["family", "axis"], sort=False):
        r = q[q.kind != "set"]
        ax_.append({"family": f, "axis": a, "lo": min(r.combined_pct.min(), 0), "hi": max(r.combined_pct.max(), 0),
                    "flo": min(r.family_pct.min(), 0), "fhi": max(r.family_pct.max(), 0),
                    "amax": np.nanmax(np.abs(q.combined_pct))})
    b = pd.DataFrame(ax_).sort_values("amax")
    n = len(b)
    lim = min(LIM, np.nanmax(np.abs(b[["lo", "hi", "flo", "fhi"]].to_numpy())) * 1.1 + 3)

    fig, ax = plt.subplots(figsize=(12, 0.62 * n + 1.8), layout="constrained")
    for i, (_, r) in enumerate(b.iterrows()):
        c = COL[r.family]
        ax.plot([clip(r.flo), clip(r.fhi)], [i, i], color=c, lw=3, alpha=0.35, solid_capstyle="butt")
        ax.plot([clip(r.lo), clip(r.hi)], [i, i], color=c, lw=8, solid_capstyle="butt")
        q = g[(g.family == r.family) & (g.axis == r.axis)]
        m = q[q.kind != "set"]
        ax.plot([clip(v) for v in m.combined_pct], [i] * len(m), "o", ms=4, color="k", zorder=5)
        st = q[q.kind == "set"]
        ax.plot([clip(v) for v in st.combined_pct], [i] * len(st), "D", ms=7, mfc="white", mec="k", mew=1.2,
                zorder=6)
        if i >= n - TOP and len(m):
            labels(ax, [clip(v) for v in m.combined_pct], list(m.row), i, lim)
    ax.axvline(0, color="k", lw=0.8)
    ax.axvspan(-MIN, MIN, color="0.5", alpha=0.15, lw=0)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-0.7, n + 0.2)
    ax.set_yticks(range(n))
    ax.set_yticklabels([f"{NAME[f]}: {a}" for f, a in zip(b.family, b.axis)])
    ax.set_xlabel("change of PGA 475 yr (%)")
    darkgrid(ax)
    ax.text(0.01, 0.998, CITY, transform=ax.transAxes, ha="left", va="top", fontsize=13)
    hnd = [Line2D([], [], color=COL[f], lw=8, label=NAME[f]) for f in COL] + [
        Line2D([], [], color="0.4", lw=3, alpha=0.35, label="family alone"),
        Line2D([], [], marker="o", color="k", ls="", ms=4, label="rows / single GMMs"),
        Line2D([], [], marker="D", mfc="white", mec="k", ls="", ms=7, label="GMM set as a whole")]
    fig.legend(handles=hnd, loc="outside lower center", ncol=6, frameon=False, fontsize=9)
    fig.savefig(OUT / f"{CITY.replace(' ', '_')}.png", dpi=170, facecolor="white")
    plt.close(fig)

    # vertical bars: axes along x, largest at the left
    b2 = b.iloc[::-1].reset_index(drop=True).head(NCOL)
    m2 = len(b2)
    fig, ax = plt.subplots(figsize=(1.05 * m2 + 2.5, 8.5), layout="constrained")
    for i, (_, r) in enumerate(b2.iterrows()):
        c = COL[r.family]
        ax.plot([i, i], [clip(r.flo), clip(r.fhi)], color=c, lw=3, alpha=0.35, solid_capstyle="butt")
        ax.plot([i, i], [clip(r.lo), clip(r.hi)], color=c, lw=10, solid_capstyle="butt")
        q = g[(g.family == r.family) & (g.axis == r.axis)]
        m = q[q.kind != "set"]
        ax.plot([i] * len(m), [clip(v) for v in m.combined_pct], "o", ms=4.5, color="k", zorder=5)
        st = q[q.kind == "set"]
        ax.plot([i] * len(st), [clip(v) for v in st.combined_pct], "D", ms=8, mfc="white", mec="k", mew=1.2,
                zorder=6)
        if len(m) and i < TOP:
            ys = np.array([clip(v) for v in m.combined_pct])
            o = np.argsort(ys)
            gap = 2 * lim / 45
            p = []
            for y in ys[o]:
                p.append(y if not p else max(y, p[-1] + gap))
            for y, py, l in zip(ys[o], p, [list(m.row)[k] for k in o]):
                ax.annotate(l, (i, y), xytext=(i + 0.22, py), textcoords="data", ha="left", va="center",
                            fontsize=7.5, color="0.15",
                            arrowprops=dict(arrowstyle="-", color="0.45", lw=0.6, shrinkA=0, shrinkB=2))
    ax.axhline(0, color="k", lw=0.8)
    ax.axhspan(-MIN, MIN, color="0.5", alpha=0.15, lw=0)
    ax.set_ylim(-lim, lim)
    ax.set_xlim(-0.6, m2 - 0.2)
    ax.set_xticks(range(m2))
    ax.set_xticklabels([f"{NAME[f]}: {a}" for f, a in zip(b2.family, b2.axis)], rotation=50, ha="right")
    ax.set_ylabel("change of PGA 475 yr (%)")
    darkgrid(ax)
    ax.text(0.005, 0.99, CITY, transform=ax.transAxes, ha="left", va="top", fontsize=13)
    fig.legend(handles=hnd, loc="outside lower center", ncol=6, frameon=False, fontsize=9)
    fig.savefig(OUT / f"{CITY.replace(' ', '_')}_columns.png", dpi=170, facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

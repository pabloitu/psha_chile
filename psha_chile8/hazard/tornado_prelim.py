# Preliminary tornado figure per city (slides for the collaborators, 17 Nov; more branch levels will follow): vertical
# bars, the NCOL axes with the largest change of the total PGA 475 yr from the left. The GMM axes are one per GMM set
# (GMM-1R, GMM-FIT, GMM-CSN, GMM-GEM): the bar spans the single models of the set (each model's curve read from
# the realizations of the set job). Thick bar = change of the total hazard, pale bar = change within the tectonic
# setting of the axis (legend: all tectonic settings / within tectonic setting), dots = branches (the reference at 0), labelled on every axis shown with leader lines; the hollow
# diamond is the average of the axis (curves of its branches averaged, equal weights; for a GMM axis the set). Axes that move the total
# by less than KEEP % are left out; a row whose total falls below the lowest level (LOW g) is drawn at that bound.
# Reads hazard/out/tornado/tornado.csv (hazard/tornado_final.py) and the set jobs; writes hazard/out/tornado_prelim/

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
CITIES = list(hc.CITIES)
OUT = hc.OUT / "tornado_prelim"
POE = 0.002105
MIN, LIM = 5.0, 100.0
TOP = 18
NCOL = 18
CACHE = {}
KEEP = 1.0
LOW = 0.005
# the reference branch of each source axis, written at 0 (GMM axes: the white diamond of GMM-1R is the reference)
REF_LABEL = {("interface", "segmentation"): "full margin", ("interface", "rate model"): "seismic",
             ("interface", "geodetic coupling χ"): "0.8", ("interface", "(a, b) uncertainty"): "ML",
             ("interface", "b per segment"): "own b", ("interface", "MFD shape"): "tapered",
             ("interface", "declustering"): "full", ("interface", "GMM truncation"): "3σ",
             ("inslab", "(a, b) uncertainty"): "ML", ("inslab", "spatial pattern"): "GK74",
             ("inslab", "GMM truncation"): "3σ", ("interface", "Mmax pad"): "+0.2",
             ("inslab", "MFD shape"): "tapered", ("inslab", "Mmax pad"): "+0.2", ("inslab", "layers"): "three",
             ("inslab", "lower depth"): "0.475", ("inslab", "rupture scaling"): "Strasser", ("inslab", "declustering"): "full", ("crustal", "spatial pattern"): "GK74",
             ("crustal", "background MFD"): "tapered", ("crustal", "background rates"): "full",
             ("crustal", "with faults"): "yes", ("crustal", "fault linkage"): "multi-fault",
             ("crustal", "aseismic coefficient ψ"): "0.8", ("crustal", "seismogenic thickness"): "10 km",
             ("crustal", "max. jump distance"): "15 km", ("crustal", "fault database"): "GEM",
             ("crustal", "LOFS secondary traces"): "not linked", ("crustal", "class Mmax pad, multi-fault"): "+0.2",
             ("crustal", "class Mmax pad, single-fault"): "+0.2", ("crustal", "fault Mmax pad, single-fault"): "+0",
             ("crustal", "GMM truncation"): "3σ"}
PRE = {"interface": "IF", "inslab": "IS", "crustal": "CR"}
FAM = {"interface": ("if", "Subduction Interface"), "inslab": ("is", "Subduction IntraSlab"),
       "crustal": ("cr", "Active Shallow Crust")}
NAME = {"interface": "interface", "inslab": "in-slab", "crustal": "crustal"}
COL = {"interface": palette.CLASS_COLOR["interface"], "inslab": palette.CLASS_COLOR["intraslab_intermediate"],
       "crustal": palette.CLASS_COLOR["forearc"]}
SETS = {"GMM-1R": "ref", "GMM-FIT": "set_gm1top4", "GMM-CSN": "set_mascsn26", "GMM-GEM": "set_gem_sam"}
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


def load(j):
    if j not in CACHE:
        CACHE[j] = post.load(j)
    return CACHE[j]


def averages(s, t):
    """Average of each source axis at site index s: the hazard curves of its branches and its base (the reference)
    averaged with equal weights, then the change of the total PGA 475 yr against the base, as for the GMM sets.
    An axis whose rows have different bases (in-slab declustering) takes the mean of its changes and 0."""
    ref = {f: post.mean(load(f"t_{a}_ref"))[s] for f, (a, _) in FAM.items()}
    lv = load("t_if_ref")["imtls"]["PGA"]
    rt = {f: combine.rate(v) for f, v in ref.items()}
    rows = []
    for (f, a), q in t.groupby(["family", "axis"], sort=False):
        if q.base.nunique() > 1:
            rows.append({"family": f, "axis": a, "row": "average", "kind": "set",
                         "family_pct": q.family_pct.sum() / (len(q) + 1),
                         "combined_pct": q.combined_pct.sum() / (len(q) + 1)})
            continue
        oth = sum(rt[x] for x in FAM if x != f)
        base = post.mean(load(q.base.iloc[0]))[s]
        mix = np.mean([base] + [post.mean(load(j))[s] for j in q.job.unique()], axis=0)
        y0 = post.iml(1 - np.exp(-(combine.rate(base) + oth)), lv, POE)
        y = post.iml(1 - np.exp(-(combine.rate(mix) + oth)), lv, POE)
        x0, x = post.iml(base, lv, POE), post.iml(mix, lv, POE)
        rows.append({"family": f, "axis": a, "row": "average", "kind": "set", "family_pct": 100 * (x / x0 - 1),
                     "combined_pct": 100 * (y / y0 - 1)})
    return pd.DataFrame(rows)


def gmm_rows(s):
    """Rows of the GMM-set axes at site index s: every model of every set, and each set as a whole."""
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
    palette.apply(size=16)
    OUT.mkdir(parents=True, exist_ok=True)
    for c in CITIES:
        one(c)
    print(f"wrote {OUT}")


def table(CITY):
    """Every row of the city: branches (kind row / model), averages and GMM sets (kind set), changes in %."""
    s = list(hc.CITIES).index(CITY)
    t = pd.read_csv(hc.OUT / "tornado" / "tornado.csv")
    t = t[(t.site == CITY) & ~t.axis.isin(["GMM set", "GMM-1R models"])].assign(kind="row")
    low = t.combined_pct.isna() & t.iml_base_combined.notna()
    t.loc[low, "combined_pct"] = 100 * (LOW / t.loc[low, "iml_base_combined"] - 1)
    t.loc[low, "row"] = t.loc[low, "row"] + f" (below {LOW} g)"
    return pd.concat([t[["family", "axis", "row", "kind", "family_pct", "combined_pct"]], averages(s, t), gmm_rows(s)],
                     ignore_index=True)


def one(CITY):
    g = table(CITY)
    g.to_csv(OUT / f"{CITY.replace(' ', '_')}.csv", index=False)
    ax_ = []
    for (f, a), q in g.groupby(["family", "axis"], sort=False):
        r = q[q.kind != "set"]
        ax_.append({"family": f, "axis": a, "lo": min(r.combined_pct.min(), 0), "hi": max(r.combined_pct.max(), 0),
                    "flo": min(r.family_pct.min(), 0), "fhi": max(r.family_pct.max(), 0),
                    "amax": np.nanmax(np.abs(q.combined_pct))})
    b = pd.DataFrame(ax_)
    b = b[b.amax >= KEEP].sort_values("amax")
    n = len(b)
    lim = min(LIM, np.nanmax(np.abs(b[["lo", "hi", "flo", "fhi"]].to_numpy())) * 1.1 + 3)

    hnd = [Line2D([], [], color=COL[f], lw=8, label=NAME[f]) for f in COL] + [
        Line2D([], [], color="0.4", lw=10, label="all tectonic settings"),
        Line2D([], [], color="0.4", lw=3, alpha=0.35, label="within tectonic setting"),
        Line2D([], [], marker="o", color="k", ls="", ms=5, label="branches"),
        Line2D([], [], marker="D", mfc="none", mec="0.1", mew=1.0, ls="", ms=7, label="average")]
    # vertical bars: axes along x, largest at the left
    b2 = b.iloc[::-1].reset_index(drop=True).head(NCOL)
    m2 = len(b2)
    fig, ax = plt.subplots(figsize=(1.15 * m2 + 2.5, 9.5), layout="constrained")
    for i, (_, r) in enumerate(b2.iterrows()):
        c = COL[r.family]
        ax.plot([i, i], [clip(r.flo), clip(r.fhi)], color=c, lw=3, alpha=0.35, solid_capstyle="butt")
        ax.plot([i, i], [clip(r.lo), clip(r.hi)], color=c, lw=10, solid_capstyle="butt")
        q = g[(g.family == r.family) & (g.axis == r.axis)]
        m = q[q.kind != "set"]
        ax.plot([i] * len(m), [clip(v) for v in m.combined_pct], "o", ms=5, color="k", zorder=5)
        st = q[q.kind == "set"]
        ax.plot([i] * len(st), [clip(v) for v in st.combined_pct], "D", ms=8, mfc="none", mec="0.1", mew=1.0,
                zorder=6)
        ref = REF_LABEL.get((r.family, r.axis))
        if ref:
            ax.plot(i, 0, "o", ms=5, color="k", zorder=5)
        if len(m) and i < TOP:
            pts = [(clip(v), l, False) for v, l in zip(m.combined_pct, m.row)] + ([(0.0, ref, True)] if ref else [])
            pts.sort(key=lambda x: x[0])
            gap = 2 * lim / 36
            p = []
            for y, _, _ in pts:
                p.append(y if not p else max(y, p[-1] + gap))
            for (y, l, isref), py in zip(pts, p):
                ax.annotate(l, (i, y), xytext=(i + 0.22, py), textcoords="data", ha="left", va="center",
                            fontsize=11, color="0.15",
                            arrowprops=dict(arrowstyle="-", color="0.45", lw=0.6, shrinkA=0, shrinkB=2))
    ax.axhline(0, color="k", lw=0.8)
    ax.axhspan(-MIN, MIN, color="0.5", alpha=0.15, lw=0)
    ax.set_ylim(-lim, lim)
    ax.set_xlim(-0.6, m2 - 0.2)
    ax.set_xticks(range(m2))
    ax.set_xticklabels([f"{PRE[f]} · {a}" for f, a in zip(b2.family, b2.axis)], rotation=50, ha="right",
                       fontsize=16)
    ax.set_ylabel("change of PGA 475 yr (%)", fontsize=18)
    darkgrid(ax)
    ax.text(0.005, 0.99, CITY, transform=ax.transAxes, ha="left", va="top", fontsize=22)
    fig.legend(handles=hnd, loc="outside lower center", ncol=len(hnd), frameon=False, fontsize=14)
    fig.savefig(OUT / f"{CITY.replace(' ', '_')}.png", dpi=170, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()

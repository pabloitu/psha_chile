# Full tornado per city, for review with the co-authors: every level of the tree, none left out, horizontal bars
# grouped by tectonic setting (interface, in-slab, crustal), each group ordered by the change of the total PGA 475 yr.
# Same marks as hazard/tornado_prelim.py (FIGURE_STYLE_tornado.md): thick bar all tectonic settings, pale bar
# within tectonic setting, dots the branches (reference at 0, labelled), hollow diamond the average.
# Reads hazard/out/tornado_prelim/<city>.csv (run tornado_prelim.py first); writes hazard/out/tornado_full/

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
from hazard import config as hc
from hazard.tornado_prelim import COL, NAME, REF_LABEL, MIN

# settings
CITIES = list(hc.CITIES)
OUT = hc.OUT / "tornado_full"
LIM = 40.0
ROW_IN = 0.52
FS = {"city": 22, "group": 16, "axis": 13, "label": 9.5, "tick": 13, "legend": 13}


def labels(ax, xs, labs, y, lo, hi):
    """Branch labels above the bar at y, spread along x so they do not overlap, with leader lines."""
    o = np.argsort(xs)
    xs, labs = np.asarray(xs)[o], [labs[i] for i in o]
    ch = (hi - lo) / 175
    p = []
    for i, l in enumerate(labs):
        p.append(xs[i] if not p else max(xs[i], p[-1] + ch * (len(labs[i - 1]) + len(l)) / 2 + ch * 2))
    over = p[-1] + ch * len(labs[-1]) / 2 - hi
    if over > 0:
        p = [v - over for v in p]
    for x, px, l in zip(xs, p, labs):
        ax.annotate(l, (x, y), xytext=(px, y - 0.36), textcoords="data", ha="center", va="bottom",
                    fontsize=FS["label"], color="0.15",
                    arrowprops=dict(arrowstyle="-", color="0.5", lw=0.6, shrinkA=0, shrinkB=2))


def axes_of(g):
    out = []
    for (f, a), q in g.groupby(["family", "axis"], sort=False):
        r = q[q.kind != "set"]
        out.append({"family": f, "axis": a, "lo": min(r.combined_pct.min(), 0), "hi": max(r.combined_pct.max(), 0),
                    "flo": min(r.family_pct.min(), 0), "fhi": max(r.family_pct.max(), 0),
                    "amax": np.nanmax(np.abs(r.combined_pct)) if len(r) else 0})
    b = pd.DataFrame(out)
    b["o"] = b.family.map({f: i for i, f in enumerate(COL)})
    return b.sort_values(["o", "amax"], ascending=[True, False]).reset_index(drop=True)


def one(CITY):
    g = pd.read_csv(hc.OUT / "tornado_prelim" / f"{CITY.replace(' ', '_')}.csv")
    b = axes_of(g)
    cl = lambda v: float(np.clip(v, -LIM, LIM)) if np.isfinite(v) else 0.0
    lo = max(-LIM, min(b.lo.min(), b.flo.min())) - 4
    hi = min(LIM, max(b.hi.max(), b.fhi.max())) + 4
    # rows from the top, a gap and a header before each tectonic setting
    y, ys, heads = 0.0, [], []
    for f in COL:
        if (b.family == f).any():
            heads.append((f, y))
            y += 1.0
            for _ in range((b.family == f).sum()):
                ys.append(y)
                y += 1.0
            y += 0.4
    fig, ax = plt.subplots(figsize=(13, ROW_IN * y + 1.6), layout="constrained")
    for (i, r), yy in zip(b.iterrows(), ys):
        c = COL[r.family]
        ax.plot([cl(r.flo), cl(r.fhi)], [yy, yy], color=c, lw=3.5, alpha=0.35, solid_capstyle="butt")
        ax.plot([cl(r.lo), cl(r.hi)], [yy, yy], color=c, lw=11, solid_capstyle="butt")
        # beyond the axis: an arrow at the edge and the value
        for v, sz in ((r.lo, 11), (r.hi, 11), (r.flo, 7), (r.fhi, 7)):
            if abs(v) > LIM:
                e = np.sign(v) * LIM
                ax.plot(e, yy, ">" if v > 0 else "<", ms=sz, color=c, alpha=1 if sz == 11 else 0.5, zorder=4)
                ax.text(e - np.sign(v) * 0.8, yy + 0.32, f"{v:+.0f} %" + ("" if sz == 11 else " within"),
                        ha="right" if v > 0 else "left", va="top", fontsize=FS["label"], color="0.15")
        q = g[(g.family == r.family) & (g.axis == r.axis)]
        m, st = q[q.kind != "set"], q[q.kind == "set"]
        ax.plot([cl(v) for v in m.combined_pct], [yy] * len(m), "o", ms=5, color="k", zorder=5)
        ax.plot([cl(v) for v in st.combined_pct], [yy] * len(st), "D", ms=8, mfc="none", mec="0.1", mew=1.0,
                zorder=6)
        ref = REF_LABEL.get((r.family, r.axis))
        pts = [(cl(v), l) for v, l in zip(m.combined_pct, m.row)]
        if ref:
            ax.plot(0, yy, "o", ms=5, color="k", zorder=5)
            pts.append((0.0, ref))
        if pts:
            labels(ax, [p[0] for p in pts], [p[1] for p in pts], yy, lo, hi)
    for f, yy in heads:
        ax.text(lo + 0.008 * (hi - lo), yy + 0.1, "■", ha="left", va="center", fontsize=FS["group"] + 4,
                color=COL[f])
        ax.text(lo + 0.04 * (hi - lo), yy + 0.1, NAME[f], ha="left", va="center", fontsize=FS["group"],
                color="0.1", fontweight="bold")
    ax.axvline(0, color="k", lw=0.8)
    ax.axvspan(-MIN, MIN, color="0.5", alpha=0.15, lw=0)
    ax.set_xlim(lo, hi)
    ax.set_ylim(y - 0.2, -1.4)
    ax.set_yticks(ys)
    ax.set_yticklabels(b.axis, fontsize=FS["axis"])
    ax.tick_params(axis="x", labelsize=FS["tick"])
    ax.set_xlabel("change of PGA 475 yr (%)", fontsize=FS["axis"] + 2)
    darkgrid(ax)
    ax.grid(axis="y", visible=False)
    ax.text(0.99, 0.995, CITY, transform=ax.transAxes, ha="right", va="top", fontsize=FS["city"])
    hnd = [Line2D([], [], color="0.4", lw=10, label="all tectonic settings"),
           Line2D([], [], color="0.4", lw=3, alpha=0.35, label="within tectonic setting"),
           Line2D([], [], marker="o", color="k", ls="", ms=5, label="branches"),
           Line2D([], [], marker="D", mfc="none", mec="0.1", mew=1.0, ls="", ms=7, label="average")]
    fig.legend(handles=hnd, loc="outside lower center", ncol=len(hnd), frameon=False, fontsize=FS["legend"])
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{CITY.replace(' ', '_')}.{ext}", dpi=150, facecolor="white")
    plt.close(fig)


def main():
    palette.apply(size=13)
    OUT.mkdir(parents=True, exist_ok=True)
    for c in CITIES:
        one(c)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

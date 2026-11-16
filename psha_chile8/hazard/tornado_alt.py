# Trial layout for the tornado (style C): thick line = change of the total, pale line = change of the family alone,
# dots = the rows of each axis, labelled on the TOP axes with the largest change of the total. Vertical (axes as rows)
# and horizontal (axes as columns). Reads hazard/out/tornado/{tornado,bars}.csv; writes hazard/out/tornado_alt/

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

# settings
CITIES = ["Iquique", "Puerto Montt"]
SRC = hc.OUT / "tornado"
OUT = hc.OUT / "tornado_alt"
MIN, LIM = 5.0, 100.0
TOP = 8
NAME = {"interface": "interface", "inslab": "in-slab", "crustal": "crustal"}
COL = {"interface": palette.CLASS_COLOR["interface"], "inslab": palette.CLASS_COLOR["intraslab_intermediate"],
       "crustal": palette.CLASS_COLOR["forearc"]}


def clip(v):
    return float(np.clip(v, -LIM, LIM)) if np.isfinite(v) else 0.0


def draw(ax, g, t, vertical):
    n = len(g)
    for i, (_, r) in enumerate(g.iterrows()):
        c = COL[r.family]
        lo, hi, flo, fhi = (clip(r[k]) for k in ("combined_lo", "combined_hi", "family_lo", "family_hi"))
        q = t[(t.family == r.family) & (t.axis == r.axis)].sort_values("combined_pct")
        xs = [clip(v) for v in q.combined_pct]
        line = (lambda a, b, **k: ax.plot([a, b], [i, i], **k)) if vertical else (
            lambda a, b, **k: ax.plot([i, i], [a, b], **k))
        line(flo, fhi, color=c, lw=3, alpha=0.35, solid_capstyle="butt")
        line(lo, hi, color=c, lw=8, solid_capstyle="butt")
        if vertical:
            ax.plot(xs, [i] * len(xs), "o", ms=4, color="k", zorder=5)
        else:
            ax.plot([i] * len(xs), xs, "o", ms=4, color="k", zorder=5)
        if (i >= n - TOP) if vertical else (i < TOP):
            grp = []
            for x, lab in zip(xs, q.row):
                if grp and x - grp[-1][0][-1] < 0.03 * LIM:
                    grp[-1][0].append(x)
                    grp[-1][1].append(lab)
                else:
                    grp.append(([x], [lab]))
            for j, (gx, gl) in enumerate(grp):
                x, lab = float(np.mean(gx)), ", ".join(gl)
                if vertical:
                    ax.annotate(lab, (x, i), xytext=(0, 8 if j % 2 == 0 else -10), textcoords="offset points",
                                ha="center", va="center", fontsize=7.5, color="0.15")
                else:
                    ax.annotate(lab, (i, x), xytext=(7, 0), textcoords="offset points", ha="left", va="center",
                                fontsize=7.5, color="0.15")
        for v in (r.combined_lo, r.combined_hi, r.family_lo, r.family_hi):
            if np.isfinite(v) and abs(v) > LIM:
                p = (np.sign(v) * LIM * 0.97, i + 0.3) if vertical else (i + 0.3, np.sign(v) * LIM * 0.97)
                ax.text(*p, f"{v:+.0f} %", fontsize=7, color="0.2",
                        ha=("right" if v > 0 else "left") if vertical else "left",
                        va="center" if vertical else ("top" if v > 0 else "bottom"))
    (ax.axvline if vertical else ax.axhline)(0, color="k", lw=0.8)
    (ax.axvspan if vertical else ax.axhspan)(-MIN, MIN, color="0.5", alpha=0.15, lw=0)
    darkgrid(ax)


def main():
    palette.apply()
    OUT.mkdir(parents=True, exist_ok=True)
    tt = pd.read_csv(SRC / "tornado.csv")
    bb = pd.read_csv(SRC / "bars.csv")
    for city in CITIES:
        t = tt[tt.site == city]
        lim = min(LIM, np.nanmax(bb[bb.site == city][["family_amax", "combined_amax"]].to_numpy()) * 1.1 + 2)
        keys = [f"{NAME[f]}: {a}" for f, a in zip(bb.family, bb.axis)]
        hnd = [Line2D([], [], color=COL[f], lw=8, label=NAME[f]) for f in COL] + [
            Line2D([], [], color="0.4", lw=8, label="total"), Line2D([], [], color="0.4", lw=3, alpha=0.35,
                                                                     label="family alone"),
            Line2D([], [], marker="o", color="k", ls="", ms=4, label="rows")]
        tag = city.replace(" ", "_")

        g = bb[bb.site == city].sort_values("combined_amax")
        lab = [f"{NAME[f]}: {a}" for f, a in zip(g.family, g.axis)]
        fig, ax = plt.subplots(figsize=(11, 0.42 * len(g) + 1.8), layout="constrained")
        draw(ax, g, t, True)
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-0.7, len(g) - 0.3)
        ax.set_yticks(range(len(g)))
        ax.set_yticklabels(lab)
        ax.set_xlabel("change of PGA 475 yr (%)")
        ax.text(0.01, 0.995, city, transform=ax.transAxes, ha="left", va="top", fontsize=13)
        fig.legend(handles=hnd, loc="outside lower center", ncol=6, frameon=False, fontsize=9)
        fig.savefig(OUT / f"{tag}_vertical.png", dpi=170, facecolor="white")
        plt.close(fig)

        g = bb[bb.site == city].sort_values("combined_amax", ascending=False)
        fig, ax = plt.subplots(figsize=(0.55 * len(g) + 3, 7.5), layout="constrained")
        draw(ax, g, t, False)
        ax.set_ylim(-lim, lim)
        ax.set_xlim(-0.7, len(g) - 0.3)
        ax.set_xticks(range(len(g)))
        ax.set_xticklabels([f"{NAME[f]}: {a}" for f, a in zip(g.family, g.axis)], rotation=55, ha="right")
        ax.set_ylabel("change of PGA 475 yr (%)")
        ax.text(0.01, 0.99, city, transform=ax.transAxes, ha="left", va="top", fontsize=13)
        fig.legend(handles=hnd, loc="outside lower center", ncol=6, frameon=False, fontsize=9)
        fig.savefig(OUT / f"{tag}_horizontal.png", dpi=170, facecolor="white")
        plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

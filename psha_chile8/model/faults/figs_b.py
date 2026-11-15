"""Figures of D16b: MASCSN restored slip against Table 17, database A against B."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import palette as P  # noqa: E402

A_COLOR, B_COLOR, BOTH_COLOR = "#2166ac", "#e0641e", "0.55"


def slip_systems(s, t17, out):
    """Restored slip rate of every MASCSN source by Table 17 system, with the range of the table."""
    import matplotlib.pyplot as plt
    P.apply()
    keys = list(t17) + ["none"]
    nm = {k: v[0].replace("Transversales ", "Transversales\n") for k, v in t17.items()}
    lab = [f"{nm[k]}\n({k})" if k in t17 else "no Table 17\nsystem" for k in keys]
    fig, ax = plt.subplots(figsize=(12, 6))
    rng = np.random.default_rng(1)
    for i, k in enumerate(keys):
        v = s[s.t17.replace("", "none") == k]
        if k in t17:
            lo, hi = t17[k][2], t17[k][3]
            ax.fill_between([i - 0.35, i + 0.35], lo * 0.97, hi * 1.03, color="0.85", zorder=1, lw=0)
        x = i + rng.uniform(-0.25, 0.25, len(v))
        ax.scatter(x, v.slip, s=12 + 0.25 * v.L, c=P.SERIES[i % len(P.SERIES)], ec="white", lw=0.5, zorder=3, alpha=0.9)
        ax.text(i, 0.006, f"{len(v)}", ha="center", fontsize=9, color="0.35")
    ax.set_yscale("log")
    ax.set_ylim(0.005, 30)
    ax.set_xticks(range(len(keys)), lab, fontsize=10)
    ax.set_ylabel("restored FaultQuake slip rate (mm/yr)")
    ax.set_title("MASCSN26 faults: slip rate restored from the FaultQuake moment budget, against Table 17")
    ax.text(0.01, 0.97, "grey: Table 17 range; dot size: trace length; numbers at the bottom: sources", transform=ax.transAxes,
            ha="left", va="top", fontsize=9, color="0.35")
    fig.savefig(out, dpi=170, bbox_inches="tight")
    plt.close(fig)


def lines(ax, geoms, **kw):
    import cartopy.crs as ccrs
    for g in geoms:
        for p in (g.geoms if g.geom_type == "MultiLineString" else [g]):
            x, y = p.xy
            ax.plot(x, y, transform=ccrs.PlateCarree(), solid_capstyle="round", **kw)


def map_ab(a_only, b_only, both, cities, panels, out):
    """Faults of A and B: in both (grey), only in A (blue), only in B (orange); main map and insets."""
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from pituplots.maps import dress_map
    P.apply()
    fig = plt.figure(figsize=(12, 15))
    gs = fig.add_gridspec(4, 2, width_ratios=[0.6, 1.0], hspace=0.16, wspace=0.06)
    axes = [fig.add_subplot(gs[:, 0], projection=ccrs.PlateCarree())]
    axes += [fig.add_subplot(gs[i, 1], projection=ccrs.PlateCarree()) for i in range(4)]
    ext = [(-77.0, -64.0, -56.0, -17.0)] + list(panels.values())
    for j, (ax, e) in enumerate(zip(axes, ext)):
        dress_map(ax, e, coastline=True, borders=True, gridlines=j == 0)
        lw = 0.9 if j == 0 else 1.6
        lines(ax, both.geometry, color=BOTH_COLOR, lw=lw, zorder=3)
        lines(ax, a_only.geometry, color=A_COLOR, lw=lw, zorder=4)
        lines(ax, b_only.geometry, color=B_COLOR, lw=lw, zorder=5)
        for n, (x, y) in cities.items():
            if e[0] < x < e[1] and e[2] < y < e[3]:
                ax.plot(x, y, "o", ms=6 if j else 4, mfc="white", mec=P.INK, mew=1.0, transform=ccrs.PlateCarree(), zorder=6)
                if j and n != "Santiago Peñalolén":
                    ax.text(x + 0.04, y + 0.04, n.replace(" centro", ""), fontsize=9, transform=ccrs.PlateCarree(), zorder=6)
        if j:
            ax.set_title(list(panels)[j - 1], fontsize=12)
        else:
            for e2 in panels.values():
                ax.plot([e2[0], e2[1], e2[1], e2[0], e2[0]], [e2[2], e2[2], e2[3], e2[3], e2[2]], color="0.4", lw=0.7,
                        ls="--", transform=ccrs.PlateCarree())
    h = [Line2D([], [], color=BOTH_COLOR, lw=2, label="in A and B (within 5 km)"),
         Line2D([], [], color=A_COLOR, lw=2, label="only in A (GEM, D16)"),
         Line2D([], [], color=B_COLOR, lw=2, label="only in B (MASCSN26)"),
         Line2D([], [], ls="", marker="o", mfc="white", mec=P.INK, label="city of the hazard runs")]
    axes[0].legend(handles=h, loc="lower left", fontsize=9, frameon=True, framealpha=0.9)
    axes[0].set_title("Crustal faults: database A against B")
    fig.savefig(out, dpi=170, bbox_inches="tight")
    plt.close(fig)

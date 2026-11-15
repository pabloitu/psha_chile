"""Figures of D16: GEM against CHAF, Magallanes–Fagnano."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import palette as P  # noqa: E402

ACT_COLOR = {"Proved": "#a50f15", "Probable": "#e0641e", "Possible": "#c9a227"}
GEM_COLOR, MATCH_COLOR = "#111111", "#9ecae1"
PANELS = {"Northern Chile": (-71.0, -68.6, -24.6, -19.4), "Santiago and Valparaíso": (-72.0, -69.8, -34.6, -32.5),
          "Liquiñe–Ofqui zone": (-75.6, -71.0, -47.2, -38.0)}


def lines(ax, geoms, **kw):
    import cartopy.crs as ccrs
    for g in geoms:
        for p in (g.geoms if g.geom_type == "MultiLineString" else [g]):
            x, y = p.xy
            ax.plot(x, y, transform=ccrs.PlateCarree(), solid_capstyle="round", **kw)


def gem_chaf(gem, ch, ms, cities, out):
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from pituplots.maps import dress_map
    P.apply()
    fig = plt.figure(figsize=(11.5, 15))
    gs = fig.add_gridspec(3, 2, width_ratios=[0.62, 1.0], hspace=0.14, wspace=0.08)
    axes = [fig.add_subplot(gs[:, 0], projection=ccrs.PlateCarree())]
    axes += [fig.add_subplot(gs[i, 1], projection=ccrs.PlateCarree()) for i in range(3)]
    ext = [(-76.5, -64.5, -56.0, -17.0)] + list(PANELS.values())
    um = ch[ch["seg2"] < 0]
    for j, (ax, e) in enumerate(zip(axes, ext)):
        dress_map(ax, e, coastline=True, borders=True, gridlines=j == 0)
        lw = 0.8 if j == 0 else 1.4
        lines(ax, ch[ch["seg2"] >= 0].geometry, color=MATCH_COLOR, lw=lw * 1.8, zorder=3)
        for a in ("Possible", "Probable", "Proved"):
            lines(ax, um[um.activity == a].geometry, color=ACT_COLOR[a], lw=lw, zorder=4)
        lines(ax, gem.geometry, color=GEM_COLOR, lw=lw * 0.7, zorder=5)
        for n, (x, y) in cities.items():
            if e[0] < x < e[1] and e[2] < y < e[3]:
                ax.plot(x, y, "o", ms=6 if j else 4, mfc="white", mec=P.INK, mew=1.0, transform=ccrs.PlateCarree(), zorder=6)
                if j and n != "Santiago Peñalolén":
                    ax.text(x + 0.04, y + 0.04, n.replace(" centro", ""), fontsize=9, transform=ccrs.PlateCarree(), zorder=6)
        if j:
            ax.set_title(f"{list(PANELS)[j - 1]} ({abs(e[3]):.0f}–{abs(e[2]):.0f}° S)", fontsize=12)
            top = ms[(ms["rank"] <= 20) & ms.lon.between(e[0], e[1]) & ms.lat.between(e[2], e[3])]
            for r in top.itertuples():
                ax.text(r.lon, r.lat, f"{r.rank}", fontsize=8, color=ACT_COLOR[r.activity], weight="bold",
                        transform=ccrs.PlateCarree(), zorder=7, ha="center", va="center",
                        bbox=dict(boxstyle="circle,pad=0.15", fc="white", ec=ACT_COLOR[r.activity], lw=0.6))
        else:
            for t, e2 in PANELS.items():
                ax.plot([e2[0], e2[1], e2[1], e2[0], e2[0]], [e2[2], e2[2], e2[3], e2[3], e2[2]], color="0.4", lw=0.7,
                        ls="--", transform=ccrs.PlateCarree())
            ax.axhline(-19.3, color="0.6", lw=0.5, ls=":")
            ax.axhline(-47.8, color="0.6", lw=0.5, ls=":")
            ax.text(-76.2, -47.6, "CHAF covers 19.3–47.8° S", fontsize=9, color="0.4", transform=ccrs.PlateCarree())
    h = [Line2D([], [], color=GEM_COLOR, lw=1.2, label="GEM (clean database)"),
         Line2D([], [], color=MATCH_COLOR, lw=3, label="CHAF, on a GEM trace (2 km)")]
    h += [Line2D([], [], color=ACT_COLOR[a], lw=2, label=f"CHAF, not in GEM: {a.lower()}") for a in ACT_COLOR]
    h += [Line2D([], [], ls="", marker="o", mfc="white", mec=P.INK, label="city of the hazard runs")]
    axes[0].legend(handles=h, loc="lower left", fontsize=9, frameon=True, framealpha=0.9)
    axes[0].set_title("Crustal faults: GEM against CHAF")
    fig.text(0.42, 0.075, "Numbers: rank of the faults missing from GEM (tables/missing_2026-11-15.csv)", fontsize=9, color="0.35")
    fig.savefig(out, dpi=170, bbox_inches="tight")
    plt.close(fig)


def fagnano(full, kept, ov, city, border, out):
    """Segments of the Magallanes–Fagnano system, Chilean and Argentine, their overlaps and the traces kept."""
    import cartopy.crs as ccrs
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from pituplots.maps import dress_map
    P.apply()
    fig = plt.figure(figsize=(15, 6.5))
    ax = fig.add_subplot(projection=ccrs.PlateCarree())
    dress_map(ax, (-75.0, -65.0, -55.6, -52.4), coastline=True, borders=True, gridlines=True)
    col = {"CL": "#2166ac", "AR": "#e0641e"}
    for r in full.itertuples():
        lines(ax, [r.geometry], color=col[r.fid[:2]], lw=0.9, ls=(0, (3, 2)), zorder=4)
        c = r.geometry.interpolate(0.5, normalized=True)
        dy = 0.08 if r.fid[:2] == "CL" else -0.12
        ax.text(c.x, c.y + dy, r.fid.split("-")[1], fontsize=8, color=col[r.fid[:2]], ha="center",
                transform=ccrs.PlateCarree(), zorder=6)
    for r in kept.itertuples():
        lines(ax, [r.geometry], color=col[r.fid[:2]], lw=2.4, zorder=5)
    for g in ov:
        lines(ax, [g], color="#a50f15", lw=7, alpha=0.25, zorder=3)
    ax.plot([border, border], [-55.3, -52.6], color="0.4", lw=0.8, ls=":", transform=ccrs.PlateCarree())
    x, y = city
    ax.plot(x, y, "o", ms=7, mfc="white", mec=P.INK, transform=ccrs.PlateCarree(), zorder=6)
    ax.text(x + 0.06, y - 0.12, "Puerto Williams", fontsize=9, transform=ccrs.PlateCarree())
    h = [Line2D([], [], color=col["CL"], lw=2.4, label="Chilean segments (CL-056), kept"),
         Line2D([], [], color=col["AR"], lw=2.4, label="Argentine segments (AR-0056), kept"),
         Line2D([], [], color="0.3", lw=0.9, ls=(0, (3, 2)), label="trace as in the database"),
         Line2D([], [], color="#a50f15", lw=7, alpha=0.25, label="Chilean and Argentine traces within 5 km"),
         Line2D([], [], color="0.4", lw=0.8, ls=":", label="border, Tierra del Fuego")]
    ax.legend(handles=h, loc="upper right", fontsize=9, frameon=True, framealpha=0.9)
    ax.set_title("Magallanes–Fagnano: segments of the GEM SARA release, one trace per section")
    fig.savefig(out, dpi=170, bbox_inches="tight")
    plt.close(fig)
